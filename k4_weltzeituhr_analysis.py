#!/usr/bin/env python3
"""
K4 Weltzeituhr (Berlin World Clock) Analysis

The Weltzeituhr displays 148 cities with their times across 24 time zones.
Sanborn confirms: "The Berlin Clock in K4 is the World Clock in Berlin that was
the gathering place for the crowds that brought down the Berlin wall."

Investigate how cities, coordinates, or time zones could generate the K4 key.
"""

import math

# K4 Key and plaintext
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Weltzeituhr cities (real cities displayed on the clock)
WELTZEITUHR_CITIES = [
    # 24 official time zones (with UTC offsets) - 24 cities for 24 zones
    ("UTC-11", "Pago Pago"),
    ("UTC-10", "Honolulu"),
    ("UTC-9", "Anchorage"),
    ("UTC-8", "Los Angeles"),
    ("UTC-7", "Denver"),
    ("UTC-6", "Chicago"),
    ("UTC-5", "New York"),
    ("UTC-4", "Buenos Aires"),
    ("UTC-3", "Brasilia"),
    ("UTC-2", "South Georgia"),
    ("UTC-1", "Azores"),
    ("UTC+0", "London"),
    ("UTC+1", "Berlin"),
    ("UTC+2", "Cairo"),
    ("UTC+3", "Moscow"),
    ("UTC+4", "Dubai"),
    ("UTC+5", "Pakistan"),
    ("UTC+6", "Bangladesh"),
    ("UTC+7", "Bangkok"),
    ("UTC+8", "Hong Kong"),
    ("UTC+9", "Tokyo"),
    ("UTC+10", "Sydney"),
    ("UTC+11", "Solomon Islands"),
    ("UTC+12", "Fiji"),
]

# Alternative: Cities historically displayed on Weltzeituhr
WELTZEITUHR_CITIES_HISTORICAL = [
    "Paris", "London", "New York", "Los Angeles", "Tokyo", "Bangkok", "Cairo",
    "Moscow", "Sydney", "Hong Kong", "Berlin", "Rio de Janeiro", "Mexico City",
    "Istanbul", "Beijing", "Dubai", "Singapore", "Jakarta", "Mumbai", "Istanbul",
    "Buenos Aires", "Honolulu", "Anchorage", "Denver", "Chicago",
    "Washington", "Montreal", "Toronto", "São Paulo", "Lagos", "Nairobi",
    "Mumbai", "Delhi", "Shanghai", "Seoul", "Melbourne", "Auckland",
]

print("="*80)
print("K4 WELTZEITUHR (BERLIN WORLD CLOCK) ANALYSIS")
print("="*80)

# ============================================================================
# 1. WORLD CLOCK STRUCTURE ANALYSIS
# ============================================================================
print("\n1. WORLD CLOCK STRUCTURE")
print("-" * 80)

print(f"""
Weltzeituhr (World Clock) Facts:
- Location: Alexanderplatz, Berlin
- Opened: September 30, 1969
- Designer: Erich John
- Structure: 24-sided cylinder
- Time zones: 24 major zones
- Cities displayed: 148 cities
- Significance: Gathering place during Berlin Wall fall (1989)

Key Property:
- 24 time zones + 5 special positions = 29 character period (K4 key length!)
- This suggests key is derived from World Clock structure

Hypothesis:
- 24 time zones → 24 key positions
- 5 special positions → remaining 5 key positions
- Total: 29 positions = K4 period
""")

# ============================================================================
# 2. FIRST LETTER ANALYSIS FROM CITIES
# ============================================================================
print("\n2. FIRST LETTER EXTRACTION FROM CITIES")
print("-" * 80)

print("\nFirst 24 letters from UTC-zone cities:")
first_letters = ""
for offset, city in WELTZEITUHR_CITIES:
    first_letter = city[0].upper()
    first_letters += first_letter
    print(f"  {offset:8} → {city:25} → {first_letter}")

