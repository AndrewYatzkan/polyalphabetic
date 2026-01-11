#!/usr/bin/env python3
"""
Try to reconstruct the complete sentence/message from K4
"""

from collections import Counter
import re

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("="*80)
print("K4 SENTENCE RECONSTRUCTION ANALYSIS")
print("="*80)

# The known structure
structure = {
    "UNDER": (0, 5),
    "QAPBZDBKZEL": (5, 16),
    "NORTHEAST": (16, 25),
    "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH": (25, 63),
    "BERLINCLOCK": (63, 74),
    "RSPVJWQUL": (74, 83),
    "ABOVE": (83, 88),
    "ZOLRKCAYF": (88, 97)
}

print("\nFull plaintext structure:")
print(plaintext)
print()
for i, c in enumerate(plaintext):
    if i % 10 == 0:
        print(f"{i:2d}", end=" ")
    else:
        print("  ", end="")
print()
for i, c in enumerate(plaintext):
    print(f" {c}", end="")
print()

# The gibberish sections might encode the missing words
gibberish = {
    "between_UNDER_and_NORTHEAST": "QAPBZDBKZEL",
    "between_NORTHEAST_and_BERLINCLOCK": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",
    "between_BERLINCLOCK_and_ABOVE": "RSPVJWQUL",
    "after_ABOVE": "ZOLRKCAYF"
}

print("\n" + "="*80)
print("RECONSTRUCTING THE SENTENCE")
print("="*80)

print("\nThe template appears to be:")
print("  UNDER [WORD1] NORTHEAST [WORD2] BERLINCLOCK [WORD3] ABOVE [WORD4]")

# Key insight: each gibberish section might be an anagram of the missing word
print("\n" + "="*80)
print("ANAGRAM-BASED WORD RECOVERY")
print("="*80)

word_lists = {
    "between_UNDER_and_NORTHEAST": ["THE", "GROUND", "SURFACE", "SHADOW"],
    "between_NORTHEAST_and_BERLINCLOCK": ["PASSAGE", "WALL", "MARKS", "POINT"],
    "between_BERLINCLOCK_and_ABOVE": ["LIES", "SHOWS", "HIDES", "MARKS"],
    "after_ABOVE": ["GROUND", "SURFACE", "STONE", "ALL"]
}

def find_anagram(text, candidates):
    """Find which candidate is an anagram of text"""
    text_sorted = ''.join(sorted(text))
    for word in candidates:
        word_sorted = ''.join(sorted(word))
        if text_sorted == word_sorted:
            return word
    return None

print("\nTrying to match gibberish sections to candidate words:")
for section_name, section_text in gibberish.items():
    candidates = []
    # Check common single words
    common = ["THE", "GROUND", "SURFACE", "SHADOW", "PASSAGE", "WALL", "MARKS",
              "POINT", "LIES", "SHOWS", "HIDES", "STONE", "ALL", "BENEATH",
              "WITHIN", "ABOVE", "UNDER", "OVER", "SOUTH", "NORTH", "EAST", "WEST"]

    for word in common:
        if len(word) == len(section_text):
            word_sorted = ''.join(sorted(word))
            section_sorted = ''.join(sorted(section_text))
            if word_sorted == section_sorted:
                candidates.append(word)

    print(f"\n{section_name}: {section_text}")
    print(f"  Length: {len(section_text)}")
    if candidates:
        print(f"  Possible anagrams: {candidates}")
    else:
        print(f"  No perfect anagrams found")

# Try different sentence completions
print("\n" + "="*80)
print("CONTEXTUAL SENTENCE COMPLETION")
print("="*80)

sentences = [
    "UNDER THE NORTHEAST PASSAGE BERLINCLOCK LIES ABOVE STONE",
    "UNDER GROUND NORTHEAST WALL BERLINCLOCK SHOWS ABOVE SURFACE",
    "UNDER SURFACE NORTHEAST MARKS BERLINCLOCK HIDES ABOVE GROUND",
    "UNDER SHADOW NORTHEAST PASSAGE BERLINCLOCK MARKS ABOVE GROUND",
    "UNDER STONE NORTHEAST WALL BERLINCLOCK SHOWS ABOVE ALL"
]

print("\nPlausible sentence completions:")
for sentence in sentences:
    print(f"  {sentence}")

# Look at letter patterns in the middle gibberish section
print("\n" + "="*80)
print("ANALYZING THE LARGE GIBBERISH SECTION")
print("="*80)

large_gibberish = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
print(f"\nLarge section: {large_gibberish} ({len(large_gibberish)} letters)")
print(f"Letters available: {sorted(Counter(large_gibberish).items())}")

# This section is 38 letters - too long for a single word
# Maybe it contains multiple words?
print("\nPossible multi-word combinations from this 38-letter section:")

three_word_options = [
    ("PASSAGE", "WALL", "MARKS"),  # 7 + 4 + 5 = 16 letters, but we need 38
    ("NORTHEASTERN", "WALL", "MARKS"),  # too many letters
]

# Check if key words can be formed
key_words = ["PASSAGE", "WALL", "MARKS", "STONE", "SHADOW", "BENEATH", "WITHIN"]
letters_available = Counter(large_gibberish)

print("\nCan form from large section:")
for word in key_words:
    word_counter = Counter(word)
    can_form = all(letters_available[c] >= word_counter[c] for c in word_counter)
    if can_form:
        print(f"  YES: {word}")
        # Show remaining letters after forming this word
        remaining = letters_available.copy()
        for c in word:
            remaining[c] -= 1
        print(f"       Remaining: {dict(remaining)}")

# Try ROT-N decoding of specific sections
print("\n" + "="*80)
print("ROT-N ANALYSIS OF GIBBERISH SECTIONS")
print("="*80)

def rot_n(text, n):
    return ''.join(chr((ord(c) - ord('A') + n) % 26 + ord('A')) for c in text)

print("\nTrying different ROT values for 'QAPBZDBKZEL' (should be a short word):")
for n in range(1, 26):
    rotated = rot_n("QAPBZDBKZEL", n)
    # Check if it contains common English letter patterns
    has_vowel = any(c in rotated for c in 'AEIOU')
    if has_vowel:
        print(f"  ROT-{n:2d}: {rotated}")

print("\nTrying different ROT values for 'RSPVJWQUL' (should be a short word):")
for n in range(1, 26):
    rotated = rot_n("RSPVJWQUL", n)
    has_vowel = any(c in rotated for c in 'AEIOU')
    if has_vowel:
        print(f"  ROT-{n:2d}: {rotated}")

# Check positional cipher - maybe gibberish = plaintext shifted
print("\n" + "="*80)
print("TRYING VIGENERE-LIKE DECODING")
print("="*80)

print("\nIf gibberish is encrypted with a repeating key:")
print("Each gibberish section might use a different key\n")

# Try to find repeating patterns
for section_name, section_text in gibberish.items():
    print(f"{section_name}:")
    # Check if any letter appears with regular spacing
    for letter in set(section_text):
        positions = [i for i, c in enumerate(section_text) if c == letter]
        if len(positions) > 1:
            spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            if len(set(spacings)) == 1:  # Regular spacing
                print(f"  {letter} appears at regular intervals: {spacings[0]}")
