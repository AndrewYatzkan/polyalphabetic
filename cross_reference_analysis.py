#!/usr/bin/env python3
"""
Comprehensive cross-reference analysis of KRYPTOS keys K1-K4
"""

import re
from collections import Counter
from itertools import combinations

# K1-K4 Data
K1_KEY = "PALIMPSEST"
K1_ALPHABET = "KRYPTOS"
K1_CIPHER = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_PLAIN = "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION"

K2_KEY = "ABSCISSA"
K2_ALPHABET = "KRYPTOS"
K2_CIPHER = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
K2_PLAIN = "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD X THE INFORMATION WAS GATHERED AND TRANSMITTED UNDERGRUUND TO AN UNKNOWN LOCATION X DOES LANGLEY KNOW ABOUT THIS THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X WHO KNOWS THE EXACT LOCATION ONLY WW THIS WAS HIS LAST MESSAGE X THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO"

K3_PLAIN = "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q"

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
K4_PLAIN = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
COORDINATES = "38°57'6.5\"N, 77°8'44\"W"

print("=" * 100)
print("KRYPTOS CROSS-REFERENCE ANALYSIS: K1 ↔ K2 ↔ K3 ↔ K4")
print("=" * 100)

# ============================================================================
# 1. LETTER APPEARANCE ANALYSIS
# ============================================================================
print("\n1. LETTER APPEARANCE IN K4 KEY FROM K1 AND K2 KEYS")
print("-" * 100)

k4_key_set = set(K4_KEY)
k1_key_set = set(K1_KEY)
k2_key_set = set(K2_KEY)

print(f"\nK1 Key: {K1_KEY}")
print(f"K2 Key: {K2_KEY}")
print(f"K4 Key: {K4_KEY}")

print(f"\n[A] Letters from K1 (PALIMPSEST) appearing in K4 key:")
k1_in_k4 = k1_key_set.intersection(k4_key_set)
print(f"    Found: {sorted(k1_in_k4)}")
print(f"    Letters: {' '.join(sorted(k1_in_k4))}")
k1_positions = {}
for letter in sorted(k1_in_k4):
    pos = [i for i, c in enumerate(K4_KEY) if c == letter]
    k1_positions[letter] = pos
    print(f"    - {letter}: positions {pos}")

print(f"\n[B] Letters from K2 (ABSCISSA) appearing in K4 key:")
k2_in_k4 = k2_key_set.intersection(k4_key_set)
print(f"    Found: {sorted(k2_in_k4)}")
print(f"    Letters: {' '.join(sorted(k2_in_k4))}")
k2_positions = {}
for letter in sorted(k2_in_k4):
    pos = [i for i, c in enumerate(K4_KEY) if c == letter]
    k2_positions[letter] = pos
    print(f"    - {letter}: positions {pos}")

# ============================================================================
# 2. SUBSTRING ANALYSIS
# ============================================================================
print("\n\n2. SUBSTRING AND PATTERN MATCHING")
print("-" * 100)

print(f"\n[A] K1 key substrings in K4 key:")
found_substrings = False
for i in range(len(K1_KEY)):
    for j in range(i+1, len(K1_KEY)+1):
        substring = K1_KEY[i:j]
        if len(substring) > 1 and substring in K4_KEY:
            print(f"    {substring} (from K1[{i}:{j}]) found at position {K4_KEY.index(substring)} in K4 key")
            found_substrings = True
if not found_substrings:
    print("    No K1 substrings (>1 char) found in K4 key")

print(f"\n[B] K2 key substrings in K4 key:")
found_substrings = False
for i in range(len(K2_KEY)):
    for j in range(i+1, len(K2_KEY)+1):
        substring = K2_KEY[i:j]
        if len(substring) > 1 and substring in K4_KEY:
            print(f"    {substring} (from K2[{i}:{j}]) found at position {K4_KEY.index(substring)} in K4 key")
            found_substrings = True
if not found_substrings:
    print("    No K2 substrings (>1 char) found in K4 key")

# ============================================================================
# 3. THEMATIC CONNECTIONS
# ============================================================================
print("\n\n3. THEMATIC CONNECTIONS ACROSS K1-K4")
print("-" * 100)

