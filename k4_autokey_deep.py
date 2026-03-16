#!/usr/bin/env python3
"""
K4 Autokey Deep Analysis

CRITICAL INSIGHT: The two K4 cribs (EASTNORTHEAST@21 and BERLINCLOCK@63) cover
COMPLETELY DISJOINT key positions mod 29. This means the period-29 assumption
has NEVER been cross-validated!

What if the cipher is actually an AUTOKEY Vigenere where the key is extended
using the plaintext (or ciphertext)?

We test:
  1. PLAINTEXT AUTOKEY (Vigenere variant): key[i] = PT[i-P] for i >= P
  2. CIPHERTEXT AUTOKEY (Vigenere variant): key[i] = CT[i-P] for i >= P
  3. BEAUFORT AUTOKEY (plaintext): PT[i] = (key[i] - CT[i]) mod 26
  4. BEAUFORT AUTOKEY (ciphertext): PT[i] = (key[i] - CT[i]) mod 26, key[i]=CT[i-P]

For both KRYPTOS and STANDARD alphabets.
"""

import math
import itertools
import sys
from collections import defaultdict

# ============================================================================
# CONSTANTS
# ============================================================================
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
K4_LEN = len(K4)  # 97

KRYPTOS = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known cribs
CRIB_ENE = ("EASTNORTHEAST", 21)   # positions 21-33
CRIB_BC  = ("BERLINCLOCK", 63)     # positions 63-73

# ============================================================================
# LOAD QUADGRAMS
# ============================================================================
print("Loading quadgrams...")
QUADGRAMS = {}
QG_TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            QG_TOTAL += count

QG_LOG = {}
LOG_TOTAL = math.log10(QG_TOTAL)
for gram, count in QUADGRAMS.items():
    QG_LOG[gram] = math.log10(count) - LOG_TOTAL

# Floor value for unknown quadgrams
QG_FLOOR = math.log10(0.01) - LOG_TOTAL


def quadgram_score(text):
    """Score text using log10 quadgram frequencies."""
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QG_LOG.get(qg, QG_FLOOR)
    return score


def normalized_qg_score(text):
    """Score per character for comparison across different lengths."""
    if len(text) < 4:
        return QG_FLOOR
    return quadgram_score(text) / (len(text) - 3)


# ============================================================================
# CIPHER OPERATIONS
# ============================================================================
def char_to_idx(c, alpha):
    return alpha.index(c)


def idx_to_char(i, alpha):
    return alpha[i % len(alpha)]


def vigenere_decrypt_char(ct_char, key_char, alpha):
    """Standard Vigenere: PT = (CT - KEY) mod N"""
    n = len(alpha)
    return alpha[(alpha.index(ct_char) - alpha.index(key_char)) % n]


def beaufort_decrypt_char(ct_char, key_char, alpha):
    """Beaufort: PT = (KEY - CT) mod N"""
    n = len(alpha)
    return alpha[(alpha.index(key_char) - alpha.index(ct_char)) % n]


# ============================================================================
# PLAINTEXT AUTOKEY DECRYPTION
# ============================================================================
def pt_autokey_decrypt(ct, keyword, alpha, beaufort=False):
    """
    Plaintext autokey decryption.
    key[0..P-1] = keyword
    key[i] = PT[i-P] for i >= P

    For Vigenere: PT[i] = (CT[i] - key[i]) mod N
    For Beaufort: PT[i] = (key[i] - CT[i]) mod N
    """
    P = len(keyword)
    n = len(alpha)
    pt = []

    for i in range(len(ct)):
        if i < P:
            key_char = keyword[i]
        else:
            key_char = pt[i - P]

        if beaufort:
            pt_char = beaufort_decrypt_char(ct[i], key_char, alpha)
        else:
            pt_char = vigenere_decrypt_char(ct[i], key_char, alpha)
        pt.append(pt_char)

    return ''.join(pt)


# ============================================================================
# CIPHERTEXT AUTOKEY DECRYPTION
# ============================================================================
def ct_autokey_decrypt(ct, keyword, alpha, beaufort=False):
    """
    Ciphertext autokey decryption.
    key[0..P-1] = keyword
    key[i] = CT[i-P] for i >= P

    Key is fully determined by CT + keyword!
    """
    P = len(keyword)
    n = len(alpha)
    pt = []

    for i in range(len(ct)):
        if i < P:
            key_char = keyword[i]
        else:
            key_char = ct[i - P]

        if beaufort:
            pt_char = beaufort_decrypt_char(ct[i], key_char, alpha)
        else:
            pt_char = vigenere_decrypt_char(ct[i], key_char, alpha)
        pt.append(pt_char)

    return ''.join(pt)


