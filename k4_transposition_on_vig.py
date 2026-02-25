#!/usr/bin/env python3
"""
K4 Transposition-after-Vigenere Attack
=======================================
Hypothesis: PT -> Transposition -> Vigenere -> CT
So: Vig^-1(CT) = Transposed(PT)
We try to un-transpose the Vigenere decryption output to recover English.

Approaches:
1. Columnar transposition (SA for column order)
2. General block permutation (small blocks: exhaustive; large: SA)
3. Route cipher (various grid routes)
4. Rail fence
5. AMSCO transposition
6. Myszkowski transposition
"""

import math
import random
import itertools
import time
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"
PERIOD = 29

# Known candidate words from K4 context
KNOWN_WORDS = [
    "BERLINCLOCK", "BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST",
    "SLOWLY", "DESPERATELY", "SHADOW", "UNDERGROUND", "SECRET",
    "LANGLEY", "LAYER", "BURIED", "BETWEEN", "DEGREES",
    "LATITUDE", "LONGITUDE", "PALIMPSEST", "ABSCISSA",
    "IQLUSION", "ILLUSION", "VIRTUALLY", "INVISIBLE",
    "DIGETAL", "INTERPRETATIU", "THEYSHOULDBE",
    "WEST", "SOUTH", "TIME", "LIGHT", "DARK",
    "OBSCURE", "SOS", "HELP", "DEAD", "LIFE",
    "WATER", "FIRE", "EARTH", "COORDINATES",
]

# ============================================================
# LOAD QUADGRAMS
# ============================================================
print("Loading quadgrams...")
QUADGRAMS = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QUADGRAMS[parts[0]] = int(parts[1])

TOTAL_QG = sum(QUADGRAMS.values())
LOG_QUADGRAMS = {}
floor_val = math.log10(0.01 / TOTAL_QG)
for qg, count in QUADGRAMS.items():
    LOG_QUADGRAMS[qg] = math.log10(count / TOTAL_QG)
print(f"Loaded {len(LOG_QUADGRAMS)} quadgrams. Floor value: {floor_val:.4f}")

# ============================================================
# VIGENERE DECRYPTION WITH KRYPTOS ALPHABET
# ============================================================
def vig_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    pt = []
    for i, c in enumerate(ct):
        ci = alpha.index(c)
        ki = alpha.index(key[i % len(key)])
        pi = (ci - ki) % 26
        pt.append(alpha[pi])
    return ''.join(pt)

VIG_OUTPUT = vig_decrypt(CT, KEY)
print(f"\nCiphertext ({len(CT)} chars): {CT}")
print(f"Key (period {PERIOD}): {KEY}")
print(f"Vig decrypt output: {VIG_OUTPUT}")
print(f"Length: {len(VIG_OUTPUT)}")

# ============================================================
# SCORING FUNCTIONS
# ============================================================
def quadgram_score(text):
    """Score text using quadgram log-likelihood."""
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += LOG_QUADGRAMS.get(qg, floor_val)
    return score

def check_known_words(text):
    """Check for known K4-related words in text."""
    found = []
    for word in KNOWN_WORDS:
        if word in text:
            found.append(word)
    return found

def ic_score(text):
    """Index of coincidence."""
    if len(text) < 2:
        return 0
    freq = defaultdict(int)
    for c in text:
        freq[c] += 1
    n = len(text)
    ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    return ic

# ============================================================
# 1. COLUMNAR TRANSPOSITION ATTACK (SA)
# ============================================================
def columnar_untranspose(text, ncols, col_order):
    """
    Un-do columnar transposition.
    During encryption: text written in rows of ncols, read out by columns in col_order.
    To decrypt: distribute ciphertext back into columns (in col_order), then read rows.
    """
    n = len(text)
    nrows = math.ceil(n / ncols)
    # Number of full columns
    full_cols = n - (nrows - 1) * ncols  # columns that have nrows chars
    # But if n is exact multiple, all cols are full
    if n % ncols == 0:
        full_cols = ncols
    
    # Determine length of each column in the order they were read out
    col_lengths = []
    for col_idx in col_order:
        if col_idx < full_cols:
            col_lengths.append(nrows)
        else:
            col_lengths.append(nrows - 1)
    
    # Split ciphertext into columns (in the order given by col_order)
    cols = {}
    pos = 0
    for i, col_idx in enumerate(col_order):
        length = col_lengths[i]
        cols[col_idx] = text[pos:pos+length]
        pos += length
    
    # Read off rows
    result = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(cols.get(col, '')):
                result.append(cols[col][row])
    
    return ''.join(result)

