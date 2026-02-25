#!/usr/bin/env python3
"""
k4_visual_masking.py
====================
Tests whether Kryptos K4 uses a visual masking technique on top of
its base cipher.

Background
----------
Ed Scheidt confirmed K4 uses "masking" on top of the base cipher.
Sanborn described using "visual systems for encoding" and said K4
might not even be "a math solution."  Scheidt had interest in
"duress ciphers" -- multi-layered ciphers where you can give up one
key that produces fake but credible plaintext.

This script exhaustively tests extraction / reading-order patterns
and checks whether any extracted subsequence yields English words
or meaningful phrases.
"""

import sys
import math
import itertools
from collections import defaultdict
from typing import List, Tuple, Set, Optional

# -- Constants --
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN    = len(K4_CIPHER)  # 97

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Known partial key from period-29 Vigenere (EASTNORTHEAST@21 + BERLINCLOCK@63)
PARTIAL_KEY = "OYNKYELYOIECBAQK?????RDUMRIYW"

# Dictionary path
DICT_PATH = "/home/user/polyalphabetic/OxfordEnglishWords.txt"

# -- Load dictionary --
def load_word_set(path):
    """Just the words, upper-cased, length >= 1."""
    words = set()
    with open(path) as f:
        for line in f:
            w = line.strip().upper()
            if w:
                words.add(w)
    for ch in ("A", "I", "O"):
        words.add(ch)
    return words


# -- English scoring --
ENGLISH_FREQ = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
    'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
    'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
    'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
    'Q': 0.10, 'Z': 0.07,
}

COMMON_DIGRAPHS = {
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
    'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
    'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
    'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA',
}

COMMON_TRIGRAPHS = {
    'THE', 'AND', 'ING', 'HER', 'ERE', 'ENT', 'THA', 'NTH', 'WAS',
    'ETH', 'FOR', 'DTH', 'ION', 'TIO', 'HAT', 'STH', 'OTH', 'ALL',
    'ARE', 'NOT', 'HIS', 'BUT', 'OUT', 'AVE', 'EST', 'ERS',
}

# Words strongly suggesting Kryptos context
KRYPTOS_WORDS = {
    'EAST', 'NORTH', 'NORTHEAST', 'BERLIN', 'CLOCK', 'PALIMPSEST',
    'ABSCISSA', 'LAYER', 'SHADOW', 'UNDERGROUND', 'BURIED', 'LANGLEY',
    'LATITUDE', 'LONGITUDE', 'COORDINATES', 'DEGREES', 'MINUTES',
    'SECONDS', 'POINT', 'MAP', 'LOCATION', 'MONUMENT', 'BETWEEN',
    'SUBTLE', 'SHADING', 'LUCID', 'MEMORY', 'VIRTUALLY', 'INVISIBLE',
    'IQLUSION', 'ILLUSION', 'DESPERATELY', 'SLOWLY', 'DESPARATLY',
}


def score_english_text(text):
    """
    Score a text fragment for English-likeness.
    Returns a composite score; higher = more English-like.
    """
    if not text:
        return 0.0

    text = text.upper()
    n = len(text)

    # 1. Frequency correlation (IoC-like)
    freq_score = 0.0
    counts = defaultdict(int)
    for ch in text:
        if ch.isalpha():
            counts[ch] += 1
    alpha_count = sum(counts.values())
    if alpha_count > 0:
        for ch, cnt in counts.items():
            observed = cnt / alpha_count * 100
            expected = ENGLISH_FREQ.get(ch, 0.5)
            freq_score -= abs(observed - expected)
        freq_score /= 26  # normalise

    # 2. Digraph score
    digraph_hits = 0
    for i in range(len(text) - 1):
        if text[i:i+2] in COMMON_DIGRAPHS:
            digraph_hits += 1
    digraph_score = digraph_hits / max(1, n - 1) * 10

    # 3. Trigraph score
    trigraph_hits = 0
    for i in range(len(text) - 2):
        if text[i:i+3] in COMMON_TRIGRAPHS:
            trigraph_hits += 1
    trigraph_score = trigraph_hits / max(1, n - 2) * 15

    return freq_score + digraph_score + trigraph_score


