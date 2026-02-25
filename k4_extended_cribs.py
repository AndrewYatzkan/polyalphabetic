#!/usr/bin/env python3
"""
K4 Extended Crib Analysis — Period 29 Vigenere

The grille/mask agent found that POINTEASTNORTHEAST...BERLINCLOCKHOLDOW
scores nearly like natural English (-4.395/char). This suggests the plaintext
may actually extend beyond the known cribs EASTNORTHEAST (pos 21-33) and
BERLINCLOCK (pos 63-73).

Key insight:
  - Positions 16-20 map to key positions 16,17,18,19,20  (the 5 unknowns)
  - Positions 45-49 map to key positions 45%29=16..20    (same unknowns!)
  - Positions 74-78 map to key positions 74%29=16..20    (same unknowns!)

So a word at any of those three windows directly determines the full key.
All three windows must agree on the same key values.

Known key (period 29): OYNKYELYOIECBAQK?????RDUMRIYW
                         0123456789012345678901234567 8
                                                ^^^^^
                                              16-20 unknown
"""

import math
import itertools
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ALPHA_SIZE = 26

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
CT_LEN = len(K4)  # 97

KNOWN_KEY_TEMPLATE = "OYNKYELYOIECBAQK?????RDUMRIYW"
PERIOD = 29
UNKNOWN_POSITIONS = [16, 17, 18, 19, 20]

QUADGRAM_FILE = "/home/user/polyalphabetic/english_quadgrams.txt"

# Build index lookups
char_to_idx = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}
idx_to_char = list(KRYPTOS_ALPHA)

# ============================================================
# QUADGRAM SCORER
# ============================================================

class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        with open(filepath) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    gram, count = parts[0], int(parts[1])
                    self.quadgrams[gram] = count
                    self.total += count
        self.floor = math.log10(0.01 / self.total)

    def score(self, text):
        text = text.upper()
        if len(text) < 4:
            return -999999.0
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            if gram in self.quadgrams:
                s += math.log10(self.quadgrams[gram] / self.total)
            else:
                s += self.floor
        return s

    def score_per_char(self, text):
        text = text.upper()
        if len(text) < 4:
            return -99.0
        return self.score(text) / (len(text) - 3)


# ============================================================
# VIGENERE ENCRYPT / DECRYPT (KRYPTOS ALPHABET)
# ============================================================

def encrypt_char(p, k):
    """Ciphertext = (plain + key) mod 26 in KRYPTOS alphabet."""
    return idx_to_char[(char_to_idx[p] + char_to_idx[k]) % ALPHA_SIZE]

def decrypt_char(c, k):
    """Plaintext = (cipher - key) mod 26 in KRYPTOS alphabet."""
    return idx_to_char[(char_to_idx[c] - char_to_idx[k]) % ALPHA_SIZE]

def key_for_pair(c, p):
    """Given ciphertext char c and plaintext char p, return the key char."""
    return idx_to_char[(char_to_idx[c] - char_to_idx[p]) % ALPHA_SIZE]

def decrypt_full(ciphertext, key_29):
    """Decrypt full ciphertext with a 29-char key."""
    result = []
    for i, c in enumerate(ciphertext):
        k = key_29[i % PERIOD]
        if k == '?':
            result.append('?')
        else:
            result.append(decrypt_char(c, k))
    return ''.join(result)


# ============================================================
# DERIVE KEY FROM CRIB AT POSITION
# ============================================================

def derive_key_from_crib(crib, start_pos):
    """
    Given a plaintext crib at ciphertext position start_pos,
    derive the key characters implied for the corresponding key positions.
    Returns dict: key_position -> key_char
    """
    key_chars = {}
    for i, p in enumerate(crib):
        ct_pos = start_pos + i
        if ct_pos >= CT_LEN:
            break
        c = K4[ct_pos]
        k = key_for_pair(c, p)
        kp = ct_pos % PERIOD
        key_chars[kp] = k
    return key_chars


