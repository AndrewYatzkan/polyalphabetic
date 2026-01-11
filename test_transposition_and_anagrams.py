#!/usr/bin/env python3
"""
Test if the gibberish sections are transpositions or anagrams of English words.
Also test other non-substitution cipher possibilities.
"""

import sys
import re
import itertools
from collections import Counter

# Load dictionary
WORDS = set()
try:
    with open('/home/user/polyalphabetic/OxfordEnglishWords.txt', 'r') as f:
        WORDS = set(word.strip().upper() for word in f.readlines() if word.strip())
except:
    print("Warning: Could not load word dictionary")

def find_anagrams(letters):
    """Find anagrams of letters in the dictionary"""
    letters = letters.upper()
    anagrams = []

    for word in WORDS:
        if len(word) == len(letters) and sorted(word) == sorted(letters):
            anagrams.append(word)

    return anagrams

def find_possible_words_in_set(letters):
    """Find all dictionary words that can be made from the letters"""
    letters = set(letters.upper())
    possible = []

    for word in WORDS:
        if all(c in letters for c in word):
            possible.append(word)

    return sorted(possible, key=len, reverse=True)

def test_columnar_transposition(ciphertext, key):
    """Try to decrypt columnar transposition"""
    ciphertext = ciphertext.upper()
    key = key.upper()

    # Sort key to get column order
    key_order = sorted(range(len(key)), key=lambda i: key[i])

    cols = len(key)
    rows = len(ciphertext) // cols

    if len(ciphertext) % cols != 0:
        return None

    # Create grid with ciphertext read in
    grid = []
    idx = 0
    for col in range(cols):
        grid.append([])
        for row in range(rows):
            if idx < len(ciphertext):
                grid[col].append(ciphertext[idx])
                idx += 1

    # Reorder columns back
    original_order = [0] * cols
    for new_pos, old_pos in enumerate(key_order):
        original_order[old_pos] = new_pos

    result = ""
    for row in range(rows):
        for col in original_order:
            if col < len(grid) and row < len(grid[col]):
                result += grid[col][row]

    return result

def test_route_transposition(ciphertext, route_type='spiral'):
    """Test simple route transposition"""
    # For now, just try reversing
    reversed_text = ciphertext[::-1]

    return reversed_text

def main():
    print("\n" + "="*80)
    print("TRANSPOSITION AND ANAGRAM ANALYSIS")
    print("="*80)

    sections = [
        ("QAPBZDBKZEL", "Gap1"),
        ("LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH", "Gap2"),
        ("RSPVJWQUL", "Gap3"),
        ("ZOLRKCAYF", "Gap4"),
    ]

    print("\n1. TESTING FOR EXACT ANAGRAMS")
    print("="*80 + "\n")

    for ciphertext, section_name in sections:
        print(f"{section_name}: {ciphertext} ({len(ciphertext)} chars)")
        anagrams = find_anagrams(ciphertext)

        if anagrams:
            print(f"  Anagrams found: {anagrams}")
        else:
            print(f"  No exact anagrams found")

        # For short sections, also show all possible words
        if len(ciphertext) <= 20:
            possible = find_possible_words_in_set(ciphertext)[:10]
            if possible:
                print(f"  Possible words (sample): {possible}")

        print()

    print("\n2. TESTING FOR COLUMNAR TRANSPOSITION")
    print("="*80 + "\n")

    # Try different key lengths
    for ciphertext, section_name in sections:
        print(f"{section_name}: {ciphertext} ({len(ciphertext)} chars)")

        for key_len in range(2, len(ciphertext)):
            if len(ciphertext) % key_len == 0:
                # Try simple alphabetic keys
                key = ''.join(chr(ord('A') + (i % 26)) for i in range(key_len))

                result = test_columnar_transposition(ciphertext, key)
                if result:
                    words = len(re.findall(r'[A-Z]{3,}', result))
                    if words > 0:
                        print(f"  Key length {key_len}: {result} ({words} potential words)")

        print()

    print("\n3. TESTING SIMPLE TRANSFORMATIONS")
    print("="*80 + "\n")

    for ciphertext, section_name in sections:
        print(f"{section_name}: {ciphertext}")

        # Reverse
        reversed_text = ciphertext[::-1]
        print(f"  Reversed: {reversed_text}")

        # ROT13
        rot13 = ""
        for char in ciphertext:
            rot13 += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
        print(f"  ROT13: {rot13}")

        # Check if reversed or ROT13 has English words
        reversed_words = re.findall(r'[A-Z]{3,}', reversed_text)
        reversed_english = [w for w in reversed_words if w in WORDS]
        if reversed_english:
            print(f"  → Reversed has English words: {reversed_english}")

        rot13_words = re.findall(r'[A-Z]{3,}', rot13)
        rot13_english = [w for w in rot13_words if w in WORDS]
        if rot13_english:
            print(f"  → ROT13 has English words: {rot13_english}")

        print()

    print("\n4. STATISTICAL ANALYSIS")
    print("="*80 + "\n")

    for ciphertext, section_name in sections:
        freq = Counter(ciphertext)

        # Most and least frequent
        most = freq.most_common(3)
        least = freq.most_common()[-3:]

        print(f"{section_name}:")
        print(f"  Most frequent: {most}")
        print(f"  Least frequent: {least}")
        print(f"  Unique letters: {len(freq)}/{len(ciphertext)}")

        # Check for patterns
        if len(freq) == len(ciphertext):
            print(f"  NOTE: All unique characters - each letter appears exactly once!")
            print(f"        This is consistent with: pure transposition, anagram, or specific construction")

        print()

    print("\n5. LOOKING FOR PATTERN IN GIBBERISH STRUCTURE")
    print("="*80 + "\n")

    # Special analysis: Gap1 contains MPAPGKPVH inside Gap2!
    gap1 = "QAPBZDBKZEL"
    gap2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
    gap3 = "RSPVJWQUL"
    gap4 = "ZOLRKCAYF"

    print("Gap2 contains MPAPGKPVH at the end:")
    print(f"  Gap2: {gap2}")
    print(f"  Index of MPAPGKPVH: {gap2.find('MPAPGKPVH')}")
    print(f"  Gap2 without MPAPGKPVH: {gap2.replace('MPAPGKPVH', '')}")

    print("\nAnalyzing structure:")
    gap2_without_mpapgkpvh = gap2[:29]  # First 29 chars
    print(f"  First 29 chars: {gap2_without_mpapgkpvh}")
    print(f"  Last 9 chars: {gap2[29:]}")

    # Check if these 29 chars are an anagram of something
    anagrams_29 = find_anagrams(gap2_without_mpapgkpvh)
    if anagrams_29:
        print(f"  29 chars anagrams: {anagrams_29}")

    anagrams_9 = find_anagrams(gap2[29:])
    if anagrams_9:
        print(f"  9 chars anagrams: {anagrams_9}")

if __name__ == '__main__':
    main()
