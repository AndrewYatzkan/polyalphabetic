#!/usr/bin/env python3
"""
K4 Gibberish Coordinate Analysis
Analyzes K4 gibberish sections to find if they encode coordinates
Tests multiple encoding methods and looks for known coordinate patterns
"""

import re
from itertools import combinations
from collections import defaultdict

# K4 Gibberish sections
gibberish = {
    'Gap1': 'QAPBZDBKZEL',      # 11 chars
    'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',  # 38 chars
    'Gap3': 'RSPVJWQUL',         # 9 chars
    'Gap4': 'ZOLRKCAYF'          # 9 chars
}

# Key coordinates to search for (in various formats)
key_coordinates = {
    'CIA_HQ': {
        'name': 'CIA Headquarters, Langley, VA',
        'decimal': (38.9518, -77.1456),
        'dms': '38°57\'6.5"N, 77°8\'44"W',
        'variations': [
            38.9518, 38.95, 77.1456, 77.14, 77.1454,
            57, 6, 8, 44,  # Minutes and seconds
            389518, 771456,  # No decimal point
        ]
    },
    'Berlin_Clock': {
        'name': 'Berlin Clock (Weltzeituhr), Berlin',
        'decimal': (52.52, 13.4122),
        'dms': '52°31\'12"N, 13°24\'44"E',
        'variations': [
            52.52, 52.5200, 13.4122, 13.41, 13.40, 13.4,
            31, 12, 24, 44,  # Minutes and seconds
            5252, 1341, 5231, 1324,  # Integer versions
        ]
    },
    'Valley_of_Kings': {
        'name': 'Valley of the Kings, Egypt',
        'decimal': (25.7333, 32.6),
        'dms': '25°44\'N, 32°36\'E',
        'variations': [
            25.7333, 25.73, 32.6, 32.60,
            44, 36,  # Minutes
            2574, 3260,  # Integer versions
        ]
    }
}

def encode_method1(text):
    """A=1, B=2... Z=26"""
    return [ord(c) - ord('A') + 1 for c in text.upper()]

def encode_method2(text):
    """A=0, B=1... Z=25"""
    return [ord(c) - ord('A') for c in text.upper()]

def encode_method3(text):
    """KRYPTOS alphabet ordering (custom)"""
    kryptos_alpha = 'KRYPTOS'
    full_alpha = 'KRYPTOS' + 'ABCDEFGHIJLMNUVWXZ'.replace('K', '').replace('R', '').replace('Y', '').replace('P', '').replace('T', '').replace('O', '').replace('S', '')
    # Standard approach: KRYPTOS alphabet typically means the order K,R,Y,P,T,O,S, then rest
    kryptos_order = list(dict.fromkeys('KRYPTOS'))  # K, R, Y, P, T, O, S
    remaining = [c for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if c not in kryptos_order]
    kryptos_full = kryptos_order + remaining

    result = []
    for c in text.upper():
        try:
            result.append(kryptos_full.index(c) + 1)
        except ValueError:
            result.append(0)
    return result

def find_decimal_patterns(values):
    """Extract decimal coordinate patterns from values"""
    results = []

    # Try combining consecutive digits as decimal coordinates
    for i in range(len(values) - 1):
        # Try as X.Y format
        combined = values[i] + (values[i+1] / 10.0)
        results.append({
            'value': combined,
            'format': f'{values[i]}.{values[i+1]}',
            'position': i
        })

        # Try as X.YY format
        if values[i+1] >= 10:
            combined = values[i] + (values[i+1] / 100.0)
            results.append({
                'value': combined,
                'format': f'{values[i]}.{values[i+1]:02d}',
                'position': i
            })

    return results

def find_dms_patterns(values):
    """Look for degree-minute-second patterns"""
    results = []

    # DMS typically: DD MM SS or DD MM.MM
    for i in range(len(values) - 2):
        deg = values[i]
        mins = values[i+1]
        secs = values[i+2]

        if deg <= 90 and mins <= 60 and secs <= 60:
            decimal = deg + (mins / 60.0) + (secs / 3600.0)
            results.append({
                'degrees': deg,
                'minutes': mins,
                'seconds': secs,
                'decimal': decimal,
                'format': f'{deg}°{mins}\'{secs}"',
                'position': i
            })

    return results

def find_integer_patterns(values):
    """Look for integer encodings of coordinates"""
    results = []

    # Check if consecutive values form known coordinate numbers
    for i in range(len(values) - 1):
        combined = int(str(values[i]) + str(values[i+1]))
        results.append({
            'combined': combined,
            'format': f'{values[i]}{values[i+1]}',
            'position': i
        })

    return results

def check_known_coordinates(value, tolerance=0.01):
    """Check if a value matches any known coordinate"""
    matches = []

    for loc_key, loc_data in key_coordinates.items():
        for variation in loc_data['variations']:
            if isinstance(variation, float):
                if abs(value - variation) < tolerance:
                    matches.append({
                        'location': loc_data['name'],
                        'expected': variation,
                        'found': value,
                        'location_key': loc_key
                    })
            else:
                if value == variation:
                    matches.append({
                        'location': loc_data['name'],
                        'expected': variation,
                        'found': value,
                        'location_key': loc_key,
                        'exact_match': True
                    })

    return matches

