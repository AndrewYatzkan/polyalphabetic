#!/usr/bin/env python3
"""
K4 MASSIVE BRUTE FORCE ATTACK

Tries THOUSANDS of variations of key positions 0-4 and 25-28 to find
solutions that produce MORE English words than the current 4-word solution.

Current solution:
  Key: DIJJQELYOIECBAQKVAATCRDUMPABT
  Words: UNDER, NORTHEAST, BERLINCLOCK, ABOVE

Goal: Find 5+ words by varying the unknown key positions.
"""

import itertools
from collections import defaultdict
import time

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Comprehensive English word list for scoring
ENGLISH_WORDS = {
    # 2-letter words (low value)
    'AN', 'AS', 'AT', 'BE', 'BY', 'DO', 'GO', 'HE', 'IF', 'IN', 'IS', 'IT',
    'ME', 'MY', 'NO', 'OF', 'ON', 'OR', 'SO', 'TO', 'UP', 'US', 'WE',

    # 3-letter words (medium value)
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
    'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'SAY', 'SHE', 'TWO',
    'WAY', 'WHO', 'DID', 'HIM', 'GET', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE',
    'ANY', 'DAY', 'HAD', 'HOW', 'MAY', 'ITS', 'LET', 'PUT', 'TOO', 'USE',
    'END', 'OWN', 'TOP', 'TRY', 'AGO', 'AIR', 'SET', 'RUN', 'WAR', 'KEY',
    'MAP', 'SIX', 'TEN', 'CIA', 'NSA', 'KGB', 'DIG', 'LAY', 'SAT', 'RED',

    # 4-letter words (high value)
    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN',
    'CALL', 'FIND', 'LONG', 'DOWN', 'OVER', 'SUCH', 'TAKE', 'KNOW', 'COME',
    'MAKE', 'THAN', 'VERY', 'WHEN', 'WHAT', 'SOME', 'THEM', 'ONLY', 'INTO',
    'TIME', 'LOOK', 'JUST', 'USED', 'EACH', 'WELL', 'ALSO', 'PLAY', 'BACK',
    'WORK', 'HAND', 'PART', 'YEAR', 'WANT', 'GIVE', 'MOST', 'EVEN', 'MANY',
    'SAID', 'HERE', 'THEN', 'LAST', 'MUST', 'DOES', 'LEFT', 'TURN', 'NEXT',
    'AREA', 'AWAY', 'HIGH', 'KEEP', 'WENT', 'TELL', 'NEED', 'HELP', 'WEST',
    'EAST', 'MOVE', 'LIVE', 'ONCE', 'SIDE', 'OPEN', 'SAME', 'SHOW', 'STOP',
    'TRUE', 'CODE', 'SITE', 'SIGN', 'ZERO', 'FIVE', 'FOUR', 'NINE', 'HIDE',
    'DEEP', 'NEAR', 'CLUE', 'WALL', 'GATE', 'PASS', 'READ', 'WORD', 'TEXT',
    'ROOM', 'DOOR', 'CITY', 'HEAD', 'FOOT', 'FEET', 'MILE', 'YARD', 'INCH',
    'HOUR', 'WEEK', 'DAYS', 'MARK', 'SPOT', 'SITE', 'BASE', 'LAND', 'PATH',
    'STEP', 'WALK', 'HALF', 'LINE', 'SCAN', 'ZONE', 'VOID', 'NULL', 'DARK',
    'COLD', 'WARM', 'DEAD', 'TOMB', 'BURY', 'DIRT', 'ROCK', 'SAND', 'CLAY',
    'IRON', 'GOLD', 'LEAD', 'ZINC', 'TUBE', 'PIPE', 'WIRE', 'POLE', 'POST',

    # 5-letter words (very high value)
    'UNDER', 'ABOVE', 'BELOW', 'AFTER', 'AGAIN', 'ABOUT', 'BEING', 'BELOW',
    'COULD', 'EVERY', 'FIRST', 'FOUND', 'GREAT', 'HOUSE', 'LARGE', 'LATER',
    'LIGHT', 'MIGHT', 'NEVER', 'NIGHT', 'NORTH', 'OTHER', 'PLACE', 'POINT',
    'RIGHT', 'SHALL', 'SINCE', 'SMALL', 'SOUTH', 'STILL', 'THEIR', 'THERE',
    'THESE', 'THING', 'THINK', 'THREE', 'UNTIL', 'WATER', 'WHERE', 'WHICH',
    'WHILE', 'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOUNG', 'CLOCK', 'LAYER',
    'EARTH', 'FIELD', 'POINT', 'STONE', 'BRICK', 'STEEL', 'GLASS', 'METAL',
    'DEPTH', 'LEVEL', 'FLOOR', 'SHAFT', 'VAULT', 'CACHE', 'CHEST', 'CRYPT',
    'GRAVE', 'RUINS', 'TOWER', 'BLOCK', 'TRACK', 'TRAIL', 'ROUTE', 'CROSS',
    'SEVEN', 'EIGHT', 'FORTY', 'FIFTY', 'SIXTY', 'MINUS', 'TIMES', 'ANGLE',
    'RADIO', 'RADAR', 'LASER', 'SONAR', 'AGENT', 'INTEL', 'COVER', 'BLACK',
    'WHITE', 'GREEN', 'BROWN', 'CLEAR', 'PLAIN', 'QUIET', 'EMPTY', 'SOLID',
    'THICK', 'SHORT', 'FIFTY', 'THIRD', 'FINAL', 'TOTAL', 'EXACT', 'SHARP',
    'BLIND', 'SIGHT', 'SOUND', 'TOUCH', 'TASTE', 'SMELL', 'SENSE', 'TRUTH',

    # 6-letter words
    'BEHIND', 'BEFORE', 'BERLIN', 'BOTTOM', 'CENTER', 'CENTRE', 'DEGREE',
    'DURING', 'ELEVEN', 'GROUND', 'HIDDEN', 'INSIDE', 'LENGTH', 'LETTER',
    'LOCATE', 'MIDDLE', 'MINUTE', 'NUMBER', 'OBJECT', 'PEOPLE', 'RECENT',
    'RECORD', 'SECRET', 'SHADOW', 'SHOULD', 'SIGNAL', 'SYSTEM', 'TARGET',
    'THIRTY', 'TWENTY', 'TWELVE', 'UPWARD', 'WITHIN', 'BEYOND', 'BURIED',
    'CORNER', 'DOUBLE', 'FIGURE', 'MARKER', 'METERS', 'MOTION', 'NARROW',
    'OFFSET', 'ORIGIN', 'OUTSET', 'RADIUS', 'SEARCH', 'SECOND', 'SOURCE',
    'SQUARE', 'STATUE', 'SUBWAY', 'SUMMIT', 'TUNNEL', 'VECTOR', 'VERTEX',
    'CIPHER', 'CYPHER', 'DECODE', 'ENCODE', 'ENIGMA', 'PUZZLE', 'RIDDLE',

    # 7-letter words
    'BETWEEN', 'CENTRAL', 'DEGREES', 'EASTERN', 'FIFTEEN', 'FORWARD',
    'HUNDRED', 'INDICES', 'INITIAL', 'LANGLEY', 'LOCATED', 'MEASURE',
    'MINUTES', 'OPENING', 'PASSAGE', 'PATTERN', 'PRIMARY', 'QUARTER',
    'READING', 'SEVENTY', 'SIXTEEN', 'STATION', 'SUBSECT', 'SURFACE',
    'THROUGH', 'TOWARDS', 'TRANSIT', 'UNKNOWN', 'UPWARDS', 'WESTERN',
    'BENEATH', 'CONTROL', 'COUNTER', 'ELEMENT', 'HEADING', 'HEIGHTS',
    'INCLINE', 'LATERAL', 'MEASURE', 'MISSION', 'OBSCURE', 'PRECISE',
    'PROJECT', 'RESTORE', 'SEGMENT', 'SECTION', 'SHELTER', 'SITUATE',

    # 8-letter words
    'DIRECTLY', 'DISTANCE', 'DOWNWARD', 'EASTWARD', 'EIGHTEEN', 'ENTRANCE',
    'FOURTEEN', 'LOCATION', 'MAGNETIC', 'MERIDIAN', 'NINETEEN', 'NORTHERN',
    'PARALLEL', 'POSITION', 'RETRIEVE', 'REVEALED', 'SOUTHERN', 'STARTING',
    'TERMINUS', 'THIRTEEN', 'VERTICAL', 'WESTWARD', 'CONCEALS', 'CONTAINS',
    'CONTROLS', 'ENTRANCE', 'EXPOSURE', 'GRADIENT', 'INSCRIPT', 'LATITUDE',
    'MONUMENT', 'MERIDIAN', 'OBSTACLE', 'ORIENTED', 'PROTOCOL', 'QUADRANT',
    'TRANSMIT', 'TRAVERSE', 'TREASURE', 'WAYPOINT', 'ARCHIVES', 'BASEMENT',
    'ARTIFACT', 'BOUNDARY', 'COMPOUND', 'CONTENTS', 'CYLINDER', 'CYLINDER',

    # 9-letter words
    'CLOCKWISE', 'DIRECTION', 'ENCRYPTED', 'LONGITUDE', 'SOUTHWEST', 'SOUTHEAST',
    'NORTHWEST', 'NORTHEAST', 'SECONDARY', 'THEREFORE', 'ELEVATION', 'PERIMETER',
    'CALCULATE', 'DETERMINE', 'FOLLOWING', 'MAGNITUDE', 'REFERENCE', 'SEVENTEEN',
    'STRUCTURE', 'THRESHOLD', 'TRAJECTORY', 'TRANSMITS', 'RECEIVING', 'OPERATION',

    # 10+ letter words
    'UNDERNEATH', 'COORDINATE', 'SUBTERRAIN', 'UNDERCOVER', 'CROSSROADS',
    'FOUNDATION', 'HEMISPHERE', 'HORIZONTAL', 'EXCAVATION', 'DIRECTIONS',
    'CALCULATED', 'DISCOVERED', 'POSITIONED', 'TRANSLATED', 'DECRYPTION',

    # Kryptos-specific words
    'BERLINCLOCK', 'PALIMPSEST', 'IQLUSION', 'ABSCISSA', 'DIGETAL',
    'UNDERGRUUND', 'VIRTUALLY', 'INVISIBLE',
}

