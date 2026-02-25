#!/usr/bin/env python3
"""
K4 Cardan Grille / Physical Mask / Selection Cipher Overlay Analysis

Tests the hypothesis that the Vigenere output contains real plaintext
MIXED with null/filler characters, and a mask or grille selects which
characters are the real message.

Based on Scheidt's clue: "masking technique" - "I disguise the English language"
"""

import math
import os
import sys
from itertools import combinations, product
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Best full Vigenere key (period 29)
BEST_KEY = "OYNKYELYOIECBAQKFANINRDUMRIYW"
# Vigenere output with this key
VIG_OUTPUT = "KSARNQAPBZDBKZELSTIMPEASTNORTHEASTQGUZOUAFZFELLSAGPSOZQUGDMGKFSBERLINCLOCKHOLDOWQULCKEPJFYANKCAYF"

# Known crib positions
CRIB_POINT = (16, 20)          # POINT
CRIB_EASTNORTHEAST = (21, 33)  # EASTNORTHEAST
CRIB_BERLINCLOCK = (63, 73)    # BERLINCLOCK

# Non-crib segments
SEG_A = VIG_OUTPUT[0:16]       # KSARNQAPBZDBKZEL (positions 0-15)
SEG_B = VIG_OUTPUT[34:63]      # QGUZOUAFZFELLSAGPSOZQUGDMGKFS (positions 34-62)
SEG_C = VIG_OUTPUT[74:97]      # HOLDOWQULCKEPJFYANKCAYF (positions 74-96)

# Key as numbers (KRYPTOS alphabet)
KEY_STR = BEST_KEY
KEY_NUMS = [KRYPTOS_ALPHA.index(c) for c in KEY_STR]

QUADGRAM_FILE = "/home/user/polyalphabetic/english_quadgrams.txt"
WORDLIST_FILE = "/home/user/polyalphabetic/OxfordEnglishWords.txt"

# ============================================================
# QUADGRAM SCORER
# ============================================================

class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        with open(filepath) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    gram, count = parts[0], int(parts[1])
                    self.quadgrams[gram] = count
                    self.total += count
        self.floor = math.log10(0.01 / self.total)

    def score(self, text):
        text = text.upper()
        if len(text) < 4:
            return -999999
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            if gram in self.quadgrams:
                s += math.log10(self.quadgrams[gram] / self.total)
            else:
                s += self.floor
        return s

    def score_per_char(self, text):
        if len(text) < 4:
            return -99
        return self.score(text) / (len(text) - 3)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def load_wordlist():
    words = set()
    if os.path.exists(WORDLIST_FILE):
        with open(WORDLIST_FILE) as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 3:
                    words.add(w)
    # Add common small words
    for w in ["A", "I", "AN", "AT", "BE", "BY", "DO", "GO", "HE", "IF", "IN",
              "IS", "IT", "ME", "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP",
              "US", "WE", "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
              "CAN", "HAD", "HER", "WAS", "ONE", "OUR", "OUT"]:
        words.add(w)
    return words

def kryptos_decrypt_char(c, k):
    """Decrypt single char: plaintext = (cipher - key) mod 26 in KRYPTOS alphabet."""
    ci = KRYPTOS_ALPHA.index(c)
    ki = KRYPTOS_ALPHA.index(k)
    pi = (ci - ki) % 26
    return KRYPTOS_ALPHA[pi]

def kryptos_shift(c, shift):
    """Shift a character by 'shift' positions in KRYPTOS alphabet."""
    ci = KRYPTOS_ALPHA.index(c)
    return KRYPTOS_ALPHA[(ci + shift) % 26]

def is_prime(n):
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def fibonacci_positions(max_pos):
    """Generate Fibonacci numbers up to max_pos."""
    fibs = []
    a, b = 1, 1
    while a <= max_pos:
        fibs.append(a)
        a, b = b, a + b
    return fibs

def triangular_positions(max_pos):
    """Generate triangular numbers up to max_pos."""
    tri = []
    n = 1
    t = 1
    while t <= max_pos:
        tri.append(t)
        n += 1
        t = n * (n + 1) // 2
    return tri

def find_english_words(text, wordlist, min_len=4):
    """Find all English words contained in text."""
    text = text.upper()
    found = []
    for length in range(min_len, min(len(text) + 1, 20)):
        for i in range(len(text) - length + 1):
            substr = text[i:i+length]
            if substr in wordlist:
                found.append((i, substr))
    return found

def extract_positions(text, positions):
    """Extract characters at given positions from text."""
    return ''.join(text[p] for p in positions if 0 <= p < len(text))


# ============================================================
# SECTION 1: GRILLE/MASK PATTERN SEARCH
# ============================================================

def test_mask_patterns(scorer):
    print("=" * 80)
    print("SECTION 1: GRILLE/MASK PATTERN SEARCH")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # 1a. Every Nth character with various offsets
    print("\n--- 1a. Every Nth Character ---")
    for n in range(2, 8):
        for offset in range(n):
            extracted = ''.join(text[i] for i in range(offset, len(text), n))
            sc = scorer.score_per_char(extracted)
            results.append((sc, f"Every {n}th char, offset={offset}", extracted))
            if sc > -7.0:
                print(f"  N={n}, offset={offset}: {extracted} (score: {sc:.3f})")

    # 1b. Key value even/odd positions
    print("\n--- 1b. Key Value Even/Odd Positions ---")
    even_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] % 2 == 0]
    odd_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] % 2 == 1]
    for name, positions in [("key_even", even_pos), ("key_odd", odd_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"Positions where key is {name}", extracted))
        print(f"  {name}: {extracted} (len={len(extracted)}, score: {sc:.3f})")

    # 1c. Key value < 13 vs >= 13
    print("\n--- 1c. Key Value < 13 vs >= 13 ---")
    low_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] < 13]
    high_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] >= 13]
    for name, positions in [("key<13", low_pos), ("key>=13", high_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"Positions where {name}", extracted))
        print(f"  {name}: {extracted} (len={len(extracted)}, score: {sc:.3f})")

    # 1d. Positions modulo various numbers
    print("\n--- 1d. Positions Modulo Patterns ---")
    for mod in range(2, 10):
        for remainder_set_size in range(1, mod):
            for remainder_combo in combinations(range(mod), remainder_set_size):
                positions = [i for i in range(len(text)) if i % mod in remainder_combo]
                if len(positions) < 8:
                    continue
                extracted = extract_positions(text, positions)
                sc = scorer.score_per_char(extracted)
                results.append((sc, f"pos%{mod} in {remainder_combo}", extracted))
                if sc > -6.5:
                    print(f"  pos%{mod} in {remainder_combo}: {extracted[:50]}... (score: {sc:.3f})")

    # 1e. Prime positions
    print("\n--- 1e. Prime Number Positions ---")
    prime_pos = [i for i in range(len(text)) if is_prime(i)]
    non_prime_pos = [i for i in range(len(text)) if not is_prime(i)]
    for name, positions in [("prime", prime_pos), ("non-prime", non_prime_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"{name} positions", extracted))
        print(f"  {name}: {extracted} (len={len(extracted)}, score: {sc:.3f})")

    # 1f. Triangular number positions
    print("\n--- 1f. Triangular Number Positions ---")
    tri_pos = triangular_positions(96)
    extracted = extract_positions(text, tri_pos)
    sc = scorer.score_per_char(extracted)
    results.append((sc, "triangular positions", extracted))
    print(f"  Triangular: {extracted} (score: {sc:.3f})")
    # Complement
    tri_set = set(tri_pos)
    comp = [i for i in range(len(text)) if i not in tri_set]
    extracted_c = extract_positions(text, comp)
    sc_c = scorer.score_per_char(extracted_c)
    results.append((sc_c, "non-triangular positions", extracted_c))
    print(f"  Non-triangular: {extracted_c[:50]}... (score: {sc_c:.3f})")

    # 1g. Fibonacci positions
    print("\n--- 1g. Fibonacci Positions ---")
    fib_pos = fibonacci_positions(96)
    extracted = extract_positions(text, fib_pos)
    sc = scorer.score_per_char(extracted)
    results.append((sc, "fibonacci positions", extracted))
    print(f"  Fibonacci: {extracted} (score: {sc:.3f})")

    # 1h. Positions where key char matches certain patterns
    print("\n--- 1h. Key Character Consonant/Vowel ---")
    vowels = set("AEIOU")
    vowel_pos = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] in vowels]
    cons_pos = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] not in vowels]
    for name, positions in [("key_vowel", vowel_pos), ("key_consonant", cons_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"Positions where {name}", extracted))
        print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    # Print top results
    results.sort(reverse=True)
    print("\n--- TOP 20 MASK PATTERNS ---")
    for sc, desc, ext in results[:20]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# SECTION 2: GRID-BASED CARDAN GRILLE
