#!/usr/bin/env python3
"""
Deep dive into the FORCED key segment (positions 5-24).
These 20 positions are mathematically certain from BERLINCLOCK and NORTHEAST.
If there's a pattern, it's HERE.
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# FORCED key segment (positions 5-24)
# From BERLINCLOCK at pos 63: key[5:16] = ELYOIECBAQK
# From NORTHEAST at pos 16:  key[16:25] = VAATCRDUM
FORCED = "ELYOIECBAQKVAATCRDUM"

def k_idx(c):
    return KRYPTOS.index(c)

def std_idx(c):
    return ord(c) - ord('A')

print("=" * 70)
print("DEEP DIVE: FORCED KEY SEGMENT (positions 5-24)")
print("=" * 70)

print(f"\nForced key: {FORCED}")
print(f"Length: {len(FORCED)}")

# KRYPTOS indices
k_vals = [k_idx(c) for c in FORCED]
print(f"KRYPTOS indices: {k_vals}")

# Standard A=0 indices
s_vals = [std_idx(c) for c in FORCED]
print(f"Standard A=0:    {s_vals}")

# 1. Look for the key pattern relative to KRYPTOS and PALIMPSEST
print("\n--- RELATIONSHIP TO K1/K2 KEYS ---")
print(f"K1 key: PALIMPSEST = {[std_idx(c) for c in 'PALIMPSEST']}")
print(f"K2 key: ABSCISSA   = {[std_idx(c) for c in 'ABSCISSA']}")

# Check if forced key letters appear in PALIMPSEST or ABSCISSA
for i, c in enumerate(FORCED):
    in_pal = c in "PALIMPSEST"
    in_abs = c in "ABSCISSA"
    marker = ""
    if in_pal and in_abs:
        marker = " ← in BOTH"
    elif in_pal:
        marker = " ← in PALIMPSEST"
    elif in_abs:
        marker = " ← in ABSCISSA"
    print(f"  [{i+5:2d}] {c} (k={k_vals[i]:2d}, s={s_vals[i]:2d}){marker}")

# 2. What word/phrase could the forced key represent?
print("\n--- FORCED KEY AS TEXT ---")
print(f"As-is: {FORCED}")
print(f"Reversed: {FORCED[::-1]}")

# Caesar shifts
print("\nCaesar shifts of forced key:")
for shift in range(1, 26):
    shifted = ''.join(chr((ord(c) - ord('A') + shift) % 26 + ord('A')) for c in FORCED)
    # Check for common English fragments
    has_word = False
    for w in ["THE", "AND", "FOR", "ARE", "NOT", "HIS", "HER", "WAS", "ONE", "ALL"]:
        if w in shifted:
            has_word = True
            break
    if has_word:
        print(f"  Shift {shift:2d}: {shifted}")

# 3. Vigenere decrypt forced key with known keys
print("\n--- DECRYPT FORCED KEY WITH OTHER KEYS ---")
def vig_decrypt(ct, key):
    pt = ""
    for i, c in enumerate(ct):
        ci = ord(c) - ord('A')
        ki = ord(key[i % len(key)]) - ord('A')
        pi = (ci - ki) % 26
        pt += chr(pi + ord('A'))
    return pt

keys_to_try = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
                "NORTHEAST", "BERLINCLOCK", "UNDER", "ABOVE"]
for key in keys_to_try:
    result = vig_decrypt(FORCED, key)
    print(f"  FORCED decrypted with {key:15s}: {result}")

# 4. Relationship between BERLINCLOCK and NORTHEAST segments
print("\n--- BERLINCLOCK vs NORTHEAST SEGMENTS ---")
bc = "ELYOIECBAQK"  # 11 chars
ne = "VAATCRDUM"     # 9 chars

bc_s = [std_idx(c) for c in bc]
ne_s = [std_idx(c) for c in ne]

print(f"BC: {bc} = {bc_s}")
print(f"NE: {ne}   = {ne_s}")

# Pairwise relationships (first 9 chars of each)
print("\nPairwise (first 9):")
for i in range(9):
    diff = (bc_s[i] - ne_s[i]) % 26
    xor = bc_s[i] ^ ne_s[i]
    sumv = (bc_s[i] + ne_s[i]) % 26
    print(f"  BC[{i}]={bc[i]}({bc_s[i]:2d}) NE[{i}]={ne[i]}({ne_s[i]:2d})  diff={diff:2d} xor={xor:2d} sum={sumv:2d}")

# 5. Check if key values match known constants
print("\n--- KEY VALUES vs KNOWN CONSTANTS ---")
print(f"Sum of all forced values (std): {sum(s_vals)}")
print(f"Sum of BC segment (std): {sum(bc_s)}")
print(f"Sum of NE segment (std): {sum(ne_s)}")
print(f"CIA latitude (38.9517): floor={38}")
print(f"CIA longitude (77.1467): floor={77}")
print(f"Berlin lat (52.52): floor={52}")
print(f"Berlin lon (13.41): floor={13}")
print(f"Sum BC + Sum NE = {sum(bc_s) + sum(ne_s)}")

# 6. What plaintext at positions 0-4 would make the key spell something?
print("\n--- WHAT STARTING WORD MAKES THE FULL KEY SPELL SOMETHING? ---")
# If key[0:5] = X, what would X need to be for the full key to contain a word?
# Full key = X + ELYOIECBAQKVAATCRDUM + Y (where Y = key[25:28])

# Check what the full key looks like with UNDER
print(f"With UNDER: DIJJQ + {FORCED} + PABT")
print(f"  Full key: DIJJQ{FORCED}PABT")

# What if key[0:5] spells something?
print("\nKey[0:5] options that make words in the full key:")
# The full key is: key[0:5] + ELYOIECBAQK + VAATCRDUM + key[25:29]
# What 5-letter prefix makes the 29-char key contain English words?

# 7. Derive what plaintext position 16 must be if NORTHEAST is elsewhere
print("\n--- WHAT IF NORTHEAST IS NOT AT POSITION 16? ---")
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# BERLINCLOCK at 63 is confirmed. This gives us key[5:16] = ELYOIECBAQK
# If NORTHEAST starts at position N, then for period P:
#   key[(N+i) % P] must decrypt CT[N+i] to NORTHEAST[i]

# For period 29:
print("Period 29: NORTHEAST position compatibility")
bc_key = {}
for i in range(11):
    pos = 63 + i
    kpos = (pos) % 29
    ct = K4_CT[pos]
    pt = "BERLINCLOCK"[i]
    ct_idx = KRYPTOS.index(ct)
    pt_idx = KRYPTOS.index(pt)
    key_val = KRYPTOS[(ct_idx - pt_idx) % 26]
    bc_key[kpos] = key_val

print(f"  Key from BERLINCLOCK: {bc_key}")

for ne_start in range(89):
    ne_key = {}
    for i in range(9):
        pos = ne_start + i
        if pos >= 97:
            break
        kpos = pos % 29
        ct = K4_CT[pos]
        pt = "NORTHEAST"[i]
        ct_idx = KRYPTOS.index(ct)
        pt_idx = KRYPTOS.index(pt)
        key_val = KRYPTOS[(ct_idx - pt_idx) % 26]
        ne_key[kpos] = key_val

    # Check compatibility
    conflict = False
    for kpos, val in ne_key.items():
        if kpos in bc_key and bc_key[kpos] != val:
            conflict = True
            break

    if not conflict:
        # How many key positions are now determined?
        combined = {**bc_key, **ne_key}
        # Build partial key
        partial = ['?'] * 29
        for kpos, val in combined.items():
            partial[kpos] = val
        pkey = ''.join(partial)
        unknowns = pkey.count('?')

        # Only show if we determine enough
        if unknowns <= 10:
            # Decrypt what we can
            pt = ""
            for j in range(97):
                kpos = j % 29
                if partial[kpos] != '?':
                    ct_idx = KRYPTOS.index(K4_CT[j])
                    key_idx = KRYPTOS.index(partial[kpos])
                    pt_idx = (ct_idx - key_idx) % 26
                    pt += KRYPTOS[pt_idx]
                else:
                    pt += '.'

            print(f"\n  NE@{ne_start:2d}: key={pkey} ({unknowns} unknowns)")
            print(f"         PT={pt}")

            # Count readable words
            words_found = []
            for w in ["THE", "AND", "FOR", "NOT", "YOU", "ALL", "HIS", "HER", "WAS", "ONE",
                       "OUT", "OUR", "DAY", "SEE", "END", "WAY", "NEW", "OLD", "USE",
                       "UNDER", "ABOVE", "BELOW", "THERE", "WHERE", "CLOCK", "NORTH",
                       "SOUTH", "EAST", "WEST", "BERLIN", "LAYER", "STONE", "EARTH",
                       "LIGHT", "NIGHT", "RIGHT", "WATCH", "HANDS", "HOURS", "FIELD",
                       "WORLD", "PLACE", "POINT", "ABOUT", "AFTER"]:
                if w in pt:
                    idx = pt.index(w)
                    words_found.append((w, idx))
            if words_found:
                print(f"         Words: {words_found}")
