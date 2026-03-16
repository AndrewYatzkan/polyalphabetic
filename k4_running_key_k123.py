#!/usr/bin/env python3
"""
Hypothesis: The Vigenere key for K4 comes from the K1-K3 solutions (plaintext or ciphertext).
Sanborn said "The codes of Kryptos from the morse code at the beginning through K5 are about delivering a message."

Tests all combinations of K1/K2/K3 plaintext and ciphertext as running keys for K4,
with both standard and KRYPTOS alphabets, using both Vigenere and Beaufort decryption.
"""

import math
import re

# ============================================================
# DATA
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# KRYPTOS alphabet (as on the sculpture)
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# K1 solved plaintext (63 chars)
K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSIONX"

# K2 solved plaintext
K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESTLANGUAGEMAKEANYSENSETOITXITWASHERELOVELYTHEYNEEDTOKNOWBUTWHOTHEYTRUSTCANTHEYORSHALLTHEYJUDGEORDERSTHELOOPETRIEDEVERYTHINGTHATWASDISCOVEREDWASUSEDAGAINSTTHEM"

# K3 solved plaintext (clean up spaces)
K3_PT = "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATLAYDISC OVEREDWASTHEFINALENTRYTOTHEOUTER CHAMBERWASABOUTTOBEUNLEADEDWITHTREMBLINGHANDSIMADESMALBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMIST"
K3_PT = K3_PT.replace(" ", "")  # Remove spaces

# K1-K3 ciphertext from the sculpture
K1_CT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K2_CT = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDF"
K3_CT = "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAABORETHNERTHEIVSREKNNEDNTOEAABORETHNERTHEGGEHEADNTEHENRNTHASEITARINNLIHANEALIREHTTENSARHOETHNERTIEIFFOESFNHIIENTFEHINAEDRIHNNETHNEOETOAOSDMHRITEGATIBTIMSEMSTRCFIRESFIMTITHGRSNQCYLEYQFHEEYTASQCOEDECAHMQNQRE"

# Clean up any non-alpha chars
K1_PT = re.sub(r'[^A-Z]', '', K1_PT.upper())
K2_PT = re.sub(r'[^A-Z]', '', K2_PT.upper())
K3_PT = re.sub(r'[^A-Z]', '', K3_PT.upper())
K1_CT = re.sub(r'[^A-Z]', '', K1_CT.upper())
K2_CT = re.sub(r'[^A-Z]', '', K2_CT.upper())
K3_CT = re.sub(r'[^A-Z]', '', K3_CT.upper())

K4_LEN = len(K4)

# Known cribs for K4
CRIBS = ["EASTNORTHEAST", "BERLINCLOCK", "NORTHEAST", "BERLIN", "CLOCK", "EAST", "NORTH"]

# ============================================================
# QUADGRAM SCORING
# ============================================================

print("Loading quadgrams...")
quadgrams = {}
total = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            quadgrams[gram] = count
            total += count

log_total = math.log10(total)
for gram in quadgrams:
    quadgrams[gram] = math.log10(quadgrams[gram]) - log_total
floor_score = math.log10(0.01) - log_total


def score_text(text):
    """Score text using quadgram frequencies. Returns score normalized per character."""
    s = 0
    n = len(text) - 3
    if n <= 0:
        return -999
    for i in range(n):
        quad = text[i:i+4]
        s += quadgrams.get(quad, floor_score)
    return s / n  # normalize per character for comparability


# ============================================================
# DECRYPTION FUNCTIONS
# ============================================================

def make_index_map(alphabet):
    """Map each letter to its index in the given alphabet."""
    return {ch: i for i, ch in enumerate(alphabet)}


def vigenere_decrypt_standard(ciphertext, key):
    """Standard Vigenere: PT = (CT - KEY) mod 26, using standard A-Z alphabet."""
    pt = []
    klen = len(key)
    for i, c in enumerate(ciphertext):
        c_idx = ord(c) - ord('A')
        k_idx = ord(key[i % klen]) - ord('A')
        p_idx = (c_idx - k_idx) % 26
        pt.append(chr(p_idx + ord('A')))
    return ''.join(pt)


