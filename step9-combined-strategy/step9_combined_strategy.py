"""
Step 9: 多指标组合策略
======================

核心内容：
- 为什么要组合多个指标
- 常见的指标组合方式
- 设计综合信号系统
- 简单回测对比

运行方式：
    python step9_combined_strategy.py
"""

from quant_utils import (
    generate_stock_data, add_ma, 
    simple_backtest, print_section, print_data_summary
)
import pandas as pd
import numpy as np

# ============================================
# 核心：多指标计算
# ============================================

def calculate_all_indicators(df):
    """
    计算所有指标：MA、RSI、MACD、布林带
    """
    # ===== MA =====
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    
    # ===== RSI =====
    df['change'] = df['close'].diff()
    df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)
    df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)
    df['avg_gain'] = df['gain'].rolling(14).mean()
    df['avg_loss'] = df['loss'].rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + df['avg_gain'] / df['avg_loss']))
    
    # ===== MACD =====
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['DIF'] = ema12 - ema26
    df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2
    
    # ===== 布林带 =====
    df['BOLL_MID'] = df['close'].rolling(20).mean()
    df['BOLL_STD'] = df['close'].rolling(20).std()
    df['BOLL_UPPER'] = df['BOLL_MID'] + 2 * df['BOLL_STD']
    df['BOLL_LOWER'] = df['BOLL_MID'] - 2 * df['BOLL_STD']
    
    return df


def generate_single_signals(df):
    """
    生成各指标的单独信号
    """
    # ----- MA 信号 -----
    df['MA5_prev'] = df['MA5'].shift(1)
    df['MA20_prev'] = df['MA20'].shift(1)
    df['MA_golden'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])
    df['MA_death'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])
    
    # ----- RSI 信号 -----
    df['RSI_oversold'] = df['RSI'] < 30  # 超卖
    df['RSI_overbought'] = df['RSI'] > 70  # 超买
    
    # ----- MACD 信号 -----
    df['DIF_prev'] = df['DIF'].shift(1)
    df['DEA_prev'] = df['DEA'].shift(1)
    df['MACD_golden'] = (df['DIF_prev'] < df['DEA_prev']) & (df['DIF'] > df['DEA'])
    df['MACD_death'] = (df['DIF_prev'] > df['DEA_prev']) & (df['DIF'] < df['DEA'])
    
    # ----- 布林带信号 -----
    df['BOLL_lower_break'] = df['close'] < df['BOLL_LOWER']  # 跌破下轨
    df['BOLL_upper_break'] = df['close'] > df['BOLL_UPPER']  # 突破上轨
    
    return df


def generate_combined_signals(df):
    """
    生成组合信号（多指标验证）
    
    策略设计：
    1. 强买入：多个指标同时发出买入信号
    2. 弱买入：部分指标发出买入信号
    3. 强卖出：多个指标同时发出卖出信号
    4. 弱卖出：部分指标发出卖出信号
    """
    # 计算买入信号强度（0-3分）
    buy_score = 0
    
    # 条件1：MA金叉 或 价格在MA20上方
    ma_condition = df['MA_golden'] | (df['close'] > df['MA20'])
    
    # 条件2：RSI超卖 或 RSI从低位回升
    rsi_condition = df['RSI_oversold'] | (df['RSI'] < 40)
    
    # 条件3：MACD金叉 或 MACD柱转正
    macd_condition = df['MACD_golden'] | (df['MACD'] > 0)
    
    # 计算卖出信号强度
    sell_score = 0
    
    # 卖出条件
    sell_ma = df['MA_death'] | (df['close'] < df['MA20'])
    sell_rsi = df['RSI_overbought'] | (df['RSI'] > 70)
    sell_macd = df['MACD_death'] | (df['MACD'] < 0)
    
    # 生成综合信号
    def get_combined_signal(row):
        if pd.isna(row['RSI']) or pd.isna(row['MA20']):
            return '数据不足'
        
        buy_count = 0
        sell_count = 0
        
        # 买入条件计数
        if row['close'] > row['MA20']:
            buy_count += 1
        if row['RSI'] < 40:
            buy_count += 1
        if row['MACD'] > 0:
            buy_count += 1
        if row['close'] < row['BOLL_LOWER']:
            buy_count += 1  # 跌破下轨也可能是机会
        
        # 卖出条件计数
        if row['close'] < row['MA20']:
            sell_count += 1
        if row['RSI'] > 70:
            sell_count += 1
        if row['MACD'] < 0:
            sell_count += 1
        if row['close'] > row['BOLL_UPPER']:
            sell_count += 1
        
        # 判断信号
        if buy_count >= 3:
            return '强买入'
        elif buy_count == 2:
            return '弱买入'
        elif sell_count >= 3:
            return '强卖出'
        elif sell_count == 2:
            return '弱卖出'
        else:
            return '观望'
    
    df['综合信号'] = df.apply(get_combined_signal, axis=1)
    
    # 简化信号（用于回测）
    def get_trade_signal(row):
        signal = row['综合信号']
        if signal in ['强买入', '弱买入']:
            return '买入'
        elif signal in ['强卖出', '弱卖出']:
            return '卖出'
        return '持有'
    
    df['交易信号'] = df.apply(get_trade_signal, axis=1)
    
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 9: 多指标组合策略学习")