def is_consistent_with_known_key(derived_keys):
    """
    Check if derived key values are consistent with the known key template.
    Returns True if all derived values match (or fill unknowns), False on conflict.
    """
    for kp, kc in derived_keys.items():
        template_char = KNOWN_KEY_TEMPLATE[kp]
        if template_char != '?' and template_char != kc:
            return False
    return True


def build_full_key(extra_keys):
    """
    Build a complete 29-char key by filling unknowns with extra_keys dict.
    Returns None if any position still unknown.
    """
    key = list(KNOWN_KEY_TEMPLATE)
    for pos, ch in extra_keys.items():
        if key[pos] == '?':
            key[pos] = ch
        elif key[pos] != ch:
            return None  # conflict
    if '?' in key:
        return None
    return ''.join(key)


# ============================================================
# ENGLISH WORD FINDER
# ============================================================

# Common English words to look for in decrypted text
COMMON_WORDS_3 = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                  "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "HIS", "HAS",
                  "ITS", "WHO", "DID", "HIM", "GET", "MAN", "NEW", "NOW",
                  "OLD", "SEE", "WAY", "DAY", "HAD", "HOW", "MAY", "SAY"]

COMMON_WORDS_4PLUS = ["THAT", "THIS", "WITH", "HAVE", "FROM", "THEY", "BEEN",
                      "SAID", "EACH", "WHICH", "THEIR", "WILL", "OTHER",
                      "ABOUT", "MANY", "THEN", "THEM", "THESE", "SOME",
                      "WOULD", "MAKE", "LIKE", "TIME", "VERY", "WHEN",
                      "WHAT", "YOUR", "JUST", "KNOW", "TAKE", "PEOPLE",
                      "INTO", "YEAR", "COULD", "THAN", "LOOK", "ONLY",
                      "COME", "OVER", "SUCH", "ALSO", "BACK", "AFTER",
                      "WORK", "FIRST", "WELL", "EVEN", "WANT", "GIVE",
                      "MOST", "FIND", "HERE", "THING", "STILL", "LONG",
                      "DOWN", "SHOULD", "WORLD", "UNDER", "WHILE",
                      "EAST", "WEST", "NORTH", "SOUTH", "CLOCK",
                      "BERLIN", "POINT", "DEGREE", "DEGREES",
                      "BETWEEN", "LAYER", "SHADOW", "LIGHT", "DARK",
                      "HIDDEN", "SECRET", "BURIED", "SLOWLY",
                      "DESPER", "ATELY", "TOTAL", "DIGIT", "IQLUSION",
                      "LANGLEY", "INVISIBLE", "UNDERGROUND"]


def find_english_words(text, min_len=3):
    """Find common English words in text. Returns list of (word, position)."""
    found = []
    all_words = COMMON_WORDS_3 + COMMON_WORDS_4PLUS
    for word in all_words:
        idx = 0
        while True:
            idx = text.find(word, idx)
            if idx == -1:
                break
            found.append((word, idx))
            idx += 1
    return sorted(found, key=lambda x: (-len(x[0]), x[1]))


# ============================================================
# MAIN ANALYSIS
# ============================================================

print("=" * 78)
print("K4 EXTENDED CRIB ANALYSIS — Period 29 Vigenere")
print("=" * 78)
print()
print(f"K4 ciphertext ({CT_LEN} chars):")
print(f"  {K4}")
print(f"Known key template: {KNOWN_KEY_TEMPLATE}")
print(f"Unknown positions:  {UNKNOWN_POSITIONS}")
print()

# Load quadgram scorer
print("Loading quadgram scorer...")
scorer = QuadgramScorer(QUADGRAM_FILE)
print(f"  Loaded {len(scorer.quadgrams)} quadgrams, total count = {scorer.total}")
print()

# ============================================================
# SECTION A: If HOLD appears at positions 74-77
# ============================================================

print("=" * 78)
print("SECTION A: HOLD at positions 74-77")
print("=" * 78)

