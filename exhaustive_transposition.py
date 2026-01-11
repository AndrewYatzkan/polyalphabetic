#!/usr/bin/env python3
"""
Exhaustive transposition analysis with pattern scoring
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

# English letter frequency order
ENGLISH_FREQ = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

# Common English bigrams
COMMON_BIGRAMS = ["TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND",
                  "TI", "ES", "OR", "TE", "OF", "ED", "IS", "IT", "AL", "AR",
                  "ST", "TO", "NT", "NG", "SE", "HA", "AS", "OU", "IO", "LE",
                  "VE", "CO", "ME", "DE", "HI", "RI", "RO", "IC", "NE", "EA"]

# Common trigrams
COMMON_TRIGRAMS = ["THE", "AND", "ING", "ION", "TIO", "ENT", "FOR", "ERE",
                   "HER", "ATE", "VER", "HIS", "OUR", "THA", "HAT"]

def score_english(text):
    """Score how English-like a text is"""
    text = text.upper()
    score = 0

    # Bigram scoring
    for i in range(len(text) - 1):
        bigram = text[i:i+2]
        if bigram in COMMON_BIGRAMS[:20]:
            score += 3
        elif bigram in COMMON_BIGRAMS[20:]:
            score += 1

    # Trigram scoring
    for i in range(len(text) - 2):
        trigram = text[i:i+3]
        if trigram in COMMON_TRIGRAMS:
            score += 5

    # Penalize rare letters
    rare = "QXJZ"
    for c in text:
        if c in rare:
            score -= 2

    # Bonus for common letter frequency match
    if text:
        freq = Counter(text)
        most_common = freq.most_common(3)
        common_letters = [x[0] for x in most_common]
        if 'E' in common_letters:
            score += 3
        if 'T' in common_letters:
            score += 2
        if 'A' in common_letters:
            score += 2

    return score

def apply_permutation(text, perm):
    """Apply a position permutation to text"""
    result = [''] * len(text)
    for i, p in enumerate(perm):
        if p < len(text):
            result[i] = text[p]
    return ''.join(result)

def block_permutation(text, block_size, perm):
    """Apply permutation within blocks"""
    result = []
    for i in range(0, len(text), block_size):
        block = text[i:i+block_size]
        if len(block) == block_size:
            permuted = ''.join(block[p] for p in perm)
        else:
            permuted = block
        result.append(permuted)
    return ''.join(result)

def full_permutation_search(text, max_len=9):
    """Try all permutations (only for short texts)"""
    n = min(len(text), max_len)

    if len(text) > max_len:
        print(f"  Text too long ({len(text)}), trying block permutations")
        return block_search(text)

    print(f"  Trying all {n}! = {factorial(n)} permutations...")

    best_results = []

    for perm in permutations(range(n)):
        result = apply_permutation(text[:n], perm)
        if len(text) > n:
            result += text[n:]
        score = score_english(result)
        if score > 0:
            best_results.append((score, perm, result))

    # Sort by score
    best_results.sort(reverse=True)
    return best_results[:20]

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

def block_search(text):
    """Try block permutations for longer texts"""
    best_results = []

    for block_size in [2, 3, 4, 5, 6]:
        for perm in permutations(range(block_size)):
            result = block_permutation(text, block_size, list(perm))
            score = score_english(result)
            if score > 0:
                best_results.append((score, f"block {block_size} {perm}", result))

    best_results.sort(reverse=True)
    return best_results[:20]

def try_all_transpositions(text):
    """Comprehensive transposition trial"""
    results = []

    # 1. Simple reversal
    rev = text[::-1]
    score = score_english(rev)
    results.append((score, "reversed", rev))

    # 2. Rail fence
    for rails in range(2, 7):
        dec = rail_fence_decrypt(text, rails)
        if dec:
            score = score_english(dec)
            results.append((score, f"rail fence {rails}", dec))

    # 3. Columnar
    for cols in range(2, min(8, len(text))):
        rows = (len(text) + cols - 1) // cols
        # Write row by row, read column by column
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

        # Read by columns
        col_read = ''.join(grid[r][c] for c in range(cols) for r in range(rows) if r < len(grid) and c < len(grid[r]) and grid[r][c])
        score = score_english(col_read)
        results.append((score, f"grid {rows}x{cols} by col", col_read))

        # Read by columns reversed
        col_rev = ''.join(grid[r][c] for c in range(cols-1, -1, -1) for r in range(rows) if r < len(grid) and c < len(grid[r]) and grid[r][c])
        score = score_english(col_rev)
        results.append((score, f"grid {rows}x{cols} by col rev", col_rev))

    # 4. Swap pairs
    pairs = []
    for i in range(0, len(text)-1, 2):
        pairs.append(text[i+1] + text[i])
    if len(text) % 2:
        pairs.append(text[-1])
    swap = ''.join(pairs)
    score = score_english(swap)
    results.append((score, "pair swap", swap))

    # 5. Every nth
    for n in range(2, 6):
        for start in range(n):
            nth = text[start::n]
            score = score_english(nth)
            results.append((score, f"every {n}th from {start}", nth))

    results.sort(reverse=True)
    return results[:15]

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

def analyze_section(name, text):
    """Full analysis of one section"""
    print(f"\n{'='*60}")
    print(f"{name}: {text} ({len(text)} chars)")
    print('='*60)

    # Letter frequency
    freq = Counter(text)
    print(f"Letter freq: {dict(freq.most_common())}")

    # Try all transpositions
    print("\nBest transposition results by English score:")
    results = try_all_transpositions(text)
    for score, method, result in results[:10]:
        print(f"  Score {score:3d}: {method:25s} -> {result}")

    # For short texts, try full permutation
    if len(text) <= 11:
        print("\nFull permutation search:")
        perm_results = full_permutation_search(text)
        if perm_results:
            for score, perm, result in perm_results[:10]:
                print(f"  Score {score:3d}: perm {perm} -> {result}")

def main():
    print("EXHAUSTIVE TRANSPOSITION ANALYSIS")
    print("="*60)

    for name, text in SECTIONS.items():
        analyze_section(name, text)

    # Also try analyzing just the consonants vs vowels
    print("\n" + "="*60)
    print("VOWEL/CONSONANT ANALYSIS")
    print("="*60)

    for name, text in SECTIONS.items():
        vowels = ''.join(c for c in text if c in 'AEIOU')
        consonants = ''.join(c for c in text if c not in 'AEIOU')
        print(f"\n{name}:")
        print(f"  Vowels ({len(vowels)}): {vowels}")
        print(f"  Consonants ({len(consonants)}): {consonants}")

if __name__ == "__main__":
    main()
