#!/usr/bin/env python3
"""
K4 + K3-style columnar transposition analysis.

Tests whether K4 uses a columnar transposition layer (like K3's KRYPTOS keyed
transposition) in addition to a period-29 Vigenere cipher.

K4 ciphertext: OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ
Best brute-force Vigenere key (period 29): OYNKYELYOIECBAQKCBNJQRDUMRIYW

Hypotheses tested:
  A) Encrypt = Vig(Transpose(plain)) => Decrypt = Un-transpose(Vig-decrypt(ct))
  B) Encrypt = Transpose(Vig(plain)) => Decrypt = Vig-decrypt(Un-transpose(ct))
  C) Multiple key variants for uncertain positions
  D) Specific K3 KRYPTOS key (0362514) in both directions
"""

import itertools
import math
import sys
import time
from collections import defaultdict

# ── Constants ──────────────────────────────────────────────────────────────────

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
VIG_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"   # period-29 best key
K4_LEN = len(K4_CT)  # 97

# KRYPTOS keyword -> numeric key
# K=0, R=3, Y=6, P=2, T=5, O=1, S=4  (alphabetical rank within KRYPTOS)
KRYPTOS_KEY_ORDER = [0, 3, 6, 2, 5, 1, 4]  # read-off order for columns
KRYPTOS_NUM_COLS = 7

# Known plaintext fragments and their approximate positions
KNOWN_FRAGMENTS = {
    "BERLINCLOCK": (62, 73),
    "EASTNORTHEAST": (20, 33),
    "NORTHEAST": (24, 33),
    "BERLIN": (62, 68),
    "CLOCK": (68, 73),
    "EAST": (20, 24),
    "NORTH": (24, 29),
}

WORD_FILE = "/home/user/polyalphabetic/OxfordEnglishWords.txt"

# ── Load dictionary ───────────────────────────────────────────────────────────

def load_words():
    words = set()
    with open(WORD_FILE) as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 3:
                words.add(w)
    return words

WORDS = load_words()

# Build a set of all words length >= 4 for scoring
WORDS4 = {w for w in WORDS if len(w) >= 4}
WORDS5 = {w for w in WORDS if len(w) >= 5}
WORDS6 = {w for w in WORDS if len(w) >= 6}

# Common English trigrams for quick scoring
COMMON_TRIGRAMS = set([
    "THE", "AND", "ING", "HER", "HAT", "HIS", "THA", "ERE", "FOR", "ENT",
    "ION", "TER", "WAS", "YOU", "ITH", "VER", "ALL", "WIT", "THI", "TIO",
    "ARE", "NOT", "BUT", "HAD", "ONE", "OUR", "OUT", "DAY", "HAV", "HEN",
])

# ── KRYPTOS alphabet Vigenere ─────────────────────────────────────────────────

def kryptos_index(ch):
    """Return index of character in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA.index(ch)

def kryptos_char(idx):
    """Return character at index in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA[idx % 26]

def vig_decrypt(ciphertext, key):
    """Decrypt using Vigenere with KRYPTOS alphabet."""
    out = []
    kl = len(key)
    for i, c in enumerate(ciphertext):
        ci = kryptos_index(c)
        ki = kryptos_index(key[i % kl])
        pi = (ci - ki) % 26
        out.append(kryptos_char(pi))
    return "".join(out)

def vig_encrypt(plaintext, key):
    """Encrypt using Vigenere with KRYPTOS alphabet."""
    out = []
    kl = len(key)
    for i, c in enumerate(plaintext):
        pi = kryptos_index(c)
        ki = kryptos_index(key[i % kl])
        ci = (pi + ki) % 26
        out.append(kryptos_char(ci))
    return "".join(out)

# ── Columnar transposition ────────────────────────────────────────────────────

def columnar_transpose(text, num_cols, col_order):
    """
    Columnar transposition encryption.
    Write text into rows of num_cols, then read off columns in col_order.
    col_order[i] = which column to read as the i-th output column.
    """
    n = len(text)
    num_full_rows = n // num_cols
    extra = n % num_cols
    
    # Build grid row by row
    grid = []
    idx = 0
    for r in range(num_full_rows + (1 if extra else 0)):
        row = []
        for c in range(num_cols):
            if idx < n:
                row.append(text[idx])
                idx += 1
            else:
                row.append(None)
        grid.append(row)
    
    # Read off columns in col_order sequence
    result = []
    for col_idx in col_order:
        for row in grid:
            if col_idx < len(row) and row[col_idx] is not None:
                result.append(row[col_idx])
    
    return "".join(result)

