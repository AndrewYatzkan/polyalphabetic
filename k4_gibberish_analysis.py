#!/usr/bin/env python3
"""
K4 Kryptos Gibberish Section Analysis

Analyzes the gibberish sections from the Period 29 solution candidate:
- Key: DXNZKELYOIECBAQKVAATCRDUMPABT
- PT: UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF

Found words: DAY@1, NORTHEAST@16, CIA@29, KGB@60, BERLINCLOCK@63, ABOVE@83
"""

import itertools
from collections import Counter
import re

# The full plaintext
PLAINTEXT = "UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF"
KEY = "DXNZKELYOIECBAQKVAATCRDUMPABT"

# Gibberish sections with their positions (based on user's analysis)
GIBBERISH_SECTIONS = {
    "section_0": {"text": "U", "start": 0, "end": 0, "context": "Before DAY"},
    "section_1": {"text": "UQAPBZDBKZEL", "start": 4, "end": 15, "context": "Between DAY and NORTHEAST"},
    "section_2": {"text": "LGUW", "start": 25, "end": 28, "context": "Between NORTHEAST and CIA"},
    "section_3": {"text": "ASQGUZOUAFZFETMMNXPSOZMPAPGL", "start": 32, "end": 59, "context": "Between CIA and KGB"},
    "section_4": {"text": "RSPVJWQUL", "start": 74, "end": 82, "context": "Between BERLINCLOCK and ABOVE"},
    "section_5": {"text": "JYBUKCAYF", "start": 88, "end": 96, "context": "After ABOVE"},
}

# Context words specific to Kryptos/CIA
CONTEXT_WORDS = [
    # Spy/intelligence words
    "AGENT", "SECRET", "CODE", "CIPHER", "SPY", "INTEL", "MISSION", "COVERT",
    "HIDDEN", "MESSAGE", "ENCRYPT", "DECRYPT", "SIGNAL", "DEAD", "DROP",
    "LANGLEY", "HEADQUARTERS", "SHADOW", "NETWORK", "ASSET", "HANDLER",
    "OPERATION", "CLASSIFIED", "TOP", "BURIED", "UNDERGROUND", "VAULT",
    "SLOWLY", "DESPARATLY", "VIRTUALLY", "INVISIBLE", "PALIMPSEST", "ABSCISSA",
    "ILLUSION", "IQLUSION", "UNDERGRUUND", "LUCID", "MEMORY", "FORCES",

    # Location/direction words
    "NORTH", "SOUTH", "EAST", "WEST", "LATITUDE", "LONGITUDE", "LOCATION",
    "COORDINATES", "DEGREES", "MINUTES", "SECONDS", "FEET", "METERS",
    "BELOW", "UNDER", "GROUND", "SURFACE", "DEEP", "LAYER", "BENEATH",

    # Time words
    "TIME", "CLOCK", "HOUR", "MINUTE", "SECOND", "DAY", "NIGHT", "YEAR",
    "DATE", "WHEN", "UNTIL", "AFTER", "BEFORE",

    # Numbers spelled out
    "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN",
    "ZERO", "HUNDRED", "THOUSAND",

    # K4 known cribs
    "BERLIN", "CLOCK", "NORTHEAST", "EASTNORTHEAST",

    # Common short words
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
    "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HOW", "MAN", "NEW", "NOW",
    "OLD", "SEE", "WAY", "WHO", "DID", "GET", "PUT", "SAY", "SHE",
    "TOO", "USE", "KNOW", "ONLY", "COME", "MADE", "FIND", "HERE", "JUST",
    "LOOK", "OVER", "SUCH", "TAKE", "THAN", "THEM", "THEN", "THEY", "THIS",
    "WILL", "WITH", "HAVE", "FROM", "BEEN", "CALL", "EACH", "INTO", "LONG",
    "MAKE", "MANY", "MORE", "MOST", "SOME", "WHAT", "WHEN", "YOUR",
]

def load_word_list():
    """Load comprehensive word list"""
    words = set(word.upper() for word in CONTEXT_WORDS)

    # Try to load system dictionary
    try:
        with open('/usr/share/dict/words', 'r') as f:
            for line in f:
                word = line.strip().upper()
                if 2 <= len(word) <= 20 and word.isalpha():
                    words.add(word)
    except FileNotFoundError:
        # Use OxfordEnglishWords.txt if available
        try:
            with open('/home/user/polyalphabetic/OxfordEnglishWords.txt', 'r') as f:
                for line in f:
                    word = line.strip().upper()
                    if 2 <= len(word) <= 20 and word.isalpha():
                        words.add(word)
        except FileNotFoundError:
            print("Note: Using context words only")

    return words

