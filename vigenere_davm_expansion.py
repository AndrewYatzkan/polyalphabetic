import re
from collections import Counter

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

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

def find_and_highlight_words(text):
    """Find and highlight potential English words"""
    common_words = {
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
        'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
        'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'OWN', 'SAY', 'SHE', 'TOO', 'TWO',
        'WAY', 'WHO', 'BOY', 'DID', 'USE', 'ONLY', 'SEE', 'LIKE', 'TIME',
        'YEAR', 'WORK', 'BACK', 'CALL', 'COME', 'EVEN', 'FIND', 'GIVE', 'GOOD',
        'HAND', 'HIGH', 'JUST', 'KEEP', 'LAST', 'LIFE', 'LONG', 'MADE', 'MAKE',
        'MANY', 'MORE', 'MOST', 'MUCH', 'MUST', 'NAME', 'NEED', 'NEXT', 'ONLY',
        'OVER', 'PART', 'SAME', 'SUCH', 'TAKE', 'TELL', 'THAN', 'THAT', 'THEM',
        'THEN', 'THEY', 'THIS', 'VERY', 'WANT', 'WELL', 'WHAT', 'WHEN', 'WITH',
    }
    
    highlighted = text
    found = []
    
    for word in sorted(common_words, key=len, reverse=True):
        if word in text:
            highlighted = highlighted.replace(word, f"[{word}]")
            found.append(word)
    
    return highlighted, found

# Test DAVM and its variations
test_keys = [
    "DAVM",
    "DAVMDAVM",
    "DAVMDAVMDAVM",
    "DAVMONLY",
    "DAVMMUSIC",
    "DAVMCLOCK",
    "DAVMBERLIN",
    "ONLY",
    "ONLYDAVM",
    "DAVMUSE",
    "DAVMSEE",
]

print("=" * 80)
print("ANALYZING KEY 'DAVM' AND VARIATIONS")
print("=" * 80)

print("\n1. K4 DECRYPTION WITH DAVM VARIANTS:\n")

for key in test_keys:
    decrypted_k4 = vigenere_decrypt(K4_CIPHER, key)
    decrypted_t49 = vigenere_decrypt(STEP49_TRANSPOSED, key)
    
    # Highlight words
    highlighted_k4, found_k4 = find_and_highlight_words(decrypted_k4)
    highlighted_t49, found_t49 = find_and_highlight_words(decrypted_t49)
    
    if found_k4 or found_t49:
        print(f"\nKey: {key}")
        print(f"  K4 found words: {found_k4}")
        print(f"  K4 decrypt: {highlighted_k4}")
        print(f"  T49 found words: {found_t49}")
        if len(highlighted_t49) <= 120:
            print(f"  T49 decrypt: {highlighted_t49}")
        else:
            print(f"  T49 decrypt: {highlighted_t49[:120]}...")

print("\n" + "=" * 80)
print("2. FULL TEXT ANALYSIS - DAVM (Most Promising)")
print("=" * 80)

key = "DAVM"
decrypt_k4 = vigenere_decrypt(K4_CIPHER, key)
decrypt_t49 = vigenere_decrypt(STEP49_TRANSPOSED, key)

print(f"\nKey: {key}")
print(f"\nK4 Decryption:")
print(decrypt_k4)
print(f"\nStep49 Transposed Decryption:")
print(decrypt_t49)

# Analyze character distribution
print(f"\n" + "=" * 80)
print("Character frequency analysis (K4 decryption):")
print("=" * 80)

freq = Counter(decrypt_k4)
sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
print("\nTop 15 characters:")
for char, count in sorted_freq[:15]:
    print(f"  {char}: {count} ({count/len(decrypt_k4)*100:.1f}%)")

# Check for sequences that look like words
print("\n" + "=" * 80)
print("Searching for potential word patterns:")
print("=" * 80)

# Look for common endings
endings = ['ING', 'TION', 'ER', 'ED', 'LY', 'NESS', 'MENT']
for ending in endings:
    count = decrypt_k4.count(ending)
    if count > 0:
        print(f"  {ending}: appears {count} times")

# Look for sequences with alternating vowels/consonants
print("\nPotential readable sequences (V=vowel, C=consonant):")
vowels = set('AEIOU')

patterns = []
current_pattern = ""
current_type = None

for i, char in enumerate(decrypt_k4):
    char_type = 'V' if char in vowels else 'C'
    
    if current_type is None:
        current_type = char_type
        current_pattern = f"{char}({char_type})"
    elif char_type == current_type:
        current_pattern += f"{char}({char_type})"
    else:
        if len(current_pattern) >= 8:  # Only show longer sequences
            patterns.append(current_pattern)
        current_pattern = f"{char}({char_type})"
        current_type = char_type

if current_pattern and len(current_pattern) >= 8:
    patterns.append(current_pattern)

# Show some interesting patterns
interesting = [p for p in patterns if 'V' in p and 'C' in p]
if interesting:
    print(f"  (showing mixed V/C patterns with good vowel distribution)")

print("\n" + "=" * 80)
print("3. EXTENDED DAVM ANALYSIS")
print("=" * 80)

# Try repeating DAVM at different intervals
extended_keys = [
    "DAVMDAVM",
    "DAVMDAVMDAVMDAVM",
    "D" * 97,
    "A" * 97,
    "V" * 97,
    "M" * 97,
]

for key in extended_keys[:3]:
    decrypt_k4 = vigenere_decrypt(K4_CIPHER, key)
    highlighted, found = find_and_highlight_words(decrypt_k4)
    
    if found:
        print(f"\nKey: {key}")
        print(f"  Found: {found}")
        print(f"  Text: {decrypt_k4}")