crib_hold = "HOLD"
derived_a = derive_key_from_crib(crib_hold, 74)
print(f"  Crib '{crib_hold}' at positions 74-77")
print(f"  Ciphertext at 74-77: {K4[74:78]}")
for kp in sorted(derived_a):
    print(f"    Key position {kp} (= ct pos {74 + kp - 16} % 29): '{derived_a[kp]}'")
consistent_a = is_consistent_with_known_key(derived_a)
print(f"  Consistent with known key: {consistent_a}")
print()

# ============================================================
# SECTION B: If HOLDOW appears at positions 74-79
# ============================================================

print("=" * 78)
print("SECTION B: HOLDOW at positions 74-79")
print("=" * 78)

crib_holdow = "HOLDOW"
derived_b = derive_key_from_crib(crib_holdow, 74)
print(f"  Crib '{crib_holdow}' at positions 74-79")
print(f"  Ciphertext at 74-79: {K4[74:80]}")
for kp in sorted(derived_b):
    print(f"    Key position {kp}: '{derived_b[kp]}'")
consistent_b = is_consistent_with_known_key(derived_b)
print(f"  Consistent with known key: {consistent_b}")

if consistent_b:
    full_key_b = build_full_key(derived_b)
    if full_key_b:
        pt_b = decrypt_full(K4, full_key_b)
        score_b = scorer.score_per_char(pt_b)
        print(f"  Full key: {full_key_b}")
        print(f"  Plaintext: {pt_b}")
        print(f"  Score/char: {score_b:.4f}")
        words_b = find_english_words(pt_b)
        if words_b:
            print(f"  English words found: {words_b[:15]}")
print()

# ============================================================
# SECTION C: Test words extending BEFORE EASTNORTHEAST (pos 16-20)
# ============================================================

print("=" * 78)
print("SECTION C: Words at positions 16-20 (before EASTNORTHEAST at 21-33)")
print("=" * 78)
print()

# These cribs would sit at positions 16-20 and be followed by EASTNORTHEAST at 21
# So the word at 16-20 is 5 chars ending just before EASTNORTHEAST
prefixes_5 = [
    "POINT",   # "POINT EAST NORTHEAST"
    "BEARI",   # start of BEARING
    "HEADI",   # start of HEADING
    "GOING",   # direction
    "FACIN",   # FACING
    "ATBEA",   # "AT BEARING"
    "NORTH",   # NORTHEAST NORTHEAST
    "SOUTH",   # SOUTHEAST NORTHEAST? unlikely
    "DUETO",   # DUE TO
    "TOTHE",   # TO THE EAST NORTHEAST
    "ISTHE",   # IS THE
    "BYTHE",   # BY THE
    "OFTHE",   # OF THE
    "RISIN",   # RISING
    "ATTHE",   # AT THE
    "ONTHE",   # ON THE
    "INTHE",   # IN THE
    "FIXAT",   # FIXAT(ION)
    "COMPA",   # COMPASS
    "TRUEN",   # TRUE NORTH?
    "EXACT",   # EXACT
    "THIRT",   # THIRTY
    "TWEST",   # ? (unlikely)
    "CLOCK",   # CLOCK
    "EIGHT",   # EIGHT
]

section_c_results = []
for prefix in prefixes_5:
    derived = derive_key_from_crib(prefix, 16)
    if is_consistent_with_known_key(derived):
        full_key = build_full_key(derived)
        if full_key:
            pt = decrypt_full(K4, full_key)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            section_c_results.append((prefix, full_key, pt, sc, words))
            status = "CONSISTENT"
        else:
            status = "INCOMPLETE KEY"
    else:
        status = "CONFLICT"
    print(f"  '{prefix}' at pos 16-20: {status}")

print()
print("  === Detailed results for consistent prefixes (sorted by score) ===")
section_c_results.sort(key=lambda x: -x[3])
for prefix, fk, pt, sc, words in section_c_results:
    print(f"\n  Prefix: '{prefix}'  Score/char: {sc:.4f}")
    print(f"  Key:    {fk}")
    print(f"  Plain:  {pt}")
    word_strs = [f"{w}@{p}" for w, p in words[:15]]
    print(f"  Words:  {', '.join(word_strs)}")
