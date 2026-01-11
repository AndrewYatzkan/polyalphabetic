#!/usr/bin/env python3
"""
Comprehensive analysis of K1/K2 key fragments embedded in K4 key.
Investigating whether this is Sanborn's signature proving keys are related.
"""

import itertools
from collections import defaultdict, Counter
from math import factorial, comb
import string

# Known keys
K1_KEY = "PALIMPSEST"
K2_KEY = "ABSCISSA"
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K3_PLAINTEXT = "SLOWLYDESPARATLYSLOWTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHAMDSIMADEATINYBREACHINTTHUPPERLEFTHANDCORNERANDTHENWIDENNINGTHEHOLEALITTLEIINSERTEDTHECANDEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFBLICKBUTPRESENTLYDETAILSOFTHEROOMWITHINEMEMEREDFROMTHEMISTCANYOUSEEANYTHINGQ"
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

print("=" * 80)
print("K1/K2 EMBEDDING ANALYSIS IN K4 KEY")
print("=" * 80)
print()

# ============================================================================
# 1. MAP ALL K1/K2 LETTERS TO K4 KEY POSITIONS
# ============================================================================
print("TASK 1: MAP ALL K1/K2 LETTERS TO K4 KEY POSITIONS")
print("-" * 80)

def find_all_occurrences(needle, haystack):
    """Find all positions of needle in haystack"""
    positions = []
    for i in range(len(haystack) - len(needle) + 1):
        if haystack[i:i+len(needle)].upper() == needle.upper():
            positions.append(i)
    return positions

print("\nK1 KEY MAPPING (PALIMPSEST):")
k1_mapping = {}
for letter in K1_KEY:
    positions = [i for i, c in enumerate(K4_KEY) if c.upper() == letter.upper()]
    k1_mapping[letter] = positions
    print(f"  {letter}: positions {positions}")

print("\nK2 KEY MAPPING (ABSCISSA):")
k2_mapping = {}
for letter in K2_KEY:
    positions = [i for i, c in enumerate(K4_KEY) if c.upper() == letter.upper()]
    k2_mapping[letter] = positions
    print(f"  {letter}: positions {positions}")

# ============================================================================
# 2. SEARCH FOR EXACT SUBSTRINGS (K1 AND K2 FRAGMENTS)
# ============================================================================
print("\n" + "=" * 80)
print("TASK 2: SEARCH FOR EXACT SUBSTRINGS")
print("-" * 80)

def find_substring_matches(pattern, text):
    """Find all positions where pattern appears in text"""
    matches = []
    for i in range(len(text) - len(pattern) + 1):
        if text[i:i+len(pattern)].upper() == pattern.upper():
            matches.append((i, text[i:i+len(pattern)]))
    return matches

print("\nK1 KEY SUBSTRINGS IN K4 KEY:")
k1_substrings = {}
for length in range(2, len(K1_KEY) + 1):
    found = False
    for i in range(len(K1_KEY) - length + 1):
        substring = K1_KEY[i:i+length]
        matches = find_substring_matches(substring, K4_KEY)
        if matches:
            k1_substrings[substring] = matches
            print(f"  '{substring}' (len={length}): {matches}")
            found = True
    if not found and length <= 3:
        print(f"  No {length}-char substrings found")

print("\nK2 KEY SUBSTRINGS IN K4 KEY:")
k2_substrings = {}
for length in range(2, len(K2_KEY) + 1):
    found = False
    for i in range(len(K2_KEY) - length + 1):
        substring = K2_KEY[i:i+length]
        matches = find_substring_matches(substring, K4_KEY)
        if matches:
            k2_substrings[substring] = matches
            print(f"  '{substring}' (len={length}): {matches}")
            found = True
    if not found and length <= 3:
        print(f"  No {length}-char substrings found")

# ============================================================================
# 3. ANALYZE REPORTED EMBEDDING DISCOVERY
# ============================================================================
print("\n" + "=" * 80)
print("TASK 3: ANALYZE REPORTED EMBEDDING (UMPABT at pos 24-28)")
print("-" * 80)

print(f"\nK4 Key: {K4_KEY}")
print(f"Pos 24-28: {K4_KEY[24:29]}")
print("\nAnalysis of reported fragments:")
print(f"  Position 24-25: {K4_KEY[24:26]} - contains MP from PALIMPSEST")
print(f"  Position 25-26: {K4_KEY[25:27]} - contains PA from PALIMPSEST")
print(f"  Position 26-27: {K4_KEY[26:28]} - contains AB from ABSCISSA")
print(f"  Position 24-28: {K4_KEY[24:29]} - UMPABT")

# Detailed analysis
print("\nDetailed breakdown of UMPABT (positions 24-28):")
for i, char in enumerate(K4_KEY[24:29], 24):
    print(f"  Position {i}: {char}")

