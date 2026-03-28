# Step 6: RSI（相对强弱指标）

## 📚 学习目标

1. 理解 RSI 的原理和计算方法
2. 学会用 Python 计算 RSI
3. 理解超买（RSI>70）和超卖（RSI<30）
4. 将 RSI 与 MA 结合使用

## 📖 知识点

### RSI 原理

```
RSI 衡量"上涨力量"占"总波动力量"的比例

RSI = 100 - 100/(1 + 平均上涨/平均下跌)
```

### RSI 判断标准

| RSI 值 | 含义 | 建议 |
|--------|------|------|
| > 70 | 超买（涨太多） | 可能要跌，考虑卖出 |
| < 30 | 超卖（跌太多） | 可能要涨，考虑买入 |
| 50 左右 | 平衡 | 无明确信号 |

### Python 计算

```python
# 计算价格变化
df['change'] = df['close'].diff()

# 分离上涨和下跌
df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)
df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)

# 计算平均
df['avg_gain'] = df['gain'].rolling(14).mean()
df['avg_loss'] = df['loss'].rolling(14).mean()

# 计算 RSI
df['RS'] = df['avg_gain'] / df['avg_loss']
df['RSI'] = 100 - (100 / (1 + df['RS']))
```

## 🚀 运行方式

```bash
python step6_rsi.py
```

## ⚠️ 注意事项

- 超买不等于马上跌！强势股可能长期维持在超买区域
- 超卖不等于马上涨！弱势股可能长期维持在超卖区域
- 结合其他指标更可靠！

## ➡️ 下一步

继续学习 Step 7: MACD 指标