import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class YFinanceClient:
    def get_stock_price(self, stock_id, start_date, end_date):
        """
        Fetch historical stock price from yfinance (fallback).
        Note: stock_id for TW stocks needs .TW or .TWO suffix.
        """
        try:
            ticker = yf.Ticker(stock_id)
            df = ticker.history(start=start_date, end=end_date)
            # Standardize column names to match FinMind style if needed
            df.reset_index(inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching yfinance stock price: {e}")
            return None