# ============================================================================
# PLAINTEXT AUTOKEY: DERIVE KEY FROM CRIBS
# ============================================================================
def derive_pt_autokey_key_from_crib(crib_text, crib_pos, ct, keyword_len, alpha, beaufort=False):
    """
    Given a known plaintext crib at a known position, derive what the
    autokey key must be, and propagate constraints backward.

    Returns: dict of {position: known_key_char} and {position: known_pt_char}
    """
    P = keyword_len
    n = len(alpha)

    known_pt = {}   # position -> plaintext char
    known_key = {}  # position -> key char

    # First, we know the plaintext at the crib positions
    for j, c in enumerate(crib_text):
        known_pt[crib_pos + j] = c

    # From PT at crib positions, derive key at those positions
    for j in range(len(crib_text)):
        pos = crib_pos + j
        ct_char = ct[pos]
        pt_char = crib_text[j]

        # Derive key[pos]: CT[pos] = PT[pos] + key[pos] (Vigenere encrypt)
        # So key[pos] = (CT[pos] - PT[pos]) mod N
        if beaufort:
            # Beaufort: CT = (KEY - PT) mod N => KEY = (CT + PT) mod N
            key_idx = (alpha.index(ct_char) + alpha.index(pt_char)) % n
        else:
            # Vigenere: CT = (PT + KEY) mod N => KEY = (CT - PT) mod N
            key_idx = (alpha.index(ct_char) - alpha.index(pt_char)) % n
        known_key[pos] = alpha[key_idx]

    # Now propagate: key[pos] = PT[pos - P] for pos >= P
    # So if we know key[pos] and pos >= P: PT[pos - P] = key[pos]
    # Also if we know PT[pos]: key[pos + P] = PT[pos]

    changed = True
    iterations = 0
    while changed and iterations < 200:
        changed = False
        iterations += 1

        # From known key -> known PT (backward propagation)
        for pos in list(known_key.keys()):
            if pos >= P:
                pt_pos = pos - P
                if pt_pos not in known_pt:
                    known_pt[pt_pos] = known_key[pos]
                    changed = True

        # From known PT -> known key (forward propagation)
        for pos in list(known_pt.keys()):
            key_pos = pos + P
            if key_pos < len(ct) and key_pos not in known_key:
                known_key[key_pos] = known_pt[pos]
                changed = True

        # From known PT, derive key at that position
        for pos in list(known_pt.keys()):
            if pos not in known_key and pos < len(ct):
                ct_char = ct[pos]
                pt_char = known_pt[pos]
                if beaufort:
                    key_idx = (alpha.index(ct_char) + alpha.index(pt_char)) % n
                else:
                    key_idx = (alpha.index(ct_char) - alpha.index(pt_char)) % n
                known_key[pos] = alpha[key_idx]
                changed = True

        # From known key at position, derive PT
        for pos in list(known_key.keys()):
            if pos not in known_pt and pos < len(ct):
                ct_char = ct[pos]
                key_char = known_key[pos]
                if beaufort:
                    pt_char = beaufort_decrypt_char(ct_char, key_char, alpha)
                else:
                    pt_char = vigenere_decrypt_char(ct_char, key_char, alpha)
                known_pt[pos] = pt_char
                changed = True

    return known_key, known_pt


# ============================================================================
# MAIN ANALYSIS
# ============================================================================
print(f"K4 length: {K4_LEN}")
print(f"K4: {K4}")
print(f"KRYPTOS alphabet: {KRYPTOS} (len={len(KRYPTOS)})")
print(f"STANDARD alphabet: {STANDARD} (len={len(STANDARD)})")
print(f"\nCrib 1: '{CRIB_ENE[0]}' at position {CRIB_ENE[1]} (positions {CRIB_ENE[1]}-{CRIB_ENE[1]+len(CRIB_ENE[0])-1})")
print(f"Crib 2: '{CRIB_BC[0]}' at position {CRIB_BC[1]} (positions {CRIB_BC[1]}-{CRIB_BC[1]+len(CRIB_BC[0])-1})")

# Global results collector
ALL_RESULTS = []