# Additional bigrams and trigrams to help identify partial words
COMMON_TRIGRAMS = {'THE', 'AND', 'ING', 'ENT', 'ION', 'HER', 'FOR', 'THA',
                   'NTH', 'INT', 'ERE', 'TIO', 'TER', 'EST', 'ERS', 'ATI',
                   'HAT', 'ATE', 'ALL', 'ETH', 'HES', 'VER', 'HIS', 'OFT'}

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt using Vigenere cipher with KRYPTOS alphabet."""
    return ''.join(alpha[(alpha.index(c) - alpha.index(key[i % len(key)])) % len(alpha)]
                   for i, c in enumerate(ct))

def find_words(text):
    """Find all English words in text."""
    found = []
    text_len = len(text)
    for word in ENGLISH_WORDS:
        word_len = len(word)
        if word_len >= 3:  # Only count words 3+ letters
            pos = text.find(word)
            while pos >= 0:
                # Check it's not part of an already found longer word at same position
                found.append((word, pos))
                pos = text.find(word, pos + 1)

    # Remove subwords (e.g., if NORTHEAST found, don't count NORTH and EAST separately at same pos)
    found.sort(key=lambda x: (-len(x[0]), x[1]))
    filtered = []
    used_positions = set()
    for word, pos in found:
        overlap = False
        for p in range(pos, pos + len(word)):
            if p in used_positions:
                overlap = True
                break
        if not overlap:
            filtered.append((word, pos))
            for p in range(pos, pos + len(word)):
                used_positions.add(p)

    return sorted(filtered, key=lambda x: x[1])

def score_solution(text, words_found):
    """Score a solution based on words found and quality."""
    score = 0
    for word, pos in words_found:
        word_len = len(word)
        if word_len >= 9:
            score += word_len * 5  # 9+ letter words are very valuable
        elif word_len >= 6:
            score += word_len * 3  # 6-8 letter words
        elif word_len >= 4:
            score += word_len * 2  # 4-5 letter words
        else:
            score += word_len  # 3 letter words

    # Bonus for cribs being present
    if 'BERLINCLOCK' in text:
        score += 50
    if 'NORTHEAST' in text:
        score += 40

    return score

def generate_key_variations(base_key, positions, letters):
    """Generate all possible key variations for given positions."""
    key_list = list(base_key)
    for combo in itertools.product(letters, repeat=len(positions)):
        for i, pos in enumerate(positions):
            key_list[pos] = combo[i]
        yield ''.join(key_list)

def main():
    print("="*80)
    print("K4 MASSIVE BRUTE FORCE ATTACK")
    print("="*80)
    print(f"Ciphertext: {K4}")
    print(f"Length: {len(K4)}")
    print()

    # Current best solution
    BASE_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"
    base_plaintext = vigenere_decrypt(K4, BASE_KEY)
    base_words = find_words(base_plaintext)
    base_score = score_solution(base_plaintext, base_words)

    print("Current solution:")
    print(f"  Key: {BASE_KEY}")
    print(f"  Plaintext: {base_plaintext}")
    print(f"  Words: {[w for w, p in base_words]}")
    print(f"  Score: {base_score}")
    print()

    # Track best solutions
    best_solutions = []
    min_words_required = 5

    # All letters to try
    ALL_LETTERS = KRYPTOS_ALPHA

    # Positions to vary
    # Positions 0-4 (currently DIJJQ)
    # Positions 25-28 (currently PABT)

    start_time = time.time()
    attempts = 0

    print("="*80)
    print("PHASE 1: Varying positions 0-4 (DIJJQ)")
    print("="*80)

    # Try all combinations for positions 0-4 (26^5 = 11.8M - too many)
    # Use heuristics: focus on common letters
    COMMON_LETTERS = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'

    # First pass: try common letters for positions 0-4
    positions_0_4 = [0, 1, 2, 3, 4]

    # Try top 8 letters for each position = 8^5 = 32768 combinations
    top_letters = COMMON_LETTERS[:8]

    print(f"Trying top {len(top_letters)} letters for each of positions 0-4...")
    print(f"Total combinations: {len(top_letters)**5}")

    for combo in itertools.product(top_letters, repeat=5):
        key = list(BASE_KEY)
        for i, pos in enumerate(positions_0_4):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(K4, key_str)
        words = find_words(plaintext)

        attempts += 1

        if len(words) >= min_words_required:
            score = score_solution(plaintext, words)
            best_solutions.append((key_str, plaintext, words, score))
            print(f"\n*** FOUND {len(words)} words! ***")
            print(f"Key: {key_str}")
            print(f"Plaintext: {plaintext}")
            print(f"Words: {[w for w, p in words]}")

    print(f"\nPhase 1 complete: {attempts} attempts, {len(best_solutions)} solutions with 5+ words")

    print()
    print("="*80)
    print("PHASE 2: Varying positions 25-28 (PABT)")
    print("="*80)

    positions_25_28 = [25, 26, 27, 28]

    print(f"Trying top {len(top_letters)} letters for each of positions 25-28...")
    print(f"Total combinations: {len(top_letters)**4}")

    for combo in itertools.product(top_letters, repeat=4):
        key = list(BASE_KEY)
        for i, pos in enumerate(positions_25_28):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(K4, key_str)
        words = find_words(plaintext)

        attempts += 1

        if len(words) >= min_words_required:
            score = score_solution(plaintext, words)
            best_solutions.append((key_str, plaintext, words, score))
            print(f"\n*** FOUND {len(words)} words! ***")
            print(f"Key: {key_str}")
            print(f"Plaintext: {plaintext}")
            print(f"Words: {[w for w, p in words]}")

    print(f"\nPhase 2 complete: {attempts} total attempts")

    print()
    print("="*80)
    print("PHASE 3: Varying BOTH position groups together")
    print("="*80)

    # This is 8^9 = 134M combinations - too many
    # Use reduced set for combined search
    reduced_letters = COMMON_LETTERS[:5]  # ETAOI
    print(f"Trying top {len(reduced_letters)} letters for all 9 positions...")
    print(f"Total combinations: {len(reduced_letters)**9}")

    all_positions = [0, 1, 2, 3, 4, 25, 26, 27, 28]

    for combo in itertools.product(reduced_letters, repeat=9):
        key = list(BASE_KEY)
        for i, pos in enumerate(all_positions):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(K4, key_str)
        words = find_words(plaintext)

        attempts += 1

        if len(words) >= min_words_required:
            score = score_solution(plaintext, words)
            best_solutions.append((key_str, plaintext, words, score))
            print(f"\n*** FOUND {len(words)} words! ***")
            print(f"Key: {key_str}")
            print(f"Plaintext: {plaintext}")
            print(f"Words: {[w for w, p in words]}")

        if attempts % 500000 == 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {attempts} attempts, {elapsed:.1f}s elapsed, {len(best_solutions)} solutions found")

    print(f"\nPhase 3 complete: {attempts} total attempts")

    print()
    print("="*80)
    print("PHASE 4: Full alphabet search for positions 0-4 only")
    print("="*80)

    # This is 26^5 = 11.8M - let's do it
    print(f"Trying all 26 letters for each of positions 0-4...")
    print(f"Total combinations: {26**5}")

    phase4_attempts = 0
    for combo in itertools.product(ALL_LETTERS, repeat=5):
        key = list(BASE_KEY)
        for i, pos in enumerate(positions_0_4):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(K4, key_str)
        words = find_words(plaintext)

        phase4_attempts += 1
        attempts += 1

        if len(words) >= min_words_required:
            score = score_solution(plaintext, words)
            # Check if we already have this solution
            if key_str not in [s[0] for s in best_solutions]:
                best_solutions.append((key_str, plaintext, words, score))
                print(f"\n*** FOUND {len(words)} words! ***")
                print(f"Key: {key_str}")
                print(f"Plaintext: {plaintext}")
                print(f"Words: {[(w, p) for w, p in words]}")

        if phase4_attempts % 1000000 == 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {phase4_attempts}/11881376 ({phase4_attempts*100/11881376:.1f}%), {elapsed:.1f}s, {len(best_solutions)} solutions")

    print(f"\nPhase 4 complete: {phase4_attempts} attempts")

    print()
    print("="*80)
    print("PHASE 5: Full alphabet search for positions 25-28 only")
    print("="*80)

    print(f"Trying all 26 letters for each of positions 25-28...")
    print(f"Total combinations: {26**4}")

    phase5_attempts = 0
    for combo in itertools.product(ALL_LETTERS, repeat=4):
        key = list(BASE_KEY)
        for i, pos in enumerate(positions_25_28):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(K4, key_str)
        words = find_words(plaintext)

        phase5_attempts += 1
        attempts += 1

        if len(words) >= min_words_required:
            score = score_solution(plaintext, words)
            if key_str not in [s[0] for s in best_solutions]:
                best_solutions.append((key_str, plaintext, words, score))
                print(f"\n*** FOUND {len(words)} words! ***")
                print(f"Key: {key_str}")
                print(f"Plaintext: {plaintext}")
                print(f"Words: {[(w, p) for w, p in words]}")

        if phase5_attempts % 100000 == 0:
            elapsed = time.time() - start_time
            print(f"  Progress: {phase5_attempts}/456976 ({phase5_attempts*100/456976:.1f}%), {elapsed:.1f}s")

    print(f"\nPhase 5 complete: {phase5_attempts} attempts")

    # Final summary
    elapsed = time.time() - start_time

    print()
    print("="*80)
    print("FINAL RESULTS")
    print("="*80)
    print(f"Total attempts: {attempts}")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"Solutions with {min_words_required}+ words: {len(best_solutions)}")
    print()

    if best_solutions:
        # Sort by score
        best_solutions.sort(key=lambda x: -x[3])

        print("TOP 20 SOLUTIONS BY SCORE:")
        print("-"*80)
        for i, (key, plaintext, words, score) in enumerate(best_solutions[:20]):
            print(f"\n{i+1}. Score: {score}")
            print(f"   Key: {key}")
            print(f"   Plaintext: {plaintext}")
            print(f"   Words ({len(words)}): {[f'{w}@{p}' for w, p in words]}")
    else:
        print("No solutions found with 5+ words.")
        print("\nBest solutions from exploration (4+ words):")
        # Show best 4-word solutions that are different from base

if __name__ == "__main__":
    main()
