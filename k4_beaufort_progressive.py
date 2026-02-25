#!/usr/bin/env python3
"""
Comprehensive test of Beaufort cipher variants and progressive cipher modifications on K4.

Tests:
  1. Beaufort key derivation (4 operations) + brute-force unknowns
  2. Progressive key modification (shift, pattern, autokey hybrid, cipher feedback)
  3. Split Beaufort/Vigenere combinations
  4. Keyed Beaufort with different tableau alphabets
  5. Reciprocal Beaufort property verification

Scoring: quadgram log-probabilities from english_quadgrams.txt
"""

import math
import time
import sys
from itertools import product

# =============================================================================
# CONSTANTS
# =============================================================================

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4_CT)  # 97

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA  = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHA_SIZE = 26

PERIOD = 29

# Known cribs
CRIB_BERLIN = ("BERLINCLOCK", 63)
CRIB_ENE    = ("EASTNORTHEAST", 21)

# Known partial Vigenere key (period 29): positions 0-15 and 21-28 known
# Positions 16-20 are unknown (marked ?)
VIGENERE_KEY_TEMPLATE = "OYNKYELYOIECBAQK?????RDUMRIYW"
UNKNOWN_POS = [16, 17, 18, 19, 20]

# =============================================================================
# ALPHABET UTILITIES
# =============================================================================

def build_alpha_maps(alpha):
    """Build char->index and index->char maps for an alphabet."""
    c2i = {}
    for i, ch in enumerate(alpha):
        c2i[ch] = i
    i2c = list(alpha)
    return c2i, i2c

def make_keyed_alphabet(keyword, base_alpha=STANDARD_ALPHA):
    """Create a keyed alphabet: keyword letters first (deduplicated), then remaining."""
    seen = set()
    result = []
    for ch in keyword.upper():
        if ch in base_alpha and ch not in seen:
            seen.add(ch)
            result.append(ch)
    for ch in base_alpha:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return ''.join(result)

# Build maps for both alphabets
STD_C2I, STD_I2C = build_alpha_maps(STANDARD_ALPHA)
KRY_C2I, KRY_I2C = build_alpha_maps(KRYPTOS_ALPHA)

# =============================================================================
# QUADGRAM SCORING
# =============================================================================

print("Loading quadgram frequencies...")
t0 = time.time()

QUADGRAMS = {}
total_count = 0

with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram = parts[0]
            count = int(parts[1])
            QUADGRAMS[gram] = count
            total_count += count

log_total = math.log10(total_count)
for gram in QUADGRAMS:
    QUADGRAMS[gram] = math.log10(QUADGRAMS[gram]) - log_total

FLOOR = math.log10(0.01) - log_total

print(f"  Loaded {len(QUADGRAMS)} quadgrams in {time.time()-t0:.2f}s")
print(f"  Floor score per quadgram: {FLOOR:.4f}")

def score_text(text):
    """Score plaintext string using quadgram log-probabilities."""
    text = text.upper()
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QUADGRAMS.get(qg, FLOOR)
    return score

def score_indices(pt_indices, i2c):
    """Score plaintext index array using quadgram log-probabilities."""
    text = ''.join(i2c[idx] for idx in pt_indices)
    return score_text(text)

# =============================================================================
# CIPHER OPERATIONS (generic, work with any alphabet)
# =============================================================================

def vigenere_decrypt_idx(ct_idx, key_idx, mod=26):
    """Vigenere: PT = (CT - KEY) mod 26"""
    return (ct_idx - key_idx) % mod

def beaufort_decrypt_idx(ct_idx, key_idx, mod=26):
    """Beaufort: PT = (KEY - CT) mod 26"""
    return (key_idx - ct_idx) % mod

def variant_beaufort_decrypt_idx(ct_idx, key_idx, mod=26):
    """Variant Beaufort: PT = (CT - KEY) mod 26 ... same as Vigenere decrypt
       Actually Variant Beaufort encrypt: CT = (PT - KEY) mod 26
       So decrypt: PT = (CT + KEY) mod 26"""
    return (ct_idx + key_idx) % mod

def decrypt_full(ct_str, key_indices, period, c2i, i2c, decrypt_func):
    """Decrypt full ciphertext with given decrypt function."""
    ct_idx = [c2i[ch] for ch in ct_str]
    pt_idx = []
    for i in range(len(ct_idx)):
        k = key_indices[i % period]
        pt_idx.append(decrypt_func(ct_idx[i], k))
    return ''.join(i2c[p] for p in pt_idx)

# =============================================================================
# GLOBAL RESULTS TRACKING
# =============================================================================

ALL_RESULTS = []  # (score, description, plaintext, key_info)
THRESHOLD = -550  # Store results above this threshold for reporting

def record_result(score, desc, plaintext, key_info=""):
    """Record a result if it meets the threshold."""
    ALL_RESULTS.append((score, desc, plaintext, key_info))

# =============================================================================
# SECTION 1: BEAUFORT KEY DERIVATION FROM CRIBS
# =============================================================================

