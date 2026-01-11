#!/usr/bin/env python3
"""
Exotic cipher approaches on K4 with comprehensive partial matching
"""

import itertools
import string
import random
from collections import defaultdict

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "DYAHR"]

def find_words(text: str) -> list:
    """Find English words in text"""
    # Common words that might appear
    words = ["BERLIN", "CLOCK", "NORTHEAST", "NORTH", "EAST", "SOUTH", "WEST",
             "UNDER", "ABOVE", "GROUND", "SHADOW", "VISIBLE", "INVISIBLE",
             "SECRET", "HIDDEN", "LAYER", "BURIED", "SLOWLY", "VIRTUAL",
             "BETWEEN", "SUBTLE", "LIGHT", "DARK", "TIME", "PASS", "PASSAGE"]

    found = []
    text = text.upper()
    for word in words:
        if word in text:
            pos = text.find(word)
            found.append((word, pos))

    return found


def report_if_interesting(cipher: str, key_info: str, plaintext: str) -> bool:
    """Report if plaintext contains interesting patterns"""
    found = find_words(plaintext)

    # Check for BERLINCLOCK at position 63
    berlin_at_63 = len(plaintext) > 73 and plaintext[63:74] == "BERLINCLOCK"

    if berlin_at_63:
        print(f"\n{'*' * 70}")
        print(f"EXACT BERLINCLOCK@63: {cipher} | {key_info}")
        print(f"Plaintext: {plaintext}")
        return True

    if found:
        print(f"\n  {cipher} ({key_info}): {found}")
        print(f"    ...{plaintext[50:80]}..." if len(plaintext) > 80 else f"    {plaintext}")
        return True

    return False


# ============================================
# DIGRAFID CIPHER
# ============================================
def digrafid_decrypt(ct: str, keyword: str, period: int = 9) -> str:
    """Digrafid cipher (combination of bifid and Playfair)"""
    # Create two 5x5 squares and one 3x3 square
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    keyword = keyword.upper().replace("J", "I")

    seen = set()
    chars = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)

    # 9x3 grid for fractionation
    c2c = {}
    c2ch = {}
    for i, c in enumerate(chars[:25]):
        row, col = i // 3, i % 9
        if col < 9 and row < 3:
            c2c[c] = (row, col)
            c2ch[(row, col)] = c

    ct = ct.upper().replace("J", "I")
    result = []

    for start in range(0, len(ct), period):
        block = ct[start:start + period]

        rows = []
        for c in block:
            if c in c2c:
                r, col = c2c[c]
                rows.append(r)
                rows.append(col)

        for i in range(0, len(rows) - 1, 2):
            coords = (rows[i] % 3, rows[i+1] % 9)
            if coords in c2ch:
                result.append(c2ch[coords])

    return ''.join(result)


