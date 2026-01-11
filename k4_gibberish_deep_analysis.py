#!/usr/bin/env python3
"""
Deep analysis of K4 gibberish sections
Plaintext with Period 29 key: DIJJQELYOIECBAQKVAATCRDUMPABT
"""

from collections import Counter
import re

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Gibberish sections with their positions
gibberish_sections = {
    "Section 1": {
        "text": "QAPBZDBKZEL",
        "positions": (5, 15),
        "length": 11
    },
    "Section 2": {
        "text": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",
        "positions": (25, 62),
        "length": 38
    },
    "Section 3": {
        "text": "RSPVJWQUL",
        "positions": (74, 82),
        "length": 9
    },
    "Section 4": {
        "text": "ZOLRKCAYF",
        "positions": (88, 96),
        "length": 9
    }
}

# English letter frequency (%)
english_freq = {
    'E': 12.70, 'T': 9.06, 'A': 8.17, 'O': 7.51, 'I': 6.97, 'N': 6.75,
    'S': 6.33, 'H': 6.09, 'R': 5.99, 'D': 4.25, 'L': 4.03, 'C': 2.78,
    'U': 2.76, 'M': 2.41, 'W': 2.36, 'F': 2.23, 'G': 2.02, 'Y': 1.97,
    'P': 1.93, 'B': 1.29, 'V': 0.98, 'K': 0.77, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07
}

# Readable sections (for comparison)
readable_sections = {
    "UNDER": (0, 4),
    "NORTHEAST": (16, 24),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73),
    "ABOVE": (83, 86)
}

print("=" * 80)
print("K4 GIBBERISH SECTIONS DEEP ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. LETTER FREQUENCY ANALYSIS
# ============================================================================
print("\n1. LETTER FREQUENCY ANALYSIS")
print("-" * 80)

for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]
    freq = Counter(text)

    print(f"\n{section_name}: {text}")
    print(f"Length: {section_data['length']} characters")

    print("\nLetter frequencies:")
    sorted_freq = sorted(freq.items(), key=lambda x: -x[1])

    freq_analysis = []
    for letter, count in sorted_freq:
        pct = (count / len(text)) * 100
        english_pct = english_freq.get(letter, 0)
        deviation = pct - english_pct
        freq_analysis.append((letter, count, pct, english_pct, deviation))
        print(f"  {letter}: {count:2d} ({pct:5.1f}%) [English: {english_pct:5.1f}%] Deviation: {deviation:+6.1f}%")

    # Chi-squared test
    chi_squared = sum(((count - (len(text) * english_freq.get(letter, 0) / 100)) ** 2)
                      / (len(text) * english_freq.get(letter, 0) / 100 + 0.001)
                      for letter, count in freq.items())
    print(f"\nChi-squared statistic: {chi_squared:.2f} (lower = more English-like)")

# ============================================================================
# 2. REPEATED PATTERNS
# ============================================================================
print("\n\n2. REPEATED PATTERNS/DIGRAPHS/TRIGRAPHS")
print("-" * 80)

for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]

    print(f"\n{section_name}: {text}")

    # Digraphs
    digraphs = Counter()
    for i in range(len(text) - 1):
        digraphs[text[i:i+2]] += 1

    print("\nTop digraphs:")
    for digraph, count in digraphs.most_common(10):
        if count > 1:
            print(f"  {digraph}: {count} times")

    # Trigraphs
    trigraphs = Counter()
    for i in range(len(text) - 2):
        trigraphs[text[i:i+3]] += 1

    print("\nTrigraphs (if any repeat):")
    for trigraph, count in trigraphs.most_common(10):
        if count > 1:
            print(f"  {trigraph}: {count} times")

    # Look for repeated single letters
    print("\nRepeated letters:")
    repeated = {letter: count for letter, count in freq.items() if count > 2}
    for letter in sorted(repeated.keys()):
        positions = [i for i, ch in enumerate(text) if ch == letter]
        print(f"  {letter}: appears {repeated[letter]} times at positions {positions}")

# ============================================================================
# 3. CHECK IF SECTIONS ARE RELATED (SAME LETTERS REARRANGED)
# ============================================================================
print("\n\n3. CHECKING IF SECTIONS ARE RELATED")
print("-" * 80)