# ============================================================

def test_grid_grille(scorer):
    print("\n" + "=" * 80)
    print("SECTION 2: GRID-BASED CARDAN GRILLE")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # Test various grid dimensions
    grid_dims = [
        (7, 14), (14, 7),
        (10, 10),
        (8, 13), (13, 8),
        (11, 9), (9, 11),
        (7, 7),   # 49 - half of 97
        (4, 25), (5, 20),
        (29, 4), (4, 29),  # key period related
    ]

    for rows, cols in grid_dims:
        total = rows * cols
        if total < len(text):
            padded = text + 'X' * (total - len(text))
        else:
            padded = text[:total]

        # Fill grid
        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                idx = r * cols + c
                if idx < len(padded):
                    row.append(padded[idx])
                else:
                    row.append('X')
            grid.append(row)

        # Read column-wise
        col_read = ''
        for c in range(cols):
            for r in range(rows):
                if r * cols + c < len(text):
                    col_read += grid[r][c]
        sc = scorer.score_per_char(col_read)
        results.append((sc, f"Grid {rows}x{cols} col-read", col_read))

        # Read diagonal
        diag_read = ''
        for d in range(rows + cols - 1):
            for r in range(rows):
                c = d - r
                if 0 <= c < cols and r * cols + c < len(text):
                    diag_read += grid[r][c]
        sc = scorer.score_per_char(diag_read)
        results.append((sc, f"Grid {rows}x{cols} diag-read", diag_read))

        # Read spiral (clockwise from outside)
        def spiral_read(grid, rows, cols):
            result = []
            top, bottom, left, right = 0, rows - 1, 0, cols - 1
            while top <= bottom and left <= right:
                for c in range(left, right + 1):
                    if top * cols + c < len(text):
                        result.append(grid[top][c])
                top += 1
                for r in range(top, bottom + 1):
                    if r * cols + right < len(text):
                        result.append(grid[r][right])
                right -= 1
                if top <= bottom:
                    for c in range(right, left - 1, -1):
                        if bottom * cols + c < len(text):
                            result.append(grid[bottom][c])
                    bottom -= 1
                if left <= right:
                    for r in range(bottom, top - 1, -1):
                        if r * cols + left < len(text):
                            result.append(grid[r][left])
                    left += 1
            return ''.join(result)

        spiral = spiral_read(grid, rows, cols)
        sc = scorer.score_per_char(spiral)
        results.append((sc, f"Grid {rows}x{cols} spiral", spiral))

        # Test simple Cardan grille: checkerboard pattern
        for parity in [0, 1]:
            extracted = ''
            for r in range(rows):
                for c in range(cols):
                    if (r + c) % 2 == parity:
                        idx = r * cols + c
                        if idx < len(text):
                            extracted += text[idx]
            sc = scorer.score_per_char(extracted)
            results.append((sc, f"Grid {rows}x{cols} checkerboard p={parity}", extracted))

    # Special: 29-column layout (key period)
    print("\n--- Key-Period Grid (29 columns) ---")
    rows29 = math.ceil(len(text) / 29)
    grid29 = []
    for r in range(rows29):
        row = []
        for c in range(29):
            idx = r * 29 + c
            if idx < len(text):
                row.append(text[idx])
            else:
                row.append('.')
        grid29.append(row)
        print(f"  Row {r}: {''.join(row)}")

    # Read columns of the 29-col grid
    col_read_29 = ''
    for c in range(29):
        for r in range(rows29):
            idx = r * 29 + c
            if idx < len(text):
                col_read_29 += text[idx]
    sc = scorer.score_per_char(col_read_29)
    results.append((sc, "Grid 29-col column-read", col_read_29))
    print(f"  Column-read: {col_read_29} (score: {sc:.3f})")

    # Print top results
    results.sort(reverse=True)
    print("\n--- TOP 15 GRID READINGS ---")
    for sc, desc, ext in results[:15]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# SECTION 3: KNOWN TEXT EXTRACTION - CAESAR ON NON-CRIB
# ============================================================

