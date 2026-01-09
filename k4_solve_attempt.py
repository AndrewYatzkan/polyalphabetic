#!/usr/bin/env python3
"""
K4 Solve Attempt - Based on brute force results

We found many keys that produce BERLIN+CLOCK.
Now search for one that ALSO produces NORTHEAST.
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def decrypt(ct, key, alpha):
    return ''.join(alpha[(alpha.index(c) - alpha.index(key[i % len(key)])) % len(alpha)]
                   for i, c in enumerate(ct))

def derive_key(ct, pt, alpha):
    return ''.join(alpha[(alpha.index(c) - alpha.index(p)) % len(alpha)]
                   for c, p in zip(ct, pt))

print("="*70)
print("K4 SOLUTION SEARCH")
print("="*70)

# We found BERLIN@0, CLOCK@6 produces adjacent BERLINCLOCK
# Now let's exhaustively search for a configuration that ALSO has NORTHEAST

print("\nSearching for BERLIN+CLOCK+NORTHEAST in same decryption...")

found_solutions = []

# Try all period lengths
for period in range(5, 20):
    # Try all possible BERLIN positions
    for berlin_pos in range(len(K4) - 6):
        # CLOCK must be adjacent (right after BERLIN) for BERLINCLOCK
        clock_pos = berlin_pos + 6

        if clock_pos + 5 > len(K4):
            continue

        # Derive key constraints from BERLINCLOCK
        bc_ct = K4[berlin_pos:berlin_pos + 11]
        bc_key_constraints = {}

        valid = True
        for i, (ct, pt) in enumerate(zip(bc_ct, "BERLINCLOCK")):
            pos = (berlin_pos + i) % period
            key_char = KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(ct) - KRYPTOS_ALPHA.index(pt)) % 26]

            if pos in bc_key_constraints:
                if bc_key_constraints[pos] != key_char:
                    valid = False
                    break
            else:
                bc_key_constraints[pos] = key_char

        if not valid:
            continue

        # Now try all possible NORTHEAST positions
        for ne_pos in range(len(K4) - 9):
            # Skip if overlaps with BERLINCLOCK
            if ne_pos <= berlin_pos + 10 and ne_pos + 9 > berlin_pos:
                continue

            # Check if NORTHEAST is compatible
            ne_ct = K4[ne_pos:ne_pos + 9]
            all_constraints = dict(bc_key_constraints)
            ne_valid = True

            for i, (ct, pt) in enumerate(zip(ne_ct, "NORTHEAST")):
                pos = (ne_pos + i) % period
                key_char = KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(ct) - KRYPTOS_ALPHA.index(pt)) % 26]

                if pos in all_constraints:
                    if all_constraints[pos] != key_char:
                        ne_valid = False
                        break
                else:
                    all_constraints[pos] = key_char

            if not ne_valid:
                continue

            # Check if we have a complete key
            missing = [i for i in range(period) if i not in all_constraints]

            if len(missing) <= 2:
                # Build the key
                key = ['?'] * period
                for pos, char in all_constraints.items():
                    key[pos] = char
                key_str = ''.join(key)

                # If complete, decrypt and verify
                if '?' not in key_str:
                    pt = decrypt(K4, key_str, KRYPTOS_ALPHA)

                    if 'BERLINCLOCK' in pt and 'NORTHEAST' in pt:
                        print(f"\n*** FOUND SOLUTION! ***")
                        print(f"Period: {period}")
                        print(f"Key: {key_str}")
                        print(f"BERLIN at: {pt.find('BERLIN')}")
                        print(f"NORTHEAST at: {pt.find('NORTHEAST')}")
                        print(f"Plaintext: {pt}")
                        found_solutions.append((key_str, pt, period))

                elif len(missing) <= 2:
                    # Brute force remaining
                    for combo in itertools.product(KRYPTOS_ALPHA[:6], repeat=len(missing)):
                        test_key = list(key)
                        for j, pos in enumerate(missing):
                            test_key[pos] = combo[j]
                        test_key_str = ''.join(test_key)

                        pt = decrypt(K4, test_key_str, KRYPTOS_ALPHA)

                        if 'BERLINCLOCK' in pt and 'NORTHEAST' in pt:
                            print(f"\n*** FOUND SOLUTION! ***")
                            print(f"Period: {period}")
                            print(f"Key: {test_key_str}")
                            print(f"Plaintext: {pt}")
                            found_solutions.append((test_key_str, pt, period))

if not found_solutions:
    print("\nNo solution found with adjacent BERLINCLOCK and NORTHEAST.")
    print("Trying with BERLIN and CLOCK in various positions...")

    # Try any configuration where all three words appear
    best_score = 0
    best_result = None

    for period in range(11, 15):
        print(f"\nTrying period {period}...")

        # Generate keys that produce BERLINCLOCK at various positions
        for bc_start in range(len(K4) - 10):
            bc_ct = K4[bc_start:bc_start+11]

            # Check if BERLINCLOCK fits with this period
            key_constraints = {}
            valid = True

            for i, (ct, pt) in enumerate(zip(bc_ct, "BERLINCLOCK")):
                pos = (bc_start + i) % period
                key_char = KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(ct) - KRYPTOS_ALPHA.index(pt)) % 26]

                if pos in key_constraints and key_constraints[pos] != key_char:
                    valid = False
                    break
                key_constraints[pos] = key_char

            if not valid:
                continue

            # Build partial key
            key = ['K'] * period  # Default to K
            for pos, char in key_constraints.items():
                key[pos] = char

            # Decrypt
            pt = decrypt(K4, ''.join(key), KRYPTOS_ALPHA)

            # Check for words
            if 'BERLINCLOCK' in pt:
                if 'NORTHEAST' in pt:
                    print(f"FOUND! BC@{bc_start}, Key={''.join(key)}")
                    print(f"  {pt}")
                elif 'NORTH' in pt or 'EAST' in pt:
                    print(f"Partial: BC@{bc_start}, has NORTH or EAST")
                    print(f"  {pt[:60]}...")

print("\n" + "="*70)
print("SEARCH COMPLETE")
print("="*70)

if found_solutions:
    print(f"\nFound {len(found_solutions)} solution(s)!")
    for key, pt, period in found_solutions:
        print(f"\nKey (period {period}): {key}")
        print(f"Plaintext: {pt}")
else:
    print("\nNo complete solution found.")
    print("K4 likely uses a non-standard cipher that requires further analysis.")
