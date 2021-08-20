import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json
import time

st.set_page_config(layout="wide")


image = Image.open("bitcoin.jpeg")
st.image(image, width=800)
st.title("Why GME when you can BTC?")
st.markdown("This app retrieves cryptocurrency prices for the top 100 cryptocurrency from the **CoinMarketCap**!")


col1 = st.sidebar
col1.header('Input Options')
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))

col2, col3 = st.columns((2,1))

@st.cache
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')
    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coins = {}
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    for i in listings:
        coins[str(i['id'])] = i['slug']
    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    price = []
    volume_24h = []

    for i in listings:
        coin_name.append(i['slug'])
        coin_symbol.append(i['symbol'])
        price.append(i['quote'][currency_price_unit]['price'])
        percent_change_1h.append(i['quote'][currency_price_unit]['percentChange1h']) # percent_change_1h
        percent_change_24h.append(i['quote'][currency_price_unit]['percentChange24h']) #percent_change_24h
        percent_change_7d.append(i['quote'][currency_price_unit]['percentChange7d']) # percent_change_7d
        market_cap.append(i['quote'][currency_price_unit]['marketCap']) # market_cap
        volume_24h.append(i['quote'][currency_price_unit]['volume24h']) # volume_24h

    df = pd.DataFrame(columns=['coin_name', 'coin_symbol', 'marketCap', 'percentChange1h', 'percentChange24h', 'percentChange7d', 'price', 'volume24h'])
    df['coin_name'] = coin_name
    df['coin_symbol'] = coin_symbol
    df['price'] = price
    df['percentChange1h'] = percent_change_1h
    df['percentChange24h'] = percent_change_24h
    df['percentChange7d'] = percent_change_7d
    df['marketCap'] = market_cap
    df['volume24h'] = volume_24h
    return df

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Export to CSV File</a>'
    return href

def main(): 
    df = load_data()
    print("df is null?", df.empty)
    try:
        if df.empty:
            raise Exception("Coinmarketcap is down...")
        else:
            #user input
            sorted_coin = sorted(df["coin_symbol"])
            # selected_coin = col1.multiselect("Cryptocurrency", sorted_coin, sorted_coin)
            selected_coin = col1.multiselect("Cryptocurrency", sorted_coin)
            df_selected_coins = df[df["coin_symbol"].isin(selected_coin)]
            st.subheader("Display Selected Cryptocurrenc")
            st.dataframe(df_selected_coins)
            st.markdown(filedownload(df_selected_coins), unsafe_allow_html=True)
            #user slider
            num_coin = col1.slider("Display Top N Cryptocurrency", 1, 100, 100)
            df_slider_coins = df[:num_coin]
            if num_coin!=0:
                st.subheader("Display Top Cryptocurrency")
                st.dataframe(df_slider_coins)
                st.markdown(filedownload(df_slider_coins), unsafe_allow_html=True)
    except Exception as e:
        print(e)
        st.markdown(e)

if __name__ == "__main__":
    main()