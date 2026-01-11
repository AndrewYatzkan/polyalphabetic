#!/usr/bin/env python3
"""
Extended running key cipher tests with multiple approaches
"""

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

def vigenere_encrypt(plaintext, key):
    """Encrypt using Vigenere cipher"""
    result = []
    key_upper = key.upper()
    plain_upper = plaintext.upper()

    key_index = 0
    for char in plain_upper:
        if char.isalpha():
            shift = ord(key_upper[key_index % len(key_upper)]) - ord('A')
            encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            result.append(encrypted_char)
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

def count_english_words(text, wordlist=None):
    """Count English-like words in text"""
    if not wordlist:
        common = {'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW', 'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'LIKE', 'THAN', 'THEM', 'THEN', 'TIME', 'VERY', 'WHEN', 'WILL', 'COME', 'HERE', 'KNOW', 'MANY', 'OVER', 'SUCH', 'TAKE', 'EVEN', 'FIND', 'GIVE', 'MAKE', 'WELL', 'YEAR', 'CALL', 'EACH', 'FEEL', 'HAND', 'HIGH', 'KEEP', 'LAST', 'LONG', 'MADE', 'MOST', 'MUCH', 'MUST', 'NAME', 'ONLY', 'OPEN', 'PART', 'SAME', 'SEEM', 'TURN', 'WANT', 'WORK', 'WORLD'}
        wordlist = common

    text_upper = text.upper()
    words = text_upper.split()
    count = sum(1 for w in words if w in wordlist)
    return count

# Data
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNCEOFIQLUSION"
K2 = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISSTHEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGREEFIFTYSEVERMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGREEEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K3 = "SLOWLYDESPARATLSLOWLYTHEREMAINSOFPASSAGEDEBRHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBELINGHANDSMIADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEABORINTHEHOTAIRESKABINGFROMTAHECABERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHMMERGEDFROMTHEMISTXCANYOUSAEANYAHINGQ"

print("=" * 80)
print("EXTENDED RUNNING KEY TESTS")
print("=" * 80)

# Test if K1/K2/K3 appear in K4 as plaintext
print("\nTest: Check if K1, K2, K3 appear in K4")
K4_upper = K4.upper()
for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
    key_upper = key.upper()
    if key_upper in K4_upper:
        print(f"{name} found in K4")
    else:
        print(f"{name} NOT in K4")

# Test: Maybe K4 is encrypted version of K1/K2/K3 and we need to find the key
print("\n" + "=" * 80)
print("Test: Is K4 the Vigenere encryption of K1/K2/K3?")
print("=" * 80)

# Check if K1 encrypted with some key gives K4
for test_name, plaintext in [('K1', K1), ('K2', K2), ('K3', K3)]:
    # Try to find what key would encrypt plaintext to K4
    if len(plaintext) >= len(K4):
        # Extract only alphabetic chars from both
        plain_alpha = ''.join(c for c in plaintext if c.isalpha())
        k4_alpha = ''.join(c for c in K4 if c.isalpha())

        if len(plain_alpha) >= len(k4_alpha):
            print(f"\nTrying {test_name} as plaintext to produce K4:")
            # Calculate the key: K4 = Encrypt(plaintext, key) => key = K4 - plaintext
            key = []
            for i in range(min(len(k4_alpha), len(plain_alpha))):
                shift = (ord(k4_alpha[i]) - ord(plain_alpha[i])) % 26
                key.append(chr(shift + ord('A')))
            key_str = ''.join(key)
            print(f"Derived key: {key_str[:50]}...")

            # Verify
            encrypted = vigenere_encrypt(plain_alpha, key_str)
            if encrypted == k4_alpha:
                print(f"SUCCESS! {test_name} with key {key_str} encrypts to K4")

# Test: Try reversing the keys
print("\n" + "=" * 80)
print("Test: Reverse key approaches")
print("=" * 80)

for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
    reversed_key = key[::-1]
    plaintext = vigenere_decrypt(K4, reversed_key)
    found = check_target_words(plaintext)
    if found:
        print(f"\n{name} reversed: Found {found}")
        print(f"Plaintext: {plaintext}")

# Test: Try every other character of keys
print("\n" + "=" * 80)
print("Test: Every other character of keys")
print("=" * 80)

for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
    for skip in [2, 3]:
        key_subset = key[::skip]
        plaintext = vigenere_decrypt(K4, key_subset)
        found = check_target_words(plaintext)
        if found:
            print(f"\n{name} every {skip}th char: Found {found}")
            print(f"Plaintext: {plaintext}")

# Test: Try Caesar shift on K4 first
print("\n" + "=" * 80)
print("Test: Caesar shift + running key")
print("=" * 80)

for shift in range(1, 5):
    caesar_shifted = ''.join(chr((ord(c) - ord('A') + shift) % 26 + ord('A')) if c.isalpha() else c for c in K4.upper())

    for name, key in [('K1', K1), ('K2', K2), ('K3', K3)]:
        plaintext = vigenere_decrypt(caesar_shifted, key)
        found = check_target_words(plaintext)
        if found:
            print(f"\nShift {shift} + {name}: Found {found}")
            print(f"Plaintext: {plaintext}")

print("\n" + "=" * 80)
print("EXTENDED TESTS COMPLETE")
print("=" * 80)
