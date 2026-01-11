#!/usr/bin/env python3
"""
Visualize the structure of readable vs gibberish sections in K4 plaintext
"""

plaintext = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

readable_sections = {
    "UNDER": (0, 4),
    "NORTHEAST": (16, 24),
    "BERLIN": (63, 68),
    "CLOCK": (69, 73),
    "ABOVE": (83, 86)
}

gibberish_sections = {
    "Section 1": (5, 15),
    "Section 2": (25, 62),
    "Section 3": (74, 82),
    "Section 4": (88, 96)
}

print("=" * 100)
print("K4 PLAINTEXT STRUCTURE VISUALIZATION")
print("=" * 100)

# Create a visual representation
print("\nPlaintext with readable words in CAPS and gibberish in lowercase:")
print()

visual = []
for i, char in enumerate(plaintext):
    # Determine if position is readable or gibberish
    is_readable = False
    for start, end in readable_sections.values():
        if start <= i <= end:
            is_readable = True
            break

    if is_readable:
        visual.append(char)
    else:
        visual.append(char.lower())

# Print in chunks of 50
for i in range(0, len(visual), 50):
    chunk = visual[i:i+50]
    pos_str = f"[{i:3d}-{i+len(chunk)-1:3d}]"
    print(f"{pos_str}: {''.join(chunk)}")

print("\n" + "=" * 100)
print("DETAILED BREAKDOWN BY SECTION")
print("=" * 100)

# Show each section with stats
all_positions = []

print("\nREADABLE SECTIONS (Known English words):")
print("-" * 100)

for name in ["UNDER", "NORTHEAST", "BERLIN", "CLOCK", "ABOVE"]:
    start, end = readable_sections[name]
    length = end - start + 1
    text = plaintext[start:end+1]
    all_positions.extend([(i, 'R') for i in range(start, end+1)])
    print(f"  {name:12s}  [{start:2d}-{end:2d}]  ({length:2d} chars)  {text}")

print("\nGIBBERISH SECTIONS (Unknown/Encrypted):")
print("-" * 100)

for name, (start, end) in gibberish_sections.items():
    length = end - start + 1
    text = plaintext[start:end+1]
    all_positions.extend([(i, 'G') for i in range(start, end+1)])
    print(f"  {name:12s}  [{start:2d}-{end:2d}]  ({length:2d} chars)  {text}")

print("\n" + "=" * 100)
print("POSITION MAP (R=Readable, G=Gibberish)")
print("=" * 100)

# Create position map
pos_map = [' '] * len(plaintext)
for start, end in readable_sections.values():
    for i in range(start, end+1):
        pos_map[i] = 'R'

for start, end in gibberish_sections.values():
    for i in range(start, end+1):
        pos_map[i] = 'G'

print("\nPosition markers (every 10 characters):")
print("         0         1         2         3         4         5         6         7         8         9")
print("         |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |    |")
print("".join(pos_map))

# Create numeric position guide
print("\nNumeric position guide:")
for i in range(0, len(plaintext), 10):
    print(f"{i:3d} ", end="")
print()

print("\n" + "=" * 100)
print("INTERLACING PATTERN")
print("=" * 100)

print("\nSequence of readable vs gibberish sections:")
print()

# Track transitions
sections_in_order = []

i = 0
while i < len(plaintext):
    # Check if readable
    for name, (start, end) in readable_sections.items():
        if i == start:
            sections_in_order.append((name, 'R', start, end))
            i = end + 1
            break
    else:
        # Check if gibberish
        for name, (start, end) in gibberish_sections.items():
            if i == start:
                sections_in_order.append((name, 'G', start, end))
                i = end + 1
                break
        else:
            i += 1

for idx, (name, type_, start, end) in enumerate(sections_in_order, 1):
    length = end - start + 1
    text = plaintext[start:end+1]
    symbol = "●" if type_ == 'R' else "○"
    print(f"{idx}. {symbol} {name:12s}  [{start:2d}-{end:2d}]  ({length:2d} chars)")

print("\n" + "=" * 100)
print("KEY PATTERNS")
print("=" * 100)

print("""
READABLE PATTERN: 5, 9, 6, 5, 4 characters
  Sum: 29 characters total
  Interesting: The key period is 29!

GIBBERISH PATTERN: 11, 38, 9, 9 characters
  Sum: 67 characters total
  Relationship: 29 + 67 = 96 total plaintext characters

PLACEMENT PATTERN:
  Position 0:    [R] UNDER
  Position 5:    [G] QAPBZDBKZEL
  Position 16:   [R] NORTHEAST
  Position 25:   [G] LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH
  Position 63:   [R] BERLIN
  Position 69:   [R] CLOCK
  Position 74:   [G] RSPVJWQUL
  Position 83:   [R] ABOVE
  Position 88:   [G] ZOLRKCAYF

ADJACENCY:
  G1 comes immediately after UNDER
  G2 comes immediately after NORTHEAST
  G3 comes immediately after CLOCK
  G4 comes after gap from ABOVE

  BERLIN and CLOCK are consecutive readable sections with NO gibberish between!
""")

print("=" * 100)
print("LETTER DISTRIBUTION")
print("=" * 100)

from collections import Counter

readable_text = "".join(plaintext[start:end+1] for start, end in readable_sections.values())
gibberish_text = "".join(plaintext[start:end+1] for start, end in gibberish_sections.values())

print(f"\nReadable text ({len(readable_text)} chars): {readable_text}")
print(f"Gibberish text ({len(gibberish_text)} chars): {gibberish_text}")

print(f"\nReadable unique letters: {sorted(set(readable_text))} ({len(set(readable_text))} unique)")
print(f"Gibberish unique letters: {sorted(set(gibberish_text))} ({len(set(gibberish_text))} unique)")

print(f"\nLetters in readable but NOT gibberish: {sorted(set(readable_text) - set(gibberish_text))}")
print(f"Letters in gibberish but NOT readable: {sorted(set(gibberish_text) - set(readable_text))}")
print(f"Common letters: {sorted(set(readable_text) & set(gibberish_text))}")

print("\nLetter 'I' analysis:")
i_in_readable = readable_text.count('I')
i_in_gibberish = gibberish_text.count('I')
print(f"  In readable sections: {i_in_readable} occurrences")
print(f"  In gibberish sections: {i_in_gibberish} occurrences")
print(f"  In entire plaintext: {plaintext.count('I')} occurrences")
print(f"  Note: 'I' appears in word BERLIN and CLOCK (readable), but NOT in gibberish")

print("\n" + "=" * 100)
