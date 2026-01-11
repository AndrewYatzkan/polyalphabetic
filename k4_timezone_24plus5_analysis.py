#!/usr/bin/env python3
"""
K4 TIMEZONE MAPPING ANALYSIS: Period 29 = 24 (Zones) + 5 (Special)

Theory: K4's period 29 key encodes:
- Positions 0-23: Berlin Clock's 24 time zones (UTC-12 to UTC+11)
- Positions 24-28: Special markers (K1/K2 embedding, validation, or signature)

Key: DIJJQELYOIECBAQKVAATCRDUMPABT (29 characters)
"""

import sys
from collections import defaultdict

# ==================== TIMEZONE AND CITY DATA ====================

# Berlin Clock cities by UTC offset (24 main zones)
# Format: (UTC offset, representative cities)
BERLIN_CLOCK_ZONES = [
    (-12, "Baker Island", "BIS"),           # Zone 0: UTC-12
    (-11, "American Samoa", "ASM"),          # Zone 1: UTC-11
    (-10, "Hawaii-Honolulu", "HON"),         # Zone 2: UTC-10
    (-9, "Alaska-Anchorage", "ANC"),         # Zone 3: UTC-9
    (-8, "Los Angeles-PDT", "LAX"),          # Zone 4: UTC-8
    (-7, "Denver-MST", "DEN"),               # Zone 5: UTC-7
    (-6, "Chicago-CST", "CHI"),              # Zone 6: UTC-6
    (-5, "New York-EST", "NYC"),             # Zone 7: UTC-5
    (-4, "Caracas-VET", "CCS"),              # Zone 8: UTC-4
    (-3, "Rio Janeiro-BRT", "RIO"),          # Zone 9: UTC-3
    (-2, "Mid-Atlantic", "MID"),             # Zone 10: UTC-2
    (-1, "Azores-AZOT", "PDL"),              # Zone 11: UTC-1
    (0, "London-GMT", "LHR"),                # Zone 12: UTC+0
    (1, "Berlin-CET", "BER"),                # Zone 13: UTC+1
    (2, "Cairo-EET", "CAI"),                 # Zone 14: UTC+2
    (3, "Moscow-MSK", "MOW"),                # Zone 15: UTC+3
    (4, "Dubai-GST", "DXB"),                 # Zone 16: UTC+4
    (5, "Karachi-PKT", "KHI"),               # Zone 17: UTC+5
    (5.5, "New Delhi-IST", "DEL"),           # Zone 18: UTC+5:30
    (6, "Bangkok-ICT", "BKK"),               # Zone 19: UTC+6
    (7, "Jakarta-WIB", "CGK"),               # Zone 20: UTC+7
    (8, "Beijing-CST", "PEI"),               # Zone 21: UTC+8
    (9, "Tokyo-JST", "TYO"),                 # Zone 22: UTC+9
    (10, "Sydney-AEST", "SYD"),              # Zone 23: UTC+10
]

# Special positions 24-28 candidates
SPECIAL_POSITIONS = {
    24: "K1_EMBEDDING",
    25: "K2_EMBEDDING",
    26: "VALIDATION_1",
    27: "VALIDATION_2",
    28: "SIGNATURE",
}

# The known period-29 key
KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# ==================== ANALYSIS FUNCTIONS ====================

def analyze_basic_structure():
    """Analyze the basic 24+5 structure of the key."""
    print("=" * 70)
    print("1. BASIC STRUCTURE ANALYSIS: 24 + 5 = 29")
    print("=" * 70)

    key_24 = KEY[:24]
    key_5 = KEY[24:29]

    print(f"\nPeriod 29 Key: {KEY}")
    print(f"Positions 0-23 (24 zones):     {key_24}")
    print(f"Positions 24-28 (5 special):   {key_5}")
    print(f"\nKey breakdown by position:")
    for i, char in enumerate(KEY):
        zone_type = f"Zone {i-12} (UTC{i-12:+d})" if i < 12 else \
                    f"Zone UTC{i-12:+d}" if i < 24 else \
                    f"Special[{i-24}]"
        print(f"  Pos {i:2d}: {char} - {zone_type}")


