#!/usr/bin/env python3
"""
Test the Weltzeituhr (World Time Clock) as a running key source for K4 decryption.

Based on Ryan Bonifacino's papers proposing K4 uses a running key derived from
the Berlin Weltzeituhr at Alexanderplatz. Sanborn confirmed "BERLINCLOCK" refers
to the Weltzeituhr.

Tests multiple key derivation methods and cipher types.
"""

import itertools
import sys

# ─── Constants ───────────────────────────────────────────────────────────────

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4_CIPHER)  # 97

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known plaintext cribs and their confirmed positions
CRIBS = {
    "BERLINCLOCK": 63,
    "EASTNORTHEAST": 21,
}

# Weltzeituhr city panels (1969 GDR version, clockwise from top)
WELTZEITUHR_CITIES = [
    "ACCRA", "ADDISABEBA", "ALGIER", "ANKARA", "ATHEN", "BAGDAD",
    "BANGKOK", "BERLIN", "BRAZZAVILLE", "BUDAPEST", "BUKAREST", "DAMASKUS",
    "DARESSALAM", "DELHI", "DJAKARTA", "DUBAI", "HANOI", "HAVANNA",
    "HELSINKI", "HONOLULU", "ISLAMABAD", "KABUL", "KAIRO", "KAMPALA",
    "KARATSCHI", "KIEW", "KOPENHAGEN", "KUALALUMPUR", "LAGOS", "LIMA",
    "LISSABON", "LONDON", "LUANDA", "MADRID", "MANAGUA", "MAPUTO",
    "MEXIKO", "MOGADISCHU", "MONROVIA", "MONTEVIDEO", "MOSKAU", "NAIROBI",
    "NOWOSIBIRSK", "NUUK", "OSLO", "OTTAWA", "PARIS", "PEKING",
    "PJOENGJANG", "PRAG", "PRETORIA", "RABAT", "REYKJAVIK", "RIO",
    "ROM", "SANTIAGODECHILE", "SOFIA", "STOCKHOLM", "TEHERAN", "TOKIO",
    "TRIPOLIS", "ULAANBAATAR", "WARSCHAU", "WASHINGTON", "WIEN", "WLADIWOSTOK",
]

# UTC offsets for the cities (approximate, using standard time)
CITY_UTC_OFFSETS = {
    "ACCRA": 0, "ADDISABEBA": 3, "ALGIER": 1, "ANKARA": 3, "ATHEN": 2,
    "BAGDAD": 3, "BANGKOK": 7, "BERLIN": 1, "BRAZZAVILLE": 1, "BUDAPEST": 1,
    "BUKAREST": 2, "DAMASKUS": 2, "DARESSALAM": 3, "DELHI": 5,  # 5:30
    "DJAKARTA": 7, "DUBAI": 4, "HANOI": 7, "HAVANNA": -5, "HELSINKI": 2,
    "HONOLULU": -10, "ISLAMABAD": 5, "KABUL": 4,  # 4:30
    "KAIRO": 2, "KAMPALA": 3, "KARATSCHI": 5, "KIEW": 2, "KOPENHAGEN": 1,
    "KUALALUMPUR": 8, "LAGOS": 1, "LIMA": -5, "LISSABON": 0, "LONDON": 0,
    "LUANDA": 1, "MADRID": 1, "MANAGUA": -6, "MAPUTO": 2, "MEXIKO": -6,
    "MOGADISCHU": 3, "MONROVIA": 0, "MONTEVIDEO": -3, "MOSKAU": 3,
    "NAIROBI": 3, "NOWOSIBIRSK": 7, "NUUK": -3, "OSLO": 1, "OTTAWA": -5,
    "PARIS": 1, "PEKING": 8, "PJOENGJANG": 9, "PRAG": 1, "PRETORIA": 2,
    "RABAT": 0, "REYKJAVIK": 0, "RIO": -3, "ROM": 1, "SANTIAGODECHILE": -4,
    "SOFIA": 2, "STOCKHOLM": 1, "TEHERAN": 3,  # 3:30
    "TOKIO": 9, "TRIPOLIS": 2, "ULAANBAATAR": 8, "WARSCHAU": 1,
    "WASHINGTON": -5, "WIEN": 1, "WLADIWOSTOK": 10,
}

# Cities changed/updated during 1997 renovation
# Original 1969 names -> 1997 updated names (some speculative)
RENOVATION_CHANGES = {
    "DJAKARTA": "JAKARTA",
    "PEKING": "BEIJING",
    "KIEW": "KYIV",
    "PJOENGJANG": "PYONGYANG",
    "KAIRO": "CAIRO",
    "NOWOSIBIRSK": "NOVOSIBIRSK",
    "MOGADISCHU": "MOGADISHU",
    "KARATSCHI": "KARACHI",
    "LISSABON": "LISBON",
    "BUKAREST": "BUCHAREST",
    "WARSCHAU": "WARSAW",
    "MOSKAU": "MOSCOW",
    "ROM": "ROME",
    "WIEN": "VIENNA",
    "ATHEN": "ATHENS",
    "KOPENHAGEN": "COPENHAGEN",
    "DAMASKUS": "DAMASCUS",
    "DARESSALAM": "DARESSALAAM",
    "ALGIER": "ALGIERS",
    "ADDISABEBA": "ADDISABABA",
}

