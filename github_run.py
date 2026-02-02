import argparse
from orchestrator import StockAnalysisOrchestrator
import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for CI
import matplotlib.pyplot as plt
from datetime import datetime

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

def generate_charts(stock_id, price_data, analysis_results, inst_data):
    """
    Generate analysis charts and save as PNG files.
    """
    charts = {}
    
    # Chart 1: Price and Moving Averages
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Price chart
    ax1.plot(price_data['date'], price_data['close'], label='收盤價', linewidth=2)
    ma5 = price_data['close'].rolling(5).mean()
    ma20 = price_data['close'].rolling(20).mean()
    ax1.plot(price_data['date'], ma5, label='MA5', alpha=0.7)
    ax1.plot(price_data['date'], ma20, label='MA20', alpha=0.7)
    
    # Add analyst signals
    last_price = price_data['close'].iloc[-1]
    last_date = price_data['date'].iloc[-1]
    for a in analysis_results:
        if a['prediction'] == '看多':
            ax1.scatter([last_date], [last_price * 1.02], marker='^', s=100, 
                       color='green', label=f"{a['analyst']} 看多", zorder=5)
        elif a['prediction'] == '看空':
            ax1.scatter([last_date], [last_price * 0.98], marker='v', s=100, 
                       color='red', label=f"{a['analyst']} 看空", zorder=5)
    
    ax1.set_ylabel('價格 (TWD)')
    ax1.set_title(f'{stock_id} 股價分析', fontsize=14, fontweight='bold')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # Volume chart
    colors = ['green' if price_data['close'].iloc[i] > price_data['open'].iloc[i] 
              else 'red' for i in range(len(price_data))]
    ax2.bar(price_data['date'], price_data['vol'], color=colors, alpha=0.6)
    ax2.set_ylabel('成交量')
    ax2.set_xlabel('日期')
    ax2.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_path = f'reports/chart_price_{stock_id}.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    charts['price'] = chart_path
    
    # Chart 2: Institutional Investors (if available)
    if inst_data is not None and not inst_data.empty:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        inst_data_sorted = inst_data.sort_values('date')
        if 'Foreign_Investor' in inst_data_sorted.columns:
            ax.plot(inst_data_sorted['date'], inst_data_sorted['Foreign_Investor'], 
                   label='外資', marker='o', linewidth=2)
        if 'Investment_Trust' in inst_data_sorted.columns:
            ax.plot(inst_data_sorted['date'], inst_data_sorted['Investment_Trust'], 
                   label='投信', marker='s', linewidth=2)
        if 'Dealer' in inst_data_sorted.columns:
            ax.plot(inst_data_sorted['date'], inst_data_sorted['Dealer'], 
                   label='自營商', marker='^', linewidth=2)
        
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax.set_ylabel('買賣超 (張)')
        ax.set_xlabel('日期')
        ax.set_title('三大法人買賣超趨勢', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        chart_path = f'reports/chart_institutional_{stock_id}.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()
        charts['institutional'] = chart_path
    
    return charts

def generate_html_report(stock_id, result, charts):
    """
    Generate a professional HTML report with embedded charts.
    """
    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票分析報告 - {stock_id}</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric {{
            display: inline-block;
            margin: 10px 20px;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #333;
        }}
        .chart {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .chart img {{
            width: 100%;
            height: auto;
        }}
        .analysts {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .analyst-card {{
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            background: #f9f9f9;
        }}
        .analyst-name {{
            font-weight: bold;
            font-size: 1.2em;
            color: #333;
        }}
        .prediction {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .bullish {{ background: #4caf50; color: white; }}
        .bearish {{ background: #f44336; color: white; }}
        .neutral {{ background: #ff9800; color: white; }}
        .score {{
            font-size: 1.5em;
            color: #667eea;
            font-weight: bold;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 股票分析報告</h1>
        <p>股票代號: {stock_id} | 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📈 市場概況</h2>
        <div class="metric">
            <div class="metric-label">目前價格</div>
            <div class="metric-value">${result['current_price']:.2f}</div>
        </div>
        <div class="metric">
            <div class="metric-label">綜合預測</div>
            <div class="metric-value">{result['prediction']['final_trend']}</div>
        </div>
        <div class="metric">
            <div class="metric-label">新聞摘要</div>
            <div class="metric-value">{result['news_summary']}</div>
        </div>
    </div>
    
    <div class="chart">
        <h2>📊 價格走勢與分析師觀點</h2>
        <img src="chart_price_{stock_id}.png" alt="價格走勢圖">
    </div>
"""
    
    if 'institutional' in charts:
        html += f"""
    <div class="chart">
        <h2>🏢 三大法人買賣超趨勢</h2>
        <img src="chart_institutional_{stock_id}.png" alt="法人買賣超">
    </div>
"""
    
    html += """
    <div class="analysts">
        <h2>👨‍💼 分析師專業觀點</h2>
"""
    
    for a in result['analysis']:
        prediction_class = 'bullish' if a['prediction'] == '看多' else ('bearish' if a['prediction'] == '看空' else 'neutral')
        html += f"""
        <div class="analyst-card">
            <div class="analyst-name">
                {a['analyst']}
                <span class="prediction {prediction_class}">{a['prediction']}</span>
                <span class="score">{a['score']}</span>
            </div>
            <p>{a['explanation']}</p>
            <div style="color: #666; font-size: 0.9em;">
                核心指標: {', '.join([f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}" for k, v in a['indicators'].items()])}
            </div>
        </div>
"""
    
    html += """
    </div>
    
    <div class="footer">
        <p>本報告由自動化股票分析系統生成</p>
        <p>數據來源: FinMind API | 僅供參考，不構成投資建議</p>
    </div>
</body>
</html>
"""
    
    return html

def generate_summary_report(all_results):
    """
    Generate a summary report comparing multiple stocks.
    """
    html = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多股票分析匯總報告</title>
    <style>
        body {{
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            background: white;
            border-collapse: collapse;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{
            background: #f9f9f9;
        }}
        .bullish {{ color: #4caf50; font-weight: bold; }}
        .bearish {{ color: #f44336; font-weight: bold; }}
        .neutral {{ color: #ff9800; font-weight: bold; }}
        .stock-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
        .stock-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 多股票分析匯總報告</h1>
        <p>分析股票數量: {len(all_results)} | 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>股票代號</th>
                <th>目前價格</th>
                <th>綜合預測</th>
                <th>平均評分</th>
                <th>看多分析師</th>
                <th>看空分析師</th>
                <th>詳細報告</th>
            </tr>
        </thead>
        <tbody>
"""
    
    for item in all_results:
        stock_id = item['stock_id']
        result = item['result']
        
        # 計算統計
        bullish_count = sum(1 for a in result['analysis'] if a['prediction'] == '看多')
        bearish_count = sum(1 for a in result['analysis'] if a['prediction'] == '看空')
        avg_score = sum(a['score'] for a in result['analysis']) / len(result['analysis'])
        
        prediction_class = 'bullish' if result['prediction']['final_trend'] == '看多' else (
            'bearish' if result['prediction']['final_trend'] == '看空' else 'neutral')
        
        html += f"""
            <tr>
                <td><strong>{stock_id}</strong></td>
                <td>${result['current_price']:.2f}</td>
                <td class="{prediction_class}">{result['prediction']['final_trend']}</td>
                <td>{avg_score:.1f}</td>
                <td>{bullish_count} 位</td>
                <td>{bearish_count} 位</td>
                <td><a href="report_{stock_id}.html" class="stock-link">查看詳情 →</a></td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
</body>
</html>
"""
    
    return html

def main():
    parser = argparse.ArgumentParser(description="GitHub 股票自動分析工具")
    parser.add_argument("--stock_id", type=str, default="2330", 
                       help="股票代號，多個股票用逗號分隔 (例如: 2330,2317,2454)")
    args = parser.parse_args()

    # 解析股票代號（支援多個）
    stock_ids = [s.strip() for s in args.stock_id.split(',')]
    
    # 初始化協調器
    orchestrator = StockAnalysisOrchestrator()
    
    # 批次分析所有股票
    all_results = []
    for stock_id in stock_ids:
        print(f"\n{'='*60}")
        print(f"開始處理股票: {stock_id}")
        print(f"{'='*60}")
        
        result = orchestrator.run_full_analysis(stock_id)
        
        if "error" in result:
            print(f"❌ 錯誤: {result['error']}")
            continue
        
        all_results.append({
            'stock_id': stock_id,
            'result': result
        })
    
    # 創建報告目錄
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # 處理每個股票
    for item in all_results:
        stock_id = item['stock_id']
        result = item['result']
        
        # 獲取數據用於圖表生成
        price_data = orchestrator.data_manager.get_stock_data(stock_id)
        inst_data = orchestrator.data_manager.get_institutional_data(stock_id)
        
        # 生成圖表
        print(f"📊 正在生成 {stock_id} 圖表...")
        charts = generate_charts(stock_id, price_data, result['analysis'], inst_data)
        
        # 生成 HTML 報告
        print(f"📝 正在生成 {stock_id} HTML 報告...")
        html_content = generate_html_report(stock_id, result, charts)
        with open(f"reports/report_{stock_id}.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # 生成簡易 Markdown 報告
        report_content = f"""
# 股票分析報告: {stock_id}
- 目前價格: {result['current_price']}
- 綜合預測: {result['prediction']['final_trend']}
- 新聞摘要: {result['news_summary']}

## 分析師觀點:
"""
        for a in result['analysis']:
            report_content += f"- **{a['analyst']}**: {a['prediction']} (評分: {a['score']})\n  - {a['explanation']}\n"
        
        with open(f"reports/report_{stock_id}.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        # 保存 JSON 數據
        result_serializable = convert_numpy_types(result)
        with open(f"reports/result_{stock_id}.json", "w", encoding="utf-8") as f:
            json.dump(result_serializable, f, ensure_ascii=False, indent=4)
        
        print(f"✅ {stock_id} 完成！")
    
    # 如果分析了多個股票，生成匯總報告
    if len(all_results) > 1:
        print(f"\n📊 正在生成匯總報告...")
        summary_html = generate_summary_report(all_results)
        with open(f"reports/summary.html", "w", encoding="utf-8") as f:
            f.write(summary_html)
        print(f"✅ 匯總報告已生成")

    print(f"\n{'='*60}")
    print(f"🎉 分析完成！")
    print(f"{'='*60}")
    print(f"✅ 已分析股票: {', '.join([item['stock_id'] for item in all_results])}")
    print(f"✅ 報告位置: reports/")
    if len(all_results) > 1:
        print(f"✅ 匯總報告: reports/summary.html")

if __name__ == "__main__":
    main()