def test_caesar_on_noncrib(scorer):
    print("\n" + "=" * 80)
    print("SECTION 3: CAESAR SHIFTS ON NON-CRIB POSITIONS")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # Non-crib positions
    crib_positions = set(range(16, 34)) | set(range(63, 74))  # POINT+EASTNORTHEAST + BERLINCLOCK
    non_crib_positions = [i for i in range(len(text)) if i not in crib_positions]
    non_crib_text = extract_positions(text, non_crib_positions)
    print(f"  Non-crib text ({len(non_crib_text)} chars): {non_crib_text}")

    # Also define the three segments
    segments = {
        "Segment A (0-15)": SEG_A,
        "Segment B (34-62)": SEG_B,
        "Segment C (74-96)": SEG_C,
        "All non-crib": non_crib_text,
    }

    for seg_name, seg_text in segments.items():
        print(f"\n  --- {seg_name}: {seg_text} ---")
        best_for_seg = []
        for shift in range(26):
            shifted = ''.join(kryptos_shift(c, shift) for c in seg_text)
            sc = scorer.score_per_char(shifted)
            best_for_seg.append((sc, shift, shifted))
        best_for_seg.sort(reverse=True)
        for sc, shift, shifted in best_for_seg[:5]:
            print(f"    Shift {shift:2d}: {shifted[:50]} (score: {sc:.3f})")
        results.extend([(sc, f"{seg_name} shift={sh}", txt) for sc, sh, txt in best_for_seg[:3]])

    # Also try Vigenere with short keys on non-crib
    print("\n  --- Short Vigenere Keys on Non-Crib Text ---")
    best_vig = []
    for period in [2, 3, 4, 5]:
        for key_combo in product(range(26), repeat=period):
            shifted = ''
            for i, c in enumerate(non_crib_text):
                shifted += kryptos_shift(c, key_combo[i % period])
            sc = scorer.score_per_char(shifted)
            if sc > -7.0:
                key_str = ''.join(KRYPTOS_ALPHA[k] for k in key_combo)
                best_vig.append((sc, f"Vig period={period} key={key_str}", shifted))
    best_vig.sort(reverse=True)
    print(f"  Found {len(best_vig)} results with score > -7.0")
    for sc, desc, shifted in best_vig[:10]:
        print(f"    {sc:.3f}  {desc}: {shifted[:50]}")
    results.extend(best_vig[:5])

    return results


# ============================================================
# SECTION 4: INTERLEAVING TESTS
# ============================================================

def test_interleaving(scorer):
    print("\n" + "=" * 80)
    print("SECTION 4: INTERLEAVING TESTS")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # 4a. Simple even/odd split
    print("\n--- 4a. Even/Odd Position Split ---")
    even_chars = ''.join(text[i] for i in range(0, len(text), 2))
    odd_chars = ''.join(text[i] for i in range(1, len(text), 2))
    for name, chars in [("even positions", even_chars), ("odd positions", odd_chars)]:
        sc = scorer.score_per_char(chars)
        results.append((sc, name, chars))
        print(f"  {name}: {chars} (score: {sc:.3f})")

    # 4b. Every 3rd, 4th, 5th position
    print("\n--- 4b. Every Nth Position Split ---")
    for n in [3, 4, 5, 6]:
        for offset in range(n):
            chars = ''.join(text[i] for i in range(offset, len(text), n))
            sc = scorer.score_per_char(chars)
            results.append((sc, f"every {n}th offset={offset}", chars))
            if sc > -7.5:
                print(f"  N={n}, offset={offset}: {chars} (score: {sc:.3f})")

    # 4c. Split by key value pattern
    print("\n--- 4c. Key-Derived Split ---")
    # Group positions by key value mod N
    for mod in [2, 3, 4]:
        groups = {r: [] for r in range(mod)}
        for i in range(len(text)):
            kv = KEY_NUMS[i % len(KEY_NUMS)]
            groups[kv % mod].append(i)
        for r in range(mod):
            chars = extract_positions(text, groups[r])
            sc = scorer.score_per_char(chars)
            results.append((sc, f"key_val%{mod}=={r}", chars))
            print(f"  key_val%{mod}=={r}: {chars[:50]}... (len={len(chars)}, score: {sc:.3f})")

    # 4d. Alternating: take N, skip M
    print("\n--- 4d. Take N / Skip M ---")
    for take in range(1, 6):
        for skip in range(1, 6):
            if take == 1 and skip == 1:
                continue  # already covered
            positions = []
            i = 0
            while i < len(text):
                for t in range(take):
                    if i + t < len(text):
                        positions.append(i + t)
                i += take + skip
            chars = extract_positions(text, positions)
            if len(chars) < 8:
                continue
            sc = scorer.score_per_char(chars)
            results.append((sc, f"take{take}_skip{skip}", chars))
            if sc > -7.0:
                print(f"  take{take}_skip{skip}: {chars[:50]}... (score: {sc:.3f})")

    # 4e. Two-message interleave test: if we know EASTNORTHEAST and BERLINCLOCK
    # positions, what pattern separates "real" from "null"?
    print("\n--- 4e. Crib-Informed Pattern Analysis ---")
    # Known real positions: 16-33 (POINTEASTNORTHEAST), 63-73 (BERLINCLOCK)
    # Possibly also 74-79 if HOLDOW or similar
    real_positions = list(range(16, 34)) + list(range(63, 74))
    # Check: what pattern do these positions follow?
    print(f"  Known real positions: {real_positions}")
    print(f"  Mod 2 pattern: {[p % 2 for p in real_positions]}")
    print(f"  Mod 3 pattern: {[p % 3 for p in real_positions]}")
    print(f"  Mod 29 pattern: {[p % 29 for p in real_positions]}")

    # What are the key values at real positions?
    real_key_vals = [KEY_NUMS[p % len(KEY_NUMS)] for p in real_positions]
    print(f"  Key values at real positions: {real_key_vals}")
    print(f"  Key value ranges: min={min(real_key_vals)}, max={max(real_key_vals)}")

    results.sort(reverse=True)
    print("\n--- TOP 15 INTERLEAVING RESULTS ---")
    for sc, desc, ext in results[:15]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# SECTION 5: ANALYSIS OF NON-CRIB SEGMENTS
# ============================================================

