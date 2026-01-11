#!/usr/bin/env python3
"""
Specific cipher implementations for K4 testing.
Focus on the 8 ciphers requested with thorough keyword combinations.
"""

import string
import itertools

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW"]


def create_polybius_square(keyword: str = "") -> tuple:
    """Create 5x5 Polybius square (I=J merged)"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # 25 chars, no J
    keyword = keyword.upper().replace("J", "I")

    seen = set()
    chars = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)

    c2c = {}
    c2ch = {}
    for i, c in enumerate(chars[:25]):
        r, col = i // 5, i % 5
        c2c[c] = (r, col)
        c2ch[(r, col)] = c

    return c2c, c2ch


def check_solution(plaintext: str, cipher_name: str, params: str) -> bool:
    """Check if plaintext matches cribs"""
    pt = plaintext.upper()

    berlin_at_63 = len(pt) > 73 and pt[63:74] == "BERLINCLOCK"
    northeast_found = "NORTHEAST" in pt

    if berlin_at_63 and northeast_found:
        print(f"\n{'*' * 70}")
        print(f"FULL MATCH: {cipher_name} | {params}")
        print(f"BERLINCLOCK at 63: YES | NORTHEAST: YES")
        print(f"Plaintext: {plaintext}")
        print(f"{'*' * 70}")
        return True

    if berlin_at_63 or northeast_found:
        ne_pos = pt.find("NORTHEAST") if northeast_found else -1
        print(f"\n  PARTIAL: {cipher_name} | {params}")
        print(f"  BERLINCLOCK@63: {berlin_at_63} | NORTHEAST: {northeast_found} (pos {ne_pos})")
        print(f"  {plaintext[:80]}...")

    # Check for any cribs
    for word in ["BERLIN", "CLOCK", "NORTH", "EAST", "UNDER", "ABOVE"]:
        if word in pt:
            pos = pt.find(word)
            if word == "BERLIN" and pos == 63:
                continue  # Already checked
            print(f"    Found {word} at {pos}")

    return False


# ============================================================
# 1. BIFID CIPHER
# ============================================================
def bifid_decrypt(ciphertext: str, keyword: str, period: int = 0) -> str:
    """
    Bifid cipher: Uses Polybius square to convert letters to coordinates,
    then rearranges rows and columns before converting back.
    """
    c2c, c2ch = create_polybius_square(keyword)
    ciphertext = ciphertext.upper().replace("J", "I")

    if period == 0 or period >= len(ciphertext):
        period = len(ciphertext)

    plaintext = []
    for start in range(0, len(ciphertext), period):
        block = ciphertext[start:start + period]

        rows = []
        cols = []
        for c in block:
            if c in c2c:
                r, col = c2c[c]
                rows.append(r)
                cols.append(col)

        # Combine rows then cols
        combined = rows + cols

        # Take pairs to form new coordinates
        for i in range(0, len(combined) - 1, 2):
            coords = (combined[i], combined[i + 1])
            if coords in c2ch:
                plaintext.append(c2ch[coords])

    return ''.join(plaintext)


# ============================================================
# 2. FOUR-SQUARE CIPHER
# ============================================================
def four_square_decrypt(ciphertext: str, keyword1: str, keyword2: str) -> str:
    """
    Four-square cipher: Uses 4 Polybius squares.
    Top-left and bottom-right are standard alphabet.
    Top-right uses keyword1, bottom-left uses keyword2.

    For decryption: ciphertext pairs come from keyed squares,
    plaintext pairs come from standard squares.
    """
    std_c2c, std_c2ch = create_polybius_square("")
    key1_c2c, key1_c2ch = create_polybius_square(keyword1)
    key2_c2c, key2_c2ch = create_polybius_square(keyword2)

    ciphertext = ciphertext.upper().replace("J", "I")
    if len(ciphertext) % 2 == 1:
        ciphertext += "X"

    plaintext = []
    for i in range(0, len(ciphertext), 2):
        c1, c2 = ciphertext[i], ciphertext[i + 1]

        if c1 not in key1_c2c or c2 not in key2_c2c:
            continue

        # c1 from top-right (keyword1), c2 from bottom-left (keyword2)
        r1, col1 = key1_c2c[c1]  # Position in keyed square 1
        r2, col2 = key2_c2c[c2]  # Position in keyed square 2

        # p1 from top-left standard: row from c1, col from c2
        # p2 from bottom-right standard: row from c2, col from c1
        p1 = std_c2ch.get((r1, col2), '?')
        p2 = std_c2ch.get((r2, col1), '?')

        plaintext.extend([p1, p2])

    return ''.join(plaintext)


# ============================================================
# 3. TWO-SQUARE CIPHER (Horizontal variant)
# ============================================================
def two_square_decrypt(ciphertext: str, keyword1: str, keyword2: str) -> str:
    """
    Two-square cipher (horizontal): Two keyed squares side by side.
    """
    key1_c2c, key1_c2ch = create_polybius_square(keyword1)
    key2_c2c, key2_c2ch = create_polybius_square(keyword2)

    ciphertext = ciphertext.upper().replace("J", "I")
    if len(ciphertext) % 2 == 1:
        ciphertext += "X"

    plaintext = []
    for i in range(0, len(ciphertext), 2):
        c1, c2 = ciphertext[i], ciphertext[i + 1]

        if c1 not in key1_c2c or c2 not in key2_c2c:
            continue

        r1, col1 = key1_c2c[c1]  # From left square
        r2, col2 = key2_c2c[c2]  # From right square

        if r1 == r2:
            # Same row - swap columns
            p1 = key1_c2ch.get((r1, col2), '?')
            p2 = key2_c2ch.get((r2, col1), '?')
        else:
            # Different rows - form rectangle
            p1 = key1_c2ch.get((r2, col1), '?')
            p2 = key2_c2ch.get((r1, col2), '?')

        plaintext.extend([p1, p2])

    return ''.join(plaintext)


# ============================================================
# 4. ADFGVX CIPHER
# ============================================================
def adfgvx_decrypt(ciphertext: str, polybius_key: str, trans_key: str) -> str:
    """
    ADFGVX cipher: Fractionation + columnar transposition.
    First reverses transposition, then converts ADFGVX pairs back to letters.

    Note: K4 contains letters beyond ADFGVX, so this may not apply directly.
    We try interpreting it as already-fractionated text.
    """
    # Create 6x6 Polybius square (A-Z + 0-9)
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    key_clean = polybius_key.upper()

    seen = set()
    square = []
    for c in key_clean + alphabet:
        if c in alphabet and c not in seen:
            square.append(c)
            seen.add(c)

    adfgvx = "ADFGVX"
    coords_to_char = {}
    for i, c in enumerate(square[:36]):
        r, col = i // 6, i % 6
        coords_to_char[(adfgvx[r], adfgvx[col])] = c

    # For K4, we can't directly apply ADFGVX since it's not limited to ADFGVX letters
    # Try treating letters as encoded positions

    trans_key = trans_key.upper()
    key_len = len(trans_key)

    # Sort key to get column order (alphabetical)
    sorted_cols = sorted(range(key_len), key=lambda x: trans_key[x])

    n = len(ciphertext)
    full_rows = n // key_len
    extra = n % key_len

    # Calculate column lengths
    col_lengths = []
    for i, col_idx in enumerate(sorted_cols):
        if col_idx < extra:
            col_lengths.append(full_rows + 1)
        else:
            col_lengths.append(full_rows)

    # Split ciphertext into columns
    columns = {}
    pos = 0
    for i, col_idx in enumerate(sorted_cols):
        length = col_lengths[i]
        columns[col_idx] = list(ciphertext[pos:pos + length])
        pos += length

    # Read off rows
    fractionated = []
    for row in range(full_rows + (1 if extra > 0 else 0)):
        for col in range(key_len):
            if row < len(columns.get(col, [])):
                fractionated.append(columns[col][row])

    # Try to interpret as ADFGVX pairs
    frac_str = ''.join(fractionated).upper()

    # Map each letter to ADFGVX based on position mod 6
    adfgvx_mapped = []
    for c in frac_str:
        if c.isalpha():
            idx = (ord(c) - ord('A')) % 6
            adfgvx_mapped.append(adfgvx[idx])

    # Convert pairs back
    plaintext = []
    for i in range(0, len(adfgvx_mapped) - 1, 2):
        pair = (adfgvx_mapped[i], adfgvx_mapped[i + 1])
        if pair in coords_to_char:
            char = coords_to_char[pair]
            if char.isalpha():
                plaintext.append(char)

    return ''.join(plaintext)


# ============================================================
# 5. STRADDLING CHECKERBOARD
# ============================================================
def straddling_checkerboard_decrypt(ciphertext: str, keyword: str) -> str:
    """
    Straddling checkerboard: Converts letters to variable-length numbers.
    Top row has gaps, remaining letters fill rows below.
    """
    # Create keyed alphabet
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper()

    seen = set()
    keyed = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            keyed.append(c)
            seen.add(c)

    # Standard checkerboard layout:
    # Row 0 (header): positions 0,1,3,5,6,8 have letters, 2,4,7,9 are row indicators
    # Rows 2,4,7: fill remaining letters (10 per row)

    # Place first 6 letters in single-digit positions
    single_positions = [0, 1, 3, 5, 6, 8]
    row_indicators = [2, 4, 7]

    code_to_char = {}
    pos = 0

    for p in single_positions:
        if pos < len(keyed):
            code_to_char[str(p)] = keyed[pos]
            pos += 1

    # Fill remaining letters in rows 2, 4, 7
    for ri in row_indicators:
        for col in range(10):
            if pos < len(keyed):
                code_to_char[f"{ri}{col}"] = keyed[pos]
                pos += 1

    # Convert ciphertext letters to digits (A=0, B=1, ... Z=25 mod 10)
    digits = ""
    for c in ciphertext.upper():
        if c.isalpha():
            digits += str((ord(c) - ord('A')) % 10)

    # Decode digit stream
    plaintext = []
    i = 0
    while i < len(digits):
        d = digits[i]
        if d in code_to_char:
            plaintext.append(code_to_char[d])
            i += 1
        elif i + 1 < len(digits):
            pair = digits[i:i+2]
            if pair in code_to_char:
                plaintext.append(code_to_char[pair])
            i += 2
        else:
            i += 1

    return ''.join(plaintext)


# ============================================================
# 6. NIHILIST CIPHER
# ============================================================
def nihilist_decrypt(ciphertext: str, polybius_key: str, cipher_key: str) -> str:
    """
    Nihilist cipher: Uses Polybius square to convert letters to 2-digit numbers,
    then subtracts key numbers (also from Polybius square).
    """
    c2c, c2ch = create_polybius_square(polybius_key)

    # Convert cipher key to number sequence (each letter -> 2-digit number)
    key_nums = []
    for c in cipher_key.upper().replace("J", "I"):
        if c in c2c:
            r, col = c2c[c]
            key_nums.append((r + 1) * 10 + (col + 1))  # 11-55 range

    if not key_nums:
        return ""

    ciphertext = ciphertext.upper().replace("J", "I")
    plaintext = []

    for i, c in enumerate(ciphertext):
        if c in c2c:
            r, col = c2c[c]
            ct_num = (r + 1) * 10 + (col + 1)
            key_num = key_nums[i % len(key_nums)]

            # For Nihilist, typically CT = PT + Key
            # So PT = CT - Key
            pt_num = ct_num - key_num + 11  # Adjust to keep in valid range

            # Modular approach
            diff = ct_num - key_num
            pr = ((diff // 10) + 5) % 5  # Row in range 0-4
            pc = ((diff % 10) + 5) % 5   # Col in range 0-4

            if (pr, pc) in c2ch:
                plaintext.append(c2ch[(pr, pc)])

    return ''.join(plaintext)


# ============================================================
# 7. GRONSFELD CIPHER
# ============================================================
def gronsfeld_decrypt(ciphertext: str, num_key: str) -> str:
    """
    Gronsfeld cipher: Like Vigenere but with digits (0-9) as key.
    """
    digits = []
    for c in num_key:
        if c.isdigit():
            digits.append(int(c))
        elif c.isalpha():
            # Convert letters to digits
            digits.append((ord(c.upper()) - ord('A')) % 10)

    if not digits:
        return ""

    plaintext = []
    key_pos = 0

    for c in ciphertext.upper():
        if c.isalpha():
            shift = digits[key_pos % len(digits)]
            p = (ord(c) - ord('A') - shift) % 26
            plaintext.append(chr(p + ord('A')))
            key_pos += 1
        else:
            plaintext.append(c)

    return ''.join(plaintext)


# ============================================================
# 8. TRITHEMIUS CIPHER
# ============================================================
def trithemius_decrypt(ciphertext: str, start: int = 0) -> str:
    """
    Trithemius cipher: Each position shifted by its index (progressive).
    """
    plaintext = []

    for i, c in enumerate(ciphertext.upper()):
        if c.isalpha():
            shift = (start + i) % 26
            p = (ord(c) - ord('A') - shift) % 26
            plaintext.append(chr(p + ord('A')))

    return ''.join(plaintext)


def test_all_ciphers():
    """Test all 8 cipher types with keyword combinations"""

    print("=" * 70)
    print("COMPREHENSIVE CLASSICAL CIPHER TESTING ON K4")
    print("=" * 70)
    print(f"K4: {K4}")
    print(f"Length: {len(K4)}")
    print(f"Looking for BERLINCLOCK at position 63 and NORTHEAST anywhere")
    print()

    all_matches = []

    # 1. BIFID
    print("\n[1] BIFID CIPHER")
    print("-" * 50)
    for keyword in KEYWORDS:
        for period in range(3, 50):
            try:
                plain = bifid_decrypt(K4, keyword, period)
                if check_solution(plain, "BIFID", f"key={keyword}, period={period}"):
                    all_matches.append(("BIFID", keyword, period, plain))
            except:
                pass

    # 2. FOUR-SQUARE
    print("\n[2] FOUR-SQUARE CIPHER")
    print("-" * 50)
    for kw1 in KEYWORDS:
        for kw2 in KEYWORDS:
            try:
                plain = four_square_decrypt(K4, kw1, kw2)
                if check_solution(plain, "FOUR-SQUARE", f"kw1={kw1}, kw2={kw2}"):
                    all_matches.append(("FOUR-SQUARE", f"{kw1}/{kw2}", 0, plain))
            except:
                pass

    # 3. TWO-SQUARE
    print("\n[3] TWO-SQUARE CIPHER")
    print("-" * 50)
    for kw1 in KEYWORDS:
        for kw2 in KEYWORDS:
            try:
                plain = two_square_decrypt(K4, kw1, kw2)
                if check_solution(plain, "TWO-SQUARE", f"kw1={kw1}, kw2={kw2}"):
                    all_matches.append(("TWO-SQUARE", f"{kw1}/{kw2}", 0, plain))
            except:
                pass

    # 4. ADFGVX
    print("\n[4] ADFGVX CIPHER")
    print("-" * 50)
    print("Note: K4 doesn't use ADFGVX letters only, trying interpretations...")
    for poly_key in KEYWORDS:
        for trans_key in KEYWORDS:
            try:
                plain = adfgvx_decrypt(K4, poly_key, trans_key)
                if len(plain) > 30:
                    if check_solution(plain, "ADFGVX", f"poly={poly_key}, trans={trans_key}"):
                        all_matches.append(("ADFGVX", f"{poly_key}/{trans_key}", 0, plain))
            except:
                pass

    # 5. STRADDLING CHECKERBOARD
    print("\n[5] STRADDLING CHECKERBOARD")
    print("-" * 50)
    for keyword in KEYWORDS:
        try:
            plain = straddling_checkerboard_decrypt(K4, keyword)
            if len(plain) > 30:
                if check_solution(plain, "STRADDLING", f"key={keyword}"):
                    all_matches.append(("STRADDLING", keyword, 0, plain))
        except:
            pass

    # 6. NIHILIST
    print("\n[6] NIHILIST CIPHER")
    print("-" * 50)
    for poly_key in KEYWORDS:
        for cipher_key in KEYWORDS:
            try:
                plain = nihilist_decrypt(K4, poly_key, cipher_key)
                if len(plain) > 50:
                    if check_solution(plain, "NIHILIST", f"poly={poly_key}, cipher={cipher_key}"):
                        all_matches.append(("NIHILIST", f"{poly_key}/{cipher_key}", 0, plain))
            except:
                pass

    # 7. GRONSFELD
    print("\n[7] GRONSFELD CIPHER")
    print("-" * 50)
    # Test with keywords converted to digits
    for keyword in KEYWORDS:
        try:
            plain = gronsfeld_decrypt(K4, keyword)
            if check_solution(plain, "GRONSFELD", f"key={keyword}"):
                all_matches.append(("GRONSFELD", keyword, 0, plain))
        except:
            pass

    # Test with numeric patterns
    num_keys = ["31415926", "27182818", "1920", "1990", "123456789", "987654321"]
    for num_key in num_keys:
        try:
            plain = gronsfeld_decrypt(K4, num_key)
            if check_solution(plain, "GRONSFELD", f"key={num_key}"):
                all_matches.append(("GRONSFELD", num_key, 0, plain))
        except:
            pass

    # 8. TRITHEMIUS
    print("\n[8] TRITHEMIUS CIPHER")
    print("-" * 50)
    for start in range(26):
        try:
            plain = trithemius_decrypt(K4, start)
            if check_solution(plain, "TRITHEMIUS", f"start={start}"):
                all_matches.append(("TRITHEMIUS", str(start), 0, plain))
        except:
            pass

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    if all_matches:
        print(f"\nFound {len(all_matches)} matches:")
        for cipher, key, period, plain in all_matches:
            print(f"\n{cipher}: {key}" + (f", period={period}" if period else ""))
            print(f"  {plain}")
    else:
        print("\nNo matches found for BERLINCLOCK@63 AND NORTHEAST")
        print("Check partial matches above for potential leads.")


if __name__ == "__main__":
    test_all_ciphers()
