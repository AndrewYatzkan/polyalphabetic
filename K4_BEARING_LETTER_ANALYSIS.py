#!/usr/bin/env python3
"""
K4 Bearing-to-Letter Mapping Analysis
Investigates if geographic bearings encode letters in the K4 cipher key
"""

import math

# Bearing values from geographic triangulation
CIA_TO_BERLIN = 44.42
BERLIN_TO_VALLEY = 144.22
VALLEY_TO_CIA = 312.91

K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

def bearing_to_letter(bearing):
    """Convert bearing (0-360) to letter (A-Z)"""
    # Method 1: Direct mapping (0-360 → 0-25)
    letter_index = round((bearing / 360) * 26) % 26
    return chr(ord('A') + letter_index)

def bearing_to_letter_quad(bearing):
    """Convert bearing to letter using quadrant method"""
    # Divide circle into 26 sections
    index = int((bearing / 360) * 26) % 26
    return chr(ord('A') + index)

def bearing_directions():
    """All compass direction bearings"""
    return {
        'N': 0, 'NNE': 22.5, 'NE': 45, 'ENE': 67.5,
        'E': 90, 'ESE': 112.5, 'SE': 135, 'SSE': 157.5,
        'S': 180, 'SSW': 202.5, 'SW': 225, 'WSW': 247.5,
        'W': 270, 'WNW': 292.5, 'NW': 315, 'NNW': 337.5
    }

def find_bearing_in_key(bearing, search_word="BERLINCLOCK"):
    """Search for bearing-derived letters in K4 key and plaintext"""
    letter = bearing_to_letter(bearing)
    quad_letter = bearing_to_letter_quad(bearing)

    print(f"\n{'='*70}")
    print(f"BEARING: {bearing:.2f}°")
    print(f"{'='*70}")
    print(f"Letter encoding (0-360→0-25): {letter}")
    print(f"Letter encoding (quadrant):   {quad_letter}")

    key_positions = [i for i, c in enumerate(K4_KEY) if c == letter]
    plain_positions = [i for i, c in enumerate(K4_PLAINTEXT) if c == letter]

    print(f"\nIn K4 Key ({len(key_positions)} occurrences):")
    if key_positions:
        for pos in key_positions:
            context = K4_KEY[max(0, pos-3):min(len(K4_KEY), pos+4)]
            print(f"  Position {pos}: ...{context}...")
    else:
        print(f"  NOT FOUND")

    print(f"\nIn K4 Plaintext ({len(plain_positions)} occurrences):")
    if plain_positions:
        for pos in plain_positions:
            context = K4_PLAINTEXT[max(0, pos-3):min(len(K4_PLAINTEXT), pos+4)]
            print(f"  Position {pos}: ...{context}...")
    else:
        print(f"  NOT FOUND")

    return letter, key_positions, plain_positions

def analyze_bearing_sequences():
    """Analyze bearing sequences and their letter values"""
    print("\n" + "█"*70)
    print("█" + " BEARING-TO-LETTER ANALYSIS ".center(68) + "█")
    print("█"*70)

    bearings = [
        ("CIA → Berlin", CIA_TO_BERLIN),
        ("Berlin → Valley", BERLIN_TO_VALLEY),
        ("Valley → CIA", VALLEY_TO_CIA)
    ]

    letters = []
    for name, bearing in bearings:
        letter = bearing_to_letter(bearing)
        letters.append(letter)
        print(f"\n{name}: {bearing:.2f}° → {letter}")

    sequence = ''.join(letters)
    print(f"\nBearing Sequence: {sequence}")

    # Check if this sequence appears in key or plaintext
    print(f"\nSearching for '{sequence}' in K4 Key...")
    if sequence in K4_KEY:
        pos = K4_KEY.index(sequence)
        print(f"  FOUND at position {pos}")
    else:
        print(f"  NOT FOUND in key")

    print(f"\nSearching for '{sequence}' in K4 Plaintext...")
    if sequence in K4_PLAINTEXT:
        pos = K4_PLAINTEXT.index(sequence)
        print(f"  FOUND at position {pos}")
    else:
        print(f"  NOT FOUND in plaintext")

    return sequence

