#!/usr/bin/env python3
"""
Bearing-to-Letter Hypothesis Test for KRYPTOS K4 Key
=====================================================

Hypothesis: The K4 key (DIJJQELYOIECBAQKVAATCRDUMPABT - 29 letters) is derived
from bearings between significant geographic locations.

Formula: letter_index = (bearing / 360) × 26 mod 26
- bearing is in degrees (0-360)
- result is converted to A-Z (0-25)

Testing strategy:
1. Calculate bearings between CIA HQ and major cities/time zones
2. Test Berlin-centric bearings
3. Test chain of bearings: CIA → Berlin → Egypt → ...
4. Test internal Berlin landmark bearings
"""

import math
from itertools import combinations, permutations

# Target K4 key
TARGET_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Geographic coordinates (latitude, longitude in decimal degrees)
LOCATIONS = {
    "CIA_HQ": (38.9519, -77.1467),  # Langley, Virginia
    "Berlin_Weltzeituhr": (52.5200, 13.4050),  # World Clock (Alexanderplatz)
    "Berlin_Wall_Memorial": (52.5397, 13.3896),  # Berlin Wall Memorial
    "Berlin_Brandenburg_Gate": (52.5163, 13.3777),  # Brandenburg Gate
    "Berlin_Reichstag": (52.5186, 13.3755),  # Reichstag
    "Valley_of_Kings": (25.7402, 32.6014),  # Egypt
    "Cairo": (30.0444, 31.2357),  # Egypt
    "Moscow": (55.7558, 37.6173),  # Russia
    "London": (51.5074, -0.1278),  # England
    "Paris": (48.8566, 2.3522),  # France
    "Rome": (41.9028, 12.4964),  # Italy
    "Tokyo": (35.6762, 139.6503),  # Japan
    "Sydney": (-33.8688, 151.2093),  # Australia
    "Beijing": (39.9042, 116.4074),  # China
    "Dubai": (25.2048, 55.2708),  # UAE
    "Bangkok": (13.7563, 100.5018),  # Thailand
    "Singapore": (1.3521, 103.8198),  # Singapore
    "Istanbul": (41.0082, 28.9784),  # Turkey
    "Athens": (37.9838, 23.7275),  # Greece
    "Jerusalem": (31.7683, 35.2137),  # Israel
    "New_York": (40.7128, -74.0060),  # USA
    "Mexico_City": (19.4326, -99.1332),  # Mexico
    "Rio_Janeiro": (-22.9068, -43.1729),  # Brazil
    "Buenos_Aires": (-34.6037, -58.3816),  # Argentina
    "Wellington": (-41.2865, 174.7762),  # New Zealand
    "Anchor_Links": (52.5200, 13.4050),  # Berlin (alternative)
}


def haversine_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate bearing from point 1 to point 2.
    Returns bearing in degrees (0-360, where 0° is North).
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing = math.atan2(x, y)
    bearing_deg = math.degrees(bearing)

    # Normalize to 0-360
    if bearing_deg < 0:
        bearing_deg += 360

    return bearing_deg


def bearing_to_letter(bearing):
    """
    Convert bearing to letter using the formula:
    letter_index = (bearing / 360) × 26 mod 26
    """
    letter_index = int((bearing / 360.0) * 26) % 26
    return chr(ord('A') + letter_index)


def bearing_to_letter_with_mod(bearing):
    """
    Convert bearing to letter using modulo arithmetic:
    More robust version that handles various interpretations.
    """
    letter_index = int(bearing / 360.0 * 26) % 26
    return chr(ord('A') + letter_index)


def test_bearing_sequence(location_pairs, name=""):
    """
    Test a sequence of bearings between location pairs.
    location_pairs: list of tuples [(start_name, end_name), ...]
    """
    result_key = ""
    bearings = []

    for start, end in location_pairs:
        if start not in LOCATIONS or end not in LOCATIONS:
            return None, None, None

        lat1, lon1 = LOCATIONS[start]
        lat2, lon2 = LOCATIONS[end]
        bearing = haversine_bearing(lat1, lon1, lat2, lon2)
        letter = bearing_to_letter(bearing)
        result_key += letter
        bearings.append((start, end, bearing, letter))

    return result_key, bearings, name