def beaufort_decrypt_standard(ciphertext, key):
    """Beaufort: PT = (KEY - CT) mod 26, using standard A-Z alphabet."""
    pt = []
    klen = len(key)
    for i, c in enumerate(ciphertext):
        c_idx = ord(c) - ord('A')
        k_idx = ord(key[i % klen]) - ord('A')
        p_idx = (k_idx - c_idx) % 26
        pt.append(chr(p_idx + ord('A')))
    return ''.join(pt)


def vigenere_decrypt_kryptos(ciphertext, key, alphabet):
    """Vigenere decrypt using KRYPTOS alphabet: PT = alphabet[(idx_CT - idx_KEY) mod 26]."""
    idx_map = make_index_map(alphabet)
    pt = []
    klen = len(key)
    for i, c in enumerate(ciphertext):
        c_idx = idx_map.get(c)
        k_idx = idx_map.get(key[i % klen])
        if c_idx is None or k_idx is None:
            pt.append('?')
            continue
        p_idx = (c_idx - k_idx) % 26
        pt.append(alphabet[p_idx])
    return ''.join(pt)


def beaufort_decrypt_kryptos(ciphertext, key, alphabet):
    """Beaufort decrypt using KRYPTOS alphabet: PT = alphabet[(idx_KEY - idx_CT) mod 26]."""
    idx_map = make_index_map(alphabet)
    pt = []
    klen = len(key)
    for i, c in enumerate(ciphertext):
        c_idx = idx_map.get(c)
        k_idx = idx_map.get(key[i % klen])
        if c_idx is None or k_idx is None:
            pt.append('?')
            continue
        p_idx = (k_idx - c_idx) % 26
        pt.append(alphabet[p_idx])
    return ''.join(pt)


# ============================================================
# RESULT COLLECTION
# ============================================================

SCORE_THRESHOLD = -550  # per-character normalized score (quadgram log-prob / n)
# Note: typical English is around -2.5 to -3.0, random is around -4.5

results = []


def check_result(plaintext, description, method, alpha_name, offset):
    """Check a decryption result for cribs and score."""
    sc = score_text(plaintext)
    found_cribs = [c for c in CRIBS if c in plaintext]

    # Store result if it passes threshold or has cribs
    if found_cribs or sc > (SCORE_THRESHOLD / K4_LEN):
        results.append({
            'plaintext': plaintext,
            'description': description,
            'method': method,
            'alphabet': alpha_name,
            'offset': offset,
            'score': sc,
            'cribs': found_cribs
        })


def try_all_methods(ciphertext, key, description, offset):
    """Try Vigenere and Beaufort with both alphabets."""
    # Standard alphabet - Vigenere
    pt = vigenere_decrypt_standard(ciphertext, key)
    check_result(pt, description, "Vigenere", "Standard", offset)

    # Standard alphabet - Beaufort
    pt = beaufort_decrypt_standard(ciphertext, key)
    check_result(pt, description, "Beaufort", "Standard", offset)

    # KRYPTOS alphabet - Vigenere
    pt = vigenere_decrypt_kryptos(ciphertext, key, KRYPTOS_ALPHA)
    check_result(pt, description, "Vigenere", "KRYPTOS", offset)

    # KRYPTOS alphabet - Beaufort
    pt = beaufort_decrypt_kryptos(ciphertext, key, KRYPTOS_ALPHA)
    check_result(pt, description, "Beaufort", "KRYPTOS", offset)


# ============================================================
# HELPER: Build running key from a source text at an offset
# ============================================================

def build_key_cycling(source, offset, length):
    """Build a key of given length from source starting at offset, cycling if needed."""
    slen = len(source)
    key = []
    for i in range(length):
        key.append(source[(offset + i) % slen])
    return ''.join(key)


def build_key_substring(source, offset, length):
    """Build a key of given length from source starting at offset, no cycling (returns None if too short)."""
    if offset + length > len(source):
        return None
    return source[offset:offset + length]


# ============================================================
# TEST 1: K1 PLAINTEXT AS KEY (with offsets, cycling)
# ============================================================