def analyze_timezone_mapping():
    """Test if positions 0-23 map directly to timezone UTC values."""
    print("\n" + "=" * 70)
    print("2. TIMEZONE UTC OFFSET MAPPING ANALYSIS")
    print("=" * 70)

    print("\nHypothesis: Key letter values (A=0...Z=25) encode UTC offsets (±12)")
    print("UTC range: UTC-12 to UTC+11 (24 zones)\n")

    # Test 1: Direct letter position as timezone
    print("Test 1: Position index = UTC offset (with -12 adjustment)")
    print("-" * 70)

    for pos in range(24):
        key_char = KEY[pos]
        letter_value = ord(key_char) - ord('A')

        # Map position to timezone
        timezone_direct = pos - 12  # Position 0 = UTC-12, Position 12 = UTC+0, Position 23 = UTC+11
        timezone_from_letter = letter_value - 12  # If A=0 means UTC-12

        # Get Berlin Clock data for this position
        utc_offset, city, code = BERLIN_CLOCK_ZONES[pos]

        print(f"Pos {pos:2d} ({city:20s}): Key={key_char} " +
              f"(val={letter_value:2d}) | Timezone: UTC{timezone_direct:+3d} | " +
              f"FromLetter: UTC{timezone_from_letter:+3d} | Actual: UTC{utc_offset:+.1f}")

    # Test 2: Letter value = UTC offset + constant
    print("\nTest 2: Analyzing letter value patterns across positions")
    print("-" * 70)

    letter_values = [ord(KEY[i]) - ord('A') for i in range(24)]
    print(f"Letter values (A=0...Z=25): {letter_values}")
    print(f"Min: {min(letter_values)}, Max: {max(letter_values)}, Mean: {sum(letter_values)/len(letter_values):.1f}")

    # Check if there's a relationship
    for pos in range(24):
        letter_val = letter_values[pos]
        utc_offset, _, _ = BERLIN_CLOCK_ZONES[pos]

        # Try various transformations
        offset_as_val = utc_offset + 12  # UTC-12 → 0, UTC+0 → 12, UTC+12 → 24
        diff = letter_val - offset_as_val

        if abs(diff) < 26:  # Check modulo 26 relationship
            print(f"Pos {pos:2d}: Letter={letter_val:2d}, (UTC+12)={offset_as_val:5.1f}, Diff={diff:+5.1f}")


def analyze_special_sequences():
    """Analyze repeated letters and special sequences."""
    print("\n" + "=" * 70)
    print("3. REPEATED LETTERS AND SPECIAL SEQUENCES")
    print("=" * 70)

    print(f"\nKey: {KEY}\n")

    # Find repeated letters
    print("Repeated letters analysis:")
    letter_positions = defaultdict(list)
    for pos, char in enumerate(KEY):
        letter_positions[char].append(pos)

    print(f"\n{'Letter':^10} {'Positions':^40} {'Count':^5}")
    print("-" * 55)

    for letter in sorted(letter_positions.keys()):
        positions = letter_positions[letter]
        if len(positions) > 1:
            print(f"{letter:^10} {str(positions):^40} {len(positions):^5}")

    # Special sequences
    print("\n\nSpecial sequences (double letters, etc.):")
    print("-" * 70)

    for i in range(len(KEY)-1):
        if KEY[i] == KEY[i+1]:
            print(f"Position {i}-{i+1}: {KEY[i]}{KEY[i+1]} (Double at {i}, {i+1})")

    # JJ analysis
    print("\n\nDETAILED: 'JJ' at Positions 2-3")
    print("-" * 70)
    print(f"Key positions 2-3: {KEY[2:4]} (both 'J')")
    print(f"J = letter value 9 (A=0)")
    print(f"These correspond to:")
    for i in [2, 3]:
        utc_offset, city, code = BERLIN_CLOCK_ZONES[i]
        print(f"  Position {i}: {city:20s} (UTC{utc_offset:+.1f})")
    print("\nInterpretation:")
    print("  Zone 2 = UTC-10 (Hawaii)")
    print("  Zone 3 = UTC-9 (Alaska)")
    print("  JJ could represent: 10-9=1 (adjacent zones)")
    print("  Or: J=10 (Hawaiian ISO), J=10 (Alaskan ISO)?")


