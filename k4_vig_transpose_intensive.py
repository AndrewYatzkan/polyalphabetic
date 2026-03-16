#!/usr/bin/env python3
"""
Intensive simulated annealing search for Kryptos K4:
Hypothesis: K4 = Vigenere(Transposition(plaintext), key)
Decrypt: V^-1 -> T^-1 -> plaintext

After undoing Vigenere with period-29 key, we get transposed text.
We then search for the inverse transposition that yields English.
"""

import math
import random
import time
import sys
from collections import defaultdict
from itertools import permutations

random.seed(42)

# ============================================================
# SETUP
# ============================================================

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
FULL_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"  # period 29, positions 16-20 = CBNJQ
N = len(K4_CIPHER)  # 97

# Load quadgrams
QUADGRAMS = {}
QG_FLOOR = 0.0
def load_quadgrams(path):
    global QUADGRAMS, QG_FLOOR
    total = 0
    raw = {}
    with open(path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                raw[parts[0]] = int(parts[1])
                total += int(parts[1])
    for k, v in raw.items():
        QUADGRAMS[k] = math.log10(v / total)
    QG_FLOOR = math.log10(0.01 / total)

load_quadgrams("/home/user/polyalphabetic/english_quadgrams.txt")

def qg_score(text):
    """Score text using quadgram frequencies."""
    s = 0.0
    t = text.upper()
    for i in range(len(t) - 3):
        q = t[i:i+4]
        if q in QUADGRAMS:
            s += QUADGRAMS[q]
        else:
            s += QG_FLOOR
    return s

# ============================================================
# VIGENERE DECRYPT (KRYPTOS alphabet)
# ============================================================

def kryptos_idx(c):
    return KRYPTOS_ALPHA.index(c)

def kryptos_chr(i):
    return KRYPTOS_ALPHA[i % 26]

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenere with KRYPTOS alphabet."""
    result = []
    klen = len(key)
    for i, c in enumerate(ciphertext):
        ci = kryptos_idx(c)
        ki = kryptos_idx(key[i % klen])
        pi = (ci - ki) % 26
        result.append(kryptos_chr(pi))
    return ''.join(result)

# Get the transposed text by undoing Vigenere
TRANSPOSED = vigenere_decrypt(K4_CIPHER, FULL_KEY)
print(f"K4 ciphertext ({N} chars): {K4_CIPHER}")
print(f"Full key (period 29): {FULL_KEY}")
print(f"After Vigenere decrypt (transposed text): {TRANSPOSED}")
print(f"Position 21-33: {TRANSPOSED[21:34]}")
print(f"Position 63-73: {TRANSPOSED[63:74]}")
print()

# Verify cribs
assert TRANSPOSED[21:34] == "EASTNORTHEAST", f"Crib mismatch at 21-33: {TRANSPOSED[21:34]}"
assert TRANSPOSED[63:74] == "BERLINCLOCK", f"Crib mismatch at 63-73: {TRANSPOSED[63:74]}"
print("Cribs verified: EASTNORTHEAST@21-33 and BERLINCLOCK@63-73")
print("=" * 70)

# ============================================================
# ENGLISH WORD DETECTION
# ============================================================

COMMON_WORDS = [
    "THE", "AND", "THAT", "WITH", "THIS", "HAVE", "FROM", "THEY",
    "BEEN", "SAID", "EACH", "WHICH", "THEIR", "WILL", "OTHER",
    "ABOUT", "MANY", "THEN", "THEM", "THESE", "SOME", "WOULD",
    "MAKE", "LIKE", "TIME", "VERY", "WHEN", "WHAT", "YOUR", "WERE",
    "THERE", "BETWEEN", "UNDER", "NORTH", "EAST", "SOUTH", "WEST",
    "BERLIN", "CLOCK", "DEGREES", "LAYER", "SLOWLY", "DESPER",
    "BURIED", "SECRET", "HIDDEN", "BELOW", "ABOVE", "GROUND",
    "LANGLEY", "SHADOW", "LIGHT", "DARK", "FORCE", "EARTH",
    "WATER", "FIRE", "PASSAGE", "TUNNEL", "DOOR", "OPEN",
    "CLOSE", "NEAR", "ONLY", "KNOW", "COULD", "INTO", "OVER",
    "THROUGH", "WHERE", "HERE", "LOCATION", "POINT", "EXACT",
    "COORDINATES", "LATITUDE", "LONGITUDE", "MINUTES", "SECONDS",
    "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST",
    "WHO", "CAN", "NOT", "ALL", "HER", "WAS", "ONE", "OUR", "OUT",
]

def count_english_words(text):
    """Count how many common English words appear in the text."""
    t = text.upper()
    count = 0
    total_len = 0
    found = []
    for w in COMMON_WORDS:
        if len(w) >= 3 and w in t:
            count += 1
            total_len += len(w)
            found.append(w)
    return count, total_len, found

# ============================================================
# TRANSPOSITION METHODS
# ============================================================

# --- Columnar Transposition ---
def columnar_encrypt(plaintext, col_order):
    """Encrypt: write plaintext in rows, read off by column order."""
    ncols = len(col_order)
    nrows = math.ceil(len(plaintext) / ncols)
    # Pad
    padded = plaintext + 'X' * (nrows * ncols - len(plaintext))
    # Write into grid row by row
    grid = []
    for r in range(nrows):
        grid.append(list(padded[r*ncols:(r+1)*ncols]))
    # Read off columns in the given order
    result = []
    for c in col_order:
        for r in range(nrows):
            result.append(grid[r][c])
    return ''.join(result)[:len(plaintext)]

def columnar_decrypt(ciphertext, col_order):
    """Decrypt columnar transposition."""
    ncols = len(col_order)
    n = len(ciphertext)
    nrows = math.ceil(n / ncols)
    # Calculate column lengths
    full_cols = n % ncols if n % ncols != 0 else ncols
    col_lens = []
    for c in range(ncols):
        if c < full_cols or full_cols == ncols:
            col_lens.append(nrows)
        else:
            col_lens.append(nrows - 1)

    # Read ciphertext into columns according to col_order
    cols = [''] * ncols
    idx = 0
    for c in col_order:
        clen = col_lens[c]
        cols[c] = ciphertext[idx:idx+clen]
        idx += clen

    # Read off row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return ''.join(result)[:n]

# --- Rail Fence ---
def rail_fence_decrypt(ciphertext, nrails):
    n = len(ciphertext)
    if nrails <= 1 or nrails >= n:
        return ciphertext
    # Calculate the pattern
    pattern = []
    for i in range(n):
        cycle = 2 * (nrails - 1)
        pos = i % cycle
        rail = pos if pos < nrails else cycle - pos
        pattern.append(rail)

    # Count chars per rail
    rail_counts = [0] * nrails
    for r in pattern:
        rail_counts[r] += 1

    # Split ciphertext into rails
    rails = []
    idx = 0
    for r in range(nrails):
        rails.append(list(ciphertext[idx:idx+rail_counts[r]]))
        idx += rail_counts[r]

    # Read off
    rail_idx = [0] * nrails
    result = []
    for r in pattern:
        result.append(rails[r][rail_idx[r]])
        rail_idx[r] += 1
    return ''.join(result)

# --- Route Cipher ---
def route_spiral_decrypt(ciphertext, nrows, ncols):
    """Read ciphertext into grid, read out in spiral pattern."""
    n = len(ciphertext)
    if nrows * ncols < n:
        return None
    # Fill grid
    grid = [['' for _ in range(ncols)] for _ in range(nrows)]
    idx = 0
    for r in range(nrows):
        for c in range(ncols):
            if idx < n:
                grid[r][c] = ciphertext[idx]
                idx += 1
            else:
                grid[r][c] = 'X'

    # Spiral read
    result = []
    top, bottom, left, right = 0, nrows-1, 0, ncols-1
    while top <= bottom and left <= right:
        for c in range(left, right+1):
            if grid[top][c]: result.append(grid[top][c])
        top += 1
        for r in range(top, bottom+1):
            if grid[r][right]: result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left-1, -1):
                if grid[bottom][c]: result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top-1, -1):
                if grid[r][left]: result.append(grid[r][left])
            left += 1
    return ''.join(result)[:n]

def route_snake_decrypt(ciphertext, nrows, ncols):
    """Read into grid, read out in snake (boustrophedon) pattern."""
    n = len(ciphertext)
    if nrows * ncols < n:
        return None
    grid = [['' for _ in range(ncols)] for _ in range(nrows)]
    idx = 0
    for r in range(nrows):
        for c in range(ncols):
            if idx < n:
                grid[r][c] = ciphertext[idx]
                idx += 1
            else:
                grid[r][c] = 'X'

    result = []
    for r in range(nrows):
        if r % 2 == 0:
            for c in range(ncols):
                if grid[r][c]: result.append(grid[r][c])
        else:
            for c in range(ncols-1, -1, -1):
                if grid[r][c]: result.append(grid[r][c])
    return ''.join(result)[:n]

# --- Block permutation ---
def block_permute(text, block_size, perm):
    """Permute characters within each block."""
    n = len(text)
    result = list(text)
    for start in range(0, n, block_size):
        block = text[start:start+block_size]
        blen = len(block)
        for i in range(blen):
            if perm[i] < blen:
                result[start + i] = block[perm[i]]
    return ''.join(result)

# ============================================================
# SIMULATED ANNEALING FOR COLUMNAR TRANSPOSITION
# ============================================================

def sa_columnar(text, width, iterations=500000, T_start=10.0, alpha=0.9999, restarts=5):
    """SA search for best column order for columnar transposition decrypt."""
    best_score_overall = -float('inf')
    best_order_overall = None
    best_text_overall = None

    for restart in range(restarts):
        # Random initial column order
        order = list(range(width))
        random.shuffle(order)

        decrypted = columnar_decrypt(text, order)
        current_score = qg_score(decrypted)
        best_score = current_score
        best_order = order[:]
        best_text = decrypted

        T = T_start
        for it in range(iterations):
            # Swap two columns
            i, j = random.sample(range(width), 2)
            order[i], order[j] = order[j], order[i]

            decrypted = columnar_decrypt(text, order)
            new_score = qg_score(decrypted)

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                current_score = new_score
                if current_score > best_score:
                    best_score = current_score
                    best_order = order[:]
                    best_text = decrypted
            else:
                order[i], order[j] = order[j], order[i]

            T *= alpha

        if best_score > best_score_overall:
            best_score_overall = best_score
            best_order_overall = best_order[:]
            best_text_overall = best_text

    return best_score_overall, best_order_overall, best_text_overall

# ============================================================
# SA FOR BLOCK PERMUTATION
# ============================================================

def sa_block_perm(text, block_size, iterations=300000, T_start=10.0, alpha=0.9999, restarts=3):
    """SA search for best block permutation."""
    best_score_overall = -float('inf')
    best_perm_overall = None
    best_text_overall = None

    for restart in range(restarts):
        perm = list(range(block_size))
        random.shuffle(perm)

        decrypted = block_permute(text, block_size, perm)
        current_score = qg_score(decrypted)
        best_score = current_score
        best_perm = perm[:]
        best_text = decrypted

        T = T_start
        for it in range(iterations):
            i, j = random.sample(range(block_size), 2)
            perm[i], perm[j] = perm[j], perm[i]

            decrypted = block_permute(text, block_size, perm)
            new_score = qg_score(decrypted)

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                current_score = new_score
                if current_score > best_score:
                    best_score = current_score
                    best_perm = perm[:]
                    best_text = decrypted
            else:
                perm[i], perm[j] = perm[j], perm[i]

            T *= alpha

        if best_score > best_score_overall:
            best_score_overall = best_score
            best_perm_overall = best_perm[:]
            best_text_overall = best_text

    return best_score_overall, best_perm_overall, best_text_overall

# ============================================================
# SA FOR GENERAL POSITION PERMUTATION (full shuffle)
# ============================================================

def sa_full_permutation(text, iterations=1000000, T_start=10.0, alpha=0.99999, restarts=3):
    """SA search over all possible position permutations."""
    n = len(text)
    best_score_overall = -float('inf')
    best_perm_overall = None
    best_text_overall = None

    for restart in range(restarts):
        perm = list(range(n))
        random.shuffle(perm)

        decrypted = ''.join(text[perm[i]] for i in range(n))
        current_score = qg_score(decrypted)
        best_score = current_score
        best_perm = perm[:]
        best_text = decrypted

        T = T_start
        for it in range(iterations):
            i, j = random.sample(range(n), 2)
            # Swap in perm
            perm[i], perm[j] = perm[j], perm[i]

            # Incremental score would be ideal but let's just rescore
            decrypted = ''.join(text[perm[k]] for k in range(n))
            new_score = qg_score(decrypted)

            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                current_score = new_score
                if current_score > best_score:
                    best_score = current_score
                    best_perm = perm[:]
                    best_text = decrypted
            else:
                perm[i], perm[j] = perm[j], perm[i]

            T *= alpha

        if best_score > best_score_overall:
            best_score_overall = best_score
            best_perm_overall = best_perm[:]
            best_text_overall = best_text

    return best_score_overall, best_perm_overall, best_text_overall

# ============================================================
# SA FOR DOUBLE COLUMNAR (encrypt then encrypt again)
# ============================================================

def sa_double_columnar(text, w1, w2, iterations=300000, T_start=10.0, alpha=0.9999, restarts=3):
    """SA for double columnar: decrypt col2 then decrypt col1."""
    best_score_overall = -float('inf')
    best_result = None

    for restart in range(restarts):
        order1 = list(range(w1))
        order2 = list(range(w2))
        random.shuffle(order1)
        random.shuffle(order2)

        dec1 = columnar_decrypt(text, order2)
        dec2 = columnar_decrypt(dec1, order1)
        current_score = qg_score(dec2)
        best_score = current_score
        best_o1, best_o2 = order1[:], order2[:]
        best_text = dec2

        T = T_start
        for it in range(iterations):
            # Alternate between modifying order1 and order2
            if random.random() < 0.5:
                i, j = random.sample(range(w1), 2)
                order1[i], order1[j] = order1[j], order1[i]
                dec1 = columnar_decrypt(text, order2)
                dec2 = columnar_decrypt(dec1, order1)
                new_score = qg_score(dec2)
                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / T):
                    current_score = new_score
                    if current_score > best_score:
                        best_score = current_score
                        best_o1, best_o2 = order1[:], order2[:]
                        best_text = dec2
                else:
                    order1[i], order1[j] = order1[j], order1[i]
            else:
                i, j = random.sample(range(w2), 2)
                order2[i], order2[j] = order2[j], order2[i]
                dec1 = columnar_decrypt(text, order2)
                dec2 = columnar_decrypt(dec1, order1)
                new_score = qg_score(dec2)
                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / T):
                    current_score = new_score
                    if current_score > best_score:
                        best_score = current_score
                        best_o1, best_o2 = order1[:], order2[:]
                        best_text = dec2
                else:
                    order2[i], order2[j] = order2[j], order2[i]

            T *= alpha

        if best_score > best_score_overall:
            best_score_overall = best_score
            best_result = (best_o1[:], best_o2[:], best_text)

    return best_score_overall, best_result

# ============================================================
# MAIN SEARCH
# ============================================================

def main():
    start_time = time.time()
    TIME_LIMIT = 280  # seconds, leave margin

    all_results = []

    def report(method, score, text, detail=""):
        wc, wl, words = count_english_words(text)
        all_results.append((score, method, text, detail, words))
        if score > -650 or wc >= 3:
            print(f"\n*** {method} | Score: {score:.2f} | Words: {wc} ({', '.join(words[:10])}) ***")
            print(f"    Text: {text}")
            if detail:
                print(f"    Detail: {detail}")

    def time_remaining():
        return TIME_LIMIT - (time.time() - start_time)

    # ============================================================
    # PART 1: Simple transformations
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 1: Simple transformations (reverse, rail fence, route ciphers)")
    print("=" * 70)

    # Reverse
    rev = TRANSPOSED[::-1]
    score = qg_score(rev)
    report("Reverse", score, rev)

    # Rail fence
    for nrails in range(2, 21):
        dec = rail_fence_decrypt(TRANSPOSED, nrails)
        score = qg_score(dec)
        report(f"Rail fence {nrails}", score, dec)

    # Rail fence on reversed text
    for nrails in range(2, 21):
        dec = rail_fence_decrypt(rev, nrails)
        score = qg_score(dec)
        report(f"Rail fence {nrails} (reversed)", score, dec)

    # Route ciphers - various grid sizes
    grid_sizes = []
    for r in range(2, 50):
        for c in range(2, 50):
            if r * c >= 97 and r * c <= 100:
                grid_sizes.append((r, c))

    for nr, nc in grid_sizes:
        dec = route_spiral_decrypt(TRANSPOSED, nr, nc)
        if dec:
            score = qg_score(dec)
            report(f"Spiral {nr}x{nc}", score, dec)

        dec = route_snake_decrypt(TRANSPOSED, nr, nc)
        if dec:
            score = qg_score(dec)
            report(f"Snake {nr}x{nc}", score, dec)

        # Also read by columns instead of rows
        # Transpose: read by columns
        grid = [['' for _ in range(nc)] for _ in range(nr)]
        idx = 0
        for r in range(nr):
            for c in range(nc):
                if idx < N:
                    grid[r][c] = TRANSPOSED[idx]
                    idx += 1
        col_read = ''
        for c in range(nc):
            for r in range(nr):
                if grid[r][c]:
                    col_read += grid[r][c]
        col_read = col_read[:N]
        score = qg_score(col_read)
        report(f"Column read {nr}x{nc}", score, col_read)

    elapsed = time.time() - start_time
    print(f"\nPart 1 complete. Time: {elapsed:.1f}s")

    # ============================================================
    # PART 2: Columnar transposition with SA
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 2: Columnar transposition with simulated annealing")
    print("=" * 70)

    # Allocate time: ~150s for columnar SA
    columnar_results = []

    # Phase 1: Quick scan of all widths
    print("\nPhase 2a: Quick scan all widths 2-20, 29, 97...")
    quick_widths = list(range(2, 21)) + [29, 97]
    for width in quick_widths:
        if time_remaining() < 60:
            print("Time running low, skipping remaining quick scans")
            break
        iters = 100000
        restarts = 2
        score, order, text = sa_columnar(TRANSPOSED, width, iterations=iters, restarts=restarts)
        columnar_results.append((score, width, order, text))
        report(f"Columnar w={width}", score, text, f"order={order}")

    # Phase 2: Intensive search on best widths
    columnar_results.sort(reverse=True)
    print(f"\nPhase 2b: Intensive SA on top widths...")
    top_widths = set()
    for score, width, order, text in columnar_results[:5]:
        top_widths.add(width)
        print(f"  Top candidate: width={width}, score={score:.2f}")

    for width in top_widths:
        if time_remaining() < 40:
            print("Time running low, stopping intensive search")
            break
        print(f"  Intensive SA on width={width}...")
        score, order, text = sa_columnar(TRANSPOSED, width, iterations=500000, T_start=10.0, alpha=0.99995, restarts=5)
        report(f"Columnar w={width} (intensive)", score, text, f"order={order}")

    # Also try with reversed text
    print("\nPhase 2c: Columnar on reversed text...")
    for width in [5, 7, 10, 13, 14, 29]:
        if time_remaining() < 30:
            break
        score, order, text = sa_columnar(rev, width, iterations=200000, restarts=3)
        report(f"Columnar w={width} (reversed)", score, text, f"order={order}")

    elapsed = time.time() - start_time
    print(f"\nPart 2 complete. Time: {elapsed:.1f}s")

    # ============================================================
    # PART 3: Block permutations with SA
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 3: Block permutations with SA")
    print("=" * 70)

    for block_size in [5, 7, 10, 13, 14, 29]:
        if time_remaining() < 20:
            print("Time running low, stopping block perms")
            break
        print(f"  Block size {block_size}...")
        score, perm, text = sa_block_perm(TRANSPOSED, block_size, iterations=200000, restarts=3)
        report(f"Block perm bs={block_size}", score, text, f"perm={perm}")

    # Block perms on reversed
    for block_size in [5, 7, 10, 29]:
        if time_remaining() < 15:
            break
        score, perm, text = sa_block_perm(rev, block_size, iterations=150000, restarts=2)
        report(f"Block perm bs={block_size} (rev)", score, text, f"perm={perm}")

    elapsed = time.time() - start_time
    print(f"\nPart 3 complete. Time: {elapsed:.1f}s")

    # ============================================================
    # PART 4: Double columnar transposition
    # ============================================================
    print("\n" + "=" * 70)
    print("PART 4: Double columnar transposition")
    print("=" * 70)

    double_pairs = [(5, 7), (7, 5), (5, 10), (10, 5), (7, 14), (14, 7), (5, 29), (29, 5)]
    for w1, w2 in double_pairs:
        if time_remaining() < 15:
            print("Time running low, stopping double columnar")
            break
        print(f"  Double columnar {w1}x{w2}...")
        score, result = sa_double_columnar(TRANSPOSED, w1, w2, iterations=200000, restarts=2)
        if result:
            o1, o2, text = result
            report(f"Double columnar {w1}x{w2}", score, text, f"o1={o1}, o2={o2}")

    elapsed = time.time() - start_time
    print(f"\nPart 4 complete. Time: {elapsed:.1f}s")

    # ============================================================
    # PART 5: Full position permutation SA
    # ============================================================
    if time_remaining() > 20:
        print("\n" + "=" * 70)
        print("PART 5: Full position permutation SA")
        print("=" * 70)

        remaining_iters = min(500000, int(time_remaining() * 15000))  # rough estimate
        print(f"  Running with ~{remaining_iters} iterations, {max(1, int(time_remaining()//20))} restarts...")
        score, perm, text = sa_full_permutation(TRANSPOSED, iterations=remaining_iters,
                                                  restarts=max(1, min(3, int(time_remaining()//20))))
        report("Full perm SA", score, text)

        elapsed = time.time() - start_time
        print(f"\nPart 5 complete. Time: {elapsed:.1f}s")

    # ============================================================
    # PART 6: Disrupted columnar & irregular patterns
    # ============================================================
    if time_remaining() > 15:
        print("\n" + "=" * 70)
        print("PART 6: Myszkowski & disrupted columnar")
        print("=" * 70)

        # Try Myszkowski-like: some columns share the same number
        # This is like columnar but with groups
        for width in [7, 10, 13, 14]:
            if time_remaining() < 10:
                break
            # Try reading columns in different groupings
            ncols = width
            nrows = math.ceil(N / ncols)

            # Standard column read with different starting offsets
            for offset in range(ncols):
                col_order = [(offset + i) % ncols for i in range(ncols)]
                dec = columnar_decrypt(TRANSPOSED, col_order)
                score = qg_score(dec)
                if score > -650:
                    report(f"Shifted columnar w={width} off={offset}", score, dec)

    # ============================================================
    # PART 7: Specific period-29 related transpositions
    # ============================================================
    if time_remaining() > 10:
        print("\n" + "=" * 70)
        print("PART 7: Period-29 specific transpositions")
        print("=" * 70)

        # Since Vigenere period is 29, transposition might also use 29
        # Try: read text into 29-column grid, permute rows
        nrows_29 = math.ceil(N / 29)  # 4 rows

        # Try all 4! = 24 row permutations
        for rperm in permutations(range(nrows_29)):
            result = []
            for r in rperm:
                start = r * 29
                end = min(start + 29, N)
                result.extend(list(TRANSPOSED[start:end]))
            text = ''.join(result[:N])
            score = qg_score(text)
            if score > -650:
                report(f"Row perm 29-col {rperm}", score, text)

        # Try: read into grid with various widths, permute rows
        for width in [7, 10, 13, 14]:
            if time_remaining() < 5:
                break
            nrows_w = math.ceil(N / width)
            if nrows_w <= 10:  # manageable number of row permutations via SA
                # SA on row permutation
                best_s = -float('inf')
                best_t = None
                for _ in range(3):
                    rperm = list(range(nrows_w))
                    random.shuffle(rperm)

                    def apply_row_perm(rp):
                        res = []
                        for r in rp:
                            start = r * width
                            end = min(start + width, N)
                            res.extend(list(TRANSPOSED[start:end]))
                        return ''.join(res[:N])

                    cur_text = apply_row_perm(rperm)
                    cur_score = qg_score(cur_text)
                    best_local_s = cur_score
                    best_local_rp = rperm[:]

                    T = 5.0
                    for it in range(50000):
                        i, j = random.sample(range(nrows_w), 2)
                        rperm[i], rperm[j] = rperm[j], rperm[i]
                        new_text = apply_row_perm(rperm)
                        new_score = qg_score(new_text)
                        delta = new_score - cur_score
                        if delta > 0 or random.random() < math.exp(delta / max(T, 0.001)):
                            cur_score = new_score
                            if cur_score > best_local_s:
                                best_local_s = cur_score
                                best_local_rp = rperm[:]
                        else:
                            rperm[i], rperm[j] = rperm[j], rperm[i]
                        T *= 0.9999

                    if best_local_s > best_s:
                        best_s = best_local_s
                        best_t = apply_row_perm(best_local_rp)

                if best_t:
                    report(f"Row perm SA w={width}", best_s, best_t)

    # ============================================================
    # PART 8: Keyed columnar with keyword-derived orders
    # ============================================================
    if time_remaining() > 5:
        print("\n" + "=" * 70)
        print("PART 8: Keyword-derived columnar keys")
        print("=" * 70)

        # Try keywords related to Kryptos
        keywords = [
            "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "BERLIN",
            "SANBORN", "SCHEIDT", "LANGLEY", "CLOCK", "NORTHEAST",
            "BETWEEN", "SUBTLE", "SHADING", "IQLUSION", "UNDERGROUND",
            "LAYER", "INVISIBLE", "DIGETAL", "VIRTUAL", "MAGNETIC",
            "COMPASS", "BEARING", "DEGREE", "MINUTES", "SECONDS",
        ]

        def keyword_to_order(kw):
            """Convert keyword to column order."""
            indexed = sorted(range(len(kw)), key=lambda i: (kw[i], i))
            order = [0] * len(kw)
            for rank, idx in enumerate(indexed):
                order[idx] = rank
            return order

        for kw in keywords:
            if time_remaining() < 2:
                break
            order = keyword_to_order(kw)
            dec = columnar_decrypt(TRANSPOSED, order)
            score = qg_score(dec)
            report(f"Keyword '{kw}' columnar", score, dec, f"order={order}")

            # Also try as the encrypt direction (inverse)
            inv_order = [0] * len(order)
            for i, o in enumerate(order):
                inv_order[o] = i
            dec2 = columnar_decrypt(TRANSPOSED, inv_order)
            score2 = qg_score(dec2)
            report(f"Keyword '{kw}' inv columnar", score2, dec2, f"order={inv_order}")

    # ============================================================
    # FINAL SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("FINAL SUMMARY - TOP 20 RESULTS")
    print("=" * 70)

    all_results.sort(reverse=True)
    seen = set()
    rank = 0
    for score, method, text, detail, words in all_results:
        if text in seen:
            continue
        seen.add(text)
        rank += 1
        if rank > 20:
            break
        wc = len(words) if words else 0
        print(f"\n#{rank}: Score={score:.2f} | {method}")
        print(f"  Text: {text}")
        if words:
            print(f"  Words ({wc}): {', '.join(words[:15])}")
        if detail:
            print(f"  Detail: {detail}")

    elapsed = time.time() - start_time
    print(f"\nTotal time: {elapsed:.1f}s")
    print(f"Total configurations tested: {len(all_results)}")

if __name__ == "__main__":
    main()
