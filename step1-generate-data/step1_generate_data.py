"""
Step 1: 生成模拟股票数据
========================

学习目标：
1. 了解股票数据的基本结构（日期、开盘价、最高价、最低价、收盘价、成交量）
2. 学会使用 pandas 创建 DataFrame
3. 理解什么是 OHLCV 数据

运行方式：
    python step1_generate_data.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================
# 第一步：生成日期序列
# ============================================
# 股票数据必须有时间维度，我们生成 60 个交易日

start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(60)]

print("📅 生成的日期范围：")
print(f"   起始日期：{dates[0].strftime('%Y-%m-%d')}")
print(f"   结束日期：{dates[-1].strftime('%Y-%m-%d')}")
print(f"   共 {len(dates)} 个交易日\n")

# ============================================
# 第二步：生成模拟价格数据
# ============================================
# OHLCV = Open, High, Low, Close, Volume
# 这是最常用的股票数据格式

np.random.seed(42)  # 固定随机种子，让结果可重复

# 设定初始价格为 100 元
initial_price = 100.0

# 生成收盘价（随机游走模型）
# 每天的价格变化 = 前一天价格 × (1 + 随机波动率)
returns = np.random.normal(0, 0.02, 60)  # 平均涨跌幅 0%，波动率 2%
close_prices = [initial_price]

for r in returns[1:]:
    new_price = close_prices[-1] * (1 + r)
    close_prices.append(new_price)

close_prices = np.array(close_prices)

# 生成开盘价（接近前一天收盘价）
open_prices = close_prices * (1 + np.random.uniform(-0.01, 0.01, 60))

# 生成最高价和最低价
high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0, 0.02, 60))
low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0, 0.02, 60))

# 生成成交量（随机，但价格大跌时成交量放大）
base_volume = 1000000
volumes = base_volume * (1 + np.random.uniform(0, 1, 60))
# 价格下跌时成交量放大
for i in range(len(volumes)):
    if close_prices[i] < open_prices[i]:
        volumes[i] *= 1.5

print("💰 生成的价格数据预览：")
print(f"   收盘价范围：{close_prices.min():.2f} ~ {close_prices.max():.2f} 元")
print(f"   成交量范围：{volumes.min():.0f} ~ {volumes.max():.0f} 股\n")

# ============================================
# 第三步：创建 DataFrame
# ============================================
# DataFrame 是 pandas 的核心数据结构，类似 Excel 表格

df = pd.DataFrame({
    'date': dates,
    'open': open_prices.round(2),      # 开盘价
    'high': high_prices.round(2),      # 最高价
    'low': low_prices.round(2),        # 最低价
    'close': close_prices.round(2),    # 收盘价
    'volume': volumes.astype(int)      # 成交量
})

# 设置日期为索引（这是量化数据处理的标准做法）
df.set_index('date', inplace=True)

print("📊 DataFrame 结构预览：")
print("-" * 60)
print(df.head(10))  # 显示前 10 行
print("-" * 60)
print(f"\n数据形状：{df.shape[0]} 行 × {df.shape[1]} 列")

# ============================================
# 第四步：保存数据
# ============================================
output_file = 'stock_data.csv'
df.to_csv(output_file)
print(f"\n✅ 数据已保存到：{output_file}")

# ============================================
# 小知识：什么是 OHLCV？
# ============================================
print("\n" + "=" * 60)
print("📖 小知识：OHLCV 数据格式")
print("=" * 60)
print("""
股票数据通常包含以下字段：

• Open  (开盘价) - 当天第一笔交易的价格
• High  (最高价) - 当天最高的成交价格
• Low   (最低价) - 当天最低的成交价格
• Close (收盘价) - 当天最后一笔交易的价格
• Volume(成交量) - 当天成交的股票数量

这是量化交易最基础的数据格式，几乎所有策略都从 OHLCV 开始！
""")