#!/usr/bin/env python3
"""
Specific pattern analysis for K4 gibberish
"""

from itertools import permutations
from collections import Counter

SECTIONS = {
    "Sec1": "QAPBZDBKZEL",      # 11 chars
    "Sec2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",  # 38 chars
    "Sec3": "RSPVJWQUL",        # 9 chars
    "Sec4": "ZOLRKCAYF",        # 9 chars
}

def factor_analysis():
    """Analyze lengths for transposition clues"""
    print("LENGTH FACTOR ANALYSIS")
    print("="*50)
    for name, text in SECTIONS.items():
        n = len(text)
        factors = [i for i in range(2, n+1) if n % i == 0]
        print(f"{name}: {n} chars, factors: {factors}")

def try_grid_reads(text, rows, cols):
    """Try all ways to read a grid"""
    if rows * cols < len(text):
        return []

    # Fill grid row by row
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append(' ')
        grid.append(row)

    results = []

    # Read column by column
    r1 = ''.join(grid[r][c] for c in range(cols) for r in range(rows) if grid[r][c] != ' ')
    results.append(("cols L-R", r1))

    # Read column by column R-L
    r2 = ''.join(grid[r][c] for c in range(cols-1, -1, -1) for r in range(rows) if grid[r][c] != ' ')
    results.append(("cols R-L", r2))

    # Read column by column, bottom to top
    r3 = ''.join(grid[r][c] for c in range(cols) for r in range(rows-1, -1, -1) if grid[r][c] != ' ')
    results.append(("cols B-T", r3))

    # Read rows bottom to top
    r4 = ''.join(grid[r][c] for r in range(rows-1, -1, -1) for c in range(cols) if grid[r][c] != ' ')
    results.append(("rows B-T", r4))

    # Diagonal
    r5 = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = d - r
            if 0 <= c < cols and grid[r][c] != ' ':
                r5.append(grid[r][c])
    results.append(("diag", ''.join(r5)))

    # Anti-diagonal
    r6 = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = cols - 1 - d + r
            if 0 <= c < cols and grid[r][c] != ' ':
                r6.append(grid[r][c])
    results.append(("anti-diag", ''.join(r6)))

    return results

def double_columnar(text, cols1, cols2):
    """Apply columnar transposition twice"""
    import math

    # First transposition
    rows1 = math.ceil(len(text) / cols1)
    grid1 = []
    idx = 0
    for r in range(rows1):
        row = []
        for c in range(cols1):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid1.append(row)

    # Read columns
    mid = ''.join(grid1[r][c] for c in range(cols1) for r in range(rows1) if r < len(grid1) and c < len(grid1[r]) and grid1[r][c])

    # Second transposition
    rows2 = math.ceil(len(mid) / cols2)
    grid2 = []
    idx = 0
    for r in range(rows2):
        row = []
        for c in range(cols2):
            if idx < len(mid):
                row.append(mid[idx])
                idx += 1
            else:
                row.append('')
        grid2.append(row)

    result = ''.join(grid2[r][c] for c in range(cols2) for r in range(rows2) if r < len(grid2) and c < len(grid2[r]) and grid2[r][c])
    return result

def check_for_words(text):
    """Check for embedded words"""
    words_3 = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
               "WAS", "ONE", "OUR", "OUT", "DAY", "HAD", "HAS", "HIS", "HOW", "ITS",
               "DIG", "MAP", "KEY", "LAT", "LON", "SUN", "CIA", "GPS"]
    words_4 = ["THAT", "WITH", "HAVE", "THIS", "WILL", "FROM", "THEY", "BEEN",
               "EAST", "WEST", "CLAY", "ROCK", "DEEP", "DARK", "TIME", "HERE",
               "CODE", "FIND", "SITE", "FEET", "YARD", "INCH", "SLOW", "FAST"]
    words_5 = ["NORTH", "SOUTH", "CLOCK", "LAYER", "UNDER", "ABOVE", "BELOW",
               "EARTH", "POINT", "PLACE", "WHERE", "THERE", "EXACT", "LIGHT"]
    words_6 = ["BERLIN", "SHADOW", "SECRET", "HIDDEN", "BURIED", "GROUND",
               "DEGREE", "MINUTE", "SECOND", "CIPHER", "DECODE"]

    found = []
    text = text.upper()
    for word in words_3 + words_4 + words_5 + words_6:
        if word in text:
            found.append(word)
    return found

