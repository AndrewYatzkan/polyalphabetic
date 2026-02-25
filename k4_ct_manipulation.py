#!/usr/bin/env python3
"""
K4 Ciphertext Manipulation Analysis
====================================

Tests the hypothesis that K4 ciphertext needs to be REARRANGED or MODIFIED
before Vigenere decryption is applied.

Categories tested:
1. Ciphertext Reversal
2. Ciphertext Rotation/Shift
3. Split and Interleave
4. Grid Transposition before Vigenere
5. Skip/Decimation (multiplicative permutation)
6. Crib-Anchored Transposition
7. K4 Read as a Matrix (padded grids)

Scoring via English quadgram log-probabilities.
"""

import math
import itertools
from collections import defaultdict

# ==============================================================================
# CONSTANTS
# ==============================================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
KNOWN_KEY = "OYNKYELYOIECBAQK?????RDUMRIYW"  # period 29, positions 0-28
KEY_PERIOD = 29
CT_LEN = len(K4)  # 97

# Known cribs and their plaintext positions
CRIB_BERLIN = ("BERLINCLOCK", 63)   # positions 63-73
CRIB_EAST   = ("EASTNORTHEAST", 21) # positions 21-33

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Scoring threshold to flag
FLAG_THRESHOLD = -500

# ==============================================================================
# QUADGRAM SCORING
# ==============================================================================

print("Loading quadgram data...")
QUADGRAMS = {}
QUADGRAM_TOTAL = 0

with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            QUADGRAM_TOTAL += count

LOG_TOTAL = math.log10(QUADGRAM_TOTAL)
QUADGRAM_FLOOR = math.log10(0.01) - LOG_TOTAL  # floor for unseen quadgrams

def quadgram_score(text):
    """Score text using log10 quadgram frequencies. Higher is better."""
    text = text.upper()
    # Only score alphabetic characters
    text = ''.join(c for c in text if c.isalpha() and c != '?')
    if len(text) < 4:
        return -9999.0
    score = 0.0
    for i in range(len(text) - 3):
        gram = text[i:i+4]
        if gram in QUADGRAMS:
            score += math.log10(QUADGRAMS[gram]) - LOG_TOTAL
        else:
            score += QUADGRAM_FLOOR
    return score

# ==============================================================================
# VIGENERE FUNCTIONS (KRYPTOS ALPHABET)
# ==============================================================================