def section1_beaufort_key_derivation():
    """Derive keys using 4 different operations from cribs, then brute-force unknowns."""
    print("\n" + "="*80)
    print("SECTION 1: BEAUFORT KEY DERIVATION FROM CRIBS")
    print("="*80)

    # We have two cribs and two alphabets
    alphabets = [
        ("STANDARD", STANDARD_ALPHA, STD_C2I, STD_I2C),
        ("KRYPTOS",  KRYPTOS_ALPHA,  KRY_C2I, KRY_I2C),
    ]

    # Four key derivation operations
    operations = [
        ("(a) key=(CT-PT) mod 26  [std Vigenere]",   lambda ct, pt, m: (ct - pt) % m),
        ("(b) key=(CT+PT) mod 26  [Beaufort rel]",    lambda ct, pt, m: (ct + pt) % m),
        ("(c) key=(PT-CT) mod 26  [variant Beaufort]", lambda ct, pt, m: (pt - ct) % m),
        ("(d) key=(26-CT-PT) mod 26 [-CT-PT]",        lambda ct, pt, m: (m - ct - pt) % m),
    ]

    # Corresponding decryption functions for each key derivation
    # If key = (CT - PT), then PT = (CT - key) -> Vigenere decrypt
    # If key = (CT + PT), then PT = (key - CT) -> Beaufort decrypt
    # If key = (PT - CT), then PT = (CT + key) -> Variant Beaufort decrypt
    # If key = (26-CT-PT), then CT = (26 - key - PT), PT = (26 - key - CT) = (-key - CT)
    decrypt_funcs = [
        ("Vigenere",         vigenere_decrypt_idx),
        ("Beaufort",         beaufort_decrypt_idx),
        ("Variant Beaufort", variant_beaufort_decrypt_idx),
        ("Negated",          lambda ct, k, m=26: (m - k - ct) % m),
    ]

    cribs = [CRIB_BERLIN, CRIB_ENE]

    for alpha_name, alpha, c2i, i2c in alphabets:
        print(f"\n--- Alphabet: {alpha_name} ({alpha}) ---")
        ct_idx = [c2i[ch] for ch in K4_CT]

        for op_idx, (op_name, op_func) in enumerate(operations):
            print(f"\n  Operation {op_name}:")

            # Derive key from both cribs
            key_from_cribs = [None] * PERIOD

            for crib_text, crib_pos in cribs:
                pt_idx_crib = [c2i[ch] for ch in crib_text]
                for j, ch in enumerate(crib_text):
                    pos = crib_pos + j
                    key_pos = pos % PERIOD
                    derived = op_func(ct_idx[pos], pt_idx_crib[j], ALPHA_SIZE)
                    derived_char = i2c[derived]

                    if key_from_cribs[key_pos] is not None and key_from_cribs[key_pos] != derived:
                        print(f"    CONFLICT at key pos {key_pos}: "
                              f"was {i2c[key_from_cribs[key_pos]]}, now {derived_char}")
                    key_from_cribs[key_pos] = derived

            # Show derived key
            key_str = ""
            unknown_positions = []
            for i in range(PERIOD):
                if key_from_cribs[i] is not None:
                    key_str += i2c[key_from_cribs[i]]
                else:
                    key_str += "?"
                    unknown_positions.append(i)

            print(f"    Derived key: {key_str}")
            print(f"    Unknown positions: {unknown_positions}")

            # Check if positions 16-20 are the unknowns (matching expected pattern)
            if len(unknown_positions) <= 7:
                # Brute-force the unknowns
                n_unknown = len(unknown_positions)
                dec_func = decrypt_funcs[op_idx][1]

                if n_unknown <= 5:
                    total_combos = ALPHA_SIZE ** n_unknown
                    print(f"    Brute-forcing {n_unknown} unknowns ({total_combos:,} combos)...")

                    best_score = -float('inf')
                    best_key = None
                    best_pt = None

                    # Pre-compute static decryption
                    static_pt = [0] * K4_LEN
                    for i in range(K4_LEN):
                        kp = i % PERIOD
                        if key_from_cribs[kp] is not None:
                            static_pt[i] = dec_func(ct_idx[i], key_from_cribs[kp])

                    for combo in product(range(ALPHA_SIZE), repeat=n_unknown):
                        # Fill in unknowns
                        trial_key = list(key_from_cribs)
                        for idx, up in enumerate(unknown_positions):
                            trial_key[up] = combo[idx]

                        # Decrypt
                        pt_indices = list(static_pt)
                        for up_idx, up in enumerate(unknown_positions):
                            for i in range(up, K4_LEN, PERIOD):
                                pt_indices[i] = dec_func(ct_idx[i], combo[up_idx])

                        # Score
                        pt_str = ''.join(i2c[p] for p in pt_indices)
                        sc = score_text(pt_str)

                        if sc > best_score:
                            best_score = sc
                            best_key = ''.join(i2c[k] for k in trial_key)
                            best_pt = pt_str

                    print(f"    BEST score: {best_score:.1f}")
                    print(f"    BEST key:   {best_key}")
                    print(f"    BEST PT:    {best_pt[:50]}...")

                    record_result(best_score,
                                  f"S1:{alpha_name}:{op_name[:20]}",
                                  best_pt, best_key)

                    # Also show top result for positions 16-20 portion
                    if best_score > -500:
                        print(f"    *** HIGH SCORE: {best_score:.1f} ***")
                        print(f"    Full plaintext: {best_pt}")

                elif n_unknown <= 7:
                    print(f"    {n_unknown} unknowns = {ALPHA_SIZE**n_unknown:,} combos (too many, sampling...)")
                    # For 6-7 unknowns, try hill-climbing approach
                    # Start with random, optimize one position at a time
                    import random
                    random.seed(42)

                    best_score = -float('inf')
                    best_key = None
                    best_pt = None

                    for trial in range(500):  # 500 random starting points
                        trial_key = list(key_from_cribs)
                        for up in unknown_positions:
                            trial_key[up] = random.randint(0, ALPHA_SIZE - 1)

                        # Hill climb
                        improved = True
                        while improved:
                            improved = False
                            for up in unknown_positions:
                                best_val = trial_key[up]
                                current_pt = [0] * K4_LEN
                                for i in range(K4_LEN):
                                    kp = i % PERIOD
                                    current_pt[i] = dec_func(ct_idx[i], trial_key[kp])
                                current_score = score_indices(current_pt, i2c)

                                for v in range(ALPHA_SIZE):
                                    if v == trial_key[up]:
                                        continue
                                    old = trial_key[up]
                                    trial_key[up] = v
                                    test_pt = list(current_pt)
                                    for i in range(up, K4_LEN, PERIOD):
                                        test_pt[i] = dec_func(ct_idx[i], v)
                                    sc = score_indices(test_pt, i2c)
                                    if sc > current_score:
                                        current_score = sc
                                        best_val = v
                                        improved = True
                                    trial_key[up] = old

                                trial_key[up] = best_val

                        # Evaluate final
                        final_pt = [0] * K4_LEN
                        for i in range(K4_LEN):
                            kp = i % PERIOD
                            final_pt[i] = dec_func(ct_idx[i], trial_key[kp])
                        final_score = score_indices(final_pt, i2c)

                        if final_score > best_score:
                            best_score = final_score
                            best_key = ''.join(i2c[k] for k in trial_key)
                            best_pt = ''.join(i2c[p] for p in final_pt)

                    print(f"    BEST score (hill-climb): {best_score:.1f}")
                    print(f"    BEST key:   {best_key}")
                    print(f"    BEST PT:    {best_pt[:50]}...")

                    record_result(best_score,
                                  f"S1:{alpha_name}:{op_name[:20]}",
                                  best_pt, best_key)
            else:
                print(f"    Too many unknowns ({len(unknown_positions)}), skipping brute-force.")


