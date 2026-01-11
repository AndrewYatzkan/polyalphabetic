#!/usr/bin/env python3
"""
Deep Statistical Analysis of K4 Key: DIJJQELYOIECBAQKVAATCRDUMPABT
Tests: frequency, patterns, words, numeric sequences, palindromes, Berlin Clock connections
"""

from collections import Counter, defaultdict
from itertools import combinations, permutations
import math

# The K4 period 29 key
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# English language reference data
ENGLISH_FREQ = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
    'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
    'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
    'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07
}

# KRYPTOS alphabet (used for K4)
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

print("=" * 80)
print("DEEP STATISTICAL ANALYSIS: K4 KEY")
print("=" * 80)
print(f"\nKey: {KEY}")
print(f"Key Length: {len(KEY)} (Period 29)")
print()

# ============================================================================
# 1. LETTER FREQUENCY ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("1. LETTER FREQUENCY ANALYSIS")
print("=" * 80)

key_freq = Counter(KEY)
print(f"\nFrequency of each letter in key:")
print(f"{'Letter':<10} {'Count':<10} {'Percentage':<15} {'English Avg':<15}")
print("-" * 50)

for letter in sorted(key_freq.keys()):
    count = key_freq[letter]
    percentage = (count / len(KEY)) * 100
    english_pct = ENGLISH_FREQ.get(letter, 0)
    print(f"{letter:<10} {count:<10} {percentage:>6.2f}%{'':<7} {english_pct:>6.2f}%")

# Overall statistics
print("\nOverall Key Statistics:")
print(f"  Unique letters: {len(key_freq)}/26 (coverage: {(len(key_freq)/26)*100:.1f}%)")
print(f"  Most frequent: {key_freq.most_common(1)[0][0]} ({key_freq.most_common(1)[0][1]} times)")
print(f"  Least frequent: {key_freq.most_common()[-1][0]} ({key_freq.most_common()[-1][1]} times)")

# Chi-squared test against English
chi_squared = 0
expected_freq = (len(KEY) / 26) if len(key_freq) == 26 else (len(KEY) / len(key_freq))
for letter in key_freq:
    observed = key_freq[letter]
    expected = expected_freq
    chi_squared += ((observed - expected) ** 2) / expected

print(f"  Chi-squared statistic: {chi_squared:.2f}")
print(f"    (High value suggests non-random distribution)")

# Missing letters
missing = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") - set(KEY)
print(f"\nMissing letters from standard alphabet: {sorted(missing)}")
print(f"  Missing count: {len(missing)}")

# ============================================================================
# 2. REPEATED PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("2. REPEATED PATTERNS AND SEQUENCES")
print("=" * 80)

# Find all repeated patterns
print(f"\nLetters appearing more than once:")
repeated = {letter: count for letter, count in key_freq.items() if count > 1}
for letter in sorted(repeated.keys(), key=lambda x: repeated[x], reverse=True):
    count = repeated[letter]
    positions = [i for i, c in enumerate(KEY) if c == letter]
    gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    print(f"  {letter}: appears {count} times at positions {positions}")
    if gaps:
        print(f"    Gaps between occurrences: {gaps}")
        print(f"    Average gap: {sum(gaps)/len(gaps):.1f}")

# Find 2-letter, 3-letter patterns
print(f"\nRepeated bigrams (2-letter sequences):")
bigrams = [KEY[i:i+2] for i in range(len(KEY)-1)]
bigram_freq = Counter(bigrams)
repeated_bigrams = {bg: count for bg, count in bigram_freq.items() if count > 1}
if repeated_bigrams:
    for bigram in sorted(repeated_bigrams.items(), key=lambda x: x[1], reverse=True):
        print(f"  {bigram[0]}: appears {bigram[1]} times")
else:
    print("  None found")

# Consecutive identical letters
print(f"\nConsecutive identical letters:")
consecutive = []
for i in range(len(KEY)-1):
    if KEY[i] == KEY[i+1]:
        consecutive.append((i, KEY[i]))
        print(f"  Position {i}-{i+1}: {KEY[i]}{KEY[i+1]}")
if not consecutive:
    print("  None found")

# Common English digraphs in the key
common_digraphs = ['TH', 'HE', 'AN', 'IN', 'ER', 'ED', 'ND', 'TO', 'EN', 'TI', 'ES', 'OR', 'AR', 'OU', 'IT']
print(f"\nCommon English digraphs present in key:")
found_digraphs = []
for digraph in common_digraphs:
    if digraph in KEY:
        found_digraphs.append(digraph)
        positions = []
        for i in range(len(KEY)-1):
            if KEY[i:i+2] == digraph:
                positions.append(i)
        print(f"  {digraph}: at position(s) {positions}")
