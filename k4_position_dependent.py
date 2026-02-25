#!/usr/bin/env python3
"""
Kryptos K4: Position-Dependent Key Modification Hypothesis Testing

Tests the hypothesis: ct[i] = (pt[i] + key[i%29] + f(i)) % 26
where f(i) is some position-dependent function.

If this is the case, the "derived key" from cribs at position i would be:
  derived_key[i] = key[i%29] + f(i)  mod 26

So key derivations at the SAME key slot but DIFFERENT absolute positions
would differ by f(i1) - f(i2).
"""

import math
import sys
from collections import defaultdict
from itertools import product

# ============================================================
# CONSTANTS
# ============================================================
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CT_LEN = len(CT)  # 97

# Known cribs:
# EASTNORTHEAST at plaintext positions 21-33 (13 chars)
# BERLINCLOCK at plaintext positions 63-73 (11 chars)
CRIB_ENE = ("EASTNORTHEAST", 21)
CRIB_BC  = ("BERLINCLOCK", 63)

# Known partial key (period 29):
# OYNKYELYOIECBAQK?????RDUMRIYW
KNOWN_KEY_STR = "OYNKYELYOIECBAQK?????RDUMRIYW"
PERIOD = 29

def k_index(ch):
    """Convert character to KRYPTOS alphabet index."""
    return KRYPTOS_ALPHA.index(ch)

def k_char(idx):
    """Convert KRYPTOS alphabet index to character."""
    return KRYPTOS_ALPHA[idx % 26]

def encrypt_char(pt_ch, key_ch):
    """Vigenere encrypt: ct = (pt + key) mod 26 in KRYPTOS alphabet."""
    return k_char((k_index(pt_ch) + k_index(key_ch)) % 26)

def decrypt_char(ct_ch, key_ch):
    """Vigenere decrypt: pt = (ct - key) mod 26 in KRYPTOS alphabet."""
    return k_char((k_index(ct_ch) - k_index(key_ch)) % 26)

def derive_key_char(ct_ch, pt_ch):
    """Derive key: key = (ct - pt) mod 26 in KRYPTOS alphabet."""
    return (k_index(ct_ch) - k_index(pt_ch)) % 26

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
        """Score text using log10 quadgram frequencies."""
        text = text.upper()
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            if gram in self.quadgrams:
                s += math.log10(self.quadgrams[gram] / self.total)
            else:
                s += self.floor
        return s

    def score_per_char(self, text):
        """Score normalized by length."""
        if len(text) < 4:
            return -99
        return self.score(text) / (len(text) - 3)

print("=" * 80)
print("KRYPTOS K4: POSITION-DEPENDENT KEY MODIFICATION ANALYSIS")
print("=" * 80)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

# ============================================================
# STEP 1: DERIVE KEY VALUES FROM BOTH CRIBS
# ============================================================
print("\n" + "=" * 80)
print("STEP 1: DERIVE KEY VALUES FROM CRIBS (SIMPLE VIGENERE ASSUMPTION)")
print("=" * 80)

derived_keys = {}  # Maps (ct_position) -> derived_key_index

# EASTNORTHEAST at positions 21-33
crib_text, crib_start = CRIB_ENE
for j, pt_ch in enumerate(crib_text):
    ct_pos = crib_start + j
    ct_ch = CT[ct_pos]
    dk = derive_key_char(ct_ch, pt_ch)
    key_slot = ct_pos % PERIOD
    derived_keys[ct_pos] = dk
    print(f"  CT[{ct_pos:2d}] = {ct_ch}, PT = {pt_ch}, derived_key = {dk:2d} ({k_char(dk)}), key_slot = {key_slot:2d}")

print()
# BERLINCLOCK at positions 63-73
crib_text, crib_start = CRIB_BC
for j, pt_ch in enumerate(crib_text):
    ct_pos = crib_start + j
    ct_ch = CT[ct_pos]
    dk = derive_key_char(ct_ch, pt_ch)
    key_slot = ct_pos % PERIOD
    derived_keys[ct_pos] = dk
    print(f"  CT[{ct_pos:2d}] = {ct_ch}, PT = {pt_ch}, derived_key = {dk:2d} ({k_char(dk)}), key_slot = {key_slot:2d}")

# ============================================================
# STEP 2: CHECK KEY CONSISTENCY ACROSS PERIODS
# ============================================================
print("\n" + "=" * 80)
print("STEP 2: KEY CONSISTENCY CHECK ACROSS PERIODS")
print("=" * 80)
print("\nFor each key slot, check if derived values from different CT positions agree.\n")

# Build map: key_slot -> list of (ct_pos, derived_key_value)
slot_to_derivations = defaultdict(list)
for ct_pos, dk in derived_keys.items():
    slot = ct_pos % PERIOD
    slot_to_derivations[slot].append((ct_pos, dk))

# Also store the known key
known_key_indices = {}
for i, ch in enumerate(KNOWN_KEY_STR):
    if ch != '?':
        known_key_indices[i] = k_index(ch)

inconsistencies = []
for slot in sorted(slot_to_derivations.keys()):
    derivations = slot_to_derivations[slot]
    known = known_key_indices.get(slot, None)
    
    print(f"  Key slot {slot:2d}:")
    for ct_pos, dk in derivations:
        match_str = ""
        if known is not None:
            if dk == known:
                match_str = " [MATCHES known key]"
            else:
                diff = (dk - known) % 26
                match_str = f" [DIFFERS from known key {k_char(known)}({known}) by {diff}]"
                inconsistencies.append((slot, ct_pos, dk, known, diff))
        print(f"    CT pos {ct_pos:2d}: derived = {dk:2d} ({k_char(dk)}){match_str}")
    
    if len(derivations) > 1:
        vals = [d[1] for d in derivations]
        if len(set(vals)) > 1:
            diffs = []
            for i in range(len(derivations)):
                for j in range(i+1, len(derivations)):
                    pos_i, val_i = derivations[i]
                    pos_j, val_j = derivations[j]
                    d = (val_j - val_i) % 26
                    diffs.append((pos_i, pos_j, d))
                    inconsistencies.append((slot, pos_j, val_j, val_i, d))
            print(f"    *** INCONSISTENCY: values differ! Differences: {diffs}")
        else:
            print(f"    Consistent across {len(derivations)} positions.")

