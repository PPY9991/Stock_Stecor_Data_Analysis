"""相关性分析模块"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

class CorrelationAnalyzer:
    """股票相关性分析器"""
    
    def __init__(self, font_path: str = None):
        """
        初始化分析器
        :param font_path: 中文字体路径
        """
        self.font = FontProperties(fname=font_path) if font_path else None
        
    def calculate_returns_correlation(self, stock_data: dict) -> pd.DataFrame:
        """
        计算股票收益率相关性
        :param stock_data: 股票数据字典 {'股票名': DataFrame}
        :return: 相关性矩阵
        """
        returns_data = pd.DataFrame()
        
        # 计算每只股票的收益率
        for name, df in stock_data.items():
            df = df.copy()
            df['return'] = df['close'].pct_change()
            returns_data[name] = df['return'].dropna()
            
        # 计算相关系数矩阵
        correlation_matrix = returns_data.corr()
        
        # 打印具体的相关��数
        print("\n股票相关系数矩阵：")
        print(correlation_matrix.round(3))
        
        return correlation_matrix
    
    def plot_correlation_heatmap(self, correlation_matrix: pd.DataFrame, title: str):
        """
        绘制相关性热图
        :param correlation_matrix: 相关性矩阵
        :param title: 图表标题
        """
        plt.figure(figsize=(12, 10))
        
        # 设置热图参数
        mask = np.triu(np.ones_like(correlation_matrix), k=1)  # 创建上三角掩码
        
        # 设置字体大小
        plt.rcParams['font.size'] = 10
        
        # 绘制热图
        ax = sns.heatmap(
            correlation_matrix,
            mask=mask,  # 使用掩码隐藏上三角
            cmap='RdYlBu_r',  # 使用更清晰的配色方案
            vmin=-1, vmax=1,  # 设置颜色范围
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": .5},
            annot=True,  # 显示具体数值
            fmt='.2f',  # 数值格式化为2位小数
            annot_kws={'size': 8}  # 调整数值大小
        )
        
        # 设置标题和标签
        if self.font:
            plt.title(title, fontproperties=self.font, pad=20, size=14)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            ax.set_xticklabels(ax.get_xticklabels(), fontproperties=self.font)
            ax.set_yticklabels(ax.get_yticklabels(), fontproperties=self.font)
            cbar = ax.collections[0].colorbar
            cbar.ax.set_ylabel('相关系数', fontproperties=self.font)
        else:
            plt.title(title, pad=20, size=14)
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
        
        # 调整布局
        plt.tight_layout()
        plt.show()
        
        # 打印相关性分析结果
        self._print_correlation_analysis(correlation_matrix)
    
    def _print_correlation_analysis(self, correlation_matrix: pd.DataFrame):
        """
        打印相关性分析结果
        :param correlation_matrix: 相关性矩阵
        """
        print("\n相关性分析结果：")
        
        # 找出高相关性的股票对
        high_corr_pairs = []
        for i in range(len(correlation_matrix.index)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.5:  # 相关系数阈值可以调整
                    stock1 = correlation_matrix.index[i]
                    stock2 = correlation_matrix.columns[j]
                    high_corr_pairs.append((stock1, stock2, corr))
        
        # 按相关系数绝对值排序
        high_corr_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        
        # 打印结果
        print("\n强相关性股票对（|相关系数| > 0.5）：")
        for stock1, stock2, corr in high_corr_pairs:
            corr_type = "正相关" if corr > 0 else "负相关"
            print(f"{stock1} 和 {stock2}: {corr:.3f} ({corr_type})") 