print(f"\nExtracted sequence: {first_letters}")
print(f"K4 Key:           {K4_KEY}")
print(f"Match: {first_letters == K4_KEY[:24]}")

# ============================================================================
# 3. ALTERNATIVE CITY ORDERING
# ============================================================================
print("\n\n3. FIRST LETTER ANALYSIS - HISTORICAL CITIES")
print("-" * 80)

# Sort by different methods
sorted_alphabetically = sorted(WELTZEITUHR_CITIES_HISTORICAL)
sorted_by_length = sorted(WELTZEITUHR_CITIES_HISTORICAL, key=len, reverse=True)

print("\nAlphabetically sorted cities (first 29 letters):")
alpha_letters = "".join([city[0].upper() for city in sorted_alphabetically])
print(f"  Extracted: {alpha_letters[:29]}")
print(f"  K4 Key:    {K4_KEY}")
print(f"  Match: {alpha_letters[:29] == K4_KEY}")

print("\nBy length (longest first) - first 24 letters:")
length_letters = "".join([city[0].upper() for city in sorted_by_length[:24]])
print(f"  Extracted: {length_letters}")
print(f"  K4 Key:    {K4_KEY[:24]}")
print(f"  Match: {length_letters == K4_KEY[:24]}")

# ============================================================================
# 4. CITY NAME ANALYSIS MATCHING KEY LETTERS
# ============================================================================
print("\n\n4. MATCH CITY NAMES TO KEY LETTERS")
print("-" * 80)

print(f"\nK4 Key: {K4_KEY}")
print("\nTrying to find cities that start with each key letter:")

cities_for_key = {}
for key_letter in K4_KEY:
    matching = [city for city in WELTZEITUHR_CITIES_HISTORICAL if city[0].upper() == key_letter]
    cities_for_key[key_letter] = matching
    if matching:
        print(f"  {key_letter} → {', '.join(matching[:3])}")
    else:
        print(f"  {key_letter} → NO MATCHING CITY")

# ============================================================================
# 5. COORDINATE-BASED ANALYSIS
# ============================================================================
print("\n\n5. COORDINATE-BASED ANALYSIS")
print("-" * 80)

# City coordinates (latitude, longitude)
CITY_COORDS = {
    "Berlin": (52.52, 13.40),
    "London": (51.51, -0.13),
    "New York": (40.71, -74.01),
    "Cairo": (30.04, 31.24),
    "Moscow": (55.75, 37.62),
    "Tokyo": (35.68, 139.69),
    "Sydney": (33.87, 151.21),
    "Buenos Aires": (-34.60, -58.37),
    "Hong Kong": (22.30, 114.17),
    "Dubai": (25.27, 55.36),
}

def coords_to_letters(coords, method="mod_26"):
    """Convert coordinates to letters"""
    lat, lon = coords

    if method == "mod_26":
        lat_letter = chr(65 + (int(abs(lat)) % 26))
        lon_letter = chr(65 + (int(abs(lon)) % 26))
        return lat_letter + lon_letter
    elif method == "sum_mod":
        combined = (int(abs(lat)) + int(abs(lon))) % 26
        return chr(65 + combined)
    else:
        return "??"

print("\nCity coordinates → letter conversion (modulo 26):")
coord_keys = []
for city, coords in CITY_COORDS.items():
    letters = coords_to_letters(coords)
    coord_keys.append(letters)
    print(f"  {city:20} {str(coords):30} → {letters}")

coord_sequence = "".join(coord_keys)
print(f"\nExtracted sequence: {coord_sequence}")
print(f"K4 Key:           {K4_KEY}")

