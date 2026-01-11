#!/usr/bin/env python3
"""
Test autokey cipher on K4 - more variations.
Testing reverse operations, different alphabets, and composite keys.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

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
    """Convert letter to position."""
    try:
        return alphabet.index(letter.upper())
    except ValueError:
        return -1


def pos_to_letter(pos, alphabet=KRYPTOS_ALPHABET):
    """Convert position to letter."""
    return alphabet[pos % len(alphabet)]


def decrypt_autokey_subtract_reverse(ciphertext, primer):
    """
    Autokey where subtraction order is reversed: P = K - C instead of C - K
    """
    key = list(primer.upper())
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
        # Reverse subtraction
        plain_pos = (key_pos - cipher_pos) % 26
        plain_char = pos_to_letter(plain_pos)
        plaintext.append(plain_char)

    return "".join(plaintext)


def decrypt_with_standard_alphabet(ciphertext, primer):
    """
    Try with standard A-Z alphabet instead of KRYPTOS alphabet.
    First convert K4 to standard alphabet assuming direct substitution.
    """
    # Map KRYPTOS alphabet to standard
    mapping = {}
    for i, char in enumerate(KRYPTOS_ALPHABET):
        mapping[char] = STANDARD_ALPHABET[i]

    # Convert ciphertext
    standard_ct = "".join(mapping.get(c, c) for c in ciphertext.upper())
    std_primer = "".join(mapping.get(c, c) for c in primer.upper())

    # Decrypt using standard alphabet
    key = list(std_primer)
    plaintext = []

    for i, cipher_char in enumerate(standard_ct):
        if cipher_char not in STANDARD_ALPHABET:
            continue

        while i >= len(key):
            idx = i - len(key)
            if idx < len(plaintext):
                key.append(plaintext[idx])

        if i >= len(key):
            break

        cipher_pos = letter_to_pos(cipher_char, STANDARD_ALPHABET)
        key_pos = letter_to_pos(key[i], STANDARD_ALPHABET)
        plain_pos = (cipher_pos - key_pos) % 26
        plain_char = pos_to_letter(plain_pos, STANDARD_ALPHABET)
        plaintext.append(plain_char)

    return "".join(plaintext)


def decrypt_bidirectional(ciphertext, primer):
    """
    Try decrypting by processing from end backwards.
    """
    key = list(primer.upper())
    ct_reversed = ciphertext.upper()[::-1]
    plaintext = []

    for i, cipher_char in enumerate(ct_reversed):
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

    return "".join(plaintext)[::-1]


def check_for_targets(plaintext):
    """Check if any target strings appear in plaintext."""
    found = []
    for target in TARGETS:
        if target in plaintext:
            found.append(target)
    return found


print("=" * 80)
print("AUTOKEY CIPHER - ADDITIONAL VARIATIONS ON K4")
print("=" * 80)

# Test reverse subtraction
print("\n" + "=" * 80)
print("PLAINTEXT AUTOKEY - REVERSE SUBTRACTION (P = K - C)")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_autokey_subtract_reverse(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer}")
    print(f"Decrypted: {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Test with standard alphabet
print("\n" + "=" * 80)
print("AUTOKEY WITH STANDARD ALPHABET (A-Z)")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_with_standard_alphabet(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer}")
    print(f"Decrypted: {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Test bidirectional
print("\n" + "=" * 80)
print("BIDIRECTIONAL - DECRYPT FROM END TO START")
print("=" * 80)

for primer in PRIMERS:
    plaintext = decrypt_bidirectional(K4, primer)
    found = check_for_targets(plaintext)

    print(f"\nPrimer: {primer}")
    print(f"Decrypted: {plaintext}")
    if found:
        print(f">>> FOUND: {found}")


# Test if any decryption ends with targets
print("\n" + "=" * 80)
print("SEARCHING FOR TARGETS AT END OR IN MIDDLE")
print("=" * 80)

all_results = {}
methods = [
    ("Plaintext Autokey Std Subtract", decrypt_autokey_subtract_reverse),
    ("Plaintext Autokey Std Alphabet", decrypt_with_standard_alphabet),
]

for method_name, method_func in methods:
    print(f"\n{method_name}:")
    for primer in PRIMERS:
        plaintext = method_func(K4, primer)
        all_results[f"{method_name}_{primer}"] = plaintext

        # Check for partial matches (last 20 chars)
        if plaintext.endswith("BERLINCLOCK") or plaintext.endswith("NORTHEAST"):
            print(f"  {primer}: FOUND at end")
        elif "BERLINCLOCK" in plaintext or "NORTHEAST" in plaintext:
            print(f"  {primer}: FOUND in middle")

        # Check for reversed targets
        if plaintext.endswith("KCOLCNILREB") or plaintext.endswith("TSAEHTRON"):
            print(f"  {primer}: FOUND (reversed) at end")


# Test with all primers concatenated as a longer key
print("\n" + "=" * 80)
print("BONUS: COMPOSITE KEY (all primers concatenated)")
print("=" * 80)

composite_key = "".join(PRIMERS)
print(f"\nComposite key: {composite_key} (length {len(composite_key)})")

# Just decrypt with this
key = list(composite_key)
plaintext = []
for i, cipher_char in enumerate(K4.upper()):
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

composite_result = "".join(plaintext)
print(f"Decrypted: {composite_result}")
if "BERLINCLOCK" in composite_result or "NORTHEAST" in composite_result:
    print(f">>> FOUND TARGETS!")
