#!/usr/bin/env python3
"""
Simultaneous optimization of Vigenere key + columnar transposition
using simulated annealing.

Hypothesis: K4 = Vig(Transpose(PT), key) or K4 = Transpose(Vig(PT, key))
We need to find both the correct key positions 16-20 AND the transposition.
"""
import math, random, time
from collections import Counter

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c): return KRYPTOS.index(c)
def k_chr(i): return KRYPTOS[i % 26]

# Load quadgrams
QG = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QG[parts[0]] = int(parts[1])
total = sum(QG.values())
QG_LOG = {k: math.log10(v/total) for k, v in QG.items()}
QG_FLOOR = math.log10(0.01/total)

def qscore(text):
    score = 0
    for i in range(len(text)-3):
        q = text[i:i+4]
        score += QG_LOG.get(q, QG_FLOOR)
    return score

def vig_decrypt(ct, key):
    pt = []
    for i, c in enumerate(ct):
        ki = k_idx(key[i % len(key)])
        ci = k_idx(c)
        pt.append(k_chr((ci - ki) % 26))
    return ''.join(pt)

# Known key (positions 0-15 and 21-28 are fixed from cribs)
KNOWN = list("OYNKYELYOIECBAQK?????RDUMRIYW")
KNOWN_MASK = [c != '?' for c in KNOWN]

def make_key(unknowns):
    """Build full 29-char key from 5 unknown values."""
    key = list(KNOWN)
    for i, v in enumerate(unknowns):
        key[16+i] = KRYPTOS[v]
    return ''.join(key)

def columnar_untranspose(text, ncols, col_order):
    """Reverse columnar transposition: given text read by columns, reconstruct row-reading."""
    n = len(text)
    nrows = (n + ncols - 1) // ncols
    full_cols = n % ncols if n % ncols != 0 else ncols
    
    # Determine column lengths
    col_lens = []
    for c in range(ncols):
        if c < full_cols or full_cols == ncols:
            col_lens.append(nrows)
        else:
            col_lens.append(nrows - 1)
    
    # Split text into columns according to col_order
    cols = [''] * ncols
    pos = 0
    for order_idx in range(ncols):
        col = col_order[order_idx]
        length = col_lens[col]
        cols[col] = text[pos:pos+length]
        pos += length
    
    # Read by rows
    result = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(cols[col]):
                result.append(cols[col][row])
    return ''.join(result)

def columnar_transpose(text, ncols, col_order):
    """Forward columnar transposition: write by rows, read by columns in col_order."""
    n = len(text)
    nrows = (n + ncols - 1) // ncols
    
    # Pad text
    padded = text + 'X' * (nrows * ncols - n)
    
    # Read by columns in col_order
    result = []
    for order_idx in range(ncols):
        col = col_order[order_idx]
        for row in range(nrows):
            pos = row * ncols + col
            if pos < n:
                result.append(padded[pos])
    return ''.join(result[:n])

# CRIB WORDS for bonus scoring
CRIB_WORDS = ["BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST", "SLOWLY", "DESPERATELY",
              "BETWEEN", "SHADOW", "LAYER", "BURIED", "HIDDEN", "SECRET", "DEGREE",
              "BEARING", "COMPASS", "POINT", "GRID", "STERN", "GROSSER"]

def word_bonus(text):
    bonus = 0
    for w in CRIB_WORDS:
        if w in text:
            bonus += len(w) * 5
    return bonus

print("=" * 80)
print("HYPOTHESIS A: K4 = Vig(PT, key) [no transposition, just optimize key]")
print("=" * 80)

# Brute force all 26^5 with quadgram scoring
best_score = -999999
best_key = None
best_pt = None

t0 = time.time()
for v0 in range(26):
    for v1 in range(26):
        for v2 in range(26):
            for v3 in range(26):
                for v4 in range(26):
                    key = make_key([v0,v1,v2,v3,v4])
                    pt = vig_decrypt(K4, key)
                    s = qscore(pt) + word_bonus(pt)
                    if s > best_score:
                        best_score = s
                        best_key = key
                        best_pt = pt

elapsed = time.time() - t0
print(f"Brute force 26^5 in {elapsed:.1f}s")
print(f"Best key: {best_key}")
print(f"Best PT:  {best_pt}")
print(f"Score:    {best_score:.2f}")
print(f"Words:    {[w for w in CRIB_WORDS if w in best_pt]}")

# Check if BERLINCLOCK and EASTNORTHEAST are present
if "BERLINCLOCK" in best_pt:
    print(f"  BERLINCLOCK at pos {best_pt.index('BERLINCLOCK')}")
if "EASTNORTHEAST" in best_pt:
    print(f"  EASTNORTHEAST at pos {best_pt.index('EASTNORTHEAST')}")

print("\n" + "=" * 80)
print("HYPOTHESIS B: K4 = Transpose(Vig(PT, key))")
print("  Decrypt: PT = Vig^-1(Transpose^-1(K4), key)")
print("=" * 80)

