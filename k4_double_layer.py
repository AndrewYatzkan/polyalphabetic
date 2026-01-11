#!/usr/bin/env python3
"""
K4 Double Layer Encryption Analysis

Hypothesis: The partial decryption with Period 29 key shows readable words
mixed with gibberish. The gibberish might be encrypted with an additional layer.

Current decryption:
UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF

Readable sections: DAY, NORTHEAST, CIA, KGB, BERLINCLOCK, ABOVE
Gibberish sections: U, UQAPBZDBKZEL, LGU, ASQGUZOUAFZFETMMNXPSOZMPAPGL, RSPVJWQUL, JYBUKCAYF
"""

import string
from itertools import product

# The K4 ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# The current best decryption with Period 29
DECRYPTED = "UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF"

# Known readable words and their positions
READABLE_WORDS = {
    "DAY": (1, 4),        # positions 1-3 (0-indexed)
    "NORTHEAST": (17, 26),
    "CIA": (30, 33),
    "KGB": (63, 66),
    "BERLINCLOCK": (66, 77),
    "ABOVE": (82, 87),
}

# KRYPTOS tableau (used in K1-K3)
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # Missing letters filled
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def identify_gibberish_sections(decrypted, words_info):
    """Identify which parts are gibberish vs readable."""
    # Mark positions that are part of readable words
    readable_mask = [False] * len(decrypted)

    for word, (start, end) in words_info.items():
        for i in range(start, end):
            if i < len(readable_mask):
                readable_mask[i] = True

    # Extract gibberish sections
    gibberish_sections = []
    current_section = ""
    current_start = None

    for i, (char, is_readable) in enumerate(zip(decrypted, readable_mask)):
        if not is_readable:
            if current_start is None:
                current_start = i
            current_section += char
        else:
            if current_section:
                gibberish_sections.append((current_start, current_section))
                current_section = ""
                current_start = None

    if current_section:
        gibberish_sections.append((current_start, current_section))

    return gibberish_sections, readable_mask

def caesar_decrypt(text, shift):
    """Decrypt using Caesar cipher with given shift."""
    result = ""
    for c in text:
        if c in string.ascii_uppercase:
            result += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
        else:
            result += c
    return result

def atbash_decrypt(text):
    """Decrypt using Atbash cipher (A<->Z, B<->Y, etc.)."""
    result = ""
    for c in text:
        if c in string.ascii_uppercase:
            result += chr(ord('Z') - (ord(c) - ord('A')))
        else:
            result += c
    return result

def rot13_decrypt(text):
    """Decrypt using ROT13."""
    return caesar_decrypt(text, 13)

def kryptos_substitution(text, reverse=False):
    """Apply KRYPTOS alphabet substitution."""
    if reverse:
        mapping = dict(zip(KRYPTOS_ALPHABET, STANDARD_ALPHABET))
    else:
        mapping = dict(zip(STANDARD_ALPHABET, KRYPTOS_ALPHABET))
    return "".join(mapping.get(c, c) for c in text)

def vigenere_decrypt(text, key):
    """Decrypt using Vigenere cipher."""
    result = ""
    key_len = len(key)
    for i, c in enumerate(text):
        if c in string.ascii_uppercase:
            shift = ord(key[i % key_len]) - ord('A')
            result += chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
        else:
            result += c
    return result

def is_promising_text(text, min_word_len=3):
    """Check if text contains English-like patterns."""
    # Common English words to look for
    common_words = [
        "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD",
        "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS",
        "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID",
        "ITS", "LET", "PUT", "SAY", "SHE", "TOO", "USE", "LAYER", "CLOCK",
        "EAST", "WEST", "NORTH", "SOUTH", "SECRET", "CODE", "KEY", "CIPHER",
        "HIDDEN", "BELOW", "ABOVE", "UNDER", "OVER", "BERLIN", "CIA", "KGB",
        "SPY", "AGENT", "TIME", "PLACE", "SLOWLY", "DESPER", "ATELY", "SHADOW"
    ]

    text_upper = text.upper()
    found_words = []
    for word in common_words:
        if word in text_upper:
            found_words.append(word)

    return found_words

def analyze_gibberish_with_caesar(gibberish):
    """Try all Caesar shifts on gibberish."""
    print("\n=== CAESAR CIPHER ANALYSIS ===")
    for shift in range(1, 26):
        decrypted = caesar_decrypt(gibberish, shift)
        words = is_promising_text(decrypted)
        if words:
            print(f"Shift {shift:2d}: {decrypted} -> Found: {words}")

    # Also show all shifts for manual inspection
    print("\nAll Caesar shifts:")
    for shift in range(1, 26):
        decrypted = caesar_decrypt(gibberish, shift)
        print(f"  {shift:2d}: {decrypted}")

