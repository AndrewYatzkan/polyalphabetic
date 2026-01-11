#!/usr/bin/env python3
"""
Comprehensive autokey testing - trying every possible variation.
Including: reverse keys, different modes, and more.
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


def letter_to_pos(letter, alphabet=KRYPTOS_ALPHABET):
    try:
        return alphabet.index(letter.upper())
    except ValueError:
        return -1


def pos_to_letter(pos, alphabet=KRYPTOS_ALPHABET):
    return alphabet[pos % len(alphabet)]


def decrypt_vigenere(ciphertext, key, alphabet=KRYPTOS_ALPHABET):
    """Standard Vigenere decryption (for comparison)."""
    key_index = 0
    plaintext = []
    for cipher_char in ciphertext.upper():
        if cipher_char not in alphabet:
            continue
        cipher_pos = letter_to_pos(cipher_char, alphabet)
        key_pos = letter_to_pos(key[key_index % len(key)], alphabet)
        plain_pos = (cipher_pos - key_pos) % len(alphabet)
        plaintext.append(pos_to_letter(plain_pos, alphabet))
        key_index += 1
    return "".join(plaintext)


def decrypt_autokey_variant(ciphertext, primer, mode="plaintext_extend", alphabet=KRYPTOS_ALPHABET):
    """
    Flexible autokey decryption with different modes.
    mode = "plaintext_extend": key = primer + plaintext
    mode = "ciphertext_extend": key = primer + ciphertext
    mode = "alternating": alternate between primer and plaintext
    mode = "mixed": primer + plaintext + plaintext2
    """
    if mode == "plaintext_extend":
        key = list(primer.upper())
        plaintext = []
        for i, cipher_char in enumerate(ciphertext.upper()):
            if cipher_char not in alphabet:
                continue
            while i >= len(key):
                idx = i - len(key)
                if idx < len(plaintext):
                    key.append(plaintext[idx])
            if i >= len(key):
                break
            cipher_pos = letter_to_pos(cipher_char, alphabet)
            key_pos = letter_to_pos(key[i], alphabet)
            plain_pos = (cipher_pos - key_pos) % len(alphabet)
            plaintext.append(pos_to_letter(plain_pos, alphabet))
        return "".join(plaintext)

    elif mode == "ciphertext_extend":
        key = list(primer.upper()) + list(ciphertext.upper())
        plaintext = []
        for i, cipher_char in enumerate(ciphertext.upper()):
            if cipher_char not in alphabet:
                continue
            cipher_pos = letter_to_pos(cipher_char, alphabet)
            key_pos = letter_to_pos(key[i], alphabet)
            plain_pos = (cipher_pos - key_pos) % len(alphabet)
            plaintext.append(pos_to_letter(plain_pos, alphabet))
        return "".join(plaintext)

    elif mode == "alternating":
        key = []
        for i, c in enumerate(primer.upper()):
            key.append(c)
        plaintext = []
        ct_idx = 0
        for i, cipher_char in enumerate(ciphertext.upper()):
            if cipher_char not in alphabet:
                continue
            # Extend key with alternating primer and plaintext
            while ct_idx >= len(key):
                key.append(primer[ct_idx % len(primer)].upper())
                if len(plaintext) > 0:
                    key.append(plaintext[ct_idx % len(plaintext)])
            cipher_pos = letter_to_pos(cipher_char, alphabet)
            key_pos = letter_to_pos(key[ct_idx], alphabet)
            plain_pos = (cipher_pos - key_pos) % len(alphabet)
            plaintext.append(pos_to_letter(plain_pos, alphabet))
            ct_idx += 1
        return "".join(plaintext)

    return ""


def find_substring_in_decryption(ciphertext, primer, substring, alphabet=KRYPTOS_ALPHABET):
    """
    Try to find where a substring would appear if we decrypt with a given primer.
    Returns the key that would produce this substring at the start.
    """
    derived_key = []
    for i, plain_char in enumerate(substring.upper()):
        if i >= len(ciphertext):
            break
        cipher_char = ciphertext[i]
        cipher_pos = letter_to_pos(cipher_char, alphabet)
        plain_pos = letter_to_pos(plain_char, alphabet)
        key_pos = (cipher_pos - plain_pos) % len(alphabet)
        key_char = pos_to_letter(key_pos, alphabet)
        derived_key.append(key_char)
    return "".join(derived_key)


print("=" * 80)
print("COMPREHENSIVE AUTOKEY TEST")
print("=" * 80)

# Standard Vigenere for comparison
print("\n" + "=" * 80)
print("STANDARD VIGENERE (for comparison - non-autokey)")
print("=" * 80)

found_any_vigenere = False
for primer in PRIMERS:
    plaintext = decrypt_vigenere(K4, primer)
    for target in TARGETS:
        if target in plaintext:
            print(f"\n{primer}: FOUND {target}")
            print(f"Plaintext: {plaintext}")
            found_any_vigenere = True

if not found_any_vigenere:
    print("(No targets found with standard Vigenere)")


# Different autokey modes
print("\n" + "=" * 80)
print("DIFFERENT AUTOKEY MODES")
print("=" * 80)

modes = ["plaintext_extend", "ciphertext_extend", "alternating"]
results_by_mode = {}

for mode in modes:
    print(f"\nMode: {mode}")
    found_any = False
    for primer in PRIMERS:
        plaintext = decrypt_autokey_variant(K4, primer, mode=mode)
        for target in TARGETS:
            if target in plaintext:
                print(f"  {primer}: FOUND {target}")
                print(f"  Plaintext: {plaintext}")
                found_any = True
        results_by_mode[f"{mode}_{primer}"] = plaintext

    if not found_any:
        print(f"  (No targets found)")


# Reverse engineering: what key would produce each target?
print("\n" + "=" * 80)
print("REVERSE ENGINEERING - Derived keys for each target")
print("=" * 80)

for target in TARGETS:
    print(f"\nTarget: {target}")
    derived = find_substring_in_decryption(K4, None, target)
    print(f"Key needed at start: {derived}")
    print(f"First 15 chars: {derived[:15]}")

    # Check if any primer is in this key
    for primer in PRIMERS:
        if primer.upper() in derived:
            print(f"  -> Contains primer: {primer}")
        if derived.startswith(primer.upper()):
            print(f"  -> Starts with: {primer}")


# Try all primers at different positions
print("\n" + "=" * 80)
print("SEARCHING FOR TARGETS AT DIFFERENT POSITIONS")
print("=" * 80)

for primer in PRIMERS[:3]:  # Just test a few
    plaintext = decrypt_autokey_variant(K4, primer, mode="plaintext_extend")
    print(f"\nPrimer: {primer}")
    print(f"Full plaintext: {plaintext}")
    for target in TARGETS:
        for i in range(len(plaintext) - len(target) + 1):
            substr = plaintext[i:i+len(target)]
            if substr == target:
                print(f"  FOUND {target} at position {i}")


# Check if targets appear when using them as keys
print("\n" + "=" * 80)
print("WHAT IF: Using targets as keys")
print("=" * 80)

for target in TARGETS:
    plaintext = decrypt_autokey_variant(K4, target, mode="plaintext_extend")
    print(f"\nUsing '{target}' as key:")
    print(f"Plaintext: {plaintext}")


# Try with key reversal
print("\n" + "=" * 80)
print("REVERSE KEY VARIANTS")
print("=" * 80)

for primer in PRIMERS[:3]:
    plaintext = decrypt_autokey_variant(K4, primer[::-1], mode="plaintext_extend")
    print(f"\nPrimer reversed ({primer[::-1]}):")
    print(f"Plaintext: {plaintext}")
    for target in TARGETS:
        if target in plaintext:
            print(f"  >>> FOUND {target}")
