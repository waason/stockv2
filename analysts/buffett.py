import pandas as pd
from .base_analyst import BaseAnalyst

class BuffettAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("價值投資分析師 (巴菲特風格)")

    def analyze(self, data):
        """
        深度價值投資分析，評估內在價值與安全邊際。
        """
        if data is None or data.empty:
            return {
                "analyst": self.name,
                "score": 50,
                "prediction": "觀望",
                "explanation": "數據不足，無法進行價值分析。",
                "indicators": {}
            }

        df = data.copy()
        df = df.sort_values('date')
        
        # 計算關鍵指標
        current_price = df['close'].iloc[-1]
        
        # 1. 價格穩定性分析 (波動率)
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5)  # 年化波動率
        
        # 2. 趨勢強度分析
        ma20 = df['close'].rolling(20).mean()
        ma60 = df['close'].rolling(60).mean()
        ma120 = df['close'].rolling(120).mean()
        
        # 3. 價值評估 - 相對歷史價格
        price_52w_high = df['close'].tail(252).max()
        price_52w_low = df['close'].tail(252).min()
        price_position = (current_price - price_52w_low) / (price_52w_high - price_52w_low)
        
        # 4. 成交量分析
        avg_volume_20 = df['vol'].tail(20).mean()
        avg_volume_60 = df['vol'].tail(60).mean()
        volume_trend = (avg_volume_20 / avg_volume_60 - 1) * 100 if avg_volume_60 > 0 else 0
        
        # 5. 價格動能
        price_change_1m = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100 if len(df) >= 20 else 0
        price_change_3m = (df['close'].iloc[-1] / df['close'].iloc[-60] - 1) * 100 if len(df) >= 60 else 0
        price_change_6m = (df['close'].iloc[-1] / df['close'].iloc[-120] - 1) * 100 if len(df) >= 120 else 0
        
        # 評分系統
        score = 50
        reasons = []
        
        # 波動率評估 (低波動加分)
        if volatility < 0.25:
            score += 15
            reasons.append(f"股價波動穩定(年化波動率{volatility*100:.1f}%)，符合價值投資標準")
        elif volatility > 0.5:
            score -= 10
            reasons.append(f"股價波動較大(年化波動率{volatility*100:.1f}%)，風險偏高")
        
        # 價格位置評估 (低位加分)
        if price_position < 0.3:
            score += 20
            reasons.append(f"目前價格位於52週低檔區({price_position*100:.1f}%)，具安全邊際")
        elif price_position > 0.8:
            score -= 15
            reasons.append(f"目前價格接近52週高點({price_position*100:.1f}%)，估值偏高")
        else:
            reasons.append(f"價格位於52週區間中段({price_position*100:.1f}%)")
        
        # 均線趨勢評估
        if len(ma20) > 0 and len(ma60) > 0 and len(ma120) > 0:
            ma20_val = ma20.iloc[-1]
            ma60_val = ma60.iloc[-1]
            ma120_val = ma120.iloc[-1]
            
            if current_price > ma20_val > ma60_val > ma120_val:
                score += 15
                reasons.append("多頭排列確立，長期趨勢向上")
            elif current_price < ma20_val < ma60_val < ma120_val:
                score -= 15
                reasons.append("空頭排列，長期趨勢向下，建議觀望")
            elif current_price > ma60_val:
                score += 5
                reasons.append("價格站穩季線之上，中期趨勢良好")
        
        # 成交量趨勢
        if volume_trend > 20:
            score += 10
            reasons.append(f"成交量放大{volume_trend:.1f}%，市場關注度提升")
        elif volume_trend < -20:
            score -= 5
            reasons.append(f"成交量萎縮{abs(volume_trend):.1f}%，市場興趣降低")
        
        # 價格動能評估
        if price_change_3m > 10 and price_change_6m > 15:
            score += 10
            reasons.append(f"中長期表現優異(3M:{price_change_3m:.1f}%, 6M:{price_change_6m:.1f}%)")
        elif price_change_3m < -10 and price_change_6m < -15:
            score -= 10
            reasons.append(f"中長期表現疲弱(3M:{price_change_3m:.1f}%, 6M:{price_change_6m:.1f}%)")
        
        # 限制分數範圍
        score = max(0, min(100, score))
        
        # 生成專業建議
        if score >= 70:
            prediction = "看多"
            summary = "綜合評估顯示該股票具備良好的價值投資特質，建議逢低布局。"
        elif score <= 40:
            prediction = "看空"
            summary = "目前估值偏高或趨勢不佳，建議暫時觀望或減碼。"
        else:
            prediction = "觀望"
            summary = "股票表現中性，建議持續觀察基本面變化。"
        
        explanation = summary + " " + " ".join(reasons)
        
        return {
            "analyst": self.name,
            "score": score,
            "prediction": prediction,
            "explanation": explanation,
            "indicators": {
                "目前價格": round(current_price, 2),
                "52週高點": round(price_52w_high, 2),
                "52週低點": round(price_52w_low, 2),
                "價格位置": f"{price_position*100:.1f}%",
                "年化波動率": f"{volatility*100:.1f}%",
                "1個月漲跌": f"{price_change_1m:+.2f}%",
                "3個月漲跌": f"{price_change_3m:+.2f}%",
                "6個月漲跌": f"{price_change_6m:+.2f}%",
                "成交量變化": f"{volume_trend:+.1f}%"
            }
        }