def analyze_gibberish_with_atbash(gibberish):
    """Try Atbash on gibberish."""
    print("\n=== ATBASH CIPHER ANALYSIS ===")
    decrypted = atbash_decrypt(gibberish)
    words = is_promising_text(decrypted)
    print(f"Atbash: {decrypted}")
    if words:
        print(f"  Found words: {words}")

def analyze_gibberish_with_vigenere(gibberish, max_key_len=3):
    """Try short Vigenere keys on gibberish."""
    print(f"\n=== VIGENERE CIPHER ANALYSIS (keys up to length {max_key_len}) ===")

    promising_results = []

    for key_len in range(1, max_key_len + 1):
        for key_tuple in product(string.ascii_uppercase, repeat=key_len):
            key = "".join(key_tuple)
            decrypted = vigenere_decrypt(gibberish, key)
            words = is_promising_text(decrypted)
            if words:
                promising_results.append((key, decrypted, words))

    if promising_results:
        print("Promising results:")
        for key, decrypted, words in promising_results[:20]:  # Limit output
            print(f"  Key '{key}': {decrypted} -> Found: {words}")
    else:
        print("No promising results found with short keys.")

def analyze_with_readable_words_as_keys(gibberish):
    """Use the readable words from the decryption as Vigenere keys."""
    print("\n=== USING READABLE WORDS AS KEYS ===")

    readable_keys = ["DAY", "NORTHEAST", "CIA", "KGB", "BERLINCLOCK", "ABOVE",
                     "CLOCK", "BERLIN", "EAST", "NORTH"]

    for key in readable_keys:
        decrypted = vigenere_decrypt(gibberish, key)
        words = is_promising_text(decrypted)
        print(f"Key '{key}': {decrypted}")
        if words:
            print(f"  Found words: {words}")

def analyze_kryptos_substitution(gibberish):
    """Try KRYPTOS alphabet substitution."""
    print("\n=== KRYPTOS ALPHABET SUBSTITUTION ===")

    forward = kryptos_substitution(gibberish, reverse=False)
    reverse = kryptos_substitution(gibberish, reverse=True)

    print(f"Standard -> KRYPTOS: {forward}")
    words = is_promising_text(forward)
    if words:
        print(f"  Found words: {words}")

    print(f"KRYPTOS -> Standard: {reverse}")
    words = is_promising_text(reverse)
    if words:
        print(f"  Found words: {words}")

def try_double_layer_full_text():
    """Try decrypting the full gibberish-combined text."""
    print("\n" + "="*60)
    print("FULL TEXT DOUBLE LAYER ANALYSIS")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Combine all gibberish
    full_gibberish = "".join(section for _, section in gibberish_sections)
    print(f"\nCombined gibberish ({len(full_gibberish)} chars): {full_gibberish}")

    analyze_gibberish_with_caesar(full_gibberish)
    analyze_gibberish_with_atbash(full_gibberish)
    analyze_with_readable_words_as_keys(full_gibberish)
    analyze_kryptos_substitution(full_gibberish)

def try_per_section_analysis():
    """Analyze each gibberish section separately."""
    print("\n" + "="*60)
    print("PER-SECTION ANALYSIS")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    for i, (start, section) in enumerate(gibberish_sections):
        if len(section) >= 3:  # Only analyze sections with 3+ chars
            print(f"\n--- Section {i+1}: '{section}' (position {start}, length {len(section)}) ---")
            analyze_gibberish_with_caesar(section)
            analyze_gibberish_with_atbash(section)

def analyze_alternating_pattern():
    """Check if there's an alternating pattern in the decryption."""
    print("\n" + "="*60)
    print("ALTERNATING PATTERN ANALYSIS")
    print("="*60)

    # Extract every other character
    even_chars = DECRYPTED[::2]
    odd_chars = DECRYPTED[1::2]

    print(f"\nEven positions: {even_chars}")
    print(f"Odd positions: {odd_chars}")

    # Check for words in each
    print(f"\nWords in even positions: {is_promising_text(even_chars)}")
    print(f"Words in odd positions: {is_promising_text(odd_chars)}")

    # Try decrypting each with Caesar
    print("\nCaesar on even positions:")
    for shift in range(1, 26):
        dec = caesar_decrypt(even_chars, shift)
        words = is_promising_text(dec)
        if words:
            print(f"  Shift {shift}: {dec} -> {words}")

    print("\nCaesar on odd positions:")
    for shift in range(1, 26):
        dec = caesar_decrypt(odd_chars, shift)
        words = is_promising_text(dec)
        if words:
            print(f"  Shift {shift}: {dec} -> {words}")

