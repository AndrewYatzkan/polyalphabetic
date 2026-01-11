#!/usr/bin/env python3
"""
Extended classical cipher testing on K4 with more variations
"""

import itertools
from typing import List, Tuple, Optional
import string

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW",
            "NORTHEAST", "BERLINCLOCK", "SANBORN", "SCHEIDT", "CIA", "LANGLEY",
            "UNDERGRUUND", "VIRTUALLY", "INVISIBLE", "DYAHR"]

def create_keyed_alphabet(keyword: str) -> str:
    """Create keyed alphabet"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper()
    seen = set()
    result = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            result.append(c)
            seen.add(c)
    return ''.join(result)

def create_polybius_square(keyword: str) -> Tuple[dict, dict]:
    """Create a 5x5 Polybius square (I=J)"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper().replace("J", "I")

    seen = set()
    key_chars = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            key_chars.append(c)
            seen.add(c)

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

        rows = []
        cols = []
        for c in block:
            if c in char_to_coords:
                r, col = char_to_coords[c]
                rows.append(r)
                cols.append(col)

        combined = rows + cols

        for i in range(0, len(combined) - 1, 2):
            coords = (combined[i], combined[i + 1])
            if coords in coords_to_char:
                plaintext.append(coords_to_char[coords])

    return ''.join(plaintext)

def bifid_encrypt(plaintext: str, keyword: str, period: int = 0) -> str:
    """Encrypt using Bifid cipher (for testing reverse)"""
    plaintext = plaintext.upper().replace("J", "I")
    char_to_coords, coords_to_char = create_polybius_square(keyword)

    if period == 0:
        period = len(plaintext)

    ciphertext = []
    for start in range(0, len(plaintext), period):
        block = plaintext[start:start + period]

        coords = []
        for c in block:
            if c in char_to_coords:
                coords.append(char_to_coords[c])

        # Take top row then bottom row
        rows = [c[0] for c in coords]
        cols = [c[1] for c in coords]

        combined = []
        for i in range(len(coords)):
            combined.append(rows[i])
            combined.append(cols[i])

        # Interleave differently - take pairs
        for i in range(0, len(combined), 2):
            r, c = combined[i], combined[i+1] if i+1 < len(combined) else 0
            if (r, c) in coords_to_char:
                ciphertext.append(coords_to_char[(r, c)])

    return ''.join(ciphertext)


def trifid_decrypt(ciphertext: str, keyword: str, period: int = 5) -> str:
    """Decrypt using Trifid cipher (3x3x3 cube)"""
    # 27 characters: A-Z plus #
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
    keyword = keyword.upper()

    seen = set()
    chars = []
    for c in keyword:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            chars.append(c)
            seen.add(c)

    char_to_coords = {}
    coords_to_char = {}
    for i, c in enumerate(chars):
        layer, row, col = i // 9, (i // 3) % 3, i % 3
        char_to_coords[c] = (layer, row, col)
        coords_to_char[(layer, row, col)] = c

    ciphertext = ciphertext.upper()
    plaintext = []

    for start in range(0, len(ciphertext), period):
        block = ciphertext[start:start + period]

        layers = []
        rows = []
        cols = []
        for c in block:
            if c in char_to_coords:
                l, r, co = char_to_coords[c]
                layers.append(l)
                rows.append(r)
                cols.append(co)

        combined = layers + rows + cols

        for i in range(0, len(combined) - 2, 3):
            coords = (combined[i], combined[i+1], combined[i+2])
            if coords in coords_to_char:
                plaintext.append(coords_to_char[coords])

    return ''.join(plaintext)


def playfair_decrypt(ciphertext: str, keyword: str) -> str:
    """Decrypt using Playfair cipher"""
    char_to_coords, coords_to_char = create_polybius_square(keyword)

    ciphertext = ciphertext.upper().replace("J", "I")
    plaintext = []

    for i in range(0, len(ciphertext) - 1, 2):
        c1, c2 = ciphertext[i], ciphertext[i+1]

        if c1 not in char_to_coords or c2 not in char_to_coords:
            continue

        r1, col1 = char_to_coords[c1]
        r2, col2 = char_to_coords[c2]

        if r1 == r2:  # Same row
            p1 = coords_to_char[(r1, (col1 - 1) % 5)]
            p2 = coords_to_char[(r2, (col2 - 1) % 5)]
        elif col1 == col2:  # Same column
            p1 = coords_to_char[((r1 - 1) % 5, col1)]
            p2 = coords_to_char[((r2 - 1) % 5, col2)]
        else:  # Rectangle
            p1 = coords_to_char[(r1, col2)]
            p2 = coords_to_char[(r2, col1)]

        plaintext.extend([p1, p2])

    return ''.join(plaintext)


