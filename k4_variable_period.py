#!/usr/bin/env python3
"""
K4 Variable-Period / Split-Cipher Hypothesis Testing

Tests whether K4 uses a variable-period or split-cipher approach rather than
a single period-29 Vigenere cipher.

Hypotheses tested:
1. Split period: first half uses one period, second half uses another
2. Interrupted key: key restarts at certain positions
3. Multiple keyword segments
4. Period 29 with modified key + dictionary attack at positions 0 and 83
5. NORTHEAST at every possible position (with BERLINCLOCK fixed at 63)
6. Non-standard Vigenere variants (Beaufort, variant Beaufort)
"""

import itertools
import string
from collections import Counter

# ==============================================================================
# CONSTANTS
# ==============================================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHA_LEN = len(KRYPTOS_ALPHA)  # 26
K4_LEN = len(K4)  # 97

# Known cribs
BERLIN_CLOCK = "BERLINCLOCK"
BERLIN_POS = 63
NORTHEAST = "NORTHEAST"
NORTHEAST_POS = 16  # assumed

# Known period-29 key (works for cribs, gibberish elsewhere)
KNOWN_KEY_29 = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# English letter frequencies
ENG_FREQ = {
    'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
    'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
    'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.10, 'R': 6.0,
    'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
    'Y': 2.0, 'Z': 0.07
}

# Common English bigrams for scoring
COMMON_BIGRAMS = {
    'TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
    'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
    'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
    'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA',
    'RA', 'CE', 'LI', 'CH', 'LL', 'BE', 'MA', 'SI', 'OM', 'UR'
}

# Common words for scoring
COMMON_WORDS_3 = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                  'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                  'ITS', 'SAY', 'SHE', 'TWO', 'WAY', 'WHO', 'DID', 'HIM',
                  'GET', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE']

COMMON_WORDS_4 = ['THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM',
                  'THEY', 'BEEN', 'SAID', 'EACH', 'MAKE', 'LIKE', 'LONG',
                  'LOOK', 'MANY', 'SOME', 'THEM', 'THAN', 'COME', 'MADE',
                  'FIND', 'BACK', 'ONLY', 'TIME', 'VERY', 'WHEN', 'WHAT',
                  'KNOW', 'TAKE', 'WERE', 'INTO', 'JUST', 'OVER', 'SUCH',
                  'ALSO', 'EAST', 'WEST']

COMMON_WORDS_5PLUS = ['THERE', 'WOULD', 'THEIR', 'WHICH', 'ABOUT', 'OTHER',
                      'SHALL', 'AFTER', 'NEVER', 'COULD', 'EVERY', 'THESE',
                      'UNDER', 'NORTH', 'SOUTH', 'CLOCK', 'LAYER',
                      'BETWEEN', 'SLOWLY', 'DEGREE', 'BERLIN', 'SHADOW',
                      'SECRET', 'HIDDEN', 'BURIED', 'LOCATION', 'COMPASS',
                      'MINUTES', 'SECONDS', 'OBSCURE', 'ILLUSION',
                      'IQLUSION', 'PALIMPSEST', 'ABSCISSA']

ALL_COMMON_WORDS = COMMON_WORDS_3 + COMMON_WORDS_4 + COMMON_WORDS_5PLUS

