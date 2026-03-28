"""
Step 10: 风险指标（最大回撤、夏普比率）
========================================

核心内容：
- 最大回撤（Maximum Drawdown）
- 夏普比率（Sharpe Ratio）
- 年化收益与风险
- 风险调整后收益

运行方式：
    python step10_risk_metrics.py
"""

from quant_utils import (
    generate_stock_data, add_ma, simple_backtest,
    print_section, print_data_summary
)
import pandas as pd
import numpy as np

# ============================================
# 核心：风险指标计算
# ============================================

def calculate_returns(df):
    """
    计算每日收益率
    
    收益率 = (今天价格 - 昨天价格) / 昨天价格
    """
    df['returns'] = df['close'].pct_change()
    return df


def calculate_max_drawdown(df):
    """
    计算最大回撤（Maximum Drawdown）
    
    回撤 = 从最高点到最低点的跌幅
    最大回撤 = 历史上最严重的亏损幅度
    
    意义：
    • 告诉你最坏情况下会亏多少
    • 帮助评估能否承受这个风险
    """
    # 计算累计净值（假设初始为1）
    cumulative = (1 + df['returns']).cumprod()
    
    # 计算历史最高点
    running_max = cumulative.cummax()
    
    # 计算回撤
    drawdown = (cumulative - running_max) / running_max
    
    # 最大回撤
    max_drawdown = drawdown.min()
    
    return max_drawdown, drawdown


def calculate_sharpe_ratio(df, risk_free_rate=0.03):
    """
    计算夏普比率（Sharpe Ratio）
    
    夏普比率 = (年化收益 - 无风险利率) / 年化波动率
    
    意义：
    • 每承担1单位风险，获得多少超额收益
    • > 1 优秀
    • > 0.5 良好
    • < 0 不值得
    
    参数：
        df: DataFrame
        risk_free_rate: 无风险利率（默认3%，可近似用国债利率）
    """
    # 年化收益率（假设每年252个交易日）
    annual_return = df['returns'].mean() * 252
    
    # 年化波动率
    annual_volatility = df['returns'].std() * np.sqrt(252)
    
    # 夏普比率
    sharpe = (annual_return - risk_free_rate) / annual_volatility
    
    return sharpe, annual_return, annual_volatility


def calculate_all_metrics(df):
    """
    计算所有风险指标
    """
    # 计算收益率
    df = calculate_returns(df)
    
    # 最大回撤
    max_dd, drawdown = calculate_max_drawdown(df)
    
    # 夏普比率
    sharpe, ann_ret, ann_vol = calculate_sharpe_ratio(df)
    
    # 其他指标
    total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
    win_rate = (df['returns'] > 0).sum() / len(df['returns'].dropna()) * 100
    avg_gain = df[df['returns'] > 0]['returns'].mean()
    avg_loss = df[df['returns'] < 0]['returns'].mean()
    profit_factor = abs(avg_gain / avg_loss) if avg_loss != 0 else 0
    
    return {
        'total_return': total_return,
        'annual_return': ann_ret * 100,
        'annual_volatility': ann_vol * 100,
        'max_drawdown': max_dd * 100,
        'sharpe_ratio': sharpe,
        'win_rate': win_rate,
        'profit_factor': profit_factor
    }


# ============================================
# 主程序
# ============================================

print_section("Step 10: 风险指标学习")

# 生成数据（模拟不同市场环境）
df = generate_stock_data(days=252, trend_pattern='random', seed=42)  # 一年数据
print_data_summary(df)

print_section("📈 计算风险指标")

print("""
风险指标说明：
┌─────────────────────────────────────────────┐
│  为什么收益高不等于策略好？                  │
│                                             │
│  策略A：收益50%，最大回撤40%                │
│  策略B：收益30%，最大回撤10%                │
│                                             │
│  → 大多数人会选B，因为风险更低！            │
│                                             │
│  风险指标帮助我们要"风险调整后收益"          │
└─────────────────────────────────────────────┘
""")

# 计算指标
metrics = calculate_all_metrics(df)

# 显示结果
print("📊 风险指标汇总：")
print("=" * 50)
print(f"{'指标':<20} {'数值':>15} {'说明':>15}")
print("-" * 50)
print(f"{'总收益率':<20} {metrics['total_return']:>14.2f}%")
print(f"{'年化收益率':<20} {metrics['annual_return']:>14.2f}%")
print(f"{'年化波动率':<20} {metrics['annual_volatility']:>14.2f}%")
print(f"{'最大回撤':<20} {metrics['max_drawdown']:>14.2f}%")
print(f"{'夏普比率':<20} {metrics['sharpe_ratio']:>14.2f}")
print(f"{'胜率':<20} {metrics['win_rate']:>14.2f}%")
print(f"{'盈亏比':<20} {metrics['profit_factor']:>14.2f}")
print("=" * 50)

# 指标解读
print_section("🔍 指标解读")

