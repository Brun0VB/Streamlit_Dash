import streamlit as st
from steam import *

# Create tabs
tabs = st.tabs(["SteamData", "WishList"])

with tabs[0]:
    st.title("SteamData")
    getSteamWishList()

with tabs[1]:
    st.title("WishList")
    viewWishlistDatabase()
