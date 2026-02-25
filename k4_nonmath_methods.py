#!/usr/bin/env python3
"""
K4 Non-Mathematical Encoding Methods
=====================================
Inspired by Sanborn's quote: "Who says it is even a math solution?"

This script tests non-mathematical approaches to decoding K4, including:
1. Book cipher using K1-K3 plaintexts
2. Physical position mapping on the sculpture
3. Letter shape analysis
4. Steganographic extraction
5. Anagram analysis
6. Substitution pattern analysis
7. Word boundary detection via repeated letters
8. Alternative reading directions

Uses english_quadgrams.txt for scoring potential plaintexts.
"""

import math
import string
from collections import Counter, OrderedDict
from itertools import combinations

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUABOROFAANDIQLUSION"
K2_PT = ("ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDX"
         "THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONX"
         "DOESTHATLANGUAGEMAKEANYSENSETOTHEXITWASHEREARELOVELYTHEYNEEDTOKNOW"
         "BUTWHOTHEYTRUSTCANTHEYORSHALLTHEJUDGEORDERSTHELOOPBETRIEDEVERYTHING"
         "THATWASDISCOVEREDWASUSEDAGAINSTTHEMHIDDENMASSESOFEGYPTIANSTEPPEDOUTSLOW")
K3_PT = ("SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBABORETHATLAYDISCOVEREDWAS"
         "THEFINALENTRYTOTHEOUTERCHAMBERWASABOUTTOBEUNLEADEDWITHTREMBLINGHANDSI"
         "MADESMALBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEI"
         "INSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHE"
         "FLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMIST")

COMBINED_PT = K1_PT + K2_PT + K3_PT

# ============================================================
# QUADGRAM SCORER
# ============================================================

