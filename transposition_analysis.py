#!/usr/bin/env python3
"""
Transposition cipher analysis on K4 gibberish sections
"""

from itertools import permutations
import math

# The gibberish sections
SECTIONS = {
    "Section 1": "QAPBZDBKZEL",      # 11 chars
    "Section 2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",  # 38 chars
    "Section 3": "RSPVJWQUL",        # 9 chars
    "Section 4": "ZOLRKCAYF",        # 9 chars
}

# Common English words to look for
COMMON_WORDS = [
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
    "WAS", "ONE", "OUR", "OUT", "DAY", "HAD", "HAS", "HIS", "HOW", "ITS",
    "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "GET",
    "LET", "PUT", "SAY", "SHE", "TOO", "USE", "THAT", "WITH", "HAVE", "THIS",
    "WILL", "YOUR", "FROM", "THEY", "BEEN", "CALL", "COME", "COULD", "FIND",
    "FIRST", "INTO", "JUST", "KNOW", "LIKE", "LONG", "LOOK", "MADE", "MAKE",
    "MORE", "ONLY", "OVER", "PART", "SAID", "SOME", "TAKE", "THAN", "THEM",
    "THEN", "THERE", "THESE", "THING", "TIME", "VERY", "WANT", "WATER", "WHEN",
    "WHERE", "WHICH", "WORD", "WORK", "WOULD", "YEAR", "ZERO", "EAST", "WEST",
    "NORTH", "SOUTH", "CLOCK", "BERLIN", "LAYER", "SHADOW", "UNDER", "ABOVE",
    "BELOW", "GROUND", "SECRET", "HIDDEN", "BURIED", "DECODE", "CODE", "KEY",
    "DARK", "LIGHT", "NIGHT", "SUN", "MOON", "STAR", "DEEP", "SLOW", "FAST",
    "PALIMPSEST", "KRYPTOS", "LANGLEY", "CIA", "SANBORN", "SCULPTURE"
]

def find_words(text):
    """Find common English words in text"""
    found = []
    text_upper = text.upper()
    for word in COMMON_WORDS:
        if len(word) >= 3 and word in text_upper:
            found.append(word)
    return found

def is_potentially_english(text):
    """Check if text has English-like patterns"""
    # Check for common bigrams
    common_bigrams = ["TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND",
                      "TI", "ES", "OR", "TE", "OF", "ED", "IS", "IT", "AL", "AR"]
    count = sum(1 for bg in common_bigrams if bg in text.upper())
    return count >= 2

def rail_fence_decrypt(text, rails):
    """Decrypt rail fence cipher"""
    if rails < 2 or rails > len(text):
        return None

    n = len(text)
    # Create pattern
    pattern = []
    rail = 0
    direction = 1
    for i in range(n):
        pattern.append(rail)
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1

    # Count chars per rail
    counts = [0] * rails
    for r in pattern:
        counts[r] += 1

    # Distribute characters to rails
    rail_chars = []
    idx = 0
    for r in range(rails):
        rail_chars.append(list(text[idx:idx+counts[r]]))
        idx += counts[r]

    # Read off in zigzag
    result = []
    indices = [0] * rails
    for r in pattern:
        if indices[r] < len(rail_chars[r]):
            result.append(rail_chars[r][indices[r]])
            indices[r] += 1

    return ''.join(result)

def columnar_decrypt(text, key_order):
    """Decrypt columnar transposition with given column order"""
    cols = len(key_order)
    rows = math.ceil(len(text) / cols)

    # Calculate chars per column
    full_cols = len(text) % cols
    if full_cols == 0:
        full_cols = cols

    # Create grid
    grid = [[''] * cols for _ in range(rows)]

    # Fill columns in key order
    idx = 0
    for col_num in range(cols):
        # Find which column gets filled next
        actual_col = key_order.index(col_num)
        col_height = rows if actual_col < full_cols else rows - 1
        for row in range(col_height):
            if idx < len(text):
                grid[row][actual_col] = text[idx]
                idx += 1

    # Read row by row
    result = ''.join(''.join(row) for row in grid)
    return result

