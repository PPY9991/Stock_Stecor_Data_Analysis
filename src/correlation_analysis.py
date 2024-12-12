"""相关性分析脚本"""
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import platform
import os
import matplotlib.font_manager as fm

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data' / 'stock_data'

# 股票列表
STOCK_LIST = {
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

def setup_chinese_font():
    """设置中文字体"""
    if platform.system() == 'Darwin':  # macOS
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
        return 'C:/Windows/Fonts/msyh.ttc'
    
    font_names = ['SimHei', 'Microsoft YaHei', 'STHeiti']
    for font_name in font_names:
        try:
            font_path = fm.findfont(fm.FontProperties(family=font_name))
            if font_path:
                return font_path
        except:
            continue
    
    return None

def load_stock_data(stock_list: dict) -> dict:
    """加载股票数据"""
    stock_data = {}
    for name, code in stock_list.items():
        try:
            file_path = DATA_DIR / f"{name}_{code}_20240101_20240131.csv"
            if file_path.exists():
                df = pd.read_csv(file_path)
                df['trade_date'] = pd.to_datetime(df['trade_date'])
                df = df.sort_values('trade_date')
                stock_data[name] = df
            else:
                print(f"找不到文件: {file_path}")
        except Exception as e:
            print(f"加载{name}数据时出错: {str(e)}")
    return stock_data

def analyze_correlation(stock_data: dict):
    """分析股票相关性"""
    # 计算收益率
    returns_data = pd.DataFrame()
    for name, df in stock_data.items():
        df = df.copy()
        df['return'] = df['close'].pct_change()
        returns_data[name] = df['return'].dropna()
    
    # 计算相关系数矩阵
    correlation_matrix = returns_data.corr()
    
    # 打印相关系数矩阵
    print("\n=== 股票相关系数矩阵 ===")
    pd.set_option('display.precision', 3)  # 设置显示精度
    pd.set_option('display.max_columns', None)  # 显示所有列
    pd.set_option('display.width', None)  # 不限制显示宽度
    print(correlation_matrix)
    
    # 绘制热图
    plt.figure(figsize=(12, 10))
    
    # 设置热图参数
    mask = np.triu(np.ones_like(correlation_matrix), k=1)
    plt.rcParams['font.size'] = 10
    
    # 设置字体
    font = fm.FontProperties(fname=setup_chinese_font()) if setup_chinese_font() else None
    
    # 绘制热图
    ax = sns.heatmap(
        correlation_matrix,
        mask=mask,
        cmap='RdYlBu_r',
        vmin=-1, vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": .5},
        annot=True,
        fmt='.2f',
        annot_kws={'size': 8}
    )
    
    # 设置标题和标签
    if font:
        plt.title('股票收益率相关性分析', fontproperties=font, pad=20, size=14)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        ax.set_xticklabels(ax.get_xticklabels(), fontproperties=font)
        ax.set_yticklabels(ax.get_yticklabels(), fontproperties=font)
        cbar = ax.collections[0].colorbar
        cbar.ax.set_ylabel('相关系数', fontproperties=font)
    else:
        plt.title('股票收益率相关性分析', pad=20, size=14)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.show()
    
    # 分析高相关性股票对
    print("\n=== 强相关性分析 ===")
    print("筛选标准：|相关系数| > 0.5\n")
    
    # 收集所有高相关性对
    high_corr_pairs = []
    for i in range(len(correlation_matrix.index)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr = correlation_matrix.iloc[i, j]
            if abs(corr) > 0.5:
                stock1 = correlation_matrix.index[i]
                stock2 = correlation_matrix.columns[j]
                high_corr_pairs.append((abs(corr), corr, stock1, stock2))
    
    # 按相关系数绝对值排序
    high_corr_pairs.sort(reverse=True)
    
    # 打印结果
    for abs_corr, corr, stock1, stock2 in high_corr_pairs:
        corr_type = "正相关" if corr > 0 else "负相关"
        print(f"{stock1:<8} 和 {stock2:<8}: {corr:>6.3f} ({corr_type})")

def main():
    """主函数"""
    # 确保数据目录存在
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    stock_data = load_stock_data(STOCK_LIST)
    
    if not stock_data:
        print("没有找到股票数据，请先运行数据收集脚本")
        return
    
    # 分析相关性
    analyze_correlation(stock_data)

if __name__ == "__main__":
    main() 