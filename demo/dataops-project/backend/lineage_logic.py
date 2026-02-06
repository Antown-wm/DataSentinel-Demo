import sqlglot
from sqlglot import exp
from neo4j import GraphDatabase
import os

# Neo4j 连接
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j-service:7687")
NEO4J_AUTH = ("neo4j", "password123")
driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

def process_sql_task(sql: str):
    print(f">>> [Worker] 开始深度解析 SQL: {sql}")
    try:
        parsed = sqlglot.parse_one(sql)
        
        # 1. 提取目标表 (INSERT INTO target)
        target_table = parsed.find(exp.Table).alias_or_name
        
        # 2. 提取 SELECT 子句
        select_stmt = parsed.find(exp.Select)
        projections = select_stmt.expressions
        
        dependencies = []

        # 3. 遍历 SELECT 的每个字段 (核心算法: 递归 AST)
        # 例如: SELECT a.col1 + b.col2 AS total ...
        for expression in projections:
            # 获取目标字段名 (As total)
            target_col = expression.alias_or_name
            
            # 递归查找该表达式里所有的源字段 (a.col1, b.col2)
            # expression.find_all(exp.Column) 会自动遍历 AST 树
            for source_node in expression.find_all(exp.Column):
                source_table = source_node.table
                source_col = source_node.name
                
                # 只有当源表和源字段都存在时才记录
                if source_table and source_col:
                    dependencies.append({
                        "src_tbl": source_table, "src_col": source_col,
                        "tgt_tbl": target_table, "tgt_col": target_col
                    })

        # 4. 写入 Neo4j (字段级图谱)
        write_to_neo4j(dependencies)
        print(f"✅ [Worker] 解析成功，存入 {len(dependencies)} 条字段血缘。")
        
    except Exception as e:
        print(f"❌ [Worker] 解析失败: {e}")

def write_to_neo4j(deps):
    with driver.session() as session:
        for d in deps:
            # Cypher 语句：不仅建立表关系，还建立字段关系
            query = """
            // 1. 建立表节点
            MERGE (st:Table {name: $src_tbl})
            MERGE (tt:Table {name: $tgt_tbl})
            MERGE (st)-[:IMPACTS]->(tt)
            
            // 2. 建立字段节点，并挂在表下面
            MERGE (sc:Column {name: $src_col, table: $src_tbl})
            MERGE (sc)-[:BELONGS_TO]->(st)
            
            MERGE (tc:Column {name: $tgt_col, table: $tgt_tbl})
            MERGE (tc)-[:BELONGS_TO]->(tt)
            
            // 3. 建立字段级血缘
            MERGE (sc)-[:DERIVED_TO]->(tc)
            """
            session.run(query, **d)
