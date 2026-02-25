#!/usr/bin/env python3
"""
K4 Artistic Cipher - Unconventional Approaches
================================================
Jim Sanborn is a VISUAL ARTIST. This script tests approaches an artist
(not a cryptographer) might use, including physical layout, compass rose,
Egypt-inspired methods, Berlin Wall dates, matrix codes, and K1-K3
method progressions.
"""

import itertools
import math
import string
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

KEYWORDS = [
    "PALIMPSEST", "ABSCISSA", "KRYPTOS", "WELTZEITUHR", "ALEXANDERPLATZ",
    "BERLINCLOCK", "EASTNORTHEAST", "TUTANKHAMUN", "CARTER", "DISCOVERY",
    "GROSSERSTERN", "BERLIN", "EGYPT", "CLOCK", "COMPASS",
    "NORTHEASTEAST", "NORTHEAST", "EAST", "NORTH", "SOUTH",
]

# K3 transposition key from KRYPTOS
K3_KEY = [0, 3, 6, 2, 5, 1, 4]  # KRYPTOS -> numeric key

# Load dictionary
def load_dictionary(path="/home/user/polyalphabetic/OxfordEnglishWords.txt"):
    words = set()
    try:
        with open(path) as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 3:
                    words.add(w)
    except FileNotFoundError:
        print(f"WARNING: Dictionary not found at {path}")
    return words

DICTIONARY = load_dictionary()

# Build sets by word length for faster scoring
WORDS_BY_LEN = {}
for w in DICTIONARY:
    WORDS_BY_LEN.setdefault(len(w), set()).add(w)

# ============================================================
# SCORING FUNCTIONS
# ============================================================
def score_text(text):
    """Score plaintext by counting dictionary words found (greedy, longest first)."""
    text = text.upper()
    total_covered = 0
    words_found = []
    
    # Try to find words of length 4+ in the text
    for wlen in sorted(WORDS_BY_LEN.keys(), reverse=True):
        if wlen < 4:
            continue
        for i in range(len(text) - wlen + 1):
            substr = text[i:i+wlen]
            if substr in WORDS_BY_LEN.get(wlen, set()):
                words_found.append((i, substr))
    
    # Remove overlapping words, keep longest
    words_found.sort(key=lambda x: (-len(x[1]), x[0]))
    used_positions = set()
    final_words = []
    for pos, word in words_found:
        positions = set(range(pos, pos + len(word)))
        if not positions & used_positions:
            used_positions |= positions
            final_words.append((pos, word))
            total_covered += len(word)
    
    final_words.sort()
    return total_covered, final_words


def check_cribs(text):
    """Check if known cribs appear near expected positions."""
    text = text.upper()
    results = []
    
    # BERLINCLOCK near position 63
    for offset in range(-10, 11):
        pos = 63 + offset
        if 0 <= pos <= len(text) - 11:
            if text[pos:pos+11] == "BERLINCLOCK":
                results.append(f"BERLINCLOCK at pos {pos} (offset {offset} from 63)")
    if "BERLINCLOCK" in text:
        idx = text.index("BERLINCLOCK")
        results.append(f"BERLINCLOCK found at position {idx}")
    
    # EASTNORTHEAST near position 21
    for offset in range(-10, 11):
        pos = 21 + offset
        if 0 <= pos <= len(text) - 13:
            if text[pos:pos+13] == "EASTNORTHEAST":
                results.append(f"EASTNORTHEAST at pos {pos} (offset {offset} from 21)")
    if "EASTNORTHEAST" in text:
        idx = text.index("EASTNORTHEAST")
        results.append(f"EASTNORTHEAST found at position {idx}")
    
    # Check partial matches
    for crib in ["BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST"]:
        if crib in text:
            idx = text.index(crib)
            results.append(f"  partial: {crib} at position {idx}")
    
    return results


def report(method_name, text, threshold=12):
    """Report results if score exceeds threshold."""
    text = text.upper()
    covered, words = score_text(text)
    cribs = check_cribs(text)
    
    if covered >= threshold or cribs:
        print(f"\n{'='*70}")
        print(f"METHOD: {method_name}")
        print(f"Result: {text}")
        print(f"Score: {covered} chars covered by dictionary words")
        if words:
            print(f"Words found: {', '.join(f'{w}@{p}' for p, w in words)}")
        if cribs:
            print(f"CRIB MATCHES: {'; '.join(cribs)}")
        print(f"{'='*70}")
        return True
    return False


# ============================================================
# CIPHER PRIMITIVES
# ============================================================
def char_to_num(c, alphabet=STANDARD_ALPHA):
    c = c.upper()
    if c in alphabet:
        return alphabet.index(c)
    return -1

def num_to_char(n, alphabet=STANDARD_ALPHA):
    return alphabet[n % len(alphabet)]

def vigenere_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    result = []
    ki = 0
    for c in ciphertext.upper():
        cn = char_to_num(c, alphabet)
        kn = char_to_num(key[ki % len(key)], alphabet)
        if cn >= 0 and kn >= 0:
            result.append(num_to_char((cn - kn) % len(alphabet), alphabet))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def vigenere_encrypt(plaintext, key, alphabet=STANDARD_ALPHA):
    result = []
    ki = 0
    for c in plaintext.upper():
        cn = char_to_num(c, alphabet)
        kn = char_to_num(key[ki % len(key)], alphabet)
        if cn >= 0 and kn >= 0:
            result.append(num_to_char((cn + kn) % len(alphabet), alphabet))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def beaufort_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    result = []
    ki = 0
    for c in ciphertext.upper():
        cn = char_to_num(c, alphabet)
        kn = char_to_num(key[ki % len(key)], alphabet)
        if cn >= 0 and kn >= 0:
            result.append(num_to_char((kn - cn) % len(alphabet), alphabet))
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def caesar_shift(text, shift, alphabet=STANDARD_ALPHA):
    result = []
    for c in text.upper():
        n = char_to_num(c, alphabet)
        if n >= 0:
            result.append(num_to_char((n - shift) % len(alphabet), alphabet))
        else:
            result.append(c)
    return ''.join(result)

