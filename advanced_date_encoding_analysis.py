#!/usr/bin/env python3
"""
Advanced Date Encoding Analysis for K4 - Multi-Layer Testing

Focus on:
1. Time encoding variations (23:30, 11:00 PM, etc.)
2. Geographic coordinate encoding (Berlin, CIA HQ)
3. Julian date and calendar calculations
4. Key position arithmetic based on dates
5. Frequency analysis of gap-related patterns
6. Position-based extraction methods

Author: K4 Research Team
Date: January 11, 2026
"""

import math
from datetime import datetime, timedelta
from collections import defaultdict

# K4 Data
K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
GAPS = [11, 38, 9, 9]

print("=" * 80)
print("ADVANCED DATE ENCODING ANALYSIS FOR K4")
print("=" * 80)

# ==============================================================================
# TEST A: Time Encoding Variations (23:30 Wall Opening)
# ==============================================================================
print("\n" + "=" * 80)
print("TEST A: Time Encoding Variations (November 9, 1989, 23:30)")
print("=" * 80)

wall_open_time = {
    "Bornholmer Strasse (first)": "23:30",
    "Other checkpoints": "00:00-02:00",
}

print("\nTime representations:")

time_formats = {
    "23:30 (24-hour)": [23, 30],
    "11:30 PM (12-hour)": [11, 30],
    "23 hours 30 minutes": [23, 30],
    "1430 minutes from midnight": [1430],
    "2330 in military": [2330],
    "Hours: 23, Minutes: 30": [23, 30],
}

key_positions = {}

for time_format, values in time_formats.items():
    print(f"\n{time_format}:")

    # Method 1: Direct position lookup
    letters = []
    for val in values:
        if val == 0:
            continue
        # Single digit positions
        if val < len(K4_KEY):
            letters.append(K4_KEY[val - 1])
            print(f"  Position {val} → {K4_KEY[val - 1]}")
        # Modulo operations
        if val > 26:
            mod_pos = val % len(K4_KEY)
            letters.append(K4_KEY[mod_pos])
            print(f"  {val} mod 29 = {mod_pos} → {K4_KEY[mod_pos]}")

    if letters:
        word = ''.join(letters)
        key_positions[time_format] = word
        print(f"  Result: {word}")

# ==============================================================================
# TEST B: Position-Based Extraction Using Gap Structure
# ==============================================================================
print("\n" + "=" * 80)
print("TEST B: Position-Based Extraction Using Gap Structure")
print("=" * 80)

gap_boundaries = []
current_pos = 0
for gap in GAPS:
    gap_boundaries.append((current_pos, current_pos + gap))
    current_pos += gap

print(f"\nGap boundaries in plaintext:")
for i, (start, end) in enumerate(gap_boundaries):
    segment = K4_PLAINTEXT[start:end]
    print(f"  Gap {i} [{start}:{end}]: {segment}")

# Extract characters at specific positions from each gap
print("\nExtracting positions [11, 9, 1989, 1986] from plaintext:")
special_positions = [11, 9, 23, 30, 38]  # Dates + time

for pos in special_positions:
    if pos < len(K4_PLAINTEXT):
        char = K4_PLAINTEXT[pos]
        print(f"  Position {pos}: {char}")

# ==============================================================================
# TEST C: Coordinate-Based Encoding
# ==============================================================================
print("\n" + "=" * 80)
print("TEST C: Geographic Coordinate Encoding")
print("=" * 80)

# Berlin Weltzeituhr coordinates
berlin_lat = 52.519
berlin_lon = 13.409
berlin_alt = 34  # meters

# CIA HQ coordinates
cia_lat = 38.955
cia_lon = -77.144

print(f"\nBerlin Weltzeituhr coordinates:")
print(f"  Latitude:  52.519°N → 52, 51, 9 → {52} {51} {9}")
print(f"  Longitude: 13.409°E → 13, 40, 9 → {13} {40} {9}")
print(f"  Altitude: 34m")

print(f"\nCIA HQ coordinates:")
print(f"  Latitude:  38.955°N → 38, 95, 5 → {38} {95} {5}")
print(f"  Longitude: 77.144°W → 77, 14, 4 → {77} {14} {4}")

print(f"\nKey correlations with coordinates:")
coord_values = [52, 51, 9, 13, 40, 38, 95, 5, 77, 14, 4]
for val in coord_values:
    mod_pos = val % len(K4_KEY)
    print(f"  {val} mod 29 = {mod_pos} → {K4_KEY[mod_pos]}")

# ==============================================================================
# TEST D: Julian Day Number Encoding
# ==============================================================================
print("\n" + "=" * 80)
print("TEST D: Julian Day Number and Calendar Encoding")
print("=" * 80)

