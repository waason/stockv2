from .base_analyst import BaseAnalyst

class BuffettAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("巴菲特")

    def analyze(self, data):
        """
        價值投資分析：企業品質與長期持有
        """
        # 模擬基本面指標
        roe = 0.18 # 18%
        gross_margin = 0.40 # 40%
        
        score = 0
        explanation = []
        
        if roe > 0.15:
            score += 50
            explanation.append(f"ROE 為 {roe*100:.1f}%，符合高股東權益報酬率標準。")
        else:
            explanation.append(f"ROE 為 {roe*100:.1f}%，企業獲利能力待觀察。")
            
        if gross_margin > 0.30:
            score += 40
            explanation.append(f"毛利率達 {gross_margin*100:.1f}%，顯示具備良好的競爭護城河。")
            
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "長期持有" if score > 70 else "持續觀察",
            "explanation": " ".join(explanation),
            "indicators": {
                "ROE": roe,
                "GrossMargin": gross_margin
            }
        }
