#!/usr/bin/env python3
"""
Expanded gibberish analysis with more techniques:
- Multiple key combinations
- Frequency analysis
- Positional analysis
- Transposition tests
- Double encryption detection
"""

import string
from collections import Counter
import math

GIBBERISH = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

K4_FULL = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known K4 structure
K4_READABLE = [
    (0, 24, "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHAUEKCAR"),  # Full K4
    (63, 11, "BERLINCLOCK"),  # Position 63-73
    (76, 9, "NORTHEAST"),     # Position 76+
]

# Common keys from previous research
KEYS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW",
        "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTBJQHTMTKLLHALRPDEDRLSPLHSVYVJAJUJINITIALIZED",
        "COORDINATES", "WELTZEITUHR", "UNDERGROUND", "CRYPTOGRAPHY", "SECRETS"]

def analyze_frequency():
    """Analyze character frequency of gibberish"""
    print("\n" + "="*70)
    print("FREQUENCY ANALYSIS OF GIBBERISH")
    print("="*70)

    counts = Counter(GIBBERISH)
    total = len(GIBBERISH)

    print(f"Length: {len(GIBBERISH)}")
    print(f"Unique characters: {len(counts)}")
    print(f"\nFrequency distribution (%, expected for random: 3.85%):")

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for char, count in sorted_counts:
        freq = (count / total) * 100
        print(f"  {char}: {count:2d} ({freq:5.2f}%)")

    print(f"\nEnglish letter frequency (typical):")
    english = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    for i, c in enumerate(english[:10]):
        print(f"  {c}: ~{[12.70, 8.17, 7.51, 7.00, 6.70, 6.33, 6.09, 5.99, 5.92, 5.10][i]:.2f}%")

    print(f"\nIoC (Index of Coincidence) = {calculate_ioc(GIBBERISH):.4f}")
    print(f"English IoC ~ 0.067, Random ~ 0.038")

def calculate_ioc(text):
    """Calculate IoC"""
    counts = Counter(c for c in text.upper() if c.isalpha())
    n = sum(counts.values())
    if n <= 1:
        return 0
    ioc = sum(count * (count - 1) for count in counts.values()) / (n * (n - 1))
    return ioc

