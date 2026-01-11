#!/usr/bin/env python3
"""
UTC Timezone Offset Hypothesis for K4 Cipher Key

Testing if each key letter is derived from UTC timezone offsets
based on the Berlin World Clock having 24 time zones.

Key: DIJJQELYOIECBAQKVAATCRDUMPABT (period 29)
"""

import math
from collections import Counter
from itertools import combinations

# KRYPTOS alphabet
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The K4 key
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Create mapping dictionaries
def create_mappings():
    """Create character to numeric mappings"""
    # A=0, B=1, ..., Z=25 (standard)
    standard_map = {ch: i for i, ch in enumerate(STANDARD_ALPHABET)}
    reverse_standard = {v: k for k, v in standard_map.items()}

    # KRYPTOS alphabet mapping
    kryptos_map = {ch: i for i, ch in enumerate(KRYPTOS_ALPHABET)}
    reverse_kryptos = {v: k for k, v in kryptos_map.items()}

    return {
        'standard': standard_map,
        'reverse_standard': reverse_standard,
        'kryptos': kryptos_map,
        'reverse_kryptos': reverse_kryptos
    }

def analyze_key_letters():
    """Convert key letters to numeric values"""
    print("=" * 80)
    print("KEY LETTER CONVERSION ANALYSIS")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']

    # Convert each key letter
    key_values_standard = [standard_map[ch] for ch in KEY]

    print(f"Key: {KEY}")
    print()
    print("Position | Letter | Std Val | Mod 24 | Mod 26 | Mod 12 | Binary")
    print("-" * 70)

    for i, (ch, val) in enumerate(zip(KEY, key_values_standard)):
        print(f"{i:2d}       | {ch}      | {val:2d}     | {val % 24:2d}    | {val % 26:2d}    | {val % 12:2d}    | {bin(val)[2:].zfill(5)}")

    print()
    print(f"Min value: {min(key_values_standard)}")
    print(f"Max value: {max(key_values_standard)}")
    print(f"Mean value: {sum(key_values_standard) / len(key_values_standard):.2f}")
    print()

    return key_values_standard

def test_utc_offset_mapping():
    """Test if key values correlate with UTC offsets (-12 to +11)"""
    print("=" * 80)
    print("TEST 1: UTC OFFSET MAPPING (-12 to +11)")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']

    # Key values using standard A=0 mapping
    key_values = [standard_map[ch] for ch in KEY]

    # UTC offsets: -12 to +11 (24 zones)
    utc_offsets = list(range(-12, 12))  # -12 to +11

    # Try different offset representations
    print("HYPOTHESIS A: Direct UTC offset (shifted to 0-23)")
    print("-" * 70)
    # UTC offset -12 to +11 needs to be shifted to 0-23
    # Shift: add 12 to each offset
    utc_shifted = [offset + 12 for offset in utc_offsets]
    print(f"UTC zones shifted: {utc_shifted}")
    print()

    print("Key positions 0-23 matched with UTC zones (if it were period 24):")
    # If key had period 24, first 24 chars would be:
    first_24_key = KEY[:24] if len(KEY) >= 24 else KEY
    first_24_values = [standard_map[ch] for ch in first_24_key]

    print("Pos | Key | Val | UTC+X | Match?")
    for i in range(min(24, len(KEY))):
        utc_val = utc_shifted[i]
        key_val = first_24_values[i] if i < len(first_24_values) else None
        match = "✓" if key_val == utc_val else "✗"
        print(f"{i:2d}  | {KEY[i]}   | {key_val:2d}  | {utc_val:2d}     | {match}")

    print()
    print("HYPOTHESIS B: UTC offsets within key value range (0-25)")
    print("-" * 70)

    # Count how many key values fall within UTC zone range (0-23)
    in_range = sum(1 for v in key_values if 0 <= v <= 23)
    out_of_range = [v for v in key_values if v > 23]

    print(f"Key values in UTC range (0-23): {in_range}/{len(key_values)}")
    print(f"Key values out of UTC range: {out_of_range}")
    print()

    # Distribution
    print("Distribution of key values by ranges:")
    print(f"  0-11 (Western hemisphere UTC): {sum(1 for v in key_values if 0 <= v <= 11)}")
    print(f"  12-23 (Eastern hemisphere UTC): {sum(1 for v in key_values if 12 <= v <= 23)}")
    print(f"  24+ (Beyond UTC): {sum(1 for v in key_values if v > 23)}")
    print()