def test_noncrib_segments(scorer, wordlist):
    print("\n" + "=" * 80)
    print("SECTION 5: NON-CRIB SEGMENT ANALYSIS")
    print("=" * 80)

    segments = {
        "A (0-15)": SEG_A,
        "B (34-62)": SEG_B,
        "C (74-96)": SEG_C,
    }

    results = []

    for seg_name, seg_text in segments.items():
        print(f"\n--- Segment {seg_name}: {seg_text} (len={len(seg_text)}) ---")

        # 5a. Reverse
        rev = seg_text[::-1]
        sc = scorer.score_per_char(rev)
        print(f"  Reverse: {rev} (score: {sc:.3f})")
        results.append((sc, f"Seg {seg_name} reversed", rev))

        # 5b. English words within
        print(f"  English words found:")
        words_found = find_english_words(seg_text, wordlist, min_len=3)
        for pos, word in words_found:
            print(f"    pos {pos}: {word}")
        # Also in reverse
        words_rev = find_english_words(rev, wordlist, min_len=3)
        for pos, word in words_rev:
            print(f"    (rev) pos {pos}: {word}")

        # 5c. Caesar shifts
        print(f"  Best Caesar shifts:")
        best_caesar = []
        for shift in range(26):
            shifted = ''.join(kryptos_shift(c, shift) for c in seg_text)
            sc = scorer.score_per_char(shifted)
            best_caesar.append((sc, shift, shifted))
        best_caesar.sort(reverse=True)
        for sc, shift, shifted in best_caesar[:3]:
            letter = KRYPTOS_ALPHA[shift]
            print(f"    Shift {shift:2d} ({letter}): {shifted} (score: {sc:.3f})")
            results.append((sc, f"Seg {seg_name} Caesar shift={shift}", shifted))

        # 5d. Atbash (reverse alphabet mapping)
        atbash = ''.join(KRYPTOS_ALPHA[25 - KRYPTOS_ALPHA.index(c)] for c in seg_text)
        sc = scorer.score_per_char(atbash)
        print(f"  Atbash: {atbash} (score: {sc:.3f})")
        results.append((sc, f"Seg {seg_name} Atbash", atbash))

        # 5e. ROT13 equivalent (shift 13)
        rot13 = ''.join(kryptos_shift(c, 13) for c in seg_text)
        sc = scorer.score_per_char(rot13)
        print(f"  ROT13: {rot13} (score: {sc:.3f})")

    # 5f. Combine segments differently
    print("\n--- Combined Segment Tests ---")
    combined_orders = [
        ("A+B+C", SEG_A + SEG_B + SEG_C),
        ("C+B+A", SEG_C + SEG_B + SEG_A),
        ("A+C+B", SEG_A + SEG_C + SEG_B),
        ("B+A+C", SEG_B + SEG_A + SEG_C),
        ("B+C+A", SEG_B + SEG_C + SEG_A),
        ("C+A+B", SEG_C + SEG_A + SEG_B),
    ]
    for name, combo in combined_orders:
        sc = scorer.score_per_char(combo)
        results.append((sc, f"Combined {name}", combo))
        print(f"  {name}: {combo[:50]}... (score: {sc:.3f})")

    # 5g. Anagram analysis - letter frequencies
    print("\n--- Letter Frequency Analysis (Non-Crib) ---")
    all_noncrib = SEG_A + SEG_B + SEG_C
    freq = Counter(all_noncrib)
    total = len(all_noncrib)
    print(f"  Total non-crib chars: {total}")
    for char, count in freq.most_common():
        pct = count / total * 100
        print(f"    {char}: {count} ({pct:.1f}%)")

    # English letter frequency comparison
    eng_freq = {'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
                'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
                'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
                'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.2, 'X': 0.2,
                'Q': 0.1, 'Z': 0.1}
    print(f"\n  Chi-squared vs English:")
    chi2 = 0
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(char, 0) / total * 100
        expected = eng_freq.get(char, 0.1)
        chi2 += (observed - expected) ** 2 / expected
    print(f"    Chi-squared: {chi2:.2f}")

    # 5h. Look for words in running text
    print("\n--- Words in Running Non-Crib Text ---")
    all_noncrib_continuous = SEG_A + SEG_B + SEG_C
    words_found = find_english_words(all_noncrib_continuous, wordlist, min_len=4)
    for pos, word in sorted(words_found, key=lambda x: -len(x[1]))[:20]:
        segment = "A" if pos < len(SEG_A) else ("B" if pos < len(SEG_A) + len(SEG_B) else "C")
        print(f"    pos {pos} (seg {segment}): {word}")

    # 5i. Different key offset on each segment
    print("\n--- Per-Segment Optimal Caesar ---")
    for seg_name, seg_text in segments.items():
        best = []
        for shift in range(26):
            shifted = ''.join(kryptos_shift(c, shift) for c in seg_text)
            sc = scorer.score_per_char(shifted)
            best.append((sc, shift, shifted))
        best.sort(reverse=True)
        sc, shift, shifted = best[0]
        print(f"  {seg_name}: best shift={shift} ({KRYPTOS_ALPHA[shift]}): {shifted} (score: {sc:.3f})")

    return results


# ============================================================
# SECTION 6: COORDINATE EXTRACTION
# ============================================================

def test_coordinate_extraction(scorer):
    print("\n" + "=" * 80)
    print("SECTION 6: COORDINATE EXTRACTION")
    print("=" * 80)
    text = VIG_OUTPUT

    # CIA HQ is approximately 38.9517 N, 77.1467 W
    # Kryptos sculpture: 38°57'6.5"N, 77°8'44"W
    # These could be encoded as: 38 57 6 N 77 8 44 W

    # Map letters to numbers (A=1, B=2, ..., Z=26) or (A=0, B=1, ...)
    print("\n--- 6a. Letter-to-Number Mappings ---")

    # Standard A=1
    def letter_to_num_std(c):
        return ord(c) - ord('A') + 1

    # KRYPTOS alphabet position
    def letter_to_num_kryptos(c):
        return KRYPTOS_ALPHA.index(c) + 1

    # Check various position subsets for coordinate-like numbers
    print("\n--- 6b. Searching for 38, 57, 77, 8 in Position Patterns ---")

    # Look at pairs of characters as two-digit numbers
    for mapping_name, mapping_fn in [("standard A=1", letter_to_num_std),
                                      ("KRYPTOS pos", letter_to_num_kryptos)]:
        print(f"\n  Mapping: {mapping_name}")
        nums = [mapping_fn(c) for c in text]
        print(f"  Numeric sequence: {nums[:30]}...")

        # Look for pairs that form 38, 57, 77, 8
        for i in range(len(nums) - 1):
            val = nums[i] * 10 + nums[i+1]
            if val in [38, 57, 77]:
                print(f"    Found {val} at positions {i},{i+1} (chars {text[i]}{text[i+1]})")

        # Single digits
        for i in range(len(nums)):
            if nums[i] == 8:
                print(f"    Found 8 at position {i} (char {text[i]})")

    # Check if non-crib chars encode coordinates when taken as number sequence
    print("\n--- 6c. Non-Crib Chars as Coordinate Digits ---")
    noncrib = SEG_A + SEG_B + SEG_C
    for mapping_name, mapping_fn in [("A=0", lambda c: ord(c) - ord('A')),
                                      ("A=1", letter_to_num_std),
                                      ("KRYPTOS", letter_to_num_kryptos)]:
        nums = [mapping_fn(c) for c in noncrib]
        # Look for sequences like 3-8-5-7 (38.57) or 7-7-0-8 (77.08)
        for i in range(len(nums) - 3):
            n4 = nums[i:i+4]
            # Check various coordinate patterns
            lat = n4[0] * 10 + n4[1] + n4[2] * 0.1 + n4[3] * 0.01
            if 38.0 <= lat <= 39.5:
                print(f"    {mapping_name}: lat-like {lat:.2f} at pos {i} from chars {noncrib[i:i+4]}")
            lon = n4[0] * 10 + n4[1] + n4[2] * 0.1 + n4[3] * 0.01
            if 76.5 <= lon <= 78.0:
                print(f"    {mapping_name}: lon-like {lon:.2f} at pos {i} from chars {noncrib[i:i+4]}")

    # Check every possible extraction of 6-8 digits from positions for coordinates
    print("\n--- 6d. Position-Based Coordinate Encoding ---")
    # Key values might encode digits directly
    print(f"  Key values (mod 10): {[k % 10 for k in KEY_NUMS]}")

    # Check if specific positions spell out coordinates
    # 38°57'N  77°8'W encoded in alphabet positions
    # In KRYPTOS: 3=S, 8=D, 5=A, 7=C -> SDAC?
    # In standard: 3=C, 8=H, 5=E, 7=G -> CHEG?
    target_sequences = {
        "38 57 N": [3, 8, 5, 7],
        "77 08 W": [7, 7, 0, 8],
        "38 57 06": [3, 8, 5, 7, 0, 6],
        "77 08 44": [7, 7, 0, 8, 4, 4],
    }

    for desc, digits in target_sequences.items():
        # Search in key values mod 10
        kv_mod10 = [k % 10 for k in KEY_NUMS]
        for i in range(len(kv_mod10) - len(digits) + 1):
            if kv_mod10[i:i+len(digits)] == digits:
                print(f"    Found '{desc}' in key values mod 10 at position {i}")

    # Also check: do the POSITIONS of the known cribs encode coordinates?
    print("\n--- 6e. Crib Position Analysis ---")
    print(f"  POINT starts at position 16")
    print(f"  EASTNORTHEAST starts at position 21")
    print(f"  BERLINCLOCK starts at position 63")
    print(f"  Position differences: 21-16=5, 63-21=42, 63-16=47")
    print(f"  Note: EAST at 21, NORTH at 25, EAST at 30 -> directions!")
    print(f"  BERLINCLOCK at 63 -> time reference")
    print(f"  POINT at 16 -> location marker")

    # Check if remaining characters modulo operations yield coordinates
    print("\n--- 6f. Digit Extraction from Character Values ---")
    for seg_name, seg_text in [("A", SEG_A), ("B", SEG_B), ("C", SEG_C)]:
        std_nums = [ord(c) - ord('A') for c in seg_text]
        # Take mod 10 to get single digits
        digits = [n % 10 for n in std_nums]
        digit_str = ''.join(str(d) for d in digits)
        print(f"  Segment {seg_name} mod10 digits: {digit_str}")
        # Look for coordinate patterns
        for i in range(len(digit_str) - 3):
            chunk = digit_str[i:i+4]
            if chunk.startswith("38") or chunk.startswith("77") or chunk.startswith("57"):
                print(f"    Possible coord fragment '{chunk}' at digit pos {i}")