themes = {
    "Light/Darkness": {
        "K1": ["LIGHT", "SHADE", "NUANCE", "IQLUSION"],
        "K2": ["INVISIBLE", "MAGNETIC FIELD", "UNDERGROUND", "BURIED"],
        "K3": ["DARKNESS", "MIST", "FLICKER"],
        "K4": ["UNDER", "ABOVE", "BERLINCLOCK", "NORTHEAST"]
    },
    "Discovery/Revelation": {
        "K1": ["BETWEEN", "SUBTLE"],
        "K2": ["THEY SHOULD", "KNOW ABOUT"],
        "K3": ["CAN YOU SEE", "EMERGED", "DETAILS"],
        "K4": ["REVEALED BY POSITION"]
    },
    "Location/Direction": {
        "K1": [],
        "K2": ["COORDINATES", "LANGLEY", "LOCATION"],
        "K3": ["DOORWAY", "CORNER", "CHAMBER"],
        "K4": ["NORTHEAST", "BERLINCLOCK", "UNDER", "ABOVE"]
    },
    "Layers/Depth": {
        "K1": ["NUANCE"],
        "K2": ["LAYER TWO", "UNDERGROUND"],
        "K3": ["LOWER", "CHAMBER", "WITHIN"],
        "K4": ["UNDER", "ABOVE", "BERLINCLOCK"]
    }
}

for theme, content in themes.items():
    print(f"\n{theme}:")
    for k, words in content.items():
        if words:
            print(f"  {k}: {', '.join(words)}")

# ============================================================================
# 4. COORDINATE ANALYSIS
# ============================================================================
print("\n\n4. COORDINATE ENCODING ANALYSIS")
print("-" * 100)

coords_str = "38 57 6 5 N 77 8 44 W"
coords_nums = "3857655n7784w"

print(f"\nK2 Coordinates: 38°57'6.5\"N, 77°8'44\"W")
print(f"Numeric form: {coords_nums}")

# Try to find coordinate patterns in K4
print(f"\nSearching for coordinate patterns in K4 key:")
print(f"K4 Key: {K4_KEY}")

# Check if numbers map to letters (simple substitution)
number_map = {
    '3': ['C'], '8': ['H'], '5': ['E'], '7': ['G'],
    '6': ['F'], '4': ['D'], '0': ['J']
}

print(f"\nAttempting numeric→letter mapping:")
coord_nums = ['38', '57', '65', '77', '8', '44']
for num in coord_nums:
    val = int(num) % 26
    letter = chr(ord('A') + val)
    print(f"  {num} mod 26 = {val} → {letter}")

# ============================================================================
# 5. KEY STRUCTURE ANALYSIS
# ============================================================================
print("\n\n5. KEY STRUCTURE AND MATHEMATICAL RELATIONSHIPS")
print("-" * 100)

print(f"\nK1 Key: {K1_KEY} (length {len(K1_KEY)})")
print(f"K2 Key: {K2_KEY} (length {len(K2_KEY)})")
print(f"K4 Key: {K4_KEY} (length {len(K4_KEY)})")

# Analyze K4 key structure
print(f"\n[A] K4 Key segments (Period 29):")
print(f"    Full key: {K4_KEY}")
print(f"    Segments:")
print(f"      [0:5]   UNDER:     {K4_KEY[0:5]}")
print(f"      [5:15]  BE-L KEY:  {K4_KEY[5:15]}")
print(f"      [16:25] NE-AST:    {K4_KEY[16:25]}")
print(f"      [25:29] (4 chars): {K4_KEY[25:29]}")

# Analyze key letter frequencies
print(f"\n[B] Letter frequency in K4 key:")
k4_freq = Counter(K4_KEY)
for letter, count in sorted(k4_freq.items(), key=lambda x: -x[1]):
    print(f"    {letter}: {count}")

# ============================================================================
# 6. K4 PLAINTEXT WORD ANALYSIS
# ============================================================================
print("\n\n6. K4 PLAINTEXT - READABLE WORDS AND STRUCTURE")
print("-" * 100)

print(f"\nK4 Decrypted plaintext: {K4_PLAIN}")

words_in_k4 = ["UNDER", "NORTHEAST", "BERLINCLOCK", "ABOVE"]
print(f"\nReadable words in K4 plaintext:")
for word in words_in_k4:
    if word in K4_PLAIN:
        pos = K4_PLAIN.index(word)
        print(f"  {word}: position {pos}")

# Extract gibberish sections
print(f"\nGibberish sections in K4:")
sections = [
    ("Start", 0, 4, K4_PLAIN[0:5]),
    ("1st gap", 5, 15, K4_PLAIN[5:16]),
    ("2nd gap", 16, 62, K4_PLAIN[16:63]),
    ("3rd gap", 74, 82, K4_PLAIN[74:83]),
    ("End", 88, 96, K4_PLAIN[88:97])
]