print(f"\n{'='*80}")
print("TEST 1: K1 PLAINTEXT AS KEY (cycling, all offsets)")
print(f"K1_PT length: {len(K1_PT)}, K4 length: {K4_LEN}")
print(f"{'='*80}")

for offset in range(len(K1_PT)):
    key = build_key_cycling(K1_PT, offset, K4_LEN)
    try_all_methods(K4, key, f"K1_PT cycling", offset)

print(f"  Completed {len(K1_PT)} offsets.")


# ============================================================
# TEST 2: K2 PLAINTEXT AS KEY (with offsets)
# ============================================================

print(f"\n{'='*80}")
print("TEST 2: K2 PLAINTEXT AS KEY (substring + cycling, all offsets)")
print(f"K2_PT length: {len(K2_PT)}, K4 length: {K4_LEN}")
print(f"{'='*80}")

# Substring (no cycling) for offsets where there's enough text
for offset in range(max(1, len(K2_PT) - K4_LEN + 1)):
    key = build_key_substring(K2_PT, offset, K4_LEN)
    if key:
        try_all_methods(K4, key, f"K2_PT substring", offset)

# Also try cycling
for offset in range(len(K2_PT)):
    key = build_key_cycling(K2_PT, offset, K4_LEN)
    try_all_methods(K4, key, f"K2_PT cycling", offset)

print(f"  Completed all offsets.")


# ============================================================
# TEST 3: K3 PLAINTEXT AS KEY (with offsets)
# ============================================================

print(f"\n{'='*80}")
print("TEST 3: K3 PLAINTEXT AS KEY (substring + cycling, all offsets)")
print(f"K3_PT length: {len(K3_PT)}, K4 length: {K4_LEN}")
print(f"{'='*80}")

# Substring
for offset in range(max(1, len(K3_PT) - K4_LEN + 1)):
    key = build_key_substring(K3_PT, offset, K4_LEN)
    if key:
        try_all_methods(K4, key, f"K3_PT substring", offset)

# Cycling
for offset in range(len(K3_PT)):
    key = build_key_cycling(K3_PT, offset, K4_LEN)
    try_all_methods(K4, key, f"K3_PT cycling", offset)

print(f"  Completed all offsets.")


# ============================================================
# TEST 4: CONCATENATED K1+K2+K3 AS KEY
# ============================================================

print(f"\n{'='*80}")
print("TEST 4: CONCATENATED PLAINTEXTS AS KEY")
print(f"{'='*80}")

concat_pt = K1_PT + K2_PT + K3_PT
print(f"Concatenated PT length: {len(concat_pt)}")

for offset in range(len(concat_pt)):
    key = build_key_cycling(concat_pt, offset, K4_LEN)
    try_all_methods(K4, key, f"K1+K2+K3 PT concat cycling", offset)

# Also try K2+K1+K3, K3+K2+K1, etc.
orderings = [
    ("K1+K2+K3", K1_PT + K2_PT + K3_PT),
    ("K2+K1+K3", K2_PT + K1_PT + K3_PT),
    ("K3+K2+K1", K3_PT + K2_PT + K1_PT),
    ("K1+K3+K2", K1_PT + K3_PT + K2_PT),
    ("K2+K3+K1", K2_PT + K3_PT + K1_PT),
    ("K3+K1+K2", K3_PT + K1_PT + K2_PT),
]

for name, concat in orderings:
    if concat == K1_PT + K2_PT + K3_PT:
        continue  # already done above
    for offset in range(len(concat)):
        key = build_key_cycling(concat, offset, K4_LEN)
        try_all_methods(K4, key, f"{name} PT concat cycling", offset)

print(f"  Completed all orderings and offsets.")

# Concatenated ciphertext too
concat_ct_orderings = [
    ("K1+K2+K3 CT", K1_CT + K2_CT + K3_CT),
    ("K2+K1+K3 CT", K2_CT + K1_CT + K3_CT),
    ("K3+K2+K1 CT", K3_CT + K2_CT + K1_CT),
    ("K1+K3+K2 CT", K1_CT + K3_CT + K2_CT),
]

