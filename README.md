# 云原生全链路数据血缘智能治理平台

> 基于 Kubernetes 的企业级数据血缘分析、追踪与智能治理解决方案

## 项目简介

本项目是一个面向云原生环境的数据血缘智能治理平台，旨在解决企业数据管道中的元数据追踪、Schema 变更影响分析、数据依赖可视化等核心问题。平台采用轻量级 Kubernetes 集群部署，集成分布式计算引擎、图数据库、消息队列等组件，实现从数据摄入到血缘分析的全链路自动化治理。

### 核心特性

- 🔍 **字段级血缘追踪**：基于 SQL 解析（sqlglot）实现精确到字段级别的数据血缘分析
- 📊 **可视化拓扑图**：使用 ECharts 构建交互式数据依赖关系图谱
- 🚨 **智能 Schema 哨兵**：定时巡检元数据变更，自动评估变更影响范围
- ⚡ **离线 + 实时双引擎**：支持 Spark 批量计算与 API 实时接入两种元数据采集方式
- 🏗️ **云原生架构**：基于 Kubernetes 的微服务架构，具备高可用与弹性扩展能力
- 💾 **数据湖底座**：集成 MinIO 对象存储，构建统一的数据湖平台

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes 集群                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   前端服务    │    │   后端服务    │    │  Redis 队列  │  │
│  │  (Nginx/HTML)│◄───┤   (FastAPI)  │◄───┤   (RQ Worker) │  │
│  └──────────────┘    └──────┬───────┘    └──────────────┘  │
│                              │                                  │
│                       ┌──────▼───────┐    ┌──────────────┐  │
│                       │  Neo4j 图库   │    │ Schema 哨兵  │  │
│                       │ (血缘图谱存储)│    │  (CronJob)   │  │
│                       └──────────────┘    └──────┬───────┘  │
│                              │                     │          │
│                       ┌──────▼─────────────┐      │          │
│                       │  Spark 集群        │◄─────┘          │
│                       │  (离线 ETL 分析)   │                 │
│                       └──────────┬─────────┘                 │
│                                  │                           │
│                       ┌──────────▼─────────┐                 │
│                       │   MinIO 数据湖     │                 │
│                       │  (对象存储/SQL日志)│                 │
│                       └────────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术选型 | 用途说明 |
|------|---------|---------|
| 容器编排 | Kubernetes | 轻量级集群（Kind/K3s），部署所有微服务 |
| 数据可视化 | ECharts | 前端依赖关系图谱渲染 |
| 后端框架 | FastAPI | RESTful API 服务，血缘分析与图谱查询 |
| 任务队列 | Redis + RQ | 异步 SQL 解析任务队列 |
| 图数据库 | Neo4j | 存储表级与字段级血缘关系 |
| 分布式计算 | Apache Spark | 离线 SQL 日志批量处理与血缘提取 |
| SQL 解析 | sqlglot | 跨方言 SQL 解析，字段级依赖提取 |
| 数据湖 | MinIO | S3 兼容对象存储，存储 SQL 执行日志 |
| 前端服务 | Nginx | 静态页面托管与服务反向代理 |

## 项目结构

```
.
├── README.md                              # 项目说明文档
├── 操作过程及结果/                        # 部署与功能演示截图及视频
│   ├── *.png                             # 系统运行状态截图
│   └── *.mp4                             # 功能演示视频
└── 源码文件/
    ├── history.csv                       # 模拟 SQL 执行日志数据
    └── dataops-project/                  # K8s 部署源码
        ├── backend/                      # 后端服务
        │   ├── main.py                   # FastAPI 服务主程序
        │   ├── lineage_logic.py          # SQL 解析与血缘提取逻辑
        │   ├── requirements.txt          # Python 依赖
        │   ├── Dockerfile                # 后端镜像构建
        │   └── backend.yaml              # K8s 部署清单
        ├── frontend/                     # 前端服务
        │   ├── index.html                # 可视化前端页面
        │   ├── Dockerfile                # 前端镜像构建
        │   └── frontend.yaml             # K8s 部署清单
        ├── spark-job/                    # Spark ETL 作业
        │   ├── etl_job.py                # 离线血缘处理脚本
        │   ├── Dockerfile                # Spark 作业镜像
        │   ├── submit.yaml               # 作业提交配置
        │   └── submit-job.sh             # 作业提交脚本
        ├── spark/                        # Spark 集群
        │   ├── spark.yaml                # Master + Worker 部署
        │   └── submit.yaml               # 提交任务配置
        ├── neo4j/                        # 图数据库
        │   ├── neo4j.yaml                # Neo4j StatefulSet 部署
        │   └── neo4j.yaml                # 配置文件
        ├── sentinel/                     # Schema 哨兵
        │   ├── sentinel.py               # 元数据巡检脚本
        │   ├── sentinel.yaml             # CronJob 部署清单
        │   └── Dockerfile                # 哨兵镜像
        ├── redis/                        # 消息队列
        │   └── redis.yaml                # Redis 部署清单
        └── minio/                        # 数据湖
            ├── minio.yaml                # MinIO 部署清单
            └── ConfigMap                 # MinIO 配置
```

