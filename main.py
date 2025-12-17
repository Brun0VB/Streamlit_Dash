import streamlit as st
from steam import *
from ui import *

# Create tabs
tabs = st.tabs(["SteamData", "WishList"])

with tabs[0]:
    st.title("SteamData")
    showSteamWishList()

with tabs[1]:
    st.title("WishList")
    plot_wishlist_altair()
