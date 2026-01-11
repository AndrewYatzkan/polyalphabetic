#!/usr/bin/env python3
"""
Test ALTERNATE CIPHERS on the 67-character gibberish section.
Hypothesis: The gibberish might use a DIFFERENT cipher than the readable words.

Gibberish: QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF (67 chars)

Tests:
1. Atbash (reverse alphabet)
2. ROT13 and other Caesar shifts (1-25)
3. Beaufort cipher with various keys
4. Playfair cipher
5. Bifid cipher
6. Autokey with seeds from K1-K3
7. Book cipher using K1-K3 plaintext
8. Gibberish as KEY to decrypt K4 or other sections
"""

import string
from collections import Counter
from itertools import permutations

GIBBERISH = "QAPBZDBKZELLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHRSPVJWQULZOLRKCAYF"

# Full K4 plaintext for reference
K4_PLAINTEXT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTBJQHTMTKLLHALRPDEDRLSPLHSVYVJAJUJINITIALIZED"

# K1 plaintext
K1_PLAIN = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

# K2 plaintext
K2_PLAIN = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLE"

# K3 plaintext
K3_PLAIN = "THEPAINOFPLEASUREANDTHEPLEASUREOFPAINISLETSCHANGETHEARRANGEMENT"

# Known readable words in K4
K4_CRIBS = ["BERLIN", "CLOCK", "NORTHEAST", "NORTH", "EAST", "COORDINATES"]

def calculate_ioc(text):
    """Calculate Index of Coincidence"""
    text = text.upper()
    counts = Counter(c for c in text if c.isalpha())
    n = sum(counts.values())
    if n == 0:
        return 0
    ioc = sum(count * (count - 1) for count in counts.values()) / (n * (n - 1))
    return ioc

def atbash_decrypt(ciphertext):
    """Atbash cipher: reverse alphabet (A<->Z, B<->Y, etc)"""
    result = []
    for c in ciphertext.upper():
        if c.isalpha():
            result.append(chr(ord('Z') - (ord(c) - ord('A'))))
        else:
            result.append(c)
    return ''.join(result)

def caesar_decrypt(ciphertext, shift):
    """Caesar cipher with given shift"""
    result = []
    for c in ciphertext.upper():
        if c.isalpha():
            result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)

def beaufort_decrypt(ciphertext, key):
    """Beaufort cipher decryption"""
    key = key.upper()
    result = []
    key_pos = 0

    for c in ciphertext.upper():
        if c.isalpha():
            shift = ord(key[key_pos % len(key)]) - ord('A')
            # Beaufort: PT = Key - CT (mod 26)
            plainchar = chr((ord(key[key_pos % len(key)]) - ord(c)) % 26 + ord('A'))
            result.append(plainchar)
            key_pos += 1
        else:
            result.append(c)

    return ''.join(result)