def columnar_untranspose(text, num_cols, col_order):
    """
    Columnar transposition decryption (reverse of columnar_transpose).
    The text was created by reading columns in col_order.
    We need to figure out how many chars are in each column, fill them back,
    then read row by row.
    """
    n = len(text)
    num_full_rows = n // num_cols
    extra = n % num_cols  # first 'extra' columns have an extra row
    
    # Determine column lengths
    col_lengths = []
    for c in range(num_cols):
        if c < extra:
            col_lengths.append(num_full_rows + 1)
        else:
            col_lengths.append(num_full_rows)
    
    # Fill columns in col_order sequence
    columns = [[] for _ in range(num_cols)]
    idx = 0
    for col_idx in col_order:
        length = col_lengths[col_idx]
        columns[col_idx] = list(text[idx:idx+length])
        idx += length
    
    # Read row by row
    result = []
    num_rows = num_full_rows + (1 if extra else 0)
    for r in range(num_rows):
        for c in range(num_cols):
            if r < len(columns[c]):
                result.append(columns[c][r])
    
    return "".join(result)

# ── Scoring ───────────────────────────────────────────────────────────────────

def score_text(text):
    """
    Score a candidate plaintext. Higher = more English-like.
    Multi-factor: long word matches, known fragment matches, trigram hits.
    """
    t = text.upper()
    score = 0.0
    
    # Check for known K4 fragments with position awareness
    fragment_bonus = 0
    if "BERLINCLOCK" in t:
        pos = t.index("BERLINCLOCK")
        fragment_bonus += 500
        if 55 <= pos <= 75:
            fragment_bonus += 300
    elif "BERLIN" in t:
        pos = t.index("BERLIN")
        fragment_bonus += 100
        if 55 <= pos <= 75:
            fragment_bonus += 50
    if "EASTNORTHEAST" in t:
        pos = t.index("EASTNORTHEAST")
        fragment_bonus += 500
        if 15 <= pos <= 35:
            fragment_bonus += 300
    elif "NORTHEAST" in t:
        pos = t.index("NORTHEAST")
        fragment_bonus += 200
        if 18 <= pos <= 38:
            fragment_bonus += 100
    elif "EAST" in t:
        for i in range(len(t) - 3):
            if t[i:i+4] == "EAST":
                fragment_bonus += 30
                break
    if "CLOCK" in t:
        fragment_bonus += 80
    
    score += fragment_bonus
    
    # Greedy longest-word matching
    word_score = 0
    n = len(t)
    i = 0
    matched_positions = set()
    
    # Try to find long words first
    for wlen in range(min(15, n), 3, -1):
        for start in range(n - wlen + 1):
            if any(p in matched_positions for p in range(start, start + wlen)):
                continue
            substr = t[start:start+wlen]
            if substr in WORDS:
                word_score += wlen * wlen  # quadratic reward for length
                for p in range(start, start + wlen):
                    matched_positions.add(p)
    
    score += word_score
    
    # Trigram frequency
    tri_count = 0
    for i in range(len(t) - 2):
        if t[i:i+3] in COMMON_TRIGRAMS:
            tri_count += 1
    score += tri_count * 3
    
    return score

def quick_score(text):
    """Fast scoring for mass screening."""
    t = text.upper()
    score = 0
    
    # Check key fragments
    if "BERLIN" in t:
        score += 200
    if "CLOCK" in t:
        score += 150
    if "EAST" in t:
        score += 80
    if "NORTH" in t:
        score += 80
    if "NORTHEAST" in t:
        score += 200
    if "BERLINCLOCK" in t:
        score += 500
    if "EASTNORTHEAST" in t:
        score += 500
    
    # Quick trigram check
    for i in range(len(t) - 2):
        if t[i:i+3] in COMMON_TRIGRAMS:
            score += 3
    
    # Check for common 4+ letter words (sample)
    for wlen in [7, 6, 5, 4]:
        for start in range(len(t) - wlen + 1):
            if t[start:start+wlen] in WORDS:
                score += wlen * wlen
                break  # just find one per length for speed
    
    return score