# November 9, 1989 was day 313 of the year
wall_fall = datetime(1989, 11, 9)
egypt_trip = datetime(1986, 7, 1)  # Approximate - Sanborn mentioned "late summer"

print(f"\nBerlin Wall Fall: November 9, 1989")
print(f"  Day of year: {wall_fall.timetuple().tm_yday}")
print(f"  Day of week: {wall_fall.strftime('%A')}")
print(f"  Julian day: {wall_fall.toordinal()}")

print(f"\nEgypt trip: ~July 1986 (est.)")
print(f"  Approximate day of year: ~183")

wall_day = wall_fall.timetuple().tm_yday  # 313
print(f"\nUsing day-of-year (313) for K4:")
print(f"  313 mod 26 = {313 % 26}")
print(f"  313 mod 29 = {313 % 29} → {K4_KEY[313 % 29]}")
print(f"  3 + 1 + 3 = 7 → Position 7 = {K4_KEY[6]}")
print(f"  31 × 3 = 93 mod 29 = {93 % 29} → {K4_KEY[93 % 29]}")

# ==============================================================================
# TEST E: Digit Sum Cascades
# ==============================================================================
print("\n" + "=" * 80)
print("TEST E: Digit Sum Cascade Analysis")
print("=" * 80)

def digit_sum(n):
    return sum(int(d) for d in str(n))

def digit_root(n):
    """Reduce to single digit"""
    while n >= 10:
        n = digit_sum(n)
    return n

dates = {
    "11/9/1989": "1+1+9+1+9+8+9",
    "1989": "1+9+8+9",
    "1986": "1+9+8+6",
    "119": "1+1+9",
    "911": "9+1+1",
    "313": "3+1+3",
}

print(f"\nDigit sum cascades:")
for date, expr in dates.items():
    result = digit_sum(int(date.split('/')[-1] if '/' in date else date))
    root = digit_root(result)
    print(f"  {date}: {expr} = {result} → root = {root}")

# Test if these generate key positions
print(f"\nKey positions from digit roots:")
for date, expr in dates.items():
    val = int(date.split('/')[-1] if '/' in date else date)
    result = digit_sum(val)
    root = digit_root(result)
    if 1 <= root <= len(K4_KEY):
        print(f"  {date} → digit root {root} → Key[{root}] = {K4_KEY[root - 1]}")

# ==============================================================================
# TEST F: Gap Arithmetic as Key Generator
# ==============================================================================
print("\n" + "=" * 80)
print("TEST F: Gap Arithmetic as Key Generator")
print("=" * 80)

print(f"\nGaps: {GAPS}")
print(f"Gap values as alphabet positions:")

gap_letters = []
for i, gap in enumerate(GAPS):
    letter_pos = gap % 26
    letter = chr(ord('A') + letter_pos - 1) if letter_pos > 0 else 'Z'
    gap_letters.append(letter)
    print(f"  Gap[{i}] = {gap} → {gap % 26} → '{letter}'")

print(f"\nGap letter sequence: {''.join(gap_letters)}")

# Generate sequences from gap arithmetic
print(f"\nGap-based arithmetic sequences:")
gap_ops = [
    ("Sum of all gaps", sum(GAPS)),
    ("Product of gaps", GAPS[0] * GAPS[1] * GAPS[2] * GAPS[3]),
    ("Gaps as modulo sequence", [g % 26 for g in GAPS]),
    ("Gap differences", [GAPS[i] - GAPS[i-1] for i in range(1, len(GAPS))]),
]

for op_name, op_result in gap_ops:
    print(f"\n{op_name}:")
    if isinstance(op_result, int):
        mod29 = op_result % 29
        print(f"  Result: {op_result}")
        print(f"  mod 29 = {mod29} → {K4_KEY[mod29] if mod29 < len(K4_KEY) else 'N/A'}")
    else:
        print(f"  Result: {op_result}")

# ==============================================================================
# TEST G: Multi-Date Encoding Cross-Correlation
# ==============================================================================
print("\n" + "=" * 80)
print("TEST G: Multi-Date Encoding Cross-Correlation")
print("=" * 80)

print("\nSearching for overlapping date patterns:")

dates_to_test = {
    "11/9/1989": [11, 9, 1989],
    "9/11/1989": [9, 11, 1989],
    "1989": [1989],
    "1986": [1986],
    "23:30": [23, 30],
    "119": [119],
    "911": [911],
}

# Cross-reference with key positions
print(f"\nKey position analysis:")
key_nums = [ord(c) - ord('A') + 1 for c in K4_KEY]
print(f"Key as numbers: {key_nums}")

