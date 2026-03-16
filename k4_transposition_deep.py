#!/usr/bin/env python3
"""
K4 Deep Transposition + Vigenere Attack - v2

HYPOTHESIS: K4 = Vigenere(Transposition(plaintext)) or K4 = Transposition(Vigenere(plaintext))

The Vigenere output with best key OYNKYELYOIECBAQKBQTNNRDUMRIYW (KRYPTOS alphabet) is:
  KSARNQAPBZDBKZELAMTITEASTNORTHEASTQGUZOUAFZFEMOUTHPSOZQUGDMGKFSBERLINCLOCKINSASWQULCKEPJFYANKCAYF

This contains EASTNORTHEAST at pos 21-33 and BERLINCLOCK at pos 62-72 but the rest is gibberish.
If the plaintext was transposed BEFORE Vigenere encryption, then this output IS the transposed
plaintext - and we need to find the un-transposition that produces coherent English.

Key insight: The WORDS EASTNORTHEAST and BERLINCLOCK in the Vigenere output constrain the
transposition - they must map FROM contiguous positions in the original plaintext TO their
current positions. This is a major constraint we can exploit.

Approach:
1. Focus on un-transposing the Vigenere output
2. For columnar transposition, use SA with MUCH higher iterations
3. Try all route ciphers thoroughly
4. Try Hypothesis B (transpose K4 first, then Vig decrypt) with SA
5. Brute-force key positions 16-20 with fast methods
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

BEST_KEY = "OYNKYELYOIECBAQKBQTNNRDUMRIYW"

# The Vigenere decryption result we'll be trying to un-transpose
VIG_OUTPUT = None  # computed below

# Words to look for in the un-transposed plaintext
BONUS_WORDS = [
    "EASTNORTHEAST", "BERLINCLOCK", "NORTHEAST", "BERLIN", "CLOCK",
    "EGYPT", "CAIRO", "PYRAMID", "PHARAOH", "TUTANKHAMUN",
    "WONDERFUL", "THINGS", "COMPASS", "WORLD", "TIME",
    "ALEXANDERPLATZ", "ALEXANDRIA", "SLOWLY", "DESPERATELY",
    "SHADOW", "BETWEEN", "HIDDEN", "BURIED", "SECRET",
    "TOMB", "CARTER", "WALL", "EAST", "NORTH", "WEST", "SOUTH",
    "LAYER", "UNDERGROUND", "TREASURE", "ANCIENT", "TEMPLE",
    "LANGLEY", "PALIMPSEST", "ABSCISSA", "IQLUSION",
    "SOUTHEAST", "NORTHWEST", "SOUTHWEST",
]

BONUS_VALUES = {}
for w in BONUS_WORDS:
    BONUS_VALUES[w] = max(10, len(w) * 3)
BONUS_VALUES["EASTNORTHEAST"] = 60
BONUS_VALUES["BERLINCLOCK"] = 60
BONUS_VALUES["NORTHEAST"] = 45
BONUS_VALUES["BERLIN"] = 40
BONUS_VALUES["CLOCK"] = 35

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

QUAD_LOG = {}
for gram, count in QUADGRAMS.items():
    QUAD_LOG[gram] = math.log10(count) - LOG_TOTAL

print(f"Loaded {len(QUADGRAMS)} quadgrams")


def qscore(text):
    """Quadgram log-probability score."""
    s = 0.0
    t = text.upper()
    for i in range(len(t) - 3):
        s += QUAD_LOG.get(t[i:i+4], FLOOR)
    return s


def word_bonus(text):
    """Bonus for finding Kryptos-related words."""
    b = 0
    t = text.upper()
    for w, v in BONUS_VALUES.items():
        if w in t:
            b += v
    return b


def score(text):
    return qscore(text) + word_bonus(text)


# ============================================================
# VIGENERE
# ============================================================
def vig_dec(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    ki = 0
    alen = len(alpha)
    for c in ct:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci - kv) % alen])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def vig_enc(pt, key, alpha=KRYPTOS_ALPHA):
    result = []
    ki = 0
    alen = len(alpha)
    for c in pt:
        ci = alpha.find(c)
        kv = alpha.find(key[ki % len(key)])
        if ci >= 0 and kv >= 0:
            result.append(alpha[(ci + kv) % alen])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


# ============================================================
# TRANSPOSITION PRIMITIVES
# ============================================================
def columnar_decrypt(ciphertext, col_order):
    """Undo columnar transposition.
    col_order: the order in which columns were read off during encryption.
    """
    ncols = len(col_order)
    nrows = math.ceil(len(ciphertext) / ncols)
    total = nrows * ncols
    short = total - len(ciphertext)

    col_lengths = []
    for c in col_order:
        if c >= ncols - short and short > 0:
            col_lengths.append(nrows - 1)
        else:
            col_lengths.append(nrows)

    cols_data = {}
    idx = 0
    for i, c in enumerate(col_order):
        length = col_lengths[i]
        cols_data[c] = list(ciphertext[idx:idx+length])
        idx += length

    result = []
    for r in range(nrows):
        for c in range(ncols):
            data = cols_data.get(c, [])
            if r < len(data):
                result.append(data[r])
    return ''.join(result)


def columnar_encrypt(plaintext, col_order):
    """Columnar transposition encryption."""
    ncols = len(col_order)
    nrows = math.ceil(len(plaintext) / ncols)
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(plaintext):
                row.append(plaintext[idx])
                idx += 1
            else:
                row.append(None)
        grid.append(row)

    result = []
    for c in col_order:
        for r in range(nrows):
            if grid[r][c] is not None:
                result.append(grid[r][c])
    return ''.join(result)


def rail_fence_decrypt(text, rails):
    if rails <= 1 or rails >= len(text):
        return text
    n = len(text)
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    cycle = len(pattern)
    rail_lens = [0] * rails
    for i in range(n):
        rail_lens[pattern[i % cycle]] += 1
    rail_texts = []
    idx = 0
    for length in rail_lens:
        rail_texts.append(list(text[idx:idx+length]))
        idx += length
    rail_idx = [0] * rails
    result = []
    for i in range(n):
        rail = pattern[i % cycle]
        result.append(rail_texts[rail][rail_idx[rail]])
        rail_idx[rail] += 1
    return ''.join(result)


def rail_fence_encrypt(text, rails):
    if rails <= 1 or rails >= len(text):
        return text
    fence = [[] for _ in range(rails)]
    rail, direction = 0, 1
    for char in text:
        fence[rail].append(char)
        if rail == 0: direction = 1
        elif rail == rails - 1: direction = -1
        rail += direction
    return ''.join(''.join(r) for r in fence)


def make_grid(text, nrows, ncols):
    """Fill text into grid row by row."""
    grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < len(text):
                row.append(text[idx])
            else:
                row.append(None)
            idx += 1
        grid.append(row)
    return grid


def read_grid_columns(grid, nrows, ncols):
    """Read grid column by column, top to bottom."""
    result = []
    for c in range(ncols):
        for r in range(nrows):
            if grid[r][c] is not None:
                result.append(grid[r][c])
    return ''.join(result)


def read_grid_spiral_cw(grid, nrows, ncols):
    """Read grid in clockwise spiral from top-left."""
    result = []
    top, bot, left, right = 0, nrows-1, 0, ncols-1
    while top <= bot and left <= right:
        for c in range(left, right+1):
            if grid[top][c] is not None: result.append(grid[top][c])
        top += 1
        for r in range(top, bot+1):
            if grid[r][right] is not None: result.append(grid[r][right])
        right -= 1
        if top <= bot:
            for c in range(right, left-1, -1):
                if grid[bot][c] is not None: result.append(grid[bot][c])
            bot -= 1
        if left <= right:
            for r in range(bot, top-1, -1):
                if grid[r][left] is not None: result.append(grid[r][left])
            left += 1
    return ''.join(result)


def read_grid_zigzag(grid, nrows, ncols):
    """Boustrophedon: alternating L-R and R-L rows."""
    result = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                if grid[r][c] is not None: result.append(grid[r][c])
        else:
            for c in range(ncols-1, -1, -1):
                if grid[r][c] is not None: result.append(grid[r][c])
    return ''.join(result)


def read_grid_diag_tl(grid, nrows, ncols):
    """Read diagonals from top-left corner."""
    result = []
    for d in range(nrows + ncols - 1):
        r0 = max(0, d - ncols + 1)
        c0 = min(d, ncols - 1)
        r, c = r0, c0
        while r < nrows and c >= 0:
            if grid[r][c] is not None: result.append(grid[r][c])
            r += 1; c -= 1
    return ''.join(result)


def invert_permutation(text, perm_func, *args):
    """Given that ciphertext = read(fill_grid(plaintext)), find plaintext.
    perm_func(grid, nrows, ncols) reads the grid in a certain order.
    To invert: fill ciphertext INTO grid in that read order, then read row by row.
    """
    n = len(text)
    nrows, ncols = args[0], args[1]
    total = nrows * ncols

    # Get the read order: which position (r*ncols+c) is read at each step
    dummy_grid = []
    idx = 0
    for r in range(nrows):
        row = []
        for c in range(ncols):
            if idx < n:
                row.append(idx)
            else:
                row.append(None)
            idx += 1
        grid_row = row
        dummy_grid.append(grid_row)

    # We need the actual position indices in read order
    # Instead, use the char-based approach
    # Fill with unique chars
    marker = ''.join(chr(i) for i in range(n)) if n < 65536 else None
    if marker is None:
        return text

    marker_grid = make_grid(marker, nrows, ncols)
    read_order = perm_func(marker_grid, nrows, ncols)
    # read_order[i] = the character at position i in the read sequence
    # = chr(original_position)

    # To invert: text[i] should go to position ord(read_order[i])
    result = [' '] * n
    for i in range(min(len(text), len(read_order))):
        pos = ord(read_order[i])
        if pos < n:
            result[pos] = text[i]
    return ''.join(result)


# ============================================================
# SIMULATED ANNEALING FOR COLUMNAR TRANSPOSITION
# ============================================================
def sa_columnar(text, ncols, score_func, iterations=80000, restarts=3):
    """SA with multiple restarts to find best column permutation."""
    best_overall_score = -1e18
    best_overall_perm = None
    best_overall_pt = None

    for restart in range(restarts):
        perm = list(range(ncols))
        random.shuffle(perm)
        pt = columnar_decrypt(text, perm)
        cur_score = score_func(pt)
        best_score = cur_score
        best_perm = perm[:]
        best_pt = pt
        temp = 2.0

        for i in range(iterations):
            new_perm = perm[:]
            a, b = random.sample(range(ncols), 2)
            new_perm[a], new_perm[b] = new_perm[b], new_perm[a]
            new_pt = columnar_decrypt(text, new_perm)
            new_score = score_func(new_pt)
            delta = new_score - cur_score
            if delta > 0 or random.random() < math.exp(delta / max(temp, 0.001)):
                perm = new_perm
                cur_score = new_score
                pt = new_pt
            if cur_score > best_score:
                best_score = cur_score
                best_perm = perm[:]
                best_pt = pt
            temp *= 0.99995

        if best_score > best_overall_score:
            best_overall_score = best_score
            best_overall_perm = best_perm
            best_overall_pt = best_pt

    return best_overall_pt, best_overall_score, best_overall_perm


# SA for general position permutation (any-to-any mapping)
def sa_general_perm(text, score_func, iterations=200000):
    """SA over arbitrary position permutations of text."""
    n = len(text)
    perm = list(range(n))
    random.shuffle(perm)
    cur_text = ''.join(text[perm[i]] for i in range(n))
    cur_score = score_func(cur_text)
    best_score = cur_score
    best_perm = perm[:]
    best_text = cur_text
    temp = 2.0

    for i in range(iterations):
        a, b = random.sample(range(n), 2)
        # Swap positions a and b in the permutation
        new_perm = perm[:]
        new_perm[a], new_perm[b] = new_perm[b], new_perm[a]
        new_text = ''.join(text[new_perm[j]] for j in range(n))
        new_score = score_func(new_text)
        delta = new_score - cur_score
        if delta > 0 or random.random() < math.exp(delta / max(temp, 0.001)):
            perm = new_perm
            cur_score = new_score
            cur_text = new_text
        if cur_score > best_score:
            best_score = cur_score
            best_perm = perm[:]
            best_text = cur_text
        temp *= 0.99998

    return best_text, best_score, best_perm


# ============================================================
# MAIN
# ============================================================
def main():
    random.seed(42)

    print("=" * 80)
    print("K4 DEEP TRANSPOSITION + VIGENERE ATTACK v2")
    print("=" * 80)
    print(f"K4 ({LEN_K4} chars): {K4}")
    print(f"Key: {BEST_KEY} (len={len(BEST_KEY)})")

    # Compute Vigenere output
    vig_out = vig_dec(K4, BEST_KEY, KRYPTOS_ALPHA)
    print(f"\nVig output (KRYPTOS alpha): {vig_out}")
    print(f"  Quadgram score: {qscore(vig_out):.2f}")
    print(f"  Word bonus: {word_bonus(vig_out)}")

    vig_out_std = vig_dec(K4, BEST_KEY, STANDARD_ALPHA)
    print(f"\nVig output (Standard alpha): {vig_out_std}")
    print(f"  Quadgram score: {qscore(vig_out_std):.2f}")

    # Reference score
    ref = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHETHENUCLEUSOFTHESCIENTIFICINTELLIGENCEAGENCYTHERE"
    print(f"\nReference English score: {qscore(ref):.2f}")

    all_results = []

    # ====================================================================
    # HYPOTHESIS A: K4 = Vig(Trans(PT))
    # vig_out = Trans(PT), need to find un-transposition
    # ====================================================================
    print("\n" + "=" * 80)
    print("HYPOTHESIS A: K4 = Vig(Trans(PT))")
    print("Vigenere output is the TRANSPOSED plaintext. Un-transposing it should give English.")
    print("=" * 80)

    for label, text in [("KRYPTOS", vig_out), ("STANDARD", vig_out_std)]:
        print(f"\n--- Working with {label} alphabet Vig output ---")
        base = qscore(text)
        print(f"  Baseline quadgram score: {base:.2f}")

        # A1: Columnar transposition - exhaustive for widths 2-7
        print("\n  [A1] Columnar transposition (exhaustive, widths 2-7)")
        for w in range(2, 8):
            best_sc = -1e18
            best_pt = ""
            best_p = None
            for p in permutations(range(w)):
                pt = columnar_decrypt(text, list(p))
                s = score(pt)
                if s > best_sc:
                    best_sc = s
                    best_pt = pt
                    best_p = p
            all_results.append((best_sc, f"A/{label}/Col w={w} p={best_p}", best_pt))
            if best_sc > base + 5:
                print(f"    w={w}: score={best_sc:.1f} perm={best_p}")
                print(f"      {best_pt[:80]}...")
            elif w in [5, 7]:
                print(f"    w={w}: best={best_sc:.1f}")

        # A2: Columnar SA for widths 8-15
        print("\n  [A2] Columnar transposition (SA, widths 8-15)")
        for w in range(8, 16):
            pt, sc, perm = sa_columnar(text, w, score, iterations=80000, restarts=5)
            all_results.append((sc, f"A/{label}/Col-SA w={w} p={perm}", pt))
            print(f"    w={w}: score={sc:.1f}")
            if sc > base + 10:
                print(f"      perm={perm}")
                print(f"      {pt[:80]}...")

        # A3: Rail fence
        print("\n  [A3] Rail fence (2-15 rails)")
        for rails in range(2, 16):
            pt = rail_fence_decrypt(text, rails)
            sc = score(pt)
            all_results.append((sc, f"A/{label}/Rail r={rails}", pt))
            if sc > base + 5:
                print(f"    rails={rails}: score={sc:.1f}")
                print(f"      {pt[:80]}...")

        # A4: Route ciphers on various grids
        print("\n  [A4] Route ciphers")
        grid_dims = []
        for w in range(2, 50):
            h = math.ceil(LEN_K4 / w)
            if (w, h) not in grid_dims and h >= 2:
                grid_dims.append((h, w))  # nrows x ncols

        route_funcs = [
            ("spiral_cw", read_grid_spiral_cw),
            ("zigzag", read_grid_zigzag),
            ("columns", read_grid_columns),
            ("diag_tl", read_grid_diag_tl),
        ]

        for nrows, ncols in grid_dims:
            if nrows * ncols > LEN_K4 + ncols:  # don't allow too much padding
                continue
            for rname, rfunc in route_funcs:
                # Forward: read text as if it were in this route order
                pt = invert_permutation(text, rfunc, nrows, ncols)
                sc = score(pt)
                all_results.append((sc, f"A/{label}/Route-inv {rname} {nrows}x{ncols}", pt))
                if sc > base + 10:
                    print(f"    {rname} inv {nrows}x{ncols}: score={sc:.1f}")
                    print(f"      {pt[:80]}...")

                # Also try direct read (text was written in route order, read row by row)
                grid = make_grid(text, nrows, ncols)
                ct = rfunc(grid, nrows, ncols)
                sc2 = score(ct)
                all_results.append((sc2, f"A/{label}/Route-dir {rname} {nrows}x{ncols}", ct))
                if sc2 > base + 10:
                    print(f"    {rname} dir {nrows}x{ncols}: score={sc2:.1f}")
                    print(f"      {ct[:80]}...")

        # A5: Reverse
        pt = text[::-1]
        sc = score(pt)
        all_results.append((sc, f"A/{label}/Reverse", pt))
        print(f"\n  [A5] Reverse: score={sc:.1f}")

        # A6: General position SA (unrestricted anagram-like)
        print("\n  [A6] General permutation SA (3 runs)")
        for run in range(3):
            random.seed(42 + run * 17)
            pt, sc, perm = sa_general_perm(text, qscore, iterations=300000)
            wb = word_bonus(pt)
            total = sc + wb
            all_results.append((total, f"A/{label}/GenPerm run={run}", pt))
            print(f"    Run {run}: qscore={sc:.1f}, words={wb}, total={total:.1f}")
            print(f"      {pt[:80]}...")

    # ====================================================================
    # HYPOTHESIS B: K4 = Trans(Vig(PT))
    # Un-transpose K4 first, then Vig decrypt
    # ====================================================================
    print("\n" + "=" * 80)
    print("HYPOTHESIS B: K4 = Trans(Vig(PT))")
    print("K4 itself is transposed Vig ciphertext. Un-transpose K4, then decrypt.")
    print("=" * 80)

    for alpha_label, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
        print(f"\n--- {alpha_label} alphabet ---")

        def score_hypb(untransposed_k4):
            pt = vig_dec(untransposed_k4, BEST_KEY, alpha)
            return score(pt)

        base_score = score_hypb(K4)
        print(f"  Baseline (no transposition): {base_score:.2f}")

        # B1: Columnar exhaustive for widths 2-7
        print("\n  [B1] Columnar on K4 (exhaustive, widths 2-7)")
        for w in range(2, 8):
            best_sc = -1e18
            best_pt = ""
            best_p = None
            for p in permutations(range(w)):
                ut = columnar_decrypt(K4, list(p))
                pt = vig_dec(ut, BEST_KEY, alpha)
                s = score(pt)
                if s > best_sc:
                    best_sc = s
                    best_pt = pt
                    best_p = p
            all_results.append((best_sc, f"B/{alpha_label}/Col w={w} p={best_p}", best_pt))
            if w in [5, 7] or best_sc > base_score + 10:
                print(f"    w={w}: best={best_sc:.1f}")
                if best_sc > base_score + 10:
                    print(f"      {best_pt[:80]}...")

        # B2: Columnar SA for widths 8-15
        print("\n  [B2] Columnar SA on K4 (widths 8-15)")
        for w in range(8, 16):
            pt, sc, perm = sa_columnar(K4, w, score_hypb, iterations=80000, restarts=5)
            final_pt = vig_dec(pt, BEST_KEY, alpha)  # pt is untransposed K4
            # Wait - sa_columnar returns the decrypted text, not the plaintext
            # Let me fix: sa_columnar decrypts the columnar, we need to vig_dec that
            ut = columnar_decrypt(K4, perm)
            final_pt = vig_dec(ut, BEST_KEY, alpha)
            sc = score(final_pt)
            all_results.append((sc, f"B/{alpha_label}/Col-SA w={w} p={perm}", final_pt))
            print(f"    w={w}: score={sc:.1f}")
            if sc > base_score + 10:
                print(f"      {final_pt[:80]}...")

        # B3: Rail fence on K4
        print("\n  [B3] Rail fence on K4")
        for rails in range(2, 16):
            ut = rail_fence_decrypt(K4, rails)
            pt = vig_dec(ut, BEST_KEY, alpha)
            sc = score(pt)
            all_results.append((sc, f"B/{alpha_label}/Rail r={rails}", pt))
            if sc > base_score + 5:
                print(f"    rails={rails}: score={sc:.1f}")
                print(f"      {pt[:80]}...")

        # B4: Route ciphers on K4
        print("\n  [B4] Route ciphers on K4")
        for nrows, ncols in grid_dims:
            if nrows * ncols > LEN_K4 + ncols:
                continue
            for rname, rfunc in route_funcs:
                ut = invert_permutation(K4, rfunc, nrows, ncols)
                pt = vig_dec(ut, BEST_KEY, alpha)
                sc = score(pt)
                all_results.append((sc, f"B/{alpha_label}/Route-inv {rname} {nrows}x{ncols}", pt))
                if sc > base_score + 10:
                    print(f"    {rname} inv {nrows}x{ncols}: score={sc:.1f}")
                    print(f"      {pt[:80]}...")

        # B5: Reverse K4
        ut = K4[::-1]
        pt = vig_dec(ut, BEST_KEY, alpha)
        sc = score(pt)
        all_results.append((sc, f"B/{alpha_label}/Reverse K4", pt))
        print(f"\n  [B5] Reverse K4: score={sc:.1f}")

    # ====================================================================
    # PHASE 3: KEY BRUTE FORCE with fast transpositions
    # ====================================================================
    print("\n" + "=" * 80)
    print("PHASE 3: Key positions 16-20 brute force")
    print("Testing 26^3 x best_2_fixed combos with rail fence + reverse")
    print("=" * 80)

    prefix = "OYNKYELYOIECBAQK"
    suffix = "RDUMRIYW"

    # Since 26^5 is too many, let's do 26^3 with the two best-fixed positions
    # from our main key (B=1, Q=16, T=19, N=13, N=13)
    # Try fixing different pairs and varying the other 3

    best_brute = []
    count = 0
    t0 = time.time()

    # Strategy: fix 2 of 5 positions from the best key, brute force the other 3
    # Best key positions 16-20: B Q T N N
    fixed_pairs = [
        (0, 1),  # fix pos 0,1 = B,Q; vary 2,3,4
        (0, 4),  # fix B,N
        (3, 4),  # fix N,N
        (1, 2),  # fix Q,T
    ]

    best_key_mid = "BQTNN"

    for fi, fj in fixed_pairs:
        for c1 in STANDARD_ALPHA:
            for c2 in STANDARD_ALPHA:
                for c3 in STANDARD_ALPHA:
                    mid = list("_____")
                    mid[fi] = best_key_mid[fi]
                    mid[fj] = best_key_mid[fj]
                    free = [k for k in range(5) if k != fi and k != fj]
                    mid[free[0]] = c1
                    mid[free[1]] = c2
                    mid[free[2]] = c3
                    key = prefix + ''.join(mid) + suffix

                    for alpha_label, alpha in [("K", KRYPTOS_ALPHA)]:
                        vig_out_test = vig_dec(K4, key, alpha)
                        sc = qscore(vig_out_test)
                        wb = word_bonus(vig_out_test)
                        total = sc + wb

                        if total > -500:
                            best_brute.append((total, f"Brute/{alpha_label} key={key}", vig_out_test))

                        # Rail fence
                        for rails in [2, 3, 4, 5]:
                            pt = rail_fence_decrypt(vig_out_test, rails)
                            sc2 = qscore(pt)
                            wb2 = word_bonus(pt)
                            t2 = sc2 + wb2
                            if t2 > -480:
                                best_brute.append((t2, f"Brute/{alpha_label} key={key} RF={rails}", pt))

                    count += 1

        elapsed = time.time() - t0
        print(f"  Fixed pair ({fi},{fj}): {count} keys tested, {elapsed:.1f}s, "
              f"best brute so far: {max((r[0] for r in best_brute), default=-999):.1f}" if best_brute else f"  Fixed pair ({fi},{fj}): no results yet")

    print(f"Total keys tested: {count}")

    best_brute.sort(key=lambda x: -x[0])
    all_results.extend(best_brute[:100])

    # ====================================================================
    # PHASE 4: Deep SA on best transpositions found
    # ====================================================================
    print("\n" + "=" * 80)
    print("PHASE 4: Deep SA on Vig output with KRYPTOS alphabet")
    print("=" * 80)

    # The main vig_out with KRYPTOS alpha is the most promising
    text = vig_out
    print(f"Input: {text}")
    print(f"Base score: {qscore(text):.2f}")

    # Try deeper SA for the most promising widths
    for w in [7, 8, 9, 10, 11, 12, 13, 14]:
        best_of_all = -1e18
        best_of_all_pt = ""
        best_of_all_perm = None
        for restart in range(10):
            random.seed(restart * 31 + w)
            pt, sc, perm = sa_columnar(text, w, score, iterations=150000, restarts=1)
            if sc > best_of_all:
                best_of_all = sc
                best_of_all_pt = pt
                best_of_all_perm = perm
        all_results.append((best_of_all, f"DeepSA/KRYPTOS/Col w={w} p={best_of_all_perm}", best_of_all_pt))
        print(f"  w={w}: best={best_of_all:.1f}, perm={best_of_all_perm}")
        if best_of_all > qscore(text) + 15:
            print(f"    {best_of_all_pt[:80]}...")

    # Also deep SA for HypB
    print("\n  Deep SA for Hypothesis B (un-transpose K4, then Vig decrypt)")
    for w in [7, 8, 9, 10, 11, 13]:
        def score_b(ut):
            pt = vig_dec(ut, BEST_KEY, KRYPTOS_ALPHA)
            return score(pt)

        best_of_all = -1e18
        best_of_all_pt = ""
        best_of_all_perm = None
        for restart in range(10):
            random.seed(restart * 37 + w)
            ut_text, sc, perm = sa_columnar(K4, w, score_b, iterations=150000, restarts=1)
            ut = columnar_decrypt(K4, perm)
            pt = vig_dec(ut, BEST_KEY, KRYPTOS_ALPHA)
            real_sc = score(pt)
            if real_sc > best_of_all:
                best_of_all = real_sc
                best_of_all_pt = pt
                best_of_all_perm = perm
        all_results.append((best_of_all, f"DeepSA-B/KRYPTOS/Col w={w} p={best_of_all_perm}", best_of_all_pt))
        print(f"  B w={w}: best={best_of_all:.1f}")
        if best_of_all > -550:
            print(f"    {best_of_all_pt[:80]}...")

    # ====================================================================
    # FINAL RESULTS
    # ====================================================================
    print("\n" + "=" * 80)
    print("TOP 20 RESULTS (all methods)")
    print("=" * 80)

    all_results.sort(key=lambda x: -x[0])

    seen = set()
    unique = []
    for sc, desc, pt in all_results:
        if pt not in seen:
            seen.add(pt)
            unique.append((sc, desc, pt))

    for rank, (sc, desc, pt) in enumerate(unique[:20], 1):
        qs = qscore(pt)
        wb = word_bonus(pt)
        print(f"\n#{rank} Score={sc:.2f} (quad={qs:.2f}, words={wb})")
        print(f"  Method: {desc}")
        print(f"  Text: {pt}")
        found = [w for w in BONUS_VALUES if w in pt]
        if found:
            print(f"  ** WORDS: {', '.join(found)} **")

    # Show the raw vig output for comparison
    print("\n" + "-" * 60)
    print("BASELINE: Raw Vig decrypt with KRYPTOS alphabet")
    qs = qscore(vig_out)
    wb = word_bonus(vig_out)
    print(f"  Score={qs+wb:.2f} (quad={qs:.2f}, words={wb})")
    print(f"  {vig_out}")

    print(f"\nReference English (97 chars): qscore={qscore(ref):.2f}")
    print("\nDone.")


if __name__ == "__main__":
    main()
