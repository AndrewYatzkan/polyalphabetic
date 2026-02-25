#!/usr/bin/env python3
"""
K4 HYDRA + Flipped Tableau Comprehensive Investigation
========================================================
Tests:
1. HYDRA as key modification (positions 16-20)
2. Flipped tableau brute-force (26^5 ~12M combos per variant)
3. Mixed approaches (alternating, Beaufort+HYDRA, etc.)
4. HYDRA-specific double encryption
"""

import math
import itertools
import time
import sys
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PERIOD = 29

# Known partial key (period 29): positions 0-15 known, 16-20 unknown, 21-28 known
KNOWN_KEY = "OYNKYELYOIECBAQK?????RDUMRIYW"

# Cribs
CRIB_ENE = ("EASTNORTHEAST", 21, 33)   # positions 21-33
CRIB_BC  = ("BERLINCLOCK", 63, 73)     # positions 63-73

DYAHR_LETTERS = "DYAHR"
HYDRA_STD = [7, 24, 3, 17, 0]  # H,Y,D,R,A in standard A=0

# Pre-compute alphabet index lookups
_K_IDX = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}
_S_IDX = {ch: i for i, ch in enumerate(STANDARD_ALPHA)}

# ============================================================
# LOAD QUADGRAM SCORER
# ============================================================

print("Loading quadgram statistics...")
QUADGRAMS = {}
QG_TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QUADGRAMS[parts[0]] = int(parts[1])
            QG_TOTAL += int(parts[1])

QG_LOG = {}
QG_FLOOR = math.log10(0.01 / QG_TOTAL)
for k, v in QUADGRAMS.items():
    QG_LOG[k] = math.log10(v / QG_TOTAL)

def score_text(text):
    """Score text using log quadgram frequencies. Higher = more English-like."""
    s = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        s += QG_LOG.get(qg, QG_FLOOR)
    return s

def score_per_char(text):
    """Normalized score per character."""
    if len(text) < 4:
        return -99.0
    return score_text(text) / (len(text) - 3)

# ============================================================
# KRYPTOS ALPHABET UTILITIES (optimized with lookup tables)
# ============================================================

def k_idx(ch):
    return _K_IDX[ch]

def k_chr(idx):
    return KRYPTOS_ALPHA[idx % 26]

def s_idx(ch):
    return _S_IDX[ch]

def s_chr(idx):
    return STANDARD_ALPHA[idx % 26]

# ============================================================
# VIGENERE VARIANTS (KRYPTOS ALPHABET)
# ============================================================

def vig_decrypt_k(ct_char, key_char):
    """Standard Vigenere decrypt using KRYPTOS alphabet: P = (C - K) mod 26"""
    return k_chr((k_idx(ct_char) - k_idx(key_char)) % 26)

def vig_encrypt_k(pt_char, key_char):
    """Standard Vigenere encrypt using KRYPTOS alphabet: C = (P + K) mod 26"""
    return k_chr((k_idx(pt_char) + k_idx(key_char)) % 26)

def beaufort_decrypt_k(ct_char, key_char):
    """Beaufort cipher decrypt: P = (K - C) mod 26 (KRYPTOS alphabet)
    Beaufort encrypt: C = (K - P) mod 26, so decrypt: P = (K - C) mod 26"""
    return k_chr((k_idx(key_char) - k_idx(ct_char)) % 26)

def variant_beaufort_decrypt_k(ct_char, key_char):
    """Variant Beaufort decrypt: encrypt was C = (P - K) mod 26,
    so decrypt: P = (C + K) mod 26"""
    return k_chr((k_idx(ct_char) + k_idx(key_char)) % 26)

def flip_row_decrypt(ct_char, key_char):
    """Flipped row order: reverse the alphabet for row (key) lookup.
    Encrypt: C = ((25 - K) + P) mod 26 = (25 - K + P) mod 26
    Decrypt: P = (C - 25 + K) mod 26 = (C + K - 25) mod 26"""
    return k_chr((k_idx(ct_char) + k_idx(key_char) - 25) % 26)

def flip_col_decrypt(ct_char, key_char):
    """Flipped column order: reverse the alphabet for col (plaintext) lookup.
    Encrypt: C = (K + (25 - P)) mod 26 = (K + 25 - P) mod 26
    Decrypt: (25 - P) = (C - K) mod 26, so P = (25 - C + K) mod 26"""
    return k_chr((25 - k_idx(ct_char) + k_idx(key_char)) % 26)

def flip_both_decrypt(ct_char, key_char):
    """Both rows and columns flipped (180-degree rotation).
    Encrypt: C = ((25 - K) + (25 - P)) mod 26 = (50 - K - P) mod 26 = (-K - P + 24) mod 26
    Decrypt: C = (24 - K - P) mod 26, so P = (24 - K - C) mod 26"""
    return k_chr((24 - k_idx(key_char) - k_idx(ct_char)) % 26)