def selective_decryption():
    """Try decrypting only specific positions based on patterns."""
    print("\n" + "="*60)
    print("SELECTIVE POSITION ANALYSIS")
    print("="*60)

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Get only gibberish positions from original K4
    gibberish_from_k4 = ""
    for i, is_readable in enumerate(readable_mask):
        if not is_readable and i < len(K4):
            gibberish_from_k4 += K4[i]

    print(f"\nOriginal K4 at gibberish positions: {gibberish_from_k4}")

    # Try different approaches on this
    print("\nTrying different single-key Vigenere on K4 gibberish positions:")
    for key in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "CLOCK", "BERLIN"]:
        decrypted = vigenere_decrypt(gibberish_from_k4, key)
        words = is_promising_text(decrypted)
        print(f"  Key '{key}': {decrypted}")
        if words:
            print(f"    Found: {words}")

def try_known_kryptos_keys():
    """Try keys from other Kryptos sections."""
    print("\n" + "="*60)
    print("TRYING KNOWN KRYPTOS KEYS ON GIBBERISH")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    known_keys = [
        "PALIMPSEST",  # K1 key
        "ABSCISSA",    # K2 key
        "KRYPTOS",     # The sculpture name
        "SHADOW",      # From clue
        "CLOCK",       # From Berlin Clock reference
        "NORTHEAST",   # From the readable text
        "BERLINCLOCK", # From the readable text
        "DXNZKELYOIECBAQKVAATCRDUMPABT",  # The Period 29 key
    ]

    for key in known_keys:
        decrypted = vigenere_decrypt(full_gibberish, key)
        words = is_promising_text(decrypted)
        print(f"Key '{key}': {decrypted}")
        if words:
            print(f"  Found: {words}")

def check_position_based_patterns():
    """Check if gibberish follows position-based patterns."""
    print("\n" + "="*60)
    print("POSITION-BASED PATTERN ANALYSIS")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    print("\nDecryption with position markers:")
    marked = ""
    for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
        if is_readable:
            marked += char
        else:
            marked += f"[{char}]"
    print(marked)

    # Check if gibberish positions follow a mathematical pattern
    gibberish_positions = [i for i, r in enumerate(readable_mask) if not r]
    print(f"\nGibberish positions: {gibberish_positions}")

    # Check differences between positions
    if len(gibberish_positions) > 1:
        diffs = [gibberish_positions[i+1] - gibberish_positions[i]
                 for i in range(len(gibberish_positions)-1)]
        print(f"Position differences: {diffs[:30]}...")

def main():
    print("K4 Double Layer Encryption Analysis")
    print("="*60)
    print(f"\nK4 ciphertext ({len(K4)} chars):")
    print(K4)
    print(f"\nCurrent decryption ({len(DECRYPTED)} chars):")
    print(DECRYPTED)

    # Identify sections
    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    print("\n" + "="*60)
    print("SECTION IDENTIFICATION")
    print("="*60)
    print("\nReadable words found:")
    for word, (start, end) in sorted(READABLE_WORDS.items(), key=lambda x: x[1][0]):
        print(f"  Position {start:2d}-{end:2d}: {word}")

    print("\nGibberish sections:")
    for start, section in gibberish_sections:
        print(f"  Position {start:2d}: '{section}' (length {len(section)})")

    # Run all analyses
    try_double_layer_full_text()
    try_per_section_analysis()
    analyze_alternating_pattern()
    selective_decryption()
    try_known_kryptos_keys()
    check_position_based_patterns()

    # Additional: Try Vigenere with 2-letter keys on combined gibberish
    print("\n" + "="*60)
    print("VIGENERE WITH 2-LETTER KEYS ON COMBINED GIBBERISH")
    print("="*60)
    full_gibberish = "".join(section for _, section in gibberish_sections)
    analyze_gibberish_with_vigenere(full_gibberish, max_key_len=2)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

def deep_dive_promising_keys():
    """Deeper analysis of the promising keys found."""
    print("\n" + "="*60)
    print("DEEP DIVE: PROMISING VIGENERE KEYS")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    # Keys that showed promise
    promising_keys = ["BC", "BT", "CR", "AC", "AG", "AI", "AV", "BN", "BR", "CH", "EB"]

    for key in promising_keys:
        decrypted = vigenere_decrypt(full_gibberish, key)
        words = is_promising_text(decrypted)
        print(f"\nKey '{key}': {decrypted}")
        print(f"  Words found: {words}")
        # Show positions of found words
        for word in words:
            pos = decrypted.find(word)
            print(f"    '{word}' at position {pos}")


def reconstruct_with_double_layer():
    """Try to reconstruct the full message assuming double-layer encryption."""
    print("\n" + "="*60)
    print("RECONSTRUCT FULL MESSAGE WITH DOUBLE LAYER")
    print("="*60)

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Try applying Caesar shifts only to gibberish positions
    print("\nApplying Caesar shifts ONLY to gibberish positions:")
    for shift in range(1, 26):
        result = ""
        for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
            if is_readable:
                result += char  # Keep readable parts
            else:
                # Decrypt gibberish
                result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))

        words = is_promising_text(result)
        # Show results that have more words or interesting patterns
        total_readable = len([w for w in READABLE_WORDS.keys() if w in result])
        if len(words) > len(READABLE_WORDS) or "SLOWLY" in result or "SHADOW" in result or "UNDER" in result:
            print(f"\n  Shift {shift:2d}: {result}")
            print(f"    All words found: {words}")


