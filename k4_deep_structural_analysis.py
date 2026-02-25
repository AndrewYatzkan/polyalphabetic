#!/usr/bin/env python3
"""
Deep structural analysis of K4 and its Vigenere decryption.
Look for patterns that might reveal the second cipher layer.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c):
    return KRYPTOS.index(c)

def k_chr(i):
    return KRYPTOS[i % 26]

def vig_decrypt(ct, key):
    pt = []
    for i, c in enumerate(ct):
        ki = k_idx(key[i % len(key)])
        ci = k_idx(c)
        pt.append(k_chr((ci - ki) % 26))
    return ''.join(pt)

def vig_encrypt(pt, key):
    ct = []
    for i, c in enumerate(pt):
        ki = k_idx(key[i % len(key)])
        pi = k_idx(c)
        ct.append(k_chr((pi + ki) % 26))
    return ''.join(ct)

# Known key with best fill for positions 16-20
# From brute-force: OYNKYELYOIECBAQKCBNJQRDUMRIYW
# But let's also try with '?' for unknowns
KEY_KNOWN = "OYNKYELYOIECBAQK?????RDUMRIYW"
KEY_BEST = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"  # From brute-force best

print("=" * 80)
print("K4 DEEP STRUCTURAL ANALYSIS")
print("=" * 80)

# 1. Decrypt with best key
pt_best = vig_decrypt(K4, KEY_BEST)
print(f"\nK4 ciphertext:    {K4}")
print(f"Best key (29):    {KEY_BEST}")
print(f"Best plaintext:   {pt_best}")

# 2. Show the plaintext in a grid (period-29 columns)
print("\n--- Plaintext in 29-column grid ---")
print("     " + "".join(f"{i%10}" for i in range(29)))
print("     " + "-" * 29)
for row in range(4):
    start = row * 29
    end = min(start + 29, 97)
    chunk = pt_best[start:end]
    print(f"  {row}: {chunk}")

# 3. Show the CIPHERTEXT in a 29-column grid
print("\n--- Ciphertext in 29-column grid ---")
print("     " + "".join(f"{i%10}" for i in range(29)))
print("     " + "-" * 29)
for row in range(4):
    start = row * 29
    end = min(start + 29, 97)
    chunk = K4[start:end]
    print(f"  {row}: {chunk}")

# 4. Column analysis: read the grid by columns
print("\n--- Reading ciphertext columns top-to-bottom ---")
for col in range(29):
    chars = [K4[row*29 + col] for row in range(4) if row*29 + col < 97]
    print(f"  Col {col:2d}: {''.join(chars)}")

# 5. Key analysis: what do the known key positions spell?
print("\n--- Key analysis ---")
print(f"Key: {KEY_BEST}")
print(f"Known positions (0-15): {KEY_BEST[:16]}")
print(f"Unknown positions (16-20): {KEY_BEST[16:21]}")
print(f"Known positions (21-28): {KEY_BEST[21:]}")

# Check if key reversed, rotated, etc. gives anything
for rot in range(29):
    rotated = KEY_BEST[rot:] + KEY_BEST[:rot]
    # Check if it looks like English
    pass

# 6. IC (Index of Coincidence) of the plaintext
from collections import Counter
ct_counts = Counter(K4)
pt_counts = Counter(pt_best)
n = len(K4)
ic_ct = sum(c*(c-1) for c in ct_counts.values()) / (n*(n-1))
ic_pt = sum(c*(c-1) for c in pt_counts.values()) / (n*(n-1))
print(f"\nIC of ciphertext: {ic_ct:.4f}")
print(f"IC of plaintext:  {ic_pt:.4f}")
print(f"Expected English: ~0.0667")
print(f"Expected random:  ~0.0385")

# 7. Digram analysis of the plaintext
print("\n--- Digram frequency in plaintext ---")
digrams = Counter()
for i in range(len(pt_best)-1):
    digrams[pt_best[i:i+2]] += 1
top_digrams = digrams.most_common(20)
print(f"Top 20 digrams: {top_digrams}")

# English expected top digrams: TH, HE, IN, EN, NT, RE, ER, AN, TI, ON...
ENGLISH_COMMON_DIGRAMS = ["TH", "HE", "IN", "EN", "NT", "RE", "ER", "AN", "TI", "ON"]
for d in ENGLISH_COMMON_DIGRAMS:
    if d in digrams:
        print(f"  '{d}' found {digrams[d]} times")
    else:
        print(f"  '{d}' NOT found")

# 8. Look for repeating patterns in the plaintext
print("\n--- Repeating patterns in plaintext ---")
for length in range(3, 8):
    pattern_positions = {}
    for i in range(len(pt_best) - length + 1):
        pat = pt_best[i:i+length]
        if pat not in pattern_positions:
            pattern_positions[pat] = []
        pattern_positions[pat].append(i)
    repeats = {k: v for k, v in pattern_positions.items() if len(v) > 1}
    if repeats:
        for pat, positions in sorted(repeats.items(), key=lambda x: -len(x[1])):
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            print(f"  '{pat}' at positions {positions}, distances: {distances}")

# 9. Autokey check: does the plaintext serve as its own key somehow?
print("\n--- Autokey self-key check ---")
# In PT-autokey: key[i] = pt[i-P] for i >= P
# If the plaintext IS the autokey output, then there's a relationship between
# characters at distance P apart
for P in [1, 2, 3, 5, 7, 11, 13, 29]:
    matches = 0
    for i in range(P, len(pt_best)):
        if pt_best[i] == pt_best[i-P]:
            matches += 1
    expected = (len(pt_best) - P) / 26.0
    print(f"  Shift {P:2d}: {matches} matches (expected: {expected:.1f})")

# 10. Difference sequence analysis
print("\n--- Difference sequence (consecutive characters) ---")
diffs = []
for i in range(len(pt_best) - 1):
    d = (k_idx(pt_best[i+1]) - k_idx(pt_best[i])) % 26
    diffs.append(d)
diff_counts = Counter(diffs)
print(f"Difference distribution: {sorted(diff_counts.items())}")

# 11. Try reading the plaintext in various patterns
print("\n--- Alternative read orders ---")

# Read every Nth character
for skip in [2, 3, 5, 7, 11, 13, 29]:
    for start in range(min(skip, 5)):
        extracted = pt_best[start::skip]
        # Check for cribs
        if "BERLIN" in extracted or "CLOCK" in extracted or "NORTH" in extracted or "EAST" in extracted:
            print(f"  Skip-{skip} start-{start}: {extracted} *** CRIB FOUND ***")

# Read in spiral, zigzag, etc.
# Zigzag with various depths
for depth in [2, 3, 4, 5]:
    zigzag = [''] * depth
    for i, c in enumerate(pt_best):
        cycle_pos = i % (2 * (depth - 1)) if depth > 1 else 0
        row = cycle_pos if cycle_pos < depth else 2 * (depth - 1) - cycle_pos
        zigzag[row] += c
    result = ''.join(zigzag)
    if "BERLIN" in result or "NORTH" in result:
        print(f"  Zigzag depth-{depth}: {result} *** CRIB FOUND ***")

# 12. K4 ciphertext self-similarity check
print("\n--- Ciphertext self-similarity (Kasiski-like) ---")
for length in range(3, 8):
    ct_patterns = {}
    for i in range(len(K4) - length + 1):
        pat = K4[i:i+length]
        if pat not in ct_patterns:
            ct_patterns[pat] = []
        ct_patterns[pat].append(i)
    ct_repeats = {k: v for k, v in ct_patterns.items() if len(v) > 1}
    if ct_repeats:
        for pat, positions in sorted(ct_repeats.items(), key=lambda x: -len(x[1])):
            distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            print(f"  CT '{pat}' at {positions}, distances: {distances}, GCDs with 29: {[d%29 for d in distances]}")

# 13. Check if K4 contains any known cipher signatures
print("\n--- Cipher signature checks ---")
# Check if CT has bias toward certain positions (fractionation signature)
for pos in range(97):
    col = pos % 29
    # nothing specific to check without hypothesis

# Check letter frequency of CT
print(f"CT frequency: {sorted(ct_counts.items(), key=lambda x: -x[1])}")
print(f"PT frequency: {sorted(pt_counts.items(), key=lambda x: -x[1])}")

# 14. CRITICAL: Test if the plaintext from Vigenere can be un-scrambled
# by a SIMPLE monoalphabetic substitution to get English
print("\n--- Monoalphabetic substitution check ---")
# If there's a fixed substitution after Vigenere, the frequency distribution
# of the Vigenere output should match English (just with letters swapped)
# English frequency order: ETAOINSHRDLCUMWFGYPBVKJXQZ

# Our plaintext frequency order:
pt_freq_order = ''.join(c for c, _ in sorted(pt_counts.items(), key=lambda x: -x[1]))
print(f"PT frequency order:      {pt_freq_order}")
print(f"English frequency order: ETAOINSHRDLCUMWFGYPBVKXQZ")

# Build substitution: map most frequent PT letter -> E, etc.
ENGLISH_FREQ = "ETAOINSHRDLCUMWFGYPBVKXQZ"  # without J (not in KRYPTOS)
sub_map = {}
for i, pt_char in enumerate(pt_freq_order):
    if i < len(ENGLISH_FREQ):
        sub_map[pt_char] = ENGLISH_FREQ[i]
    else:
        sub_map[pt_char] = '?'

mono_result = ''.join(sub_map.get(c, '?') for c in pt_best)
print(f"Mono-substituted PT: {mono_result}")
# Check for words
for word in ["THE", "AND", "BERLIN", "CLOCK", "NORTH", "EAST", "THAT", "WITH", "FROM"]:
    if word in mono_result:
        print(f"  Found '{word}' in mono-sub result!")

# 15. Cross-period analysis: are certain key positions "special"?
print("\n--- Cross-period plaintext grouping ---")
for kp in range(29):
    chars = [pt_best[i] for i in range(kp, 97, 29)]
    ct_chars = [K4[i] for i in range(kp, 97, 29)]
    print(f"  Key pos {kp:2d}: CT={''.join(ct_chars)} PT={''.join(chars)} "
          f"PT_dist={dict(Counter(chars))}")

# 16. Look for the word KRYPTOS or PALIMPSEST or ABSCISSA in various transformations
print("\n--- Keyword search in transformations ---")
keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SANBORN", "SCHEIDT",
            "LANGLEY", "SHADOW", "SECRET", "BURIED", "HIDDEN"]
for kw in keywords:
    if kw in pt_best:
        print(f"  '{kw}' found in plaintext!")
    if kw in K4:
        print(f"  '{kw}' found in ciphertext!")
    # Check reversed
    if kw[::-1] in pt_best:
        print(f"  '{kw}' reversed found in plaintext!")

# 17. Numerical analysis of key
print("\n--- Key numerical properties ---")
key_vals = [k_idx(c) for c in KEY_BEST]
print(f"Key values (KRYPTOS idx): {key_vals}")
print(f"Key sum: {sum(key_vals)}")
print(f"Key sum mod 26: {sum(key_vals) % 26}")
print(f"Key product mod 26: {1}")  # compute properly
prod = 1
for v in key_vals:
    prod = (prod * v) % 26 if v != 0 else 0
print(f"Key product mod 26: {prod}")

# Check for arithmetic/geometric progressions in key
diffs_key = [(key_vals[i+1] - key_vals[i]) % 26 for i in range(len(key_vals)-1)]
print(f"Key differences: {diffs_key}")

# 18. CRITICAL: What if the masking is a NULL CIPHER?
# Read every Nth character of the plaintext
print("\n--- Null cipher extraction from plaintext ---")
for skip in range(2, 10):
    for start in range(skip):
        extracted = pt_best[start::skip]
        # Check for long English words (4+ chars)
        found_words = []
        for w in ["BERLIN", "CLOCK", "NORTH", "EAST", "UNDER", "ABOVE", "LAYER",
                   "SHADOW", "HIDDEN", "SECRET", "THERE", "WHERE", "POINT", "LIGHT",
                   "NIGHT", "PLACE", "STONE", "EARTH", "FIELD", "WORLD", "HANDS",
                   "HOURS", "WATCH", "COMPASS", "DEGREE", "BEARING", "BETWEEN",
                   "THROUGH", "BENEATH", "THE", "AND", "FOR", "NOT", "YOU", "ALL",
                   "SLOWLY", "DESPERATELY"]:
            if w in extracted:
                found_words.append(w)
        if found_words:
            print(f"  Skip-{skip} start-{start}: {extracted}")
            print(f"    Words found: {found_words}")

# 19. Matrix layout analysis
print("\n--- Matrix layouts ---")
# Try laying out in various grid sizes and reading columns
for width in [7, 8, 9, 10, 11, 13, 14, 29]:
    # Read columns
    col_read = ''
    for col in range(width):
        for row in range((97 + width - 1) // width):
            pos = row * width + col
            if pos < 97:
                col_read += pt_best[pos]

    # Check for cribs
    has_crib = False
    for crib in ["BERLINCLOCK", "EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK"]:
        if crib in col_read:
            has_crib = True
            pos = col_read.index(crib)
            print(f"  Width {width}: '{crib}' at pos {pos} in column-read!")

    if not has_crib and width in [7, 29]:
        print(f"  Width {width}: {col_read[:50]}...")

# 20. Check the "Vigenere output as intermediate" hypothesis
# What if we need to apply a SECOND Vigenere with a different key?
print("\n--- Double Vigenere test ---")
# If ct = Vig2(Vig1(pt, key1), key2), then:
# Vig2_decrypt(ct, key2) = Vig1(pt, key1)
# We've been computing Vig1_decrypt(ct, key1) which gives WRONG result
# The correct approach: Vig2_decrypt(ct, key2) first, then Vig1_decrypt(result, key1)
# This is equivalent to: pt = Vig1_decrypt(Vig2_decrypt(ct, key2), key1)
# But Vig is linear, so: pt = Vig_decrypt(ct, key1+key2) where addition is elementwise
# So double Vigenere = single Vigenere with combined key!
# UNLESS key2 has a DIFFERENT period.

# Test second key with small periods (2, 3, 5, 7)
for period2 in [2, 3, 5, 7, 11, 13]:
    best_score = -1
    best_key2 = None
    best_pt = None

    # For small periods, we can brute force the second key
    if period2 <= 3:
        from itertools import product
        for combo in product(range(26), repeat=period2):
            key2 = ''.join(KRYPTOS[v] for v in combo)
            # First decrypt with key2, then with key1
            intermediate = vig_decrypt(K4, key2)
            final = vig_decrypt(intermediate, KEY_BEST)

            # Quick score: count common English trigrams
            score = 0
            for trig in ["THE", "AND", "ING", "ION", "TIO", "ENT", "FOR", "ATE"]:
                score += final.count(trig) * 10
            for dig in ["TH", "HE", "IN", "ER", "AN", "RE", "ON", "EN"]:
                score += final.count(dig) * 3

            if score > best_score:
                best_score = score
                best_key2 = key2
                best_pt = final

    if best_score > 0:
        print(f"  Period-{period2} second key: {best_key2} score={best_score}")
        print(f"    PT: {best_pt}")
    else:
        if period2 <= 3:
            print(f"  Period-{period2}: No improvement found (best score 0)")

print("\nDone.")
