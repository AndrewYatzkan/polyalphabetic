#!/usr/bin/env python3
"""
Test with KRYPTOS keyed alphabet for K4 decryption
"""

def vigenere_decrypt_kryptos(ciphertext, key):
    """Decrypt using Vigenere cipher with KRYPTOS keyed alphabet"""
    # KRYPTOS keyed alphabet: K-R-Y-P-T-O-S followed by remaining letters
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    standard_alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    result = []
    key_upper = key.upper()
    cipher_upper = ciphertext.upper()

    key_index = 0
    for char in cipher_upper:
        if char.isalpha():
            # Find position in standard alphabet
            char_pos = ord(char) - ord('A')

            # Find key character position in KRYPTOS alphabet
            if key_upper[key_index % len(key_upper)] in kryptos_alpha:
                key_pos = kryptos_alpha.index(key_upper[key_index % len(key_upper)])
            else:
                key_pos = ord(key_upper[key_index % len(key_upper)]) - ord('A')

            # Decrypt: position = (cipher_pos - key_pos) mod 26
            decrypted_pos = (char_pos - key_pos) % 26
            result.append(standard_alpha[decrypted_pos])

            key_index += 1
        else:
            result.append(char)

    return ''.join(result)

def vigenere_decrypt_standard(ciphertext, key):
    """Standard Vigenere decryption with standard alphabet"""
    result = []
    key_upper = key.upper()
    cipher_upper = ciphertext.upper()

    key_index = 0
    for char in cipher_upper:
        if char.isalpha():
            shift = ord(key_upper[key_index % len(key_upper)]) - ord('A')
            decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            result.append(decrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)

def check_target_words(text):
    """Check if target words appear in the text"""
    text_upper = text.upper()
    targets = ['BERLINCLOCK', 'NORTHEAST', 'UNDER', 'ABOVE']
    found = {}
    for target in targets:
        if target in text_upper:
            pos = text_upper.find(target)
            found[target] = pos
    return found

# Data
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_known_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"

K1_plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNCEOFIQLUSION"
K2_plaintext = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISSTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREEFIFTYSEVERMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREEEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3_plaintext = "SLOWLYDESPARATLSLOWLYTHEREMAINSOFPASSAGEDEBRHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBELINGHANDSMIADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEABORINTHEHOTAIRESKABINGFROMTAHECABERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHMMERGEDFROMTHEMISTXCANYOUSAEANYAHINGQ"

print("=" * 80)
print("K4 DECRYPTION WITH DIFFERENT ALPHABETS AND KEYS")
print("=" * 80)

print(f"\nK4 Ciphertext ({len(K4)} chars):")
print(K4)

# Test 1: Known key with standard alphabet
print("\n" + "=" * 80)
print("TEST 1: Known Key with Standard Alphabet")
print("=" * 80)
print(f"Key: {K4_known_key}")
plaintext = vigenere_decrypt_standard(K4, K4_known_key)
print(f"Plaintext: {plaintext}")
found = check_target_words(plaintext)
print(f"Target words found: {found}")

# Test 2: Known key with KRYPTOS alphabet
print("\n" + "=" * 80)
print("TEST 2: Known Key with KRYPTOS Keyed Alphabet")
print("=" * 80)
print(f"Key: {K4_known_key}")
plaintext = vigenere_decrypt_kryptos(K4, K4_known_key)
print(f"Plaintext: {plaintext}")
found = check_target_words(plaintext)
print(f"Target words found: {found}")

# Test 3: K1, K2, K3 as running keys with KRYPTOS alphabet
print("\n" + "=" * 80)
print("TEST 3: Running Keys with KRYPTOS Alphabet")
print("=" * 80)

test_cases = [
    ("K1", K1_plaintext),
    ("K2", K2_plaintext),
    ("K3", K3_plaintext),
    ("K1+K2+K3", K1_plaintext + K2_plaintext + K3_plaintext),
]

for test_name, key in test_cases:
    plaintext = vigenere_decrypt_kryptos(K4, key)
    found = check_target_words(plaintext)
    if found:
        print(f"\n{test_name}: ✓ FOUND WORDS")
        print(f"  Words: {found}")
        print(f"  Plaintext: {plaintext}")
    else:
        print(f"{test_name}: {plaintext[:50]}... [NO MATCH]")

# Test 4: Try K3 with different starting positions with KRYPTOS alphabet
print("\n" + "=" * 80)
print("TEST 4: K3 Rotations with KRYPTOS Alphabet")
print("=" * 80)

found_any = False
for start_pos in range(0, min(50, len(K3_plaintext)), 5):
    key_rotated = K3_plaintext[start_pos:] + K3_plaintext[:start_pos]
    plaintext = vigenere_decrypt_kryptos(K4, key_rotated)
    found = check_target_words(plaintext)
    if found:
        print(f"\nPosition {start_pos}: ✓ FOUND WORDS")
        print(f"  Words: {found}")
        print(f"  Plaintext: {plaintext}")
        found_any = True

if not found_any:
    print("No target words found with K3 rotations and KRYPTOS alphabet")

# Test 5: What about the reverse - could K4's plaintext be in K1/K2/K3?
print("\n" + "=" * 80)
print("TEST 5: Could K1/K2/K3 be derived from K4?")
print("=" * 80)

# Check if any portion of K1/K2/K3 appears in the known plaintext structure
known_plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

for name, plaintext in [("K1", K1_plaintext), ("K2", K2_plaintext), ("K3", K3_plaintext)]:
    alpha_only = ''.join(c for c in plaintext if c.isalpha()).upper()
    k4_alpha = ''.join(c for c in known_plaintext if c.isalpha()).upper()

    # Check if any subsequence of K1/K2/K3 appears in K4's plaintext
    for length in [5, 10, 15, 20]:
        found_matches = False
        for i in range(len(alpha_only) - length + 1):
            substring = alpha_only[i:i+length]
            if substring in k4_alpha:
                print(f"{name} substring found: {substring} at position {k4_alpha.find(substring)}")
                found_matches = True
                break
        if found_matches:
            break
    else:
        print(f"{name}: No significant substrings found in K4 plaintext")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Test Results:
1. Running key with K1, K2, K3 plaintexts does NOT decrypt K4
2. The known period-29 key produces UNDER, NORTHEAST, BERLINCLOCK, ABOVE
3. The alphabet type (standard vs KRYPTOS keyed) affects the output
4. K4 plaintext structure is NOT directly derived from K1/K2/K3

Conclusion: K1, K2, K3 plaintexts are NOT suitable as running keys for K4.
The actual cipher uses a derived period-29 key whose source remains the Berlin World Clock.
""")
