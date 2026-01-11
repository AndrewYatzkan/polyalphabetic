#!/usr/bin/env python3
"""
Comprehensive hidden word extraction from K4 gibberish using multiple methods.
"""

import re
from collections import defaultdict

# K4 Gibberish
K4_TEXT = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

# Load word lists
def load_english_words():
    """Load English dictionary words"""
    try:
        with open('/home/user/polyalphabetic/OxfordEnglishWords.txt', 'r') as f:
            words = set(w.strip().upper() for w in f.readlines() if len(w.strip()) >= 3)
        return words
    except:
        return set()

# Extended word lists for specialized terms
KRYPTOS_WORDS = {
    'PALIMPSEST', 'ABSCISSA', 'SHADOW', 'SANBORN', 'KRYPTOS', 'DECRYPT',
    'CIPHER', 'KEY', 'BERLIN', 'CLOCK', 'BEARING', 'COORDINATES',
    'UNDERGROUND', 'LUCIDITY', 'PASSAGE', 'SLOWLY', 'DESPARATELY'
}

PLACE_NAMES = {
    'BERLIN', 'CAIRO', 'EGYPT', 'CIA', 'ENGLAND', 'FRANCE', 'GERMANY',
    'RUSSIA', 'MEXICO', 'CHINA', 'JAPAN', 'LONDON', 'PARIS', 'ROME',
    'NEW', 'YORK', 'WALL', 'PRAGUE'
}

GERMAN_WORDS = {
    'WALL', 'UFER', 'RITTER', 'STADT', 'ZEIT', 'BEAR', 'BIER', 'SCHIRM',
    'SCHLOSS', 'TURM', 'FLUSS', 'WALD', 'BERG'
}

def find_words_in_text(text, word_list, min_length=3):
    """Find words from word_list in text"""
    found = {}
    for word in word_list:
        if len(word) >= min_length and word in text:
            pos = text.find(word)
            if pos >= 0:
                found[word] = pos
    return found

def extract_every_nth(text, n):
    """Extract every nth character"""
    return text[::n]

def reverse_reading(text):
    """Read the text in reverse"""
    return text[::-1]

def snake_reading(text, cols=None):
    """Read text in boustrophedon (snake) pattern"""
    if cols is None:
        cols = 10  # Try different column widths
    rows = (len(text) + cols - 1) // cols
    grid = []
    idx = 0
    for r in range(rows):
        row = []
        for c in range(cols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
        grid.append(row)

    # Read snake pattern
    result = ""
    for r in range(len(grid)):
        if r % 2 == 0:
            result += ''.join(grid[r])
        else:
            result += ''.join(reversed(grid[r]))
    return result

def diagonal_reading(text, grid_size=None):
    """Read diagonals from grid arrangement"""
    if grid_size is None:
        # Try square root
        size = int(len(text) ** 0.5)
        if size * size < len(text):
            size += 1
    else:
        size = grid_size

    # Create grid
    grid = []
    idx = 0
    for r in range(size):
        row = []
        for c in range(size):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)

    # Read diagonals
    result = ""
    # Main diagonal
    for i in range(size):
        if i < len(grid) and i < len(grid[i]) and grid[i][i]:
            result += grid[i][i]
    return result

def first_letter_segments(text, segment_size=5):
    """Extract first letter of each segment"""
    result = ""
    for i in range(0, len(text), segment_size):
        result += text[i]
    return result

def prime_positions(text):
    """Extract characters at prime positions"""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]
    result = ""
    for p in primes:
        if p < len(text):
            result += text[p]
    return result

def fibonacci_positions(text):
    """Extract characters at Fibonacci positions"""
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    result = ""
    seen = set()
    for f in fib:
        if f < len(text) and f not in seen:
            result += text[f]
            seen.add(f)
    return result

def interleave_gaps(text, gap1_start=0, gap2_start=1, gap3_start=2, gap4_start=3):
    """Interleave different gap patterns"""
    results = {}

    # Extract gap patterns
    gap1 = text[gap1_start::4]
    gap2 = text[gap2_start::4]
    gap3 = text[gap3_start::4]
    gap4 = text[gap4_start::4]

    # Different interleave combinations
    results['gap1+gap3'] = gap1 + gap3
    results['gap2+gap4'] = gap2 + gap4
    results['gap1+gap2'] = gap1 + gap2
    results['gap3+gap4'] = gap3 + gap4
    results['gap1+gap2+gap3'] = gap1 + gap2 + gap3
    results['gap1+gap2+gap3+gap4'] = gap1 + gap2 + gap3 + gap4

    # Interleaved versions
    interleaved1 = ""
    for i in range(max(len(gap1), len(gap3))):
        if i < len(gap1):
            interleaved1 += gap1[i]
        if i < len(gap3):
            interleaved1 += gap3[i]
    results['interleaved_gap1_gap3'] = interleaved1

    return results

def analyze_grid_arrangements(text):
    """Try different grid arrangements and extract patterns"""
    results = {}

    # Try common grid sizes
    for cols in [5, 6, 7, 8, 9, 10, 11, 12, 13]:
        rows = (len(text) + cols - 1) // cols

        # Create grid
        grid = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                if idx < len(text):
                    row.append(text[idx])
                    idx += 1
            grid.append(row)

        # Read columns
        for c in range(cols):
            col_text = ""
            for r in range(len(grid)):
                if c < len(grid[r]):
                    col_text += grid[r][c]
            if col_text:
                results[f'grid_{cols}x_col_{c}'] = col_text

        # Read rows
        for r in range(len(grid)):
            results[f'grid_{cols}x_row_{r}'] = ''.join(grid[r])

    return results

