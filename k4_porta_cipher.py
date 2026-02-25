#!/usr/bin/env python3
"""
K4 Porta Cipher Hypothesis Testing
====================================
Tests Porta, Beaufort, and Variant Beaufort ciphers against Kryptos K4
using known cribs EASTNORTHEAST@21 and BERLINCLOCK@63.
"""

import math
import string
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
assert len(K4) == 97, f"K4 length is {len(K4)}, expected 97"

# Known cribs (0-indexed)
CRIB1_PLAIN = "EASTNORTHEAST"
CRIB1_START = 21  # positions 21-33
CRIB1_CIPHER = K4[CRIB1_START:CRIB1_START + len(CRIB1_PLAIN)]

CRIB2_PLAIN = "BERLINCLOCK"
CRIB2_START = 63  # positions 63-73
CRIB2_CIPHER = K4[CRIB2_START:CRIB2_START + len(CRIB2_PLAIN)]

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA  = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

print("=" * 70)
print("K4 PORTA CIPHER HYPOTHESIS TESTING")
print("=" * 70)
print(f"K4 ciphertext ({len(K4)} chars): {K4}")
print(f"Crib 1: '{CRIB1_PLAIN}' at positions {CRIB1_START}-{CRIB1_START+len(CRIB1_PLAIN)-1}")
print(f"  Cipher chars: {CRIB1_CIPHER}")
print(f"Crib 2: '{CRIB2_PLAIN}' at positions {CRIB2_START}-{CRIB2_START+len(CRIB2_PLAIN)-1}")
print(f"  Cipher chars: {CRIB2_CIPHER}")
print()

# ============================================================
# QUADGRAM SCORER
# ============================================================
class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        with open(filepath) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    key, count = parts[0], int(parts[1])
                    self.quadgrams[key] = count
                    self.total += count
        self.floor = math.log10(0.01 / self.total)
        print(f"Loaded {len(self.quadgrams)} quadgrams, total count = {self.total}")
        self.log_probs = {}
        for k, v in self.quadgrams.items():
            self.log_probs[k] = math.log10(v / self.total)

    def score(self, text):
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            qg = text[i:i+4]
            s += self.log_probs.get(qg, self.floor)
        return s

    def normalized_score(self, text):
        if len(text) < 4:
            return -99.0
        return self.score(text) / len(text)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

ref_english = "THEEASTNORTHEASTBERLINCLOCKISPARTOFTHEKRYPTOSSCULPTURE"
print(f"Reference English score (per char): {scorer.normalized_score(ref_english):.4f}")
print()

# ============================================================
# STANDARD PORTA CIPHER
# ============================================================
def porta_derive_key_tableau(cipher_char, plain_char, alphabet):
    """
    Given cipher/plain pair, derive the Porta tableau number (0..12).
    Returns None if both chars are in the same half (impossible for Porta).
    """
    n = len(alphabet)
    half = n // 2  # 13

    c_idx = alphabet.index(cipher_char)
    p_idx = alphabet.index(plain_char)

    # Porta swaps halves: one must be in first half, other in second
    if (c_idx < half) == (p_idx < half):
        return None  # same half -> impossible

    # Normalize: identify which is first-half, which is second-half
    if p_idx < half:
        first_idx = p_idx
        second_idx = c_idx - half
    else:
        first_idx = c_idx
        second_idx = p_idx - half

    # Tableau t: first_half[i] <-> second_half[(i + t) % 13]
    t = (second_idx - first_idx) % half
    return t


def porta_decrypt_char(cipher_char, tableau_num, alphabet):
    """Decrypt a single char using Porta with given tableau number."""
    n = len(alphabet)
    half = n // 2
    c_idx = alphabet.index(cipher_char)

    if c_idx < half:
        # cipher in first half -> plain in second half
        # first_idx = ? maps to c_idx via: c_idx is first_half result
        # Actually for Porta (reciprocal): apply same transform
        # cipher_first[i] -> plain = second[(i + t) % 13]
        mapped = (c_idx + tableau_num) % half
        return alphabet[half + mapped]
    else:
        # cipher in second half -> plain in first half
        mapped = (c_idx - half - tableau_num) % half
        return alphabet[mapped]


