#!/usr/bin/env python3
"""
K4 Two-Step Cipher Hypothesis Tester
=====================================
Tests whether K4 uses:
  (A) Vigenere THEN columnar transposition
  (B) Columnar transposition THEN Vigenere
  (C) Rail fence + Vigenere combinations
  (D) Route cipher + Vigenere combinations

Known constraints:
  - K4 ciphertext: 97 characters
  - BERLINCLOCK at position 63 in final plaintext
  - NORTHEAST at position 16 in final plaintext
  - KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ

Uses crib-based pruning to massively reduce search space.
"""

import itertools
import math
import sys
from collections import Counter

# ─── Constants ────────────────────────────────────────────────────────────────

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4)  # 97

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known cribs
CRIB_BERLIN = ("BERLINCLOCK", 63)   # plaintext, position in final plaintext
CRIB_NORTHEAST = ("NORTHEAST", 16)

# Candidate Vigenere keys
VIG_KEYS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
    "BERLINCLOCK", "NORTHEAST", "SANBORN", "CIA", "NSA",
    "SHADOW", "LUCID", "SECRET", "ENIGMA", "CRYPTO",
    "KEY", "KOMITET", "DYAHR", "DIGETAL", "INTERPRETIV",
    "QUAGMIRE", "PORTA", "BEAUFORT",
]

# ─── Utility Functions ───────────────────────────────────────────────────────

