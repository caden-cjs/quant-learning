"""
Step 6: RSI（相对强弱指标）- 简洁版
==================================

使用 quant_utils 工具模块，代码更简洁！
核心内容一目了然，方便理解 RSI 的本质。

运行方式：
    python step6_rsi_v2.py
"""

from quant_utils import (
    generate_stock_data, add_ma, 
    plot_price_with_ma, plot_indicator,
    print_section, print_data_summary
)
import pandas as pd

# ============================================
# 核心：RSI 计算逻辑
# ============================================

def calculate_rsi(df, period=14):
    """
    计算 RSI
    
    RSI 原理：
    衡量"上涨力量"占"总波动力量"的比例
    RSI = 100 - 100/(1 + 平均上涨/平均下跌)
    
    参数：
        df: DataFrame（包含 close 列）
        period: 周期（默认14）
    
    返回：
        添加了 RSI 列的 DataFrame
    """
    # 1. 计算价格变化
    df['change'] = df['close'].diff()
    
    # 2. 分离上涨和下跌
    df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)   # 上涨部分
    df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)  # 下跌部分（取正）
    
    # 3. 计算平均值
    df['avg_gain'] = df['gain'].rolling(window=period).mean()
    df['avg_loss'] = df['loss'].rolling(window=period).mean()
    
    # 4. 计算 RSI
    df['RS'] = df['avg_gain'] / df['avg_loss']
    df['RSI'] = 100 - (100 / (1 + df['RS']))
    
    return df


def analyze_rsi_signals(df):
    """
    分析 RSI 超买超卖信号
    
    超买：RSI > 70 → 可能要跌
    超卖：RSI < 30 → 可能要涨
    
    返回：
        添加了信号列的 DataFrame
    """
    df['超买'] = df['RSI'] > 70
    df['超卖'] = df['RSI'] < 30
    
    # 结合 MA 的综合信号
    def get_signal(row):
        if pd.isna(row['RSI']) or pd.isna(row['MA20']):
            return '数据不足'
        if row['RSI'] < 30 and row['close'] < row['MA20']:
            return '强买入'  # 超卖 + 价格低于MA
        if row['RSI'] > 70 and row['close'] > row['MA20']:
            return '强卖出'  # 超买 + 价格高于MA
        if row['RSI'] < 30:
            return '弱买入'
        if row['RSI'] > 70:
            return '弱卖出'
        return '观望'
    
    df['信号'] = df.apply(get_signal, axis=1)
    return df


# ============================================
# 主程序
# ============================================

print_section("Step 6: RSI 指标学习")

# 生成数据（一行代码！）
df = generate_stock_data(trend_pattern='volatile')  # 大幅波动，便于观察 RSI
print_data_summary(df)

# 添加 MA
df = add_ma(df, periods=[5, 20])

# ========== 核心：计算 RSI ==========
print_section("📈 计算 RSI")
df = calculate_rsi(df, period=14)

print("""
RSI 公式：
┌─────────────────────────────────────────────┐
│  RSI = 100 - 100/(1 + 平均上涨/平均下跌)    │
│                                             │
│  • RSI > 70 → 超买（涨太多，可能要跌）      │
│  • RSI < 30 → 超卖（跌太多，可能要涨）      │
│  • RSI ≈ 50 → 平衡状态                      │
└─────────────────────────────────────────────┘
""")

# 分析信号
print_section("🔍 分析超买超卖")
df = analyze_rsi_signals(df)

# 统计
print(f"超买天数：{df['超买'].sum()} 天")
print(f"超卖天数：{df['超卖'].sum()} 天")

# 显示信号统计
signal_counts = df['信号'].value_counts()
print("\n综合信号：")
for s, c in signal_counts.items():
    print(f"  • {s}: {c} 天")

# 绘图
print_section("🎨 绑制图表")
plot_indicator(df, 'RSI', 'RSI 指标', 
               upper_threshold=70, lower_threshold=30,
               save_path='rsi_chart_v2.png')

print_section("🎉 完成！")
print("""
你学会了：
✅ RSI 的核心计算公式
✅ 超买（>70）和超卖（<30）的含义
✅ RSI 与 MA 结合使用

⚠️ 注意：
- 超买不等于马上跌！
- 超卖不等于马上涨！
- 结合多个指标更可靠！
""")