# For each column width, try SA on column order
for ncols in [7, 8, 9, 10, 11, 13, 14, 29]:
    if 97 % ncols == 0 or ncols <= 14:
        best_col_score = -999999
        best_col_order = None
        best_col_pt = None
        best_col_key = None
        
        # Use the brute-force best key as starting point
        unknowns = [k_idx(best_key[16+i]) for i in range(5)]
        
        # SA on column order
        nrows = (97 + ncols - 1) // ncols
        col_order = list(range(ncols))
        
        T = 5.0
        T_min = 0.01
        alpha = 0.9995
        
        current_order = col_order[:]
        current_unknowns = unknowns[:]
        
        # Compute current score
        key = make_key(current_unknowns)
        untransposed = columnar_untranspose(K4, ncols, current_order)
        pt = vig_decrypt(untransposed, key)
        current_score = qscore(pt) + word_bonus(pt)
        
        best_local = current_score
        best_local_order = current_order[:]
        best_local_unknowns = current_unknowns[:]
        best_local_pt = pt
        
        iterations = 0
        max_iter = 200000
        
        while T > T_min and iterations < max_iter:
            iterations += 1
            
            # Choose mutation type
            r = random.random()
            new_order = current_order[:]
            new_unknowns = current_unknowns[:]
            
            if r < 0.6:
                # Swap two columns
                i, j = random.sample(range(ncols), 2)
                new_order[i], new_order[j] = new_order[j], new_order[i]
            elif r < 0.8:
                # Move a column to a new position
                i = random.randrange(ncols)
                j = random.randrange(ncols)
                col = new_order.pop(i)
                new_order.insert(j, col)
            else:
                # Mutate a key unknown
                pos = random.randrange(5)
                new_unknowns[pos] = random.randrange(26)
            
            key = make_key(new_unknowns)
            untransposed = columnar_untranspose(K4, ncols, new_order)
            pt = vig_decrypt(untransposed, key)
            new_score = qscore(pt) + word_bonus(pt)
            
            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                current_order = new_order
                current_unknowns = new_unknowns
                current_score = new_score
                
                if current_score > best_local:
                    best_local = current_score
                    best_local_order = current_order[:]
                    best_local_unknowns = current_unknowns[:]
                    best_local_pt = pt
            
            T *= alpha
        
        if best_local > best_col_score:
            best_col_score = best_local
            best_col_order = best_local_order
            best_col_pt = best_local_pt
            best_col_key = make_key(best_local_unknowns)
        
        print(f"\n  Width {ncols}: best score = {best_col_score:.2f}")
        print(f"    Col order: {best_col_order}")
        print(f"    Key:       {best_col_key}")
        print(f"    PT:        {best_col_pt}")
        words = [w for w in CRIB_WORDS if w in best_col_pt]
        if words:
            print(f"    *** WORDS: {words} ***")

print("\n" + "=" * 80)
print("HYPOTHESIS C: K4 = Vig(Transpose(PT), key)")
print("  Decrypt: PT = Transpose^-1(Vig^-1(K4, key))")
print("=" * 80)

# First Vig decrypt, then un-transpose
for ncols in [7, 8, 9, 10, 11, 13, 14, 29]:
    if 97 % ncols == 0 or ncols <= 14:
        best_local = -999999
        best_local_order = None
        best_local_pt = None
        best_local_key = None
        
        unknowns = [k_idx(best_key[16+i]) for i in range(5)]
        col_order = list(range(ncols))
        current_order = col_order[:]
        current_unknowns = unknowns[:]
        
        key = make_key(current_unknowns)
        vig_output = vig_decrypt(K4, key)
        pt = columnar_untranspose(vig_output, ncols, current_order)
        current_score = qscore(pt) + word_bonus(pt)
        
        T = 5.0
        T_min = 0.01
        alpha = 0.9995
        iterations = 0
        max_iter = 200000
        
        while T > T_min and iterations < max_iter:
            iterations += 1
            
            r = random.random()
            new_order = current_order[:]
            new_unknowns = current_unknowns[:]
            
            if r < 0.6:
                i, j = random.sample(range(ncols), 2)
                new_order[i], new_order[j] = new_order[j], new_order[i]
            elif r < 0.8:
                i = random.randrange(ncols)
                j = random.randrange(ncols)
                col = new_order.pop(i)
                new_order.insert(j, col)
            else:
                pos = random.randrange(5)
                new_unknowns[pos] = random.randrange(26)
            
            key = make_key(new_unknowns)
            vig_output = vig_decrypt(K4, key)
            pt = columnar_untranspose(vig_output, ncols, new_order)
            new_score = qscore(pt) + word_bonus(pt)
            
            delta = new_score - current_score
            if delta > 0 or random.random() < math.exp(delta / T):
                current_order = new_order
                current_unknowns = new_unknowns
                current_score = new_score
                
                if current_score > best_local:
                    best_local = current_score
                    best_local_order = current_order[:]
                    best_local_unknowns = current_unknowns[:]
                    best_local_pt = pt
                    best_local_key = make_key(current_unknowns)
            
            T *= alpha
        
        print(f"\n  Width {ncols}: best score = {best_local:.2f}")
        print(f"    Col order: {best_local_order}")
        print(f"    Key:       {best_local_key}")
        print(f"    PT:        {best_local_pt}")
        words = [w for w in CRIB_WORDS if w in best_local_pt]
        if words:
            print(f"    *** WORDS: {words} ***")

print("\nDone.")