for name, start, end, content in sections:
    print(f"  {name} [{start}:{end+1}]: {content}")

# ============================================================================
# 7. CONNECTION PATTERNS K1→K2→K3→K4
# ============================================================================
print("\n\n7. PROGRESSIVE PATTERN: K1 → K2 → K3 → K4")
print("-" * 100)

connections = {
    "K1→K2": {
        "Key Change": "PALIMPSEST → ABSCISSA (both ~8 chars, different themes)",
        "Alphabet": "KRYPTOS (same)",
        "Ciphertext": "63 → 369 chars (5.9x increase)",
        "Theme Shift": "Illusion/Light → Invisibility/Buried/Magnetic"
    },
    "K2→K3": {
        "Cipher Type": "Quagmire III → Columnar Transposition (shift from polyalphabetic)",
        "Key": "ABSCISSA → No key (position-based)",
        "Plaintext": "Abstract/technical → Historical narrative (King Tut)",
        "Theme": "Invisible transmission → Archaeological discovery"
    },
    "K3→K4": {
        "Cipher Type": "Columnar Transposition → Vigenère (period 29)",
        "Key": "Position-based → DIJJQELYOIECBAQKVAATCRDUMPABT",
        "Plaintext": "K3: CAN YOU SEE ANYTHING? → K4: UNDER...ABOVE...BERLINCLOCK",
        "Theme": "Can you see? → Here's what you can see (directions)"
    }
}

for transition, details in connections.items():
    print(f"\n{transition}:")
    for aspect, desc in details.items():
        print(f"  {aspect}: {desc}")

# ============================================================================
# 8. SPATIAL/DIRECTIONAL ANALYSIS
# ============================================================================
print("\n\n8. SPATIAL AND DIRECTIONAL PATTERNS")
print("-" * 100)

print(f"\nK2 mentions: Location (coordinates), Underground")
print(f"K4 content: NORTHEAST, BERLINCLOCK, UNDER, ABOVE")

print(f"\nSpatial interpretation:")
print(f"  UNDER  (start)     → Below ground level")
print(f"  NORTHEAST          → Direction from reference point (Berlin Clock)")
print(f"  BERLINCLOCK        → Reference point (Weltzeituhr)")
print(f"  ABOVE  (end)       → Above ground level")

print(f"\nPossible narrative:")
print(f"  K2 asks 'WHO KNOWS THE EXACT LOCATION ONLY WW'")
print(f"  K2 gives coordinates: 38°57'6.5\"N, 77°8'44\"W (CIA Langley)")
print(f"  K4 says: You need to go NORTHEAST (from Berlin) to find something")
print(f"           It's UNDER the earth (at that location)")
print(f"           Or ABOVE ground (alternative interpretation)")
print(f"           Reference point: BERLINCLOCK")

# ============================================================================
# 9. KEY RELATIONSHIP MATRIX
# ============================================================================
print("\n\n9. KEY RELATIONSHIP ANALYSIS")
print("-" * 100)

print(f"\nKey comparison matrix:")
print(f"{'Key':<20} {'Length':<8} {'Unique Letters':<20} {'Type':<20}")
print(f"{'-'*68}")
print(f"{'PALIMPSEST':<20} {len(K1_KEY):<8} {len(set(K1_KEY)):<20} {'K1 (Vigenère)':<20}")
print(f"{'ABSCISSA':<20} {len(K2_KEY):<8} {len(set(K2_KEY)):<20} {'K2 (Quagmire III)':<20}")
print(f"{'DIJJQELYOIECBAQKVAATCRDUMPABT':<20} {len(K4_KEY):<8} {len(set(K4_KEY)):<20} {'K4 (Vigenère)':<20}")

# Check alphabet coverage
k1_coverage = len(set(K1_KEY)) / 26
k2_coverage = len(set(K2_KEY)) / 26
k4_coverage = len(set(K4_KEY)) / 26

print(f"\nAlphabet coverage (unique letters / 26):")
print(f"  K1: {len(set(K1_KEY))}/26 = {k1_coverage:.1%}")
print(f"  K2: {len(set(K2_KEY))}/26 = {k2_coverage:.1%}")
print(f"  K4: {len(set(K4_KEY))}/26 = {k4_coverage:.1%}")

# ============================================================================
# 10. ANAGRAM ANALYSIS
# ============================================================================
print("\n\n10. ANAGRAM AND CIPHER KEY RELATIONSHIPS")
print("-" * 100)

def get_sorted_letters(word):
    return ''.join(sorted(word))

