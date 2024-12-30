# AXS Auto Re-Stake Script  
✨ **Automate your AXS staking rewards with ease and efficiency!** ✨  

This script provides a **comprehensive and integrated solution** for performing automatic AXS re-stakes. It’s perfect for maximizing returns without manual monitoring. With native integration to free services like **Render** and blockchain tools like **Moralis**, you can set it up and let it run 24/7 without any additional costs!

---

## Requirements  

### ➡️ Moralis Account (Free)  
A **free Moralis account** is required to connect to the **Ronin blockchain** and calculate re-stake intervals automatically. You can sign up at [Moralis](https://admin.moralis.com/) and obtain an API key.

### ➡️ Render WebService Integration (Free)  
The script is specifically adapted for **Render’s WebService**, enabling you to run it in a **free tier**. This eliminates the need for keeping your computer on or paying for hosting. Render ensures the script runs smoothly as a complete and cost-free AXS re-stake system.  
Sign up for Render at [Render](https://render.com/).

---

## Features  

- ✅ **Automatic Re-Stake**: Monitors your staking rewards and reinvests them automatically.  
- ✅ **Free Hosting:** Leverage Render WebService for 24/7 operations without any charges.  
- ✅ **Simple Configuration:** Only the `config.ini` file needs to be edited.  
- ✅ **Blockchain Integration:** Uses Moralis API for seamless Ronin blockchain access.  
- ✅ **Logs & Monitoring:** Detailed activity logs with modular configurations.  
- ✅ **Secure:** Protects your private keys with proper handling.  
- ✅ **Customizable:** Fully configurable for intervals, time zones, and more.  

---

## Installation  

1. **Clone the Repository:**  
   ```bash
   git clone https://github.com/williamlala/axs-auto-restaking.git
   cd axs-auto-restaking

2. **Install Dependencies:**  
   ```bash
   pip install -r requirements.txt

3. **Edit the `config.ini` File:**  
Open `config.ini` and configure the following parameters:

#### `[WALLET]`
- **STAKE_ACCOUNT_ADDRESS:** Your Ronin wallet address.  
- **STAKE_PK:** Your Ronin private key (**keep it secure and never share it**).  

#### `[RENDER]`
- **USE_RENDER_WEB_SERVICE:**  
  - Set to **YES** if using Render WebService.  
  - Set to **NO** if you'll run the script on your own computer.  
- **RENDER_PORT:** Set the port to **8080** or another value.  

#### `[MORALIS]`
- **MORALIS_API_KEY:** Add your API key from Moralis.  
- **MORALIS_BASE_URL:** Base URL for the Moralis API.  
  Example: `https://deep-index.moralis.io/api/v2`.  
- **MORALIS_CHAIN:** Name of the blockchain used in Moralis.  
  Example: `ronin`.  

#### `[RONIN]`
- **RONIN_RPC_URL:** RPC URL of the Ronin blockchain (connection with the blockchain).  
  Example: `https://api.roninchain.com/rpc`.  
- **CHAIN_ID:** Ronin network identifier, used in transactions.  
  Example: `2020`.  
- **GAS_LIMIT:** Maximum gas amount the transaction can consume.  
  Example: `371098`.  
- **GAS_PRICE_MULTIPLIER:** Multiplier to calculate the gas price (e.g., 1.1 for a 10% increase to avoid transaction errors).  
  Example: `1.1`.  
- **CONTRACT_ADDRESS:** Staking contract address for AXS.  
  Example: `0x05b0bb3c1c320b280501b86706c3551995bc8571`.  
- **ABI_FILE:** JSON file name containing the contract's ABI.  
  Example: `axs_staking_abi.json`.  

#### `[DEFAULT]`
- **LOG_FILE:** Log file name for storing system logs.  
  Example: `main_log.log`.  
- **LOG_DATE_FORMAT:** Date format used in logs (1 for mm/dd/yyyy, 2 for dd/mm/yyyy).  
  Example: `1`.  
- **LOG_MAX_SIZE_MB:** Maximum log size in MB before generating a new log file. The system will always keep 2 logs, replacing the oldest one when necessary.  
  Example: `2`.  
- **UTC_FOR_LAST_STAKING:** UTC offset for the "Last successful staking" time (e.g., 0 for UTC, +3 for UTC+3, -3 for UTC-3).  
  Example: `0`.  
- **RECHECK_DELAY_SECONDS:** Interval in seconds to check if it's time to perform the re-stake.  
  Example: `5`.  
- **FAILED_RESTAKE_RETRY_SECONDS:** Wait time in seconds before retrying in case of a re-stake failure.  
  Example: `60`.  
- **SUCCESSFUL_RESTAKE_DELAY_HOURS:** Default interval in hours between successful re-stakes.  
  Example: `24`.  
- **SUCCESSFUL_RESTAKE_EXTRA_SECONDS:** Extra time in seconds to avoid re-stakes before the minimum interval.  
  Example: `1`.  
- **TRANSACTION_TIMEOUT_SECONDS:** Timeout in seconds to check the status of a transaction.  
  Example: `300`.  

---

🌟 **Support the Project!** 🌟  
If you find this project useful and would like to contribute, here are the wallet addresses where you can show your support. Every contribution helps keep this initiative running! Thank you for your generosity! ❤️  

💰 **Solana (SOL):**
```plaintext
7FSz5e9VVSGNREHfEu8gbmaQLEN1brQEzfYxTJdecfX2
```
💰 **Bitcoin (BTC):**
```plaintext  
bc1q680dmh3wskx72umpqk7m2wkzjsv6n53pz0qsq8
```
💰 **Ethereum (ETH):**
```plaintext  
0xA77aB3da49035c37Ff0f5FFB819721f6b51838Db
```
💰 **Binance Smart Chain (BSC):**
```plaintext  
0xA77aB3da49035c37Ff0f5FFB819721f6b51838Db
```
🎉 **Thank you for your support! Together, we build something amazing. 🚀**
