#!/usr/bin/env python3
"""
K4 Shift-7 Kappa Anomaly Investigation

Statistical analysis found a kappa spike at shift 7 (9 matches out of 90 possible,
kappa = 0.1000). This is 2.5x the random expectation (1/26 ~ 0.0385) and could
indicate a period-7 component in K4's encryption.

This script investigates:
1. Full kappa test for all shifts 1-96
2. Period-7 Vigenere via IC-based key recovery
3. Whether the known period-29 key has period-7 substructure
4. Period-7 transformation applied AFTER Vigenere-29 decryption
5. XOR/addition of period-7 key on Vigenere-29 output
6. Combined period 29+7: Vigenere-29 then Vigenere-7 with hill-climbing
7. Period-7 as transposition period (all 5040 column permutations)
8. Whether the kappa anomaly appears in raw ciphertext vs Vigenere output
"""

import math
import itertools
import random
from collections import Counter

# =============================================================================
# CONSTANTS
# =============================================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
N = len(K4)  # 97

# Known period-29 key: 24 of 29 positions known, positions 16-20 unknown
KNOWN_KEY_29 = "OYNKYELYOIECBAQK?????RDUMRIYW"
PERIOD_29 = 29

# =============================================================================
# LOAD QUADGRAMS
# =============================================================================
print("Loading quadgrams...")
QUADGRAMS = {}
QG_TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            QG_TOTAL += count

QG_LOG = {}
QG_FLOOR = math.log10(0.01 / QG_TOTAL)  # floor for unseen quadgrams
for gram, count in QUADGRAMS.items():
    QG_LOG[gram] = math.log10(count / QG_TOTAL)

def quadgram_score(text):
    """Score text using log-probability of English quadgrams."""
    text = text.upper()
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QG_LOG.get(qg, QG_FLOOR)
    return score

print(f"  Loaded {len(QUADGRAMS)} quadgrams (total count: {QG_TOTAL})")
print(f"  Floor value: {QG_FLOOR:.4f}")
print(f"  Sanity check - 'THE ': {QG_LOG.get('THER', 'NOT FOUND'):.4f}")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def k_idx(c):
    """Get index of character in KRYPTOS alphabet."""
    return KRYPTOS.index(c)

def k_chr(i):
    """Get character at index in KRYPTOS alphabet."""
    return KRYPTOS[i % 26]

def s_idx(c):
    """Get index of character in standard alphabet."""
    return ord(c) - ord('A')

def s_chr(i):
    """Get character at index in standard alphabet."""
    return chr(i % 26 + ord('A'))

def vig_decrypt_kryptos(ct, key):
    """Vigenere decrypt using KRYPTOS alphabet."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            result.append(KRYPTOS[(KRYPTOS.index(c) - KRYPTOS.index(k)) % 26])
    return ''.join(result)

def vig_encrypt_kryptos(pt, key):
    """Vigenere encrypt using KRYPTOS alphabet."""
    result = []
    for i, c in enumerate(pt):
        k = key[i % len(key)]
        result.append(KRYPTOS[(KRYPTOS.index(c) + KRYPTOS.index(k)) % 26])
    return ''.join(result)

def vig_decrypt_standard(ct, key):
    """Vigenere decrypt using standard alphabet."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            result.append(s_chr((s_idx(c) - s_idx(k)) % 26))
    return ''.join(result)

def vig_encrypt_standard(pt, key):
    """Vigenere encrypt using standard alphabet."""
    result = []
    for i, c in enumerate(pt):
        k = key[i % len(key)]
        result.append(s_chr((s_idx(c) + s_idx(k)) % 26))
    return ''.join(result)

def ic_of_text(text):
    """Compute index of coincidence for a text."""
    text = [c for c in text.upper() if c.isalpha()]
    n = len(text)
    if n < 2:
        return 0.0
    freq = Counter(text)
    total = sum(f * (f - 1) for f in freq.values())
    return total / (n * (n - 1))

def kappa_test(text, shift):
    """Count coincidences between text and itself shifted by 'shift' positions."""
    matches = 0
    comparisons = len(text) - shift
    for i in range(comparisons):
        if text[i] == text[i + shift]:
            matches += 1
    return matches, comparisons

# Partial decryption with known 24/29 key
def partial_decrypt_29():
    """Decrypt K4 with the known 24/29 key positions."""
    return vig_decrypt_kryptos(K4, KNOWN_KEY_29)

PARTIAL_PT = partial_decrypt_29()

# =============================================================================
# SECTION 1: FULL KAPPA TEST FOR ALL SHIFTS
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 1: KAPPA TEST FOR ALL SHIFTS 1-96")
print("=" * 80)

random_expected = 1.0 / 26  # ~0.0385
english_expected = 0.0667   # English IC

print(f"\nRandom expectation: {random_expected:.4f}")
print(f"English expectation: {english_expected:.4f}")
print(f"K4 length: {N}")

kappa_results = []
for shift in range(1, N):
    matches, comparisons = kappa_test(K4, shift)
    kappa = matches / comparisons if comparisons > 0 else 0
    kappa_results.append((shift, matches, comparisons, kappa))

