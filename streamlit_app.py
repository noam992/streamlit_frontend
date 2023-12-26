import streamlit as st
import yfinance as yf
import pandas as pd


st.write("""
# Simple Stock Price App
         
Shown are the stock **closing price** and volume of Google!
         
""")

tickerSymbol = 'GOOGL'

try:
    tickerData = yf.Ticker(tickerSymbol)
    tickerDf = tickerData.history(period='1d', start='2010-5-31', end='2020-5-31')

    st.line_chart(tickerDf.Close)
    st.line_chart(tickerDf.Volume)

except Exception as e:
    st.error("An error occurred: {}".format(e))
