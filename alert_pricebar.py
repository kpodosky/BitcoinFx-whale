def test_display():
    """Test function to display crypto price status without Twitter posting"""
    import requests
    import json
    from pathlib import Path
    import time
    
    # Constants and API endpoints
    BTC_ATH = 1000000
    COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD"
    COINSTATS_API = "https://api.coinstats.app/public/v1/markets?coinId="
    PRICE_HISTORY_FILE = Path('btc_price_history.json')

    # Add Unicode arrow constants
    UP_ARROW = "\u2197\ufe0f"    # ↗️ (Unicode U+2197 with variation selector)
    DOWN_ARROW = "\u2198\ufe0f"  # ↙️ (Unicode U+2198 with variation selector)
    FLAT_ARROW = "\u2194\ufe0f"  # ↔️ (Unicode U+2194 with variation selector)

    def load_last_price():
        try:
            if PRICE_HISTORY_FILE.exists():
                with open(PRICE_HISTORY_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('price', 0), data.get('timestamp', 0)
            return 0, 0
        except:
            return 0, 0
    
    def save_current_price(price):
        try:
            with open(PRICE_HISTORY_FILE, 'w') as f:
                json.dump({
                    'price': price,
                    'timestamp': time.time()
                }, f)
        except:
            pass

    def get_btc_price():
        try:
            # Try CoinGecko first
            response = requests.get(COINGECKO_API, timeout=10)
            response.raise_for_status()
            return float(response.json()["bitcoin"]["usd"])
        except Exception as e:
            print(f"Error fetching from CoinGecko: {e}")
            try:
                # Try CryptoCompare as backup
                response = requests.get(CRYPTOCOMPARE_API, timeout=10)
                response.raise_for_status()
                return float(response.json()["BTC"]["USD"])
            except Exception as e:
                print(f"Error fetching from CryptoCompare: {e}")
                try:
                    # Try CoinStats as final backup
                    response = requests.get(COINSTATS_API + "bitcoin", timeout=10)
                    response.raise_for_status()
                    return float(response.json()["pairs"][0]["price"])
                except Exception as e:
                    print(f"Error fetching from CoinStats: {e}")
                    return 0.0

    def get_eth_price():
        try:
            # Try CoinGecko first
            response = requests.get(COINGECKO_API, timeout=10)
            response.raise_for_status()
            return float(response.json()["ethereum"]["usd"])
        except Exception as e:
            print(f"Error fetching from CoinGecko: {e}")
            try:
                # Try CryptoCompare as backup
                response = requests.get(CRYPTOCOMPARE_API, timeout=10)
                response.raise_for_status()
                return float(response.json()["ETH"]["USD"])
            except Exception as e:
                print(f"Error fetching from CryptoCompare: {e}")
                try:
                    # Try CoinStats as final backup
                    response = requests.get(COINSTATS_API + "ethereum", timeout=10)
                    response.raise_for_status()
                    return float(response.json()["pairs"][0]["price"])
                except Exception as e:
                    print(f"Error fetching from CoinStats: {e}")
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
        print("Error fetching prices")
        return None
    
    # Load last price and calculate change
    last_price, last_time = load_last_price()
    if last_price > 0:
        price_change = btc_price - last_price
        price_change_pct = (price_change / last_price) * 100
        change_symbol = UP_ARROW if price_change > 0 else DOWN_ARROW
        change_text = f"{change_symbol} {abs(price_change_pct):.2f}% (${abs(price_change):,.2f})"
    else:
        change_text = f"{FLAT_ARROW} 0.00%"
    
    # Save current price for next comparison
    save_current_price(btc_price)
    
    # Calculate other metrics
    percentage = (btc_price / BTC_ATH) * 100
    eth_btc_ratio = eth_price / btc_price
    
    # Build status message with price change
    status = f"#Bitcoin  {change_text}\n\n"
    status += f"{get_progress_bar(percentage)}\n\n"
    status += f"${btc_price:,.2f}        eth/btc: {eth_btc_ratio:.3f}"
    
    # Print for debugging
    print("\nTest Display Output:")
    print(status)
    
    return status

if __name__ == "__main__":
    test_display()