# Sort by kappa value descending
kappa_sorted = sorted(kappa_results, key=lambda x: -x[3])

print(f"\nTop 20 shifts by kappa value:")
print(f"{'Shift':>6} {'Matches':>8} {'Compared':>9} {'Kappa':>8} {'Ratio':>7} {'Significance':>13}")
print("-" * 60)
for shift, matches, comp, kappa in kappa_sorted[:20]:
    ratio = kappa / random_expected
    # Simple significance: how many standard deviations above random?
    # Under null: each comparison is Bernoulli(1/26), so variance = p(1-p)/n
    p = random_expected
    std = math.sqrt(p * (1 - p) / comp) if comp > 0 else 1
    z = (kappa - p) / std if std > 0 else 0
    sig = f"{z:.1f}sigma"
    print(f"{shift:>6} {matches:>8} {comp:>9} {kappa:>8.4f} {ratio:>7.2f}x {sig:>13}")

# Highlight shift 7 specifically
shift7 = next(r for r in kappa_results if r[0] == 7)
print(f"\n*** SHIFT 7: {shift7[1]} matches / {shift7[2]} comparisons = kappa {shift7[3]:.4f} ***")
print(f"    Ratio to random: {shift7[3]/random_expected:.2f}x")

# Check if any multiples of 7 are also elevated
print(f"\nKappa at multiples of 7:")
for mult in range(7, N, 7):
    r = next(x for x in kappa_results if x[0] == mult)
    ratio = r[3] / random_expected
    flag = " <-- ELEVATED" if ratio > 1.5 else ""
    print(f"  Shift {mult:>3}: kappa={r[3]:.4f} ({ratio:.2f}x){flag}")

# Also check factors of 97 (prime - so only 1 and 97)
print(f"\n97 is prime, so no non-trivial factors to check.")

# Check multiples of 29 (the known period)
print(f"\nKappa at multiples of 29:")
for mult in range(29, N, 29):
    r = next(x for x in kappa_results if x[0] == mult)
    ratio = r[3] / random_expected
    flag = " <-- ELEVATED" if ratio > 1.5 else ""
    print(f"  Shift {mult:>3}: kappa={r[3]:.4f} ({ratio:.2f}x){flag}")

# Histogram-style display of all kappas
print(f"\nKappa distribution for all shifts:")
bins = [0] * 10
for _, _, _, kappa in kappa_results:
    bin_idx = min(int(kappa * 50), 9)
    bins[bin_idx] += 1
for i, count in enumerate(bins):
    lo = i * 0.02
    hi = (i + 1) * 0.02
    bar = "#" * count
    print(f"  {lo:.2f}-{hi:.2f}: {bar} ({count})")

# =============================================================================
# SECTION 2: PERIOD-7 VIGENERE - IC-BASED KEY RECOVERY
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 2: PERIOD-7 VIGENERE (IC-BASED KEY RECOVERY)")
print("=" * 80)

# Split K4 into 7 cosets (columns of period-7 matrix)
print(f"\nSplitting K4 into 7 cosets:")
for period in [7]:
    cosets = [[] for _ in range(period)]
    for i, c in enumerate(K4):
        cosets[i % period].append(c)

    print(f"\nPeriod {period}:")
    total_ic = 0
    for col in range(period):
        col_text = ''.join(cosets[col])
        col_ic = ic_of_text(col_text)
        total_ic += col_ic
        print(f"  Column {col} (n={len(col_text)}): IC={col_ic:.4f}  chars: {col_text}")

    avg_ic = total_ic / period
    print(f"\n  Average IC across {period} columns: {avg_ic:.4f}")
    print(f"  Random IC: {random_expected:.4f}")
    print(f"  English IC: ~0.0667")
    if avg_ic > 0.050:
        print(f"  --> Elevated! Consistent with period-{period} Vigenere")
    else:
        print(f"  --> Not significantly elevated above random")

# Now try IC-based key recovery for period 7
# For each column, try all 26 shifts and pick the one that gives most English-like frequencies
print(f"\nIC-based key recovery for period 7 (both alphabets):")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    print(f"\n  Using {alpha_name} alphabet:")
    best_key = []

    for col in range(7):
        col_chars = [K4[i] for i in range(col, N, 7)]
        best_shift = 0
        best_chi2 = float('inf')

        # English letter frequencies
        eng_freq = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
                    'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
                    'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.10, 'R': 6.0,
                    'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
                    'Y': 2.0, 'Z': 0.07}

        for shift in range(26):
            # Decrypt this column with this shift
            decrypted = []
            for c in col_chars:
                idx = alpha.index(c)
                decrypted.append(alpha[(idx - shift) % 26])

            # Chi-squared against English
            freq = Counter(decrypted)
            n_col = len(decrypted)
            chi2 = 0
            for letter in STANDARD:
                observed = freq.get(letter, 0)
                expected = eng_freq.get(letter, 0) * n_col / 100.0
                if expected > 0:
                    chi2 += (observed - expected) ** 2 / expected

            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift

        best_key.append(alpha[best_shift])

    key_str = ''.join(best_key)
    pt = ''
    for i, c in enumerate(K4):
        k = best_key[i % 7]
        idx = alpha.index(c)
        kidx = alpha.index(k)
        pt += alpha[(idx - kidx) % 26]

    qscore = quadgram_score(pt)
    print(f"    Recovered key: {key_str}")
    print(f"    Plaintext: {pt}")
    print(f"    Quadgram score: {qscore:.2f}")

