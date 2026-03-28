"""
Step 3: 绘制价格走势图
======================

学习目标：
1. 学会用 Matplotlib 绑制股票价格图
2. 在图上显示 MA5、MA10、MA20
3. 理解图表如何帮助我们判断趋势
4. 学会保存图片到文件

运行方式：
    python step3_plot_price.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 设置中文字体（避免中文显示乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']  # 中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# ============================================
# 第一步：准备数据
# ============================================
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

# 计算 MA
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA10'] = df['close'].rolling(window=10).mean()
df['MA20'] = df['close'].rolling(window=20).mean()

print("=" * 60)
print("📊 数据准备完成")
print("=" * 60)
print(f"日期范围：{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
print(f"价格范围：{df['close'].min():.2f} ~ {df['close'].max():.2f} 元")
print()

# ============================================
# 第二步：创建图表
# ============================================
print("=" * 60)
print("🎨 开始绑制图表...")
print("=" * 60)

# 创建画布（图形大小：12x6 英寸）
fig, ax = plt.subplots(figsize=(12, 6))

# 绑制收盘价（黑色实线）
ax.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)

# 绑制 MA5（红色虚线）
ax.plot(df.index, df['MA5'], label='MA5（5日均线）', color='red', linewidth=1, linestyle='--')

# 绑制 MA10（橙色虚线）
ax.plot(df.index, df['MA10'], label='MA10（10日均线）', color='orange', linewidth=1, linestyle='--')

# 绑制 MA20（蓝色实线，较粗）
ax.plot(df.index, df['MA20'], label='MA20（20日均线）', color='blue', linewidth=2)

# 设置标题和标签
ax.set_title('股票价格走势图（含移动平均线）', fontsize=14, fontweight='bold')
ax.set_xlabel('日期', fontsize=12)
ax.set_ylabel('价格（元）', fontsize=12)

# 显示图例（右上角）
ax.legend(loc='upper right', fontsize=10)

# 添加网格线（方便看数值）
ax.grid(True, linestyle=':', alpha=0.6)

# 旋转日期标签（避免重叠）
plt.xticks(rotation=45)

# 自动调整布局
plt.tight_layout()

print("""
图表说明：
┌────────────────────────────────────────────┐
│  黑色实线 → 收盘价（实际价格）             │
│  红色虚线 → MA5（短期趋势）                │
│  橙色虚线 → MA10（中期趋势）               │
│  蓝色实线 → MA20（长期趋势）               │
│                                            │
│  观察要点：                                │
│  • 价格在 MA 之上 → 上升趋势              │
│  • 价格在 MA 之下 → 下降趋势              │
│  • MA5 穿越 MA20 → 金叉/死叉              │
└────────────────────────────────────────────┘
""")

# ============================================
# 第三步：保存图片
# ============================================
output_file = 'price_with_ma.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ 图表已保存：{output_file}")
print()

# 显示图表（如果在本地运行）
# plt.show()

# ============================================
# 第四步：标记金叉/死叉点（进阶）
# ============================================
print("=" * 60)
print("🔍 标记金叉和死叉位置")
print("=" * 60)

# 计算金叉和死叉
df['MA5_prev'] = df['MA5'].shift(1)
df['MA20_prev'] = df['MA20'].shift(1)
df['golden_cross'] = (df['MA5_prev'] < df['MA20_prev']) & (df['MA5'] > df['MA20'])
df['death_cross'] = (df['MA5_prev'] > df['MA20_prev']) & (df['MA5'] < df['MA20'])

# 创建第二张图（标记交叉点）
fig2, ax2 = plt.subplots(figsize=(12, 6))

# 绑制价格和 MA
ax2.plot(df.index, df['close'], label='收盘价', color='black', linewidth=1.5)
ax2.plot(df.index, df['MA5'], label='MA5', color='red', linewidth=1, linestyle='--')
ax2.plot(df.index, df['MA20'], label='MA20', color='blue', linewidth=2)

# 标记金叉（绿色向上箭头）
golden_cross_points = df[df['golden_cross']]
if not golden_cross_points.empty:
    ax2.scatter(golden_cross_points.index, golden_cross_points['MA5'], 
                color='green', marker='^', s=100, label='金叉（买入信号）', zorder=5)
    for idx in golden_cross_points.index:
        ax2.annotate('金叉', (idx, golden_cross_points.loc[idx, 'MA5']), 
                     textcoords="offset points", xytext=(0,10), fontsize=8, color='green')

# 标记死叉（红色向下箭头）
death_cross_points = df[df['death_cross']]
if not death_cross_points.empty:
    ax2.scatter(death_cross_points.index, death_cross_points['MA5'], 
                color='red', marker='v', s=100, label='死叉（卖出信号）', zorder=5)
    for idx in death_cross_points.index:
        ax2.annotate('死叉', (idx, death_cross_points.loc[idx, 'MA5']), 
                     textcoords="offset points", xytext=(0,-15), fontsize=8, color='red')

# 设置标题和样式
ax2.set_title('股票价格走势图（标记金叉/死叉）', fontsize=14, fontweight='bold')
ax2.set_xlabel('日期', fontsize=12)
ax2.set_ylabel('价格（元）', fontsize=12)
ax2.legend(loc='upper right', fontsize=10)
ax2.grid(True, linestyle=':', alpha=0.6)
plt.xticks(rotation=45)
plt.tight_layout()

output_file2 = 'price_with_signals.png'
plt2_saved = plt.savefig(output_file2, dpi=150, bbox_inches='tight')
print(f"✅ 信号图已保存：{output_file2}")

# 统计信号
print(f"\n📊 信号统计：")
print(f"   金叉数量：{len(golden_cross_points)}")
print(f"   死叉数量：{len(death_cross_points)}")

if len(golden_cross_points) > 0:
    print("\n   金叉日期：")
    for idx in golden_cross_points.index:
        print(f"      • {idx.strftime('%Y-%m-%d')} (MA5={golden_cross_points.loc[idx, 'MA5']:.2f})")

if len(death_cross_points) > 0:
    print("\n   死叉日期：")
    for idx in death_cross_points.index:
        print(f"      • {idx.strftime('%Y-%m-%d')} (MA5={death_cross_points.loc[idx, 'MA5']:.2f})")

print()

# ============================================
# 小知识：Matplotlib 基础
# ============================================
print("=" * 60)
print("📖 Matplotlib 基础函数")
print("=" * 60)
print("""
常用绑图函数：

