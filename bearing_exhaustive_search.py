#!/usr/bin/env python3
"""
Exhaustive Search for Bearing-Based K4 Key Derivation
=====================================================

Strategy: Search for sequences of 29 location pairs that produce the exact target key.
Uses constraint satisfaction and optimization techniques.
"""

import math
import itertools
from collections import defaultdict

# Target K4 key
TARGET_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# Geographic coordinates
LOCATIONS = {
    "CIA_HQ": (38.9519, -77.1467),
    "Berlin_Weltzeituhr": (52.5200, 13.4050),
    "Berlin_Wall_Memorial": (52.5397, 13.3896),
    "Berlin_Brandenburg_Gate": (52.5163, 13.3777),
    "Berlin_Reichstag": (52.5186, 13.3755),
    "Valley_of_Kings": (25.7402, 32.6014),
    "Cairo": (30.0444, 31.2357),
    "Moscow": (55.7558, 37.6173),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Rome": (41.9028, 12.4964),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (-33.8688, 151.2093),
    "Beijing": (39.9042, 116.4074),
    "Dubai": (25.2048, 55.2708),
    "Bangkok": (13.7563, 100.5018),
    "Singapore": (1.3521, 103.8198),
    "Istanbul": (41.0082, 28.9784),
    "Athens": (37.9838, 23.7275),
    "Jerusalem": (31.7683, 35.2137),
    "New_York": (40.7128, -74.0060),
    "Mexico_City": (19.4326, -99.1332),
    "Rio_Janeiro": (-22.9068, -43.1729),
    "Buenos_Aires": (-34.6037, -58.3816),
    "Wellington": (-41.2865, 174.7762),
}


