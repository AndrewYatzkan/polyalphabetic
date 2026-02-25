#!/usr/bin/env python3
"""
TARGETED APPROACH: The 5 unknown key positions (16-20) determine text at
three groups of positions in the Vigenere output:
  Group A: positions 16-20
  Group B: positions 45-49
  Group C: positions 74-78

For each choice of 5 key values, these three groups spell specific 5-letter
combinations. Find choices where ALL THREE groups form English words/fragments.

Also look at the CONTEXT around these groups with fixed key positions:
  ...KZEL[A]EASTNORTHEAST... (positions 12-33)
  ...LLSAG[B]QUGDM...       (positions 42-54)
  ...CLOCK[C]WQULC...        (positions 69-83)
"""
import math
from collections import Counter

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def k_idx(c): return KRYPTOS.index(c)
def k_chr(i): return KRYPTOS[i % 26]

# Load quadgrams
QG = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QG[parts[0]] = int(parts[1])
total = sum(QG.values())
QG_LOG = {k: math.log10(v/total) for k, v in QG.items()}
QG_FLOOR = math.log10(0.01/total)

def qscore(text):
    score = 0
    for i in range(len(text)-3):
        q = text[i:i+4]
        score += QG_LOG.get(q, QG_FLOOR)
    return score

# Known key positions (KRYPTOS alphabet indices)
KNOWN_KEY = "OYNKYELYOIECBAQK?????RDUMRIYW"

# For each of the 26^5 key choices, compute the 3 groups
# and look for English combinations

# First, let's understand the mapping:
# Key position k (16-20) affects CT positions: k, k+29, k+58, (k+87 if < 97)
# Position 16: CT positions 16, 45, 74 (and 87+16=103 > 97, so only 3)
# Position 17: CT positions 17, 46, 75
# Position 18: CT positions 18, 47, 76
# Position 19: CT positions 19, 48, 77
# Position 20: CT positions 20, 49, 78

print("=== CT characters at key-dependent positions ===")
for kp in range(16, 21):
    positions = [kp + 29*r for r in range(4) if kp + 29*r < 97]
    ct_chars = [K4[p] for p in positions]
    ct_idxs = [k_idx(c) for c in ct_chars]
    print(f"  Key pos {kp}: CT positions {positions}")
    print(f"    CT chars: {ct_chars}, CT indices: {ct_idxs}")

# Get the fixed Vigenere output at non-key-dependent positions
fixed_key = {}
for i in range(29):
    if i < 16 or i > 20:
        fixed_key[i] = k_idx(KNOWN_KEY[i])

fixed_pt = {}
for i in range(97):
    kp = i % 29
    if kp in fixed_key:
        fixed_pt[i] = k_chr((k_idx(K4[i]) - fixed_key[kp]) % 26)

print("\n=== Fixed Vigenere output (non-key-dependent positions) ===")
for i in range(97):
    if i in fixed_pt:
        print(fixed_pt[i], end='')
    else:
        print('?', end='')
print()

# Context around the 3 groups
print("\n=== Context around key-dependent groups ===")
print("Group A context (positions 10-35):")
for i in range(10, 36):
    if i in fixed_pt:
        print(fixed_pt[i], end='')
    else:
        print('?', end='')
print()

print("Group B context (positions 40-55):")
for i in range(40, 56):
    if i in fixed_pt:
        print(fixed_pt[i], end='')
    else:
        print('?', end='')
print()

print("Group C context (positions 69-84):")
for i in range(69, 85):
    if i in fixed_pt:
        print(fixed_pt[i], end='')
    else:
        print('?', end='')
print()

# Now: for each of 26^5 key choices, compute groups A, B, C
# and score based on English word content at those positions

# Common 5-letter English words and fragments
WORDS5 = set()
WORDS4 = set()
WORDS3 = set()

