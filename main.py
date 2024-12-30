# Used Python version 3.12.4
# pip install web3==7.6.1 requests==2.31.0 flask==3.0.3 tqdm==4.66.4

import os
import sys
import logging
import json
import time
import subprocess
from datetime import datetime, timedelta, timezone
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import requests
import configparser
from logging.handlers import RotatingFileHandler
from tqdm import tqdm
from flask import Flask

# Change the current directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load configurations from config.ini file
config = configparser.ConfigParser()
config.read(os.path.join(script_dir, 'config.ini'))

# Access configurations
LOG_FILE = config['DEFAULT']['LOG_FILE']
LOG_DATE_FORMAT = int(config['DEFAULT']['LOG_DATE_FORMAT'])
LOG_MAX_SIZE_MB = int(config['DEFAULT']['LOG_MAX_SIZE_MB']) * 1024 * 1024  # Convert MB to bytes
LOG_MAX_SIZE_BYTES = LOG_MAX_SIZE_MB * 1024 * 1024

USE_RENDER_WEB_SERVICE = config['RENDER'].get('USE_RENDER_WEB_SERVICE', 'NO').upper() == 'YES'

UTC_FOR_LAST_STAKING = int(config['DEFAULT']['UTC_FOR_LAST_STAKING'])
SUCCESSFUL_RESTAKE_DELAY_HOURS = int(config['DEFAULT']['SUCCESSFUL_RESTAKE_DELAY_HOURS'])
SUCCESSFUL_RESTAKE_EXTRA_SECONDS = int(config['DEFAULT']['SUCCESSFUL_RESTAKE_EXTRA_SECONDS'])
FAILED_RESTAKE_RETRY_SECONDS = int(config['DEFAULT']['FAILED_RESTAKE_RETRY_SECONDS'])
RECHECK_DELAY_SECONDS = int(config['DEFAULT']['RECHECK_DELAY_SECONDS'])
TRANSACTION_TIMEOUT_SECONDS = int(config['DEFAULT']['TRANSACTION_TIMEOUT_SECONDS'])

MORALIS_API_KEY = config['MORALIS']['MORALIS_API_KEY']
MORALIS_BASE_URL = config['MORALIS']['MORALIS_BASE_URL']
MORALIS_CHAIN = config['MORALIS']['MORALIS_CHAIN']

RONIN_RPC_URL = config['RONIN']['RONIN_RPC_URL']
CHAIN_ID = int(config['RONIN']['CHAIN_ID'])
GAS_LIMIT = int(config['RONIN']['GAS_LIMIT'])
GAS_PRICE_MULTIPLIER = float(config['RONIN']['GAS_PRICE_MULTIPLIER'])
CONTRACT_ADDRESS = config['RONIN']['CONTRACT_ADDRESS']
ABI_FILE = config['RONIN']['ABI_FILE']

STAKE_ACCOUNT_ADDRESS = config['WALLET']['STAKE_ACCOUNT_ADDRESS']
STAKE_PK = config['WALLET']['STAKE_PK']

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(RONIN_RPC_URL))
web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Load the contract's ABI
with open(ABI_FILE) as f:
    restake_abi = json.load(f)

contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=restake_abi)

# Choose the date format based on LOG_DATE_FORMAT
if LOG_DATE_FORMAT == 1:
    DATE_FORMAT = '%m/%d/%Y %H:%M:%S'  # mm/dd/yyyy
elif LOG_DATE_FORMAT == 2:
    DATE_FORMAT = '%d/%m/%Y %H:%M:%S'  # dd/mm/yyyy
else:
    raise ValueError("LOG_DATE_FORMAT must be 1 (mm/dd/yyyy) or 2 (dd/mm/yyyy)")

# Define the timezone based on UTC_FOR_LAST_STAKING
utc_offset = timezone(timedelta(hours=UTC_FOR_LAST_STAKING))