# 生成数据
df = generate_stock_data(days=60, trend_pattern='up_then_down')
print_data_summary(df)

# 计算所有指标
print_section("📊 计算所有指标")
df = calculate_all_indicators(df)
df = generate_single_signals(df)
print("已计算：MA、RSI、MACD、布林带")

# 生成组合信号
print_section("🔗 生成组合信号")

print("""
组合策略设计：
┌─────────────────────────────────────────────┐
│  买入条件（满足2个以上）：                   │
│  • 价格 > MA20                              │
│  • RSI < 40（偏低）                         │
│  • MACD > 0（多头）                         │
│  • 价格 < 布林下轨（超卖）                  │
│                                             │
│  卖出条件（满足2个以上）：                   │
│  • 价格 < MA20                              │
│  • RSI > 70（偏高）                         │
│  • MACD < 0（空头）                         │
│  • 价格 > 布林上轨（超买）                  │
│                                             │
│  信号强度：                                  │
│  • 强买入/强卖出：满足3+个条件             │
│  • 弱买入/弱卖出：满足2个条件              │
│  • 观望：其他情况                           │
└─────────────────────────────────────────────┘
""")

df = generate_combined_signals(df)

# 统计信号
signal_counts = df['综合信号'].value_counts()
print("\n综合信号统计：")
for s, c in signal_counts.items():
    print(f"  • {s}: {c} 天")

# ============================================
# 回测对比
# ============================================
print_section("💰 回测对比：单指标 vs 组合策略")

# 策略1：买入持有
buy_hold_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100

# 策略2：MA金叉死叉
def get_ma_signal(row):
    if row['MA_golden']:
        return '买入'
    if row['MA_death']:
        return '卖出'
    return '持有'
df['MA信号'] = df.apply(get_ma_signal, axis=1)
ma_result = simple_backtest(df, 'MA信号', 10000)

# 策略3：组合策略
combined_result = simple_backtest(df, '交易信号', 10000)

print(f"""
┌────────────────────┬──────────┬──────────┐
│ 策略               │ 最终价值 │ 收益率   │
├────────────────────┼──────────┼──────────┤
│ 买入持有           │ {10000*(1+buy_hold_return/100):>8.2f} │ {buy_hold_return:>7.2f}% │
│ MA金叉死叉         │ {ma_result['final_value']:>8.2f} │ {ma_result['return_rate']:>7.2f}% │
│ 组合策略           │ {combined_result['final_value']:>8.2f} │ {combined_result['return_rate']:>7.2f}% │
└────────────────────┴──────────┴──────────┘
""")

# 找出最佳策略
results = [
    ('买入持有', buy_hold_return),
    ('MA金叉死叉', ma_result['return_rate']),
    ('组合策略', combined_result['return_rate'])
]
best = max(results, key=lambda x: x[1])
print(f"🏆 最佳策略：{best[0]}（{best[1]:.2f}%）")

