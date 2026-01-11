#!/usr/bin/env python3
"""
Check if gibberish sections need additional Vigenere decryption
"""

SECTIONS = {
    "Sec1": "QAPBZDBKZEL",
    "Sec2": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH",
    "Sec3": "RSPVJWQUL",
    "Sec4": "ZOLRKCAYF",
}

def vigenere_decrypt(ciphertext, key):
    """Decrypt Vigenere cipher"""
    result = []
    key_upper = key.upper()
    for i, c in enumerate(ciphertext.upper()):
        if c.isalpha():
            shift = ord(key_upper[i % len(key_upper)]) - ord('A')
            decrypted = chr((ord(c) - ord('A') - shift) % 26 + ord('A'))
            result.append(decrypted)
        else:
            result.append(c)
    return ''.join(result)

def score_text(text):
    """Simple English scoring"""
    common = "ETAOINSHRDLU"
    score = sum(1 for c in text if c in common)
    # Bonus for common bigrams
    bigrams = ["TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND"]
    for bg in bigrams:
        if bg in text:
            score += 3
    return score

def try_common_keys(text, name):
    """Try common K4-related keys"""
    keys = [
        "KRYPTOS", "SANBORN", "BERLIN", "CLOCK", "SHADOW", "LAYER",
        "UNDER", "ABOVE", "PALIMPSEST", "ABSCISSA", "NORTHEAST",
        "LANGLEY", "CIA", "K", "K4", "KEY", "CODE", "TIME",
        "A", "B", "C", "D", "E", "Z", "FOUR", "EAST", "WEST"
    ]

    print(f"\n{name}: {text}")
    print("-" * 40)

    results = []
    for key in keys:
        decrypted = vigenere_decrypt(text, key)
        score = score_text(decrypted)
        results.append((score, key, decrypted))

    results.sort(reverse=True)
    print("Top 10 Vigenere decryptions:")
    for score, key, dec in results[:10]:
        print(f"  Key={key:15s} -> {dec} (score: {score})")

def brute_force_short_keys(text, name, max_len=3):
    """Try all short keys"""
    from itertools import product
    import string

    print(f"\n{name}: Brute force keys 1-{max_len} chars")
    print("-" * 40)

    best = []
    for key_len in range(1, max_len + 1):
        for key_tuple in product(string.ascii_uppercase, repeat=key_len):
            key = ''.join(key_tuple)
            decrypted = vigenere_decrypt(text, key)
            score = score_text(decrypted)
            if score > 5:  # Only keep high scorers
                best.append((score, key, decrypted))

    best.sort(reverse=True)
    if best:
        print("Top 10 by score:")
        for score, key, dec in best[:10]:
            print(f"  Key={key:5s} -> {dec} (score: {score})")
    else:
        print("  No high-scoring results")

def check_letter_patterns(text, name):
    """Check for interesting letter patterns"""
    print(f"\n{name}: Pattern analysis")
    print("-" * 40)

    # Every other letter
    even = text[0::2]
    odd = text[1::2]
    print(f"  Even positions: {even}")
    print(f"  Odd positions:  {odd}")

    # Every 3rd
    for start in range(3):
        every3 = text[start::3]
        print(f"  Every 3rd from {start}: {every3}")

    # Check for repeated patterns
    n = len(text)
    for period in range(2, n//2):
        if all(text[i] == text[i % period] if i + period < n and text[i] == text[i + period] else False
               for i in range(n - period)):
            print(f"  Periodic with period {period}")

def main():
    print("=" * 60)
    print("VIGENERE ANALYSIS OF GIBBERISH SECTIONS")
    print("=" * 60)

    for name, text in SECTIONS.items():
        try_common_keys(text, name)

    print("\n" + "=" * 60)
    print("SHORT KEY BRUTE FORCE")
    print("=" * 60)

    for name, text in SECTIONS.items():
        brute_force_short_keys(text, name, max_len=2)

    print("\n" + "=" * 60)
    print("LETTER PATTERN ANALYSIS")
    print("=" * 60)

    for name, text in SECTIONS.items():
        check_letter_patterns(text, name)

if __name__ == "__main__":
    main()