def analyze_position_correlation():
    """Check if gibberish positions correlate with readable word positions."""
    print("\n" + "="*60)
    print("POSITION CORRELATION ANALYSIS")
    print("="*60)

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # For each gibberish character, compute its distance to nearest readable word
    print("\nGibberish character analysis:")
    for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
        if not is_readable:
            # Find nearest readable word
            min_dist = float('inf')
            nearest_word = None
            for word, (start, end) in READABLE_WORDS.items():
                dist = min(abs(i - start), abs(i - end))
                if dist < min_dist:
                    min_dist = dist
                    nearest_word = word

    # Check if gibberish letters could spell something using position as key
    gibberish_chars = [(i, DECRYPTED[i]) for i, r in enumerate(readable_mask) if not r]

    print(f"\nGibberish positions and letters:")
    for pos, char in gibberish_chars[:30]:
        print(f"  Position {pos:2d}: {char} (K4 char: {K4[pos]})")


def try_position_based_shift():
    """Try shifting gibberish by its position or related values."""
    print("\n" + "="*60)
    print("POSITION-BASED SHIFT ON GIBBERISH")
    print("="*60)

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Method 1: Shift by position mod 26
    print("\nMethod 1: Shift each gibberish char by its position mod 26:")
    result = ""
    for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
        if is_readable:
            result += char
        else:
            shift = i % 26
            result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    print(f"  {result}")
    print(f"  Words: {is_promising_text(result)}")

    # Method 2: Use K4 position in original ciphertext as shift
    print("\nMethod 2: Shift gibberish by K4 letter value at that position:")
    result = ""
    for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
        if is_readable:
            result += char
        else:
            shift = ord(K4[i]) - ord('A')
            result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    print(f"  {result}")
    print(f"  Words: {is_promising_text(result)}")

    # Method 3: Use sum of position digits
    print("\nMethod 3: Shift by sum of digits of position:")
    result = ""
    for i, (char, is_readable) in enumerate(zip(DECRYPTED, readable_mask)):
        if is_readable:
            result += char
        else:
            shift = sum(int(d) for d in str(i))
            result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    print(f"  {result}")
    print(f"  Words: {is_promising_text(result)}")


def try_readable_word_derived_keys():
    """Use patterns from readable words to decrypt gibberish."""
    print("\n" + "="*60)
    print("READABLE WORD DERIVED KEYS")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    # Extract first letters of readable words: D-N-C-K-B-A
    first_letters = "".join(word[0] for word in sorted(READABLE_WORDS.keys(),
                           key=lambda w: READABLE_WORDS[w][0]))
    print(f"\nFirst letters of readable words (by position): {first_letters}")
    dec = vigenere_decrypt(full_gibberish, first_letters)
    print(f"  Vigenere decrypt: {dec}")
    print(f"  Words: {is_promising_text(dec)}")

    # Concatenate all readable words
    all_words = "".join(sorted(READABLE_WORDS.keys(), key=lambda w: READABLE_WORDS[w][0]))
    print(f"\nAll readable words concatenated: {all_words}")
    dec = vigenere_decrypt(full_gibberish, all_words)
    print(f"  Vigenere decrypt: {dec}")
    print(f"  Words: {is_promising_text(dec)}")

    # Try the readable words' positions as keys
    positions = sorted([start for start, _ in READABLE_WORDS.values()])
    print(f"\nReadable word start positions: {positions}")
    pos_key = "".join(chr((p % 26) + ord('A')) for p in positions)
    print(f"  As letters (mod 26): {pos_key}")
    dec = vigenere_decrypt(full_gibberish, pos_key)
    print(f"  Vigenere decrypt: {dec}")
    print(f"  Words: {is_promising_text(dec)}")