def sa_columnar(text, ncols, iterations=50000, temp_start=2.0, temp_end=0.01):
    """Simulated annealing for columnar transposition column order."""
    n = len(text)
    if ncols < 2 or ncols > n:
        return None, float('-inf')
    
    # Initial random order
    current_order = list(range(ncols))
    random.shuffle(current_order)
    
    current_text = columnar_untranspose(text, ncols, current_order)
    current_score = quadgram_score(current_text)
    
    best_order = current_order[:]
    best_score = current_score
    best_text = current_text
    
    for i in range(iterations):
        temp = temp_start * (temp_end / temp_start) ** (i / iterations)
        
        # Swap two columns
        new_order = current_order[:]
        a, b = random.sample(range(ncols), 2)
        new_order[a], new_order[b] = new_order[b], new_order[a]
        
        new_text = columnar_untranspose(text, ncols, new_order)
        new_score = quadgram_score(new_text)
        
        delta = new_score - current_score
        if delta > 0 or random.random() < math.exp(delta / temp):
            current_order = new_order
            current_score = new_score
            current_text = new_text
            
            if current_score > best_score:
                best_score = current_score
                best_order = current_order[:]
                best_text = current_text
    
    return best_order, best_score, best_text

def attack_columnar(text):
    """Try columnar transposition with SA for various widths."""
    print("\n" + "="*70)
    print("ATTACK 1: COLUMNAR TRANSPOSITION (Simulated Annealing)")
    print("="*70)
    
    results = []
    
    for ncols in range(2, 21):
        best_overall_score = float('-inf')
        best_overall_order = None
        best_overall_text = None
        
        # Run SA multiple times for each width
        for trial in range(5):
            order, score, decrypted = sa_columnar(text, ncols, iterations=80000)
            if score > best_overall_score:
                best_overall_score = score
                best_overall_order = order
                best_overall_text = decrypted
        
        words = check_known_words(best_overall_text)
        results.append((ncols, best_overall_score, best_overall_order, best_overall_text, words))
        
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"  Width {ncols:2d}: score={best_overall_score:8.2f}  order={best_overall_order}  text={best_overall_text[:50]}...{word_str}")
    
    # Sort by score and show top results
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  TOP 5 COLUMNAR RESULTS:")
    for ncols, score, order, text, words in results[:5]:
        ic = ic_score(text)
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"    Width {ncols:2d}: score={score:8.2f}  IC={ic:.4f}  order={order}")
        print(f"              text={text}{word_str}")
    
    return results

# ============================================================
# 2. BLOCK PERMUTATION ATTACK
# ============================================================
def block_permute(text, block_size, perm):
    """Apply a permutation within blocks of given size."""
    result = []
    for start in range(0, len(text), block_size):
        block = text[start:start+block_size]
        new_block = []
        for p in perm:
            if p < len(block):
                new_block.append(block[p])
            # If block is shorter (last block), skip missing positions
        # Add any remaining chars not covered by perm
        result.extend(new_block)
    return ''.join(result)

