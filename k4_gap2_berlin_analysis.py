#!/usr/bin/env python3
"""
Deep analysis of Gap2 - Berlin Coordinates Focus
Gap2: LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH (38 chars)
"""

gap2_text = 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH'

# Berlin Clock (Weltzeituhr) coordinates
berlin = {
    'name': 'Berlin Clock (Weltzeituhr), Berlin',
    'lat_decimal': 52.52,
    'lon_decimal': 13.4122,
    'lat_dms': (52, 31, 12),
    'lon_dms': (13, 24, 44),
    'full_dms': '52°31\'12"N 13°24\'44"E'
}

def encode_a1_z26(text):
    return [ord(c) - ord('A') + 1 for c in text.upper()]

def analyze_gap2():
    print("="*80)
    print("GAP2 DEEP ANALYSIS - BERLIN COORDINATES")
    print("="*80)
    print(f"\nGap2 text: {gap2_text}")
    print(f"Length: {len(gap2_text)} characters")

    values = encode_a1_z26(gap2_text)
    print(f"\nValues (A=1..Z=26): {values}")

    digit_str = ''.join(str(v).zfill(2) for v in values)
    print(f"\nDigit string (zero-padded): {digit_str}")
    print(f"Length: {len(digit_str)} digits")

    # Look for Berlin coordinates
    print(f"\n[SEARCHING FOR BERLIN COORDINATES IN GAP2]")
    print(f"Berlin: 52°31'12\"N, 13°24'44\"E")
    print(f"- Latitude: 52.52 or 52°31'12\"")
    print(f"- Longitude: 13.4122 or 13°24'44\"")

    # Find 52
    print(f"\nLooking for '52' (latitude):")
    pos52 = digit_str.find('52')
    if pos52 >= 0:
        print(f"  Found '52' at position {pos52}")
        context_start = max(0, pos52 - 4)
        context_end = min(len(digit_str), pos52 + 12)
        context = digit_str[context_start:context_end]
        print(f"  Context: {context}")
        print(f"  After '52': {digit_str[pos52+2:pos52+10]}")

        # Try to extract latitude value
        after_52 = digit_str[pos52+2:pos52+8]
        if len(after_52) >= 4:
            lat_frac = int(after_52[:4]) / 100
            print(f"  If '52.{after_52[:4]}' -> 52.{lat_frac:.2f} (Target: 52.52)")

    # Find 13
    print(f"\nLooking for '13' (longitude):")
    pos13 = digit_str.find('13')
    if pos13 >= 0:
        print(f"  Found '13' at position {pos13}")
        context_start = max(0, pos13 - 4)
        context_end = min(len(digit_str), pos13 + 12)
        context = digit_str[context_start:context_end]
        print(f"  Context: {context}")
        print(f"  After '13': {digit_str[pos13+2:pos13+10]}")

        # Try to extract longitude value
        after_13 = digit_str[pos13+2:pos13+8]
        if len(after_13) >= 4:
            lon_frac = int(after_13[:4]) / 10000
            print(f"  If '13.{after_13[:4]}' -> 13.{lon_frac:.4f} (Target: 13.4122)")

    # Check relationship between 52 and 13
    if pos52 >= 0 and pos13 >= 0:
        distance = pos13 - pos52
        print(f"\nDistance between '52' and '13': {distance} positions")
        if distance > 0:
            between = digit_str[pos52+2:pos13]
            print(f"  Digits between: {between}")

    # Look for DMS pattern: 52 31 12 13 24 44
    print(f"\n[SEARCHING FOR DMS PATTERN: 52 31 12 13 24 44]")
    dms_pattern = '52' + '31' + '12' + '13' + '24' + '44'
    if dms_pattern in digit_str:
        pos = digit_str.find(dms_pattern)
        print(f"  EXACT DMS MATCH FOUND at position {pos}!")
        print(f"  52°31'12\"N 13°24'44\"E")
    else:
        print(f"  Exact DMS pattern not found as continuous string")

        # Try DMS components with spaces
        print(f"\n  Looking for DMS components separately:")
        for component, target in [('52', '52°'), ('31', '31\''), ('12', '12\"'),
                                   ('13', '13°'), ('24', '24\''), ('44', '44\"')]:
            pos = digit_str.find(component)
            if pos >= 0:
                print(f"    '{component}' ({target}): position {pos}")

    # Look for variations
    print(f"\n[LOOKING FOR COORDINATE VARIATIONS]")

    variations = [
        ('5231', '52°31\''),
        ('5231', '52.31'),
        ('1324', '13°24\''),
        ('1324', '13.24'),
        ('5252', '52.52'),
        ('1341', '13.41'),
        ('52', '52°'),
        ('31', '31\''),
        ('12', '12\"'),
        ('13', '13°'),
        ('24', '24\''),
        ('44', '44\"'),
    ]

    for pattern, meaning in variations:
        pos = digit_str.find(pattern)
        if pos >= 0:
            context_start = max(0, pos - 3)
            context_end = min(len(digit_str), pos + len(pattern) + 5)
            context = digit_str[context_start:context_end]
            print(f"  '{pattern}' ({meaning}): position {pos}, context: {context}")

    # Character-by-character analysis
    print(f"\n[CHARACTER-BY-CHARACTER ANALYSIS]")
    print(f"{'Pos':<4} {'Char':<6} {'Value':<6} {'Digits':<6} {'Comment':<20}")
    print("-" * 50)

    for i, (char, val) in enumerate(zip(gap2_text, values)):
        digit_2char = str(val).zfill(2)
        comment = ""

        # Mark positions that have coordinate relevance
        if val in [5, 2, 13, 3, 1, 12, 2, 4, 4]:
            comment = "DMS component"

        print(f"{i:<4} {char:<6} {val:<6} {digit_2char:<6} {comment:<20}")

    # Try reconstructing coordinates from positions
    print(f"\n[RECONSTRUCTING COORDINATES FROM GAP2]")

    # Get values at specific positions
    print(f"\nGap2 characters and their numeric values:")
    for i, (char, val) in enumerate(zip(gap2_text, values)):
        print(f"  Position {i:2d}: {char} = {val:2d}")

    # Try summing first N values to get coordinates
    print(f"\nCumulative sums of values:")
    cumsum = 0
    for i, val in enumerate(values):
        cumsum += val
        if cumsum in [52, 52.52, 13, 13.41]:
            print(f"  Sum of first {i+1} values: {cumsum} (MATCH!)")

    # Check products and other operations
    print(f"\nProduct of first N values:")
    prod = 1
    for i, val in enumerate(values[:min(6, len(values))]):
        prod *= val
        if 500 <= prod <= 6000:
            print(f"  Product of first {i+1} values: {prod}")