def transpose_decrypt(ct_char, key_char):
    """Transposed tableau: swap row/col roles.
    Standard: C = (K + P) mod 26 -- symmetric, so transpose is the same for standard Vigenere.
    But if we think of it as: the crib-derived key was derived assuming standard roles,
    and the actual cipher transposed them, then the 'key' we derived is really the 'plaintext column'.
    For standard Vigenere this is the same. But let's implement swapped decrypt:
    Original encrypt: C = tableau[key_row][pt_col] = (K + P) mod 26
    Transposed: C = tableau[pt_row][key_col] = (P + K) mod 26 -- same.
    So transpose with standard Vigenere is identical. However, if we derive key differently...
    For completeness, just note this is same as standard."""
    return k_chr((k_idx(ct_char) - k_idx(key_char)) % 26)

# ============================================================
# KEY DERIVATION FROM CRIBS (for each method)
# ============================================================

def derive_key_standard(ct_char, pt_char):
    """K = (C - P) mod 26"""
    return k_chr((k_idx(ct_char) - k_idx(pt_char)) % 26)

def derive_key_beaufort(ct_char, pt_char):
    """Beaufort: C = (K - P), so K = (C + P) mod 26"""
    return k_chr((k_idx(ct_char) + k_idx(pt_char)) % 26)

def derive_key_variant_beaufort(ct_char, pt_char):
    """Variant Beaufort: C = (P - K), so K = (P - C) mod 26"""
    return k_chr((k_idx(pt_char) - k_idx(ct_char)) % 26)

def derive_key_flip_row(ct_char, pt_char):
    """Flip row: C = (25 - K + P), so K = (25 + P - C) mod 26"""
    return k_chr((25 + k_idx(pt_char) - k_idx(ct_char)) % 26)

def derive_key_flip_col(ct_char, pt_char):
    """Flip col: C = (K + 25 - P), so K = (C - 25 + P) mod 26"""
    return k_chr((k_idx(ct_char) - 25 + k_idx(pt_char)) % 26)

def derive_key_flip_both(ct_char, pt_char):
    """Flip both: C = (24 - K - P), so K = (24 - C - P) mod 26"""
    return k_chr((24 - k_idx(ct_char) - k_idx(pt_char)) % 26)

# Maps
DECRYPT_FUNCS = {
    'standard':          vig_decrypt_k,
    'beaufort':          beaufort_decrypt_k,
    'variant_beaufort':  variant_beaufort_decrypt_k,
    'flip_row':          flip_row_decrypt,
    'flip_col':          flip_col_decrypt,
    'flip_both':         flip_both_decrypt,
    'transpose':         transpose_decrypt,
}

DERIVE_FUNCS = {
    'standard':          derive_key_standard,
    'beaufort':          derive_key_beaufort,
    'variant_beaufort':  derive_key_variant_beaufort,
    'flip_row':          derive_key_flip_row,
    'flip_col':          derive_key_flip_col,
    'flip_both':         derive_key_flip_both,
    'transpose':         derive_key_standard,  # same as standard
}

# ============================================================
# DECRYPT/DERIVE HELPERS
# ============================================================

def decrypt_full(ciphertext, key, method='standard'):
    func = DECRYPT_FUNCS[method]
    return ''.join(func(ciphertext[i], key[i % len(key)]) for i in range(len(ciphertext)))

def derive_key_from_cribs(method='standard'):
    """Derive key chars from both cribs using the given method. Returns dict {pos: char}."""
    derive_fn = DERIVE_FUNCS[method]
    key_dict = {}
    # ENE crib
    for i, pt_ch in enumerate("EASTNORTHEAST"):
        ct_pos = 21 + i
        key_pos = ct_pos % PERIOD
        key_dict[key_pos] = derive_fn(K4_CIPHER[ct_pos], pt_ch)
    # BC crib
    for i, pt_ch in enumerate("BERLINCLOCK"):
        ct_pos = 63 + i
        key_pos = ct_pos % PERIOD
        key_dict[key_pos] = derive_fn(K4_CIPHER[ct_pos], pt_ch)
    return key_dict

def build_full_key(key_dict, period=29):
    return ''.join(key_dict.get(i, '?') for i in range(period))

def get_unknown_positions(key_dict, period=29):
    return [p for p in range(period) if p not in key_dict]

# ============================================================
# ENGLISH WORD CHECK
# ============================================================

COMMON_WORDS = set()
try:
    with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 4:
                COMMON_WORDS.add(w)
except:
    pass

def count_english_words(text, min_len=4):
    count = 0
    found = []
    for wlen in range(min_len, min(12, len(text)) + 1):
        for i in range(len(text) - wlen + 1):
            fragment = text[i:i+wlen]
            if fragment in COMMON_WORDS:
                count += 1
                if wlen >= 5:
                    found.append((i, fragment))
    return count, found

# ============================================================
# BASELINES
# ============================================================

import random
random.seed(42)
random_scores = [score_per_char(''.join(random.choices(STANDARD_ALPHA, k=97))) for _ in range(100)]
RANDOM_BASELINE = sum(random_scores) / len(random_scores)
ENGLISH_BASELINE = -2.3

print(f"Random baseline score/char: {RANDOM_BASELINE:.3f}")
print(f"English baseline score/char: ~{ENGLISH_BASELINE}")
print(f"K4 ciphertext length: {len(K4_CIPHER)}")
print(f"Known key: {KNOWN_KEY}")
print(f"Loaded {len(COMMON_WORDS)} English words for fragment detection")
print("=" * 80)