def attack_block_permutation(text):
    """Try all permutations for small block sizes, SA for larger."""
    print("\n" + "="*70)
    print("ATTACK 2: BLOCK PERMUTATION")
    print("="*70)
    
    results = []
    
    # Exhaustive for small blocks (2-8)
    for bsize in range(2, 9):
        best_score = float('-inf')
        best_perm = None
        best_text = None
        
        for perm in itertools.permutations(range(bsize)):
            decrypted = block_permute(text, bsize, perm)
            score = quadgram_score(decrypted)
            if score > best_score:
                best_score = score
                best_perm = perm
                best_text = decrypted
        
        words = check_known_words(best_text)
        results.append((bsize, best_score, best_perm, best_text, words))
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"  Block {bsize}: score={best_score:8.2f}  perm={best_perm}  text={best_text[:50]}...{word_str}")
    
    # SA for larger blocks (9-10)
    for bsize in range(9, 11):
        best_score = float('-inf')
        best_perm = None
        best_text = None
        
        for trial in range(10):
            current_perm = list(range(bsize))
            random.shuffle(current_perm)
            current_text = block_permute(text, bsize, current_perm)
            current_score = quadgram_score(current_text)
            
            for i in range(30000):
                temp = 2.0 * (0.01 / 2.0) ** (i / 30000)
                new_perm = current_perm[:]
                a, b = random.sample(range(bsize), 2)
                new_perm[a], new_perm[b] = new_perm[b], new_perm[a]
                new_text = block_permute(text, bsize, new_perm)
                new_score = quadgram_score(new_text)
                
                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / temp):
                    current_perm = new_perm
                    current_score = new_score
                    current_text = new_text
                    
                    if current_score > best_score:
                        best_score = current_score
                        best_perm = tuple(current_perm)
                        best_text = current_text
        
        words = check_known_words(best_text)
        results.append((bsize, best_score, best_perm, best_text, words))
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"  Block {bsize}: score={best_score:8.2f}  perm={best_perm}  text={best_text[:50]}...{word_str}")
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  TOP 3 BLOCK PERMUTATION RESULTS:")
    for bsize, score, perm, text, words in results[:3]:
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"    Block {bsize}: score={score:8.2f}  perm={perm}")
        print(f"              text={text}{word_str}")
    
    return results

# ============================================================
# 3. ROUTE CIPHER ATTACK
# ============================================================
def route_column_read(text, nrows, ncols, col_order=None):
    """Write text into grid by rows, read by columns."""
    grid = []
    for r in range(nrows):
        row = []
        for c in range(ncols):
            idx = r * ncols + c
            if idx < len(text):
                row.append(text[idx])
            else:
                row.append('')
        grid.append(row)
    
    if col_order is None:
        col_order = list(range(ncols))
    
    result = []
    for c in col_order:
        for r in range(nrows):
            if grid[r][c]:
                result.append(grid[r][c])
    return ''.join(result)

def route_spiral_read(text, nrows, ncols):
    """Write text into grid by rows, read in spiral order."""
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
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            if grid[top][c]: result.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            if grid[r][right]: result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if grid[bottom][c]: result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if grid[r][left]: result.append(grid[r][left])
            left += 1
    return ''.join(result)

def route_diagonal_read(text, nrows, ncols):
    """Write text into grid by rows, read diagonally."""
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
    for d in range(nrows + ncols - 1):
        for r in range(min(d, nrows - 1), max(d - ncols + 1, 0) - 1 if d - ncols + 1 > 0 else -1, -1):
            c = d - r
            if 0 <= r < nrows and 0 <= c < ncols and grid[r][c]:
                result.append(grid[r][c])
    return ''.join(result)

def route_zigzag_read(text, nrows, ncols):
    """Write text into grid by rows, read in zigzag (alternating column direction)."""
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

def route_reverse_spiral_untranspose(text, nrows, ncols):
    """
    If encryption was: write in spiral, read by rows -> CT.
    Then to decrypt: write CT by rows into grid, read in spiral.
    But we also try the reverse: write CT in spiral, read by rows.
    """
    # Create spiral order of positions
    positions = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            positions.append((top, c))
        top += 1
        for r in range(top, bottom + 1):
            positions.append((r, right))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                positions.append((bottom, c))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                positions.append((r, left))
            left += 1
    
    # Write text into spiral positions
    grid = [['' for _ in range(ncols)] for _ in range(nrows)]
    for i, (r, c) in enumerate(positions):
        if i < len(text):
            grid[r][c] = text[i]
    
    # Read by rows
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c]:
                result.append(grid[r][c])
    return ''.join(result)

