"""
加密货币数据获取演示
===================

演示如何获取实时数据并计算指标
"""

import ccxt
import pandas as pd
import numpy as np

# ============================================
# 获取实时数据
# ============================================

print("=" * 60)
print("🚀 加密货币实时数据演示")
print("=" * 60)

# 创建交易所实例
exchange = ccxt.binance()

# 获取 BTC 实时价格
print("\n📊 获取 BTC/USDT 实时数据...\n")

ticker = exchange.fetch_ticker('BTC/USDT')
print(f"💰 当前价格: {ticker['last']:,.2f} USDT")
print(f"📈 24h涨跌: {ticker['percentage']:+.2f}%")
print(f"📊 24h最高: {ticker['high']:,.2f} USDT")
print(f"📊 24h最低: {ticker['low']:,.2f} USDT")
print(f"💼 24h成交量: {ticker['quoteVolume']:,.0f} USDT")

# ============================================
# 获取 K 线数据
# ============================================

print("\n" + "=" * 60)
print("📉 获取最近 100 根 1 小时 K 线...")
print("=" * 60)

ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=100)

df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('datetime', inplace=True)
df.drop('timestamp', axis=1, inplace=True)

# ============================================
# 计算指标
# ============================================

print("\n📊 计算技术指标...")

# MA
df['MA5'] = df['close'].rolling(5).mean()
df['MA20'] = df['close'].rolling(20).mean()

# RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(14).mean()
avg_loss = loss.rolling(14).mean()
df['RSI'] = 100 - (100 / (1 + avg_gain / avg_loss))

# MACD
ema12 = df['close'].ewm(span=12, adjust=False).mean()
ema26 = df['close'].ewm(span=26, adjust=False).mean()
df['DIF'] = ema12 - ema26
df['DEA'] = df['DIF'].ewm(span=9, adjust=False).mean()
df['MACD'] = (df['DIF'] - df['DEA']) * 2

# ============================================
# 显示结果
# ============================================

print("\n最近 10 小时数据（含指标）：")
print("-" * 80)
cols = ['close', 'MA5', 'MA20', 'RSI', 'MACD']
print(df[cols].tail(10).round(2))
print("-" * 80)

# ============================================
# 生成信号
# ============================================

last = df.iloc[-1]

print("\n" + "=" * 60)
print("🎯 当前信号分析")
print("=" * 60)

print(f"\n📍 当前状态：")
print(f"   价格: {last['close']:,.2f} USDT")
print(f"   MA5: {last['MA5']:,.2f} USDT")
print(f"   MA20: {last['MA20']:,.2f} USDT")
print(f"   RSI: {last['RSI']:.1f}")
print(f"   MACD柱: {last['MACD']:.2f}")

print(f"\n📈 趋势判断：")
if last['close'] > last['MA20']:
    print(f"   价格 > MA20 → 上升趋势")
else:
    print(f"   价格 < MA20 → 下降趋势")

print(f"\n📊 超买超卖：")
if last['RSI'] > 70:
    print(f"   RSI > 70 → 超买区域")
elif last['RSI'] < 30:
    print(f"   RSI < 30 → 超卖区域")
else:
    print(f"   RSI 在正常区域")

print(f"\n💪 动能：")
if last['MACD'] > 0:
    print(f"   MACD柱 > 0 → 多头动能强")
else:
    print(f"   MACD柱 < 0 → 空头动能强")

# 综合信号
buy_signals = 0
sell_signals = 0

if last['close'] > last['MA20']:
    buy_signals += 1
else:
    sell_signals += 1

if last['RSI'] < 40:
    buy_signals += 1
elif last['RSI'] > 70:
    sell_signals += 1

if last['MACD'] > 0:
    buy_signals += 1
else:
    sell_signals += 1

print("\n" + "=" * 60)
print("🚦 交易信号")
print("=" * 60)

if buy_signals >= 2:
    print(f"\n  ✅ 建议操作：买入")
    print(f"   信号强度：{buy_signals}/3")
elif sell_signals >= 2:
    print(f"\n  ⚠️ 建议操作：卖出")
    print(f"   信号强度：{sell_signals}/3")
else:
    print(f"\n  ⏸️ 建议操作：观望")
    print(f"   买入信号：{buy_signals}/3")
    print(f"   卖出信号：{sell_signals}/3")

print("\n" + "=" * 60)
print("使用说明：")
print("=" * 60)
print("""
1. 实时运行：
   python crypto_live_trading.py

2. 修改交易对：
   修改代码中的 symbol = 'BTC/USDT' 
   可选：ETH/USDT, SOL/USDT, DOGE/USDT 等

3. 修改周期：
   timeframe = '1h'  # 可选: 1m, 5m, 15m, 1h, 4h, 1d

4. 停止运行：
   按 Ctrl+C
""")