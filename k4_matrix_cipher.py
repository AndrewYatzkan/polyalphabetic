#!/usr/bin/env python3
"""
K4 Matrix Cipher Analysis
=========================
Sanborn worked with Ed Scheidt (head of CIA's Cryptographic Center) on "matrix codes."
This script explores multiple matrix-based cipher approaches for K4.

Approaches:
1. Hill Cipher (2x2, 3x3) - matrix multiplication encryption, derive from cribs
2. Hill + Vigenere combo
3. Polybius Square Matrix operations (Bifid-like)
4. Matrix Transposition (dihedral group)
5. Vigenere then Hill (brute force 2x2)
6. Pure Hill brute force
"""

import math
import itertools
import sys

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known crib: positions 21-33 (0-indexed) decrypt to EASTNORTHEAST
CRIB_POS_START = 21
CRIB_TEXT = "EASTNORTHEAST"
CRIB_CT = K4[CRIB_POS_START:CRIB_POS_START + len(CRIB_TEXT)]

# Additional crib: BERLINCLOCK at positions 62-73
CRIB2_POS_START = 62
CRIB2_TEXT = "BERLINCLOCK"
CRIB2_CT = K4[CRIB2_POS_START:CRIB2_POS_START + len(CRIB2_TEXT)]

# Best known Vigenere key
VIG_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"

CRIBS = ["EASTNORTHEAST", "NORTHEAST", "BERLINCLOCK", "BERLIN", "CLOCK",
         "EAST", "NORTH", "BETWEEN", "SUBTLE", "SHADOW",
         "UNDERGROUND", "IQLUSION", "ILLUSION", "INVISIBLE",
         "SECRET", "HIDDEN", "LANGLEY", "LAYER", "DYAHR"]

# ============================================================
# QUADGRAM SCORER
# ============================================================

print("Loading quadgrams...")
QUADGRAMS = {}
TOTAL = 0
with open("/home/user/polyalphabetic/english_quadgrams.txt", "r") as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            gram, count = parts[0], int(parts[1])
            QUADGRAMS[gram] = count
            TOTAL += count

LOG_TOTAL = math.log10(TOTAL)
FLOOR = math.log10(0.01 / TOTAL)

def score_text(text):
    """Score text using log10 quadgram frequencies."""
    s = 0
    for i in range(len(text) - 3):
        quad = text[i:i+4]
        if quad in QUADGRAMS:
            s += math.log10(QUADGRAMS[quad]) - LOG_TOTAL
        else:
            s += FLOOR
    return s

def check_cribs(text):
    """Check if any known cribs appear in the text."""
    found = []
    for crib in CRIBS:
        if crib in text:
            found.append(crib)
    return found

INTERESTING_COUNT = 0

def report_result(desc, text, sc=None):
    """Print a result if it's interesting."""
    global INTERESTING_COUNT
    if sc is None:
        sc = score_text(text)
    cribs = check_cribs(text)
    if cribs or sc > -550:
        INTERESTING_COUNT += 1
        print(f"\n{'='*70}")
        print(f"  ** INTERESTING RESULT #{INTERESTING_COUNT} ** : {desc}")
        print(f"  Plaintext: {text}")
        print(f"  Score: {sc:.2f}")
        if cribs:
            print(f"  CRIBS FOUND: {cribs}")
        print(f"{'='*70}")
        return True
    return False

# ============================================================
# MODULAR ARITHMETIC HELPERS
# ============================================================