def haversine_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2 (0-360 degrees)."""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))

    bearing = math.atan2(x, y)
    bearing_deg = math.degrees(bearing)

    if bearing_deg < 0:
        bearing_deg += 360

    return bearing_deg


def bearing_to_letter(bearing):
    """Convert bearing to letter."""
    letter_index = int((bearing / 360.0) * 26) % 26
    return chr(ord('A') + letter_index)


def find_bearing_pairs_for_letter(target_letter):
    """Find all location pairs that produce a specific letter."""
    target_index = ord(target_letter) - ord('A')
    pairs = []

    for start_name in LOCATIONS:
        for end_name in LOCATIONS:
            if start_name == end_name:
                continue

            lat1, lon1 = LOCATIONS[start_name]
            lat2, lon2 = LOCATIONS[end_name]
            bearing = haversine_bearing(lat1, lon1, lat2, lon2)
            letter = bearing_to_letter(bearing)

            if letter == target_letter:
                pairs.append((start_name, end_name, bearing))

    return pairs


def analyze_letter_requirements():
    """Analyze which location pairs can produce each required letter."""
    print("\n" + "="*80)
    print("LETTER-TO-BEARING MAPPING ANALYSIS")
    print("="*80)

    for letter in sorted(set(TARGET_KEY)):
        pairs = find_bearing_pairs_for_letter(letter)
        count = len(pairs)

        print(f"\nLetter '{letter}': {count} possible pairs")
        if count <= 20:
            for start, end, bearing in pairs[:10]:
                print(f"  {start:25} → {end:25} | {bearing:7.2f}°")
            if count > 10:
                print(f"  ... and {count - 10} more")


def test_constrained_search():
    """
    Use constraint satisfaction: find location pairs for each letter,
    then find valid sequences.
    """
    print("\n" + "="*80)
    print("CONSTRAINT-BASED SEARCH")
    print("="*80)
    print(f"Target key: {TARGET_KEY} ({len(TARGET_KEY)} letters)")

    # Get all possible pairs for each position
    required_pairs = []
    for i, letter in enumerate(TARGET_KEY):
        pairs = find_bearing_pairs_for_letter(letter)
        required_pairs.append(pairs)
        print(f"Position {i:2d} ('{letter}'): {len(pairs):3d} possible pairs")

    # Find sequences where end location of step N = start location of step N+1
    print("\n" + "="*80)
    print("SEARCHING FOR VALID CHAINS...")
    print("="*80)

    def search_chain(position, current_end_location, chain):
        """Recursively search for valid chains."""
        if position == len(TARGET_KEY):
            # Found a complete chain!
            return chain

        pairs_for_this_position = required_pairs[position]

        for start, end, bearing in pairs_for_this_position:
            # Check if this pair connects properly
            if position == 0 or start == current_end_location:
                result = search_chain(
                    position + 1,
                    end,
                    chain + [(start, end, bearing)]
                )
                if result is not None:
                    return result

        return None

    # Try starting from each possible first pair
    first_letter = TARGET_KEY[0]
    first_pairs = find_bearing_pairs_for_letter(first_letter)

    solution = None
    for start, end, bearing in first_pairs:
        print(f"\nTrying initial pair: {start} → {end}")
        result = search_chain(1, end, [(start, end, bearing)])

        if result is not None:
            solution = result
            break

    if solution:
        print("\n" + "="*80)
        print("SOLUTION FOUND!")
        print("="*80)
        result_key = ""
        for i, (start, end, bearing) in enumerate(solution):
            letter = bearing_to_letter(bearing)
            result_key += letter
            print(f"{i+1:2d}. {start:25} → {end:25} | {bearing:7.2f}° | {letter}")

        print(f"\nResult Key: {result_key}")
        print(f"Target Key: {TARGET_KEY}")
        print(f"Match: {result_key == TARGET_KEY}")
    else:
        print("\nNo valid chain found with simple connectivity constraint.")


def test_flexible_routing():
    """
    Test if we can build chains allowing location reuse or skipping.
    """
    print("\n" + "="*80)
    print("FLEXIBLE ROUTING SEARCH (with location reuse)")
    print("="*80)

    def search_flexible(position, chain):
        """Search allowing any location pairs (no connectivity requirement)."""
        if position == len(TARGET_KEY):
            return chain

        letter = TARGET_KEY[position]
        pairs = find_bearing_pairs_for_letter(letter)

        for start, end, bearing in pairs:
            result = search_flexible(position + 1, chain + [(start, end, bearing)])
            if result is not None:
                return result

        return None

    print("Searching for any sequence of 29 pairs (no connectivity constraints)...")
    solution = search_flexible(0, [])

    if solution:
        print("\n" + "="*80)
        print("FLEXIBLE SOLUTION FOUND!")
        print("="*80)

        result_key = ""
        for i, (start, end, bearing) in enumerate(solution):
            letter = bearing_to_letter(bearing)
            result_key += letter
            print(f"{i+1:2d}. {start:25} → {end:25} | {bearing:7.2f}° | {letter}")

        print(f"\nResult Key: {result_key}")
        print(f"Target Key: {TARGET_KEY}")
        print(f"Match: {result_key == TARGET_KEY}")
    else:
        print("No solution found.")


def test_alternative_formula():
    """
    Test alternative interpretations of the bearing-to-letter formula.
    """
    print("\n" + "="*80)
    print("TESTING ALTERNATIVE FORMULAS")
    print("="*80)

    lat1, lon1 = LOCATIONS["CIA_HQ"]
    lat2, lon2 = LOCATIONS["Berlin_Weltzeituhr"]
    bearing = haversine_bearing(lat1, lon1, lat2, lon2)

    print(f"\nBearing CIA→Berlin: {bearing:.4f}°")
    print(f"Target letter: D (index 3)\n")

    # Try different formulas
    formulas = [
        ("(bearing / 360) × 26 mod 26", lambda b: int((b / 360) * 26) % 26),
        ("round((bearing / 360) × 26) mod 26", lambda b: round((b / 360) * 26) % 26),
        ("(bearing / 14) mod 26", lambda b: int(b / 14) % 26),
        ("(bearing / 13.8) mod 26", lambda b: int(b / 13.8) % 26),
        ("(bearing / 13.846) mod 26", lambda b: int(b / 13.846) % 26),
        ("(bearing / 18) mod 26", lambda b: int(b / 18) % 26),
        ("round(bearing / 13.846) mod 26", lambda b: round(b / 13.846) % 26),
    ]

    for name, formula in formulas:
        try:
            result = formula(bearing)
            letter = chr(ord('A') + result)
            match = "✓" if letter == 'D' else " "
            print(f"{match} {name:<40} = {result:2d} → {letter}")
        except:
            print(f"  {name:<40} ERROR")


def test_pattern_analysis():
    """Analyze patterns in the target key."""
    print("\n" + "="*80)
    print("TARGET KEY PATTERN ANALYSIS")
    print("="*80)

    key = TARGET_KEY

    print(f"Key: {key}")
    print(f"Length: {len(key)}")

    # Frequency analysis
    from collections import Counter
    freq = Counter(key)
    print(f"\nLetter frequencies:")
    for letter in sorted(freq.keys()):
        print(f"  {letter}: {freq[letter]}")

    # Look for repeating substrings
    print(f"\nRepeating patterns:")
    for length in range(2, 6):
        substrings = defaultdict(list)
        for i in range(len(key) - length + 1):
            sub = key[i:i+length]
            substrings[sub].append(i)

        repeats = {s: pos for s, pos in substrings.items() if len(pos) > 1}
        if repeats:
            for sub, positions in repeats.items():
                print(f"  '{sub}' at positions: {positions}")


def test_incremental_bearing():
    """
    Test if bearings increment in a pattern.
    """
    print("\n" + "="*80)
    print("INCREMENTAL BEARING HYPOTHESIS")
    print("="*80)

    # Get required bearings for each letter in key
    required_bearings = []
    for letter in TARGET_KEY:
        letter_index = ord(letter) - ord('A')
        # Primary bearing
        bearing = (letter_index / 26) * 360
        required_bearings.append(bearing)

    print(f"Required bearings (raw):")
    for i, b in enumerate(required_bearings[:10]):
        print(f"  {i}: {b:.2f}°")

    # Calculate differences
    print(f"\nBearing differences:")
    for i in range(min(10, len(required_bearings) - 1)):
        diff = required_bearings[i+1] - required_bearings[i]
        print(f"  {i}→{i+1}: {diff:.2f}°")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("BEARING-BASED K4 KEY: EXHAUSTIVE SEARCH")
    print("="*80)

    analyze_letter_requirements()
    test_alternative_formula()
    test_pattern_analysis()
    test_incremental_bearing()
    test_constrained_search()
    test_flexible_routing()

    print("\n" + "="*80)
    print("SEARCH COMPLETE")
    print("="*80)