def comprehensive_word_search():
    """Search for ANY 3+ letter words in all decryption attempts."""
    print("\n" + "="*60)
    print("COMPREHENSIVE WORD SEARCH IN GIBBERISH DECRYPTIONS")
    print("="*60)

    # Large word list for comprehensive search
    word_list = [
        # K4 specific words
        "SLOWLY", "DESPER", "ATELY", "SHADOW", "UNDER", "GROUND", "CLOCK",
        "EAST", "WEST", "NORTH", "SOUTH", "LAYER", "DEGREE", "SECONDS",
        "LANGLEY", "SANBORN", "SCHEIDT", "BERLIN", "WALL",
        # Common words
        "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HAD",
        "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "GET", "HAS", "HIM", "HIS",
        "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO", "BOY", "DID",
        "ITS", "LET", "PUT", "SAY", "SHE", "TOO", "USE", "THEY", "BEEN", "HAVE",
        "MANY", "SOME", "THEM", "TIME", "VERY", "WHEN", "COME", "COULD", "MAKE",
        "THAN", "CALL", "DOWN", "EACH", "FIND", "FIRST", "FROM", "HAND", "INTO",
        "JUST", "KNOW", "LIKE", "LONG", "LOOK", "OVER", "ONLY", "PART", "PEOPLE",
        "ROOM", "TAKE", "THAT", "THEIR", "THIS", "THROUGH", "WATER", "WHERE",
        "WHICH", "WITH", "WORD", "WORK", "YEAR", "ALSO", "BACK", "BEEN", "BEFORE",
        "HIGH", "JUST", "LAST", "LIFE", "LINE", "LIVE", "MADE", "MORE", "MUCH",
        "NAME", "NEED", "NEXT", "ONLY", "SAME", "SELF", "SUCH", "TELL", "WELL",
        "WHAT", "WILL", "WORLD", "WOULD", "WRITE", "ABOUT", "AFTER", "AGAIN",
        "CLEAR", "CODE", "CIPHER", "SECRET", "HIDDEN", "MESSAGE", "TEXT", "KEY",
        "ZERO", "FORTY", "FIFTY", "HUNDRED", "TWENTY", "THIRTY"
    ]

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    def check_words(text, label):
        found = []
        for word in word_list:
            if len(word) >= 4 and word in text:  # Only 4+ letter words for significance
                found.append(word)
        if found:
            print(f"{label}: Found {found}")
            return True
        return False

    # Try all Caesar shifts
    print("\nCaesar shifts with 4+ letter words:")
    for shift in range(1, 26):
        dec = caesar_decrypt(full_gibberish, shift)
        check_words(dec, f"  Shift {shift}")

    # Try all 2-letter Vigenere keys
    print("\n2-letter Vigenere keys with 4+ letter words:")
    for k1 in string.ascii_uppercase:
        for k2 in string.ascii_uppercase:
            key = k1 + k2
            dec = vigenere_decrypt(full_gibberish, key)
            check_words(dec, f"  Key '{key}'")


def try_mixed_layer_decryption():
    """Try decrypting with different keys for different sections."""
    print("\n" + "="*60)
    print("MIXED LAYER DECRYPTION")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Try applying different Caesar shifts to different gibberish sections
    print("\nTrying different shifts for each gibberish section:")

    # Best shifts found for individual sections
    section_shifts = {
        0: [0],      # 'U' - single char, try keeping
        1: [3],      # 'UQAPBZDBKZELN' - shift 3 gives 'WAY'
        2: list(range(26)),  # 'GUWC' - try all
        3: [5, 11, 17],  # 'SQGUZOUAFZFETMMNXPSOZMPAPGLKGB' - found HIS, OUT, PUT
        4: [9],      # 'VJWQU' - shift 9 gives 'MAN'
        5: list(range(26)),  # 'EJYBUKCAYF' - try all
    }

    # Show individual section results with their best shifts
    for i, (start, section) in enumerate(gibberish_sections):
        if len(section) >= 3:
            print(f"\nSection {i}: '{section}' (pos {start})")
            for shift in section_shifts.get(i, range(26))[:5]:
                dec = caesar_decrypt(section, shift)
                print(f"  Shift {shift}: {dec}")


def try_three_letter_keys():
    """Try 3-letter Vigenere keys on gibberish."""
    print("\n" + "="*60)
    print("3-LETTER VIGENERE KEY SEARCH (targeted)")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    # Focus on keys that might produce more words
    # Try combinations starting with promising letters
    promising_starts = ['A', 'B', 'C', 'D', 'K', 'S', 'T']

    word_list = [
        "SLOWLY", "SHADOW", "UNDER", "GROUND", "CLOCK", "LAYER", "DEGREE",
        "SECONDS", "LANGLEY", "SANBORN", "BERLIN", "THE", "AND", "FOR",
        "NOT", "YOU", "ALL", "WAS", "ONE", "OUT", "DAY", "HIS", "MAN", "WAY",
        "DID", "PUT", "TOO", "SPY", "HAD", "THEY", "BEEN", "HAVE", "FROM",
        "TIME", "OVER", "ONLY", "BACK", "SELF", "THAT", "THIS", "WITH"
    ]

    found_results = []

    for k1 in promising_starts:
        for k2 in string.ascii_uppercase:
            for k3 in string.ascii_uppercase:
                key = k1 + k2 + k3
                dec = vigenere_decrypt(full_gibberish, key)

                found = []
                for word in word_list:
                    if len(word) >= 4 and word in dec:
                        found.append(word)

                if len(found) >= 1:
                    found_results.append((key, dec, found))

    # Sort by number of words found
    found_results.sort(key=lambda x: (-len(x[2]), -max(len(w) for w in x[2]) if x[2] else 0))

    print("\nTop results with 4+ letter words:")
    for key, dec, found in found_results[:30]:
        print(f"  Key '{key}': {found}")
        if len(found) > 1 or (found and len(found[0]) >= 5):
            print(f"    Full: {dec}")