# =============================================================================
# SECTION 3: DOES THE PERIOD-29 KEY HAVE PERIOD-7 SUBSTRUCTURE?
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 3: PERIOD-7 SUBSTRUCTURE IN THE PERIOD-29 KEY")
print("=" * 80)

print(f"\nKnown key (period 29): {KNOWN_KEY_29}")
print(f"29 and 7 are coprime: gcd(29,7) = {math.gcd(29, 7)}")
print(f"  (Since coprime, period-7 substructure would be purely coincidental)")

# Check if key values repeat with period 7
key_values = []
for c in KNOWN_KEY_29:
    if c == '?':
        key_values.append(None)
    else:
        key_values.append(KRYPTOS.index(c))

print(f"\nKey values (KRYPTOS indices):")
for i, v in enumerate(key_values):
    print(f"  Position {i:>2}: {KNOWN_KEY_29[i]} = {v}")

# Check if key[i] == key[i+7] for any known pairs
print(f"\nChecking key[i] vs key[i+7] for known positions:")
period7_matches = 0
period7_checks = 0
for i in range(22):  # 29-7=22
    v1 = key_values[i]
    v2 = key_values[i + 7]
    if v1 is not None and v2 is not None:
        period7_checks += 1
        match = "MATCH" if v1 == v2 else ""
        diff = (v2 - v1) % 26
        if v1 == v2:
            period7_matches += 1
        print(f"  key[{i:>2}]={KNOWN_KEY_29[i]}({v1:>2}) vs key[{i+7:>2}]={KNOWN_KEY_29[i+7]}({v2:>2})  diff={diff:>2}  {match}")

print(f"\n  Period-7 matches: {period7_matches}/{period7_checks}")
if period7_checks > 0:
    print(f"  Expected by random: {period7_checks/26:.1f}")

# Check if the DIFFERENCES between key[i] and key[i+7] are constant (affine relationship)
print(f"\nDifferences key[i+7]-key[i] mod 26 (looking for constant = affine relationship):")
diffs_7 = []
for i in range(22):
    v1 = key_values[i]
    v2 = key_values[i + 7]
    if v1 is not None and v2 is not None:
        diff = (v2 - v1) % 26
        diffs_7.append(diff)

diff_counter = Counter(diffs_7)
print(f"  Differences: {diffs_7}")
print(f"  Most common: {diff_counter.most_common(5)}")
if diff_counter:
    top_diff, top_count = diff_counter.most_common(1)[0]
    print(f"  Top difference {top_diff} appears {top_count}/{len(diffs_7)} times")
    print(f"  Expected by random: {len(diffs_7)/26:.1f}")

# =============================================================================
# SECTION 4: PERIOD-7 TRANSFORMATION AFTER VIGENERE-29 DECRYPTION
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 4: PERIOD-7 TRANSFORMATION ON VIGENERE-29 OUTPUT")
print("=" * 80)

print(f"\nPartial decryption (24/29 key): {PARTIAL_PT}")
known_positions = [i for i in range(N) if KNOWN_KEY_29[i % PERIOD_29] != '?']
unknown_positions = [i for i in range(N) if KNOWN_KEY_29[i % PERIOD_29] == '?']
print(f"Known positions: {len(known_positions)}/{N}")
print(f"Unknown positions: {unknown_positions}")

# Extract only the known portions for analysis
known_text = ''.join(PARTIAL_PT[i] if i in known_positions else '' for i in range(N))
print(f"\nKnown decrypted text (gaps removed): {known_text}")
print(f"Known decrypted text length: {len(known_text)}")

# Kappa test on the partial decryption (known positions only)
print(f"\nKappa test on known decrypted positions:")
for shift in [1, 2, 3, 5, 7, 14, 29]:
    matches = 0
    comp = 0
    for i in range(N - shift):
        if i in known_positions and (i + shift) in known_positions:
            comp += 1
            if PARTIAL_PT[i] == PARTIAL_PT[i + shift]:
                matches += 1
    if comp > 0:
        kappa = matches / comp
        ratio = kappa / random_expected
        print(f"  Shift {shift:>3}: {matches}/{comp} = {kappa:.4f} ({ratio:.2f}x random)")