print()

# ============================================================
# SECTION D: Test words after BERLINCLOCK at position 74+
# ============================================================

print("=" * 78)
print("SECTION D: Words starting at position 74 (after BERLINCLOCK at 63-73)")
print("=" * 78)
print()

# Position 74 is right after BERLINCLOCK (63-73)
# Try various words/phrases that might follow "BERLIN CLOCK"
post_berlinclock_cribs = [
    # Starting at 74
    ("HOLDS", 74),
    ("TOWER", 74),
    ("SHOWS", 74),
    ("READS", 74),
    ("TELLS", 74),
    ("TICKS", 74),
    ("STOPS", 74),
    ("WORKS", 74),
    ("STAND", 74),
    ("STOOD", 74),
    ("RINGS", 74),
    ("LIGHT", 74),
    ("MIDNI", 74),   # MIDNIGHT
    ("UNDER", 74),
    ("BELOW", 74),
    ("ABOVE", 74),
    ("NEARB", 74),   # NEARBY
    ("THIRT", 74),   # THIRTY
    ("TWELV", 74),   # TWELVE
    ("THREE", 74),
    ("SEVEN", 74),
    ("EIGHT", 74),
    ("ELEVE", 74),   # ELEVEN
    ("TWENT", 74),   # TWENTY
    # "HOLDOW" and other extended forms
    ("HOLDOW", 74),
    ("HOLDSW", 74),
    ("HOLDER", 74),
    ("SHADO", 74),   # SHADOW
    ("HIDDE", 74),   # HIDDEN
    ("SECRE", 74),   # SECRET
    ("BURIE", 74),   # BURIED
    ("LAYER", 74),
    # Try with pos 74 starting a sentence fragment
    ("ATONE", 74),
    ("ISONE", 74),
    ("ISTHE", 74),
    ("ISNOT", 74),
    ("ANDTH", 74),
    ("ONTHE", 74),
    ("INTHE", 74),
    ("FORSA", 74),   # FORSAKE?
    ("MARKS", 74),
    ("POINT", 74),
]

section_d_results = []
for crib, pos in post_berlinclock_cribs:
    derived = derive_key_from_crib(crib, pos)
    if is_consistent_with_known_key(derived):
        full_key = build_full_key(derived)
        if full_key:
            pt = decrypt_full(K4, full_key)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            section_d_results.append((crib, pos, full_key, pt, sc, words))
            status = "CONSISTENT"
        else:
            status = "INCOMPLETE KEY"
    else:
        status = "CONFLICT"
    print(f"  '{crib}' at pos {pos}: {status}")

print()
print("  === Detailed results for consistent cribs (sorted by score) ===")
section_d_results.sort(key=lambda x: -x[4])
for crib, pos, fk, pt, sc, words in section_d_results:
    print(f"\n  Crib: '{crib}' at pos {pos}  Score/char: {sc:.4f}")
    print(f"  Key:    {fk}")
    print(f"  Plain:  {pt}")
    word_strs = [f"{w}@{p}" for w, p in words[:15]]
    print(f"  Words:  {', '.join(word_strs)}")
print()

# ============================================================
# SECTION E & F: Test ALL consistent pairs across positions 16-20, 45-49, 74-78
# ============================================================

print("=" * 78)
print("SECTION E/F: Consistent pairs — positions 16-20 / 45-49 / 74-78")
print("            (All three windows map to key positions 16-20)")
print("=" * 78)
print()

# First, build a comprehensive list of 5-letter candidates for each window
# Window 1: positions 16-20 (before EASTNORTHEAST)
# Window 2: positions 45-49 (mid-text)
# Window 3: positions 74-78 (after BERLINCLOCK)