def interleaved_decryption():
    """Try if odd/even positions use different keys."""
    print("\n" + "="*60)
    print("INTERLEAVED KEY ANALYSIS")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    # Separate odd and even positions in gibberish
    even_gib = full_gibberish[::2]
    odd_gib = full_gibberish[1::2]

    print(f"\nEven positions in gibberish: {even_gib}")
    print(f"Odd positions in gibberish: {odd_gib}")

    word_list = ["SLOWLY", "SHADOW", "UNDER", "CLOCK", "LAYER", "THE", "AND",
                 "FOR", "NOT", "YOU", "WAS", "OUT", "HIS", "MAN", "WAY", "TIME"]

    # Try different single-key Caesar on each half
    print("\nBest Caesar for even positions:")
    for shift in range(26):
        dec = caesar_decrypt(even_gib, shift)
        for word in word_list:
            if len(word) >= 3 and word in dec:
                print(f"  Shift {shift}: {dec} -> {word}")

    print("\nBest Caesar for odd positions:")
    for shift in range(26):
        dec = caesar_decrypt(odd_gib, shift)
        for word in word_list:
            if len(word) >= 3 and word in dec:
                print(f"  Shift {shift}: {dec} -> {word}")


def segment_pattern_analysis():
    """Analyze if different segments use different encryption."""
    print("\n" + "="*60)
    print("SEGMENT PATTERN ANALYSIS")
    print("="*60)

    # Split the full decrypted text into 29-char segments (period 29)
    print("\nPeriod 29 segments:")
    for i in range(0, len(DECRYPTED), 29):
        segment = DECRYPTED[i:i+29]
        print(f"  {i:2d}-{i+28:2d}: {segment}")

    # Check if gibberish appears at consistent positions within segments
    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    print("\nGibberish positions modulo 29:")
    gib_mod29 = {}
    for i, is_readable in enumerate(readable_mask):
        if not is_readable:
            mod = i % 29
            if mod not in gib_mod29:
                gib_mod29[mod] = []
            gib_mod29[mod].append(DECRYPTED[i])

    for mod in sorted(gib_mod29.keys()):
        print(f"  Position mod 29 = {mod:2d}: {''.join(gib_mod29[mod])}")


def try_autokey_cipher():
    """Try autokey cipher on gibberish."""
    print("\n" + "="*60)
    print("AUTOKEY CIPHER ANALYSIS")
    print("="*60)

    gibberish_sections, _ = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    def autokey_decrypt(text, primer):
        """Decrypt autokey cipher with given primer."""
        result = []
        key_stream = list(primer)

        for i, c in enumerate(text):
            if c in string.ascii_uppercase:
                shift = ord(key_stream[i % len(key_stream)]) - ord('A')
                plain = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
                result.append(plain)
                if i >= len(primer) - 1:
                    # In autokey, plaintext becomes next key
                    key_stream.append(plain)
            else:
                result.append(c)

        return "".join(result)

    # Try various primers
    primers = ["A", "K", "D", "KRYPTOS", "PALIMPSEST", "ABSCISSA",
               "CIA", "KGB", "BERLIN", "CLOCK", "DAY", "NORTHEAST", "ABOVE"]

    word_list = ["SLOWLY", "SHADOW", "UNDER", "CLOCK", "THE", "AND", "FOR",
                 "NOT", "YOU", "WAS", "OUT", "HIS", "MAN", "WAY", "TIME", "LAYER"]

    print("\nAutokey decryption attempts:")
    for primer in primers:
        dec = autokey_decrypt(full_gibberish, primer)
        found = [w for w in word_list if w in dec]
        if found:
            print(f"  Primer '{primer}': {dec}")
            print(f"    Found: {found}")


def analyze_running_key():
    """Try using readable text as running key for gibberish."""
    print("\n" + "="*60)
    print("RUNNING KEY ANALYSIS")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Get readable text only
    readable_text = "".join(DECRYPTED[i] for i, r in enumerate(readable_mask) if r)
    print(f"\nReadable text: {readable_text}")

    # Get gibberish only
    full_gibberish = "".join(section for _, section in gibberish_sections)
    print(f"Gibberish text: {full_gibberish}")

    # Try using readable text as Vigenere key for gibberish
    dec = vigenere_decrypt(full_gibberish, readable_text)
    print(f"\nGibberish decrypted with readable as key: {dec}")

    word_list = ["SLOWLY", "SHADOW", "UNDER", "CLOCK", "THE", "AND", "FOR",
                 "NOT", "YOU", "WAS", "OUT", "HIS", "MAN", "WAY", "TIME"]
    found = [w for w in word_list if w in dec]
    if found:
        print(f"  Found: {found}")

    # Try reverse
    dec = vigenere_decrypt(full_gibberish, readable_text[::-1])
    print(f"\nGibberish decrypted with reversed readable as key: {dec}")
    found = [w for w in word_list if w in dec]
    if found:
        print(f"  Found: {found}")