def vigenere_encrypt(pt, key, alpha=KRYPTOS_ALPHA):
    """Encrypt plaintext with Vigenere using given alphabet."""
    result = []
    ki = 0
    for c in pt:
        if c in alpha:
            ci = (alpha.index(c) + alpha.index(key[ki % len(key)])) % len(alpha)
            result.append(alpha[ci])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt ciphertext with Vigenere using given alphabet."""
    result = []
    ki = 0
    for c in ct:
        if c in alpha:
            pi = (alpha.index(c) - alpha.index(key[ki % len(key)])) % len(alpha)
            result.append(alpha[pi])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)


def columnar_transpose(text, key_order):
    """
    Apply columnar transposition.
    key_order is a list like [2,0,3,1] meaning column 0 is read 3rd, etc.
    We write text row-by-row into a grid, then read columns in key_order.
    """
    ncols = len(key_order)
    nrows = math.ceil(len(text) / ncols)

    # Pad text to fill grid (we'll track actual length)
    padded = text + '\x00' * (nrows * ncols - len(text))

    # Write into grid row by row
    grid = []
    for r in range(nrows):
        grid.append(list(padded[r * ncols:(r + 1) * ncols]))

    # Read columns in key_order sequence
    result = []
    for col_rank in range(ncols):
        # Find which column has this rank
        col_idx = key_order.index(col_rank)
        for r in range(nrows):
            ch = grid[r][col_idx]
            if ch != '\x00':
                result.append(ch)

    return ''.join(result)


def columnar_untranspose(ct, key_order):
    """
    Reverse columnar transposition.
    key_order[i] = rank of column i (0 = read first).
    """
    ncols = len(key_order)
    nrows = math.ceil(len(ct) / ncols)
    n_full = len(ct) - ncols * (nrows - 1)  # number of full-length columns
    # Actually: total cells = nrows * ncols, but we only have len(ct) chars
    # So (nrows*ncols - len(ct)) columns are short (length nrows-1)
    n_short = nrows * ncols - len(ct)

    # Determine length of each column when read in key_order
    # Column read at rank r: if the ORIGINAL column index corresponding to rank r
    # is among the "short" ones. Short columns are the LAST n_short columns (rightmost).
    col_lengths = {}
    for col_idx in range(ncols):
        # The last n_short column positions (by index) have nrows-1 entries
        if col_idx >= ncols - n_short:
            col_lengths[col_idx] = nrows - 1
        else:
            col_lengths[col_idx] = nrows

    # Read text into columns in key_order sequence
    columns = {}
    pos = 0
    for rank in range(ncols):
        col_idx = key_order.index(rank)
        clen = col_lengths[col_idx]
        columns[col_idx] = ct[pos:pos + clen]
        pos += clen

    # Reconstruct by reading row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if r < len(columns[c]):
                result.append(columns[c][r])

    return ''.join(result)


def rail_fence_encrypt(text, rails):
    """Encrypt with rail fence cipher."""
    if rails <= 1:
        return text
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for ch in text:
        fence[rail].append(ch)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return ''.join(''.join(row) for row in fence)


def rail_fence_decrypt(ct, rails):
    """Decrypt rail fence cipher."""
    if rails <= 1:
        return ct
    n = len(ct)
    # Figure out lengths of each rail
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    pattern = []
    for i in range(n):
        pattern.append(rail)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction

    # Count chars per rail
    rail_counts = Counter(pattern)

    # Split ciphertext into rails
    pos = 0
    rail_chars = {}
    for r in range(rails):
        rail_chars[r] = list(ct[pos:pos + rail_counts[r]])
        pos += rail_counts[r]

    # Read back in zigzag order
    rail_indices = {r: 0 for r in range(rails)}
    result = []
    for r in pattern:
        result.append(rail_chars[r][rail_indices[r]])
        rail_indices[r] += 1

    return ''.join(result)


def score_english(text):
    """Score text based on English quadgram frequencies. Higher = more English-like."""
    global QUADGRAMS
    score = 0.0
    for i in range(len(text) - 3):
        quad = text[i:i+4]
        score += QUADGRAMS.get(quad, FLOOR_SCORE)
    return score


def contains_crib(text, crib, position):
    """Check if text contains crib at the specified position."""
    if position + len(crib) > len(text):
        return False
    return text[position:position + len(crib)] == crib


def check_both_cribs(text):
    """Check if text contains both known cribs at their positions."""
    has_berlin = contains_crib(text, CRIB_BERLIN[0], CRIB_BERLIN[1])
    has_northeast = contains_crib(text, CRIB_NORTHEAST[0], CRIB_NORTHEAST[1])
    return has_berlin, has_northeast


def find_english_words(text, min_len=4):
    """Find English words in text."""
    found = []
    for w in ENGLISH_WORDS:
        if len(w) >= min_len and w in text:
            pos = text.find(w)
            found.append((w, pos))
    return found


# ─── Load Resources ──────────────────────────────────────────────────────────

print("Loading resources...")

# Load quadgrams
QUADGRAMS = {}
try:
    with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                QUADGRAMS[parts[0]] = math.log10(int(parts[1]))
    total = math.log10(sum(10**v for v in QUADGRAMS.values()))
    FLOOR_SCORE = math.log10(0.01) - total  # penalty for unknown quadgrams
except FileNotFoundError:
    print("WARNING: Quadgram file not found. English scoring disabled.")
    QUADGRAMS = {}
    FLOOR_SCORE = -10

# Load word list
ENGLISH_WORDS = set()
try:
    with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 4:
                ENGLISH_WORDS.add(w)
except FileNotFoundError:
    print("WARNING: Word list not found.")

print(f"Loaded {len(QUADGRAMS)} quadgrams, {len(ENGLISH_WORDS)} words")
print(f"K4 length: {K4_LEN}")
print()

# ─── Transposition Position Mapping ──────────────────────────────────────────

def get_transposition_mapping(key_order, text_len):
    """
    For a columnar transposition with given key_order applied to text of text_len,
    return mapping: output_pos -> input_pos
    i.e., output[output_pos] = input[input_pos]
    """
    ncols = len(key_order)
    nrows = math.ceil(text_len / ncols)
    n_short = nrows * ncols - text_len

    # Determine column lengths
    col_lengths = {}
    for col_idx in range(ncols):
        if col_idx >= ncols - n_short:
            col_lengths[col_idx] = nrows - 1
        else:
            col_lengths[col_idx] = nrows

    # Build mapping: when we READ columns in key_order, output position maps to grid position
    out_pos = 0
    mapping = {}  # out_pos -> input_pos (row-by-row position in grid)
    for rank in range(ncols):
        col_idx = key_order.index(rank)
        for row in range(col_lengths[col_idx]):
            input_pos = row * ncols + col_idx
            # But input_pos might exceed text_len in padded positions
            if input_pos < text_len:
                mapping[out_pos] = input_pos
                out_pos += 1

    return mapping


def get_inverse_mapping(key_order, text_len):
    """
    For UNDOING a columnar transposition: given ciphertext positions,
    return mapping: original_plaintext_pos -> ciphertext_pos

    If CT was produced by columnar_transpose(PT, key_order),
    then to get PT back: PT[input_pos] = CT[output_pos]
    So we need: for each plaintext position, which CT position provides it.
    """
    fwd = get_transposition_mapping(key_order, text_len)
    # fwd: ct_pos -> pt_pos  (output[ct_pos] came from input[pt_pos])
    inv = {}
    for ct_pos, pt_pos in fwd.items():
        inv[pt_pos] = ct_pos
    return inv


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 1: Vigenere THEN Transposition
# Plain -> Vig encrypt -> Columnar transpose -> K4
# To decode: K4 -> Un-transpose -> Vig decrypt -> Plain
# ═════════════════════════════════════════════════════════════════════════════

print("=" * 78)
print("APPROACH 1: Vigenere THEN Columnar Transposition")
print("  Encryption: Plain -> Vig(key) -> ColTranspose -> K4")
print("  Decryption: K4 -> Un-transpose -> Vig_decrypt(key) -> Plain")
print("=" * 78)

def test_approach1():
    """
    For this approach, after un-transposing K4, then Vig-decrypting,
    we need BERLINCLOCK at pos 63 and NORTHEAST at pos 16.

    Strategy: for each Vig key, for each transposition key length,
    use the crib constraints to determine which column orderings are possible.
    """
    results = []
    best_score = -float('inf')

    for vig_key in VIG_KEYS:
        for ncols in range(2, 16):
            nrows = math.ceil(K4_LEN / ncols)
            n_short = nrows * ncols - K4_LEN

            # For small ncols, enumerate all permutations
            if ncols <= 8:
                # Use crib-based pruning
                # After un-transposition and vig-decrypt, position 63..73 = BERLINCLOCK
                # After un-transposition, position 63..73 must vig-decrypt to BERLINCLOCK
                # So un-transposed[63+j] must be vig_encrypt(BERLINCLOCK[j], vig_key[(63+j) % len(vig_key)])

                # What the intermediate (after Vig encrypt, before transpose) text must have at positions 63-73:
                expected_intermediate = ""
                for j, ch in enumerate("BERLINCLOCK"):
                    pos = 63 + j
                    ki = pos % len(vig_key)
                    # Vig encrypt: intermediate = alpha[(pt + key) % 26]
                    ci = (KRYPTOS_ALPHA.index(ch) + KRYPTOS_ALPHA.index(vig_key[ki])) % 26
                    expected_intermediate += KRYPTOS_ALPHA[ci]

                # Also for NORTHEAST at position 16-24:
                expected_ne_intermediate = ""
                for j, ch in enumerate("NORTHEAST"):
                    pos = 16 + j
                    ki = pos % len(vig_key)
                    ci = (KRYPTOS_ALPHA.index(ch) + KRYPTOS_ALPHA.index(vig_key[ki])) % 26
                    expected_ne_intermediate += KRYPTOS_ALPHA[ci]

                # Now, un-transpose(K4) must produce these at positions 63-73 and 16-24
                # For columnar_untranspose(K4, key_order)[pos] = expected
                # This means: in K4 (the transposed text), the character that ends up
                # at position pos after un-transposition must match.

                # The untranspose mapping: for each key_order, pt_pos -> ct_pos
                # means un_transposed[pt_pos] = K4[ct_pos]
                # So K4[ct_pos] must equal expected_intermediate[j] for each crib position

                # We can prune: for a given key_order, compute where positions 63-73
                # and 16-24 map FROM in K4, and check character matches.

                n_perms = math.factorial(ncols)
                if n_perms > 100000:
                    continue  # Skip if too many permutations (ncols=9 would be 362880)

                for perm in itertools.permutations(range(ncols)):
                    key_order = list(perm)

                    # Get the inverse mapping: pt_pos -> ct_pos
                    inv_map = get_inverse_mapping(key_order, K4_LEN)

                    # Check BERLINCLOCK crib
                    match = True
                    for j in range(len("BERLINCLOCK")):
                        pt_pos = 63 + j
                        if pt_pos not in inv_map:
                            match = False
                            break
                        ct_pos = inv_map[pt_pos]
                        if ct_pos >= K4_LEN:
                            match = False
                            break
                        if K4[ct_pos] != expected_intermediate[j]:
                            match = False
                            break

                    if not match:
                        continue

                    # Check NORTHEAST crib
                    for j in range(len("NORTHEAST")):
                        pt_pos = 16 + j
                        if pt_pos not in inv_map:
                            match = False
                            break
                        ct_pos = inv_map[pt_pos]
                        if ct_pos >= K4_LEN:
                            match = False
                            break
                        if K4[ct_pos] != expected_ne_intermediate[j]:
                            match = False
                            break

                    if not match:
                        continue

                    # Both cribs match! Full decrypt.
                    untransposed = columnar_untranspose(K4, key_order)
                    plaintext = vigenere_decrypt(untransposed, vig_key)

                    has_b, has_n = check_both_cribs(plaintext)
                    sc = score_english(plaintext)

                    if has_b and has_n:
                        words = find_english_words(plaintext, min_len=5)
                        print(f"\n*** BOTH CRIBS MATCH! ***")
                        print(f"  Vig key: {vig_key}, Transp cols: {ncols}, order: {key_order}")
                        print(f"  Plaintext: {plaintext}")
                        print(f"  English score: {sc:.2f}")
                        if words:
                            print(f"  English words found: {words}")
                        results.append((sc, plaintext, vig_key, key_order))

                    if sc > best_score:
                        best_score = sc
                        if sc > -6.0 * (K4_LEN - 3):  # reasonable English threshold
                            words = find_english_words(plaintext, min_len=5)
                            if words:
                                print(f"\n  High-scoring result (score={sc:.2f}):")
                                print(f"  Vig key: {vig_key}, cols: {ncols}, order: {key_order}")
                                print(f"  Plaintext: {plaintext}")
                                print(f"  Words: {words}")
                                results.append((sc, plaintext, vig_key, key_order))

            # For larger ncols (9-15), we can't enumerate all permutations
            # Instead, use crib constraints to directly determine required column positions
            elif ncols <= 15:
                # For each crib position, figure out which column it must come from
                # This creates constraints on the key_order
                # We use BERLINCLOCK (11 chars at pos 63-73) as primary constraint

                # The intermediate text at pos p was written to row r=p//ncols, col c=p%ncols
                # After transposition with key_order, it gets read out at some position in CT
                # We need: the CT char at the mapped position == expected_intermediate char

                expected_intermediate = ""
                for j, ch in enumerate("BERLINCLOCK"):
                    pos = 63 + j
                    ki = pos % len(vig_key)
                    ci = (KRYPTOS_ALPHA.index(ch) + KRYPTOS_ALPHA.index(vig_key[ki])) % 26
                    expected_intermediate += KRYPTOS_ALPHA[ci]

                expected_ne_intermediate = ""
                for j, ch in enumerate("NORTHEAST"):
                    pos = 16 + j
                    ki = pos % len(vig_key)
                    ci = (KRYPTOS_ALPHA.index(ch) + KRYPTOS_ALPHA.index(vig_key[ki])) % 26
                    expected_ne_intermediate += KRYPTOS_ALPHA[ci]

                # We can't efficiently enumerate, so skip very large ncols for now
                # (The crib pruning for approach 1 with ncols<=8 is the main test)
                pass

    return results


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 2: Transposition THEN Vigenere
# Plain -> ColTranspose -> Vig encrypt -> K4
# To decode: K4 -> Vig decrypt -> Un-transpose -> Plain
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("APPROACH 2: Columnar Transposition THEN Vigenere")
print("  Encryption: Plain -> ColTranspose -> Vig(key) -> K4")
print("  Decryption: K4 -> Vig_decrypt(key) -> Un-transpose -> Plain")
print("=" * 78)

def test_approach2():
    """
    Decrypt: first Vig-decrypt K4 to get intermediate, then un-transpose.

    Key insight: After Vig-decrypt and un-transpose, positions 63-73 = BERLINCLOCK.
    The un-transposition rearranges positions, so:
    un_transposed[63+j] = intermediate[source_pos] where source_pos depends on key_order.
    And intermediate[i] = vig_decrypt(K4[i], key).

    Since we know the Vig key, we can compute the full intermediate text.
    Then we just need to find a transposition that places BERLINCLOCK at pos 63.
    """
    results = []
    best_score = -float('inf')

    for vig_key in VIG_KEYS:
        # First, Vig-decrypt K4 with this key
        intermediate = vigenere_decrypt(K4, vig_key)

        # Also try with standard alphabet
        for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
            inter = vigenere_decrypt(K4, vig_key, alpha)

            for ncols in range(2, 16):
                nrows = math.ceil(K4_LEN / ncols)
                n_short = nrows * ncols - K4_LEN

                # After un-transposing inter with key_order, we need:
                # result[63+j] = BERLINCLOCK[j]  and  result[16+j] = NORTHEAST[j]
                #
                # un_transposed[pt_pos] = inter[ct_pos] where ct_pos = inv_map[pt_pos]
                # So inter[inv_map[63+j]] = BERLINCLOCK[j]
                # Meaning: in the intermediate text, the positions that map to 63-73
                # after un-transposition must contain B,E,R,L,I,N,C,L,O,C,K

                # For each permutation, check if inter contains the right chars at right positions

                if ncols <= 8:
                    n_perms = math.factorial(ncols)
                    if n_perms > 100000:
                        continue

                    for perm in itertools.permutations(range(ncols)):
                        key_order = list(perm)
                        inv_map = get_inverse_mapping(key_order, K4_LEN)

                        # Check BERLINCLOCK
                        match = True
                        for j, ch in enumerate("BERLINCLOCK"):
                            pt_pos = 63 + j
                            if pt_pos not in inv_map:
                                match = False
                                break
                            ct_pos = inv_map[pt_pos]
                            if inter[ct_pos] != ch:
                                match = False
                                break

                        if not match:
                            continue

                        # Check NORTHEAST
                        for j, ch in enumerate("NORTHEAST"):
                            pt_pos = 16 + j
                            if pt_pos not in inv_map:
                                match = False
                                break
                            ct_pos = inv_map[pt_pos]
                            if inter[ct_pos] != ch:
                                match = False
                                break

                        if not match:
                            continue

                        # Both cribs match!
                        plaintext = columnar_untranspose(inter, key_order)

                        has_b, has_n = check_both_cribs(plaintext)
                        sc = score_english(plaintext)

                        if has_b and has_n:
                            words = find_english_words(plaintext, min_len=5)
                            print(f"\n*** BOTH CRIBS MATCH! ***")
                            print(f"  Vig key: {vig_key} ({alpha_name}), Transp cols: {ncols}, order: {key_order}")
                            print(f"  Plaintext: {plaintext}")
                            print(f"  English score: {sc:.2f}")
                            if words:
                                print(f"  English words found: {words}")
                            results.append((sc, plaintext, vig_key, key_order, "approach2"))

                        if sc > best_score:
                            best_score = sc
                            if sc > -6.0 * (K4_LEN - 3):
                                words = find_english_words(plaintext, min_len=5)
                                if words:
                                    print(f"\n  High-scoring ({alpha_name}, score={sc:.2f}):")
                                    print(f"  Vig key: {vig_key}, cols: {ncols}, order: {key_order}")
                                    print(f"  Plaintext: {plaintext}")
                                    print(f"  Words: {words}")
                                    results.append((sc, plaintext, vig_key, key_order, "approach2"))

                # For larger ncols: use partial constraint solving
                elif ncols <= 12:
                    # For ncols 9-12, we use a smarter approach:
                    # Determine which columns specific plaintext positions fall in,
                    # and what characters must be there, then build partial key_order
                    # constraints and enumerate only valid completions.

                    # For position p in plaintext (row-major), it's at row p//ncols, col p%ncols
                    # After untransposition, we need inter[source] = expected_char
                    # where source is determined by the column ordering.

                    # Let's determine constraints from BERLINCLOCK
                    constraints = {}  # col_idx -> list of (row, expected_char_from_inter)

                    # For BERLINCLOCK at positions 63-73:
                    berlin_constraints = []
                    for j, ch in enumerate("BERLINCLOCK"):
                        pt_pos = 63 + j
                        row = pt_pos // ncols
                        col = pt_pos % ncols
                        berlin_constraints.append((col, row, ch))

                    # For NORTHEAST at positions 16-24:
                    ne_constraints = []
                    for j, ch in enumerate("NORTHEAST"):
                        pt_pos = 16 + j
                        row = pt_pos // ncols
                        col = pt_pos % ncols
                        ne_constraints.append((col, row, ch))

                    # For a given key_order, un-transposing means:
                    # The intermediate text is split into columns read in key_order order.
                    # To find what inter[source_pos] maps to plaintext[pt_pos]:
                    # pt_pos is at (row, col) in the grid
                    # The character at (row, col) in the grid comes from the col-th column
                    # of the intermediate, which was read at position rank=key_order[col].
                    #
                    # So we need: for each (col, row, expected_char), when we read
                    # column col at its key_order rank, the row-th element must be expected_char.

                    # The col-th column starts at some offset in inter determined by
                    # how many columns with lower rank come before it.
                    # offset = sum of lengths of columns with rank < key_order[col]

                    # Column lengths depend on which columns are "short":
                    col_lengths = {}
                    for c in range(ncols):
                        if c >= ncols - n_short:
                            col_lengths[c] = nrows - 1
                        else:
                            col_lengths[c] = nrows

                    # For each possible ordering, we'd check constraints.
                    # But with ncols=9..12, factorial is too large.
                    #
                    # Alternative: determine, for each column needed by a crib position,
                    # what characters from inter must appear. Build a mapping from
                    # column index -> required characters at specific rows.
                    # Then check which assignments of ranks satisfy these.

                    # For efficiency, we check char-by-char:
                    # un_transposed[pt_pos] where pt_pos = row*ncols + col
                    # This character comes from inter at position:
                    #   offset_of_col_in_inter + row
                    # where offset_of_col_in_inter = sum of col_lengths[c'] for all c'
                    # with key_order[c'] < key_order[col]

                    # This is still combinatorial. Let's use a backtracking approach
                    # with constraint propagation.

                    all_constraints = berlin_constraints + ne_constraints

                    # Group constraints by column
                    col_constraints = {}  # col_idx -> [(row, expected_char)]
                    for col, row, ch in all_constraints:
                        if col not in col_constraints:
                            col_constraints[col] = []
                        col_constraints[col].append((row, ch))

                    # For each column that has constraints, determine which ranks are possible
                    # Given a rank for column c, the offset is sum of col_lengths of columns
                    # with rank < this_rank. But we don't know other columns' ranks yet.
                    #
                    # However, we can enumerate: if column c gets rank r,
                    # then the offset depends on how many full and short columns have rank < r.
                    # Let's precompute possible offsets.

                    # Since columns with lower rank are read first from inter:
                    # If col c has rank r, its offset in inter = sum of lengths of the r columns
                    # that come before it (ranks 0..r-1).
                    # These columns could be full (nrows) or short (nrows-1).

                    # This is complex. For ncols 9-12, let's just use hill-climbing
                    # or random sampling instead of full enumeration.

                    import random
                    random.seed(42)

                    n_samples = 50000
                    for _ in range(n_samples):
                        key_order = list(range(ncols))
                        random.shuffle(key_order)

                        inv_map = get_inverse_mapping(key_order, K4_LEN)

                        # Quick check on first 3 chars of BERLINCLOCK
                        match = True
                        for j in range(min(3, len("BERLINCLOCK"))):
                            pt_pos = 63 + j
                            if pt_pos not in inv_map:
                                match = False
                                break
                            ct_pos = inv_map[pt_pos]
                            if inter[ct_pos] != "BERLINCLOCK"[j]:
                                match = False
                                break

                        if not match:
                            continue

                        # Full BERLINCLOCK check
                        for j in range(3, len("BERLINCLOCK")):
                            pt_pos = 63 + j
                            if pt_pos not in inv_map:
                                match = False
                                break
                            ct_pos = inv_map[pt_pos]
                            if inter[ct_pos] != "BERLINCLOCK"[j]:
                                match = False
                                break

                        if not match:
                            continue

                        # NORTHEAST check
                        for j, ch in enumerate("NORTHEAST"):
                            pt_pos = 16 + j
                            if pt_pos not in inv_map:
                                match = False
                                break
                            ct_pos = inv_map[pt_pos]
                            if inter[ct_pos] != ch:
                                match = False
                                break

                        if not match:
                            continue

                        plaintext = columnar_untranspose(inter, key_order)
                        has_b, has_n = check_both_cribs(plaintext)
                        sc = score_english(plaintext)

                        if has_b and has_n:
                            words = find_english_words(plaintext, min_len=5)
                            print(f"\n*** BOTH CRIBS MATCH (sampled)! ***")
                            print(f"  Vig key: {vig_key} ({alpha_name}), cols: {ncols}, order: {key_order}")
                            print(f"  Plaintext: {plaintext}")
                            print(f"  Score: {sc:.2f}")
                            if words:
                                print(f"  Words: {words}")
                            results.append((sc, plaintext, vig_key, key_order, "approach2-sampled"))

    return results


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 3: Rail Fence + Vigenere
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("APPROACH 3: Rail Fence + Vigenere Combinations")
print("=" * 78)

def test_approach3():
    """Test rail fence cipher combined with Vigenere in both orders."""
    results = []

    for rails in range(2, 11):
        for vig_key in VIG_KEYS:
            for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
                # Order A: Vig then Rail fence (decrypt: un-rail then vig-decrypt)
                un_railed = rail_fence_decrypt(K4, rails)
                pt_a = vigenere_decrypt(un_railed, vig_key, alpha)

                has_b, has_n = check_both_cribs(pt_a)
                if has_b or has_n:
                    sc = score_english(pt_a)
                    words = find_english_words(pt_a, min_len=5)
                    which = []
                    if has_b: which.append("BERLINCLOCK@63")
                    if has_n: which.append("NORTHEAST@16")
                    print(f"\n  Rail({rails}) then Vig({vig_key},{alpha_name}): cribs={which}")
                    print(f"  Plaintext: {pt_a}")
                    print(f"  Score: {sc:.2f}, Words: {words}")
                    results.append((sc, pt_a, f"rail{rails}+vig_{vig_key}", "A"))

                # Order B: Rail fence then Vig (decrypt: vig-decrypt then un-rail)
                vig_decrypted = vigenere_decrypt(K4, vig_key, alpha)
                pt_b = rail_fence_decrypt(vig_decrypted, rails)

                has_b, has_n = check_both_cribs(pt_b)
                if has_b or has_n:
                    sc = score_english(pt_b)
                    words = find_english_words(pt_b, min_len=5)
                    which = []
                    if has_b: which.append("BERLINCLOCK@63")
                    if has_n: which.append("NORTHEAST@16")
                    print(f"\n  Vig({vig_key},{alpha_name}) then Rail({rails}): cribs={which}")
                    print(f"  Plaintext: {pt_b}")
                    print(f"  Score: {sc:.2f}, Words: {words}")
                    results.append((sc, pt_b, f"vig_{vig_key}+rail{rails}", "B"))

    return results


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 4: Route Cipher + Vigenere
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("APPROACH 4: Route Cipher + Vigenere Combinations")
print("=" * 78)

def route_spiral_read(text, nrows, ncols):
    """Read text written into grid in spiral order (clockwise, starting top-left)."""
    if nrows * ncols < len(text):
        return None

    # Write into grid row by row
    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        grid[i // ncols][i % ncols] = ch

    # Read in spiral order
    result = []
    top, bottom, left, right = 0, nrows - 1, 0, ncols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            if grid[top][c] != '\x00':
                result.append(grid[top][c])
        top += 1
        for r in range(top, bottom + 1):
            if grid[r][right] != '\x00':
                result.append(grid[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                if grid[bottom][c] != '\x00':
                    result.append(grid[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                if grid[r][left] != '\x00':
                    result.append(grid[r][left])
            left += 1

    return ''.join(result[:len(text)])


def route_spiral_unread(text, nrows, ncols):
    """Reverse spiral reading: text was read spirally, put it back row-by-row."""
    if nrows * ncols < len(text):
        return None

    # Determine spiral order of positions
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

    # Place text into grid at spiral positions
    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        if i < len(positions):
            r, c = positions[i]
            grid[r][c] = ch

    # Read row by row
    result = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c] != '\x00':
                result.append(grid[r][c])

    return ''.join(result[:len(text)])


def route_diagonal_read(text, nrows, ncols):
    """Read text from grid diagonally (top-left to bottom-right diagonals)."""
    if nrows * ncols < len(text):
        return None

    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        grid[i // ncols][i % ncols] = ch

    result = []
    for d in range(nrows + ncols - 1):
        for r in range(max(0, d - ncols + 1), min(nrows, d + 1)):
            c = d - r
            if 0 <= c < ncols and grid[r][c] != '\x00':
                result.append(grid[r][c])

    return ''.join(result[:len(text)])


def route_diagonal_unread(text, nrows, ncols):
    """Reverse diagonal reading."""
    if nrows * ncols < len(text):
        return None

    positions = []
    for d in range(nrows + ncols - 1):
        for r in range(max(0, d - ncols + 1), min(nrows, d + 1)):
            c = d - r
            if 0 <= c < ncols:
                positions.append((r, c))

    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        if i < len(positions):
            r, c = positions[i]
            grid[r][c] = ch

    result = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c] != '\x00':
                result.append(grid[r][c])

    return ''.join(result[:len(text)])


def route_zigzag_cols(text, nrows, ncols):
    """Read column by column, alternating direction (down, up, down, ...)."""
    if nrows * ncols < len(text):
        return None

    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        grid[i // ncols][i % ncols] = ch

    result = []
    for c in range(ncols):
        if c % 2 == 0:
            for r in range(nrows):
                if grid[r][c] != '\x00':
                    result.append(grid[r][c])
        else:
            for r in range(nrows - 1, -1, -1):
                if grid[r][c] != '\x00':
                    result.append(grid[r][c])

    return ''.join(result[:len(text)])


def route_zigzag_cols_unread(text, nrows, ncols):
    """Reverse zigzag column reading."""
    if nrows * ncols < len(text):
        return None

    positions = []
    for c in range(ncols):
        if c % 2 == 0:
            for r in range(nrows):
                positions.append((r, c))
        else:
            for r in range(nrows - 1, -1, -1):
                positions.append((r, c))

    grid = [['\x00'] * ncols for _ in range(nrows)]
    for i, ch in enumerate(text):
        if i < len(positions):
            r, c = positions[i]
            grid[r][c] = ch

    result = []
    for r in range(nrows):
        for c in range(ncols):
            if grid[r][c] != '\x00':
                result.append(grid[r][c])

    return ''.join(result[:len(text)])


def test_approach4():
    """Test route ciphers combined with Vigenere."""
    results = []

    route_methods = [
        ("spiral", route_spiral_unread),
        ("diagonal", route_diagonal_unread),
        ("zigzag_cols", route_zigzag_cols_unread),
    ]

    # Find grid dimensions that fit 97 chars
    dimensions = []
    for ncols in range(2, 50):
        nrows = math.ceil(K4_LEN / ncols)
        if nrows >= 2:
            dimensions.append((nrows, ncols))

    for nrows, ncols in dimensions:
        for route_name, route_func in route_methods:
            un_routed = route_func(K4, nrows, ncols)
            if un_routed is None or len(un_routed) != K4_LEN:
                continue

            for vig_key in VIG_KEYS:
                for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
                    # Order A: Vig then Route (decrypt: un-route then vig-decrypt)
                    pt_a = vigenere_decrypt(un_routed, vig_key, alpha)
                    has_b, has_n = check_both_cribs(pt_a)
                    if has_b or has_n:
                        sc = score_english(pt_a)
                        words = find_english_words(pt_a, min_len=5)
                        which = []
                        if has_b: which.append("BERLINCLOCK@63")
                        if has_n: which.append("NORTHEAST@16")
                        print(f"\n  {route_name}({nrows}x{ncols}) then Vig({vig_key},{alpha_name}): {which}")
                        print(f"  Plaintext: {pt_a}")
                        print(f"  Score: {sc:.2f}, Words: {words}")
                        results.append((sc, pt_a, f"{route_name}+vig", "A"))

                    # Order B: Route then Vig (decrypt: vig-decrypt then un-route)
                    vig_dec = vigenere_decrypt(K4, vig_key, alpha)
                    pt_b = route_func(vig_dec, nrows, ncols)
                    if pt_b is None or len(pt_b) != K4_LEN:
                        continue
                    has_b, has_n = check_both_cribs(pt_b)
                    if has_b or has_n:
                        sc = score_english(pt_b)
                        words = find_english_words(pt_b, min_len=5)
                        which = []
                        if has_b: which.append("BERLINCLOCK@63")
                        if has_n: which.append("NORTHEAST@16")
                        print(f"\n  Vig({vig_key},{alpha_name}) then {route_name}({nrows}x{ncols}): {which}")
                        print(f"  Plaintext: {pt_b}")
                        print(f"  Score: {sc:.2f}, Words: {words}")
                        results.append((sc, pt_b, f"vig+{route_name}", "B"))

    return results


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 5: Exhaustive Short Vig Keys + Transposition
# Try ALL possible short Vigenere keys (length 2-4) with transposition
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("APPROACH 5: Short Vigenere Keys (len 2-4) + Small Transpositions")
print("  Using crib constraints for maximum pruning")
print("=" * 78)

def test_approach5():
    """
    For short Vigenere keys combined with small transpositions,
    use crib constraints to derive key characters.

    For Approach 2 (transpose then Vig):
    K4[i] = Vig_enc(transposed_plain[i], key[i % keylen])
    So: transposed_plain[i] = Vig_dec(K4[i], key[i % keylen])
    Then un-transpose to get plain.

    We know plain[63..73] = BERLINCLOCK, plain[16..24] = NORTHEAST.
    For a given transposition key_order, we know which transposed positions
    map to plain positions 63-73 and 16-24.
    This tells us what transposed_plain values must be at those positions.
    Combined with K4 values at those positions, we can derive Vig key chars.
    """
    results = []

    # Approach: For each transposition ncols (2-8):
    #   For each column permutation:
    #     Determine which K4 positions map to plaintext positions 63-73 and 16-24
    #     For each such position i, we need:
    #       vig_dec(K4[i], key[i % keylen]) -> then untransposed -> BERLINCLOCK/NORTHEAST char
    #     Actually, the transposition happens FIRST (on plaintext), then Vig.
    #     So: K4[i] = Vig_enc(intermediate[i]), where intermediate = transpose(plaintext)
    #     plaintext[p] appears at intermediate[t(p)] where t is the transposition mapping.
    #     K4[t(p)] = Vig_enc(plaintext[p], key[t(p) % keylen])
    #     So: plaintext[p] = Vig_dec(K4[t(p)], key[t(p) % keylen])
    #
    #     For p in {63..73}: plaintext[p] = BERLINCLOCK[p-63]
    #     So: BERLINCLOCK[j] = Vig_dec(K4[t(63+j)], key[t(63+j) % keylen])
    #     Which gives: key[t(63+j) % keylen] = Vig_key_from(K4[t(63+j)], BERLINCLOCK[j])
    #
    # For the REVERSE (Vig then transpose):
    #     K4 = transpose(Vig_enc(plaintext))
    #     intermediate = Vig_enc(plaintext)
    #     intermediate[p] = Vig_enc(plaintext[p], key[p % keylen])
    #     K4[t(p)] = intermediate[p] = Vig_enc(plaintext[p], key[p % keylen])
    #     plaintext[p] = Vig_dec(K4[inv_t(p)], key[p % keylen])  ... no that's wrong
    #
    #     Actually: K4 = transpose(intermediate)
    #     So K4[out_pos] = intermediate[in_pos] via the transposition mapping
    #     And intermediate[p] = Vig_enc(plaintext[p], key[p % keylen])
    #     So to get plaintext: intermediate[p] = K4[t(p)] (where t maps input to output)
    #     plaintext[p] = Vig_dec(intermediate[p], key[p % keylen])
    #     = Vig_dec(K4[t(p)], key[p % keylen])
    #
    #     For p=63+j: BERLINCLOCK[j] = Vig_dec(K4[t(63+j)], key[(63+j) % keylen])
    #     key[(63+j) % keylen] = derive_from(K4[t(63+j)], BERLINCLOCK[j])

    # Let's implement for Approach2 specifically (transpose then Vig) with key derivation

    print("\n--- Deriving Vig key from cribs for Transpose-then-Vig ---")

    for ncols in range(2, 9):
        nrows = math.ceil(K4_LEN / ncols)
        n_perms = math.factorial(ncols)
        if n_perms > 100000:
            continue

        for perm in itertools.permutations(range(ncols)):
            key_order = list(perm)

            # Get forward mapping: input_pos -> output_pos for the transposition
            fwd_map = get_transposition_mapping(key_order, K4_LEN)
            # fwd_map[out_pos] = in_pos means: transpose output[out_pos] = input[in_pos]

            # Build input->output map
            in_to_out = {}
            for out_pos, in_pos in fwd_map.items():
                in_to_out[in_pos] = out_pos

            # For Transpose-then-Vig (encryption: plain -> transpose -> vig -> K4):
            # K4[i] = Vig_enc(transposed[i], key[i%kl])
            # transposed[out_pos] = plain[in_pos] where fwd_map[out_pos] = in_pos
            # So to decrypt: transposed[i] = Vig_dec(K4[i], key[i%kl])
            # then plain[in_pos] = transposed[out_pos] via inverse
            #
            # For plain[p] = BERLINCLOCK[j] (p = 63+j):
            # p is at in_pos = p in the grid
            # transposed[in_to_out[p]] = plain[p]
            # K4[in_to_out[p]] = Vig_enc(plain[p], key[in_to_out[p] % kl])
            # So key[in_to_out[p] % kl] = (K4_idx(K4[in_to_out[p]]) - K4_idx(plain[p])) % 26

            for vig_keylen in range(2, 15):
                derived_key = [None] * vig_keylen
                consistent = True

                # Derive from BERLINCLOCK
                for j, ch in enumerate("BERLINCLOCK"):
                    p = 63 + j
                    if p not in in_to_out:
                        consistent = False
                        break
                    out_p = in_to_out[p]
                    if out_p >= K4_LEN:
                        consistent = False
                        break

                    ct_char = K4[out_p]
                    pt_char = ch

                    # key_char: ct = (pt + key) % 26 in KRYPTOS alphabet
                    key_val = (KRYPTOS_ALPHA.index(ct_char) - KRYPTOS_ALPHA.index(pt_char)) % 26
                    key_char = KRYPTOS_ALPHA[key_val]

                    slot = out_p % vig_keylen
                    if derived_key[slot] is None:
                        derived_key[slot] = key_char
                    elif derived_key[slot] != key_char:
                        consistent = False
                        break

                if not consistent:
                    continue

                # Derive from NORTHEAST
                for j, ch in enumerate("NORTHEAST"):
                    p = 16 + j
                    if p not in in_to_out:
                        consistent = False
                        break
                    out_p = in_to_out[p]
                    if out_p >= K4_LEN:
                        consistent = False
                        break

                    ct_char = K4[out_p]
                    pt_char = ch

                    key_val = (KRYPTOS_ALPHA.index(ct_char) - KRYPTOS_ALPHA.index(pt_char)) % 26
                    key_char = KRYPTOS_ALPHA[key_val]

                    slot = out_p % vig_keylen
                    if derived_key[slot] is None:
                        derived_key[slot] = key_char
                    elif derived_key[slot] != key_char:
                        consistent = False
                        break

                if not consistent:
                    continue

                # We have a consistent (possibly partial) key!
                # Fill unknowns and try all possibilities for unfilled slots
                unknown_slots = [i for i in range(vig_keylen) if derived_key[i] is None]
                n_unknown = len(unknown_slots)

                if n_unknown > 4:
                    # Too many unknowns to brute-force; skip
                    continue

                # Try all combinations for unknown slots
                for combo in itertools.product(range(26), repeat=n_unknown):
                    test_key = derived_key[:]
                    for idx, val in zip(unknown_slots, combo):
                        test_key[idx] = KRYPTOS_ALPHA[val]

                    key_str = ''.join(test_key)

                    # Full decrypt
                    intermediate = vigenere_decrypt(K4, key_str)
                    plaintext = columnar_untranspose(intermediate, key_order)

                    has_b, has_n = check_both_cribs(plaintext)
                    if has_b and has_n:
                        sc = score_english(plaintext)
                        words = find_english_words(plaintext, min_len=5)
                        print(f"\n*** CRIBS MATCH (Transpose-then-Vig)! ***")
                        print(f"  Derived Vig key: {key_str} (len {vig_keylen})")
                        print(f"  Transp cols: {ncols}, order: {key_order}")
                        print(f"  Plaintext: {plaintext}")
                        print(f"  Score: {sc:.2f}")
                        if words:
                            print(f"  Words: {words}")
                        results.append((sc, plaintext, key_str, key_order, "transpose-then-vig"))

            # Also do Vig-then-Transpose derivation
            # Encryption: plain -> Vig -> transpose -> K4
            # K4[out] = intermediate[in] via transposition fwd_map
            # intermediate[p] = Vig_enc(plain[p], key[p % kl])
            # So K4[in_to_out[p]] = Vig_enc(plain[p], key[p % kl])
            # For plain[p] known: key[p % kl] = (K4_idx(K4[in_to_out[p]]) - K4_idx(plain[p])) % 26
            # Wait, this is the same mapping since we use p for position.
            # Actually NO: for Vig-then-transpose:
            # intermediate[p] = Vig_enc(plain[p], key[p % kl])   -- Vig uses plaintext position
            # K4[out] = intermediate[in] via transposition
            # So K4[in_to_out[p]] = intermediate[p] = Vig_enc(plain[p], key[p % kl])
            # key[p % kl] = (idx(K4[in_to_out[p]]) - idx(plain[p])) % 26

            for vig_keylen in range(2, 15):
                derived_key = [None] * vig_keylen
                consistent = True

                for j, ch in enumerate("BERLINCLOCK"):
                    p = 63 + j
                    if p not in in_to_out:
                        consistent = False
                        break
                    out_p = in_to_out[p]
                    if out_p >= K4_LEN:
                        consistent = False
                        break

                    ct_char = K4[out_p]
                    pt_char = ch
                    key_val = (KRYPTOS_ALPHA.index(ct_char) - KRYPTOS_ALPHA.index(pt_char)) % 26
                    key_char = KRYPTOS_ALPHA[key_val]

                    slot = p % vig_keylen  # NOTE: Vig key position based on plaintext position
                    if derived_key[slot] is None:
                        derived_key[slot] = key_char
                    elif derived_key[slot] != key_char:
                        consistent = False
                        break

                if not consistent:
                    continue

                for j, ch in enumerate("NORTHEAST"):
                    p = 16 + j
                    if p not in in_to_out:
                        consistent = False
                        break
                    out_p = in_to_out[p]
                    if out_p >= K4_LEN:
                        consistent = False
                        break

                    ct_char = K4[out_p]
                    pt_char = ch
                    key_val = (KRYPTOS_ALPHA.index(ct_char) - KRYPTOS_ALPHA.index(pt_char)) % 26
                    key_char = KRYPTOS_ALPHA[key_val]

                    slot = p % vig_keylen
                    if derived_key[slot] is None:
                        derived_key[slot] = key_char
                    elif derived_key[slot] != key_char:
                        consistent = False
                        break

                if not consistent:
                    continue

                unknown_slots = [i for i in range(vig_keylen) if derived_key[i] is None]
                n_unknown = len(unknown_slots)

                if n_unknown > 4:
                    continue

                for combo in itertools.product(range(26), repeat=n_unknown):
                    test_key = derived_key[:]
                    for idx, val in zip(unknown_slots, combo):
                        test_key[idx] = KRYPTOS_ALPHA[val]

                    key_str = ''.join(test_key)

                    # Decrypt: un-transpose K4, then vig-decrypt
                    untransposed = columnar_untranspose(K4, key_order)
                    plaintext = vigenere_decrypt(untransposed, key_str)

                    has_b, has_n = check_both_cribs(plaintext)
                    if has_b and has_n:
                        sc = score_english(plaintext)
                        words = find_english_words(plaintext, min_len=5)
                        print(f"\n*** CRIBS MATCH (Vig-then-Transpose)! ***")
                        print(f"  Derived Vig key: {key_str} (len {vig_keylen})")
                        print(f"  Transp cols: {ncols}, order: {key_order}")
                        print(f"  Plaintext: {plaintext}")
                        print(f"  Score: {sc:.2f}")
                        if words:
                            print(f"  Words: {words}")
                        results.append((sc, plaintext, key_str, key_order, "vig-then-transpose"))

    return results


# ═════════════════════════════════════════════════════════════════════════════
# APPROACH 6: Keyword-based column order transpositions
# Instead of numeric permutations, derive column order from keyword
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("APPROACH 6: Keyword-Derived Column Orders + Vigenere")
print("=" * 78)

def keyword_to_order(keyword):
    """Convert keyword to column order (alphabetical ranking of letters)."""
    indexed = sorted(enumerate(keyword), key=lambda x: x[1])
    order = [0] * len(keyword)
    for rank, (orig_idx, _) in enumerate(indexed):
        order[orig_idx] = rank
    return order


def test_approach6():
    """Test keyword-derived transposition orders with Vigenere."""
    results = []

    transp_keywords = [
        "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
        "BERLINCLOCK", "NORTHEAST", "SANBORN", "CIA", "NSA",
        "SHADOW", "LUCID", "SECRET", "ENIGMA", "CRYPTO",
        "QUAGMIRE", "DIGETAL", "INTERPRETIV",
        "SB", "JG", "WW", "KR", "FK",  # short keys
    ]

    for t_kw in transp_keywords:
        key_order = keyword_to_order(t_kw)

        for vig_key in VIG_KEYS:
            for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
                # Order A: Vig then Transpose (decrypt: un-transpose then vig-decrypt)
                untransposed = columnar_untranspose(K4, key_order)
                pt_a = vigenere_decrypt(untransposed, vig_key, alpha)

                has_b, has_n = check_both_cribs(pt_a)
                if has_b or has_n:
                    sc = score_english(pt_a)
                    words = find_english_words(pt_a, min_len=5)
                    which = []
                    if has_b: which.append("BERLINCLOCK@63")
                    if has_n: which.append("NORTHEAST@16")
                    print(f"\n  Trans({t_kw}={key_order}) then Vig({vig_key},{alpha_name}): {which}")
                    print(f"  Plaintext: {pt_a}")
                    print(f"  Score: {sc:.2f}, Words: {words}")
                    results.append((sc, pt_a, f"trans_{t_kw}+vig_{vig_key}", key_order))

                # Order B: Transpose then Vig (decrypt: vig-decrypt then un-transpose)
                vig_dec = vigenere_decrypt(K4, vig_key, alpha)
                pt_b = columnar_untranspose(vig_dec, key_order)

                has_b, has_n = check_both_cribs(pt_b)
                if has_b or has_n:
                    sc = score_english(pt_b)
                    words = find_english_words(pt_b, min_len=5)
                    which = []
                    if has_b: which.append("BERLINCLOCK@63")
                    if has_n: which.append("NORTHEAST@16")
                    print(f"\n  Vig({vig_key},{alpha_name}) then Trans({t_kw}={key_order}): {which}")
                    print(f"  Plaintext: {pt_b}")
                    print(f"  Score: {sc:.2f}, Words: {words}")
                    results.append((sc, pt_b, f"vig_{vig_key}+trans_{t_kw}", key_order))

    return results


# ═════════════════════════════════════════════════════════════════════════════
# RUN ALL APPROACHES
# ═════════════════════════════════════════════════════════════════════════════

all_results = []

print("\n" + "#" * 78)
print("# RUNNING APPROACH 1: Vig then Columnar Transposition (enumeration)")
print("#" * 78)
r1 = test_approach1()
all_results.extend(r1)
print(f"\nApproach 1 complete. Found {len(r1)} results.")

print("\n" + "#" * 78)
print("# RUNNING APPROACH 2: Columnar Transposition then Vig")
print("#" * 78)
r2 = test_approach2()
all_results.extend(r2)
print(f"\nApproach 2 complete. Found {len(r2)} results.")

print("\n" + "#" * 78)
print("# RUNNING APPROACH 3: Rail Fence + Vig")
print("#" * 78)
r3 = test_approach3()
all_results.extend(r3)
print(f"\nApproach 3 complete. Found {len(r3)} results.")

print("\n" + "#" * 78)
print("# RUNNING APPROACH 4: Route Cipher + Vig")
print("#" * 78)
r4 = test_approach4()
all_results.extend(r4)
print(f"\nApproach 4 complete. Found {len(r4)} results.")

print("\n" + "#" * 78)
print("# RUNNING APPROACH 5: Short Vig Keys + Transposition (key derivation)")
print("#" * 78)
r5 = test_approach5()
all_results.extend(r5)
print(f"\nApproach 5 complete. Found {len(r5)} results.")

print("\n" + "#" * 78)
print("# RUNNING APPROACH 6: Keyword-Derived Column Orders + Vig")
print("#" * 78)
r6 = test_approach6()
all_results.extend(r6)
print(f"\nApproach 6 complete. Found {len(r6)} results.")

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 78)
print("FINAL SUMMARY")
print("=" * 78)

if all_results:
    all_results.sort(key=lambda x: x[0], reverse=True)
    print(f"\nTotal results found: {len(all_results)}")
    print("\nTop results by English score:")
    for i, res in enumerate(all_results[:20]):
        sc = res[0]
        pt = res[1]
        info = res[2:]
        print(f"\n  #{i+1} Score: {sc:.2f}")
        print(f"     Plaintext: {pt}")
        print(f"     Details: {info}")
        words = find_english_words(pt, min_len=4)
        if words:
            print(f"     English words: {words[:15]}")
else:
    print("\nNo results found with crib matches or high English scores.")
    print("\nThis strongly suggests K4 does NOT use a simple two-step process of")
    print("Vigenere + columnar transposition (or rail fence / route cipher) with")
    print("the tested keys. The encryption method is likely more complex:")
    print("  - Non-standard transposition pattern")
    print("  - Key-dependent substitution (not simple Vigenere)")
    print("  - More than two layers of encryption")
    print("  - A completely different cipher type")

print("\n" + "=" * 78)
print("ANALYSIS COMPLETE")
print("=" * 78)
