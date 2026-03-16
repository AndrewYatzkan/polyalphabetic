#!/usr/bin/env python3
"""
Kryptos K4 - Extended Running Key Cipher Analysis
===================================================
CryptoCrack ranked RUNNING KEY as the #1 most likely cipher type for K4.

A running key cipher uses a long text passage as the key (one key letter per
ciphertext letter, no period/repetition).

With the KRYPTOS alphabet:
  CT[i] = (PT[i] + KEY[i]) mod 26
  PT[i] = (CT[i] - KEY[i]) mod 26
  KEY[i] = (CT[i] - PT[i]) mod 26

We use the confirmed cribs to derive what the running key MUST be at those
positions, then check if those key fragments look like English text (which
they should, since the key IS a passage of text).

We also test many candidate source texts at all offsets.
"""

import math
import sys
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars, K=0

assert len(KRYPTOS_ALPHA) == 26, f"KRYPTOS alphabet must be 26 chars, got {len(KRYPTOS_ALPHA)}"
assert len(K4_CT) == 97, f"K4 ciphertext must be 97 chars, got {len(K4_CT)}"

# Build index lookup
ALPHA_INDEX = {ch: i for i, ch in enumerate(KRYPTOS_ALPHA)}

# Confirmed cribs (0-indexed positions, inclusive start, exclusive end)
CRIB_ENE = ("EASTNORTHEAST", 21, 34)   # positions 21-33 inclusive = 13 chars
CRIB_BC  = ("BERLINCLOCK",   63, 74)   # positions 63-73 inclusive = 11 chars

# ============================================================
# QUADGRAM SCORER
# ============================================================

print("Loading quadgram statistics...")
QUADGRAMS = {}
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QUADGRAMS[parts[0]] = int(parts[1])

TOTAL_QG = sum(QUADGRAMS.values())
LOG_TOTAL = math.log10(TOTAL_QG)
FLOOR_LOG = math.log10(0.01 / TOTAL_QG)  # floor for unseen quadgrams

def quadgram_score(text):
    """Score a text string using log10 quadgram frequencies."""
    text = text.upper()
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        if qg in QUADGRAMS:
            score += math.log10(QUADGRAMS[qg]) - LOG_TOTAL
        else:
            score += FLOOR_LOG
    return score

def normalized_qg_score(text):
    """Quadgram score normalized per character."""
    if len(text) < 4:
        return -99.0
    return quadgram_score(text) / len(text)

# ============================================================
# KRYPTOS ALPHABET CIPHER OPERATIONS
# ============================================================

def k_index(ch):
    """Get the index of a character in the KRYPTOS alphabet."""
    return ALPHA_INDEX[ch]

def k_char(idx):
    """Get the character at a given index in the KRYPTOS alphabet."""
    return KRYPTOS_ALPHA[idx % 26]

def running_key_encrypt(plaintext, key):
    """Encrypt: CT[i] = (PT[i] + KEY[i]) mod 26 in KRYPTOS alphabet."""
    result = []
    for i in range(min(len(plaintext), len(key))):
        pt_idx = k_index(plaintext[i])
        key_idx = k_index(key[i])
        ct_idx = (pt_idx + key_idx) % 26
        result.append(k_char(ct_idx))
    return ''.join(result)

def running_key_decrypt(ciphertext, key):
    """Decrypt: PT[i] = (CT[i] - KEY[i]) mod 26 in KRYPTOS alphabet."""
    result = []
    for i in range(min(len(ciphertext), len(key))):
        ct_idx = k_index(ciphertext[i])
        key_idx = k_index(key[i])
        pt_idx = (ct_idx - key_idx) % 26
        result.append(k_char(pt_idx))
    return ''.join(result)

def derive_key(ciphertext, plaintext):
    """Derive key: KEY[i] = (CT[i] - PT[i]) mod 26 in KRYPTOS alphabet."""
    result = []
    for i in range(min(len(ciphertext), len(plaintext))):
        ct_idx = k_index(ciphertext[i])
        pt_idx = k_index(plaintext[i])
        key_idx = (ct_idx - pt_idx) % 26
        result.append(k_char(key_idx))
    return ''.join(result)

# ============================================================
# ALSO TEST WITH STANDARD ALPHABET (in case KRYPTOS alphabet isn't used)
# ============================================================

STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
STD_INDEX = {ch: i for i, ch in enumerate(STANDARD_ALPHA)}

def std_derive_key(ciphertext, plaintext):
    """Derive key using standard alphabet."""
    result = []
    for i in range(min(len(ciphertext), len(plaintext))):
        ct_idx = STD_INDEX[ciphertext[i]]
        pt_idx = STD_INDEX[plaintext[i]]
        key_idx = (ct_idx - pt_idx) % 26
        result.append(STANDARD_ALPHA[key_idx])
    return ''.join(result)

def std_decrypt(ciphertext, key):
    """Decrypt using standard alphabet."""
    result = []
    for i in range(min(len(ciphertext), len(key))):
        ct_idx = STD_INDEX[ciphertext[i]]
        key_idx = STD_INDEX[key[i]]
        pt_idx = (ct_idx - key_idx) % 26
        result.append(STANDARD_ALPHA[pt_idx])
    return ''.join(result)

# ============================================================
# STEP 1: Derive running key at crib positions
# ============================================================

print("\n" + "=" * 80)
print("STEP 1: DERIVE RUNNING KEY AT CRIB POSITIONS")
print("=" * 80)

