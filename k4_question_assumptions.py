#!/usr/bin/env python3
"""
Question our assumptions about K4.
What if UNDER and ABOVE are not the correct words?
"""

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def decrypt(ct, key):
    pt = ""
    for i, c in enumerate(ct):
        if c not in KRYPTOS:
            pt += c
            continue
        ct_idx = KRYPTOS.index(c)
        key_idx = KRYPTOS.index(key[i % len(key)])
        pt_idx = (ct_idx - key_idx) % 26
        pt += KRYPTOS[pt_idx]
    return pt

def derive_key_segment(ciphertext, plaintext, start_pos, key_len=29):
    """Derive key segment from known plaintext at given position."""
    key_segment = {}
    for i, (ct, pt) in enumerate(zip(ciphertext, plaintext)):
        pos = (start_pos + i) % key_len
        ct_idx = KRYPTOS.index(ct)
        pt_idx = KRYPTOS.index(pt)
        key_char = KRYPTOS[(ct_idx - pt_idx) % 26]
        key_segment[pos] = key_char
    return key_segment

# We KNOW these are correct (Sanborn confirmed):
# - BERLINCLOCK at position 63
# - NORTHEAST somewhere in the plaintext

# From BERLINCLOCK at pos 63:
berlin_key = derive_key_segment(K4[63:74], "BERLINCLOCK", 63)
print("Key from BERLINCLOCK at pos 63:")
print(f"  Positions 5-15: {''.join([berlin_key[i] for i in range(5, 16)])}")

# From NORTHEAST - but where exactly?
# Let's test ALL positions where NORTHEAST could appear
print("\nTesting all possible NORTHEAST positions:")
print("(Looking for positions that don't conflict with BERLINCLOCK key)")

compatible_positions = []
for start in range(97 - 9):  # NORTHEAST is 9 chars
    ne_key = derive_key_segment(K4[start:start+9], "NORTHEAST", start)

    # Check for conflicts with BERLINCLOCK-derived key
    conflict = False
    for pos, char in ne_key.items():
        if pos in berlin_key and berlin_key[pos] != char:
            conflict = True
            break

    if not conflict:
        # Build full key and decrypt
        full_key = ['?'] * 29
        for pos, char in berlin_key.items():
            full_key[pos] = char
        for pos, char in ne_key.items():
            full_key[pos] = char

        key_str = ''.join(full_key)
        unknown_count = key_str.count('?')

        if unknown_count <= 10:  # Reasonable number of unknowns
            compatible_positions.append((start, key_str, unknown_count))
            print(f"\n  Position {start}: {unknown_count} unknowns")
            print(f"  Key: {key_str}")

            # Try to decrypt with partial key (fill ? with A for now)
            test_key = key_str.replace('?', 'K')  # K is first letter of KRYPTOS
            pt = decrypt(K4, test_key)
            print(f"  PT preview: {pt[:30]}...{pt[60:80]}...")

print(f"\n\nFound {len(compatible_positions)} compatible NORTHEAST positions")

# Now let's focus on position 16 (which we believe is correct)
# And systematically try different words at positions 0 and 83

print("\n" + "="*60)
print("TESTING DIFFERENT STARTING WORDS (keeping NORTHEAST@16, BERLINCLOCK@63)")
print("="*60)

# Base key from BERLINCLOCK and NORTHEAST at pos 16
base_key = ['?'] * 29
# From BERLINCLOCK at 63 (key pos 5-15)
for i, c in enumerate("ELYOIECBAQK"):
    base_key[5 + i] = c
# From NORTHEAST at 16 (key pos 16-24)
for i, c in enumerate("VAATCRDUM"):
    base_key[16 + i] = c

print(f"Base key (from confirmed cribs): {''.join(base_key)}")
print(f"Unknown positions: 0-4, 25-28 (9 total)")

