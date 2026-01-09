#!/usr/bin/env python3
"""
K4 Advanced Attack - More sophisticated attempts

Theories being tested:
1. Double encryption (substitution + transposition)
2. Masking / XOR operations
3. Berlin Clock-based encoding
4. Route transposition variations
5. Modified Vigenère with irregular stepping
"""

import itertools
import string
from collections import Counter
import re

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known cribs
BERLIN_POS = 63  # 0-indexed start of BERLIN
CLOCK_POS = 69   # 0-indexed start of CLOCK

def vigenere_decrypt(ct, key, alpha=STANDARD_ALPHA):
    result = []
    ki = 0
    for c in ct:
        if c in alpha:
            result.append(alpha[(alpha.index(c) - alpha.index(key[ki % len(key)])) % len(alpha)])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def vigenere_encrypt(pt, key, alpha=STANDARD_ALPHA):
    result = []
    ki = 0
    for c in pt:
        if c in alpha:
            result.append(alpha[(alpha.index(c) + alpha.index(key[ki % len(key)])) % len(alpha)])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def columnar_transpose(text, key):
    """Columnar transposition with numeric key."""
    cols = len(key)
    rows = (len(text) + cols - 1) // cols
    # Pad text
    padded = text + 'X' * (rows * cols - len(text))

    # Create grid
    grid = [padded[i*cols:(i+1)*cols] for i in range(rows)]

    # Read off in key order
    result = ''
    for k in sorted(range(cols), key=lambda x: key[x]):
        for row in grid:
            if k < len(row):
                result += row[k]
    return result[:len(text)]

def columnar_untranspose(text, key):
    """Reverse columnar transposition."""
    cols = len(key)
    rows = (len(text) + cols - 1) // cols

    # Calculate column lengths
    full_cols = len(text) % cols or cols
    col_lens = [rows if i < full_cols else rows - 1 for i in range(cols)]

    # Distribute text into columns based on key order
    sorted_key = sorted(range(cols), key=lambda x: key[x])
    columns = [''] * cols
    pos = 0
    for k in sorted_key:
        columns[k] = text[pos:pos + col_lens[sorted_key.index(k)]]
        pos += col_lens[sorted_key.index(k)]

    # Read off row by row
    result = ''
    for r in range(rows):
        for c in range(cols):
            if r < len(columns[c]):
                result += columns[c][r]
    return result

def route_cipher(text, rows, cols, route='spiral'):
    """Route cipher - read text in different patterns."""
    if len(text) > rows * cols:
        return None

    # Pad text
    padded = text + 'X' * (rows * cols - len(text))

    # Create grid
    grid = [[padded[i*cols + j] for j in range(cols)] for i in range(rows)]

    result = ''
    if route == 'spiral_cw':
        # Clockwise spiral from outside
        top, bottom, left, right = 0, rows-1, 0, cols-1
        while top <= bottom and left <= right:
            for i in range(left, right+1): result += grid[top][i]
            top += 1
            for i in range(top, bottom+1): result += grid[i][right]
            right -= 1
            if top <= bottom:
                for i in range(right, left-1, -1): result += grid[bottom][i]
                bottom -= 1
            if left <= right:
                for i in range(bottom, top-1, -1): result += grid[i][left]
                left += 1
    elif route == 'diagonal':
        # Diagonal reading
        for d in range(rows + cols - 1):
            for i in range(max(0, d - cols + 1), min(d + 1, rows)):
                j = d - i
                if j < cols:
                    result += grid[i][j]
    elif route == 'zigzag':
        # Zigzag pattern
        for i in range(rows):
            if i % 2 == 0:
                result += ''.join(grid[i])
            else:
                result += ''.join(reversed(grid[i]))

    return result[:len(text)]

