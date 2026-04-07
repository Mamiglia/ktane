import random
from copy import copy
from typing import Any, Any, Optional

def _chars_from_ranges(ranges):
    return [chr(codepoint) for start, end in ranges for codepoint in range(start, end + 1)]

SYMBOLS = [chr(i) for i in range(32, 127)] + _chars_from_ranges([
    (0x0041, 0x005A),   # Latin uppercase A-Z
    (0x0401, 0x0401),   # Cyrillic uppercase YO
    (0x0410, 0x042F),   # Cyrillic uppercase А-Я
    (0x391, 0x3A9),   # Greek uppercase Α-Ω
    # (0x4E00, 0x9FFF),   # CJK Unified Ideographs (Chinese characters)
    # (0x1F300, 0x1F5FF), # Misc Symbols and Pictographs
    (0x1F600, 0x1F64F), # Emoticons
    # (0x1F680, 0x1F6FF), # Transport and Map Symbols
    # (0x1F900, 0x1F9FF), # Supplemental Symbols and Pictographs
])

class Cipher:
    def __init__(self, values: list[str], seed: Optional[int] = None):
        self.values = values
        if seed is not None:
            random.seed(seed)
        
        self.mapping = self.create_mapping()

    def create_mapping(self) -> dict:
        # Each value maps to a random character in all the unicode symbols
        symbols = copy(SYMBOLS)
        random.shuffle(symbols)
        mapping = {}
        for value in self.values:
            mapping[value] = symbols.pop()
        return mapping
    
    def encode(self, values: str | Any) -> str:
        if not isinstance(values, str):
            values = str(values)
        return ''.join(self.mapping[value] for value in values)
    
    def decode(self, encoded: str) -> str:
        reverse_mapping = {v: k for k, v in self.mapping.items()}
        return ''.join(reverse_mapping[char] for char in encoded)
    
    def display_mapping(self):
        return '\n'.join(f"{char} -> {value}" for value, char in self.mapping.items())
    
    def __str__(self) -> str:
        return f"Cipher({self.mapping})"
    
    
class NumericCipher(Cipher):
    def __init__(self, seed: Optional[int] = None):
        values = [str(i) for i in range(10)] + ['.']
        super().__init__(values, seed=seed)
        
        
if __name__ == "__main__":
    cipher = NumericCipher()
    encoded = cipher.encode("3.14")
    decoded = cipher.decode(encoded)
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")