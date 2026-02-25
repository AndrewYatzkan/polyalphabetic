#!/usr/bin/env python3
"""
CRITICAL TEST: Compute IC on ONLY the positions where the key is KNOWN
(from confirmed cribs BERLINCLOCK@63 and EASTNORTHEAST@21).

If the Vigenere output at known-key positions has English-like IC (~0.0667),
then the cipher is Vigenere + transposition.
If it's random-like (~0.038), then there's a DIFFERENT kind of second layer.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c): return KRYPTOS.index(c)
def k_chr(i): return KRYPTOS[i % 26]

# Known key from cribs (period 29)
# EASTNORTHEAST@21 gives key positions 21-28, 0-4
# BERLINCLOCK@63 gives key positions 5-15
# Unknown: positions 16-20

known_key = {}

# From EASTNORTHEAST at CT positions 21-33
CRIB1 = "EASTNORTHEAST"
for j, pt_char in enumerate(CRIB1):
    ct_pos = 21 + j
    key_pos = ct_pos % 29
    key_char = k_chr((k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26)
    known_key[key_pos] = key_char

# From BERLINCLOCK at CT positions 63-73
CRIB2 = "BERLINCLOCK"
for j, pt_char in enumerate(CRIB2):
    ct_pos = 63 + j
    key_pos = ct_pos % 29
    key_char = k_chr((k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26)
    known_key[key_pos] = key_char

print("Known key positions:")
for i in range(29):
    if i in known_key:
        print(f"  Key[{i:2d}] = {known_key[i]} (KRYPTOS idx {k_idx(known_key[i])})")
    else:
        print(f"  Key[{i:2d}] = ? (unknown)")

# Identify which CT positions use known vs unknown key slots
known_ct_positions = [i for i in range(97) if (i % 29) in known_key]
unknown_ct_positions = [i for i in range(97) if (i % 29) not in known_key]

print(f"\nKnown-key CT positions ({len(known_ct_positions)}): {known_ct_positions}")
print(f"Unknown-key CT positions ({len(unknown_ct_positions)}): {unknown_ct_positions}")

# Decrypt known-key positions
known_pt_chars = []
for i in known_ct_positions:
    kp = i % 29
    pt_char = k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26)
    known_pt_chars.append(pt_char)

known_pt_str = ''.join(known_pt_chars)
print(f"\nDecrypted text at known-key positions ({len(known_pt_str)} chars):")
print(f"  {known_pt_str}")

# Compute IC of known-key positions only
from collections import Counter
counts = Counter(known_pt_str)
n = len(known_pt_str)
ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
print(f"\nIC of known-key decrypted positions: {ic:.4f}")
print(f"Expected English: 0.0667")
print(f"Expected random:  0.0385")

# Also compute IC for each key position group separately
print("\nIC per key position group:")
for kp in sorted(known_key.keys()):
    positions = [i for i in range(97) if i % 29 == kp]
    chars = [k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26) for i in positions]
    chars_str = ''.join(chars)
    # Can't compute meaningful IC with only 3-4 chars, but show the distribution
    print(f"  Key pos {kp:2d}: {chars_str} ({len(chars)} chars)")

# Now the CRITICAL question: is the known-key plaintext just the original
# plaintext at those positions, or has it been transposed?

# If there's NO transposition layer, then the known-key plaintext should
# contain the cribs at their expected positions:
print("\n--- Crib position check in full decryption ---")
full_pt = []
for i in range(97):
    kp = i % 29
    if kp in known_key:
        full_pt.append(k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26))
    else:
        full_pt.append('?')
full_pt_str = ''.join(full_pt)
print(f"Full PT: {full_pt_str}")
print(f"Positions 21-33: {full_pt_str[21:34]}")
print(f"Positions 63-73: {full_pt_str[63:74]}")

# Check: does BERLINCLOCK appear at 63? YES by construction
# Does EASTNORTHEAST appear at 21? YES by construction
# But what about the OTHER positions?

# The non-crib positions at known key slots should also be English if there's
# no transposition. Let's look at them grouped by region:
print("\n--- Non-crib plaintext at known-key positions ---")
regions = [
    ("Before ENE (pos 0-20)", 0, 21),
    ("Between cribs (pos 34-62)", 34, 63),
    ("After BC (pos 74-96)", 74, 97),
]
for name, start, end in regions:
    chars = []
    for i in range(start, end):
        kp = i % 29
        if kp in known_key:
            c = k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26)
            chars.append((i, c))
        else:
            chars.append((i, '?'))
    text = ''.join(c for _, c in chars)
    known_text = ''.join(c for _, c in chars if c != '?')
    print(f"  {name}: {text}")
    print(f"    Known chars only: {known_text}")

    # Count English-like digrams
    english_digrams = ["TH", "HE", "IN", "ER", "AN", "RE", "EN", "ON", "AT", "ND",
                        "ST", "OR", "TE", "ES", "IS", "IT", "AL", "AR", "NE", "NG"]
    found = [d for d in english_digrams if d in text.replace('?', '')]
    if found:
        print(f"    English digrams: {found}")

# Frequency analysis of non-crib known-key plaintext
non_crib_chars = []
for i in range(97):
    kp = i % 29
    if kp in known_key:
        # Skip positions that are part of cribs
        if 21 <= i <= 33 or 63 <= i <= 73:
            continue
        c = k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26)
        non_crib_chars.append(c)

non_crib_str = ''.join(non_crib_chars)
print(f"\nNon-crib known-key plaintext ({len(non_crib_str)} chars): {non_crib_str}")
nc_counts = Counter(non_crib_str)
nc_n = len(non_crib_str)
if nc_n > 1:
    nc_ic = sum(c*(c-1) for c in nc_counts.values()) / (nc_n*(nc_n-1))
    print(f"IC of non-crib known-key PT: {nc_ic:.4f}")
else:
    print("Not enough chars for IC")

print(f"Frequency: {sorted(nc_counts.items(), key=lambda x: -x[1])}")

# SECOND CRITICAL TEST: What if the period is NOT 29?
# Test alternative periods and see if they give higher IC
print("\n" + "=" * 80)
print("ALTERNATIVE PERIOD IC TEST")
print("=" * 80)
for period in range(2, 60):
    # Use Kasiski/IC-based key derivation
    # Group ciphertext by position mod period
    groups = [[] for _ in range(period)]
    for i, c in enumerate(K4):
        groups[i % period].append(k_idx(c))

    # Compute IC for each group
    group_ics = []
    for g in groups:
        if len(g) < 2:
            continue
        counts = Counter(g)
        n = len(g)
        ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
        group_ics.append(ic)

    if group_ics:
        avg_ic = sum(group_ics) / len(group_ics)
        if avg_ic > 0.05:  # Above random threshold
            print(f"  Period {period:2d}: avg IC = {avg_ic:.4f} {'***' if avg_ic > 0.055 else ''}")

# THIRD CRITICAL TEST: What if position 16-20 of the key, when chosen correctly,
# makes the overall IC much higher?
print("\n" + "=" * 80)
print("KEY POSITION 16-20 IC OPTIMIZATION")
print("=" * 80)
# For each of 5 unknown positions, find the key value that maximizes
# the IC contribution of that group

for kp in range(16, 21):
    positions = [i for i in range(97) if i % 29 == kp]
    ct_chars = [k_idx(K4[i]) for i in positions]

    best_ic = -1
    best_key = None
    best_chars = None

    for key_val in range(26):
        pt_chars = [(c - key_val) % 26 for c in ct_chars]
        # Check frequency - we want high IC (more skewed distribution)
        counts = Counter(pt_chars)
        n = len(pt_chars)
        if n < 2:
            continue
        ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))

        if ic > best_ic:
            best_ic = ic
            best_key = KRYPTOS[key_val]
            best_chars = ''.join(KRYPTOS[p] for p in pt_chars)

    print(f"  Key pos {kp}: best key char = {best_key} (IC={best_ic:.4f})")
    print(f"    Decrypted: {best_chars} at CT positions {positions}")

# FOURTH TEST: What if the cipher uses STANDARD alphabet instead of KRYPTOS?
print("\n" + "=" * 80)
print("STANDARD ALPHABET TEST")
print("=" * 80)
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def s_idx(c): return STANDARD.index(c)
def s_chr(i): return STANDARD[i % 26]

# Re-derive key with standard alphabet
std_key = {}
for j, pt_char in enumerate(CRIB1):
    ct_pos = 21 + j
    key_pos = ct_pos % 29
    # Note: CRIB1 contains no J, so standard alphabet works
    key_char = s_chr((s_idx(K4[ct_pos]) - s_idx(pt_char)) % 26)
    std_key[key_pos] = key_char

for j, pt_char in enumerate(CRIB2):
    ct_pos = 63 + j
    key_pos = ct_pos % 29
    key_char = s_chr((s_idx(K4[ct_pos]) - s_idx(pt_char)) % 26)
    std_key[key_pos] = key_char

std_key_str = ''.join(std_key.get(i, '?') for i in range(29))
print(f"Standard alphabet key: {std_key_str}")

# Decrypt with standard alphabet
std_pt = []
for i in range(97):
    kp = i % 29
    if kp in std_key:
        std_pt.append(s_chr((s_idx(K4[i]) - s_idx(std_key[kp])) % 26))
    else:
        std_pt.append('?')
std_pt_str = ''.join(std_pt)
print(f"Standard PT: {std_pt_str}")

# Compute IC
std_known = [c for c in std_pt_str if c != '?']
std_counts = Counter(std_known)
std_n = len(std_known)
std_ic = sum(c*(c-1) for c in std_counts.values()) / (std_n*(std_n-1))
print(f"Standard PT IC (known positions): {std_ic:.4f}")

# FIFTH TEST: Compare IC with and without crib positions
print("\n" + "=" * 80)
print("IC BREAKDOWN: CRIB vs NON-CRIB POSITIONS")
print("=" * 80)

# The cribs are forced English text. Their contribution to IC is "cheating."
# What matters is the IC of the NON-CRIB positions.

# Known key positions that are NOT part of cribs
non_crib_known_positions = []
for i in range(97):
    kp = i % 29
    if kp in known_key:
        if not (21 <= i <= 33 or 63 <= i <= 73):
            non_crib_known_positions.append(i)

non_crib_pt = [k_chr((k_idx(K4[i]) - k_idx(known_key[i % 29])) % 26)
               for i in non_crib_known_positions]
non_crib_pt_str = ''.join(non_crib_pt)
print(f"Non-crib known-key positions ({len(non_crib_pt_str)} chars): {non_crib_pt_str}")

nc2_counts = Counter(non_crib_pt_str)
nc2_n = len(non_crib_pt_str)
nc2_ic = sum(c*(c-1) for c in nc2_counts.values()) / (nc2_n*(nc2_n-1))
print(f"IC of non-crib known-key PT: {nc2_ic:.4f}")
print(f"  English expected: 0.0667")
print(f"  Random expected:  0.0385")
print(f"  This IC is {'ENGLISH-like' if nc2_ic > 0.055 else 'RANDOM-like' if nc2_ic < 0.045 else 'AMBIGUOUS'}")

# Show the complete picture
print(f"\nFull picture (? = unknown key, | = crib boundary):")
annotated = []
for i in range(97):
    if i == 21 or i == 34 or i == 63 or i == 74:
        annotated.append('|')
    kp = i % 29
    if kp in known_key:
        c = k_chr((k_idx(K4[i]) - k_idx(known_key[kp])) % 26)
        annotated.append(c)
    else:
        annotated.append('?')
print(''.join(annotated))

print("\nDone.")
