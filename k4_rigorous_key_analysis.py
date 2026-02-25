#!/usr/bin/env python3
"""
K4 Key Pattern Analysis - Rigorous, no speculation.
Analyze the key DIJJQELYOIECBAQKVAATCRDUMPABT for internal structure.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Map letters to their position in KRYPTOS alphabet
def k_idx(c):
    return KRYPTOS.index(c)

print("=" * 70)
print("K4 KEY: RIGOROUS PATTERN ANALYSIS")
print("=" * 70)

# 1. Key as numeric values (position in KRYPTOS alphabet)
print("\n1. KEY AS KRYPTOS INDICES")
indices = [k_idx(c) for c in KEY]
print(f"Key:     {KEY}")
print(f"Indices: {indices}")

# As standard A=0 values
std_indices = [ord(c) - ord('A') for c in KEY]
print(f"A=0:     {std_indices}")

# 2. Differences between consecutive key letters
print("\n2. CONSECUTIVE DIFFERENCES (mod 26)")
diffs = [(indices[i+1] - indices[i]) % 26 for i in range(len(indices)-1)]
print(f"Diffs:   {diffs}")
# Standard alphabet diffs
std_diffs = [(std_indices[i+1] - std_indices[i]) % 26 for i in range(len(std_indices)-1)]
print(f"Std diffs: {std_diffs}")

# 3. Key segments from known cribs
print("\n3. KEY SEGMENTS (derived from known plaintext)")
print(f"  Pos 0-4  (from UNDER):        {KEY[0:5]}  = {[k_idx(c) for c in KEY[0:5]]}")
print(f"  Pos 5-15 (from BERLINCLOCK):   {KEY[5:16]} = {[k_idx(c) for c in KEY[5:16]]}")
print(f"  Pos 16-24 (from NORTHEAST):    {KEY[16:25]} = {[k_idx(c) for c in KEY[16:25]]}")
print(f"  Pos 25-28 (from ABOVE):        {KEY[25:29]} = {[k_idx(c) for c in KEY[25:29]]}")

# 4. Which key letters are FORCED vs ASSUMED?
print("\n4. FORCED vs ASSUMED KEY POSITIONS")
print("  Sanborn CONFIRMED: BERLINCLOCK at pos 63, NORTHEAST somewhere")
print("  BERLINCLOCK at 63 → key[5:16] = ELYOIECBAQK (FORCED)")
print("  NORTHEAST at 16 → key[16:25] = VAATCRDUM (FORCED IF pos 16 is correct)")
print("  UNDER at 0 → key[0:5] = DIJJQ (ASSUMED - we chose UNDER)")
print("  ABOVE at 83 → key[25:29] = PABT (ASSUMED - we chose ABOVE)")
print()
print("  FORCED: 20 positions (5-24)")
print("  ASSUMED: 9 positions (0-4, 25-28)")
print()
print("  KEY INSIGHT: If UNDER and ABOVE are wrong, 9 key positions change!")

# 5. Repeating letters in key
print("\n5. REPEATING LETTERS IN KEY")
from collections import Counter
counts = Counter(KEY)
for letter, count in counts.most_common():
    if count > 1:
        positions = [i for i, c in enumerate(KEY) if c == letter]
        print(f"  {letter} appears {count}x at positions {positions}")

# 6. Are there arithmetic progressions?
print("\n6. ARITHMETIC PROGRESSIONS IN KEY VALUES")
for start in range(len(indices)):
    for step in range(1, len(indices) - start):
        seq = []
        pos = start
        while pos < len(indices):
            seq.append((pos, indices[pos]))
            pos += step
            if len(seq) >= 3:
                # Check if values form arithmetic progression
                vals = [s[1] for s in seq]
                diffs_seq = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
                if len(set(diffs_seq)) == 1 and diffs_seq[0] != 0:
                    if len(seq) >= 4:
                        print(f"  Positions {[s[0] for s in seq]}: values {vals}, diff={diffs_seq[0]}")
            if len(seq) >= 6:
                break

# 7. Does the FORCED part (positions 5-24) have structure?
print("\n7. FORCED KEY SEGMENT ANALYSIS (positions 5-24)")
forced = KEY[5:25]
forced_idx = indices[5:25]
print(f"  Segment: {forced}")
print(f"  Indices: {forced_idx}")
print(f"  Sum: {sum(forced_idx)}")
print(f"  Mean: {sum(forced_idx)/len(forced_idx):.2f}")

# Check for palindrome
print(f"  Is palindrome? {forced == forced[::-1]}")
# Check for symmetry
mid = len(forced_idx) // 2
first_half = forced_idx[:mid]
second_half = forced_idx[mid:]
print(f"  First half:  {first_half}")
print(f"  Second half: {second_half}")
print(f"  Sum first:  {sum(first_half)}")
print(f"  Sum second: {sum(second_half)}")

# 8. Relationship between BERLINCLOCK segment and NORTHEAST segment
print("\n8. BERLINCLOCK vs NORTHEAST KEY SEGMENTS")
bc_seg = KEY[5:16]   # ELYOIECBAQK
ne_seg = KEY[16:25]  # VAATCRDUM
print(f"  BERLINCLOCK key: {bc_seg} = {[k_idx(c) for c in bc_seg]}")
print(f"  NORTHEAST key:   {ne_seg}  = {[k_idx(c) for c in ne_seg]}")

# XOR/diff between overlapping positions
bc_vals = [k_idx(c) for c in bc_seg]
ne_vals = [k_idx(c) for c in ne_seg]
print(f"  Sum of BERLINCLOCK segment: {sum(bc_vals)}")
print(f"  Sum of NORTHEAST segment: {sum(ne_vals)}")

# 9. What if key positions map to clock hours?
print("\n9. KEY VALUES AS CLOCK HOURS (mod 24)")
hours = [v % 24 for v in indices]
print(f"  Key values mod 24: {hours}")
# Check if any are valid UTC offsets (-12 to +14)
offsets = [(v - 12) for v in hours]
print(f"  As UTC offsets:    {offsets}")

# 10. The FULL plaintext with annotations
print("\n10. FULL ANNOTATED PLAINTEXT")
def decrypt(ct, key):
    pt = ""
    for i, c in enumerate(ct):
        ct_idx = KRYPTOS.index(c)
        key_idx = KRYPTOS.index(key[i % len(key)])
        pt_idx = (ct_idx - key_idx) % 26
        pt += KRYPTOS[pt_idx]
    return pt

pt = decrypt(K4_CT, KEY)
print(f"  CT: {K4_CT}")
print(f"  PT: {pt}")
print()

# Show key cycling
key_cycle = ""
for i in range(97):
    key_cycle += KEY[i % 29]
print(f"  KY: {key_cycle}")

# 11. What positions use each key letter?
print("\n11. WHICH PLAINTEXT POSITIONS USE EACH KEY POSITION")
for kp in range(29):
    positions = list(range(kp, 97, 29))
    pt_chars = [pt[p] for p in positions]
    ct_chars = [K4_CT[p] for p in positions]
    print(f"  Key[{kp:2d}]={KEY[kp]}: CT={''.join(ct_chars)} → PT={''.join(pt_chars)}  (positions {positions})")
