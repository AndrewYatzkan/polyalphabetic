#!/usr/bin/env python3
"""
Beaufort and Quagmire cipher variant tests on Kryptos K4.

Tests Beaufort, Variant Beaufort, and Quagmire I-IV ciphers using both
standard (A-Z) and KRYPTOS keyed alphabets. Derives key constraints from
known cribs (BERLINCLOCK@63, NORTHEAST@16), checks compatibility across
periods 26-31, and scores decryptions for English content.
"""

import sys
import os
from collections import defaultdict
from itertools import product

# ============================================================================
# CONSTANTS
# ============================================================================

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4_CIPHERTEXT)  # 97

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA  = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Known cribs
CRIBS = [
    ("BERLINCLOCK", 63),
    ("NORTHEAST", 16),
]

# The standard Vigenere key with period 29 (for reference)
VIGENERE_KEY_29 = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Periods to test
PERIODS = [26, 27, 28, 29, 30, 31]

# Word list path
WORDLIST_PATH = "/home/user/polyalphabetic/OxfordEnglishWords.txt"


# ============================================================================
# LOAD ENGLISH WORDS
# ============================================================================

def load_words(path):
    """Load English words from file, return set of uppercase words."""
    words = set()
    if not os.path.exists(path):
        print(f"WARNING: Word list not found at {path}")
        return words
    with open(path, 'r') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 3:
                words.add(w)
    return words

ENGLISH_WORDS = load_words(WORDLIST_PATH)

# Also build a set of words by length for faster scanning
WORDS_BY_LEN = defaultdict(set)
for w in ENGLISH_WORDS:
    WORDS_BY_LEN[len(w)].add(w)


# ============================================================================
# SCORING
# ============================================================================

def find_english_words(text, min_len=4):
    """Find all English words of length >= min_len in the text."""
    text = text.upper()
    found = []
    for length in range(min(20, len(text)), min_len - 1, -1):
        for i in range(len(text) - length + 1):
            substr = text[i:i+length]
            if substr in WORDS_BY_LEN[length]:
                found.append((substr, i))
    return found

def score_text(text, min_len=4):
    """
    Score text by counting total characters covered by English words.
    Returns (score, words_found).
    """
    text = text.upper()
    covered = set()
    words_found = []

    # Greedily find longest words first
    for length in range(min(20, len(text)), min_len - 1, -1):
        for i in range(len(text) - length + 1):
            substr = text[i:i+length]
            if substr in WORDS_BY_LEN[length]:
                # Check not already covered by a longer word
                positions = set(range(i, i + length))
                if not positions.issubset(covered):
                    words_found.append((substr, i))
                    covered.update(positions)

    return len(covered), words_found


# ============================================================================
# ALPHABET UTILITIES
# ============================================================================

def char_to_idx(c, alphabet):
    """Convert character to index in given alphabet."""
    return alphabet.index(c.upper())

def idx_to_char(i, alphabet):
    """Convert index to character in given alphabet."""
    return alphabet[i % len(alphabet)]

def make_keyed_alphabet(keyword):
    """Create a keyed alphabet from a keyword (standard A-Z base)."""
    seen = set()
    result = []
    for c in keyword.upper():
        if c not in seen and c.isalpha():
            seen.add(c)
            result.append(c)
    for c in STANDARD_ALPHA:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return ''.join(result)


# ============================================================================
# CIPHER IMPLEMENTATIONS
# ============================================================================

def vigenere_decrypt(ct, key, ct_alpha=STANDARD_ALPHA, pt_alpha=STANDARD_ALPHA):
    """Standard Vigenere: PT = CT - KEY (mod 26). Handles '?' in key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
            continue
        c_idx = ct_alpha.index(c)
        k_idx = ct_alpha.index(k)
        p_idx = (c_idx - k_idx) % 26
        result.append(pt_alpha[p_idx])
    return ''.join(result)

def vigenere_encrypt(pt, key, ct_alpha=STANDARD_ALPHA, pt_alpha=STANDARD_ALPHA):
    """Standard Vigenere encrypt: CT = PT + KEY (mod 26)"""
    result = []
    for i, c in enumerate(pt):
        p_idx = pt_alpha.index(c)
        k_idx = ct_alpha.index(key[i % len(key)])
        c_idx = (p_idx + k_idx) % 26
        result.append(ct_alpha[c_idx])
    return ''.join(result)


def beaufort_decrypt(ct, key, alphabet=STANDARD_ALPHA):
    """Beaufort cipher: PT = KEY - CT (mod 26). Reciprocal. Handles '?' in key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
            continue
        c_idx = alphabet.index(c)
        k_idx = alphabet.index(k)
        p_idx = (k_idx - c_idx) % 26
        result.append(alphabet[p_idx])
    return ''.join(result)

def beaufort_encrypt(pt, key, alphabet=STANDARD_ALPHA):
    """Beaufort cipher encrypt: CT = KEY - PT (mod 26). Same as decrypt."""
    return beaufort_decrypt(pt, key, alphabet)