# For window 1 (pos 16-20), things that make sense before EASTNORTHEAST:
window1_cribs = [
    "POINT", "BEARI", "HEADI", "GOING", "FACIN",
    "NORTH", "SOUTH", "DUETO", "TOTHE", "ISTHE",
    "BYTHE", "OFTHE", "ATTHE", "ONTHE", "INTHE",
    "RISIN", "COMPA", "TRUEN", "EXACT", "EIGHT",
    "CLOCK", "THIRT", "FIXAT",
]

# For window 2 (pos 45-49), could be anything:
window2_cribs = [
    "THEWA", "THERE", "THETR", "UNDER", "INTHE",
    "ATTHE", "ONTHE", "NORTH", "SOUTH", "WHERE",
    "WHICH", "THESE", "THOSE", "THEIR", "ABOUT",
    "WOULD", "COULD", "SHALL", "AFTER", "BELOW",
    "ABOVE", "BETWE", "LAYOF", "LAYER", "SHADO",
    "LIGHT", "DARKN", "SECRE", "HIDDE", "NEVER",
    "OFTEN", "GIVEN", "ISNOT", "TAKEN", "FOUND",
    "KNOWN", "POINT", "DEGRE", "THROU",
]

# For window 3 (pos 74-78), things after BERLINCLOCK:
window3_cribs = [
    "HOLDS", "TOWER", "SHOWS", "READS", "TELLS",
    "TICKS", "STOPS", "WORKS", "STAND", "RINGS",
    "LIGHT", "MIDNI", "UNDER", "BELOW", "ABOVE",
    "NEARB", "THIRT", "TWELV", "THREE", "SEVEN",
    "EIGHT", "ELEVE", "TWENT", "HOLDO",
    "SHADO", "HIDDE", "SECRE", "BURIE", "LAYER",
    "ATONE", "ISONE", "ISTHE", "ANDTH", "ONTHE",
    "INTHE", "MARKS", "POINT",
]


def derive_unknown_5(crib, start_pos):
    """
    Derive the 5 unknown key values from a 5-char crib at start_pos.
    start_pos must be such that start_pos%29 == 16.
    Returns a tuple of 5 key chars for positions 16-20, or None on conflict.
    """
    key_vals = {}
    for i in range(len(crib)):
        ct_pos = start_pos + i
        if ct_pos >= CT_LEN:
            return None
        kp = ct_pos % PERIOD
        c = K4[ct_pos]
        k = key_for_pair(c, crib[i])
        if kp in key_vals and key_vals[kp] != k:
            return None  # internal conflict
        key_vals[kp] = k
    # Check only covers unknown positions
    for kp, kc in key_vals.items():
        tmpl = KNOWN_KEY_TEMPLATE[kp]
        if tmpl != '?' and tmpl != kc:
            return None
    # Extract positions 16-20
    result = []
    for p in UNKNOWN_POSITIONS:
        if p in key_vals:
            result.append(key_vals[p])
        else:
            result.append(None)
    return tuple(result)


print("Step 1: Derive key[16-20] from each crib in each window")
print()

# Store: key_tuple -> list of (window, crib, start_pos)
key_to_sources = defaultdict(list)

for crib in window1_cribs:
    vals = derive_unknown_5(crib, 16)
    if vals and all(v is not None for v in vals):
        key_to_sources[vals].append((1, crib, 16))

for crib in window2_cribs:
    vals = derive_unknown_5(crib, 45)
    if vals and all(v is not None for v in vals):
        key_to_sources[vals].append((2, crib, 45))

for crib in window3_cribs:
    vals = derive_unknown_5(crib, 74)
    if vals and all(v is not None for v in vals):
        key_to_sources[vals].append((3, crib, 74))

# Also test 6-char cribs at pos 74 (covers key 16-21, but 21='R' is known)
window3_cribs_6 = [
    "HOLDOW", "TOWERS", "SHOWED", "READER",
    "HIDDEN", "SECRET", "SHADOW", "LAYERS",
    "TWELVE", "TWENTY", "THIRTY", "ELEVEN",
]
for crib in window3_cribs_6:
    vals = derive_unknown_5(crib, 74)
    if vals and all(v is not None for v in vals):
        key_to_sources[vals].append((3, crib, 74))

