"""
Step 4 & 5: 趋势判断与简单回测
==============================

学习目标：
1. 根据MA判断趋势方向（上涨、下跌、横盘）
2. 生成交易信号（买入、卖出、持有）
3. 进行简单回测，计算策略收益
4. 对比"买入持有"与"MA策略"的表现

运行方式：
    python step4_5_backtest.py
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

# 生成更有趋势性的价格数据（先涨后跌）
initial_price = 100.0
prices = []
current_price = initial_price

# 前30天：上涨趋势（日均涨1%）
for i in range(30):
    change = np.random.normal(0.01, 0.02)  # 平均涨1%
    current_price = current_price * (1 + change)
    prices.append(current_price)

# 后30天：下跌趋势（日均跌0.5%）
for i in range(30):
    change = np.random.normal(-0.005, 0.02)  # 平均跌0.5%
    current_price = current_price * (1 + change)
    prices.append(current_price)

prices = np.array(prices)

df = pd.DataFrame({
    'date': dates,
    'close': prices.round(2)
})
df.set_index('date', inplace=True)

# 计算 MA
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA10'] = df['close'].rolling(window=10).mean()
df['MA20'] = df['close'].rolling(window=20).mean()

print("=" * 60)
print("📊 数据准备完成（模拟先涨后跌趋势）")
print("=" * 60)
print(f"起始价格：{df['close'].iloc[0]:.2f} 元")
print(f"最高价格：{df['close'].max():.2f} 元（约第30天）")
print(f"结束价格：{df['close'].iloc[-1]:.2f} 元")
print()

# ============================================
# 第二步：趋势判断（Step 4）
# ============================================
print("=" * 60)
print("📈 Step 4: 趋势判断")
print("=" * 60)

# 趋势判断逻辑
# 1. 价格 > MA5 且 MA5 > MA20 → 强上涨趋势
# 2. 价格 < MA5 且 MA5 < MA20 → 强下跌趋势
# 3. 其他情况 → 横盘/震荡

def judge_trend(row):
    """判断趋势方向"""
    if pd.isna(row['MA5']) or pd.isna(row['MA20']):
        return '数据不足'
    
    if row['close'] > row['MA5'] and row['MA5'] > row['MA20']:
        return '强上涨'
    elif row['close'] < row['MA5'] and row['MA5'] < row['MA20']:
        return '强下跌'
    elif row['close'] > row['MA5']:
        return '弱势上涨'
    elif row['close'] < row['MA5']:
        return '弱势下跌'
    else:
        return '横盘'

df['趋势'] = df.apply(judge_trend, axis=1)

# 统计各趋势天数
trend_counts = df['趋势'].value_counts()
print("\n趋势统计：")
for trend, count in trend_counts.items():
    print(f"   • {trend}: {count} 天")

print()

# ============================================
# 第三步：生成交易信号
# ============================================
print("=" * 60)
print("🎯 生成交易信号")
print("=" * 60)

# 信号逻辑（经典MA交叉策略）
# 1. 金叉（MA5上穿MA20）→ 买入信号
# 2. 死叉（MA5下穿MA20）→ 卖出信号
# 3. 其他 → 持有

df['MA5_prev'] = df['MA5'].shift(1)
df['MA20_prev'] = df['MA20'].shift(1)

# 金叉：前一天MA5<MA20，今天MA5>MA20
df['金叉'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])

# 死叉：前一天MA5>MA20，今天MA5<MA20
df['死叉'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])

# 生成信号列
def get_signal(row):
    if row['金叉']:
        return '买入'
    elif row['死叉']:
        return '卖出'
    else:
        return '持有'

df['信号'] = df.apply(get_signal, axis=1)

# 统计信号
signal_counts = df['信号'].value_counts()
print("\n信号统计：")
for signal, count in signal_counts.items():
    print(f"   • {signal}: {count} 天")

# 列出买卖日期
buy_dates = df[df['信号'] == '买入'].index.tolist()
sell_dates = df[df['信号'] == '卖出'].index.tolist()

print("\n买入信号日期：")
for d in buy_dates:
    print(f"   • {d.strftime('%Y-%m-%d')} (价格={df.loc[d, 'close']:.2f})")

print("\n卖出信号日期：")
for d in sell_dates:
    print(f"   • {d.strftime('%Y-%m-%d')} (价格={df.loc[d, 'close']:.2f})")

print()

# ============================================
# 第四步：简单回测（Step 5）
# ============================================
print("=" * 60)
print("💰 Step 5: 简单回测 - 验证策略收益")
print("=" * 60)

print("""
回测说明：
┌────────────────────────────────────────────┐
│  回测 = 用历史数据模拟交易，计算收益       │
│                                            │
│  我们模拟两种策略：                        │
│  1. 买入持有策略：第一天买入，最后一天卖出 │
│  2. MA交叉策略：金叉买入，死叉卖出         │
│                                            │
│  然后对比两者的收益表现                    │
└────────────────────────────────────────────┘
""")

# 初始资金
initial_capital = 10000  # 1万元

# ---------- 策略1：买入持有 ----------
# 第一天买入，最后一天卖出
buy_hold_shares = initial_capital / df['close'].iloc[0]  # 能买多少股
buy_hold_final = buy_hold_shares * df['close'].iloc[-1]  # 最后价值
buy_hold_return = (buy_hold_final - initial_capital) / initial_capital * 100  # 收益率

print("📊 策略1：买入持有")
print(f"   初始资金：{initial_capital:.0f} 元")
print(f"   买入价格：{df['close'].iloc[0]:.2f} 元")
print(f"   卖出价格：{df['close'].iloc[-1]:.2f} 元")
print(f"   持有股数：{buy_hold_shares:.2f} 股")
print(f"   最终价值：{buy_hold_final:.2f} 元")
print(f"   收益率：{buy_hold_return:.2f}%")

# ---------- 策略2：MA交叉策略 ----------
# 模拟交易过程
capital = initial_capital
shares = 0  # 当前持有股数
trades = []  # 记录每笔交易

for idx, row in df.iterrows():
    if row['信号'] == '买入' and shares == 0:  # 有信号且当前空仓
        shares = capital / row['close']  # 全仓买入
        trades.append({
            'date': idx,
            'action': '买入',
            'price': row['close'],
            'shares': shares
        })
        capital = 0  # 资金转为股票
        
    elif row['信号'] == '卖出' and shares > 0:  # 有信号且当前持仓
        capital = shares * row['close']  # 全仓卖出
        trades.append({
            'date': idx,
            'action': '卖出',
            'price': row['close'],
            'shares': shares,
            'profit': capital - trades[-1]['shares'] * trades[-1]['price']
        })
        shares = 0  # 清仓

# 最后如果还持有股票，按最后价格计算
if shares > 0:
    capital = shares * df['close'].iloc[-1]

ma_final = capital
ma_return = (ma_final - initial_capital) / initial_capital * 100

print("\n📊 策略2：MA交叉策略")
print(f"   初始资金：{initial_capital:.0f} 元")
print(f"   交易次数：{len(trades)} 次")
for t in trades:
    print(f"      {t['date'].strftime('%Y-%m-%d')} {t['action']} @ {t['price']:.2f}")
print(f"   最终价值：{ma_final:.2f} 元")
print(f"   收益率：{ma_return:.2f}%")

# ---------- 对比 ----------
print("\n" + "=" * 60)
print("📊 策略对比")
print("=" * 60)
print(f"""
┌────────────────────┬──────────┬──────────┐
│ 策略               │ 最终价值 │ 收益率   │
├────────────────────┼──────────┼──────────┤
│ 买入持有           │ {buy_hold_final:>8.2f} │ {buy_hold_return:>7.2f}% │
│ MA交叉策略         │ {ma_final:>8.2f} │ {ma_return:>7.2f}% │
└────────────────────┴──────────┴──────────┘

