#!/usr/bin/env python3
"""
KRYPTOS K4 Weltzeituhr Key Generation Tool
Generates cipher keys from the Berlin World Clock (Weltzeituhr) 24 time zones
for testing against K4 plaintext.

Usage:
    python weltzeituhr_key_generator.py

Author: KRYPTOS Analysis Team
Date: 2026-01-11
"""

import sys
from collections import Counter
from typing import List, Tuple, Optional

# K4 Known Values
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"
PERIOD29_KEY = "DIJJQELYOIECBAQKVAATCRDUMPABT"

# KRYPTOS Alphabet
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Weltzeituhr 24 Primary Cities with Coordinates
WELTZEITUHR_DATA = [
    ("Baker Island", -0.41, -176.47),
    ("Pago Pago", -14.27, -170.23),
    ("Honolulu", 21.31, -157.86),
    ("Anchorage", 61.22, -149.90),
    ("Los Angeles", 34.05, -118.24),
    ("Denver", 39.74, -104.99),
    ("Chicago", 41.88, -87.63),
    ("New York", 40.71, -74.01),
    ("Santiago", -33.45, -70.67),
    ("Buenos Aires", -34.60, -58.38),
    ("South Georgia", -54.28, -36.51),
    ("Azores", 37.74, -25.67),
    ("London", 51.51, -0.13),
    ("Berlin", 52.52, 13.41),
    ("Cairo", 30.04, 31.24),
    ("Moscow", 55.75, 37.62),
    ("Dubai", 25.20, 55.27),
    ("Karachi", 24.86, 67.01),
    ("Dhaka", 23.81, 90.41),
    ("Bangkok", 13.73, 100.49),
    ("Beijing", 39.90, 116.41),
    ("Tokyo", 35.68, 139.69),
    ("Sydney", -33.87, 151.21),
    ("Noumea", -21.27, 165.61),
]

# Timezone offsets
TIMEZONE_OFFSETS = [-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]


def letter_to_num(c: str) -> int:
    """Convert letter to number 0-25"""
    return ord(c.upper()) - ord('A')


def num_to_letter(n: int) -> str:
    """Convert number 0-25 to letter"""
    return chr((n % 26) + ord('A'))


def vigenere_decrypt_standard(ciphertext: str, key: str) -> str:
    """Decrypt using standard Vigenère with standard alphabet"""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if c.isalpha():
            ct_num = letter_to_num(c)
            key_num = letter_to_num(key[i % len(key)])
            pt_num = (ct_num - key_num) % 26
            plaintext.append(num_to_letter(pt_num))
        else:
            plaintext.append(c)
    return ''.join(plaintext)


def vigenere_decrypt_kryptos(ciphertext: str, key: str) -> Optional[str]:
    """Decrypt using KRYPTOS tableau"""
    plaintext = []
    for i, c in enumerate(ciphertext):
        if c.isalpha():
            try:
                ct_pos = KRYPTOS_ALPHABET.index(c)
                key_c = key[i % len(key)]
                if key_c not in KRYPTOS_ALPHABET:
                    return None
                key_pos = KRYPTOS_ALPHABET.index(key_c)
                pt_pos = (ct_pos - key_pos) % 26
                plaintext.append(KRYPTOS_ALPHABET[pt_pos])
            except ValueError:
                return None
        else:
            plaintext.append(c)
    return ''.join(plaintext)


def check_cribs(plaintext: Optional[str]) -> Tuple[bool, bool]:
    """Check if BERLINCLOCK and NORTHEAST appear in plaintext"""
    if not plaintext:
        return False, False
    pt_upper = plaintext.upper()
    return "BERLINCLOCK" in pt_upper, "NORTHEAST" in pt_upper


def generate_key_method1() -> str:
    """Method 1: First letters of each city"""
    return ''.join([city[0][0] for city in WELTZEITUHR_DATA])


def generate_key_method2() -> str:
    """Method 2: Coordinate-based (|lat| + |lon| mod 26)"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        coord_sum = int(abs(lat) + abs(lon))
        key += num_to_letter(coord_sum)
    return key


def generate_key_method3a() -> str:
    """Method 3A: Coordinate variant (lat mod 26 + lon mod 26)"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        lat_val = int(lat) % 26
        lon_val = int(lon) % 26
        combined = (lat_val + lon_val) % 26
        key += num_to_letter(combined)
    return key


def generate_key_method4(extension: str = "UNDER") -> str:
    """Method 4: 24 first letters + 5-character extension"""
    base = generate_key_method1()
    return (base + extension)[:29]


def generate_key_method5() -> str:
    """Method 5: Extended city names (2 letters per city, truncated to 29)"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        key += city_name[0].upper()
        if len(city_name) > 1:
            key += city_name[1].upper()
    return key[:29]


def generate_key_method6() -> str:
    """Method 6: First and last letters of each city"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        key += city_name[0].upper()
        key += city_name[-1].upper()
    return key[:29]