print(f"\n  Total inconsistencies found: {len(inconsistencies)}")

# ============================================================
# STEP 3: ANALYZE INCONSISTENCIES TO DETECT f(i)
# ============================================================
print("\n" + "=" * 80)
print("STEP 3: ANALYZE INCONSISTENCIES TO DETECT f(i)")
print("=" * 80)

# For overlapping key slots between the two cribs, compute offset
# ENE covers key slots: 21%29=21, 22%29=22, ..., 33%29=4
# BC  covers key slots: 63%29=5, 64%29=6, ..., 73%29=15

ene_slots = {}
for j, pt_ch in enumerate("EASTNORTHEAST"):
    ct_pos = 21 + j
    slot = ct_pos % PERIOD
    dk = derive_key_char(CT[ct_pos], pt_ch)
    ene_slots[slot] = (ct_pos, dk)

bc_slots = {}
for j, pt_ch in enumerate("BERLINCLOCK"):
    ct_pos = 63 + j
    slot = ct_pos % PERIOD
    dk = derive_key_char(CT[ct_pos], pt_ch)
    bc_slots[slot] = (ct_pos, dk)

# Find overlapping slots
overlap_slots = set(ene_slots.keys()) & set(bc_slots.keys())
print(f"\nENE key slots: {sorted(ene_slots.keys())}")
print(f"BC  key slots: {sorted(bc_slots.keys())}")
print(f"Overlapping slots: {sorted(overlap_slots)}")

if overlap_slots:
    print("\nOverlap analysis:")
    for slot in sorted(overlap_slots):
        pos1, val1 = ene_slots[slot]
        pos2, val2 = bc_slots[slot]
        diff = (val2 - val1) % 26
        print(f"  Slot {slot:2d}: ENE pos {pos1} val {val1}({k_char(val1)}) vs BC pos {pos2} val {val2}({k_char(val2)}) => diff = {diff}")
else:
    print("\nNo overlapping slots between ENE and BC cribs.")
    print("ENE covers absolute positions 21-33, key slots 21-28 and 0-4")
    print("BC  covers absolute positions 63-73, key slots 5-15")
    print("These are disjoint! Cannot directly compare.")
    
    # But we CAN compare derived key vs KNOWN key
    print("\nComparing derived key values to known key OYNKYELYOIECBAQK?????RDUMRIYW:")
    print()
    full_known_key = "OYNKYELYOIECBAQK?????RDUMRIYW"
    
    # For each crib-derived key value, compare to known key at that slot
    all_diffs = []
    for ct_pos, dk in derived_keys.items():
        slot = ct_pos % PERIOD
        if full_known_key[slot] != '?':
            known_val = k_index(full_known_key[slot])
            diff = (dk - known_val) % 26
            period_num = ct_pos // PERIOD  # which period this position falls in
            all_diffs.append((ct_pos, slot, dk, known_val, diff, period_num))
            print(f"  CT[{ct_pos:2d}] slot={slot:2d} period={period_num}: derived={dk:2d}({k_char(dk)}) known={known_val:2d}({k_char(known_val)}) diff={diff:2d}")
    
    # Check if diffs correlate with position
    print("\n  Differences grouped by absolute position:")
    for ct_pos, slot, dk, kv, diff, pn in all_diffs:
        print(f"    pos={ct_pos:2d}, period={pn}, diff={diff:2d}, diff_as_function_of_pos: i={ct_pos}, i//29={pn}, i%29={slot}")

# ============================================================
# STEP 4: THE KNOWN KEY IS DERIVED FROM CRIBS - CHECK IF IT IS SELF-CONSISTENT
# ============================================================
print("\n" + "=" * 80)
print("STEP 4: VERIFY THE KNOWN KEY WAS DERIVED CONSISTENTLY")
print("=" * 80)

# The known key OYNKYELYOIECBAQK?????RDUMRIYW should be derivable from cribs
# ENE at pos 21-33 gives key slots 21-28, 0-4
# BC at pos 63-73 gives key slots 5-15

print("\nKey derived from EASTNORTHEAST (pos 21-33):")
ene_key = {}
for j, pt_ch in enumerate("EASTNORTHEAST"):
    ct_pos = 21 + j
    slot = ct_pos % PERIOD
    dk = derive_key_char(CT[ct_pos], pt_ch)
    ene_key[slot] = (dk, k_char(dk), ct_pos)
    print(f"  slot {slot:2d}: {k_char(dk)} (from CT[{ct_pos}])")

print("\nKey derived from BERLINCLOCK (pos 63-73):")
bc_key = {}
for j, pt_ch in enumerate("BERLINCLOCK"):
    ct_pos = 63 + j
    slot = ct_pos % PERIOD
    dk = derive_key_char(CT[ct_pos], pt_ch)
    bc_key[slot] = (dk, k_char(dk), ct_pos)
    print(f"  slot {slot:2d}: {k_char(dk)} (from CT[{ct_pos}])")

print("\nCombined key (from simple Vigenere assumption):")
combined = {}
for slot in range(29):
    if slot in ene_key:
        combined[slot] = ene_key[slot]
    elif slot in bc_key:
        combined[slot] = bc_key[slot]
    else:
        combined[slot] = (None, '?', None)

key_str = ""
for slot in range(29):
    val, ch, pos = combined[slot]
    key_str += ch
    known_ch = KNOWN_KEY_STR[slot]
    match = "OK" if ch == known_ch else ("unknown" if known_ch == '?' else f"MISMATCH(expected {known_ch})")
    if val is not None:
        print(f"  slot {slot:2d}: {ch} (val={val:2d}, from CT[{pos}]) -- {match}")
    else:
        print(f"  slot {slot:2d}: ? (not covered by cribs) -- {match}")

