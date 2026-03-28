"""
Step 3: 绘制价格走势图
======================

核心内容：
- Matplotlib 基础绑图
- 在图上显示价格和 MA
- 标记金叉/死叉信号

运行方式：
    python step3_plot_price.py
"""

from quant_utils import (
    generate_stock_data, add_ma, 
    plot_price_with_ma, print_section, print_data_summary
)
import matplotlib.pyplot as plt

# ============================================
# 核心：绑图逻辑
# ============================================

def plot_with_signals(df, save_path='price_chart.png'):
    """
    绘制价格图并标记金叉/死叉
    
    Matplotlib 核心函数：
    - ax.plot() → 折线图
    - ax.scatter() → 散点图（标记点）
    - ax.legend() → 图例
    - plt.savefig() → 保存图片
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绑制价格和 MA
    ax.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
    ax.plot(df.index, df['MA5'], label='MA5', color='red', linestyle='--')
    ax.plot(df.index, df['MA20'], label='MA20', color='blue', linewidth=2)
    
    # 标记金叉（绿色向上箭头）
    golden = df[df['金叉']]
    if len(golden) > 0:
        ax.scatter(golden.index, golden['MA5'], color='green', marker='^', s=100, label='金叉')
    
    # 标记死叉（红色向下箭头）
    death = df[df['死叉']]
    if len(death) > 0:
        ax.scatter(death.index, death['MA5'], color='red', marker='v', s=100, label='死叉')
    
    # 设置样式
    ax.set_title('价格走势与 MA', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ 图表已保存：{save_path}")
    
    return fig, ax


# ============================================
# 主程序
# ============================================

print_section("Step 3: 绘制价格走势图")

# 生成数据并计算 MA
df = generate_stock_data(days=60)
df = add_ma(df, periods=[5, 20])
print_data_summary(df)

# 计算交叉信号
df['MA5_prev'] = df['MA5'].shift(1)
df['MA20_prev'] = df['MA20'].shift(1)
df['金叉'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])
df['死叉'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])

# 核心：绑图
print_section("🎨 Matplotlib 绑图")

print("""
┌─────────────────────────────────────────────┐
│  Matplotlib 常用函数：                      │
│                                             │
│  fig, ax = plt.subplots(figsize=(12,6))    │
│  ax.plot(x, y, label='名称', color='颜色') │
│  ax.scatter(x, y, marker='形状')           │
│  ax.set_title('标题')                       │
│  ax.legend()                                │
│  ax.grid(True)                              │
│  plt.savefig('文件名.png')                  │
│                                             │
│  标记样式：                                  │
│  marker='^' → 向上三角形（金叉）            │
│  marker='v' → 向下三角形（死叉）            │
└─────────────────────────────────────────────┘
""")

# 绑图
plot_with_signals(df, save_path='price_chart.png')

print_section("🎉 完成！")
print("""
你学会了：
✅ 用 Matplotlib 绑制折线图
✅ 在图上标记金叉/死叉信号
✅ 保存图片到文件

下一步：Step 4-5 - 趋势判断与回测
""")