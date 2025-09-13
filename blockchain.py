import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_data = {"type": "genesis", "message": "Genesis Block"}
        self.create_block(genesis_data)

    def create_block(self, data):
        index = len(self.chain) + 1
        timestamp = time.time()
        previous_hash = self.chain[-1].hash if self.chain else '0'
        hash = self.hash_block(index, previous_hash, timestamp, data)
        block = Block(index, previous_hash, timestamp, data, hash)
        self.chain.append(block)
        return block

    def hash_block(self, index, previous_hash, timestamp, data):
        block_string = json.dumps({
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "data": data
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