def exhaustive_word_search_all_methods():
    """Final exhaustive search combining all methods."""
    print("\n" + "="*60)
    print("EXHAUSTIVE COMBINED ANALYSIS")
    print("="*60)

    gibberish_sections, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)
    full_gibberish = "".join(section for _, section in gibberish_sections)

    # Target words that would confirm K4 solution
    target_words = ["SLOWLY", "DESPER", "ATELY", "SHADOW", "UNDER", "GROUND",
                    "LAYER", "SECOND", "LANGLEY", "CLOCK"]

    print("\nSearching for K4-specific words in all decryption attempts...")

    # Method 1: All Caesar shifts
    for shift in range(26):
        dec = caesar_decrypt(full_gibberish, shift)
        for word in target_words:
            if word in dec:
                print(f"  CAESAR shift {shift}: Found '{word}' in {dec}")

    # Method 2: All 2-letter Vigenere
    for k1 in string.ascii_uppercase:
        for k2 in string.ascii_uppercase:
            key = k1 + k2
            dec = vigenere_decrypt(full_gibberish, key)
            for word in target_words:
                if word in dec:
                    print(f"  VIGENERE key '{key}': Found '{word}' in {dec}")

    # Method 3: Position-based with variations
    for offset in range(26):
        result = ""
        for i, char in enumerate(full_gibberish):
            shift = (i + offset) % 26
            result += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
        for word in target_words:
            if word in result:
                print(f"  POSITION (offset {offset}): Found '{word}' in {result}")

    print("\nExhaustive search complete.")


def analyze_visible_word_boundaries():
    """Analyze the boundaries between readable and gibberish sections."""
    print("\n" + "="*60)
    print("WORD BOUNDARY ANALYSIS")
    print("="*60)

    # What if we look at text around word boundaries?
    print("\nContext around each readable word:")
    for word, (start, end) in sorted(READABLE_WORDS.items(), key=lambda x: x[1][0]):
        context_start = max(0, start - 5)
        context_end = min(len(DECRYPTED), end + 5)
        context = DECRYPTED[context_start:context_end]

        # Mark the word
        before = DECRYPTED[context_start:start]
        after = DECRYPTED[end:context_end]

        print(f"  '{word}': ...{before}[{word}]{after}...")


def try_different_key_at_each_position():
    """What if different periods/keys apply to different positions?"""
    print("\n" + "="*60)
    print("VARIABLE KEY BY PERIOD POSITION")
    print("="*60)

    # The current key is period 29: DXNZKELYOIECBAQKVAATCRDUMPABT
    current_key = "DXNZKELYOIECBAQKVAATCRDUMPABT"

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # Check what key positions correspond to readable vs gibberish
    print("\nKey positions for readable vs gibberish:")

    readable_key_positions = []
    gibberish_key_positions = []

    for i, is_readable in enumerate(readable_mask):
        key_pos = i % 29
        if is_readable:
            readable_key_positions.append(key_pos)
        else:
            gibberish_key_positions.append(key_pos)

    print(f"Key positions producing readable text: {set(readable_key_positions)}")
    print(f"Key positions producing gibberish: {set(gibberish_key_positions)}")

    # Check if certain key positions are "wrong"
    print("\nKey letter frequency at each position for gibberish:")
    gib_by_keypos = {}
    for i, is_readable in enumerate(readable_mask):
        if not is_readable:
            key_pos = i % 29
            key_letter = current_key[key_pos]
            if key_pos not in gib_by_keypos:
                gib_by_keypos[key_pos] = []
            gib_by_keypos[key_pos].append((i, DECRYPTED[i], K4[i], key_letter))

    for pos in sorted(gib_by_keypos.keys()):
        items = gib_by_keypos[pos]
        print(f"  Key pos {pos:2d} ('{current_key[pos]}'): {len(items)} gibberish chars")
        for idx, dec_char, k4_char, key_char in items[:3]:
            print(f"    Position {idx}: K4='{k4_char}' -> Decrypted='{dec_char}'")