for crib_name, (crib_text, start, end) in [("EASTNORTHEAST", CRIB_ENE), ("BERLINCLOCK", CRIB_BC)]:
    ct_segment = K4_CT[start:end]
    print(f"\nCrib: {crib_text} at positions {start}-{end-1}")
    print(f"  Ciphertext:  {ct_segment}")
    print(f"  Plaintext:   {crib_text}")

    # KRYPTOS alphabet
    key_k = derive_key(ct_segment, crib_text)
    print(f"  Key (KRYPTOS alpha): {key_k}")

    # Standard alphabet
    key_s = std_derive_key(ct_segment, crib_text)
    print(f"  Key (Standard alpha): {key_s}")

# Derive full key fragments
ct_ene = K4_CT[21:34]
key_ene_k = derive_key(ct_ene, "EASTNORTHEAST")
key_ene_s = std_derive_key(ct_ene, "EASTNORTHEAST")

ct_bc = K4_CT[63:74]
key_bc_k = derive_key(ct_bc, "BERLINCLOCK")
key_bc_s = std_derive_key(ct_bc, "BERLINCLOCK")

print(f"\n--- Key fragment analysis ---")
print(f"Positions 21-33 key (KRYPTOS): '{key_ene_k}'")
print(f"Positions 21-33 key (Standard): '{key_ene_s}'")
print(f"Positions 63-73 key (KRYPTOS): '{key_bc_k}'")
print(f"Positions 63-73 key (Standard): '{key_bc_s}'")

# ============================================================
# STEP 2: Analyze if key fragments look like English
# ============================================================

print("\n" + "=" * 80)
print("STEP 2: DO THE KEY FRAGMENTS LOOK LIKE ENGLISH TEXT?")
print("=" * 80)

for label, key_frag in [
    ("Pos 21-33 KRYPTOS alpha", key_ene_k),
    ("Pos 21-33 Standard alpha", key_ene_s),
    ("Pos 63-73 KRYPTOS alpha", key_bc_k),
    ("Pos 63-73 Standard alpha", key_bc_s),
]:
    score = normalized_qg_score(key_frag)
    print(f"\n  {label}: '{key_frag}'")
    print(f"    Quadgram score (normalized): {score:.4f}")
    print(f"    (Typical English: -2.0 to -2.5, Random: -3.5 to -4.0)")

    # Check for common English fragments
    common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                    "HER", "WAS", "ONE", "OUR", "OUT", "HIS", "HAS", "HER",
                    "CAN", "HAD", "HIM", "ITS", "SAY", "SHE", "HOW", "MAN",
                    "OLD", "NEW", "NOW", "WAY", "MAY", "WHO", "DID", "GET",
                    "HIT", "LET", "PUT", "SAT", "TOP", "RED", "RUN", "OWN",
                    "AGE", "END", "BIG", "WHY", "TRY", "ASK", "MEN", "EAR",
                    "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM",
                    "THEY", "BEEN", "SAID", "EACH", "MAKE", "LIKE", "LONG",
                    "LOOK", "MANY", "SOME", "THEM", "THAN", "BEEN", "CALL",
                    "COME", "MADE", "FIND", "HERE", "KNOW", "TAKE", "WANT"]
    found = []
    for w in common_words:
        if w in key_frag:
            found.append(w)
    if found:
        print(f"    English words found: {found}")
    else:
        print(f"    No common English words found in fragment")

# ============================================================
# STEP 3: Also try Beaufort variant: KEY[i] = PT[i] - CT[i] mod 26
# and Minuend variant: PT[i] = KEY[i] - CT[i] mod 26
# ============================================================

print("\n" + "=" * 80)
print("STEP 2B: TRY BEAUFORT/VARIANT KEY DERIVATIONS")
print("=" * 80)

def beaufort_derive_key_k(ct, pt):
    """Beaufort: KEY = PT - CT mod 26 (KRYPTOS)"""
    return ''.join(k_char((k_index(pt[i]) - k_index(ct[i])) % 26) for i in range(len(pt)))

def minuend_derive_key_k(ct, pt):
    """Minuend variant: assumes PT = KEY - CT, so KEY = PT + CT mod 26"""
    return ''.join(k_char((k_index(pt[i]) + k_index(ct[i])) % 26) for i in range(len(pt)))

def beaufort_derive_key_s(ct, pt):
    """Beaufort: KEY = PT - CT mod 26 (Standard)"""
    return ''.join(STANDARD_ALPHA[(STD_INDEX[pt[i]] - STD_INDEX[ct[i]]) % 26] for i in range(len(pt)))

def minuend_derive_key_s(ct, pt):
    """Minuend: KEY = PT + CT mod 26 (Standard)"""
    return ''.join(STANDARD_ALPHA[(STD_INDEX[pt[i]] + STD_INDEX[ct[i]]) % 26] for i in range(len(pt)))

for variant_name, derive_func_k, derive_func_s in [
    ("Beaufort (KEY=PT-CT)", beaufort_derive_key_k, beaufort_derive_key_s),
    ("Minuend (KEY=PT+CT)", minuend_derive_key_k, minuend_derive_key_s),
]:
    print(f"\n--- {variant_name} ---")
    for crib_text, start, end in [CRIB_ENE, CRIB_BC]:
        ct_seg = K4_CT[start:end]
        key_k = derive_func_k(ct_seg, crib_text)
        key_s = derive_func_s(ct_seg, crib_text)
        score_k = normalized_qg_score(key_k)
        score_s = normalized_qg_score(key_s)
        print(f"  {crib_text}:")
        print(f"    KRYPTOS key: '{key_k}' (norm score: {score_k:.4f})")
        print(f"    Standard key: '{key_s}' (norm score: {score_s:.4f})")

