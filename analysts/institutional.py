import pandas as pd
from .base_analyst import BaseAnalyst

class InstitutionalAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("三大法人分析師")

    def analyze(self, data, institutional_data=None):
        """
        分析三大法人買賣超趨勢。
        """
        if institutional_data is None or institutional_data.empty:
            return {
                "analyst": self.name,
                "score": 50,
                "prediction": "觀望",
                "explanation": "缺乏三大法人數據，無法進行分析。",
                "indicators": {}
            }

        df = institutional_data.copy()
        # 確保日期排序
        df = df.sort_values('date')
        
        # 取得最近 5 個交易日
        recent_5 = df.tail(5)
        
        # 計算外資與投信的買賣超總和
        foreign_buy = recent_5['Foreign_Investor'].sum()
        it_buy = recent_5['Investment_Trust'].sum()
        dealer_buy = recent_5['Dealer'].sum()
        
        total_buy = foreign_buy + it_buy + dealer_buy
        
        score = 50
        explanation = []
        
        if foreign_buy > 0:
            score += 15
            explanation.append("外資近期呈現買超趨勢。")
        else:
            score -= 10
            explanation.append("外資近期呈現賣超，需留意。")
            
        if it_buy > 0:
            score += 15
            explanation.append("投信積極加碼，籌碼面看好。")
        else:
            explanation.append("投信動向不明。")
            
        if total_buy > 0:
            score += 20
            explanation.append("整體三大法人合力買超，支撐強勁。")
        else:
            score -= 10
            explanation.append("法人整體賣壓較重。")
            
        # 限制分數在 0-100 之間
        score = max(0, min(100, score))
        
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "看多" if score > 60 else ("看空" if score < 40 else "觀望"),
            "explanation": " ".join(explanation),
            "indicators": {
                "外資買賣": foreign_buy,
                "投信買賣": it_buy,
                "合計買賣": total_buy
            }
        }