def variant_beaufort_decrypt(ct, key, alphabet=STANDARD_ALPHA):
    """Variant Beaufort / Vigenere decrypt: PT = CT - KEY (mod 26). Handles '?' in key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
            continue
        c_idx = alphabet.index(c)
        k_idx = alphabet.index(k)
        p_idx = (c_idx - k_idx) % 26
        result.append(alphabet[p_idx])
    return ''.join(result)

def variant_beaufort_encrypt(pt, key, alphabet=STANDARD_ALPHA):
    """Variant Beaufort encrypt: CT = KEY - PT (mod 26)."""
    result = []
    for i, c in enumerate(pt):
        p_idx = alphabet.index(c)
        k_idx = alphabet.index(key[i % len(key)])
        c_idx = (k_idx - p_idx) % 26
        result.append(alphabet[c_idx])
    return ''.join(result)


def quagmire_decrypt(ct, key, pt_alpha, ct_alpha, period):
    """
    Quagmire general decryption. Handles '?' in key.

    For each position i:
      1. Find position of ct[i] in ct_alpha -> pos_ct
      2. Find position of key[i%period] in ct_alpha -> pos_key
      3. pt_idx = (pos_ct - pos_key) % 26
      4. PT char = pt_alpha[pt_idx]
    """
    result = []
    for i, c in enumerate(ct):
        k_char = key[i % len(key)]
        if k_char == '?':
            result.append('?')
            continue
        pos_ct = ct_alpha.index(c)
        pos_key = ct_alpha.index(k_char)
        pt_idx = (pos_ct - pos_key) % 26
        result.append(pt_alpha[pt_idx])
    return ''.join(result)

def quagmire_encrypt(pt, key, pt_alpha, ct_alpha, period):
    """
    Quagmire general encryption.

    For each position i:
      1. Find position of pt[i] in pt_alpha -> pos_pt
      2. Find position of key[i%period] in ct_alpha -> pos_key
      3. ct_idx = (pos_pt + pos_key) % 26
      4. CT char = ct_alpha[ct_idx]
    """
    result = []
    for i, c in enumerate(pt):
        pos_pt = pt_alpha.index(c)
        k_char = key[i % len(key)]
        pos_key = ct_alpha.index(k_char)
        ct_idx = (pos_pt + pos_key) % 26
        result.append(ct_alpha[ct_idx])
    return ''.join(result)


def quagmire_variant_decrypt(ct, key, pt_alpha, ct_alpha, period):
    """
    Quagmire with variant (Beaufort-like) decryption. Handles '?' in key.
    pt_idx = (pos_ct + pos_key) % 26 instead of subtraction.
    """
    result = []
    for i, c in enumerate(ct):
        k_char = key[i % len(key)]
        if k_char == '?':
            result.append('?')
            continue
        pos_ct = ct_alpha.index(c)
        pos_key = ct_alpha.index(k_char)
        pt_idx = (pos_ct + pos_key) % 26
        result.append(pt_alpha[pt_idx])
    return ''.join(result)


# ============================================================================
# KEY DERIVATION FROM CRIBS
# ============================================================================

def derive_vigenere_key_char(ct_char, pt_char, alphabet=STANDARD_ALPHA):
    """For Vigenere: KEY = CT - PT (mod 26) in given alphabet."""
    c = alphabet.index(ct_char)
    p = alphabet.index(pt_char)
    k = (c - p) % 26
    return alphabet[k]

def derive_beaufort_key_char(ct_char, pt_char, alphabet=STANDARD_ALPHA):
    """For Beaufort: KEY = CT + PT (mod 26) in given alphabet."""
    c = alphabet.index(ct_char)
    p = alphabet.index(pt_char)
    k = (c + p) % 26
    return alphabet[k]

def derive_variant_beaufort_key_char(ct_char, pt_char, alphabet=STANDARD_ALPHA):
    """For Variant Beaufort (enc: CT = KEY - PT): KEY = CT + PT (mod 26)."""
    c = alphabet.index(ct_char)
    p = alphabet.index(pt_char)
    k = (c + p) % 26
    return alphabet[k]


def derive_quagmire_key_char(ct_char, pt_char, pt_alpha, ct_alpha):
    """
    For Quagmire: derive the key character.
    Encryption: ct_idx = (pt_pos + key_pos) % 26 where pt_pos is position of PT in pt_alpha,
                key_pos is position of KEY in ct_alpha
    So: key_pos = (ct_pos - pt_pos) % 26, then key_char = ct_alpha[key_pos]

    Actually we need:
      pos_ct = ct_alpha.index(ct_char)
      pos_pt = pt_alpha.index(pt_char)
      pos_key = (pos_ct - pos_pt) % 26
      key_char = ct_alpha[pos_key]
    """
    pos_ct = ct_alpha.index(ct_char)
    pos_pt = pt_alpha.index(pt_char)
    pos_key = (pos_ct - pos_pt) % 26
    return ct_alpha[pos_key]


def derive_quagmire_variant_key_char(ct_char, pt_char, pt_alpha, ct_alpha):
    """
    For Quagmire variant: pt_idx = (pos_ct + pos_key) % 26
    So: pos_key = (pos_pt - pos_ct) % 26 (solving for encryption direction)

    Actually from decrypt: pt_alpha[pt_idx] where pt_idx = (pos_ct + pos_key) % 26
    So pos_key = (pt_pos_in_pt_alpha - pos_ct) % 26...

    Let's think about it differently. If decrypt is:
      pos_ct = ct_alpha.index(ct_char)
      pos_key = ct_alpha.index(key_char)
      pt_idx = (pos_ct + pos_key) % 26
      pt_char = pt_alpha[pt_idx]

    Then: pt_alpha.index(pt_char) = (pos_ct + pos_key) % 26
    So: pos_key = (pt_alpha.index(pt_char) - ct_alpha.index(ct_char)) % 26
    And: key_char = ct_alpha[pos_key]
    """
    pos_ct = ct_alpha.index(ct_char)
    pos_pt = pt_alpha.index(pt_char)
    pos_key = (pos_pt - pos_ct) % 26
    return ct_alpha[pos_key]


# ============================================================================
# KEY COMPATIBILITY CHECK
# ============================================================================

def check_key_compatibility(ct, cribs, period, derive_func, **kwargs):
    """
    Derive key characters from cribs and check for conflicts.

    Returns:
        (compatible, key_chars, conflicts)
        - compatible: True if no key position has conflicting values
        - key_chars: dict mapping key_position -> set of (char, source_crib)
        - conflicts: list of conflicting positions
    """
    key_chars = defaultdict(set)
    key_values = defaultdict(set)

    for crib_text, crib_pos in cribs:
        for j, pt_char in enumerate(crib_text):
            ct_pos = crib_pos + j
            if ct_pos >= len(ct):
                continue
            ct_char = ct[ct_pos]
            key_pos = ct_pos % period

            k_char = derive_func(ct_char, pt_char, **kwargs)
            key_chars[key_pos].add((k_char, f"{crib_text}[{j}]@ct{ct_pos}"))
            key_values[key_pos].add(k_char)

    conflicts = []
    for pos in key_values:
        if len(key_values[pos]) > 1:
            conflicts.append((pos, key_values[pos], key_chars[pos]))

    compatible = len(conflicts) == 0
    return compatible, key_chars, key_values, conflicts


def check_quagmire_key_compatibility(ct, cribs, period, derive_func, pt_alpha, ct_alpha):
    """Same as above but for quagmire which needs alphabet params."""
    key_chars = defaultdict(set)
    key_values = defaultdict(set)

    for crib_text, crib_pos in cribs:
        for j, pt_char in enumerate(crib_text):
            ct_pos = crib_pos + j
            if ct_pos >= len(ct):
                continue
            ct_char = ct[ct_pos]
            key_pos = ct_pos % period

            k_char = derive_func(ct_char, pt_char, pt_alpha, ct_alpha)
            key_chars[key_pos].add((k_char, f"{crib_text}[{j}]@ct{ct_pos}"))
            key_values[key_pos].add(k_char)

    conflicts = []
    for pos in key_values:
        if len(key_values[pos]) > 1:
            conflicts.append((pos, key_values[pos], key_chars[pos]))

    compatible = len(conflicts) == 0
    return compatible, key_chars, key_values, conflicts


# ============================================================================
# BUILD FULL KEY AND DECRYPT
# ============================================================================

def build_partial_key(key_values, period, alphabet=STANDARD_ALPHA):
    """Build a key string from known positions. Use '?' for unknown."""
    key = []
    for i in range(period):
        if i in key_values and len(key_values[i]) == 1:
            key.append(list(key_values[i])[0])
        else:
            key.append('?')
    return ''.join(key)


def decrypt_with_partial_key(ct, key, decrypt_func, **kwargs):
    """Decrypt ciphertext; unknown key positions produce '?'."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            # Build a temporary full key for just this position
            temp_key = k
            # Call decrypt for single char
            if 'alphabet' in kwargs:
                alpha = kwargs['alphabet']
                c_idx = alpha.index(c)
                k_idx = alpha.index(k)
                if 'beaufort' in str(decrypt_func.__name__):
                    p_idx = (k_idx - c_idx) % 26
                elif 'variant' in str(decrypt_func.__name__):
                    p_idx = (c_idx - k_idx) % 26
                else:
                    p_idx = (c_idx - k_idx) % 26
                result.append(alpha[p_idx])
            else:
                # For quagmire, the decrypt function handles it
                result.append('?')  # Simplified
    return ''.join(result)