# Additional keywords
SPECIAL_KEYWORDS = [
    "BERLINDERWELTZEITUHR",
    "ALEXANDERPLATZ",
    "WELTZEITUHR",
    "WORLDTIMECLOCK",
    "BERLINCLOCK",
    "BERLINWELTZEITUHR",
    "DIEWELTZEITUHR",
    "URANIA",  # Urania-Weltzeituhr is its full name
    "URANIAWELTZEITUHR",
    "ERICHFRIEDRICH",  # architect
    "ERICHFRIEDRICHJOHN",
    "HANSJOACHIMKUNSCH",  # co-designer
]

# ─── Load dictionary ────────────────────────────────────────────────────────

def load_dictionary(path="/home/user/polyalphabetic/OxfordEnglishWords.txt"):
    """Load word list, filter to words >= 4 chars, uppercase."""
    words = set()
    try:
        with open(path, "r") as f:
            for line in f:
                w = line.strip().upper()
                if len(w) >= 4 and w.isalpha():
                    words.add(w)
    except FileNotFoundError:
        print(f"WARNING: Dictionary not found at {path}")
    return words


# ─── Cipher helper functions ────────────────────────────────────────────────

def char_to_idx(c, alphabet):
    """Convert character to index in given alphabet."""
    try:
        return alphabet.index(c)
    except ValueError:
        return -1


def idx_to_char(i, alphabet):
    """Convert index to character in given alphabet."""
    return alphabet[i % len(alphabet)]


def vigenere_decrypt(ciphertext, key, ct_alpha, pt_alpha):
    """
    Vigenère decryption: P = (C - K) mod n
    ct_alpha: alphabet used for ciphertext indexing
    pt_alpha: alphabet used for plaintext output
    """
    n = len(ct_alpha)
    assert len(pt_alpha) == n, f"Alphabet length mismatch: {len(ct_alpha)} vs {len(pt_alpha)}"
    result = []
    ki = 0
    for c in ciphertext:
        ci = char_to_idx(c, ct_alpha)
        if ci == -1:
            result.append(c)
            continue
        k_char = key[ki % len(key)]
        k_idx = char_to_idx(k_char, ct_alpha)
        if k_idx == -1:
            # Try standard alpha for key
            k_idx = char_to_idx(k_char, STANDARD_ALPHA)
            if k_idx == -1:
                ki += 1
                result.append('?')
                continue
        pi = (ci - k_idx) % n
        result.append(idx_to_char(pi, pt_alpha))
        ki += 1
    return "".join(result)


def beaufort_decrypt(ciphertext, key, alphabet):
    """Beaufort cipher: P = (K - C) mod n"""
    n = len(alphabet)
    result = []
    ki = 0
    for c in ciphertext:
        ci = char_to_idx(c, alphabet)
        if ci == -1:
            result.append(c)
            continue
        k_char = key[ki % len(key)]
        k_idx = char_to_idx(k_char, alphabet)
        if k_idx == -1:
            k_idx = char_to_idx(k_char, STANDARD_ALPHA)
            if k_idx == -1:
                ki += 1
                result.append('?')
                continue
        pi = (k_idx - ci) % n
        result.append(idx_to_char(pi, alphabet))
        ki += 1
    return "".join(result)


def vigenere_decrypt_numeric(ciphertext, key_numbers, alphabet):
    """Vigenère decryption with numeric key values."""
    n = len(alphabet)
    result = []
    ki = 0
    for c in ciphertext:
        ci = char_to_idx(c, alphabet)
        if ci == -1:
            result.append(c)
            continue
        shift = key_numbers[ki % len(key_numbers)]
        pi = (ci - shift) % n
        result.append(idx_to_char(pi, alphabet))
        ki += 1
    return "".join(result)


def autokey_decrypt(ciphertext, primer, alphabet):
    """Autokey Vigenère: key = primer + plaintext so far."""
    n = len(alphabet)
    key_stream = list(primer)
    result = []
    for i, c in enumerate(ciphertext):
        ci = char_to_idx(c, alphabet)
        if ci == -1:
            result.append(c)
            continue
        if i < len(key_stream):
            k_idx = char_to_idx(key_stream[i], alphabet)
        else:
            # Use previous plaintext
            k_idx = char_to_idx(result[i - len(primer)], alphabet)
        if k_idx == -1:
            result.append('?')
            continue
        pi = (ci - k_idx) % n
        pt_char = idx_to_char(pi, alphabet)
        result.append(pt_char)
        key_stream.append(pt_char)
    return "".join(result)


# ─── Scoring ─────────────────────────────────────────────────────────────────

