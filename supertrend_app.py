import streamlit as st
import pandas as pd
import yfinance as yf
from ta.trend import SuperTrend

# --- CONFIG ---
PERIOD = 10
MULTIPLIER = 3
LOOKBACK = "1y"  # how much data to pull

st.set_page_config(page_title="Supertrend (10,3) Screener", layout="centered")

st.title("📈 S&P 500 Supertrend (10,3) Screener")
st.caption("Find stocks crossing above the Supertrend indicator today")

# --- Load ticker list from GitHub ---
@st.cache_data
def load_tickers():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    df['Symbol'] = df['Symbol'].str.replace('.', '-', regex=False)
    return df

tickers_df = load_tickers()
tickers = tickers_df['Symbol'].tolist()

# --- Supertrend Crossing Logic ---
def check_supertrend_cross(ticker):
    try:
        df = yf.download(ticker, period=LOOKBACK, interval="1d", progress=False)
        df.dropna(inplace=True)

        if len(df) < PERIOD + 2:
            return False

        st_ind = SuperTrend(high=df['High'], low=df['Low'], close=df['Close'],
                            window=PERIOD, multiplier=MULTIPLIER)
        df['supertrend'] = st_ind.supertrend()

        # Crossing up condition: prev close < prev ST and current close > current ST
        if df['Close'].iloc[-2] < df['supertrend'].iloc[-2] and df['Close'].iloc[-1] > df['supertrend'].iloc[-1]:
            return True
        else:
            return False
    except:
        return False

# --- Button to trigger scanning ---
if st.button("🔄 Scan for Supertrend Crosses"):
    crossing_up = []

    with st.spinner("Scanning stocks..."):
        for symbol in tickers:
            if check_supertrend_cross(symbol):
                crossing_up.append(symbol)

    st.success(f"Found {len(crossing_up)} stocks crossing above Supertrend today.")
    if crossing_up:
        st.dataframe(pd.DataFrame(crossing_up, columns=["Ticker"]))
    else:
        st.write("🚫 No stocks crossed above the Supertrend today.")

else:
    st.info("Click the button above to start scanning.")

