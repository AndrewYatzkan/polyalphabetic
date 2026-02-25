#!/usr/bin/env python3
"""
K4 Quagmire III/IV and Multi-Tableau Cipher Testing
=====================================================
Tests Quagmire III, Quagmire IV, Porta, Beaufort-with-keyed-alphabet,
and multi-alphabet rotation schemes against K4 ciphertext.

Cribs: BERLINCLOCK at positions 63-73, EASTNORTHEAST at positions 21-33
Period: 29
KRYPTOS alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ
"""

import math
import itertools
from collections import defaultdict

# ============================================================
# CONSTANTS
# ============================================================
K4_CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
PERIOD = 29
LEN_K4 = len(K4_CT)  # 97

# Known cribs
CRIB_BERLIN = ("BERLINCLOCK", 63)
CRIB_EASTNORTHEAST = ("EASTNORTHEAST", 21)

# Keywords to try
KEYWORDS = [
    "PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLIN", "CLOCK",
    "BERLINCLOCK", "EASTNORTHEAST", "NORTHEAST", "EAST", "NORTH",
    "SANBORN", "SCHEIDT", "CIA", "LANGLEY", "SHADOW",
    "LUCID", "MEMORY", "DYAHR", "DIGETAL", "OBSCURA",
    "INTERPRETIV", "UNDERGRUUND", "IQLUSION", "SLOWLYDESPARATLY",
    "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHETHENUEANCEOFIQLUSION",
    "WHQAOBEK",  # potential key fragment
]

# ============================================================
# SCORING
# ============================================================
print("Loading quadgram statistics...")
QUADGRAMS = {}
QUADGRAM_TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            QUADGRAMS[parts[0]] = int(parts[1])
            QUADGRAM_TOTAL += int(parts[1])

LOG_TOTAL = math.log10(QUADGRAM_TOTAL)
FLOOR = math.log10(0.01 / QUADGRAM_TOTAL)

def quadgram_score(text):
    """Score text using log10 quadgram frequency."""
    t = text.upper()
    score = 0.0
    for i in range(len(t) - 3):
        q = t[i:i+4]
        if q in QUADGRAMS:
            score += math.log10(QUADGRAMS[q]) - LOG_TOTAL
        else:
            score += FLOOR
    return score

# Load dictionary for word detection
print("Loading dictionary...")
DICTIONARY = set()
with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
    for line in f:
        w = line.strip().upper()
        if len(w) >= 4:
            DICTIONARY.add(w)

# Add some common short words and K4-relevant words
for w in ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN",
          "HER", "WAS", "ONE", "OUR", "OUT", "DAY", "HAD", "HAS", "HIS",
          "HOW", "ITS", "MAY", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO",
          "DID", "GET", "LET", "SAY", "SHE", "TOO", "USE",
          "BERLIN", "CLOCK", "EAST", "NORTH", "NORTHEAST", "LAYER",
          "BETWEEN", "SHADOW", "LIGHT", "LUCID", "MEMORY",
          "UNDERGROUND", "BURIED", "SECRET", "HIDDEN", "LOCATION",
          "LATITUDE", "LONGITUDE", "DEGREES", "MINUTES", "SECONDS",
          "SLOWLY", "DESPERATELY", "VIRTUALLY", "INVISIBLE",
          "ILLUSION", "ABSENCE", "SUBTLE", "SHADING", "NUANCE"]:
    DICTIONARY.add(w.upper())


def count_english_words(text, min_len=4):
    """Count how many dictionary words appear in text."""
    t = text.upper()
    found = []
    for length in range(min_len, min(16, len(t)+1)):
        for i in range(len(t) - length + 1):
            sub = t[i:i+length]
            if sub in DICTIONARY:
                found.append((i, sub))
    return found


def check_cribs(text):
    """Check if known cribs appear at expected positions."""
    t = text.upper()
    results = {}
    for crib_text, crib_pos in [CRIB_BERLIN, CRIB_EASTNORTHEAST]:
        if crib_pos + len(crib_text) <= len(t):
            actual = t[crib_pos:crib_pos+len(crib_text)]
            match_count = sum(1 for a, b in zip(actual, crib_text) if a == b)
            results[crib_text] = (match_count, len(crib_text), actual)
        # Also check if crib appears anywhere
        idx = t.find(crib_text)
        if idx >= 0:
            results[f"{crib_text}_found_at"] = idx
    return results


# ============================================================
# ALPHABET UTILITIES
# ============================================================

def make_keyed_alphabet(keyword, base_alpha=STANDARD_ALPHA):
    """Create a keyed alphabet: keyword letters first (deduplicated), then remaining."""
    seen = set()
    result = []
    for ch in keyword.upper():
        if ch not in seen and ch in base_alpha:
            seen.add(ch)
            result.append(ch)
    for ch in base_alpha:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)
    return ''.join(result)


def make_kryptos_keyed(keyword):
    """Create a keyed alphabet using KRYPTOS alphabet as base ordering."""
    return make_keyed_alphabet(keyword, KRYPTOS_ALPHA)


# ============================================================
# QUAGMIRE CIPHER IMPLEMENTATIONS
# ============================================================