## 核心功能

### 1. 字段级血缘深度分析

基于 `sqlglot` 解析 SQL 语句的抽象语法树（AST），精确提取字段级依赖关系。例如：

```sql
INSERT INTO report_daily 
SELECT u.name, sum(o.amount) as total 
FROM users u 
JOIN fact_orders o ON u.id = o.uid
```

系统自动识别：
- 源表/字段：`users.name`, `fact_orders.amount`
- 目标表/字段：`report_daily.name`, `report_daily.total`
- 依赖关系：`users.name → report_daily.name`, `fact_orders.amount → report_daily.total`

### 2. 分布式 ETL 离线血缘提取

Spark 从 MinIO 读取 SQL 执行日志（`history.csv`），批量解析并写入 Neo4j：

```python
# 读取数据湖日志
df = spark.read.csv("s3a://sql-logs/history.csv", header=True)

# 解析 SQL 并提取表级血缘
for row in df.collect():
    parsed = sqlglot.parse_one(row['sql_text'])
    sources = [t.alias_or_name for t in parsed.find_all(exp.Table)]
    # 写入 Neo4j 图数据库
```

### 3. 实时血缘 API

提供异步 API 接口，支持实时提交 SQL 分析任务：

```bash
POST /analyze/sql
Body: {"sql": "INSERT INTO ... SELECT ..."}
Response: {"status": "queued", "job_id": "uuid"}
```

任务通过 Redis + RQ 队列异步处理，前端可轮询查询任务状态。

### 4. 智能 Schema 哨兵

通过 CronJob 定时触发元数据巡检，检测 Schema 变更并评估影响：

- **巡检周期**：每 1 分钟执行一次（可配置）
- **检测能力**：字段级变更监控
- **影响分析**：基于 Neo4j 图数据库递归查找下游依赖表
- **报警机制**：发现破坏性变更时触发红色阻断报警

```python
# 哨兵核心逻辑
if impacted_tables:
    print("🔴 【严重阻断】触发熔断报警！")
    print(f"🔴 将导致下游任务失败：{impacted_tables}")
else:
    print("✅ 无下游依赖或变更安全，继续运行。")
```

### 5. 可视化血缘图谱

前端通过 ECharts 渲染力导向图，展示表级依赖关系：

- 支持节点拖拽与缩放
- 边类型标注（`SPARK_PROCESSED`、`IMPACTS`、`DERIVED_TO`）
- 响应式布局，自动适应屏幕大小

访问地址：`http://<节点IP>:30080`

## 快速开始

### 前置要求

- Docker 20.10+
- Kubernetes 1.20+（推荐使用 Kind 或 K3s）
- kubectl 命令行工具
- 至少 4GB 可用内存

### 部署步骤

#### 1. 构建 Docker 镜像

```bash
# 构建后端镜像
cd 源码文件/dataops-project/backend
docker build -t lineage-backend:latest .

# 构建 Spark 作业镜像
cd ../spark-job
docker build -t spark-etl-job:latest .

# 构建哨兵镜像
cd ../sentinel
docker build -t schema-sentinel:latest .
```

#### 2. 部署基础服务

