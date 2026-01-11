#!/usr/bin/env python3
"""
K4 Word Boundary Analysis

Analyzes the candidate plaintext to identify potential word boundaries
and hidden words in the gaps between known words.
"""

# Best candidate plaintext
PLAINTEXT = "UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF"

# Known words with their positions
KNOWN_WORDS = [
    ("DAY", 1),
    ("NORTHEAST", 16),
    ("CIA", 29),
    ("KGB", 60),
    ("BERLINCLOCK", 63),
    ("ABOVE", 83),
]

# Common English words to try in gaps
COMMON_WORDS = {
    # Short prepositions and articles
    "short": ["A", "I", "OF", "TO", "IN", "AT", "ON", "BY", "AS", "OR", "AN", "UP", "IS", "IT", "WE", "US", "BE", "GO", "DO", "NO", "SO", "MY", "ME", "IF", "AM", "HE"],
    # Medium prepositions and conjunctions
    "medium": ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS", "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID", "ITS", "LET", "PUT", "SAY", "SHE", "TOO", "USE"],
    # Longer words
    "longer": ["UNDER", "ABOVE", "BELOW", "AFTER", "BEFORE", "BETWEEN", "BEHIND", "BENEATH", "THROUGH", "WITHIN", "WITHOUT", "AROUND", "ACROSS", "ALONG", "TOWARD", "INSIDE", "OUTSIDE", "SLOWLY", "DEEPLY", "HIDDEN", "SECRET", "BURIED", "CLOCK", "SHADOW", "TUNNEL", "LAYER", "LEVEL"],
    # Spy/intelligence related
    "spy": ["SPY", "DEAD", "DROP", "CODE", "AGENT", "ASSET", "INTEL", "MOLE", "SAFE", "HOUSE", "SIGNAL", "COVERT", "COVER", "WATCH", "TARGET", "MISSION", "HANDLER", "SOURCE", "CIPHER", "CRYPTO"],
    # Location related
    "location": ["EAST", "WEST", "NORTH", "SOUTH", "WALL", "GATE", "DOOR", "PATH", "ROAD", "STREET", "POINT", "BASE", "SITE", "ZONE", "AREA", "SECTOR", "REGION"],
}