for name, concat in concat_ct_orderings:
    for offset in range(len(concat)):
        key = build_key_cycling(concat, offset, K4_LEN)
        try_all_methods(K4, key, f"{name} concat cycling", offset)

print(f"  Completed CT concatenation orderings.")


# ============================================================
# TEST 5: K1-K3 CIPHERTEXT AS KEY
# ============================================================

print(f"\n{'='*80}")
print("TEST 5: K1-K3 CIPHERTEXT AS KEY (individual)")
print(f"K1_CT length: {len(K1_CT)}, K2_CT length: {len(K2_CT)}, K3_CT length: {len(K3_CT)}")
print(f"{'='*80}")

# K1 CT
for offset in range(len(K1_CT)):
    key = build_key_cycling(K1_CT, offset, K4_LEN)
    try_all_methods(K4, key, f"K1_CT cycling", offset)

# K2 CT - substring
for offset in range(max(1, len(K2_CT) - K4_LEN + 1)):
    key = build_key_substring(K2_CT, offset, K4_LEN)
    if key:
        try_all_methods(K4, key, f"K2_CT substring", offset)

# K2 CT - cycling
for offset in range(len(K2_CT)):
    key = build_key_cycling(K2_CT, offset, K4_LEN)
    try_all_methods(K4, key, f"K2_CT cycling", offset)

# K3 CT - substring
for offset in range(max(1, len(K3_CT) - K4_LEN + 1)):
    key = build_key_substring(K3_CT, offset, K4_LEN)
    if key:
        try_all_methods(K4, key, f"K3_CT substring", offset)

# K3 CT - cycling
for offset in range(len(K3_CT)):
    key = build_key_cycling(K3_CT, offset, K4_LEN)
    try_all_methods(K4, key, f"K3_CT cycling", offset)

print(f"  Completed all CT offsets.")


# ============================================================
# TEST 6: REVERSED K1-K3 AS KEY
# ============================================================

print(f"\n{'='*80}")
print("TEST 6: REVERSED K1-K3 AS KEY (plaintext and ciphertext)")
print(f"{'='*80}")

reversed_sources = [
    ("K1_PT reversed", K1_PT[::-1]),
    ("K2_PT reversed", K2_PT[::-1]),
    ("K3_PT reversed", K3_PT[::-1]),
    ("K1_CT reversed", K1_CT[::-1]),
    ("K2_CT reversed", K2_CT[::-1]),
    ("K3_CT reversed", K3_CT[::-1]),
    ("K1+K2+K3 PT reversed", (K1_PT + K2_PT + K3_PT)[::-1]),
    ("K1+K2+K3 CT reversed", (K1_CT + K2_CT + K3_CT)[::-1]),
]

for name, source in reversed_sources:
    for offset in range(len(source)):
        key = build_key_cycling(source, offset, K4_LEN)
        try_all_methods(K4, key, name, offset)

print(f"  Completed all reversed key tests.")


# ============================================================
# ALSO TRY: K4 reversed as ciphertext
# ============================================================

print(f"\n{'='*80}")
print("BONUS: K4 REVERSED as ciphertext against all keys")
print(f"{'='*80}")

K4_REV = K4[::-1]

all_sources = [
    ("K1_PT", K1_PT),
    ("K2_PT", K2_PT),
    ("K3_PT", K3_PT),
    ("K1_CT", K1_CT),
    ("K2_CT", K2_CT),
    ("K3_CT", K3_CT),
    ("K1+K2+K3 PT", K1_PT + K2_PT + K3_PT),
    ("K1+K2+K3 CT", K1_CT + K2_CT + K3_CT),
]

for name, source in all_sources:
    for offset in range(len(source)):
        key = build_key_cycling(source, offset, K4_LEN)
        # Standard Vigenere
        pt = vigenere_decrypt_standard(K4_REV, key)
        check_result(pt, f"K4_REV + {name}", "Vigenere", "Standard", offset)
        # Standard Beaufort
        pt = beaufort_decrypt_standard(K4_REV, key)
        check_result(pt, f"K4_REV + {name}", "Beaufort", "Standard", offset)
        # KRYPTOS Vigenere
        pt = vigenere_decrypt_kryptos(K4_REV, key, KRYPTOS_ALPHA)
        check_result(pt, f"K4_REV + {name}", "Vigenere", "KRYPTOS", offset)
        # KRYPTOS Beaufort
        pt = beaufort_decrypt_kryptos(K4_REV, key, KRYPTOS_ALPHA)
        check_result(pt, f"K4_REV + {name}", "Beaufort", "KRYPTOS", offset)