# ── Intermediate text from Vigenere decryption ────────────────────────────────

VIG_INTERMEDIATE = vig_decrypt(K4_CT, VIG_KEY)
print(f"K4 ciphertext ({K4_LEN} chars): {K4_CT}")
print(f"Vigenere key (period 29):       {VIG_KEY}")
print(f"Vigenere intermediate text:     {VIG_INTERMEDIATE}")
print(f"Length: {len(VIG_INTERMEDIATE)}")
print()

# Verify known fragments in intermediate
for frag in ["EASTNORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST"]:
    if frag in VIG_INTERMEDIATE:
        pos = VIG_INTERMEDIATE.index(frag)
        print(f"  Found '{frag}' at position {pos} in intermediate text")

print()
print("=" * 80)
print("HYPOTHESIS A: Decrypt = Un-transpose( Vig-decrypt(ct) )")
print("  The intermediate text IS the transposed plaintext.")
print("  Un-transposing should yield coherent English.")
print("=" * 80)
print()

results = []  # (score, description, text)

# ── Hypothesis A & D: Un-transpose the Vigenere intermediate ──────────────────

def test_untranspose_intermediate(intermediate, label_prefix="HypA"):
    """Try all columnar un-transpositions on the intermediate text."""
    local_results = []
    
    # D: Specific KRYPTOS key (width 7, order 0362514)
    print(f"[{label_prefix}] Testing KRYPTOS key order {KRYPTOS_KEY_ORDER} (width 7)...")
    
    # Un-transpose
    pt = columnar_untranspose(intermediate, 7, KRYPTOS_KEY_ORDER)
    s = score_text(pt)
    desc = f"{label_prefix} w=7 key=0362514(KRYPTOS) untranspose"
    local_results.append((s, desc, pt))
    print(f"  {desc}: score={s:.0f}")
    print(f"    {pt}")
    
    # Transpose (reverse direction)
    pt2 = columnar_transpose(intermediate, 7, KRYPTOS_KEY_ORDER)
    s2 = score_text(pt2)
    desc2 = f"{label_prefix} w=7 key=0362514(KRYPTOS) transpose"
    local_results.append((s2, desc2, pt2))
    print(f"  {desc2}: score={s2:.0f}")
    print(f"    {pt2}")
    
    # Also try inverse permutation of KRYPTOS key
    # If KRYPTOS key is [0,3,6,2,5,1,4], the inverse is:
    inv_key = [0] * 7
    for i, k in enumerate(KRYPTOS_KEY_ORDER):
        inv_key[k] = i
    print(f"  Inverse KRYPTOS key: {inv_key}")
    
    pt3 = columnar_untranspose(intermediate, 7, inv_key)
    s3 = score_text(pt3)
    desc3 = f"{label_prefix} w=7 key={inv_key}(inv-KRYPTOS) untranspose"
    local_results.append((s3, desc3, pt3))
    print(f"  {desc3}: score={s3:.0f}")
    print(f"    {pt3}")
    
    pt4 = columnar_transpose(intermediate, 7, inv_key)
    s4 = score_text(pt4)
    desc4 = f"{label_prefix} w=7 key={inv_key}(inv-KRYPTOS) transpose"
    local_results.append((s4, desc4, pt4))
    print(f"  {desc4}: score={s4:.0f}")
    print(f"    {pt4}")
    
    print()
    
    # Width 7: try ALL 5040 permutations
    print(f"[{label_prefix}] Testing ALL 5040 permutations for width 7...")
    best_w7 = []
    for perm in itertools.permutations(range(7)):
        perm_list = list(perm)
        # Un-transpose
        pt = columnar_untranspose(intermediate, 7, perm_list)
        s = quick_score(pt)
        if s > 20:
            s_full = score_text(pt)
            best_w7.append((s_full, f"{label_prefix} w=7 key={perm_list} untranspose", pt))
        
        # Transpose
        pt2 = columnar_transpose(intermediate, 7, perm_list)
        s2 = quick_score(pt2)
        if s2 > 20:
            s2_full = score_text(pt2)
            best_w7.append((s2_full, f"{label_prefix} w=7 key={perm_list} transpose", pt2))
    
    best_w7.sort(reverse=True)
    print(f"  Found {len(best_w7)} results with quick_score > 20")
    for s, d, t in best_w7[:10]:
        print(f"  {d}: score={s:.0f}")
        print(f"    {t}")
    local_results.extend(best_w7[:50])
    print()
    
    # Other widths 3-20 (skip 7, already done exhaustively)
    for width in range(3, 21):
        if width == 7:
            continue
        
        # Try identity order
        identity = list(range(width))
        pt = columnar_untranspose(intermediate, width, identity)
        s = score_text(pt)
        local_results.append((s, f"{label_prefix} w={width} key=identity untranspose", pt))
        
        pt2 = columnar_transpose(intermediate, width, identity)
        s2 = score_text(pt2)
        local_results.append((s2, f"{label_prefix} w={width} key=identity transpose", pt2))
        
        # Try reverse order
        rev = list(range(width - 1, -1, -1))
        pt = columnar_untranspose(intermediate, width, rev)
        s = score_text(pt)
        local_results.append((s, f"{label_prefix} w={width} key=reverse untranspose", pt))
        
        pt2 = columnar_transpose(intermediate, width, rev)
        s2 = score_text(pt2)
        local_results.append((s2, f"{label_prefix} w={width} key=reverse transpose", pt2))
        
        # For small widths, try all permutations
        if width <= 8:
            perms_to_try = list(itertools.permutations(range(width)))
            for perm in perms_to_try:
                perm_list = list(perm)
                pt = columnar_untranspose(intermediate, width, perm_list)
                s = quick_score(pt)
                if s > 30:
                    s_full = score_text(pt)
                    local_results.append((s_full, f"{label_prefix} w={width} key={perm_list} untranspose", pt))
                
                pt2 = columnar_transpose(intermediate, width, perm_list)
                s2 = quick_score(pt2)
                if s2 > 30:
                    s2_full = score_text(pt2)
                    local_results.append((s2_full, f"{label_prefix} w={width} key={perm_list} transpose", pt2))
        else:
            # For larger widths, try some keyword-derived orders
            # KRYPTOS-derived for the width
            keyword = "KRYPTOS"
            if width <= len(keyword):
                sub = keyword[:width]
            else:
                sub = keyword + "ABCDEFGHIJLMNQUVWXZ"[:width - len(keyword)]
            order = [i for i, _ in sorted(enumerate(sub), key=lambda x: x[1])]
            
            pt = columnar_untranspose(intermediate, width, order)
            s = score_text(pt)
            local_results.append((s, f"{label_prefix} w={width} key=KRYPTOS-derived untranspose", pt))
            
            pt2 = columnar_transpose(intermediate, width, order)
            s2 = score_text(pt2)
            local_results.append((s2, f"{label_prefix} w={width} key=KRYPTOS-derived transpose", pt2))
    
    return local_results

