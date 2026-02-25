#!/usr/bin/env python3
"""
K4 AUTOKEY CIPHER HYPOTHESIS TEST
==================================
Tests plaintext autokey and ciphertext autokey using KRYPTOS keyed alphabet.
In autokey, the key stream is: primer + plaintext (or primer + ciphertext).

Known constraints:
  - BERLINCLOCK must appear at position 63 (Sanborn confirmed)
  - NORTHEAST must appear somewhere (Sanborn confirmed)
  - K4 length: 97 chars
  - Alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ (26 chars, no P duplicate - P appears once)

Ciphertext:
  OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
  Position 63 (0-indexed): S  (BERLINCLOCK starts here → positions 63-73)
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

assert len(K4) == 97, f"K4 length should be 97, got {len(K4)}"
assert len(KRYPTOS_ALPHA) == 26, f"KRYPTOS alpha should be 26 chars, got {len(KRYPTOS_ALPHA)}"
assert len(set(KRYPTOS_ALPHA)) == 26, "KRYPTOS alpha must have 26 unique chars"

# Confirm position 63
print("K4 ciphertext:")
print(K4)
print("Position markers:")
for i in range(0, 100, 10):
    if i < len(K4):
        print(f"  pos {i:2d}: {K4[i]}")
print(f"  K4[63:74] = '{K4[63:74]}'  (this decrypts to BERLINCLOCK)")
print()

# ── Core cipher primitives ──────────────────────────────────────────────────

def alpha_idx(c, alpha):
    return alpha.index(c)

def alpha_chr(i, alpha):
    return alpha[i % len(alpha)]

def vigenere_decrypt_char(ct_char, key_char, alpha):
    """Standard Vigenere decrypt: P = C - K (mod 26)."""
    c = alpha_idx(ct_char, alpha)
    k = alpha_idx(key_char, alpha)
    return alpha_chr((c - k) % len(alpha), alpha)

def vigenere_encrypt_char(pt_char, key_char, alpha):
    """Standard Vigenere encrypt: C = P + K (mod 26)."""
    p = alpha_idx(pt_char, alpha)
    k = alpha_idx(key_char, alpha)
    return alpha_chr((p + k) % len(alpha), alpha)

def beaufort_decrypt_char(ct_char, key_char, alpha):
    """Beaufort variant: P = K - C (mod 26)."""
    c = alpha_idx(ct_char, alpha)
    k = alpha_idx(key_char, alpha)
    return alpha_chr((k - c) % len(alpha), alpha)

# ── Autokey variants ─────────────────────────────────────────────────────────

def pt_autokey_decrypt(ciphertext, primer, alpha):
    """
    Plaintext autokey decryption.
    Key stream = primer + plaintext[0] + plaintext[1] + ...
    Decrypt: P[i] = C[i] - key[i]  (Vigenere)
    """
    pt = []
    plen = len(primer)
    for i, c in enumerate(ciphertext):
        if i < plen:
            key_char = primer[i]
        else:
            key_char = pt[i - plen]
        pt.append(vigenere_decrypt_char(c, key_char, alpha))
    return ''.join(pt)

def ct_autokey_decrypt(ciphertext, primer, alpha):
    """
    Ciphertext autokey decryption.
    Key stream = primer + ciphertext[0] + ciphertext[1] + ...
    Decrypt: P[i] = C[i] - key[i]  (Vigenere)
    Note: key[plen + j] = C[j], so this is purely mechanical.
    """
    pt = []
    plen = len(primer)
    for i, c in enumerate(ciphertext):
        if i < plen:
            key_char = primer[i]
        else:
            key_char = ciphertext[i - plen]
        pt.append(vigenere_decrypt_char(c, key_char, alpha))
    return ''.join(pt)

def pt_autokey_beaufort_decrypt(ciphertext, primer, alpha):
    """Plaintext autokey with Beaufort variant: P[i] = key[i] - C[i]."""
    pt = []
    plen = len(primer)
    for i, c in enumerate(ciphertext):
        if i < plen:
            key_char = primer[i]
        else:
            key_char = pt[i - plen]
        pt.append(beaufort_decrypt_char(c, key_char, alpha))
    return ''.join(pt)

def ct_autokey_beaufort_decrypt(ciphertext, primer, alpha):
    """Ciphertext autokey with Beaufort variant: P[i] = key[i] - C[i]."""
    pt = []
    plen = len(primer)
    for i, c in enumerate(ciphertext):
        if i < plen:
            key_char = primer[i]
        else:
            key_char = ciphertext[i - plen]
        pt.append(beaufort_decrypt_char(c, key_char, alpha))
    return ''.join(pt)

# ── Analytical: derive primer from known plaintext ────────────────────────────

def derive_primer_pt_autokey(ciphertext, plaintext_known, known_start, primer_len, alpha):
    """
    Given known plaintext at position known_start, derive the primer for
    plaintext autokey.

    In plaintext autokey:
      key[i] = primer[i]     for i < primer_len
      key[i] = pt[i - primer_len]  for i >= primer_len

    So at position i (where we know pt[i]):
      pt[i] = C[i] - key[i]
    => key[i] = C[i] - pt[i]  (the required key value)

    If i >= primer_len, then key[i] = pt[i - primer_len]
    => pt[i - primer_len] = key[i]  ... which we can check or use to back-derive primer.

    For i < primer_len, key[i] = primer[i], so we get primer[i] directly.
    """
    required_keys = []
    for j, pt_char in enumerate(plaintext_known):
        i = known_start + j
        c = ciphertext[i]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(pt_char, alpha)
        ki = (ci - pi) % len(alpha)
        required_keys.append((i, alpha_chr(ki, alpha)))

    # If primer_len > known_start, some required keys ARE primer chars
    primer_chars = {}
    for (i, k) in required_keys:
        if i < primer_len:
            primer_chars[i] = k

    return required_keys, primer_chars

def derive_primer_ct_autokey(ciphertext, plaintext_known, known_start, primer_len, alpha):
    """
    Ciphertext autokey:
      key[i] = primer[i]       for i < primer_len
      key[i] = C[i - primer_len]  for i >= primer_len

    At each known position i:
      pt[i] = C[i] - key[i]

    If i >= primer_len, key[i] = C[i - primer_len], fully determined by ciphertext.
    If i < primer_len, key[i] = primer[i].
    """
    required_keys = []
    for j, pt_char in enumerate(plaintext_known):
        i = known_start + j
        c = ciphertext[i]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(pt_char, alpha)
        ki = (ci - pi) % len(alpha)
        required_keys.append((i, alpha_chr(ki, alpha)))

        # What does the cipher actually provide as key[i]?
        if i >= primer_len:
            actual_key = ciphertext[i - primer_len]
        else:
            actual_key = None  # comes from primer

        required_keys[-1] = (i, alpha_chr(ki, alpha), actual_key)

    return required_keys

# ── Primers to test ───────────────────────────────────────────────────────────

PRIMERS = [
    # Kryptos-related
    "KRYPTOS",
    "PALIMPSEST",
    "ABSCISSA",
    "SHADOW",
    "KOMITET",
    # K4-specific clues
    "BERLIN",
    "BERLINCLOCK",
    "NORTHEAST",
    "CLOCK",
    "EAST",
    "NORTH",
    # CIA/location
    "LANGLEY",
    "CIA",
    "SANBORN",
    "DIGETAL",
    "DIGITAL",
    # From sculpture
    "UNDERGROUNDLAYER",
    "UNDERGROUND",
    "LAYER",
    "BELOW",
    "ABOVE",
    "UNDER",
    # Cryptographic terms
    "VIGENERE",
    "AUTOKEY",
    "TABLEAU",
    # Date-related
    "NOVEMBER",
    "BERLIN1989",
    "NINETEEN",
    # Single-word primers
    "SECRET",
    "HIDDEN",
    "SOLVED",
    "ANSWER",
    "WATER",
    "STONE",
    "EARTH",
    "FIRE",
    "WIND",
    # Known K1/K2 keys used together
    "KRYPTOSPALIMPSEST",
    "PALIMPSESTKRYPTOS",
    "KRYPTOSABSCISSA",
    "ABSCISSAKRYPTOS",
    # From K3 plaintext (Berlin Wall reference)
    "VIRTUALLY",
    "INVISIBLE",
    "DIGETAL",
    "INTERPRET",
    "DARKNESS",
    "DAYLIGHT",
    "SLOWLY",
    "DESPERATELY",
    # Single letters (trivially short but complete the set)
    "K", "R", "Y", "P", "T", "O", "S",
    "A", "B", "C", "D", "E", "F", "G",
    # Two-letter
    "KR", "KY", "KP", "KT", "KO", "KS",
    # Possible coordinate-derived
    "FOURTYEIGHT",
    "THIRTYEIGHT",
    # German (Berlin wall context)
    "FREIHEIT",
    "MAUER",
    "OST",
    "WEST",
    "NORDEN",
    "SUEDEN",
]

# ── Check validity: filter primers with chars not in KRYPTOS alpha ────────────

def valid_for_alpha(primer, alpha):
    return all(c in alpha for c in primer.upper())

# ── Scoring ───────────────────────────────────────────────────────────────────

ENGLISH_WORDS = [
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'WAS',
    'ONE', 'OUR', 'OUT', 'HIS', 'HER', 'HAS', 'WITH', 'THAT', 'THIS',
    'HAVE', 'FROM', 'THEY', 'BEEN', 'WERE', 'WOULD', 'COULD', 'THEIR',
    'WHAT', 'WHEN', 'WILL', 'ABOUT', 'WHICH', 'THERE', 'BEEN', 'MORE',
    'ALSO', 'SOME', 'THAN', 'INTO', 'TIME', 'ONLY', 'OVER', 'SUCH',
    # Domain-specific
    'EAST', 'WEST', 'NORTH', 'SOUTH', 'BERLIN', 'CLOCK', 'NORTHEAST',
    'BERLINCLOCK', 'LAYER', 'SHADOW', 'LIGHT', 'DARK', 'DEEP', 'BELOW',
    'ABOVE', 'UNDER', 'DEGREES', 'LATITUDE', 'LONGITUDE',
    'SLOWLY', 'DIGITAL', 'INTERPRET', 'INVISIBLE', 'VIRTUALLY',
]

def score_english(text):
    score = 0
    for word in ENGLISH_WORDS:
        count = 0
        start = 0
        while True:
            pos = text.find(word, start)
            if pos == -1:
                break
            count += 1
            score += len(word) ** 2
            start = pos + 1
    return score

# ── Main search ───────────────────────────────────────────────────────────────

METHODS = [
    ("PT-Autokey-Vigenere", pt_autokey_decrypt),
    ("CT-Autokey-Vigenere", ct_autokey_decrypt),
    ("PT-Autokey-Beaufort", pt_autokey_beaufort_decrypt),
    ("CT-Autokey-Beaufort", ct_autokey_beaufort_decrypt),
]

ALPHABETS = [
    ("KRYPTOS", KRYPTOS_ALPHA),
    ("STANDARD", STANDARD_ALPHA),
]

print("=" * 80)
print("PHASE 1: SYSTEMATIC PRIMER TEST")
print("Testing all primers x all methods x both alphabets")
print("Looking for BERLINCLOCK at pos 63 AND/OR NORTHEAST anywhere")
print("=" * 80)

hits_bc_exact = []   # BERLINCLOCK exactly at position 63
hits_bc_any   = []   # BERLINCLOCK anywhere
hits_ne       = []   # NORTHEAST anywhere
hits_both     = []   # both

for alpha_name, alpha in ALPHABETS:
    for method_name, method_fn in METHODS:
        for primer in PRIMERS:
            primer_up = primer.upper()
            if not valid_for_alpha(primer_up, alpha):
                continue

            try:
                pt = method_fn(K4, primer_up, alpha)
            except Exception as e:
                continue

            has_bc     = "BERLINCLOCK" in pt
            bc_at_63   = pt[63:74] == "BERLINCLOCK"
            has_ne     = "NORTHEAST" in pt
            has_north  = "NORTH" in pt
            has_east   = "EAST" in pt

            if bc_at_63:
                hits_bc_exact.append((alpha_name, method_name, primer, pt))
            if has_bc:
                hits_bc_any.append((alpha_name, method_name, primer, pt, pt.find("BERLINCLOCK")))
            if has_ne:
                hits_ne.append((alpha_name, method_name, primer, pt, pt.find("NORTHEAST")))
            if has_bc and has_ne:
                hits_both.append((alpha_name, method_name, primer, pt))

print(f"\nResults:")
print(f"  BERLINCLOCK at exactly pos 63: {len(hits_bc_exact)}")
print(f"  BERLINCLOCK anywhere:          {len(hits_bc_any)}")
print(f"  NORTHEAST anywhere:            {len(hits_ne)}")
print(f"  BOTH found:                    {len(hits_both)}")

# ── Report hits ───────────────────────────────────────────────────────────────

def report_result(label, alpha_name, method_name, primer, pt, extra=""):
    print(f"\n{'='*70}")
    print(f"  *** {label} ***")
    print(f"  Method:  {method_name}")
    print(f"  Alphabet: {alpha_name}")
    print(f"  Primer:  '{primer}'")
    if extra:
        print(f"  {extra}")
    print(f"  Plaintext: {pt}")
    print(f"  pos 63-74: '{pt[63:74] if len(pt)>=74 else pt[63:]}'")
    ne_pos = pt.find("NORTHEAST")
    bc_pos = pt.find("BERLINCLOCK")
    if bc_pos >= 0:
        print(f"  BERLINCLOCK at pos {bc_pos}")
    if ne_pos >= 0:
        print(f"  NORTHEAST at pos {ne_pos}")

if hits_bc_exact:
    print("\n" + "!"*70)
    print("!!! BERLINCLOCK FOUND EXACTLY AT POSITION 63 !!!")
    print("!"*70)
    for alpha_name, method_name, primer, pt in hits_bc_exact:
        report_result("BERLINCLOCK @ 63", alpha_name, method_name, primer, pt)

if hits_both:
    print("\n" + "!"*70)
    print("!!! BOTH BERLINCLOCK AND NORTHEAST FOUND !!!")
    print("!"*70)
    for alpha_name, method_name, primer, pt in hits_both:
        report_result("BERLINCLOCK + NORTHEAST", alpha_name, method_name, primer, pt)

if hits_bc_any and not hits_bc_exact:
    print("\nBERLINCLOCK found (not at pos 63):")
    for alpha_name, method_name, primer, pt, pos in hits_bc_any:
        report_result(f"BERLINCLOCK at pos {pos}", alpha_name, method_name, primer, pt)

if hits_ne and not hits_both:
    print("\nNORTHEAST found (without BERLINCLOCK):")
    for alpha_name, method_name, primer, pt, pos in hits_ne:
        report_result(f"NORTHEAST at pos {pos}", alpha_name, method_name, primer, pt)

# ── PHASE 2: Analytical derivation ───────────────────────────────────────────

print("\n" + "=" * 80)
print("PHASE 2: ANALYTICAL DERIVATION")
print("Derive what the key must be at positions 63-73 (BERLINCLOCK)")
print("and check if it's consistent with each autokey variant.")
print("=" * 80)

KNOWN_PT   = "BERLINCLOCK"
KNOWN_START = 63

for alpha_name, alpha in ALPHABETS:
    print(f"\n--- Alphabet: {alpha_name} ---")

    ct_segment = K4[KNOWN_START:KNOWN_START + len(KNOWN_PT)]
    print(f"Ciphertext[63:74]: {ct_segment}")
    print(f"Plaintext[63:74]:  {KNOWN_PT}")

    # Required key chars at positions 63-73
    required_key = []
    for j in range(len(KNOWN_PT)):
        c = ct_segment[j]
        p = KNOWN_PT[j]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p, alpha)
        # Vigenere: p = c - k  => k = c - p
        ki_vig = (ci - pi) % len(alpha)
        # Beaufort: p = k - c  => k = p + c
        ki_bft = (pi + ci) % len(alpha)
        required_key.append({
            'pos': KNOWN_START + j,
            'ct': c, 'pt': p,
            'key_vigenere': alpha_chr(ki_vig, alpha),
            'key_beaufort': alpha_chr(ki_bft, alpha),
        })

    print(f"\nRequired key at positions 63-73:")
    print(f"  {'Pos':>4}  {'CT':>3}  {'PT':>3}  {'Key(Vig)':>9}  {'Key(Bft)':>9}")
    for r in required_key:
        print(f"  {r['pos']:>4}  {r['ct']:>3}  {r['pt']:>3}  {r['key_vigenere']:>9}  {r['key_beaufort']:>9}")

    # Vigenere key string at positions 63-73
    key_str_vig = ''.join(r['key_vigenere'] for r in required_key)
    key_str_bft = ''.join(r['key_beaufort'] for r in required_key)
    print(f"\n  Vigenere key[63:74] = '{key_str_vig}'")
    print(f"  Beaufort key[63:74] = '{key_str_bft}'")

    # For PLAINTEXT AUTOKEY with Vigenere:
    # key[i] = pt[i - primer_len]  for i >= primer_len
    # So key[63] = pt[63 - primer_len]
    # If primer_len = P, key[63] = pt[63 - P], key[64] = pt[64 - P], etc.
    # We know pt[63:74] = BERLINCLOCK, and we need key[63:74].
    # If we assume some primer length P, we need pt[63-P : 74-P] = key[63:74]
    # meaning the plaintext 11 chars before BERLINCLOCK equals the required key.
    print(f"\n  For PLAINTEXT AUTOKEY (Vigenere): key[63:74] must be '{key_str_vig}'")
    print(f"  This means pt[63-P : 74-P] = '{key_str_vig}' for primer length P")
    print(f"  Checking if this segment appears in full K4 decryption for various P:")

    for alpha_name2, alpha2 in [(alpha_name, alpha)]:
        for method_name, method_fn in [("PT-Autokey-Vigenere", pt_autokey_decrypt),
                                        ("PT-Autokey-Beaufort", pt_autokey_beaufort_decrypt)]:
            target_key = key_str_vig if "Vigenere" in method_name else key_str_bft
            for primer in PRIMERS:
                primer_up = primer.upper()
                if not valid_for_alpha(primer_up, alpha2):
                    continue
                try:
                    pt = method_fn(K4, primer_up, alpha2)
                except:
                    continue
                # Check if the key segment at 63 matches
                plen = len(primer_up)
                if plen <= 63:
                    actual_key_at_63 = pt[63 - plen: 74 - plen] if (63 - plen) >= 0 else None
                    if actual_key_at_63 == target_key:
                        print(f"    MATCH! method={method_name}, primer='{primer}', P={plen}")
                        print(f"    pt = {pt}")

    # For CIPHERTEXT AUTOKEY with Vigenere:
    # key[i] = ct[i - primer_len]  for i >= primer_len
    # So key[63:74] = ct[63-P : 74-P]
    print(f"\n  For CIPHERTEXT AUTOKEY (Vigenere): key[63:74] must be '{key_str_vig}'")
    print(f"  This means ct[63-P : 74-P] = '{key_str_vig}' for primer length P")
    # Scan K4 for key_str_vig in ciphertext
    for P in range(0, 64):
        seg = K4[63 - P: 74 - P]
        if seg == key_str_vig:
            print(f"    MATCH! Primer length P = {P}, ct[{63-P}:{74-P}] = '{seg}'")
            print(f"    --> This primer length would make CT-Autokey-Vigenere work!")

    print(f"\n  For CIPHERTEXT AUTOKEY (Beaufort): key[63:74] must be '{key_str_bft}'")
    for P in range(0, 64):
        seg = K4[63 - P: 74 - P]
        if seg == key_str_bft:
            print(f"    MATCH! Primer length P = {P}, ct[{63-P}:{74-P}] = '{seg}'")
            print(f"    --> This primer length would make CT-Autokey-Beaufort work!")

# ── PHASE 3: Partial known-plaintext attack ───────────────────────────────────

print("\n" + "=" * 80)
print("PHASE 3: PARTIAL KNOWN-PLAINTEXT ATTACK")
print("Use BERLINCLOCK@63 to bootstrap and find the primer")
print("=" * 80)

for alpha_name, alpha in ALPHABETS:
    print(f"\n--- Alphabet: {alpha_name} ---")
    N = len(alpha)

    # For PT-Autokey-Vigenere:
    # We know pt[63:74] = BERLINCLOCK
    # key[63:74] is determined by the required key chars derived above.
    # key[63 + j] = pt[63 + j - P]  for P <= 63
    # If P <= 63: pt[63 - P : 74 - P] = key[63:74]
    # But we don't know pt[0:63] yet. However, we can try each primer length
    # and see if the implied pt segment at 63-P:74-P is consistent.

    # Approach: for each primer length P from 1..63,
    # compute what pt[63-P:74-P] must be (= required key chars),
    # then check if that partial plaintext is consistent with the decryption
    # from the primer through position 63-P.
    # This is complex; instead: for each P, derive the required primer chars
    # from BERLINCLOCK constraint, then complete the decryption and check NORTHEAST.

    # Required Vigenere key chars at 63..73:
    required_vigenere_key = []
    required_beaufort_key = []
    for j in range(len(KNOWN_PT)):
        i = KNOWN_START + j
        c = K4[i]
        p = KNOWN_PT[j]
        ci = alpha_idx(c, alpha)
        pi = alpha_idx(p, alpha)
        required_vigenere_key.append((i, alpha_chr((ci - pi) % N, alpha)))
        required_beaufort_key.append((i, alpha_chr((pi + ci) % N, alpha)))

    for variant_name, required_key, method_fn in [
        ("PT-Autokey-Vigenere", required_vigenere_key, pt_autokey_decrypt),
        ("PT-Autokey-Beaufort", required_beaufort_key, pt_autokey_beaufort_decrypt),
    ]:
        print(f"\n  Variant: {variant_name}")
        key_at_63_73 = ''.join(k for _, k in required_key)
        print(f"  Required key[63:74] = '{key_at_63_73}'")

        for P in range(1, 64):
            # In PT-autokey, key[63+j] = pt[63+j-P]
            # So pt[63-P : 74-P] must equal required key chars
            start = 63 - P
            if start < 0:
                continue
            # The plaintext we need at positions start..start+11
            required_pt_segment = key_at_63_73

            # Now: can we derive a primer of length P such that
            # decrypting K4 with that primer gives us 'required_pt_segment' at pos start?
            # The primer affects positions 0..P-1 directly, and then propagates.
            # For P <= start, positions 0..P-1 are primer, and pt[P..start+10] depends on them.
            # This is a forward propagation problem.
            #
            # Key insight: if we fix the primer, the decryption is deterministic.
            # We need pt[start:start+11] = required_pt_segment AND pt[63:74] = BERLINCLOCK.
            # By construction of required_pt_segment, the second condition is automatically
            # satisfied IF the first is (in PT-autokey, they're equivalent).
            #
            # So the question is: what primer gives pt[start:start+11] = required_pt_segment?
            # Since decryption is sequential and each pt char depends on prior pt chars
            # (which depend on primer), this is fully determined by the primer.
            #
            # For small P, we can brute-force. For larger P, we use the analytical approach:
            # The primer of length P fully determines all of pt[0..P-1], and then pt[P..] follows.
            # pt[start:start+11] = required_pt_segment constrains the primer.

            # Skip unless P is small (brute-forceable) or we have a clever approach
            # For now, just try our known primers and report matches
            for primer in PRIMERS:
                primer_up = primer.upper()
                if len(primer_up) != P:
                    continue
                if not valid_for_alpha(primer_up, alpha):
                    continue
                try:
                    pt = method_fn(K4, primer_up, alpha)
                except:
                    continue
                if pt[start:start+11] == required_pt_segment:
                    print(f"    MATCH! P={P}, primer='{primer}'")
                    print(f"    pt = {pt}")
                    if "NORTHEAST" in pt:
                        print(f"    *** NORTHEAST at pos {pt.find('NORTHEAST')} ***")

# ── PHASE 4: Brute-force short primers ───────────────────────────────────────

print("\n" + "=" * 80)
print("PHASE 4: SHORT PRIMER BRUTE-FORCE (length 1-6)")
print("KRYPTOS alphabet only, all 4 methods")
print("Looking for BERLINCLOCK at pos 63")
print("=" * 80)

import itertools

alpha = KRYPTOS_ALPHA
alpha_name = "KRYPTOS"
N = len(alpha)

for primer_len in range(1, 7):
    count_checked = 0
    count_found = 0
    print(f"\nPrimer length {primer_len} ({N**primer_len} combinations)...")

    for primer_tuple in itertools.product(alpha, repeat=primer_len):
        primer = ''.join(primer_tuple)
        count_checked += 1

        for method_name, method_fn in METHODS:
            try:
                pt = method_fn(K4, primer, alpha)
            except:
                continue

            if pt[63:74] == "BERLINCLOCK":
                count_found += 1
                ne_pos = pt.find("NORTHEAST")
                print(f"\n  *** BERLINCLOCK @ 63 FOUND! ***")
                print(f"  method={method_name}, primer='{primer}'")
                print(f"  pt = {pt}")
                if ne_pos >= 0:
                    print(f"  NORTHEAST at pos {ne_pos}")
                    print(f"  *** BOTH FOUND - POSSIBLE SOLUTION! ***")

    print(f"  Checked {count_checked}, found {count_found} with BERLINCLOCK@63")

# ── PHASE 5: Mixed autokey (fixed key prefix, then autokey) ──────────────────

print("\n" + "=" * 80)
print("PHASE 5: MIXED AUTOKEY")
print("Fixed repeating key for first N chars, then autokey kicks in")
print("Testing: K4[0:P] decrypted with fixed key, then pt-autokey for rest")
print("=" * 80)

# Here we test: what if the cipher is Vigenere for first P chars with a known key,
# then switches to pt-autokey?
# We check if pt[63:74] = BERLINCLOCK for various transition points P.

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA)]:
    for primer in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLINCLOCK", "NORTHEAST"]:
        primer_up = primer.upper()
        if not valid_for_alpha(primer_up, alpha):
            continue

        # Try each transition point
        for trans in range(1, 63):
            # Phase 1: Vigenere with repeating primer (periodic)
            pt_phase1 = []
            for i in range(trans):
                k = primer_up[i % len(primer_up)]
                pt_phase1.append(vigenere_decrypt_char(K4[i], k, alpha))

            # Phase 2: autokey using pt from phase 1 as seed
            # key for position i (i >= trans) = pt[i - len(primer_up)]
            pt_full = list(pt_phase1)
            for i in range(trans, len(K4)):
                key_idx = i - len(primer_up)
                if key_idx >= 0:
                    k = pt_full[key_idx]
                else:
                    # Still in primer range
                    k = primer_up[i % len(primer_up)]
                pt_full.append(vigenere_decrypt_char(K4[i], k, alpha))

            pt_str = ''.join(pt_full)
            if pt_str[63:74] == "BERLINCLOCK":
                ne_pos = pt_str.find("NORTHEAST")
                print(f"\n  *** MATCH! primer='{primer}', trans={trans}, alpha={alpha_name}")
                print(f"  pt = {pt_str}")
                if ne_pos >= 0:
                    print(f"  NORTHEAST at pos {ne_pos}")

print("\n" + "=" * 80)
print("AUTOKEY ANALYSIS COMPLETE")
print("=" * 80)

# ── PHASE 6: CT-Autokey analytical check for all primer lengths ──────────────

print("\n" + "=" * 80)
print("PHASE 6: CT-AUTOKEY COMPLETE ANALYTICAL CHECK")
print("For CT-Autokey-Vigenere: key[i] = ct[i-P] for i>=P")
print("So pt[63+j] = ct[63+j] - ct[63+j-P]  (in alphabet arithmetic)")
print("We need pt[63:74] = BERLINCLOCK => check every P from 1 to 63")
print("=" * 80)

for alpha_name, alpha in [("KRYPTOS", KRYPTOS_ALPHA), ("STANDARD", STANDARD_ALPHA)]:
    N = len(alpha)
    print(f"\nAlphabet: {alpha_name}")

    for P in range(1, 90):
        # For CT-autokey-Vigenere:
        # pt[i] = ct[i] - ct[i-P]  for i >= P
        # (primer determines pt[0..P-1])
        # Check if pt[63:74] = BERLINCLOCK
        if 63 < P:
            # All of BERLINCLOCK is in the primer-determined zone; can't check analytically
            continue

        match = True
        for j, p_char in enumerate(KNOWN_PT):
            i = KNOWN_START + j
            if i < P:
                # This position is primer-dependent; skip check
                continue
            ct_i   = alpha_idx(K4[i], alpha)
            ct_im  = alpha_idx(K4[i - P], alpha)
            pt_calc = alpha_chr((ct_i - ct_im) % N, alpha)
            if pt_calc != p_char:
                match = False
                break

        if match:
            # Compute full plaintext for P (primer is irrelevant for positions >= P)
            pt = []
            # For positions 0..P-1, we need the primer. We'll use a dummy '*' marker.
            for i in range(min(P, len(K4))):
                pt.append('?')  # primer-dependent, unknown
            for i in range(P, len(K4)):
                ct_i  = alpha_idx(K4[i], alpha)
                ct_im = alpha_idx(K4[i - P], alpha)
                pt.append(alpha_chr((ct_i - ct_im) % N, alpha))
            pt_str = ''.join(pt)
            ne_pos = pt_str.find("NORTHEAST")
            print(f"\n  *** BERLINCLOCK @ 63 for P={P} ***")
            print(f"  pt = {pt_str}")
            if ne_pos >= 0:
                print(f"  *** NORTHEAST at pos {ne_pos} ***")
                print(f"  *** THIS IS A CANDIDATE SOLUTION! ***")
            print(f"  (First {P} chars are primer-dependent and shown as '?')")

    # Same for CT-Autokey-Beaufort: pt[i] = ct[i-P] - ct[i]
    print(f"\n  CT-Autokey-Beaufort for {alpha_name}:")
    for P in range(1, 90):
        if 63 < P:
            continue
        match = True
        for j, p_char in enumerate(KNOWN_PT):
            i = KNOWN_START + j
            if i < P:
                continue
            ct_i   = alpha_idx(K4[i], alpha)
            ct_im  = alpha_idx(K4[i - P], alpha)
            pt_calc = alpha_chr((ct_im - ct_i) % N, alpha)
            if pt_calc != p_char:
                match = False
                break
        if match:
            pt = []
            for i in range(min(P, len(K4))):
                pt.append('?')
            for i in range(P, len(K4)):
                ct_i  = alpha_idx(K4[i], alpha)
                ct_im = alpha_idx(K4[i - P], alpha)
                pt.append(alpha_chr((ct_im - ct_i) % N, alpha))
            pt_str = ''.join(pt)
            ne_pos = pt_str.find("NORTHEAST")
            print(f"\n  *** Beaufort BERLINCLOCK @ 63 for P={P} ***")
            print(f"  pt = {pt_str}")
            if ne_pos >= 0:
                print(f"  *** NORTHEAST at pos {ne_pos} ***")

print("\n" + "=" * 80)
print("ALL PHASES COMPLETE")
print("=" * 80)
