from stock_analysis.data_collector import StockDataCollector
from stock_analysis.correlation_analyzer import CorrelationAnalyzer
from stock_analysis.cluster_analyzer import ClusterAnalyzer
from stock_analysis.time_window_analyzer import TimeWindowAnalyzer
import pandas as pd
import os
from pathlib import Path
import platform
import matplotlib.font_manager as fm

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'stock_data'

# 设置中文字体
def setup_chinese_font():
    """设置中文字体"""
    if platform.system() == 'Darwin':  # macOS
        # 尝试多个可能的字体路径
        possible_fonts = [
            '/System/Library/Fonts/STHeiti Light.ttc',
            '/System/Library/Fonts/STHeiti Medium.ttc',
            '/System/Library/Fonts/PingFang.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc'
        ]
        for font_path in possible_fonts:
            if os.path.exists(font_path):
                return font_path
    elif platform.system() == 'Windows':
        return 'C:/Windows/Fonts/msyh.ttc'  # 微软雅黑
    
    # 如果找不到系统字体，尝试使用matplotlib内置的中文字体
    font_names = ['SimHei', 'Microsoft YaHei', 'STHeiti']
    for font_name in font_names:
        try:
            font_path = fm.findfont(fm.FontProperties(family=font_name))
            if font_path:
                return font_path
        except:
            continue
    
    return None  # 如果都找不到，返回None

# 设置字体路径
FONT_PATH = setup_chinese_font()

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_stock_data(file_paths: dict) -> dict:
    """
    从CSV文件加载股票数据
    :param file_paths: 文件路径字典
    :return: 股票数据字典
    """
    stock_data = {}
    for name, path in file_paths.items():
        try:
            df = pd.read_csv(path)
            # 确保列名符合预期
            if 'trade_date' not in df.columns or 'close' not in df.columns:
                df = df.rename(columns={
                    '交易日期': 'trade_date',
                    '收盘价': 'close'
                })
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
            stock_data[name] = df
        except Exception as e:
            print(f"加载{name}数据时出错: {str(e)}")
    return stock_data

def main():
    # 初始化数据收集器
    token = '94dab43691e9de6efe181288968723ca36f358382552cf76a90815f2'
    collector = StockDataCollector(token)
    
    # 定义股票
    stocks = {
        '海康威视': '002415.SZ',
        '金山办公': '688111.SH',
        '京东方A': '000725.SZ',
        '科大讯飞': '002230.SZ',
        '韦尔股份': '603501.SH',
        '长安汽车': '000625.SZ',
        '长城汽车': '601633.SH',
        '中芯国际': '688981.SH',
        '比亚迪': '002594.SZ'
    }
    
    # 检查并创建数据目录
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # 检查是否需要收集数据
    if not os.path.exists(DATA_DIR) or not os.listdir(DATA_DIR):
        file_paths = collector.collect_stock_data(
            stocks,
            start_date='20240101',
            end_date='20240131',
            output_dir=DATA_DIR
        )
    else:
        file_paths = {
            name: os.path.join(DATA_DIR, f"{name}_{code}_20240101_20240131.csv")
            for name, code in stocks.items()
        }
    
    # 加载数据
    stock_data = load_stock_data(file_paths)
    
    # 相关性分析
    analyzer = CorrelationAnalyzer(font_path=FONT_PATH)
    correlation_matrix = analyzer.calculate_returns_correlation(stock_data)
    analyzer.plot_correlation_heatmap(correlation_matrix, '股票收益率相关性分析')
    
    # 聚类分析
    cluster_analyzer = ClusterAnalyzer()
    data_orig, data_scaled = cluster_analyzer.prepare_data(stock_data)
    cluster_analyzer.find_optimal_clusters(data_scaled)
    results = cluster_analyzer.perform_clustering(data_scaled, n_clusters=3)
    
    # 添加股票名称到聚类结果
    results['Stock'] = list(stock_data.keys())
    
    print("\n聚类结果：")
    for cluster in range(3):
        stocks_in_cluster = results[results['Cluster'] == cluster]['Stock'].tolist()
        print(f"\n簇 {cluster + 1}:")
        print(", ".join(stocks_in_cluster))
    
    # 时间窗口分析
    window_analyzer = TimeWindowAnalyzer(font_path=FONT_PATH)
    
    # 计算滚动相关系数
    rolling_corr = window_analyzer.calculate_rolling_correlation(stock_data, window=10)
    window_analyzer.plot_rolling_correlation(rolling_corr)
    
    # 计算波动率
    volatility = window_analyzer.analyze_volatility(stock_data)
    window_analyzer.plot_volatility(volatility, '股票波动率分析')
    
    # 分析成交量与价格相关性
    volume_price_corr = window_analyzer.analyze_volume_price_correlation(stock_data)
    window_analyzer.plot_volume_price_correlation(volume_price_corr, '成交量-价格相关性分析')

if __name__ == "__main__":
    main() 