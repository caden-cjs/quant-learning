"""
Step 6: RSI（相对强弱指标）
==========================

学习目标：
1. 理解 RSI 的原理和计算方法
2. 学会用 Python 计算 RSI
3. 理解超买（RSI>70）和超卖（RSI<30）
4. 将 RSI 与 MA 结合使用

运行方式：
    python step6_rsi.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ============================================
# 第一步：准备数据
# ============================================
np.random.seed(42)
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(60)]

# 生成有波动性的价格数据
initial_price = 100.0
prices = []
current_price = initial_price

# 模拟真实市场波动
for i in range(60):
    # 前20天上涨
    if i < 20:
        change = np.random.normal(0.02, 0.03)
    # 中间20天震荡
    elif i < 40:
        change = np.random.normal(0, 0.02)
    # 后20天下跌
    else:
        change = np.random.normal(-0.02, 0.03)
    
    current_price = current_price * (1 + change)
    prices.append(current_price)

prices = np.array(prices)

df = pd.DataFrame({
    'date': dates,
    'close': prices.round(2)
})
df.set_index('date', inplace=True)

print("=" * 60)
print("📊 数据准备完成")
print("=" * 60)
print(f"日期范围：{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
print(f"价格范围：{df['close'].min():.2f} ~ {df['close'].max():.2f} 元")
print()

# ============================================
# 第二步：计算 RSI
# ============================================
print("=" * 60)
print("📈 计算 RSI（相对强弱指标）")
print("=" * 60)

print("""
RSI 原理：
┌────────────────────────────────────────────┐
│  RSI 衡量"上涨力量"占"总波动力量"的比例    │
│                                            │
│  计算步骤：                                │
│  1. 计算每天的价格变化（涨或跌）           │
│  2. 分别计算最近N天的"平均上涨"和"平均下跌"│
│  3. RSI = 100 - 100/(1 + 平均上涨/平均下跌)│
│                                            │
│  常用周期：RSI14（最近14天）               │
└────────────────────────────────────────────┘
""")

# 计算价格变化
df['change'] = df['close'].diff()  # 今天 - 昨天

# 分离上涨和下跌
df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)  # 上涨部分
df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)  # 下跌部分（取正数）

# 计算平均上涨和平均下跌（使用14天周期）
period = 14
df['avg_gain'] = df['gain'].rolling(window=period).mean()
df['avg_loss'] = df['loss'].rolling(window=period).mean()

# 计算 RS（相对强弱）
df['RS'] = df['avg_gain'] / df['avg_loss']

# 计算 RSI
df['RSI'] = 100 - (100 / (1 + df['RS']))

print("📊 RSI 计算结果（显示部分数据）")
print("-" * 70)
print(df[['close', 'change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'RSI']].tail(20).round(2))
print("-" * 70)
print()

# ============================================
# 第三步：分析超买和超卖
# ============================================
print("=" * 60)
print("🔍 分析超买和超卖信号")
print("=" * 60)

# 超买：RSI > 70
df['超买'] = df['RSI'] > 70

# 超卖：RSI < 30
df['超卖'] = df['RSI'] < 30

# 统计
overbought_count = df['超买'].sum()
oversold_count = df['超卖'].sum()

print(f"\n超买天数（RSI > 70）：{overbought_count} 天")
print(f"超卖天数（RSI < 30）：{oversold_count} 天")

# 列出超买/超卖日期
overbought_dates = df[df['超买']].index.tolist()
oversold_dates = df[df['超卖']].index.tolist()

if overbought_dates:
    print("\n超买日期（可能要跌，考虑卖出）：")
    for d in overbought_dates:
        print(f"   • {d.strftime('%Y-%m-%d')} (RSI={df.loc[d, 'RSI']:.1f}, 价格={df.loc[d, 'close']:.2f})")

if oversold_dates:
    print("\n超卖日期（可能要涨，考虑买入）：")
    for d in oversold_dates:
        print(f"   • {d.strftime('%Y-%m-%d')} (RSI={df.loc[d, 'RSI']:.1f}, 价格={df.loc[d, 'close']:.2f})")

print()

# ============================================
# 第四步：结合 MA 分析
# ============================================
print("=" * 60)
print("💡 RSI + MA 结合使用")
print("=" * 60)

# 计算 MA
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()

print("""
为什么要结合多个指标？
┌────────────────────────────────────────────┐
│  单一指标可能产生假信号！                  │
│                                            │
│  结合使用更可靠：                          │
│  • RSI 超卖 + 价格跌破 MA → 可能真要反弹  │
│  • RSI 超买 + 价格远高于 MA → 可能真要跌  │
│  • RSI 超买但价格刚突破 MA → 可能继续涨   │
└────────────────────────────────────────────┘
""")

# 生成综合信号
def get_combined_signal(row):
    """结合 RSI 和 MA 判断"""
    if pd.isna(row['RSI']) or pd.isna(row['MA20']):
        return '数据不足'
    
    rsi = row['RSI']
    price = row['close']
    ma20 = row['MA20']
    
    # 强买入信号：超卖 + 价格低于MA20
    if rsi < 30 and price < ma20:
        return '强买入'
    
    # 强卖出信号：超买 + 价格高于MA20
    if rsi > 70 and price > ma20:
        return '强卖出'
    
    # 弱买入：仅超卖
    if rsi < 30:
        return '弱买入'
    
    # 弱卖出：仅超买
    if rsi > 70:
        return '弱卖出'
    
    return '观望'

df['综合信号'] = df.apply(get_combined_signal, axis=1)

# 统计综合信号
signal_counts = df['综合信号'].value_counts()
print("\n综合信号统计：")
for signal, count in signal_counts.items():
    print(f"   • {signal}: {count} 天")

print()

# ============================================
# 第五步：可视化
# ============================================
print("=" * 60)
print("🎨 绑制 RSI 图表")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 图1：价格和MA
ax1 = axes[0]
ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax1.plot(df.index, df['MA20'], label='MA20', color='blue', linewidth=2)

# 标记超买超卖点
for d in overbought_dates:
    ax1.scatter(d, df.loc[d, 'close'], color='red', marker='v', s=80, zorder=5)
for d in oversold_dates:
    ax1.scatter(d, df.loc[d, 'close'], color='green', marker='^', s=80, zorder=5)

ax1.set_title('价格走势（红色=超买，绿色=超卖）', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylabel('价格（元）')

# 图2：RSI
ax2 = axes[1]
ax2.plot(df.index, df['RSI'], label='RSI', color='purple', linewidth=1.5)

# 添加超买超卖线
ax2.axhline(y=70, color='red', linestyle='--', label='超买线(70)')
ax2.axhline(y=30, color='green', linestyle='--', label='超卖线(30)')
ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='中线(50)')

# 填充超买超卖区域
ax2.fill_between(df.index, 70, df['RSI'], where=df['RSI'] > 70, color='red', alpha=0.3)
ax2.fill_between(df.index, 30, df['RSI'], where=df['RSI'] < 30, color='green', alpha=0.3)

ax2.set_title('RSI 指标', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylabel('RSI 值')
ax2.set_ylim(0, 100)

plt.tight_layout()

output_file = 'rsi_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ RSI 图表已保存：{output_file}")
print()

# ============================================
# 小知识：RSI 的使用技巧
# ============================================
print("=" * 60)
print("📖 RSI 使用技巧")
print("=" * 60)
print("""
RSI 常见用法：

1. 超买超卖判断
   • RSI > 70 → 超买，可能下跌
   • RSI < 30 → 超卖，可能上涨

2. 趋势确认
   • RSI > 50 → 处于上升趋势
   • RSI < 50 → 处于下降趋势

3. 背离信号（进阶）
   • 价格创新高，RSI没创新高 → 顶背离，可能下跌
   • 价格创新低，RSI没创新低 → 底背离，可能上涨

注意事项：
┌────────────────────────────────────────────┐
│  ⚠️ 超买不等于马上跌！                    │
│     强势股可能长期维持在超买区域           │
│                                            │
│  ⚠️ 超卖不等于马上涨！                    │
│     弱势股可能长期维持在超卖区域           │
│                                            │
│  ⚠️ 结合其他指标更可靠！                   │
│     不要单独依赖 RSI                       │
└────────────────────────────────────────────┘
""")

print("=" * 60)
print("🎉 Step 6 完成！")
print("=" * 60)
print("""
你学会了：
1. ✅ RSI 的原理和计算方法
2. ✅ 超买（RSI>70）和超卖（RSI<30）的含义
3. ✅ 将 RSI 与 MA 结合使用
4. ✅ 生成综合信号（强买入/强卖出）

下一步：Step 7 - MACD 指标
""")