# ============================================================================
# PART 1: PLAINTEXT AUTOKEY WITH CRIB PROPAGATION
# ============================================================================
print("\n" + "="*80)
print("PART 1: PLAINTEXT AUTOKEY - CRIB PROPAGATION ANALYSIS")
print("="*80)

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"
        print(f"\n--- {mode} Plaintext Autokey with {alpha_name} alphabet ---")

        for P in range(1, 51):
            # Derive constraints from BOTH cribs
            key1, pt1 = derive_pt_autokey_key_from_crib(
                CRIB_ENE[0], CRIB_ENE[1], K4, P, alpha, beaufort)
            key2, pt2 = derive_pt_autokey_key_from_crib(
                CRIB_BC[0], CRIB_BC[1], K4, P, alpha, beaufort)

            # Check consistency between the two cribs
            consistent = True
            conflict_details = []
            for pos in set(pt1.keys()) & set(pt2.keys()):
                if pt1[pos] != pt2[pos]:
                    consistent = False
                    conflict_details.append(
                        f"  PT conflict at pos {pos}: crib1 says '{pt1[pos]}', crib2 says '{pt2[pos]}'")

            for pos in set(key1.keys()) & set(key2.keys()):
                if key1[pos] != key2[pos]:
                    consistent = False
                    conflict_details.append(
                        f"  KEY conflict at pos {pos}: crib1 says '{key1[pos]}', crib2 says '{key2[pos]}'")

            if not consistent:
                continue  # Skip inconsistent keyword lengths

            # Merge constraints
            merged_pt = {**pt1, **pt2}
            merged_key = {**key1, **key2}

            # How many keyword positions (0..P-1) are determined?
            known_keyword_positions = {pos: merged_key[pos] for pos in range(P) if pos in merged_key}
            unknown_keyword_positions = [pos for pos in range(P) if pos not in merged_key]

            # How many total PT positions are known?
            total_known_pt = len(merged_pt)

            # If all keyword positions are known, we can fully decrypt
            if len(unknown_keyword_positions) == 0:
                keyword = ''.join(merged_key[i] for i in range(P))
                pt_full = pt_autokey_decrypt(K4, keyword, alpha, beaufort)
                score = quadgram_score(pt_full)
                norm_score = normalized_qg_score(pt_full)

                # Verify cribs are present
                has_ene = pt_full[CRIB_ENE[1]:CRIB_ENE[1]+len(CRIB_ENE[0])] == CRIB_ENE[0]
                has_bc = pt_full[CRIB_BC[1]:CRIB_BC[1]+len(CRIB_BC[0])] == CRIB_BC[0]

                if has_ene and has_bc:
                    result_label = f"{mode}_PT_AUTOKEY_{alpha_name}_P{P}"
                    ALL_RESULTS.append((score, norm_score, result_label, keyword, pt_full))
                    if norm_score > -9.0:
                        print(f"  P={P}: keyword='{keyword}' norm_score={norm_score:.4f}")
                        print(f"    PT: {pt_full[:70]}...")

            elif len(unknown_keyword_positions) <= 6 and len(unknown_keyword_positions) > 0:
                # Brute force the unknown positions
                n_unknown = len(unknown_keyword_positions)
                n_alpha = len(alpha)

                # For efficiency, limit brute force
                if n_alpha ** n_unknown > 5_000_000:
                    # Too many combinations, skip or sample
                    if P <= 21:
                        print(f"  P={P}: {n_unknown} unknown keyword positions, {len(known_keyword_positions)} known - TOO LARGE to brute force ({n_alpha}^{n_unknown})")
                    continue

                best_for_P = None
                count = 0

                for combo in itertools.product(range(n_alpha), repeat=n_unknown):
                    # Build keyword
                    keyword_chars = [''] * P
                    for pos, ch in known_keyword_positions.items():
                        keyword_chars[pos] = ch
                    for idx, pos in enumerate(unknown_keyword_positions):
                        keyword_chars[pos] = alpha[combo[idx]]
                    keyword = ''.join(keyword_chars)

                    pt_full = pt_autokey_decrypt(K4, keyword, alpha, beaufort)

                    # Quick check: do both cribs appear?
                    if pt_full[CRIB_ENE[1]:CRIB_ENE[1]+len(CRIB_ENE[0])] != CRIB_ENE[0]:
                        continue
                    if pt_full[CRIB_BC[1]:CRIB_BC[1]+len(CRIB_BC[0])] != CRIB_BC[0]:
                        continue

                    score = quadgram_score(pt_full)
                    norm_score = normalized_qg_score(pt_full)

                    if best_for_P is None or score > best_for_P[0]:
                        best_for_P = (score, norm_score, keyword, pt_full)

                    result_label = f"{mode}_PT_AUTOKEY_{alpha_name}_P{P}"
                    ALL_RESULTS.append((score, norm_score, result_label, keyword, pt_full))
                    count += 1

                if best_for_P and best_for_P[1] > -9.5:
                    print(f"  P={P}: best keyword='{best_for_P[2]}' norm_score={best_for_P[1]:.4f} ({count} valid combos)")
                    print(f"    PT: {best_for_P[3][:70]}...")

            else:
                # Report how constrained this keyword length is
                if total_known_pt > 40 and P <= 21:
                    print(f"  P={P}: {len(known_keyword_positions)}/{P} keyword chars known, "
                          f"{total_known_pt}/{K4_LEN} PT chars known, "
                          f"{len(unknown_keyword_positions)} unknown keyword positions")


