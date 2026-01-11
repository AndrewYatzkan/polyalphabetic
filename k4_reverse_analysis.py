#!/usr/bin/env python3
"""
Reverse engineering analysis for K4.
Working backwards from known crib positions to identify possible cipher types.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known cribs
# Position 63-73: NYPVTTMZFPK -> BERLINCLOCK
# NORTHEAST appears somewhere

# Let's analyze the transformation from CT to PT at known positions
def analyze_transformation():
    """Analyze the CT->PT transformation at known positions"""
    print("=" * 70)
    print("REVERSE ANALYSIS OF KNOWN TRANSFORMATIONS")
    print("=" * 70)

    # Positions 63-73 (0-indexed)
    ct_berlin = K4[63:74]  # NYPVTTMZFPK
    pt_berlin = "BERLINCLOCK"

    print(f"\nBERLINCLOCK transformation (positions 63-73):")
    print(f"Ciphertext:  {ct_berlin}")
    print(f"Plaintext:   {pt_berlin}")
    print()

    # Calculate various transformations
    print("Position-by-position analysis:")
    print("-" * 50)
    print(f"{'Pos':>4} {'CT':>3} {'PT':>3} {'CT-PT':>6} {'PT-CT':>6} {'CT*':>4} {'Polybius?'}")
    print("-" * 50)

    for i, (c, p) in enumerate(zip(ct_berlin, pt_berlin)):
        ct_val = ord(c) - ord('A')
        pt_val = ord(p) - ord('A')
        diff_ct_pt = (ct_val - pt_val) % 26
        diff_pt_ct = (pt_val - ct_val) % 26

        # Polybius coordinates
        ct_row, ct_col = ct_val // 5, ct_val % 5
        pt_row, pt_col = pt_val // 5, pt_val % 5

        print(f"{63+i:>4} {c:>3} {p:>3} {diff_ct_pt:>6} {diff_pt_ct:>6} {ct_val:>4} {ct_row},{ct_col} -> {pt_row},{pt_col}")

    # Check for Vigenere-like key
    print("\n\nVigenere key extraction:")
    print("-" * 50)
    key_letters = []
    for c, p in zip(ct_berlin, pt_berlin):
        ct_val = ord(c) - ord('A')
        pt_val = ord(p) - ord('A')
        # For standard Vigenere: CT = PT + KEY, so KEY = CT - PT
        key_val = (ct_val - pt_val) % 26
        key_letters.append(chr(key_val + ord('A')))

    key = ''.join(key_letters)
    print(f"Standard Vigenere key: {key}")

    # Check for KRYPTOS alphabet Vigenere
    kryptos_alpha = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    print("\n\nKRYPTOS alphabet Vigenere key extraction:")
    print("-" * 50)
    key_letters_kryptos = []
    for c, p in zip(ct_berlin, pt_berlin):
        ct_pos = kryptos_alpha.find(c)
        pt_pos = kryptos_alpha.find(p)
        if ct_pos >= 0 and pt_pos >= 0:
            # KEY = CT - PT in KRYPTOS alphabet
            key_pos = (ct_pos - pt_pos) % 26
            key_letters_kryptos.append(kryptos_alpha[key_pos])

    key_kryptos = ''.join(key_letters_kryptos)
    print(f"KRYPTOS alphabet key: {key_kryptos}")


def test_polybius_transformations():
    """Test if Polybius-based transformations could work"""
    print("\n" + "=" * 70)
    print("POLYBIUS TRANSFORMATION ANALYSIS")
    print("=" * 70)

    def create_polybius(keyword: str = ""):
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        keyword = keyword.upper().replace("J", "I")

        seen = set()
        chars = []
        for c in keyword + alphabet:
            if c in alphabet and c not in seen:
                chars.append(c)
                seen.add(c)

        c2c = {}
        c2ch = {}
        for i, c in enumerate(chars):
            r, col = i // 5, i % 5
            c2c[c] = (r, col)
            c2ch[(r, col)] = c

        return c2c, c2ch

    keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"]

    ct_berlin = K4[63:74].replace("J", "I")
    pt_berlin = "BERLINCLOCK".replace("J", "I")

    for keyword in keywords:
        c2c, c2ch = create_polybius(keyword)

        print(f"\n\nKeyword: {keyword}")
        print("-" * 40)

        # Get coordinates for each pair
        print("Coordinate analysis:")
        for i, (c, p) in enumerate(zip(ct_berlin, pt_berlin)):
            if c in c2c and p in c2c:
                ct_r, ct_c = c2c[c]
                pt_r, pt_c = c2c[p]
                print(f"  {c}->{p}: ({ct_r},{ct_c})->({pt_r},{pt_c}) diff: ({(ct_r-pt_r)%5},{(ct_c-pt_c)%5})")


def test_digraph_ciphers():
    """Test if digraph transformations could work"""
    print("\n" + "=" * 70)
    print("DIGRAPH CIPHER ANALYSIS")
    print("=" * 70)

    ct_berlin = K4[63:74]
    pt_berlin = "BERLINCLOCK"

    print("\nDigraph pairs (CT -> PT):")
    print("-" * 40)

    # Split into pairs
    for i in range(0, 10, 2):
        ct_pair = ct_berlin[i:i+2] if i+1 < len(ct_berlin) else ct_berlin[i]
        pt_pair = pt_berlin[i:i+2] if i+1 < len(pt_berlin) else pt_berlin[i]
        print(f"  {ct_pair} -> {pt_pair}")

    # Check for Playfair-like transformation
    print("\nPlayfair analysis:")
    print("-" * 40)

    def create_polybius(keyword: str = ""):
        alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
        keyword = keyword.upper().replace("J", "I")

        seen = set()
        chars = []
        for c in keyword + alphabet:
            if c in alphabet and c not in seen:
                chars.append(c)
                seen.add(c)

        c2c = {}
        c2ch = {}
        for i, c in enumerate(chars):
            r, col = i // 5, i % 5
            c2c[c] = (r, col)
            c2ch[(r, col)] = c

        return c2c, c2ch

    keywords = ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]

    for keyword in keywords:
        c2c, c2ch = create_polybius(keyword)

        print(f"\n  Keyword: {keyword}")
        for i in range(0, 10, 2):
            c1, c2 = ct_berlin[i].replace("J", "I"), ct_berlin[i+1].replace("J", "I") if i+1 < len(ct_berlin) else "X"
            p1, p2 = pt_berlin[i].replace("J", "I"), pt_berlin[i+1].replace("J", "I") if i+1 < len(pt_berlin) else "X"

            if c1 in c2c and c2 in c2c and p1 in c2c and p2 in c2c:
                cr1, cc1 = c2c[c1]
                cr2, cc2 = c2c[c2]
                pr1, pc1 = c2c[p1]
                pr2, pc2 = c2c[p2]

                # Check Playfair rules
                same_row = cr1 == cr2 and pr1 == pr2
                same_col = cc1 == cc2 and pc1 == pc2
                rectangle = cr1 != cr2 and cc1 != cc2

                print(f"    {c1}{c2}->{p1}{p2}: CT({cr1},{cc1})({cr2},{cc2}) PT({pr1},{pc1})({pr2},{pc2}) ", end="")
                if same_row:
                    print("same_row", end="")
                elif same_col:
                    print("same_col", end="")
                elif rectangle:
                    print("rectangle", end="")
                print()


def find_northeast_positions():
    """Try to find where NORTHEAST might decrypt from"""
    print("\n" + "=" * 70)
    print("SEARCHING FOR NORTHEAST POSITIONS")
    print("=" * 70)

    # If we use a Vigenere-like cipher, what CT positions could give NORTHEAST?
    northeast = "NORTHEAST"

    print("\nFor standard Vigenere, CT positions that could give NORTHEAST:")
    print("-" * 50)

    for start_pos in range(len(K4) - len(northeast) + 1):
        ct_segment = K4[start_pos:start_pos + len(northeast)]

        # Calculate required key
        key_vals = []
        for c, p in zip(ct_segment, northeast):
            ct_val = ord(c) - ord('A')
            pt_val = ord(p) - ord('A')
            key_val = (ct_val - pt_val) % 26
            key_vals.append(key_val)

        # Check if key has interesting pattern
        key_str = ''.join(chr(v + ord('A')) for v in key_vals)

        # Check for repeated patterns
        has_pattern = False
        for period in [3, 4, 5, 6, 7, 8, 9]:
            if len(key_str) >= period:
                if key_str[:period] in key_str[period:]:
                    has_pattern = True
                    break

        # Check if key forms a word
        known_words = ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW"]
        for word in known_words:
            if key_str in word or word in key_str:
                print(f"  Position {start_pos}: CT={ct_segment} Key={key_str} (contains/in {word})")
                break

        # Also check if same key works for BERLINCLOCK at 63
        if len(key_str) >= 11:
            berlinclock_key = ""
            for i, (c, p) in enumerate(zip(K4[63:74], "BERLINCLOCK")):
                ct_val = ord(c) - ord('A')
                pt_val = ord(p) - ord('A')
                key_val = (ct_val - pt_val) % 26
                berlinclock_key += chr(key_val + ord('A'))

            # Check if keys are related
            if key_str[:11] == berlinclock_key or berlinclock_key[:len(key_str)] == key_str:
                print(f"  Position {start_pos}: MATCH with BERLINCLOCK key!")
                print(f"    CT={ct_segment} Key={key_str}")
                print(f"    BERLINCLOCK key: {berlinclock_key}")


def analyze_periodic_keys():
    """Analyze if any periodic key works for both cribs"""
    print("\n" + "=" * 70)
    print("PERIODIC KEY COMPATIBILITY ANALYSIS")
    print("=" * 70)

    # BERLINCLOCK at position 63
    berlinclock_key = []
    for c, p in zip(K4[63:74], "BERLINCLOCK"):
        ct_val = ord(c) - ord('A')
        pt_val = ord(p) - ord('A')
        key_val = (ct_val - pt_val) % 26
        berlinclock_key.append(key_val)

    print(f"\nBERLINCLOCK key values: {berlinclock_key}")
    print(f"Key letters: {''.join(chr(v + ord('A')) for v in berlinclock_key)}")

    # For each possible NORTHEAST position, calculate required key values
    northeast = "NORTHEAST"

    print(f"\nChecking NORTHEAST at each position for period compatibility:")
    print("-" * 60)

    for start_pos in range(len(K4) - len(northeast) + 1):
        ct_segment = K4[start_pos:start_pos + len(northeast)]

        ne_key = []
        for c, p in zip(ct_segment, northeast):
            ct_val = ord(c) - ord('A')
            pt_val = ord(p) - ord('A')
            key_val = (ct_val - pt_val) % 26
            ne_key.append(key_val)

        # Check if any period makes both keys compatible
        for period in range(5, 30):
            compatible = True

            # Check each position in BERLINCLOCK
            for i, kv in enumerate(berlinclock_key):
                pos_in_key = (63 + i) % period
                # Check if same position in NORTHEAST key matches
                for j, nkv in enumerate(ne_key):
                    ne_pos_in_key = (start_pos + j) % period
                    if pos_in_key == ne_pos_in_key and kv != nkv:
                        compatible = False
                        break
                if not compatible:
                    break

            if compatible:
                print(f"  Period {period} compatible: NORTHEAST at {start_pos}")

                # Build complete key
                key = [None] * period
                for i, kv in enumerate(berlinclock_key):
                    pos = (63 + i) % period
                    key[pos] = kv
                for j, nkv in enumerate(ne_key):
                    pos = (start_pos + j) % period
                    if key[pos] is None:
                        key[pos] = nkv

                # Fill remaining with ?
                key_str = ''.join(chr(v + ord('A')) if v is not None else '?' for v in key)
                print(f"    Key: {key_str}")


def main():
    analyze_transformation()
    test_polybius_transformations()
    test_digraph_ciphers()
    find_northeast_positions()
    analyze_periodic_keys()


if __name__ == "__main__":
    main()
