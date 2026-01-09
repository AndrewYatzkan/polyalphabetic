#!/usr/bin/env python3
"""
K4 Backwards Solve

Work backwards from known constraints:
1. BERLINCLOCK at position 63-73 (0-indexed)
2. Use this to derive key stream constraints
3. Try to extend to find NORTHEAST and other patterns

Key insight: For Vigenère with KRYPTOS alphabet:
- Key stream at 63-73 = ELYOIECBAQK (produces BERLINCLOCK)
- For ANY periodic cipher, this constrains the full key
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def derive_key(ct, pt, alpha=KRYPTOS_ALPHA):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

def decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

def calc_ioc(text):
    freq = Counter(text)
    n = len(text)
    if n <= 1:
        return 0
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

print("="*70)
print("K4 BACKWARDS SOLVE")
print("="*70)

# Known: BERLINCLOCK at position 63
bc_key = ''.join(derive_key(K4[63+i], c, KRYPTOS_ALPHA)
                 for i, c in enumerate("BERLINCLOCK"))
print(f"\nKey stream for BERLINCLOCK at 63: {bc_key}")

# For each period P, key positions 63%P through 73%P are constrained
# Period P means key[63%P] = bc_key[0], key[64%P] = bc_key[1], etc.

print("\n" + "="*70)
print("PERIODIC KEY CONSTRAINT ANALYSIS")
print("="*70)

for period in range(7, 50):
    # Map key position -> required value
    key_constraints = {}
    conflict = False

    for i, k in enumerate(bc_key):
        pos = (63 + i) % period
        if pos in key_constraints:
            if key_constraints[pos] != k:
                conflict = True
                break
        else:
            key_constraints[pos] = k

    if not conflict:
        # Build partial key
        partial_key = ['?'] * period
        for pos, k in key_constraints.items():
            partial_key[pos] = k

        # Count constrained positions
        constrained = sum(1 for k in partial_key if k != '?')

        # Decrypt with partial key
        partial_pt = []
        for i, c in enumerate(K4):
            k = partial_key[i % period]
            if k != '?':
                partial_pt.append(decrypt(c, k))
            else:
                partial_pt.append('?')
        partial_pt = ''.join(partial_pt)

        # Check if this contains NORTHEAST
        has_northeast = 'NORTHEAST' in partial_pt or 'NORTH' in partial_pt

        # Calculate IoC of known characters
        known_chars = [c for c in partial_pt if c != '?']
        ioc = calc_ioc(known_chars) if known_chars else 0

        if constrained >= 5 or has_northeast:
            print(f"\nPeriod {period}: {constrained}/{period} positions constrained")
            print(f"  Key: {''.join(partial_key)}")
            print(f"  PT: {partial_pt[:50]}...")
            print(f"  IoC (known chars): {ioc:.4f}")
            if has_northeast:
                print("  *** Contains NORTH/NORTHEAST! ***")

# Now let's try to find period where both BERLINCLOCK and NORTHEAST constraints work
print("\n" + "="*70)
print("DUAL CONSTRAINT ANALYSIS (BERLINCLOCK + NORTHEAST)")
print("="*70)

# For each possible NORTHEAST position
for ne_start in range(0, len(K4) - 9):
    # Skip if overlaps with BERLINCLOCK
    if 63 <= ne_start <= 73 or 63 <= ne_start + 8 <= 73:
        continue

    ne_key = ''.join(derive_key(K4[ne_start+i], c, KRYPTOS_ALPHA)
                     for i, c in enumerate("NORTHEAST"))

    # Try to find a period that satisfies both constraints
    for period in range(7, 50):
        bc_constraints = {}
        ne_constraints = {}
        conflict = False

        # BERLINCLOCK constraints
        for i, k in enumerate(bc_key):
            pos = (63 + i) % period
            bc_constraints[pos] = k

        # NORTHEAST constraints
        for i, k in enumerate(ne_key):
            pos = (ne_start + i) % period
            ne_constraints[pos] = k

        # Check for conflicts between the two sets
        for pos in set(bc_constraints.keys()) & set(ne_constraints.keys()):
            if bc_constraints[pos] != ne_constraints[pos]:
                conflict = True
                break

        if not conflict:
            # Merge constraints
            all_constraints = {**bc_constraints, **ne_constraints}

            # Build key
            key = ['?'] * period
            for pos, k in all_constraints.items():
                key[pos] = k

            constrained = sum(1 for k in key if k != '?')

            # Only report if highly constrained
            if constrained >= period * 0.6:
                # Decrypt
                pt = []
                for i, c in enumerate(K4):
                    k = key[i % period]
                    if k != '?':
                        pt.append(decrypt(c, k))
                    else:
                        pt.append('?')
                pt = ''.join(pt)

                ioc = calc_ioc([c for c in pt if c != '?'])

                print(f"\nNE@{ne_start}, Period {period}: {constrained}/{period} constrained")
                print(f"  Key: {''.join(key)}")
                print(f"  PT: {pt}")
                print(f"  IoC: {ioc:.4f}")

# Let's also try the case where we DON'T use KRYPTOS alphabet
print("\n" + "="*70)
print("STANDARD ALPHABET ANALYSIS")
print("="*70)

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

bc_key_std = ''.join(derive_key(K4[63+i], c, STANDARD_ALPHA)
                     for i, c in enumerate("BERLINCLOCK"))
print(f"Key stream for BERLINCLOCK (standard alphabet): {bc_key_std}")

# Try this key as Vigenère
for period in [11, 22, 33]:  # Divisors of 11 (BERLINCLOCK length)
    key = list(bc_key_std[:period])
    while len(key) < period:
        key.append('?')

    pt = ''.join(decrypt(K4[i], key[i % period], STANDARD_ALPHA)
                 if key[i % period] != '?' else '?'
                 for i in range(len(K4)))

    print(f"\nPeriod {period} with standard alphabet:")
    print(f"  Key: {''.join(key)}")
    print(f"  PT: {pt}")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
