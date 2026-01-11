import re

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

print("=" * 80)
print("CRIB VERIFICATION AND ALIGNMENT ANALYSIS")
print("=" * 80)

print(f"\nK4 Ciphertext length: {len(K4_CIPHER)}")
print(f"Step 49 Transposed length: {len(STEP49_TRANSPOSED)}")

# Verify cribs in transposed text
cribs = ["ONLY", "USE", "SEE"]
print("\nCribs in STEP49_TRANSPOSED:")
for crib in cribs:
    if crib in STEP49_TRANSPOSED:
        pos = STEP49_TRANSPOSED.find(crib)
        end_pos = pos + len(crib)
        print(f"  {crib}: Position {pos}-{end_pos}")
        print(f"    Context: ...{STEP49_TRANSPOSED[max(0,pos-5):end_pos+5]}...")
        
        # Get corresponding ciphertext chunk
        if end_pos <= len(K4_CIPHER):
            cipher_chunk = K4_CIPHER[pos:end_pos]
            print(f"    Cipher chunk: {cipher_chunk}")

print("\n" + "=" * 80)
print("KNOWN PLAINTEXT CRIB ATTACK - Detailed")
print("=" * 80)

def derive_full_key(ciphertext, plaintext_known, position):
    """Try to derive key from known plaintext at specific position"""
    ciphertext = re.sub(r'[^A-Za-z]', '', ciphertext).upper()
    plaintext_known = re.sub(r'[^A-Za-z]', '', plaintext_known).upper()
    
    key_chars = []
    for i, p_char in enumerate(plaintext_known):
        if position + i < len(ciphertext):
            c_char = ciphertext[position + i]
            shift = (ord(c_char) - ord(p_char)) % 26
            key_chars.append(chr(shift + ord('A')))
    
    return ''.join(key_chars)

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

# For each crib, derive the key
print("\nDeriving keys from cribs:\n")

for crib in cribs:
    if crib in STEP49_TRANSPOSED:
        pos = STEP49_TRANSPOSED.find(crib)
        key_fragment = derive_full_key(K4_CIPHER, crib, pos)
        print(f"Crib: {crib} at position {pos}")
        print(f"  Key fragment: {key_fragment}")
        
        # What if we use this fragment repeated?
        full_key = (key_fragment * (len(K4_CIPHER) // len(key_fragment) + 1))[:len(K4_CIPHER)]
        decrypted = vigenere_decrypt(STEP49_TRANSPOSED, key_fragment)
        
        print(f"  Decrypt with '{key_fragment}': {decrypted[:60]}...\n")

print("\n" + "=" * 80)
print("STATISTICAL ANALYSIS - Checking for periodic patterns")
print("=" * 80)

# Check if there's a repeating pattern in the key
keys_found = []
for crib in cribs:
    if crib in STEP49_TRANSPOSED:
        pos = STEP49_TRANSPOSED.find(crib)
        key_frag = derive_full_key(K4_CIPHER, crib, pos)
        keys_found.append(key_frag)

print(f"\nKey fragments found: {keys_found}")

# Check for common characters
if keys_found:
    all_chars = ''.join(keys_found)
    from collections import Counter
    freq = Counter(all_chars)
    print(f"Character frequency in fragments: {dict(freq.most_common())}")

print("\n" + "=" * 80)
print("TRY: What if ONLY/USE/SEE are NOT at those positions in plaintext?")
print("=" * 80)

# What if the transposition scrambled the positions of these words?
# Try decrypting K4 with different keys and look for ONLY, USE, SEE

test_keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "NORTHEAST",
             "DAVM", "MSQ", "SQD", "DAVMMSQ", "MSQSQD"]

print("\nSearching for cribs after Vigenere decryption of K4:\n")

for key in test_keys:
    decrypted = vigenere_decrypt(K4_CIPHER, key)
    
    found_cribs = []
    for crib in cribs:
        if crib in decrypted:
            pos = decrypted.find(crib)
            found_cribs.append(f"{crib}@{pos}")
    
    if found_cribs:
        print(f"Key: {key:15} -> Found: {', '.join(found_cribs)}")
        print(f"  Text: {decrypted[:70]}...")

