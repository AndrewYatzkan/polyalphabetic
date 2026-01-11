#!/usr/bin/env python3
"""
BERLIN CLOCK HYPOTHESIS
Investigating if Gap3 and Gap4 encode Berlin Clock positions or angles
"""

import math

GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

# Berlin Clock (Weltzeituhr) details:
# - 24-hour clock face
# - 148 cities displayed
# - Seconds: 60 positions
# - Minutes: 60 positions  
# - Hours: 24 positions (or can think as 360°/24 = 15° per hour)

def letter_value(letter):
    """A=1, B=2, ..., Z=26"""
    return ord(letter.upper()) - ord('A') + 1

def letter_to_angle_360(letter):
    """Convert letter to angle 0-360"""
    val = letter_value(letter)
    return ((val - 1) * 360 / 26) % 360

def letter_to_time_24h(letter):
    """Convert letter to 24-hour time value"""
    return ((letter_value(letter) - 1) % 24)

def letter_to_degrees_dms(letter):
    """Convert letter to degree minute second format (0-90)"""
    val = letter_value(letter)
    total_seconds = val * 240  # scale 1-26 to some range
    degrees = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return degrees, minutes, seconds

print("=" * 80)
print("BERLIN CLOCK HYPOTHESIS ANALYSIS")
print("=" * 80)

print("\n[ANALYSIS 1] ANGLES AND BEARINGS")
print("-" * 80)

print(f"\nGap3 ({GAP3}) as compass bearings (0-360°):")
gap3_angles = [letter_to_angle_360(c) for c in GAP3]
for i, c in enumerate(GAP3):
    print(f"  {c} → {gap3_angles[i]:6.2f}°")

print(f"\nGap4 ({GAP4}) as compass bearings (0-360°):")
gap4_angles = [letter_to_angle_360(c) for c in GAP4]
for i, c in enumerate(GAP4):
    print(f"  {c} → {gap4_angles[i]:6.2f}°")

# Check for coordinate patterns
print("\n[ANALYSIS 2] COORDINATE PAIRS (LATITUDE/LONGITUDE STYLE)")
print("-" * 80)

# Treat pairs as coordinates
print(f"\nGap3 as 4 coordinate pairs + 1 extra:")
for i in range(0, 9, 2):
    if i+1 < 9:
        lat = gap3_angles[i]
        lon = gap3_angles[i+1]
        print(f"  Pair {i//2 + 1}: {GAP3[i]}{GAP3[i+1]} → ({lat:6.2f}°, {lon:6.2f}°)")
    else:
        print(f"  Extra: {GAP3[i]} → {gap3_angles[i]:6.2f}°")

print(f"\nGap4 as 4 coordinate pairs + 1 extra:")
for i in range(0, 9, 2):
    if i+1 < 9:
        lat = gap4_angles[i]
        lon = gap4_angles[i+1]
        print(f"  Pair {i//2 + 1}: {GAP4[i]}{GAP4[i+1]} → ({lat:6.2f}°, {lon:6.2f}°)")
    else:
        print(f"  Extra: {GAP4[i]} → {gap4_angles[i]:6.2f}°")

print("\n[ANALYSIS 3] TIME VALUES (24-HOUR FORMAT)")
print("-" * 80)

print(f"\nGap3 ({GAP3}) as 24-hour time components:")
gap3_times = [letter_to_time_24h(c) for c in GAP3]
for i, c in enumerate(GAP3):
    hours = gap3_times[i]
    print(f"  {c} → {hours:2d}:00 ({hours:02d}:00)")

print(f"\nGap4 ({GAP4}) as 24-hour time components:")
gap4_times = [letter_to_time_24h(c) for c in GAP4]
for i, c in enumerate(GAP4):
    hours = gap4_times[i]
    print(f"  {c} → {hours:2d}:00 ({hours:02d}:00)")

# Pairs as times
print(f"\nGap3 as time pairs (HH:MM):")
for i in range(0, 9, 2):
    if i+1 < 9:
        hh = gap3_times[i]
        mm = gap3_times[i+1]
        print(f"  {GAP3[i:i+2]} → {hh:02d}:{mm:02d}")

