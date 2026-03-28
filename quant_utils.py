"""
quant_utils.py - 量化学习通用工具模块
=====================================

封装重复使用的数据生成、绘图等功能，
让每个 Step 的代码更简洁，聚焦于核心概念。

使用方式：
    from quant_utils import generate_stock_data, plot_indicator
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


# ============================================
# 数据生成函数
# ============================================

def generate_stock_data(days=60, seed=42, trend_pattern='random'):
    """
    生成模拟股票数据
    
    参数：
        days: 天数（默认60）
        seed: 随机种子（保证可重复）
        trend_pattern: 趋势模式
            - 'random': 随机波动
            - 'up_then_down': 先涨后跌
            - 'up': 持续上涨
            - 'down': 持续下跌
            - 'volatile': 大幅波动
    
    返回：
        DataFrame，包含 date, close 列
    """
    np.random.seed(seed)
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    initial_price = 100.0
    prices = []
    current_price = initial_price
    
    for i in range(days):
        if trend_pattern == 'random':
            change = np.random.normal(0, 0.02)  # 随机波动
        elif trend_pattern == 'up_then_down':
            # 前30天涨，后30天跌
            if i < days // 2:
                change = np.random.normal(0.02, 0.02)
            else:
                change = np.random.normal(-0.02, 0.02)
        elif trend_pattern == 'up':
            change = np.random.normal(0.01, 0.02)  # 持续上涨
        elif trend_pattern == 'down':
            change = np.random.normal(-0.01, 0.02)  # 持续下跌
        elif trend_pattern == 'volatile':
            change = np.random.normal(0, 0.05)  # 大幅波动
        else:
            change = np.random.normal(0, 0.02)
        
        current_price = current_price * (1 + change)
        prices.append(current_price)
    
    df = pd.DataFrame({
        'date': dates,
        'close': np.array(prices).round(2)
    })
    df.set_index('date', inplace=True)
    
    return df


def add_ma(df, periods=[5, 10, 20]):
    """
    给 DataFrame 添加 MA 列
    
    参数：
        df: 包含 close 列的 DataFrame
        periods: MA 周期列表
    
    返回：
        添加了 MA 列的 DataFrame
    """
    for period in periods:
        df[f'MA{period}'] = df['close'].rolling(window=period).mean()
    return df


# ============================================
# 绘图函数
# ============================================

def plot_price_with_ma(df, title='价格走势图', save_path=None):
    """
    绑制价格和MA图
    
    参数：
        df: 包含 close, MA5, MA10, MA20 的 DataFrame
        title: 图表标题
        save_path: 保存路径（可选）
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
    
    colors = {'MA5': 'red', 'MA10': 'orange', 'MA20': 'blue'}
    styles = {'MA5': '--', 'MA10': '--', 'MA20': '-'}
    
    for ma in ['MA5', 'MA10', 'MA20']:
        if ma in df.columns:
            ax.plot(df.index, df[ma], label=ma, 
                   color=colors.get(ma, 'gray'), 
                   linestyle=styles.get(ma, '-'))
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('日期')
    ax.set_ylabel('价格（元）')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存：{save_path}")
    
    return fig, ax


def plot_indicator(df, indicator_col, indicator_name, 
                   upper_threshold=None, lower_threshold=None,
                   title=None, save_path=None):
    """
    绑制指标图（带阈值线）
    
    参数：
        df: DataFrame
        indicator_col: 指标列名（如 'RSI'）
        indicator_name: 指标名称（如 'RSI 指标'）
        upper_threshold: 上阈值线（如 70）
        lower_threshold: 下阈值线（如 30）
        title: 标题
        save_path: 保存路径
    """
    fig, ax = plt.subplots(figsize=(12, 4))
    
    ax.plot(df.index, df[indicator_col], label=indicator_name, 
           color='purple', linewidth=1.5)
    
    if upper_threshold:
        ax.axhline(y=upper_threshold, color='red', linestyle='--', 
                  label=f'上阈值({upper_threshold})')
        ax.fill_between(df.index, upper_threshold, df[indicator_col], 
                       where=df[indicator_col] > upper_threshold, 
                       color='red', alpha=0.3)
    
    if lower_threshold:
        ax.axhline(y=lower_threshold, color='green', linestyle='--', 
                  label=f'下阈值({lower_threshold})')
        ax.fill_between(df.index, lower_threshold, df[indicator_col], 
                       where=df[indicator_col] < lower_threshold, 
                       color='green', alpha=0.3)
    
    ax.set_title(title or indicator_name, fontsize=12, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 图表已保存：{save_path}")
    
    return fig, ax


# ============================================
# 回测函数
# ============================================

def simple_backtest(df, signal_col, initial_capital=10000):
    """
    简单回测
    
    参数：
        df: 包含 close 和信号列的 DataFrame
        signal_col: 信号列名（值为 '买入', '卖出', '持有'）
        initial_capital: 初始资金
    
    返回：
        回测结果字典
    """
    capital = initial_capital
    shares = 0
    trades = []
    
    for idx, row in df.iterrows():
        if row[signal_col] == '买入' and shares == 0:
            shares = capital / row['close']
            trades.append({'date': idx, 'action': '买入', 'price': row['close']})
            capital = 0
        elif row[signal_col] == '卖出' and shares > 0:
            capital = shares * row['close']
            trades.append({'date': idx, 'action': '卖出', 'price': row['close']})
            shares = 0
    
    # 最后清仓
    if shares > 0:
        capital = shares * df['close'].iloc[-1]
    
    final_value = capital if capital > 0 else shares * df['close'].iloc[-1]
    return_rate = (final_value - initial_capital) / initial_capital * 100
    
    return {
        'initial_capital': initial_capital,
        'final_value': final_value,
        'return_rate': return_rate,
        'trades': trades,
        'trade_count': len(trades)
    }


# ============================================
# 打印辅助函数
# ============================================

def print_section(title):
    """打印分节标题"""
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_data_summary(df):
    """打印数据摘要"""
    print(f"日期范围：{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"价格范围：{df['close'].min():.2f} ~ {df['close'].max():.2f} 元")
    print(f"数据天数：{len(df)} 天")


# ============================================
# 使用示例
# ============================================

if __name__ == '__main__':
    # 测试工具函数
    print("📊 quant_utils 测试")
    print()
    
    # 生成数据
    df = generate_stock_data(trend_pattern='up_then_down')
    print_data_summary(df)
    print()
    
    # 添加 MA
    df = add_ma(df)
    print("MA 列已添加：", list(df.columns))
    print()
    
    # 绘图测试
    plot_price_with_ma(df, title='测试图表', save_path='test_chart.png')
    print()
    
    print("✅ quant_utils 测试完成！")