def columnar_transposition_decrypt(ciphertext, key_order):
    """Decrypt columnar transposition given numeric key order."""
    ncols = len(key_order)
    nrows = math.ceil(len(ciphertext) / ncols)
    total_cells = nrows * ncols
    empty_cells = total_cells - len(ciphertext)
    
    # Determine column lengths
    col_lengths = [nrows] * ncols
    # Last row has empty cells in the rightmost columns
    for i in range(empty_cells):
        col_lengths[ncols - 1 - i] -= 1
    
    # Read ciphertext into columns in key order
    sorted_cols = sorted(range(ncols), key=lambda x: key_order[x])
    columns = {}
    pos = 0
    for col_idx in sorted_cols:
        clen = col_lengths[col_idx]
        columns[col_idx] = ciphertext[pos:pos+clen]
        pos += clen
    
    # Read off row by row
    result = []
    for row in range(nrows):
        for col in range(ncols):
            if row < len(columns.get(col, '')):
                result.append(columns[col][row])
    
    return ''.join(result)

def columnar_transposition_encrypt(plaintext, key_order):
    """Encrypt with columnar transposition."""
    ncols = len(key_order)
    nrows = math.ceil(len(plaintext) / ncols)
    
    # Pad plaintext
    padded = plaintext + 'X' * (nrows * ncols - len(plaintext))
    
    # Write into grid row by row
    grid = []
    for r in range(nrows):
        grid.append(padded[r*ncols:(r+1)*ncols])
    
    # Read columns in key order
    sorted_cols = sorted(range(ncols), key=lambda x: key_order[x])
    result = []
    for col in sorted_cols:
        for row in range(nrows):
            if col < len(grid[row]):
                result.append(grid[row][col])
    
    return ''.join(result)[:len(plaintext)]


def reverse_text(text):
    return text[::-1]


# ============================================================
# 1. PHYSICAL LAYOUT ON THE SCULPTURE
# ============================================================
def test_physical_layout():
    print("\n" + "#"*70)
    print("# 1. PHYSICAL LAYOUT ON THE SCULPTURE")
    print("#"*70)
    
    results_found = 0
    
    # Test various grid arrangements
    grid_configs = [
        (8, 12, "8x12 grid"),
        (8, 13, "8x13 grid (last row short)"),
        (7, 14, "7x14 grid"),
        (7, 13, "7x13+6 grid"),
        (9, 11, "9x11 grid (last row short)"),
        (10, 10, "10x10 grid"),
        (11, 9, "11x9 grid"),
        (12, 8, "12x8 grid"),
    ]
    
    for nrows, ncols, desc in grid_configs:
        # Arrange into grid
        grid = []
        for r in range(nrows):
            start = r * ncols
            end = min(start + ncols, len(K4))
            if start < len(K4):
                grid.append(K4[start:end])
        
        # a) Read down columns (left to right)
        col_read = []
        for c in range(ncols):
            for r in range(len(grid)):
                if c < len(grid[r]):
                    col_read.append(grid[r][c])
        result = ''.join(col_read)
        if report(f"Layout {desc} - columns L->R", result):
            results_found += 1
        
        # b) Read down columns (right to left)
        col_read_rl = []
        for c in range(ncols-1, -1, -1):
            for r in range(len(grid)):
                if c < len(grid[r]):
                    col_read_rl.append(grid[r][c])
        result = ''.join(col_read_rl)
        if report(f"Layout {desc} - columns R->L", result):
            results_found += 1
        
        # c) Boustrophedon (alternate row direction)
        bous = []
        for r in range(len(grid)):
            if r % 2 == 0:
                bous.append(grid[r])
            else:
                bous.append(grid[r][::-1])
        result = ''.join(bous)
        if report(f"Layout {desc} - boustrophedon", result):
            results_found += 1
        
        # d) Boustrophedon then read columns
        # Create boustrophedon grid first
        bous_grid = []
        for r in range(len(grid)):
            if r % 2 == 0:
                bous_grid.append(grid[r])
            else:
                bous_grid.append(grid[r][::-1])
        
        col_read_bous = []
        for c in range(ncols):
            for r in range(len(bous_grid)):
                if c < len(bous_grid[r]):
                    col_read_bous.append(bous_grid[r][c])
        result = ''.join(col_read_bous)
        if report(f"Layout {desc} - boustrophedon+columns", result):
            results_found += 1
        
        # e) Spiral reading (clockwise from top-left)
        if len(grid) > 0 and all(len(row) == ncols for row in grid[:-1]):
            spiral = []
            top, bottom, left, right = 0, len(grid)-1, 0, ncols-1
            visited = set()
            while top <= bottom and left <= right:
                for c in range(left, right+1):
                    if top < len(grid) and c < len(grid[top]):
                        if (top, c) not in visited:
                            spiral.append(grid[top][c])
                            visited.add((top, c))
                top += 1
                for r in range(top, bottom+1):
                    if r < len(grid) and right < len(grid[r]):
                        if (r, right) not in visited:
                            spiral.append(grid[r][right])
                            visited.add((r, right))
                right -= 1
                for c in range(right, left-1, -1):
                    if bottom < len(grid) and c < len(grid[bottom]):
                        if (bottom, c) not in visited:
                            spiral.append(grid[bottom][c])
                            visited.add((bottom, c))
                bottom -= 1
                for r in range(bottom, top-1, -1):
                    if r < len(grid) and left < len(grid[r]):
                        if (r, left) not in visited:
                            spiral.append(grid[r][left])
                            visited.add((r, left))
                left += 1
            result = ''.join(spiral)
            if report(f"Layout {desc} - spiral reading", result):
                results_found += 1
    
    # Test physical layout with Vigenere decryption afterward
    for nrows, ncols, desc in [(8, 12, "8x12"), (8, 13, "8x13")]:
        grid = []
        for r in range(nrows):
            start = r * ncols
            end = min(start + ncols, len(K4))
            if start < len(K4):
                grid.append(K4[start:end])
        
        # Column-read then Vigenere
        col_read = []
        for c in range(ncols):
            for r in range(len(grid)):
                if c < len(grid[r]):
                    col_read.append(grid[r][c])
        transposed = ''.join(col_read)
        
        for kw in KEYWORDS:
            for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                aname = "STD" if alpha == STANDARD_ALPHA else "KA"
                result = vigenere_decrypt(transposed, kw, alpha)
                report(f"Layout {desc} cols+Vig({kw},{aname})", result)
                
                result = beaufort_decrypt(transposed, kw, alpha)
                report(f"Layout {desc} cols+Beaufort({kw},{aname})", result)
    
    print(f"\n  Physical layout tests complete.")


