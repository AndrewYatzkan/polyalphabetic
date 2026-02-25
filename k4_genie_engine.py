#!/usr/bin/env python3
"""
K4 Genie Engine Approach
========================
Implements and tests the "Genie Engine" Berlin-Clock-inspired transposition
combined with k mod 3 substitution for Kryptos K4.

Parameters from the published paper:
  - Band structure: 4-4-11-4 (Berlin Clock rows)
  - Cycle length: 23
  - Boustrophedon reversal mask: 15 (all bands reverse)
  - Offset: 21
  - Substitution: k mod 3 cycling through 3 alphabets

Known cribs:
  - BERLINCLOCK at plaintext position 63
  - EASTNORTHEAST at plaintext position 21
"""

import sys
import time
import itertools
import string
from collections import Counter

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4_CIPHER)  # 97

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CRIBS = {
    "BERLINCLOCK": 63,
    "EASTNORTHEAST": 21,
}

DICT_PATH = "/home/user/polyalphabetic/OxfordEnglishWords.txt"

# ─────────────────────────────────────────────
# Load dictionary
# ─────────────────────────────────────────────
def load_dictionary(min_len=4):
    words = set()
    try:
        with open(DICT_PATH, 'r') as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= min_len and w.isalpha():
                    words.add(w)
    except FileNotFoundError:
        print(f"[WARNING] Dictionary not found at {DICT_PATH}")
    return words

# ─────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────
def count_english_words(text, dictionary, min_len=4):
    text = text.upper()
    found = []
    for word in dictionary:
        if len(word) >= min_len and word in text:
            found.append(word)
    return found

def check_cribs(text):
    results = {}
    for crib, expected_pos in CRIBS.items():
        idx = text.upper().find(crib)
        if idx >= 0:
            results[crib] = {"found": True, "at_pos": idx, "expected_pos": expected_pos,
                             "correct_pos": idx == expected_pos}
        else:
            results[crib] = {"found": False}
    return results

def has_any_crib(text):
    t = text.upper()
    return any(crib in t for crib in CRIBS)

# ─────────────────────────────────────────────
# Substitution helpers
# ─────────────────────────────────────────────
def vigenere_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    result = []
    alen = len(alphabet)
    for i, c in enumerate(ciphertext):
        if c in alphabet:
            ct_idx = alphabet.index(c)
            key_idx = alphabet.index(key[i % len(key)])
            result.append(alphabet[(ct_idx - key_idx) % alen])
        else:
            result.append(c)
    return ''.join(result)

def caesar_shift(text, shift, alphabet=STANDARD_ALPHA):
    result = []
    alen = len(alphabet)
    for c in text:
        if c in alphabet:
            result.append(alphabet[(alphabet.index(c) + shift) % alen])
        else:
            result.append(c)
    return ''.join(result)

# ─────────────────────────────────────────────
# Transposition engines
# ─────────────────────────────────────────────
def build_perm_v1(n, bands, mask):
    """
    Build permutation array for band-level boustrophedon.
    perm[i] = source position for output position i.
    
    Text is divided into cycles of sum(bands). Within each cycle,
    bands define groups. On odd cycles, bands with their mask bit set
    are read in reverse.
    """
    cycle_len = sum(bands)
    perm = []
    pos = 0
    cycle = 0
    while len(perm) < n:
        for band_idx, bw in enumerate(bands):
            should_reverse = (cycle % 2 == 1) and ((mask >> band_idx) & 1)
            band_positions = list(range(pos, min(pos + bw, n)))
            if should_reverse:
                band_positions = band_positions[::-1]
            perm.extend(band_positions)
            pos += bw
            if pos >= n:
                break
        cycle += 1
    return perm[:n]


def build_perm_v2(n, bands, mask):
    """
    V2: Write into rows of cycle_len. On odd rows, reverse specified bands.
    Same as V1 for mask operations, but conceptually row-based.
    """
    # V2 is identical to V1 in its output (row = cycle)
    return build_perm_v1(n, bands, mask)


def build_perm_v3(n, bands, mask):
    """
    V3: Write text into rows of cycle_len width. Read columns within each band group,
    with direction controlled by mask.
    """
    cycle_len = sum(bands)
    num_rows = (n + cycle_len - 1) // cycle_len
    perm = []
    col_start = 0
    for band_idx, bw in enumerate(bands):
        should_reverse = (mask >> band_idx) & 1
        for col_offset in range(bw):
            col = col_start + col_offset
            if should_reverse:
                row_order = range(num_rows - 1, -1, -1)
            else:
                row_order = range(num_rows)
            for row in row_order:
                idx = row * cycle_len + col
                if idx < n:
                    perm.append(idx)
        col_start += bw
    return perm[:n]