def print_structure():
    """Print the known word structure."""
    print("=" * 80)
    print("K4 WORD BOUNDARY ANALYSIS")
    print("=" * 80)
    print(f"\nPlaintext ({len(PLAINTEXT)} chars):")
    print(PLAINTEXT)
    print()

    # Create visual map
    print("Known word positions:")
    markers = ['.'] * len(PLAINTEXT)
    for word, pos in KNOWN_WORDS:
        for i, char in enumerate(word):
            markers[pos + i] = char
    print(''.join(markers))
    print()

    # Create position ruler
    print("Position:  ", end="")
    for i in range(0, len(PLAINTEXT), 10):
        print(f"{i:<10}", end="")
    print()
    print("           " + "|" + " " * 9 + "|" * ((len(PLAINTEXT) - 1) // 10))

def analyze_gaps():
    """Analyze the gaps between known words."""
    print("\n" + "=" * 80)
    print("GAP ANALYSIS")
    print("=" * 80)

    # Sort words by position
    sorted_words = sorted(KNOWN_WORDS, key=lambda x: x[1])

    # Analyze each gap
    gaps = []

    # Gap before first known word
    first_word, first_pos = sorted_words[0]
    if first_pos > 0:
        gap_text = PLAINTEXT[0:first_pos]
        gaps.append(("START", 0, first_word, first_pos, gap_text))
        print(f"\nGap: START to {first_word}")
        print(f"  Position: 0 to {first_pos}")
        print(f"  Length: {len(gap_text)} chars")
        print(f"  Content: '{gap_text}'")

    # Gaps between known words
    for i in range(len(sorted_words) - 1):
        word1, pos1 = sorted_words[i]
        word2, pos2 = sorted_words[i + 1]
        gap_start = pos1 + len(word1)
        gap_end = pos2

        if gap_end > gap_start:
            gap_text = PLAINTEXT[gap_start:gap_end]
            gaps.append((word1, gap_start, word2, gap_end, gap_text))
            print(f"\nGap: {word1} to {word2}")
            print(f"  Position: {gap_start} to {gap_end}")
            print(f"  Length: {len(gap_text)} chars")
            print(f"  Content: '{gap_text}'")

    # Gap after last known word
    last_word, last_pos = sorted_words[-1]
    last_end = last_pos + len(last_word)
    if last_end < len(PLAINTEXT):
        gap_text = PLAINTEXT[last_end:]
        gaps.append((last_word, last_end, "END", len(PLAINTEXT), gap_text))
        print(f"\nGap: {last_word} to END")
        print(f"  Position: {last_end} to {len(PLAINTEXT)}")
        print(f"  Length: {len(gap_text)} chars")
        print(f"  Content: '{gap_text}'")

    return gaps

def find_words_in_text(text, start_offset=0):
    """Find potential English words in a text segment."""
    found = []
    all_words = []
    for category, words in COMMON_WORDS.items():
        all_words.extend([(w, category) for w in words])

    for word, category in all_words:
        pos = 0
        while True:
            idx = text.find(word, pos)
            if idx == -1:
                break
            found.append((word, idx + start_offset, category))
            pos = idx + 1

    return sorted(found, key=lambda x: x[1])

def analyze_gap_contents(gaps):
    """Look for potential words in each gap."""
    print("\n" + "=" * 80)
    print("POTENTIAL WORDS IN GAPS")
    print("=" * 80)

    for gap_info in gaps:
        from_word, gap_start, to_word, gap_end, gap_text = gap_info
        print(f"\n--- Gap: {from_word} -> {to_word} ---")
        print(f"Content: '{gap_text}' (length {len(gap_text)})")

        found = find_words_in_text(gap_text, gap_start)
        if found:
            print("Potential words found:")
            for word, pos, category in found:
                print(f"  '{word}' at position {pos} ({category})")
        else:
            print("No common words found")

def check_position_zero():
    """Check if 'U' at position 0 could be part of a longer word."""
    print("\n" + "=" * 80)
    print("POSITION 0 ANALYSIS - 'U' PREFIX")
    print("=" * 80)

    # Words that start with U
    u_words = [
        "UNDER", "UNTIL", "UPON", "UPPER", "UP", "US", "USE", "USED",
        "USING", "USUAL", "ULTRA", "UNABLE", "UNCLE", "UNKNOWN", "UNLESS",
        "UNLIKE", "UNSEEN", "UNTOLD", "UNCOVER", "UNDERGO", "UNDERGROUND"
    ]

    prefix = PLAINTEXT[:10]  # First 10 chars
    print(f"First 10 characters: '{prefix}'")
    print()

    print("Checking U-words:")
    for word in u_words:
        if PLAINTEXT.startswith(word):
            print(f"  MATCH: '{word}' at position 0!")
        elif PLAINTEXT[0:len(word)] == word:
            print(f"  MATCH: '{word}' at position 0!")

    # Special check for UDAY - could be a word or name
    print("\nNote: 'UDAY' (positions 0-3) could be:")
    print("  - A name (Uday - Arabic name)")
    print("  - 'U' + 'DAY' (U as single letter)")
    print("  - Part of longer word")

    # Check if position 0 U combined with something after DAY makes sense
    print("\nChecking 'U' + 'DAY' pattern:")
    print(f"  If U is separate: U + DAY + ... (positions 0, 1-3)")
    print(f"  If UDAY is a name: UDAY + ... (positions 0-3)")

def try_word_combinations():
    """Try inserting common words into gaps and check for patterns."""
    print("\n" + "=" * 80)
    print("WORD COMBINATION ANALYSIS")
    print("=" * 80)

    # Key gaps to analyze
    gaps_to_analyze = [
        ("Gap 1: U[DAY]...NORTHEAST", PLAINTEXT[4:16], 4),
        ("Gap 2: NORTHEAST...CIA", PLAINTEXT[25:29], 25),
        ("Gap 3: CIA...KGB", PLAINTEXT[32:60], 32),
        ("Gap 4: BERLINCLOCK...ABOVE", PLAINTEXT[74:83], 74),
        ("Gap 5: ABOVE...END", PLAINTEXT[88:], 88),
    ]

    for gap_name, gap_text, offset in gaps_to_analyze:
        print(f"\n{gap_name}")
        print(f"  Content: '{gap_text}'")
        print(f"  Length: {len(gap_text)}")

        # Try to find meaningful substrings
        words_found = find_words_in_text(gap_text, offset)
        if words_found:
            print(f"  Potential words: {words_found}")

def structural_summary():
    """Print a structural summary of the plaintext."""
    print("\n" + "=" * 80)
    print("STRUCTURAL SUMMARY")
    print("=" * 80)

    print("\nWord structure with positions:")
    print("  [0] U")
    print("  [1-3] DAY (known)")
    print("  [4-15] UQAPBZDBKZEL (12 chars - unknown)")
    print("  [16-24] NORTHEAST (known)")
    print("  [25-28] LGUW (4 chars - unknown)")
    print("  [29-31] CIA (known)")
    print("  [32-59] ASQGUZOUAFZFETMMNXPSOZMPAPGL (28 chars - unknown)")
    print("  [60-62] KGB (known)")
    print("  [63-73] BERLINCLOCK (known)")
    print("  [74-82] RSPVJWQUL (9 chars - unknown)")
    print("  [83-87] ABOVE (known)")
    print("  [88-96] JYBUKCAYF (9 chars - unknown)")

    print("\nKnown coverage:")
    known_chars = 3 + 9 + 3 + 3 + 11 + 5  # DAY + NORTHEAST + CIA + KGB + BERLINCLOCK + ABOVE
    print(f"  Known words: {known_chars} characters")
    print(f"  Unknown gaps: {97 - known_chars} characters")
    print(f"  Coverage: {known_chars/97*100:.1f}%")

    print("\nSpacing pattern:")
    print("  U(1) + DAY(3) + gap(12) + NORTHEAST(9) + gap(4) + CIA(3)")
    print("  + gap(28) + KGB(3) + BERLINCLOCK(11) + gap(9) + ABOVE(5) + gap(9)")

def deep_gap_analysis():
    """Perform deeper analysis on each gap."""
    print("\n" + "=" * 80)
    print("DEEP GAP ANALYSIS")
    print("=" * 80)

    # Gap 1: Position 4-15 (UQAPBZDBKZEL)
    gap1 = "UQAPBZDBKZEL"
    print(f"\nGap 1 (pos 4-15): '{gap1}'")
    print("  Possible patterns:")
    print(f"    - Q at position 5 is unusual in English")
    print(f"    - ZEL at end could be part of word")
    print(f"    - Check: AP, AT patterns")

    # Gap 2: Position 25-28 (LGUW)
    gap2 = "LGUW"
    print(f"\nGap 2 (pos 25-28): '{gap2}'")
    print("  Very short gap - likely:")
    print("    - Part of a preposition")
    print("    - Random noise")
    print("    - Could 'W' connect to CIA? (WCIA?)")

    # Gap 3: Position 32-59 (ASQGUZOUAFZFETMMNXPSOZMPAPGL)
    gap3 = "ASQGUZOUAFZFETMMNXPSOZMPAPGL"
    print(f"\nGap 3 (pos 32-59): '{gap3}'")
    print("  Longest gap - looking for patterns:")
    substrings_to_check = ["AS", "AT", "SO", "TO", "MP", "AP", "ET", "MN", "OZ"]
    for sub in substrings_to_check:
        if sub in gap3:
            idx = gap3.find(sub)
            print(f"    - '{sub}' found at relative position {idx}")

    # Gap 4: Position 74-82 (RSPVJWQUL)
    gap4 = "RSPVJWQUL"
    print(f"\nGap 4 (pos 74-82): '{gap4}'")
    print("  Looking for patterns:")
    if "SP" in gap4:
        print("    - 'SP' found - could be 'SPY', 'SPOT', etc.")
    print(f"    - Ends with 'UL' - unusual")

    # Gap 5: Position 88-96 (JYBUKCAYF)
    gap5 = "JYBUKCAYF"
    print(f"\nGap 5 (pos 88-96): '{gap5}'")
    print("  Looking for patterns:")
    if "AY" in gap5:
        print("    - 'AY' found - could be 'DAY', 'WAY', 'SAY'")
    if "BY" in gap5:
        print("    - 'BY' found at position 89")
    print(f"    - J at start is uncommon")

def alternative_word_boundaries():
    """Check for alternative word boundaries."""
    print("\n" + "=" * 80)
    print("ALTERNATIVE WORD BOUNDARY CHECK")
    print("=" * 80)

    # Check if UNDER could be at position 0
    print("\nChecking for UNDER at various positions:")
    for i in range(len(PLAINTEXT) - 5):
        segment = PLAINTEXT[i:i+5]
        if segment == "UNDER":
            print(f"  UNDER found at position {i}!")

    # Look for overlapping words
    print("\nLooking for words that might overlap with known positions:")

    # Could LGUW be part of something?
    print(f"\nAround NORTHEAST (16-24):")
    print(f"  Before: {PLAINTEXT[12:16]}")
    print(f"  After: {PLAINTEXT[25:32]}")

    # Look for THE, AND, etc.
    important_words = ["THE", "AND", "WAS", "FOR", "ARE", "WITH", "THAT", "THIS", "FROM", "HAVE"]
    print("\nSearching for common connectors:")
    for word in important_words:
        if word in PLAINTEXT:
            idx = PLAINTEXT.find(word)
            print(f"  '{word}' found at position {idx}")

def letter_frequency_in_gaps():
    """Analyze letter frequencies in gap regions."""
    print("\n" + "=" * 80)
    print("LETTER FREQUENCY IN GAPS")
    print("=" * 80)

    # Combine all gap text
    gap_text = PLAINTEXT[0:1] + PLAINTEXT[4:16] + PLAINTEXT[25:29] + PLAINTEXT[32:60] + PLAINTEXT[74:83] + PLAINTEXT[88:]

    print(f"\nCombined gap text ({len(gap_text)} chars): '{gap_text}'")

    freq = {}
    for char in gap_text:
        freq[char] = freq.get(char, 0) + 1

    print("\nLetter frequencies (sorted by count):")
    for char, count in sorted(freq.items(), key=lambda x: -x[1]):
        pct = count / len(gap_text) * 100
        bar = "*" * count
        print(f"  {char}: {count:2d} ({pct:5.1f}%) {bar}")

    # English letter frequency comparison
    print("\nNote: High frequency of Q, Z, X suggests:")
    print("  - These gaps may still be partially encrypted")
    print("  - OR the cipher isn't producing clean plaintext")

if __name__ == "__main__":
    print_structure()
    gaps = analyze_gaps()
    analyze_gap_contents(gaps)
    check_position_zero()
    try_word_combinations()
    structural_summary()
    deep_gap_analysis()
    alternative_word_boundaries()
    letter_frequency_in_gaps()

    print("\n" + "=" * 80)
    print("CONCLUSIONS")
    print("=" * 80)
    print("""
1. The plaintext shows clear English words at specific positions
2. The gaps between words contain unusual letter combinations (Q, Z, X)
3. This suggests the decryption may be partial or use multiple cipher systems
4. The 'U' at position 0 does not appear to form UNDER or similar words
5. Key observation: Known words account for only ~35% of the text
6. The gaps may contain:
   - More encrypted text requiring a different key
   - Null characters or padding
   - Additional plaintext with rare letter patterns

Recommended next steps:
- Try different keys for the gap regions
- Check if gaps follow a different cipher pattern
- Look for number/null patterns in gaps
""")