print(f"  Completed K4 reversed tests.")


# ============================================================
# PRINT RESULTS
# ============================================================

print(f"\n{'='*80}")
print(f"RESULTS SUMMARY")
print(f"{'='*80}")
print(f"Total configurations tested: many thousands")
print(f"Results passing threshold (score > {SCORE_THRESHOLD / K4_LEN:.4f} per char) or containing cribs: {len(results)}")

if not results:
    print("\nNo results found matching criteria.")
    print("Adjusting threshold to show top results...")

    # Collect ALL results to find the best ones
    # Re-run a quick sample to get baseline scores
    print("\nSampling baseline scores for reference:")
    sample_scores = []
    for offset in range(0, len(K1_PT), 10):
        key = build_key_cycling(K1_PT, offset, K4_LEN)
        pt = vigenere_decrypt_standard(K4, key)
        sample_scores.append((score_text(pt), pt, f"K1_PT Vig Std off={offset}"))
    for offset in range(0, len(K2_PT), 30):
        key = build_key_cycling(K2_PT, offset, K4_LEN)
        pt = vigenere_decrypt_standard(K4, key)
        sample_scores.append((score_text(pt), pt, f"K2_PT Vig Std off={offset}"))
    for offset in range(0, len(K3_PT), 30):
        key = build_key_cycling(K3_PT, offset, K4_LEN)
        pt = vigenere_decrypt_standard(K4, key)
        sample_scores.append((score_text(pt), pt, f"K3_PT Vig Std off={offset}"))

    sample_scores.sort(key=lambda x: x[0], reverse=True)
    print(f"\nTop 5 sampled scores:")
    for sc, pt, desc in sample_scores[:5]:
        print(f"  Score: {sc:.4f}  {desc}")
        print(f"  PT: {pt}")

# Sort results by score (best first)
results.sort(key=lambda r: r['score'], reverse=True)

# Print top results
print(f"\n{'='*80}")
print("TOP RESULTS (sorted by quadgram score, best first):")
print(f"{'='*80}")

# Print results with cribs first
crib_results = [r for r in results if r['cribs']]
if crib_results:
    print(f"\n*** RESULTS WITH CRIB MATCHES ({len(crib_results)}): ***")
    for r in crib_results:
        print(f"\n  Description: {r['description']}")
        print(f"  Method: {r['method']}  Alphabet: {r['alphabet']}  Offset: {r['offset']}")
        print(f"  Score: {r['score']:.4f}")
        print(f"  Cribs found: {r['cribs']}")
        print(f"  Plaintext: {r['plaintext']}")

# Print top scoring results
top_n = min(50, len(results))
if top_n > 0:
    print(f"\n--- Top {top_n} by score: ---")
    for i, r in enumerate(results[:top_n]):
        crib_str = f" CRIBS: {r['cribs']}" if r['cribs'] else ""
        print(f"\n  #{i+1} Score: {r['score']:.4f}  {r['description']} off={r['offset']} "
              f"[{r['method']}/{r['alphabet']}]{crib_str}")
        print(f"       PT: {r['plaintext']}")

# ============================================================
# ADDITIONAL ANALYSIS: Show the actual key letters being used
# for the top results
# ============================================================

