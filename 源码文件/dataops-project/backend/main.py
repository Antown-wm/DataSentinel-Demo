from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from rq import Queue
# 引入刚才写的逻辑函数名（但不执行）
from lineage_logic import process_sql_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# 连接 Redis
redis_conn = Redis(host='redis-service', port=6379)
q = Queue(connection=redis_conn)

class SQLRequest(BaseModel):
    sql: str

@app.post("/analyze/sql")
def analyze_sql_async(req: SQLRequest):
    """ 异步接口：接收任务 -> 放入 Redis -> 立即返回 """
    # Enqueue: 把函数和参数打包扔进队列
    job = q.enqueue(process_sql_task, req.sql)
    return {"status": "queued", "job_id": job.id, "msg": "任务已放入后台队列"}

# 保留原来的图查询接口给前端用
from neo4j import GraphDatabase
import os
driver = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://neo4j-service:7687"), auth=("neo4j", "password123"))

@app.get("/graph/data")
def get_graph_data():
    with driver.session() as session:
        # 这样就能查出 SPARK_PROCESSED, IMPACTS, DERIVED_TO 等所有关系
        result = session.run("MATCH (n)-[r]->(m) RETURN n.name, type(r), m.name")
        # -----------------------------------------------------
        
        nodes = set()
        links = []
        for record in result:
            # 简单处理：把所有节点都放进去
            # 为了兼容性，可以取别名
            n_name = record["n.name"] if record["n.name"] else "Unknown"
            m_name = record["m.name"] if record["m.name"] else "Unknown"
            
            nodes.add(n_name)
            nodes.add(m_name)
            links.append({"source": n_name, "target": m_name, "value": record["type(r)"]})
        
        return {
            "nodes": [{"name": n, "category": 0, "symbolSize": 30} for n in nodes], 
            "links": links
        }
# --- 追加的接口，用于哨兵报警 ---
@app.get("/impact/check")
def check_impact(table: str, column: str):
    """
    逻辑：
    1. 找到起点：orders 表的 amount 字段
    2. 找路径：沿着 DERIVED_TO 关系往下游爬
    3. 找终点：任何被影响的字段所属的表
    """
    with driver.session() as session:
        # 使用 Neo4j 5.x 推荐的参数传递方式
        query = """
        // 1. 定位起点字段 (Label是 Column, 属性是 name 和 table)
        MATCH (start:Column {name: $col_name, table: $tbl_name})
        
        // 2. 递归查找所有下游字段 (*表示任意深度)
        MATCH (start)-[:DERIVED_TO*]->(end:Column)
        
        // 3. 查找下游字段所属的表
        MATCH (end)-[:BELONGS_TO]->(dest_table:Table)
        
        // 4. 返回去重的下游表名
        RETURN DISTINCT dest_table.name as table_name
        """
        
        result = session.run(query, col_name=column, tbl_name=table)
        
        # 提取结果列表
        impacted_tables = [record["table_name"] for record in result]

    # 判定逻辑：只要找到了下游表，就视为危险
    if impacted_tables:
        return {
            "deleted_field": f"{table}.{column}",
            "impacted_tables": impacted_tables,
            "status": "DANGER"  # 触发红色报警
        }
    
    return {
        "deleted_field": f"{table}.{column}",
        "impacted_tables": [],
        "status": "SAFE"
    }