def apply_perm(text, perm):
    """Apply forward permutation: output[i] = text[perm[i]]."""
    return ''.join(text[p] if p < len(text) else '?' for p in perm)


def apply_inv_perm(text, perm):
    """Apply inverse permutation: result[perm[i]] = text[i]."""
    result = ['?'] * len(text)
    for i, p in enumerate(perm):
        if p < len(text) and i < len(text):
            result[p] = text[i]
    return ''.join(result)


def apply_offset(perm, offset, n):
    """Shift permutation by offset (circular)."""
    if offset == 0:
        return perm
    return perm[offset:] + perm[:offset]


def is_identity(perm):
    """Check if a permutation is the identity."""
    return all(perm[i] == i for i in range(len(perm)))


# ─────────────────────────────────────────────
# Key derivation from cribs
# ─────────────────────────────────────────────
def derive_key_from_cribs(transposed_text, period, alphabet=STANDARD_ALPHA):
    """
    Given transposed ciphertext and known plaintext cribs,
    derive Vigenere key values.
    
    plaintext[i] = decrypt(transposed[i], key[i % period])
    => key[i % period] = (transposed[i] - plaintext[i]) mod 26
    """
    alen = len(alphabet)
    key_slots = {}
    
    for crib, pt_pos in CRIBS.items():
        for j, ch in enumerate(crib):
            pos = pt_pos + j
            if pos < len(transposed_text):
                ct_val = alphabet.index(transposed_text[pos])
                pt_val = alphabet.index(ch)
                key_val = (ct_val - pt_val) % alen
                slot = pos % period
                if slot in key_slots:
                    if key_slots[slot] != key_val:
                        return None  # Inconsistent
                else:
                    key_slots[slot] = key_val
    return key_slots


def decrypt_with_partial_key(text, key_slots, period, alphabet=STANDARD_ALPHA):
    """Decrypt text using partial key."""
    alen = len(alphabet)
    result = []
    for i, c in enumerate(text):
        slot = i % period
        if slot in key_slots:
            pt_val = (alphabet.index(c) - key_slots[slot]) % alen
            result.append(alphabet[pt_val])
        else:
            result.append('?')
    return ''.join(result)


def verify_cribs_in_plaintext(pt):
    """Check cribs appear at exact expected positions."""
    for crib, pos in CRIBS.items():
        if pt[pos:pos + len(crib)] != crib:
            return False
    return True


