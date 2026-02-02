import logging
import yaml
from data_layer.data_manager import DataManager
from analysts.chen_mingxian import ChenMingxianAnalyst
from analysts.lin_chi import LynchAnalyst
from analysts.buffett import BuffettAnalyst
from analysts.xu_xiaoping import XuXiaopingAnalyst
from analysts.zhang_tianhao import ZhangTianhaoAnalyst
from prediction.prediction_engine import PredictionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAnalysisOrchestrator:
    def __init__(self, config_path="config.yaml"):
        self.data_manager = DataManager(config_path)
        self.prediction_engine = PredictionEngine()
        self.analysts = [
            ChenMingxianAnalyst(),
            LynchAnalyst(),
            BuffettAnalyst(),
            XuXiaopingAnalyst(),
            ZhangTianhaoAnalyst()
        ]

    def run_full_analysis(self, stock_id):
        logger.info(f"開始分析股票: {stock_id}")
        
        # 1. 獲取數據
        price_data = self.data_manager.get_stock_data(stock_id)
        if price_data is None:
            return {"error": "無法獲取股價數據"}
            
        inst_data = self.data_manager.get_institutional_data(stock_id)
        news_data = self.data_manager.get_news_data(stock_id)
        
        # 2. 執行分析師分析
        analysis_results = []
        for analyst in self.analysts:
            try:
                result = analyst.analyze(price_data)
                analysis_results.append(result)
            except Exception as e:
                logger.error(f"分析師 {analyst.name} 執行出錯: {e}")
                
        # 3. 執行預測
        prediction = self.prediction_engine.get_ensemble_prediction(price_data)
        
        # 4. 整合報告
        summary = {
            "stock_id": stock_id,
            "current_price": price_data['close'].iloc[-1],
            "analysis": analysis_results,
            "prediction": prediction,
            "institutional": inst_data.to_dict(orient='records') if inst_data is not None else [],
            "news_summary": f"共獲取 {len(news_data)} 則相關新聞" if news_data is not None else "無新聞數據"
        }
        
        return summary