def create_playfair_square(keyword=""):
    """Create 5x5 Playfair square"""
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # No J
    keyword = keyword.upper().replace("J", "I")

    seen = set()
    chars = []
    for c in keyword + alphabet:
        if c in alphabet and c not in seen:
            chars.append(c)
            seen.add(c)

    square = {}
    for i, c in enumerate(chars[:25]):
        square[c] = (i // 5, i % 5)

    return square

def playfair_decrypt(ciphertext, keyword):
    """Simplified Playfair decryption (assuming even-length ciphertext)"""
    square = create_playfair_square(keyword)
    ciphertext = ciphertext.upper().replace("J", "I")

    if len(ciphertext) % 2 == 1:
        ciphertext += "X"

    plaintext = []
    for i in range(0, len(ciphertext), 2):
        c1, c2 = ciphertext[i], ciphertext[i+1]

        if c1 not in square or c2 not in square:
            continue

        r1, col1 = square[c1]
        r2, col2 = square[c2]

        if r1 == r2:  # Same row
            new_col1 = (col1 - 1) % 5
            new_col2 = (col2 - 1) % 5
        elif col1 == col2:  # Same column
            new_r1 = (r1 - 1) % 5
            new_r2 = (r2 - 1) % 5
            # Find chars at new positions
            for c, (r, c_col) in square.items():
                if c_col == col1 and r == new_r1:
                    plaintext.append(c)
                if c_col == col2 and r == new_r2:
                    plaintext.append(c)
            continue
        else:  # Rectangle
            new_col1 = col2
            new_col2 = col1

        for c, (r, c_col) in square.items():
            if r == r1 and c_col == new_col1:
                plaintext.append(c)
            if r == r2 and c_col == new_col2:
                plaintext.append(c)

    return ''.join(plaintext)

def bifid_decrypt(ciphertext, keyword, period=0):
    """Bifid cipher decryption"""
    square = create_playfair_square(keyword)
    ciphertext = ciphertext.upper().replace("J", "I")

    if period == 0 or period >= len(ciphertext):
        period = len(ciphertext)

    plaintext = []
    for start in range(0, len(ciphertext), period):
        block = ciphertext[start:start + period]

        rows = []
        cols = []
        for c in block:
            if c in square:
                r, col = square[c]
                rows.append(r)
                cols.append(col)

        combined = rows + cols

        for i in range(0, len(combined) - 1, 2):
            r, col = combined[i], combined[i + 1]
            for c, (cr, cc) in square.items():
                if cr == r and cc == col:
                    plaintext.append(c)
                    break

    return ''.join(plaintext)

def vigenere_decrypt(ciphertext, key):
    """Vigenere cipher decryption"""
    key = key.upper()
    result = []
    key_pos = 0

    for c in ciphertext.upper():
        if c.isalpha():
            shift = ord(key[key_pos % len(key)]) - ord('A')
            result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
            key_pos += 1
        else:
            result.append(c)

    return ''.join(result)

def autokey_decrypt(ciphertext, seed_key):
    """Autokey cipher decryption"""
    key = seed_key.upper()
    ciphertext = ciphertext.upper()
    result = []

    for c in ciphertext:
        if c.isalpha():
            shift = ord(key[len(result) % len(key)]) - ord('A')
            plainchar = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            result.append(plainchar)
            key += plainchar  # Extend key with plaintext
        else:
            result.append(c)

    return ''.join(result)

def count_english_words(text, common_words=None):
    """Count how many common English words appear in text"""
    if common_words is None:
        common_words = {"THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
                       "WAS", "ONE", "OUR", "OUT", "NOW", "NEW", "HAD", "HIS", "HOW", "ITS",
                       "MAY", "SAY", "SHE", "TOO", "USE", "WHO", "BOY", "DID", "GET", "GOT",
                       "LET", "PUT", "SAY", "WAY", "WHO", "BERLIN", "CLOCK", "NORTH", "EAST",
                       "COORDINATES", "NORTHEAST"}

    words = text.upper().split()
    count = 0
    for word in words:
        word_clean = ''.join(c for c in word if c.isalpha())
        if word_clean in common_words:
            count += 1
    return count

def gibberish_as_key_vigenere(ciphertext, gibberish_key):
    """Use gibberish as Vigenere key on full K4"""
    return vigenere_decrypt(ciphertext, gibberish_key)

def gibberish_as_key_autokey(ciphertext, gibberish_key):
    """Use gibberish as autokey seed on full K4"""
    return autokey_decrypt(ciphertext, gibberish_key)

def gibberish_as_key_beaufort(ciphertext, gibberish_key):
    """Use gibberish as Beaufort key on full K4"""
    return beaufort_decrypt(ciphertext, gibberish_key)

def test_atbash():
    """Test Atbash cipher on gibberish"""
    print("\n" + "="*70)
    print("1. ATBASH CIPHER")
    print("="*70)

    result = atbash_decrypt(GIBBERISH)
    ioc = calculate_ioc(result)

    print(f"Input:  {GIBBERISH}")
    print(f"Output: {result}")
    print(f"IoC: {ioc:.4f} (English ~0.067)")

    # Check for words
    word_count = count_english_words(result)
    print(f"English words found: {word_count}")

    if word_count > 2:
        print(f"*** PROMISING RESULT ***")
        return result

    return None

def test_caesar_shifts():
    """Test all Caesar shifts (ROT1-ROT25) on gibberish"""
    print("\n" + "="*70)
    print("2. CAESAR SHIFTS (ROT1-ROT25)")
    print("="*70)

    best_ioc = 0
    best_shift = 0
    best_result = ""

    for shift in range(1, 26):
        result = caesar_decrypt(GIBBERISH, shift)
        ioc = calculate_ioc(result)
        word_count = count_english_words(result)

        if word_count > 2 or ioc > 0.06:
            print(f"  ROT{shift:2d}: IoC={ioc:.4f}, Words={word_count}, {result[:40]}...")
            if ioc > best_ioc:
                best_ioc = ioc
                best_shift = shift
                best_result = result

    if best_ioc > 0.06:
        print(f"\n*** BEST CAESAR SHIFT: ROT{best_shift} (IoC={best_ioc:.4f}) ***")
        print(f"Result: {best_result}")
        return best_result

    return None

def test_beaufort_ciphers():
    """Test Beaufort cipher with various keys"""
    print("\n" + "="*70)
    print("3. BEAUFORT CIPHER")
    print("="*70)

    keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW",
            "COORDINATES", "NORTHEAST", "WELTZEITUHR", "UNDERGROUND"]

    results = []
    for key in keys:
        try:
            result = beaufort_decrypt(GIBBERISH, key)
            ioc = calculate_ioc(result)
            word_count = count_english_words(result)

            if word_count > 2 or ioc > 0.06:
                print(f"  Key={key:15s}: IoC={ioc:.4f}, Words={word_count}, {result[:40]}...")
                results.append((key, result, ioc, word_count))
        except:
            pass

    if results:
        results.sort(key=lambda x: x[3], reverse=True)  # Sort by word count
        print(f"\n*** BEST BEAUFORT: Key={results[0][0]}, Words={results[0][3]} ***")
        print(f"Result: {results[0][1]}")
        return results[0][1]

    return None