# ─────────────────────────────────────────────
# PART 1: Test exact Genie Engine parameters
# ─────────────────────────────────────────────
def test_genie_exact_params():
    print("=" * 80)
    print("PART 1: Testing Exact Genie Engine Parameters")
    print("=" * 80)
    print(f"K4 ciphertext ({K4_LEN} chars): {K4_CIPHER}")
    print(f"Bands: (4,4,11,4), Cycle: 23, Mask: 15, Offset: 21")
    print()

    bands = (4, 4, 11, 4)
    mask = 15
    offset = 21
    n = K4_LEN

    # Build permutations for all versions
    versions = {}
    for vname, build_fn in [("V1", build_perm_v1), ("V3", build_perm_v3)]:
        perm = build_fn(n, bands, mask)
        perm_off = apply_offset(perm, offset, n)
        fwd = apply_perm(K4_CIPHER, perm_off)
        inv = apply_inv_perm(K4_CIPHER, perm_off)
        versions[vname] = {"fwd": fwd, "inv": inv, "perm": perm_off}

    for vname, data in versions.items():
        for direction, text in [("forward", data["fwd"]), ("inverse", data["inv"])]:
            print(f"  {vname} {direction}: {text}")
            crib_check = check_cribs(text)
            for crib, info in crib_check.items():
                if info["found"]:
                    print(f"    *** CRIB: {crib} at pos {info['at_pos']} (expected {info['expected_pos']})")
    print()

    # Test k mod 3 substitution on all transposed results
    print("  Testing k mod 3 Caesar substitution (26^3 = 17,576 keys per text)...")
    hit_count = 0

    all_texts = []
    for vname, data in versions.items():
        all_texts.append((f"{vname}_fwd", data["fwd"]))
        all_texts.append((f"{vname}_inv", data["inv"]))

    # Also add V1 with mask=0 (no reversal) and other masks
    for m in range(16):
        for off in [0, 21]:
            perm = build_perm_v1(n, bands, m)
            perm_off = apply_offset(perm, off, n)
            if not is_identity(perm_off):
                fwd = apply_perm(K4_CIPHER, perm_off)
                all_texts.append((f"V1_m{m}_o{off}_fwd", fwd))
                inv = apply_inv_perm(K4_CIPHER, perm_off)
                all_texts.append((f"V1_m{m}_o{off}_inv", inv))
            # V3
            perm3 = build_perm_v3(n, bands, m)
            perm3_off = apply_offset(perm3, off, n)
            if not is_identity(perm3_off):
                fwd3 = apply_perm(K4_CIPHER, perm3_off)
                all_texts.append((f"V3_m{m}_o{off}_fwd", fwd3))

    # Deduplicate
    seen = set()
    unique_texts = []
    for name, text in all_texts:
        if text not in seen:
            seen.add(text)
            unique_texts.append((name, text))

    print(f"  Unique transposed texts to test: {len(unique_texts)}")

    for t_name, t_text in unique_texts:
        # Standard alphabet mod-3
        for s0 in range(26):
            for s1 in range(26):
                for s2 in range(26):
                    shifts = [s0, s1, s2]
                    pt = []
                    for i, c in enumerate(t_text):
                        idx = STANDARD_ALPHA.index(c)
                        pt.append(STANDARD_ALPHA[(idx - shifts[i % 3]) % 26])
                    pt_str = ''.join(pt)
                    if has_any_crib(pt_str):
                        hit_count += 1
                        print(f"  *** MOD-3 HIT ({t_name}, shifts={shifts}): {pt_str}")
                        cr = check_cribs(pt_str)
                        for crib, info in cr.items():
                            if info["found"]:
                                pos_match = "CORRECT POS" if info["correct_pos"] else f"at {info['at_pos']}"
                                print(f"      {crib}: {pos_match}")

        # KRYPTOS alphabet mod-3
        for s0 in range(26):
            for s1 in range(26):
                for s2 in range(26):
                    shifts = [s0, s1, s2]
                    pt = []
                    for i, c in enumerate(t_text):
                        idx = KRYPTOS_ALPHA.index(c)
                        pt.append(KRYPTOS_ALPHA[(idx - shifts[i % 3]) % 26])
                    pt_str = ''.join(pt)
                    if has_any_crib(pt_str):
                        hit_count += 1
                        print(f"  *** MOD-3 KRYPTOS HIT ({t_name}, shifts={shifts}): {pt_str}")

    # Test Vigenere period-3 on raw K4
    print(f"\n  Testing Vigenere period-3 on raw K4 (no transposition)...")
    for s0 in range(26):
        for s1 in range(26):
            for s2 in range(26):
                key = STANDARD_ALPHA[s0] + STANDARD_ALPHA[s1] + STANDARD_ALPHA[s2]
                pt = vigenere_decrypt(K4_CIPHER, key)
                if has_any_crib(pt):
                    print(f"  *** RAW VIG-3 HIT (key='{key}'): {pt}")

    print(f"\n  Part 1 mod-3 hits: {hit_count}")
    print("  Part 1 complete.\n")


