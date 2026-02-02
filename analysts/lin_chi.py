from .base_analyst import BaseAnalyst

class LynchAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("林奇")

    def analyze(self, data):
        """
        價值成長分析：注重成長性與估值
        """
        # 假設 data 包含基本面數據，這裡先示範邏輯
        # 實際應從 DataManager 獲取基本面資訊
        
        # 模擬數據
        pe_ratio = 15 
        eps_growth = 0.20 # 20%
        
        peg = pe_ratio / (eps_growth * 100)
        
        score = 0
        explanation = []
        
        if peg < 1:
            score = 80
            explanation.append(f"PEG 為 {peg:.2f}，低於 1，顯示股價相對於成長性被低估。")
        elif peg < 1.5:
            score = 60
            explanation.append(f"PEG 為 {peg:.2f}，估值尚屬合理。")
        else:
            score = 30
            explanation.append(f"PEG 為 {peg:.2f}，估值偏高，投資宜謹慎。")
            
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "強烈推薦" if score >= 80 else ("推薦" if score >= 60 else "中性"),
            "explanation": " ".join(explanation),
            "indicators": {
                "PEG": peg
            }
        }
