#!/usr/bin/env python3
"""
K4 Deep Transposition + Vigenere Attack

HYPOTHESIS: K4 = Vigenere(Transposition(plaintext)) or K4 = Transposition(Vigenere(plaintext))

If K4 = Vig(Trans(PT)):
  - Vig_decrypt(K4) = Trans(PT)
  - We need to un-transpose the Vigenere output to recover PT

If K4 = Trans(Vig(PT)):
  - Un-transpose K4 first, then Vig_decrypt to get PT

Uses quadgram scoring + word bonus for known Kryptos-related words.
"""

import math
import random
import time
import sys
from itertools import permutations
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
LEN_K4 = len(K4)  # 97
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known partial key (29 chars, positions 16-20 unknown)
PARTIAL_KEY = "OYNKYELYOIECBAQK?????RDUMRIYW"
BEST_KEY_GUESS = "OYNKYELYOIECBAQKBQTNNRDUMRIYW"

# Words to look for in final plaintext (with bonuses)
BONUS_WORDS = {
    "EASTNORTHEAST": 50, "BERLINCLOCK": 50,
    "NORTHEAST": 40, "BERLIN": 35, "CLOCK": 30,
    "EGYPT": 25, "CAIRO": 25, "PYRAMID": 25, "PHARAOH": 25,
    "TUTANKHAMUN": 30, "WONDERFUL": 25, "THINGS": 20,
    "COMPASS": 20, "WORLD": 15, "TIME": 12,
    "ALEXANDERPLATZ": 30, "ALEXANDRIA": 25,
    "SLOWLY": 20, "DESPERATELY": 25, "SHADOW": 20,
    "BETWEEN": 20, "HIDDEN": 20, "BURIED": 20, "SECRET": 20,
    "TOMB": 18, "CARTER": 20, "WALL": 15, "EAST": 12, "NORTH": 12,
    "WEST": 12, "SOUTH": 12, "LAYER": 15, "UNDERGROUND": 20,
    "TREASURE": 20, "ANCIENT": 18, "TEMPLE": 18,
}

# ============================================================
# QUADGRAM SCORER
# ============================================================
print("Loading quadgram statistics...")
QUADGRAMS = {}
TOTAL_QUADGRAMS = 0

with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            TOTAL_QUADGRAMS += count

LOG_TOTAL = math.log10(TOTAL_QUADGRAMS)
FLOOR = math.log10(0.01 / TOTAL_QUADGRAMS)

# Pre-compute log probabilities
QUAD_LOG = {}
for gram, count in QUADGRAMS.items():
    QUAD_LOG[gram] = math.log10(count) - LOG_TOTAL

print(f"Loaded {len(QUADGRAMS)} quadgrams, total count={TOTAL_QUADGRAMS}")


def quadgram_score(text):
    """Score text using log10 quadgram probabilities."""
    score = 0.0
    text = text.upper()
    for i in range(len(text) - 3):
        gram = text[i:i+4]
        score += QUAD_LOG.get(gram, FLOOR)
    return score


def word_bonus(text):
    """Give bonus for finding known Kryptos-related words."""
    bonus = 0
    text_upper = text.upper()
    for word, value in BONUS_WORDS.items():
        if word in text_upper:
            bonus += value
    return bonus


def combined_score(text):
    """Quadgram score + word bonus."""
    return quadgram_score(text) + word_bonus(text)


# ============================================================
# VIGENERE FUNCTIONS (using KRYPTOS alphabet)
# ============================================================
def vig_decrypt_kryptos(ct, key):
    """Vigenere decrypt using KRYPTOS alphabet."""
    alpha = KRYPTOS_ALPHA
    alen = len(alpha)
    result = []
    ki = 0
    for c in ct:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci - kv) % alen])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def vig_encrypt_kryptos(pt, key):
    """Vigenere encrypt using KRYPTOS alphabet."""
    alpha = KRYPTOS_ALPHA
    alen = len(alpha)
    result = []
    ki = 0
    for c in pt:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci + kv) % alen])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def vig_decrypt_standard(ct, key):
    """Vigenere decrypt using standard alphabet."""
    alpha = STANDARD_ALPHA
    result = []
    ki = 0
    for c in ct:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci - kv) % 26])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def vig_encrypt_standard(pt, key):
    """Vigenere encrypt using standard alphabet."""
    alpha = STANDARD_ALPHA
    result = []
    ki = 0
    for c in pt:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci + kv) % 26])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