# =============================================================================
# SECTION 2: PROGRESSIVE KEY MODIFICATION
# =============================================================================

def section2_progressive_key():
    """Test progressive key modifications where the key changes each period."""
    print("\n" + "="*80)
    print("SECTION 2: PROGRESSIVE KEY MODIFICATION")
    print("="*80)

    alphabets = [
        ("STANDARD", STANDARD_ALPHA, STD_C2I, STD_I2C),
        ("KRYPTOS",  KRYPTOS_ALPHA,  KRY_C2I, KRY_I2C),
    ]

    # Use the known Vigenere key template as base
    for alpha_name, alpha, c2i, i2c in alphabets:
        ct_idx = [c2i[ch] for ch in K4_CT]

        # Parse the known key template for this alphabet
        base_key_str = VIGENERE_KEY_TEMPLATE
        base_key_idx = []
        for ch in base_key_str:
            if ch != '?':
                base_key_idx.append(c2i[ch])
            else:
                base_key_idx.append(-1)

        print(f"\n--- Alphabet: {alpha_name} ---")

        # For each progressive scheme, brute-force positions 16-20
        decrypt_modes = [
            ("Vigenere",  vigenere_decrypt_idx),
            ("Beaufort",  beaufort_decrypt_idx),
            ("VarBeaufort", variant_beaufort_decrypt_idx),
        ]

        for dec_name, dec_func in decrypt_modes:
            print(f"\n  Decrypt mode: {dec_name}")

            # Progressive scheme A: Key shifts by +1 each period cycle
            # key_effective[i] = (base_key[i%29] + floor(i/29)) mod 26
            for shift_amount in [1, 2, -1, -2, 3]:
                scheme_name = f"Shift+{shift_amount}/period"

                best_score = -float('inf')
                best_combo = None
                best_pt_str = None

                for combo in product(range(ALPHA_SIZE), repeat=5):
                    trial_key = list(base_key_idx)
                    for idx, up in enumerate(UNKNOWN_POS):
                        trial_key[up] = combo[idx]

                    # Decrypt with progressive shift
                    pt_chars = []
                    for i in range(K4_LEN):
                        kp = i % PERIOD
                        cycle = i // PERIOD
                        k = (trial_key[kp] + cycle * shift_amount) % ALPHA_SIZE
                        pt_chars.append(i2c[dec_func(ct_idx[i], k)])

                    pt_str = ''.join(pt_chars)
                    sc = score_text(pt_str)

                    if sc > best_score:
                        best_score = sc
                        best_combo = combo
                        best_pt_str = pt_str

                trial_key = list(base_key_idx)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = best_combo[idx]
                key_display = ''.join(i2c[k] for k in trial_key)

                print(f"    {scheme_name}: score={best_score:.1f} key={key_display} pt={best_pt_str[:40]}...")
                record_result(best_score, f"S2:{alpha_name}:{dec_name}:{scheme_name}", best_pt_str, key_display)

            # Progressive scheme B: Key shifts by position-dependent pattern
            # key_effective[i] = (base_key[i%29] + i) mod 26
            for pattern_name, pattern_func in [
                ("shift+i",         lambda i, kp, cycle: i),
                ("shift+i%29",      lambda i, kp, cycle: kp),
                ("shift+cycle*kp",  lambda i, kp, cycle: cycle * kp),
            ]:
                best_score = -float('inf')
                best_combo = None
                best_pt_str = None

                for combo in product(range(ALPHA_SIZE), repeat=5):
                    trial_key = list(base_key_idx)
                    for idx, up in enumerate(UNKNOWN_POS):
                        trial_key[up] = combo[idx]

                    pt_chars = []
                    for i in range(K4_LEN):
                        kp = i % PERIOD
                        cycle = i // PERIOD
                        shift = pattern_func(i, kp, cycle)
                        k = (trial_key[kp] + shift) % ALPHA_SIZE
                        pt_chars.append(i2c[dec_func(ct_idx[i], k)])

                    pt_str = ''.join(pt_chars)
                    sc = score_text(pt_str)

                    if sc > best_score:
                        best_score = sc
                        best_combo = combo
                        best_pt_str = pt_str

                trial_key = list(base_key_idx)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = best_combo[idx]
                key_display = ''.join(i2c[k] for k in trial_key)

                print(f"    {pattern_name}: score={best_score:.1f} key={key_display} pt={best_pt_str[:40]}...")
                record_result(best_score, f"S2:{alpha_name}:{dec_name}:{pattern_name}", best_pt_str, key_display)

            # Progressive scheme C: Autokey hybrid
            # After first period, key[i] = (base_key[i%29] + PT[i-29]) mod 26
            # This requires sequential decryption
            best_score = -float('inf')
            best_combo = None
            best_pt_str = None

            for combo in product(range(ALPHA_SIZE), repeat=5):
                trial_key = list(base_key_idx)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = combo[idx]

                pt_indices = [0] * K4_LEN
                for i in range(K4_LEN):
                    kp = i % PERIOD
                    if i < PERIOD:
                        k = trial_key[kp]
                    else:
                        k = (trial_key[kp] + pt_indices[i - PERIOD]) % ALPHA_SIZE
                    pt_indices[i] = dec_func(ct_idx[i], k)

                pt_str = ''.join(i2c[p] for p in pt_indices)
                sc = score_text(pt_str)

                if sc > best_score:
                    best_score = sc
                    best_combo = combo
                    best_pt_str = pt_str

            trial_key = list(base_key_idx)
            for idx, up in enumerate(UNKNOWN_POS):
                trial_key[up] = best_combo[idx]
            key_display = ''.join(i2c[k] for k in trial_key)

            print(f"    Autokey hybrid: score={best_score:.1f} key={key_display} pt={best_pt_str[:40]}...")
            record_result(best_score, f"S2:{alpha_name}:{dec_name}:AutokeyHybrid", best_pt_str, key_display)

            # Progressive scheme D: Cipher feedback
            # key_effective[i] = (base_key[i%29] + CT[i-1]) mod 26 for i>0
            best_score = -float('inf')
            best_combo = None
            best_pt_str = None

            for combo in product(range(ALPHA_SIZE), repeat=5):
                trial_key = list(base_key_idx)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = combo[idx]

                pt_chars = []
                for i in range(K4_LEN):
                    kp = i % PERIOD
                    if i == 0:
                        k = trial_key[kp]
                    else:
                        k = (trial_key[kp] + ct_idx[i-1]) % ALPHA_SIZE
                    pt_chars.append(i2c[dec_func(ct_idx[i], k)])

                pt_str = ''.join(pt_chars)
                sc = score_text(pt_str)

                if sc > best_score:
                    best_score = sc
                    best_combo = combo
                    best_pt_str = pt_str

            trial_key = list(base_key_idx)
            for idx, up in enumerate(UNKNOWN_POS):
                trial_key[up] = best_combo[idx]
            key_display = ''.join(i2c[k] for k in trial_key)

            print(f"    Cipher feedback: score={best_score:.1f} key={key_display} pt={best_pt_str[:40]}...")
            record_result(best_score, f"S2:{alpha_name}:{dec_name}:CipherFeedback", best_pt_str, key_display)