# ============================================================
# STEP 3: EXTENDED SOURCE TEXTS
# ============================================================

print("\n" + "=" * 80)
print("STEP 3: PREPARE CANDIDATE SOURCE TEXTS")
print("=" * 80)

def clean_text(text):
    """Remove non-alpha characters and uppercase."""
    return ''.join(ch for ch in text.upper() if ch.isalpha())

# K1, K2, K3 plaintexts
K1_PLAIN = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUABOREOFIQLUSION"
K2_PLAIN = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESILANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIEDOUTTHEREXWHOISITREALLYBETTERIFYOUKNOWASKTHEKNOWINGLYISTHEREANYONEELSEINTHISROOM"
K3_PLAIN = "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENIGTHEHOLEALITTLEINSERTEDACANDLEANDPEABORNESINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"

# Howard Carter text (source for K3)
CARTER_TEXT = clean_text("At first I could see nothing the hot air escaping from the chamber caused the candle to flicker but presently as my eyes grew accustomed to the light details of the room within emerged from the mist strange animals statues and gold everywhere the glint of gold")

# Coordinates text
COORDS_TEXT = "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGRESEIGHTMINUTESFORTYFOURSECONDSWEST"

# Declaration of Independence (opening)
DECLARATION = clean_text("When in the Course of human events it becomes necessary for one people to dissolve the political bands which have connected them with another and to assume among the powers of the earth the separate and equal station to which the Laws of Nature and of Natures God entitle them a decent respect to the opinions of mankind requires that they should declare the causes which impel them to the separation We hold these truths to be self evident that all men are created equal that they are endowed by their Creator with certain unalienable Rights that among these are Life Liberty and the pursuit of Happiness")

# Gettysburg Address
GETTYSBURG = clean_text("Four score and seven years ago our fathers brought forth on this continent a new nation conceived in Liberty and dedicated to the proposition that all men are created equal Now we are engaged in a great civil war testing whether that nation or any nation so conceived and so dedicated can long endure We are met on a great battle field of that war We have come to dedicate a portion of that field as a final resting place for those who here gave their lives that that nation might live It is altogether fitting and proper that we should do this")

# Bible - Genesis opening
GENESIS = clean_text("In the beginning God created the heaven and the earth And the earth was without form and void and darkness was upon the face of the deep And the Spirit of God moved upon the face of the waters And God said Let there be light and there was light And God saw the light that it was good and God divided the light from the darkness And God called the light Day and the darkness he called Night And the evening and the morning were the first day")

# Shakespeare - Hamlet opening
HAMLET = clean_text("Who is there Nay answer me stand and unfold yourself Long live the king Bernardo He You come most carefully upon your hour Tis now struck twelve get thee to bed Francisco For this relief much thanks tis bitter cold and I am sick at heart Have you had quiet guard Not a mouse stirring")

# CIA-related text
CIA_TEXT1 = clean_text("The Central Intelligence Agency is a civilian foreign intelligence service of the federal government of the United States officially tasked with gathering processing and analyzing national security information from around the world primarily through the use of human intelligence")
CIA_TEXT2 = clean_text("Information is gathered and transmitted underground to an unknown location The earth magnetic field was used to hide the information They should know about this it is buried out there")
CIA_TEXT3 = clean_text("Between subtle shading and the absence of light lies the nuance of iqlusion It was totally invisible how is that possible They used the earths magnetic field")

# Berlin-related texts
BERLIN1 = clean_text("The time that the Berlin clock shows is the same as the clock in the cafeteria at Langley the time zone difference between Berlin and Washington is six hours")
BERLIN2 = clean_text("The Berlin Wall fell on November ninth nineteen eighty nine unifying East and West Germany after decades of division the cold war was effectively over")
BERLIN3 = clean_text("The Weltzeituhr or World Time Clock is a large turret like structure on Alexanderplatz in Berlin showing the time in major cities around the world")

# Kryptos dedication text / Sanborn quotes
SANBORN1 = clean_text("The sculpture contains a message in four parts three of which have been solved the fourth part known as K four remains one of the most famous unsolved codes in the world")
SANBORN2 = clean_text("It was meant to be a piece of art with a coded message that would take years to solve the work is a meditation on the nature of secrecy and the hidden world of intelligence")

# Edgar Allan Poe (CIA connection - Poe has a connection to cryptography)
POE_GOLD_BUG = clean_text("A good glass in the bishops hostel in the devils seat forty one degrees and thirteen minutes northeast and by north main branch seventh limb east side shoot from the left eye of the deaths head a bee line from the tree through the shot fifty feet out")

# Concatenation of K1+K2+K3 as one continuous text
K123_COMBINED = K1_PLAIN + K2_PLAIN + K3_PLAIN

