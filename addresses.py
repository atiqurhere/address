import pandas as pd
import requests
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------- RPC endpoints --------
RPC = {
    "ethereum": "https://ethereum.publicnode.com",
    "base": "https://base.publicnode.com",
    "bsc": "https://bsc-dataseed1.binance.org"
}
RPC_BACKUP = {
    "ethereum": "https://rpc.ankr.com/eth",
    "base": "https://mainnet.base.org",
    "bsc": "https://rpc.ankr.com/bsc"
}

# -------- Function to get balance --------
def get_eth_balance(primary_url, backup_url, address):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    try:
        r = requests.post(primary_url, json=payload, timeout=10)
        r.raise_for_status()
        result = r.json().get("result")
    except Exception:
        try:
            r = requests.post(backup_url, json=payload, timeout=10)
            r.raise_for_status()
            result = r.json().get("result")
        except Exception:
            return None

    if result:
        return int(result, 16) / 1e18  # Convert wei → ETH
    return None

# -------- Worker function --------
def check_address(address):
    try:
        eth = get_eth_balance(RPC["ethereum"], RPC_BACKUP["ethereum"], address)
        base = get_eth_balance(RPC["base"], RPC_BACKUP["base"], address)
        bsc = get_eth_balance(RPC["bsc"], RPC_BACKUP["bsc"], address)
    except Exception:
        eth, base, bsc = None, None, None
    return [address, eth, base, bsc]

# -------- Stop signal --------
stop_flag = False
def cancel_listener():
    global stop_flag
    while True:
        command = input().strip().lower()
        if command == "cancel":
            stop_flag = True
            print("\n🛑 Cancel command received! Finishing current batch...")
            break

# -------- Main process --------
def process_csv(input_file="addresses.csv", start_row=1, end_row=None, workers=10):
    df = pd.read_csv(input_file, header=None, names=["data"])
    df["address"] = df["data"].apply(lambda x: json.loads(x)["address"])

    total_rows = len(df)
    if end_row is None or end_row > total_rows:
        end_row = total_rows

    df = df.iloc[start_row-1:end_row]  # 1-based index for user input

    output_file = f"balances_{start_row}-{end_row}.xlsx"

    print(f"📂 Checking addresses from row {start_row} to {end_row}")
    print(f"💾 Results will be saved to {output_file}\n")

    out_df = pd.DataFrame(columns=["address", "Ethereum_ETH", "Base_ETH", "BSC_ETH"])
    results = []
    checked_count = 0
    total_addresses = len(df)

    # Start cancel listener thread
    listener_thread = threading.Thread(target=cancel_listener, daemon=True)
    listener_thread.start()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_address = {executor.submit(check_address, addr): addr for addr in df["address"]}

        for future in as_completed(future_to_address):
            if stop_flag:
                break

            result = future.result()
            results.append(result)
            checked_count += 1

            remaining = total_addresses - checked_count
            print(f"✅ Checked {checked_count}/{total_addresses} | Remaining: {remaining}", end="\r")

            if len(results) >= 100 or checked_count == total_addresses:
                temp_df = pd.DataFrame(results, columns=["address", "Ethereum_ETH", "Base_ETH", "BSC_ETH"])

                for col in ["Ethereum_ETH", "Base_ETH", "BSC_ETH"]:
                    temp_df[col] = temp_df[col].apply(lambda x: f"{x:.18f}" if x is not None else "")

                out_df = pd.concat([out_df, temp_df], ignore_index=True)
                out_df.to_excel(output_file, index=False)
                results = []

    print(f"\n\n📁 Saved progress to {output_file}")
    if stop_flag:
        print("🚫 Process stopped by user.")
    else:
        print("🎉 Finished all addresses in selected range!")

# -------- Run interaction loop --------
if __name__ == "__main__":
    while True:
        try:
            start = int(input("Enter starting row number: "))
            end = input("Enter ending row number (or press Enter for all): ")
            end = int(end) if end.strip() else None
            process_csv(start_row=start, end_row=end, workers=15)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user.")
        except Exception as e:
            print(f"⚠️ Error: {e}")

        again = input("\nDo you want to start again? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("👋 Exiting program.")
            break
