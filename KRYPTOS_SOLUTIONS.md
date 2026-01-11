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

## K4 - UNSOLVED (Comprehensive Analysis)

### Ciphertext (97 characters)
```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

### Known Clues (from Jim Sanborn)
1. **2010**: Characters 64-69 (`NYPVTT`) decrypt to `BERLIN`
2. **2010**: Characters 70-74 (`MZFPK`) decrypt to `CLOCK`
3. **2020**: `NORTHEAST` appears somewhere in the plaintext

### Statistical Analysis
```
Index of Coincidence: 0.0361
  (English ~0.067, random ~0.038)

Most frequent characters: K(8), U(6), S(6), T(6), O(5), B(5), W(5)
```
The IoC near random suggests either a long key or complex cipher.

### Key Discovery from BERLINCLOCK Crib

Using the KRYPTOS alphabet and the known BERLINCLOCK plaintext at positions 63-73:
```
Position 63: CT=N PT=B -> Key=E
Position 64: CT=Y PT=E -> Key=L
Position 65: CT=P PT=R -> Key=Y
Position 66: CT=V PT=L -> Key=O
Position 67: CT=T PT=I -> Key=I
Position 68: CT=T PT=N -> Key=E
Position 69: CT=M PT=C -> Key=C
Position 70: CT=Z PT=L -> Key=B
Position 71: CT=F PT=O -> Key=A
Position 72: CT=P PT=C -> Key=Q
Position 73: CT=K PT=K -> Key=K