# Try IC-based period-7 key recovery on the PARTIAL decryption
print(f"\nIC-based period-7 key recovery on partial Vigenere-29 output:")
for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    print(f"\n  Using {alpha_name} alphabet on known positions:")
    best_key7 = []

    for col in range(7):
        # Get characters at positions where key is known AND position mod 7 == col
        col_chars = [PARTIAL_PT[i] for i in range(col, N, 7)
                     if KNOWN_KEY_29[i % PERIOD_29] != '?']

        if not col_chars:
            best_key7.append('A')
            continue

        eng_freq = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
                    'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
                    'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.10, 'R': 6.0,
                    'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
                    'Y': 2.0, 'Z': 0.07}

        best_shift = 0
        best_chi2 = float('inf')

        for shift in range(26):
            decrypted = [alpha[(alpha.index(c) - shift) % 26] for c in col_chars]
            freq = Counter(decrypted)
            n_col = len(decrypted)
            chi2 = 0
            for letter in STANDARD:
                observed = freq.get(letter, 0)
                expected = eng_freq.get(letter, 0) * n_col / 100.0
                if expected > 0:
                    chi2 += (observed - expected) ** 2 / expected
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift

        best_key7.append(alpha[best_shift])

    key7_str = ''.join(best_key7)
    # Apply this key to the known portions of partial plaintext
    pt7 = []
    for i in range(N):
        if KNOWN_KEY_29[i % PERIOD_29] == '?':
            pt7.append('?')
        else:
            c = PARTIAL_PT[i]
            k = best_key7[i % 7]
            pt7.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])
    pt7_str = ''.join(pt7)

    # Score only known parts
    known_pt7 = ''.join(c for c in pt7_str if c != '?')
    qscore = quadgram_score(known_pt7)
    print(f"    Recovered period-7 key: {key7_str}")
    print(f"    Double-decrypted text: {pt7_str}")
    print(f"    Quadgram score (known): {qscore:.2f}")

# =============================================================================
# SECTION 5: XOR/ADDITION WITH PERIOD-7 KEY ON VIGENERE-29 OUTPUT
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 5: MODULAR ADDITION/SUBTRACTION WITH PERIOD-7 KEY")
print("=" * 80)

# This is essentially the same as Section 4's Vigenere approach
# But let's also try: what if the period-7 key is applied using standard alphabet
# while the period-29 key uses KRYPTOS alphabet?

print(f"\nTesting mixed-alphabet scenarios:")
print(f"  Layer 1: Vigenere-29 with KRYPTOS alphabet (known)")
print(f"  Layer 2: Vigenere-7 with [KRYPTOS or STANDARD] alphabet")

# For the known decrypted text, try period-7 subtraction with all possible keys
# Optimize each position independently using chi-squared

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    print(f"\n  Layer 2 using {alpha_name} alphabet:")

    best_key7 = []
    for col in range(7):
        col_chars = [PARTIAL_PT[i] for i in range(col, N, 7)
                     if KNOWN_KEY_29[i % PERIOD_29] != '?']

        if not col_chars:
            best_key7.append('A')
            continue

        eng_freq = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
                    'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
                    'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.10, 'R': 6.0,
                    'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
                    'Y': 2.0, 'Z': 0.07}

        best_shift = 0
        best_chi2 = float('inf')

        for shift in range(26):
            decrypted = [alpha[(alpha.index(c) - shift) % 26] for c in col_chars]
            freq = Counter(decrypted)
            n_col = len(decrypted)
            chi2 = 0
            for letter in STANDARD:
                observed = freq.get(letter, 0)
                expected = eng_freq.get(letter, 0) * n_col / 100.0
                if expected > 0:
                    chi2 += (observed - expected) ** 2 / expected
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift

        best_key7.append(alpha[best_shift])

    key7_str = ''.join(best_key7)

    # Also try ADDITION instead of subtraction
    best_key7_add = []
    for col in range(7):
        col_chars = [PARTIAL_PT[i] for i in range(col, N, 7)
                     if KNOWN_KEY_29[i % PERIOD_29] != '?']

        if not col_chars:
            best_key7_add.append('A')
            continue

        best_shift = 0
        best_chi2 = float('inf')

        for shift in range(26):
            decrypted = [alpha[(alpha.index(c) + shift) % 26] for c in col_chars]
            freq = Counter(decrypted)
            n_col = len(decrypted)
            chi2 = 0
            for letter in STANDARD:
                observed = freq.get(letter, 0)
                expected = eng_freq.get(letter, 0) * n_col / 100.0
                if expected > 0:
                    chi2 += (observed - expected) ** 2 / expected
            if chi2 < best_chi2:
                best_chi2 = chi2
                best_shift = shift

        best_key7_add.append(alpha[best_shift])

    key7_add_str = ''.join(best_key7_add)

    print(f"    Subtraction key: {key7_str}")
    print(f"    Addition key:    {key7_add_str}")

    # Apply subtraction key
    pt_sub = []
    for i in range(N):
        if KNOWN_KEY_29[i % PERIOD_29] == '?':
            pt_sub.append('?')
        else:
            c = PARTIAL_PT[i]
            k = best_key7[i % 7]
            pt_sub.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])
    known_sub = ''.join(c for c in pt_sub if c != '?')

    # Apply addition key
    pt_add = []
    for i in range(N):
        if KNOWN_KEY_29[i % PERIOD_29] == '?':
            pt_add.append('?')
        else:
            c = PARTIAL_PT[i]
            k = best_key7_add[i % 7]
            pt_add.append(alpha[(alpha.index(c) + alpha.index(k)) % 26])
    known_add = ''.join(c for c in pt_add if c != '?')

    print(f"    Subtract result: {''.join(pt_sub)}")
    print(f"      Score: {quadgram_score(known_sub):.2f}")
    print(f"    Addition result: {''.join(pt_add)}")
    print(f"      Score: {quadgram_score(known_add):.2f}")

