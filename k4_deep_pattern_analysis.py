#!/usr/bin/env python3
"""
Deep pattern analysis of K4 gibberish sections
Looking for anagrams, hidden words, and coordinate patterns
"""

from itertools import permutations
import os

# The gibberish sections
SECTIONS = [
    ("Section 1", "QAPBZDBKZEL"),        # Between UNDER and NORTHEAST
    ("Section 2", "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ"),  # Between NORTHEAST and BERLINCLOCK
    ("Section 3", "MPAPGKPVH"),          # Possibly between segments
    ("Section 4", "RSPVJWQUL"),          # Between BERLINCLOCK and ABOVE
    ("Section 5", "ZOLRKCAYF")           # After ABOVE (end)
]

# Load a word list if available
def load_wordlist():
    """Try to load system word list"""
    wordlist = set()

    # Common word list locations
    paths = ['/usr/share/dict/words', '/usr/share/dict/american-english',
             '/usr/share/dict/british-english']

    for path in paths:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    word = line.strip().upper()
                    if word.isalpha():
                        wordlist.add(word)
            break

    # Add some critical words we're looking for
    wordlist.update([
        "COORDINATES", "LOCATION", "LATITUDE", "LONGITUDE", "DEGREES",
        "MINUTES", "SECONDS", "POSITION", "BEARING", "HEADING", "AZIMUTH",
        "BURIED", "HIDDEN", "SECRET", "TREASURE", "CACHE", "VAULT",
        "LANGLEY", "VIRGINIA", "BERLIN", "CLOCK", "NORTHEAST", "UNDER", "ABOVE",
        "KRYPTOS", "CIPHER", "DECODE", "DECRYPT", "MESSAGE", "LAYER",
        "PALIMPSEST", "ABSCISSA", "SHADOW", "LIGHT", "IQLUSION",
        "MAP", "KEY", "CODE", "SPY", "CIA", "NSA", "FBI", "KGB",
        "CHECKPOINT", "CHARLIE", "WALL", "EAST", "WEST", "GATE",
        "ALEXANDERPLATZ", "POTSDAMER", "FRIEDRICHSTRASSE", "TIERGARTEN"
    ])

    return wordlist

def find_anagrams_brute(text, wordlist, max_len=8):
    """Find anagrams by checking permutations (for short strings)"""
    text = text.upper()
    if len(text) > max_len:
        print(f"  Text too long for brute force ({len(text)} chars)")
        return []

    found = []
    seen = set()

    for p in permutations(text):
        word = ''.join(p)
        if word not in seen and word in wordlist:
            found.append(word)
            seen.add(word)

    return found


def find_partial_anagrams(text, wordlist, min_len=4):
    """Find words that can be formed from the letters in text"""
    text = text.upper()
    from collections import Counter
    text_counter = Counter(text)

    found = []
    for word in wordlist:
        if min_len <= len(word) <= len(text):
            word_counter = Counter(word)
            # Check if word can be formed from text letters
            if all(word_counter[c] <= text_counter[c] for c in word_counter):
                found.append(word)

    return sorted(found, key=len, reverse=True)[:20]  # Top 20 longest


def check_coordinate_encoding(text):
    """Check if text encodes coordinates in various formats"""
    results = []
    text = text.upper()

    # A=1, B=2, etc.
    nums = [ord(c) - ord('A') + 1 for c in text]

    # K2 coordinates: 38 57 6.5 N, 77 8 44 W
    # Check if numbers could form something similar

    # Try parsing as degree-minute-second format
    if len(nums) >= 6:
        # Try groups of 3 for lat/lon
        for i in range(0, len(nums)-5, 3):
            deg = nums[i]
            min_val = nums[i+1]
            sec = nums[i+2]
            if 0 <= deg <= 90 and 0 <= min_val < 60 and 0 <= sec < 60:
                results.append(f"  Possible coordinate at {i}: {deg}deg {min_val}min {sec}sec")

    # Check for K2-like latitude (38.57)
    for i in range(len(nums)-1):
        if nums[i] == 3 and nums[i+1] == 8:  # 38
            results.append(f"  '38' pattern at position {i}")
        if nums[i] == 7 and nums[i+1] == 7:  # 77
            results.append(f"  '77' pattern at position {i}")

    # Sum of letters might encode coordinates
    total = sum(nums)
    results.append(f"  Sum of A=1 values: {total}")
    if 30 <= total <= 50:
        results.append(f"    Could be latitude: {total}")
    if 70 <= total <= 90:
        results.append(f"    Could be longitude: {total}")

    return results