print(f"\nGap4 as time pairs (HH:MM):")
for i in range(0, 9, 2):
    if i+1 < 9:
        hh = gap4_times[i]
        mm = gap4_times[i+1]
        print(f"  {GAP4[i:i+2]} → {hh:02d}:{mm:02d}")

print("\n[ANALYSIS 4] BERLIN CITIES (148 CITIES ON CLOCK)")
print("-" * 80)

# Berlin Clock shows 148 cities
# If we use 9 chars to encode 4 pairs + 1 = 5 data points
# 26^9 = massive, but 148 is a specific number

print(f"\nIf Gap3 and Gap4 represent city selections on Berlin Clock:")
print(f"  Total combinations: 148^4 = {148**4:,}")
print(f"  Gap3 + Gap4 combinations: 148^8 = {148**8:,}")
print(f"  Possible encodings with 26 letters per position: 26^18 = {26**18:,}")

# Check if letter values modulo 148 create meaningful indices
print(f"\nLetter values mod 148 (index into 148 cities):")
gap3_city_idx = [letter_value(c) % 148 for c in GAP3]
gap4_city_idx = [letter_value(c) % 148 for c in GAP4]
print(f"  Gap3: {gap3_city_idx}")
print(f"  Gap4: {gap4_city_idx}")

print("\n[ANALYSIS 5] LATTITUDE/LONGITUDE REAL BERLIN LOCATIONS")
print("-" * 80)

# Real Berlin coordinates: 52.5°N, 13.4°E
print(f"\nBerlin geographic coordinates: 52°30'N, 13°24'E")
print(f"CIA Langley (Virginia, USA): 38°55'N, 77°10'W")
print(f"Kryptos location: Langley")

# Check if gaps encode these or related coordinates
print(f"\nGap3 values as pseudo-lat/long components:")
print(f"  Sum: {sum(letter_value(c) for c in GAP3)} (52°30' = 52.5° ≈ 52.5)")
print(f"  Average: {sum(letter_value(c) for c in GAP3) / 9:.2f}°")

print(f"\nGap4 values:")
print(f"  Sum: {sum(letter_value(c) for c in GAP4)} (38°55' = 38.92° or 13°24' = 13.4°)")
print(f"  Average: {sum(letter_value(c) for c in GAP4) / 9:.2f}°")

print("\n[ANALYSIS 6] 9-CHARACTER ENCODING SPECIFICS")
print("-" * 80)

# Why exactly 9 characters?
print(f"\n9 characters could encode:")
print(f"  - 4 x (latitude, longitude) pairs + 1 flag bit")
print(f"  - 3 x (hours, minutes, seconds) triads")
print(f"  - 2 x coordinates (4.5 chars each)")
print(f"  - 3 x 3-digit numbers (DDD format)")

print(f"\nGap3 as 3-digit numbers (3 groups of 3):")
for i in range(0, 9, 3):
    subset = GAP3[i:i+3]
    values = [letter_value(c) for c in subset]
    total = sum(values)
    print(f"  {subset} → {values} → sum={total}")

print(f"\nGap4 as 3-digit numbers (3 groups of 3):")
for i in range(0, 9, 3):
    subset = GAP4[i:i+3]
    values = [letter_value(c) for c in subset]
    total = sum(values)
    print(f"  {subset} → {values} → sum={total}")

print("\n[ANALYSIS 7] DIRECTIONAL ENCODING")
print("-" * 80)

# Cardinal directions: N, S, E, W
# Check if gaps contain directional hints
directions_n = 'N' in GAP3 or 'N' in GAP4
directions_s = 'S' in GAP3 or 'S' in GAP4
directions_e = 'E' in GAP3 or 'E' in GAP4
directions_w = 'W' in GAP3 or 'W' in GAP4

print(f"\nCardinal directions present:")
print(f"  N: {directions_n}, S: {directions_s}, E: {directions_e}, W: {directions_w}")

# Get all letters
print(f"\nLetters present in Gap3: {sorted(GAP3)}")
print(f"Letters present in Gap4: {sorted(GAP4)}")
print(f"Letters in both: {sorted(set(GAP3) & set(GAP4))}")

print("\n" + "=" * 80)
print("END OF BERLIN CLOCK ANALYSIS")
print("=" * 80)
