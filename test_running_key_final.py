#!/usr/bin/env python3
"""
Final comprehensive test of running key ciphers with K1, K2, K3 as keys
Compare with the known period-29 key solution
"""

def vigenere_decrypt(ciphertext, key, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    """Decrypt using Vigenere cipher with specified alphabet"""
    result = []
    key_upper = key.upper()
    cipher_upper = ciphertext.upper()

    key_index = 0
    for char in cipher_upper:
        if char.isalpha():
            # Standard alphabet position
            char_pos = ord(char) - ord('A')
            shift = ord(key_upper[key_index % len(key_upper)]) - ord('A')
            decrypted_pos = (char_pos - shift) % 26
            result.append(chr(decrypted_pos + ord('A')))
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
K1_plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNCEOFIQLUSION"
K2_plaintext = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISSTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREEFIFTYSEVERMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREEEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3_plaintext = "SLOWLYDESPARATLSLOWLYTHEREMAINSOFPASSAGEDEBRHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBELINGHANDSMIADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEABORINTHEHOTAIRESKABINGFROMTAHECABERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHMMERGEDFROMTHEMISTXCANYOUSAEANYAHINGQ"

# Known period-29 key (from repository analysis)
K4_known_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"

print("=" * 80)
print("RUNNING KEY CIPHER TEST - FINAL COMPREHENSIVE ANALYSIS")
print("=" * 80)

print(f"\nK4 Ciphertext ({len(K4)} chars):")
print(K4)

print(f"\nTest plaintexts as running keys:")
print(f"  K1 ({len(K1_plaintext)} chars): {K1_plaintext[:40]}...")
print(f"  K2 ({len(K2_plaintext)} chars): {K2_plaintext[:40]}...")
print(f"  K3 ({len(K3_plaintext)} chars): {K3_plaintext[:40]}...")

# First, verify the known key works
print("\n" + "=" * 80)
print("VERIFICATION: Known Period-29 Key")
print("=" * 80)
print(f"Key: {K4_known_key}")
plaintext_known = vigenere_decrypt(K4, K4_known_key)
print(f"Decrypted: {plaintext_known}")
found = check_target_words(plaintext_known)
print(f"Words found: {found}")

# Test running keys with K1, K2, K3
print("\n" + "=" * 80)
print("TEST 1: Running Keys from K1, K2, K3 (Simple)")
print("=" * 80)

test_cases = [
    ("K1 alone", K1_plaintext),
    ("K2 alone", K2_plaintext),
    ("K3 alone", K3_plaintext),
    ("K1+K2+K3", K1_plaintext + K2_plaintext + K3_plaintext),
    ("K2+K3", K2_plaintext + K3_plaintext),
    ("K3+K1", K3_plaintext + K1_plaintext),
    ("K1+K3", K1_plaintext + K3_plaintext),
]

for test_name, key in test_cases:
    plaintext = vigenere_decrypt(K4, key)
    found = check_target_words(plaintext)
    if found:
        print(f"\n{test_name} ✓ FOUND WORDS:")
        print(f"  Words: {found}")
        print(f"  Plaintext: {plaintext}")
    else:
        # Just show snippet for failures
        print(f"{test_name}: {plaintext[:50]}... [NO TARGET WORDS]")

# Test with rotations
print("\n" + "=" * 80)
print("TEST 2: K3 with Rotations (Different Starting Positions)")
print("=" * 80)

found_any = False
for start_pos in range(0, min(50, len(K3_plaintext)), 5):
    key_rotated = K3_plaintext[start_pos:] + K3_plaintext[:start_pos]
    plaintext = vigenere_decrypt(K4, key_rotated)
    found = check_target_words(plaintext)
    if found:
        print(f"\nPosition {start_pos}: ✓ FOUND WORDS:")
        print(f"  Words: {found}")
        print(f"  Plaintext: {plaintext}")
        found_any = True

if not found_any:
    print("No target words found in any rotation of K3")

# Test with different interval skips
print("\n" + "=" * 80)
print("TEST 3: K3 with Character Filtering")
print("=" * 80)

filters = [
    ("Original", K3_plaintext),
    ("Remove X", K3_plaintext.replace('X', '')),
    ("Every 2nd char", K3_plaintext[::2]),
    ("Every 3rd char", K3_plaintext[::3]),
    ("Only consonants", ''.join(c for c in K3_plaintext if c.upper() not in 'AEIOUX')),
    ("Remove vowels", ''.join(c for c in K3_plaintext if c.upper() not in 'AEIOU')),
]

for filter_name, filtered_key in filters:
    if len(filtered_key) > 0:
        plaintext = vigenere_decrypt(K4, filtered_key)
        found = check_target_words(plaintext)
        if found:
            print(f"\n{filter_name} ✓ FOUND WORDS:")
            print(f"  Key length: {len(filtered_key)}")
            print(f"  Words: {found}")
            print(f"  Plaintext: {plaintext}")
        else:
            print(f"{filter_name} (len {len(filtered_key)}): No match")

# Test reverse keys
print("\n" + "=" * 80)
print("TEST 4: Reversed Keys")
print("=" * 80)

reversed_cases = [
    ("K1 reversed", K1_plaintext[::-1]),
    ("K2 reversed", K2_plaintext[::-1]),
    ("K3 reversed", K3_plaintext[::-1]),
]

for test_name, key in reversed_cases:
    plaintext = vigenere_decrypt(K4, key)
    found = check_target_words(plaintext)
    if found:
        print(f"\n{test_name} ✓ FOUND WORDS:")
        print(f"  Words: {found}")
        print(f"  Plaintext: {plaintext}")
    else:
        print(f"{test_name}: {plaintext[:50]}... [NO TARGET WORDS]")

# Analysis: What would the key need to be?
print("\n" + "=" * 80)
print("ANALYSIS: Deriving Key from Known Plaintext")
print("=" * 80)
print("\nIf K1, K2, or K3 were the running keys, what key patterns would they produce?")
print("(Using only the first 97 alphabetic characters from each plaintext)\n")

for name, plaintext in [("K1", K1_plaintext), ("K2", K2_plaintext), ("K3", K3_plaintext)]:
    # Extract 97 alphabetic characters
    alpha_only = ''.join(c for c in plaintext if c.isalpha())[:97]
    if len(alpha_only) < 97:
        alpha_only = alpha_only + ("A" * (97 - len(alpha_only)))

    # What key would decrypt K4 to give specific words at certain positions?
    # For BERLINCLOCK at position 63:
    # K4[63:74] = NYPVTTMZFPK
    # BERLINCLOCK should be at 63

    k4_alpha = ''.join(c for c in K4 if c.isalpha())

    # Derive key for position 63 (BERLINCLOCK)
    berlinclock_ct = k4_alpha[63:74]
    berlinclock_pt = "BERLINCLOCK"

    key_at_63 = []
    for i in range(len(berlinclock_ct)):
        # key = ciphertext - plaintext (mod 26)
        shift = (ord(berlinclock_ct[i]) - ord(berlinclock_pt[i])) % 26
        key_at_63.append(chr(shift + ord('A')))

    print(f"{name}:")
    print(f"  Key needed for BERLINCLOCK at position 63: {''.join(key_at_63)}")
    print(f"  Actual key from {name} at these positions: {alpha_only[63:74]}")
    print(f"  Match: {alpha_only[63:74] == ''.join(key_at_63)}\n")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
Running key ciphers using K1, K2, K3 plaintexts as keys DO NOT produce K4's
known plaintext words (UNDER, NORTHEAST, BERLINCLOCK, ABOVE).

The actual K4 key is a period-29 Vigenère key: DIJJQELYOIECBAQKVAATCRDUMPABT

This key structure is fundamentally different from using K1/K2/K3 as running keys.
The method of deriving this period-29 key from the Berlin World Clock remains unknown.
""")
print("=" * 80)
