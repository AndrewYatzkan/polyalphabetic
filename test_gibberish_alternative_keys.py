#!/usr/bin/env python3
"""
Test if gibberish sections are encrypted with DIFFERENT keys.

Current state:
- K4 plaintext: UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF
- K4 key (Period 29): DIJJQELYOIECBAQKVAATCRDUMPABT
- Readable words: UNDER, NORTHEAST, BERLINCLOCK, ABOVE
- Gibberish sections: QAPBZDBKZEL, LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH, RSPVJWQUL, ZOLRKCAYF

Hypotheses to test:
1. Gibberish key = readable words concatenated: UNDERNORTHEASTBERLINCLOCKABOVE
2. Gibberish key = K1 key: PALIMPSEST
3. Gibberish key = K2 key: ABSCISSA
4. Gibberish key = Berlin Wall date: 11091989
5. Gibberish = XOR result of readable words and ciphertext
6. Odd/even position split keys
"""

from collections import Counter
import re

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Extract gibberish sections
READABLE_WORDS = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]
GIBBERISH_SECTIONS = [
    ("QAPBZDBKZEL", 5, 16),          # Gap 1: positions 5-15 (11 chars)
    ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", 16, 54),  # Gap 2: positions 16-53 (38 chars)
    ("RSPVJWQUL", 54, 63),           # Gap 3: positions 54-62 (9 chars)
    ("ZOLRKCAYF", 63, 72)            # Gap 4: positions 63-71 (9 chars)
]

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenère cipher."""
    plaintext = ""
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext += decrypted
            key_idx += 1
        else:
            plaintext += char
    return plaintext

def vigenere_encrypt(plaintext, key):
    """Encrypt using Vigenère cipher."""
    ciphertext = ""
    key_idx = 0
    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            encrypted = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            ciphertext += encrypted
            key_idx += 1
        else:
            ciphertext += char
    return ciphertext

def beaufort_decrypt(ciphertext, key):
    """Decrypt using Beaufort cipher (symmetric)."""
    plaintext = ""
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = chr((ord(key[key_idx % len(key)]) - ord(char)) % 26 + ord('A'))
            plaintext += decrypted
            key_idx += 1
        else:
            plaintext += char
    return plaintext

def xor_decrypt(ciphertext, key):
    """Decrypt using XOR with key."""
    plaintext = ""
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            char_val = ord(char) - ord('A')
            key_val = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = chr((char_val ^ key_val) + ord('A'))
            plaintext += decrypted
            key_idx += 1
        else:
            plaintext += char
    return plaintext

def test_alternative_key(gibberish, key, key_name, cipher_type="vigenere"):
    """Test if alternative key produces readable plaintext."""
    if cipher_type == "vigenere":
        decrypted = vigenere_decrypt(gibberish, key)
    elif cipher_type == "beaufort":
        decrypted = beaufort_decrypt(gibberish, key)
    elif cipher_type == "xor":
        decrypted = xor_decrypt(gibberish, key)
    else:
        decrypted = vigenere_decrypt(gibberish, key)

    # Check for English characteristics
    vowels = sum(1 for c in decrypted if c in 'AEIOU')
    vowel_ratio = vowels / len(decrypted) if decrypted else 0

    # Check for common patterns
    english_bigrams = ['TH', 'HE', 'IN', 'ER', 'AN', 'ED', 'ND', 'ON', 'EN', 'AT', 'OU', 'IT', 'HA', 'ES', 'OR']
    found_bigrams = sum(1 for b in english_bigrams if b in decrypted)

    # Check for repeated characters
    char_freq = Counter(decrypted)
    max_freq = max(char_freq.values()) if char_freq else 0

    return {
        'decrypted': decrypted,
        'vowel_ratio': vowel_ratio,
        'english_bigrams': found_bigrams,
        'max_char_freq': max_freq,
        'repeats': sum(1 for f in char_freq.values() if f > 1)
    }

def analyze_all_gaps_with_key(key, key_name, cipher_type="vigenere"):
    """Analyze all gibberish gaps with a single key."""
    print(f"\n{'='*80}")
    print(f"Testing key: {key_name}")
    print(f"Key value: {key}")
    print(f"Cipher type: {cipher_type}")
    print(f"{'='*80}")

    any_english = False
    for gap_text, gap_name, start, end in [
        ("QAPBZDBKZEL", "Gap 1", 5, 16),
        ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", "Gap 2", 16, 54),
        ("RSPVJWQUL", "Gap 3", 54, 63),
        ("ZOLRKCAYF", "Gap 4", 63, 72)
    ]:
        result = test_alternative_key(gap_text, key, key_name, cipher_type)

        print(f"\n{gap_name}: {gap_text}")
        print(f"  Decrypted: {result['decrypted']}")
        print(f"  Vowel ratio: {result['vowel_ratio']:.2%}")
        print(f"  English bigrams found: {result['english_bigrams']}/15")
        print(f"  Max char frequency: {result['max_char_freq']}")
        print(f"  Repeated characters: {result['repeats']}")

        # Check if looks like English
        if result['vowel_ratio'] > 0.25 and result['english_bigrams'] >= 2:
            print(f"  ⚠ POTENTIAL ENGLISH PATTERN!")
            any_english = True

    return any_english

print("\n" + "="*80)
print("HYPOTHESIS TESTING: ALTERNATIVE ENCRYPTION KEYS FOR K4 GIBBERISH")
print("="*80)

# ============================================================================
# HYPOTHESIS 1: Key from readable words
# ============================================================================
key1 = "UNDERNORTHEASTBERLINCLOCKABOVE"
analyze_all_gaps_with_key(key1, "Hypothesis 1: Readable words concatenated")

# ============================================================================
# HYPOTHESIS 2: K1 key (PALIMPSEST)
# ============================================================================
key2 = "PALIMPSEST"
analyze_all_gaps_with_key(key2, "Hypothesis 2: K1 key (PALIMPSEST)", "vigenere")
analyze_all_gaps_with_key(key2, "Hypothesis 2: K1 key (PALIMPSEST) - Beaufort", "beaufort")

# ============================================================================
# HYPOTHESIS 3: K2 key (ABSCISSA)
# ============================================================================
key3 = "ABSCISSA"
analyze_all_gaps_with_key(key3, "Hypothesis 3: K2 key (ABSCISSA)", "vigenere")
analyze_all_gaps_with_key(key3, "Hypothesis 3: K2 key (ABSCISSA) - Beaufort", "beaufort")

# ============================================================================
# HYPOTHESIS 4: Berlin Wall date (11091989)
# ============================================================================
key4 = "BERLIN1989"  # Berlin Wall fell 11/9/1989
analyze_all_gaps_with_key(key4, "Hypothesis 4: Berlin Wall date format", "vigenere")

# ============================================================================
# HYPOTHESIS 5: Reverse the key
# ============================================================================
key5 = K4_KEY[::-1]  # TBPAMUDRCTAAVQABCEIOYLIJD
analyze_all_gaps_with_key(key5, "Hypothesis 5: K4 key reversed", "vigenere")

# ============================================================================
# HYPOTHESIS 6: Position-dependent keys (odd vs even positions)
# ============================================================================
print(f"\n{'='*80}")
print("Testing position-dependent keys (odd/even split)")
print(f"{'='*80}")

# Test with reading key shifted
odd_key = K4_KEY[0::2]  # Characters at positions 0, 2, 4, ...
even_key = K4_KEY[1::2]  # Characters at positions 1, 3, 5, ...

print(f"\nOdd positions key: {odd_key}")
print(f"Even positions key: {even_key}")

for gap_text, gap_name, start, end in [
    ("QAPBZDBKZEL", "Gap 1", 5, 16),
    ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", "Gap 2", 16, 54),
    ("RSPVJWQUL", "Gap 3", 54, 63),
    ("ZOLRKCAYF", "Gap 4", 63, 72)
]:
    print(f"\n{gap_name}: {gap_text}")

    # Try odd key
    result_odd = test_alternative_key(gap_text, odd_key, "Odd positions", "vigenere")
    print(f"  With odd key: {result_odd['decrypted']}")
    print(f"    Vowel ratio: {result_odd['vowel_ratio']:.2%}, Bigrams: {result_odd['english_bigrams']}")

    # Try even key
    result_even = test_alternative_key(gap_text, even_key, "Even positions", "vigenere")
    print(f"  With even key: {result_even['decrypted']}")
    print(f"    Vowel ratio: {result_even['vowel_ratio']:.2%}, Bigrams: {result_even['english_bigrams']}")

# ============================================================================
# HYPOTHESIS 7: XOR operations
# ============================================================================
print(f"\n{'='*80}")
print("Testing XOR operations")
print(f"{'='*80}")

# Get the plaintext positions that correspond to gibberish
plain_positions = [
    (5, 16, "Gap 1 plaintext"),
    (16, 54, "Gap 2 plaintext"),
    (54, 63, "Gap 3 plaintext"),
    (63, 72, "Gap 4 plaintext")
]

for start, end, label in plain_positions:
    print(f"\n{label}: {K4_PLAINTEXT[start:end]}")

# ============================================================================
# HYPOTHESIS 8: Shift the key by position
# ============================================================================
print(f"\n{'='*80}")
print("Testing shifted keys (ROT variations)")
print(f"{'='*80}")

for shift_amount in [1, 2, 3, 5, 13]:
    shifted_key = ""
    for char in K4_KEY:
        new_char = chr((ord(char) - ord('A') + shift_amount) % 26 + ord('A'))
        shifted_key += new_char

    print(f"\nTesting ROT{shift_amount} key: {shifted_key}")
    gap_text = "QAPBZDBKZEL"
    result = test_alternative_key(gap_text, shifted_key, f"ROT{shift_amount}", "vigenere")
    print(f"  Gap 1 result: {result['decrypted']} (vowels: {result['vowel_ratio']:.2%})")

# ============================================================================
# HYPOTHESIS 9: Try key expansion patterns
# ============================================================================
print(f"\n{'='*80}")
print("Testing key expansion patterns")
print(f"{'='*80}")

# Double the key
key_double = K4_KEY + K4_KEY
print(f"\nDouble key: {key_double[:40]}...")
gap_text = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
result = test_alternative_key(gap_text, key_double, "Doubled key", "vigenere")
print(f"Gap 2 result: {result['decrypted']}")
print(f"Vowel ratio: {result['vowel_ratio']:.2%}, Bigrams: {result['english_bigrams']}")

print(f"\n{'='*80}")
print("SUMMARY: Testing complete")
print("Check output above for any English patterns (vowel ratio > 25% or bigrams > 2)")
print(f"{'='*80}")
