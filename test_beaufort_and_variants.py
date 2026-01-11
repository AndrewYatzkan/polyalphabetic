#!/usr/bin/env python3
"""
Test Beaufort cipher and other variants with running keys
"""

def beaufort_decrypt(ciphertext, key):
    """Decrypt using Beaufort cipher (reverse Vigenere)"""
    result = []
    key_upper = key.upper()
    cipher_upper = ciphertext.upper()

    key_index = 0
    for char in cipher_upper:
        if char.isalpha():
            shift = ord(key_upper[key_index % len(key_upper)]) - ord('A')
            # Beaufort: plaintext = key - ciphertext (mod 26)
            decrypted_char = chr((ord(key_upper[key_index % len(key_upper)]) - ord(char)) % 26 + ord('A'))
            result.append(decrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)

def beaufort_encrypt(plaintext, key):
    """Encrypt using Beaufort cipher"""
    result = []
    key_upper = key.upper()
    plain_upper = plaintext.upper()

    key_index = 0
    for char in plain_upper:
        if char.isalpha():
            # Beaufort: ciphertext = key - plaintext (mod 26)
            encrypted_char = chr((ord(key_upper[key_index % len(key_upper)]) - ord(char)) % 26 + ord('A'))
            result.append(encrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere cipher"""
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
    targets = ['BERLINCLOCK', 'NORTHEAST', 'BERLIN', 'CLOCK', 'LAYER', 'FOUR']
    found = {}
    for target in targets:
        if target in text_upper:
            pos = text_upper.find(target)
            found[target] = pos
    return found

# Data
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNCEOFIQLUSION"
K2 = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISSTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREEFIFTYSEVERMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREEEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3 = "SLOWLYDESPARATLSLOWLYTHEREMAINSOFPASSAGEDEBRHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBELINGHANDSMIADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEABORINTHEHOTAIRESKABINGFROMTAHECABERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHMMERGEDFROMTHEMISTXCANYOUSAEANYAHINGQ"

# Remove X's from keys
K2_no_x = K2.replace('X', '')
K3_no_x = K3.replace('X', '')

print("=" * 80)
print("BEAUFORT CIPHER TESTS")
print("=" * 80)

tests = [
    ('K1 Beaufort', K1),
    ('K2 Beaufort', K2),
    ('K2_no_x Beaufort', K2_no_x),
    ('K3 Beaufort', K3),
    ('K3_no_x Beaufort', K3_no_x),
    ('K1+K2 Beaufort', K1 + K2),
    ('K2+K3 Beaufort', K2 + K3),
    ('K1+K2+K3 Beaufort', K1 + K2 + K3),
]

for test_name, key in tests:
    plaintext = beaufort_decrypt(K4, key)
    found = check_target_words(plaintext)
    if found:
        print(f"\n{test_name}: Found {found}")
        print(f"Plaintext: {plaintext}")

print("\n" + "=" * 80)
print("BEAUFORT WITH ROTATION TESTS")
print("=" * 80)

# Try rotations with K3 Beaufort (since it's similar length to K4)
for start_pos in [0, 10, 20, 30, 50, 80, 100]:
    if start_pos >= len(K3):
        break
    key_rotated = K3[start_pos:] + K3[:start_pos]
    plaintext = beaufort_decrypt(K4, key_rotated)
    found = check_target_words(plaintext)
    if found:
        print(f"\nK3 start_pos {start_pos}: Found {found}")
        print(f"Plaintext: {plaintext}")

print("\n" + "=" * 80)
print("VARIANT: Remove vowels from key")
print("=" * 80)

for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
    # Remove vowels
    key_no_vowels = ''.join(c for c in key if c.upper() not in 'AEIOU')
    plaintext_v = vigenere_decrypt(K4, key_no_vowels)
    plaintext_b = beaufort_decrypt(K4, key_no_vowels)

    found_v = check_target_words(plaintext_v)
    found_b = check_target_words(plaintext_b)

    if found_v:
        print(f"{name} no vowels Vigenere: Found {found_v}")
        print(f"Plaintext: {plaintext_v}")
    if found_b:
        print(f"{name} no vowels Beaufort: Found {found_b}")
        print(f"Plaintext: {plaintext_b}")

print("\n" + "=" * 80)
print("VARIANT: Use only consonants from key")
print("=" * 80)

for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
    # Keep only consonants
    key_consonants = ''.join(c for c in key if c.upper() not in 'AEIOUX')
    plaintext_v = vigenere_decrypt(K4, key_consonants)
    plaintext_b = beaufort_decrypt(K4, key_consonants)

    found_v = check_target_words(plaintext_v)
    found_b = check_target_words(plaintext_b)

    if found_v:
        print(f"{name} consonants Vigenere: Found {found_v}")
        print(f"Plaintext: {plaintext_v}")
    if found_b:
        print(f"{name} consonants Beaufort: Found {found_b}")
        print(f"Plaintext: {plaintext_b}")

print("\n" + "=" * 80)
print("CHECK: Can we encrypt K1/K2/K3 with some key to get K4?")
print("=" * 80)

# Maybe K4 is actually plaintext and we need to find what it decrypts to
# Or K1/K2/K3 are keys and K4 is plaintext that needs a password
for plain_name, plaintext in [('K1', K1), ('K2', K2), ('K3', K3)]:
    # Extract alphabetic only
    plain_alpha = ''.join(c for c in plaintext if c.isalpha())
    k4_alpha = ''.join(c for c in K4 if c.isalpha())

    # Try Beaufort: if Beaufort_Encrypt(plain, key) = k4_alpha
    # Then key = plain XOR k4_alpha
    print(f"\nIf {plain_name} encrypts to K4 with some key (Beaufort):")

    if len(plain_alpha) >= len(k4_alpha):
        key = []
        for i in range(len(k4_alpha)):
            # Beaufort: cipher = key - plain => key = cipher + plain
            shift = (ord(k4_alpha[i]) + ord(plain_alpha[i])) % 26
            key.append(chr(shift + ord('A')))
        key_str = ''.join(key)
        print(f"Derived key: {key_str[:50]}...")

        # Verify by encrypting
        encrypted = beaufort_encrypt(plain_alpha, key_str)
        if encrypted == k4_alpha:
            print(f"SUCCESS! {plain_name} with Beaufort key {key_str} encrypts to K4")
        else:
            print(f"Verification failed")

print("\n" + "=" * 80)
print("BEAUFORT TESTS COMPLETE")
print("=" * 80)