# 5-letter words that could start the message
start_words = [
    "UNDER", "LAYER", "BELOW", "AFTER", "ALONG", "AMONG",
    "ABOUT", "ABOVE", "AHEAD", "ALONE", "ASIDE", "AWAIT",
    "BEGIN", "BEING", "BELOW", "BIRTH", "BLANK", "BLIND",
    "BLOCK", "BOARD", "BOUND", "BREAK", "BRICK", "BRING",
    "BROAD", "BRUSH", "BUILD", "BUILT", "CARRY", "CATCH",
    "CEASE", "CHAIN", "CHAIR", "CHASE", "CHECK", "CHIEF",
    "CHILD", "CLAIM", "CLASS", "CLEAN", "CLEAR", "CLIMB",
    "CLOCK", "CLOSE", "COAST", "COULD", "COUNT", "COURT",
    "COVER", "CRAFT", "CRASH", "CREAM", "CROSS", "CROWD",
    "DYING", "DEATH", "DEPTH", "DIGIT", "DOUBT", "DRAFT",
    "DRAIN", "DRAMA", "DRAWN", "DREAM", "DRESS", "DRIED",
    "DRINK", "DRIVE", "DROWN", "EARLY", "EARTH", "EIGHT",
    "EMPTY", "ENEMY", "ENJOY", "ENTER", "ENTRY", "EQUAL",
    "ERROR", "EVENT", "EVERY", "EXACT", "EXIST", "EXTRA",
    "FAITH", "FALSE", "FAULT", "FAVOR", "FEAST", "FIELD",
    "FIFTY", "FIGHT", "FINAL", "FINDS", "FIRST", "FIXED",
    "FLAME", "FLASH", "FLOOR", "FOCUS", "FORCE", "FORTH",
    "FORTY", "FOUND", "FRAME", "FRANK", "FRONT", "FRUIT",
    "GHOST", "GIANT", "GIVEN", "GLASS", "GLOBE", "GLORY",
    "GOING", "GRACE", "GRADE", "GRAIN", "GRAND", "GRANT",
    "GRASS", "GRAVE", "GREAT", "GREEN", "GROSS", "GROUP",
    "GROWN", "GUARD", "GUESS", "GUIDE", "GUILT", "HANDS",
    "HAPPY", "HEARD", "HEART", "HEAVY", "HENCE", "HENRY",
    "HOLES", "HONOR", "HORSE", "HOTEL", "HOURS", "HOUSE",
    "HUMAN", "IDEAL", "IMAGE", "INDEX", "INNER", "INPUT",
    "INTER", "ISSUE", "JESUS", "JOINT", "JONES", "JUDGE",
    "KNOWN", "LABEL", "LABOR", "LARGE", "LASER", "LATER",
    "LAUGH", "LAYER", "LEARN", "LEAST", "LEAVE", "LEGAL",
    "LEVEL", "LEWIS", "LIGHT", "LIMIT", "LINES", "LINKS",
    "LIVED", "LOCAL", "LODGE", "LOGIC", "LOOSE", "LORDS",
    "LOWER", "LUCKY", "LUNCH", "LYING", "MAGIC", "MAJOR",
    "MAKER", "MARCH", "MARIA", "MARKS", "MARRY", "MASON",
    "MATCH", "MAYBE", "MAYOR", "MEANS", "MEANT", "MEDIA",
    "METAL", "MIDST", "MIGHT", "MILES", "MINDS", "MINOR",
    "MINUS", "MIXED", "MODEL", "MONEY", "MONTH", "MORAL",
    "MOTOR", "MOUNT", "MOUSE", "MOUTH", "MOVED", "MOVIE",
    "MUSIC", "NAMED", "NEEDS", "NERVE", "NEVER", "NEWLY",
    "NIGHT", "NINTH", "NOBLE", "NOISE", "NORTH", "NOTED",
    "NOVEL", "NURSE", "OCCUR", "OCEAN", "OFFER", "OFTEN",
    "OLDER", "OLIVE", "ORDER", "OTHER", "OUGHT", "OUTER",
    "OWING", "OWNER", "PAGES", "PAINT", "PANEL", "PAPER",
    "PARTS", "PARTY", "PATCH", "PAUSE", "PEACE", "PETER",
    "PHASE", "PHONE", "PHOTO", "PIANO", "PIECE", "PILOT",
    "PITCH", "PLACE", "PLAIN", "PLANE", "PLANT", "PLATE",
    "PLAYS", "PLAZA", "POINT", "POLAR", "POOLS", "POWER",
    "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR",
    "PRIZE", "PROOF", "PROUD", "PROVE", "PROXY", "QUEEN",
    "QUERY", "QUEST", "QUEUE", "QUICK", "QUIET", "QUITE",
    "QUOTE", "RADIO", "RAISE", "RALLY", "RANCH", "RANGE",
    "RAPID", "RATIO", "REACH", "REACT", "READS", "READY",
    "REALM", "REFER", "REIGN", "RELAX", "REPLY", "RIGHT",
    "RINGS", "RISEN", "RISES", "RIVER", "ROADS", "ROBIN",
    "ROCKS", "ROMAN", "ROOMS", "ROOTS", "ROUGH", "ROUND",
    "ROUTE", "ROYAL", "RURAL", "SADLY", "SAINT", "SALES",
    "SANDY", "SCALE", "SCENE", "SCOPE", "SCORE", "SEEDS",
    "SEEMS", "SELLS", "SENSE", "SERVE", "SEVEN", "SHADE",
    "SHAKE", "SHALL", "SHAME", "SHAPE", "SHARE", "SHARP",
    "SHEEP", "SHEER", "SHEET", "SHELF", "SHELL", "SHIFT",
    "SHINE", "SHIPS", "SHIRT", "SHOCK", "SHOES", "SHOOK",
    "SHOOT", "SHOPS", "SHORE", "SHORT", "SHOTS", "SHOWN",
    "SHOWS", "SIDES", "SIGHT", "SIGNS", "SIMON", "SINCE",
    "SITES", "SIXTH", "SIXTY", "SIZED", "SKILL", "SLEEP",
    "SLIDE", "SLOPE", "SLOWS", "SMALL", "SMART", "SMELL",
    "SMILE", "SMITH", "SMOKE", "SNAKE", "SOLAR", "SOLID",
    "SOLVE", "SONGS", "SORRY", "SORTS", "SOULS", "SOUND",
    "SOUTH", "SPACE", "SPARE", "SPEAK", "SPEED", "SPELL",
    "SPEND", "SPENT", "SPIES", "SPLIT", "SPOKE", "SPORT",
    "SPOTS", "SPRAY", "SQUAD", "STAFF", "STAGE", "STAIR",
    "STAKE", "STAMP", "STAND", "STARS", "START", "STATE",
    "STAYS", "STEAM", "STEEL", "STEEP", "STEPS", "STICK",
    "STILL", "STOCK", "STONE", "STOOD", "STOPS", "STORE",
    "STORM", "STORY", "STRAP", "STRIP", "STUCK", "STUDY",
    "STUFF", "STYLE", "SUGAR", "SUITE", "SUPER", "SURGE",
    "SWEET", "SWIFT", "SWING", "SWISS", "TABLE", "TAKEN",
    "TAKES", "TALKS", "TANKS", "TASTE", "TAXES", "TEACH",
    "TEAMS", "TEETH", "TELLS", "TEMPO", "TENDS", "TERMS",
    "TESTS", "TEXAS", "TEXTS", "THANK", "THEFT", "THEIR",
    "THEME", "THERE", "THESE", "THICK", "THING", "THINK",
    "THIRD", "THOSE", "THREE", "THREW", "THROW", "THUMB",
    "TIGHT", "TIMES", "TIRED", "TITLE", "TODAY", "TOKEN",
    "TONES", "TOOLS", "TOOTH", "TOPIC", "TOTAL", "TOUCH",
    "TOUGH", "TOURS", "TOWER", "TOWNS", "TRACK", "TRACT",
    "TRADE", "TRAIL", "TRAIN", "TRAIT", "TRASH", "TREAT",
    "TREES", "TREND", "TRIAL", "TRIBE", "TRICK", "TRIED",
    "TRIES", "TRIPS", "TROOP", "TRUCK", "TRULY", "TRUNK",
    "TRUST", "TRUTH", "TWICE", "TWINS", "TYPES", "ULTRA",
    "UNCLE", "UNDER", "UNDUE", "UNION", "UNITE", "UNITS",
    "UNITY", "UNTIL", "UPPER", "URBAN", "URGED", "USAGE",
    "USERS", "USING", "USUAL", "VAGUE", "VALID", "VALUE",
    "VIDEO", "VIEWS", "VIRUS", "VISIT", "VITAL", "VIVID",
    "VOCAL", "VOICE", "VOTES", "WAGES", "WALKS", "WALLS",
    "WASTE", "WATCH", "WATER", "WAVES", "WEARY", "WEEKS",
    "WEIRD", "WELLS", "WELSH", "WHERE", "WHICH", "WHILE",
    "WHITE", "WHOLE", "WHOSE", "WIDER", "WIDTH", "WINGS",
    "WITCH", "WOMAN", "WOMEN", "WOODS", "WORDS", "WORKS",
    "WORLD", "WORRY", "WORSE", "WORST", "WORTH", "WOULD",
    "WOUND", "WRITE", "WRONG", "WROTE", "YARDS", "YEARS",
    "YIELD", "YOUNG", "YOURS", "YOUTH", "ZONES"
]