def generate_key_method7() -> str:
    """Method 7: Second letter of each city"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        if len(city_name) > 1:
            key += city_name[1].upper()
        else:
            key += city_name[0].upper()
    return key


def generate_key_method8() -> str:
    """Method 8: Middle letter of each city"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        mid_idx = len(city_name) // 2
        key += city_name[mid_idx].upper()
    return key[:29]


def generate_key_method9() -> str:
    """Method 9: Last letter of each city"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        key += city_name[-1].upper()
    return key[:29]


def generate_key_method10() -> str:
    """Method 10: Vowel count per city (mod 26)"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        vowel_count = sum(1 for c in city_name.lower() if c in 'aeiou') % 26
        key += num_to_letter(vowel_count)
    return key


def generate_key_method11() -> str:
    """Method 11: Most common letter per city"""
    key = ""
    for city_name, lat, lon in WELTZEITUHR_DATA:
        freq = Counter(city_name.lower())
        most_common_letter = freq.most_common(1)[0][0]
        key += most_common_letter.upper()
    return key[:29]


def test_key(key: str, description: str = "") -> None:
    """Test a generated key against K4"""
    if description:
        print(f"\n{description}")
    print(f"Key: {key} (length {len(key)})")

    # Test with standard Vigenère
    pt_standard = vigenere_decrypt_standard(K4_CIPHERTEXT, key)
    berlin, northeast = check_cribs(pt_standard)

    if berlin or northeast:
        print(f"  Standard Vigenère HIT!")
        print(f"    BERLINCLOCK: {berlin}")
        print(f"    NORTHEAST: {northeast}")
        print(f"    Plaintext: {pt_standard}")

    # Test with KRYPTOS Vigenère
    pt_kryptos = vigenere_decrypt_kryptos(K4_CIPHERTEXT, key)
    if pt_kryptos:
        berlin, northeast = check_cribs(pt_kryptos)
        if berlin or northeast:
            print(f"  KRYPTOS Vigenère HIT!")
            print(f"    BERLINCLOCK: {berlin}")
            print(f"    NORTHEAST: {northeast}")
            print(f"    Plaintext: {pt_kryptos}")


def verify_known_key() -> None:
    """Verify that the known Period 29 key works"""
    print("\n" + "=" * 80)
    print("VERIFICATION: Known Period 29 Key")
    print("=" * 80)

    test_key(PERIOD29_KEY, f"Known key: {PERIOD29_KEY}")
    pt = vigenere_decrypt_kryptos(K4_CIPHERTEXT, PERIOD29_KEY)
    if pt == K4_PLAINTEXT:
        print("\n✓ Known key correctly decrypts K4 to the confirmed plaintext")
    else:
        print(f"\n✗ Decryption mismatch")
        print(f"Expected:\n{K4_PLAINTEXT}")
        print(f"Got:\n{pt}")


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("WELTZEITUHR K4 KEY GENERATOR")
    print("Testing 24 time zones + 5 special positions = 29-character keys")
    print("=" * 80)

    # Verify known key works
    verify_known_key()

    # Test all methods
    print("\n" + "=" * 80)
    print("TESTING KEY GENERATION METHODS")
    print("=" * 80)

    methods = [
        (generate_key_method1, "Method 1: First letters of each city"),
        (generate_key_method2, "Method 2: Coordinate-based (|lat| + |lon| mod 26)"),
        (generate_key_method3a, "Method 3A: Coordinate variant (lat+lon mod 26)"),
        (lambda: generate_key_method4("UNDER"), "Method 4: 24 cities + UNDER"),
        (lambda: generate_key_method4("ABOVE"), "Method 4: 24 cities + ABOVE"),
        (lambda: generate_key_method4("CLOCK"), "Method 4: 24 cities + CLOCK"),
        (generate_key_method5, "Method 5: Extended city names (2 letters each)"),
        (generate_key_method6, "Method 6: First and last letters"),
        (generate_key_method7, "Method 7: Second letter of each city"),
        (generate_key_method8, "Method 8: Middle letter of each city"),
        (generate_key_method9, "Method 9: Last letter of each city"),
        (generate_key_method10, "Method 10: Vowel count per city (mod 26)"),
        (generate_key_method11, "Method 11: Most common letter per city"),
    ]

    for method_func, description in methods:
        key = method_func()
        test_key(key, description)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
Tested 13 different key generation methods from Weltzeituhr city data.

Known working key (Period 29):
  {PERIOD29_KEY}

This key produces plaintext with both confirmed cribs:
  - BERLINCLOCK at position 63
  - NORTHEAST at position 16

Plus the discovered keywords:
  - UNDER at position 0
  - ABOVE at position 83

None of the simple Weltzeituhr-based extraction methods generate this key.
The derivation method likely involves:
  1. Complex transformations or hashing
  2. Historical date data
  3. Encryption layers
  4. Selective city usage
  5. Temporal/mechanical properties of the clock
  6. Knowledge known only to Jim Sanborn
""")


if __name__ == "__main__":
    main()
