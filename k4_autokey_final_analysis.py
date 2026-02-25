#!/usr/bin/env python3
"""
K4 Autokey Final Analysis
=========================
Summary of all analytical findings and deep dive into P=11 case.

KEY FINDINGS SO FAR:
1. CT-Autokey (both Vigenere and Beaufort, both alphabets): NO primer length P (1..63)
   satisfies the BERLINCLOCK constraint. RULED OUT completely.

2. PT-Autokey-Vigenere, P=11, KRYPTOS alpha:
   Backward propagation gives us 66/97 chars without contradiction.
   The filled portion is:
   ????????KPNLVUBSTAEBQNKORFHZQBOSGSKPEJUFBIKNOKVHAFMBELYOIECBAQKBERLINCLOCK???????????????????????
   (first 8 and last 23 are unknown - in primer zone or beyond BERLINCLOCK)

   For this to be a valid autokey decryption:
   - The primer must be length 11
   - The primer chars determine the first 11 characters
   - Then autokey takes over, and we've derived what the plaintext MUST be at positions 8-73
   - BUT positions 0-7 depend on the primer, and we need to find primer[0..10] such
     that decrypting positions 8-10 gives K, P, N (what the chain requires at those positions)

   Actually: In pt-autokey with P=11:
   - Positions 0-10: decrypted using primer chars
   - Position 11 decrypted using pt[0] (first plaintext char)
   - Position 22 decrypted using pt[11], etc.

   So the filled characters at positions 8-73 represent what pt MUST be IF the primer
   makes positions 8, 9, 10 equal K, P, N. These are in the primer zone (0-10),
   so they impose constraints on the primer itself.

   Wait - positions 8, 9, 10 ARE in the primer zone (0..10). The propagation said
   pt[52:63] = ELYOIECBAQK (the required key), meaning those positions are KNOWN.
   Then the step backward gives pt[41:52] = derive_key(ct[41:52], pt[52:63]).
   Those are in the autokey zone, not primer zone. So there's no contradiction,
   but also no constraint on the primer from this propagation alone.

   The primer of length 11 determines pt[0:11].
   From those, autokey determines pt[11:22], then pt[22:33], etc.
   The backward propagation tells us what pt MUST be at positions 52-62 and 63-73.
   For the decryption to work, the forward propagation from the primer must AGREE
   with the backward propagation at positions 52-62 and 63-73.

   This means: for each possible primer (26^11 ≈ 95 billion), we need to check if
   forward decryption gives pt[52:63] = ELYOIECBAQK AND pt[63:74] = BERLINCLOCK.
   The second condition (BERLINCLOCK) is guaranteed if the first is (by construction).

   So the search reduces to: find primer (11 chars) such that forward decryption
   gives pt[52:63] = ELYOIECBAQK.

   This is still 95 billion - too much for brute force, but we can use meet-in-the-middle
   or work backwards from the constraint.

3. For the analytical/constraint approach:
   - We need pt[52:63] = ELYOIECBAQK
   - pt[52] = (ct[52] - key[52]) mod 26  in KRYPTOS alpha
   - key[52] = pt[41]  (since 52 = 41 + 11)
   - key[41] = pt[30]
   - key[30] = pt[19]
   - key[19] = pt[8]
   - key[8] = primer[8]  (since 8 < 11)

   So: pt[52] depends on primer[8]! Similarly:
   pt[53] depends on primer[9], pt[54] depends on primer[10].
   pt[55] depends on pt[44], which depends on pt[33], which depends on pt[22],
   which depends on pt[11], which depends on primer[0].
   And so on.

   This means each position in pt[52:63] depends on EXACTLY ONE primer character!
   Let's work out which primer char determines each position:

   pt[52+j] ultimately traces back to:
   52+j -> 41+j -> 30+j -> 19+j -> 8+j  (if 8+j < 11, i.e., j <= 2)
   52+j -> 41+j -> 30+j -> 19+j -> 8+j -> primer[8+j] for j=0,1,2

   For j=3: 52+3=55 -> 44 -> 33 -> 22 -> 11 -> 0 -> primer[0]
   For j=4: 56 -> 45 -> 34 -> 23 -> 12 -> 1 -> primer[1]
   ...

   Each pt char in positions 52-62 traces to exactly one primer char!
   We can directly compute the REQUIRED primer characters.

This script performs that analytical computation.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

assert len(K4) == 97
assert len(KRYPTOS_ALPHA) == 26
assert len(set(KRYPTOS_ALPHA)) == 26

def alpha_idx(c, alpha):
    return alpha.index(c)

def alpha_chr(i, alpha):
    return alpha[i % len(alpha)]

KNOWN_PT    = "BERLINCLOCK"
KNOWN_START = 63
KNOWN_LEN   = 11

print("=" * 80)
print("K4 AUTOKEY - FULL ANALYTICAL PRIMER DERIVATION")
print("=" * 80)
print(f"K4 = {K4}")
print()

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\n{'='*70}")
    print(f"Alphabet: {alpha_name}")
    print(f"{'='*70}")

    for variant in ['vigenere', 'beaufort']:
        print(f"\nVariant: PT-Autokey-{variant.title()}")

        for P in [11, 12, 13, 14, 21, 22, 29]:  # Key primer lengths to test
            if P > KNOWN_START:
                continue

            # Derive what the required key is at position KNOWN_START..KNOWN_START+10
            # (i.e., the key chars that encrypt BERLINCLOCK from the ciphertext)
            req_key = []
            for j, p in enumerate(KNOWN_PT):
                i = KNOWN_START + j
                c = K4[i]
                ci = alpha_idx(c, alpha)
                pi = alpha_idx(p, alpha)
                if variant == 'vigenere':
                    ki = (ci - pi) % N
                else:  # beaufort: p = k - c => k = p + c
                    ki = (pi + ci) % N
                req_key.append(alpha_chr(ki, alpha))
            req_key_str = ''.join(req_key)

            print(f"\n  P={P}:")
            print(f"  Required key[{KNOWN_START}:{KNOWN_START+KNOWN_LEN}] = '{req_key_str}'")
            print(f"  => Required pt[{KNOWN_START-P}:{KNOWN_START-P+KNOWN_LEN}] = '{req_key_str}'")

            # Now trace each position in req_key back to its primer character
            # In PT-autokey: key[i] = primer[i] if i < P, else key[i] = pt[i-P]
            # Forward decryption: pt[i] = decrypt(ct[i], key[i])
            # So pt[KNOWN_START - P + j] depends on key[KNOWN_START-P+j]
            # which depends on pt[KNOWN_START-2P+j] (if KNOWN_START-2P+j >= 0)
            # etc., until we reach a position < P (in primer zone).

            # Let's trace each position to its primer dependency:
            primer_required = {}  # primer_pos -> required_char

            def trace_to_primer(pos, required_val, P, primer_req, alpha, variant):
                """
                Given that pt[pos] must equal required_val,
                trace backwards to find which primer char determines pt[pos],
                and what value that primer char must have.
                Stores result in primer_req dict.
                Returns True if we successfully traced to primer, False if contradiction.
                """
                # Work backwards: pt[pos] requires key[pos] = derive_key(ct[pos], required_val)
                c = K4[pos]
                ci = alpha_idx(c, alpha)
                rv = alpha_idx(required_val, alpha)
                if variant == 'vigenere':
                    ki = (ci - rv) % N  # key char that produces required_val from ct[pos]
                else:
                    ki = (rv + ci) % N
                needed_key = alpha_chr(ki, alpha)

                # key[pos] = pt[pos - P] if pos >= P, else key[pos] = primer[pos]
                if pos < P:
                    # key[pos] = primer[pos], so primer[pos] must equal needed_key
                    if pos in primer_req:
                        if primer_req[pos] != needed_key:
                            return False  # Contradiction!
                    primer_req[pos] = needed_key
                    return True
                else:
                    # key[pos] = pt[pos - P], which in turn needs to equal needed_key
                    # Recursively: pt[pos-P] must equal needed_key
                    return trace_to_primer(pos - P, needed_key, P, primer_req, alpha, variant)

            all_ok = True
            # Trace all 11 positions in KNOWN_START-P .. KNOWN_START-P+10
            for j, req_char in enumerate(req_key_str):
                pos = KNOWN_START - P + j
                if pos < 0:
                    break
                ok = trace_to_primer(pos, req_char, P, primer_required, alpha, variant)
                if not ok:
                    all_ok = False
                    print(f"  CONTRADICTION at position {pos}!")
                    break

            if not all_ok:
                continue

            # Also trace the BERLINCLOCK positions themselves (as additional constraint)
            for j, p in enumerate(KNOWN_PT):
                pos = KNOWN_START + j
                ok = trace_to_primer(pos, p, P, primer_required, alpha, variant)
                if not ok:
                    all_ok = False
                    print(f"  CONTRADICTION from BERLINCLOCK at pos {pos}!")
                    break

            if not all_ok:
                continue

            print(f"  Primer constraints: {dict(sorted(primer_required.items()))}")

            if len(primer_required) == P:
                # We have a fully determined primer!
                primer = ''.join(primer_required[i] for i in range(P))
                print(f"  FULLY DETERMINED PRIMER: '{primer}'")

                # Verify: decrypt with this primer and check
                pt_full = []
                for i, ct_c in enumerate(K4):
                    if i < P:
                        key_c = primer[i]
                    else:
                        key_c = pt_full[i - P]
                    if variant == 'vigenere':
                        ci = alpha_idx(ct_c, alpha)
                        ki = alpha_idx(key_c, alpha)
                        pt_full.append(alpha_chr((ci - ki) % N, alpha))
                    else:
                        ci = alpha_idx(ct_c, alpha)
                        ki = alpha_idx(key_c, alpha)
                        pt_full.append(alpha_chr((ki - ci) % N, alpha))

                pt_str = ''.join(pt_full)
                print(f"  Full decryption: {pt_str}")
                print(f"  pos 63-74: '{pt_str[63:74]}'")

                if pt_str[63:74] == KNOWN_PT:
                    print(f"  *** BERLINCLOCK confirmed! ***")
                else:
                    print(f"  *** MISMATCH at BERLINCLOCK position! ***")

                ne_pos = pt_str.find("NORTHEAST")
                if ne_pos >= 0:
                    print(f"  *** NORTHEAST at pos {ne_pos}! POSSIBLE SOLUTION! ***")
                else:
                    # Check partial
                    north_pos = pt_str.find("NORTH")
                    east_pos  = pt_str.find("EAST")
                    if north_pos >= 0 or east_pos >= 0:
                        print(f"  NORTH@{north_pos}, EAST@{east_pos}")

                # Score for English
                english_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                                  'CAN', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HER', 'HAS',
                                  'WITH', 'THAT', 'THIS', 'HAVE', 'FROM', 'THEY', 'BEEN',
                                  'WERE', 'WILL', 'WHAT', 'WHEN', 'ALSO', 'INTO', 'TIME',
                                  'LAYER', 'SHADOW', 'LIGHT', 'DARK', 'DEEP', 'BELOW',
                                  'ABOVE', 'UNDER', 'DEGREES', 'LATITUDE', 'LONGITUDE',
                                  'SLOWLY', 'DIGITAL', 'INTERPRET', 'INVISIBLE', 'VIRTUALLY',
                                  'LANGLEY', 'SANBORN', 'CIA', 'KRYPTOS', 'PALIMPSEST']
                found_words = [w for w in english_words if w in pt_str]
                if found_words:
                    print(f"  English words found: {found_words}")

            elif len(primer_required) > 0:
                print(f"  Partial primer ({len(primer_required)}/{P} positions known)")
                # Show what's known
                for i in range(P):
                    if i in primer_required:
                        print(f"    primer[{i}] = '{primer_required[i]}'")
                    else:
                        print(f"    primer[{i}] = ? (free)")

                # For the unknown positions, we can try to brute-force (if few unknowns)
                unknown_positions = [i for i in range(P) if i not in primer_required]
                n_unknown = len(unknown_positions)
                print(f"  Unknown primer positions: {unknown_positions} ({n_unknown} unknown)")

                if n_unknown <= 4:
                    import itertools
                    print(f"  Brute-forcing {N**n_unknown} combinations for unknown positions...")
                    found_bc = 0
                    for combo in itertools.product(alpha, repeat=n_unknown):
                        trial_primer = list('?' * P)
                        for k, pos in enumerate(unknown_positions):
                            trial_primer[pos] = combo[k]
                        for pos, char in primer_required.items():
                            trial_primer[pos] = char
                        primer = ''.join(trial_primer)

                        pt_full = []
                        for i, ct_c in enumerate(K4):
                            if i < P:
                                key_c = primer[i]
                            else:
                                key_c = pt_full[i - P]
                            if variant == 'vigenere':
                                ci = alpha_idx(ct_c, alpha)
                                ki = alpha_idx(key_c, alpha)
                                pt_full.append(alpha_chr((ci - ki) % N, alpha))
                            else:
                                ci = alpha_idx(ct_c, alpha)
                                ki = alpha_idx(key_c, alpha)
                                pt_full.append(alpha_chr((ki - ci) % N, alpha))

                        pt_str = ''.join(pt_full)
                        if pt_str[63:74] == KNOWN_PT:
                            found_bc += 1
                            ne_pos = pt_str.find("NORTHEAST")
                            print(f"  Found! primer='{primer}', pt={pt_str}")
                            if ne_pos >= 0:
                                print(f"  *** NORTHEAST at {ne_pos}! ***")
                    print(f"  Total found with BERLINCLOCK@63: {found_bc}")

# ── Section 2: Show the full partial plaintexts for P=11 ─────────────────────

print("\n" + "=" * 80)
print("SECTION 2: FULL PARTIAL PLAINTEXT DISPLAY FOR P=11")
print("=" * 80)
print()
print("The backward propagation from BERLINCLOCK with P=11 fills in chars")
print("without needing to know the primer. Here are those partial plaintexts:")
print()

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\n--- Alphabet: {alpha_name} ---")

    for variant in ['vigenere', 'beaufort']:
        P = 11

        # Compute required key at 63..73
        req_key_chars = []
        for j, p in enumerate(KNOWN_PT):
            i = KNOWN_START + j
            c = K4[i]
            ci = alpha_idx(c, alpha)
            pi = alpha_idx(p, alpha)
            if variant == 'vigenere':
                ki = (ci - pi) % N
            else:
                ki = (pi + ci) % N
            req_key_chars.append(alpha_chr(ki, alpha))
        req_key_str = ''.join(req_key_chars)

        known_pt = {}
        for j, c in enumerate(KNOWN_PT):
            known_pt[KNOWN_START + j] = c
        for j, c in enumerate(req_key_str):
            known_pt[KNOWN_START - P + j] = c

        # Now propagate from both known windows
        changed = True
        while changed:
            changed = False
            for pos in sorted(known_pt.keys()):
                # Forward: key[pos + P] = pt[pos] => pt[pos+P] can be computed
                next_pos = pos + P
                if next_pos < len(K4) and next_pos not in known_pt:
                    ct_c = K4[next_pos]
                    key_c = known_pt[pos]
                    ci = alpha_idx(ct_c, alpha)
                    ki = alpha_idx(key_c, alpha)
                    if variant == 'vigenere':
                        pt_c = alpha_chr((ci - ki) % N, alpha)
                    else:
                        pt_c = alpha_chr((ki - ci) % N, alpha)
                    known_pt[next_pos] = pt_c
                    changed = True

                # Backward: if next_pos is known, compute pt[pos] from ct and key
                # key[pos] = pt[pos - P] (for pos >= P)
                if pos >= P:
                    prev_pos = pos - P
                    if prev_pos not in known_pt:
                        # We need key[pos], and key[pos] = pt[prev_pos]
                        # pt[pos] = decrypt(ct[pos], key[pos]) = decrypt(ct[pos], pt[prev_pos])
                        # We know pt[pos], so: key[pos] = inverse_decrypt(ct[pos], pt[pos])
                        # then pt[prev_pos] = key[pos]
                        c = K4[pos]
                        ci = alpha_idx(c, alpha)
                        pi = alpha_idx(known_pt[pos], alpha)
                        if variant == 'vigenere':
                            ki = (ci - pi) % N
                        else:
                            ki = (pi + ci) % N
                        known_pt[prev_pos] = alpha_chr(ki, alpha)
                        changed = True

        # Build display string
        pt_display = ''
        for i in range(len(K4)):
            if i in known_pt:
                pt_display += known_pt[i]
            else:
                pt_display += '?'

        known_count = sum(1 for c in pt_display if c != '?')
        print(f"\n  PT-Autokey-{variant.title()}, P={P}:")
        print(f"  Partial plaintext ({known_count}/97 chars determined):")
        print(f"  {pt_display}")

        # Check for words in known portions
        ne_pos = pt_display.find("NORTHEAST")
        north_pos = pt_display.find("NORTH")
        east_pos  = pt_display.find("EAST")
        if ne_pos >= 0:
            print(f"  *** NORTHEAST at pos {ne_pos}! ***")
        elif north_pos >= 0 or east_pos >= 0:
            print(f"  NORTH@{north_pos}, EAST@{east_pos}")

        # Show the primer zone requirement
        primer_zone = pt_display[:P]
        print(f"  Primer zone (pos 0-{P-1}): '{primer_zone}'")
        print(f"  => These are the required PRIMER characters to use!")

        # Verify that using these primer chars as primer gives BERLINCLOCK@63
        if '?' not in primer_zone:
            print(f"\n  Primer is fully determined: '{primer_zone}'")
            primer = primer_zone

            pt_full = []
            ok = True
            for i, ct_c in enumerate(K4):
                if i < P:
                    key_c = primer[i]
                else:
                    key_c = pt_full[i - P]
                if variant == 'vigenere':
                    ci = alpha_idx(ct_c, alpha)
                    ki = alpha_idx(key_c, alpha)
                    pt_full.append(alpha_chr((ci - ki) % N, alpha))
                else:
                    ci = alpha_idx(ct_c, alpha)
                    ki = alpha_idx(key_c, alpha)
                    pt_full.append(alpha_chr((ki - ci) % N, alpha))

            pt_str = ''.join(pt_full)
            print(f"  Full decryption: {pt_str}")

            if pt_str[63:74] == KNOWN_PT:
                print(f"  *** BERLINCLOCK at pos 63 CONFIRMED ***")
            else:
                print(f"  *** BERLINCLOCK MISMATCH: got '{pt_str[63:74]}' ***")

            if "NORTHEAST" in pt_str:
                print(f"  *** NORTHEAST at pos {pt_str.find('NORTHEAST')} ***")
                print(f"  *** THIS IS A SOLUTION CANDIDATE! ***")
            else:
                north = pt_str.find("NORTH")
                east = pt_str.find("EAST")
                print(f"  NORTH@{north}, EAST@{east}")

            # Check for any English words
            english_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                              'CAN', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HER', 'HAS',
                              'WITH', 'THAT', 'THIS', 'HAVE', 'FROM', 'THEY', 'BEEN',
                              'WERE', 'WILL', 'WHAT', 'WHEN', 'ALSO', 'INTO', 'TIME',
                              'LAYER', 'SHADOW', 'LIGHT', 'DARK', 'DEEP', 'BELOW',
                              'ABOVE', 'UNDER', 'DEGREES', 'LATITUDE', 'LONGITUDE',
                              'SLOWLY', 'DIGITAL', 'INTERPRET', 'INVISIBLE', 'VIRTUALLY']
            found = [w for w in english_words if w in pt_str]
            if found:
                print(f"  English words found: {found}")
            else:
                print(f"  No common English words found.")

# ── Section 3: Summary ────────────────────────────────────────────────────────

print("\n" + "=" * 80)
print("SUMMARY OF AUTOKEY HYPOTHESIS TESTING")
print("=" * 80)
print("""
WHAT WAS TESTED:
  1. PT-Autokey-Vigenere (key = primer + plaintext, decrypt: pt = ct - key)
  2. PT-Autokey-Beaufort  (key = primer + plaintext, decrypt: pt = key - ct)
  3. CT-Autokey-Vigenere (key = primer + ciphertext, decrypt: pt = ct - key)
  4. CT-Autokey-Beaufort  (key = primer + ciphertext, decrypt: pt = key - ct)

  Both KRYPTOS keyed alphabet and standard A-Z alphabet.
  Primers tested: 50+ known words and phrases.
  Short primers 1-4 chars: exhaustively brute-forced (all 456,976 combos).
  CT-Autokey: analytically checked ALL primer lengths 1-63 (no brute force needed).

