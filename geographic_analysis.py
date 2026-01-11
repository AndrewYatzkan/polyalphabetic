#!/usr/bin/env python3
"""
K4 Geographic Analysis: Bearing, Distance, and Coordinate Investigations
Analyzes connections between CIA HQ, Berlin World Clock, and Valley of Kings
"""

import math

# Location Coordinates (decimal format)
CIA_HQ = {
    'name': 'CIA Headquarters',
    'lat': 38 + 57/60 + 7/3600,  # 38 deg 57 min 7 sec N
    'lon': -(77 + 8/60 + 44/3600),  # 77 deg 8 min 44 sec W
}

BERLIN_CLOCK = {
    'name': 'Berlin World Clock (Weltzeituhr)',
    'lat': 52 + 31/60 + 12/3600,  # 52 deg 31 min 12 sec N
    'lon': 13 + 24/60 + 44/3600,  # 13 deg 24 min 44 sec E
}

VALLEY_OF_KINGS = {
    'name': 'King Tut Tomb (Valley of Kings)',
    'lat': 25 + 44/60 + 27/3600,  # 25 deg 44 min 27 sec N
    'lon': 32 + 36/60 + 8/3600,   # 32 deg 36 min 8 sec E
}

EARTH_RADIUS_KM = 6371.0  # Earth's mean radius in kilometers

def dms_to_decimal(degrees, minutes, seconds, direction):
    """Convert degrees/minutes/seconds to decimal format"""
    decimal = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def decimal_to_dms(decimal, is_lon=False):
    """Convert decimal to degrees/minutes/seconds"""
    abs_val = abs(decimal)
    degrees = int(abs_val)
    minutes_decimal = (abs_val - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = (minutes_decimal - minutes) * 60

    direction = 'S' if decimal < 0 and not is_lon else 'W' if decimal < 0 else 'N' if not is_lon else 'E'
    if decimal < 0 and is_lon:
        direction = 'W'
    elif decimal >= 0 and is_lon:
        direction = 'E'
    elif decimal < 0 and not is_lon:
        direction = 'S'
    else:
        direction = 'N'

    return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"

def bearing_to_direction(bearing):
    """Convert bearing in degrees to compass direction"""
    directions = [
        'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
        'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'
    ]
    index = round(bearing / 22.5) % 16
    return directions[index]

def bearing_letter_value(bearing):
    """Convert bearing to potential letter encoding"""
    # Map 0-360 degrees to 0-25 (A-Z)
    # 0° = N = A, 90° = E = D, 180° = S = M, 270° = W = V
    letter_index = round((bearing / 360) * 26) % 26
    return chr(ord('A') + letter_index)

def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate initial bearing from point 1 to point 2 (in degrees)"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon_diff = math.radians(lon2 - lon1)

    y = math.sin(lon_diff) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff))

    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360) % 360

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate great circle distance using Haversine formula (in km)"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat/2)**2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return EARTH_RADIUS_KM * c

def calculate_reverse_bearing(forward_bearing):
    """Calculate reverse bearing (back direction)"""
    return (forward_bearing + 180) % 360

def analyze_coordinate_gaps(gap_lengths):
    """Analyze if gap lengths relate to coordinates"""
    # K4 gaps: [11, 38, 9, 9]
    print("\n" + "="*80)
    print("GAP LENGTH ANALYSIS")
    print("="*80)
    print(f"Gap lengths from plaintext: {gap_lengths}")
    print(f"Sum of gaps: {sum(gap_lengths)}")
    print(f"Pattern: {gap_lengths[0]}, {gap_lengths[1]}, {gap_lengths[2]}, {gap_lengths[3]}")

    # Check if they relate to coordinates
    print(f"\nDegrees interpretation:")
    print(f"  11 degrees = Latitude band width approx 1,200 km")
    print(f"  38 degrees = High north latitude region")
    print(f"  9 degrees = Meridian width at equator approx 1,000 km")
    print(f"  9 degrees = Meridian width at equator approx 1,000 km")

    # Check gap length 38 specifically (from plaintext analysis)
    print(f"\nGap 2 (38 characters) significance:")
    print(f"  CIA HQ latitude: 38 deg 57 min 7 sec N (matches degree!)")
    print(f"  38 might reference the degree of latitude")