# ============================================================================
# COMPREHENSIVE TESTING
# ============================================================================

def print_separator(char='=', width=80):
    print(char * width)

def print_header(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()


def test_cipher_variant(name, ct, cribs, periods, derive_func, decrypt_func,
                        alphabet=STANDARD_ALPHA, extra_kwargs=None):
    """
    Test a cipher variant across multiple periods.

    Returns list of (period, score, words, decrypted_text, key) tuples.
    """
    results = []

    if extra_kwargs is None:
        extra_kwargs = {}

    for period in periods:
        compatible, key_chars, key_values, conflicts = check_key_compatibility(
            ct, cribs, period, derive_func, alphabet=alphabet
        )

        if not compatible:
            # Still report conflicts briefly
            results.append({
                'period': period,
                'compatible': False,
                'conflicts': conflicts,
                'key': None,
                'decrypted': None,
                'score': 0,
                'words': [],
            })
            continue

        # Build key
        partial_key = build_partial_key(key_values, period, alphabet)

        # Decrypt
        decrypted = decrypt_func(ct, partial_key, alphabet=alphabet)

        # Score
        score, words = score_text(decrypted.replace('?', ''))

        results.append({
            'period': period,
            'compatible': True,
            'conflicts': [],
            'key': partial_key,
            'decrypted': decrypted,
            'score': score,
            'words': words,
            'known_positions': sum(1 for v in key_values.values() if len(v) == 1),
            'total_positions': period,
        })

    return results


def test_quagmire_variant(name, ct, cribs, periods, derive_func, decrypt_func,
                          pt_alpha, ct_alpha, variant=False):
    """Test a Quagmire variant across multiple periods."""
    results = []

    for period in periods:
        compatible, key_chars, key_values, conflicts = check_quagmire_key_compatibility(
            ct, cribs, period, derive_func, pt_alpha, ct_alpha
        )

        if not compatible:
            results.append({
                'period': period,
                'compatible': False,
                'conflicts': conflicts,
                'key': None,
                'decrypted': None,
                'score': 0,
                'words': [],
            })
            continue

        # Build key (key chars are from ct_alpha)
        partial_key = build_partial_key(key_values, period, ct_alpha)

        # Decrypt
        if variant:
            decrypted = quagmire_variant_decrypt(ct, partial_key, pt_alpha, ct_alpha, period)
        else:
            decrypted = quagmire_decrypt(ct, partial_key, pt_alpha, ct_alpha, period)

        # Handle unknown positions
        decrypted_clean = ""
        for i, c in enumerate(ct):
            k_pos = i % period
            if k_pos in key_values and len(key_values[k_pos]) == 1:
                decrypted_clean += decrypted[i]
            else:
                decrypted_clean += '?'

        # Score
        score, words = score_text(decrypted_clean.replace('?', ''))

        results.append({
            'period': period,
            'compatible': True,
            'conflicts': [],
            'key': partial_key,
            'decrypted': decrypted_clean,
            'score': score,
            'words': words,
            'known_positions': sum(1 for v in key_values.values() if len(v) == 1),
            'total_positions': period,
        })

    return results


def print_results(name, results, show_all=False):
    """Print results, highlighting any with English words."""
    any_words = any(r.get('score', 0) > 0 for r in results)
    any_compatible = any(r.get('compatible', False) for r in results)

    print(f"\n--- {name} ---")

    for r in results:
        period = r['period']
        if not r['compatible']:
            n_conflicts = len(r['conflicts'])
            if show_all:
                print(f"  Period {period}: INCOMPATIBLE ({n_conflicts} key position conflict(s))")
                for pos, vals, details in r['conflicts'][:3]:
                    vals_str = ', '.join(sorted(vals))
                    print(f"    Key pos {pos}: {vals_str}")
            continue

        known = r.get('known_positions', 0)
        total = r.get('total_positions', period)
        key = r['key']
        score = r['score']
        words = r['words']
        decrypted = r['decrypted']

        if score > 0 or show_all:
            print(f"  Period {period}: Key={key} ({known}/{total} known)")
            if decrypted:
                # Show decrypted with known crib regions highlighted
                print(f"    Decrypted: {decrypted}")
            if score > 0:
                # Sort words by length descending
                words_sorted = sorted(words, key=lambda x: len(x[0]), reverse=True)
                words_str = ', '.join(f"{w}@{p}" for w, p in words_sorted[:15])
                print(f"    Score: {score} chars covered | Words: {words_str}")

    if not any_compatible:
        print(f"  -> All periods incompatible")
    elif not any_words and not show_all:
        print(f"  -> No English words found in any period (all compatible periods tested)")

    return any_words


# ============================================================================
# MAIN TEST SUITE
# ============================================================================

def main():
    print("=" * 80)
    print("  K4 BEAUFORT AND QUAGMIRE CIPHER VARIANT ANALYSIS")
    print("=" * 80)
    print(f"\nK4 ciphertext ({K4_LEN} chars): {K4_CIPHERTEXT}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Standard alphabet: {STANDARD_ALPHA}")
    print(f"Cribs: {', '.join(f'{c}@{p}' for c,p in CRIBS)}")
    print(f"Periods tested: {PERIODS}")
    print(f"English words loaded: {len(ENGLISH_WORDS)}")

    all_results = []  # Collect (name, results) for final summary

    # ==================================================================
    # SECTION 1: STANDARD VIGENERE (BASELINE)
    # ==================================================================
    print_header("SECTION 1: STANDARD VIGENERE (BASELINE)")

    name = "Standard Vigenere (A-Z alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_vigenere_key_char,
        decrypt_func=variant_beaufort_decrypt,  # Vigenere decrypt = CT - KEY
        alphabet=STANDARD_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    name = "Standard Vigenere (KRYPTOS alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_vigenere_key_char,
        decrypt_func=variant_beaufort_decrypt,
        alphabet=KRYPTOS_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    # ==================================================================
    # SECTION 2: BEAUFORT CIPHER
    # ==================================================================
    print_header("SECTION 2: BEAUFORT CIPHER (PT = KEY - CT)")

    name = "Beaufort (A-Z alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_beaufort_key_char,
        decrypt_func=beaufort_decrypt,
        alphabet=STANDARD_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    name = "Beaufort (KRYPTOS alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_beaufort_key_char,
        decrypt_func=beaufort_decrypt,
        alphabet=KRYPTOS_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    # ==================================================================
    # SECTION 3: VARIANT BEAUFORT
    # ==================================================================
    print_header("SECTION 3: VARIANT BEAUFORT (Enc: CT = KEY - PT, Dec: PT = CT - KEY)")
    print("Note: Variant Beaufort decryption is identical to standard Vigenere decryption.")
    print("The difference is in how the key is derived from cribs (KEY = CT + PT, not CT - PT).")

    name = "Variant Beaufort (A-Z alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_variant_beaufort_key_char,
        decrypt_func=variant_beaufort_decrypt,
        alphabet=STANDARD_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    name = "Variant Beaufort (KRYPTOS alphabet)"
    results = test_cipher_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_variant_beaufort_key_char,
        decrypt_func=variant_beaufort_decrypt,
        alphabet=KRYPTOS_ALPHA
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    # ==================================================================
    # SECTION 4: QUAGMIRE I (Plain=keyed, Cipher=standard)
    # ==================================================================
    print_header("SECTION 4: QUAGMIRE I (Plain alphabet keyed, Cipher alphabet standard)")

    # Quagmire I with KRYPTOS as plaintext keyed alphabet
    for pt_name, pt_alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("Standard A-Z", STANDARD_ALPHA)]:
        for ct_name, ct_alpha_base in [("Standard A-Z", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
            if pt_name == "Standard A-Z" and ct_name == "Standard A-Z":
                continue  # This is just standard Vigenere

            name = f"Quagmire I (PT={pt_name}, CT={ct_name})"
            results = test_quagmire_variant(
                name, K4_CIPHERTEXT, CRIBS, PERIODS,
                derive_func=derive_quagmire_key_char,
                decrypt_func=quagmire_decrypt,
                pt_alpha=pt_alpha,
                ct_alpha=ct_alpha_base,
            )
            print_results(name, results, show_all=True)
            all_results.append((name, results))

    # ==================================================================
    # SECTION 5: QUAGMIRE II (Plain=standard, Cipher=keyed)
    # ==================================================================
    print_header("SECTION 5: QUAGMIRE II (Plain alphabet standard, Cipher alphabet keyed)")

    for ct_name, ct_alpha_q in [("KRYPTOS", KRYPTOS_ALPHA)]:
        name = f"Quagmire II (PT=Standard, CT={ct_name})"
        results = test_quagmire_variant(
            name, K4_CIPHERTEXT, CRIBS, PERIODS,
            derive_func=derive_quagmire_key_char,
            decrypt_func=quagmire_decrypt,
            pt_alpha=STANDARD_ALPHA,
            ct_alpha=ct_alpha_q,
        )
        print_results(name, results, show_all=True)
        all_results.append((name, results))

    # ==================================================================
    # SECTION 6: QUAGMIRE III (Both alphabets keyed with same keyword)
    # ==================================================================
    print_header("SECTION 6: QUAGMIRE III (Both alphabets keyed with KRYPTOS)")

    name = "Quagmire III (PT=KRYPTOS, CT=KRYPTOS)"
    results = test_quagmire_variant(
        name, K4_CIPHERTEXT, CRIBS, PERIODS,
        derive_func=derive_quagmire_key_char,
        decrypt_func=quagmire_decrypt,
        pt_alpha=KRYPTOS_ALPHA,
        ct_alpha=KRYPTOS_ALPHA,
    )
    print_results(name, results, show_all=True)
    all_results.append((name, results))

    # ==================================================================
    # SECTION 7: QUAGMIRE IV (Both alphabets keyed with different keywords)
    # ==================================================================
    print_header("SECTION 7: QUAGMIRE IV (Two different keyed alphabets)")

    # Try KRYPTOS as PT alphabet with several other keywords for CT alphabet
    other_keywords = ["PALIMPSEST", "ABSCISSA", "SHADOW", "LUCID", "BERLIN",
                      "CLOCK", "SANBORN", "SCHEIDT", "CIA", "LANGLEY",
                      "IQLUSION", "UNDERGRUUND", "NORTHEAST"]

    for kw in other_keywords:
        ct_alpha_kw = make_keyed_alphabet(kw)
        name = f"Quagmire IV (PT=KRYPTOS, CT=keyed({kw}))"
        results = test_quagmire_variant(
            name, K4_CIPHERTEXT, CRIBS, PERIODS,
            derive_func=derive_quagmire_key_char,
            decrypt_func=quagmire_decrypt,
            pt_alpha=KRYPTOS_ALPHA,
            ct_alpha=ct_alpha_kw,
        )
        has_words = print_results(name, results)
        all_results.append((name, results))

    # Also try the reverse: other keyword for PT, KRYPTOS for CT
    print(f"\n  --- Also testing with KRYPTOS as CT alphabet ---")
    for kw in other_keywords:
        pt_alpha_kw = make_keyed_alphabet(kw)
        name = f"Quagmire IV (PT=keyed({kw}), CT=KRYPTOS)"
        results = test_quagmire_variant(
            name, K4_CIPHERTEXT, CRIBS, PERIODS,
            derive_func=derive_quagmire_key_char,
            decrypt_func=quagmire_decrypt,
            pt_alpha=pt_alpha_kw,
            ct_alpha=KRYPTOS_ALPHA,
        )
        has_words = print_results(name, results)
        all_results.append((name, results))

    # ==================================================================
    # SECTION 8: QUAGMIRE VARIANTS WITH BEAUFORT-LIKE DECRYPTION
    # ==================================================================
    print_header("SECTION 8: QUAGMIRE + VARIANT (Beaufort-like) DECRYPTION")
    print("Testing Quagmire I-III with variant (additive) decryption instead of subtractive.")

    configs = [
        ("Quagmire I Variant (PT=KRYPTOS, CT=A-Z)", KRYPTOS_ALPHA, STANDARD_ALPHA),
        ("Quagmire II Variant (PT=A-Z, CT=KRYPTOS)", STANDARD_ALPHA, KRYPTOS_ALPHA),
        ("Quagmire III Variant (PT=KRYPTOS, CT=KRYPTOS)", KRYPTOS_ALPHA, KRYPTOS_ALPHA),
    ]

    for name, pt_a, ct_a in configs:
        results = test_quagmire_variant(
            name, K4_CIPHERTEXT, CRIBS, PERIODS,
            derive_func=derive_quagmire_variant_key_char,
            decrypt_func=quagmire_variant_decrypt,
            pt_alpha=pt_a,
            ct_alpha=ct_a,
            variant=True,
        )
        print_results(name, results, show_all=True)
        all_results.append((name, results))

    # ==================================================================
    # SECTION 9: KRYPTOS ALPHABET AS CIPHER ALPHABET (not tableau keyword)
    # ==================================================================
    print_header("SECTION 9: KRYPTOS ALPHABET AS THE CIPHER ALPHABET")
    print("What if ciphertext characters are indexed via KRYPTOS alphabet order")
    print("but the key and plaintext use standard A-Z?")

    # In this model:
    # - Ciphertext is written in KRYPTOS alphabet order
    # - Key uses standard alphabet
    # - Plaintext uses standard alphabet
    # Vigenere: c_kryptos_pos - k_std_pos = p_std_pos (mod 26)

    for period in PERIODS:
        key_values = defaultdict(set)
        key_chars = defaultdict(set)

        for crib_text, crib_pos in CRIBS:
            for j, pt_char in enumerate(crib_text):
                ct_pos = crib_pos + j
                if ct_pos >= K4_LEN:
                    continue
                ct_char = K4_CIPHERTEXT[ct_pos]
                key_pos = ct_pos % period

                # CT indexed by KRYPTOS, PT and KEY by standard
                c_idx = KRYPTOS_ALPHA.index(ct_char)
                p_idx = STANDARD_ALPHA.index(pt_char)
                k_idx = (c_idx - p_idx) % 26
                k_char = STANDARD_ALPHA[k_idx]

                key_values[key_pos].add(k_char)
                key_chars[key_pos].add((k_char, f"{crib_text}[{j}]@ct{ct_pos}"))

        conflicts = [(pos, vals) for pos, vals in key_values.items() if len(vals) > 1]
        compatible = len(conflicts) == 0

        if compatible:
            key = build_partial_key(key_values, period)
            # Decrypt: p_idx = kryptos_idx(ct) - std_idx(key) mod 26
            decrypted = []
            for i, c in enumerate(K4_CIPHERTEXT):
                k_pos = i % period
                if k_pos in key_values and len(key_values[k_pos]) == 1:
                    c_idx = KRYPTOS_ALPHA.index(c)
                    k_idx = STANDARD_ALPHA.index(list(key_values[k_pos])[0])
                    p_idx = (c_idx - k_idx) % 26
                    decrypted.append(STANDARD_ALPHA[p_idx])
                else:
                    decrypted.append('?')
            dec_text = ''.join(decrypted)
            score, words = score_text(dec_text.replace('?', ''))

            known = sum(1 for v in key_values.values() if len(v) == 1)
            print(f"  Period {period}: COMPATIBLE Key={key} ({known}/{period} known)")
            print(f"    Decrypted: {dec_text}")
            if score > 0:
                words_str = ', '.join(f"{w}@{p}" for w, p in sorted(words, key=lambda x: len(x[0]), reverse=True)[:15])
                print(f"    Score: {score} | Words: {words_str}")
        else:
            print(f"  Period {period}: INCOMPATIBLE ({len(conflicts)} conflicts)")

    # Same but with Beaufort formula: p = k + c (using KRYPTOS for c)
    print(f"\n  --- Beaufort variant (P = KEY + CT_kryptos mod 26) ---")
    for period in PERIODS:
        key_values = defaultdict(set)

        for crib_text, crib_pos in CRIBS:
            for j, pt_char in enumerate(crib_text):
                ct_pos = crib_pos + j
                if ct_pos >= K4_LEN:
                    continue
                ct_char = K4_CIPHERTEXT[ct_pos]
                key_pos = ct_pos % period

                c_idx = KRYPTOS_ALPHA.index(ct_char)
                p_idx = STANDARD_ALPHA.index(pt_char)
                # P = K + C -> K = P - C
                k_idx = (p_idx - c_idx) % 26
                k_char = STANDARD_ALPHA[k_idx]
                key_values[key_pos].add(k_char)

        conflicts = [(pos, vals) for pos, vals in key_values.items() if len(vals) > 1]
        compatible = len(conflicts) == 0

        if compatible:
            key = build_partial_key(key_values, period)
            decrypted = []
            for i, c in enumerate(K4_CIPHERTEXT):
                k_pos = i % period
                if k_pos in key_values and len(key_values[k_pos]) == 1:
                    c_idx = KRYPTOS_ALPHA.index(c)
                    k_idx = STANDARD_ALPHA.index(list(key_values[k_pos])[0])
                    p_idx = (k_idx + c_idx) % 26
                    decrypted.append(STANDARD_ALPHA[p_idx])
                else:
                    decrypted.append('?')
            dec_text = ''.join(decrypted)
            score, words = score_text(dec_text.replace('?', ''))

            known = sum(1 for v in key_values.values() if len(v) == 1)
            print(f"  Period {period}: COMPATIBLE Key={key} ({known}/{period} known)")
            print(f"    Decrypted: {dec_text}")
            if score > 0:
                words_str = ', '.join(f"{w}@{p}" for w, p in sorted(words, key=lambda x: len(x[0]), reverse=True)[:15])
                print(f"    Score: {score} | Words: {words_str}")
        else:
            print(f"  Period {period}: INCOMPATIBLE ({len(conflicts)} conflicts)")

    # ==================================================================
    # SECTION 10: TWO DIFFERENT KEYED ALPHABETS (exhaustive small search)
    # ==================================================================
    print_header("SECTION 10: TWO DIFFERENT KEYED ALPHABETS - SYSTEMATIC TEST")
    print("Testing all pairs of keyed alphabets from a curated keyword list.")

    keywords_for_alphabets = [
        "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "BERLIN", "CLOCK",
        "SANBORN", "NORTHEAST", "LANGLEY", "CIA", "LUCID", "IQLUSION",
        "UNDERGRUUND", "SCHEIDT", "ENIGMA", "VIGENERE",
    ]

    keyed_alphabets = {}
    for kw in keywords_for_alphabets:
        keyed_alphabets[kw] = make_keyed_alphabet(kw)

    best_score = 0
    best_configs = []

    tested = 0
    for pt_kw in keywords_for_alphabets:
        for ct_kw in keywords_for_alphabets:
            pt_a = keyed_alphabets[pt_kw]
            ct_a = keyed_alphabets[ct_kw]

            for period in PERIODS:
                # Try standard Quagmire decryption
                compat, kc, kv, conflicts = check_quagmire_key_compatibility(
                    K4_CIPHERTEXT, CRIBS, period,
                    derive_quagmire_key_char, pt_a, ct_a
                )

                if compat:
                    partial_key = build_partial_key(kv, period, ct_a)
                    dec = quagmire_decrypt(K4_CIPHERTEXT, partial_key, pt_a, ct_a, period)

                    # Build clean decrypted with unknowns
                    dec_clean = ""
                    for i in range(K4_LEN):
                        k_pos = i % period
                        if k_pos in kv and len(kv[k_pos]) == 1:
                            dec_clean += dec[i]
                        else:
                            dec_clean += '?'

                    score, words = score_text(dec_clean.replace('?', ''))
                    tested += 1

                    if score > best_score:
                        best_score = score

                    if score >= 12:  # Threshold for interesting results
                        best_configs.append({
                            'pt_kw': pt_kw, 'ct_kw': ct_kw, 'period': period,
                            'key': partial_key, 'decrypted': dec_clean,
                            'score': score, 'words': words,
                            'mode': 'standard'
                        })

                # Try variant Quagmire decryption
                compat_v, kc_v, kv_v, conflicts_v = check_quagmire_key_compatibility(
                    K4_CIPHERTEXT, CRIBS, period,
                    derive_quagmire_variant_key_char, pt_a, ct_a
                )

                if compat_v:
                    partial_key_v = build_partial_key(kv_v, period, ct_a)
                    dec_v = quagmire_variant_decrypt(K4_CIPHERTEXT, partial_key_v, pt_a, ct_a, period)

                    dec_clean_v = ""
                    for i in range(K4_LEN):
                        k_pos = i % period
                        if k_pos in kv_v and len(kv_v[k_pos]) == 1:
                            dec_clean_v += dec_v[i]
                        else:
                            dec_clean_v += '?'

                    score_v, words_v = score_text(dec_clean_v.replace('?', ''))
                    tested += 1

                    if score_v > best_score:
                        best_score = score_v

                    if score_v >= 12:
                        best_configs.append({
                            'pt_kw': pt_kw, 'ct_kw': ct_kw, 'period': period,
                            'key': partial_key_v, 'decrypted': dec_clean_v,
                            'score': score_v, 'words': words_v,
                            'mode': 'variant'
                        })

    print(f"  Tested {tested} compatible configurations")
    print(f"  Best score: {best_score}")

    if best_configs:
        # Sort by score descending
        best_configs.sort(key=lambda x: x['score'], reverse=True)
        print(f"\n  Top results (score >= 12):")
        for cfg in best_configs[:20]:
            words_str = ', '.join(f"{w}@{p}" for w, p in sorted(cfg['words'], key=lambda x: len(x[0]), reverse=True)[:10])
            print(f"    PT={cfg['pt_kw']}, CT={cfg['ct_kw']}, Period={cfg['period']}, Mode={cfg['mode']}")
            print(f"      Key: {cfg['key']}")
            print(f"      Dec: {cfg['decrypted']}")
            print(f"      Score: {cfg['score']} | Words: {words_str}")
    else:
        print(f"  No configurations scored >= 12")

    # ==================================================================
    # SECTION 11: DETAILED ANALYSIS OF PERIOD 29 (REFERENCE)
    # ==================================================================
    print_header("SECTION 11: DETAILED PERIOD 29 KEY ANALYSIS")
    print(f"Reference Vigenere key: {VIGENERE_KEY_29}")

    # Show what the known key gives us for standard Vigenere
    dec_vig = vigenere_decrypt(K4_CIPHERTEXT, VIGENERE_KEY_29)
    print(f"\nStandard Vigenere decrypt with full key:")
    print(f"  {dec_vig}")
    score_v, words_v = score_text(dec_vig)
    if words_v:
        words_str = ', '.join(f"{w}@{p}" for w, p in sorted(words_v, key=lambda x: len(x[0]), reverse=True)[:15])
        print(f"  Score: {score_v} | Words: {words_str}")

    # Now show what Beaufort gives with the same key
    dec_beau = beaufort_decrypt(K4_CIPHERTEXT, VIGENERE_KEY_29)
    print(f"\nBeaufort decrypt with same key:")
    print(f"  {dec_beau}")
    score_b, words_b = score_text(dec_beau)
    if words_b:
        words_str = ', '.join(f"{w}@{p}" for w, p in sorted(words_b, key=lambda x: len(x[0]), reverse=True)[:15])
        print(f"  Score: {score_b} | Words: {words_str}")

    # Beaufort key derivation for period 29
    print(f"\nBeaufort key derivation (KEY = CT + PT) for period 29:")
    beau_key_values = defaultdict(set)
    for crib_text, crib_pos in CRIBS:
        for j, pt_char in enumerate(crib_text):
            ct_pos = crib_pos + j
            ct_char = K4_CIPHERTEXT[ct_pos]
            key_pos = ct_pos % 29

            c_idx = STANDARD_ALPHA.index(ct_char)
            p_idx = STANDARD_ALPHA.index(pt_char)
            k_idx = (c_idx + p_idx) % 26
            k_char = STANDARD_ALPHA[k_idx]
            beau_key_values[key_pos].add(k_char)

    beau_key = build_partial_key(beau_key_values, 29)
    print(f"  Beaufort key: {beau_key}")

    beau_conflicts = [(pos, vals) for pos, vals in beau_key_values.items() if len(vals) > 1]
    if beau_conflicts:
        print(f"  Conflicts: {len(beau_conflicts)}")
        for pos, vals in beau_conflicts:
            print(f"    Position {pos}: {sorted(vals)}")
    else:
        print(f"  No conflicts! Full decryption:")
        dec = beaufort_decrypt(K4_CIPHERTEXT, beau_key)
        print(f"  {dec}")
        score, words = score_text(dec)
        if words:
            words_str = ', '.join(f"{w}@{p}" for w, p in sorted(words, key=lambda x: len(x[0]), reverse=True)[:15])
            print(f"  Score: {score} | Words: {words_str}")

    # ==================================================================
    # SECTION 12: MIXED ALPHABET DIRECTIONS
    # ==================================================================
    print_header("SECTION 12: MIXED ALPHABET DIRECTION TESTS")
    print("Testing: What if KRYPTOS alphabet is read backwards, or shifted?")

    kryptos_reversed = KRYPTOS_ALPHA[::-1]
    print(f"  KRYPTOS reversed: {kryptos_reversed}")

    for alpha_name, alpha in [("KRYPTOS reversed", kryptos_reversed)]:
        for cipher_name, derive_f, decrypt_f in [
            ("Vigenere", derive_vigenere_key_char, variant_beaufort_decrypt),
            ("Beaufort", derive_beaufort_key_char, beaufort_decrypt),
        ]:
            name = f"{cipher_name} ({alpha_name})"
            results = test_cipher_variant(
                name, K4_CIPHERTEXT, CRIBS, PERIODS,
                derive_func=derive_f,
                decrypt_func=decrypt_f,
                alphabet=alpha
            )
            has_words = print_results(name, results)
            all_results.append((name, results))

    # Also test KRYPTOS alphabet shifted to start at each position
    print(f"\n  --- KRYPTOS alphabet rotations ---")
    best_rotation_score = 0
    best_rotation_info = None

    for shift in range(26):
        rotated = KRYPTOS_ALPHA[shift:] + KRYPTOS_ALPHA[:shift]

        for cipher_type in ["vigenere", "beaufort"]:
            for period in PERIODS:
                key_values = defaultdict(set)

                for crib_text, crib_pos in CRIBS:
                    for j, pt_char in enumerate(crib_text):
                        ct_pos = crib_pos + j
                        if ct_pos >= K4_LEN:
                            continue
                        ct_char = K4_CIPHERTEXT[ct_pos]
                        key_pos = ct_pos % period

                        c_idx = rotated.index(ct_char)
                        p_idx = rotated.index(pt_char)

                        if cipher_type == "vigenere":
                            k_idx = (c_idx - p_idx) % 26
                        else:
                            k_idx = (c_idx + p_idx) % 26

                        k_char = rotated[k_idx]
                        key_values[key_pos].add(k_char)

                conflicts = [(pos, vals) for pos, vals in key_values.items() if len(vals) > 1]

                if len(conflicts) == 0:
                    key = build_partial_key(key_values, period, rotated)

                    decrypted = []
                    for i, c in enumerate(K4_CIPHERTEXT):
                        k_pos = i % period
                        if k_pos in key_values and len(key_values[k_pos]) == 1:
                            c_idx = rotated.index(c)
                            k_idx = rotated.index(list(key_values[k_pos])[0])
                            if cipher_type == "vigenere":
                                p_idx = (c_idx - k_idx) % 26
                            else:
                                p_idx = (k_idx - c_idx) % 26
                            decrypted.append(rotated[p_idx])
                        else:
                            decrypted.append('?')

                    dec_text = ''.join(decrypted)
                    score, words = score_text(dec_text.replace('?', ''))

                    if score > best_rotation_score:
                        best_rotation_score = score
                        best_rotation_info = {
                            'shift': shift, 'rotated': rotated,
                            'cipher': cipher_type, 'period': period,
                            'key': key, 'decrypted': dec_text,
                            'score': score, 'words': words,
                        }

    if best_rotation_info:
        r = best_rotation_info
        print(f"  Best rotation: shift={r['shift']}, cipher={r['cipher']}, period={r['period']}")
        print(f"    Alphabet: {r['rotated']}")
        print(f"    Key: {r['key']}")
        print(f"    Decrypted: {r['decrypted']}")
        if r['words']:
            words_str = ', '.join(f"{w}@{p}" for w, p in sorted(r['words'], key=lambda x: len(x[0]), reverse=True)[:15])
            print(f"    Score: {r['score']} | Words: {words_str}")
    else:
        print(f"  No compatible rotation found")

    # ==================================================================
    # FINAL SUMMARY
    # ==================================================================
    print_header("FINAL SUMMARY: ALL RESULTS WITH ENGLISH WORDS")

    any_found = False
    summary_results = []

    for name, results in all_results:
        for r in results:
            if r.get('score', 0) > 0:
                summary_results.append((name, r))

    # Sort by score
    summary_results.sort(key=lambda x: x[1]['score'], reverse=True)

    if summary_results:
        any_found = True
        for name, r in summary_results:
            period = r['period']
            score = r['score']
            words = r['words']
            key = r.get('key', '?')
            decrypted = r.get('decrypted', '?')

            words_sorted = sorted(words, key=lambda x: len(x[0]), reverse=True)
            words_str = ', '.join(f"{w}@{p}" for w, p in words_sorted[:15])

            print(f"\n  {name} | Period {period} | Score: {score}")
            print(f"    Key: {key}")
            print(f"    Dec: {decrypted}")
            print(f"    Words: {words_str}")

    if not any_found:
        print("\n  No cipher variant produced English words beyond the known cribs.")
        print("  This suggests K4 may use a more complex mechanism than standard")
        print("  Beaufort/Quagmire variants with these alphabet configurations.")

    # ==================================================================
    # COMPATIBILITY SUMMARY TABLE
    # ==================================================================
    print_header("COMPATIBILITY SUMMARY TABLE")
    print(f"  {'Cipher Variant':<50} | {'Period':<6} | {'Compat':<7} | {'Known':<6} | {'Score':<6}")
    print(f"  {'-'*50}-+-{'-'*6}-+-{'-'*7}-+-{'-'*6}-+-{'-'*6}")

    for name, results in all_results:
        for r in results:
            period = r['period']
            compat = 'YES' if r.get('compatible', False) else 'NO'
            known = r.get('known_positions', '-')
            score = r.get('score', 0)
            if r.get('compatible', False) or r['period'] == 29:
                marker = ' ***' if score > 10 else ''
                print(f"  {name:<50} | {period:>6} | {compat:>7} | {str(known):>6} | {score:>6}{marker}")

    print(f"\n  *** = Score > 10 (potentially interesting)")
    print(f"\nAnalysis complete.")


if __name__ == '__main__':
    main()
