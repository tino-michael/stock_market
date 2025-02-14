def calculate_bollinger_sig(data, period=20):
    med = data.iloc[-period:].median()
    std = data.iloc[-period:].std()
    last = data.iloc[-1]
    sig = (last - med) / (2*std)

    return sig


def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def calculate_ma_deviation(data, period=100):
    ma = data.mean()
    deviation = (data.iloc[-1] - ma) / ma * 100  # percentage deviation
    return deviation
