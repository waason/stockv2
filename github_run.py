import argparse
from orchestrator import StockAnalysisOrchestrator
import json
import os
import numpy as np

def convert_numpy_types(obj):
    """
    Recursively convert numpy types to native Python types for JSON serialization.
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def main():
    parser = argparse.ArgumentParser(description="GitHub 股票自動分析工具")
    parser.add_argument("--stock_id", type=str, default="2330", help="股票代號")
    args = parser.parse_args()

    # 初始化協調器
    orchestrator = StockAnalysisOrchestrator()
    
    # 執行全分析
    print(f"--- 開始處理股票: {args.stock_id} ---")
    result = orchestrator.run_full_analysis(args.stock_id)
    
    if "error" in result:
        print(f"錯誤: {result['error']}")
        return

    # 輸出簡易報告到虛擬環境
    report_content = f"""
# 股票分析報告: {args.stock_id}
- 目前價格: {result['current_price']}
- 綜合預測: {result['prediction']['final_trend']}
- 新聞摘要: {result['news_summary']}

## 分析師觀點:
"""
    for a in result['analysis']:
        report_content += f"- **{a['analyst']}**: {a['prediction']} (評分: {a['score']})\n  - {a['explanation']}\n"

    # 存檔供 Actions 成生成 Artifacts
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    with open(f"reports/report_{args.stock_id}.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    # Convert numpy types before JSON serialization
    result_serializable = convert_numpy_types(result)
    
    with open(f"reports/result_{args.stock_id}.json", "w", encoding="utf-8") as f:
        json.dump(result_serializable, f, ensure_ascii=False, indent=4)

    print(f"--- 分析完成，報告已儲存至 reports 夾 ---")

if __name__ == "__main__":
    main()
