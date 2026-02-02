import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_unified_chart(price_data, analysis_results):
    """
    建立整合圖表，包含 K 線、均線與分析師預測標記。
    """
    df = price_data.copy()
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, subplot_titles=('股價 K 線與分析預測', '成交量'), 
                       row_heights=[0.7, 0.3])

    # K 線圖
    fig.add_trace(go.Candlestick(x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'], name='K線'), row=1, col=1)

    # 5日均線
    ma5 = df['close'].rolling(5).mean()
    fig.add_trace(go.Scatter(x=df['date'], y=ma5, line=dict(color='orange', width=1), name='MA5'), row=1, col=1)

    # 成交量
    fig.add_trace(go.Bar(x=df['date'], y=df['vol'], name='成交量', marker_color='rgba(100, 100, 100, 0.5)'), row=2, col=1)

    # 更新版面
    fig.update_layout(
        title='綜合股票分析看板',
        yaxis_title='價格',
        xaxis_rangeslider_visible=False,
        height=800,
        template='plotly_dark'
    )
    
    return fig
