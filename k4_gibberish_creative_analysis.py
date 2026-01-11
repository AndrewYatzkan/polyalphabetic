#!/usr/bin/env python3
"""
Creative pattern analysis for K4 gibberish sections
Looking for: word fragments, partial decryption, substitution patterns
"""

from collections import Counter
import string

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

gibberish = {
    "Section 1": "QAPBZDBKZEL",      # 5-15
    "Section 2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",  # 25-62
    "Section 3": "RSPVJWQUL",        # 74-82
    "Section 4": "ZOLRKCAYF"         # 88-96
}

readable = {
    "UNDER": (0, 4),
    "NORTHEAST": (16, 24),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73),
    "ABOVE": (83, 86)
}

# Common English substrings and words
common_substrings = [
    'THE', 'AND', 'FOR', 'ARE', 'YOU', 'NOT', 'BUT', 'CAN', 'HAD', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
    'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY',
    'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'OVER', 'MANY',
    'MORE', 'SOME', 'SUCH', 'TIME', 'VERY', 'WHEN', 'JUST', 'KNOW', 'TAKE',
    'COME', 'DOES', 'GOOD', 'MADE', 'MAKE', 'MOST', 'THEM', 'THEN', 'WITH'
]

print("=" * 80)
print("CREATIVE PATTERN ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. LOOK FOR PARTIAL WORDS / WORD FRAGMENTS
# ============================================================================
print("\n1. LOOKING FOR PARTIAL WORDS / WORD FRAGMENTS")
print("-" * 80)

# Common word endings
endings = ['ED', 'ER', 'ING', 'LY', 'TION', 'NESS', 'MENT', 'ABLE', 'FUL', 'LESS']
# Common word beginnings
beginnings = ['UN', 'RE', 'PRE', 'COM', 'CON', 'SUB', 'OVER', 'OUT', 'UNDER']

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    # Check for endings
    found_endings = []
    for ending in endings:
        if ending in sec_text:
            pos = sec_text.find(ending)
            found_endings.append(f"{ending} at position {pos}")

    if found_endings:
        print(f"  Found word endings: {', '.join(found_endings)}")

    # Check for beginnings
    found_begins = []
    for beginning in beginnings:
        if beginning in sec_text:
            pos = sec_text.find(beginning)
            found_begins.append(f"{beginning} at position {pos}")

    if found_begins:
        print(f"  Found word beginnings: {', '.join(found_begins)}")

    # Check for common substrings
    found_subs = []
    for substring in common_substrings:
        if substring in sec_text:
            pos = sec_text.find(substring)
            found_subs.append(f"{substring} at position {pos}")

    if found_subs:
        print(f"  Found common substrings: {', '.join(found_subs)}")

    # If nothing found
    if not found_endings and not found_begins and not found_subs:
        print(f"  No common English patterns found")

# ============================================================================
# 2. PATTERN: LOOK FOR REPEATED LETTER SEQUENCES THAT COULD BE MARKERS
# ============================================================================
print("\n\n2. REPEATED SEQUENCES THAT MIGHT BE MARKERS")
print("-" * 80)

all_gibberish = "".join(gibberish.values())

# Look for 2-letter sequences that repeat across sections
digraph_freq = Counter()
for sec_text in gibberish.values():
    for i in range(len(sec_text) - 1):
        digraph_freq[sec_text[i:i+2]] += 1

print(f"\nDigraphs appearing in multiple sections:")
for digraph, count in sorted(digraph_freq.items(), key=lambda x: -x[1]):
    if count > 1:
        # Find which sections contain it
        containing = []
        for sec_name, sec_text in gibberish.items():
            if digraph in sec_text:
                containing.append(sec_name)
        print(f"  {digraph}: {count} times in {', '.join(containing)}")

# ============================================================================
# 3. CHECK FOR LETTER SUBSTITUTION PATTERNS
# ============================================================================
print("\n\n3. POTENTIAL LETTER SUBSTITUTION ANALYSIS")
print("-" * 80)

# Get all unique letters from each section
print("\nUnique letter sets by section:")
for sec_name, sec_text in gibberish.items():
    unique = set(sec_text)
    print(f"  {sec_name}: {sorted(unique)} ({len(unique)} unique)")

# Find overlaps
all_letters = set(all_gibberish)
print(f"\nTotal unique letters in all gibberish: {sorted(all_letters)} ({len(all_letters)} letters)")
print(f"Missing from English alphabet: {sorted(set(string.ascii_uppercase) - all_letters)}")

# ============================================================================
# 4. POSITIONAL ANALYSIS - DO LETTERS APPEAR IN SIMILAR POSITIONS?
# ============================================================================
print("\n\n4. POSITIONAL PATTERNS")
print("-" * 80)

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    # Group by position modulo 3, 4, 5 (common Vigenere periods)
    for mod in [3, 4, 5]:
        position_groups = {i: [] for i in range(mod)}
        for idx, letter in enumerate(sec_text):
            position_groups[idx % mod].append(letter)

        print(f"  Grouping by position mod {mod}:")
        for pos in range(mod):
            letters = position_groups[pos]
            unique = set(letters)
            print(f"    Position {pos}: {letters} -> unique: {sorted(unique)}")

# ============================================================================
# 5. STRUCTURE ANALYSIS - ARE THERE BLOCK PATTERNS?
# ============================================================================
print("\n\n5. STRUCTURAL/BLOCK PATTERNS")
print("-" * 80)

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text} (length: {len(sec_text)})")

    # Try breaking into chunks of various sizes
    for chunk_size in [2, 3, 4]:
        if len(sec_text) % chunk_size == 0:
            chunks = [sec_text[i:i+chunk_size] for i in range(0, len(sec_text), chunk_size)]
            print(f"  Chunks of {chunk_size}: {' '.join(chunks)}")

            # Check if any chunks are repeated
            chunk_freq = Counter(chunks)
            repeated = {c: count for c, count in chunk_freq.items() if count > 1}
            if repeated:
                print(f"    Repeated chunks: {repeated}")