class CustomLogger:
    def __init__(self, logger):
        self.logger = logger

    def info(self, message, save_to_file=True):
        """Displays messages with control over saving to a file."""
        if save_to_file:
            self.logger.info(message)
        else:
            # Temporarily disable file logging for this message
            for handler in self.logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.setLevel(logging.CRITICAL)  # Temporarily disable
            self.logger.info(message)
            for handler in self.logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    handler.setLevel(logging.INFO)  # Restore log level

# Replace the default logger with CustomLogger
custom_logger = CustomLogger(logging.getLogger())

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt=DATE_FORMAT,
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=LOG_MAX_SIZE_BYTES, backupCount=2),  # Rotating logs with configured size
        logging.StreamHandler()  # Logs to console (stdout)
    ]
)

if USE_RENDER_WEB_SERVICE:
    logging.info("Starting the Render Web Service")
    subprocess.Popen(['python', os.path.join(script_dir, 'render_usage.py')])

# Initial message to indicate the system has started
logging.info("The AXS re-stake system has started.")

def format_datetime(dt):
    """Formats datetime based on LOG_DATE_FORMAT and UTC_FOR_LAST_STAKING."""
    if LOG_DATE_FORMAT == 1:
        date_format = '%m/%d/%Y %H:%M:%S'  # mm/dd/yyyy
    elif LOG_DATE_FORMAT == 2:
        date_format = '%d/%m/%Y %H:%M:%S'  # dd/mm/yyyy
    else:
        date_format = '%Y-%m-%d %H:%M:%S'  # Default

    # Ensure the original datetime is in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    adjusted_dt = dt.astimezone(utc_offset)
    formatted_datetime = adjusted_dt.strftime(date_format)
    return formatted_datetime

def countdown(seconds):
    """Countdown timer."""
    if USE_RENDER_WEB_SERVICE:
        for remaining in range(seconds, 0, -1):
            # Log only to console (do not save to file)
            custom_logger.info(f"Retrying in {remaining} seconds...", save_to_file=False)
            time.sleep(1)
    else:
        with tqdm(total=seconds, bar_format="{desc}") as pbar:
            for remaining in range(seconds, 0, -1):
                pbar.set_description(f"Retrying in {remaining} seconds...")
                time.sleep(1)
                pbar.update(1)

def countdown_to_next_restake(seconds):
    """Displays a countdown timer for the next re-staking."""
    if USE_RENDER_WEB_SERVICE:
        for remaining in range(seconds, 0, -1):
            hours, remainder = divmod(remaining, 3600)
            minutes, seconds = divmod(remainder, 60)
            # Log only to console (do not save to file)
            custom_logger.info(
                f"Time remaining for the next re-staking: {hours:02}h:{minutes:02}m:{seconds:02}s",
                save_to_file=False,
            )
            time.sleep(1)
    else:
        with tqdm(total=seconds, bar_format="{desc}") as pbar:
            for remaining in range(seconds, 0, -1):
                hours, remainder = divmod(remaining, 3600)
                minutes, seconds = divmod(remainder, 60)
                pbar.set_description(
                    f"Time remaining for the next re-staking: {hours:02}h:{minutes:02}m:{seconds:02}s"
                )
                time.sleep(1)
                pbar.update(1)