```bash
# 部署 Redis
kubectl apply -f 源码文件/dataops-project/redis/redis.yaml

# 部署 Neo4j
kubectl apply -f 源码文件/dataops-project/neo4j/neo4j.yaml

# 部署 MinIO（数据湖）
kubectl apply -f 源码文件/dataops-project/minio/minio.yaml
```

#### 3. 部署 Spark 集群

```bash
kubectl apply -f 源码文件/dataops-project/spark/spark.yaml
# 等待 Pod 状态变为 Running
kubectl get pods -l app=spark
```

#### 4. 部署应用服务

```bash
# 部署后端（包含 API + Worker）
kubectl apply -f 源码文件/dataops-project/backend/backend.yaml

# 部署前端
kubectl apply -f 源码文件/dataops-project/frontend/frontend.yaml

# 部署 Schema 哨兵
kubectl apply -f 源码文件/dataops-project/sentinel/sentinel.yaml
```

#### 5. 提交 Spark ETL 作业

```bash
# 从本地提交作业到集群
kubectl apply -f 源码文件/dataops-project/spark-job/submit.yaml

# 查看作业执行日志
kubectl logs -f <spark-driver-pod-name>
```

#### 6. 访问系统

- **血缘可视化界面**：`http://localhost:30080`
- **Neo4j 控制台**：`http://localhost:30080` (需配置 Ingress)
- **MinIO 控制台**：`http://localhost:9000` (admin/password123)

### 验证部署

```bash
# 检查所有 Pod 状态
kubectl get pods

# 预期输出：
# NAME                           READY   STATUS
# lineage-backend-xxx            1/1     Running
# lineage-frontend-xxx           1/1     Running
# lineage-redis-xxx              1/1     Running
# lineage-neo4j-0                1/1     Running
# spark-master-xxx               1/1     Running
# spark-worker-0                 1/1     Running
# schema-sentinel-xxx            0/1     Completed
```

## API 文档

### 获取血缘图谱数据

```http
GET /graph/data
```

**响应示例**：
```json
{
  "nodes": [
    {"name": "users", "category": 0, "symbolSize": 30},
    {"name": "fact_orders", "category": 0, "symbolSize": 30},
    {"name": "report_daily", "category": 0, "symbolSize": 30}
  ],
  "links": [
    {"source": "users", "target": "fact_orders", "value": "IMPACTS"},
    {"source": "fact_orders", "target": "report_daily", "value": "IMPACTS"}
  ]
}
```

### 提交 SQL 分析任务

```http
POST /analyze/sql
Content-Type: application/json

{
  "sql": "INSERT INTO target_table SELECT col FROM source_table"
}
```

**响应示例**：
```json
{
  "status": "queued",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "msg": "任务已放入后台队列"
}
```

### Schema 变更影响检查

```http
GET /impact/check?table=orders&column=amount
```

**响应示例（危险变更）**：
```json
{
  "deleted_field": "orders.amount",
  "impacted_tables": ["fact_orders", "report_daily"],
  "status": "DANGER"
}
```

**响应示例（安全变更）**：
```json
{
  "deleted_field": "orders.amount",
  "impacted_tables": [],
  "status": "SAFE"
}
```

## Neo4j 数据模型

### 节点类型

| 节点标签 | 属性 | 说明 |
|---------|------|------|
| `Table` | `name` | 数据表节点 |
| `Column` | `name`, `table` | 字段节点（关联到所属表） |

### 关系类型

| 关系类型 | 起点 → 终点 | 说明 |
|---------|------------|------|
| `IMPACTS` | `Table → Table` | 表级影响关系 |
| `SPARK_PROCESSED` | `Table → Table` | Spark ETL 处理产生的血缘 |
| `DERIVED_TO` | `Column → Column` | 字段级衍生关系 |
| `BELONGS_TO` | `Column → Table` | 字段归属表关系 |

### Cypher 查询示例

