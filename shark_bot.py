import requests
import json
import tweepy
import time
from typing import Tuple, Dict

# Constants
BTC_ATH = 1000000  # Reference point for percentage calculations
REFRESH_INTERVAL = 180  # Time between updates in seconds
MEMPOOL_API = "https://mempool.space/api/v1/prices"
COINGECKO_API = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"

class CryptoTracker:
    def __init__(self, twitter_creds: Dict[str, str]):
        self.previous_btc_price = None
        self.client = self._setup_twitter(twitter_creds)
        
    def _setup_twitter(self, creds: Dict[str, str]) -> tweepy.Client:
        return tweepy.Client(
            bearer_token=creds['bearer_token'],
            consumer_key=creds['consumer_key'],
            consumer_secret=creds['consumer_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret'],
            wait_on_rate_limit=True
        )

    def get_btc_price(self) -> float:
        """Fetch current Bitcoin price from Mempool API"""
        try:
            response = requests.get(MEMPOOL_API)
            response.raise_for_status()
            return float(response.json()["USD"])
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            print(f"Error fetching BTC price: {e}")
            return 0.0

    def get_eth_price(self) -> float:
        """Fetch current Ethereum price from CoinGecko API"""
        try:
            response = requests.get(COINGECKO_API)
            response.raise_for_status()
            data = response.json()
            return float(data[1]["current_price"])  # ETH is typically second in the list
        except (requests.RequestException, KeyError, json.JSONDecodeError, IndexError) as e:
            print(f"Error fetching ETH price: {e}")
            return 0.0

    def calculate_price_change(self, current_price: float) -> Tuple[str, float]:
        """
        Calculate price change percentage and direction
        Returns: (direction_arrow, percentage_change)
        """
        if self.previous_btc_price is None:
            self.previous_btc_price = current_price
            return "𓆝 𓆟 𓆞 𓆝 𓆟", 0.0
        
        price_change = current_price - self.previous_btc_price
        price_change_pct = (price_change / self.previous_btc_price) * 100
        
        arrow = "↑" if price_change >= 0 else "↓"
        
        self.previous_btc_price = current_price
        return arrow, price_change_pct

    def get_progress_bar(self, percentage: float) -> str:
        """Generate progress bar based on percentage of ATH"""
        filled = min(int(percentage / 10), 10)
        bar = "⬛" * filled + "⬜" * (10 - filled)
        
        # Add red marker at each 10% interval if we're exactly at that percentage
        if percentage % 10 == 0 and percentage <= 100:
            marker_position = int(percentage / 10) - 1
            if marker_position >= 0:
                bar = bar[:marker_position] + "🟥" + bar[marker_position + 1:]
                
        return f"{bar} {percentage:.0f}%"

    def get_header(self, percentage: float, direction: str, price_change_pct: float) -> str:
        """Generate header with price change percentage"""
        base_header = "Bitcoin" if percentage >= 25 else "Bitcoin"
        # Format percentage with appropriate sign and 2 decimal places
        pct_str = f"+{price_change_pct:.2f}%" if price_change_pct >= 0 else f"{price_change_pct:.2f}%"
        return f"{base_header} {direction} {pct_str}"

    def generate_status(self) -> str:
        """Generate the complete status update"""
        btc_price = self.get_btc_price()
        eth_price = self.get_eth_price()
        
        if btc_price == 0 or eth_price == 0:
            return "Error fetching prices"
                                    
        percentage = (btc_price / BTC_ATH) * 100
        eth_btc_ratio = eth_price / btc_price
        
        # Get price change direction and percentage
        direction, price_change_pct = self.calculate_price_change(btc_price)
        
        # Build status message
        status = f"{self.get_header(percentage, direction, price_change_pct)}\n\n"
        status += f"{self.get_progress_bar(percentage)}\n\n"
        status += f"${btc_price:,.2f}        eth/btc: {eth_btc_ratio:.2f}"
        
        return status

    def run(self):
        """Main loop to fetch prices and post updates"""
        while True:
            try:
                status = self.generate_status()
                self.client.create_tweet(text=status)
                print(status)
                time.sleep(REFRESH_INTERVAL)
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(30)  # Wait a minute before retrying

if __name__ == "__main__":
    # Twitter credentials should be imported from keys.py
    from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret
    
    creds = {
        'bearer_token': bearer_token,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    }
    
    tracker = CryptoTracker(creds)
    tracker.run()