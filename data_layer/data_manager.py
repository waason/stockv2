import pandas as pd
import os
from datetime import datetime, timedelta
from .finmind_client import FinMindClient
from .yfinance_client import YFinanceClient
import logging
import yaml

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.finmind = FinMindClient(token=self.config['api'].get('finmind_token'))
        self.yfinance = YFinanceClient()
        self.cache_dir = "data_cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_stock_data(self, stock_id, start_date=None, end_date=None, use_cache=True):
        """
        Get stock price data with fallback and caching.
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        cache_file = os.path.join(self.cache_dir, f"{stock_id}_{start_date}_{end_date}.csv")
        
        if use_cache and os.path.exists(cache_file):
            logger.info(f"Loading cached data for {stock_id}")
            return pd.read_csv(cache_file)

        # Try FinMind first
        df = self.finmind.get_stock_price(stock_id, start_date, end_date)
        
        if df is None or df.empty:
            logger.warning(f"FinMind failed for {stock_id}, trying yfinance")
            # Format for yfinance if it's a TW stock
            yf_stock_id = stock_id
            if stock_id.isdigit():
                yf_stock_id = f"{stock_id}.TW"
            df = self.yfinance.get_stock_price(yf_stock_id, start_date, end_date)

        if df is not None and not df.empty:
            if use_cache:
                df.to_csv(cache_file, index=False)
            return df
        
        return None

    def get_institutional_data(self, stock_id, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        return self.finmind.get_institutional_investors(stock_id, start_date, end_date)

    def get_news_data(self, stock_id, start_date=None, end_date=None):
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
        return self.finmind.get_stock_news(stock_id, start_date, end_date)