if results:
    print(f"\n{'='*80}")
    print("KEY ANALYSIS FOR TOP 5:")
    print(f"{'='*80}")
    for i, r in enumerate(results[:5]):
        print(f"\n  #{i+1}: {r['description']} off={r['offset']} [{r['method']}/{r['alphabet']}]")
        print(f"  Score: {r['score']:.4f}")
        print(f"  PT: {r['plaintext']}")

        # Reconstruct the key
        desc = r['description']
        offset = r['offset']

        # Try to identify source
        if 'K1_PT' in desc and 'cycling' in desc:
            key = build_key_cycling(K1_PT, offset, K4_LEN)
        elif 'K2_PT' in desc and 'cycling' in desc:
            key = build_key_cycling(K2_PT, offset, K4_LEN)
        elif 'K3_PT' in desc and 'cycling' in desc:
            key = build_key_cycling(K3_PT, offset, K4_LEN)
        elif 'K1_CT' in desc and 'cycling' in desc:
            key = build_key_cycling(K1_CT, offset, K4_LEN)
        elif 'K2_CT' in desc and 'cycling' in desc:
            key = build_key_cycling(K2_CT, offset, K4_LEN)
        elif 'K3_CT' in desc and 'cycling' in desc:
            key = build_key_cycling(K3_CT, offset, K4_LEN)
        else:
            key = "N/A (complex source)"

        if key != "N/A (complex source)":
            print(f"  KEY: {key}")


# ============================================================
# FINAL STATISTICS
# ============================================================

print(f"\n{'='*80}")
print("FINAL STATISTICS")
print(f"{'='*80}")
print(f"K4 ciphertext: {K4}")
print(f"K4 length: {K4_LEN}")
print(f"K1_PT length: {len(K1_PT)}")
print(f"K2_PT length: {len(K2_PT)}")
print(f"K3_PT length: {len(K3_PT)}")
print(f"K1_CT length: {len(K1_CT)}")
print(f"K2_CT length: {len(K2_CT)}")
print(f"K3_CT length: {len(K3_CT)}")
print(f"Total results passing threshold: {len(results)}")
print(f"Results with crib matches: {len([r for r in results if r['cribs']])}")
print(f"Score threshold used: {SCORE_THRESHOLD / K4_LEN:.4f} per character")

# Show the known partial solution for reference
print(f"\nKnown K4 partial solution (positions 64-74): EASTNORTHEAST")
print(f"Known K4 partial solution (positions 22-32): BERLINCLOCK")
print(f"\nK4 positions 64-74 ciphertext: {K4[64:77]}")
print(f"K4 positions 22-32 ciphertext: {K4[22:33]}")

# For the known cribs, what key letters would be needed?
print(f"\n{'='*80}")
print("REQUIRED KEY LETTERS FOR KNOWN CRIBS (Standard Vigenere):")
print(f"{'='*80}")

print("\nFor BERLINCLOCK at position 22:")
for i, (c, p) in enumerate(zip(K4[22:33], "BERLINCLOCK")):
    k = (ord(c) - ord(p)) % 26
    print(f"  pos {22+i}: CT={c} PT={p} => KEY={chr(k + ord('A'))}")

print("\nFor EASTNORTHEAST at position 64:")
for i, (c, p) in enumerate(zip(K4[64:77], "EASTNORTHEAST")):
    k = (ord(c) - ord(p)) % 26
    print(f"  pos {64+i}: CT={c} PT={p} => KEY={chr(k + ord('A'))}")

# Check if these required key letters appear in any K1-K3 source at the right offsets
print(f"\n{'='*80}")
print("CHECKING IF REQUIRED KEY LETTERS MATCH K1-K3 SOURCES:")
print(f"{'='*80}")

# Required key for BERLINCLOCK at pos 22-32
berlin_key = ''.join(chr((ord(c) - ord(p)) % 26 + ord('A')) for c, p in zip(K4[22:33], "BERLINCLOCK"))
# Required key for EASTNORTHEAST at pos 64-76
east_key = ''.join(chr((ord(c) - ord(p)) % 26 + ord('A')) for c, p in zip(K4[64:77], "EASTNORTHEAST"))

print(f"\nRequired key at pos 22-32 (for BERLINCLOCK): {berlin_key}")
print(f"Required key at pos 64-76 (for EASTNORTHEAST): {east_key}")

# Search for these key fragments in all sources
all_key_sources = [
    ("K1_PT", K1_PT),
    ("K2_PT", K2_PT),
    ("K3_PT", K3_PT),
    ("K1_CT", K1_CT),
    ("K2_CT", K2_CT),
    ("K3_CT", K3_CT),
    ("K1+K2+K3 PT", K1_PT + K2_PT + K3_PT),
    ("K1+K2+K3 CT", K1_CT + K2_CT + K3_CT),
]