# ============================================================
# PRE-COMPUTE for fast brute-force
# ============================================================

# Pre-compute ciphertext indices in KRYPTOS alphabet
CT_K_IDX = [k_idx(ch) for ch in K4_CIPHER]

# For the brute force, we pre-compute the known key indices for each method
# Unknown positions are 16, 17, 18, 19, 20

def precompute_known_key_indices(key_dict):
    """Return array of key indices (KRYPTOS alphabet) for all 29 positions.
    Unknown positions get -1."""
    result = [-1] * PERIOD
    for pos, ch in key_dict.items():
        result[pos] = k_idx(ch)
    return result

def fast_bruteforce(method_name, key_dict, unknown_pos, top_n=5, label=""):
    """Brute-force 26^5 combinations for unknown positions.
    Uses optimized inner loop with pre-computed values.
    Returns top N results sorted by score."""

    assert len(unknown_pos) == 5, f"Expected 5 unknown positions, got {len(unknown_pos)}"

    # Pre-compute known key indices
    known_key_idx = precompute_known_key_indices(key_dict)

    # Pre-compute which key position each ciphertext position maps to
    ct_to_key = [i % PERIOD for i in range(97)]

    # Pre-compute which ciphertext positions use each unknown key position
    # For efficiency, pre-compute the decrypt mapping for all possible (ct_idx, key_idx) pairs
    # This avoids repeated function calls in the inner loop

    # Build decrypt tables: for each method, decrypt_table[c][k] = plaintext_index
    # Then plaintext char = KRYPTOS_ALPHA[plaintext_index]
    decrypt_table = [[0]*26 for _ in range(26)]

    if method_name == 'standard':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (c - k) % 26
    elif method_name == 'beaufort':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (k - c) % 26
    elif method_name == 'variant_beaufort':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (c + k) % 26
    elif method_name == 'flip_row':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (c + k - 25) % 26
    elif method_name == 'flip_col':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (25 - c + k) % 26
    elif method_name == 'flip_both':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (24 - k - c) % 26
    elif method_name == 'transpose':
        for c in range(26):
            for k in range(26):
                decrypt_table[c][k] = (c - k) % 26
    else:
        raise ValueError(f"Unknown method: {method_name}")

    # Pre-compute the plaintext for positions that use KNOWN key values
    # and track which positions need the brute-forced key values
    pt_indices_known = [0] * 97   # pre-filled where key is known
    needs_unknown = [False] * 97  # True if this CT position uses an unknown key position
    which_unknown = [0] * 97     # index into unknown_pos (0-4) for positions that need it

    for i in range(97):
        kp = ct_to_key[i]
        if known_key_idx[kp] >= 0:
            pt_indices_known[i] = decrypt_table[CT_K_IDX[i]][known_key_idx[kp]]
            needs_unknown[i] = False
        else:
            # Find which unknown position this corresponds to
            try:
                uidx = unknown_pos.index(kp)
                needs_unknown[i] = True
                which_unknown[i] = uidx
            except ValueError:
                # Should not happen
                pt_indices_known[i] = 0
                needs_unknown[i] = False

    # Precompute: for each unknown position (0-4), which CT positions use it
    unknown_ct_positions = [[] for _ in range(5)]
    for i in range(97):
        if needs_unknown[i]:
            unknown_ct_positions[which_unknown[i]].append(i)

    # Pre-build quadgram lookup as a flat array for speed
    # Convert quadgram indices to a single integer key

    # For the inner loop, we'll build plaintext as list of indices, then score
    # Score using quadgrams

    best = []  # list of (score, key_str, plaintext)
    worst_best = -float('inf')

    total = 26**5
    count = 0
    start_time = time.time()

    # Convert KRYPTOS_ALPHA to list for faster indexing
    ka = KRYPTOS_ALPHA

    for a in range(26):
        for b in range(26):
            for c in range(26):
                for d in range(26):
                    for e in range(26):
                        count += 1

                        # Build plaintext indices array
                        trial_keys = [a, b, c, d, e]

                        # Compute plaintext
                        pt_idx = list(pt_indices_known)
                        for uidx in range(5):
                            kv = trial_keys[uidx]
                            for pos in unknown_ct_positions[uidx]:
                                pt_idx[pos] = decrypt_table[CT_K_IDX[pos]][kv]

                        # Convert to string and score
                        pt = ''.join(ka[pi] for pi in pt_idx)
                        sc = score_text(pt)

                        if len(best) < top_n or sc > worst_best:
                            # Build key string
                            trial_key_dict = dict(key_dict)
                            for i, pos in enumerate(unknown_pos):
                                trial_key_dict[pos] = ka[trial_keys[i]]
                            key_str = build_full_key(trial_key_dict)

                            best.append((sc, key_str, pt))
                            best.sort(key=lambda x: x[0], reverse=True)
                            if len(best) > top_n:
                                best = best[:top_n]
                            worst_best = best[-1][0]

                        if count % 1000000 == 0:
                            elapsed = time.time() - start_time
                            rate = count / elapsed if elapsed > 0 else 0
                            eta = (total - count) / rate if rate > 0 else 0
                            print(f"  [{label}] {count:,}/{total:,} ({count*100//total}%) "
                                  f"rate={rate:,.0f}/s ETA={eta:.0f}s "
                                  f"best_score={best[0][0]:.1f}")
                            sys.stdout.flush()

    elapsed = time.time() - start_time
    print(f"  [{label}] COMPLETE: {count:,} combos in {elapsed:.1f}s ({count/elapsed:,.0f}/s)")
    sys.stdout.flush()

    return best


