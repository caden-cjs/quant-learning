"""
Step 7: MACD（指数平滑异同移动平均线）
=====================================

核心内容：
- MACD 的原理和计算方法
- EMA（指数移动平均）vs MA（简单移动平均）
- DIF、DEA、MACD柱的含义
- MACD 金叉/死叉信号

运行方式：
    python step7_macd.py
"""

from quant_utils import (
    generate_stock_data, 
    plot_indicator,
    print_section, print_data_summary
)
import pandas as pd
import numpy as np

# ============================================
# 核心：MACD 计算逻辑
# ============================================

def calculate_ema(series, period):
    """
    计算 EMA（指数移动平均）
    
    EMA vs MA 的区别：
    - MA：所有天数权重相同
    - EMA：最近的价格权重更大，反应更快
    
    公式：EMA = 价格 × 平滑系数 + 前一天EMA × (1 - 平滑系数)
    平滑系数 = 2 / (周期 + 1)
    """
    return series.ewm(span=period, adjust=False).mean()


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    计算 MACD 指标
    
    MACD 组成：
    1. DIF（快线）= EMA(12) - EMA(26)
    2. DEA（慢线）= EMA(DIF, 9)
    3. MACD柱 = (DIF - DEA) × 2
    
    参数：
        df: DataFrame（包含 close 列）
        fast: 快线周期（默认12）
        slow: 慢线周期（默认26）
        signal: 信号线周期（默认9）
    
    返回：
        添加了 MACD 列的 DataFrame
    """
    # 计算 EMA
    df['EMA12'] = calculate_ema(df['close'], fast)
    df['EMA26'] = calculate_ema(df['close'], slow)
    
    # 计算 DIF（快线）
    df['DIF'] = df['EMA12'] - df['EMA26']
    
    # 计算 DEA（慢线/信号线）
    df['DEA'] = calculate_ema(df['DIF'], signal)
    
    # 计算 MACD 柱
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    
    return df


def analyze_macd_signals(df):
    """
    分析 MACD 信号
    
    买入信号：
    1. 金叉：DIF 从下往上穿过 DEA
    2. MACD 柱由负转正
    
    卖出信号：
    1. 死叉：DIF 从上往下穿过 DEA
    2. MACD 柱由正转负
    """
    # DIF 与 DEA 的交叉
    df['DIF_prev'] = df['DIF'].shift(1)
    df['DEA_prev'] = df['DEA'].shift(1)
    
    # 金叉：DIF 从下往上穿过 DEA
    df['金叉'] = (df['DIF_prev'] < df['DEA_prev']) & (df['DIF'] > df['DEA'])
    
    # 死叉：DIF 从上往下穿过 DEA
    df['死叉'] = (df['DIF_prev'] > df['DEA_prev']) & (df['DIF'] < df['DEA'])
    
    # MACD 柱变化
    df['MACD_prev'] = df['MACD'].shift(1)
    df['柱转正'] = (df['MACD_prev'] < 0) & (df['MACD'] > 0)  # 由负转正
    df['柱转负'] = (df['MACD_prev'] > 0) & (df['MACD'] < 0)  # 由正转负
    
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 7: MACD 指标学习")

# 生成数据
df = generate_stock_data(days=60, trend_pattern='up_then_down')
print_data_summary(df)

# 核心：计算 MACD
print_section("📈 计算 MACD")

print("""
MACD 原理：
┌─────────────────────────────────────────────┐
│  MACD = Moving Average Convergence Divergence│
│                                             │
│  组成部分：                                  │
│  • DIF（快线）= EMA12 - EMA26              │
│  • DEA（慢线）= DIF 的 9 日 EMA            │
│  • MACD柱 = (DIF - DEA) × 2               │
│                                             │
│  EMA vs MA：                                │
│  • MA：所有天数权重相同                     │
│  • EMA：最近价格权重更大，反应更快          │
└─────────────────────────────────────────────┘
""")

df = calculate_macd(df)

# 显示数据
print("📊 MACD 数据预览（最近15天）：")
print(df[['close', 'DIF', 'DEA', 'MACD']].tail(15).round(4))

# 分析信号
print_section("🔍 MACD 信号分析")

df = analyze_macd_signals(df)

print("""
MACD 信号解读：