def fetch_last_successful_restake():
    """Fetches the last successful re-stake transaction."""
    try:
        url = f"{MORALIS_BASE_URL}/{STAKE_ACCOUNT_ADDRESS}"
        params = {"chain": MORALIS_CHAIN}
        headers = {"accept": "application/json", "X-API-Key": MORALIS_API_KEY}
        cursor = None

        while True:
            if cursor:
                params["cursor"] = cursor

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            transactions = data.get("result", [])

            for tx in transactions:
                if tx.get("receipt_status") == "1" and tx.get("input", "").startswith("0x3d8527ba"):
                    timestamp = datetime.strptime(tx["block_timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    return timestamp

            cursor = data.get("cursor")
            if not cursor:
                break

        logging.info("No successful re-stake transactions found.")
        return None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error while fetching transactions: {http_err}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None

def perform_restake():
    """Executes the re-stake process."""
    try:
        account_address = Web3.to_checksum_address(STAKE_ACCOUNT_ADDRESS)
        nonce = web3.eth.get_transaction_count(account_address)
        dynamic_gas_price = web3.eth.gas_price
        gas_price = int(dynamic_gas_price * GAS_PRICE_MULTIPLIER)

        logging.info(f"Calculated Gas Price: {gas_price} wei")
        transfer_txn = contract.functions.restakeRewards().build_transaction({
            'chainId': CHAIN_ID,
            'gas': GAS_LIMIT,
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        signed_txn = web3.eth.account.sign_transaction(
            transfer_txn,
            private_key=bytearray.fromhex(STAKE_PK.replace("0x", ""))
        )

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return tx_hash.hex()
    except Exception as e:
        logging.error(f"Error executing re-stake: {e}")
        return None

def verify_transaction(tx_hash):
    """Verifies the status of the re-stake transaction."""
    try:
        logging.info(f"Verifying re-stake transaction with hash: {tx_hash}")
        for _ in range(TRANSACTION_TIMEOUT_SECONDS):
            receipt = web3.eth.get_transaction_receipt(tx_hash)
            if receipt and receipt.status == 1:
                logging.info("Re-stake successfully completed!")
                return True
            countdown(TRANSACTION_TIMEOUT_SECONDS)
            
        logging.error("Re-stake transaction failed: timeout reached.")
        return False
    except Exception as e:
        logging.error(f"Error verifying transaction: {e}")
        return False

def main():
    logging.info("Checking the last successful transaction to calculate the next re-stake time...")
    last_successful_time = fetch_last_successful_restake()

    if last_successful_time:
        logging.info(f"Last successful staking date: {format_datetime(last_successful_time)} (UTC{UTC_FOR_LAST_STAKING:+d})")
        next_restake_time = last_successful_time + timedelta(
            hours=SUCCESSFUL_RESTAKE_DELAY_HOURS,
            seconds=SUCCESSFUL_RESTAKE_EXTRA_SECONDS
        )
        logging.info(f"Next re-stake scheduled for: {format_datetime(next_restake_time)} (UTC{UTC_FOR_LAST_STAKING:+d})")
    else:
        logging.info("No previous transactions found. Starting staking process...")
        next_restake_time = datetime.now()
        formatted_next_restake_time = next_restake_time.strftime(DATE_FORMAT)
        logging.info(f"Next re-stake set to now: {formatted_next_restake_time} (UTC{UTC_FOR_LAST_STAKING:+d})")

    while True:
        current_time = datetime.now()

        if current_time >= next_restake_time:
            logging.info("Attempting to perform re-stake...")
            tx_hash = perform_restake()

            if tx_hash:
                logging.info(f"Re-stake transaction sent. Hash: {tx_hash}")
                if not verify_transaction(tx_hash):
                    logging.warning("Re-stake failed.")
                    countdown(FAILED_RESTAKE_RETRY_SECONDS)
                    last_successful_time = fetch_last_successful_restake()
                    if last_successful_time:
                        logging.info(f"Last successful staking found on blockchain: {format_datetime(last_successful_time)} (UTC{UTC_FOR_LAST_STAKING:+d})")
                        next_restake_time = last_successful_time + timedelta(
                            hours=SUCCESSFUL_RESTAKE_DELAY_HOURS,
                            seconds=SUCCESSFUL_RESTAKE_EXTRA_SECONDS
                        )
                        logging.info(f"Next re-stake scheduled for: {format_datetime(next_restake_time)} (UTC{UTC_FOR_LAST_STAKING:+d})")
            else:
                logging.error("Error sending re-stake.")
                countdown(FAILED_RESTAKE_RETRY_SECONDS)
        else:
            remaining_time = int((next_restake_time - datetime.now()).total_seconds())
            countdown_to_next_restake(remaining_time)

if __name__ == "__main__":
    main()