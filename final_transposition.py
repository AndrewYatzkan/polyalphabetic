#!/usr/bin/env python3
"""
Final comprehensive transposition analysis
Focus on finding complete readable English
"""

from itertools import permutations
from collections import Counter
import re

SECTIONS = {
    "Sec1": "QAPBZDBKZEL",
    "Sec2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",
    "Sec3": "RSPVJWQUL",
    "Sec4": "ZOLRKCAYF",
}

# Extended word list
WORDS = set()
try:
    with open('/usr/share/dict/words', 'r') as f:
        for line in f:
            word = line.strip().upper()
            if 3 <= len(word) <= 12:
                WORDS.add(word)
except:
    pass

# Add common/K4 words
K4_WORDS = [
    "FOR", "THE", "AND", "CLAY", "ROCK", "FORTY", "FIFTY", "SIXTY", "NORTH",
    "SOUTH", "EAST", "WEST", "DEGREES", "FEET", "UNDER", "ABOVE", "BELOW",
    "LAYER", "SHADOW", "CLOCK", "BERLIN", "DEEP", "DARK", "TIME", "HERE",
    "THERE", "WHERE", "WHAT", "WHEN", "CODE", "KEY", "SITE", "POINT", "MAP",
    "GPS", "LAT", "LON", "DIG", "FIND", "SECRET", "HIDDEN", "BURIED"
]
WORDS.update(K4_WORDS)

def find_words_in_text(text):
    """Find all words that appear as substrings"""
    found = []
    text = text.upper()
    for word in WORDS:
        if len(word) >= 3 and word in text:
            pos = text.find(word)
            found.append((word, pos, len(word)))
    found.sort(key=lambda x: (-x[2], x[1]))  # Sort by length desc, then position
    return found

def try_all_complete_readings(text, name):
    """Try to find complete English readings"""
    n = len(text)
    print(f"\n{name}: {text} ({n} chars)")
    print("-" * 50)

    best = []

    # 1. All simple transpositions
    methods = []

    # Reversed
    methods.append(("reversed", text[::-1]))

    # Rail fence
    for rails in range(2, 7):
        dec = rail_fence_decrypt(text, rails)
        if dec:
            methods.append((f"rail {rails}", dec))

    # Grid reads
    for cols in range(2, min(10, n)):
        rows = (n + cols - 1) // cols

        # Fill row-wise, read column-wise
        grid = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if idx < n:
                    row.append(text[idx])
                    idx += 1
                else:
                    row.append('')
            grid.append(row)

        # Read by columns L-R
        col_lr = ''.join(grid[r][c] for c in range(cols) for r in range(rows)
                        if r < len(grid) and c < len(grid[r]) and grid[r][c])
        methods.append((f"grid {rows}x{cols} col-LR", col_lr))

        # Read by columns R-L
        col_rl = ''.join(grid[r][c] for c in range(cols-1, -1, -1) for r in range(rows)
                        if r < len(grid) and c < len(grid[r]) and grid[r][c])
        methods.append((f"grid {rows}x{cols} col-RL", col_rl))

        # Read rows backwards
        row_rev = ''.join(grid[r][c] for r in range(rows-1, -1, -1) for c in range(cols)
                         if r < len(grid) and c < len(grid[r]) and grid[r][c])
        methods.append((f"grid {rows}x{cols} row-rev", row_rev))

    # Skip patterns
    for skip in range(2, min(7, n)):
        for start in range(skip):
            nth = text[start::skip]
            methods.append((f"skip {skip} start {start}", nth))

        # All skip parts concatenated
        all_parts = [text[s::skip] for s in range(skip)]
        combined = ''.join(all_parts)
        methods.append((f"skip {skip} all-concat", combined))

        # Reverse each part
        rev_parts = ''.join(p[::-1] for p in all_parts)
        methods.append((f"skip {skip} rev-parts", rev_parts))

    # Pair swap
    swapped = ''.join(text[i+1:i+2] + text[i:i+1] for i in range(0, n, 2))
    methods.append(("pair-swap", swapped))

    # Check each method for words
    results_with_words = []
    for method, result in methods:
        words = find_words_in_text(result)
        if words:
            results_with_words.append((method, result, words))

    # Sort by longest word found
    results_with_words.sort(key=lambda x: -max(w[2] for w in x[2]))

    if results_with_words:
        print(f"\n  Methods producing words:")
        seen = set()
        for method, result, words in results_with_words[:15]:
            if result not in seen:
                seen.add(result)
                word_list = [w[0] for w in words[:5]]
                print(f"    {method:25s}: {result}")
                print(f"    {'':25s}  -> Words: {word_list}")
    else:
        print("  No dictionary words found in any transposition")

    return results_with_words

