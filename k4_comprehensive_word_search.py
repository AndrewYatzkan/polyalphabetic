#!/usr/bin/env python3
"""
K4 Comprehensive Word Search

Try MANY starting words and look for additional word patterns throughout the plaintext.
Also try words at position 83 (where ABOVE was found).
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# The known key constraints from BERLINCLOCK at position 63
BERLINCLOCK_KEY = {
    5: 'E', 6: 'L', 7: 'Y', 8: 'O', 9: 'I', 10: 'E',
    11: 'C', 12: 'B', 13: 'A', 14: 'Q', 15: 'K'
}

# NORTHEAST at position 16 gives us key positions (16 mod 29) to (24 mod 29) = 16 to 24
NORTHEAST_KEY = {
    16: 'V', 17: 'A', 18: 'A', 19: 'T', 20: 'C',
    21: 'R', 22: 'D', 23: 'U', 24: 'M'
}

def derive_key_char(ct_char, pt_char, alpha=KRYPTOS_ALPHA):
    """Derive key character: key = ct - pt mod 26"""
    ct_pos = alpha.index(ct_char)
    pt_pos = alpha.index(pt_char)
    key_val = (ct_pos - pt_pos) % len(alpha)
    return alpha[key_val]

def decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Decrypt: pt = ct - key mod 26"""
    ct_pos = alpha.index(ct_char)
    key_pos = alpha.index(key_char)
    pt_pos = (ct_pos - key_pos) % len(alpha)
    return alpha[pt_pos]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt full ciphertext with key"""
    return ''.join(decrypt_char(c, key[i % len(key)], alpha) for i, c in enumerate(ct))

# Expanded word list (3-7 letters)
ENGLISH_WORDS = set([
    # 3-letter words (very common)
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE',
    'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'NOW', 'HIM', 'HOW', 'MAN', 'NEW', 'WAY', 'DAY',
    'TWO', 'USE', 'SET', 'END', 'SEE', 'SAY', 'SHE', 'OWN', 'OLD', 'WHO', 'WHY', 'TRY',
    'DIG', 'DUG', 'MAP', 'KEY', 'SIX', 'TEN', 'RUN', 'SIT', 'LET', 'PUT', 'TOP', 'GET',
    'GOT', 'ASK', 'BOX', 'SUN', 'SKY', 'SEA', 'AIR', 'BAR', 'BIT', 'ODD', 'AGO', 'ERA',
    'FEW', 'FAR', 'LOW', 'BAD', 'BIG', 'CUT', 'LAY', 'LED', 'LIE', 'MET', 'NOR', 'OFF',
    'RAW', 'RED', 'ROW', 'RUB', 'TAP', 'TIE', 'WET', 'WON', 'YET', 'ADD',
    # 4-letter words
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
    # 5-letter words
    'ABOUT', 'AFTER', 'AGAIN', 'BELOW', 'BIRTH', 'BLOCK', 'BREAD', 'BREAK', 'BRING',
    'BUILD', 'CLOCK', 'CLOSE', 'COULD', 'DEPTH', 'EARTH', 'FIELD', 'FIRST', 'FOUND',
    'GIVEN', 'GOING', 'GREAT', 'GROUP', 'HEART', 'HOUSE', 'KNOWN', 'LARGE', 'LAYER',
    'LEARN', 'LEVEL', 'LIGHT', 'LOCAL', 'MAYBE', 'MONEY', 'NIGHT', 'NORTH', 'OTHER',
    'PEACE', 'PLACE', 'POINT', 'POWER', 'PRESS', 'QUITE', 'RIGHT', 'SHALL', 'SINCE',
    'SMALL', 'SOUND', 'SOUTH', 'SPEAK', 'SPENT', 'STAND', 'START', 'STATE', 'STILL',
    'STORY', 'STUDY', 'TAKEN', 'TERMS', 'THEIR', 'THERE', 'THESE', 'THING', 'THINK',
    'THREE', 'TODAY', 'TRUTH', 'UNTIL', 'USING', 'VALUE', 'VOICE', 'WATCH', 'WATER',
    'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE', 'WORLD', 'WOULD', 'WRITE', 'YEARS',
    'YOUNG', 'UNDER', 'ABOVE', 'CROSS', 'GRAVE', 'STONE', 'METER', 'STEPS', 'MILES',
    'SIGHT', 'ENTRY', 'ANGLE', 'EXACT', 'COVER', 'CLOAK', 'CRYPT', 'VAULT', 'SPACE',
    'FINAL', 'INNER', 'OUTER', 'LOWER', 'UPPER', 'DIGIT', 'HANDS', 'HOURS', 'FORTH',
    'HENCE', 'TOWER', 'EIGHT', 'SEVEN', 'SIXTY', 'FIFTY', 'FORTY', 'THIRD', 'SIXTH',
    'TENTH', 'GUIDE', 'TRAIL', 'ROUTE', 'TRACK', 'ROUND', 'ARROW', 'CURVE', 'SLOPE',
    'POINT', 'MARKS', 'SPOTS', 'LINES', 'HOLES', 'DOORS', 'WALLS', 'GATES', 'ROADS',
    'FLOOR', 'ROOMS', 'SHAFT', 'LAYER', 'LEVEL', 'DEPTH', 'WIDTH', 'LENTH', 'HIGHT',
    # 6-letter words
    'BURIED', 'HIDDEN', 'SECRET', 'LOCATE', 'CENTER', 'CORNER', 'INSIDE', 'GROUND',
    'METERS', 'STAIRS', 'BEHIND', 'BESIDE', 'ACROSS', 'AROUND', 'TOWARD', 'WITHIN',
    'BEFORE', 'DURING', 'TWENTY', 'THIRTY', 'ELEVEN', 'TWELVE', 'DEGREE', 'MINUTE',
    'SECOND', 'SHADOW', 'DEEPER', 'HIGHER', 'SEARCH', 'FOLLOW', 'DIRECT', 'ONWARD',
    'UPWARD', 'INWARD', 'OUTWAY', 'TUNNEL', 'CELLAR', 'MARKER', 'SIGNAL', 'CIPHER',
    # 7+ letter words
    'BETWEEN', 'THROUGH', 'BECAUSE', 'HOWEVER', 'ANOTHER', 'AGAINST', 'ALREADY',
    'FURTHER', 'WITHOUT', 'BENEATH', 'EXACTLY', 'FIFTEEN', 'SIXTEEN', 'SEVENTY',
    'HUNDRED', 'DEGREES', 'MINUTES', 'SECONDS', 'HEADING', 'BEARING', 'COMPASS',
    'LOCATION', 'POSITION', 'DIRECTLY', 'TREASURE', 'ENTRANCE', 'DISTANCE',
    # Direction/navigation words
    'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
    # Berlin related
    'BERLIN', 'BERLINCLOCK', 'CLOCK', 'WALL', 'GATE',
])

# Much larger word list for starting positions
FIVE_LETTER_WORDS = [
    'ABOUT', 'ABOVE', 'ADMIT', 'ADOPT', 'AFTER', 'AGAIN', 'AGENT', 'AGREE', 'AHEAD',
    'ALARM', 'ALBUM', 'ALERT', 'ALIEN', 'ALIGN', 'ALIKE', 'ALIVE', 'ALLEY', 'ALLOW',
    'ALONE', 'ALONG', 'ALTER', 'AMONG', 'ANGEL', 'ANGER', 'ANGLE', 'ANGRY', 'ANKLE',
    'APART', 'APPLE', 'APPLY', 'ARENA', 'ARGUE', 'ARISE', 'ARROW', 'ASIDE', 'ASSET',
    'AVOID', 'AWARD', 'AWARE', 'AWFUL', 'BASIC', 'BASIS', 'BEACH', 'BEGAN', 'BEGIN',
    'BEING', 'BELOW', 'BENCH', 'BIRTH', 'BLACK', 'BLAME', 'BLANK', 'BLAST', 'BLEND',
    'BLIND', 'BLOCK', 'BLOOD', 'BOARD', 'BONUS', 'BOOTH', 'BOUND', 'BRAIN', 'BRAND',
    'BRAVE', 'BREAD', 'BREAK', 'BREED', 'BRICK', 'BRIDE', 'BRIEF', 'BRING', 'BROAD',
    'BROKE', 'BROWN', 'BUILD', 'BUILT', 'BUNCH', 'BURST', 'BUYER', 'CABLE', 'CABIN',
    'CACHE', 'CHAIN', 'CHAIR', 'CHAOS', 'CHARM', 'CHART', 'CHASE', 'CHEAP', 'CHECK',
    'CHEST', 'CHIEF', 'CHILD', 'CHINA', 'CHOSE', 'CHUNK', 'CLAIM', 'CLASS', 'CLEAN',
    'CLEAR', 'CLERK', 'CLICK', 'CLIFF', 'CLIMB', 'CLOCK', 'CLONE', 'CLOSE', 'CLOUD',
    'COACH', 'COAST', 'COULD', 'COUNT', 'COURT', 'COVER', 'CRACK', 'CRAFT', 'CRASH',
    'CRAZY', 'CREAM', 'CRIME', 'CROSS', 'CROWD', 'CROWN', 'CRUEL', 'CRUSH', 'CRYPT',
    'CURVE', 'CYCLE', 'DAILY', 'DANCE', 'DEALT', 'DEATH', 'DEBUT', 'DECAY', 'DELAY',
    'DEPTH', 'DIGIT', 'DIRTY', 'DOING', 'DOUBT', 'DOZEN', 'DRAFT', 'DRAIN', 'DRAMA',
    'DRANK', 'DRAWN', 'DREAM', 'DRESS', 'DRIED', 'DRIFT', 'DRILL', 'DRINK', 'DRIVE',
    'DROVE', 'DYING', 'EAGER', 'EARLY', 'EARTH', 'EATEN', 'EIGHT', 'ELDER', 'ELECT',
    'EMPTY', 'ENEMY', 'ENJOY', 'ENTER', 'ENTRY', 'EQUAL', 'ERROR', 'ESSAY', 'EVENT',
    'EVERY', 'EXACT', 'EXIST', 'EXTRA', 'FAITH', 'FALSE', 'FANCY', 'FATAL', 'FAULT',
    'FAVOR', 'FEAST', 'FEVER', 'FIELD', 'FIFTY', 'FIGHT', 'FINAL', 'FIRST', 'FIXED',
    'FLAME', 'FLASH', 'FLESH', 'FLOAT', 'FLOOD', 'FLOOR', 'FLOUR', 'FLUID', 'FLUSH',
    'FOCUS', 'FORCE', 'FORTH', 'FORTY', 'FORUM', 'FOUND', 'FRAME', 'FRANK', 'FRAUD',
    'FRESH', 'FRONT', 'FROST', 'FRUIT', 'FULLY', 'FUNNY', 'GIANT', 'GIVEN', 'GLASS',
    'GLOBE', 'GLORY', 'GOING', 'GRACE', 'GRADE', 'GRAIN', 'GRAND', 'GRANT', 'GRAPH',
    'GRASP', 'GRASS', 'GRAVE', 'GREAT', 'GREEN', 'GREET', 'GRIEF', 'GRILL', 'GROSS',
    'GROUP', 'GROVE', 'GROWN', 'GUARD', 'GUESS', 'GUEST', 'GUIDE', 'GUILD', 'GUILT',
    'HANDS', 'HAPPY', 'HARSH', 'HASTE', 'HAVEN', 'HEART', 'HEAVY', 'HENCE', 'HORSE',
    'HOTEL', 'HOURS', 'HOUSE', 'HUMAN', 'IDEAL', 'IMAGE', 'INDEX', 'INNER', 'INPUT',
    'ISSUE', 'JOINT', 'JONES', 'JUDGE', 'JUICE', 'KNOWN', 'LABEL', 'LABOR', 'LACKS',
    'LARGE', 'LASER', 'LATER', 'LAUGH', 'LAYER', 'LEADS', 'LEARN', 'LEASE', 'LEAST',
    'LEAVE', 'LEGAL', 'LEMON', 'LEVEL', 'LEVER', 'LIGHT', 'LIMIT', 'LINKS', 'LIONS',
    'LISTS', 'LIVER', 'LIVES', 'LOCAL', 'LOCKS', 'LODGE', 'LOGIC', 'LOOSE', 'LORDS',
    'LOSES', 'LOVED', 'LOVER', 'LOWER', 'LOYAL', 'LUCKY', 'LUNCH', 'LYING', 'MAGIC',
    'MAJOR', 'MAKER', 'MANOR', 'MARCH', 'MARKS', 'MARRY', 'MARSH', 'MATCH', 'MAYBE',
    'MAYOR', 'MEANS', 'MEANT', 'MEDAL', 'MEDIA', 'MERCY', 'MERGE', 'MERIT', 'MERRY',
    'METAL', 'METER', 'MIDST', 'MIGHT', 'MILES', 'MINOR', 'MINUS', 'MIXED', 'MODEL',
    'MONEY', 'MONTH', 'MORAL', 'MOTOR', 'MOUNT', 'MOUSE', 'MOUTH', 'MOVED', 'MOVIE',
    'MUSIC', 'NAMED', 'NAMES', 'NAVAL', 'NEEDS', 'NERVE', 'NEVER', 'NEWLY', 'NIGHT',
    'NINTH', 'NOBLE', 'NODES', 'NOISE', 'NORTH', 'NOTED', 'NOTES', 'NOVEL', 'NURSE',
    'OCCUR', 'OCEAN', 'OFFER', 'OFTEN', 'ORDER', 'OTHER', 'OUGHT', 'OUTER', 'OWNED',
    'OWNER', 'OXIDE', 'OZONE', 'PAINT', 'PANEL', 'PANIC', 'PAPER', 'PARTY', 'PATCH',
    'PAUSE', 'PEACE', 'PEARL', 'PENNY', 'PHASE', 'PHONE', 'PHOTO', 'PIANO', 'PICKS',
    'PIECE', 'PILOT', 'PITCH', 'PIZZA', 'PLACE', 'PLAIN', 'PLANE', 'PLANS', 'PLANT',
    'PLATE', 'PLAZA', 'PLAYS', 'PLAZA', 'PLEAD', 'PLOTS', 'POINT', 'POKED', 'POLAR',
    'POLLS', 'POOLS', 'PORTS', 'POSED', 'POSTS', 'POUND', 'POWER', 'PRESS', 'PRICE',
    'PRIDE', 'PRIME', 'PRINT', 'PRIOR', 'PRIZE', 'PROBE', 'PROOF', 'PROUD', 'PROVE',
    'PROXY', 'PULSE', 'PUPIL', 'QUEEN', 'QUERY', 'QUEST', 'QUEUE', 'QUICK', 'QUIET',
    'QUITE', 'QUOTE', 'RADAR', 'RADIO', 'RAILS', 'RAISE', 'RANCH', 'RANGE', 'RANKS',
    'RAPID', 'RATIO', 'REACH', 'REACT', 'READS', 'READY', 'REALM', 'REBEL', 'REFER',
    'REIGN', 'RELAX', 'RELAY', 'REPLY', 'RESET', 'RIGHT', 'RIGID', 'RINGS', 'RISES',
    'RISKS', 'RIVAL', 'RIVER', 'ROADS', 'ROCKS', 'ROLES', 'ROMAN', 'ROOMS', 'ROOTS',
    'ROSES', 'ROUGH', 'ROUND', 'ROUTE', 'ROYAL', 'RUGBY', 'RULER', 'RULES', 'RURAL',
    'SADLY', 'SAINT', 'SALAD', 'SALES', 'SALON', 'SAVED', 'SCALE', 'SCENE', 'SCOPE',
    'SCORE', 'SCOUT', 'SCREW', 'SEATS', 'SEEDS', 'SEIZE', 'SENSE', 'SERVE', 'SETUP',
    'SEVEN', 'SHADE', 'SHAFT', 'SHAKE', 'SHALL', 'SHAME', 'SHAPE', 'SHARE', 'SHARP',
    'SHEET', 'SHELF', 'SHELL', 'SHIFT', 'SHINE', 'SHIPS', 'SHIRT', 'SHOCK', 'SHOES',
    'SHOOK', 'SHOOT', 'SHORE', 'SHORT', 'SHOTS', 'SHOWN', 'SHOWS', 'SIDES', 'SIGHT',
    'SIGNS', 'SILLY', 'SINCE', 'SITES', 'SIXTH', 'SIXTY', 'SIZED', 'SIZES', 'SKILL',
    'SLAVE', 'SLEEP', 'SLIDE', 'SLOPE', 'SLOTS', 'SMALL', 'SMART', 'SMELL', 'SMILE',
    'SMITH', 'SMOKE', 'SOLAR', 'SOLID', 'SOLVE', 'SONGS', 'SORRY', 'SORTS', 'SOULS',
    'SOUND', 'SOUTH', 'SPACE', 'SPARE', 'SPARK', 'SPEAK', 'SPEAR', 'SPEED', 'SPELL',
    'SPEND', 'SPENT', 'SPILL', 'SPINE', 'SPLIT', 'SPOKE', 'SPORT', 'SPOTS', 'SPRAY',
    'STAFF', 'STAGE', 'STAKE', 'STAMP', 'STAND', 'STARE', 'START', 'STATE', 'STAYS',
    'STEAK', 'STEAL', 'STEAM', 'STEEL', 'STEEP', 'STEER', 'STEMS', 'STEPS', 'STICK',
    'STILL', 'STOCK', 'STONE', 'STOOD', 'STOPS', 'STORE', 'STORM', 'STORY', 'STRAP',
    'STRAW', 'STRIP', 'STUCK', 'STUDY', 'STUFF', 'STYLE', 'SUGAR', 'SUITE', 'SUPER',
    'SURGE', 'SWEET', 'SWEPT', 'SWIFT', 'SWING', 'SWORD', 'TABLE', 'TAKEN', 'TAKES',
    'TALES', 'TALKS', 'TANKS', 'TASTE', 'TAXES', 'TEACH', 'TEAMS', 'TEARS', 'TEENS',
    'TEETH', 'TELLS', 'TEMPO', 'TENDS', 'TENTH', 'TERMS', 'TESTS', 'TEXTS', 'THANK',
    'THEME', 'THICK', 'THIEF', 'THING', 'THINK', 'THIRD', 'THOSE', 'THREE', 'THREW',
    'THROW', 'THUMB', 'TIGHT', 'TIMER', 'TIMES', 'TIRED', 'TITLE', 'TODAY', 'TOKEN',
    'TONES', 'TOOLS', 'TOOTH', 'TOPIC', 'TOTAL', 'TOUCH', 'TOUGH', 'TOURS', 'TOWER',
    'TOWNS', 'TRACE', 'TRACK', 'TRADE', 'TRAIL', 'TRAIN', 'TRAIT', 'TRASH', 'TREAT',
    'TREES', 'TREND', 'TRIAL', 'TRIBE', 'TRICK', 'TRIED', 'TRIES', 'TROOP', 'TRUCK',
    'TRULY', 'TRUNK', 'TRUST', 'TRUTH', 'TUBES', 'TUMOR', 'TUNES', 'TURNS', 'TWICE',
    'TWINS', 'TWIST', 'TYPED', 'TYPES', 'UNCLE', 'UNDER', 'UNION', 'UNITE', 'UNITS',
    'UNITY', 'UNTIL', 'UPPER', 'UPSET', 'URBAN', 'URGED', 'USAGE', 'USERS', 'USING',
    'USUAL', 'VAGUE', 'VALID', 'VALUE', 'VALVE', 'VAULT', 'VEGAS', 'VENUE', 'VERSE',
    'VIDEO', 'VIEWS', 'VIRUS', 'VISIT', 'VITAL', 'VOCAL', 'VOICE', 'VOTED', 'VOTER',
    'WAGES', 'WAGON', 'WAIST', 'WALLS', 'WANTS', 'WASTE', 'WATCH', 'WATER', 'WAVES',
    'WEIRD', 'WELLS', 'WELSH', 'WHEEL', 'WHERE', 'WHICH', 'WHILE', 'WHITE', 'WHOLE',
    'WHOSE', 'WIDER', 'WIDTH', 'WINDS', 'WINGS', 'WIRES', 'WITCH', 'WIVES', 'WOMAN',
    'WOMEN', 'WOODS', 'WORDS', 'WORKS', 'WORLD', 'WORRY', 'WORSE', 'WORST', 'WORTH',
    'WOULD', 'WOUND', 'WRIST', 'WRITE', 'WRONG', 'WROTE', 'YARDS', 'YEARS', 'YIELD',
    'YOUNG', 'YOURS', 'YOUTH', 'ZONES',
]

def find_all_words(text, min_len=3):
    """Find all English words in text, including overlapping"""
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
    """Find English words in text, preferring longer ones"""
    found = find_all_words(text, min_len)
    # Sort by length (longest first), then position
    found.sort(key=lambda x: (-len(x[0]), x[1]))

    result = []
    used = set()
    for word, pos in found:
        # Check if any position is already used
        word_positions = set(range(pos, pos + len(word)))
        if not word_positions & used:
            result.append((word, pos))
            used.update(word_positions)
    return sorted(result, key=lambda x: x[1])

def test_starting_word(word, period=29):
    """Test a starting word and return results"""
    # Build key with fixed positions from BERLINCLOCK (5-15) and NORTHEAST (16-24)
    key = ['?'] * period

    # Fill in from BERLINCLOCK at position 63
    for pos, char in BERLINCLOCK_KEY.items():
        key[pos] = char

    # Fill in from NORTHEAST at position 16
    for pos, char in NORTHEAST_KEY.items():
        key[pos] = char

    # Derive key for starting word at positions 0-len(word)
    for i, pt_char in enumerate(word):
        if i < len(K4):
            ct_char = K4[i]
            key_char = derive_key_char(ct_char, pt_char)
            key[i % period] = key_char

    # Decrypt with partial key (using 'K' for unknowns)
    test_key = ''.join(c if c != '?' else 'K' for c in key)
    plaintext = vigenere_decrypt(K4, test_key)

    # Check BERLINCLOCK at position 63
    has_berlinclock = plaintext[63:74] == 'BERLINCLOCK'

    # Check NORTHEAST at position 16
    has_northeast = plaintext[16:25] == 'NORTHEAST'

    # Find words
    words_found = find_non_overlapping_words(plaintext, min_len=3)

    return {
        'word': word,
        'key': test_key,
        'plaintext': plaintext,
        'has_berlinclock': has_berlinclock,
        'has_northeast': has_northeast,
        'words_found': words_found,
        'word_count': len(words_found),
        'unknown_positions': [i for i, c in enumerate(key) if c == '?']
    }

print("="*80)
print("K4 COMPREHENSIVE WORD SEARCH")
print("="*80)
print(f"Testing {len(FIVE_LETTER_WORDS)} five-letter words at position 0")
print(f"Period: 29")
print()

# Test all starting words
results = []
for word in FIVE_LETTER_WORDS:
    result = test_starting_word(word)
    results.append(result)

# Sort by number of words found (must have both cribs)
results_with_cribs = [r for r in results if r['has_berlinclock'] and r['has_northeast']]
results_with_cribs.sort(key=lambda x: (-x['word_count'], x['word']))

print(f"Found {len(results_with_cribs)} words that maintain both cribs\n")

# Show top 50 results
print("="*80)
print("TOP 50 RESULTS (sorted by word count, with both cribs)")
print("="*80)

for i, r in enumerate(results_with_cribs[:50]):
    print(f"\n{i+1}. {r['word']} -> {r['word_count']} words: {[w for w, p in r['words_found']]}")
    print(f"   Plaintext: {r['plaintext']}")
    # Highlight word positions
    positions = [(w, p) for w, p in r['words_found'] if w not in ['NORTHEAST', 'BERLINCLOCK', r['word']]]
    if positions:
        print(f"   Additional words: {positions}")

# Focus on results with 4+ words
print("\n" + "="*80)
print("RESULTS WITH 4+ WORDS (detailed)")
print("="*80)

for r in results_with_cribs:
    if r['word_count'] >= 4:
        print(f"\n{'='*70}")
        print(f"Starting word: {r['word']}")
        print(f"Key: {r['key']}")
        print(f"Plaintext: {r['plaintext']}")
        print(f"Words found ({r['word_count']}):")
        for word, pos in r['words_found']:
            print(f"  Position {pos}: {word}")
        print()
        # Show structure
        pt = r['plaintext']
        print("Structure:")
        print(f"  0-4:   {pt[0:5]}")
        print(f"  5-15:  {pt[5:16]}")
        print(f" 16-24:  {pt[16:25]}")
        print(f" 25-62:  {pt[25:63]}")
        print(f" 63-73:  {pt[63:74]}")
        print(f" 74-96:  {pt[74:97]}")