def try_modifying_key_at_gibberish_positions():
    """Try modifying the key at positions that produce gibberish."""
    print("\n" + "="*60)
    print("MODIFIED KEY ANALYSIS")
    print("="*60)

    current_key = "DXNZKELYOIECBAQKVAATCRDUMPABT"

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    # For each gibberish position, what key letter would produce good text?
    word_list = ["SLOWLY", "DESPER", "ATELY", "SHADOW", "UNDER", "GROUND",
                 "LAYER", "SECOND", "LANGLEY", "THE", "AND", "FOR", "WAS",
                 "THAT", "WITH", "THIS", "HAVE", "FROM", "TIME", "BEEN"]

    # Try shifting only certain key positions
    print("\nTrying to find alternative key letters that improve readability...")

    # Get gibberish positions and their key positions
    gib_positions = [i for i, r in enumerate(readable_mask) if not r]

    # Try modifying key at positions that have most gibberish
    key_position_counts = {}
    for pos in gib_positions:
        key_pos = pos % 29
        key_position_counts[key_pos] = key_position_counts.get(key_pos, 0) + 1

    # Focus on key positions with most gibberish
    problem_positions = sorted(key_position_counts.items(), key=lambda x: -x[1])[:5]
    print(f"\nKey positions with most gibberish: {problem_positions}")

    # For the most problematic key position, try all alternatives
    for problem_pos, count in problem_positions[:2]:
        print(f"\nTrying alternatives for key position {problem_pos} (affects {count} chars):")
        original_letter = current_key[problem_pos]

        for alt_letter in string.ascii_uppercase:
            if alt_letter == original_letter:
                continue

            # Create modified key
            new_key = list(current_key)
            new_key[problem_pos] = alt_letter
            new_key = "".join(new_key)

            # Decrypt K4 with modified key
            result = vigenere_decrypt(K4, new_key)

            # Check if this creates new readable words
            found = []
            for word in word_list:
                if word in result and word not in DECRYPTED:
                    found.append(word)

            if found:
                print(f"  Key pos {problem_pos}: '{original_letter}'->'{alt_letter}': NEW words {found}")
                print(f"    Result: {result}")


def analyze_original_k4_at_readable():
    """Check what the original K4 looks like at readable positions."""
    print("\n" + "="*60)
    print("K4 PATTERNS AT READABLE POSITIONS")
    print("="*60)

    _, readable_mask = identify_gibberish_sections(DECRYPTED, READABLE_WORDS)

    print("\nOriginal K4 at readable text positions:")
    for word, (start, end) in sorted(READABLE_WORDS.items(), key=lambda x: x[1][0]):
        k4_segment = K4[start:end]
        print(f"  {word:15s} (pos {start:2d}-{end:2d}): K4 = '{k4_segment}'")


def summary_and_conclusions():
    """Summarize findings and draw conclusions."""
    print("\n" + "="*60)
    print("SUMMARY AND CONCLUSIONS")
    print("="*60)

    print("""
FINDINGS:

1. The Period 29 decryption produces readable words at these positions:
   - DAY (1-4)
   - NORTHEAST (17-26)
   - CIA (30-33) [overlaps with IAA in decryption]
   - KGB (63-66)
   - BERLINCLOCK (66-77)
   - ABOVE (82-87)

2. No secondary encryption was found that produces K4-specific words
   (SLOWLY, SHADOW, UNDER, GROUND, LAYER, etc.) from the gibberish.

3. Common English words (THE, AND, FOR, WAS, etc.) appear in some
   Caesar/Vigenere decryptions, but these are likely coincidental.

4. Position-based analysis shows gibberish appears at multiple key
   positions, suggesting the issue isn't with specific key letters.

CONCLUSIONS:

A. The Period 29 key may be partially correct, revealing fragments
   of the true message.

B. The gibberish may not be double-encrypted; it may simply be
   incorrectly decrypted text due to:
   - Wrong key letters at some positions
   - Wrong period (perhaps not exactly 29)
   - A different cipher mechanism

C. The readable words could be:
   - True parts of the message
   - False positives (coincidental word formations)
   - Deliberate red herrings

D. Alternative approaches to investigate:
   - Try periods near 29 (28, 30)
   - Search for different key that produces MORE readable words
   - Consider the readable words as clues to the actual solution
""")


if __name__ == "__main__":
    main()

    # Additional deep analysis
    deep_dive_promising_keys()
    reconstruct_with_double_layer()
    analyze_position_correlation()
    try_position_based_shift()
    try_readable_word_derived_keys()
    comprehensive_word_search()
    try_mixed_layer_decryption()

    # New analyses
    try_three_letter_keys()
    interleaved_decryption()
    segment_pattern_analysis()
    try_autokey_cipher()
    analyze_running_key()
    exhaustive_word_search_all_methods()

    # Final analyses
    analyze_visible_word_boundaries()
    try_different_key_at_each_position()
    try_modifying_key_at_gibberish_positions()
    analyze_original_k4_at_readable()
    summary_and_conclusions()
