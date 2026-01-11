#!/usr/bin/env python3
"""
Test various classical cipher approaches on K4
"""

import itertools
from typing import List, Tuple, Optional
import string

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "NORTHEAST", "BERLINCLOCK"]

def create_polybius_square(keyword: str, size: int = 5) -> Tuple[dict, dict]:
    """Create a Polybius square from a keyword (5x5, I=J)"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # No J
    keyword = keyword.upper().replace("J", "I")

    # Remove duplicates while preserving order
    seen = set()
    key_chars = []
    for c in keyword:
        if c in alphabet and c not in seen:
            key_chars.append(c)
            seen.add(c)

    # Add remaining alphabet
    for c in alphabet:
        if c not in seen:
            key_chars.append(c)
            seen.add(c)

    # Create mappings
    char_to_coords = {}
    coords_to_char = {}
    for i, c in enumerate(key_chars):
        row, col = i // 5, i % 5
        char_to_coords[c] = (row, col)
        coords_to_char[(row, col)] = c

    return char_to_coords, coords_to_char


def bifid_decrypt(ciphertext: str, keyword: str, period: int = 0) -> str:
    """Decrypt using Bifid cipher"""
    ciphertext = ciphertext.upper().replace("J", "I")
    char_to_coords, coords_to_char = create_polybius_square(keyword)

    if period == 0:
        period = len(ciphertext)

    plaintext = []
    for start in range(0, len(ciphertext), period):
        block = ciphertext[start:start + period]

        # Get all coordinates
        rows = []
        cols = []
        for c in block:
            if c in char_to_coords:
                r, col = char_to_coords[c]
                rows.append(r)
                cols.append(col)

        # Combine rows then cols
        combined = rows + cols

        # Take pairs to get plaintext
        for i in range(0, len(combined) - 1, 2):
            coords = (combined[i], combined[i + 1])
            if coords in coords_to_char:
                plaintext.append(coords_to_char[coords])

    return ''.join(plaintext)


def four_square_decrypt(ciphertext: str, keyword1: str, keyword2: str) -> str:
    """Decrypt using Four-square cipher"""
    # Standard square (top-left and bottom-right)
    std_c2c, std_c2ch = create_polybius_square("")
    # Keyed squares (top-right and bottom-left)
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

        # Get positions in keyed squares
        r1, col1 = key1_c2c[c1]  # Top-right square
        r2, col2 = key2_c2c[c2]  # Bottom-left square

        # Plain chars from standard squares
        p1 = std_c2ch.get((r1, col2), '?')  # Top-left
        p2 = std_c2ch.get((r2, col1), '?')  # Bottom-right

        plaintext.extend([p1, p2])

    return ''.join(plaintext)


def two_square_decrypt_horizontal(ciphertext: str, keyword1: str, keyword2: str) -> str:
    """Decrypt using Two-square cipher (horizontal variant)"""
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

        r1, col1 = key1_c2c[c1]
        r2, col2 = key2_c2c[c2]

        if r1 == r2:
            # Same row - swap columns
            p1 = key1_c2ch.get((r1, col2), '?')
            p2 = key2_c2ch.get((r2, col1), '?')
        else:
            # Different rows - rectangle
            p1 = key1_c2ch.get((r2, col1), '?')
            p2 = key2_c2ch.get((r1, col2), '?')

        plaintext.extend([p1, p2])

    return ''.join(plaintext)


def adfgvx_decrypt(ciphertext: str, polybius_key: str, trans_key: str) -> str:
    """Decrypt using ADFGVX cipher"""
    # Create 6x6 Polybius square with ADFGVX
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
    char_to_coords = {}
    for i, c in enumerate(square[:36]):
        r, col = i // 6, i % 6
        coords_to_char[(adfgvx[r], adfgvx[col])] = c
        char_to_coords[c] = (adfgvx[r], adfgvx[col])

    # First, reverse the columnar transposition
    trans_key = trans_key.upper()
    key_len = len(trans_key)

    # Get column order
    sorted_cols = sorted(range(key_len), key=lambda x: trans_key[x])

    # Calculate column lengths
    full_rows = len(ciphertext) // key_len
    extra = len(ciphertext) % key_len

    # Split ciphertext into columns
    col_lengths = [full_rows + (1 if i < extra else 0) for i in sorted_cols]

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

    # Convert ADFGVX pairs back to plaintext
    plaintext = []
    frac_str = ''.join(fractionated).upper()
    for i in range(0, len(frac_str) - 1, 2):
        pair = (frac_str[i], frac_str[i + 1])
        if pair in coords_to_char:
            plaintext.append(coords_to_char[pair])

    return ''.join(plaintext)


def straddling_checkerboard_decrypt(ciphertext: str, keyword: str) -> str:
    """Decrypt using straddling checkerboard"""
    # Standard setup with blanks at positions for high-frequency letters
    # Row 0: _ T _ A _ _ _ O _ N
    # This is a simplified version

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key_clean = keyword.upper()

    seen = set()
    key_chars = []
    for c in key_clean + alphabet:
        if c in alphabet and c not in seen:
            key_chars.append(c)
            seen.add(c)

    # Create checkerboard (3 rows, 10 columns)
    # First row has gaps, remaining letters fill in
    high_freq = "ESTONIAR"  # Common letters for top row

    board = {}
    digit_to_char = {}

    # Place high-frequency letters in single-digit positions
    single_positions = [0, 1, 3, 5, 6, 8]  # Leaving 2, 4, 7, 9 as row indicators
    row_indicators = [2, 4, 7]

    pos = 0
    for i, p in enumerate(single_positions):
        if pos < len(key_chars):
            digit_to_char[str(p)] = key_chars[pos]
            pos += 1

    # Fill remaining letters in rows 2, 4, 7
    for ri, row in enumerate(row_indicators):
        for col in range(10):
            if pos < len(key_chars):
                digit_to_char[f"{row}{col}"] = key_chars[pos]
                pos += 1

    # Decrypt
    plaintext = []
    i = 0
    ciphertext = ciphertext.upper()

    # Convert letters to digits (A=0, B=1, etc.)
    digits = ""
    for c in ciphertext:
        if c.isalpha():
            digits += str(ord(c) - ord('A'))
        elif c.isdigit():
            digits += c

    i = 0
    while i < len(digits):
        d = digits[i]
        if d in digit_to_char:
            plaintext.append(digit_to_char[d])
            i += 1
        elif i + 1 < len(digits):
            pair = digits[i:i+2]
            if pair in digit_to_char:
                plaintext.append(digit_to_char[pair])
            i += 2
        else:
            i += 1

    return ''.join(plaintext)


def nihilist_decrypt(ciphertext: str, keyword: str, num_key: str) -> str:
    """Decrypt using Nihilist cipher (numbers expected)"""
    # Nihilist typically uses number pairs
    # This version tries to interpret letter pairs as numbers
    char_to_coords, coords_to_char = create_polybius_square(keyword)

    # Convert keyword to number sequence
    num_seq = []
    for c in num_key.upper():
        if c in char_to_coords:
            r, col = char_to_coords[c]
            num_seq.append((r + 1) * 10 + (col + 1))

    if not num_seq:
        return ""

    ciphertext = ciphertext.upper().replace("J", "I")
    plaintext = []

    # Try interpreting consecutive letter pairs
    for i, c in enumerate(ciphertext):
        if c in char_to_coords:
            r, col = char_to_coords[c]
            cipher_num = (r + 1) * 10 + (col + 1)
            key_num = num_seq[i % len(num_seq)]
            plain_num = cipher_num - key_num

            pr, pc = (plain_num // 10) - 1, (plain_num % 10) - 1
            if 0 <= pr < 5 and 0 <= pc < 5:
                if (pr, pc) in coords_to_char:
                    plaintext.append(coords_to_char[(pr, pc)])

    return ''.join(plaintext)


def gronsfeld_decrypt(ciphertext: str, num_key: str) -> str:
    """Decrypt using Gronsfeld cipher (Vigenere with digits)"""
    # Extract digits from key
    digits = [int(d) for d in num_key if d.isdigit()]
    if not digits:
        # Convert letters to digit sum
        for c in num_key.upper():
            if c.isalpha():
                digits.append((ord(c) - ord('A')) % 10)

    if not digits:
        return ""

    plaintext = []
    key_pos = 0

    for c in ciphertext.upper():
        if c.isalpha():
            shift = digits[key_pos % len(digits)]
            plain = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            plaintext.append(plain)
            key_pos += 1
        else:
            plaintext.append(c)

    return ''.join(plaintext)


def trithemius_decrypt(ciphertext: str, start: int = 0) -> str:
    """Decrypt using Trithemius cipher (progressive shift)"""
    plaintext = []

    for i, c in enumerate(ciphertext.upper()):
        if c.isalpha():
            shift = (start + i) % 26
            plain = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            plaintext.append(plain)

    return ''.join(plaintext)


def check_cribs(plaintext: str) -> Tuple[bool, bool, int, int]:
    """Check for BERLINCLOCK at pos 63 and NORTHEAST anywhere"""
    plaintext = plaintext.upper()

    berlin_at_63 = False
    northeast_pos = -1

    if len(plaintext) > 73:
        if plaintext[63:74] == "BERLINCLOCK":
            berlin_at_63 = True

    ne_pos = plaintext.find("NORTHEAST")
    if ne_pos >= 0:
        northeast_pos = ne_pos

    return berlin_at_63, northeast_pos >= 0, 63 if berlin_at_63 else -1, northeast_pos


def test_all_ciphers():
    """Test all cipher types with all keywords"""

    results = []

    print("=" * 80)
    print("Testing Classical Ciphers on K4")
    print("=" * 80)
    print(f"K4: {K4}")
    print(f"Length: {len(K4)}")
    print()

    # 1. BIFID CIPHER
    print("\n" + "=" * 40)
    print("1. BIFID CIPHER")
    print("=" * 40)

    for keyword in KEYWORDS:
        # Test various periods
        for period in [0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19, 29, 97]:
            try:
                plain = bifid_decrypt(K4, keyword, period)
                berlin, ne, bpos, npos = check_cribs(plain)

                if berlin or ne:
                    print(f"\n*** MATCH: keyword={keyword}, period={period}")
                    print(f"    Plaintext: {plain[:80]}...")
                    print(f"    BERLINCLOCK@63: {berlin}, NORTHEAST: {ne} (pos {npos})")
                    results.append(("BIFID", keyword, period, plain, berlin, ne))

                # Also check for partial matches
                if "BERLIN" in plain or "CLOCK" in plain or "NORTH" in plain or "EAST" in plain:
                    print(f"  Partial: {keyword}, period={period}: ...{plain[55:85]}...")
            except Exception as e:
                pass

    # 2. FOUR-SQUARE CIPHER
    print("\n" + "=" * 40)
    print("2. FOUR-SQUARE CIPHER")
    print("=" * 40)

    for kw1 in KEYWORDS:
        for kw2 in KEYWORDS:
            try:
                plain = four_square_decrypt(K4, kw1, kw2)
                berlin, ne, bpos, npos = check_cribs(plain)

                if berlin or ne:
                    print(f"\n*** MATCH: kw1={kw1}, kw2={kw2}")
                    print(f"    Plaintext: {plain}")
                    print(f"    BERLINCLOCK@63: {berlin}, NORTHEAST: {ne}")
                    results.append(("FOUR-SQUARE", f"{kw1}/{kw2}", 0, plain, berlin, ne))

                if "BERLIN" in plain or "CLOCK" in plain or "NORTH" in plain:
                    print(f"  Partial: {kw1}/{kw2}: {plain[55:85]}...")
            except Exception as e:
                pass

    # 3. TWO-SQUARE CIPHER
    print("\n" + "=" * 40)
    print("3. TWO-SQUARE CIPHER")
    print("=" * 40)

    for kw1 in KEYWORDS:
        for kw2 in KEYWORDS:
            try:
                plain = two_square_decrypt_horizontal(K4, kw1, kw2)
                berlin, ne, bpos, npos = check_cribs(plain)

                if berlin or ne:
                    print(f"\n*** MATCH: kw1={kw1}, kw2={kw2}")
                    print(f"    Plaintext: {plain}")
                    print(f"    BERLINCLOCK@63: {berlin}, NORTHEAST: {ne}")
                    results.append(("TWO-SQUARE", f"{kw1}/{kw2}", 0, plain, berlin, ne))

                if "BERLIN" in plain or "CLOCK" in plain or "NORTH" in plain:
                    print(f"  Partial: {kw1}/{kw2}: {plain[55:85]}...")
            except Exception as e:
                pass

    # 4. ADFGVX CIPHER
    print("\n" + "=" * 40)
    print("4. ADFGVX CIPHER")
    print("=" * 40)

    # ADFGVX needs ciphertext to be ADFGVX letters only - K4 isn't
    # But we can try treating it as already-transposed fractionated text
    print("Note: K4 doesn't appear to be ADFGVX encoded (not limited to ADFGVX letters)")
    print("Skipping standard ADFGVX - trying modified approaches...")

    # 5. STRADDLING CHECKERBOARD
    print("\n" + "=" * 40)
    print("5. STRADDLING CHECKERBOARD")
    print("=" * 40)

    for keyword in KEYWORDS:
        try:
            plain = straddling_checkerboard_decrypt(K4, keyword)
            berlin, ne, bpos, npos = check_cribs(plain)

            if berlin or ne:
                print(f"\n*** MATCH: keyword={keyword}")
                print(f"    Plaintext: {plain}")
                results.append(("STRADDLING", keyword, 0, plain, berlin, ne))

            if len(plain) > 20:
                if "BERLIN" in plain or "CLOCK" in plain:
                    print(f"  Partial: {keyword}: {plain[:60]}...")
        except Exception as e:
            pass

    # 6. NIHILIST CIPHER
    print("\n" + "=" * 40)
    print("6. NIHILIST CIPHER")
    print("=" * 40)

    for polybius_kw in KEYWORDS:
        for num_kw in KEYWORDS:
            try:
                plain = nihilist_decrypt(K4, polybius_kw, num_kw)
                if len(plain) > 50:
                    berlin, ne, bpos, npos = check_cribs(plain)

                    if berlin or ne:
                        print(f"\n*** MATCH: poly={polybius_kw}, numkey={num_kw}")
                        print(f"    Plaintext: {plain}")
                        results.append(("NIHILIST", f"{polybius_kw}/{num_kw}", 0, plain, berlin, ne))
            except Exception as e:
                pass

    # 7. GRONSFELD CIPHER
    print("\n" + "=" * 40)
    print("7. GRONSFELD CIPHER")
    print("=" * 40)

    # Try numeric keys derived from keywords
    test_keys = ["31415926", "27182818", "12345", "54321", "19201", "0123456789"]
    test_keys.extend([str(i) for i in range(1000)])  # Try simple numeric keys

    for keyword in KEYWORDS:
        try:
            plain = gronsfeld_decrypt(K4, keyword)
            berlin, ne, bpos, npos = check_cribs(plain)

            if berlin or ne:
                print(f"\n*** MATCH: keyword={keyword}")
                print(f"    Plaintext: {plain}")
                results.append(("GRONSFELD", keyword, 0, plain, berlin, ne))

            if "BERLIN" in plain or "CLOCK" in plain or "NORTH" in plain:
                print(f"  Partial: {keyword}: ...{plain[55:85]}...")
        except Exception as e:
            pass

    for num_key in test_keys[:100]:  # Limit to first 100
        try:
            plain = gronsfeld_decrypt(K4, num_key)
            berlin, ne, bpos, npos = check_cribs(plain)

            if berlin or ne:
                print(f"\n*** MATCH: num_key={num_key}")
                print(f"    Plaintext: {plain}")
                results.append(("GRONSFELD", num_key, 0, plain, berlin, ne))
        except Exception as e:
            pass

    # 8. TRITHEMIUS CIPHER
    print("\n" + "=" * 40)
    print("8. TRITHEMIUS CIPHER")
    print("=" * 40)

    for start in range(26):
        plain = trithemius_decrypt(K4, start)
        berlin, ne, bpos, npos = check_cribs(plain)

        if berlin or ne:
            print(f"\n*** MATCH: start={start}")
            print(f"    Plaintext: {plain}")
            results.append(("TRITHEMIUS", str(start), 0, plain, berlin, ne))

        if "BERLIN" in plain or "CLOCK" in plain or "NORTH" in plain:
            print(f"  Partial: start={start}: ...{plain[55:85]}...")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY OF MATCHES")
    print("=" * 80)

    if results:
        for cipher, key, period, plain, berlin, ne in results:
            print(f"\n{cipher}: key={key}" + (f", period={period}" if period else ""))
            print(f"  BERLINCLOCK@63: {berlin}, NORTHEAST: {ne}")
            print(f"  Plaintext: {plain[:100]}...")
    else:
        print("No exact matches found for both BERLINCLOCK@63 and NORTHEAST")

    return results


if __name__ == "__main__":
    test_all_ciphers()