# ============================================================================
# PART 2: CIPHERTEXT AUTOKEY (key fully determined from CT)
# ============================================================================
print("\n" + "="*80)
print("PART 2: CIPHERTEXT AUTOKEY - BRUTE FORCE KEYWORD")
print("="*80)
print("In ciphertext autokey, key[i] = CT[i-P] for i >= P")
print("So the key is fully determined except for the first P positions (the keyword)")
print("We brute-force keyword for P <= 8\n")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"
        print(f"\n--- {mode} Ciphertext Autokey with {alpha_name} alphabet ---")

        for P in range(1, 9):
            n_alpha = len(alpha)
            total_combos = n_alpha ** P

            # For P > 5 with 26-letter alphabet, we need a smarter approach
            # Use the cribs to constrain the keyword first

            # In CT autokey, the key at position i (for i >= P) is CT[i-P]
            # which is known. So the only unknowns are keyword[0..P-1].

            # From the EASTNORTHEAST crib at position 21:
            # PT[21..33] = EASTNORTHEAST
            # For positions 21..33: if pos >= P, key[pos] = CT[pos-P] (known)
            # So PT[pos] is determined for pos >= P
            # We can derive what keyword chars are needed for pos < P

            # For the ENE crib at pos 21-33:
            # key[pos] = keyword[pos] if pos < P, else CT[pos-P]
            # Vigenere: PT[pos] = (CT[pos] - key[pos]) mod N
            # So: keyword[pos] = (CT[pos] - PT[pos]) mod N for pos < P and pos in [21..33]
            # But positions 21..33 are all >= P when P <= 8, so key = CT[pos-P] there

            # Let's just check: for P <= 8, positions 21+ all have key = CT[pos-P]
            # So the ENE crib constrains nothing in the keyword directly...
            # BUT we can use it to verify: does decryption with key=CT[pos-P] give
            # EASTNORTHEAST at positions 21-33?

            # Check if the known-CT-derived key at crib positions gives correct crib
            crib_ok_ene = True
            crib_ok_bc = True

            for j, expected_pt in enumerate(CRIB_ENE[0]):
                pos = CRIB_ENE[1] + j
                if pos >= P:
                    key_char = K4[pos - P]
                    if beaufort:
                        got = beaufort_decrypt_char(K4[pos], key_char, alpha)
                    else:
                        got = vigenere_decrypt_char(K4[pos], key_char, alpha)
                    if got != expected_pt:
                        crib_ok_ene = False
                        break

            for j, expected_pt in enumerate(CRIB_BC[0]):
                pos = CRIB_BC[1] + j
                if pos >= P:
                    key_char = K4[pos - P]
                    if beaufort:
                        got = beaufort_decrypt_char(K4[pos], key_char, alpha)
                    else:
                        got = vigenere_decrypt_char(K4[pos], key_char, alpha)
                    if got != expected_pt:
                        crib_ok_bc = False
                        break

            if not crib_ok_ene:
                print(f"  P={P}: ENE crib FAILS with CT-derived key - skipping")
                continue
            if not crib_ok_bc:
                print(f"  P={P}: BC crib FAILS with CT-derived key - skipping")
                continue

            print(f"  P={P}: Both cribs consistent with CT autokey! Brute-forcing {total_combos} keywords...")

            if total_combos > 10_000_000:
                print(f"    Too many combinations ({total_combos}), skipping")
                continue

            best_score = -float('inf')
            best_keyword = None
            best_pt = None
            candidates_checked = 0

            for combo in itertools.product(range(n_alpha), repeat=P):
                keyword = ''.join(alpha[c] for c in combo)
                pt_full = ct_autokey_decrypt(K4, keyword, alpha, beaufort)
                score = quadgram_score(pt_full)
                candidates_checked += 1

                if score > best_score:
                    best_score = score
                    best_keyword = keyword
                    best_pt = pt_full

                    norm = normalized_qg_score(pt_full)
                    result_label = f"{mode}_CT_AUTOKEY_{alpha_name}_P{P}"
                    ALL_RESULTS.append((score, norm, result_label, keyword, pt_full))

            if best_pt:
                norm = normalized_qg_score(best_pt)
                print(f"    Best: keyword='{best_keyword}' norm_score={norm:.4f}")
                print(f"    PT: {best_pt[:70]}...")

                # Also show top 5 for this P
                # Re-collect for sorting
                p_results = []
                for combo in itertools.product(range(n_alpha), repeat=P):
                    keyword = ''.join(alpha[c] for c in combo)
                    pt_full = ct_autokey_decrypt(K4, keyword, alpha, beaufort)
                    score = quadgram_score(pt_full)
                    p_results.append((score, keyword, pt_full))

                p_results.sort(key=lambda x: -x[0])
                print(f"    Top 3:")
                for rank, (sc, kw, pt) in enumerate(p_results[:3]):
                    ns = normalized_qg_score(pt)
                    print(f"      {rank+1}. kw='{kw}' norm={ns:.4f} PT={pt[:60]}...")