def find_words_in_text(text, word_set, min_len=3):
    """Find all dictionary words of length >= min_len that appear in text."""
    text = text.upper()
    found = []
    seen = set()
    for length in range(min_len, min(len(text) + 1, 20)):
        for start in range(len(text) - length + 1):
            substr = text[start:start+length]
            if substr in word_set and substr not in seen:
                found.append(substr)
                seen.add(substr)
    return found


def greedy_word_cover(text, word_set, min_len=3):
    """
    Greedily cover the text with dictionary words.
    Returns (list_of_words, fraction_covered).
    """
    text = text.upper()
    n = len(text)
    covered = [False] * n
    words_found = []

    # Try longest words first
    for length in range(min(n, 18), min_len - 1, -1):
        for start in range(n - length + 1):
            substr = text[start:start+length]
            if substr in word_set:
                already = sum(covered[start:start+length])
                if already < length * 0.5:
                    words_found.append((start, substr))
                    for i in range(start, start + length):
                        covered[i] = True

    coverage = sum(covered) / n if n > 0 else 0
    words_found.sort()
    return [w for _, w in words_found], coverage


# -- Number-theoretic helpers --
def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def fibonacci_positions(limit):
    fibs = []
    a, b = 0, 1
    while a < limit:
        fibs.append(a)
        a, b = b, a + b
    return fibs


def triangular_numbers(limit):
    tri = []
    n = 0
    t = 0
    while t < limit:
        tri.append(t)
        n += 1
        t = n * (n + 1) // 2
    return tri


def square_numbers(limit):
    sq = []
    n = 0
    while n * n < limit:
        sq.append(n * n)
        n += 1
    return sq


# -- Extraction functions --
def extract_positions(text, positions):
    """Extract characters at given positions (0-indexed)."""
    return ''.join(text[p] for p in positions if 0 <= p < len(text))


def extract_every_nth(text, n, offset=0):
    """Extract every Nth character starting at offset."""
    return text[offset::n]


# -- Grid helpers --
def fill_grid(text, rows, cols, pad='X'):
    """Fill text into a rows x cols grid, row-major."""
    padded = text + pad * (rows * cols - len(text))
    grid = []
    for r in range(rows):
        grid.append(list(padded[r*cols:(r+1)*cols]))
    return grid


def read_column_major(grid, rows, cols):
    result = []
    for c in range(cols):
        for r in range(rows):
            if r < len(grid) and c < len(grid[r]):
                result.append(grid[r][c])
    return ''.join(result)


def read_diagonal(grid, rows, cols):
    """Read all diagonals (top-left to bottom-right)."""
    result = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = d - r
            if 0 <= c < cols:
                result.append(grid[r][c])
    return ''.join(result)


def read_anti_diagonal(grid, rows, cols):
    """Read all anti-diagonals (top-right to bottom-left)."""
    result = []
    for d in range(rows + cols - 1):
        for r in range(rows):
            c = (cols - 1) - d + r
            if 0 <= c < cols:
                result.append(grid[r][c])
    return ''.join(result)


def read_boustrophedon(grid, rows, cols):
    """Read alternating L-R and R-L by row."""
    result = []
    for r in range(rows):
        row = grid[r][:cols]
        if r % 2 == 1:
            row = row[::-1]
        result.extend(row)
    return ''.join(result)


def read_spiral(grid, rows, cols):
    """Read grid in clockwise spiral."""
    result = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(grid[r][left])
            left += 1
    return ''.join(result)


