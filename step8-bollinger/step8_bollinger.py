"""
Step 8: 布林带（Bollinger Bands）
=================================

核心内容：
- 布林带的原理和计算方法
- 标准差的概念
- 布林带收窄与突破信号
- 结合其他指标使用

运行方式：
    python step8_bollinger.py
"""

from quant_utils import (
    generate_stock_data, 
    print_section, print_data_summary
)
import pandas as pd
import numpy as np

# ============================================
# 核心：布林带计算逻辑
# ============================================

def calculate_bollinger(df, period=20, std_dev=2):
    """
    计算布林带
    
    布林带组成：
    1. 中轨 = MA(N)  → N日简单移动平均
    2. 上轨 = 中轨 + K × 标准差
    3. 下轨 = 中轨 - K × 标准差
    
    参数：
        df: DataFrame（包含 close 列）
        period: 周期（默认20）
        std_dev: 标准差倍数（默认2）
    
    返回：
        添加了布林带列的 DataFrame
    """
    # 中轨 = MA
    df['BOLL_MID'] = df['close'].rolling(window=period).mean()
    
    # 标准差
    df['BOLL_STD'] = df['close'].rolling(window=period).std()
    
    # 上轨 = 中轨 + 2倍标准差
    df['BOLL_UPPER'] = df['BOLL_MID'] + std_dev * df['BOLL_STD']
    
    # 下轨 = 中轨 - 2倍标准差
    df['BOLL_LOWER'] = df['BOLL_MID'] - std_dev * df['BOLL_STD']
    
    # 通道宽度（用于判断收窄）
    df['BOLL_WIDTH'] = (df['BOLL_UPPER'] - df['BOLL_LOWER']) / df['BOLL_MID'] * 100
    
    return df


def analyze_bollinger_signals(df):
    """
    分析布林带信号
    
    信号类型：
    1. 突破上轨 → 超买，可能回调
    2. 跌破下轨 → 超卖，可能反弹
    3. 通道收窄 → 可能要变盘（突破）
    4. 通道扩张 → 趋势加强
    """
    # 价格位置
    df['突破上轨'] = df['close'] > df['BOLL_UPPER']
    df['跌破下轨'] = df['close'] < df['BOLL_LOWER']
    
    # 通道收窄（宽度变小）
    df['WIDTH_PREV'] = df['BOLL_WIDTH'].shift(1)
    df['通道收窄'] = df['BOLL_WIDTH'] < df['WIDTH_PREV'] * 0.9  # 宽度缩小10%
    
    # 价格在中轨上方/下方
    df['中轨上方'] = df['close'] > df['BOLL_MID']
    
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 8: 布林带（Bollinger Bands）学习")

# 生成数据（大幅波动，便于观察布林带）
df = generate_stock_data(days=60, trend_pattern='volatile')
print_data_summary(df)

# 核心：计算布林带
print_section("📈 计算布林带")

print("""
布林带原理：
┌─────────────────────────────────────────────┐
│  布林带 = 用标准差画出价格的"正常波动范围" │
│                                             │
│  组成部分：                                  │
│  • 中轨 = MA(20)     → 20日移动平均        │
│  • 上轨 = 中轨 + 2×标准差                  │
│  • 下轨 = 中轨 - 2×标准差                  │
│                                             │
│  标准差含义：                                │
│  • 标准差衡量价格波动的"剧烈程度"           │
│  • 波动大 → 通道宽                          │
│  • 波动小 → 通道窄                          │
│                                             │
│  统计学原理：                                │
│  • 约95%的价格会在上下轨之间波动            │
│  • 突破轨道 = 超出正常范围                  │
└─────────────────────────────────────────────┘
""")

df = calculate_bollinger(df)

# 显示数据
print("📊 布林带数据预览（最近15天）：")
cols = ['close', 'BOLL_UPPER', 'BOLL_MID', 'BOLL_LOWER', 'BOLL_WIDTH']
print(df[cols].tail(15).round(2))

# 分析信号
print_section("🔍 布林带信号分析")

df = analyze_bollinger_signals(df)

print("""
布林带信号解读：

1. 突破信号
   • 突破上轨 → 超买，价格过高，可能回调
   • 跌破下轨 → 超卖，价格过低，可能反弹

2. 通道形态
   • 通道收窄 → 波动变小，可能要变盘（大行情）
   • 通道扩张 → 波动变大，趋势加强

3. 价格位置
   • 价格在中轨上方 → 偏多（上涨趋势）
   • 价格在中轨下方 → 偏空（下跌趋势）

4. 经典策略
   • 下轨买入 + 回到中轨卖出
   • 上轨卖出 + 回到中轨买入
""")