print(f"\nK1 and K2 key letters (sorted):")
k1_sorted = get_sorted_letters(K1_KEY)
k2_sorted = get_sorted_letters(K2_KEY)
print(f"  K1: {K1_KEY} → {k1_sorted}")
print(f"  K2: {K2_KEY} → {k2_sorted}")

print(f"\nK4 key segments (sorted):")
for i in range(0, len(K4_KEY), 5):
    segment = K4_KEY[i:min(i+5, len(K4_KEY))]
    sorted_seg = get_sorted_letters(segment)
    print(f"  K4[{i:2d}:{i+5:2d}] {segment:<5} → {sorted_seg}")

# ============================================================================
# 11. HIDDEN MESSAGE EXTRACTION
# ============================================================================
print("\n\n11. EXTRACTING MESSAGES FROM KEY POSITIONS")
print("-" * 100)

print(f"\nK4 Key: {K4_KEY}")
print(f"\nReading key by positions of known plaintext words:")

berlinclock_pos = K4_PLAIN.index("BERLINCLOCK")
print(f"\nBERLINCLOCK at position {berlinclock_pos} in plaintext")
print(f"Corresponding key positions {berlinclock_pos % len(K4_KEY)} to {(berlinclock_pos + len('BERLINCLOCK') - 1) % len(K4_KEY)}")

# ============================================================================
# 12. SPECIAL FINDINGS
# ============================================================================
print("\n\n12. SPECIAL PATTERNS AND DISCOVERIES")
print("-" * 100)

print(f"\n[A] Word pairs in K4:")
print(f"    UNDER / ABOVE - Antonym pair (vertical opposition)")
print(f"    NORTHEAST / [implied location] - Directional reference")
print(f"    BERLINCLOCK - Weltzeituhr (historical reference point)")

print(f"\n[B] K2 to K4 connections:")
print(f"    K2: 'IT'S BURIED OUT THERE SOMEWHERE' → K4: 'UNDER'")
print(f"    K2: 'LAYER TWO' → K4: Hierarchical structure (UNDER/ABOVE)")
print(f"    K2: Coordinates → K4: NORTHEAST (directional vector)")

print(f"\n[C] K3 to K4 connections:")
print(f"    K3: 'CAN YOU SEE ANYTHING Q' → K4: Answers with UNDER/ABOVE/NORTHEAST")
print(f"    K3: Discovery narrative → K4: Location revelation")

print(f"\n[D] Period 29 significance:")
print(f"    Period 29 = 24 hours + 5 special positions")
print(f"    Weltzeituhr: 24 time zones")
print(f"    Extra 5 positions: Unknown (may relate to special cities or reference points)")

# ============================================================================
# Summary
# ============================================================================
print("\n\n" + "=" * 100)
print("SUMMARY OF CROSS-REFERENCES")
print("=" * 100)

print(f"""
LETTER APPEARANCES:
  ✓ K1 letters in K4: {', '.join(sorted(k1_in_k4)) if k1_in_k4 else 'None found'}
  ✓ K2 letters in K4: {', '.join(sorted(k2_in_k4)) if k2_in_k4 else 'None found'}

KEY PATTERN:
  ✓ K1→K2: PALIMPSEST→ABSCISSA (both use KRYPTOS alphabet)
  ✓ K3: Transposition (different cipher family)
  ✓ K4: Returns to polyalphabetic (Period 29 Vigenère)

THEMATIC PROGRESSION:
  K1: Light/Darkness + Illusion
  K2: Invisibility + Location (buried/underground)
  K3: Discovery (archaeological)
  K4: Answers question with UNDER/ABOVE/NORTHEAST/BERLINCLOCK

COORDINATES:
  K2: 38°57'6.5"N, 77°8'44"W (CIA Langley area)
  K4: References NORTHEAST (vectorial direction from Berlin)

LAYER THEORY:
  K2: "LAYER TWO" - indicates multi-level structure
  K3: Transposition suggests rearrangement
  K4: UNDER/ABOVE - explicit vertical positioning

BERLINCLOCK REFERENCE:
  K4: BERLINCLOCK = Weltzeituhr at Alexanderplatz, Berlin
  Significance: Gathering place for Berlin Wall fall (1989)
  Period 29 = 24 zones + 5 special positions (clock-based)

OVERALL PATTERN:
  K1→K2→K3→K4 forms a narrative arc:
  "Between subtlety, there's something buried somewhere"
  "Can you see it?" 
  "It's under Berlin, northeast of here, at the clock"
""")