def print_bearing_sequence(bearings, name=""):
    """Pretty print a bearing sequence."""
    print(f"\n{'='*80}")
    if name:
        print(f"Test: {name}")
    print(f"{'='*80}")

    result_key = ""
    for start, end, bearing, letter in bearings:
        result_key += letter
        print(f"{start:20} → {end:25} | Bearing: {bearing:7.2f}° | Letter: {letter}")

    print(f"{'='*80}")
    print(f"Result Key: {result_key}")
    print(f"Target Key: {TARGET_KEY}")
    print(f"Match: {result_key == TARGET_KEY}")

    # Character-by-character comparison
    if result_key != TARGET_KEY:
        matches = sum(1 for i, (r, t) in enumerate(zip(result_key, TARGET_KEY)) if r == t)
        print(f"Matches: {matches}/{len(TARGET_KEY)} characters")

        # Show differences
        print("\nDifferences:")
        for i, (r, t) in enumerate(zip(result_key, TARGET_KEY)):
            if r != t:
                print(f"  Position {i}: got '{r}', expected '{t}'")

    return result_key


def test_cia_to_world_cities():
    """Test bearings from CIA HQ to major world cities."""
    print("\n" + "="*80)
    print("TEST 1: CIA HQ to World Cities (24 cities)")
    print("="*80)

    cities = [
        "Berlin_Weltzeituhr", "Moscow", "London", "Paris", "Rome", "Istanbul",
        "Athens", "Jerusalem", "Cairo", "Dubai", "Bangkok", "Singapore",
        "Beijing", "Tokyo", "Sydney", "Wellington", "Rio_Janeiro", "Buenos_Aires",
        "Mexico_City", "New_York", "Valley_of_Kings", "Berlin_Wall_Memorial",
        "Berlin_Brandenburg_Gate", "Berlin_Reichstag"
    ]

    location_pairs = [("CIA_HQ", city) for city in cities]
    result_key, bearings, _ = test_bearing_sequence(location_pairs)

    if result_key:
        print_bearing_sequence(bearings, f"CIA to {len(cities)} cities")

        # Check for partial matches
        matches = sum(1 for i, (r, t) in enumerate(zip(result_key, TARGET_KEY)) if r == t)
        print(f"Exact character matches: {matches}/{len(TARGET_KEY)}")


def test_berlin_centric():
    """Test bearings from Berlin World Clock to various locations."""
    print("\n" + "="*80)
    print("TEST 2: Berlin Weltzeituhr to Various Locations")
    print("="*80)

    targets = [
        "CIA_HQ", "Moscow", "London", "Paris", "Rome", "Istanbul",
        "Athens", "Jerusalem", "Cairo", "Dubai", "Bangkok", "Singapore",
        "Beijing", "Tokyo", "Sydney", "Valley_of_Kings", "Wall_Memorial",
        "Berlin_Wall_Memorial", "Berlin_Brandenburg_Gate", "Berlin_Reichstag",
        "Rio_Janeiro", "Buenos_Aires", "Mexico_City", "New_York"
    ]

    location_pairs = [("Berlin_Weltzeituhr", target) for target in targets if target in LOCATIONS]
    result_key, bearings, _ = test_bearing_sequence(location_pairs)

    if result_key:
        print_bearing_sequence(bearings, f"Berlin to {len(location_pairs)} locations")


def test_chain_bearings():
    """Test chain of bearings: CIA → Berlin → Egypt → ..."""
    print("\n" + "="*80)
    print("TEST 3: Chain of Bearings (CIA → Berlin → Egypt → other cities)")
    print("="*80)

    # Build a chain that could produce 29 letters
    chain = [
        ("CIA_HQ", "Berlin_Weltzeituhr"),  # Should give D
        ("Berlin_Weltzeituhr", "Valley_of_Kings"),
        ("Valley_of_Kings", "Cairo"),
        ("Cairo", "Moscow"),
        ("Moscow", "London"),
        ("London", "Paris"),
        ("Paris", "Rome"),
        ("Rome", "Istanbul"),
        ("Istanbul", "Athens"),
        ("Athens", "Jerusalem"),
        ("Jerusalem", "Dubai"),
        ("Dubai", "Bangkok"),
        ("Bangkok", "Singapore"),
        ("Singapore", "Beijing"),
        ("Beijing", "Tokyo"),
        ("Tokyo", "Sydney"),
        ("Sydney", "Wellington"),
        ("Wellington", "Rio_Janeiro"),
        ("Rio_Janeiro", "Buenos_Aires"),
        ("Buenos_Aires", "Mexico_City"),
        ("Mexico_City", "New_York"),
        ("New_York", "Berlin_Wall_Memorial"),
        ("Berlin_Wall_Memorial", "Berlin_Brandenburg_Gate"),
        ("Berlin_Brandenburg_Gate", "Berlin_Reichstag"),
        ("Berlin_Reichstag", "CIA_HQ"),
        ("CIA_HQ", "Moscow"),
        ("Moscow", "Beijing"),
        ("Beijing", "Sydney"),
        ("Sydney", "London"),
    ]

    result_key, bearings, _ = test_bearing_sequence(chain[:29])  # Use first 29 for exact match

    if result_key:
        print_bearing_sequence(bearings, "Chain of 29 bearings")


