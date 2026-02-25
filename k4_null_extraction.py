#!/usr/bin/env python3
"""
K4 Null Extraction Hypothesis Tester
=====================================
Tests whether the Vigenere output of K4 contains NULL characters mixed with
real plaintext. If we can identify and remove the nulls, readable English
should emerge.

Hypothesis basis:
- Ed Scheidt: "I masked the English language so it's more of a challenge"
- Ed Scheidt: "frequency analysis won't help"
- IC of Vigenere output at known-key positions is 0.043 (between English 0.067 and random 0.038)
  This is consistent with English diluted by random nulls.
"""

import math
import itertools
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
BEST_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"  # period 29
KEY_PERIOD = 29

# Known K4 themed words to search for
SEARCH_WORDS = [
    "THE", "AND", "FOR", "THAT", "THIS", "WITH", "FROM", "HAVE", "BEEN",
    "BERLIN", "CLOCK", "EAST", "NORTH", "SOUTH", "WEST",
    "SLOWLY", "DESPERATELY", "SHADOW", "UNDERGROUND",
    "BURIED", "SECRET", "HIDDEN", "LAYER", "PALIMPSEST",
    "ABSCISSA", "IQLUSION", "BETWEEN", "SUBTLE", "SHADING",
    "LANGLEY", "VIRTUALLY", "INVISIBLE", "DEGREE", "MINUTES",
    "SECONDS", "LATITUDE", "LONGITUDE", "NORTHEAST",
    "OBSCURE", "INFORMATION", "GATHERED",
]

# ============================================================
# LOAD QUADGRAMS
# ============================================================

print("Loading quadgrams...")
QUADGRAMS = {}
QUADGRAM_TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            QUADGRAM_TOTAL += count

QUADGRAM_LOG = {}
LOG_FLOOR = math.log10(0.01 / QUADGRAM_TOTAL)  # floor for unknown quadgrams
for gram, count in QUADGRAMS.items():
    QUADGRAM_LOG[gram] = math.log10(count / QUADGRAM_TOTAL)

