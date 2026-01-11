#!/usr/bin/env python3
"""
Test secondary cipher on K4 gibberish sections from Period 29 solution.

Period 29 solution gives:
UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF

Identified sections:
- UNDER (0-4) - READABLE
- QAPBZDBKZEL (5-15) - GIBBERISH
- NORTHEAST (16-24) - READABLE
- LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH (25-62) - GIBBERISH
- BERLINCLOCK (63-73) - READABLE
- RSPVJWQUL (74-82) - GIBBERISH
- ABOVE (83-87) - READABLE
- ZOLRKCAYF (88-96) - GIBBERISH
"""

import string

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# The partial solution with period 29
PERIOD29_PLAIN = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

# Gibberish sections
GIBBERISH_1 = "QAPBZDBKZEL"  # positions 5-15
GIBBERISH_2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"  # positions 25-62
GIBBERISH_3 = "RSPVJWQUL"  # positions 74-82
GIBBERISH_4 = "ZOLRKCAYF"  # positions 88-96

ALL_GIBBERISH = GIBBERISH_1 + GIBBERISH_2 + GIBBERISH_3 + GIBBERISH_4

KEYWORDS = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW",
            "NORTHEAST", "DYAHR", "SANBORN", "SCHEIDT"]


def create_keyed_alphabet(keyword: str) -> str:
    """Create keyed alphabet from keyword"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    seen = set()
    result = []
    for c in keyword.upper():
        if c in alphabet and c not in seen:
            result.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            result.append(c)
            seen.add(c)
    return ''.join(result)


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


def bifid_decrypt(ct: str, keyword: str, period: int = 0) -> str:
    """Bifid cipher decryption"""
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

        combined = rows + cols

        for i in range(0, len(combined) - 1, 2):
            coords = (combined[i], combined[i + 1])
            if coords in c2ch:
                result.append(c2ch[coords])

    return ''.join(result)


def playfair_decrypt(ct: str, keyword: str) -> str:
    """Playfair cipher decryption"""
    c2c, c2ch = create_polybius_square(keyword)
    ct = ct.upper().replace("J", "I")

    result = []
    for i in range(0, len(ct) - 1, 2):
        c1, c2 = ct[i], ct[i+1]

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


def vigenere_decrypt(ct: str, key: str) -> str:
    """Vigenere decryption"""
    key = key.upper()
    result = []
    for i, c in enumerate(ct.upper()):
        if c.isalpha():
            k = ord(key[i % len(key)]) - ord('A')
            p = (ord(c) - ord('A') - k) % 26
            result.append(chr(p + ord('A')))
    return ''.join(result)


def simple_sub_decrypt(ct: str, keyword: str) -> str:
    """Simple substitution from keyed alphabet"""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    keyed = create_keyed_alphabet(keyword)

    mapping = {keyed[i]: alphabet[i] for i in range(26)}
    return ''.join(mapping.get(c, c) for c in ct.upper())


def caesar_decrypt(ct: str, shift: int) -> str:
    """Caesar cipher decryption"""
    result = []
    for c in ct.upper():
        if c.isalpha():
            p = (ord(c) - ord('A') - shift) % 26
            result.append(chr(p + ord('A')))
    return ''.join(result)


def atbash(ct: str) -> str:
    """Atbash cipher"""
    result = []
    for c in ct.upper():
        if c.isalpha():
            p = 25 - (ord(c) - ord('A'))
            result.append(chr(p + ord('A')))
    return ''.join(result)


def rot13(ct: str) -> str:
    """ROT13"""
    return caesar_decrypt(ct, 13)


def affine_decrypt(ct: str, a: int, b: int) -> str:
    """Affine cipher decryption"""
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


def reverse_text(text: str) -> str:
    """Reverse text"""
    return text[::-1]


def rail_fence_decrypt(ct: str, rails: int) -> str:
    """Rail fence cipher decryption"""
    n = len(ct)
    if rails <= 1:
        return ct

    # Calculate period
    period = 2 * (rails - 1)

    # Calculate rail lengths
    lengths = [0] * rails
    for i in range(n):
        rail = i % period
        if rail >= rails:
            rail = period - rail
        lengths[rail] += 1

    # Split ciphertext into rails
    rail_texts = []
    pos = 0
    for length in lengths:
        rail_texts.append(list(ct[pos:pos + length]))
        pos += length

    # Read off in zigzag
    result = []
    indices = [0] * rails
    for i in range(n):
        rail = i % period
        if rail >= rails:
            rail = period - rail
        if indices[rail] < len(rail_texts[rail]):
            result.append(rail_texts[rail][indices[rail]])
            indices[rail] += 1

    return ''.join(result)


def columnar_decrypt(ct: str, key_len: int) -> str:
    """Simple columnar transposition"""
    n = len(ct)
    num_rows = (n + key_len - 1) // key_len

    # Calculate column lengths
    full_cols = n % key_len if n % key_len != 0 else key_len

    result = [''] * n
    pos = 0
    for col in range(key_len):
        col_len = num_rows if col < full_cols else num_rows - 1
        for row in range(col_len):
            if pos < n:
                idx = row * key_len + col
                if idx < n:
                    result[idx] = ct[pos]
                pos += 1

    return ''.join(result)


def find_words(text: str) -> list:
    """Find English words"""
    words = ["BERLIN", "CLOCK", "NORTHEAST", "NORTH", "EAST", "SOUTH", "WEST",
             "UNDER", "ABOVE", "GROUND", "SHADOW", "VISIBLE", "INVISIBLE",
             "SECRET", "HIDDEN", "LAYER", "BURIED", "SLOWLY", "VIRTUAL",
             "BETWEEN", "SUBTLE", "LIGHT", "DARK", "TIME", "PASS", "PASSAGE",
             "DEGREE", "MINUTE", "SECOND", "WEST", "LOCATION", "WHERE", "THERE",
             "THE", "AND", "BUT", "NOT", "FOR", "ALL", "CAN", "HER", "WAS", "ONE",
             "THAT", "WITH", "THEY", "HAVE", "THIS", "WILL", "YOUR", "FROM",
             "WHAT", "WERE", "BEEN", "CALL", "FIRST", "WATER", "AFTER", "DOWN",
             "SHOULD", "COULD", "THESE", "ABOUT", "WOULD", "MADE", "FIND"]

    found = []
    text = text.upper()
    for word in words:
        if len(word) >= 4 and word in text:
            pos = text.find(word)
            found.append((word, pos))

    return found


def analyze_gibberish(name: str, text: str):
    """Try various decryptions on gibberish sections"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {name}")
    print(f"Text: {text}")
    print(f"Length: {len(text)}")
    print(f"{'='*60}")

    results = []

    # Simple transformations
    rev = reverse_text(text)
    words = find_words(rev)
    if words:
        print(f"  REVERSE: {rev} -> {words}")
        results.append(("REVERSE", rev, words))

    atb = atbash(text)
    words = find_words(atb)
    if words:
        print(f"  ATBASH: {atb} -> {words}")
        results.append(("ATBASH", atb, words))

    # Caesar shifts
    for shift in range(1, 26):
        dec = caesar_decrypt(text, shift)
        words = find_words(dec)
        if words:
            print(f"  CAESAR-{shift}: {dec} -> {words}")
            results.append((f"CAESAR-{shift}", dec, words))

    # Vigenere with keywords
    for kw in KEYWORDS:
        dec = vigenere_decrypt(text, kw)
        words = find_words(dec)
        if words:
            print(f"  VIG-{kw}: {dec} -> {words}")
            results.append((f"VIG-{kw}", dec, words))

    # Simple substitution with keywords
    for kw in KEYWORDS:
        dec = simple_sub_decrypt(text, kw)
        words = find_words(dec)
        if words:
            print(f"  SUB-{kw}: {dec} -> {words}")
            results.append((f"SUB-{kw}", dec, words))

    # Bifid with various periods
    for kw in KEYWORDS:
        for period in [0, 3, 5, 7, 9, 11]:
            try:
                dec = bifid_decrypt(text, kw, period)
                words = find_words(dec)
                if words:
                    print(f"  BIFID-{kw}-{period}: {dec} -> {words}")
                    results.append((f"BIFID-{kw}-{period}", dec, words))
            except:
                pass

    # Playfair
    for kw in KEYWORDS:
        try:
            dec = playfair_decrypt(text, kw)
            words = find_words(dec)
            if words:
                print(f"  PLAYFAIR-{kw}: {dec} -> {words}")
                results.append((f"PLAYFAIR-{kw}", dec, words))
        except:
            pass

    # Rail fence
    for rails in range(2, 6):
        try:
            dec = rail_fence_decrypt(text, rails)
            words = find_words(dec)
            if words:
                print(f"  RAILFENCE-{rails}: {dec} -> {words}")
                results.append((f"RAILFENCE-{rails}", dec, words))
        except:
            pass

    # Columnar transposition
    for key_len in range(2, 8):
        try:
            dec = columnar_decrypt(text, key_len)
            words = find_words(dec)
            if words:
                print(f"  COLUMNAR-{key_len}: {dec} -> {words}")
                results.append((f"COLUMNAR-{key_len}", dec, words))
        except:
            pass

    # Affine cipher
    valid_a = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
    for a in valid_a:
        for b in range(26):
            dec = affine_decrypt(text, a, b)
            words = find_words(dec)
            if words:
                print(f"  AFFINE-{a}-{b}: {dec} -> {words}")
                results.append((f"AFFINE-{a}-{b}", dec, words))

    if not results:
        print("  No English words found with tested ciphers")

    return results


