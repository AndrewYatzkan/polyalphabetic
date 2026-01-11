#!/usr/bin/env python3
"""
K4 Position 83 Search

Try different words at position 83 to find combinations that maximize English words.
Position 83 mod 29 = 25, so we need key positions 25-28 (and wrapping to 0 for longer words).
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Fixed key constraints
BERLINCLOCK_KEY = {5: 'E', 6: 'L', 7: 'Y', 8: 'O', 9: 'I', 10: 'E', 11: 'C', 12: 'B', 13: 'A', 14: 'Q', 15: 'K'}
NORTHEAST_KEY = {16: 'V', 17: 'A', 18: 'A', 19: 'T', 20: 'C', 21: 'R', 22: 'D', 23: 'U', 24: 'M'}

def derive_key_char(ct_char, pt_char, alpha=KRYPTOS_ALPHA):
    ct_pos = alpha.index(ct_char)
    pt_pos = alpha.index(pt_char)
    key_val = (ct_pos - pt_pos) % len(alpha)
    return alpha[key_val]

def decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    ct_pos = alpha.index(ct_char)
    key_pos = alpha.index(key_char)
    pt_pos = (ct_pos - key_pos) % len(alpha)
    return alpha[pt_pos]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    return ''.join(decrypt_char(c, key[i % len(key)], alpha) for i, c in enumerate(ct))

ENGLISH_WORDS = set([
    # 3-letter
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE',
    'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'NOW', 'HIM', 'HOW', 'MAN', 'NEW', 'WAY', 'DAY',
    'TWO', 'USE', 'SET', 'END', 'SEE', 'SAY', 'SHE', 'OWN', 'OLD', 'WHO', 'WHY', 'TRY',
    'DIG', 'DUG', 'MAP', 'KEY', 'SIX', 'TEN', 'RUN', 'SIT', 'LET', 'PUT', 'TOP', 'GET',
    'GOT', 'ASK', 'BOX', 'SUN', 'SKY', 'SEA', 'AIR', 'BAR', 'BIT', 'ODD', 'AGO', 'ERA',
    'FEW', 'FAR', 'LOW', 'BAD', 'BIG', 'CUT', 'LAY', 'LED', 'LIE', 'MET', 'NOR', 'OFF',
    'RAW', 'RED', 'ROW', 'RUB', 'TAP', 'TIE', 'WET', 'WON', 'YET', 'ADD', 'PER',
    # 4-letter
    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN', 'CALL',
    'FIND', 'MANY', 'THEN', 'ALSO', 'INTO', 'JUST', 'OVER', 'SUCH', 'THAN', 'THEM',
    'WELL', 'WERE', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'MADE', 'EACH', 'ONLY',
    'KNOW', 'TAKE', 'YEAR', 'WORK', 'LAST', 'HERE', 'PART', 'SAID', 'BACK', 'MAKE',
    'LOOK', 'EVEN', 'MOST', 'LIKE', 'WHAT', 'MUST', 'LONG', 'EAST', 'WEST', 'NEAR',
    'LEFT', 'SIDE', 'HIGH', 'TURN', 'HEAD', 'HAND', 'FEET', 'DOOR', 'DOWN', 'UPON',
    'ROOM', 'AREA', 'SITE', 'BURY', 'DEEP', 'HIDE', 'TRUE', 'NEXT', 'WALL', 'STEP',
    'ZERO', 'FIVE', 'FOUR', 'NINE', 'HALF', 'MARK', 'LINE', 'PASS', 'PATH', 'YARD',
    'MILE', 'INCH', 'SPOT', 'CITY', 'GATE', 'SPAN', 'OPEN', 'WIDE', 'DARK', 'FIRE',
    'LAND', 'ROCK', 'TOMB', 'GOLD', 'COAL', 'IRON', 'CLAY', 'SAND', 'SOIL', 'TREE',
    'CODE', 'CLUE', 'HINT', 'WORD', 'TEXT', 'NOTE', 'SIGN', 'NAME', 'TELL', 'READ',
    'MOVE', 'KEEP', 'HOLD', 'LEAD', 'SEEK', 'SHOW', 'GAVE', 'FORM', 'GOES', 'GONE',
    'CAME', 'FELL', 'SENT', 'TOLD', 'TOOK', 'KNEW', 'COPY', 'PAST', 'SAFE', 'LOCK',
    # 5-letter
    'ABOUT', 'AFTER', 'AGAIN', 'BELOW', 'BIRTH', 'BLOCK', 'CLOCK', 'CLOSE', 'COULD',
    'DEPTH', 'EARTH', 'EIGHT', 'FIELD', 'FIRST', 'FOUND', 'GIVEN', 'GOING', 'GREAT',
    'GROUP', 'HEART', 'HOUSE', 'KNOWN', 'LARGE', 'LAYER', 'LEARN', 'LEVEL', 'LIGHT',
    'LOCAL', 'MAYBE', 'MONEY', 'NIGHT', 'NORTH', 'OTHER', 'PEACE', 'PLACE', 'POINT',
    'POWER', 'PRESS', 'QUITE', 'RIGHT', 'SHALL', 'SINCE', 'SMALL', 'SOUND', 'SOUTH',
    'SPEAK', 'SPENT', 'STAND', 'START', 'STATE', 'STILL', 'STORY', 'STUDY', 'TAKEN',
    'TERMS', 'THEIR', 'THERE', 'THESE', 'THING', 'THINK', 'THREE', 'TODAY', 'TRUTH',
    'UNDER', 'UNTIL', 'USING', 'VALUE', 'VOICE', 'WATCH', 'WATER', 'WHERE', 'WHICH',
    'WHILE', 'WHITE', 'WHOLE', 'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOUNG', 'ABOVE',
    'CROSS', 'GRAVE', 'STONE', 'METER', 'STEPS', 'MILES', 'SIGHT', 'ENTRY', 'ANGLE',
    'EXACT', 'COVER', 'CLOAK', 'CRYPT', 'VAULT', 'SPACE', 'FINAL', 'INNER', 'OUTER',
    'LOWER', 'UPPER', 'DIGIT', 'HANDS', 'HOURS', 'FORTH', 'HENCE', 'TOWER', 'SEVEN',
    'SIXTY', 'FIFTY', 'FORTY', 'THIRD', 'SIXTH', 'TENTH', 'GUIDE', 'TRAIL', 'ROUTE',
    'TRACK', 'ROUND', 'ARROW', 'CURVE', 'SLOPE', 'MARKS', 'SPOTS', 'LINES', 'HOLES',
    'DOORS', 'WALLS', 'GATES', 'ROADS', 'FLOOR', 'ROOMS', 'SHAFT', 'WIDTH', 'ARENA',
    'AHEAD', 'ALLOW', 'APART', 'BRING', 'DRAWN', 'EVERY', 'LODGE', 'MANOR', 'MINOR',
    'ROCKS', 'THEME', 'TOURS', 'USERS', 'WOMAN', 'WORDS', 'WORKS',
    # 6-letter
    'BURIED', 'HIDDEN', 'SECRET', 'LOCATE', 'CENTER', 'CORNER', 'INSIDE', 'GROUND',
    'METERS', 'STAIRS', 'BEHIND', 'BESIDE', 'ACROSS', 'AROUND', 'TOWARD', 'WITHIN',
    'BEFORE', 'DURING', 'TWENTY', 'THIRTY', 'ELEVEN', 'TWELVE', 'DEGREE', 'MINUTE',
    'SECOND', 'SHADOW', 'DEEPER', 'HIGHER', 'SEARCH', 'FOLLOW', 'DIRECT', 'ONWARD',
    'UPWARD', 'INWARD', 'TUNNEL', 'CELLAR', 'MARKER', 'SIGNAL', 'CIPHER',
    # 7+ letter
    'BETWEEN', 'THROUGH', 'BECAUSE', 'HOWEVER', 'ANOTHER', 'AGAINST', 'ALREADY',
    'FURTHER', 'WITHOUT', 'BENEATH', 'EXACTLY', 'FIFTEEN', 'SIXTEEN', 'SEVENTY',
    'HUNDRED', 'DEGREES', 'MINUTES', 'SECONDS', 'HEADING', 'BEARING', 'COMPASS',
    'LOCATION', 'POSITION', 'DIRECTLY', 'TREASURE', 'ENTRANCE', 'DISTANCE',
    # Direction words
    'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
    # Berlin
    'BERLIN', 'BERLINCLOCK', 'CLOCK', 'WALL', 'GATE',
])

WORDS_AT_83 = [
    'DIG', 'DUG', 'LET', 'WAS', 'ADD', 'ALL', 'BUT', 'FEW', 'HER', 'ONE', 'RUB', 'SAY', 'ASK',
    'ABOVE', 'UNDER', 'THEIR', 'THERE', 'THESE', 'WHERE', 'WHICH', 'AFTER', 'AGAIN', 'BEING',
    'COULD', 'EVERY', 'FIRST', 'FOUND', 'GIVEN', 'GOING', 'GREAT', 'KNOWN', 'MIGHT', 'NEVER',
    'OTHER', 'PLACE', 'POINT', 'RIGHT', 'SHALL', 'SINCE', 'SMALL', 'SOUTH', 'STAND', 'START',
    'STATE', 'STILL', 'TAKEN', 'THINK', 'THOSE', 'THREE', 'TODAY', 'UNTIL', 'WHILE', 'WHOLE',
    'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOUNG',
]

WORDS_AT_0 = [
    'ARENA', 'AHEAD', 'ALLOW', 'APART', 'BELOW', 'BRING', 'DIGIT', 'DRAWN', 'EIGHT', 'EVERY',
    'HOURS', 'LEVEL', 'LODGE', 'MANOR', 'MINOR', 'PRESS', 'ROCKS', 'THEME', 'TOURS', 'USERS',
    'WOMAN', 'WORDS', 'WORKS', 'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOURS', 'ABOUT', 'ABOVE',
    'AFTER', 'AGAIN', 'UNDER', 'FIRST', 'THERE', 'WHERE', 'COULD', 'THEIR', 'WHICH', 'SOUTH',
    'NORTH', 'EARTH', 'LAYER',
]

def find_all_words(text, min_len=3):
    found = []
    for word in ENGLISH_WORDS:
        if len(word) >= min_len:
            pos = 0
            while True:
                idx = text.find(word, pos)
                if idx == -1:
                    break
                found.append((word, idx))
                pos = idx + 1
    return sorted(set(found), key=lambda x: x[1])

def find_non_overlapping_words(text, min_len=3):
    found = find_all_words(text, min_len)
    found.sort(key=lambda x: (-len(x[0]), x[1]))
    result = []
    used = set()
    for word, pos in found:
        word_positions = set(range(pos, pos + len(word)))
        if not word_positions & used:
            result.append((word, pos))
            used.update(word_positions)
    return sorted(result, key=lambda x: x[1])

def test_words_at_both_positions(word0, word83, period=29):
    """Test starting word at 0 and word at 83"""
    key = ['?'] * period

    # Fill in from BERLINCLOCK at position 63
    for pos, char in BERLINCLOCK_KEY.items():
        key[pos] = char

    # Fill in from NORTHEAST at position 16
    for pos, char in NORTHEAST_KEY.items():
        key[pos] = char

    # Derive key for word at position 0
    for i, pt_char in enumerate(word0):
        if i < len(K4):
            ct_char = K4[i]
            key_char = derive_key_char(ct_char, pt_char)
            key[i % period] = key_char

    # Derive key for word at position 83
    for i, pt_char in enumerate(word83):
        pos = 83 + i
        if pos < len(K4):
            ct_char = K4[pos]
            key_char = derive_key_char(ct_char, pt_char)
            key_pos = pos % period
            # Check for conflict
            if key[key_pos] != '?' and key[key_pos] != key_char:
                return None  # Conflict
            key[key_pos] = key_char

    # Decrypt with partial key
    test_key = ''.join(c if c != '?' else 'K' for c in key)
    plaintext = vigenere_decrypt(K4, test_key)

    # Verify constraints
    has_berlinclock = plaintext[63:74] == 'BERLINCLOCK'
    has_northeast = plaintext[16:25] == 'NORTHEAST'
    has_word0 = plaintext[0:len(word0)] == word0
    has_word83 = plaintext[83:83+len(word83)] == word83

    if not (has_berlinclock and has_northeast and has_word0 and has_word83):
        return None

    words_found = find_non_overlapping_words(plaintext, min_len=3)

    return {
        'word0': word0,
        'word83': word83,
        'key': test_key,
        'plaintext': plaintext,
        'words_found': words_found,
        'word_count': len(words_found),
    }

print("="*80)
print("K4 TWO-POSITION WORD SEARCH")
print("="*80)
print(f"Testing combinations of words at position 0 and position 83")
print()

results = []
for word0 in WORDS_AT_0:
    for word83 in WORDS_AT_83:
        result = test_words_at_both_positions(word0, word83)
        if result:
            results.append(result)

# Sort by word count
results.sort(key=lambda x: -x['word_count'])

print(f"Found {len(results)} valid combinations\n")

# Show top results
print("="*80)
print("TOP 30 RESULTS")
print("="*80)

for i, r in enumerate(results[:30]):
    print(f"\n{i+1}. {r['word0']} + {r['word83']} -> {r['word_count']} words")
    print(f"   Words: {[w for w, p in r['words_found']]}")
    print(f"   Plaintext: {r['plaintext']}")

# Show the very best results in detail
print("\n" + "="*80)
print("BEST RESULTS WITH 6+ WORDS (detailed)")
print("="*80)

for r in results:
    if r['word_count'] >= 6:
        print(f"\n{'='*70}")
        print(f"Starting word: {r['word0']}, Position 83: {r['word83']}")
        print(f"Key: {r['key']}")
        print(f"Plaintext: {r['plaintext']}")
        print(f"Words found ({r['word_count']}):")
        for word, pos in r['words_found']:
            print(f"  Position {pos}: {word}")
        print()
        pt = r['plaintext']
        print("Structure:")
        print(f"  0-4:   {pt[0:5]} <- {r['word0']}")
        print(f"  5-15:  {pt[5:16]}")
        print(f" 16-24:  {pt[16:25]} <- NORTHEAST")
        print(f" 25-62:  {pt[25:63]}")
        print(f" 63-73:  {pt[63:74]} <- BERLINCLOCK")
        print(f" 74-82:  {pt[74:83]}")
        print(f" 83-87:  {pt[83:88]} <- {r['word83']}")
        print(f" 88-96:  {pt[88:97]}")