# 5-letter words
for w in ["ABOUT", "AFTER", "AGAIN", "ALONG", "AMONG", "ANGLE", "BEING",
          "BLACK", "BLOCK", "BOARD", "BOUND", "BREAK", "BRING", "BUILT",
          "CARDS", "CAUSE", "CHAIN", "CHIEF", "CHILD", "CLAIM", "CLASS",
          "CLEAN", "CLEAR", "CLIMB", "CLOSE", "CLOCK", "COULD", "COUNT",
          "COVER", "CROSS", "CYCLE", "DAILY", "DEATH", "EIGHT", "EMBER",
          "EMPTY", "ENTER", "EQUAL", "ERROR", "EVENT", "EVERY", "EXACT",
          "EXTRA", "FAITH", "FALSE", "FIELD", "FIFTY", "FINAL", "FIRST",
          "FIXED", "FLAME", "FLESH", "FLOOR", "FOCUS", "FORCE", "FORTH",
          "FOUND", "FRAME", "FRONT", "GIVEN", "GLASS", "GOING", "GRACE",
          "GRADE", "GRAND", "GRANT", "GRASS", "GRAVE", "GREAT", "GREEN",
          "GROSS", "GROUP", "GROWN", "GUARD", "GUESS", "GUIDE", "HANDS",
          "HAPPY", "HEART", "HENCE", "HORSE", "HOURS", "HOUSE", "HUMAN",
          "IMAGE", "INNER", "ISSUE", "JUDGE", "KNOWN", "LABOR", "LARGE",
          "LATER", "LAYER", "LEARN", "LEAST", "LEAVE", "LEVEL", "LIGHT",
          "LIMIT", "LINES", "LOGIC", "LOWER", "LYING", "MAJOR", "MATCH",
          "MEANT", "METAL", "MIGHT", "MINOR", "MINUS", "MODEL", "MONEY",
          "MONTH", "MORAL", "MOUTH", "MOVED", "MUSIC", "NAMED", "NEVER",
          "NIGHT", "NOBLE", "NOISE", "NORTH", "NOTED", "NOVEL", "OCCUR",
          "OFFER", "OFTEN", "ORDER", "OTHER", "OUTER", "OWNER", "PAINT",
          "PANEL", "PAPER", "PARTS", "PARTY", "PATCH", "PAUSE", "PEACE",
          "PHASE", "PIECE", "PILOT", "PITCH", "PLACE", "PLAIN", "PLANE",
          "PLANT", "PLATE", "PLAZA", "PLEAD", "PLUMB", "POINT", "POUND",
          "POWER", "PRESS", "PRICE", "PRIDE", "PRIME", "PRINT", "PRIOR",
          "PRIZE", "PROOF", "PROUD", "PROVE", "QUEEN", "QUEST", "QUICK",
          "QUIET", "QUITE", "QUOTE", "RADIO", "RAISE", "RANGE", "RAPID",
          "RATIO", "REACH", "REALM", "REIGN", "REPLY", "RIGHT", "RIVER",
          "ROBOT", "ROUND", "ROUTE", "ROYAL", "RURAL", "SAINT", "SCALE",
          "SCENE", "SCOPE", "SCORE", "SENSE", "SERVE", "SEVEN", "SHALL",
          "SHAPE", "SHARE", "SHARP", "SHELL", "SHIFT", "SHINE", "SHORT",
          "SHOWN", "SIGHT", "SINCE", "SIXTY", "SLEEP", "SLIDE", "SMALL",
          "SMART", "SMILE", "SMITH", "SMOKE", "SOLID", "SOLVE", "SORRY",
          "SOUND", "SOUTH", "SPACE", "SPARE", "SPEAK", "SPEED", "SPEND",
          "SPLIT", "SPOKE", "STAFF", "STAGE", "STAND", "START", "STATE",
          "STAYS", "STEAM", "STEEL", "STEEP", "STERN", "STICK", "STILL",
          "STOCK", "STONE", "STOOD", "STORE", "STORM", "STORY", "STRIP",
          "STUCK", "STUFF", "STYLE", "SUGAR", "SUITE", "SUPER", "SWEET",
          "SWEPT", "SWORD", "TABLE", "TAKEN", "TASTE", "TEACH", "TERMS",
          "THANK", "THEME", "THERE", "THICK", "THING", "THINK", "THIRD",
          "THOSE", "THREE", "THREW", "THROW", "TIGHT", "TIMES", "TITLE",
          "TODAY", "TOKEN", "TOTAL", "TOUCH", "TOUGH", "TOWER", "TOWNS",
          "TRACE", "TRACK", "TRADE", "TRAIL", "TRAIN", "TRAIT", "TRANS",
          "TREAT", "TREND", "TRIAL", "TRIBE", "TRICK", "TRIED", "TROOP",
          "TRUCK", "TRULY", "TRUST", "TRUTH", "ULTRA", "UNDER", "UNION",
          "UNITE", "UNITY", "UNTIL", "UPPER", "UPSET", "URBAN", "USAGE",
          "USUAL", "USING", "UTTER", "VALID", "VALUE", "VIDEO", "VIGOR",
          "VINYL", "VIRAL", "VISIT", "VITAL", "VOCAL", "VOICE", "WASTE",
          "WATCH", "WATER", "WEIGH", "WHEEL", "WHERE", "WHICH", "WHILE",
          "WHITE", "WHOLE", "WHOSE", "WIDER", "WOMAN", "WORLD", "WORRY",
          "WORSE", "WORST", "WORTH", "WOULD", "WRITE", "WROTE", "YIELD",
          "YOUNG", "YOUTH",
          # Kryptos-specific
          "BELOW", "BERLI", "CLOCK", "EARTH", "LAYER", "SHADO", "SLOWL",
          "DESPE", "BETWE", "COMPA", "BEARI", "DEGRE", "GRIDS", "HIDDE",
          "SECRE", "BURIE", "LANGL", "STEAD", "HOLDS", "HOLDI"]:
    WORDS5.add(w)