def analyze_gap(gap_name, gap_text):
    """Comprehensive analysis of a gap"""
    print(f"\n{'='*70}")
    print(f"ANALYZING {gap_name}: {gap_text}")
    print(f"{'='*70}")

    # Method 1: A=1, B=2... Z=26
    values1 = encode_method1(gap_text)
    print(f"\n[METHOD 1] A=1, B=2... Z=26")
    print(f"  Values: {values1}")

    # Check decimal patterns
    decimals1 = find_decimal_patterns(values1)
    print(f"  Decimal patterns found: {len(decimals1)}")
    for dec in decimals1[:5]:  # Show first 5
        matches = check_known_coordinates(dec['value'])
        if matches:
            print(f"    MATCH: {dec['format']} = {dec['value']:.4f}")
            for m in matches:
                print(f"      -> {m['location']} ({m['expected']})")

    # Check DMS patterns
    dms1 = find_dms_patterns(values1)
    print(f"  DMS patterns found: {len(dms1)}")
    for d in dms1[:5]:
        matches = check_known_coordinates(d['decimal'])
        if matches:
            print(f"    MATCH: {d['format']} = {d['decimal']:.4f}")
            for m in matches:
                print(f"      -> {m['location']}")

    # Method 2: A=0, B=1... Z=25
    values2 = encode_method2(gap_text)
    print(f"\n[METHOD 2] A=0, B=1... Z=25")
    print(f"  Values: {values2}")

    decimals2 = find_decimal_patterns(values2)
    print(f"  Decimal patterns found: {len(decimals2)}")
    for dec in decimals2[:5]:
        matches = check_known_coordinates(dec['value'])
        if matches:
            print(f"    MATCH: {dec['format']} = {dec['value']:.4f}")
            for m in matches:
                print(f"      -> {m['location']}")

    # Method 3: KRYPTOS alphabet
    values3 = encode_method3(gap_text)
    print(f"\n[METHOD 3] KRYPTOS Alphabet Ordering")
    print(f"  Values: {values3}")

    decimals3 = find_decimal_patterns(values3)
    print(f"  Decimal patterns found: {len(decimals3)}")
    for dec in decimals3[:5]:
        matches = check_known_coordinates(dec['value'])
        if matches:
            print(f"    MATCH: {dec['format']} = {dec['value']:.4f}")
            for m in matches:
                print(f"      -> {m['location']}")

    # Look for digit sequences
    print(f"\n[METHOD 4] Direct digit patterns (looking for 38, 77, 52, 13, 25, 32, etc.)")
    values1_str = ''.join(str(v).zfill(2) for v in values1)
    values2_str = ''.join(str(v).zfill(2) for v in values2)
    values3_str = ''.join(str(v).zfill(2) for v in values3)

    for method_name, digit_str in [('Method 1', values1_str), ('Method 2', values2_str), ('Method 3', values3_str)]:
        for pattern in ['38', '77', '52', '13', '25', '32', '57', '8', '31', '12', '24', '36', '44']:
            if pattern in digit_str:
                pos = digit_str.index(pattern)
                print(f"    {method_name}: Found '{pattern}' at position {pos}")

def analyze_combined_gaps():
    """Analyze combinations of gaps"""
    print(f"\n{'='*70}")
    print("ANALYZING COMBINED GAPS")
    print(f"{'='*70}")

    all_gaps = ''.join(gibberish.values())
    values1 = encode_method1(all_gaps)
    values2 = encode_method2(all_gaps)

    print(f"\nCombined text: {all_gaps}")
    print(f"Total length: {len(all_gaps)}")

    # Look for patterns
    print(f"\n[METHOD 1 COMBINED]")
    values1_str = ''.join(str(v).zfill(2) for v in values1)
    print(f"  Digit string: {values1_str[:50]}...")

    for pattern in ['38', '77', '52', '13', '25', '32', '57', '8', '31', '12', '24', '36', '44']:
        matches = [i for i in range(len(values1_str)-len(pattern)+1) if values1_str[i:i+len(pattern)] == pattern]
        if matches:
            print(f"    Pattern '{pattern}' found at positions: {matches}")

    print(f"\n[METHOD 2 COMBINED]")
    values2_str = ''.join(str(v).zfill(2) for v in values2)
    print(f"  Digit string: {values2_str[:50]}...")

    for pattern in ['38', '77', '52', '13', '25', '32', '57', '8', '31', '12', '24', '36', '44']:
        matches = [i for i in range(len(values2_str)-len(pattern)+1) if values2_str[i:i+len(pattern)] == pattern]
        if matches:
            print(f"    Pattern '{pattern}' found at positions: {matches}")

def main():
    print("K4 GIBBERISH COORDINATE ENCODING ANALYSIS")
    print("=" * 70)

    # Analyze each gap
    for gap_name, gap_text in gibberish.items():
        analyze_gap(gap_name, gap_text)

    # Analyze combined gaps
    analyze_combined_gaps()

    # Summary report
    print(f"\n{'='*70}")
    print("COORDINATE PATTERNS TO LOOK FOR")
    print(f"{'='*70}")
    print("\nKEY COORDINATES:")
    for loc_key, loc_data in key_coordinates.items():
        print(f"\n  {loc_data['name']}")
        print(f"    Decimal: {loc_data['decimal']}")
        print(f"    DMS: {loc_data['dms']}")
        print(f"    Key numbers: {loc_data['variations'][:8]}")

    # Summary of findings
    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}")
    print("\nNOTE: Check the output above for any coordinate-like patterns.")
    print("Pay special attention to:")
    print("  - Values near 38-39 (CIA latitude)")
    print("  - Values near 77 (CIA longitude)")
    print("  - Values near 52 (Berlin latitude)")
    print("  - Values near 13 (Berlin longitude)")
    print("  - DMS patterns that decode to known locations")

if __name__ == '__main__':
    main()