def rail_fence_decrypt(text, rails):
    if rails < 2 or rails > len(text):
        return None

    n = len(text)
    pattern = []
    rail = 0
    direction = 1
    for i in range(n):
        pattern.append(rail)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1

    counts = [0] * rails
    for r in pattern:
        counts[r] += 1

    rail_chars = []
    idx = 0
    for r in range(rails):
        rail_chars.append(list(text[idx:idx+counts[r]]))
        idx += counts[r]

    result = []
    indices = [0] * rails
    for r in pattern:
        if indices[r] < len(rail_chars[r]):
            result.append(rail_chars[r][indices[r]])
            indices[r] += 1

    return ''.join(result)

def try_permutation_reconstruction(text, name):
    """For short texts, try finding word-forming permutations"""
    if len(text) > 11:
        return

    print(f"\n  Permutation word search for {name}:")

    # Find all possible words from letters
    letter_pool = Counter(text.upper())

    possible_words = []
    for word in WORDS:
        if len(word) >= 4:
            word_count = Counter(word)
            if all(letter_pool.get(c, 0) >= n for c, n in word_count.items()):
                possible_words.append(word)

    possible_words.sort(key=lambda x: -len(x))

    print(f"    Possible words from letters: {possible_words[:15]}")

    # For very short texts, check if entire text anagrams to a word
    if len(text) <= 9:
        # Check single words
        for word in WORDS:
            if len(word) == len(text):
                if Counter(word) == Counter(text.upper()):
                    print(f"    ANAGRAM MATCH: {text} -> {word}")

def main():
    print("=" * 60)
    print("FINAL COMPREHENSIVE TRANSPOSITION ANALYSIS")
    print("=" * 60)

    for name, text in SECTIONS.items():
        try_all_complete_readings(text, name)
        try_permutation_reconstruction(text, name)

    # Combined analysis
    print("\n" + "=" * 60)
    print("COMBINED GIBBERISH ANALYSIS")
    print("=" * 60)

    combined = "".join(SECTIONS.values())
    print(f"\nCombined: {combined}")
    print(f"Length: {len(combined)}")

    # What longest words can be spelled?
    letter_pool = Counter(combined)
    print(f"\nLetter inventory: {dict(letter_pool)}")

    # Find all spellable words
    spellable = []
    for word in WORDS:
        if len(word) >= 5:
            word_count = Counter(word)
            if all(letter_pool.get(c, 0) >= n for c, n in word_count.items()):
                spellable.append(word)

    spellable.sort(key=lambda x: -len(x))
    print(f"\nLongest spellable words: {spellable[:25]}")

    # Check for coordinate-like patterns
    print("\n" + "=" * 60)
    print("COORDINATE PATTERN CHECK")
    print("=" * 60)

    # Does any section contain number-like letter patterns?
    # In some ciphers, numbers are spelled or encoded
    for name, text in SECTIONS.items():
        # Check for sequences that might be number words
        num_patterns = ["ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
                       "EIGHT", "NINE", "TEN", "FORTY", "FIFTY", "SIXTY"]
        found = []
        for pattern in num_patterns:
            if pattern in text:
                found.append(pattern)
        if found:
            print(f"{name}: Contains number words: {found}")

if __name__ == "__main__":
    main()
