#!/usr/bin/env python3
"""
Advanced analysis for K4 gibberish - test coordinate patterns and substitution.

The perfect uniformity in Gaps 3 & 4 suggests they might be:
1. Coordinate data encoded as letters
2. Location names
3. Substitution cipher output
"""

import re
from collections import Counter
import math

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Extract gaps
GAP1 = "QAPBZDBKZEL"      # 11 chars
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"  # 38 chars
GAP3 = "RSPVJWQUL"        # 9 chars
GAP4 = "ZOLRKCAYF"        # 9 chars

def frequency_analysis(text):
    """Analyze letter frequencies."""
    freq = Counter(text)
    total = len(text)
    return {char: count/total for char, count in freq.items()}

def chi_squared(text):
    """Calculate chi-squared against English."""
    english_freq = {
        'A': 0.082, 'B': 0.015, 'C': 0.028, 'D': 0.043, 'E': 0.127,
        'F': 0.022, 'G': 0.020, 'H': 0.061, 'I': 0.070, 'J': 0.002,
        'K': 0.008, 'L': 0.040, 'M': 0.024, 'N': 0.067, 'O': 0.075,
        'P': 0.019, 'Q': 0.001, 'R': 0.060, 'S': 0.063, 'T': 0.091,
        'U': 0.028, 'V': 0.010, 'W': 0.024, 'X': 0.002, 'Y': 0.020,
        'Z': 0.001
    }

    freq = frequency_analysis(text)
    chi_sq = 0
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(char, 0)
        expected = english_freq[char]
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected
    return chi_sq

def test_substitution_candidates(text, name):
    """Test if text could be substitution cipher with specific patterns."""
    print(f"\n{name}: {text}")

    freq = Counter(text)
    print(f"  Frequency: {dict(freq)}")

    # Check for perfect uniformity
    if len(set(freq.values())) == 1:
        print(f"  ⚠ PERFECT UNIFORMITY: All {len(set(text))} letters appear {list(freq.values())[0]} times!")

    # Check for null characters
    if len(set(text)) == len(text):
        print(f"  ⚠ ALL UNIQUE: Each letter appears exactly once (9 unique letters in {len(text)} chars)")

    # Test if could be coordinates
    # Latitude: 0-90, Longitude: 0-180 or -90 to 90
    # Could be encoded as letters where A=0, B=1, etc.

    print(f"  Letter-to-number mapping (A=0, B=1, ...):")
    num_seq = [ord(c) - ord('A') for c in text]
    print(f"    {num_seq}")

    # Try interpreting as lat/lon
    # 3 letters for degrees + decimals

    return freq

def test_keyword_cipher(ciphertext, keyword):
    """Try keyword substitution cipher."""
    # Build substitution table
    seen = set()
    substitution = ""

    for char in keyword:
        if char not in seen:
            substitution += char
            seen.add(char)

    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if char not in seen:
            substitution += char

    # Reverse mapping (ciphertext -> plaintext)
    decrypt_map = {}
    for i, cipher_char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        decrypt_map[cipher_char] = substitution[i]

    decrypted = "".join(decrypt_map.get(c, c) for c in ciphertext)
    return decrypted

def find_possible_words(text, min_length=3):
    """Find any English word substrings."""
    # Common 3-4 letter words
    common_words = [
        'AND', 'THE', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'CAN', 'HER',
        'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS',
        'LAT', 'LON', 'ALT', 'DEG', 'MIN', 'SEC', 'POS', 'BAT'
    ]

    found = []
    for word in common_words:
        if word in text:
            found.append(word)

    return found

def analyze_gaps_structure():
    """Analyze structure of the gaps."""
    print("\n" + "="*80)
    print("GAP STRUCTURE ANALYSIS")
    print("="*80)

    gaps = [
        ("Gap 1", GAP1),
        ("Gap 2", GAP2),
        ("Gap 3", GAP3),
        ("Gap 4", GAP4)
    ]

    for gap_name, gap_text in gaps:
        print(f"\n{gap_name} ({len(gap_text)} chars): {gap_text}")

        freq = test_substitution_candidates(gap_text, gap_name)

        # Check for common patterns
        words = find_possible_words(gap_text)
        if words:
            print(f"  ✓ Found words: {words}")

        # Check character distribution
        unique_chars = len(set(gap_text))
        print(f"  Unique characters: {unique_chars}/{len(gap_text)} ({100*unique_chars/len(gap_text):.1f}%)")

        # Chi-squared test
        chi_sq = chi_squared(gap_text)
        print(f"  Chi-squared vs English: {chi_sq:.2f}")

