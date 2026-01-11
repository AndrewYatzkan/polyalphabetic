#!/usr/bin/env python3
"""
K4 Coordinate Extraction - Advanced Analysis
Extracts complete coordinate pairs and validates against known locations
"""

# K4 Gibberish sections
gibberish = {
    'Gap1': 'QAPBZDBKZEL',
    'Gap2': 'LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH',
    'Gap3': 'RSPVJWQUL',
    'Gap4': 'ZOLRKCAYF'
}

# Key target coordinates
targets = {
    'CIA': {'lat': 38.9518, 'lon': -77.1456, 'lat_str': '38.95', 'lon_str': '77.14', 'dms': '38 57 6.5 77 8 44'},
    'Berlin': {'lat': 52.52, 'lon': 13.4122, 'lat_str': '52.52', 'lon_str': '13.41', 'dms': '52 31 12 13 24 44'},
    'Valley': {'lat': 25.7333, 'lon': 32.6, 'lat_str': '25.73', 'lon_str': '32.6', 'dms': '25 44 32 36'},
}

def encode_a1_z26(text):
    """Convert text to A=1, B=2... Z=26"""
    return [ord(c) - ord('A') + 1 for c in text.upper()]

def encode_a0_z25(text):
    """Convert text to A=0, B=1... Z=25"""
    return [ord(c) - ord('A') for c in text.upper()]

def extract_consecutive_digits(values, length):
    """Extract consecutive digit sequences of given length"""
    results = []
    values_str = ''.join(str(v).zfill(2) for v in values)

    for i in range(len(values_str) - length + 1):
        seq = values_str[i:i+length]
        if seq[0] != '0':  # No leading zeros
            results.append({
                'sequence': seq,
                'position': i,
                'as_int': int(seq),
                'as_float_2digit': float(seq) / 100 if len(seq) == 2 else None,
            })

    return results

def find_coordinate_pairs(values, gap_name):
    """Find potential latitude-longitude pairs in values"""
    values_str = ''.join(str(v).zfill(2) for v in values)

    print(f"\n{'='*70}")
    print(f"{gap_name} DETAILED EXTRACTION")
    print(f"{'='*70}")
    print(f"\nRaw digit string (A=1 method): {values_str}")
    print(f"Length: {len(values_str)}")

    # Look for 2-digit and 3-digit latitude patterns
    print(f"\n[2-DIGIT LAT/LON SEQUENCES]")
    pairs_2digit = []
    for i in range(0, len(values_str) - 3, 2):
        lat_str = values_str[i:i+2]
        lon_str = values_str[i+2:i+4]

        if lat_str and lon_str and lat_str[0] != '0' and lon_str[0] != '0':
            lat = int(lat_str)
            lon = int(lon_str)

            # Check if plausible coordinates
            if (1 <= lat <= 90) and (1 <= lon <= 180):
                pairs_2digit.append({
                    'lat': lat,
                    'lon': lon,
                    'position': i,
                    'plausible': True
                })

                # Check against known targets
                for target_name, target_data in targets.items():
                    if abs(lat - int(str(target_data['lat']).split('.')[0])) <= 1:
                        if abs(lon - int(str(target_data['lon']).split('.')[0])) <= 1:
                            print(f"  POTENTIAL MATCH: {lat}°{lon}° near {target_name} at position {i}")

    # Look for 3-digit + 2-digit patterns
    print(f"\n[3-DIGIT LAT + 2-DIGIT LON SEQUENCES]")
    for i in range(len(values_str) - 4):
        lat_str = values_str[i:i+3]
        lon_str = values_str[i+3:i+5]

        if lat_str and lon_str and lat_str[0] != '0' and lon_str[0] != '0':
            lat = int(lat_str)
            lon = int(lon_str)

            # Check if plausible coordinates
            if (1 <= lat <= 900) and (1 <= lon <= 180):
                lat_decimal = lat / 10.0  # Interpret as DDD.D
                lon_decimal = lon

                for target_name, target_data in targets.items():
                    if abs(lat_decimal - target_data['lat']) < 5:
                        if abs(lon_decimal - target_data['lon']) < 5:
                            print(f"  POTENTIAL: {lat_decimal}°{lon_decimal}° near {target_name} at position {i}")

    # Look for minute/second patterns
    print(f"\n[LOOKING FOR DMS PATTERNS]")
    # DMS: Degrees Minutes Seconds
    # Berlin: 52°31'12"N 13°24'44"E
    # CIA: 38°57'6.5"N 77°8'44"W

    for i in range(0, len(values_str) - 5, 2):
        parts = []
        for j in range(0, 6, 2):
            if i + j + 2 <= len(values_str):
                parts.append(int(values_str[i+j:i+j+2]))

        if len(parts) >= 3:
            deg, mins, secs = parts[0], parts[1], parts[2]

            # Check constraints
            if deg <= 90 and 0 <= mins <= 60 and 0 <= secs <= 60:
                decimal = deg + (mins / 60.0) + (secs / 3600.0)

                # Check against targets
                for target_name, target_data in targets.items():
                    if abs(decimal - target_data['lat']) < 0.5:
                        print(f"  MATCH LAT: {deg}°{mins}'{secs}\" = {decimal:.4f}° near {target_name}")

    # Look for decimal point sequences (e.g., 38.95)
    print(f"\n[DECIMAL PATTERNS (X.YY format)]")
    for i in range(len(values_str) - 3):
        int_part = int(values_str[i:i+2])
        dec_part = int(values_str[i+2:i+4])
        value = int_part + (dec_part / 100.0)

        if 0 < value < 180:
            for target_name, target_data in targets.items():
                if abs(value - target_data['lat']) < 0.1 or abs(value - target_data['lon']) < 0.1:
                    print(f"  MATCH: {int_part}.{dec_part:02d} = {value:.4f}° ({target_name})")

