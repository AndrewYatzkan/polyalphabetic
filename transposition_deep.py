#!/usr/bin/env python3
"""
Deep transposition cipher analysis - looking for any readable patterns
"""

from itertools import permutations
import math
import re

# The gibberish sections
SECTIONS = {
    "Section 1": "QAPBZDBKZEL",      # 11 chars
    "Section 2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",  # 38 chars
    "Section 3": "RSPVJWQUL",        # 9 chars
    "Section 4": "ZOLRKCAYF",        # 9 chars
}

# Load a comprehensive word list
def load_words():
    words = set()
    # Try system dictionary
    try:
        with open('/usr/share/dict/words', 'r') as f:
            for line in f:
                word = line.strip().upper()
                if 3 <= len(word) <= 15:
                    words.add(word)
    except:
        pass

    # Add K4-related words
    k4_words = [
        "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
        "WAS", "ONE", "OUR", "OUT", "DAY", "HAD", "HAS", "HIS", "HOW", "ITS",
        "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY", "BEEN",
        "EAST", "WEST", "NORTH", "SOUTH", "CLOCK", "BERLIN", "LAYER", "SHADOW",
        "UNDER", "ABOVE", "BELOW", "GROUND", "SECRET", "HIDDEN", "BURIED",
        "DEEP", "SLOW", "FAST", "DARK", "LIGHT", "NIGHT", "SUN", "MOON",
        "PALIMPSEST", "KRYPTOS", "LANGLEY", "CIA", "SANBORN", "SCULPTURE",
        "TIME", "PLACE", "HERE", "THERE", "WHERE", "WHEN", "WHO", "WHAT",
        "VIRTUALLY", "INVISIBLE", "IQLUSION", "ILLUSION", "BURIED", "UNKNOWN",
        "DESPERATELY", "KNOW", "EXACT", "LOCATION", "ONLY", "WW", "COORDINATES",
        "FORTY", "FIFTY", "SIXTY", "DEGREES", "MINUTES", "SECONDS",
        "LAT", "LON", "GPS", "MAP", "POINT", "SITE", "DIG", "FIND",
        "KEY", "CODE", "CIPHER", "DECODE", "DECRYPT", "MESSAGE", "PLAIN",
        "ROCK", "CLAY", "SOIL", "EARTH", "FEET", "METER", "YARD", "INCH"
    ]
    words.update(k4_words)
    return words

WORDS = load_words()

def find_all_words(text, min_len=3):
    """Find all dictionary words as substrings"""
    found = []
    text_upper = text.upper()
    for word in WORDS:
        if len(word) >= min_len and word in text_upper:
            # Find position
            pos = text_upper.find(word)
            found.append((word, pos))
    # Sort by length descending
    found.sort(key=lambda x: -len(x[0]))
    return found

def rail_fence_decrypt(text, rails):
    """Decrypt rail fence cipher"""
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

def columnar_decrypt(text, num_cols, key_order):
    """Decrypt columnar transposition"""
    rows = math.ceil(len(text) / num_cols)

    # Calculate column heights
    short_cols = num_cols * rows - len(text)
    col_heights = [rows if i < num_cols - short_cols else rows - 1 for i in range(num_cols)]

    # Reorder based on key
    reordered_heights = [col_heights[key_order.index(i)] for i in range(num_cols)]

    # Fill columns
    columns = []
    idx = 0
    for i in range(num_cols):
        h = reordered_heights[i]
        columns.append(text[idx:idx+h])
        idx += h

    # Reorder columns back
    final_cols = [''] * num_cols
    for i, col_num in enumerate(key_order):
        final_cols[col_num] = columns[i]

    # Read rows
    result = []
    for r in range(rows):
        for c in range(num_cols):
            if r < len(final_cols[c]):
                result.append(final_cols[c][r])

    return ''.join(result)

def every_nth(text, n, offset=0):
    """Extract every nth character starting at offset"""
    return ''.join(text[i] for i in range(offset, len(text), n))

def read_in_columns(text, cols):
    """Write row-by-row, read column-by-column"""
    rows = math.ceil(len(text) / cols)
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)

    # Read column by column
    result = []
    for c in range(cols):
        for r in range(rows):
            if grid[r][c]:
                result.append(grid[r][c])
    return ''.join(result)