def check_word_fragments(text):
    """Check for meaningful word fragments"""
    text = text.upper()

    # Words that might appear as fragments
    fragments = [
        # Geographic/directional
        "NORTH", "SOUTH", "EAST", "WEST", "NE", "NW", "SE", "SW",
        "LAT", "LON", "DEG", "MIN", "SEC", "POS",
        # Location related
        "BURY", "HIDE", "DIG", "MARK", "SPOT", "SITE", "PLACE",
        # Kryptos related
        "KEY", "CODE", "CIA", "SPY", "LANG", "VIRG",
        # Time/clock related
        "TIME", "HOUR", "CLOCK",
        # Berlin related
        "BERL", "MAUER", "WALL", "OST", "WEST", "GRENZ",
        # Numbers as words
        "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
        # Other
        "MAP", "GPS", "REF", "GRID", "ZONE", "AREA"
    ]

    found = []
    for frag in fragments:
        if frag in text:
            pos = text.find(frag)
            found.append(f"  Contains '{frag}' at position {pos}")
        if frag in text[::-1]:
            found.append(f"  Reversed contains '{frag}'")

    return found


def check_abbreviation_patterns(text):
    """Check if text looks like an abbreviation/acronym"""
    text = text.upper()
    results = []

    # Common abbreviation patterns for locations/coordinates
    if len(text) <= 5:
        results.append(f"  Short enough to be an abbreviation")

        # Check if it could be a military/intelligence abbreviation
        if text.startswith(('Z', 'Q', 'X')):
            results.append(f"  Starts with uncommon letter (possible code designator)")

    # Check for embedded numbers (via letter-number correspondence)
    # Q=17, A=1, P=16, B=2, Z=26, etc.
    nums = [ord(c) - ord('A') + 1 for c in text]

    # Check for obvious number sequences
    for i in range(len(nums)-1):
        if abs(nums[i] - nums[i+1]) == 1:
            results.append(f"  Sequential numbers at pos {i}: {nums[i]}, {nums[i+1]}")

    return results


def letter_shift_analysis(text):
    """Analyze shifts between consecutive letters"""
    text = text.upper()
    shifts = []

    for i in range(len(text)-1):
        shift = (ord(text[i+1]) - ord(text[i])) % 26
        shifts.append(shift)

    return shifts


def check_repeating_patterns(text):
    """Check for repeating patterns within the text"""
    text = text.upper()
    results = []

    # Check for repeated substrings
    for length in range(2, len(text)//2 + 1):
        for i in range(len(text) - length):
            substr = text[i:i+length]
            if text.count(substr) > 1:
                results.append(f"  Repeated pattern '{substr}' appears {text.count(substr)} times")

    return results


def roman_numeral_check(text):
    """Check if text contains roman numerals"""
    text = text.upper()

    roman_chars = set('IVXLCDM')
    roman_count = sum(1 for c in text if c in roman_chars)

    results = []
    if roman_count > len(text) * 0.3:
        results.append(f"  High proportion of Roman numeral chars: {roman_count}/{len(text)}")

    # Look for complete roman numerals
    romans = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
              'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX',
              'XXI', 'XXX', 'XL', 'L', 'LX', 'LXX', 'LXXX', 'XC', 'C', 'CC', 'CCC',
              'CD', 'D', 'CM', 'M']

    for r in romans:
        if len(r) >= 2 and r in text:
            results.append(f"  Contains Roman numeral '{r}'")

    return results


def analyze_as_cipher_output(text):
    """Analyze if text looks like cipher output patterns"""
    text = text.upper()
    from collections import Counter

    freq = Counter(text)
    results = []

    # English letter frequency order (most common)
    english_order = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

    # Calculate how 'English-like' the frequency distribution is
    sorted_letters = [x[0] for x in freq.most_common()]

    # IoC calculation
    n = len(text)
    ioc = sum(f * (f-1) for f in freq.values()) / (n * (n-1)) if n > 1 else 0
    results.append(f"  Index of Coincidence: {ioc:.4f} (English ~0.067, random ~0.038)")

    if ioc < 0.045:
        results.append(f"    -> Very flat distribution, suggests strong encryption")
    elif ioc < 0.055:
        results.append(f"    -> Somewhat flat, may be substitution cipher")
    else:
        results.append(f"    -> Near English, may contain plaintext fragments")

    return results


