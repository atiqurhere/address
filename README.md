# 🧾 Wallet Balance Checker

<p align="center">
  <b>Check Ethereum, Base & BSC wallet balances easily with row control and cancel command.</b><br>
  <i>Choose your range. Cancel anytime. Save progress automatically.</i>
</p>

---

## ⚙️ Features

- ✅ Supports **Ethereum**, **Base**, and **BSC** networks  
- ✅ Fetches **BNB** and **ETH-pegged tokens (WETH, Binance-Peg ETH)** separately on BSC  
- ✅ Choose any **start** and **end** row  
- ✅ Type `cancel` to stop safely at any time  
- ✅ Auto-saves every 50 results (batch saving)  
- ✅ File names include row range (e.g., `balances_50-1000.csv`)  
- ✅ Resume from existing CSV files  
- ✅ Option to restart or exit after stopping  

---

## 📦 Requirements

Make sure you have **Python 3.8+** installed.  

Install required packages:

```bash
pip install requests

> Note: pandas is not required for Termux or lightweight environments.




---

📁 Input File

Your input file must be named addresses.csv and placed in the same folder as the script.

Each line should contain a JSON object with an address:

{"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}
{"address": "0x00000000219ab540356cBB839Cbe05303d7705Fa"}


---

🚀 How to Run

1. Open terminal in the script directory


2. Run:



python balance_checker.py

3. Enter starting row (e.g., 50)


4. Enter ending row (or press Enter for all rows)


5. Watch live progress as balances are fetched




---

🛑 Cancel Command

At any time, type:

cancel

The script will safely stop after the current batch and save your progress automatically.


---

💾 Output

Results are saved automatically as:

balances_50-1000.csv

Each file includes the following columns:

address	Ethereum_ETH	Base_ETH	BSC_BNB	BSC_BinancePegETH	BSC_WETH

0x...	0.000000000000000123	0.000000000000000000	0.000000000000045678	0.000000000000000000	0.000000000000000012


All balances are stored with 18 decimal precision

Each BSC ETH-pegged token has its own column



---

🔁 Restart or Exit

After completion or cancellation, you'll see:

Do you want to start again? (yes/no)

Type yes to start another row range

Type no to exit the program



---

🧠 Notes

Safe to re-run for different row ranges

Avoid running multiple instances simultaneously

Progress auto-saves every 50 results

Thread-safe CSV writing ensures correct column alignment



---

🖼 Workflow Diagram

Input CSV -> Fetch Balances (Ethereum, Base, BSC) -> Fetch BSC ETH Tokens -> Append Results -> Save CSV (Thread-Safe) -> Auto-Resume if interrupted


---

<h3 align="center">👨‍💻 Author: Ahmed Sumon</h3>
<p align="center">
  <b>Version:</b> 2.1<br>
  <b>License:</b> Free for personal and educational use
</p>
```