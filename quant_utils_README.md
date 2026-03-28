# quant_utils.py - 量化学习通用工具

## 📚 功能说明

封装重复使用的功能，让每个 Step 的代码更简洁：

| 函数 | 作用 |
|------|------|
| `generate_stock_data()` | 生成模拟股票数据 |
| `add_ma()` | 添加 MA 列 |
| `plot_price_with_ma()` | 绑制价格和 MA 图 |
| `plot_indicator()` | 绑制指标图（带阈值线） |
| `simple_backtest()` | 简单回测 |
| `print_section()` | 打印分节标题 |
| `print_data_summary()` | 打印数据摘要 |

## 🚀 使用方式

```python
from quant_utils import generate_stock_data, add_ma, plot_price_with_ma

# 一行生成数据
df = generate_stock_data(days=60, trend_pattern='up_then_down')

# 一行添加 MA
df = add_ma(df, periods=[5, 10, 20])

# 一行绘图
plot_price_with_ma(df, save_path='chart.png')
```

## 📊 数据模式

`trend_pattern` 参数支持：

- `'random'` - 随机波动
- `'up_then_down'` - 先涨后跌
- `'up'` - 持续上涨
- `'down'` - 持续下跌
- `'volatile'` - 大幅波动