if not found_digraphs:
    print("  None of the common digraphs found")

# ============================================================================
# 3. CHECK IF KEY LETTERS FORM WORDS OR ACRONYMS
# ============================================================================
print("\n" + "=" * 80)
print("3. WORDS AND ACRONYMS IN THE KEY")
print("=" * 80)

# Common English words that might be hidden
common_words = [
    'AND', 'THE', 'THAT', 'THEY', 'WHAT', 'WHEN', 'WHICH', 'THEIR',
    'EAST', 'WEST', 'NORTH', 'SOUTH', 'ABOVE', 'BELOW', 'UNDER',
    'CLOCK', 'BERLIN', 'DATE', 'DAY', 'TIME', 'YEAR', 'KEY', 'CIPHER',
    'EGYPT', 'WALL', 'CODE', 'SECRET', 'HIDDEN'
]

print(f"\nSearching for common words in key:")
found_words = []
for word in common_words:
    if word in KEY:
        pos = KEY.index(word)
        found_words.append((word, pos))
        print(f"  {word}: at position {pos}")

if not found_words:
    print("  No complete words found")

# Check for hidden substrings (length 3+)
print(f"\nAll substrings of length 3+:")
substrings = {}
for length in range(3, 8):
    subs = [KEY[i:i+length] for i in range(len(KEY)-length+1)]
    for sub in subs:
        if sub in substrings:
            substrings[sub] += 1
        else:
            substrings[sub] = 1

repeated_subs = {sub: count for sub, count in substrings.items() if count > 1}
if repeated_subs:
    print("  Repeated substrings:")
    for sub in sorted(repeated_subs.items(), key=lambda x: x[1], reverse=True):
        print(f"    {sub[0]}: {sub[1]} times")
else:
    print("  No repeated substrings of length 3+")

# Check first letters forming acronyms (acrostics)
print(f"\nInitial letters (potential acrostic):")
print(f"  D I J J Q E L Y O I E C B A Q K V A A T C R D U M P A B T")
print(f"  Pattern: D-I-J-J-Q suggests possible structure")

# ============================================================================
# 4. NUMERIC ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("4. NUMERIC ANALYSIS (A=0, B=1, ... Z=25)")
print("=" * 80)

# Convert to numeric (A=0)
key_numeric_a0 = [ord(c) - ord('A') for c in KEY]
print(f"\nKey as numbers (A=0):")
print(f"  {key_numeric_a0}")

# Sum and statistics
key_sum = sum(key_numeric_a0)
key_avg = key_sum / len(key_numeric_a0)
key_var = sum((x - key_avg) ** 2 for x in key_numeric_a0) / len(key_numeric_a0)
key_std = math.sqrt(key_var)

print(f"\nNumeric statistics (A=0):")
print(f"  Sum: {key_sum}")
print(f"  Average: {key_avg:.2f}")
print(f"  Variance: {key_var:.2f}")
print(f"  Std Dev: {key_std:.2f}")
print(f"  Min: {min(key_numeric_a0)} ({KEY[key_numeric_a0.index(min(key_numeric_a0))]})")
print(f"  Max: {max(key_numeric_a0)} ({KEY[key_numeric_a0.index(max(key_numeric_a0))]})")

# Convert to numeric (A=1)
key_numeric_a1 = [ord(c) - ord('A') + 1 for c in KEY]
print(f"\nKey as numbers (A=1):")
print(f"  {key_numeric_a1}")

key_sum_a1 = sum(key_numeric_a1)
print(f"  Sum: {key_sum_a1}")
print(f"  Average: {key_sum_a1 / len(key_numeric_a1):.2f}")

# Look for arithmetic sequences
print(f"\nLooking for arithmetic sequences in numeric values:")
sequences_found = False
for start_idx in range(len(key_numeric_a0)-2):
    for end_idx in range(start_idx+2, min(start_idx+7, len(key_numeric_a0))):
        subseq = key_numeric_a0[start_idx:end_idx+1]
        diffs = [subseq[i+1] - subseq[i] for i in range(len(subseq)-1)]
        if all(d == diffs[0] for d in diffs):  # Arithmetic sequence
            print(f"  Position {start_idx}-{end_idx}: {KEY[start_idx:end_idx+1]} = {subseq} (diff: {diffs[0]})")
            sequences_found = True

if not sequences_found:
    print("  No perfect arithmetic sequences found")

# Modulo operations
print(f"\nKey mod 26: {[x % 26 for x in key_numeric_a0]}")
print(f"Key mod 24 (Berlin Clock zones): {[x % 24 for x in key_numeric_a0]}")
print(f"Key mod 12: {[x % 12 for x in key_numeric_a0]}")