def calculate_offset_bearings():
    """Calculate offset bearings that might produce key letters"""
    print("\n" + "="*70)
    print("OFFSET BEARING ANALYSIS")
    print("="*70)

    target_letters = list(K4_KEY)
    print(f"\nK4 Key to match: {K4_KEY}")
    print(f"\nTrying to find bearing offsets for each key letter:")

    bearing_base = CIA_TO_BERLIN

    for i, target in enumerate(target_letters[:10]):  # First 10 letters
        # Try: base bearing + (i * some_offset)
        offsets = [0, 15, 30, 45, 60, 90]
        found = False

        for offset in offsets:
            test_bearing = (bearing_base + (i * offset)) % 360
            test_letter = bearing_to_letter(test_bearing)

            if test_letter == target:
                print(f"  Position {i}: {target} ← bearing {test_bearing:.1f}° (base + {i}*{offset}°)")
                found = True
                break

        if not found:
            print(f"  Position {i}: {target} ← NO MATCH FOUND")

def analyze_reverse_operation():
    """Work backwards: given key letters, what bearings would produce them?"""
    print("\n" + "="*70)
    print("REVERSE OPERATION: KEY LETTERS → REQUIRED BEARINGS")
    print("="*70)

    print(f"\nK4 Key: {K4_KEY}")
    print(f"\nTo encode each key letter, we would need bearing:")

    for i, letter in enumerate(K4_KEY):
        letter_value = ord(letter) - ord('A')
        # Reverse: letter_index = round((bearing / 360) * 26) % 26
        # So: bearing = (letter_index / 26) * 360
        bearing = (letter_value / 26) * 360
        print(f"  {letter} (pos {i:2d}): {bearing:7.2f}°")

    print(f"\nCompare to actual triangle bearings:")
    print(f"  CIA → Berlin:    {CIA_TO_BERLIN:.2f}°")
    print(f"  Berlin → Valley: {BERLIN_TO_VALLEY:.2f}°")
    print(f"  Valley → CIA:    {VALLEY_TO_CIA:.2f}°")

def check_multiple_triangles():
    """Check if rotating/scaling the triangle produces different bearing patterns"""
    print("\n" + "="*70)
    print("MULTIPLE TRIANGLE PATTERNS")
    print("="*70)

    base_bearings = [CIA_TO_BERLIN, BERLIN_TO_VALLEY, VALLEY_TO_CIA]

    for scale in [1, 2, 3]:
        print(f"\nScale factor {scale}:")
        scaled = [b * scale for b in base_bearings]
        letters = [bearing_to_letter(b) for b in scaled]
        sequence = ''.join(letters)
        print(f"  Bearings: {[f'{b:.1f}' for b in scaled]}")
        print(f"  Letters: {sequence}")

def analyze_gap_lengths_as_bearings():
    """Analyze if K4 gap lengths encode as bearing offsets"""
    print("\n" + "="*70)
    print("GAP LENGTHS AS BEARING OFFSETS")
    print("="*70)

    gaps = [11, 38, 9, 9]
    base_bearing = CIA_TO_BERLIN

    print(f"\nBase bearing (CIA → Berlin): {base_bearing:.2f}°")
    print(f"K4 gap lengths: {gaps}")

    print(f"\nApplying gaps as bearing offsets:")
    for i, gap in enumerate(gaps):
        offset_bearing = (base_bearing + gap) % 360
        letter = bearing_to_letter(offset_bearing)
        print(f"  Gap {i+1} ({gap}°): {base_bearing:.1f}° + {gap}° = {offset_bearing:.1f}° → {letter}")

    # Also try cumulative
    print(f"\nCumulative gap offsets:")
    cumulative = 0
    for i, gap in enumerate(gaps):
        cumulative += gap
        offset_bearing = (base_bearing + cumulative) % 360
        letter = bearing_to_letter(offset_bearing)
        print(f"  Gaps 1-{i+1} ({cumulative}°): {base_bearing:.1f}° + {cumulative}° = {offset_bearing:.1f}° → {letter}")

