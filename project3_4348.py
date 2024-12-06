import os
import struct

# Constants
MAGIC_NUMBER = b"4337PRJ3"
BLOCK_SIZE = 512
MIN_DEGREE = 10  # Minimum degree of the B-Tree

# BTreeNode Class
class BTreeNode:
    """Represents a B-Tree node."""

    def __init__(self, block_id, parent_id, key_count=0):
        """Initialize a node with metadata and storage for keys, values, and children."""
        self.block_id = block_id
        self.parent_id = parent_id
        self.key_count = key_count
        self.keys = [0] * (2 * MIN_DEGREE - 1)  # Keys array
        self.values = [0] * (2 * MIN_DEGREE - 1)  # Values array
        self.children = [0] * (2 * MIN_DEGREE)  # Child pointers


    def serialize(self):
        """Convert the node into bytes for file storage."""
        data = struct.pack(">Q", self.block_id) + struct.pack(">Q", self.parent_id) + struct.pack(">Q", self.key_count)
        data += b''.join(struct.pack(">Q", key) for key in self.keys)
        data += b''.join(struct.pack(">Q", value) for value in self.values)
        data += b''.join(struct.pack(">Q", child) for child in self.children)
        return data.ljust(BLOCK_SIZE, b'\x00')  # Pad to 512 bytes

    @staticmethod
    def deserialize(data):
        """Convert bytes back into a BTreeNode object."""
        block_id = struct.unpack(">Q", data[:8])[0]
        parent_id = struct.unpack(">Q", data[8:16])[0]
        key_count = struct.unpack(">Q", data[16:24])[0]
        keys = [struct.unpack(">Q", data[24 + i * 8:32 + i * 8])[0] for i in range(2 * MIN_DEGREE - 1)]
        values = [struct.unpack(">Q", data[184 + i * 8:192 + i * 8])[0] for i in range(2 * MIN_DEGREE - 1)]
        children = [struct.unpack(">Q", data[344 + i * 8:352 + i * 8])[0] for i in range(2 * MIN_DEGREE)]
        return BTreeNode(block_id, parent_id, key_count)

# IndexManager Class
class IndexManager:
    """Manages the index file and implements the commands."""

    def __init__(self):
        self.file_name = None
        self.index = {}

    def create(self):
        """Create a new index file."""
        file_name = input("Enter file name: ").strip()
        if os.path.exists(file_name):
            overwrite = input(f"File {file_name} exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != "yes":
                print("Operation canceled.")
                return
        with open(file_name, "wb") as f:
            f.write(MAGIC_NUMBER)  # Write header
            f.write(b"\x00" * (BLOCK_SIZE - len(MAGIC_NUMBER)))  # Pad to BLOCK_SIZE
        self.file_name = file_name
        self.index.clear()
        print(f"File {file_name} created and opened.")

    def open(self):
        """Open an existing index file."""
        file_name = input("Enter file name: ").strip()
        if not os.path.exists(file_name):
            print(f"Error: File {file_name} does not exist.")
            return
        with open(file_name, "rb") as f:
            magic = f.read(8)
            if magic != MAGIC_NUMBER:
                print("Error: Invalid file format.")
                return
        self.file_name = file_name
        self.index.clear()  # Reset index for new file
        print(f"File {file_name} opened.")

    def insert(self):
        """Insert a key-value pair into the index."""
        if not self.file_name:
            print("Error: No file is open.")
            return
        try:
            key = int(input("Enter key: "))
            value = int(input("Enter value: "))
            if key in self.index:
                print("Error: Key already exists.")
            else:
                self.index[key] = value
                print("Key-value pair inserted.")
        except ValueError:
            print("Error: Invalid input.")

    def search(self):
        """Search for a key in the index."""
        if not self.file_name:
            print("Error: No file is open.")
            return
        try:
            key = int(input("Enter key: "))
            if key in self.index:
                print(f"Key: {key}, Value: {self.index[key]}")
            else:
                print("Error: Key not found.")
        except ValueError:
            print("Error: Invalid input.")

    def load(self):
        """Load key-value pairs from a file."""
        if not self.file_name:
            print("Error: No file is open.")
            return
        file_name = input("Enter file name: ").strip()
        if not os.path.exists(file_name):
            print(f"Error: File {file_name} does not exist.")
            return
        with open(file_name, "r") as f:
            for line in f:
                try:
                    key, value = map(int, line.strip().split(","))
                    if key in self.index:
                        print(f"Warning: Key {key} already exists. Skipping.")
                    else:
                        self.index[key] = value
                except ValueError:
                    print(f"Error: Invalid line '{line.strip()}'. Skipping.")

    def print_index(self):
        """Print all key-value pairs."""
        if not self.file_name:
            print("Error: No file is open.")
            return
        for key, value in sorted(self.index.items()):
            print(f"Key: {key}, Value: {value}")

    def extract(self):
        """Save all key-value pairs to a file."""
        if not self.file_name:
            print("Error: No file is open.")
            return
        file_name = input("Enter file name to save: ").strip()
        if os.path.exists(file_name):
            overwrite = input(f"File {file_name} exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite != "yes":
                print("Operation canceled.")
                return
        with open(file_name, "w") as f:
            for key, value in sorted(self.index.items()):
                f.write(f"{key},{value}\n")
        print(f"Index saved to {file_name}.")

    def quit(self):
        """Exit the program."""
        print("Exiting program.")
        exit()

    def interactive_menu(self):
        """Main interactive menu for user commands."""
        commands = {
            "create": self.create,
            "open": self.open,
            "insert": self.insert,
            "search": self.search,
            "load": self.load,
            "print": self.print_index,
            "extract": self.extract,
            "quit": self.quit,
        }
        while True:
            print("Commands: create, open, insert, search, load, print, extract, quit")
            command = input("Enter a command: ").strip().lower()
            if command in commands:
                commands[command]()
            else:
                print("Invalid command. Try again.")

# Main Execution
if __name__ == "__main__":
    manager = IndexManager()
    manager.interactive_menu()
