import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def user_input():
    st.sidebar.header("Investor details")

    age = st.sidebar.slider("Enter your age", 18, 70, 30)

    q0 = st.sidebar.selectbox(
        "Required annual return (1 - 10%, 3 - 30%)", [1, 2, 3], index=1)
    q1 = st.sidebar.selectbox(
        "Reaction to 20% loss in 1 year (1 - Exit, 3 - Hold)", [1, 2, 3], index=1)
    q2 = st.sidebar.selectbox(
        "Investment experience (1 - Beginner, 3 - Expert)", [1, 2, 3], index=1)
    time = st.sidebar.selectbox(
        "Investment horizon (1 - <1 year, 3 - >3 years)", [1, 2, 3], index=1)
    q3 = st.sidebar.selectbox(
        "Were you active in 2008 crash? (1 - Yes, 2 - No)", [1, 2], index=1)

    risk_score = q0 * 0.25 + q1 * 0.25 + q2 * 0.25 + time * 0.25

    if q3 == 1:
        risk_score -= 0.5
    if age < 35:
        risk_score += 0.5
    elif age > 55:
        risk_score -= 0.5

    return round(risk_score, 2)

def asset_allocation(risk_score):
    asset_class = {"Equity": 0, "Bonds": 0, "Real_Estate": 0, "Gold": 0, "Crypto": 0}
    if risk_score <= 1.5:
        asset_class.update({"Equity": 20, "Bonds": 50, "Real_Estate": 5, "Gold": 20, "Crypto": 5})
    elif risk_score <= 2.5:
        asset_class.update({"Equity": 40, "Bonds": 20, "Real_Estate": 10, "Gold": 20, "Crypto": 10})
    else:
        asset_class.update({"Equity": 60, "Bonds": 10, "Real_Estate": 5, "Gold": 5, "Crypto": 20})
    return asset_class

def recommend_etfs(asset_class):
    etf_db = {
        "Equity": {
            "VTI": "Vanguard Total Stock Market ETF",
            "VOO": "Vanguard S&P 500 ETF",
            "QQQ": "Invesco QQQ Trust",
        },
        "Bonds": {
            "BND": "Vanguard Total Bond Market ETF",
            "TLT": "iShares 20+ Year Treasury Bond ETF",
            "LQD": "iShares Investment Grade Bond ETF",
        },
        "Real_Estate": {
            "VNQ": "Vanguard Real Estate ETF",
            "SCHH": "Schwab U.S. REIT ETF",
            "IYR": "iShares U.S. Real Estate ETF",
        },
        "Gold": {
            "GLD": "SPDR Gold Shares",
            "IAU": "iShares Gold Trust",
            "SGOL": "Aberdeen Standard Gold ETF",
        },
        "Crypto": {
            "BITO": "ProShares Bitcoin Strategy ETF",
            "WGMI": "Valkyrie Bitcoin Miners ETF",
            "BCHN": "Grayscale Bitcoin Cash Trust",
        }
    }

    recommendation = {}
    for asset_name, allocation in asset_class.items():
        if allocation > 0:
            etfs = list(etf_db[asset_name].items())[:3]
            sub_allocation = allocation / len(etfs)
            recommendation[asset_name] = []
            for symbol, name in etfs:
                recommendation[asset_name].append({
                    "etf_symbol": symbol,
                    "etf_name": name,
                    "allocation": round(sub_allocation, 2)
                })

    return recommendation

def fetch_etfdata(recommendation):
    data = {}
    for asset in recommendation:
        for etf in recommendation[asset]:
            etf_symbol = etf["etf_symbol"]
            try:
                ticker = yf.Ticker(etf_symbol)
                hist = ticker.history(period="1y")
                if not hist.empty:
                    start_price = hist['Close'].iloc[0]
                    end_price = hist['Close'].iloc[-1]
                    return_1y = ((end_price - start_price) / start_price) * 100
                    data[etf_symbol] = {
                        "current price": round(end_price, 2),
                        "year highest": round(hist['Close'].max(), 2),
                        "year lowest": round(hist['Close'].min(), 2),
                        "volatility": round(hist['Close'].std(), 2),
                        "1Y return (%)": round(return_1y, 2)
                    }
                else:
                    data[etf_symbol] = {"error": "No data"}
            except Exception as e:
                data[etf_symbol] = {"error": str(e)}
    return data

def display_etf_data(etf_data):
    if not etf_data:
        st.warning("No ETF data available to display.")
        return
    df = pd.DataFrame.from_dict(etf_data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'ETF Symbol'}, inplace=True)
    st.subheader("ETF Performance Summary (1-Year)")
    st.dataframe(df.style.format({
        "current price": "₹{:.2f}",
        "year highest": "₹{:.2f}",
        "year lowest": "₹{:.2f}",
        "volatility": "{:.2f}",
        "1Y return (%)": "{:.2f}%"
    }))

def main():
    st.title('YOUR PERSONALISED ROBO INVESTMENT-ADVISOR')

    risk_score = user_input()
    asset_class = asset_allocation(risk_score)
    recommendation = recommend_etfs(asset_class)
    etf_data = fetch_etfdata(recommendation)

    st.subheader("Your Risk Score")
    st.metric("Score", risk_score)

    st.subheader("Your Asset Allocation (%)")
    st.write(asset_class)

    # Pie chart for allocation
    fig, ax = plt.subplots()
    ax.pie(asset_class.values(), labels=asset_class.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    st.subheader('Recommended ETFs')
    display_etf_data(etf_data)

    st.subheader("Investment Advice")
    if risk_score < 1.5:
        st.info("You are a conservative investor. Prioritize capital preservation with limited equity exposure.")
    elif risk_score < 2.5:
        st.info("You are a balanced investor. Maintain a diversified portfolio with moderate equity and bond allocation.")
    else:
        st.info("You are an aggressive investor. You can take higher risks for higher returns.")

main() 