def test_playfair_ciphers():
    """Test Playfair cipher with various keys"""
    print("\n" + "="*70)
    print("4. PLAYFAIR CIPHER")
    print("="*70)

    keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]

    results = []
    for key in keys:
        try:
            result = playfair_decrypt(GIBBERISH, key)
            ioc = calculate_ioc(result)
            word_count = count_english_words(result)

            if word_count > 2 or ioc > 0.06:
                print(f"  Key={key:15s}: IoC={ioc:.4f}, Words={word_count}, {result[:40]}...")
                results.append((key, result, ioc, word_count))
        except:
            pass

    if results:
        results.sort(key=lambda x: x[3], reverse=True)
        print(f"\n*** BEST PLAYFAIR: Key={results[0][0]}, Words={results[0][3]} ***")
        print(f"Result: {results[0][1]}")
        return results[0][1]

    return None

def test_bifid_ciphers():
    """Test Bifid cipher with various keys and periods"""
    print("\n" + "="*70)
    print("5. BIFID CIPHER")
    print("="*70)

    keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN"]

    results = []
    for key in keys:
        for period in [5, 10, 15, 20, 25, 30, 67]:
            try:
                result = bifid_decrypt(GIBBERISH, key, period)
                if len(result) > 30:
                    ioc = calculate_ioc(result)
                    word_count = count_english_words(result)

                    if word_count > 2 or ioc > 0.06:
                        print(f"  Key={key:15s}, Period={period:2d}: IoC={ioc:.4f}, Words={word_count}")
                        results.append((key, period, result, ioc, word_count))
            except:
                pass

    if results:
        results.sort(key=lambda x: x[4], reverse=True)
        print(f"\n*** BEST BIFID: Key={results[0][0]}, Period={results[0][1]}, Words={results[0][4]} ***")
        print(f"Result: {results[0][2][:60]}...")
        return results[0][2]

    return None

