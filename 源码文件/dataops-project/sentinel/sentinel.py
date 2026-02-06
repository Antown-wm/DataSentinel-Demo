import requests
import datetime

# K8s 内部直接访问后端服务
API_URL = "http://lineage-backend-service:80/impact/check"

# sentinel.py (仅修改 run 函数)
def run():
    print(f"[{datetime.datetime.now()}] 启动 Schema 巡检...")
    
    # 1. 模拟：检测到 orders 表的 amount 字段被删了 (字段级监控)
    table, col = "orders", "amount" 
    print(f"⚠️  检测到元数据变更：{table}.{col} 已丢失")
    
    try:
        # 调用后端 API，传入 table 和 column 参数
        res = requests.get(API_URL, params={"table": table, "column": col})
        data = res.json()
        
        # 检查后端返回的状态
        if data.get("status") == "DANGER":
            impact_list = data.get("impacted_tables", [])
            
            print("🔴 【严重阻断】触发熔断报警！")
            print(f"🔴 变更源：{table}.{col}")
            print(f"🔴 将导致下游任务失败：{impact_list}")
        else:
            print("✅ 无下游依赖或变更安全，继续运行。")
            
    except Exception as e:
        print(f"❌ 检测失败，API调用异常: {e}")
if __name__ == "__main__":
    run()