# =============================================================================
# SECTION 6: COMBINED PERIOD 29+7 WITH HILL-CLIMBING
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 6: COMBINED VIGENERE-29 + VIGENERE-7 (HILL-CLIMBING)")
print("=" * 80)

print(f"\nStrategy: Fix the known 24/29 key positions for layer 1,")
print(f"then hill-climb over the 7-position second layer key.")
print(f"Also hill-climb over the 5 unknown positions in layer 1.")
print(f"Total unknowns: 5 (layer 1) + 7 (layer 2) = 12 positions")

def combined_decrypt(ct, key29, key7, alpha=KRYPTOS):
    """Apply Vigenere-29 then Vigenere-7 decryption."""
    # Layer 1: Vigenere-29
    intermediate = []
    for i, c in enumerate(ct):
        k = key29[i % len(key29)]
        intermediate.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])

    # Layer 2: Vigenere-7
    result = []
    for i, c in enumerate(intermediate):
        k = key7[i % len(key7)]
        result.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])

    return ''.join(result)

def hill_climb_combined(ct, known_key29, alpha=KRYPTOS, iterations=50000):
    """Hill-climb to find the best 7-position key and fill 5 unknown positions."""
    # Initialize
    key29 = list(known_key29)
    unknown_pos_29 = [i for i, c in enumerate(key29) if c == '?']

    # Random initialization for unknown positions
    for pos in unknown_pos_29:
        key29[pos] = alpha[random.randint(0, 25)]

    # Random initialization for key7
    key7 = [alpha[random.randint(0, 25)] for _ in range(7)]

    # Current score
    pt = combined_decrypt(ct, key29, key7, alpha)
    best_score = quadgram_score(pt)
    best_key29 = list(key29)
    best_key7 = list(key7)
    best_pt = pt

    no_improve = 0

    for iteration in range(iterations):
        # Randomly choose: modify key29 unknown or key7
        if random.random() < 0.3 and unknown_pos_29:
            # Modify a random unknown position in key29
            pos = random.choice(unknown_pos_29)
            old_val = key29[pos]
            key29[pos] = alpha[random.randint(0, 25)]
        else:
            # Modify a random position in key7
            pos7 = random.randint(0, 6)
            old_val = key7[pos7]
            key7[pos7] = alpha[random.randint(0, 25)]
            pos = -1  # flag for key7

        pt = combined_decrypt(ct, key29, key7, alpha)
        score = quadgram_score(pt)

        if score > best_score:
            best_score = score
            best_key29 = list(key29)
            best_key7 = list(key7)
            best_pt = pt
            no_improve = 0
        else:
            # Revert
            if pos >= 0:
                key29[pos] = old_val
            else:
                key7[pos7] = old_val
            no_improve += 1

        # Restart if stuck
        if no_improve > 2000:
            for p in unknown_pos_29:
                key29[p] = alpha[random.randint(0, 25)]
            key7 = [alpha[random.randint(0, 25)] for _ in range(7)]
            pt = combined_decrypt(ct, key29, key7, alpha)
            current_score = quadgram_score(pt)
            no_improve = 0

    return best_key29, best_key7, best_score, best_pt

# Run hill-climbing multiple times with different random seeds
print(f"\nRunning hill-climbing (5 restarts x 50000 iterations each)...")

overall_best_score = -float('inf')
overall_best = None

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    print(f"\n  Alphabet: {alpha_name}")

    for trial in range(5):
        random.seed(42 + trial * 1000)
        key29, key7, score, pt = hill_climb_combined(K4, KNOWN_KEY_29, alpha, iterations=50000)

        k29_str = ''.join(key29)
        k7_str = ''.join(key7)

        if score > overall_best_score:
            overall_best_score = score
            overall_best = (alpha_name, k29_str, k7_str, score, pt)

        if trial == 0 or score > -350:
            print(f"    Trial {trial}: key29={''.join(key29)} key7={k7_str} score={score:.2f}")
            print(f"              pt={pt[:60]}...")

if overall_best:
    print(f"\n  BEST OVERALL:")
    print(f"    Alphabet: {overall_best[0]}")
    print(f"    Key-29: {overall_best[1]}")
    print(f"    Key-7:  {overall_best[2]}")
    print(f"    Score:  {overall_best[3]:.2f}")
    print(f"    Text:   {overall_best[4]}")

# Also try Vigenere-7 FIRST, then Vigenere-29
print(f"\n  Also testing reverse order: Vigenere-7 first, then Vigenere-29...")

def combined_decrypt_reversed(ct, key7, key29, alpha=KRYPTOS):
    """Apply Vigenere-7 then Vigenere-29 decryption (reversed order)."""
    intermediate = []
    for i, c in enumerate(ct):
        k = key7[i % len(key7)]
        intermediate.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])

    result = []
    for i, c in enumerate(intermediate):
        k = key29[i % len(key29)]
        if k == '?':
            result.append('?')
        else:
            result.append(alpha[(alpha.index(c) - alpha.index(k)) % 26])

    return ''.join(result)

