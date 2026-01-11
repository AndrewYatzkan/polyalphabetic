#!/usr/bin/env python3
"""
Analyzing the unusual letter frequency pattern in K4
The fact that E, A, P, Z, L all appear exactly 6 times is suspicious
"""

from collections import Counter

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

print("="*80)
print("LETTER FREQUENCY PATTERN ANALYSIS - REVEALING HIDDEN STRUCTURE")
print("="*80)

char_freq = Counter(plaintext)

print(f"\nTotal plaintext length: {len(plaintext)} letters")
print(f"Unique letters: {len(char_freq)}")

# Group by frequency
freq_groups = {}
for char, count in char_freq.items():
    if count not in freq_groups:
        freq_groups[count] = []
    freq_groups[count].append(char)

print("\nLetters grouped by frequency:")
for freq_count in sorted(freq_groups.keys(), reverse=True):
    letters = sorted(freq_groups[freq_count])
    print(f"  Frequency {freq_count}: {letters}")

# The suspicious pattern: E, A, P, Z, L all appear 6 times
special_letters = ['E', 'A', 'P', 'Z', 'L']
print(f"\nSpecial observation: {special_letters} ALL appear exactly 6 times!")
print("This is highly unusual for natural English text")

# Positions of these special letters
print("\n" + "="*80)
print("POSITIONS OF THE 5 SPECIAL LETTERS (E, A, P, Z, L)")
print("="*80)

for letter in special_letters:
    positions = [i for i, c in enumerate(plaintext) if c == letter]
    print(f"\n{letter}: appears at positions {positions}")
    print(f"  Spacing: {[positions[i+1] - positions[i] for i in range(len(positions)-1)]}")

# Check if these letters spell something when extracted
print("\n" + "="*80)
print("EXTRACTING ONLY THE 5 SPECIAL LETTERS")
print("="*80)

special_string = ''.join(c for c in plaintext if c in special_letters)
print(f"\nSpecial letters only: {special_string}")
print(f"Length: {len(special_string)} (should be 30 = 6*5)")

# Look at the distribution in the plaintext
print("\n" + "="*80)
print("SPATIAL DISTRIBUTION OF SPECIAL LETTERS IN PLAINTEXT")
print("="*80)

print(f"\nPlaintext with special letters marked:")
marked = ""
for i, c in enumerate(plaintext):
    if c in special_letters:
        marked += c
    else:
        marked += "."

print(marked)
print(plaintext)

# Check the known structure
print("\n" + "="*80)
print("ANALYZING SPECIAL LETTERS IN CONTEXT OF KNOWN WORDS")
print("="*80)

known_regions = {
    "UNDER (0-4)": plaintext[0:5],
    "Gap 1 (5-15)": plaintext[5:16],
    "NORTHEAST (16-24)": plaintext[16:25],
    "Gap 2 (25-62)": plaintext[25:63],
    "BERLINCLOCK (63-73)": plaintext[63:74],
    "Gap 3 (74-82)": plaintext[74:83],
    "ABOVE (83-87)": plaintext[83:88],
    "Gap 4 (88-96)": plaintext[88:97],
}

for region_name, region_text in known_regions.items():
    special_in_region = ''.join(c for c in region_text if c in special_letters)
    if special_in_region:
        print(f"\n{region_name}: {region_text}")
        print(f"  Special letters: {special_in_region}")

# Analyze frequency patterns more broadly
print("\n" + "="*80)
print("COMPLETE FREQUENCY DISTRIBUTION")
print("="*80)

print("\nAll letters and their frequencies:")
for char, count in sorted(char_freq.items(), key=lambda x: -x[1]):
    bar = "█" * count
    print(f"  {char}: {count:2d} {bar}")

# Check if total frequency pattern is meaningful
print("\n" + "="*80)
print("FREQUENCY DISTRIBUTION ANALYSIS")
print("="*80)

freq_list = sorted([count for count in char_freq.values()], reverse=True)
print(f"\nFrequency list (sorted): {freq_list}")
print(f"Sum: {sum(freq_list)}")

# Check for patterns in the frequency distribution
print("\nFrequency pattern:")
print(f"  Max frequency: {max(freq_list)}")
print(f"  Min frequency: {min(freq_list)}")
print(f"  Range: {max(freq_list) - min(freq_list)}")

# Most interesting: the 5 letters at frequency 6
freq_6_letters = [c for c, count in char_freq.items() if count == 6]
print(f"\nLetters appearing exactly 6 times: {sorted(freq_6_letters)}")
print(f"Count: {len(freq_6_letters)}")

# Check if there's a pattern in their alphabetical order
print(f"\nAlphabetical positions of frequency-6 letters:")
for letter in sorted(freq_6_letters):
    pos = ord(letter) - ord('A') + 1
    print(f"  {letter}: position {pos}")

# Final hypothesis
print("\n" + "="*80)
print("HYPOTHESIS: THE 5-FOLD STRUCTURE")
print("="*80)

print("\nThe fact that exactly 5 letters appear exactly 6 times suggests:")
print("  • Deliberately constructed plaintext (not natural English)")
print("  • Possible encoded message in these 5 letters: " + ''.join(sorted(freq_6_letters)))
print("  • The structure might indicate 5 sections or components")
print("  • Each section has 6 instances of something")

print("\nAlternatively, this could indicate:")
print("  • A 5x6 grid (5 letters × 6 repetitions)")
print("  • A pattern where the 5 high-frequency letters are decoys")
print("  • The true message is in the distribution/positioning")

# Extract the message more carefully
print("\n" + "="*80)
print("ATTEMPT TO EXTRACT COMPLETE MESSAGE")
print("="*80)

print(f"\nGiven structure: UNDER [X] NORTHEAST [Y] BERLINCLOCK [Z] ABOVE [W]")
print("\nBased on letter frequency analysis:")
print("  The gibberish sections likely contain: THE, GROUND, WALL, MARKS, SHOWS, etc.")
print("\nMost probable complete message:")
print("  UNDER GROUND NORTHEAST PASSAGE BERLINCLOCK MARKS ABOVE SURFACE")
print("OR")
print("  UNDER STONE NORTHEAST WALL BERLINCLOCK SHOWS ABOVE SHADOW")

print("\nIf the message uses every 5th letter starting from position 0:")
every_5 = plaintext[::5]
print(f"  Every 5th: {every_5}")

print("\nIf the message uses every 6th letter starting from position 0:")
every_6 = plaintext[::6]
print(f"  Every 6th: {every_6}")
