import pandas as pd
from FinMind.data import DataLoader
import logging

logger = logging.getLogger(__name__)

class FinMindClient:
    def __init__(self, token=None):
        self.loader = DataLoader()
        if token:
            self.loader.login_by_token(token)
            
    def get_stock_price(self, stock_id, start_date, end_date):
        """
        Fetch historical stock price from FinMind.
        """
        try:
            df = self.loader.taiwan_stock_daily(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            logger.error(f"Error fetching FinMind stock price: {e}")
            return None

    def get_institutional_investors(self, stock_id, start_date, end_date):
        """
        Fetch institutional investors data.
        """
        try:
            df = self.loader.taiwan_stock_institutional_investors(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            logger.error(f"Error fetching FinMind institutional investors: {e}")
            return None

    def get_stock_news(self, stock_id, start_date, end_date):
        """
        Fetch stock related news.
        """
        try:
            df = self.loader.taiwan_stock_news(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            logger.error(f"Error fetching FinMind stock news: {e}")
            return None