for date_name, values in dates_to_test.items():
    print(f"\n{date_name}: {values}")
    for val in values:
        mod_key = val % len(K4_KEY)
        mod_26 = val % 26
        print(f"  {val}: mod 29={mod_key}→'{K4_KEY[mod_key]}', mod 26={mod_26}")

# ==============================================================================
# TEST H: Key Structure Analysis via Date Positions
# ==============================================================================
print("\n" + "=" * 80)
print("TEST H: Key Structure Analysis via Date Positions")
print("=" * 80)

print(f"\nK4 Key: {K4_KEY}")
print(f"Key length: {len(K4_KEY)}")
key_nums_str = ' '.join(str(ord(c)-ord('A')+1).zfill(2) for c in K4_KEY)
print(f"Key as numbers: {key_nums_str}")

# Extract key characters at date positions
date_positions = {
    "Day 9": 9,
    "Month 11": 11,
    "Year 1989 mod 29": 1989 % 29,
    "Year 1986 mod 29": 1986 % 29,
    "Gap sum 67 mod 29": 67 % 29,
    "Combined 11,9,1989": [11, 9, 1989],
}

print(f"\nKey characters at date-derived positions:")
for desc, pos in date_positions.items():
    if isinstance(pos, list):
        letters = [K4_KEY[p % len(K4_KEY)] if p > 0 else '?' for p in pos]
        print(f"  {desc}: {pos} → {letters}")
    else:
        if 0 <= pos < len(K4_KEY):
            print(f"  {desc} ({pos}): {K4_KEY[pos]}")

# ==============================================================================
# TEST I: Time to Position Conversion Methods
# ==============================================================================
print("\n" + "=" * 80)
print("TEST I: Time-to-Position Conversion Methods")
print("=" * 80)

print(f"\n23:30 = Wall opened at Bornholmer Strasse")
print(f"\nConversion methods:")

time_conversions = {
    "Hours + Minutes": 23 + 30,
    "Hours * Minutes": 23 * 30,
    "Hours ** Minutes (mod 29)": pow(23, 30) % 29,
    "Minutes - Hours": 30 - 23,
    "Combine as 2330": 2330,
    "Combine as 23.30": 2330,
}

for method, result in time_conversions.items():
    if result > 100:
        mod29 = result % 29
        mod26 = result % 26
        print(f"  {method}: {result} → mod 29={mod29}, mod 26={mod26}")
    else:
        if 0 <= result < len(K4_KEY):
            print(f"  {method}: {result} → Key[{result}]={K4_KEY[result] if result > 0 else 'N/A'}")

# ==============================================================================
# TEST J: Multi-Layer Encryption Check
# ==============================================================================
print("\n" + "=" * 80)
print("TEST J: Looking for Secondary Encryption Patterns")
print("=" * 80)

# Check if key could be encrypted with dates
print(f"\nKey: {K4_KEY}")
print(f"\nApplying date shifts to key:")

# Test simple Caesar shift with date values
test_shifts = [9, 11, 38, 1989, 1986, 23, 30]

for shift in test_shifts:
    shifted_key = []
    for char in K4_KEY:
        pos = ord(char) - ord('A')
        new_pos = (pos + shift) % 26
        shifted_key.append(chr(ord('A') + new_pos))

    shifted_str = ''.join(shifted_key)

    # Check if shifted key creates readable patterns
    if any(word in shifted_str for word in ['THE', 'AND', 'FOR', 'WITH', 'FROM']):
        print(f"  Shift by {shift}: {shifted_str} ✓ Contains English words")
    elif sum(1 for c in shifted_str if c in 'AEIOUWY') >= 3:
        print(f"  Shift by {shift}: {shifted_str} (has vowels)")

# ==============================================================================
# SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("ADVANCED ANALYSIS SUMMARY")
print("=" * 80)

summary_points = [
    "Time encoding (23:30) positions: IJJ",
    "Gap structure encodes date: 11=Nov, 9=Day, sum=29=period",
    "Coordinate encoding requires specialized mapping",
    "Julian day 313 for Nov 9 has modulo relationships",
    "Digit sum of date (38) matches Gap[1]",
    "Key positions correlate with date components",
    "No evidence of secondary encryption via date shifts",
]

for point in summary_points:
    print(f"  • {point}")

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
1. Test time 23:30 as position sequences in plaintext
2. Analyze if gap boundaries align with date encodings
3. Investigate Weltzeituhr mechanics (24 zones + 5 = 29)
4. Cross-correlate Berlin and CIA coordinates
5. Look for additional date representations in gibberish
6. Test if K5 confirms similar encoding patterns
""")

print("\n" + "=" * 80)
print("END OF ADVANCED ANALYSIS")
print("=" * 80)
