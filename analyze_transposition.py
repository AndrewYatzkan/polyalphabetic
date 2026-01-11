import re
from collections import Counter

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_RESULT = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

print("=" * 80)
print("STEP49 TRANSPOSITION ANALYSIS")
print("=" * 80)

print(f"\nK4 Cipher:      {K4_CIPHER}")
print(f"Step 49 Result: {STEP49_RESULT}")

# Verify they're anagrams
k4_freq = Counter(K4_CIPHER)
step49_freq = Counter(STEP49_RESULT)

print(f"\nCharacter frequency comparison:")
if k4_freq == step49_freq:
    print("✓ Confirmed: STEP49_RESULT is a transposition of K4_CIPHER")
else:
    print("✗ Different character frequencies")

# The key insight: STEP49_RESULT contains ONLY, USE, SEE as readable words
# This suggests K4 was decrypted with Vigenere first, then transposed

print("\n" + "=" * 80)
print("HYPOTHESIS: K4 cipher -> Vigenere decrypt -> Transposition Step 49")
print("=" * 80)

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
    
    return ''.join(plaintext)

# We already found DAVM produces ONLY at position 28 in K4 decrypted
# Let's work backwards: if ONLY is at position 28 in the transposed result
# and the transposition moves characters around, then we need to find
# where position 28 comes from in K4

print("\nWorking backwards from STEP49_RESULT:")
print(f"  ONLY appears at position 28-31 in STEP49_RESULT")
print(f"  USE appears at position 85-87 in STEP49_RESULT")  
print(f"  SEE appears at position 86-88 in STEP49_RESULT")

# Key insight: Since STEP49 and K4 are anagrams with ONLY appearing in STEP49
# But ONLY NOT appearing in K4, this means:
# The transposition CREATED the word ONLY by rearranging characters
# So the original K4 decryption (before transposition) had the letters O,N,L,Y
# but not consecutive

print("\n" + "=" * 80)
print("REVERSE TRANSPOSITION STEP 49")
print("=" * 80)

# To reverse the transposition, we need to find the permutation
# Create a simple analysis: where does each character position map?

# Build reverse mapping by finding repeated characters
print("\nLooking for transposition pattern...")

# Method: Find repeating characters and their position relationships
for target_char in ['A', 'B', 'C', 'D', 'E', 'F']:
    k4_positions = [i for i, c in enumerate(K4_CIPHER) if c == target_char]
    step49_positions = [i for i, c in enumerate(STEP49_RESULT) if c == target_char]
    
    if k4_positions and step49_positions:
        print(f"\n'{target_char}' positions:")
        print(f"  K4:     {k4_positions}")
        print(f"  STEP49: {step49_positions}")
        
        if len(k4_positions) == len(step49_positions):
            # Calculate offset differences
            diffs = [s - k for s, k in zip(step49_positions, k4_positions)]
            print(f"  Offset: {diffs}")

print("\n" + "=" * 80)
print("TESTING HYPOTHESIS: Apply Vigenere with found keys")
print("=" * 80)

# We found that key fragment "DAVM" from position 28
# What if this key (or variations) was used for Vigenere before transposition?

print("\nKey candidates:")
key_candidates = ["DAVM", "DAVMDAVM", "DAVMMUSIC", "DAVIDMUSIC"]

for key in key_candidates:
    decrypted = vigenere_decrypt(K4_CIPHER, key)
    
    # Check if this decrypted text is a permutation of STEP49
    decrypted_freq = Counter(decrypted)
    step49_freq = Counter(STEP49_RESULT)
    
    if decrypted_freq == step49_freq:
        print(f"\n✓ KEY FOUND: '{key}'")
        print(f"  K4 decrypted with '{key}' is a permutation of STEP49!")
        print(f"  Decrypted: {decrypted}")
        print(f"\n  This means: K4 -> Vigenere('{key}') -> {decrypted}")
        print(f"             -> Transposition Step 49 -> {STEP49_RESULT}")
    else:
        print(f"\n✗ Key '{key}': Different character frequencies")
        # Show what's different
        all_chars = set(decrypted_freq.keys()) | set(step49_freq.keys())
        differences = []
        for char in sorted(all_chars):
            if decrypted_freq.get(char, 0) != step49_freq.get(char, 0):
                differences.append(f"{char}({decrypted_freq.get(char, 0)}vs{step49_freq.get(char, 0)})")
        
        if len(differences) <= 5:
            print(f"  Differences: {', '.join(differences[:5])}")