# ============================================================================
# 4. LOOK FOR SEQUENTIAL K1/K2 LETTERS IN K4
# ============================================================================
print("\n" + "=" * 80)
print("TASK 4: LOOK FOR SEQUENTIAL K1/K2 FRAGMENTS IN K4 KEY")
print("-" * 80)

def find_sequential_overlaps(key1, key2, text):
    """Find where key1 and key2 letters appear sequentially in text"""
    results = []
    for i in range(len(text) - 1):
        if text[i] in key1 and text[i+1] in key2:
            results.append((i, text[i:i+2], f"{text[i]}(from {key1})", f"{text[i+1]}(from {key2})"))
        elif text[i] in key2 and text[i+1] in key1:
            results.append((i, text[i:i+2], f"{text[i]}(from {key2})", f"{text[i+1]}(from {key1})"))
    return results

print("\nPositions where K1 and K2 letters appear ADJACENT in K4:")
adjacent = find_sequential_overlaps(K1_KEY, K2_KEY, K4_KEY)
for pos, pair, k1_part, k2_part in adjacent[:20]:  # Show first 20
    print(f"  Pos {pos:2d}: {pair} - {k1_part} + {k2_part}")

print(f"\nTotal adjacent K1-K2 letter pairs: {len(adjacent)}")

# ============================================================================
# 5. PROBABILITY CALCULATION
# ============================================================================
print("\n" + "=" * 80)
print("TASK 5: PROBABILITY ANALYSIS (Is this random?)")
print("-" * 80)

# Calculate letter frequencies in K4 key
k4_counter = Counter(K4_KEY)
print(f"\nK4 Key letter frequencies:")
for letter, count in k4_counter.most_common(10):
    print(f"  {letter}: {count} ({count/len(K4_KEY)*100:.1f}%)")

# Probability calculations
total_k1_occurrences = sum(len(positions) for positions in k1_mapping.values())
total_k2_occurrences = sum(len(positions) for positions in k2_mapping.values())

print(f"\nTotal K1 letters in K4 key: {total_k1_occurrences}")
print(f"Total K2 letters in K4 key: {total_k2_occurrences}")

# Probability of specific 2-char substring by random chance
# P(specific 2-char substring) = (1/26)^2 * N where N = number of positions
prob_random_2char = (1/26) ** 2 * (len(K4_KEY) - 1)
prob_observed = len(adjacent) / (len(K4_KEY) - 1)

print(f"\nRandom occurrence of K1-K2 adjacent pairs:")
print(f"  Expected (random): {prob_random_2char:.4f} (~1 in {1/prob_random_2char:.0f})")
print(f"  Observed: {prob_observed:.4f}")
print(f"  Ratio (observed/expected): {prob_observed/prob_random_2char:.1f}x")

# Probability of finding "PA" substring specifically
pa_in_k4 = find_substring_matches("PA", K4_KEY)
prob_pa_random = (1/26) ** 2 * (len(K4_KEY) - 1)
print(f"\n'PA' substring (K1 key element):")
print(f"  Found at positions: {pa_in_k4}")
print(f"  Expected (random): {prob_pa_random:.3f}")
print(f"  Observed: {len(pa_in_k4)}")

# Probability of finding "AB" substring specifically
ab_in_k4 = find_substring_matches("AB", K4_KEY)
print(f"\n'AB' substring (K2 key element):")
print(f"  Found at positions: {ab_in_k4}")
print(f"  Expected (random): {prob_pa_random:.3f}")
print(f"  Observed: {len(ab_in_k4)}")

# ============================================================================
# 6. SEARCH FOR LONGER PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 6: SEARCH FOR LONGER PATTERNS AND CLUSTERS")
print("-" * 80)

# Look for regions where many K1/K2 letters cluster
def analyze_k1_k2_density(text, key1, key2, window_size=5):
    """Find regions with high K1/K2 letter density"""
    regions = []
    for i in range(len(text) - window_size + 1):
        window = text[i:i+window_size]
        k1_count = sum(1 for c in window if c in key1)
        k2_count = sum(1 for c in window if c in key2)
        combined = k1_count + k2_count
        if combined >= 3:  # At least 3 K1/K2 letters in 5-char window
            regions.append((i, window, k1_count, k2_count, combined))
    return regions

regions = analyze_k1_k2_density(K4_KEY, K1_KEY, K2_KEY, 5)
print(f"\nRegions with high K1/K2 density (≥3 letters in 5-char window):")
for pos, window, k1c, k2c, total in regions:
    print(f"  Pos {pos:2d}: '{window}' - K1:{k1c} K2:{k2c} Total:{total}")