def check_porta_cribs(period, alphabet):
    """
    For a given period, derive key tableaux from crib1, check crib2.
    Returns (key_info dict, True) or (None, False).
    """
    half = len(alphabet) // 2
    key_info = {}

    # Derive from crib 1
    for i in range(len(CRIB1_PLAIN)):
        pos = CRIB1_START + i
        kp = pos % period
        t = porta_derive_key_tableau(K4[pos], CRIB1_PLAIN[i], alphabet)
        if t is None:
            return None, False
        if kp in key_info:
            if key_info[kp] != t:
                return None, False
        key_info[kp] = t

    # Check crib 2
    for i in range(len(CRIB2_PLAIN)):
        pos = CRIB2_START + i
        kp = pos % period
        t = porta_derive_key_tableau(K4[pos], CRIB2_PLAIN[i], alphabet)
        if t is None:
            return None, False
        if kp in key_info:
            if key_info[kp] != t:
                return None, False
        key_info[kp] = t

    return key_info, True


def decrypt_porta_full(key_info, period, alphabet):
    """Decrypt K4 using derived Porta key info."""
    result = []
    for i, c in enumerate(K4):
        kp = i % period
        if kp in key_info:
            result.append(porta_decrypt_char(c, key_info[kp], alphabet))
        else:
            result.append('?')
    return ''.join(result)


# ============================================================
# TEST 1: Standard Porta, all periods 1-50
# ============================================================
print("=" * 70)
print("TEST 1: STANDARD PORTA CIPHER (standard alphabet)")
print("=" * 70)
print()

hits_standard = []
for period in range(1, 51):
    key_info, consistent = check_porta_cribs(period, STANDARD_ALPHA)
    if consistent and key_info is not None:
        decrypted = decrypt_porta_full(key_info, period, STANDARD_ALPHA)
        known_count = sum(1 for c in decrypted if c != '?')
        known_text = decrypted.replace('?', '')
        sc = scorer.normalized_score(known_text) if len(known_text) >= 4 else -99.0
        hits_standard.append((period, key_info, decrypted, known_count, sc))

        key_display = []
        for p in range(period):
            if p in key_info:
                t = key_info[p]
                key_display.append(f"{STANDARD_ALPHA[2*t]}/{STANDARD_ALPHA[2*t+1]}")
            else:
                key_display.append("??")

        print(f"Period {period:2d}: BOTH CRIBS MATCH!")
        print(f"  Key tableaux: {', '.join(key_display)}")
        print(f"  Known chars: {known_count}/{len(K4)}")
        print(f"  Score (per char): {sc:.4f}")
        print(f"  Decrypted: {decrypted}")
        print()