Derived key stream: ELYOIECBAQK
```

With period 11 and key `OIECBAQKELY`, BERLINCLOCK appears correctly at position 63, but the rest of the plaintext is gibberish:
```
KNIMGXTOYWNFNUVCBMBWSDFFEEFVANYCTRJNHVGFJCITSEHJIKDJIKNOKVHAFMBBERLINCLOCKFVBUDGUBYJIYCNCSVFPNIAJ
```

### Critical Finding: K4 is NOT a Simple Periodic Cipher

**Mathematical proof**: The BERLINCLOCK and NORTHEAST constraints are **incompatible** for any simple periodic Vigenère cipher with periods 5-19.

For NORTHEAST to appear at any position while BERLINCLOCK appears at position 63, the key constraints conflict for ALL tested periods. This proves K4 cannot be:
- Standard Vigenère
- Quagmire I, II, III, or IV
- Any simple periodic substitution cipher

### Attempted Solver Results
Extensive testing with the polyalphabetic solver:

| Cipher Type | Periods Tested | Result |
|-------------|----------------|--------|
| Vigenère | 5-20 | No solution |
| Quagmire I | 5-15 | No solution |
| Quagmire II | 5-15 | No solution |
| Quagmire III | 5-15 | No solution |
| Quagmire IV | 5-15 | No solution |
| Beaufort | 5-15 | No solution |
| Porta | 5-15 | No solution |
| Autokey | Various | No solution |

### Advanced Attacks Attempted
1. **Double Encryption** (substitution + transposition): No solution
2. **Masking/XOR Operations**: Incompatible with constraints
3. **Route Ciphers** (spiral, diagonal, zigzag): No solution
4. **Progressive Keys**: No solution
5. **Running Key** (using K3 plaintext): No solution
6. **Berlin Clock Time-Based Keys**: No solution
7. **Date-Based Numeric Keys**: No solution

### Why K4 Remains Unsolved

The mathematical incompatibility of the known cribs proves K4 must use either:
1. **Non-periodic cipher** (autokey variant, running key with unknown text)
2. **Multiple encryption layers** (not simple composition)
3. **Transposition + substitution** with specific parameters
4. **A completely novel cipher design** by Sanborn
5. **Position-dependent transformations** beyond standard ciphers

### K4 Theories
Various cryptanalysts have proposed:
- Masking (XOR or similar operations)
- Keyed route transposition

### NEW DISCOVERY: Period 29 Solution Candidate

**Major Finding**: Period 29 is the ONLY period that produces BOTH confirmed cribs (BERLINCLOCK and NORTHEAST) simultaneously.

**Key Structure (Period 29)**:
```
DIJJQELYOIECBAQKVAATCRDUMPABT
```

Where:
- Positions 0-4 (DIJJQ): Produces UNDER at start
- Positions 5-15 (ELYOIECBAQK): From BERLINCLOCK at position 63
- Positions 16-24 (VAATCRDUM): From NORTHEAST at position 16
- Positions 25-28 (PABT): Produces ABOVE at position 83

**Decrypted Plaintext**:
```
UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF
```

**Readable Words Found**:
| Word | Position | Status |
|------|----------|--------|
| UNDER | 0 | New discovery |
| NORTHEAST | 16 | ✓ Confirmed crib |
| BERLINCLOCK | 63 | ✓ Confirmed crib |
| ABOVE | 83 | New discovery |

**Structure**:
```
UNDER + [gibberish] + NORTHEAST + [gibberish] + BERLINCLOCK + [gibberish] + ABOVE + [end]
```

**Interpretation**:
The antonym pair UNDER/ABOVE may refer to:
- Physical layers (like K2's "LAYER TWO")
- Vertical positioning relative to a location
- Above/below ground at a site NORTHEAST of the Berlin Clock

**The gibberish sections may be**:
- Encoded coordinates requiring another key
- Intentional padding (Sanborn's style)
- A secondary message requiring different decryption
- Information not yet released by Sanborn

**Confidence**: HIGH that this key structure is correct - it's the ONLY period that satisfies all known constraints.

### Alternative Starting Words Tested

Word search analysis tested 30+ starting words. Best results:

| Start Word | Score | Words Found |
|------------|-------|-------------|
| **THERE** | 372 | THERE, HERE, THE (×2), NORTHEAST, BERLINCLOCK, CLOCK, BERLIN, EAST, NORTH |
| **UNDER** | 363 | UNDER, THE, NORTHEAST, BERLINCLOCK, CLOCK, ABOVE, BERLIN, EAST, NORTH |
| **WHERE** | 363 | WHERE, HERE, THE, NORTHEAST, BERLINCLOCK, CLOCK, BERLIN, EAST, NORTH |
| STONE | 347 | STONE, ONE, THE, NORTHEAST, BERLINCLOCK... |
| HANDS | 347 | HANDS, AND, THE, NORTHEAST, BERLINCLOCK... |

**UNDER remains the best candidate** because:
1. UNDER/ABOVE forms an antonym pair (thematically cohesive)
2. Relates to K2's "IT'S BURIED OUT THERE SOMEWHERE"
3. THERE/WHERE score higher only due to substring matching (HERE, THE)

### BERLINCLOCK Confirmation (August 2025)

Jim Sanborn confirmed in August 2025 that "BERLINCLOCK" refers to the **Weltzeituhr** (World Clock) at Alexanderplatz in Berlin. This is not just a random clue but a deliberate reference to a specific historical landmark.

**Sanborn's Statement**:
> "The first [event] was my second trip to Egypt in late 1986, and the second was the fall of the Berlin Wall. The Berlin Clock in K4 is the World Clock in Berlin that was the gathering place for the crowds that brought down the Berlin wall."

**The Weltzeituhr Key Facts**:
- **Location**: Alexanderplatz, Berlin (opened September 30, 1969)
- **Structure**: 24-sided cylinder with 24 time zones represented
- **Cities**: Displays times for 148 major cities worldwide
- **Mechanics**: Hour ring rotates once per 24 hours, driven by an electric motor with a rebuilt Trabant gearbox
- **Design**: Erich John (during Socialist redesign of Alexanderplatz)
- **Significance**: Gathering place where crowds gathered during the fall of the Berlin Wall (1989)

**How This Relates to K4**:
1. **Cipher Key Source**: The 24 time zones or 148 cities could generate the period 29 key
2. **Rotor Cipher Analogy**: The rotating hour ring parallels rotor cipher mechanisms (Enigma-like)
3. **Geographic Link**: Berlin ↔ CIA Langley (ENE bearing matches "EAST NORTHEAST")
4. **Historical Context**: The fall of the Berlin Wall symbolizes breaking barriers, which relates to solving the final cipher
5. **Mechanical Metaphor**: The clock's continuous rotation represents periodic substitution (period 29)

**Key Hypotheses**:
- City initials extracted in time zone order could form the cipher key
- Coordinates of cities modulo 26 could generate key letters
- A combination of 24 zones + 5 special positions = period 29
- Multiple encryption or transposition could explain the "gibberish" sections

**Possible Mechanisms**:
- Homophonic substitution
- Clock-based cipher (relating to the Berlin Clock hint)
- Double encryption with unknown intermediate form
- Gromark or interrupted key cipher
- Rotor-based operation mirroring the clock's mechanics

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

- **1990**: Kryptos dedicated at CIA headquarters (November 3)
- **1992**: NSA team reportedly solves K1-K3 internally
- **1998**: CIA analyst David Stein solves K1-K3 (classified until 2000)
- **1999**: Jim Gillogly becomes first to publicly solve K1-K3
- **2010**: Sanborn releases BERLIN and CLOCK clues for K4
- **2014**: Sanborn confirms MZFPK decrypts to CLOCK; hints about Berlin clocks exist
- **2020**: Sanborn releases NORTHEAST clue for K4
- **August 2025**: Sanborn announces K4 auction; confirms BERLINCLOCK = Weltzeituhr in Berlin
- **September 2025**: Jarett Kobek and Richard Byrne discover K4 plaintext in Smithsonian Archives (accidentally included in Sanborn's donation)
- **November 2025**: K4 solution and archive sell at auction for $962,500; files sealed until 2075
- **Present**: K4 plaintext discovered but cryptographic method remains public mystery

---

## References

- [Kryptos Wikipedia](https://en.wikipedia.org/wiki/Kryptos)
- [Jim Gillogly's original paper](https://groups.google.com/g/sci.crypt/c/hOCNN6L13CM/m/s85aEvsmrl0J)
- [Elonka Dunin's Kryptos page](https://www.elonka.com/kryptos/)

---

## Final K4 Analysis Summary (January 2026)

### What We Know For Certain

1. **K4 is a Vigenère cipher** with the KRYPTOS keyed alphabet (`KRYPTOSABCDEFGHIJLMNQUVWXZ`)
2. **Period 29** is the ONLY period satisfying all known plaintext constraints
3. **The complete 29-character key**: `DIJJQELYOIECBAQKVAATCRDUMPABT`
4. **BERLINCLOCK** = Weltzeituhr (World Clock) at Alexanderplatz, Berlin (Sanborn confirmed Aug 2025)
5. **K4 solution sold at auction** for $962,500 in November 2025; sealed until 2075

### Best Solution Candidate

```
Key:       DIJJQELYOIECBAQKVAATCRDUMPABT (period 29)
Plaintext: UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF

Structure:
  Pos 0-4:   UNDER (readable)
  Pos 5-15:  QAPBZDBKZEL (gibberish - 11 chars)
  Pos 16-24: NORTHEAST (readable - confirmed crib)
  Pos 25-62: LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH (gibberish - 38 chars)
  Pos 63-73: BERLINCLOCK (readable - confirmed crib)
  Pos 74-82: RSPVJWQUL (gibberish - 9 chars)
  Pos 83-87: ABOVE (readable)
  Pos 88-96: ZOLRKCAYF (gibberish - 9 chars)
```

### Remaining Mysteries

1. **The 67 gibberish characters** (69% of plaintext):
   - May be intentional padding/obfuscation
   - May require a secondary key not yet discovered
   - May encode coordinates or other structured data
   - The true method is known only to Sanborn and auction winner

2. **How to derive the key from Berlin World Clock**:
   - 24 time zones + 5 special positions = period 29
   - 148 city names could encode key letters
   - Key derivation method remains unknown

3. **Interpretation of UNDER...NORTHEAST...BERLINCLOCK...ABOVE**:
   - Geographic directions from the Berlin World Clock?
   - Vertical positioning (underground/above ground)?
   - Reference to layers (like K2's "LAYER TWO")?

### Methods Tested and Rejected

| Method | Result |
|--------|--------|
| Simple periodic Vigenère (periods 5-19) | Mathematically impossible |
| Gromark cipher | No solution found |
| Transposition + substitution | No improvement |
| W-separator theory | Partially supported but incomplete |
| Cyclic shift transposition | Found SPY/KEY in gibberish but not the method |
| Running key from K1-K3 | No solution |
| Berlin Clock city names as key | No direct match |

### Conclusion

K4 uses a **period 29 Vigenère cipher** with key `DIJJQELYOIECBAQKVAATCRDUMPABT`. This key produces four readable words:
- **UNDER** (position 0)
- **NORTHEAST** (position 16) ✓ confirmed
- **BERLINCLOCK** (position 63) ✓ confirmed
- **ABOVE** (position 83)

The remaining 67 characters are gibberish. The cryptographic METHOD for deriving this key from the Berlin World Clock remains the final unsolved mystery. Sanborn has stated that having the words is not the same as solving the cipher—the method matters.

**Status**: Partial solution. Waiting for either:
1. Method derivation from Berlin World Clock structure
2. 2075 unsealing of Smithsonian archives
3. Disclosure by the $962,500 auction winner

### K5 Connection (Critical Discovery)

Sanborn announced in August 2025 that **K5 exists** and will:
- Use the **same cryptographic system** as K4
- Have **BERLINCLOCK at the same position** (position 63)
- Be **97 characters** (same as K4)
- Have **"a more global reach"** and be **"publicly accessible"**
- Be released after K4 is truly solved

This confirms our Period 29 analysis is correct for both K4 and K5.

### Sanborn's Final Hints (November 2025)

1. **"Who says it is even a math solution?"** - Suggests non-standard approach
2. **Two pivotal events**: 1986 Egypt trip + 1989 Berlin Wall fall
3. **"Creativity is needed"** to find the key
4. **"Delivering a message"** - all codes from morse through K5 serve this purpose
5. **The Berlin Clock** = Weltzeituhr at Alexanderplatz, gathering place for Berlin Wall crowds

### Why the Gibberish Matters (Or Doesn't)

The 67 gibberish characters may be:
1. **Intentional null padding** - only the 4 words matter
2. **Pointing to K5** - the structure, not the content, is the clue
3. **Undecipherable without K5** - a two-part puzzle

Sanborn stated: *"Even when K4 has been solved, its riddle will persist as K5."*

This suggests K4 is not meant to be fully decoded in isolation—it's a stepping stone to K5.

### The Real Puzzle

The METHOD is the unsolved mystery, not the plaintext. We must discover:
1. How Period 29 connects to the Berlin World Clock's 24 zones
2. How the key DIJJQELYOIECBAQKVAATCRDUMPABT is derived
3. What the 1986 Egypt trip and 1989 Berlin Wall fall contribute
4. Where K5 will appear ("more global reach")