# ============================================================================
# PART 3: SPECIAL ANALYSIS - WHAT KEYWORD LENGTHS ARE CONSISTENT?
# ============================================================================
print("\n" + "="*80)
print("PART 3: CONSISTENCY ANALYSIS - WHICH KEYWORD LENGTHS WORK?")
print("="*80)
print("For each keyword length P, check if both cribs can be simultaneously")
print("satisfied by a plaintext autokey cipher.\n")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"
        print(f"\n--- {mode} Plaintext Autokey with {alpha_name} alphabet ---")

        consistent_Ps = []

        for P in range(1, 51):
            key1, pt1 = derive_pt_autokey_key_from_crib(
                CRIB_ENE[0], CRIB_ENE[1], K4, P, alpha, beaufort)
            key2, pt2 = derive_pt_autokey_key_from_crib(
                CRIB_BC[0], CRIB_BC[1], K4, P, alpha, beaufort)

            # Check consistency
            consistent = True
            for pos in set(pt1.keys()) & set(pt2.keys()):
                if pt1[pos] != pt2[pos]:
                    consistent = False
                    break
            if consistent:
                for pos in set(key1.keys()) & set(key2.keys()):
                    if key1[pos] != key2[pos]:
                        consistent = False
                        break

            if consistent:
                merged_pt = {**pt1, **pt2}
                merged_key = {**key1, **key2}
                known_kw = sum(1 for i in range(P) if i in merged_key)
                unknown_kw = P - known_kw
                consistent_Ps.append((P, len(merged_pt), known_kw, unknown_kw))

        print(f"  Consistent keyword lengths: {len(consistent_Ps)}")
        for P, npt, nkw_known, nkw_unknown in consistent_Ps:
            marker = " <-- FULLY DETERMINED" if nkw_unknown == 0 else ""
            if nkw_unknown <= 4:
                marker += " <-- FEASIBLE BRUTE FORCE"
            print(f"    P={P:2d}: {npt:2d}/{K4_LEN} PT known, "
                  f"{nkw_known}/{P} keyword known, {nkw_unknown} unknown{marker}")


