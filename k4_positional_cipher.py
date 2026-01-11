#!/usr/bin/env python3
"""
Positional cipher and structural analysis
Looking for how the gibberish might encode the missing words
"""

from collections import Counter

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("="*80)
print("POSITIONAL CIPHER ANALYSIS FOR K4")
print("="*80)

# Maybe the gibberish is positioned specifically to reveal message
# Let's try extracting the hidden message using different position extraction methods

print("\n1. ALTERNATING POSITION EXTRACTION FROM WHOLE PLAINTEXT")
print("-"*80)

# Every 2nd letter starting from position 0
every_2_even = plaintext[::2]
print(f"Every 2nd letter (starting 0): {every_2_even}")

# Every 2nd letter starting from position 1
every_2_odd = plaintext[1::2]
print(f"Every 2nd letter (starting 1): {every_2_odd}")

# Look for patterns within this
print(f"\nLooking for words in every-2nd extraction:")
# Check against known words
keywords = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE", "THE", "GROUND",
            "STONE", "SHADOW", "PASSAGE", "WALL", "MARKS"]

for keyword in keywords:
    if keyword in every_2_even:
        idx = every_2_even.find(keyword)
        print(f"  Found '{keyword}' at position {idx} in even-positions string")
    if keyword in every_2_odd:
        idx = every_2_odd.find(keyword)
        print(f"  Found '{keyword}' at position {idx} in odd-positions string")

print("\n2. EXTRACTING POSITIONS BETWEEN KNOWN WORDS")
print("-"*80)

# Extract the exact structure
structure = [
    ("UNDER", 0, 5),
    ("GAP", 5, 16),
    ("NORTHEAST", 16, 25),
    ("GAP", 25, 63),
    ("BERLINCLOCK", 63, 74),
    ("GAP", 74, 83),
    ("ABOVE", 83, 88),
    ("GAP", 88, 97)
]

print(f"Total length: {len(plaintext)}")
print(f"\nStructural breakdown:")
for name, start, end in structure:
    section = plaintext[start:end]
    print(f"  {name:15} ({start:2d}-{end:2d}): {section}")

# Analyze gap positions
print("\n3. GAP POSITION ANALYSIS")
print("-"*80)

gaps = [
    ("1st GAP (5-15)", plaintext[5:16], "11 letters"),
    ("2nd GAP (25-62)", plaintext[25:63], "38 letters"),
    ("3rd GAP (74-82)", plaintext[74:83], "9 letters"),
    ("4th GAP (88-96)", plaintext[88:97], "9 letters")
]

for name, gap_text, length_desc in gaps:
    print(f"\n{name}: {gap_text}")
    print(f"  Length: {length_desc}")

    # Try every nth letter extraction within gap
    for n in [2, 3]:
        extracted = gap_text[::n]
        if len(extracted) > 0:
            print(f"  Every {n}th: {extracted}")

# Try to see if there's a pattern in gap lengths
print("\n4. GAP LENGTH PATTERN ANALYSIS")
print("-"*80)

gap_lengths = [11, 38, 9, 9]
print(f"Gap lengths: {gap_lengths}")
print(f"Total gap letters: {sum(gap_lengths)}")

# Check if this forms a pattern
print("\nPossible interpretations of lengths:")
print(f"  11 = ? (could be 11 letters, or a code)")
print(f"  38 = ? (could encode something)")
print(f"  9 = ? (could be 9 letters)")
print(f"  9 = ? (could be 9 letters)")

# Try Caesar on the entire plaintext
print("\n5. CAESAR SHIFT TEST")
print("-"*80)

def caesar_shift(text, shift):
    return ''.join(chr((ord(c) - ord('A') + shift) % 26 + ord('A')) for c in text)

# Maybe the gaps encode with a caesar cipher
print("Trying Caesar shifts on gap sections:")

for gap_name, gap_text, _ in gaps:
    print(f"\n{gap_name}: {gap_text}")
    for shift in [5, 13, 17]:  # Common shifts
        shifted = caesar_shift(gap_text, shift)
        print(f"  ROT-{shift:2d}: {shifted}")

# Look for the sentence pattern more carefully
print("\n6. SENTENCE PATTERN COMPLETION")
print("-"*80)

print("\nKnown structure:")
print("  UNDER [X1] NORTHEAST [X2] BERLINCLOCK [X3] ABOVE [X4]")
print("\nWhere:")
print(f"  X1 is embedded in: {plaintext[5:16]}")
print(f"  X2 is embedded in: {plaintext[25:63]}")
print(f"  X3 is embedded in: {plaintext[74:83]}")
print(f"  X4 is embedded in: {plaintext[88:97]}")

