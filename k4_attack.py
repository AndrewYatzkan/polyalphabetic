#!/usr/bin/env python3
"""
K4 Attack Script - Comprehensive attack on Kryptos K4

Known information:
- Ciphertext: 97 characters
- Position 64-69 (1-indexed): NYPVTT -> BERLIN
- Position 70-74 (1-indexed): MZFPK -> CLOCK
- NORTHEAST appears somewhere in plaintext (2020 hint)

This script tries various cipher types and modifications.
"""

import itertools
import string
from collections import Counter

# K4 Ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known cribs (0-indexed)
CRIBS = {
    63: 'B',  # BERLIN starts at position 63 (0-indexed)
    64: 'E',
    65: 'R',
    66: 'L',
    67: 'I',
    68: 'N',
    69: 'C',  # CLOCK starts at position 69
    70: 'L',
    71: 'O',
    72: 'C',
    73: 'K',
}

# KRYPTOS keyed alphabet
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def create_keyed_alphabet(keyword):
    """Create a keyed alphabet from a keyword."""
    seen = set()
    result = []
    for c in keyword.upper():
        if c not in seen and c in STANDARD_ALPHA:
            seen.add(c)
            result.append(c)
    for c in STANDARD_ALPHA:
        if c not in seen:
            result.append(c)
    return ''.join(result)

def vigenere_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    """Decrypt using Vigenère cipher."""
    result = []
    key_index = 0
    for c in ciphertext:
        if c in alphabet:
            ct_pos = alphabet.index(c)
            key_pos = alphabet.index(key[key_index % len(key)])
            pt_pos = (ct_pos - key_pos) % len(alphabet)
            result.append(alphabet[pt_pos])
            key_index += 1
        else:
            result.append(c)
    return ''.join(result)

def vigenere_encrypt(plaintext, key, alphabet=STANDARD_ALPHA):
    """Encrypt using Vigenère cipher."""
    result = []
    key_index = 0
    for c in plaintext:
        if c in alphabet:
            pt_pos = alphabet.index(c)
            key_pos = alphabet.index(key[key_index % len(key)])
            ct_pos = (pt_pos + key_pos) % len(alphabet)
            result.append(alphabet[ct_pos])
            key_index += 1
        else:
            result.append(c)
    return ''.join(result)

def beaufort_decrypt(ciphertext, key, alphabet=STANDARD_ALPHA):
    """Decrypt using Beaufort cipher (symmetric)."""
    result = []
    key_index = 0
    for c in ciphertext:
        if c in alphabet:
            ct_pos = alphabet.index(c)
            key_pos = alphabet.index(key[key_index % len(key)])
            pt_pos = (key_pos - ct_pos) % len(alphabet)
            result.append(alphabet[pt_pos])
            key_index += 1
        else:
            result.append(c)
    return ''.join(result)

def derive_key_from_cribs(ciphertext, cribs, alphabet=STANDARD_ALPHA):
    """Derive key characters from known plaintext-ciphertext pairs."""
    key_chars = {}
    for pos, pt_char in cribs.items():
        ct_char = ciphertext[pos]
        ct_pos = alphabet.index(ct_char)
        pt_pos = alphabet.index(pt_char)
        # For Vigenère: ct = pt + key, so key = ct - pt
        key_val = (ct_pos - pt_pos) % len(alphabet)
        key_char = alphabet[key_val]
        key_chars[pos] = key_char
    return key_chars

def analyze_key_pattern(key_chars, ciphertext_len):
    """Analyze derived key characters for patterns."""
    print("\n=== Key Analysis from Cribs ===")
    for pos, key_char in sorted(key_chars.items()):
        ct = K4[pos]
        pt = CRIBS[pos]
        print(f"Position {pos:2d}: CT={ct} -> PT={pt}, Key={key_char}")

    # Check for period patterns
    print("\n=== Period Analysis ===")
    positions = sorted(key_chars.keys())
    for period in range(1, 15):
        matches = []
        for p1, p2 in itertools.combinations(positions, 2):
            if (p2 - p1) % period == 0 and key_chars[p1] == key_chars[p2]:
                matches.append((p1, p2, key_chars[p1]))
        if matches:
            print(f"Period {period}: {len(matches)} matching pairs - {matches}")

