#!/usr/bin/env python3
"""
Test alternative encoding hypotheses for K4 gibberish.

Since standard Vigenère keys don't produce coherent English,
test if gibberish uses:
1. Coordinates encoded as letters
2. Atbash cipher (reverse alphabet)
3. Substitution cipher based on position
4. XOR operations
5. Simple rotation patterns
"""

from collections import Counter

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

GAP1 = "QAPBZDBKZEL"
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

def atbash_decode(text):
    """Decode using Atbash cipher (A↔Z, B↔Y, etc)."""
    result = ""
    for char in text:
        if char.isalpha():
            result += chr(ord('Z') - (ord(char) - ord('A')))
        else:
            result += char
    return result

def substitution_from_position(text, start_positions):
    """Test if each gap uses a substitution based on its position."""
    # Gap 1 starts at position 5, Gap 2 at 16, Gap 3 at 54, Gap 4 at 63
    results = []
    for gap_name, gap_text, start_pos in start_positions:
        # Create position-based substitution
        decoded = ""
        for i, char in enumerate(gap_text):
            shift = (start_pos + i) % 26
            decoded_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            decoded += decoded_char

        results.append((gap_name, decoded))
    return results

def xor_with_readable(ciphertext, readable_word):
    """XOR gibberish with readable words."""
    result = ""
    for i, char in enumerate(ciphertext):
        if i < len(readable_word):
            xor_val = ord(char) ^ ord(readable_word[i % len(readable_word)])
            result += chr((xor_val % 26) + ord('A'))
        else:
            result += char
    return result

def reverse_alphabetic(text):
    """Reverse text and apply Atbash."""
    return atbash_decode(text[::-1])

# =============================================================================
# TEST 1: ATBASH CIPHER
# =============================================================================

print("="*80)
print("TEST 1: ATBASH CIPHER (Reverse alphabet: A↔Z, B↔Y, etc)")
print("="*80)

gaps = [
    ("Gap 1", GAP1, 5),
    ("Gap 2", GAP2, 16),
    ("Gap 3", GAP3, 54),
    ("Gap 4", GAP4, 63)
]

for gap_name, gap_text, start_pos in gaps:
    decoded = atbash_decode(gap_text)
    print(f"\n{gap_name}: {gap_text}")
    print(f"  Atbash: {decoded}")

    # Check for English-like patterns
    vowels = sum(1 for c in decoded if c in 'AEIOU')
    vowel_ratio = vowels / len(decoded)

    # Check for word patterns
    words_found = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'CAN']
    found = [w for w in words_found if w in decoded]

    print(f"  Vowel ratio: {vowel_ratio:.1%}")
    if found:
        print(f"  ⚠ Found words: {found}")

# =============================================================================
# TEST 2: REVERSED + ATBASH
# =============================================================================

print(f"\n{'='*80}")
print("TEST 2: REVERSED TEXT + ATBASH")
print("="*80)

for gap_name, gap_text, start_pos in gaps:
    decoded = reverse_alphabetic(gap_text)
    print(f"\n{gap_name}: {gap_text}")
    print(f"  Reversed Atbash: {decoded}")

    vowels = sum(1 for c in decoded if c in 'AEIOU')
    vowel_ratio = vowels / len(decoded)
    print(f"  Vowel ratio: {vowel_ratio:.1%}")

# =============================================================================
# TEST 3: POSITION-BASED SHIFT
# =============================================================================

print(f"\n{'='*80}")
print("TEST 3: POSITION-BASED SHIFT (ROT by position in plaintext)")
print("="*80)

print("\nUsing gap starting positions: Gap1=5, Gap2=16, Gap3=54, Gap4=63")
results = substitution_from_position(GAP1 + GAP2 + GAP3 + GAP4, gaps)

