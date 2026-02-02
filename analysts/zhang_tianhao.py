import pandas as pd
import numpy as np
from .base_analyst import BaseAnalyst

class ZhangTianhaoAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("技術分析專家 (張天豪)")

    def calculate_rsi(self, prices, period=14):
        """計算RSI指標"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices):
        """計算MACD指標"""
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram

    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """計算布林通道"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    def analyze(self, data):
        """
        深度技術分析：整合多種技術指標進行綜合判斷
        """
        if data is None or data.empty or len(data) < 60:
            return {
                "analyst": self.name,
                "score": 50,
                "prediction": "觀望",
                "explanation": "數據不足，無法進行完整技術分析。",
                "indicators": {}
            }

        df = data.copy()
        df = df.sort_values('date')
        
        current_price = df['close'].iloc[-1]
        
        # 計算技術指標
        rsi = self.calculate_rsi(df['close'])
        macd, signal, histogram = self.calculate_macd(df['close'])
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(df['close'])
        
        # 支撐壓力位
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        
        # 均線系統
        ma5 = df['close'].rolling(5).mean()
        ma10 = df['close'].rolling(10).mean()
        ma20 = df['close'].rolling(20).mean()
        ma60 = df['close'].rolling(60).mean()
        
        # 成交量分析
        vol_ma5 = df['vol'].rolling(5).mean()
        vol_ma20 = df['vol'].rolling(20).mean()
        
        # 評分系統
        score = 50
        signals = []
        
        # 1. RSI分析 (30-70為正常區間)
        current_rsi = rsi.iloc[-1]
        if current_rsi < 30:
            score += 20
            signals.append(f"RSI超賣({current_rsi:.1f})，反彈機會大")
        elif current_rsi > 70:
            score -= 15
            signals.append(f"RSI超買({current_rsi:.1f})，回檔風險高")
        elif 40 <= current_rsi <= 60:
            signals.append(f"RSI中性({current_rsi:.1f})，市場平衡")
        else:
            signals.append(f"RSI為{current_rsi:.1f}")
        
        # 2. MACD分析
        current_macd = macd.iloc[-1]
        current_signal = signal.iloc[-1]
        current_hist = histogram.iloc[-1]
        prev_hist = histogram.iloc[-2] if len(histogram) > 1 else 0
        
        if current_macd > current_signal and current_hist > 0:
            score += 15
            signals.append("MACD黃金交叉，多頭訊號")
        elif current_macd < current_signal and current_hist < 0:
            score -= 15
            signals.append("MACD死亡交叉，空頭訊號")
        
        if current_hist > prev_hist and current_hist > 0:
            score += 5
            signals.append("MACD柱狀圖擴大，動能增強")
        elif current_hist < prev_hist and current_hist < 0:
            score -= 5
            signals.append("MACD柱狀圖擴大，下跌動能增強")
        
        # 3. 布林通道分析
        current_upper = upper_bb.iloc[-1]
        current_middle = middle_bb.iloc[-1]
        current_lower = lower_bb.iloc[-1]
        bb_width = (current_upper - current_lower) / current_middle * 100
        
        if current_price < current_lower:
            score += 15
            signals.append(f"價格觸及布林下軌(${current_lower:.2f})，超賣訊號")
        elif current_price > current_upper:
            score -= 10
            signals.append(f"價格觸及布林上軌(${current_upper:.2f})，超買訊號")
        
        if bb_width < 5:
            signals.append(f"布林通道收斂({bb_width:.1f}%)，醞釀突破")
        elif bb_width > 15:
            signals.append(f"布林通道擴張({bb_width:.1f}%)，波動加劇")
        
        # 4. 均線系統分析
        ma5_val = ma5.iloc[-1]
        ma10_val = ma10.iloc[-1]
        ma20_val = ma20.iloc[-1]
        ma60_val = ma60.iloc[-1]
        
        if current_price > ma5_val > ma10_val > ma20_val > ma60_val:
            score += 20
            signals.append("完美多頭排列，強勢上漲格局")
        elif current_price < ma5_val < ma10_val < ma20_val < ma60_val:
            score -= 20
            signals.append("完美空頭排列，弱勢下跌格局")
        elif current_price > ma20_val:
            score += 10
            signals.append("站穩月線之上，中期偏多")
        elif current_price < ma20_val:
            score -= 10
            signals.append("跌破月線，中期偏空")
        
        # 5. 成交量分析
        current_vol = df['vol'].iloc[-1]
        vol_ma5_val = vol_ma5.iloc[-1]
        vol_ma20_val = vol_ma20.iloc[-1]
        
        if current_vol > vol_ma5_val * 1.5:
            if current_price > df['close'].iloc[-2]:
                score += 10
                signals.append(f"爆量上漲，買盤積極")
            else:
                score -= 10
                signals.append(f"爆量下跌，賣壓沉重")
        elif current_vol < vol_ma20_val * 0.5:
            signals.append("成交量萎縮，觀望氣氛濃厚")
        
        # 6. 支撐壓力分析
        distance_to_high = (recent_high - current_price) / current_price * 100
        distance_to_low = (current_price - recent_low) / current_price * 100
        
        if distance_to_low < 2:
            score += 10
            signals.append(f"接近支撐位${recent_low:.2f}，反彈機會高")
        elif distance_to_high < 2:
            score -= 10
            signals.append(f"接近壓力位${recent_high:.2f}，突破不易")
        
        # 限制分數範圍
        score = max(0, min(100, score))
        
        # 生成專業建議
        if score >= 70:
            prediction = "看多"
            summary = "技術面呈現多頭格局，多項指標支持上漲，建議順勢操作。"
        elif score <= 40:
            prediction = "看空"
            summary = "技術面轉弱，多項指標顯示下跌風險，建議謹慎觀望。"
        else:
            prediction = "觀望"
            summary = "技術面訊號混雜，建議等待明確方向再進場。"
        
        explanation = summary + " " + " ".join(signals)
        
        return {
            "analyst": self.name,
            "score": score,
            "prediction": prediction,
            "explanation": explanation,
            "indicators": {
                "RSI": round(current_rsi, 2),
                "MACD": round(current_macd, 2),
                "MACD訊號線": round(current_signal, 2),
                "布林上軌": round(current_upper, 2),
                "布林中軌": round(current_middle, 2),
                "布林下軌": round(current_lower, 2),
                "MA5": round(ma5_val, 2),
                "MA20": round(ma20_val, 2),
                "MA60": round(ma60_val, 2),
                "支撐位": round(recent_low, 2),
                "壓力位": round(recent_high, 2)
            }
        }