t0 = time.time()
results.extend(test_untranspose_intermediate(VIG_INTERMEDIATE, "HypA"))
print(f"Hypothesis A completed in {time.time()-t0:.1f}s")
print()

# ── Hypothesis B: Un-transpose ciphertext FIRST, then Vigenere decrypt ────────

print("=" * 80)
print("HYPOTHESIS B: Decrypt = Vig-decrypt( Un-transpose(ct) )")
print("  The ciphertext was transposed AFTER Vigenere encryption.")
print("  Un-transpose the ciphertext first, then Vigenere decrypt.")
print("=" * 80)
print()

def test_untranspose_ct_then_vig(label_prefix="HypB"):
    """Un-transpose K4 ciphertext, then Vigenere decrypt."""
    local_results = []
    
    # Width 7: try ALL 5040 permutations
    print(f"[{label_prefix}] Testing ALL 5040 permutations for width 7 on ciphertext...")
    best_w7 = []
    
    for perm in itertools.permutations(range(7)):
        perm_list = list(perm)
        
        # Un-transpose ciphertext
        ct_untrans = columnar_untranspose(K4_CT, 7, perm_list)
        pt = vig_decrypt(ct_untrans, VIG_KEY)
        s = quick_score(pt)
        if s > 20:
            s_full = score_text(pt)
            best_w7.append((s_full, f"{label_prefix} w=7 key={perm_list} untrans-then-vig", pt))
        
        # Transpose ciphertext (reverse)
        ct_trans = columnar_transpose(K4_CT, 7, perm_list)
        pt2 = vig_decrypt(ct_trans, VIG_KEY)
        s2 = quick_score(pt2)
        if s2 > 20:
            s2_full = score_text(pt2)
            best_w7.append((s2_full, f"{label_prefix} w=7 key={perm_list} trans-then-vig", pt2))
    
    best_w7.sort(reverse=True)
    print(f"  Found {len(best_w7)} results with quick_score > 20")
    for s, d, t in best_w7[:10]:
        print(f"  {d}: score={s:.0f}")
        print(f"    {t}")
    local_results.extend(best_w7[:50])
    print()
    
    # KRYPTOS key specifically
    print(f"[{label_prefix}] KRYPTOS key order on ciphertext...")
    for key_order, key_name in [(KRYPTOS_KEY_ORDER, "KRYPTOS"), 
                                  ([0]*7, "will-compute-inv")]:
        if key_name == "will-compute-inv":
            key_order = [0] * 7
            for i, k in enumerate(KRYPTOS_KEY_ORDER):
                key_order[k] = i
            key_name = "inv-KRYPTOS"
        
        ct_untrans = columnar_untranspose(K4_CT, 7, key_order)
        pt = vig_decrypt(ct_untrans, VIG_KEY)
        s = score_text(pt)
        desc = f"{label_prefix} w=7 {key_name} untrans-ct-then-vig"
        local_results.append((s, desc, pt))
        print(f"  {desc}: score={s:.0f}")
        print(f"    {pt}")
        
        ct_trans = columnar_transpose(K4_CT, 7, key_order)
        pt2 = vig_decrypt(ct_trans, VIG_KEY)
        s2 = score_text(pt2)
        desc2 = f"{label_prefix} w=7 {key_name} trans-ct-then-vig"
        local_results.append((s2, desc2, pt2))
        print(f"  {desc2}: score={s2:.0f}")
        print(f"    {pt2}")
    print()
    
    # Other widths with all permutations for small widths
    for width in range(3, 21):
        if width == 7:
            continue
        if width <= 8:
            for perm in itertools.permutations(range(width)):
                perm_list = list(perm)
                ct_untrans = columnar_untranspose(K4_CT, width, perm_list)
                pt = vig_decrypt(ct_untrans, VIG_KEY)
                s = quick_score(pt)
                if s > 30:
                    s_full = score_text(pt)
                    local_results.append((s_full, f"{label_prefix} w={width} key={perm_list} untrans-then-vig", pt))
                
                ct_trans = columnar_transpose(K4_CT, width, perm_list)
                pt2 = vig_decrypt(ct_trans, VIG_KEY)
                s2 = quick_score(pt2)
                if s2 > 30:
                    s2_full = score_text(pt2)
                    local_results.append((s2_full, f"{label_prefix} w={width} key={perm_list} trans-then-vig", pt2))
        else:
            # Just try KRYPTOS-derived and identity
            for key_order, key_name in [(list(range(width)), "identity"),
                                          (list(range(width-1, -1, -1)), "reverse")]:
                ct_untrans = columnar_untranspose(K4_CT, width, key_order)
                pt = vig_decrypt(ct_untrans, VIG_KEY)
                s = score_text(pt)
                local_results.append((s, f"{label_prefix} w={width} {key_name} untrans-then-vig", pt))
                
                ct_trans = columnar_transpose(K4_CT, width, key_order)
                pt2 = vig_decrypt(ct_trans, VIG_KEY)
                s2 = score_text(pt2)
                local_results.append((s2, f"{label_prefix} w={width} {key_name} trans-then-vig", pt2))
    
    return local_results