if not hits_standard:
    print("  No periods produced consistent key from both cribs.")
    print()
    # Diagnose
    half = 13
    same_half_1 = []
    for i in range(len(CRIB1_PLAIN)):
        pos = CRIB1_START + i
        c_idx = STANDARD_ALPHA.index(K4[pos])
        p_idx = STANDARD_ALPHA.index(CRIB1_PLAIN[i])
        if (c_idx < half) == (p_idx < half):
            same_half_1.append((pos, K4[pos], c_idx, CRIB1_PLAIN[i], p_idx))

    same_half_2 = []
    for i in range(len(CRIB2_PLAIN)):
        pos = CRIB2_START + i
        c_idx = STANDARD_ALPHA.index(K4[pos])
        p_idx = STANDARD_ALPHA.index(CRIB2_PLAIN[i])
        if (c_idx < half) == (p_idx < half):
            same_half_2.append((pos, K4[pos], c_idx, CRIB2_PLAIN[i], p_idx))

    if same_half_1:
        print(f"  Crib1 same-half violations ({len(same_half_1)}/{len(CRIB1_PLAIN)}):")
        for pos, cc, ci, pc, pi in same_half_1:
            hc = "1st" if ci < half else "2nd"
            hp = "1st" if pi < half else "2nd"
            print(f"    Pos {pos}: C={cc}(idx={ci},{hc}) P={pc}(idx={pi},{hp})")
    else:
        print(f"  Crib1: all pairs cross halves (OK for Porta)")

    if same_half_2:
        print(f"  Crib2 same-half violations ({len(same_half_2)}/{len(CRIB2_PLAIN)}):")
        for pos, cc, ci, pc, pi in same_half_2:
            hc = "1st" if ci < half else "2nd"
            hp = "1st" if pi < half else "2nd"
            print(f"    Pos {pos}: C={cc}(idx={ci},{hc}) P={pc}(idx={pi},{hp})")
    else:
        print(f"  Crib2: all pairs cross halves (OK for Porta)")
    print()

# ============================================================
# TEST 2: Porta with KRYPTOS-ordered alphabet
# ============================================================
print("=" * 70)
print("TEST 2: PORTA CIPHER WITH KRYPTOS ALPHABET")
print("=" * 70)
print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
print(f"First half (0-12):  {KRYPTOS_ALPHA[:13]}")
print(f"Second half (13-25): {KRYPTOS_ALPHA[13:]}")
print()

hits_kryptos = []
for period in range(1, 51):
    key_info, consistent = check_porta_cribs(period, KRYPTOS_ALPHA)
    if consistent and key_info is not None:
        decrypted = decrypt_porta_full(key_info, period, KRYPTOS_ALPHA)
        known_count = sum(1 for c in decrypted if c != '?')
        known_text = decrypted.replace('?', '')
        sc = scorer.normalized_score(known_text) if len(known_text) >= 4 else -99.0
        hits_kryptos.append((period, key_info, decrypted, known_count, sc))

        key_display = []
        for p in range(period):
            if p in key_info:
                t = key_info[p]
                key_display.append(f"{KRYPTOS_ALPHA[2*t]}/{KRYPTOS_ALPHA[2*t+1]}")
            else:
                key_display.append("??")

        print(f"Period {period:2d}: BOTH CRIBS MATCH!")
        print(f"  Key tableaux: {', '.join(key_display)}")
        print(f"  Known chars: {known_count}/{len(K4)}")
        print(f"  Score (per char): {sc:.4f}")
        print(f"  Decrypted: {decrypted}")
        print()

if not hits_kryptos:
    print("  No periods produced consistent key from both cribs.")
    half = 13
    same_half_1 = []
    for i in range(len(CRIB1_PLAIN)):
        pos = CRIB1_START + i
        c_idx = KRYPTOS_ALPHA.index(K4[pos])
        p_idx = KRYPTOS_ALPHA.index(CRIB1_PLAIN[i])
        if (c_idx < half) == (p_idx < half):
            same_half_1.append((pos, K4[pos], c_idx, CRIB1_PLAIN[i], p_idx))

    same_half_2 = []
    for i in range(len(CRIB2_PLAIN)):
        pos = CRIB2_START + i
        c_idx = KRYPTOS_ALPHA.index(K4[pos])
        p_idx = KRYPTOS_ALPHA.index(CRIB2_PLAIN[i])
        if (c_idx < half) == (p_idx < half):
            same_half_2.append((pos, K4[pos], c_idx, CRIB2_PLAIN[i], p_idx))

    if same_half_1:
        print(f"  Crib1 same-half violations ({len(same_half_1)}/{len(CRIB1_PLAIN)}):")
        for pos, cc, ci, pc, pi in same_half_1:
            print(f"    Pos {pos}: C={cc}(idx={ci}) P={pc}(idx={pi})")
    else:
        print(f"  Crib1: all pairs cross halves (OK)")

    if same_half_2:
        print(f"  Crib2 same-half violations ({len(same_half_2)}/{len(CRIB2_PLAIN)}):")
        for pos, cc, ci, pc, pi in same_half_2:
            print(f"    Pos {pos}: C={cc}(idx={ci}) P={pc}(idx={pi})")
    else:
        print(f"  Crib2: all pairs cross halves (OK)")
    print()