def score_plaintext(plaintext, dictionary):
    """Score by counting characters covered by dictionary words found in text."""
    text = plaintext.upper()
    covered = [False] * len(text)
    words_found = []

    # Check for known cribs first
    crib_hits = 0
    for crib, pos in CRIBS.items():
        if pos < len(text) and text[pos:pos+len(crib)] == crib:
            crib_hits += 1
            for i in range(pos, min(pos + len(crib), len(text))):
                covered[i] = True
            words_found.append(f"{crib}@{pos}")

    # Search for dictionary words (length >= 4)
    sorted_words = sorted(dictionary, key=len, reverse=True)
    for word in sorted_words:
        wlen = len(word)
        if wlen < 4:
            continue
        idx = 0
        while True:
            pos = text.find(word, idx)
            if pos == -1:
                break
            # Only count if not fully covered already
            new_coverage = sum(1 for i in range(pos, pos + wlen) if not covered[i])
            if new_coverage > 0:
                for i in range(pos, pos + wlen):
                    covered[i] = True
                words_found.append(f"{word}@{pos}")
            idx = pos + 1

    total_covered = sum(covered)
    # Big bonus for crib hits
    score = total_covered + crib_hits * 200
    return score, total_covered, crib_hits, words_found


def check_cribs(plaintext):
    """Check if known cribs appear at correct positions."""
    hits = {}
    for crib, pos in CRIBS.items():
        if pos + len(crib) <= len(plaintext):
            actual = plaintext[pos:pos+len(crib)]
            if actual == crib:
                hits[crib] = pos
    return hits


# ─── Key generation methods ──────────────────────────────────────────────────

