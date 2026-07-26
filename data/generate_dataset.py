"""
Synthetic AML Dataset Generator for FinShield AI
=================================================
Generates a realistic synthetic transaction dataset for Anti-Money Laundering (AML)
demonstration purposes.

Inspired by:
- PaySim synthetic financial dataset (Kaggle, E. A. Lopez-Rojas, 2016)
- IBM AML synthetic data (Kaggle, IBM Research, 2023)

Dataset Schema:
  transaction_id      : Unique transaction identifier
  customer_id         : Sender customer ID
  recipient_id        : Recipient customer ID
  amount              : Transaction amount (USD)
  timestamp           : ISO-8601 datetime
  transaction_type    : WIRE / CASH / ACH / CRYPTO / SWIFT
  country_origin      : Originating country (ISO-3166 alpha-2)
  country_dest        : Destination country (ISO-3166 alpha-2)
  ip_address          : Login IP of the sender
  device_id           : Sender device fingerprint
  merchant_id         : Merchant ID (if applicable)
  wallet_id           : Crypto wallet (if CRYPTO type)
  aml_pattern         : Ground truth AML pattern (NONE/STRUCTURING/SMURFING/LAYERING/SHELL)
  is_flagged          : Ground truth flag (0/1)

Usage:
  python data/generate_dataset.py
"""

import csv, random, string
from datetime import datetime, timedelta

random.seed(42)

N_CUSTOMERS = 500
N_TRANSACTIONS = 10_000
N_FLAGGED_CUSTOMERS = 50
OUTPUT_PATH = "data/aml_transactions.csv"

HIGH_RISK_COUNTRIES = ["PK","YE","SY","IR","KP","MM","AF","HT","LA"]
NORMAL_COUNTRIES    = ["US","GB","SG","DE","AU","CA","JP","FR","NL","IN","AE"]
TX_TYPES = ["WIRE","CASH","ACH","CRYPTO","SWIFT"]

def rand_id(prefix, n=6):
    return f"{prefix}_{''.join(random.choices(string.digits, k=n))}"

def rand_ip():
    return f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

def rand_ts(start, end):
    delta = end - start
    return (start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))).isoformat()

customers = [rand_id("C") for _ in range(N_CUSTOMERS)]
flagged_set = set(random.sample(customers, N_FLAGGED_CUSTOMERS))
shells = [rand_id("SHELL") for _ in range(20)]

START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)
rows = []

for i in range(N_TRANSACTIONS):
    tx_id = rand_id("TX", 8)
    customer = random.choice(customers)
    is_bad = customer in flagged_set
    ts = rand_ts(START_DATE, END_DATE)
    tx_type = random.choice(TX_TYPES)
    amount = round(random.uniform(100, 50_000), 2)
    country_origin = random.choice(NORMAL_COUNTRIES)
    country_dest   = random.choice(NORMAL_COUNTRIES)
    aml_pattern    = "NONE"
    is_flagged     = 0
    recipient      = rand_id("C")
    merchant_id    = rand_id("M") if tx_type == "ACH" else ""
    wallet_id      = rand_id("W") if tx_type == "CRYPTO" else ""
    ip_addr        = rand_ip()
    device_id      = rand_id("DEV")

    if is_bad:
        pattern = random.choices(
            ["STRUCTURING","SMURFING","LAYERING","SHELL"],
            weights=[35,25,25,15]
        )[0]
        if pattern == "STRUCTURING":
            amount = round(random.uniform(8_500, 9_999), 2)
            tx_type = "CASH"
            country_dest = country_origin
            aml_pattern = "STRUCTURING"
            is_flagged = 1
        elif pattern == "SMURFING":
            amount = round(random.uniform(500, 3_000), 2)
            aml_pattern = "SMURFING"
            is_flagged = 1
        elif pattern == "LAYERING":
            country_dest = random.choice(HIGH_RISK_COUNTRIES)
            amount = round(random.uniform(20_000, 200_000), 2)
            tx_type = random.choice(["WIRE","SWIFT","CRYPTO"])
            aml_pattern = "LAYERING"
            is_flagged = 1
        elif pattern == "SHELL":
            recipient = random.choice(shells)
            country_dest = random.choice(HIGH_RISK_COUNTRIES)
            amount = round(random.uniform(50_000, 500_000), 2)
            tx_type = "WIRE"
            aml_pattern = "SHELL"
            is_flagged = 1

    rows.append({
        "transaction_id": tx_id, "customer_id": customer, "recipient_id": recipient,
        "amount": amount, "timestamp": ts, "transaction_type": tx_type,
        "country_origin": country_origin, "country_dest": country_dest,
        "ip_address": ip_addr, "device_id": device_id, "merchant_id": merchant_id,
        "wallet_id": wallet_id, "aml_pattern": aml_pattern, "is_flagged": is_flagged,
    })

fields = list(rows[0].keys())
with open(OUTPUT_PATH, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

total_flagged = sum(r["is_flagged"] for r in rows)
print(f"Dataset generated: {OUTPUT_PATH}")
print(f"  Transactions:   {N_TRANSACTIONS:,}")
print(f"  Flagged txns:   {total_flagged:,} ({total_flagged/N_TRANSACTIONS*100:.1f}%)")