# ============================================================
# TEST 3: Modified Porta with various alphabet half-splits
# ============================================================
print("=" * 70)
print("TEST 3: MODIFIED PORTA - ALTERNATE HALF-SPLITS")
print("=" * 70)
print()

def derive_custom_porta_tableau(cipher_char, plain_char, first_half, second_half):
    """Derive tableau number for Porta with custom half-splits."""
    half = len(first_half)
    fh_set = set(first_half)
    sh_set = set(second_half)

    if cipher_char in fh_set and plain_char in sh_set:
        c_idx = first_half.index(cipher_char)
        p_idx = second_half.index(plain_char)
        # cipher in first, plain in second:
        # If plain in second half -> decrypt: plain_second[i] -> first[(i - t) % 13]
        # cipher = first[(p_idx - t) % 13]  => c_idx = (p_idx - t) % 13 => t = (p_idx - c_idx) % 13
        t = (p_idx - c_idx) % half
        return t
    elif cipher_char in sh_set and plain_char in fh_set:
        c_idx = second_half.index(cipher_char)
        p_idx = first_half.index(plain_char)
        # cipher in second, plain in first:
        # plain_first[i] -> second[(i + t) % 13]
        # cipher = second[(p_idx + t) % 13] => c_idx = (p_idx + t) % 13 => t = (c_idx - p_idx) % 13
        t = (c_idx - p_idx) % half
        return t
    else:
        return None  # same half


def custom_porta_decrypt_char(cipher_char, tableau_num, first_half, second_half):
    """Decrypt with custom-split Porta."""
    half = len(first_half)
    fh_set = set(first_half)
    sh_set = set(second_half)

    if cipher_char in fh_set:
        c_idx = first_half.index(cipher_char)
        mapped = (c_idx + tableau_num) % half
        return second_half[mapped]
    else:
        c_idx = second_half.index(cipher_char)
        mapped = (c_idx - tableau_num) % half
        return first_half[mapped]


splits_to_test = [
    ("Standard A-M / N-Z",
     list("ABCDEFGHIJKLM"), list("NOPQRSTUVWXYZ")),
    ("KRYPTOS first 13 / last 13",
     list(KRYPTOS_ALPHA[:13]), list(KRYPTOS_ALPHA[13:])),
    ("Even/odd index in KRYPTOS",
     [KRYPTOS_ALPHA[i] for i in range(0, 26, 2)],
     [KRYPTOS_ALPHA[i] for i in range(1, 26, 2)]),
    ("Vowels+freq vs rest (custom)",
     list("AEIOULNRST"), list("BCDFGHJKMPQUVWXYZ")),
]

# Only test splits where both halves have exactly 13 chars
splits_to_test = [(n, f, s) for n, f, s in splits_to_test if len(f) == 13 and len(s) == 13]