print(f"  Found {len(key_to_sources)} distinct key[16-20] tuples from cribs")
print()

# Now find keys that have sources from MULTIPLE windows
print("Step 2: Find key tuples supported by MULTIPLE windows (cross-validation)")
print()
multi_window_keys = {}
for kt, sources in key_to_sources.items():
    windows_hit = set(s[0] for s in sources)
    if len(windows_hit) > 1:
        multi_window_keys[kt] = sources

if multi_window_keys:
    print(f"  Found {len(multi_window_keys)} key tuples with multi-window support!")
    for kt, sources in multi_window_keys.items():
        key_str = ''.join(kt)
        print(f"\n  Key[16-20] = {key_str}")
        for wn, crib, pos in sources:
            print(f"    Window {wn}: '{crib}' at position {pos}")
        # Build full key and decrypt
        extra = {16+i: kt[i] for i in range(5)}
        fk = build_full_key(extra)
        if fk:
            pt = decrypt_full(K4, fk)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            print(f"    Full key: {fk}")
            print(f"    Plaintext: {pt}")
            print(f"    Score/char: {sc:.4f}")
            word_strs = [f"{w}@{p}" for w, p in words[:15]]
            print(f"    Words: {', '.join(word_strs)}")
else:
    print("  No key tuples with multi-window support found among hand-picked cribs.")
print()

# ============================================================
# SECTION E (continued): For EACH consistent crib, decrypt ALL 97 chars
# ============================================================

print("=" * 78)
print("SECTION E/F: Full decryptions for ALL consistent cribs, ranked by score")
print("=" * 78)
print()

all_results = []

# Collect from all three windows
for crib in window1_cribs:
    vals = derive_unknown_5(crib, 16)
    if vals and all(v is not None for v in vals):
        extra = {16+i: vals[i] for i in range(5)}
        fk = build_full_key(extra)
        if fk:
            pt = decrypt_full(K4, fk)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            all_results.append((sc, f"W1:'{crib}'@16", fk, pt, words))

for crib in window2_cribs:
    vals = derive_unknown_5(crib, 45)
    if vals and all(v is not None for v in vals):
        extra = {16+i: vals[i] for i in range(5)}
        fk = build_full_key(extra)
        if fk:
            pt = decrypt_full(K4, fk)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            all_results.append((sc, f"W2:'{crib}'@45", fk, pt, words))

for crib in window3_cribs + window3_cribs_6:
    start = 74
    vals = derive_unknown_5(crib, start)
    if vals and all(v is not None for v in vals):
        extra = {16+i: vals[i] for i in range(5)}
        fk = build_full_key(extra)
        if fk:
            pt = decrypt_full(K4, fk)
            sc = scorer.score_per_char(pt)
            words = find_english_words(pt)
            all_results.append((sc, f"W3:'{crib}'@{start}", fk, pt, words))

# De-duplicate by full key
seen_keys = set()
unique_results = []
for r in all_results:
    if r[2] not in seen_keys:
        seen_keys.add(r[2])
        unique_results.append(r)

unique_results.sort(key=lambda x: -x[0])

print(f"Total unique full-key candidates: {len(unique_results)}")
print()
for rank, (sc, source, fk, pt, words) in enumerate(unique_results, 1):
    print(f"  #{rank}  Score/char: {sc:.4f}  Source: {source}")
    print(f"       Key:   {fk}")
    print(f"       Plain: {pt}")
    # Show words
    word_strs = [f"{w}@{p}" for w, p in words[:20]]
    print(f"       Words: {', '.join(word_strs)}")
    # Highlight the three windows
    w1 = pt[16:21]
    w2 = pt[45:50]
    w3 = pt[74:79]
    print(f"       Window1[16-20]: {w1}  Window2[45-49]: {w2}  Window3[74-78]: {w3}")
    print()

# ============================================================
# SECTION G: Detailed analysis of top candidates
# ============================================================

