#!/usr/bin/env python3
"""
Phase 6 only: CT-Autokey analytical check.
This is purely O(N) - no brute force needed.
Checks every possible primer length for CT-autokey variants.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

KNOWN_PT    = "BERLINCLOCK"
KNOWN_START = 63

assert len(K4) == 97
assert len(KRYPTOS_ALPHA) == 26
assert len(set(KRYPTOS_ALPHA)) == 26

def alpha_idx(c, alpha):
    return alpha.index(c)

def alpha_chr(i, alpha):
    return alpha[i % len(alpha)]

print("=" * 80)
print("CT-AUTOKEY ANALYTICAL CHECK - All primer lengths 1..96")
print("=" * 80)
print(f"K4 = {K4}")
print(f"K4[63:74] = '{K4[63:74]}' => must decrypt to '{KNOWN_PT}'")
print()

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\n{'='*60}")
    print(f"Alphabet: {alpha_name}")
    print(f"{'='*60}")

    # ── CT-Autokey Vigenere: pt[i] = ct[i] - ct[i-P]  for i >= P
    print("\nCT-Autokey Vigenere (pt[i] = ct[i] - ct[i-P]):")
    for P in range(1, len(K4)):
        if KNOWN_START < P:
            break  # all of BERLINCLOCK in primer zone, can't check
        match = True
        for j, p_char in enumerate(KNOWN_PT):
            i = KNOWN_START + j
            if i < P:
                continue  # in primer zone
            ct_i  = alpha_idx(K4[i], alpha)
            ct_im = alpha_idx(K4[i - P], alpha)
            pt_c  = alpha_chr((ct_i - ct_im) % N, alpha)
            if pt_c != p_char:
                match = False
                break
        if match:
            # Reconstruct full plaintext (primer zone = '?')
            pt_chars = ['?'] * min(P, len(K4))
            for i in range(P, len(K4)):
                ct_i  = alpha_idx(K4[i], alpha)
                ct_im = alpha_idx(K4[i - P], alpha)
                pt_chars.append(alpha_chr((ct_i - ct_im) % N, alpha))
            pt_str = ''.join(pt_chars)
            ne_pos = pt_str.find("NORTHEAST")
            north_pos = pt_str.find("NORTH")
            east_pos  = pt_str.find("EAST")
            print(f"\n  *** P={P} MATCH! ***")
            print(f"  pt = {pt_str}")
            print(f"  pt[63:74] = '{pt_str[63:74]}'")
            if ne_pos >= 0:
                print(f"  *** NORTHEAST at pos {ne_pos} ***")
            elif north_pos >= 0 or east_pos >= 0:
                print(f"  NORTH at {north_pos}, EAST at {east_pos}")
            print(f"  (first {P} chars are primer-dependent)")

    # ── CT-Autokey Beaufort: pt[i] = ct[i-P] - ct[i]  for i >= P
    print("\nCT-Autokey Beaufort (pt[i] = ct[i-P] - ct[i]):")
    for P in range(1, len(K4)):
        if KNOWN_START < P:
            break
        match = True
        for j, p_char in enumerate(KNOWN_PT):
            i = KNOWN_START + j
            if i < P:
                continue
            ct_i  = alpha_idx(K4[i], alpha)
            ct_im = alpha_idx(K4[i - P], alpha)
            pt_c  = alpha_chr((ct_im - ct_i) % N, alpha)
            if pt_c != p_char:
                match = False
                break
        if match:
            pt_chars = ['?'] * min(P, len(K4))
            for i in range(P, len(K4)):
                ct_i  = alpha_idx(K4[i], alpha)
                ct_im = alpha_idx(K4[i - P], alpha)
                pt_chars.append(alpha_chr((ct_im - ct_i) % N, alpha))
            pt_str = ''.join(pt_chars)
            ne_pos = pt_str.find("NORTHEAST")
            north_pos = pt_str.find("NORTH")
            east_pos  = pt_str.find("EAST")
            print(f"\n  *** P={P} MATCH! ***")
            print(f"  pt = {pt_str}")
            print(f"  pt[63:74] = '{pt_str[63:74]}'")
            if ne_pos >= 0:
                print(f"  *** NORTHEAST at pos {ne_pos} ***")
            elif north_pos >= 0 or east_pos >= 0:
                print(f"  NORTH at {north_pos}, EAST at {east_pos}")
            print(f"  (first {P} chars are primer-dependent)")

    # ── Also: PT-Autokey fully analytical ────────────────────────────────────
    # In PT-autokey, the chain is: pt[i] depends on the primer and ALL prior pt chars.
    # There's NO closed-form check like CT-autokey.
    # BUT: we know pt[63:74] = BERLINCLOCK.
    # And in PT-autokey, key[63+j] = pt[63+j-P].
    # So the key at BERLINCLOCK positions IS pt[63-P : 74-P].
    # We need to verify: for each P, does the required key chunk match what the decryption
    # at positions 63-P:74-P would produce?
    # This requires actually running the cipher from the primer forward.
    # We handle this by: given the required key chunk at 63..73 (= ELYOIECBAQK for KRYPTOS),
    # we propagate BACKWARDS to find what primer would generate it.

    print(f"\nPT-Autokey Vigenere - backward primer derivation:")
    # Required key at 63..73 for Vigenere:
    req_key_vig = []
    for j, p_char in enumerate(KNOWN_PT):
        i = KNOWN_START + j
        c = K4[i]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p_char, alpha)
        req_key_vig.append(alpha_chr((ci - pi) % N, alpha))
    req_key_str = ''.join(req_key_vig)
    print(f"  Required key[63:74] = '{req_key_str}'")

    req_key_bft = []
    for j, p_char in enumerate(KNOWN_PT):
        i = KNOWN_START + j
        c = K4[i]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p_char, alpha)
        req_key_bft.append(alpha_chr((pi + ci) % N, alpha))
    req_key_bft_str = ''.join(req_key_bft)
    print(f"  Required key[63:74] (Beaufort) = '{req_key_bft_str}'")

    # For PT-autokey with primer length P (P <= 63):
    # key[63:74] = pt[63-P : 74-P]
    # We know pt[63:74] = BERLINCLOCK, so if 63-P >= 63, we'd need P=0 (trivial).
    # For 0 < P <= 63, pt[63-P : 74-P] spans into UNKNOWN territory.
    # For P >= 11: the window 63-P:74-P doesn't overlap with 63:74.
    # For P < 11: window overlaps.

    # We can analytically compute: given BERLINCLOCK at 63, what must pt[63-P:74-P] be?
    # It must equal req_key_str. But pt[63-P:74-P] is part of the plaintext we're trying to find.
    # What we CAN check: for each P, does the segment ct[63-P:74-P] decrypted with the
    # implied key (which depends on prior pt) equal req_key_str?
    # This is a self-referential constraint.

    # A clean way: if P >= 74 (primer length >= 74), then the entire BERLINCLOCK segment
    # is in the primer zone and primer must include it.
    # If P = 63 exactly, key[63] = pt[0] (first char of plaintext, from primer's first char).
    # So primer[0] must encrypt K4[63] to 'B', etc.

    print(f"\n  Checking if required key segment appears in K4 ciphertext:")
    for P in range(1, 64):
        seg_start = 63 - P
        if seg_start < 0:
            break
        seg = K4[seg_start: seg_start + 11]
        if len(seg) < 11:
            break
        # For PT-autokey, the key chars at 63..73 are pt[63-P..73-P].
        # But the KEY chars we need are req_key_vig. If the ciphertext at those positions,
        # when decrypted by the self-referential key, equals req_key_vig... that's complex.
        # Instead just note: ct[63-P:74-P] = '{seg}', required key = '{req_key_str}'
        if seg == req_key_str:
            print(f"    EXACT MATCH: ct[{seg_start}:{seg_start+11}] = '{seg}' = req_key_vig for P={P}")
            print(f"    This would mean pt[{seg_start}:{seg_start+11}] in a CT-autokey sense...")

print("\n" + "=" * 80)
print("PT-AUTOKEY ANALYTICAL: Find primer by backward propagation")
print("=" * 80)

# For PT-autokey-Vigenere with KRYPTOS alpha:
# Key insight: if we know pt[63:74] = BERLINCLOCK, we know key[63:74].
# In PT-autokey, key[63+j] = pt[63+j-P].
# So pt[63-P+j] = key[63+j] for j=0..10.
# That means: pt at positions 63-P through 73-P equals the required key string.
# Now, decrypting K4 positions 63-P..73-P with the autokey starting from the primer:
# those positions are determined by pt[0..63-P-1].
# We need that decryption to equal the required key string.
# This gives us a TARGET for positions 63-P..73-P.

# We can use this recursively!
# If we know pt[63:74] = BERLINCLOCK, that constrains pt[63-P:74-P] = req_key.
# And from pt[63-P:74-P] = req_key, we get a constraint on pt[63-2P:74-2P] = further_req_key...
# etc., until we reach the primer zone.

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA)]:
    N = len(alpha)
    print(f"\nAlphabet: {alpha_name}")

    # Build required key at positions 63..73
    req_key_at = {}  # position -> required plaintext char
    for j, p_char in enumerate(KNOWN_PT):
        i = KNOWN_START + j
        req_key_at[i] = p_char

    # Derive required key chars at 63..73
    req_key_chars = []
    for j, p_char in enumerate(KNOWN_PT):
        i = KNOWN_START + j
        c = K4[i]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p_char, alpha)
        req_key_chars.append((i, alpha_chr((ci - pi) % N, alpha)))

    print(f"\nRequired key[63:74] = {''.join(k for _,k in req_key_chars)}")

    # For primer length P, the key at positions 63..73 is pt[63-P..73-P].
    # Those pt values are themselves determined by the cipher.
    # For K4 position i (63-P <= i < 74-P):
    #   pt[i] determined by key[i] = pt[i-P]  (if i >= P+P)
    #                           or   key[i] = pt[i-P]  (if i >= P, which it is since i >= 63-P >= 0)
    # This backward propagation can continue but gets exponentially complex.
    # Let's instead propagate FORWARD from required key constraints:

    # For P from 1 to 63:
    #   pt[63-P .. 73-P] = required_key_chars (decoded as key values)
    #   => ct[63-P+j] - key[63-P+j] = req_key_chars[j]  (for Vigenere)
    #   => key[63-P+j] = ct[63-P+j] - req_key_chars[j]  (mod N)
    #   => pt[63-P+j-P] = ct[63-P+j] - req_key_chars[j]  (for positions >= P)
    # This recurses... let's implement it as a forward pass with partial knowledge.

    # Simpler approach for finding primer: assume a primer length P.
    # Then generate all constraints and see if they're self-consistent.

    print("\nSelf-consistency check for each primer length P (PT-Autokey-Vigenere, KRYPTOS):")
    print("We propagate the BERLINCLOCK constraint backwards through the key chain.")

    for P in range(1, 64):
        # Known plaintext constraints from BERLINCLOCK
        known_pt = {}
        for j, p_char in enumerate(KNOWN_PT):
            known_pt[KNOWN_START + j] = p_char

        # Propagate: if we know pt[i], and i >= P, then
        # key[i + P] = pt[i]  => this constrains pt[i+P] via ciphertext.
        # Also: pt[i] constrains key[i] -> pt[i-P] if we go backwards.
        # Let's go backwards from BERLINCLOCK:

        # key[63+j] = pt[63+j-P] for j=0..10  (from autokey rule)
        # pt[63+j-P] is what pt must be at position 63-P+j through 73-P.
        # These pt values at 63-P..73-P must be the required key chars.
        # So we now "know" pt at positions 63-P..73-P = req_key_chars.

        # Extend known_pt backward
        for j in range(len(KNOWN_PT)):
            pos_new = KNOWN_START + j - P
            if 0 <= pos_new < len(K4):
                req_char = req_key_chars[j][1]
                if pos_new in known_pt:
                    if known_pt[pos_new] != req_char:
                        # CONTRADICTION
                        break
                else:
                    known_pt[pos_new] = req_char
        else:
            # Check if these new known values are self-consistent with ciphertext
            # For each newly known pt[i] (at 63-P..73-P), it was produced by:
            # pt[i] = ct[i] - key[i]
            # key[i] = pt[i-P]  (for i >= P)
            # So: known_pt[i] = ct[i] - known_pt[i-P]  (if both known and i >= P)
            consistent = True
            for pos, pt_val in sorted(known_pt.items()):
                if pos < P:
                    continue  # in primer zone, no check
                if (pos - P) in known_pt:
                    # Check: pt[pos] should equal alpha_chr((ct[pos] - pt[pos-P]) % N)
                    ct_pos = K4[pos]
                    ci = alpha_idx(ct_pos, alpha)
                    pi_prev = alpha_idx(known_pt[pos - P], alpha)
                    expected_pt = alpha_chr((ci - pi_prev) % N, alpha)
                    if expected_pt != pt_val:
                        consistent = False
                        break

            if consistent and len(known_pt) > len(KNOWN_PT):
                known_list = sorted(known_pt.items())
                print(f"\n  P={P}: Self-consistent! Known positions: {[k for k,v in known_list]}")
                print(f"  Known plaintext: {dict(known_list)}")
                # Can we determine the primer?
                if P <= 63:
                    primer_constraints = {pos: val for pos, val in known_pt.items() if pos < P}
                    if primer_constraints:
                        print(f"  Primer constraints: {primer_constraints}")

print("\nDone.")