for split_name, fh_list, sh_list in splits_to_test:
    fh_set = set(fh_list)
    sh_set = set(sh_list)
    print(f"  Split: {split_name}")
    print(f"    First half:  {''.join(fh_list)}")
    print(f"    Second half: {''.join(sh_list)}")

    # Check cross-half validity
    valid1 = sum(1 for i in range(len(CRIB1_PLAIN))
                 if (K4[CRIB1_START+i] in fh_set) != (CRIB1_PLAIN[i] in fh_set))
    valid2 = sum(1 for i in range(len(CRIB2_PLAIN))
                 if (K4[CRIB2_START+i] in fh_set) != (CRIB2_PLAIN[i] in fh_set))

    print(f"    Crib1 cross-half pairs: {valid1}/{len(CRIB1_PLAIN)}")
    print(f"    Crib2 cross-half pairs: {valid2}/{len(CRIB2_PLAIN)}")

    if valid1 < len(CRIB1_PLAIN) or valid2 < len(CRIB2_PLAIN):
        print(f"    -> Cannot work: not all pairs cross halves")
    else:
        print(f"    -> All pairs cross halves! Testing periods 1-50...")
        found_any = False
        for period in range(1, 51):
            key_info = {}
            ok = True
            for crib_plain, crib_start in [(CRIB1_PLAIN, CRIB1_START), (CRIB2_PLAIN, CRIB2_START)]:
                for i in range(len(crib_plain)):
                    pos = crib_start + i
                    kp = pos % period
                    t = derive_custom_porta_tableau(K4[pos], crib_plain[i], fh_list, sh_list)
                    if t is None:
                        ok = False
                        break
                    if kp in key_info:
                        if key_info[kp] != t:
                            ok = False
                            break
                    key_info[kp] = t
                if not ok:
                    break

            if ok:
                found_any = True
                decrypted = []
                for j, c in enumerate(K4):
                    kp = j % period
                    if kp in key_info:
                        decrypted.append(custom_porta_decrypt_char(c, key_info[kp], fh_list, sh_list))
                    else:
                        decrypted.append('?')
                dec_text = ''.join(decrypted)
                known_text = dec_text.replace('?', '')
                sc = scorer.normalized_score(known_text) if len(known_text) >= 4 else -99.0
                known_count = sum(1 for c in dec_text if c != '?')

                print(f"      Period {period}: MATCH! Known={known_count} Score={sc:.4f}")
                print(f"        {dec_text}")

        if not found_any:
            print(f"    -> No consistent periods found")
    print()

# ============================================================
# TEST 4: BEAUFORT CIPHER (C = K - P mod 26)
# ============================================================
print("=" * 70)
print("TEST 4: BEAUFORT CIPHER (C = K - P mod 26)")
print("=" * 70)
print()

def beaufort_derive_key_char(cipher_char, plain_char, alphabet):
    """K = (C + P) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    p_idx = alphabet.index(plain_char)
    k_idx = (c_idx + p_idx) % n
    return alphabet[k_idx]

def beaufort_decrypt_char(cipher_char, key_char, alphabet):
    """P = (K - C) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    k_idx = alphabet.index(key_char)
    p_idx = (k_idx - c_idx) % n
    return alphabet[p_idx]

def test_polyalpha(cipher_name, derive_func, decrypt_func, alphabet, alpha_name, periods):
    """Generic tester for polyalphabetic ciphers."""
    results = []
    for period in periods:
        key_chars = {}
        ok = True
        for crib_plain, crib_start in [(CRIB1_PLAIN, CRIB1_START), (CRIB2_PLAIN, CRIB2_START)]:
            for i in range(len(crib_plain)):
                pos = crib_start + i
                kp = pos % period
                k = derive_func(K4[pos], crib_plain[i], alphabet)
                if kp in key_chars:
                    if key_chars[kp] != k:
                        ok = False
                        break
                key_chars[kp] = k
            if not ok:
                break

        if ok:
            decrypted = []
            for j, c in enumerate(K4):
                kp = j % period
                if kp in key_chars:
                    decrypted.append(decrypt_func(c, key_chars[kp], alphabet))
                else:
                    decrypted.append('?')
            dec_text = ''.join(decrypted)
            known_text = dec_text.replace('?', '')
            sc = scorer.normalized_score(known_text) if len(known_text) >= 4 else -99.0
            known_count = sum(1 for c in dec_text if c != '?')

            key_display = ''.join(key_chars.get(i, '?') for i in range(period))
            results.append((period, key_chars, dec_text, known_count, sc, key_display))

    return results