# ============================================================
# 2. COMPASS ROSE CIPHER
# ============================================================
def test_compass_rose():
    print("\n" + "#"*70)
    print("# 2. COMPASS ROSE CIPHER")
    print("#"*70)
    
    # Compass directions and their degree values
    compass_dirs = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5,
    }
    
    # a) Rotate alphabet by compass degree values
    for direction, degrees in compass_dirs.items():
        shift = int(degrees) % 26
        if shift == 0:
            continue
        result = caesar_shift(K4, shift)
        report(f"Compass {direction} ({degrees}deg) shift={shift}", result)
    
    # b) EASTNORTHEAST = ENE = 67.5 degrees
    # Use 67 and 68 as shifts
    for shift in [67, 68, 6, 7, 5, 675]:
        shift_mod = shift % 26
        result = caesar_shift(K4, shift_mod)
        report(f"ENE-derived shift={shift} (mod26={shift_mod})", result)
    
    # c) Use compass bearing sequence as Vigenere key
    # "EASTNORTHEAST" -> E=4,A=0,S=18,T=19,N=13,O=14,R=17,T=19,H=7,E=4,A=0,S=18,T=19
    for kw in ["EASTNORTHEAST", "ENE", "NORTHEAST"]:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            result = vigenere_decrypt(K4, kw, alpha)
            report(f"Compass Vigenere({kw},{aname})", result)
            result = beaufort_decrypt(K4, kw, alpha)
            report(f"Compass Beaufort({kw},{aname})", result)
    
    # d) ENE as reading direction on physical grid (67.5 degrees ~ diagonal)
    # Map onto 8x12 grid, read at ~67.5 degree angle (steep diagonal)
    grid = []
    ncols = 12
    for r in range(8):
        start = r * ncols
        end = min(start + ncols, len(K4))
        if start < len(K4):
            grid.append(K4[start:end])
    # Pad last row
    while len(grid[-1]) < ncols:
        grid[-1] += 'X'
    
    # Read diagonals at various angles
    # 67.5 deg ~ go 2 rows down for every 1 column right
    for dx, dy, angle_desc in [(1, 2, "steep ~67deg"), (1, 1, "45deg"), (2, 1, "shallow ~22deg")]:
        for start_r in range(len(grid)):
            for start_c in range(ncols):
                diag = []
                r, c = start_r, start_c
                while 0 <= r < len(grid) and 0 <= c < ncols:
                    diag.append(grid[r][c])
                    r += dy
                    c += dx
                if len(diag) >= 8:
                    result = ''.join(diag)
                    report(f"Diagonal({angle_desc}) from ({start_r},{start_c})", result, threshold=6)
    
    print(f"\n  Compass rose tests complete.")


# ============================================================
# 3. EGYPT-INSPIRED APPROACHES
# ============================================================
def test_egypt():
    print("\n" + "#"*70)
    print("# 3. EGYPT-INSPIRED APPROACHES")
    print("#"*70)
    
    # a) K3 plaintext contains key to K4?
    # K3 plaintext (paraphrase of Howard Carter's account)
    k3_plain = "SLOWLYDESPERATLYSLOWLYTHEREMAINSOFPASSABORINGDUEWEREMAINLYON" \
               "THEUPPERLEVELOFTHEDOORWAYCONDITIONSRECEIVEDMYEYESSPREADTOYOU" \
               "WITHGLITTERINGCANBEYOUMAKEANYTHINGYES"
    # Note: K3 has deliberate misspellings
    
    # Extract potential keywords from K3
    k3_keywords = ["SLOWLY", "DESPERATLY", "REMAINS", "PASSAGE", "DOORWAY",
                    "GLITTERING", "ANYTHING", "CONDITIONS", "UPPER", "LEVEL",
                    "BORING", "EYES", "SPREAD", "MAKE"]
    
    for kw in k3_keywords:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            result = vigenere_decrypt(K4, kw, alpha)
            report(f"Egypt/K3-keyword Vig({kw},{aname})", result)
            result = beaufort_decrypt(K4, kw, alpha)
            report(f"Egypt/K3-keyword Beaufort({kw},{aname})", result)
    
    # b) Hieroglyphic-inspired: group letters into pairs/triples (like hieroglyphic cartouches)
    # Take pairs as coordinates
    for group_size in [2, 3]:
        groups = [K4[i:i+group_size] for i in range(0, len(K4), group_size)]
        # Convert each group to a single letter using sum of positions mod 26
        result_chars = []
        for g in groups:
            total = sum(STANDARD_ALPHA.index(c) for c in g if c in STANDARD_ALPHA)
            result_chars.append(STANDARD_ALPHA[total % 26])
        result = ''.join(result_chars)
        report(f"Egypt hieroglyphic grouping (size={group_size})", result, threshold=6)
    
    # c) Rosetta Stone approach: K4 as multiple encodings
    # Split K4 in half and check if both halves decrypt to similar messages
    half = len(K4) // 2
    first_half = K4[:half]
    second_half = K4[half:]
    
    for kw in KEYWORDS[:8]:
        r1 = vigenere_decrypt(first_half, kw)
        r2 = vigenere_decrypt(second_half, kw)
        # Check if halves share significant substrings
        for wlen in range(6, 3, -1):
            for i in range(len(r1) - wlen + 1):
                sub = r1[i:i+wlen]
                if sub in r2:
                    print(f"  Rosetta match: '{sub}' in both halves with key {kw}")
    
    # d) TUTANKHAMUN as key with various methods
    for kw in ["TUTANKHAMUN", "CARTER", "HOWARDCARTER", "CANOPICJAR"]:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            result = vigenere_decrypt(K4, kw, alpha)
            report(f"Egypt Vig({kw},{aname})", result)
    
    print(f"\n  Egypt-inspired tests complete.")