# ============================================
# CM BIFID (Conjugated Matrix Bifid)
# ============================================
def cm_bifid_decrypt(ct: str, keyword: str, period: int = 5) -> str:
    """CM Bifid - uses two different Polybius squares"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"

    # First square from keyword
    kw1 = keyword.upper().replace("J", "I")
    seen = set()
    chars1 = []
    for c in kw1 + alphabet:
        if c in alphabet and c not in seen:
            chars1.append(c)
            seen.add(c)

    # Second square - reversed keyword
    kw2 = kw1[::-1]
    seen = set()
    chars2 = []
    for c in kw2 + alphabet:
        if c in alphabet and c not in seen:
            chars2.append(c)
            seen.add(c)

    c2c1 = {}
    c2ch1 = {}
    c2c2 = {}
    c2ch2 = {}

    for i in range(25):
        r, col = i // 5, i % 5
        c2c1[chars1[i]] = (r, col)
        c2ch1[(r, col)] = chars1[i]
        c2c2[chars2[i]] = (r, col)
        c2ch2[(r, col)] = chars2[i]

    ct = ct.upper().replace("J", "I")

    if period == 0:
        period = len(ct)

    result = []
    for start in range(0, len(ct), period):
        block = ct[start:start + period]

        rows = []
        cols = []
        for c in block:
            if c in c2c1:
                r, col = c2c1[c]
                rows.append(r)
                cols.append(col)

        combined = rows + cols

        for i in range(0, len(combined) - 1, 2):
            coords = (combined[i], combined[i + 1])
            if coords in c2ch2:  # Use second square for output
                result.append(c2ch2[coords])

    return ''.join(result)


# ============================================
# FRACTIONATED MORSE
# ============================================
def fractionated_morse_decrypt(ct: str, keyword: str) -> str:
    """Fractionated Morse - converts letters to morse then regroups"""
    morse = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', ' ': 'x'
    }

    # Create keyed alphabet for trigraph mapping
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kw = keyword.upper()
    seen = set()
    keyed = []
    for c in kw + alphabet:
        if c in alphabet and c not in seen:
            keyed.append(c)
            seen.add(c)

    # Map 26 letters to morse trigraphs (incomplete - simplified)
    trigraphs = []
    for a in '.x-':
        for b in '.x-':
            for c in '.x-':
                trigraphs.append(a + b + c)

    char_to_tri = {}
    for i, c in enumerate(keyed):
        if i < len(trigraphs):
            char_to_tri[c] = trigraphs[i]

    # This is a simplified version - real implementation more complex
    ct = ct.upper()
    morse_stream = ''.join(char_to_tri.get(c, '') for c in ct)

    # Try to decode back
    result = []
    morse_rev = {v: k for k, v in morse.items()}
    current = ''
    for c in morse_stream:
        if c == 'x':
            if current in morse_rev:
                result.append(morse_rev[current])
            current = ''
        else:
            current += c

    return ''.join(result)


# ============================================
# BAZERIES CIPHER
# ============================================
def bazeries_decrypt(ct: str, num_key: int, keyword: str) -> str:
    """Bazeries cipher - combines transposition and substitution"""
    # Create substitution alphabet from keyword
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    kw = keyword.upper().replace("J", "I")

    seen = set()
    sub_alpha = []
    for c in kw + alphabet:
        if c in alphabet and c not in seen:
            sub_alpha.append(c)
            seen.add(c)

    # Create mapping
    sub_map = {alphabet[i]: sub_alpha[i] for i in range(25)}
    rev_map = {v: k for k, v in sub_map.items()}

    # Apply substitution first (reverse of encryption)
    substituted = ''.join(rev_map.get(c, c) for c in ct.upper().replace("J", "I"))

    # Then reverse transposition based on spelled number
    # Simplified - just doing basic period transposition
    period = num_key % 20 + 2

    # Column transposition decryption
    n = len(substituted)
    num_cols = period
    num_full_rows = n // num_cols
    extra = n % num_cols

    result = [''] * n
    pos = 0
    for col in range(num_cols):
        rows = num_full_rows + (1 if col < extra else 0)
        for row in range(rows):
            if pos < n and row * num_cols + col < n:
                result[row * num_cols + col] = substituted[pos]
                pos += 1

    return ''.join(result)


# ============================================
# POLLUX CIPHER (variant)
# ============================================
def pollux_variant(ct: str, keyword: str) -> str:
    """Modified Pollux-style cipher"""
    # Map letters to numbers 0-9 based on position in keyword alphabet
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kw = keyword.upper()

    seen = set()
    keyed = []
    for c in kw + alphabet:
        if c in alphabet and c not in seen:
            keyed.append(c)
            seen.add(c)

    # Map each letter to its position mod 10
    char_to_digit = {c: i % 10 for i, c in enumerate(keyed)}

    # Convert ciphertext to digit stream
    digits = [char_to_digit.get(c, 0) for c in ct.upper() if c.isalpha()]

    # Try to interpret digit pairs as letter positions
    result = []
    for i in range(0, len(digits) - 1, 2):
        pos = digits[i] * 10 + digits[i + 1]
        if 0 <= pos < 26:
            result.append(chr(pos + ord('A')))

    return ''.join(result)


# ============================================
# GRANDPRE CIPHER
# ============================================
def grandpre_decrypt(ct: str, keyword: str) -> str:
    """Grandpré cipher - digraph substitution"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    kw = keyword.upper().replace("J", "I")

    # Create 5x5 square
    seen = set()
    chars = []
    for c in kw + alphabet:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)

    c2c = {}
    c2ch = {}
    for i, c in enumerate(chars):
        r, col = i // 5, i % 5
        c2c[c] = (r, col)
        c2ch[(r, col)] = c

    ct = ct.upper().replace("J", "I")
    result = []

    # Each pair of letters decrypts via coordinates
    for i in range(0, len(ct) - 1, 2):
        c1, c2 = ct[i], ct[i+1]
        if c1 in c2c and c2 in c2c:
            r1, col1 = c2c[c1]
            r2, col2 = c2c[c2]

            # Decode: use first letter's row and second's column
            p = c2ch.get((r1, col2), '?')
            result.append(p)

    return ''.join(result)