def main():
    print(f"K4 GIBBERISH ANALYSIS")
    print(f"Text: {K4_TEXT}")
    print(f"Length: {len(K4_TEXT)}")
    print("=" * 80)

    # Load word lists
    english_words = load_english_words()
    print(f"Loaded {len(english_words)} English words")
    all_words = english_words | KRYPTOS_WORDS | PLACE_NAMES | GERMAN_WORDS
    print(f"Total words in lookup: {len(all_words)}")
    print("=" * 80)

    findings = defaultdict(list)

    # Method 1: Every Nth letter
    print("\n1. EVERY NTH LETTER EXTRACTION:")
    for n in range(2, 12):
        extracted = extract_every_nth(K4_TEXT, n)
        print(f"   Every {n}th: {extracted}")
        found = find_words_in_text(extracted, all_words)
        if found:
            for word, pos in found.items():
                findings['Every Nth'].append((n, word, extracted, pos))
                print(f"      FOUND: {word} at position {pos} in extracted text")

    # Method 2: Reverse reading
    print("\n2. REVERSE READING:")
    reversed_text = reverse_reading(K4_TEXT)
    print(f"   Reversed: {reversed_text}")
    found = find_words_in_text(reversed_text, all_words)
    if found:
        for word, pos in found.items():
            findings['Reverse'].append((word, reversed_text, pos))
            print(f"      FOUND: {word} at position {pos}")

    # Method 3: Snake reading
    print("\n3. SNAKE/BOUSTROPHEDON READING:")
    for cols in [6, 7, 8, 9, 10, 11]:
        snake_text = snake_reading(K4_TEXT, cols)
        print(f"   Snake ({cols} cols): {snake_text}")
        found = find_words_in_text(snake_text, all_words)
        if found:
            for word, pos in found.items():
                findings['Snake'].append((cols, word, snake_text, pos))
                print(f"      FOUND: {word} at position {pos}")

    # Method 4: Diagonal reading
    print("\n4. DIAGONAL READING:")
    for size in [8, 9, 10, 11]:
        diag_text = diagonal_reading(K4_TEXT, size)
        print(f"   Diagonal ({size}x{size}): {diag_text}")
        found = find_words_in_text(diag_text, all_words)
        if found:
            for word, pos in found.items():
                findings['Diagonal'].append((size, word, diag_text, pos))
                print(f"      FOUND: {word} at position {pos}")

    # Method 5: First letter of segments
    print("\n5. FIRST LETTER OF SEGMENTS:")
    for seg_size in [3, 4, 5, 6, 7]:
        seg_text = first_letter_segments(K4_TEXT, seg_size)
        print(f"   Segment size {seg_size}: {seg_text}")
        found = find_words_in_text(seg_text, all_words)
        if found:
            for word, pos in found.items():
                findings['First Letter'].append((seg_size, word, seg_text, pos))
                print(f"      FOUND: {word} at position {pos}")

    # Method 6: Position-based extraction
    print("\n6. POSITION-BASED EXTRACTION:")
    prime_text = prime_positions(K4_TEXT)
    print(f"   Prime positions: {prime_text}")
    found = find_words_in_text(prime_text, all_words)
    if found:
        for word, pos in found.items():
            findings['Primes'].append((word, prime_text, pos))
            print(f"      FOUND: {word} at position {pos}")

    fib_text = fibonacci_positions(K4_TEXT)
    print(f"   Fibonacci positions: {fib_text}")
    found = find_words_in_text(fib_text, all_words)
    if found:
        for word, pos in found.items():
            findings['Fibonacci'].append((word, fib_text, pos))
            print(f"      FOUND: {word} at position {pos}")

    # Method 7 & 8: Gap interleaving
    print("\n7-8. GAP INTERLEAVING:")
    gap_results = interleave_gaps(K4_TEXT)
    for key, text in gap_results.items():
        print(f"   {key}: {text}")
        found = find_words_in_text(text, all_words)
        if found:
            for word, pos in found.items():
                findings['Gap Interleave'].append((key, word, text, pos))
                print(f"      FOUND: {word} at position {pos}")

    # Grid arrangements
    print("\n9. GRID ARRANGEMENTS (Columns/Rows):")
    grid_results = analyze_grid_arrangements(K4_TEXT)
    for key, text in sorted(grid_results.items()):
        found = find_words_in_text(text, all_words)
        if found:
            for word, pos in found.items():
                findings['Grid'].append((key, word, text, pos))
                print(f"   {key}: FOUND {word} at position {pos}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY OF FINDINGS:")
    print("=" * 80)

    if findings:
        for method, results in findings.items():
            print(f"\n{method}:")
            for result in results:
                print(f"  {result}")
    else:
        print("No hidden words found using standard extraction methods.")

    # Additional analysis - look for partial matches
    print("\n" + "=" * 80)
    print("PARTIAL MATCHES (3+ consecutive letters from words):")
    print("=" * 80)

    partial_matches = defaultdict(list)
    for word in all_words:
        if len(word) >= 4:
            if word in K4_TEXT:
                partial_matches['Direct'].append(word)
            if word[:3] in K4_TEXT:
                partial_matches['3-letter prefix'].append(word)
            if word[-3:] in K4_TEXT:
                partial_matches['3-letter suffix'].append(word)

            # Check in reversed
            if word in K4_TEXT[::-1]:
                partial_matches['Reversed'].append(word)

    for key, words in partial_matches.items():
        if words:
            print(f"\n{key}:")
            for word in sorted(set(words))[:10]:  # Limit output
                print(f"  {word}")

if __name__ == "__main__":
    main()