t0 = time.time()
results.extend(test_untranspose_ct_then_vig("HypB"))
print(f"Hypothesis B completed in {time.time()-t0:.1f}s")
print()

# ── Hypothesis C: Multiple Vigenere keys with KRYPTOS transposition ───────────

print("=" * 80)
print("HYPOTHESIS C: Multiple Vigenere keys + KRYPTOS transposition")
print("  Positions 16-20 of the key are uncertain.")
print("  Try varying those 5 positions with KRYPTOS columnar transposition.")
print("=" * 80)
print()

def test_key_variants_with_transposition():
    """
    Try key variants where positions 16-20 vary, combined with
    KRYPTOS columnar transposition (width 7).
    """
    local_results = []
    base_key = list(VIG_KEY)  # 29 chars
    uncertain_positions = [16, 17, 18, 19, 20]
    
    # Instead of 26^5, sample strategically:
    # Try each uncertain position individually with all 26 letters
    print("[HypC] Testing individual position variants...")
    count = 0
    
    # First, try all single-position changes
    for pos in uncertain_positions:
        original = base_key[pos]
        for ch in KRYPTOS_ALPHA:
            if ch == original:
                continue
            test_key = base_key.copy()
            test_key[pos] = ch
            key_str = "".join(test_key)
            
            intermediate = vig_decrypt(K4_CT, key_str)
            
            # Test with KRYPTOS transposition (both directions)
            for key_order, direction in [(KRYPTOS_KEY_ORDER, "KRYPTOS-untrans"),
                                          ([0]*7, "inv-KRYPTOS-untrans")]:
                if direction == "inv-KRYPTOS-untrans":
                    key_order = [0] * 7
                    for i, k in enumerate(KRYPTOS_KEY_ORDER):
                        key_order[k] = i
                
                pt = columnar_untranspose(intermediate, 7, key_order)
                s = quick_score(pt)
                if s > 40:
                    s_full = score_text(pt)
                    local_results.append((s_full, f"HypC pos{pos}={ch} {direction}", pt))
                    count += 1
                
                pt2 = columnar_transpose(intermediate, 7, key_order)
                s2 = quick_score(pt2)
                if s2 > 40:
                    s2_full = score_text(pt2)
                    local_results.append((s2_full, f"HypC pos{pos}={ch} {direction}-rev", pt2))
                    count += 1
            
            # Also test without transposition but with modified key
            pt_direct = intermediate
            s_direct = quick_score(pt_direct)
            if s_direct > 50:
                s_full = score_text(pt_direct)
                local_results.append((s_full, f"HypC pos{pos}={ch} direct", pt_direct))
    
    print(f"  Found {count} results above threshold from single-position changes")
    
    # Try pairs of positions
    print("[HypC] Testing position-pair variants (positions 16-20, pairs)...")
    count2 = 0
    for p1, p2 in itertools.combinations(uncertain_positions, 2):
        for c1 in KRYPTOS_ALPHA[::3]:  # sample every 3rd letter for speed
            for c2 in KRYPTOS_ALPHA[::3]:
                test_key = base_key.copy()
                test_key[p1] = c1
                test_key[p2] = c2
                key_str = "".join(test_key)
                
                intermediate = vig_decrypt(K4_CT, key_str)
                
                # KRYPTOS untranspose
                inv_key = [0] * 7
                for i, k in enumerate(KRYPTOS_KEY_ORDER):
                    inv_key[k] = i
                
                for key_order in [KRYPTOS_KEY_ORDER, inv_key]:
                    pt = columnar_untranspose(intermediate, 7, key_order)
                    s = quick_score(pt)
                    if s > 50:
                        s_full = score_text(pt)
                        local_results.append((s_full, f"HypC p{p1}={c1},p{p2}={c2} untrans", pt))
                        count2 += 1
                    
                    pt2 = columnar_transpose(intermediate, 7, key_order)
                    s2 = quick_score(pt2)
                    if s2 > 50:
                        s2_full = score_text(pt2)
                        local_results.append((s2_full, f"HypC p{p1}={c1},p{p2}={c2} trans", pt2))
                        count2 += 1
    
    print(f"  Found {count2} results above threshold from pair changes")
    
    return local_results