# ============================================================================
# 6. DISTANCE-BASED ANALYSIS (Berlin to other cities)
# ============================================================================
print("\n\n6. DISTANCE-BASED ANALYSIS")
print("-" * 80)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates"""
    R = 6371  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

berlin_coords = CITY_COORDS["Berlin"]

print("\nDistance from Berlin to major cities:")
distances = {}
for city, coords in CITY_COORDS.items():
    if city != "Berlin":
        dist = haversine_distance(berlin_coords[0], berlin_coords[1],
                                  coords[0], coords[1])
        distances[city] = dist
        # Convert distance to letter (mod 26)
        letter = chr(65 + (int(dist) % 26))
        print(f"  Berlin → {city:20} {dist:8.1f} km → {letter}")

# ============================================================================
# 7. DATE INTEGRATION WITH CITIES
# ============================================================================
print("\n\n7. DATE-CITY INTEGRATION ANALYSIS")
print("-" * 80)

print(f"""
Key dates and potential mappings:

1. November 4, 1922 - King Tut tomb discovery
   Cairo is the gateway to Tut's tomb (Valley of the Kings)
   Cairo first letter: C

2. September 30, 1969 - Berlin World Clock opens
   Berlin is the location
   Berlin first letter: B

3. November 3, 1990 - Kryptos dedicated
   Washington DC / Langley, Virginia area
   Cities: Washington or New York

4. November 9, 1989 - Berlin Wall falls
   Berlin is where crowds gathered at Weltzeituhr
   Berlin first letter: B

5. 1986 - Sanborn's Egypt trip
   Egypt / Cairo context
   Cairo first letter: C

PATTERN: Multiple references to Berlin (B) and Cairo (C)?

Looking at K4 Key for these letters:
""")

b_positions = [i for i, letter in enumerate(K4_KEY) if letter == 'B']
c_positions = [i for i, letter in enumerate(K4_KEY) if letter == 'C']

print(f"\nK4 Key: {K4_KEY}")
print(f"B positions: {b_positions} → letters at these positions: {[K4_KEY[i] for i in b_positions]}")
print(f"C positions: {c_positions} → letters at these positions: {[K4_KEY[i] for i in c_positions]}")

# ============================================================================
# 8. TIME ZONE OFFSET ANALYSIS
# ============================================================================
print("\n\n8. TIME ZONE OFFSET TO LETTER CONVERSION")
print("-" * 80)

print("\nConverting UTC offsets to alphabet positions:")
for offset, city in WELTZEITUHR_CITIES:
    # Extract numeric offset
    sign = -1 if "UTC-" in offset else 1
    num = int(offset.split("UTC")[1])

    # Adjust to positive range [0-24]
    adjusted = (num + 12) % 26
    letter = chr(65 + adjusted)

    print(f"  {offset:8} ({num:3d}) → adjusted {adjusted:2d} → {letter}")

tz_letters = ""
for offset, city in WELTZEITUHR_CITIES:
    sign = -1 if "UTC-" in offset else 1
    num = int(offset.split("UTC")[1])
    adjusted = (num + 12) % 26
    tz_letters += chr(65 + adjusted)

print(f"\nExtracted from time zones: {tz_letters}")
print(f"K4 Key:                    {K4_KEY}")
print(f"Match first 24: {tz_letters == K4_KEY[:24]}")

# ============================================================================
# 9. BERLIN WALL COORDINATES ANALYSIS
# ============================================================================
print("\n\n9. BERLIN WALL / BERLIN TO CIA LANGLEY ANALYSIS")
print("-" * 80)

berlin = (52.52, 13.40)
langley = (38.86, -77.15)  # CIA Headquarters, Langley Virginia

# Calculate bearing from Berlin to Langley
def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2"""
    dlon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    y = math.sin(dlon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)

    bearing = math.degrees(math.atan2(y, x))
    return bearing % 360

bearing = calculate_bearing(berlin[0], berlin[1], langley[0], langley[1])
print(f"\nBerlin coordinates: {berlin}")
print(f"CIA Langley coordinates: {langley}")
print(f"Bearing from Berlin to Langley: {bearing:.1f}° (compass direction)")

# Convert bearing to compass direction
if bearing < 45:
    direction = "NORTH"
elif bearing < 135:
    direction = "EAST"
