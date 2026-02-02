from .base_analyst import BaseAnalyst

class ZhangTianhaoAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("張天豪")

    def analyze(self, data):
        """
        視覺圖形分析：形態與支撐壓力
        """
        df = data.copy()
        last_30 = df.iloc[-30:]
        
        highest = last_30['high'].max()
        lowest = last_30['low'].min()
        current = df['close'].iloc[-1]
        
        score = 50
        explanation = []
        
        near_support = (current - lowest) / lowest < 0.03
        near_resistance = (highest - current) / current < 0.03
        
        if near_support:
            score += 30
            explanation.append("股價接近 30 日支撐位，具備跌深反彈潛力。")
        elif near_resistance:
            score -= 10
            explanation.append("股價接近 30 日壓力位，短期內可能有賣壓。")
        else:
            explanation.append("股價處於盤整區間，建議等待進一步形態確認。")
            
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "支撐區布局" if near_support else "區間整理",
            "explanation": " ".join(explanation),
            "indicators": {
                "30DRestistance": highest,
                "30DSupport": lowest
            }
        }