def variant_beaufort_decrypt(ciphertext: str, keyword: str) -> str:
    """Variant Beaufort: P = K - C"""
    keyword = keyword.upper()
    ciphertext = ciphertext.upper()
    plaintext = []

    for i, c in enumerate(ciphertext):
        if c.isalpha():
            k = ord(keyword[i % len(keyword)]) - ord('A')
            ci = ord(c) - ord('A')
            p = (k - ci) % 26
            plaintext.append(chr(p + ord('A')))

    return ''.join(plaintext)


def beaufort_decrypt(ciphertext: str, keyword: str) -> str:
    """Beaufort: P = C - K (different from variant)"""
    keyword = keyword.upper()
    ciphertext = ciphertext.upper()
    plaintext = []

    for i, c in enumerate(ciphertext):
        if c.isalpha():
            k = ord(keyword[i % len(keyword)]) - ord('A')
            ci = ord(c) - ord('A')
            p = (ci - k) % 26
            plaintext.append(chr(p + ord('A')))

    return ''.join(plaintext)


def porta_decrypt(ciphertext: str, keyword: str) -> str:
    """Porta cipher decryption"""
    # Porta tableau
    alphabet1 = "ABCDEFGHIJKLM"
    alphabet2 = "NOPQRSTUVWXYZ"

    tableaux = [
        "NOPQRSTUVWXYZABCDEFGHIJKLM",
        "OPQRSTUVWXYZNMABCDEFGHIJKL",
        "PQRSTUVWXYZNOLMABCDEFGHIJK",
        "QRSTUVWXYZNOPKLMABCDEFGHIJ",
        "RSTUVWXYZNOPQJKLMABCDEFGHI",
        "STUVWXYZNOPQRIJKLMABCDEFGH",
        "TUVWXYZNOPQRSHIJKLMABCDEFG",
        "UVWXYZNOPQRSTGHIJKLMABCDEF",
        "VWXYZNOPQRSTUFGHIJKLMABCDE",
        "WXYZNOPQRSTUVEFGHIJKLMABCD",
        "XYZNOPQRSTUVWDEFGHIJKLMABC",
        "YZNOPQRSTUVWXCDEFGHIJKLMAB",
        "ZNOPQRSTUVWXYBCDEFGHIJKLMA",
    ]

    keyword = keyword.upper()
    ciphertext = ciphertext.upper()
    plaintext = []

    for i, c in enumerate(ciphertext):
        if c.isalpha():
            k = keyword[i % len(keyword)]
            row = (ord(k) - ord('A')) // 2

            if c in alphabet1:
                idx = alphabet1.index(c)
                plaintext.append(alphabet2[idx])
            else:
                idx = tableaux[row % len(tableaux)].find(c)
                if idx >= 0 and idx < 13:
                    plaintext.append(alphabet1[idx])
                elif idx >= 13:
                    plaintext.append(alphabet2[idx - 13])
                else:
                    plaintext.append(c)

    return ''.join(plaintext)


def autokey_decrypt(ciphertext: str, primer: str) -> str:
    """Autokey cipher decryption"""
    primer = primer.upper()
    ciphertext = ciphertext.upper()
    plaintext = []
    key = primer

    for i, c in enumerate(ciphertext):
        if c.isalpha():
            k = ord(key[i % len(key)] if i < len(key) else key[i]) - ord('A')
            ci = ord(c) - ord('A')
            p = (ci - k) % 26
            p_char = chr(p + ord('A'))
            plaintext.append(p_char)
            key += p_char

    return ''.join(plaintext)