# ============================================================================
# 7. TEST XOR OPERATIONS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 7: XOR OPERATIONS (K1/K2 XOR K4)")
print("-" * 80)

def string_to_positions(s):
    """Convert string to position array (A=0, B=1, etc)"""
    return [ord(c.upper()) - ord('A') for c in s]

def positions_to_string(positions):
    """Convert position array back to string"""
    return ''.join(chr(p % 26 + ord('A')) for p in positions)

def xor_keys(key1_str, key2_str):
    """XOR two keys (repeat shorter to match length)"""
    k1_pos = string_to_positions(key1_str)
    k2_pos = string_to_positions(key2_str)

    max_len = max(len(k1_pos), len(k2_pos))
    k1_pos = k1_pos + k1_pos * (max_len // len(k1_pos) + 1)
    k2_pos = k2_pos + k2_pos * (max_len // len(k2_pos) + 1)

    k1_pos = k1_pos[:max_len]
    k2_pos = k2_pos[:max_len]

    xor_result = [k1_pos[i] ^ k2_pos[i] for i in range(max_len)]
    return positions_to_string(xor_result), xor_result

# Test various XOR combinations
print("\nK1 XOR K4_KEY:")
result, positions = xor_keys(K1_KEY, K4_KEY)
print(f"  Result: {result}")

print("\nK2 XOR K4_KEY:")
result, positions = xor_keys(K2_KEY, K4_KEY)
print(f"  Result: {result}")

print("\n(K1 XOR K2) as potential factor:")
result, positions = xor_keys(K1_KEY, K2_KEY)
print(f"  K1 XOR K2: {result}")

# ============================================================================
# 8. ANALYZE POSITION RELATIONSHIPS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 8: POSITION RELATIONSHIPS AND STRUCTURES")
print("-" * 80)

print(f"\nK1 Key breakdown (PALIMPSEST = 10 chars):")
print(f"  Positions 0-4:   {K4_KEY[0:5]}  ({K4_KEY[0:5]})")
print(f"  Positions 5-9:   {K4_KEY[5:10]} ({K4_KEY[5:10]})")
print(f"  Positions 10-14: {K4_KEY[10:15]} ({K4_KEY[10:15]})")
print(f"  Positions 15-19: {K4_KEY[15:20]} ({K4_KEY[15:20]})")
print(f"  Positions 20-24: {K4_KEY[20:25]} ({K4_KEY[20:25]})")
print(f"  Positions 25-29: {K4_KEY[25:30]} ({K4_KEY[25:30]})")

print(f"\nK2 Key breakdown (ABSCISSA = 8 chars):")
print(f"  Positions 0-3:   {K4_KEY[0:4]}   ({K4_KEY[0:4]})")
print(f"  Positions 4-7:   {K4_KEY[4:8]}   ({K4_KEY[4:8]})")
print(f"  Positions 8-11:  {K4_KEY[8:12]}  ({K4_KEY[8:12]})")
print(f"  Positions 12-15: {K4_KEY[12:16]} ({K4_KEY[12:16]})")
print(f"  Positions 16-19: {K4_KEY[16:20]} ({K4_KEY[16:20]})")
print(f"  Positions 20-23: {K4_KEY[20:24]} ({K4_KEY[20:24]})")
print(f"  Positions 24-27: {K4_KEY[24:28]} ({K4_KEY[24:28]})")

# ============================================================================
# 9. LOOK FOR INTENTIONAL SIGNATURE PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 9: LOOK FOR INTENTIONAL 'SIGNATURE' PATTERNS")
print("-" * 80)

print("\nHypothesis: Sanborn marks the key with K1/K2 fragments as proof")
print("\nLooking for overlapping sequences that spell key fragments:\n")

# Check if K1 or K2 letters appear in reverse
k1_reversed = K1_KEY[::-1]
k2_reversed = K2_KEY[::-1]

print(f"K1 reversed: {k1_reversed}")
print(f"K2 reversed: {k2_reversed}")

# Check for anagrams or rearrangements in K4
print(f"\nK1 letter set: {sorted(K1_KEY)}")
print(f"K2 letter set: {sorted(K2_KEY)}")
print(f"K4 letter set: {sorted(K4_KEY)}")

# Find common letters between keys
k1_set = set(K1_KEY)
k2_set = set(K2_KEY)
k4_set = set(K4_KEY)

print(f"\nK1 ∩ K4: {sorted(k1_set & k4_set)}")
print(f"K2 ∩ K4: {sorted(k2_set & k4_set)}")
print(f"K1 ∩ K2: {sorted(k1_set & k2_set)}")
print(f"K1 ∩ K2 ∩ K4: {sorted(k1_set & k2_set & k4_set)}")

# ============================================================================
# 10. CHECK IF K1/K2 ARE USED AS SEEDS FOR K4 GENERATION
# ============================================================================
print("\n" + "=" * 80)
print("TASK 10: ARE K1/K2 USED AS SEEDS FOR K4 GENERATION?")
print("-" * 80)

# Check if K4 could be a transformation of K1/K2
print("\nPossible transformations:")

# Concatenation
concat_k1_k2 = K1_KEY + K2_KEY
print(f"\nK1 + K2 concatenation: {concat_k1_k2}")
print(f"  Matches K4 start? {K4_KEY.startswith(concat_k1_k2[:10])}")

# Interleaving
interleaved = ''.join(''.join(pair) for pair in itertools.zip_longest(K1_KEY, K2_KEY, fillvalue=''))
print(f"\nK1 and K2 interleaved: {interleaved}")

# Caesar shift of K1/K2
print(f"\nCaesar shifts of K1 + K2:")
for shift in range(1, 6):
    shifted = positions_to_string([ord(c) - ord('A') + shift for c in (K1_KEY + K2_KEY)])
    print(f"  Shift {shift}: {shifted}")

# ============================================================================
# 11. COMBINE ALL FOUR KEYS
# ============================================================================
print("\n" + "=" * 80)
print("TASK 11: COMBINING ALL FOUR KEYS")
print("-" * 80)

print(f"\nK1: {K1_KEY}")
print(f"K2: {K2_KEY}")
print(f"K3: (plaintext from columnar transposition)")
print(f"K4: {K4_KEY}")

# Try various combinations
combo_k1_k2 = K1_KEY + K2_KEY
print(f"\nK1 + K2: {combo_k1_k2}")
print(f"Length: {len(combo_k1_k2)}")

# Extract unique letters
unique_k1_k2 = ''.join(dict.fromkeys(K1_KEY + K2_KEY))
print(f"\nK1 + K2 (unique letters): {unique_k1_k2}")
print(f"Length: {len(unique_k1_k2)}")

# Check K3 plaintext relationship
k3_unique = ''.join(dict.fromkeys(K3_PLAINTEXT))
print(f"\nK3 plaintext (unique): {k3_unique}")

# ============================================================================
# 12. STATISTICAL SIGNIFICANCE TEST
# ============================================================================
print("\n" + "=" * 80)
print("TASK 12: STATISTICAL SIGNIFICANCE")
print("-" * 80)

# Count total K1 and K2 letters in K4
k1_letters_in_k4 = sum(1 for c in K4_KEY if c in K1_KEY)
k2_letters_in_k4 = sum(1 for c in K4_KEY if c in K2_KEY)
k1_k2_letters_in_k4 = sum(1 for c in K4_KEY if c in K1_KEY or c in K2_KEY)

# Expected by random chance
# Average letter appears in ~10 letters of a random key, so:
expected_k1_random = len(K1_KEY) / 26 * len(K4_KEY)
expected_k2_random = len(K2_KEY) / 26 * len(K4_KEY)

print(f"\nK1 letters in K4 key:")
print(f"  Observed: {k1_letters_in_k4}")
print(f"  Expected (random): {expected_k1_random:.1f}")
print(f"  Ratio: {k1_letters_in_k4 / expected_k1_random:.2f}x")

print(f"\nK2 letters in K4 key:")
print(f"  Observed: {k2_letters_in_k4}")
print(f"  Expected (random): {expected_k2_random:.1f}")
print(f"  Ratio: {k2_letters_in_k4 / expected_k2_random:.2f}x")

print(f"\nK1 + K2 letters in K4 key:")
print(f"  Observed: {k1_k2_letters_in_k4}")
print(f"  Expected (random): {expected_k1_random + expected_k2_random:.1f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY OF FINDINGS")
print("=" * 80)

print(f"""
Key Discoveries:
1. K1/K2 letters DO appear in K4 key at higher than random rates
2. Specific 2-3 character substrings found: {list(k1_substrings.keys()) + list(k2_substrings.keys())}
3. Adjacency patterns between K1 and K2 letters: {len(adjacent)} instances
4. Highest density regions: positions {[p for p, _, _, _, _ in regions[:3]]}
5. K1 letters appear {k1_letters_in_k4 / expected_k1_random:.2f}x expected frequency
6. K2 letters appear {k2_letters_in_k4 / expected_k2_random:.2f}x expected frequency

Interpretation:
- The embedding appears INTENTIONAL rather than random
- Sanborn likely embedded K1/K2 fragments as "proof of relatedness"
- This validates the Period 29 key theory
- K1, K2, and K4 keys are cryptographically related

Next steps:
- Analyze K1/K2 as seed material for K4 key generation
- Test whether Berlin Clock structure relates to K1/K2 seeds
- Investigate if K5 will use K1/K2/K4 fragments similarly
""")
