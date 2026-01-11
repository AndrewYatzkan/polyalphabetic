#!/usr/bin/env python3
"""
COMPREHENSIVE VERIFICATION: Test ALL 29 location pairs from BEARING_KEY_SOLUTION.md

This script verifies whether the claimed 29 location pairs actually produce
the K4 key DIJJQELYOIECBAQKVAATCRDUMPABT using the bearing formula.

SUSPICIOUS ELEMENTS TO CHECK:
1. Multiple identical location pairs (e.g., CIA→Bangkok used 4 times)
2. Whether the formula actually works for ALL 29 positions
3. Are there any discrepancies between claimed and calculated bearings?
"""

import math
from typing import Tuple, Dict, List

# K4 key to produce
TARGET_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# All coordinates (verified from documentation)
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
}

# The 29 claimed location pairs from BEARING_KEY_SOLUTION.md
CLAIMED_PAIRS = [
    ("CIA_HQ", "Berlin_Weltzeituhr", "D"),
    ("Berlin_Weltzeituhr", "Dubai", "I"),
    ("Berlin_Weltzeituhr", "Istanbul", "J"),
    ("Berlin_Weltzeituhr", "Istanbul", "J"),
    ("CIA_HQ", "Mexico_City", "Q"),
    ("CIA_HQ", "Valley_of_Kings", "E"),
    ("CIA_HQ", "Buenos_Aires", "L"),
    ("Berlin_Weltzeituhr", "Berlin_Wall_Memorial", "Y"),
    ("Berlin_Wall_Memorial", "Berlin_Brandenburg_Gate", "O"),
    ("Berlin_Weltzeituhr", "Dubai", "I"),
    ("CIA_HQ", "Valley_of_Kings", "E"),
    ("CIA_HQ", "Moscow", "C"),
    ("Berlin_Brandenburg_Gate", "Berlin_Wall_Memorial", "B"),
    ("CIA_HQ", "Bangkok", "A"),
    ("CIA_HQ", "Mexico_City", "Q"),
    ("CIA_HQ", "Rio_Janeiro", "K"),
    ("Berlin_Weltzeituhr", "CIA_HQ", "V"),
    ("CIA_HQ", "Bangkok", "A"),
    ("CIA_HQ", "Bangkok", "A"),
    ("Berlin_Weltzeituhr", "Berlin_Reichstag", "T"),
    ("CIA_HQ", "Moscow", "C"),
    ("CIA_HQ", "Wellington", "R"),
    ("CIA_HQ", "Berlin_Weltzeituhr", "D"),
    ("London", "CIA_HQ", "U"),
    ("Tokyo", "Sydney", "M"),
    ("Moscow", "Athens", "P"),
    ("CIA_HQ", "Bangkok", "A"),
    ("Berlin_Brandenburg_Gate", "Berlin_Wall_Memorial", "B"),
    ("Berlin_Weltzeituhr", "Berlin_Reichstag", "T"),
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


def verify_all_pairs():
    """Verify all 29 claimed pairs."""

    print("=" * 100)
    print("VERIFICATION OF ALL 29 LOCATION PAIRS")
    print("=" * 100)
    print()

    # Check if all locations exist
    print("STEP 1: VERIFYING LOCATION DATA")
    print("-" * 100)

    for from_city, to_city, expected_letter in CLAIMED_PAIRS:
        if from_city not in LOCATIONS:
            print(f"ERROR: Location '{from_city}' not found in database")
        if to_city not in LOCATIONS:
            print(f"ERROR: Location '{to_city}' not found in database")

    print(f"✓ All {len(set(loc for pair in CLAIMED_PAIRS for loc in [pair[0], pair[1]]))} locations verified")
    print()

    # Calculate and verify each pair
    print("STEP 2: CALCULATING BEARINGS AND VERIFYING LETTERS")
    print("-" * 100)
    print()

    matches = 0
    mismatches = 0
    results = []

    for i, (from_city, to_city, expected_letter) in enumerate(CLAIMED_PAIRS, 1):
        from_coords = LOCATIONS[from_city]
        to_coords = LOCATIONS[to_city]

        bearing = haversine_bearing(from_coords[0], from_coords[1],
                                   to_coords[0], to_coords[1])
        index, calculated_letter = bearing_to_letter(bearing)

        match = calculated_letter == expected_letter
        if match:
            matches += 1
            status = "✓"
        else:
            mismatches += 1
            status = "✗"

        results.append({
            "position": i,
            "from": from_city,
            "to": to_city,
            "bearing": bearing,
            "calculated_letter": calculated_letter,
            "expected_letter": expected_letter,
            "match": match,
            "status": status
        })

        print(f"Pos {i:2d}: {from_city:25s} → {to_city:25s} | "
              f"Bearing {bearing:7.2f}° | {calculated_letter} (exp: {expected_letter}) {status}")

    print()
    print("-" * 100)
    print(f"RESULTS: {matches} matches, {mismatches} mismatches out of 29")
    print(f"Success rate: {100.0 * matches / 29:.1f}%")
    print()

    # Construct the generated key
    generated_key = "".join([r["calculated_letter"] for r in results])

    print("Generated key: ", generated_key)
    print("Expected key:  ", TARGET_KEY)
    print()

    # Character-by-character comparison
    print("STEP 3: CHARACTER-BY-CHARACTER COMPARISON")
    print("-" * 100)
    print()

    all_match = generated_key == TARGET_KEY

    if all_match:
        print("✓✓✓ PERFECT MATCH - All 29 letters match exactly!")
        print()
    else:
        print("✗ MISMATCH DETECTED - Key does not match")
        print()
        print("Position | Generated | Expected | Match")
        print("-" * 50)
        for i, (gen_char, exp_char) in enumerate(zip(generated_key, TARGET_KEY), 1):
            match = "✓" if gen_char == exp_char else "✗"
            print(f"{i:8d} | {gen_char:9s} | {exp_char:8s} | {match}")
        print()

    # Identify any duplicate pairs
    print("STEP 4: DUPLICATE LOCATION PAIRS ANALYSIS")
    print("-" * 100)
    print()

    pair_count = {}
    for from_city, to_city, _ in CLAIMED_PAIRS:
        pair_key = (from_city, to_city)
        pair_count[pair_key] = pair_count.get(pair_key, 0) + 1

    duplicates = {pair: count for pair, count in pair_count.items() if count > 1}

    if duplicates:
        print(f"Found {len(duplicates)} pairs used multiple times:")
        print()
        for (from_city, to_city), count in sorted(duplicates.items(), key=lambda x: -x[1]):
            bearing = haversine_bearing(LOCATIONS[from_city][0], LOCATIONS[from_city][1],
                                       LOCATIONS[to_city][0], LOCATIONS[to_city][1])
            _, letter = bearing_to_letter(bearing)
            print(f"  {from_city:25s} → {to_city:25s}: used {count} times (bearing {bearing:.2f}°, letter {letter})")
        print()
        print(f"Total unique pairs: {len(pair_count)}")
        print(f"Total positions in key: {len(CLAIMED_PAIRS)}")
        print()

    # Summary
    print("=" * 100)
    print("FINAL VERDICT")
    print("=" * 100)
    print()

    if all_match:
        print("✓✓✓ CLAIM VERIFIED ✓✓✓")
        print()
        print("The geographic bearing formula DOES produce the K4 key.")
        print(f"Formula: letter_index = floor((bearing / 360) × 26) mod 26")
        print(f"All 29 location pairs verified successfully.")
        print()
    else:
        print("✗✗✗ CLAIM REJECTED ✗✗✗")
        print()
        print("The geographic bearing formula DOES NOT produce the K4 key.")
        print(f"Mismatches found: {mismatches} out of 29")
        print()

    return all_match, matches, mismatches


if __name__ == "__main__":
    all_match, matches, mismatches = verify_all_pairs()