def check_cribs(plaintext: str) -> dict:
    """Check for various cribs"""
    plaintext = plaintext.upper()

    result = {
        'berlinclock_at_63': False,
        'berlin_pos': plaintext.find('BERLIN'),
        'clock_pos': plaintext.find('CLOCK'),
        'northeast_pos': plaintext.find('NORTHEAST'),
        'north_pos': plaintext.find('NORTH'),
        'east_pos': plaintext.find('EAST'),
        'under_pos': plaintext.find('UNDER'),
        'above_pos': plaintext.find('ABOVE'),
        'ground_pos': plaintext.find('GROUND'),
        'shadow_pos': plaintext.find('SHADOW'),
    }

    if len(plaintext) > 73:
        if plaintext[63:74] == "BERLINCLOCK":
            result['berlinclock_at_63'] = True

    return result


def report_interesting(cipher_name: str, key_info: str, plaintext: str, cribs: dict):
    """Report if interesting patterns found"""
    interesting = False

    if cribs['berlinclock_at_63']:
        print(f"\n*** EXACT MATCH: {cipher_name} with {key_info}")
        print(f"    BERLINCLOCK at position 63!")
        interesting = True

    if cribs['northeast_pos'] >= 0:
        print(f"\n*** NORTHEAST FOUND: {cipher_name} with {key_info}")
        print(f"    NORTHEAST at position {cribs['northeast_pos']}")
        interesting = True

    # Check for partial matches
    partial = []
    if cribs['berlin_pos'] >= 0:
        partial.append(f"BERLIN@{cribs['berlin_pos']}")
    if cribs['clock_pos'] >= 0:
        partial.append(f"CLOCK@{cribs['clock_pos']}")
    if cribs['north_pos'] >= 0 and cribs['northeast_pos'] < 0:
        partial.append(f"NORTH@{cribs['north_pos']}")
    if cribs['under_pos'] >= 0:
        partial.append(f"UNDER@{cribs['under_pos']}")
    if cribs['shadow_pos'] >= 0:
        partial.append(f"SHADOW@{cribs['shadow_pos']}")

    if partial:
        print(f"\n  Partial ({cipher_name}, {key_info}): {', '.join(partial)}")
        print(f"    {plaintext[:80]}...")
        interesting = True

    return interesting


