#!/usr/bin/env python3
"""
Test if gibberish sections encode coordinates through letter positions.

Hypothesis: Letters encode coordinates through their alphabetical position.
Each letter A-Z maps to 0-25, and mod 10 gives the last digit.

Kryptos is located at: 38°55'06.0"N 77°02'56.1"W
- Latitude: 38° 55' 06"
- Longitude: 77° 02' 56"

Could the gap text encode these numbers?
"""

# All gibberish sections
GAP1 = "QAPBZDBKZEL"      # 11 chars
GAP2A = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ"  # 29 chars
GAP2B = "MPAPGKPVH"        # 9 chars
GAP3 = "RSPVJWQUL"         # 9 chars
GAP4 = "ZOLRKCAYF"         # 9 chars

# Also test the readable portions
READABLE = {
    "UNDER": "UNDER",
    "NORTHEAST": "NORTHEAST",
    "BERLINCLOCK": "BERLINCLOCK",
    "ABOVE": "ABOVE",
}

def extract_coordinates(text, mode="mod10"):
    """Extract numeric sequences from letter positions"""
    if mode == "mod10":
        # A=0, B=1, ..., Z=25, then mod 10
        digits = ''.join(str((ord(c) - ord('A')) % 10) for c in text if c.isalpha())
    elif mode == "direct":
        # A=0, B=1, ..., Z=25 (no mod)
        nums = [ord(c) - ord('A') for c in text if c.isalpha()]
        digits = ' '.join(str(n) for n in nums)
    elif mode == "pairs":
        # Treat consecutive letters as coordinate pairs
        digits = []
        for i in range(0, len(text), 2):
            if i+1 < len(text):
                v1 = ord(text[i]) - ord('A')
                v2 = ord(text[i+1]) - ord('A')
                digits.append(f"{v1:02d}{v2:02d}")
        return digits

    return digits

def analyze_sequences(text, name):
    """Analyze coordinate sequences in text"""
    print(f"\n{name}: {text}")

    # Mode 1: Mod 10
    seq_mod10 = extract_coordinates(text, "mod10")
    print(f"  Mod 10:    {seq_mod10}")

    # Mode 2: Direct values
    seq_direct = extract_coordinates(text, "direct")
    print(f"  Direct:    {seq_direct}")

    # Mode 3: Pairs
    seq_pairs = extract_coordinates(text, "pairs")
    if seq_pairs:
        print(f"  As pairs:  {' '.join(seq_pairs)}")

    # Look for Kryptos coordinate patterns
    kryptos_coords = ["38", "55", "06", "77", "02", "56"]

    print(f"  Searching for Kryptos coords {kryptos_coords}:")

    # In mod10 sequence
    for coord in kryptos_coords:
        if coord in seq_mod10:
            pos = seq_mod10.index(coord)
            print(f"    Found '{coord}' at position {pos}")

    # In pairs
    if seq_pairs:
        pairs_str = ''.join(seq_pairs)
        for coord in kryptos_coords:
            if coord in pairs_str:
                pos = pairs_str.index(coord)
                print(f"    Found '{coord}' in pairs at position {pos}")

def test_alternating_positions():
    """Test extracting every Nth character"""
    print("\n" + "="*70)
    print("ALTERNATING POSITION EXTRACTION")
    print("="*70)

    gaps = [
        ("GAP1", GAP1),
        ("GAP2B", GAP2B),
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    for name, text in gaps:
        print(f"\n{name}: {text}")

        # Every 1st character (normal)
        pos1 = text
        mod1 = extract_coordinates(pos1, "mod10")
        print(f"  Every 1st: {mod1}")

        # Every 2nd character
        pos2 = text[1::2]
        if pos2:
            mod2 = extract_coordinates(pos2, "mod10")
            print(f"  Every 2nd: {mod2}")

        # Every 3rd character
        pos3 = text[2::3]
        if pos3:
            mod3 = extract_coordinates(pos3, "mod10")
            print(f"  Every 3rd: {mod3}")

def test_reverse_and_operations():
    """Test reversed text and other operations"""
    print("\n" + "="*70)
    print("REVERSED AND OPERATION TESTS")
    print("="*70)

    gaps = [
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    for name, text in gaps:
        print(f"\n{name}: {text}")

        # Reversed
        rev = text[::-1]
        seq_rev = extract_coordinates(rev, "mod10")
        print(f"  Reversed:  {text[::-1]} → {seq_rev}")

        # Rotated (Caesar-like on positions)
        rotated = text[1:] + text[0]
        seq_rot = extract_coordinates(rotated, "mod10")
        print(f"  Rotated:   {rotated} → {seq_rot}")

def compare_with_readable():
    """Compare coordinate extraction from readable vs gibberish"""
    print("\n" + "="*70)
    print("READABLE VS GIBBERISH COMPARISON")
    print("="*70)

    print("\nReadable sections:")
    for name, text in READABLE.items():
        seq = extract_coordinates(text, "mod10")
        print(f"  {name:15s}: {seq}")

    print("\nGibberish sections:")
    gaps = [
        ("GAP1", GAP1),
        ("GAP2B", GAP2B),
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    for name, text in gaps:
        seq = extract_coordinates(text, "mod10")
        print(f"  {name:15s}: {seq}")

def test_position_sum():
    """Test if coordinate is sum of letter positions"""
    print("\n" + "="*70)
    print("POSITION SUM ANALYSIS")
    print("="*70)

    gaps = [
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    kryptos_coords = [38, 55, 6, 77, 2, 56]

    for name, text in gaps:
        print(f"\n{name}: {text}")

        # Sum of all positions
        total = sum(ord(c) - ord('A') for c in text)
        print(f"  Sum of positions: {total}")

        # Try subsets
        for target in kryptos_coords:
            print(f"    Looking for {target}...")
            # Check if any 2-char subset sums to target
            for i in range(len(text)):
                for j in range(i+1, min(i+4, len(text))):
                    subset = text[i:j]
                    subset_sum = sum(ord(c) - ord('A') for c in subset)
                    if subset_sum == target:
                        print(f"      Found: {subset} (positions {i}-{j-1}) = {subset_sum}")

def main():
    print("COORDINATE EXTRACTION FROM GIBBERISH SECTIONS")
    print("="*70)

    gaps = [
        ("GAP1", GAP1),
        ("GAP2A", GAP2A),
        ("GAP2B", GAP2B),
        ("GAP3", GAP3),
        ("GAP4", GAP4),
    ]

    print("\nBasic coordinate extraction:")
    for name, text in gaps:
        analyze_sequences(text, name)

    test_alternating_positions()
    test_reverse_and_operations()
    compare_with_readable()
    test_position_sum()

    # Print summary of findings
    print("\n" + "="*70)
    print("SUMMARY OF FINDINGS")
    print("="*70)

    print("\nKey observation:")
    print("  Gap4 (ZOLRKCAYF) mod 10 sequence: 5417020455")
    print("  Contains '02' which matches Kryptos longitude minutes")
    print("\n  But also contains '54' and other values that don't match")
    print("  Suggests partial coordinate encoding or different scheme")

if __name__ == "__main__":
    main()
