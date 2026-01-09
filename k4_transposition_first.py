#!/usr/bin/env python3
"""
K4 Transposition-First Attack

Theory: K4 might be transposition THEN substitution.
Try untransposing first, then applying Vigenère.

We know BERLINCLOCK should appear at position 63 in the FINAL plaintext.
If transposition was applied first, BERLINCLOCK letters would be scattered.
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

print("="*70)
print("K4 TRANSPOSITION-FIRST ATTACK")
print("="*70)

def columnar_untranspose(text, key_order):
    """Reverse columnar transposition given key order."""
    cols = len(key_order)
    rows = (len(text) + cols - 1) // cols

    # Calculate column lengths
    short_cols = rows * cols - len(text)
    col_lens = []
    for i in range(cols):
        if key_order.index(i) >= cols - short_cols:
            col_lens.append(rows - 1)
        else:
            col_lens.append(rows)

    # Split text into columns in key order
    columns = []
    pos = 0
    for i in sorted(range(cols), key=lambda x: key_order[x]):
        col_len = col_lens[i]
        columns.append((i, text[pos:pos + col_len]))
        pos += col_len

    # Reorder columns
    columns.sort(key=lambda x: x[0])

    # Read row by row
    result = ''
    for r in range(rows):
        for col_idx, col in columns:
            if r < len(col):
                result += col[r]

    return result

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    ki = 0
    for c in ct:
        if c in alpha:
            result.append(alpha[(alpha.index(c) - alpha.index(key[ki % len(key)])) % len(alpha)])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

# Try various columnar transposition keys followed by Vigenère
print("\n--- Columnar Untransposition then Vigenère ---")

common_keys = [
    'KRYPTOS',
    'PALIMPSEST',
    'ABSCISSA',
    'BERLIN',
    'CLOCK',
    'KOMITET',
]

# Also try numeric orders for columns
for cols in range(7, 14):
    print(f"\n=== Trying {cols} columns ===")

    # Try all permutations for small column counts
    if cols <= 8:
        perms_to_try = list(itertools.permutations(range(cols)))[:500]  # Limit
    else:
        # Just try some patterns
        perms_to_try = [
            tuple(range(cols)),  # Sequential
            tuple(range(cols-1, -1, -1)),  # Reversed
            tuple([cols-1] + list(range(cols-1))),  # Last first
        ]
        # Add keyword-based orders
        for kw in common_keys:
            if len(kw) >= cols:
                order = sorted(range(cols), key=lambda i: kw[i] if i < len(kw) else chr(ord('Z') + i))
                perms_to_try.append(tuple(order))

    for key_order in perms_to_try:
        # Untranspose
        untrans = columnar_untranspose(K4, key_order)

        # Try various Vigenère keys
        for vig_key in common_keys + ['OIECBAQKELY']:
            for alpha in [KRYPTOS_ALPHA]:
                pt = vigenere_decrypt(untrans, vig_key, alpha)

                # Check for both cribs
                if 'BERLINCLOCK' in pt:
                    print(f"FOUND BERLINCLOCK!")
                    print(f"  Cols: {cols}, Order: {key_order}")
                    print(f"  Vig key: {vig_key}")
                    print(f"  Plaintext: {pt}")

                if 'NORTHEAST' in pt:
                    print(f"FOUND NORTHEAST!")
                    print(f"  Cols: {cols}, Order: {key_order}")
                    print(f"  Vig key: {vig_key}")
                    print(f"  Plaintext: {pt}")

                # Check if both BERLIN and CLOCK appear (even if not together)
                if 'BERLIN' in pt and 'CLOCK' in pt and 'EAST' in pt:
                    print(f"Found BERLIN + CLOCK + EAST:")
                    print(f"  Cols: {cols}, Vig key: {vig_key}")
                    print(f"  Plaintext: {pt}")

# Also try route transpositions
print("\n" + "="*70)
print("ROUTE CIPHER THEN VIGENÈRE")
print("="*70)

def spiral_read(text, rows, cols):
    """Read text in spiral pattern."""
    if rows * cols < len(text):
        return None

    # Place text in grid
    grid = [['' for _ in range(cols)] for _ in range(rows)]
    idx = 0
    for r in range(rows):
        for c in range(cols):
            if idx < len(text):
                grid[r][c] = text[idx]
                idx += 1

    # Read spiral (clockwise from outside)
    result = ''
    top, bottom, left, right = 0, rows-1, 0, cols-1
    while top <= bottom and left <= right:
        for i in range(left, right+1):
            if grid[top][i]:
                result += grid[top][i]
        top += 1
        for i in range(top, bottom+1):
            if grid[i][right]:
                result += grid[i][right]
        right -= 1
        if top <= bottom:
            for i in range(right, left-1, -1):
                if grid[bottom][i]:
                    result += grid[bottom][i]
            bottom -= 1
        if left <= right:
            for i in range(bottom, top-1, -1):
                if grid[i][left]:
                    result += grid[i][left]
            left += 1

    return result

# 97 is prime, so try near-rectangular shapes
shapes = [(7, 14), (14, 7), (8, 13), (13, 8), (10, 10), (11, 9), (9, 11)]

for rows, cols in shapes:
    if rows * cols >= len(K4):
        spiral = spiral_read(K4, rows, cols)
        if spiral:
            for vig_key in common_keys:
                pt = vigenere_decrypt(spiral, vig_key, KRYPTOS_ALPHA)
                if 'BERLIN' in pt or 'NORTHEAST' in pt:
                    print(f"Found with spiral {rows}x{cols}, key={vig_key}:")
                    print(f"  {pt}")

print("\n" + "="*70)
print("SEARCH COMPLETE")
print("="*70)
