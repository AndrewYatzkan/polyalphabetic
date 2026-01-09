#!/usr/bin/env python3
"""
K4 Creative Attack Suite

Unconventional approaches to crack K4:
1. Berlin Clock mechanism as key generator
2. Playfair cipher variants
3. Bifid/Trifid ciphers
4. Progressive/shifted keys
5. Coordinate-based keys from K2
6. Morse code analysis
7. Null cipher detection
8. Gromark cipher
"""

import itertools
from collections import Counter
import math

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)])
    return ''.join(result)

print("="*70)
print("K4 CREATIVE ATTACK SUITE")
print("="*70)

# ============================================================
# ATTACK 1: Berlin Clock Mechanism
# ============================================================
print("\n" + "="*70)
print("ATTACK 1: BERLIN CLOCK PATTERNS")
print("="*70)

# Berlin Clock displays time in specific way
# What if the key follows this pattern?

# Try CLOCK-related words as keys
clock_keys = [
    'CLOCK', 'BERLIN', 'BERLINCLOCK', 'CLOCKBERLIN',
    'MENGENLEHREUHR',  # German name for Berlin Clock
    'SETTHECLOCKUHR',
    'TIME', 'ZEIT',  # German for time
    'CLOCKWORK',
]

print("Testing clock-themed keys...")
for key in clock_keys:
    pt = vigenere_decrypt(K4, key)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE', 'SLOWLY'] if w in pt]
    if words:
        print(f"Key '{key}': Found {words}")
        print(f"  PT: {pt[:60]}...")

# ============================================================
# ATTACK 2: Playfair Cipher
# ============================================================
print("\n" + "="*70)
print("ATTACK 2: PLAYFAIR CIPHER")
print("="*70)

def create_playfair_grid(keyword):
    keyword = keyword.upper().replace('J', 'I')
    seen = set()
    grid = []
    for c in keyword + "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if c not in seen and c.isalpha():
            seen.add(c)
            grid.append(c)
    return [grid[i:i+5] for i in range(0, 25, 5)]

def playfair_decrypt(ct, grid):
    pos = {}
    for r, row in enumerate(grid):
        for c, char in enumerate(row):
            pos[char] = (r, c)

    ct = ct.replace('J', 'I')
    if len(ct) % 2:
        ct += 'X'

    pt = []
    for i in range(0, len(ct), 2):
        a, b = ct[i], ct[i+1]
        if a not in pos or b not in pos:
            pt.extend([a, b])
            continue
        ra, ca = pos[a]
        rb, cb = pos[b]

        if ra == rb:
            pt.append(grid[ra][(ca - 1) % 5])
            pt.append(grid[rb][(cb - 1) % 5])
        elif ca == cb:
            pt.append(grid[(ra - 1) % 5][ca])
            pt.append(grid[(rb - 1) % 5][cb])
        else:
            pt.append(grid[ra][cb])
            pt.append(grid[rb][ca])

    return ''.join(pt)

playfair_keywords = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK',
                     'BERLINCLOCK', 'SANBORN', 'CIA', 'LANGLEY', 'SHADOW']

print("Testing Playfair cipher...")
for kw in playfair_keywords:
    grid = create_playfair_grid(kw)
    pt = playfair_decrypt(K4, grid)
    
    if 'BERLIN' in pt or 'CLOCK' in pt or 'NORTH' in pt or 'EAST' in pt:
        print(f"Keyword: {kw} - Found crib!")
        print(f"  Plaintext: {pt}")

# ============================================================
# ATTACK 3: Progressive Key Shift
# ============================================================
print("\n" + "="*70)
print("ATTACK 3: PROGRESSIVE KEY SHIFT")
print("="*70)

def progressive_decrypt(ct, base_key, shift_func, alpha=KRYPTOS_ALPHA):
    result = []
    for i, c in enumerate(ct):
        key_idx = i % len(base_key)
        shift = shift_func(i)
        effective_key = alpha[(alpha.index(base_key[key_idx]) + shift) % len(alpha)]
        pt_char = alpha[(alpha.index(c) - alpha.index(effective_key)) % len(alpha)]
        result.append(pt_char)
    return ''.join(result)

base_key = "ELYOIECBAQK"  # Key derived from BERLINCLOCK