# ============================================================
# 4. BERLIN WALL DATE ENCODING
# ============================================================
def test_berlin_wall():
    print("\n" + "#"*70)
    print("# 4. BERLIN WALL DATE ENCODING")
    print("#"*70)
    
    # Date: November 9, 1989
    # Various numeric representations
    date_sequences = [
        ([1, 1, 9, 1, 9, 8, 9], "11/9/1989 digits"),
        ([9, 1, 1, 1, 9, 8, 9], "9/11/1989 digits"),
        ([11, 9, 19, 89], "11-9-19-89"),
        ([9, 11, 19, 89], "9-11-19-89"),
        ([11, 9, 1, 9, 8, 9], "11-9-1-9-8-9"),
        ([1, 1, 0, 9, 1, 9, 8, 9], "11091989 digits"),
        ([0, 9, 1, 1, 1, 9, 8, 9], "09111989 digits"),
        ([1, 9, 8, 9, 1, 1, 9], "1989-11-9 digits"),
        ([1, 9, 8, 9, 1, 1, 0, 9], "19891109 digits"),
        ([11, 9, 89], "11-9-89"),
        ([9, 11, 89], "9-11-89"),
    ]
    
    for seq, desc in date_sequences:
        # a) As transposition key
        if max(seq) < len(K4) and len(set(seq)) > 1:
            # Use as columnar transposition key
            result = columnar_transposition_decrypt(K4, seq)
            report(f"Berlin date transposition ({desc})", result)
        
        # b) As Caesar shifts applied cyclically
        shifted = []
        for i, c in enumerate(K4):
            s = seq[i % len(seq)]
            n = char_to_num(c)
            if n >= 0:
                shifted.append(num_to_char((n - s) % 26))
            else:
                shifted.append(c)
        result = ''.join(shifted)
        report(f"Berlin date Caesar cycle ({desc})", result)
        
        # Also try adding instead of subtracting
        shifted_add = []
        for i, c in enumerate(K4):
            s = seq[i % len(seq)]
            n = char_to_num(c)
            if n >= 0:
                shifted_add.append(num_to_char((n + s) % 26))
            else:
                shifted_add.append(c)
        result = ''.join(shifted_add)
        report(f"Berlin date Caesar+ cycle ({desc})", result)
    
    # c) Date as Vigenere key (letters corresponding to date digits)
    date_keys_alpha = []
    for seq, desc in date_sequences:
        key = ''.join(STANDARD_ALPHA[s % 26] for s in seq)
        date_keys_alpha.append((key, desc))
    
    for key, desc in date_keys_alpha:
        result = vigenere_decrypt(K4, key)
        report(f"Berlin date Vigenere key={key} ({desc})", result)
    
    # d) Combine Berlin date with KRYPTOS keyword
    for seq, desc in date_sequences[:4]:
        # Transposition with date, then Vigenere with KRYPTOS keyword
        transposed = columnar_transposition_decrypt(K4, seq) if max(seq) < len(K4) else K4
        for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK"]:
            result = vigenere_decrypt(transposed, kw)
            report(f"Berlin transp({desc})+Vig({kw})", result)
    
    print(f"\n  Berlin Wall date tests complete.")


# ============================================================
# 5. MATRIX CODE (Hill cipher, Polybius, ADFGVX)
# ============================================================
def test_matrix_code():
    print("\n" + "#"*70)
    print("# 5. MATRIX CODE")
    print("#"*70)
    
    # a) Polybius square with KRYPTOS alphabet
    # KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ (26 letters)
    # Can use 5x5 grid (combine I/J) or we use full 26-letter mapping
    # KRYPTOS alphabet has no duplicate, it's a permutation of A-Z
    
    # 5x5 Polybius (dropping one letter or combining)
    # Using KRYPTOS_ALPHA in a 5x5+1 arrangement
    polybius_grid = {}
    for i, c in enumerate(KRYPTOS_ALPHA[:25]):  # first 25 for 5x5
        row, col = i // 5, i % 5
        polybius_grid[c] = (row, col)
    # Map Z (26th) to same as X or separate handling
    polybius_grid['Z'] = (4, 4)  # share last position
    
    # Reverse mapping
    polybius_reverse = {}
    for c, (r, cc) in polybius_grid.items():
        polybius_reverse[(r, cc)] = c
    
    # Try Polybius decode: pairs of digits in K4 positions
    # Convert K4 letters to their KRYPTOS_ALPHA positions, then treat as row/col pairs
    k4_positions = []
    for c in K4:
        if c in KRYPTOS_ALPHA:
            k4_positions.append(KRYPTOS_ALPHA.index(c))
    
    # Treat consecutive position values as (row, col) pairs
    for mod_val in [5, 6]:  # 5x5 or 6x6 grid
        decoded = []
        for i in range(0, len(k4_positions) - 1, 2):
            r = k4_positions[i] % mod_val
            c = k4_positions[i+1] % mod_val
            idx = r * mod_val + c
            if idx < 26:
                decoded.append(STANDARD_ALPHA[idx])
            elif idx < len(KRYPTOS_ALPHA):
                decoded.append(KRYPTOS_ALPHA[idx])
        result = ''.join(decoded)
        report(f"Polybius decode (mod {mod_val})", result, threshold=8)
    
    # b) ADFGVX cipher (WWI German cipher - Berlin theme)
    # ADFGVX uses a 6x6 grid with letters A,D,F,G,V,X as coordinates
    # Standard ADFGVX key letters: A D F G V X
    adfgvx_letters = "ADFGVX"
    
    # Check if K4 could be ADFGVX ciphertext
    adfgvx_count = sum(1 for c in K4 if c in adfgvx_letters)
    print(f"\n  ADFGVX letter count in K4: {adfgvx_count}/{len(K4)} ({100*adfgvx_count/len(K4):.1f}%)")
    
    # Even if not pure ADFGVX, test with KRYPTOS-alphabet grid
    # Create a 6x6 ADFGVX grid using KRYPTOS alphabet + digits
    adfgvx_grid_content = KRYPTOS_ALPHA + "0123456789"  # 36 chars for 6x6
    adfgvx_grid = {}
    adfgvx_reverse_grid = {}
    for i, c in enumerate(adfgvx_grid_content[:36]):
        r, cc = i // 6, i % 6
        coord = adfgvx_letters[r] + adfgvx_letters[cc]
        adfgvx_grid[c] = coord
        adfgvx_reverse_grid[coord] = c
    
    # Try interpreting K4 letter pairs as ADFGVX coordinates
    # First map each K4 letter to ADFGVX if possible
    for mapping_key in ["KRYPTOS", "ABSCISSA"]:
        # Simple approach: take pairs of K4 chars, map to ADFGVX coords
        pairs_result = []
        for i in range(0, len(K4) - 1, 2):
            c1_idx = STANDARD_ALPHA.index(K4[i]) % 6
            c2_idx = STANDARD_ALPHA.index(K4[i+1]) % 6
            coord = adfgvx_letters[c1_idx] + adfgvx_letters[c2_idx]
            if coord in adfgvx_reverse_grid:
                pairs_result.append(adfgvx_reverse_grid[coord])
        result = ''.join(pairs_result)
        if result:
            report(f"ADFGVX-style pair decode", result, threshold=8)
    
    # c) Hill cipher with small matrices
    # 2x2 Hill cipher decryption
    def mod_inverse(a, m=26):
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return None
    
    def hill_decrypt_2x2(ciphertext, key_matrix):
        """Decrypt with 2x2 Hill cipher. key_matrix = [[a,b],[c,d]]"""
        a, b, c, d = key_matrix[0][0], key_matrix[0][1], key_matrix[1][0], key_matrix[1][1]
        det = (a * d - b * c) % 26
        det_inv = mod_inverse(det)
        if det_inv is None:
            return None
        # Inverse matrix
        inv = [
            [(d * det_inv) % 26, ((-b) * det_inv) % 26],
            [((-c) * det_inv) % 26, (a * det_inv) % 26]
        ]
        
        result = []
        nums = [STANDARD_ALPHA.index(c) for c in ciphertext.upper() if c in STANDARD_ALPHA]
        for i in range(0, len(nums) - 1, 2):
            p1 = (inv[0][0] * nums[i] + inv[0][1] * nums[i+1]) % 26
            p2 = (inv[1][0] * nums[i] + inv[1][1] * nums[i+1]) % 26
            result.append(STANDARD_ALPHA[p1])
            result.append(STANDARD_ALPHA[p2])
        return ''.join(result)
    
    # Try Hill cipher with key matrices derived from keywords
    print("\n  Testing Hill cipher 2x2 with keyword-derived matrices...")
    for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "EGYPT", "CLOCK"]:
        # Use first 4 chars of keyword as 2x2 matrix
        if len(kw) >= 4:
            key_mat = [
                [STANDARD_ALPHA.index(kw[0]), STANDARD_ALPHA.index(kw[1])],
                [STANDARD_ALPHA.index(kw[2]), STANDARD_ALPHA.index(kw[3])]
            ]
            result = hill_decrypt_2x2(K4, key_mat)
            if result:
                report(f"Hill 2x2 ({kw[:4]})", result)
    
    # d) Polybius square - encode K4 positions as two-digit numbers, then decode
    # Using KRYPTOS alphabet as Polybius key
    print("\n  Testing Polybius variants...")
    
    # Map K4 through Polybius: each letter -> (row,col) -> concatenate digits -> read as new letters
    for alpha_key in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
        aname = "KA" if alpha_key == KRYPTOS_ALPHA else "STD"
        digits = []
        for c in K4:
            if c in alpha_key:
                idx = alpha_key.index(c)
                r, cc = idx // 5, idx % 5
                digits.extend([r, cc])
        
        # Now read digit pairs as new positions
        reconstituted = []
        for i in range(0, len(digits) - 1, 2):
            idx = digits[i] * 5 + digits[i+1]
            if idx < len(alpha_key):
                reconstituted.append(alpha_key[idx])
        result = ''.join(reconstituted)
        report(f"Polybius round-trip ({aname})", result, threshold=8)
    
    print(f"\n  Matrix code tests complete.")