# =============================================================================
# SECTION 3: SPLIT BEAUFORT/VIGENERE
# =============================================================================

def section3_split_beaufort_vigenere():
    """Test combinations where some positions use Beaufort and others use Vigenere."""
    print("\n" + "="*80)
    print("SECTION 3: SPLIT BEAUFORT/VIGENERE")
    print("="*80)

    alphabets = [
        ("STANDARD", STANDARD_ALPHA, STD_C2I, STD_I2C),
        ("KRYPTOS",  KRYPTOS_ALPHA,  KRY_C2I, KRY_I2C),
    ]

    # Split patterns: each returns True for Beaufort, False for Vigenere at position i
    split_patterns = [
        ("Even=Beaufort, Odd=Vigenere",   lambda i, kp: i % 2 == 0),
        ("Odd=Beaufort, Even=Vigenere",    lambda i, kp: i % 2 == 1),
        ("First48=Beaufort, Rest=Vigenere", lambda i, kp: i < 48),
        ("First48=Vigenere, Rest=Beaufort", lambda i, kp: i >= 48),
        ("KeyPos0-15=Beaufort, 16-28=Vig", lambda i, kp: kp <= 15),
        ("KeyPos0-15=Vig, 16-28=Beaufort", lambda i, kp: kp > 15),
        ("KeyPos even=Beaufort, odd=Vig",  lambda i, kp: kp % 2 == 0),
        ("KeyPos odd=Beaufort, even=Vig",  lambda i, kp: kp % 2 == 1),
        ("First29=Vig, Rest=Beaufort",     lambda i, kp: i >= 29),
        ("First29=Beaufort, Rest=Vig",     lambda i, kp: i < 29),
    ]

    for alpha_name, alpha, c2i, i2c in alphabets:
        ct_idx = [c2i[ch] for ch in K4_CT]

        base_key_idx = []
        for ch in VIGENERE_KEY_TEMPLATE:
            if ch != '?':
                base_key_idx.append(c2i[ch])
            else:
                base_key_idx.append(-1)

        print(f"\n--- Alphabet: {alpha_name} ---")

        for pat_name, pat_func in split_patterns:
            best_score = -float('inf')
            best_combo = None
            best_pt_str = None

            for combo in product(range(ALPHA_SIZE), repeat=5):
                trial_key = list(base_key_idx)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = combo[idx]

                pt_chars = []
                for i in range(K4_LEN):
                    kp = i % PERIOD
                    k = trial_key[kp]
                    if pat_func(i, kp):
                        # Beaufort
                        pt_chars.append(i2c[beaufort_decrypt_idx(ct_idx[i], k)])
                    else:
                        # Vigenere
                        pt_chars.append(i2c[vigenere_decrypt_idx(ct_idx[i], k)])

                pt_str = ''.join(pt_chars)
                sc = score_text(pt_str)

                if sc > best_score:
                    best_score = sc
                    best_combo = combo
                    best_pt_str = pt_str

            trial_key = list(base_key_idx)
            for idx, up in enumerate(UNKNOWN_POS):
                trial_key[up] = best_combo[idx]
            key_display = ''.join(i2c[k] for k in trial_key)

            print(f"  {pat_name}: score={best_score:.1f} key={key_display}")
            print(f"    pt={best_pt_str[:50]}...")
            record_result(best_score, f"S3:{alpha_name}:{pat_name}", best_pt_str, key_display)

            if best_score > -500:
                print(f"    *** HIGH SCORE ***")
                print(f"    Full: {best_pt_str}")