def main():
    print("=" * 80)
    print("DEEP PATTERN ANALYSIS OF K4 GIBBERISH SECTIONS")
    print("=" * 80)

    wordlist = load_wordlist()
    print(f"\nLoaded wordlist with {len(wordlist)} words")

    for name, text in SECTIONS:
        print(f"\n{'='*80}")
        print(f"{name}: {text}")
        print(f"Length: {len(text)}")
        print("=" * 80)

        # Partial anagrams (words that can be made from letters)
        print("\n--- WORDS FORMABLE FROM THESE LETTERS ---")
        partials = find_partial_anagrams(text, wordlist)
        if partials:
            print(f"  {', '.join(partials[:15])}")
        else:
            print("  None found")

        # Full anagrams for short texts
        if len(text) <= 9:
            print("\n--- FULL ANAGRAM CHECK (brute force) ---")
            anagrams = find_anagrams_brute(text, wordlist)
            if anagrams:
                print(f"  FOUND: {', '.join(anagrams)}")
            else:
                print("  No exact anagrams found")

        # Coordinate patterns
        print("\n--- COORDINATE ENCODING ANALYSIS ---")
        coords = check_coordinate_encoding(text)
        for c in coords:
            print(c)

        # Word fragments
        print("\n--- WORD FRAGMENT CHECK ---")
        frags = check_word_fragments(text)
        if frags:
            for f in frags:
                print(f)
        else:
            print("  No known fragments found")

        # Abbreviation patterns
        print("\n--- ABBREVIATION ANALYSIS ---")
        abbrevs = check_abbreviation_patterns(text)
        if abbrevs:
            for a in abbrevs:
                print(a)
        else:
            print("  No clear abbreviation patterns")

        # Letter shifts
        print("\n--- LETTER SHIFT PATTERN ---")
        shifts = letter_shift_analysis(text)
        print(f"  Shifts: {shifts}")
        print(f"  Sum of shifts: {sum(shifts)}")

        # Repeating patterns
        print("\n--- REPEATING PATTERNS ---")
        repeats = check_repeating_patterns(text)
        if repeats:
            for r in repeats[:5]:  # Top 5
                print(r)
        else:
            print("  No significant repeating patterns")

        # Roman numerals
        print("\n--- ROMAN NUMERAL CHECK ---")
        romans = roman_numeral_check(text)
        if romans:
            for r in romans:
                print(r)
        else:
            print("  No significant Roman numeral content")

        # Cipher analysis
        print("\n--- CIPHER OUTPUT ANALYSIS ---")
        cipher_analysis = analyze_as_cipher_output(text)
        for c in cipher_analysis:
            print(c)

    # Cross-section analysis
    print("\n" + "=" * 80)
    print("CROSS-SECTION ANALYSIS")
    print("=" * 80)

    # First letters
    firsts = ''.join(t[0] for _, t in SECTIONS)
    print(f"\nFirst letters: {firsts}")
    print(f"  A=1 values: {[ord(c) - ord('A') + 1 for c in firsts]}")

    # Last letters
    lasts = ''.join(t[-1] for _, t in SECTIONS)
    print(f"\nLast letters: {lasts}")
    print(f"  A=1 values: {[ord(c) - ord('A') + 1 for c in lasts]}")

    # Length patterns
    lengths = [len(t) for _, t in SECTIONS]
    print(f"\nSection lengths: {lengths}")
    print(f"  Sum: {sum(lengths)}")
    print(f"  As letters: {''.join(chr(ord('A') + n - 1) if 1 <= n <= 26 else '?' for n in lengths)}")

    # All text combined
    all_text = ''.join(t for _, t in SECTIONS)
    print(f"\nCombined text: {all_text}")
    print(f"Total length: {len(all_text)}")

    # Look for words in combined text
    print("\n--- WORDS IN COMBINED TEXT ---")
    for word in sorted(wordlist, key=len, reverse=True):
        if len(word) >= 4 and word in all_text:
            pos = all_text.find(word)
            print(f"  Found '{word}' at position {pos}")


if __name__ == "__main__":
    main()