def try_key_extensions(key_chars, ciphertext, period):
    """Try to extend partial key to full key."""
    print(f"\n=== Trying period {period} ===")

    # Group key chars by position mod period
    groups = {}
    for pos, key_char in key_chars.items():
        group = pos % period
        if group not in groups:
            groups[group] = []
        groups[group].append((pos, key_char))

    print(f"Key groups: {groups}")

    # Try to construct full key
    key = ['?'] * period
    for group, chars in groups.items():
        # Check if all chars in group are consistent
        unique_chars = set(c for _, c in chars)
        if len(unique_chars) == 1:
            key[group] = list(unique_chars)[0]
        else:
            print(f"  Group {group} inconsistent: {unique_chars}")

    print(f"Partial key: {''.join(key)}")
    return key

def brute_force_remaining(partial_key, ciphertext, cribs, alphabet=STANDARD_ALPHA):
    """Brute force remaining unknown key positions."""
    unknown_positions = [i for i, c in enumerate(partial_key) if c == '?']

    if len(unknown_positions) > 5:
        print(f"Too many unknowns ({len(unknown_positions)}) for brute force")
        return None

    print(f"Brute forcing {len(unknown_positions)} positions...")

    best_score = 0
    best_key = None
    best_plaintext = None

    # Common English patterns to look for
    common_words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                   'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'NORTH', 'EAST',
                   'WEST', 'SOUTH', 'BERLIN', 'CLOCK', 'SECRET', 'HIDDEN']

    for combo in itertools.product(alphabet, repeat=len(unknown_positions)):
        key = list(partial_key)
        for i, pos in enumerate(unknown_positions):
            key[pos] = combo[i]
        key_str = ''.join(key)

        plaintext = vigenere_decrypt(ciphertext, key_str, alphabet)

        # Check if cribs match
        crib_match = all(plaintext[pos] == pt for pos, pt in cribs.items())
        if not crib_match:
            continue

        # Score based on common patterns
        score = sum(1 for word in common_words if word in plaintext)

        # Check for NORTHEAST
        if 'NORTHEAST' in plaintext:
            score += 10

        if score > best_score:
            best_score = score
            best_key = key_str
            best_plaintext = plaintext
            print(f"  Score {score}: Key={key_str}")
            print(f"    {plaintext[:50]}...")

    return best_key, best_plaintext

def try_modified_vigenere(ciphertext, cribs):
    """Try Vigenère with various alphabets."""
    print("\n=== Modified Vigenère Attempts ===")

    alphabets = [
        ("Standard", STANDARD_ALPHA),
        ("KRYPTOS", KRYPTOS_ALPHA),
        ("Reversed", STANDARD_ALPHA[::-1]),
        ("KRYPTOS Reversed", KRYPTOS_ALPHA[::-1]),
    ]

    for name, alpha in alphabets:
        print(f"\n--- Alphabet: {name} ---")
        key_chars = derive_key_from_cribs(ciphertext, cribs, alpha)

        # Try various periods
        for period in range(5, 12):
            partial_key = try_key_extensions(key_chars, ciphertext, period)
            unknowns = partial_key.count('?')
            if unknowns <= 4:
                result = brute_force_remaining(partial_key, ciphertext, cribs, alpha)
                if result and result[0]:
                    print(f"POTENTIAL SOLUTION with {name}, period {period}!")
                    print(f"Key: {result[0]}")
                    print(f"Plaintext: {result[1]}")

