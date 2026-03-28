# 📈 量化交易学习笔记

欢迎来到量化交易学习仓库！这里记录了我的学习过程和代码示例。

## 🎯 学习路线

| 阶段 | 内容 | 状态 |
|------|------|------|
| Step 1 | 生成模拟股票数据 - OHLCV | ✅ 完成 |
| Step 2 | 计算移动平均线 (MA) | ✅ 完成 |
| Step 3 | 绘制价格走势图 | ✅ 完成 |
| Step 4 | 趋势判断与信号 | ✅ 完成 |
| Step 5 | 简单回测逻辑 | ✅ 完成 |
| Step 6 | RSI（相对强弱指标） | ✅ 完成 |
| Step 7 | MACD（指数平滑异同移动平均线） | ✅ 完成 |
| Step 8 | 布林带 | 🔲 待开始 |

## ⭐ quant_utils 工具模块

所有 Step 统一使用工具模块，代码更简洁：

```python
from quant_utils import generate_stock_data, add_ma
df = generate_stock_data(days=60)  # 一行生成数据
df = add_ma(df, periods=[5, 20])   # 一行添加 MA
```

## 🛠️ 环境要求

```bash
pip install pandas numpy matplotlib
```

Happy Learning! 🚀
