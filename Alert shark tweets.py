import time
import json
import tweepy
import logging
from typing import List, Tuple, Dict
from collections import deque
from dataclasses import dataclass
from alert_shark_1m import test_display
from report_bitcoin import BitcoinWhaleTracker

@dataclass
class TransactionData:
    btc_value: float
    svg_path: str
    timestamp: str

class TwitterPoster:
    def __init__(self, creds: Dict[str, str]):
        # Setup authentication
        auth = tweepy.OAuthHandler(creds['consumer_key'], creds['consumer_secret'])
        auth.set_access_token(creds['access_token'], creds['access_token_secret'])
        
        # Initialize API v1.1 for media uploads
        self.api = tweepy.API(auth)
        
        # Initialize v2 client
        self.client = tweepy.Client(
            bearer_token=creds['bearer_token'],
            consumer_key=creds['consumer_key'],
            consumer_secret=creds['consumer_secret'],
            access_token=creds['access_token'],
            access_token_secret=creds['access_token_secret'],
            wait_on_rate_limit=True
        )

    def post_tweets(self, text_output: str, svg_images: List[Tuple[float, str]]):
        try:
            # Post initial text tweet
            self.client.create_tweet(text=text_output[:280])
            time.sleep(2)  # Rate limit padding
            
            # Sort SVGs by Bitcoin value and get top 2
            sorted_svgs = sorted(svg_images, key=lambda x: x[0], reverse=True)[:2]
            
            # Post SVG images
            for _, svg_path in sorted_svgs:
                try:
                    # Upload media
                    media = self.api.media_upload(svg_path)
                    # Create tweet with media
                    self.client.create_tweet(media_ids=[media.media_id_string])
                    time.sleep(2)  # Rate limit padding
                except Exception as e:
                    logging.error(f"Error posting SVG {svg_path}: {e}")
                    
        except Exception as e:
            logging.error(f"Error in post_tweets: {e}")

class BitcoinMonitor:
    def __init__(self, twitter_creds: Dict[str, str], min_btc=100):
        self.logger = self._setup_logging()
        self.twitter_poster = TwitterPoster(twitter_creds)
        self.whale_tracker = BitcoinWhaleTracker(min_btc)
        self.recent_transactions = deque(maxlen=10)
        
    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bitcoin_monitor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('BitcoinMonitor')

    def collect_data(self) -> Tuple[str, List[Tuple[float, str]]]:
        """Collect data from both sources"""
        price_status = test_display()
        transactions = []
        
        try:
            block_hash = self.whale_tracker.get_latest_block()
            if block_hash:
                for tx in self.whale_tracker.get_block_transactions(block_hash):
                    processed_tx = self.whale_tracker.process_transaction(tx)
                    if processed_tx:
                        transactions.append(
                            TransactionData(
                                processed_tx['btc_volume'],
                                processed_tx.get('svg_path', ''),
                                processed_tx['timestamp']
                            )
                        )
        except Exception as e:
            self.logger.error(f"Error collecting whale transactions: {e}")

        svg_images = [(tx.btc_value, tx.svg_path) for tx in transactions]
        return price_status, svg_images

    def run(self, interval: int = 60):
        """Main monitoring loop"""
        self.logger.info("Starting Bitcoin Monitor...")
        
        while True:
            try:
                price_status, svg_images = self.collect_data()
                
                if price_status and svg_images:
                    self.twitter_poster.post_tweets(price_status, svg_images)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret
    
    creds = {
        'bearer_token': bearer_token,
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'access_token': access_token,
        'access_token_secret': access_token_secret
    }
    
    monitor = BitcoinMonitor(creds)
    monitor.run()