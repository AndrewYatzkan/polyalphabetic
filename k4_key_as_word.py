#!/usr/bin/env python3
"""
CRITICAL: The known partial Vigenere key (OYNKYELYOIECBAQK?????RDUMRIYW)
doesn't look like English. But what if we're using the WRONG alphabet?

Test: derive the key using DIFFERENT keyed alphabets. If one of them
produces a key that IS a recognizable English word/phrase, that's
probably the correct alphabet.

Also test: what if the key is a word when read through a different mapping?
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

def make_keyed_alphabet(keyword, base="ABCDEFGHIKLMNOPQRSTUVWXYZ"):
    """Create keyed alphabet from keyword (25 letters, no J)."""
    seen = set()
    result = []
    for c in keyword.upper():
        if c == 'J':
            c = 'I'
        if c not in seen and c in base:
            result.append(c)
            seen.add(c)
    for c in base:
        if c not in seen:
            result.append(c)
            seen.add(c)
    return ''.join(result)

def make_keyed_alphabet_26(keyword, base="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """Create keyed alphabet from keyword (26 letters)."""
    seen = set()
    result = []
    for c in keyword.upper():
        if c not in seen and c in base:
            result.append(c)
            seen.add(c)
    for c in base:
        if c not in seen:
            result.append(c)
            seen.add(c)
    return ''.join(result)

def derive_key_with_alpha(ct, pt_text, pt_start, alpha):
    """Derive key characters from a crib using given alphabet."""
    n = len(alpha)
    key = {}
    for j, pt_char in enumerate(pt_text):
        ct_pos = pt_start + j
        ct_char = ct[ct_pos]
        if ct_char not in alpha or pt_char not in alpha:
            return None  # Invalid character for this alphabet
        ct_idx = alpha.index(ct_char)
        pt_idx = alpha.index(pt_char)
        key_val = (ct_idx - pt_idx) % n
        key[ct_pos] = alpha[key_val]
    return key

# Test many different alphabets
KRYPTOS_26 = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars
STANDARD_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

keywords_to_test = [
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "BERLINCLOCK",
    "SANBORN",
    "SCHEIDT",
    "LANGLEY",
    "SHADOW",
    "BETWEEN",
    "DESPERATELY",
    "SLOWLY",
    "INVISIBLE",
    "DIGETAL",  # Sanborn's misspelling
    "VIRTUAL",
    "UNDERGRUUND",  # Another Sanborn misspelling
    "IQLUSION",  # Another misspelling
    "COMPASS",
    "NORTHEAST",
    "SECRET",
    "HIDDEN",
    "BURIED",
    "CIA",
    "INTELLIGENCE",
    "AGENCY",
    "CENTRAL",
]

print("=" * 80)
print("KEY DERIVATION WITH DIFFERENT ALPHABETS")
print("=" * 80)

# For each keyword, generate keyed alphabet and derive key
results = []
for kw in keywords_to_test:
    alpha = make_keyed_alphabet_26(kw)

    # Derive key from BERLINCLOCK@63
    bc_key = derive_key_with_alpha(K4, "BERLINCLOCK", 63, alpha)
    if bc_key is None:
        continue

    # Derive key from EASTNORTHEAST@21
    ene_key = derive_key_with_alpha(K4, "EASTNORTHEAST", 21, alpha)
    if ene_key is None:
        continue

    # Merge keys (check for conflicts at overlapping period-29 positions)
    merged_key = {}
    conflict = False
    for pos, val in {**bc_key, **ene_key}.items():
        kp = pos % 29
        if kp in merged_key:
            if merged_key[kp] != val:
                conflict = True
                break
        else:
            merged_key[kp] = val

    if conflict:
        continue

    # Build full key string
    key_str = ''.join(merged_key.get(i, '?') for i in range(29))

    # Check if key looks like English
    # Remove '?' and check for dictionary words
    key_known = key_str.replace('?', '')

    # Score: how many English letters/words in key?
    common_words_in_key = []
    for word in ["THE", "AND", "FOR", "KEY", "SET", "ALL", "ONE", "OUT", "MAN",
                  "OLD", "NEW", "DAY", "WAY", "MAY", "SAY", "USE", "OUR", "TWO",
                  "HER", "HIS", "HOW", "ITS", "LET", "PUT", "RUN", "SAW", "TEN",
                  "BIG", "TOP", "BOX", "END", "RED", "SUN", "CUT", "DID", "OIL",
                  "SIT", "NOW", "TRY", "ASK", "LOW", "HOT"]:
        if word in key_str:
            common_words_in_key.append(word)

    results.append((len(common_words_in_key), kw, alpha, key_str, common_words_in_key))

    if len(common_words_in_key) > 0 or kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
        print(f"\nAlphabet keyword: {kw}")
        print(f"  Alphabet: {alpha}")
        print(f"  Key (period 29): {key_str}")
        if common_words_in_key:
            print(f"  *** Words in key: {common_words_in_key} ***")

# Sort by score
results.sort(key=lambda x: -x[0])
print(f"\n\nBest alphabets by words-in-key score:")
for score, kw, alpha, key_str, words in results[:10]:
    print(f"  {kw}: key={key_str} words={words}")

# Now test: what if the KEY is a known word, and we derive the ALPHABET?
print("\n" + "=" * 80)
print("REVERSE: KNOWN KEY WORD → DERIVE ALPHABET")
print("=" * 80)

# If the key is a known word of length 29 (or repeating shorter word)...
# 29-letter words are rare. But what about phrases?
# "KRYPTOSPALIMPSESTABSCISSA" = 25 chars... close to 29
# "KRYPTOS" repeated: KRYPTOSKRYPTOSKRYPTOSKRYPTO = 28 chars...

# Actually, what about the key being a meaningful phrase of exactly 29 chars?
# Some possibilities:
key_candidates = [
    "THEBERLINCLOCKISTHEANSWERX",  # 26 chars
    "BERLINKRYPTOSCHEIDTSANBORN",  # 27 chars
    "KRYPTOSSCULPTUREATLANGLEYVA",  # 28 chars...
    "BERLINCLOCKDEGREESTWENTYNINE",  # 29 chars!
    "THEDIRECTIONISEASTNORTHEAST",  # 28 chars
    "SHADOWSANDLAYERSBENEATHTHEM",  # 28 chars
    # What about cycling KRYPTOS: KRYPTOSKRYPTOSKRYPTOSKRYPTOS = 28
    # Or: PALIMPSESTABSCISSAKRYPTOS = 25
]

for key_cand in key_candidates:
    if len(key_cand) < 29:
        key_cand = key_cand + 'X' * (29 - len(key_cand))
    key_cand = key_cand[:29]

    # Check: does this key, with KRYPTOS alphabet, correctly decrypt the cribs?
    # Decrypt positions 63-73 and check for BERLINCLOCK
    alpha = KRYPTOS_26
    ok = True
    for j, expected_pt in enumerate("BERLINCLOCK"):
        ct_pos = 63 + j
        kp = ct_pos % 29
        ct_idx = alpha.index(K4[ct_pos])
        key_idx = alpha.index(key_cand[kp])
        pt_char = alpha[(ct_idx - key_idx) % 26]
        if pt_char != expected_pt:
            ok = False
            break

    if ok:
        # Also check EASTNORTHEAST@21
        ene_ok = True
        for j, expected_pt in enumerate("EASTNORTHEAST"):
            ct_pos = 21 + j
            kp = ct_pos % 29
            ct_idx = alpha.index(K4[ct_pos])
            key_idx = alpha.index(key_cand[kp])
            pt_char = alpha[(ct_idx - key_idx) % 26]
            if pt_char != expected_pt:
                ene_ok = False
                break

        if ene_ok:
            # Full decrypt!
            pt = []
            for i in range(97):
                kp = i % 29
                ct_idx = alpha.index(K4[i])
                key_idx = alpha.index(key_cand[kp])
                pt.append(alpha[(ct_idx - key_idx) % 26])
            pt_str = ''.join(pt)
            print(f"\n*** BOTH CRIBS MATCH! ***")
            print(f"  Key: {key_cand}")
            print(f"  PT:  {pt_str}")

# Test cycling known passwords
print("\n--- Cycling known keywords to period 29 ---")
cycling_keywords = [
    "KRYPTOS",          # 7 chars → repeat to 29
    "PALIMPSEST",       # 10 chars → repeat to 29
    "ABSCISSA",         # 8 chars → repeat to 29
    "BERLINCLOCK",      # 11 chars → repeat to 29
    "SHADOW",           # 6 chars → repeat to 29
    "KRYPTOSABSCISSA",  # 15 chars → repeat to 29
    "KRYPTOSPALIMPSEST",# 17 chars → repeat to 29
]

for kw in cycling_keywords:
    # Cycle to length 29
    key29 = (kw * (29 // len(kw) + 1))[:29]

    # Check cribs
    alpha = KRYPTOS_26
    bc_ok = True
    for j, expected_pt in enumerate("BERLINCLOCK"):
        ct_pos = 63 + j
        kp = ct_pos % 29
        ct_idx = alpha.index(K4[ct_pos])
        key_idx = alpha.index(key29[kp])
        pt_char = alpha[(ct_idx - key_idx) % 26]
        if pt_char != expected_pt:
            bc_ok = False
            break

    ene_ok = True
    for j, expected_pt in enumerate("EASTNORTHEAST"):
        ct_pos = 21 + j
        kp = ct_pos % 29
        ct_idx = alpha.index(K4[ct_pos])
        key_idx = alpha.index(key29[kp])
        pt_char = alpha[(ct_idx - key_idx) % 26]
        if pt_char != expected_pt:
            ene_ok = False
            break

    print(f"  {kw:25s} → key29={key29} BC={'✓' if bc_ok else '✗'} ENE={'✓' if ene_ok else '✗'}")

# What if the key is generated by a different rule?
print("\n" + "=" * 80)
print("KEY GENERATION RULES TEST")
print("=" * 80)

known_key = "OYNKYELYOIECBAQK?????RDUMRIYW"
known_vals = [KRYPTOS_26.index(c) if c != '?' else None for c in known_key]

# Test: is the key an arithmetic sequence mod 26?
print("\nArithmetic sequence test:")
for a in range(26):  # start
    for d in range(26):  # common difference
        seq = [(a + i * d) % 26 for i in range(29)]
        match = True
        for i in range(29):
            if known_vals[i] is not None and seq[i] != known_vals[i]:
                match = False
                break
        if match:
            key_str = ''.join(KRYPTOS_26[v] for v in seq)
            print(f"  a={a} d={d}: {key_str}")

# Test: is the key a polynomial sequence?
print("\nQuadratic sequence test (a + bi + ci^2):")
found_any = False
for a in range(26):
    for b in range(26):
        for c in range(1, 26):  # c=0 is arithmetic
            seq = [(a + b*i + c*i*i) % 26 for i in range(29)]
            match = True
            for i in range(29):
                if known_vals[i] is not None and seq[i] != known_vals[i]:
                    match = False
                    break
            if match:
                key_str = ''.join(KRYPTOS_26[v] for v in seq)
                print(f"  a={a} b={b} c={c}: {key_str}")
                found_any = True
                if found_any:
                    break
        if found_any:
            break
    if found_any:
        break
if not found_any:
    print("  No quadratic sequence matches")

# Test: is the key generated by a LFSR (linear feedback shift register)?
print("\nLFSR test (each char = linear combo of previous chars):")
# For a simple LFSR of order 2: key[i] = (a*key[i-1] + b*key[i-2]) mod 26
for a_coeff in range(26):
    for b_coeff in range(26):
        # Seed from known_vals[0] and known_vals[1]
        if known_vals[0] is None or known_vals[1] is None:
            continue
        seq = [known_vals[0], known_vals[1]]
        for i in range(2, 29):
            seq.append((a_coeff * seq[i-1] + b_coeff * seq[i-2]) % 26)
        match = True
        for i in range(29):
            if known_vals[i] is not None and seq[i] != known_vals[i]:
                match = False
                break
        if match:
            key_str = ''.join(KRYPTOS_26[v] for v in seq)
            print(f"  LFSR(2) a={a_coeff} b={b_coeff}: {key_str}")

# Order 3 LFSR
print("\nLFSR order 3:")
if all(known_vals[i] is not None for i in range(3)):
    for a_c in range(26):
        for b_c in range(26):
            for c_c in range(26):
                seq = [known_vals[0], known_vals[1], known_vals[2]]
                for i in range(3, 29):
                    seq.append((a_c * seq[i-1] + b_c * seq[i-2] + c_c * seq[i-3]) % 26)
                match = True
                for i in range(29):
                    if known_vals[i] is not None and seq[i] != known_vals[i]:
                        match = False
                        break
                if match:
                    key_str = ''.join(KRYPTOS_26[v] for v in seq)
                    print(f"  LFSR(3) a={a_c} b={b_c} c={c_c}: {key_str}")

print("\nDone.")