# ============================================================================
# PART 4: EXTENDED CIPHERTEXT AUTOKEY WITH LARGER KEYWORD
# ============================================================================
print("\n" + "="*80)
print("PART 4: CIPHERTEXT AUTOKEY - CRIB-CONSTRAINED SEARCH FOR P=9..20")
print("="*80)
print("For P > 8, brute force is too large. Use cribs to constrain.\n")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"
        n_alpha = len(alpha)

        for P in range(9, 22):
            # In CT autokey with keyword length P:
            # key[i] = keyword[i] for i < P
            # key[i] = CT[i-P] for i >= P

            # For ENE crib at pos 21-33:
            # Positions where keyword is used: pos < P => max pos = P-1
            # For P <= 21: all crib positions (21-33) have key = CT[pos-P]
            # For P = 22..33: some crib positions use keyword

            # Constraint: From each crib position where key = CT[pos-P],
            # the decryption must give the expected PT char

            # First check if CT-derived portions of key are consistent with cribs
            constraints = {}  # keyword_pos -> required_char
            crib_consistent = True

            for crib_text, crib_pos in [(CRIB_ENE[0], CRIB_ENE[1]), (CRIB_BC[0], CRIB_BC[1])]:
                for j, expected_pt in enumerate(crib_text):
                    pos = crib_pos + j

                    if pos >= P:
                        # Key is CT[pos-P], fully determined
                        key_char = K4[pos - P]
                        if beaufort:
                            got = beaufort_decrypt_char(K4[pos], key_char, alpha)
                        else:
                            got = vigenere_decrypt_char(K4[pos], key_char, alpha)
                        if got != expected_pt:
                            crib_consistent = False
                            break
                    else:
                        # Key is keyword[pos], need to determine it
                        # Vigenere: PT = (CT - KEY) mod N => KEY = (CT - PT) mod N
                        # Beaufort: PT = (KEY - CT) mod N => KEY = (CT + PT) mod N
                        if beaufort:
                            req_key = alpha[(alpha.index(K4[pos]) + alpha.index(expected_pt)) % n_alpha]
                        else:
                            req_key = alpha[(alpha.index(K4[pos]) - alpha.index(expected_pt)) % n_alpha]

                        if pos in constraints:
                            if constraints[pos] != req_key:
                                crib_consistent = False
                                break
                        else:
                            constraints[pos] = req_key

                if not crib_consistent:
                    break

            if not crib_consistent:
                continue

            # How many keyword positions are constrained?
            known_kw_positions = set(constraints.keys())
            unknown_kw_positions = [i for i in range(P) if i not in known_kw_positions]
            n_unknown = len(unknown_kw_positions)

            if n_unknown > 6:
                # Too many unknowns to brute force; skip or sample
                continue

            total_combos = n_alpha ** n_unknown
            if total_combos > 5_000_000:
                continue

            print(f"  {mode} {alpha_name} P={P}: {len(known_kw_positions)} keyword chars constrained by cribs, "
                  f"{n_unknown} unknown, {total_combos} combos to search")

            best_score = -float('inf')
            best_keyword = None
            best_pt = None

            for combo in itertools.product(range(n_alpha), repeat=n_unknown):
                kw_chars = [''] * P
                for pos, ch in constraints.items():
                    kw_chars[pos] = ch
                for idx, pos in enumerate(unknown_kw_positions):
                    kw_chars[pos] = alpha[combo[idx]]
                keyword = ''.join(kw_chars)

                pt_full = ct_autokey_decrypt(K4, keyword, alpha, beaufort)
                score = quadgram_score(pt_full)

                if score > best_score:
                    best_score = score
                    best_keyword = keyword
                    best_pt = pt_full

            if best_pt:
                norm = normalized_qg_score(best_pt)
                result_label = f"{mode}_CT_AUTOKEY_{alpha_name}_P{P}"
                ALL_RESULTS.append((best_score, norm, result_label, best_keyword, best_pt))
                print(f"    Best: keyword='{best_keyword}' norm_score={norm:.4f}")
                print(f"    PT: {best_pt[:70]}...")


# ============================================================================
# PART 5: DICTIONARY KEYWORD SEARCH FOR PT AUTOKEY
# ============================================================================
print("\n" + "="*80)
print("PART 5: DICTIONARY KEYWORD SEARCH FOR PLAINTEXT AUTOKEY")
print("="*80)

