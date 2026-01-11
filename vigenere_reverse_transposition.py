import re

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STEP49_RESULT = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"

print("=" * 80)
print("ATTEMPTING TO RECOVER TRANSPOSITION MAPPING")
print("=" * 80)

print(f"\nK4 Cipher length: {len(K4_CIPHER)}")
print(f"Step 49 Result length: {len(STEP49_RESULT)}")

# If Step49_Result is a transposition of K4, we can derive the mapping
# by finding where each character of K4 appears in Step49_Result

print("\nAnalyzing if STEP49_RESULT is a transposition of K4:\n")

# Create position mapping
position_map = {}
for i, char in enumerate(K4_CIPHER):
    # Find this position's character in the result
    # This is tricky because multiple chars are the same
    pass

# Alternative: Try to find the transposition key
# If we know plaintext contains ONLY at position 28 in STEP49_RESULT
# Then in K4_CIPHER, ONLY should be at position of the transposed indices

print("Verifying: Does K4 contain the characters of STEP49_RESULT?")
k4_sorted = sorted(K4_CIPHER)
step49_sorted = sorted(STEP49_RESULT)

if k4_sorted == step49_sorted:
    print("YES - They're both anagrams of each other!")
    print("\nThis means STEP49_RESULT is a pure transposition of K4_CIPHER")
    
    # Now find the transposition mapping
    # We need to find which positions map from K4 to STEP49
    
    # Method: For each position in STEP49, find where that character comes from in K4
    # Since we know "ONLY" is at position 28 in STEP49
    # We need to find "ONLY" in K4
    
    k4_index = 0
    step49_positions = {}
    
    for step49_pos in range(len(STEP49_RESULT)):
        target_char = STEP49_RESULT[step49_pos]
        # Find next occurrence of this character in K4 (starting from k4_index)
        remaining_k4 = K4_CIPHER[k4_index:]
        char_pos = remaining_k4.find(target_char)
        
        if char_pos >= 0:
            actual_k4_pos = k4_index + char_pos
            step49_positions[step49_pos] = actual_k4_pos
            k4_index = actual_k4_pos + 1
        else:
            print(f"Could not find {target_char} at position {step49_pos}")
            break
    
    print("\nTransposition mapping (first 20 positions):")
    for i in range(min(20, len(step49_positions))):
        print(f"  STEP49[{i:2}] = K4[{step49_positions.get(i, '?'):2}]  ({STEP49_RESULT[i]} = {K4_CIPHER.get(step49_positions.get(i, 0), '?')})")
    
    # Check if "ONLY" is findable in K4
    if "ONLY" in K4_CIPHER:
        only_pos_k4 = K4_CIPHER.find("ONLY")
        print(f"\n'ONLY' found in K4 at position {only_pos_k4}")
        print(f"  Context: ...{K4_CIPHER[max(0,only_pos_k4-5):only_pos_k4+9]}...")
    else:
        print("\n'ONLY' NOT found in K4 as a continuous substring")
    
    if "USE" in K4_CIPHER:
        use_pos_k4 = K4_CIPHER.find("USE")
        print(f"'USE' found in K4 at position {use_pos_k4}")
    else:
        print("'USE' NOT found in K4 as a continuous substring")
        
    if "SEE" in K4_CIPHER:
        see_pos_k4 = K4_CIPHER.find("SEE")
        print(f"'SEE' found in K4 at position {see_pos_k4}")
    else:
        print("'SEE' NOT found in K4 as a continuous substring")

else:
    print("NO - They are different character frequencies")
    print("K4 sorted:", ''.join(k4_sorted))
    print("STEP49 sorted:", ''.join(step49_sorted))

print("\n" + "=" * 80)
print("DIRECT VIGENERE DECRYPTION + ANALYSIS")
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
        else:
            plaintext.append(char)
    
    return ''.join(plaintext)

# What if the key is hidden in the plaintext itself?
# Try keys based on the words we know are in the result
known_words_in_result = ["ONLY", "USE", "SEE"]

print(f"\nTrying to construct key from known cribs:")

for crib in known_words_in_result:
    # If ONLY is at position 28 in plaintext
    # Then cipher[28:32] encrypted "ONLY" with key[28%len(key):32%len(key)]
    
    only_pos = STEP49_RESULT.find(crib)
    if only_pos >= 0:
        # Extract corresponding K4 characters
        k4_segment = K4_CIPHER[only_pos:only_pos+len(crib)]
        
        # Derive key
        key_chars = []
        for i, p_char in enumerate(crib):
            c_char = k4_segment[i]
            shift = (ord(c_char) - ord(p_char)) % 26
            key_chars.append(chr(shift + ord('A')))
        
        derived_key = ''.join(key_chars)
        print(f"\nCrib '{crib}' at position {only_pos}:")
        print(f"  K4 segment: {k4_segment}")
        print(f"  Derived key: {derived_key}")

print("\n" + "=" * 80)
print("CHECK: Is STEP49_RESULT already decrypted plaintext?")
print("=" * 80)

print("\nStep 49 Result:")
print(STEP49_RESULT)
print("\nContains readable words:")
print(f"  ONLY: {STEP49_RESULT.find('ONLY') >= 0} at position {STEP49_RESULT.find('ONLY')}")
print(f"  USE: {STEP49_RESULT.find('USE') >= 0} at position {STEP49_RESULT.find('USE')}")
print(f"  SEE: {STEP49_RESULT.find('SEE') >= 0} at position {STEP49_RESULT.find('SEE')}")

print("\nHypothesis: STEP49_RESULT might be partially decrypted plaintext")
print("The user said to 'combine cyclic shift step 49 with Vigenere'")
print("This suggests: Apply Vigenere decryption to K4 cipher -> STEP49_RESULT")
print("OR: Apply cyclic shift step 49 on K4, then Vigenere decrypt")