# Beaufort
for alpha_name, alphabet in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"--- Beaufort with {alpha_name} alphabet, periods 1-50 ---")

    results = test_polyalpha(
        "Beaufort", beaufort_derive_key_char, beaufort_decrypt_char,
        alphabet, alpha_name, range(1, 51)
    )

    if results:
        for period, kc, dec, known, sc, key_str in results:
            print(f"  Period {period:2d}: Key={key_str} Known={known}/{len(K4)} Score={sc:.4f}")
            print(f"    {dec}")
            print()
    else:
        print("  No consistent periods found.")
    print()

# ============================================================
# TEST 5: VARIANT BEAUFORT (C = P - K mod 26)
# ============================================================
print("=" * 70)
print("TEST 5: VARIANT BEAUFORT (C = P - K mod 26)")
print("=" * 70)
print()

def var_beaufort_derive_key_char(cipher_char, plain_char, alphabet):
    """K = (P - C) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    p_idx = alphabet.index(plain_char)
    k_idx = (p_idx - c_idx) % n
    return alphabet[k_idx]

def var_beaufort_decrypt_char(cipher_char, key_char, alphabet):
    """P = (C + K) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    k_idx = alphabet.index(key_char)
    p_idx = (c_idx + k_idx) % n
    return alphabet[p_idx]

for alpha_name, alphabet in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"--- Variant Beaufort with {alpha_name} alphabet, periods 1-50 ---")

    results = test_polyalpha(
        "VarBeaufort", var_beaufort_derive_key_char, var_beaufort_decrypt_char,
        alphabet, alpha_name, range(1, 51)
    )

    if results:
        for period, kc, dec, known, sc, key_str in results:
            print(f"  Period {period:2d}: Key={key_str} Known={known}/{len(K4)} Score={sc:.4f}")
            print(f"    {dec}")
            print()
    else:
        print("  No consistent periods found.")
    print()

# ============================================================
# TEST 6: STANDARD VIGENERE (C = P + K mod 26)
# ============================================================
print("=" * 70)
print("TEST 6: STANDARD VIGENERE (C = P + K mod 26)")
print("=" * 70)
print()