# 统计信号
print(f"突破上轨次数：{df['突破上轨'].sum()}")
print(f"跌破下轨次数：{df['跌破下轨'].sum()}")
print(f"通道收窄次数：{df['通道收窄'].sum()}")

# 列出突破日期
upper_break = df[df['突破上轨']].index.tolist()
lower_break = df[df['跌破下轨']].index.tolist()

if upper_break:
    print("\n突破上轨日期（可能回调）：")
    for d in upper_break[-5:]:  # 只显示最近5个
        print(f"  • {d.strftime('%Y-%m-%d')} 价格={df.loc[d, 'close']:.2f} 上轨={df.loc[d, 'BOLL_UPPER']:.2f}")

if lower_break:
    print("\n跌破下轨日期（可能反弹）：")
    for d in lower_break[-5:]:
        print(f"  • {d.strftime('%Y-%m-%d')} 价格={df.loc[d, 'close']:.2f} 下轨={df.loc[d, 'BOLL_LOWER']:.2f}")

# ============================================
# 可视化
# ============================================
print_section("🎨 绑制布林带图表")

import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [2, 1]})

# 图1：价格与布林带
ax1 = axes[0]

# 布林带通道（填充）
ax1.fill_between(df.index, df['BOLL_UPPER'], df['BOLL_LOWER'], 
                  alpha=0.2, color='blue', label='布林带通道')

# 价格和均线
ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax1.plot(df.index, df['BOLL_MID'], label='中轨(MA20)', color='blue', linewidth=1)
ax1.plot(df.index, df['BOLL_UPPER'], label='上轨', color='red', linestyle='--', linewidth=0.8)
ax1.plot(df.index, df['BOLL_LOWER'], label='下轨', color='green', linestyle='--', linewidth=0.8)

# 标记突破点
for d in upper_break:
    ax1.scatter(d, df.loc[d, 'close'], color='red', marker='v', s=60, zorder=5)
for d in lower_break:
    ax1.scatter(d, df.loc[d, 'close'], color='green', marker='^', s=60, zorder=5)

ax1.set_title('布林带（红点=突破上轨，绿点=跌破下轨）', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylabel('价格（元）')

# 图2：通道宽度
ax2 = axes[1]
ax2.plot(df.index, df['BOLL_WIDTH'], label='通道宽度(%)', color='purple', linewidth=1.5)
ax2.axhline(y=df['BOLL_WIDTH'].mean(), color='gray', linestyle='--', alpha=0.5, label='平均宽度')

ax2.set_title('布林带通道宽度（收窄=可能变盘）', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylabel('宽度(%)')

plt.xticks(rotation=45)
plt.tight_layout()

output_file = 'bollinger_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 图表已保存：{output_file}")

# ============================================
# 小知识
# ============================================
print_section("📖 布林带使用技巧")

print("""
布林带经典用法：

1. 趋势判断
   • 价格在中轨以上 + 通道扩张 → 上涨趋势
   • 价格在中轨以下 + 通道扩张 → 下跌趋势
   • 通道收窄 → 趋势可能反转

2. 买卖信号
   • 跌破下轨后回到下轨内 → 买入
   • 突破上轨后回到上轨内 → 卖出
   • 价格触及下轨 + RSI超卖 → 强买入

3. 收窄突破
   • 通道极度收窄 → 大行情即将到来
   • 收窄后向上突破上轨 → 买入
   • 收窄后向下突破下轨 → 卖出

4. 参数调整
   • 默认：20日，2倍标准差
   • 短线：10日，1.5倍标准差
   • 长线：50日，2.5倍标准差

⚠️ 注意事项：
┌────────────────────────────────────────────┐
│  • 布林带是相对指标，不是绝对买卖点        │
│  • 强趋势中价格可能长期在上轨/下轨外       │
│  • 结合 RSI、成交量等其他指标更可靠        │
│  • "收窄后突破"信号最可靠                  │
└────────────────────────────────────────────┘
""")

print_section("🎉 Step 8 完成！")
print("""
你学会了：
✅ 布林带的组成：中轨、上轨、下轨
✅ 标准差的含义和计算
✅ 突破上轨/跌破下轨的信号
✅ 通道收窄预示变盘

下一步：Step 9 - 多指标组合策略
""")