all_texts = {name: data["text"] for name, data in gibberish_sections.items()}

# Compare all pairs
for i, (name1, text1) in enumerate(all_texts.items()):
    for name2, text2 in list(all_texts.items())[i+1:]:
        freq1 = Counter(text1)
        freq2 = Counter(text2)

        # Find common letters
        common = set(freq1.keys()) & set(freq2.keys())
        unique1 = set(freq1.keys()) - set(freq2.keys())
        unique2 = set(freq2.keys()) - set(freq1.keys())

        print(f"\n{name1} vs {name2}:")
        print(f"  Common letters: {sorted(common)} ({len(common)} letters)")
        print(f"  Unique to {name1}: {sorted(unique1)}")
        print(f"  Unique to {name2}: {sorted(unique2)}")

        # Check if one is an anagram of the other
        if sorted(text1) == sorted(text2):
            print(f"  >>> ANAGRAM! Exact letter rearrangement!")

        # Check overlap percentage
        overlap = sum(min(freq1[l], freq2[l]) for l in common)
        max_len = max(len(text1), len(text2))
        overlap_pct = (overlap / max_len) * 100
        print(f"  Letter overlap: {overlap}/{max_len} = {overlap_pct:.1f}%")

# ============================================================================
# 4. BACKWARDS READING
# ============================================================================
print("\n\n4. READING SECTIONS BACKWARDS")
print("-" * 80)

for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]
    reversed_text = text[::-1]

    print(f"\n{section_name}:")
    print(f"  Forward:  {text}")
    print(f"  Backward: {reversed_text}")

    # Check if reversed version contains any English words
    # Look for common patterns
    if "THE" in reversed_text or "AND" in reversed_text or "FOR" in reversed_text:
        print(f"  >>> Contains English words when reversed!")

# ============================================================================
# 5. ACROSTIC PATTERNS
# ============================================================================
print("\n\n5. ACROSTIC PATTERNS (First letters)")
print("-" * 80)

print(f"\nFirst letters of all gibberish sections:")
first_letters = "".join(section["text"][0] for section in gibberish_sections.values())
print(f"  {first_letters}")
print(f"  Reversed: {first_letters[::-1]}")

print(f"\nLast letters of all gibberish sections:")
last_letters = "".join(section["text"][-1] for section in gibberish_sections.values())
print(f"  {last_letters}")
print(f"  Reversed: {last_letters[::-1]}")

# ============================================================================
# 6. CONTEXT ANALYSIS - LOOK FOR WORD FRAGMENTS
# ============================================================================
print("\n\n6. CONTEXT ANALYSIS - LOOKING FOR WORD FRAGMENTS")
print("-" * 80)

# Check what comes before and after each section
for section_name, section_data in gibberish_sections.items():
    start, end = section_data["positions"]
    text = section_data["text"]

    # Get context (5 chars before and after if available)
    before = plaintext[max(0, start-5):start] if start >= 0 else ""
    after = plaintext[end+1:min(len(plaintext), end+6)] if end < len(plaintext)-1 else ""

    print(f"\n{section_name} ({start}-{end}):")
    print(f"  Before (5 chars): {before}")
    print(f"  Section:          {text}")
    print(f"  After (5 chars):  {after}")

    # Check if section starts with common letter combinations
    first_few = text[:3]
    last_few = text[-3:]

    print(f"  First 3 letters: {first_few}")
    print(f"  Last 3 letters:  {last_few}")

    # Look for potential word boundaries
    if text[0] in 'AEIOU':
        print(f"    -> Starts with vowel (could be continuation of previous word or new word)")
    else:
        print(f"    -> Starts with consonant (likely new word or continuation)")

# ============================================================================
# 7. STATISTICAL ANALYSIS
# ============================================================================
print("\n\n7. STATISTICAL ANALYSIS")
print("-" * 80)

print("\nVowel vs Consonant analysis:")
vowels = set('AEIOU')