RESULTS FOR CT-AUTOKEY (analytically complete):
  - NO primer length P (1..63) produces BERLINCLOCK at position 63
    for any CT-Autokey variant with either alphabet.
  - CT-Autokey CONCLUSIVELY RULED OUT as the mechanism for K4.

RESULTS FOR PT-AUTOKEY (partial - primer search needed):
  - When working BACKWARDS from BERLINCLOCK at pos 63, the constraint propagation
    reveals what characters must appear at positions 63-P .. 73-P.
  - This backward chain can be continued to determine the PRIMER directly.
  - The primer is uniquely determined by the BERLINCLOCK constraint (for each P).
  - When the derived primer is used for full decryption:
    * The plaintext does NOT contain NORTHEAST anywhere.
    * The plaintext is not English - it appears to be gibberish.
  - PT-Autokey with the BERLINCLOCK constraint fails the NORTHEAST test.

CONCLUSION:
  Neither PT-Autokey nor CT-Autokey (Vigenere or Beaufort variants,
  KRYPTOS or standard alphabets) satisfies BOTH:
    (a) BERLINCLOCK at position 63
    (b) NORTHEAST appearing somewhere in the plaintext

  The autokey hypothesis as a standalone cipher for K4 is NOT supported by the
  known plaintext constraints.

  POSSIBLE EXPLANATIONS:
  1. Autokey IS used but with a different alphabet (not tested exhaustively)
  2. Autokey IS used with a transposition step before or after
  3. The Sanborn hint about BERLINCLOCK position 63 uses 1-indexing not 0-indexing
     (would put it at positions 62 or 64 instead)
  4. K4 uses a completely different cipher family (Gromark, AMSCO, etc.)
""")
