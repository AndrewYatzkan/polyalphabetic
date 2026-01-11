#!/usr/bin/env python3
"""
EXHAUSTIVE SEARCH: Find the correct 29 location pairs that produce K4 key

This script searches through all possible location pairs to find a sequence
that produces DIJJQELYOIECBAQKVAATCRDUMPABT
"""

import math
from itertools import product
from typing import List, Tuple, Dict, Set

TARGET_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

LOCATIONS = {
    "CIA": (38.9517, -77.1467),
    "Berlin_Clock": (52.5200, 13.4050),
    "Brandenburg_Gate": (52.5163, 13.3777),
    "Wall_Memorial": (52.5397, 13.3896),
    "Reichstag": (52.5186, 13.3755),
    "Dubai": (25.2048, 55.2708),
    "Istanbul": (41.0082, 28.9784),
    "Moscow": (55.7558, 37.6173),
    "Valley_Kings": (25.7402, 32.6014),
    "Mexico_City": (19.4326, -99.1332),
    "Bangkok": (13.7563, 100.5018),
    "Rio": (22.9068, -43.1729),
    "Buenos_Aires": (34.6037, -58.3816),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
    "Sydney": (33.8688, 151.2093),
    "Wellington": (41.2865, 174.7762),
    "Athens": (37.9838, 23.7275),
    "Cairo": (30.0444, 31.2357),
}


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing."""
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlon = lon2_rad - lon1_rad
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def bearing_to_letter(b: float) -> str:
    """Convert bearing to letter."""
    return chr(ord('A') + (math.floor((b / 360.0) * 26) % 26))


def main():
    print("=" * 100)
    print("SEARCHING FOR CORRECT 29 LOCATION PAIRS")
    print("=" * 100)
    print()

    # Pre-calculate all possible bearings
    print("Calculating all possible bearings...")
    bearing_map = {}

    for from_city in LOCATIONS:
        for to_city in LOCATIONS:
            if from_city == to_city:
                continue
            b = bearing(LOCATIONS[from_city][0], LOCATIONS[from_city][1],
                       LOCATIONS[to_city][0], LOCATIONS[to_city][1])
            letter = bearing_to_letter(b)

            if letter not in bearing_map:
                bearing_map[letter] = []
            bearing_map[letter].append((from_city, to_city, b))

    print(f"Calculated {sum(len(v) for v in bearing_map.values())} possible pairs")
    print()

    # Show options for each letter
    print("AVAILABLE PAIRS FOR EACH LETTER:")
    print("-" * 100)
    print()

    for letter in sorted(bearing_map.keys()):
        pairs = bearing_map[letter]
        print(f"Letter '{letter}': {len(pairs)} options")
        if len(pairs) <= 5:
            for from_city, to_city, b in pairs:
                print(f"  {from_city:20s} → {to_city:20s} ({b:7.2f}°)")
        else:
            for from_city, to_city, b in pairs[:3]:
                print(f"  {from_city:20s} → {to_city:20s} ({b:7.2f}°)")
            print(f"  ... and {len(pairs) - 3} more")
        print()

    # Check if all letters in target key have options
    print("FEASIBILITY CHECK:")
    print("-" * 100)
    print()

    possible = True
    for i, letter in enumerate(TARGET_KEY, 1):
        if letter not in bearing_map:
            print(f"✗ Position {i}: No pairs found for '{letter}'")
            possible = False
        else:
            count = len(bearing_map[letter])
            print(f"✓ Position {i}: '{letter}' has {count} options")

    print()

    if not possible:
        print("CONCLUSION: The key CANNOT be produced from available bearings.")
        print()
        print("This suggests either:")
        print("  1. Missing locations (not in current database)")
        print("  2. Different coordinate system")
        print("  3. Different bearing calculation method")
        print("  4. The bearing approach is fundamentally flawed")
        return

    # Try greedy search (just to show feasibility)
    print("=" * 100)
    print("GREEDY SEARCH ATTEMPT")
    print("=" * 100)
    print()

    solution = []
    used_pairs = set()

    for target_letter in TARGET_KEY:
        found = False

        # Try to find a pair that hasn't been used
        for from_city, to_city, b in bearing_map[target_letter]:
            pair_key = (from_city, to_city)

            if pair_key not in used_pairs:
                solution.append(pair_key)
                used_pairs.add(pair_key)
                found = True
                break

        # If no unused pair, use any pair (allowing repeats)
        if not found:
            from_city, to_city, b = bearing_map[target_letter][0]
            solution.append((from_city, to_city))
            found = True

        if not found:
            print(f"✗ Could not find pair for '{target_letter}'")
            break

    if len(solution) == 29:
        print("✓ Found a complete solution (using greedy search):")
        print()

        for i, (from_city, to_city) in enumerate(solution, 1):
            b = bearing(LOCATIONS[from_city][0], LOCATIONS[from_city][1],
                       LOCATIONS[to_city][0], LOCATIONS[to_city][1])
            letter = bearing_to_letter(b)
            print(f"Pos {i:2d}: {from_city:20s} → {to_city:20s} | Bearing {b:7.2f}° = {letter}")

        print()
        result_key = "".join([bearing_to_letter(bearing(LOCATIONS[f][0], LOCATIONS[f][1],
                                                       LOCATIONS[t][0], LOCATIONS[t][1]))
                             for f, t in solution])
        print(f"Resulting key: {result_key}")
        print(f"Expected key:  {TARGET_KEY}")
        print(f"Match: {'✓' if result_key == TARGET_KEY else '✗'}")
    else:
        print(f"Could not find complete solution (got {len(solution)}/29)")

    print()
    print("=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()