# 4-letter words for partial matching
for w in ["THAT", "WITH", "THIS", "HAVE", "FROM", "THEY", "BEEN", "SAID",
          "EACH", "MAKE", "LIKE", "LONG", "LOOK", "MANY", "SOME", "TIME",
          "VERY", "WHEN", "COME", "YOUR", "THEM", "THAN", "CALL", "WILL",
          "MOST", "INTO", "OVER", "SUCH", "TAKE", "YEAR", "ALSO", "BACK",
          "WORK", "GOOD", "GIVE", "LAST", "HAND", "HIGH", "KEEP", "KNOW",
          "PART", "TAKE", "SHOW", "SIDE", "TURN", "EAST", "WEST", "HOLD",
          "LINE", "DARK", "STEP", "NEAR", "SLOW", "DEEP", "BEAR", "GRID",
          "MASK", "HIDE", "BURY", "CLUE", "FIND", "SEEK", "GATE", "WALL",
          "ROOM", "DOOR", "SIGN", "CODE", "LOCK", "OPEN", "PASS", "HALF",
          "TRUE", "LIES"]:
    WORDS4.add(w)

# 3-letter words
for w in ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "ANY",
          "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "HAD", "HAS",
          "HIS", "HOW", "ITS", "LET", "MAY", "NEW", "NOW", "OLD", "SEE",
          "WAY", "WHO", "DID", "GOT", "USE", "SAY", "SHE", "TWO", "SET"]:
    WORDS3.add(w)

print("\n=== Searching for word combinations at key-dependent positions ===")
print("Testing all 26^5 key combinations...\n")

# For efficiency, precompute CT indices
ct_indices = {}
for kp in range(16, 21):
    positions = [kp + 29*r for r in range(4) if kp + 29*r < 97]
    ct_indices[kp] = [(p, k_idx(K4[p])) for p in positions]

best_word_score = 0
best_word_results = []
best_qg_score = -999999
best_qg_result = None