def read_in_rows_from_columns(text, cols):
    """Write column-by-column, read row-by-row"""
    rows = math.ceil(len(text) / cols)
    # Fill column by column
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    idx = 0
    for c in range(cols):
        for r in range(rows):
            if idx < len(text):
                grid[r][c] = text[idx]
                idx += 1

    # Read row by row
    result = ''.join(''.join(row) for row in grid)
    return result

def scytale(text, cols):
    """Scytale cipher - wrap around a rod"""
    return read_in_rows_from_columns(text, cols)

def analyze_section(name, text):
    """Comprehensive transposition analysis"""
    print(f"\n{'='*70}")
    print(f"{name}: {text} ({len(text)} chars)")
    print('='*70)

    all_results = []

    # Method 1: Simple backwards
    result = text[::-1]
    words = find_all_words(result)
    if words:
        all_results.append(("Reversed", result, words))

    # Method 2: Rail fence 2-8
    for depth in range(2, 9):
        result = rail_fence_decrypt(text, depth)
        if result:
            words = find_all_words(result)
            if words:
                all_results.append((f"Rail fence depth {depth}", result, words))

    # Method 3: Columnar with all permutations up to 5 columns
    for cols in range(2, min(6, len(text))):
        for perm in permutations(range(cols)):
            result = columnar_decrypt(text, cols, list(perm))
            words = find_all_words(result)
            if words:
                all_results.append((f"Columnar {cols} cols order {perm}", result, words))

    # Method 4: Read in columns (transposition)
    for cols in range(2, min(12, len(text))):
        result = read_in_columns(text, cols)
        words = find_all_words(result)
        if words:
            all_results.append((f"Grid {cols} cols read by col", result, words))

        result = read_in_rows_from_columns(text, cols)
        words = find_all_words(result)
        if words:
            all_results.append((f"Scytale {cols} cols", result, words))

    # Method 5: Skip ciphers
    for skip in range(2, min(8, len(text))):
        for offset in range(skip):
            result = every_nth(text, skip, offset)
            words = find_all_words(result)
            if words:
                all_results.append((f"Every {skip}th from {offset}", result, words))

    # Method 6: Pairs swap
    pairs_swap = []
    for i in range(0, len(text)-1, 2):
        pairs_swap.append(text[i+1])
        pairs_swap.append(text[i])
    if len(text) % 2:
        pairs_swap.append(text[-1])
    result = ''.join(pairs_swap)
    words = find_all_words(result)
    if words:
        all_results.append(("Pair swap", result, words))

    # Method 7: Triple rotations
    for i in range(0, len(text)-2, 3):
        pass  # Skip for now

    # Print results
    if all_results:
        # Deduplicate and sort by longest word found
        seen = set()
        unique_results = []
        for method, result, words in all_results:
            key = (result, tuple(w[0] for w in words))
            if key not in seen:
                seen.add(key)
                unique_results.append((method, result, words))

        # Sort by longest word
        unique_results.sort(key=lambda x: -max(len(w[0]) for w in x[2]))

        print(f"\n*** {len(unique_results)} RESULTS WITH WORDS ***")
        for method, result, words in unique_results[:20]:  # Top 20
            word_str = ', '.join(f"{w[0]}@{w[1]}" for w in words[:5])
            print(f"  {method}:")
            print(f"    {result}")
            print(f"    Words: {word_str}")
    else:
        print("\n  No dictionary words found")

    return all_results

def check_anagram(text):
    """Check what words could be formed from these letters"""
    from collections import Counter
    text_count = Counter(text.upper())

    matching = []
    for word in WORDS:
        if len(word) >= 4:
            word_count = Counter(word)
            if all(text_count.get(c, 0) >= n for c, n in word_count.items()):
                matching.append(word)

    # Sort by length
    matching.sort(key=lambda x: -len(x))
    return matching[:30]

def main():
    print("DEEP TRANSPOSITION ANALYSIS")
    print("="*70)

    for name, text in SECTIONS.items():
        analyze_section(name, text)

        print(f"\n  Possible anagram words from letters:")
        anagrams = check_anagram(text)
        print(f"    {', '.join(anagrams[:15])}")

    # Combined analysis
    print("\n" + "="*70)
    print("COMBINED SECTIONS")
    print("="*70)

    combined = "".join(SECTIONS.values())
    print(f"\nAll gibberish: {combined}")
    print(f"Length: {len(combined)}")

    # Check combined anagrams
    print("\nLongest words possible from combined letters:")
    anagrams = check_anagram(combined)
    print(f"  {', '.join(anagrams[:20])}")

if __name__ == "__main__":
    main()
