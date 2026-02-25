#!/usr/bin/env python3
"""
K4 Double-Layer Cipher Hypothesis Tester
=========================================
Tests whether K4 uses TWO layers of encryption:
  Layer 1: Vigenere with period 29 and KRYPTOS alphabet
  Layer 2: One of several classical ciphers

Known:
  - Vigenere key (partial): OYNKYELYOIECBAQK?????RDUMRIYW
  - Best guess for unknowns: BQTNN -> full key OYNKYELYOIECBAQKBQTNNRDUMRIYW
  - Positions 21-33 decrypt to EASTNORTHEAST
  - Positions 63-73 decrypt to BERLINCLOCK
  - Other positions produce gibberish => suggests a second layer

Hypotheses tested:
  1. Vig-29 then Simple Substitution
  2. Vig-29 then Columnar Transposition (widths 7-14)
  3. Vig-29 then Route Cipher (spiral, zigzag, diagonal)
  4. Vig-29 then Rail Fence (2-10 rails)
  5. Vig-29 then Skip/Decimation (all N coprime to 97)

Each uses simulated annealing with 500,000 iterations.
Scoring: quadgram log-probability + bonus for known crib words.
"""

import math
import random
import time
import sys
from itertools import permutations

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
N = len(K4)  # 97

# Partial key: positions 16-20 are unknown
KNOWN_KEY = list("OYNKYELYOIECBAQK?????RDUMRIYW")
UNKNOWN_POS = [16, 17, 18, 19, 20]

# Best-guess full key (from prior analysis)
BEST_GUESS_KEY = "OYNKYELYOIECBAQKBQTNNRDUMRIYW"

# ============================================================
# KRYPTOS ALPHABET UTILITIES
# ============================================================

_K2I = {c: i for i, c in enumerate(KRYPTOS)}

def k_idx(c):
    return _K2I[c]

def k_chr(i):
    return KRYPTOS[i % 26]

# ============================================================
# QUADGRAM SCORER
# ============================================================

print("Loading quadgrams...")
QG_LOG = {}
_total = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            _total += count
            QG_LOG[gram] = count

# Convert to log probabilities
for gram in QG_LOG:
    QG_LOG[gram] = math.log10(QG_LOG[gram] / _total)
QG_FLOOR = math.log10(0.01 / _total)

def qscore(text):
    """Quadgram log-probability score."""
    s = 0.0
    for i in range(len(text) - 3):
        q = text[i:i+4]
        s += QG_LOG.get(q, QG_FLOOR)
    return s

# ============================================================
# CRIB WORDS AND BONUS SCORING
# ============================================================

CRIB_WORDS = [
    "EASTNORTHEAST", "BERLINCLOCK", "NORTHEAST", "BERLIN", "CLOCK",
    "SLOWLY", "DESPERATELY", "SHADOW", "LAYER", "UNDERGROUND",
    "BURIED", "HIDDEN", "SECRET", "DEGREE", "BETWEEN",
    "COMPASS", "BEARING", "LANGLEY", "ITWAS", "TOTALLY",
    "INVISIBLE", "HOWSTHAT", "POSSIBLE", "THEYD", "USED",
    "EARTHS", "MAGNETIC", "FIELD", "INFORMATION", "GATHERED",
    "DIGETAL", "INTERPRETED",
]

def word_bonus(text):
    """Large bonus for crib words found anywhere in text."""
    bonus = 0
    for w in CRIB_WORDS:
        if w in text:
            bonus += len(w) * 8  # strong bonus per character
    return bonus

def found_words(text):
    """Return list of crib words found in text."""
    return [w for w in CRIB_WORDS if w in text]

# ============================================================
# VIGENERE DECRYPT (KRYPTOS ALPHABET)
# ============================================================

def vig_decrypt(ct, key):
    """Decrypt ciphertext with Vigenere using KRYPTOS alphabet."""
    pt = []
    klen = len(key)
    for i, c in enumerate(ct):
        ci = k_idx(c)
        ki = k_idx(key[i % klen])
        pt.append(k_chr((ci - ki) % 26))
    return ''.join(pt)

# ============================================================
# KEY BUILDING
# ============================================================

def make_key(unknowns):
    """Build full 29-char key from 5 unknown indices (0-25 each)."""
    key = list(KNOWN_KEY)
    for i, v in enumerate(unknowns):
        key[UNKNOWN_POS[i]] = KRYPTOS[v % 26]
    return ''.join(key)

def get_unknowns_from_key(key_str):
    """Extract the 5 unknown values from a key string."""
    return [k_idx(key_str[p]) for p in UNKNOWN_POS]

# ============================================================
# RESULT TRACKING
# ============================================================

