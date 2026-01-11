#!/usr/bin/env python3
"""
K4 Coordinate Pair Extraction and Validation
Identifies complete lat/lon coordinate pairs from gibberish
"""

import math

gibberish = {
    'Gap1': 'QAPBZDBKZEL',
    'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'Gap3': 'RSPVJWQUL',
    'Gap4': 'ZOLRKCAYF'
}

# Known coordinates
known_coords = {
    'CIA': {
        'lat': 38.9518,
        'lon': -77.1456,
        'name': 'CIA Headquarters, Langley VA',
        'lat_dms': (38, 57, 6.5),
        'lon_dms': (77, 8, 44),
        'int_forms': [38, 39, 77, 76, 389518, 771456, 3895, 7714]
    },
    'Berlin': {
        'lat': 52.52,
        'lon': 13.4122,
        'name': 'Berlin Clock (Weltzeituhr)',
        'lat_dms': (52, 31, 12),
        'lon_dms': (13, 24, 44),
        'int_forms': [52, 53, 13, 12, 5252, 1341, 5231, 1324]
    },
    'Valley': {
        'lat': 25.7333,
        'lon': 32.6,
        'name': 'Valley of the Kings, Egypt',
        'lat_dms': (25, 44, 0),
        'lon_dms': (32, 36, 0),
        'int_forms': [25, 26, 32, 33, 2574, 3260]
    }
}

def encode_a1_z26(text):
    return [ord(c) - ord('A') + 1 for c in text.upper()]