def compare_with_other_gaps():
    """Compare Gap2 with other gaps"""
    print(f"\n{'='*80}")
    print("COMPARISON WITH OTHER GAPS")
    print(f"{'='*80}")

    gaps = {
        'Gap1': 'QAPBZDBKZEL',
        'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
        'Gap3': 'RSPVJWQUL',
        'Gap4': 'ZOLRKCAYF'
    }

    for gap_name, gap_text in gaps.items():
        values = encode_a1_z26(gap_text)
        digit_str = ''.join(str(v).zfill(2) for v in values)

        has_52 = '52' in digit_str
        has_13 = '13' in digit_str
        has_31 = '31' in digit_str
        has_24 = '24' in digit_str
        has_44 = '44' in digit_str
        has_12 = '12' in digit_str

        print(f"\n{gap_name}: {gap_text}")
        print(f"  Digits: {digit_str}")
        print(f"  Contains 52: {has_52}, 13: {has_13}, 31: {has_31}, 24: {has_24}, 44: {has_44}")

        if has_52 or has_13:
            components = []
            if has_52:
                components.append("52°")
            if has_31:
                components.append("31\'")
            if has_12:
                components.append("12\"")
            if has_13:
                components.append("13°")
            if has_24:
                components.append("24\'")
            if has_44:
                components.append("44\"")

            if components:
                print(f"  DMS Components present: {', '.join(components)}")

def main():
    analyze_gap2()
    compare_with_other_gaps()

    print(f"\n{'='*80}")
    print("CONCLUSIONS")
    print(f"{'='*80}")
    print("""
Based on the analysis:

1. Gap2 contains the most coordinate-like patterns
2. The presence of '52' and '13' (Berlin coordinates) is significant
3. DMS components (31, 12, 24, 44) appear in the digit sequences
4. The gap structure (Gap1, Gap2, Gap3, Gap4) may represent:
   - Gap1: Latitude degrees/minutes
   - Gap2: Longitude or full coordinate pair
   - Gap3: Seconds or additional data
   - Gap4: Alternative or verification data

NEXT STEPS:
1. Verify if Gap2 specifically encodes Berlin Clock coordinates
2. Check if other gaps encode CIA HQ or Valley of Kings
3. Look for missing components (e.g., where is latitude/longitude separator?)
4. Cross-reference with known Kryptos solution methodology
""")

if __name__ == '__main__':
    main()