class TopResults:
    """Track the top N results for a given hypothesis."""
    def __init__(self, n=5):
        self.n = n
        self.results = []  # list of (score, info_dict)

    def add(self, score, info):
        self.results.append((score, info))
        self.results.sort(key=lambda x: -x[0])
        self.results = self.results[:self.n]

    def best_score(self):
        return self.results[0][0] if self.results else -999999

    def print_results(self, label):
        print(f"\n{'='*80}")
        print(f"  TOP 5 RESULTS: {label}")
        print(f"{'='*80}")
        for rank, (score, info) in enumerate(self.results, 1):
            highlight = " <<<< HIGH SCORE" if score > -500 else ""
            print(f"\n  #{rank}  Score: {score:.2f}{highlight}")
            for k, v in info.items():
                print(f"       {k}: {v}")
            # Check for words
            if 'plaintext' in info:
                wds = found_words(info['plaintext'])
                if wds:
                    print(f"       *** CRIB WORDS FOUND: {wds} ***")
        print()

# ============================================================
# HYPOTHESIS 1: VIGENERE-29 then SIMPLE SUBSTITUTION
# ============================================================

def test_vig_then_substitution(iterations=500000):
    """
    Decrypt with Vig-29, then apply a monoalphabetic substitution.
    SA optimizes the substitution table + the 5 unknown key positions.
    """
    print("\n" + "#"*80)
    print("# HYPOTHESIS 1: VIGENERE-29 then SIMPLE SUBSTITUTION")
    print("#"*80)
    print(f"  Iterations: {iterations}")

    top = TopResults(5)
    t0 = time.time()

    # Run multiple SA restarts
    num_restarts = 5
    for restart in range(num_restarts):
        iters_per = iterations // num_restarts

        # Initialize: random substitution + best-guess unknowns
        sub = list(range(26))
        random.shuffle(sub)
        unknowns = get_unknowns_from_key(BEST_GUESS_KEY)
        if restart > 0:
            # Perturb unknowns on restarts
            for i in range(5):
                unknowns[i] = random.randrange(26)

        # Current state
        key = make_key(unknowns)
        vig_out = vig_decrypt(K4, key)
        # Apply substitution
        pt = ''.join(k_chr(sub[k_idx(c)]) for c in vig_out)
        current_score = qscore(pt) + word_bonus(pt)

        best_score = current_score
        best_sub = sub[:]
        best_unknowns = unknowns[:]
        best_pt = pt

        T = 10.0
        alpha = 1.0 - (3.0 / iters_per)  # cool to ~T*exp(-3) by end

        for it in range(iters_per):
            new_sub = sub[:]
            new_unknowns = unknowns[:]

            r = random.random()
            if r < 0.75:
                # Swap two entries in substitution
                i, j = random.sample(range(26), 2)
                new_sub[i], new_sub[j] = new_sub[j], new_sub[i]
            elif r < 0.90:
                # Swap two AND another two entries
                i, j = random.sample(range(26), 2)
                new_sub[i], new_sub[j] = new_sub[j], new_sub[i]
                i2, j2 = random.sample(range(26), 2)
                new_sub[i2], new_sub[j2] = new_sub[j2], new_sub[i2]
            else:
                # Mutate one unknown key position
                pos = random.randrange(5)
                new_unknowns[pos] = random.randrange(26)

            key = make_key(new_unknowns)
            vig_out = vig_decrypt(K4, key)
            pt = ''.join(k_chr(new_sub[k_idx(c)]) for c in vig_out)
            new_score = qscore(pt) + word_bonus(pt)

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
                sub = new_sub
                unknowns = new_unknowns
                current_score = new_score

                if current_score > best_score:
                    best_score = current_score
                    best_sub = sub[:]
                    best_unknowns = unknowns[:]
                    best_pt = pt

            T *= alpha

        # Build substitution table string
        sub_str = ''.join(k_chr(s) for s in best_sub)
        full_key = make_key(best_unknowns)
        top.add(best_score, {
            'key': full_key,
            'substitution': f"KRYPTOS -> {sub_str}",
            'plaintext': best_pt,
            'restart': restart,
        })

        print(f"  Restart {restart+1}/{num_restarts}: best={best_score:.2f}  PT={best_pt[:40]}...")

    elapsed = time.time() - t0
    print(f"  Total time: {elapsed:.1f}s")
    top.print_results("VIG-29 + SIMPLE SUBSTITUTION")
    return top

# ============================================================
# HYPOTHESIS 2: VIGENERE-29 then COLUMNAR TRANSPOSITION
# ============================================================

def columnar_untranspose(text, ncols, col_order):
    """
    Reverse columnar transposition.
    text was produced by: write plaintext in rows of width ncols,
    then read columns in col_order. We reverse this.
    """
    n = len(text)
    nrows = (n + ncols - 1) // ncols
    short_cols = nrows * ncols - n  # number of columns that are short (nrows-1)

    # Columns in col_order: first (ncols - short_cols) are long (nrows), rest are short (nrows-1)
    col_lens = {}
    for rank, col in enumerate(col_order):
        if rank < ncols - short_cols:
            col_lens[col] = nrows
        else:
            col_lens[col] = nrows - 1

    # Split text into columns in col_order
    cols = {}
    pos = 0
    for col in col_order:
        length = col_lens[col]
        cols[col] = text[pos:pos+length]
        pos += length

    # Read by rows
    result = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(cols.get(col, '')):
                result.append(cols[col][row])
    return ''.join(result)

