import time
import tweepy
import logging
import random
from btc_monitor import BitcoinWhaleTracker
from alert_pricebar import test_display as btc_price_bar
from eth_pricebar import test_display as eth_price_bar
from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret

class AlertSharkBot:
    def __init__(self):
        # Setup Twitter client
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Initialize BTC monitor with full address tracking
        self.btc_monitor = BitcoinWhaleTracker(min_btc=500)
        
        # Expand known exchanges and entities to track
        self.tracked_entities = {
            'exchanges': [
                'binance', 'coinbase', 'kraken', 'bybit', 'huobi', 
                'okex', 'kucoin', 'bitfinex', 'gemini', 'bitstamp',
                'bittrex', 'gate_io', 'ftx', 'cryptocom'
            ],
            'institutions': [
                'grayscale', 'microstrategy', 'tesla', 'block.one'
            ],
            'defi': [
                'blockfi', 'celsius'
            ],
            'mining_pools': [
                'antpool', 'btc.com', 'foundry', 'f2pool'
            ],
            'seized_assets': [
                'doj', 'fbi', 'usms'
            ]
        }
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('twitter_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('AlertSharkBot')
        
        # Define variable delays for rate limiting
        self.tweet_delays = [30, 45, 25, 75]  # Seconds between tweets

    def post_tweet_with_retry(self, message, max_retries=3):
        """Post tweet with retry mechanism"""
        for attempt in range(max_retries):
            try:
                tweet = self.client.create_tweet(text=message)
                self.logger.info(f"Tweet posted successfully")
                return True
            except Exception as e:
                if "Rate limit" in str(e):
                    wait_time = 60 * (attempt + 1)  # Progressive waiting: 60s, 120s, 180s
                    self.logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Failed to tweet: {e}")
                    return False
        return False

    def filter_important_transactions(self, message):
        """Enhanced filter to check for all important entities"""
        for category, entities in self.tracked_entities.items():
            if any(entity.lower() in message.lower() for entity in entities):
                return True
        return False

    def handle_btc_updates(self, updates):
        """Handle multiple BTC updates with varied delays and enhanced filtering"""
        if not updates:
            return False
            
        if isinstance(updates, list):
            important_updates = [
                update for update in updates 
                if self.filter_important_transactions(update)
            ]
            
            for i, update in enumerate(important_updates):
                delay = self.tweet_delays[i % len(self.tweet_delays)]
                if self.post_tweet_with_retry(update):
                    self.logger.info(f"Posted important BTC update {i+1}/{len(important_updates)}")
                    if i < len(important_updates) - 1:
                        self.logger.info(f"Waiting {delay} seconds before next tweet...")
                        time.sleep(delay)
            return bool(important_updates)
        else:
            if self.filter_important_transactions(updates):
                return self.post_tweet_with_retry(updates)
        return False

    def run(self):
        """Main bot loop with reordered priority"""
        self.logger.info("Starting Alert Shark Bot with reordered priority...")
        
        while True:
            try:
                # 1. BTC Price Bar update (Now first priority)
                self.logger.info("Getting BTC price bar update...")
                btc_price_update = btc_price_bar()
                if btc_price_update:
                    self.post_tweet_with_retry(btc_price_update)
                self.logger.info("Waiting 2 minutes after BTC price update...")
                time.sleep(120)  # Wait 2 minutes

                # 2. BTC Monitor updates (Now second priority)
                self.logger.info("Getting BTC monitor updates...")
                btc_updates = self.btc_monitor.monitor_transactions()
                
                if btc_updates:
                    if self.handle_btc_updates(btc_updates):
                        self.logger.info("Important movements detected, waiting 3 minutes...")
                        time.sleep(180)  # Wait 3 minutes
                else:
                    self.logger.info("No movements, proceeding to ETH updates...")

                # 3. ETH Price Bar update (Now third priority)
                self.logger.info("Getting ETH price bar update...")
                eth_update = eth_price_bar()
                if eth_update:
                    self.post_tweet_with_retry(eth_update)
                self.logger.info("Waiting 5 minutes after ETH price update...")
                time.sleep(300)  # Wait 5 minutes

                self.logger.info("Completing cycle, starting next round...")

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute on error

if __name__ == "__main__":
    bot = AlertSharkBot()
    bot.run()