# =============================================================================
# SECTION 4: KEYED BEAUFORT WITH DIFFERENT TABLEAU ALPHABETS
# =============================================================================

def section4_keyed_beaufort():
    """Test Beaufort with keyed alphabets as tableau."""
    print("\n" + "="*80)
    print("SECTION 4: KEYED BEAUFORT WITH DIFFERENT TABLEAU ALPHABETS")
    print("="*80)

    keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "HYDRA", "SHADOW"]

    for keyword in keywords:
        # Create keyed alphabet from keyword using STANDARD base
        keyed_alpha = make_keyed_alphabet(keyword, STANDARD_ALPHA)
        ka_c2i, ka_i2c = build_alpha_maps(keyed_alpha)

        # Also try keyed alphabet starting from KRYPTOS alphabet
        keyed_alpha_k = make_keyed_alphabet(keyword, KRYPTOS_ALPHA)
        ka_k_c2i, ka_k_i2c = build_alpha_maps(keyed_alpha_k)

        tableau_variants = [
            (f"Keyed({keyword})+StdBase", keyed_alpha, ka_c2i, ka_i2c),
            (f"Keyed({keyword})+KryBase", keyed_alpha_k, ka_k_c2i, ka_k_i2c),
        ]

        for tab_name, tab_alpha, tab_c2i, tab_i2c in tableau_variants:
            print(f"\n  Tableau: {tab_name} -> {tab_alpha}")

            # The CT and key are indexed in the tableau alphabet
            # Beaufort in keyed alphabet: PT_idx = (KEY_idx - CT_idx) mod 26
            # where indices are positions in the keyed alphabet
            ct_idx = [tab_c2i[ch] for ch in K4_CT]

            # Derive key from cribs using Beaufort relationship
            # Beaufort: CT = (KEY - PT) mod 26, so KEY = (CT + PT) mod 26
            key_from_cribs = [None] * PERIOD

            for crib_text, crib_pos in [CRIB_BERLIN, CRIB_ENE]:
                for j, ch in enumerate(crib_text):
                    pos = crib_pos + j
                    kp = pos % PERIOD
                    ct_val = ct_idx[pos]
                    pt_val = tab_c2i[ch]
                    # For Beaufort: KEY = (CT + PT) mod 26
                    key_val = (ct_val + pt_val) % ALPHA_SIZE

                    if key_from_cribs[kp] is not None and key_from_cribs[kp] != key_val:
                        pass  # Conflict - already derived differently
                    key_from_cribs[kp] = key_val

            unknown_positions = [i for i in range(PERIOD) if key_from_cribs[i] is None]
            key_str = ''.join(tab_i2c[k] if k is not None else '?' for k in key_from_cribs)
            print(f"    Beaufort-derived key: {key_str}")
            print(f"    Unknowns: {unknown_positions}")

            if len(unknown_positions) <= 5:
                # Brute force
                best_score = -float('inf')
                best_pt = None
                best_key_display = None

                for combo in product(range(ALPHA_SIZE), repeat=len(unknown_positions)):
                    trial_key = list(key_from_cribs)
                    for idx, up in enumerate(unknown_positions):
                        trial_key[up] = combo[idx]

                    pt_chars = []
                    for i in range(K4_LEN):
                        kp = i % PERIOD
                        # Beaufort decrypt: PT = (KEY - CT) mod 26
                        pt_idx = (trial_key[kp] - ct_idx[i]) % ALPHA_SIZE
                        pt_chars.append(tab_i2c[pt_idx])

                    pt_str = ''.join(pt_chars)
                    sc = score_text(pt_str)

                    if sc > best_score:
                        best_score = sc
                        best_pt = pt_str
                        best_key_display = ''.join(tab_i2c[k] for k in trial_key)

                print(f"    BEST: score={best_score:.1f} key={best_key_display}")
                print(f"    PT: {best_pt[:50]}...")
                record_result(best_score, f"S4:Beaufort:{tab_name}", best_pt, best_key_display)

                if best_score > -500:
                    print(f"    *** HIGH SCORE ***")
                    print(f"    Full: {best_pt}")

            # Also try Vigenere with this tableau
            key_from_cribs_vig = [None] * PERIOD
            for crib_text, crib_pos in [CRIB_BERLIN, CRIB_ENE]:
                for j, ch in enumerate(crib_text):
                    pos = crib_pos + j
                    kp = pos % PERIOD
                    ct_val = ct_idx[pos]
                    pt_val = tab_c2i[ch]
                    # Vigenere: KEY = (CT - PT) mod 26
                    key_val = (ct_val - pt_val) % ALPHA_SIZE
                    key_from_cribs_vig[kp] = key_val

            unknown_vig = [i for i in range(PERIOD) if key_from_cribs_vig[i] is None]

            if len(unknown_vig) <= 5:
                best_score = -float('inf')
                best_pt = None
                best_key_display = None

                for combo in product(range(ALPHA_SIZE), repeat=len(unknown_vig)):
                    trial_key = list(key_from_cribs_vig)
                    for idx, up in enumerate(unknown_vig):
                        trial_key[up] = combo[idx]

                    pt_chars = []
                    for i in range(K4_LEN):
                        kp = i % PERIOD
                        pt_idx = (ct_idx[i] - trial_key[kp]) % ALPHA_SIZE
                        pt_chars.append(tab_i2c[pt_idx])

                    pt_str = ''.join(pt_chars)
                    sc = score_text(pt_str)

                    if sc > best_score:
                        best_score = sc
                        best_pt = pt_str
                        best_key_display = ''.join(tab_i2c[k] for k in trial_key)

                print(f"    Vig BEST: score={best_score:.1f} key={best_key_display}")
                print(f"    PT: {best_pt[:50]}...")
                record_result(best_score, f"S4:Vigenere:{tab_name}", best_pt, best_key_display)


