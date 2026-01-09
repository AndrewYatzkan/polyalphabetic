#!/usr/bin/env python3
"""
K4 Systematic Search

Try to find a cipher configuration where both:
1. BERLINCLOCK appears at position 63
2. NORTHEAST appears somewhere

This requires finding a key/method that satisfies both constraints.
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

def vigenere_decrypt_char(ct_char, key_char, alpha):
    ct_pos = alpha.index(ct_char)
    key_pos = alpha.index(key_char)
    return alpha[(ct_pos - key_pos) % len(alpha)]

def derive_key_char(ct_char, pt_char, alpha):
    ct_pos = alpha.index(ct_char)
    pt_pos = alpha.index(pt_char)
    return alpha[(ct_pos - pt_pos) % len(alpha)]

print("="*70)
print("K4 SYSTEMATIC CONSTRAINT SEARCH")
print("="*70)

# Known constraints
BERLIN_CLOCK = "BERLINCLOCK"
BC_START = 63  # 0-indexed start position

# For each possible NORTHEAST position, check compatibility
print("\nSearching for NORTHEAST positions compatible with BERLINCLOCK...")
print(f"BERLINCLOCK must be at positions {BC_START}-{BC_START+10}")
print()

NORTHEAST = "NORTHEAST"

compatible_found = []

for ne_pos in range(len(K4) - len(NORTHEAST) + 1):
    # Skip if NORTHEAST would overlap with BERLINCLOCK
    ne_end = ne_pos + len(NORTHEAST) - 1
    bc_end = BC_START + len(BERLIN_CLOCK) - 1

    # Check overlap
    if not (ne_end < BC_START or ne_pos > bc_end):
        # Overlapping - check if compatible
        overlap_compatible = True
        for i in range(len(NORTHEAST)):
            pos = ne_pos + i
            if BC_START <= pos <= bc_end:
                bc_idx = pos - BC_START
                if NORTHEAST[i] != BERLIN_CLOCK[bc_idx]:
                    overlap_compatible = False
                    break
        if not overlap_compatible:
            continue

    # For each period, check if the key constraints are compatible
    for period in range(5, 20):
        # Derive key constraints from BERLINCLOCK
        bc_key = {}
        for i, (ct, pt) in enumerate(zip(K4[BC_START:BC_START+11], BERLIN_CLOCK)):
            key_pos = (BC_START + i) % period
            key_char = derive_key_char(ct, pt, KRYPTOS_ALPHA)
            if key_pos in bc_key:
                if bc_key[key_pos] != key_char:
                    break  # Inconsistent
            else:
                bc_key[key_pos] = key_char
        else:
            # BERLINCLOCK constraints are consistent for this period
            # Now check NORTHEAST constraints

            ne_key = {}
            consistent = True
            for i, (ct, pt) in enumerate(zip(K4[ne_pos:ne_pos+9], NORTHEAST)):
                key_pos = (ne_pos + i) % period
                key_char = derive_key_char(ct, pt, KRYPTOS_ALPHA)

                if key_pos in ne_key:
                    if ne_key[key_pos] != key_char:
                        consistent = False
                        break
                else:
                    ne_key[key_pos] = key_char

                # Also check against BERLINCLOCK constraints
                if key_pos in bc_key:
                    if bc_key[key_pos] != key_char:
                        consistent = False
                        break

            if consistent:
                # Merge constraints
                all_key = {**bc_key, **ne_key}

                # Check if we have a complete key
                missing = [i for i in range(period) if i not in all_key]

                if len(missing) <= 3:
                    compatible_found.append({
                        'ne_pos': ne_pos,
                        'period': period,
                        'key': all_key,
                        'missing': missing
                    })

print(f"Found {len(compatible_found)} compatible configurations")

# Analyze the best candidates
best_candidates = sorted(compatible_found, key=lambda x: len(x['missing']))[:20]

for i, cand in enumerate(best_candidates):
    print(f"\n--- Candidate {i+1} ---")
    print(f"NORTHEAST at position {cand['ne_pos']}")
    print(f"Period: {cand['period']}")
    print(f"Missing key positions: {cand['missing']}")

    # Reconstruct key
    key = ['?'] * cand['period']
    for pos, char in cand['key'].items():
        key[pos] = char
    key_str = ''.join(key)
    print(f"Partial key: {key_str}")

    # If complete or nearly complete, try decrypting
    if len(cand['missing']) == 0:
        # Full decrypt
        pt = ''
        for i, c in enumerate(K4):
            key_char = key[i % cand['period']]
            pt += vigenere_decrypt_char(c, key_char, KRYPTOS_ALPHA)
        print(f"Plaintext: {pt}")

        # Verify
        print(f"  BERLINCLOCK at 63: {pt[63:74]} {'OK' if pt[63:74] == 'BERLINCLOCK' else 'FAIL'}")
        print(f"  NORTHEAST at {cand['ne_pos']}: {pt[cand['ne_pos']:cand['ne_pos']+9]}")

        # Count English-like patterns
        common = ['THE', 'AND', 'FOR', 'WAS', 'ARE', 'THAT', 'WITH', 'THIS',
                  'FROM', 'HAVE', 'NORTH', 'EAST', 'WEST', 'SOUTH']
        found_words = [w for w in common if w in pt]
        print(f"  English words found: {found_words}")

    elif len(cand['missing']) <= 2:
        # Try brute force
        print(f"  Brute forcing {len(cand['missing'])} positions...")
        best_score = 0
        best_pt = None
        best_full_key = None

        for combo in itertools.product(KRYPTOS_ALPHA[:8], repeat=len(cand['missing'])):
            test_key = list(key)
            for j, pos in enumerate(cand['missing']):
                test_key[pos] = combo[j]

            # Decrypt
            pt = ''
            for idx, c in enumerate(K4):
                key_char = test_key[idx % cand['period']]
                pt += vigenere_decrypt_char(c, key_char, KRYPTOS_ALPHA)

            # Verify constraints
            if pt[63:74] != 'BERLINCLOCK':
                continue
            if pt[cand['ne_pos']:cand['ne_pos']+9] != 'NORTHEAST':
                continue

            # Score
            common = ['THE', 'AND', 'FOR', 'YOU', 'WAS', 'ARE', 'BUT', 'NOT',
                      'ALL', 'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT']
            score = sum(1 for w in common if w in pt)

            if score > best_score:
                best_score = score
                best_pt = pt
                best_full_key = ''.join(test_key)

        if best_pt:
            print(f"  Best key: {best_full_key}")
            print(f"  Best plaintext: {best_pt}")
            print(f"  Score: {best_score}")

print("\n" + "="*70)
print("SEARCH COMPLETE")
print("="*70)
