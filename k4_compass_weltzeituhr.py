#!/usr/bin/env python3
"""
K4 Compass Rose / Weltzeituhr Transposition Analysis
=====================================================
NEW INTELLIGENCE: "BERLINCLOCK" in K4 refers to the Weltzeituhr (World Clock)
at Alexanderplatz, Berlin. It sits on a COMPASS ROSE shaped stone mosaic.
Kryptos itself also features a compass rose. Sanborn described K4 plaintext
as "scrambled text" (= transposition).

Hypothesis: The transposition pattern is based on compass directions or
the Weltzeituhr's properties.

Tests:
1. Compass Rose Grid Reading (8 directions, multiple grids)
2. Clock-Based Transposition (24 time zones, circular reading)
3. Compass Bearing Transposition (angular grid reading)
4. Alexanderplatz Connection (keyword columnar transposition)
5. Vigenere-then-Transposition with period-29 key
6. Transposition-then-Vigenere
7. Kryptos Compass Rose specific tests
"""

import math
import itertools
import os

# ============================================================================
# CONSTANTS
# ============================================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4)  # 97

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

BEST_VIG_KEY = "OYNKYELYOIECBAQKBQTNNRDUMRIYW"  # period-29 key

# Cribs to search for
CRIBS = [
    "BERLINCLOCK", "NORTHEAST", "EAST", "NORTH", "BERLIN", "CLOCK",
    "EGYPT", "CAIRO", "PYRAMID", "TOMB", "PHARAOH", "NILE",
    "WALL", "GATE", "ALEXANDERPLATZ", "WELTZEIT",
    "SHADOW", "UNDERGROUND", "BURIED", "HIDDEN", "SECRET",
    "COMPASS", "BEARING", "DEGREE", "LODESTONE",
    "SLOWLY", "DESPER", "THEEAR", "LAYER",
    "ITSHO", "ULDBE",  # "IT SHOULD BE"
    "WASIT",  # Sanborn hint fragments
    "VIRTUALLY", "INVISIBLE",
]

# Keywords to test as columnar transposition keys
KEYWORDS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "WELTZEITUHR",
    "ALEXANDERPLATZ", "COMPASSROSE", "SANBORN", "SCHEIDT", "EGYPT",
    "CAIRO", "PYRAMID", "LODESTONE", "NORTHEAST", "COMPASS",
    "WORLDCLOCK", "BERLIN", "CLOCK",
]

# ============================================================================
# QUADGRAM SCORER
# ============================================================================

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
        s = 0.0
        for i in range(len(text) - 3):
            gram = text[i:i+4]
            if gram in self.quadgrams:
                s += math.log10(self.quadgrams[gram] / self.total)
            else:
                s += self.floor
        return s

    def score_per_char(self, text):
        if len(text) < 4:
            return -99.0
        return self.score(text) / (len(text) - 3)

