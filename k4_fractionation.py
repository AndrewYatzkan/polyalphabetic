#!/usr/bin/env python3
"""
K4 Fractionation Cipher Hypothesis Testing
Tests ADFGVX, ADFGX, Bifid, Trifid, and modified fractionation ciphers.

K4 ciphertext: OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR (97 chars)
KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ (26 chars)
Known cribs: BERLINCLOCK, EASTNORTHEAST
Period 29 somehow involved
"""

import itertools
import math
import string
import sys
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
CRIBS = ["BERLINCLOCK", "EASTNORTHEAST", "BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST"]
ADFGX_LETTERS = "ADFGX"
ADFGVX_LETTERS = "ADFGVX"

print(f"K4 ciphertext: {K4}")
print(f"K4 length: {len(K4)}")
print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
print(f"KRYPTOS alphabet length: {len(KRYPTOS_ALPHA)}")
print()

# ============================================================
# QUADGRAM SCORING
# ============================================================
class QuadgramScorer:
    def __init__(self, filepath):
        self.quadgrams = {}
        self.total = 0
        try:
            with open(filepath) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        key, count = parts[0], int(parts[1])
                        self.quadgrams[key] = count
                        self.total += count
            self.floor = math.log10(0.01 / self.total)
            for key in self.quadgrams:
                self.quadgrams[key] = math.log10(self.quadgrams[key] / self.total)
        except:
            self.quadgrams = {}
            self.floor = -10
            
    def score(self, text):
        text = text.upper()
        s = 0
        for i in range(len(text) - 3):
            quad = text[i:i+4]
            if quad in self.quadgrams:
                s += self.quadgrams[quad]
            else:
                s += self.floor
        return s
    
    def score_per_char(self, text):
        if len(text) < 4:
            return -10
        return self.score(text) / (len(text) - 3)

scorer = QuadgramScorer("/home/user/polyalphabetic/english_quadgrams.txt")

# Quick English benchmark
eng_score = scorer.score_per_char("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG")
rand_score = scorer.score_per_char("XZQWVBMKJLPTRSDGFHNYC")
print(f"English benchmark score (per char): {eng_score:.4f}")
print(f"Random benchmark score (per char): {rand_score:.4f}")
print()

# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def check_cribs(text):
    """Check if any known cribs appear in the text."""
    found = []
    for crib in CRIBS:
        if crib in text.upper():
            found.append(crib)
    return found

def make_polybius_5x5(keyword):
    """Create a 5x5 Polybius square from a keyword (I/J merged)."""
    seen = set()
    square = []
    for ch in keyword.upper():
        if ch == 'J':
            ch = 'I'
        if ch not in seen and ch in string.ascii_uppercase:
            seen.add(ch)
            square.append(ch)
    for ch in string.ascii_uppercase:
        if ch == 'J':
            continue
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    return square  # 25 letters

def make_polybius_6x6(keyword):
    """Create a 6x6 Polybius square from a keyword (26 letters + 10 digits)."""
    seen = set()
    square = []
    for ch in keyword.upper():
        if ch not in seen and (ch in string.ascii_uppercase or ch in string.digits):
            seen.add(ch)
            square.append(ch)
    for ch in string.ascii_uppercase + string.digits:
        if ch not in seen:
            seen.add(ch)
            square.append(ch)
    return square  # 36 characters

def make_kryptos_polybius(extra_char=None):
    """Create 5x5 or 5x5+1 Polybius from KRYPTOS alphabet."""
    alpha = list(KRYPTOS_ALPHA)
    # KRYPTOS alphabet is 26 chars, for 5x5 we need 25
    # Try dropping various letters
    results = []
    if extra_char is None:
        # Return the full 26-letter version
        return alpha
    else:
        # Drop the specified character
        return [c for c in alpha if c != extra_char]

def columnar_transposition_decrypt(ciphertext, key):
    """Decrypt columnar transposition. Key is a string; columns sorted alphabetically."""
    ncols = len(key)
    nrows = math.ceil(len(ciphertext) / ncols)
    total_cells = nrows * ncols
    padding = total_cells - len(ciphertext)
    
    # Determine column order from key
    order = sorted(range(ncols), key=lambda i: (key[i], i))
    
    # Determine how many chars go in each column
    col_lengths = []
    for col_idx in range(ncols):
        # Which original column position does this sorted column correspond to?
        orig_col = order[col_idx]
        # Last row might be short for some columns
        if orig_col >= ncols - padding:
            col_lengths.append(nrows - 1)
        else:
            col_lengths.append(nrows)
    
    # Fill columns in sorted order
    cols = {}
    pos = 0
    for i, col_idx in enumerate(order):
        length = col_lengths[i]
        cols[col_idx] = ciphertext[pos:pos + length]
        pos += length
    
    # Read off row by row
    plaintext = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(cols.get(col, '')):
                plaintext.append(cols[col][row])
    
    return ''.join(plaintext)

def columnar_transposition_encrypt(plaintext, key):
    """Encrypt with columnar transposition."""
    ncols = len(key)
    nrows = math.ceil(len(plaintext) / ncols)
    
    # Pad plaintext
    padded = plaintext + 'X' * (nrows * ncols - len(plaintext))
    
    # Write into grid row by row
    grid = []
    for r in range(nrows):
        grid.append(padded[r * ncols:(r + 1) * ncols])
    
    # Read off columns in key order
    order = sorted(range(ncols), key=lambda i: (key[i], i))
    ciphertext = []
    for col_idx in order:
        for row in range(nrows):
            ciphertext.append(grid[row][col_idx])
    
    return ''.join(ciphertext)

