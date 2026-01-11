#!/usr/bin/env python3
"""
Test running key cipher using K1, K2, K3 plaintexts as the key for K4
"""

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere cipher"""
    result = []
    key_upper = key.upper()
    cipher_upper = ciphertext.upper()

    key_index = 0
    for char in cipher_upper:
        if char.isalpha():
            # Get shift from key
            shift = ord(key_upper[key_index % len(key_upper)]) - ord('A')
            # Decrypt
            decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            result.append(decrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)

def check_target_words(text):
    """Check if target words appear in the text"""
    text_upper = text.upper()
    targets = ['BERLINCLOCK', 'NORTHEAST', 'BERLIN', 'CLOCK']
    found = {}
    for target in targets:
        if target in text_upper:
            pos = text_upper.find(target)
            found[target] = pos
    return found

# K4 ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# K1, K2, K3 plaintexts (to be used as keys)
K1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNCEOFIQLUSION"
K2 = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISSTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREEFIFTYSEVERMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREEEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3 = "SLOWLYDESPARATLSLOWLYTHEREMAINSOFPASSAGEDEBRHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBELINGHANDSMIADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEABORINTHEHOTAIRESKABINGFROMTAHECABERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHMMERGEDFROMTHEMISTXCANYOUSAEANYAHINGQ"

print("=" * 80)
print("RUNNING KEY CIPHER TESTS")
print("=" * 80)
print(f"\nK4 ciphertext ({len(K4)} chars):")
print(K4)
print(f"\nK1 plaintext ({len(K1)} chars): {K1[:50]}...")
print(f"K2 plaintext ({len(K2)} chars): {K2[:50]}...")
print(f"K3 plaintext ({len(K3)} chars): {K3[:50]}...")

# Test 1: K1 + K2 + K3 concatenated
print("\n" + "=" * 80)
print("TEST 1: K1 + K2 + K3 concatenated as running key")
print("=" * 80)
K123 = K1 + K2 + K3
print(f"Combined key length: {len(K123)} chars")
plaintext = vigenere_decrypt(K4, K123)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

# Test 2: K3 alone (similar length to K4)
print("\n" + "=" * 80)
print("TEST 2: K3 alone as running key")
print("=" * 80)
print(f"K3 length: {len(K3)} chars (K4 length: {len(K4)} chars)")
plaintext = vigenere_decrypt(K4, K3)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

# Test 3: K1 alone
print("\n" + "=" * 80)
print("TEST 3: K1 alone as running key")
print("=" * 80)
print(f"K1 length: {len(K1)} chars (K4 length: {len(K4)} chars)")
plaintext = vigenere_decrypt(K4, K1)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

# Test 4: K2 alone
print("\n" + "=" * 80)
print("TEST 4: K2 alone as running key")
print("=" * 80)
print(f"K2 length: {len(K2)} chars (K4 length: {len(K4)} chars)")
plaintext = vigenere_decrypt(K4, K2)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

# Test 5: Try different starting positions with K3
print("\n" + "=" * 80)
print("TEST 5: K3 at different starting positions")
print("=" * 80)
for start_pos in [0, 5, 10, 15, 20, 30, 50, 100, 150]:
    if start_pos >= len(K3):
        break
    key_rotated = K3[start_pos:] + K3[:start_pos]
    plaintext = vigenere_decrypt(K4, key_rotated)
    found = check_target_words(plaintext)
    if found:
        print(f"Position {start_pos}: Found {found}")
        print(f"  Plaintext: {plaintext}")

# Test 6: Try different starting positions with K123
print("\n" + "=" * 80)
print("TEST 6: K1+K2+K3 at different starting positions")
print("=" * 80)
for start_pos in [0, 10, 20, 50, 100, 200, 300, 400]:
    if start_pos >= len(K123):
        break
    key_rotated = K123[start_pos:] + K123[:start_pos]
    plaintext = vigenere_decrypt(K4, key_rotated)
    found = check_target_words(plaintext)
    if found:
        print(f"Position {start_pos}: Found {found}")
        print(f"  Plaintext: {plaintext}")

# Test 7: Try K2 + K3 concatenated
print("\n" + "=" * 80)
print("TEST 7: K2 + K3 concatenated as running key")
print("=" * 80)
K23 = K2 + K3
print(f"Combined key length: {len(K23)} chars")
plaintext = vigenere_decrypt(K4, K23)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

# Test 8: Try K1 + K3 concatenated
print("\n" + "=" * 80)
print("TEST 8: K1 + K3 concatenated as running key")
print("=" * 80)
K13 = K1 + K3
print(f"Combined key length: {len(K13)} chars")
plaintext = vigenere_decrypt(K4, K13)
print(f"Decrypted: {plaintext}")
found = check_target_words(plaintext)
if found:
    print(f"Found target words: {found}")
else:
    print("No target words found")

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