def turning_grille_read(text, size):
    """
    Simulate a Cardano / turning grille on a size x size grid.
    Test a few structured patterns (exhaustive is 2^(size*size/4)).
    """
    results = []
    n = size

    def rotate90(r, c, n):
        return (c, n - 1 - r)

    half = (n + 1) // 2
    # Pattern 1: top-left quadrant cells sequentially
    cells_tl = [(r, c) for r in range(half) for c in range(half)][:n*n//4]

    # Pattern 2: diagonal cells
    cells_diag = [(i, i) for i in range(half)]
    cells_diag += [(i, half - 1 - i) for i in range(half) if (i, half - 1 - i) not in cells_diag]
    cells_diag = cells_diag[:n*n//4]

    # Pattern 3: checkerboard in top-left
    cells_check = [(r, c) for r in range(half) for c in range(half) if (r + c) % 2 == 0][:n*n//4]

    for pattern_label, pattern_cells in [("seq", cells_tl), ("diag", cells_diag), ("check", cells_check)]:
        reading = []
        used = set()
        current_cells = list(pattern_cells)
        for rotation in range(4):
            for r, c in current_cells:
                idx = r * n + c
                if 0 <= idx < len(text) and idx not in used:
                    reading.append(text[idx])
                    used.add(idx)
            current_cells = [rotate90(r, c, n) for r, c in current_cells]
        results.append((pattern_label, ''.join(reading)))

    return results


# ====================================================================
#  MAIN TESTING
# ====================================================================

def main():
    print("=" * 78)
    print("  K4 VISUAL MASKING ANALYSIS")
    print("=" * 78)
    print(f"\nK4 ciphertext : {K4_CIPHER}")
    print(f"Length         : {K4_LEN}")
    print(f"Partial key    : {PARTIAL_KEY}")
    print()

    # Load dictionary
    word_set = load_word_set(DICT_PATH)
    print(f"Dictionary loaded: {len(word_set)} words")

    # We will collect all results and rank them
    all_results = []
    # (score, label, extracted_text, found_words, coverage, cover_str)

    kryptos_ord = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}

    def evaluate(label, text):
        """Evaluate an extracted text and store result."""
        if not text or len(text) < 3:
            return
        text = text.upper()
        score = score_english_text(text)
        words = find_words_in_text(text, word_set, min_len=3)
        word_cover, coverage = greedy_word_cover(text, word_set, min_len=3)

        # Boost score for Kryptos-relevant words
        kryptos_bonus = 0
        for w in words:
            if w in KRYPTOS_WORDS:
                kryptos_bonus += 20

        # Boost for high coverage
        coverage_bonus = coverage * 15

        # Boost for long words
        long_word_bonus = sum(len(w) for w in words if len(w) >= 5) * 0.5

        total = score + kryptos_bonus + coverage_bonus + long_word_bonus

        word_str = ', '.join(words[:15]) if words else '(none)'
        cover_str = ', '.join(word_cover[:10]) if word_cover else ''

        all_results.append((total, label, text, word_str, coverage, cover_str))

    # ---------------------------------------------------------------
    print("\n" + "-" * 78)
    print("  HYPOTHESIS 1: NULL CIPHER / GRILLE")
    print("-" * 78)

    # 1a. Every Nth character
    print("\n[1a] Every Nth character (skip patterns)...")
    for n in range(2, 20):
        for offset in range(n):
            extracted = extract_every_nth(K4_CIPHER, n, offset)
            evaluate(f"Every {n}th, offset {offset}", extracted)

    # 1b. Mathematical position patterns
    print("[1b] Mathematical position patterns...")

    primes = [p for p in range(K4_LEN) if is_prime(p)]
    evaluate("Prime positions", extract_positions(K4_CIPHER, primes))
    non_primes = [p for p in range(K4_LEN) if not is_prime(p)]
    evaluate("Non-prime positions", extract_positions(K4_CIPHER, non_primes))

    fibs = [f for f in fibonacci_positions(K4_LEN)]
    evaluate("Fibonacci positions", extract_positions(K4_CIPHER, fibs))

    tris = [t for t in triangular_numbers(K4_LEN)]
    evaluate("Triangular positions", extract_positions(K4_CIPHER, tris))

    sqs = [s for s in square_numbers(K4_LEN)]
    evaluate("Square positions", extract_positions(K4_CIPHER, sqs))

    # 1c. Key-based position selection
    print("[1c] Key-range based position selection...")
    full_key_97 = []
    key_len = len(PARTIAL_KEY)
    for i in range(K4_LEN):
        key_char = PARTIAL_KEY[i % key_len]
        full_key_97.append(key_char)

    for threshold in range(1, 26, 2):
        selected = []
        for i, kc in enumerate(full_key_97):
            if kc != '?' and kc in kryptos_ord and kryptos_ord[kc] < threshold:
                selected.append(i)
        if 5 <= len(selected) <= 80:
            evaluate(f"Key ord < {threshold} (n={len(selected)})",
                     extract_positions(K4_CIPHER, selected))

    for threshold in range(5, 26, 2):
        selected = []
        for i, kc in enumerate(full_key_97):
            if kc != '?' and kc in kryptos_ord and kryptos_ord[kc] >= threshold:
                selected.append(i)
        if 5 <= len(selected) <= 80:
            evaluate(f"Key ord >= {threshold} (n={len(selected)})",
                     extract_positions(K4_CIPHER, selected))

    # 1d. Berlin Clock intervals
    print("[1d] Berlin Clock intervals...")
    for pattern in [(4,), (5,), (11,), (4, 11), (5, 1), (4, 4, 11, 4), (5, 5, 1, 1)]:
        for start_pos in range(3):
            positions = []
            pos = start_pos
            pidx = 0
            while pos < K4_LEN:
                positions.append(pos)
                pos += pattern[pidx % len(pattern)]
                pidx += 1
            evaluate(f"Berlin Clock {pattern} start={start_pos}",
                     extract_positions(K4_CIPHER, positions))

    # ---------------------------------------------------------------
    print("\n" + "-" * 78)
    print("  HYPOTHESIS 2: TURNING GRILLE (Cardano)")
    print("-" * 78)

    # 2a. 10x10 turning grille
    print("\n[2a] 10x10 turning grille patterns...")
    for size in [10]:
        readings = turning_grille_read(K4_CIPHER, size)
        for label_suffix, reading in readings:
            evaluate(f"Turning grille {size}x{size} ({label_suffix})", reading)

    # 2b. Various grid sizes close to 97
    print("[2b] Grid-based readings (column-major)...")
    for rows, cols in [(7, 14), (14, 7), (10, 10), (11, 9), (9, 11), (8, 13), (13, 8)]:
        if rows * cols < K4_LEN:
            continue
        grid = fill_grid(K4_CIPHER, rows, cols)
        cm = read_column_major(grid, rows, cols)
        evaluate(f"Column-major {rows}x{cols}", cm[:K4_LEN])

    # ---------------------------------------------------------------
    print("\n" + "-" * 78)
    print("  HYPOTHESIS 3: STEGANOGRAPHIC READING")
    print("-" * 78)

    # 3a. Grid diagonals
    print("\n[3a] Grid diagonal readings...")
    for rows, cols in [(7, 14), (14, 7), (10, 10), (11, 9), (9, 11), (8, 13), (13, 8)]:
        if rows * cols < K4_LEN:
            continue
        grid = fill_grid(K4_CIPHER, rows, cols)
        diag = read_diagonal(grid, rows, cols)
        evaluate(f"Diagonal {rows}x{cols}", diag)
        adiag = read_anti_diagonal(grid, rows, cols)
        evaluate(f"Anti-diagonal {rows}x{cols}", adiag)

    # 3b. Boustrophedon
    print("[3b] Boustrophedon readings...")
    for rows, cols in [(7, 14), (14, 7), (10, 10), (11, 9), (9, 11), (8, 13), (13, 8)]:
        if rows * cols < K4_LEN:
            continue
        grid = fill_grid(K4_CIPHER, rows, cols)
        bous = read_boustrophedon(grid, rows, cols)
        evaluate(f"Boustrophedon {rows}x{cols}", bous)

    # 3c. Spiral readings
    print("[3c] Spiral readings...")
    for rows, cols in [(7, 14), (14, 7), (10, 10), (11, 9), (9, 11)]:
        if rows * cols < K4_LEN:
            continue
        grid = fill_grid(K4_CIPHER, rows, cols)
        sp = read_spiral(grid, rows, cols)
        evaluate(f"Spiral {rows}x{cols}", sp)

    # 3d. First letter of "words" split by various delimiters
    print("[3d] First-letter-of-groups readings...")
    for group_size in range(2, 15):
        firsts = ''.join(K4_CIPHER[i] for i in range(0, K4_LEN, group_size))
        evaluate(f"First of every {group_size}-group", firsts)
        lasts = ''.join(K4_CIPHER[min(i + group_size - 1, K4_LEN - 1)]
                        for i in range(0, K4_LEN, group_size))
        evaluate(f"Last of every {group_size}-group", lasts)

    # ---------------------------------------------------------------
    print("\n" + "-" * 78)
    print("  HYPOTHESIS 4: POSITION-BASED EXTRACTION")
    print("-" * 78)

    # 4a. K2 coordinate positions
    print("\n[4a] K2 coordinate-based positions...")
    k2_coords = [38, 57, 6, 5, 77, 8, 44]
    evaluate("K2 coordinate positions", extract_positions(K4_CIPHER, k2_coords))

    # Cumulative offsets
    cumulative = []
    pos = 0
    for delta in k2_coords:
        pos = (pos + delta) % K4_LEN
        cumulative.append(pos)
    evaluate("K2 coords as cumulative offsets", extract_positions(K4_CIPHER, cumulative))

    # Extended
    extended = []
    pos = 0
    for _ in range(15):
        for delta in k2_coords:
            pos = (pos + delta) % K4_LEN
            if pos not in extended:
                extended.append(pos)
    evaluate("K2 coords extended", extract_positions(K4_CIPHER, sorted(extended)))

    # 4b. Berlin Wall date positions
    print("[4b] Berlin Wall date positions...")
    berlin_dates = [11, 9, 19, 89, 1, 9, 8, 9]
    evaluate("Berlin Wall date positions",
             extract_positions(K4_CIPHER, [d for d in berlin_dates if d < K4_LEN]))

    berlin_digits = [1, 1, 0, 9, 1, 9, 8, 9]
    evaluate("Berlin Wall digit positions",
             extract_positions(K4_CIPHER, berlin_digits))

    # Cumulative from Berlin Wall
    cum_berlin = []
    pos = 0
    for d in berlin_dates * 5:
        pos = (pos + d) % K4_LEN
        cum_berlin.append(pos)
    evaluate("Berlin Wall cumulative", extract_positions(K4_CIPHER, cum_berlin))

    # 4c. Egypt trip year 1986
    print("[4c] Egypt trip year positions...")
    egypt = [1, 9, 8, 6]
    for start in range(20):
        positions = [(start + d) % K4_LEN for d in egypt]
        evaluate(f"Egypt 1986 offsets from {start}",
                 extract_positions(K4_CIPHER, positions))

    # 4d. Modular selection
    print("[4d] Modular position selection (pos % N == M)...")
    for n in range(2, 30):
        for m in range(n):
            positions = [i for i in range(K4_LEN) if i % n == m]
            if 4 <= len(positions) <= 60:
                evaluate(f"pos%{n}=={m}", extract_positions(K4_CIPHER, positions))

    # ---------------------------------------------------------------
    print("\n" + "-" * 78)
    print("  HYPOTHESIS 5: TWO-PASS READING")
    print("-" * 78)

    # 5a. Odd then even
    print("\n[5a] Odd/even interleaving...")
    odd_pos = [i for i in range(K4_LEN) if i % 2 == 1]
    even_pos = [i for i in range(K4_LEN) if i % 2 == 0]
    evaluate("Odd positions then even", extract_positions(K4_CIPHER, odd_pos + even_pos))
    evaluate("Even positions then odd", extract_positions(K4_CIPHER, even_pos + odd_pos))
    evaluate("Only odd positions", extract_positions(K4_CIPHER, odd_pos))
    evaluate("Only even positions", extract_positions(K4_CIPHER, even_pos))

    # 5b. Column-major on various grids
    print("[5b] Column-major grid readings...")
    for rows in range(2, 50):
        cols = math.ceil(K4_LEN / rows)
        if rows * cols > K4_LEN + rows:
            continue
        grid = fill_grid(K4_CIPHER, rows, cols)
        cm = read_column_major(grid, rows, cols)
        cm = cm[:K4_LEN]
        evaluate(f"ColMajor {rows}x{cols}", cm)

    # Fill column-major, read row-major
    for rows, cols in [(10, 10), (7, 14), (14, 7)]:
        if rows * cols < K4_LEN:
            continue
        grid_cm = [['' for _ in range(cols)] for _ in range(rows)]
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx < K4_LEN:
                    grid_cm[r][c] = K4_CIPHER[idx]
                    idx += 1
        row_read = ''.join(''.join(row) for row in grid_cm)
        evaluate(f"Fill col-major, read row-major {rows}x{cols}", row_read)

    # 5c. Reverse
    print("[5c] Reverse reading...")
    evaluate("Full reverse", K4_CIPHER[::-1])

    for block_size in [2, 3, 4, 5, 7, 10, 14, 29]:
        blocks = [K4_CIPHER[i:i+block_size] for i in range(0, K4_LEN, block_size)]
        reversed_blocks = ''.join(b[::-1] for b in blocks)
        evaluate(f"Reverse each {block_size}-block", reversed_blocks)
        reversed_order = ''.join(reversed(blocks))
        evaluate(f"Reverse order of {block_size}-blocks", reversed_order)
        reversed_both = ''.join(b[::-1] for b in reversed(blocks))
        evaluate(f"Reverse both order+content {block_size}-blocks", reversed_both)

    # 5d. Rail fence / zigzag
    print("[5d] Rail fence readings...")
    for rails in range(2, 12):
        rail_order = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(K4_LEN):
            rail_order[rail].append(i)
            if rail == 0:
                direction = 1
            elif rail == rails - 1:
                direction = -1
            rail += direction
        flat_positions = []
        for r_positions in rail_order:
            flat_positions.extend(r_positions)
        # Inverse mapping for decryption
        inv = [0] * K4_LEN
        for i, p in enumerate(flat_positions):
            inv[p] = i
        decrypted = [''] * K4_LEN
        for i in range(K4_LEN):
            decrypted[inv[i]] = K4_CIPHER[i]
        evaluate(f"Rail fence decrypt {rails} rails", ''.join(decrypted))

        direct = extract_positions(K4_CIPHER, flat_positions)
        evaluate(f"Rail fence direct {rails} rails", direct)

    # 5e. Route cipher / Scytale
    print("\n[5e] Route cipher / Scytale readings...")
    for cols in range(2, 30):
        rows = math.ceil(K4_LEN / cols)
        if rows * cols > K4_LEN + cols:
            continue
        padded = K4_CIPHER + 'X' * (rows * cols - K4_LEN)
        reading = ''
        for c in range(cols):
            for r in range(rows):
                idx = r * cols + c
                if idx < K4_LEN:
                    reading += padded[idx]
        evaluate(f"Scytale cols={cols}", reading[:K4_LEN])

    # ---------------------------------------------------------------
    # Combine masking with partial decryption
    print("\n" + "-" * 78)
    print("  BONUS: MASKING ON PARTIAL PLAINTEXT")
    print("-" * 78)

    def vigenere_decrypt_kryptos(ct_char, key_char):
        """Decrypt one character using KRYPTOS alphabet Vigenere."""
        if ct_char not in kryptos_ord or key_char not in kryptos_ord:
            return '?'
        ct_idx = kryptos_ord[ct_char]
        key_idx = kryptos_ord[key_char]
        pt_idx = (ct_idx - key_idx) % 26
        return KRYPTOS_ALPHA[pt_idx]

    partial_plaintext = []
    for i in range(K4_LEN):
        key_char = full_key_97[i]
        if key_char == '?':
            partial_plaintext.append('.')
        else:
            pt = vigenere_decrypt_kryptos(K4_CIPHER[i], key_char)
            partial_plaintext.append(pt)
    partial_pt_str = ''.join(partial_plaintext)
    print(f"\nPartial plaintext: {partial_pt_str}")
    print(f"Known positions:   {sum(1 for c in partial_pt_str if c != '.')} / {K4_LEN}")

    # Extract only known positions
    known_chars = ''.join(c for c in partial_pt_str if c != '.')
    evaluate("Known plaintext chars only", known_chars)

    known_positions = [i for i in range(K4_LEN) if partial_pt_str[i] != '.']

    for n in range(2, 10):
        for offset in range(n):
            selected = [i for i in known_positions if i % n == offset]
            if len(selected) >= 4:
                extracted = ''.join(partial_pt_str[i] for i in selected)
                evaluate(f"Partial PT pos%{n}=={offset}", extracted)

    for n in range(2, 8):
        extracted = known_chars[::n]
        evaluate(f"Every {n}th known PT char", extracted)

    # ====================================================================
    #  RESULTS
    # ====================================================================
    print("\n" + "=" * 78)
    print("  RANKED RESULTS (Top 50)")
    print("=" * 78)

    # Sort by score descending
    all_results.sort(key=lambda x: x[0], reverse=True)

    for rank, (score, label, text, words, coverage, cover) in enumerate(all_results[:50], 1):
        display_text = text[:60] + "..." if len(text) > 60 else text
        print(f"\n  #{rank:3d}  Score: {score:7.2f}  Coverage: {coverage:.0%}")
        print(f"        Method: {label}")
        print(f"        Text:   {display_text}  (len={len(text)})")
        if words and words != '(none)':
            print(f"        Words:  {words}")
        if cover:
            print(f"        Cover:  {cover}")

    # ---------------------------------------------------------------
    # Detailed analysis of top results
    print("\n" + "=" * 78)
    print("  DETAILED ANALYSIS OF TOP 10")
    print("=" * 78)

    for rank, (score, label, text, words, coverage, cover) in enumerate(all_results[:10], 1):
        print(f"\n{'-' * 78}")
        print(f"  #{rank}  {label}")
        print(f"{'-' * 78}")
        print(f"  Full text: {text}")
        print(f"  Length:    {len(text)}")
        print(f"  Score:     {score:.2f}")
        print(f"  Coverage:  {coverage:.1%}")

        freq = defaultdict(int)
        for ch in text:
            freq[ch] += 1
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        print(f"  Freq:      {' '.join(f'{ch}:{n}' for ch, n in sorted_freq[:10])}")

        all_words = find_words_in_text(text, word_set, min_len=3)
        all_words.sort(key=len, reverse=True)
        print(f"  All words: {', '.join(all_words[:20])}")

        cover_words, cov = greedy_word_cover(text, word_set, min_len=3)
        print(f"  Cover:     {' | '.join(cover_words[:15])}  ({cov:.1%})")

        kryptos_found = [w for w in all_words if w in KRYPTOS_WORDS]
        if kryptos_found:
            print(f"  *** KRYPTOS WORDS: {', '.join(kryptos_found)} ***")

    # ---------------------------------------------------------------
    # Summary statistics
    print("\n" + "=" * 78)
    print("  SUMMARY")
    print("=" * 78)
    print(f"\n  Total methods tested: {len(all_results)}")

    high_score = [r for r in all_results if r[0] > 5.0]
    print(f"  Methods with score > 5.0: {len(high_score)}")

    high_coverage = [r for r in all_results if r[4] > 0.5]
    print(f"  Methods with >50% word coverage: {len(high_coverage)}")

    # Check for Kryptos-relevant words across all results
    kryptos_hits = []
    for score, label, text, words, coverage, cover in all_results:
        all_w = find_words_in_text(text, word_set, min_len=4)
        for w in all_w:
            if w in KRYPTOS_WORDS:
                kryptos_hits.append((label, w, text[:40]))
    if kryptos_hits:
        print(f"\n  *** KRYPTOS-RELEVANT WORD HITS: ***")
        seen_hits = set()
        for label, word, snippet in kryptos_hits[:30]:
            key = (word, label)
            if key not in seen_hits:
                seen_hits.add(key)
                print(f"    {word:20s}  via {label:40s}  text: {snippet}...")
    else:
        print(f"\n  No Kryptos-relevant words found in any extraction.")

    # ---------------------------------------------------------------
    # Final assessment
    print("\n" + "=" * 78)
    print("  ASSESSMENT")
    print("=" * 78)

    top_score = all_results[0][0] if all_results else 0
    if top_score > 15:
        print("""
  STRONG SIGNAL: One or more extraction methods produced text with
  high English-likeness scores. The visual masking hypothesis is
  SUPPORTED. Review the top results above for potential plaintext.""")
    elif top_score > 8:
        print("""
  MODERATE SIGNAL: Some extraction methods produced partially
  English-like text. This could indicate a masking technique but
  could also be coincidental. Further investigation warranted.""")
    else:
        print("""
  WEAK SIGNAL: No extraction method produced strongly English-like
  text from the raw K4 ciphertext. Either:
    1. The masking technique is more complex than those tested
    2. Masking applies to the plaintext layer, not the ciphertext
    3. The 'visual masking' operates differently than expected
    4. The ciphertext needs full decryption before masking reveals
       hidden content

  Note: Since K4 is still encrypted, visual masking might only
  become apparent after complete decryption of the base cipher.""")

    print(f"\n  Highest composite score: {top_score:.2f}")
    print(f"  Best method: {all_results[0][1] if all_results else 'N/A'}")
    print()


if __name__ == "__main__":
    main()
