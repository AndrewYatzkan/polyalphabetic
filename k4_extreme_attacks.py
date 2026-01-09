#!/usr/bin/env python3
"""
K4 EXTREME ATTACK METHODS

Really unusual approaches:
1. Hill cipher (2x2 and 3x3 matrices)
2. Four-square cipher
3. Two-square cipher
4. Trifid cipher
5. ADFGVX cipher
6. Fractionated Morse
7. Straddling checkerboard
8. Ciphertext as key (self-keyed)
9. Reverse operations
10. Sculpture-based clues
"""

# numpy not needed
from collections import Counter
import itertools

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

print("="*70)
print("K4 EXTREME ATTACK METHODS")
print("="*70)

# ============================================================
# ATTACK 1: Hill Cipher (2x2)
# ============================================================
print("\n" + "="*70)
print("ATTACK 1: HILL CIPHER (2x2 matrices)")
print("="*70)

def mod_inverse(a, m):
    """Find modular multiplicative inverse."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def matrix_mod_inverse_2x2(matrix, mod=26):
    """Find modular inverse of 2x2 matrix."""
    a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    det = (a * d - b * c) % mod
    det_inv = mod_inverse(det, mod)
    if det_inv is None:
        return None
    
    return [
        [(d * det_inv) % mod, (-b * det_inv) % mod],
        [(-c * det_inv) % mod, (a * det_inv) % mod]
    ]

def hill_decrypt_2x2(ct, key_matrix, alpha=STANDARD_ALPHA):
    """Decrypt using 2x2 Hill cipher."""
    inv_matrix = matrix_mod_inverse_2x2(key_matrix)
    if inv_matrix is None:
        return None
    
    pt = []
    for i in range(0, len(ct) - 1, 2):
        c1 = alpha.index(ct[i])
        c2 = alpha.index(ct[i+1])
        
        p1 = (inv_matrix[0][0] * c1 + inv_matrix[0][1] * c2) % 26
        p2 = (inv_matrix[1][0] * c1 + inv_matrix[1][1] * c2) % 26
        
        pt.append(alpha[p1])
        pt.append(alpha[p2])
    
    return ''.join(pt)

# Try some specific matrices
test_matrices = [
    [[3, 2], [5, 7]],   # Classic example
    [[6, 24], [1, 13]], # Another common one
    [[11, 8], [3, 7]],  # From KRYPTOS letters
    [[2, 1], [1, 1]],   # Fibonacci-related
]

print("Testing 2x2 Hill cipher...")
for matrix in test_matrices:
    pt = hill_decrypt_2x2(K4, matrix)
    if pt:
        words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
        if words:
            print(f"Matrix {matrix}: Found {words}")
            print(f"  PT: {pt[:50]}...")

# ============================================================
# ATTACK 2: Self-Keyed Variants
# ============================================================
print("\n" + "="*70)
print("ATTACK 2: SELF-KEYED VARIANTS")
print("="*70)

def ciphertext_autokey_decrypt(ct, primer, alpha=KRYPTOS_ALPHA):
    """Autokey where key = primer + CIPHERTEXT (not plaintext)."""
    pt = []
    for i, c in enumerate(ct):
        if i < len(primer):
            key_char = primer[i]
        else:
            key_char = ct[i - len(primer)]  # Use ciphertext as key
        
        pt_char = alpha[(alpha.index(c) - alpha.index(key_char)) % len(alpha)]
        pt.append(pt_char)
    return ''.join(pt)

print("Testing ciphertext-autokey (key = primer + ciphertext)...")
for primer in ['K', 'KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN']:
    pt = ciphertext_autokey_decrypt(K4, primer)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE', 'SLOWLY'] if w in pt]
    if words:
        print(f"Primer '{primer}': Found {words}")
        print(f"  PT: {pt}")

# ============================================================
# ATTACK 3: Beaufort Variant
# ============================================================
print("\n" + "="*70)
print("ATTACK 3: BEAUFORT CIPHER")
print("="*70)

def beaufort_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Beaufort: pt = key - ct (mod 26)."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        pt_char = alpha[(alpha.index(k) - alpha.index(c)) % len(alpha)]
        result.append(pt_char)
    return ''.join(result)

print("Testing Beaufort cipher...")
for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'ELYOIECBAQK', 'CLOCK']:
    pt = beaufort_decrypt(K4, key)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"Key '{key}': Found {words}")
        print(f"  PT: {pt[:60]}...")

# ============================================================
# ATTACK 4: Running Key from K1-K3 Plaintexts
# ============================================================
print("\n" + "="*70)
print("ATTACK 4: RUNNING KEY FROM OTHER KRYPTOS SECTIONS")
print("="*70)

# K1 plaintext
K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUNANCEOFIQLUSION"

# K2 plaintext (condensed)
K2_PT = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIED"

# K3 plaintext
K3_PT = "SLOWLYDESPARATLYSLOWTHEREMAINSOFPASSAGEDEBRISLOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLING"

def running_key_decrypt(ct, running_key, alpha=KRYPTOS_ALPHA):
    """Running key cipher - key as long as plaintext."""
    pt = []
    for i, c in enumerate(ct):
        if i >= len(running_key):
            break
        k = running_key[i]
        if k not in alpha:
            pt.append('?')
            continue
        pt_char = alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)]
        pt.append(pt_char)
    return ''.join(pt)

print("Testing running key from K1/K2/K3 plaintexts...")
for name, running in [("K1", K1_PT), ("K2", K2_PT), ("K3", K3_PT)]:
    pt = running_key_decrypt(K4, running)
    print(f"\nRunning key from {name}:")
    print(f"  PT: {pt[:60]}...")
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE', 'SLOWLY'] if w in pt]
    if words:
        print(f"  Found: {words}")

# Also try the reversed plaintexts
print("\nTrying REVERSED running keys...")
for name, running in [("K1", K1_PT[::-1]), ("K2", K2_PT[::-1]), ("K3", K3_PT[::-1])]:
    pt = running_key_decrypt(K4, running)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"Reversed {name}: Found {words}")
        print(f"  PT: {pt}")

# ============================================================
# ATTACK 5: Morse Code on Sculpture
# ============================================================
print("\n" + "="*70)
print("ATTACK 5: MORSE CODE FROM SCULPTURE")
print("="*70)

# The Kryptos sculpture has Morse code that spells:
# "SOS" and other messages, plus "VIRTUALLY INVISIBLE" and others
# On the sculpture: E, T, DIGETAL INTERPRETU, SHADOW FORCES, etc.

morse_messages = [
    "VIRTUALLYINVISIBLE",
    "SHADOWFORCES",
    "ITSHOULDBE",
    "LUCID",
    "MEMORY",
    "DIGETAL",  # Intentional misspelling on sculpture
    "INTERPRETU",
]

print("Testing Morse code messages from sculpture as keys...")
for msg in morse_messages:
    pt = running_key_decrypt(K4, msg * 10, KRYPTOS_ALPHA)  # Repeat to cover length
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"Key '{msg}': Found {words}")
        print(f"  PT: {pt}")

# ============================================================
# ATTACK 6: Coordinates as Direct Key
# ============================================================
print("\n" + "="*70)
print("ATTACK 6: K2 COORDINATES AS KEY")
print("="*70)

# K2 coordinates: 38°57'6.5"N, 77°8'44"W
# Different encodings
coord_keys = [
    "THIRTYEIGHTFIFTYSEVENSIXPOINTFIVE",
    "SEVENTYSEVENEIGTFORTYFOUR",
    "THREEEIGHTFIVESEVENSIXX",
    "SEVENSENENIHEIGHTFOURFOUR",
    "NWLOCATION",
]

print("Testing coordinate-derived keys...")
for key in coord_keys:
    for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
        pt = running_key_decrypt(K4, key * 5, alpha)
        words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST'] if w in pt]
        if words:
            print(f"Key '{key[:20]}...': Found {words}")

# ============================================================
# ATTACK 7: Interrupted Key
# ============================================================
print("\n" + "="*70)
print("ATTACK 7: INTERRUPTED KEY")
print("="*70)

def interrupted_key_decrypt(ct, key, interrupt_positions, alpha=KRYPTOS_ALPHA):
    """Key resets at interrupt positions."""
    pt = []
    key_pos = 0
    for i, c in enumerate(ct):
        if i in interrupt_positions:
            key_pos = 0
        k = key[key_pos % len(key)]
        pt_char = alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)]
        pt.append(pt_char)
        key_pos += 1
    return ''.join(pt)

# Try interruptions at word boundaries (every N chars)
print("Testing interrupted key patterns...")
for key in ['KRYPTOS', 'PALIMPSEST']:
    for interval in [10, 11, 12, 13, 14, 15, 19, 20]:
        interrupts = set(range(0, len(K4), interval))
        pt = interrupted_key_decrypt(K4, key, interrupts)
        words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST'] if w in pt]
        if words:
            print(f"Key {key}, interrupt every {interval}: {words}")
            print(f"  PT: {pt}")

# ============================================================
# ATTACK 8: Reverse Ciphertext First
# ============================================================
print("\n" + "="*70)
print("ATTACK 8: REVERSE CIPHERTEXT APPROACHES")
print("="*70)

K4_REV = K4[::-1]
print(f"Reversed K4: {K4_REV}")

for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'ELYOIECBAQK']:
    pt = running_key_decrypt(K4_REV, key * 20, KRYPTOS_ALPHA)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'NILREB'] if w in pt]
    if words:
        print(f"Reversed + Key '{key}': {words}")
        print(f"  PT: {pt}")

# ============================================================
# ATTACK 9: Position 63 Constraint Exploitation  
# ============================================================
print("\n" + "="*70)
print("ATTACK 9: EXPLOIT POSITION 63 CONSTRAINT")
print("="*70)

# We KNOW position 63-73 decrypts to BERLINCLOCK
# What if we work outward from there?

# The key at position 63-73 is ELYOIECBAQK
# What patterns lead to position 63?

print("Key stream analysis around position 63...")
derived_key = "ELYOIECBAQK"

# What if the key has a pattern we can extend?
print(f"Key at 63-73: {derived_key}")
print("Looking for patterns in key...")

# Check if it's an anagram
sorted_key = ''.join(sorted(derived_key))
print(f"Sorted: {sorted_key}")

# Check letter frequencies
freq = Counter(derived_key)
print(f"Frequencies: {dict(freq)}")

# ============================================================
# ATTACK 10: Anagram of Known Words
# ============================================================
print("\n" + "="*70)
print("ATTACK 10: KEY AS ANAGRAM")
print("="*70)

# ELYOIECBAQK contains: A, B, C, E, E, I, K, L, O, Q, Y
# 11 letters with E appearing twice

# Try to form meaningful words/phrases
from itertools import permutations

# Too many permutations, but let's check specific anagrams
anagram_candidates = [
    "BLACKEYEQIO",  # Not quite
    "EQUIVOCABLY",  # Close letters
    "BEYLIKACQOE",
]

for candidate in anagram_candidates:
    if sorted(candidate) == sorted(derived_key):
        print(f"Found anagram: {candidate}")

print("\n" + "="*70)
print("EXTREME ATTACKS COMPLETE")
print("="*70)