def try_autokey(ciphertext, cribs, alphabet=STANDARD_ALPHA):
    """Try autokey cipher variations."""
    print("\n=== Autokey Cipher Attempts ===")

    # In autokey, the key is a primer followed by the plaintext itself
    # ct[i] = pt[i] + key[i] where key = primer + plaintext

    for primer_len in range(3, 10):
        print(f"\n--- Primer length {primer_len} ---")
        # We can derive constraints from cribs
        # This is complex for autokey, simplified attempt:

        for primer in itertools.product(alphabet[:10], repeat=min(primer_len, 3)):
            primer_str = ''.join(primer)
            # Simplified autokey decrypt
            pt = []
            key = list(primer_str)
            for i, c in enumerate(ciphertext):
                if c in alphabet:
                    ct_pos = alphabet.index(c)
                    key_pos = alphabet.index(key[i % len(key)] if i < len(key) else key[-1])
                    pt_char = alphabet[(ct_pos - key_pos) % len(alphabet)]
                    pt.append(pt_char)
                    if i >= primer_len:
                        key.append(pt_char)

            plaintext = ''.join(pt)

            # Check cribs
            if all(plaintext[pos] == char for pos, char in cribs.items() if pos < len(plaintext)):
                if 'NORTHEAST' in plaintext or 'BERLIN' in plaintext:
                    print(f"Potential: primer={primer_str}, plaintext={plaintext[:60]}...")

def statistical_analysis(ciphertext):
    """Perform statistical analysis on K4."""
    print("\n=== Statistical Analysis ===")

    print(f"Length: {len(ciphertext)}")

    # Frequency analysis
    freq = Counter(ciphertext)
    print(f"\nCharacter frequencies:")
    for char, count in freq.most_common():
        pct = count / len(ciphertext) * 100
        print(f"  {char}: {count} ({pct:.1f}%)")

    # Index of coincidence
    n = len(ciphertext)
    ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
    print(f"\nIndex of Coincidence: {ic:.4f}")
    print(f"  (English ~0.067, random ~0.038)")

    # Kasiski examination - find repeated sequences
    print("\n=== Repeated Sequences ===")
    for seq_len in range(3, 6):
        sequences = {}
        for i in range(len(ciphertext) - seq_len + 1):
            seq = ciphertext[i:i + seq_len]
            if seq not in sequences:
                sequences[seq] = []
            sequences[seq].append(i)

        repeats = {s: p for s, p in sequences.items() if len(p) > 1}
        if repeats:
            print(f"\nLength {seq_len} repeats:")
            for seq, positions in sorted(repeats.items(), key=lambda x: -len(x[1])):
                distances = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
                print(f"  '{seq}' at {positions}, distances: {distances}")

def try_transposition_first(ciphertext, cribs):
    """Try transposition before substitution."""
    print("\n=== Transposition + Substitution ===")

    # Try simple columnar transposition
    for cols in range(5, 15):
        rows = (len(ciphertext) + cols - 1) // cols

        # Read by columns
        transposed = [''] * len(ciphertext)
        idx = 0
        for c in range(cols):
            for r in range(rows):
                pos = r * cols + c
                if pos < len(ciphertext) and idx < len(ciphertext):
                    transposed[pos] = ciphertext[idx]
                    idx += 1

        transposed_str = ''.join(transposed)

        # Try Vigenère on transposed
        for period in range(7, 12):
            for key_start in ['KRYPTOS', 'BERLIN', 'CLOCK']:
                key = (key_start * ((period // len(key_start)) + 1))[:period]
                pt = vigenere_decrypt(transposed_str, key, KRYPTOS_ALPHA)

                if 'NORTHEAST' in pt or ('BERLIN' in pt and 'CLOCK' in pt):
                    print(f"POTENTIAL: cols={cols}, key={key}")
                    print(f"  {pt}")

def main():
    print("=" * 70)
    print("K4 COMPREHENSIVE ATTACK")
    print("=" * 70)
    print(f"\nCiphertext: {K4}")
    print(f"Length: {len(K4)}")

    # Statistical analysis
    statistical_analysis(K4)

    # Derive key info from cribs
    print("\n" + "=" * 70)
    print("CRIB ANALYSIS")
    print("=" * 70)

    key_chars = derive_key_from_cribs(K4, CRIBS, KRYPTOS_ALPHA)
    analyze_key_pattern(key_chars, len(K4))

    # Try standard approaches
    print("\n" + "=" * 70)
    print("CIPHER ATTACKS")
    print("=" * 70)

    try_modified_vigenere(K4, CRIBS)

    # Try transposition combinations
    try_transposition_first(K4, CRIBS)

    print("\n" + "=" * 70)
    print("ATTACK COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
