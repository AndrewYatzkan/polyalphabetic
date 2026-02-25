#!/usr/bin/env python3
"""
Test two critical 2025 Sanborn clues:
1. DYAHR - displaced letters in upper left of sculpture
2. W as separator splitting K4 into six segments

DYAHR could be:
- An anagram (HARDY, HYDRA, etc.)
- Part of the key
- A key to decode the segments
- Related to the 5 unknown key positions (16-20)
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c): return KRYPTOS.index(c)
def k_chr(i): return KRYPTOS[i % 26]
def vig_decrypt(ct, key, alpha=KRYPTOS):
    return ''.join(alpha[(alpha.index(ct[i]) - alpha.index(key[i % len(key)])) % 26] for i in range(len(ct)))
def vig_encrypt(pt, key, alpha=KRYPTOS):
    return ''.join(alpha[(alpha.index(pt[i]) + alpha.index(key[i % len(key)])) % 26] for i in range(len(pt)))

print("=" * 80)
print("DYAHR ANALYSIS")
print("=" * 80)

# DYAHR anagrams
from itertools import permutations
dyahr_perms = set(''.join(p) for p in permutations("DYAHR"))
english_words_5 = {"HARDY", "HYDRA", "DAIRY", "DIARY", "HARRY", "READY", "DRYAH", "HANDY"}
matches = dyahr_perms & english_words_5
print(f"DYAHR anagrams that are English words: {matches}")
# HARDY and HYDRA are the notable ones

# DYAHR as key for 5 unknown positions (16-20)
known_key_base = list("OYNKYELYOIECBAQK?????RDUMRIYW")
print(f"\nKnown key: {''.join(known_key_base)}")

# Test DYAHR and its anagrams as the 5 unknown positions
print("\nTesting DYAHR permutations as key positions 16-20:")
from collections import Counter

best_score = -1
best_perm = None
best_pt = None

# Load quadgram data for scoring
import math
quadgram_scores = {}
try:
    with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                quadgram_scores[parts[0]] = math.log10(int(parts[1]))
    total = math.log10(sum(10**v for v in quadgram_scores.values()))
    floor_score = math.log10(0.01) - total
except:
    quadgram_scores = {}
    floor_score = -10

def qscore(text):
    if not quadgram_scores:
        return 0
    score = 0
    for i in range(len(text) - 3):
        q = text[i:i+4]
        score += quadgram_scores.get(q, floor_score)
    return score

for perm in sorted(dyahr_perms):
    key = list(known_key_base)
    for i, c in enumerate(perm):
        key[16 + i] = c
    key_str = ''.join(key)

    pt = vig_decrypt(K4, key_str)
    score = qscore(pt)

    # Check for English words
    words_found = []
    for w in ["THE", "AND", "FOR", "WITH", "THAT", "THIS", "FROM", "HAVE",
              "BEEN", "WILL", "YOUR", "THERE", "WHERE", "UNDER", "ABOVE",
              "BELOW", "FIND", "NORTH", "SOUTH", "EAST", "WEST", "CLOCK",
              "BERLIN", "SHADOW", "LAYER", "POINT", "PLACE", "STONE",
              "SLOWLY", "DEGREES", "BEARING", "COMPASS", "HIDDEN", "SECRET"]:
        if w in pt and w not in ["EAST", "NORTH"]:  # exclude crib substrings
            pos = pt.index(w)
            if not (21 <= pos <= 33 or 63 <= pos <= 73):  # not in crib region
                words_found.append((w, pos))

    if words_found or perm in ["DYAHR", "HARDY", "HYDRA"]:
        print(f"  Key[16:21]={perm}: score={score:.1f} words={words_found}")
        print(f"    PT: {pt}")

    if score > best_score:
        best_score = score
        best_perm = perm
        best_pt = pt

print(f"\nBest DYAHR permutation: {best_perm} (score={best_score:.1f})")
print(f"  PT: {best_pt}")

# Also test DYAHR in KRYPTOS alphabet indices
print("\nDYAHR in KRYPTOS indices:")
for c in "DYAHR":
    print(f"  {c} = KRYPTOS index {k_idx(c)}")
# D=10, Y=2, A=7, H=14, R=1

print("\n" + "=" * 80)
print("W-SEPARATOR DETAILED ANALYSIS")
print("=" * 80)

# Find all W positions
w_positions = [i for i, c in enumerate(K4) if c == 'W']
print(f"W positions in K4: {w_positions}")

segments = []
prev = 0
for wp in w_positions:
    segments.append(K4[prev:wp])
    prev = wp + 1
segments.append(K4[prev:])

print(f"\nSegments ({len(segments)}):")
for i, seg in enumerate(segments):
    start = sum(len(s) for s in segments[:i]) + i  # account for W separators
    end = start + len(seg) - 1
    print(f"  Seg {i+1}: [{start:2d}-{end:2d}] ({len(seg):2d} chars) {seg}")

    # IC of segment
    if len(seg) >= 2:
        counts = Counter(seg)
        n = len(seg)
        ic = sum(c*(c-1) for c in counts.values()) / (n*(n-1))
        print(f"         IC={ic:.4f} {'(English-like!)' if ic > 0.055 else ''}")

# Segment-by-segment Vigenere analysis
print("\n--- Segment-level cipher analysis ---")

# Segment 2 contains EASTNORTHEAST at position 0 (relative to segment)
# Segment 5 contains BERLINCLOCK at position 4 (relative to segment)

# For segment 2 (15 chars): first 13 = EASTNORTHEAST, last 2 unknown
seg2 = segments[1]  # FLRVQQPRNGKSSOT
seg2_pt_known = "EASTNORTHEAST"
print(f"\nSegment 2: {seg2} (15 chars)")
print(f"  Known PT[0:13] = EASTNORTHEAST")
print(f"  Unknown PT[13:15] = ??")

# Derive key for segment 2 assuming independent Vigenere
seg2_key_known = []
for i in range(13):
    k = k_chr((k_idx(seg2[i]) - k_idx(seg2_pt_known[i])) % 26)
    seg2_key_known.append(k)
print(f"  Derived key[0:13] = {''.join(seg2_key_known)}")

# Test all possible periods for segment 2
print("\n  Testing periodic keys for segment 2:")
for period in range(1, 14):
    # Check if the derived key is periodic with this period
    consistent = True
    key_of_period = {}
    for i, kc in enumerate(seg2_key_known):
        pos = i % period
        if pos in key_of_period:
            if key_of_period[pos] != kc:
                consistent = False
                break
        else:
            key_of_period[pos] = kc
    if consistent:
        key_str = ''.join(key_of_period[j] for j in range(period))
        # Decrypt full segment with this key
        seg2_pt = vig_decrypt(seg2, key_str)
        print(f"    Period {period}: key={key_str} PT={seg2_pt}")

# For segment 5 (15 chars): BERLINCLOCK at positions 4-14
seg5 = segments[4]  # INFBNYPVTTMZFPK
seg5_pt_known = "BERLINCLOCK"
seg5_offset = 4  # BERLINCLOCK starts at position 4 in segment
print(f"\nSegment 5: {seg5} (15 chars)")
print(f"  Known PT[4:15] = BERLINCLOCK (but segment only has 15 chars...)")
# Wait: segment 5 has 15 chars, BERLINCLOCK is 11 chars at positions 4-14
# So position 15 doesn't exist. BERLINCLOCK fills positions 4-14 exactly.
print(f"  Unknown PT[0:4] = ????")

# Derive key for BERLINCLOCK portion
seg5_key_known = []
for i in range(11):
    ct_pos = seg5_offset + i
    k = k_chr((k_idx(seg5[ct_pos]) - k_idx(seg5_pt_known[i])) % 26)
    seg5_key_known.append(k)
print(f"  Derived key[4:15] = {''.join(seg5_key_known)}")

# Test periodic keys for segment 5
print("\n  Testing periodic keys for segment 5:")
for period in range(1, 12):
    key_of_period = {}
    consistent = True
    for i, kc in enumerate(seg5_key_known):
        pos = (seg5_offset + i) % period
        if pos in key_of_period:
            if key_of_period[pos] != kc:
                consistent = False
                break
        else:
            key_of_period[pos] = kc
    if consistent and len(key_of_period) == period:
        key_str = ''.join(key_of_period[j] for j in range(period))
        seg5_pt = vig_decrypt(seg5, key_str)
        print(f"    Period {period}: key={key_str} PT={seg5_pt}")
    elif consistent:
        # Partial key - fill in unknowns
        key_chars = []
        for j in range(period):
            key_chars.append(key_of_period.get(j, '?'))
        key_disp = ''.join(key_chars)
        if '?' not in key_disp:
            seg5_pt = vig_decrypt(seg5, key_disp)
            print(f"    Period {period}: key={key_disp} PT={seg5_pt}")
        else:
            print(f"    Period {period}: key={key_disp} (incomplete)")

# Test if segments use a common key but different starting offsets
print("\n--- Common key with segment offsets ---")
# If all segments use the same key but start at different offsets:
# The key derived from seg2 (at global position 21) and seg5 (at global position 59)
# would need to be consistent.
# Seg2 key starts at some offset O2 in the master key
# Seg5 key starts at offset O5

# With period 29 master key, seg2 starts at key offset 21 (global position 21 mod 29 = 21)
# But if W's are REMOVED, positions shift:
# Without W's, position of EASTNORTHEAST = 21 - 1 (one W before it at pos 20) = 20
# Without W's, position of BERLINCLOCK = 63 - 4 (four W's before it at pos 20,36,48,58) = 59

# If the key is applied to the TEXT WITHOUT W's:
text_no_w = K4.replace('W', '')
print(f"K4 without W ({len(text_no_w)} chars): {text_no_w}")

# EASTNORTHEAST in text_no_w
for crib in ["EASTNORTHEAST", "BERLINCLOCK"]:
    # Positions of crib chars in original K4
    pass

# Actually, if W's are separators, the encrypted segments are concatenated
# Let's try: concatenate segments and apply period-29 Vigenere
concatenated = ''.join(segments)
print(f"\nConcatenated (no W): {concatenated} ({len(concatenated)} chars)")

# Find where cribs would be in concatenated text
# Seg1 = 20 chars, Seg2 starts at 20
# EASTNORTHEAST is at seg2[0:13], so at concatenated position 20
# Seg5 starts at 20+15+11+9 = 55
# BERLINCLOCK is at seg5[4:15], so at concatenated position 55+4 = 59

print(f"EASTNORTHEAST position in concatenated: 20")
print(f"BERLINCLOCK position in concatenated: 59")

# Try period-29 Vigenere on concatenated text with known cribs
# Derive key from cribs at NEW positions
known_key_new = {}
for j, pt_char in enumerate("EASTNORTHEAST"):
    ct_pos = 20 + j
    key_pos = ct_pos % 29
    key_char = k_chr((k_idx(concatenated[ct_pos]) - k_idx(pt_char)) % 26)
    if key_pos in known_key_new:
        if known_key_new[key_pos] != key_char:
            print(f"  CONFLICT at key pos {key_pos}: {known_key_new[key_pos]} vs {key_char}")
    else:
        known_key_new[key_pos] = key_char

for j, pt_char in enumerate("BERLINCLOCK"):
    ct_pos = 59 + j
    key_pos = ct_pos % 29
    key_char = k_chr((k_idx(concatenated[ct_pos]) - k_idx(pt_char)) % 26)
    if key_pos in known_key_new:
        if known_key_new[key_pos] != key_char:
            print(f"  CONFLICT at key pos {key_pos}: {known_key_new[key_pos]} vs {key_char}")
    else:
        known_key_new[key_pos] = key_char

key_new_str = ''.join(known_key_new.get(i, '?') for i in range(29))
print(f"\nNew key (W-stripped, period 29): {key_new_str}")
print(f"Known positions: {sorted(known_key_new.keys())}")
unknown_new = [i for i in range(29) if i not in known_key_new]
print(f"Unknown positions: {unknown_new}")

# Decrypt what we can
pt_new = []
for i in range(len(concatenated)):
    kp = i % 29
    if kp in known_key_new:
        pt_new.append(k_chr((k_idx(concatenated[i]) - k_idx(known_key_new[kp])) % 26))
    else:
        pt_new.append('?')
pt_new_str = ''.join(pt_new)
print(f"\nDecrypted (W-stripped): {pt_new_str}")

# Count known vs unknown
known_count = sum(1 for c in pt_new_str if c != '?')
print(f"Known: {known_count}/{len(concatenated)}")

# Check IC of known positions
known_chars = [c for c in pt_new_str if c != '?']
if len(known_chars) > 1:
    nc = Counter(known_chars)
    n = len(known_chars)
    ic = sum(c*(c-1) for c in nc.values()) / (n*(n-1))
    print(f"IC of known positions: {ic:.4f}")
    non_crib = [c for i, c in enumerate(pt_new_str) if c != '?' and not (20 <= i <= 32) and not (59 <= i <= 69)]
    if len(non_crib) > 1:
        nc2 = Counter(non_crib)
        n2 = len(non_crib)
        ic2 = sum(c*(c-1) for c in nc2.values()) / (n2*(n2-1))
        print(f"IC of non-crib known positions ({n2} chars): {ic2:.4f}")

# Compare with original key
print("\n--- Key comparison: original vs W-stripped ---")
orig_key = "OYNKYELYOIECBAQK?????RDUMRIYW"
print(f"Original (with W): {orig_key}")
print(f"W-stripped:         {key_new_str}")
for i in range(29):
    o = orig_key[i]
    n = key_new_str[i]
    if o != '?' and n != '?':
        match = "=" if o == n else f"DIFFER ({o} vs {n})"
        print(f"  Pos {i:2d}: {match}")

# Test: what if we use KRYPTOS alphabet Beaufort instead of Vigenere?
print("\n--- Beaufort variant on concatenated text ---")
known_key_beaufort = {}
for j, pt_char in enumerate("EASTNORTHEAST"):
    ct_pos = 20 + j
    key_pos = ct_pos % 29
    # Beaufort: ct = key - pt, so key = ct + pt
    key_char = k_chr((k_idx(concatenated[ct_pos]) + k_idx(pt_char)) % 26)
    if key_pos in known_key_beaufort:
        if known_key_beaufort[key_pos] != key_char:
            print(f"  CONFLICT at key pos {key_pos}")
    else:
        known_key_beaufort[key_pos] = key_char

for j, pt_char in enumerate("BERLINCLOCK"):
    ct_pos = 59 + j
    key_pos = ct_pos % 29
    key_char = k_chr((k_idx(concatenated[ct_pos]) + k_idx(pt_char)) % 26)
    if key_pos in known_key_beaufort:
        if known_key_beaufort[key_pos] != key_char:
            print(f"  CONFLICT at key pos {key_pos}")
    else:
        known_key_beaufort[key_pos] = key_char

key_bft_str = ''.join(known_key_beaufort.get(i, '?') for i in range(29))
print(f"Beaufort key (W-stripped, period 29): {key_bft_str}")

# Decrypt with Beaufort
pt_bft = []
for i in range(len(concatenated)):
    kp = i % 29
    if kp in known_key_beaufort:
        # pt = key - ct
        pt_bft.append(k_chr((k_idx(known_key_beaufort[kp]) - k_idx(concatenated[i])) % 26)
)
    else:
        pt_bft.append('?')
pt_bft_str = ''.join(pt_bft)
print(f"Beaufort PT (W-stripped): {pt_bft_str}")

# Check non-crib IC for Beaufort
non_crib_bft = [c for i, c in enumerate(pt_bft_str) if c != '?' and not (20 <= i <= 32) and not (59 <= i <= 69)]
if len(non_crib_bft) > 1:
    nc3 = Counter(non_crib_bft)
    n3 = len(non_crib_bft)
    ic3 = sum(c*(c-1) for c in nc3.values()) / (n3*(n3-1))
    print(f"Beaufort non-crib IC ({n3} chars): {ic3:.4f}")

# CRITICAL TEST: Does stripping W's and using period 29 produce better IC?
print("\n" + "=" * 80)
print("CRITICAL IC COMPARISON")
print("=" * 80)

# Method 1: Original K4 with period 29 (known key)
orig_non_crib = []
for i in range(97):
    kp = i % 29
    if kp in {k: v for k, v in enumerate("OYNKYELYOIECBAQK") if True}:
        pass  # This is wrong, let me redo

# Let me use the proper known_key dict
known_key_orig = {}
for j, pt_char in enumerate("EASTNORTHEAST"):
    ct_pos = 21 + j
    key_pos = ct_pos % 29
    known_key_orig[key_pos] = k_chr((k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26)
for j, pt_char in enumerate("BERLINCLOCK"):
    ct_pos = 63 + j
    key_pos = ct_pos % 29
    known_key_orig[key_pos] = k_chr((k_idx(K4[ct_pos]) - k_idx(pt_char)) % 26)

orig_non_crib_chars = []
for i in range(97):
    kp = i % 29
    if kp in known_key_orig and not (21 <= i <= 33) and not (63 <= i <= 73):
        c = k_chr((k_idx(K4[i]) - k_idx(known_key_orig[kp])) % 26)
        orig_non_crib_chars.append(c)

new_non_crib_chars = []
for i in range(len(concatenated)):
    kp = i % 29
    if kp in known_key_new and not (20 <= i <= 32) and not (59 <= i <= 69):
        c = k_chr((k_idx(concatenated[i]) - k_idx(known_key_new[kp])) % 26)
        new_non_crib_chars.append(c)

if len(orig_non_crib_chars) > 1:
    nc_o = Counter(orig_non_crib_chars)
    n_o = len(orig_non_crib_chars)
    ic_o = sum(c*(c-1) for c in nc_o.values()) / (n_o*(n_o-1))
    print(f"Original (with W): non-crib IC = {ic_o:.4f} ({n_o} chars)")
    print(f"  Chars: {''.join(orig_non_crib_chars)}")

if len(new_non_crib_chars) > 1:
    nc_n = Counter(new_non_crib_chars)
    n_n = len(new_non_crib_chars)
    ic_n = sum(c*(c-1) for c in nc_n.values()) / (n_n*(n_n-1))
    print(f"W-stripped: non-crib IC = {ic_n:.4f} ({n_n} chars)")
    print(f"  Chars: {''.join(new_non_crib_chars)}")

print(f"\nIC improvement from W-stripping: {'YES' if len(new_non_crib_chars) > 1 and ic_n > ic_o else 'NO'}")

print("\nDone.")
