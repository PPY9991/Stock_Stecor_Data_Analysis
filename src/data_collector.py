import tushare as ts
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import json
import time

class DataCollector:
    """股票数据收集器"""
    
    def __init__(self, token: str):
        """初始化数据收集器"""
        self.token = token
        self._initialize_api()
        self.retry_count = 3
        self.retry_delay = 2  # 秒
        
    def _initialize_api(self):
        """初始化Tushare API"""
        try:
            ts.set_token(self.token)
            self.pro = ts.pro_api(self.token)
        except Exception as e:
            raise ConnectionError(f"Tushare API初始化失败: {str(e)}")
    
    def _retry_operation(self, operation, *args, **kwargs):
        """重试操作"""
        for attempt in range(self.retry_count):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.retry_count - 1:
                    raise e
                print(f"操作失败，{self.retry_delay}秒后重试...")
                time.sleep(self.retry_delay)
        
    def search_stock(self, stock_name: str) -> Optional[Tuple[str, str]]:
        """搜索股票代码"""
        try:
            # 缓存文件路径
            cache_file = Path(__file__).parent.parent / 'data' / 'cache' / 'stock_list.json'
            stocks_df = None
            
            # 尝试从缓存加载
            if cache_file.exists() and (datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)).days < 1:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    stocks_dict = json.load(f)
                    stocks_df = pd.DataFrame(stocks_dict)
            
            # 如果没有缓存或缓存过期，从API获取
            if stocks_df is None:
                stocks_df = self._retry_operation(self.pro.stock_basic, exchange='', list_status='L')
                # 保存缓存
                os.makedirs(cache_file.parent, exist_ok=True)
                stocks_dict = stocks_df.to_dict('list')
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(stocks_dict, f, ensure_ascii=False)
            
            # 模糊匹配股票名称和代码
            matched = stocks_df[
                stocks_df['name'].str.contains(stock_name, na=False) |
                stocks_df['ts_code'].str.contains(stock_name.upper(), na=False)
            ]
            
            if matched.empty:
                print(f"未找到股票：{stock_name}")
                return None
                
            if len(matched) > 1:
                print("\n找到多个匹配的股票：")
                for idx, row in matched.iterrows():
                    print(f"{idx}: {row['name']} ({row['ts_code']}) - {row['industry']}")
                while True:
                    try:
                        choice = input("\n请选择股票序号（输入q取消）：").strip()
                        if choice.lower() == 'q':
                            return None
                        choice = int(choice)
                        if 0 <= choice < len(matched):
                            selected = matched.iloc[choice]
                            return (selected['ts_code'], selected['name'])
                    except ValueError:
                        print("请输入有效的数字")
            else:
                return (matched.iloc[0]['ts_code'], matched.iloc[0]['name'])
                
        except Exception as e:
            print(f"搜索股票时出错：{str(e)}")
            return None
            
    def collect_data(self, stock_code: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """收集股票数据"""
        try:
            df = self._retry_operation(self.pro.daily, ts_code=stock_code, 
                                     start_date=start_date, end_date=end_date)
            if df.empty:
                print(f"警告：{stock_code} 在指定时间段内没有数据")
                return None
                
            # 添加技术指标
            df = self._add_technical_indicators(df)
            return df
            
        except Exception as e:
            print(f"获取数据时出错：{str(e)}")
            return None
            
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加技术指标"""
        df = df.sort_values('trade_date')
        
        # 计算MA
        for period in [5, 10, 20, 30]:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
            
        # 计算成交量MA
        df['VWAP'] = (df['amount'] / df['vol']).fillna(df['close'])
        
        return df

def validate_date(date_str: str) -> bool:
    """验证日期格式"""
    try:
        date = datetime.strptime(date_str, '%Y%m%d')
        # 检查是否是未来日期
        if date > datetime.now():
            print("不能输入未来日期")
            return False
        return True
    except ValueError:
        return False

def get_user_input() -> Tuple[str, str]:
    """获取用户输入的日期范围"""
    print("\n日期输入说明：")
    print("1. 直接输入日期，格式为YYYYMMDD")
    print("2. 输入'today'表示今天")
    print("3. 输入'-30'表示30天前\n")
    
    def parse_date_input(date_input: str) -> str:
        if date_input.lower() == 'today':
            return datetime.now().strftime('%Y%m%d')
        if date_input.startswith('-'):
            try:
                days = int(date_input)
                return (datetime.now() + timedelta(days=days)).strftime('%Y%m%d')
            except ValueError:
                return date_input
        return date_input
    
    while True:
        start_date = parse_date_input(input("请输入开始日期: ").strip())
        if validate_date(start_date):
            break
        print("日期格式错误，请使用YYYYMMDD格式")
    
    while True:
        end_date = parse_date_input(input("请输入结束日期: ").strip())
        if validate_date(end_date) and end_date >= start_date:
            break
        print("日期格式错误或结束日期早于开始日期")
    
    return start_date, end_date

def main():
    """主函数"""
    try:
        # 设置token和数据目录
        token = 'your own token!'
        project_root = Path(__file__).parent.parent
        data_dir = project_root / 'data' / 'stock_data'
        os.makedirs(data_dir, exist_ok=True)
        
        collector = DataCollector(token)
        collected_stocks = []
        
        print("\n=== 股票数据收集工具 ===")
        print("提示：")
        print("1. 输入股票名称或代码进行搜索")
        print("2. 支持模糊匹配")
        print("3. 输入'q'结束股票输入")
        
        while True:
            stock_name = input("\n请输入股票名称或代码: ").strip()
            if stock_name.lower() == 'q':
                break
                
            result = collector.search_stock(stock_name)
            if result:
                collected_stocks.append(result)
                print(f"已添加：{result[1]} ({result[0]})")
        
        if not collected_stocks:
            print("未选择任何股票，程序结束")
            return
            
        # 显示已选股票列表
        print("\n已选择的股票：")
        for code, name in collected_stocks:
            print(f"- {name} ({code})")
            
        # 获取日期范围
        start_date, end_date = get_user_input()
        
        # 收集并保存数据
        print("\n开始收集数据...")
        success_count = 0
        
        for stock_code, stock_name in collected_stocks:
            print(f"\n处理 {stock_name} 的数据...")
            df = collector.collect_data(stock_code, start_date, end_date)
            
            if df is not None:
                file_path = data_dir / f"{stock_name}_{stock_code}_{start_date}_{end_date}.csv"
                df.to_csv(file_path, index=False)
                print(f"已保存到：{file_path}")
                success_count += 1
        
        print(f"\n数据收集完成！成功收集 {success_count}/{len(collected_stocks)} 只股票的数据")
        print(f"数据保存在：{data_dir}")
        
    except Exception as e:
        print(f"\n程序运行出错：{str(e)}")
        raise

if __name__ == "__main__":
    main() 