shift_patterns = [
    ("Linear +1", lambda i: i),
    ("Linear -1", lambda i: -i),
    ("Mod 11", lambda i: i % 11),
    ("Floor div 11", lambda i: i // 11),
    ("Triangular", lambda i: i * (i + 1) // 2 % 26),
]

print("Testing progressive shifts with ELYOIECBAQK base key...")
for name, pattern in shift_patterns:
    pt = progressive_decrypt(K4, base_key, pattern)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"{name}: Found {words}")
        print(f"  PT: {pt[:60]}...")

# ============================================================
# ATTACK 4: Null Cipher Detection  
# ============================================================
print("\n" + "="*70)
print("ATTACK 4: NULL CIPHER DETECTION")
print("="*70)

print("Extracting patterns from K4...")

# Every Nth character
for n in range(2, 15):
    for offset in range(n):
        extracted = K4[offset::n]
        for word in ['THE', 'AND', 'BERLIN', 'CLOCK', 'CIA', 'NORTH', 'SECRET']:
            if word in extracted:
                print(f"Every {n}th char (offset {offset}): ...{word}... in {extracted}")

# First letters of groups
for gs in range(3, 12):
    first = ''.join(K4[i] for i in range(0, len(K4), gs))
    for word in ['THE', 'CIA', 'SPY', 'BERLIN']:
        if word in first:
            print(f"First of every {gs}: {first}")

# ============================================================
# ATTACK 5: Substitution + Transposition Combo
# ============================================================
print("\n" + "="*70)
print("ATTACK 5: DOUBLE LAYER ATTACKS")
print("="*70)

def reverse_columnar(ct, num_cols):
    num_rows = math.ceil(len(ct) / num_cols)
    full_cols = len(ct) % num_cols or num_cols
    
    result = [''] * len(ct)
    pos = 0
    for col in range(num_cols):
        col_len = num_rows if col < full_cols else num_rows - 1
        for row in range(col_len):
            idx = row * num_cols + col
            if idx < len(ct):
                result[idx] = ct[pos]
            pos += 1
    return ''.join(c for c in result if c)

print("Testing transposition -> substitution...")
for cols in range(5, 15):
    transposed = reverse_columnar(K4, cols)
    for key in ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'ELYOIECBAQK']:
        decrypted = vigenere_decrypt(transposed, key)
        if 'BERLIN' in decrypted or 'CLOCK' in decrypted:
            print(f"Cols={cols}, Key={key}: {decrypted}")

print("\nTesting substitution -> reverse transposition...")
for key in ['KRYPTOS', 'PALIMPSEST', 'ELYOIECBAQK']:
    substituted = vigenere_decrypt(K4, key)
    for cols in range(5, 15):
        transposed = reverse_columnar(substituted, cols)
        if 'BERLIN' in transposed or 'CLOCK' in transposed:
            print(f"Key={key}, Cols={cols}: {transposed}")

# ============================================================
# ATTACK 6: Gromark Cipher
# ============================================================
print("\n" + "="*70)
print("ATTACK 6: GROMARK CIPHER")
print("="*70)

def gromark_decrypt(ct, primer, alpha=STANDARD_ALPHA):
    key_nums = [int(c) if c.isdigit() else (ord(c.upper()) - 65) % 10 for c in primer]
    
    pt = []
    for i, c in enumerate(ct):
        if i < len(key_nums):
            shift = key_nums[i]
        else:
            shift = (key_nums[-1] + key_nums[-2]) % 10
            key_nums.append(shift)
        
        pt_char = alpha[(alpha.index(c) - shift) % len(alpha)]
        pt.append(pt_char)
    
    return ''.join(pt)

primers = ['1990', '385765778844', 'KRYPTOS', '63', '97', '11031990', '19901103']
print("Testing Gromark cipher...")
for primer in primers:
    pt = gromark_decrypt(K4, primer)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"Primer {primer}: {words}")
        print(f"  PT: {pt}")

# ============================================================
# ATTACK 7: Mixed Alphabet Variants
# ============================================================
print("\n" + "="*70)
print("ATTACK 7: ALTERNATIVE ALPHABETS")
print("="*70)

# What if K4 uses a different keyed alphabet?
alt_alphabets = [
    ("Standard", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    ("Reversed", "ZYXWVUTSRQPONMLKJIHGFEDCBA"),
    ("KRYPTOS", "KRYPTOSABCDEFGHIJLMNQUVWXZ"),
    ("PALIMPSEST", "PALIMPSESTBCDFGHJKNOQRUVWXYZ"[:26]),
    ("ABSCISSA", "ABSCISDEFGHJKLMNOPQRTUVWXYZ"[:26]),
    ("BERLIN", "BERLINACDFGHJKMOPQSTUVWXYZ"[:26]),
]

print("Testing different tableau alphabets with key ELYOIECBAQK...")
for name, alpha in alt_alphabets:
    if len(set(alpha)) != 26:
        continue
    try:
        pt = vigenere_decrypt(K4, "ELYOIECBAQK", alpha)
        words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST'] if w in pt]
        if words:
            print(f"{name}: Found {words}")
            print(f"  PT: {pt[:60]}...")
    except:
        pass

# ============================================================
# ATTACK 8: XOR with ASCII
# ============================================================
print("\n" + "="*70)
print("ATTACK 8: XOR OPERATIONS")
print("="*70)

def xor_decrypt(ct, key):
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        xored = chr((ord(c) ^ ord(k)) % 26 + 65)
        result.append(xored)
    return ''.join(result)

print("Testing XOR with various keys...")
xor_keys = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'ELYOIECBAQK']
for key in xor_keys:
    pt = xor_decrypt(K4, key)
    words = [w for w in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'THE'] if w in pt]
    if words:
        print(f"XOR key {key}: {words}")
        print(f"  PT: {pt}")

print("\n" + "="*70)
print("CREATIVE ATTACKS COMPLETE")
print("="*70)
