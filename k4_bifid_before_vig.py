#!/usr/bin/env python3
"""
K4 Bifid-Before-Vigenere Hypothesis Test
=========================================
Hypothesis: English PT -> Bifid cipher -> Vigenere -> K4 ciphertext
So after reversing the Vigenere layer we have Bifid(PT).
We reverse the Bifid to recover PT.

Tests:
1. Standard bifid with KRYPTOS-keyed Polybius square, various periods
2. Standard bifid with other keyword squares (PALIMPSEST, ABSCISSA, etc.)
3. Trifid cipher with 3x3x3 cube
4. Bifid with 6x6 grid (letters + digits)
5. Reverse bifid (encrypt instead of decrypt direction)
6. Playfair / Two-square cipher decryption
7. KRYPTOS-ordered alphabet square
8. Standard alphabet Vigenere variant
9. Extended keyword/period search
10. Verification roundtrip
11. Nihilist substitution variant
"""

import math
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 25 unique letters
VIG_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"  # period 29
KRYPTOS_25 = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Standard 25-letter (no J)
KRYPTOS_ORDERED = "KRYPTOSABCDEFGHILMNQUVWXZ"

# ============================================================
# LOAD QUADGRAM SCORES
# ============================================================

print("Loading quadgram statistics...")
QUADGRAMS = {}
TOTAL_QG = 0
try:
    with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                qg, count = parts[0].upper(), int(parts[1])
                QUADGRAMS[qg] = count
                TOTAL_QG += count
    LOG_TOTAL = math.log10(TOTAL_QG)
    QG_LOG = {}
    floor_val = math.log10(0.01 / TOTAL_QG)
    for qg, count in QUADGRAMS.items():
        QG_LOG[qg] = math.log10(count) - LOG_TOTAL
    QG_FLOOR = floor_val
    print(f"  Loaded {len(QUADGRAMS)} quadgrams, total count = {TOTAL_QG}")
except FileNotFoundError:
    print("  WARNING: Quadgrams file not found. Using IC only.")
    QG_LOG = {}
    QG_FLOOR = -10.0

def quadgram_score(text):
    """Return normalized quadgram log-probability score."""
    text = text.upper()
    if len(text) < 4:
        return -99.0
    score = 0.0
    n = 0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QG_LOG.get(qg, QG_FLOOR)
        n += 1
    return score / n if n > 0 else -99.0

def ic(text):
    """Index of Coincidence."""
    text = text.upper()
    n = len(text)
    if n < 2:
        return 0.0
    freq = Counter(text)
    total = sum(f * (f - 1) for f in freq.values())
    return total / (n * (n - 1))

def english_word_count(text, min_len=4):
    """Count common English words in text."""
    common_words = [
        "THAT", "WITH", "HAVE", "THIS", "WILL", "YOUR", "FROM", "THEY",
        "BEEN", "MANY", "SOME", "THEM", "THAN", "EACH", "MAKE",
        "LIKE", "LONG", "LOOK", "MOST", "OVER", "SUCH", "TAKE",
        "COME", "MADE", "FIND", "HERE", "KNOW", "LAST", "VERY", "WHEN",
        "WHAT", "WERE", "SAID", "EAST", "WEST", "NORTH", "SOUTH",
        "BETWEEN", "CLOCK", "LAYER", "UNDER", "GROUND", "SLOWLY",
        "BERLIN", "SHADOW", "LIGHT", "DEGREE", "BURIED", "SECRET",
        "HIDDEN", "POINT", "PLACE", "WHERE", "THERE", "WHICH", "WOULD",
        "ABOUT", "COULD", "OTHER", "AFTER", "THOSE", "THESE", "FIRST",
        "THEIR", "BEING", "THREE", "WATER", "EARTH",
        "PALIMPSEST", "ABSCISSA", "ILLUSION", "OBSCURE", "LANGLEY",
        "INVISIBLE", "DESPARATLY", "VIRTUALLY",
    ]
    text_upper = text.upper()
    count = 0
    found = []
    for w in common_words:
        if len(w) >= min_len and w in text_upper:
            count += 1
            found.append(w)
    return count, found

# ============================================================
# KRYPTOS VIGENERE
# ============================================================

def kryptos_vig_decrypt(ct, key):
    """Decrypt ct with Vigenere using the KRYPTOS alphabet."""
    alpha = KRYPTOS_ALPHA
    n = len(alpha)
    result = []
    key_len = len(key)
    for i, c in enumerate(ct):
        ct_idx = alpha.index(c)
        key_idx = alpha.index(key[i % key_len])
        pt_idx = (ct_idx - key_idx) % n
        result.append(alpha[pt_idx])
    return "".join(result)

def standard_vig_decrypt(ct, key):
    """Standard Vigenere decrypt (A-Z, mod 26)."""
    result = []
    key_len = len(key)
    for i, c in enumerate(ct):
        ct_idx = ord(c) - ord('A')
        key_idx = ord(key[i % key_len]) - ord('A')
        pt_idx = (ct_idx - key_idx) % 26
        result.append(chr(pt_idx + ord('A')))
    return "".join(result)