DICTIONARY_WORDS = [
    # Kryptos-related
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "KOMITET",
    "SANBORN", "SCHEIDT", "CIA", "LANGLEY", "BERLIN", "CLOCK",
    "BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST", "EAST", "NORTH",
    "BETWEEN", "SUBTLE", "SHADING", "SHADOW", "UNDERGROUND",
    "DESPARATLY", "DESPERATELY", "BURIED", "HIDDEN", "SECRET",
    "INVISIBLE", "DIGETAL", "DIGITAL", "SLOWLY", "LIGHT", "LAYER",
    "MONUMENT", "SCULPTURE", "MAGNETIC", "COMPASS", "BEARING",
    "DEGREES", "MINUTES", "SECONDS", "LATITUDE", "LONGITUDE",
    "COORDINATES", "POSITION", "LOCATION", "AGENCY", "CENTRAL",
    "INTELLIGENCE", "VIRTUALLY", "IQLUSION", "ILLUSION",
    "LUCID", "MEMORY", "PASSAGE", "ADMIT", "TIME", "WEST",
    "SOUTH", "POINT", "LINE", "CURVE", "ENTRY",
    # Common short words
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "KEY", "END",
    "SOS", "WAR", "SPY", "CODE", "DATA",
    # Numbers as words
    "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN",
    "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE",
    # Combinations
    "KRYPTOSPALIMPSEST", "KRYPTOSABSCISSA", "PALIMPSESTABSCISSA",
    "KRYPTOSSHADOW", "SHADOWKRYPTOS",
]

# Also add two-word combinations of short words
SHORT_WORDS = ["KRYPTOS", "BERLIN", "CLOCK", "EAST", "NORTH", "SHADOW",
               "LIGHT", "LAYER", "KEY", "CIA", "SPY", "CODE", "WAR",
               "WEST", "SOUTH", "TIME", "END", "SOS", "POINT"]
for w1 in SHORT_WORDS:
    for w2 in SHORT_WORDS:
        combo = w1 + w2
        if len(combo) <= 20:
            DICTIONARY_WORDS.append(combo)

# Remove duplicates
DICTIONARY_WORDS = list(set(DICTIONARY_WORDS))
print(f"Testing {len(DICTIONARY_WORDS)} dictionary keywords...")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"

        for keyword in DICTIONARY_WORDS:
            # Check all chars are in alphabet
            if not all(c in alpha for c in keyword):
                continue

            pt = pt_autokey_decrypt(K4, keyword, alpha, beaufort)
            score = quadgram_score(pt)
            norm = normalized_qg_score(pt)

            # Check if either crib appears
            has_ene = CRIB_ENE[0] in pt
            has_bc = CRIB_BC[0] in pt

            result_label = f"{mode}_PT_AUTOKEY_{alpha_name}_P{len(keyword)}_DICT"
            ALL_RESULTS.append((score, norm, result_label, keyword, pt))

            if has_ene or has_bc:
                crib_info = []
                if has_ene:
                    crib_info.append(f"ENE@{pt.find(CRIB_ENE[0])}")
                if has_bc:
                    crib_info.append(f"BC@{pt.find(CRIB_BC[0])}")
                print(f"  {mode} {alpha_name} kw='{keyword}': {', '.join(crib_info)} norm={norm:.4f}")
                print(f"    PT: {pt[:70]}...")

        # Also try CT autokey with dictionary words
        for keyword in DICTIONARY_WORDS:
            if not all(c in alpha for c in keyword):
                continue

            pt = ct_autokey_decrypt(K4, keyword, alpha, beaufort)
            score = quadgram_score(pt)
            norm = normalized_qg_score(pt)

            has_ene = CRIB_ENE[0] in pt
            has_bc = CRIB_BC[0] in pt

            result_label = f"{mode}_CT_AUTOKEY_{alpha_name}_P{len(keyword)}_DICT"
            ALL_RESULTS.append((score, norm, result_label, keyword, pt))

            if has_ene or has_bc:
                crib_info = []
                if has_ene:
                    crib_info.append(f"ENE@{pt.find(CRIB_ENE[0])}")
                if has_bc:
                    crib_info.append(f"BC@{pt.find(CRIB_BC[0])}")
                print(f"  {mode} CT {alpha_name} kw='{keyword}': {', '.join(crib_info)} norm={norm:.4f}")
                print(f"    PT: {pt[:70]}...")


# ============================================================================
# PART 6: SPECIAL - PERIOD 29 AS AUTOKEY PRIMER LENGTH
# ============================================================================
print("\n" + "="*80)
print("PART 6: WHAT IF PERIOD 29 IS ACTUALLY THE AUTOKEY PRIMER LENGTH?")
print("="*80)
print("Testing P=29 specifically with both cribs as constraints.\n")

