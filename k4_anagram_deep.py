#!/usr/bin/env python3
"""
Deep anagram and message extraction analysis for K4
"""

from collections import Counter
import itertools

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Gibberish sections
gibberish_sections = {
    "before_NORTHEAST": "QAPBZDBKZEL",
    "before_BERLINCLOCK": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",
    "before_ABOVE": "RSPVJWQUL",
    "after_ABOVE": "ZOLRKCAYF"
}

print("="*80)
print("DEEP ANAGRAM AND MESSAGE EXTRACTION ANALYSIS")
print("="*80)

# Load a comprehensive word list
common_words = [
    # Directional/location words
    "GROUND", "SURFACE", "SHADOW", "WATER", "STONE", "VAULT", "PASSAGE",
    "WALL", "CORNER", "EDGE", "MARKS", "POINT", "SECRET", "HIDDEN",
    "BENEATH", "WITHIN", "TREASURE", "CHAMBER", "TUNNEL", "ENTRY", "EXIT",
    "LOCATION", "PLACE", "SPOT", "SITE", "CHAMBER", "ROOM", "SPACE",
    "COORDINATES", "COMPASS", "BEARING", "DIRECTION",
    # Common short words
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN",
    "HER", "WAS", "ONE", "OUR", "OUT", "WHO", "OIL", "MEN", "SEE",
    "HAD", "HAS", "GET", "GOT", "NEW", "NOW", "OLD", "OWN", "SAY",
    "SHE", "TOO", "TWO", "USE", "WAY", "MAY", "DAY", "LET", "PUT",
    # Cryptography/puzzle words
    "CIPHER", "CODE", "CLUE", "HINT", "KEY", "LOCK", "OPEN", "CLOSE",
    "SOLVE", "FIND", "SEEK", "LOOK", "SEARCH", "DISCOVER",
    # Treasure/hunt words
    "QUEST", "HUNT", "PRIZE", "GOLD", "JEWEL", "RICHES",
    # Action words
    "MARK", "SHOW", "TELL", "TAKE", "GIVE", "MAKE", "TURN", "MOVE"
]

print("\n1. ANAGRAM ANALYSIS FOR EACH GIBBERISH SECTION")
print("-" * 80)

def find_anagrams_and_subsequences(text, word_list, min_length=4):
    """Find anagrams AND letter combinations that spell words"""
    results = {
        'anagrams': [],
        'subsequences': [],
        'contained': []
    }

    available = Counter(text)

    for word in word_list:
        word_counter = Counter(word)

        # Check if it's a perfect anagram (uses subset of available letters)
        can_form = all(available[c] >= word_counter[c] for c in word_counter)
        if can_form:
            results['anagrams'].append(word)

        # Check if letters appear in sequence
        remaining = list(text)
        found_sequence = True
        for c in word:
            if c in remaining:
                remaining.remove(c)
            else:
                found_sequence = False
                break
        if found_sequence:
            results['subsequences'].append(word)

        # Check if word is contained within
        if word in text:
            results['contained'].append(word)

    return results

for section_name, section_text in gibberish_sections.items():
    print(f"\n{section_name}: {section_text} ({len(section_text)} letters)")
    results = find_anagrams_and_subsequences(section_text, common_words)

    if results['contained']:
        print(f"  CONTAINED: {results['contained']}")
    if results['anagrams']:
        print(f"  ANAGRAMS: {results['anagrams']}")
    if results['subsequences']:
        print(f"  SUBSEQUENCES: {results['subsequences']}")
    if not any([results['contained'], results['anagrams'], results['subsequences']]):
        print(f"  (No matches found)")

# Try to extract meaningful words from specific positions
print("\n" + "="*80)
print("2. LETTER POSITION MAPPING (Extract by position pattern)")
print("-" * 80)

# Try alternating patterns starting from different positions
print("\nAlternating letter patterns:")
for start_offset in range(2):
    for step in [2, 3, 4, 5]:
        extracted = plaintext[start_offset::step]
        print(f"  Offset {start_offset}, Step {step}: {extracted}")

# Extract letters matching a position formula
print("\nPositions matching X^2 mod N patterns:")
positions_to_extract = []

# Try positions where position % 7 == specific value
for mod_val in range(7):
    positions = [i for i in range(len(plaintext)) if i % 7 == mod_val]
    extracted = ''.join(plaintext[i] for i in positions[:15])  # First 15
    print(f"  i % 7 == {mod_val}: {extracted}")

# Try specific high-value positions
print("\nEvery 13th letter:")
print(f"  {plaintext[::13]}")

print("\nEvery 17th letter:")
print(f"  {plaintext[::17]}")

# Check if gibberish sections themselves contain hidden messages
print("\n" + "="*80)
print("3. GIBBERISH SECTION INTERNAL ANALYSIS")
print("-" * 80)

def analyze_section(text):
    """Extract every nth letter from a section"""
    print(f"\nSection: {text}")
    for n in [2, 3]:
        extracted = text[::n]
        print(f"  Every {n}th: {extracted}")

for section_name, section_text in gibberish_sections.items():
    analyze_section(section_text)

# Look for sentence completion using extracted patterns
print("\n" + "="*80)
print("4. SENTENCE STRUCTURE ANALYSIS")
print("-" * 80)

print("\nThe message pattern appears to be a direction sequence:")
print("  UNDER [X] NORTHEAST [Y] BERLINCLOCK [Z] ABOVE [W]")
print("\nPotential meanings:")
print("  - Geographic directions (compass points)")
print("  - Spatial relationships (under ground, above surface)")
print("  - Treasure hunt clues")

# Extract initials from gibberish
print("\n" + "="*80)
print("5. FIRST LETTERS OF GIBBERISH SECTIONS")
print("-" * 80)

first_letters = []
for section_name, section_text in gibberish_sections.items():
    first_letters.append(section_text[0])
    print(f"{section_name:25} starts with: {section_text[0]} (from {section_text[:3]})")

print(f"\nFirst letters spell: {''.join(first_letters)}")

# Last letters
print("\n" + "="*80)
print("6. LAST LETTERS OF GIBBERISH SECTIONS")
print("-" * 80)

last_letters = []
for section_name, section_text in gibberish_sections.items():
    last_letters.append(section_text[-1])
    print(f"{section_name:25} ends with: {section_text[-1]} (from {section_text[-3:]})")

print(f"\nLast letters spell: {''.join(last_letters)}")

# Try decoding gibberish as simple substitution
print("\n" + "="*80)
print("7. LOOKING FOR SIMPLE SUBSTITUTION PATTERNS")
print("-" * 80)

# Check if gibberish might be gibberish transformed by ROT-N
for rot in range(1, 26):
    for section_name, section_text in gibberish_sections.items():
        rotated = ''.join(chr((ord(c) - ord('A') + rot) % 26 + ord('A')) for c in section_text)
        # Check if any common words appear
        if any(word in rotated for word in ['THE', 'AND', 'FOR', 'GROUND', 'STONE', 'SHADOW']):
            print(f"ROT-{rot} {section_name}: {rotated}")

print("\n" + "="*80)
print("8. BIGRAM AND TRIGRAM FREQUENCY IN GIBBERISH")
print("-" * 80)

for section_name, section_text in gibberish_sections.items():
    print(f"\n{section_name}:")

    # Bigrams
    bigrams = Counter(section_text[i:i+2] for i in range(len(section_text)-1))
    print(f"  Most common bigrams: {bigrams.most_common(3)}")

    # Trigrams
    trigrams = Counter(section_text[i:i+3] for i in range(len(section_text)-2))
    print(f"  Most common trigrams: {trigrams.most_common(3)}")