print("=" * 78)
print("SECTION G: Detailed analysis of top 10 candidates")
print("=" * 78)
print()

for rank, (sc, source, fk, pt, words) in enumerate(unique_results[:10], 1):
    print(f"--- Candidate #{rank}: {source}  Score/char: {sc:.4f} ---")
    print(f"  Key:       {fk}")
    print(f"  Key[16-20]: {''.join(fk[i] for i in UNKNOWN_POSITIONS)}")
    print()

    # Show plaintext with segment breakdown
    print(f"  Full plaintext: {pt}")
    print()

    # Breakdown by known/unknown segments
    segments = [
        (0, 16, "Segment A (unknown)"),
        (16, 21, "Window 1 (key 16-20)"),
        (21, 34, "EASTNORTHEAST crib"),
        (34, 45, "Segment B (unknown)"),
        (45, 50, "Window 2 (key 16-20)"),
        (50, 63, "Segment C (unknown)"),
        (63, 74, "BERLINCLOCK crib"),
        (74, 79, "Window 3 (key 16-20)"),
        (79, 97, "Segment D (unknown)"),
    ]

    for start, end, label in segments:
        seg = pt[start:end]
        if len(seg) >= 4:
            seg_sc = scorer.score_per_char(seg)
            print(f"  [{start:2d}-{end:2d}] {label:30s}: '{seg}'  (score/char: {seg_sc:.3f})")
        else:
            print(f"  [{start:2d}-{end:2d}] {label:30s}: '{seg}'")

    # Find English words in non-crib segments
    non_crib_text = pt[0:16] + pt[34:63] + pt[79:97]
    non_crib_words = find_english_words(non_crib_text)
    if non_crib_words:
        print(f"\n  English words in non-crib portions: {non_crib_words[:15]}")

    # Also look in the full plaintext
    all_words_in_pt = find_english_words(pt)
    non_trivial = [(w, p) for w, p in all_words_in_pt if len(w) >= 4
                   and not (21 <= p <= 33 - len(w) + 1)   # not in EASTNORTHEAST
                   and not (63 <= p <= 73 - len(w) + 1)]  # not in BERLINCLOCK
    if non_trivial:
        print(f"  Non-crib words (len>=4) in full plaintext: {non_trivial[:20]}")

    print()

# ============================================================
# BONUS: Exhaustive brute-force of all 26^5 key combos
#        for positions 16-20, scoring by quadgrams
# ============================================================

print("=" * 78)
print("BONUS: Exhaustive brute-force of 26^5 = 11,881,376 key combos")
print("       for unknown positions 16-20")
print("=" * 78)
print()

# Pre-compute known key indices
known_key_idx = [char_to_idx[c] if c != '?' else -1 for c in KNOWN_KEY_TEMPLATE]
ct_idx = [char_to_idx[c] for c in K4]

# Pre-compute which unknown key positions affect which ciphertext positions
# For each of the 5 unknown key positions, list the ciphertext positions
unknown_ct_positions = defaultdict(list)
for ct_pos in range(CT_LEN):
    kp = ct_pos % PERIOD
    if kp in UNKNOWN_POSITIONS:
        unknown_ct_positions[kp].append(ct_pos)

# Pre-compute partial plaintext for all known key positions
partial_pt = [0] * CT_LEN
for ct_pos in range(CT_LEN):
    kp = ct_pos % PERIOD
    if known_key_idx[kp] >= 0:
        partial_pt[ct_pos] = (ct_idx[ct_pos] - known_key_idx[kp]) % ALPHA_SIZE

print("Running brute force (this may take a moment)...")

import time
t0 = time.time()

best_heap = []  # min-heap of (score, key_tuple)
HEAP_SIZE = 50