print(f"  Loaded {len(QUADGRAMS)} quadgrams, total count = {QUADGRAM_TOTAL}")

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt ciphertext with Vigenere using KRYPTOS alphabet."""
    pt = []
    for i, c in enumerate(ct):
        ci = alpha.index(c)
        ki = alpha.index(key[i % len(key)])
        pi = (ci - ki) % 26
        pt.append(alpha[pi])
    return "".join(pt)


def compute_ic(text):
    """Compute Index of Coincidence."""
    if len(text) < 2:
        return 0.0
    counts = Counter(text)
    n = len(text)
    ic = sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))
    return ic


def quadgram_score(text):
    """Compute quadgram log-likelihood score (higher = more English-like)."""
    if len(text) < 4:
        return -999999
    score = 0.0
    for i in range(len(text) - 3):
        gram = text[i:i+4]
        score += QUADGRAM_LOG.get(gram, LOG_FLOOR)
    return score


def normalized_quadgram_score(text):
    """Quadgram score normalized per quadgram (for comparison across lengths)."""
    if len(text) < 4:
        return -999999
    n_quads = len(text) - 3
    return quadgram_score(text) / n_quads


def find_words(text, min_len=3):
    """Find known words in text."""
    found = []
    for word in SEARCH_WORDS:
        if len(word) >= min_len and word in text:
            pos = text.find(word)
            found.append((word, pos))
    return found


def report(label, extracted, max_label_width=60):
    """Report IC, quadgram score, words found for an extracted string."""
    if len(extracted) < 4:
        return None
    ic = compute_ic(extracted)
    qs = normalized_quadgram_score(extracted)
    words = find_words(extracted)
    return {
        "label": label,
        "text": extracted,
        "length": len(extracted),
        "ic": ic,
        "qscore": qs,
        "words": words,
    }


def print_result(r, show_text=True):
    """Pretty-print a result dict."""
    if r is None:
        return
    words_str = ", ".join(f"{w}@{p}" for w, p in r["words"]) if r["words"] else "none"
    print(f"  {r['label'][:70]:<70s} | len={r['length']:3d} | IC={r['ic']:.4f} | QS={r['qscore']:.3f} | words: {words_str}")
    if show_text and r["length"] <= 100:
        print(f"    Text: {r['text']}")


def print_top_results(results, n=10, label=""):
    """Print top N results sorted by quadgram score."""
    valid = [r for r in results if r is not None]
    valid.sort(key=lambda r: r["qscore"], reverse=True)
    print(f"\n{'='*100}")
    print(f"  TOP {n} RESULTS {label}")
    print(f"{'='*100}")
    for r in valid[:n]:
        print_result(r, show_text=True)
    return valid[:n]


# ============================================================
# DECRYPT K4 WITH BEST KEY
# ============================================================

print("\n" + "="*100)
print("  VIGENERE DECRYPTION OF K4")
print("="*100)

VIG_PT = vigenere_decrypt(K4_CT, BEST_KEY)
print(f"  Ciphertext:  {K4_CT}")
print(f"  Key:         {BEST_KEY} (period {KEY_PERIOD})")
print(f"  Vig output:  {VIG_PT}")
print(f"  Length:       {len(VIG_PT)}")
print(f"  IC:           {compute_ic(VIG_PT):.4f}")
print(f"  Quad score:   {normalized_quadgram_score(VIG_PT):.3f}")
print(f"  Words found:  {find_words(VIG_PT)}")

# ============================================================
# TEST 1: REGULAR EXTRACTION PATTERNS
# ============================================================

print("\n" + "="*100)
print("  TEST 1: REGULAR EXTRACTION PATTERNS (every Nth char, various offsets)")
print("="*100)

all_results = []

for step in range(2, 8):
    for offset in range(step):
        extracted = VIG_PT[offset::step]
        label = f"Every {step}th char, offset={offset}"
        r = report(label, extracted)
        all_results.append(r)
        if r and (r["ic"] > 0.055 or r["words"]):
            print_result(r)

# Also test complement: remove every Nth char
for step in range(2, 8):
    for offset in range(step):
        extracted = "".join(VIG_PT[i] for i in range(len(VIG_PT)) if i % step != offset)
        label = f"Remove every {step}th char, offset={offset}"
        r = report(label, extracted)
        all_results.append(r)
        if r and (r["ic"] > 0.055 or r["words"]):
            print_result(r)

print_top_results(all_results, 10, "(Test 1: Regular extraction)")

# ============================================================
# TEST 2: W-POSITION BASED EXTRACTION
# ============================================================

print("\n" + "="*100)
print("  TEST 2: W-POSITION BASED EXTRACTION")
print("="*100)

# Find W positions in Vigenere output
w_positions = [i for i, c in enumerate(VIG_PT) if c == "W"]
print(f"  W positions in Vigenere output: {w_positions}")

# Also find W positions in ciphertext
w_ct_positions = [i for i, c in enumerate(K4_CT) if c == "W"]
print(f"  W positions in ciphertext: {w_ct_positions}")

test2_results = []

# Extract segments between W positions
boundaries = [-1] + w_positions + [len(VIG_PT)]
segments = []
for i in range(len(boundaries) - 1):
    seg = VIG_PT[boundaries[i]+1:boundaries[i+1]]
    if seg:
        segments.append(seg)

print(f"\n  Segments between W's in Vigenere output:")
for i, seg in enumerate(segments):
    print(f"    Segment {i}: '{seg}' (len={len(seg)})")

# Concatenate segments without W's
no_w = "".join(segments)
r = report("All chars except W positions", no_w)
test2_results.append(r)
print_result(r)

# Try extracting every 2nd, 3rd char within each segment
for step in range(2, 5):
    for offset in range(step):
        extracted = "".join(seg[offset::step] for seg in segments)
        label = f"W-segments, every {step}th, offset={offset}"
        r = report(label, extracted)
        test2_results.append(r)
        if r and (r["ic"] > 0.05 or r["words"]):
            print_result(r)

# Try first/last char of each segment
first_chars = "".join(seg[0] for seg in segments if seg)
last_chars = "".join(seg[-1] for seg in segments if seg)
test2_results.append(report("First char of each W-segment", first_chars))
test2_results.append(report("Last char of each W-segment", last_chars))

print_top_results(test2_results, 5, "(Test 2: W-position extraction)")

# ============================================================
# TEST 3: ODD/EVEN POSITION EXTRACTION
# ============================================================

print("\n" + "="*100)
print("  TEST 3: ODD/EVEN POSITION EXTRACTION")
print("="*100)

test3_results = []

even_chars = VIG_PT[0::2]
odd_chars = VIG_PT[1::2]

r_even = report("Even positions (0,2,4,...)", even_chars)
r_odd = report("Odd positions (1,3,5,...)", odd_chars)
test3_results.extend([r_even, r_odd])
print_result(r_even)
print_result(r_odd)

# Test mod-3 splits
for offset in range(3):
    extracted = "".join(VIG_PT[i] for i in range(offset, len(VIG_PT), 3))
    complement = "".join(VIG_PT[i] for i in range(len(VIG_PT)) if i % 3 != offset)
    label_ext = f"Mod 3 = {offset}"
    label_comp = f"Mod 3 != {offset}"
    r1 = report(label_ext, extracted)
    r2 = report(label_comp, complement)
    test3_results.extend([r1, r2])
    print_result(r1)
    print_result(r2)

print_top_results(test3_results, 5, "(Test 3: Odd/Even)")

# ============================================================
# TEST 4: KEY-POSITION BASED EXTRACTION
# ============================================================

print("\n" + "="*100)
print("  TEST 4: KEY-POSITION BASED EXTRACTION (specific key positions mod 29)")
print("="*100)

test4_results = []

# Which key positions map to which key letters?
print(f"\n  Key: {BEST_KEY}")
for pos in range(KEY_PERIOD):
    chars_at_pos = [VIG_PT[i] for i in range(pos, len(VIG_PT), KEY_PERIOD)]
    print(f"    Key pos {pos:2d} (key='{BEST_KEY[pos]}') -> {''.join(chars_at_pos)} (IC={compute_ic(''.join(chars_at_pos)):.3f})")

# Test: extract chars where key letter is a vowel vs consonant
vowels = set("AEIOU")
vowel_positions = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] in vowels]
consonant_positions = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] not in vowels]

v_text = "".join(VIG_PT[i] for i in vowel_positions)
c_text = "".join(VIG_PT[i] for i in consonant_positions)

r_v = report("Key-vowel positions", v_text)
r_c = report("Key-consonant positions", c_text)
test4_results.extend([r_v, r_c])
print(f"\n  Key-vowel positions: {vowel_positions[:20]}...")
print_result(r_v)
print(f"  Key-consonant positions: {consonant_positions[:20]}...")
print_result(r_c)

# Test: extract chars from specific subsets of key positions
key_letter_positions = {}
for pos in range(KEY_PERIOD):
    letter = BEST_KEY[pos]
    if letter not in key_letter_positions:
        key_letter_positions[letter] = []
    key_letter_positions[letter].append(pos)

print(f"\n  Key letter groupings:")
for letter, positions in sorted(key_letter_positions.items()):
    print(f"    '{letter}': key positions {positions}")

# Extract based on each unique key letter
for letter, key_positions in sorted(key_letter_positions.items()):
    extract_positions = []
    for kp in key_positions:
        extract_positions.extend(range(kp, len(VIG_PT), KEY_PERIOD))
    extract_positions.sort()
    extracted = "".join(VIG_PT[i] for i in extract_positions)
    label = f"Key letter '{letter}' (key pos {key_positions})"
    r = report(label, extracted)
    test4_results.append(r)

# Extract complement: all chars EXCEPT those at positions where key = specific letter
for letter, key_positions in sorted(key_letter_positions.items()):
    exclude_positions = set()
    for kp in key_positions:
        exclude_positions.update(range(kp, len(VIG_PT), KEY_PERIOD))
    extracted = "".join(VIG_PT[i] for i in range(len(VIG_PT)) if i not in exclude_positions)
    label = f"Exclude key letter '{letter}'"
    r = report(label, extracted)
    test4_results.append(r)

# Try extracting first half vs second half of key positions
first_half_kp = list(range(KEY_PERIOD // 2))
second_half_kp = list(range(KEY_PERIOD // 2, KEY_PERIOD))

fh_positions = []
for kp in first_half_kp:
    fh_positions.extend(range(kp, len(VIG_PT), KEY_PERIOD))
fh_positions.sort()
fh_text = "".join(VIG_PT[i] for i in fh_positions)

sh_positions = []
for kp in second_half_kp:
    sh_positions.extend(range(kp, len(VIG_PT), KEY_PERIOD))
sh_positions.sort()
sh_text = "".join(VIG_PT[i] for i in sh_positions)

test4_results.append(report("First 14 key positions (0-13)", fh_text))
test4_results.append(report("Last 15 key positions (14-28)", sh_text))

# Try combinations of 2 key positions removed
print("\n  Testing removal of key position pairs...")
best_removal = None
best_removal_score = -999999
for kp1, kp2 in itertools.combinations(range(KEY_PERIOD), 2):
    exclude = set()
    exclude.update(range(kp1, len(VIG_PT), KEY_PERIOD))
    exclude.update(range(kp2, len(VIG_PT), KEY_PERIOD))
    extracted = "".join(VIG_PT[i] for i in range(len(VIG_PT)) if i not in exclude)
    qs = normalized_quadgram_score(extracted)
    if qs > best_removal_score:
        best_removal_score = qs
        best_removal = (kp1, kp2, extracted)

if best_removal:
    kp1, kp2, text = best_removal
    label = f"Remove key positions {kp1},{kp2}"
    r = report(label, text)
    test4_results.append(r)
    print(f"  Best pair removal: positions {kp1},{kp2}")
    print_result(r)

print_top_results(test4_results, 10, "(Test 4: Key-position based)")

# ============================================================
# TEST 5: GRILLE/MASK PATTERNS
# ============================================================

print("\n" + "="*100)
print("  TEST 5: GRILLE/MASK PATTERNS (key-value based masks)")
print("="*100)

test5_results = []

# Test: positions where key letter maps to specific KRYPTOS index
for target_idx in range(26):
    target_letter = KRYPTOS_ALPHA[target_idx]
    positions = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] == target_letter]
    if positions:
        extracted = "".join(VIG_PT[i] for i in positions)
        label = f"Key value = {target_letter} (idx {target_idx})"
        r = report(label, extracted)
        test5_results.append(r)

# Test: positions where key index is even/odd
for parity_name, parity in [("even", 0), ("odd", 1)]:
    positions = [i for i in range(len(VIG_PT)) if KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) % 2 == parity]
    extracted = "".join(VIG_PT[i] for i in positions)
    label = f"Key index parity = {parity_name}"
    r = report(label, extracted)
    test5_results.append(r)
    print_result(r)

# Test: positions where key index > threshold
for threshold in [5, 10, 13, 15, 20]:
    positions_above = [i for i in range(len(VIG_PT)) if KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) > threshold]
    positions_below = [i for i in range(len(VIG_PT)) if KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) <= threshold]
    
    if len(positions_above) >= 4:
        extracted_a = "".join(VIG_PT[i] for i in positions_above)
        r = report(f"Key index > {threshold}", extracted_a)
        test5_results.append(r)
    
    if len(positions_below) >= 4:
        extracted_b = "".join(VIG_PT[i] for i in positions_below)
        r = report(f"Key index <= {threshold}", extracted_b)
        test5_results.append(r)

# Test: binary mask from key - positions where key letter is in first/second half of alphabet
first_half_alpha = set(KRYPTOS_ALPHA[:13])
second_half_alpha = set(KRYPTOS_ALPHA[13:])

fh_pos = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] in first_half_alpha]
sh_pos = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] in second_half_alpha]

test5_results.append(report("Key in KRYPTOS[0:13]", "".join(VIG_PT[i] for i in fh_pos)))
test5_results.append(report("Key in KRYPTOS[13:26]", "".join(VIG_PT[i] for i in sh_pos)))

# Test: Use key letter indices as a binary mask (bit 0, bit 1, etc.)
for bit in range(5):
    positions_set = [i for i in range(len(VIG_PT)) if (KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) >> bit) & 1]
    positions_unset = [i for i in range(len(VIG_PT)) if not ((KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) >> bit) & 1)]
    
    if len(positions_set) >= 4:
        test5_results.append(report(f"Key index bit {bit} = 1", "".join(VIG_PT[i] for i in positions_set)))
    if len(positions_unset) >= 4:
        test5_results.append(report(f"Key index bit {bit} = 0", "".join(VIG_PT[i] for i in positions_unset)))

print_top_results(test5_results, 10, "(Test 5: Grille/Mask patterns)")

# ============================================================
# TEST 6: MATHEMATICAL POSITION EXTRACTION
# ============================================================

print("\n" + "="*100)
print("  TEST 6: MATHEMATICAL POSITION EXTRACTION (primes, fibonacci, triangular, etc.)")
print("="*100)

test6_results = []

# Prime positions
def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

prime_positions = [i for i in range(len(VIG_PT)) if is_prime(i)]
non_prime_positions = [i for i in range(len(VIG_PT)) if not is_prime(i)]

r_prime = report("Prime positions", "".join(VIG_PT[i] for i in prime_positions))
r_nonprime = report("Non-prime positions", "".join(VIG_PT[i] for i in non_prime_positions))
test6_results.extend([r_prime, r_nonprime])
print_result(r_prime)
print_result(r_nonprime)

# Fibonacci positions
fib = [0, 1]
while fib[-1] < len(VIG_PT):
    fib.append(fib[-1] + fib[-2])
fib_positions = [f for f in fib if f < len(VIG_PT)]
non_fib = [i for i in range(len(VIG_PT)) if i not in set(fib_positions)]

r_fib = report("Fibonacci positions", "".join(VIG_PT[i] for i in fib_positions))
r_nonfib = report("Non-Fibonacci positions", "".join(VIG_PT[i] for i in non_fib))
test6_results.extend([r_fib, r_nonfib])
print_result(r_fib)

# Triangular number positions
tri_positions = []
n = 0
while n * (n + 1) // 2 < len(VIG_PT):
    tri_positions.append(n * (n + 1) // 2)
    n += 1
non_tri = [i for i in range(len(VIG_PT)) if i not in set(tri_positions)]

r_tri = report("Triangular number positions", "".join(VIG_PT[i] for i in tri_positions))
r_nontri = report("Non-triangular positions", "".join(VIG_PT[i] for i in non_tri))
test6_results.extend([r_tri, r_nontri])
print_result(r_tri)

# Square positions
sq_positions = [i*i for i in range(10) if i*i < len(VIG_PT)]
non_sq = [i for i in range(len(VIG_PT)) if i not in set(sq_positions)]

r_sq = report("Square number positions", "".join(VIG_PT[i] for i in sq_positions))
r_nonsq = report("Non-square positions", "".join(VIG_PT[i] for i in non_sq))
test6_results.extend([r_sq, r_nonsq])
print_result(r_sq)

# Powers of 2
pow2_positions = [2**i for i in range(7) if 2**i < len(VIG_PT)]
r_pow2 = report("Power of 2 positions", "".join(VIG_PT[i] for i in pow2_positions))
test6_results.append(r_pow2)

# Multiples of specific numbers
for m in [3, 5, 7, 11, 13, 29]:
    positions = list(range(0, len(VIG_PT), m))
    complement = [i for i in range(len(VIG_PT)) if i % m != 0]
    r_m = report(f"Multiples of {m}", "".join(VIG_PT[i] for i in positions))
    r_cm = report(f"Non-multiples of {m}", "".join(VIG_PT[i] for i in complement))
    test6_results.extend([r_m, r_cm])

print_top_results(test6_results, 10, "(Test 6: Mathematical positions)")

# ============================================================
# TEST 7: TWO-MESSAGE INTERLEAVE
# ============================================================

print("\n" + "="*100)
print("  TEST 7: TWO-MESSAGE INTERLEAVE")
print("="*100)

test7_results = []

# Simple interleave: split into 2..5 streams
for n_streams in [2, 3, 4, 5]:
    for stream_id in range(n_streams):
        extracted = VIG_PT[stream_id::n_streams]
        label = f"{n_streams}-way interleave, stream {stream_id}"
        r = report(label, extracted)
        test7_results.append(r)

# Alternate blocks
for block_size in [2, 3, 4, 5, 7, 10, 14, 15]:
    stream_a = []
    stream_b = []
    for i in range(len(VIG_PT)):
        block_num = i // block_size
        if block_num % 2 == 0:
            stream_a.append(VIG_PT[i])
        else:
            stream_b.append(VIG_PT[i])
    
    r_a = report(f"Block interleave (size={block_size}), even blocks", "".join(stream_a))
    r_b = report(f"Block interleave (size={block_size}), odd blocks", "".join(stream_b))
    test7_results.extend([r_a, r_b])

# Interleave based on ciphertext letter properties
ct_first_half = [i for i in range(len(K4_CT)) if KRYPTOS_ALPHA.index(K4_CT[i]) < 13]
ct_second_half = [i for i in range(len(K4_CT)) if KRYPTOS_ALPHA.index(K4_CT[i]) >= 13]

r_ct_fh = report("CT letter in KRYPTOS[0:13]", "".join(VIG_PT[i] for i in ct_first_half))
r_ct_sh = report("CT letter in KRYPTOS[13:26]", "".join(VIG_PT[i] for i in ct_second_half))
test7_results.extend([r_ct_fh, r_ct_sh])

# Interleave based on plaintext letter properties
pt_first_half = [i for i in range(len(VIG_PT)) if KRYPTOS_ALPHA.index(VIG_PT[i]) < 13]
pt_second_half = [i for i in range(len(VIG_PT)) if KRYPTOS_ALPHA.index(VIG_PT[i]) >= 13]

r_pt_fh = report("PT letter in KRYPTOS[0:13]", "".join(VIG_PT[i] for i in pt_first_half))
r_pt_sh = report("PT letter in KRYPTOS[13:26]", "".join(VIG_PT[i] for i in pt_second_half))
test7_results.extend([r_pt_fh, r_pt_sh])

print_top_results(test7_results, 10, "(Test 7: Two-message interleave)")

# ============================================================
# TEST 8: COLUMNAR EXTRACTION FROM PERIOD-29 GRID
# ============================================================

print("\n" + "="*100)
print("  TEST 8: COLUMNAR EXTRACTION FROM PERIOD-29 GRID")
print("="*100)

test8_results = []

# Lay out in 29-column grid
n_cols = KEY_PERIOD
n_rows = (len(VIG_PT) + n_cols - 1) // n_cols
grid = []
for r_idx in range(n_rows):
    row = []
    for c_idx in range(n_cols):
        pos = r_idx * n_cols + c_idx
        if pos < len(VIG_PT):
            row.append(VIG_PT[pos])
        else:
            row.append(".")
    grid.append(row)

print(f"\n  29-column grid of Vigenere output:")
print(f"  Key: {BEST_KEY}")
for r_idx, row in enumerate(grid):
    print(f"  Row {r_idx}: {''.join(row)}")

# Read individual columns
print(f"\n  Column contents:")
col_ics = []
for c_idx in range(n_cols):
    col = "".join(grid[r_idx][c_idx] for r_idx in range(n_rows) if grid[r_idx][c_idx] != ".")
    ic = compute_ic(col)
    col_ics.append((c_idx, ic, col))
    print(f"    Col {c_idx:2d} (key='{BEST_KEY[c_idx]}'): {col:5s} IC={ic:.3f}")

# Read columns in different orders
all_cols = "".join(col for _, _, col in col_ics)
test8_results.append(report("Columns L-to-R", all_cols))

# Read columns sorted by key letter
sorted_cols = sorted(col_ics, key=lambda x: KRYPTOS_ALPHA.index(BEST_KEY[x[0]]))
sorted_text = "".join(col for _, _, col in sorted_cols)
test8_results.append(report("Columns sorted by key letter", sorted_text))
print(f"\n  Column order sorted by key letter: {[c[0] for c in sorted_cols]}")
print(f"  Text: {sorted_text}")

# Read columns sorted by key letter (reverse)
sorted_cols_rev = sorted(col_ics, key=lambda x: KRYPTOS_ALPHA.index(BEST_KEY[x[0]]), reverse=True)
sorted_text_rev = "".join(col for _, _, col in sorted_cols_rev)
test8_results.append(report("Columns sorted by key letter (reverse)", sorted_text_rev))

# Read rows in different orders
for order_name, col_order in [
    ("reverse", list(range(n_cols-1, -1, -1))),
    ("snake (alt reverse)", None),
]:
    if order_name == "snake (alt reverse)":
        text = []
        for r_idx in range(n_rows):
            if r_idx % 2 == 0:
                for c_idx in range(n_cols):
                    pos = r_idx * n_cols + c_idx
                    if pos < len(VIG_PT):
                        text.append(VIG_PT[pos])
            else:
                for c_idx in range(n_cols-1, -1, -1):
                    pos = r_idx * n_cols + c_idx
                    if pos < len(VIG_PT):
                        text.append(VIG_PT[pos])
        test8_results.append(report(f"Snake reading (alt reverse rows)", "".join(text)))
    else:
        text = []
        for r_idx in range(n_rows):
            for c_idx in col_order:
                pos = r_idx * n_cols + c_idx
                if pos < len(VIG_PT):
                    text.append(VIG_PT[pos])
        test8_results.append(report(f"Rows read in {order_name} col order", "".join(text)))

# Columns with highest IC
high_ic_cols = sorted(col_ics, key=lambda x: x[1], reverse=True)
print(f"\n  Columns sorted by IC: {[(c[0], f'{c[1]:.3f}') for c in high_ic_cols]}")

# Take top half by IC
top_half = high_ic_cols[:n_cols//2]
top_half_positions = set()
for c_idx, _, _ in top_half:
    for r_idx in range(n_rows):
        pos = r_idx * n_cols + c_idx
        if pos < len(VIG_PT):
            top_half_positions.add(pos)
extracted = "".join(VIG_PT[i] for i in sorted(top_half_positions))
test8_results.append(report("Top half columns by IC", extracted))

# Bottom half by IC
bottom_half = high_ic_cols[n_cols//2:]
bottom_half_positions = set()
for c_idx, _, _ in bottom_half:
    for r_idx in range(n_rows):
        pos = r_idx * n_cols + c_idx
        if pos < len(VIG_PT):
            bottom_half_positions.add(pos)
extracted_b = "".join(VIG_PT[i] for i in sorted(bottom_half_positions))
test8_results.append(report("Bottom half columns by IC", extracted_b))

# Read diagonals
for d_offset in range(n_cols):
    diag = []
    for r_idx in range(n_rows):
        c_idx = (d_offset + r_idx) % n_cols
        pos = r_idx * n_cols + c_idx
        if pos < len(VIG_PT):
            diag.append(VIG_PT[pos])
    if len(diag) >= 4:
        test8_results.append(report(f"Diagonal starting col {d_offset}", "".join(diag)))

# Anti-diagonals
for d_offset in range(n_cols):
    diag = []
    for r_idx in range(n_rows):
        c_idx = (d_offset - r_idx) % n_cols
        pos = r_idx * n_cols + c_idx
        if pos < len(VIG_PT):
            diag.append(VIG_PT[pos])
    if len(diag) >= 4:
        test8_results.append(report(f"Anti-diagonal starting col {d_offset}", "".join(diag)))

print_top_results(test8_results, 10, "(Test 8: Columnar extraction)")

# ============================================================
# BONUS TEST: COMBINED APPROACHES
# ============================================================

print("\n" + "="*100)
print("  BONUS: COMBINED / CREATIVE APPROACHES")
print("="*100)

bonus_results = []

# A) Positions where Vigenere output matches ciphertext (PT[i] == CT[i])
match_positions = [i for i in range(len(VIG_PT)) if VIG_PT[i] == K4_CT[i]]
nonmatch_positions = [i for i in range(len(VIG_PT)) if VIG_PT[i] != K4_CT[i]]
print(f"\n  Positions where VIG_PT == CT: {match_positions} ({len(match_positions)} positions)")
if len(match_positions) >= 4:
    bonus_results.append(report("PT==CT positions", "".join(VIG_PT[i] for i in match_positions)))
bonus_results.append(report("PT!=CT positions", "".join(VIG_PT[i] for i in nonmatch_positions)))

# B) Positions where key shift is 0 (key = K = index 0)
zero_shift_positions = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] == "K"]
if zero_shift_positions:
    print(f"  Positions where key = K (shift 0): {zero_shift_positions}")
    bonus_results.append(report("Key shift = 0 positions", "".join(VIG_PT[i] for i in zero_shift_positions)))
    nonzero = [i for i in range(len(VIG_PT)) if BEST_KEY[i % KEY_PERIOD] != "K"]
    bonus_results.append(report("Key shift != 0 positions", "".join(VIG_PT[i] for i in nonzero)))

# C) Cumulative key-index sum mod N mask
key_indices = [KRYPTOS_ALPHA.index(BEST_KEY[i % KEY_PERIOD]) for i in range(len(VIG_PT))]
cumsum = []
s = 0
for ki in key_indices:
    s += ki
    cumsum.append(s)

for mod_val in [2, 3, 4, 5]:
    for target in range(mod_val):
        positions = [i for i in range(len(VIG_PT)) if cumsum[i] % mod_val == target]
        if len(positions) >= 4:
            extracted = "".join(VIG_PT[i] for i in positions)
            bonus_results.append(report(f"Cumulative key sum mod {mod_val} = {target}", extracted))

# D) Position XOR key-index mask
for mod_val in [2, 3, 4]:
    for target in range(mod_val):
        positions = [i for i in range(len(VIG_PT)) if (i ^ key_indices[i]) % mod_val == target]
        if len(positions) >= 4:
            extracted = "".join(VIG_PT[i] for i in positions)
            bonus_results.append(report(f"(pos XOR key_idx) mod {mod_val} = {target}", extracted))

# E) Position + key-index mask
for mod_val in [2, 3, 4, 5]:
    for target in range(mod_val):
        positions = [i for i in range(len(VIG_PT)) if (i + key_indices[i]) % mod_val == target]
        if len(positions) >= 4:
            extracted = "".join(VIG_PT[i] for i in positions)
            bonus_results.append(report(f"(pos + key_idx) mod {mod_val} = {target}", extracted))

# F) Self-referential: position where VIG_PT letter index determines next read position
visited = set()
pos = 0
route_text = []
for _ in range(len(VIG_PT)):
    if pos >= len(VIG_PT) or pos in visited:
        break
    visited.add(pos)
    route_text.append(VIG_PT[pos])
    pos = (pos + KRYPTOS_ALPHA.index(VIG_PT[pos]) + 1) % len(VIG_PT)
bonus_results.append(report(f"Self-referential route ({len(route_text)} chars)", "".join(route_text)))

# G) Extract only positions where VIG_PT letter frequency in full text is <= median
freq = Counter(VIG_PT)
sorted_freq = sorted(freq.values())
median_freq = sorted_freq[len(sorted_freq) // 2]
low_freq_positions = [i for i in range(len(VIG_PT)) if freq[VIG_PT[i]] <= median_freq]
high_freq_positions = [i for i in range(len(VIG_PT)) if freq[VIG_PT[i]] > median_freq]

bonus_results.append(report("Low-frequency PT letters", "".join(VIG_PT[i] for i in low_freq_positions)))
bonus_results.append(report("High-frequency PT letters", "".join(VIG_PT[i] for i in high_freq_positions)))

# H) Difference between consecutive key indices as mask
key_diffs = [0] + [(key_indices[i] - key_indices[i-1]) % 26 for i in range(1, len(key_indices))]
for mod_val in [2, 3]:
    for target in range(mod_val):
        positions = [i for i in range(len(VIG_PT)) if key_diffs[i] % mod_val == target]
        if len(positions) >= 4:
            extracted = "".join(VIG_PT[i] for i in positions)
            bonus_results.append(report(f"Key diff mod {mod_val} = {target}", extracted))

# I) Positions where CT letter == key letter
ct_eq_key = [i for i in range(len(K4_CT)) if K4_CT[i] == BEST_KEY[i % KEY_PERIOD]]
ct_neq_key = [i for i in range(len(K4_CT)) if K4_CT[i] != BEST_KEY[i % KEY_PERIOD]]
print(f"\n  Positions where CT == KEY: {ct_eq_key} ({len(ct_eq_key)} positions)")
if len(ct_eq_key) >= 4:
    bonus_results.append(report("CT==KEY positions (PT)", "".join(VIG_PT[i] for i in ct_eq_key)))
bonus_results.append(report("CT!=KEY positions (PT)", "".join(VIG_PT[i] for i in ct_neq_key)))

print_top_results(bonus_results, 15, "(Bonus: Combined approaches)")

# ============================================================
# GRAND SUMMARY
# ============================================================

print("\n" + "="*100)
print("  GRAND SUMMARY: TOP 25 ACROSS ALL TESTS")
print("="*100)

all_combined = all_results + test2_results + test3_results + test4_results + \
               test5_results + test6_results + test7_results + test8_results + bonus_results

valid_combined = [r for r in all_combined if r is not None and r["length"] >= 10]
valid_combined.sort(key=lambda r: r["qscore"], reverse=True)

print(f"\n  Total extraction patterns tested: {len([r for r in all_combined if r is not None])}")
print(f"  English reference IC: 0.0667, Random IC: 0.0385")
print(f"  Vigenere output IC: {compute_ic(VIG_PT):.4f}\n")

for i, r in enumerate(valid_combined[:25]):
    words_str = ", ".join(f"{w}@{p}" for w, p in r["words"]) if r["words"] else "none"
    flag = " ***" if r["ic"] > 0.055 else ""
    print(f"  {i+1:3d}. {r['label'][:65]:<65s} | len={r['length']:3d} | IC={r['ic']:.4f} | QS={r['qscore']:.3f}{flag} | {words_str}")
    if i < 10:
        print(f"       Text: {r['text'][:80]}")

# Highlight results with good IC
print(f"\n  Results with IC > 0.055 (possibly English-like):")
high_ic = [r for r in valid_combined if r["ic"] > 0.055]
high_ic.sort(key=lambda r: r["ic"], reverse=True)
for r in high_ic[:20]:
    words_str = ", ".join(f"{w}@{p}" for w, p in r["words"]) if r["words"] else "none"
    print(f"    IC={r['ic']:.4f} | QS={r['qscore']:.3f} | len={r['length']:3d} | {r['label'][:50]} | {words_str}")
    print(f"      Text: {r['text'][:80]}")

# Highlight results with found words
print(f"\n  Results with recognized words found:")
with_words = [r for r in valid_combined if r["words"]]
with_words.sort(key=lambda r: (-len(r["words"]), r["qscore"]))
for r in with_words[:20]:
    words_str = ", ".join(f"{w}@{p}" for w, p in r["words"])
    print(f"    Words: {words_str} | IC={r['ic']:.4f} | QS={r['qscore']:.3f} | len={r['length']:3d} | {r['label'][:50]}")
    print(f"      Text: {r['text'][:80]}")

print(f"\n{'='*100}")
print(f"  ANALYSIS COMPLETE")
print(f"{'='*100}")