def vigenere_derive_key_char(cipher_char, plain_char, alphabet):
    """K = (C - P) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    p_idx = alphabet.index(plain_char)
    k_idx = (c_idx - p_idx) % n
    return alphabet[k_idx]

def vigenere_decrypt_char(cipher_char, key_char, alphabet):
    """P = (C - K) mod n"""
    n = len(alphabet)
    c_idx = alphabet.index(cipher_char)
    k_idx = alphabet.index(key_char)
    p_idx = (c_idx - k_idx) % n
    return alphabet[p_idx]

for alpha_name, alphabet in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    print(f"--- Vigenere with {alpha_name} alphabet, periods 1-50 ---")

    results = test_polyalpha(
        "Vigenere", vigenere_derive_key_char, vigenere_decrypt_char,
        alphabet, alpha_name, range(1, 51)
    )

    if results:
        for period, kc, dec, known, sc, key_str in results:
            print(f"  Period {period:2d}: Key={key_str} Known={known}/{len(K4)} Score={sc:.4f}")
            print(f"    {dec}")
            print()
    else:
        print("  No consistent periods found.")
    print()

# ============================================================
# TEST 7: DEEP DIVE - PERIOD 29 ANALYSIS
# ============================================================
print("=" * 70)
print("TEST 7: DEEP DIVE - PERIOD 29 KEY CONFLICT ANALYSIS")
print("=" * 70)
print()

for cipher_name, derive_func in [
    ("Beaufort (K=C+P)", beaufort_derive_key_char),
    ("Variant Beaufort (K=P-C)", var_beaufort_derive_key_char),
    ("Vigenere (K=C-P)", vigenere_derive_key_char),
]:
    for alpha_name, alphabet in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
        period = 29
        print(f"  {cipher_name} with {alpha_name} alphabet, period {period}:")

        key_chars = {}
        conflicts = []

        for crib_plain, crib_start, crib_name in [
            (CRIB1_PLAIN, CRIB1_START, "EASTNORTHEAST"),
            (CRIB2_PLAIN, CRIB2_START, "BERLINCLOCK"),
        ]:
            for i in range(len(crib_plain)):
                pos = crib_start + i
                kp = pos % period
                k = derive_func(K4[pos], crib_plain[i], alphabet)
                if kp in key_chars:
                    if key_chars[kp] != k:
                        conflicts.append((kp, key_chars[kp], k, crib_name, pos))
                else:
                    key_chars[kp] = k

        if conflicts:
            print(f"    CONFLICTS ({len(conflicts)}):")
            for kp, k1, k2, crib, pos in conflicts:
                print(f"      Key pos {kp}: existing='{k1}' new='{k2}' from {crib} at text pos {pos}")
        else:
            key_str = ''.join(key_chars.get(i, '?') for i in range(period))
            print(f"    CONSISTENT! Key ({len(key_chars)}/{period} known): {key_str}")
        print()

# ============================================================
# COMPREHENSIVE SUMMARY
# ============================================================
print("=" * 70)
print("COMPREHENSIVE SUMMARY")
print("=" * 70)
print()

all_results = []

# Collect Porta results
for period, key_info, dec, kc, sc in hits_standard:
    all_results.append(("Porta-Standard", period, dec, kc, sc))
for period, key_info, dec, kc, sc in hits_kryptos:
    all_results.append(("Porta-KRYPTOS", period, dec, kc, sc))

# Re-run Beaufort/VarBeaufort/Vigenere to collect
for cipher_name, derive_func, decrypt_func in [
    ("Beaufort", beaufort_derive_key_char, beaufort_decrypt_char),
    ("VarBeaufort", var_beaufort_derive_key_char, var_beaufort_decrypt_char),
    ("Vigenere", vigenere_derive_key_char, vigenere_decrypt_char),
]:
    for alpha_name, alphabet in [("STD", STANDARD_ALPHA), ("KRY", KRYPTOS_ALPHA)]:
        results = test_polyalpha(cipher_name, derive_func, decrypt_func, alphabet, alpha_name, range(1, 51))
        for period, kc, dec, known, sc, key_str in results:
            all_results.append((f"{cipher_name}-{alpha_name}", period, dec, known, sc))

if all_results:
    all_results.sort(key=lambda x: x[4], reverse=True)

    print(f"{'Cipher':<25} {'Period':>6} {'Known':>5} {'Score/char':>10}")
    print("-" * 50)
    for cipher, period, dec, kc, sc in all_results[:30]:
        print(f"{cipher:<25} {period:>6} {kc:>5} {sc:>10.4f}")

    print()
    print("Top 5 decryptions (by quadgram score):")
    for i, (cipher, period, dec, kc, sc) in enumerate(all_results[:5]):
        print(f"\n  #{i+1}: {cipher} period={period} score={sc:.4f} known={kc}/{len(K4)}")
        print(f"      {dec}")

    # Check if any score is close to English
    print()
    print(f"  English reference score: {scorer.normalized_score(ref_english):.4f}")
    best_sc = all_results[0][4]
    if best_sc > -2.5:
        print(f"  ** Best score {best_sc:.4f} is close to English! Worth investigating. **")
    elif best_sc > -3.0:
        print(f"  ** Best score {best_sc:.4f} is marginal. Possible partial plaintext. **")
    else:
        print(f"  ** Best score {best_sc:.4f} is far from English. These ciphers likely not the answer. **")
else:
    print("No consistent results found across any cipher/alphabet/period combination.")

print()
print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
