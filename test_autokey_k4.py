#!/usr/bin/env python3
"""
Test autokey cipher on K4 of KRYPTOS puzzle.
Both plaintext autokey and ciphertext autokey variants.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

PRIMERS = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "BERLIN",
    "BERLINCLOCK",
    "NORTHEAST",
    "UNDER",
    "ABOVE",
    "SHADOW",
    "CLOCK"
]

TARGETS = ["BERLINCLOCK", "NORTHEAST"]


def letter_to_pos(letter):
    """Convert letter to position in KRYPTOS alphabet."""
    return KRYPTOS_ALPHABET.index(letter.upper())


def pos_to_letter(pos):
    """Convert position to letter in KRYPTOS alphabet."""
    return KRYPTOS_ALPHABET[pos % 26]


def decrypt_autokey_plaintext(ciphertext, primer):
    """
    Decrypt using plaintext autokey variant.
    Key = primer + plaintext
    """
    key = primer.upper()
    plaintext = ""

    for i, cipher_char in enumerate(ciphertext.upper()):
        if cipher_char not in KRYPTOS_ALPHABET:
            continue

        # Get key character
        if i < len(key):
            key_char = key[i]
        else:
            # Key is extended by plaintext
            if i - len(key) < len(plaintext):
                key_char = plaintext[i - len(key)]
            else:
                key_char = "?"

        if key_char == "?":
            break

        cipher_pos = letter_to_pos(cipher_char)
        key_pos = letter_to_pos(key_char)
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext += plain_char

        # Extend key with plaintext if needed
        if i >= len(key) and len(plaintext) > len(key):
            key = key + plaintext[len(key):]

    return plaintext


def decrypt_autokey_ciphertext(ciphertext, primer):
    """
    Decrypt using ciphertext autokey variant.
    Key = primer + ciphertext
    """
    key = primer.upper() + ciphertext.upper()
    plaintext = ""

    for i, cipher_char in enumerate(ciphertext.upper()):
        if cipher_char not in KRYPTOS_ALPHABET:
            continue

        key_char = key[i]
        cipher_pos = letter_to_pos(cipher_char)
        key_pos = letter_to_pos(key_char)
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext += plain_char

    return plaintext


def check_for_targets(plaintext):
    """Check if any target strings appear in plaintext."""
    found = []
    for target in TARGETS:
        if target in plaintext:
            found.append(target)
    return found


print("=" * 80)
print("AUTOKEY CIPHER TEST ON K4")
print("=" * 80)
print(f"\nK4 Ciphertext: {K4}")
print(f"Length: {len(K4)}")
print(f"Alphabet: {KRYPTOS_ALPHABET}\n")

# Test plaintext autokey
print("\n" + "=" * 80)
print("PLAINTEXT AUTOKEY (key extended by plaintext)")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_autokey_plaintext(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer}")
    print(f"Decrypted: {plaintext}")
    if found:
        print(f">>> FOUND: {found}")
    else:
        print(f"  (no targets found)")


# Test ciphertext autokey
print("\n" + "=" * 80)
print("CIPHERTEXT AUTOKEY (key extended by ciphertext)")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_autokey_ciphertext(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer}")
    print(f"Decrypted: {plaintext}")
    if found:
        print(f">>> FOUND: {found}")
    else:
        print(f"  (no targets found)")


# Test some variations: what if we need to search for partial words?
print("\n" + "=" * 80)
print("SEARCHING FOR PARTIAL MATCHES")
print("=" * 80)

def find_partial_matches(plaintext, min_length=4):
    """Find interesting substrings."""
    results = []
    for target in TARGETS:
        # Search for substrings
        for i in range(len(plaintext) - len(target) + 1):
            substr = plaintext[i:i+len(target)]
            if substr.startswith(target[:4]) or target.startswith(substr[:4]):
                results.append((i, substr))
    return results

print("\nPlaintext Autokey - Partial Matches:")
for primer in PRIMERS:
    plaintext = decrypt_autokey_plaintext(K4, primer)
    matches = find_partial_matches(plaintext)
    if matches:
        print(f"\n{primer}:")
        for pos, match in matches[:5]:  # Show first 5
            print(f"  pos {pos}: {match}")

print("\nCiphertext Autokey - Partial Matches:")
for primer in PRIMERS:
    plaintext = decrypt_autokey_ciphertext(K4, primer)
    matches = find_partial_matches(plaintext)
    if matches:
        print(f"\n{primer}:")
        for pos, match in matches[:5]:  # Show first 5
            print(f"  pos {pos}: {match}")