# All candidate texts with names
CANDIDATE_TEXTS = [
    ("K1 plaintext", K1_PLAIN),
    ("K2 plaintext", K2_PLAIN),
    ("K3 plaintext", K3_PLAIN),
    ("K1+K2+K3 combined", K123_COMBINED),
    ("Howard Carter text", CARTER_TEXT),
    ("Coordinates text", COORDS_TEXT),
    ("Declaration of Independence", DECLARATION),
    ("Gettysburg Address", GETTYSBURG),
    ("Genesis (Bible)", GENESIS),
    ("Hamlet (Shakespeare)", HAMLET),
    ("CIA description 1", CIA_TEXT1),
    ("CIA description 2", CIA_TEXT2),
    ("CIA-Kryptos mashup", CIA_TEXT3),
    ("Berlin Clock text", BERLIN1),
    ("Berlin Wall text", BERLIN2),
    ("Weltzeituhr text", BERLIN3),
    ("Sanborn quote 1", SANBORN1),
    ("Sanborn quote 2", SANBORN2),
    ("Poe Gold Bug", POE_GOLD_BUG),
]

for name, text in CANDIDATE_TEXTS:
    print(f"  {name}: {len(text)} chars")

# ============================================================
# STEP 4: TEST EACH CANDIDATE TEXT AT ALL OFFSETS
# ============================================================

print("\n" + "=" * 80)
print("STEP 4: TEST CANDIDATE RUNNING KEYS AT ALL OFFSETS")
print("=" * 80)

def test_running_key_text(name, key_text, decrypt_func, derive_func, alpha_name):
    """
    Test a candidate running key text at all possible offsets.
    Returns list of (score, offset, plaintext, key_used) for promising results.
    """
    results = []
    ct_len = len(K4_CT)

    # Try every possible offset (where in the key_text we start reading for position 0)
    max_offset = len(key_text) - ct_len
    if max_offset < 0:
        # Key text too short to cover all 97 positions, but we can still try
        # where the key covers positions 0 through len(key_text)-1
        max_offset = 0

    for offset in range(max_offset + 1):
        key_segment = key_text[offset:offset + ct_len]
        if len(key_segment) < ct_len:
            continue

        plaintext = decrypt_func(K4_CT, key_segment)

        # Check if cribs appear at correct positions
        ene_match = plaintext[21:34] == "EASTNORTHEAST"
        bc_match = plaintext[63:74] == "BERLINCLOCK"

        if ene_match or bc_match:
            score = quadgram_score(plaintext)
            norm_score = score / len(plaintext)
            results.append((norm_score, offset, plaintext, key_segment, ene_match, bc_match))

    return results

def decrypt_kryptos(ct, key):
    """Decrypt using KRYPTOS alphabet."""
    return running_key_decrypt(ct, key)

def decrypt_standard(ct, key):
    """Decrypt using standard alphabet."""
    return std_decrypt(ct, key)

# Also test Beaufort variants
def beaufort_decrypt_k(ct, key):
    """Beaufort decrypt KRYPTOS: PT = KEY - CT mod 26"""
    return ''.join(k_char((k_index(key[i]) - k_index(ct[i])) % 26) for i in range(min(len(ct), len(key))))

def beaufort_decrypt_s(ct, key):
    """Beaufort decrypt Standard: PT = KEY - CT mod 26"""
    return ''.join(STANDARD_ALPHA[(STD_INDEX[key[i]] - STD_INDEX[ct[i]]) % 26] for i in range(min(len(ct), len(key))))

all_hits = []

for name, text in CANDIDATE_TEXTS:
    for alpha_name, decrypt_func in [
        ("KRYPTOS", decrypt_kryptos),
        ("Standard", decrypt_standard),
        ("Beaufort-K", beaufort_decrypt_k),
        ("Beaufort-S", beaufort_decrypt_s),
    ]:
        results = test_running_key_text(name, text, decrypt_func, None, alpha_name)
        for norm_score, offset, pt, key_seg, ene, bc in results:
            cribs = []
            if ene: cribs.append("ENE")
            if bc: cribs.append("BC")
            all_hits.append((norm_score, name, alpha_name, offset, pt, cribs))
            print(f"  HIT! {name} [{alpha_name}] offset={offset}: {'+'.join(cribs)} matched")
            print(f"    Plaintext: {pt}")
            print(f"    Score: {norm_score:.4f}")

if not all_hits:
    print("\n  No exact crib matches found with any candidate text.")
else:
    print(f"\n  Total hits: {len(all_hits)}")
    all_hits.sort(reverse=True)
    print("\n  Top 10 by score:")
    for i, (score, name, alpha, offset, pt, cribs) in enumerate(all_hits[:10]):
        print(f"  {i+1}. [{score:.4f}] {name} ({alpha}) offset={offset} cribs={cribs}")
        print(f"     PT: {pt}")

# ============================================================
# STEP 5: SEARCH FOR KEY PATTERNS IN ENGLISH TEXT
# ============================================================

print("\n" + "=" * 80)
print("STEP 5: SEARCH FOR DERIVED KEY FRAGMENTS IN SOURCE TEXTS")
print("=" * 80)

# For each alphabet variant and cipher variant, check if derived key fragments
# appear as substrings in any source text

all_key_fragments = {}
for variant_name, derive_func_k, derive_func_s in [
    ("Vigenere (KEY=CT-PT)", derive_key, std_derive_key),
    ("Beaufort (KEY=PT-CT)", beaufort_derive_key_k, beaufort_derive_key_s),
    ("Minuend (KEY=PT+CT)", minuend_derive_key_k, minuend_derive_key_s),
]:
    for alpha_name, derive_func in [("KRYPTOS", derive_func_k), ("Standard", derive_func_s)]:
        for crib_text, start, end in [CRIB_ENE, CRIB_BC]:
            ct_seg = K4_CT[start:end]
            key_frag = derive_func(ct_seg, crib_text)
            label = f"{variant_name} {alpha_name} {crib_text}"
            all_key_fragments[label] = (key_frag, start, end)

