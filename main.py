import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import timedelta

st.write("""
# Stock Price App
The chart below represents the evolution of Brazilian stock prices over the years.
""")

@st.cache_data
def load_data(companies):
    stock_data = yf.Tickers(companies)
    stock_prices = stock_data.history(period='1d', start='2015-01-01', end='2024-07-01')
    stock_prices = stock_prices["Close"]
    return stock_prices

data = load_data("ITUB4.SA BBAS3.SA VALE3.SA ABEV3.SA MGLU3.SA PETR4.SA GGBR4.SA")

st.sidebar.header("Filters")
selected_stocks = st.sidebar.multiselect("Choose stocks to display on the chart", data.columns)
start_date = data.index.min().to_pydatetime()
end_date = data.index.max().to_pydatetime()
date_range = st.sidebar.slider("Select the period", 
                                min_value=start_date, 
                                max_value=end_date, value=(start_date, end_date), step=timedelta(days=1))

# Filter data
data = data.loc[date_range[0]:date_range[1]]
# Filter stocks
if selected_stocks:
    data = data[selected_stocks]
    if len(selected_stocks) == 1:
        data = data.rename(columns={selected_stocks[0]: "Close"})

st.line_chart(data)

# Performance calculation
performance_text = ""

if len(selected_stocks) == 0:
    selected_stocks = list(data.columns)
elif len(selected_stocks) == 1:
    data = data.rename(columns={"Close": selected_stocks[0]})

portfolio = [1000 for stock in selected_stocks]
total_initial_portfolio = sum(portfolio)

for i, stock in enumerate(selected_stocks):
    stock_performance = data[stock].iloc[-1] / data[stock].iloc[0] - 1
    stock_performance = float(stock_performance)

    portfolio[i] = portfolio[i] * (1 + stock_performance)

    if stock_performance > 0:
        performance_text += f"  \n{stock}: :green[{stock_performance:.1%}]"
    elif stock_performance < 0:
        performance_text += f"  \n{stock}: :red[{stock_performance:.1%}]"
    else:
        performance_text += f"  \n{stock}: {stock_performance:.1%}"

total_final_portfolio = sum(portfolio)
portfolio_performance = total_final_portfolio / total_initial_portfolio - 1

if portfolio_performance > 0:
    portfolio_performance_text = f"Portfolio performance with all assets: :green[{portfolio_performance:.1%}]"
elif portfolio_performance < 0:
    portfolio_performance_text = f"Portfolio performance with all assets: :red[{portfolio_performance:.1%}]"
else:
    portfolio_performance_text = f"Portfolio performance with all assets: {portfolio_performance:.1%}"

st.write(f"""
### Stock Performance
This was the performance of each stock over the selected period:

{performance_text}

{portfolio_performance_text}
""")
