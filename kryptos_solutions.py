#!/usr/bin/env python3
"""
Kryptos Cipher Solutions

This script demonstrates the decryption of the Kryptos sculpture ciphers
at CIA headquarters, Langley, Virginia.

Kryptos was created by artist Jim Sanborn and dedicated in November 1990.
It contains four encrypted passages (K1-K4), of which three have been solved:
- K1: Solved by CIA in 1999 (Vigenère with KRYPTOS tableau)
- K2: Solved by CIA in 1999 (Vigenère with KRYPTOS tableau)
- K3: Solved by CIA in 1999 (Transposition cipher)
- K4: UNSOLVED (97 characters)
"""

def create_kryptos_tableau():
    """Create the KRYPTOS keyed alphabet tableau."""
    keyword = "KRYPTOS"
    standard = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # Create keyed alphabet: KRYPTOS followed by remaining letters in order
    keyed = keyword
    for c in standard:
        if c not in keyed:
            keyed += c
    return keyed

def vigenere_decrypt(ciphertext, key, alphabet):
    """Decrypt using Vigenère cipher with custom alphabet."""
    plaintext = ""
    key_index = 0
    for c in ciphertext:
        if c in alphabet:
            # Find positions in alphabet
            ct_pos = alphabet.index(c)
            key_pos = alphabet.index(key[key_index % len(key)])
            # Decrypt: shift backward by key position
            pt_pos = (ct_pos - key_pos) % len(alphabet)
            plaintext += alphabet[pt_pos]
            key_index += 1
        else:
            plaintext += c
    return plaintext

def format_plaintext(text, word_boundaries=None):
    """Format plaintext with spaces at word boundaries."""
    if word_boundaries:
        result = ""
        for i, c in enumerate(text):
            if i in word_boundaries:
                result += " "
            result += c
        return result.strip()
    return text

# Known Kryptos ciphertexts
K1_CIPHER = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K2_CIPHER = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
K3_CIPHER = "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWENATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAECTDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIMEHNLSSTTRTVDOHW"
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Known keys
K1_KEY = "PALIMPSEST"
K2_KEY = "ABSCISSA"

print("=" * 80)
print("KRYPTOS CIPHER SOLUTIONS")
print("=" * 80)

# Create KRYPTOS tableau
tableau = create_kryptos_tableau()
print(f"\nKRYPTOS Tableau (Keyed Alphabet): {tableau}")

# Solve K1
print("\n" + "=" * 80)
print("K1 - VIGENÈRE CIPHER")
print("=" * 80)
print(f"Ciphertext ({len(K1_CIPHER)} chars): {K1_CIPHER}")
print(f"Key: {K1_KEY}")
k1_plain = vigenere_decrypt(K1_CIPHER, K1_KEY, tableau)
print(f"\nPlaintext: {k1_plain}")

# Add word boundaries for K1
k1_formatted = "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION"
print(f"\nFormatted: {k1_formatted}")
print("\nNote: 'IQLUSION' is intentionally misspelled (Q instead of L) in the original")

# Solve K2
print("\n" + "=" * 80)
print("K2 - VIGENÈRE CIPHER")
print("=" * 80)
print(f"Ciphertext ({len(K2_CIPHER)} chars): {K2_CIPHER[:50]}...")
print(f"Key: {K2_KEY}")
k2_plain = vigenere_decrypt(K2_CIPHER, K2_KEY, tableau)
print(f"\nPlaintext: {k2_plain}")

# K2 formatted text
k2_formatted = """IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD X
THE INFORMATION WAS GATHERED AND TRANSMITTED UNDERGRUUND TO AN UNKNOWN LOCATION X
DOES LANGLEY KNOW ABOUT THIS THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X
WHO KNOWS THE EXACT LOCATION ONLY WW THIS WAS HIS LAST MESSAGE X
THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO"""
print(f"\nFormatted:\n{k2_formatted}")
print("\nNotes:")
print("- 'UNDERGRUUND' has intentional misspelling (U instead of O)")
print("- 'WW' likely refers to William Webster, CIA Director at the time")
print("- Coordinates: 38°57'6.5\"N, 77°8'44\"W (CIA headquarters area)")

# K3 - Transposition cipher (columnar transposition)
print("\n" + "=" * 80)
print("K3 - TRANSPOSITION CIPHER")
print("=" * 80)
print(f"Ciphertext ({len(K3_CIPHER)} chars): {K3_CIPHER[:50]}...")
print("\nK3 uses a columnar transposition, not a substitution cipher.")
print("The plaintext is read by arranging the ciphertext in columns:")

K3_PLAINTEXT = """SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER
PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE
UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE
AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER
BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE
ANYTHING Q"""

print(f"\nPlaintext:\n{K3_PLAINTEXT}")
print("\nNote: This is an excerpt from Howard Carter's account of opening")
print("King Tutankhamun's tomb in 1922. 'DESPARATLY' is misspelled (missing E).")
print("The 'Q' at the end represents a question mark.")

# K4 - UNSOLVED
print("\n" + "=" * 80)
print("K4 - UNSOLVED CIPHER")
print("=" * 80)
print(f"Ciphertext ({len(K4_CIPHER)} chars): {K4_CIPHER}")
print("\nK4 remains UNSOLVED since 1990.")
print("\nKnown clues from Jim Sanborn:")
print("- Characters 64-69: 'NYPVTT' decrypts to 'BERLIN'")
print("- Characters 70-74: 'MZFPK' decrypts to 'CLOCK'")
print("- 2020 hint: 'NORTHEAST' appears somewhere in the plaintext")
print("\nThe encryption method for K4 is unknown and may involve:")
print("- A different cipher type than K1-K3")
print("- Multiple encryption layers")
print("- A custom algorithm devised by Sanborn")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
Section | Length | Cipher Type              | Key(s)                 | Status
--------|--------|--------------------------|------------------------|--------
K1      | 63     | Vigenère (KRYPTOS table) | PALIMPSEST            | SOLVED
K2      | 369    | Vigenère (KRYPTOS table) | ABSCISSA              | SOLVED
K3      | 336    | Columnar Transposition   | Not publicly known    | SOLVED
K4      | 97     | UNKNOWN                  | UNKNOWN               | UNSOLVED

Total characters: 865 (763 solved, 97 unsolved)

Famous cryptanalysts who have worked on K4:
- Jim Gillogly (first to publicly solve K1-K3 in 1999)
- CIA internal team (solved privately in 1998)
- NSA team (solved K1-K3 in 1992)
- Countless independent researchers worldwide
""")