# Maybe X1, X2, X3, X4 are anagrams
print("\n7. ANAGRAM WORD EXTRACTION BY LENGTH")
print("-"*80)

# Common words of different lengths that might fit
word_candidates = {
    11: ["NORTHEASTERN", "SOUTHEASTERN", "SOUTHWESTERN"],  # too long
    11: ["UNDERNEATH", "TRANSFORMER"],  # actual 11-letter words
    38: [],  # This is very long - probably multiple words
    9: ["CLOCKWISE", "NORTHEAST", "LOCATIONS", "DIRECTION"],
}

# Actually, try shorter words that would fit
actual_words = {
    11: ["UNDERNEATH", "TRANSFORMER", "GRANDFATHER"],
    38: ["A COLLECTION OF WORDS", "MULTIPLE SENTENCES"],
    9: ["DIRECTION", "CLOCKWISE", "NORTHEAST", "LOCATIONS"],
}

print("If gaps contain single words:")
print("  11-letter words: UNDERNEATH, TRANSFORMER, GRANDFATHER")
print("  38-letter gap: Probably NOT a single word (maybe padding + hidden message)")
print("  9-letter words: DIRECTION, CLOCKWISE, NORTHEAST, LOCATIONS")

# Try looking at first letters
print("\n8. ACROSTIC ANALYSIS")
print("-"*80)

print("First letters of words in plaintext:")
words_in_plaintext = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]
first_letters = [w[0] for w in words_in_plaintext]
print(f"  First letters: {first_letters} = {''.join(first_letters)}")

print("\nGap section first letters:")
gap_texts = [plaintext[5:16], plaintext[25:63], plaintext[74:83], plaintext[88:97]]
gap_firsts = [g[0] for g in gap_texts]
print(f"  Gap first letters: {gap_firsts} = {''.join(gap_firsts)}")

print("\nGap section last letters:")
gap_lasts = [g[-1] for g in gap_texts]
print(f"  Gap last letters: {gap_lasts} = {''.join(gap_lasts)}")

# Check if message is in middle of long gap
print("\n9. CHECKING IF MESSAGE HIDDEN IN LARGE GAP")
print("-"*80)

large_gap = plaintext[25:63]
print(f"Large gap (38 letters): {large_gap}")

# Maybe the middle of this gap contains the real message?
mid = len(large_gap) // 2
print(f"First half: {large_gap[:mid]}")
print(f"Second half: {large_gap[mid:]}")

# Try extracting from every 3rd position
print(f"Every 3rd letter: {large_gap[::3]}")
print(f"Every 4th letter: {large_gap[::4]}")

# Try looking at positions that correspond to known word lengths
print("\n10. WORD LENGTH RECONSTRUCTION")
print("-"*80)

# If the sentence is "UNDER X NORTHEAST Y BERLINCLOCK Z ABOVE W"
# Try common word combinations
print("\nMost likely sentence completions:")
print("  1. UNDER GROUND NORTHEAST ... BERLINCLOCK LIES ABOVE GROUND")
print("  2. UNDER STONE NORTHEAST PASSAGE BERLINCLOCK MARKS ABOVE SHADOW")
print("  3. UNDER THE NORTHEAST WALL BERLINCLOCK SHOWS ABOVE SURFACE")

# Check which of these could be encoded
test_sentences = [
    ("GROUND", "NORTHEASTERN", "LIES", "GROUND"),
    ("STONE", "PASSAGE", "MARKS", "SHADOW"),
    ("THE", "WALL", "SHOWS", "SURFACE"),
]

for word1, word2, word3, word4 in test_sentences:
    total = sum(len(w) for w in [word1, word2, word3, word4])
    print(f"\n'{word1}' + '{word2}' + '{word3}' + '{word4}'")
    print(f"  Lengths: {len(word1)} + {len(word2)} + {len(word3)} + {len(word4)} = {total}")
    print(f"  Available gaps: 11 + 38 + 9 + 9 = 67")
    if total <= 67:
        print(f"  ✓ Could fit (with {67-total} extra padding letters)")

# Check for hidden message in position
print("\n11. POSITIONAL PATTERN CHECK")
print("-"*80)

# Maybe the plaintext positions themselves are meaningful
# Map each gibberish letter to its position
print("Gibberish letter positions in plaintext:")
for gap_name, gap_text, _ in gaps:
    positions = []
    for i, letter in enumerate(gap_text):
        # Find actual position in plaintext
        actual_pos = plaintext.find(gap_text)
        positions.append(actual_pos + i)
    print(f"{gap_name}: {positions}")