print("\nAll derived key fragments:")
for label, (frag, start, end) in sorted(all_key_fragments.items()):
    print(f"  {label}: '{frag}' (pos {start}-{end-1})")

print("\nSearching for key fragments in all source texts...")
for label, (frag, start, end) in all_key_fragments.items():
    for src_name, src_text in CANDIDATE_TEXTS:
        # Search for fragments of length >= 5
        for frag_len in range(len(frag), 4, -1):
            for frag_start in range(len(frag) - frag_len + 1):
                sub = frag[frag_start:frag_start + frag_len]
                idx = src_text.find(sub)
                if idx >= 0:
                    print(f"  MATCH! '{sub}' ({frag_len} chars) from [{label}]")
                    print(f"    Found in '{src_name}' at position {idx}")
                    print(f"    Context: ...{src_text[max(0,idx-10):idx+frag_len+10]}...")
                    break  # Found longest match, skip shorter ones for this start
            else:
                continue
            break  # Found a match, skip other start positions for this fragment length

# ============================================================
# STEP 6: BRUTE-FORCE APPROACH - Try all offset pairs
# ============================================================

print("\n" + "=" * 80)
print("STEP 6: WHAT IF KEY TEXT IS DIFFERENT FOR DIFFERENT POSITIONS?")
print("=" * 80)
print("(Testing: derive key at BOTH crib positions and look for coherent key)")

# Get the full 97-char key assuming both cribs are correct
# We know plaintext at positions 21-33 and 63-73
# Key at other positions is unknown

# Let's build the partial key
partial_key_k = [None] * 97
partial_key_s = [None] * 97

for crib_text, start, end in [CRIB_ENE, CRIB_BC]:
    ct_seg = K4_CT[start:end]
    key_k = derive_key(ct_seg, crib_text)
    key_s = std_derive_key(ct_seg, crib_text)
    for i, pos in enumerate(range(start, end)):
        partial_key_k[pos] = key_k[i]
        partial_key_s[pos] = key_s[i]

print("\nPartial key (KRYPTOS alphabet):")
key_str_k = ''.join(ch if ch else '.' for ch in partial_key_k)
print(f"  {key_str_k}")
print(f"  Position: {''.join(str(i%10) for i in range(97))}")

print("\nPartial key (Standard alphabet):")
key_str_s = ''.join(ch if ch else '.' for ch in partial_key_s)
print(f"  {key_str_s}")
print(f"  Position: {''.join(str(i%10) for i in range(97))}")

# Key at positions 21-33 and 63-73:
key_21_33_k = key_str_k[21:34]
key_63_73_k = key_str_k[63:74]
key_21_33_s = key_str_s[21:34]
key_63_73_s = key_str_s[63:74]

print(f"\nKey at pos 21-33 (KRYPTOS): '{key_21_33_k}'")
print(f"Key at pos 63-73 (KRYPTOS): '{key_63_73_k}'")
print(f"Key at pos 21-33 (Standard): '{key_21_33_s}'")
print(f"Key at pos 63-73 (Standard): '{key_63_73_s}'")

# Gap between the two known key segments: positions 34-62 = 29 chars unknown
# And we need the key to be continuous English text
gap = 63 - 34  # 29 chars
print(f"\nGap between known key segments: {gap} characters (positions 34-62)")
print("For a running key, the key from pos 21 to 73 should be 53 chars of continuous English.")
print(f"  Known: '{key_21_33_k}' + [29 unknown chars] + '{key_63_73_k}'")
print(f"  Known: '{key_21_33_s}' + [29 unknown chars] + '{key_63_73_s}'")

# ============================================================
# STEP 7: DEEPER ANALYSIS - Try with longer known English passages
# ============================================================

print("\n" + "=" * 80)
print("STEP 7: TRY LONGER ENGLISH PASSAGES AS RUNNING KEY")
print("=" * 80)

