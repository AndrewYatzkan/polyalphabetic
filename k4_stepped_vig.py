#!/usr/bin/env python3
"""
K4 Stepped/Progressive Vigenere Analysis
=========================================
Tests multiple progressive Vigenere variants to find a second cipher layer
on top of the period-29 Vigenere already identified in Kryptos K4.

Hypotheses tested:
1. Per-period shift (delta added per full 29-char period)
2. Linear progressive shift (delta added per character)
3. Quadratic progressive shift (i^2 * delta)
4. Fibonacci/Lucas progressive shift
5. Key rotation per period
6. Column-keyed progressive (key index shifts per period)
"""

import math
import sys
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================

CT_STR = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
PERIOD = 29

# Known cribs (0-indexed positions in plaintext)
CRIB_ENE = ("EASTNORTHEAST", 21)
CRIB_BC = ("BERLINCLOCK", 63)

# Known partial key (positions 0-28), '?' = unknown
KNOWN_KEY_STR = "OYNKYELYOIECBAQK?????RDUMRIYW"

assert len(CT_STR) == 97, f"Ciphertext length is {len(CT_STR)}, expected 97"
assert len(KRYPTOS_ALPHA) == 26, f"Alphabet length is {len(KRYPTOS_ALPHA)}, expected 26"
assert len(KNOWN_KEY_STR) == 29, f"Key length is {len(KNOWN_KEY_STR)}, expected 29"

# Convert to numeric
def char_to_num(c):
    idx = KRYPTOS_ALPHA.index(c)
    return idx

def num_to_char(n):
    return KRYPTOS_ALPHA[n % 26]

CT = [char_to_num(c) for c in CT_STR]

KNOWN_KEY = []
for c in KNOWN_KEY_STR:
    if c == '?':
        KNOWN_KEY.append(None)
    else:
        KNOWN_KEY.append(char_to_num(c))

CRIB_ENE_NUMS = [char_to_num(c) for c in CRIB_ENE[0]]
CRIB_ENE_START = CRIB_ENE[1]

CRIB_BC_NUMS = [char_to_num(c) for c in CRIB_BC[0]]
CRIB_BC_START = CRIB_BC[1]

# ============================================================
# QUADGRAM SCORING
# ============================================================

print("Loading quadgram data...")
QUADGRAMS = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QUADGRAMS[parts[0]] = int(parts[1])

TOTAL_QUADGRAMS = sum(QUADGRAMS.values())
LOG_TOTAL = math.log10(TOTAL_QUADGRAMS)
FLOOR_LOG = math.log10(0.01 / TOTAL_QUADGRAMS)

QUADGRAM_LOG = {}
for qg, count in QUADGRAMS.items():
    QUADGRAM_LOG[qg] = math.log10(count) - LOG_TOTAL

def quadgram_score(text):
    text = text.upper()
    score = 0.0
    count = 0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        if qg in QUADGRAM_LOG:
            score += QUADGRAM_LOG[qg]
        else:
            score += FLOOR_LOG
        count += 1
    if count == 0:
        return -999999
    return score

def quadgram_score_per_char(text):
    text = text.upper()
    score = 0.0
    count = 0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        if qg in QUADGRAM_LOG:
            score += QUADGRAM_LOG[qg]
        else:
            score += FLOOR_LOG
        count += 1
    if count == 0:
        return -999999
    return score / count

# ============================================================
# COMMON ENGLISH WORDS
# ============================================================

COMMON_WORDS = set([
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
    "WAS", "ONE", "OUR", "OUT", "HAS", "HAD", "HOT", "HIS", "HOW", "MAN",
    "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "DID", "GET", "LET", "SAY",
    "SHE", "TOO", "USE", "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR",
    "FROM", "THEY", "BEEN", "SAID", "EACH", "MAKE", "LIKE", "LONG", "LOOK",
    "MANY", "SOME", "THEM", "THAN", "WHAT", "WHEN", "WERE", "WOULD", "THERE",
    "THEIR", "WHICH", "ABOUT", "COULD", "OTHER", "AFTER", "THESE", "FIRST",
    "NORTH", "SOUTH", "EAST", "WEST", "CLOCK", "TIME", "BERLIN", "WALL",
    "BETWEEN", "SHADOW", "UNDERGROUND", "BURIED", "SECRET", "HIDDEN",
    "SLOWLY", "DESPERATELY", "LAYER", "INVISIBLE", "IQLUSION", "ILLUSION",
    "DEGREE", "MINUTES", "SECONDS", "LATITUDE", "LONGITUDE", "LOCATION",
    "COORDINATE", "LANGLEY", "CIA", "INTELLIGENCE", "AGENCY", "PALIMPSEST",
    "ABSCISSA", "VIRTUALLY", "ONLY", "WCA", "SOS", "DIGETAL", "DIGITAL",
])

def count_english_words(text):
    text = text.upper()
    found = []
    for word in COMMON_WORDS:
        if len(word) >= 3 and word in text:
            found.append(word)
    return found

# ============================================================
# HELPERS
# ============================================================

