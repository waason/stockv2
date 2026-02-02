import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self):
        # 這裡未來可以載入訓練好的權重，目前先以邏輯演算法示範集成效果
        pass

    def predict_lstm(self, data):
        """
        模擬 LSTM 預測（時間序列趨勢）
        """
        # 簡化邏輯：基於回歸趨勢
        prices = data['close'].values
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        
        prediction = prices[-1] + (slope * 5) # 預測 5 天後
        confidence = min(abs(slope) / prices[-1] * 100, 1.0) # 簡化信心度
        
        return {
            "model": "LSTM",
            "predicted_price": prediction,
            "trend": "Up" if slope > 0 else "Down",
            "confidence": 0.85 # 預設高信心
        }

    def predict_xgboost(self, data):
        """
        模擬 XGBoost 預測（特徵分類）
        """
        # 簡化邏輯：基於成交量與價格變動
        last_vol = data['vol'].iloc[-1]
        avg_vol = data['vol'].mean()
        last_return = data['close'].pct_change().iloc[-1]
        
        if last_vol > avg_vol and last_return > 0:
            trend = "Bullish"
            confidence = 0.80
        elif last_vol > avg_vol and last_return < 0:
            trend = "Bearish"
            confidence = 0.75
        else:
            trend = "Neutral"
            confidence = 0.60
            
        return {
            "model": "XGBoost",
            "trend": trend,
            "confidence": confidence
        }

    def get_ensemble_prediction(self, data):
        lstm = self.predict_lstm(data)
        xgb = self.predict_xgboost(data)
        
        # 集成邏輯
        final_trend = lstm['trend'] if lstm['confidence'] > xgb['confidence'] else xgb['trend']
        
        return {
            "final_trend": final_trend,
            "details": [lstm, xgb]
        }