# ============================================================
# SECTION 7: ADVANCED GRILLE PATTERNS
# ============================================================

def test_advanced_grille(scorer):
    print("\n" + "=" * 80)
    print("SECTION 7: ADVANCED GRILLE / MASKING PATTERNS")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # 7a. Rotating Cardan grille simulation on square grids
    print("\n--- 7a. Rotating Cardan Grille (Quarter-Turn) ---")

    for size in [5, 6, 7, 8, 10]:
        total = size * size
        if total < 20:
            continue
        # For a rotating Cardan grille, we need to select positions such that
        # each quarter of the grid is read in one rotation
        # We'll try all possible quarter-patterns for small grids

        # Generate quarter positions (top-left quadrant)
        half = (size + 1) // 2
        quarter_size = half * half if size % 2 == 1 else (size // 2) * (size // 2)

        # For each cell in top-left quadrant, it maps to 4 cells (or 1 if center of odd grid)
        def rotate_pos(r, c, n):
            """Rotate position 90 degrees clockwise in an n x n grid."""
            return (c, n - 1 - r)

        quarter_cells = []
        for r in range(half):
            for c in range(half):
                if size % 2 == 1 and r == half - 1 and c == half - 1:
                    continue  # center cell
                positions = [(r, c)]
                cr, cc = r, c
                for _ in range(3):
                    cr, cc = rotate_pos(cr, cc, size)
                    positions.append((cr, cc))
                quarter_cells.append(positions)

        # Try a few random grille patterns by selecting ~1/4 of quarter cells
        if len(quarter_cells) <= 12:
            # For small grids, try selecting some cells
            num_holes = max(1, len(quarter_cells) // 2)
            # Try a systematic subset
            for pattern_idx in range(min(50, 2**len(quarter_cells))):
                # Use pattern_idx as bitmask
                if bin(pattern_idx).count('1') != num_holes:
                    continue
                all_positions = []
                for bit in range(len(quarter_cells)):
                    if pattern_idx & (1 << bit):
                        for r, c in quarter_cells[bit]:
                            idx = r * size + c
                            if idx < len(text):
                                all_positions.append(idx)
                all_positions.sort()
                if len(all_positions) < 8:
                    continue
                extracted = extract_positions(text, all_positions)
                sc = scorer.score_per_char(extracted)
                if sc > -7.0:
                    results.append((sc, f"Cardan {size}x{size} pattern={pattern_idx}", extracted))

        # Simple pattern: read first quarter positions across all 4 rotations
        for rotation_order in [(0, 1, 2, 3), (0, 2, 1, 3), (0, 3, 2, 1)]:
            extracted = ''
            for rot in rotation_order:
                for cells in quarter_cells:
                    r, c = cells[rot]
                    idx = r * size + c
                    if idx < len(text):
                        extracted += text[idx]
            sc = scorer.score_per_char(extracted)
            results.append((sc, f"Cardan {size}x{size} rot_order={rotation_order}", extracted))

    # 7b. Mask based on key character repetitions
    print("\n--- 7b. Key-Derived Masks ---")
    # Characters that appear only once in the key
    key_char_count = Counter(KEY_STR)
    unique_key_chars = {c for c, count in key_char_count.items() if count == 1}
    repeated_key_chars = {c for c, count in key_char_count.items() if count > 1}

    unique_pos = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] in unique_key_chars]
    repeated_pos = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] in repeated_key_chars]

    for name, positions in [("unique_key_char", unique_pos), ("repeated_key_char", repeated_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, name, extracted))
        print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    # 7c. Binary key mask: key value > average
    avg_key = sum(KEY_NUMS) / len(KEY_NUMS)
    above_avg_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] > avg_key]
    below_avg_pos = [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] <= avg_key]
    for name, positions in [("key_above_avg", above_avg_pos), ("key_below_avg", below_avg_pos)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, name, extracted))
        print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    # 7d. Positions where Vigenere output matches ciphertext
    print("\n--- 7d. Cipher-Plaintext Match Positions ---")
    match_pos = [i for i in range(len(text)) if text[i] == K4_CIPHERTEXT[i]]
    nonmatch_pos = [i for i in range(len(text)) if text[i] != K4_CIPHERTEXT[i]]
    print(f"  Matching positions ({len(match_pos)}): {match_pos}")
    if match_pos:
        extracted = extract_positions(text, match_pos)
        print(f"  Matching chars: {extracted}")
    extracted_nm = extract_positions(text, nonmatch_pos)
    sc = scorer.score_per_char(extracted_nm)
    results.append((sc, "non-matching positions", extracted_nm))

    # 7e. XOR-style mask: positions where key XOR position gives specific pattern
    print("\n--- 7e. XOR-Derived Masks ---")
    for threshold in [0, 1]:
        positions = [i for i in range(len(text)) if (KEY_NUMS[i % len(KEY_NUMS)] ^ i) % 2 == threshold]
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"key_XOR_pos mod2=={threshold}", extracted))
        print(f"  key_XOR_pos mod2=={threshold}: {extracted[:50]}... (score: {sc:.3f})")

    # 7f. Mask from the ciphertext itself
    print("\n--- 7f. Ciphertext-Derived Masks ---")
    for threshold in range(13, 14):
        ct_nums = [KRYPTOS_ALPHA.index(c) for c in K4_CIPHERTEXT]
        above_pos = [i for i in range(len(text)) if ct_nums[i] >= threshold]
        below_pos = [i for i in range(len(text)) if ct_nums[i] < threshold]
        for name, positions in [(f"ct>={threshold}", above_pos), (f"ct<{threshold}", below_pos)]:
            extracted = extract_positions(text, positions)
            sc = scorer.score_per_char(extracted)
            results.append((sc, name, extracted))
            print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    results.sort(reverse=True)
    print("\n--- TOP 15 ADVANCED GRILLE RESULTS ---")
    for sc, desc, ext in results[:15]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# SECTION 8: COMPREHENSIVE MASK-THEN-READ TESTS