print(f"\nSearching for '{berlin_key}' in sources (exact match):")
for name, src in all_key_sources:
    idx = src.find(berlin_key)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}!")
        # Check what offset would make this align to K4 position 22
        required_offset = idx - 22
        print(f"    This means offset = {required_offset} for this source")

print(f"\nSearching for '{east_key}' in sources (exact match):")
for name, src in all_key_sources:
    idx = src.find(east_key)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}!")
        required_offset = idx - 64
        print(f"    This means offset = {required_offset} for this source")

# Also check with KRYPTOS alphabet
print(f"\nRequired key at pos 22-32 (for BERLINCLOCK, KRYPTOS alphabet):")
kryp_idx = make_index_map(KRYPTOS_ALPHA)
berlin_key_k = ''.join(KRYPTOS_ALPHA[(kryp_idx[c] - kryp_idx[p]) % 26] for c, p in zip(K4[22:33], "BERLINCLOCK"))
east_key_k = ''.join(KRYPTOS_ALPHA[(kryp_idx[c] - kryp_idx[p]) % 26] for c, p in zip(K4[64:77], "EASTNORTHEAST"))
print(f"  KRYPTOS alphabet key for BERLINCLOCK: {berlin_key_k}")
print(f"  KRYPTOS alphabet key for EASTNORTHEAST: {east_key_k}")

print(f"\nSearching for '{berlin_key_k}' (KRYPTOS) in sources:")
for name, src in all_key_sources:
    idx = src.find(berlin_key_k)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 22})")

print(f"\nSearching for '{east_key_k}' (KRYPTOS) in sources:")
for name, src in all_key_sources:
    idx = src.find(east_key_k)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 64})")

# Beaufort key check
print(f"\nRequired key (Beaufort, standard): PT = (KEY - CT) mod 26")
berlin_key_b = ''.join(chr((ord(p) + ord(c) - 2*ord('A')) % 26 + ord('A')) for c, p in zip(K4[22:33], "BERLINCLOCK"))
east_key_b = ''.join(chr((ord(p) + ord(c) - 2*ord('A')) % 26 + ord('A')) for c, p in zip(K4[64:77], "EASTNORTHEAST"))
print(f"  Beaufort key for BERLINCLOCK at pos 22: {berlin_key_b}")
print(f"  Beaufort key for EASTNORTHEAST at pos 64: {east_key_b}")

print(f"\nSearching for '{berlin_key_b}' (Beaufort) in sources:")
for name, src in all_key_sources:
    idx = src.find(berlin_key_b)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 22})")

print(f"\nSearching for '{east_key_b}' (Beaufort) in sources:")
for name, src in all_key_sources:
    idx = src.find(east_key_b)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 64})")

# Beaufort with KRYPTOS alphabet
berlin_key_bk = ''.join(KRYPTOS_ALPHA[(kryp_idx[p] + kryp_idx[c]) % 26] for c, p in zip(K4[22:33], "BERLINCLOCK"))
east_key_bk = ''.join(KRYPTOS_ALPHA[(kryp_idx[p] + kryp_idx[c]) % 26] for c, p in zip(K4[64:77], "EASTNORTHEAST"))
print(f"\n  Beaufort KRYPTOS key for BERLINCLOCK: {berlin_key_bk}")
print(f"  Beaufort KRYPTOS key for EASTNORTHEAST: {east_key_bk}")

print(f"\nSearching for '{berlin_key_bk}' (Beaufort KRYPTOS) in sources:")
for name, src in all_key_sources:
    idx = src.find(berlin_key_bk)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 22})")

print(f"\nSearching for '{east_key_bk}' (Beaufort KRYPTOS) in sources:")
for name, src in all_key_sources:
    idx = src.find(east_key_bk)
    if idx >= 0:
        print(f"  FOUND in {name} at position {idx}! (offset = {idx - 64})")

print(f"\n{'='*80}")
print("ANALYSIS COMPLETE")
print(f"{'='*80}")
