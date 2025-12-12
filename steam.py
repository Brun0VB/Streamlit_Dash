import requests 

class steamclient:
    """Cliente para interagir com a Steam API"""
    
    BASE_URL = "https://api.steampowered.com"
    
    def __init__(self, steamid, webapikey):
        self.steamid = steamid
        self.webapikey = webapikey

    def getAppName(self, appid):
        """Fetch app details including name and price"""
        appdetail = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br").json()
        
        if appdetail[str(appid)]["success"]:
            data = appdetail[str(appid)].get("data")
            name = data.get("name", "Unknown App")
            
            return {
                "appid": appid,
                "name": name,
            }
    
    def getAppPrice(self, appid):
        """Fetch app details including name and price"""
        appdetail = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br").json()
        
        if appdetail[str(appid)]["success"]:
            data = appdetail[str(appid)].get("data")
            name = data.get("name", "Unknown App")
            
            # Extract price from price_overview
            price = None
            currency = None
            if "price_overview" in data:
                price_overview = data["price_overview"]
                price = price_overview.get("final", 0) / 100  # Price is in cents
                currency = price_overview.get("currency", "BRL")
            
            return {
                "appid": appid,
                "name": name,
                "price": price,
                "currency": currency
            }
        
        return {
            "appid": appid,
            "name": "Unknown App",
            "price": None,
            "currency": None
        }

    def getSteamWishList(self):
        wishlist = requests.get(f"{self.BASE_URL}/IWishlistService/GetWishlist/v1/?key={self.webapikey}&steamid={self.steamid}").json()["response"]["items"]
        appids = [item["appid"] for item in wishlist]
        
        return appids #retorna lista de app ids
    
    def getSteamAppPrice(self, appid):
        app_info = self.getAppPrice(appid)
        return {"price": app_info["price"], "currency": app_info["currency"]}

    