# ============================================================

def test_mask_then_read(scorer):
    """Test: apply mask, then read the surviving characters for English."""
    print("\n" + "=" * 80)
    print("SECTION 8: BINARY MASK OPTIMIZATION (Crib-Guided)")
    print("=" * 80)
    text = VIG_OUTPUT

    # We know positions 16-33 are real (POINTEASTNORTHEAST) and 63-73 are real (BERLINCLOCK)
    # Use this constraint to search for full masks

    known_real = set(range(16, 34)) | set(range(63, 74))
    known_real_list = sorted(known_real)

    results = []

    # Strategy: for each remaining position, test if adding it improves English score
    # Start with known positions and greedily expand

    print("\n--- 8a. Greedy Mask Expansion from Known Cribs ---")
    remaining = [i for i in range(len(text)) if i not in known_real]

    # Try expanding to include positions 74-96 (HOLDOWQULCKEPJFYANKCAYF)
    # "HOLD" at 74-77 looks promising
    # Check extended crib regions
    for start, end, label in [(74, 80, "HOLDOW"), (74, 97, "full tail")]:
        test_text = extract_positions(text, sorted(known_real | set(range(start, min(end, len(text))))))
        sc = scorer.score_per_char(test_text)
        print(f"  Known + {label}: {test_text[:60]}... (score: {sc:.3f})")

    # 8b. Test if positions 0-15 contain a word when read with different offset
    print("\n--- 8b. Segment A (0-15) Deep Analysis ---")
    seg_a = SEG_A  # KSARNQAPBZDBKZEL
    print(f"  Raw: {seg_a}")
    # Try all 26 shifts
    best = []
    for shift in range(26):
        shifted = ''.join(kryptos_shift(c, shift) for c in seg_a)
        sc = scorer.score_per_char(shifted)
        best.append((sc, shift, shifted))
    best.sort(reverse=True)
    for sc, shift, shifted in best[:5]:
        print(f"    Shift {shift} ({KRYPTOS_ALPHA[shift]}): {shifted} (score: {sc:.3f})")

    # Try reading every other character
    for offset in [0, 1]:
        sub = seg_a[offset::2]
        sc = scorer.score_per_char(sub)
        print(f"    Every 2nd (offset {offset}): {sub} (score: {sc:.3f})")

    # 8c. Test reading positions backward within each segment
    print("\n--- 8c. Segments Read Backward ---")
    for name, seg in [("A", SEG_A), ("B", SEG_B), ("C", SEG_C)]:
        rev = seg[::-1]
        sc = scorer.score_per_char(rev)
        print(f"  Seg {name} reversed: {rev} (score: {sc:.3f})")
        # Also shifted
        for shift in range(26):
            shifted = ''.join(kryptos_shift(c, shift) for c in rev)
            sc2 = scorer.score_per_char(shifted)
            if sc2 > -7.0:
                print(f"    Seg {name} rev+shift {shift}: {shifted} (score: {sc2:.3f})")
                results.append((sc2, f"Seg {name} rev+shift {shift}", shifted))

    # 8d. Full message reconstruction attempts
    print("\n--- 8d. Full Message with Segment C as Continuation ---")
    # Test: cribs + segment C forms a message
    crib_text = "POINTEASTNORTHEAST"
    # BERLINCLOCK + HOLDOWQULCKEPJFYANKCAYF
    end_text = "BERLINCLOCK" + SEG_C
    print(f"  Crib portion: ...{crib_text}...")
    print(f"  End portion: {end_text}")

    # Words in HOLDOWQULCKEPJFYANKCAYF
    test = "HOLDOWQULCKEPJFYANKCAYF"
    print(f"  Segment C raw: {test}")
    # HOLD + OW + QULCKE + PJFY + ANK + CAYF
    # Could be: HOLD + OW (=HOLD OW?)
    # QUICKLY? QULCKE -> rearrange?
    # Look for English words
    words_in_c = find_english_words(test, wordlist_global, min_len=3)
    print(f"  Words in seg C: {[(p, w) for p, w in words_in_c]}")

    # BERLINCLOCKHOLDOWQULCKEPJFYANKCAYF
    full_end = "BERLINCLOCKHOLDOWQULCKEPJFYANKCAYF"
    words_in_end = find_english_words(full_end, wordlist_global, min_len=3)
    print(f"  Words in BERLINCLOCK+C: {[(p, w) for p, w in words_in_end]}")

    # 8e. What if we read the full Vigenere output but skip specific positions?
    print("\n--- 8e. Skip-Pattern Tests ---")
    # Skip positions that are "Q" or "Z" (uncommon in English)
    uncommon = set('QZXJV')
    positions_no_uncommon = [i for i in range(len(text)) if text[i] not in uncommon]
    extracted = extract_positions(text, positions_no_uncommon)
    sc = scorer.score_per_char(extracted)
    print(f"  Skip QZXJV chars: {extracted[:60]}... (score: {sc:.3f})")
    results.append((sc, "skip uncommon chars", extracted))

    # Skip positions where key and plaintext differ by > 13
    diff_pos = []
    for i in range(len(text)):
        ki = KEY_NUMS[i % len(KEY_NUMS)]
        pi = KRYPTOS_ALPHA.index(text[i])
        if abs(ki - pi) <= 13:
            diff_pos.append(i)
    extracted = extract_positions(text, diff_pos)
    sc = scorer.score_per_char(extracted)
    print(f"  |key-plain|<=13: {extracted[:60]}... (len={len(extracted)}, score: {sc:.3f})")
    results.append((sc, "|key-plain|<=13", extracted))

    return results


# ============================================================
# SECTION 9: TRANSPOSITION WITHIN SEGMENTS
# ============================================================