count = 0
for v16 in range(26):
    for v17 in range(26):
        for v18 in range(26):
            for v19 in range(26):
                for v20 in range(26):
                    unknowns = [v16, v17, v18, v19, v20]

                    # Compute the three groups
                    groups = ['', '', '']
                    for ki, kp in enumerate(range(16, 21)):
                        for gi, (pos, ct_val) in enumerate(ct_indices[kp]):
                            pt_val = (ct_val - unknowns[ki]) % 26
                            groups[gi] += k_chr(pt_val)

                    # Score based on words found
                    word_score = 0
                    found_words = []

                    for gi, g in enumerate(groups):
                        if g in WORDS5:
                            word_score += 50
                            found_words.append((gi, g))
                        # Check 4-letter substrings
                        for start in range(len(g)-3):
                            sub = g[start:start+4]
                            if sub in WORDS4:
                                word_score += 20
                                found_words.append((gi, sub))
                        # Check 3-letter substrings
                        for start in range(len(g)-2):
                            sub = g[start:start+3]
                            if sub in WORDS3:
                                word_score += 5
                                found_words.append((gi, sub))

                    if word_score > best_word_score:
                        best_word_score = word_score
                        best_word_results = [(unknowns[:], groups[:], found_words[:])]
                    elif word_score == best_word_score and word_score > 0:
                        best_word_results.append((unknowns[:], groups[:], found_words[:]))

                    # Also compute full Vigenere plaintext and score
                    if word_score >= 40:  # Only for promising ones
                        key = list(KNOWN_KEY)
                        for i, v in enumerate(unknowns):
                            key[16+i] = KRYPTOS[v]
                        key_str = ''.join(key)
                        pt = []
                        for i in range(97):
                            kp = i % 29
                            ki = k_idx(key_str[kp])
                            ci = k_idx(K4[i])
                            pt.append(k_chr((ci - ki) % 26))
                        pt_str = ''.join(pt)
                        s = qscore(pt_str)
                        if s > best_qg_score:
                            best_qg_score = s
                            best_qg_result = (unknowns[:], key_str, pt_str, groups[:], found_words[:])

                    count += 1

    # Progress
    pct = (v16+1) / 26 * 100
    print(f"  {pct:.0f}% done, best word score: {best_word_score}, results so far: {len(best_word_results)}")

print(f"\n=== RESULTS ===")
print(f"Best word score: {best_word_score}")
print(f"Number of results with best score: {len(best_word_results)}")

# Show top results
shown = 0
for unknowns, groups, words in best_word_results[:50]:
    key_chars = ''.join(KRYPTOS[v] for v in unknowns)
    print(f"\n  Key[16-20] = {key_chars} ({unknowns})")
    print(f"    Group A (pos 16-20): {groups[0]}")
    print(f"    Group B (pos 45-49): {groups[1]}")
    print(f"    Group C (pos 74-78): {groups[2]}")
    print(f"    Words: {words}")

    # Full context
    key = list(KNOWN_KEY)
    for i, v in enumerate(unknowns):
        key[16+i] = KRYPTOS[v]
    key_str = ''.join(key)
    pt = []
    for i in range(97):
        kp = i % 29
        ki = k_idx(key_str[kp])
        ci = k_idx(K4[i])
        pt.append(k_chr((ci - ki) % 26))
    pt_str = ''.join(pt)
    s = qscore(pt_str)
    print(f"    Full PT: {pt_str}")
    print(f"    Quadgram score: {s:.2f}")
    shown += 1

if best_qg_result:
    unknowns, key_str, pt_str, groups, words = best_qg_result
    print(f"\n=== BEST QUADGRAM RESULT (among high word-score candidates) ===")
    print(f"  Key: {key_str}")
    print(f"  PT:  {pt_str}")
    print(f"  Score: {best_qg_score:.2f}")
    print(f"  Groups: A={groups[0]} B={groups[1]} C={groups[2]}")
    print(f"  Words: {words}")

# Now: specifically test keys that make Group C start with "HOLDS", "WHERE", etc.
print("\n=== TARGETED WORD TESTS AT SPECIFIC POSITIONS ===")

# What word could follow BERLINCLOCK?
# BERLINCLOCKHOLDS, BERLINCLOCKTIME, BERLINCLOCKSHOW
# Group C = pos 74-78, which is right after BERLINCLOCK (63-73)
# So positions 74-78 follow "CK" at 72-73

# Also: what precedes EASTNORTHEAST?
# Group A = pos 16-20, followed by EASTNORTHEAST at 21-33
# So we need: [Group A]EASTNORTHEAST