for alpha_name, alpha in [("KRYPTOS", KRYPTOS), ("STANDARD", STANDARD)]:
    for beaufort in [False, True]:
        mode = "BEAUFORT" if beaufort else "VIGENERE"

        P = 29
        key1, pt1 = derive_pt_autokey_key_from_crib(
            CRIB_ENE[0], CRIB_ENE[1], K4, P, alpha, beaufort)
        key2, pt2 = derive_pt_autokey_key_from_crib(
            CRIB_BC[0], CRIB_BC[1], K4, P, alpha, beaufort)

        # Check consistency
        consistent = True
        for pos in set(pt1.keys()) & set(pt2.keys()):
            if pt1[pos] != pt2[pos]:
                consistent = False
                break
        if consistent:
            for pos in set(key1.keys()) & set(key2.keys()):
                if key1[pos] != key2[pos]:
                    consistent = False
                    break

        merged_pt = {**pt1, **pt2}
        merged_key = {**key1, **key2}
        known_kw = {i: merged_key[i] for i in range(P) if i in merged_key}
        unknown_kw = [i for i in range(P) if i not in merged_key]

        status = "CONSISTENT" if consistent else "INCONSISTENT"
        print(f"  {mode} {alpha_name} P=29: {status}")
        print(f"    Known keyword positions: {sorted(known_kw.keys())}")
        print(f"    Known keyword chars: {''.join(known_kw.get(i, '?') for i in range(P))}")
        print(f"    Unknown keyword positions ({len(unknown_kw)}): {unknown_kw}")
        print(f"    Known PT positions ({len(merged_pt)}): {sorted(merged_pt.keys())[:30]}...")

        # Show the known PT as a partial string
        partial_pt = ''.join(merged_pt.get(i, '.') for i in range(K4_LEN))
        print(f"    Partial PT: {partial_pt}")


# ============================================================================
# FINAL RESULTS
# ============================================================================
print("\n" + "="*80)
print("FINAL RESULTS: TOP 20 ACROSS ALL METHODS")
print("="*80)

# Sort by raw quadgram score (higher = better)
ALL_RESULTS.sort(key=lambda x: -x[0])

# Deduplicate by plaintext
seen_pt = set()
unique_results = []
for score, norm, label, keyword, pt in ALL_RESULTS:
    if pt not in seen_pt:
        seen_pt.add(pt)
        unique_results.append((score, norm, label, keyword, pt))

print(f"\nTotal unique results: {len(unique_results)}")
print(f"\nTop 20 results:\n")

for rank, (score, norm, label, keyword, pt) in enumerate(unique_results[:20]):
    has_ene = CRIB_ENE[0] in pt
    has_bc = CRIB_BC[0] in pt
    crib_markers = []
    if has_ene:
        crib_markers.append(f"ENE@{pt.find(CRIB_ENE[0])}")
    if has_bc:
        crib_markers.append(f"BC@{pt.find(CRIB_BC[0])}")
    crib_str = " | CRIBS: " + ", ".join(crib_markers) if crib_markers else ""

    print(f"  {rank+1:2d}. [{norm:+.4f}] {label}")
    print(f"      Keyword: '{keyword}'{crib_str}")
    print(f"      Score: {score:.2f}")
    print(f"      PT: {pt}")
    print()


# ============================================================================
# BONUS: Show any results where BOTH cribs appear at correct positions
# ============================================================================
print("="*80)
print("RESULTS WITH BOTH CRIBS AT CORRECT POSITIONS")
print("="*80)

both_crib_results = []
for score, norm, label, keyword, pt in unique_results:
    ene_ok = pt[CRIB_ENE[1]:CRIB_ENE[1]+len(CRIB_ENE[0])] == CRIB_ENE[0]
    bc_ok = pt[CRIB_BC[1]:CRIB_BC[1]+len(CRIB_BC[0])] == CRIB_BC[0]
    if ene_ok and bc_ok:
        both_crib_results.append((score, norm, label, keyword, pt))

both_crib_results.sort(key=lambda x: -x[0])

if both_crib_results:
    print(f"\nFound {len(both_crib_results)} results with both cribs at correct positions!")
    print(f"\nTop 20:\n")
    for rank, (score, norm, label, keyword, pt) in enumerate(both_crib_results[:20]):
        print(f"  {rank+1:2d}. [{norm:+.4f}] {label}")
        print(f"      Keyword: '{keyword}'")
        print(f"      Score: {score:.2f}")
        print(f"      PT: {pt}")
        print()
else:
    print("\nNo results found with both cribs at their correct positions.")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