def analyze_city_name_initials():
    """Check if key spells out city names when mapped to zones."""
    print("\n" + "=" * 70)
    print("4. CITY NAME INITIAL MAPPING")
    print("=" * 70)

    print("\nTest: Do key letters match city name initials?\n")

    print(f"{'Pos':^4} {'Zone':^15} {'Key':^4} {'City':^25} {'Initial':^8} {'Match':^6}")
    print("-" * 70)

    matches = 0
    for pos in range(24):
        key_char = KEY[pos]
        utc_offset, city, _ = BERLIN_CLOCK_ZONES[pos]
        city_initial = city[0]
        is_match = "✓" if key_char == city_initial else ""

        if key_char == city_initial:
            matches += 1

        print(f"{pos:4d} {f'UTC{utc_offset:+.1f}':^15} {key_char:^4} " +
              f"{city:^25} {city_initial:^8} {is_match:^6}")

    print(f"\nMatches: {matches}/24 ({100*matches/24:.1f}%)")

    # Check reverse: which cities match key letters
    print("\n\nReverse check: Cities that START with key letters")
    print("-" * 70)

    for pos in range(24):
        key_char = KEY[pos]
        utc_offset, city, _ = BERLIN_CLOCK_ZONES[pos]

        # Find all cities starting with this letter from all zones
        matching_cities = []
        for p in range(24):
            _, c, _ = BERLIN_CLOCK_ZONES[p]
            if c[0] == key_char:
                matching_cities.append(c)

        if city[0] != key_char and len(matching_cities) > 0:
            print(f"Pos {pos}: Key='{key_char}' but city='{city}'")
            print(f"  → Could map to: {', '.join(set(matching_cities))}")


def analyze_letter_value_patterns():
    """Analyze letter values as numbers."""
    print("\n" + "=" * 70)
    print("5. LETTER VALUE PATTERN ANALYSIS (A=0 to Z=25)")
    print("=" * 70)

    print(f"\nKey: {KEY}\n")

    print(f"{'Pos':^4} {'Zone':^12} {'Letter':^6} {'Value':^6} {'UTC':^8}")
    print("-" * 50)

    for pos in range(24):
        key_char = KEY[pos]
        letter_value = ord(key_char) - ord('A')
        utc_offset, city, _ = BERLIN_CLOCK_ZONES[pos]

        print(f"{pos:4d} {f'UTC{utc_offset:+.1f}':^12} {key_char:^6} " +
              f"{letter_value:^6d} {f'UTC{utc_offset:+.1f}':^8}")

    # Find patterns
    letter_values = [ord(KEY[i]) - ord('A') for i in range(24)]

    print("\n\nPattern Detection:")
    print("-" * 70)
    print(f"Min value: {min(letter_values)} ({chr(ord('A') + min(letter_values))})")
    print(f"Max value: {max(letter_values)} ({chr(ord('A') + max(letter_values))})")
    print(f"Range: {max(letter_values) - min(letter_values)}")
    print(f"Expected range for UTC-12 to UTC+11: 24 values")

    # Check if it's a permutation or shifted pattern
    value_freq = defaultdict(int)
    for v in letter_values:
        value_freq[v] += 1

    print(f"\nValue frequency:")
    for v in sorted(value_freq.keys()):
        letter = chr(ord('A') + v)
        count = value_freq[v]
        print(f"  Value {v:2d} ({letter}): {count}x")


def analyze_special_5_positions():
    """Analyze positions 24-28 (special markers)."""
    print("\n" + "=" * 70)
    print("6. SPECIAL POSITIONS 24-28 ANALYSIS")
    print("=" * 70)

    special_key = KEY[24:29]
    print(f"\nSpecial positions key: {special_key}")
    print(f"Individual letters: {' '.join(special_key)}\n")

    print(f"{'Pos':^4} {'Letter':^8} {'Value':^8} {'Candidate Purpose':^40}")
    print("-" * 60)

    for pos in range(24, 29):
        key_char = KEY[pos]
        letter_value = ord(key_char) - ord('A')
        purpose = SPECIAL_POSITIONS.get(pos, "Unknown")

        print(f"{pos:4d} {key_char:^8} {letter_value:^8d} {purpose:^40}")

    print("\n\nHypothesis Testing for MPABT:")
    print("-" * 70)

    # M P A B T
    test_hypotheses = {
        "K1_K2_EMBEDDING": "Could M-P represent K1 and K2 messages",
        "VALIDATION": "Could A-B-T be checksum or validation",
        "COORDINATES": "M=13 (lat), P=16 (lon)?",
        "BERLIN_REFERENCE": "M (Moscow?), P (Paris?), A (Athens?), B (Berlin), T (Tokyo?)",
        "ALPHABET_MARKER": "MPABT could mark positions in keyed alphabet",
        "SIGNATURE": "Could spell part of Sanborn's name or hidden message",
    }

    for hypothesis, description in test_hypotheses.items():
        print(f"\n{hypothesis}:")
        print(f"  {description}")
        if hypothesis == "BERLIN_REFERENCE":
            print(f"  M={ord('M')-ord('A')}, P={ord('P')-ord('A')}, A={ord('A')-ord('A')}, " +
                  f"B={ord('B')-ord('A')}, T={ord('T')-ord('A')}")