# Small dictionary of 5-letter English words for hypothesis 4
FIVE_LETTER_WORDS = [
    'ABOUT', 'ABOVE', 'AFTER', 'AGAIN', 'ALONG', 'ANGRY', 'ASIDE',
    'BEGAN', 'BEGIN', 'BEING', 'BELOW', 'BLACK', 'BLOOD', 'BOARD',
    'BREAK', 'BRING', 'BROAD', 'BROWN', 'BUILD', 'CARRY', 'CATCH',
    'CAUSE', 'CHAIN', 'CHAIR', 'CHEAP', 'CHECK', 'CHIEF', 'CHILD',
    'CLAIM', 'CLASS', 'CLEAN', 'CLEAR', 'CLIMB', 'CLOCK', 'CLOSE',
    'COAST', 'COULD', 'COUNT', 'COURT', 'COVER', 'CRACK', 'CRAFT',
    'CRASH', 'CREAM', 'CRIME', 'CROSS', 'CROWD', 'DANCE', 'DEATH',
    'DEPTH', 'DIRTY', 'DOUBT', 'DRAFT', 'DRAIN', 'DRAMA', 'DRAWN',
    'DREAM', 'DRESS', 'DRINK', 'DRIVE', 'EARLY', 'EARTH', 'EIGHT',
    'ENEMY', 'ENJOY', 'ENTER', 'EQUAL', 'ERROR', 'EVENT', 'EVERY',
    'EXACT', 'EXIST', 'EXTRA', 'FAITH', 'FALSE', 'FAULT', 'FENCE',
    'FEWER', 'FIELD', 'FIFTH', 'FIFTY', 'FIGHT', 'FINAL', 'FIRST',
    'FIXED', 'FLAME', 'FLASH', 'FLEET', 'FLESH', 'FLOAT', 'FLOOD',
    'FLOOR', 'FORCE', 'FORTH', 'FOUND', 'FRAME', 'FRESH', 'FRONT',
    'FRUIT', 'GHOST', 'GIANT', 'GIVEN', 'GLASS', 'GLOBE', 'GOING',
    'GRACE', 'GRADE', 'GRAIN', 'GRAND', 'GRANT', 'GRASS', 'GRAVE',
    'GREAT', 'GREEN', 'GRIND', 'GROSS', 'GROUP', 'GROWN', 'GUARD',
    'GUESS', 'GUIDE', 'HAPPY', 'HARRY', 'HEART', 'HEAVY', 'HENCE',
    'HORSE', 'HOTEL', 'HOUSE', 'HUMAN', 'IDEAL', 'IMAGE', 'INDEX',
    'INNER', 'INPUT', 'IRONY', 'ISSUE', 'JAMES', 'JIMMY', 'JOINT',
    'JONES', 'JUDGE', 'KNIFE', 'KNOCK', 'KNOWN', 'LABEL', 'LARGE',
    'LASER', 'LATER', 'LAUGH', 'LAYER', 'LEARN', 'LEAST', 'LEAVE',
    'LEGAL', 'LEVEL', 'LIGHT', 'LIMIT', 'LIVES', 'LOCAL', 'LOOSE',
    'LOVER', 'LOWER', 'LUCKY', 'LUNCH', 'MAGIC', 'MAJOR', 'MARCH',
    'MATCH', 'MAYBE', 'MAYOR', 'MEANT', 'MEDIA', 'METAL', 'MIGHT',
    'MINOR', 'MINUS', 'MODEL', 'MONEY', 'MONTH', 'MORAL', 'MOTOR',
    'MOUNT', 'MOUSE', 'MOUTH', 'MOVED', 'MOVIE', 'MUSIC', 'NEEDS',
    'NERVE', 'NEVER', 'NEWLY', 'NIGHT', 'NOISE', 'NORTH', 'NOTED',
    'NOVEL', 'NURSE', 'OCCUR', 'OCEAN', 'OFFER', 'OFTEN', 'ORDER',
    'OTHER', 'OUGHT', 'OUTER', 'OWNER', 'PAINT', 'PANEL', 'PAPER',
    'PARTY', 'PATCH', 'PAUSE', 'PEACE', 'PENNY', 'PHASE', 'PHONE',
    'PHOTO', 'PIANO', 'PIECE', 'PILOT', 'PITCH', 'PLACE', 'PLAIN',
    'PLANE', 'PLANT', 'PLATE', 'PLAZA', 'PLEAD', 'POINT', 'POUND',
    'POWER', 'PRESS', 'PRICE', 'PRIDE', 'PRIME', 'PRINT', 'PRIOR',
    'PRIZE', 'PROOF', 'PROUD', 'PROVE', 'QUEEN', 'QUEST', 'QUICK',
    'QUIET', 'QUITE', 'QUOTE', 'RADIO', 'RAISE', 'RANGE', 'RAPID',
    'RATIO', 'REACH', 'READY', 'REALM', 'REIGN', 'RELAX', 'RIDER',
    'RIDGE', 'RIFLE', 'RIGHT', 'RIGID', 'RISEN', 'RISKY', 'RIVER',
    'ROBIN', 'ROBOT', 'ROCKY', 'ROGER', 'ROMAN', 'ROUGH', 'ROUND',
    'ROUTE', 'ROYAL', 'RULER', 'RURAL', 'SAINT', 'SALAD', 'SCALE',
    'SCENE', 'SCOPE', 'SCORE', 'SENSE', 'SERVE', 'SEVEN', 'SHALL',
    'SHAPE', 'SHARE', 'SHARK', 'SHARP', 'SHEEP', 'SHEER', 'SHEET',
    'SHELF', 'SHELL', 'SHIFT', 'SHINE', 'SHIRT', 'SHOCK', 'SHOOT',
    'SHORT', 'SHOWN', 'SIGHT', 'SINCE', 'SIXTH', 'SIXTY', 'SIZED',
    'SKILL', 'SLEEP', 'SLIDE', 'SMALL', 'SMART', 'SMELL', 'SMILE',
    'SMOKE', 'SOLAR', 'SOLID', 'SOLVE', 'SORRY', 'SOUND', 'SOUTH',
    'SPACE', 'SPARE', 'SPEAK', 'SPEED', 'SPEND', 'SPENT', 'SPLIT',
    'SPOKE', 'SPORT', 'SPRAY', 'SQUAD', 'STACK', 'STAFF', 'STAGE',
    'STAIN', 'STAKE', 'STAND', 'STARE', 'START', 'STATE', 'STAYS',
    'STEAM', 'STEEL', 'STEEP', 'STERN', 'STICK', 'STILL', 'STOCK',
    'STONE', 'STOOD', 'STORE', 'STORM', 'STORY', 'STRIP', 'STUCK',
    'STUDY', 'STUFF', 'STYLE', 'SUGAR', 'SUITE', 'SUPER', 'SWEAR',
    'SWEET', 'SWEPT', 'SWING', 'SWORD', 'TABLE', 'TASTE', 'TEACH',
    'TEETH', 'THANK', 'THEME', 'THERE', 'THICK', 'THING', 'THINK',
    'THIRD', 'THOSE', 'THREE', 'THREW', 'THROW', 'TIGHT', 'TIRED',
    'TITLE', 'TODAY', 'TOKEN', 'TOTAL', 'TOUCH', 'TOUGH', 'TOWER',
    'TRACE', 'TRACK', 'TRADE', 'TRAIL', 'TRAIN', 'TRAIT', 'TREAT',
    'TREND', 'TRIAL', 'TRIBE', 'TRICK', 'TRIED', 'TROOP', 'TRUCK',
    'TRULY', 'TRUST', 'TRUTH', 'TWICE', 'UNDER', 'UNION', 'UNITY',
    'UNTIL', 'UPPER', 'UPSET', 'URBAN', 'USAGE', 'USUAL', 'VALID',
    'VALUE', 'VIDEO', 'VIRUS', 'VISIT', 'VITAL', 'VOCAL', 'VOICE',
    'VOTER', 'WAGON', 'WASTE', 'WATCH', 'WATER', 'WEIGH', 'WHEEL',
    'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE', 'WHOSE', 'WOMAN',
    'WOMEN', 'WORLD', 'WORRY', 'WORSE', 'WORST', 'WORTH', 'WOULD',
    'WOUND', 'WRITE', 'WRONG', 'WROTE', 'YIELD', 'YOUNG', 'YOUTH',
    # KRYPTOS-specific words
    'DIGBY', 'LAYER', 'SHADE', 'LIGHT', 'POINT', 'EARTH', 'CLOCK',
    'SHADOW', 'ANGLE', 'FIELD', 'STONE', 'WATER',
]

# ==============================================================================
# CIPHER FUNCTIONS
# ==============================================================================

def kryptos_index(c):
    """Get index of character in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA.index(c)

def kryptos_char(i):
    """Get character at index in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA[i % ALPHA_LEN]

def decrypt_standard(ct_char, key_char):
    """Standard Vigenere: PT = (CT - KEY) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(ct_char) - kryptos_index(key_char))

def decrypt_beaufort(ct_char, key_char):
    """Beaufort: PT = (KEY - CT) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(key_char) - kryptos_index(ct_char))