def test_coordinate_hypotheses():
    """Test if gaps encode coordinates."""
    print("\n" + "="*80)
    print("COORDINATE ENCODING HYPOTHESES")
    print("="*80)

    # Gap 3 and Gap 4 are 9 characters each
    # Could represent: LAT + LON + ALT or similar
    # 3 chars for latitude (0-90)
    # 3 chars for longitude (0-180)
    # 3 chars for altitude/other

    for gap_name, gap_text in [("Gap 3", GAP3), ("Gap 4", GAP4)]:
        print(f"\n{gap_name}: {gap_text}")

        # Try different splits
        for split in [(3, 3, 3), (4, 5), (2, 4, 3)]:
            parts = []
            start = 0
            for size in split:
                if start + size <= len(gap_text):
                    parts.append(gap_text[start:start+size])
                    start += size

            if len(parts) == len(split) and start == len(gap_text):
                print(f"  Split {split}: {' | '.join(parts)}")

                # Convert to numbers (A=0, B=1, etc.)
                nums = []
                for part in parts:
                    num = 0
                    for char in part:
                        num = num * 26 + (ord(char) - ord('A'))
                    nums.append(num)

                print(f"    As numbers: {nums}")

def test_transposition_patterns():
    """Test if could be transposition cipher."""
    print("\n" + "="*80)
    print("TRANSPOSITION PATTERN ANALYSIS")
    print("="*80)

    for gap_name, gap_text in [("Gap 3", GAP3), ("Gap 4", GAP4)]:
        print(f"\n{gap_name}: {gap_text}")

        # Try reversals
        reversed_text = gap_text[::-1]
        print(f"  Reversed: {reversed_text}")

        # Look for patterns
        pairs = []
        for i in range(0, len(gap_text), 2):
            if i+1 < len(gap_text):
                pairs.append((gap_text[i], gap_text[i+1]))

        print(f"  As pairs: {pairs}")

        # Try swapping
        swapped = ""
        for i in range(0, len(gap_text), 2):
            if i+1 < len(gap_text):
                swapped += gap_text[i+1] + gap_text[i]
            else:
                swapped += gap_text[i]

        print(f"  Pairs swapped: {swapped}")

def test_columnar_transposition():
    """Test columnar transposition."""
    print("\n" + "="*80)
    print("COLUMNAR TRANSPOSITION TEST")
    print("="*80)

    text = GAP2  # 38 characters
    print(f"Gap 2 ({len(text)} chars): {text}")

    # Try different column counts
    for cols in [2, 3, 4, 5, 6, 7, 19, 38]:
        if len(text) % cols == 0:
            rows = len(text) // cols
            print(f"\n  {rows} rows × {cols} cols:")

            # Arrange in grid
            grid = []
            for i in range(rows):
                row = text[i*cols:(i+1)*cols]
                grid.append(row)

            # Print grid
            for row in grid:
                print(f"    {' '.join(row)}")

            # Try reading by columns
            transposed = ""
            for col in range(cols):
                for row in range(rows):
                    transposed += grid[row][col]

            print(f"  Read by columns: {transposed}")

def test_keyword_substitution():
    """Test various keywords for substitution cipher."""
    print("\n" + "="*80)
    print("KEYWORD SUBSTITUTION TESTS")
    print("="*80)

    keywords = [
        "PALIMPSEST",
        "ABSCISSA",
        "KRYPTOS",
        "SANBORN",
        "BERLIN",
        "CLOCK",
        "UNDERGROUND",
        "COORDINATES",
        "POSITION",
        "COMPASS",
        "BEARING"
    ]

    gap = GAP3  # Use Gap 3 which is smaller
    print(f"\nTesting on Gap 3: {gap}")

    for keyword in keywords:
        decrypted = test_keyword_cipher(gap, keyword)

        # Check for vowel content
        vowels = sum(1 for c in decrypted if c in 'AEIOU')
        vowel_ratio = vowels / len(decrypted) if decrypted else 0

        # Check for English patterns
        words = find_possible_words(decrypted)

        print(f"  {keyword:15s} -> {decrypted:15s} (vowels: {vowel_ratio:.1%})", end="")
        if words or vowel_ratio > 0.4:
            print(" ⚠")
        else:
            print()

# ============================================================================
# RUN ALL ANALYSES
# ============================================================================

analyze_gaps_structure()
test_coordinate_hypotheses()
test_transposition_patterns()
test_columnar_transposition()
test_keyword_substitution()

print("\n" + "="*80)
print("ADVANCED ANALYSIS COMPLETE")
print("="*80)
print("\nKey findings:")
print("- Gap 3 & 4: Perfect uniformity (9 unique letters, 9 chars each)")
print("- Gap 2: 38 characters (longer plaintext or complex structure)")
print("- Gap 1: 11 characters (prefix/key candidate?)")
print("\nNext steps:")
print("- Test if perfect uniformity in Gaps 3&4 indicates coordinate encoding")
print("- Try frequency matching against known geographic data")
print("- Test columnar transposition decryption")
print("- Analyze relationship between readable words and gibberish")