# ============================================================================
# CIPHER UTILITIES
# ============================================================================

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Decrypt ciphertext with Vigenere using given alphabet."""
    result = []
    ki = 0
    for c in ct:
        if c in alpha:
            ci = (alpha.index(c) - alpha.index(key[ki % len(key)])) % len(alpha)
            result.append(alpha[ci])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def vigenere_encrypt(pt, key, alpha=KRYPTOS_ALPHA):
    """Encrypt plaintext with Vigenere using given alphabet."""
    result = []
    ki = 0
    for c in pt:
        if c in alpha:
            ci = (alpha.index(c) + alpha.index(key[ki % len(key)])) % len(alpha)
            result.append(alpha[ci])
            ki += 1
        else:
            result.append(c)
    return ''.join(result)

def keyword_to_order(keyword):
    """Convert keyword to columnar transposition column order."""
    indexed = sorted(enumerate(keyword), key=lambda x: (x[1], x[0]))
    order = [0] * len(keyword)
    for rank, (orig_idx, _) in enumerate(indexed):
        order[orig_idx] = rank
    return order

def columnar_transpose(text, key_order):
    """Apply columnar transposition: write rows, read columns in key order."""
    cols = len(key_order)
    rows = math.ceil(len(text) / cols)
    # Pad text
    padded = text + 'X' * (rows * cols - len(text))
    # Build grid row by row
    grid = []
    for r in range(rows):
        grid.append(padded[r * cols:(r + 1) * cols])
    # Read columns in key order
    result = ''
    for col_rank in range(cols):
        col_idx = key_order.index(col_rank)
        for r in range(rows):
            if r * cols + col_idx < len(text):
                result += grid[r][col_idx]
    return result

def columnar_untranspose(text, key_order):
    """Reverse columnar transposition given key order."""
    cols = len(key_order)
    rows = math.ceil(len(text) / cols)
    extra = len(text) - (rows - 1) * cols  # number of full-length columns

    # Determine column lengths
    col_lens = []
    for i in range(cols):
        rank = key_order[i]
        if rank < extra:
            col_lens.append(rows)
        else:
            col_lens.append(rows - 1)

    # Read columns in rank order (rank 0 first, etc.)
    columns = [''] * cols
    pos = 0
    for rank in range(cols):
        col_idx = key_order.index(rank)
        clen = col_lens[col_idx]
        columns[col_idx] = text[pos:pos + clen]
        pos += clen

    # Read row by row
    result = ''
    for r in range(rows):
        for c in range(cols):
            if r < len(columns[c]):
                result += columns[c][r]
    return result

def check_cribs(text, label=""):
    """Check for cribs in text. Returns list of found cribs."""
    found = []
    text_upper = text.upper()
    for crib in CRIBS:
        idx = text_upper.find(crib)
        if idx != -1:
            found.append((crib, idx))
    return found

def rail_fence_decrypt(text, rails):
    """Decrypt rail fence cipher."""
    n = len(text)
    # Calculate the pattern
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for i in range(n):
        fence[rail].append(i)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    # Fill in the characters
    result = [''] * n
    idx = 0
    for r in range(rails):
        for pos in fence[r]:
            result[pos] = text[idx]
            idx += 1
    return ''.join(result)

def rail_fence_encrypt(text, rails):
    """Encrypt with rail fence cipher."""
    n = len(text)
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1
    for i in range(n):
        fence[rail].append(i)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    result = ''
    for r in range(rails):
        for pos in fence[r]:
            result += text[pos]
    return result

# ============================================================================
# TEST 1: COMPASS ROSE GRID READING
# ============================================================================

def test_compass_rose_grid(scorer):
    """Lay out text in grids and read following compass directions."""
    print("\n" + "=" * 70)
    print("TEST 1: COMPASS ROSE GRID READING")
    print("=" * 70)
    print("Lay K4 in various grids, read following 8 compass directions")

    grids = [(7, 14), (8, 13), (9, 11), (10, 10), (11, 9), (13, 8), (14, 7),
             (97, 1), (1, 97)]  # degenerate cases

    best_results = []

    for rows, cols in grids:
        if rows * cols < K4_LEN:
            continue
        padded = K4 + 'X' * (rows * cols - K4_LEN)

        # Build grid
        grid = []
        for r in range(rows):
            grid.append(padded[r * cols:(r + 1) * cols])

        # Read in 8 compass directions from each corner and midpoint
        directions = {
            'N_to_S': [],       # Top to bottom, left to right
            'S_to_N': [],       # Bottom to top, left to right
            'E_to_W': [],       # Right to left, top to bottom
            'W_to_E': [],       # Left to right, top to bottom (normal)
            'NW_to_SE': [],     # Diagonal
            'NE_to_SW': [],     # Diagonal
            'SE_to_NW': [],     # Diagonal
            'SW_to_NE': [],     # Diagonal
            'spiral_CW': [],    # Clockwise spiral inward
            'spiral_CCW': [],   # Counter-clockwise spiral
            'cols_first': [],   # Read columns first (column-major)
            'cols_rev': [],     # Read columns in reverse
            'snake': [],        # Boustrophedon
        }

        # N to S: read column by column, top to bottom
        for c in range(cols):
            for r in range(rows):
                directions['N_to_S'].append(grid[r][c])

        # S to N: read column by column, bottom to top
        for c in range(cols):
            for r in range(rows - 1, -1, -1):
                directions['S_to_N'].append(grid[r][c])

        # W to E: normal row reading
        for r in range(rows):
            for c in range(cols):
                directions['W_to_E'].append(grid[r][c])

        # E to W: row reading reversed
        for r in range(rows):
            for c in range(cols - 1, -1, -1):
                directions['E_to_W'].append(grid[r][c])

        # NW to SE: read diagonals starting from top-left
        for d in range(rows + cols - 1):
            for r in range(rows):
                c = d - r
                if 0 <= c < cols:
                    directions['NW_to_SE'].append(grid[r][c])

        # NE to SW: read diagonals starting from top-right
        for d in range(rows + cols - 1):
            for r in range(rows):
                c = (cols - 1) - (d - r)
                if 0 <= c < cols:
                    directions['NE_to_SW'].append(grid[r][c])

        # SE to NW: reverse of NW_to_SE
        directions['SE_to_NW'] = directions['NW_to_SE'][::-1]

        # SW to NE: reverse of NE_to_SW
        directions['SW_to_NE'] = directions['NE_to_SW'][::-1]

        # Spiral clockwise
        visited = [[False] * cols for _ in range(rows)]
        r, c = 0, 0
        dr, dc = 0, 1  # Start going right
        for _ in range(rows * cols):
            directions['spiral_CW'].append(grid[r][c])
            visited[r][c] = True
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                r, c = nr, nc
            else:
                # Turn clockwise: right->down->left->up
                dr, dc = dc, -dr
                r, c = r + dr, c + dc

        # Spiral counter-clockwise
        visited = [[False] * cols for _ in range(rows)]
        r, c = 0, 0
        dr, dc = 1, 0  # Start going down
        for _ in range(rows * cols):
            directions['spiral_CCW'].append(grid[r][c])
            visited[r][c] = True
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                r, c = nr, nc
            else:
                # Turn counter-clockwise: down->right->up->left
                dr, dc = -dc, dr
                r, c = r + dr, c + dc

        # Column-major reading
        for c in range(cols):
            for r in range(rows):
                directions['cols_first'].append(grid[r][c])

        # Reverse column reading
        for c in range(cols - 1, -1, -1):
            for r in range(rows):
                directions['cols_rev'].append(grid[r][c])

        # Snake / boustrophedon
        for r in range(rows):
            if r % 2 == 0:
                for c in range(cols):
                    directions['snake'].append(grid[r][c])
            else:
                for c in range(cols - 1, -1, -1):
                    directions['snake'].append(grid[r][c])

        for direction_name, chars in directions.items():
            text = ''.join(chars)[:K4_LEN]  # Trim padding
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"{rows}x{cols} {direction_name}", text, cribs))

    # Sort and print best
    best_results.sort(reverse=True)
    print(f"\n  Top 15 compass grid readings:")
    for sc, label, text, cribs in best_results[:15]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    # Check all for cribs
    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 2: CLOCK-BASED TRANSPOSITION
# ============================================================================

def test_clock_transposition(scorer):
    """Treat K4 as arranged on a clock face and read by time zones."""
    print("\n" + "=" * 70)
    print("TEST 2: CLOCK-BASED TRANSPOSITION")
    print("=" * 70)
    print("Weltzeituhr: 148 cities, 24 time zones")
    print("Arrange 97 chars in a circle, read by various clock patterns")

    best_results = []

    # 2A: Arrange in circle, read every N-th character
    print("\n  2A: Read every N-th character from circular arrangement")
    for step in range(1, K4_LEN):
        if math.gcd(step, K4_LEN) != 1:
            continue  # Skip non-coprime steps (won't visit all positions)
        text = ''
        for i in range(K4_LEN):
            text += K4[(i * step) % K4_LEN]
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"step={step}", text, cribs))

    # 2B: 24 time zones - arrange text in 24 groups
    print("  2B: 24 time-zone based grouping")
    for start_offset in range(24):
        # Group chars into 24 time zones
        groups = [[] for _ in range(24)]
        for i, ch in enumerate(K4):
            zone = (i + start_offset) % 24
            groups[zone].append(ch)

        # Read groups in different orders
        # Forward order
        text = ''.join(''.join(g) for g in groups)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"24tz_fwd_off={start_offset}", text, cribs))

        # Reverse order
        text = ''.join(''.join(g) for g in reversed(groups))
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"24tz_rev_off={start_offset}", text, cribs))

        # Interleave: even zones then odd zones
        even = [groups[i] for i in range(0, 24, 2)]
        odd = [groups[i] for i in range(1, 24, 2)]
        text = ''.join(''.join(g) for g in even + odd)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"24tz_intlv_off={start_offset}", text, cribs))

    # 2C: Read starting from each position in the circle
    print("  2C: Circular starting positions")
    for start in range(K4_LEN):
        text = K4[start:] + K4[:start]
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"rotate_start={start}", text, cribs))

    # 2D: 24 segments, read alternating direction (clock hands)
    print("  2D: Clock-hand alternating direction reads")
    segment_size = K4_LEN // 24  # ~4 chars per segment
    for start_offset in range(24):
        chars = []
        for seg in range(24):
            actual_seg = (seg + start_offset) % 24
            begin = actual_seg * segment_size
            end = min(begin + segment_size, K4_LEN)
            segment_chars = list(K4[begin:end])
            if seg % 2 == 1:
                segment_chars.reverse()
            chars.extend(segment_chars)
        # Append any remaining characters
        if 24 * segment_size < K4_LEN:
            chars.extend(K4[24 * segment_size:])
        text = ''.join(chars)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"clockhand_off={start_offset}", text, cribs))

    best_results.sort(reverse=True)
    print(f"\n  Top 15 clock-based transpositions:")
    for sc, label, text, cribs in best_results[:15]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 3: COMPASS BEARING TRANSPOSITION
# ============================================================================

def test_compass_bearing(scorer):
    """Read grid at various compass bearing angles."""
    print("\n" + "=" * 70)
    print("TEST 3: COMPASS BEARING TRANSPOSITION")
    print("=" * 70)
    print("Read grid at angles: 0, 22.5, 45, 67.5, 90, etc.")

    best_results = []
    grids = [(7, 14), (8, 13), (9, 11), (10, 10), (11, 9)]

    for rows, cols in grids:
        if rows * cols < K4_LEN:
            continue
        padded = K4 + 'X' * (rows * cols - K4_LEN)
        grid = []
        for r in range(rows):
            grid.append(padded[r * cols:(r + 1) * cols])

        # For each bearing angle, read characters along parallel lines at that angle
        for bearing_idx in range(16):  # 0 to 337.5 in steps of 22.5
            angle_deg = bearing_idx * 22.5
            angle_rad = math.radians(angle_deg)

            # Direction vector
            dx = math.sin(angle_rad)
            dy = -math.cos(angle_rad)  # negative because row 0 is top (north)

            # For each angle, we need to define "scan lines" perpendicular to this direction
            # and read characters along them
            # Perpendicular direction
            px = -dy
            py = dx

            # Collect all grid positions with their projection onto the perpendicular axis
            positions = []
            for r in range(rows):
                for c in range(cols):
                    # Project onto perpendicular direction for ordering scan lines
                    perp_proj = c * px + r * py
                    # Project onto main direction for ordering within scan line
                    main_proj = c * dx + r * dy
                    positions.append((perp_proj, main_proj, r, c))

            # Sort: primary by perpendicular projection, secondary by main projection
            positions.sort()
            text = ''.join(grid[r][c] for _, _, r, c in positions)[:K4_LEN]
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"{rows}x{cols} bearing={angle_deg:.1f}", text, cribs))

            # Also try reversed main direction
            positions2 = [(pp, -mp, r, c) for pp, mp, r, c in positions]
            positions2.sort()
            text2 = ''.join(grid[r][c] for _, _, r, c in positions2)[:K4_LEN]
            sc2 = scorer.score_per_char(text2)
            cribs2 = check_cribs(text2)
            best_results.append((sc2, f"{rows}x{cols} bearing={angle_deg:.1f}_rev", text2, cribs2))

    best_results.sort(reverse=True)
    print(f"\n  Top 15 bearing-based reads:")
    for sc, label, text, cribs in best_results[:15]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 4: ALEXANDERPLATZ CONNECTION
# ============================================================================

def test_alexanderplatz_keywords(scorer):
    """Test keyword-based columnar transposition with thematic keywords."""
    print("\n" + "=" * 70)
    print("TEST 4: ALEXANDERPLATZ CONNECTION - KEYWORD COLUMNAR TRANSPOSITION")
    print("=" * 70)

    test_keywords = [
        "ALEXANDERPLATZ",   # 14 letters
        "WELTZEITUHR",      # 11 letters
        "WORLDCLOCK",       # 10 letters
        "COMPASSROSE",      # 11 letters
        "BERLINCLOCK",      # 11 letters
        "KRYPTOS",          # 7 letters
        "PALIMPSEST",       # 10 letters
        "ABSCISSA",         # 8 letters
        "SANBORN",          # 7 letters
        "SCHEIDT",          # 7 letters
        "LODESTONE",        # 9 letters
        "NORTHEAST",        # 9 letters
        "EASTNORTHEAST",    # 13 letters
        "PYRAMID",          # 7 letters
        "EGYPT",            # 5 letters
        "CAIRO",            # 5 letters
        "COMPASS",          # 7 letters
        "BEARING",          # 7 letters
    ]

    best_results = []

    for kw in test_keywords:
        order = keyword_to_order(kw)

        # Untranspose (decrypt columnar)
        text = columnar_untranspose(K4, order)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"untransp({kw})", text, cribs))

        # Transpose (encrypt columnar) - in case it was "encrypt" style
        text2 = columnar_transpose(K4, order)
        sc2 = scorer.score_per_char(text2)
        cribs2 = check_cribs(text2)
        best_results.append((sc2, f"transp({kw})", text2, cribs2))

        # Also try reversed keyword order
        rev_order = [len(order) - 1 - x for x in order]
        text3 = columnar_untranspose(K4, rev_order)
        sc3 = scorer.score_per_char(text3)
        cribs3 = check_cribs(text3)
        best_results.append((sc3, f"untransp_rev({kw})", text3, cribs3))

    # Also try rail fence with various rail counts
    print("\n  Also testing rail fence...")
    for rails in range(2, 20):
        text = rail_fence_decrypt(K4, rails)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"railfence_dec(rails={rails})", text, cribs))

        text2 = rail_fence_encrypt(K4, rails)
        sc2 = scorer.score_per_char(text2)
        cribs2 = check_cribs(text2)
        best_results.append((sc2, f"railfence_enc(rails={rails})", text2, cribs2))

    best_results.sort(reverse=True)
    print(f"\n  Top 20 keyword transpositions:")
    for sc, label, text, cribs in best_results[:20]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 5: VIGENERE THEN TRANSPOSITION
# ============================================================================

def test_vigenere_then_transposition(scorer):
    """First Vigenere decrypt K4, then try various untranspositions."""
    print("\n" + "=" * 70)
    print("TEST 5: VIGENERE THEN TRANSPOSITION")
    print("=" * 70)
    print(f"First Vigenere decrypt with period-29 key: {BEST_VIG_KEY}")
    print("Then try keyword-based columnar un-transposition")

    # Step 1: Vigenere decrypt
    vig_decrypted = vigenere_decrypt(K4, BEST_VIG_KEY, KRYPTOS_ALPHA)
    print(f"\n  After Vigenere decryption: {vig_decrypted}")
    print(f"  Score: {scorer.score_per_char(vig_decrypted):.4f}")

    # Also try with standard alphabet
    vig_decrypted_std = vigenere_decrypt(K4, BEST_VIG_KEY, STANDARD_ALPHA)
    print(f"  With standard alphabet:   {vig_decrypted_std}")
    print(f"  Score: {scorer.score_per_char(vig_decrypted_std):.4f}")

    best_results = []

    for vig_text, alpha_label in [(vig_decrypted, "kryptos"), (vig_decrypted_std, "std")]:
        # Step 2: Try columnar un-transposition with each keyword
        for kw in KEYWORDS:
            order = keyword_to_order(kw)

            # Untranspose
            text = columnar_untranspose(vig_text, order)
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"vig({alpha_label})+untransp({kw})", text, cribs))

            # Transpose (reverse direction)
            text2 = columnar_transpose(vig_text, order)
            sc2 = scorer.score_per_char(text2)
            cribs2 = check_cribs(text2)
            best_results.append((sc2, f"vig({alpha_label})+transp({kw})", text2, cribs2))

        # Also try rail fence after Vigenere
        for rails in range(2, 15):
            text = rail_fence_decrypt(vig_text, rails)
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"vig({alpha_label})+railfence({rails})", text, cribs))

        # Try simple reversals and rotations
        text = vig_text[::-1]
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"vig({alpha_label})+reverse", text, cribs))

        for start in range(1, K4_LEN):
            text = vig_text[start:] + vig_text[:start]
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            if cribs or sc > -3.5:
                best_results.append((sc, f"vig({alpha_label})+rotate({start})", text, cribs))

        # Try reading every nth character (decimation)
        for step in range(2, 50):
            if math.gcd(step, K4_LEN) == 1:
                text = ''.join(vig_text[(i * step) % K4_LEN] for i in range(K4_LEN))
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                best_results.append((sc, f"vig({alpha_label})+decimate({step})", text, cribs))

    best_results.sort(reverse=True)
    print(f"\n  Top 20 Vigenere-then-transposition results:")
    for sc, label, text, cribs in best_results[:20]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 6: TRANSPOSITION THEN VIGENERE
# ============================================================================

def test_transposition_then_vigenere(scorer):
    """First un-transpose K4 with keyword, then Vigenere decrypt."""
    print("\n" + "=" * 70)
    print("TEST 6: TRANSPOSITION THEN VIGENERE")
    print("=" * 70)
    print("First un-transpose K4 with keyword, then Vigenere decrypt")
    print(f"Vigenere key: {BEST_VIG_KEY}")

    best_results = []

    for kw in KEYWORDS:
        order = keyword_to_order(kw)

        for direction, func in [("untransp", columnar_untranspose),
                                ("transp", columnar_transpose)]:
            untransposed = func(K4, order)

            # Then Vigenere decrypt
            for alpha, alpha_label in [(KRYPTOS_ALPHA, "kryptos"), (STANDARD_ALPHA, "std")]:
                text = vigenere_decrypt(untransposed, BEST_VIG_KEY, alpha)
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                best_results.append((sc, f"{direction}({kw})+vig({alpha_label})", text, cribs))

    # Also try rail fence then Vigenere
    for rails in range(2, 15):
        for rf_func, rf_label in [(rail_fence_decrypt, "rf_dec"),
                                   (rail_fence_encrypt, "rf_enc")]:
            untransposed = rf_func(K4, rails)
            for alpha, alpha_label in [(KRYPTOS_ALPHA, "kryptos"), (STANDARD_ALPHA, "std")]:
                text = vigenere_decrypt(untransposed, BEST_VIG_KEY, alpha)
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                best_results.append((sc, f"{rf_label}({rails})+vig({alpha_label})", text, cribs))

    # Try decimation then Vigenere
    for step in range(2, 50):
        if math.gcd(step, K4_LEN) == 1:
            untransposed = ''.join(K4[(i * step) % K4_LEN] for i in range(K4_LEN))
            for alpha, alpha_label in [(KRYPTOS_ALPHA, "kryptos"), (STANDARD_ALPHA, "std")]:
                text = vigenere_decrypt(untransposed, BEST_VIG_KEY, alpha)
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                best_results.append((sc, f"decimate({step})+vig({alpha_label})", text, cribs))

    # Try rotation then Vigenere
    for start in range(1, K4_LEN):
        rotated = K4[start:] + K4[:start]
        for alpha, alpha_label in [(KRYPTOS_ALPHA, "kryptos"), (STANDARD_ALPHA, "std")]:
            text = vigenere_decrypt(rotated, BEST_VIG_KEY, alpha)
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            if cribs or sc > -3.5:
                best_results.append((sc, f"rotate({start})+vig({alpha_label})", text, cribs))

    best_results.sort(reverse=True)
    print(f"\n  Top 20 Transposition-then-Vigenere results:")
    for sc, label, text, cribs in best_results[:20]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# TEST 7: KRYPTOS COMPASS ROSE SPECIFIC TESTS
# ============================================================================

def test_kryptos_compass_rose(scorer):
    """Test patterns specific to the Kryptos compass rose at CIA."""
    print("\n" + "=" * 70)
    print("TEST 7: KRYPTOS COMPASS ROSE SPECIFIC TESTS")
    print("=" * 70)
    print("The Kryptos compass rose has N/S/E/W markings and a lodestone")
    print("Testing compass-rose-inspired transposition patterns")

    best_results = []

    # 7A: The compass rose has 4 cardinal + 4 ordinal directions = 8 sectors
    # Divide K4 into 8 sectors and rearrange
    print("\n  7A: 8-sector rearrangement (compass sectors)")
    sector_size = K4_LEN // 8  # ~12 chars per sector
    remainder = K4_LEN % 8

    sectors = []
    pos = 0
    for i in range(8):
        sz = sector_size + (1 if i < remainder else 0)
        sectors.append(K4[pos:pos + sz])
        pos += sz

    # Compass direction orderings (N=0, NE=1, E=2, SE=3, S=4, SW=5, W=6, NW=7)
    compass_orders = {
        'NESW_CW': [0, 1, 2, 3, 4, 5, 6, 7],
        'NESW_CCW': [0, 7, 6, 5, 4, 3, 2, 1],
        'cardinals_first': [0, 2, 4, 6, 1, 3, 5, 7],
        'ordinals_first': [1, 3, 5, 7, 0, 2, 4, 6],
        'opposite_pairs': [0, 4, 1, 5, 2, 6, 3, 7],
        'cross_pattern': [0, 4, 2, 6, 1, 5, 3, 7],
        'zigzag_NS': [0, 4, 1, 5, 2, 6, 3, 7],
        'reverse': [7, 6, 5, 4, 3, 2, 1, 0],
        'from_E': [2, 3, 4, 5, 6, 7, 0, 1],      # Starting from East
        'from_NE': [1, 2, 3, 4, 5, 6, 7, 0],     # Starting from NE (EASTNORTHEAST direction)
        'from_ENE_skip': [1, 3, 5, 7, 0, 2, 4, 6],  # NE, starting skip
    }

    for name, order in compass_orders.items():
        text = ''.join(sectors[i] for i in order)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"8sector_{name}", text, cribs))

        # Also try reversing each sector
        text2 = ''.join(sectors[i][::-1] for i in order)
        sc2 = scorer.score_per_char(text2)
        cribs2 = check_cribs(text2)
        best_results.append((sc2, f"8sector_{name}_revchars", text2, cribs2))

    # 7B: Interleave from opposite compass points
    print("  7B: Interleave from opposite compass points")
    # N(0) vs S(4), NE(1) vs SW(5), E(2) vs W(6), SE(3) vs NW(7)
    pairs = [(0, 4), (1, 5), (2, 6), (3, 7)]
    for pair_order in itertools.permutations(pairs):
        text = ''
        for a, b in pair_order:
            # Interleave characters from sector a and sector b
            sa, sb = sectors[a], sectors[b]
            for i in range(max(len(sa), len(sb))):
                if i < len(sa):
                    text += sa[i]
                if i < len(sb):
                    text += sb[i]
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"interleave_pairs_{pair_order}", text, cribs))

    # 7C: Compass rose has 32 points (every 11.25 degrees)
    # But 97 doesn't divide well. Try 32 sectors anyway.
    print("  7C: 32-point compass (every 11.25 degrees)")
    # Arrange as 32 groups, read in various orders
    groups32 = [[] for _ in range(32)]
    for i, ch in enumerate(K4):
        groups32[i % 32].append(ch)

    # Read in standard 32-point order
    text = ''.join(''.join(g) for g in groups32)
    sc = scorer.score_per_char(text)
    cribs = check_cribs(text)
    best_results.append((sc, f"32pt_mod32", text, cribs))

    # Read every other group (interleave)
    for step in [2, 3, 4, 8, 16]:
        if math.gcd(step, 32) == 1 or step == 2:
            order = []
            visited = set()
            idx = 0
            while len(visited) < 32:
                if idx not in visited:
                    order.append(idx)
                    visited.add(idx)
                idx = (idx + step) % 32
                if idx in visited and len(visited) < 32:
                    # Find next unvisited
                    for j in range(32):
                        if j not in visited:
                            idx = j
                            break
            text = ''.join(''.join(groups32[i]) for i in order)
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"32pt_step{step}", text, cribs))

    # 7D: The compass rose layout - arrange in concentric rings
    print("  7D: Concentric ring arrangement (like compass rose)")
    # Try various ring configurations
    ring_configs = [
        [1, 8, 16, 24, 48],   # 1 center + rings
        [1, 4, 8, 16, 32, 36], # inner to outer
        [4, 8, 12, 16, 20, 24, 13],  # evenly growing
        [8, 16, 24, 32, 17],   # compass-like
        [12, 12, 12, 12, 12, 12, 12, 13],  # 8 equal-ish sectors of ~12
    ]

    for config_idx, ring_sizes in enumerate(ring_configs):
        if sum(ring_sizes) != K4_LEN:
            # Adjust last ring
            ring_sizes = list(ring_sizes)
            ring_sizes[-1] = K4_LEN - sum(ring_sizes[:-1])
            if ring_sizes[-1] <= 0:
                continue

        rings = []
        pos = 0
        valid = True
        for sz in ring_sizes:
            if sz <= 0 or pos + sz > K4_LEN:
                valid = False
                break
            rings.append(K4[pos:pos + sz])
            pos += sz
        if not valid or pos != K4_LEN:
            continue

        # Read rings in different orders
        # Inside out
        text = ''.join(rings)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"rings_in_out_{config_idx}", text, cribs))

        # Outside in
        text = ''.join(reversed(rings))
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"rings_out_in_{config_idx}", text, cribs))

        # Alternating direction per ring
        alt_text = ''
        for i, ring in enumerate(rings):
            if i % 2 == 0:
                alt_text += ring
            else:
                alt_text += ring[::-1]
        sc = scorer.score_per_char(alt_text)
        cribs = check_cribs(alt_text)
        best_results.append((sc, f"rings_alt_{config_idx}", alt_text, cribs))

    # 7E: Lodestone / magnetic deviation pattern
    print("  7E: Lodestone/magnetic deviation pattern")
    # Magnetic declination at CIA HQ (Langley, VA) is about -10 degrees
    # Try shifting the reading pattern by various amounts
    for cols in [7, 8, 9, 10, 11, 13, 14]:
        rows = math.ceil(K4_LEN / cols)
        padded = K4 + 'X' * (rows * cols - K4_LEN)
        grid = []
        for r in range(rows):
            grid.append(padded[r * cols:(r + 1) * cols])

        # Read with offset per row (like magnetic deviation)
        for offset_per_row in range(1, cols):
            text = ''
            for r in range(rows):
                for c in range(cols):
                    actual_c = (c + r * offset_per_row) % cols
                    if r * cols + actual_c < K4_LEN:
                        text += grid[r][actual_c]
            text = text[:K4_LEN]
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            best_results.append((sc, f"lodestone_{cols}col_shift{offset_per_row}", text, cribs))

    # 7F: True North vs Magnetic North offset
    # The Kryptos compass rose is reportedly misaligned by a few degrees
    # This could mean reading with a systematic offset
    print("  7F: Compass misalignment patterns")
    for offset in range(1, K4_LEN):
        # Read: take char at position i, place it at position (i + offset) % 97
        result = [''] * K4_LEN
        for i in range(K4_LEN):
            result[(i + offset) % K4_LEN] = K4[i]
        text = ''.join(result)
        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"misalign_offset={offset}", text, cribs))

    best_results.sort(reverse=True)
    print(f"\n  Top 20 Kryptos compass rose results:")
    for sc, label, text, cribs in best_results[:20]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# BONUS: COMBINED DOUBLE TRANSPOSITION
# ============================================================================

def test_double_transposition(scorer):
    """Test double transposition (two keywords)."""
    print("\n" + "=" * 70)
    print("BONUS: DOUBLE TRANSPOSITION (two keyword combination)")
    print("=" * 70)

    short_keywords = [kw for kw in KEYWORDS if len(kw) <= 11]
    best_results = []

    for kw1 in short_keywords:
        order1 = keyword_to_order(kw1)
        step1 = columnar_untranspose(K4, order1)
        for kw2 in short_keywords:
            if kw1 == kw2:
                continue
            order2 = keyword_to_order(kw2)
            text = columnar_untranspose(step1, order2)
            sc = scorer.score_per_char(text)
            cribs = check_cribs(text)
            if cribs or sc > -3.8:
                best_results.append((sc, f"double_untransp({kw1},{kw2})", text, cribs))

    best_results.sort(reverse=True)
    print(f"\n  Top 15 double transposition results:")
    for sc, label, text, cribs in best_results[:15]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# BONUS 2: SCYTALE CIPHER (wrapping around a cylinder)
# ============================================================================

def test_scytale(scorer):
    """Test scytale cipher - text wrapped around cylinder of various diameters."""
    print("\n" + "=" * 70)
    print("BONUS 2: SCYTALE CIPHER (cylinder wrapping)")
    print("=" * 70)
    print("A scytale is a transposition cipher using a cylinder, related to")
    print("compass/circular themes.")

    best_results = []

    for diameter in range(2, 49):
        # Scytale decrypt: text was written in rows of width=diameter
        # To decrypt, we read column by column
        cols = diameter
        rows = math.ceil(K4_LEN / cols)
        padded = K4 + 'X' * (rows * cols - K4_LEN)

        # Read column by column
        text = ''
        for c in range(cols):
            for r in range(rows):
                idx = r * cols + c
                if idx < K4_LEN:
                    text += padded[idx]
        text = text[:K4_LEN]

        sc = scorer.score_per_char(text)
        cribs = check_cribs(text)
        best_results.append((sc, f"scytale_d={diameter}", text, cribs))

        # Also try the inverse: read row by row from column-arranged text
        text2 = ''
        for r in range(rows):
            for c in range(cols):
                idx = c * rows + r
                if idx < K4_LEN:
                    text2 += K4[idx]
        text2 = text2[:K4_LEN]

        sc2 = scorer.score_per_char(text2)
        cribs2 = check_cribs(text2)
        best_results.append((sc2, f"scytale_inv_d={diameter}", text2, cribs2))

    best_results.sort(reverse=True)
    print(f"\n  Top 10 scytale results:")
    for sc, label, text, cribs in best_results[:10]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# BONUS 3: TRANSPOSITION + VIGENERE WITH MULTIPLE SHORT KEYS
# ============================================================================

def test_transposition_various_vig_keys(scorer):
    """Try transposition with various Vigenere keys (not just period-29)."""
    print("\n" + "=" * 70)
    print("BONUS 3: TRANSPOSITION + VARIOUS VIGENERE KEYS")
    print("=" * 70)
    print("Try the keyword transpositions combined with simpler Vigenere keys")

    vig_keys = [
        "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "WELTZEITUHR",
        "ALEXANDERPLATZ", "COMPASSROSE", "SANBORN", "SCHEIDT",
        "NORTHEAST", "LODESTONE", "SHADOW", "SECRET",
    ]

    transp_keywords = [
        "KRYPTOS", "BERLINCLOCK", "WELTZEITUHR", "ALEXANDERPLATZ",
        "COMPASSROSE", "NORTHEAST", "LODESTONE",
    ]

    best_results = []

    # Approach A: Vigenere decrypt THEN un-transpose
    print("  Approach A: Vigenere decrypt then un-transpose")
    for vk in vig_keys:
        for alpha, alpha_label in [(KRYPTOS_ALPHA, "kr"), (STANDARD_ALPHA, "st")]:
            vig_dec = vigenere_decrypt(K4, vk, alpha)
            for tk in transp_keywords:
                order = keyword_to_order(tk)
                text = columnar_untranspose(vig_dec, order)
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                if cribs or sc > -3.8:
                    best_results.append((sc, f"vig_{alpha_label}({vk})+untransp({tk})", text, cribs))

                text2 = columnar_transpose(vig_dec, order)
                sc2 = scorer.score_per_char(text2)
                cribs2 = check_cribs(text2)
                if cribs2 or sc2 > -3.8:
                    best_results.append((sc2, f"vig_{alpha_label}({vk})+transp({tk})", text2, cribs2))

    # Approach B: Un-transpose THEN Vigenere decrypt
    print("  Approach B: Un-transpose then Vigenere decrypt")
    for tk in transp_keywords:
        order = keyword_to_order(tk)
        untransposed = columnar_untranspose(K4, order)
        transposed = columnar_transpose(K4, order)

        for vk in vig_keys:
            for alpha, alpha_label in [(KRYPTOS_ALPHA, "kr"), (STANDARD_ALPHA, "st")]:
                text = vigenere_decrypt(untransposed, vk, alpha)
                sc = scorer.score_per_char(text)
                cribs = check_cribs(text)
                if cribs or sc > -3.8:
                    best_results.append((sc, f"untransp({tk})+vig_{alpha_label}({vk})", text, cribs))

                text2 = vigenere_decrypt(transposed, vk, alpha)
                sc2 = scorer.score_per_char(text2)
                cribs2 = check_cribs(text2)
                if cribs2 or sc2 > -3.8:
                    best_results.append((sc2, f"transp({tk})+vig_{alpha_label}({vk})", text2, cribs2))

    best_results.sort(reverse=True)
    print(f"\n  Top 20 transposition + various Vigenere results:")
    for sc, label, text, cribs in best_results[:20]:
        crib_str = f"  CRIBS: {cribs}" if cribs else ""
        print(f"    {sc:.4f}  {label}: {text[:60]}...{crib_str}")

    all_cribs = [(label, cribs) for sc, label, text, cribs in best_results if cribs]
    if all_cribs:
        print(f"\n  ** CRIB MATCHES FOUND: **")
        for label, cribs in all_cribs:
            print(f"    {label}: {cribs}")

    return best_results[:5]


# ============================================================================
# GRAND SUMMARY
# ============================================================================

def grand_summary(all_results):
    """Print overall best results across all tests."""
    print("\n" + "=" * 70)
    print("GRAND SUMMARY - TOP RESULTS ACROSS ALL TESTS")
    print("=" * 70)

    # Flatten
    flat = []
    for test_name, results in all_results:
        for sc, label, text, cribs in results:
            flat.append((sc, label, text, cribs, test_name))

    flat.sort(reverse=True)

    print(f"\n  Overall Top 30:")
    for sc, label, text, cribs, test_name in flat[:30]:
        crib_str = f"  ** CRIBS: {cribs} **" if cribs else ""
        print(f"    {sc:.4f}  [{test_name}] {label}")
        print(f"           {text[:70]}...{crib_str}")

    # Print all crib matches
    all_cribs = [(label, cribs, text, test_name) for sc, label, text, cribs, test_name in flat if cribs]
    if all_cribs:
        print(f"\n  *** ALL CRIB MATCHES ({len(all_cribs)} total): ***")
        for label, cribs, text, test_name in all_cribs:
            print(f"    [{test_name}] {label}")
            print(f"      Cribs: {cribs}")
            print(f"      Text:  {text[:80]}")
    else:
        print("\n  No crib matches found in any test.")

    # Statistics
    print(f"\n  Total configurations tested: {len(flat)}")
    if flat:
        print(f"  Best score:  {flat[0][0]:.4f}")
        print(f"  Worst score: {flat[-1][0]:.4f}")
        print(f"  Median score: {flat[len(flat)//2][0]:.4f}")

    # Score of raw K4 for reference
    raw_sc = flat[0][0]  # will be overridden
    for sc, label, text, cribs, test_name in flat:
        if text == K4:
            raw_sc = sc
            break

    print(f"\n  Reference: Raw K4 score = (check below)")
    return flat[:10]


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("K4 COMPASS ROSE / WELTZEITUHR TRANSPOSITION ANALYSIS")
    print("=" * 70)
    print(f"K4 ({K4_LEN} chars): {K4}")
    print(f"Period-29 key: {BEST_VIG_KEY}")
    print(f"Kryptos alphabet: {KRYPTOS_ALPHA}")

    # Load quadgram scorer
    qg_path = "/home/user/polyalphabetic/english_quadgrams.txt"
    if not os.path.exists(qg_path):
        print(f"ERROR: Quadgram file not found at {qg_path}")
        return

    scorer = QuadgramScorer(qg_path)
    raw_score = scorer.score_per_char(K4)
    print(f"\nRaw K4 quadgram score: {raw_score:.4f}")

    all_results = []

    # Test 1: Compass Rose Grid Reading
    r1 = test_compass_rose_grid(scorer)
    all_results.append(("Test1_CompassGrid", r1))

    # Test 2: Clock-Based Transposition
    r2 = test_clock_transposition(scorer)
    all_results.append(("Test2_Clock", r2))

    # Test 3: Compass Bearing Transposition
    r3 = test_compass_bearing(scorer)
    all_results.append(("Test3_Bearing", r3))

    # Test 4: Alexanderplatz Connection
    r4 = test_alexanderplatz_keywords(scorer)
    all_results.append(("Test4_Keywords", r4))

    # Test 5: Vigenere Then Transposition
    r5 = test_vigenere_then_transposition(scorer)
    all_results.append(("Test5_VigThenTransp", r5))

    # Test 6: Transposition Then Vigenere
    r6 = test_transposition_then_vigenere(scorer)
    all_results.append(("Test6_TranspThenVig", r6))

    # Test 7: Kryptos Compass Rose
    r7 = test_kryptos_compass_rose(scorer)
    all_results.append(("Test7_KryptosCompass", r7))

    # Bonus: Double Transposition
    r8 = test_double_transposition(scorer)
    all_results.append(("Bonus_DoubleTrans", r8))

    # Bonus 2: Scytale
    r9 = test_scytale(scorer)
    all_results.append(("Bonus_Scytale", r9))

    # Bonus 3: Transposition + Various Vigenere Keys
    r10 = test_transposition_various_vig_keys(scorer)
    all_results.append(("Bonus_TranspVigKeys", r10))

    # Grand Summary
    grand_summary(all_results)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