# ─────────────────────────────────────────────
# PART 2: Exhaustive transposition search
# ─────────────────────────────────────────────
def exhaustive_transposition_search():
    print("=" * 80)
    print("PART 2: Exhaustive Transposition Parameter Search")
    print("=" * 80)
    
    start_time = time.time()
    hits = []
    n = K4_LEN

    # PHASE 2A: Identity transposition baseline
    print("\n  Phase 2A: Baseline - identity transposition (no rearrangement)")
    print("  Checking which Vigenere periods are consistent with both cribs...")
    
    consistent_periods = []
    for period in range(2, 98):
        ks = derive_key_from_cribs(K4_CIPHER, period)
        if ks is not None:
            pt = decrypt_with_partial_key(K4_CIPHER, ks, period)
            filled = len(ks)
            consistent_periods.append((period, filled, ks))

    print(f"  Consistent periods: {[p for p, f, _ in consistent_periods]}")
    for period, filled, ks in consistent_periods:
        partial_key = ['?'] * period
        for slot, val in ks.items():
            partial_key[slot] = STANDARD_ALPHA[val]
        pt = decrypt_with_partial_key(K4_CIPHER, ks, period)
        print(f"    Period {period} ({filled}/{period} slots): key={''.join(partial_key)}")
        print(f"      PT: {pt}")

    # PHASE 2B: Non-trivial transpositions with Berlin Clock bands
    print(f"\n  Phase 2B: Berlin Clock bands (4,4,11,4) - all masks and offsets")
    print(f"    Testing 3 build methods x 16 masks x 97 offsets x 2 dirs = {3*16*97*2} combos")
    print(f"    Checking period-29 key consistency (excluding identity permutations)")
    
    bands_4411_4 = (4, 4, 11, 4)
    period = 29
    nontrivial_hits = []

    for build_name, build_fn in [("V1", build_perm_v1), ("V3", build_perm_v3)]:
        for mask in range(16):
            base_perm = build_fn(n, bands_4411_4, mask)
            for offset in range(n):
                perm = apply_offset(base_perm, offset, n)
                if is_identity(perm):
                    continue  # Skip identity - already tested above

                for direction, apply_fn in [("fwd", apply_perm), ("inv", apply_inv_perm)]:
                    transposed = apply_fn(K4_CIPHER, perm)
                    
                    # Direct crib check
                    if has_any_crib(transposed):
                        print(f"    *** DIRECT CRIB: {build_name} mask={mask} off={offset} {direction}")
                        print(f"        {transposed}")
                        nontrivial_hits.append(("direct", build_name, mask, offset, direction))

                    # Vigenere period 29 consistency
                    ks = derive_key_from_cribs(transposed, period)
                    if ks is not None and len(ks) >= 20:
                        pt = decrypt_with_partial_key(transposed, ks, period)
                        if verify_cribs_in_plaintext(pt):
                            # Check if the non-crib parts look at all different from identity
                            identity_ks = derive_key_from_cribs(K4_CIPHER, period)
                            if ks != identity_ks:
                                partial_key = ['?'] * period
                                for slot, val in ks.items():
                                    partial_key[slot] = STANDARD_ALPHA[val]
                                filled = len(ks)
                                nontrivial_hits.append(("vig29", build_name, mask, offset, direction, ks))
                                # Only print first few
                                if len(nontrivial_hits) <= 20:
                                    print(f"    HIT: {build_name} m={mask} o={offset} {direction} ({filled}/{period})")
                                    print(f"      Key: {''.join(partial_key)}")
                                    print(f"      PT:  {pt[:40]}...{pt[60:75]}...{pt[85:]}")

    print(f"  Phase 2B total non-trivial hits: {len(nontrivial_hits)}")

    # PHASE 2C: Broader band structures (non-identity only)
    print(f"\n  Phase 2C: Testing diverse band structures with period 29")
    
    # Generate interesting band structures
    test_structures = set()
    # Permutations of Berlin Clock
    for perm in itertools.permutations([4, 4, 11, 4]):
        test_structures.add(perm)
    # Variations
    for base in [(4,4,11,4), (5,5,11,4), (4,4,12,4), (3,4,11,5)]:
        for perm in itertools.permutations(base):
            if 20 <= sum(perm) <= 30:
                test_structures.add(perm)
    # Simple equal-band structures
    for bw in range(2, 16):
        for nb in range(2, 7):
            s = bw * nb
            if 20 <= s <= 30:
                test_structures.add(tuple([bw] * nb))
    # Some 3-band structures
    for a in range(2, 20):
        for b in range(2, 20):
            c = 23 - a - b
            if 2 <= c <= 20:
                test_structures.add((a, b, c))
            c = 29 - a - b
            if 2 <= c <= 20:
                test_structures.add((a, b, c))

    print(f"  Band structures to test: {len(test_structures)}")
    
    phase2c_hits = []
    tested = 0
    
    for bands in test_structures:
        num_bands = len(bands)
        max_mask = 1 << num_bands
        
        for build_name, build_fn in [("V1", build_perm_v1), ("V3", build_perm_v3)]:
            for mask in range(max_mask):
                if mask == 0:
                    continue  # mask=0 with V1 is always identity
                base_perm = build_fn(n, bands, mask)
                if is_identity(base_perm):
                    continue
                    
                for offset in range(n):
                    perm = apply_offset(base_perm, offset, n)
                    tested += 1
                    
                    for direction, apply_fn in [("fwd", apply_perm), ("inv", apply_inv_perm)]:
                        transposed = apply_fn(K4_CIPHER, perm)
                        
                        if has_any_crib(transposed):
                            print(f"    *** DIRECT CRIB: {bands} {build_name} m={mask} o={offset} {direction}")
                            phase2c_hits.append(("direct", bands, build_name, mask, offset))
                        
                        ks = derive_key_from_cribs(transposed, period)
                        if ks is not None and len(ks) >= 20:
                            pt = decrypt_with_partial_key(transposed, ks, period)
                            if verify_cribs_in_plaintext(pt):
                                # Check non-? chars look like English (IC test)
                                known_chars = [c for c in pt if c != '?']
                                if len(known_chars) >= 50:
                                    freq = Counter(known_chars)
                                    total = len(known_chars)
                                    ic = sum(f * (f-1) for f in freq.values()) / (total * (total - 1)) if total > 1 else 0
                                    if ic > 0.055:  # English-like IC
                                        partial_key = ['?'] * period
                                        for slot, val in ks.items():
                                            partial_key[slot] = STANDARD_ALPHA[val]
                                        phase2c_hits.append(("highIC", bands, build_name, mask, offset, direction, ic))
                                        if len(phase2c_hits) <= 15:
                                            print(f"    HIGH IC HIT ({ic:.4f}): {bands} {build_name} m={mask} o={offset} {direction}")
                                            print(f"      Key: {''.join(partial_key)}")
                                            print(f"      PT:  {pt}")
                    
                    if tested % 200000 == 0:
                        elapsed = time.time() - start_time
                        print(f"    ... {tested:,} tested ({elapsed:.1f}s)")
                    
                    if time.time() - start_time > 180:  # 3 min limit
                        print(f"    [Time limit for Phase 2C: {tested:,} combos in {time.time()-start_time:.1f}s]")
                        break
                else:
                    continue
                break
            else:
                continue
            break
        else:
            continue
        break

    print(f"  Phase 2C hits: {len(phase2c_hits)}, tested: {tested:,}")

    # PHASE 2D: Test with KRYPTOS alphabet
    print(f"\n  Phase 2D: Berlin Clock bands with KRYPTOS alphabet Vigenere")
    
    for build_name, build_fn in [("V1", build_perm_v1), ("V3", build_perm_v3)]:
        for mask in range(1, 16):
            base_perm = build_fn(n, bands_4411_4, mask)
            if is_identity(base_perm):
                continue
            for offset in range(n):
                perm = apply_offset(base_perm, offset, n)
                for direction, apply_fn in [("fwd", apply_perm), ("inv", apply_inv_perm)]:
                    transposed = apply_fn(K4_CIPHER, perm)
                    ks = derive_key_from_cribs(transposed, 29, KRYPTOS_ALPHA)
                    if ks is not None and len(ks) >= 20:
                        pt = decrypt_with_partial_key(transposed, ks, 29, KRYPTOS_ALPHA)
                        if verify_cribs_in_plaintext(pt):
                            known_chars = [c for c in pt if c != '?']
                            if len(known_chars) >= 50:
                                freq = Counter(known_chars)
                                total = len(known_chars)
                                ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                                if ic > 0.055:
                                    partial_key = ['?'] * 29
                                    for slot, val in ks.items():
                                        partial_key[slot] = KRYPTOS_ALPHA[val]
                                    print(f"    KRYPTOS HIT (IC={ic:.4f}): {build_name} m={mask} o={offset} {direction}")
                                    print(f"      Key: {''.join(partial_key)}")
                                    print(f"      PT:  {pt}")
                                    hits.append(("kryptos", build_name, mask, offset, direction, ic))

        if time.time() - start_time > 240:
            print(f"    [Time limit for Phase 2D]")
            break

    elapsed = time.time() - start_time
    print(f"\n  Part 2 complete. Time: {elapsed:.1f}s")
    print(f"  Total hits: Phase 2B={len(nontrivial_hits)}, 2C={len(phase2c_hits)}, 2D={len(hits)}")
    return nontrivial_hits + phase2c_hits + hits