def analyze_double_jj():
    """Deep dive into the JJ pattern at positions 2-3."""
    print("\n" + "=" * 70)
    print("7. DEEP DIVE: JJ AT POSITIONS 2-3")
    print("=" * 70)

    print(f"\nKey: {KEY}")
    print(f"     {''.join(['↑' if i in [2,3] else ' ' for i in range(29)])}")
    print(f"     Positions 2-3: JJ\n")

    # Geographic analysis
    print("Geographic Context:")
    print("-" * 70)
    for i in [2, 3]:
        utc_offset, city, code = BERLIN_CLOCK_ZONES[i]
        print(f"Position {i}: {city:20s} (UTC{utc_offset:+.1f})")

        if i == 2:
            print(f"  → UTC-10: Hawaii/Honolulu time zone")
            print(f"  → J = 10th letter (could mean: UTC-10)")
        elif i == 3:
            print(f"  → UTC-9: Alaska/Anchorage time zone")
            print(f"  → J = 10th letter (could mean: UTC-9 ≈ 10?)")

    print("\n\nPattern Interpretation:")
    print("-" * 70)
    print("Theory 1: JJ = Double J for Western Hemisphere transition")
    print("  Hawaii (UTC-10) and Alaska (UTC-9) are both far west")
    print("  JJ marks the western edge of continental Americas")

    print("\nTheory 2: JJ = Letter value encoding UTC offsets")
    print(f"  J = {ord('J')-ord('A')} (10th letter)")
    print("  Could represent: UTC-10 (Hawaii)")
    print("  Could represent: 10 as abstract number")

    print("\nTheory 3: JJ = K1/K2 embedding trigger")
    print("  Double letter marks a special transition")
    print("  Beginning of Americas region in clockwise order")
    print("  Could signal 'embedded message' mode")

    print("\nTheory 4: JJ = Bearing/Distance encoding")
    print("  Hawaii to Alaska bearing or distance relationship")
    print("  Hawaii: ~20°N, 157°W")
    print("  Alaska: ~61°N, 149°W")


def analyze_geographic_order():
    """Analyze if key follows geographic order around the world."""
    print("\n" + "=" * 70)
    print("8. GEOGRAPHIC ORDER ANALYSIS")
    print("=" * 70)

    print("\nAnalyzing if key follows a geographic progression...\n")

    print("WESTBOUND from Prime Meridian (starting at UTC+0):")
    print("-" * 70)

    westbound = []
    for pos in range(24):
        utc_offset, city, code = BERLIN_CLOCK_ZONES[pos]
        key_char = KEY[pos]

        # Group by hemisphere
        hemisphere = "Western" if utc_offset < 0 else "Eastern"

        westbound.append({
            'pos': pos,
            'offset': utc_offset,
            'city': city,
            'key': key_char,
            'hemisphere': hemisphere
        })

    # Print sorted by longitude
    westbound_sorted = sorted(westbound, key=lambda x: x['offset'])

    for item in westbound_sorted:
        print(f"UTC{item['offset']:+6.1f}: {item['city']:20s} → Key: {item['key']:^2} " +
              f"({item['hemisphere']})")

    print("\n\nPattern check: Does key follow geographic/alphabetic order?")
    print("-" * 70)

    # Check for alphabetic progression
    key_seq = [KEY[i] for i in range(24)]
    print(f"Key sequence: {''.join(key_seq)}")

    # Check for increasing/decreasing letter values
    changes = []
    for i in range(1, 24):
        curr = ord(KEY[i]) - ord('A')
        prev = ord(KEY[i-1]) - ord('A')
        change = curr - prev
        changes.append(change)

    ups = sum(1 for c in changes if c > 0)
    downs = sum(1 for c in changes if c < 0)

    print(f"\nLetter value changes: {ups} increases, {downs} decreases")
    print(f"Pattern appears: {'random' if ups > 10 else 'structured'}")