# ============================================================
# 6. K1-K3 METHOD PROGRESSION
# ============================================================
def test_k1k3_progression():
    print("\n" + "#"*70)
    print("# 6. K1-K3 METHOD PROGRESSION")
    print("#"*70)
    
    k3_key_order = [0, 3, 6, 2, 5, 1, 4]  # KRYPTOS numeric key
    
    # Generate permutations of operation order
    keywords_vig = ["PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLINCLOCK", 
                     "EASTNORTHEAST", "WELTZEITUHR"]
    
    # a) Vigenere THEN columnar transposition decrypt
    print("\n  Testing Vigenere then columnar transposition...")
    for kw in keywords_vig:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            
            # First Vigenere decrypt, then undo transposition
            vig_first = vigenere_decrypt(K4, kw, alpha)
            result = columnar_transposition_decrypt(vig_first, k3_key_order)
            report(f"Vig({kw},{aname}) then ColTrans(KRYPTOS)", result)
            
            # Beaufort variant
            beau_first = beaufort_decrypt(K4, kw, alpha)
            result = columnar_transposition_decrypt(beau_first, k3_key_order)
            report(f"Beaufort({kw},{aname}) then ColTrans(KRYPTOS)", result)
    
    # b) Columnar transposition decrypt THEN Vigenere
    print("\n  Testing columnar transposition then Vigenere...")
    trans_first = columnar_transposition_decrypt(K4, k3_key_order)
    report(f"ColTrans(KRYPTOS) alone", trans_first)
    
    for kw in keywords_vig:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            result = vigenere_decrypt(trans_first, kw, alpha)
            report(f"ColTrans(KRYPTOS) then Vig({kw},{aname})", result)
            
            result = beaufort_decrypt(trans_first, kw, alpha)
            report(f"ColTrans(KRYPTOS) then Beaufort({kw},{aname})", result)
    
    # c) Double transposition
    print("\n  Testing double transposition...")
    # Use PALIMPSEST as second transposition key
    palimpsest_key = []
    pword = "PALIMPSEST"
    sorted_chars = sorted(enumerate(pword), key=lambda x: x[1])
    for rank, (orig_idx, _) in enumerate(sorted_chars):
        palimpsest_key.append((orig_idx, rank))
    palimpsest_key.sort()
    palimpsest_order = [rank for _, rank in palimpsest_key]
    
    # ABSCISSA key
    aword = "ABSCISSA"
    sorted_chars = sorted(enumerate(aword), key=lambda x: (x[1], x[0]))
    abscissa_key = [0] * len(aword)
    for rank, (orig_idx, _) in enumerate(sorted_chars):
        abscissa_key[orig_idx] = rank
    
    for key1_name, key1 in [("KRYPTOS", k3_key_order), ("PALIMPSEST", palimpsest_order), ("ABSCISSA", abscissa_key)]:
        for key2_name, key2 in [("KRYPTOS", k3_key_order), ("PALIMPSEST", palimpsest_order), ("ABSCISSA", abscissa_key)]:
            if key1_name == key2_name:
                continue
            result1 = columnar_transposition_decrypt(K4, key1)
            result2 = columnar_transposition_decrypt(result1, key2)
            report(f"DoubleTrans({key1_name}+{key2_name})", result2)
    
    # d) Vigenere with K1 key, then Vigenere with K2 key (double Vigenere)
    print("\n  Testing double Vigenere...")
    for kw1 in ["PALIMPSEST", "ABSCISSA", "KRYPTOS"]:
        for kw2 in ["PALIMPSEST", "ABSCISSA", "KRYPTOS"]:
            if kw1 == kw2:
                continue
            for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                aname = "STD" if alpha == STANDARD_ALPHA else "KA"
                intermediate = vigenere_decrypt(K4, kw1, alpha)
                result = vigenere_decrypt(intermediate, kw2, alpha)
                report(f"DoubleVig({kw1}+{kw2},{aname})", result)
    
    # e) Progressive key: use KRYPTOS key extended by K1/K2 results
    # What if the key is PALIMPSESTABSCISSA (K1 key + K2 key)?
    combo_keys = [
        "PALIMPSESTABSCISSA",
        "ABSCISSAPALIMPSEST",
        "KRYPTOSPALIMPSEST",
        "KRYPTOSABSCISSA",
        "PALIMPSESTKRYPTOS",
        "ABSCISSAKRYPTOS",
    ]
    for ck in combo_keys:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            result = vigenere_decrypt(K4, ck, alpha)
            report(f"ComboKey Vig({ck},{aname})", result)
    
    # f) K3 method (keyed transposition) with different keywords
    print("\n  Testing keyed transposition with various keywords...")
    for kw_raw in KEYWORDS:
        # Generate numeric key from keyword
        sorted_chars = sorted(enumerate(kw_raw), key=lambda x: (x[1], x[0]))
        key_order = [0] * len(kw_raw)
        for rank, (orig_idx, _) in enumerate(sorted_chars):
            key_order[orig_idx] = rank
        
        result = columnar_transposition_decrypt(K4, key_order)
        report(f"ColTrans({kw_raw})", result)
        
        # Also try with Vigenere after
        for vig_kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
            vig_result = vigenere_decrypt(result, vig_kw)
            report(f"ColTrans({kw_raw})+Vig({vig_kw})", vig_result)
    
    # g) Reverse K4 then apply methods
    print("\n  Testing reversed K4...")
    k4_rev = K4[::-1]
    for kw in keywords_vig:
        result = vigenere_decrypt(k4_rev, kw)
        report(f"Reverse+Vig({kw})", result)
        result = columnar_transposition_decrypt(k4_rev, k3_key_order)
        report(f"Reverse+ColTrans(KRYPTOS)", result)
    
    print(f"\n  K1-K3 progression tests complete.")