def mod_inv(a, m=26):
    """Modular inverse of a mod m."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def mat_det_2x2(M, mod=26):
    return (M[0]*M[3] - M[1]*M[2]) % mod

def mat_inv_2x2_flat(M, mod=26):
    """Inverse of 2x2 matrix given as flat [a,b,c,d]. Returns flat or None."""
    det = (M[0]*M[3] - M[1]*M[2]) % mod
    det_inv = mod_inv(det, mod)
    if det_inv is None:
        return None
    return [(M[3] * det_inv) % mod, ((-M[1]) * det_inv) % mod,
            ((-M[2]) * det_inv) % mod, (M[0] * det_inv) % mod]

# ============================================================
# PRE-COMPUTE ALL INVERTIBLE 2x2 MATRICES mod 26
# ============================================================

print("Pre-computing all invertible 2x2 matrices mod 26...")
INVERTIBLE_2X2 = []  # List of (M_flat, M_inv_flat)
for a in range(26):
    for b in range(26):
        for c in range(26):
            for d in range(26):
                det = (a*d - b*c) % 26
                if math.gcd(det, 26) != 1:
                    continue
                M = [a, b, c, d]
                M_inv = mat_inv_2x2_flat(M)
                if M_inv is not None:
                    INVERTIBLE_2X2.append((M, M_inv))
print(f"  Found {len(INVERTIBLE_2X2)} invertible 2x2 matrices")

# ============================================================
# 3x3 MATRIX HELPERS
# ============================================================

def mat_det_3x3(M):
    return (M[0][0]*(M[1][1]*M[2][2] - M[1][2]*M[2][1])
          - M[0][1]*(M[1][0]*M[2][2] - M[1][2]*M[2][0])
          + M[0][2]*(M[1][0]*M[2][1] - M[1][1]*M[2][0])) % 26

def mat_inv_3x3(M):
    det = mat_det_3x3(M)
    det_inv = mod_inv(det, 26)
    if det_inv is None:
        return None
    cof = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            rows = [r for r in range(3) if r != i]
            cols = [cc for cc in range(3) if cc != j]
            minor = M[rows[0]][cols[0]]*M[rows[1]][cols[1]] - M[rows[0]][cols[1]]*M[rows[1]][cols[0]]
            cof[i][j] = ((-1)**(i+j) * minor) % 26
    adj = [[cof[j][i] for j in range(3)] for i in range(3)]
    inv = [[(det_inv * adj[i][j]) % 26 for j in range(3)] for i in range(3)]
    return inv

def mat_mult_3x3(A, B):
    result = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            result[i][j] = sum(A[i][k]*B[k][j] for k in range(3)) % 26
    return result

def mat_mult_2x2(A, B):
    """A and B are nested [[a,b],[c,d]]."""
    return [
        [(A[0][0]*B[0][0] + A[0][1]*B[1][0]) % 26, (A[0][0]*B[0][1] + A[0][1]*B[1][1]) % 26],
        [(A[1][0]*B[0][0] + A[1][1]*B[1][0]) % 26, (A[1][0]*B[0][1] + A[1][1]*B[1][1]) % 26]
    ]

def mat_inv_2x2_nested(M):
    det = (M[0][0]*M[1][1] - M[0][1]*M[1][0]) % 26
    det_inv = mod_inv(det, 26)
    if det_inv is None:
        return None
    return [[(M[1][1]*det_inv) % 26, ((-M[0][1])*det_inv) % 26],
            [((-M[1][0])*det_inv) % 26, (M[0][0]*det_inv) % 26]]

# ============================================================
# ALPHABET MAPPING
# ============================================================

def to_nums(text, alpha=STANDARD_ALPHA):
    return [alpha.index(c) for c in text]

def from_nums(nums, alpha=STANDARD_ALPHA):
    return ''.join(alpha[n % 26] for n in nums)

# ============================================================
# HILL CIPHER DECRYPTION (optimized with flat matrices)
# ============================================================

def hill_decrypt_2x2_row(ct_nums, M_inv_flat):
    """Decrypt using row vector: PT = CT * M_inv. ct_nums is list of ints."""
    a, b, c, d = M_inv_flat
    pt = []
    n = len(ct_nums)
    if n % 2 != 0:
        ct_nums = ct_nums + [0]
    for i in range(0, len(ct_nums), 2):
        x, y = ct_nums[i], ct_nums[i+1]
        pt.append((x*a + y*c) % 26)
        pt.append((x*b + y*d) % 26)
    return pt[:n]

def hill_decrypt_2x2_col(ct_nums, M_inv_flat):
    """Decrypt using column vector: PT = M_inv * CT."""
    a, b, c, d = M_inv_flat
    pt = []
    n = len(ct_nums)
    if n % 2 != 0:
        ct_nums = ct_nums + [0]
    for i in range(0, len(ct_nums), 2):
        x, y = ct_nums[i], ct_nums[i+1]
        pt.append((a*x + b*y) % 26)
        pt.append((c*x + d*y) % 26)
    return pt[:n]

def hill_decrypt_3x3_row(ct_nums, M_inv):
    """Decrypt using row vector: PT_triple * M_inv. M_inv is 3x3 nested."""
    pt = []
    n = len(ct_nums)
    nums = ct_nums[:]
    while len(nums) % 3 != 0:
        nums.append(0)
    for i in range(0, len(nums), 3):
        v = nums[i:i+3]
        for j in range(3):
            pt.append(sum(v[k]*M_inv[k][j] for k in range(3)) % 26)
    return pt[:n]

def hill_decrypt_3x3_col(ct_nums, M_inv):
    """Decrypt using column vector: M_inv * CT_triple."""
    pt = []
    n = len(ct_nums)
    nums = ct_nums[:]
    while len(nums) % 3 != 0:
        nums.append(0)
    for i in range(0, len(nums), 3):
        v = nums[i:i+3]
        for j in range(3):
            pt.append(sum(M_inv[j][k]*v[k] for k in range(3)) % 26)
    return pt[:n]

def nums_to_text(nums, alpha=STANDARD_ALPHA):
    return ''.join(alpha[n % 26] for n in nums)

# ============================================================
# VIGENERE FUNCTIONS
# ============================================================

def vigenere_decrypt(ct, key, alpha=STANDARD_ALPHA):
    pt = []
    for i, c in enumerate(ct):
        ci = alpha.index(c)
        ki = alpha.index(key[i % len(key)])
        pt.append(alpha[(ci - ki) % 26])
    return ''.join(pt)

def vigenere_encrypt(pt, key, alpha=STANDARD_ALPHA):
    ct = []
    for i, c in enumerate(pt):
        pi = alpha.index(c)
        ki = alpha.index(key[i % len(key)])
        ct.append(alpha[(pi + ki) % 26])
    return ''.join(ct)

# ============================================================
# PRE-COMPUTE K4 IN NUMERIC FORM
# ============================================================

K4_STD = to_nums(K4, STANDARD_ALPHA)
K4_KRY = to_nums(K4, KRYPTOS_ALPHA)

# ============================================================
# SECTION 1: HILL CIPHER FROM CRIBS (2x2)
# ============================================================

def derive_hill_2x2_from_cribs():
    print("\n" + "="*70)
    print("SECTION 1: HILL CIPHER (2x2) - Deriving key from cribs")
    print("="*70)

    results_found = 0

    for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
        print(f"\n--- Using {alpha_name} alphabet ---")

        pt_text = CRIB_TEXT  # EASTNORTHEAST
        ct_text = CRIB_CT   # FLRVQQPRNGKSS
        print(f"  PT: {pt_text}")
        print(f"  CT: {ct_text}")

        pt_nums = to_nums(pt_text, alpha)
        ct_nums = to_nums(ct_text, alpha)
        print(f"  PT nums ({alpha_name}): {pt_nums}")
        print(f"  CT nums ({alpha_name}): {ct_nums}")

        k4_nums = K4_STD if alpha_name == "STANDARD" else K4_KRY

        # Try different block alignment offsets
        for offset in [0, 1]:
            if offset == 1:
                pn = pt_nums[1:]
                cn = ct_nums[1:]
            else:
                pn = pt_nums
                cn = ct_nums

            # Create pairs
            pt_pairs = [(pn[i], pn[i+1]) for i in range(0, len(pn)-1, 2)]
            ct_pairs = [(cn[i], cn[i+1]) for i in range(0, len(cn)-1, 2)]
            n_pairs = min(len(pt_pairs), len(ct_pairs))
            pt_pairs = pt_pairs[:n_pairs]
            ct_pairs = ct_pairs[:n_pairs]

            print(f"\n  Offset={offset}, {n_pairs} pairs:")
            for idx in range(n_pairs):
                print(f"    Pair {idx}: PT={pt_pairs[idx]} CT={ct_pairs[idx]}")

            # For both vector conventions
            for conv_name, use_col in [("ROW_VEC", False), ("COL_VEC", True)]:
                for i in range(n_pairs):
                    for j in range(i+1, n_pairs):
                        if use_col:
                            # M * PT = CT (column vectors)
                            # Stack as columns: M * [pt_i | pt_j] = [ct_i | ct_j]
                            # M = CT_mat * PT_mat_inv
                            P = [[pt_pairs[i][0], pt_pairs[j][0]],
                                 [pt_pairs[i][1], pt_pairs[j][1]]]
                            C = [[ct_pairs[i][0], ct_pairs[j][0]],
                                 [ct_pairs[i][1], ct_pairs[j][1]]]
                        else:
                            # PT * M = CT (row vectors)
                            # Stack as rows: [pt_i; pt_j] * M = [ct_i; ct_j]
                            # M = PT_mat_inv * CT_mat
                            P = [[pt_pairs[i][0], pt_pairs[i][1]],
                                 [pt_pairs[j][0], pt_pairs[j][1]]]
                            C = [[ct_pairs[i][0], ct_pairs[i][1]],
                                 [ct_pairs[j][0], ct_pairs[j][1]]]

                        P_inv = mat_inv_2x2_nested(P)
                        if P_inv is None:
                            continue

                        if use_col:
                            M = mat_mult_2x2(C, P_inv)
                        else:
                            M = mat_mult_2x2(P_inv, C)

                        M_inv = mat_inv_2x2_nested(M)
                        if M_inv is None:
                            continue

                        # Verify against other pairs
                        consistent = True
                        for k in range(n_pairs):
                            if k == i or k == j:
                                continue
                            p = list(pt_pairs[k])
                            c = list(ct_pairs[k])
                            if use_col:
                                expected = [(M[0][0]*p[0] + M[0][1]*p[1]) % 26,
                                            (M[1][0]*p[0] + M[1][1]*p[1]) % 26]
                            else:
                                expected = [(p[0]*M[0][0] + p[1]*M[1][0]) % 26,
                                            (p[0]*M[0][1] + p[1]*M[1][1]) % 26]
                            if expected[0] != c[0] or expected[1] != c[1]:
                                consistent = False
                                break

                        # Also verify against BERLINCLOCK crib
                        crib2_pt = to_nums(CRIB2_TEXT, alpha)
                        crib2_ct = to_nums(CRIB2_CT, alpha)
                        crib2_consistent = True
                        # Check alignment: if global pos 62 with block size 2
                        # offset 0: block starts at even positions
                        # position 62 is even -> pair (62,63)
                        # offset 1: block starts at odd positions
                        # position 62 is even -> 62 is end of block (61,62), next is (63,64)
                        c2_off = 0 if ((CRIB2_POS_START + offset) % 2 == 0) else 1
                        c2_pt = crib2_pt[c2_off:]
                        c2_ct = crib2_ct[c2_off:]
                        c2_pairs_pt = [(c2_pt[ii], c2_pt[ii+1]) for ii in range(0, len(c2_pt)-1, 2)]
                        c2_pairs_ct = [(c2_ct[ii], c2_ct[ii+1]) for ii in range(0, len(c2_ct)-1, 2)]
                        for kk in range(min(len(c2_pairs_pt), len(c2_pairs_ct))):
                            p = list(c2_pairs_pt[kk])
                            c = list(c2_pairs_ct[kk])
                            if use_col:
                                expected = [(M[0][0]*p[0] + M[0][1]*p[1]) % 26,
                                            (M[1][0]*p[0] + M[1][1]*p[1]) % 26]
                            else:
                                expected = [(p[0]*M[0][0] + p[1]*M[1][0]) % 26,
                                            (p[0]*M[0][1] + p[1]*M[1][1]) % 26]
                            if expected[0] != c[0] or expected[1] != c[1]:
                                crib2_consistent = False
                                break

                        status = "CONSISTENT" if consistent else "inconsistent"
                        crib2_status = "CRIB2-OK" if crib2_consistent else "crib2-fail"

                        # Decrypt full K4
                        M_inv_flat = [M_inv[0][0], M_inv[0][1], M_inv[1][0], M_inv[1][1]]
                        if use_col:
                            pt_nums_dec = hill_decrypt_2x2_col(k4_nums, M_inv_flat)
                        else:
                            pt_nums_dec = hill_decrypt_2x2_row(k4_nums, M_inv_flat)
                        pt = nums_to_text(pt_nums_dec, alpha)
                        sc = score_text(pt)

                        if consistent or crib2_consistent:
                            print(f"\n  {status}/{crib2_status}: off={offset} {conv_name} pairs({i},{j})")
                            print(f"  Key M = [[{M[0][0]},{M[0][1]}],[{M[1][0]},{M[1][1]}]]")
                            print(f"  Decrypted: {pt[:60]}...")
                            print(f"  Score: {sc:.2f}")
                            results_found += 1

                        report_result(
                            f"Hill-2x2 {alpha_name} off={offset} {conv_name} pairs({i},{j}) {status} {crib2_status}",
                            pt, sc
                        )

    if results_found == 0:
        print("\n  No fully consistent Hill-2x2 keys found from cribs.")
    return results_found

# ============================================================
# SECTION 1b: HILL CIPHER FROM CRIBS (3x3)
# ============================================================

def derive_hill_3x3_from_cribs():
    print("\n" + "="*70)
    print("SECTION 1b: HILL CIPHER (3x3) - Deriving key from cribs")
    print("="*70)

    results_found = 0

    for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
        print(f"\n--- Using {alpha_name} alphabet ---")

        pt_nums = to_nums(CRIB_TEXT, alpha)
        ct_nums = to_nums(CRIB_CT, alpha)
        k4_nums = K4_STD if alpha_name == "STANDARD" else K4_KRY

        for offset in [0, 1, 2]:
            pn = pt_nums[offset:]
            cn = ct_nums[offset:]
            pt_triples = [(pn[i], pn[i+1], pn[i+2]) for i in range(0, len(pn)-2, 3)]
            ct_triples = [(cn[i], cn[i+1], cn[i+2]) for i in range(0, len(cn)-2, 3)]
            nt = min(len(pt_triples), len(ct_triples))
            pt_triples = pt_triples[:nt]
            ct_triples = ct_triples[:nt]

            if nt < 3:
                continue

            print(f"\n  Offset={offset}, {nt} triples")

            for conv_name, use_col in [("ROW_VEC", False), ("COL_VEC", True)]:
                for combo in itertools.combinations(range(nt), 3):
                    ii, jj, kk = combo

                    if use_col:
                        P = [[pt_triples[ii][r] for r in range(3)] for r_idx in range(1)]
                        P = [[pt_triples[ii][0], pt_triples[jj][0], pt_triples[kk][0]],
                             [pt_triples[ii][1], pt_triples[jj][1], pt_triples[kk][1]],
                             [pt_triples[ii][2], pt_triples[jj][2], pt_triples[kk][2]]]
                        C = [[ct_triples[ii][0], ct_triples[jj][0], ct_triples[kk][0]],
                             [ct_triples[ii][1], ct_triples[jj][1], ct_triples[kk][1]],
                             [ct_triples[ii][2], ct_triples[jj][2], ct_triples[kk][2]]]
                    else:
                        P = [list(pt_triples[ii]), list(pt_triples[jj]), list(pt_triples[kk])]
                        C = [list(ct_triples[ii]), list(ct_triples[jj]), list(ct_triples[kk])]

                    P_inv = mat_inv_3x3(P)
                    if P_inv is None:
                        continue

                    if use_col:
                        M = mat_mult_3x3(C, P_inv)
                    else:
                        M = mat_mult_3x3(P_inv, C)

                    M_inv = mat_inv_3x3(M)
                    if M_inv is None:
                        continue

                    # Verify remaining triples
                    consistent = True
                    for t in range(nt):
                        if t in combo:
                            continue
                        p = list(pt_triples[t])
                        c = list(ct_triples[t])
                        if use_col:
                            expected = [sum(M[r][k]*p[k] for k in range(3)) % 26 for r in range(3)]
                        else:
                            expected = [sum(p[k]*M[k][j] for k in range(3)) % 26 for j in range(3)]
                        if expected != list(c):
                            consistent = False
                            break

                    if use_col:
                        pt_dec = hill_decrypt_3x3_col(k4_nums, M_inv)
                    else:
                        pt_dec = hill_decrypt_3x3_row(k4_nums, M_inv)
                    pt = nums_to_text(pt_dec, alpha)
                    sc = score_text(pt)

                    if consistent:
                        print(f"\n  CONSISTENT 3x3: off={offset} {conv_name} combo{combo}")
                        print(f"  M = {M}")
                        print(f"  Decrypted: {pt[:60]}...")
                        print(f"  Score: {sc:.2f}")
                        results_found += 1

                    report_result(f"Hill-3x3 {alpha_name} off={offset} {conv_name} {combo}", pt, sc)

    if results_found == 0:
        print("\n  No fully consistent Hill-3x3 keys found from cribs.")
    return results_found

# ============================================================
# SECTION 2: HILL + VIGENERE COMBO (long key)
# ============================================================

def hill_vigenere_combo():
    print("\n" + "="*70)
    print("SECTION 2: HILL + VIGENERE COMBINATION (long key)")
    print("="*70)

    vig_key = VIG_KEY
    vig_dec = vigenere_decrypt(K4, vig_key)
    vig_dec_nums = to_nums(vig_dec)
    print(f"  Vigenere decryption with key {vig_key}")
    print(f"  Result: {vig_dec}")
    print(f"  Vig score: {score_text(vig_dec):.2f}")

    # Direction A: Vigenere first, then Hill
    print(f"\n  Direction A: Vig decrypt -> Hill decrypt (testing {len(INVERTIBLE_2X2)} matrices)...")
    best_a = (-9999, "", "")
    for M, M_inv in INVERTIBLE_2X2:
        # Row vector
        pt_nums = hill_decrypt_2x2_row(vig_dec_nums, M_inv)
        pt = nums_to_text(pt_nums)
        sc = score_text(pt)
        if sc > best_a[0]:
            best_a = (sc, pt, f"Vig+Hill2 M={M} row")
        report_result(f"Vig({vig_key[:8]}..)+Hill2 M={M} row", pt, sc)

        # Col vector
        pt_nums = hill_decrypt_2x2_col(vig_dec_nums, M_inv)
        pt = nums_to_text(pt_nums)
        sc = score_text(pt)
        if sc > best_a[0]:
            best_a = (sc, pt, f"Vig+Hill2 M={M} col")
        report_result(f"Vig({vig_key[:8]}..)+Hill2 M={M} col", pt, sc)

    print(f"  Best (Vig->Hill): score={best_a[0]:.2f}")
    print(f"    {best_a[2]}")
    print(f"    {best_a[1][:60]}...")

    # Direction B: Hill first, then Vigenere
    print(f"\n  Direction B: Hill decrypt -> Vig decrypt...")
    best_b = (-9999, "", "")
    for M, M_inv in INVERTIBLE_2X2:
        # Row
        h_nums = hill_decrypt_2x2_row(K4_STD, M_inv)
        h_text = nums_to_text(h_nums)
        pt = vigenere_decrypt(h_text, vig_key)
        sc = score_text(pt)
        if sc > best_b[0]:
            best_b = (sc, pt, f"Hill2 M={M} row + Vig")
        report_result(f"Hill2 M={M} row + Vig({vig_key[:8]}..)", pt, sc)

        # Col
        h_nums = hill_decrypt_2x2_col(K4_STD, M_inv)
        h_text = nums_to_text(h_nums)
        pt = vigenere_decrypt(h_text, vig_key)
        sc = score_text(pt)
        if sc > best_b[0]:
            best_b = (sc, pt, f"Hill2 M={M} col + Vig")
        report_result(f"Hill2 M={M} col + Vig({vig_key[:8]}..)", pt, sc)

    print(f"  Best (Hill->Vig): score={best_b[0]:.2f}")
    print(f"    {best_b[2]}")
    print(f"    {best_b[1][:60]}...")

# ============================================================
# SECTION 3: POLYBIUS SQUARE MATRIX
# ============================================================

def build_polybius_square(key_alpha):
    """Build 5x5 Polybius square (J=I)."""
    seen = set()
    letters = []
    for c in key_alpha:
        cc = 'I' if c == 'J' else c
        if cc not in seen:
            seen.add(cc)
            letters.append(cc)
    grid = []
    char_to_pos = {}
    for i in range(5):
        row = []
        for j in range(5):
            idx = i*5 + j
            if idx < len(letters):
                ch = letters[idx]
                row.append(ch)
                char_to_pos[ch] = (i, j)
        grid.append(row)
    return grid, char_to_pos

def polybius_matrix_cipher():
    print("\n" + "="*70)
    print("SECTION 3: POLYBIUS SQUARE MATRIX OPERATIONS")
    print("="*70)

    for alpha_name, key_alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
        print(f"\n--- {alpha_name} keyed Polybius ---")
        grid, char_to_pos = build_polybius_square(key_alpha)
        print("  Grid:")
        for row in grid:
            print(f"    {' '.join(row)}")

        ct_text = K4.replace('J', 'I')
        coords = []
        for c in ct_text:
            if c in char_to_pos:
                coords.append(char_to_pos[c])
            else:
                coords.append((0, 0))

        # Method A: Bifid-style decryption with various periods
        print(f"\n  Method A: Bifid decryption")
        for period in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 19, 29, 47, 48, 49, 97]:
            pt_chars = []
            for block_start in range(0, len(coords), period):
                block = coords[block_start:block_start+period]
                brows = [c[0] for c in block]
                bcols = [c[1] for c in block]
                combined = brows + bcols
                for i in range(0, len(combined)-1, 2):
                    r, cv = combined[i], combined[i+1]
                    if 0 <= r < 5 and 0 <= cv < 5:
                        pt_chars.append(grid[r][cv])
                    else:
                        pt_chars.append('X')
            pt = ''.join(pt_chars)
            if len(pt) >= 50:
                sc = score_text(pt)
                report_result(f"Bifid {alpha_name} period={period}", pt, sc)

        # Method B: 2x2 matrix on (row,col) mod 5
        print(f"\n  Method B: Matrix multiplication on Polybius coords (mod 5)")
        best_b = (-9999, "", "")
        for a in range(5):
            for b in range(5):
                for c in range(5):
                    for d in range(5):
                        det = (a*d - b*c) % 5
                        if det == 0:
                            continue
                        det_inv = None
                        for x in range(1, 5):
                            if (det * x) % 5 == 1:
                                det_inv = x
                                break
                        if det_inv is None:
                            continue
                        Mi = [[(d*det_inv) % 5, ((-b)*det_inv) % 5],
                              [((-c)*det_inv) % 5, (a*det_inv) % 5]]

                        pt_chars = []
                        for coord in coords:
                            r, co = coord
                            nr = (Mi[0][0]*r + Mi[0][1]*co) % 5
                            nc = (Mi[1][0]*r + Mi[1][1]*co) % 5
                            pt_chars.append(grid[nr][nc])
                        pt = ''.join(pt_chars)
                        sc = score_text(pt)
                        if sc > best_b[0]:
                            best_b = (sc, pt, f"M=[{a},{b},{c},{d}]")
                        report_result(f"Polybius-mat {alpha_name} [{a},{b},{c},{d}]", pt, sc)

        print(f"  Best Polybius matrix ({alpha_name}): {best_b[0]:.2f} {best_b[2]}")
        print(f"    {best_b[1][:60]}...")

        # Method C: Trifid-style (convert to base-3 coordinates in 3x3x3 cube)
        print(f"\n  Method C: Trifid-style (3x3x3 cube)")
        # Build 3x3x3 cube from keyed alphabet (27 slots, 26 letters + pad)
        seen_set = set()
        cube_letters = []
        for ch in key_alpha:
            cc = ch.upper()
            if cc not in seen_set:
                seen_set.add(cc)
                cube_letters.append(cc)
        while len(cube_letters) < 27:
            cube_letters.append('+')

        char_to_3d = {}
        td_to_char = {}
        for idx, ch in enumerate(cube_letters[:27]):
            layer = idx // 9
            row = (idx % 9) // 3
            col = idx % 3
            char_to_3d[ch] = (layer, row, col)
            td_to_char[(layer, row, col)] = ch

        for period in [3, 5, 7, 9, 13, 27, 97]:
            ct_3d = [char_to_3d.get(c, (0,0,0)) for c in ct_text]
            pt_chars = []
            for bs in range(0, len(ct_3d), period):
                block = ct_3d[bs:bs+period]
                layers = [t[0] for t in block]
                rows = [t[1] for t in block]
                cols = [t[2] for t in block]
                combined = layers + rows + cols
                for i in range(0, len(combined)-2, 3):
                    key_3d = (combined[i] % 3, combined[i+1] % 3, combined[i+2] % 3)
                    pt_chars.append(td_to_char.get(key_3d, 'X'))
            pt = ''.join(pt_chars)
            if len(pt) >= 30:
                sc = score_text(pt)
                report_result(f"Trifid {alpha_name} period={period}", pt, sc)

# ============================================================
# SECTION 4: MATRIX TRANSPOSITION
# ============================================================

def matrix_transposition():
    print("\n" + "="*70)
    print("SECTION 4: MATRIX TRANSPOSITION (Dihedral Group)")
    print("="*70)

    n = len(K4)  # 97
    dimensions = set()
    for r in range(2, 50):
        for c in range(2, 50):
            if r * c >= n and r * c <= n + 10:
                dimensions.add((r, c))
    # Ensure specific ones
    for dim in [(7, 14), (8, 13), (9, 11), (10, 10)]:
        dimensions.add(dim)

    dimensions = sorted(dimensions)
    print(f"  Testing {len(dimensions)} matrix dimensions")

    best_overall = (-9999, "", "")

    for fill in ['rows', 'cols']:
        for rows, cols in dimensions:
            matrix = [[None]*cols for _ in range(rows)]
            idx = 0
            if fill == 'rows':
                for r in range(rows):
                    for c in range(cols):
                        if idx < n:
                            matrix[r][c] = K4[idx]; idx += 1
            else:
                for c in range(cols):
                    for r in range(rows):
                        if idx < n:
                            matrix[r][c] = K4[idx]; idx += 1

            # Generate readouts
            readouts = {}

            # 8 basic orientations
            def readout(r_range, c_range, row_first=True):
                t = ''
                if row_first:
                    for r in r_range:
                        for c in c_range:
                            if 0 <= r < rows and 0 <= c < cols and matrix[r][c]:
                                t += matrix[r][c]
                else:
                    for c in c_range:
                        for r in r_range:
                            if 0 <= r < rows and 0 <= c < cols and matrix[r][c]:
                                t += matrix[r][c]
                return t

            readouts['r_lr_tb'] = readout(range(rows), range(cols), True)
            readouts['r_rl_tb'] = readout(range(rows), range(cols-1,-1,-1), True)
            readouts['r_lr_bt'] = readout(range(rows-1,-1,-1), range(cols), True)
            readouts['r_rl_bt'] = readout(range(rows-1,-1,-1), range(cols-1,-1,-1), True)
            readouts['c_tb_lr'] = readout(range(rows), range(cols), False)
            readouts['c_bt_lr'] = readout(range(rows-1,-1,-1), range(cols), False)
            readouts['c_tb_rl'] = readout(range(rows), range(cols-1,-1,-1), False)
            readouts['c_bt_rl'] = readout(range(rows-1,-1,-1), range(cols-1,-1,-1), False)

            # Diagonal reads
            t = ''
            for d in range(rows + cols - 1):
                for r in range(rows):
                    c = d - r
                    if 0 <= c < cols and matrix[r][c]:
                        t += matrix[r][c]
            readouts['diag'] = t

            t = ''
            for d in range(rows + cols - 1):
                for r in range(rows):
                    c = (cols-1) - (d - r)
                    if 0 <= c < cols and matrix[r][c]:
                        t += matrix[r][c]
            readouts['antidiag'] = t

            # Spiral clockwise
            t = ''
            top, bot, left, right = 0, rows-1, 0, cols-1
            while top <= bot and left <= right:
                for c in range(left, right+1):
                    if matrix[top][c]: t += matrix[top][c]
                top += 1
                for r in range(top, bot+1):
                    if matrix[r][right]: t += matrix[r][right]
                right -= 1
                if top <= bot:
                    for c in range(right, left-1, -1):
                        if matrix[bot][c]: t += matrix[bot][c]
                    bot -= 1
                if left <= right:
                    for r in range(bot, top-1, -1):
                        if matrix[r][left]: t += matrix[r][left]
                    left += 1
            readouts['spiral'] = t

            # Boustrophedon (alternating direction rows)
            t = ''
            for r in range(rows):
                if r % 2 == 0:
                    for c in range(cols):
                        if matrix[r][c]: t += matrix[r][c]
                else:
                    for c in range(cols-1, -1, -1):
                        if matrix[r][c]: t += matrix[r][c]
            readouts['boustro'] = t

            for tname, text in readouts.items():
                text = text[:n]
                if len(text) < 50:
                    continue
                sc = score_text(text)
                if sc > best_overall[0]:
                    best_overall = (sc, text, f"fill={fill} {rows}x{cols} {tname}")
                report_result(f"MatTrans fill={fill} {rows}x{cols} {tname}", text, sc)

    print(f"\n  Best transposition: {best_overall[0]:.2f}")
    print(f"  {best_overall[2]}")
    print(f"  {best_overall[1][:60]}...")

# ============================================================
# SECTION 5: VIGENERE THEN HILL (Short Keys + Brute Force 2x2)
# ============================================================

def vigenere_then_hill():
    print("\n" + "="*70)
    print("SECTION 5: VIGENERE THEN HILL (Short Keys)")
    print("="*70)

    short_keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "BERLIN",
                  "CLOCK", "SCHEIDT", "MATRIX", "SANBORN", "CIA",
                  "NORTHEAST", "EAST", "NORTH", "LAYER", "TWO",
                  "DYAHR", "ED", "JIM"]
    all_keys = short_keys + [VIG_KEY]

    overall_best = (-9999, "", "")

    for key in all_keys:
        key = key.upper()
        dec = vigenere_decrypt(K4, key)
        dec_nums = to_nums(dec)
        label = key if len(key) <= 12 else key[:10]+".."

        best = (-9999, "", "")
        for M, M_inv in INVERTIBLE_2X2:
            # Row
            pt_nums = hill_decrypt_2x2_row(dec_nums, M_inv)
            pt = nums_to_text(pt_nums)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, f"M={M} row")
            if sc > overall_best[0]:
                overall_best = (sc, pt, f"Vig({label})+Hill2 M={M} row")
            report_result(f"Vig({label})+Hill2 M={M} row", pt, sc)

            # Col
            pt_nums = hill_decrypt_2x2_col(dec_nums, M_inv)
            pt = nums_to_text(pt_nums)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, f"M={M} col")
            if sc > overall_best[0]:
                overall_best = (sc, pt, f"Vig({label})+Hill2 M={M} col")
            report_result(f"Vig({label})+Hill2 M={M} col", pt, sc)

        print(f"  Vig({label}): best Hill2 = {best[0]:.2f} {best[2]}")

    print(f"\n  Overall best (Vig+Hill2): {overall_best[0]:.2f}")
    print(f"  {overall_best[2]}")
    print(f"  {overall_best[1][:60]}...")

    # Also try Hill-3x3 with structured matrices on Vigenere-decrypted
    print(f"\n  Trying Hill-3x3 structured matrices on Vig-decrypted...")
    vig_dec_main = vigenere_decrypt(K4, VIG_KEY)
    vig_dec_nums = to_nums(vig_dec_main)

    best3 = (-9999, "", "")

    # Permutation matrices
    for perm in itertools.permutations([0, 1, 2]):
        M = [[0]*3 for _ in range(3)]
        for i in range(3):
            M[i][perm[i]] = 1
        M_inv = mat_inv_3x3(M)
        if M_inv is None:
            continue
        for use_col in [False, True]:
            if use_col:
                pt_dec = hill_decrypt_3x3_col(vig_dec_nums, M_inv)
            else:
                pt_dec = hill_decrypt_3x3_row(vig_dec_nums, M_inv)
            pt = nums_to_text(pt_dec)
            sc = score_text(pt)
            if sc > best3[0]:
                best3 = (sc, pt, f"perm={perm} {'col' if use_col else 'row'}")
            report_result(f"Vig+Hill3 perm={perm} {'col' if use_col else 'row'}", pt, sc)

    # Small-entry matrices (0-3)
    print("  Trying Hill-3x3 entries 0-3...")
    count = 0
    for vals in itertools.product(range(4), repeat=9):
        M = [list(vals[i*3:(i+1)*3]) for i in range(3)]
        det = mat_det_3x3(M)
        if math.gcd(det % 26, 26) != 1:
            continue
        M_inv = mat_inv_3x3(M)
        if M_inv is None:
            continue
        count += 1

        pt_dec = hill_decrypt_3x3_row(vig_dec_nums, M_inv)
        pt = nums_to_text(pt_dec)
        sc = score_text(pt)
        if sc > best3[0]:
            best3 = (sc, pt, f"small M={vals} row")
        report_result(f"Vig+Hill3 small row {vals}", pt, sc)

        pt_dec = hill_decrypt_3x3_col(vig_dec_nums, M_inv)
        pt = nums_to_text(pt_dec)
        sc = score_text(pt)
        if sc > best3[0]:
            best3 = (sc, pt, f"small M={vals} col")
        report_result(f"Vig+Hill3 small col {vals}", pt, sc)

    print(f"  Tested {count} small 3x3 matrices")
    print(f"  Best Hill-3x3: {best3[0]:.2f} {best3[2]}")
    print(f"    {best3[1][:60]}...")

# ============================================================
# SECTION 5b: HILL THEN VIGENERE (Short Keys)
# ============================================================

def hill_then_vigenere():
    print("\n" + "="*70)
    print("SECTION 5b: HILL THEN VIGENERE (Short Keys)")
    print("="*70)

    short_keys = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "BERLIN",
                  "CLOCK", "SCHEIDT", "MATRIX", "SANBORN", "CIA",
                  "NORTHEAST", "EAST", "NORTH", "LAYER", "TWO",
                  "DYAHR", "ED", "JIM"]

    overall_best = (-9999, "", "")

    for key in short_keys:
        key = key.upper()
        label = key if len(key) <= 12 else key[:10]+".."
        best = (-9999, "", "")

        for M, M_inv in INVERTIBLE_2X2:
            # Row: Hill decrypt then Vig decrypt
            h_nums = hill_decrypt_2x2_row(K4_STD, M_inv)
            h_text = nums_to_text(h_nums)
            pt = vigenere_decrypt(h_text, key)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, f"M={M} row")
            if sc > overall_best[0]:
                overall_best = (sc, pt, f"Hill2 M={M} row + Vig({label})")
            report_result(f"Hill2 {M} row + Vig({label})", pt, sc)

            # Col
            h_nums = hill_decrypt_2x2_col(K4_STD, M_inv)
            h_text = nums_to_text(h_nums)
            pt = vigenere_decrypt(h_text, key)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, f"M={M} col")
            if sc > overall_best[0]:
                overall_best = (sc, pt, f"Hill2 M={M} col + Vig({label})")
            report_result(f"Hill2 {M} col + Vig({label})", pt, sc)

        print(f"  Vig({label}): best = {best[0]:.2f} {best[2]}")

    print(f"\n  Overall best (Hill+Vig): {overall_best[0]:.2f}")
    print(f"  {overall_best[2]}")
    print(f"  {overall_best[1][:60]}...")

# ============================================================
# SECTION 6: PURE HILL BRUTE FORCE
# ============================================================

def pure_hill_bruteforce():
    print("\n" + "="*70)
    print("SECTION 6: PURE HILL-2x2 BRUTE FORCE ON K4")
    print("="*70)

    for alpha_name, alpha, k4_nums in [("STANDARD", STANDARD_ALPHA, K4_STD),
                                        ("KRYPTOS", KRYPTOS_ALPHA, K4_KRY)]:
        print(f"\n--- {alpha_name} alphabet ---")
        best = (-9999, "", None, "")

        for M, M_inv in INVERTIBLE_2X2:
            pt_nums = hill_decrypt_2x2_row(k4_nums, M_inv)
            pt = nums_to_text(pt_nums, alpha)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, M, "row")
            report_result(f"Pure Hill2 {alpha_name} {M} row", pt, sc)

            pt_nums = hill_decrypt_2x2_col(k4_nums, M_inv)
            pt = nums_to_text(pt_nums, alpha)
            sc = score_text(pt)
            if sc > best[0]:
                best = (sc, pt, M, "col")
            report_result(f"Pure Hill2 {alpha_name} {M} col", pt, sc)

        print(f"  Best: score={best[0]:.2f} M={best[2]} conv={best[3]}")
        print(f"  {best[1][:60]}...")

# ============================================================
# MAIN
# ============================================================

def main():
    print("\nK4 Matrix Cipher Analysis")
    print(f"K4 = {K4}")
    print(f"Length = {len(K4)}")
    print(f"KRYPTOS alphabet: {KRYPTOS_ALPHA}")
    print(f"Crib CT (pos {CRIB_POS_START}-{CRIB_POS_START+len(CRIB_TEXT)-1}): {CRIB_CT}")
    print(f"Crib PT: {CRIB_TEXT}")
    print(f"Crib2 CT (pos {CRIB2_POS_START}-{CRIB2_POS_START+len(CRIB2_TEXT)-1}): {CRIB2_CT}")
    print(f"Crib2 PT: {CRIB2_TEXT}")

    # Section 1: Hill from cribs (fast)
    print("\n" + "#"*70)
    print("# SECTION 1: HILL CIPHER FROM CRIBS")
    print("#"*70)
    derive_hill_2x2_from_cribs()
    derive_hill_3x3_from_cribs()

    # Section 3: Polybius (fast)
    print("\n" + "#"*70)
    print("# SECTION 3: POLYBIUS SQUARE MATRIX")
    print("#"*70)
    polybius_matrix_cipher()

    # Section 4: Matrix transposition (fast)
    print("\n" + "#"*70)
    print("# SECTION 4: MATRIX TRANSPOSITION")
    print("#"*70)
    matrix_transposition()

    # Section 6: Pure Hill brute force (moderate - ~157K * 2 alphas * 2 convs)
    print("\n" + "#"*70)
    print("# SECTION 6: PURE HILL-2x2 BRUTE FORCE")
    print("#"*70)
    pure_hill_bruteforce()

    # Section 2: Hill+Vigenere with long key (moderate)
    print("\n" + "#"*70)
    print("# SECTION 2: HILL + VIGENERE COMBO (long key)")
    print("#"*70)
    hill_vigenere_combo()

    # Section 5: Vigenere then Hill with short keys (heavier)
    print("\n" + "#"*70)
    print("# SECTION 5: VIGENERE THEN HILL (Short Keys)")
    print("#"*70)
    vigenere_then_hill()

    # Section 5b: Hill then Vigenere with short keys (heavier)
    print("\n" + "#"*70)
    print("# SECTION 5b: HILL THEN VIGENERE (Short Keys)")
    print("#"*70)
    hill_then_vigenere()

    print("\n" + "="*70)
    print(f"ANALYSIS COMPLETE - {INTERESTING_COUNT} interesting results found")
    print("="*70)

if __name__ == "__main__":
    main()
