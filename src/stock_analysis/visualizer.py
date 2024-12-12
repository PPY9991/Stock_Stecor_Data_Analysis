"""可视化模块"""
from .base_analyzer import BaseAnalyzer
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Tuple, Optional

class Visualizer(BaseAnalyzer):
    """可视化工具"""
    
    def plot_rolling_correlation(self, rolling_corr: pd.DataFrame, 
                               stock_pairs: Optional[List[Tuple[str, str]]] = None,
                               min_periods: int = 5):
        """绘制滚动相关系数图"""
        if rolling_corr.empty:
            raise ValueError("相关系数数据为空")
            
        if stock_pairs is None:
            stocks = list(set(rolling_corr.index.get_level_values(1)))
            stock_pairs = [(s1, s2) for i, s1 in enumerate(stocks) 
                          for s2 in stocks[i+1:]]
        
        n_pairs = len(stock_pairs)
        if n_pairs == 0:
            raise ValueError("没有可用的股票对")
            
        n_cols = min(2, n_pairs)
        n_rows = (n_pairs + n_cols - 1) // n_cols
        
        fig = plt.figure(figsize=(15, 5 * n_rows))
        
        for i, (stock1, stock2) in enumerate(stock_pairs, 1):
            self._plot_correlation_subplot(fig, n_rows, n_cols, i, 
                                        rolling_corr, stock1, stock2, min_periods)
            
        plt.tight_layout()
        plt.show()
    
    def plot_volatility(self, volatility_data: pd.DataFrame, title: str):
        """绘制波动率图表"""
        self._plot_time_series(volatility_data, title, '年化波动率')
    
    def plot_volume_price_correlation(self, volume_price_corr: pd.DataFrame, title: str):
        """绘制成交量-价格相关性图表"""
        self._plot_time_series(volume_price_corr, title, '量价相关系数')
    
    def _plot_time_series(self, data: pd.DataFrame, title: str, ylabel: str):
        """绘制时间序列数据"""
        plt.figure(figsize=(15, 8))
        for column in data.columns:
            plt.plot(data.index, data[column], label=column)
            
        plt.title(title, fontproperties=self.font)
        plt.xlabel('日期', fontproperties=self.font)
        plt.ylabel(ylabel, fontproperties=self.font)
        plt.legend(prop=self.font)
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show() 