# ============================================================
# SECTION A: ADFGX CIPHER TESTS
# ============================================================
print("=" * 80)
print("SECTION A: ADFGX CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("ADFGX uses a 5x5 Polybius square. Each letter -> pair of {A,D,F,G,X}.")
print(f"K4 has {len(K4)} chars. If K4 is ADFGX ciphertext, plaintext = {len(K4)//2} chars.")
print(f"  But ADFGX ciphertext should only contain letters A,D,F,G,X.")
print(f"  K4 letters: {sorted(set(K4))}")
print(f"  K4 has {len(set(K4))} unique letters, not 5. So K4 is NOT direct ADFGX output.")
print()

# But maybe a modified ADFGX where the 5 coordinate letters are different?
# Check: are there exactly 5 letters that appear with significantly higher frequency?
freq = Counter(K4)
print("K4 letter frequencies:")
for letter, count in sorted(freq.items(), key=lambda x: -x[1]):
    print(f"  {letter}: {count} ({count/len(K4)*100:.1f}%)")
print()

# ============================================================
# SECTION B: ADFGVX CIPHER TESTS (6x6 Polybius)
# ============================================================
print("=" * 80)
print("SECTION B: ADFGVX CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("ADFGVX uses a 6x6 Polybius square (36 chars: 26 letters + 10 digits).")
print("Each character -> pair of {A,D,F,G,V,X}.")
print(f"K4 has {len(K4)} chars. If ADFGVX ciphertext, plaintext = {len(K4)//2} chars = {len(K4)//2}")
print(f"Same problem: K4 uses {len(set(K4))} unique letters, not 6.")
print()

# ============================================================
# SECTION C: REVERSE ADFGX (K4 is plaintext that was ADFGX-encrypted)
# ============================================================
print("=" * 80)
print("SECTION C: TRYING REVERSE ADFGX/ADFGVX")
print("=" * 80)
print()
print("What if someone encrypted a message with ADFGX to get K4?")
print("Then K4 is the plaintext-side, and the actual ciphertext (ADFGX output)")
print("was what was posted... but K4 uses full alphabet. This doesn't work directly.")
print("However, we can test: what if K4 was produced by a Polybius substitution")
print("followed by columnar transposition (the ADFGX mechanism but with full alphabet)?")
print()

# ============================================================
# SECTION D: BIFID CIPHER TESTS
# ============================================================
print("=" * 80)
print("SECTION D: BIFID CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("Bifid cipher uses a 5x5 Polybius square.")
print("Each letter -> (row, col). Rows and cols are separated,")
print("then re-paired and converted back to letters.")
print("Plaintext length = ciphertext length (97 chars). Fits!")
print()

def bifid_decrypt(ciphertext, square, period=0):
    """
    Decrypt Bifid cipher.
    square: list of 25 characters (5x5 Polybius)
    period: 0 means full-length, otherwise block size
    """
    # Build lookup
    char_to_pos = {}
    for i, ch in enumerate(square):
        char_to_pos[ch] = (i // 5, i % 5)
    pos_to_char = {}
    for i, ch in enumerate(square):
        pos_to_char[(i // 5, i % 5)] = ch
    
    # Handle J/I merge
    if 'J' not in char_to_pos and 'I' in char_to_pos:
        char_to_pos['J'] = char_to_pos['I']
    
    ct = ciphertext.upper()
    # Check all chars are in square
    for ch in ct:
        if ch not in char_to_pos:
            return None
    
    if period == 0:
        period = len(ct)
    
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        n = len(block)
        
        # Get rows and cols for each ciphertext letter
        rows = []
        cols = []
        for ch in block:
            r, c = char_to_pos[ch]
            rows.append(r)
            cols.append(c)
        
        # In Bifid encryption: plaintext rows+cols -> interleave -> ciphertext
        # So to decrypt: ciphertext -> de-interleave rows+cols -> plaintext
        # The fractionated stream is: rows[0], cols[0], rows[1], cols[1], ...
        # which gets split into first half (new rows) and second half (new cols)
        
        # Actually, standard Bifid:
        # Encrypt: pt letters -> rows[], cols[] -> concatenate rows+cols -> re-pair -> ct letters
        # Decrypt: ct letters -> rows[], cols[] -> stream = rows+cols 
        #          -> first n values are pt_rows, last n values are pt_cols -> pt letters
        
        # Wait, let me be more careful.
        # Bifid ENCRYPT:
        #   For each plaintext letter, get (row, col)
        #   Write all rows: r0, r1, r2, ..., rn-1
        #   Write all cols: c0, c1, c2, ..., cn-1
        #   Now read pairs: (r0, r1), (r2, r3), ..., or (r0, c0), (r1, c1), ...
        # 
        # Standard Bifid: concatenate rows then cols into one stream:
        #   r0 r1 r2 ... rn-1 c0 c1 c2 ... cn-1
        # Then take pairs: (r0, r1), (r2, r3), ... wait, no.
        # Then take consecutive pairs as (row, col) for ciphertext letters:
        #   ct[0] = pos_to_char[(stream[0], stream[1])]
        #   ct[1] = pos_to_char[(stream[2], stream[3])]
        #   etc.
        # So the stream has 2n values, giving n ciphertext letters. Good.
        #
        # Bifid DECRYPT (reverse):
        #   For each ciphertext letter, get (row, col)
        #   Write coordinates in order: r0 c0 r1 c1 r2 c2 ...
        #   This gives us the stream of 2n values
        #   First n values = plaintext rows, last n values = plaintext cols
        #   Pair them up: pt[i] = pos_to_char[(stream[i], stream[n+i])]
        
        # Get the interleaved stream from ciphertext
        stream = []
        for ch in block:
            r, c = char_to_pos[ch]
            stream.append(r)
            stream.append(c)
        
        # First n = plaintext rows, last n = plaintext cols
        pt_rows = stream[:n]
        pt_cols = stream[n:]
        
        for i in range(n):
            pos = (pt_rows[i], pt_cols[i])
            if pos in pos_to_char:
                plaintext.append(pos_to_char[pos])
            else:
                plaintext.append('?')
    
    return ''.join(plaintext)

def bifid_encrypt(plaintext, square, period=0):
    """Encrypt with Bifid cipher for verification."""
    char_to_pos = {}
    for i, ch in enumerate(square):
        char_to_pos[ch] = (i // 5, i % 5)
    pos_to_char = {}
    for i, ch in enumerate(square):
        pos_to_char[(i // 5, i % 5)] = ch
    
    if 'J' not in char_to_pos and 'I' in char_to_pos:
        char_to_pos['J'] = char_to_pos['I']
    
    pt = plaintext.upper()
    if period == 0:
        period = len(pt)
    
    ciphertext = []
    for block_start in range(0, len(pt), period):
        block = pt[block_start:block_start + period]
        n = len(block)
        
        rows = []
        cols = []
        for ch in block:
            if ch not in char_to_pos:
                return None
            r, c = char_to_pos[ch]
            rows.append(r)
            cols.append(c)
        
        # Concatenate rows then cols
        stream = rows + cols
        
        # Read off as pairs -> ciphertext letters
        for i in range(0, len(stream), 2):
            pos = (stream[i], stream[i + 1])
            if pos in pos_to_char:
                ciphertext.append(pos_to_char[pos])
            else:
                ciphertext.append('?')
    
    return ''.join(ciphertext)

# Verify Bifid implementation
test_square = make_polybius_5x5("BGWKZQPNDSIOAXEFCLUMTHYVR")  # Example
test_pt = "HELLOWORLD"
test_ct = bifid_encrypt(test_pt, test_square, period=5)
test_dec = bifid_decrypt(test_ct, test_square, period=5)
print(f"Bifid verification: {test_pt} -> {test_ct} -> {test_dec}")
assert test_dec == test_pt, f"Bifid decrypt failed: got {test_dec}"
print("Bifid implementation verified correctly!")
print()

# Test Bifid with various squares and periods
best_bifid_results = []

keywords_for_square = [
    "KRYPTOS", "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALIMPSEST", "ABSCISSA",
    "BERLIN", "BERLINCLOK", "CLOCK", "BERLINCLOCK",
    "SANBORN", "MEDUSA", "LANGLEY", "CIA",
    "EASTNORTHEAST", "NORTHEAST",
    "", # Standard alphabet
]

periods_to_test = [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 23, 29, 31, 37, 41, 43, 47, 97]

print("Testing Bifid cipher with various Polybius squares and periods...")
print("-" * 60)

count = 0
for kw in keywords_for_square:
    square = make_polybius_5x5(kw)
    for period in periods_to_test:
        if period > len(K4):
            continue
        result = bifid_decrypt(K4, square, period)
        if result is None:
            continue
        count += 1
        score = scorer.score_per_char(result)
        cribs = check_cribs(result)
        
        if cribs or score > -8.0:
            best_bifid_results.append((score, kw if kw else "STANDARD", period, result, cribs))
            
        if cribs:
            print(f"  *** CRIB FOUND! kw={kw}, period={period}: {result}")
            print(f"      Cribs: {cribs}")

# Sort by score
best_bifid_results.sort(key=lambda x: -x[0])
print(f"\nTested {count} Bifid combinations.")
print(f"\nTop 10 Bifid results by English score:")
for i, (score, kw, period, result, cribs) in enumerate(best_bifid_results[:10]):
    print(f"  {i+1}. score={score:.4f} kw='{kw}' period={period}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION E: TRIFID CIPHER TESTS
# ============================================================
print("=" * 80)
print("SECTION E: TRIFID CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("Trifid uses a 3x3x3 cube (27 positions, perfect for 26 letters + 1 separator).")
print("Each letter -> (layer, row, col). Three coordinate streams.")
print("Plaintext length = ciphertext length. Fits 97 chars!")
print()

def trifid_decrypt(ciphertext, cube, period):
    """
    Decrypt Trifid cipher.
    cube: list of 27 characters (3x3x3)
    period: block size (required for Trifid)
    """
    # Build lookup
    char_to_pos = {}
    for i, ch in enumerate(cube):
        layer = i // 9
        row = (i % 9) // 3
        col = i % 3
        char_to_pos[ch] = (layer, row, col)
    pos_to_char = {}
    for i, ch in enumerate(cube):
        layer = i // 9
        row = (i % 9) // 3
        col = i % 3
        pos_to_char[(layer, row, col)] = ch
    
    ct = ciphertext.upper()
    for ch in ct:
        if ch not in char_to_pos:
            return None
    
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        n = len(block)
        
        # Get coordinates from ciphertext
        layers = []
        rows = []
        cols = []
        for ch in block:
            l, r, c = char_to_pos[ch]
            layers.append(l)
            rows.append(r)
            cols.append(c)
        
        # In Trifid encryption:
        #   plaintext -> layers[], rows[], cols[]
        #   concatenate: layers + rows + cols (3n values)
        #   read as triples: (stream[0], stream[1], stream[2]), (stream[3], stream[4], stream[5]), ...
        #   -> ciphertext letters
        #
        # Trifid DECRYPT:
        #   ciphertext -> triples: l0 r0 c0, l1 r1 c1, ...
        #   interleaved stream: l0 r0 c0 l1 r1 c1 ...  (3n values)
        #   first n = plaintext layers, second n = plaintext rows, third n = plaintext cols
        #   pt[i] = pos_to_char[(stream[i], stream[n+i], stream[2n+i])]
        
        stream = []
        for ch in block:
            l, r, c = char_to_pos[ch]
            stream.append(l)
            stream.append(r)
            stream.append(c)
        
        # Should have 3n values
        assert len(stream) == 3 * n
        
        pt_layers = stream[:n]
        pt_rows = stream[n:2*n]
        pt_cols = stream[2*n:3*n]
        
        for i in range(n):
            pos = (pt_layers[i], pt_rows[i], pt_cols[i])
            if pos in pos_to_char:
                plaintext.append(pos_to_char[pos])
            else:
                plaintext.append('?')
    
    return ''.join(plaintext)

def make_trifid_cube(keyword):
    """Create a 27-element cube from keyword. Uses 26 letters + '.' as 27th."""
    seen = set()
    cube = []
    for ch in keyword.upper():
        if ch not in seen and ch in string.ascii_uppercase:
            seen.add(ch)
            cube.append(ch)
    for ch in string.ascii_uppercase:
        if ch not in seen:
            seen.add(ch)
            cube.append(ch)
    cube.append('.')  # 27th character (separator/null)
    return cube

# Test Trifid
print("Testing Trifid cipher with various cubes and periods...")
print("-" * 60)

best_trifid_results = []
count = 0

trifid_keywords = [
    "KRYPTOS", "KRYPTOSABCDEFGHIJLMNQUVWXZ", "PALIMPSEST", "ABSCISSA",
    "BERLIN", "CLOCK", "BERLINCLOCK", "SANBORN", "",
    "EASTNORTHEAST", "NORTHEAST", "MEDUSA", "LANGLEY",
]

trifid_periods = [3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 19, 23, 29, 31, 37, 41, 43, 47, 97]

for kw in trifid_keywords:
    cube = make_trifid_cube(kw)
    for period in trifid_periods:
        if period > len(K4):
            continue
        result = trifid_decrypt(K4, cube, period)
        if result is None or '.' in result:
            if result and '?' not in result:
                # Remove dots and check
                clean = result.replace('.', '')
                if len(clean) > 10:
                    score = scorer.score_per_char(clean)
                    cribs = check_cribs(clean)
                    if cribs or score > -8.0:
                        best_trifid_results.append((score, kw if kw else "STANDARD", period, clean, cribs))
                    if cribs:
                        print(f"  *** CRIB FOUND! kw={kw}, period={period}: {clean}")
            continue
        count += 1
        score = scorer.score_per_char(result)
        cribs = check_cribs(result)
        
        if cribs or score > -8.0:
            best_trifid_results.append((score, kw if kw else "STANDARD", period, result, cribs))
        
        if cribs:
            print(f"  *** CRIB FOUND! kw={kw}, period={period}: {result}")
            print(f"      Cribs: {cribs}")

best_trifid_results.sort(key=lambda x: -x[0])
print(f"\nTested {count} Trifid combinations.")
print(f"\nTop 10 Trifid results by English score:")
for i, (score, kw, period, result, cribs) in enumerate(best_trifid_results[:10]):
    print(f"  {i+1}. score={score:.4f} kw='{kw}' period={period}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION F: MODIFIED FRACTIONATION (Polybius + Columnar Transposition)
# ============================================================
print("=" * 80)
print("SECTION F: POLYBIUS SUBSTITUTION + COLUMNAR TRANSPOSITION")
print("=" * 80)
print()
print("This tests the ADFGX/ADFGVX *mechanism* (Polybius fractionation + columnar")
print("transposition) but where the Polybius output is NOT restricted to ADFGX letters.")
print("Instead, rows/cols are mapped back to letters via some scheme.")
print()
print("Approach: Reverse columnar transposition, then reverse Polybius substitution.")
print()

# For this to work with K4 (97 chars, full alphabet), we need a different approach.
# The idea: K4 was created by:
# 1. Take plaintext, convert each letter to (row, col) using 5x5 Polybius -> 2*97 = 194 digits (0-4)
# 2. Write these 194 digits into a grid with some number of columns
# 3. Read off columns in keyword order -> ciphertext digits
# 4. Convert pairs of digits back to letters -> 97-letter ciphertext (K4)
#
# Actually, standard ADFGX: step 4 would give ADFGX letters. K4 isn't in ADFGX.
# 
# Alternative: Maybe the transposition operates on the LETTERS (not the fractionated pairs).
# i.e., Polybius substitution (digraphic) then columnar transposition of the result.
# 
# Or: columnar transposition first, then Polybius substitution.
# 
# Let's test: columnar transposition of K4, then check if result could be Polybius pairs.

transposition_keys = [
    "KRYPTOS",     # 7 cols
    "BERLIN",      # 6 cols
    "CLOCK",       # 5 cols
    "PALIMPSEST",  # 10 cols
    "ABSCISSA",    # 8 cols
    "SANBORN",     # 7 cols
    "MEDUSA",      # 6 cols
    "KRYPT",       # 5 cols
    "CIA",         # 3 cols
]

# Also test numeric keys for period 29
# Try transposition with key length 29
print("Testing columnar transposition decryption then Bifid decryption...")
print("-" * 60)

best_combo_results = []

for tkey in transposition_keys:
    # Step 1: Undo columnar transposition
    transposed = columnar_transposition_decrypt(K4, tkey)
    
    # Step 2: Try Bifid decrypt on the result
    for skw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "BERLINCLOCK", ""]:
        square = make_polybius_5x5(skw)
        for period in [0, 5, 7, 10, 29, 97]:
            result = bifid_decrypt(transposed, square, period)
            if result is None:
                continue
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -7.5:
                best_combo_results.append((score, f"trans={tkey}+bifid={skw}", period, result, cribs))
            if cribs:
                print(f"  *** CRIB! trans_key={tkey}, bifid_kw={skw}, period={period}")
                print(f"     {result}")

    # Also try: Bifid first, then columnar transposition
    for skw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", ""]:
        square = make_polybius_5x5(skw)
        for period in [0, 5, 7, 10, 29, 97]:
            bifid_result = bifid_decrypt(K4, square, period)
            if bifid_result is None:
                continue
            # Then undo transposition
            result = columnar_transposition_decrypt(bifid_result, tkey)
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -7.5:
                best_combo_results.append((score, f"bifid={skw}+trans={tkey}", period, result, cribs))
            if cribs:
                print(f"  *** CRIB! bifid_kw={skw}, trans_key={tkey}, period={period}")
                print(f"     {result}")

best_combo_results.sort(key=lambda x: -x[0])
print(f"\nTop 10 Transposition+Bifid combo results:")
for i, (score, desc, period, result, cribs) in enumerate(best_combo_results[:10]):
    print(f"  {i+1}. score={score:.4f} {desc} period={period}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION G: ADFGX WITH NUMBER-ENCODED COORDINATES
# ============================================================
print("=" * 80)
print("SECTION G: ADFGX/ADFGVX REVERSE ENGINEERING")
print("=" * 80)
print()
print("Testing: What if K4 was encrypted as follows:")
print("  1. Plaintext -> Polybius pairs (using digits 0-4 or 0-5)")
print("  2. Digit stream -> columnar transposition")  
print("  3. Transposed digits -> converted to letters somehow")
print()

def try_adfgx_decrypt(ciphertext, polybius_square, trans_key, coord_letters="ADFGX"):
    """
    Full ADFGX decryption:
    1. Map ciphertext letters to coordinate letters (if they match)
    2. Undo columnar transposition on the coordinate string
    3. Take pairs and look up in Polybius square
    """
    # Check if ciphertext uses only the coordinate letters
    ct = ciphertext.upper()
    valid = all(ch in coord_letters for ch in ct)
    if not valid:
        return None, "Ciphertext contains letters outside coordinate set"
    
    # Undo columnar transposition
    untransposed = columnar_transposition_decrypt(ct, trans_key)
    
    # Convert pairs to plaintext
    if len(untransposed) % 2 != 0:
        untransposed = untransposed[:-1]  # Drop last if odd
    
    coord_to_idx = {ch: i for i, ch in enumerate(coord_letters)}
    plaintext = []
    for i in range(0, len(untransposed), 2):
        row = coord_to_idx.get(untransposed[i])
        col = coord_to_idx.get(untransposed[i+1])
        if row is not None and col is not None:
            idx = row * len(coord_letters) + col
            if idx < len(polybius_square):
                plaintext.append(polybius_square[idx])
            else:
                plaintext.append('?')
        else:
            plaintext.append('?')
    
    return ''.join(plaintext), "OK"

# Since K4 is NOT in ADFGX letters, we can't directly apply standard ADFGX.
# But what if the coordinate letters are different? Let's check all 5-letter subsets
# of the K4 alphabet that could serve as coordinates.

# Actually, let's try something else: what if K4 has been converted from ADFGX output
# via a simple substitution? I.e., A->some letter, D->some letter, etc.
# If so, K4 should have exactly 5 distinct letters (it doesn't - it has 22).
# So this doesn't work.

print("K4 has 22 unique letters - cannot be standard ADFGX/ADFGVX output.")
print()

# ============================================================
# SECTION H: NIHILIST CIPHER (Polybius + addition)
# ============================================================
print("=" * 80)
print("SECTION H: NIHILIST CIPHER HYPOTHESIS")  
print("=" * 80)
print()
print("Nihilist cipher: Each plaintext letter -> 2-digit number from Polybius square.")
print("Key letter -> 2-digit number. Add them modulo.")
print("Result is a stream of 2-digit numbers (10-55 range for 5x5 square).")
print("This doesn't directly produce letters, but if we map numbers back to letters...")
print()

def nihilist_decrypt_attempt(ciphertext, polybius_square, key):
    """
    Attempt Nihilist-like decryption where ciphertext letters represent
    Polybius coordinates that have been shifted by a key.
    """
    # Map each letter to its Polybius position (row*5+col gives 0-24, or (row+1)*10+(col+1) gives 11-55)
    char_to_num = {}
    for i, ch in enumerate(polybius_square):
        row = i // 5 + 1
        col = i % 5 + 1
        char_to_num[ch] = row * 10 + col
    
    num_to_char = {}
    for ch, num in char_to_num.items():
        num_to_char[num] = ch
    
    # Get key numbers
    key_nums = []
    for ch in key.upper():
        if ch == 'J':
            ch = 'I'
        if ch in char_to_num:
            key_nums.append(char_to_num[ch])
    
    if not key_nums:
        return None
    
    # Get ciphertext numbers
    ct_nums = []
    for ch in ciphertext.upper():
        if ch == 'J':
            ch = 'I'
        if ch in char_to_num:
            ct_nums.append(char_to_num[ch])
        else:
            return None
    
    # Subtract key (repeating)
    plaintext = []
    for i, ct_num in enumerate(ct_nums):
        key_num = key_nums[i % len(key_nums)]
        # Try subtraction
        pt_num = ct_num - key_num + 11  # Offset to keep in valid range
        # Adjust to valid range (11-55)
        row = pt_num // 10
        col = pt_num % 10
        if 1 <= row <= 5 and 1 <= col <= 5:
            if pt_num in num_to_char:
                plaintext.append(num_to_char[pt_num])
            else:
                plaintext.append('?')
        else:
            plaintext.append('?')
    
    result = ''.join(plaintext)
    if '?' in result:
        return None
    return result

print("Testing Nihilist-like decryption...")
nihilist_results = []

for skw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", ""]:
    square = make_polybius_5x5(skw)
    for key in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "BERLINCLOCK",
                "SANBORN", "NORTHEAST", "EASTNORTHEAST", "MEDUSA"]:
        result = nihilist_decrypt_attempt(K4, square, key)
        if result and '?' not in result:
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -8.0:
                nihilist_results.append((score, skw if skw else "STD", key, result, cribs))
            if cribs:
                print(f"  *** CRIB! square={skw}, key={key}: {result}")

nihilist_results.sort(key=lambda x: -x[0])
print(f"Top 5 Nihilist results:")
for i, (score, skw, key, result, cribs) in enumerate(nihilist_results[:5]):
    print(f"  {i+1}. score={score:.4f} square='{skw}' key='{key}': {result[:50]}...")
print()

# ============================================================
# SECTION I: FOUR-SQUARE CIPHER
# ============================================================
print("=" * 80)
print("SECTION I: FOUR-SQUARE CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("Four-square uses 4 Polybius squares. Digraphic cipher: 2 letters -> 2 letters.")
print("Plaintext length = ciphertext length (97 chars, but needs even - so 96 or pad).")
print()

def four_square_decrypt(ciphertext, square1, square2):
    """
    Decrypt Four-square cipher.
    Uses standard alphabet for top-left and bottom-right squares.
    square1 = top-right keyed square
    square2 = bottom-left keyed square
    """
    std_alpha = make_polybius_5x5("")
    
    # Build lookups
    def build_lookup(square):
        c2p = {}
        p2c = {}
        for i, ch in enumerate(square):
            r, c = i // 5, i % 5
            c2p[ch] = (r, c)
            p2c[(r, c)] = ch
        if 'J' not in c2p and 'I' in c2p:
            c2p['J'] = c2p['I']
        return c2p, p2c
    
    std_c2p, std_p2c = build_lookup(std_alpha)
    s1_c2p, s1_p2c = build_lookup(square1)
    s2_c2p, s2_p2c = build_lookup(square2)
    
    ct = ciphertext.upper().replace('J', 'I')
    plaintext = []
    
    for i in range(0, len(ct) - 1, 2):
        ch1, ch2 = ct[i], ct[i+1]
        
        # ch1 is from square1 (top-right), ch2 is from square2 (bottom-left)
        if ch1 not in s1_c2p or ch2 not in s2_c2p:
            plaintext.append('?')
            plaintext.append('?')
            continue
        
        r1, c1 = s1_c2p[ch1]
        r2, c2 = s2_c2p[ch2]
        
        # Plaintext: top-left gets (r1, c2), bottom-right gets (r2, c1)
        pt1 = std_p2c.get((r1, c2), '?')
        pt2 = std_p2c.get((r2, c1), '?')
        plaintext.append(pt1)
        plaintext.append(pt2)
    
    # Handle odd last character
    if len(ct) % 2 == 1:
        plaintext.append(ct[-1])
    
    return ''.join(plaintext)

print("Testing Four-Square cipher...")
four_square_results = []

sq_keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
               "BERLINCLOCK", "SANBORN", "MEDUSA", "NORTHEAST", ""]

for kw1 in sq_keywords:
    for kw2 in sq_keywords:
        s1 = make_polybius_5x5(kw1)
        s2 = make_polybius_5x5(kw2)
        result = four_square_decrypt(K4, s1, s2)
        if result and '?' not in result:
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -7.5:
                k1 = kw1 if kw1 else "STD"
                k2 = kw2 if kw2 else "STD"
                four_square_results.append((score, k1, k2, result, cribs))
            if cribs:
                print(f"  *** CRIB! s1={kw1}, s2={kw2}: {result}")

four_square_results.sort(key=lambda x: -x[0])
print(f"\nTop 10 Four-Square results:")
for i, (score, k1, k2, result, cribs) in enumerate(four_square_results[:10]):
    print(f"  {i+1}. score={score:.4f} s1='{k1}' s2='{k2}': {result[:50]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION J: TWO-SQUARE (PLAYFAIR VARIANT)
# ============================================================
print("=" * 80)
print("SECTION J: TWO-SQUARE / PLAYFAIR HYPOTHESIS")
print("=" * 80)
print()

def two_square_decrypt_horizontal(ciphertext, square1, square2):
    """Two-square with horizontal arrangement (side by side)."""
    def build_lookup(square):
        c2p = {}
        p2c = {}
        for i, ch in enumerate(square):
            r, c = i // 5, i % 5
            c2p[ch] = (r, c)
            p2c[(r, c)] = ch
        if 'J' not in c2p and 'I' in c2p:
            c2p['J'] = c2p['I']
        return c2p, p2c
    
    s1_c2p, s1_p2c = build_lookup(square1)
    s2_c2p, s2_p2c = build_lookup(square2)
    
    ct = ciphertext.upper().replace('J', 'I')
    plaintext = []
    
    for i in range(0, len(ct) - 1, 2):
        ch1, ch2 = ct[i], ct[i+1]
        if ch1 not in s1_c2p or ch2 not in s2_c2p:
            plaintext.append('?')
            plaintext.append('?')
            continue
        r1, c1 = s1_c2p[ch1]
        r2, c2 = s2_c2p[ch2]
        
        if r1 == r2:
            # Same row: swap columns directly
            pt1 = s1_p2c.get((r1, c2), '?')
            pt2 = s2_p2c.get((r2, c1), '?')
        else:
            # Rectangle: take opposite corners
            pt1 = s1_p2c.get((r2, c1), '?')
            pt2 = s2_p2c.get((r1, c2), '?')
        
        plaintext.append(pt1)
        plaintext.append(pt2)
    
    if len(ct) % 2 == 1:
        plaintext.append(ct[-1])
    
    return ''.join(plaintext)

print("Testing Two-Square cipher...")
two_square_results = []

for kw1 in sq_keywords:
    for kw2 in sq_keywords:
        s1 = make_polybius_5x5(kw1)
        s2 = make_polybius_5x5(kw2)
        result = two_square_decrypt_horizontal(K4, s1, s2)
        if result and '?' not in result:
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -7.5:
                k1 = kw1 if kw1 else "STD"
                k2 = kw2 if kw2 else "STD"
                two_square_results.append((score, k1, k2, result, cribs))
            if cribs:
                print(f"  *** CRIB! s1={kw1}, s2={kw2}: {result}")

two_square_results.sort(key=lambda x: -x[0])
print(f"\nTop 10 Two-Square results:")
for i, (score, k1, k2, result, cribs) in enumerate(two_square_results[:10]):
    print(f"  {i+1}. score={score:.4f} s1='{k1}' s2='{k2}': {result[:50]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION K: BIFID WITH PERIOD 29 (DEEP SEARCH)
# ============================================================
print("=" * 80)
print("SECTION K: DEEP BIFID SEARCH WITH PERIOD 29")
print("=" * 80)
print()
print("Period 29 is known to be involved. Testing Bifid with period=29")
print("and many more Polybius square variations.")
print()

# Generate many 5x5 squares by permuting KRYPTOS alphabet
# For exhaustive search of first few letters...

best_p29_results = []

# More comprehensive keyword list
extended_keywords = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "BERLINCLOCK",
    "SANBORN", "MEDUSA", "LANGLEY", "CIA", "NORTHEAST", "EASTNORTHEAST",
    "EAST", "NORTH", "WEST", "SOUTH",
    "DESPARATEVEIL", "IQLUSION", "ILLUSION", "SHADOW", "FORCES",
    "LUCID", "MEMORY", "VIRTUALLY", "INVISIBLE",
    "DIGETAL", "DIGITAL", "INTERPRETATU", "THEYRE",
    "UNDERGRUUND", "UNDERGROUND",
    "SLOWLYDESPARATLY", "TOTALLYINVISIBLE",
    "KRYPTOSPALIMPSEST", "KRYPTOSABSCISSA",
    "PALIMPSESTABSCISSA", "KRYPTOSPALIMPSESTABSCISSA",
    # K1-K3 related
    "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENURANCEOFILLUSION",
    "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLE",
    "ENDTRANSPOSITION",  
    "NYPVTTMZFPK",  # from K4 itself
    # Sanborn's words
    "DYAHR",
    "SCHEIBE", "ENIGMA",
    # Common cipher words
    "SECRET", "CIPHER", "DECODE", "ENCRYPT",
    "", # Standard alphabet
]

for kw in extended_keywords:
    square = make_polybius_5x5(kw)
    result = bifid_decrypt(K4, square, period=29)
    if result is None:
        continue
    score = scorer.score_per_char(result)
    cribs = check_cribs(result)
    best_p29_results.append((score, kw if kw else "STANDARD", result, cribs))
    if cribs:
        print(f"  *** CRIB FOUND! kw={kw}: {result}")
        print(f"      Cribs: {cribs}")

best_p29_results.sort(key=lambda x: -x[0])
print(f"\nTop 15 Bifid period=29 results:")
for i, (score, kw, result, cribs) in enumerate(best_p29_results[:15]):
    print(f"  {i+1}. score={score:.4f} kw='{kw}'")
    print(f"     {result[:70]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION L: BIFID WITH KRYPTOS-ORDERED SQUARE (DROP EACH LETTER)
# ============================================================
print("=" * 80)
print("SECTION L: BIFID WITH KRYPTOS-ORDERED 5x5 SQUARES")
print("=" * 80)
print()
print("KRYPTOS alphabet has 26 letters. For 5x5 Polybius, need to drop one.")
print("Testing dropping each of the 26 letters.")
print()

best_kryptos_bifid = []

for drop_letter in KRYPTOS_ALPHA:
    # Create square by removing this letter from KRYPTOS alphabet
    square = [ch for ch in KRYPTOS_ALPHA if ch != drop_letter]
    assert len(square) == 25, f"Expected 25, got {len(square)}"
    
    for period in [0, 5, 7, 10, 13, 29, 97]:
        result = bifid_decrypt(K4, square, period)
        if result is None:
            # Some K4 letters might not be in square (the dropped letter)
            # Need to handle: if the dropped letter appears in K4, this won't work
            continue
        score = scorer.score_per_char(result)
        cribs = check_cribs(result)
        best_kryptos_bifid.append((score, drop_letter, period, result, cribs))
        if cribs:
            print(f"  *** CRIB! drop='{drop_letter}' period={period}: {result}")

best_kryptos_bifid.sort(key=lambda x: -x[0])
print(f"Top 10 KRYPTOS-ordered Bifid results:")
for i, (score, drop, period, result, cribs) in enumerate(best_kryptos_bifid[:10]):
    print(f"  {i+1}. score={score:.4f} drop='{drop}' period={period}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION M: CONJUGATED MATRIX BIFID
# ============================================================
print("=" * 80)
print("SECTION M: CONJUGATED MATRIX BIFID (CM-BIFID)")
print("=" * 80)
print()
print("CM-Bifid uses TWO different Polybius squares: one for encoding, one for decoding.")
print("This is more resistant to attack but worth testing with known keywords.")
print()

def cm_bifid_decrypt(ciphertext, enc_square, dec_square, period=0):
    """
    Conjugated Matrix Bifid decryption.
    enc_square: used to convert ciphertext to coordinates
    dec_square: used to convert coordinates back to plaintext
    """
    # Build lookups
    enc_c2p = {}
    for i, ch in enumerate(enc_square):
        enc_c2p[ch] = (i // 5, i % 5)
    if 'J' not in enc_c2p and 'I' in enc_c2p:
        enc_c2p['J'] = enc_c2p['I']
    
    dec_p2c = {}
    for i, ch in enumerate(dec_square):
        dec_p2c[(i // 5, i % 5)] = ch
    
    ct = ciphertext.upper()
    for ch in ct:
        if ch not in enc_c2p:
            return None
    
    if period == 0:
        period = len(ct)
    
    plaintext = []
    for block_start in range(0, len(ct), period):
        block = ct[block_start:block_start + period]
        n = len(block)
        
        stream = []
        for ch in block:
            r, c = enc_c2p[ch]
            stream.append(r)
            stream.append(c)
        
        pt_rows = stream[:n]
        pt_cols = stream[n:]
        
        for i in range(n):
            pos = (pt_rows[i], pt_cols[i])
            if pos in dec_p2c:
                plaintext.append(dec_p2c[pos])
            else:
                plaintext.append('?')
    
    return ''.join(plaintext)

cm_results = []

# Test pairs of different keyword squares
cm_keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "BERLINCLOCK", "SANBORN", ""]

for kw1 in cm_keywords:
    for kw2 in cm_keywords:
        if kw1 == kw2:
            continue  # Same as regular Bifid, already tested
        s1 = make_polybius_5x5(kw1)
        s2 = make_polybius_5x5(kw2)
        for period in [0, 5, 7, 10, 29, 97]:
            result = cm_bifid_decrypt(K4, s1, s2, period)
            if result is None:
                continue
            score = scorer.score_per_char(result)
            cribs = check_cribs(result)
            if cribs or score > -7.5:
                k1 = kw1 if kw1 else "STD"
                k2 = kw2 if kw2 else "STD"
                cm_results.append((score, k1, k2, period, result, cribs))
            if cribs:
                print(f"  *** CRIB! enc={kw1}, dec={kw2}, period={period}: {result}")

cm_results.sort(key=lambda x: -x[0])
print(f"Top 10 CM-Bifid results:")
for i, (score, k1, k2, period, result, cribs) in enumerate(cm_results[:10]):
    print(f"  {i+1}. score={score:.4f} enc='{k1}' dec='{k2}' period={period}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION N: CRIB-DRAGGING WITH BIFID
# ============================================================
print("=" * 80)
print("SECTION N: CRIB-DRAGGING ANALYSIS WITH BIFID")
print("=" * 80)
print()
print("If BERLINCLOCK appears at some position in the plaintext,")
print("we can work backwards to constrain the Polybius square.")
print()

def bifid_crib_analysis(ciphertext, crib, position, period):
    """
    Given that 'crib' appears at 'position' in the plaintext,
    determine constraints on the Polybius square for Bifid with given period.
    """
    n = len(ciphertext)
    crib_len = len(crib)
    
    if position + crib_len > n:
        return None
    
    # Determine which block(s) the crib falls in
    if period == 0:
        period = n
    
    block_start = (position // period) * period
    block_end = block_start + period
    
    # For simplicity, only analyze if crib fits within one block
    if position + crib_len > block_end:
        return None
    
    # Within the block:
    # The crib letters have known (row, col) positions
    # The corresponding ciphertext letters also have (row, col) positions
    # The Bifid relationship connects them
    
    # Crib position within block
    offset = position - block_start
    block_ct = ciphertext[block_start:block_end]
    block_len = len(block_ct)
    
    # In Bifid decryption:
    # stream = [r0,c0,r1,c1,...] from ciphertext
    # pt_rows = stream[:block_len] = [r0, c0, r1, c1, ...block_len items]
    # pt_cols = stream[block_len:] = [remaining items]
    # pt[i] = square[pt_rows[i]*5 + pt_cols[i]]
    
    # The crib tells us: for positions offset..offset+crib_len-1,
    # we know what pt_rows[i] and pt_cols[i] must be (for any given square).
    # And we know which ct characters contribute to stream positions pt_rows[i] and pt_cols[i].
    
    info = {
        'block_start': block_start,
        'block_len': block_len,
        'offset': offset,
        'crib': crib,
        'block_ct': block_ct,
    }
    return info

# Analyze where BERLINCLOCK could be placed
for crib in ["BERLINCLOCK", "EASTNORTHEAST"]:
    print(f"Crib: {crib} (length {len(crib)})")
    for pos in range(len(K4) - len(crib) + 1):
        info = bifid_crib_analysis(K4, crib, pos, 29)
        if info:
            # Just note which block it falls in
            pass
    print(f"  Can be placed at positions 0-{len(K4)-len(crib)} in K4")
    print(f"  With period 29: fits in blocks of size 29")
    
    # For period 29: blocks are [0:29], [29:58], [58:87], [87:97]
    blocks = []
    p = 29
    for bs in range(0, len(K4), p):
        be = min(bs + p, len(K4))
        blocks.append((bs, be, be - bs))
    print(f"  Period 29 blocks: {blocks}")
    
    for bs, be, blen in blocks:
        max_pos = blen - len(crib)
        if max_pos >= 0:
            print(f"    Block [{bs}:{be}] (len {blen}): crib can start at offset 0-{max_pos}")
        else:
            print(f"    Block [{bs}:{be}] (len {blen}): crib doesn't fit")
    print()

# ============================================================
# SECTION O: BIFID + VIGENERE COMBINATION
# ============================================================
print("=" * 80)
print("SECTION O: BIFID + VIGENERE COMBINATION")
print("=" * 80)
print()
print("What if K4 = Vigenere(Bifid(plaintext))? Or Bifid(Vigenere(plaintext))?")
print("Testing with known keywords...")
print()

def vigenere_decrypt(ciphertext, key):
    """Standard Vigenere decryption."""
    result = []
    key = key.upper()
    ct = ciphertext.upper()
    ki = 0
    for ch in ct:
        if ch in string.ascii_uppercase:
            shift = ord(key[ki % len(key)]) - ord('A')
            decrypted = chr((ord(ch) - ord('A') - shift) % 26 + ord('A'))
            result.append(decrypted)
            ki += 1
        else:
            result.append(ch)
    return ''.join(result)

def beaufort_decrypt(ciphertext, key):
    """Beaufort decryption (same as encryption)."""
    result = []
    key = key.upper()
    ct = ciphertext.upper()
    ki = 0
    for ch in ct:
        if ch in string.ascii_uppercase:
            shift = ord(key[ki % len(key)]) - ord('A')
            decrypted = chr((shift - (ord(ch) - ord('A'))) % 26 + ord('A'))
            result.append(decrypted)
            ki += 1
        else:
            result.append(ch)
    return ''.join(result)

combo_vig_bifid_results = []

vig_keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK",
            "BERLINCLOCK", "SANBORN", "MEDUSA", "NORTHEAST"]

bifid_kws = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", ""]

for vk in vig_keys:
    for bkw in bifid_kws:
        square = make_polybius_5x5(bkw)
        for period in [0, 5, 7, 29, 97]:
            # Vigenere first, then Bifid decrypt
            vig_result = vigenere_decrypt(K4, vk)
            bifid_result = bifid_decrypt(vig_result, square, period)
            if bifid_result:
                score = scorer.score_per_char(bifid_result)
                cribs = check_cribs(bifid_result)
                if cribs or score > -7.5:
                    combo_vig_bifid_results.append(
                        (score, f"vig({vk})->bifid({bkw},p={period})", bifid_result, cribs))
                if cribs:
                    print(f"  *** CRIB! vig={vk}->bifid kw={bkw} p={period}: {bifid_result}")
            
            # Bifid first, then Vigenere decrypt
            bifid_result2 = bifid_decrypt(K4, square, period)
            if bifid_result2:
                vig_result2 = vigenere_decrypt(bifid_result2, vk)
                score = scorer.score_per_char(vig_result2)
                cribs = check_cribs(vig_result2)
                if cribs or score > -7.5:
                    combo_vig_bifid_results.append(
                        (score, f"bifid({bkw},p={period})->vig({vk})", vig_result2, cribs))
                if cribs:
                    print(f"  *** CRIB! bifid kw={bkw} p={period}->vig={vk}: {vig_result2}")
            
            # Also try Beaufort
            beau_result = beaufort_decrypt(K4, vk)
            bifid_result3 = bifid_decrypt(beau_result, square, period)
            if bifid_result3:
                score = scorer.score_per_char(bifid_result3)
                cribs = check_cribs(bifid_result3)
                if cribs or score > -7.5:
                    combo_vig_bifid_results.append(
                        (score, f"beau({vk})->bifid({bkw},p={period})", bifid_result3, cribs))
                if cribs:
                    print(f"  *** CRIB! beau={vk}->bifid kw={bkw} p={period}: {bifid_result3}")

combo_vig_bifid_results.sort(key=lambda x: -x[0])
print(f"\nTop 10 Vigenere+Bifid combo results:")
for i, (score, desc, result, cribs) in enumerate(combo_vig_bifid_results[:10]):
    print(f"  {i+1}. score={score:.4f} {desc}")
    print(f"     {result[:60]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION P: PLAYFAIR CIPHER
# ============================================================
print("=" * 80)
print("SECTION P: PLAYFAIR CIPHER HYPOTHESIS")
print("=" * 80)
print()
print("Playfair is a digraphic cipher using a 5x5 square.")
print("K4 has 97 chars (odd). Playfair needs even-length input.")
print("Maybe last char is padding, or maybe K4 isn't Playfair.")
print()

def playfair_decrypt(ciphertext, square):
    """Decrypt Playfair cipher."""
    c2p = {}
    p2c = {}
    for i, ch in enumerate(square):
        r, c = i // 5, i % 5
        c2p[ch] = (r, c)
        p2c[(r, c)] = ch
    if 'J' not in c2p and 'I' in c2p:
        c2p['J'] = c2p['I']
    
    ct = ciphertext.upper().replace('J', 'I')
    if len(ct) % 2 == 1:
        ct = ct + 'X'  # Pad
    
    plaintext = []
    for i in range(0, len(ct), 2):
        a, b = ct[i], ct[i+1]
        if a not in c2p or b not in c2p:
            plaintext.append('?')
            plaintext.append('?')
            continue
        
        ra, ca = c2p[a]
        rb, cb = c2p[b]
        
        if ra == rb:  # Same row
            plaintext.append(p2c[(ra, (ca - 1) % 5)])
            plaintext.append(p2c[(rb, (cb - 1) % 5)])
        elif ca == cb:  # Same column
            plaintext.append(p2c[((ra - 1) % 5, ca)])
            plaintext.append(p2c[((rb - 1) % 5, cb)])
        else:  # Rectangle
            plaintext.append(p2c[(ra, cb)])
            plaintext.append(p2c[(rb, ca)])
    
    return ''.join(plaintext)

playfair_results = []

for kw in extended_keywords[:20]:
    square = make_polybius_5x5(kw)
    result = playfair_decrypt(K4, square)
    if result and '?' not in result:
        score = scorer.score_per_char(result)
        cribs = check_cribs(result)
        playfair_results.append((score, kw if kw else "STANDARD", result, cribs))
        if cribs:
            print(f"  *** CRIB! kw={kw}: {result}")

playfair_results.sort(key=lambda x: -x[0])
print(f"Top 10 Playfair results:")
for i, (score, kw, result, cribs) in enumerate(playfair_results[:10]):
    print(f"  {i+1}. score={score:.4f} kw='{kw}': {result[:50]}...")
    if cribs:
        print(f"     *** CRIBS: {cribs}")
print()

# ============================================================
# SECTION Q: FRACTIONATED MORSE
# ============================================================
print("=" * 80)
print("SECTION Q: FRACTIONATED MORSE HYPOTHESIS")
print("=" * 80)
print()
print("Fractionated Morse converts plaintext to Morse, groups into trigrams,")
print("then substitutes. Output length != input length generally.")
print("Skipping detailed implementation as length relationship is complex.")
print()

# ============================================================
# SECTION R: COMPREHENSIVE SCORING SUMMARY
# ============================================================
print("=" * 80)
print("COMPREHENSIVE RESULTS SUMMARY")
print("=" * 80)
print()

all_results = []

for score, kw, period, result, cribs in best_bifid_results[:5]:
    all_results.append((score, f"Bifid kw='{kw}' p={period}", result, cribs))

for score, kw, period, result, cribs in best_trifid_results[:5]:
    all_results.append((score, f"Trifid kw='{kw}' p={period}", result, cribs))

for score, desc, period, result, cribs in best_combo_results[:5]:
    all_results.append((score, f"Trans+Bifid {desc} p={period}", result, cribs))

for score, k1, k2, result, cribs in four_square_results[:5]:
    all_results.append((score, f"FourSquare s1='{k1}' s2='{k2}'", result, cribs))

for score, k1, k2, result, cribs in two_square_results[:5]:
    all_results.append((score, f"TwoSquare s1='{k1}' s2='{k2}'", result, cribs))

for score, drop, period, result, cribs in best_kryptos_bifid[:5]:
    all_results.append((score, f"KRYPTOS-Bifid drop='{drop}' p={period}", result, cribs))

for score, k1, k2, period, result, cribs in cm_results[:5]:
    all_results.append((score, f"CM-Bifid enc='{k1}' dec='{k2}' p={period}", result, cribs))

for score, desc, result, cribs in combo_vig_bifid_results[:5]:
    all_results.append((score, f"Vig+Bifid {desc}", result, cribs))

for score, kw, result, cribs in playfair_results[:5]:
    all_results.append((score, f"Playfair kw='{kw}'", result, cribs))

for score, skw, key, result, cribs in nihilist_results[:5]:
    all_results.append((score, f"Nihilist sq='{skw}' key='{key}'", result, cribs))

all_results.sort(key=lambda x: -x[0])

print("OVERALL TOP 25 RESULTS (all cipher types):")
print("-" * 80)
for i, (score, desc, result, cribs) in enumerate(all_results[:25]):
    marker = " *** HAS CRIBS ***" if cribs else ""
    print(f"{i+1:3d}. score={score:.4f} | {desc}")
    print(f"     {result[:70]}")
    if cribs:
        print(f"     CRIBS FOUND: {cribs}")
    print()

# Check if any result contains cribs
any_cribs = any(cribs for _, _, _, cribs in all_results)
if any_cribs:
    print("*** CRIB MATCHES FOUND! See above for details. ***")
else:
    print("No crib matches found in any decryption attempt.")
    print()
    print("ANALYSIS:")
    print("- None of the tested fractionation ciphers (Bifid, Trifid, Four-Square,")
    print("  Two-Square, Playfair, Nihilist, ADFGX/ADFGVX, or combinations with")
    print("  Vigenere/Beaufort and columnar transposition) produced the known cribs.")
    print("- The best English-like scores achieved were around -7.5 to -8.0 per char,")
    print("  compared to the English benchmark of about -2.3 per char.")
    print("- K4's 97-character length and 22 unique letters rule out standard ADFGX/ADFGVX.")
    print("- The search space for unknown Polybius squares is 25! which is too large")
    print("  for brute force without additional constraints.")
    print()
    print("RECOMMENDATIONS FOR FURTHER INVESTIGATION:")
    print("- Try hill-climbing on Bifid square with period 29 (genetic algorithm)")
    print("- Try ADFGX where the Polybius output is FURTHER encrypted with Vigenere")
    print("- Try seriated Playfair or other exotic variants")
    print("- Consider that K4 may use a non-standard or novel cipher mechanism")

print()
print("Script complete.")