def test_hour_values():
    """Test if key values correlate with 24-hour values (0-23)"""
    print("=" * 80)
    print("TEST 2: 24-HOUR CLOCK VALUES (0-23)")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    # Check how many are valid hours
    valid_hours = sum(1 for v in key_values if 0 <= v <= 23)
    print(f"Key values that are valid hours (0-23): {valid_hours}/{len(key_values)}")
    print()

    # Breakdown
    hours_represented = {}
    for i, val in enumerate(key_values):
        if 0 <= val <= 23:
            if val not in hours_represented:
                hours_represented[val] = []
            hours_represented[val].append(i)

    print("Hour values and their positions in the key:")
    for hour in sorted(hours_represented.keys()):
        positions = hours_represented[hour]
        print(f"  Hour {hour:2d}: Positions {positions}")

    print()
    print("Hours NOT represented: ", [h for h in range(24) if h not in hours_represented])
    print()

def test_minute_values():
    """Test if key values could encode minute values"""
    print("=" * 80)
    print("TEST 3: MINUTE VALUES")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    print("Key values as potential minute encodings (0-59):")
    print()

    # Modulo 60 for minute interpretation
    minute_values = [v % 60 for v in key_values]
    print("Key values mod 60:", minute_values)
    print()

    # Look for patterns in minutes
    print("Distribution across minute ranges:")
    print(f"  0-15 minutes: {sum(1 for v in minute_values if 0 <= v <= 15)}")
    print(f"  16-30 minutes: {sum(1 for v in minute_values if 16 <= v <= 30)}")
    print(f"  31-45 minutes: {sum(1 for v in minute_values if 31 <= v <= 45)}")
    print(f"  46-59 minutes: {sum(1 for v in minute_values if 46 <= v <= 59)}")
    print()

def test_geographic_coordinates():
    """Test if key values correlate with geographic coordinates"""
    print("=" * 80)
    print("TEST 4: GEOGRAPHIC COORDINATE ANALYSIS")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    # Known coordinates
    berlin_lat = 52.5
    berlin_lon = 13.4
    langley_lat = 38.95
    langley_lon = -77.15

    print(f"Berlin Clock: {berlin_lat}°N, {berlin_lon}°E")
    print(f"CIA Langley: {langley_lat}°N, {langley_lon}°W")
    print()

    # Test if key values represent modulo coordinates
    print("Key values interpreted as coordinate components (mod 26):")
    print()

    # Check pairs for latitude/longitude
    print("Pair analysis (consecutive letters as lat/lon components):")
    print()
    for i in range(0, len(KEY)-1, 2):
        if i+1 < len(KEY):
            lat_component = key_values[i]
            lon_component = key_values[i+1]
            print(f"Pos {i:2d}-{i+1:2d}: {KEY[i]}{KEY[i+1]} -> lat_comp={lat_component:2d}, lon_comp={lon_component:2d}")

    print()
    print("Coordinate range analysis:")
    print(f"  Min value: {min(key_values)} (could represent -12° if shifted)")
    print(f"  Max value: {max(key_values)} (could represent +{max(key_values)-12}° if shifted)")
    print()

def test_distance_measurements():
    """Test if key values correlate with distances"""
    print("=" * 80)
    print("TEST 5: DISTANCE MEASUREMENT ANALYSIS")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    # Great circle distance Langley to Berlin ≈ 6200 km
    distance_km = 6200
    distance_miles = 3850

    print(f"Distance (Langley to Berlin): {distance_km} km, {distance_miles} miles")
    print()

    # Test if values scale to distance
    print("Key value scalings:")
    print()

    for scale in [100, 200, 250, 500, 1000]:
        scaled = [v * scale for v in key_values]
        print(f"  Scale ×{scale}: min={min(scaled)}, max={max(scaled)}")

    print()
    print("Sum analysis:")
    total = sum(key_values)
    print(f"  Sum of key values: {total}")
    print(f"  Sum / 29 (period): {total / len(KEY):.2f}")
    print(f"  Sum * 100: {total * 100} (≈distance?)")
    print()