# ============================================================
# COLLECT ALL RESULTS
# ============================================================

all_results = []

def record_result(test_name, description, plaintext, key_used, score):
    all_results.append({
        'test': test_name,
        'desc': description,
        'plaintext': plaintext,
        'key': key_used,
        'score': score,
        'score_per_char': score / max(1, len(plaintext) - 3),
    })


# ############################################################
# TEST 1: HYDRA AS KEY MODIFICATION (positions 16-20)
# ############################################################

print("\n" + "=" * 80)
print("TEST 1: HYDRA / DYAHR permutations as key positions 16-20")
print("=" * 80)

# 1a: All 120 permutations of DYAHR with standard Vigenere
print("\n--- 1a: DYAHR permutations, standard Vigenere ---")
best_t1a = []
for perm in itertools.permutations("DYAHR"):
    perm_str = ''.join(perm)
    key = list(KNOWN_KEY)
    for i, ch in enumerate(perm_str):
        key[16 + i] = ch
    key_str = ''.join(key)
    pt = decrypt_full(K4_CIPHER, key_str, 'standard')
    sc = score_text(pt)
    spc = score_per_char(pt)
    best_t1a.append((spc, sc, perm_str, key_str, pt))
    record_result("T1a_DYAHR_std", perm_str, pt, key_str, sc)