# Find words that produce readable text
results = []
for word in start_words:
    # Derive key positions 0-4 from this word at position 0
    key = list(base_key)
    for i, c in enumerate(word):
        ct_char = K4[i]
        pt_char = c
        ct_idx = KRYPTOS.index(ct_char)
        pt_idx = KRYPTOS.index(pt_char)
        key_char = KRYPTOS[(ct_idx - pt_idx) % 26]
        key[i] = key_char

    # Now we have positions 0-4, 5-24 filled, still need 25-28
    # For now, fill with the original assumption
    for i, c in enumerate("PABT"):
        key[25 + i] = c

    key_str = ''.join(key)
    pt = decrypt(K4, key_str)

    # Score by counting recognizable patterns
    score = 0
    if "NORTHEAST" in pt: score += 100
    if "BERLINCLOCK" in pt: score += 100

    # Check for common words in the plaintext
    common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "HAD"]
    for w in common_words:
        if w in pt:
            score += len(w)

    results.append((word, key_str, pt, score))

# Sort by score
results.sort(key=lambda x: -x[3])

print("\nTop 20 starting words by score:")
for i, (word, key, pt, score) in enumerate(results[:20]):
    print(f"\n{i+1}. {word} (score: {score})")
    print(f"   Key: {key}")
    print(f"   PT: {pt}")