def decrypt_variant(ct_char, key_char):
    """Variant Beaufort: PT = (CT + KEY) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(ct_char) + kryptos_index(key_char))

def encrypt_standard(pt_char, key_char):
    """Standard Vigenere encrypt: CT = (PT + KEY) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(pt_char) + kryptos_index(key_char))

def derive_key_char(ct_char, pt_char):
    """Derive key character: KEY = (CT - PT) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(ct_char) - kryptos_index(pt_char))

def derive_key_char_beaufort(ct_char, pt_char):
    """Derive key for Beaufort: KEY = (CT + PT) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(ct_char) + kryptos_index(pt_char))

def derive_key_char_variant(ct_char, pt_char):
    """Derive key for variant: KEY = (PT - CT) mod 26 in KRYPTOS alphabet."""
    return kryptos_char(kryptos_index(pt_char) - kryptos_index(ct_char))

def decrypt_string(ct, key, decrypt_func=decrypt_standard):
    """Decrypt ciphertext string with repeating key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        if k == '?':
            result.append('?')
        else:
            result.append(decrypt_func(c, k))
    return ''.join(result)

def decrypt_string_positional(ct, key_map, decrypt_func=decrypt_standard):
    """Decrypt using a position-to-key-char mapping (dict)."""
    result = []
    for i, c in enumerate(ct):
        if i in key_map:
            result.append(decrypt_func(c, key_map[i]))
        else:
            result.append('?')
    return ''.join(result)

# ==============================================================================
# SCORING FUNCTIONS
# ==============================================================================

def score_english(text):
    """
    Score text for English-likeness. Higher = more English-like.
    Works on partial text (ignores '?' characters).
    """
    # Filter out unknowns
    known = [c for c in text if c != '?']
    if len(known) < 5:
        return -1000.0

    score = 0.0
    n = len(known)
    known_str = ''.join(known)

    # 1. Letter frequency chi-squared (lower is better, so we negate)
    freq = Counter(known)
    chi2 = 0.0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(letter, 0) / n * 100.0
        expected = ENG_FREQ.get(letter, 0.5)
        chi2 += (observed - expected) ** 2 / max(expected, 0.01)
    score -= chi2 * 0.3

    # 2. Bigram frequency bonus
    bigram_count = 0
    for i in range(len(known_str) - 1):
        bg = known_str[i:i+2]
        if bg in COMMON_BIGRAMS:
            bigram_count += 1
    if n > 1:
        score += bigram_count / (n - 1) * 100.0

    # 3. Common word bonus
    for word in ALL_COMMON_WORDS:
        if word in known_str:
            score += len(word) * 3.0

    # 4. Penalize rare letters heavily
    for c in known:
        if c in 'JXQZ':
            score -= 3.0

    # 5. Consonant cluster penalty (more than 4 consonants in a row)
    vowels = set('AEIOU')
    consonant_run = 0
    for c in known_str:
        if c not in vowels:
            consonant_run += 1
            if consonant_run > 4:
                score -= 2.0
        else:
            consonant_run = 0

    return score

def score_english_quick(text):
    """Quick score - just letter frequency and bigrams, no word search."""
    known = [c for c in text if c != '?']
    if len(known) < 3:
        return -1000.0

    n = len(known)
    known_str = ''.join(known)
    score = 0.0

    # Letter frequency
    freq = Counter(known)
    chi2 = 0.0
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(letter, 0) / n * 100.0
        expected = ENG_FREQ.get(letter, 0.5)
        chi2 += (observed - expected) ** 2 / max(expected, 0.01)
    score -= chi2 * 0.3

    # Bigrams
    bigram_count = 0
    for i in range(len(known_str) - 1):
        bg = known_str[i:i+2]
        if bg in COMMON_BIGRAMS:
            bigram_count += 1
    if n > 1:
        score += bigram_count / (n - 1) * 80.0

    return score

# ==============================================================================
# HYPOTHESIS 1: SPLIT PERIOD
# ==============================================================================

def test_split_period():
    """
    Test if K4 uses different periods for different segments.
    Try split points at every position 20-80.
    For each split, try period combinations (5-35) for each half.
    Constraint: NORTHEAST@16 constrains first half, BERLINCLOCK@63 constrains second.
    """
    print("=" * 78)
    print("HYPOTHESIS 1: SPLIT PERIOD")
    print("=" * 78)
    print("Testing if K4 uses different Vigenere periods for different segments.")
    print(f"K4 length: {K4_LEN}")
    print(f"NORTHEAST@{NORTHEAST_POS} constrains the segment containing positions 16-24")
    print(f"BERLINCLOCK@{BERLIN_POS} constrains the segment containing positions 63-73")
    print()

    results = []

    for split in range(20, 81):
        # First half: positions 0..split-1
        # Second half: positions split..96

        # NORTHEAST at 16-24 must be in the first half (if split > 24)
        # BERLINCLOCK at 63-73 must be in the second half (if split <= 63)
        ne_in_first = (split > 24)
        bc_in_second = (split <= 63)

        if not ne_in_first or not bc_in_second:
            continue  # Skip if cribs cross the split boundary

        first_half_ct = K4[:split]
        second_half_ct = K4[split:]

        for p1 in range(5, 36):
            # Derive key for first half from NORTHEAST@16
            key1 = ['?'] * p1
            valid_p1 = True
            for j, pt_char in enumerate(NORTHEAST):
                pos = NORTHEAST_POS + j
                if pos >= split:
                    valid_p1 = False
                    break
                key_pos = pos % p1
                derived = derive_key_char(K4[pos], pt_char)
                if key1[key_pos] == '?':
                    key1[key_pos] = derived
                elif key1[key_pos] != derived:
                    valid_p1 = False
                    break

            if not valid_p1:
                continue

            for p2 in range(5, 36):
                # Derive key for second half from BERLINCLOCK@63
                key2 = ['?'] * p2
                valid_p2 = True
                for j, pt_char in enumerate(BERLIN_CLOCK):
                    pos = BERLIN_POS + j
                    if pos < split:
                        valid_p2 = False
                        break
                    # Position within the second half
                    pos_in_half = pos - split
                    key_pos = pos_in_half % p2
                    derived = derive_key_char(K4[pos], pt_char)
                    if key2[key_pos] == '?':
                        key2[key_pos] = derived
                    elif key2[key_pos] != derived:
                        valid_p2 = False
                        break

                if not valid_p2:
                    continue

                # Decrypt what we can
                pt_parts = []
                for i in range(K4_LEN):
                    if i < split:
                        k = key1[i % p1]
                    else:
                        k = key2[(i - split) % p2]

                    if k != '?':
                        pt_parts.append(decrypt_standard(K4[i], k))
                    else:
                        pt_parts.append('?')

                pt = ''.join(pt_parts)

                # Count known characters
                known_count = sum(1 for c in pt if c != '?')

                # Score the known parts
                s = score_english(pt)

                # Also check that cribs are correctly placed
                ne_check = pt[NORTHEAST_POS:NORTHEAST_POS + len(NORTHEAST)]
                bc_check = pt[BERLIN_POS:BERLIN_POS + len(BERLIN_CLOCK)]

                if NORTHEAST in ne_check and BERLIN_CLOCK in bc_check:
                    results.append((s, split, p1, p2,
                                    ''.join(key1), ''.join(key2),
                                    pt, known_count))

    results.sort(key=lambda x: -x[0])

    print(f"Found {len(results)} valid split-period configurations.")
    print("\nTop 10 results:")
    print("-" * 78)
    for i, (s, split, p1, p2, k1, k2, pt, known) in enumerate(results[:10]):
        print(f"\n  #{i+1}: Split@{split}, Period1={p1}, Period2={p2}, "
              f"Score={s:.1f}, Known={known}/{K4_LEN}")
        print(f"  Key1: {k1}")
        print(f"  Key2: {k2}")
        print(f"  PT:   {pt}")
        # Show just the non-crib decoded parts
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    print()
    return results

# ==============================================================================
# HYPOTHESIS 2: INTERRUPTED KEY
# ==============================================================================

def test_interrupted_key():
    """
    Test if the key restarts at certain positions.
    Try various restart points.
    """
    print("=" * 78)
    print("HYPOTHESIS 2: INTERRUPTED KEY")
    print("=" * 78)
    print("Testing if the Vigenere key restarts at certain positions.")
    print()

    # Try different restart positions
    restart_sets = [
        [0, 16, 63],        # Start, NORTHEAST, BERLINCLOCK
        [0, 16, 25, 63],    # + end of NORTHEAST
        [0, 16, 25, 63, 74],  # + end of BERLINCLOCK
        [0, 5, 16, 25, 63, 74, 83],  # Various points
        [0, 25, 63],        # After NORTHEAST, BERLINCLOCK
        [0, 29, 58, 87],    # Every 29 positions
        [0, 29, 58],        # Every 29
        [0, 32, 64],        # Thirds
        [0, 48],            # Halves
        [0, 16, 48, 63],    # Quarters-ish around cribs
    ]

    results = []

    for restarts in restart_sets:
        # For each restart set, try various periods
        for period in range(5, 36):
            # Build key map: for each position, determine which key char it uses
            # Key restarts at each restart point
            key = ['?'] * period

            # Derive key constraints from NORTHEAST@16
            valid = True
            for j, pt_char in enumerate(NORTHEAST):
                pos = NORTHEAST_POS + j
                # Find which restart segment this position belongs to
                seg_start = max(r for r in restarts if r <= pos)
                pos_in_seg = pos - seg_start
                key_pos = pos_in_seg % period
                derived = derive_key_char(K4[pos], pt_char)
                if key[key_pos] == '?':
                    key[key_pos] = derived
                elif key[key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Derive key constraints from BERLINCLOCK@63
            for j, pt_char in enumerate(BERLIN_CLOCK):
                pos = BERLIN_POS + j
                seg_start = max(r for r in restarts if r <= pos)
                pos_in_seg = pos - seg_start
                key_pos = pos_in_seg % period
                derived = derive_key_char(K4[pos], pt_char)
                if key[key_pos] == '?':
                    key[key_pos] = derived
                elif key[key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Decrypt with the derived key + restart points
            pt_chars = []
            for i in range(K4_LEN):
                seg_start = max(r for r in restarts if r <= i)
                pos_in_seg = i - seg_start
                key_pos = pos_in_seg % period
                k = key[key_pos]
                if k != '?':
                    pt_chars.append(decrypt_standard(K4[i], k))
                else:
                    pt_chars.append('?')

            pt = ''.join(pt_chars)
            known_count = sum(1 for c in pt if c != '?')
            s = score_english(pt)

            results.append((s, restarts, period, ''.join(key), pt, known_count))

    results.sort(key=lambda x: -x[0])

    print(f"Found {len(results)} valid interrupted-key configurations.")
    print("\nTop 10 results:")
    print("-" * 78)
    for i, (s, restarts, period, key_str, pt, known) in enumerate(results[:10]):
        print(f"\n  #{i+1}: Restarts={restarts}, Period={period}, "
              f"Score={s:.1f}, Known={known}/{K4_LEN}")
        print(f"  Key: {key_str}")
        print(f"  PT:  {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    print()
    return results

# ==============================================================================
# HYPOTHESIS 3: MULTIPLE KEYWORD SEGMENTS
# ==============================================================================

def test_multiple_keyword_segments():
    """
    Test if K4 uses different keyword segments for chunks of text.
    E.g., first 29 use one key, next 29 another, last 39 a third.
    """
    print("=" * 78)
    print("HYPOTHESIS 3: MULTIPLE KEYWORD SEGMENTS")
    print("=" * 78)
    print("Testing if K4 uses different keywords for different chunks.")
    print()

    # Try different segment boundaries
    segment_configs = [
        # (segment_boundaries, description)
        ([0, 29, 58], "Three segments: 29+29+39"),
        ([0, 29, 58, 87], "Four segments: 29+29+29+10"),
        ([0, 25, 63], "Three segments: split at crib boundaries"),
        ([0, 16, 25, 63, 74], "Five segments: between and around cribs"),
        ([0, 32, 64], "Three equal-ish segments"),
        ([0, 48], "Two halves: 48+49"),
        ([0, 16, 63], "Three segments: at crib starts"),
        ([0, 25, 74], "Three segments: at crib ends"),
        ([0, 24, 48, 72], "Four quarters"),
        ([0, 19, 38, 57, 76], "Five segments of ~19"),
    ]

    results = []

    for boundaries, desc in segment_configs:
        # For each segment configuration, try various periods for each segment
        # For efficiency, limit period range to 5-20 per segment
        n_segs = len(boundaries)

        # For each segment, derive what we can from the cribs
        for period in range(3, 30):
            # Use same period for all segments but different key starting points
            # (effectively a different key per segment)
            seg_keys = [['?'] * period for _ in range(n_segs)]

            valid = True

            # Derive from NORTHEAST@16
            for j, pt_char in enumerate(NORTHEAST):
                pos = NORTHEAST_POS + j
                # Which segment?
                seg_idx = 0
                for si in range(len(boundaries)):
                    if boundaries[si] <= pos:
                        seg_idx = si
                pos_in_seg = pos - boundaries[seg_idx]
                key_pos = pos_in_seg % period
                derived = derive_key_char(K4[pos], pt_char)
                if seg_keys[seg_idx][key_pos] == '?':
                    seg_keys[seg_idx][key_pos] = derived
                elif seg_keys[seg_idx][key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Derive from BERLINCLOCK@63
            for j, pt_char in enumerate(BERLIN_CLOCK):
                pos = BERLIN_POS + j
                seg_idx = 0
                for si in range(len(boundaries)):
                    if boundaries[si] <= pos:
                        seg_idx = si
                pos_in_seg = pos - boundaries[seg_idx]
                key_pos = pos_in_seg % period
                derived = derive_key_char(K4[pos], pt_char)
                if seg_keys[seg_idx][key_pos] == '?':
                    seg_keys[seg_idx][key_pos] = derived
                elif seg_keys[seg_idx][key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Decrypt
            pt_chars = []
            for i in range(K4_LEN):
                seg_idx = 0
                for si in range(len(boundaries)):
                    if boundaries[si] <= i:
                        seg_idx = si
                pos_in_seg = i - boundaries[seg_idx]
                key_pos = pos_in_seg % period
                k = seg_keys[seg_idx][key_pos]
                if k != '?':
                    pt_chars.append(decrypt_standard(K4[i], k))
                else:
                    pt_chars.append('?')

            pt = ''.join(pt_chars)
            known_count = sum(1 for c in pt if c != '?')
            s = score_english(pt)

            key_strs = [''.join(sk) for sk in seg_keys]
            results.append((s, desc, boundaries, period, key_strs, pt, known_count))

    results.sort(key=lambda x: -x[0])

    print(f"Found {len(results)} valid multi-segment configurations.")
    print("\nTop 10 results:")
    print("-" * 78)
    for i, (s, desc, bounds, period, key_strs, pt, known) in enumerate(results[:10]):
        print(f"\n  #{i+1}: {desc}, Period={period}, "
              f"Score={s:.1f}, Known={known}/{K4_LEN}")
        print(f"  Boundaries: {bounds}")
        for si, ks in enumerate(key_strs):
            print(f"  Key[{si}]: {ks}")
        print(f"  PT: {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    print()
    return results

# ==============================================================================
# HYPOTHESIS 4: PERIOD 29 WITH DICTIONARY ATTACK AT UNKNOWN POSITIONS
# ==============================================================================

def test_period29_dictionary():
    """
    Period 29 key has 5 unknown positions (0-4) and possibly 25-28.
    Key: DIJJQELYOIECBAQKVAATCRDUMPABT (29 chars)
    Known: positions 5-24 from cribs.
    Unknown: positions 0-4 (and maybe 25-28 if those aren't right).

    Try all 5-letter dictionary words at position 0 and position 83 of plaintext.
    """
    print("=" * 78)
    print("HYPOTHESIS 4: PERIOD 29 WITH DICTIONARY ATTACK")
    print("=" * 78)
    print(f"Known key: {KNOWN_KEY_29}")
    print(f"Testing dictionary words at position 0 (affects key[0-4])")
    print(f"and position 83 (affects key positions that overlap with 83-87)")
    print()

    period = 29

    # The known key from just the two cribs:
    base_key = list('?' * 29)

    # From NORTHEAST@16
    for j, pt_char in enumerate(NORTHEAST):
        pos = NORTHEAST_POS + j
        key_pos = pos % period
        base_key[key_pos] = derive_key_char(K4[pos], pt_char)

    # From BERLINCLOCK@63
    for j, pt_char in enumerate(BERLIN_CLOCK):
        pos = BERLIN_POS + j
        key_pos = pos % period
        base_key[key_pos] = derive_key_char(K4[pos], pt_char)

    known_key_str = ''.join(base_key)
    unknown_positions = [i for i, k in enumerate(base_key) if k == '?']
    print(f"Key from cribs only: {known_key_str}")
    print(f"Unknown key positions: {unknown_positions}")

    # APPROACH 4A: Try dictionary words starting at plaintext position 0
    print("\n--- Approach 4A: 5-letter words at plaintext position 0 ---")

    results_4a = []
    for word in FIVE_LETTER_WORDS:
        test_key = list(base_key)
        valid = True
        for j, pt_char in enumerate(word):
            pos = j  # plaintext position
            key_pos = pos % period
            derived = derive_key_char(K4[pos], pt_char)
            if test_key[key_pos] == '?':
                test_key[key_pos] = derived
            elif test_key[key_pos] != derived:
                valid = False
                break

        if not valid:
            continue

        # Decrypt what we can
        pt = decrypt_string(K4, test_key)
        known_count = sum(1 for c in pt if c != '?')
        s = score_english(pt)

        results_4a.append((s, word, ''.join(test_key), pt, known_count))

    results_4a.sort(key=lambda x: -x[0])

    print(f"Found {len(results_4a)} valid configurations.")
    print("\nTop 10:")
    for i, (s, word, key_str, pt, known) in enumerate(results_4a[:10]):
        print(f"\n  #{i+1}: Word@0='{word}', Score={s:.1f}, Known={known}/{K4_LEN}")
        print(f"  Key: {key_str}")
        print(f"  PT:  {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']
                       and w != word]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    # APPROACH 4B: Try dictionary words starting at plaintext position 83
    # Position 83 mod 29 = 83 - 2*29 = 83 - 58 = 25
    # So positions 83-87 -> key positions 25, 26, 27, 28, 0
    print("\n--- Approach 4B: 5-letter words at plaintext position 83 ---")

    results_4b = []
    for word in FIVE_LETTER_WORDS:
        test_key = list(base_key)
        valid = True
        for j, pt_char in enumerate(word):
            pos = 83 + j
            if pos >= K4_LEN:
                break
            key_pos = pos % period
            derived = derive_key_char(K4[pos], pt_char)
            if test_key[key_pos] == '?':
                test_key[key_pos] = derived
            elif test_key[key_pos] != derived:
                valid = False
                break

        if not valid:
            continue

        pt = decrypt_string(K4, test_key)
        known_count = sum(1 for c in pt if c != '?')
        s = score_english(pt)

        results_4b.append((s, word, ''.join(test_key), pt, known_count))

    results_4b.sort(key=lambda x: -x[0])

    print(f"Found {len(results_4b)} valid configurations.")
    print("\nTop 10:")
    for i, (s, word, key_str, pt, known) in enumerate(results_4b[:10]):
        print(f"\n  #{i+1}: Word@83='{word}', Score={s:.1f}, Known={known}/{K4_LEN}")
        print(f"  Key: {key_str}")
        print(f"  PT:  {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']
                       and w != word]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    # APPROACH 4C: Try words at BOTH position 0 and position 83
    print("\n--- Approach 4C: Words at BOTH position 0 AND position 83 ---")

    results_4c = []
    for word0 in FIVE_LETTER_WORDS:
        test_key_0 = list(base_key)
        valid0 = True
        for j, pt_char in enumerate(word0):
            pos = j
            key_pos = pos % period
            derived = derive_key_char(K4[pos], pt_char)
            if test_key_0[key_pos] == '?':
                test_key_0[key_pos] = derived
            elif test_key_0[key_pos] != derived:
                valid0 = False
                break

        if not valid0:
            continue

        for word83 in FIVE_LETTER_WORDS:
            test_key = list(test_key_0)
            valid83 = True
            for j, pt_char in enumerate(word83):
                pos = 83 + j
                if pos >= K4_LEN:
                    break
                key_pos = pos % period
                derived = derive_key_char(K4[pos], pt_char)
                if test_key[key_pos] == '?':
                    test_key[key_pos] = derived
                elif test_key[key_pos] != derived:
                    valid83 = False
                    break

            if not valid83:
                continue

            # Check if all unknown positions are now filled
            still_unknown = sum(1 for k in test_key if k == '?')

            pt = decrypt_string(K4, test_key)
            known_count = sum(1 for c in pt if c != '?')
            s = score_english(pt)

            results_4c.append((s, word0, word83, ''.join(test_key), pt,
                               known_count, still_unknown))

    results_4c.sort(key=lambda x: -x[0])

    print(f"Found {len(results_4c)} valid dual-word configurations.")
    print("\nTop 10:")
    for i, (s, w0, w83, key_str, pt, known, unk) in enumerate(results_4c[:10]):
        print(f"\n  #{i+1}: Word@0='{w0}', Word@83='{w83}', "
              f"Score={s:.1f}, Known={known}/{K4_LEN}, UnkKeyPos={unk}")
        print(f"  Key: {key_str}")
        print(f"  PT:  {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']
                       and w != w0 and w != w83]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    print()
    return results_4a, results_4b, results_4c

# ==============================================================================
# HYPOTHESIS 5: NORTHEAST AT EVERY POSSIBLE POSITION
# ==============================================================================

def test_northeast_all_positions():
    """
    BERLINCLOCK@63 is confirmed. But NORTHEAST position is assumed.
    Test NORTHEAST at every possible position 0-88 with period 29.
    For each valid position, derive the complete key, decrypt, and rank.
    """
    print("=" * 78)
    print("HYPOTHESIS 5: NORTHEAST AT EVERY POSSIBLE POSITION (Period 29)")
    print("=" * 78)
    print(f"BERLINCLOCK is CONFIRMED at position {BERLIN_POS}.")
    print(f"Testing NORTHEAST at every position 0-{K4_LEN - len(NORTHEAST)}.")
    print()

    period = 29
    results = []

    for ne_pos in range(0, K4_LEN - len(NORTHEAST) + 1):
        key = ['?'] * period

        # Derive from BERLINCLOCK@63 (always)
        valid = True
        for j, pt_char in enumerate(BERLIN_CLOCK):
            pos = BERLIN_POS + j
            key_pos = pos % period
            derived = derive_key_char(K4[pos], pt_char)
            if key[key_pos] == '?':
                key[key_pos] = derived
            elif key[key_pos] != derived:
                valid = False
                break

        if not valid:
            # This should always be valid since BERLINCLOCK constraints are consistent
            continue

        # Derive from NORTHEAST@ne_pos
        for j, pt_char in enumerate(NORTHEAST):
            pos = ne_pos + j
            if pos >= K4_LEN:
                valid = False
                break
            key_pos = pos % period
            derived = derive_key_char(K4[pos], pt_char)
            if key[key_pos] == '?':
                key[key_pos] = derived
            elif key[key_pos] != derived:
                valid = False
                break

        if not valid:
            continue

        # Now try to fill remaining unknown positions with best-frequency chars
        # First, decrypt with partial key
        key_str = ''.join(key)
        unknown_positions = [i for i, k in enumerate(key) if k == '?']

        # For each unknown key position, find the best letter by frequency
        for ukp in unknown_positions:
            ct_positions = [i for i in range(K4_LEN) if i % period == ukp]
            best_score = -1000
            best_char = 'A'
            for test_char in KRYPTOS_ALPHA:
                pts = [decrypt_standard(K4[i], test_char) for i in ct_positions]
                freq_score = sum(ENG_FREQ.get(c, 0) for c in pts)
                if freq_score > best_score:
                    best_score = freq_score
                    best_char = test_char
            key[ukp] = best_char

        # Decrypt fully
        full_key = ''.join(key)
        pt = decrypt_string(K4, key)

        # Verify cribs
        ne_check = pt[ne_pos:ne_pos + len(NORTHEAST)]
        bc_check = pt[BERLIN_POS:BERLIN_POS + len(BERLIN_CLOCK)]

        s = score_english(pt)

        results.append((s, ne_pos, full_key, key_str, pt,
                         len(unknown_positions), ne_check, bc_check))

    results.sort(key=lambda x: -x[0])

    print(f"Found {len(results)} valid NORTHEAST positions with period 29.")
    print("\nTop 10 results:")
    print("-" * 78)
    for i, (s, ne_pos, full_key, partial_key, pt, n_unk,
            ne_check, bc_check) in enumerate(results[:10]):
        print(f"\n  #{i+1}: NORTHEAST@{ne_pos}, Score={s:.1f}, "
              f"UnkKeyPos={n_unk}")
        print(f"  Partial key (from cribs): {partial_key}")
        print(f"  Full key (freq-filled):   {full_key}")
        print(f"  PT: {pt}")
        print(f"  NE check: '{ne_check}', BC check: '{bc_check}'")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']]
        if extra_words:
            print(f"  Extra words found: {extra_words}")

    # Also show all valid positions for reference
    print("\n\nAll valid NORTHEAST positions (sorted by position):")
    print("-" * 78)
    by_pos = sorted(results, key=lambda x: x[1])
    for s, ne_pos, full_key, partial_key, pt, n_unk, ne_check, bc_check in by_pos:
        # Count known key positions
        known_key = sum(1 for c in partial_key if c != '?')
        print(f"  NE@{ne_pos:2d}: key_known={known_key}/29, "
              f"score={s:7.1f}, partial_key={partial_key}")

    print()
    return results

# ==============================================================================
# HYPOTHESIS 6: NON-STANDARD VIGENERE VARIANTS
# ==============================================================================

def test_nonstandard_vigenere():
    """
    Test different decryption formulas:
    - Standard: PT = (CT - KEY) mod 26
    - Beaufort: PT = (KEY - CT) mod 26
    - Variant:  PT = (CT + KEY) mod 26
    All with KRYPTOS alphabet mapping.
    """
    print("=" * 78)
    print("HYPOTHESIS 6: NON-STANDARD VIGENERE VARIANTS")
    print("=" * 78)
    print("Testing Beaufort and Variant Beaufort with KRYPTOS alphabet.")
    print()

    period = 29

    variants = [
        ("Standard", decrypt_standard, derive_key_char),
        ("Beaufort", decrypt_beaufort, derive_key_char_beaufort),
        ("Variant",  decrypt_variant,  derive_key_char_variant),
    ]

    all_results = []

    for variant_name, dec_func, key_func in variants:
        print(f"\n--- {variant_name} Vigenere ---")

        # Test with BERLINCLOCK@63 and NORTHEAST@16
        # For each NE position 0-88
        results = []

        for ne_pos in range(0, K4_LEN - len(NORTHEAST) + 1):
            key = ['?'] * period

            valid = True

            # Derive from BERLINCLOCK@63
            for j, pt_char in enumerate(BERLIN_CLOCK):
                pos = BERLIN_POS + j
                key_pos = pos % period
                derived = key_func(K4[pos], pt_char)
                if key[key_pos] == '?':
                    key[key_pos] = derived
                elif key[key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Derive from NORTHEAST@ne_pos
            for j, pt_char in enumerate(NORTHEAST):
                pos = ne_pos + j
                if pos >= K4_LEN:
                    valid = False
                    break
                key_pos = pos % period
                derived = key_func(K4[pos], pt_char)
                if key[key_pos] == '?':
                    key[key_pos] = derived
                elif key[key_pos] != derived:
                    valid = False
                    break

            if not valid:
                continue

            # Fill unknowns with frequency analysis
            for ukp in range(period):
                if key[ukp] != '?':
                    continue
                ct_positions = [i for i in range(K4_LEN) if i % period == ukp]
                best_score = -1000
                best_char = 'A'
                for test_char in KRYPTOS_ALPHA:
                    pts = [dec_func(K4[i], test_char) for i in ct_positions]
                    freq_score = sum(ENG_FREQ.get(c, 0) for c in pts)
                    if freq_score > best_score:
                        best_score = freq_score
                        best_char = test_char
                key[ukp] = best_char

            pt = ''.join(dec_func(K4[i], key[i % period]) for i in range(K4_LEN))
            s = score_english(pt)

            results.append((s, ne_pos, ''.join(key), pt, variant_name))

        results.sort(key=lambda x: -x[0])

        print(f"  Valid NE positions: {len(results)}")
        print(f"  Top 10:")
        for i, (s, ne_pos, key_str, pt, vn) in enumerate(results[:10]):
            print(f"    #{i+1}: NE@{ne_pos}, Score={s:.1f}, Key={key_str}")
            print(f"    PT: {pt}")
            extra_words = [w for w in ALL_COMMON_WORDS
                           if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                     'BERLINCLOCK', 'EAST', 'NORTH']]
            if extra_words:
                print(f"    Extra words: {extra_words}")

        all_results.extend(results)

    # Overall best across all variants
    all_results.sort(key=lambda x: -x[0])

    print("\n\nOverall Top 10 across ALL variants:")
    print("-" * 78)
    for i, (s, ne_pos, key_str, pt, vn) in enumerate(all_results[:10]):
        print(f"\n  #{i+1}: {vn}, NE@{ne_pos}, Score={s:.1f}")
        print(f"  Key: {key_str}")
        print(f"  PT:  {pt}")
        extra_words = [w for w in ALL_COMMON_WORDS
                       if w in pt and w not in ['NORTHEAST', 'BERLIN', 'CLOCK',
                                                 'BERLINCLOCK', 'EAST', 'NORTH']]
        if extra_words:
            print(f"  Extra words: {extra_words}")

    print()
    return all_results

# ==============================================================================
# SUMMARY AND CROSS-ANALYSIS
# ==============================================================================

def print_summary(r1, r2, r3, r4a, r4b, r4c, r5, r6):
    """Print summary comparison across all hypotheses."""
    print("=" * 78)
    print("SUMMARY: CROSS-HYPOTHESIS COMPARISON")
    print("=" * 78)

    hypotheses = [
        ("H1: Split Period", r1),
        ("H2: Interrupted Key", r2),
        ("H3: Multiple Segments", r3),
        ("H4a: Dict@0", r4a),
        ("H4b: Dict@83", r4b),
        ("H4c: Dict@0+83", r4c),
        ("H5: NE All Positions", r5),
        ("H6: Non-std Vigenere", r6),
    ]

    print(f"\n{'Hypothesis':<30} {'Best Score':>10} {'# Valid':>8} {'Best Config':<30}")
    print("-" * 78)
    for name, results in hypotheses:
        if results:
            best_score = results[0][0]
            n = len(results)
            # Extract a short config description
            if name.startswith("H1"):
                _, _, split, p1, p2, _, _, _, _ = results[0] if len(results[0]) == 9 else (*results[0], None)
                config = f"split@{results[0][1]}, p={results[0][2]}/{results[0][3]}"
            elif name.startswith("H2"):
                config = f"restarts={results[0][1]}, p={results[0][2]}"
            elif name.startswith("H3"):
                config = f"{results[0][1][:25]}, p={results[0][3]}"
            elif name.startswith("H4a"):
                config = f"word@0='{results[0][1]}'"
            elif name.startswith("H4b"):
                config = f"word@83='{results[0][1]}'"
            elif name.startswith("H4c"):
                config = f"'{results[0][1]}'@0 + '{results[0][2]}'@83"
            elif name.startswith("H5"):
                config = f"NE@{results[0][1]}"
            elif name.startswith("H6"):
                config = f"{results[0][4]}, NE@{results[0][1]}"
            else:
                config = "?"
            print(f"  {name:<28} {best_score:>10.1f} {n:>8} {config:<30}")
        else:
            print(f"  {name:<28} {'N/A':>10} {0:>8} {'No valid results':<30}")

    # Show the absolute best across all
    all_best = []
    for name, results in hypotheses:
        if results:
            all_best.append((results[0][0], name, results[0]))

    all_best.sort(key=lambda x: -x[0])

    print("\n\nAbsolute Best Result:")
    print("-" * 78)
    if all_best:
        score, name, result = all_best[0]
        print(f"  Hypothesis: {name}")
        print(f"  Score: {score:.1f}")
        # Find plaintext in the result tuple (it's always a string near the end)
        for item in result:
            if isinstance(item, str) and len(item) == K4_LEN:
                print(f"  PT: {item}")
                break

    # Key insight analysis
    print("\n\nKey Insights:")
    print("-" * 78)

    # Check if any non-standard Vigenere beats standard
    std_best = -1000
    nonstd_best = -1000
    for s, ne_pos, key_str, pt, vn in r6:
        if vn == "Standard":
            std_best = max(std_best, s)
        else:
            nonstd_best = max(nonstd_best, s)

    if nonstd_best > std_best:
        print("  [!] Non-standard Vigenere outperforms standard - worth investigating")
    else:
        print("  [.] Standard Vigenere scores best among variants")

    # Check if any split/interrupted approach beats single period
    single_best = max((r[0] for r in r5), default=-1000)
    split_best = max((r[0] for r in r1), default=-1000)
    int_best = max((r[0] for r in r2), default=-1000)
    seg_best = max((r[0] for r in r3), default=-1000)

    if split_best > single_best:
        print("  [!] Split period outperforms single period - variable period likely")
    else:
        print("  [.] Single period scores as well or better than split period")

    if int_best > single_best:
        print("  [!] Interrupted key outperforms single period")
    else:
        print("  [.] Interrupted key does not outperform single period")

    if seg_best > single_best:
        print("  [!] Multiple segments outperform single period")
    else:
        print("  [.] Multiple segments do not outperform single period")

    # Check dictionary results
    dict_best = max(
        max((r[0] for r in r4a), default=-1000),
        max((r[0] for r in r4b), default=-1000),
        max((r[0] for r in r4c), default=-1000),
    )
    if dict_best > single_best:
        print("  [!] Dictionary attack found better result than frequency-only")
    else:
        print("  [.] Dictionary attack does not improve over frequency analysis")

    # Check if NE@16 is actually the best position
    ne16_results = [r for r in r5 if r[1] == 16]
    if ne16_results:
        ne16_score = ne16_results[0][0]
        best_ne_score = r5[0][0] if r5 else -1000
        best_ne_pos = r5[0][1] if r5 else -1
        if best_ne_pos != 16:
            print(f"  [!] NORTHEAST@{best_ne_pos} (score={best_ne_score:.1f}) beats "
                  f"NORTHEAST@16 (score={ne16_score:.1f})")
        else:
            print(f"  [.] NORTHEAST@16 is the best or tied for best position")


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("*" * 78)
    print("K4 VARIABLE-PERIOD / SPLIT-CIPHER HYPOTHESIS TESTING")
    print("*" * 78)
    print(f"\nK4 ciphertext ({K4_LEN} chars): {K4}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Known cribs: BERLINCLOCK@{BERLIN_POS} (confirmed), NORTHEAST@{NORTHEAST_POS} (assumed)")
    print(f"Known period-29 key: {KNOWN_KEY_29}")
    print()

    # Verify basics
    print("Verification - decrypt BERLINCLOCK with known key:")
    for j, pt_char in enumerate(BERLIN_CLOCK):
        pos = BERLIN_POS + j
        ct_char = K4[pos]
        key_char = KNOWN_KEY_29[pos % 29]
        dec = decrypt_standard(ct_char, key_char)
        print(f"  pos {pos}: CT={ct_char} KEY={key_char} -> PT={dec} (expected {pt_char})", end="")
        print(" OK" if dec == pt_char else " MISMATCH!")

    print("\nVerification - decrypt NORTHEAST with known key:")
    for j, pt_char in enumerate(NORTHEAST):
        pos = NORTHEAST_POS + j
        ct_char = K4[pos]
        key_char = KNOWN_KEY_29[pos % 29]
        dec = decrypt_standard(ct_char, key_char)
        print(f"  pos {pos}: CT={ct_char} KEY={key_char} -> PT={dec} (expected {pt_char})", end="")
        print(" OK" if dec == pt_char else " MISMATCH!")

    print("\nFull decryption with known period-29 key:")
    full_pt = decrypt_string(K4, KNOWN_KEY_29)
    print(f"  {full_pt}")
    print()

    # Run all hypothesis tests
    r1 = test_split_period()
    r2 = test_interrupted_key()
    r3 = test_multiple_keyword_segments()
    r4a, r4b, r4c = test_period29_dictionary()
    r5 = test_northeast_all_positions()
    r6 = test_nonstandard_vigenere()

    # Print summary
    print_summary(r1, r2, r3, r4a, r4b, r4c, r5, r6)

    print("\n" + "*" * 78)
    print("ANALYSIS COMPLETE")
    print("*" * 78)