def test_transposition_within(scorer):
    print("\n" + "=" * 80)
    print("SECTION 9: TRANSPOSITION WITHIN SEGMENTS")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # Test columnar transposition of each segment
    for seg_name, seg_text in [("A", SEG_A), ("B", SEG_B), ("C", SEG_C)]:
        print(f"\n--- Segment {seg_name}: {seg_text} ---")
        best = []
        for ncols in range(2, min(len(seg_text), 9)):
            # Fill row by row, read column by column
            nrows = math.ceil(len(seg_text) / ncols)
            col_read = ''
            for c in range(ncols):
                for r in range(nrows):
                    idx = r * ncols + c
                    if idx < len(seg_text):
                        col_read += seg_text[idx]
            sc = scorer.score_per_char(col_read)
            best.append((sc, f"cols={ncols}", col_read))

            # Also fill column by column, read row by row
            row_read = ''
            nrows2 = math.ceil(len(seg_text) / ncols)
            for r in range(nrows2):
                for c in range(ncols):
                    idx = c * nrows2 + r
                    if idx < len(seg_text):
                        row_read += seg_text[idx]
            sc2 = scorer.score_per_char(row_read)
            best.append((sc2, f"cols={ncols} (col-fill/row-read)", row_read))

        best.sort(reverse=True)
        for sc, desc, txt in best[:3]:
            print(f"  {desc}: {txt} (score: {sc:.3f})")
            results.append((sc, f"Seg {seg_name} transp {desc}", txt))

    # Test transposition of the entire Vigenere output
    print("\n--- Full Vigenere Output Transposition ---")
    best_full = []
    for ncols in range(2, 15):
        nrows = math.ceil(len(text) / ncols)
        col_read = ''
        for c in range(ncols):
            for r in range(nrows):
                idx = r * ncols + c
                if idx < len(text):
                    col_read += text[idx]
        sc = scorer.score_per_char(col_read)
        best_full.append((sc, f"full cols={ncols}", col_read))
    best_full.sort(reverse=True)
    for sc, desc, txt in best_full[:5]:
        print(f"  {desc}: {txt[:60]}... (score: {sc:.3f})")
        results.append((sc, desc, txt))

    # Rail fence cipher variants
    print("\n--- Rail Fence on Vigenere Output ---")
    for rails in range(2, 8):
        # Encode positions in rail fence pattern
        fence = [[] for _ in range(rails)]
        rail = 0
        direction = 1
        for i in range(len(text)):
            fence[rail].append(i)
            if rail == 0:
                direction = 1
            elif rail == rails - 1:
                direction = -1
            rail += direction
        # Read off the fence
        fence_read = ''
        for rail_positions in fence:
            fence_read += ''.join(text[p] for p in rail_positions)
        sc = scorer.score_per_char(fence_read)
        results.append((sc, f"rail fence {rails} rails", fence_read))
        if sc > -8.5:
            print(f"  {rails} rails: {fence_read[:60]}... (score: {sc:.3f})")

        # Also try decoding (reading off as if it was rail-fence encoded)
        # This means reordering the characters
        order = []
        for rail_positions in fence:
            order.extend(rail_positions)
        # Inverse: position i in the fence-read corresponds to original position order[i]
        decoded = [''] * len(text)
        for i, orig_pos in enumerate(order):
            if i < len(text):
                decoded[orig_pos] = text[i]
        decoded_str = ''.join(decoded)
        sc2 = scorer.score_per_char(decoded_str)
        results.append((sc2, f"rail fence {rails} rails (decode)", decoded_str))
        if sc2 > -8.5:
            print(f"  {rails} rails (decode): {decoded_str[:60]}... (score: {sc2:.3f})")

    return results


# ============================================================
# SECTION 10: HOLISTIC SCORING AND BEST RESULTS
# ============================================================

def compile_results(all_results, scorer):
    print("\n" + "=" * 80)
    print("FINAL: TOP 30 RESULTS ACROSS ALL TESTS")
    print("=" * 80)

    # Flatten and sort
    flat = []
    for result_list in all_results:
        if isinstance(result_list, list):
            flat.extend(result_list)

    flat.sort(reverse=True)

    seen = set()
    rank = 0
    for sc, desc, text in flat:
        if text in seen:
            continue
        seen.add(text)
        rank += 1
        if rank > 30:
            break
        # Find English words in this result
        words = find_english_words(text, wordlist_global, min_len=4)
        word_str = ', '.join(w for _, w in words[:5]) if words else "none"
        print(f"\n  #{rank}. Score: {sc:.3f} | {desc}")
        print(f"      Text: {text[:70]}")
        if len(text) > 70:
            print(f"            {text[70:]}")
        print(f"      Words found: {word_str}")


# ============================================================
# SECTION 11: SPECIFIC PATTERN TESTS BASED ON SCHEIDT CLUE
# ============================================================