# ============================================================================
# 6. PHONETIC PATTERNS - DO SECTIONS SOUND LIKE SOMETHING?
# ============================================================================
print("\n\n6. VOWEL PLACEMENT ANALYSIS")
print("-" * 80)

vowels = set('AEIOU')

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    # Mark vowel positions
    vowel_pattern = ''.join('V' if c in vowels else 'C' for c in sec_text)
    print(f"  Pattern (V=vowel, C=consonant): {vowel_pattern}")

    # Find consonant clusters
    clusters = []
    cluster = ""
    for c in vowel_pattern:
        if c == 'C':
            cluster += c
        else:
            if cluster:
                clusters.append(cluster)
            cluster = ""
    if cluster:
        clusters.append(cluster)

    if clusters:
        print(f"  Consonant clusters: {clusters}")
        print(f"  Max cluster size: {max(len(c) for c in clusters)} consonants in a row")

# ============================================================================
# 7. LOOKING FOR KEYWORDS HIDDEN BY POSITION
# ============================================================================
print("\n\n7. HIDDEN KEYWORDS (EVERY NTH LETTER)")
print("-" * 80)

keywords = ['KRYPTOS', 'PALIMPSEST', 'SHADOW', 'BERLIN', 'CLOCK', 'NORTH',
            'EAST', 'ALPHABET', 'CIPHER', 'KEY', 'DECRYPT']

all_gib = "".join(gibberish.values())

for keyword in keywords:
    for step in [2, 3, 4, 5]:
        # Every nth letter
        extracted = all_gib[::step]
        if keyword in extracted:
            print(f"\nFound '{keyword}' at step {step}!")
            print(f"  Extracted: {extracted}")

        # Backwards
        extracted_rev = all_gib[::-1][::step]
        if keyword in extracted_rev:
            print(f"\nFound '{keyword}' backwards at step {step}!")
            print(f"  Extracted: {extracted_rev}")

# ============================================================================
# 8. CHECKING FOR SUBSTITUTION CIPHER CLUES
# ============================================================================
print("\n\n8. LETTER REPLACEMENT ANALYSIS")
print("-" * 80)

# For each gibberish section, check if replacing certain letters with others
# produces English words
def find_substitutions(text, dictionary_words):
    """Try to find substitutions that produce English words"""
    candidates = []

    # Common substitution pairs (based on frequency analysis)
    common_pairs = [
        ('Z', 'E'), ('Q', 'S'), ('X', 'T'), ('J', 'R'),
        ('B', 'A'), ('K', 'D'), ('P', 'N'), ('V', 'L')
    ]

    for old, new in common_pairs:
        test = text.replace(old, new)
        for word in dictionary_words:
            if word in test:
                candidates.append((text, old, new, test, word))

    return candidates

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")

    subs = find_substitutions(sec_text, common_substrings)
    if subs:
        for orig, old, new, result, word in subs:
            print(f"  {old}->{new}: {result} (contains '{word}')")

# ============================================================================
# 9. CONTEXT-BASED ANALYSIS
# ============================================================================
print("\n\n9. CONTEXT ANALYSIS - WHAT WORDS COULD FOLLOW/PRECEDE?")
print("-" * 80)

# The readable words are: UNDER, NORTHEAST, BERLIN, CLOCK, ABOVE
# What could logically follow these in the context of Kryptos?

print("\nReadable words and their context:")
print("  UNDER -> ?")
print("  NORTHEAST -> ?")
print("  BERLIN -> ?")
print("  CLOCK -> ?")
print("  ABOVE -> ?")

print("\nPossible contextual words (Kryptos clues):")
possible_words = [
    'LAYER', 'SHADOW', 'PALIMPSEST', 'ABSCISSA', 'ORDINATE',
    'DIGRAPH', 'PLAINTEXT', 'CIPHERTEXT', 'KEY', 'PERIOD'
]

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text}")
    for word in possible_words:
        if any(substr in sec_text for substr in [word[i:i+3] for i in range(len(word)-2)]):
            print(f"  Contains substring(s) from: {word}")

# ============================================================================
# 10. CHECKING IF GIBBERISH COULD BE ANAGRAMS OF REAL WORDS
# ============================================================================
print("\n\n10. ANAGRAM ANALYSIS")
print("-" * 80)

# Common long words that might be anagrammed
long_words = [
    'PALIMPSEST', 'ABSCISSA', 'ORDINATE', 'DIGRAPH', 'CIPHERTEXT',
    'WESTWARDLY', 'SOUTHWEST', 'SOMETHING', 'DIFFERENT', 'CRYPTOGRAPHY'
]

for sec_name, sec_text in gibberish.items():
    print(f"\n{sec_name}: {sec_text} (letters: {sorted(sec_text)})")

    for word in long_words:
        if len(word) == len(sec_text):
            if sorted(word) == sorted(sec_text):
                print(f"  >>> ANAGRAM OF: {word}")

print("\n" + "=" * 80)
print("END OF CREATIVE ANALYSIS")
print("=" * 80)
