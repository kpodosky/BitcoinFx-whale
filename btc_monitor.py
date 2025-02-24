# -*- coding: UTF-8 -*-
import re
import requests
import time
import os
from datetime import datetime
from collections import defaultdict

class BitcoinWhaleTracker:
    def __init__(self, min_btc=500):  # Changed from 100 to 500
        self.base_url = "https://blockchain.info"
        self.min_btc = min_btc
        self.satoshi_to_btc = 100000000
        self.processed_blocks = set()  # Track processed blocks
        self.last_block_height = None  # Track last block height
        
        # Address statistics tracking
        self.address_stats = defaultdict(lambda: {
            'received_count': 0,
            'sent_count': 0,
            'total_received': 0,
            'total_sent': 0,
            'last_seen': None
        })
        
        # Known addresses database (keeping original database)
        self.known_addresses = {
            'binance': {
                'type': 'exchange',
                'addresses': [
                    '3FaA4dJuuvJFyUHbqHLkZKJcuDPugvG3zE',  # Binance Hot Wallet
                    '1NDyJtNTjmwk5xPNhjgAMu4HDHigtobu1s',  # Binance Cold Wallet
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # Binance-BTC-2
                    '1LQv8aKtQoiY5M5zkaG8RWL7LMwNzNsLfb',  # Binance-BTC-3
                    '1AC4fMwgY8j9onSbXEWeH6Zan8QGMSdmtA'   # Binance-BTC-4
                ]
            },
            'coinbase': {
                'type': 'exchange',
                'addresses': [
                    '3FzScn724foqFRWvL1kCZwitQvcxrnSQ4K',  # Coinbase Hot Wallet
                    '3Kzh9qAqVWQhEsfQz7zEQL1EuSx5tyNLNS',  # Coinbase Cold Storage
                    '1CWYTCvwKfH5cWnX3VcAykgTsmjsuB3wXe',  # Coinbase-BTC-2
                    '1FxkfJQLJTXpW6QmxGT6hEo5DtBrnFpM3r',  # Coinbase-BTC-3
                    '1GR9qNz7zgtaW5HwwVpEJWMnGWhsbsieCG'   # Coinbase Prime
                ]
                  },
            'grayscale': {
                'type': 'investment',
                'addresses': [
                    'bc1qe7nps5yv7ruc884zscwrk9g2mxvqh7tkxfxwny',
                    'bc1qkz7u6l5c8wqz8nc5yxkls2j8u4y2hkdzlgfnl4'
                ]
            },
            'microstrategy': {
                'type': 'corporate',
                'addresses': [
                    'bc1qazcm763858nkj2dj986etajv6wquslv8uxwczt',
                    'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh'
                ]
            },
            'blockfi': {
                'type': 'lending',
                'addresses': [
                    'bc1q7kyrfmx49qa7n6g8mvlh36d4w9zf4lkwfg4j5q',
                    'bc1qd73dxk2qfs2x5wv2sesvqrzgx7t5tqt4y5vpym'
                ]
            },
            'celsius': {
                'type': 'lending',
                'addresses': [
                    'bc1q06ymtp6eq27mlz3ppv8z7esc8vq3v4nsjx9eng',
                    'bc1qcex3e38gqh6qnzpn9jth5drgfyh5k9sjzq3rkm'
                ]
            },
            'kraken': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Kraken Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # Kraken Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR',  # Kraken-BTC-2
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv'   # Kraken-BTC-3
                ]
            },
            'bitfinex': {
                'type': 'exchange',
                'addresses': [
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitfinex Hot Wallet
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bitfinex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bitfinex-BTC-2
                ]
            },
            'huobi': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # Huobi Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Huobi Cold Storage
                    '1HckjUpRGcrrRAtFaaCAUaGjsPx9oYmLaZ'   # Huobi-BTC-2
                ]
            },
            'okex': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # OKEx Hot Wallet
                    '3LCGsSmfr24demGvriN4e3ft8wEcDuHFqh',  # OKEx Cold Storage
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE'   # OKEx-BTC-2
                ]
            },
            'gemini': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Gemini Hot Wallet
                    '393HLwqnkrJMxYQTHjWBJPAKC3UG6k6FwB',  # Gemini Cold Storage
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ'   # Gemini-BTC-2
                ]
            },
            'bitstamp': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Bitstamp Hot Wallet
                    '3D2oetdNuZUqQHPJmcMDDHYoqkyNVsFk9r',  # Bitstamp Cold Storage
                    '3DbAZpqKhUBu4rqafHzj7hWquoBL6gFBvj'   # Bitstamp-BTC-2
                ]
            },
            'bittrex': {
                'type': 'exchange',
                'addresses': [
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Hot Wallet
                    '3KJrsjfg1dD6CrsTeHdM5SSk3PhXjNwhA7',  # Bittrex Cold Storage
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL'   # Bittrex-BTC-2
                ]
            },
            'kucoin': {
                'type': 'exchange',
                'addresses': [
                    '3M219KR5vEneNb47ewrPfWyb5jQ2DjxRP6',  # KuCoin Hot Wallet
                    '3H5JTt42K7RmZtromfTSefcMEFMMe18pMD',  # KuCoin Cold Storage
                    '3AfP9N7KNq2pYXiGQdgNJy8SD2Mo7pQKUR'   # KuCoin-BTC-2
                ]
            },
            'gate_io': {
                'type': 'exchange',
                'addresses': [
                    '3FupZp77ySr7jwoLYEJ9mwzJpvoNBXsBnE',  # Gate.io Hot Wallet
                    '38WUPqGLXphpD1DwkMR8koGfd5UQfRnmrk',  # Gate.io Cold Storage
                ]
            },
            'ftx': {
                'type': 'exchange',
                'addresses': [
                    '3LQUu4v9z6KNch71j7kbj8GPeAGUo1FW6a',  # FTX Hot Wallet
                    '3E1jkR1PJ8hFUqCkDjimwPoF2bZVrkqnpv',  # FTX Cold Storage
                ]
            },
            'bybit': {
                'type': 'exchange',
                'addresses': [
                    '3JZq4atUahhuA9rLhXLMhhTo133J9rF97j',  # Bybit Hot Wallet
                    '3QW95MafxER9W7kWDcosQNdLk4Z36TYJZL',  # Bybit Cold Storage
                ]
            },
            'cryptocom': {
                'type': 'exchange',
                'addresses': [
                    '3P3QsMVK89JBNqZQv5zMAKG8FK3kJM4rjt',  # Crypto.com Hot Wallet
                    '3AAzK4Xbu8PTM8AD7gw2XaMZavL6xoKWHQ',  # Crypto.com Cold Storage
                ]
            }
        }

        # Add exchange wallet pattern recognition
        self.exchange_patterns = {
            "Binance": {
                "prefixes": ["bnb1", "0x"],
                "patterns": [
                    r"^1FzWLk.*",
                    r"^bc1q[0-9a-zA-Z]{38,48}$",
                ],
                "known_ranges": ["34", "3J", "bc1q"]
            },
            "Coinbase": {
                "prefixes": ["0x", "bc1q"],
                "patterns": [
                    r"^1Qab.*",
                    r"^bc1q[0-9a-zA-Z]{59}$"
                ],
                "known_ranges": ["13", "3", "bc1q"]
            },
            "Kraken": {
                "prefixes": ["0x", "bc1q"],
                "patterns": [
                    r"^1kraken.*",
                    r"^bc1q[a-zA-Z0-9]{38,42}$"
                ],
                "known_ranges": ["13", "3", "bc1q"]
            },
            "Huobi": {
                "prefixes": ["0x", "ht"],
                "patterns": [
                    r"^1HuobiW.*",
                    r"^bc1q[0-9a-zA-Z]{38,42}$"
                ],
                "known_ranges": ["1H", "bc1q"]
            }
        }

        # Add additional known addresses
        self.known_addresses.update({
            'mining_pools': {
                'type': 'mining',
                'addresses': [
                    '1CK6KHY6MHgYvmRQ4PAafKYDrg1ejbH1cE',  # AntPool
                    '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Satoshi-Genesis
                    '12ib7dApVFvg82TXKycWBNpN8kFyiAN1dr',  # BTC.com
                    '3Gpex6g5FPmYWm26myFq7dW12ntd8zMcCY'   # Foundry
                ]
            },
            'corporate_treasury': {
                'type': 'corporate',
                'addresses': [
                    '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo',  # MicroStrategy
                    '3E1MQVD1yN5FLsCR1HZvnVw9PfWF5BQswC',  # Tesla-BTC
                    '1P1iThxBH542Gmk1kZNXyji4E4iwpvSbrt'   # Block.one
                ]
            },
            'investment_funds': {
                'type': 'fund',
                'addresses': [
                    '385cR5DM96n1HvBDMzLHPYcw89fZAXULJP',  # Grayscale
                    '3FHNBLobJnbCTFTVakh5TXmEneyf5PT61B',  # Purpose ETF
                    'bc1qr4dl5wa7kl8yu792dceg9z5knl2gkn220lk7dv',  # Pantera
                    'bc1q9d8u7hf4k7vp9jg586w8ff838z4z7rcyzktw7t'   # Polychain
                ]
            },
            'doj_seized': {
                'type': 'seized',
                'addresses': [
                    'bc1q5shae2q9et4k2824ts8vqu0zwwlue4glrhr0qx',  # Silk Road
                    'bc1qa5wkgaew2dkv56kfvj49j0av5nml45x9ek9hz6',  # DOJ 2020
                    '1Cu2kh4M1ZXJNzjzBqoFs4Om3PFD6zQV2N'           # FTX Related
                ]
            }
        })

        # Add hacker groups and stolen fund addresses
        self.known_addresses.update({
            'lazarus_group': {
                'type': 'hacker',
                'addresses': [
                    'bc1qw7yazn56qd66xz28r7g85uh5xzj0qwzex2crying',  # Bybit hack 2024
                    'bc1q53fwz5kxkv4r7s7pjzxvfnkut5hkj7sc8kl0m2',    # ETH Bridge hack
                    'bc1qjnnfk5xa54n9q4s44vhg8dhp4zg4jmhspwqkyw',    # Atomic wallet hack
                    'bc1q2qd7ke58vz5m8wkte5p4rh28dvlhvx6f4lmgsr',    # Stake.com hack
                    '3DXQAkBp1DLwu5QiFsE7Y6zWzr3DmHLcEk',            # Known mixer address
                    'bc1qkcrnwupjg8xts39qxz5kpxmvp33qle7qkxepqr',    # Known Lazarus wallet
                    # Add more addresses as they're identified
                ]
            },
            'stolen_funds': {
                'type': 'compromised',
                'addresses': [
                    'bc1q0pzqz5q5gmkj77zxrj0m8klkv2rsg8kn3zxwrg',  # Bybit stolen funds
                    'bc1q3kqr4ej7qz5mpvs8ex2kl9yvg4gku8h5k8nstx',  # Bridge exploit
                    # Add more as identified
                ]
            }
        })

        # Add Lazarus-specific patterns to exchange_patterns
        self.exchange_patterns.update({
            "Lazarus": {
                "prefixes": ["bc1q", "3"],
                "patterns": [
                    r"^bc1q[0-9a-zA-Z]{38,42}$",
                    r"^3[a-zA-Z0-9]{33}$"
                ],
                "known_ranges": ["bc1q", "3"]
            }
        })


    def get_latest_block(self):
        """Get the latest block hash and ensure we don't process duplicates"""
        try:
            response = requests.get(f"{self.base_url}/latestblock")
            block_data = response.json()
            current_height = block_data['height']
            current_hash = block_data['hash']
            
            # If this is our first block, initialize
            if self.last_block_height is None:
                self.last_block_height = current_height
                return current_hash
                
            # If we've seen this block already, return None
            if current_hash in self.processed_blocks:
                return None
                
            # If this is a new block
            if current_height > self.last_block_height:
                self.last_block_height = current_height
                # Keep track of last 1000 blocks to manage memory
                if len(self.processed_blocks) > 1000:
                    self.processed_blocks.clear()
                self.processed_blocks.add(current_hash)
                print(f"\nNew Block: {current_height} | Hash: {current_hash[:8]}...")
                return current_hash
                
            return None
            
        except Exception as e:
            print(f"Error getting latest block: {e}")
            return None

    def get_block_transactions(self, block_hash):
        """Get all transactions in a block"""
        try:
            response = requests.get(f"{self.base_url}/rawblock/{block_hash}")
            return response.json()['tx']
        except Exception as e:
            print(f"Error getting block transactions: {e}")
            return []

    def get_address_label(self, address):
        """Get the entity label for an address"""
        for entity, info in self.known_addresses.items():
            if address in info['addresses']:
                return f"({entity.upper()} {info['type']})"
        return ""

    def update_address_stats(self, address, is_sender, btc_amount, timestamp):
        """Update statistics for an address"""
        stats = self.address_stats[address]
        if is_sender:
            stats['sent_count'] += 1
            stats['total_sent'] += btc_amount
        else:
            stats['received_count'] += 1
            stats['total_received'] += btc_amount
        stats['last_seen'] = timestamp

    def get_address_summary(self, address):
        """Get formatted summary of address activity"""
        stats = self.address_stats[address]
        entity_label = self.get_address_label(address)
        return (f"{entity_label} "
                f"[↑{stats['sent_count']}|↓{stats['received_count']}] "
                f"Total: ↑{stats['total_sent']:.2f}|↓{stats['total_received']:.2f} BTC")

    def identify_address(self, address):
        """Enhanced address identification with pattern matching"""
        # First check known addresses
        for entity, info in self.known_addresses.items():
            if address in info['addresses']:
                return {
                    'name': entity,
                    'type': info['type']
                }

        # Then check patterns
        for exchange, patterns in self.exchange_patterns.items():
            # Check prefixes
            if any(address.startswith(prefix) for prefix in patterns['prefixes']):
                return {'name': exchange, 'type': 'exchange'}
            
            # Check regex patterns
            if any(re.match(pattern, address) for pattern in patterns['patterns']):
                return {'name': exchange, 'type': 'exchange'}
            
            # Check known ranges
            if any(address.startswith(range_prefix) for range_prefix in patterns['known_ranges']):
                return {'name': exchange, 'type': 'exchange'}
                
        return None

    def determine_transaction_type(self, sender, receiver):
        """Determine transaction type and involved entities"""
        sender_info = self.identify_address(sender)
        receiver_info = self.identify_address(receiver)
        
        if sender_info and receiver_info:
            return {
                'type': 'INTERNAL TRANSFER',
                'from_entity': sender_info,
                'to_entity': receiver_info
            }
        elif sender_info:
            return {
                'type': 'WITHDRAWAL',
                'from_entity': sender_info,
                'to_entity': None
            }
        elif receiver_info:
            return {
                'type': 'DEPOSIT',
                'from_entity': None,
                'to_entity': receiver_info
            }
        else:
            return {
                'type': 'UNKNOWN TRANSFER',
                'from_entity': None,
                'to_entity': None
            }

    def process_transaction(self, tx):
        """Process a single transaction and return if it meets criteria"""
        # Calculate total input value
        input_value = sum(inp.get('prev_out', {}).get('value', 0) for inp in tx.get('inputs', []))
        btc_value = input_value / self.satoshi_to_btc
        
        # Only process transactions over minimum BTC threshold
        if btc_value < self.min_btc:
            return None
            
        # Get the primary sender (first input address)
        sender = tx.get('inputs', [{}])[0].get('prev_out', {}).get('addr', 'Unknown')
        
        # Get the primary receiver (first output address)
        receiver = tx.get('out', [{}])[0].get('addr', 'Unknown')
        
        timestamp = datetime.fromtimestamp(tx.get('time', 0))
        
        # Update address statistics
        self.update_address_stats(sender, True, btc_value, timestamp)
        self.update_address_stats(receiver, False, btc_value, timestamp)
        
        # Get transaction type and entities involved
        tx_info = self.determine_transaction_type(sender, receiver)
        
        # Calculate fee
        output_value = sum(out.get('value', 0) for out in tx.get('out', []))
        fee = (input_value - output_value) / self.satoshi_to_btc
        
        return {
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'transaction_hash': tx.get('hash', 'Unknown'),
            'sender': sender,
            'receiver': receiver,
            'btc_volume': round(btc_value, 4),
            'fee_btc': round(fee, 8),
            'tx_type': tx_info['type'],
            'from_entity': tx_info['from_entity'],
            'to_entity': tx_info['to_entity']
        }

    def print_transaction(self, tx):
        """Print transaction in formatted alert style"""
        # Determine number of alarm emojis based on BTC volume
        alarm_count = min(8, max(1, int(tx['btc_volume'] / 500)))  # 1 emoji per 250 BTC, max 8
        alarms = "🚨" * alarm_count
        
        # Format BTC amount with comma for thousands
        btc_amount = f"{tx['btc_volume']:,.0f}"
        
        # Calculate USD value (mock price of $96,073.862 per BTC)
        usd_value = tx['btc_volume'] * 96073.862
        usd_formatted = f"{usd_value:,.0f}"
        
        # Format fee in sats and USD
        fee_sats = tx['fee_btc'] * 100000000  # Convert BTC to sats
        fee_usd = tx['fee_btc'] * 96073.862
        
        # Get entity names
        from_entity = tx['from_entity']['name'].title() if tx['from_entity'] else "unknown"
        to_entity = "unknown new wallet" if not tx['to_entity'] else tx['to_entity']['name'].title()
        
        # Build the message
        message = (
            f"{alarms}{btc_amount} #BTC ({usd_formatted} USD) transferred "
            f"({tx['tx_type'].title()}) from #{from_entity} to #{to_entity} "
            f"for {fee_sats:.2f} sats (${fee_usd:.0f}) fees"
        )
        
        print(message)

    def monitor_transactions(self):
        """Main method to track whale transactions"""
        print(f"Tracking Bitcoin transactions over {self.min_btc} BTC...")
        print("Waiting for new blocks...")
        
        while True:
            try:
                block_hash = self.get_latest_block()
                
                if block_hash:
                    transactions = self.get_block_transactions(block_hash)
                    processed_count = 0
                    whale_count = 0
                    
                    for tx in transactions:
                        processed_count += 1
                        whale_tx = self.process_transaction(tx)
                        if whale_tx:
                            whale_count += 1
                            self.print_transaction(whale_tx)
                    
                    print(f"Processed {processed_count} transactions, found {whale_count} whale movements")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(30)

if __name__ == "__main__":
    tracker = BitcoinWhaleTracker(min_btc=500)  # Changed from 100 to 500
    tracker.monitor_transactions()  # Changed from track_whale_transactions to monitor_transactions