import time
import tweepy
import logging
from alert_shark_1m import test_display
from Block_alert import BitcoinWhaleTracker
from keys import bearer_token, consumer_key, consumer_secret, access_token, access_token_secret

class TwitterBot:
    def __init__(self):
        # Use Twitter API v2 authentication
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
        
        # Test authentication
        try:
            me = self.client.get_me()
            print(f"Authentication OK - User ID: {me.data.id}")
        except Exception as e:
            print("Error during authentication:", str(e))
            raise
            
        self.whale_tracker = BitcoinWhaleTracker(min_btc=500)  # Changed to 500 BTC minimum
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('TwitterBot')

    def post_tweet(self, message):
        try:
            # Use v2 create_tweet instead of update_status
            tweet = self.client.create_tweet(text=message)
            self.logger.info(f"Tweet posted successfully with id: {tweet.data['id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to tweet: {e}")
            return False

    def check_price_update(self):
        """Run and post price status from alert_shark_1m.py"""
        try:
            status = test_display()
            if status and status != "Error fetching prices":
                self.logger.info("Price status generated successfully")
                return status
            return None
        except Exception as e:
            self.logger.error(f"Error in price update: {e}")
            return None

    def check_whale_alert(self):
        """Run and post whale alerts from Block_alert.py"""
        try:
            block_hash = self.whale_tracker.get_latest_block()
            if block_hash:
                txs = self.whale_tracker.get_block_transactions(block_hash)
                for tx in txs:
                    if processed_tx := self.whale_tracker.process_transaction(tx):
                        btc_price = self.whale_tracker.get_btc_price()
                        usd_value = processed_tx['btc_volume'] * btc_price
                        fee_usd = processed_tx.get('fee', 0) * btc_price
                        
                        # Use the wallet names directly from Block_alert.py
                        sender = processed_tx['sender']    # Will contain exchange/wallet name if identified
                        receiver = processed_tx['receiver']  # Will contain exchange/wallet name if identified
                        
                        message = (
                            f"🚨🚨🚨 {processed_tx['tx_type']}:\n"
                            f"{processed_tx['btc_volume']:.2f} #BTC (${usd_value:,.2f}) "
                            f"was sent from {sender} to {receiver}\n"
                            f"and the transaction #fee was {processed_tx.get('fee', 0):.8f} BTC (${fee_usd:.2f})"
                        )
                        return self.post_tweet(message)
        except Exception as e:
            self.logger.error(f"Error in whale alert: {e}")
        return False

    def run(self):
        self.logger.info("Starting Twitter Bot...")
        while True:
            try:
                # Initial wait to ensure API readiness
                self.logger.info("Initial startup delay (30 seconds)...")
                time.sleep(30)
                
                # Get price update
                self.logger.info("Fetching price update...")
                status = self.check_price_update()
                
                if status:
                    # Wait before posting
                    self.logger.info("Waiting 2 minutes before posting price update...")
                    time.sleep(120)
                    # Post the price update
                    if self.post_tweet(status):
                        self.logger.info("Price update posted successfully")
                    else:
                        self.logger.error("Failed to post price update")
                
                # Continue with whale alerts
                self.logger.info("Waiting 2 minutes before checking whale alerts...")
                time.sleep(120)
                
                # Check whale alerts
                self.logger.info("Checking whale alerts...")
                if self.check_whale_alert():
                    # If whale alert was posted, wait 2 minutes
                    self.logger.info("Whale alert posted, waiting 2 minutes...")
                    time.sleep(120)
                else:
                    # If no whale alert, wait 3 minutes
                    self.logger.info("No whale activity, waiting 3 minutes...")
                    time.sleep(180)

            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    bot = TwitterBot()
    bot.run()