# =============================================================================
# SECTION 5: RECIPROCAL BEAUFORT PROPERTY
# =============================================================================

def section5_reciprocal_beaufort():
    """
    Beaufort is self-reciprocal: encrypt(encrypt(x)) = x.
    So Beaufort_encrypt(K4, key) should give plaintext.
    Test with all candidate keys from previous sections.
    Also test with known partial key directly.
    """
    print("\n" + "="*80)
    print("SECTION 5: RECIPROCAL BEAUFORT PROPERTY")
    print("="*80)

    alphabets = [
        ("STANDARD", STANDARD_ALPHA, STD_C2I, STD_I2C),
        ("KRYPTOS",  KRYPTOS_ALPHA,  KRY_C2I, KRY_I2C),
    ]

    for alpha_name, alpha, c2i, i2c in alphabets:
        ct_idx = [c2i[ch] for ch in K4_CT]

        print(f"\n--- Alphabet: {alpha_name} ---")
        print("  Testing Beaufort self-reciprocal property:")
        print("  Beaufort_encrypt(CT, KEY) should equal PT")
        print("  Since Beaufort encrypt = (KEY - input) mod 26,")
        print("  this is the same as Beaufort decrypt.")

        # Parse key template
        base_key_idx = []
        for ch in VIGENERE_KEY_TEMPLATE:
            if ch != '?':
                base_key_idx.append(c2i[ch])
            else:
                base_key_idx.append(-1)

        # Method 1: Use known Vigenere key with Beaufort encrypt (= Beaufort decrypt)
        # This tests: what if Sanborn used Beaufort to encrypt, and we have the key?
        # Beaufort encrypt: CT = (KEY - PT) mod 26
        # So PT = (KEY - CT) mod 26 = Beaufort decrypt

        best_score = -float('inf')
        best_combo = None
        best_pt = None

        print(f"\n  Beaufort encrypt(CT, key) = (KEY - CT) mod 26:")
        for combo in product(range(ALPHA_SIZE), repeat=5):
            trial_key = list(base_key_idx)
            for idx, up in enumerate(UNKNOWN_POS):
                trial_key[up] = combo[idx]

            pt_chars = []
            for i in range(K4_LEN):
                kp = i % PERIOD
                pt_idx = (trial_key[kp] - ct_idx[i]) % ALPHA_SIZE
                pt_chars.append(i2c[pt_idx])

            pt_str = ''.join(pt_chars)
            sc = score_text(pt_str)

            if sc > best_score:
                best_score = sc
                best_combo = combo
                best_pt = pt_str

        trial_key = list(base_key_idx)
        for idx, up in enumerate(UNKNOWN_POS):
            trial_key[up] = best_combo[idx]
        key_display = ''.join(i2c[k] for k in trial_key)

        print(f"    BEST: score={best_score:.1f} key={key_display}")
        print(f"    PT: {best_pt[:50]}...")
        record_result(best_score, f"S5:Reciprocal:{alpha_name}:Beaufort(CT,key)", best_pt, key_display)

        if best_score > -500:
            print(f"    *** HIGH SCORE ***")
            print(f"    Full: {best_pt}")

        # Method 2: Derive key from cribs using Beaufort relationship,
        # then use that key with Beaufort
        # Beaufort: CT = (KEY - PT) -> KEY = (CT + PT) mod 26
        key_beaufort = [None] * PERIOD
        for crib_text, crib_pos in [CRIB_BERLIN, CRIB_ENE]:
            for j, ch in enumerate(crib_text):
                pos = crib_pos + j
                kp = pos % PERIOD
                ct_val = ct_idx[pos]
                pt_val = c2i[ch]
                key_val = (ct_val + pt_val) % ALPHA_SIZE
                if key_beaufort[kp] is not None and key_beaufort[kp] != key_val:
                    print(f"    CONFLICT at kp={kp}: {i2c[key_beaufort[kp]]} vs {i2c[key_val]}")
                key_beaufort[kp] = key_val

        unknown_b = [i for i in range(PERIOD) if key_beaufort[i] is None]
        key_b_str = ''.join(i2c[k] if k is not None else '?' for k in key_beaufort)
        print(f"\n  Beaufort-derived key: {key_b_str}")
        print(f"  Unknowns: {unknown_b}")

        if len(unknown_b) <= 5:
            best_score = -float('inf')
            best_pt = None
            best_key_display = None

            for combo in product(range(ALPHA_SIZE), repeat=len(unknown_b)):
                trial_key = list(key_beaufort)
                for idx, up in enumerate(unknown_b):
                    trial_key[up] = combo[idx]

                pt_chars = []
                for i in range(K4_LEN):
                    kp = i % PERIOD
                    pt_idx = (trial_key[kp] - ct_idx[i]) % ALPHA_SIZE
                    pt_chars.append(i2c[pt_idx])

                pt_str = ''.join(pt_chars)
                sc = score_text(pt_str)

                if sc > best_score:
                    best_score = sc
                    best_pt = pt_str
                    best_key_display = ''.join(i2c[k] for k in trial_key)

            print(f"    BEST: score={best_score:.1f} key={best_key_display}")
            print(f"    PT: {best_pt[:50]}...")
            record_result(best_score, f"S5:Reciprocal:{alpha_name}:BeaufortDerivedKey", best_pt, best_key_display)

            if best_score > -500:
                print(f"    *** HIGH SCORE ***")
                print(f"    Full: {best_pt}")

        # Method 3: What if the key itself was Beaufort-encrypted?
        # i.e., true_key = Beaufort(vigenere_key, some_password)
        # Try small passwords
        print(f"\n  Testing Beaufort-encrypted key with short passwords...")
        test_passwords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SANBORN", "CIA", "NSA",
                          "BERLIN", "CLOCK", "SHADOW", "HYDRA", "KEY", "FOUR"]

        for password in test_passwords:
            # Transform the known key positions using Beaufort with the password
            pw_idx = [c2i[ch] for ch in password]
            pw_len = len(password)

            transformed_key = list(base_key_idx)
            for i in range(PERIOD):
                if transformed_key[i] >= 0:
                    pw_char = pw_idx[i % pw_len]
                    transformed_key[i] = (pw_char - transformed_key[i]) % ALPHA_SIZE

            # Now brute-force unknowns with transformed key
            best_score_pw = -float('inf')
            best_pt_pw = None
            best_combo_pw = None

            for combo in product(range(ALPHA_SIZE), repeat=5):
                trial_key = list(transformed_key)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = combo[idx]

                pt_chars = []
                for i in range(K4_LEN):
                    kp = i % PERIOD
                    # Try both Vigenere and Beaufort decrypt
                    pt_idx = (ct_idx[i] - trial_key[kp]) % ALPHA_SIZE
                    pt_chars.append(i2c[pt_idx])

                pt_str = ''.join(pt_chars)
                sc = score_text(pt_str)

                if sc > best_score_pw:
                    best_score_pw = sc
                    best_pt_pw = pt_str
                    best_combo_pw = combo

            if best_score_pw > -560:
                trial_key = list(transformed_key)
                for idx, up in enumerate(UNKNOWN_POS):
                    trial_key[up] = best_combo_pw[idx]
                key_disp = ''.join(i2c[k] for k in trial_key)
                print(f"    Password={password}: score={best_score_pw:.1f} key={key_disp}")
                print(f"      PT: {best_pt_pw[:50]}...")
                record_result(best_score_pw, f"S5:{alpha_name}:KeyTransform:Beaufort({password})",
                              best_pt_pw, key_disp)