def hill_climb_reversed(ct, known_key29, alpha=KRYPTOS, iterations=50000):
    """Hill-climb: Vigenere-7 first, then Vigenere-29."""
    key29 = list(known_key29)
    unknown_pos_29 = [i for i, c in enumerate(key29) if c == '?']

    for pos in unknown_pos_29:
        key29[pos] = alpha[random.randint(0, 25)]

    key7 = [alpha[random.randint(0, 25)] for _ in range(7)]

    pt = combined_decrypt_reversed(ct, key7, key29, alpha)
    pt_known = pt.replace('?', '')
    best_score = quadgram_score(pt_known) if len(pt_known) > 3 else -9999
    best_key29 = list(key29)
    best_key7 = list(key7)
    best_pt = pt

    no_improve = 0

    for iteration in range(iterations):
        if random.random() < 0.3 and unknown_pos_29:
            pos = random.choice(unknown_pos_29)
            old_val = key29[pos]
            key29[pos] = alpha[random.randint(0, 25)]
        else:
            pos7 = random.randint(0, 6)
            old_val = key7[pos7]
            key7[pos7] = alpha[random.randint(0, 25)]
            pos = -1

        pt = combined_decrypt_reversed(ct, key7, key29, alpha)
        pt_known = pt.replace('?', '')
        score = quadgram_score(pt_known) if len(pt_known) > 3 else -9999

        if score > best_score:
            best_score = score
            best_key29 = list(key29)
            best_key7 = list(key7)
            best_pt = pt
            no_improve = 0
        else:
            if pos >= 0:
                key29[pos] = old_val
            else:
                key7[pos7] = old_val
            no_improve += 1

        if no_improve > 2000:
            for p in unknown_pos_29:
                key29[p] = alpha[random.randint(0, 25)]
            key7 = [alpha[random.randint(0, 25)] for _ in range(7)]
            no_improve = 0

    return best_key29, best_key7, best_score, best_pt

for alpha_name, alpha in [("KRYPTOS", KRYPTOS)]:
    print(f"\n  Reversed order with {alpha_name} alphabet:")
    for trial in range(3):
        random.seed(7777 + trial * 500)
        key29, key7, score, pt = hill_climb_reversed(K4, KNOWN_KEY_29, alpha, iterations=50000)
        k7_str = ''.join(key7)
        print(f"    Trial {trial}: key7={k7_str} score={score:.2f}")
        print(f"              pt={pt[:60]}...")

# =============================================================================
# SECTION 7: PERIOD-7 AS TRANSPOSITION (ALL 5040 PERMUTATIONS)
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 7: PERIOD-7 TRANSPOSITION (ALL 5040 COLUMN PERMUTATIONS)")
print("=" * 80)

print(f"\n97 characters in 7 columns: 13 full rows + 6 remainder characters")
print(f"  (13 * 7 = 91, remainder = 6)")
print(f"  Columns 0-5 have 14 chars, column 6 has 13 chars")

# Apply transposition on the Vigenere-29 partial output
# First, try on the RAW ciphertext
def apply_columnar_transposition(text, ncols, perm):
    """Read text into rows of ncols, then read out in column order given by perm.
    This UNDOES a columnar transposition that was applied with column order 'perm'.
    """
    nrows = len(text) // ncols
    extra = len(text) % ncols

    # Build the grid - columns in perm[:extra] have nrows+1 chars, rest have nrows
    # We need to figure out how the ciphertext fills the grid based on the permutation

    # The encryption process writes plaintext in rows, reads in column order perm
    # So to decrypt: the ciphertext was read column-by-column in perm order
    # We need to figure out how many chars each column got

    col_lengths = []
    for col in range(ncols):
        if col < extra:
            col_lengths.append(nrows + 1)
        else:
            col_lengths.append(nrows)

    # The ciphertext is columns read in perm order
    # Split ciphertext into columns according to perm ordering
    columns = {}
    pos = 0
    for p in perm:
        clen = col_lengths[p]
        columns[p] = text[pos:pos + clen]
        pos += clen

    # Now read off rows
    result = []
    for row in range(nrows + 1):
        for col in range(ncols):
            if row < len(columns.get(col, '')):
                result.append(columns[col][row])

    return ''.join(result)

def apply_columnar_transposition_inv(text, ncols, perm):
    """Inverse: the plaintext was written into columns in perm order, read off in rows."""
    nrows = len(text) // ncols
    extra = len(text) % ncols

    col_lengths = []
    for col in range(ncols):
        if col < extra:
            col_lengths.append(nrows + 1)
        else:
            col_lengths.append(nrows)

    # Write text into rows
    grid = []
    pos = 0
    for row in range(nrows + (1 if extra > 0 else 0)):
        row_data = []
        for col in range(ncols):
            if pos < len(text) and row < col_lengths[col]:
                row_data.append(text[pos])
                pos += 1
        grid.append(row_data)

    # Read out columns in perm order
    result = []
    for p in perm:
        for row in range(len(grid)):
            if p < len(grid[row]):
                result.append(grid[row][p])

    return ''.join(result)