print(f"\nDerived key:  {key_str}")
print(f"Known key:    {KNOWN_KEY_STR}")

# ============================================================
# STEP 5: DECRYPT WITH SIMPLE VIGENERE AND CHECK
# ============================================================
print("\n" + "=" * 80)
print("STEP 5: SIMPLE VIGENERE DECRYPTION (BASELINE)")
print("=" * 80)

# Use the key as derived, with ? for unknowns
simple_pt = []
for i in range(CT_LEN):
    slot = i % PERIOD
    if combined[slot][0] is not None:
        key_val = combined[slot][0]
        pt_val = (k_index(CT[i]) - key_val) % 26
        simple_pt.append(k_char(pt_val))
    else:
        simple_pt.append('?')

simple_pt_str = ''.join(simple_pt)
print(f"\nSimple Vigenere plaintext (partial):")
for start in range(0, CT_LEN, 29):
    end = min(start + 29, CT_LEN)
    segment = simple_pt_str[start:end]
    print(f"  [{start:2d}-{end-1:2d}]: {segment}")

# Check if ENE and BC appear
print(f"\n  Positions 21-33: {simple_pt_str[21:34]}")
print(f"  Positions 63-73: {simple_pt_str[63:74]}")

# Score the known portions
known_portions = simple_pt_str.replace('?', '')
if len(known_portions) >= 4:
    score = scorer.score_per_char(known_portions)
    print(f"\n  Quadgram score of known portions: {score:.4f}")
    print(f"  (English typically scores around -2.3 to -2.0; random is around -4.5)")

# ============================================================
# STEP 6: TEST POSITION-DEPENDENT FUNCTIONS f(i)
# ============================================================
print("\n" + "=" * 80)
print("STEP 6: TEST POSITION-DEPENDENT KEY MODIFICATION FUNCTIONS")
print("=" * 80)

