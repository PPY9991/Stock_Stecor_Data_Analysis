import tushare as ts
import pandas as pd
import os

class StockDataCollector:
    """股票数据收集器"""
    
    def __init__(self, token: str):
        """
        初始化数据收集器
        :param token: Tushare API token
        """
        ts.set_token(token)
        self.pro = ts.pro_api(token)
        
    def collect_stock_data(self, stocks: dict, start_date: str, end_date: str, output_dir: str) -> dict:
        """
        收集股票数据并保存为CSV文件
        :param stocks: 股票代码字典 {'股票名': '股票代码'}
        :param start_date: 开始日期 'YYYYMMDD'
        :param end_date: 结束日期 'YYYYMMDD'
        :param output_dir: 输出目录
        :return: 文件路径字典
        """
        file_paths = {}
        os.makedirs(output_dir, exist_ok=True)
        
        for name, ts_code in stocks.items():
            try:
                df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                file_path = os.path.join(output_dir, f'{name}_{ts_code}_{start_date}_{end_date}.csv')
                df.to_csv(file_path, index=False)
                file_paths[name] = file_path
                print(f'{name} 数据已保存到 {file_path}')
            except Exception as e:
                print(f'获取{name}数据时出错: {str(e)}')
                
        return file_paths 