def read_backwards(text):
    """Read text backwards"""
    return text[::-1]

def read_grid_diagonal(text, cols):
    """Read a grid diagonally"""
    if cols < 2 or cols > len(text):
        return None

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

    # Read diagonals (top-left to bottom-right)
    result = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = d - r
            if 0 <= c < cols and r < len(grid) and c < len(grid[r]) and grid[r][c]:
                result.append(grid[r][c])

    return ''.join(result)

def spiral_read(text, cols):
    """Read grid in spiral pattern"""
    if cols < 2 or cols > len(text):
        return None

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

    result = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1

    while top <= bottom and left <= right:
        # Right
        for c in range(left, right + 1):
            if top < len(grid) and c < len(grid[top]) and grid[top][c]:
                result.append(grid[top][c])
        top += 1

        # Down
        for r in range(top, bottom + 1):
            if r < len(grid) and right < len(grid[r]) and grid[r][right]:
                result.append(grid[r][right])
        right -= 1

        # Left
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if bottom < len(grid) and c < len(grid[bottom]) and grid[bottom][c]:
                    result.append(grid[bottom][c])
            bottom -= 1

        # Up
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if r < len(grid) and left < len(grid[r]) and grid[r][left]:
                    result.append(grid[r][left])
            left += 1

    return ''.join(result)

def zigzag_read(text, cols):
    """Read grid in zigzag (boustrophedon) pattern"""
    if cols < 2 or cols > len(text):
        return None

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

    result = []
    for r in range(rows):
        if r % 2 == 0:
            for c in range(cols):
                if c < len(grid[r]) and grid[r][c]:
                    result.append(grid[r][c])
        else:
            for c in range(cols - 1, -1, -1):
                if c < len(grid[r]) and grid[r][c]:
                    result.append(grid[r][c])

    return ''.join(result)

def skip_cipher(text, skip):
    """Read every nth letter"""
    results = []
    for start in range(skip):
        result = ''.join(text[i] for i in range(start, len(text), skip))
        results.append(result)
    return results

def interleave_halves(text):
    """Split into halves and interleave"""
    mid = len(text) // 2
    first_half = text[:mid]
    second_half = text[mid:]

    results = []

    # Interleave first-second
    r1 = []
    for i in range(max(len(first_half), len(second_half))):
        if i < len(first_half):
            r1.append(first_half[i])
        if i < len(second_half):
            r1.append(second_half[i])
    results.append(''.join(r1))

    # Interleave second-first
    r2 = []
    for i in range(max(len(first_half), len(second_half))):
        if i < len(second_half):
            r2.append(second_half[i])
        if i < len(first_half):
            r2.append(first_half[i])
    results.append(''.join(r2))

    return results