def analyze_full_text():
    """Analyze the full K4 gibberish combined"""
    combined = ''.join(gibberish.values())
    values1 = encode_a1_z26(combined)

    print(f"\n{'='*70}")
    print("FULL K4 GIBBERISH COMBINED ANALYSIS")
    print(f"{'='*70}")
    print(f"\nCombined text: {combined}")
    print(f"Length: {len(combined)}")

    values_str = ''.join(str(v).zfill(2) for v in values1)
    print(f"\nFull digit string: {values_str}")
    print(f"\nSearching for target sequences...")

    # Search for known coordinate strings
    search_patterns = [
        ('CIA Lat (38)', '38'),
        ('CIA Lon (77)', '77'),
        ('Berlin Lat (52)', '52'),
        ('Berlin Lon (13)', '13'),
        ('Valley Lat (25)', '25'),
        ('Valley Lon (32)', '32'),
        ('38.95', '3895'),
        ('77.14', '7714'),
        ('52.52', '5252'),
        ('13.41', '1341'),
        ('25.73', '2573'),
        ('32.6', '326'),
    ]

    print(f"\nTarget sequence locations:")
    for name, pattern in search_patterns:
        positions = []
        for i in range(len(values_str) - len(pattern) + 1):
            if values_str[i:i+len(pattern)] == pattern:
                positions.append(i)

        if positions:
            print(f"  '{pattern}' ({name}): found at position(s) {positions}")

def analyze_with_modulo():
    """Try analyzing with modulo operations"""
    print(f"\n{'='*70}")
    print("MODULO AND TRANSFORMATION ANALYSIS")
    print(f"{'='*70}")

    for gap_name, gap_text in gibberish.items():
        values = encode_a1_z26(gap_text)
        print(f"\n{gap_name}: {gap_text}")
        print(f"  Values: {values}")

        # Try modulo 26, 10, 9
        mod_26 = [v % 26 for v in values]
        mod_10 = [v % 10 for v in values]
        mod_9 = [v % 9 for v in values]

        print(f"  Mod 26: {mod_26}")
        print(f"  Mod 10: {mod_10}")
        print(f"  Mod 9:  {mod_9}")

        # Look for coordinate patterns in transformations
        mod_26_str = ''.join(str(v).zfill(2) for v in mod_26)
        if '38' in mod_26_str or '77' in mod_26_str or '52' in mod_26_str or '13' in mod_26_str:
            print(f"    >>> PATTERN FOUND in Mod 26: {mod_26_str}")

def main():
    # Analyze each gap
    for gap_name, gap_text in gibberish.items():
        values = encode_a1_z26(gap_text)
        find_coordinate_pairs(values, gap_name)

    # Analyze full combined text
    analyze_full_text()

    # Try other transformations
    analyze_with_modulo()

    print(f"\n{'='*70}")
    print("SUMMARY OF FINDINGS")
    print(f"{'='*70}")
    print("""
Key Observations:
1. Multiple instances of coordinate-like digits (52, 13, 25, 32, etc.)
2. Pattern '52' appears frequently (Berlin latitude)
3. Pattern '13' appears multiple times (Berlin longitude)
4. Pattern '25' appears several times (Valley latitude)

Next Steps to Try:
1. Check if coordinate pairs are adjacent in the digit string
2. Try reverse reading or different offset alignments
3. Look for sum/difference relationships
4. Check if specific positions in the text encode specific lat/lon digits
5. Analyze the gaps for positional encoding (each gap = each coordinate component)
""")

if __name__ == '__main__':
    main()
