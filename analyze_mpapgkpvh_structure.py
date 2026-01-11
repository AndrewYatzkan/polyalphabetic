#!/usr/bin/env python3
"""
Deep analysis of MPAPGKPVH and its relationships to:
1. K4 ciphertext
2. Period 29 key
3. K4 plaintext structure
4. Other anomalies in the gibberish
"""

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# K4 data
k4_ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
k4_plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
period29_key = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# The mysterious key candidates
mpapgkpvh = "MPAPGKPVH"
aeplz = "AEPLZ"

def char_to_num(c, alphabet=STANDARD_ALPHA):
    """Convert character to position"""
    return alphabet.index(c.upper())

def num_to_char(n, alphabet=STANDARD_ALPHA):
    """Convert position to character"""
    return alphabet[n % len(alphabet)]

def analyze_positions(text, substring):
    """Find all positions of substring"""
    positions = []
    for i in range(len(text) - len(substring) + 1):
        if text[i:i+len(substring)] == substring:
            positions.append(i)
    return positions

def extract_substring_relationships(ciphertext, plaintext, key, start, end):
    """Extract key relationships for a given text segment"""
    relationships = []
    key_index = start

    for i in range(start, min(end, len(ciphertext))):
        ct_char = ciphertext[i]
        pt_char = plaintext[i]

        ct_pos = char_to_num(ct_char)
        pt_pos = char_to_num(pt_char)
        key_char = key[key_index % len(key)]
        key_pos = char_to_num(key_char)

        relationships.append({
            'position': i,
            'key_index': key_index % len(key),
            'ciphertext': ct_char,
            'plaintext': pt_char,
            'key_char': key_char,
            'key_pos': key_pos,
            'key_cycle': key_index // len(key)
        })

        key_index += 1

    return relationships