def attack_route_cipher(text):
    """Try various route cipher un-transpositions."""
    print("\n" + "="*70)
    print("ATTACK 3: ROUTE CIPHER")
    print("="*70)
    
    n = len(text)
    results = []
    
    for nrows in range(2, 48):
        ncols_float = n / nrows
        for ncols in [math.floor(ncols_float), math.ceil(ncols_float)]:
            if ncols < 2 or nrows * ncols < n - ncols:
                continue
            
            # Try various route reads
            routes = {
                "col_read": lambda t, nr=nrows, nc=ncols: route_column_read(t, nr, nc),
                "spiral": lambda t, nr=nrows, nc=ncols: route_spiral_read(t, nr, nc),
                "diagonal": lambda t, nr=nrows, nc=ncols: route_diagonal_read(t, nr, nc),
                "zigzag": lambda t, nr=nrows, nc=ncols: route_zigzag_read(t, nr, nc),
                "rev_spiral": lambda t, nr=nrows, nc=ncols: route_reverse_spiral_untranspose(t, nr, nc),
            }
            
            for route_name, route_fn in routes.items():
                try:
                    decrypted = route_fn(text)
                    if len(decrypted) != n:
                        continue
                    score = quadgram_score(decrypted)
                    words = check_known_words(decrypted)
                    results.append((f"{nrows}x{ncols} {route_name}", score, decrypted, words))
                except:
                    pass
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"  Tested {len(results)} route combinations.")
    print(f"\n  TOP 10 ROUTE CIPHER RESULTS:")
    for desc, score, text_out, words in results[:10]:
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"    {desc:25s}: score={score:8.2f}  text={text_out[:50]}...{word_str}")
    
    return results