# ============================================================
# TRANSPOSITION FUNCTIONS
# ============================================================
def columnar_encrypt(plaintext, col_order):
    """Columnar transposition encryption.
    col_order = list of column indices in read-off order.
    E.g., [2,0,1] means: read column 2 first, then 0, then 1.
    """
    ncols = len(col_order)
    nrows = math.ceil(len(plaintext) / ncols)
    # Fill grid row by row
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(plaintext):
                row.append(plaintext[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)

    # Read columns in col_order
    result = []
    for c in col_order:
        for r in range(nrows):
            if grid[r][c]:
                result.append(grid[r][c])
    return ''.join(result)


def columnar_decrypt(ciphertext, col_order):
    """Columnar transposition decryption (reverse of encrypt).
    col_order = order columns were read off during encryption.
    """
    ncols = len(col_order)
    nrows = math.ceil(len(ciphertext) / ncols)
    total_cells = nrows * ncols
    short = total_cells - len(ciphertext)  # number of short columns (last row)

    # Determine length of each column
    col_lengths = []
    for c in col_order:
        # Columns with index >= ncols - short have one fewer row
        if c >= ncols - short and short > 0:
            col_lengths.append(nrows - 1)
        else:
            col_lengths.append(nrows)

    # Split ciphertext into columns
    cols_data = {}
    idx = 0
    for i, c in enumerate(col_order):
        length = col_lengths[i]
        cols_data[c] = ciphertext[idx:idx+length]
        idx += length

    # Read row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols_data.get(c, '')):
                result.append(cols_data[c][r])
    return ''.join(result)


def route_spiral_cw(text, nrows, ncols, start_corner=0):
    """Read text from grid in clockwise spiral from given corner.
    start_corner: 0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left
    Returns the text read in spiral order.
    """
    # Fill grid row by row
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('X')
        grid.append(row)

    # Read in spiral
    result = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1

    if start_corner == 0:  # top-left CW
        while top <= bottom and left <= right:
            for c in range(left, right + 1): result.append(grid[top][c])
            top += 1
            for r in range(top, bottom + 1): result.append(grid[r][right])
            right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1): result.append(grid[bottom][c])
                bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1): result.append(grid[r][left])
                left += 1
    elif start_corner == 1:  # top-right CW
        while top <= bottom and left <= right:
            for r in range(top, bottom + 1): result.append(grid[r][right])
            right -= 1
            if left <= right:
                for c in range(right, left - 1, -1): result.append(grid[bottom][c])
                bottom -= 1
            if top <= bottom:
                for r in range(bottom, top - 1, -1): result.append(grid[r][left])
                left += 1
            for c in range(left, right + 1): result.append(grid[top][c])
            top += 1
    elif start_corner == 2:  # bottom-right CW
        while top <= bottom and left <= right:
            for c in range(right, left - 1, -1): result.append(grid[bottom][c])
            bottom -= 1
            for r in range(bottom, top - 1, -1): result.append(grid[r][left])
            left += 1
            if top <= bottom:
                for c in range(left, right + 1): result.append(grid[top][c])
                top += 1
            if left <= right:
                for r in range(top, bottom + 1): result.append(grid[r][right])
                right -= 1
    elif start_corner == 3:  # bottom-left CW
        while top <= bottom and left <= right:
            for r in range(bottom, top - 1, -1): result.append(grid[r][left])
            left += 1
            for c in range(left, right + 1): result.append(grid[top][c])
            top += 1
            if left <= right:
                for r in range(top, bottom + 1): result.append(grid[r][right])
                right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1): result.append(grid[bottom][c])
                bottom -= 1

    return ''.join(result[:len(text)])


def route_zigzag(text, nrows, ncols):
    """Read text from grid in zigzag (boustrophedon) order."""
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)

    result = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                if grid[r][c]: result.append(grid[r][c])
        else:
            for c in range(ncols - 1, -1, -1):
                if grid[r][c]: result.append(grid[r][c])
    return ''.join(result)