结论：MA策略是否优于买入持有？
""")

if ma_return > buy_hold_return:
    print(f"   ✅ MA策略表现更好，多赚 {ma_return - buy_hold_return:.2f}%")
else:
    print(f"   ❌ MA策略表现较差，少赚 {buy_hold_return - ma_return:.2f}%")

print()

# ============================================
# 第五步：可视化回测结果
# ============================================
print("=" * 60)
print("🎨 绑制回测对比图")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# 图1：价格和MA
ax1 = axes[0]
ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax1.plot(df.index, df['MA5'], label='MA5', color='red', linestyle='--')
ax1.plot(df.index, df['MA20'], label='MA20', color='blue', linewidth=2)

# 标记买卖点
for t in trades:
    if t['action'] == '买入':
        ax1.scatter(t['date'], t['price'], color='green', marker='^', s=100, zorder=5)
        ax1.annotate('买入', (t['date'], t['price']), textcoords="offset points", 
                     xytext=(0,10), fontsize=9, color='green')
    elif t['action'] == '卖出':
        ax1.scatter(t['date'], t['price'], color='red', marker='v', s=100, zorder=5)
        ax1.annotate('卖出', (t['date'], t['price']), textcoords="offset points", 
                     xytext=(0,-15), fontsize=9, color='red')

ax1.set_title('价格走势与交易信号', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylabel('价格（元）')

# 图2：策略收益对比
ax2 = axes[1]
strategies = ['买入持有', 'MA交叉策略']
returns = [buy_hold_return, ma_return]
colors = ['gray', 'blue']

bars = ax2.bar(strategies, returns, color=colors, alpha=0.7)
ax2.set_title('策略收益率对比', fontsize=12, fontweight='bold')
ax2.set_ylabel('收益率 (%)')
ax2.grid(True, linestyle=':', alpha=0.6, axis='y')

# 标注数值
for bar, ret in zip(bars, returns):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
             f'{ret:.2f}%', ha='center', fontsize=11)

plt.xticks(rotation=0)
plt.tight_layout()

output_file = 'backtest_result.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 回测对比图已保存：{output_file}")
print()

# ============================================
# 小知识：回测的意义
# ============================================
print("=" * 60)
print("📖 回测的意义与局限")
print("=" * 60)
print("""
为什么需要回测？
┌────────────────────────────────────────────┐
│  1. 验证策略：信号真的能赚钱吗？           │
│  2. 优化参数：MA5好还是MA10好？            │
│  3. 了解风险：最大亏损是多少？             │
│  4. 对比基准：是否比简单持有更好？         │
└────────────────────────────────────────────┘

回测的局限（重要！）：
┌────────────────────────────────────────────┐
│  ⚠️ 过去表现 ≠ 未来表现                   │
│  ⚠️ 回测可能过度拟合历史数据               │
│  ⚠️ 实盘交易有滑点、手续费等成本           │
│  ⚠️ 市场环境可能变化                       │
└────────────────────────────────────────────┘

专业量化还需要考虑：
• 最大回撤（最大亏损幅度）
• 夏普比率（风险调整后收益）
• 交易成本（手续费、滑点）
• 资金管理（仓位控制）
""")

print("=" * 60)
print("🎉 Step 4 & 5 完成！")
print("=" * 60)
print("""
你学会了：
1. ✅ 趋势判断（强上涨、强下跌、横盘）
2. ✅ 生成交易信号（金叉买入、死叉卖出）
3. ✅ 简单回测（计算策略收益）
4. ✅ 对比不同策略的表现

下一步建议：
• 尝试调整MA周期（MA10 vs MA20）
• 加入更多指标（RSI、MACD）
• 学习更专业的回测框架（Backtrader）
""")