def test_vig_then_columnar(iterations=500000):
    """
    After Vig-29 decrypt, un-transpose with various column widths.
    SA optimizes column order + unknown key positions.
    Cribs must appear in output but NOT necessarily at positions 21 and 63.
    """
    print("\n" + "#"*80)
    print("# HYPOTHESIS 2: VIGENERE-29 then COLUMNAR TRANSPOSITION")
    print("#"*80)
    print(f"  Iterations per width: {iterations}")

    widths = [7, 8, 9, 10, 11, 13, 14]
    global_top = TopResults(5)
    t0 = time.time()

    for ncols in widths:
        print(f"\n  --- Testing width {ncols} ---")
        top = TopResults(5)

        num_restarts = 3
        iters_per = iterations // num_restarts

        for restart in range(num_restarts):
            # Initialize
            col_order = list(range(ncols))
            random.shuffle(col_order)
            unknowns = get_unknowns_from_key(BEST_GUESS_KEY)
            if restart > 0:
                for i in range(5):
                    unknowns[i] = random.randrange(26)

            key = make_key(unknowns)
            vig_out = vig_decrypt(K4, key)
            pt = columnar_untranspose(vig_out, ncols, col_order)
            current_score = qscore(pt) + word_bonus(pt)

            best_score = current_score
            best_order = col_order[:]
            best_unknowns = unknowns[:]
            best_pt = pt

            T = 10.0
            alpha = 1.0 - (3.0 / iters_per)

            for it in range(iters_per):
                new_order = col_order[:]
                new_unknowns = unknowns[:]

                r = random.random()
                if r < 0.50:
                    # Swap two columns
                    i, j = random.sample(range(ncols), 2)
                    new_order[i], new_order[j] = new_order[j], new_order[i]
                elif r < 0.70:
                    # Move a column
                    i = random.randrange(ncols)
                    j = random.randrange(ncols)
                    col = new_order.pop(i)
                    new_order.insert(j, col)
                elif r < 0.85:
                    # Reverse a segment of the column order
                    i = random.randrange(ncols)
                    j = random.randrange(i+1, min(i+5, ncols)+1)
                    new_order[i:j] = reversed(new_order[i:j])
                else:
                    # Mutate unknown key position
                    pos = random.randrange(5)
                    new_unknowns[pos] = random.randrange(26)

                key = make_key(new_unknowns)
                vig_out = vig_decrypt(K4, key)
                pt = columnar_untranspose(vig_out, ncols, new_order)
                new_score = qscore(pt) + word_bonus(pt)

                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
                    col_order = new_order
                    unknowns = new_unknowns
                    current_score = new_score

                    if current_score > best_score:
                        best_score = current_score
                        best_order = col_order[:]
                        best_unknowns = unknowns[:]
                        best_pt = pt

                T *= alpha

            full_key = make_key(best_unknowns)
            top.add(best_score, {
                'key': full_key,
                'width': ncols,
                'col_order': best_order,
                'plaintext': best_pt,
            })
            global_top.add(best_score, {
                'key': full_key,
                'width': ncols,
                'col_order': best_order,
                'plaintext': best_pt,
            })

        # Print best for this width
        bs = top.results[0] if top.results else None
        if bs:
            wds = found_words(bs[1]['plaintext'])
            print(f"    Best score: {bs[0]:.2f}  Words: {wds}")
            print(f"    PT: {bs[1]['plaintext'][:50]}...")
            print(f"    Col order: {bs[1]['col_order']}")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    global_top.print_results("VIG-29 + COLUMNAR TRANSPOSITION (all widths)")
    return global_top

# ============================================================
# HYPOTHESIS 3: VIGENERE-29 then ROUTE CIPHER
# ============================================================

