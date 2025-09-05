import time
from blockchain import Blockchain

# Initialize blockchain
bc = Blockchain()

# Add sample identity blocks
identities = [
    {"type": "identity", "name": "Alice", "id_number": "ID12345", "public_key": "AlicePublicKey"},
    {"type": "identity", "name": "Bob", "id_number": "ID67890", "public_key": "BobPublicKey"}
]

for identity in identities:
    bc.create_block(identity)

# Print the blockchain
for block in bc.chain:
    print({
        "index": block.index,
        "previous_hash": block.previous_hash,
        "timestamp": block.timestamp,
        "data": block.data,
        "hash": block.hash
    })