# =============================================================================
# MAIN: RUN ALL SECTIONS AND REPORT
# =============================================================================

def print_final_report():
    """Print comprehensive final report."""
    print("\n" + "="*80)
    print("FINAL REPORT: ALL RESULTS SORTED BY SCORE")
    print("="*80)

    # Sort by score descending
    sorted_results = sorted(ALL_RESULTS, key=lambda x: x[0], reverse=True)

    # Print top 50
    print(f"\nTotal configurations tested: {len(sorted_results)}")

    above_450 = [r for r in sorted_results if r[0] > -450]
    above_500 = [r for r in sorted_results if r[0] > -500]
    above_550 = [r for r in sorted_results if r[0] > -550]

    print(f"Results above -450: {len(above_450)}")
    print(f"Results above -500: {len(above_500)}")
    print(f"Results above -550: {len(above_550)}")

    if above_450:
        print(f"\n{'='*80}")
        print("*** RESULTS ABOVE -450 (POTENTIAL SOLUTIONS) ***")
        print(f"{'='*80}")
        for score, desc, pt, key in above_450:
            print(f"\n  Score: {score:.1f}")
            print(f"  Method: {desc}")
            print(f"  Key: {key}")
            print(f"  Plaintext: {pt}")

    print(f"\n{'='*80}")
    print("TOP 50 RESULTS:")
    print(f"{'='*80}")
    for i, (score, desc, pt, key) in enumerate(sorted_results[:50]):
        print(f"\n  #{i+1}: Score={score:.1f}")
        print(f"       Method: {desc}")
        print(f"       Key: {key}")
        print(f"       PT: {pt[:60]}...")

    # Section summary
    print(f"\n{'='*80}")
    print("SECTION-BY-SECTION BEST SCORES:")
    print(f"{'='*80}")

    sections = {}
    for score, desc, pt, key in sorted_results:
        sec = desc.split(":")[0]
        if sec not in sections or score > sections[sec][0]:
            sections[sec] = (score, desc, pt, key)

    for sec in sorted(sections.keys()):
        score, desc, pt, key = sections[sec]
        print(f"  {sec}: {score:.1f} ({desc}) key={key}")
        print(f"       PT: {pt[:60]}...")


if __name__ == "__main__":
    start_time = time.time()

    print(f"K4 Ciphertext ({K4_LEN} chars): {K4_CT}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Period: {PERIOD}")
    print(f"Known key template: {VIGENERE_KEY_TEMPLATE}")
    print(f"Unknown positions: {UNKNOWN_POS}")

    section1_beaufort_key_derivation()
    section2_progressive_key()
    section3_split_beaufort_vigenere()
    section4_keyed_beaufort()
    section5_reciprocal_beaufort()

    print_final_report()

    elapsed = time.time() - start_time
    print(f"\nTotal elapsed time: {elapsed:.1f}s")
    print("DONE.")
