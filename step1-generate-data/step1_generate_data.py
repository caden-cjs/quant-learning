"""
Step 1: 生成模拟股票数据 - OHLCV
================================

核心内容：
- 什么是 OHLCV 数据格式
- 用 Pandas 创建 DataFrame
- 设置日期索引

运行方式：
    python step1_generate_data.py
"""

from quant_utils import generate_stock_data, print_section, print_data_summary
import pandas as pd

# ============================================
# 核心：OHLCV 数据格式
# ============================================

def add_ohlcv_columns(df):
    """
    添加完整的 OHLCV 列
    
    OHLCV = Open, High, Low, Close, Volume
    这是股票数据的标准格式
    """
    import numpy as np
    
    # Open: 开盘价（接近前一天收盘）
    df['open'] = df['close'].shift(1) * (1 + np.random.uniform(-0.01, 0.01, len(df)))
    df['open'].iloc[0] = df['close'].iloc[0]  # 第一天开盘=收盘
    
    # High: 最高价
    df['high'] = df[['open', 'close']].max(axis=1) * (1 + np.random.uniform(0, 0.02, len(df)))
    
    # Low: 最低价
    df['low'] = df[['open', 'close']].min(axis=1) * (1 - np.random.uniform(0, 0.02, len(df)))
    
    # Volume: 成交量（随机生成）
    df['volume'] = (1000000 * (1 + np.random.uniform(0, 1, len(df))).astype(int))
    
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 1: OHLCV 数据格式")

# 生成基础数据（使用工具模块）
df = generate_stock_data(days=60, seed=42)
print_data_summary(df)

# 核心：添加 OHLCV 列
print_section("📖 OHLCV 数据格式说明")

print("""
┌─────────────────────────────────────────────┐
│  OHLCV = 股票数据的标准格式                 │
│                                             │
│  • Open  (开盘价) - 当天第一笔交易的价格    │
│  • High  (最高价) - 当天最高的成交价格      │
│  • Low   (最低价) - 当天最低的成交价格      │
│  • Close (收盘价) - 当天最后一笔交易的价格  │
│  • Volume(成交量) - 当天成交的股票数量      │
│                                             │
│  这是量化交易最基础的数据格式！             │
└─────────────────────────────────────────────┘
""")

# 添加 OHLCV
df = add_ohlcv_columns(df)

# 重新排列列顺序
df = df[['open', 'high', 'low', 'close', 'volume']]

# 显示数据
print("📊 OHLCV 数据预览：")
print(df.head(10).round(2))

# 保存
df.to_csv('stock_data.csv')
print(f"\n✅ 数据已保存：stock_data.csv")

print_section("🎉 完成！")
print("""
你学会了：
✅ OHLCV 是股票数据的标准格式
✅ 收盘价(close)是最重要的参考价格
✅ DataFrame 是 Pandas 的核心数据结构

下一步：Step 2 - 计算 MA（移动平均线）
""")