t0 = time.time()
results.extend(test_key_variants_with_transposition())
print(f"Hypothesis C completed in {time.time()-t0:.1f}s")
print()

# ── Hypothesis D: K3's exact transposition applied directly ───────────────────

print("=" * 80)
print("HYPOTHESIS D: K3's exact KRYPTOS transposition")
print("  Testing with padding for incomplete rows.")
print("=" * 80)
print()

def test_k3_exact_transposition():
    """Test K3's exact transposition with various padding options."""
    local_results = []
    
    # 97 chars / 7 cols = 13 full rows + 6 extra
    print(f"[HypD] 97 chars, 7 columns: 13 full rows + 6 extra chars")
    print(f"  KRYPTOS key order: {KRYPTOS_KEY_ORDER}")
    print()
    
    # Test with padding to fill last row
    for pad_char in ['', 'X', 'Z', 'K', 'A']:
        for text, text_name in [(VIG_INTERMEDIATE, "vig-intermediate"), (K4_CT, "ciphertext")]:
            if pad_char:
                padded = text + pad_char * ((7 - len(text) % 7) % 7)
                pad_desc = f"pad={pad_char}"
            else:
                padded = text
                pad_desc = "nopad"
            
            inv_key = [0] * 7
            for i, k in enumerate(KRYPTOS_KEY_ORDER):
                inv_key[k] = i
            
            for key_order, key_name in [(KRYPTOS_KEY_ORDER, "KRYPTOS"),
                                          (inv_key, "inv-KRYPTOS")]:
                pt = columnar_untranspose(padded, 7, key_order)[:97]
                s = score_text(pt)
                desc = f"HypD {text_name} {key_name} untrans {pad_desc}"
                local_results.append((s, desc, pt))
                if s > 30:
                    print(f"  {desc}: score={s:.0f}")
                    print(f"    {pt}")
                
                pt2 = columnar_transpose(padded, 7, key_order)[:97]
                s2 = score_text(pt2)
                desc2 = f"HypD {text_name} {key_name} trans {pad_desc}"
                local_results.append((s2, desc2, pt2))
                if s2 > 30:
                    print(f"  {desc2}: score={s2:.0f}")
                    print(f"    {pt2}")
    
    # For Hypothesis D, also try: un-transpose ciphertext, THEN Vigenere decrypt
    print()
    print("[HypD] Un-transpose ciphertext first, then Vigenere decrypt...")
    inv_key = [0] * 7
    for i, k in enumerate(KRYPTOS_KEY_ORDER):
        inv_key[k] = i
    
    for key_order, key_name in [(KRYPTOS_KEY_ORDER, "KRYPTOS"),
                                  (inv_key, "inv-KRYPTOS")]:
        for pad_char in ['', 'X', 'Z']:
            if pad_char:
                padded_ct = K4_CT + pad_char * ((7 - len(K4_CT) % 7) % 7)
                pad_desc = f"pad={pad_char}"
            else:
                padded_ct = K4_CT
                pad_desc = "nopad"
            
            ct_untrans = columnar_untranspose(padded_ct, 7, key_order)[:97]
            pt = vig_decrypt(ct_untrans, VIG_KEY)
            s = score_text(pt)
            desc = f"HypD untrans-ct({key_name},{pad_desc})-then-vig"
            local_results.append((s, desc, pt))
            print(f"  {desc}: score={s:.0f}")
            print(f"    {pt}")
            
            ct_trans = columnar_transpose(padded_ct, 7, key_order)[:97]
            pt2 = vig_decrypt(ct_trans, VIG_KEY)
            s2 = score_text(pt2)
            desc2 = f"HypD trans-ct({key_name},{pad_desc})-then-vig"
            local_results.append((s2, desc2, pt2))
            print(f"  {desc2}: score={s2:.0f}")
            print(f"    {pt2}")
    
    return local_results