# ============================================
# MONOME-DINOME
# ============================================
def monome_dinome_decrypt(ct: str, keyword: str) -> str:
    """Monome-Dinome cipher"""
    # Single and double substitution hybrid
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kw = keyword.upper()

    seen = set()
    keyed = []
    for c in kw + alphabet:
        if c in alphabet and c not in seen:
            keyed.append(c)
            seen.add(c)

    # First 8 letters are single-digit (1-8)
    # Rest are two-digit (91-99, 01-09, etc.)
    single = keyed[:8]
    double = keyed[8:]

    ct = ct.upper()
    result = []
    i = 0

    while i < len(ct):
        c = ct[i]
        if c in single:
            # Single letter substitution
            idx = single.index(c)
            result.append(keyed[idx])
            i += 1
        elif i + 1 < len(ct):
            # Double letter substitution
            pair = ct[i:i+2]
            # Simplified decoding
            if ct[i] in double and ct[i+1] in keyed:
                idx = (keyed.index(ct[i]) + keyed.index(ct[i+1])) % 26
                result.append(alphabet[idx])
            i += 2
        else:
            i += 1

    return ''.join(result)


# ============================================
# QUAGMIRE VARIANTS
# ============================================
def quagmire_decrypt(ct: str, pt_keyword: str, ct_keyword: str, indicator: str) -> str:
    """Quagmire cipher variants"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # Create plaintext alphabet
    seen = set()
    pt_alpha = []
    for c in pt_keyword.upper():
        if c in alphabet and c not in seen:
            pt_alpha.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            pt_alpha.append(c)
            seen.add(c)

    # Create ciphertext alphabet
    seen = set()
    ct_alpha = []
    for c in ct_keyword.upper():
        if c in alphabet and c not in seen:
            ct_alpha.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            ct_alpha.append(c)
            seen.add(c)

    # Indicator word shifts the cipher alphabet
    ind = indicator.upper()

    result = []
    for i, c in enumerate(ct.upper()):
        if c in alphabet:
            # Get shift from indicator
            ind_char = ind[i % len(ind)]
            shift = alphabet.index(ind_char) if ind_char in alphabet else 0

            # Find position in shifted cipher alphabet
            ct_idx = ct_alpha.index(c) if c in ct_alpha else -1
            if ct_idx >= 0:
                # Apply shift and map back through plaintext alphabet
                pt_idx = (ct_idx - shift) % 26
                result.append(pt_alpha[pt_idx])

    return ''.join(result)


def test_all_exotic():
    """Test all exotic ciphers"""

    print("=" * 70)
    print("EXOTIC CIPHER TESTING ON K4")
    print("=" * 70)
    print(f"K4: {K4}")
    print(f"Length: {len(K4)}")
    print()

    matches = []

    # 1. Digrafid
    print("\n[1] DIGRAFID CIPHER")
    print("-" * 40)
    for kw in KEYWORDS:
        for period in [5, 7, 9, 11, 13]:
            try:
                plain = digrafid_decrypt(K4, kw, period)
                if report_if_interesting("DIGRAFID", f"kw={kw}, p={period}", plain):
                    matches.append(("DIGRAFID", kw, period, plain))
            except:
                pass

    # 2. CM Bifid
    print("\n[2] CM BIFID")
    print("-" * 40)
    for kw in KEYWORDS:
        for period in [3, 5, 7, 9, 11, 13, 19, 29]:
            try:
                plain = cm_bifid_decrypt(K4, kw, period)
                if report_if_interesting("CM-BIFID", f"kw={kw}, p={period}", plain):
                    matches.append(("CM-BIFID", kw, period, plain))
            except:
                pass

    # 3. Fractionated Morse
    print("\n[3] FRACTIONATED MORSE")
    print("-" * 40)
    for kw in KEYWORDS:
        try:
            plain = fractionated_morse_decrypt(K4, kw)
            if report_if_interesting("FRAC-MORSE", f"kw={kw}", plain):
                matches.append(("FRAC-MORSE", kw, 0, plain))
        except:
            pass

    # 4. Bazeries
    print("\n[4] BAZERIES CIPHER")
    print("-" * 40)
    for num in range(1, 100):
        for kw in KEYWORDS:
            try:
                plain = bazeries_decrypt(K4, num, kw)
                if report_if_interesting("BAZERIES", f"n={num}, kw={kw}", plain):
                    matches.append(("BAZERIES", f"{num}/{kw}", 0, plain))
            except:
                pass

    # 5. Pollux variant
    print("\n[5] POLLUX VARIANT")
    print("-" * 40)
    for kw in KEYWORDS:
        try:
            plain = pollux_variant(K4, kw)
            if report_if_interesting("POLLUX", f"kw={kw}", plain):
                matches.append(("POLLUX", kw, 0, plain))
        except:
            pass

    # 6. Grandpré
    print("\n[6] GRANDPRE CIPHER")
    print("-" * 40)
    for kw in KEYWORDS:
        try:
            plain = grandpre_decrypt(K4, kw)
            if report_if_interesting("GRANDPRE", f"kw={kw}", plain):
                matches.append(("GRANDPRE", kw, 0, plain))
        except:
            pass

    # 7. Quagmire variants
    print("\n[7] QUAGMIRE CIPHER")
    print("-" * 40)
    for pt_kw in KEYWORDS[:4]:
        for ct_kw in KEYWORDS[:4]:
            for ind in KEYWORDS[:4]:
                try:
                    plain = quagmire_decrypt(K4, pt_kw, ct_kw, ind)
                    if report_if_interesting("QUAGMIRE", f"pt={pt_kw}, ct={ct_kw}, ind={ind}", plain):
                        matches.append(("QUAGMIRE", f"{pt_kw}/{ct_kw}/{ind}", 0, plain))
                except:
                    pass

    # 8. Simple substitutions with transposition
    print("\n[8] SUBSTITUTION + TRANSPOSITION")
    print("-" * 40)

    def simple_sub(ct: str, key: str) -> str:
        """Simple substitution cipher"""
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        kw = key.upper()
        seen = set()
        keyed = []
        for c in kw:
            if c in alphabet and c not in seen:
                keyed.append(c)
                seen.add(c)
        for c in alphabet:
            if c not in seen:
                keyed.append(c)
                seen.add(c)

        mapping = {keyed[i]: alphabet[i] for i in range(26)}
        return ''.join(mapping.get(c, c) for c in ct.upper())

    def route_decrypt(ct: str, rows: int) -> str:
        """Route transposition"""
        n = len(ct)
        cols = (n + rows - 1) // rows

        grid = [[''] * cols for _ in range(rows)]
        pos = 0
        for r in range(rows):
            for c in range(cols):
                if pos < n:
                    grid[r][c] = ct[pos]
                    pos += 1

        # Read columns
        result = []
        for c in range(cols):
            for r in range(rows):
                if grid[r][c]:
                    result.append(grid[r][c])

        return ''.join(result)

    for kw in KEYWORDS:
        for rows in range(2, 15):
            try:
                # Sub then route
                subbed = simple_sub(K4, kw)
                routed = route_decrypt(subbed, rows)
                if report_if_interesting("SUB+ROUTE", f"kw={kw}, rows={rows}", routed):
                    matches.append(("SUB+ROUTE", f"{kw}/{rows}", 0, routed))

                # Route then sub
                routed = route_decrypt(K4, rows)
                subbed = simple_sub(routed, kw)
                if report_if_interesting("ROUTE+SUB", f"rows={rows}, kw={kw}", subbed):
                    matches.append(("ROUTE+SUB", f"{rows}/{kw}", 0, subbed))
            except:
                pass

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if matches:
        print(f"\nFound {len(matches)} interesting results:")
        for cipher, key, period, plain in matches:
            print(f"\n  {cipher}: {key}" + (f", period={period}" if period else ""))
            print(f"    {plain[:80]}...")
    else:
        print("\nNo significant matches found")


if __name__ == "__main__":
    test_all_exotic()
