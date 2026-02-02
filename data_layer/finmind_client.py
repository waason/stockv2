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
        Normalizes column names to match expected schema.
        """
        try:
            df = self.loader.taiwan_stock_daily(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or df.empty:
                return None
            
            # Normalize column names to match expected schema
            column_mapping = {
                'Trading_Volume': 'vol',
                'max': 'high',
                'min': 'low'
            }
            df = df.rename(columns=column_mapping)
            
            return df
        except Exception as e:
            logger.error(f"Error fetching FinMind stock price: {e}")
            return None

    def get_institutional_investors(self, stock_id, start_date, end_date):
        """
        Fetch institutional investors data.
        Transforms from long format to wide format with net buy/sell columns.
        """
        try:
            df = self.loader.taiwan_stock_institutional_investors(
                stock_id=stock_id,
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or df.empty:
                return None
            
            # Calculate net buy (buy - sell)
            df['net_buy'] = df['buy'] - df['sell']
            
            # Pivot to wide format: each investor type becomes a column
            pivot_df = df.pivot_table(
                index='date',
                columns='name',
                values='net_buy',
                aggfunc='sum'
            ).reset_index()
            
            # Rename columns to English for consistency
            column_mapping = {
                'Foreign_Investor': 'Foreign_Investor',
                'Investment_Trust': 'Investment_Trust',
                'Dealer': 'Dealer'
            }
            
            # Only rename columns that exist
            existing_cols = {k: v for k, v in column_mapping.items() if k in pivot_df.columns}
            pivot_df = pivot_df.rename(columns=existing_cols)
            
            return pivot_df
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
            
            # Handle case where API returns dict instead of DataFrame
            if isinstance(df, dict) and 'data' not in df:
                logger.warning(f"No news data available for {stock_id}")
                return pd.DataFrame()
            
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return pd.DataFrame()
                
            return df
        except Exception as e:
            logger.error(f"Error fetching FinMind stock news: {e}")
            return pd.DataFrame()