# ============================================================
# 7. KEYWORD TESTING WITH ALL METHODS
# ============================================================
def test_keywords():
    print("\n" + "#"*70)
    print("# 7. KEYWORD TESTING (SANBORN'S CLUES)")
    print("#"*70)
    
    all_keywords = KEYWORDS + [
        "SHADOW", "LUCID", "FORCES", "MAGNETICFIELD",
        "COPPERPLATE", "LANGLEY", "CIA", "INVISIBLE",
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT",
        "IQLUSION", "UNDERGRUUND",  # K3 misspellings
        "DESPARATLY", "SLOWLY",
    ]
    
    # Test each keyword with both alphabets and multiple cipher types
    for kw in all_keywords:
        if len(kw) < 2:
            continue
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            
            # Standard Vigenere
            result = vigenere_decrypt(K4, kw, alpha)
            report(f"Vig({kw},{aname})", result)
            
            # Beaufort
            result = beaufort_decrypt(K4, kw, alpha)
            report(f"Beaufort({kw},{aname})", result)
            
            # Autokey (Vigenere autokey)
            autokey_result = []
            key_stream = list(kw.upper())
            for i, c in enumerate(K4):
                cn = char_to_num(c, alpha)
                kn = char_to_num(key_stream[i] if i < len(key_stream) else 'A', alpha)
                if cn >= 0 and kn >= 0:
                    plain_char = num_to_char((cn - kn) % len(alpha), alpha)
                    autokey_result.append(plain_char)
                    key_stream.append(plain_char)  # autokey extends with plaintext
                else:
                    autokey_result.append(c)
            result = ''.join(autokey_result)
            report(f"Autokey({kw},{aname})", result)
    
    print(f"\n  Keyword tests complete.")