def route_spiral_read(grid, nrows, ncols, clockwise=True):
    """Read a grid in a spiral pattern."""
    result = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        if clockwise:
            for c in range(left, right + 1):
                if top < nrows and c < ncols and top * ncols + c < len(grid):
                    result.append(grid[top][c])
            top += 1
            for r in range(top, bottom + 1):
                if r < nrows and right < ncols and r * ncols + right < len(grid):
                    result.append(grid[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if bottom < nrows and c < ncols and bottom * ncols + c < len(grid):
                        result.append(grid[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if r < nrows and left < ncols and r * ncols + left < len(grid):
                        result.append(grid[r][left])
                left += 1
        else:
            # Counter-clockwise
            for r in range(top, bottom + 1):
                if r < nrows and left < ncols:
                    result.append(grid[r][left])
            left += 1
            for c in range(left, right + 1):
                if bottom < nrows and c < ncols:
                    result.append(grid[bottom][c])
            bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    if r < nrows and right < ncols:
                        result.append(grid[r][right])
                right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    if top < nrows and c < ncols:
                        result.append(grid[top][c])
                top += 1
    return ''.join(result[:N])

def route_zigzag_read(grid, nrows, ncols):
    """Read a grid in a zigzag (boustrophedon) pattern."""
    result = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                if r < len(grid) and c < len(grid[r]):
                    result.append(grid[r][c])
        else:
            for c in range(ncols - 1, -1, -1):
                if r < len(grid) and c < len(grid[r]):
                    result.append(grid[r][c])
    return ''.join(result[:N])

def route_diagonal_read(grid, nrows, ncols):
    """Read a grid by diagonals (top-left to bottom-right)."""
    result = []
    for d in range(nrows + ncols - 1):
        if d % 2 == 0:
            r = min(d, nrows - 1)
            c = d - r
            while r >= 0 and c < ncols:
                if r < len(grid) and c < len(grid[r]):
                    result.append(grid[r][c])
                r -= 1
                c += 1
        else:
            c = min(d, ncols - 1)
            r = d - c
            while c >= 0 and r < nrows:
                if r < len(grid) and c < len(grid[r]):
                    result.append(grid[r][c])
                r += 1
                c -= 1
    return ''.join(result[:N])

def route_column_read(grid, nrows, ncols):
    """Read a grid column by column (top to bottom, left to right)."""
    result = []
    for c in range(ncols):
        for r in range(nrows):
            if r < len(grid) and c < len(grid[r]):
                result.append(grid[r][c])
    return ''.join(result[:N])

def route_reverse_row_read(grid, nrows, ncols):
    """Read a grid row by row but bottom to top."""
    result = []
    for r in range(nrows - 1, -1, -1):
        for c in range(ncols):
            if r < len(grid) and c < len(grid[r]):
                result.append(grid[r][c])
    return ''.join(result[:N])

def invert_route(text, nrows, ncols, route_func):
    """
    Given text that was read from a grid via route_func,
    figure out what the row-by-row reading would be.

    Method: create a grid, fill it row-by-row with position indices,
    read via the route to get the reading order, then invert.
    """
    total = nrows * ncols
    # Build grid of indices
    idx_grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < N:
                row.append(pos)
            else:
                row.append(-1)  # padding
            pos += 1
        idx_grid.append(row)

    # Read indices in route order
    route_order_str = route_func(
        [[chr(idx_grid[r][c] + 32) if idx_grid[r][c] >= 0 else '\x00'
          for c in range(ncols)] for r in range(nrows)],
        nrows, ncols
    )

    # Actually, let's do this properly: map position-in-route to position-in-grid
    # Create a grid filled with index chars, read via route
    grid_chars = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < N:
                row.append(str(pos).zfill(3))
            else:
                row.append("---")
            pos += 1
        grid_chars.append(row)

    # Instead, use a simpler approach: generate the route reading order
    # by putting sequential chars in a grid and reading them
    marker_grid = []
    pos = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if pos < N:
                row.append(chr(pos % 94 + 33))  # use printable ASCII
            else:
                row.append('\x00')
            pos += 1
        marker_grid.append(row)

    # Actually, let me just directly compute the route order as indices
    route_indices = []
    # Simulate route_func but collect indices instead
    # This is route-specific, so let me build a position grid and read it

    pos_grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < N:
                row.append(idx)
                idx += 1
            else:
                row.append(-1)
        pos_grid.append(row)

    return pos_grid  # We'll use a different approach below

def get_spiral_order(nrows, ncols, n, clockwise=True):
    """Get the reading order indices for a spiral."""
    order = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        if clockwise:
            for c in range(left, right + 1):
                idx = top * ncols + c
                if idx < n:
                    order.append(idx)
            top += 1
            for r in range(top, bottom + 1):
                idx = r * ncols + right
                if idx < n:
                    order.append(idx)
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    idx = bottom * ncols + c
                    if idx < n:
                        order.append(idx)
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    idx = r * ncols + left
                    if idx < n:
                        order.append(idx)
                left += 1
        else:
            for r in range(top, bottom + 1):
                idx = r * ncols + left
                if idx < n:
                    order.append(idx)
            left += 1
            for c in range(left, right + 1):
                idx = bottom * ncols + c
                if idx < n:
                    order.append(idx)
            bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1):
                    idx = r * ncols + right
                    if idx < n:
                        order.append(idx)
                right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1):
                    idx = top * ncols + c
                    if idx < n:
                        order.append(idx)
                top += 1
    return order[:n]

def get_zigzag_order(nrows, ncols, n):
    """Get the reading order for zigzag (boustrophedon)."""
    order = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                idx = r * ncols + c
                if idx < n:
                    order.append(idx)
        else:
            for c in range(ncols - 1, -1, -1):
                idx = r * ncols + c
                if idx < n:
                    order.append(idx)
    return order[:n]

def get_diagonal_order(nrows, ncols, n):
    """Get the reading order for diagonal traversal."""
    order = []
    for d in range(nrows + ncols - 1):
        if d % 2 == 0:
            r = min(d, nrows - 1)
            c = d - r
            while r >= 0 and c < ncols:
                idx = r * ncols + c
                if idx < n:
                    order.append(idx)
                r -= 1
                c += 1
        else:
            c = min(d, ncols - 1)
            r = d - c
            while c >= 0 and r < nrows:
                idx = r * ncols + c
                if idx < n:
                    order.append(idx)
                r += 1
                c -= 1
    return order[:n]

def get_column_order(nrows, ncols, n):
    """Get the reading order for column-by-column."""
    order = []
    for c in range(ncols):
        for r in range(nrows):
            idx = r * ncols + c
            if idx < n:
                order.append(idx)
    return order[:n]

def apply_inverse_route(text, route_order):
    """
    If ciphertext was produced by writing plaintext into grid row-by-row
    then reading via route_order, this inverts it.
    route_order[i] = grid position that was read at position i.
    So: ciphertext[i] came from plaintext[route_order[i]].
    To invert: plaintext[route_order[i]] = ciphertext[i].
    """
    n = len(text)
    pt = ['?'] * n
    for i, grid_pos in enumerate(route_order):
        if i < n and grid_pos < n:
            pt[grid_pos] = text[i]
    return ''.join(pt)

def apply_route(text, route_order):
    """
    If plaintext was in the grid row-by-row, reading via route_order gives ciphertext.
    ciphertext[i] = plaintext[route_order[i]]
    """
    return ''.join(text[route_order[i]] for i in range(min(len(text), len(route_order))))

def test_vig_then_route(iterations=500000):
    """
    Write Vig-29 output into a grid, read by different routes.
    Test grid sizes: 7x14(-1), 8x13(-7), 9x11(-2), 10x10(-3)
    Routes: spiral CW, spiral CCW, zigzag, diagonal, column-by-column
    """
    print("\n" + "#"*80)
    print("# HYPOTHESIS 3: VIGENERE-29 then ROUTE CIPHER")
    print("#"*80)
    print(f"  Iterations: {iterations} (SA over unknown key positions)")

    grid_configs = [
        (7, 14, "7x14"),
        (8, 13, "8x13"),
        (9, 11, "9x11"),
        (10, 10, "10x10"),
        (14, 7, "14x7"),
        (13, 8, "13x8"),
        (11, 9, "11x9"),
    ]

    route_generators = {
        'spiral_CW': lambda nr, nc: get_spiral_order(nr, nc, N, clockwise=True),
        'spiral_CCW': lambda nr, nc: get_spiral_order(nr, nc, N, clockwise=False),
        'zigzag': lambda nr, nc: get_zigzag_order(nr, nc, N),
        'diagonal': lambda nr, nc: get_diagonal_order(nr, nc, N),
        'columns': lambda nr, nc: get_column_order(nr, nc, N),
    }

    global_top = TopResults(5)
    t0 = time.time()

    for nrows, ncols, label in grid_configs:
        if nrows * ncols < N:
            continue  # grid too small

        for route_name, gen_func in route_generators.items():
            route_order = gen_func(nrows, ncols)
            if len(route_order) < N:
                continue

            # Deduplicate: make sure all N positions are covered
            if len(set(route_order[:N])) < N:
                continue

            # SA to optimize the 5 unknown key positions
            unknowns = get_unknowns_from_key(BEST_GUESS_KEY)

            key = make_key(unknowns)
            vig_out = vig_decrypt(K4, key)

            # Two directions: route was applied to plaintext then Vig,
            # OR Vig was applied then route
            # We test: CT = route(Vig(PT, key))
            # => PT = Vig^-1(route^-1(CT), key)  ... but that changes Vig positions
            # OR: CT = Vig(route(PT), key)
            # => Vig^-1(CT, key) = route(PT) => PT = route^-1(Vig^-1(CT, key))
            # The second interpretation: Vig first, then un-route the result

            # Interpretation: Vig output was produced by route-reading the plaintext grid
            # So we invert the route on vig_out to get plaintext
            pt = apply_inverse_route(vig_out, route_order[:N])
            current_score = qscore(pt) + word_bonus(pt)

            best_score = current_score
            best_unknowns = unknowns[:]
            best_pt = pt

            T = 5.0
            sa_iters = iterations // (len(grid_configs) * len(route_generators))
            alpha = 1.0 - (3.0 / max(sa_iters, 1))

            for it in range(sa_iters):
                new_unknowns = unknowns[:]
                pos = random.randrange(5)
                new_unknowns[pos] = random.randrange(26)

                key = make_key(new_unknowns)
                vig_out = vig_decrypt(K4, key)
                pt = apply_inverse_route(vig_out, route_order[:N])
                new_score = qscore(pt) + word_bonus(pt)

                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
                    unknowns = new_unknowns
                    current_score = new_score
                    if current_score > best_score:
                        best_score = current_score
                        best_unknowns = unknowns[:]
                        best_pt = pt

                T *= alpha

            # Also test: route was applied AFTER Vig
            # CT = Vig(PT, key), but CT was route-read from intermediate grid
            # So actual CT positions are scrambled by route
            # This means: route(intermediate) = K4
            # intermediate[route_order[i]] = K4[i] ... wait, let's think again
            # If encryption was: write Vig output into grid, read by route to get CT
            # Then: K4[i] = vig_out[route_order[i]]
            # To decrypt: vig_out[route_order[i]] = K4[i]
            # => vig_out = inverse_route(K4)
            # Then PT = Vig^-1(vig_out, key)
            # But this changes which key position applies to which character!
            # Let's try this interpretation too:

            unknowns2 = get_unknowns_from_key(BEST_GUESS_KEY)
            unrouted_ct = apply_inverse_route(K4, route_order[:N])
            key2 = make_key(unknowns2)
            pt2 = vig_decrypt(unrouted_ct, key2)
            score2 = qscore(pt2) + word_bonus(pt2)

            best_score2 = score2
            best_unknowns2 = unknowns2[:]
            best_pt2 = pt2

            T = 5.0
            for it in range(sa_iters):
                new_unknowns2 = unknowns2[:]
                pos = random.randrange(5)
                new_unknowns2[pos] = random.randrange(26)

                key2 = make_key(new_unknowns2)
                pt2 = vig_decrypt(unrouted_ct, key2)
                score2 = qscore(pt2) + word_bonus(pt2)

                delta = score2 - best_score2
                if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
                    unknowns2 = new_unknowns2
                    if score2 > best_score2:
                        best_score2 = score2
                        best_unknowns2 = unknowns2[:]
                        best_pt2 = pt2

                T *= alpha

            # Record best of both interpretations
            full_key = make_key(best_unknowns)
            global_top.add(best_score, {
                'key': full_key,
                'grid': label,
                'route': route_name,
                'direction': 'Vig then un-route',
                'plaintext': best_pt,
            })

            full_key2 = make_key(best_unknowns2)
            global_top.add(best_score2, {
                'key': full_key2,
                'grid': label,
                'route': route_name,
                'direction': 'un-route CT then Vig',
                'plaintext': best_pt2,
            })

    elapsed = time.time() - t0
    print(f"  Total time: {elapsed:.1f}s")
    global_top.print_results("VIG-29 + ROUTE CIPHER")
    return global_top

# ============================================================
# HYPOTHESIS 4: VIGENERE-29 then RAIL FENCE
# ============================================================

def rail_fence_encode_order(n, num_rails):
    """Get the reading order for rail fence cipher with given number of rails."""
    if num_rails <= 1 or num_rails >= n:
        return list(range(n))

    # Build the rail assignments
    rails = [[] for _ in range(num_rails)]
    rail = 0
    direction = 1
    for i in range(n):
        rails[rail].append(i)
        if rail == 0:
            direction = 1
        elif rail == num_rails - 1:
            direction = -1
        rail += direction

    # Reading order: rail 0 first, then rail 1, etc.
    order = []
    for rail_list in rails:
        order.extend(rail_list)
    return order

def rail_fence_decode(text, num_rails):
    """Decode a rail fence cipher."""
    n = len(text)
    if num_rails <= 1 or num_rails >= n:
        return text

    encode_order = rail_fence_encode_order(n, num_rails)

    # encode_order[i] = original position that ends up at position i in encoded text
    # Wait: encode_order gives positions in original text in the order they appear in cipher
    # So cipher[j] = plain[encode_order[j]]
    # To decode: plain[encode_order[j]] = cipher[j]

    plain = ['?'] * n
    for j, orig_pos in enumerate(encode_order):
        plain[orig_pos] = text[j]
    return ''.join(plain)

def test_vig_then_railfence(iterations=500000):
    """
    For each rail count (2-10), un-do the rail fence on Vig-29 output.
    SA optimizes the 5 unknown key positions.
    """
    print("\n" + "#"*80)
    print("# HYPOTHESIS 4: VIGENERE-29 then RAIL FENCE")
    print("#"*80)
    print(f"  Iterations per rail count: {iterations // 9}")

    global_top = TopResults(5)
    t0 = time.time()

    for num_rails in range(2, 11):
        iters = iterations // 9

        # SA over the 5 unknown key positions
        unknowns = get_unknowns_from_key(BEST_GUESS_KEY)

        key = make_key(unknowns)
        vig_out = vig_decrypt(K4, key)

        # Interpretation 1: PT was rail-fenced, then Vig encrypted
        # CT = Vig(railfence(PT), key)
        # => railfence(PT) = Vig^-1(CT, key) = vig_out
        # => PT = rail_fence_decode(vig_out)
        pt1 = rail_fence_decode(vig_out, num_rails)
        score1 = qscore(pt1) + word_bonus(pt1)

        best_score1 = score1
        best_unknowns1 = unknowns[:]
        best_pt1 = pt1

        # Interpretation 2: Vig output was rail-fenced to produce CT
        # CT = railfence(Vig(PT, key))
        # => Vig(PT, key) = rail_fence_decode(CT)
        # => PT = Vig^-1(rail_fence_decode(CT), key)
        # But this changes Vig alignment!
        decoded_ct = rail_fence_decode(K4, num_rails)
        pt2 = vig_decrypt(decoded_ct, key)
        score2 = qscore(pt2) + word_bonus(pt2)

        best_score2 = score2
        best_unknowns2 = unknowns[:]
        best_pt2 = pt2

        T = 5.0
        alpha = 1.0 - (3.0 / max(iters, 1))

        unknowns1 = unknowns[:]
        unknowns2 = unknowns[:]
        cur_score1 = score1
        cur_score2 = score2

        for it in range(iters):
            # Interpretation 1
            new_unk1 = unknowns1[:]
            pos = random.randrange(5)
            new_unk1[pos] = random.randrange(26)

            key1 = make_key(new_unk1)
            vo1 = vig_decrypt(K4, key1)
            p1 = rail_fence_decode(vo1, num_rails)
            s1 = qscore(p1) + word_bonus(p1)

            delta1 = s1 - cur_score1
            if delta1 > 0 or random.random() < math.exp(delta1 / max(T, 0.001)):
                unknowns1 = new_unk1
                cur_score1 = s1
                if s1 > best_score1:
                    best_score1 = s1
                    best_unknowns1 = unknowns1[:]
                    best_pt1 = p1

            # Interpretation 2
            new_unk2 = unknowns2[:]
            pos = random.randrange(5)
            new_unk2[pos] = random.randrange(26)

            key2 = make_key(new_unk2)
            p2 = vig_decrypt(decoded_ct, key2)
            s2 = qscore(p2) + word_bonus(p2)

            delta2 = s2 - cur_score2
            if delta2 > 0 or random.random() < math.exp(delta2 / max(T, 0.001)):
                unknowns2 = new_unk2
                cur_score2 = s2
                if s2 > best_score2:
                    best_score2 = s2
                    best_unknowns2 = unknowns2[:]
                    best_pt2 = p2

            T *= alpha

        wds1 = found_words(best_pt1)
        wds2 = found_words(best_pt2)
        print(f"  Rails={num_rails}: interp1={best_score1:.2f} words={wds1}  |  interp2={best_score2:.2f} words={wds2}")

        global_top.add(best_score1, {
            'key': make_key(best_unknowns1),
            'rails': num_rails,
            'direction': 'Vig then un-railfence',
            'plaintext': best_pt1,
        })
        global_top.add(best_score2, {
            'key': make_key(best_unknowns2),
            'rails': num_rails,
            'direction': 'un-railfence CT then Vig',
            'plaintext': best_pt2,
        })

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    global_top.print_results("VIG-29 + RAIL FENCE")
    return global_top

# ============================================================
# HYPOTHESIS 5: VIGENERE-29 then SKIP / DECIMATION
# ============================================================

def decimation_decode(text, step):
    """
    Decode a decimation/skip cipher.
    If the encoder read every step-th character (mod n) from plaintext,
    we reverse that.
    Encoder: cipher[i] = plain[(i * step) % n]
    Decoder: plain[(i * step) % n] = cipher[i]
    """
    n = len(text)
    plain = ['?'] * n
    for i in range(n):
        pos = (i * step) % n
        plain[pos] = text[i]
    return ''.join(plain)

def decimation_encode_order(n, step):
    """Get the reading order for decimation with given step."""
    return [(i * step) % n for i in range(n)]

def test_vig_then_decimation(iterations=500000):
    """
    Read every Nth character from Vig-29 output.
    97 is prime, so all 1 < N < 97 are coprime to 97.
    Test all such N. SA optimizes unknown key positions.
    """
    print("\n" + "#"*80)
    print("# HYPOTHESIS 5: VIGENERE-29 then SKIP/DECIMATION")
    print("#"*80)
    print(f"  Testing all steps 2..96 (97 is prime, all coprime)")
    print(f"  Iterations per step: {iterations // 95}")

    global_top = TopResults(5)
    t0 = time.time()

    iters_per_step = iterations // 95

    for step in range(2, 97):
        # SA over the 5 unknown key positions
        unknowns = get_unknowns_from_key(BEST_GUESS_KEY)

        key = make_key(unknowns)
        vig_out = vig_decrypt(K4, key)

        # Interpretation 1: PT was decimated then Vig encrypted
        # CT = Vig(decimate(PT, step), key)
        # decimate(PT, step) = Vig^-1(CT, key) = vig_out
        # PT = decimation_decode(vig_out, step)
        pt1 = decimation_decode(vig_out, step)
        score1 = qscore(pt1) + word_bonus(pt1)

        best_score1 = score1
        best_unknowns1 = unknowns[:]
        best_pt1 = pt1

        # Interpretation 2: Vig output was decimated to produce CT
        # CT = decimate(Vig(PT, key), step)
        # Vig(PT, key) = decimation_decode(CT, step)
        # PT = Vig^-1(decimation_decode(CT, step), key)
        decoded_ct = decimation_decode(K4, step)
        pt2 = vig_decrypt(decoded_ct, key)
        score2 = qscore(pt2) + word_bonus(pt2)

        best_score2 = score2
        best_unknowns2 = unknowns[:]
        best_pt2 = pt2

        T = 5.0
        alpha = 1.0 - (3.0 / max(iters_per_step, 1))

        unknowns1 = unknowns[:]
        unknowns2 = unknowns[:]
        cur1 = score1
        cur2 = score2

        for it in range(iters_per_step):
            # Interp 1
            nu1 = unknowns1[:]
            pos = random.randrange(5)
            nu1[pos] = random.randrange(26)
            k1 = make_key(nu1)
            vo1 = vig_decrypt(K4, k1)
            p1 = decimation_decode(vo1, step)
            s1 = qscore(p1) + word_bonus(p1)
            d1 = s1 - cur1
            if d1 > 0 or random.random() < math.exp(d1 / max(T, 0.001)):
                unknowns1 = nu1
                cur1 = s1
                if s1 > best_score1:
                    best_score1 = s1
                    best_unknowns1 = nu1[:]
                    best_pt1 = p1

            # Interp 2
            nu2 = unknowns2[:]
            pos = random.randrange(5)
            nu2[pos] = random.randrange(26)
            k2 = make_key(nu2)
            p2 = vig_decrypt(decoded_ct, k2)
            s2 = qscore(p2) + word_bonus(p2)
            d2 = s2 - cur2
            if d2 > 0 or random.random() < math.exp(d2 / max(T, 0.001)):
                unknowns2 = nu2
                cur2 = s2
                if s2 > best_score2:
                    best_score2 = s2
                    best_unknowns2 = nu2[:]
                    best_pt2 = p2

            T *= alpha

        global_top.add(best_score1, {
            'key': make_key(best_unknowns1),
            'step': step,
            'direction': 'Vig then un-decimation',
            'plaintext': best_pt1,
        })
        global_top.add(best_score2, {
            'key': make_key(best_unknowns2),
            'step': step,
            'direction': 'un-decimation CT then Vig',
            'plaintext': best_pt2,
        })

    elapsed = time.time() - t0
    print(f"  Total time: {elapsed:.1f}s")
    global_top.print_results("VIG-29 + SKIP/DECIMATION")
    return global_top

# ============================================================
# MAIN
# ============================================================

def print_banner():
    print("="*80)
    print("  K4 DOUBLE-LAYER CIPHER HYPOTHESIS TESTER")
    print("  Testing 5 second-layer hypotheses with Simulated Annealing")
    print("="*80)
    print(f"  K4 ciphertext ({N} chars): {K4}")
    print(f"  KRYPTOS alphabet: {KRYPTOS}")
    print(f"  Partial key:      {''.join(KNOWN_KEY)}")
    print(f"  Best-guess key:   {BEST_GUESS_KEY}")
    print()

    # Show what the best-guess key produces
    pt = vig_decrypt(K4, BEST_GUESS_KEY)
    print(f"  Vig decrypt with best-guess key:")
    print(f"    {pt}")
    score = qscore(pt)
    wds = found_words(pt)
    print(f"    Quadgram score: {score:.2f}")
    print(f"    Crib words found: {wds}")
    print()

    # Highlight the cribs
    highlight = list(pt)
    for w in ['EASTNORTHEAST', 'BERLINCLOCK']:
        idx = pt.find(w)
        if idx >= 0:
            print(f"    '{w}' at position {idx}")
    print()

def print_final_summary(all_results):
    print("\n" + "="*80)
    print("  GRAND SUMMARY: ALL HYPOTHESES")
    print("="*80)

    # Collect all results across hypotheses
    grand = TopResults(20)
    for label, top in all_results:
        for score, info in top.results:
            info_with_label = dict(info)
            info_with_label['hypothesis'] = label
            grand.add(score, info_with_label)

    print(f"\n  Top 20 results across ALL hypotheses:\n")

    for rank, (score, info) in enumerate(grand.results, 1):
        highlight = " <<<< HIGH SCORE >>>>" if score > -500 else ""
        pt = info.get('plaintext', '')
        wds = found_words(pt)
        hyp = info.get('hypothesis', '?')
        print(f"  #{rank:2d}  Score={score:8.2f}  Hypothesis: {hyp}{highlight}")
        print(f"       PT: {pt[:60]}...")
        if wds:
            print(f"       *** WORDS: {wds} ***")

        # Print key details
        key_info = {k: v for k, v in info.items()
                    if k not in ('plaintext', 'hypothesis')}
        for k, v in key_info.items():
            print(f"       {k}: {v}")
        print()

    # Check for any high scores
    high_scores = [(s, i) for s, i in grand.results if s > -500]
    if high_scores:
        print(f"\n  *** {len(high_scores)} RESULT(S) ABOVE -500 THRESHOLD ***")
        for s, i in high_scores:
            print(f"      Score {s:.2f}: {i.get('hypothesis', '?')}")
    else:
        print("\n  No results above the -500 threshold.")
        print("  The double-layer hypothesis may not apply, or the correct")
        print("  second layer is not among those tested.")

    print("\n" + "="*80)
    print("  ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    random.seed(42)  # reproducible results
    print_banner()

    SA_ITERS = 500000

    all_results = []

    # Hypothesis 1: Vig + Simple Substitution
    top1 = test_vig_then_substitution(iterations=SA_ITERS)
    all_results.append(("Vig-29 + Simple Substitution", top1))

    # Hypothesis 2: Vig + Columnar Transposition
    top2 = test_vig_then_columnar(iterations=SA_ITERS)
    all_results.append(("Vig-29 + Columnar Transposition", top2))

    # Hypothesis 3: Vig + Route Cipher
    top3 = test_vig_then_route(iterations=SA_ITERS)
    all_results.append(("Vig-29 + Route Cipher", top3))

    # Hypothesis 4: Vig + Rail Fence
    top4 = test_vig_then_railfence(iterations=SA_ITERS)
    all_results.append(("Vig-29 + Rail Fence", top4))

    # Hypothesis 5: Vig + Skip/Decimation
    top5 = test_vig_then_decimation(iterations=SA_ITERS)
    all_results.append(("Vig-29 + Skip/Decimation", top5))

    # Final summary
    print_final_summary(all_results)
