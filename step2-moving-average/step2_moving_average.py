"""
Step 2: 计算移动平均线（MA）
===========================

核心内容：
- MA 的原理和计算方法
- Pandas rolling() 函数
- MA5、MA10、MA20 的意义

运行方式：
    python step2_moving_average.py
"""

from quant_utils import generate_stock_data, add_ma, print_section, print_data_summary
import pandas as pd

# ============================================
# 核心：MA 计算逻辑
# ============================================

def calculate_ma(df, periods=[5, 10, 20]):
    """
    计算移动平均线
    
    MA 原理：
    MA = 最近N天收盘价的平均值
    用于平滑价格波动，判断趋势
    
    Pandas 实现：
    df['MA5'] = df['close'].rolling(5).mean()
    """
    return add_ma(df, periods)


def find_cross_signals(df):
    """
    找出金叉和死叉
    
    金叉：MA5 从下往上穿过 MA20 → 买入信号
    死叉：MA5 从上往下穿过 MA20 → 卖出信号
    """
    df['MA5_prev'] = df['MA5'].shift(1)
    df['MA20_prev'] = df['MA20'].shift(1)
    
    # 金叉条件
    df['金叉'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])
    
    # 死叉条件
    df['死叉'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])
    
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 2: 移动平均线（MA）")

# 生成数据
df = generate_stock_data(days=60)
print_data_summary(df)

# 核心：计算 MA
print_section("📈 MA 计算原理")

print("""
┌─────────────────────────────────────────────┐
│  MA = Moving Average（移动平均线）          │
│                                             │
│  计算方法：                                  │
│  MA5 = (Day1~Day5 收盘价之和) / 5           │
│  MA20 = (Day1~Day20 收盘价之和) / 20        │
│                                             │
│  Pandas 实现：                              │
│  df['MA5'] = df['close'].rolling(5).mean() │
│                                             │
│  rolling(N) 创建滑动窗口，每次取最近N个数据│
└─────────────────────────────────────────────┘
""")

# 计算 MA
df = calculate_ma(df, periods=[5, 10, 20])

# 显示结果
print("📊 数据预览（含 MA）：")
print(df[['close', 'MA5', 'MA10', 'MA20']].tail(15).round(2))

# 找交叉信号
print_section("🔍 金叉与死叉")
print("""
金叉（买入信号）：MA5 从下往上穿过 MA20
死叉（卖出信号）：MA5 从上往下穿过 MA20
""")

df = find_cross_signals(df)

# 统计
golden_count = df['金叉'].sum()
death_count = df['死叉'].sum()

print(f"金叉次数：{golden_count}")
print(f"死叉次数：{death_count}")

if golden_count > 0:
    print("\n金叉日期：")
    for idx in df[df['金叉']].index:
        print(f"  • {idx.strftime('%Y-%m-%d')}")

if death_count > 0:
    print("\n死叉日期：")
    for idx in df[df['死叉']].index:
        print(f"  • {idx.strftime('%Y-%m-%d')}")

# 保存
df[['close', 'MA5', 'MA10', 'MA20']].to_csv('stock_with_ma.csv')
print(f"\n✅ 数据已保存：stock_with_ma.csv")

print_section("🎉 完成！")
print("""
你学会了：
✅ MA 的计算方法：rolling().mean()
✅ MA5（短期）、MA20（长期）的意义
✅ 金叉/死叉信号的概念

⚠️ 注意：
- 前 N 天的 MA 是 NaN（数据不足）
- 单一信号可能不准确，需结合其他指标

下一步：Step 3 - 绑制价格走势图
""")