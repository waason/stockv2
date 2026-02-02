import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices):
    exp1 = prices.ewm(span=12, adjust=False).mean()
    exp2 = prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal
    return macd, signal, hist

def create_unified_chart(price_data, analysis_results, visible_analysts=None):
    """
    建立整合圖表，包含 K 線、均線、RSI、MACD 與分析師預測標記。
    """
    df = price_data.copy()
    df['RSI'] = calculate_rsi(df['close'])
    macd, signal, hist = calculate_macd(df['close'])
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Hist'] = hist
    
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.02, 
                       subplot_titles=('股價 K 線與分析預測', 'RSI 指標', 'MACD 指標', '成交量'), 
                       row_heights=[0.5, 0.15, 0.15, 0.2])

    # K 線圖
    fig.add_trace(go.Candlestick(x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'], name='K線'), row=1, col=1)

    # 5日均線
    ma5 = df['close'].rolling(5).mean()
    fig.add_trace(go.Scatter(x=df['date'], y=ma5, line=dict(color='orange', width=1), name='MA5'), row=1, col=1)
    
    # 20日均線
    ma20 = df['close'].rolling(20).mean()
    fig.add_trace(go.Scatter(x=df['date'], y=ma20, line=dict(color='cyan', width=1), name='MA20'), row=1, col=1)

    # 分析師標記
    last_date = df['date'].iloc[-1]
    last_price = df['close'].iloc[-1]
    
    for a in analysis_results:
        if visible_analysts and a['analyst'] not in visible_analysts:
            continue
            
        color = 'green' if a['prediction'] == '看多' else ('red' if a['prediction'] == '看空' else 'gray')
        symbol = 'triangle-up' if a['prediction'] == '看多' else ('triangle-down' if a['prediction'] == '看空' else 'circle')
        
        # 在最後一個交易日標記分析師觀點
        fig.add_trace(go.Scatter(
            x=[last_date], 
            y=[last_price * (1.02 if a['prediction'] == '看多' else 0.98)],
            mode='markers+text',
            marker=dict(symbol=symbol, size=12, color=color),
            text=[a['analyst']],
            textposition="top center" if a['prediction'] == '看多' else "bottom center",
            name=f"{a['analyst']} 訊號"
        ), row=1, col=1)

    # RSI 子圖
    fig.add_trace(go.Scatter(x=df['date'], y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'), row=2, col=1)
    fig.add_shape(type="line", x0=df['date'].min(), y0=70, x1=df['date'].max(), y1=70, line=dict(color="red", dash="dash"), row=2, col=1)
    fig.add_shape(type="line", x0=df['date'].min(), y0=30, x1=df['date'].max(), y1=30, line=dict(color="green", dash="dash"), row=2, col=1)

    # MACD 子圖
    fig.add_trace(go.Scatter(x=df['date'], y=df['MACD'], name='MACD', line=dict(color='white')), row=3, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['MACD_Signal'], name='Signal', line=dict(color='yellow')), row=3, col=1)
    fig.add_trace(go.Bar(x=df['date'], y=df['MACD_Hist'], name='Hist', marker_color='gray'), row=3, col=1)

    # 成交量
    colors = ['green' if df['close'].iloc[i] > df['open'].iloc[i] else 'red' for i in range(len(df))]
    fig.add_trace(go.Bar(x=df['date'], y=df['vol'], name='成交量', marker_color=colors), row=4, col=1)

    # 更新版面
    fig.update_layout(
        title='綜合股票分析看板',
        yaxis_title='價格',
        xaxis_rangeslider_visible=False,
        height=1000,
        template='plotly_dark',
        showlegend=True
    )
    
    return fig