def derive_key_from_crib(ct_nums, pt_nums, ct_start, extra_shift_func):
    derived = {}
    for j, pt_val in enumerate(pt_nums):
        i = ct_start + j
        if i >= len(ct_nums):
            break
        key_pos = i % PERIOD
        extra = extra_shift_func(i)
        key_val = (ct_nums[i] - pt_val - extra) % 26
        derived[key_pos] = key_val
    return derived

def full_decrypt(ct_nums, key_nums_29, extra_shift_func):
    pt = []
    for i in range(len(ct_nums)):
        key_pos = i % PERIOD
        if key_nums_29[key_pos] is None:
            pt.append(None)
        else:
            extra = extra_shift_func(i)
            pt_val = (ct_nums[i] - key_nums_29[key_pos] - extra) % 26
            pt.append(pt_val)
    return pt

def pt_to_string(pt_nums):
    return ''.join(num_to_char(n) if n is not None else '?' for n in pt_nums)

def check_crib_consistency(derived_from_ene, derived_from_bc):
    for pos in derived_from_ene:
        if pos in derived_from_bc:
            if derived_from_ene[pos] != derived_from_bc[pos]:
                return False
    return True

def merge_keys(derived_from_ene, derived_from_bc, base_key=None):
    merged = [None] * 29
    if base_key:
        for i in range(29):
            merged[i] = base_key[i]
    for pos, val in derived_from_ene.items():
        merged[pos] = val
    for pos, val in derived_from_bc.items():
        merged[pos] = val
    return merged

def key_to_string(key_nums):
    return ''.join(num_to_char(n) if n is not None else '?' for n in key_nums)

# ============================================================
# HYPOTHESIS 1: Per-period shift
# ct[i] = (pt[i] + key[i%29] + floor(i/29)*delta) % 26
# ============================================================

def test_per_period_shift():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 1: Per-period shift")
    print("ct[i] = (pt[i] + key[i%29] + floor(i/29)*delta) % 26")
    print("=" * 70)
    
    results = []
    
    for delta in range(26):
        extra_shift = lambda i, d=delta: (i // PERIOD) * d % 26
        
        derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
        derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
        
        consistent = check_crib_consistency(derived_ene, derived_bc)
        merged = merge_keys(derived_ene, derived_bc)
        
        if delta == 0:
            key_str = key_to_string(merged)
            print(f"\n  Delta=0 (baseline) derived key: {key_str}")
            known_match = True
            for i in range(29):
                if KNOWN_KEY[i] is not None and merged[i] is not None:
                    if KNOWN_KEY[i] != merged[i]:
                        known_match = False
                        break
            print(f"  Matches known key: {known_match}")
        
        pt_nums = full_decrypt(CT, merged, extra_shift)
        pt_str = pt_to_string(pt_nums)
        
        known_text = ''.join(c for c in pt_str if c != '?')
        if len(known_text) >= 4:
            score = quadgram_score(known_text)
            score_norm = quadgram_score_per_char(known_text)
        else:
            score = -999999
            score_norm = -999999
        
        words = count_english_words(pt_str)
        results.append((delta, consistent, key_to_string(merged), pt_str, score, score_norm, words))
    
    results.sort(key=lambda x: x[4], reverse=True)
    
    print(f"\n  Top 10 results by quadgram score:")
    print(f"  {'Delta':>5} | {'Consistent':>10} | {'Score':>10} | {'Norm':>8} | {'Words Found':>30} | Key")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*30}-+-{'-'*29}")
    
    for delta, consistent, key_str, pt_str, score, score_norm, words in results[:10]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"  {delta:>5} | {'YES' if consistent else 'NO':>10} | {score:>10.1f} | {score_norm:>8.3f} | {word_str:>30} | {key_str}")
    
    best = results[0]
    print(f"\n  Best result: delta={best[0]}, consistent={best[1]}")
    print(f"  Key: {best[2]}")
    print(f"  PT:  {best[3]}")
    print(f"  Words: {best[6]}")
    
    return results

# ============================================================
# HYPOTHESIS 2: Linear progressive shift
# ct[i] = (pt[i] + key[i%29] + i*delta) % 26
# ============================================================

def test_linear_progressive():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 2: Linear progressive shift")
    print("ct[i] = (pt[i] + key[i%29] + i*delta) % 26")
    print("=" * 70)
    
    results = []
    
    for delta in range(26):
        extra_shift = lambda i, d=delta: (i * d) % 26
        
        derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
        derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
        
        consistent = check_crib_consistency(derived_ene, derived_bc)
        merged = merge_keys(derived_ene, derived_bc)
        
        pt_nums = full_decrypt(CT, merged, extra_shift)
        pt_str = pt_to_string(pt_nums)
        
        known_text = ''.join(c for c in pt_str if c != '?')
        if len(known_text) >= 4:
            score = quadgram_score(known_text)
            score_norm = quadgram_score_per_char(known_text)
        else:
            score = -999999
            score_norm = -999999
        
        words = count_english_words(pt_str)
        results.append((delta, consistent, key_to_string(merged), pt_str, score, score_norm, words))
    
    results.sort(key=lambda x: x[4], reverse=True)
    
    print(f"\n  Top 10 results by quadgram score:")
    print(f"  {'Delta':>5} | {'Consistent':>10} | {'Score':>10} | {'Norm':>8} | {'Words Found':>30} | Key")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*30}-+-{'-'*29}")
    
    for delta, consistent, key_str, pt_str, score, score_norm, words in results[:10]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"  {delta:>5} | {'YES' if consistent else 'NO':>10} | {score:>10.1f} | {score_norm:>8.3f} | {word_str:>30} | {key_str}")
    
    best = results[0]
    print(f"\n  Best result: delta={best[0]}, consistent={best[1]}")
    print(f"  Key: {best[2]}")
    print(f"  PT:  {best[3]}")
    print(f"  Words: {best[6]}")
    
    consistent_results = [r for r in results if r[1]]
    print(f"\n  Consistent results (cribs agree): {len(consistent_results)}")
    for delta, consistent, key_str, pt_str, score, score_norm, words in consistent_results[:5]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"    delta={delta}: score={score:.1f}, key={key_str}")
        print(f"    PT: {pt_str}")
    
    return results