WORD_LIST = load_word_list()
print(f"Loaded {len(WORD_LIST)} words")

def shift_letter(letter, shift):
    """Shift a letter by a given amount (can be negative)"""
    if not letter.isalpha():
        return letter
    base = ord('A')
    return chr((ord(letter.upper()) - base + shift) % 26 + base)

def find_anagram_words(text, word_list, min_len=3):
    """Find words that can be formed from anagramming the text"""
    text = text.upper()
    letter_counts = Counter(text)
    found = []

    for word in word_list:
        if len(word) < min_len or len(word) > len(text):
            continue
        word_counts = Counter(word)
        if all(letter_counts[c] >= word_counts[c] for c in word_counts):
            found.append(word)

    return sorted(found, key=len, reverse=True)

def find_substrings(text, word_list, min_len=3):
    """Find valid words that appear as substrings"""
    text = text.upper()
    found = []

    for i in range(len(text)):
        for j in range(i + min_len, len(text) + 1):
            substring = text[i:j]
            if substring in word_list:
                found.append((substring, i, j))

    return found

def try_single_substitutions(text, word_list, distance=2):
    """Try substituting single letters and look for words"""
    text = text.upper()
    results = []

    for i in range(len(text)):
        original = text[i]
        for shift in range(-distance, distance + 1):
            if shift == 0:
                continue
            new_letter = shift_letter(original, shift)
            new_text = text[:i] + new_letter + text[i+1:]

            # Check for substrings in modified text
            substrings = find_substrings(new_text, word_list, min_len=3)
            for word, start, end in substrings:
                if start <= i < end:  # The substitution is in the word
                    results.append({
                        'original': text,
                        'modified': new_text,
                        'word': word,
                        'position': i,
                        'shift': shift,
                        'from': original,
                        'to': new_letter
                    })

    return results