def analyze_section(name, text):
    """Deep analysis of one section"""
    print(f"\n{'='*60}")
    print(f"{name}: {text} ({len(text)} chars)")
    print('='*60)

    results_with_words = []

    # Try various grid dimensions
    n = len(text)
    for rows in range(2, n):
        for cols in range(2, n):
            if rows * cols >= n and rows * cols <= n + cols:  # Allow some padding
                grid_results = try_grid_reads(text, rows, cols)
                for method, result in grid_results:
                    words = check_for_words(result)
                    if words:
                        results_with_words.append((f"Grid {rows}x{cols} {method}", result, words))

    # Try double transposition
    for cols1 in range(2, min(8, n)):
        for cols2 in range(2, min(8, n)):
            result = double_columnar(text, cols1, cols2)
            words = check_for_words(result)
            if words:
                results_with_words.append((f"Double trans {cols1}x{cols2}", result, words))

    # Skip cipher combinations
    for skip in range(2, 6):
        # Collect every nth, then reverse
        parts = [text[i::skip] for i in range(skip)]
        for perm in permutations(range(skip)):
            combined = ''.join(parts[i] for i in perm)
            words = check_for_words(combined)
            if words:
                results_with_words.append((f"Skip {skip} order {perm}", combined, words))

            # Also try each part reversed
            rev_combined = ''.join(parts[i][::-1] for i in perm)
            words = check_for_words(rev_combined)
            if words:
                results_with_words.append((f"Skip {skip} order {perm} rev", rev_combined, words))

    # Print results
    if results_with_words:
        print(f"\n*** FOUND {len(results_with_words)} RESULTS WITH WORDS ***")
        # Deduplicate
        seen = set()
        for method, result, words in results_with_words:
            if result not in seen:
                seen.add(result)
                print(f"\n  {method}:")
                print(f"    {result}")
                print(f"    Words: {words}")
    else:
        print("\n  No words found")

def look_for_phrase(text, phrase):
    """Check if letters of text could spell phrase"""
    text_count = Counter(text.upper())
    phrase_letters = phrase.upper().replace(" ", "")
    phrase_count = Counter(phrase_letters)

    missing = []
    for letter, count in phrase_count.items():
        if text_count.get(letter, 0) < count:
            missing.append(f"{letter}:{count - text_count.get(letter, 0)}")

    if missing:
        return False, missing
    return True, []

def main():
    factor_analysis()

    for name, text in SECTIONS.items():
        analyze_section(name, text)

    # Check if combined could spell interesting phrases
    combined = "".join(SECTIONS.values())
    print("\n" + "="*60)
    print("PHRASE POSSIBILITY CHECK")
    print("="*60)
    print(f"\nCombined letters: {combined}")
    print(f"Letter counts: {dict(Counter(combined))}")

    phrases = [
        "DEGREES LATITUDE LONGITUDE",
        "BURIED BELOW GROUND",
        "SECRET LAYER UNDERNEATH",
        "SHADOW CLOCK TIME",
        "LANGLEY SCULPTURE SECRET",
        "DECODE CIPHER MESSAGE",
        "FORTY DEGREES NORTH",
        "DIG HERE BELOW",
    ]

    for phrase in phrases:
        possible, missing = look_for_phrase(combined, phrase)
        if possible:
            print(f"  POSSIBLE: '{phrase}'")
        else:
            print(f"  Cannot spell '{phrase}' - missing: {missing}")

if __name__ == "__main__":
    main()