# Test all 5040 permutations on K4 raw ciphertext
print(f"\nTesting all 5040 column permutations on RAW K4 ciphertext:")

best_transpositions_raw = []
all_perms = list(itertools.permutations(range(7)))

for perm in all_perms:
    # Try both transposition directions
    pt1 = apply_columnar_transposition(K4, 7, perm)
    pt2 = apply_columnar_transposition_inv(K4, 7, perm)

    s1 = quadgram_score(pt1)
    s2 = quadgram_score(pt2)

    best_transpositions_raw.append((perm, s1, pt1, 'decrypt'))
    best_transpositions_raw.append((perm, s2, pt2, 'inverse'))

best_transpositions_raw.sort(key=lambda x: -x[1])

print(f"\n  Top 10 transpositions on raw K4:")
for perm, score, pt, direction in best_transpositions_raw[:10]:
    print(f"    Perm {perm} ({direction}): score={score:.2f}")
    print(f"      {pt[:70]}...")

# Now test on the Vigenere-29 partial output (using only known positions is tricky,
# so let's fill unknowns with best-guess and transpose the full thing)
print(f"\nTesting transpositions on Vigenere-29 output (filling unknowns with freq-based guess):")

# Fill unknown positions with frequency-based best guess
filled_pt = list(PARTIAL_PT)
for pos in unknown_positions:
    # Use the most common English letter 'E' as placeholder
    filled_pt[pos] = 'E'
filled_pt_str = ''.join(filled_pt)

best_transpositions_vig = []
for perm in all_perms:
    pt1 = apply_columnar_transposition(filled_pt_str, 7, perm)
    pt2 = apply_columnar_transposition_inv(filled_pt_str, 7, perm)

    s1 = quadgram_score(pt1)
    s2 = quadgram_score(pt2)

    best_transpositions_vig.append((perm, s1, pt1, 'decrypt'))
    best_transpositions_vig.append((perm, s2, pt2, 'inverse'))

best_transpositions_vig.sort(key=lambda x: -x[1])

print(f"\n  Top 10 transpositions on Vigenere-29 output:")
for perm, score, pt, direction in best_transpositions_vig[:10]:
    print(f"    Perm {perm} ({direction}): score={score:.2f}")
    print(f"      {pt[:70]}...")

# Compare: does transposition help?
identity_score_raw = quadgram_score(K4)
identity_score_vig = quadgram_score(filled_pt_str)
print(f"\n  Identity (no transposition) scores:")
print(f"    Raw K4: {identity_score_raw:.2f}")
print(f"    Vigenere-29 output: {identity_score_vig:.2f}")
print(f"    Best transposition on raw: {best_transpositions_raw[0][1]:.2f}")
print(f"    Best transposition on Vig-29: {best_transpositions_vig[0][1]:.2f}")

# =============================================================================
# SECTION 8: KAPPA ON RAW CIPHERTEXT VS VIGENERE OUTPUT
# =============================================================================
print("\n" + "=" * 80)
print("SECTION 8: KAPPA ON RAW CIPHERTEXT VS VIGENERE-29 OUTPUT")
print("=" * 80)

print(f"\nComparing shift-7 kappa on different texts:")

# Raw K4
m_raw, c_raw = kappa_test(K4, 7)
k_raw = m_raw / c_raw

# Partial decryption (treat unknowns as special char that never matches)
m_partial = 0
c_partial = 0
for i in range(N - 7):
    if (KNOWN_KEY_29[i % PERIOD_29] != '?' and
        KNOWN_KEY_29[(i+7) % PERIOD_29] != '?'):
        c_partial += 1
        if PARTIAL_PT[i] == PARTIAL_PT[i + 7]:
            m_partial += 1

k_partial = m_partial / c_partial if c_partial > 0 else 0

print(f"\n  Raw K4:           shift-7 kappa = {m_raw}/{c_raw} = {k_raw:.4f} ({k_raw/random_expected:.2f}x)")
print(f"  Vigenere-29 out:  shift-7 kappa = {m_partial}/{c_partial} = {k_partial:.4f} ({k_partial/random_expected:.2f}x)")

# Full kappa profile for the Vigenere-29 output
print(f"\nFull kappa profile for Vigenere-29 output (known positions only):")
vig_kappa_results = []
for shift in range(1, N):
    matches = 0
    comp = 0
    for i in range(N - shift):
        if (KNOWN_KEY_29[i % PERIOD_29] != '?' and
            KNOWN_KEY_29[(i+shift) % PERIOD_29] != '?'):
            comp += 1
            if PARTIAL_PT[i] == PARTIAL_PT[i + shift]:
                matches += 1
    if comp > 0:
        kappa = matches / comp
    else:
        kappa = 0
    vig_kappa_results.append((shift, matches, comp, kappa))

# Sort and show top
vig_kappa_sorted = sorted(vig_kappa_results, key=lambda x: -x[3])

