#!/usr/bin/env python3
"""
RIGOROUS VERIFICATION of the bearing-to-letter K4 key derivation claim.

This script implements proper geographic bearing calculation and tests
whether the claimed formula actually produces the K4 key.

SKEPTICAL APPROACH: We will verify everything independently.
"""

import math
from typing import Tuple, List

# K4 ciphertext and plaintext
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVYSGBNNTFBPBGFABFCVDXLOXKXOHSKNUFQHTQELYOIECBAQKVAATCRDUMPABT"
K4_PLAINTEXT = "UNDERNEATHTHEOBJECTFORABOUTTHIRTYTHREEFEETESTOBKRUOXOGHULBSOLIFBBWFLRVYSGBNNTFBPBGFABFCVD"

# Claimed K4 key
CLAIMED_K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Known coordinates (must be verified)
COORDINATES = {
    "CIA_HQ": (38.9517, -77.1467),
    "Berlin_Weltzeituhr": (52.5200, 13.4050),
    "Valley_of_Kings": (25.7402, 32.6014),
    "Cairo": (30.0444, 31.2357),
    "Dubai": (25.2048, 55.2708),
    "Istanbul": (41.0082, 28.9784),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Rome": (41.9028, 12.4964),
    "Moscow": (55.7558, 37.6173),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (33.8688, 151.2093),
    "Los_Angeles": (34.0522, -118.2437),
    "New_York": (40.7128, -74.0060),
    "Mexico_City": (19.4326, -99.1332),
    "Rio_de_Janeiro": (22.9068, -43.1729),
    "Athens": (37.9838, 23.7275),
    "Jerusalem": (31.7683, 35.2137),
    "Shanghai": (31.2304, 121.4737),
    "Johannesburg": (26.2023, 28.0436),
    "Buenos_Aires": (34.6037, -58.3816),
    "Bangkok": (13.7563, 100.5018),
    "Singapore": (1.3521, 103.8198),
    "Hong_Kong": (22.3193, 114.1694),
    "Mumbai": (19.0760, 72.8777),
    "Istanbul_Historic": (41.0057, 28.9775),
}


def haversine_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate initial bearing from point 1 to point 2 using haversine formula.

    Returns bearing in degrees (0-360).
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate differences
    dlon = lon2_rad - lon1_rad

    # Calculate bearing
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing_rad = math.atan2(y, x)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to 0-360
    bearing_deg = (bearing_deg + 360) % 360

    return bearing_deg


def bearing_to_letter(bearing: float) -> Tuple[int, str]:
    """
    Convert bearing to letter using the claimed formula:
    letter_index = floor((bearing / 360) × 26) mod 26
    """
    index = math.floor((bearing / 360.0) * 26) % 26
    letter = chr(ord('A') + index)
    return index, letter


def test_single_pair(from_city: str, from_coords: Tuple[float, float],
                     to_city: str, to_coords: Tuple[float, float],
                     expected_letter: str) -> dict:
    """
    Test if a bearing pair produces the expected letter.
    """
    bearing = haversine_bearing(from_coords[0], from_coords[1],
                               to_coords[0], to_coords[1])
    index, letter = bearing_to_letter(bearing)

    match = letter == expected_letter

    return {
        "from": from_city,
        "to": to_city,
        "bearing": bearing,
        "calculated_index": index,
        "calculated_letter": letter,
        "expected_letter": expected_letter,
        "match": match,
        "formula_result": f"floor(({bearing:.2f}/360) × 26) = {index}"
    }


