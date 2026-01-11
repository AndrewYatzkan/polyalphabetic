import re
from itertools import combinations

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

# Known cribs/patterns
CRIBS = ["BERLIN", "CLOCK", "KRYPTOS", "PALIMPSEST", "ABSCISSA", "ONLY", "USE", "SEE"]
POSSIBLE_PLAINTEXTS = [
    "BERLINCLOCK",
    "BERLINCLOCKUNDERGROUND",
    "THECLOCKRUNSNORTH",
    "NORTHEASTCORNER",
]

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere cipher"""
    ciphertext = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    key = re.sub(r'[^A-Za-z]', '', key).upper()
    
    plaintext = []
    key_index = 0
    
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext.append(decrypted)
            key_index += 1
        else:
            plaintext.append(char)
    
    return ''.join(plaintext)

def vigenere_encrypt(plaintext, key):
    """Encrypt using Vigenere cipher"""
    plaintext = re.sub(r'[^A-Za-z]', '', plaintext).upper()
    key = re.sub(r'[^A-Za-z]', '', key).upper()
    
    ciphertext = []
    key_index = 0
    
    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('A')
            encrypted = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            ciphertext.append(encrypted)
            key_index += 1
        else:
            ciphertext.append(char)
    
    return ''.join(ciphertext)

def derive_key_from_ciphertext_and_plaintext(ciphertext, plaintext):
    """Derive the key from known plaintext attack"""
    ciphertext = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    plaintext = re.sub(r'[^A-Za-z]', '', plaintext).upper()
    
    if len(ciphertext) < len(plaintext):
        return None
    
    key = []
    for i in range(len(plaintext)):
        shift = (ord(ciphertext[i]) - ord(plaintext[i])) % 26
        key.append(chr(shift + ord('A')))
    
    return ''.join(key)

def count_vowels(text):
    """Count vowel ratio"""
    vowels = sum(1 for c in text if c in 'AEIOU')
    return vowels / len(text) if text else 0

def find_english_patterns(text):
    """Look for English word patterns"""
    patterns = {
        'THE': r'THE',
        'AND': r'AND',
        'ING': r'ING',
        'TION': r'TION',
        'ER': r'ER',
    }
    
    found = []
    for pattern_name, pattern in patterns.items():
        if re.search(pattern, text):
            found.append(pattern_name)
    
    return found

print("=" * 80)
print("ADVANCED VIGENERE ANALYSIS")
print("=" * 80)

# Try different key combinations and lengths
extended_keys = CRIBS + [
    "KRYPTOS" + x for x in CRIBS
] + [
    "BERLIN" + "CLOCK",
    "CLOCK" + "BERLIN",
    "NORTHEAST" + "BERLIN",
    "PALIMPSEST" + "ABSCISSA",
]

print("\nTrying all keys on STEP49 transposed text:\n")

best_results = []

for key in extended_keys[:15]:  # Limit to first 15
    decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key)
    vowel_ratio = count_vowels(decrypted)
    patterns = find_english_patterns(decrypted)
    
    if vowel_ratio > 0.35 or patterns:
        best_results.append((key, decrypted, vowel_ratio, patterns))
        print(f"Key: {key:25} | Vowels: {vowel_ratio:.2%} | Patterns: {patterns}")
        print(f"  Result: {decrypted[:50]}...\n")

print("\n" + "=" * 80)
print("KNOWN PLAINTEXT ATTACK")
print("=" * 80)

# Try to find key using crib positions
print("\nSearching for ONLY, USE, SEE positions in transposed text...")
transposed = STEP49_TRANSPOSED

for crib in ["ONLY", "USE", "SEE"]:
    if crib in transposed:
        pos = transposed.find(crib)
        print(f"\nFound '{crib}' at position {pos}")
        
        # Try to derive key from this position
        if pos + len(crib) <= len(K4_CIPHER):
            ciphertext_chunk = K4_CIPHER[pos:pos+len(crib)]
            potential_key = derive_key_from_ciphertext_and_plaintext(ciphertext_chunk, crib)
            if potential_key:
                print(f"  Potential key fragment: {potential_key}")
                
                # Try extending this key
                full_decrypt = vigenere_decrypt(STEP49_TRANSPOSED, potential_key)
                print(f"  Full decrypt with key '{potential_key}': {full_decrypt[:60]}...")

# Try Reverse Vigenere first, then check for transposition patterns
print("\n\n" + "=" * 80)
print("REVERSE ORDER: Vigenere on K4 first")
print("=" * 80)

for key in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "NORTHEAST"]:
    decrypted = vigenere_decrypt(K4_CIPHER, key)
    vowel_ratio = count_vowels(decrypted)
    patterns = find_english_patterns(decrypted)
    
    if vowel_ratio > 0.35 or patterns:
        print(f"\nKey: {key} | Vowels: {vowel_ratio:.2%} | Patterns: {patterns}")
        print(f"Result: {decrypted[:50]}...")
        
        # Check for sequence position patterns
        if "ONLY" in decrypted:
            print(f"  Contains ONLY!")
        if "USE" in decrypted:
            print(f"  Contains USE!")
        if "SEE" in decrypted:
            print(f"  Contains SEE!")

