#!/usr/bin/env python3
"""
The BERLINCLOCK key segment and NORTHEAST key segment both sum to exactly 94
(standard A=0 indexing). This seems too precise to be coincidental.

Investigate: Is this a property of the cipher, or is it special?
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def std_idx(c):
    return ord(c) - ord('A')

def k_idx(c):
    return KRYPTOS.index(c)

def derive_key_char(ct_char, pt_char):
    """Derive key character from ciphertext and plaintext (KRYPTOS alphabet)."""
    ct_idx = KRYPTOS.index(ct_char)
    pt_idx = KRYPTOS.index(pt_char)
    return KRYPTOS[(ct_idx - pt_idx) % 26]

# Derive key segments
def derive_key_segment(ct_start, plaintext):
    segment = ""
    for i, pt_char in enumerate(plaintext):
        segment += derive_key_char(K4_CT[ct_start + i], pt_char)
    return segment

bc_key = derive_key_segment(63, "BERLINCLOCK")
ne_key = derive_key_segment(16, "NORTHEAST")

bc_std = [std_idx(c) for c in bc_key]
ne_std = [std_idx(c) for c in ne_key]

bc_krypt = [k_idx(c) for c in bc_key]
ne_krypt = [k_idx(c) for c in ne_key]

print("=" * 70)
print("EQUAL SUM ANALYSIS")
print("=" * 70)

print(f"\nBERLINCLOCK key segment: {bc_key}")
print(f"  Standard (A=0):  {bc_std}  sum={sum(bc_std)}")
print(f"  KRYPTOS indices: {bc_krypt}  sum={sum(bc_krypt)}")

print(f"\nNORTHEAST key segment:   {ne_key}")
print(f"  Standard (A=0):  {ne_std}  sum={sum(ne_std)}")
print(f"  KRYPTOS indices: {ne_krypt}  sum={sum(ne_krypt)}")

print(f"\n*** Standard sums: BC={sum(bc_std)}, NE={sum(ne_std)} ***")
print(f"*** KRYPTOS sums:  BC={sum(bc_krypt)}, NE={sum(ne_krypt)} ***")

# Is this just because of the relationship between ciphertext and plaintext?
# Key[i] = (CT[i] - PT[i]) mod 26  (in KRYPTOS alphabet)
# So sum(key) = sum(CT[positions]) - sum(PT) mod 26... but mod makes this tricky

print("\n--- WHY DO THEY SUM TO THE SAME VALUE? ---")

# Ciphertext at BERLINCLOCK positions
bc_ct = K4_CT[63:74]
bc_ct_std = [std_idx(c) for c in bc_ct]
bc_pt_std = [std_idx(c) for c in "BERLINCLOCK"]

print(f"\nBERLINCLOCK:")
print(f"  CT at 63-73: {bc_ct}  std={bc_ct_std}  sum={sum(bc_ct_std)}")
print(f"  PT:          BERLINCLOCK  std={bc_pt_std}  sum={sum(bc_pt_std)}")
print(f"  Key sum (std) = CT_sum - PT_sum = {sum(bc_ct_std)} - {sum(bc_pt_std)} = {sum(bc_ct_std) - sum(bc_pt_std)}")
print(f"  Actual key sum (std) = {sum(bc_std)}")
print(f"  Difference = {sum(bc_std) - (sum(bc_ct_std) - sum(bc_pt_std))}")

# For KRYPTOS alphabet, we need to account for the permutation
print(f"\n  In KRYPTOS alphabet:")
bc_ct_k = [k_idx(c) for c in bc_ct]
bc_pt_k = [k_idx(c) for c in "BERLINCLOCK"]
print(f"  CT kryptos: {bc_ct_k}  sum={sum(bc_ct_k)}")
print(f"  PT kryptos: {bc_pt_k}  sum={sum(bc_pt_k)}")
print(f"  Key sum = {sum(bc_krypt)}")
print(f"  CT_sum - PT_sum = {sum(bc_ct_k) - sum(bc_pt_k)} (vs actual {sum(bc_krypt)})")

# Now NORTHEAST
ne_ct = K4_CT[16:25]
ne_ct_std = [std_idx(c) for c in ne_ct]
ne_pt_std = [std_idx(c) for c in "NORTHEAST"]

print(f"\nNORTHEAST:")
print(f"  CT at 16-24: {ne_ct}  std={ne_ct_std}  sum={sum(ne_ct_std)}")
print(f"  PT:          NORTHEAST  std={ne_pt_std}  sum={sum(ne_pt_std)}")
print(f"  Key sum (std) = CT_sum - PT_sum = {sum(ne_ct_std)} - {sum(ne_pt_std)} = {sum(ne_ct_std) - sum(ne_pt_std)}")
print(f"  Actual key sum (std) = {sum(ne_std)}")

# The sums won't be exact because of mod 26 wrapping
# Let's check without mod wrapping
print("\n--- RAW SUBTRACTION (no mod 26) ---")
bc_raw = [(KRYPTOS.index(ct) - KRYPTOS.index(pt)) for ct, pt in zip(bc_ct, "BERLINCLOCK")]
ne_raw = [(KRYPTOS.index(ct) - KRYPTOS.index(pt)) for ct, pt in zip(ne_ct, "NORTHEAST")]
print(f"BC raw differences: {bc_raw}  sum={sum(bc_raw)}")
print(f"NE raw differences: {ne_raw}  sum={sum(ne_raw)}")
print(f"Any negative (indicating mod wrap)? BC: {[x for x in bc_raw if x < 0]}, NE: {[x for x in ne_raw if x < 0]}")

# Test: what if NORTHEAST is at a DIFFERENT position?
print("\n--- DOES THE EQUAL SUM HOLD FOR OTHER NORTHEAST POSITIONS? ---")
for ne_start in range(89):
    ne_ct_pos = K4_CT[ne_start:ne_start+9]
    if not all(c in KRYPTOS for c in ne_ct_pos):
        continue
    key_seg = derive_key_segment(ne_start, "NORTHEAST")
    key_std = [std_idx(c) for c in key_seg]
    s = sum(key_std)
    if s == 94:
        print(f"  NE@{ne_start}: key={key_seg} sum={s} *** EQUALS BC SUM! ***")
    elif abs(s - 94) <= 5:
        print(f"  NE@{ne_start}: key={key_seg} sum={s} (close)")

# What about other words?
print("\n--- SUM FOR OTHER WORDS AT VARIOUS POSITIONS ---")
test_words = ["UNDER", "ABOVE", "THERE", "WHERE", "BELOW", "LAYER", "CLOCK",
              "NORTH", "SOUTH", "LIGHT", "NIGHT", "WORLD", "EARTH"]
for word in test_words:
    for start in range(97 - len(word) + 1):
        ct_slice = K4_CT[start:start+len(word)]
        if not all(c in KRYPTOS for c in ct_slice):
            continue
        key_seg = derive_key_segment(start, word)
        key_std = [std_idx(c) for c in key_seg]
        s = sum(key_std)
        if s == 94:
            print(f"  '{word}' @ pos {start}: key={key_seg} sum={s} *** EQUALS 94! ***")

# Statistical context
print("\n--- STATISTICAL CONTEXT ---")
# What's the expected sum for a random 11-letter key?
# E[sum of 11 random values 0-25] = 11 * 12.5 = 137.5
# E[sum of 9 random values 0-25] = 9 * 12.5 = 112.5
# Std dev = sqrt(n * var) where var(uniform 0-25) = (25^2 - 1)/12 = 52
# std dev for 11 values = sqrt(11 * 52) = 23.9
# std dev for 9 values = sqrt(9 * 52) = 21.6
print(f"Expected sum for random 11-letter key: 137.5 (std: 23.9)")
print(f"Expected sum for random 9-letter key:  112.5 (std: 21.6)")
print(f"BC sum: {sum(bc_std)} (below expected by {137.5 - sum(bc_std):.1f} = {(137.5 - sum(bc_std))/23.9:.1f} sigma)")
print(f"NE sum: {sum(ne_std)} (below expected by {112.5 - sum(ne_std):.1f} = {(112.5 - sum(ne_std))/21.6:.1f} sigma)")
print(f"P(both = 94) under random assumption: very low (both are below expectation)")