def vigenere_decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Decrypt a single character using Vigenere with given alphabet."""
    ct_idx = alpha.index(ct_char)
    key_idx = alpha.index(key_char)
    return alpha[(ct_idx - key_idx) % len(alpha)]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt ciphertext with repeating key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            result.append(vigenere_decrypt_char(c, k, alpha))
    return ''.join(result)

def derive_key_char(ct_char, pt_char, alpha=KRYPTOS_ALPHA):
    """Given CT and PT chars, derive the key character."""
    ct_idx = alpha.index(ct_char)
    pt_idx = alpha.index(pt_char)
    return alpha[(ct_idx - pt_idx) % len(alpha)]

def derive_key_from_crib(ct, crib_text, crib_pos, period, alpha=KRYPTOS_ALPHA):
    """Derive key characters from a known crib at a known plaintext position."""
    key = ['?'] * period
    for i, p_char in enumerate(crib_text):
        ct_pos = crib_pos + i
        if ct_pos < len(ct):
            key_pos = ct_pos % period
            k = derive_key_char(ct[ct_pos], p_char, alpha)
            if key[key_pos] == '?':
                key[key_pos] = k
            elif key[key_pos] != k:
                return None  # Conflict
    return ''.join(key)

def merge_keys(key1, key2):
    """Merge two partial keys. Returns None on conflict."""
    if len(key1) != len(key2):
        return None
    result = []
    for a, b in zip(key1, key2):
        if a == '?' and b == '?':
            result.append('?')
        elif a == '?':
            result.append(b)
        elif b == '?':
            result.append(a)
        elif a == b:
            result.append(a)
        else:
            return None  # Conflict
    return ''.join(result)

def count_known(key):
    """Count non-'?' characters in key."""
    return sum(1 for c in key if c != '?')

# ==============================================================================
# RESULT TRACKING
# ==============================================================================

class ResultTracker:
    """Track top N results per category."""
    def __init__(self, n=5):
        self.n = n
        self.results = []

    def add(self, score, description, plaintext, key_info=""):
        self.results.append((score, description, plaintext, key_info))
        self.results.sort(key=lambda x: x[0], reverse=True)
        self.results = self.results[:self.n]

    def report(self, category_name):
        print(f"\n{'='*80}")
        print(f"TOP {self.n} RESULTS: {category_name}")
        print(f"{'='*80}")
        flagged = False
        for i, (score, desc, pt, key_info) in enumerate(self.results):
            flag = " *** FLAGGED ***" if score > FLAG_THRESHOLD else ""
            if score > FLAG_THRESHOLD:
                flagged = True
            print(f"\n  #{i+1}: Score = {score:.2f}{flag}")
            print(f"       Method: {desc}")
            print(f"       PT:  {pt[:80]}{'...' if len(pt)>80 else ''}")
            if key_info:
                print(f"       Key: {key_info}")
        if not self.results:
            print("  (no results)")
        return flagged

# ==============================================================================
# CATEGORY 1: CIPHERTEXT REVERSAL
# ==============================================================================

def test_reversal():
    print("\n" + "#"*80)
    print("# CATEGORY 1: CIPHERTEXT REVERSAL")
    print("#"*80)
    tracker = ResultTracker(5)

    # 1a. Reverse entire K4, then apply period-29 Vigenere with known key
    reversed_ct = K4[::-1]
    pt = vigenere_decrypt(reversed_ct, KNOWN_KEY)
    score = quadgram_score(pt)
    tracker.add(score, "Reversed CT + known partial key (period 29)", pt, KNOWN_KEY)
    print(f"\n  [1a] Reversed CT + known key: score={score:.2f}")
    print(f"       PT: {pt}")

    # 1b. Reverse K4 and derive new key from cribs at their ORIGINAL positions
    # If CT is reversed, cribs in plaintext are still at 63-73 and 21-33
    # but map to different CT characters
    key_b = derive_key_from_crib(reversed_ct, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
    key_e = derive_key_from_crib(reversed_ct, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
    if key_b and key_e:
        merged = merge_keys(key_b, key_e)
        if merged:
            pt = vigenere_decrypt(reversed_ct, merged)
            score = quadgram_score(pt)
            tracker.add(score, "Reversed CT + new key from cribs at original positions", pt, merged)
            print(f"\n  [1b] Reversed CT + new crib key: score={score:.2f}")
            print(f"       Key: {merged} (known: {count_known(merged)}/29)")
            print(f"       PT: {pt}")

    # 1c. Reverse K4, derive key with cribs at REVERSED positions
    # BERLINCLOCK at 63-73 -> in reversed text would start at 97-73-1=23
    # EASTNORTHEAST at 21-33 -> starts at 97-33-1=63
    rev_berlin_pos = CT_LEN - CRIB_BERLIN[1] - len(CRIB_BERLIN[0])
    rev_east_pos = CT_LEN - CRIB_EAST[1] - len(CRIB_EAST[0])
    key_rb = derive_key_from_crib(reversed_ct, CRIB_BERLIN[0], rev_berlin_pos, KEY_PERIOD)
    key_re = derive_key_from_crib(reversed_ct, CRIB_EAST[0], rev_east_pos, KEY_PERIOD)
    if key_rb and key_re:
        merged2 = merge_keys(key_rb, key_re)
        if merged2:
            pt = vigenere_decrypt(reversed_ct, merged2)
            score = quadgram_score(pt)
            tracker.add(score, "Reversed CT + cribs at mirrored positions", pt, merged2)
            print(f"\n  [1c] Reversed CT + mirrored crib positions: score={score:.2f}")
            print(f"       Key: {merged2} (known: {count_known(merged2)}/29)")
            print(f"       PT: {pt}")
        else:
            print(f"\n  [1c] Key conflict with mirrored crib positions")
    else:
        print(f"\n  [1c] Could not derive key from mirrored positions")

    # 1d. Read backwards letter by letter (same as reversed), try standard Vigenere too
    for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
        pt = vigenere_decrypt(reversed_ct, KNOWN_KEY, alpha)
        score = quadgram_score(pt)
        tracker.add(score, f"Reversed CT + known key ({alpha_name} alphabet)", pt, KNOWN_KEY)

    return tracker

# ==============================================================================
# CATEGORY 2: CIPHERTEXT ROTATION/SHIFT
# ==============================================================================

def test_rotation():
    print("\n" + "#"*80)
    print("# CATEGORY 2: CIPHERTEXT ROTATION/SHIFT")
    print("#"*80)
    tracker = ResultTracker(5)

    for n in range(1, CT_LEN):
        rotated = K4[n:] + K4[:n]

        # Try with known key
        pt = vigenere_decrypt(rotated, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Rotate CT by {n}, known partial key", pt, KNOWN_KEY)

        # Try deriving key from cribs at original positions
        key_b = derive_key_from_crib(rotated, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
        key_e = derive_key_from_crib(rotated, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
        if key_b and key_e:
            merged = merge_keys(key_b, key_e)
            if merged:
                pt2 = vigenere_decrypt(rotated, merged)
                score2 = quadgram_score(pt2)
                tracker.add(score2, f"Rotate CT by {n}, crib-derived key", pt2, merged)

    print(f"\n  Tested {CT_LEN-1} rotations with known key + crib-derived keys")
    return tracker

# ==============================================================================
# CATEGORY 3: SPLIT AND INTERLEAVE
# ==============================================================================

def test_split_interleave():
    print("\n" + "#"*80)
    print("# CATEGORY 3: SPLIT AND INTERLEAVE")
    print("#"*80)
    tracker = ResultTracker(5)

    # 3a. Split into 2 halves, interleave
    for split_point in range(1, CT_LEN):
        half1 = K4[:split_point]
        half2 = K4[split_point:]
        interleaved = []
        i, j = 0, 0
        while i < len(half1) or j < len(half2):
            if i < len(half1):
                interleaved.append(half1[i])
                i += 1
            if j < len(half2):
                interleaved.append(half2[j])
                j += 1
        text = ''.join(interleaved)

        # Try known key
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Split at {split_point}, interleave 2 halves, known key", pt, KNOWN_KEY)

        # Try crib-derived key
        key_b = derive_key_from_crib(text, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
        key_e = derive_key_from_crib(text, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
        if key_b and key_e:
            merged = merge_keys(key_b, key_e)
            if merged:
                pt2 = vigenere_decrypt(text, merged)
                score2 = quadgram_score(pt2)
                tracker.add(score2, f"Split at {split_point}, interleave, crib key", pt2, merged)

    print(f"  [3a] Tested {CT_LEN-1} split points for 2-way interleave")

    # 3b. Split into 3 parts, interleave
    for s1 in range(1, CT_LEN-1):
        for s2 in range(s1+1, CT_LEN):
            if (s2 - s1) > 40 or s1 > 40:
                continue  # Keep it manageable
            p1 = K4[:s1]
            p2 = K4[s1:s2]
            p3 = K4[s2:]
            interleaved = []
            i, j, k = 0, 0, 0
            while i < len(p1) or j < len(p2) or k < len(p3):
                if i < len(p1):
                    interleaved.append(p1[i]); i += 1
                if j < len(p2):
                    interleaved.append(p2[j]); j += 1
                if k < len(p3):
                    interleaved.append(p3[k]); k += 1
            text = ''.join(interleaved)
            pt = vigenere_decrypt(text, KNOWN_KEY)
            score = quadgram_score(pt)
            tracker.add(score, f"3-split at ({s1},{s2}), interleave, known key", pt, KNOWN_KEY)

    print(f"  [3b] Tested 3-part interleaves (limited range)")

    # 3c. Split at W positions
    w_positions = [20, 36, 48, 58, 74]
    for wp in w_positions:
        h1 = K4[:wp]
        h2 = K4[wp:]
        interleaved = []
        i, j = 0, 0
        while i < len(h1) or j < len(h2):
            if i < len(h1):
                interleaved.append(h1[i]); i += 1
            if j < len(h2):
                interleaved.append(h2[j]); j += 1
        text = ''.join(interleaved)
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Split at W-position {wp}, interleave, known key", pt, KNOWN_KEY)

        # Crib-derived
        key_b = derive_key_from_crib(text, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
        key_e = derive_key_from_crib(text, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
        if key_b and key_e:
            merged = merge_keys(key_b, key_e)
            if merged:
                pt2 = vigenere_decrypt(text, merged)
                score2 = quadgram_score(pt2)
                tracker.add(score2, f"Split at W-position {wp}, interleave, crib key", pt2, merged)

    print(f"  [3c] Tested W-position splits: {w_positions}")
    return tracker

# ==============================================================================
# CATEGORY 4: GRID TRANSPOSITION BEFORE VIGENERE
# ==============================================================================

def grid_read_columns(text, width):
    """Write text row-by-row into grid, read column-by-column."""
    rows = []
    for i in range(0, len(text), width):
        rows.append(text[i:i+width])
    result = []
    for col in range(width):
        for row in rows:
            if col < len(row):
                result.append(row[col])
    return ''.join(result)

def grid_read_reverse_columns(text, width):
    """Write row-by-row, read columns in reverse order."""
    rows = []
    for i in range(0, len(text), width):
        rows.append(text[i:i+width])
    result = []
    for col in range(width-1, -1, -1):
        for row in rows:
            if col < len(row):
                result.append(row[col])
    return ''.join(result)

def grid_read_zigzag(text, width):
    """Write row-by-row, read columns alternating direction (down, up, down, ...)."""
    rows = []
    for i in range(0, len(text), width):
        rows.append(text[i:i+width])
    num_rows = len(rows)
    result = []
    for col in range(width):
        if col % 2 == 0:
            for row in rows:
                if col < len(row):
                    result.append(row[col])
        else:
            for row in reversed(rows):
                if col < len(row):
                    result.append(row[col])
    return ''.join(result)

def grid_read_diagonal(text, width):
    """Write row-by-row, read diagonals (top-left to bottom-right)."""
    rows = []
    for i in range(0, len(text), width):
        rows.append(text[i:i+width])
    num_rows = len(rows)
    result = []
    # Diagonals starting from first row
    for start_col in range(width):
        r, c = 0, start_col
        while r < num_rows and c < width:
            if c < len(rows[r]):
                result.append(rows[r][c])
            r += 1
            c += 1
    # Diagonals starting from first column (skip 0,0 already done)
    for start_row in range(1, num_rows):
        r, c = start_row, 0
        while r < num_rows and c < width:
            if c < len(rows[r]):
                result.append(rows[r][c])
            r += 1
            c += 1
    return ''.join(result)

def grid_read_spiral(text, width):
    """Write row-by-row, read in spiral from top-left."""
    rows = []
    for i in range(0, len(text), width):
        rows.append(list(text[i:i+width]))
    # Pad last row if needed
    if rows and len(rows[-1]) < width:
        rows[-1].extend([''] * (width - len(rows[-1])))
    num_rows = len(rows)
    result = []
    top, bottom, left, right = 0, num_rows - 1, 0, width - 1
    while top <= bottom and left <= right:
        # Right across top
        for c in range(left, right + 1):
            if rows[top][c]:
                result.append(rows[top][c])
        top += 1
        # Down right side
        for r in range(top, bottom + 1):
            if c <= right and right < len(rows[r]) and rows[r][right]:
                result.append(rows[r][right])
        right -= 1
        # Left across bottom
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if rows[bottom][c]:
                    result.append(rows[bottom][c])
            bottom -= 1
        # Up left side
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if left < len(rows[r]) and rows[r][left]:
                    result.append(rows[r][left])
            left += 1
    return ''.join(result)

def test_grid_transposition():
    print("\n" + "#"*80)
    print("# CATEGORY 4: GRID TRANSPOSITION BEFORE VIGENERE")
    print("#"*80)
    tracker = ResultTracker(5)

    widths = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 29]
    read_methods = [
        ("columns", grid_read_columns),
        ("reverse-columns", grid_read_reverse_columns),
        ("zigzag", grid_read_zigzag),
        ("diagonal", grid_read_diagonal),
        ("spiral", grid_read_spiral),
    ]

    count = 0
    for w in widths:
        for method_name, method_fn in read_methods:
            rearranged = method_fn(K4, w)
            if len(rearranged) != CT_LEN:
                continue  # Skip if something went wrong

            # With known key
            pt = vigenere_decrypt(rearranged, KNOWN_KEY)
            score = quadgram_score(pt)
            tracker.add(score, f"Grid {w}-wide, {method_name}, known key", pt, KNOWN_KEY)

            # With crib-derived key
            key_b = derive_key_from_crib(rearranged, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
            key_e = derive_key_from_crib(rearranged, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
            if key_b and key_e:
                merged = merge_keys(key_b, key_e)
                if merged:
                    pt2 = vigenere_decrypt(rearranged, merged)
                    score2 = quadgram_score(pt2)
                    tracker.add(score2, f"Grid {w}-wide, {method_name}, crib key", pt2, merged)
            count += 1

    # Also try writing column-by-column and reading row-by-row (inverse)
    for w in widths:
        # The inverse of "write rows, read columns" is "write columns, read rows"
        # Which is equivalent to grid_read_columns with height as width
        num_rows = math.ceil(CT_LEN / w)
        inv = grid_read_columns(K4, num_rows)
        if len(inv) == CT_LEN:
            pt = vigenere_decrypt(inv, KNOWN_KEY)
            score = quadgram_score(pt)
            tracker.add(score, f"Grid {w}-wide INVERSE (cols->rows), known key", pt, KNOWN_KEY)
            count += 1

    print(f"  Tested {count} grid transpositions")
    return tracker

# ==============================================================================
# CATEGORY 5: SKIP/DECIMATION
# ==============================================================================

def test_decimation():
    print("\n" + "#"*80)
    print("# CATEGORY 5: SKIP/DECIMATION")
    print("#"*80)
    tracker = ResultTracker(5)

    # 97 is prime, so all m from 1..96 are coprime to 97
    # Permutation: position i -> position (i*m) mod 97

    count = 0
    for m in range(2, CT_LEN):
        # Read K4 at positions i*m mod 97 for i=0..96
        decimated = ''.join(K4[(i * m) % CT_LEN] for i in range(CT_LEN))

        # With known key
        pt = vigenere_decrypt(decimated, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Decimation m={m}, known key", pt, KNOWN_KEY)

        # With crib-derived key
        key_b = derive_key_from_crib(decimated, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
        key_e = derive_key_from_crib(decimated, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
        if key_b and key_e:
            merged = merge_keys(key_b, key_e)
            if merged:
                pt2 = vigenere_decrypt(decimated, merged)
                score2 = quadgram_score(pt2)
                tracker.add(score2, f"Decimation m={m}, crib key", pt2, merged)
        count += 1

    # Also test simple skip patterns: every Nth character (not mod 97)
    for skip in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        chars = []
        for start in range(skip):
            for i in range(start, CT_LEN, skip):
                chars.append(K4[i])
        text = ''.join(chars)
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Skip pattern every {skip}th char, known key", pt, KNOWN_KEY)
        count += 1

    print(f"  Tested {count} decimation/skip patterns")
    return tracker

# ==============================================================================
# CATEGORY 6: CRIB-ANCHORED TRANSPOSITION
# ==============================================================================

def test_crib_anchored():
    print("\n" + "#"*80)
    print("# CATEGORY 6: CRIB-ANCHORED TRANSPOSITION")
    print("#"*80)
    tracker = ResultTracker(5)

    # The cribs are at known positions in the plaintext.
    # If a transposition was applied to CT before Vigenere encryption,
    # we need to find permutations where the crib positions are FIXED.
    #
    # Crib positions that must be fixed: 21-33 (EASTNORTHEAST) and 63-73 (BERLINCLOCK)
    # That's 13 + 11 = 24 positions that must be identity-mapped.
    # The remaining 97 - 24 = 73 positions can be permuted.
    #
    # Testing all 73! permutations is impossible, so we test structured permutations:

    fixed_positions = set(range(21, 34)) | set(range(63, 74))
    free_positions = [i for i in range(CT_LEN) if i not in fixed_positions]

    count = 0

    # 6a. Reverse the free positions only
    perm = list(range(CT_LEN))
    rev_free = list(reversed(free_positions))
    for i, fp in enumerate(free_positions):
        perm[fp] = rev_free[i]
    rearranged = ''.join(K4[perm[i]] for i in range(CT_LEN))
    pt = vigenere_decrypt(rearranged, KNOWN_KEY)
    score = quadgram_score(pt)
    tracker.add(score, "Reverse free positions (cribs fixed), known key", pt, KNOWN_KEY)
    count += 1

    # 6b. Rotate free positions by N
    for n in range(1, len(free_positions)):
        rotated_free = free_positions[n:] + free_positions[:n]
        rearranged = list(K4)
        for i, fp in enumerate(free_positions):
            rearranged[fp] = K4[rotated_free[i]]
        text = ''.join(rearranged)
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Rotate free positions by {n} (cribs fixed), known key", pt, KNOWN_KEY)
        count += 1

    # 6c. Swap free positions in blocks
    # Split free positions into segments and rearrange segments
    num_free = len(free_positions)
    for block_size in [2, 3, 4, 5, 7, 10, 12]:
        if num_free < block_size * 2:
            continue
        blocks = []
        for i in range(0, num_free, block_size):
            blocks.append(free_positions[i:i+block_size])

        # Reverse block order
        rev_blocks = list(reversed(blocks))
        new_free = []
        for b in rev_blocks:
            new_free.extend(b)
        rearranged = list(K4)
        for i, fp in enumerate(free_positions):
            if i < len(new_free):
                rearranged[fp] = K4[new_free[i]]
        text = ''.join(rearranged)
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Reverse blocks of {block_size} in free positions, known key", pt, KNOWN_KEY)
        count += 1

    # 6d. Multiplicative permutation on free positions only
    for m in range(2, min(len(free_positions), 50)):
        if math.gcd(m, len(free_positions)) != 1:
            continue
        new_order = [free_positions[(i * m) % len(free_positions)] for i in range(len(free_positions))]
        rearranged = list(K4)
        for i, fp in enumerate(free_positions):
            rearranged[fp] = K4[new_order[i]]
        text = ''.join(rearranged)
        pt = vigenere_decrypt(text, KNOWN_KEY)
        score = quadgram_score(pt)
        tracker.add(score, f"Multiplicative perm m={m} on free positions, known key", pt, KNOWN_KEY)
        count += 1

    print(f"  Tested {count} crib-anchored transpositions")
    return tracker

# ==============================================================================
# CATEGORY 7: K4 READ AS A MATRIX (PADDED)
# ==============================================================================

def test_padded_matrix():
    print("\n" + "#"*80)
    print("# CATEGORY 7: K4 READ AS MATRIX (PADDED TO 98, 99, 100)")
    print("#"*80)
    tracker = ResultTracker(5)

    pad_configs = [
        (98, [(2, 49), (7, 14), (14, 7), (49, 2)]),
        (99, [(9, 11), (11, 9), (3, 33), (33, 3)]),
        (100, [(10, 10), (5, 20), (20, 5), (4, 25), (25, 4)]),
    ]

    count = 0
    for padded_len, grids in pad_configs:
        # Try padding at the end with different characters
        for pad_char in ['X', 'K', 'A', 'Z']:
            padded = K4 + pad_char * (padded_len - CT_LEN)

            for rows, cols in grids:
                # Write row-by-row, read column-by-column
                col_read = []
                for c in range(cols):
                    for r in range(rows):
                        idx = r * cols + c
                        if idx < len(padded):
                            col_read.append(padded[idx])
                text = ''.join(col_read)[:CT_LEN]  # Take only first 97

                pt = vigenere_decrypt(text, KNOWN_KEY)
                score = quadgram_score(pt)
                tracker.add(score, f"Pad to {padded_len}({pad_char}), {rows}x{cols} col-read, known key", pt, KNOWN_KEY)
                count += 1

                # Crib-derived key
                key_b = derive_key_from_crib(text, CRIB_BERLIN[0], CRIB_BERLIN[1], KEY_PERIOD)
                key_e = derive_key_from_crib(text, CRIB_EAST[0], CRIB_EAST[1], KEY_PERIOD)
                if key_b and key_e:
                    merged = merge_keys(key_b, key_e)
                    if merged:
                        pt2 = vigenere_decrypt(text, merged)
                        score2 = quadgram_score(pt2)
                        tracker.add(score2, f"Pad to {padded_len}({pad_char}), {rows}x{cols} col-read, crib key", pt2, merged)
                        count += 1

                # Write column-by-column, read row-by-row (inverse direction)
                row_read = []
                for r in range(rows):
                    for c in range(cols):
                        idx = c * rows + r
                        if idx < len(padded):
                            row_read.append(padded[idx])
                text2 = ''.join(row_read)[:CT_LEN]
                pt3 = vigenere_decrypt(text2, KNOWN_KEY)
                score3 = quadgram_score(pt3)
                tracker.add(score3, f"Pad to {padded_len}({pad_char}), {rows}x{cols} row-read, known key", pt3, KNOWN_KEY)
                count += 1

                # Spiral read
                # Write into rows x cols grid row-by-row
                grid = []
                for r_idx in range(rows):
                    row = []
                    for c_idx in range(cols):
                        pos = r_idx * cols + c_idx
                        if pos < len(padded):
                            row.append(padded[pos])
                        else:
                            row.append('')
                    grid.append(row)

                # Spiral read from top-left
                spiral = []
                t, b, l, ri = 0, rows - 1, 0, cols - 1
                while t <= b and l <= ri:
                    for c_idx in range(l, ri + 1):
                        if grid[t][c_idx]:
                            spiral.append(grid[t][c_idx])
                    t += 1
                    for r_idx in range(t, b + 1):
                        if grid[r_idx][ri]:
                            spiral.append(grid[r_idx][ri])
                    ri -= 1
                    if t <= b:
                        for c_idx in range(ri, l - 1, -1):
                            if grid[b][c_idx]:
                                spiral.append(grid[b][c_idx])
                        b -= 1
                    if l <= ri:
                        for r_idx in range(b, t - 1, -1):
                            if grid[r_idx][l]:
                                spiral.append(grid[r_idx][l])
                        l += 1

                text_sp = ''.join(spiral)[:CT_LEN]
                pt_sp = vigenere_decrypt(text_sp, KNOWN_KEY)
                score_sp = quadgram_score(pt_sp)
                tracker.add(score_sp, f"Pad to {padded_len}({pad_char}), {rows}x{cols} spiral, known key", pt_sp, KNOWN_KEY)
                count += 1

    print(f"  Tested {count} padded matrix configurations")
    return tracker

# ==============================================================================
# BASELINE REFERENCE
# ==============================================================================

def baseline():
    print("\n" + "#"*80)
    print("# BASELINE: Original K4 with known key (no manipulation)")
    print("#"*80)

    pt = vigenere_decrypt(K4, KNOWN_KEY)
    score = quadgram_score(pt)
    print(f"\n  Original K4 + known partial key:")
    print(f"  PT:    {pt}")
    print(f"  Score: {score:.2f}")
    print(f"  Key:   {KNOWN_KEY}")
    return score

# ==============================================================================
# MAIN
# ==============================================================================

def main():
    print("=" * 80)
    print("K4 CIPHERTEXT MANIPULATION ANALYSIS")
    print("=" * 80)
    print(f"\nK4 ({CT_LEN} chars): {K4}")
    print(f"KRYPTOS alphabet:  {KRYPTOS_ALPHA}")
    print(f"Known key:         {KNOWN_KEY}")
    print(f"Key period:        {KEY_PERIOD}")
    print(f"Crib 1: '{CRIB_EAST[0]}' at positions {CRIB_EAST[1]}-{CRIB_EAST[1]+len(CRIB_EAST[0])-1}")
    print(f"Crib 2: '{CRIB_BERLIN[0]}' at positions {CRIB_BERLIN[1]}-{CRIB_BERLIN[1]+len(CRIB_BERLIN[0])-1}")
    print(f"Flag threshold:    {FLAG_THRESHOLD}")

    baseline_score = baseline()

    all_flagged = []

    # Run all categories
    categories = [
        ("1. CIPHERTEXT REVERSAL", test_reversal),
        ("2. CIPHERTEXT ROTATION/SHIFT", test_rotation),
        ("3. SPLIT AND INTERLEAVE", test_split_interleave),
        ("4. GRID TRANSPOSITION", test_grid_transposition),
        ("5. SKIP/DECIMATION", test_decimation),
        ("6. CRIB-ANCHORED TRANSPOSITION", test_crib_anchored),
        ("7. PADDED MATRIX", test_padded_matrix),
    ]

    trackers = []
    for name, fn in categories:
        tracker = fn()
        flagged = tracker.report(name)
        trackers.append((name, tracker, flagged))
        if flagged:
            all_flagged.append(name)

    # ==============================================================================
    # GRAND SUMMARY
    # ==============================================================================
    print("\n" + "=" * 80)
    print("GRAND SUMMARY")
    print("=" * 80)
    print(f"\nBaseline score (no manipulation): {baseline_score:.2f}")
    print(f"Flag threshold: {FLAG_THRESHOLD}")

    # Collect all results, find global top 10
    all_results = []
    for name, tracker, _ in trackers:
        for r in tracker.results:
            all_results.append((r[0], name, r[1], r[2], r[3]))
    all_results.sort(key=lambda x: x[0], reverse=True)

    print(f"\n--- GLOBAL TOP 10 ---")
    for i, (score, cat, desc, pt, key_info) in enumerate(all_results[:10]):
        flag = " *** FLAGGED ***" if score > FLAG_THRESHOLD else ""
        better = " (BETTER THAN BASELINE)" if score > baseline_score else ""
        print(f"\n  #{i+1}: Score = {score:.2f}{flag}{better}")
        print(f"       Category: {cat}")
        print(f"       Method:   {desc}")
        print(f"       PT: {pt[:80]}{'...' if len(pt)>80 else ''}")
        if key_info:
            print(f"       Key: {key_info}")

    if all_flagged:
        print(f"\n*** CATEGORIES WITH FLAGGED RESULTS (score > {FLAG_THRESHOLD}): ***")
        for name in all_flagged:
            print(f"  - {name}")
    else:
        print(f"\nNo results exceeded the flag threshold of {FLAG_THRESHOLD}.")
        print("All manipulated ciphertexts scored poorly, suggesting:")
        print("  - K4 ciphertext is likely NOT transposed before Vigenere encryption")
        print("  - OR the transposition pattern was not among those tested")
        print("  - OR a different cipher entirely is layered on top")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