def test_autokey_ciphers():
    """Test Autokey with various seeds"""
    print("\n" + "="*70)
    print("6. AUTOKEY CIPHER")
    print("="*70)

    seeds = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", K1_PLAIN[:10], K2_PLAIN[:10]]

    results = []
    for seed in seeds:
        try:
            result = autokey_decrypt(GIBBERISH, seed)
            ioc = calculate_ioc(result)
            word_count = count_english_words(result)

            if word_count > 2 or ioc > 0.06:
                print(f"  Seed={seed:15s}: IoC={ioc:.4f}, Words={word_count}, {result[:40]}...")
                results.append((seed, result, ioc, word_count))
        except:
            pass

    if results:
        results.sort(key=lambda x: x[3], reverse=True)
        print(f"\n*** BEST AUTOKEY: Seed={results[0][0]}, Words={results[0][3]} ***")
        print(f"Result: {results[0][1]}")
        return results[0][1]

    return None

def test_gibberish_as_key():
    """Test using gibberish as key to decrypt K4 or other sections"""
    print("\n" + "="*70)
    print("7. GIBBERISH AS KEY FOR DECRYPTION")
    print("="*70)

    K4_FULL = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    results = []

    # Test Vigenere
    print("\nTrying Gibberish as VIGENERE key on K4...")
    result = gibberish_as_key_vigenere(K4_FULL, GIBBERISH)
    ioc = calculate_ioc(result)
    word_count = count_english_words(result)
    print(f"  Vigenere: IoC={ioc:.4f}, Words={word_count}, {result[:50]}...")
    if word_count > 5:
        results.append(("Vigenere(Gibberish)", result, ioc, word_count))

    # Test Beaufort
    print("Trying Gibberish as BEAUFORT key on K4...")
    result = gibberish_as_key_beaufort(K4_FULL, GIBBERISH)
    ioc = calculate_ioc(result)
    word_count = count_english_words(result)
    print(f"  Beaufort: IoC={ioc:.4f}, Words={word_count}, {result[:50]}...")
    if word_count > 5:
        results.append(("Beaufort(Gibberish)", result, ioc, word_count))

    # Test Autokey
    print("Trying Gibberish as AUTOKEY seed on K4...")
    result = gibberish_as_key_autokey(K4_FULL, GIBBERISH)
    ioc = calculate_ioc(result)
    word_count = count_english_words(result)
    print(f"  Autokey: IoC={ioc:.4f}, Words={word_count}, {result[:50]}...")
    if word_count > 5:
        results.append(("Autokey(Gibberish)", result, ioc, word_count))

    if results:
        results.sort(key=lambda x: x[3], reverse=True)
        print(f"\n*** BEST GIBBERISH AS KEY: {results[0][0]}, Words={results[0][3]} ***")
        print(f"Result: {results[0][1]}")
        return results[0][1]

    return None

def main():
    """Run all tests"""
    print("TESTING ALTERNATE CIPHERS ON K4 GIBBERISH SECTION")
    print(f"Gibberish: {GIBBERISH}")
    print(f"Length: {len(GIBBERISH)} characters")

    all_results = []

    # Run all tests
    r = test_atbash()
    if r: all_results.append(("Atbash", r))

    r = test_caesar_shifts()
    if r: all_results.append(("Caesar", r))

    r = test_beaufort_ciphers()
    if r: all_results.append(("Beaufort", r))

    r = test_playfair_ciphers()
    if r: all_results.append(("Playfair", r))

    r = test_bifid_ciphers()
    if r: all_results.append(("Bifid", r))

    r = test_autokey_ciphers()
    if r: all_results.append(("Autokey", r))

    r = test_gibberish_as_key()
    if r: all_results.append(("Gibberish-as-Key", r))

    # Summary
    print("\n" + "="*70)
    print("SUMMARY OF PROMISING RESULTS")
    print("="*70)

    if all_results:
        print(f"\nFound {len(all_results)} promising results:\n")
        for name, result in all_results:
            print(f"{name:20s}: {result[:70]}")
    else:
        print("\nNo highly promising results found.")
        print("Check the detailed output above for partial matches.")

if __name__ == "__main__":
    main()