def try_double_encryption():
    """Try substitution followed by transposition or vice versa."""
    print("\n" + "="*70)
    print("DOUBLE ENCRYPTION ATTACKS")
    print("="*70)

    common_keywords = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK',
                      'KOMITET', 'SHADOW', 'SECRET', 'LANGLEY', 'AGENCY']

    # Try transposition THEN Vigenère
    print("\n--- Transposition then Vigenère ---")
    for cols in range(7, 15):
        for keyword in common_keywords:
            # Create numeric key from keyword
            key = [ord(c) - ord('A') for c in keyword[:cols]]
            while len(key) < cols:
                key.append(len(key))

            # Untranspose
            untrans = columnar_untranspose(K4, key[:cols])

            # Try Vigenère with various keys
            for vkey in common_keywords:
                for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                    pt = vigenere_decrypt(untrans, vkey, alpha)

                    if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTHEAST' in pt:
                        print(f"FOUND: cols={cols}, trans_key={keyword[:cols]}, vig_key={vkey}")
                        print(f"  Plaintext: {pt}")

    # Try Vigenère THEN transposition
    print("\n--- Vigenère then Transposition ---")
    for vkey in common_keywords:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            # First decrypt Vigenère
            intermediate = vigenere_decrypt(K4, vkey, alpha)

            # Then try various transpositions
            for cols in range(7, 15):
                for trans_key in common_keywords:
                    key = [ord(c) - ord('A') for c in trans_key[:cols]]
                    while len(key) < cols:
                        key.append(len(key))

                    pt = columnar_untranspose(intermediate, key[:cols])

                    if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTHEAST' in pt:
                        print(f"FOUND: vig_key={vkey}, cols={cols}, trans_key={trans_key[:cols]}")
                        print(f"  Plaintext: {pt}")

