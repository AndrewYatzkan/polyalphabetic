import re

STEP49_TRANSPOSED = "OABTKJRKULOUXDOIGAHWUILNBFSBONLYIPFVBTBTWMFZLFRPVKQWQGPDRKNZGXKTSJSCODTIWGTKQUSHJUQASUSEEKKCZAZRW"
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

print("=" * 80)
print("DIRECT ANALYSIS OF STEP49_TRANSPOSED")
print("=" * 80)

print(f"\nText: {STEP49_TRANSPOSED}")
print(f"Length: {len(STEP49_TRANSPOSED)}")

# The text contains ONLY, USE, SEE - let's extract sections
print("\n" + "=" * 80)
print("EXTRACTING SECTIONS WITH KNOWN WORDS")
print("=" * 80)

words_of_interest = ["ONLY", "USE", "SEE"]

for word in words_of_interest:
    pos = STEP49_TRANSPOSED.find(word)
    if pos >= 0:
        start = max(0, pos - 10)
        end = min(len(STEP49_TRANSPOSED), pos + len(word) + 10)
        context = STEP49_TRANSPOSED[start:end]
        print(f"\n'{word}' at position {pos}:")
        print(f"  Context: ...{context}...")

# The user said "This contains ONLY, USE, SEE"
# Maybe these are clues and we should look at what's around them?

print("\n" + "=" * 80)
print("INTERPRETATION: STEP49 might already be plaintext")
print("=" * 80)

print(f"""
Hypothesis: STEP49_TRANSPOSED is the result of:
  1. Applying cyclic shift (or rotation) by 49
  2. Maybe combined with some other operation

The fact that it contains readable English words (ONLY, USE, SEE) 
suggests it might already be decrypted or at least partially readable.

Let's try different interpretations of "cyclic shift step 49":
""")

# Maybe "step 49" is a rotation/shift of 49 positions?
print("\n1. ROT-49 (cyclic shift by 49):")
print("   (Though this is same as ROT-13 or ROT-3 depending on modulo)")

for shift in [49, 49 % 26]:
    shifted = ""
    for char in K4_CIPHER:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted += chr((ord(char) - base + shift) % 26 + base)
        else:
            shifted += char
    
    print(f"\n   Shift {shift}: {shifted}")
    
    # Check if this matches STEP49
    if shifted == STEP49_TRANSPOSED:
        print("   ✓ MATCHES STEP49_TRANSPOSED!")

# Maybe it's reading every 49th character?
print("\n2. EVERY 49TH CHARACTER from K4:")
every_49th = K4_CIPHER[::49]
print(f"   Result: {every_49th}")

# Maybe it's reading backwards with some interval?
print("\n3. REVERSE + every Nth:")
reversed_k4 = K4_CIPHER[::-1]
print(f"   Reversed K4: {reversed_k4}")

# Check if there's a pattern with reading columns
# Maybe it's from a columnar transposition with 49?
print("\n4. COLUMNAR TRANSPOSITION TEST:")
print("   If STEP49 is result of columnar transposition with 49 columns")
print("   But K4 is only 97 chars, so max ~2 rows")

# Let me check actual pattern
# 97 / 49 = 1.98 - so we could have ~2 rows of ~49 chars each

rows = (len(K4_CIPHER) + 48) // 49  # Round up
cols = 49

print(f"\n   Grid dimensions: {rows} rows × {cols} columns")
print(f"   Total cells needed: {rows * cols}")

# Try building K4 as a grid and reading differently
grid = [['' for _ in range(cols)] for _ in range(rows)]

# Fill grid row by row
idx = 0
for r in range(rows):
    for c in range(cols):
        if idx < len(K4_CIPHER):
            grid[r][c] = K4_CIPHER[idx]
            idx += 1

print(f"\n   K4 as grid (first few rows/cols):")
for r in range(min(3, rows)):
    row_str = ''.join(grid[r][:20])
    print(f"   Row {r}: {row_str}...")

# Read column by column
cols_read = ""
for c in range(cols):
    for r in range(rows):
        if grid[r][c]:
            cols_read += grid[r][c]

print(f"\n   Reading columns: {cols_read[:60]}...")

# Check if column reading gives us STEP49
if cols_read == STEP49_TRANSPOSED:
    print("\n   ✓✓✓ MATCH! Reading K4 as grid and then reading columns gives STEP49!")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print(f"""
The STEP49_TRANSPOSED text:
- Contains English words: ONLY, USE, SEE
- Is an anagram of K4_CIPHER (same characters, different order)
- Might be the result of columnar transposition with 49 columns

Next steps:
1. Verify the transposition method
2. Try Vigenere decryption on already-readable sections
3. Look for complete English sentences between the known words
""")

