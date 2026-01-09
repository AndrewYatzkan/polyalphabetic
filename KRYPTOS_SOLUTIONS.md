# Kryptos Cipher Solutions

This document demonstrates solving the Kryptos sculpture ciphers using the polyalphabetic cipher solver in this repository.

## Background

**Kryptos** is an encrypted sculpture created by artist Jim Sanborn, dedicated on November 3, 1990, on the grounds of CIA headquarters in Langley, Virginia. The sculpture contains four encrypted passages (K1-K4), of which three have been publicly solved.

## Results Summary

| Section | Length | Cipher Type | Key(s) | Status | Solver Time |
|---------|--------|-------------|--------|--------|-------------|
| K1 | 63 | Vigenère (KRYPTOS tableau) | PALIMPSEST | **SOLVED** | N/A (known) |
| K2 | 369 | Quagmire III | KRYPTOS / ABSCISSA | **SOLVED** | ~2 seconds |
| K3 | 336 | Columnar Transposition | (not polyalphabetic) | **SOLVED** | N/A |
| K4 | 97 | **UNKNOWN** | **UNKNOWN** | **UNSOLVED** | - |

---

## K1 - Vigenère Cipher with KRYPTOS Tableau

### Ciphertext (63 characters)
```
EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD
```

### Key
- **Keyed Alphabet**: `KRYPTOSABCDEFGHIJLMNQUVWXZ` (KRYPTOS followed by remaining letters)
- **Keyword**: `PALIMPSEST`

### Plaintext
```
BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF IQLUSION
```

**Note**: "IQLUSION" is intentionally misspelled (Q instead of L) in Sanborn's original design.

---

## K2 - Quagmire III Cipher

### Ciphertext (369 characters)
```
VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQE
DAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLS
ZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFK
ZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQ
XEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG
```

### Solver Command
```bash
./polyalphabetic -type 3 -cipher ciphers/kryptos/K2.txt -ngramsize 4 \
  -ngramfile english_quadgrams.txt -nhillclimbs 1000 -nrestarts 1000 \
  -backtrackprob 0.15 -slipprob 0.0005 -plaintextkeywordlen 7 -cyclewordlen 8 -verbose
```

### Results
- **Keyed Alphabet**: `KRYPTOSABCDEFGHIJLMNQUVWXZ`
- **Cycleword**: `ABSCISSA`
- **Solve Time**: ~2.16 seconds
- **Score**: 3.18

### Plaintext
```
IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD X
THE INFORMATION WAS GATHERED AND TRANSMITTED UNDERGRUUND TO AN UNKNOWN LOCATION X
DOES LANGLEY KNOW ABOUT THIS THEY SHOULD ITS BURIED OUT THERE SOMEWHERE X
WHO KNOWS THE EXACT LOCATION ONLY WW THIS WAS HIS LAST MESSAGE X
THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST X LAYER TWO
```

**Notes**:
- "UNDERGRUUND" is intentionally misspelled (U instead of O)
- "WW" likely refers to William Webster, CIA Director at the time of the sculpture's installation
- Coordinates (38°57'6.5"N, 77°8'44"W) point to a location near CIA headquarters

---

## K3 - Columnar Transposition Cipher

K3 uses a **columnar transposition cipher**, not a substitution cipher, so the polyalphabetic solver is not applicable. The ciphertext is rearranged by reading columns in a specific order.

### Ciphertext (336 characters)
```
ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNETPRNGATIHNRAR
PESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLSEDTIWENHAEIOYTEYQHEENC
TAYCREIFTBRSPAMHHEWENATAMATEGYEERLBTEEFOASFIOTUETUAEOTOARMAEERTNRTIBSEDDNIA
AHTTMSTEWPIEROAGRIEWFEBAECTDDHILCEIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEO
HMGFMFEUHEECDMRIPFEIMEHNLSSTTRTVDOHW
```

### Plaintext
This is an excerpt from Howard Carter's account of discovering King Tutankhamun's tomb in 1922:

```
SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER
PART OF THE DOORWAY WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE
UPPER LEFT HAND CORNER AND THEN WIDENING THE HOLE A LITTLE I INSERTED THE CANDLE
AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE FLAME TO FLICKER
BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE
ANYTHING Q
```

**Note**: "DESPARATLY" is misspelled (missing E). The "Q" represents a question mark.

---

## K4 - UNSOLVED

### Ciphertext (97 characters)
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

### Known Clues (from Jim Sanborn)
1. **2010**: Characters 64-69 (`NYPVTT`) decrypt to `BERLIN`
2. **2010**: Characters 70-74 (`MZFPK`) decrypt to `CLOCK`
3. **2020**: `NORTHEAST` appears somewhere in the plaintext

### Attempted Solver Results
The polyalphabetic solver was unable to crack K4 using:
- Vigenère cipher (type 0)
- Quagmire I-IV ciphers (types 1-4)
- Beaufort cipher (type 5)
- Porta cipher (type 6)
- Autokey cipher (type 7)

All attempts produced gibberish, suggesting K4 uses:
- A different cipher type entirely
- Multiple encryption layers
- A custom algorithm devised by Sanborn
- Modified parameters not captured by standard methods

### K4 Theories
Various cryptanalysts have proposed:
- Masking (XOR or similar operations)
- Keyed route transposition
- Homophonic substitution
- Clock-based cipher (relating to the Berlin Clock hint)
- Double encryption

---

## Model Cipher (cipher.txt)

The repository includes a test cipher (`cipher.txt`) that uses K3-related content as a demonstration.

### Ciphertext (97 characters)
```
MFABBMNNQEYEZIAIABLJJEFXNWJOTNPVDIBHQNNSIMRJPZIXOEJXROJVTNPFILBBJNSNTGLDRISJZWQCSDVIFKNNMVOIXTQOP
```

### Crib
```
_____________________EASTNORTHEAST_____________________________BERLINCLOCK_______________________
```

### Solver Command
```bash
./polyalphabetic -type 3 -cipher cipher.txt -crib crib.txt -ngramsize 4 \
  -ngramfile english_quadgrams.txt -nhillclimbs 2500 -nrestarts 5000 \
  -backtrackprob 0.15 -slipprob 0.0005 -plaintextkeywordlen 7 -cyclewordlen 7 -verbose
```

### Results
- **Keyed Alphabet**: `KRYPTOSABCDEFGHIJLMNQUVWXZ`
- **Cycleword**: `KOMITET`
- **Solve Time**: ~0.62 seconds

### Plaintext
```
MAINTAINING A HEADING OF EAST NORTHEAST THIRTY THREE DEGREES FROM THE WEST BERLIN CLOCK
YOU WILL SEE FURTHER INFORM
```

---

## Historical Notes

- **1990**: Kryptos dedicated at CIA headquarters
- **1992**: NSA team reportedly solves K1-K3 internally
- **1998**: CIA analyst David Stein solves K1-K3 (classified until 2000)
- **1999**: Jim Gillogly becomes first to publicly solve K1-K3
- **2010**: Sanborn releases BERLIN and CLOCK clues for K4
- **2020**: Sanborn releases NORTHEAST clue for K4
- **Present**: K4 remains unsolved after 35+ years

---

## References

- [Kryptos Wikipedia](https://en.wikipedia.org/wiki/Kryptos)
- [Jim Gillogly's original paper](https://groups.google.com/g/sci.crypt/c/hOCNN6L13CM/m/s85aEvsmrl0J)
- [Elonka Dunin's Kryptos page](https://www.elonka.com/kryptos/)