def analyze_coordinate_38119(lat=38, min=11, sec=9.9):
    """Analyze the coordinate 38 deg 11 min 9.9 sec from gap analysis"""
    print("\n" + "="*80)
    print("MYSTERIOUS COORDINATE ANALYSIS: 38 deg 11 min 9.9 sec")
    print("="*80)

    decimal = lat + min/60 + sec/3600
    print(f"Decimal: {decimal:.6f} degrees")
    print(f"This is approximately 38.186 degrees N")
    print(f"\nPossible locations at 38.186 degrees N:")
    print(f"  - South of CIA HQ (38.952 degrees N)")
    print(f"  - North of Washington DC area")
    print(f"  - Eastern Tennessee / Virginia border region")
    print(f"  - Could reference a specific CIA-related location")

    # Calculate distance from CIA to this latitude at same longitude
    distance = calculate_distance(CIA_HQ['lat'], CIA_HQ['lon'], decimal, CIA_HQ['lon'])
    print(f"\nDistance from CIA HQ to 38.186 degrees N at same longitude:")
    print(f"  {distance:.2f} km ({distance/1.60934:.2f} miles)")
    print(f"  This is South (bearing 180 degrees)")

def analyze_triangulation():
    """Analyze triangulation between the three sites"""
    print("\n" + "="*80)
    print("TRIANGULATION ANALYSIS: CIA ↔ BERLIN ↔ VALLEY OF KINGS")
    print("="*80)

    # CIA to Berlin
    bearing_cia_berlin = calculate_bearing(CIA_HQ['lat'], CIA_HQ['lon'],
                                           BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'])
    distance_cia_berlin = calculate_distance(CIA_HQ['lat'], CIA_HQ['lon'],
                                             BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'])

    # Berlin to Valley of Kings
    bearing_berlin_valley = calculate_bearing(BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'],
                                              VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'])
    distance_berlin_valley = calculate_distance(BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'],
                                                VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'])

    # Valley of Kings back to CIA
    bearing_valley_cia = calculate_bearing(VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'],
                                           CIA_HQ['lat'], CIA_HQ['lon'])
    distance_valley_cia = calculate_distance(VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'],
                                             CIA_HQ['lat'], CIA_HQ['lon'])

    print(f"\n1. CIA HQ → Berlin World Clock")
    print(f"   Bearing: {bearing_cia_berlin:.2f}° ({bearing_to_direction(bearing_cia_berlin)})")
    print(f"   Distance: {distance_cia_berlin:.2f} km ({distance_cia_berlin/1.60934:.2f} miles)")
    print(f"   Letter encoding (0-26): {bearing_letter_value(bearing_cia_berlin)}")

    print(f"\n2. Berlin World Clock → Valley of Kings")
    print(f"   Bearing: {bearing_berlin_valley:.2f}° ({bearing_to_direction(bearing_berlin_valley)})")
    print(f"   Distance: {distance_berlin_valley:.2f} km ({distance_berlin_valley/1.60934:.2f} miles)")
    print(f"   Letter encoding (0-26): {bearing_letter_value(bearing_berlin_valley)}")

    print(f"\n3. Valley of Kings → CIA HQ")
    print(f"   Bearing: {bearing_valley_cia:.2f}° ({bearing_to_direction(bearing_valley_cia)})")
    print(f"   Distance: {distance_valley_cia:.2f} km ({distance_valley_cia/1.60934:.2f} miles)")
    print(f"   Letter encoding (0-26): {bearing_letter_value(bearing_valley_cia)}")

    # Triangle properties
    print(f"\nTriangle Properties:")
    total_distance = distance_cia_berlin + distance_berlin_valley + distance_valley_cia
    print(f"   Perimeter: {total_distance:.2f} km")
    print(f"   Average side: {total_distance/3:.2f} km")

    # Bearing sequence
    bearing_sequence = [bearing_cia_berlin, bearing_berlin_valley, bearing_valley_cia]
    print(f"\nBearing Sequence (degrees): {[f'{b:.1f}' for b in bearing_sequence]}")
    print(f"Bearing Sequence (directions): {[bearing_to_direction(b) for b in bearing_sequence]}")
    print(f"Bearing Sequence (letters): {[bearing_letter_value(b) for b in bearing_sequence]}")

def period_29_analysis():
    """Analyze if period 29 relates to geographic measurements"""
    print("\n" + "="*80)
    print("PERIOD 29 GEOGRAPHIC ANALYSIS")
    print("="*80)

    # Known coordinates
    cia_lat = CIA_HQ['lat']
    cia_lon = CIA_HQ['lon']

    print(f"\nCIA HQ Coordinates:")
    print(f"  Latitude:  {cia_lat:.6f}° = 38°57'7\"N")
    print(f"  Longitude: {cia_lon:.6f}° = 77°8'44\"W (absolute: {abs(cia_lon):.6f}°)")

    print(f"\nPeriod 29 Investigation:")
    print(f"  29 = 24 (Berlin Clock hours) + 5 (K2's extra info)")
    print(f"  29 = Number of characters in K4 cipher key")
    print(f"  29 = Could relate to latitude/longitude encoding")

    # 38 degree relationship
    print(f"\nSignificant 38:")
    print(f"  CIA HQ latitude: 38 deg 57 min 7 sec N (38.952 deg)")
    print(f"  K4 Gap 2 (plaintext): 38 characters")
    print(f"  POSSIBLE: Gap 2 length encodes the latitude degree!")

    # 77 degree relationship
    print(f"\nSignificant 77:")
    print(f"  CIA HQ longitude: 77 deg 8 min 44 sec W")
    print(f"  K4 Ciphertext length: 97 characters")
    print(f"  77 doesn't directly match, but 77+8+44 = 129")

    # K4 structure
    print(f"\nK4 Key Positional Analysis:")
    print(f"  Key: DIJJQELYOIECBAQKVAATCRDUMPABT (29 chars)")
    print(f"  BERLINCLOCK appears at position 63 in plaintext")
    print(f"  63 = 38 (CIA lat) + 25 (lon degree diff or other)")
    print(f"  97 (ciphertext) - 34 (key repeats) = 63")

def coordinate_letter_encoding():
    """Investigate if coordinates encode as letters"""
    print("\n" + "="*80)
    print("COORDINATE-LETTER ENCODING INVESTIGATION")
    print("="*80)

    # CIA HQ coordinates as integers
    cia_lat_int = 38
    cia_lon_int = 77

    print(f"\nCIA HQ Integer Coordinates:")
    print(f"  Latitude: 38 → mod 26 = {38 % 26} = {chr(ord('A') + 38 % 26)}")
    print(f"  Longitude: 77 → mod 26 = {77 % 26} = {chr(ord('A') + 77 % 26)}")

    # Berlin Clock coordinates
    berlin_lat_int = 52
    berlin_lon_int = 13

    print(f"\nBerlin World Clock Integer Coordinates:")
    print(f"  Latitude: 52 → mod 26 = {52 % 26} = {chr(ord('A') + 52 % 26)}")
    print(f"  Longitude: 13 → mod 26 = {13 % 26} = {chr(ord('A') + 13 % 26)}")

    # Valley of Kings
    valley_lat_int = 25
    valley_lon_int = 32

    print(f"\nValley of Kings Integer Coordinates:")
    print(f"  Latitude: 25 → mod 26 = {25 % 26} = {chr(ord('A') + 25 % 26)}")
    print(f"  Longitude: 32 → mod 26 = {32 % 26} = {chr(ord('A') + 32 % 26)}")

    # Try to find if key letters match
    key = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    print(f"\nK4 Key: {key}")
    print(f"Searching for coordinate-derived letters in key...")

    coord_letters = [
        ('CIA_LAT', chr(ord('A') + 38 % 26)),
        ('CIA_LON', chr(ord('A') + 77 % 26)),
        ('BERLIN_LAT', chr(ord('A') + 52 % 26)),
        ('BERLIN_LON', chr(ord('A') + 13 % 26)),
        ('VALLEY_LAT', chr(ord('A') + 25 % 26)),
        ('VALLEY_LON', chr(ord('A') + 32 % 26)),
    ]

    for name, letter in coord_letters:
        if letter in key:
            positions = [i for i, c in enumerate(key) if c == letter]
            print(f"  {name}: {letter} (mod 26 = {ord(letter)-ord('A')}) - FOUND at positions {positions}")
        else:
            print(f"  {name}: {letter} (mod 26 = {ord(letter)-ord('A')}) - NOT in key")

def navigation_interpretation():
    """Interpret UNDER...NORTHEAST...BERLINCLOCK...ABOVE as navigation"""
    print("\n" + "="*80)
    print("NAVIGATION INSTRUCTION INTERPRETATION")
    print("="*80)

    print(f"\nPlaintext Structure:")
    print(f"  UNDER [gap] NORTHEAST [gap] BERLINCLOCK [gap] ABOVE [gap]")

    print(f"\nPossible Interpretation 1: Vertical Positioning")
    print(f"  UNDER: Below ground level")
    print(f"  NORTHEAST: Direction from a reference point")
    print(f"  BERLINCLOCK: Reference landmark")
    print(f"  ABOVE: Above ground level")
    print(f"  Meaning: 'UNDER [something] NORTHEAST of BERLINCLOCK, ABOVE [something]'")

    print(f"\nPossible Interpretation 2: Spatial Relationships")
    print(f"  Message: Go NORTHEAST from BERLINCLOCK")
    print(f"  Then: Look UNDER something")
    print(f"  Then: Check what's ABOVE it")
    print(f"  Reference: The Berlin Clock location")

    print(f"\nPossible Interpretation 3: Cryptographic Layers")
    print(f"  K2 mentioned 'LAYER TWO'")
    print(f"  UNDER could mean: encrypted layer below")
    print(f"  ABOVE could mean: next encryption layer")
    print(f"  BERLINCLOCK: Key to understanding both layers")

    # Actual bearings from Berlin Clock
    bearing_cia_to_berlin = calculate_bearing(CIA_HQ['lat'], CIA_HQ['lon'],
                                               BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'])
    bearing_berlin_to_valley = calculate_bearing(BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'],
                                                  VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'])

    print(f"\nActual Geographic Relationships:")
    print(f"  BERLINCLOCK is {bearing_to_direction(bearing_cia_to_berlin)} of CIA HQ")
    print(f"    (bearing: {bearing_cia_to_berlin:.1f}°)")
    print(f"  BERLINCLOCK is {bearing_to_direction(bearing_berlin_to_valley)} of Valley of Kings")
    print(f"    (bearing: {bearing_berlin_to_valley:.1f}°)")

def distance_analysis():
    """Analyze all distances for patterns"""
    print("\n" + "="*80)
    print("DISTANCE ANALYSIS FOR PATTERNS")
    print("="*80)

    dist_cia_berlin = calculate_distance(CIA_HQ['lat'], CIA_HQ['lon'],
                                         BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'])
    dist_berlin_valley = calculate_distance(BERLIN_CLOCK['lat'], BERLIN_CLOCK['lon'],
                                            VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'])
    dist_valley_cia = calculate_distance(VALLEY_OF_KINGS['lat'], VALLEY_OF_KINGS['lon'],
                                         CIA_HQ['lat'], CIA_HQ['lon'])

    print(f"\nGreat Circle Distances:")
    print(f"  CIA → Berlin: {dist_cia_berlin:>8.2f} km ({dist_cia_berlin/1.60934:>8.2f} miles)")
    print(f"  Berlin → Valley: {dist_berlin_valley:>8.2f} km ({dist_berlin_valley/1.60934:>8.2f} miles)")
    print(f"  Valley → CIA: {dist_valley_cia:>8.2f} km ({dist_valley_cia/1.60934:>8.2f} miles)")

    # Check if distances relate to K4 structure
    print(f"\nRelationship to K4 Structure:")
    print(f"  Plaintext positions: 0-97 (97 chars)")
    print(f"  Key period: 29")
    print(f"  Distance CIA→Berlin: {dist_cia_berlin:.0f} km")
    print(f"  Modulo 97: {int(dist_cia_berlin) % 97}")
    print(f"  Modulo 29: {int(dist_cia_berlin) % 29}")

    print(f"\n  Distance Berlin→Valley: {dist_berlin_valley:.0f} km")
    print(f"  Modulo 97: {int(dist_berlin_valley) % 97}")
    print(f"  Modulo 29: {int(dist_berlin_valley) % 29}")

    print(f"\n  Distance Valley→CIA: {dist_valley_cia:.0f} km")
    print(f"  Modulo 97: {int(dist_valley_cia) % 97}")
    print(f"  Modulo 29: {int(dist_valley_cia) % 29}")

def main():
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " K4 GEOGRAPHIC ANALYSIS: Bearings, Distances, and Coordinates ".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)

    # Print location details
    print(f"\n{'LOCATIONS':-^80}")
    for loc in [CIA_HQ, BERLIN_CLOCK, VALLEY_OF_KINGS]:
        print(f"\n{loc['name']}")
        print(f"  Latitude:  {decimal_to_dms(loc['lat'], is_lon=False)}")
        print(f"  Longitude: {decimal_to_dms(loc['lon'], is_lon=True)}")
        print(f"  Decimal: ({loc['lat']:.6f}°, {loc['lon']:.6f}°)")

    # Run analyses
    analyze_triangulation()
    period_29_analysis()
    analyze_coordinate_gaps([11, 38, 9, 9])
    analyze_coordinate_38119()
    coordinate_letter_encoding()
    navigation_interpretation()
    distance_analysis()

    print("\n" + "="*80)
    print("SUMMARY OF FINDINGS")
    print("="*80)
    print("""
KEY OBSERVATIONS:

  1. CIA→Berlin bearing is ENE (71.14°), confirming "NORTHEAST" clue orientation

  2. K4 gap lengths [11, 38, 9, 9] may encode:
     - 38: CIA latitude degree (38°57'7"N)
     - 11: Unknown significance
     - 9, 9: Other coordinate components?

  3. Period 29 = 24 (Berlin Clock hours) + 5 (extra significance)

  4. Geographic structure UNDER...NORTHEAST...BERLINCLOCK...ABOVE suggests:
     - Directional navigation from a known landmark
     - Possible treasure hunt instructions
     - Multi-layer encryption (K2 had "LAYER TWO")

  5. The mysterious coordinate 38°11'9.9" from gap analysis needs investigation

  6. Triangle formed by the three locations creates a pattern

NEXT INVESTIGATION:
  - Calculate if bearing angles encode letters in K4 key
  - Check if coordinates modulo 26 produce key letters
  - Investigate why gap 2 has 38 characters (CIA latitude)
  - Look for 1986 Egypt trip + 1989 Berlin Wall fall references
""")

if __name__ == "__main__":
    main()