# Much larger set of English texts
EXTENDED_TEXTS = {
    "Moby Dick opening": clean_text("Call me Ishmael Some years ago never mind how long precisely having little or no money in my purse and nothing particular to interest me on shore I thought I would sail about a little and see the watery part of the world It is a way I have of driving off the spleen and regulating the circulation"),
    "Tale of Two Cities": clean_text("It was the best of times it was the worst of times it was the age of wisdom it was the age of foolishness it was the epoch of belief it was the epoch of incredulity it was the season of Light it was the season of Darkness it was the spring of hope it was the winter of despair"),
    "Pride and Prejudice": clean_text("It is a truth universally acknowledged that a single man in possession of a good fortune must be in want of a wife However little known the feelings or views of such a man may be on his first entering a neighbourhood this truth is so well fixed in the minds of the surrounding families"),
    "1984 Orwell": clean_text("It was a bright cold day in April and the clocks were striking thirteen Winston Smith his chin nuzzled into his breast in an effort to escape the vile wind slipped quickly through the glass doors of Victory Mansions though not quickly enough to prevent a swirl of gritty dust from entering along with him"),
    "US Constitution Preamble": clean_text("We the People of the United States in Order to form a more perfect Union establish Justice insure domestic Tranquility provide for the common defence promote the general Welfare and secure the Blessings of Liberty to ourselves and our Posterity do ordain and establish this Constitution for the United States of America"),
    "Psalms 23": clean_text("The Lord is my shepherd I shall not want He maketh me to lie down in green pastures he leadeth me beside the still waters He restoreth my soul he leadeth me in the paths of righteousness for his names sake Yea though I walk through the valley of the shadow of death I will fear no evil for thou art with me thy rod and thy staff they comfort me"),
    "Lorem CIA": clean_text("The agency was established in nineteen forty seven with the signing of the National Security Act by President Harry Truman It grew out of the wartime Office of Strategic Services and was intended to coordinate the nations intelligence activities and correlate evaluate and disseminate intelligence"),
    "Kryptos inscription full": clean_text("Between subtle shading and the absence of light lies the nuance of iqlusion It was totally invisible hows that possible they used the earths magnetic field the information was gathered and transmitted underground to an unknown location does Langley know about this they should its buried out there somewhere who is it really better if you know ask the knowingly is there anyone else in this room"),
    "Kryptos K3 Carter full": clean_text("Slowly desperately slowly the remains of passage debris that encumbered the lower part of the doorway was removed with trembling hands I made a tiny breach in the upper left hand corner and then widening the hole a little I inserted a candle and peered in the hot air escaping from the chamber caused the flame to flicker but presently details of the room within emerged from the mist Can you see anything"),
    "Berlin info": clean_text("Berlin is the capital and largest city of Germany by both area and population Its more than three point seven million inhabitants make it the European Unions most populous city according to population within city limits The city is also one of the states of Germany and is the third smallest state in the country by area"),
    "CIA motto/mission": clean_text("The work of a nation the center of intelligence we are the nations first line of defense we accomplish what others cannot accomplish and go where others cannot go the Central Intelligence Agency works every day to keep our nation safe we do this through collecting and analyzing intelligence and conducting covert action"),
    "Sanborn artist statement": clean_text("I wanted to create a piece that would be a paradox in terms of its function and its context here you have a sculpture that is about secrecy about the nature of hidden knowledge and about the power that comes from knowing things that others do not know yet it sits right here at the headquarters of the worlds most famous intelligence agency"),
    "JFK CIA speech": clean_text("The very word secrecy is repugnant in a free and open society and we are as a people inherently and historically opposed to secret societies to secret oaths and to secret proceedings we decided long ago that the dangers of excessive and unwarranted concealment of pertinent facts far outweighed the dangers which are cited to justify it"),
    "Kryptos poem Sanborn": clean_text("Virtually invisible how is that possible they used the earths magnetic field x the information was gathered and transmitted underground to an unknown location x does Langley know about this they should its buried out there somewhere x who is it"),
    "Numbers station": clean_text("Attention attention this is a numbers station broadcasting to all agents in the field please copy the following message carefully and confirm receipt the time is zero nine hundred hours Greenwich Mean Time all frequencies are being monitored"),
    "NATO alphabet": clean_text("Alpha Bravo Charlie Delta Echo Foxtrot Golf Hotel India Juliet Kilo Lima Mike November Oscar Papa Quebec Romeo Sierra Tango Uniform Victor Whiskey Xray Yankee Zulu"),
    "Longitude/Latitude": clean_text("Thirty eight degrees fifty seven minutes six point five seconds north seventy seven degrees eight minutes forty four seconds west coordinates of the Central Intelligence Agency headquarters in Langley Virginia United States of America near Washington District of Columbia"),
    "Cold War text": clean_text("During the Cold War the Berlin Wall divided the city of Berlin into East and West for twenty eight years from nineteen sixty one to nineteen eighty nine the wall served as a physical barrier between communist East Germany and democratic West Berlin it became a symbol of the Iron Curtain that separated the Eastern and Western blocs"),
}

# Add all extended texts to candidates
for name, text in EXTENDED_TEXTS.items():
    CANDIDATE_TEXTS.append((name, text))

# Now test ALL texts (including extended ones)
print(f"\nTesting {len(CANDIDATE_TEXTS)} candidate texts at all offsets...")

all_hits_extended = []
for name, text in CANDIDATE_TEXTS:
    if len(text) < 97:
        continue  # Too short to be a complete running key
    for alpha_name, decrypt_func in [
        ("KRYPTOS", decrypt_kryptos),
        ("Standard", decrypt_standard),
        ("Beaufort-K", beaufort_decrypt_k),
        ("Beaufort-S", beaufort_decrypt_s),
    ]:
        max_offset = len(text) - 97
        for offset in range(max_offset + 1):
            key_segment = text[offset:offset + 97]
            plaintext = decrypt_func(K4_CT, key_segment)

            ene_match = plaintext[21:34] == "EASTNORTHEAST"
            bc_match = plaintext[63:74] == "BERLINCLOCK"

            if ene_match or bc_match:
                score = normalized_qg_score(plaintext)
                cribs = []
                if ene_match: cribs.append("ENE")
                if bc_match: cribs.append("BC")
                all_hits_extended.append((score, name, alpha_name, offset, plaintext, cribs))

if all_hits_extended:
    all_hits_extended.sort(reverse=True)
    print(f"\n  Found {len(all_hits_extended)} hits!")
    print("\n  Top 20 by score:")
    for i, (score, name, alpha, offset, pt, cribs) in enumerate(all_hits_extended[:20]):
        print(f"  {i+1}. [{score:.4f}] {name} ({alpha}) offset={offset} cribs={cribs}")
        print(f"     PT: {pt}")