for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]
    vowel_count = sum(1 for c in text if c in vowels)
    consonant_count = len(text) - vowel_count
    vowel_pct = (vowel_count / len(text)) * 100
    consonant_pct = (consonant_count / len(text)) * 100

    print(f"\n{section_name}:")
    print(f"  Vowels: {vowel_count}/{len(text)} ({vowel_pct:.1f}%)")
    print(f"  Consonants: {consonant_count}/{len(text)} ({consonant_pct:.1f}%)")
    print(f"  [English average: ~38% vowels, ~62% consonants]")

# ============================================================================
# 8. COMPARING WITH READABLE SECTIONS
# ============================================================================
print("\n\n8. COMPARISON WITH READABLE SECTIONS")
print("-" * 80)

readable_texts = {}
for word, (start, end) in readable_sections.items():
    readable_texts[word] = plaintext[start:end+1]

all_readable = "".join(readable_texts.values())
freq_readable = Counter(all_readable)

print(f"\nReadable sections combined: {all_readable}")
print(f"Length: {len(all_readable)}")

print("\nLetter frequency in readable sections:")
for letter, count in sorted(freq_readable.items(), key=lambda x: -x[1]):
    pct = (count / len(all_readable)) * 100
    print(f"  {letter}: {count:2d} ({pct:5.1f}%)")

print("\nComparing to gibberish sections...")
all_gibberish = "".join(section["text"] for section in gibberish_sections.values())
freq_gibberish = Counter(all_gibberish)

print(f"\nGibberish sections combined: {len(all_gibberish)} characters")
print(f"Gibberish unique letters: {len(freq_gibberish)}")
print(f"Readable unique letters: {len(freq_readable)}")

# Letters only in gibberish
only_in_gibberish = set(freq_gibberish.keys()) - set(freq_readable.keys())
only_in_readable = set(freq_readable.keys()) - set(freq_gibberish.keys())

print(f"\nLetters only in gibberish: {sorted(only_in_gibberish)}")
print(f"Letters only in readable: {sorted(only_in_readable)}")

# ============================================================================
# 9. LOOKING FOR HIDDEN PATTERNS
# ============================================================================
print("\n\n9. LOOKING FOR HIDDEN PATTERNS")
print("-" * 80)

# Check for repeated letter patterns within sections
for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]

    print(f"\n{section_name}: {text}")

    # Look for doubled letters
    doubled = []
    for i in range(len(text) - 1):
        if text[i] == text[i+1]:
            doubled.append((i, text[i]))

    if doubled:
        print(f"  Doubled letters: {doubled}")
    else:
        print(f"  No doubled letters")

    # Look for pattern: same letter appears X positions apart
    for distance in [2, 3, 4, 5]:
        patterns = []
        for i in range(len(text) - distance):
            if text[i] == text[i + distance]:
                patterns.append((i, distance, text[i]))

        if patterns:
            print(f"  Letters separated by {distance} positions: {patterns[:5]}")

# ============================================================================
# 10. ENTROPY AND RANDOMNESS
# ============================================================================
print("\n\n10. ENTROPY AND RANDOMNESS MEASURE")
print("-" * 80)

import math

def calculate_entropy(text):
    """Calculate Shannon entropy of text"""
    freq = Counter(text)
    entropy = 0
    for count in freq.values():
        p = count / len(text)
        entropy -= p * math.log2(p)
    return entropy

print("\nShannon Entropy (higher = more random):")
for section_name, section_data in gibberish_sections.items():
    text = section_data["text"]
    entropy = calculate_entropy(text)
    max_entropy = math.log2(26)  # Maximum entropy for 26 letters
    normalized = entropy / max_entropy * 100
    print(f"  {section_name}: {entropy:.3f} ({normalized:.1f}% of max)")

# Entropy of readable sections
entropy_readable = calculate_entropy(all_readable)
print(f"\n  All readable: {entropy_readable:.3f}")

entropy_gibberish = calculate_entropy(all_gibberish)
print(f"  All gibberish: {entropy_gibberish:.3f}")

print("\nNote: English text has entropy ~4.7 bits")
print("      Random text has entropy ~4.7 bits (for uniform distribution)")
print("      This section should show if gibberish is more random than English")

print("\n" + "=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
