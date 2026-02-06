from pyspark.sql import SparkSession
import sqlglot
from sqlglot import exp
from neo4j import GraphDatabase

# Neo4j 连接配置
NEO4J_URI = "bolt://neo4j-service:7687"
NEO4J_AUTH = ("neo4j", "password123")

# 初始化 Spark，配置连接 MinIO (S3协议) 所需的参数
spark = SparkSession.builder \
    .appName("LineageETL") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio-service:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "admin") \
    .config("spark.hadoop.fs.s3a.secret.key", "password123") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

print(">>> [Step 1] 正在从数据湖 (MinIO) 读取 history.csv ...")
# 读取 S3 数据
df = spark.read.csv("s3a://sql-logs/history.csv", header=True)

# 将数据收集到 Driver 端进行处理 (简化演示)
# 真实大数据场景下应该使用 mapPartitions 在 Worker 端并行写入
rows = df.collect()
print(f">>> [Step 2] 读取成功，共 {len(rows)} 条日志，开始解析...")

driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

success_count = 0
with driver.session() as session:
    for row in rows:
        sql = row['sql_text']
        if not sql: continue
        
        try:
            # 使用 sqlglot 解析 SQL
            parsed = sqlglot.parse_one(sql)
            
            # 提取目标表
            target = parsed.find(exp.Table).alias_or_name
            
            # 提取源表 (排除掉目标表自己)
            sources = [t.alias_or_name for t in parsed.find_all(exp.Table) if t.alias_or_name != target]
            
            print(f"    解析结果: {sources} -> {target}")

            # 写入 Neo4j
            for source in sources:
                session.run("""
                    MERGE (s:Table {name: $s})
                    MERGE (t:Table {name: $t})
                    MERGE (s)-[:SPARK_PROCESSED]->(t)
                """, s=source, t=target)
            success_count += 1
        except Exception as e:
            print(f"    解析失败: {e}")

print(f">>> [Step 3] 任务完成！成功写入 {success_count} 条血缘关系到图数据库。")
spark.stop()