买入信号：
  • DIF 金叉 DEA（DIF 从下往上穿过 DEA）
  • MACD 柱由负转正（红柱变绿柱）

卖出信号：
  • DIF 死叉 DEA（DIF 从上往下穿过 DEA）
  • MACD 柱由正转负（绿柱变红柱）

注意：
  • 零轴上方 = 多头市场（上涨趋势）
  • 零轴下方 = 空头市场（下跌趋势）
""")

# 统计信号
print(f"金叉次数：{df['金叉'].sum()}")
print(f"死叉次数：{df['死叉'].sum()}")
print(f"柱转正次数：{df['柱转正'].sum()}")
print(f"柱转负次数：{df['柱转负'].sum()}")

# 列出信号日期
golden_dates = df[df['金叉']].index.tolist()
death_dates = df[df['死叉']].index.tolist()

if golden_dates:
    print("\n金叉日期：")
    for d in golden_dates:
        print(f"  • {d.strftime('%Y-%m-%d')} (DIF={df.loc[d, 'DIF']:.4f})")

if death_dates:
    print("\n死叉日期：")
    for d in death_dates:
        print(f"  • {d.strftime('%Y-%m-%d')} (DIF={df.loc[d, 'DIF']:.4f})")

# ============================================
# 可视化
# ============================================
print_section("🎨 绑制 MACD 图表")

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})

# 图1：价格
ax1 = axes[0]
ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax1.plot(df.index, df['EMA12'], label='EMA12', color='red', linestyle='--', alpha=0.7)
ax1.plot(df.index, df['EMA26'], label='EMA26', color='blue', linestyle='--', alpha=0.7)
ax1.set_title('价格走势与 EMA', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylabel('价格（元）')

# 图2：MACD
ax2 = axes[1]
ax2.plot(df.index, df['DIF'], label='DIF（快线）', color='red', linewidth=1.5)
ax2.plot(df.index, df['DEA'], label='DEA（慢线）', color='blue', linewidth=1.5)
ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.5)

# MACD 柱（红绿柱）
colors = ['red' if v < 0 else 'green' for v in df['MACD']]
ax2.bar(df.index, df['MACD'], color=colors, alpha=0.3, label='MACD柱')

# 标记金叉死叉
for d in golden_dates:
    ax2.scatter(d, df.loc[d, 'DIF'], color='green', marker='^', s=80, zorder=5)
for d in death_dates:
    ax2.scatter(d, df.loc[d, 'DIF'], color='red', marker='v', s=80, zorder=5)

ax2.set_title('MACD 指标（绿柱=多头，红柱=空头）', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylabel('MACD 值')

plt.xticks(rotation=45)
plt.tight_layout()

output_file = 'macd_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 图表已保存：{output_file}")

# ============================================
# 小知识
# ============================================
print_section("📖 MACD 使用技巧")

print("""
MACD 经典用法：

1. 趋势判断
   • DIF > 0 且 DEA > 0 → 多头市场（上涨趋势）
   • DIF < 0 且 DEA < 0 → 空头市场（下跌趋势）

2. 买卖信号
   • 金叉 + 零轴上方 → 强买入信号
   • 金叉 + 零轴下方 → 弱买入信号（可能是反弹）
   • 死叉 + 零轴上方 → 弱卖出信号
   • 死叉 + 零轴下方 → 强卖出信号

3. 背离信号（进阶）
   • 顶背离：价格创新高，MACD 没创新高 → 可能下跌
   • 底背离：价格创新低，MACD 没创新低 → 可能上涨

4. MACD 参数
   • 默认：12, 26, 9
   • 短线：可改为 6, 13, 5
   • 长线：可改为 24, 52, 18

⚠️ 注意事项：
┌────────────────────────────────────────────┐
│  • MACD 是滞后指标，信号出现较晚          │
│  • 震荡市中容易产生假信号                  │
│  • 建议结合其他指标（RSI、成交量）使用     │
└────────────────────────────────────────────┘
""")

print_section("🎉 Step 7 完成！")
print("""
你学会了：
✅ MACD 的组成：DIF、DEA、MACD柱
✅ EMA 与 MA 的区别
✅ MACD 金叉/死叉信号
✅ MACD 柱的多空判断

下一步：Step 8 - 布林带（Bollinger Bands）
""")