def main():
    print("\n" + "="*80)
    print("ANALYSIS OF MPAPGKPVH AND K4 STRUCTURE")
    print("="*80)

    # Section positions in K4 plaintext
    print("\n1. LOCATIONS IN K4 PLAINTEXT")
    print("="*80 + "\n")

    print(f"K4 plaintext ({len(k4_plaintext)} chars):")
    print(f"{k4_plaintext}\n")

    print("Key words/sections:")
    print(f"  Pos 0-4:      UNDER")
    print(f"  Pos 5-15:     QAPBZDBKZEL (Gap1)")
    print(f"  Pos 16-24:    NORTHEAST")
    print(f"  Pos 25-62:    LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH (Gap2 = 29 + 9 chars)")
    print(f"  Pos 63-73:    BERLINCLOCK")
    print(f"  Pos 74-82:    RSPVJWQUL (Gap3)")
    print(f"  Pos 83-87:    ABOVE")
    print(f"  Pos 88-96:    ZOLRKCAYF (Gap4)")

    print(f"\nMPAPGKPVH location: Pos 53-61 (part of Gap2)")
    print(f"  MPAPGKPVH appears at index {k4_plaintext.find('MPAPGKPVH')} in plaintext")

    # Look in ciphertext
    print(f"\n2. LOOKING FOR MPAPGKPVH IN K4 CIPHERTEXT")
    print("="*80 + "\n")

    mpapgkpvh_in_ct = analyze_positions(k4_ciphertext, mpapgkpvh)
    if mpapgkpvh_in_ct:
        print(f"MPAPGKPVH found in ciphertext at positions: {mpapgkpvh_in_ct}")
    else:
        print(f"MPAPGKPVH NOT found in ciphertext\n")

    # Now check if the 9 chars of MPAPGKPVH are scattered in ciphertext
    print(f"\nSearching for individual characters of MPAPGKPVH in ciphertext:")
    for char in mpapgkpvh:
        positions = analyze_positions(k4_ciphertext, char)
        print(f"  {char}: appears at {len(positions)} position(s) - {positions[:5]}{'...' if len(positions) > 5 else ''}")

    # Analyze the Period 29 key
    print(f"\n3. PERIOD 29 KEY STRUCTURE")
    print("="*80 + "\n")

    print(f"Period 29 key: {period29_key}")
    print(f"Key length: {len(period29_key)}")

    # Split the key into the discovered segments
    print(f"\nKey segments:")
    print(f"  Pos 0-4:   {period29_key[0:5]}   (for UNDER)")
    print(f"  Pos 5-15:  {period29_key[5:16]}  (for NORTHEAST start)")
    print(f"  Pos 16-28: {period29_key[16:29]} (for BERLINCLOCK start)")
    print(f"  Repeating: {period29_key[5:14]} + {period29_key[0:7]} ...")

    # Check: does MPAPGKPVH appear in the key?
    mpapgkpvh_in_key = analyze_positions(period29_key, mpapgkpvh)
    if mpapgkpvh_in_key:
        print(f"\nMPAPGKPVH found in key at positions: {mpapgkpvh_in_key}")
    else:
        print(f"\nMPAPGKPVH NOT found directly in Period 29 key")

    # Check components
    print(f"\nSearching for components of MPAPGKPVH in key:")
    for component in ['MP', 'PA', 'AP', 'PG', 'GK', 'KP', 'PV', 'VH']:
        positions = analyze_positions(period29_key, component)
        if positions:
            print(f"  {component}: found at positions {positions}")

    # Extract the actual encryption key used for MPAPGKPVH in the ciphertext
    print(f"\n4. ENCRYPTION KEY FOR MPAPGKPVH SECTION")
    print("="*80 + "\n")

    mpapgkpvh_start = k4_plaintext.find('MPAPGKPVH')
    mpapgkpvh_end = mpapgkpvh_start + len('MPAPGKPVH')

    print(f"MPAPGKPVH positions in K4: {mpapgkpvh_start}-{mpapgkpvh_end}")

    # Extract key for this section
    actual_key_used = ""
    key_index = mpapgkpvh_start

    for i in range(mpapgkpvh_start, mpapgkpvh_end):
        ct_char = k4_ciphertext[i]
        pt_char = k4_plaintext[i]

        ct_pos = char_to_num(ct_char)
        pt_pos = char_to_num(pt_char)

        key_pos = (ct_pos - pt_pos) % 26
        actual_key_used += num_to_char(key_pos)

    print(f"Plaintext:  {k4_plaintext[mpapgkpvh_start:mpapgkpvh_end]}")
    print(f"Ciphertext: {k4_ciphertext[mpapgkpvh_start:mpapgkpvh_end]}")
    print(f"Actual key: {actual_key_used}")

    # Compare with Period 29 cycling
    period29_at_this_position = ""
    key_index = mpapgkpvh_start
    for i in range(len('MPAPGKPVH')):
        period29_at_this_position += period29_key[key_index % len(period29_key)]
        key_index += 1

    print(f"Period29:   {period29_at_this_position}")

    # Are they the same?
    if actual_key_used == period29_at_this_position:
        print(f"✓ Keys match! MPAPGKPVH was encrypted with the Period 29 key cycling as expected.")
    else:
        print(f"✗ Keys DON'T match! This is ANOMALOUS!")
        print(f"   This suggests MPAPGKPVH might have been encrypted with a different method.")

    # Analyze all gap sections similarly
    print(f"\n5. KEY ANALYSIS FOR ALL GAP SECTIONS")
    print("="*80 + "\n")

    gap_positions = [
        ("Gap1", 5, 16),
        ("Gap2A", 25, 53),
        ("Gap2B (MPAPGKPVH)", 53, 62),
        ("Gap3", 74, 83),
        ("Gap4", 88, 97),
    ]

    for gap_name, start, end in gap_positions:
        print(f"{gap_name} (pos {start}-{end}):")
        plaintext_seg = k4_plaintext[start:end]
        ciphertext_seg = k4_ciphertext[start:end]

        # Extract actual key
        actual_key = ""
        for i in range(len(plaintext_seg)):
            ct_pos = char_to_num(ciphertext_seg[i])
            pt_pos = char_to_num(plaintext_seg[i])
            key_pos = (ct_pos - pt_pos) % 26
            actual_key += num_to_char(key_pos)

        # Compare with Period 29
        period29_seg = ""
        key_index = start
        for i in range(len(plaintext_seg)):
            period29_seg += period29_key[key_index % len(period29_key)]
            key_index += 1

        match = "✓" if actual_key == period29_seg else "✗"
        print(f"  {match} Actual: {actual_key}")
        print(f"    P29:    {period29_seg}")

        if actual_key != period29_seg:
            # Show differences
            diffs = []
            for i in range(len(actual_key)):
                if actual_key[i] != period29_seg[i]:
                    diffs.append(f"pos {i}: {actual_key[i]} vs {period29_seg[i]}")
            if diffs:
                print(f"    Differences: {diffs[:3]}")

        print()

    # Check if AEPLZ is related to any structure
    print(f"\n6. ANALYSIS OF AEPLZ (6×6 diagonal)")
    print("="*80 + "\n")

    print(f"AEPLZ: {aeplz}")
    print(f"In ciphertext: {analyze_positions(k4_ciphertext, aeplz)}")
    print(f"In plaintext: {analyze_positions(k4_plaintext, aeplz)}")
    print(f"In Period 29 key: {analyze_positions(period29_key, aeplz)}")

if __name__ == '__main__':
    main()