class QuadgramScorer:
    """Score text using log-probability of quadgrams."""

    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        with open(filepath, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    quad, count = parts[0], int(parts[1])
                    self.quadgrams[quad] = count
                    self.total += count
        self.floor = math.log10(0.01 / self.total)

    def score(self, text):
        """Return log-probability score for text. Higher = more English-like."""
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            quad = text[i:i+4]
            if quad in self.quadgrams:
                s += math.log10(self.quadgrams[quad] / self.total)
            else:
                s += self.floor
        return s

    def score_per_char(self, text):
        """Normalized score per character for comparing different-length texts."""
        if len(text) < 4:
            return self.floor
        return self.score(text) / (len(text) - 3)


print("=" * 80)
print("K4 NON-MATHEMATICAL ENCODING METHODS")
print("Inspired by Sanborn: 'Who says it is even a math solution?'")
print("=" * 80)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

# Baseline: score of raw K4
k4_score = scorer.score_per_char(K4)
print(f"\nBaseline K4 score (per char): {k4_score:.4f}")
print(f"For reference, K3 plaintext score: {scorer.score_per_char(K3_PT):.4f}")


# ============================================================
# 1. BOOK CIPHER
# ============================================================

print("\n" + "=" * 80)
print("1. BOOK CIPHER - Using K1-K3 plaintexts as the 'book'")
print("=" * 80)

def book_cipher_by_position(ciphertext, book, alphabet=None):
    """
    Treat each letter in ciphertext as an index into the book.
    A=0/1, B=1/2, etc. Try various offset schemes.
    """
    results = []

    # Method 1a: Standard A=0 index, modular into book
    plain = []
    for ch in ciphertext:
        idx = ord(ch) - ord('A')
        book_idx = idx % len(book)
        plain.append(book[book_idx])
    result = ''.join(plain)
    results.append(("A=0 mod book_len", result))

    # Method 1b: Standard A=1 index
    plain = []
    for ch in ciphertext:
        idx = ord(ch) - ord('A') + 1
        book_idx = idx % len(book)
        plain.append(book[book_idx])
    result = ''.join(plain)
    results.append(("A=1 mod book_len", result))

    # Method 1c: Using KRYPTOS alphabet position
    if alphabet:
        plain = []
        for ch in ciphertext:
            if ch in alphabet:
                idx = alphabet.index(ch)
            else:
                idx = ord(ch) - ord('A')
            book_idx = idx % len(book)
            plain.append(book[book_idx])
        result = ''.join(plain)
        results.append(("KRYPTOS alphabet pos mod book_len", result))

    # Method 1d: Cumulative indexing - each letter shifts further into book
    plain = []
    running = 0
    for ch in ciphertext:
        idx = ord(ch) - ord('A')
        running += idx
        book_idx = running % len(book)
        plain.append(book[book_idx])
    result = ''.join(plain)
    results.append(("Cumulative index mod book_len", result))

    return results


def book_cipher_nth_occurrence(ciphertext, book):
    """
    For each letter in K4, find the Nth occurrence of that letter in the book
    where N increments for each use of the same letter.
    Return the position, which could encode something.
    """
    letter_counts = {}
    positions = []
    for ch in ciphertext:
        n = letter_counts.get(ch, 0)
        letter_counts[ch] = n + 1
        # Find the (n+1)th occurrence
        count = 0
        found = False
        for i, bc in enumerate(book):
            if bc == ch:
                if count == n:
                    positions.append(i)
                    found = True
                    break
                count += 1
        if not found:
            # Wrap around
            count_total = book.count(ch)
            if count_total > 0:
                wrapped_n = n % count_total
                count = 0
                for i, bc in enumerate(book):
                    if bc == ch:
                        if count == wrapped_n:
                            positions.append(i)
                            break
                        count += 1
            else:
                positions.append(-1)
    return positions


print("\n--- Method 1a-d: Direct position-based book cipher ---")
for book_name, book_text in [("K1+K2+K3", COMBINED_PT), ("K3 only", K3_PT), ("K2 only", K2_PT)]:
    results = book_cipher_by_position(K4, book_text, KRYPTOS_ALPHABET)
    for method, result in results:
        sc = scorer.score_per_char(result)
        if sc > k4_score + 0.3:
            print(f"  [{book_name}] {method}: score={sc:.4f} ***INTERESTING***")
            print(f"    -> {result[:80]}...")
        else:
            print(f"  [{book_name}] {method}: score={sc:.4f}")
            print(f"    -> {result[:60]}...")

print("\n--- Method 1e: Nth occurrence position extraction ---")
positions = book_cipher_nth_occurrence(K4, COMBINED_PT)
valid_positions = [p for p in positions if p >= 0]
print(f"  Found {len(valid_positions)}/{len(K4)} valid positions in combined K1-K3")
if valid_positions:
    # Try using positions mod 26 as letters
    letters = ''.join(chr(ord('A') + (p % 26)) for p in valid_positions)
    sc = scorer.score_per_char(letters)
    print(f"  Positions mod 26 as letters: score={sc:.4f}")
    print(f"    -> {letters[:60]}...")

    # Differences between consecutive positions
    if len(valid_positions) > 1:
        diffs = [valid_positions[i+1] - valid_positions[i] for i in range(len(valid_positions)-1)]
        diff_letters = ''.join(chr(ord('A') + (abs(d) % 26)) for d in diffs)
        sc = scorer.score_per_char(diff_letters)
        print(f"  Position differences mod 26: score={sc:.4f}")
        print(f"    -> {diff_letters[:60]}...")


# ============================================================
# 2. PHYSICAL POSITION ON SCULPTURE
# ============================================================

print("\n" + "=" * 80)
print("2. PHYSICAL POSITION - Mapping K4 to rows/columns on copper plate")
print("=" * 80)

# The Kryptos sculpture has the ciphertext arranged in rows on the copper plate.
# K4 is 97 characters. Try various grid dimensions.

def try_grid_reading(text, ncols, reading="normal"):
    """Lay text on grid of ncols columns, read in various orders."""
    nrows = math.ceil(len(text) / ncols)
    # Pad text
    padded = text + 'X' * (nrows * ncols - len(text))

    grid = []
    for r in range(nrows):
        grid.append(list(padded[r*ncols:(r+1)*ncols]))

    results = {}

    # Column-first reading (top to bottom, left to right)
    col_read = ''.join(grid[r][c] for c in range(ncols) for r in range(nrows))
    results['col_first'] = col_read[:len(text)]

    # Column-first reverse (bottom to top, left to right)
    col_rev = ''.join(grid[r][c] for c in range(ncols) for r in range(nrows-1, -1, -1))
    results['col_first_rev'] = col_rev[:len(text)]

    # Diagonal reading
    diag = []
    for d in range(nrows + ncols - 1):
        for r in range(nrows):
            c = d - r
            if 0 <= c < ncols:
                diag.append(grid[r][c])
    results['diagonal'] = ''.join(diag)[:len(text)]

    # Spiral reading
    spiral = []
    top, bottom, left, right = 0, nrows-1, 0, ncols-1
    temp_grid = [row[:] for row in grid]
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            spiral.append(temp_grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            spiral.append(temp_grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                spiral.append(temp_grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                spiral.append(temp_grid[r][left])
            left += 1
    results['spiral'] = ''.join(spiral)[:len(text)]

    return results


print("\nTrying various grid dimensions and reading orders:")
best_grid_results = []
for ncols in range(5, 20):
    readings = try_grid_reading(K4, ncols)
    for method, result in readings.items():
        sc = scorer.score_per_char(result)
        best_grid_results.append((sc, ncols, method, result))

best_grid_results.sort(reverse=True)
print(f"\n  Top 10 grid reading results:")
for sc, ncols, method, result in best_grid_results[:10]:
    nrows = math.ceil(len(K4) / ncols)
    print(f"  {nrows}x{ncols} {method}: score={sc:.4f}")
    print(f"    -> {result[:60]}...")

# Physical layout: K4 on the actual sculpture is in rows of ~86 characters across 4 sections
print("\n--- Sculpture physical layout (approx 86 chars wide) ---")
# Actually the full Kryptos text is about 869 chars laid out on the plate
# K4 starts around position 772. The plate is roughly 30 rows of ~29 characters each.
# Let's try the commonly cited layouts:
for ncols in [29, 30, 31, 86]:
    readings = try_grid_reading(K4, ncols)
    for method, result in readings.items():
        sc = scorer.score_per_char(result)
        if sc > k4_score + 0.1:
            print(f"  {ncols}-col {method}: score={sc:.4f} *better than baseline*")
            print(f"    -> {result[:60]}...")


# Map each K4 letter to its row/column position on the plate
print("\n--- Row/column coordinate extraction ---")
for ncols in [7, 8, 9, 10, 11, 12, 13, 14, 97]:
    row_letters = []
    col_letters = []
    for i, ch in enumerate(K4):
        r = i // ncols
        c = i % ncols
        row_letters.append(chr(ord('A') + (r % 26)))
        col_letters.append(chr(ord('A') + (c % 26)))
    row_str = ''.join(row_letters)
    col_str = ''.join(col_letters)
    # XOR K4 with row/col
    xor_row = ''.join(chr(ord('A') + ((ord(K4[i]) - ord('A')) ^ (ord(row_letters[i]) - ord('A'))) % 26) for i in range(len(K4)))
    xor_col = ''.join(chr(ord('A') + ((ord(K4[i]) - ord('A')) ^ (ord(col_letters[i]) - ord('A'))) % 26) for i in range(len(K4)))
    sc_r = scorer.score_per_char(xor_row)
    sc_c = scorer.score_per_char(xor_col)
    if sc_r > k4_score + 0.1 or sc_c > k4_score + 0.1:
        if sc_r > sc_c:
            print(f"  {ncols}-col XOR with row: score={sc_r:.4f}")
            print(f"    -> {xor_row[:60]}...")
        else:
            print(f"  {ncols}-col XOR with col: score={sc_c:.4f}")
            print(f"    -> {xor_col[:60]}...")


# ============================================================
# 3. LETTER SHAPES
# ============================================================

print("\n" + "=" * 80)
print("3. LETTER SHAPES - Visual properties of letters")
print("=" * 80)

# Classify letters by visual properties
CURVED_LETTERS = set("BCDGJOPQRSU")
STRAIGHT_LETTERS = set("AEFHIKLMNTVWXYZ")
SYMMETRIC_LETTERS = set("AHIMOTUVWXY")
ASYMMETRIC_LETTERS = set("BCDEFGJKLNPQRSZ")
TALL_LETTERS = set("BDFHIJKLT")  # ascenders in lowercase
SHORT_LETTERS = set("ACEGMNOPQRSUVWXYZ")
OPEN_TOP = set("CGLSUVWZ")
CLOSED_TOP = set("ABDEHIJKMNOPQRTXY")

# Letters with enclosed spaces
ENCLOSED_LETTERS = set("ABDOPQR")
NO_ENCLOSED = set("CEFGHIJKLMNSTUVWXYZ")

shape_categories = {
    "curved": CURVED_LETTERS,
    "straight": STRAIGHT_LETTERS,
    "symmetric": SYMMETRIC_LETTERS,
    "enclosed": ENCLOSED_LETTERS,
}

print("\nBinary encoding by letter shape properties:")
for prop_name, prop_set in shape_categories.items():
    binary = ''.join('1' if ch in prop_set else '0' for ch in K4)
    print(f"\n  {prop_name}: {binary}")

    # Convert binary groups of 5 to letters (like Bacon's cipher)
    if len(binary) >= 5:
        bacon_letters = []
        for i in range(0, len(binary) - 4, 5):
            group = binary[i:i+5]
            val = int(group, 2)
            if val < 26:
                bacon_letters.append(chr(ord('A') + val))
        bacon_text = ''.join(bacon_letters)
        sc = scorer.score_per_char(bacon_text)
        print(f"  Bacon decode (5-bit groups): '{bacon_text}' score={sc:.4f}")

    # Extract only letters with this property
    extracted = ''.join(ch for ch in K4 if ch in prop_set)
    sc_ext = scorer.score_per_char(extracted) if len(extracted) >= 4 else -99
    print(f"  Extracted {prop_name} letters ({len(extracted)}): {extracted[:60]}...")
    print(f"    score={sc_ext:.4f}")

    # Extract letters WITHOUT this property
    anti = ''.join(ch for ch in K4 if ch not in prop_set)
    sc_anti = scorer.score_per_char(anti) if len(anti) >= 4 else -99
    print(f"  Extracted non-{prop_name} letters ({len(anti)}): {anti[:60]}...")
    print(f"    score={sc_anti:.4f}")

# Interleave: curved letters form one message, straight another
print("\n--- Dual-stream by curve/straight ---")
curved_stream = ''.join(ch for ch in K4 if ch in CURVED_LETTERS)
straight_stream = ''.join(ch for ch in K4 if ch in STRAIGHT_LETTERS)
print(f"  Curved stream ({len(curved_stream)}): {curved_stream}")
print(f"    score={scorer.score_per_char(curved_stream):.4f}")
print(f"  Straight stream ({len(straight_stream)}): {straight_stream}")
print(f"    score={scorer.score_per_char(straight_stream):.4f}")


# ============================================================
# 4. STEGANOGRAPHY
# ============================================================

print("\n" + "=" * 80)
print("4. STEGANOGRAPHY - Hidden messages in letter selection")
print("=" * 80)

# 4a: Split at possible delimiters
print("\n--- 4a: Word splitting at delimiters ---")
# Common delimiter letters that appear frequently
for delimiter in ['Q', 'X', 'Z', 'W', 'K']:
    parts = K4.split(delimiter)
    if len(parts) > 1:
        first_letters = ''.join(p[0] for p in parts if p)
        last_letters = ''.join(p[-1] for p in parts if p)
        print(f"  Split on '{delimiter}' -> {len(parts)} parts")
        print(f"    First letters: {first_letters}")
        print(f"    Last letters:  {last_letters}")

# 4b: Every Nth letter
print("\n--- 4b: Every Nth letter extraction ---")
best_nth = []
for n in range(2, 20):
    for start in range(n):
        extracted = K4[start::n]
        if len(extracted) >= 4:
            sc = scorer.score_per_char(extracted)
            best_nth.append((sc, n, start, extracted))

best_nth.sort(reverse=True)
print(f"  Top 10 Nth-letter extractions:")
for sc, n, start, extracted in best_nth[:10]:
    print(f"  Every {n}th from pos {start}: score={sc:.4f} -> {extracted[:50]}...")

# 4c: Letters by frequency of appearance
print("\n--- 4c: Letters by frequency of appearance in K4 ---")
freq = Counter(K4)
print(f"  Letter frequencies: {dict(sorted(freq.items(), key=lambda x: -x[1]))}")

for target_count in range(1, 6):
    letters_with_count = [ch for ch in K4 if freq[ch] == target_count]
    unique_letters = sorted(set(ch for ch in K4 if freq[ch] == target_count))
    if unique_letters:
        print(f"  Letters appearing exactly {target_count} time(s): {''.join(unique_letters)}")

# Letters that appear exactly once (hapax legomena)
hapax = ''.join(ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if freq.get(ch, 0) == 1)
print(f"\n  Hapax (appear once in K4): {hapax}")
missing = ''.join(ch for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if freq.get(ch, 0) == 0)
print(f"  Missing from K4: {missing}")

# Extract positions of rare letters
rare_positions = [i for i, ch in enumerate(K4) if freq[ch] <= 2]
print(f"  Positions of rare letters (freq<=2): {rare_positions}")
if rare_positions:
    rare_text = ''.join(K4[i] for i in rare_positions)
    print(f"  Rare letter sequence: {rare_text}")

# 4d: Mathematical position selection
print("\n--- 4d: Positional extraction (prime, Fibonacci, triangular, square) ---")

def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def fibonacci_positions(limit):
    fibs = set()
    a, b = 0, 1
    while a <= limit:
        fibs.add(a)
        a, b = b, a + b
    return fibs

def triangular_positions(limit):
    triangles = set()
    n = 0
    t = 0
    while t <= limit:
        triangles.add(t)
        n += 1
        t = n * (n + 1) // 2
    return triangles

def square_positions(limit):
    squares = set()
    n = 0
    while n * n <= limit:
        squares.add(n * n)
        n += 1
    return squares

position_types = {
    "prime": set(i for i in range(len(K4)) if is_prime(i)),
    "fibonacci": fibonacci_positions(len(K4) - 1),
    "triangular": triangular_positions(len(K4) - 1),
    "square": square_positions(len(K4) - 1),
    "prime (1-indexed)": set(i - 1 for i in range(len(K4) + 1) if is_prime(i)),
}

for pos_name, positions in position_types.items():
    valid_pos = sorted(p for p in positions if 0 <= p < len(K4))
    extracted = ''.join(K4[p] for p in valid_pos)
    remaining = ''.join(K4[p] for p in range(len(K4)) if p not in positions)
    sc_ext = scorer.score_per_char(extracted) if len(extracted) >= 4 else -99
    sc_rem = scorer.score_per_char(remaining) if len(remaining) >= 4 else -99
    print(f"  {pos_name} positions ({len(valid_pos)} chars):")
    print(f"    Extracted: {extracted[:60]}... score={sc_ext:.4f}")
    print(f"    Remaining: {remaining[:60]}... score={sc_rem:.4f}")

# 4e: Spiral reading on various grids
print("\n--- 4e: Spiral pattern reading on grids ---")
best_spiral = []
for ncols in range(5, 20):
    readings = try_grid_reading(K4, ncols)
    spiral = readings.get('spiral', '')
    if len(spiral) >= 4:
        sc = scorer.score_per_char(spiral)
        best_spiral.append((sc, ncols, spiral))

best_spiral.sort(reverse=True)
print("  Top 5 spiral readings:")
for sc, ncols, text in best_spiral[:5]:
    nrows = math.ceil(len(K4) / ncols)
    print(f"  {nrows}x{ncols} spiral: score={sc:.4f}")
    print(f"    -> {text[:60]}...")

# 4f: K4 position matches KRYPTOS alphabet position
print("\n--- 4f: Position matching in KRYPTOS alphabet ---")
# Extract letters where K4[i] is at position i (mod 26) in the KRYPTOS alphabet
matches = []
for i, ch in enumerate(K4):
    kryp_pos = KRYPTOS_ALPHABET.index(ch) if ch in KRYPTOS_ALPHABET else -1
    std_pos = ord(ch) - ord('A')
    # Check various matching conditions
    if kryp_pos == (i % 26):
        matches.append((i, ch, "kryptos_pos==i%26"))
    if std_pos == (i % 26):
        matches.append((i, ch, "std_pos==i%26"))
    if kryp_pos == std_pos:
        matches.append((i, ch, "kryptos_pos==std_pos"))

print(f"  Found {len(matches)} position matches:")
for condition in ["kryptos_pos==i%26", "std_pos==i%26", "kryptos_pos==std_pos"]:
    cond_matches = [(i, ch) for i, ch, c in matches if c == condition]
    if cond_matches:
        extracted = ''.join(ch for _, ch in cond_matches)
        print(f"  {condition}: positions {[i for i, _ in cond_matches]}")
        print(f"    letters: {extracted}")

# Self-referential: K4[i] == KRYPTOS_ALPHABET[i % len(KRYPTOS_ALPHABET)]
self_ref = []
for i, ch in enumerate(K4):
    expected = KRYPTOS_ALPHABET[i % len(KRYPTOS_ALPHABET)]
    if ch == expected:
        self_ref.append((i, ch))
if self_ref:
    print(f"\n  Self-referential matches (K4[i]==KRYPTOS_ALPHA[i%26]): {len(self_ref)}")
    print(f"    positions: {[i for i, _ in self_ref]}")
    print(f"    letters: {''.join(ch for _, ch in self_ref)}")


# ============================================================
# 5. ANAGRAM ANALYSIS
# ============================================================

print("\n" + "=" * 80)
print("5. ANAGRAM ANALYSIS - Frequency comparison with English")
print("=" * 80)

# English letter frequencies (approximate)
ENGLISH_FREQ = {
    'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7, 'S': 6.3,
    'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4,
    'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5, 'V': 1.0,
    'K': 0.8, 'J': 0.15, 'X': 0.15, 'Q': 0.10, 'Z': 0.07
}

k4_freq = Counter(K4)
total = len(K4)

print(f"\nK4 length: {total} characters")
print(f"\n{'Letter':>8} {'K4 count':>10} {'K4 %':>8} {'English %':>10} {'Delta':>8}")
print("-" * 50)

deviations = []
for ch in sorted("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    k4_count = k4_freq.get(ch, 0)
    k4_pct = 100 * k4_count / total
    eng_pct = ENGLISH_FREQ.get(ch, 0)
    delta = k4_pct - eng_pct
    deviations.append((abs(delta), ch, k4_count, k4_pct, eng_pct, delta))
    flag = " ***" if abs(delta) > 3 else ""
    print(f"{ch:>8} {k4_count:>10} {k4_pct:>7.1f}% {eng_pct:>9.1f}% {delta:>+7.1f}{flag}")

print("\nMost deviant letters from English frequencies:")
deviations.sort(reverse=True)
for dev, ch, count, k4p, engp, delta in deviations[:5]:
    direction = "over-represented" if delta > 0 else "under-represented"
    print(f"  {ch}: {direction} by {dev:.1f}% (K4={k4p:.1f}%, English={engp:.1f}%)")

# Chi-squared test
chi_sq = 0
for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    observed = k4_freq.get(ch, 0)
    expected = ENGLISH_FREQ.get(ch, 0) * total / 100
    if expected > 0:
        chi_sq += (observed - expected) ** 2 / expected
print(f"\nChi-squared vs English: {chi_sq:.2f}")
print(f"  (For 25 df, critical value at p=0.05 is 37.65)")
print(f"  {'REJECT: K4 frequencies differ significantly from English' if chi_sq > 37.65 else 'ACCEPT: K4 frequencies consistent with English'}")

# Index of Coincidence
ic = sum(k4_freq[ch] * (k4_freq[ch] - 1) for ch in k4_freq) / (total * (total - 1))
print(f"\nIndex of Coincidence: {ic:.4f}")
print(f"  English IC: ~0.0667, Random IC: ~0.0385")
if ic > 0.055:
    print(f"  -> Suggests monoalphabetic cipher or plaintext")
elif ic > 0.045:
    print(f"  -> Suggests polyalphabetic cipher with short period")
else:
    print(f"  -> Suggests polyalphabetic cipher with longer period")

# Anagram potential: look for common English words that can be formed
print("\n--- Checking if common English words can be formed from K4 letters ---")
common_words = [
    "BETWEEN", "SUBTLE", "SHADING", "ABSENCE", "LIGHT", "SLOWLY", "DESPERATELY",
    "CHAMBER", "TREASURE", "BURIED", "SECRET", "HIDDEN", "PALIMPSEST", "KRYPTOS",
    "LANGLEY", "UNDERGROUND", "MAGNETIC", "FIELD", "LOCATION", "UNKNOWN",
    "NORTHEAST", "BERLIN", "CLOCK", "WALL", "PASSAGE", "DISCOVERY",
    "EAST", "WEST", "NORTH", "SOUTH", "LATITUDE", "LONGITUDE"
]

k4_available = dict(k4_freq)
print(f"  Testing if key words can be spelled from K4's letters:")
for word in common_words:
    word_freq = Counter(word)
    can_form = all(k4_available.get(ch, 0) >= cnt for ch, cnt in word_freq.items())
    if can_form:
        print(f"    {word} - YES (available in K4)")
    else:
        missing = {ch: cnt - k4_available.get(ch, 0) for ch, cnt in word_freq.items()
                   if k4_available.get(ch, 0) < cnt}
        print(f"    {word} - NO (need more: {missing})")


# ============================================================
# 6. SUBSTITUTION PATTERNS
# ============================================================

print("\n" + "=" * 80)
print("6. SUBSTITUTION PATTERNS - Repeated bigrams/trigrams as code groups")
print("=" * 80)

# Find all bigrams and their frequencies
print("\n--- Bigram analysis ---")
bigrams = Counter(K4[i:i+2] for i in range(len(K4)-1))
repeated_bigrams = {k: v for k, v in bigrams.items() if v > 1}
sorted_bigrams = sorted(repeated_bigrams.items(), key=lambda x: -x[1])
print(f"  Repeated bigrams ({len(repeated_bigrams)} found):")
for bg, count in sorted_bigrams[:15]:
    positions = [i for i in range(len(K4)-1) if K4[i:i+2] == bg]
    spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    print(f"    {bg}: {count}x at positions {positions}, spacings={spacings}")

# Find all trigrams
print("\n--- Trigram analysis ---")
trigrams = Counter(K4[i:i+3] for i in range(len(K4)-2))
repeated_trigrams = {k: v for k, v in trigrams.items() if v > 1}
sorted_trigrams = sorted(repeated_trigrams.items(), key=lambda x: -x[1])
print(f"  Repeated trigrams ({len(repeated_trigrams)} found):")
for tg, count in sorted_trigrams[:10]:
    positions = [i for i in range(len(K4)-2) if K4[i:i+3] == tg]
    spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    print(f"    {tg}: {count}x at positions {positions}, spacings={spacings}")

# Look for patterns: if bigrams represent single letters (like Polybius)
print("\n--- Polybius-like bigram decoding ---")
# If pairs of letters are coordinates in a 5x5 or 6x6 grid
def polybius_decode(text, grid_size=5, alphabet=None):
    """Decode pairs as Polybius square coordinates."""
    if alphabet is None:
        # Standard 5x5 (I/J combined)
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # no J
    result = []
    for i in range(0, len(text) - 1, 2):
        r = ord(text[i]) - ord('A')
        c = ord(text[i+1]) - ord('A')
        if grid_size == 5:
            idx = (r % 5) * 5 + (c % 5)
        else:
            idx = (r % grid_size) * grid_size + (c % grid_size)
        if idx < len(alphabet):
            result.append(alphabet[idx])
        else:
            result.append('?')
    return ''.join(result)

for grid in [5, 6]:
    plain = polybius_decode(K4, grid)
    sc = scorer.score_per_char(plain)
    print(f"  Polybius {grid}x{grid}: {plain[:50]}... score={sc:.4f}")

# With KRYPTOS alphabet
plain_kryp = polybius_decode(K4, 5, KRYPTOS_ALPHABET[:25])
sc = scorer.score_per_char(plain_kryp)
print(f"  Polybius 5x5 (KRYPTOS alpha): {plain_kryp[:50]}... score={sc:.4f}")

# Kasiski analysis - GCD of spacings for repeated n-grams
print("\n--- Kasiski examination (GCD of repeat spacings) ---")
all_spacings = []
for length in range(2, 5):
    ngrams = {}
    for i in range(len(K4) - length + 1):
        ng = K4[i:i+length]
        if ng not in ngrams:
            ngrams[ng] = []
        ngrams[ng].append(i)
    for ng, positions in ngrams.items():
        if len(positions) > 1:
            for j in range(len(positions)):
                for k in range(j+1, len(positions)):
                    all_spacings.append(positions[k] - positions[j])

spacing_factors = Counter()
for s in all_spacings:
    for f in range(2, s+1):
        if s % f == 0:
            spacing_factors[f] += 1

print(f"  Most common spacing factors:")
for factor, count in spacing_factors.most_common(10):
    print(f"    Factor {factor}: appears {count} times")


# ============================================================
# 7. WORD BOUNDARIES
# ============================================================

print("\n" + "=" * 80)
print("7. WORD BOUNDARIES - Using double letters and patterns as delimiters")
print("=" * 80)

# Find double letters in K4
doubles = []
for i in range(len(K4) - 1):
    if K4[i] == K4[i+1]:
        doubles.append((i, K4[i:i+2]))

print(f"\nDouble letters found in K4:")
for pos, pair in doubles:
    print(f"  Position {pos}: {pair}")
    context_start = max(0, pos - 3)
    context_end = min(len(K4), pos + 5)
    print(f"    Context: ...{K4[context_start:pos]}[{pair}]{K4[pos+2:context_end]}...")

# Split K4 at double letters
print(f"\n--- Splitting K4 at double letters ---")
split_text = K4
positions_of_doubles = [pos for pos, _ in doubles]

# Mark double letter positions
segments = []
prev = 0
for pos, pair in doubles:
    if pos > prev:
        segments.append(K4[prev:pos])
    segments.append(f"[{pair}]")
    prev = pos + 2
if prev < len(K4):
    segments.append(K4[prev:])

print(f"  Segmented: {'|'.join(segments)}")

# Extract text between doubles
between_doubles = []
prev_end = 0
for pos, pair in doubles:
    if pos > prev_end:
        between_doubles.append(K4[prev_end:pos])
    prev_end = pos + 2
if prev_end < len(K4):
    between_doubles.append(K4[prev_end:])

print(f"\n  Text segments between doubles:")
for i, seg in enumerate(between_doubles):
    print(f"    Segment {i}: '{seg}' (len={len(seg)})")

# First letters of segments
if between_doubles:
    first_of_segs = ''.join(s[0] for s in between_doubles if s)
    last_of_segs = ''.join(s[-1] for s in between_doubles if s)
    print(f"\n  First letters of segments: {first_of_segs}")
    print(f"  Last letters of segments:  {last_of_segs}")

# Lengths of segments could encode something
seg_lengths = [len(s) for s in between_doubles]
print(f"  Segment lengths: {seg_lengths}")
length_letters = ''.join(chr(ord('A') + (l % 26)) for l in seg_lengths)
print(f"  Lengths as letters (A=0): {length_letters}")

# What if the double letters themselves spell something?
double_chars = ''.join(pair[0] for _, pair in doubles)
print(f"\n  Double letter characters: {double_chars}")
print(f"  Double positions: {[pos for pos, _ in doubles]}")
print(f"  Spacings between doubles: {[positions_of_doubles[i+1] - positions_of_doubles[i] for i in range(len(positions_of_doubles)-1)]}")

# Letters just before and after each double
print(f"\n  Context around doubles:")
for pos, pair in doubles:
    before = K4[pos-1] if pos > 0 else '-'
    after = K4[pos+2] if pos+2 < len(K4) else '-'
    print(f"    {before}[{pair}]{after}")


# ============================================================
# 8. READING DIRECTION
# ============================================================

print("\n" + "=" * 80)
print("8. READING DIRECTION - Backwards, boustrophedon, zigzag")
print("=" * 80)

# 8a: Backwards
print("\n--- 8a: K4 reversed ---")
k4_rev = K4[::-1]
sc_rev = scorer.score_per_char(k4_rev)
print(f"  Reversed: {k4_rev}")
print(f"  Score: {sc_rev:.4f} (baseline: {k4_score:.4f})")

# 8b: Boustrophedon (every other row reversed)
print("\n--- 8b: Boustrophedon (alternating row direction) ---")
best_boust = []
for ncols in range(5, 20):
    nrows = math.ceil(len(K4) / ncols)
    padded = K4 + 'X' * (nrows * ncols - len(K4))
    result = []
    for r in range(nrows):
        row = padded[r*ncols:(r+1)*ncols]
        if r % 2 == 1:
            row = row[::-1]
        result.append(row)
    boust = ''.join(result)[:len(K4)]
    sc = scorer.score_per_char(boust)
    best_boust.append((sc, ncols, boust))

best_boust.sort(reverse=True)
print(f"  Top 5 boustrophedon results:")
for sc, ncols, text in best_boust[:5]:
    print(f"  {ncols}-col: score={sc:.4f} -> {text[:60]}...")

# 8c: Zigzag (rail fence pattern)
print("\n--- 8c: Rail fence / zigzag reading ---")
def rail_fence_decode(text, nrails):
    """Decode a rail fence cipher with given number of rails."""
    if nrails <= 1 or nrails >= len(text):
        return text
    # Calculate the pattern
    pattern = list(range(nrails)) + list(range(nrails-2, 0, -1))
    # Build rails
    indices = [[] for _ in range(nrails)]
    for i in range(len(text)):
        rail = pattern[i % len(pattern)]
        indices[rail].append(i)
    # Fill in the decoded text
    result = [''] * len(text)
    pos = 0
    for rail in range(nrails):
        for idx in indices[rail]:
            if pos < len(text):
                result[idx] = text[pos]
                pos += 1
    return ''.join(result)

def rail_fence_encode(text, nrails):
    """Read text off rails (encode = read in zigzag, write in rows)."""
    if nrails <= 1 or nrails >= len(text):
        return text
    pattern = list(range(nrails)) + list(range(nrails-2, 0, -1))
    rails = [[] for _ in range(nrails)]
    for i, ch in enumerate(text):
        rail = pattern[i % len(pattern)]
        rails[rail].append(ch)
    return ''.join(''.join(r) for r in rails)

best_rail = []
for nrails in range(2, 15):
    decoded = rail_fence_decode(K4, nrails)
    sc = scorer.score_per_char(decoded)
    best_rail.append((sc, nrails, "decode", decoded))

    encoded = rail_fence_encode(K4, nrails)
    sc2 = scorer.score_per_char(encoded)
    best_rail.append((sc2, nrails, "encode", encoded))

best_rail.sort(reverse=True)
print(f"  Top 10 rail fence results:")
for sc, nrails, direction, text in best_rail[:10]:
    print(f"  {nrails} rails ({direction}): score={sc:.4f}")
    print(f"    -> {text[:60]}...")

# 8d: Column transposition (read columns in different order)
print("\n--- 8d: Column transposition decryption ---")
best_col_trans = []
for ncols in range(5, 12):
    nrows = math.ceil(len(K4) / ncols)
    padded = K4 + 'X' * (nrows * ncols - len(K4))

    # Read column by column
    cols = []
    for c in range(ncols):
        col = ''.join(padded[r * ncols + c] for r in range(nrows))
        cols.append(col)

    # Try all simple column reorderings we can reasonably test
    # For small ncols, try reversing column order
    rev_cols = ''.join(cols[::-1])[:len(K4)]
    sc = scorer.score_per_char(rev_cols)
    best_col_trans.append((sc, ncols, "reverse cols", rev_cols))

    # Interleave odd/even columns
    even_cols = ''.join(cols[i] for i in range(0, ncols, 2))
    odd_cols = ''.join(cols[i] for i in range(1, ncols, 2))
    interleaved = (even_cols + odd_cols)[:len(K4)]
    sc = scorer.score_per_char(interleaved)
    best_col_trans.append((sc, ncols, "even+odd cols", interleaved))

    # Read rows from the column-rearranged grid
    # Try KRYPTOS keyword ordering for columns
    if ncols <= len(KRYPTOS_ALPHABET):
        keyword_order = sorted(range(ncols), key=lambda i: KRYPTOS_ALPHABET[i % len(KRYPTOS_ALPHABET)])
        reordered = ''.join(cols[keyword_order[i]] for i in range(ncols) if keyword_order[i] < ncols)[:len(K4)]
        sc = scorer.score_per_char(reordered)
        best_col_trans.append((sc, ncols, "KRYPTOS keyword order", reordered))

best_col_trans.sort(reverse=True)
print(f"  Top 10 column transposition results:")
for sc, ncols, method, text in best_col_trans[:10]:
    print(f"  {ncols}-col {method}: score={sc:.4f}")
    print(f"    -> {text[:60]}...")

# 8e: Route cipher - read grid in various routes
print("\n--- 8e: Route cipher (snake, diagonal) ---")
best_route = []
for ncols in [7, 8, 9, 10, 11, 12, 13, 14]:
    nrows = math.ceil(len(K4) / ncols)
    padded = K4 + 'X' * (nrows * ncols - len(K4))
    grid = []
    for r in range(nrows):
        grid.append(list(padded[r*ncols:(r+1)*ncols]))

    # Snake: left-right then right-left alternating
    snake = []
    for r in range(nrows):
        if r % 2 == 0:
            snake.extend(grid[r])
        else:
            snake.extend(reversed(grid[r]))
    snake_text = ''.join(snake)[:len(K4)]
    sc = scorer.score_per_char(snake_text)
    best_route.append((sc, ncols, "snake", snake_text))

    # Columns top-bottom alternating direction
    col_snake = []
    for c in range(ncols):
        if c % 2 == 0:
            for r in range(nrows):
                col_snake.append(grid[r][c])
        else:
            for r in range(nrows-1, -1, -1):
                col_snake.append(grid[r][c])
    col_snake_text = ''.join(col_snake)[:len(K4)]
    sc = scorer.score_per_char(col_snake_text)
    best_route.append((sc, ncols, "col_snake", col_snake_text))

best_route.sort(reverse=True)
print(f"  Top 10 route cipher results:")
for sc, ncols, method, text in best_route[:10]:
    print(f"  {ncols}-col {method}: score={sc:.4f}")
    print(f"    -> {text[:60]}...")


# ============================================================
# COMPREHENSIVE RESULTS SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("COMPREHENSIVE RESULTS SUMMARY")
print("=" * 80)

# Collect all scored results
all_results = []

# From grid readings
for sc, ncols, method, result in best_grid_results[:5]:
    all_results.append((sc, f"Grid {ncols}-col {method}", result))

# From Nth letter
for sc, n, start, extracted in best_nth[:5]:
    all_results.append((sc, f"Every {n}th from {start}", extracted))

# From spiral
for sc, ncols, text in best_spiral[:3]:
    all_results.append((sc, f"Spiral {ncols}-col", text))

# From boustrophedon
for sc, ncols, text in best_boust[:3]:
    all_results.append((sc, f"Boustrophedon {ncols}-col", text))

# From rail fence
for sc, nrails, direction, text in best_rail[:5]:
    all_results.append((sc, f"Rail fence {nrails} ({direction})", text))

# From column transposition
for sc, ncols, method, text in best_col_trans[:5]:
    all_results.append((sc, f"Col trans {ncols} {method}", text))

# From route cipher
for sc, ncols, method, text in best_route[:5]:
    all_results.append((sc, f"Route {ncols}-col {method}", text))

# Reversed
all_results.append((sc_rev, "Reversed K4", k4_rev))

# Book cipher results
for book_name, book_text in [("K1+K2+K3", COMBINED_PT)]:
    results = book_cipher_by_position(K4, book_text, KRYPTOS_ALPHABET)
    for method, result in results:
        sc = scorer.score_per_char(result)
        all_results.append((sc, f"Book cipher ({method})", result))

# Sort all results
all_results.sort(reverse=True)

print(f"\nBaseline K4 score: {k4_score:.4f}")
print(f"English plaintext score (K3): {scorer.score_per_char(K3_PT):.4f}")
print(f"\nTop 20 results across all methods:\n")
print(f"{'Rank':>4} {'Score':>8} {'Method':<45} {'Preview'}")
print("-" * 120)
for i, (sc, method, text) in enumerate(all_results[:20]):
    flag = ""
    if sc > k4_score + 0.5:
        flag = " *** NOTABLE ***"
    elif sc > k4_score + 0.2:
        flag = " * interesting *"
    print(f"{i+1:>4} {sc:>8.4f} {method:<45} {text[:50]}...{flag}")


# ============================================================
# INTERESTING PATTERNS & OBSERVATIONS
# ============================================================

print("\n" + "=" * 80)
print("INTERESTING PATTERNS & OBSERVATIONS")
print("=" * 80)

print("\n--- Double letters form the sequence ---")
print(f"  BB, QQ, SS, ZZ, TT (positions: {[pos for pos, _ in doubles]})")
print(f"  Characters: {double_chars}")
print(f"  In KRYPTOS alphabet positions: {[KRYPTOS_ALPHABET.index(ch) if ch in KRYPTOS_ALPHABET else -1 for ch in double_chars]}")

print("\n--- K4 divided into 97 characters (prime number) ---")
print(f"  97 is prime, so no clean rectangular grid possible")
print(f"  Closest factorizations: 1x97, but could be padded to 98=2x7x7, 99=9x11, 100=10x10")

print("\n--- Letter at known plaintext positions ---")
# Sanborn revealed: position 64-69 is BERLIN, position 70-74 is CLOCK
# (0-indexed: 63-68 = BERLIN, 69-73 = CLOCK)
print(f"  K4[63:69] = '{K4[63:69]}' (should map to BERLIN)")
print(f"  K4[69:74] = '{K4[69:74]}' (should map to CLOCK)")
print(f"  K4[26:34] = '{K4[26:34]}' (should map to NORTHEAST per 2020 clue)")

# What does EASTNORTHEAST look like in K4?
print(f"\n--- Sanborn's clue: positions 22-25 = EAST, 26-34 = NORTHEAST ---")
print(f"  K4[21:25] = '{K4[21:25]}' -> EAST")
print(f"  K4[25:34] = '{K4[25:34]}' -> NORTHEAST")

print("\n--- Summary of double letter analysis ---")
spacing_dbl = [positions_of_doubles[i+1] - positions_of_doubles[i]
               for i in range(len(positions_of_doubles)-1)]
print(f"  Double positions: {positions_of_doubles}")
print(f"  Spacings: {spacing_dbl}")
print(f"  Sum of spacings: {sum(spacing_dbl)}")
print(f"  Do spacings correspond to letters? {''.join(chr(ord('A') + s) for s in spacing_dbl)}")

# Check if positions of doubles encode coordinates
print(f"\n--- Do double-letter positions encode coordinates? ---")
for i in range(0, len(positions_of_doubles) - 1, 2):
    lat_val = positions_of_doubles[i]
    lon_val = positions_of_doubles[i+1] if i+1 < len(positions_of_doubles) else None
    if lon_val is not None:
        # CIA HQ is approximately 38.95N, 77.15W
        print(f"  Pair ({lat_val}, {lon_val}) -> could represent {lat_val}.{lon_val} or {lon_val}.{lat_val}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("""
KEY FINDINGS:
- All non-mathematical methods tested against quadgram scoring baseline
- Double letters (BB, QQ, SS, ZZ, TT) at positions noted for potential word boundaries
- Physical grid layouts tested with spiral, boustrophedon, zigzag, and route readings
- Steganographic extractions tested at mathematical positions and frequency-based selection
- Book cipher approaches using K1-K3 plaintexts explored
- Letter shape binary encoding tested (Bacon cipher variant)
- Substitution patterns analyzed via bigram/trigram frequency and Kasiski examination

The top-scoring methods are listed above. Any method scoring significantly above
the K4 baseline (-3.x range) toward the English plaintext range (-2.x range)
warrants deeper investigation.
""")