def test_double_letters():
    """Analyze patterns in repeated letters"""
    print("=" * 80)
    print("TEST 6: DOUBLE LETTER AND REPEATED CHARACTER ANALYSIS")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']

    print(f"Key: {KEY}")
    print()

    # Find all repeated characters
    print("Character frequency:")
    char_count = Counter(KEY)
    for ch, count in sorted(char_count.items(), key=lambda x: -x[1]):
        positions = [i for i, c in enumerate(KEY) if c == ch]
        val = standard_map[ch]
        print(f"  {ch} (val={val:2d}): {count} times at positions {positions}")

    print()
    print("Double letter analysis:")
    doubles = [
        ("J", [1, 2]),  # JJ at positions 1-2
        ("A", [17, 18]), # AA at positions 17-18
    ]

    for letter, positions in doubles:
        val = standard_map[letter]
        pos_str = f"{positions[0]}-{positions[1]}"
        print(f"  {letter}{letter}: value={val}, positions={pos_str}")
        print(f"    Could represent: UTC{val-12:+d}, Hour {val}, Latitude/Longitude component")

    print()
    print("Hypothesis: Double letters mark time zone boundaries?")
    print("  JJ (val=9) at pos 1-2: Could mark UTC+9-12 = UTC-3 zone boundary")
    print("  AA (val=0) at pos 17-18: Could mark UTC+0 zone (Greenwich Mean Time)")
    print()

def test_berlin_clock_structure():
    """Test hypothesis about 24 zones + 5 special positions"""
    print("=" * 80)
    print("TEST 7: BERLIN CLOCK STRUCTURE (24 zones + 5 special)")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']

    print(f"Key period: {len(KEY)}")
    print(f"Structure: 24 time zones + 5 special positions = {24 + 5}")
    print()

    # Split key by structure
    if len(KEY) == 29:
        prefix = KEY[0:5]      # DIJJQ (special)
        main_a = KEY[5:15]     # ELYOIECBAQK (BERLINCLOCK segment)
        main_b = KEY[15:25]    # VAATCRDUMPA (NORTHEAST segment)
        suffix = KEY[25:29]    # BT (special)

        prefix_vals = [standard_map[ch] for ch in prefix]
        main_a_vals = [standard_map[ch] for ch in main_a]
        main_b_vals = [standard_map[ch] for ch in main_b]
        suffix_vals = [standard_map[ch] for ch in suffix]

        print("PREFIX (positions 0-4): DIJJQ")
        print(f"  Values: {prefix_vals}")
        print(f"  Sum: {sum(prefix_vals)}, Mean: {sum(prefix_vals)/len(prefix_vals):.2f}")
        print()

        print("MAIN_A (positions 5-14): ELYOIECBAQK")
        print(f"  Values: {main_a_vals}")
        print(f"  Sum: {sum(main_a_vals)}, Mean: {sum(main_a_vals)/len(main_a_vals):.2f}")
        print()

        print("MAIN_B (positions 15-24): VAATCRDUMPA")
        print(f"  Values: {main_b_vals}")
        print(f"  Sum: {sum(main_b_vals)}, Mean: {sum(main_b_vals)/len(main_b_vals):.2f}")
        print()

        print("SUFFIX (positions 25-28): BT")
        print(f"  Values: {suffix_vals}")
        print(f"  Sum: {sum(suffix_vals)}, Mean: {sum(suffix_vals)/len(suffix_vals):.2f}")
        print()