best_t1a.sort(reverse=True)
print("Top 5 DYAHR permutations (standard Vigenere):")
for i, (spc, sc, perm, key, pt) in enumerate(best_t1a[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{perm}] score/char={spc:.3f} total={sc:.1f} words={wc}")
    print(f"     Key: {key}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")

# 1b: HYDRA modifying existing key (XOR, add, multiply mod 26)
print("\n--- 1b: HYDRA modifying known key (add/sub/xor/mul mod 26) ---")
best_t1b = []
hydra_k_vals = [k_idx(c) for c in "HYDRA"]

for perm in itertools.permutations("DYAHR"):
    perm_str = ''.join(perm)
    # Fill unknowns first
    base_key = list(KNOWN_KEY)
    for i, ch in enumerate(perm_str):
        base_key[16 + i] = ch
    base_key_str = ''.join(base_key)
    base_k_idx = [k_idx(ch) for ch in base_key_str]

    hydra_perm_vals = [k_idx(c) for c in perm_str]

    for op_name, op_fn in [
        ("add",  lambda ki, hi: (ki + hi) % 26),
        ("sub",  lambda ki, hi: (ki - hi) % 26),
        ("xor",  lambda ki, hi: (ki ^ hi) % 26),
        ("mul",  lambda ki, hi: (ki * hi) % 26),
    ]:
        # Apply HYDRA modification cyclically across entire key
        mod_key = ''.join(k_chr(op_fn(base_k_idx[i], hydra_k_vals[i % 5])) for i in range(PERIOD))
        pt = decrypt_full(K4_CIPHER, mod_key, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t1b.append((spc, sc, f"{op_name}_{perm_str}", mod_key, pt))

best_t1b.sort(reverse=True)
print("Top 5 HYDRA-modified key results:")
for i, (spc, sc, desc, key, pt) in enumerate(best_t1b[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     Key: {key}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")
    record_result("T1b_HYDRA_mod", desc, pt, key, sc)

# 1c: HYDRA repeated as second key layer (period 5)
print("\n--- 1c: HYDRA as second key layer (period 5) ---")
best_t1c = []
for perm_fill in itertools.permutations("DYAHR"):
    perm_fill_str = ''.join(perm_fill)
    base_key = list(KNOWN_KEY)
    for i, ch in enumerate(perm_fill_str):
        base_key[16 + i] = ch
    key_str = ''.join(base_key)

    # Decrypt with primary key, then decrypt result with "HYDRA" (period 5)
    intermediate = decrypt_full(K4_CIPHER, key_str, 'standard')
    for hydra_perm in [('H','Y','D','R','A'), ('D','Y','A','H','R'), ('A','R','D','H','Y'), ('R','H','A','D','Y'), ('Y','D','H','A','R')]:
        hydra_str = ''.join(hydra_perm)
        pt = decrypt_full(intermediate, hydra_str, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t1c.append((spc, sc, f"{perm_fill_str}+{hydra_str}", key_str, pt))

best_t1c.sort(reverse=True)
print("Top 5 double-layer results:")
for i, (spc, sc, desc, key, pt) in enumerate(best_t1c[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")
    record_result("T1c_double_layer", desc, pt, key, sc)

# 1d: HYDRA as primer for running key generation
print("\n--- 1d: HYDRA as primer for running key (autokey-like) ---")
best_t1d = []
for perm in itertools.permutations("DYAHR"):
    perm_str = ''.join(perm)
    base_key = list(KNOWN_KEY)
    for i, ch in enumerate(perm_str):
        base_key[16 + i] = ch
    key_str = ''.join(base_key)

    # Autokey variant: after exhausting the key, use plaintext as key (plaintext autokey)
    pt_chars = []
    for i in range(len(K4_CIPHER)):
        if i < PERIOD:
            k_char = key_str[i]
        else:
            k_char = pt_chars[i - PERIOD]  # use plaintext from PERIOD positions back
        pt_chars.append(vig_decrypt_k(K4_CIPHER[i], k_char))
    pt = ''.join(pt_chars)
    sc = score_text(pt)
    spc = score_per_char(pt)
    best_t1d.append((spc, sc, f"autokey_{perm_str}", key_str, pt))

    # Ciphertext autokey variant
    ct_chars = []
    for i in range(len(K4_CIPHER)):
        if i < PERIOD:
            k_char = key_str[i]
        else:
            k_char = K4_CIPHER[i - PERIOD]  # use ciphertext from PERIOD positions back
        ct_chars.append(vig_decrypt_k(K4_CIPHER[i], k_char))
    pt2 = ''.join(ct_chars)
    sc2 = score_text(pt2)
    spc2 = score_per_char(pt2)
    best_t1d.append((spc2, sc2, f"ct_autokey_{perm_str}", key_str, pt2))

best_t1d.sort(reverse=True)
print("Top 5 autokey results:")
for i, (spc, sc, desc, key, pt) in enumerate(best_t1d[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")
    record_result("T1d_autokey", desc, pt, key, sc)


# ############################################################
# TEST 2: FLIPPED TABLEAU BRUTE-FORCE (26^5 per variant)
# ############################################################

print("\n" + "=" * 80)
print("TEST 2: Flipped tableau brute-force (26^5 = 11,881,376 per variant)")
print("=" * 80)

tableau_methods = [
    'standard',
    'beaufort',
    'variant_beaufort',
    'flip_row',
    'flip_col',
    'flip_both',
]

for method in tableau_methods:
    print(f"\n{'='*60}")
    print(f"  BRUTE-FORCING: {method}")
    print(f"{'='*60}")

    # Derive key from cribs using this method
    key_dict = derive_key_from_cribs(method)
    key_partial = build_full_key(key_dict)
    unknown_pos = get_unknown_positions(key_dict)

    print(f"  Derived key: {key_partial}")
    print(f"  Unknown positions: {unknown_pos}")

    if len(unknown_pos) != 5:
        print(f"  WARNING: Expected 5 unknowns, got {len(unknown_pos)}. Skipping brute-force.")
        # Still try DYAHR permutations
        if len(unknown_pos) < 5:
            print(f"  (Over-determined: fewer than 5 unknowns due to crib overlap at this period)")
        continue

    results = fast_bruteforce(method, key_dict, unknown_pos, top_n=5, label=method)

    print(f"\n  TOP 5 RESULTS for {method}:")
    for rank, (sc, key_str, pt) in enumerate(results):
        spc = sc / max(1, len(pt) - 3)
        wc, wds = count_english_words(pt)
        print(f"    {rank+1}. score={sc:.1f} score/char={spc:.3f} words={wc}")
        print(f"       Key: {key_str}")
        print(f"       PT:  {pt}")
        if wds:
            print(f"       Words: {wds[:5]}")
        record_result(f"T2_bf_{method}", f"bf_{key_str[16:21]}", pt, key_str, sc)

    # Also check: does HYDRA appear in the top results?
    hydra_key = dict(key_dict)
    for i, pos in enumerate(unknown_pos):
        hydra_key[pos] = "HYDRA"[i]
    hydra_key_str = build_full_key(hydra_key)
    hydra_pt = decrypt_full(K4_CIPHER, hydra_key_str, method)
    hydra_sc = score_text(hydra_pt)
    hydra_spc = score_per_char(hydra_pt)
    wc, wds = count_english_words(hydra_pt)
    print(f"\n  HYDRA check ({method}): score={hydra_sc:.1f} score/char={hydra_spc:.3f} words={wc}")
    print(f"    Key: {hydra_key_str}")
    print(f"    PT:  {hydra_pt}")
    if wds:
        print(f"    Words: {wds[:5]}")
    record_result(f"T2_HYDRA_{method}", "HYDRA_at_unknowns", hydra_pt, hydra_key_str, hydra_sc)


# ############################################################
# TEST 3: MIXED APPROACHES
# ############################################################

print("\n" + "=" * 80)
print("TEST 3: Mixed approaches")
print("=" * 80)

# 3a: Beaufort with HYDRA at positions 16-20 (using standard-derived key for other positions)
print("\n--- 3a: Beaufort with HYDRA at positions 16-20 ---")
beau_key_dict = derive_key_from_cribs('beaufort')
beau_unknown = get_unknown_positions(beau_key_dict)
print(f"  Beaufort key: {build_full_key(beau_key_dict)}")
print(f"  Unknown: {beau_unknown}")

for hydra_perm in itertools.permutations("HYDRA"):
    hp = ''.join(hydra_perm)
    test_key = dict(beau_key_dict)
    for i, pos in enumerate(beau_unknown):
        if i < 5:
            test_key[pos] = hp[i]
    key_str = build_full_key(test_key)
    if '?' in key_str:
        continue
    pt = decrypt_full(K4_CIPHER, key_str, 'beaufort')
    sc = score_text(pt)
    spc = score_per_char(pt)
    if hp == "HYDRA":
        wc, wds = count_english_words(pt)
        print(f"  HYDRA: score/char={spc:.3f} words={wc}")
        print(f"    Key: {key_str}")
        print(f"    PT:  {pt}")
    record_result("T3a_beau_hydra", hp, pt, key_str, sc)

# 3b: Odd/even positions use different tableau orientations
print("\n--- 3b: Alternating Vigenere/Beaufort by position ---")

def decrypt_alternating(ciphertext, key, method_even, method_odd):
    func_even = DECRYPT_FUNCS[method_even]
    func_odd = DECRYPT_FUNCS[method_odd]
    result = []
    for i, c in enumerate(ciphertext):
        k = key[i % len(key)]
        if i % 2 == 0:
            result.append(func_even(c, k))
        else:
            result.append(func_odd(c, k))
    return ''.join(result)

def derive_key_alternating(method_even, method_odd):
    """Derive key using alternating methods from cribs."""
    fn_even = DERIVE_FUNCS[method_even]
    fn_odd = DERIVE_FUNCS[method_odd]
    key_dict = {}
    for i, pt_ch in enumerate("EASTNORTHEAST"):
        ct_pos = 21 + i
        key_pos = ct_pos % PERIOD
        if ct_pos % 2 == 0:
            key_dict[key_pos] = fn_even(K4_CIPHER[ct_pos], pt_ch)
        else:
            key_dict[key_pos] = fn_odd(K4_CIPHER[ct_pos], pt_ch)
    for i, pt_ch in enumerate("BERLINCLOCK"):
        ct_pos = 63 + i
        key_pos = ct_pos % PERIOD
        if ct_pos % 2 == 0:
            key_dict[key_pos] = fn_even(K4_CIPHER[ct_pos], pt_ch)
        else:
            key_dict[key_pos] = fn_odd(K4_CIPHER[ct_pos], pt_ch)
    return key_dict

alt_combos = [
    ('standard', 'beaufort'),
    ('beaufort', 'standard'),
    ('standard', 'flip_col'),
    ('flip_col', 'standard'),
    ('standard', 'variant_beaufort'),
    ('variant_beaufort', 'standard'),
    ('beaufort', 'variant_beaufort'),
    ('variant_beaufort', 'beaufort'),
    ('flip_row', 'flip_col'),
    ('flip_col', 'flip_row'),
    ('standard', 'flip_row'),
    ('flip_row', 'standard'),
    ('standard', 'flip_both'),
    ('flip_both', 'standard'),
]

best_t3b = []
for me, mo in alt_combos:
    key_dict = derive_key_alternating(me, mo)
    unknown_pos = get_unknown_positions(key_dict)

    for perm in itertools.permutations("DYAHR"):
        perm_str = ''.join(perm)
        full_key = dict(key_dict)
        for i, ch in enumerate(perm_str):
            if i < len(unknown_pos):
                full_key[unknown_pos[i]] = ch
        key_str = build_full_key(full_key)
        if '?' in key_str:
            continue
        pt = decrypt_alternating(K4_CIPHER, key_str, me, mo)
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t3b.append((spc, sc, f"{me}/{mo}", perm_str, key_str, pt))

best_t3b.sort(reverse=True)
print("Top 10 alternating method results:")
for i, (spc, sc, methods, perm, key, pt) in enumerate(best_t3b[:10]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{methods}] [{perm}] score/char={spc:.3f} words={wc}")
    print(f"     Key: {key}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Words: {wds[:5]}")
    record_result(f"T3b_alt_{methods}", perm, pt, key, sc)

# 3c: Key derived from HYDRA permutation applied to known key
print("\n--- 3c: HYDRA permutation as key permutation cipher ---")
best_t3c = []

# Use HYDRA letter indices to permute the key
for perm in itertools.permutations(range(5)):
    # Fill positions 16-20 with the known key reordered by HYDRA permutation
    # But positions 16-20 are unknown... so use HYDRA letters permuted
    for hydra_perm in itertools.permutations("HYDRA"):
        hp = ''.join(hydra_perm)
        # Apply permutation to the HYDRA letters
        permuted = ''.join(hp[p] for p in perm)
        base_key = list(KNOWN_KEY)
        for i, ch in enumerate(permuted):
            base_key[16 + i] = ch
        key_str = ''.join(base_key)
        pt = decrypt_full(K4_CIPHER, key_str, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t3c.append((spc, sc, f"{hp}->{permuted}", key_str, pt))

best_t3c.sort(reverse=True)
# Deduplicate since many permutations of permutations give same result
seen = set()
count_printed = 0
print("Top 5 unique HYDRA-permuted key results:")
for spc, sc, desc, key, pt in best_t3c:
    if pt in seen:
        continue
    seen.add(pt)
    count_printed += 1
    if count_printed > 5:
        break
    wc, wds = count_english_words(pt)
    print(f"  {count_printed}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    record_result("T3c_hydra_perm", desc, pt, key, sc)


# ############################################################
# TEST 4: HYDRA-SPECIFIC CIPHER (Double encryption)
# ############################################################

print("\n" + "=" * 80)
print("TEST 4: HYDRA-specific double encryption")
print("=" * 80)

# 4a: K4 = Vig(Vig(PT, key1_period29), key2_period5_HYDRA)
# Decrypt: PT = Vig_dec(Vig_dec(K4, key2_HYDRA), key1_period29)
print("\n--- 4a: Double Vig - decrypt HYDRA(period5) first, then key(period29) ---")
best_t4a = []
for hydra_perm in itertools.permutations("HYDRA"):
    hp = ''.join(hydra_perm)
    # First strip off HYDRA layer
    intermediate = decrypt_full(K4_CIPHER, hp, 'standard')
    # Then decrypt with known key (try all DYAHR fills for unknowns)
    for fill_perm in itertools.permutations("DYAHR"):
        fp = ''.join(fill_perm)
        base_key = list(KNOWN_KEY)
        for i, ch in enumerate(fp):
            base_key[16 + i] = ch
        key_str = ''.join(base_key)
        pt = decrypt_full(intermediate, key_str, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t4a.append((spc, sc, f"hydra={hp},fill={fp}", key_str, pt))

best_t4a.sort(reverse=True)
print("Top 5 results (strip HYDRA first, then period-29 key):")
for i, (spc, sc, desc, key, pt) in enumerate(best_t4a[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")
    record_result("T4a_double_vig", desc, pt, key, sc)

# 4b: Decrypt period-29 key first, then strip HYDRA
print("\n--- 4b: Double Vig - decrypt key(period29) first, then HYDRA(period5) ---")
best_t4b = []
for fill_perm in itertools.permutations("DYAHR"):
    fp = ''.join(fill_perm)
    base_key = list(KNOWN_KEY)
    for i, ch in enumerate(fp):
        base_key[16 + i] = ch
    key_str = ''.join(base_key)
    intermediate = decrypt_full(K4_CIPHER, key_str, 'standard')
    for hydra_perm in itertools.permutations("HYDRA"):
        hp = ''.join(hydra_perm)
        pt = decrypt_full(intermediate, hp, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        best_t4b.append((spc, sc, f"fill={fp},hydra={hp}", key_str, pt))

best_t4b.sort(reverse=True)
print("Top 5 results (strip period-29 first, then HYDRA):")
for i, (spc, sc, desc, key, pt) in enumerate(best_t4b[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    if wds:
        print(f"     Found words: {wds[:5]}")
    record_result("T4b_double_vig_rev", desc, pt, key, sc)

# 4c: Double encryption with Beaufort as one layer
print("\n--- 4c: Mixed double encryption (Vig+Beaufort, Beaufort+Vig, Beaufort+Beaufort) ---")
best_t4c = []
double_combos = [
    ('standard', 'beaufort', "vig_then_beau"),
    ('beaufort', 'standard', "beau_then_vig"),
    ('beaufort', 'beaufort', "beau_then_beau"),
    ('standard', 'variant_beaufort', "vig_then_varbeau"),
    ('variant_beaufort', 'standard', "varbeau_then_vig"),
]

for m1, m2, combo_name in double_combos:
    for hydra_perm in [('H','Y','D','R','A'), ('D','Y','A','H','R')]:
        hp = ''.join(hydra_perm)
        # Decrypt outer layer (HYDRA, period 5)
        intermediate = decrypt_full(K4_CIPHER, hp, m1)
        # Decrypt inner layer (known key, period 29)
        for fill_perm in [('H','Y','D','R','A'), ('D','Y','A','H','R'), ('A','R','D','H','Y')]:
            fp = ''.join(fill_perm)
            base_key = list(KNOWN_KEY)
            for i, ch in enumerate(fp):
                base_key[16 + i] = ch
            key_str = ''.join(base_key)
            pt = decrypt_full(intermediate, key_str, m2)
            sc = score_text(pt)
            spc = score_per_char(pt)
            best_t4c.append((spc, sc, f"{combo_name}:hydra={hp},fill={fp}", key_str, pt))

best_t4c.sort(reverse=True)
print("Top 5 mixed double encryption results:")
for i, (spc, sc, desc, key, pt) in enumerate(best_t4c[:5]):
    wc, wds = count_english_words(pt)
    print(f"  {i+1}. [{desc}] score/char={spc:.3f} words={wc}")
    print(f"     PT:  {pt}")
    record_result("T4c_mixed_double", desc, pt, key, sc)

# 4d: Since double Vigenere with same period = single Vigenere with combined key,
# test different period for HYDRA (period 5 vs period 29)
# The combined effect of period-29 + period-5 keys = period LCM(29,5) = 145
# which is longer than K4 (97 chars), so effectively a period-97 key
print("\n--- 4d: Combined key analysis (period 29 + period 5 = effectively period 145) ---")
# Since LCM(29,5)=145 > 97, the combined key has 97 unique chars
# Compute the combined key for a few HYDRA variants
for hp_str in ["HYDRA", "DYAHR", "ARDHY", "RHYDA", "YAHDR"]:
    for fp_str in ["HYDRA", "DYAHR"]:
        base_key = list(KNOWN_KEY)
        for i, ch in enumerate(fp_str):
            base_key[16 + i] = ch
        key29 = ''.join(base_key)

        # Combined key at position i: (key29[i%29] + hydra[i%5]) mod 26
        combined = []
        for i in range(97):
            k29_val = k_idx(key29[i % 29])
            h5_val = k_idx(hp_str[i % 5])
            combined.append(k_chr((k29_val + h5_val) % 26))
        combined_key = ''.join(combined)

        pt = decrypt_full(K4_CIPHER, combined_key, 'standard')
        sc = score_text(pt)
        spc = score_per_char(pt)
        if hp_str == "HYDRA" and fp_str == "HYDRA":
            wc, wds = count_english_words(pt)
            print(f"  Combined key (HYDRA+HYDRA): score/char={spc:.3f} words={wc}")
            print(f"    PT: {pt}")
        record_result("T4d_combined", f"{fp_str}+{hp_str}", pt, combined_key[:29]+"...", sc)

# ############################################################
# GRAND SUMMARY
# ############################################################

print("\n" + "=" * 80)
print("GRAND SUMMARY: TOP 25 RESULTS ACROSS ALL TESTS")
print("=" * 80)

all_results_sorted = sorted(all_results, key=lambda x: x['score_per_char'], reverse=True)

seen_pt = set()
rank = 0
for r in all_results_sorted:
    if r['plaintext'] in seen_pt:
        continue
    seen_pt.add(r['plaintext'])
    rank += 1
    if rank > 25:
        break
    wc, wds = count_english_words(r['plaintext'])
    marker = " ***" if r['score_per_char'] > -3.5 else ""
    print(f"\n  #{rank} [{r['test']}] score/char={r['score_per_char']:.3f} words={wc}{marker}")
    print(f"     Desc: {r['desc']}")
    print(f"     Key:  {r['key']}")
    print(f"     PT:   {r['plaintext']}")
    if wds:
        print(f"     English words found: {wds[:8]}")

# ============================================================
# STATISTICAL ANALYSIS
# ============================================================

print("\n" + "=" * 80)
print("STATISTICAL ANALYSIS")
print("=" * 80)

if all_results:
    scores = [r['score_per_char'] for r in all_results]
    print(f"  Total decryptions tested: {len(all_results)}")
    print(f"  Score/char range: [{min(scores):.3f}, {max(scores):.3f}]")
    print(f"  Mean score/char: {sum(scores)/len(scores):.3f}")
    print(f"  Random text baseline: {RANDOM_BASELINE:.3f}")
    print(f"  English text baseline: ~{ENGLISH_BASELINE}")

    above_threshold = [r for r in all_results if r['score_per_char'] > -3.5]
    print(f"  Results above -3.5 threshold: {len(above_threshold)}")

    if above_threshold:
        print("\n  PROMISING RESULTS (score/char > -3.5):")
        for r in sorted(above_threshold, key=lambda x: x['score_per_char'], reverse=True)[:10]:
            print(f"    {r['test']}: {r['desc']} -> score/char={r['score_per_char']:.3f}")
            print(f"      PT: {r['plaintext'][:60]}...")
    else:
        print("\n  No results exceeded the -3.5 English-like threshold.")
        print("  This suggests none of the tested hypotheses alone crack K4,")
        print("  OR the unknown key positions are not a simple DYAHR anagram,")
        print("  OR there is an additional transformation layer not yet tested.")

# Method-by-method comparison for brute-force results
print("\n" + "=" * 80)
print("BRUTE-FORCE METHOD COMPARISON (Test 2)")
print("=" * 80)

bf_results = [r for r in all_results if r['test'].startswith('T2_bf_')]
if bf_results:
    by_method = defaultdict(list)
    for r in bf_results:
        method = r['test'].replace('T2_bf_', '')
        by_method[method].append(r)

    print(f"\n  {'Method':<25} {'Best Score/Char':>15} {'Best Total':>12} {'Words':>6}")
    print(f"  {'-'*25} {'-'*15} {'-'*12} {'-'*6}")
    for method in tableau_methods:
        if method in by_method:
            best = max(by_method[method], key=lambda x: x['score_per_char'])
            wc, _ = count_english_words(best['plaintext'])
            print(f"  {method:<25} {best['score_per_char']:>15.3f} {best['score']:>12.1f} {wc:>6}")
            print(f"    Best key: {best['key']}")
            print(f"    Best PT:  {best['plaintext'][:60]}...")

# HYDRA-specific summary
print("\n" + "=" * 80)
print("HYDRA-SPECIFIC SUMMARY")
print("=" * 80)

hydra_results = [r for r in all_results if 'HYDRA' in r['desc'] or 'HYDRA' in r['test']]
if hydra_results:
    best_hydra = max(hydra_results, key=lambda x: x['score_per_char'])
    print(f"  Best HYDRA-related result:")
    print(f"    Test: {best_hydra['test']}")
    print(f"    Desc: {best_hydra['desc']}")
    print(f"    Score/char: {best_hydra['score_per_char']:.3f}")
    print(f"    Key: {best_hydra['key']}")
    print(f"    PT:  {best_hydra['plaintext']}")
    wc, wds = count_english_words(best_hydra['plaintext'])
    print(f"    Words found: {wc}")
    if wds:
        print(f"    Specific words: {wds[:10]}")

print("\n" + "=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