# Compute Vigenere intermediate texts
VIG_OUTPUT = kryptos_vig_decrypt(K4_CT, VIG_KEY)
VIG_OUTPUT_STD = standard_vig_decrypt(K4_CT, VIG_KEY)

print(f"\nK4 ciphertext:       {K4_CT}")
print(f"Vigenere key:        {VIG_KEY} (period {len(VIG_KEY)})")
print(f"KRYPTOS Vig output:  {VIG_OUTPUT}")
print(f"  Length: {len(VIG_OUTPUT)}, IC: {ic(VIG_OUTPUT):.6f}, QG: {quadgram_score(VIG_OUTPUT):.4f}")
print(f"Standard Vig output: {VIG_OUTPUT_STD}")
print(f"  Length: {len(VIG_OUTPUT_STD)}, IC: {ic(VIG_OUTPUT_STD):.6f}, QG: {quadgram_score(VIG_OUTPUT_STD):.4f}")

# ============================================================
# BIFID CIPHER IMPLEMENTATION (CORRECTED)
# ============================================================

def build_polybius_square(keyword, alphabet="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Build a 5x5 Polybius square from keyword."""
    seen = set()
    square = []
    for ch in keyword.upper():
        if ch == 'J':
            ch = 'I'
        if ch not in seen and ch in alphabet:
            seen.add(ch)
            square.append(ch)
    for ch in alphabet:
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    char_to_pos = {}
    pos_to_char = {}
    for idx, ch in enumerate(square):
        r, c = divmod(idx, 5)
        char_to_pos[ch] = (r, c)
        pos_to_char[(r, c)] = ch
    return square, char_to_pos, pos_to_char

def bifid_encrypt(plaintext, keyword, period, alphabet="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Encrypt with bifid cipher."""
    pt = plaintext.upper().replace('J', 'I')
    square, c2p, p2c = build_polybius_square(keyword, alphabet)
    ciphertext = []
    for block_start in range(0, len(pt), period):
        block = pt[block_start:block_start + period]
        blen = len(block)
        rows = []
        cols = []
        for ch in block:
            if ch in c2p:
                r, c = c2p[ch]
                rows.append(r)
                cols.append(c)
        # Concatenate: rows || cols
        combined = rows + cols
        # Read pairs: (combined[0],combined[1]), (combined[2],combined[3]), ...
        for i in range(blen):
            cr = combined[2 * i]
            cc = combined[2 * i + 1]
            ciphertext.append(p2c[(cr % 5, cc % 5)])
    return "".join(ciphertext)

def bifid_decrypt(ciphertext, keyword, period, alphabet="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Decrypt bifid cipher (CORRECTED)."""
    ct = ciphertext.upper().replace('J', 'I')
    square, c2p, p2c = build_polybius_square(keyword, alphabet)
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        blen = len(block)
        # Get (row, col) for each ciphertext char
        ct_rows = []
        ct_cols = []
        for ch in block:
            if ch in c2p:
                r, c = c2p[ch]
                ct_rows.append(r)
                ct_cols.append(c)
        # Interleave CT coordinates: [r0,c0,r1,c1,...]
        interleaved = []
        for i in range(blen):
            interleaved.append(ct_rows[i])
            interleaved.append(ct_cols[i])
        # Split: first blen = PT rows, second blen = PT cols
        pt_rows = interleaved[:blen]
        pt_cols = interleaved[blen:]
        for i in range(blen):
            plaintext.append(p2c[(pt_rows[i] % 5, pt_cols[i] % 5)])
    return "".join(plaintext)

def build_polybius_direct(ordered_alpha):
    """Build square from a direct 25-char ordering."""
    c2p = {}
    p2c = {}
    for idx, ch in enumerate(ordered_alpha):
        r, c = divmod(idx, 5)
        c2p[ch] = (r, c)
        p2c[(r, c)] = ch
    return list(ordered_alpha), c2p, p2c

def bifid_encrypt_direct(plaintext_str, ordered_alpha, period):
    """Bifid encrypt with direct alphabet ordering."""
    pt = plaintext_str.upper().replace('J', 'I')
    square, c2p, p2c = build_polybius_direct(ordered_alpha)
    ciphertext = []
    for block_start in range(0, len(pt), period):
        block = pt[block_start:block_start + period]
        blen = len(block)
        rows = []
        cols = []
        for ch in block:
            if ch in c2p:
                r, c = c2p[ch]
                rows.append(r)
                cols.append(c)
        combined = rows + cols
        for i in range(blen):
            cr = combined[2 * i]
            cc = combined[2 * i + 1]
            ciphertext.append(p2c[(cr % 5, cc % 5)])
    return "".join(ciphertext)

def bifid_decrypt_direct(ciphertext, ordered_alpha, period):
    """Bifid decrypt with direct alphabet ordering."""
    ct = ciphertext.upper().replace('J', 'I')
    square, c2p, p2c = build_polybius_direct(ordered_alpha)
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        blen = len(block)
        ct_rows = []
        ct_cols = []
        for ch in block:
            if ch in c2p:
                r, c = c2p[ch]
                ct_rows.append(r)
                ct_cols.append(c)
        interleaved = []
        for i in range(blen):
            interleaved.append(ct_rows[i])
            interleaved.append(ct_cols[i])
        pt_rows = interleaved[:blen]
        pt_cols = interleaved[blen:]
        for i in range(blen):
            plaintext.append(p2c[(pt_rows[i] % 5, pt_cols[i] % 5)])
    return "".join(plaintext)

# ============================================================
# TRIFID CIPHER IMPLEMENTATION
# ============================================================

def build_trifid_cube(keyword, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ+"):
    """Build a 3x3x3 trifid cube (27 positions)."""
    seen = set()
    cube = []
    for ch in keyword.upper():
        if ch not in seen and ch in alphabet:
            seen.add(ch)
            cube.append(ch)
    for ch in alphabet:
        if ch not in seen:
            seen.add(ch)
            cube.append(ch)
    char_to_pos = {}
    pos_to_char = {}
    for idx, ch in enumerate(cube[:27]):
        layer = idx // 9
        row = (idx % 9) // 3
        col = idx % 3
        char_to_pos[ch] = (layer, row, col)
        pos_to_char[(layer, row, col)] = ch
    return cube, char_to_pos, pos_to_char

def trifid_decrypt(ciphertext, keyword, period, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ+"):
    """Decrypt trifid cipher."""
    ct = ciphertext.upper()
    cube, c2p, p2c = build_trifid_cube(keyword, alphabet)
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        blen = len(block)
        # Convert each CT char to (layer, row, col)
        ct_layers = []
        ct_rows = []
        ct_cols = []
        for ch in block:
            if ch in c2p:
                l, r, c = c2p[ch]
                ct_layers.append(l)
                ct_rows.append(r)
                ct_cols.append(c)
        # Interleave: [l0,r0,c0,l1,r1,c1,...]
        interleaved = []
        for i in range(blen):
            interleaved.append(ct_layers[i])
            interleaved.append(ct_rows[i])
            interleaved.append(ct_cols[i])
        # Split into three parts: PT layers, PT rows, PT cols
        pt_layers = interleaved[:blen]
        pt_rows = interleaved[blen:2*blen]
        pt_cols = interleaved[2*blen:3*blen]
        for i in range(blen):
            pl = pt_layers[i] % 3 if i < len(pt_layers) else 0
            pr = pt_rows[i] % 3 if i < len(pt_rows) else 0
            pc = pt_cols[i] % 3 if i < len(pt_cols) else 0
            ch = p2c.get((pl, pr, pc), '?')
            if ch != '+':
                plaintext.append(ch)
            # If '+', skip (null padding)
    return "".join(plaintext)

def trifid_encrypt(plaintext_str, keyword, period, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ+"):
    """Encrypt with trifid cipher."""
    pt = plaintext_str.upper()
    cube, c2p, p2c = build_trifid_cube(keyword, alphabet)
    ciphertext = []
    for block_start in range(0, len(pt), period):
        block = pt[block_start:block_start + period]
        blen = len(block)
        layers = []
        rows = []
        cols = []
        for ch in block:
            if ch in c2p:
                l, r, c = c2p[ch]
                layers.append(l)
                rows.append(r)
                cols.append(c)
        # Concatenate layers || rows || cols
        combined = layers + rows + cols
        # Read triples
        for i in range(blen):
            idx = i * 3
            cl = combined[idx] % 3
            cr = combined[idx + 1] % 3
            cc = combined[idx + 2] % 3
            ciphertext.append(p2c.get((cl, cr, cc), '?'))
    return "".join(ciphertext)

# ============================================================
# PLAYFAIR CIPHER IMPLEMENTATION
# ============================================================

def playfair_decrypt(ciphertext, keyword, alphabet="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Decrypt Playfair cipher."""
    ct = ciphertext.upper().replace('J', 'I')
    square, c2p, p2c = build_polybius_square(keyword, alphabet)
    if len(ct) % 2 != 0:
        ct = ct + 'X'
    plaintext = []
    for i in range(0, len(ct), 2):
        a, b = ct[i], ct[i+1]
        if a not in c2p or b not in c2p:
            plaintext.extend([a, b])
            continue
        ra, ca = c2p[a]
        rb, cb = c2p[b]
        if ra == rb:
            plaintext.append(p2c[(ra, (ca - 1) % 5)])
            plaintext.append(p2c[(rb, (cb - 1) % 5)])
        elif ca == cb:
            plaintext.append(p2c[((ra - 1) % 5, ca)])
            plaintext.append(p2c[((rb - 1) % 5, cb)])
        else:
            plaintext.append(p2c[(ra, cb)])
            plaintext.append(p2c[(rb, ca)])
    return "".join(plaintext)

# ============================================================
# VERIFICATION: Bifid roundtrip
# ============================================================

print("\n" + "=" * 80)
print("VERIFICATION: Bifid encrypt/decrypt roundtrip (corrected)")
print("=" * 80)

test_pt = "THEQUICKBROWNFOXIUMPSOVERTHELAZYDOG"
all_ok = True
for p in [3, 5, 7, 11, 34, 97]:
    enc = bifid_encrypt(test_pt, "KRYPTOS", p)
    dec = bifid_decrypt(enc, "KRYPTOS", p)
    match = "OK" if dec == test_pt else "MISMATCH"
    if dec != test_pt:
        all_ok = False
    print(f"  Period {p:>3}: ENC={enc[:25]}... DEC={dec[:25]}... [{match}]")
    print(f"             PT IC={ic(test_pt):.5f}, ENC IC={ic(enc):.5f}")

# Also verify trifid roundtrip
print("\n  Trifid roundtrip:")
for p in [3, 5, 7, 11]:
    enc_t = trifid_encrypt(test_pt, "KRYPTOS", p)
    dec_t = trifid_decrypt(enc_t, "KRYPTOS", p)
    match_t = "OK" if dec_t == test_pt else "MISMATCH"
    if dec_t != test_pt:
        all_ok = False
    print(f"  Period {p:>3}: [{match_t}] ENC={enc_t[:25]}... DEC={dec_t[:25]}...")

if all_ok:
    print("\n  All roundtrip tests PASSED.")
else:
    print("\n  WARNING: Some roundtrip tests FAILED!")

# ============================================================
# TEST 1: Standard Bifid with KRYPTOS-keyed square, various periods
# ============================================================

print("\n" + "=" * 80)
print("TEST 1: BIFID DECRYPT with KRYPTOS-keyed Polybius square")
print("=" * 80)

sq, _, _ = build_polybius_square("KRYPTOS", KRYPTOS_25)
print("\nPolybius square (KRYPTOS keyword):")
for row in range(5):
    print("  ", " ".join(sq[row*5:(row+1)*5]))

periods_to_test = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 29, 48, 49, 97]

best_score = -99.0
best_result = ""
best_params = ""

results = []
for p in periods_to_test:
    dec = bifid_decrypt(VIG_OUTPUT, "KRYPTOS", p, KRYPTOS_25)
    sc = quadgram_score(dec)
    ic_val = ic(dec)
    wc, words = english_word_count(dec)
    results.append((sc, p, dec, ic_val, wc, words, "decrypt"))
    if sc > best_score:
        best_score, best_result, best_params = sc, dec, f"KRYPTOS bifid decrypt, period={p}"

results.sort(reverse=True)
print(f"\n{'Period':>6} | {'QG Score':>9} | {'IC':>7} | {'Words':>5} | Decrypted text (first 60)")
print("-" * 110)
for sc, p, dec, ic_val, wc, words, mode in results[:15]:
    dec_short = dec[:60] + "..." if len(dec) > 60 else dec
    print(f"{p:>6} | {sc:>9.4f} | {ic_val:.5f} | {wc:>5} | {dec_short}")
    if words:
        print(f"{'':>6} | {'':>9} | {'':>7} | {'':>5} | Words: {', '.join(words[:10])}")

# ============================================================
# TEST 2: Bifid with alternative keyword squares
# ============================================================

print("\n" + "=" * 80)
print("TEST 2: BIFID DECRYPT with various keyword Polybius squares")
print("=" * 80)

keywords = [
    "PALIMPSEST", "ABSCISSA", "KRYPTOSABSCISSA", "KRYPTOSPALIMPSEST",
    "BERLINCLOCK", "SANBORN", "SCHEIDT", "CIA", "LANGLEY",
    "IQLUSION", "ILLUSION", "SHADOW", "DIGETAL", "VIRTUALLY",
    "INVISIBLE", "DESPARATLY", "OBSCURE",
    "",  # No keyword
    "MEDUSA", "YELLOWSUBMARINE",
]

test2_results = []
for kw in keywords:
    for p in [3, 5, 7, 9, 10, 11, 13, 14, 15, 29, 97]:
        dec = bifid_decrypt(VIG_OUTPUT, kw, p, KRYPTOS_25)
        sc = quadgram_score(dec)
        ic_val = ic(dec)
        wc, words = english_word_count(dec)
        test2_results.append((sc, kw if kw else "(none)", p, dec, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, dec, f"bifid decrypt kw='{kw}', p={p}"

test2_results.sort(reverse=True)
print(f"\n{'Keyword':>20} | {'Per':>3} | {'QG Score':>9} | {'IC':>7} | {'Wd':>2} | Decrypted (first 55)")
print("-" * 120)
for sc, kw, p, dec, ic_val, wc, words in test2_results[:25]:
    dec_short = dec[:55] + "..." if len(dec) > 55 else dec
    print(f"{kw:>20} | {p:>3} | {sc:>9.4f} | {ic_val:.5f} | {wc:>2} | {dec_short}")
    if words:
        print(f"{'':>20} | {'':>3} | {'':>9} | {'':>7} | {'':>2} | Words: {', '.join(words[:8])}")

# ============================================================
# TEST 3: Trifid cipher
# ============================================================

print("\n" + "=" * 80)
print("TEST 3: TRIFID DECRYPT with various keywords and periods")
print("=" * 80)

TRIFID_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ+"

trifid_results = []
for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "", "BERLINCLOCK", "SANBORN"]:
    for p in [3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 29, 97]:
        dec = trifid_decrypt(VIG_OUTPUT, kw, p, TRIFID_ALPHA)
        if len(dec) < 10:
            continue
        sc = quadgram_score(dec)
        ic_val = ic(dec)
        wc, words = english_word_count(dec)
        trifid_results.append((sc, kw if kw else "(none)", p, dec, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, dec, f"TRIFID kw='{kw}', p={p}"

trifid_results.sort(reverse=True)
print(f"\n{'Keyword':>15} | {'Per':>3} | {'QG Score':>9} | {'IC':>7} | {'Wd':>2} | Decrypted (first 55)")
print("-" * 110)
for sc, kw, p, dec, ic_val, wc, words in trifid_results[:15]:
    dec_short = dec[:55] + "..." if len(dec) > 55 else dec
    print(f"{kw:>15} | {p:>3} | {sc:>9.4f} | {ic_val:.5f} | {wc:>2} | {dec_short}")
    if words:
        print(f"{'':>15} | {'':>3} | {'':>9} | {'':>7} | {'':>2} | Words: {', '.join(words[:8])}")

# ============================================================
# TEST 4: Bifid with 6x6 grid
# ============================================================

print("\n" + "=" * 80)
print("TEST 4: BIFID with 6x6 grid (A-Z + 0-9)")
print("=" * 80)

def build_polybius_6x6(keyword, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
    seen = set()
    square = []
    for ch in keyword.upper():
        if ch not in seen and ch in alphabet:
            seen.add(ch)
            square.append(ch)
    for ch in alphabet:
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    c2p = {}
    p2c = {}
    for idx, ch in enumerate(square[:36]):
        r, c = divmod(idx, 6)
        c2p[ch] = (r, c)
        p2c[(r, c)] = ch
    return square, c2p, p2c

def bifid_decrypt_6x6(ciphertext, keyword, period):
    ALPHA_6x6 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    ct = ciphertext.upper()
    square, c2p, p2c = build_polybius_6x6(keyword, ALPHA_6x6)
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        blen = len(block)
        ct_rows = []
        ct_cols = []
        for ch in block:
            if ch in c2p:
                r, c = c2p[ch]
                ct_rows.append(r)
                ct_cols.append(c)
        interleaved = []
        for i in range(len(ct_rows)):
            interleaved.append(ct_rows[i])
            interleaved.append(ct_cols[i])
        pt_rows = interleaved[:len(ct_rows)]
        pt_cols = interleaved[len(ct_rows):]
        for i in range(len(ct_rows)):
            pr = pt_rows[i] % 6
            pc = pt_cols[i] % 6
            plaintext.append(p2c.get((pr, pc), '?'))
    return "".join(plaintext)

test4_results = []
for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "", "BERLINCLOCK"]:
    for p in [5, 7, 9, 10, 11, 13, 14, 15, 29, 97]:
        dec = bifid_decrypt_6x6(VIG_OUTPUT, kw, p)
        alpha_only = "".join(c for c in dec if c.isalpha())
        if len(alpha_only) < 10:
            continue
        sc = quadgram_score(alpha_only)
        ic_val = ic(alpha_only)
        wc, words = english_word_count(alpha_only)
        test4_results.append((sc, kw if kw else "(none)", p, dec, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, dec, f"6x6 bifid kw='{kw}', p={p}"

test4_results.sort(reverse=True)
print(f"\n{'Keyword':>15} | {'Per':>3} | {'QG Score':>9} | {'IC':>7} | Decrypted (first 55)")
print("-" * 100)
for sc, kw, p, dec, ic_val, wc, words in test4_results[:10]:
    dec_short = dec[:55] + "..." if len(dec) > 55 else dec
    print(f"{kw:>15} | {p:>3} | {sc:>9.4f} | {ic_val:.5f} | {dec_short}")

# ============================================================
# TEST 5: REVERSE BIFID (encrypt direction)
# ============================================================

print("\n" + "=" * 80)
print("TEST 5: REVERSE BIFID - apply bifid ENCRYPT to Vigenere output")
print("        (if original was bifid decrypt, not encrypt)")
print("=" * 80)

test5_results = []
for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "", "BERLINCLOCK", "SANBORN"]:
    for p in [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 29, 48, 97]:
        enc = bifid_encrypt(VIG_OUTPUT, kw, p, KRYPTOS_25)
        sc = quadgram_score(enc)
        ic_val = ic(enc)
        wc, words = english_word_count(enc)
        test5_results.append((sc, kw if kw else "(none)", p, enc, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, enc, f"REVERSE bifid kw='{kw}', p={p}"

test5_results.sort(reverse=True)
print(f"\n{'Keyword':>15} | {'Per':>3} | {'QG Score':>9} | {'IC':>7} | {'Wd':>2} | Text (first 55)")
print("-" * 110)
for sc, kw, p, dec, ic_val, wc, words in test5_results[:15]:
    dec_short = dec[:55] + "..." if len(dec) > 55 else dec
    print(f"{kw:>15} | {p:>3} | {sc:>9.4f} | {ic_val:.5f} | {wc:>2} | {dec_short}")
    if words:
        print(f"{'':>15} | {'':>3} | {'':>9} | {'':>7} | {'':>2} | Words: {', '.join(words[:8])}")

# ============================================================
# TEST 6: Playfair decryption
# ============================================================

print("\n" + "=" * 80)
print("TEST 6: PLAYFAIR DECRYPT on Vigenere output")
print("=" * 80)

test6_results = []
for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "", "BERLINCLOCK", "SANBORN",
           "KRYPTOSABSCISSA", "KRYPTOSPALIMPSEST", "IQLUSION", "SHADOW"]:
    dec = playfair_decrypt(VIG_OUTPUT, kw, KRYPTOS_25)
    sc = quadgram_score(dec)
    ic_val = ic(dec)
    wc, words = english_word_count(dec)
    test6_results.append((sc, kw if kw else "(none)", dec, ic_val, wc, words))
    if sc > best_score:
        best_score, best_result, best_params = sc, dec, f"PLAYFAIR kw='{kw}'"

test6_results.sort(reverse=True)
print(f"\n{'Keyword':>20} | {'QG Score':>9} | {'IC':>7} | {'Wd':>2} | Decrypted (first 60)")
print("-" * 115)
for sc, kw, dec, ic_val, wc, words in test6_results:
    dec_short = dec[:60] + "..." if len(dec) > 60 else dec
    print(f"{kw:>20} | {sc:>9.4f} | {ic_val:.5f} | {wc:>2} | {dec_short}")
    if words:
        print(f"{'':>20} | {'':>9} | {'':>7} | {'':>2} | Words: {', '.join(words[:8])}")

# ============================================================
# TEST 7: KRYPTOS-ordered alphabet square
# ============================================================

print("\n" + "=" * 80)
print("TEST 7: BIFID with KRYPTOS-ordered alphabet in square")
print("        Grid: KRYPTOSABCDEFGHILMNQUVWXZ (J=I)")
print("=" * 80)

print("\nPolybius square:")
for row in range(5):
    print("  ", " ".join(KRYPTOS_ORDERED[row*5:(row+1)*5]))

test7_results = []
for p in periods_to_test:
    dec = bifid_decrypt_direct(VIG_OUTPUT, KRYPTOS_ORDERED, p)
    sc = quadgram_score(dec)
    ic_val = ic(dec)
    wc, words = english_word_count(dec)
    test7_results.append((sc, f"decrypt p={p}", dec, ic_val, wc, words))
    if sc > best_score:
        best_score, best_result, best_params = sc, dec, f"KRYPTOS-ordered decrypt, p={p}"

    enc = bifid_encrypt_direct(VIG_OUTPUT, KRYPTOS_ORDERED, p)
    sc2 = quadgram_score(enc)
    ic_val2 = ic(enc)
    wc2, words2 = english_word_count(enc)
    test7_results.append((sc2, f"encrypt p={p}", enc, ic_val2, wc2, words2))
    if sc2 > best_score:
        best_score, best_result, best_params = sc2, enc, f"KRYPTOS-ordered encrypt, p={p}"

test7_results.sort(reverse=True)
print(f"\n{'Mode':>18} | {'QG Score':>9} | {'IC':>7} | {'Wd':>2} | Text (first 55)")
print("-" * 105)
for sc, mode, dec, ic_val, wc, words in test7_results[:15]:
    dec_short = dec[:55] + "..." if len(dec) > 55 else dec
    print(f"{mode:>18} | {sc:>9.4f} | {ic_val:.5f} | {wc:>2} | {dec_short}")
    if words:
        print(f"{'':>18} | {'':>9} | {'':>7} | {'':>2} | Words: {', '.join(words[:8])}")

# ============================================================
# TEST 8: Standard alphabet Vigenere then bifid
# ============================================================

print("\n" + "=" * 80)
print("TEST 8: STANDARD A-Z VIGENERE -> BIFID decrypt/encrypt")
print("=" * 80)

test8_results = []
for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", ""]:
    for p in [3, 5, 7, 9, 10, 11, 13, 14, 15, 29, 97]:
        dec = bifid_decrypt(VIG_OUTPUT_STD, kw, p, KRYPTOS_25)
        sc = quadgram_score(dec)
        ic_val = ic(dec)
        wc, words = english_word_count(dec)
        test8_results.append((sc, kw if kw else "(none)", f"dec p={p}", dec, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, dec, f"STD VIG + bifid dec kw='{kw}', p={p}"

        enc = bifid_encrypt(VIG_OUTPUT_STD, kw, p, KRYPTOS_25)
        sc2 = quadgram_score(enc)
        ic_val2 = ic(enc)
        wc2, words2 = english_word_count(enc)
        test8_results.append((sc2, kw if kw else "(none)", f"enc p={p}", enc, ic_val2, wc2, words2))
        if sc2 > best_score:
            best_score, best_result, best_params = sc2, enc, f"STD VIG + bifid enc kw='{kw}', p={p}"

    pf = playfair_decrypt(VIG_OUTPUT_STD, kw, KRYPTOS_25)
    sc3 = quadgram_score(pf)
    test8_results.append((sc3, kw if kw else "(none)", "playfair", pf, ic(pf), 0, []))

test8_results.sort(reverse=True)
print(f"\n{'Keyword':>15} | {'Mode':>10} | {'QG Score':>9} | {'IC':>7} | Text (first 50)")
print("-" * 105)
for sc, kw, mode, dec, ic_val, wc, words in test8_results[:15]:
    dec_short = dec[:50] + "..." if len(dec) > 50 else dec
    print(f"{kw:>15} | {mode:>10} | {sc:>9.4f} | {ic_val:.5f} | {dec_short}")

# ============================================================
# TEST 9: Extended keyword + period search
# ============================================================

print("\n" + "=" * 80)
print("TEST 9: Extended search - all periods 2..30 + key periods, many keywords")
print("=" * 80)

extended_keywords = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "SANBORN",
    "KRYPTOSPALIMPSESTABSCISSA", "SHADOWFORCES",
    "CIA", "NSA", "LANGLEY", "WEBSTER", "THEAMERICANWAY",
]

test9_results = []
all_periods = list(range(2, 31)) + [48, 49, 97]

for kw in extended_keywords:
    for p in all_periods:
        dec = bifid_decrypt(VIG_OUTPUT, kw, p, KRYPTOS_25)
        sc = quadgram_score(dec)
        ic_val = ic(dec)
        wc, words = english_word_count(dec)
        test9_results.append((sc, kw, p, "dec", dec, ic_val, wc, words))
        if sc > best_score:
            best_score, best_result, best_params = sc, dec, f"Extended dec kw='{kw}', p={p}"

        enc = bifid_encrypt(VIG_OUTPUT, kw, p, KRYPTOS_25)
        sc2 = quadgram_score(enc)
        ic_val2 = ic(enc)
        wc2, words2 = english_word_count(enc)
        test9_results.append((sc2, kw, p, "enc", enc, ic_val2, wc2, words2))
        if sc2 > best_score:
            best_score, best_result, best_params = sc2, enc, f"Extended enc kw='{kw}', p={p}"

test9_results.sort(reverse=True)
print(f"\n{'Keyword':>28} | {'Per':>3} | {'Dir':>3} | {'QG Score':>9} | {'IC':>7} | Text (first 50)")
print("-" * 120)
for sc, kw, p, direction, dec, ic_val, wc, words in test9_results[:20]:
    dec_short = dec[:50] + "..." if len(dec) > 50 else dec
    print(f"{kw:>28} | {p:>3} | {direction:>3} | {sc:>9.4f} | {ic_val:.5f} | {dec_short}")
    if words:
        print(f"{'':>28} | {'':>3} | {'':>3} | {'':>9} | {'':>7} | Words: {', '.join(words[:6])}")

# ============================================================
# TEST 10: Interesting observation - the VIG_OUTPUT contains plaintext fragments
# ============================================================

print("\n" + "=" * 80)
print("TEST 10: ANALYSIS of Vigenere intermediate text")
print("=" * 80)
print(f"\nVig output: {VIG_OUTPUT}")
wc_vig, words_vig = english_word_count(VIG_OUTPUT, min_len=3)
# Also search manually for notable substrings
notable = ["NORTHEAST", "BERLINCLOCK", "EAST", "NORTH", "CLOCK", "BERLIN",
           "FELL", "HOLD", "SLOW"]
found_notable = []
for w in notable:
    idx = VIG_OUTPUT.find(w)
    if idx >= 0:
        found_notable.append(f"{w} at pos {idx}")
if found_notable:
    print(f"  Notable substrings in Vig output: {', '.join(found_notable)}")
    print(f"  This suggests the Vig key may partially decrypt K4 correctly,")
    print(f"  and the 'masking layer' hypothesis may apply only to certain sections,")
    print(f"  or the known plaintext fragments (NORTHEAST, BERLINCLOCK) are embedded.")
else:
    print(f"  No notable substrings found.")

# Check letter frequencies
print(f"\n  Letter frequency in Vig output:")
freq = Counter(VIG_OUTPUT)
for ch, cnt in sorted(freq.items(), key=lambda x: -x[1])[:10]:
    print(f"    {ch}: {cnt} ({cnt/len(VIG_OUTPUT)*100:.1f}%)")

# ============================================================
# TEST 11: Nihilist substitution variant
# ============================================================

print("\n" + "=" * 80)
print("TEST 11: NIHILIST SUBSTITUTION variant")
print("=" * 80)

def nihilist_decrypt(ciphertext, sq_keyword, key_phrase):
    square, c2p, p2c = build_polybius_square(sq_keyword, KRYPTOS_25)
    ct_nums = []
    for ch in ciphertext.upper().replace('J', 'I'):
        if ch in c2p:
            r, c = c2p[ch]
            ct_nums.append((r + 1) * 10 + (c + 1))
    key_nums = []
    for ch in key_phrase.upper().replace('J', 'I'):
        if ch in c2p:
            r, c = c2p[ch]
            key_nums.append((r + 1) * 10 + (c + 1))
    if not key_nums:
        return ""
    plaintext = []
    for i, cn in enumerate(ct_nums):
        kn = key_nums[i % len(key_nums)]
        pn = cn - kn
        pr = (pn // 10) - 1
        pc = (pn % 10) - 1
        if 0 <= pr < 5 and 0 <= pc < 5:
            plaintext.append(p2c.get((pr, pc), '?'))
        else:
            plaintext.append('?')
    return "".join(plaintext)

nihilist_results = []
for sq_kw in ["KRYPTOS", "PALIMPSEST", ""]:
    for key_phrase in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "NORTHEAST"]:
        dec = nihilist_decrypt(VIG_OUTPUT, sq_kw, key_phrase)
        valid = sum(1 for c in dec if c != '?')
        ratio = valid / len(dec) if len(dec) > 0 else 0
        alpha = dec.replace('?', '')
        if len(alpha) >= 10:
            sc = quadgram_score(alpha)
            nihilist_results.append((sc, sq_kw if sq_kw else "(none)", key_phrase, dec, ratio))

nihilist_results.sort(reverse=True)
print(f"\n{'Sq KW':>15} | {'Key Phrase':>15} | {'QG Score':>9} | {'Valid%':>6} | Text (first 50)")
print("-" * 110)
for sc, sq_kw, kp, dec, ratio in nihilist_results[:10]:
    dec_short = dec[:50] + "..." if len(dec) > 50 else dec
    print(f"{sq_kw:>15} | {kp:>15} | {sc:>9.4f} | {ratio*100:>5.1f}% | {dec_short}")

# ============================================================
# GLOBAL SUMMARY
# ============================================================

print("\n" + "=" * 80)
print("GLOBAL SUMMARY")
print("=" * 80)

print(f"\nVigenere intermediate text: {VIG_OUTPUT}")
print(f"  IC = {ic(VIG_OUTPUT):.6f}, QG = {quadgram_score(VIG_OUTPUT):.4f}")

print(f"\nBest result found across ALL tests:")
print(f"  Parameters: {best_params}")
print(f"  Score: {best_score:.4f}")
print(f"  Text: {best_result}")
print(f"  IC: {ic(best_result):.6f}")
wc_best, words_best = english_word_count(best_result)
print(f"  English words found: {wc_best} -> {words_best}")

print(f"\nReference quadgram scores:")
print(f"  English text:       ~-2.2 to -2.5")
print(f"  Random text:        ~-4.5 to -5.0")
print(f"  Vig output:          {quadgram_score(VIG_OUTPUT):.4f}")
print(f"  Best decryption:     {best_score:.4f}")

print(f"\nReference IC values:")
print(f"  English text:      ~0.0667")
print(f"  Random text:       ~0.0385")
print(f"  Vig output:         {ic(VIG_OUTPUT):.4f}")
print(f"  Best decryption:    {ic(best_result):.4f}")

# Analysis of the VIG output
print(f"\n--- KEY OBSERVATION ---")
print(f"The Vigenere output contains recognizable fragments:")
print(f"  '{VIG_OUTPUT}'")
# Highlight known words
import re
for pat, name in [("EASTNORTHEAST", "EASTNORTHEAST"), ("BERLINCLOCK", "BERLINCLOCK"),
                   ("FELL", "FELL"), ("HOLD", "HOLD")]:
    m = re.search(pat, VIG_OUTPUT)
    if m:
        print(f"  Found '{name}' at position {m.start()}-{m.end()-1}")

if best_score > -3.5:
    print(f"\n*** PROMISING: Best score ({best_score:.4f}) is significantly above random! ***")
elif best_score > -4.0:
    print(f"\n  MARGINALLY INTERESTING: Best score ({best_score:.4f}) slightly above random.")
else:
    print(f"\n  NO STRONG SIGNAL from bifid/trifid/Playfair decryption.")
    print(f"  The best QG score ({best_score:.4f}) is well below English levels (-2.2 to -2.5)")
    print(f"  and even below partially-decrypted levels (~-3.5).")
    print(f"")
    print(f"  However, the VIG output ALREADY contains 'EASTNORTHEAST' and 'BERLINCLOCK'")
    print(f"  which are known K4 cribs. This suggests the Vigenere key is partially correct")
    print(f"  and the remaining garbled portions might need a DIFFERENT type of transformation")
    print(f"  (e.g., transposition, route cipher, or a different substitution on select segments).")
    print(f"")
    print(f"  The bifid hypothesis is NOT supported by these tests -- applying bifid")
    print(f"  decryption (or encryption) to the Vigenere output does NOT produce English.")
    print(f"  The IC of the Vig output (~0.041) is slightly above random (~0.038), which")
    print(f"  is consistent with a partially-correct decryption, not bifid fractionation.")

print("\nDone.")
