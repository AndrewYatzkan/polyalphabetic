#!/usr/bin/env python3
"""
CRITICAL INSIGHT: The two cribs EASTNORTHEAST@21 and BERLINCLOCK@63 cover
COMPLETELY DISJOINT key positions mod 29. This means period 29 has NEVER
been cross-validated! Other periods might be equally valid.

This script:
1. Tests ALL periods 2-97 for crib consistency
2. For each valid period, derives the key from cribs
3. Brute-forces any remaining unknown positions
4. Scores with quadgram analysis

If there's a period != 29 that works, it could break the cipher.
"""
import math, time
from collections import Counter
from itertools import product

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

# Cribs
CRIB1_TEXT = "EASTNORTHEAST"
CRIB1_START = 21
CRIB2_TEXT = "BERLINCLOCK"
CRIB2_START = 63

print("=" * 80)
print("PERIOD CONSISTENCY TEST")
print("=" * 80)

valid_periods = []

for period in range(2, 98):
    # Derive key positions from both cribs
    key = {}
    conflict = False

    # From EASTNORTHEAST@21
    for j, pt_char in enumerate(CRIB1_TEXT):
        ct_pos = CRIB1_START + j
        kp = ct_pos % period
        key_val = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26
        if kp in key:
            if key[kp] != key_val:
                conflict = True
                break
        else:
            key[kp] = key_val

    if conflict:
        continue

    # From BERLINCLOCK@63
    for j, pt_char in enumerate(CRIB2_TEXT):
        ct_pos = CRIB2_START + j
        kp = ct_pos % period
        key_val = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26
        if kp in key:
            if key[kp] != key_val:
                conflict = True
                break
        else:
            key[kp] = key_val

    if conflict:
        continue

    # Count known and unknown positions
    known = len(key)
    unknown = period - known

    valid_periods.append((period, known, unknown))

    # Show all valid periods
    key_str = ''.join(KRYPTOS[key[i]] if i in key else '?' for i in range(period))

    if unknown <= 8:  # Potentially brute-forceable
        marker = "*** BRUTE-FORCEABLE ***" if unknown <= 5 else f"(2^{unknown*4.7:.0f} combos)"
        print(f"\n  Period {period:2d}: key={key_str} ({known} known, {unknown} unknown) {marker}")
    elif unknown == 0:
        print(f"\n  Period {period:2d}: key={key_str} (FULLY DETERMINED!)")
    else:
        print(f"  Period {period:2d}: {known} known, {unknown} unknown")

print(f"\n\nTotal valid periods: {len(valid_periods)}")
print(f"Brute-forceable (≤5 unknowns): {[p for p, k, u in valid_periods if u <= 5]}")
print(f"Fully determined: {[p for p, k, u in valid_periods if u == 0]}")

# Now brute-force ALL periods with ≤5 unknowns
print("\n" + "=" * 80)
print("BRUTE-FORCE SEARCH FOR ALL LOW-UNKNOWN PERIODS")
print("=" * 80)

results = []