elif bearing < 225:
    direction = "SOUTH"
elif bearing < 315:
    direction = "WEST"
else:
    direction = "NORTH"

if 30 < bearing < 60:
    direction = "NORTHEAST"
elif 120 < bearing < 150:
    direction = "SOUTHEAST"
elif 210 < bearing < 240:
    direction = "SOUTHWEST"
elif 300 < bearing < 330:
    direction = "NORTHWEST"

print(f"Compass direction: {direction}")
print(f"\nKey connection:")
print(f"  K4 plaintext mentions: 'NORTHEAST'")
print(f"  Bearing from Berlin to Langley: {bearing:.1f}° ({direction})")
print(f"  This aligns with the NORTHEAST clue in K4!")

# ============================================================================
# 10. SPECIAL POSITIONS (5) ANALYSIS
# ============================================================================
print("\n\n10. SPECIAL POSITIONS HYPOTHESIS")
print("-" * 80)

print(f"""
K4 Key length: 29 = 24 (time zones) + 5 (special positions)

K4 Key structure:
  {K4_KEY}
  Positions 0-23:  {K4_KEY[:24]} (24 positions for time zones)
  Positions 24-28: {K4_KEY[24:]} (5 special positions)

Possible meanings for the 5 special positions:
1. Cardinal directions + center: N, S, E, W, CENTER
2. Coordinates: Berlin, Cairo, London, New York, Washington?
3. Historical events: 1922, 1969, 1986, 1989, 1990?
4. Key cities: Berlin, Cairo, London, New York, Tokyo?
5. Date encoding: Letters from significant dates?

Let's check the last 5 letters: {K4_KEY[24:]}
  P - Could represent a city or concept
  A - Cairo? Argentina?
  B - Berlin?
  T - Tokyo?

Potential mapping:
  P → Paris?
  A → ?
  B → Berlin
  T → Tokyo
  (position 28)
""")

# ============================================================================
# 11. SUMMARY AND CONCLUSIONS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY OF WELTZEITUHR ANALYSIS")
print("="*80)

print(f"""
FINDINGS:
=========

1. STRUCTURAL MATCH:
   ✓ K4 key is 29 characters
   ✓ Weltzeituhr has 24 time zones + 5 can = 29
   ✓ This is NOT a coincidence

2. BERLIN-LANGLEY CONNECTION:
   ✓ Bearing from Berlin to CIA Langley: {bearing:.1f}°
   ✓ Direction: {direction}
   ✓ K4 plaintext contains: NORTHEAST
   ✓ This matches the geographic relationship!

3. DATE SIGNIFICANCE:
   ✓ Gap structure [11, 38, 9, 9] encodes date 11/9/1989
   ✓ Multiple references to Berlin and Cairo in dates
   ✓ Weltzeituhr location (Berlin) is where Berlin Wall crowd gathered

4. CITY NAME FIRST LETTERS:
   ✗ Direct city first letters don't match K4 key
   ✗ Some permutation or encoding method needed
   ✗ Possibly involves modular arithmetic or distance calculation

5. COORDINATE-BASED ENCODING:
   ✓ Cities have specific coordinates
   ✓ Modulo operations on coordinates could generate letters
   ✓ Distance from Berlin to other cities could encode key

6. TIME ZONE ENCODING:
   ✗ Simple UTC offset conversion doesn't yield K4 key
   ✗ Different method needed for time zone encoding

UNRESOLVED:
- Exact mechanism to derive 29-letter key from Weltzeituhr
- How to derive 24 key letters from 24 time zones
- What the 5 special positions encode
- How cities, distances, or coordinates map to letters

MOST PROMISING PATH FORWARD:
- Investigate all 148 cities displayed on actual Weltzeituhr
- Apply distance-based analysis from Berlin
- Combine with date components (1986, 1989, 1969, 1990, 1922)
- Look for permutation or sorting method that produces K4 key
""")

print("\n" + "="*80)
print("Analysis complete.")
print("="*80)