# ============================================================
# HYPOTHESIS 3: Quadratic progressive shift
# ct[i] = (pt[i] + key[i%29] + (i*i*delta) % 26) % 26
# ============================================================

def test_quadratic_progressive():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 3: Quadratic progressive shift")
    print("ct[i] = (pt[i] + key[i%29] + (i^2 * delta) % 26) % 26")
    print("=" * 70)
    
    results = []
    
    for delta in range(26):
        extra_shift = lambda i, d=delta: (i * i * d) % 26
        
        derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
        derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
        
        consistent = check_crib_consistency(derived_ene, derived_bc)
        merged = merge_keys(derived_ene, derived_bc)
        
        pt_nums = full_decrypt(CT, merged, extra_shift)
        pt_str = pt_to_string(pt_nums)
        
        known_text = ''.join(c for c in pt_str if c != '?')
        if len(known_text) >= 4:
            score = quadgram_score(known_text)
            score_norm = quadgram_score_per_char(known_text)
        else:
            score = -999999
            score_norm = -999999
        
        words = count_english_words(pt_str)
        results.append((delta, consistent, key_to_string(merged), pt_str, score, score_norm, words))
    
    results.sort(key=lambda x: x[4], reverse=True)
    
    print(f"\n  Top 10 results by quadgram score:")
    print(f"  {'Delta':>5} | {'Consistent':>10} | {'Score':>10} | {'Norm':>8} | {'Words Found':>30} | Key")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*30}-+-{'-'*29}")
    
    for delta, consistent, key_str, pt_str, score, score_norm, words in results[:10]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"  {delta:>5} | {'YES' if consistent else 'NO':>10} | {score:>10.1f} | {score_norm:>8.3f} | {word_str:>30} | {key_str}")
    
    best = results[0]
    print(f"\n  Best result: delta={best[0]}, consistent={best[1]}")
    print(f"  Key: {best[2]}")
    print(f"  PT:  {best[3]}")
    
    return results

# ============================================================
# HYPOTHESIS 4: Fibonacci/Lucas progressive shift
# ============================================================

