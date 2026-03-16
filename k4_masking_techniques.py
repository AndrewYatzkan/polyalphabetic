#!/usr/bin/env python3
"""
K4 Masking Techniques Analysis
===============================
Tests the hypothesis that Sanborn applied a MASKING technique to the English
plaintext BEFORE Vigenere encryption, as he stated:
  "I masked the English language so it's more of a challenge now"

Hypotheses tested:
  1. Simple substitution (monoalphabetic) before Vigenere
  2. Homophonic substitution before Vigenere
  3. Polybius square / fractionation before Vigenere
  4. Atbash-like / reversed alphabet substitution
  5. Null insertion before encryption
  6. Phonetic encoding
  7. Caesar shift of plaintext before Vigenere
  8. Keyword-based substitution alphabets
"""

import math
import itertools
from collections import Counter, defaultdict

# ============================================================
# CONSTANTS
# ============================================================

KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

FULL_KEY = "OYNKYELYOIECBAQKCBNJQRDUMRIYW"
PERIOD = 29

# Cribs: (plaintext, start_position_0indexed)
CRIBS = [
    ("EASTNORTHEAST", 21),
    ("BERLINCLOCK", 63),
]

assert len(CT) == 97
assert len(FULL_KEY) == 29
assert len(KRYPTOS_ALPHA) == 26

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def k_idx(ch):
    """Index of character in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA.index(ch)

def k_chr(idx):
    """Character at index in KRYPTOS alphabet."""
    return KRYPTOS_ALPHA[idx % 26]

def s_idx(ch):
    """Index of character in standard alphabet."""
    return STANDARD_ALPHA.index(ch)

def s_chr(idx):
    """Character at index in standard alphabet."""
    return STANDARD_ALPHA[idx % 26]

def vig_encrypt_kryptos(pt_char, key_char):
    """Vigenere encrypt a single char using KRYPTOS alphabet."""
    return k_chr(k_idx(pt_char) + k_idx(key_char))

def vig_decrypt_kryptos(ct_char, key_char):
    """Vigenere decrypt a single char using KRYPTOS alphabet."""
    return k_chr(k_idx(ct_char) - k_idx(key_char))

def vig_encrypt_standard(pt_char, key_char):
    """Vigenere encrypt a single char using standard alphabet."""
    return s_chr(s_idx(pt_char) + s_idx(key_char))

def vig_decrypt_standard(ct_char, key_char):
    """Vigenere decrypt a single char using standard alphabet."""
    return s_chr(s_idx(ct_char) - s_idx(key_char))

def full_vig_decrypt(ciphertext, key, alphabet='kryptos'):
    """Full Vigenere decryption."""
    result = []
    for i, ch in enumerate(ciphertext):
        k = key[i % len(key)]
        if alphabet == 'kryptos':
            result.append(vig_decrypt_kryptos(ch, k))
        else:
            result.append(vig_decrypt_standard(ch, k))
    return ''.join(result)

def full_vig_encrypt(plaintext, key, alphabet='kryptos'):
    """Full Vigenere encryption."""
    result = []
    for i, ch in enumerate(plaintext):
        k = key[i % len(key)]
        if alphabet == 'kryptos':
            result.append(vig_encrypt_kryptos(ch, k))
        else:
            result.append(vig_encrypt_standard(ch, k))
    return ''.join(result)


# Load quadgram scoring
QUADGRAMS = {}
QUADGRAM_TOTAL = 0

def load_quadgrams(filepath="/home/user/polyalphabetic/english_quadgrams.txt"):
    global QUADGRAMS, QUADGRAM_TOTAL
    with open(filepath) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                gram, count = parts[0], int(parts[1])
                QUADGRAMS[gram] = count
                QUADGRAM_TOTAL += count
    # Convert to log probabilities
    for gram in QUADGRAMS:
        QUADGRAMS[gram] = math.log10(QUADGRAMS[gram] / QUADGRAM_TOTAL)

load_quadgrams()

FLOOR = math.log10(0.01 / QUADGRAM_TOTAL)

def quadgram_score(text):
    """Score text using quadgram log probabilities."""
    text = text.upper()
    score = 0.0
    for i in range(len(text) - 3):
        gram = text[i:i+4]
        score += QUADGRAMS.get(gram, FLOOR)
    return score

def ic_score(text):
    """Index of coincidence."""
    n = len(text)
    if n < 2:
        return 0
    counts = Counter(text)
    total = sum(c * (c - 1) for c in counts.values())
    return total / (n * (n - 1))


# ============================================================
# COMPUTE VIGENERE DECRYPTION (the "intermediate" text)
# ============================================================

VIG_OUTPUT = full_vig_decrypt(CT, FULL_KEY, 'kryptos')

print("=" * 80)
print("K4 MASKING TECHNIQUES ANALYSIS")
print("=" * 80)
print()
print(f"Ciphertext:     {CT}")
print(f"Key:            {FULL_KEY}")
print(f"Vig decrypted:  {VIG_OUTPUT}")
print(f"Length:          {len(VIG_OUTPUT)}")
print()

# Verify cribs appear in Vigenere output
for crib_text, crib_pos in CRIBS:
    segment = VIG_OUTPUT[crib_pos:crib_pos + len(crib_text)]
    print(f"  Crib '{crib_text}' at pos {crib_pos}: found '{segment}' - {'MATCH' if segment == crib_text else 'NO MATCH'}")

print()

# Non-crib positions
crib_positions = set()
for crib_text, crib_pos in CRIBS:
    for i in range(crib_pos, crib_pos + len(crib_text)):
        crib_positions.add(i)

non_crib_text = ''.join(VIG_OUTPUT[i] for i in range(97) if i not in crib_positions)
print(f"Non-crib text ({len(non_crib_text)} chars): {non_crib_text}")
print(f"Non-crib IC: {ic_score(non_crib_text):.4f}")
print(f"Non-crib quadgram score: {quadgram_score(non_crib_text):.2f}")
print(f"Full text quadgram score: {quadgram_score(VIG_OUTPUT):.2f}")
print()

# ============================================================
# HYPOTHESIS 1: SIMPLE SUBSTITUTION BEFORE VIGENERE
# ============================================================

print("=" * 80)
print("HYPOTHESIS 1: SIMPLE SUBSTITUTION (MONOALPHABETIC) BEFORE VIGENERE")
print("=" * 80)
print()
print("If plaintext was first run through a simple substitution cipher, then")
print("Vigenere encrypted, the Vigenere output IS the substitution output.")
print("So VIG_OUTPUT = sub(real_plaintext)")
print("The cribs tell us: at crib positions, real_plaintext is known, and")
print("VIG_OUTPUT is known, so we can derive the substitution mapping.")
print()

# Build substitution mapping from cribs
# VIG_OUTPUT[pos] = substitution(real_plaintext[pos])
# So if real_plaintext letter is P and VIG_OUTPUT letter is Q,
# then substitution maps P -> Q

sub_mapping = {}  # real_letter -> substituted_letter
sub_conflicts = []

for crib_text, crib_pos in CRIBS:
    print(f"  Crib: '{crib_text}' at position {crib_pos}")
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        vig_ch = VIG_OUTPUT[pos]
        if real_ch in sub_mapping:
            if sub_mapping[real_ch] != vig_ch:
                sub_conflicts.append((real_ch, sub_mapping[real_ch], vig_ch, pos))
                print(f"    CONFLICT: '{real_ch}' -> was '{sub_mapping[real_ch]}', now '{vig_ch}' at pos {pos}")
            else:
                print(f"    Confirmed: '{real_ch}' -> '{vig_ch}' (pos {pos})")
        else:
            sub_mapping[real_ch] = vig_ch
            print(f"    New:       '{real_ch}' -> '{vig_ch}' (pos {pos})")

print()
print(f"  Substitution mapping derived ({len(sub_mapping)} letters):")
for ch in sorted(sub_mapping.keys()):
    print(f"    {ch} -> {sub_mapping[ch]}")

print(f"\n  Conflicts found: {len(sub_conflicts)}")
for conflict in sub_conflicts:
    print(f"    Letter '{conflict[0]}': maps to both '{conflict[1]}' and '{conflict[2]}' (pos {conflict[3]})")

if not sub_conflicts:
    print("\n  NO CONFLICTS - substitution is consistent!")
    print("  Attempting to invert the substitution on full VIG_OUTPUT...")

    # Invert: for each VIG_OUTPUT char, find what real letter maps to it
    inv_mapping = {}
    for real_ch, sub_ch in sub_mapping.items():
        if sub_ch in inv_mapping:
            print(f"    WARNING: '{sub_ch}' maps from both '{inv_mapping[sub_ch]}' and '{real_ch}'")
        inv_mapping[sub_ch] = real_ch

    # Apply inverse to full text
    partial_plain = []
    for i, ch in enumerate(VIG_OUTPUT):
        if ch in inv_mapping:
            partial_plain.append(inv_mapping[ch])
        else:
            partial_plain.append('?')
    partial_text = ''.join(partial_plain)

    known_count = sum(1 for c in partial_text if c != '?')
    print(f"\n  Partial plaintext ({known_count}/97 known):")
    print(f"  {partial_text}")

    # Check if the known portions look like English
    # Extract runs of known characters
    runs = []
    current_run = ""
    for ch in partial_text:
        if ch != '?':
            current_run += ch
        else:
            if len(current_run) >= 4:
                runs.append(current_run)
            current_run = ""
    if len(current_run) >= 4:
        runs.append(current_run)

    print(f"\n  Known character runs (length >= 4):")
    for run in runs:
        print(f"    '{run}' (score: {quadgram_score(run):.2f})")
else:
    print("\n  Conflicts exist - pure monoalphabetic substitution before Vigenere is unlikely")
    print("  UNLESS the key positions 16-20 are wrong.")
    print()
    print("  Testing with key variants for positions 16-20...")

# ============================================================
# HYPOTHESIS 1b: Try ALL possible key[16:21] to find consistent substitution
# ============================================================

print()
print("-" * 70)
print("HYPOTHESIS 1b: Brute-force key positions 16-20 for consistent substitution")
print("-" * 70)
print()

# For each possible 5-letter key at positions 16-20, check if the crib-derived
# substitution is consistent (no conflicts)

base_key = list(FULL_KEY)
consistent_keys = []

# We need to check which crib positions use key positions 16-20
# Position i uses key[i % 29]
crib_key_positions = {}
for crib_text, crib_pos in CRIBS:
    for i in range(len(crib_text)):
        pos = crib_pos + i
        kp = pos % 29
        crib_key_positions[pos] = kp

# Which positions in the cribs use key positions 16-20?
affected_positions = {pos: kp for pos, kp in crib_key_positions.items() if 16 <= kp <= 20}
print(f"  Crib positions affected by key[16:21]: {affected_positions}")

# If no crib positions use 16-20, the substitution mapping doesn't change
if not affected_positions:
    print("  No crib positions use key[16:21], so mapping is independent of these positions")
else:
    # Brute force over 26^5 possibilities for those 5 positions
    # That's ~12M which is too many. Instead, check smaller spaces.
    # Actually the affected positions are a subset. Let's be smart about it.

    # For each affected crib position, the vig_output char depends on key[kp].
    # VIG_OUTPUT[pos] = K_chr(K_idx(CT[pos]) - K_idx(key[kp]))
    # So for a given key letter at kp, the vig_output is determined.
    # We need: for each real_plaintext letter, all its vig_output values agree.

    # Let's enumerate only the key positions actually needed
    needed_key_positions = sorted(set(affected_positions.values()))
    print(f"  Key positions actually needed: {needed_key_positions}")

    # For a manageable search: brute-force just the needed positions
    num_needed = len(needed_key_positions)
    print(f"  Search space: 26^{num_needed} = {26**num_needed}")

    if 26**num_needed <= 26**5:  # ~12M - might be slow but doable with optimization
        best_consistent = []

        # Build lookup: for each (affected_pos, key_letter_at_kp), what is vig_output?
        # and what is the real plaintext letter?
        affected_crib_info = []
        for crib_text, crib_pos in CRIBS:
            for i in range(len(crib_text)):
                pos = crib_pos + i
                kp = pos % 29
                if kp in needed_key_positions:
                    real_ch = crib_text[i]
                    ct_ch = CT[pos]
                    affected_crib_info.append((pos, kp, real_ch, ct_ch))

        # Also need all crib positions NOT affected (their mapping is fixed)
        fixed_mapping = {}
        fixed_conflicts = False
        for crib_text, crib_pos in CRIBS:
            for i in range(len(crib_text)):
                pos = crib_pos + i
                kp = pos % 29
                if kp not in needed_key_positions:
                    real_ch = crib_text[i]
                    vig_ch = VIG_OUTPUT[pos]  # This is fixed
                    if real_ch in fixed_mapping:
                        if fixed_mapping[real_ch] != vig_ch:
                            fixed_conflicts = True
                    else:
                        fixed_mapping[real_ch] = vig_ch

        print(f"  Fixed mapping (non-affected positions): {fixed_mapping}")
        print(f"  Fixed mapping has conflicts: {fixed_conflicts}")

        if not fixed_conflicts:
            # Now try all combinations for the needed key positions
            count_tested = 0
            count_consistent = 0

            for combo in itertools.product(range(26), repeat=num_needed):
                count_tested += 1

                # Build trial mapping starting from fixed
                trial_mapping = dict(fixed_mapping)
                conflict = False

                for pos, kp, real_ch, ct_ch in affected_crib_info:
                    # Which key letter at this position?
                    key_letter_idx = combo[needed_key_positions.index(kp)]
                    key_letter = KRYPTOS_ALPHA[key_letter_idx]
                    # Compute vig output
                    vig_ch = k_chr(k_idx(ct_ch) - key_letter_idx)

                    if real_ch in trial_mapping:
                        if trial_mapping[real_ch] != vig_ch:
                            conflict = True
                            break
                    else:
                        # Also check: is vig_ch already mapped from a different letter?
                        # (substitution must be 1-to-1)
                        trial_mapping[real_ch] = vig_ch

                if not conflict:
                    # Check 1-to-1 property
                    values = list(trial_mapping.values())
                    if len(values) == len(set(values)):
                        key_variant = list(FULL_KEY)
                        for j, kp in enumerate(needed_key_positions):
                            key_variant[kp] = KRYPTOS_ALPHA[combo[j]]
                        key_str = ''.join(key_variant)

                        # Decrypt with this key and score
                        decrypted = full_vig_decrypt(CT, key_str, 'kryptos')

                        # Apply inverse substitution
                        inv = {v: k for k, v in trial_mapping.items()}
                        plain_chars = []
                        for ch in decrypted:
                            plain_chars.append(inv.get(ch, '?'))
                        plain = ''.join(plain_chars)

                        # Score only the known portions
                        known = ''.join(c for c in plain if c != '?')

                        count_consistent += 1
                        if count_consistent <= 5 or len(trial_mapping) >= 12:
                            best_consistent.append((key_str, trial_mapping.copy(), plain, known))

            print(f"\n  Tested: {count_tested}, Consistent: {count_consistent}")

            if best_consistent:
                # Score and sort
                scored = []
                for key_str, mapping, plain, known in best_consistent:
                    # Score the full decrypted text
                    dec = full_vig_decrypt(CT, key_str, 'kryptos')
                    sc = quadgram_score(dec)
                    scored.append((sc, key_str, mapping, plain, dec))
                scored.sort(reverse=True)

                print(f"\n  Top results by quadgram score of Vig output:")
                for sc, key_str, mapping, plain, dec in scored[:10]:
                    print(f"    Key: {key_str}")
                    print(f"    Vig output: {dec}")
                    print(f"    Mapping ({len(mapping)} letters): {dict(sorted(mapping.items()))}")
                    print(f"    Score: {sc:.2f}")
                    print()

# ============================================================
# HYPOTHESIS 2: SPECIFIC SUBSTITUTION PATTERNS
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 2: ATBASH AND SYSTEMATIC SUBSTITUTION PATTERNS")
print("=" * 80)
print()

# 2a. Atbash in KRYPTOS alphabet: K<->Z, R<->X, Y<->W, etc.
# Position i in KRYPTOS maps to position 25-i

def kryptos_atbash(text):
    return ''.join(KRYPTOS_ALPHA[25 - KRYPTOS_ALPHA.index(ch)] for ch in text)

def standard_atbash(text):
    return ''.join(chr(ord('Z') - (ord(ch) - ord('A'))) for ch in text)

# Apply atbash to VIG_OUTPUT
atbash_k = kryptos_atbash(VIG_OUTPUT)
atbash_s = standard_atbash(VIG_OUTPUT)

print("2a. Atbash applied to Vigenere output:")
print(f"  KRYPTOS Atbash: {atbash_k}")
print(f"  Score: {quadgram_score(atbash_k):.2f}, IC: {ic_score(atbash_k):.4f}")
print(f"  Standard Atbash: {atbash_s}")
print(f"  Score: {quadgram_score(atbash_s):.2f}, IC: {ic_score(atbash_s):.4f}")
print()

# 2b. ROT-N (Caesar shift) in KRYPTOS alphabet
print("2b. Caesar shifts (ROT-N) in KRYPTOS alphabet applied to Vig output:")
best_caesar = (float('-inf'), 0, "")
for shift in range(1, 26):
    shifted = ''.join(k_chr(k_idx(ch) + shift) for ch in VIG_OUTPUT)
    sc = quadgram_score(shifted)
    if sc > best_caesar[0]:
        best_caesar = (sc, shift, shifted)
    if shift <= 5 or shift in [13, 25]:
        print(f"  ROT-{shift:2d}: {shifted[:50]}... score={sc:.2f}")

print(f"\n  Best Caesar: ROT-{best_caesar[1]} score={best_caesar[0]:.2f}")
print(f"  {best_caesar[2]}")
print()

# 2c. Affine cipher: E(x) = (ax + b) mod 26
print("2c. Affine substitution on Vig output (KRYPTOS alphabet):")
best_affine = (float('-inf'), 0, 0, "")
# a must be coprime with 26: 1,3,5,7,9,11,15,17,19,21,23,25
coprimes = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]

for a in coprimes:
    # Find modular inverse of a
    a_inv = pow(a, -1, 26)
    for b in range(26):
        # Decrypt: D(y) = a_inv * (y - b) mod 26
        decrypted = ''.join(k_chr((a_inv * (k_idx(ch) - b)) % 26) for ch in VIG_OUTPUT)
        sc = quadgram_score(decrypted)
        if sc > best_affine[0]:
            best_affine = (sc, a, b, decrypted)

print(f"  Best affine: a={best_affine[1]}, b={best_affine[2]}, score={best_affine[0]:.2f}")
print(f"  {best_affine[3]}")
print()

# 2d. Keyword substitution alphabets
print("2d. Keyword-based substitution alphabets on Vig output:")
print("  Testing common KRYPTOS-related keywords...")

def make_keyword_alphabet(keyword, base_alpha=STANDARD_ALPHA):
    """Create a substitution alphabet from a keyword."""
    seen = set()
    alpha = []
    for ch in keyword.upper():
        if ch in base_alpha and ch not in seen:
            alpha.append(ch)
            seen.add(ch)
    for ch in base_alpha:
        if ch not in seen:
            alpha.append(ch)
            seen.add(ch)
    return ''.join(alpha)

keywords = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "BERLIN", "CLOCK",
    "NORTHEAST", "SANBORN", "SCHEIDT", "LANGLEY", "CIA", "COMPASS",
    "IQLUSION", "ILLUSION", "DIGETAL", "DIGITAL", "LUCID", "MEMORY",
    "UNDERGRUUND", "UNDERGROUND", "BETWEEN", "SUBTLE", "SHADING",
    "VIRTUALLY", "INVISIBLE", "DESPARATLY", "DESPERATELY",
    "SLOWLYDESPARATLY", "TOTALLYINVISIBLE",
    "DYAHR", "LAYERTWO", "ENIGMA", "BLETCHLEY", "TURING",
]

best_keyword = (float('-inf'), "", "")
for kw in keywords:
    # Make substitution alphabet from keyword in KRYPTOS ordering
    sub_alpha = make_keyword_alphabet(kw, KRYPTOS_ALPHA)
    # Apply: each VIG_OUTPUT char at position i in sub_alpha maps to KRYPTOS_ALPHA[i]
    try:
        decrypted = ''.join(KRYPTOS_ALPHA[sub_alpha.index(ch)] for ch in VIG_OUTPUT)
        sc = quadgram_score(decrypted)
        if sc > best_keyword[0]:
            best_keyword = (sc, kw, decrypted)
    except ValueError:
        pass

    # Also try reverse: KRYPTOS_ALPHA[i] -> sub_alpha[i]
    decrypted2 = ''.join(sub_alpha[KRYPTOS_ALPHA.index(ch)] for ch in VIG_OUTPUT)
    sc2 = quadgram_score(decrypted2)
    if sc2 > best_keyword[0]:
        best_keyword = (sc2, kw + " (reverse)", decrypted2)

    # Try with standard alphabet too
    sub_alpha_std = make_keyword_alphabet(kw, STANDARD_ALPHA)
    decrypted3 = ''.join(STANDARD_ALPHA[sub_alpha_std.index(ch)] for ch in VIG_OUTPUT)
    sc3 = quadgram_score(decrypted3)
    if sc3 > best_keyword[0]:
        best_keyword = (sc3, kw + " (std)", decrypted3)

print(f"  Best keyword: '{best_keyword[1]}' score={best_keyword[0]:.2f}")
print(f"  {best_keyword[2]}")
print()


# ============================================================
# HYPOTHESIS 3: POLYBIUS SQUARE / FRACTIONATION
# ============================================================

print("=" * 80)
print("HYPOTHESIS 3: POLYBIUS SQUARE / FRACTIONATION BEFORE VIGENERE")
print("=" * 80)
print()

# Idea: plaintext was converted to pairs of digits via a 5x5 Polybius grid,
# then those digits were converted back to letters for Vigenere.
# 97 chars = 48 pairs + 1 extra (odd number is problematic but let's test)

# Standard Polybius (I/J merged):
# Key: KRYPTOS, fill rest
polybius_key = "KRYPTOSABCDEFGHILMNQUVWXZ"  # 25 chars, J->I
assert len(polybius_key) == 25
assert len(set(polybius_key)) == 25

def polybius_encode(text, grid):
    """Encode text to digit pairs using Polybius grid."""
    result = []
    for ch in text.upper():
        if ch == 'J':
            ch = 'I'
        idx = grid.index(ch)
        row, col = idx // 5, idx % 5
        result.append((row, col))
    return result

def polybius_decode(pairs, grid):
    """Decode digit pairs back to text using Polybius grid."""
    result = []
    for row, col in pairs:
        idx = row * 5 + col
        result.append(grid[idx])
    return ''.join(result)

# Try: VIG_OUTPUT digits encode Polybius pairs
# Each letter of VIG_OUTPUT maps to a digit 0-4 somehow
# Two consecutive digits form a Polybius pair

# Method 1: Use KRYPTOS alphabet position mod 5 for row and col
print("3a. Polybius with letter->digit mapping (KRYPTOS idx mod 5):")
digits = [k_idx(ch) % 5 for ch in VIG_OUTPUT]
# Group into pairs
if len(digits) % 2 == 1:
    digits_even = digits[:-1]
else:
    digits_even = digits

pairs = [(digits_even[i], digits_even[i+1]) for i in range(0, len(digits_even), 2)]
try:
    decoded = polybius_decode(pairs, polybius_key)
    print(f"  Decoded ({len(decoded)} chars): {decoded}")
    print(f"  Score: {quadgram_score(decoded):.2f}")
except (ValueError, IndexError) as e:
    print(f"  Error: {e}")

# Method 2: Use KRYPTOS alphabet position // 5 and mod 5
print("\n3b. Polybius with (idx//5, idx%5) -> read consecutively:")
pairs2 = []
for ch in VIG_OUTPUT:
    idx = k_idx(ch)
    pairs2.append((idx // 5, idx % 5))
# These are the Polybius coordinates of the ENCRYPTED Polybius text
# To reverse: take the digits row-col-row-col and regroup
all_digits = []
for r, c in pairs2:
    all_digits.append(r)
    all_digits.append(c)
# Now regroup into pairs for Polybius decode
repaired = [(all_digits[i], all_digits[i+1]) for i in range(0, len(all_digits) - 1, 2)]
try:
    decoded2 = polybius_decode(repaired, polybius_key)
    print(f"  Decoded ({len(decoded2)} chars): {decoded2}")
    print(f"  Score: {quadgram_score(decoded2):.2f}")
except (ValueError, IndexError) as e:
    print(f"  Error: {e}")

# Method 3: Bifid-like - separate all rows and all columns, then interleave
print("\n3c. Bifid-like unfractionation (separate rows and cols, recombine):")
rows = [k_idx(ch) // 5 for ch in VIG_OUTPUT]
cols = [k_idx(ch) % 5 for ch in VIG_OUTPUT]
# In bifid, the rows are listed first, then cols, then regrouped in pairs
combined = rows + cols
pairs3 = [(combined[i], combined[i+1]) for i in range(0, len(combined) - 1, 2)]
try:
    decoded3 = polybius_decode(pairs3, polybius_key)
    print(f"  Decoded ({len(decoded3)} chars): {decoded3}")
    print(f"  Score: {quadgram_score(decoded3):.2f}")
except (ValueError, IndexError) as e:
    print(f"  Error: {e}")

# Method 4: Reverse bifid - interleave rows and cols
print("\n3d. Reverse bifid (interleave rows/cols from halves):")
half = len(VIG_OUTPUT) // 2
first_half_indices = [k_idx(ch) for ch in VIG_OUTPUT[:half]]
second_half_indices = [k_idx(ch) for ch in VIG_OUTPUT[half:half*2]]  # may lose last char
pairs4 = []
for i in range(min(len(first_half_indices), len(second_half_indices))):
    r = first_half_indices[i] % 5
    c = second_half_indices[i] % 5
    pairs4.append((r, c))
try:
    decoded4 = polybius_decode(pairs4, polybius_key)
    print(f"  Decoded ({len(decoded4)} chars): {decoded4}")
    print(f"  Score: {quadgram_score(decoded4):.2f}")
except (ValueError, IndexError) as e:
    print(f"  Error: {e}")

print()

# ============================================================
# HYPOTHESIS 4: NULL INSERTION BEFORE ENCRYPTION
# ============================================================

print("=" * 80)
print("HYPOTHESIS 4: NULL INSERTION BEFORE ENCRYPTION")
print("=" * 80)
print()

# If nulls were inserted into the plaintext at regular intervals before Vigenere,
# removing them from the Vigenere output should yield English.
# Test: remove every Nth character

print("4a. Remove every Nth character from Vig output:")
best_null = (float('-inf'), 0, 0, "")
for period in range(2, 20):
    for offset in range(period):
        remaining = ''.join(VIG_OUTPUT[i] for i in range(97) if (i % period) != offset)
        sc = quadgram_score(remaining)
        if sc > best_null[0]:
            best_null = (sc, period, offset, remaining)
        if period <= 4 and offset == 0:
            print(f"  Remove every {period}th (offset 0): {remaining[:60]}... len={len(remaining)} score={sc:.2f}")

print(f"\n  Best null removal: period={best_null[1]}, offset={best_null[2]}, score={best_null[0]:.2f}")
print(f"  {best_null[3][:80]}...")
print()

# 4b. Remove characters at specific positions (e.g., positions that are rare letters)
print("4b. Remove positions with uncommon letters (potential nulls):")
# Check frequency of each letter in VIG_OUTPUT
freq = Counter(VIG_OUTPUT)
print(f"  Letter frequencies in Vig output:")
for ch, cnt in sorted(freq.items(), key=lambda x: -x[1]):
    print(f"    {ch}: {cnt} ({cnt/97*100:.1f}%)")

# What if we remove all instances of a specific letter?
print(f"\n  Remove all instances of each letter:")
best_remove_letter = (float('-inf'), "", "")
for letter in KRYPTOS_ALPHA:
    remaining = VIG_OUTPUT.replace(letter, '')
    if len(remaining) >= 10:
        sc = quadgram_score(remaining)
        if sc > best_remove_letter[0]:
            best_remove_letter = (sc, letter, remaining)

print(f"  Best: remove '{best_remove_letter[1]}' -> score={best_remove_letter[0]:.2f}")
print(f"  {best_remove_letter[2]}")
print()


# ============================================================
# HYPOTHESIS 5: PHONETIC ENCODING
# ============================================================

print("=" * 80)
print("HYPOTHESIS 5: PHONETIC ENCODING")
print("=" * 80)
print()

# Look for phonetic patterns in the Vigenere output
# Common phonetic substitutions:
# ATE/8 -> EIGHT, C/SEE -> SEE, U -> YOU, R -> ARE, Y -> WHY
# B -> BE, T -> TEA, I -> EYE, O -> OH, Q -> QUEUE
# NE -> ANY, UR -> YOUR, etc.

print("Vig output: ", VIG_OUTPUT)
print()

# Check for common letter-to-word phonetic readings
phonetic_map = {
    'U': 'YOU', 'R': 'ARE', 'Y': 'WHY', 'C': 'SEE', 'B': 'BE',
    'I': 'EYE', 'O': 'OH', 'T': 'TEA', 'Q': 'QUEUE', 'P': 'PEA',
    'N': 'EN', 'S': 'ES', 'X': 'EX', 'F': 'EF', 'L': 'EL',
    'M': 'EM', 'W': 'DOUBLE-U',
}

# Also check digraph phonetic readings
digraph_phonetic = {
    'NE': 'ANY', 'MT': 'EMPTY', 'XS': 'EXCESS', 'NV': 'ENVY',
    'DK': 'DECAY', 'SA': 'ESSAY', 'TP': 'TEEPEE', 'IC': 'ICY',
    'AR': 'ARE', 'ER': 'HER', 'OR': 'OR', 'UR': 'YOUR',
    'AB': 'ABBE', 'AD': 'ADD', 'QU': 'QUEUE',
}

# Look for phonetic sequences in VIG_OUTPUT
print("5a. Scanning for phonetic digraph patterns in Vig output:")
found_phonetics = []
for i in range(len(VIG_OUTPUT) - 1):
    digraph = VIG_OUTPUT[i:i+2]
    if digraph in digraph_phonetic:
        found_phonetics.append((i, digraph, digraph_phonetic[digraph]))

for pos, dg, word in found_phonetics:
    print(f"  Position {pos}: '{dg}' -> '{word}'")

# 5b. Try reading the text as initials/abbreviations
print("\n5b. Non-crib sections as potential abbreviations:")
# Extract segments between cribs
segments = [
    ("Before EASTNORTHEAST", VIG_OUTPUT[:21]),
    ("Between cribs", VIG_OUTPUT[34:63]),
    ("After BERLINCLOCK", VIG_OUTPUT[74:]),
]
for name, seg in segments:
    print(f"  {name}: {seg}")

# 5c. Check for vowel-consonant patterns suggesting phonetic spelling
print("\n5c. Vowel-consonant pattern analysis of non-crib text:")
vowels = set("AEIOU")
for name, seg in segments:
    v_count = sum(1 for c in seg if c in vowels)
    c_count = len(seg) - v_count
    ratio = v_count / len(seg) if len(seg) > 0 else 0
    print(f"  {name}: {v_count}V/{c_count}C ratio={ratio:.2f} (English ~0.38)")

# ============================================================
# HYPOTHESIS 6: HOMOPHONIC SUBSTITUTION
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 6: HOMOPHONIC SUBSTITUTION BEFORE VIGENERE")
print("=" * 80)
print()
print("If a homophonic cipher was used before Vigenere, common plaintext letters")
print("would have multiple ciphertext representations. After Vigenere decryption,")
print("we'd need to map MULTIPLE Vig output letters to the SAME plaintext letter.")
print()

# The Vigenere output for the crib positions tells us what the homophonic
# cipher produced for known plaintext letters.
# From EASTNORTHEAST: E->K, A->S, S->A, T->R, N->N, O->Q, R->A... wait R->A?
# But S->A too! That's the conflict from before.
# In homophonic: both S and R could map to A (or different homophones)
# Actually no - in homophonic, each PLAINTEXT letter maps to MULTIPLE ciphertext letters
# So E might map to {K, B, ...}, A might map to {S, ...}, etc.
# The mapping is plaintext -> set of ciphertext letters

print("Homophonic mapping from cribs (plaintext -> set of Vig output letters):")
homo_mapping = defaultdict(set)
for crib_text, crib_pos in CRIBS:
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        vig_ch = VIG_OUTPUT[pos]
        homo_mapping[real_ch].add(vig_ch)

for ch in sorted(homo_mapping.keys()):
    print(f"  {ch} -> {sorted(homo_mapping[ch])}")

# Check: do any vig_output letters map to multiple plaintext letters?
reverse_homo = defaultdict(set)
for real_ch, vig_set in homo_mapping.items():
    for vig_ch in vig_set:
        reverse_homo[vig_ch].add(real_ch)

print("\nReverse mapping (Vig output -> possible plaintext letters):")
multi_mappings = 0
for vig_ch in sorted(reverse_homo.keys()):
    pt_set = reverse_homo[vig_ch]
    marker = " <-- MULTI" if len(pt_set) > 1 else ""
    print(f"  {vig_ch} -> {sorted(pt_set)}{marker}")
    if len(pt_set) > 1:
        multi_mappings += 1

print(f"\nVig output letters mapping to multiple plaintext letters: {multi_mappings}")
if multi_mappings > 0:
    print("This means the masking is NOT a simple homophonic cipher")
    print("(or the key is wrong at some positions)")
else:
    print("Consistent with homophonic - but same as simple substitution in this case")

# ============================================================
# HYPOTHESIS 7: COLUMN/ROW TRANSPOSITION OF VIG OUTPUT
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 7: TRANSPOSITION APPLIED TO PLAINTEXT BEFORE VIGENERE")
print("=" * 80)
print()
print("If a transposition was applied to the plaintext BEFORE Vigenere encryption,")
print("we need to un-transpose the Vig output to recover the plaintext.")
print("But transposition before Vigenere with a periodic key is complex...")
print()

# Simple approach: try columnar transposition on VIG_OUTPUT
# with small number of columns

def columnar_decrypt(text, num_cols):
    """Try all column orderings for columnar transposition."""
    n = len(text)
    num_full_cols = n % num_cols
    col_lengths = []
    for c in range(num_cols):
        if num_full_cols == 0:
            col_lengths.append(n // num_cols)
        elif c < num_full_cols:
            col_lengths.append(n // num_cols + 1)
        else:
            col_lengths.append(n // num_cols)

    # Read off columns
    cols = []
    pos = 0
    for c in range(num_cols):
        cols.append(text[pos:pos + col_lengths[c]])
        pos += col_lengths[c]

    # Read row by row
    result = []
    max_rows = max(col_lengths)
    for r in range(max_rows):
        for c in range(num_cols):
            if r < len(cols[c]):
                result.append(cols[c][r])
    return ''.join(result)

print("7a. Simple columnar transposition of Vig output:")
best_col_trans = (float('-inf'), 0, "")
for num_cols in range(2, 20):
    # Just read columns sequentially (identity column order)
    decrypted = columnar_decrypt(VIG_OUTPUT, num_cols)
    sc = quadgram_score(decrypted)
    if sc > best_col_trans[0]:
        best_col_trans = (sc, num_cols, decrypted)
    if num_cols <= 6:
        print(f"  {num_cols} cols: {decrypted[:60]}... score={sc:.2f}")

print(f"\n  Best: {best_col_trans[1]} cols, score={best_col_trans[0]:.2f}")
print(f"  {best_col_trans[2]}")

# Route transposition (read in one pattern, out in another)
print("\n7b. Route transposition - read into grid, extract in different order:")
for num_cols in [7, 8, 9, 10, 11, 12, 13, 14, 29]:
    num_rows = (97 + num_cols - 1) // num_cols
    # Pad
    padded = VIG_OUTPUT + 'X' * (num_rows * num_cols - 97)
    # Read into grid row by row
    grid = []
    for r in range(num_rows):
        grid.append(padded[r * num_cols:(r + 1) * num_cols])

    # Read out column by column
    col_read = ''
    for c in range(num_cols):
        for r in range(num_rows):
            col_read += grid[r][c]
    col_read = col_read[:97]

    # Read out spiral (simplified - just reverse rows alternately)
    boustrophedon = ''
    for r in range(num_rows):
        if r % 2 == 0:
            boustrophedon += grid[r]
        else:
            boustrophedon += grid[r][::-1]
    boustrophedon = boustrophedon[:97]

    sc_col = quadgram_score(col_read)
    sc_bou = quadgram_score(boustrophedon)

    if num_cols in [7, 10, 29]:
        print(f"  Grid {num_rows}x{num_cols}: col-read score={sc_col:.2f}, boustrophedon score={sc_bou:.2f}")

print()


# ============================================================
# HYPOTHESIS 8: REVERSED TEXT / SECTIONS
# ============================================================

print("=" * 80)
print("HYPOTHESIS 8: REVERSED TEXT OR REVERSED SECTIONS")
print("=" * 80)
print()

# 8a. Full reversal
reversed_vig = VIG_OUTPUT[::-1]
print(f"8a. Full reversal: {reversed_vig}")
print(f"    Score: {quadgram_score(reversed_vig):.2f}")

# 8b. Reverse in blocks
for block_size in [2, 3, 4, 5, 7, 10, 29]:
    blocks = [VIG_OUTPUT[i:i+block_size] for i in range(0, 97, block_size)]
    reversed_blocks = ''.join(b[::-1] for b in blocks)
    sc = quadgram_score(reversed_blocks)
    print(f"8b. Reverse blocks of {block_size}: score={sc:.2f} -> {reversed_blocks[:50]}...")

# 8c. Reverse order of blocks
for block_size in [2, 3, 4, 5, 7, 29]:
    blocks = [VIG_OUTPUT[i:i+block_size] for i in range(0, 97, block_size)]
    reordered = ''.join(reversed(blocks))
    sc = quadgram_score(reordered)
    print(f"8c. Reverse block order (size {block_size}): score={sc:.2f}")

print()


# ============================================================
# HYPOTHESIS 9: COMBINED APPROACH - SUBSTITUTION + ANALYSIS
# ============================================================

print("=" * 80)
print("HYPOTHESIS 9: DEEP ANALYSIS OF CRIB-DERIVED SUBSTITUTION")
print("=" * 80)
print()

# Let's really carefully work out what the substitution mapping tells us
print("Detailed crib analysis:")
print()
print("Position | CT | Key | Key_pos | Vig_Out | Crib_PT | sub(PT)->Vig")
print("-" * 72)

all_mappings = []
for crib_text, crib_pos in CRIBS:
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        ct_ch = CT[pos]
        key_ch = FULL_KEY[pos % 29]
        key_pos = pos % 29
        vig_ch = VIG_OUTPUT[pos]

        all_mappings.append((pos, ct_ch, key_ch, key_pos, vig_ch, real_ch))
        print(f"   {pos:3d}    | {ct_ch}  | {key_ch}   |   {key_pos:2d}    |    {vig_ch}    |    {real_ch}    | {real_ch}->{vig_ch}")

print()

# Build the substitution mapping with full detail
sub_detail = defaultdict(list)
for pos, ct_ch, key_ch, key_pos, vig_ch, real_ch in all_mappings:
    sub_detail[real_ch].append((vig_ch, pos, key_pos))

print("Substitution detail per plaintext letter:")
for real_ch in sorted(sub_detail.keys()):
    entries = sub_detail[real_ch]
    vig_chars = set(e[0] for e in entries)
    positions = [(e[1], e[2]) for e in entries]
    consistent = "CONSISTENT" if len(vig_chars) == 1 else "INCONSISTENT"
    print(f"  {real_ch} -> {sorted(vig_chars)} ({consistent}) at positions {positions}")

# Check which key positions are involved in inconsistencies
print("\nInconsistencies by key position:")
for real_ch in sorted(sub_detail.keys()):
    entries = sub_detail[real_ch]
    vig_chars = set(e[0] for e in entries)
    if len(vig_chars) > 1:
        print(f"  {real_ch}:")
        for vig_ch, pos, kp in entries:
            uses_unknown = "** UNKNOWN KEY **" if 16 <= kp <= 20 else ""
            print(f"    -> {vig_ch} at pos {pos} (key pos {kp}) {uses_unknown}")

# ============================================================
# HYPOTHESIS 10: WHAT IF THE SUBSTITUTION IS POSITION-DEPENDENT?
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 10: POSITION-DEPENDENT MASKING")
print("=" * 80)
print()
print("What if the masking changes based on position? E.g., alternating between")
print("two substitution alphabets, or shifting based on position.")
print()

# Check: for each repeated plaintext letter in the cribs, does the substitution
# output correlate with position in any systematic way?

for real_ch in sorted(sub_detail.keys()):
    entries = sub_detail[real_ch]
    if len(entries) > 1:
        vig_chars = set(e[0] for e in entries)
        if len(vig_chars) > 1:
            print(f"  Letter '{real_ch}' has different outputs:")
            for vig_ch, pos, kp in entries:
                # Check position parity, position mod 3, etc.
                vig_idx = k_idx(vig_ch)
                real_idx = k_idx(real_ch)
                diff = (vig_idx - real_idx) % 26
                print(f"    pos={pos} (mod2={pos%2}, mod3={pos%3}) -> {vig_ch} (shift={diff})")

# ============================================================
# HYPOTHESIS 11: AUTOKEY / PROGRESSIVE KEY MASKING
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 11: AUTOKEY-STYLE MASKING")
print("=" * 80)
print()
print("What if the masking is an autokey cipher where each plaintext letter")
print("determines the next masking shift?")
print()

# For the cribs, compute what the autokey sequence would need to be
# If masking is: masked[i] = (PT[i] + autokey[i]) mod 26
# And masked[i] = VIG_OUTPUT[i] (what Vigenere produces)
# Then autokey[i] = (VIG_OUTPUT[i] - PT[i]) mod 26

# For autokey, the key starts with a primer, then uses plaintext letters
# autokey[0] = primer, autokey[i] = PT[i-1] for i > 0

for crib_text, crib_pos in CRIBS:
    print(f"  Crib '{crib_text}' at pos {crib_pos}:")
    shifts = []
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        vig_ch = VIG_OUTPUT[pos]
        shift = (k_idx(vig_ch) - k_idx(real_ch)) % 26
        shifts.append(shift)
        shift_letter = KRYPTOS_ALPHA[shift]
        print(f"    pos {pos}: {real_ch} -> {vig_ch}, shift={shift} ({shift_letter})")

    # Check if shifts follow autokey pattern: shift[i] = PT[i-1] (as KRYPTOS index)
    print(f"  Checking autokey pattern (shift[i] should equal PT[i-1]):")
    matches = 0
    total = 0
    for i in range(1, len(crib_text)):
        expected_shift = k_idx(crib_text[i-1])
        actual_shift = shifts[i]
        match = "YES" if expected_shift == actual_shift else "no"
        if expected_shift == actual_shift:
            matches += 1
        total += 1
        print(f"    shift[{i}]={actual_shift} vs PT[{i-1}]='{crib_text[i-1]}'={expected_shift}: {match}")
    print(f"  Autokey matches: {matches}/{total}")
    print()

# Also check with standard alphabet
print("  Same analysis with STANDARD alphabet:")
for crib_text, crib_pos in CRIBS:
    shifts = []
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        vig_ch = VIG_OUTPUT[pos]
        shift = (s_idx(vig_ch) - s_idx(real_ch)) % 26
        shifts.append(shift)

    matches = 0
    for i in range(1, len(crib_text)):
        expected_shift = s_idx(crib_text[i-1])
        if expected_shift == shifts[i]:
            matches += 1
    print(f"  Crib '{crib_text}': autokey matches (std alpha): {matches}/{len(crib_text)-1}")


# ============================================================
# HYPOTHESIS 12: TWO-LETTER SUBSTITUTION (DIGRAPH SUBSTITUTION)
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 12: DIGRAPH SUBSTITUTION (PLAYFAIR-LIKE)")
print("=" * 80)
print()

# In a Playfair cipher, pairs of letters are substituted together.
# If this was done before Vigenere, pairs of Vig output letters
# correspond to pairs of plaintext letters.

print("Digraph mapping from cribs:")
for crib_text, crib_pos in CRIBS:
    # Pair up letters
    padded_crib = crib_text
    if len(padded_crib) % 2 == 1:
        padded_crib += 'X'  # Standard Playfair padding

    for i in range(0, len(crib_text) - 1, 2):
        pos = crib_pos + i
        if pos + 1 < 97:
            pt_pair = crib_text[i:i+2]
            vig_pair = VIG_OUTPUT[pos:pos+2]
            print(f"  {pt_pair} -> {vig_pair} (pos {pos}-{pos+1})")

# Check if any standard Playfair grid produces these mappings
# (Too many possibilities to brute force, but we can check a few)
print("\nChecking KRYPTOS-keyed Playfair grid:")

def make_playfair_grid(keyword):
    """Create 5x5 Playfair grid from keyword."""
    seen = set()
    grid = []
    for ch in keyword.upper():
        if ch == 'J':
            ch = 'I'
        if ch not in seen and ch.isalpha():
            grid.append(ch)
            seen.add(ch)
    for ch in 'ABCDEFGHIKLMNOPQRSTUVWXYZ':
        if ch not in seen:
            grid.append(ch)
            seen.add(ch)
    return grid

def playfair_encrypt_pair(a, b, grid):
    """Encrypt a pair of letters with Playfair."""
    if a == 'J': a = 'I'
    if b == 'J': b = 'I'

    pos_a = grid.index(a)
    pos_b = grid.index(b)
    row_a, col_a = pos_a // 5, pos_a % 5
    row_b, col_b = pos_b // 5, pos_b % 5

    if row_a == row_b:
        return grid[row_a * 5 + (col_a + 1) % 5] + grid[row_b * 5 + (col_b + 1) % 5]
    elif col_a == col_b:
        return grid[((row_a + 1) % 5) * 5 + col_a] + grid[((row_b + 1) % 5) * 5 + col_b]
    else:
        return grid[row_a * 5 + col_b] + grid[row_b * 5 + col_a]

def playfair_decrypt_pair(a, b, grid):
    """Decrypt a pair of letters with Playfair."""
    if a == 'J': a = 'I'
    if b == 'J': b = 'I'

    pos_a = grid.index(a)
    pos_b = grid.index(b)
    row_a, col_a = pos_a // 5, pos_a % 5
    row_b, col_b = pos_b // 5, pos_b % 5

    if row_a == row_b:
        return grid[row_a * 5 + (col_a - 1) % 5] + grid[row_b * 5 + (col_b - 1) % 5]
    elif col_a == col_b:
        return grid[((row_a - 1) % 5) * 5 + col_a] + grid[((row_b - 1) % 5) * 5 + col_b]
    else:
        return grid[row_a * 5 + col_b] + grid[row_b * 5 + col_a]

for kw in ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "SANBORN"]:
    grid = make_playfair_grid(kw)
    print(f"\n  Grid keyword '{kw}': {''.join(grid[:5])} / {''.join(grid[5:10])} / {''.join(grid[10:15])} / {''.join(grid[15:20])} / {''.join(grid[20:25])}")

    # Try Playfair decrypt on VIG_OUTPUT pairs
    decrypted_pairs = []
    for i in range(0, 96, 2):
        a, b = VIG_OUTPUT[i], VIG_OUTPUT[i+1]
        try:
            dec = playfair_decrypt_pair(a, b, grid)
            decrypted_pairs.append(dec)
        except ValueError:
            decrypted_pairs.append('??')

    if len(VIG_OUTPUT) % 2 == 1:
        decrypted_pairs.append(VIG_OUTPUT[-1])

    decrypted = ''.join(decrypted_pairs)
    sc = quadgram_score(decrypted)
    print(f"  Playfair decrypt: {decrypted[:60]}... score={sc:.2f}")

    # Also try encrypt direction (in case we need to reverse)
    encrypted_pairs = []
    for i in range(0, 96, 2):
        a, b = VIG_OUTPUT[i], VIG_OUTPUT[i+1]
        try:
            enc = playfair_encrypt_pair(a, b, grid)
            encrypted_pairs.append(enc)
        except ValueError:
            encrypted_pairs.append('??')

    if len(VIG_OUTPUT) % 2 == 1:
        encrypted_pairs.append(VIG_OUTPUT[-1])

    encrypted = ''.join(encrypted_pairs)
    sc2 = quadgram_score(encrypted)
    print(f"  Playfair encrypt: {encrypted[:60]}... score={sc2:.2f}")


# ============================================================
# HYPOTHESIS 13: DOUBLE VIGENERE (Vigenere masking before Vigenere)
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 13: SECONDARY VIGENERE (SHORT KEY) AS MASKING")
print("=" * 80)
print()
print("What if the masking is a second Vigenere with a short, memorable keyword?")
print("VIG_OUTPUT = Vig2(plaintext, short_key)")
print("So: plaintext = Vig2_decrypt(VIG_OUTPUT, short_key)")
print()

# Try short keywords
test_keywords = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "SHADOW", "CLOCK", "BERLIN",
    "CIA", "KEY", "MASK", "HIDE", "CODE", "ZERO", "EASY", "HARD",
    "NORTH", "EAST", "SOUTH", "WEST", "TIME", "DARK", "LIGHT",
    "SANBORN", "SCHEIDT", "LANGLEY", "SECRET", "DYAHR", "QUEEN",
    "INVISIBLE", "LUCID", "MEMORY", "ENIGMA", "ULTRA", "MAGIC",
    "NOVA", "IQLUSION", "ILLUSION", "BETWEEN", "SUBTLE", "SHADING",
    "LAYER", "DOUBLE", "MATRIX", "DESPARATLY", "DESPERATELY",
]

best_double_vig = (float('-inf'), "", "")
for kw in test_keywords:
    # Decrypt VIG_OUTPUT with keyword using KRYPTOS alphabet
    dec = full_vig_decrypt(VIG_OUTPUT, kw, 'kryptos')
    sc = quadgram_score(dec)
    if sc > best_double_vig[0]:
        best_double_vig = (sc, kw, dec)

    # Also try standard alphabet
    dec2 = full_vig_decrypt(VIG_OUTPUT, kw, 'standard')
    sc2 = quadgram_score(dec2)
    if sc2 > best_double_vig[0]:
        best_double_vig = (sc2, kw + " (std)", dec2)

print(f"  Best double Vigenere: key='{best_double_vig[1]}' score={best_double_vig[0]:.2f}")
print(f"  {best_double_vig[2]}")
print()

# More thorough: try all 3-4 letter keywords
print("  Trying all 3-letter keywords (KRYPTOS alphabet)...")
best_3letter = (float('-inf'), "", "")
for a in range(26):
    for b in range(26):
        for c in range(26):
            kw = KRYPTOS_ALPHA[a] + KRYPTOS_ALPHA[b] + KRYPTOS_ALPHA[c]
            dec = full_vig_decrypt(VIG_OUTPUT, kw, 'kryptos')
            sc = quadgram_score(dec)
            if sc > best_3letter[0]:
                best_3letter = (sc, kw, dec)

print(f"  Best 3-letter key: '{best_3letter[1]}' score={best_3letter[0]:.2f}")
print(f"  {best_3letter[2]}")

# Try 2-letter keys
print("\n  Trying all 2-letter keywords...")
best_2letter = (float('-inf'), "", "")
for a in range(26):
    for b in range(26):
        kw = KRYPTOS_ALPHA[a] + KRYPTOS_ALPHA[b]
        dec = full_vig_decrypt(VIG_OUTPUT, kw, 'kryptos')
        sc = quadgram_score(dec)
        if sc > best_2letter[0]:
            best_2letter = (sc, kw, dec)

print(f"  Best 2-letter key: '{best_2letter[1]}' score={best_2letter[0]:.2f}")
print(f"  {best_2letter[2]}")
print()


# ============================================================
# HYPOTHESIS 14: BEAUFORT/VARIANT BEAUFORT AS MASKING
# ============================================================

print("=" * 80)
print("HYPOTHESIS 14: BEAUFORT CIPHER AS MASKING LAYER")
print("=" * 80)
print()

def beaufort_decrypt(text, key, alphabet):
    """Beaufort: CT = KEY - PT mod 26, so PT = KEY - CT mod 26."""
    result = []
    for i, ch in enumerate(text):
        k = key[i % len(key)]
        if alphabet == 'kryptos':
            result.append(k_chr(k_idx(k) - k_idx(ch)))
        else:
            result.append(s_chr(s_idx(k) - s_idx(ch)))
    return ''.join(result)

best_beaufort = (float('-inf'), "", "")
for kw in test_keywords:
    dec = beaufort_decrypt(VIG_OUTPUT, kw, 'kryptos')
    sc = quadgram_score(dec)
    if sc > best_beaufort[0]:
        best_beaufort = (sc, kw, dec)

print(f"  Best Beaufort masking: key='{best_beaufort[1]}' score={best_beaufort[0]:.2f}")
print(f"  {best_beaufort[2]}")
print()


# ============================================================
# HYPOTHESIS 15: COMPREHENSIVE CRIB CONSISTENCY CHECK
# ============================================================

print("=" * 80)
print("HYPOTHESIS 15: COMPREHENSIVE CRIB CONSISTENCY WITH VARIED KEYS")
print("=" * 80)
print()
print("Testing all 26^5 keys for positions 16-20, checking which produce")
print("crib-consistent simple substitution AND high English scores.")
print()

# This is the most thorough test. Let's identify exactly which crib positions
# depend on key positions 16-20.

print("Crib position -> key position mapping:")
crib_data = []
for crib_text, crib_pos in CRIBS:
    for i, real_ch in enumerate(crib_text):
        pos = crib_pos + i
        kp = pos % 29
        crib_data.append((pos, kp, real_ch, CT[pos]))
        print(f"  pos={pos} key_pos={kp} PT='{real_ch}' CT='{CT[pos]}'")

# Identify which of positions 16-20 are used by crib positions
crib_uses_unknown = [(pos, kp, real_ch, ct_ch) for pos, kp, real_ch, ct_ch in crib_data if 16 <= kp <= 20]
print(f"\nCrib positions using unknown key positions: {len(crib_uses_unknown)}")
for pos, kp, real_ch, ct_ch in crib_uses_unknown:
    print(f"  pos={pos} key_pos={kp} PT='{real_ch}' CT='{ct_ch}'")

print()

# For each trial key[16:21], compute the substitution mapping from cribs
# and check for consistency
print("Searching for key variants with consistent substitution...")

best_results = []
base_key_list = list(FULL_KEY)

# Determine which key positions among 16-20 are actually used
used_unknown_kps = sorted(set(kp for _, kp, _, _ in crib_uses_unknown))
print(f"Unknown key positions used by cribs: {used_unknown_kps}")

if not used_unknown_kps:
    print("No crib positions use the unknown key positions!")
    print("The substitution mapping is fully determined by the known key.")
else:
    n_unknown = len(used_unknown_kps)
    total = 26 ** n_unknown
    print(f"Search space: 26^{n_unknown} = {total}")

    consistent_count = 0
    best_scored_consistent = []

    for combo in itertools.product(range(26), repeat=n_unknown):
        # Build trial key
        trial_key = list(FULL_KEY)
        for j, kp in enumerate(used_unknown_kps):
            trial_key[kp] = KRYPTOS_ALPHA[combo[j]]
        trial_key_str = ''.join(trial_key)

        # Compute Vig output for all crib positions
        trial_mapping = {}
        consistent = True

        for pos, kp, real_ch, ct_ch in crib_data:
            key_ch = trial_key[kp]
            vig_ch = k_chr(k_idx(ct_ch) - k_idx(key_ch))

            if real_ch in trial_mapping:
                if trial_mapping[real_ch] != vig_ch:
                    consistent = False
                    break
            else:
                trial_mapping[real_ch] = vig_ch

        if consistent:
            # Check 1-to-1
            values = list(trial_mapping.values())
            if len(values) == len(set(values)):
                # Score the full Vig output
                dec = full_vig_decrypt(CT, trial_key_str, 'kryptos')
                sc = quadgram_score(dec)

                # Also try applying the inverse substitution
                inv = {v: k for k, v in trial_mapping.items()}
                plain_chars = [inv.get(ch, ch) for ch in dec]
                plain = ''.join(plain_chars)
                sc_plain = quadgram_score(plain)

                consistent_count += 1
                best_scored_consistent.append((sc_plain, sc, trial_key_str, trial_mapping.copy(), dec, plain))

    best_scored_consistent.sort(reverse=True)

    print(f"\nTotal consistent keys found: {consistent_count}")
    print(f"\nTop 20 by plaintext score (after inverse substitution):")
    for rank, (sc_plain, sc_vig, key_str, mapping, dec, plain) in enumerate(best_scored_consistent[:20]):
        unknown_part = ''.join(key_str[kp] for kp in range(16, 21))
        print(f"\n  #{rank+1}: Key[16:21]={unknown_part}")
        print(f"    Full key: {key_str}")
        print(f"    Vig output score: {sc_vig:.2f}")
        print(f"    Mapping: {dict(sorted(mapping.items()))}")
        print(f"    Vig output: {dec}")
        print(f"    Inv-sub applied: {plain}")
        print(f"    Plaintext score: {sc_plain:.2f}")

        # Check if known portions are English words
        # Mark crib positions
        crib_check = list(plain)
        for crib_text, crib_pos in CRIBS:
            segment = plain[crib_pos:crib_pos + len(crib_text)]
            if segment == crib_text:
                print(f"    Crib '{crib_text}' at {crib_pos}: MATCH")
            else:
                print(f"    Crib '{crib_text}' at {crib_pos}: got '{segment}'")


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("SUMMARY OF ALL MASKING TECHNIQUE TESTS")
print("=" * 80)
print()

print(f"Vigenere output (best key): {VIG_OUTPUT}")
print(f"Quadgram score of Vig output: {quadgram_score(VIG_OUTPUT):.2f}")
print()

# Collect all scores for comparison
english_reference_score = quadgram_score("THEUNITEDSTATESOFAMERICAISTHECOUNTRYWITHTHELARGESTECONOMYINTHEWORLD"[:97] if 97 <= 68 else "THEUNITEDSTATESOFAMERICAISTHECOUNTRYWITHTHELARGESTECONOMYINTHEWORLDANDHASTHELARGESTMILITARYBUDGET")
random_text_score = quadgram_score("XQZJWVBKMLNPRFTSHDGCYUAIOE" * 4)

print(f"Reference scores:")
print(f"  English text:  {english_reference_score:.2f}")
print(f"  Random text:   {random_text_score:.2f}")
print(f"  Vig output:    {quadgram_score(VIG_OUTPUT):.2f}")
print()

results_summary = [
    ("Hypothesis 1: Simple substitution (crib-derived)", "See detailed analysis above"),
    ("Hypothesis 2a: KRYPTOS Atbash", f"{quadgram_score(atbash_k):.2f}"),
    ("Hypothesis 2b: Best Caesar shift", f"{best_caesar[0]:.2f} (ROT-{best_caesar[1]})"),
    ("Hypothesis 2c: Best Affine", f"{best_affine[0]:.2f} (a={best_affine[1]},b={best_affine[2]})"),
    ("Hypothesis 2d: Best Keyword sub", f"{best_keyword[0]:.2f} ('{best_keyword[1]}')"),
    ("Hypothesis 4: Best null removal", f"{best_null[0]:.2f} (every {best_null[1]}th, offset {best_null[2]})"),
    ("Hypothesis 7: Best columnar trans", f"{best_col_trans[0]:.2f} ({best_col_trans[1]} cols)"),
    ("Hypothesis 8: Full reversal", f"{quadgram_score(reversed_vig):.2f}"),
    ("Hypothesis 13a: Best double Vig (named)", f"{best_double_vig[0]:.2f} ('{best_double_vig[1]}')"),
    ("Hypothesis 13b: Best 3-letter Vig", f"{best_3letter[0]:.2f} ('{best_3letter[1]}')"),
    ("Hypothesis 13c: Best 2-letter Vig", f"{best_2letter[0]:.2f} ('{best_2letter[1]}')"),
    ("Hypothesis 14: Best Beaufort", f"{best_beaufort[0]:.2f} ('{best_beaufort[1]}')"),
]

print("Score comparison (higher = more English-like):")
for name, score_str in results_summary:
    print(f"  {name}: {score_str}")

print()
print("KEY OBSERVATIONS:")
print("=" * 80)
print()
print("1. The crib-derived substitution mapping from the best key tells us exactly")
print("   what masking function was applied at the known positions.")
print()
print("2. If the substitution is consistent (no conflicts), we have strong evidence")
print("   for a monoalphabetic substitution masking layer.")
print()
print("3. The non-crib portions of VIG_OUTPUT, when run through the inverse")
print("   substitution, should produce English text if the hypothesis is correct.")
print()
print("4. If inconsistencies exist only at positions using key[16:20], then")
print("   alternative key values may resolve them (tested in Hypothesis 15).")
print()
print("5. Compare all hypothesis scores against the English reference score")
print("   to identify the most promising masking technique.")
print()

# ============================================================
# DEEP DIVE: THE IDENTITY MAPPING REVELATION
# ============================================================

print()
print("=" * 80)
print("CRITICAL FINDING: IDENTITY MAPPING AT ALL CRIB POSITIONS")
print("=" * 80)
print()
print("Every crib letter maps to ITSELF in the Vig output!")
print("This means the Vigenere output IS the plaintext at crib positions.")
print("The shifts are ALL ZERO. The key OYNKYELYOIECBAQKCBNJQRDUMRIYW")
print("perfectly decrypts the cribs to their plaintext values.")
print()
print("This eliminates simple substitution as the masking method,")
print("UNLESS the masking only operates on the non-crib portions.")
print()
print("IMPLICATIONS:")
print("  1. The masking does NOT alter recognizable English words")
print("  2. The masking operates on something OTHER than letter-by-letter substitution")
print("  3. The non-crib portions are the actual masked/encoded content")
print("  4. The masking might be: abbreviation, vowel removal from certain words,")
print("     word-level encoding, or the non-crib text IS the actual plaintext")
print()

# Let's analyze the non-crib portions more carefully
print("=" * 80)
print("DEEP ANALYSIS OF NON-CRIB VIG OUTPUT SEGMENTS")
print("=" * 80)
print()

segments_detail = [
    ("Segment A (pos 0-20)", VIG_OUTPUT[0:21], 0),
    ("Segment B (pos 34-62)", VIG_OUTPUT[34:63], 34),
    ("Segment C (pos 74-96)", VIG_OUTPUT[74:97], 74),
]

for name, seg, start in segments_detail:
    print(f"{name}: {seg}")
    print(f"  Length: {len(seg)}")
    freq_seg = Counter(seg)
    vowels_in = sum(freq_seg.get(v, 0) for v in "AEIOU")
    print(f"  Vowels: {vowels_in}/{len(seg)} ({vowels_in/len(seg)*100:.1f}%)")
    print(f"  IC: {ic_score(seg):.4f}")
    print(f"  Quadgram score: {quadgram_score(seg):.2f}")

    # Look for English words
    print(f"  Potential words spotted:")
    # Check for common 3+ letter words
    common_words = ["THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL",
                    "CAN", "HER", "WAS", "ONE", "OUR", "OUT", "HAS", "HIS",
                    "HOW", "MAN", "NEW", "NOW", "OLD", "SEE", "WAY", "WHO",
                    "BOY", "DID", "GET", "HIM", "LET", "SAY", "SHE", "TOO",
                    "USE", "DAD", "MOM", "SET", "RUN", "TRY", "ASK", "MEN",
                    "READ", "NEED", "LAND", "HELP", "HOLD", "TURN", "MOVE",
                    "LIVE", "REAL", "LEFT", "LONG", "FELL", "CALL", "JUST",
                    "TIME", "SLOW", "DOWN", "OPEN", "SEEM", "TELL", "ALSO",
                    "BACK", "GIVE", "MOST", "FIND", "HERE", "KNOW", "TAKE",
                    "COME", "MADE", "THEM", "THAN", "LOOK", "ONLY", "INTO",
                    "OVER", "SUCH", "GOOD", "YEAR", "SOME", "HAVE", "FROM",
                    "THAT", "WITH", "THIS", "WILL", "EACH", "MAKE", "LIKE",
                    "WELL", "THEN", "SAID", "WHAT", "WHEN", "BEEN", "MUCH",
                    "LAST", "LOCK", "CLOCK", "EAST", "NORTH", "SOUTH", "WEST",
                    "HELD", "HOLD", "AGE", "SAG", "FELL", "ELL", "IMP",
                    "SAGE", "DIME", "TIME", "LIMP", "STOMP", "STAMP",
                    "ZEL", "ZERO", "QUG", "SOZ", "PSOZ",
                    "STIMP", "DBKZEL", "QGUZ", "HOLDOW",
                    ]

    for word in set(common_words):
        pos_in_seg = seg.find(word)
        if pos_in_seg >= 0:
            print(f"    '{word}' at local pos {pos_in_seg} (global {start + pos_in_seg})")

    print()

# ============================================================
# DEEP DIVE: NULL REMOVAL FINDING (-316.67 score!)
# ============================================================

print("=" * 80)
print("DEEP DIVE: NULL REMOVAL (BEST SCORING HYPOTHESIS)")
print("=" * 80)
print()
print("Removing every 2nd character (offset 1) scored -316.67!")
print("This is BETTER than the English reference score (-365.78).")
print("Let's analyze this in detail.")
print()

# Reproduce the best null removal
for offset in [0, 1]:
    remaining = ''.join(VIG_OUTPUT[i] for i in range(97) if (i % 2) != offset)
    removed = ''.join(VIG_OUTPUT[i] for i in range(97) if (i % 2) == offset)
    print(f"  Remove offset {offset}:")
    print(f"    Remaining ({len(remaining)}): {remaining}")
    print(f"    Removed   ({len(removed)}):  {removed}")
    print(f"    Remaining score: {quadgram_score(remaining):.2f}")
    print(f"    Remaining IC: {ic_score(remaining):.4f}")

    # Check what happens at crib positions
    print(f"    Crib positions check:")
    for crib_text, crib_pos in CRIBS:
        kept = ''.join(crib_text[i] for i in range(len(crib_text)) if ((crib_pos + i) % 2) != offset)
        print(f"      '{crib_text}' keeps: '{kept}'")
    print()

# The high score for offset=1 is suspicious - let's verify it's not just
# because the cribs happen to contribute lots of good quadgrams
print("Verifying: is the high score driven by crib residue?")
# Remove crib positions entirely and check just non-crib chars
for offset in [0, 1]:
    non_crib_remaining = []
    for i in range(97):
        if i not in crib_positions and (i % 2) != offset:
            non_crib_remaining.append(VIG_OUTPUT[i])
    non_crib_text = ''.join(non_crib_remaining)
    print(f"  Offset {offset}, non-crib only ({len(non_crib_text)} chars): {non_crib_text}")
    print(f"    Score: {quadgram_score(non_crib_text):.2f}")
    print(f"    IC: {ic_score(non_crib_text):.4f}")

print()

# Let's also try: what if nulls are inserted at specific positions
# (not periodic) - e.g., padding to fill out Vigenere key alignment?
print("Testing: remove characters at positions where Vig output has rare letters:")
rare_letters = set()
freq = Counter(VIG_OUTPUT)
for ch, cnt in freq.items():
    if cnt <= 2:
        rare_letters.add(ch)
print(f"  Rare letters (count <= 2): {sorted(rare_letters)}")

remaining_no_rare = ''.join(ch for ch in VIG_OUTPUT if ch not in rare_letters)
print(f"  Remove all rare: {remaining_no_rare} ({len(remaining_no_rare)} chars)")
print(f"  Score: {quadgram_score(remaining_no_rare):.2f}")
print()


# ============================================================
# HYPOTHESIS 16: MASKING = TEXT COMPRESSION / ABBREVIATION
# ============================================================

print("=" * 80)
print("HYPOTHESIS 16: MASKING = TEXT ABBREVIATION / COMPRESSION")
print("=" * 80)
print()
print("Scheidt said: 'I masked the English language' and mentioned")
print("removing vowels and phonetic spelling. The cribs retain their")
print("vowels, so maybe only SOME sections have vowels removed.")
print()

# The full Vig output with cribs highlighted
print("Full Vig output with sections:")
print(f"  [0-20]:  {VIG_OUTPUT[0:21]}  (unknown)")
print(f"  [21-33]: {VIG_OUTPUT[21:34]}  (=EASTNORTHEAST)")
print(f"  [34-62]: {VIG_OUTPUT[34:63]}  (unknown)")
print(f"  [63-73]: {VIG_OUTPUT[63:74]}  (=BERLINCLOCK)")
print(f"  [74-96]: {VIG_OUTPUT[74:97]}  (unknown)")
print()

# Can we read the unknown segments as abbreviated English?
# Segment A: KSARNQAPBZDBKZELSTIMP
print("Segment A: KSARNQAPBZDBKZELSTIMP")
print("  Possible readings with vowel re-insertion:")
# Look for consonant clusters that suggest missing vowels
# KS-A-RN-Q-AP-B-ZD-BK-Z-EL-ST-IMP
print("  K_S A_R_N Q_A_P B_Z_D B_K Z_E_L S_T I_M_P")
print("  Patterns: 'EL' (common suffix), 'IMP' (word), 'ST' (common)")
print("  'STIAMP' or 'STIMP'? Could be 'STAMP' or 'STOMP'")
print()

# Try inserting vowels between consonant pairs
# This is speculative but let's try a simple approach
print("  Trying common vowel insertions:")
seg_a = "KSARNQAPBZDBKZELSTIMP"

# Let's see if we can find words from a dictionary
try:
    with open("/home/user/polyalphabetic/OxfordEnglishWords.txt") as f:
        english_words = set(w.strip().upper() for w in f if len(w.strip()) >= 3)
    print(f"  Loaded {len(english_words)} English words")

    # Find any substrings that are words
    for seg_name, seg in [("A", VIG_OUTPUT[0:21]), ("B", VIG_OUTPUT[34:63]), ("C", VIG_OUTPUT[74:97])]:
        print(f"\n  Words found in Segment {seg_name} ({seg}):")
        found = []
        for length in range(3, min(len(seg) + 1, 12)):
            for start in range(len(seg) - length + 1):
                word = seg[start:start + length]
                if word in english_words:
                    found.append((start, word))
        found.sort(key=lambda x: -len(x[1]))
        for pos, word in found[:20]:
            print(f"    pos {pos}: '{word}'")

except FileNotFoundError:
    print("  Dictionary file not found")

print()


# ============================================================
# HYPOTHESIS 17: MASKING VIA KEY-DEPENDENT ALPHABET SELECTION
# ============================================================

print("=" * 80)
print("HYPOTHESIS 17: THE MASKING IS IN THE KRYPTOS ALPHABET ITSELF")
print("=" * 80)
print()
print("What if the 'masking' is simply the use of the KRYPTOS alphabet")
print("instead of standard? And the non-crib text IS the plaintext,")
print("just with some words that are not obvious English?")
print()

# The Vig output directly as message
print("Reading Vig output directly as a message:")
print()
print("  KSARNQAPBZDBKZELSTIMP EASTNORTHEAST QGUZOUAFZFELLSAGPSOZQUGDMGKFS BERLINCLOCK HOLDOWQULCKEPJFYANKCAYF")
print()
print("  Looking for word boundaries in non-crib segments...")

# Try to find word boundaries using a dictionary approach
# Score all possible word segmentations

# Simple: find the longest matching word at each position
for seg_name, seg in [
    ("Segment A", VIG_OUTPUT[0:21]),
    ("Segment B", VIG_OUTPUT[34:63]),
    ("Segment C", VIG_OUTPUT[74:97]),
]:
    print(f"\n  {seg_name}: {seg}")
    # Greedy longest-match word finding
    words_found = []
    i = 0
    while i < len(seg):
        best_word = None
        for length in range(min(len(seg) - i, 10), 2, -1):
            candidate = seg[i:i+length]
            if candidate in english_words:
                best_word = candidate
                break
        if best_word:
            words_found.append(best_word)
            i += len(best_word)
        else:
            words_found.append(seg[i])
            i += 1
    print(f"  Greedy parse: {' '.join(words_found)}")


# ============================================================
# HYPOTHESIS 18: WHAT IF MASKING = ENCODING NUMBERS/COORDS?
# ============================================================

print()
print("=" * 80)
print("HYPOTHESIS 18: NON-CRIB TEXT ENCODES NUMBERS OR COORDINATES")
print("=" * 80)
print()

# Convert non-crib text to numbers using various schemes
seg_a = VIG_OUTPUT[0:21]
seg_b = VIG_OUTPUT[34:63]
seg_c = VIG_OUTPUT[74:97]

print("Position-in-alphabet values (KRYPTOS ordering):")
for name, seg in [("A", seg_a), ("B", seg_b), ("C", seg_c)]:
    nums = [k_idx(ch) for ch in seg]
    print(f"  Segment {name}: {nums}")
    # Check for coordinate-like patterns
    # Kryptos is at 38.9517° N, 77.1467° W
    # Look for 38, 95, 17, 77, 14, 67
    nums_str = ''.join(str(n) for n in nums)
    print(f"  As digit string: {nums_str}")
    for target in ['38', '95', '77', '14', '67', '17', '3895', '7714']:
        if target in nums_str:
            pos = nums_str.index(target)
            print(f"    Found '{target}' at digit position {pos}")

print()

# A-Z = 1-26 encoding
print("Standard A=1, B=2, ... Z=26 values:")
for name, seg in [("A", seg_a), ("B", seg_b), ("C", seg_c)]:
    nums = [s_idx(ch) + 1 for ch in seg]
    print(f"  Segment {name}: {nums}")
    print(f"  Sum: {sum(nums)}")

print()


# ============================================================
# HYPOTHESIS 19: ANAGRAM / TRANSPOSITION WITHIN SEGMENTS
# ============================================================

print("=" * 80)
print("HYPOTHESIS 19: ANAGRAM/TRANSPOSITION WITHIN VIG OUTPUT SEGMENTS")
print("=" * 80)
print()

# What if each non-crib segment is an anagram?
for name, seg in [("A", seg_a), ("B", seg_b), ("C", seg_c)]:
    letters = Counter(seg)
    print(f"  Segment {name} ({len(seg)} chars): {seg}")
    print(f"    Letter counts: {dict(sorted(letters.items()))}")

    # Check if letters could form known words
    # E.g., does segment A contain letters for any meaningful phrase?
    # Use simple anagram check with dictionary
    seg_counter = Counter(seg)

    # Find all words that could be formed from these letters
    possible_words = []
    for word in english_words:
        if len(word) >= 4:
            word_counter = Counter(word)
            if all(word_counter[ch] <= seg_counter[ch] for ch in word_counter):
                possible_words.append(word)

    possible_words.sort(key=len, reverse=True)
    print(f"    Longest formable words (top 15):")
    for w in possible_words[:15]:
        print(f"      {w}")
    print()


# ============================================================
# HYPOTHESIS 20: COMBINED VIG + MASKING AS WORD BOUNDARIES
# ============================================================

print("=" * 80)
print("HYPOTHESIS 20: FULL VIG OUTPUT WORD BOUNDARY ANALYSIS")
print("=" * 80)
print()

# The full output with cribs is partially readable.
# Let's try to find the best word-boundary parsing of the ENTIRE Vig output.

full_text = VIG_OUTPUT
print(f"Full text: {full_text}")
print()

# Dynamic programming word segmentation
def best_word_segmentation(text, word_set, max_word_len=15):
    """Find the segmentation that maximizes total word coverage."""
    n = len(text)
    # dp[i] = (max_coverage, segmentation_list) for text[0:i]
    dp = [None] * (n + 1)
    dp[0] = (0, [])

    for i in range(1, n + 1):
        # Option 1: treat text[i-1] as a non-word character
        if dp[i-1] is not None:
            coverage, segs = dp[i-1]
            candidate = (coverage, segs + [text[i-1]])
            if dp[i] is None or candidate[0] > dp[i][0]:
                dp[i] = candidate

        # Option 2: end a word at position i
        for word_len in range(3, min(i, max_word_len) + 1):
            start = i - word_len
            word = text[start:i]
            if word in word_set and dp[start] is not None:
                coverage = dp[start][0] + word_len
                segs = dp[start][1] + ['[' + word + ']']
                if dp[i] is None or coverage > dp[i][0]:
                    dp[i] = (coverage, segs)

    if dp[n] is not None:
        return dp[n]
    return (0, list(text))

coverage, segmentation = best_word_segmentation(full_text, english_words)
print(f"Best word segmentation ({coverage}/{len(full_text)} chars covered):")
print(f"  {' '.join(segmentation)}")
print()

# Also try just the non-crib segments
for name, seg in [("A", seg_a), ("B", seg_b), ("C", seg_c)]:
    coverage, segmentation = best_word_segmentation(seg, english_words)
    print(f"  Segment {name} ({coverage}/{len(seg)} covered): {' '.join(segmentation)}")

print()


# ============================================================
# HYPOTHESIS 21: THE MASKING PRESERVES CRIBS BUT SCRAMBLES REST
# ============================================================

print("=" * 80)
print("HYPOTHESIS 21: SELECTIVE MASKING - ONLY NON-ENGLISH PORTIONS")
print("=" * 80)
print()
print("Since the cribs decode perfectly, the masking must be something that")
print("only affects the non-crib portions. Possible explanations:")
print()
print("  A) The non-crib text IS English, just not obvious words")
print("  B) The non-crib text uses abbreviations/codes")
print("  C) There's a SECOND cipher layer only on certain segments")
print("  D) Null characters are interspersed in the non-crib portions")
print("  E) The plaintext contains proper nouns, place names, numbers-as-words")
print()

# Test D: Try removing specific letters from non-crib portions
print("Testing: Remove each letter from non-crib text and score:")
non_crib_indices = [i for i in range(97) if i not in crib_positions]
non_crib = ''.join(VIG_OUTPUT[i] for i in non_crib_indices)

best_removal = (float('-inf'), "", "")
for letter in KRYPTOS_ALPHA:
    cleaned = non_crib.replace(letter, '')
    if len(cleaned) >= 10:
        sc = quadgram_score(cleaned)
        if sc > best_removal[0]:
            best_removal = (sc, letter, cleaned)
        if letter in "QZXJW":
            print(f"  Remove '{letter}': {cleaned[:50]}... score={sc:.2f}")

print(f"  Best: remove '{best_removal[1]}' -> score={best_removal[0]:.2f}")
print(f"  {best_removal[2]}")
print()

# Test: What if Q, Z, X are null insertions?
null_chars = set("QZXJW")
cleaned = ''.join(ch for i, ch in enumerate(VIG_OUTPUT) if ch not in null_chars or i in crib_positions)
print(f"Remove Q,Z,X,J,W from non-crib portions: {cleaned}")
print(f"  Length: {len(cleaned)}, Score: {quadgram_score(cleaned):.2f}")
print()


# ============================================================
# FINAL COMPREHENSIVE SCORING TABLE
# ============================================================

print()
print("=" * 80)
print("FINAL COMPREHENSIVE RESULTS")
print("=" * 80)
print()
print(f"{'Method':<55} {'Score':>8} {'Comment'}")
print(f"{'-'*55} {'-'*8} {'-'*30}")

final_results = [
    ("English reference text", english_reference_score, "Target score"),
    ("Raw Vig output (identity mapping at cribs!)", quadgram_score(VIG_OUTPUT), "Contains 2 English cribs"),
    ("Null removal: every 2nd char (offset 1)", -316.67, "BEST SCORE - investigate!"),
    ("Null removal: every 2nd char (offset 0)", quadgram_score(''.join(VIG_OUTPUT[i] for i in range(97) if (i % 2) != 0)), ""),
    ("KRYPTOS Atbash", quadgram_score(atbash_k), ""),
    ("Standard Atbash", quadgram_score(atbash_s), ""),
    ("Best Caesar (ROT-24)", best_caesar[0], ""),
    ("Best Affine (identity)", best_affine[0], ""),
    ("Best keyword sub", best_keyword[0], ""),
    ("Best columnar transposition (9 cols)", best_col_trans[0], ""),
    ("Reversed text", quadgram_score(reversed_vig), ""),
    ("Best double Vigenere", best_double_vig[0], ""),
    ("Best Beaufort", best_beaufort[0], ""),
    ("Random text reference", random_text_score, "Baseline for random"),
]

for method, score, comment in final_results:
    print(f"  {method:<55} {score:>8.2f} {comment}")

print()
print("=" * 80)
print("MOST IMPORTANT FINDINGS")
print("=" * 80)
print()
print("1. IDENTITY MAPPING: The substitution derived from cribs is the IDENTITY")
print("   function. Every letter maps to itself. This means the Vigenere key")
print("   OYNKYELYOIECBAQKCBNJQRDUMRIYW decrypts to the actual plaintext at")
print("   crib positions, with NO additional masking layer for those letters.")
print()
print("2. NULL REMOVAL ANOMALY: Removing every 2nd char (offset 1) gives a")
print("   score of -316.67, better than the English reference. This needs")
print("   careful investigation - could indicate null interleaving.")
print()
print("3. THE NON-CRIB TEXT: The portions outside the cribs have low vowel")
print("   frequency (~20-28% vs English 38%), suggesting possible vowel")
print("   removal, abbreviation, or encoding in those segments.")
print()
print("4. NO SIMPLE CIPHER LAYER FOUND: No Caesar, Atbash, affine, keyword,")
print("   double-Vigenere, Beaufort, or Playfair layer improves the score")
print("   significantly. The identity at cribs rules these out.")
print()
print("5. WORD FRAGMENTS: The non-crib text contains word fragments like")
print("   FELL, IMP, HOLD, ELL, SAG suggesting the plaintext may be")
print("   partially readable with the right parsing.")
print()
print("6. NULL REMOVAL CORRECTION: The -316.67 score for null removal is")
print("   actually poor when normalized for text length (49 chars).")
print("   English text of 49 chars scores ~-174. So -316 is WORSE")
print("   than English for that length. The initial comparison was")
print("   misleading because it compared against a 97-char reference.")
print()

# ============================================================
# NORMALIZED SCORE COMPARISON
# ============================================================

print("=" * 80)
print("LENGTH-NORMALIZED SCORE COMPARISON (score per quadgram)")
print("=" * 80)
print()

ref_97 = "THEUNITEDSTATESOFAMERICAISTHECOUNTRYWITHTHELARGESTECONOMYINTHEWORLDANDHASTHELARGESTMILITARYBUDGET"
ref_49 = ref_97[:49]
ref_48 = ref_97[:48]

ref_97_score = quadgram_score(ref_97)
ref_49_score = quadgram_score(ref_49)
ref_48_score = quadgram_score(ref_48)

# Per-quadgram normalization
def normalized_score(text):
    sc = quadgram_score(text)
    n_quads = max(1, len(text) - 3)
    return sc / n_quads

print(f"{'Method':<50} {'Raw':>8} {'Len':>4} {'Per-QG':>8}")
print(f"{'-'*50} {'-'*8} {'-'*4} {'-'*8}")

norm_results = [
    ("English reference (97 chars)", ref_97_score, 97),
    ("English reference (49 chars)", ref_49_score, 49),
    ("English reference (48 chars)", ref_48_score, 48),
    ("Raw Vig output", quadgram_score(VIG_OUTPUT), 97),
    ("Null removal offset=1 (49 chars)", quadgram_score(''.join(VIG_OUTPUT[i] for i in range(97) if (i%2)!=1)), 49),
    ("Null removal offset=0 (48 chars)", quadgram_score(''.join(VIG_OUTPUT[i] for i in range(97) if (i%2)!=0)), 48),
    ("Best columnar transposition", best_col_trans[0], 97),
    ("Best double Vigenere", best_double_vig[0], 97),
]

for method, score, length in norm_results:
    nquads = max(1, length - 3)
    perscore = score / nquads
    print(f"  {method:<50} {score:>8.2f} {length:>4} {perscore:>8.4f}")

print()
print("A per-quadgram score closer to the English reference (~-3.8)")
print("indicates more English-like text. Random text scores ~-9.4")
print()

print("=" * 80)
print("FINAL CONCLUSION")
print("=" * 80)
print()
print("The most significant finding from this analysis is the IDENTITY MAPPING:")
print("the Vigenere decryption with key OYNKYELYOIECBAQKCBNJQRDUMRIYW produces")
print("the crib plaintext UNCHANGED at all 24 crib positions. Every crib letter")
print("maps to itself (E->E, A->A, S->S, T->T, N->N, O->O, R->R, H->H, B->B,")
print("L->L, I->I, C->C, K->K).")
print()
print("This rules out ANY letter-level substitution masking that would change")
print("the crib letters before Vigenere encryption. The masking (if it exists)")
print("must be one of:")
print("  - Word-level encoding (abbreviations, codes, phonetic spelling)")
print("  - Applied only to non-crib portions of the text")
print("  - A transposition that happens to leave crib positions intact")
print("  - The plaintext genuinely contains non-English elements (names, coords)")
print("  - The key CBNJQ for positions 16-20 may not be optimal, and")
print("    a different key might reveal additional structure")
print()
print("The non-crib portions (73 chars) have notably low vowel frequency")
print("(~20-28% vs English ~38%), supporting the vowel-removal hypothesis")
print("mentioned by Scheidt, but only for the non-crib segments.")
print()
print("DONE.")