def quagmire_I_decrypt(ct, indicator_key, pt_keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Quagmire I: Plain alphabet keyed with pt_keyword.
                Cipher alphabets are standard.
                Indicator key indexes into KEYED alphabet.
    """
    pt_alpha = make_keyed_alphabet(pt_keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in base_alpha:
            plaintext.append(c)
            continue
        key_char = indicator_key[i % period]
        # Shift = position of key_char in pt_alpha (keyed)
        shift = pt_alpha.index(key_char)
        # ct position in standard alphabet
        ct_pos = base_alpha.index(c)
        # Decrypt: pt_pos in standard = (ct_pos - shift) mod 26
        pt_pos = (ct_pos - shift) % len(base_alpha)
        # Map back through keyed pt alphabet? No - 
        # Actually in Quag I: encrypt is ct = standard[(keyed.index(pt) + shift) % 26]
        # So decrypt: pt = keyed[(standard.index(ct) - shift) % 26]
        pt_pos = (ct_pos - shift) % len(base_alpha)
        plaintext.append(pt_alpha[pt_pos])
    return ''.join(plaintext)


def quagmire_II_decrypt(ct, indicator_key, ct_keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Quagmire II: Plain alphabet standard.
                 Cipher alphabets keyed with ct_keyword.
                 Indicator key indexes into STANDARD alphabet.
    """
    ct_alpha = make_keyed_alphabet(ct_keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in ct_alpha:
            plaintext.append('?')
            continue
        key_char = indicator_key[i % period]
        # Shift = position of key_char in standard
        shift = base_alpha.index(key_char)
        # ct position in keyed cipher alphabet
        ct_pos = ct_alpha.index(c)
        # Decrypt: pt_pos in standard = (ct_pos - shift) mod 26
        pt_pos = (ct_pos - shift) % len(base_alpha)
        plaintext.append(base_alpha[pt_pos])
    return ''.join(plaintext)


def quagmire_III_decrypt(ct, indicator_key, keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Quagmire III: Both plain and cipher alphabets keyed with SAME keyword.
                  Indicator key indexes into KEYED alphabet.
    """
    keyed = make_keyed_alphabet(keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in keyed:
            plaintext.append('?')
            continue
        key_char = indicator_key[i % period]
        # Shift = position of key_char in keyed alphabet
        shift = keyed.index(key_char)
        # ct position in keyed alphabet
        ct_pos = keyed.index(c)
        # Decrypt: pt_pos = (ct_pos - shift) mod 26
        pt_pos = (ct_pos - shift) % len(base_alpha)
        plaintext.append(keyed[pt_pos])
    return ''.join(plaintext)


def quagmire_IV_decrypt(ct, indicator_key, pt_keyword, ct_keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Quagmire IV: Plain alphabet keyed with pt_keyword.
                 Cipher alphabet keyed with ct_keyword (different keyword).
                 Indicator key indexes into pt_keyword keyed alphabet.
    """
    pt_alpha = make_keyed_alphabet(pt_keyword, base_alpha)
    ct_alpha = make_keyed_alphabet(ct_keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in ct_alpha:
            plaintext.append('?')
            continue
        key_char = indicator_key[i % period]
        # Shift = position of key_char in pt_alpha (keyed)
        shift = pt_alpha.index(key_char)
        # ct position in ct_alpha
        ct_pos = ct_alpha.index(c)
        # Decrypt: pt_pos = (ct_pos - shift) mod 26
        pt_pos = (ct_pos - shift) % len(base_alpha)
        plaintext.append(pt_alpha[pt_pos])
    return ''.join(plaintext)


def beaufort_keyed_decrypt(ct, key, keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Beaufort with keyed alphabet: pt = key - ct (in keyed alphabet arithmetic).
    """
    keyed = make_keyed_alphabet(keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in keyed:
            plaintext.append('?')
            continue
        key_char = key[i % period]
        key_pos = keyed.index(key_char)
        ct_pos = keyed.index(c)
        pt_pos = (key_pos - ct_pos) % len(base_alpha)
        plaintext.append(keyed[pt_pos])
    return ''.join(plaintext)


def variant_beaufort_keyed_decrypt(ct, key, keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Variant Beaufort with keyed alphabet: pt = ct - key (in keyed alphabet arithmetic).
    """
    keyed = make_keyed_alphabet(keyword, base_alpha)
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in keyed:
            plaintext.append('?')
            continue
        key_char = key[i % period]
        key_pos = keyed.index(key_char)
        ct_pos = keyed.index(c)
        pt_pos = (ct_pos - key_pos) % len(base_alpha)
        plaintext.append(keyed[pt_pos])
    return ''.join(plaintext)


def porta_decrypt(ct, key, period, base_alpha=STANDARD_ALPHA):
    """
    Porta cipher: reciprocal cipher where alphabet is split in half.
    Each key letter selects one of 13 cipher alphabets.
    The cipher is reciprocal: encrypt = decrypt.
    Uses standard 26-letter alphabet.
    """
    n = len(base_alpha)
    half = n // 2
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in base_alpha:
            plaintext.append('?')
            continue
        key_char = key[i % period]
        key_pos = base_alpha.index(key_char)
        ct_pos = base_alpha.index(c)
        # Key selects row (0-12), pairing letters
        row = key_pos // 2
        
        if ct_pos < half:
            # First half: shift in second half
            pt_pos = half + (ct_pos + row) % half
        else:
            # Second half: reverse shift in first half
            pt_pos = (ct_pos - half - row) % half
        plaintext.append(base_alpha[pt_pos])
    return ''.join(plaintext)


def porta_keyed_decrypt(ct, key, keyword, period, base_alpha=STANDARD_ALPHA):
    """
    Porta cipher with keyed alphabet.
    """
    keyed = make_keyed_alphabet(keyword, base_alpha)
    n = len(keyed)
    half = n // 2
    plaintext = []
    for i, c in enumerate(ct.upper()):
        if c not in keyed:
            plaintext.append('?')
            continue
        key_char = key[i % period]
        key_pos = keyed.index(key_char)
        ct_pos = keyed.index(c)
        row = key_pos // 2
        
        if ct_pos < half:
            pt_pos = half + (ct_pos + row) % half
        else:
            pt_pos = (ct_pos - half - row) % half
        plaintext.append(keyed[pt_pos])
    return ''.join(plaintext)


# ============================================================
# KEY EXTRACTION FROM CRIBS
# ============================================================

def extract_key_from_crib(ct, pt, pos, alpha, cipher_type="vigenere"):
    """
    Given crib plaintext at position in ciphertext, extract key characters.
    Returns dict of {key_position_mod_period: key_char}
    """
    key_chars = {}
    for i, (c, p) in enumerate(zip(ct[pos:pos+len(pt)], pt)):
        key_pos = (pos + i) % PERIOD
        if c in alpha and p in alpha:
            c_idx = alpha.index(c)
            p_idx = alpha.index(p)
            if cipher_type == "vigenere":
                k_idx = (c_idx - p_idx) % len(alpha)
            elif cipher_type == "beaufort":
                k_idx = (c_idx + p_idx) % len(alpha)
            elif cipher_type == "variant_beaufort":
                k_idx = (c_idx - p_idx) % len(alpha)  # same direction different convention
            else:
                k_idx = (c_idx - p_idx) % len(alpha)
            key_chars[key_pos] = alpha[k_idx]
    return key_chars


def extract_quagmire_key(ct, pt, pos, keyed_alpha, cipher_type="quag3"):
    """Extract key characters for Quagmire variants given a crib."""
    key_chars = {}
    for i, (c, p) in enumerate(zip(ct[pos:pos+len(pt)], pt)):
        key_pos = (pos + i) % PERIOD
        if c in keyed_alpha and p in keyed_alpha:
            c_idx = keyed_alpha.index(c)
            p_idx = keyed_alpha.index(p)
            if cipher_type in ("quag3", "quag4"):
                k_idx = (c_idx - p_idx) % len(keyed_alpha)
            elif cipher_type == "beaufort":
                k_idx = (c_idx + p_idx) % len(keyed_alpha)  # pt = key - ct => key = ct + pt
            else:
                k_idx = (c_idx - p_idx) % len(keyed_alpha)
            key_chars[key_pos] = keyed_alpha[k_idx]
    return key_chars


# ============================================================
# MULTI-ALPHABET ROTATION (k mod 3 approach)
# ============================================================

def multi_alphabet_decrypt(ct, key, alphabets, period, rotation_period=3):
    """
    Use different cipher alphabets in rotation.
    alphabets is a list of alphabet strings; cycle through them.
    """
    plaintext = []
    for i, c in enumerate(ct.upper()):
        alpha = alphabets[i % rotation_period]
        if c not in alpha:
            plaintext.append('?')
            continue
        key_char = key[i % period]
        if key_char not in alpha:
            plaintext.append('?')
            continue
        key_pos = alpha.index(key_char)
        ct_pos = alpha.index(c)
        pt_pos = (ct_pos - key_pos) % len(alpha)
        plaintext.append(alpha[pt_pos])
    return ''.join(plaintext)


# ============================================================
# COMPREHENSIVE INDICATOR KEY GENERATION
# ============================================================

def generate_indicator_keys_from_cribs(keyed_alpha, cipher_func_name="quag3"):
    """
    Use both cribs to extract as many key positions as possible,
    then return partial key (with None for unknown positions).
    """
    partial_key = [None] * PERIOD
    
    # Extract from BERLINCLOCK at 63
    for i, (c, p) in enumerate(zip(K4_CT[63:63+11], "BERLINCLOCK")):
        kpos = (63 + i) % PERIOD
        if c in keyed_alpha and p in keyed_alpha:
            c_idx = keyed_alpha.index(c)
            p_idx = keyed_alpha.index(p)
            k_idx = (c_idx - p_idx) % len(keyed_alpha)
            partial_key[kpos] = keyed_alpha[k_idx]
    
    # Extract from EASTNORTHEAST at 21
    for i, (c, p) in enumerate(zip(K4_CT[21:21+13], "EASTNORTHEAST")):
        kpos = (21 + i) % PERIOD
        if c in keyed_alpha and p in keyed_alpha:
            c_idx = keyed_alpha.index(c)
            p_idx = keyed_alpha.index(p)
            k_idx = (c_idx - p_idx) % len(keyed_alpha)
            partial_key[kpos] = keyed_alpha[k_idx]
    
    return partial_key


def generate_beaufort_indicator_keys_from_cribs(keyed_alpha):
    """Extract key for Beaufort: key = ct + pt (mod alpha)."""
    partial_key = [None] * PERIOD
    
    for i, (c, p) in enumerate(zip(K4_CT[63:63+11], "BERLINCLOCK")):
        kpos = (63 + i) % PERIOD
        if c in keyed_alpha and p in keyed_alpha:
            c_idx = keyed_alpha.index(c)
            p_idx = keyed_alpha.index(p)
            # Beaufort: pt = key - ct => key = pt + ct
            k_idx = (p_idx + c_idx) % len(keyed_alpha)
            partial_key[kpos] = keyed_alpha[k_idx]
    
    for i, (c, p) in enumerate(zip(K4_CT[21:21+13], "EASTNORTHEAST")):
        kpos = (21 + i) % PERIOD
        if c in keyed_alpha and p in keyed_alpha:
            c_idx = keyed_alpha.index(c)
            p_idx = keyed_alpha.index(p)
            k_idx = (p_idx + c_idx) % len(keyed_alpha)
            partial_key[kpos] = keyed_alpha[k_idx]
    
    return partial_key


# ============================================================
# RESULT TRACKING
# ============================================================
results = []

def test_and_record(name, plaintext, key_info=""):
    """Test a decryption result and record it."""
    if not plaintext or '?' in plaintext:
        return
    score = quadgram_score(plaintext)
    cribs = check_cribs(plaintext)
    words = count_english_words(plaintext)
    
    # Check for crib matches
    berlin_match = cribs.get("BERLINCLOCK", (0, 11, ""))[0] if "BERLINCLOCK" in cribs else 0
    ene_match = cribs.get("EASTNORTHEAST", (0, 13, ""))[0] if "EASTNORTHEAST" in cribs else 0
    berlin_found = cribs.get("BERLINCLOCK_found_at", -1)
    ene_found = cribs.get("EASTNORTHEAST_found_at", -1)
    
    results.append({
        'name': name,
        'plaintext': plaintext,
        'score': score,
        'berlin_match': berlin_match,
        'ene_match': ene_match,
        'berlin_found': berlin_found,
        'ene_found': ene_found,
        'words': words,
        'key_info': key_info,
    })
    
    # Print immediately if interesting
    is_interesting = (berlin_match >= 8 or ene_match >= 9 or 
                      berlin_found >= 0 or ene_found >= 0 or
                      score > -350 or len(words) >= 5)
    
    if is_interesting:
        print(f"\n{'='*70}")
        print(f"*** INTERESTING: {name}")
        print(f"    Key: {key_info}")
        print(f"    PT:  {plaintext}")
        print(f"    Score: {score:.1f}")
        print(f"    BERLINCLOCK match: {berlin_match}/11 at pos 63")
        print(f"    EASTNORTHEAST match: {ene_match}/13 at pos 21")
        if berlin_found >= 0:
            print(f"    BERLINCLOCK found at position {berlin_found}!")
        if ene_found >= 0:
            print(f"    EASTNORTHEAST found at position {ene_found}!")
        if words:
            print(f"    Words found: {words[:10]}")
        print(f"{'='*70}")


# ============================================================
# TEST 1: QUAGMIRE III WITH KRYPTOS ALPHABET
# ============================================================
print("\n" + "="*70)
print("TEST 1: QUAGMIRE III - Both alphabets keyed with same keyword")
print("="*70)

for alpha_keyword in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
    keyed = make_keyed_alphabet(alpha_keyword, STANDARD_ALPHA)
    print(f"\n  Keyed alphabet ({alpha_keyword}): {keyed}")
    
    # Also test with KRYPTOS as base
    keyed_k = make_keyed_alphabet(alpha_keyword, KRYPTOS_ALPHA)
    print(f"  Keyed alphabet ({alpha_keyword} on KRYPTOS base): {keyed_k}")
    
    for indicator in KEYWORDS:
        if len(indicator) > PERIOD:
            # Truncate or use modular
            ind = indicator[:PERIOD]
        else:
            ind = indicator
        
        # Standard base
        pt = quagmire_III_decrypt(K4_CT, ind, alpha_keyword, len(ind), STANDARD_ALPHA)
        test_and_record(
            f"Quag3 std alpha={alpha_keyword} ind={ind} per={len(ind)}",
            pt, f"alpha={alpha_keyword} ind={ind}"
        )
        
        # With period 29 - pad indicator by repeating
        if len(ind) < PERIOD:
            # Try indicator repeated to fill period 29
            ind29 = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
            pt = quagmire_III_decrypt(K4_CT, ind29, alpha_keyword, PERIOD, STANDARD_ALPHA)
            test_and_record(
                f"Quag3 std alpha={alpha_keyword} ind={ind}(x29) per=29",
                pt, f"alpha={alpha_keyword} ind={ind}(x29)"
            )
        
        # KRYPTOS base
        pt = quagmire_III_decrypt(K4_CT, ind, alpha_keyword, len(ind), KRYPTOS_ALPHA)
        test_and_record(
            f"Quag3 kryp alpha={alpha_keyword} ind={ind} per={len(ind)}",
            pt, f"alpha={alpha_keyword}(kryp) ind={ind}"
        )
        
        if len(ind) < PERIOD:
            ind29 = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
            pt = quagmire_III_decrypt(K4_CT, ind29, alpha_keyword, PERIOD, KRYPTOS_ALPHA)
            test_and_record(
                f"Quag3 kryp alpha={alpha_keyword} ind={ind}(x29) per=29",
                pt, f"alpha={alpha_keyword}(kryp) ind={ind}(x29)"
            )

    # Use crib-derived key
    partial_key = generate_indicator_keys_from_cribs(keyed)
    known_count = sum(1 for k in partial_key if k is not None)
    print(f"\n  Crib-derived key ({alpha_keyword}, std): {known_count}/29 positions known")
    print(f"  Key: {''.join(k if k else '?' for k in partial_key)}")
    
    # Check consistency
    conflicts = False
    for i, k in enumerate(partial_key):
        if k is not None:
            pass  # could check cross-crib consistency
    
    partial_key_k = generate_indicator_keys_from_cribs(keyed_k)
    known_count_k = sum(1 for k in partial_key_k if k is not None)
    print(f"  Crib-derived key ({alpha_keyword}, kryp): {known_count_k}/29 positions known")
    print(f"  Key: {''.join(k if k else '?' for k in partial_key_k)}")

    # Try filling unknown positions with each letter and decrypting
    # For now, fill unknowns with 'A' (identity shift) as baseline
    for fill_char in ['A', 'K']:
        full_key_std = ''.join(k if k else fill_char for k in partial_key)
        pt = quagmire_III_decrypt(K4_CT, full_key_std, alpha_keyword, PERIOD, STANDARD_ALPHA)
        test_and_record(
            f"Quag3 crib-key std alpha={alpha_keyword} fill={fill_char}",
            pt, f"key={full_key_std}"
        )
        
        full_key_k = ''.join(k if k else fill_char for k in partial_key_k)
        pt = quagmire_III_decrypt(K4_CT, full_key_k, alpha_keyword, PERIOD, KRYPTOS_ALPHA)
        test_and_record(
            f"Quag3 crib-key kryp alpha={alpha_keyword} fill={fill_char}",
            pt, f"key={full_key_k}"
        )


# ============================================================
# TEST 2: QUAGMIRE IV WITH TWO KEYWORDS
# ============================================================
print("\n" + "="*70)
print("TEST 2: QUAGMIRE IV - Plain & cipher alphabets with different keywords")
print("="*70)

keyword_pairs = [
    ("KRYPTOS", "PALIMPSEST"),
    ("KRYPTOS", "ABSCISSA"),
    ("PALIMPSEST", "KRYPTOS"),
    ("ABSCISSA", "KRYPTOS"),
    ("PALIMPSEST", "ABSCISSA"),
    ("ABSCISSA", "PALIMPSEST"),
    ("KRYPTOS", "BERLIN"),
    ("KRYPTOS", "CLOCK"),
    ("KRYPTOS", "BERLINCLOCK"),
    ("BERLIN", "CLOCK"),
    ("CLOCK", "BERLIN"),
    ("KRYPTOS", "SANBORN"),
    ("KRYPTOS", "SCHEIDT"),
]

for pt_kw, ct_kw in keyword_pairs:
    for indicator in ["PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLIN", "CLOCK", "BERLINCLOCK"]:
        ind = indicator[:PERIOD] if len(indicator) > PERIOD else indicator
        
        # Standard base
        pt = quagmire_IV_decrypt(K4_CT, ind, pt_kw, ct_kw, len(ind), STANDARD_ALPHA)
        test_and_record(
            f"Quag4 std pt={pt_kw} ct={ct_kw} ind={ind}",
            pt, f"pt_kw={pt_kw} ct_kw={ct_kw} ind={ind}"
        )
        
        # KRYPTOS base
        pt = quagmire_IV_decrypt(K4_CT, ind, pt_kw, ct_kw, len(ind), KRYPTOS_ALPHA)
        test_and_record(
            f"Quag4 kryp pt={pt_kw} ct={ct_kw} ind={ind}",
            pt, f"pt_kw={pt_kw} ct_kw={ct_kw} ind={ind}"
        )
        
        # Period 29 padded
        if len(ind) < PERIOD:
            ind29 = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
            pt = quagmire_IV_decrypt(K4_CT, ind29, pt_kw, ct_kw, PERIOD, STANDARD_ALPHA)
            test_and_record(
                f"Quag4 std pt={pt_kw} ct={ct_kw} ind={ind}(x29)",
                pt, f"pt_kw={pt_kw} ct_kw={ct_kw} ind={ind}(x29)"
            )
            pt = quagmire_IV_decrypt(K4_CT, ind29, pt_kw, ct_kw, PERIOD, KRYPTOS_ALPHA)
            test_and_record(
                f"Quag4 kryp pt={pt_kw} ct={ct_kw} ind={ind}(x29)",
                pt, f"pt_kw={pt_kw} ct_kw={ct_kw} ind={ind}(x29)"
            )

    # Crib-derived key for Quag IV
    # For Quag IV: key_shift = ct_alpha.index(c) - pt_alpha.index(p) mod 26
    # And key char = pt_alpha[key_shift]
    pt_alpha = make_keyed_alphabet(pt_kw, STANDARD_ALPHA)
    ct_alpha = make_keyed_alphabet(ct_kw, STANDARD_ALPHA)
    partial_key = [None] * PERIOD
    for crib_text, crib_pos in [CRIB_BERLIN, CRIB_EASTNORTHEAST]:
        for i, (c, p) in enumerate(zip(K4_CT[crib_pos:crib_pos+len(crib_text)], crib_text)):
            kpos = (crib_pos + i) % PERIOD
            if c in ct_alpha and p in pt_alpha:
                c_idx = ct_alpha.index(c)
                p_idx = pt_alpha.index(p)
                k_idx = (c_idx - p_idx) % 26
                partial_key[kpos] = pt_alpha[k_idx]
    
    known = sum(1 for k in partial_key if k is not None)
    key_str = ''.join(k if k else '?' for k in partial_key)
    if known >= 15:
        print(f"  Quag4 pt={pt_kw} ct={ct_kw}: {known}/29 key positions: {key_str}")
        
        for fill_char in ['A', 'K']:
            full_key = ''.join(k if k else fill_char for k in partial_key)
            ptxt = quagmire_IV_decrypt(K4_CT, full_key, pt_kw, ct_kw, PERIOD, STANDARD_ALPHA)
            test_and_record(
                f"Quag4 crib std pt={pt_kw} ct={ct_kw} fill={fill_char}",
                ptxt, f"key={full_key}"
            )


# ============================================================
# TEST 3: MULTIPLE CIPHER ALPHABETS (k mod 3 rotation)
# ============================================================
print("\n" + "="*70)
print("TEST 3: MULTI-ALPHABET ROTATION (Genie Engine k%3 approach)")
print("="*70)

# Generate different keyed alphabets
alphabet_sets = [
    ("KRYPTOS/PALIMPSEST/ABSCISSA", [
        make_keyed_alphabet("KRYPTOS", STANDARD_ALPHA),
        make_keyed_alphabet("PALIMPSEST", STANDARD_ALPHA),
        make_keyed_alphabet("ABSCISSA", STANDARD_ALPHA),
    ]),
    ("KRYPTOS/BERLIN/CLOCK", [
        make_keyed_alphabet("KRYPTOS", STANDARD_ALPHA),
        make_keyed_alphabet("BERLIN", STANDARD_ALPHA),
        make_keyed_alphabet("CLOCK", STANDARD_ALPHA),
    ]),
    ("STD/KRYPTOS/PALIMPSEST", [
        STANDARD_ALPHA,
        KRYPTOS_ALPHA,
        make_keyed_alphabet("PALIMPSEST", STANDARD_ALPHA),
    ]),
    ("KRYPTOS_base variants", [
        make_keyed_alphabet("KRYPTOS", KRYPTOS_ALPHA),
        make_keyed_alphabet("PALIMPSEST", KRYPTOS_ALPHA),
        make_keyed_alphabet("ABSCISSA", KRYPTOS_ALPHA),
    ]),
]

# Extract a crib-derived key using standard vigenere with KRYPTOS alphabet
std_key_chars = {}
for crib_text, crib_pos in [CRIB_BERLIN, CRIB_EASTNORTHEAST]:
    for i, (c, p) in enumerate(zip(K4_CT[crib_pos:crib_pos+len(crib_text)], crib_text)):
        kpos = (crib_pos + i) % PERIOD
        if c in KRYPTOS_ALPHA and p in KRYPTOS_ALPHA:
            c_idx = KRYPTOS_ALPHA.index(c)
            p_idx = KRYPTOS_ALPHA.index(p)
            k_idx = (c_idx - p_idx) % 26
            std_key_chars[kpos] = KRYPTOS_ALPHA[k_idx]

base_key = ''.join(std_key_chars.get(i, 'K') for i in range(PERIOD))
print(f"  Base crib-derived key (KRYPTOS alph, Vigenere): {base_key}")

for name, alphas in alphabet_sets:
    print(f"\n  Testing rotation with alphabets: {name}")
    for rp in [2, 3, 4, 5, 29]:
        # Use only first rp alphabets (cycling)
        cycle_alphas = alphas[:min(rp, len(alphas))]
        if len(cycle_alphas) < rp:
            cycle_alphas = (cycle_alphas * ((rp // len(cycle_alphas)) + 1))[:rp]
        
        # Try with various indicator keys
        for ind_name, ind_key in [("base_key", base_key)] + [(kw, kw) for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]]:
            key = ind_key if len(ind_key) >= PERIOD else (ind_key * ((PERIOD // len(ind_key)) + 1))[:PERIOD]
            pt = multi_alphabet_decrypt(K4_CT, key, cycle_alphas, PERIOD, rp)
            test_and_record(
                f"MultiAlpha rot={rp} alphas={name} key={ind_name}",
                pt, f"rot={rp} key={key[:PERIOD]}"
            )

# Also test: each of the 29 key positions uses a different shifted KRYPTOS alphabet
print("\n  Testing 29 different shifted KRYPTOS alphabets...")
for shift_keyword in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
    keyed = make_keyed_alphabet(shift_keyword, KRYPTOS_ALPHA)
    # Create 29 alphabets, each shifted by a different amount
    for shift_source in ["sequential", "key_derived"]:
        alphas_29 = []
        for j in range(PERIOD):
            if shift_source == "sequential":
                s = j
            else:
                s = KRYPTOS_ALPHA.index(base_key[j]) if base_key[j] in KRYPTOS_ALPHA else j
            shifted = keyed[s:] + keyed[:s]
            alphas_29.append(shifted)
        
        # Each position uses its own alphabet; key is "A" (no additional shift)
        pt_chars = []
        for i, c in enumerate(K4_CT):
            alpha = alphas_29[i % PERIOD]
            if c in alpha:
                ct_pos = alpha.index(c)
                pt_chars.append(alpha[(ct_pos) % 26])  # identity mapping - the shift IS the key
            else:
                pt_chars.append('?')
        pt = ''.join(pt_chars)
        test_and_record(
            f"29-shifted-alphas keyed={shift_keyword} src={shift_source}",
            pt, f"Each pos uses differently shifted {shift_keyword}-keyed alphabet"
        )


# ============================================================
# TEST 4: PORTA CIPHER
# ============================================================
print("\n" + "="*70)
print("TEST 4: PORTA CIPHER")
print("="*70)

for ind_keyword in KEYWORDS[:15]:
    ind = ind_keyword[:PERIOD] if len(ind_keyword) > PERIOD else ind_keyword
    
    # Standard Porta
    pt = porta_decrypt(K4_CT, ind, len(ind), STANDARD_ALPHA)
    test_and_record(f"Porta std ind={ind}", pt, f"ind={ind}")
    
    # Porta period 29
    if len(ind) < PERIOD:
        ind29 = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
        pt = porta_decrypt(K4_CT, ind29, PERIOD, STANDARD_ALPHA)
        test_and_record(f"Porta std ind={ind}(x29) per=29", pt, f"ind={ind}(x29)")
    
    # Porta with keyed alphabet
    for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
        pt = porta_keyed_decrypt(K4_CT, ind, kw, len(ind), STANDARD_ALPHA)
        test_and_record(f"Porta keyed={kw} ind={ind}", pt, f"keyed={kw} ind={ind}")
        
        pt = porta_keyed_decrypt(K4_CT, ind, kw, len(ind), KRYPTOS_ALPHA)
        test_and_record(f"Porta keyed={kw}(kryp) ind={ind}", pt, f"keyed={kw}(kryp) ind={ind}")

# Porta with crib-derived key
# Porta is reciprocal, so encrypt = decrypt
# If pt[i] and ct[i] are in different halves, we can derive key
print("\n  Deriving Porta key from cribs...")
for alpha_name, alpha in [("standard", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
    half = len(alpha) // 2
    porta_key = [None] * PERIOD
    
    for crib_text, crib_pos in [CRIB_BERLIN, CRIB_EASTNORTHEAST]:
        for i, (c, p) in enumerate(zip(K4_CT[crib_pos:crib_pos+len(crib_text)], crib_text)):
            kpos = (crib_pos + i) % PERIOD
            c_idx = alpha.index(c) if c in alpha else -1
            p_idx = alpha.index(p) if p in alpha else -1
            if c_idx < 0 or p_idx < 0:
                continue
            
            # Try all possible key rows (0-12) and see which one maps correctly
            for row in range(13):
                if p_idx < half:
                    # Expected: c_idx = half + (p_idx + row) % half
                    expected_c = half + (p_idx + row) % half
                else:
                    # Expected: c_idx = (p_idx - half - row) % half
                    expected_c = (p_idx - half - row) % half
                
                if expected_c == c_idx:
                    # This row works; key letter has index row*2 or row*2+1
                    porta_key[kpos] = (row, alpha[row*2], alpha[row*2+1] if row*2+1 < len(alpha) else '?')
                    break
    
    known_porta = sum(1 for k in porta_key if k is not None)
    print(f"  Porta key ({alpha_name}): {known_porta}/29 positions derived")
    key_display = []
    for k in porta_key:
        if k is None:
            key_display.append('??')
        else:
            key_display.append(f"{k[1]}/{k[2]}")
    print(f"  Key pairs: {' '.join(key_display)}")


# ============================================================
# TEST 5: BEAUFORT VARIANTS WITH KEYED ALPHABET
# ============================================================
print("\n" + "="*70)
print("TEST 5: BEAUFORT WITH KEYED ALPHABET")
print("="*70)

for alpha_keyword in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
    for base in [("std", STANDARD_ALPHA), ("kryp", KRYPTOS_ALPHA)]:
        base_name, base_alpha = base
        keyed = make_keyed_alphabet(alpha_keyword, base_alpha)
        
        # Crib-derived Beaufort key
        partial_key = generate_beaufort_indicator_keys_from_cribs(keyed)
        known = sum(1 for k in partial_key if k is not None)
        key_str = ''.join(k if k else '?' for k in partial_key)
        
        if known >= 15:
            print(f"\n  Beaufort keyed={alpha_keyword} base={base_name}: {known}/29 key: {key_str}")
        
        for fill_char in [keyed[0], 'A']:
            full_key = ''.join(k if k else fill_char for k in partial_key)
            
            pt = beaufort_keyed_decrypt(K4_CT, full_key, alpha_keyword, PERIOD, base_alpha)
            test_and_record(
                f"Beaufort keyed={alpha_keyword} base={base_name} fill={fill_char}",
                pt, f"key={full_key}"
            )
            
            pt = variant_beaufort_keyed_decrypt(K4_CT, full_key, alpha_keyword, PERIOD, base_alpha)
            test_and_record(
                f"VarBeaufort keyed={alpha_keyword} base={base_name} fill={fill_char}",
                pt, f"key={full_key}"
            )
        
        # Also test with keyword indicators
        for ind in ["PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLIN", "CLOCK"]:
            ind_key = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
            
            pt = beaufort_keyed_decrypt(K4_CT, ind_key, alpha_keyword, PERIOD, base_alpha)
            test_and_record(
                f"Beaufort keyed={alpha_keyword} base={base_name} ind={ind}",
                pt, f"keyed={alpha_keyword} ind={ind_key}"
            )
            
            pt = variant_beaufort_keyed_decrypt(K4_CT, ind_key, alpha_keyword, PERIOD, base_alpha)
            test_and_record(
                f"VarBeaufort keyed={alpha_keyword} base={base_name} ind={ind}",
                pt, f"keyed={alpha_keyword} ind={ind_key}"
            )


# ============================================================
# TEST 6: DEEP QUAGMIRE III/IV CRIB CONSISTENCY CHECK
# ============================================================
print("\n" + "="*70)
print("TEST 6: CRIB CONSISTENCY ANALYSIS")
print("="*70)

# For each cipher type and alphabet combination, check if the two cribs
# produce CONSISTENT key values at overlapping positions
# Positions covered by BERLINCLOCK (63-73): mod 29 = 5,6,7,8,9,10,11,12,13,14,15
# Positions covered by EASTNORTHEAST (21-33): mod 29 = 21,22,23,24,25,26,27,28,0,1,2,3,4

# So positions 5-15 and 21-28,0-4 => NO overlap! They cover 24 of 29 positions.
# Missing: positions 16, 17, 18, 19, 20

print("  BERLINCLOCK at 63-73 covers key positions: ", [(63+i)%29 for i in range(11)])
print("  EASTNORTHEAST at 21-33 covers key positions:", [(21+i)%29 for i in range(13)])
missing = set(range(29)) - set([(63+i)%29 for i in range(11)]) - set([(21+i)%29 for i in range(13)])
print(f"  Missing key positions: {sorted(missing)}")
print(f"  => 24 of 29 key positions determined, only {sorted(missing)} unknown")

# For Quagmire III with KRYPTOS-keyed alphabet
for alpha_kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
    for base_name, base_alpha in [("std", STANDARD_ALPHA), ("kryp", KRYPTOS_ALPHA)]:
        keyed = make_keyed_alphabet(alpha_kw, base_alpha)
        partial = generate_indicator_keys_from_cribs(keyed)
        known = sum(1 for k in partial if k is not None)
        
        # Fill missing with brute force over 26^5 = ~12M possibilities
        # Too many for full brute force, but we can try common letters
        # For efficiency: try all 26 values for each of 5 unknown positions
        # but score after each, keeping best
        
        missing_list = sorted(missing)
        
        # Quick test: fill with each single letter
        best_score = -9999
        best_fill = None
        best_pt = None
        
        for fill_idx in range(26):
            fill_char = base_alpha[fill_idx]
            full_key = list(partial)
            for m in missing_list:
                full_key[m] = fill_char
            key_str = ''.join(k if k else '?' for k in full_key)
            
            pt = quagmire_III_decrypt(K4_CT, key_str, alpha_kw, PERIOD, base_alpha)
            score = quadgram_score(pt)
            
            if score > best_score:
                best_score = score
                best_fill = fill_char
                best_pt = pt
                best_key = key_str
        
        if best_pt:
            test_and_record(
                f"Quag3 crib+fill alpha={alpha_kw} base={base_name} best_fill={best_fill}",
                best_pt, f"key={best_key} score={best_score:.1f}"
            )
        
        # Same for Beaufort
        partial_b = generate_beaufort_indicator_keys_from_cribs(keyed)
        
        best_score_b = -9999
        best_pt_b = None
        
        for fill_idx in range(26):
            fill_char = base_alpha[fill_idx]
            full_key = list(partial_b)
            for m in missing_list:
                full_key[m] = fill_char
            key_str = ''.join(k if k else '?' for k in full_key)
            
            pt = beaufort_keyed_decrypt(K4_CT, key_str, alpha_kw, PERIOD, base_alpha)
            score = quadgram_score(pt)
            
            if score > best_score_b:
                best_score_b = score
                best_pt_b = pt
                best_key_b = key_str
        
        if best_pt_b:
            test_and_record(
                f"Beaufort crib+fill alpha={alpha_kw} base={base_name}",
                best_pt_b, f"key={best_key_b} score={best_score_b:.1f}"
            )


# ============================================================
# TEST 7: BRUTE FORCE 5 UNKNOWN KEY POSITIONS (Quag III, best configs)
# ============================================================
print("\n" + "="*70)
print("TEST 7: BRUTE FORCE 5 UNKNOWN KEY POSITIONS")
print("="*70)

# Only do this for the most promising configurations
# With 26^5 ≈ 12M, we need to be strategic. 
# Use a hill-climbing approach: optimize one position at a time.

for alpha_kw in ["KRYPTOS"]:
    for base_name, base_alpha in [("kryp", KRYPTOS_ALPHA), ("std", STANDARD_ALPHA)]:
        keyed = make_keyed_alphabet(alpha_kw, base_alpha)
        
        for cipher_name, decrypt_func in [
            ("Quag3", lambda ct, key: quagmire_III_decrypt(ct, key, alpha_kw, PERIOD, base_alpha)),
            ("Beaufort", lambda ct, key: beaufort_keyed_decrypt(ct, key, alpha_kw, PERIOD, base_alpha)),
            ("VarBeaufort", lambda ct, key: variant_beaufort_keyed_decrypt(ct, key, alpha_kw, PERIOD, base_alpha)),
        ]:
            # Get crib-derived key
            if cipher_name == "Beaufort":
                partial = generate_beaufort_indicator_keys_from_cribs(keyed)
            elif cipher_name == "Quag3":
                partial = generate_indicator_keys_from_cribs(keyed)
            else:
                # Variant Beaufort: key = ct - pt
                partial_vb = [None] * PERIOD
                for crib_text, crib_pos in [CRIB_BERLIN, CRIB_EASTNORTHEAST]:
                    for i, (c, p) in enumerate(zip(K4_CT[crib_pos:crib_pos+len(crib_text)], crib_text)):
                        kpos = (crib_pos + i) % PERIOD
                        if c in keyed and p in keyed:
                            c_idx = keyed.index(c)
                            p_idx = keyed.index(p)
                            k_idx = (c_idx - p_idx) % len(base_alpha)
                            partial_vb[kpos] = keyed[k_idx]
                partial = partial_vb
            
            missing_list = sorted(missing)
            
            # Hill climbing: iterate through unknown positions, try all 26 values each
            current_key = list(partial)
            for m in missing_list:
                current_key[m] = base_alpha[0]  # initialize
            
            for iteration in range(5):  # 5 rounds of hill climbing
                improved = False
                for m in missing_list:
                    best_score = -9999
                    best_char = current_key[m]
                    for ci in range(26):
                        current_key[m] = base_alpha[ci]
                        key_str = ''.join(k for k in current_key)
                        pt = decrypt_func(K4_CT, key_str)
                        score = quadgram_score(pt)
                        if score > best_score:
                            best_score = score
                            best_char = base_alpha[ci]
                    current_key[m] = best_char
                    improved = True
            
            key_str = ''.join(k for k in current_key)
            pt = decrypt_func(K4_CT, key_str)
            score = quadgram_score(pt)
            
            test_and_record(
                f"{cipher_name} hill-climb alpha={alpha_kw} base={base_name}",
                pt, f"key={key_str} score={score:.1f}"
            )
            print(f"  {cipher_name} alpha={alpha_kw} base={base_name}: score={score:.1f}")
            print(f"    key={key_str}")
            print(f"    pt={pt}")


# ============================================================
# TEST 8: QUAGMIRE I and II for completeness
# ============================================================
print("\n" + "="*70)
print("TEST 8: QUAGMIRE I AND II")
print("="*70)

for alpha_kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
    for base_name, base_alpha in [("std", STANDARD_ALPHA), ("kryp", KRYPTOS_ALPHA)]:
        for ind in ["PALIMPSEST", "ABSCISSA", "KRYPTOS", "BERLIN"]:
            ind_key = (ind * ((PERIOD // len(ind)) + 1))[:PERIOD]
            
            # Quagmire I
            pt = quagmire_I_decrypt(K4_CT, ind_key, alpha_kw, PERIOD, base_alpha)
            test_and_record(
                f"Quag1 base={base_name} pt_kw={alpha_kw} ind={ind}",
                pt, f"pt_kw={alpha_kw} ind={ind_key}"
            )
            
            # Quagmire II
            pt = quagmire_II_decrypt(K4_CT, ind_key, alpha_kw, PERIOD, base_alpha)
            test_and_record(
                f"Quag2 base={base_name} ct_kw={alpha_kw} ind={ind}",
                pt, f"ct_kw={alpha_kw} ind={ind_key}"
            )


# ============================================================
# TEST 9: EXHAUSTIVE 26^5 BRUTE FORCE (most promising config)
# ============================================================
print("\n" + "="*70)
print("TEST 9: EXHAUSTIVE 26^5 BRUTE FORCE for Quag III KRYPTOS/KRYPTOS-base")
print("="*70)

# This tests all ~12M combinations for the 5 unknown positions.
# Focus on the single most promising configuration.

alpha_kw = "KRYPTOS"
base_alpha = KRYPTOS_ALPHA
keyed = make_keyed_alphabet(alpha_kw, base_alpha)
partial = generate_indicator_keys_from_cribs(keyed)
missing_list = sorted(missing)

print(f"  Keyed alphabet: {keyed}")
print(f"  Partial key: {''.join(k if k else '?' for k in partial)}")
print(f"  Missing positions: {missing_list}")
print(f"  Brute forcing {26**5} = {26**5} combinations...")

best_results = []  # Keep top 20

import time
start = time.time()
count = 0
TOTAL = 26**5

for a in range(26):
    for b in range(26):
        for c in range(26):
            for d in range(26):
                for e in range(26):
                    count += 1
                    key_list = list(partial)
                    key_list[missing_list[0]] = base_alpha[a]
                    key_list[missing_list[1]] = base_alpha[b]
                    key_list[missing_list[2]] = base_alpha[c]
                    key_list[missing_list[3]] = base_alpha[d]
                    key_list[missing_list[4]] = base_alpha[e]
                    key_str = ''.join(k for k in key_list)
                    
                    pt = quagmire_III_decrypt(K4_CT, key_str, alpha_kw, PERIOD, base_alpha)
                    score = quadgram_score(pt)
                    
                    if len(best_results) < 20 or score > best_results[-1][0]:
                        best_results.append((score, key_str, pt))
                        best_results.sort(key=lambda x: -x[0])
                        best_results = best_results[:20]
                    
                    if count % 1000000 == 0:
                        elapsed = time.time() - start
                        rate = count / elapsed
                        remaining = (TOTAL - count) / rate
                        print(f"  Progress: {count}/{TOTAL} ({100*count/TOTAL:.1f}%) "
                              f"rate={rate:.0f}/s ETA={remaining:.0f}s "
                              f"best={best_results[0][0]:.1f}")

elapsed = time.time() - start
print(f"\n  Completed {TOTAL} combinations in {elapsed:.1f}s")

print("\n  TOP 20 RESULTS (Quag III, KRYPTOS keyed, KRYPTOS base):")
for i, (score, key, pt) in enumerate(best_results):
    words = count_english_words(pt)
    cribs = check_cribs(pt)
    berlin_m = cribs.get("BERLINCLOCK", (0,0,""))[0]
    ene_m = cribs.get("EASTNORTHEAST", (0,0,""))[0]
    print(f"  #{i+1}: score={score:.1f} key={key}")
    print(f"       pt={pt}")
    print(f"       BERLIN={berlin_m}/11 ENE={ene_m}/13 words={[w for _,w in words[:5]]}")
    
    test_and_record(f"BRUTE Quag3 rank#{i+1}", pt, f"key={key}")


# Also do exhaustive for Beaufort keyed with KRYPTOS
print("\n  Now brute forcing Beaufort keyed KRYPTOS/KRYPTOS-base...")
partial_b = generate_beaufort_indicator_keys_from_cribs(keyed)
best_beaufort = []

start = time.time()
count = 0

for a in range(26):
    for b in range(26):
        for c in range(26):
            for d in range(26):
                for e in range(26):
                    count += 1
                    key_list = list(partial_b)
                    key_list[missing_list[0]] = base_alpha[a]
                    key_list[missing_list[1]] = base_alpha[b]
                    key_list[missing_list[2]] = base_alpha[c]
                    key_list[missing_list[3]] = base_alpha[d]
                    key_list[missing_list[4]] = base_alpha[e]
                    key_str = ''.join(k for k in key_list)
                    
                    pt = beaufort_keyed_decrypt(K4_CT, key_str, alpha_kw, PERIOD, base_alpha)
                    score = quadgram_score(pt)
                    
                    if len(best_beaufort) < 20 or score > best_beaufort[-1][0]:
                        best_beaufort.append((score, key_str, pt))
                        best_beaufort.sort(key=lambda x: -x[0])
                        best_beaufort = best_beaufort[:20]
                    
                    if count % 1000000 == 0:
                        elapsed = time.time() - start
                        rate = count / elapsed
                        remaining = (TOTAL - count) / rate
                        print(f"  Progress: {count}/{TOTAL} ({100*count/TOTAL:.1f}%) "
                              f"rate={rate:.0f}/s ETA={remaining:.0f}s "
                              f"best={best_beaufort[0][0]:.1f}")

elapsed = time.time() - start
print(f"\n  Completed {TOTAL} Beaufort combinations in {elapsed:.1f}s")

print("\n  TOP 20 RESULTS (Beaufort keyed KRYPTOS, KRYPTOS base):")
for i, (score, key, pt) in enumerate(best_beaufort):
    words = count_english_words(pt)
    cribs = check_cribs(pt)
    berlin_m = cribs.get("BERLINCLOCK", (0,0,""))[0]
    ene_m = cribs.get("EASTNORTHEAST", (0,0,""))[0]
    print(f"  #{i+1}: score={score:.1f} key={key}")
    print(f"       pt={pt}")
    print(f"       BERLIN={berlin_m}/11 ENE={ene_m}/13 words={[w for _,w in words[:5]]}")
    
    test_and_record(f"BRUTE Beaufort rank#{i+1}", pt, f"key={key}")


# Also do exhaustive for standard alphabet Quag III
print("\n  Now brute forcing Quag III KRYPTOS/standard-base...")
keyed_std = make_keyed_alphabet("KRYPTOS", STANDARD_ALPHA)
partial_std = generate_indicator_keys_from_cribs(keyed_std)
best_std = []

start = time.time()
count = 0

for a in range(26):
    for b in range(26):
        for c in range(26):
            for d in range(26):
                for e in range(26):
                    count += 1
                    key_list = list(partial_std)
                    key_list[missing_list[0]] = STANDARD_ALPHA[a]
                    key_list[missing_list[1]] = STANDARD_ALPHA[b]
                    key_list[missing_list[2]] = STANDARD_ALPHA[c]
                    key_list[missing_list[3]] = STANDARD_ALPHA[d]
                    key_list[missing_list[4]] = STANDARD_ALPHA[e]
                    key_str = ''.join(k for k in key_list)
                    
                    pt = quagmire_III_decrypt(K4_CT, key_str, "KRYPTOS", PERIOD, STANDARD_ALPHA)
                    score = quadgram_score(pt)
                    
                    if len(best_std) < 20 or score > best_std[-1][0]:
                        best_std.append((score, key_str, pt))
                        best_std.sort(key=lambda x: -x[0])
                        best_std = best_std[:20]
                    
                    if count % 1000000 == 0:
                        elapsed = time.time() - start
                        rate = count / elapsed
                        remaining = (TOTAL - count) / rate
                        print(f"  Progress: {count}/{TOTAL} ({100*count/TOTAL:.1f}%) "
                              f"rate={rate:.0f}/s ETA={remaining:.0f}s "
                              f"best={best_std[0][0]:.1f}")

elapsed = time.time() - start
print(f"\n  Completed {TOTAL} Quag3-std combinations in {elapsed:.1f}s")

print("\n  TOP 20 RESULTS (Quag III, KRYPTOS keyed, standard base):")
for i, (score, key, pt) in enumerate(best_std):
    words = count_english_words(pt)
    cribs = check_cribs(pt)
    berlin_m = cribs.get("BERLINCLOCK", (0,0,""))[0]
    ene_m = cribs.get("EASTNORTHEAST", (0,0,""))[0]
    print(f"  #{i+1}: score={score:.1f} key={key}")
    print(f"       pt={pt}")
    print(f"       BERLIN={berlin_m}/11 ENE={ene_m}/13 words={[w for _,w in words[:5]]}")


# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "="*70)
print("FINAL SUMMARY - TOP 50 RESULTS ACROSS ALL METHODS")
print("="*70)

# Sort all results by score
results.sort(key=lambda x: -x['score'])

for i, r in enumerate(results[:50]):
    print(f"\n#{i+1}: {r['name']}")
    print(f"  Score: {r['score']:.1f}")
    print(f"  Key: {r['key_info']}")
    print(f"  PT: {r['plaintext']}")
    print(f"  BERLINCLOCK match: {r['berlin_match']}/11  EASTNORTHEAST match: {r['ene_match']}/13")
    if r['berlin_found'] >= 0:
        print(f"  *** BERLINCLOCK FOUND at position {r['berlin_found']}! ***")
    if r['ene_found'] >= 0:
        print(f"  *** EASTNORTHEAST FOUND at position {r['ene_found']}! ***")
    if r['words']:
        print(f"  Words: {r['words'][:8]}")

# Check if any result actually contains the cribs
crib_hits = [r for r in results if r['berlin_found'] >= 0 or r['ene_found'] >= 0]
if crib_hits:
    print(f"\n{'='*70}")
    print(f"*** {len(crib_hits)} RESULTS CONTAIN ACTUAL CRIB TEXT ***")
    print(f"{'='*70}")
    for r in crib_hits:
        print(f"  {r['name']}: {r['plaintext']}")
else:
    print(f"\n  No results contained full crib text at any position.")

print(f"\nTotal configurations tested: {len(results)}")
print("Done.")
