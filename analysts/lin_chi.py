import pandas as pd
import numpy as np
from .base_analyst import BaseAnalyst

class LinChiAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("趨勢動能分析師 (林奇)")

    def analyze(self, data):
        """
        深度趨勢與動能分析：評估市場趨勢強度與持續性
        """
        if data is None or data.empty or len(data) < 60:
            return {
                "analyst": self.name,
                "score": 50,
                "prediction": "觀望",
                "explanation": "數據不足，無法進行趨勢分析。",
                "indicators": {}
            }

        df = data.copy()
        df = df.sort_values('date')
        
        current_price = df['close'].iloc[-1]
        
        # 計算多週期均線
        ma5 = df['close'].rolling(5).mean()
        ma10 = df['close'].rolling(10).mean()
        ma20 = df['close'].rolling(20).mean()
        ma60 = df['close'].rolling(60).mean()
        
        # 計算動能指標
        momentum_5 = (df['close'] / df['close'].shift(5) - 1) * 100
        momentum_20 = (df['close'] / df['close'].shift(20) - 1) * 100
        momentum_60 = (df['close'] / df['close'].shift(60) - 1) * 100
        
        # 計算價格波動率
        returns = df['close'].pct_change()
        volatility_20 = returns.rolling(20).std() * np.sqrt(252) * 100
        
        # 計算趨勢強度 (ADX概念)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(14).mean()
        
        # 計算價格通道
        highest_20 = df['high'].rolling(20).max()
        lowest_20 = df['low'].rolling(20).min()
        channel_position = (current_price - lowest_20.iloc[-1]) / (highest_20.iloc[-1] - lowest_20.iloc[-1]) * 100
        
        # 成交量趨勢
        vol_ma5 = df['vol'].rolling(5).mean()
        vol_ma20 = df['vol'].rolling(20).mean()
        vol_trend = (vol_ma5.iloc[-1] / vol_ma20.iloc[-1] - 1) * 100
        
        # 評分系統
        score = 50
        insights = []
        
        # 1. 均線趨勢評估
        ma5_val = ma5.iloc[-1]
        ma10_val = ma10.iloc[-1]
        ma20_val = ma20.iloc[-1]
        ma60_val = ma60.iloc[-1]
        
        # 多頭排列檢查
        if ma5_val > ma10_val > ma20_val > ma60_val:
            score += 25
            insights.append("均線呈現完美多頭排列，趨勢強勁向上")
            
            # 檢查均線間距（趨勢強度）
            ma_spread = (ma5_val - ma60_val) / ma60_val * 100
            if ma_spread > 5:
                score += 10
                insights.append(f"均線發散度{ma_spread:.1f}%，上升動能強勁")
        elif ma5_val < ma10_val < ma20_val < ma60_val:
            score -= 25
            insights.append("均線呈現完美空頭排列，趨勢明顯向下")
            
            ma_spread = (ma60_val - ma5_val) / ma60_val * 100
            if ma_spread > 5:
                score -= 10
                insights.append(f"均線發散度{ma_spread:.1f}%，下跌動能強勁")
        else:
            # 混亂排列
            if current_price > ma20_val:
                score += 5
                insights.append("價格站穩月線，中期趨勢偏多")
            else:
                score -= 5
                insights.append("價格跌破月線，中期趨勢偏空")
        
        # 2. 動能分析
        current_momentum_5 = momentum_5.iloc[-1]
        current_momentum_20 = momentum_20.iloc[-1]
        current_momentum_60 = momentum_60.iloc[-1]
        
        if current_momentum_5 > 3 and current_momentum_20 > 5:
            score += 15
            insights.append(f"短中期動能強勁(5日:{current_momentum_5:.1f}%, 20日:{current_momentum_20:.1f}%)")
        elif current_momentum_5 < -3 and current_momentum_20 < -5:
            score -= 15
            insights.append(f"短中期動能疲弱(5日:{current_momentum_5:.1f}%, 20日:{current_momentum_20:.1f}%)")
        
        # 長期動能
        if current_momentum_60 > 15:
            score += 10
            insights.append(f"長期趨勢強勁(60日漲幅{current_momentum_60:.1f}%)")
        elif current_momentum_60 < -15:
            score -= 10
            insights.append(f"長期趨勢疲弱(60日跌幅{abs(current_momentum_60):.1f}%)")
        
        # 3. 波動率分析
        current_volatility = volatility_20.iloc[-1]
        if current_volatility < 20:
            score += 5
            insights.append(f"波動率低({current_volatility:.1f}%)，趨勢穩定")
        elif current_volatility > 40:
            score -= 5
            insights.append(f"波動率高({current_volatility:.1f}%)，市場不穩定")
        
        # 4. 價格通道位置
        if channel_position > 80:
            score += 10
            insights.append(f"價格位於通道頂部({channel_position:.1f}%)，強勢格局")
        elif channel_position < 20:
            score -= 10
            insights.append(f"價格位於通道底部({channel_position:.1f}%)，弱勢格局")
        else:
            insights.append(f"價格位於通道中段({channel_position:.1f}%)")
        
        # 5. 成交量趨勢配合
        if vol_trend > 20:
            if current_momentum_5 > 0:
                score += 10
                insights.append(f"量價齊揚(量增{vol_trend:.1f}%)，多頭氣盛")
            else:
                score -= 5
                insights.append(f"量增價跌(量增{vol_trend:.1f}%)，賣壓沉重")
        elif vol_trend < -20:
            insights.append(f"成交量萎縮({abs(vol_trend):.1f}%)，市場觀望")
        
        # 6. 趨勢一致性檢查
        trend_consistency = 0
        if current_momentum_5 > 0:
            trend_consistency += 1
        if current_momentum_20 > 0:
            trend_consistency += 1
        if current_momentum_60 > 0:
            trend_consistency += 1
        
        if trend_consistency == 3:
            score += 10
            insights.append("短中長期趨勢一致向上，趨勢可靠度高")
        elif trend_consistency == 0:
            score -= 10
            insights.append("短中長期趨勢一致向下，跌勢明確")
        else:
            insights.append("多週期趨勢不一致，方向尚未明朗")
        
        # 限制分數範圍
        score = max(0, min(100, score))
        
        # 生成專業建議
        if score >= 70:
            prediction = "看多"
            summary = "趨勢分析顯示多頭格局明確，動能強勁，建議順勢做多。"
        elif score <= 40:
            prediction = "看空"
            summary = "趨勢分析顯示空頭格局，動能疲弱，建議迴避或做空。"
        else:
            prediction = "觀望"
            summary = "趨勢方向不明確，建議等待趨勢確立後再進場。"
        
        explanation = summary + " " + " ".join(insights)
        
        return {
            "analyst": self.name,
            "score": score,
            "prediction": prediction,
            "explanation": explanation,
            "indicators": {
                "5日動能": f"{current_momentum_5:+.2f}%",
                "20日動能": f"{current_momentum_20:+.2f}%",
                "60日動能": f"{current_momentum_60:+.2f}%",
                "波動率": f"{current_volatility:.1f}%",
                "通道位置": f"{channel_position:.1f}%",
                "MA5": round(ma5_val, 2),
                "MA10": round(ma10_val, 2),
                "MA20": round(ma20_val, 2),
                "MA60": round(ma60_val, 2),
                "成交量趨勢": f"{vol_trend:+.1f}%"
            }
        }
