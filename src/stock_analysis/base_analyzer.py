"""
基础分析器模块
提供数据处理、分析和可视化的基础功能
"""
import pandas as pd
import numpy as np
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from typing import Optional, Dict, Union
from pathlib import Path
import logging

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class BaseAnalyzer:
    """
    基础分析器类，提供共享功能
    包含数据预处理、计算和绘图的基础方法
    """
    
    def __init__(self, font_path: Optional[Union[str, Path]] = None):
        """
        初始化分析器
        Args:
            font_path: 中文字体文件路径，用于图表显示中文
        """
        self.font = self._init_font(font_path)
        plt.style.use('seaborn')  # 使用seaborn样式美化图表
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _init_font(self, font_path: Optional[Union[str, Path]]) -> Optional[FontProperties]:
        """
        初始化字体设置
        Args:
            font_path: 字体文件路径
        Returns:
            FontProperties对象或None（如果字体加载失败）
        """
        if font_path:
            try:
                return FontProperties(fname=str(font_path))
            except Exception as e:
                self.logger.warning(f"字体加载失败: {e}")
        return None
    
    @staticmethod
    def _validate_dataframe(df: pd.DataFrame, required_cols: list) -> bool:
        """
        验证DataFrame是否包含必要的列
        Args:
            df: 待验证的DataFrame
            required_cols: 必需的列名列表
        Returns:
            bool: 是否包含所有必需的列
        """
        return all(col in df.columns for col in required_cols)
    
    def _prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据预处理：标准化数据格式，处理缺失值，设置索引等
        Args:
            df: 原始数据DataFrame
        Returns:
            处理后的DataFrame
        Raises:
            ValueError: 当缺少必要的列时
            Exception: 其他处理错误
        """
        try:
            df = df.copy()  # 创建副本避免修改原始数据
            required_cols = ['trade_date', 'close']
            
            # 验证数据完整性
            if not self._validate_dataframe(df, required_cols):
                raise ValueError(f"数据缺少必要的列: {required_cols}")
            
            # 处理日期列：转换格式并设置为索引
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df.set_index('trade_date', inplace=True)
            df.sort_index(inplace=True)  # 确保按时间顺序排序
            
            # 处理缺失值
            df = self._handle_missing_values(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"数据预处理失败: {e}")
            raise
    
    @staticmethod
    def _handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """
        处理数据中的缺失值
        Args:
            df: 包含缺失值的DataFrame
        Returns:
            处理后的DataFrame
        Note:
            - 对数值列使用前向填充方法处理缺失值
            - 适用于时间序列数据
        """
        # 获取所有数值类型的列
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # 使用前向填充处理缺失值（假设数据按时间排序）
        df[numeric_cols] = df[numeric_cols].fillna(method='ffill')
        return df
    
    def _calculate_returns(self, df: pd.DataFrame) -> pd.Series:
        """
        计算收益率序列
        Args:
            df: 包含收盘价的DataFrame
        Returns:
            收益率Series
        Note:
            - 使用对数收益率计算
            - 第一个值的收益率为NaN，填充为0
            - 异常值会被记录但不会被处理
        """
        try:
            returns = df['close'].pct_change()
            return returns.fillna(0)  # 第一个值的收益率填充为0
        except Exception as e:
            self.logger.error(f"收益率计算失败: {e}")
            raise
    
    def plot_setup(self, figsize: tuple = (12, 6)) -> None:
        """
        设置绘图全局参数
        Args:
            figsize: 图表大小，默认为(12, 6)
        Note:
            - 设置图表大小
            - 配置中文字体（如果可用）
            - 可以在此添加其他全局绘图设置
        """
        plt.figure(figsize=figsize)
        if self.font:
            plt.rcParams['font.family'] = self.font.get_family()