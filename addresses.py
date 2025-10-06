import requests
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

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

# -------- ETH-pegged tokens on BSC (name + address) --------
BSC_ETH_TOKENS = [
    ("BSC_BinancePegETH", "0x2170ed0880ac9a755fd29b2688956bd959f933f8"),
    ("BSC_WETH", "0x8babbb98678facc7342735486c851abd7a0d17ca")
]

# -------- Stop signal --------
stop_flag = False
write_lock = threading.Lock()

def cancel_listener():
    global stop_flag
    while True:
        command = input().strip().lower()
        if command == "cancel":
            stop_flag = True
            print("\n🛑 Cancel command received! Finishing current batch...")
            break

# -------- Function to get native balance --------
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
            return 0.0
    if result:
        return int(result, 16) / 1e18
    return 0.0

# -------- Function to get ERC20 token balance --------
def get_token_balance(primary_url, backup_url, address, token_address):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": token_address,
            "data": "0x70a08231000000000000000000000000" + address[2:]
        }, "latest"],
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
            return 0.0

    if result and result != "0x":
        return int(result, 16) / 1e18
    return 0.0

# -------- Worker function --------
def check_address(address, private_key):
    try:
        eth = get_eth_balance(RPC["ethereum"], RPC_BACKUP["ethereum"], address)
        base = get_eth_balance(RPC["base"], RPC_BACKUP["base"], address)
        bsc_bnb = get_eth_balance(RPC["bsc"], RPC_BACKUP["bsc"], address)

        # Get each ETH-pegged token balance separately
        bsc_tokens_balances = []
        for name, token_address in BSC_ETH_TOKENS:
            bsc_tokens_balances.append(get_token_balance(RPC["bsc"], RPC_BACKUP["bsc"], address, token_address))
    except Exception:
        eth, base, bsc_bnb = 0.0, 0.0, 0.0
        bsc_tokens_balances = [0.0 for _ in BSC_ETH_TOKENS]

    return [address, private_key, eth, base, bsc_bnb] + bsc_tokens_balances

# -------- CSV save function (thread-safe) --------
def save_results_csv(file_name, data):
    file_exists = os.path.exists(file_name)
    headers = ["address", "private_key", "Ethereum_ETH", "Base_ETH", "BSC_BNB"] + [name for name, _ in BSC_ETH_TOKENS]
    with write_lock:
        with open(file_name, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            for row in data:
                formatted_row = [f"{x:.18f}" if isinstance(x, float) else x for x in row]
                writer.writerow(formatted_row)

# -------- Main process --------
def process_csv(input_file="addresses.csv", start_row=1, end_row=None, workers=10):
    records = []
    with open(input_file, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                try:
                    data = json.loads(row[0])
                    addr = data["address"]
                    pk = data.get("private_key", "")
                    records.append((addr, pk))
                except Exception:
                    continue

    total_rows = len(records)
    if end_row is None or end_row > total_rows:
        end_row = total_rows

    records = records[start_row-1:end_row]
    output_file = f"balances_{start_row}-{end_row}.csv"

    done_addresses = set()
    if os.path.exists(output_file):
        with open(output_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                done_addresses.add(row["address"])
        print(f"Resuming... {len(done_addresses)} already processed")

    records_to_check = [r for r in records if r[0] not in done_addresses]
    total_addresses = len(records_to_check)
    print(f"📂 Checking addresses from row {start_row} to {end_row}")
    print(f"💾 Results will be saved to {output_file}\n")

    results = []
    checked_count = 0

    listener_thread = threading.Thread(target=cancel_listener, daemon=True)
    listener_thread.start()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_record = {executor.submit(check_address, addr, pk): addr for addr, pk in records_to_check}

        for future in as_completed(future_to_record):
            if stop_flag:
                break

            result = future.result()
            results.append(result)
            checked_count += 1

            remaining = total_addresses - checked_count
            print(f"✅ Checked {checked_count}/{total_addresses} | Remaining: {remaining}", end="\r")

            # Save every 50 results or at the end
            if len(results) >= 50 or checked_count == total_addresses:
                save_results_csv(output_file, results)
                results = []

    if results:
        save_results_csv(output_file, results)

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
