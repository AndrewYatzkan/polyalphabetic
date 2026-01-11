#!/usr/bin/env python3
"""
K4 Creative Solution Exploration

Sanborn's hints:
1. "Who says it is even a math solution?"
2. Berlin Clock = Weltzeituhr at Alexanderplatz
3. 1986 Egypt trip + 1989 Berlin Wall fall
4. K5 uses same system, BERLINCLOCK at same position
5. "Creativity is needed"
6. "Delivering a message"
"""

# Known readable plaintext
READABLE = {
    (0, 5): "UNDER",
    (16, 25): "NORTHEAST",
    (63, 74): "BERLINCLOCK",
    (83, 88): "ABOVE"
}

# Gibberish sections
GIBBERISH = {
    (5, 16): "QAPBZDBKZEL",    # 11 chars
    (25, 63): "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",  # 38 chars
    (74, 83): "RSPVJWQUL",     # 9 chars
    (88, 97): "ZOLRKCAYF"      # 9 chars
}

print("=" * 70)
print("K4 CREATIVE SOLUTION EXPLORATION")
print("=" * 70)

# Theory 1: The message is just the readable words
print("\n1. READABLE WORDS ONLY")
print("UNDER ... NORTHEAST ... BERLINCLOCK ... ABOVE")
print("Interpretation: Directions to a location northeast of the Berlin Clock")
print("              with something above and below ground")

# Theory 2: First letters of gibberish spell something
print("\n2. FIRST LETTERS OF SECTIONS")
first_letters = ""
for (start, end), text in sorted(GIBBERISH.items()):
    first_letters += text[0]
print(f"Gibberish first letters: {first_letters}")
print("(QLRZ - doesn't spell anything obvious)")

# Theory 3: Gibberish lengths encode something
print("\n3. GIBBERISH LENGTHS AS CODE")
lengths = [11, 38, 9, 9]
print(f"Lengths: {lengths}")
print(f"As coordinates: 11°38'9.9\" or 38°11'9.9\" ?")
print(f"Berlin World Clock: 52°31'12\"N, 13°24'44\"E")
print(f"CIA HQ: 38°57'7\"N, 77°8'44\"W")

# Theory 4: Connection to dates
print("\n4. DATE-BASED INTERPRETATION")
print("Berlin Wall fall: November 9, 1989")
print("  11/9/89 or 9/11/89")
print("  Gap1 = 11 chars (November?)")
print("  Position 89 is in Gap4 (year 89?)")
print("")
print("1986 Egypt trip:")
print("  Could be encoded in gap positions or lengths")

# Theory 5: What makes grammatical sense?
print("\n5. GRAMMATICAL SENTENCE RECONSTRUCTION")
print("\nTrying to fill gaps with grammatically sensible words:")

# Gap1 (11 chars) between UNDER and NORTHEAST
gap1_options = [
    "THE GROUND",    # 10 chars + space handling
    "NEATH STONE",   # 11 chars
    "THE SURFACE",   # 11 chars
    "GROUND LIES",   # 11 chars
    "A STONE MARK",  # 12 chars - too long
]
print("\nGap1 (11 chars) - between UNDER and NORTHEAST:")
for opt in gap1_options:
    cleaned = opt.replace(" ", "")
    print(f"  '{opt}' = {len(cleaned)} chars")

# Gap2 (38 chars) between NORTHEAST and BERLINCLOCK
print("\nGap2 (38 chars) - between NORTHEAST and BERLINCLOCK:")
print("  This is the longest gap - likely a full phrase")
print("  Possible: 'OF THE SHADOW CAST BY THE HANDS OF THE' = 35 chars")
print("  Possible: 'CORNER OF THE SQUARE BY THE HANDS OF THE' = 38 chars")
print("  Possible: 'SIDE OF THE PLAZA FROM THE TOP OF THE' = 36 chars")