def test_combined_gibberish():
    """Test all gibberish sections together"""
    print(f"\n{'#'*70}")
    print("COMBINED GIBBERISH ANALYSIS")
    print(f"{'#'*70}")

    all_gib = ALL_GIBBERISH
    print(f"\nAll gibberish combined: {all_gib}")
    print(f"Length: {len(all_gib)}")

    analyze_gibberish("ALL_GIBBERISH", all_gib)


def test_secondary_layer_on_original():
    """Test if original K4 might have secondary cipher before Vigenere"""
    print(f"\n{'#'*70}")
    print("TESTING SECONDARY CIPHER BEFORE PERIOD 29 VIGENERE")
    print(f"{'#'*70}")

    # Maybe K4 = Vigenere(Secondary(Plaintext))
    # So we should try Secondary on K4 first, then Vigenere

    # Try Playfair then Vigenere
    for play_kw in KEYWORDS[:4]:
        try:
            playfair_ct = playfair_decrypt(K4, play_kw)

            # Then try Vigenere with Period 29 key
            key29 = "DIJJQELYOIECBAQKVAATCRDUMPABT"  # The period 29 key

            result = vigenere_decrypt(playfair_ct, key29[:len(playfair_ct)])
            words = find_words(result)
            if words:
                print(f"\n  PLAYFAIR({play_kw}) -> VIG29: {words}")
                print(f"    {result[:50]}...")
        except:
            pass

    # Try Bifid then Vigenere
    for bifid_kw in KEYWORDS[:4]:
        for period in [0, 5, 7, 11]:
            try:
                bifid_ct = bifid_decrypt(K4, bifid_kw, period)

                key29 = "DIJJQELYOIECBAQKVAATCRDUMPABT"
                result = vigenere_decrypt(bifid_ct, key29[:len(bifid_ct)])
                words = find_words(result)
                if words:
                    print(f"\n  BIFID({bifid_kw},p={period}) -> VIG29: {words}")
                    print(f"    {result[:50]}...")
            except:
                pass


def main():
    print("=" * 70)
    print("K4 SECONDARY CIPHER ANALYSIS")
    print("=" * 70)
    print(f"\nPeriod 29 partial solution:")
    print(f"{PERIOD29_PLAIN}")
    print(f"\nReadable: UNDER (0-4), NORTHEAST (16-24), BERLINCLOCK (63-73), ABOVE (83-87)")
    print(f"Gibberish sections to analyze:")
    print(f"  1: {GIBBERISH_1} (pos 5-15)")
    print(f"  2: {GIBBERISH_2} (pos 25-62)")
    print(f"  3: {GIBBERISH_3} (pos 74-82)")
    print(f"  4: {GIBBERISH_4} (pos 88-96)")

    # Analyze each gibberish section
    analyze_gibberish("GIBBERISH_1 (pos 5-15)", GIBBERISH_1)
    analyze_gibberish("GIBBERISH_2 (pos 25-62)", GIBBERISH_2)
    analyze_gibberish("GIBBERISH_3 (pos 74-82)", GIBBERISH_3)
    analyze_gibberish("GIBBERISH_4 (pos 88-96)", GIBBERISH_4)

    # Try combined
    test_combined_gibberish()

    # Try secondary cipher on original K4
    test_secondary_layer_on_original()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
