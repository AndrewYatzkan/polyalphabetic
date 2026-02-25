#!/usr/bin/env python3
"""
K4 Autokey Rigorous Test
========================
The backward-propagation phase in the previous script reported "self-consistent"
for every P from 11-63, but those checks only confirmed that the one-step backward
propagation is trivially consistent (it always is by construction).

This script takes the correct approach:

For PT-Autokey-Vigenere with primer length P:
  - We know pt[63:74] = BERLINCLOCK
  - In PT-autokey, key[i+P] = pt[i] for i >= 0
  - Therefore key[63:74] = pt[63-P:74-P]  ... the required key chars MUST equal pt at 63-P..73-P
  - We know key[63:74] = ELYOIECBAQK (derived from BERLINCLOCK + ciphertext)
  - So pt[63-P:74-P] must equal ELYOIECBAQK

  Now we recursively apply this:
  - pt[63-P:74-P] = ELYOIECBAQK
  - => key[63-P:74-P] = pt[63-2P:74-2P] (for positions >= P, i.e., 63-P >= P, i.e., P <= 31)
  - key[63-P:74-P] can be derived from ciphertext and pt[63-P:74-P]
  - So we get another required segment for pt[63-2P:74-2P]
  - Continue until we reach the primer zone

This recursive propagation gives us the full plaintext (or required primer chars) from
the BERLINCLOCK constraint alone.

The key insight: each chain of propagation back through the primer length P steps
gives another constraint. If these constraints are consistent with the ciphertext,
the autokey hypothesis is validated.

We then use the derived primer to decrypt the full message and check for NORTHEAST.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

KNOWN_PT    = "BERLINCLOCK"
KNOWN_START = 63
KNOWN_LEN   = len(KNOWN_PT)

assert len(K4) == 97

def alpha_idx(c, alpha):
    return alpha.index(c)

def alpha_chr(i, alpha):
    return alpha[i % len(alpha)]

def derive_key_chars(ct_seg, pt_seg, alpha, variant='vigenere'):
    """Given ciphertext and plaintext segments, derive the key chars."""
    N = len(alpha)
    result = []
    for c, p in zip(ct_seg, pt_seg):
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p, alpha)
        if variant == 'vigenere':
            ki = (ci - pi) % N
        else:  # beaufort
            ki = (pi + ci) % N
        result.append(alpha_chr(ki, alpha))
    return ''.join(result)

def pt_from_ct_and_key(ct_seg, key_seg, alpha, variant='vigenere'):
    """Decrypt a ciphertext segment given key segment."""
    N = len(alpha)
    result = []
    for c, k in zip(ct_seg, key_seg):
        ci = alpha_idx(c, alpha)
        ki = alpha_idx(k, alpha)
        if variant == 'vigenere':
            pi = (ci - ki) % N
        else:  # beaufort: pt = key - ct
            pi = (ki - ci) % N
        result.append(alpha_chr(pi, alpha))
    return ''.join(result)

print("=" * 80)
print("K4 AUTOKEY - RIGOROUS BACKWARD PROPAGATION FROM BERLINCLOCK")
print("=" * 80)
print(f"K4 = {K4}")
print(f"K4[63:74] = '{K4[63:74]}' => decrypts to '{KNOWN_PT}'")
print()

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\n{'='*70}")
    print(f"Alphabet: {alpha_name}")
    print(f"{'='*70}")

    for variant in ['vigenere', 'beaufort']:
        print(f"\nVariant: PT-Autokey-{variant.title()}")

        # Required key at positions 63..73
        key_at_63 = derive_key_chars(K4[63:74], KNOWN_PT, alpha, variant)
        print(f"  key[63:74] = '{key_at_63}'")
        print(f"  (This must equal pt[63-P:74-P] for primer length P)")

        # For each primer length P, propagate the constraint backward
        for P in range(1, 64):
            # Full chain of known pt values
            # Start: pt[63:74] = BERLINCLOCK, key[63:74] = key_at_63
            # Step 1: pt[63-P:74-P] = key[63:74] = key_at_63
            # Step 2: key[63-P:74-P] = derive from ct[63-P:74-P] and pt[63-P:74-P]
            #         then pt[63-2P:74-2P] = key[63-P:74-P]
            # etc.

            known_pt_array = ['?'] * len(K4)
            # Initial known: BERLINCLOCK at 63
            for j, c in enumerate(KNOWN_PT):
                known_pt_array[63 + j] = c

            current_key_seg = key_at_63
            current_key_start = 63

            # Propagate backward in steps of P
            contradictions = []
            propagation_steps = 0

            while True:
                prev_start = current_key_start - P
                if prev_start < 0:
                    break
                if prev_start + KNOWN_LEN > len(K4):
                    break

                # pt[prev_start:prev_start+11] must equal current_key_seg
                # Check against already-known values
                contradiction = False
                for j, expected in enumerate(current_key_seg):
                    pos = prev_start + j
                    if pos >= len(K4):
                        break
                    if known_pt_array[pos] != '?' and known_pt_array[pos] != expected:
                        contradictions.append((pos, known_pt_array[pos], expected))
                        contradiction = True
                        break

                if contradiction:
                    break

                # Set these values
                for j, expected in enumerate(current_key_seg):
                    pos = prev_start + j
                    if pos < len(K4):
                        known_pt_array[pos] = expected

                propagation_steps += 1

                # Now derive the key at prev_start..prev_start+10
                # (These key chars tell us about even earlier pt values)
                ct_seg = K4[prev_start:prev_start + KNOWN_LEN]
                pt_seg = current_key_seg[:len(ct_seg)]
                if len(ct_seg) < KNOWN_LEN:
                    break

                new_key_seg = derive_key_chars(ct_seg, pt_seg, alpha, variant)
                current_key_seg = new_key_seg
                current_key_start = prev_start

            # Now we have a partial plaintext. If propagation went all the way
            # to position 0, we can also figure out primer constraints.
            # The primer positions (0..P-1) that we know constrain the primer.

            known_count = sum(1 for c in known_pt_array if c != '?')

            if known_count > KNOWN_LEN:
                # Meaningful propagation happened
                primer_known = {}
                for i in range(P):
                    if known_pt_array[i] != '?':
                        primer_known[i] = known_pt_array[i]

                # Now fill in remaining unknown positions using the primer
                # Positions P..97 can be filled in using propagation
                # But we need to verify consistency.

                # For positions that we know, verify they match what the cipher
                # would produce if decrypted forward with the derived primer.
                # Build the primer: known positions are constrained, unknown are free.
                # If all primer positions are known, we can do a complete decryption.

                all_primer_known = len(primer_known) == P and all(i in primer_known for i in range(P))

                if all_primer_known or propagation_steps >= 2:
                    pt_str = ''.join(known_pt_array)

                    # Check for NORTHEAST in known positions
                    ne_found = 'NORTHEAST' in pt_str
                    north_found = 'NORTH' in pt_str
                    east_found = 'EAST' in pt_str

                    interesting = ne_found or (propagation_steps >= 5 and known_count > 20)

                    if interesting or all_primer_known:
                        print(f"\n  P={P}, propagation_steps={propagation_steps}, known_chars={known_count}/{len(K4)}")
                        print(f"  pt = {pt_str}")
                        print(f"  Contradictions: {contradictions}")
                        if ne_found:
                            print(f"  *** NORTHEAST FOUND! at pos {pt_str.find('NORTHEAST')} ***")
                        elif north_found or east_found:
                            print(f"  NORTH at {pt_str.find('NORTH')}, EAST at {pt_str.find('EAST')}")

                        if all_primer_known:
                            primer = ''.join(primer_known[i] for i in range(P))
                            print(f"  Fully determined primer: '{primer}'")

                            # Full decryption with this primer
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

                            pt_full_str = ''.join(pt_full)
                            print(f"  Full decryption: {pt_full_str}")
                            if pt_full_str[63:74] == KNOWN_PT:
                                print(f"  *** BERLINCLOCK confirmed at pos 63! ***")
                            if 'NORTHEAST' in pt_full_str:
                                print(f"  *** NORTHEAST at pos {pt_full_str.find('NORTHEAST')}! ***")


# ── Section 2: Forward propagation from BERLINCLOCK ──────────────────────────

print("\n" + "=" * 80)
print("SECTION 2: FORWARD PROPAGATION FROM BERLINCLOCK")
print("=" * 80)
print()
print("In PT-autokey, knowing pt[63:74] = BERLINCLOCK tells us:")
print("  key[63+P:74+P] = BERLINCLOCK  (the key at those future positions)")
print("  i.e., pt[74:74+P+KNOWN_LEN-P] = BERLINCLOCK shifted (more precisely:)")
print("  key[63+P] = pt[63] = B => allows decrypting ct[63+P]")
print("  key[64+P] = pt[64] = E => allows decrypting ct[64+P]")
print("  etc.")
print()

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\n--- Alphabet: {alpha_name} ---")

    for variant in ['vigenere', 'beaufort']:
        print(f"\nVariant: PT-Autokey-{variant.title()}")

        for P in range(1, 64):
            # Forward: pt[63+j] = B,E,R,L,I,N,C,L,O,C,K
            # => at position 63+P+j, the key is pt[63+j] = BERLINCLOCK[j]
            # => pt[63+P+j] can be computed from ct[63+P+j] and key = BERLINCLOCK[j]

            known_pt_array = ['?'] * len(K4)
            for j, c in enumerate(KNOWN_PT):
                pos = 63 + j
                if pos < len(K4):
                    known_pt_array[pos] = c

            # Propagate forward
            step = 0
            while True:
                new_known = {}
                for j, c in enumerate(KNOWN_PT):
                    src_pos = 63 + j
                    dst_pos = src_pos + P
                    if dst_pos >= len(K4):
                        continue
                    if known_pt_array[dst_pos] != '?':
                        continue
                    # key at dst_pos = pt[src_pos] = c
                    ct_c = K4[dst_pos]
                    if variant == 'vigenere':
                        ci = alpha_idx(ct_c, alpha)
                        ki = alpha_idx(c, alpha)
                        pt_c = alpha_chr((ci - ki) % N, alpha)
                    else:  # beaufort
                        ci = alpha_idx(ct_c, alpha)
                        ki = alpha_idx(c, alpha)
                        pt_c = alpha_chr((ki - ci) % N, alpha)
                    new_known[dst_pos] = pt_c

                if not new_known:
                    break

                for pos, val in new_known.items():
                    known_pt_array[pos] = val

                # Now propagate from the newly known values
                # key at pos + P = pt[pos] for newly known pos values
                changed = True
                while changed:
                    changed = False
                    for pos in range(len(K4)):
                        if known_pt_array[pos] == '?':
                            continue
                        next_pos = pos + P
                        if next_pos >= len(K4):
                            continue
                        if known_pt_array[next_pos] != '?':
                            continue
                        ct_c = K4[next_pos]
                        key_c = known_pt_array[pos]
                        if variant == 'vigenere':
                            ci = alpha_idx(ct_c, alpha)
                            ki = alpha_idx(key_c, alpha)
                            pt_c = alpha_chr((ci - ki) % N, alpha)
                        else:
                            ci = alpha_idx(ct_c, alpha)
                            ki = alpha_idx(key_c, alpha)
                            pt_c = alpha_chr((ki - ci) % N, alpha)
                        known_pt_array[next_pos] = pt_c
                        changed = True
                break

            known_count = sum(1 for c in known_pt_array if c != '?')
            pt_str = ''.join(known_pt_array)

            if 'NORTHEAST' in pt_str:
                ne_pos = pt_str.find('NORTHEAST')
                print(f"\n  *** P={P}: NORTHEAST found at pos {ne_pos}! known={known_count} ***")
                print(f"  pt = {pt_str}")

            # Check for NORTH and EAST separately in known positions
            known_only = [c if c != '?' else '_' for c in known_pt_array]
            known_str = ''.join(known_only)
            # Check contiguous known sections for NORTH/EAST
            # (simple: just check for NORTH and EAST in the string)
            if 'NORTH' in known_str and 'EAST' in known_str:
                print(f"  P={P}: NORTH at {known_str.find('NORTH')}, EAST at {known_str.find('EAST')}")
                print(f"  pt = {pt_str}")


# ── Section 3: Complete consistency test for CT-Autokey ──────────────────────

print("\n" + "=" * 80)
print("SECTION 3: CT-AUTOKEY - WHAT DOES THE FULL PLAINTEXT LOOK LIKE?")
print("(showing best candidates from phase 6 - all possible primer lengths)")
print("=" * 80)

print("\nCT-Autokey-Vigenere with KRYPTOS alphabet (showing all where BERLINCLOCK@63):")
alpha = KRYPTOS_ALPHA
N = len(alpha)
best_ne_candidates = []

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
        pt_c  = alpha_chr((ct_i - ct_im) % N, alpha)
        if pt_c != p_char:
            match = False
            break
    if match:
        pt_chars = ['?'] * min(P, len(K4))
        for i in range(P, len(K4)):
            ct_i  = alpha_idx(K4[i], alpha)
            ct_im = alpha_idx(K4[i - P], alpha)
            pt_chars.append(alpha_chr((ct_i - ct_im) % N, alpha))
        pt_str = ''.join(pt_chars)
        ne_pos = pt_str.find("NORTHEAST")
        north_pos = pt_str.find("NORTH")
        east_pos  = pt_str.find("EAST")

        print(f"\n  P={P}: pt={pt_str}")
        if ne_pos >= 0:
            print(f"  *** NORTHEAST at pos {ne_pos}! ***")
            best_ne_candidates.append((P, 'CT-Vigenere', 'KRYPTOS', pt_str))
        elif north_pos >= 0 or east_pos >= 0:
            print(f"  NORTH@{north_pos}, EAST@{east_pos}")
        # Check for other known K4 words
        for word in ['SHADOW', 'LAYER', 'BENEATH', 'BELOW', 'UNDER', 'CLOCK', 'BERLIN', 'DIGETAL']:
            if word in pt_str:
                print(f"  Found '{word}' at pos {pt_str.find(word)}")

if best_ne_candidates:
    print("\n" + "!"*70)
    print("!!! NORTHEAST FOUND IN CT-AUTOKEY DECRYPTION !!!")
    for P, method, alpha_name, pt in best_ne_candidates:
        print(f"\nP={P}, {method}, {alpha_name}: {pt}")

print("\n" + "=" * 80)
print("CT-Autokey-Beaufort with KRYPTOS alphabet:")
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
        print(f"\n  P={P}: pt={pt_str}")
        if ne_pos >= 0:
            print(f"  *** NORTHEAST at pos {ne_pos}! ***")
        elif north_pos >= 0 or east_pos >= 0:
            print(f"  NORTH@{north_pos}, EAST@{east_pos}")

print("\n" + "=" * 80)
print("STANDARD ALPHABET CT-Autokey variants:")
alpha = STANDARD_ALPHA
N = len(alpha)

for variant_name, op in [("Vigenere", lambda ci, cm: (ci - cm) % N),
                           ("Beaufort", lambda ci, cm: (cm - ci) % N)]:
    print(f"\nCT-Autokey-{variant_name}, STANDARD:")
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
            pt_c  = alpha_chr(op(ct_i, ct_im), alpha)
            if pt_c != p_char:
                match = False
                break
        if match:
            pt_chars = ['?'] * min(P, len(K4))
            for i in range(P, len(K4)):
                ct_i  = alpha_idx(K4[i], alpha)
                ct_im = alpha_idx(K4[i - P], alpha)
                pt_chars.append(alpha_chr(op(ct_i, ct_im), alpha))
            pt_str = ''.join(pt_chars)
            ne_pos = pt_str.find("NORTHEAST")
            north_pos = pt_str.find("NORTH")
            east_pos  = pt_str.find("EAST")
            print(f"\n  P={P}: pt={pt_str}")
            if ne_pos >= 0:
                print(f"  *** NORTHEAST at pos {ne_pos}! ***")
            elif north_pos >= 0 or east_pos >= 0:
                print(f"  NORTH@{north_pos}, EAST@{east_pos}")

print("\n" + "=" * 80)
print("COMPLETE - ALL AUTOKEY VARIANTS TESTED")
print("=" * 80)