def analyze_position_bearing_relationship():
    """Check if bearing encodes the position in plaintext where it should appear"""
    print("\n" + "="*70)
    print("BEARING ↔ PLAINTEXT POSITION RELATIONSHIP")
    print("="*70)

    plaintext_positions = {
        'BERLINCLOCK': 63,
        'NORTHEAST': 16,
        'UNDER': 0,
        'ABOVE': 83
    }

    bearings_named = {
        'CIA→Berlin': CIA_TO_BERLIN,
        'Berlin→Valley': BERLIN_TO_VALLEY,
        'Valley→CIA': VALLEY_TO_CIA
    }

    print(f"\nKey words in plaintext:")
    for word, pos in plaintext_positions.items():
        print(f"  {word:15s} at position {pos:2d}")

    print(f"\nTriangle bearings:")
    for name, bearing in bearings_named.items():
        print(f"  {name:15s}: {bearing:7.2f}°")

    print(f"\nRelationship check:")
    for name, bearing in bearings_named.items():
        modulo_97 = int(bearing) % 97
        modulo_29 = int(bearing) % 29
        print(f"  {name:15s}: {bearing:7.2f}° mod 97 = {modulo_97:2d}, mod 29 = {modulo_29:2d}")

    print(f"\nSignificant positions mod values:")
    for word, pos in plaintext_positions.items():
        mod_29 = pos % 29
        print(f"  {word:15s} pos {pos:2d}: mod 29 = {mod_29:2d}")

def main():
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + " K4 BEARING-TO-LETTER MAPPING ANALYSIS ".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)

    # Main analyses
    bearing_sequence = analyze_bearing_sequences()

    # Individual bearing analysis
    find_bearing_in_key(CIA_TO_BERLIN)
    find_bearing_in_key(BERLIN_TO_VALLEY)
    find_bearing_in_key(VALLEY_TO_CIA)

    # Offset analysis
    calculate_offset_bearings()

    # Reverse operation
    analyze_reverse_operation()

    # Multiple triangles
    check_multiple_triangles()

    # Gap lengths as offsets
    analyze_gap_lengths_as_bearings()

    # Position relationships
    analyze_position_bearing_relationship()

    # Summary
    print("\n" + "="*70)
    print("SUMMARY OF BEARING-LETTER ANALYSIS")
    print("="*70)
    print(f"""
FINDINGS:

1. Triangle Bearing Letters:
   - CIA → Berlin (44.42°) → D
   - Berlin → Valley (144.22°) → K
   - Valley → CIA (312.91°) → X
   Sequence: D-K-X (does NOT appear in K4 key consecutively)

2. Coordinate Modulo-26 Encoding:
   - Individual bearings encode to specific letters
   - These letters may mark positions in the key/plaintext

3. Gap Lengths (11, 38, 9, 9):
   - May represent bearing offsets from base (44.42°)
   - Cumulative offsets would generate different letters

4. Position Encoding:
   - BERLINCLOCK at position 63
   - NORTHEAST at position 16
   - UNDER at position 0
   - ABOVE at position 83
   - These positions may relate to bearing calculations

5. Key Discovery:
   - The bearing D-K-X sequence starts with D (position 0)
   - First letter of K4 key IS D
   - This may not be coincidence!

HYPOTHESIS: K4's cipher key can be partially derived from:
  1. Triangle bearings as initial/reference values
  2. Gap lengths as offset increments
  3. Position encoding for message placement
""")

if __name__ == "__main__":
    main()
