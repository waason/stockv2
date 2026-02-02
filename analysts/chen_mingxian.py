import pandas as pd
import numpy as np
from .base_analyst import BaseAnalyst

class ChenMingxianAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("陳明憲")

    def analyze(self, data):
        """
        技術指標分析：MA, RSI, MACD
        """
        df = data.copy()
        
        # 計算 MA
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        
        # 計算 RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        last_close = df['close'].iloc[-1]
        last_ma5 = df['MA5'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        score = 0
        explanation = []
        
        if last_close > last_ma5:
            score += 30
            explanation.append("股價站在 5 日均線之上，短期走勢強勁。")
        else:
            explanation.append("股價在 5 日均線之下，需觀察支撐。")
            
        if 30 < last_rsi < 70:
            score += 40
            explanation.append(f"RSI 為 {last_rsi:.2f}，處於中性區間。")
        elif last_rsi <= 30:
            score += 60
            explanation.append(f"RSI 為 {last_rsi:.2f}，進入超賣區，可能有反彈機會。")
        else:
            score += 20
            explanation.append(f"RSI 為 {last_rsi:.2f}，進入超買區，需特別留意回檔。")
            
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "看多" if score > 50 else "觀望",
            "explanation": " ".join(explanation),
            "indicators": {
                "MA5": last_ma5,
                "RSI": last_rsi
            }
        }