print(f"""
最大回撤（Max Drawdown）: {metrics['max_drawdown']:.2f}%
┌─────────────────────────────────────────────┐
│  含义：历史上最严重的亏损幅度              │
│                                             │
│  评估标准：                                  │
│  • < 10%：低风险                            │
│  • 10-20%：中等风险                         │
│  • 20-30%：较高风险                         │
│  • > 30%：高风险                            │
│                                             │
│  当前状态：{'低风险' if metrics['max_drawdown'] > -10 else '中等风险' if metrics['max_drawdown'] > -20 else '较高风险' if metrics['max_drawdown'] > -30 else '高风险'}（{abs(metrics['max_drawdown']):.1f}%回撤）│
└─────────────────────────────────────────────┘

夏普比率（Sharpe Ratio）: {metrics['sharpe_ratio']:.2f}
┌─────────────────────────────────────────────┐
│  含义：每承担1单位风险获得的超额收益        │
│                                             │
│  评估标准：                                  │
│  • > 2：非常优秀                            │
│  • 1-2：优秀                                │
│  • 0.5-1：良好                              │
│  • 0-0.5：一般                              │
│  • < 0：不值得投资                          │
│                                             │
│  当前状态：{'非常优秀' if metrics['sharpe_ratio'] > 2 else '优秀' if metrics['sharpe_ratio'] > 1 else '良好' if metrics['sharpe_ratio'] > 0.5 else '一般' if metrics['sharpe_ratio'] > 0 else '不值得'}（{metrics['sharpe_ratio']:.2f}）│
└─────────────────────────────────────────────┘

胜率（Win Rate）: {metrics['win_rate']:.2f}%
┌─────────────────────────────────────────────┐
│  含义：盈利天数占总交易天数的比例          │
│                                             │
│  注意：胜率高不等于赚钱！                   │
│  • 胜率90% + 亏损时亏损大 = 可能亏钱       │
│  • 胜率40% + 盈利时盈利大 = 可能赚钱        │
│                                             │
│  需要结合盈亏比一起看                       │
└─────────────────────────────────────────────┘

盈亏比（Profit Factor）: {metrics['profit_factor']:.2f}
┌─────────────────────────────────────────────┐
│  含义：平均盈利 / 平均亏损                  │
│                                             │
│  评估标准：                                  │
│  • > 2：非常优秀                            │
│  • 1.5-2：良好                              │
│  • 1-1.5：一般                              │
│  • < 1：亏损策略                            │
└─────────────────────────────────────────────┘
""")

# ============================================
# 可视化
# ============================================
print_section("🎨 绑制风险分析图")

import matplotlib.pyplot as plt

df = calculate_returns(df)

# 计算累计收益和回撤
cumulative = (1 + df['returns']).cumprod()
running_max = cumulative.cummax()
drawdown = (cumulative - running_max) / running_max * 100

fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# 图1：累计收益
ax1 = axes[0]
ax1.plot(df.index, cumulative, label='累计收益', color='blue', linewidth=1.5)
ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
ax1.fill_between(df.index, 1, cumulative, where=cumulative > 1, alpha=0.3, color='green')
ax1.fill_between(df.index, cumulative, 1, where=cumulative < 1, alpha=0.3, color='red')
ax1.set_title(f'累计收益（总收益: {metrics["total_return"]:.2f}%）', fontsize=12, fontweight='bold')
ax1.legend()
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.set_ylabel('累计净值')

# 图2：回撤
ax2 = axes[1]
ax2.fill_between(df.index, 0, drawdown, color='red', alpha=0.3)
ax2.plot(df.index, drawdown, color='red', linewidth=1)
ax2.axhline(y=metrics['max_drawdown'], color='darkred', linestyle='--', label=f'最大回撤: {metrics["max_drawdown"]:.2f}%')
ax2.set_title('回撤分析', fontsize=12, fontweight='bold')
ax2.legend()
ax2.grid(True, linestyle=':', alpha=0.6)
ax2.set_ylabel('回撤(%)')

# 图3：收益分布
ax3 = axes[2]
ax3.hist(df['returns'].dropna() * 100, bins=50, color='steelblue', alpha=0.7, edgecolor='white')
ax3.axvline(x=df['returns'].mean() * 100, color='red', linestyle='--', label=f'平均收益: {df["returns"].mean()*100:.2f}%')
ax3.axvline(x=0, color='gray', linestyle='-', alpha=0.5)
ax3.set_title('日收益率分布', fontsize=12, fontweight='bold')
ax3.legend()
ax3.grid(True, linestyle=':', alpha=0.6)
ax3.set_xlabel('日收益率(%)')
ax3.set_ylabel('天数')

plt.tight_layout()

output_file = 'risk_metrics_chart.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 图表已保存：{output_file}")

# ============================================
# 小知识
# ============================================
print_section("📖 风险管理原则")

print("""
专业量化交易的核心：风险管理

1. 最大回撤控制
   • 设定止损线：如回撤超过20%就停止策略
   • 分散投资：不要把鸡蛋放在一个篮子里
   • 仓位管理：高风险时降低仓位

2. 夏普比率优化
   • 在相同收益下降低波动率
   • 在相同风险下提高收益
   • 选择夏普比率高的策略

3. 评估策略的关键指标组合
   • 收益 + 最大回撤 → 能否承受
   • 夏普比率 → 风险性价比
   • 胜率 + 盈亏比 → 稳定性

4. 实战建议
┌────────────────────────────────────────────┐
│  • 单策略最大回撤不超过20%                 │
│  • 夏普比率 > 0.5 才值得考虑              │
│  • 盈亏比 > 1.5 才有长期盈利可能           │
│  • 永远设置止损！永远设置止损！            │
└────────────────────────────────────────────┘
""")

print_section("🎉 Step 10 完成！")
print("""
你学会了：
✅ 最大回撤：最严重的亏损幅度
✅ 夏普比率：风险调整后的收益
✅ 胜率和盈亏比：策略稳定性指标
✅ 风险管理的基本原则

🎉 恭喜完成全部学习内容！
""")