for period, known, unknown in valid_periods:
    if unknown > 5:
        continue
    if unknown == 0:
        # Fully determined - just decrypt
        key = {}
        for j, pt_char in enumerate(CRIB1_TEXT):
            ct_pos = CRIB1_START + j
            kp = ct_pos % period
            key[kp] = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26
        for j, pt_char in enumerate(CRIB2_TEXT):
            ct_pos = CRIB2_START + j
            kp = ct_pos % period
            key[kp] = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26

        key_str = ''.join(KRYPTOS[key[i]] for i in range(period))
        pt = vig_decrypt(K4, key_str)
        s = qscore(pt)
        results.append((s, period, key_str, pt))
        print(f"\n  Period {period}: score={s:.2f}")
        print(f"    Key: {key_str}")
        print(f"    PT:  {pt}")
        continue

    # Get key structure
    key_base = {}
    for j, pt_char in enumerate(CRIB1_TEXT):
        ct_pos = CRIB1_START + j
        kp = ct_pos % period
        key_base[kp] = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26
    for j, pt_char in enumerate(CRIB2_TEXT):
        ct_pos = CRIB2_START + j
        kp = ct_pos % period
        key_base[kp] = (k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26

    unknown_positions = [i for i in range(period) if i not in key_base]

    print(f"\n  Period {period}: {unknown} unknown positions {unknown_positions}")

    best_score = -999999
    best_key = None
    best_pt = None
    count = 0

    t0 = time.time()
    for combo in product(range(26), repeat=unknown):
        key_full = dict(key_base)
        for idx, pos in enumerate(unknown_positions):
            key_full[pos] = combo[idx]

        key_str = ''.join(KRYPTOS[key_full[i]] for i in range(period))
        pt = vig_decrypt(K4, key_str)
        s = qscore(pt)

        if s > best_score:
            best_score = s
            best_key = key_str
            best_pt = pt

        count += 1
        if count % 1000000 == 0:
            elapsed = time.time() - t0
            print(f"    {count/26**unknown*100:.1f}% done ({elapsed:.0f}s) best={best_score:.2f}")

    elapsed = time.time() - t0
    results.append((best_score, period, best_key, best_pt))
    print(f"  Period {period}: DONE in {elapsed:.1f}s")
    print(f"    Best score: {best_score:.2f}")
    print(f"    Best key:   {best_key}")
    print(f"    Best PT:    {best_pt}")

    # Check for crib words in non-crib positions
    crib_words = ["BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST", "SLOWLY", "DESPERATELY",
                  "BETWEEN", "SHADOW", "LAYER", "BURIED", "HIDDEN", "SECRET", "DEGREE",
                  "BEARING", "COMPASS", "POINT", "GRID", "HOLD", "UNDER", "GROUND",
                  "TIME", "HOUR", "LIGHT", "DARK", "NIGHT", "WATCH", "TOWER",
                  "THAT", "THIS", "THEY", "WHAT", "WITH", "HAVE", "FROM",
                  "THERE", "WHERE", "WHICH", "THEIR", "ABOUT", "COULD", "WOULD"]
    found = [w for w in crib_words if w in best_pt]
    if found:
        # Check if words are outside crib regions
        non_crib_words = []
        for w in found:
            pos = best_pt.index(w)
            if not (21 <= pos <= 33 or 63 <= pos <= 73):
                non_crib_words.append((w, pos))
            elif best_pt.count(w) > 1:  # Also appears elsewhere
                for p in range(len(best_pt)):
                    if best_pt[p:p+len(w)] == w and not (21 <= p <= 33 or 63 <= p <= 73):
                        non_crib_words.append((w, p))
        if non_crib_words:
            print(f"    *** NON-CRIB WORDS: {non_crib_words} ***")

# Also test Beaufort for all valid periods with ≤5 unknowns
print("\n" + "=" * 80)
print("BEAUFORT VARIANT FOR ALL LOW-UNKNOWN PERIODS")
print("=" * 80)

def beaufort_decrypt(ct, key):
    pt = []
    for i, c in enumerate(ct):
        ki = k_idx(key[i % len(key)])
        ci = k_idx(c)
        pt.append(k_chr((ki - ci) % 26))
    return ''.join(pt)

for period, known, unknown in valid_periods:
    if unknown > 5:
        continue

    # Derive Beaufort key from cribs: key = (CT + PT) mod 26? No.
    # Beaufort: CT = key - PT mod 26, so PT = key - CT mod 26
    # Key = CT + PT mod 26
    key_base = {}
    conflict = False
    for j, pt_char in enumerate(CRIB1_TEXT):
        ct_pos = CRIB1_START + j
        kp = ct_pos % period
        key_val = (k_idx(K4[ct_pos]) + k_idx(pt_char)) % 26
        if kp in key_base:
            if key_base[kp] != key_val:
                conflict = True
                break
        else:
            key_base[kp] = key_val
    if conflict:
        continue

    for j, pt_char in enumerate(CRIB2_TEXT):
        ct_pos = CRIB2_START + j
        kp = ct_pos % period
        key_val = (k_idx(K4[ct_pos]) + k_idx(pt_char)) % 26
        if kp in key_base:
            if key_base[kp] != key_val:
                conflict = True
                break
        else:
            key_base[kp] = key_val
    if conflict:
        print(f"  Beaufort Period {period}: CONFLICT in crib key derivation")
        continue

    unknown_positions = [i for i in range(period) if i not in key_base]

    if unknown == 0:
        key_str = ''.join(KRYPTOS[key_base[i]] for i in range(period))
        pt = beaufort_decrypt(K4, key_str)
        s = qscore(pt)
        results.append((s, period, f"B:{key_str}", pt))
        if s > -550:
            print(f"\n  Beaufort Period {period}: score={s:.2f}")
            print(f"    Key: {key_str}")
            print(f"    PT:  {pt}")
        continue

    best_score = -999999
    best_key = None
    best_pt = None

    for combo in product(range(26), repeat=unknown):
        key_full = dict(key_base)
        for idx, pos in enumerate(unknown_positions):
            key_full[pos] = combo[idx]

        key_str = ''.join(KRYPTOS[key_full[i]] for i in range(period))
        pt = beaufort_decrypt(K4, key_str)
        s = qscore(pt)

        if s > best_score:
            best_score = s
            best_key = key_str
            best_pt = pt

    results.append((best_score, period, f"B:{best_key}", best_pt))
    if best_score > -550:
        print(f"\n  Beaufort Period {period}: Best score={best_score:.2f}")
        print(f"    Key: {best_key}")
        print(f"    PT:  {best_pt}")

# Sort and show top results
print("\n" + "=" * 80)
print("TOP 20 RESULTS ACROSS ALL PERIODS AND VARIANTS")
print("=" * 80)
results.sort(key=lambda x: -x[0])
for i, (score, period, key, pt) in enumerate(results[:20]):
    print(f"\n  #{i+1}: Period {period}, Score {score:.2f}")
    print(f"    Key: {key}")
    print(f"    PT:  {pt}")
    # Highlight any English words
    for w in ["THE", "AND", "THAT", "WITH", "FROM", "THIS", "HAVE", "WILL",
              "BERLIN", "CLOCK", "EAST", "NORTH", "POINT", "SLOWLY", "BETWEEN",
              "SHADOW", "HIDDEN", "SECRET", "LAYER", "COMPASS", "DEGREE", "HOLD",
              "UNDER", "GROUND", "TIME", "LIGHT", "DARK", "WATCH"]:
        if w in pt:
            pos = pt.index(w)
            if not (21 <= pos <= 33 and "EASTNORTHEAST"[pos-21:pos-21+len(w)] == w) and \
               not (63 <= pos <= 73 and "BERLINCLOCK"[pos-63:pos-63+len(w)] == w):
                print(f"    *** Found '{w}' at position {pos} (outside cribs!) ***")

print("\nDone.")
