def test_display():
    """Test function to display Ethereum price status"""
    import requests
    import json
    from pathlib import Path
    import time
    
    # Constants and API endpoints
    ETH_ATH = 10000  # Ethereum's all-time high
    COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    CRYPTOCOMPARE_API = "https://min-api.cryptocompare.com/data/pricemulti?fsyms=ETH,BTC&tsyms=USD"
    COINSTATS_API = "https://api.coinstats.app/public/v1/markets?coinId="
    PRICE_HISTORY_FILE = Path('eth_price_history.json')

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

    def get_crypto_prices():
        """Get both ETH and BTC prices for ratio calculation"""
        try:
            response = requests.get(COINGECKO_API, timeout=10)
            response.raise_for_status()
            data = response.json()
            return float(data["ethereum"]["usd"]), float(data["bitcoin"]["usd"])
        except Exception as e:
            print(f"Error fetching from CoinGecko: {e}")
            try:
                response = requests.get(CRYPTOCOMPARE_API, timeout=10)
                response.raise_for_status()
                data = response.json()
                return float(data["ETH"]["USD"]), float(data["BTC"]["USD"])
            except Exception as e:
                print(f"Error fetching from CryptoCompare: {e}")
                return 0.0, 0.0

    def get_progress_bar(percentage):
        """Ethereum-styled progress bar using blue squares"""
        filled = min(int(percentage / 10), 10)
        bar = "🟦" * filled + "⬜" * (10 - filled)  # Blue squares for ETH
        if percentage % 10 == 0 and percentage <= 100:
            marker_position = int(percentage / 10) - 1
            if marker_position >= 0:
                bar = bar[:marker_position] + "💠" + bar[marker_position + 1:]  # Diamond for ETH
        return f"{bar} {percentage:.0f}%"

    # Fetch current prices
    eth_price, btc_price = get_crypto_prices()
    
    if eth_price == 0:
        print("Error fetching prices")
        return None
    
    # Load last price and calculate change
    last_price, last_time = load_last_price()
    if last_price > 0:
        price_change = eth_price - last_price
        price_change_pct = (price_change / last_price) * 100
        change_symbol = UP_ARROW if price_change > 0 else DOWN_ARROW
        change_text = f"{change_symbol} {abs(price_change_pct):.2f}% (${abs(price_change):,.2f})"
    else:
        change_text = f"{FLAT_ARROW} 0.00%"
    
    # Save current price for next comparison
    save_current_price(eth_price)
    
    # Calculate metrics
    percentage = (eth_price / ETH_ATH) * 100
    eth_btc_ratio = eth_price / btc_price if btc_price else 0
    
    # Build status message
    status = f"#Ethereum {change_text}\n\n"
    status += f"{get_progress_bar(percentage)}\n\n"
    status += f"${eth_price:,.2f}        eth/btc: {eth_btc_ratio:.3f}"
    
    print("\nTest Display Output:")
    print(status)
    
    return status

if __name__ == "__main__":
    test_display()