# ============================================
# 可视化
# ============================================
print_section("🎨 绑制组合信号图")

import matplotlib.pyplot as plt

fig, axes = plt.subplots(3, 1, figsize=(14, 10), 
                         gridspec_kw={'height_ratios': [2, 1, 1]})

# 图1：价格与指标
ax1 = axes[0]
ax1.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax1.plot(df.index, df['MA20'], label='MA20', color='blue', linewidth=1)
ax1.plot(df.index, df['BOLL_UPPER'], label='布林上轨', color='red', linestyle='--', alpha=0.5)
ax1.plot(df.index, df['BOLL_LOWER'], label='布林下轨', color='green', linestyle='--', alpha=0.5)

# 标记强买入/强卖出
strong_buy = df[df['综合信号'] == '强买入']
strong_sell = df[df['综合信号'] == '强卖出']
ax1.scatter(strong_buy.index, strong_buy['close'], color='green', marker='^', s=100, label='强买入', zorder=5)
ax1.scatter(strong_sell.index, strong_sell['close'], color='red', marker='v', s=100, label='强卖出', zorder=5)

ax1.set_title('价格与组合信号', fontsize=12, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, linestyle=':', alpha=0.6)

# 图2：RSI
ax2 = axes[1]
ax2.plot(df.index, df['RSI'], label='RSI', color='purple', linewidth=1.5)
ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
ax2.fill_between(df.index, 70, 100, color='red', alpha=0.1)
ax2.fill_between(df.index, 0, 30, color='green', alpha=0.1)
ax2.set_title('RSI 指标', fontsize=12, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylim(0, 100)

# 图3：MACD
ax3 = axes[2]
ax3.plot(df.index, df['DIF'], label='DIF', color='red', linewidth=1)
ax3.plot(df.index, df['DEA'], label='DEA', color='blue', linewidth=1)
colors = ['red' if v < 0 else 'green' for v in df['MACD']]
ax3.bar(df.index, df['MACD'], color=colors, alpha=0.3)
ax3.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
ax3.set_title('MACD 指标', fontsize=12, fontweight='bold')
ax3.legend(loc='upper right')
ax3.grid(True, linestyle=':', alpha=0.6)

plt.xticks(rotation=45)
plt.tight_layout()

output_file = 'combined_strategy_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 图表已保存：{output_file}")

# ============================================
# 小知识
# ============================================
print_section("📖 多指标组合原则")

print("""
为什么要组合指标？

1. 单一指标的局限
   • MA：滞后，震荡市频繁假信号
   • RSI：强趋势中可能长期超买/超卖
   • MACD：滞后，信号出现晚
   • 布林带：强趋势中价格可能长期在轨道外

2. 组合原则
   ┌────────────────────────────────────────────┐
   │  ✅ 趋势类 + 震荡类 组合效果最好          │
   │  ✅ 不同计算原理的指标互相印证            │
   │  ❌ 避免同类型指标重复（如 MA + EMA）    │
   └────────────────────────────────────────────┘

3. 经典组合
   • MA + RSI：趋势 + 超买超卖
   • MACD + RSI：趋势 + 动量
   • 布林带 + RSI：通道 + 超买超卖
   • MA + MACD + RSI：三重验证

4. 信号确认
   • 强信号：多个指标同时确认
   • 弱信号：部分指标确认
   • 冲突时：观望，等待更多确认

⚠️ 注意事项：
┌────────────────────────────────────────────┐
│  • 指标越多 ≠ 效果越好                     │
│  • 2-3个指标组合效果最佳                   │
│  • 回测验证是关键                          │
│  • 实盘需要考虑手续费和滑点                │
└────────────────────────────────────────────┘
""")

print_section("🎉 Step 9 完成！")
print("""
你学会了：
✅ 多指标组合的原理
✅ 组合信号的设计方法
✅ 单指标 vs 组合策略的回测对比
✅ 不同类型指标的互补性

下一步：Step 10 - 风险指标（最大回撤、夏普比率）
""")