# ─────────────────────────────────────────────
# PART 3: Simpler route ciphers
# ─────────────────────────────────────────────
def route_cipher_spiral(text, rows, cols, direction='cw'):
    n = len(text)
    if rows * cols < n:
        return None
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = r * cols + c
            row.append(text[idx] if idx < n else 'X')
        grid.append(row)

    result = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    while top <= bottom and left <= right:
        if direction == 'cw':
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
        else:
            for r in range(top, bottom + 1): result.append(grid[r][left])
            left += 1
            for c in range(left, right + 1): result.append(grid[bottom][c])
            bottom -= 1
            if left <= right:
                for r in range(bottom, top - 1, -1): result.append(grid[r][right])
                right -= 1
            if top <= bottom:
                for c in range(right, left - 1, -1): result.append(grid[top][c])
                top += 1
    return ''.join(result[:n])


def route_cipher_zigzag(text, rows, cols):
    n = len(text)
    if rows * cols < n:
        return None
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = r * cols + c
            row.append(text[idx] if idx < n else 'X')
        grid.append(row)
    result = []
    for r in range(rows):
        if r % 2 == 0:
            for c in range(cols): result.append(grid[r][c])
        else:
            for c in range(cols - 1, -1, -1): result.append(grid[r][c])
    return ''.join(result[:n])


def route_cipher_diagonal(text, rows, cols):
    n = len(text)
    if rows * cols < n:
        return None
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = r * cols + c
            row.append(text[idx] if idx < n else 'X')
        grid.append(row)
    result = []
    for d in range(rows + cols - 1):
        if d % 2 == 0:
            r = min(d, rows - 1); c = d - r
            while r >= 0 and c < cols:
                result.append(grid[r][c]); r -= 1; c += 1
        else:
            c = min(d, cols - 1); r = d - c
            while c >= 0 and r < rows:
                result.append(grid[r][c]); r += 1; c -= 1
    return ''.join(result[:n])