# ============================================================
# 4. RAIL FENCE ATTACK
# ============================================================
def rail_fence_decrypt(text, nrails):
    """Decrypt rail fence cipher."""
    n = len(text)
    if nrails < 2 or nrails >= n:
        return text
    
    # Calculate the length of each rail
    rail_lens = [0] * nrails
    rail = 0
    direction = 1
    for i in range(n):
        rail_lens[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == nrails - 1:
            direction = -1
        rail += direction
    
    # Split text into rails
    rails = []
    pos = 0
    for r in range(nrails):
        rails.append(text[pos:pos+rail_lens[r]])
        pos += rail_lens[r]
    
    # Read off in zigzag order
    result = []
    rail_pos = [0] * nrails
    rail = 0
    direction = 1
    for i in range(n):
        result.append(rails[rail][rail_pos[rail]])
        rail_pos[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == nrails - 1:
            direction = -1
        rail += direction
    
    return ''.join(result)

def attack_rail_fence(text):
    """Try rail fence with various depths."""
    print("\n" + "="*70)
    print("ATTACK 4: RAIL FENCE")
    print("="*70)
    
    results = []
    for depth in range(2, 20):
        decrypted = rail_fence_decrypt(text, depth)
        score = quadgram_score(decrypted)
        words = check_known_words(decrypted)
        results.append((depth, score, decrypted, words))
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"  Depth {depth:2d}: score={score:8.2f}  text={decrypted[:50]}...{word_str}")
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  BEST RAIL FENCE: depth={results[0][0]}, score={results[0][1]:.2f}")
    print(f"  text={results[0][2]}")
    return results

# ============================================================
# 5. AMSCO TRANSPOSITION ATTACK
# ============================================================
def amsco_decrypt(text, ncols, col_order, start_with=1):
    """
    Decrypt AMSCO transposition.
    AMSCO alternates taking 1 and 2 characters per cell.
    start_with: 1 or 2 (which size the first cell uses)
    """
    n = len(text)
    
    # First, figure out how many chars go in each column
    # Build the grid structure (how many chars per cell)
    grid = []
    pos = 0
    row = 0
    while pos < n:
        row_data = []
        for col in range(ncols):
            if pos >= n:
                row_data.append(0)
                continue
            # Determine cell size: alternates 1,2,1,2... or 2,1,2,1...
            cell_num = row * ncols + col
            if start_with == 1:
                size = 1 if cell_num % 2 == 0 else 2
            else:
                size = 2 if cell_num % 2 == 0 else 1
            size = min(size, n - pos)
            row_data.append(size)
            pos += size
        grid.append(row_data)
        row += 1
    
    nrows = len(grid)
    
    # Calculate chars per column (in column order)
    col_chars = [0] * ncols
    for r in range(nrows):
        for c in range(ncols):
            col_chars[c] += grid[r][c]
    
    # Distribute ciphertext to columns in col_order
    col_data = {}
    pos = 0
    for c in col_order:
        col_data[c] = text[pos:pos+col_chars[c]]
        pos += col_chars[c]
    
    # Read rows
    result = []
    col_pos = {c: 0 for c in range(ncols)}
    for r in range(nrows):
        for c in range(ncols):
            size = grid[r][c]
            if size > 0:
                result.append(col_data[c][col_pos[c]:col_pos[c]+size])
                col_pos[c] += size
    
    return ''.join(result)

def attack_amsco(text):
    """Try AMSCO transposition with SA for column order."""
    print("\n" + "="*70)
    print("ATTACK 5: AMSCO TRANSPOSITION (SA)")
    print("="*70)
    
    results = []
    
    for ncols in range(2, 13):
        for start_with in [1, 2]:
            best_score = float('-inf')
            best_order = None
            best_text = None
            
            for trial in range(3):
                current_order = list(range(ncols))
                random.shuffle(current_order)
                
                try:
                    current_text = amsco_decrypt(text, ncols, current_order, start_with)
                    current_score = quadgram_score(current_text)
                except:
                    continue
                
                for i in range(40000):
                    temp = 2.0 * (0.01 / 2.0) ** (i / 40000)
                    new_order = current_order[:]
                    a, b = random.sample(range(ncols), 2)
                    new_order[a], new_order[b] = new_order[b], new_order[a]
                    
                    try:
                        new_text = amsco_decrypt(text, ncols, new_order, start_with)
                        new_score = quadgram_score(new_text)
                    except:
                        continue
                    
                    delta = new_score - current_score
                    if delta > 0 or random.random() < math.exp(delta / temp):
                        current_order = new_order
                        current_score = new_score
                        current_text = new_text
                        
                        if current_score > best_score:
                            best_score = current_score
                            best_order = current_order[:]
                            best_text = current_text
            
            if best_text:
                words = check_known_words(best_text)
                results.append((ncols, start_with, best_score, best_order, best_text, words))
                word_str = f" *** WORDS: {words}" if words else ""
                print(f"  AMSCO cols={ncols:2d} start={start_with}: score={best_score:8.2f}  text={best_text[:50]}...{word_str}")
    
    results.sort(key=lambda x: x[2], reverse=True)
    print(f"\n  TOP 5 AMSCO RESULTS:")
    for ncols, sw, score, order, text_out, words in results[:5]:
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"    AMSCO cols={ncols} start={sw}: score={score:8.2f}  order={order}")
        print(f"              text={text_out}{word_str}")
    
    return results