def try_multiple_substitutions(text, word_list, max_changes=2, distance=2):
    """Try multiple letter substitutions"""
    text = text.upper()
    results = []

    if len(text) > 10:  # Skip for very long strings (too many combinations)
        return results

    positions = list(range(len(text)))

    for num_changes in range(1, min(max_changes + 1, len(text) + 1)):
        for pos_combo in itertools.combinations(positions, num_changes):
            shift_options = list(range(-distance, distance + 1))
            shift_options.remove(0)

            for shifts in itertools.product(shift_options, repeat=num_changes):
                new_text = list(text)
                changes = []

                for pos, shift in zip(pos_combo, shifts):
                    old = new_text[pos]
                    new = shift_letter(old, shift)
                    new_text[pos] = new
                    changes.append((pos, old, new, shift))

                new_text = ''.join(new_text)

                # Check if the entire new_text is a word
                if new_text in word_list:
                    results.append({
                        'original': text,
                        'modified': new_text,
                        'word': new_text,
                        'changes': changes,
                        'full_match': True
                    })

                # Check for long substrings
                min_word_len = max(3, len(text) // 2)
                substrings = find_substrings(new_text, word_list, min_len=min_word_len)
                for word, start, end in substrings:
                    if any(start <= pos < end for pos, _, _, _ in changes):
                        results.append({
                            'original': text,
                            'modified': new_text,
                            'word': word,
                            'changes': changes,
                            'full_match': False
                        })

    return results

def analyze_phonetics(text):
    """Analyze text for phonetic patterns"""
    text = text.upper()

    patterns = {
        'double_letters': re.findall(r'(.)\1', text),
        'vowel_sequences': re.findall(r'[AEIOU]{2,}', text),
        'consonant_clusters': re.findall(r'[BCDFGHJKLMNPQRSTVWXYZ]{3,}', text),
        'common_digraphs': re.findall(r'(TH|CH|SH|WH|PH|CK|NG|QU|GH)', text),
        'common_endings': re.findall(r'(ING|TION|ED|LY|ER|EST|NESS|MENT|ABLE|IBLE)', text),
        'common_beginnings': re.findall(r'^(UN|RE|IN|DIS|EN|NON|PRE|MIS|OVER|SUB)', text),
    }

    vowels = sum(1 for c in text if c in 'AEIOU')
    consonants = len(text) - vowels
    patterns['vowel_ratio'] = vowels / len(text) if text else 0
    patterns['vowels'] = vowels
    patterns['consonants'] = consonants

    return patterns

def try_caesar_shifts(text, word_list):
    """Try shifting entire text by each possible amount"""
    results = []

    for shift in range(1, 26):
        shifted = ''.join(shift_letter(c, shift) for c in text)
        substrings = find_substrings(shifted, word_list, min_len=3)
        if substrings:
            results.append({
                'shift': shift,
                'shifted_text': shifted,
                'words_found': substrings
            })

    return results

def find_near_misses(text, target_words):
    """Find target words that are close to segments of text"""
    text = text.upper()
    results = []

    for target in target_words:
        target = target.upper()
        if len(target) > len(text):
            continue

        # Slide target across text
        for start in range(len(text) - len(target) + 1):
            segment = text[start:start+len(target)]
            diff = sum(1 for a, b in zip(segment, target) if a != b)

            if diff <= 2 and len(target) >= 4:
                # Calculate which positions differ
                diffs = [(i, segment[i], target[i]) for i in range(len(target)) if segment[i] != target[i]]
                results.append({
                    'target': target,
                    'segment': segment,
                    'start': start,
                    'differences': diff,
                    'diff_positions': diffs
                })

    return results

def analyze_section(name, section):
    """Comprehensive analysis of a gibberish section"""
    text = section['text']
    print(f"\n{'='*70}")
    print(f"ANALYZING: {name}")
    print(f"Text: {text}")
    print(f"Length: {len(text)}")
    print(f"Position: {section['start']}-{section['end']}")
    print(f"Context: {section['context']}")
    print('='*70)

    # 1. Phonetic analysis
    print("\n--- PHONETIC ANALYSIS ---")
    phonetics = analyze_phonetics(text)
    print(f"Vowel ratio: {phonetics['vowel_ratio']:.2%} ({phonetics['vowels']} vowels, {phonetics['consonants']} consonants)")
    for key, value in phonetics.items():
        if key not in ['vowel_ratio', 'vowels', 'consonants'] and value:
            print(f"  {key}: {value}")

    # 2. Direct substring search
    print("\n--- DIRECT SUBSTRINGS ---")
    substrings = find_substrings(text, WORD_LIST, min_len=2)
    if substrings:
        for word, start, end in sorted(substrings, key=lambda x: len(x[0]), reverse=True)[:15]:
            print(f"  '{word}' at position {start}-{end}")
    else:
        print("  No valid substrings found")

    # 3. Anagram words
    print("\n--- ANAGRAM WORDS ---")
    anagrams = find_anagram_words(text, WORD_LIST, min_len=3)
    if anagrams:
        print(f"  Found {len(anagrams)} anagrammable words")
        top_anagrams = [w for w in anagrams if len(w) >= 4][:20]
        print(f"  Best: {top_anagrams}")
    else:
        print("  No anagram words found")

    # 4. Single letter substitutions
    print("\n--- SINGLE SUBSTITUTIONS (distance 1-2) ---")
    single_subs = try_single_substitutions(text, WORD_LIST, distance=2)
    if single_subs:
        seen = set()
        unique_subs = []
        for sub in single_subs:
            key = (sub['word'], sub['position'], sub['shift'])
            if key not in seen:
                seen.add(key)
                unique_subs.append(sub)

        unique_subs.sort(key=lambda x: len(x['word']), reverse=True)
        for sub in unique_subs[:15]:
            print(f"  Change {sub['from']}->{sub['to']} at pos {sub['position']} (shift {sub['shift']:+d}): '{sub['word']}' in '{sub['modified']}'")
    else:
        print("  No words found with single substitutions")

    # 5. Multiple substitutions (only for shorter strings)
    if len(text) <= 10:
        print("\n--- MULTIPLE SUBSTITUTIONS (up to 2 changes) ---")
        multi_subs = try_multiple_substitutions(text, WORD_LIST, max_changes=2, distance=2)
        if multi_subs:
            seen = set()
            for sub in sorted(multi_subs, key=lambda x: (x.get('full_match', False), len(x['word'])), reverse=True)[:10]:
                key = sub['word']
                if key not in seen:
                    seen.add(key)
                    changes_str = ', '.join(f"{old}->{new} at {pos}" for pos, old, new, shift in sub['changes'])
                    marker = " [FULL MATCH]" if sub.get('full_match') else ""
                    print(f"  '{sub['word']}' via: {changes_str}{marker}")
        else:
            print("  No words found with multiple substitutions")

    # 6. Caesar shifts
    print("\n--- CAESAR SHIFTS ---")
    caesar_results = try_caesar_shifts(text, WORD_LIST)
    if caesar_results:
        best = sorted(caesar_results, key=lambda x: max(len(w) for w, _, _ in x['words_found']), reverse=True)[:5]
        for result in best:
            words = [w for w, _, _ in result['words_found'] if len(w) >= 3]
            if words:
                print(f"  Shift {result['shift']:+d}: {result['shifted_text']}")
                print(f"    Words: {words[:10]}")
    else:
        print("  No significant words found with Caesar shifts")

    # 7. Near misses to target words
    print("\n--- NEAR MISSES TO TARGET WORDS ---")
    target_words = ["SHADOW", "FORCE", "SLOWLY", "LUCID", "MEMORY", "VIRTUAL",
                    "INVISIBLE", "ILLUSION", "PALIMPSEST", "UNDERGROUND", "BENEATH",
                    "BURIED", "HIDDEN", "SECRET", "LAYER", "LEVEL", "DEEP",
                    "LANGLEY", "CLOCK", "TIME", "ZONE", "DEGREES", "MINUTES",
                    "LATITUDE", "LONGITUDE", "COORDINATES", "LOCATION"]
    near_misses = find_near_misses(text, target_words)
    if near_misses:
        for nm in sorted(near_misses, key=lambda x: x['differences'])[:10]:
            print(f"  '{nm['target']}' ~ '{nm['segment']}' at pos {nm['start']} ({nm['differences']} diffs: {nm['diff_positions']})")
    else:
        print("  No near misses found")

    # 8. Letter frequency
    print("\n--- LETTER FREQUENCY ---")
    freq = Counter(text)
    print(f"  {dict(freq.most_common())}")

    # 9. Reversed text analysis
    print("\n--- REVERSED TEXT ---")
    reversed_text = text[::-1]
    print(f"  Reversed: {reversed_text}")
    rev_substrings = find_substrings(reversed_text, WORD_LIST, min_len=3)
    if rev_substrings:
        print(f"  Words in reversed: {[w for w, _, _ in rev_substrings][:10]}")

def look_for_coordinates():
    """Special analysis for coordinate-like patterns"""
    print("\n" + "="*70)
    print("SPECIAL ANALYSIS: COORDINATE PATTERNS")
    print("="*70)

    large_section = GIBBERISH_SECTIONS['section_3']['text']
    print(f"\nLarge section: {large_section}")
    print(f"Length: {len(large_section)}")

    print("\nLetter-to-number mapping (A=1):")
    numbers = [ord(c) - ord('A') + 1 for c in large_section]
    print(f"  {numbers}")

    print("\nLetter-to-number mapping (A=0):")
    numbers = [ord(c) - ord('A') for c in large_section]
    print(f"  {numbers}")

    # Langley coordinates are approximately: 38.9516 N, 77.1467 W
    # K2 revealed: 38 57 6.5 N, 77 8 44 W
    print("\nChecking for coordinate-like number sequences:")

    # Check if any subsequences could be 38, 57, 77 etc
    for i in range(len(large_section)):
        for length in [2, 3]:
            if i + length <= len(large_section):
                sub = large_section[i:i+length]
                vals = [ord(c) - ord('A') + 1 for c in sub]
                combined = sum(v * (10**(length-1-j)) for j, v in enumerate(vals) if v <= 9)
                if combined in [38, 57, 77, 6, 44, 8]:
                    print(f"  Potential coord value {combined} at position {i}: {sub}")

def analyze_adjacent_context():
    """Analyze gibberish in context of adjacent words"""
    print("\n" + "="*70)
    print("CONTEXTUAL ANALYSIS: Adjacent Words")
    print("="*70)

    contexts = [
        ("U", "DAY", "U+DAY = ?"),
        ("DAY", "UQAPBZDBKZEL", "DAY+gibberish"),
        ("UQAPBZDBKZEL", "NORTHEAST", "gibberish+NORTHEAST"),
        ("NORTHEAST", "LGUW", "NORTHEAST+gibberish"),
        ("LGUW", "CIA", "gibberish+CIA"),
        ("CIA", "ASQGUZOUAFZFETMMNXPSOZMPAPGL", "CIA+gibberish"),
        ("ASQGUZOUAFZFETMMNXPSOZMPAPGL", "KGB", "gibberish+KGB"),
        ("BERLINCLOCK", "RSPVJWQUL", "BERLINCLOCK+gibberish"),
        ("RSPVJWQUL", "ABOVE", "gibberish+ABOVE"),
        ("ABOVE", "JYBUKCAYF", "ABOVE+gibberish"),
    ]

    for word1, word2, desc in contexts:
        combined = word1 + word2
        print(f"\n{desc}: {word1} + {word2} = {combined}")

        # Look for spanning words
        substrings = find_substrings(combined, WORD_LIST, min_len=4)
        spanning = [s for s in substrings if s[1] < len(word1) and s[2] > len(word1)]

        if spanning:
            print(f"  SPANNING WORDS: {[(w, start, end) for w, start, end in spanning]}")

        # Also check if combined starts/ends with interesting words
        for length in range(4, min(10, len(combined)+1)):
            prefix = combined[:length]
            suffix = combined[-length:]
            if prefix in WORD_LIST and prefix not in [word1, word2]:
                print(f"  Prefix word: {prefix}")
            if suffix in WORD_LIST and suffix not in [word1, word2]:
                print(f"  Suffix word: {suffix}")

def special_word_checks():
    """Check for specific words that might be hidden in the plaintext"""
    print("\n" + "="*70)
    print("SPECIAL WORD CHECKS (full plaintext)")
    print("="*70)

    special_words = [
        "SHADOW", "FORCES", "LUCID", "MEMORY", "UNDERGROUND", "BURIED",
        "HIDDEN", "SECRET", "PALIMPSEST", "LAYER", "SLOWLY", "DESPERATELY",
        "VIRTUALLY", "INVISIBLE", "ILLUSION", "UNDERGRUUND", "IQLUSION",
        "LANGLEY", "HEADQUARTERS", "DEGREES", "LATITUDE", "LONGITUDE",
        "COORDINATES", "LOCATION", "TREASURE", "VAULT", "TIME", "ZONE",
        "OBSCURA", "UNDER", "OVER", "WITHIN", "WITHOUT", "BENEATH",
        "DIGETAL", "INTERPRETATOIN", "THEYSHOULDTRANSPARE", "WW",
        "NYPVTT", "FLRVQQPRNG", "KRYPTOS", "SOS", "SANBORN"
    ]

    full_pt = PLAINTEXT
    print(f"\nFull plaintext: {full_pt}")
    print(f"Length: {len(full_pt)}")

    print("\n--- Checking for exact matches and near misses ---")

    for word in special_words:
        # Exact match
        if word in full_pt:
            pos = full_pt.find(word)
            print(f"  FOUND '{word}' at position {pos}")
            continue

        # Near misses (1-2 letter differences)
        for i in range(len(full_pt) - len(word) + 1):
            segment = full_pt[i:i+len(word)]
            diff = sum(1 for a, b in zip(segment, word) if a != b)
            if diff == 1:
                print(f"  NEAR-MISS '{word}' at position {i}: '{segment}' (1 diff)")
            elif diff == 2 and len(word) >= 6:
                print(f"  POSSIBLE '{word}' at position {i}: '{segment}' (2 diffs)")

def analyze_key_relationship():
    """Analyze relationship between gibberish and the key"""
    print("\n" + "="*70)
    print("KEY RELATIONSHIP ANALYSIS")
    print("="*70)

    print(f"Key: {KEY}")
    print(f"Key length: {len(KEY)}")

    for name, section in GIBBERISH_SECTIONS.items():
        text = section['text']
        start = section['start']

        key_segment = ""
        for i in range(len(text)):
            key_pos = (start + i) % len(KEY)
            key_segment += KEY[key_pos]

        print(f"\n{name} (pos {start}): {text}")
        print(f"  Key segment: {key_segment}")

        # Vigenere decrypt
        derived = ""
        for p, k in zip(text, key_segment):
            shift = ord(k) - ord('A')
            derived += shift_letter(p, -shift)
        print(f"  Vigenere decrypt: {derived}")

        # Check derived for words
        derived_words = find_substrings(derived, WORD_LIST, min_len=3)
        if derived_words:
            print(f"  Words in derived: {[w for w, _, _ in derived_words]}")

def full_plaintext_word_scan():
    """Scan the entire plaintext for any words we might have missed"""
    print("\n" + "="*70)
    print("FULL PLAINTEXT WORD SCAN")
    print("="*70)

    print(f"\nPlaintext: {PLAINTEXT}")
    print(f"\nAll words found (min length 3):")

    all_words = find_substrings(PLAINTEXT, WORD_LIST, min_len=3)
    all_words_sorted = sorted(all_words, key=lambda x: (len(x[0]), x[1]), reverse=True)

    # Show longest words first
    seen_ranges = set()
    for word, start, end in all_words_sorted:
        # Check for overlap with already shown words
        overlap = any(start < e and end > s for s, e in seen_ranges)
        marker = "" if not overlap else " (overlaps)"

        if len(word) >= 4:  # Only show significant words
            print(f"  '{word}' at position {start}-{end}{marker}")
            seen_ranges.add((start, end))

def check_partial_extensions():
    """Check if gibberish sections could be partial words extending found words"""
    print("\n" + "="*70)
    print("PARTIAL WORD EXTENSION ANALYSIS")
    print("="*70)

    found_words = {
        "DAY": (1, 4),
        "NORTHEAST": (16, 25),
        "CIA": (29, 32),
        "KGB": (60, 63),
        "BERLINCLOCK": (63, 74),
        "ABOVE": (83, 88),
    }

    # For each found word, check if gibberish before/after could extend it
    print("\nChecking word extensions:")

    # UDAY -> could be SUNDAY, MONDAY, TUESDAY, etc.?
    print(f"\n  Before DAY: U + DAY = UDAY")
    uday_extends = [w for w in WORD_LIST if w.endswith("UDAY") or w.startswith("UDAY")]
    print(f"    Words containing UDAY: {uday_extends[:10]}")

    # DAYUQAPBZDBKZEL - what words start with DAY?
    print(f"\n  After DAY: DAY + UQAPBZDBKZEL")
    day_extends = [w for w in WORD_LIST if w.startswith("DAY") and len(w) > 3]
    print(f"    Words starting with DAY: {day_extends[:10]}")

    # LGUWCIA - check LGUW
    print(f"\n  Before CIA: LGUW + CIA = LGUWCIA")
    print(f"    Checking if LGUW could be part of a word...")
    lguw_words = [w for w in WORD_LIST if "LGUW" in w]
    print(f"    Words containing LGUW: {lguw_words}")

    # After CIA
    print(f"\n  After CIA: CIA + ASQGUZOUAFZFETMMNXPSOZMPAPGL")
    # Check beginning of gibberish for word starts
    gibberish = "ASQGUZOUAFZFETMMNXPSOZMPAPGL"
    for length in range(3, 8):
        prefix = gibberish[:length]
        matching = [w for w in WORD_LIST if w.startswith(prefix)]
        if matching:
            print(f"    Words starting with {prefix}: {matching[:5]}")

    # ABOVEJYBUKCAYF
    print(f"\n  After ABOVE: ABOVE + JYBUKCAYF = ABOVEJYBUKCAYF")
    above_extends = [w for w in WORD_LIST if w.startswith("ABOVE") and len(w) > 5]
    print(f"    Words starting with ABOVE: {above_extends[:10]}")

def main():
    print("K4 KRYPTOS GIBBERISH SECTION ANALYSIS")
    print("="*70)
    print(f"Full plaintext: {PLAINTEXT}")
    print(f"Total length: {len(PLAINTEXT)}")
    print(f"Key: {KEY}")
    print(f"Word list size: {len(WORD_LIST)} words")

    # Analyze each section
    for name, section in GIBBERISH_SECTIONS.items():
        analyze_section(name, section)

    # Special analyses
    look_for_coordinates()
    analyze_adjacent_context()
    special_word_checks()
    analyze_key_relationship()
    full_plaintext_word_scan()
    check_partial_extensions()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
Key observations from analysis:
1. The gibberish sections need further investigation for:
   - Anagram possibilities
   - Single/multiple letter substitution corrections
   - Coordinate encodings
   - Word boundary extensions

2. Near-miss analysis may reveal intended words with key errors

3. The pattern of found words (DAY, NORTHEAST, CIA, KGB, BERLINCLOCK, ABOVE)
   suggests a geopolitical/Cold War theme

4. The key relationship analysis may reveal if gibberish is encoded differently
    """)

if __name__ == "__main__":
    main()