else:
    print("\n  No exact crib matches found with extended texts either.")

# ============================================================
# STEP 8: WHAT IF ONLY PARTIAL CRIBS MATCH?
# ============================================================

print("\n" + "=" * 80)
print("STEP 8: PARTIAL CRIB SCORING (relaxed matching)")
print("=" * 80)
print("Checking for near-misses where plaintext is CLOSE to cribs...")

best_partial = []
for name, text in CANDIDATE_TEXTS:
    if len(text) < 97:
        continue
    for alpha_name, decrypt_func in [
        ("KRYPTOS", decrypt_kryptos),
        ("Standard", decrypt_standard),
    ]:
        max_offset = len(text) - 97
        for offset in range(max_offset + 1):
            key_segment = text[offset:offset + 97]
            plaintext = decrypt_func(K4_CT, key_segment)

            # Count matching characters at crib positions
            ene_pt = plaintext[21:34]
            bc_pt = plaintext[63:74]
            ene_matches = sum(1 for a, b in zip(ene_pt, "EASTNORTHEAST") if a == b)
            bc_matches = sum(1 for a, b in zip(bc_pt, "BERLINCLOCK") if a == b)
            total_matches = ene_matches + bc_matches

            if total_matches >= 8:  # At least 8 out of 24 crib chars match
                score = normalized_qg_score(plaintext)
                best_partial.append((total_matches, score, name, alpha_name, offset, plaintext,
                                   ene_matches, bc_matches, ene_pt, bc_pt))

if best_partial:
    best_partial.sort(reverse=True)
    print(f"\n  Found {len(best_partial)} partial matches (>= 8 crib chars)")
    print("\n  Top 20:")
    for i, (tot, score, name, alpha, offset, pt, ene_m, bc_m, ene_pt, bc_pt) in enumerate(best_partial[:20]):
        print(f"  {i+1}. Crib matches: {tot}/24 (ENE={ene_m}/13, BC={bc_m}/11)")
        print(f"     {name} ({alpha}) offset={offset}, QG score={score:.4f}")
        print(f"     ENE area: {ene_pt} vs EASTNORTHEAST")
        print(f"     BC area:  {bc_pt} vs BERLINCLOCK")
        print(f"     Full PT: {pt}")
else:
    print("\n  No partial matches >= 8 chars found.")

# ============================================================
# STEP 9: CONSISTENCY CHECK - Can the key at both positions
#          come from continuous English?
# ============================================================

print("\n" + "=" * 80)
print("STEP 9: CONTINUOUS ENGLISH KEY PLAUSIBILITY CHECK")
print("=" * 80)

# The running key from position 21 to 73 = 53 characters
# We know chars at 21-33 and 63-73
# If this is from continuous English text, the whole 53-char span should be English

for alpha_label, key_21_33, key_63_73 in [
    ("KRYPTOS", key_21_33_k, key_63_73_k),
    ("Standard", key_21_33_s, key_63_73_s),
]:
    print(f"\n--- {alpha_label} alphabet ---")
    full_known = key_21_33 + "?" * 29 + key_63_73
    print(f"  Key pos 21-73: {full_known}")
    print(f"  Key pos 21-33: '{key_21_33}' - QG score: {normalized_qg_score(key_21_33):.4f}")
    print(f"  Key pos 63-73: '{key_63_73}' - QG score: {normalized_qg_score(key_63_73):.4f}")

    # For a running key cipher to work, BOTH fragments must be English
    # Let's check letter frequency of each fragment
    for pos_label, frag in [(f"pos 21-33", key_21_33), (f"pos 63-73", key_63_73)]:
        freq = Counter(frag)
        total = len(frag)
        # English letter frequency order: ETAOINSHRDLU
        print(f"  {pos_label} frequency: {dict(sorted(freq.items(), key=lambda x:-x[1]))}")

        # IC (Index of Coincidence)
        ic = sum(c * (c - 1) for c in freq.values()) / (total * (total - 1)) if total > 1 else 0
        print(f"  {pos_label} IC: {ic:.4f} (English ~0.065, Random ~0.038)")

# Also check Beaufort-derived keys
print("\n--- Beaufort variants ---")
for variant_name, derive_func_k, derive_func_s in [
    ("Beaufort (KEY=PT-CT)", beaufort_derive_key_k, beaufort_derive_key_s),
    ("Minuend (KEY=PT+CT)", minuend_derive_key_k, minuend_derive_key_s),
]:
    for alpha_name, derive_func in [("KRYPTOS", derive_func_k), ("Standard", derive_func_s)]:
        ct_ene_seg = K4_CT[21:34]
        ct_bc_seg = K4_CT[63:74]
        key_ene = derive_func(ct_ene_seg, "EASTNORTHEAST")
        key_bc = derive_func(ct_bc_seg, "BERLINCLOCK")
        score_ene = normalized_qg_score(key_ene)
        score_bc = normalized_qg_score(key_bc)
        combined_score = score_ene + score_bc  # rough combined metric
        print(f"  {variant_name} {alpha_name}:")
        print(f"    ENE key: '{key_ene}' (score: {score_ene:.4f})")
        print(f"    BC key:  '{key_bc}' (score: {score_bc:.4f})")
        print(f"    Combined: {combined_score:.4f}")

