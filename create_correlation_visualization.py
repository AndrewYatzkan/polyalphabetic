#!/usr/bin/env python3
"""
Create detailed correlation visualization tables for K4 key analysis.
Outputs comprehensive tables showing all correlations.
"""

import csv
from datetime import datetime

# KRYPTOS alphabet
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The K4 key
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Confirmed plaintext
PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

def create_mapping():
    """Create character to numeric mapping"""
    return {ch: i for i, ch in enumerate(STANDARD_ALPHABET)}

def analyze_with_all_interpretations():
    """Create comprehensive table with all interpretations"""
    mapping = create_mapping()

    print("=" * 120)
    print("COMPREHENSIVE K4 KEY CORRELATION TABLE - ALL INTERPRETATIONS")
    print("=" * 120)
    print()

    # Header
    header = (
        "Pos | Key | Plain | Val | UTC±  | Hour | Min  | Bearing | Lon | Special Markers\n"
        "    |     | Text  |     | Zone  | 0-23 | (÷60)| (°)     | Mod |"
    )
    print(header)
    print("-" * 120)

    for i in range(len(KEY)):
        key_ch = KEY[i]
        plain_ch = PLAINTEXT[i] if i < len(PLAINTEXT) else "?"
        val = mapping[key_ch]

        # Calculations
        utc_offset = val - 12
        hour = val % 24
        minute = (val * 2.5) % 60
        bearing = (val * 15.625) % 360
        lon_mod = val % 26

        # Identify special markers
        markers = []

        # Double letters
        if i > 0 and KEY[i] == KEY[i-1]:
            markers.append("DOUBLE")
        if i < len(KEY) - 1 and KEY[i] == KEY[i+1]:
            markers.append("DOUBLE")

        # Key positions (0-4, 25-28)
        if i < 5:
            markers.append("PREFIX")
        if i >= 25:
            markers.append("SUFFIX")

        # Geographic markers
        if key_ch == 'A':
            markers.append("GEO:BERLIN")
        if key_ch == 'E':
            markers.append("GEO:CAIRO")
        if val == 0:
            markers.append("UTC:GMT")
        if val == 2:
            markers.append("UTC:CAIRO")

        # Plaintext markers
        if i == 0:
            markers.append("START:UNDER")
        if i == 16:
            markers.append("MID:NORTHEAST")
        if i == 63:
            markers.append("BERLINCLOCK")
        if i == 83:
            markers.append("ABOVE")

        marker_str = " ".join(markers) if markers else ""

        # Format row
        print(
            f"{i:2d}  | {key_ch:1s}   | {plain_ch:1s}     | {val:2d}  | "
            f"UTC{utc_offset:+2d}  | {hour:2d}   | {minute:5.1f} | {bearing:6.1f} | {lon_mod:2d}  | {marker_str}"
        )

    print()

def print_plaintext_with_positions():
    """Print plaintext with position markers"""
    print("=" * 120)
    print("K4 PLAINTEXT WITH POSITION MARKERS")
    print("=" * 120)
    print()

    print("Position markers every 10 characters:")
    print()

    # Print plaintext in rows of 50
    for start in range(0, len(PLAINTEXT), 50):
        end = min(start + 50, len(PLAINTEXT))
        chunk = PLAINTEXT[start:end]
        positions = "".join(str(i % 10) for i in range(start, end))

        print(f"Pos {start:2d}-{end:2d}: {chunk}")
        print(f"           {positions}")
        print()

    print("Key plaintext sections:")
    print("  0-4:   UNDER (5 chars)")
    print("  5-15:  QAPBZDBKZEL (11 chars)")
    print("  16-24: NORTHEAST (9 chars)")
    print("  25-62: [gibberish] (38 chars)")
    print("  63-73: BERLINCLOCK (11 chars)")
    print("  74-82: RSPVJWQUL (9 chars)")
    print("  83-87: ABOVE (5 chars)")
    print("  88-96: ZOLRKCAYF (9 chars)")
    print()

def print_utc_zone_mapping():
    """Print UTC zone mapping for 24 main positions"""
    print("=" * 120)
    print("UTC ZONE MAPPING FOR MAIN 24 POSITIONS")
    print("=" * 120)
    print()

    mapping = create_mapping()

    utc_zones = [
        (0, "UTC-12", "Baker Island"),
        (1, "UTC-11", "American Samoa"),
        (2, "UTC-10", "Tahiti"),
        (3, "UTC-9", "Anchorage"),
        (4, "UTC-8", "Los Angeles"),
        (5, "UTC-7", "Denver"),
        (6, "UTC-6", "Mexico City"),
        (7, "UTC-5", "New York"),
        (8, "UTC-4", "Santiago"),
        (9, "UTC-3", "Brasília"),
        (10, "UTC-2", "Mid-Atlantic"),
        (11, "UTC-1", "Azores"),
        (12, "UTC+0", "London/GMT"),
        (13, "UTC+1", "Paris"),
        (14, "UTC+2", "Cairo"),
        (15, "UTC+3", "Moscow"),
        (16, "UTC+4", "Dubai"),
        (17, "UTC+5", "Pakistan"),
        (18, "UTC+6", "Bangladesh"),
        (19, "UTC+7", "Bangkok"),
        (20, "UTC+8", "Beijing"),
        (21, "UTC+9", "Tokyo"),
        (22, "UTC+10", "Sydney"),
        (23, "UTC+11", "Solomon Is"),
    ]

    print("If key position maps to UTC zone:")
    print()
    print("Pos | Key | Val | UTC   | City              | ✓ Match?")
    print("-" * 70)

    for zone_idx, utc_name, city in utc_zones:
        if zone_idx < len(KEY):
            key_ch = KEY[zone_idx]
            key_val = mapping[key_ch]
            zone_num = utc_name.split("+")[1] if "+" in utc_name else utc_name.split("-")[1]
            zone_num = int(zone_num)
            expected = zone_idx - 12

            match = "✓" if key_val == zone_idx else "✗"
            print(f"{zone_idx:2d}  | {key_ch:1s}   | {key_val:2d}  | {utc_name:6s} | {city:17s} | {match}")

    print()