def test_scheidt_masking(scorer):
    """
    Scheidt said: "masking technique" - "I disguise the English language"
    This suggests the plaintext IS there but disguised.
    Test: what if every Nth char is a null inserted to disguise?
    """
    print("\n" + "=" * 80)
    print("SECTION 11: SCHEIDT 'MASKING' SPECIFIC TESTS")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # 11a. Remove every Nth character
    print("\n--- 11a. Remove Every Nth Character ---")
    for n in range(2, 8):
        for offset in range(n):
            positions = [i for i in range(len(text)) if i % n != offset]
            extracted = extract_positions(text, positions)
            sc = scorer.score_per_char(extracted)
            results.append((sc, f"remove every {n}th (offset {offset})", extracted))
            if sc > -7.5:
                print(f"  Remove every {n}th (offset {offset}): {extracted[:60]}... (score: {sc:.3f})")

    # 11b. What if the mask is spelled out in the key?
    print("\n--- 11b. Key-Letter-Based Mask ---")
    # Maybe positions where key letter is in "MASK" or "KRYPTOS" or "BERLIN" etc.
    for keyword in ["MASK", "KRYPTOS", "BERLIN", "CLOCK", "PALIMPSEST", "ABSCISSA"]:
        kw_set = set(keyword)
        positions = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] in kw_set]
        if len(positions) < 8:
            continue
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, f"key in '{keyword}'", extracted))
        print(f"  Key chars in '{keyword}': {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

        # Complement
        comp_pos = [i for i in range(len(text)) if KEY_STR[i % len(KEY_STR)] not in kw_set]
        extracted_c = extract_positions(text, comp_pos)
        sc_c = scorer.score_per_char(extracted_c)
        results.append((sc_c, f"key NOT in '{keyword}'", extracted_c))
        if sc_c > -8.0:
            print(f"  Key chars NOT in '{keyword}': {extracted_c[:50]}... (score: {sc_c:.3f})")

    # 11c. Position parity matching key parity
    print("\n--- 11c. Position-Key Parity Match ---")
    match_parity = [i for i in range(len(text)) if i % 2 == KEY_NUMS[i % len(KEY_NUMS)] % 2]
    mismatch_parity = [i for i in range(len(text)) if i % 2 != KEY_NUMS[i % len(KEY_NUMS)] % 2]
    for name, positions in [("parity_match", match_parity), ("parity_mismatch", mismatch_parity)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, name, extracted))
        print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    # 11d. Cumulative key sum mod N
    print("\n--- 11d. Cumulative Key Sum Masks ---")
    cumsum = []
    s = 0
    for i in range(len(text)):
        s += KEY_NUMS[i % len(KEY_NUMS)]
        cumsum.append(s)
    for mod in [2, 3, 4, 5]:
        for val in range(mod):
            positions = [i for i in range(len(text)) if cumsum[i] % mod == val]
            if len(positions) < 8:
                continue
            extracted = extract_positions(text, positions)
            sc = scorer.score_per_char(extracted)
            results.append((sc, f"cumsum%{mod}=={val}", extracted))
            if sc > -7.5:
                print(f"  cumsum%{mod}=={val}: {extracted[:50]}... (score: {sc:.3f})")

    # 11e. Running XOR of consecutive key values
    print("\n--- 11e. Key Difference Masks ---")
    key_diffs = [abs(KEY_NUMS[(i+1) % len(KEY_NUMS)] - KEY_NUMS[i % len(KEY_NUMS)]) for i in range(len(text))]
    median_diff = sorted(key_diffs)[len(key_diffs) // 2]
    above_median = [i for i in range(len(text)) if key_diffs[i] > median_diff]
    below_median = [i for i in range(len(text)) if key_diffs[i] <= median_diff]
    for name, positions in [("keydiff>median", above_median), ("keydiff<=median", below_median)]:
        extracted = extract_positions(text, positions)
        sc = scorer.score_per_char(extracted)
        results.append((sc, name, extracted))
        print(f"  {name}: {extracted[:50]}... (len={len(extracted)}, score: {sc:.3f})")

    # 11f. Mask from the Vigenere output itself: pick chars that are vowels/consonants
    print("\n--- 11f. Vowel/Consonant Selection from Output ---")
    vowels = set("AEIOU")
    vowel_positions = [i for i in range(len(text)) if text[i] in vowels]
    consonant_positions = [i for i in range(len(text)) if text[i] not in vowels]
    print(f"  Vowels in output ({len(vowel_positions)}): {extract_positions(text, vowel_positions)}")
    print(f"  Consonant positions: {len(consonant_positions)}")

    results.sort(reverse=True)
    print("\n--- TOP 15 SCHEIDT MASKING RESULTS ---")
    for sc, desc, ext in results[:15]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# SECTION 12: DOUBLE EXTRACTION (Mask + Secondary Cipher)
# ============================================================

def test_double_extraction(scorer):
    """Test: mask selects characters, then apply a secondary cipher."""
    print("\n" + "=" * 80)
    print("SECTION 12: MASK + SECONDARY CIPHER")
    print("=" * 80)
    text = VIG_OUTPUT
    results = []

    # For each promising mask pattern, try secondary Caesar on the extracted text
    promising_masks = [
        ("every 2nd offset=0", [i for i in range(0, len(text), 2)]),
        ("every 2nd offset=1", [i for i in range(1, len(text), 2)]),
        ("every 3rd offset=0", [i for i in range(0, len(text), 3)]),
        ("every 3rd offset=1", [i for i in range(1, len(text), 3)]),
        ("every 3rd offset=2", [i for i in range(2, len(text), 3)]),
        ("key_even", [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] % 2 == 0]),
        ("key_odd", [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] % 2 == 1]),
        ("key<13", [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] < 13]),
        ("key>=13", [i for i in range(len(text)) if KEY_NUMS[i % len(KEY_NUMS)] >= 13]),
        ("prime positions", [i for i in range(len(text)) if is_prime(i)]),
    ]

    for mask_name, positions in promising_masks:
        extracted = extract_positions(text, positions)
        if len(extracted) < 8:
            continue
        for shift in range(26):
            shifted = ''.join(kryptos_shift(c, shift) for c in extracted)
            sc = scorer.score_per_char(shifted)
            if sc > -6.5:
                results.append((sc, f"{mask_name} + Caesar {shift}", shifted))
                print(f"  {mask_name} + Caesar {shift}: {shifted[:50]}... (score: {sc:.3f})")

    # Also try mask + Atbash
    for mask_name, positions in promising_masks:
        extracted = extract_positions(text, positions)
        if len(extracted) < 8:
            continue
        atbash = ''.join(KRYPTOS_ALPHA[25 - KRYPTOS_ALPHA.index(c)] for c in extracted)
        sc = scorer.score_per_char(atbash)
        if sc > -7.0:
            results.append((sc, f"{mask_name} + Atbash", atbash))
            print(f"  {mask_name} + Atbash: {atbash[:50]}... (score: {sc:.3f})")

    if not results:
        print("  No results above threshold.")

    results.sort(reverse=True)
    print(f"\n  Total results found: {len(results)}")
    for sc, desc, ext in results[:10]:
        print(f"  {sc:.3f}  {desc}: {ext[:60]}")

    return results


# ============================================================
# MAIN
# ============================================================

wordlist_global = None

def main():
    global wordlist_global

    print("K4 Cardan Grille / Physical Mask / Selection Cipher Analysis")
    print("=" * 80)
    print(f"K4 Ciphertext:    {K4_CIPHERTEXT}")
    print(f"Vigenere Output:  {VIG_OUTPUT}")
    print(f"Key:              {BEST_KEY}")
    print(f"Key (numeric):    {KEY_NUMS}")
    print(f"")
    print(f"Known cribs in Vigenere output:")
    print(f"  Pos 16-20: POINT          = {VIG_OUTPUT[16:21]}")
    print(f"  Pos 21-33: EASTNORTHEAST  = {VIG_OUTPUT[21:34]}")
    print(f"  Pos 63-73: BERLINCLOCK    = {VIG_OUTPUT[63:74]}")
    print(f"")
    print(f"Non-crib segments:")
    print(f"  Seg A (0-15):  {SEG_A}")
    print(f"  Seg B (34-62): {SEG_B}")
    print(f"  Seg C (74-96): {SEG_C}")
    print()

    scorer = QuadgramScorer(QUADGRAM_FILE)
    wordlist_global = load_wordlist()

    # Reference scores
    print("Reference quadgram scores:")
    for ref_text in ["THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",
                     "EASTNORTHEAST", "BERLINCLOCK", "POINTEASTNORTHEAST",
                     VIG_OUTPUT, SEG_A, SEG_B, SEG_C]:
        sc = scorer.score_per_char(ref_text)
        print(f"  {ref_text[:40]:40s} -> {sc:.3f}")
    print()

    all_results = []

    # Run all test sections
    all_results.append(test_mask_patterns(scorer))
    all_results.append(test_grid_grille(scorer))
    all_results.append(test_caesar_on_noncrib(scorer))
    all_results.append(test_interleaving(scorer))
    all_results.append(test_noncrib_segments(scorer, wordlist_global))
    test_coordinate_extraction(scorer)  # This one prints but doesn't return scored results
    all_results.append(test_advanced_grille(scorer))
    all_results.append(test_mask_then_read(scorer))
    all_results.append(test_transposition_within(scorer))
    all_results.append(test_scheidt_masking(scorer))
    all_results.append(test_double_extraction(scorer))

    # Final compilation
    compile_results(all_results, scorer)

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