def route_columns_down(text, nrows, ncols):
    """Read grid column by column, top to bottom."""
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)
    result = []
    for c in range(ncols):
        for r in range(nrows):
            if grid[r][c]: result.append(grid[r][c])
    return ''.join(result)


def route_columns_alternating(text, nrows, ncols):
    """Read columns alternating down/up."""
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)
    result = []
    for c in range(ncols):
        if c % 2 == 0:
            for r in range(nrows):
                if grid[r][c]: result.append(grid[r][c])
        else:
            for r in range(nrows - 1, -1, -1):
                if grid[r][c]: result.append(grid[r][c])
    return ''.join(result)


def route_diagonal(text, nrows, ncols):
    """Read grid diagonally (top-left to bottom-right diagonals)."""
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')
        grid.append(row)

    result = []
    # Diagonals starting from first row and first column
    for d in range(nrows + ncols - 1):
        if d < ncols:
            r, c = 0, d
        else:
            r, c = d - ncols + 1, ncols - 1
        while r < nrows and c >= 0:
            if grid[r][c]: result.append(grid[r][c])
            r += 1
            c -= 1
    return ''.join(result)


def inverse_route(text, route_func, nrows, ncols, **kwargs):
    """Inverse a route cipher: given ciphertext written in route order,
    read back row by row to get plaintext."""
    # Create position mapping: route reads positions in some order
    dummy = ''.join(chr(i) if i < 256 else '?' for i in range(nrows * ncols))
    # We need to figure out which position maps where
    # Place numbers 0..N-1 in the grid, apply route, see the order
    positions = list(range(nrows * ncols))
    pos_text = ''
    for p in positions:
        pos_text += chr(ord('A') + (p % 26))  # dummy

    # Actually, let's think about this differently:
    # route_func reads the grid in a certain order -> gives ciphertext
    # To invert: ciphertext characters go INTO the grid in route order,
    # then read row by row to get plaintext

    # Get the route order by tracking which positions are read
    n = nrows * ncols
    # Create a text where each char encodes its position
    marker = list(range(n))
    # Simulate the route to get read order
    # We'll use a trick: fill grid with index markers
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            row.append(idx)
            idx += 1
        grid.append(row)

    # Apply route function on a dummy text to get position order
    dummy_text = ''.join(chr(65 + (i % 26)) for i in range(min(len(text), n)))
    route_output = route_func(dummy_text, nrows, ncols, **kwargs) if kwargs else route_func(dummy_text, nrows, ncols)

    # The route function reads positions in order - we need to know that order
    # Fill grid with unique markers
    unique_text = ''.join(chr(i + 33) for i in range(min(n, 94)))  # limited
    # Better approach: use the grid indices directly

    # For inversion: text was written row by row, read in route order = ciphertext
    # So to decrypt: write ciphertext in route order, read row by row
    # Route order = the order positions appear when route reads the grid

    # Let's get route order by using position-encoded text
    if n > 256:
        return text  # too large

    # Create text where position i has a unique identifier
    pos_encoded = bytes(range(n)).decode('latin-1')
    routed = route_func(pos_encoded[:len(text)], nrows, ncols, **kwargs) if kwargs else route_func(pos_encoded[:len(text)], nrows, ncols)

    # route_order[i] = original position of i-th character in route output
    route_order = [ord(c) for c in routed]

    # To invert: place ciphertext chars back at their original positions
    result = [''] * len(text)
    for i, pos in enumerate(route_order):
        if i < len(text) and pos < len(text):
            result[pos] = text[i]

    return ''.join(result)


# ============================================================
# SIMULATED ANNEALING FOR COLUMNAR TRANSPOSITION
# ============================================================
def sa_columnar(text, ncols, score_func, iterations=30000, temp=1.0, cooling=0.9999):
    """Use simulated annealing to find best column permutation."""
    # Start with random permutation
    current_perm = list(range(ncols))
    random.shuffle(current_perm)

    current_pt = columnar_decrypt(text, current_perm)
    current_score = score_func(current_pt)

    best_perm = current_perm[:]
    best_score = current_score
    best_pt = current_pt

    for i in range(iterations):
        # Swap two random columns
        new_perm = current_perm[:]
        a, b = random.sample(range(ncols), 2)
        new_perm[a], new_perm[b] = new_perm[b], new_perm[a]

        new_pt = columnar_decrypt(text, new_perm)
        new_score = score_func(new_pt)

        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / temp):
            current_perm = new_perm
            current_score = new_score
            current_pt = new_pt

        if current_score > best_score:
            best_score = current_score
            best_perm = current_perm[:]
            best_pt = current_pt

        temp *= cooling

    return best_pt, best_score, best_perm