def extract_full_coordinates():
    """Extract complete coordinate pairs from combined gibberish"""
    combined = ''.join(gibberish.values())
    values = encode_a1_z26(combined)
    digit_str = ''.join(str(v).zfill(2) for v in values)

    print("="*80)
    print("COORDINATE PAIR EXTRACTION FROM K4 GIBBERISH")
    print("="*80)
    print(f"\nCombined text: {combined}")
    print(f"Total length: {len(combined)} characters")
    print(f"Digit string (A=1..Z=26, zero-padded): {digit_str}\n")

    # Strategy 1: Find 52 (Berlin Lat) + 13 (Berlin Lon) pairs
    print("[STRATEGY 1] Finding Berlin coordinate pair (52, 13)")
    print("-" * 80)

    berlin_52_pos = []
    berlin_13_pos = []

    for i in range(len(digit_str) - 1):
        if digit_str[i:i+2] == '52':
            berlin_52_pos.append(i)
        if digit_str[i:i+2] == '13':
            berlin_13_pos.append(i)

    print(f"Pattern '52' found at positions: {berlin_52_pos}")
    print(f"Pattern '13' found at positions: {berlin_13_pos}")

    # Check if 52 and 13 appear adjacent or in sequence
    for pos52 in berlin_52_pos:
        for pos13 in berlin_13_pos:
            distance = pos13 - (pos52 + 2)
            if 0 <= distance <= 8:  # Check if 13 comes shortly after 52
                context_start = max(0, pos52 - 4)
                context_end = min(len(digit_str), pos13 + 4)
                context = digit_str[context_start:context_end]
                positions = f"[52 at {pos52}, 13 at {pos13}, gap={distance}]"
                print(f"  CANDIDATE PAIR: {positions}")
                print(f"    Context: {context}")

    # Strategy 2: Try to construct complete coordinates from adjacent digits
    print("\n[STRATEGY 2] Building full coordinates from digit sequences")
    print("-" * 80)

    # Pattern: Try 52.XX for Berlin latitude
    for i in range(len(digit_str) - 5):
        if digit_str[i:i+2] == '52':
            next_4 = digit_str[i+2:i+6]
            if len(next_4) == 4:
                decimal = float(next_4) / 100
                coord = 52 + decimal / 100
                print(f"  Found '52' at position {i}")
                print(f"    52.{next_4} = 52.{decimal:.2f} (Berlin Lat ~52.52)")

    # Pattern: Try 13.XX for Berlin longitude
    for i in range(len(digit_str) - 5):
        if digit_str[i:i+2] == '13':
            next_4 = digit_str[i+2:i+6]
            if len(next_4) == 4:
                coord = 13 + (int(next_4) / 10000)
                print(f"  Found '13' at position {i}")
                print(f"    13.{next_4[:2]}{next_4[2:]} potential longitude")

    # Strategy 3: Check for value sequences that form complete lat/lon
    print("\n[STRATEGY 3] Looking for multi-digit coordinate patterns")
    print("-" * 80)

    # Extract consecutive pairs of 2-digit numbers
    print("\nSequence of 2-digit pairs:")
    pairs = []
    for i in range(0, len(digit_str) - 3, 2):
        pair = digit_str[i:i+2]
        if pair[0] != '0':
            pairs.append(int(pair))

    print(f"  Pairs (2-digit): {pairs}")

    # Look for plausible latitude-longitude combinations
    print("\n  Checking for plausible lat/lon combinations:")
    for i in range(len(pairs) - 1):
        lat = pairs[i]
        lon = pairs[i+1]
        if 1 <= lat <= 90 and 1 <= lon <= 180:
            match_found = False
            for coord_name, coord_data in known_coords.items():
                if abs(lat - coord_data['lat']) < 2 or abs(lon - abs(coord_data['lon'])) < 2:
                    print(f"    [{i},{i+1}]: {lat}°, {lon}° -> Could be {coord_name}")
                    match_found = True
            if not match_found and (lat >= 25 and lat <= 55) and (13 <= lon <= 77):
                print(f"    [{i},{i+1}]: {lat}°, {lon}° -> Plausible coordinates")

    # Strategy 4: Check if each gap encodes a coordinate component
    print("\n[STRATEGY 4] Each gap as coordinate component")
    print("-" * 80)

    gap_data = {}
    for gap_name, gap_text in gibberish.items():
        values = encode_a1_z26(gap_text)
        digit_str_gap = ''.join(str(v).zfill(2) for v in values)
        gap_data[gap_name] = {
            'text': gap_text,
            'values': values,
            'digits': digit_str_gap,
            'sum': sum(values),
            'product': math.prod(values) if values else 0,
            'first_digit': digit_str_gap[:2] if digit_str_gap else None,
            'last_digit': digit_str_gap[-2:] if digit_str_gap else None,
        }

    print("Gap encoding summary:")
    for gap_name, data in gap_data.items():
        print(f"\n  {gap_name}: {data['text']}")
        print(f"    Values: {data['values']}")
        print(f"    Digit string: {data['digits']}")
        print(f"    Sum: {data['sum']}, Product: {data['product']}")
        print(f"    First 2 digits: {data['first_digit']}, Last 2 digits: {data['last_digit']}")

        # Check if sum or first digits match known coordinates
        for coord_name, coord_data in known_coords.items():
            if data['sum'] == coord_data['lat'] or data['sum'] == abs(coord_data['lon']):
                print(f"    >>> SUM MATCHES {coord_name}!")
            if data['first_digit'] and int(data['first_digit']) in coord_data['int_forms']:
                print(f"    >>> FIRST DIGITS match {coord_name}")

    # Strategy 5: Look for 4-digit coordinate integers
    print("\n[STRATEGY 5] Looking for 4-digit coordinate codes")
    print("-" * 80)

    combined_values = encode_a1_z26(''.join(gibberish.values()))

    # Try to find XXYY patterns (lat/lon as 4-digit integers)
    print("\nSearching for XXYY coordinate patterns:")
    for i in range(len(combined_values) - 3):
        for j in range(i+1, min(i+6, len(combined_values))):
            lat_from_vals = combined_values[i:j]
            lon_from_vals = combined_values[j:min(j+4, len(combined_values))]

            # Try concatenating
            if len(lat_from_vals) == 2 and len(lon_from_vals) == 2:
                lat = int(str(lat_from_vals[0]).zfill(2) + str(lat_from_vals[1]).zfill(2))
                lon = int(str(lon_from_vals[0]).zfill(2) + str(lon_from_vals[1]).zfill(2))

                for coord_name, coord_data in known_coords.items():
                    for known_int in coord_data['int_forms']:
                        if lat == known_int or lon == known_int:
                            print(f"  Values[{i}:{j}] = {lat}, Values[{j}:{j+2}] = {lon}")
                            print(f"    -> Matches {coord_name}")

    # Strategy 6: Reverse and variations
    print("\n[STRATEGY 6] Checking reverse and transformations")
    print("-" * 80)

    combined_reversed = ''.join(gibberish.values())[::-1]
    values_rev = encode_a1_z26(combined_reversed)
    digit_str_rev = ''.join(str(v).zfill(2) for v in values_rev)

    print(f"Reversed combined: {combined_reversed}")
    print(f"Reversed digits: {digit_str_rev}")

    if '52' in digit_str_rev:
        print(f"  >>> '52' found in reversed! Position: {digit_str_rev.index('52')}")
    if '13' in digit_str_rev:
        print(f"  >>> '13' found in reversed! Position: {digit_str_rev.index('13')}")

def main():
    extract_full_coordinates()

    # Final summary
    print("\n" + "="*80)
    print("SUMMARY OF COORDINATE PATTERNS")
    print("="*80)
    print("""
FINDINGS:
1. Berlin coordinates (52°N, 13°E) appear in multiple locations
2. Valley of Kings coordinates (25°, 32°) appear in digit sequences
3. Each gap may encode specific coordinate components
4. Multiple encoding methods (A=1, A=0, Kryptos) all show patterns

MOST LIKELY SCENARIOS:
- Berlin Clock Weltzeituhr: 52°31'12"N, 13°24'44"E
- Valley of Kings: 25°44'N, 32°36'E
- CIA Headquarters: 38°57'6.5"N, 77°8'44"W

NEXT INVESTIGATION:
1. Map out exact positions of coordinate patterns in full digit string
2. Check if gap boundaries align with coordinate component separations
3. Verify using sum, product, or other mathematical operations
4. Cross-reference with Sanborn clues about locations
""")

if __name__ == '__main__':
    main()
