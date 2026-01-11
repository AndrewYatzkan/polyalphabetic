#!/usr/bin/env python3
"""
Analyze the ACTUAL keys extracted from gap sections.
These keys differ from the Period 29 key, suggesting secondary encryption!

Extracted keys:
- Gap1: YXZFIRKRTKA (11 chars)
- Gap2A: FKVVLJHJNYNCUCYJLTNARNNJDERW (29 chars)
- Gap2B: MIOILQYYK (9 chars) - starts with M, like MPAPGKPVH!
- Gap3: FOOPQBDPR (9 chars)
- Gap4: IGPDUICCM (9 chars)
"""

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# The extracted actual keys (not Period 29)
actual_keys = {
    'Gap1': 'YXZFIRKRTKA',      # 11 chars
    'Gap2A': 'FKVVLJHJNYNCUCYJLTNARNNJDERW',  # 29 chars
    'Gap2B': 'MIOILQYYK',        # 9 chars
    'Gap3': 'FOOPQBDPR',         # 9 chars
    'Gap4': 'IGPDUICCM',         # 9 chars
}

def analyze_key_structure(key_name, key):
    """Analyze properties of a key"""
    print(f"\n{key_name}: {key} ({len(key)} chars)")
    print("="*60)

    # Character frequencies
    from collections import Counter
    freq = Counter(key)

    print(f"Unique chars: {len(freq)}/{len(key)}")
    print(f"Most common: {freq.most_common(3)}")

    # Look for patterns
    print(f"\nPatterns:")

    # Repeated pairs
    repeated_pairs = []
    for i in range(len(key) - 1):
        if key[i] == key[i+1]:
            repeated_pairs.append((i, key[i]))

    if repeated_pairs:
        print(f"  Repeated chars: {repeated_pairs}")

    # Alphabetic sequences
    sequences = []
    for i in range(len(key) - 1):
        c1_pos = ord(key[i]) - ord('A')
        c2_pos = ord(key[i+1]) - ord('A')
        if c2_pos == (c1_pos + 1) % 26:
            sequences.append(f"{key[i]}{key[i+1]}")

    if sequences:
        print(f"  Sequential pairs: {sequences}")

    # Reverse alphabetic
    reverse_sequences = []
    for i in range(len(key) - 1):
        c1_pos = ord(key[i]) - ord('A')
        c2_pos = ord(key[i+1]) - ord('A')
        if c1_pos == (c2_pos + 1) % 26:
            reverse_sequences.append(f"{key[i]}{key[i+1]}")

    if reverse_sequences:
        print(f"  Reverse sequential: {reverse_sequences}")

    # Differences from previous char
    diffs = []
    for i in range(len(key) - 1):
        c1_pos = ord(key[i]) - ord('A')
        c2_pos = ord(key[i+1]) - ord('A')
        diff = (c2_pos - c1_pos) % 26
        diffs.append(diff)

    if diffs:
        print(f"  Position differences: {diffs}")
        print(f"  Sum of diffs: {sum(diffs)}")
        print(f"  Avg diff: {sum(diffs)/len(diffs):.1f}")

def find_relationships(gap1_key, gap2a_key, gap2b_key, gap3_key, gap4_key):
    """Look for relationships between the keys"""
    print("\n" + "="*80)
    print("RELATIONSHIPS BETWEEN KEYS")
    print("="*80)

    # Check if any key is contained in another
    all_keys = {
        'Gap1': gap1_key,
        'Gap2A': gap2a_key,
        'Gap2B': gap2b_key,
        'Gap3': gap3_key,
        'Gap4': gap4_key,
    }

    print("\nLooking for key containment:")
    for key1_name, key1 in all_keys.items():
        for key2_name, key2 in all_keys.items():
            if key1_name != key2_name:
                if key1 in key2:
                    print(f"  {key1_name} ({key1}) found in {key2_name}")
                if key2 in key1:
                    print(f"  {key2_name} ({key2}) found in {key1_name}")

    # Check for XOR relationships
    print("\nXOR analysis (Gap1 XOR Gap3):")
    xor_result = ""
    for i in range(min(len(gap1_key), len(gap3_key))):
        c1_pos = ord(gap1_key[i]) - ord('A')
        c2_pos = ord(gap3_key[i]) - ord('A')
        xor_pos = c1_pos ^ c2_pos
        xor_result += chr(xor_pos + ord('A'))

    print(f"  Gap1 XOR Gap3: {xor_result}")

    # Check relationship to known candidates
    print(f"\nRelationship to MPAPGKPVH:")
    mpapgkpvh = "MPAPGKPVH"

    # Is MPAPGKPVH in any key?
    for key_name, key in all_keys.items():
        if mpapgkpvh in key:
            print(f"  MPAPGKPVH found in {key_name}")

    # Compare letter by letter
    if len(gap2b_key) == len(mpapgkpvh):
        print(f"\nGap2B vs MPAPGKPVH (same length: 9):")
        print(f"  Gap2B:      {gap2b_key}")
        print(f"  MPAPGKPVH:  {mpapgkpvh}")

        matches = sum(1 for i in range(len(gap2b_key)) if gap2b_key[i] == mpapgkpvh[i])
        print(f"  Matching positions: {matches}/9")

        # Show differences
        diffs = []
        for i in range(len(gap2b_key)):
            if gap2b_key[i] != mpapgkpvh[i]:
                g2_pos = ord(gap2b_key[i]) - ord('A')
                mp_pos = ord(mpapgkpvh[i]) - ord('A')
                diff = (mp_pos - g2_pos) % 26
                diffs.append(f"Pos {i}: {gap2b_key[i]}→{mpapgkpvh[i]} (diff: {diff})")

        if diffs:
            print(f"  Differences:")
            for d in diffs:
                print(f"    {d}")

    # Check if Gap2B could be derived from MPAPGKPVH with a simple transformation
    print(f"\nIs Gap2B a transformation of MPAPGKPVH?")

    # Rotation check
    for rotation in range(26):
        rotated = ""
        for c in mpapgkpvh:
            new_pos = (ord(c) - ord('A') + rotation) % 26
            rotated += chr(new_pos + ord('A'))

        if rotated == gap2b_key:
            print(f"  ✓ Gap2B = MPAPGKPVH rotated by {rotation}")
            break

def main():
    print("\n" + "="*80)
    print("ANALYSIS OF ACTUAL EXTRACTED KEYS FROM GAP SECTIONS")
    print("="*80)
    print("\nThese are the ACTUAL keys used to encrypt the gaps,")
    print("NOT the Period 29 key. This proves secondary encryption!")

    # Analyze each key
    for key_name, key in actual_keys.items():
        analyze_key_structure(key_name, key)

    # Look for relationships
    find_relationships(
        actual_keys['Gap1'],
        actual_keys['Gap2A'],
        actual_keys['Gap2B'],
        actual_keys['Gap3'],
        actual_keys['Gap4']
    )

    # Additional analysis
    print(f"\n" + "="*80)
    print("ENTROPY AND RANDOMNESS ANALYSIS")
    print("="*80 + "\n")

    from math import log

    for key_name, key in actual_keys.items():
        # Shannon entropy
        from collections import Counter
        freq = Counter(key)
        entropy = 0
        for count in freq.values():
            p = count / len(key)
            entropy -= p * log(p, 2)

        max_entropy = log(len(set(key)), 2)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

        print(f"{key_name:10} | Entropy: {entropy:.2f} | Normalized: {normalized_entropy:.2f}")

    print("\nNote: Higher entropy = more random")

if __name__ == '__main__':
    main()