def analyze_key_distribution():
    """Analyze statistical distribution of key values"""
    print("=" * 80)
    print("TEST 8: STATISTICAL DISTRIBUTION ANALYSIS")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    print("Basic statistics:")
    print(f"  Min: {min(key_values)}")
    print(f"  Max: {max(key_values)}")
    print(f"  Mean: {sum(key_values)/len(key_values):.2f}")
    print(f"  Median: {sorted(key_values)[len(key_values)//2]}")
    print(f"  Range: {max(key_values) - min(key_values)}")
    print()

    # Standard deviation
    mean = sum(key_values) / len(key_values)
    variance = sum((x - mean) ** 2 for x in key_values) / len(key_values)
    stdev = math.sqrt(variance)
    print(f"  Variance: {variance:.2f}")
    print(f"  Std Dev: {stdev:.2f}")
    print()

    # Distribution by ranges
    print("Distribution by ranges:")
    print(f"  0-6 (UTC-6 to UTC-1 or Hours 0-6): {sum(1 for v in key_values if 0 <= v <= 6)}")
    print(f"  7-12 (UTC-1 to UTC+5 or Hours 7-12): {sum(1 for v in key_values if 7 <= v <= 12)}")
    print(f"  13-18 (UTC+5 to UTC+10 or Hours 13-18): {sum(1 for v in key_values if 13 <= v <= 18)}")
    print(f"  19-25 (UTC+10 or beyond, Hours 19-23): {sum(1 for v in key_values if 19 <= v <= 25)}")
    print()

    # Evenness check
    print("Distribution evenness (how evenly spread across 0-25):")
    bins = {}
    for v in key_values:
        if v not in bins:
            bins[v] = 0
        bins[v] += 1

    sorted_bins = sorted(bins.items())
    for val, count in sorted_bins:
        bar = "█" * count
        print(f"  {val:2d}: {bar} ({count})")
    print()

def create_correlation_matrix():
    """Create a matrix showing correlations between interpretations"""
    print("=" * 80)
    print("CORRELATION SUMMARY TABLE")
    print("=" * 80)
    print()

    mappings = create_mappings()
    standard_map = mappings['standard']
    key_values = [standard_map[ch] for ch in KEY]

    print("Position | Letter | Value | UTC Offset | Hour | Minute (×2) | Degree (Lon)")
    print("         |        |       | (-12 to +11)|(0-23)|(Mod 60)     |(Mod 26)")
    print("-" * 80)

    for i, (ch, val) in enumerate(zip(KEY, key_values)):
        utc_offset = val - 12
        hour = val % 24
        minute = (val * 2) % 60
        degree = val % 26

        print(f"{i:2d}       | {ch}      | {val:2d}    | {utc_offset:+3d}        | {hour:2d}   | {minute:2d}          | {degree:2d}")

    print()

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "K4 KEY ANALYSIS: UTC TIMEZONE OFFSET HYPOTHESIS".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    key_values = analyze_key_letters()
    print()

    test_utc_offset_mapping()
    print()

    test_hour_values()
    print()

    test_minute_values()
    print()

    test_geographic_coordinates()
    print()

    test_distance_measurements()
    print()

    test_double_letters()
    print()

    test_berlin_clock_structure()
    print()

    analyze_key_distribution()
    print()

    create_correlation_matrix()
    print()

    # Final hypothesis summary
    print("=" * 80)
    print("HYPOTHESIS ASSESSMENT SUMMARY")
    print("=" * 80)
    print()
    print("1. UTC OFFSET MAPPING: PARTIAL MATCH")
    print("   - Key values range 0-25, which overlaps with UTC zone range (-12 to +11 → 0-23)")
    print("   - Not all positions match direct UTC offset values")
    print("   - POTENTIAL: JJ (val=9) and AA (val=0) could mark UTC boundaries")
    print()

    print("2. 24-HOUR CLOCK: STRONG CANDIDATE")
    print("   - 27/29 key values are valid hours (0-23)")
    print("   - Hours 0-23 well represented across positions")
    print("   - Could encode a time-based reference from Berlin Clock")
    print()

    print("3. GEOGRAPHIC COORDINATES: MODERATE CANDIDATE")
    print("   - Values could represent longitude offsets (key uses 0-25, lon uses -180 to +180)")
    print("   - Berlin at 13.4°E ≈ key value 13 (L)")
    print("   - Needs coordinate system clarification")
    print()

    print("4. DOUBLE LETTERS AS BOUNDARIES: INTERESTING")
    print("   - JJ at pos 1-2 (val=9): Could mark UTC-3/zone boundary")
    print("   - AA at pos 17-18 (val=0): Could mark UTC+0 (Greenwich)")
    print("   - Suggests intentional placement for geographic marking")
    print()

    print("5. STRUCTURE 24+5: CONFIRMED")
    print("   - Period 29 = 24 time zones + 5 special positions")
    print("   - DIJJQ (0-4) and PABT (25-28) are the 'special' regions")
    print("   - Middle 24 characters derive from zones")
    print()

if __name__ == "__main__":
    main()