def try_masking():
    """Try XOR-like masking operations."""
    print("\n" + "="*70)
    print("MASKING ATTACKS")
    print("="*70)

    # In alphabetic terms, masking could mean adding/subtracting a repeating pattern

    # Known: positions 63-73 should give BERLINCLOCK
    target = "BERLINCLOCK"
    ct_segment = K4[63:74]  # NYPVTTMZFPK

    print(f"\nCiphertext segment: {ct_segment}")
    print(f"Target plaintext:   {target}")

    # Calculate the mask for the known segment
    mask = []
    for i, (c, p) in enumerate(zip(ct_segment, target)):
        ct_pos = KRYPTOS_ALPHA.index(c)
        pt_pos = KRYPTOS_ALPHA.index(p)
        mask_val = (ct_pos - pt_pos) % 26
        mask.append(mask_val)

    print(f"Derived mask values: {mask}")
    print(f"Mask as letters: {''.join(KRYPTOS_ALPHA[m] for m in mask)}")

    # Try extending this mask pattern
    print("\n--- Trying to find mask pattern ---")

    # Look for repeating patterns in the mask
    for period in range(1, 12):
        # Check if mask repeats with this period
        matches = True
        for i in range(len(mask)):
            for j in range(i + period, len(mask), period):
                if j < len(mask) and mask[i % period] != mask[j % period]:
                    matches = False
                    break

        if period <= len(mask):
            base_mask = mask[:period]
            print(f"Period {period}: base mask = {base_mask} = {''.join(KRYPTOS_ALPHA[m] for m in base_mask)}")

            # Try applying this mask to entire ciphertext
            full_mask = (base_mask * ((len(K4) // period) + 1))[:len(K4)]
            pt = ''
            for i, c in enumerate(K4):
                ct_pos = KRYPTOS_ALPHA.index(c) if c in KRYPTOS_ALPHA else ord(c) - ord('A')
                pt_pos = (ct_pos - full_mask[i]) % 26
                pt += KRYPTOS_ALPHA[pt_pos] if pt_pos < len(KRYPTOS_ALPHA) else chr(ord('A') + pt_pos)

            # Check if BERLINCLOCK appears at correct position
            if pt[63:74] == 'BERLINCLOCK':
                score = sum(1 for word in ['THE', 'AND', 'NORTHEAST', 'EAST', 'NORTH'] if word in pt)
                if score > 0 or 'NORTHEAST' in pt:
                    print(f"  *** Mask matches at period {period}! ***")
                    print(f"  Plaintext: {pt}")
                    print(f"  Score: {score}")

def try_berlin_clock():
    """Try Berlin Clock-themed approaches."""
    print("\n" + "="*70)
    print("BERLIN CLOCK ATTACKS")
    print("="*70)

    # The Berlin Clock displays time using illuminated colored blocks
    # Rows: 4 red (5 hrs), 4 red (1 hr), 11 (5 min, 3rd/6th/9th are red), 4 yellow (1 min)

    # Theory: key could relate to clock positions
    # 5-hour blocks: 4 positions
    # 1-hour blocks: 4 positions
    # 5-minute blocks: 11 positions
    # 1-minute blocks: 4 positions

    clock_periods = [4, 4, 11, 4, 23]  # Various Berlin Clock-related numbers

    print("\n--- Trying Berlin Clock periods ---")
    for period in clock_periods:
        print(f"\nPeriod {period}:")

        # Try Vigenère with this period
        for keyword in ['KRYPTOS', 'BERLIN', 'CLOCK', 'TIME', 'HOUR']:
            key = (keyword * ((period // len(keyword)) + 1))[:period]

            for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                pt = vigenere_decrypt(K4, key, alpha)

                if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTHEAST' in pt:
                    print(f"  Key={key}, Plaintext: {pt[:60]}...")

def try_route_ciphers():
    """Try various route cipher patterns."""
    print("\n" + "="*70)
    print("ROUTE CIPHER ATTACKS")
    print("="*70)

    # K4 has 97 characters - factor pairs: 97 is prime!
    # Try near-rectangular arrangements
    dimensions = [(7, 14), (14, 7), (8, 13), (13, 8), (10, 10), (11, 9), (9, 11)]
    routes = ['spiral_cw', 'diagonal', 'zigzag']

    for rows, cols in dimensions:
        if rows * cols >= len(K4):
            for route in routes:
                # Try reading K4 in this route
                result = route_cipher(K4, rows, cols, route)
                if result:
                    # Try Vigenère on the result
                    for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA']:
                        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                            pt = vigenere_decrypt(result, key, alpha)

                            if 'BERLIN' in pt or 'NORTHEAST' in pt:
                                print(f"Route {route} {rows}x{cols}, key={key}: {pt[:50]}...")

def try_progressive_key():
    """Try keys that change progressively."""
    print("\n" + "="*70)
    print("PROGRESSIVE KEY ATTACKS")
    print("="*70)

    # Theory: key shifts by some amount at each position or after certain intervals

    base_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'KOMITET']

    for base_key in base_keys:
        for shift in range(1, 5):
            for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                # Progressive shift key
                pt = ''
                for i, c in enumerate(K4):
                    if c in alpha:
                        key_char = base_key[i % len(base_key)]
                        key_pos = (alpha.index(key_char) + (i // len(base_key)) * shift) % len(alpha)
                        ct_pos = alpha.index(c)
                        pt_pos = (ct_pos - key_pos) % len(alpha)
                        pt += alpha[pt_pos]
                    else:
                        pt += c

                if 'BERLIN' in pt or 'NORTHEAST' in pt:
                    print(f"Base={base_key}, shift={shift}: {pt[:50]}...")

def exhaustive_northeast_search():
    """Search for NORTHEAST in all positions with various decryptions."""
    print("\n" + "="*70)
    print("NORTHEAST POSITION SEARCH")
    print("="*70)

    # NORTHEAST is 9 characters
    # It could be anywhere in the 97-char plaintext

    for start_pos in range(97 - 9):
        # Extract the ciphertext at this position
        ct_segment = K4[start_pos:start_pos + 9]
        target = "NORTHEAST"

        # Calculate required key for Vigenère
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            key_segment = ''
            valid = True
            for ct_c, pt_c in zip(ct_segment, target):
                if ct_c in alpha and pt_c in alpha:
                    key_val = (alpha.index(ct_c) - alpha.index(pt_c)) % len(alpha)
                    key_segment += alpha[key_val]
                else:
                    valid = False
                    break

            if valid:
                # Check if this key segment could be part of a repeating key
                # and if so, what the full decryption looks like
                for period in range(len(key_segment), len(key_segment) + 5):
                    # Try to extend key
                    if period >= len(key_segment):
                        for ext_len in range(period - len(key_segment) + 1):
                            for ext in itertools.product(alpha[:6], repeat=min(ext_len, 2)):
                                full_key = key_segment + ''.join(ext)
                                if len(full_key) >= period:
                                    test_key = full_key[:period]
                                    pt = vigenere_decrypt(K4, test_key, alpha)

                                    if 'NORTHEAST' in pt and ('BERLIN' in pt or pt[63:69] == 'BERLIN'):
                                        print(f"FOUND at pos {start_pos}!")
                                        print(f"  Key: {test_key}")
                                        print(f"  Plaintext: {pt}")
                                        return

def main():
    print("="*70)
    print("K4 ADVANCED ATTACK SUITE")
    print("="*70)
    print(f"Ciphertext: {K4}")
    print(f"Length: {len(K4)}")
    print(f"Looking for: BERLIN at pos 63, CLOCK at pos 69, NORTHEAST somewhere")

    try_masking()
    try_double_encryption()
    try_berlin_clock()
    try_route_ciphers()
    try_progressive_key()
    exhaustive_northeast_search()

    print("\n" + "="*70)
    print("ADVANCED ATTACK COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
