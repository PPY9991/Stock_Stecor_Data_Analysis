"""聚类分析模块"""
from .base_analyzer import BaseAnalyzer
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt
from typing import Tuple, Dict, List

class ClusterAnalyzer(BaseAnalyzer):
    """股票聚类分析器"""
    
    def __init__(self, font_path: str = None, max_clusters: int = 10):
        super().__init__(font_path)
        self.max_clusters = max_clusters
        self.scaler = StandardScaler()
        self.kmeans_models = {}  # 缓存训练好的模型
    
    def prepare_data(self, stock_data: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        准备聚类数据
        :param stock_data: 股票数据字典
        :return: (原始数据, 标准化数据)
        """
        try:
            merged_data = pd.DataFrame()
            
            for name, df in stock_data.items():
                df = self._prepare_data(df)
                if merged_data.empty:
                    merged_data = pd.DataFrame(index=df.index)
                merged_data[name] = df['close']
            
            # 计算收益率矩阵
            returns_matrix = merged_data.pct_change().fillna(0)
            data_for_clustering = returns_matrix.T
            
            # 标准化数据
            data_scaled = self.scaler.fit_transform(data_for_clustering)
            
            return data_for_clustering, data_scaled
            
        except Exception as e:
            self.logger.error(f"数据准备失败: {e}")
            raise
    
    def find_optimal_clusters(self, data_scaled: np.ndarray) -> Tuple[List[float], List[float]]:
        """
        使用肘部法则和轮廓系数找到最佳聚类数
        :return: (惯性值列表, 轮廓系数列表)
        """
        inertias = []
        silhouette_scores = []
        k_range = range(2, self.max_clusters + 1)
        
        for k in k_range:
            self.logger.info(f"测试聚类数 k={k}")
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(data_scaled)
            
            # 保存模型
            self.kmeans_models[k] = kmeans
            
            # 计算指标
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(data_scaled, kmeans.labels_))
        
        # 绘制评估图
        self._plot_evaluation_metrics(k_range, inertias, silhouette_scores)
        
        return inertias, silhouette_scores
    
    def _plot_evaluation_metrics(self, k_range: range, inertias: List[float], 
                               silhouette_scores: List[float]) -> None:
        """绘制评估指标图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # 绘制肘部法则图
        ax1.plot(list(k_range), inertias, 'bx-')
        ax1.set_xlabel('聚类数(k)', fontproperties=self.font)
        ax1.set_ylabel('惯性值', fontproperties=self.font)
        ax1.set_title('K-means聚类肘部法则图', fontproperties=self.font)
        ax1.grid(True)
        
        # 绘制轮廓系数图
        ax2.plot(list(k_range), silhouette_scores, 'rx-')
        ax2.set_xlabel('聚类数(k)', fontproperties=self.font)
        ax2.set_ylabel('轮廓系数', fontproperties=self.font)
        ax2.set_title('轮廓系数评估图', fontproperties=self.font)
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def perform_clustering(self, data_scaled: np.ndarray, n_clusters: int) -> pd.DataFrame:
        """
        执行聚类分析
        :param data_scaled: 标准化数据
        :param n_clusters: 聚类数
        :return: 聚类结果DataFrame
        """
        try:
            # 使用缓存的模型或训练新模型
            if n_clusters in self.kmeans_models:
                kmeans = self.kmeans_models[n_clusters]
                clusters = kmeans.labels_
            else:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(data_scaled)
                self.kmeans_models[n_clusters] = kmeans
            
            return pd.DataFrame({
                'Stock': range(len(clusters)),
                'Cluster': clusters
            })
            
        except Exception as e:
            self.logger.error(f"聚类分析失败: {e}")
            raise 