def analyze_k1_k2_embedding():
    """Test if K1/K2 clues are embedded in K4 key."""
    print("\n" + "=" * 70)
    print("9. K1 AND K2 EMBEDDING TEST")
    print("=" * 70)

    print("\nK1-K3 Known Information:")
    print("-" * 70)
    print("K1 Plaintext: KRYPTOSABCDEFGHIKLMNOPQUVWXYZ")
    print("K2 Plaintext: BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT...")
    print("  K2 Key: PALIMPSEST")
    print("  K2 Contains: CIA coordinates (38°57'N, 77°8'W)")
    print("K3 Plaintext: SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE PRIMARY CHANNEL EMERGED...")
    print("  K3 Key: KRYPTOS")

    print("\n\nSearching for K1/K2 references in K4 key...")
    print("-" * 70)

    k4_key = KEY

    # Search for K1 clues
    print("\nK1 References in K4:")
    if "KRYPTOS" in k4_key:
        print("  ✓ KRYPTOS found in K4 key!")
        idx = k4_key.index("KRYPTOS")
        print(f"    Position: {idx}")
    else:
        print("  ✗ KRYPTOS not directly in K4 key")

    if "KRYPT" in k4_key:
        print("  ✓ KRYPT found in K4 key!")
        idx = k4_key.index("KRYPT")
        print(f"    Position: {idx}")

    # Search for K2 clues
    print("\nK2 References in K4:")
    if "PALIMPSEST" in k4_key:
        print("  ✓ PALIMPSEST found in K4 key!")
    else:
        print("  ✗ PALIMPSEST not directly in K4 key")

    if "PAL" in k4_key:
        print("  ✓ PAL found in K4 key!")
        idx = k4_key.index("PAL")
        print(f"    Position: {idx}")

    # Special position analysis
    print("\n\nSpecial positions (24-28) detailed:")
    print(f"  {KEY[24:29]} = MPABT")
    print(f"  Could contain: PAL (from K2 PALIMPSEST)?")

    if "PAL" in KEY[20:]:
        print(f"  ✓ PAL appears in positions 20+!")
        for i in range(20, 26):
            if KEY[i:i+3] == "PAL":
                print(f"    Position {i}: {KEY[i:i+3]}")


def create_visualization():
    """Create a visual representation of the timezone mapping."""
    print("\n" + "=" * 70)
    print("10. VISUAL REPRESENTATION")
    print("=" * 70)

    print("\nK4 Key mapped to 24 Time Zones:")
    print("-" * 70)
    print("\nWESTERN HEMISPHERE (UTC-12 to UTC-1):")
    print()

    for i in range(12):
        utc_offset, city, code = BERLIN_CLOCK_ZONES[i]
        key_char = KEY[i]
        bar = "█" * max(1, (i % 6) + 1)
        print(f"Pos {i:2d} | UTC{utc_offset:+6.1f} | {city:20s} | Key: {key_char} {bar}")

    print("\nEASTERN HEMISPHERE (UTC+0 to UTC+11):")
    print()

    for i in range(12, 24):
        utc_offset, city, code = BERLIN_CLOCK_ZONES[i]
        key_char = KEY[i]
        bar = "█" * ((i - 12) % 6 + 1)
        print(f"Pos {i:2d} | UTC{utc_offset:+6.1f} | {city:20s} | Key: {key_char} {bar}")

    print("\nSPECIAL POSITIONS (24-28):")
    print()

    for i in range(24, 29):
        key_char = KEY[i]
        purpose = SPECIAL_POSITIONS.get(i, "Unknown")
        print(f"Pos {i} | {key_char} | {purpose}")


# ==================== MAIN EXECUTION ====================

def main():
    """Run all analyses."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "K4 TIMEZONE 24+5 STRUCTURE ANALYSIS" + " " * 18 + "║")
    print("║" + " " * 68 + "║")
    print("║" + f" Key: {KEY}" + " " * 33 + "║")
    print("║" + f" Period: 29 = 24 zones + 5 special" + " " * 32 + "║")
    print("╚" + "=" * 68 + "╝")

    analyze_basic_structure()
    analyze_timezone_mapping()
    analyze_repeated_letters()
    analyze_special_sequences()
    analyze_city_name_initials()
    analyze_letter_value_patterns()
    analyze_special_5_positions()
    analyze_double_jj()
    analyze_geographic_order()
    analyze_k1_k2_embedding()
    create_visualization()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


def analyze_repeated_letters():
    """Placeholder for repeated letters."""
    pass


if __name__ == "__main__":
    main()