# ============================================================
# MAIN ATTACK
# ============================================================
def main():
    print("=" * 80)
    print("K4 DEEP TRANSPOSITION + VIGENERE ATTACK")
    print("=" * 80)
    print(f"K4 ciphertext ({LEN_K4} chars): {K4}")
    print(f"Best key guess: {BEST_KEY_GUESS}")
    print()

    # Global results tracker
    all_results = []  # (score, description, plaintext)

    # --------------------------------------------------------
    # PHASE 1: Generate candidate keys
    # --------------------------------------------------------
    print("=" * 60)
    print("PHASE 1: Generating candidate keys")
    print("=" * 60)

    # Primary key candidates
    candidate_keys = [
        BEST_KEY_GUESS,
        "OYNKYELYOIECBAQKBQTNNRDUMRIYW",
        "OYNKYELYOIECBAQKAQTNNRDUMRIYW",
        "OYNKYELYOIECBAQKKRYPTRDUMRIYW",
        "OYNKYELYOIECBAQKSANBNRDUMRIYW",
        "OYNKYELYOIECBAQKPALIMRDUMRIYW",  # PALIM(psest)
        "OYNKYELYOIECBAQKBERLIRDUMRIYW",  # BERLI(n)
        "OYNKYELYOIECBAQKCLOCKRDUMRIYW",  # CLOCK
    ]

    # Also try with standard alphabet
    key_alphabet_pairs = []
    for key in candidate_keys:
        key_alphabet_pairs.append((key, "KRYPTOS", vig_decrypt_kryptos))
        key_alphabet_pairs.append((key, "STANDARD", vig_decrypt_standard))

    # --------------------------------------------------------
    # PHASE 2: For each key, decrypt and try transpositions
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 2: Vigenere decrypt -> Un-transpose (Hypothesis A)")
    print("K4 = Vig(Trans(PT)) => Trans(PT) = Vig_dec(K4)")
    print("=" * 60)

    for key, alpha_name, decrypt_func in key_alphabet_pairs:
        vig_output = decrypt_func(K4, key)
        base_vig_score = quadgram_score(vig_output)

        desc_prefix = f"Key={key[:8]}..{key[-4:]}/{alpha_name}"
        print(f"\n--- {desc_prefix} ---")
        print(f"  Vig output: {vig_output[:40]}... (qscore={base_vig_score:.1f})")

        # 2a) Columnar transposition - exhaustive for small widths
        for width in range(5, 8):
            best_local_score = -999999
            best_local_pt = ""
            best_local_perm = None

            print(f"  Columnar width={width}: testing {math.factorial(width)} permutations...", end="", flush=True)

            for perm in permutations(range(width)):
                pt = columnar_decrypt(vig_output, list(perm))
                sc = combined_score(pt)
                if sc > best_local_score:
                    best_local_score = sc
                    best_local_pt = pt
                    best_local_perm = perm

            all_results.append((best_local_score,
                f"HypA: {desc_prefix}, ColTrans w={width}, perm={best_local_perm}",
                best_local_pt))
            print(f" best={best_local_score:.1f}")

        # 2a-2) Columnar with SA for larger widths
        for width in [8, 9, 10, 11, 12, 13, 14]:
            best_pt, best_sc, best_perm = sa_columnar(
                vig_output, width, combined_score, iterations=50000)
            all_results.append((best_sc,
                f"HypA: {desc_prefix}, ColTrans(SA) w={width}, perm={best_perm}",
                best_pt))
            if width in [8, 10, 13]:
                print(f"  Columnar(SA) width={width}: best={best_sc:.1f}")

        # 2b) Route ciphers
        grid_sizes = [(7, 14), (14, 7), (8, 13), (13, 8), (9, 11), (11, 9), (10, 10)]
        for nrows, ncols in grid_sizes:
            if nrows * ncols < len(vig_output):
                continue

            # Spiral from 4 corners
            for corner in range(4):
                try:
                    pt = inverse_route(vig_output, route_spiral_cw, nrows, ncols, start_corner=corner)
                    sc = combined_score(pt)
                    all_results.append((sc,
                        f"HypA: {desc_prefix}, Spiral({nrows}x{ncols}) corner={corner}",
                        pt))
                except:
                    pass

            # Zigzag
            try:
                pt = inverse_route(vig_output, route_zigzag, nrows, ncols)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypA: {desc_prefix}, Zigzag({nrows}x{ncols})",
                    pt))
            except:
                pass

            # Column-by-column
            try:
                pt = inverse_route(vig_output, route_columns_down, nrows, ncols)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypA: {desc_prefix}, ColDown({nrows}x{ncols})",
                    pt))
            except:
                pass

            # Alternating columns
            try:
                pt = inverse_route(vig_output, route_columns_alternating, nrows, ncols)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypA: {desc_prefix}, ColAlt({nrows}x{ncols})",
                    pt))
            except:
                pass

            # Diagonal
            try:
                pt = inverse_route(vig_output, route_diagonal, nrows, ncols)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypA: {desc_prefix}, Diagonal({nrows}x{ncols})",
                    pt))
            except:
                pass

        # 2c) Simple reversals and shifts
        for shift in range(1, LEN_K4):
            pt = vig_output[shift:] + vig_output[:shift]
            sc = combined_score(pt)
            if sc > base_vig_score + 5:
                all_results.append((sc,
                    f"HypA: {desc_prefix}, Shift={shift}",
                    pt))

        # Reverse
        pt = vig_output[::-1]
        sc = combined_score(pt)
        all_results.append((sc, f"HypA: {desc_prefix}, Reversed", pt))

        # Rail fence (common transposition)
        for rails in range(2, 8):
            pt = rail_fence_decrypt(vig_output, rails)
            sc = combined_score(pt)
            all_results.append((sc,
                f"HypA: {desc_prefix}, RailFence r={rails}",
                pt))

    # --------------------------------------------------------
    # PHASE 3: REVERSE HYPOTHESIS
    # K4 = Trans(Vig(PT)) => Vig(PT) = Un-trans(K4)
    # PT = Vig_dec(Un-trans(K4))
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 3: Un-transpose K4 FIRST, then Vigenere decrypt (Hypothesis B)")
    print("K4 = Trans(Vig(PT)) => Vig(PT) = Un-trans(K4)")
    print("=" * 60)

    for key, alpha_name, decrypt_func in key_alphabet_pairs:
        desc_prefix = f"Key={key[:8]}..{key[-4:]}/{alpha_name}"

        # 3a) Columnar un-transpose K4, then Vig decrypt
        for width in range(5, 8):
            best_local_score = -999999
            best_local_pt = ""
            best_local_perm = None

            print(f"  HypB {desc_prefix}, ColTrans w={width}...", end="", flush=True)

            for perm in permutations(range(width)):
                untransposed = columnar_decrypt(K4, list(perm))
                pt = decrypt_func(untransposed, key)
                sc = combined_score(pt)
                if sc > best_local_score:
                    best_local_score = sc
                    best_local_pt = pt
                    best_local_perm = perm

            all_results.append((best_local_score,
                f"HypB: {desc_prefix}, ColTrans w={width}, perm={best_local_perm}",
                best_local_pt))
            print(f" best={best_local_score:.1f}")

        # 3a-2) SA for larger widths
        for width in [8, 9, 10, 11, 12, 13, 14]:
            def score_hypb(untransposed):
                pt = decrypt_func(untransposed, key)
                return combined_score(pt)

            best_ut, best_sc, best_perm = sa_columnar(
                K4, width, score_hypb, iterations=50000)
            pt = decrypt_func(best_ut, key)
            all_results.append((best_sc,
                f"HypB: {desc_prefix}, ColTrans(SA) w={width}, perm={best_perm}",
                pt))
            if width in [8, 10, 13]:
                print(f"  HypB ColTrans(SA) w={width}: best={best_sc:.1f}")

        # 3b) Route cipher un-transpose K4, then Vig decrypt
        grid_sizes = [(7, 14), (14, 7), (8, 13), (13, 8), (9, 11), (11, 9), (10, 10)]
        for nrows, ncols in grid_sizes:
            if nrows * ncols < LEN_K4:
                continue

            for corner in range(4):
                try:
                    untransposed = inverse_route(K4, route_spiral_cw, nrows, ncols, start_corner=corner)
                    pt = decrypt_func(untransposed, key)
                    sc = combined_score(pt)
                    all_results.append((sc,
                        f"HypB: {desc_prefix}, Spiral({nrows}x{ncols}) corner={corner}",
                        pt))
                except:
                    pass

            try:
                untransposed = inverse_route(K4, route_zigzag, nrows, ncols)
                pt = decrypt_func(untransposed, key)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypB: {desc_prefix}, Zigzag({nrows}x{ncols})",
                    pt))
            except:
                pass

            try:
                untransposed = inverse_route(K4, route_columns_down, nrows, ncols)
                pt = decrypt_func(untransposed, key)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypB: {desc_prefix}, ColDown({nrows}x{ncols})",
                    pt))
            except:
                pass

            try:
                untransposed = inverse_route(K4, route_columns_alternating, nrows, ncols)
                pt = decrypt_func(untransposed, key)
                sc = combined_score(pt)
                all_results.append((sc,
                    f"HypB: {desc_prefix}, ColAlt({nrows}x{ncols})",
                    pt))
            except:
                pass

        # 3c) Rail fence on K4 first
        for rails in range(2, 8):
            untransposed = rail_fence_decrypt(K4, rails)
            pt = decrypt_func(untransposed, key)
            sc = combined_score(pt)
            all_results.append((sc,
                f"HypB: {desc_prefix}, RailFence r={rails}",
                pt))

        # 3d) Simple reverse of K4, then decrypt
        untransposed = K4[::-1]
        pt = decrypt_func(untransposed, key)
        sc = combined_score(pt)
        all_results.append((sc,
            f"HypB: {desc_prefix}, Reversed K4",
            pt))

    # --------------------------------------------------------
    # PHASE 4: Key position 16-20 brute force with best transpositions
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 4: Brute-force key positions 16-20")
    print("Testing top transposition methods with varied keys")
    print("=" * 60)

    # Find the best transposition methods so far
    all_results.sort(key=lambda x: -x[0])

    # Extract unique transposition methods from top results
    top_methods = []
    seen_methods = set()
    for sc, desc, pt in all_results[:50]:
        # Extract method signature
        parts = desc.split(", ", 1)
        if len(parts) > 1:
            method = parts[1]
            if method not in seen_methods:
                seen_methods.add(method)
                top_methods.append(desc)

    # Try brute forcing the 5 unknown key positions with promising methods
    # 26^5 = 11,881,376 is too many for full search, so we'll sample intelligently

    # Start with common English letters at positions 16-20
    common_letters = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

    prefix = "OYNKYELYOIECBAQK"
    suffix = "RDUMRIYW"

    # Strategy: try most common letter combinations (top 15 letters, ~759375 combos)
    # But that's still a lot. Let's do top 10 = 100000 combos
    top_n = 10
    test_letters = common_letters[:top_n]
    total_combos = top_n ** 5
    print(f"Testing {total_combos} key combinations with top {top_n} letters: {test_letters}")

    best_brute_score = -999999
    best_brute_results = []

    count = 0
    start_time = time.time()

    # Test both hypotheses with the best simple transpositions
    # Focus on the most promising: columnar width 7 (which we can do exhaustively per key)
    # and rail fence (fast)

    for c1 in test_letters:
        for c2 in test_letters:
            for c3 in test_letters:
                for c4 in test_letters:
                    for c5 in test_letters:
                        key = prefix + c1 + c2 + c3 + c4 + c5 + suffix
                        count += 1

                        if count % 20000 == 0:
                            elapsed = time.time() - start_time
                            rate = count / elapsed if elapsed > 0 else 0
                            print(f"  {count}/{total_combos} ({100*count/total_combos:.1f}%) "
                                  f"rate={rate:.0f}/s best={best_brute_score:.1f}")

                        # HypA: Vig decrypt, then score directly and with simple transpositions
                        for decrypt_func, aname in [(vig_decrypt_kryptos, "K"), (vig_decrypt_standard, "S")]:
                            vig_out = decrypt_func(K4, key)

                            # Raw vig output score
                            sc = combined_score(vig_out)
                            if sc > best_brute_score - 20:
                                best_brute_results.append((sc,
                                    f"BruteA: key={key}/{aname}, raw", vig_out))
                                if sc > best_brute_score:
                                    best_brute_score = sc

                            # Rail fence
                            for rails in [2, 3, 4, 5]:
                                pt = rail_fence_decrypt(vig_out, rails)
                                sc = combined_score(pt)
                                if sc > best_brute_score - 15:
                                    best_brute_results.append((sc,
                                        f"BruteA: key={key}/{aname}, RF r={rails}", pt))
                                    if sc > best_brute_score:
                                        best_brute_score = sc

                            # Reverse
                            pt = vig_out[::-1]
                            sc = combined_score(pt)
                            if sc > best_brute_score - 15:
                                best_brute_results.append((sc,
                                    f"BruteA: key={key}/{aname}, rev", pt))
                                if sc > best_brute_score:
                                    best_brute_score = sc

                        # HypB: Simple transpositions on K4, then decrypt
                        for decrypt_func, aname in [(vig_decrypt_kryptos, "K"), (vig_decrypt_standard, "S")]:
                            # Rail fence on K4
                            for rails in [2, 3, 4, 5]:
                                untransposed = rail_fence_decrypt(K4, rails)
                                pt = decrypt_func(untransposed, key)
                                sc = combined_score(pt)
                                if sc > best_brute_score - 15:
                                    best_brute_results.append((sc,
                                        f"BruteB: key={key}/{aname}, RF K4 r={rails}", pt))
                                    if sc > best_brute_score:
                                        best_brute_score = sc

                            # Reverse K4
                            pt = decrypt_func(K4[::-1], key)
                            sc = combined_score(pt)
                            if sc > best_brute_score - 15:
                                best_brute_results.append((sc,
                                    f"BruteB: key={key}/{aname}, rev K4", pt))
                                if sc > best_brute_score:
                                    best_brute_score = sc

    elapsed = time.time() - start_time
    print(f"Phase 4 complete: {count} keys tested in {elapsed:.1f}s")

    # Add brute force results to main list
    best_brute_results.sort(key=lambda x: -x[0])
    all_results.extend(best_brute_results[:200])  # Keep top 200

    # --------------------------------------------------------
    # PHASE 5: Compass Rose / Direction-based transposition
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 5: Compass Rose / Direction-based transpositions")
    print("=" * 60)

    key = BEST_KEY_GUESS
    for decrypt_func, aname in [(vig_decrypt_kryptos, "KRYPTOS"), (vig_decrypt_standard, "STANDARD")]:
        vig_out = decrypt_func(K4, key)

        # Try reading grid in compass directions
        for nrows, ncols in [(7, 14), (14, 7), (8, 13), (13, 8), (9, 11), (11, 9), (10, 10)]:
            if nrows * ncols < LEN_K4:
                continue

            # Fill grid
            grid = []
            idx = 0
            for r in range(nrows):
                row = []
                for c in range(ncols):
                    if idx < len(vig_out):
                        row.append(vig_out[idx])
                    else:
                        row.append('X')
                    idx += 1
                grid.append(row)

            # N: top to bottom, column by column
            pt = route_columns_down(vig_out, nrows, ncols)
            sc = combined_score(pt)
            all_results.append((sc, f"Compass N: {aname}, {nrows}x{ncols}", pt))

            # S: bottom to top, column by column
            result = []
            for c in range(ncols):
                for r in range(nrows - 1, -1, -1):
                    if r < nrows and c < ncols and grid[r][c] != 'X':
                        result.append(grid[r][c])
            pt = ''.join(result)[:LEN_K4]
            sc = combined_score(pt)
            all_results.append((sc, f"Compass S: {aname}, {nrows}x{ncols}", pt))

            # E: left to right, row by row (normal reading)
            pt = vig_out  # same as normal

            # W: right to left, row by row
            result = []
            for r in range(nrows):
                for c in range(ncols - 1, -1, -1):
                    if r < nrows and c < ncols and grid[r][c] != 'X':
                        result.append(grid[r][c])
            pt = ''.join(result)[:LEN_K4]
            sc = combined_score(pt)
            all_results.append((sc, f"Compass W: {aname}, {nrows}x{ncols}", pt))

            # NE diagonal
            pt = route_diagonal(vig_out, nrows, ncols)
            sc = combined_score(pt)
            all_results.append((sc, f"Compass NE: {aname}, {nrows}x{ncols}", pt))

        # Also try compass directions on K4 BEFORE decryption (HypB)
        for nrows, ncols in [(7, 14), (14, 7), (10, 10)]:
            if nrows * ncols < LEN_K4:
                continue

            # Read K4 column-by-column (un-transpose), then decrypt
            untransposed = route_columns_down(K4, nrows, ncols)
            pt = decrypt_func(untransposed, key)
            sc = combined_score(pt)
            all_results.append((sc, f"Compass-B N: {aname}, {nrows}x{ncols}", pt))

            # Zigzag K4, then decrypt
            untransposed = route_zigzag(K4, nrows, ncols)
            pt = decrypt_func(untransposed, key)
            sc = combined_score(pt)
            all_results.append((sc, f"Compass-B Zigzag: {aname}, {nrows}x{ncols}", pt))

    # --------------------------------------------------------
    # FINAL RESULTS
    # --------------------------------------------------------
    print("\n" + "=" * 80)
    print("TOP 20 RESULTS")
    print("=" * 80)

    all_results.sort(key=lambda x: -x[0])

    # Deduplicate
    seen_texts = set()
    unique_results = []
    for sc, desc, pt in all_results:
        if pt not in seen_texts:
            seen_texts.add(pt)
            unique_results.append((sc, desc, pt))

    for rank, (sc, desc, pt) in enumerate(unique_results[:20], 1):
        wb = word_bonus(pt)
        qs = quadgram_score(pt)
        print(f"\n#{rank} Score={sc:.2f} (quad={qs:.2f}, words={wb})")
        print(f"  Method: {desc}")
        print(f"  Text: {pt}")

        # Check for any words
        found_words = []
        for word in BONUS_WORDS:
            if word in pt:
                found_words.append(word)
        if found_words:
            print(f"  ** WORDS FOUND: {', '.join(found_words)} **")

    # Also show baseline
    print("\n" + "=" * 60)
    print("BASELINE COMPARISONS")
    print("=" * 60)

    for key in [BEST_KEY_GUESS]:
        for decrypt_func, aname in [(vig_decrypt_kryptos, "KRYPTOS"), (vig_decrypt_standard, "STANDARD")]:
            vig_out = decrypt_func(K4, key)
            sc = combined_score(vig_out)
            print(f"Raw Vig decrypt ({aname}): score={sc:.2f}")
            print(f"  {vig_out}")

    print(f"\nRaw K4: score={combined_score(K4):.2f}")

    # Example known English for reference
    ref = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHETHENUCLEUSOFTHESCIENTIFICINTELLIGENCEAGENCYTHERE"
    print(f"Reference English (97 chars): score={combined_score(ref):.2f}")


def rail_fence_encrypt(text, rails):
    """Rail fence cipher encryption."""
    if rails <= 1:
        return text
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for char in text:
        fence[rail].append(char)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return ''.join(''.join(row) for row in fence)


def rail_fence_decrypt(text, rails):
    """Rail fence cipher decryption."""
    if rails <= 1:
        return text
    n = len(text)
    # Calculate the length of each rail
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    cycle = len(pattern)

    rail_lengths = [0] * rails
    for i in range(n):
        rail_lengths[pattern[i % cycle]] += 1

    # Split text into rails
    rail_texts = []
    idx = 0
    for length in rail_lengths:
        rail_texts.append(text[idx:idx+length])
        idx += length

    # Read back in zigzag order
    rail_indices = [0] * rails
    result = []
    for i in range(n):
        rail = pattern[i % cycle]
        result.append(rail_texts[rail][rail_indices[rail]])
        rail_indices[rail] += 1

    return ''.join(result)


if __name__ == "__main__":
    main()
