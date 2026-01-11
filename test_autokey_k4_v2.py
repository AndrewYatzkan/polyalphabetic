#!/usr/bin/env python3
"""
Test autokey cipher on K4 - refined implementation.
Tests multiple variations and directions.
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
    try:
        return KRYPTOS_ALPHABET.index(letter.upper())
    except ValueError:
        return -1


def pos_to_letter(pos):
    """Convert position to letter in KRYPTOS alphabet."""
    return KRYPTOS_ALPHABET[pos % 26]


def decrypt_autokey_plaintext_v1(ciphertext, primer):
    """
    Decrypt using plaintext autokey variant (original implementation).
    Key position i: primer[i] if i < len(primer), else plaintext[i - len(primer)]
    """
    key = list(primer.upper())
    plaintext = []

    for i, cipher_char in enumerate(ciphertext.upper()):
        if cipher_char not in KRYPTOS_ALPHABET:
            continue

        # Extend key if needed
        while i >= len(key):
            idx = i - len(key)
            if idx < len(plaintext):
                key.append(plaintext[idx])
            else:
                break

        if i >= len(key):
            break

        cipher_pos = letter_to_pos(cipher_char)
        key_pos = letter_to_pos(key[i])
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext.append(plain_char)

    return "".join(plaintext)


def decrypt_autokey_ciphertext_v1(ciphertext, primer):
    """
    Decrypt using ciphertext autokey variant.
    Key = primer + ciphertext
    """
    key = list(primer.upper()) + list(ciphertext.upper())
    plaintext = []

    for i, cipher_char in enumerate(ciphertext.upper()):
        if cipher_char not in KRYPTOS_ALPHABET:
            continue

        cipher_pos = letter_to_pos(cipher_char)
        key_pos = letter_to_pos(key[i])
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext.append(plain_char)

    return "".join(plaintext)


def encrypt_autokey_plaintext(plaintext, primer):
    """
    Encrypt using plaintext autokey.
    For comparison/testing.
    """
    key = list(primer.upper())
    plaintext_list = list(plaintext.upper())
    ciphertext = []

    for i, plain_char in enumerate(plaintext_list):
        if plain_char not in KRYPTOS_ALPHABET:
            ciphertext.append(plain_char)
            continue

        # Extend key with plaintext
        while i >= len(key):
            key.append(plaintext_list[i - len(key)])

        plain_pos = letter_to_pos(plain_char)
        key_pos = letter_to_pos(key[i])
        cipher_pos = (plain_pos + key_pos) % 26
        cipher_char = pos_to_letter(cipher_pos)
        ciphertext.append(cipher_char)

    return "".join(ciphertext)


def decrypt_autokey_plaintext_v2(ciphertext, primer):
    """
    Alternative: key might be reversed.
    """
    key = list(primer.upper()[::-1])
    plaintext = []

    for i, cipher_char in enumerate(ciphertext.upper()):
        if cipher_char not in KRYPTOS_ALPHABET:
            continue

        while i >= len(key):
            idx = i - len(key)
            if idx < len(plaintext):
                key.append(plaintext[idx])

        if i >= len(key):
            break

        cipher_pos = letter_to_pos(cipher_char)
        key_pos = letter_to_pos(key[i])
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext.append(plain_char)

    return "".join(plaintext)


def check_for_targets(plaintext):
    """Check if any target strings appear in plaintext."""
    found = []
    for target in TARGETS:
        if target in plaintext:
            found.append(target)
    return found


print("=" * 80)
print("AUTOKEY CIPHER - REFINED TEST ON K4")
print("=" * 80)
print(f"\nK4 Ciphertext: {K4}")
print(f"Length: {len(K4)}")
print(f"Alphabet: {KRYPTOS_ALPHABET}\n")

# Test plaintext autokey v1
print("\n" + "=" * 80)
print("PLAINTEXT AUTOKEY v1 (key extended by plaintext)")
print("=" * 80)

results_v1 = []
for primer in PRIMERS:
    plaintext = decrypt_autokey_plaintext_v1(K4, primer)
    found = check_for_targets(plaintext)
    results_v1.append((primer, plaintext, found))

    print(f"\nPrimer: {primer}")
    print(f"Decrypted ({len(plaintext)} chars): {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Test ciphertext autokey v1
print("\n" + "=" * 80)
print("CIPHERTEXT AUTOKEY v1 (key = primer + ciphertext)")
print("=" * 80)

results_ct = []
for primer in PRIMERS:
    plaintext = decrypt_autokey_ciphertext_v1(K4, primer)
    found = check_for_targets(plaintext)
    results_ct.append((primer, plaintext, found))

    print(f"\nPrimer: {primer}")
    print(f"Decrypted ({len(plaintext)} chars): {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Test plaintext autokey v2 (reversed primer)
print("\n" + "=" * 80)
print("PLAINTEXT AUTOKEY v2 (reversed primer)")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_autokey_plaintext_v2(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer} (reversed: {primer[::-1]})")
    print(f"Decrypted ({len(plaintext)} chars): {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Now try to verify: if we encrypt known plaintext, what key would work?
print("\n" + "=" * 80)
print("REVERSE ENGINEERING: What key produces K4 from known plaintexts?")
print("=" * 80)

# Try assuming the first few characters
test_starts = [
    ("BERLINCLOCK", 11),
    ("NORTHEAST", 9),
    ("USESOMETHINGTEMPLACETOREMEMBERTHEKEY", None),
    ("THEKEYISPALIMPSEST", None),
]

for test_plain, length in test_starts:
    if length:
        test_plain = test_plain[:length]
    print(f"\nAssuming plaintext starts with: {test_plain}")

    # What would the key be?
    derived_key = []
    for i, plain_char in enumerate(test_plain.upper()):
        if i >= len(K4):
            break
        cipher_char = K4[i]

        cipher_pos = letter_to_pos(cipher_char)
        plain_pos = letter_to_pos(plain_char)
        key_pos = (cipher_pos - plain_pos) % 26
        key_char = pos_to_letter(key_pos)
        derived_key.append(key_char)

    derived_key_str = "".join(derived_key)
    print(f"Derived key: {derived_key_str}")

    # Check if any primer is a prefix
    for primer in PRIMERS:
        if derived_key_str.startswith(primer):
            print(f"  -> Primer '{primer}' matches!")


# Summary
print("\n" + "=" * 80)
print("SUMMARY - TARGETS FOUND")
print("=" * 80)

found_any = False
for name, results in [("Plaintext Autokey v1", results_v1), ("Ciphertext Autokey v1", results_ct)]:
    print(f"\n{name}:")
    for primer, plaintext, found in results:
        if found:
            found_any = True
            print(f"  {primer}: {found}")

if not found_any:
    print("\nNo exact targets found with tested primers.")