# Gap3 (9 chars) between BERLINCLOCK and ABOVE
gap3_options = [
    "LOOK UP",       # 6 chars
    "LIES HIGH",     # 8 chars
    "INDICATES",     # 9 chars
    "POINTS TO",     # 8 chars
    "TELLS YOU",     # 8 chars
    "SHOWS THE",     # 8 chars
]
print("\nGap3 (9 chars) - between BERLINCLOCK and ABOVE:")
for opt in gap3_options:
    cleaned = opt.replace(" ", "")
    print(f"  '{opt}' = {len(cleaned)} chars")

# Gap4 (9 chars) after ABOVE
gap4_options = [
    "THE TOWER",     # 8 chars
    "GROUND IN",     # 8 chars
    "THE EARTH",     # 8 chars
    "THE CLOCK",     # 8 chars
    "BELOW TOO",     # 8 chars
]
print("\nGap4 (9 chars) - after ABOVE:")
for opt in gap4_options:
    cleaned = opt.replace(" ", "")
    print(f"  '{opt}' = {len(cleaned)} chars")

# Theory 6: If K5 has BERLINCLOCK at same position
print("\n6. K5 IMPLICATIONS")
print("K5 will have:")
print("  - Same cryptographic system")
print("  - BERLINCLOCK at position 63")
print("  - 97 characters")
print("  - 'More global reach'")
print("")
print("This means:")
print("  - Key positions 5-15 must produce BERLINCLOCK at pos 63")
print("  - Period 29 structure is likely correct for both K4 and K5")
print("  - The method for deriving the key is what matters")

# Theory 7: Visual/Physical interpretation
print("\n7. VISUAL/PHYSICAL INTERPRETATION")
print("The Berlin World Clock (Weltzeituhr) is a physical structure:")
print("  - 24-sided cylinder")
print("  - Rotating hour ring")
print("  - Shows 148 cities")
print("")
print("'UNDER' and 'ABOVE' might refer to:")
print("  - Physical positions on the clock")
print("  - The rotating mechanism (under) and the planetary system (above)")
print("  - Underground vs surface level at Alexanderplatz")

# Theory 8: The message is intentionally incomplete
print("\n8. INTENTIONAL INCOMPLETENESS")
print("Sanborn said 'even when K4 is solved, its riddle will persist as K5'")
print("The gibberish may be intentional - NOT meant to be decoded")
print("")
print("The message might simply be:")
print("  UNDER [null] NORTHEAST [null] BERLINCLOCK [null] ABOVE [null]")
print("")
print("Meaning: 'Go to the Berlin Clock, look northeast, then check")
print("         under and above for the next clue (K5)'")

# Theory 9: Egypt connection
print("\n9. EGYPT CONNECTION")
print("K3 = Howard Carter discovering King Tut's tomb (1922)")
print("Sanborn's 1986 Egypt trip is significant")
print("")
print("Carter's words (from K3): 'CAN YOU SEE ANYTHING'")
print("Answer: 'YES, WONDERFUL THINGS'")
print("")
print("K4 might continue this theme:")
print("  'UNDER... NORTHEAST... BERLINCLOCK... ABOVE' = directions to find something")

print("\n" + "=" * 70)
print("MOST LIKELY INTERPRETATION")
print("=" * 70)
print("""
K4 is NOT a puzzle to be fully decoded letter-by-letter.

The METHOD is the puzzle:
1. Use Period 29 Vigenère with KRYPTOS alphabet
2. The key is derived from the Berlin World Clock somehow
3. The readable words (UNDER, NORTHEAST, BERLINCLOCK, ABOVE) are the message
4. The gibberish is padding/null characters

The MESSAGE is directions:
  "UNDER [something] NORTHEAST [of the] BERLINCLOCK [look] ABOVE"

This points to K5, which will be "more global" and "publicly accessible"
- possibly a physical installation or global hunt.

The MYSTERY that persists:
1. How exactly is the Period 29 key derived from the Berlin World Clock?
2. What is the full plaintext if not UNDER/NORTHEAST/BERLINCLOCK/ABOVE?
3. Where/what is K5?
""")
