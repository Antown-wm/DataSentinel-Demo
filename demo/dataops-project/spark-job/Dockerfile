FROM apache/spark:3.4.0

USER root

# 1. 安装 Python 依赖库
RUN pip install sqlglot neo4j

# 2. 下载连接 MinIO (S3) 必须的 JAR 包
# 必须下载 hadoop-aws 和 aws-java-sdk-bundle
RUN curl -L https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -o /opt/spark/jars/hadoop-aws-3.3.4.jar
RUN curl -L https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar -o /opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar

# 3. 复制代码
WORKDIR /app
COPY etl_job.py .