target_phrases = {
    "A": [  # What comes before EASTNORTHEAST?
        "POINT", "GOING", "LEADS", "TAKEN", "AIMED",
        "TWOFE", "HEADS", "LOOKS", "MOVES", "FACIN",
        "THREE", "STEER", "GUIDE", "DRIFT", "SIXTY",
        "FIFTY", "NORTH", "SOUTH", "BEARS", "WHEEL",
        "DEGRE", "GRIDS", "COMPA", "FORTY", "EIGHT",
        "SEVER", "FORCE", "TRACK", "CHART",
    ],
    "C": [  # What comes after BERLINCLOCK (positions 74-78)
        "HOLDS", "SHOWS", "HANDS", "READS", "TELLS",
        "TOWER", "TIMES", "FACES", "STOOD", "POINT",
        "MARKS", "LIGHT", "SIGNS", "TURNS", "RINGS",
        "GIVES", "LEADS", "GUIDE", "HOURS", "AFTER",
        "SHONE", "ABOVE", "UNDER", "WHERE",
    ],
}

print("\nGroup A (precedes EASTNORTHEAST):")
for target in target_phrases["A"]:
    # Find key values that produce this at positions 16-20
    unknowns = []
    for ki, kp in enumerate(range(16, 21)):
        ct_val = k_idx(K4[kp])
        target_val = k_idx(target[ki])
        key_val = (ct_val - target_val) % 26
        unknowns.append(key_val)

    # Check what groups B and C become
    groups = ['', '', '']
    for ki, kp in enumerate(range(16, 21)):
        for gi, (pos, ct_val) in enumerate(ct_indices[kp]):
            pt_val = (ct_val - unknowns[ki]) % 26
            groups[gi] += k_chr(pt_val)

    # Check for words in B and C
    word_hits = []
    for g in [groups[1], groups[2]]:
        for w in WORDS5:
            if w == g:
                word_hits.append(w)
        for w in WORDS4:
            if w in g:
                word_hits.append(w)
        for w in WORDS3:
            if w in g:
                word_hits.append(w)

    # Full decrypt
    key = list(KNOWN_KEY)
    for i, v in enumerate(unknowns):
        key[16+i] = KRYPTOS[v]
    key_str = ''.join(key)
    pt = []
    for i in range(97):
        kp = i % 29
        ki = k_idx(key_str[kp])
        ci = k_idx(K4[i])
        pt.append(k_chr((ci - ki) % 26))
    pt_str = ''.join(pt)
    s = qscore(pt_str)

    marker = " ***" if word_hits else ""
    if word_hits or target in ["POINT", "NORTH", "SIXTY", "FORTY"]:
        print(f"  A={target} → B={groups[1]} C={groups[2]} score={s:.2f} words={word_hits}{marker}")
        if s > -650:
            print(f"    Full PT: {pt_str}")

print("\nGroup C (follows BERLINCLOCK):")
for target in target_phrases["C"]:
    unknowns = []
    for ki, kp in enumerate(range(16, 21)):
        # Group C = 3rd occurrence (positions 74-78)
        ct_pos = kp + 29*2  # = 74, 75, 76, 77, 78
        ct_val = k_idx(K4[ct_pos])
        target_val = k_idx(target[ki])
        key_val = (ct_val - target_val) % 26
        unknowns.append(key_val)

    groups = ['', '', '']
    for ki, kp in enumerate(range(16, 21)):
        for gi, (pos, ct_val) in enumerate(ct_indices[kp]):
            pt_val = (ct_val - unknowns[ki]) % 26
            groups[gi] += k_chr(pt_val)

    word_hits = []
    for g in [groups[0], groups[1]]:
        for w in WORDS5:
            if w == g:
                word_hits.append(w)
        for w in WORDS4:
            if w in g:
                word_hits.append(w)
        for w in WORDS3:
            if w in g:
                word_hits.append(w)

    key = list(KNOWN_KEY)
    for i, v in enumerate(unknowns):
        key[16+i] = KRYPTOS[v]
    key_str = ''.join(key)
    pt = []
    for i in range(97):
        kp = i % 29
        ki = k_idx(key_str[kp])
        ci = k_idx(K4[i])
        pt.append(k_chr((ci - ki) % 26))
    pt_str = ''.join(pt)
    s = qscore(pt_str)

    marker = " ***" if word_hits else ""
    if word_hits or target in ["HOLDS", "HANDS", "TOWER", "SHOWS", "HOURS"]:
        print(f"  C={target} → A={groups[0]} B={groups[1]} score={s:.2f} words={word_hits}{marker}")
        if s > -650:
            print(f"    Full PT: {pt_str}")

print("\nDone.")
