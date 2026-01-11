#!/usr/bin/env python3
"""
Comprehensive hidden structure analysis for K4 plaintext
"""

import re
from collections import Counter
from itertools import permutations
import math

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("="*80)
print("K4 PLAINTEXT STRUCTURE ANALYSIS")
print("="*80)
print(f"\nFull plaintext ({len(plaintext)} letters):")
print(plaintext)

# First, let's clearly parse the known words
print("\n" + "="*80)
print("1. PARSING KNOWN WORDS AND GIBBERISH")
print("="*80)

known_words = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]

# Find positions of known words
positions = {}
for word in known_words:
    idx = plaintext.find(word)
    if idx != -1:
        positions[word] = (idx, idx + len(word))
        print(f"{word:20} at positions {idx:3}-{idx+len(word)-1:3}")

# Extract gibberish sections
print("\nGibberish sections:")
current_pos = 0
sections = []
for word in sorted(positions.keys(), key=lambda w: positions[w][0]):
    start, end = positions[word]
    if current_pos < start:
        gibberish = plaintext[current_pos:start]
        sections.append(("GIBBERISH", gibberish, current_pos))
        print(f"  Positions {current_pos:3}-{start-1:3}: {gibberish}")
    sections.append((word, plaintext[start:end], start))
    current_pos = end

if current_pos < len(plaintext):
    gibberish = plaintext[current_pos:]
    sections.append(("GIBBERISH", gibberish, current_pos))
    print(f"  Positions {current_pos:3}-{len(plaintext)-1:3}: {gibberish}")

# List all gibberish sections with analysis
print("\nDetailed gibberish analysis:")
for name, section, pos in sections:
    if name == "GIBBERISH":
        print(f"\n  Section at {pos:3}-{pos+len(section)-1:3} ({len(section)} letters): {section}")
        # Check for patterns
        chars = Counter(section)
        print(f"    Character frequencies: {dict(sorted(chars.items()))}")
        print(f"    Most common: {chars.most_common(3)}")

# Now let's check for the complete sentence pattern
print("\n" + "="*80)
print("2. SENTENCE COMPLETION ANALYSIS")
print("="*80)
print("\nThe pattern suggests: UNDER [?] NORTHEAST [?] BERLINCLOCK [?] ABOVE [?]")
print("\nLooking at extracted gibberish sections to complete sentences:")

# Get gibberish between known words
gibberish_segments = {}
prev_end = 0
sorted_words = sorted(positions.keys(), key=lambda w: positions[w][0])

for word in sorted_words:
    start, end = positions[word]
    if prev_end < start:
        gibberish = plaintext[prev_end:start]
        gibberish_segments[f"before_{word}"] = gibberish
    prev_end = end

last_word = sorted_words[-1]
after_last = plaintext[positions[last_word][1]:]
if after_last:
    gibberish_segments[f"after_{last_word}"] = after_last

for key, value in gibberish_segments.items():
    print(f"  {key:25} : {value}")

# Extract every Nth letter
print("\n" + "="*80)
print("3. EVERY NTH LETTER EXTRACTION")
print("="*80)

for n in [2, 3, 4, 5, 7, 11]:
    extracted = plaintext[::n]
    print(f"\nEvery {n}th letter ({len(extracted)} letters):")
    print(f"  {extracted}")

    # Check for common words in extracted text
    words_found = []
    for length in range(3, 8):
        for i in range(len(extracted) - length + 1):
            substring = extracted[i:i+length]
            if substring in ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "WHO", "OIL", "MEN", "SEE"]:
                words_found.append((i, substring))
    if words_found:
        print(f"  Possible words found: {words_found}")

# Position-based extraction
print("\n" + "="*80)
print("4. SPECIFIC POSITION EXTRACTION")
print("="*80)

# Extract letters at positions matching a pattern
print("\nLetters at odd positions:")
odd_positions = plaintext[1::2]
print(f"  {odd_positions}")

print("\nLetters at even positions:")
even_positions = plaintext[::2]
print(f"  {even_positions}")

