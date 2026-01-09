#!/usr/bin/env python3
"""
K4 Triple Crib Analysis

Known cribs from Sanborn:
1. BERLIN at positions 64-69 (1-indexed) = 63-68 (0-indexed)
2. CLOCK at positions 70-74 (1-indexed) = 69-73 (0-indexed)
3. EAST at positions 22-25 (1-indexed) = 21-24 (0-indexed)

Additionally, NORTHEAST appears somewhere, which means NORTH is at positions 17-21 (0-indexed)
if NORTHEAST = NORTH + EAST with EAST at 21-24.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def derive_key(ct, pt, alpha):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

def decrypt(ct, key, alpha):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

print("="*70)
print("K4 TRIPLE CRIB ANALYSIS")
print("="*70)

# Known positions (0-indexed)
cribs = {
    'BERLIN': (63, 68),      # positions 63-68
    'CLOCK': (69, 73),       # positions 69-73
    'EAST': (21, 24),        # positions 21-24
}

# If EAST is at 21-24, and we have NORTHEAST, NORTH would be at 17-20
# But that's 4 letters NORTH = 5 letters, so NORTH at 17-21, EAST at 21-24
# Wait, that overlaps at 21... Let me reconsider

# NORTHEAST = 9 characters
# If EAST ends at position 24 (0-indexed), NORTHEAST starts at position 16
# N(16) O(17) R(18) T(19) H(20) E(21) A(22) S(23) T(24)

print("\nIf EAST is at positions 21-24 (0-indexed):")
print("And NORTHEAST appears in the plaintext:")
print("Then NORTHEAST spans positions 16-24")
print()

# Let's verify with both alphabets
for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    print(f"\n{'='*70}")
    print(f"Using {alpha_name} alphabet")
    print("="*70)

    # Derive key stream from all known cribs
    key_stream = ['?'] * len(K4)

    # BERLINCLOCK at 63-73
    berlinclock = "BERLINCLOCK"
    for i, pt in enumerate(berlinclock):
        pos = 63 + i
        ct = K4[pos]
        key_char = derive_key(ct, pt, alpha)
        key_stream[pos] = key_char

    # NORTHEAST at 16-24
    northeast = "NORTHEAST"
    for i, pt in enumerate(northeast):
        pos = 16 + i
        ct = K4[pos]
        key_char = derive_key(ct, pt, alpha)
        key_stream[pos] = key_char

    print("\nDerived key stream:")
    print(f"Positions 16-24 (NORTHEAST): {''.join(key_stream[16:25])}")
    print(f"Positions 63-73 (BERLINCLOCK): {''.join(key_stream[63:74])}")

    # Check for periodic patterns
    print("\nChecking for periodic patterns between the two key segments...")

    ne_key = ''.join(key_stream[16:25])
    bc_key = ''.join(key_stream[63:74])

    print(f"NORTHEAST key (pos 16-24): {ne_key}")
    print(f"BERLINCLOCK key (pos 63-73): {bc_key}")

    # The distance between starts is 63 - 16 = 47 positions
    # For period P, position 16 and 63 align if 47 % P == 0
    # 47 = 47 (prime), so only period 47 or 1 works directly

    # Check various periods
    print("\nPeriod compatibility check:")
    for period in range(5, 50):
        compatible = True
        conflicts = []
        matches = []

        # Check if any positions in NORTHEAST and BERLINCLOCK would use same key char
        for ne_pos in range(16, 25):
            for bc_pos in range(63, 74):
                if (bc_pos - ne_pos) % period == 0:
                    ne_idx = ne_pos - 16
                    bc_idx = bc_pos - 63
                    ne_k = key_stream[ne_pos]
                    bc_k = key_stream[bc_pos]
                    if ne_k != bc_k:
                        conflicts.append((ne_pos, bc_pos, ne_k, bc_k))
                        compatible = False
                    else:
                        matches.append((ne_pos, bc_pos, ne_k))

        if compatible and matches:
            print(f"  Period {period}: COMPATIBLE! Matches: {matches}")
        elif conflicts and len(conflicts) <= 2:
            print(f"  Period {period}: {len(conflicts)} conflicts, {len(matches)} matches")

# Try standard Vigenère with keys that satisfy constraints
print("\n" + "="*70)
print("SEARCHING FOR KEYS SATISFYING ALL THREE CONSTRAINTS")
print("="*70)

# With KRYPTOS alphabet
alpha = KRYPTOS_ALPHA

# Build constraint set
constraints = {}

# NORTHEAST at 16-24
for i, pt in enumerate("NORTHEAST"):
    pos = 16 + i
    constraints[pos] = derive_key(K4[pos], pt, alpha)

# BERLINCLOCK at 63-73
for i, pt in enumerate("BERLINCLOCK"):
    pos = 63 + i
    constraints[pos] = derive_key(K4[pos], pt, alpha)

print(f"\nKey constraints ({len(constraints)} positions fixed):")
for pos in sorted(constraints.keys()):
    print(f"  Position {pos}: key = {constraints[pos]}")

# Check if any periodic key satisfies all constraints
print("\nTrying to find a periodic key that satisfies all constraints...")

for period in range(5, 30):
    # Build key from constraints
    key_positions = {}  # key_idx -> required char

    conflict_found = False
    for pos, k in constraints.items():
        key_idx = pos % period
        if key_idx in key_positions:
            if key_positions[key_idx] != k:
                conflict_found = True
                break
        else:
            key_positions[key_idx] = k

    if not conflict_found:
        # Found a compatible period!
        print(f"\nPeriod {period} is COMPATIBLE!")
        # Build the key
        key = ['?'] * period
        for idx, k in key_positions.items():
            key[idx] = k
        print(f"  Partial key: {''.join(key)}")

        # Decrypt with this partial key
        pt = []
        for i, c in enumerate(K4):
            key_char = key[i % period]
            if key_char != '?':
                pt.append(decrypt(c, key_char, alpha))
            else:
                pt.append('?')
        plaintext = ''.join(pt)
        print(f"  Partial plaintext: {plaintext}")

        # Count known characters
        known = sum(1 for c in plaintext if c != '?')
        print(f"  Known characters: {known}/{len(K4)}")

# What if the position hint was 1-indexed differently?
print("\n" + "="*70)
print("TRYING ALTERNATE POSITION INTERPRETATIONS")
print("="*70)

# Sanborn said "64-69" for BERLIN - but maybe he meant something else
# Let's try EAST at various positions near 21-24
for east_start in range(15, 30):
    alpha = KRYPTOS_ALPHA

    # EAST at this position
    constraints = {}
    for i, pt in enumerate("EAST"):
        pos = east_start + i
        if pos < len(K4):
            constraints[pos] = derive_key(K4[pos], pt, alpha)

    # BERLINCLOCK at 63-73 (this is well-established)
    for i, pt in enumerate("BERLINCLOCK"):
        pos = 63 + i
        constraints[pos] = derive_key(K4[pos], pt, alpha)

    # Check for periodic compatibility
    for period in range(5, 20):
        key_positions = {}
        conflict_found = False

        for pos, k in constraints.items():
            key_idx = pos % period
            if key_idx in key_positions:
                if key_positions[key_idx] != k:
                    conflict_found = True
                    break
            else:
                key_positions[key_idx] = k

        if not conflict_found:
            # Build and test key
            key = ['?'] * period
            for idx, k in key_positions.items():
                key[idx] = k

            # Count non-? positions
            known_key_positions = sum(1 for c in key if c != '?')

            if known_key_positions >= period // 2:  # At least half the key is known
                print(f"\nEAST at {east_start}, Period {period}: COMPATIBLE")
                print(f"  Key: {''.join(key)}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