```cypher
// 查找所有表级血缘
MATCH (n)-[r]->(m) RETURN n.name, type(r), m.name

// 查找字段级血缘（递归）
MATCH (start:Column {name: $col_name, table: $tbl_name})
MATCH (start)-[:DERIVED_TO*]->(end:Column)
MATCH (end)-[:BELONGS_TO]->(dest_table:Table)
RETURN DISTINCT dest_table.name
```

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|-------|-------|------|
| `NEO4J_URI` | `bolt://neo4j-service:7687` | Neo4j 连接地址 |
| `REDIS_HOST` | `redis-service` | Redis 服务地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `MINIO_ENDPOINT` | `http://minio-service:9000` | MinIO 服务地址 |

### Sentinel CronJob 配置

修改 `sentinel/sentinel.yaml` 调整巡检频率：

```yaml
schedule: "*/1 * * * *"  # 每 1 分钟执行一次
```

## 系统截图

- [构建轻量级 Kubernetes 集群验证](操作过程及结果/1.构建轻量级%20Kubernetes%20集群%20验证集群状态为%20Ready.png)
- [Neo4j 配置修复](操作过程及结果/3.Neo4j%20配置冲突修复.png)
- [可视化前端连接正常](操作过程及结果/4.开发可视化前端%20前端服务连接正常.png)
- [数据湖底座部署成功](操作过程及结果/5.部署数据湖底座%20成功访问并创建了%20sql-logs%20存储桶%20上传了%20history.csv%20模拟数据.png)
- [分布式 ETL 链路打通](操作过程及结果/6.分布式%20ETL%20链路成功打通.jpg)
- [Spark 集群血缘写入](操作过程及结果/7.Spark%20集群将血缘写入图谱.png)
- [实时 API 元数据接入](操作过程及结果/8.除了离线计算%20还支持通过%20API%20实时接入元数据.png)
- [Schema 哨兵运行](操作过程及结果/9.部署%20Schema%20哨兵%20CronJob每隔%201%20分钟，自动触发一次.png)
- [字段级血缘深挖](操作过程及结果/11.将分析精度提升至字段级别%20进行字段级血缘深挖.png)
- [Neo4j 字段依赖路径](操作过程及结果/12.Neo4j%20里已经成功建立起了字段到表的深层依赖路径.png)

更多详细截图与演示视频请查看 `操作过程及结果/` 目录。

## 常见问题

### 1. Neo4j 启动失败

**问题**：Pod 因环境变量配置错误无法启动。

**解决**：检查 `neo4j.yaml` 中的 `NEO4J_AUTH` 配置，确保密码与后端连接配置一致。

### 2. Spark 作业无法连接 MinIO

**问题**：作业日志显示 `S3A filesystem` 相关错误。

**解决**：确认 `etl_job.py` 中 S3A 配置正确：
```python
.config("spark.hadoop.fs.s3a.path.style.access", "true")
.config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
```

### 3. 前端无法访问后端 API

**问题**：浏览器控制台显示跨域错误或连接失败。

**解决**：
- 检查 `frontend.yaml` 中 NodePort 配置（默认 30080）
- 确认后端 Service 名称正确：`lineage-backend-service`

### 4. Schema 哨兵无输出

**问题**：CronJob 执行但无日志输出。

**解决**：
- 检查 Pod 状态：`kubectl get pods -l app=schema-sentinel`
- 查看 Job 日志：`kubectl logs <sentinel-pod-name>`
- 确认后端 API 地址可访问：`http://lineage-backend-service:80`

## 扩展与优化

### 支持更多 SQL 方言

修改 `lineage_logic.py`，sqlglot 已支持：
- MySQL, PostgreSQL, Oracle
- Hive, Spark SQL, Presto
- Snowflake, BigQuery 等

### 增强血缘可视化

- 集成 Neo4j Bloom 进行交互式探索
- 添加时间轴视图展示血缘演进历史
- 支持血缘影响面热力图

### 生产环境增强

- 添加用户认证与权限管理（Keycloak）
- 配置 Prometheus + Grafana 监控
- 实现血缘变更事件告警（Slack/钉钉）
- 数据血缘版本控制与回滚

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目仅供学习与参考使用。

## 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**注**：本系统已在 Kubernetes 环境中完整测试，支持字段级血缘追踪、Schema 变更影响分析、实时与离线元数据接入等核心功能。详细演示请查看 `操作过程及结果/` 目录中的截图与视频。