def generate_keys():
    """Generate all candidate running keys from Weltzeituhr data."""
    keys = {}

    # 1. Concatenated city names (original order)
    concat_orig = "".join(WELTZEITUHR_CITIES)
    keys["cities_concat_original"] = concat_orig

    # 2. First letters of each city
    first_letters = "".join(c[0] for c in WELTZEITUHR_CITIES)
    keys["cities_first_letters"] = first_letters

    # 3. Alphabetical order
    alpha_sorted = sorted(WELTZEITUHR_CITIES)
    keys["cities_concat_alphabetical"] = "".join(alpha_sorted)
    keys["cities_firstletters_alphabetical"] = "".join(c[0] for c in alpha_sorted)

    # 4. Reverse order
    keys["cities_concat_reverse"] = "".join(reversed(WELTZEITUHR_CITIES))
    keys["cities_firstletters_reverse"] = "".join(c[0] for c in reversed(WELTZEITUHR_CITIES))

    # 5. By timezone (sorted by UTC offset)
    tz_sorted = sorted(WELTZEITUHR_CITIES, key=lambda c: CITY_UTC_OFFSETS.get(c, 0))
    keys["cities_concat_by_timezone"] = "".join(tz_sorted)
    keys["cities_firstletters_by_timezone"] = "".join(c[0] for c in tz_sorted)

    # 6. Reverse timezone
    tz_rev = list(reversed(tz_sorted))
    keys["cities_concat_by_timezone_rev"] = "".join(tz_rev)

    # 7. Renovation-changed names (English versions)
    changed_cities = []
    for city in WELTZEITUHR_CITIES:
        if city in RENOVATION_CHANGES:
            changed_cities.append(RENOVATION_CHANGES[city])
        else:
            changed_cities.append(city)
    keys["cities_concat_1997_updated"] = "".join(changed_cities)
    keys["cities_firstletters_1997"] = "".join(c[0] for c in changed_cities)

    # 8. Only the changed city names (differences between 1969 and 1997)
    changed_only_old = "".join(k for k in RENOVATION_CHANGES.keys())
    changed_only_new = "".join(v for v in RENOVATION_CHANGES.values())
    keys["changed_cities_1969_names"] = changed_only_old
    keys["changed_cities_1997_names"] = changed_only_new

    # 9. Special keywords
    for kw in SPECIAL_KEYWORDS:
        keys[f"keyword_{kw}"] = kw

    # 10. Berlin-specific combinations
    keys["BERLIN_repeated"] = "BERLIN" * 20
    keys["BERLINCLOCK_repeated"] = "BERLINCLOCK" * 10

    # 11. City names containing specific letters/patterns
    # Cities starting with each letter of KRYPTOS
    kryptos_cities = []
    for ch in "KRYPTOS":
        for city in WELTZEITUHR_CITIES:
            if city[0] == ch:
                kryptos_cities.append(city)
                break
    if kryptos_cities:
        keys["cities_starting_KRYPTOS"] = "".join(kryptos_cities)

    # 12. Every Nth city (for period patterns)
    for step in [2, 3, 4, 6, 8, 12]:
        selected = [WELTZEITUHR_CITIES[i] for i in range(0, len(WELTZEITUHR_CITIES), step)]
        keys[f"cities_every_{step}th"] = "".join(selected)

    # 13. Panel position numbers as letters (A=1, B=2, etc.)
    # 24 panels, map 1-24 to A-X
    panel_letters = "".join(chr(64 + i) for i in range(1, 25))  # A through X
    keys["panel_positions_as_letters"] = panel_letters

    # 14. City name lengths as key numbers
    keys["_numeric_city_name_lengths"] = [len(c) for c in WELTZEITUHR_CITIES]

    # 15. 24 cities + 5 markers = 29 (period hypothesis)
    # Try padding with special words to reach period 29
    extra5_options = [
        "NORTH",  # compass directions
        "SOUTH",
        "EAST_",  # placeholder
        "WESTN",
        "CLOCK",
    ]
    for extra_word in ["CLOCK", "NORTH", "SOUTH", "UHRZE", "PLATZ"]:
        padded = first_letters + extra_word
        keys[f"firstletters_plus_{extra_word}"] = padded

    # 16. Interleave city first-letters with offset digits
    interleaved = ""
    for city in WELTZEITUHR_CITIES:
        offset = CITY_UTC_OFFSETS.get(city, 0)
        interleaved += city[0]
        interleaved += chr(65 + (offset % 26))
    keys["interleaved_city_offset"] = interleaved

    # 17. UTC offsets grouped by hour (0-23 corresponding to panels)
    # Each of 24 hours, which city appears
    hour_key = ""
    for h in range(24):
        for city in WELTZEITUHR_CITIES:
            if CITY_UTC_OFFSETS.get(city, 0) % 24 == h:
                hour_key += city[0]
                break
        else:
            hour_key += "A"  # filler
    keys["hourly_first_city_letter"] = hour_key

    # 18. Concatenated with BERLIN at start
    keys["BERLIN_then_cities"] = "BERLIN" + concat_orig
    keys["WELTZEITUHR_then_cities"] = "WELTZEITUHR" + concat_orig

    # 19. Cities that were on the ORIGINAL 1969 clock only
    # (same list but emphasizing it's the DDR/GDR version)
    keys["cities_concat_ddr"] = concat_orig  # same, but test with different offsets

    # 20. Double the first letters for period 29+ coverage
    keys["firstletters_doubled"] = first_letters * 2

    # 21. City names cycling to exactly 97 chars (K4 length)
    cycling_key = (concat_orig * 3)[:K4_LEN]
    keys["cities_cycling_97"] = cycling_key

    # 22. Reversed individual city names, concatenated
    keys["cities_reversed_names"] = "".join(c[::-1] for c in WELTZEITUHR_CITIES)

    # 23. Only consonants from city names
    vowels = set("AEIOU")
    keys["cities_consonants_only"] = "".join(
        "".join(ch for ch in city if ch not in vowels) for city in WELTZEITUHR_CITIES
    )

    # 24. Only vowels from city names
    keys["cities_vowels_only"] = "".join(
        "".join(ch for ch in city if ch in vowels) for city in WELTZEITUHR_CITIES
    )

    # 25. BERLIN panel and its neighbors (panels 7,8,9 in 0-indexed -> BANGKOK, BERLIN, BRAZZAVILLE)
    keys["berlin_neighbors"] = "BANGKOKBERLINBRAZZAVILLE"

    # 26. First two letters of each city
    keys["cities_first_two_letters"] = "".join(c[:2] for c in WELTZEITUHR_CITIES)

    # 27. Last letters of each city
    keys["cities_last_letters"] = "".join(c[-1] for c in WELTZEITUHR_CITIES)

    return keys


def generate_numeric_keys():
    """Generate numeric key sequences from Weltzeituhr data."""
    numeric_keys = {}

    # UTC offsets directly
    offsets = [CITY_UTC_OFFSETS.get(c, 0) for c in WELTZEITUHR_CITIES]
    numeric_keys["utc_offsets_direct"] = offsets

    # UTC offsets mod 26
    numeric_keys["utc_offsets_mod26"] = [(o % 26) for o in offsets]

    # Absolute UTC offsets
    numeric_keys["utc_offsets_absolute"] = [abs(o) for o in offsets]

    # UTC offsets + 12 (to make all positive)
    numeric_keys["utc_offsets_plus12"] = [(o + 12) for o in offsets]

    # City name lengths
    numeric_keys["city_name_lengths"] = [len(c) for c in WELTZEITUHR_CITIES]

    # Panel numbers 0-23 repeated
    numeric_keys["panel_numbers_0_23"] = list(range(24))

    # Panel numbers 1-24
    numeric_keys["panel_numbers_1_24"] = list(range(1, 25))

    # Differences between consecutive UTC offsets
    diffs = [offsets[i+1] - offsets[i] for i in range(len(offsets)-1)]
    numeric_keys["utc_offset_differences"] = diffs

    # Hours on a 24-hour clock (0-23) mapped to timezone offsets
    # Sorted UTC offsets
    sorted_offsets = sorted(set(offsets))
    numeric_keys["sorted_unique_offsets"] = sorted_offsets

    # Number of cities per timezone
    tz_counts = {}
    for o in offsets:
        tz_counts[o] = tz_counts.get(o, 0) + 1
    count_sequence = [tz_counts.get(o, 0) for o in offsets]
    numeric_keys["cities_per_timezone"] = count_sequence

    return numeric_keys


