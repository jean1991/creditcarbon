import uuid

class Identity:
    def __init__(self, name, id_number, public_key):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.id_number = id_number
        self.public_key = public_key

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "name": self.name,
            "id_number": self.id_number,
            "public_key": self.public_key,
        }

def create_identity(name, id_number, public_key):
    return Identity(name, id_number, public_key)

def verify_identity(blockchain, id_number):
    for block in blockchain.chain:
        data = block.data
        if isinstance(data, dict) and data.get("type") == "identity":
            if data.get("id_number") == id_number:
                return data
    return None