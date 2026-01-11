#!/usr/bin/env python3
"""
Test autokey with word matching - look for any English words in output.
Also test with expanded primer combinations.
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

# Common KRYPTOS-related words and clues
COMMON_WORDS = [
    "THE", "AND", "FOR", "YOU",
    "BERLINCLOCK", "NORTHEAST",
    "CLOCK", "BERLIN", "KRYPTOS",
    "UNDERABOVE", "SHADOWOFNIGHT",
    "PALIMPSEST", "ABSCISSA",
    "COORDINATES", "GRANITE",
    "WATER", "TREE",
]


def letter_to_pos(letter, alphabet=KRYPTOS_ALPHABET):
    try:
        return alphabet.index(letter.upper())
    except ValueError:
        return -1


def pos_to_letter(pos, alphabet=KRYPTOS_ALPHABET):
    return alphabet[pos % len(alphabet)]


def decrypt_autokey(ciphertext, primer, alphabet=KRYPTOS_ALPHABET):
    """Plaintext autokey decryption."""
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


def score_plaintext(text):
    """Score plaintext based on how many recognizable patterns it contains."""
    score = 0
    text_upper = text.upper()

    # Look for vowel patterns
    vowels = "AEIO"
    vowel_count = sum(1 for c in text_upper if c in vowels and c in KRYPTOS_ALPHABET)
    if len(text) > 0:
        vowel_ratio = vowel_count / len(text)
        # Normal English is about 40% vowels
        if 0.25 < vowel_ratio < 0.55:
            score += 2

    # Look for common two-letter combinations
    common_pairs = ["TH", "HE", "AN", "OR", "IN", "AT", "ER", "EN"]
    for pair in common_pairs:
        score += text_upper.count(pair)

    # Look for doubled letters (common in English)
    for i in range(len(text_upper) - 1):
        if text_upper[i] == text_upper[i+1]:
            score += 1

    return score


print("=" * 80)
print("AUTOKEY WITH WORD MATCHING")
print("=" * 80)

all_decryptions = []

for primer in PRIMERS:
    plaintext = decrypt_autokey(K4, primer)
    score = score_plaintext(plaintext)
    all_decryptions.append((primer, plaintext, score))

    print(f"\nPrimer: {primer}")
    print(f"Score: {score}")
    print(f"Plaintext: {plaintext}")

    # Check for words
    for word in COMMON_WORDS:
        if word in plaintext:
            print(f"  >> CONTAINS: {word}")


# Sort by score
print("\n" + "=" * 80)
print("RANKED BY ENGLISH-LIKE QUALITY")
print("=" * 80)

all_decryptions.sort(key=lambda x: x[2], reverse=True)
for primer, plaintext, score in all_decryptions[:5]:
    print(f"\n{primer} (score: {score})")
    print(f"{plaintext}")


# Try composite keys
print("\n" + "=" * 80)
print("COMPOSITE KEYS - Combinations of primers")
print("=" * 80)

# Try some key combinations
test_keys = [
    "BERLINCLOCK" + "KRYPTOS",
    "UNDER" + "ABOVE",
    "NORTHEAST" + "BERLIN",
    "SHADOW" + "CLOCK",
    "KRYPTOS" * 3,  # Repeated key
    "BERLINCLOCK" * 2,
]

for key in test_keys:
    plaintext = decrypt_autokey(K4, key)
    score = score_plaintext(plaintext)
    print(f"\nKey: {key[:30]}... (score: {score})")
    print(f"Plaintext: {plaintext}")
    for target in ["BERLINCLOCK", "NORTHEAST"]:
        if target in plaintext:
            print(f"  >>> FOUND: {target}")


# Try looking for the pattern at specific positions
print("\n" + "=" * 80)
print("SEARCHING FULL CORPUS FOR COMMON KRYPTOS WORDS")
print("=" * 80)

important_words = [
    "BERLINCLOCK", "NORTHEAST", "UNDERABOVE", "SHADOW",
    "PALIMPSEST", "ABSCISSA", "COORDINATES", "GRANITE",
    "KRYPTOS", "CLOCK", "BERLIN", "UNDER", "ABOVE"
]

for primer in PRIMERS:
    plaintext = decrypt_autokey(K4, primer)
    text_upper = plaintext.upper()
    found = []

    for word in important_words:
        if word in text_upper:
            found.append(word)

    if found:
        print(f"\n{primer}:")
        for word in found:
            idx = text_upper.find(word)
            print(f"  {word} at position {idx}")


# Test if backwards reading gives anything
print("\n" + "=" * 80)
print("TESTING REVERSE/BACKWARDS OPERATIONS")
print("=" * 80)

for primer in ["KRYPTOS", "BERLINCLOCK", "NORTHEAST"][:1]:
    plaintext = decrypt_autokey(K4, primer)

    # Try reading in reverse
    reversed_text = plaintext[::-1]
    print(f"\nPrimer: {primer}")
    print(f"Original: {plaintext}")
    print(f"Reversed: {reversed_text}")

    for word in ["BERLINCLOCK", "NORTHEAST"]:
        if word in reversed_text:
            print(f"  >>> FOUND {word} in reversed!")