def print_hour_distribution():
    """Print hour distribution analysis"""
    print("=" * 120)
    print("HOUR DISTRIBUTION IN KEY")
    print("=" * 120)
    print()

    mapping = create_mapping()

    hours = {}
    for i, ch in enumerate(KEY):
        val = mapping[ch]
        hour = val % 24
        if hour not in hours:
            hours[hour] = []
        hours[hour].append(i)

    print("Hour | Key Letter Positions | Frequency | Notes")
    print("-" * 120)

    for hour in range(24):
        if hour in hours:
            positions = hours[hour]
            letters = "".join(KEY[p] for p in positions)
            freq = len(positions)
            notes = ""

            if hour == 0:
                notes = "Midnight (A=0)"
            elif hour == 9:
                notes = "Morning (J=9) - JJ at pos 2-3!"
            elif hour == 12:
                notes = "Noon (M=12)"
            elif hour == 15:
                notes = "Afternoon (P=15)"
            elif hour == 21:
                notes = "Night (V=21)"

            print(f"{hour:2d}:00 | {letters:20s} | Pos {str(positions):30s} | {notes}")
        else:
            print(f"{hour:2d}:00 | [NOT REPRESENTED]        |                              |")

    print()
    missing = [h for h in range(24) if h not in hours]
    print(f"Missing hours: {missing}")
    print()

def print_geographic_analysis():
    """Print geographic encoding analysis"""
    print("=" * 120)
    print("GEOGRAPHIC ENCODING ANALYSIS")
    print("=" * 120)
    print()

    mapping = create_mapping()

    print("Known coordinates:")
    print()

    coords = {
        "Cairo, Egypt": (30.0, 31.2, "UTC+2"),
        "Berlin, Germany": (52.5, 13.4, "UTC+1"),
        "Langley, VA USA": (38.95, -77.15, "UTC-5"),
    }

    for city, (lat, lon, tz) in coords.items():
        lat_mod = int(lat) % 26
        lon_mod = int(abs(lon)) % 26
        sum_mod = (int(lat) + int(abs(lon))) % 26

        lat_letter = chr(65 + lat_mod)
        lon_letter = chr(65 + lon_mod)
        sum_letter = chr(65 + sum_mod)

        print(f"{city:25s}")
        print(f"  Latitude: {lat:6.1f}° mod 26 = {lat_mod:2d} ({lat_letter}) {mapping.get(lat_letter, '?')}")
        print(f"  Longitude: {lon:7.2f}° mod 26 = {lon_mod:2d} ({lon_letter})")
        print(f"  Sum: {sum_mod:2d} ({sum_letter})")
        print()

    print("Scanning key for geographic markers:")
    print()

    key_marker_map = {
        'A': (0, "Berlin latitude marker (52% mod 26)"),
        'E': (4, "Cairo latitude marker (30° mod 26)"),
        'C': (2, "Cairo timezone (UTC+2)"),
        'N': (13, "Berlin longitude (13.4°)"),
    }

    for ch, (expected_val, description) in key_marker_map.items():
        actual_val = mapping[ch]
        positions = [i for i, c in enumerate(KEY) if c == ch]
        print(f"{ch} (val={actual_val}): {description}")
        print(f"   Found at positions: {positions}")
        print()

def main():
    """Run all visualizations"""
    print("\n\n")
    print("╔" + "═" * 118 + "╗")
    print("║" + "K4 KEY CORRELATION VISUALIZATION - COMPREHENSIVE ANALYSIS".center(118) + "║")
    print("║" + "January 11, 2026".center(118) + "║")
    print("╚" + "═" * 118 + "╝")
    print("\n")

    analyze_with_all_interpretations()
    print("\n\n")

    print_plaintext_with_positions()
    print("\n\n")

    print_utc_zone_mapping()
    print("\n\n")

    print_hour_distribution()
    print("\n\n")

    print_geographic_analysis()

    # Save to file
    print("=" * 120)
    print("VISUALIZATION COMPLETE")
    print("=" * 120)

if __name__ == "__main__":
    main()