# ============================================================
# 8. ADDITIONAL UNCONVENTIONAL APPROACHES
# ============================================================
def test_unconventional():
    print("\n" + "#"*70)
    print("# 8. ADDITIONAL UNCONVENTIONAL APPROACHES")
    print("#"*70)
    
    # a) Rail fence cipher (visual zigzag pattern)
    print("\n  Testing rail fence cipher...")
    for nrails in range(2, 10):
        # Decrypt rail fence
        cycle = 2 * (nrails - 1)
        if cycle == 0:
            continue
        
        # Calculate length of each rail
        rail_lengths = [0] * nrails
        for i in range(len(K4)):
            pos_in_cycle = i % cycle
            rail = pos_in_cycle if pos_in_cycle < nrails else cycle - pos_in_cycle
            rail_lengths[rail] += 1
        
        # Split ciphertext into rails
        rails = []
        start = 0
        for length in rail_lengths:
            rails.append(K4[start:start+length])
            start += length
        
        # Read off in zigzag order
        rail_indices = [0] * nrails
        result = []
        for i in range(len(K4)):
            pos_in_cycle = i % cycle
            rail = pos_in_cycle if pos_in_cycle < nrails else cycle - pos_in_cycle
            if rail_indices[rail] < len(rails[rail]):
                result.append(rails[rail][rail_indices[rail]])
                rail_indices[rail] += 1
        
        result_str = ''.join(result)
        report(f"Rail fence (rails={nrails})", result_str)
        
        # Rail fence then Vigenere
        for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
            vig_result = vigenere_decrypt(result_str, kw)
            report(f"Rail({nrails})+Vig({kw})", vig_result)
    
    # b) Route cipher through grid
    print("\n  Testing route cipher (various grid sizes)...")
    for nrows in [7, 8, 9, 10, 11]:
        ncols = math.ceil(len(K4) / nrows)
        # Pad K4
        padded = K4 + 'X' * (nrows * ncols - len(K4))
        
        # Create grid
        grid = []
        for r in range(nrows):
            grid.append(padded[r*ncols:(r+1)*ncols])
        
        # Route: vertical serpentine (down col 0, up col 1, down col 2, ...)
        route_result = []
        for c in range(ncols):
            if c % 2 == 0:
                for r in range(nrows):
                    route_result.append(grid[r][c])
            else:
                for r in range(nrows - 1, -1, -1):
                    route_result.append(grid[r][c])
        result = ''.join(route_result)[:len(K4)]
        report(f"Route serpentine ({nrows}x{ncols})", result)
    
    # c) Atbash cipher (mirror alphabet - simple visual reversal)
    atbash = ''.join(STANDARD_ALPHA[25 - STANDARD_ALPHA.index(c)] for c in K4)
    report("Atbash cipher", atbash)
    
    # Atbash with KRYPTOS alphabet
    atbash_k = ''.join(KRYPTOS_ALPHA[25 - KRYPTOS_ALPHA.index(c)] for c in K4)
    report("Atbash (KRYPTOS alphabet)", atbash_k)
    
    # Atbash then Vigenere
    for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
        result = vigenere_decrypt(atbash, kw)
        report(f"Atbash+Vig({kw})", result)
        result = vigenere_decrypt(atbash_k, kw, KRYPTOS_ALPHA)
        report(f"Atbash(KA)+Vig({kw},KA)", result)
    
    # d) Scytale cipher (ancient Greek - fits artist's interest in ancient writing)
    print("\n  Testing scytale cipher...")
    for diameter in range(2, 20):
        # Scytale unwrap: write in rows of width=diameter, read columns
        ncols = diameter
        nrows = math.ceil(len(K4) / ncols)
        padded = K4 + 'X' * (nrows * ncols - len(K4))
        
        # Read columns
        result_chars = []
        for c in range(ncols):
            for r in range(nrows):
                idx = r * ncols + c
                if idx < len(K4):
                    result_chars.append(padded[idx])
        result = ''.join(result_chars)[:len(K4)]
        report(f"Scytale (diameter={diameter})", result)
        
        # Also reverse: write in columns, read rows
        result_chars2 = []
        for r in range(nrows):
            for c in range(ncols):
                idx = c * nrows + r
                if idx < len(K4):
                    result_chars2.append(K4[idx])
        result2 = ''.join(result_chars2)[:len(K4)]
        report(f"Scytale reverse (diameter={diameter})", result2)
    
    # e) Skip cipher / every-nth-letter
    print("\n  Testing skip cipher (every nth letter)...")
    for skip in range(2, 20):
        for start in range(skip):
            extracted = K4[start::skip]
            if len(extracted) >= 8:
                report(f"Skip-{skip} start={start}", extracted, threshold=8)
    
    # f) Combination: physical grid + Vigenere with KRYPTOS alphabet
    # The 86+11 layout mentioned in the prompt
    print("\n  Testing 86+11 specific layout...")
    # 86 chars in main body, 11 in last row
    # If rows are ~12 chars: 7*12=84 + 13=97... or 8*11=88 + 9=97
    for main_chars, last_chars in [(86, 11), (84, 13), (88, 9)]:
        if main_chars + last_chars != len(K4):
            continue
        main_part = K4[:main_chars]
        last_part = K4[main_chars:]
        
        # Try various column counts for main part
        for ncols in range(10, 15):
            nrows = math.ceil(main_chars / ncols)
            grid = []
            for r in range(nrows):
                start = r * ncols
                end = min(start + ncols, main_chars)
                grid.append(main_part[start:end])
            grid.append(last_part)  # Add last row
            
            # Column read
            col_read = []
            max_cols = max(len(row) for row in grid)
            for c in range(max_cols):
                for row in grid:
                    if c < len(row):
                        col_read.append(row[c])
            result = ''.join(col_read)
            report(f"86+11 layout ({ncols}cols) column-read", result)
    
    # g) Nihilist cipher (Russian - Cold War theme)
    print("\n  Testing Nihilist-style cipher...")
    # Use KRYPTOS Polybius square, convert each letter to 2-digit number
    # Then subtract key values
    polybius_vals = {}
    for i, c in enumerate(KRYPTOS_ALPHA[:25]):
        r, cc = i // 5 + 1, i % 5 + 1
        polybius_vals[c] = r * 10 + cc
    polybius_vals['Z'] = 55
    
    k4_nums = [polybius_vals.get(c, 0) for c in K4]
    
    for kw in ["KRYPTOS", "BERLIN", "CLOCK"]:
        kw_nums = [polybius_vals.get(c, 0) for c in kw]
        # Subtract key cyclically
        result_nums = []
        for i, n in enumerate(k4_nums):
            diff = n - kw_nums[i % len(kw_nums)]
            r = ((diff // 10) - 1) % 5
            c = ((diff % 10) - 1) % 5
            idx = r * 5 + c
            if 0 <= idx < len(KRYPTOS_ALPHA):
                result_nums.append(KRYPTOS_ALPHA[idx])
            else:
                result_nums.append('?')
        result = ''.join(result_nums)
        report(f"Nihilist({kw}) KRYPTOS Polybius", result)
    
    print(f"\n  Unconventional tests complete.")


# ============================================================
# 9. COMBINED / LAYERED APPROACHES (Artist's "visual systems")
# ============================================================
def test_combined():
    print("\n" + "#"*70)
    print("# 9. COMBINED / LAYERED APPROACHES")
    print("#"*70)
    
    k3_key_order = [0, 3, 6, 2, 5, 1, 4]
    
    # a) Grid transposition + Vigenere + reversal combinations
    # Try: reverse -> grid column-read -> Vigenere
    k4_rev = K4[::-1]
    
    for ncols in [7, 8, 10, 11, 12, 13, 14]:
        nrows = math.ceil(len(K4) / ncols)
        padded = K4 + 'X' * (nrows * ncols - len(K4))
        
        # Column read
        col_read = []
        for c in range(ncols):
            for r in range(nrows):
                idx = r * ncols + c
                if idx < len(K4):
                    col_read.append(padded[idx])
        col_text = ''.join(col_read)[:len(K4)]
        
        for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "EASTNORTHEAST"]:
            for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
                aname = "STD" if alpha == STANDARD_ALPHA else "KA"
                result = vigenere_decrypt(col_text, kw, alpha)
                report(f"Grid({ncols}col)+Vig({kw},{aname})", result)
    
    # b) KRYPTOS transposition + keyword Vigenere with KRYPTOS alphabet
    trans = columnar_transposition_decrypt(K4, k3_key_order)
    for kw in KEYWORDS:
        result = vigenere_decrypt(trans, kw, KRYPTOS_ALPHA)
        report(f"Trans(KRYPTOS)+Vig({kw},KA)", result)
    
    # c) Try encryption direction (maybe Sanborn encrypted with these, so we need opposite)
    # What if K4 = Transposition(Vigenere(plaintext)) and we need to:
    # 1. Undo transposition first
    # 2. Then undo Vigenere
    # vs. what if K4 = Vigenere(Transposition(plaintext)) and we need:
    # 1. Undo Vigenere first  
    # 2. Then undo transposition
    
    for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK"]:
        for alpha in [STANDARD_ALPHA, KRYPTOS_ALPHA]:
            aname = "STD" if alpha == STANDARD_ALPHA else "KA"
            
            # Option 1: Undo vig, then undo trans
            step1 = vigenere_decrypt(K4, kw, alpha)
            step2 = columnar_transposition_decrypt(step1, k3_key_order)
            report(f"UndoVig({kw},{aname})->UndoTrans", step2)
            
            # Option 2: Undo trans, then undo vig
            step1 = columnar_transposition_decrypt(K4, k3_key_order)
            step2 = vigenere_decrypt(step1, kw, alpha)
            report(f"UndoTrans->UndoVig({kw},{aname})", step2)
    
    # d) Grille cipher (artist might use a physical mask/grille)
    # Test extracting every nth character at various offsets
    print("\n  Testing grille-like extractions...")
    for period in [2, 3, 4, 5, 7, 11, 13]:
        for offset in range(period):
            extracted = ''.join(K4[i] for i in range(offset, len(K4), period))
            remaining = ''.join(K4[i] for i in range(len(K4)) if i % period != offset)
            
            if len(extracted) >= 10:
                report(f"Grille extract period={period} offset={offset}", extracted, threshold=8)
            if len(remaining) >= 10:
                # Check if remaining has words  
                report(f"Grille remaining period={period} offset={offset}", remaining, threshold=10)
    
    # e) Berlin Wall + Egypt combination
    # Use date numbers as shifts with Egypt-themed keywords
    date_shifts = [1, 1, 9, 1, 9, 8, 9]
    date_shifted = []
    for i, c in enumerate(K4):
        s = date_shifts[i % len(date_shifts)]
        n = char_to_num(c)
        if n >= 0:
            date_shifted.append(num_to_char((n - s) % 26))
    date_text = ''.join(date_shifted)
    
    for kw in ["TUTANKHAMUN", "CARTER", "KRYPTOS", "BERLINCLOCK"]:
        result = vigenere_decrypt(date_text, kw)
        report(f"DateShift+Vig({kw})", result)
    
    # Also: Vigenere first, then date shift
    for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK"]:
        vig_first = vigenere_decrypt(K4, kw)
        date_shifted2 = []
        for i, c in enumerate(vig_first):
            s = date_shifts[i % len(date_shifts)]
            n = char_to_num(c)
            if n >= 0:
                date_shifted2.append(num_to_char((n - s) % 26))
        result = ''.join(date_shifted2)
        report(f"Vig({kw})+DateShift", result)
    
    print(f"\n  Combined approach tests complete.")


# ============================================================
# 10. EXHAUSTIVE VIGENERE WITH KRYPTOS ALPHABET
# ============================================================
def test_exhaustive_vigenere_kryptos():
    print("\n" + "#"*70)
    print("# 10. EXHAUSTIVE VIGENERE WITH KRYPTOS ALPHABET (short keys)")
    print("#"*70)
    
    # Test all 1-letter and 2-letter keys with KRYPTOS alphabet
    best_score = 0
    
    # 1-letter keys (Caesar shifts in KRYPTOS alphabet)
    for c in KRYPTOS_ALPHA:
        result = vigenere_decrypt(K4, c, KRYPTOS_ALPHA)
        covered, words = score_text(result)
        if covered > best_score:
            best_score = covered
            report(f"KA-Vig(key={c})", result, threshold=10)
    
    # 2-letter keys
    print("  Testing 2-letter KRYPTOS alphabet Vigenere keys...")
    for c1 in KRYPTOS_ALPHA:
        for c2 in KRYPTOS_ALPHA:
            key = c1 + c2
            result = vigenere_decrypt(K4, key, KRYPTOS_ALPHA)
            covered, words = score_text(result)
            if covered >= 14:
                report(f"KA-Vig(key={key})", result)
    
    print(f"\n  Exhaustive Vigenere tests complete. Best single-score: {best_score}")


# ============================================================
# MAIN
# ============================================================
def main():
    print("="*70)
    print("K4 ARTISTIC CIPHER - UNCONVENTIONAL APPROACHES")
    print("="*70)
    print(f"\nK4 ciphertext: {K4}")
    print(f"Length: {len(K4)}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Dictionary words loaded: {len(DICTIONARY)}")
    print(f"Words 4+ letters: {sum(1 for w in DICTIONARY if len(w) >= 4)}")
    
    # Frequency analysis of K4
    freq = Counter(K4)
    print(f"\nK4 letter frequencies:")
    for c, count in freq.most_common():
        print(f"  {c}: {count} ({100*count/len(K4):.1f}%)")
    
    # Run all tests
    test_physical_layout()
    test_compass_rose()
    test_egypt()
    test_berlin_wall()
    test_matrix_code()
    test_k1k3_progression()
    test_keywords()
    test_unconventional()
    test_combined()
    test_exhaustive_vigenere_kryptos()
    
    # Final summary
    print("\n" + "="*70)
    print("COMPLETE - All unconventional approaches tested.")
    print("="*70)
    print("\nNote: Any results with score >= 12 dictionary chars covered,")
    print("or containing known cribs (BERLINCLOCK, EASTNORTHEAST), were printed above.")
    print("Lower-scoring results were suppressed for readability.")


if __name__ == "__main__":
    main()
