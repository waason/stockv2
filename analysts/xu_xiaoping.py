import numpy as np
from .base_analyst import BaseAnalyst

class XuXiaopingAnalyst(BaseAnalyst):
    def __init__(self):
        super().__init__("徐小萍")

    def analyze(self, data):
        """
        量化分析：風險與回撤
        """
        df = data.copy()
        returns = df['close'].pct_change().dropna()
        
        # 計算夏普比率 (假設無風險利率 0)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        
        # 計算最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        score = 50
        explanation = [f"基於量化回測，夏普比率為 {sharpe:.2f}。"]
        
        if max_drawdown > -0.15:
            score += 30
            explanation.append(f"最大回撤僅 {max_drawdown*100:.1f}%，風險控制極佳。")
        else:
            score -= 20
            explanation.append(f"最大回撤達 {max_drawdown*100:.1f}%，波動風險較大。")
            
        return {
            "analyst": self.name,
            "score": score,
            "prediction": "風險平衡" if score > 60 else "高風險低報酬",
            "explanation": " ".join(explanation),
            "indicators": {
                "Sharpe": sharpe,
                "MaxDrawdown": max_drawdown
            }
        }
