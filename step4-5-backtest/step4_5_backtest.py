"""
Step 4-5: 趋势判断与简单回测
============================

核心内容：
- 趋势判断逻辑
- 生成交易信号
- 回测计算收益
- 策略对比

运行方式：
    python step4_5_backtest.py
"""

from quant_utils import (
    generate_stock_data, add_ma, 
    simple_backtest, print_section, print_data_summary
)
import matplotlib.pyplot as plt

# ============================================
# 核心：趋势判断
# ============================================

def judge_trend(df):
    """
    判断趋势方向
    
    规则：
    - 价格 > MA5 且 MA5 > MA20 → 强上涨
    - 价格 < MA5 且 MA5 < MA20 → 强下跌
    - 其他 → 横盘/震荡
    """
    def get_trend(row):
        if pd.isna(row['MA5']) or pd.isna(row['MA20']):
            return '数据不足'
        if row['close'] > row['MA5'] and row['MA5'] > row['MA20']:
            return '强上涨'
        if row['close'] < row['MA5'] and row['MA5'] < row['MA20']:
            return '强下跌'
        return '横盘'
    
    import pandas as pd
    df['趋势'] = df.apply(get_trend, axis=1)
    return df


# ============================================
# 核心：交易信号
# ============================================

def generate_signals(df):
    """
    生成交易信号
    
    金叉 → 买入
    死叉 → 卖出
    其他 → 持有
    """
    df['MA5_prev'] = df['MA5'].shift(1)
    df['MA20_prev'] = df['MA20'].shift(1)
    
    df['金叉'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])
    df['死叉'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])
    
    import pandas as pd
    def get_signal(row):
        if row['金叉']:
            return '买入'
        if row['死叉']:
            return '卖出'
        return '持有'
    
    df['信号'] = df.apply(get_signal, axis=1)
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 4-5: 趋势判断与回测")

# 生成数据（先涨后跌，便于观察回测效果）
df = generate_stock_data(days=60, trend_pattern='up_then_down')
df = add_ma(df, periods=[5, 20])
print_data_summary(df)

# Step 4: 趋势判断
print_section("📈 Step 4: 趋势判断")

print("""
趋势判断规则：
┌─────────────────────────────────────────────┐
│  价格 > MA5 且 MA5 > MA20 → 强上涨趋势     │
│  价格 < MA5 且 MA5 < MA20 → 强下跌趋势     │
│  其他情况 → 横盘/震荡                       │
└─────────────────────────────────────────────┘
""")

df = judge_trend(df)
print("趋势统计：")
for t, c in df['趋势'].value_counts().items():
    print(f"  • {t}: {c} 天")

# Step 5: 回测
print_section("💰 Step 5: 简单回测")

print("""
回测原理：
┌─────────────────────────────────────────────┐
│  用历史数据模拟交易，计算策略收益          │
│                                             │
│  收益率 = (最终价值 - 初始资金) / 初始资金 │
└─────────────────────────────────────────────┘
""")

# 生成交易信号
df = generate_signals(df)

print("信号统计：")
for s, c in df['信号'].value_counts().items():
    print(f"  • {s}: {c} 天")

# 策略1：买入持有
buy_hold_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100

# 策略2：MA交叉策略
import pandas as pd
ma_result = simple_backtest(df, '信号', initial_capital=10000)

# 对比
print_section("📊 策略对比")

print(f"""
┌────────────────────┬──────────┬──────────┐
│ 策略               │ 最终价值 │ 收益率   │
├────────────────────┼──────────┼──────────┤
│ 买入持有           │ {10000*(1+buy_hold_return/100):>8.2f} │ {buy_hold_return:>7.2f}% │
│ MA交叉策略         │ {ma_result['final_value']:>8.2f} │ {ma_result['return_rate']:>7.2f}% │
└────────────────────┴──────────┴──────────┘
""")

if ma_result['return_rate'] > buy_hold_return:
    print(f"✅ MA策略优于买入持有，多赚 {ma_result['return_rate'] - buy_hold_return:.2f}%")
else:
    print(f"❌ MA策略不如买入持有，少赚 {buy_hold_return - ma_result['return_rate']:.2f}%")

print_section("🎉 完成！")
print("""
你学会了：
✅ 趋势判断：MA 相对位置
✅ 交易信号：金叉买入、死叉卖出
✅ 回测计算：模拟交易收益
✅ 策略对比：基准 vs 策略

⚠️ 回测局限：
- 过去表现 ≠ 未来表现
- 实盘有手续费、滑点成本
- 可能过度拟合历史数据

下一步：Step 6 - RSI 指标
""")