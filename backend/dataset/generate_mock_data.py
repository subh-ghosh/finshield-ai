import pandas as pd
import random
import os

# Use current directory
DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_PATH = os.path.join(DATASET_DIR, "accounts.csv")
TRANSACTIONS_PATH = os.path.join(DATASET_DIR, "transactions.csv")

def generate_data(num_accounts=500, num_transactions=5000):
    print("Loading existing data to find max IDs...")
    try:
        df_accounts = pd.read_csv(ACCOUNTS_PATH)
        max_account_id = df_accounts["ACCOUNT_ID"].max()
    except Exception:
        max_account_id = 10000
        
    try:
        df_tx = pd.read_csv(TRANSACTIONS_PATH)
        max_tx_id = df_tx["TX_ID"].max()
        max_timestamp = df_tx["TIMESTAMP"].max()
    except Exception:
        max_tx_id = 1323236
        max_timestamp = 100
        
    print(f"Current Max Account ID: {max_account_id}")
    print(f"Current Max TX ID: {max_tx_id}")
    print(f"Current Max Timestamp: {max_timestamp}")
    
    # Generate Accounts
    new_accounts = []
    for i in range(1, num_accounts + 1):
        acc_id = max_account_id + i
        new_accounts.append({
            "ACCOUNT_ID": acc_id,
            "CUSTOMER_ID": f"C_{acc_id}",
            "INIT_BALANCE": round(random.uniform(100, 5000), 2),
            "COUNTRY": "US",
            "ACCOUNT_TYPE": "I",
            "IS_FRAUD": "false",
            "TX_BEHAVIOR_ID": 1
        })
        
    df_new_accounts = pd.DataFrame(new_accounts)
    
    # Generate Transactions
    new_transactions = []
    account_ids = list(df_accounts["ACCOUNT_ID"]) + [a["ACCOUNT_ID"] for a in new_accounts]
    
    for i in range(1, num_transactions + 1):
        tx_id = max_tx_id + i
        sender = random.choice(account_ids)
        receiver = random.choice(account_ids)
        while receiver == sender:
            receiver = random.choice(account_ids)
            
        new_transactions.append({
            "TX_ID": tx_id,
            "SENDER_ACCOUNT_ID": sender,
            "RECEIVER_ACCOUNT_ID": receiver,
            "TX_TYPE": "TRANSFER",
            "TX_AMOUNT": round(random.uniform(10, 2000), 2),
            "TIMESTAMP": max_timestamp + random.randint(1, 10),
            "IS_FRAUD": "False",
            "ALERT_ID": -1
        })
        
    df_new_tx = pd.DataFrame(new_transactions)
    
    print(f"Appending {num_accounts} accounts and {num_transactions} transactions...")
    df_new_accounts.to_csv(ACCOUNTS_PATH, mode='a', header=False, index=False)
    df_new_tx.to_csv(TRANSACTIONS_PATH, mode='a', header=False, index=False)
    print("Done! Dataset expanded.")

if __name__ == "__main__":
    generate_data()