def analyze_section(name, text):
    """Apply all transposition methods to a section"""
    print(f"\n{'='*60}")
    print(f"{name}: {text} ({len(text)} chars)")
    print('='*60)

    results = []

    # 1. Rail fence (depths 2-6)
    print("\n--- Rail Fence Cipher ---")
    for depth in range(2, 7):
        result = rail_fence_decrypt(text, depth)
        if result:
            words = find_words(result)
            english_like = is_potentially_english(result)
            if words or english_like:
                print(f"  Depth {depth}: {result} <- WORDS: {words}")
                results.append(("Rail fence", depth, result, words))
            else:
                print(f"  Depth {depth}: {result}")

    # 2. Columnar transposition (try various column counts)
    print("\n--- Columnar Transposition ---")
    for cols in range(2, min(7, len(text))):
        # Try a few key orders for each column count
        if cols <= 4:  # Try all permutations for small column counts
            for perm in permutations(range(cols)):
                result = columnar_decrypt(text, list(perm))
                words = find_words(result)
                if words:
                    print(f"  Cols {cols}, order {perm}: {result} <- WORDS: {words}")
                    results.append(("Columnar", f"{cols} cols, order {perm}", result, words))
        else:
            # Just try reverse order
            result = columnar_decrypt(text, list(range(cols-1, -1, -1)))
            words = find_words(result)
            if words:
                print(f"  Cols {cols}, reverse: {result} <- WORDS: {words}")

    # 3. Read backwards
    print("\n--- Backwards ---")
    result = read_backwards(text)
    words = find_words(result)
    print(f"  Reversed: {result}")
    if words:
        print(f"    <- WORDS: {words}")
        results.append(("Backwards", "", result, words))

    # 4. Grid diagonal reads
    print("\n--- Diagonal Grid Read ---")
    for cols in range(2, min(8, len(text))):
        result = read_grid_diagonal(text, cols)
        if result:
            words = find_words(result)
            if words:
                print(f"  {cols} cols: {result} <- WORDS: {words}")
                results.append(("Diagonal", cols, result, words))

    # 5. Route ciphers
    print("\n--- Route Ciphers (Spiral) ---")
    for cols in range(2, min(8, len(text))):
        result = spiral_read(text, cols)
        if result:
            words = find_words(result)
            if words:
                print(f"  Spiral {cols} cols: {result} <- WORDS: {words}")
                results.append(("Spiral", cols, result, words))

    print("\n--- Route Ciphers (Zigzag) ---")
    for cols in range(2, min(8, len(text))):
        result = zigzag_read(text, cols)
        if result:
            words = find_words(result)
            if words:
                print(f"  Zigzag {cols} cols: {result} <- WORDS: {words}")
                results.append(("Zigzag", cols, result, words))

    # 6. Skip ciphers
    print("\n--- Skip Ciphers ---")
    for skip in range(2, min(6, len(text))):
        skip_results = skip_cipher(text, skip)
        for i, result in enumerate(skip_results):
            words = find_words(result)
            if words:
                print(f"  Every {skip}th, start {i}: {result} <- WORDS: {words}")
                results.append(("Skip", f"every {skip}, start {i}", result, words))
        # Also check concatenation of all skip results
        combined = ''.join(skip_results)
        if combined != text:
            words = find_words(combined)
            if words:
                print(f"  Skip {skip} combined: {combined} <- WORDS: {words}")

    # 7. Interleave halves
    print("\n--- Interleaved Halves ---")
    interleaved = interleave_halves(text)
    for i, result in enumerate(interleaved):
        words = find_words(result)
        print(f"  Variant {i+1}: {result}")
        if words:
            print(f"    <- WORDS: {words}")
            results.append(("Interleave", i+1, result, words))

    # Summary
    if results:
        print(f"\n*** PROMISING RESULTS for {name} ***")
        for method, param, result, words in results:
            print(f"  {method} ({param}): {result} -> {words}")

    return results

def main():
    print("TRANSPOSITION CIPHER ANALYSIS")
    print("K4 Gibberish Sections")
    print("="*60)

    all_results = {}

    for name, text in SECTIONS.items():
        results = analyze_section(name, text)
        if results:
            all_results[name] = results

    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY - ALL ENGLISH WORDS FOUND")
    print("="*60)

    if all_results:
        for name, results in all_results.items():
            print(f"\n{name}:")
            for method, param, result, words in results:
                print(f"  {method} ({param}): {words} in '{result}'")
    else:
        print("\nNo clear English words found in any transposition.")

    # Also try combined sections
    print("\n" + "="*60)
    print("TRYING COMBINED GIBBERISH SECTIONS")
    print("="*60)

    combined = "".join(SECTIONS.values())
    print(f"\nCombined: {combined} ({len(combined)} chars)")

    # Quick check on combined
    print("\n--- Combined Backwards ---")
    result = read_backwards(combined)
    words = find_words(result)
    print(f"  {result}")
    if words:
        print(f"  WORDS: {words}")

if __name__ == "__main__":
    main()
