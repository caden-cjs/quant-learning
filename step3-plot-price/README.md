# Step 3: 绑制价格走势图

## 📚 学习目标

1. 学会用 Matplotlib 绑制股票价格图
2. 在图上显示 MA5、MA10、MA20
3. 理解图表如何帮助我们判断趋势
4. 学会保存图片到文件

## 📖 知识点

### Matplotlib 基础

```python
# 创建画布
fig, ax = plt.subplots(figsize=(12, 6))

# 绑制折线
ax.plot(df.index, df['close'], label='收盘价', color='black')
ax.plot(df.index, df['MA5'], label='MA5', color='red', linestyle='--')

# 设置样式
ax.set_title('股票价格走势图')
ax.legend()
ax.grid(True)

# 保存图片
plt.savefig('price.png', dpi=150)
```

### 图表解读

- 黑色实线 → 收盘价（实际价格）
- 红色虚线 → MA5（短期趋势）
- 橙色虚线 → MA10（中期趋势）
- 蓝色实线 → MA20（长期趋势）

观察要点：
- 价格在 MA 之上 → 上升趋势
- 价格在 MA 之下 → 下降趋势
- MA5 穿越 MA20 → 金叉/死叉

## 🚀 运行方式

```bash
python step3_plot_price.py
```

## 📊 输出文件

- `price_with_ma.png` - 价格走势图（含MA）
- `price_with_signals.png` - 标记金叉/死叉的图

## 🤔 思考题

1. 图表比数字表格有什么优势？
2. 如何判断趋势的强弱？
3. 金叉后价格一定会涨吗？

## ➡️ 下一步

继续学习 Step 4: 趋势判断与交易信号