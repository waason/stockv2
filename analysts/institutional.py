import pandas as pd
from .base_analyst import BaseAnalyst

class InstitutionalAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("三大法人籌碼分析師")

    def analyze(self, data, institutional_data=None):
        """
        深度三大法人籌碼分析：評估外資、投信、自營商的買賣動向與影響力
        """
        if institutional_data is None or institutional_data.empty:
            return {
                "analyst": self.name,
                "score": 50,
                "prediction": "觀望",
                "explanation": "缺乏三大法人數據，無法進行籌碼分析。",
                "indicators": {}
            }

        df = institutional_data.copy()
        df = df.sort_values('date')
        
        # 計算各法人近期買賣超
        recent_5 = df.tail(5)
        recent_10 = df.tail(10)
        recent_20 = df.tail(20)
        
        # 安全取得欄位資料
        foreign_5 = recent_5.get('Foreign_Investor', pd.Series([0])).fillna(0).sum()
        it_5 = recent_5.get('Investment_Trust', pd.Series([0])).fillna(0).sum()
        dealer_5 = recent_5.get('Dealer', pd.Series([0])).fillna(0).sum()
        
        foreign_10 = recent_10.get('Foreign_Investor', pd.Series([0])).fillna(0).sum()
        it_10 = recent_10.get('Investment_Trust', pd.Series([0])).fillna(0).sum()
        dealer_10 = recent_10.get('Dealer', pd.Series([0])).fillna(0).sum()
        
        foreign_20 = recent_20.get('Foreign_Investor', pd.Series([0])).fillna(0).sum()
        it_20 = recent_20.get('Investment_Trust', pd.Series([0])).fillna(0).sum()
        dealer_20 = recent_20.get('Dealer', pd.Series([0])).fillna(0).sum()
        
        total_5 = foreign_5 + it_5 + dealer_5
        total_10 = foreign_10 + it_10 + dealer_10
        total_20 = foreign_20 + it_20 + dealer_20
        
        # 評分系統
        score = 50
        insights = []
        
        # 1. 外資分析 (權重最高)
        if foreign_5 > 0:
            if foreign_10 > 0 and foreign_20 > 0:
                score += 25
                insights.append(f"外資連續買超(5日:{foreign_5:.0f}張, 10日:{foreign_10:.0f}張, 20日:{foreign_20:.0f}張)，多頭主力明確")
            else:
                score += 15
                insights.append(f"外資近期轉為買超(5日:{foreign_5:.0f}張)，籌碼面改善")
        elif foreign_5 < 0:
            if foreign_10 < 0 and foreign_20 < 0:
                score -= 20
                insights.append(f"外資持續賣超(5日:{foreign_5:.0f}張, 10日:{foreign_10:.0f}張, 20日:{foreign_20:.0f}張)，籌碼面疲弱")
            else:
                score -= 10
                insights.append(f"外資近期轉為賣超(5日:{foreign_5:.0f}張)，需觀察後續動向")
        else:
            insights.append("外資近期無明顯買賣動作")
        
        # 2. 投信分析 (中期指標)
        if it_5 > 0:
            if it_10 > 0:
                score += 20
                insights.append(f"投信積極布局(5日:{it_5:.0f}張, 10日:{it_10:.0f}張)，中期看好")
            else:
                score += 10
                insights.append(f"投信開始買超(5日:{it_5:.0f}張)，籌碼轉強")
        elif it_5 < 0:
            if it_10 < 0:
                score -= 15
                insights.append(f"投信持續賣超(5日:{it_5:.0f}張, 10日:{it_10:.0f}張)，中期偏空")
            else:
                score -= 5
                insights.append(f"投信近期賣超(5日:{it_5:.0f}張)")
        
        # 3. 自營商分析 (短期指標)
        if dealer_5 > 0:
            score += 10
            insights.append(f"自營商買超(5日:{dealer_5:.0f}張)，短線偏多")
        elif dealer_5 < 0:
            score -= 5
            insights.append(f"自營商賣超(5日:{dealer_5:.0f}張)，短線偏空")
        
        # 4. 三大法人合計分析
        if total_5 > 0:
            if total_10 > 0 and total_20 > 0:
                score += 20
                insights.append(f"三大法人合力買超(5日:{total_5:.0f}張, 10日:{total_10:.0f}張, 20日:{total_20:.0f}張)，籌碼面極佳")
            else:
                score += 10
                insights.append(f"三大法人合計買超(5日:{total_5:.0f}張)，籌碼面轉強")
        elif total_5 < 0:
            if total_10 < 0 and total_20 < 0:
                score -= 15
                insights.append(f"三大法人合計賣超(5日:{total_5:.0f}張, 10日:{total_10:.0f}張, 20日:{total_20:.0f}張)，賣壓沉重")
            else:
                score -= 8
                insights.append(f"三大法人合計賣超(5日:{total_5:.0f}張)")
        
        # 5. 籌碼趨勢一致性
        consistency_score = 0
        if foreign_5 > 0:
            consistency_score += 1
        if it_5 > 0:
            consistency_score += 1
        if dealer_5 > 0:
            consistency_score += 1
        
        if consistency_score == 3:
            score += 15
            insights.append("三大法人買盤一致，籌碼面高度樂觀")
        elif consistency_score == 0:
            score -= 10
            insights.append("三大法人賣盤一致，籌碼面高度悲觀")
        else:
            insights.append("法人動向分歧，籌碼面中性")
        
        # 6. 買賣超強度分析
        if abs(total_5) > 1000:
            if total_5 > 0:
                score += 10
                insights.append(f"大量買超({total_5:.0f}張)，籌碼集中度提升")
            else:
                score -= 10
                insights.append(f"大量賣超({abs(total_5):.0f}張)，籌碼鬆動")
        
        # 限制分數範圍
        score = max(0, min(100, score))
        
        # 生成專業建議
        if score >= 70:
            prediction = "看多"
            summary = "三大法人籌碼面呈現多頭格局，主力積極布局，建議跟隨法人腳步。"
        elif score <= 40:
            prediction = "看空"
            summary = "三大法人籌碼面轉弱，主力持續調節，建議謹慎觀望。"
        else:
            prediction = "觀望"
            summary = "三大法人籌碼面中性，建議等待明確訊號。"
        
        explanation = summary + " " + " ".join(insights)
        
        return {
            "analyst": self.name,
            "score": score,
            "prediction": prediction,
            "explanation": explanation,
            "indicators": {
                "外資5日": f"{foreign_5:+.0f}張",
                "外資10日": f"{foreign_10:+.0f}張",
                "外資20日": f"{foreign_20:+.0f}張",
                "投信5日": f"{it_5:+.0f}張",
                "投信10日": f"{it_10:+.0f}張",
                "自營商5日": f"{dealer_5:+.0f}張",
                "合計5日": f"{total_5:+.0f}張",
                "合計10日": f"{total_10:+.0f}張",
                "合計20日": f"{total_20:+.0f}張"
            }
        }
        
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