count = 0
for k16 in range(ALPHA_SIZE):
    for k17 in range(ALPHA_SIZE):
        for k18 in range(ALPHA_SIZE):
            for k19 in range(ALPHA_SIZE):
                for k20 in range(ALPHA_SIZE):
                    # Build full plaintext as index array
                    pt_arr = list(partial_pt)
                    unk = [k16, k17, k18, k19, k20]
                    for i, kp in enumerate(UNKNOWN_POSITIONS):
                        kv = unk[i]
                        for cp in unknown_ct_positions[kp]:
                            pt_arr[cp] = (ct_idx[cp] - kv) % ALPHA_SIZE

                    # Convert to string for scoring
                    pt_str = ''.join(idx_to_char[v] for v in pt_arr)

                    # Quick check: does it contain EASTNORTHEAST and BERLINCLOCK?
                    # (It should by construction, but let's verify the first time)

                    # Score with quadgrams
                    sc = scorer.score_per_char(pt_str)

                    if len(best_heap) < HEAP_SIZE:
                        import heapq
                        heapq.heappush(best_heap, (sc, (k16, k17, k18, k19, k20), pt_str))
                    elif sc > best_heap[0][0]:
                        heapq.heapreplace(best_heap, (sc, (k16, k17, k18, k19, k20), pt_str))

                    count += 1

t1 = time.time()
print(f"Brute force complete: {count:,} keys tested in {t1-t0:.1f}s")
print()

# Sort best results
best_results = sorted(best_heap, key=lambda x: -x[0])

print(f"TOP {len(best_results)} RESULTS BY QUADGRAM SCORE:")
print()

for rank, (sc, unk_tuple, pt_str) in enumerate(best_results, 1):
    key_chars = ''.join(idx_to_char[v] for v in unk_tuple)
    # Build full key string
    fk = list(KNOWN_KEY_TEMPLATE)
    for i, kp in enumerate(UNKNOWN_POSITIONS):
        fk[kp] = idx_to_char[unk_tuple[i]]
    fk = ''.join(fk)

    words = find_english_words(pt_str)
    non_crib_words = [(w, p) for w, p in words if len(w) >= 4
                      and not (21 <= p <= 33 - len(w) + 1)
                      and not (63 <= p <= 73 - len(w) + 1)]

    print(f"  #{rank:2d}  Score/char: {sc:.4f}  Key[16-20]: {key_chars}")
    print(f"       Full key: {fk}")
    print(f"       Plaintext: {pt_str}")
    print(f"       W1[16-20]: {pt_str[16:21]}  W2[45-49]: {pt_str[45:50]}  W3[74-78]: {pt_str[74:79]}")
    if non_crib_words:
        print(f"       Non-crib words (4+): {non_crib_words[:15]}")
    print()

# ============================================================
# FINAL SUMMARY
# ============================================================

print("=" * 78)
print("FINAL SUMMARY")
print("=" * 78)
print()

if best_results:
    top_sc, top_unk, top_pt = best_results[0]
    top_key_chars = ''.join(idx_to_char[v] for v in top_unk)
    fk = list(KNOWN_KEY_TEMPLATE)
    for i, kp in enumerate(UNKNOWN_POSITIONS):
        fk[kp] = idx_to_char[top_unk[i]]
    fk = ''.join(fk)

    print(f"Best overall key[16-20]:  {top_key_chars}")
    print(f"Best full key:            {fk}")
    print(f"Best score/char:          {top_sc:.4f}")
    print(f"Best plaintext:           {top_pt}")
    print()

    # Check if POINT is the winner for position 16-20
    if top_pt[16:21] == "POINT":
        print(">>> POINT confirmed at positions 16-20 <<<")
    else:
        print(f">>> Positions 16-20 decrypt to: {top_pt[16:21]} <<<")

    # Check positions 74-78
    w3 = top_pt[74:79]
    print(f">>> Positions 74-78 decrypt to: {w3} <<<")
    w3_6 = top_pt[74:80]
    print(f">>> Positions 74-79 decrypt to: {w3_6} <<<")

    # Check position 45-49
    w2 = top_pt[45:50]
    print(f">>> Positions 45-49 decrypt to: {w2} <<<")

print()
print("Done.")