# ============================================================
# 6. MYSZKOWSKI TRANSPOSITION ATTACK
# ============================================================
def myszkowski_decrypt(text, key_order):
    """
    Myszkowski transposition: like columnar but columns with same key value
    are read left-to-right across rows before moving to next row.
    key_order: list of ints, e.g. [2,0,1,2] means cols 0,3 share value 2.
    """
    n = len(text)
    ncols = len(key_order)
    nrows = math.ceil(n / ncols)
    full_cols = n - (nrows - 1) * ncols
    if n % ncols == 0:
        full_cols = ncols
    
    # Group columns by key value
    key_groups = defaultdict(list)
    for i, k in enumerate(key_order):
        key_groups[k].append(i)
    
    sorted_keys = sorted(key_groups.keys())
    
    # Distribute text to column groups
    col_data = {}
    pos = 0
    for k in sorted_keys:
        cols = key_groups[k]
        if len(cols) == 1:
            # Single column - normal columnar
            c = cols[0]
            length = nrows if c < full_cols else nrows - 1
            col_data[c] = text[pos:pos+length]
            pos += length
        else:
            # Multiple columns - read across rows
            total_chars = sum(nrows if c < full_cols else nrows - 1 for c in cols)
            group_text = text[pos:pos+total_chars]
            pos += total_chars
            
            # Distribute across rows
            col_data_group = {c: [] for c in cols}
            gi = 0
            for r in range(nrows):
                for c in cols:
                    if r < (nrows if c < full_cols else nrows - 1):
                        if gi < len(group_text):
                            col_data_group[c].append(group_text[gi])
                            gi += 1
            for c in cols:
                col_data[c] = ''.join(col_data_group[c])
    
    # Read rows
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(col_data.get(c, '')):
                result.append(col_data[c][r])
    
    return ''.join(result)

def attack_myszkowski(text):
    """Try Myszkowski transposition with SA."""
    print("\n" + "="*70)
    print("ATTACK 6: MYSZKOWSKI TRANSPOSITION (SA)")
    print("="*70)
    
    results = []
    
    for ncols in range(3, 11):
        best_score = float('-inf')
        best_key = None
        best_text = None
        
        # Try keys with some repeated values
        for trial in range(5):
            # Generate random key with some repeats
            n_unique = random.randint(max(2, ncols - 3), ncols)
            vals = list(range(n_unique))
            current_key = [random.choice(vals) for _ in range(ncols)]
            
            try:
                current_text = myszkowski_decrypt(text, current_key)
                current_score = quadgram_score(current_text)
            except:
                continue
            
            for i in range(30000):
                temp = 2.0 * (0.01 / 2.0) ** (i / 30000)
                new_key = current_key[:]
                
                # Random mutation
                mut_type = random.random()
                if mut_type < 0.5:
                    # Change one value
                    pos = random.randint(0, ncols - 1)
                    new_key[pos] = random.randint(0, ncols - 1)
                else:
                    # Swap two values
                    a, b = random.sample(range(ncols), 2)
                    new_key[a], new_key[b] = new_key[b], new_key[a]
                
                try:
                    new_text = myszkowski_decrypt(text, new_key)
                    new_score = quadgram_score(new_text)
                except:
                    continue
                
                delta = new_score - current_score
                if delta > 0 or random.random() < math.exp(delta / temp):
                    current_key = new_key
                    current_score = new_score
                    current_text = new_text
                    
                    if current_score > best_score:
                        best_score = current_score
                        best_key = current_key[:]
                        best_text = current_text
        
        if best_text:
            words = check_known_words(best_text)
            results.append((ncols, best_score, best_key, best_text, words))
            word_str = f" *** WORDS: {words}" if words else ""
            print(f"  Myszkowski cols={ncols:2d}: score={best_score:8.2f}  key={best_key}  text={best_text[:50]}...{word_str}")
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  TOP 3 MYSZKOWSKI RESULTS:")
    for ncols, score, key, text_out, words in results[:3]:
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"    cols={ncols}: score={score:8.2f}  key={key}")
        print(f"              text={text_out}{word_str}")
    
    return results