# ─── Main test runner ────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("WELTZEITUHR RUNNING KEY TEST FOR K4 DECRYPTION")
    print("=" * 80)
    print(f"\nK4 ciphertext ({K4_LEN} chars): {K4_CIPHER}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Standard alphabet: {STANDARD_ALPHA}")
    print(f"\nKnown cribs:")
    for crib, pos in CRIBS.items():
        print(f"  {crib} at position {pos}")
    print(f"\nWeltzeituhr cities: {len(WELTZEITUHR_CITIES)}")
    print(f"Concatenated length: {len(''.join(WELTZEITUHR_CITIES))}")

    # Load dictionary
    dictionary = load_dictionary()
    print(f"Dictionary loaded: {len(dictionary)} words (4+ chars)")

    # Generate keys
    text_keys = generate_keys()
    numeric_keys = generate_numeric_keys()

    print(f"\nText keys to test: {len(text_keys)}")
    print(f"Numeric keys to test: {len(numeric_keys)}")

    results = []
    test_count = 0

    # ─── Test text keys ──────────────────────────────────────────────────

    print("\n" + "─" * 80)
    print("TESTING TEXT-BASED KEYS")
    print("─" * 80)

    for key_name, key_text in text_keys.items():
        if key_name.startswith("_numeric_"):
            continue  # Skip numeric entries stored here

        key_upper = key_text.upper()
        # Filter to only alphabetic characters
        key_alpha = "".join(c for c in key_upper if c.isalpha())

        if not key_alpha:
            continue

        # Ensure key is long enough (at least K4_LEN or will cycle)
        key_for_use = key_alpha
        if len(key_for_use) < K4_LEN:
            # Repeat to cover
            repeats = (K4_LEN // len(key_for_use)) + 1
            key_for_use = (key_for_use * repeats)[:K4_LEN]

        # Test with multiple cipher types and alphabets
        configs = [
            ("Vigenere_Std", lambda ct, k: vigenere_decrypt(ct, k, STANDARD_ALPHA, STANDARD_ALPHA)),
            ("Vigenere_Kryptos", lambda ct, k: vigenere_decrypt(ct, k, KRYPTOS_ALPHA, KRYPTOS_ALPHA)),
            ("Vigenere_KtoS", lambda ct, k: vigenere_decrypt(ct, k, KRYPTOS_ALPHA, STANDARD_ALPHA)),
            ("Vigenere_StoK", lambda ct, k: vigenere_decrypt(ct, k, STANDARD_ALPHA, KRYPTOS_ALPHA)),
            ("Beaufort_Std", lambda ct, k: beaufort_decrypt(ct, k, STANDARD_ALPHA)),
            ("Beaufort_Kryptos", lambda ct, k: beaufort_decrypt(ct, k, KRYPTOS_ALPHA)),
        ]

        # Also test autokey for short keys (primers)
        if len(key_alpha) <= 30:
            configs.extend([
                ("Autokey_Std", lambda ct, k: autokey_decrypt(ct, k, STANDARD_ALPHA)),
                ("Autokey_Kryptos", lambda ct, k: autokey_decrypt(ct, k, KRYPTOS_ALPHA)),
            ])

        for cipher_name, decrypt_fn in configs:
            test_count += 1
            try:
                plaintext = decrypt_fn(K4_CIPHER, key_for_use)
            except Exception as e:
                continue

            # Check cribs
            crib_hits = check_cribs(plaintext)

            # Score
            score, covered, n_cribs, words = score_plaintext(plaintext, dictionary)

            result_entry = {
                "key_name": key_name,
                "cipher": cipher_name,
                "plaintext": plaintext,
                "score": score,
                "covered": covered,
                "crib_hits": crib_hits,
                "words": words,
                "key_preview": key_alpha[:50],
            }

            results.append(result_entry)

            # Print immediately if cribs match
            if crib_hits:
                print(f"\n*** CRIB HIT *** {key_name} / {cipher_name}")
                print(f"  Plaintext: {plaintext}")
                print(f"  Crib hits: {crib_hits}")
                print(f"  Key: {key_alpha[:80]}...")

        # Also test with different starting offsets (0-10)
        for offset in range(1, min(11, len(key_alpha))):
            shifted_key = key_alpha[offset:] + key_alpha[:offset]
            if len(shifted_key) < K4_LEN:
                repeats = (K4_LEN // len(shifted_key)) + 1
                shifted_key = (shifted_key * repeats)[:K4_LEN]

            for cipher_name_base, decrypt_fn in [
                ("Vigenere_Std", lambda ct, k: vigenere_decrypt(ct, k, STANDARD_ALPHA, STANDARD_ALPHA)),
                ("Vigenere_Kryptos", lambda ct, k: vigenere_decrypt(ct, k, KRYPTOS_ALPHA, KRYPTOS_ALPHA)),
                ("Beaufort_Std", lambda ct, k: beaufort_decrypt(ct, k, STANDARD_ALPHA)),
            ]:
                test_count += 1
                try:
                    plaintext = decrypt_fn(K4_CIPHER, shifted_key)
                except Exception:
                    continue

                crib_hits = check_cribs(plaintext)
                score, covered, n_cribs, words = score_plaintext(plaintext, dictionary)

                result_entry = {
                    "key_name": f"{key_name}_offset{offset}",
                    "cipher": cipher_name_base,
                    "plaintext": plaintext,
                    "score": score,
                    "covered": covered,
                    "crib_hits": crib_hits,
                    "words": words,
                    "key_preview": shifted_key[:50],
                }
                results.append(result_entry)

                if crib_hits:
                    print(f"\n*** CRIB HIT *** {key_name}_offset{offset} / {cipher_name_base}")
                    print(f"  Plaintext: {plaintext}")
                    print(f"  Crib hits: {crib_hits}")

    # ─── Test numeric keys ───────────────────────────────────────────────

    print("\n" + "─" * 80)
    print("TESTING NUMERIC KEYS (UTC offsets, panel numbers, etc.)")
    print("─" * 80)

    for key_name, key_nums in numeric_keys.items():
        if not key_nums:
            continue

        for alpha_name, alpha in [("Std", STANDARD_ALPHA), ("Kryptos", KRYPTOS_ALPHA)]:
            test_count += 1
            try:
                plaintext = vigenere_decrypt_numeric(K4_CIPHER, key_nums, alpha)
            except Exception:
                continue

            crib_hits = check_cribs(plaintext)
            score, covered, n_cribs, words = score_plaintext(plaintext, dictionary)

            result_entry = {
                "key_name": f"numeric_{key_name}",
                "cipher": f"Vigenere_{alpha_name}",
                "plaintext": plaintext,
                "score": score,
                "covered": covered,
                "crib_hits": crib_hits,
                "words": words,
                "key_preview": str(key_nums[:20]),
            }
            results.append(result_entry)

            if crib_hits:
                print(f"\n*** CRIB HIT *** numeric_{key_name} / Vigenere_{alpha_name}")
                print(f"  Plaintext: {plaintext}")
                print(f"  Crib hits: {crib_hits}")
                print(f"  Key: {key_nums}")

    # ─── Test 24+5=29 period hypothesis ──────────────────────────────────

    print("\n" + "─" * 80)
    print("TESTING 24+5=29 PERIOD HYPOTHESIS")
    print("─" * 80)

    # 24 city first letters = 24 chars. Need 5 more for period 29.
    first_24 = "".join(c[0] for c in WELTZEITUHR_CITIES[:24])
    # But we have 66 cities total (some clocks show more). Use first 24.
    # Actually, the clock has 24 panels with multiple cities each.
    # Let's try different padding strategies

    padding_options = [
        ("ABCDE", "sequential_letters"),
        ("CLOCK", "CLOCK"),
        ("ZEITU", "ZEITU_from_Weltzeituhr"),
        ("NORTH", "NORTH"),
        ("PLATZ", "PLATZ_Alexanderplatz"),
        ("UHREN", "UHREN_clocks"),
        ("JAMES", "JAMES_Sanborn"),
        ("WORLD", "WORLD"),
        ("KRYPT", "KRYPT"),
        ("BRLNC", "BERLINCLOCK_consonants"),
    ]

    for padding, pad_name in padding_options:
        # 24 first letters + 5 padding = period 29 key
        key29 = first_24 + padding

        for cipher_name, decrypt_fn in [
            ("Vigenere_Std", lambda ct, k: vigenere_decrypt(ct, k, STANDARD_ALPHA, STANDARD_ALPHA)),
            ("Vigenere_Kryptos", lambda ct, k: vigenere_decrypt(ct, k, KRYPTOS_ALPHA, KRYPTOS_ALPHA)),
            ("Beaufort_Std", lambda ct, k: beaufort_decrypt(ct, k, STANDARD_ALPHA)),
        ]:
            test_count += 1
            # Repeat to cover K4_LEN
            key_repeated = (key29 * 4)[:K4_LEN]
            try:
                plaintext = decrypt_fn(K4_CIPHER, key_repeated)
            except Exception:
                continue

            crib_hits = check_cribs(plaintext)
            score, covered, n_cribs, words = score_plaintext(plaintext, dictionary)

            result_entry = {
                "key_name": f"period29_{pad_name}",
                "cipher": cipher_name,
                "plaintext": plaintext,
                "score": score,
                "covered": covered,
                "crib_hits": crib_hits,
                "words": words,
                "key_preview": key29,
            }
            results.append(result_entry)

            if crib_hits:
                print(f"\n*** CRIB HIT *** period29_{pad_name} / {cipher_name}")
                print(f"  Plaintext: {plaintext}")
                print(f"  Crib hits: {crib_hits}")

    # ─── Test using BERLINCLOCK/EASTNORTHEAST as partial known plaintext ──

    print("\n" + "─" * 80)
    print("REVERSE-ENGINEERING KEY FROM KNOWN PLAINTEXT POSITIONS")
    print("─" * 80)

    # If we know plaintext at positions 63-73 is BERLINCLOCK and 21-33 is EASTNORTHEAST,
    # we can derive the key at those positions and see if it matches any city pattern.

    for alpha_name, alpha in [("Standard", STANDARD_ALPHA), ("Kryptos", KRYPTOS_ALPHA)]:
        n = len(alpha)
        print(f"\n  Using {alpha_name} alphabet:")

        # Derive key for BERLINCLOCK at position 63
        derived_key_bc = []
        crib = "BERLINCLOCK"
        for i, (c_char, p_char) in enumerate(zip(K4_CIPHER[63:63+len(crib)], crib)):
            ci = char_to_idx(c_char, alpha)
            pi = char_to_idx(p_char, alpha)
            if ci != -1 and pi != -1:
                ki = (ci - pi) % n
                derived_key_bc.append((63+i, idx_to_char(ki, alpha), ki))
            else:
                derived_key_bc.append((63+i, '?', -1))

        print(f"  Key for BERLINCLOCK@63: ", end="")
        print("".join(k[1] for k in derived_key_bc))
        print(f"  Key positions 63-73:    ", end="")
        print(" ".join(f"{k[2]:2d}" for k in derived_key_bc))

        # Derive key for EASTNORTHEAST at position 21
        derived_key_ene = []
        crib2 = "EASTNORTHEAST"
        for i, (c_char, p_char) in enumerate(zip(K4_CIPHER[21:21+len(crib2)], crib2)):
            ci = char_to_idx(c_char, alpha)
            pi = char_to_idx(p_char, alpha)
            if ci != -1 and pi != -1:
                ki = (ci - pi) % n
                derived_key_ene.append((21+i, idx_to_char(ki, alpha), ki))
            else:
                derived_key_ene.append((21+i, '?', -1))

        print(f"  Key for EASTNORTHEAST@21: ", end="")
        print("".join(k[1] for k in derived_key_ene))
        print(f"  Key positions 21-33:      ", end="")
        print(" ".join(f"{k[2]:2d}" for k in derived_key_ene))

        # Beaufort: K = C + P mod n
        print(f"\n  Beaufort key derivation ({alpha_name}):")
        derived_beau_bc = []
        for i, (c_char, p_char) in enumerate(zip(K4_CIPHER[63:63+len(crib)], crib)):
            ci = char_to_idx(c_char, alpha)
            pi = char_to_idx(p_char, alpha)
            if ci != -1 and pi != -1:
                ki = (ci + pi) % n
                derived_beau_bc.append((63+i, idx_to_char(ki, alpha), ki))
            else:
                derived_beau_bc.append((63+i, '?', -1))
        print(f"  Beaufort key for BERLINCLOCK@63: ", end="")
        print("".join(k[1] for k in derived_beau_bc))

        derived_beau_ene = []
        for i, (c_char, p_char) in enumerate(zip(K4_CIPHER[21:21+len(crib2)], crib2)):
            ci = char_to_idx(c_char, alpha)
            pi = char_to_idx(p_char, alpha)
            if ci != -1 and pi != -1:
                ki = (ci + pi) % n
                derived_beau_ene.append((21+i, idx_to_char(ki, alpha), ki))
            else:
                derived_beau_ene.append((21+i, '?', -1))
        print(f"  Beaufort key for EASTNORTHEAST@21: ", end="")
        print("".join(k[1] for k in derived_beau_ene))

        # Check if derived key segments match any city name sequences
        key_bc_str = "".join(k[1] for k in derived_key_bc)
        key_ene_str = "".join(k[1] for k in derived_key_ene)
        beau_bc_str = "".join(k[1] for k in derived_beau_bc)
        beau_ene_str = "".join(k[1] for k in derived_beau_ene)

        # Search for these patterns in our concatenated city keys
        for key_name, key_text in text_keys.items():
            if key_name.startswith("_"):
                continue
            key_alpha_str = "".join(c for c in key_text.upper() if c.isalpha())
            for pattern_name, pattern, pos in [
                ("Vig_BC", key_bc_str, 63),
                ("Vig_ENE", key_ene_str, 21),
                ("Beau_BC", beau_bc_str, 63),
                ("Beau_ENE", beau_ene_str, 21),
            ]:
                # Check if pattern appears at correct position in key (considering cycling)
                key_len = len(key_alpha_str)
                if key_len == 0:
                    continue
                # For a repeating key, the position in the key = pos % key_len
                key_pos = pos % key_len
                # Extract key segment
                key_segment = ""
                for j in range(len(pattern)):
                    key_segment += key_alpha_str[(key_pos + j) % key_len]
                if key_segment == pattern:
                    print(f"\n  *** KEY MATCH *** {pattern_name} matches {key_name} at key position {key_pos}")
                    print(f"    Pattern: {pattern}")
                    print(f"    Key segment: {key_segment}")

    # ─── Comprehensive derived key analysis ──────────────────────────────

    print("\n" + "─" * 80)
    print("FULL 97-POSITION KEY DERIVATION (assuming Vigenere with standard alphabet)")
    print("─" * 80)

    # Show what the full key MUST be if both cribs are correct
    known_key = ['?'] * K4_LEN
    for alpha_name, alpha in [("Standard", STANDARD_ALPHA), ("Kryptos", KRYPTOS_ALPHA)]:
        n = len(alpha)
        key_positions = {}

        for crib_text, crib_pos in CRIBS.items():
            for i, (c_char, p_char) in enumerate(zip(K4_CIPHER[crib_pos:crib_pos+len(crib_text)], crib_text)):
                ci = char_to_idx(c_char, alpha)
                pi = char_to_idx(p_char, alpha)
                if ci != -1 and pi != -1:
                    ki = (ci - pi) % n
                    key_positions[crib_pos + i] = idx_to_char(ki, alpha)

        key_display = ['.' for _ in range(K4_LEN)]
        for pos, ch in key_positions.items():
            key_display[pos] = ch

        print(f"\n  {alpha_name} alphabet - derived key positions:")
        print(f"  Pos: ", end="")
        for i in range(K4_LEN):
            if i % 10 == 0:
                print(f"{i:>2}", end="")
            else:
                print("  ", end="")
        print()
        # Print in rows of 50
        kd_str = "".join(key_display)
        print(f"  Key: {kd_str[:50]}")
        print(f"       {kd_str[50:]}")

        # Check the derived key letters against city name concat positions
        concat_cities = "".join(WELTZEITUHR_CITIES)
        match_count = 0
        for pos, ch in key_positions.items():
            if pos < len(concat_cities) and concat_cities[pos] == ch:
                match_count += 1
        print(f"  Matches against raw city concat: {match_count}/{len(key_positions)}")

        # Check against cycling city concat
        for cycle_len in [len(concat_cities)] + list(range(20, 100)):
            cycling = (concat_cities * 5)[:max(K4_LEN, cycle_len)]
            match = 0
            for pos, ch in key_positions.items():
                if pos < len(cycling) and cycling[pos] == ch:
                    match += 1
            if match > len(key_positions) * 0.3:  # >30% match
                print(f"  Cycling period {cycle_len}: {match}/{len(key_positions)} matches")

    # ─── Sort and display top results ────────────────────────────────────

    print("\n" + "=" * 80)
    print(f"TOP 20 RESULTS (from {len(results)} total decryptions, {test_count} tests)")
    print("=" * 80)

    results.sort(key=lambda r: r["score"], reverse=True)

    for rank, r in enumerate(results[:20], 1):
        print(f"\n{'─' * 70}")
        print(f"Rank {rank}: Score={r['score']} (covered={r['covered']}/{K4_LEN}, cribs={len(r['crib_hits'])})")
        print(f"  Key:    {r['key_name']}")
        print(f"  Cipher: {r['cipher']}")
        print(f"  Key preview: {r['key_preview']}")
        print(f"  Plaintext: {r['plaintext']}")
        if r['crib_hits']:
            print(f"  *** CRIB HITS: {r['crib_hits']} ***")
        if r['words']:
            top_words = sorted(r['words'], key=lambda w: len(w.split('@')[0]), reverse=True)[:10]
            print(f"  Words found: {', '.join(top_words)}")

    # ─── Summary statistics ──────────────────────────────────────────────

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    any_crib = [r for r in results if r['crib_hits']]
    if any_crib:
        print(f"\n  *** {len(any_crib)} results had crib matches! ***")
        for r in any_crib:
            print(f"    {r['key_name']} / {r['cipher']}: {r['crib_hits']}")
            print(f"    Plaintext: {r['plaintext']}")
    else:
        print("\n  No results matched known crib positions (BERLINCLOCK@63, EASTNORTHEAST@21)")

    # Stats on best scores
    if results:
        best = results[0]
        print(f"\n  Best score: {best['score']} ({best['key_name']} / {best['cipher']})")
        print(f"  Coverage: {best['covered']}/{K4_LEN} characters explained by dictionary words")

    print(f"\n  Total tests run: {test_count}")
    print(f"  Total decryptions evaluated: {len(results)}")

    # Show histogram of scores
    print("\n  Score distribution:")
    brackets = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 50), (50, 100), (100, 500)]
    for lo, hi in brackets:
        count = sum(1 for r in results if lo <= r['score'] < hi)
        bar = "#" * min(count // 5, 50)
        print(f"    {lo:3d}-{hi:3d}: {count:5d} {bar}")


if __name__ == "__main__":
    main()