def analyze_structure():
    """Look for patterns/structure in gibberish"""
    print("\n" + "="*70)
    print("STRUCTURAL ANALYSIS")
    print("="*70)

    # Look for repeated substrings
    print("\nRepeated substrings (length >= 3):")
    for length in [3, 4, 5]:
        substrings = {}
        for i in range(len(GIBBERISH) - length + 1):
            sub = GIBBERISH[i:i+length]
            if sub not in substrings:
                substrings[sub] = []
            substrings[sub].append(i)

        repeats = {k: v for k, v in substrings.items() if len(v) > 1}
        if repeats:
            print(f"\n  Length {length}:")
            for sub, positions in sorted(repeats.items(), key=lambda x: len(x[1]), reverse=True):
                print(f"    {sub}: positions {positions}")

    # Look for palindromes
    print("\nPalindromes (length >= 3):")
    palindromes = []
    for length in [3, 4, 5, 6]:
        for i in range(len(GIBBERISH) - length + 1):
            sub = GIBBERISH[i:i+length]
            if sub == sub[::-1]:
                palindromes.append((i, sub))

    if palindromes:
        for pos, pal in palindromes:
            print(f"  Position {pos}: {pal}")
    else:
        print("  None found")

    # Bigram frequencies
    print("\nMost common bigrams:")
    bigrams = {}
    for i in range(len(GIBBERISH) - 1):
        bg = GIBBERISH[i:i+2]
        bigrams[bg] = bigrams.get(bg, 0) + 1

    for bg, count in sorted(bigrams.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {bg}: {count}")

def test_vigenere_variants():
    """Test various Vigenere variants with all keys"""
    print("\n" + "="*70)
    print("VIGENERE CIPHER - ALL KEYS")
    print("="*70)

    def vigenere_decrypt(ct, key):
        result = []
        key = key.upper()
        key_pos = 0
        for c in ct.upper():
            if c.isalpha():
                shift = ord(key[key_pos % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
                key_pos += 1
        return ''.join(result)

    for key in KEYS[:8]:  # First 8 keys
        result = vigenere_decrypt(GIBBERISH, key)
        ioc = calculate_ioc(result)
        # Count vowels and consonants
        vowels = sum(1 for c in result if c in 'AEIOU')
        consonants = sum(1 for c in result if c.isalpha() and c not in 'AEIOU')

        print(f"  {key:30s}: IoC={ioc:.4f}, V/C={vowels}/{consonants}, {result[:40]}")

def test_transposition():
    """Test various transposition methods"""
    print("\n" + "="*70)
    print("TRANSPOSITION ANALYSIS")
    print("="*70)

    # Try columnar transposition
    print("\nColumnar transposition (various column counts):")
    for cols in [5, 6, 7, 8, 9, 10, 11]:
        if len(GIBBERISH) % cols != 0:
            continue

        rows = len(GIBBERISH) // cols
        grid = []
        for i in range(rows):
            grid.append(GIBBERISH[i*cols:(i+1)*cols])

        # Try reading column by column
        result = ""
        for c in range(cols):
            for r in range(rows):
                result += grid[r][c]

        ioc = calculate_ioc(result)
        print(f"  {cols} cols: IoC={ioc:.4f}, {result[:40]}...")

    # Try rail fence
    print("\nRail Fence transposition (2-4 rails):")
    for rails in [2, 3, 4]:
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1

        for c in GIBBERISH:
            fence[rail].append(c)
            if rails > 1:
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1

        result = ''.join(''.join(f) for f in fence)
        ioc = calculate_ioc(result)
        print(f"  {rails} rails: IoC={ioc:.4f}, {result[:40]}...")

def test_keyword_positions():
    """Test if gibberish contains encrypted keywords at specific positions"""
    print("\n" + "="*70)
    print("KEYWORD POSITION ANALYSIS")
    print("="*70)

    keywords = ["COORDINATES", "LATITUDE", "LONGITUDE", "NORTH", "EAST", "DEGREE",
                "MINUTE", "SECOND", "38", "55", "06", "40", "26", "51"]

    print("\nSearching for keyword patterns...")

    # Look for letter pairs that could spell coordinates
    # Gibberish might encode coordinates in a specific pattern

    # Extract pairs
    pairs = [GIBBERISH[i:i+2] for i in range(0, len(GIBBERISH), 2)]
    print(f"Number of pairs: {len(pairs)}")
    print(f"Pairs: {' '.join(pairs)}")

    # Look for vowel patterns (coordinates often have specific patterns)
    vowel_pattern = ''.join(['V' if c in 'AEIOU' else 'C' for c in GIBBERISH])
    print(f"\nVowel pattern: {vowel_pattern}")

def test_combined_encryption():
    """Test if gibberish is result of double encryption"""
    print("\n" + "="*70)
    print("DOUBLE ENCRYPTION DETECTION")
    print("="*70)

    # Try decrypting with two keys in sequence
    def vigenere_decrypt(ct, key):
        result = []
        key = key.upper()
        key_pos = 0
        for c in ct.upper():
            if c.isalpha():
                shift = ord(key[key_pos % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
                key_pos += 1
        return ''.join(result)

    print("\nTrying double Vigenere (KRYPTOS + PALIMPSEST):")
    result = vigenere_decrypt(GIBBERISH, "KRYPTOS")
    result = vigenere_decrypt(result, "PALIMPSEST")
    ioc = calculate_ioc(result)
    print(f"  IoC={ioc:.4f}, {result[:50]}...")

    print("\nTrying double Vigenere (KRYPTOS + BERLIN):")
    result = vigenere_decrypt(GIBBERISH, "KRYPTOS")
    result = vigenere_decrypt(result, "BERLIN")
    ioc = calculate_ioc(result)
    print(f"  IoC={ioc:.4f}, {result[:50]}...")

    print("\nTrying double Vigenere (PALIMPSEST + ABSCISSA):")
    result = vigenere_decrypt(GIBBERISH, "PALIMPSEST")
    result = vigenere_decrypt(result, "ABSCISSA")
    ioc = calculate_ioc(result)
    print(f"  IoC={ioc:.4f}, {result[:50]}...")

def test_substitution_analysis():
    """Try to detect substitution cipher patterns"""
    print("\n" + "="*70)
    print("SUBSTITUTION ANALYSIS")
    print("="*70)

    print(f"\nGibberish digraphs vs English common digraphs:")
    gibberish_bigrams = {}
    for i in range(len(GIBBERISH) - 1):
        bg = GIBBERISH[i:i+2]
        gibberish_bigrams[bg] = gibberish_bigrams.get(bg, 0) + 1

    english_common = ["THE", "AND", "HER", "HAT", "HIS", "THA", "ERE", "FOR", "ENT", "ION"]

    print(f"Most common in gibberish: {sorted(gibberish_bigrams.items(), key=lambda x: x[1], reverse=True)[:5]}")
    print(f"Expected in English: {english_common[:5]}")

    # Calculate chi-squared for different shifts
    print(f"\nChi-squared test for Caesar shifts:")
    english_freq = {
        'A': 0.0817, 'B': 0.0149, 'C': 0.0278, 'D': 0.0425, 'E': 0.1270,
        'F': 0.0222, 'G': 0.0202, 'H': 0.0609, 'I': 0.0697, 'J': 0.0015,
        'K': 0.0077, 'L': 0.0403, 'M': 0.0241, 'N': 0.0675, 'O': 0.0751,
        'P': 0.0193, 'Q': 0.0010, 'R': 0.0599, 'S': 0.0633, 'T': 0.0906,
        'U': 0.0276, 'V': 0.0098, 'W': 0.0236, 'X': 0.0015, 'Y': 0.0197,
        'Z': 0.0007
    }

    def caesar_decrypt(ct, shift):
        result = []
        for c in ct.upper():
            if c.isalpha():
                result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
        return ''.join(result)

    def chi_squared(text):
        counts = Counter(text.upper())
        chi2 = 0
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            observed = counts.get(letter, 0) / len(text)
            expected = english_freq[letter]
            if expected > 0:
                chi2 += ((observed - expected) ** 2) / expected
        return chi2

    results = []
    for shift in range(26):
        decrypted = caesar_decrypt(GIBBERISH, shift)
        chi2 = chi_squared(decrypted)
        results.append((shift, chi2, decrypted))

    results.sort(key=lambda x: x[1])
    for shift, chi2, decrypted in results[:5]:
        print(f"  Shift {shift:2d}: Chi²={chi2:.4f}, {decrypted[:40]}...")

def main():
    print("EXPANDED GIBBERISH ANALYSIS")
    print(f"Gibberish: {GIBBERISH}")
    print(f"Length: {len(GIBBERISH)}")

    analyze_frequency()
    analyze_structure()
    test_vigenere_variants()
    test_transposition()
    test_keyword_positions()
    test_combined_encryption()
    test_substitution_analysis()

if __name__ == "__main__":
    main()