1. plt.subplots()      → 创建画布和坐标轴
   fig, ax = plt.subplots(figsize=(12, 6))

2. ax.plot()           → 绑制折线图
   ax.plot(x, y, label='名称', color='颜色', linestyle='样式')

3. ax.scatter()        → 绑制散点图（标记点）
   ax.scatter(x, y, color='颜色', marker='形状')

4. ax.set_title()      → 设置标题
5. ax.set_xlabel()     → 设置 X 轴标签
6. ax.set_ylabel()     → 设置 Y 轴标签
7. ax.legend()         → 显示图例
8. ax.grid()           → 添加网格线
9. plt.savefig()       → 保存图片
10. plt.show()         → 显示图片

线条样式：
• linestyle='-'   → 实线
• linestyle='--'  → 虚线
• linestyle=':'   → 点线

标记样式：
• marker='^'      → 向上三角形（金叉）
• marker='v'      → 向下三角形（死叉）
• marker='o'      → 圆点
""")

print("=" * 60)
print("🎉 Step 3 完成！")
print("=" * 60)
print("""
你学会了：
1. ✅ 用 Matplotlib 绑制价格走势图
2. ✅ 在图上显示多条 MA 线
3. ✅ 标记金叉/死叉信号点
4. ✅ 保存图片到文件

下一步：Step 4 - 趋势判断与交易信号
""")