# ============================================================
# 7. GENERAL POSITION PERMUTATION (SA) - Full shuffle
# ============================================================
def attack_general_permutation(text):
    """
    SA on a full position permutation - the most general attack.
    Start from identity and use swaps to explore.
    """
    print("\n" + "="*70)
    print("ATTACK 7: GENERAL POSITION PERMUTATION (SA)")
    print("="*70)
    
    n = len(text)
    best_overall_score = float('-inf')
    best_overall_perm = None
    best_overall_text = None
    
    for trial in range(5):
        # Start from a random permutation
        current_perm = list(range(n))
        random.shuffle(current_perm)
        current_text = ''.join(text[current_perm[i]] for i in range(n))
        current_score = quadgram_score(current_text)
        
        best_score = current_score
        best_perm = current_perm[:]
        best_text = current_text
        
        iterations = 200000
        for i in range(iterations):
            temp = 5.0 * (0.001 / 5.0) ** (i / iterations)
            
            # Swap two positions
            a, b = random.sample(range(n), 2)
            
            # Incremental score update would be ideal but quadgrams make it complex
            # Just recalculate for positions affected
            new_perm = current_perm[:]
            new_perm[a], new_perm[b] = new_perm[b], new_perm[a]
            new_text = ''.join(text[new_perm[j]] for j in range(n))
            new_score = quadgram_score(new_text)
            
            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / temp):
                current_perm = new_perm
                current_score = new_score
                current_text = new_text
                
                if current_score > best_score:
                    best_score = current_score
                    best_perm = current_perm[:]
                    best_text = current_text
        
        if best_score > best_overall_score:
            best_overall_score = best_score
            best_overall_perm = best_perm
            best_overall_text = best_text
        
        words = check_known_words(best_text)
        word_str = f" *** WORDS: {words}" if words else ""
        print(f"  Trial {trial+1}: score={best_score:8.2f}  text={best_text[:60]}...{word_str}")
    
    words = check_known_words(best_overall_text)
    word_str = f" *** WORDS: {words}" if words else ""
    print(f"\n  BEST GENERAL PERMUTATION: score={best_overall_score:.2f}")
    print(f"  text={best_overall_text}{word_str}")
    
    return best_overall_score, best_overall_perm, best_overall_text

# ============================================================
# ALSO TRY: reversed text, and combining with reversal
# ============================================================
def attack_simple_transforms(text):
    """Try simple transforms: reverse, every-nth, etc."""
    print("\n" + "="*70)
    print("ATTACK 0: SIMPLE TRANSFORMS (baseline)")
    print("="*70)
    
    results = []
    
    # Identity (baseline)
    score = quadgram_score(text)
    results.append(("identity", score, text))
    print(f"  Identity:     score={score:8.2f}  text={text[:50]}...")
    
    # Reverse
    rev = text[::-1]
    score = quadgram_score(rev)
    results.append(("reverse", score, rev))
    print(f"  Reverse:      score={score:8.2f}  text={rev[:50]}...")
    
    # Every nth character (decimation)
    n = len(text)
    for step in range(2, 20):
        if math.gcd(step, n) == 1:  # Only coprime steps give full text
            dec = ''.join(text[(i * step) % n] for i in range(n))
            score = quadgram_score(dec)
            words = check_known_words(dec)
            results.append((f"decimate_{step}", score, dec))
            word_str = f" *** WORDS: {words}" if words else ""
            if score > -400:
                print(f"  Decimate {step:2d}: score={score:8.2f}  text={dec[:50]}...{word_str}")
    
    results.sort(key=lambda x: x[1], reverse=True)
    print(f"\n  BEST SIMPLE TRANSFORM: {results[0][0]}, score={results[0][1]:.2f}")
    print(f"  text={results[0][2][:60]}...")
    
    return results