print(f"\n  Top 15 shifts by kappa (Vigenere-29 output):")
print(f"  {'Shift':>6} {'Matches':>8} {'Compared':>9} {'Kappa':>8} {'Ratio':>7}")
print(f"  " + "-" * 50)
for shift, matches, comp, kappa in vig_kappa_sorted[:15]:
    ratio = kappa / random_expected
    print(f"  {shift:>6} {matches:>8} {comp:>9} {kappa:>8.4f} {ratio:>7.2f}x")

# Specifically compare shift-7 in both
print(f"\nShift-7 comparison:")
raw_7 = next(r for r in kappa_results if r[0] == 7)
vig_7 = next(r for r in vig_kappa_results if r[0] == 7)
print(f"  Raw K4:      {raw_7[1]}/{raw_7[2]} = {raw_7[3]:.4f}")
print(f"  Vig-29 out:  {vig_7[1]}/{vig_7[2]} = {vig_7[3]:.4f}")

if vig_7[3] > raw_7[3]:
    print(f"  --> Kappa INCREASES after Vigenere-29 decryption (anomaly is in the plaintext)")
elif vig_7[3] < raw_7[3] * 0.5:
    print(f"  --> Kappa DECREASES after Vigenere-29 decryption (anomaly is in the ciphertext structure)")
else:
    print(f"  --> Kappa is similar before and after (anomaly source unclear)")

# Does the Vigenere-29 key itself have period-7 structure that would cause this?
print(f"\nDoes the Vigenere-29 decryption PRESERVE or CREATE the period-7 kappa?")
print(f"  If C(i)=C(i+7), does P(i)=P(i+7) depend on K(i%29)==K((i+7)%29)?")
print(f"  Since 7 mod 29 = 7, P(i)=P(i+7) iff C(i)=C(i+7) AND key[i%29]=key[(i+7)%29]")
print(f"  OR C(i)!=C(i+7) but the key difference compensates exactly")

# Check: for each shift-7 match in K4, does key[i%29] == key[(i+7)%29]?
print(f"\n  Analyzing shift-7 matches in raw K4:")
for i in range(N - 7):
    if K4[i] == K4[i + 7]:
        kp1 = i % PERIOD_29
        kp2 = (i + 7) % PERIOD_29
        k1 = KNOWN_KEY_29[kp1]
        k2 = KNOWN_KEY_29[kp2]
        key_match = "YES" if k1 == k2 else ("?" if k1 == '?' or k2 == '?' else "NO")
        pt_match = ""
        if k1 != '?' and k2 != '?':
            p1 = PARTIAL_PT[i]
            p2 = PARTIAL_PT[i + 7]
            pt_match = f"  P[{i}]={p1}, P[{i+7}]={p2}, {'MATCH' if p1==p2 else 'DIFF'}"
        print(f"    i={i:>2}: C[{i}]=C[{i+7}]={K4[i]}, key[{kp1}]={k1} vs key[{kp2}]={k2} -> key_match={key_match}{pt_match}")

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("SUMMARY OF FINDINGS")
print("=" * 80)

print(f"""
1. KAPPA TEST (Section 1):
   - Shift 7: {raw_7[1]} matches / {raw_7[2]} comparisons = kappa {raw_7[3]:.4f} ({raw_7[3]/random_expected:.2f}x random)
   - Rank among all shifts: #{next(i+1 for i, (s,_,_,_) in enumerate(kappa_sorted) if s == 7)}
   - Top shift: {kappa_sorted[0][0]} with kappa {kappa_sorted[0][3]:.4f}

2. PERIOD-7 VIGENERE (Section 2):
   - Average IC across 7 columns: indicates whether period-7 Vigenere is plausible
   - IC-based key recovery attempted with both alphabets

3. PERIOD-29 KEY SUBSTRUCTURE (Section 3):
   - Period-7 matches in key: {period7_matches}/{period7_checks}
   - 29 and 7 are coprime, so no inherent mathematical relationship

4. POST-VIGENERE PERIOD-7 (Sections 4-5):
   - Applied period-7 Vigenere on the Vigenere-29 output
   - Tested both subtraction and addition modes
   - Tested both KRYPTOS and standard alphabets

5. HILL-CLIMBING COMBINED (Section 6):
   - Best combined score: {f'{overall_best[3]:.2f}' if overall_best else 'N/A'}
   - Tests whether two-layer encryption is viable

6. TRANSPOSITION (Section 7):
   - Best transposition on raw K4: {best_transpositions_raw[0][1]:.2f}
   - Best transposition on Vig-29: {best_transpositions_vig[0][1]:.2f}
   - Compare to identity (no transposition): raw={identity_score_raw:.2f}, vig={identity_score_vig:.2f}

7. RAW VS DECRYPTED KAPPA (Section 8):
   - Raw K4 shift-7 kappa: {raw_7[3]:.4f}
   - Vig-29 output shift-7 kappa: {vig_7[3]:.4f}
   - The kappa anomaly {'persists' if vig_7[3] > random_expected * 1.5 else 'disappears'} after Vigenere-29 decryption
""")

print("=" * 80)
print("INVESTIGATION COMPLETE")
print("=" * 80)
