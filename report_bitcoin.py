# -*- coding: UTF-8 -*-
import requests
import time
import os
from datetime import datetime
from collections import defaultdict

class BitcoinWhaleTracker:
    def __init__(self, min_btc=100):
        self.base_url = "https://blockchain.info"
        self.min_btc = min_btc
        self.satoshi_to_btc = 100000000
        self.processed_blocks = set()  # Track processed blocks
        self.last_block_height = None  # Track last block height
        
        # Create svg output directory if it doesn't exist
        self.svg_dir = "whale_transactions_svg"
        if not os.path.exists(self.svg_dir):
            os.makedirs(self.svg_dir)
        
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
        
    def generate_transaction_svg(self, tx):
        """Generate SVG visualization for a transaction"""
        svg_template = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400">
    <!-- Background -->
    <rect width="800" height="400" fill="#f9fafb"/>
    
    <!-- Transaction Type and Amount -->
    <text x="400" y="50" text-anchor="middle" font-size="24" font-weight="bold">{tx['tx_type']}</text>
    <text x="400" y="80" text-anchor="middle" font-size="20" fill="#4b5563">{tx['btc_volume']} BTC</text>
    
    <!-- From Box -->
    <rect x="50" y="120" width="300" height="160" fill="white" stroke="black" stroke-width="2" rx="8"/>
    <text x="60" y="150" font-size="14">From: {tx['sender'][:20]}...</text>
    <text x="60" y="170" font-size="14">{self.get_address_label(tx['sender'])}</text>
    <text x="60" y="200" font-size="12" fill="#4b5563" font-family="monospace">
        [↑{self.address_stats[tx['sender']]['sent_count']}|↓{self.address_stats[tx['sender']]['received_count']}]
    </text>
    <text x="60" y="220" font-size="12" fill="#4b5563" font-family="monospace">
        Total: ↑{self.address_stats[tx['sender']]['total_sent']:.2f}|↓{self.address_stats[tx['sender']]['total_received']:.2f} BTC
    </text>
    
    <!-- Arrow -->
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
        </marker>
    </defs>
    <line x1="350" y1="200" x2="438" y2="200" stroke="black" stroke-width="2" marker-end="url(#arrowhead)"/>
    
    <!-- To Box -->
    <rect x="450" y="120" width="300" height="160" fill="white" stroke="black" stroke-width="2" rx="8"/>
    <text x="460" y="150" font-size="14">To: {tx['receiver'][:20]}...</text>
    <text x="460" y="170" font-size="14">{self.get_address_label(tx['receiver'])}</text>
    <text x="460" y="200" font-size="12" fill="#4b5563" font-family="monospace">
        [↑{self.address_stats[tx['receiver']]['sent_count']}|↓{self.address_stats[tx['receiver']]['received_count']}]
    </text>
    <text x="460" y="220" font-size="12" fill="#4b5563" font-family="monospace">
        Total: ↑{self.address_stats[tx['receiver']]['total_sent']:.2f}|↓{self.address_stats[tx['receiver']]['total_received']:.2f} BTC
    </text>
    
    <!-- Transaction Details -->
    <text x="400" y="350" text-anchor="middle" font-size="12" fill="#4b5563">
        Hash: {tx['transaction_hash'][:20]}... | Fee: {tx['fee_btc']} BTC | {tx['timestamp']}
    </text>
</svg>'''
        
        return svg_template

    def save_transaction_svg(self, tx):
        """Save transaction visualization as SVG file"""
        svg_content = self.generate_transaction_svg(tx)
        filename = f"{self.svg_dir}/transaction_{tx['timestamp'].replace(' ', '_').replace(':', '-')}_{tx['transaction_hash'][:8]}.svg"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return filename

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
        """Identify the owner and type of an address"""
        for entity, info in self.known_addresses.items():
            if address in info['addresses']:
                return {
                    'name': entity,
                    'type': info['type']
                }
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
        
        processed_tx = {
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

        # Save SVG visualization
        svg_file = self.save_transaction_svg(processed_tx)
        print(f"SVG visualization saved: {svg_file}")

        return processed_tx

    def print_transaction(self, tx):
        """Print transaction in formatted alert style"""
        color_code = {
            'DEPOSIT': '\033[92m',          # Green
            'WITHDRAWAL': '\033[91m',       # Red
            'INTERNAL TRANSFER': '\033[93m', # Yellow
            'UNKNOWN TRANSFER': '\033[94m'   # Blue
        }.get(tx['tx_type'], '\033[94m')
        
        print("\n" + "=" * 120)
        print(f"{color_code}🚨 Bitcoin {tx['tx_type']} Alert! {tx['timestamp']}")
        
        sender_label = self.get_address_label(tx['sender'])
        receiver_label = self.get_address_label(tx['receiver'])
        
        print(f"Hash: {tx['transaction_hash']}")
        print(f"{tx['btc_volume']} BTC", end='')
        print(f"        Fee: {tx['fee_btc']} BTC\033[0m")
        
        print(f"From: {tx['sender']} {sender_label}")
        print(f"    History: {self.get_address_summary(tx['sender'])}")
        print(f"To: {tx['receiver']} {receiver_label}")
        print(f"    History: {self.get_address_summary(tx['receiver'])}")
        
        print("=" * 120 + "\n")

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
    tracker = BitcoinWhaleTracker(min_btc=100)  # Track transactions over 100 BTC
    tracker.monitor_transactions()  # Changed from track_whale_transactions to monitor_transactions