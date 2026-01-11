#!/usr/bin/env python3
"""
Advanced classical cipher analysis on K4 with flexible crib checking
"""

import itertools
import string

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW",
            "NORTHEAST", "BERLINCLOCK", "SANBORN", "SCHEIDT"]

def create_polybius_square(keyword: str) -> tuple:
    """Create 5x5 Polybius square"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper().replace("J", "I")

    seen = set()
    chars = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)

    c2c = {}
    c2ch = {}
    for i, c in enumerate(chars):
        r, col = i // 5, i % 5
        c2c[c] = (r, col)
        c2ch[(r, col)] = c

    return c2c, c2ch


def nihilist_substitution_decrypt(ct: str, poly_key: str, cipher_key: str) -> str:
    """
    Nihilist substitution: each letter becomes 2-digit number via Polybius,
    then key is subtracted (each key letter also becomes 2-digit number)
    """
    c2c, c2ch = create_polybius_square(poly_key)

    # Convert cipher key to number sequence
    key_nums = []
    for c in cipher_key.upper().replace("J", "I"):
        if c in c2c:
            r, col = c2c[c]
            key_nums.append((r + 1) * 10 + (col + 1))

    if not key_nums:
        return ""

    ct = ct.upper().replace("J", "I")
    plaintext = []

    for i, c in enumerate(ct):
        if c in c2c:
            r, col = c2c[c]
            ct_num = (r + 1) * 10 + (col + 1)
            key_num = key_nums[i % len(key_nums)]

            # Subtract key
            pt_num = ct_num - key_num

            # Convert back
            pr, pc = (pt_num // 10) - 1, (pt_num % 10) - 1
            if 0 <= pr < 5 and 0 <= pc < 5 and (pr, pc) in c2ch:
                plaintext.append(c2ch[(pr, pc)])
            else:
                # Try modular arithmetic
                pt_num = ((ct_num - 11) - (key_num - 11)) % 55 + 11
                pr, pc = (pt_num // 10) - 1, (pt_num % 10) - 1
                if 0 <= pr < 5 and 0 <= pc < 5 and (pr, pc) in c2ch:
                    plaintext.append(c2ch[(pr, pc)])

    return ''.join(plaintext)


def seriated_playfair_decrypt(ct: str, keyword: str, period: int) -> str:
    """Seriated (periodic) Playfair"""
    c2c, c2ch = create_polybius_square(keyword)
    ct = ct.upper().replace("J", "I")

    # Process in periods
    result = []

    for start in range(0, len(ct), period):
        block = ct[start:start + period]
        if len(block) % 2 == 1:
            block += "X"

        for i in range(0, len(block), 2):
            c1, c2 = block[i], block[i + 1]

            if c1 not in c2c or c2 not in c2c:
                continue

            r1, col1 = c2c[c1]
            r2, col2 = c2c[c2]

            if r1 == r2:
                p1 = c2ch[(r1, (col1 - 1) % 5)]
                p2 = c2ch[(r2, (col2 - 1) % 5)]
            elif col1 == col2:
                p1 = c2ch[((r1 - 1) % 5, col1)]
                p2 = c2ch[((r2 - 1) % 5, col2)]
            else:
                p1 = c2ch[(r1, col2)]
                p2 = c2ch[(r2, col1)]

            result.extend([p1, p2])

    return ''.join(result)


def phillips_decrypt(ct: str, keyword: str) -> str:
    """Phillips cipher (similar to Playfair but 8x8)"""
    # Create 8x8 grid
    chars = []
    seen = set()
    for c in keyword.upper():
        if c.isalnum() and c not in seen:
            chars.append(c)
            seen.add(c)

    for c in string.ascii_uppercase + string.digits:
        if c not in seen:
            chars.append(c)
            seen.add(c)

    # Pad to 64
    while len(chars) < 64:
        chars.append(' ')

    c2c = {}
    c2ch = {}
    for i, c in enumerate(chars[:64]):
        r, col = i // 8, i % 8
        c2c[c] = (r, col)
        c2ch[(r, col)] = c

    ct = ct.upper()
    result = []

    for i in range(0, len(ct) - 1, 2):
        c1, c2 = ct[i], ct[i + 1]

        if c1 not in c2c or c2 not in c2c:
            continue

        r1, col1 = c2c[c1]
        r2, col2 = c2c[c2]

        if r1 == r2:
            p1 = c2ch[(r1, (col1 - 1) % 8)]
            p2 = c2ch[(r2, (col2 - 1) % 8)]
        elif col1 == col2:
            p1 = c2ch[((r1 - 1) % 8, col1)]
            p2 = c2ch[((r2 - 1) % 8, col2)]
        else:
            p1 = c2ch[(r1, col2)]
            p2 = c2ch[(r2, col1)]

        result.extend([p1, p2])

    return ''.join(result)


def gronsfeld_decrypt(ct: str, num_key: list) -> str:
    """Gronsfeld with numeric key"""
    result = []
    for i, c in enumerate(ct.upper()):
        if c.isalpha():
            shift = num_key[i % len(num_key)]
            p = (ord(c) - ord('A') - shift) % 26
            result.append(chr(p + ord('A')))
    return ''.join(result)


def find_all_occurrences(text: str, pattern: str) -> list:
    """Find all occurrences of pattern in text"""
    positions = []
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos < 0:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def analyze_result(cipher: str, key_info: str, plaintext: str):
    """Analyze decryption result for interesting patterns"""
    pt = plaintext.upper()

    matches = {}

    # Check for key strings
    for pattern in ["BERLINCLOCK", "BERLIN", "CLOCK", "NORTHEAST", "NORTH", "EAST",
                    "UNDER", "ABOVE", "GROUND", "SHADOW", "VISIBLE", "INVISIBLE"]:
        positions = find_all_occurrences(pt, pattern)
        if positions:
            matches[pattern] = positions

    # Check BERLINCLOCK at position 63 specifically
    if len(pt) > 73 and pt[63:74] == "BERLINCLOCK":
        matches["BERLINCLOCK@63"] = [63]

    if matches:
        print(f"\n{'*' * 60}")
        print(f"MATCH FOUND: {cipher} | {key_info}")
        print(f"Plaintext: {plaintext[:100]}...")
        print(f"Matches: {matches}")
        return True

    return False


def vigenere_decrypt(ct: str, key: str) -> str:
    key = key.upper()
    result = []
    for i, c in enumerate(ct.upper()):
        if c.isalpha():
            k = ord(key[i % len(key)]) - ord('A')
            p = (ord(c) - ord('A') - k) % 26
            result.append(chr(p + ord('A')))
    return ''.join(result)


def test_running_key_variants():
    """Try running key cipher with known text"""
    print("\n[RUNNING KEY CIPHER VARIANTS]")
    print("-" * 40)

    # Known K1, K2, K3 plaintexts as potential running keys
    running_keys = [
        "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION",
        "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELD",
        "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBABORABLOODANDTHEBODYNEWANDSTRONGANDREAYTOTHEREAREDIFFERENTFROMTHEPASTBUTALMOSTHESAME",
        "ENDYAHROHEWLDTHENEARINBETHEEASTSENORTHEASTANDSOFORTHFAKEANNOTHERPERIODSYSTEM",
        # Try reversed
        "NOISULIQFOSECNAUNEHTSEILTHGILFOSECNESBAEHTDNAGNIDAHSELBTUSNEWTEB",
    ]

    for running_key in running_keys:
        running_key = ''.join(c for c in running_key.upper() if c.isalpha())
        if len(running_key) >= len(K4):
            plain = vigenere_decrypt(K4, running_key[:len(K4)])
            analyze_result("RUNNING-KEY", f"key_len={len(running_key)}", plain)


def test_nihilist_variations():
    """Test various Nihilist cipher variations"""
    print("\n[NIHILIST CIPHER VARIATIONS]")
    print("-" * 40)

    for poly_key in KEYWORDS:
        for cipher_key in KEYWORDS:
            try:
                plain = nihilist_substitution_decrypt(K4, poly_key, cipher_key)
                if len(plain) > 50:
                    analyze_result("NIHILIST", f"poly={poly_key}, cipher={cipher_key}", plain)
            except:
                pass


def test_gronsfeld_variations():
    """Test Gronsfeld with various numeric keys"""
    print("\n[GRONSFELD CIPHER VARIATIONS]")
    print("-" * 40)

    # Try various numeric patterns
    test_keys = [
        [1, 9, 2, 0],  # 1920 (construction year)
        [1, 9, 9, 0],  # 1990 (sculpture year)
        [3, 1, 4, 1, 5, 9],  # pi
        [2, 7, 1, 8, 2, 8],  # e
        [1, 1, 2, 3, 5, 8],  # fibonacci
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
    ]

    # Generate keys from keyword letter positions
    for keyword in KEYWORDS:
        key = [(ord(c) - ord('A')) % 10 for c in keyword.upper() if c.isalpha()]
        test_keys.append(key)

    for key in test_keys:
        if key:
            plain = gronsfeld_decrypt(K4, key)
            analyze_result("GRONSFELD", f"key={key}", plain)


def test_seriated_playfair():
    """Test seriated Playfair with various periods"""
    print("\n[SERIATED PLAYFAIR]")
    print("-" * 40)

    for keyword in KEYWORDS:
        for period in range(4, 20, 2):
            plain = seriated_playfair_decrypt(K4, keyword, period)
            analyze_result("SERIATED-PLAYFAIR", f"key={keyword}, period={period}", plain)


def test_bifid_column_variations():
    """Test Bifid with different column reading patterns"""
    print("\n[BIFID VARIATIONS]")
    print("-" * 40)

    def bifid_variant(ct: str, keyword: str, period: int, reverse_combine: bool = False) -> str:
        c2c, c2ch = create_polybius_square(keyword)
        ct = ct.upper().replace("J", "I")

        if period == 0:
            period = len(ct)

        result = []
        for start in range(0, len(ct), period):
            block = ct[start:start + period]

            rows = []
            cols = []
            for c in block:
                if c in c2c:
                    r, col = c2c[c]
                    rows.append(r)
                    cols.append(col)

            if reverse_combine:
                combined = cols + rows  # Reversed
            else:
                combined = rows + cols

            for i in range(0, len(combined) - 1, 2):
                coords = (combined[i], combined[i + 1])
                if coords in c2ch:
                    result.append(c2ch[coords])

        return ''.join(result)

    for keyword in KEYWORDS:
        for period in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 29]:
            # Standard
            plain = bifid_variant(K4, keyword, period, False)
            analyze_result("BIFID-STD", f"key={keyword}, period={period}", plain)

            # Reversed row/col
            plain = bifid_variant(K4, keyword, period, True)
            analyze_result("BIFID-REV", f"key={keyword}, period={period}", plain)


def test_double_columnar():
    """Test double columnar transposition followed by substitution"""
    print("\n[DOUBLE COLUMNAR + SUBSTITUTION]")
    print("-" * 40)

    def columnar_decrypt(ct: str, key: str) -> str:
        n = len(ct)
        key_len = len(key)
        num_rows = (n + key_len - 1) // key_len

        # Sort key to get column order
        sorted_indices = sorted(range(key_len), key=lambda x: key[x])

        # Calculate column lengths
        full_cols = n % key_len if n % key_len != 0 else key_len

        columns = {}
        pos = 0
        for i, col_idx in enumerate(sorted_indices):
            col_len = num_rows if col_idx < full_cols else num_rows - 1
            columns[col_idx] = list(ct[pos:pos + col_len])
            pos += col_len

        # Read off rows
        result = []
        for row in range(num_rows):
            for col in range(key_len):
                if row < len(columns.get(col, [])):
                    result.append(columns[col][row])

        return ''.join(result)

    for trans_key in KEYWORDS[:4]:
        transposed = columnar_decrypt(K4, trans_key)
        for sub_key in KEYWORDS:
            plain = vigenere_decrypt(transposed, sub_key)
            analyze_result("COL-TRANS+VIG", f"trans={trans_key}, vig={sub_key}", plain)


def test_affine_variants():
    """Test affine cipher variants"""
    print("\n[AFFINE CIPHER VARIANTS]")
    print("-" * 40)

    def affine_decrypt(ct: str, a: int, b: int) -> str:
        # Find modular inverse of a
        a_inv = None
        for i in range(26):
            if (a * i) % 26 == 1:
                a_inv = i
                break

        if a_inv is None:
            return ""

        result = []
        for c in ct.upper():
            if c.isalpha():
                y = ord(c) - ord('A')
                x = (a_inv * (y - b)) % 26
                result.append(chr(x + ord('A')))

        return ''.join(result)

    # Valid 'a' values (coprime with 26)
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

    for a in valid_a:
        for b in range(26):
            plain = affine_decrypt(K4, a, b)
            analyze_result("AFFINE", f"a={a}, b={b}", plain)


def main():
    print("=" * 70)
    print("ADVANCED CLASSICAL CIPHER ANALYSIS ON K4")
    print("=" * 70)
    print(f"K4: {K4}")
    print(f"Length: {len(K4)}")
    print(f"Looking for BERLINCLOCK at position 63 and NORTHEAST anywhere")
    print()

    test_running_key_variants()
    test_nihilist_variations()
    test_gronsfeld_variations()
    test_seriated_playfair()
    test_bifid_column_variations()
    test_double_columnar()
    test_affine_variants()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