# Check for coordinates (numbers encoded as letters)
print("\n" + "="*80)
print("5. POTENTIAL COORDINATES (A=1, B=2, etc.)")
print("="*80)

def letter_to_num(letter):
    return ord(letter) - ord('A') + 1

# Try extracting from gibberish sections
for name, section, pos in sections:
    if name == "GIBBERISH" and len(section) >= 4:
        # Try to interpret as coordinates
        nums = [letter_to_num(c) for c in section[:6]]
        print(f"\n{section[:6]}: {nums} (if A=1, B=2, ...)")

# Check for anagrams of common words in gibberish
print("\n" + "="*80)
print("6. ANAGRAM ANALYSIS")
print("="*80)

common_words = ["TREASURE", "GROUND", "SHADOW", "SURFACE", "WALL", "STONE",
                "LOCATION", "BENEATH", "WITHIN", "HIDDEN", "SECRET", "VAULT",
                "CHAMBER", "PASSAGE", "TUNNEL", "ENTRY", "EXIT", "KEY"]

def can_form(available, target):
    """Check if target can be formed from available letters"""
    available_counter = Counter(available)
    target_counter = Counter(target)
    for char, count in target_counter.items():
        if available_counter[char] < count:
            return False
    return True

print("\nChecking which common words can be formed from gibberish sections:")
for name, section, pos in sections:
    if name == "GIBBERISH":
        possible = []
        for word in common_words:
            if can_form(section, word):
                possible.append(word)
        if possible:
            print(f"\n  {section} ({len(section)} letters):")
            print(f"    Can form: {possible}")

# Analyze letter distribution
print("\n" + "="*80)
print("7. LETTER FREQUENCY ANALYSIS")
print("="*80)

char_freq = Counter(plaintext)
print("\nFull plaintext letter frequencies:")
for char, count in char_freq.most_common():
    print(f"  {char}: {count:2d} ({count/len(plaintext)*100:5.1f}%)")

# Check for repeating patterns
print("\n" + "="*80)
print("8. REPEATING PATTERNS")
print("="*80)

print("\nLooking for repeated substrings (3+ letters):")
repeating = {}
for length in range(3, 8):
    for i in range(len(plaintext) - length + 1):
        substring = plaintext[i:i+length]
        if substring not in repeating:
            repeating[substring] = []
        repeating[substring].append(i)

repeated_items = {k: v for k, v in repeating.items() if len(v) > 1}
for substring, positions_list in sorted(repeated_items.items(), key=lambda x: -len(x[1])):
    print(f"  '{substring}' appears {len(positions_list)} times at positions: {positions_list}")

# Try to find sentence structure
print("\n" + "="*80)
print("9. SENTENCE COMPLETION SUGGESTIONS")
print("="*80)

print("\nThematic words to try filling in:")
candidates = {
    "UNDER": ["THE", "GROUND", "SHADOW", "SURFACE", "WATER"],
    "NORTHEAST": ["PASSAGE", "WALL", "CORNER", "EDGE", "MARKS"],
    "BERLINCLOCK": ["LIES", "MARKS", "SHOWS", "POINTS", "HIDES"],
    "ABOVE": ["GROUND", "ALL", "THIS", "PASSAGE", "THE"]
}

print("Pattern: UNDER [word1] NORTHEAST [word2] BERLINCLOCK [word3] ABOVE [word4]")
for position, words in candidates.items():
    print(f"  {position}: {', '.join(words)}")

# Check what letters appear between known words
print("\n" + "="*80)
print("10. INTERSTITIAL LETTER PATTERNS")
print("="*80)

print("\nLetters appearing BETWEEN key words:")
for word in sorted(positions.keys(), key=lambda w: positions[w][0]):
    start, end = positions[word]
    before_start = max(0, start - 5)
    after_end = min(len(plaintext), end + 5)

    before_text = plaintext[before_start:start]
    after_text = plaintext[end:after_end]

    print(f"\n{word}:")
    print(f"  Before (last 5): {before_text}")
    print(f"  After (first 5): {after_text}")
