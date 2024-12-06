import os
import struct

# Constants
MAGIC_NUMBER = b"4337PRJ3"
BLOCK_SIZE = 512
MIN_DEGREE = 10  # Minimum degree of the B-Tree

# BTreeNode Class
class BTreeNode:
    def __init__(self, block_id, parent_id, key_count=0):
        self.block_id = block_id
        self.parent_id = parent_id
        self.key_count = key_count
        self.keys = [0] * (2 * MIN_DEGREE - 1)
        self.values = [0] * (2 * MIN_DEGREE - 1)
        self.children = [0] * (2 * MIN_DEGREE)

    def serialize(self):
        # Serialize node into 512-byte block
        data = struct.pack(">Q", self.block_id) + struct.pack(">Q", self.parent_id) + struct.pack(">Q", self.key_count)
        data += b''.join(struct.pack(">Q", key) for key in self.keys)
        data += b''.join(struct.pack(">Q", value) for value in self.values)
        data += b''.join(struct.pack(">Q", child) for child in self.children)
        return data.ljust(BLOCK_SIZE, b'\x00')

    @staticmethod
    def deserialize(data):
        # Deserialize node from 512-byte block
        block_id = struct.unpack(">Q", data[:8])[0]
        parent_id = struct.unpack(">Q", data[8:16])[0]
        key_count = struct.unpack(">Q", data[16:24])[0]
        keys = [struct.unpack(">Q", data[24 + i * 8:32 + i * 8])[0] for i in range(2 * MIN_DEGREE - 1)]
        values = [struct.unpack(">Q", data[184 + i * 8:192 + i * 8])[0] for i in range(2 * MIN_DEGREE - 1)]
        children = [struct.unpack(">Q", data[344 + i * 8:352 + i * 8])[0] for i in range(2 * MIN_DEGREE)]
        return BTreeNode(block_id, parent_id, key_count, keys, values, children)

# FileHandler Class
class FileHandler:
    def __init__(self):
        self.file_name = None
        self.file = None

    def create_file(self, file_name):
        if os.path.exists(file_name):
            overwrite = input(f"File {file_name} exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != 'yes':
                print("Aborted.")
                return False
        with open(file_name, "wb") as f:
            f.write(MAGIC_NUMBER)  # Write magic number
            f.write(struct.pack(">Q", 0))  # Root ID
            f.write(struct.pack(">Q", 1))  # Next block ID
            f.write(b'\x00' * (BLOCK_SIZE - 24))  # Padding
        print(f"File {file_name} created.")
        self.file_name = file_name
        return True

    def open_file(self, file_name):
        if not os.path.exists(file_name):
            print(f"File {file_name} does not exist.")
            return False
        with open(file_name, "rb") as f:
            magic = f.read(8)
            if magic != MAGIC_NUMBER:
                print(f"File {file_name} is not a valid index file.")
                return False
        self.file_name = file_name
        print(f"File {file_name} opened.")
        return True

# Main Menu Class
class IndexManager:
    def __init__(self):
        self.file_handler = FileHandler()

    def interactive_menu(self):
        while True:
            print("\nCommands: create, open, quit")
            command = input("Enter a command: ").strip().lower()
            if command == "create":
                file_name = input("Enter file name: ").strip()
                self.file_handler.create_file(file_name)
            elif command == "open":
                file_name = input("Enter file name: ").strip()
                self.file_handler.open_file(file_name)
            elif command == "quit":
                print("Exiting program.")
                break
            else:
                print("Invalid command. Try again.")

# Main Execution
if __name__ == "__main__":
    manager = IndexManager()
    manager.interactive_menu()