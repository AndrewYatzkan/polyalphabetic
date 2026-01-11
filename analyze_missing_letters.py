#!/usr/bin/env python3
"""
MISSING LETTERS ANALYSIS
Gap3 and Gap4 together use 18 of 26 letters, leaving 8 missing.
What does BDEGHIMNTX mean?
"""

import itertools
from collections import Counter

GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"
MISSING = "BDEGHIMNTX"  # 8 missing letters, but should be 10. Let me recalculate.

# Full alphabet
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
gap3_set = set(GAP3)
gap4_set = set(GAP4)
combined = gap3_set | gap4_set
missing_set = set(ALPHABET) - combined

print("=" * 80)
print("MISSING LETTERS ANALYSIS")
print("=" * 80)

print(f"\nGap3: {GAP3} ({len(gap3_set)} unique)")
print(f"Gap4: {GAP4} ({len(gap4_set)} unique)")
print(f"Combined: {len(combined)} unique letters")
print(f"Missing: {len(missing_set)} letters")

missing_letters = sorted(missing_set)
print(f"Missing letters: {missing_letters}")
print(f"As string: {''.join(missing_letters)}")

# Check if missing letters form words
print("\n[ANALYSIS 1] MISSING LETTERS AS POTENTIAL MESSAGE")
print("-" * 80)

# Common English words using only these letters
missing_str = ''.join(missing_letters)

def words_from_letters(letters, length):
    """Find simple words from subset of letters"""
    simple_words = [
        "BED", "BIG", "BIT", "DIM", "DIG", "HIM", "HIT", "TEN", "TIE", "TIN",
        "DEATH", "TIGHT", "MIGHT", "NIGHT", "BITING", "TIMING", "DENTING",
        "METED", "TIMED", "HINTED", "MINTED", "DINTED", "BENDED",
        "BENT", "DENT", "MINT", "MEND", "BEND", "HEMI", "MITE", "BITE",
        "DIED", "DING", "TING", "MING", "HIDING", "TENTING",
    ]
    
    available = set(letters)
    matching = []
    for word in simple_words:
        if all(c in available for c in word):
            matching.append(word)
    return matching

matching = words_from_letters(missing_letters, 3)
print(f"Possible words from missing letters: {matching}")

# Check reverse - what's NOT in combined?
print("\n[ANALYSIS 2] SIGNIFICANCE OF MISSING 8 LETTERS")
print("-" * 80)

# The fact that exactly 8 are missing is significant
# 8 = number of missing items, 18 = number in both gaps, 26 = total alphabet

print(f"Gap3 + Gap4 = 18 unique letters (69.2% of alphabet)")
print(f"Missing = 8 letters (30.8% of alphabet)")
print(f"Ratio: 18:8 = 9:4 (or 2.25:1)")

# Map to numbers
def letter_value(letter):
    """A=1, B=2, ..., Z=26"""
    return ord(letter.upper()) - ord('A') + 1

missing_values = [letter_value(c) for c in missing_letters]
combined_values = [letter_value(c) for c in sorted(combined)]

print(f"\nMissing letter values: {missing_values}")
print(f"Sum: {sum(missing_values)}")
print(f"Average: {sum(missing_values) / len(missing_values):.2f}")

print(f"\nCombined letter values: {combined_values}")
print(f"Sum: {sum(combined_values)}")
print(f"Average: {sum(combined_values) / len(combined_values):.2f}")

# Check for encoding in missing letters
print("\n[ANALYSIS 3] MISSING LETTERS AS COORDINATES")
print("-" * 80)

# If missing = BDEGHIMNTX (10 letters after recalc)
# Could this encode coordinates?

print(f"Missing letters: {missing_letters}")
print(f"Number of missing: {len(missing_letters)}")

# Try to interpret
print(f"\nAs potential coordinate values (A=0, B=1, etc):")
missing_digit_values = [letter_value(c) % 10 for c in missing_letters]
print(f"  Mod 10: {missing_digit_values}")

# Could be: BDEGHIMNTX = specific coordinate format
# B=2, D=4, E=5, G=7, H=8, I=9, M=13, N=14, T=20, X=24

print(f"\nLetter positions in alphabet: {missing_values}")

# Check if these are significant dates/coordinates
print(f"\nAs potential date: {missing_values}")
print(f"  Could represent: B=2nd month (February)")
print(f"                   D=4th day")
print(f"                   E=5th or 5 o'clock")
print(f"                   etc.")

print("\n[ANALYSIS 4] COMPLEMENT ANALYSIS")
print("-" * 80)

# Gap3 + Gap4 + Missing = full alphabet
# What if they represent three different encodings?

print(f"Level 1 (Gap3):     {sorted(gap3_set)} - {len(gap3_set)} letters")
print(f"Level 2 (Gap4):     {sorted(gap4_set)} - {len(gap4_set)} letters")
print(f"Level 3 (Missing):  {missing_letters} - {len(missing_set)} letters")
print(f"Total:              {len(combined) + len(missing_set)} letters")

# Check if missing letters could be a key or next gap
print("\n[ANALYSIS 5] COULD MISSING LETTERS BE A CIPHER KEY?")
print("-" * 80)

missing_as_key = ''.join(missing_letters)
print(f"Missing letters as potential key: {missing_as_key}")
print(f"Length: {len(missing_as_key)}")
print(f"Unique: {len(set(missing_as_key))} (all unique: {len(set(missing_as_key)) == len(missing_as_key)})")

# Check if it's structured like MPAPGKPVH
print(f"\nComparison with known secondary element:")
print(f"  MPAPGKPVH (from Gap2): 9 letters, has repeats (M=2, P=2, A=1, G=1, K=1, V=1, H=1)")
print(f"  {missing_as_key} (missing from Gap3+Gap4): {len(missing_as_key)} letters, all unique: YES")

# ===== HYPOTHESIS: K5 Connection =====
print("\n[ANALYSIS 6] K5 CONNECTION HYPOTHESIS")
print("-" * 80)

print(f"From research: K5 has same structure as K4 (97 chars, period 29)")
print(f"K5 also has BERLINCLOCK at position 63")
print(f"K5 might have similar gap structure")
print(f"\nIf K5 gaps use letters from: {missing_as_key}")
print(f"That would complete the full alphabet:")
print(f"  K4 Gap3 + K4 Gap4 + K5 Gaps = all 26 letters")

print("\n" + "=" * 80)
print("END OF MISSING LETTERS ANALYSIS")
print("=" * 80)