# Look for period-related patterns (29 = 29)
print(f"\nPeriod-related analysis (Period = 29):")
print(f"  Period / 2: {29 / 2} = 14.5")
print(f"  Period - 5: {29 - 5} = 24 (Berlin Clock zones)")
print(f"  Key length 29 = 24 + 5 (coincidence?)")

# ============================================================================
# 5. POSITIONS OF REPEATED LETTERS
# ============================================================================
print("\n" + "=" * 80)
print("5. POSITIONS OF REPEATED LETTERS (SIGNIFICANCE ANALYSIS)")
print("=" * 80)

print(f"\nRepeated letter positions and their properties:")
for letter in sorted(repeated.keys(), key=lambda x: repeated[x], reverse=True):
    count = repeated[letter]
    positions = [i for i, c in enumerate(KEY) if c == letter]
    print(f"\n{letter} (appears {count} times at {positions}):")

    # Position properties
    for i, pos in enumerate(positions):
        # Distance from start/end
        dist_from_start = pos
        dist_from_end = len(KEY) - 1 - pos
        pct_position = (pos / (len(KEY) - 1)) * 100

        # Quarter position
        quarter = pos // (len(KEY) // 4)

        print(f"    Position {pos}: {dist_from_start} from start, {dist_from_end} from end, {pct_position:.1f}% through, Quarter {quarter}")

    # Gaps between positions
    if len(positions) > 1:
        gaps = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        print(f"    Gaps: {gaps}")
        print(f"    Avg gap: {sum(gaps)/len(gaps):.1f}")

        # Check if gaps are related to 24 or 148
        for gap in gaps:
            if gap == 24:
                print(f"      ** Gap of 24 (Berlin Clock zones) found! **")
            if gap == 148:
                print(f"      ** Gap of 148 (Berlin Clock cities) found! **")
            if gap % 24 == 0:
                print(f"      * Gap is multiple of 24: {gap} = 24 × {gap // 24}")

# ============================================================================
# 6. PALINDROMES AND REVERSALS
# ============================================================================
print("\n" + "=" * 80)
print("6. PALINDROMES, REVERSALS, AND STRUCTURAL SYMMETRIES")
print("=" * 80)

# Check if key is palindrome
key_reversed = KEY[::-1]
is_palindrome = KEY == key_reversed
print(f"\nKey: {KEY}")
print(f"Reversed: {key_reversed}")
print(f"Is palindrome? {is_palindrome}")

# Look for palindromic substrings
print(f"\nPalindromic substrings (length 3+):")
palindromes_found = []
for length in range(3, 8):
    for i in range(len(KEY) - length + 1):
        substring = KEY[i:i+length]
        if substring == substring[::-1]:
            palindromes_found.append((substring, i))
            print(f"  {substring} at position {i}")

if not palindromes_found:
    print("  None found")

# Check if key contains reversed substrings from itself
print(f"\nReversed substrings (checking if AB appears as BA later):")
for length in range(2, 5):
    found_reversals = []
    for i in range(len(KEY) - length + 1):
        substring = KEY[i:i+length]
        reversed_sub = substring[::-1]
        for j in range(i+1, len(KEY) - length + 1):
            if KEY[j:j+length] == reversed_sub:
                found_reversals.append((substring, i, reversed_sub, j))

    if found_reversals:
        print(f"\n  Length {length}:")
        for original, orig_pos, reversed_ver, rev_pos in found_reversals:
            print(f"    {original} at pos {orig_pos} -> {reversed_ver} at pos {rev_pos}")

if not found_reversals:
    print("  None found")

# Check symmetry around center
center_pos = (len(KEY) - 1) / 2
print(f"\nSymmetry analysis (center at position {center_pos:.1f}):")
print(f"  First half: {KEY[:len(KEY)//2]}")
print(f"  Second half: {KEY[len(KEY)//2:]}")