t0 = time.time()
results.extend(test_k3_exact_transposition())
print(f"Hypothesis D completed in {time.time()-t0:.1f}s")
print()

# ── Additional: Route transposition (diagonal/spiral reads) ──────────────────

print("=" * 80)
print("BONUS: Route transpositions on intermediate text (width 7)")
print("=" * 80)
print()

def route_transpositions(text, num_cols):
    """Try various route transposition patterns."""
    local_results = []
    n = len(text)
    num_rows = math.ceil(n / num_cols)
    
    # Pad text
    padded = text + "X" * (num_rows * num_cols - n)
    
    # Write into grid
    grid = []
    for r in range(num_rows):
        grid.append(list(padded[r*num_cols:(r+1)*num_cols]))
    
    # Read by columns (top to bottom, left to right)
    result1 = ""
    for c in range(num_cols):
        for r in range(num_rows):
            result1 += grid[r][c]
    result1 = result1[:n]
    s = score_text(result1)
    local_results.append((s, f"Route col-down-LR w={num_cols}", result1))
    
    # Read by columns (bottom to top, left to right)
    result2 = ""
    for c in range(num_cols):
        for r in range(num_rows - 1, -1, -1):
            result2 += grid[r][c]
    result2 = result2[:n]
    s = score_text(result2)
    local_results.append((s, f"Route col-up-LR w={num_cols}", result2))
    
    # Read by columns alternating direction (serpentine)
    result3 = ""
    for c in range(num_cols):
        if c % 2 == 0:
            for r in range(num_rows):
                result3 += grid[r][c]
        else:
            for r in range(num_rows - 1, -1, -1):
                result3 += grid[r][c]
    result3 = result3[:n]
    s = score_text(result3)
    local_results.append((s, f"Route col-serpentine w={num_cols}", result3))
    
    # Diagonal read
    result4 = ""
    for diag in range(num_rows + num_cols - 1):
        for r in range(num_rows):
            c = diag - r
            if 0 <= c < num_cols:
                result4 += grid[r][c]
    result4 = result4[:n]
    s = score_text(result4)
    local_results.append((s, f"Route diagonal w={num_cols}", result4))
    
    # Spiral read (clockwise from top-left)
    result5 = ""
    visited = [[False]*num_cols for _ in range(num_rows)]
    r, c = 0, 0
    dr, dc = 0, 1  # right
    for _ in range(num_rows * num_cols):
        result5 += grid[r][c]
        visited[r][c] = True
        nr, nc = r + dr, c + dc
        if 0 <= nr < num_rows and 0 <= nc < num_cols and not visited[nr][nc]:
            r, c = nr, nc
        else:
            # Turn clockwise
            dr, dc = dc, -dr
            r, c = r + dr, c + dc
            if not (0 <= r < num_rows and 0 <= c < num_cols):
                break
    result5 = result5[:n]
    s = score_text(result5)
    local_results.append((s, f"Route spiral-CW w={num_cols}", result5))
    
    return local_results