for gap_name, decoded in results:
    print(f"\n{gap_name}: {decoded}")
    vowels = sum(1 for c in decoded if c in 'AEIOU')
    vowel_ratio = vowels / len(decoded)
    print(f"  Vowel ratio: {vowel_ratio:.1%}")

# =============================================================================
# TEST 4: XOR WITH READABLE WORDS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 4: XOR GIBBERISH WITH READABLE WORDS")
print("="*80)

readable_words = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]

# Try XOR-ing Gap 1 with each readable word
print(f"\nGap 1: {GAP1} (paired with readable words)")
for word in readable_words:
    result = xor_with_readable(GAP1, word)
    print(f"  XOR with {word:15s}: {result}")

# Try XOR-ing Gap 2 with each readable word
print(f"\nGap 2: {GAP2} (first 20 chars, paired with readable words)")
for word in readable_words:
    result = xor_with_readable(GAP2[:20], word)
    print(f"  XOR with {word:15s}: {result}")

# =============================================================================
# TEST 5: REVERSE TEXT ONLY
# =============================================================================

print(f"\n{'='*80}")
print("TEST 5: REVERSED TEXT")
print("="*80)

for gap_name, gap_text, start_pos in gaps:
    reversed_text = gap_text[::-1]
    print(f"\n{gap_name}: {gap_text}")
    print(f"  Reversed: {reversed_text}")

    vowels = sum(1 for c in reversed_text if c in 'AEIOU')
    vowel_ratio = vowels / len(reversed_text)
    print(f"  Vowel ratio: {vowel_ratio:.1%}")

# =============================================================================
# TEST 6: CHECK IF GIBBERISH SPELLS SOMETHING BACKWARDS
# =============================================================================

print(f"\n{'='*80}")
print("TEST 6: COMMON WORDS SPELLED BACKWARDS IN GIBBERISH")
print("="*80)

common_words = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
    'BERLIN', 'CLOCK', 'UNDERGROUND', 'COORDINATES', 'LOCATION', 'BEARING'
]

all_gaps = "".join([GAP1, GAP2, GAP3, GAP4])

for word in common_words:
    reversed_word = word[::-1]
    if reversed_word in all_gaps:
        pos = all_gaps.find(reversed_word)
        print(f"  Found '{word}' backwards as '{reversed_word}' at position {pos}")
    if word in all_gaps:
        pos = all_gaps.find(word)
        print(f"  Found '{word}' forwards at position {pos}")

# =============================================================================
# TEST 7: NUMERIC ENCODING
# =============================================================================

print(f"\n{'='*80}")
print("TEST 7: INTERPRET AS NUMERIC ENCODING")
print("="*80)

# Convert letters to numbers (A=0, B=1, ..., Z=25)
for gap_name, gap_text, start_pos in gaps:
    numbers = [ord(c) - ord('A') for c in gap_text]
    print(f"\n{gap_name}: {gap_text}")
    print(f"  As numbers (A=0...Z=25): {numbers}")

    # Try interpreting as coordinates
    # Could be: deg.minutes.seconds or similar
    # Or could be: base-26 encoded numbers

    # Base-26 interpretation
    base26_val = 0
    for num in numbers:
        base26_val = base26_val * 26 + num

    print(f"  Base-26 value: {base26_val}")

    # Check if could be coordinates (assuming 3-char chunks for degrees)
    if len(gap_text) == 9:
        chunks = [gap_text[i:i+3] for i in range(0, 9, 3)]
        print(f"  Split into 3-char chunks: {chunks}")

        for chunk in chunks:
            val = sum((ord(c) - ord('A')) * (26 ** (2-i)) for i, c in enumerate(chunk))
            print(f"    {chunk}: base-26 = {val}, as degrees = {val/100:.2f}°")

print("\n" + "="*80)
print("ALTERNATIVE ENCODING TEST COMPLETE")
print("="*80)
print("\nIf any of these show readable English or recognizable patterns,")
print("the gibberish may use that encoding instead of standard Vigenère!")
