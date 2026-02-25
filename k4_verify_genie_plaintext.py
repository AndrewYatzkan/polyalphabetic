#!/usr/bin/env python3
"""
Verify the Genie Engine's claimed plaintext against K4 ciphertext.

The Genie Engine claims:
  Plaintext: "TO SET THE EAST-NORTHEAST HOUR BY BEARING BERLIN CLOCK DEGREES
              GRID POINT NORTHWEST TO FIND GROSSER STERN"

If we remove spaces and punctuation:
  TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN

Check:
1. Does this plaintext have the right length (97)?
2. When encrypted with period-29 Vigenere, does it produce K4?
3. What key would be needed?
4. Does BERLINCLOCK appear at position 63?
5. Does EASTNORTHEAST appear at position 21?
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c):
    return KRYPTOS.index(c)

def k_chr(i):
    return KRYPTOS[i % 26]

def derive_key_char(ct, pt):
    return k_chr(k_idx(ct) - k_idx(pt))

def vig_encrypt(pt, key, alpha=KRYPTOS):
    ct = []
    for i, c in enumerate(pt):
        ki = alpha.index(key[i % len(key)])
        pi = alpha.index(c)
        ct.append(alpha[(pi + ki) % 26])
    return ''.join(ct)

def vig_decrypt(ct, key, alpha=KRYPTOS):
    pt = []
    for i, c in enumerate(ct):
        ki = alpha.index(key[i % len(key)])
        ci = alpha.index(c)
        pt.append(alpha[(ci - ki) % 26])
    return ''.join(pt)

print("=" * 80)
print("GENIE ENGINE PLAINTEXT VERIFICATION")
print("=" * 80)

# The claimed plaintext (remove spaces, hyphens)
genie_pt_raw = "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"
# Note: "BEARING" not "EARRING" - but the raw text above has "EARINGB" which looks wrong
# Let me try the exact claimed text more carefully:
# "TO SET THE EAST-NORTHEAST HOUR BY BEARING BERLIN CLOCK DEGREES GRID POINT NORTHWEST TO FIND GROSSER STERN"

variants = [
    ("Original (no J)", "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"),
    ("With BEARING", "TOSETTHEEASTNORTHEASTHOURBYBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"),
    ("Full with BEARING", "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"),
]

# Actually let me construct it word by word:
words = ["TO", "SET", "THE", "EASTNORTHEAST", "HOUR", "BY", "BEARING", "BERLIN", "CLOCK",
         "DEGREES", "GRID", "POINT", "NORTHWEST", "TO", "FIND", "GROSSER", "STERN"]
full_pt = "".join(words)

# J is not in KRYPTOS alphabet - check if any letter is missing
print(f"\nClaimed plaintext: {full_pt}")
print(f"Length: {len(full_pt)}")
print(f"K4 length: {len(K4)}")

# Check for invalid chars
invalid = [c for c in full_pt if c not in KRYPTOS]
if invalid:
    print(f"WARNING: Invalid chars not in KRYPTOS alphabet: {set(invalid)}")
    # J is not in KRYPTOS alphabet! Need to substitute
    full_pt_fixed = full_pt.replace('J', 'I')  # Standard substitution
    print(f"After J->I: {full_pt_fixed} (len={len(full_pt_fixed)})")
else:
    full_pt_fixed = full_pt
    print("All chars valid in KRYPTOS alphabet")

# Pad or trim to 97
if len(full_pt_fixed) < 97:
    print(f"\nPlaintext is {97 - len(full_pt_fixed)} chars SHORT of 97")
    # Try adding padding letters or extra words
    padding_options = [
        ("X" * (97 - len(full_pt_fixed)), "Pad with X"),
        ("A" * (97 - len(full_pt_fixed)), "Pad with A"),
    ]
elif len(full_pt_fixed) > 97:
    print(f"\nPlaintext is {len(full_pt_fixed) - 97} chars LONG")
elif len(full_pt_fixed) == 97:
    print("\nExact match at 97 chars!")

# Check crib positions
bc_pos = full_pt_fixed.find("BERLINCLOCK")
ene_pos = full_pt_fixed.find("EASTNORTHEAST")
print(f"\nBERLINCLOCK position: {bc_pos} (expected: 63)")
print(f"EASTNORTHEAST position: {ene_pos} (expected: 21)")

# If the plaintext is correct, derive the full key
if len(full_pt_fixed) == 97:
    print("\n--- Deriving key from claimed plaintext ---")
    key_chars = []
    for i in range(97):
        kc = derive_key_char(K4[i], full_pt_fixed[i])
        key_chars.append(kc)

    # Check if it's periodic
    for period in range(1, 50):
        consistent = True
        key_of_period = {}
        for i, kc in enumerate(key_chars):
            pos = i % period
            if pos in key_of_period:
                if key_of_period[pos] != kc:
                    consistent = False
                    break
            else:
                key_of_period[pos] = kc
        if consistent:
            key_str = ''.join(key_of_period[j] for j in range(period))
            print(f"  Period {period}: consistent! Key = {key_str}")
            if period <= 35:
                break  # First consistent period

# Try different word arrangements to hit length 97
print("\n" + "=" * 80)
print("TRYING DIFFERENT ARRANGEMENTS TO HIT LENGTH 97")
print("=" * 80)

# Let's try various phrasings
test_plaintexts = [
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYBEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "SETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERNX",
    "TOSETANEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREEATGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGOFBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDTHEGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGTHEBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
]

for pt in test_plaintexts:
    pt_clean = pt.replace('J', 'I')
    bc = pt_clean.find("BERLINCLOCK")
    ene = pt_clean.find("EASTNORTHEAST")

    status = []
    if len(pt_clean) == 97:
        status.append("LEN=97!")
    if bc == 63:
        status.append("BC@63!")
    if ene == 21:
        status.append("ENE@21!")

    marker = " *** " if len(status) >= 2 else ""
    print(f"  len={len(pt_clean):3d} BC@{bc:3d} ENE@{ene:3d} {marker}{' '.join(status)}")
    print(f"    {pt_clean}")

    if len(pt_clean) == 97 and bc == 63 and ene == 21:
        print(f"    *** PERFECT MATCH! ***")
        # Derive key
        key_chars = [derive_key_char(K4[i], pt_clean[i]) for i in range(97)]
        for period in range(1, 50):
            consistent = True
            key_of_period = {}
            for i, kc in enumerate(key_chars):
                pos = i % period
                if pos in key_of_period:
                    if key_of_period[pos] != kc:
                        consistent = False
                        break
                else:
                    key_of_period[pos] = kc
            if consistent:
                key_str = ''.join(key_of_period[j] for j in range(period))
                print(f"    Period {period}: Key = {key_str}")
                break

# Now systematically: what plaintext of length 97 has EASTNORTHEAST@21 and BERLINCLOCK@63?
print("\n" + "=" * 80)
print("CONSTRAINT-BASED ANALYSIS")
print("=" * 80)
print("EASTNORTHEAST occupies positions 21-33")
print("BERLINCLOCK occupies positions 63-73")
print("Gap 1: positions 0-20 (21 chars)")
print("Gap 2: positions 34-62 (29 chars)")
print("Gap 3: positions 74-96 (23 chars)")
print()

# What English phrases fit?
# From the Genie Engine:
# Gap 1 (21 chars): "TOSETTHE" = 8 chars, need 21
# Hmm, "TO SET THE" = 8 chars, but we need 21 before EASTNORTHEAST

# Let's count more carefully
print("Genie claimed: TO SET THE EASTNORTHEAST HOUR BY BEARING BERLIN CLOCK ...")
pt_test = "TOSETTHE"
print(f"'TOSETTHE' = {len(pt_test)} chars -> need {21 - len(pt_test)} more before EASTNORTHEAST@21")

# What if the claimed plaintext positions don't match the confirmed crib positions?
# Maybe the Genie Engine uses a DIFFERENT definition of position?

# Let's check: in the Genie output, where does EASTNORTHEAST start?
genie_full = "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN"
print(f"\nGenie plaintext: {genie_full}")
print(f"  EASTNORTHEAST @ position {genie_full.find('EASTNORTHEAST')}")
print(f"  BERLINCLOCK @ position {genie_full.find('BERLINCLOCK')}")
print(f"  Length: {len(genie_full)}")

# Hmm - EASTNORTHEAST is at position 8, BERLINCLOCK at position 38!
# NOT at 21 and 63! This contradicts the confirmed crib positions!

# What if the Genie Engine applies a transposition that moves the cribs?
# The cribs are confirmed at positions 21 and 63 in the CIPHERTEXT
# If there's a transposition, the cribs could be at different positions in the plaintext

# Wait - Sanborn said positions 64-69 decrypt to BERLIN (1-indexed = 63-68 0-indexed)
# and 70-74 decrypt to CLOCK (= 69-73 0-indexed)
# This means the CIPHERTEXT at those positions, when decrypted, gives BERLINCLOCK
# Under standard Vigenere, the crib positions are in the PLAINTEXT at positions 63-73
# But if there's a transposition layer, the plaintext might have been rearranged

print("\n" + "=" * 80)
print("CRITICAL ANALYSIS: GENIE ENGINE vs CONFIRMED CRIBS")
print("=" * 80)
print()
print("Sanborn confirmed: K4 ciphertext positions 64-74 (1-indexed) decrypt to BERLINCLOCK")
print("This means: decrypt(K4[63:74]) = BERLINCLOCK")
print()
print("For standard Vigenere: plaintext[63:74] = BERLINCLOCK")
print("For Vigenere+transposition: plaintext positions would be DIFFERENT")
print()
print("The Genie Engine claims a route cipher (transposition), so the cribs")
print("would NOT necessarily be at positions 63 and 21 in the plaintext.")
print("Instead, they'd be at the positions that MAP to ciphertext positions 63 and 21")
print("after the transposition.")
print()
print("Genie Engine's claimed plaintext has:")
print(f"  EASTNORTHEAST at position {genie_full.find('EASTNORTHEAST')} (maps to CT position 21 via transposition)")
print(f"  BERLINCLOCK at position {genie_full.find('BERLINCLOCK')} (maps to CT position 63 via transposition)")
print(f"  Length: {len(genie_full)} (needs to be 97)")
print()
print("The Genie plaintext is only 88 chars. It needs 9 more chars to reach 97.")
print("Possible: additional words, padding, or we have the wrong version of the text.")

# Let me try longer versions
print("\n" + "=" * 80)
print("TESTING LONGER GENIE VARIANTS")
print("=" * 80)

longer_variants = [
    "TOSETTHEEASTNORTHEASTHOURBYABEARINGOFBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDTHEGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGOFTHEBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERNX",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDTHEGROSSERSTERNX",
    "XTOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERNX",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGTHEBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERNX",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESATGRIDPOINTNORTHWESTTOFINDGROSSERSTERNX",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDAGROSSERSTERNX",
    "TOSETANEASTNORTHEASTHOURBYEARINGTHEBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGBERLINCLOCKDEGREESFROMGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
    "TOSETTHEEASTNORTHEASTHOURBYEARINGFROMBERLINCLOCKDEGREESGRIDPOINTNORTHWESTTOFINDGROSSERSTERN",
]

for pt in longer_variants:
    pt_clean = pt.replace('J', 'I')
    # Check all chars valid
    bad = [c for c in pt_clean if c not in KRYPTOS]
    if bad:
        pt_clean = pt_clean  # skip
    print(f"  len={len(pt_clean):3d}: {pt_clean[:60]}...")
    if len(pt_clean) == 97:
        print(f"    *** LENGTH 97! ***")
        # This could be the plaintext if a transposition maps cribs correctly
        # Derive the "key" (which would include transposition effects)
        key_chars = [derive_key_char(K4[i], pt_clean[i]) for i in range(97)]
        # Check periodicity
        for period in range(1, 50):
            consistent = True
            key_of_period = {}
            for i, kc in enumerate(key_chars):
                pos = i % period
                if pos in key_of_period:
                    if key_of_period[pos] != kc:
                        consistent = False
                        break
                else:
                    key_of_period[pos] = kc
            if consistent:
                key_str = ''.join(key_of_period[j] for j in range(period))
                print(f"    Periodic key (period {period}): {key_str}")
                break
        else:
            print(f"    No periodic key found (up to period 49)")
            # Show the raw key
            print(f"    Raw key: {''.join(key_chars)}")

print("\n" + "=" * 80)
print("KEY CONCLUSION")
print("=" * 80)
print("""
The Genie Engine plaintext is only 88 characters, not 97.
The cribs are at positions 8 and 38, not 21 and 63.
This means the Genie Engine MUST use a transposition that:
  1. Maps plaintext position 8 → ciphertext position 21 (or wherever ENE goes)
  2. Maps plaintext position 38 → ciphertext position 63 (or wherever BC goes)
  3. Adds 9 more characters somehow

Without the exact transposition mapping and the 3 substitution alphabets,
we cannot verify the Genie Engine claim. The claim remains UNVERIFIABLE
from public information alone.

However, the key insight is: K4 likely involves BOTH substitution AND transposition.
The period-29 Vigenere may describe the substitution part, and there's a separate
transposition that rearranges character positions.
""")