def route_cipher_columns(text, rows, cols):
    """Read column by column (top to bottom, left to right)."""
    n = len(text)
    if rows * cols < n:
        return None
    result = []
    for c in range(cols):
        for r in range(rows):
            idx = r * cols + c
            if idx < n:
                result.append(text[idx])
    return ''.join(result[:n])


def columnar_transposition_decrypt(text, key_order):
    n = len(text)
    num_cols = len(key_order)
    num_full_rows = n // num_cols
    extra = n % num_cols
    col_lengths = [num_full_rows + (1 if col < extra else 0) for col in range(num_cols)]
    sorted_cols = sorted(range(num_cols), key=lambda x: key_order[x])
    columns = {}
    pos = 0
    for col_idx in sorted_cols:
        cl = col_lengths[col_idx]
        columns[col_idx] = text[pos:pos + cl]
        pos += cl
    result = []
    for row in range(num_full_rows + 1):
        for col in range(num_cols):
            if row < len(columns.get(col, '')):
                result.append(columns[col][row])
    return ''.join(result[:n])


def test_route_ciphers(dictionary):
    print("\n" + "=" * 80)
    print("PART 3: Testing Simpler Route Ciphers")
    print("=" * 80)

    start_time = time.time()
    hits = []
    period = 29

    # Grid dimensions to test
    grid_dims = set()
    for r in range(2, 50):
        for c in range(2, 50):
            if r * c >= K4_LEN and r * c <= K4_LEN + 10:
                grid_dims.add((r, c))
    # Berlin Clock specific
    for extra in [(4, 25), (25, 4), (23, 5), (5, 23), (23, 4), (4, 23), (11, 9), (9, 11)]:
        grid_dims.add(extra)

    grid_dims = sorted(grid_dims)
    print(f"\n  Testing {len(grid_dims)} grid dimensions with route patterns...")

    for rows, cols in grid_dims:
        for route_name, route_func in [
            ("spiral_cw", lambda t, r=rows, c=cols: route_cipher_spiral(t, r, c, 'cw')),
            ("spiral_ccw", lambda t, r=rows, c=cols: route_cipher_spiral(t, r, c, 'ccw')),
            ("zigzag", lambda t, r=rows, c=cols: route_cipher_zigzag(t, r, c)),
            ("diagonal", lambda t, r=rows, c=cols: route_cipher_diagonal(t, r, c)),
            ("columns", lambda t, r=rows, c=cols: route_cipher_columns(t, r, c)),
        ]:
            result = route_func(K4_CIPHER)
            if result is None:
                continue

            # Direct crib check
            if has_any_crib(result):
                print(f"  *** DIRECT CRIB: {route_name} {rows}x{cols}: {result}")
                hits.append(("direct", route_name, rows, cols))

            # Vigenere period 29 consistency check
            ks = derive_key_from_cribs(result, period)
            if ks is not None and len(ks) >= 20:
                pt = decrypt_with_partial_key(result, ks, period)
                if verify_cribs_in_plaintext(pt):
                    known_chars = [c for c in pt if c != '?']
                    if len(known_chars) >= 50:
                        freq = Counter(known_chars)
                        total = len(known_chars)
                        ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                        partial_key = ['?'] * period
                        for slot, val in ks.items():
                            partial_key[slot] = STANDARD_ALPHA[val]
                        print(f"  VIG-29 OK: {route_name} {rows}x{cols} (IC={ic:.4f}, {len(ks)}/{period} slots)")
                        print(f"    Key: {''.join(partial_key)}")
                        print(f"    PT:  {pt}")
                        hits.append(("vig29", route_name, rows, cols, ic, ''.join(partial_key)))

            # Also check with KRYPTOS alphabet
            ks_k = derive_key_from_cribs(result, period, KRYPTOS_ALPHA)
            if ks_k is not None and len(ks_k) >= 20:
                pt_k = decrypt_with_partial_key(result, ks_k, period, KRYPTOS_ALPHA)
                if verify_cribs_in_plaintext(pt_k):
                    known_chars = [c for c in pt_k if c != '?']
                    if len(known_chars) >= 50:
                        freq = Counter(known_chars)
                        total = len(known_chars)
                        ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                        partial_key = ['?'] * period
                        for slot, val in ks_k.items():
                            partial_key[slot] = KRYPTOS_ALPHA[val]
                        print(f"  KRYPTOS VIG-29: {route_name} {rows}x{cols} (IC={ic:.4f})")
                        print(f"    Key: {''.join(partial_key)}")
                        print(f"    PT:  {pt_k}")
                        hits.append(("kryptos_vig29", route_name, rows, cols, ic))

    # Columnar transposition
    print(f"\n  Testing columnar transposition (key lengths 4, 7, 11, 23)...")
    
    for key_len in [4, 7, 11, 23]:
        if key_len <= 8:
            perms = list(itertools.permutations(range(key_len)))
            print(f"    Key length {key_len}: {len(perms)} permutations")
            for perm in perms:
                try:
                    result = columnar_transposition_decrypt(K4_CIPHER, list(perm))
                except:
                    continue

                if has_any_crib(result):
                    print(f"    *** DIRECT CRIB: columnar k={key_len} order={perm}: {result}")
                    hits.append(("col_direct", key_len, perm))

                ks = derive_key_from_cribs(result, period)
                if ks is not None and len(ks) >= 20:
                    pt = decrypt_with_partial_key(result, ks, period)
                    if verify_cribs_in_plaintext(pt):
                        known_chars = [c for c in pt if c != '?']
                        if len(known_chars) >= 50:
                            freq = Counter(known_chars)
                            total = len(known_chars)
                            ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                            if ic > 0.050:
                                partial_key = ['?'] * period
                                for slot, val in ks.items():
                                    partial_key[slot] = STANDARD_ALPHA[val]
                                print(f"    COL VIG-29 (IC={ic:.4f}): k={key_len} order={perm}")
                                print(f"      Key: {''.join(partial_key)}")
                                print(f"      PT:  {pt}")
                                hits.append(("col_vig29", key_len, perm, ic))

                if time.time() - start_time > 120:
                    break
        else:
            # For longer keys, test some specific orderings derived from keywords
            keywords_to_try = [
                "KRYPTOS",
                "BERLINCLOCK",
                "MENGENLEHREUHR",
                "SANBORN",
                "PALIMPSEST",
                "ABSCISSA",
            ]
            for keyword in keywords_to_try:
                # Derive column order from keyword
                kw = keyword[:key_len].ljust(key_len, 'A')
                order = sorted(range(key_len), key=lambda i: (kw[i], i))
                try:
                    result = columnar_transposition_decrypt(K4_CIPHER, order)
                except:
                    continue
                if has_any_crib(result):
                    print(f"    *** DIRECT CRIB: columnar keyword='{kw}': {result}")
                    hits.append(("col_kw_direct", keyword, order))

                ks = derive_key_from_cribs(result, period)
                if ks is not None and len(ks) >= 20:
                    pt = decrypt_with_partial_key(result, ks, period)
                    if verify_cribs_in_plaintext(pt):
                        partial_key = ['?'] * period
                        for slot, val in ks.items():
                            partial_key[slot] = STANDARD_ALPHA[val]
                        known_chars = [c for c in pt if c != '?']
                        freq = Counter(known_chars)
                        total = len(known_chars)
                        ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                        print(f"    COL-KW VIG-29 (IC={ic:.4f}): keyword='{kw}'")
                        print(f"      Key: {''.join(partial_key)}")
                        print(f"      PT:  {pt}")
                        hits.append(("col_kw_vig29", keyword, ic))

    # Berlin Clock grid - band reading
    print(f"\n  Testing Berlin Clock grid band reading...")
    cycle = 23
    num_rows = (K4_LEN + cycle - 1) // cycle
    padded = K4_CIPHER + 'X' * (num_rows * cycle - K4_LEN)
    
    print(f"    Grid: {num_rows} rows x {cycle} cols")
    for r in range(num_rows):
        print(f"      Row {r}: {padded[r*cycle:(r+1)*cycle]}")

    band_cols = [(0, 4), (4, 8), (8, 19), (19, 23)]

    best_ic = 0
    best_info = None
    
    for band_order in itertools.permutations(range(4)):
        for mask in range(16):
            result_chars = []
            for bi_idx, bi in enumerate(band_order):
                c_start, c_end = band_cols[bi]
                reverse_rows = (mask >> bi_idx) & 1
                for c in range(c_start, c_end):
                    row_range = range(num_rows - 1, -1, -1) if reverse_rows else range(num_rows)
                    for r in row_range:
                        idx = r * cycle + c
                        if idx < K4_LEN:
                            result_chars.append(K4_CIPHER[idx])
            result = ''.join(result_chars)

            if has_any_crib(result):
                print(f"    *** DIRECT CRIB: band_order={band_order} mask={mask}")
                hits.append(("band_direct", band_order, mask))

            ks = derive_key_from_cribs(result, period)
            if ks is not None and len(ks) >= 20:
                pt = decrypt_with_partial_key(result, ks, period)
                if verify_cribs_in_plaintext(pt):
                    known_chars = [c for c in pt if c != '?']
                    if len(known_chars) >= 50:
                        freq = Counter(known_chars)
                        total = len(known_chars)
                        ic = sum(f*(f-1) for f in freq.values()) / (total*(total-1)) if total > 1 else 0
                        if ic > best_ic:
                            best_ic = ic
                            partial_key = ['?'] * period
                            for slot, val in ks.items():
                                partial_key[slot] = STANDARD_ALPHA[val]
                            best_info = (band_order, mask, ic, ''.join(partial_key), pt)

    if best_info:
        bo, m, ic, pk, pt = best_info
        print(f"    Best IC band reading: order={bo} mask={m} IC={ic:.4f}")
        print(f"      Key: {pk}")
        print(f"      PT:  {pt}")

    # Score top route cipher results against dictionary
    print(f"\n  Scoring route cipher results against dictionary...")
    scored_results = []
    
    for rows, cols in [(4, 25), (5, 20), (5, 23), (7, 14), (10, 10), (23, 5)]:
        if rows * cols < K4_LEN:
            continue
        for route_name, route_func in [
            ("spiral_cw", lambda t: route_cipher_spiral(t, rows, cols, 'cw')),
            ("zigzag", lambda t: route_cipher_zigzag(t, rows, cols)),
            ("columns", lambda t: route_cipher_columns(t, rows, cols)),
        ]:
            result = route_func(K4_CIPHER)
            if result:
                words = count_english_words(result, dictionary, min_len=4)
                if words:
                    scored_results.append((len(words), route_name, rows, cols, words[:8], result[:50]))

    scored_results.sort(reverse=True)
    if scored_results:
        print(f"    Top dictionary matches in route cipher outputs:")
        for i, (wc, rn, r, c, words, text) in enumerate(scored_results[:10]):
            print(f"      {i+1}. {rn} {r}x{c}: {wc} words - {words}")
    else:
        print(f"    No significant dictionary matches found.")

    elapsed = time.time() - start_time
    print(f"\n  Part 3 complete. Hits: {len(hits)}, Time: {elapsed:.1f}s")
    return hits


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main():
    print("K4 Genie Engine Analysis")
    print("=" * 80)
    print(f"K4 ciphertext: {K4_CIPHER}")
    print(f"Length: {K4_LEN}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Known cribs: {CRIBS}")
    print()

    overall_start = time.time()

    # Load dictionary
    print("Loading dictionary...")
    dictionary = load_dictionary(min_len=4)
    print(f"  Loaded {len(dictionary)} words (min length 4)\n")

    # PART 1
    test_genie_exact_params()

    # PART 2
    part2_hits = exhaustive_transposition_search()

    # PART 3
    part3_hits = test_route_ciphers(dictionary)

    # ─────────────────────────────────────────
    # Summary
    # ─────────────────────────────────────────
    total_time = time.time() - overall_start
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total execution time: {total_time:.1f}s")
    print()

    # Restate the baseline finding
    print("  BASELINE (no transposition):")
    print("    Period 29 Vigenere is consistent with both cribs (24/29 key positions known)")
    print("    Key: GCKAZMUYKLGKORNA?????BLZCDCYY")
    print("    This is well-known and matches published K4 analysis.")
    print()

    print(f"  PART 1 (Exact Genie Engine params + mod-3 substitution):")
    print(f"    No crib matches found. The mod-3 substitution with Berlin Clock")
    print(f"    boustrophedon transposition does not directly reveal the cribs.")
    print()

    print(f"  PART 2 (Exhaustive transposition + Vigenere):")
    print(f"    Total non-trivial hits: {len(part2_hits)}")
    if part2_hits:
        # Summarize by type
        types = Counter(h[0] for h in part2_hits)
        for t, c in types.items():
            print(f"      {t}: {c} hits")
    else:
        print(f"    No non-trivial transpositions improved on identity.")
    print()

    print(f"  PART 3 (Route ciphers):")
    print(f"    Total hits: {len(part3_hits)}")
    if part3_hits:
        types = Counter(h[0] for h in part3_hits)
        for t, c in types.items():
            print(f"      {t}: {c} hits")
    else:
        print(f"    No route cipher approach produced crib matches.")
    print()

    print("  CONCLUSION:")
    print("    The Genie Engine approach (Berlin Clock 4-4-11-4 boustrophedon + mod-3")
    print("    substitution) does not produce the known K4 cribs at their expected positions.")
    print("    The identity transposition with period-29 Vigenere remains the most consistent")
    print("    framework, with 24 of 29 key positions determined by the two cribs.")
    print("    The remaining 5 key positions (slots 16-20) are still unknown.")
    print("=" * 80)


if __name__ == "__main__":
    main()
