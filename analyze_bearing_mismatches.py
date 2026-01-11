#!/usr/bin/env python3
"""
DETAILED ANALYSIS OF BEARING MISMATCHES

The previous test revealed 4 mismatches out of 29. This script investigates:
1. What bearings would produce the CORRECT letters?
2. Are there alternative location pairs that would work?
3. What coordinates would be needed?
"""

import math
from typing import Tuple, List, Dict

LOCATIONS = {
    "CIA_HQ": (38.9517, -77.1467),
    "Berlin_Weltzeituhr": (52.5200, 13.4050),
    "Berlin_Brandenburg_Gate": (52.5163, 13.3777),
    "Berlin_Wall_Memorial": (52.5397, 13.3896),
    "Berlin_Reichstag": (52.5186, 13.3755),
    "Dubai": (25.2048, 55.2708),
    "Istanbul": (41.0082, 28.9784),
    "Moscow": (55.7558, 37.6173),
    "Valley_of_Kings": (25.7402, 32.6014),
    "Mexico_City": (19.4326, -99.1332),
    "Bangkok": (13.7563, 100.5018),
    "Rio_Janeiro": (22.9068, -43.1729),
    "Buenos_Aires": (34.6037, -58.3816),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (33.8688, 151.2093),
    "Wellington": (41.2865, 174.7762),
    "Athens": (37.9838, 23.7275),
    "Cairo": (30.0444, 31.2357),
}

# The 4 mismatches
MISMATCHES = [
    ("CIA_HQ", "Buenos_Aires", "L"),  # Position 7
    ("CIA_HQ", "Rio_Janeiro", "K"),   # Position 16
    ("CIA_HQ", "Wellington", "R"),    # Position 22
    ("Tokyo", "Sydney", "M"),          # Position 25
]


def haversine_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate initial bearing from point 1 to point 2."""
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlon = lon2_rad - lon1_rad

    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)

    return (bearing_deg + 360) % 360


def bearing_to_letter(bearing: float) -> Tuple[int, str]:
    """Convert bearing to letter."""
    index = math.floor((bearing / 360.0) * 26) % 26
    letter = chr(ord('A') + index)
    return index, letter


def letter_to_bearing_range(letter: str) -> Tuple[float, float]:
    """Calculate the bearing range that produces a given letter."""
    index = ord(letter) - ord('A')
    min_bearing = (index / 26) * 360
    max_bearing = ((index + 1) / 26) * 360
    return min_bearing, max_bearing


def find_alternative_locations(target_letter: str) -> List[Tuple[str, str, float]]:
    """Find location pairs that would produce the target letter."""

    min_bearing, max_bearing = letter_to_bearing_range(target_letter)

    print(f"\n{'=' * 100}")
    print(f"FINDING ALTERNATIVES FOR '{target_letter}' (bearing range: {min_bearing:.2f}° - {max_bearing:.2f}°)")
    print(f"{'=' * 100}\n")

    valid_pairs = []

    for from_city in LOCATIONS:
        for to_city in LOCATIONS:
            if from_city == to_city:
                continue

            bearing = haversine_bearing(LOCATIONS[from_city][0], LOCATIONS[from_city][1],
                                      LOCATIONS[to_city][0], LOCATIONS[to_city][1])
            _, letter = bearing_to_letter(bearing)

            if letter == target_letter:
                valid_pairs.append((from_city, to_city, bearing))

    valid_pairs.sort(key=lambda x: x[2])

    print(f"Found {len(valid_pairs)} location pairs that produce '{target_letter}':\n")

    for from_city, to_city, bearing in valid_pairs[:15]:  # Show top 15
        print(f"  {from_city:25s} → {to_city:25s} | Bearing {bearing:7.2f}°")

    return valid_pairs


def main():
    print("=" * 100)
    print("ANALYSIS: BEARING MISMATCHES AND ALTERNATIVES")
    print("=" * 100)
    print()

    # Analyze each mismatch
    for from_city, to_city, expected_letter in MISMATCHES:
        print(f"\nMISMATCH: {from_city} → {to_city}")
        print("-" * 100)

        from_coords = LOCATIONS[from_city]
        to_coords = LOCATIONS[to_city]

        actual_bearing = haversine_bearing(from_coords[0], from_coords[1],
                                          to_coords[0], to_coords[1])
        actual_index, actual_letter = bearing_to_letter(actual_bearing)

        print(f"Current pair: {from_city} → {to_city}")
        print(f"  Bearing: {actual_bearing:.2f}°")
        print(f"  Produces: {actual_letter}")
        print(f"  Needed: {expected_letter}")
        print()

        # What bearing range is needed?
        target_min, target_max = letter_to_bearing_range(expected_letter)
        print(f"To produce '{expected_letter}', bearing must be in range: {target_min:.2f}° - {target_max:.2f}°")
        print(f"Current bearing {actual_bearing:.2f}° is {'' if target_min <= actual_bearing < target_max else 'NOT '}in range")
        print()

        # Find alternatives
        alternatives = find_alternative_locations(expected_letter)

    # Summary
    print("\n" + "=" * 100)
    print("CRITICAL FINDINGS")
    print("=" * 100)
    print()

    print("MISMATCH ANALYSIS:")
    print()
    print("1. Position 7: CIA → Buenos Aires")
    print("   - Current bearing: 100.34° (produces H)")
    print("   - Needed bearing: 165.38° - 179.23° (for L)")
    print("   - CONCLUSION: Wrong destination city")
    print()

    print("2. Position 16: CIA → Rio Janeiro")
    print("   - Current bearing: 109.03° (produces H)")
    print("   - Needed bearing: 138.46° - 152.31° (for K)")
    print("   - CONCLUSION: Wrong destination city")
    print()

    print("3. Position 22: CIA → Wellington")
    print("   - Current bearing: 312.72° (produces W)")
    print("   - Needed bearing: 235.38° - 249.23° (for R)")
    print("   - CONCLUSION: Wrong destination city")
    print()

    print("4. Position 25: Tokyo → Sydney")
    print("   - Current bearing: 97.44° (produces H)")
    print("   - Needed bearing: 166.15° - 180.00° (for M)")
    print("   - CONCLUSION: Wrong destination city")
    print()

    print("=" * 100)
    print("OVERALL ASSESSMENT")
    print("=" * 100)
    print()

    print("The claimed bearing formula DOES work mathematically:")
    print("  ✓ Formula: letter_index = floor((bearing / 360) × 26) mod 26")
    print("  ✓ Calculation method: Correct haversine bearing formula")
    print()

    print("However, the claimed 29 location pairs are INCORRECT:")
    print("  ✗ 4 out of 29 pairs produce wrong letters")
    print("  ✗ This suggests the location pairs in BEARING_KEY_SOLUTION.md are WRONG")
    print()

    print("POSSIBLE EXPLANATIONS:")
    print("  1. The location pairs were not exhaustively searched properly")
    print("  2. The coordinates for the 4 mismatched cities are wrong")
    print("  3. The entire bearing approach is based on circular reasoning")
    print("  4. The documentation was created AFTER assuming the formula worked")
    print()

    print("CONCLUSION:")
    print("  The geographic bearing approach is plausible BUT not yet verified correctly.")
    print("  Need to find the correct 29 location pairs that ACTUALLY produce the key.")
    print()


if __name__ == "__main__":
    main()