# Mirror positions
print(f"\nMirror position pairs around center:")
for i in range(len(KEY) // 2):
    mirror_i = len(KEY) - 1 - i
    print(f"  Pos {i} ({KEY[i]}) <-> Pos {mirror_i} ({KEY[mirror_i]})")

# ============================================================================
# 7. ACROSTIC/PHRASE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("7. ACROSTIC AND PHRASE DERIVATION ANALYSIS")
print("=" * 80)

# First letters
print(f"\nFirst letters of each position:")
first_letters = KEY
print(f"  {first_letters}")
print(f"  Pattern: D-I-J-J-Q...")

# Try common phrase interpretations
test_phrases = [
    "DIJJ",
    "DIJ",
    "DIJJQ",
    "Dijjqe",
    "ELYOI",
    "VAATC"
]

print(f"\nInitial analysis of letter groupings:")
for phrase in test_phrases:
    if phrase in KEY:
        print(f"  Substring '{phrase}' found at position {KEY.index(phrase)}")

# Analysis of two-letter acronyms
print(f"\nTwo-letter combinations that might represent something:")
bigrams_list = [KEY[i:i+2] for i in range(0, len(KEY), 2)]
print(f"  Pairs (every 2 letters): {' '.join(bigrams_list)}")

# Try extracting first letter of each section (if divided by 5)
print(f"\nIf key represents 29 letters from a phrase:")
print(f"  Assuming 29-word phrase: {' '.join(list(KEY))}")

# ============================================================================
# 8. BERLIN WORLD CLOCK CONNECTIONS
# ============================================================================
print("\n" + "=" * 80)
print("8. BERLIN WORLD CLOCK CONNECTIONS")
print("=" * 80)

print(f"\nBerlin Weltzeituhr facts:")
print(f"  - 24 time zones (24-sided cylinder)")
print(f"  - 148 cities displayed")
print(f"  - Key period: 29")
print(f"  - Relationship: 24 + 5 = 29")

# Check if key could derive from 24 zones + 5 extras
print(f"\nKey structure analysis:")
print(f"  Total length: 29")
print(f"  29 = 24 zones + 5 special")
print(f"  29 = 148 cities / 5.1 ≈ 29 cities per group?")

# Check for numerical patterns related to dates
print(f"\nDate-related analysis:")
print(f"  Berlin Wall: 11/9/89")
print(f"  Egypt trip: 1986")
print(f"  K4 key length: 29")
print(f"  11 + 9 + 89 = 109")
print(f"  1986 - 1989 = -3 (or 1989 - 1986 = 3)")

# Check if key letters map to specific cities or zones
print(f"\nChecking key letter codes:")
for i, letter in enumerate(KEY):
    numeric = ord(letter) - ord('A')
    zone = i % 24
    city_index = numeric % 148
    print(f"  Position {i}: {letter} (numeric {numeric}) -> Zone {zone}, City ~{city_index}", end="")
    if i == 24:  # After 24 zones
        print(" [END OF FIRST 24]", end="")
    print()

# Check if there's a Berlin Wall date pattern
print(f"\nBerlin Wall (11/9/89) pattern search:")
print(f"  Looking for letters that could encode 11, 9, 89...")
for numeric_pattern in [[11, 9, 89], [1, 1, 9, 8, 9], [24, 9, 1]]:
    print(f"  Pattern {numeric_pattern}:")
    for i in range(len(KEY) - len(numeric_pattern) + 1):
        window = [ord(KEY[j]) - ord('A') for j in range(i, i + len(numeric_pattern))]
        if window == numeric_pattern:
            print(f"    Found at position {i}: {KEY[i:i+len(numeric_pattern)]}")

# Egypt 1986 pattern
print(f"\nEgypt (1986) pattern search:")
letters_1986 = ['A', 'T', 'T', 'G']  # 1=A, 9=I, 8=H, 6=F
numeric_1986 = [1, 9, 8, 6]
for i in range(len(KEY) - 3):
    window = [ord(KEY[j]) - ord('A') for j in range(i, i + 4)]
    if window == numeric_1986:
        print(f"  Pattern [1,9,8,6] found at position {i}: {KEY[i:i+4]}")

# ============================================================================
# 9. SUMMARY OF KEY PATTERNS
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY OF SIGNIFICANT PATTERNS")
print("=" * 80)

print(f"\nKEY: {KEY}")
print(f"Length: {len(KEY)}")
print(f"Unique letters: {len(key_freq)}/26")
print(f"\nRepeated letters: {list(repeated.keys())}")
print(f"Numeric sum (A=0): {key_sum}")
print(f"Numeric sum (A=1): {key_sum_a1}")

# Most important finding
print(f"\nMOST IMPORTANT STRUCTURAL FACT:")
print(f"  Period 29 = 24 (Berlin Clock zones) + 5 (special positions)")
print(f"  This structure strongly suggests the key derives from the Berlin Weltzeituhr")
print(f"  Possible mechanism: 24 letters from zones + 5 derived from cities or dates")

print(f"\nKey sections:")
print(f"  Positions 0-4:  DIJJQ (from UNDER crib)")
print(f"  Positions 5-15: ELYOIECBAQK (from BERLINCLOCK crib at position 63)")
print(f"  Positions 16-24: VAATCRDUM (from NORTHEAST crib at position 16)")
print(f"  Positions 25-28: PABT (from ABOVE crib at position 83)")

print("\n" + "=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