# ============================================================
# STEP 10: FIND THE BEST KEY FRAGMENT SCORES ACROSS ALL VARIANTS
# ============================================================

print("\n" + "=" * 80)
print("STEP 10: RANK ALL CIPHER/ALPHABET VARIANTS BY KEY ENGLISH-NESS")
print("=" * 80)

variant_scores = []

# Build comprehensive list of all possible cipher+alphabet combos
for cipher_name, derive_func_pairs in [
    ("Vigenere (KEY=CT-PT)", [(derive_key, "KRYPTOS"), (std_derive_key, "Standard")]),
    ("Beaufort (KEY=PT-CT)", [(beaufort_derive_key_k, "KRYPTOS"), (beaufort_derive_key_s, "Standard")]),
    ("Minuend (KEY=PT+CT)", [(minuend_derive_key_k, "KRYPTOS"), (minuend_derive_key_s, "Standard")]),
]:
    for derive_func, alpha_name in derive_func_pairs:
        ct_ene_seg = K4_CT[21:34]
        ct_bc_seg = K4_CT[63:74]
        key_ene = derive_func(ct_ene_seg, "EASTNORTHEAST")
        key_bc = derive_func(ct_bc_seg, "BERLINCLOCK")
        score_ene = normalized_qg_score(key_ene)
        score_bc = normalized_qg_score(key_bc)
        avg_score = (score_ene + score_bc) / 2
        variant_scores.append((avg_score, cipher_name, alpha_name, key_ene, key_bc, score_ene, score_bc))

variant_scores.sort(reverse=True)
print("\nRanked by average key fragment English-ness:")
for i, (avg, cipher, alpha, k_ene, k_bc, s_ene, s_bc) in enumerate(variant_scores):
    print(f"\n  {i+1}. [{avg:.4f}] {cipher} / {alpha}")
    print(f"     ENE key: '{k_ene}' (score: {s_ene:.4f})")
    print(f"     BC key:  '{k_bc}' (score: {s_bc:.4f})")

# ============================================================
# STEP 11: DICTIONARY SEARCH FOR KEY FRAGMENTS
# ============================================================

print("\n" + "=" * 80)
print("STEP 11: DICTIONARY WORD SEARCH IN KEY FRAGMENTS")
print("=" * 80)

# Load word list
try:
    with open("/home/user/polyalphabetic/OxfordEnglishWords.txt", "r") as f:
        wordlist = set(w.strip().upper() for w in f if len(w.strip()) >= 3)
    print(f"Loaded {len(wordlist)} words from dictionary")
except:
    wordlist = set()
    print("Could not load dictionary")

if wordlist:
    print("\nSearching for dictionary words in all key fragments...")
    for i, (avg, cipher, alpha, k_ene, k_bc, s_ene, s_bc) in enumerate(variant_scores):
        found_words_ene = []
        found_words_bc = []

        # Search for words in ENE key fragment
        for wlen in range(min(len(k_ene), 8), 2, -1):
            for start in range(len(k_ene) - wlen + 1):
                word = k_ene[start:start + wlen]
                if word in wordlist:
                    found_words_ene.append((word, start))

        # Search for words in BC key fragment
        for wlen in range(min(len(k_bc), 8), 2, -1):
            for start in range(len(k_bc) - wlen + 1):
                word = k_bc[start:start + wlen]
                if word in wordlist:
                    found_words_bc.append((word, start))

        if found_words_ene or found_words_bc:
            print(f"\n  {cipher} / {alpha}:")
            print(f"    ENE key '{k_ene}': {found_words_ene}")
            print(f"    BC key '{k_bc}': {found_words_bc}")

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

print("""
RUNNING KEY CIPHER ANALYSIS FOR K4:

1. We derived the running key characters at known crib positions for every
   combination of cipher variant (Vigenere/Beaufort/Minuend) and alphabet
   (KRYPTOS/Standard).

2. For a running key cipher to be the correct hypothesis, the derived key
   characters at crib positions MUST form recognizable English text (since
   the key IS a passage of text).

3. We tested {n_texts} candidate source texts at all possible offsets.

4. We ranked all cipher/alphabet variants by how "English-like" the derived
   key fragments are (using quadgram scoring).

KEY FINDINGS:
""".format(n_texts=len(CANDIDATE_TEXTS)))

best = variant_scores[0]
print(f"- Best variant: {best[1]} / {best[2]}")
print(f"  ENE key fragment: '{best[3]}' (score: {best[5]:.4f})")
print(f"  BC key fragment:  '{best[4]}' (score: {best[6]:.4f})")
print(f"  Average score: {best[0]:.4f}")
print(f"  (English text typically scores -2.0 to -2.5; random text scores -3.5 to -4.0)")

print(f"\n- Total exact crib matches from source texts: {len(all_hits) + len(all_hits_extended)}")
if best_partial:
    bp = best_partial[0]
    print(f"- Best partial match: {bp[0]}/24 crib chars, from '{bp[2]}' ({bp[3]})")
else:
    print(f"- No significant partial matches found")

print("""
INTERPRETATION:
- If key fragments score well (> -2.5), running key cipher is plausible
- If key fragments score poorly (< -3.0), running key cipher is unlikely
  (unless the key text is in a non-English language or encoded)
- The gap of 29 characters between known key positions makes it hard to
  verify continuity without knowing the actual source text
- None of the tested source texts produced exact crib matches, suggesting
  that if K4 IS a running key cipher, the source text is not among those tested
""")

print("Script complete.")