def test_internal_berlin():
    """Test bearings within Berlin landmarks."""
    print("\n" + "="*80)
    print("TEST 4: Internal Berlin Landmarks")
    print("="*80)

    berlin_locations = [
        "Berlin_Weltzeituhr",
        "Berlin_Wall_Memorial",
        "Berlin_Brandenburg_Gate",
        "Berlin_Reichstag",
    ]

    # Test from Weltzeituhr to other Berlin locations
    location_pairs = [
        ("Berlin_Weltzeituhr", "Berlin_Wall_Memorial"),
        ("Berlin_Wall_Memorial", "Berlin_Brandenburg_Gate"),
        ("Berlin_Brandenburg_Gate", "Berlin_Reichstag"),
        ("Berlin_Reichstag", "Berlin_Weltzeituhr"),
    ]

    result_key, bearings, _ = test_bearing_sequence(location_pairs)

    if result_key:
        print_bearing_sequence(bearings, "Berlin landmarks chain")


def brute_force_search():
    """
    Attempt to find sequences that match the target key.
    This is computationally expensive but exhaustive for small sequences.
    """
    print("\n" + "="*80)
    print("TEST 5: Brute Force Search (limited)")
    print("="*80)

    location_names = list(LOCATIONS.keys())
    best_matches = []

    # Test combinations of starting locations with sequence extensions
    print(f"Testing sequences starting from CIA_HQ...")

    # Just test from CIA to all combinations for first few steps
    from itertools import combinations

    starts_with_cia = [("CIA_HQ", name) for name in location_names if name != "CIA_HQ"]

    # Test all first bearings
    print(f"\nFirst bearing from CIA_HQ:")
    for start, end in starts_with_cia[:10]:
        lat1, lon1 = LOCATIONS[start]
        lat2, lon2 = LOCATIONS[end]
        bearing = haversine_bearing(lat1, lon1, lat2, lon2)
        letter = bearing_to_letter(bearing)
        match = "✓" if letter == TARGET_KEY[0] else " "
        print(f"  {match} CIA_HQ → {end:25} | {bearing:7.2f}° | {letter} (need: {TARGET_KEY[0]})")


def test_reverse_engineering():
    """Try to work backwards from the target letters to needed bearings."""
    print("\n" + "="*80)
    print("TEST 6: Reverse Engineering - Required Bearings for Target Key")
    print("="*80)
    print(f"\nTarget key: {TARGET_KEY}")
    print(f"Key length: {len(TARGET_KEY)} letters\n")

    print("Required bearings for each letter (in degrees):")
    print(f"{'Letter':<8} {'Bearing Range':<20} {'Letter Index':<15}")
    print("-" * 50)

    for i, letter in enumerate(TARGET_KEY):
        letter_index = ord(letter) - ord('A')
        # bearing = letter_index / 26 * 360
        # But we need to account for modulo

        # Possible bearings that give this letter:
        possible_bearings = [letter_index / 26 * 360]

        for k in range(1, 3):
            test_bearing = (letter_index + 26 * k) / 26 * 360
            if 0 <= test_bearing <= 360:
                possible_bearings.append(test_bearing)

        print(f"{letter:<8} {str(possible_bearings):<20} {letter_index:<15}")

    print("\nNow testing if actual bearings match these values...")


def analyze_first_bearing():
    """Detailed analysis of the CIA→Berlin bearing (should be 44.42°)."""
    print("\n" + "="*80)
    print("VERIFICATION: CIA HQ → Berlin World Clock")
    print("="*80)

    lat1, lon1 = LOCATIONS["CIA_HQ"]
    lat2, lon2 = LOCATIONS["Berlin_Weltzeituhr"]

    bearing = haversine_bearing(lat1, lon1, lat2, lon2)
    letter = bearing_to_letter(bearing)

    print(f"CIA HQ:           {lat1}°N, {lon1}°W")
    print(f"Berlin Clock:     {lat2}°N, {lon2}°E")
    print(f"Bearing:          {bearing:.2f}°")
    print(f"Formula:          ({bearing:.2f} / 360) × 26 = {(bearing/360)*26:.4f}")
    print(f"Mod 26:           {int((bearing/360)*26) % 26}")
    print(f"Letter:           {letter}")
    print(f"Expected:         D")
    print(f"Match:            {'✓ YES' if letter == 'D' else '✗ NO'}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("KRYPTOS K4 BEARING-TO-LETTER HYPOTHESIS TEST")
    print("="*80)

    # First verify the CIA→Berlin example
    analyze_first_bearing()

    # Run all tests
    test_cia_to_world_cities()
    test_berlin_centric()
    test_chain_bearings()
    test_internal_berlin()
    test_reverse_engineering()
    brute_force_search()

    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
