"""时间窗口分析模块"""
from .base_analyzer import BaseAnalyzer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings

class TimeWindowAnalyzer(BaseAnalyzer):
    """滚动时间窗口分析器"""
    
    def calculate_rolling_correlation(self, stock_data: Dict[str, pd.DataFrame], 
                                   window: int = 20) -> pd.DataFrame:
        """计算滚动相关系数"""
        try:
            returns_data = pd.DataFrame()
            
            for name, df in stock_data.items():
                df = self._prepare_data(df)
                returns_data[name] = self._calculate_returns(df)
                
            returns_data = returns_data.dropna()
            
            if returns_data.empty:
                raise ValueError("没有足够的数据计算相关系数")
                
            return returns_data.rolling(window=window).corr()
            
        except Exception as e:
            warnings.warn(f"计算滚动相关系数时出错: {str(e)}")
            return pd.DataFrame()
    
    def analyze_volatility(self, stock_data: dict, window: int = 20) -> pd.DataFrame:
        """分析波动性"""
        volatility_data = pd.DataFrame()
        
        for name, df in stock_data.items():
            df = self._prepare_data(df)
            returns = self._calculate_returns(df)
            volatility = returns.rolling(window=window).std() * np.sqrt(252)
            volatility_data[name] = volatility
            
        return volatility_data
    
    def analyze_volume_price_correlation(self, stock_data: dict, window: int = 20) -> pd.DataFrame:
        """分析成交量与价格的相关性"""
        volume_price_corr = pd.DataFrame()
        
        for name, df in stock_data.items():
            df = self._prepare_data(df)
            if 'volume' not in df.columns and 'vol' in df.columns:
                df['volume'] = df['vol']
            
            if 'volume' in df.columns:
                price_return = self._calculate_returns(df)
                volume_change = df['volume'].pct_change()
                corr = price_return.rolling(window=window).corr(volume_change)
                volume_price_corr[name] = corr
            
        return volume_price_corr