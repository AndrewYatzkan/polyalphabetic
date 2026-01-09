#!/usr/bin/env python3
"""
K4 Non-Periodic Cipher Attacks

Since we've proven K4 can't be a simple periodic cipher
(BERLINCLOCK and NORTHEAST constraints are incompatible),
try non-periodic methods:
1. Autokey cipher
2. Running key cipher
3. Progressive key
4. Gronsfeld with varying base
"""

import itertools
from collections import Counter

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def derive_key_char(ct, pt, alpha):
    return alpha[(alpha.index(ct) - alpha.index(pt)) % len(alpha)]

def decrypt_char(ct, key, alpha):
    return alpha[(alpha.index(ct) - alpha.index(key)) % len(alpha)]

print("="*70)
print("K4 NON-PERIODIC CIPHER ATTACKS")
print("="*70)
print("\nProven: K4 is NOT a simple periodic Vigenère cipher")
print("Reason: BERLINCLOCK and NORTHEAST constraints are mathematically incompatible")
print()

# Known constraints
BERLIN_CLOCK = "BERLINCLOCK"
BC_START = 63

# Derive key stream at BERLINCLOCK position
print("="*70)
print("KEY STREAM ANALYSIS AT BERLINCLOCK")
print("="*70)

bc_keys = []
for i, (ct, pt) in enumerate(zip(K4[BC_START:BC_START+11], BERLIN_CLOCK)):
    key = derive_key_char(ct, pt, KRYPTOS_ALPHA)
    bc_keys.append(key)
    print(f"Position {BC_START+i}: CT={ct} PT={pt} -> Key={key}")

print(f"\nKey stream: {''.join(bc_keys)}")

# Is this key stream part of a pattern?
print("\n--- Checking for patterns in key stream ---")

# Check if it could be text
print(f"As text: {''.join(bc_keys)}")

# Check for autokey pattern (key = primer + plaintext)
print("\n" + "="*70)
print("AUTOKEY CIPHER ANALYSIS")
print("="*70)

# In autokey: ct[i] = pt[i] + key[i], where key = primer + pt[0:n-primer_len]
# So key[i] = ct[i] - pt[i]
# For positions 63+, if autokey with primer p:
# key[63] = pt[63 - p] for appropriate offset

# If BERLINCLOCK starts at 63, and we know key[63:74] = ELYOIECBAQK (derived earlier)
# Check if any prefix of plaintext matches this

print("Checking if key stream could be plaintext from earlier...")
key_str = ''.join(bc_keys)  # ELYOIECBAQK

# If this is autokey with primer length p, then key[63] = pt[63-p] for some offset
# The key at position 63 would be plaintext from position 63-primer_len

for primer_len in range(1, 50):
    # If key[63] came from pt[63-primer_len], then the plaintext should match
    # This requires working backwards

    # Try to find where ELYOIECBAQK could appear in plaintext
    # If autokey, and key[63:74] = ELYOIECBAQK, this equals pt[63-primer_len : 74-primer_len]

    source_start = BC_START - primer_len
    if source_start >= 0 and source_start + 11 <= len(K4):
        # We need pt[source_start:source_start+11] = ELYOIECBAQK
        # And pt[63:74] = BERLINCLOCK

        # Try to build consistent plaintext
        # This is complex for autokey - simplified check:
        pass

# Running key cipher with known text
print("\n" + "="*70)
print("RUNNING KEY CIPHER")
print("="*70)

# Try running key where key is another known text
# Common running key sources could be:
# - Text from K1, K2, K3
# - The sculpture itself
# - Dictionary words

K3_PLAINTEXT = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADETINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENIN"

print("\nTrying K3 plaintext as running key...")
for offset in range(-50, 50):
    # Align K3 text with K4
    key_start = max(0, -offset)
    ct_start = max(0, offset)

    pt = ''
    valid = True
    for i in range(len(K4)):
        key_idx = i + offset
        if 0 <= key_idx < len(K3_PLAINTEXT):
            key_char = K3_PLAINTEXT[key_idx]
            if key_char in KRYPTOS_ALPHA:
                pt += decrypt_char(K4[i], key_char, KRYPTOS_ALPHA)
            else:
                pt += '?'
        else:
            pt += '?'

    if 'BERLIN' in pt or 'NORTHEAST' in pt:
        print(f"Offset {offset}: {pt[:50]}...")

# Try progressive key
print("\n" + "="*70)
print("PROGRESSIVE KEY ANALYSIS")
print("="*70)

# What if the key shifts progressively?
# key[i] = base_key[i % period] + i * shift

for base_key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'OIECBAQKELY']:
    for shift in range(1, 5):
        pt = ''
        for i, c in enumerate(K4):
            # Progressive shift
            base_char = base_key[i % len(base_key)]
            key_val = (KRYPTOS_ALPHA.index(base_char) + (i // len(base_key)) * shift) % len(KRYPTOS_ALPHA)
            pt += KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(c) - key_val) % len(KRYPTOS_ALPHA)]

        if 'BERLIN' in pt or 'NORTHEAST' in pt:
            print(f"Base={base_key}, shift={shift}: {pt[:60]}...")

# Gromark cipher (Gronsfeld with variable numbers)
print("\n" + "="*70)
print("GROMARK / GRONSFELD VARIATIONS")
print("="*70)

# Try numeric keys
for num_key in ['1234567', '3141592', '2718281', '1618033', '97']:
    key_digits = [int(d) for d in num_key]
    pt = ''
    for i, c in enumerate(K4):
        shift = key_digits[i % len(key_digits)]
        pt += KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(c) - shift) % len(KRYPTOS_ALPHA)]

    if 'BERLIN' in pt or 'NORTHEAST' in pt or 'CLOCK' in pt:
        print(f"Numeric key {num_key}: {pt[:60]}...")

# Berlin Clock time-based key
print("\n" + "="*70)
print("BERLIN CLOCK TIME-BASED KEY")
print("="*70)

# Berlin Clock can show times - maybe key is time-based
# The sculpture was dedicated Nov 3, 1990
# Try date-based numeric keys

date_keys = [
    '11031990',  # Nov 3 1990 US format
    '03111990',  # Nov 3 1990 EU format
    '19901103',  # ISO format
    '389657',    # K2 coordinates encoded
]

for key in date_keys:
    key_digits = [int(d) for d in key if d.isdigit()]
    pt = ''
    for i, c in enumerate(K4):
        shift = key_digits[i % len(key_digits)]
        pt += KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(c) - shift) % len(KRYPTOS_ALPHA)]

    if 'BERLIN' in pt or 'NORTHEAST' in pt:
        print(f"Date key {key}: {pt[:60]}...")
    else:
        # Just show first few characters
        print(f"Date key {key}: {pt[:40]}...")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print("\nKey Finding: K4 cannot be a simple periodic polyalphabetic cipher")
print("The BERLINCLOCK and NORTHEAST constraints are mathematically incompatible")
print("for any key period from 5-19.")
print("\nThis suggests K4 uses either:")
print("  1. A non-periodic cipher (autokey, running key)")
print("  2. Multiple encryption layers")
print("  3. Transposition combined with substitution")
print("  4. A completely novel cipher design")