for width in [7, 14, 29]:
    r = route_transpositions(VIG_INTERMEDIATE, width)
    results.extend(r)
    for s, d, t in r:
        if s > 20:
            print(f"  {d}: score={s:.0f}")
            print(f"    {t}")

print()

# ── Additional: Rail fence cipher ────────────────────────────────────────────

print("=" * 80)
print("BONUS: Rail fence on intermediate text")
print("=" * 80)
print()

def rail_fence_decrypt(text, num_rails):
    """Decrypt rail fence cipher."""
    n = len(text)
    if num_rails <= 1 or num_rails >= n:
        return text
    
    # Calculate the length of each rail
    rail_lengths = [0] * num_rails
    rail = 0
    direction = 1
    for i in range(n):
        rail_lengths[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == num_rails - 1:
            direction = -1
        rail += direction
    
    # Split text into rails
    rails = []
    idx = 0
    for r in range(num_rails):
        rails.append(list(text[idx:idx+rail_lengths[r]]))
        idx += rail_lengths[r]
    
    # Read off in zigzag order
    result = []
    rail_idx = [0] * num_rails
    rail = 0
    direction = 1
    for i in range(n):
        result.append(rails[rail][rail_idx[rail]])
        rail_idx[rail] += 1
        if rail == 0:
            direction = 1
        elif rail == num_rails - 1:
            direction = -1
        rail += direction
    
    return "".join(result)

for num_rails in range(2, 15):
    pt = rail_fence_decrypt(VIG_INTERMEDIATE, num_rails)
    s = score_text(pt)
    results.append((s, f"RailFence r={num_rails} on intermediate", pt))
    if s > 30:
        print(f"  RailFence r={num_rails}: score={s:.0f}")
        print(f"    {pt}")

print()

# ── Final results ─────────────────────────────────────────────────────────────

print("=" * 80)
print("TOP 20 RESULTS (ALL HYPOTHESES)")
print("=" * 80)
print()

results.sort(reverse=True)
seen = set()
rank = 0
for score, desc, text in results:
    if text in seen:
        continue
    seen.add(text)
    rank += 1
    if rank > 20:
        break
    print(f"#{rank:2d} Score={score:7.1f} | {desc}")
    print(f"     {text}")
    
    # Highlight any known fragment positions
    for frag in ["BERLINCLOCK", "EASTNORTHEAST", "NORTHEAST", "BERLIN", "CLOCK"]:
        if frag in text:
            pos = text.index(frag)
            print(f"     *** Found '{frag}' at position {pos} ***")
    print()

print("=" * 80)
print(f"Total candidates tested: {len(results)}")
print("Done.")