def main():
    print("=" * 80)
    print("RIGOROUS BEARING-TO-LETTER FORMULA VERIFICATION")
    print("=" * 80)
    print()

    # Test 1: CIA to Berlin (should produce 'D')
    print("TEST 1: CIA HQ → Berlin Weltzeituhr")
    print("-" * 80)

    result = test_single_pair(
        "CIA_HQ", COORDINATES["CIA_HQ"],
        "Berlin_Weltzeituhr", COORDINATES["Berlin_Weltzeituhr"],
        "D"  # Expected first letter of key
    )

    print(f"From: {result['from']} {COORDINATES['CIA_HQ']}")
    print(f"To:   {result['to']} {COORDINATES['Berlin_Weltzeituhr']}")
    print(f"Bearing: {result['bearing']:.4f}°")
    print(f"Formula: {result['formula_result']}")
    print(f"Calculated letter: {result['calculated_letter']} (index {result['calculated_index']})")
    print(f"Expected letter:   {result['expected_letter']}")
    print(f"MATCH: {'✓ YES' if result['match'] else '✗ NO'}")
    print()

    if not result['match']:
        print("CRITICAL FINDING: Formula does NOT produce expected letter D")
        print(f"Distance from expected: {abs(ord(result['calculated_letter']) - ord(result['expected_letter']))} positions")
        print()

    # Test 2: Berlin to Dubai (should produce 'I')
    print("TEST 2: Berlin Weltzeituhr → Dubai")
    print("-" * 80)

    result2 = test_single_pair(
        "Berlin_Weltzeituhr", COORDINATES["Berlin_Weltzeituhr"],
        "Dubai", COORDINATES["Dubai"],
        "I"  # Expected second letter
    )

    print(f"From: {result2['from']} {COORDINATES['Berlin_Weltzeituhr']}")
    print(f"To:   {result2['to']} {COORDINATES['Dubai']}")
    print(f"Bearing: {result2['bearing']:.4f}°")
    print(f"Formula: {result2['formula_result']}")
    print(f"Calculated letter: {result2['calculated_letter']} (index {result2['calculated_index']})")
    print(f"Expected letter:   {result2['expected_letter']}")
    print(f"MATCH: {'✓ YES' if result2['match'] else '✗ NO'}")
    print()

    # Test 3: Detailed bearing analysis for CIA to Berlin
    print("TEST 3: DETAILED BEARING ANALYSIS - CIA to Berlin")
    print("-" * 80)

    lat1, lon1 = COORDINATES["CIA_HQ"]
    lat2, lon2 = COORDINATES["Berlin_Weltzeituhr"]
    bearing = haversine_bearing(lat1, lon1, lat2, lon2)

    print(f"Point 1 (CIA): {lat1}°N, {abs(lon1)}°W")
    print(f"Point 2 (Berlin): {lat2}°N, {lon2}°E")
    print()
    print(f"Calculated bearing: {bearing:.4f}°")
    print()

    # Step-by-step formula
    step1 = bearing / 360.0
    step2 = step1 * 26
    step3 = math.floor(step2)
    step4 = step3 % 26

    print("Step-by-step formula execution:")
    print(f"  1. bearing / 360 = {bearing:.4f} / 360 = {step1:.6f}")
    print(f"  2. × 26 = {step1:.6f} × 26 = {step2:.4f}")
    print(f"  3. floor(...) = {step3}")
    print(f"  4. mod 26 = {step4}")
    print(f"  5. Result letter: {chr(ord('A') + step4)}")
    print()

    claimed_value = 44.42
    print(f"Claimed bearing in docs: {claimed_value}°")
    print(f"Actual calculated bearing: {bearing:.4f}°")
    print(f"Difference: {abs(bearing - claimed_value):.4f}°")
    print()

    # What bearing would produce 'D'?
    # D = index 3
    # 3 = floor((bearing / 360) × 26)
    # So: 3 <= (bearing / 360) × 26 < 4
    # So: 3/26 × 360 <= bearing < 4/26 × 360
    # So: 41.54° <= bearing < 55.38°

    min_bearing_for_d = (3 / 26) * 360
    max_bearing_for_d = (4 / 26) * 360

    print(f"To produce 'D' (index 3), bearing must be in range:")
    print(f"  {min_bearing_for_d:.2f}° ≤ bearing < {max_bearing_for_d:.2f}°")
    print(f"Actual bearing {bearing:.4f}° is {'IN' if min_bearing_for_d <= bearing < max_bearing_for_d else 'OUTSIDE'} this range")
    print()

    # Test 4: Compare claimed coordinates
    print("TEST 4: VERIFICATION OF CLAIMED COORDINATES")
    print("-" * 80)

    # These are the coordinates claimed in documentation
    claimed_coords = {
        "CIA_HQ": (38.9517, -77.1467),
        "Berlin": (52.5200, 13.4050),
    }

    actual_coords = {
        "CIA_HQ": COORDINATES["CIA_HQ"],
        "Berlin_Weltzeituhr": COORDINATES["Berlin_Weltzeituhr"],
    }

    print("Checking coordinates match...")
    print(f"CIA HQ - Claimed: {claimed_coords['CIA_HQ']}, Actual: {actual_coords['CIA_HQ']}")
    print(f"Berlin - Claimed: {claimed_coords['Berlin']}, Actual: {actual_coords['Berlin_Weltzeituhr']}")
    print()

    # Test 5: Try multiple bearing interpretations
    print("TEST 5: TESTING ALTERNATIVE BEARING FORMULAS")
    print("-" * 80)

    lat1, lon1 = COORDINATES["CIA_HQ"]
    lat2, lon2 = COORDINATES["Berlin_Weltzeituhr"]

    # Method 1: Haversine (standard)
    bearing1 = haversine_bearing(lat1, lon1, lat2, lon2)
    idx1, let1 = bearing_to_letter(bearing1)

    # Method 2: Using raw atan2 without intermediate calculations
    dlon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing2_rad = math.atan2(y, x)
    bearing2 = (math.degrees(bearing2_rad) + 360) % 360
    idx2, let2 = bearing_to_letter(bearing2)

    print(f"Method 1 (Haversine): {bearing1:.4f}° → {let1} (index {idx1})")
    print(f"Method 2 (atan2 direct): {bearing2:.4f}° → {let2} (index {idx2})")
    print()

    # Method 3: What if we use absolute difference in longitude?
    simple_bearing = abs(lon2 - lon1) * 100  # Arbitrary scaling
    idx3, let3 = bearing_to_letter(simple_bearing % 360)
    print(f"Method 3 (Raw lon diff scaled): {(simple_bearing % 360):.4f}° → {let3}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY OF FINDINGS")
    print("=" * 80)
    print()

    index, letter = bearing_to_letter(bearing)

    if bearing < min_bearing_for_d or bearing >= max_bearing_for_d:
        print("❌ BEARING FORMULA DOES NOT PRODUCE EXPECTED 'D'")
        print()
        print("Actual bearing calculation shows:")
        print(f"  CIA → Berlin = {bearing:.4f}°")
        print(f"  This produces letter '{letter}' (index {index})")
        print(f"  NOT 'D' as claimed")
        print()
        print("POSSIBLE EXPLANATIONS:")
        print("  1. Different coordinate data was used")
        print("  2. Different bearing calculation method")
        print("  3. The bearing values in docs are from a different location pair")
        print("  4. The formula is correct but documentation is wrong")
        print("  5. The entire bearing approach is incorrect")
        print()
    else:
        print("✓ BEARING FORMULA PRODUCES 'D' AS EXPECTED")
        print()

    print("CRITICAL ISSUE: Need to find which location pairs actually produce")
    print("the key DIJJQELYOIECBAQKVAATCRDUMPABT")
    print()
    print("The documentation claims 100% match, but the calculation shows:")
    print(f"  - Actual bearing CIA→Berlin: {bearing:.4f}°")
    print(f"  - Letter produced: {letter}")
    print(f"  - Expected letter: D")
    print()

    # Test what bearings would be needed
    print("=" * 80)
    print("REVERSE ENGINEERING: What bearings produce the K4 key?")
    print("=" * 80)
    print()

    for i, expected_letter in enumerate(CLAIMED_K4_KEY):
        index = ord(expected_letter) - ord('A')
        # bearing must satisfy: index = floor((bearing/360) × 26)
        min_bearing = (index / 26) * 360
        max_bearing = ((index + 1) / 26) * 360
        print(f"Letter {i+1}: {expected_letter} (index {index}) requires bearing: {min_bearing:.2f}° - {max_bearing:.2f}°")

    print()
    print("Now we need to find which location pairs actually produce these bearings.")


if __name__ == "__main__":
    main()
