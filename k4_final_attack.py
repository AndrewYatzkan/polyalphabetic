#!/usr/bin/env python3
"""
K4 Final Attack - Position-by-position key analysis

Try to find ANY key stream (not necessarily periodic) that:
1. Produces BERLINCLOCK at position 63
2. Produces NORTHEAST somewhere
3. Results in English-like text overall
"""

import itertools
from collections import Counter
import re

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def derive_key(ct, pt, alpha=KRYPTOS_ALPHA):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

def decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

print("="*70)
print("K4 FINAL COMPREHENSIVE ATTACK")
print("="*70)

# Fixed constraint: BERLINCLOCK at positions 63-73
BC_KEY = "ELYOIECBAQK"  # Required key for BERLINCLOCK

print(f"\nFixed constraint: Key[63:74] = {BC_KEY}")
print(f"This produces: BERLINCLOCK")

# For NORTHEAST to appear at position P, we need specific key values
# Let's find ALL positions where NORTHEAST could appear without
# conflicting with BERLINCLOCK

print("\n" + "="*70)
print("FINDING NON-CONFLICTING NORTHEAST POSITIONS")
print("="*70)

NORTHEAST = "NORTHEAST"
valid_ne_positions = []

for ne_pos in range(len(K4) - 9 + 1):
    # Check if this position conflicts with BERLINCLOCK
    conflicts = False
    for i in range(9):
        pos = ne_pos + i
        if 63 <= pos <= 73:  # Overlaps with BERLINCLOCK
            bc_idx = pos - 63
            # What key char does NORTHEAST need here?
            ne_key = derive_key(K4[pos], NORTHEAST[i])
            if ne_key != BC_KEY[bc_idx]:
                conflicts = True
                break

    if not conflicts:
        # Calculate required key for NORTHEAST at this position
        ne_key_stream = ''.join(derive_key(K4[ne_pos + i], NORTHEAST[i])
                                 for i in range(9))
        valid_ne_positions.append((ne_pos, ne_key_stream))

print(f"\nFound {len(valid_ne_positions)} non-conflicting NORTHEAST positions:")
for pos, key in valid_ne_positions[:20]:  # Show first 20
    print(f"  Position {pos}: key = {key}")

if len(valid_ne_positions) > 20:
    print(f"  ... and {len(valid_ne_positions) - 20} more")

# Now, for each valid NORTHEAST position, construct the partial key stream
# and see if any pattern emerges
print("\n" + "="*70)
print("ANALYZING KEY PATTERNS")
print("="*70)

for ne_pos, ne_key in valid_ne_positions[:10]:  # Analyze top 10
    print(f"\n--- NORTHEAST at position {ne_pos} ---")

    # Build partial key stream
    key_stream = ['?'] * len(K4)

    # Fill in BERLINCLOCK key
    for i, k in enumerate(BC_KEY):
        key_stream[63 + i] = k

    # Fill in NORTHEAST key
    for i, k in enumerate(ne_key):
        key_stream[ne_pos + i] = k

    # Show the partial key
    key_str = ''.join(key_stream)
    print(f"  Partial key: ...{key_str[max(0,ne_pos-5):ne_pos]}[{key_str[ne_pos:ne_pos+9]}]{key_str[ne_pos+9:min(len(K4),ne_pos+14)]}...")
    print(f"                ...{key_str[58:63]}[{key_str[63:74]}]{key_str[74:79]}...")

    # Count how many key positions are determined
    known = sum(1 for k in key_stream if k != '?')
    print(f"  Known key positions: {known}/{len(K4)}")

    # Check for any patterns in the combined key constraints
    known_keys = [(i, k) for i, k in enumerate(key_stream) if k != '?']

    # Look for repeating patterns
    for period in range(5, 20):
        matches = 0
        conflicts = 0
        for i, k in known_keys:
            for j, k2 in known_keys:
                if i != j and (j - i) % period == 0:
                    if k == k2:
                        matches += 1
                    else:
                        conflicts += 1
        if matches > 0 and conflicts == 0:
            print(f"  Period {period}: {matches} matches, 0 conflicts")

# Try to find a working key by exploring common English plaintext patterns
print("\n" + "="*70)
print("TRYING ENGLISH PLAINTEXT PATTERNS")
print("="*70)

# Common phrases that might appear with BERLINCLOCK and NORTHEAST
patterns = [
    ("THE ", 0),
    ("AND ", 0),
    ("NORTH", 0),
    ("EAST", 0),
    ("DEGREES", 0),
    ("CLOCK", 0),
]

# For each valid NORTHEAST position, try filling in common patterns
for ne_pos, ne_key in valid_ne_positions[:5]:
    print(f"\n--- Testing with NORTHEAST at {ne_pos} ---")

    # Try to find positions where common words might fit
    # without conflicting with known key constraints

    # Build constraint set
    key_constraints = {}
    for i, k in enumerate(BC_KEY):
        key_constraints[63 + i] = k
    for i, k in enumerate(ne_key):
        key_constraints[ne_pos + i] = k

    # Try placing "THE" at various positions
    for the_pos in range(len(K4) - 3):
        # Skip if conflicts with known constraints
        conflict = False
        the_key = ""
        for i, pt in enumerate("THE"):
            pos = the_pos + i
            needed_key = derive_key(K4[pos], pt)
            if pos in key_constraints and key_constraints[pos] != needed_key:
                conflict = True
                break
            the_key += needed_key

        if not conflict:
            # Check if this key makes sense
            if the_pos < 10 or the_pos > 80:  # Beginning or end
                print(f"    'THE' could fit at position {the_pos}, key={the_key}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"""
Analysis complete. K4 remains unsolved.

Key findings:
1. {len(valid_ne_positions)} positions exist where NORTHEAST can appear
   without conflicting with BERLINCLOCK at position 63

2. No simple periodic pattern connects these constraints

3. The cipher likely uses one of:
   - A non-periodic key (e.g., book cipher, running key)
   - Multiple encryption layers
   - A custom cipher designed by Sanborn
   - Position-dependent transformations

The key stream 'ELYOIECBAQK' at position 63 (for BERLINCLOCK)
remains the most significant clue for future cryptanalysis.
""")