def generate_fibonacci(n):
    fib = [0, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

def generate_lucas(n):
    luc = [2, 1]
    while len(luc) < n:
        luc.append(luc[-1] + luc[-2])
    return luc[:n]

def generate_tribonacci(n):
    tri = [0, 0, 1]
    while len(tri) < n:
        tri.append(tri[-1] + tri[-2] + tri[-3])
    return tri[:n]

def test_fibonacci_progressive():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 4: Fibonacci/Lucas progressive shift")
    print("ct[i] = (pt[i] + key[i%29] + seq[i]*scale) % 26")
    print("=" * 70)
    
    n = len(CT)
    fib = generate_fibonacci(n)
    luc = generate_lucas(n)
    tri = generate_tribonacci(n)
    
    fib_cumsum = [0] * n
    fib_cumsum[0] = fib[0]
    for i in range(1, n):
        fib_cumsum[i] = fib_cumsum[i-1] + fib[i]
    
    sequences = {
        "Fibonacci": fib,
        "Lucas": luc,
        "Tribonacci": tri,
        "Fibonacci_cumsum": fib_cumsum,
    }
    
    all_results = []
    
    for seq_name, seq in sequences.items():
        results = []
        for scale in range(26):
            extra_shift = lambda i, s=scale, sq=seq: (sq[i] * s) % 26
            
            derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
            derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
            
            consistent = check_crib_consistency(derived_ene, derived_bc)
            merged = merge_keys(derived_ene, derived_bc)
            
            pt_nums = full_decrypt(CT, merged, extra_shift)
            pt_str = pt_to_string(pt_nums)
            
            known_text = ''.join(c for c in pt_str if c != '?')
            if len(known_text) >= 4:
                score = quadgram_score(known_text)
                score_norm = quadgram_score_per_char(known_text)
            else:
                score = -999999
                score_norm = -999999
            
            words = count_english_words(pt_str)
            results.append((scale, consistent, key_to_string(merged), pt_str, score, score_norm, words))
        
        results.sort(key=lambda x: x[4], reverse=True)
        
        print(f"\n  Sequence: {seq_name}")
        print(f"  Top 3 results:")
        for scale, consistent, key_str, pt_str, score, score_norm, words in results[:3]:
            word_str = ','.join(words[:5]) if words else '-'
            print(f"    scale={scale}, consistent={'Y' if consistent else 'N'}, score={score:.1f}, norm={score_norm:.3f}, words=[{word_str}]")
            print(f"    Key: {key_str}")
            print(f"    PT:  {pt_str}")
        
        all_results.extend([(seq_name, *r) for r in results])
    
    all_results.sort(key=lambda x: x[5], reverse=True)
    print(f"\n  Overall best: {all_results[0][0]}, scale={all_results[0][1]}")
    print(f"  PT: {all_results[0][4]}")
    
    return all_results

# ============================================================
# HYPOTHESIS 5: Key rotation per period
# ============================================================

def test_key_rotation():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 5: Key rotation per period")
    print("Period p: key_pos = (i%29 + floor(i/29)*delta) % 29")
    print("=" * 70)
    
    results = []
    
    for delta in range(29):
        def get_key_pos(i, d=delta):
            return (i % PERIOD + (i // PERIOD) * d) % PERIOD
        
        derived_ene = {}
        for j, pt_val in enumerate(CRIB_ENE_NUMS):
            i = CRIB_ENE_START + j
            if i >= len(CT):
                break
            kp = get_key_pos(i)
            key_val = (CT[i] - pt_val) % 26
            if kp in derived_ene and derived_ene[kp] != key_val:
                derived_ene[kp] = None
            else:
                derived_ene[kp] = key_val
        
        derived_bc = {}
        for j, pt_val in enumerate(CRIB_BC_NUMS):
            i = CRIB_BC_START + j
            if i >= len(CT):
                break
            kp = get_key_pos(i)
            key_val = (CT[i] - pt_val) % 26
            if kp in derived_bc and derived_bc[kp] != key_val:
                derived_bc[kp] = None
            else:
                derived_bc[kp] = key_val
        
        consistent = True
        for pos in derived_ene:
            if derived_ene[pos] is None:
                consistent = False
                break
            if pos in derived_bc:
                if derived_bc[pos] is None or derived_ene[pos] != derived_bc[pos]:
                    consistent = False
                    break
        
        merged = [None] * 29
        for pos, val in derived_ene.items():
            if val is not None:
                merged[pos] = val
        for pos, val in derived_bc.items():
            if val is not None:
                merged[pos] = val
        
        pt = []
        for i in range(len(CT)):
            kp = get_key_pos(i)
            if merged[kp] is None:
                pt.append(None)
            else:
                pt_val = (CT[i] - merged[kp]) % 26
                pt.append(pt_val)
        
        pt_str = pt_to_string(pt)
        known_text = ''.join(c for c in pt_str if c != '?')
        if len(known_text) >= 4:
            score = quadgram_score(known_text)
            score_norm = quadgram_score_per_char(known_text)
        else:
            score = -999999
            score_norm = -999999
        
        words = count_english_words(pt_str)
        results.append((delta, consistent, key_to_string(merged), pt_str, score, score_norm, words))
    
    results.sort(key=lambda x: x[4], reverse=True)
    
    print(f"\n  Top 10 results by quadgram score:")
    print(f"  {'Delta':>5} | {'Consistent':>10} | {'Score':>10} | {'Norm':>8} | {'Words Found':>30} | Key")
    print(f"  {'-'*5}-+-{'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*30}-+-{'-'*29}")
    
    for delta, consistent, key_str, pt_str, score, score_norm, words in results[:10]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"  {delta:>5} | {'YES' if consistent else 'NO':>10} | {score:>10.1f} | {score_norm:>8.3f} | {word_str:>30} | {key_str}")
    
    consistent_results = [r for r in results if r[1]]
    print(f"\n  Consistent results: {len(consistent_results)}")
    for delta, consistent, key_str, pt_str, score, score_norm, words in consistent_results[:5]:
        print(f"    delta={delta}: score={score:.1f}, key={key_str}")
        print(f"    PT: {pt_str}")
    
    return results

# ============================================================
# HYPOTHESIS 6: Column-keyed progressive / Per-position key progression
# ============================================================

def test_column_keyed_progressive():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 6: Per-position key progression")
    print("key_p[j] = base_key[j] + p * delta_j  (per-position delta)")
    print("Also: uniform delta across all positions (sub-case of H1)")
    print("=" * 70)
    
    # Collect equations: for each (key_position, period), what effective key value?
    equations = {}
    
    for j, pt_val in enumerate(CRIB_ENE_NUMS):
        i = CRIB_ENE_START + j
        if i >= len(CT):
            break
        kp = i % PERIOD
        period = i // PERIOD
        eff_key = (CT[i] - pt_val) % 26
        if kp not in equations:
            equations[kp] = []
        equations[kp].append((period, eff_key))
    
    for j, pt_val in enumerate(CRIB_BC_NUMS):
        i = CRIB_BC_START + j
        if i >= len(CT):
            break
        kp = i % PERIOD
        period = i // PERIOD
        eff_key = (CT[i] - pt_val) % 26
        if kp not in equations:
            equations[kp] = []
        equations[kp].append((period, eff_key))
    
    print(f"\n  Equations collected per key position:")
    for kp in sorted(equations.keys()):
        eqs = equations[kp]
        eq_str = ', '.join(f"p{p}={num_to_char(v)}({v})" for p, v in eqs)
        print(f"    pos {kp:2d}: {eq_str}")
    
    # For positions with multiple period observations, derive delta
    print(f"\n  Positions with multiple period observations:")
    for kp in sorted(equations.keys()):
        eqs = equations[kp]
        if len(eqs) >= 2:
            for i_eq in range(len(eqs)):
                for j_eq in range(i_eq + 1, len(eqs)):
                    p1, v1 = eqs[i_eq]
                    p2, v2 = eqs[j_eq]
                    if p1 != p2:
                        dp = p2 - p1
                        dv = (v2 - v1) % 26
                        found_delta = None
                        for d in range(26):
                            if (dp * d) % 26 == dv:
                                found_delta = d
                                break
                        if found_delta is not None:
                            base = (v1 - p1 * found_delta) % 26
                            print(f"    pos {kp:2d}: periods {p1},{p2} -> delta={found_delta} ({num_to_char(found_delta)}), base={base} ({num_to_char(base)})")
                        else:
                            print(f"    pos {kp:2d}: periods {p1},{p2} -> NO SOLUTION (dp={dp}, dv={dv})")
    
    # Test uniform delta
    print(f"\n  Testing uniform delta (all positions same delta):")
    consistent_deltas = []
    for test_delta in range(26):
        base_key = [None] * 29
        consistent = True
        for kp in equations:
            eqs = equations[kp]
            base_values = set()
            for p, v in eqs:
                base = (v - p * test_delta) % 26
                base_values.add(base)
            if len(base_values) > 1:
                consistent = False
                break
            base_key[kp] = base_values.pop()
        
        if consistent:
            pt = []
            for i in range(len(CT)):
                kp = i % PERIOD
                period = i // PERIOD
                if base_key[kp] is None:
                    pt.append(None)
                else:
                    eff_key = (base_key[kp] + period * test_delta) % 26
                    pt_val = (CT[i] - eff_key) % 26
                    pt.append(pt_val)
            
            pt_str = pt_to_string(pt)
            known_text = ''.join(c for c in pt_str if c != '?')
            score = quadgram_score(known_text) if len(known_text) >= 4 else -999999
            
            words = count_english_words(pt_str)
            word_str = ','.join(words[:5]) if words else '-'
            
            consistent_deltas.append(test_delta)
            print(f"    delta={test_delta:2d}: CONSISTENT, score={score:.1f}, words=[{word_str}]")
            print(f"      base_key: {key_to_string(base_key)}")
            print(f"      PT: {pt_str}")
    
    if not consistent_deltas:
        print(f"    No uniform delta found consistent with both cribs.")
        print(f"    (This is expected if the cribs span different periods with overlapping key positions)")
    
    return equations

# ============================================================
# HYPOTHESIS 7: Cumulative ciphertext shift
# ============================================================

def test_autokey_progressive():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 7: Cumulative ciphertext-based shift")
    print("shift[i] = (sum(ct[0..i-1]) * scale) % 26")
    print("=" * 70)
    
    ct_cumsum = [0] * (len(CT) + 1)
    for i in range(len(CT)):
        ct_cumsum[i + 1] = ct_cumsum[i] + CT[i]
    
    results = []
    for scale in range(26):
        extra_shift = lambda i, s=scale: (ct_cumsum[i] * s) % 26
        
        derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
        derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
        
        consistent = check_crib_consistency(derived_ene, derived_bc)
        merged = merge_keys(derived_ene, derived_bc)
        
        pt_nums = full_decrypt(CT, merged, extra_shift)
        pt_str = pt_to_string(pt_nums)
        
        known_text = ''.join(c for c in pt_str if c != '?')
        score = quadgram_score(known_text) if len(known_text) >= 4 else -999999
        score_norm = quadgram_score_per_char(known_text) if len(known_text) >= 4 else -999999
        
        words = count_english_words(pt_str)
        results.append(("ct_cumsum", scale, consistent, key_to_string(merged), pt_str, score, score_norm, words))
    
    results.sort(key=lambda x: x[5], reverse=True)
    
    print(f"\n  Top 5:")
    for name, scale, consistent, key_str, pt_str, score, score_norm, words in results[:5]:
        word_str = ','.join(words[:5]) if words else '-'
        print(f"    scale={scale}, consistent={'Y' if consistent else 'N'}, score={score:.1f}, words=[{word_str}]")
        if consistent:
            print(f"    Key: {key_str}")
            print(f"    PT:  {pt_str}")
    
    return results

# ============================================================
# HYPOTHESIS 8: Various position-modular shifts
# ============================================================

def test_modular_shifts():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 8: Various position-modular shifts")
    print("=" * 70)
    
    all_results = []
    
    shift_functions = {
        "i%29": lambda i: i % 29,
        "i%13": lambda i: i % 13,
        "(i//29)*(i%29)": lambda i: ((i // 29) * (i % 29)) % 26,
        "triangular(i)": lambda i: (i * (i + 1) // 2) % 26,
        "i^3": lambda i: (i * i * i) % 26,
        "2^i": lambda i: pow(2, i, 26),
        "3^i": lambda i: pow(3, i, 26),
        "i*floor(i/29)": lambda i: (i * (i // 29)) % 26,
    }
    
    for name, func in shift_functions.items():
        results = []
        for scale in range(26):
            extra_shift = lambda i, s=scale, f=func: (f(i) * s) % 26
            
            derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
            derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
            
            consistent = check_crib_consistency(derived_ene, derived_bc)
            merged = merge_keys(derived_ene, derived_bc)
            
            pt_nums = full_decrypt(CT, merged, extra_shift)
            pt_str = pt_to_string(pt_nums)
            
            known_text = ''.join(c for c in pt_str if c != '?')
            score = quadgram_score(known_text) if len(known_text) >= 4 else -999999
            score_norm = quadgram_score_per_char(known_text) if len(known_text) >= 4 else -999999
            
            words = count_english_words(pt_str)
            results.append((scale, consistent, key_to_string(merged), pt_str, score, score_norm, words))
        
        results.sort(key=lambda x: x[4], reverse=True)
        best = results[0]
        consistent_best = [r for r in results if r[1]]
        
        word_str = ','.join(best[6][:5]) if best[6] else '-'
        print(f"\n  f(i) = {name}:")
        print(f"    Best: scale={best[0]}, consistent={'Y' if best[1] else 'N'}, score={best[4]:.1f}, words=[{word_str}]")
        if consistent_best:
            cb = max(consistent_best, key=lambda x: x[4])
            word_str2 = ','.join(cb[6][:5]) if cb[6] else '-'
            print(f"    Best consistent: scale={cb[0]}, score={cb[4]:.1f}, words=[{word_str2}]")
            print(f"    Key: {cb[2]}")
            print(f"    PT:  {cb[3]}")
        
        all_results.extend([(name, *r) for r in results])
    
    return all_results

# ============================================================
# HYPOTHESIS 9: Variable delta per period
# ============================================================

def test_variable_period_deltas():
    print("\n" + "=" * 70)
    print("HYPOTHESIS 9: Variable delta per period")
    print("Period 0: no extra shift")
    print("Period 1: extra shift = d1")  
    print("Period 2: extra shift = d2")
    print("Period 3: extra shift = d3")
    print("(97 chars = 3 full periods of 29 + 10 in period 3)")
    print("=" * 70)
    
    # Period 0 of ENE: positions 21-28
    base_from_p0 = {}
    for j in range(8):
        i = CRIB_ENE_START + j
        kp = i % PERIOD
        key_val = (CT[i] - CRIB_ENE_NUMS[j]) % 26
        base_from_p0[kp] = key_val
    
    # Period 1 of ENE: positions 29-33
    ene_p1 = {}
    for j in range(8, 13):
        i = CRIB_ENE_START + j
        kp = i % PERIOD
        key_val_plus_d1 = (CT[i] - CRIB_ENE_NUMS[j]) % 26
        ene_p1[kp] = key_val_plus_d1
    
    # BERLINCLOCK: positions 63-73, period 2
    bc_p2 = {}
    for j, pt_val in enumerate(CRIB_BC_NUMS):
        i = CRIB_BC_START + j
        kp = i % PERIOD
        key_val_plus_d2 = (CT[i] - pt_val) % 26
        bc_p2[kp] = key_val_plus_d2
    
    print(f"\n  Base key from period 0 (positions 21-28):")
    for kp in sorted(base_from_p0.keys()):
        print(f"    key[{kp}] = {base_from_p0[kp]} ({num_to_char(base_from_p0[kp])})")
    
    print(f"\n  Key+d1 from period 1 (positions 0-4):")
    for kp in sorted(ene_p1.keys()):
        print(f"    key[{kp}]+d1 = {ene_p1[kp]} ({num_to_char(ene_p1[kp])})")
    
    print(f"\n  Key+d2 from period 2 (positions 5-15):")
    for kp in sorted(bc_p2.keys()):
        print(f"    key[{kp}]+d2 = {bc_p2[kp]} ({num_to_char(bc_p2[kp])})")
    
    # Use known key to determine d1 and d2
    print(f"\n  Using known key to determine d1:")
    d1_values = []
    for kp in ene_p1:
        if KNOWN_KEY[kp] is not None:
            d1 = (ene_p1[kp] - KNOWN_KEY[kp]) % 26
            print(f"    From key[{kp}]: d1 = ({ene_p1[kp]} - {KNOWN_KEY[kp]}) % 26 = {d1} ({num_to_char(d1)})")
            d1_values.append(d1)
    
    print(f"\n  Using known key to determine d2:")
    d2_values = []
    for kp in bc_p2:
        if KNOWN_KEY[kp] is not None:
            d2 = (bc_p2[kp] - KNOWN_KEY[kp]) % 26
            print(f"    From key[{kp}]: d2 = ({bc_p2[kp]} - {KNOWN_KEY[kp]}) % 26 = {d2} ({num_to_char(d2)})")
            d2_values.append(d2)
    
    d1_set = set(d1_values)
    d2_set = set(d2_values)
    
    if len(d1_set) == 1:
        print(f"\n  CONSISTENT d1 = {d1_set.pop()}")
    elif len(d1_set) > 1:
        print(f"\n  INCONSISTENT d1 values: {d1_set}")
    
    if len(d2_set) == 1:
        print(f"  CONSISTENT d2 = {d2_set.pop()}")
    elif len(d2_set) > 1:
        print(f"  INCONSISTENT d2 values: {d2_set}")
    
    # Brute force d1, d2, d3
    print(f"\n  Brute-forcing d1, d2, d3 (26^3 = {26**3} combos)...")
    
    best_results = []
    
    for d1 in range(26):
        for d2 in range(26):
            for d3 in range(26):
                deltas = [0, d1, d2, d3]
                
                full_key = [None] * 29
                for kp in range(29):
                    if KNOWN_KEY[kp] is not None:
                        full_key[kp] = KNOWN_KEY[kp]
                
                for kp, val in base_from_p0.items():
                    full_key[kp] = val
                for kp, val in ene_p1.items():
                    full_key[kp] = (val - d1) % 26
                for kp, val in bc_p2.items():
                    full_key[kp] = (val - d2) % 26
                
                pt = []
                for i in range(len(CT)):
                    kp = i % PERIOD
                    period = i // PERIOD
                    if full_key[kp] is None:
                        pt.append(None)
                    else:
                        eff_key = (full_key[kp] + deltas[period]) % 26
                        pt_val = (CT[i] - eff_key) % 26
                        pt.append(pt_val)
                
                pt_str = pt_to_string(pt)
                known_text = ''.join(c for c in pt_str if c != '?')
                score = quadgram_score(known_text) if len(known_text) >= 4 else -999999
                
                if len(best_results) < 30 or score > best_results[-1][5]:
                    best_results.append((d1, d2, d3, key_to_string(full_key), pt_str, score))
                    best_results.sort(key=lambda x: x[5], reverse=True)
                    best_results = best_results[:30]
    
    print(f"\n  Top 20 results:")
    for rank, (d1, d2, d3, key_str, pt_str, score) in enumerate(best_results[:20]):
        words = count_english_words(pt_str)
        word_str = ','.join(words[:5]) if words else '-'
        print(f"    #{rank+1}: d1={d1},d2={d2},d3={d3}, score={score:.1f}, words=[{word_str}]")
        print(f"         key={key_str}")
        print(f"         PT:  {pt_str}")
    
    return best_results

# ============================================================
# BRUTEFORCE: 5 unknown key positions
# ============================================================

def test_unknown_key_bruteforce():
    print("\n" + "=" * 70)
    print("BRUTEFORCE: Testing all 26^5 possibilities for unknown key positions")
    print("Using baseline (delta=0) with cribs + known key")
    print("=" * 70)
    
    extra_shift = lambda i: 0
    derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift)
    derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift)
    
    merged = merge_keys(derived_ene, derived_bc)
    
    for i in range(29):
        if KNOWN_KEY[i] is not None and merged[i] is None:
            merged[i] = KNOWN_KEY[i]
    
    unknown_pos = [i for i in range(29) if merged[i] is None]
    print(f"  Known key positions from cribs+known: {key_to_string(merged)}")
    print(f"  Unknown positions: {unknown_pos}")
    print(f"  Search space: 26^{len(unknown_pos)} = {26**len(unknown_pos)}")
    
    if len(unknown_pos) > 5:
        print("  Too many unknowns for brute force, skipping.")
        return []
    
    if len(unknown_pos) == 0:
        pt_nums = full_decrypt(CT, merged, extra_shift)
        pt_str = pt_to_string(pt_nums)
        score = quadgram_score(pt_str)
        print(f"  All positions known!")
        print(f"  PT: {pt_str}")
        print(f"  Score: {score:.1f}")
        return [(merged, pt_str, score)]
    
    best_results = []
    total = 26 ** len(unknown_pos)
    
    for combo_idx in range(total):
        test_key = merged[:]
        idx = combo_idx
        for pos in unknown_pos:
            test_key[pos] = idx % 26
            idx //= 26
        
        pt_nums = full_decrypt(CT, test_key, extra_shift)
        pt_str = pt_to_string(pt_nums)
        score = quadgram_score(pt_str)
        
        if len(best_results) < 20 or score > best_results[-1][2]:
            best_results.append((test_key[:], pt_str, score))
            best_results.sort(key=lambda x: x[2], reverse=True)
            best_results = best_results[:20]
        
        if combo_idx % 500000 == 0 and combo_idx > 0:
            pct = 100 * combo_idx / total
            print(f"  Progress: {combo_idx}/{total} ({pct:.1f}%)")
    
    print(f"\n  Top 20 results:")
    for rank, (key, pt, score) in enumerate(best_results):
        words = count_english_words(pt)
        word_str = ','.join(words[:5]) if words else '-'
        print(f"    #{rank+1}: score={score:.1f}, key={key_to_string(key)}, words=[{word_str}]")
        print(f"         PT: {pt}")
    
    return best_results

# ============================================================
# MAIN
# ============================================================

def main():
    print("K4 STEPPED/PROGRESSIVE VIGENERE ANALYSIS")
    print("=" * 70)
    print(f"Ciphertext: {CT_STR}")
    print(f"Length: {len(CT_STR)}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Period: {PERIOD}")
    print(f"Known key: {KNOWN_KEY_STR}")
    print(f"Cribs: EASTNORTHEAST@{CRIB_ENE_START}, BERLINCLOCK@{CRIB_BC_START}")
    
    # Baseline
    print("\n" + "=" * 70)
    print("BASELINE: Standard period-29 Vigenere with known partial key")
    print("=" * 70)
    
    extra_shift_zero = lambda i: 0
    derived_ene = derive_key_from_crib(CT, CRIB_ENE_NUMS, CRIB_ENE_START, extra_shift_zero)
    derived_bc = derive_key_from_crib(CT, CRIB_BC_NUMS, CRIB_BC_START, extra_shift_zero)
    merged_baseline = merge_keys(derived_ene, derived_bc)
    
    for i in range(29):
        if KNOWN_KEY[i] is not None and merged_baseline[i] is None:
            merged_baseline[i] = KNOWN_KEY[i]
    
    pt_baseline = full_decrypt(CT, merged_baseline, extra_shift_zero)
    pt_baseline_str = pt_to_string(pt_baseline)
    
    print(f"  Key:       {key_to_string(merged_baseline)}")
    print(f"  Plaintext: {pt_baseline_str}")
    known_text = ''.join(c for c in pt_baseline_str if c != '?')
    baseline_score = quadgram_score(known_text)
    baseline_words = count_english_words(pt_baseline_str)
    print(f"  Score:     {baseline_score:.1f}")
    print(f"  Words:     {baseline_words}")
    
    # Run all hypothesis tests
    r1 = test_per_period_shift()
    r2 = test_linear_progressive()
    r3 = test_quadratic_progressive()
    r4 = test_fibonacci_progressive()
    r5 = test_key_rotation()
    r6 = test_column_keyed_progressive()
    r7 = test_autokey_progressive()
    r8 = test_modular_shifts()
    r9 = test_variable_period_deltas()
    r_bf = test_unknown_key_bruteforce()
    
    # ============================================================
    # GRAND SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("GRAND SUMMARY")
    print("=" * 70)
    print(f"\n  Baseline score: {baseline_score:.1f}")
    print(f"  Baseline words: {baseline_words}")
    
    summaries = []
    
    if r1:
        best_h1 = max(r1, key=lambda x: x[4])
        summaries.append(("H1 Per-period shift", f"delta={best_h1[0]}", best_h1[4], best_h1[6], best_h1[3], best_h1[1]))
    
    if r2:
        best_h2 = max(r2, key=lambda x: x[4])
        summaries.append(("H2 Linear progressive", f"delta={best_h2[0]}", best_h2[4], best_h2[6], best_h2[3], best_h2[1]))
    
    if r3:
        best_h3 = max(r3, key=lambda x: x[4])
        summaries.append(("H3 Quadratic progressive", f"delta={best_h3[0]}", best_h3[4], best_h3[6], best_h3[3], best_h3[1]))
    
    if r4:
        best_h4_list = [(name, *rest) for (name, *rest) in r4]
        best_h4 = max(best_h4_list, key=lambda x: x[5])
        summaries.append(("H4 Fibonacci/Lucas", f"{best_h4[0]},s={best_h4[1]}", best_h4[5], best_h4[7], best_h4[4], best_h4[2]))
    
    if r5:
        best_h5 = max(r5, key=lambda x: x[4])
        summaries.append(("H5 Key rotation", f"delta={best_h5[0]}", best_h5[4], best_h5[6], best_h5[3], best_h5[1]))
    
    if r7:
        best_h7 = max(r7, key=lambda x: x[5])
        summaries.append(("H7 CT cumsum shift", f"scale={best_h7[1]}", best_h7[5], best_h7[7], best_h7[4], best_h7[2]))
    
    if r9:
        best_h9 = max(r9, key=lambda x: x[5])
        summaries.append(("H9 Variable per-period", f"d1={best_h9[0]},d2={best_h9[1]},d3={best_h9[2]}", best_h9[5], count_english_words(best_h9[4]), best_h9[4], True))
    
    if r_bf:
        best_bf = max(r_bf, key=lambda x: x[2])
        summaries.append(("BF Unknown positions", key_to_string(best_bf[0]), best_bf[2], count_english_words(best_bf[1]), best_bf[1], True))
    
    print(f"\n  {'Hypothesis':<30} | {'Param':<25} | {'Score':>10} | {'Consistent':>10} | Words")
    print(f"  {'-'*30}-+-{'-'*25}-+-{'-'*10}-+-{'-'*10}-+------")
    for name, param, score, words, pt, consistent in sorted(summaries, key=lambda x: x[2], reverse=True):
        word_str = ','.join(words[:5]) if words else '-'
        print(f"  {name:<30} | {str(param):<25} | {score:>10.1f} | {'YES' if consistent else 'NO':>10} | {word_str}")
    
    print(f"\n  Best plaintexts:")
    for name, param, score, words, pt, consistent in sorted(summaries, key=lambda x: x[2], reverse=True)[:5]:
        print(f"\n  {name} (param={param}, score={score:.1f}, consistent={consistent}):")
        print(f"  PT: {pt}")
        print(f"  Words: {words}")


if __name__ == "__main__":
    main()
