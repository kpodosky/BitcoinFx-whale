def test_display():
    """Test function to display crypto price status without Twitter posting"""
    import requests
    import json
    
    # Constants and API endpoints
    BTC_ATH = 1000000
    MEMPOOL_API = "https://mempool.space/api/v1/prices"
    COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
    
    def get_btc_price():
        try:
            response = requests.get(MEMPOOL_API)
            response.raise_for_status()
            return float(response.json()["USD"])
        except Exception as e:
            print(f"Error fetching BTC price: {e}")
            return 0.0

    def get_eth_price():
        try:
            response = requests.get(COINGECKO_API)
            response.raise_for_status()
            data = response.json()
            return float(data[1]["current_price"])
        except Exception as e:
            print(f"Error fetching ETH price: {e}")
            return 0.0
            
    def get_progress_bar(percentage):
        filled = min(int(percentage / 10), 10)
        bar = "⬛" * filled + "⬜" * (10 - filled)
        if percentage % 10 == 0 and percentage <= 100:
            marker_position = int(percentage / 10) - 1
            if marker_position >= 0:
                bar = bar[:marker_position] + "🟥" + bar[marker_position + 1:]
        return f"{bar} {percentage:.0f}%"

    # Fetch current prices
    btc_price = get_btc_price()
    eth_price = get_eth_price()
    
    if btc_price == 0 or eth_price == 0:
        return "Error fetching prices"
        
    # Calculate metrics
    percentage = (btc_price / BTC_ATH) * 100
    eth_btc_ratio = eth_price / btc_price
    
    # Build status message
    status = f"Bitcoin ↔ +0.00%\n\n"  # Sample direction for test
    status += f"{get_progress_bar(percentage)}\n\n"
    status += f"${btc_price:,.2f}        eth/btc: {eth_btc_ratio:.2f}"
    
    print("\nTest Display Output:")
    print(status) 

if __name__ == "__main__":
    test_display()
    