def fibonacci_mod26(n):
    """Return fibonacci(n) mod 26."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b) % 26
    return a

def triangular(n):
    return (n * (n + 1) // 2) % 26

def digit_sum(n):
    return sum(int(d) for d in str(n)) % 26

# Define f(i) functions to test
f_functions = {
    "f(i) = 0 (baseline, simple Vig)": lambda i: 0,
    "f(i) = i mod 26": lambda i: i % 26,
    "f(i) = -i mod 26": lambda i: (-i) % 26,
    "f(i) = i//29 (period counter)": lambda i: (i // 29) % 26,
    "f(i) = -(i//29) mod 26": lambda i: (-(i // 29)) % 26,
    "f(i) = 2*(i//29) mod 26": lambda i: (2 * (i // 29)) % 26,
    "f(i) = (i//29)^2 mod 26": lambda i: ((i // 29) ** 2) % 26,
    "f(i) = i*(i+1)/2 mod 26 (triangular)": lambda i: triangular(i),
    "f(i) = i^2 mod 26": lambda i: (i * i) % 26,
    "f(i) = fibonacci(i) mod 26": lambda i: fibonacci_mod26(i),
    "f(i) = digit_sum(i) mod 26": lambda i: digit_sum(i),
    "f(i) = i*3 mod 26": lambda i: (i * 3) % 26,
    "f(i) = i*5 mod 26": lambda i: (i * 5) % 26,
    "f(i) = i*7 mod 26": lambda i: (i * 7) % 26,
    "f(i) = i*11 mod 26": lambda i: (i * 11) % 26,
    "f(i) = i*13 mod 26": lambda i: (i * 13) % 26,
    "f(i) = floor(sqrt(i)) mod 26": lambda i: int(math.sqrt(i)) % 26,
    "f(i) = i mod 7 (KRYPTOS columns)": lambda i: (i % 7),
    "f(i) = i//7 (KRYPTOS rows)": lambda i: (i // 7) % 26,
    "f(i) = (i%7) + (i//7) mod 26": lambda i: ((i % 7) + (i // 7)) % 26,
    "f(i) = (i%7) * (i//7) mod 26": lambda i: ((i % 7) * (i // 7)) % 26,
    "f(i) = i mod 10": lambda i: i % 10,
    "f(i) = i mod 13": lambda i: i % 13,
    "f(i) = ct_index[i-1] (autokey-like, prev CT)": "autokey_ct",
    "f(i) = running sum of ct mod 26": "running_ct_sum",
}

def decrypt_with_f(ct, key_slots, f_func, period=29):
    """
    Decrypt: pt[i] = (ct[i] - key[i%period] - f(i)) mod 26
    key_slots: dict of slot -> key_value (index)
    f_func: callable int->int, or special string
    Returns plaintext string with ? for unknown key slots.
    """
    pt = []
    running_ct_sum = 0
    for i in range(len(ct)):
        slot = i % period
        if slot not in key_slots or key_slots[slot] is None:
            pt.append('?')
            running_ct_sum = (running_ct_sum + k_index(ct[i])) % 26
            continue
        
        key_val = key_slots[slot]
        
        if f_func == "autokey_ct":
            if i == 0:
                fi = 0
            else:
                fi = k_index(ct[i-1])
        elif f_func == "running_ct_sum":
            fi = running_ct_sum
        else:
            fi = f_func(i)
        
        pt_val = (k_index(ct[i]) - key_val - fi) % 26
        pt.append(k_char(pt_val))
        running_ct_sum = (running_ct_sum + k_index(ct[i])) % 26
    
    return ''.join(pt)

# Build key_slots dict from combined
key_slots = {}
for slot in range(29):
    if combined[slot][0] is not None:
        key_slots[slot] = combined[slot][0]

results = []
for name, f_func in f_functions.items():
    pt = decrypt_with_f(CT, key_slots, f_func)
    
    # Check if ENE and BC still appear (they should for f(i)=0 but not others)
    ene_check = pt[21:34]
    bc_check = pt[63:74]
    
    # Score
    known = pt.replace('?', '')
    if len(known) >= 4:
        score = scorer.score_per_char(known)
    else:
        score = -99
    
    results.append((score, name, pt, ene_check, bc_check))

results.sort(key=lambda x: -x[0])  # Best score first

print("\nResults (sorted by quadgram score, best first):\n")
for score, name, pt, ene, bc in results[:15]:
    print(f"  Score: {score:.4f} | {name}")
    print(f"    Full PT: {pt}")
    print(f"    ENE region: {ene}")
    print(f"    BC region:  {bc}")
    print()

# ============================================================
# STEP 7: SMARTER APPROACH - USE CRIBS TO DETERMINE f(i) CONSTRAINTS
# ============================================================
print("\n" + "=" * 80)
print("STEP 7: USE CRIBS TO DETERMINE f(i) CONSTRAINTS")
print("=" * 80)

# Key insight: We KNOW the plaintext at certain positions.
# EASTNORTHEAST at pos 21-33, BERLINCLOCK at pos 63-73.
#
# Under model ct[i] = (pt[i] + key[i%29] + f(i)) mod 26:
#   key[i%29] + f(i) = (ct[i] - pt[i]) mod 26
#
# Call this the "effective key" ek[i] = key[i%29] + f(i) mod 26
#
# We know ek[i] at all crib positions.
# For key slot s, ek values at different absolute positions MUST satisfy:
#   ek[i] = key[s] + f(i) mod 26
#
# So for two positions i1, i2 with same key slot s:
#   ek[i1] - ek[i2] = f(i1) - f(i2) mod 26
#
# Since ENE and BC don't share key slots, we need another approach.
# 
# Instead: assume the KNOWN KEY is the TRUE key (derived under some consistent scheme).
# The known key was derived assuming f=0. But it might be that at positions where
# it was derived, f happened to be 0 (or constant).
#
# Alternative: The known key IS correct, and f varies per position.
# Then: for ENE, f(21)=f(22)=...=f(33)=0 and for BC, f(63)=...=f(73)=0?
# That's unlikely unless f is 0 everywhere.
#
# Better approach: Assume f(i) = g(i//29) i.e. f depends only on which period.
# ENE is entirely in period 0 (pos 0-28) -> no, pos 21-33 spans periods 0 and 1!
# pos 21-28 is period 0, pos 29-33 is period 1.
# BC is pos 63-73, period 2 (pos 58-86) -> all period 2.

print("\nCrib positions and their periods:")
print("  EASTNORTHEAST (pos 21-33):")
for j in range(13):
    pos = 21 + j
    print(f"    pos {pos}: period {pos//29}, slot {pos%29}")

print("  BERLINCLOCK (pos 63-73):")
for j in range(11):
    pos = 63 + j
    print(f"    pos {pos}: period {pos//29}, slot {pos%29}")

# ENE: pos 21-28 in period 0, pos 29-33 in period 1
# BC: pos 63-73 all in period 2

# If f(i) = g(period), then:
# For pos 21-28: ek = key[slot] + g(0)
# For pos 29-33: ek = key[slot] + g(1)
# For pos 63-73: ek = key[slot] + g(2)

# The known key was derived assuming g=0 for all. But if g(0) != g(1),
# then the key values derived from period 0 part of ENE would differ
# from those derived from period 1 part by g(1)-g(0).

# Let's check: key slots derived from period 0 vs period 1 within ENE
print("\n\nChecking if ENE-derived key is consistent across period boundary:")
print("  Period 0 (pos 21-28), key slots 21-28:")
period0_keys = {}
for j in range(8):  # pos 21-28
    pos = 21 + j
    pt_ch = "EASTNORTHEAST"[j]
    slot = pos % PERIOD
    ek = derive_key_char(CT[pos], pt_ch)
    period0_keys[slot] = ek
    print(f"    pos {pos}, slot {slot}: ek = {ek} ({k_char(ek)})")

print("  Period 1 (pos 29-33), key slots 0-4:")
period1_keys = {}
for j in range(8, 13):  # pos 29-33
    pos = 21 + j
    pt_ch = "EASTNORTHEAST"[j]
    slot = pos % PERIOD
    ek = derive_key_char(CT[pos], pt_ch)
    period1_keys[slot] = ek
    print(f"    pos {pos}, slot {slot}: ek = {ek} ({k_char(ek)})")

print("  Period 2 (pos 63-73), key slots 5-15:")
period2_keys = {}
for j in range(11):
    pos = 63 + j
    pt_ch = "BERLINCLOCK"[j]
    slot = pos % PERIOD
    ek = derive_key_char(CT[pos], pt_ch)
    period2_keys[slot] = ek
    print(f"    pos {pos}, slot {slot}: ek = {ek} ({k_char(ek)})")

# No direct overlap between these three sets of key slots!
# Period 0: slots 21-28
# Period 1: slots 0-4
# Period 2: slots 5-15
# Together they cover slots 0-15 and 21-28 with NO overlap.
# So we CANNOT detect f from crib overlap alone with period-level f.

print("\n  Key slot coverage:")
print(f"    Period 0: slots {sorted(period0_keys.keys())}")
print(f"    Period 1: slots {sorted(period1_keys.keys())}")
print(f"    Period 2: slots {sorted(period2_keys.keys())}")
print(f"    No overlap! Cannot directly detect period-level f from cribs alone.")

# ============================================================
# STEP 8: BRUTE-FORCE TEST OF f(i) = c * (i//29) FOR c in 0..25
# ============================================================
print("\n" + "=" * 80)
print("STEP 8: BRUTE-FORCE f(i) = c * (i//29) mod 26 FOR c IN 0..25")
print("=" * 80)

# Under this model, the TRUE key at slot s is:
# For period 0 derivations: true_key[s] = ek[s] - c*0 = ek[s]
# For period 1 derivations: true_key[s] = ek[s] - c*1
# For period 2 derivations: true_key[s] = ek[s] - c*2
#
# The known key was derived assuming c=0. If c != 0, the key slots from
# different periods are wrong relative to each other.

# Currently, key slots 21-28 from period 0, 0-4 from period 1, 5-15 from period 2
# True key:
#   slots 21-28: ek (no adjustment)
#   slots 0-4:   ek - c (adjustment for period 1)
#   slots 5-15:  ek - 2c (adjustment for period 2)

step_results = []
for c in range(26):
    adjusted_key = {}
    for slot in range(29):
        if slot in period0_keys:
            adjusted_key[slot] = period0_keys[slot]  # period 0, no adjustment
        elif slot in period1_keys:
            adjusted_key[slot] = (period1_keys[slot] - c) % 26  # adjust for period 1
        elif slot in period2_keys:
            adjusted_key[slot] = (period2_keys[slot] - 2 * c) % 26  # adjust for period 2
    
    # Decrypt: pt[i] = ct[i] - key[i%29] - c*(i//29) mod 26
    pt = []
    for i in range(CT_LEN):
        slot = i % PERIOD
        if slot in adjusted_key:
            fi = (c * (i // 29)) % 26
            pt_val = (k_index(CT[i]) - adjusted_key[slot] - fi) % 26
            pt.append(k_char(pt_val))
        else:
            pt.append('?')
    
    pt_str = ''.join(pt)
    known = pt_str.replace('?', '')
    score = scorer.score_per_char(known) if len(known) >= 4 else -99
    
    # Check cribs
    ene_ok = pt_str[21:34] == "EASTNORTHEAST"
    bc_ok = pt_str[63:74] == "BERLINCLOCK"
    
    step_results.append((score, c, pt_str, ene_ok, bc_ok))

step_results.sort(key=lambda x: -x[0])

print("\nTop results (f(i) = c * floor(i/29)):\n")
for score, c, pt, ene_ok, bc_ok in step_results[:10]:
    print(f"  c={c:2d}: score={score:.4f} ENE={'YES' if ene_ok else 'NO '} BC={'YES' if bc_ok else 'NO '}")
    print(f"         {pt}")
    print()

# ============================================================
# STEP 9: GENERAL f(i) = a*i + b*(i//29) + c*(i^2) SMALL COEFFICIENTS
# ============================================================
print("\n" + "=" * 80)
print("STEP 9: TEST f(i) = a*i + b*(i//29) mod 26 FOR SMALL a, b")
print("=" * 80)

# Under this model, the effective key at position i is:
#   ek[i] = true_key[i%29] + a*i + b*(i//29) mod 26
# The derived key at crib position i is:
#   derived[i] = ek[i] = true_key[slot] + a*i + b*(i//29)
# So true_key[slot] = derived[i] - a*i - b*(i//29) mod 26

general_results = []
for a in range(26):
    for b in range(26):
        # Compute true key from each crib position
        true_key = {}
        for ct_pos, dk in derived_keys.items():
            slot = ct_pos % PERIOD
            fi = (a * ct_pos + b * (ct_pos // 29)) % 26
            tk = (dk - fi) % 26
            if slot in true_key:
                if true_key[slot] != tk:
                    break  # Inconsistency within same slot
            else:
                true_key[slot] = tk
        else:
            # No inconsistency. Decrypt.
            pt = []
            for i in range(CT_LEN):
                slot = i % PERIOD
                if slot in true_key:
                    fi = (a * i + b * (i // 29)) % 26
                    pt_val = (k_index(CT[i]) - true_key[slot] - fi) % 26
                    pt.append(k_char(pt_val))
                else:
                    pt.append('?')
            
            pt_str = ''.join(pt)
            known = pt_str.replace('?', '')
            score = scorer.score_per_char(known) if len(known) >= 4 else -99
            
            if score > -3.5:  # Only keep promising results
                general_results.append((score, a, b, pt_str))

general_results.sort(key=lambda x: -x[0])

print(f"\n  Tested {26*26} (a,b) combinations.")
print(f"  Found {len(general_results)} with score > -3.5\n")

for score, a, b, pt in general_results[:20]:
    print(f"  a={a:2d}, b={b:2d}: score={score:.4f}")
    print(f"    {pt}")
    # Show periods
    for start in range(0, CT_LEN, 29):
        end = min(start + 29, CT_LEN)
        print(f"    [{start:2d}-{end-1:2d}]: {pt[start:end]}")
    print()

# ============================================================
# STEP 10: TEST f(i) = a*i mod 26 ONLY (PROGRESSIVE KEY)
# ============================================================
print("\n" + "=" * 80)
print("STEP 10: TEST f(i) = a*i mod 26 (PROGRESSIVE/SLIDING KEY)")
print("=" * 80)

prog_results = []
for a in range(26):
    true_key = {}
    consistent = True
    for ct_pos, dk in derived_keys.items():
        slot = ct_pos % PERIOD
        fi = (a * ct_pos) % 26
        tk = (dk - fi) % 26
        if slot in true_key:
            if true_key[slot] != tk:
                consistent = False
                break
        else:
            true_key[slot] = tk
    
    if not consistent:
        continue
    
    pt = []
    for i in range(CT_LEN):
        slot = i % PERIOD
        if slot in true_key:
            fi = (a * i) % 26
            pt_val = (k_index(CT[i]) - true_key[slot] - fi) % 26
            pt.append(k_char(pt_val))
        else:
            pt.append('?')
    
    pt_str = ''.join(pt)
    known = pt_str.replace('?', '')
    score = scorer.score_per_char(known) if len(known) >= 4 else -99
    
    prog_results.append((score, a, pt_str, true_key))

prog_results.sort(key=lambda x: -x[0])

print(f"\n  Tested 26 values of a. {len(prog_results)} consistent.\n")
for score, a, pt, tk in prog_results[:10]:
    key_str = ''.join(k_char(tk[s]) if s in tk else '?' for s in range(29))
    print(f"  a={a:2d}: score={score:.4f}, true_key={key_str}")
    print(f"    {pt}")
    print()

# ============================================================
# STEP 11: TEST AUTOKEY VARIANTS
# ============================================================
print("\n" + "=" * 80)
print("STEP 11: AUTOKEY-LIKE SECOND LAYERS")
print("=" * 80)

# Hypothesis: After Vigenere with the known key, there's an autokey layer.
# Model 1: ct[i] = (pt[i] + key[i%29] + pt[i-1]) mod 26 (plaintext autokey)
# Model 2: ct[i] = (pt[i] + key[i%29] + ct[i-1]) mod 26 (ciphertext autokey)
# Model 3: ct[i] = (pt[i] + key[i%29] + running_key[i]) mod 26

# For Model 2 (CT autokey), working backwards from cribs:
# At crib positions, we know pt. So:
#   pt[i] = (ct[i] - key[slot] - ct[i-1]) mod 26
# This means derived key = (ct[i] - pt[i]) mod 26 = key[slot] + ct[i-1] mod 26
# So the "extra" is ct[i-1].

print("\nModel: ct[i] = pt[i] + key[i%29] + ct[i-1] mod 26")
print("Testing if this produces consistent key from cribs:\n")

# Derive true key assuming ct autokey
ct_autokey_results = {}
for ct_pos, dk in derived_keys.items():
    slot = ct_pos % PERIOD
    if ct_pos > 0:
        extra = k_index(CT[ct_pos - 1])
    else:
        extra = 0
    tk = (dk - extra) % 26
    if slot in ct_autokey_results:
        if ct_autokey_results[slot] != tk:
            print(f"  INCONSISTENCY at slot {slot}: pos {ct_pos} gives {tk}, previously had {ct_autokey_results[slot]}")
    else:
        ct_autokey_results[slot] = tk

print(f"  Derived {len(ct_autokey_results)} consistent key slots")
ct_ak_key_str = ''.join(k_char(ct_autokey_results[s]) if s in ct_autokey_results else '?' for s in range(29))
print(f"  Key: {ct_ak_key_str}")

# Decrypt
pt_ct_ak = []
for i in range(CT_LEN):
    slot = i % PERIOD
    if slot in ct_autokey_results:
        extra = k_index(CT[i-1]) if i > 0 else 0
        pt_val = (k_index(CT[i]) - ct_autokey_results[slot] - extra) % 26
        pt_ct_ak.append(k_char(pt_val))
    else:
        pt_ct_ak.append('?')

pt_ct_ak_str = ''.join(pt_ct_ak)
known = pt_ct_ak_str.replace('?', '')
score = scorer.score_per_char(known) if len(known) >= 4 else -99
print(f"  Score: {score:.4f}")
print(f"  PT: {pt_ct_ak_str}")

# Now test plaintext autokey
print("\nModel: ct[i] = pt[i] + key[i%29] + pt[i-1] mod 26")
print("This requires iterative decryption since pt[i-1] depends on pt[i-2]...")
print("We can only test at crib positions where we know the plaintext sequence.\n")

# For PT autokey, we need to decrypt sequentially. At crib positions we can verify.
# But for unknown positions, we need the key AND previous plaintext.
# Let's try: derive key from cribs assuming pt autokey, then decrypt forward.

pt_ak_key = {}
for ct_pos, dk in derived_keys.items():
    slot = ct_pos % PERIOD
    # Need pt[ct_pos - 1]
    if ct_pos - 1 >= 21 and ct_pos - 1 <= 33:
        prev_pt = "EASTNORTHEAST"[ct_pos - 1 - 21] if ct_pos - 1 - 21 < 13 else None
    elif ct_pos - 1 >= 63 and ct_pos - 1 <= 73:
        prev_pt = "BERLINCLOCK"[ct_pos - 1 - 63] if ct_pos - 1 - 63 < 11 else None
    else:
        prev_pt = None
    
    if prev_pt is not None:
        extra = k_index(prev_pt)
        tk = (dk - extra) % 26
        if slot in pt_ak_key:
            if pt_ak_key[slot] != tk:
                print(f"  INCONSISTENCY at slot {slot}: pos {ct_pos} gives {tk}({k_char(tk)}), previously had {pt_ak_key[slot]}({k_char(pt_ak_key[slot])})")
        else:
            pt_ak_key[slot] = tk
    else:
        print(f"  Skipping pos {ct_pos} (unknown previous plaintext)")

pt_ak_key_str = ''.join(k_char(pt_ak_key[s]) if s in pt_ak_key else '?' for s in range(29))
print(f"\n  PT autokey derived key: {pt_ak_key_str}")
print(f"  ({len(pt_ak_key)} slots filled)")

# ============================================================
# STEP 12: GRID-BASED MODIFICATIONS
# ============================================================
print("\n" + "=" * 80)
print("STEP 12: GRID-BASED KEY MODIFICATIONS")
print("=" * 80)

# If K4 is laid out in a grid, the key modification might depend on row/column
# Test grids: 7 cols (KRYPTOS), 29 cols (period), other sizes

grid_results = []
for ncols in [7, 8, 10, 14, 29, 97]:
    for func_name, func in [
        ("row", lambda i, nc: (i // nc) % 26),
        ("col", lambda i, nc: (i % nc) % 26),
        ("row+col", lambda i, nc: ((i // nc) + (i % nc)) % 26),
        ("row*col", lambda i, nc: ((i // nc) * (i % nc)) % 26),
        ("row-col", lambda i, nc: ((i // nc) - (i % nc)) % 26),
        ("diag", lambda i, nc: ((i // nc) + (i % nc)) % 26),
    ]:
        true_key = {}
        consistent = True
        for ct_pos, dk in derived_keys.items():
            slot = ct_pos % PERIOD
            fi = func(ct_pos, ncols)
            tk = (dk - fi) % 26
            if slot in true_key:
                if true_key[slot] != tk:
                    consistent = False
                    break
            else:
                true_key[slot] = tk
        
        if not consistent:
            continue
        
        pt = []
        for i in range(CT_LEN):
            slot = i % PERIOD
            if slot in true_key:
                fi = func(i, ncols)
                pt_val = (k_index(CT[i]) - true_key[slot] - fi) % 26
                pt.append(k_char(pt_val))
            else:
                pt.append('?')
        
        pt_str = ''.join(pt)
        known = pt_str.replace('?', '')
        score = scorer.score_per_char(known) if len(known) >= 4 else -99
        
        grid_results.append((score, ncols, func_name, pt_str))

grid_results.sort(key=lambda x: -x[0])

print(f"\n  Tested grid-based modifications. Top results:\n")
for score, ncols, func_name, pt in grid_results[:15]:
    print(f"  Grid {ncols} cols, f={func_name}: score={score:.4f}")
    print(f"    {pt}")
    print()

# ============================================================
# STEP 13: EXHAUSTIVE f(i) = a*i + b*(i//29) + c*i^2 (SMALL)
# ============================================================
print("\n" + "=" * 80)
print("STEP 13: EXHAUSTIVE f(i) = a*i + b*(i//29) + c*i^2 mod 26")
print("=" * 80)

quad_results = []
for a in range(26):
    for b in range(26):
        for c in range(1, 14):  # Only test small quadratic terms
            true_key = {}
            consistent = True
            for ct_pos, dk in derived_keys.items():
                slot = ct_pos % PERIOD
                fi = (a * ct_pos + b * (ct_pos // 29) + c * ct_pos * ct_pos) % 26
                tk = (dk - fi) % 26
                if slot in true_key:
                    if true_key[slot] != tk:
                        consistent = False
                        break
                else:
                    true_key[slot] = tk
            
            if not consistent:
                continue
            
            pt = []
            for i in range(CT_LEN):
                slot = i % PERIOD
                if slot in true_key:
                    fi = (a * i + b * (i // 29) + c * i * i) % 26
                    pt_val = (k_index(CT[i]) - true_key[slot] - fi) % 26
                    pt.append(k_char(pt_val))
                else:
                    pt.append('?')
            
            pt_str = ''.join(pt)
            known = pt_str.replace('?', '')
            score = scorer.score_per_char(known) if len(known) >= 4 else -99
            
            if score > -3.2:
                quad_results.append((score, a, b, c, pt_str))

quad_results.sort(key=lambda x: -x[0])

print(f"\n  Tested {26*26*13} (a,b,c) combinations. {len(quad_results)} with score > -3.2\n")
for score, a, b, c, pt in quad_results[:10]:
    print(f"  a={a:2d}, b={b:2d}, c={c:2d}: score={score:.4f}")
    print(f"    {pt}")
    print()

# ============================================================
# STEP 14: BRUTE-FORCE UNKNOWN KEY POSITIONS WITH BEST f(i)
# ============================================================
print("\n" + "=" * 80)
print("STEP 14: FILL UNKNOWN KEY SLOTS (16-20) WITH BEST f(i) = 0")
print("=" * 80)

# Unknown key positions: 16, 17, 18, 19, 20
# These are used at CT positions: 16, 45, 74 (slot 16)
#                                   17, 46, 75 (slot 17)
#                                   18, 47, 76 (slot 18)
#                                   19, 48, 77 (slot 19)
#                                   20, 49, 78 (slot 20)

# With simple Vigenere (f=0), brute-force all 26^5 combinations
# But 26^5 = 11,881,376 which is too many to test exhaustively
# Let's be smarter: test each slot independently first

print("\nTesting each unknown slot (16-20) independently for best single-char value:\n")

for unknown_slot in range(16, 21):
    best_score = -999
    best_val = 0
    results_for_slot = []
    
    # CT positions using this slot
    positions = [i for i in range(CT_LEN) if i % PERIOD == unknown_slot]
    
    for val in range(26):
        # Decrypt only positions using this slot
        snippet = ""
        for pos in positions:
            pt_val = (k_index(CT[pos]) - val) % 26
            snippet += k_char(pt_val)
        
        # Also decrypt surrounding context with known keys
        test_key = dict(key_slots)
        test_key[unknown_slot] = val
        
        # Get extended context around each position
        full_text = []
        for i in range(CT_LEN):
            slot = i % PERIOD
            if slot in test_key:
                pt_val = (k_index(CT[i]) - test_key[slot]) % 26
                full_text.append(k_char(pt_val))
            else:
                full_text.append('?')
        
        ft = ''.join(full_text)
        known = ft.replace('?', '')
        score = scorer.score_per_char(known) if len(known) >= 4 else -99
        results_for_slot.append((score, val, k_char(val), ft))
    
    results_for_slot.sort(key=lambda x: -x[0])
    print(f"  Slot {unknown_slot} (CT positions {positions}):")
    for score, val, ch, ft in results_for_slot[:5]:
        print(f"    key={ch}({val:2d}): score={score:.4f}")
    print()

# ============================================================
# STEP 15: FOCUSED 5-SLOT BRUTE FORCE WITH BEAM SEARCH
# ============================================================
print("\n" + "=" * 80)
print("STEP 15: BEAM SEARCH OVER 5 UNKNOWN KEY POSITIONS")
print("=" * 80)

# Use beam search: for each slot, keep top candidates and expand
beam_width = 50

# Start with all known key slots
base_key = dict(key_slots)

# Add unknown slots one at a time
candidates = [(0.0, base_key.copy())]

for unknown_slot in range(16, 21):
    new_candidates = []
    for parent_score, parent_key in candidates:
        for val in range(26):
            test_key = parent_key.copy()
            test_key[unknown_slot] = val
            
            # Decrypt with this key
            pt = []
            for i in range(CT_LEN):
                slot = i % PERIOD
                if slot in test_key:
                    pt_val = (k_index(CT[i]) - test_key[slot]) % 26
                    pt.append(k_char(pt_val))
                else:
                    pt.append('?')
            
            pt_str = ''.join(pt)
            known = pt_str.replace('?', '')
            score = scorer.score_per_char(known) if len(known) >= 4 else -99
            
            new_candidates.append((score, test_key))
    
    new_candidates.sort(key=lambda x: -x[0])
    candidates = new_candidates[:beam_width]
    
    best = candidates[0]
    best_chars = ''.join(k_char(best[1].get(s, 0)) for s in range(16, unknown_slot + 1))
    print(f"  After slot {unknown_slot}: best score = {best[0]:.4f}, partial unknown key = {best_chars}")

print(f"\n  Top {min(10, len(candidates))} complete key candidates:\n")
for rank, (score, full_key) in enumerate(candidates[:10]):
    unknown_part = ''.join(k_char(full_key[s]) for s in range(16, 21))
    full_key_str = ''.join(k_char(full_key.get(s, 0)) for s in range(29))
    
    # Full decrypt
    pt = []
    for i in range(CT_LEN):
        slot = i % PERIOD
        pt_val = (k_index(CT[i]) - full_key[slot]) % 26
        pt.append(k_char(pt_val))
    
    pt_str = ''.join(pt)
    
    print(f"  #{rank+1}: score={score:.4f}, unknown slots={unknown_part}, key={full_key_str}")
    print(f"       PT: {pt_str}")
    
    # Show in segments
    for start in range(0, CT_LEN, 29):
        end = min(start + 29, CT_LEN)
        print(f"       [{start:2d}-{end-1:2d}]: {pt_str[start:end]}")
    print()

# ============================================================
# STEP 16: COMBINE BEST f(i) WITH 5-SLOT SEARCH
# ============================================================
print("\n" + "=" * 80)
print("STEP 16: COMBINE POSITION FUNCTIONS WITH UNKNOWN KEY SEARCH")
print("=" * 80)

# Test the top few f(i) functions combined with brute force over unknown slots
promising_funcs = [
    ("f=0", lambda i: 0),
    ("f=i mod 26", lambda i: i % 26),
    ("f=-i mod 26", lambda i: (-i) % 26),
    ("f=i//29", lambda i: (i // 29) % 26),
    ("f=-(i//29)", lambda i: (-(i // 29)) % 26),
    ("f=2*(i//29)", lambda i: (2 * (i // 29)) % 26),
    ("f=3*(i//29)", lambda i: (3 * (i // 29)) % 26),
    ("f=5*(i//29)", lambda i: (5 * (i // 29)) % 26),
    ("f=7*(i//29)", lambda i: (7 * (i // 29)) % 26),
    ("f=13*(i//29)", lambda i: (13 * (i // 29)) % 26),
]

combined_results = []

for fname, ffunc in promising_funcs:
    # Derive true key from cribs for this f
    true_key = {}
    for ct_pos, dk in derived_keys.items():
        slot = ct_pos % PERIOD
        fi = ffunc(ct_pos)
        tk = (dk - fi) % 26
        if slot in true_key:
            if true_key[slot] != tk:
                break  # Inconsistent
        else:
            true_key[slot] = tk
    else:
        # Consistent. Now brute force unknown slots (16-20)
        # Use beam search
        beam = [(0.0, true_key.copy())]
        
        for unknown_slot in range(16, 21):
            new_beam = []
            for ps, pk in beam:
                for val in range(26):
                    tk = pk.copy()
                    tk[unknown_slot] = val
                    
                    pt = []
                    for i in range(CT_LEN):
                        slot = i % PERIOD
                        if slot in tk:
                            fi = ffunc(i)
                            pt_val = (k_index(CT[i]) - tk[slot] - fi) % 26
                            pt.append(k_char(pt_val))
                        else:
                            pt.append('?')
                    
                    pt_str = ''.join(pt)
                    known = pt_str.replace('?', '')
                    score = scorer.score_per_char(known) if len(known) >= 4 else -99
                    new_beam.append((score, tk))
            
            new_beam.sort(key=lambda x: -x[0])
            beam = new_beam[:30]
        
        for score, tk in beam[:3]:
            unknown_part = ''.join(k_char(tk[s]) for s in range(16, 21))
            
            # Full decrypt
            pt = []
            for i in range(CT_LEN):
                slot = i % PERIOD
                fi = ffunc(i)
                pt_val = (k_index(CT[i]) - tk[slot] - fi) % 26
                pt.append(k_char(pt_val))
            pt_str = ''.join(pt)
            
            combined_results.append((score, fname, unknown_part, pt_str))

combined_results.sort(key=lambda x: -x[0])

print(f"\n  Top 20 results across all f(i) functions:\n")
for rank, (score, fname, unk, pt) in enumerate(combined_results[:20]):
    print(f"  #{rank+1}: score={score:.4f}, {fname}, unknown={unk}")
    print(f"       {pt}")
    # Check for known words
    for word in ["BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST", "SLOWLY", "DESPER", 
                 "UNDER", "GROUND", "LAYER", "BURIED", "SECRET", "HIDDEN"]:
        if word in pt:
            print(f"       *** Contains '{word}' ***")
    print()

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print(f"""
Key findings:

1. CT length: {CT_LEN} characters
2. Period: {PERIOD}
3. Known key: {KNOWN_KEY_STR}
4. EASTNORTHEAST crib: positions 21-33 (spans period 0 and 1)
5. BERLINCLOCK crib: positions 63-73 (all in period 2)
6. Key slots from cribs: 0-15 and 21-28 (slots 16-20 unknown)
7. ENE and BC cover DISJOINT key slots - no direct consistency check possible
   between the two cribs for simple Vigenere!

The cribs span three different periods:
  - Period 0 (pos 0-28): ENE gives slots 21-28
  - Period 1 (pos 29-57): ENE gives slots 0-4
  - Period 2 (pos 58-86): BC gives slots 5-15

Since each crib-derived key slot comes from exactly ONE period,
any f(i) that depends only on the period number will produce a
"consistent" key (just shifted). This means we CANNOT distinguish
f(i)=0 from f(i)=c*(i//29) using crib consistency alone!

To distinguish, we need:
  - The resulting plaintext to be English
  - Or additional cribs/constraints
""")

# Print the very best overall result
if combined_results:
    best = combined_results[0]
    print(f"Best overall decryption (score={best[0]:.4f}):")
    print(f"  Function: {best[1]}")
    print(f"  Unknown key slots: {best[2]}")
    print(f"  Plaintext: {best[3]}")

print("\n" + "=" * 80)
print("DONE")
print("=" * 80)