def test_extended():
    """Test extended cipher variations"""

    print("=" * 80)
    print("EXTENDED CLASSICAL CIPHER TESTING ON K4")
    print("=" * 80)
    print(f"\nK4: {K4}")
    print(f"Length: {len(K4)}\n")

    matches = []

    # 1. Bifid with many more periods
    print("\n[1] BIFID CIPHER - Extended Periods")
    print("-" * 40)
    for keyword in KEYWORDS:
        for period in range(3, 50):
            try:
                plain = bifid_decrypt(K4, keyword, period)
                cribs = check_cribs(plain)
                if report_interesting("BIFID", f"key={keyword}, period={period}", plain, cribs):
                    if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                        matches.append(("BIFID", keyword, period, plain))
            except:
                pass

    # 2. Trifid cipher
    print("\n[2] TRIFID CIPHER")
    print("-" * 40)
    for keyword in KEYWORDS:
        for period in range(3, 30):
            try:
                plain = trifid_decrypt(K4, keyword, period)
                cribs = check_cribs(plain)
                if report_interesting("TRIFID", f"key={keyword}, period={period}", plain, cribs):
                    if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                        matches.append(("TRIFID", keyword, period, plain))
            except:
                pass

    # 3. Playfair
    print("\n[3] PLAYFAIR CIPHER")
    print("-" * 40)
    for keyword in KEYWORDS:
        try:
            plain = playfair_decrypt(K4, keyword)
            cribs = check_cribs(plain)
            if report_interesting("PLAYFAIR", f"key={keyword}", plain, cribs):
                if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                    matches.append(("PLAYFAIR", keyword, 0, plain))
        except:
            pass

    # 4. Beaufort variants
    print("\n[4] BEAUFORT CIPHER VARIANTS")
    print("-" * 40)
    for keyword in KEYWORDS:
        try:
            plain = beaufort_decrypt(K4, keyword)
            cribs = check_cribs(plain)
            if report_interesting("BEAUFORT", f"key={keyword}", plain, cribs):
                if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                    matches.append(("BEAUFORT", keyword, 0, plain))
        except:
            pass

        try:
            plain = variant_beaufort_decrypt(K4, keyword)
            cribs = check_cribs(plain)
            if report_interesting("VAR-BEAUFORT", f"key={keyword}", plain, cribs):
                if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                    matches.append(("VAR-BEAUFORT", keyword, 0, plain))
        except:
            pass

    # 5. Porta cipher
    print("\n[5] PORTA CIPHER")
    print("-" * 40)
    for keyword in KEYWORDS:
        try:
            plain = porta_decrypt(K4, keyword)
            cribs = check_cribs(plain)
            if report_interesting("PORTA", f"key={keyword}", plain, cribs):
                if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                    matches.append(("PORTA", keyword, 0, plain))
        except:
            pass

    # 6. Autokey
    print("\n[6] AUTOKEY CIPHER")
    print("-" * 40)
    for keyword in KEYWORDS:
        try:
            plain = autokey_decrypt(K4, keyword)
            cribs = check_cribs(plain)
            if report_interesting("AUTOKEY", f"primer={keyword}", plain, cribs):
                if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                    matches.append(("AUTOKEY", keyword, 0, plain))
        except:
            pass

    # 7. Combined: Vigenere + Transposition tests
    print("\n[7] COMBINED APPROACHES")
    print("-" * 40)

    # Try simple transposition first, then Vigenere
    def simple_columnar_decrypt(ct: str, key_len: int) -> str:
        """Simple columnar transposition decryption"""
        n = len(ct)
        rows = (n + key_len - 1) // key_len

        # Calculate column lengths
        full_cols = n % key_len if n % key_len != 0 else key_len

        result = [''] * n
        pos = 0
        for col in range(key_len):
            col_len = rows if col < full_cols else rows - 1
            for row in range(col_len):
                if pos < n:
                    result[row * key_len + col] = ct[pos]
                    pos += 1

        return ''.join(result)

    def vigenere_decrypt(ct: str, key: str) -> str:
        key = key.upper()
        result = []
        for i, c in enumerate(ct.upper()):
            if c.isalpha():
                k = ord(key[i % len(key)]) - ord('A')
                p = (ord(c) - ord('A') - k) % 26
                result.append(chr(p + ord('A')))
        return ''.join(result)

    # Try transposition followed by Vigenere
    for trans_key_len in range(2, 15):
        transposed = simple_columnar_decrypt(K4, trans_key_len)
        for keyword in KEYWORDS[:6]:
            try:
                plain = vigenere_decrypt(transposed, keyword)
                cribs = check_cribs(plain)
                if report_interesting("TRANS+VIG", f"cols={trans_key_len}, key={keyword}", plain, cribs):
                    if cribs['berlinclock_at_63'] or cribs['northeast_pos'] >= 0:
                        matches.append(("TRANS+VIG", f"{trans_key_len}/{keyword}", 0, plain))
            except:
                pass

    # 8. Try reverse text
    print("\n[8] REVERSE TEXT VARIATIONS")
    print("-" * 40)

    K4_rev = K4[::-1]

    for keyword in KEYWORDS:
        for period in [0, 5, 7, 10, 13, 19]:
            try:
                plain = bifid_decrypt(K4_rev, keyword, period)
                cribs = check_cribs(plain)
                if report_interesting("REV-BIFID", f"key={keyword}, period={period}", plain, cribs):
                    matches.append(("REV-BIFID", keyword, period, plain))
            except:
                pass

        try:
            plain = playfair_decrypt(K4_rev, keyword)
            cribs = check_cribs(plain)
            if report_interesting("REV-PLAYFAIR", f"key={keyword}", plain, cribs):
                matches.append(("REV-PLAYFAIR", keyword, 0, plain))
        except:
            pass

    # Summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    if matches:
        print(f"\nFound {len(matches)} significant matches:")
        for cipher, key, period, plain in matches:
            print(f"\n  {cipher}: key={key}" + (f", period={period}" if period else ""))
            print(f"    Plaintext: {plain}")
    else:
        print("\nNo matches found for BERLINCLOCK@63 or NORTHEAST")
        print("Review partial matches above for potential leads.")


if __name__ == "__main__":
    test_extended()
