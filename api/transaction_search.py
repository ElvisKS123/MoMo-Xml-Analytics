import time
import json


transactions = [
    {
        "id": i,
        "address": "M-Money",
        "date": f"1715369560{i}245",
        "readable_date": f"10 May 2024 9:{30+i}:40 PM",
        "body": f"New transaction body {i}",
        "transaction_type": "PAYMENT" if i % 2 == 0 else "DEBIT",
        "amount": 100 + i*5,
        "sender": None,
        "recipient": f"Recipient {i}",
        "cont": f"Extra content {i}"
    }
    for i in range(20)
]

# ---------------------------
# Linear Search
# ---------------------------
def linear_search(transactions, tx_id):
    """
    Search for a transaction by ID using linear search (O(n))
    """
    for t in transactions:
        if t["id"] == tx_id:
            return t
    return None

# ---------------------------
# Dictionary Lookup
# ---------------------------

tx_dict = {t["id"]: t for t in transactions}

def dict_lookup(tx_dict, tx_id):
    """
    Search for a transaction by ID using dictionary lookup (O(1))
    """
    return tx_dict.get(tx_id)

# ---------------------------
# Test execution time
# ---------------------------
search_id = 15  # choose any ID between 0 and 19

# Linear search timing
start = time.time()
linear_result = linear_search(transactions, search_id)
linear_time = time.time() - start

# Dict lookup timing
start = time.time()
dict_result = dict_lookup(tx_dict, search_id)
dict_time = time.time() - start

# ---------------------------
# Print results
# ---------------------------
print(f"Searching for transaction ID {search_id}\n")

print("Linear Search Result:")
print(json.dumps(linear_result, indent=2))
print(f"Linear Search Time: {linear_time:.8f} seconds\n")

print("Dictionary Lookup Result:")
print(json.dumps(dict_result, indent=2))
print(f"Dictionary Lookup Time: {dict_time:.8f} seconds\n")

# ---------------------------
# Reflection
# ---------------------------
print("Observation:")
print("Dictionary lookup is faster because it uses hashing (O(1)) compared to linear search (O(n)).")