# ============================================================
# MAIN
# ============================================================
def main():
    random.seed(42)  # For reproducibility
    
    text = VIG_OUTPUT
    print(f"\nVigenere output to un-transpose: {text}")
    print(f"Length: {len(text)}")
    print(f"IC: {ic_score(text):.4f} (English ~0.0667)")
    print(f"Quadgram score: {quadgram_score(text):.2f}")
    
    start_time = time.time()
    
    # Run all attacks
    all_results = {}
    
    all_results['simple'] = attack_simple_transforms(text)
    all_results['rail_fence'] = attack_rail_fence(text)
    all_results['block_perm'] = attack_block_permutation(text)
    all_results['columnar'] = attack_columnar(text)
    all_results['route'] = attack_route_cipher(text)
    all_results['amsco'] = attack_amsco(text)
    all_results['myszkowski'] = attack_myszkowski(text)
    all_results['general'] = attack_general_permutation(text)
    
    # Also try on reversed Vigenere output
    print("\n" + "="*70)
    print("BONUS: COLUMNAR SA ON REVERSED VIG OUTPUT")
    print("="*70)
    rev_text = text[::-1]
    print(f"  Reversed: {rev_text}")
    rev_results = []
    for ncols in range(2, 16):
        best_score = float('-inf')
        best_text = None
        best_order = None
        for trial in range(3):
            order, score, decrypted = sa_columnar(rev_text, ncols, iterations=50000)
            if score > best_score:
                best_score = score
                best_text = decrypted
                best_order = order
        words = check_known_words(best_text)
        rev_results.append((ncols, best_score, best_order, best_text, words))
        word_str = f" *** WORDS: {words}" if words else ""
        if words or best_score > -380:
            print(f"  Rev width {ncols:2d}: score={best_score:8.2f}  text={best_text[:50]}...{word_str}")
    
    rev_results.sort(key=lambda x: x[1], reverse=True)
    print(f"  Best reversed columnar: width={rev_results[0][0]}, score={rev_results[0][1]:.2f}")
    print(f"  text={rev_results[0][3]}")
    
    elapsed = time.time() - start_time
    
    # ============================================================
    # GRAND SUMMARY
    # ============================================================
    print("\n" + "="*70)
    print("GRAND SUMMARY")
    print("="*70)
    print(f"Total time: {elapsed:.1f} seconds")
    
    # Collect all top results across all methods
    grand = []
    
    for name, score, text_out in all_results['simple'][:3]:
        grand.append((f"Simple/{name}", score, text_out, check_known_words(text_out)))
    
    for depth, score, text_out, words in all_results['rail_fence'][:3]:
        grand.append((f"RailFence/d={depth}", score, text_out, words))
    
    for bsize, score, perm, text_out, words in all_results['block_perm'][:3]:
        grand.append((f"BlockPerm/b={bsize}", score, text_out, words))
    
    for ncols, score, order, text_out, words in all_results['columnar'][:3]:
        grand.append((f"Columnar/w={ncols}", score, text_out, words))
    
    for desc, score, text_out, words in all_results['route'][:3]:
        grand.append((f"Route/{desc}", score, text_out, words))
    
    for ncols, sw, score, order, text_out, words in all_results['amsco'][:3]:
        grand.append((f"AMSCO/c={ncols},s={sw}", score, text_out, words))
    
    for ncols, score, key, text_out, words in all_results['myszkowski'][:3]:
        grand.append((f"Myszkowski/c={ncols}", score, text_out, words))
    
    gen_score, gen_perm, gen_text = all_results['general']
    grand.append(("GeneralPerm", gen_score, gen_text, check_known_words(gen_text)))
    
    for ncols, score, order, text_out, words in rev_results[:3]:
        grand.append((f"RevColumnar/w={ncols}", score, text_out, words))
    
    grand.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nTOP 20 RESULTS ACROSS ALL METHODS:")
    print(f"{'Rank':>4s}  {'Method':30s}  {'Score':>8s}  {'Words':15s}  Text")
    print("-" * 120)
    for i, (method, score, text_out, words) in enumerate(grand[:20]):
        word_str = ','.join(words) if words else "-"
        print(f"{i+1:4d}  {method:30s}  {score:8.2f}  {word_str:15s}  {text_out[:55]}")
    
    # Check if any result found known words
    print(f"\nRESULTS WITH KNOWN WORDS:")
    found_any = False
    for method, score, text_out, words in grand:
        if words:
            print(f"  {method}: score={score:.2f} words={words}")
            print(f"  text={text_out}")
            found_any = True
    if not found_any:
        print("  None found.")
    
    # Show the absolute best
    print(f"\nABSOLUTE BEST RESULT:")
    best = grand[0]
    print(f"  Method: {best[0]}")
    print(f"  Score:  {best[1]:.2f}")
    print(f"  Text:   {best[2]}")
    print(f"  Words:  {best[3] if best[3] else 'None'}")
    print(f"  IC:     {ic_score(best[2]):.4f}")

if __name__ == "__main__":
    main()
