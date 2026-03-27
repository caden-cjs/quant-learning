"""
Step 2: 计算移动平均线（MA）
============================

学习目标：
1. 理解移动平均线的原理和计算方法
2. 学会用 Pandas 计算 MA（rolling mean）
3. 理解不同周期 MA 的意义（MA5、MA10、MA20）
4. 初识"金叉"和"死叉"信号

运行方式：
    python step2_moving_average.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================
# 第一步：读取或生成股票数据
# ============================================
# 如果有 Step 1 生成的 CSV，可以直接读取
# df = pd.read_csv('stock_data.csv', index_col='date', parse_dates=True)

# 这里我们重新生成数据，方便独立运行
np.random.seed(42)
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(60)]

initial_price = 100.0
returns = np.random.normal(0, 0.02, 60)
close_prices = [initial_price]
for r in returns[1:]:
    close_prices.append(close_prices[-1] * (1 + r))
close_prices = np.array(close_prices)

df = pd.DataFrame({
    'date': dates,
    'close': close_prices.round(2)
})
df.set_index('date', inplace=True)

print("=" * 60)
print("📊 股票收盘价数据（前10行）")
print("=" * 60)
print(df.head(10))
print()

# ============================================
# 第二步：计算移动平均线（MA）
# ============================================
# MA = Moving Average（移动平均）
# 使用 Pandas 的 rolling() 函数计算

print("=" * 60)
print("📈 计算移动平均线")
print("=" * 60)

# MA5：最近5天的平均价格
df['MA5'] = df['close'].rolling(window=5).mean()

# MA10：最近10天的平均价格
df['MA10'] = df['close'].rolling(window=10).mean()

# MA20：最近20天的平均价格
df['MA20'] = df['close'].rolling(window=20).mean()

print("""
MA 计算原理：
┌─────────────────────────────────────────────┐
│  MA5 = (Day1 + Day2 + Day3 + Day4 + Day5) / 5 │
│  MA10 = 最近10天收盘价之和 / 10               │
│  MA20 = 最近20天收盘价之和 / 20               │
└─────────────────────────────────────────────┘

注意：前几天的 MA 会是 NaN（因为没有足够的数据）
""")

print("📊 带 MA 的数据（前20行，注意 NaN）")
print("-" * 60)
print(df.head(20).round(2))
print("-" * 60)
print()

# ============================================
# 第三步：分析 MA 的意义
# ============================================
print("=" * 60)
print("💡 不同周期 MA 的意义")
print("=" * 60)
print("""
| MA周期 | 特点 | 用途 |
|--------|------|------|
| MA5    | 变化快，贴近当前价格 | 短期趋势判断 |
| MA10   | 中等平滑度 | 中短期交易参考 |
| MA20   | 变化慢，更平滑 | 长期趋势判断 |

一般规律：
• 价格 > MA → 处于上升趋势
• 价格 < MA → 处于下降趋势
• MA5 > MA20 → 短期趋势向上
• MA5 < MA20 → 短期趋势向下
""")

# ============================================
# 第四步：寻找"金叉"和"死叉"
# ============================================
print("=" * 60)
print("🔍 金叉与死叉")
print("=" * 60)
print("""
金叉（Golden Cross）：MA5 从下往上穿过 MA20
    → 可能是买入信号 ✅

死叉（Death Cross）：MA5 从上往下穿过 MA20
    → 可能是卖出信号 ❌
""")

# 计算金叉和死叉
# 方法：比较前一天和当天的 MA5 与 MA20 关系

# 前一天：MA5 < MA20，今天：MA5 > MA20 → 金叉
# 前一天：MA5 > MA20，今天：MA5 < MA20 → 死叉

df['MA5_prev'] = df['MA5'].shift(1)  # 前一天的 MA5
df['MA20_prev'] = df['MA20'].shift(1)  # 前一天的 MA20

# 金叉条件
df['golden_cross'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])

# 死叉条件
df['death_cross'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])

# 找出金叉和死叉的日期
golden_cross_dates = df[df['golden_cross']].index.tolist()
death_cross_dates = df[df['death_cross']].index.tolist()

print("📈 金叉日期（买入信号）：")
if golden_cross_dates:
    for d in golden_cross_dates:
        print(f"   • {d.strftime('%Y-%m-%d')}")
else:
    print("   （本次数据中未出现金叉）")

print("\n📉 死叉日期（卖出信号）：")
if death_cross_dates:
    for d in death_cross_dates:
        print(f"   • {d.strftime('%Y-%m-%d')}")
else:
    print("   （本次数据中未出现死叉）")

print()

# ============================================
# 第五步：保存结果
# ============================================
# 只保留需要的列
output_df = df[['close', 'MA5', 'MA10', 'MA20']].copy()
output_df.to_csv('stock_with_ma.csv')

print("=" * 60)
print("✅ 结果已保存")
print("=" * 60)
print(f"文件：stock_with_ma.csv")
print(f"包含列：close, MA5, MA10, MA20")
print()

# ============================================
# 小知识：rolling() 函数
# ============================================
print("=" * 60)
print("📖 Pandas rolling() 函数详解")
print("=" * 60)
print("""
rolling(window=N) 的作用：
┌────────────────────────────────────────────────┐
│  创建一个"滑动窗口"，每次取最近 N 个数据      │
│                                                │
│  例如 rolling(5).mean()：                      │
│                                                │
│  Day 1-5 → 计算前5天的平均 → 得到 Day5 的 MA5 │
│  Day 2-6 → 计算这5天的平均 → 得到 Day6 的 MA5 │
│  Day 3-7 → 计算这5天的平均 → 得到 Day7 的 MA5 │
│  ...                                           │
│                                                │
│  窗口像滑动的"框"，每次向前移动一天           │
└────────────────────────────────────────────────┘

常用方法：
• rolling(5).mean()   → 移动平均
• rolling(5).sum()    → 移动求和
• rolling(5).max()    → 移动最大值
• rolling(5).std()    → 移动标准差（波动率）
""")

print("=" * 60)
print("🎉 Step 2 完成！")
print("=" * 60)
print("""
你学会了：
1. ✅ MA 的原理和计算方法
2. ✅ 用 Pandas rolling() 计算 MA
3. ✅ 不同周期 MA 的意义
4. ✅ 金叉/死叉信号

下一步：Step 3 - 绘制价格走势图（可视化 MA）
""")