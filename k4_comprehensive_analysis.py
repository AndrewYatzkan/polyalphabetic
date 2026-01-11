#!/usr/bin/env python3
"""
Comprehensive analysis of K4 gibberish sections with extensive checks
"""

from itertools import permutations, combinations
from collections import Counter
import re

SECTIONS = {
    "Section 1 (after UNDER)": "QAPBZDBKZEL",
    "Section 2 (after NORTHEAST)": "LGUWCXDJFQGUZOUAFZFETMMNXPSOZ",
    "Section 3 (middle)": "MPAPGKPVH",
    "Section 4 (after BERLINCLOCK)": "RSPVJWQUL",
    "Section 5 (after ABOVE, end)": "ZOLRKCAYF"
}

# Comprehensive word lists
ENGLISH_9_LETTER = [
    "abandoned", "abilities", "abolition", "absurdity", "abundance", "accompany",
    "according", "achieving", "acquiring", "activated", "adventure", "afterward",
    "agreement", "algorithm", "alignment", "allocated", "amendment", "analyzing",
    "announced", "answering", "appearing", "appointed", "approving", "arbitrary",
    "architect", "arguments", "arranging", "artifacts", "assembled", "asserting",
    "assistant", "associate", "attempted", "attention", "authentic", "authority",
    "awakening", "awareness", "beautiful", "beginning", "behaviour", "billboard",
    "biography", "blueprint", "broadcast", "buildings", "bypassing", "calculate",
    "capturing", "carefully", "cartridge", "catalogue", "cathedral", "celebrate",
    "certainly", "certified", "character", "chemicals", "childhood", "chocolate",
    "cigarette", "classical", "clearance", "clockwork", "coalition", "cognitive",
    "collected", "commander", "commodity", "community", "comparing", "competing",
    "completed", "component", "computing", "concealed", "conceived", "concerned",
    "concluded", "condemned", "condition", "conducted", "confident", "confirmed",
    "confusing", "connected", "conscious", "consensus", "consulted", "contained",
    "continued", "convinced", "cooperate", "copyright", "corrupted", "countries",
    "crossword", "dangerous", "databases", "deceptive", "dedicated", "defensive",
    "demanding", "democracy", "departure", "depressed", "described", "designing",
    "desperate", "destroyed", "detective", "determine", "developed", "deviation",
    "different", "difficult", "dimension", "directing", "directory", "disappear",
    "disasters", "discharge", "disclosed", "discovery", "discussed", "disguised",
    "displayed", "dissolved", "distances", "districts", "disturbed", "diversity",
    "documents", "dominance", "dominated", "duplicate", "elaborate", "elections",
    "eliminate", "elsewhere", "embracing", "emergence", "emergency", "emotional",
    "emphasize", "employees", "encounter", "encrypted", "endlessly", "engineers",
    "enhancing", "enjoyable", "entertain", "enumerate", "equipment", "essential",
    "establish", "estimated", "evaluated", "everybody", "evolution", "examining",
    "exceeding", "excellent", "exception", "excessive", "exchanged", "excluding",
    "exclusive", "executing", "executive", "existence", "expansion", "expecting",
    "expensive", "expertise", "explained", "exploding", "exploring", "expressed",
    "extending", "extension", "extensive", "extracted", "extremist", "fabricate",
    "factories", "favorable", "featuring", "fertility", "financing", "fireplace",
    "fisherman", "flashback", "foreigner", "forgotten", "formation", "formatted",
    "formulate", "forwarded", "framework", "franchise", "frequency", "frontline",
    "fulfilled", "functions", "generated", "gentleman", "happening", "harassing",
    "harmonize", "hazardous", "headlines", "heartbeat", "hierarchy", "highlight",
    "historian", "holocaust", "hopefully", "hospitals", "hostility", "household",
    "hurricane", "identical", "ignorance", "imaginary", "immediate", "immensely",
    "impacting", "implement", "important", "improving", "inability", "incidents",
    "including", "incorrect", "increased", "incumbent", "indicated", "indicator",
    "infection", "influence", "informant", "inherited", "initially", "initiated",
    "inquiries", "insisting", "inspector", "installed", "instantly", "institute",
    "insulting", "insurance", "integrate", "integrity", "intellect", "intensely",
    "intensive", "intention", "interface", "interpret", "interrupt", "interview",
    "introduce", "intuition", "invariant", "invention", "inventory", "investing",
    "invisible", "involving", "irregular", "jefferson", "kidnapped", "kilometer",
    "knowledge", "labelling", "laborious", "landscape", "languages", "launching",
    "lawmakers", "legendary", "legislate", "lightning", "limestone", "literally",
    "locations", "magnitude", "maintains", "manifesto", "marketing", "materials",
    "meanwhile", "measuring", "mechanism", "mechanics", "medicinal", "memorable",
    "mentioned", "merchants", "messaging", "migration", "ministers", "miserable",
    "modelling", "moderator", "molecular", "monastery", "monitored", "motivated",
    "mountains", "movements", "narrative", "naturally", "navigator", "necessity",
    "negotiate", "neighbors", "networked", "newspaper", "nightmare", "nominated",
    "northeast", "northwest", "notebooks", "notifying", "numerical", "objective",
    "obligated", "obscurity", "observant", "observing", "obsession", "obtaining",
    "occupants", "occupying", "occurring", "offensive", "officials", "operating",
    "operation", "opponents", "orchestra", "ordinance", "organisms", "organized",
    "organizer", "originals", "overnight", "packaging", "paintings", "paperwork",
    "paragraph", "paramount", "partially", "particles", "partition", "passenger",
    "patrolled", "patronage", "peacetime", "peninsula", "perimeter", "permanent",
    "permitted", "personnel", "petitions", "phenomena", "pioneered", "placement",
    "planetary", "platforms", "plausible", "poisoning", "polarized", "pollution",
    "populated", "possessed", "potential", "practical", "precedent", "precisely",
    "precision", "predicted", "preferred", "prejudice", "preparing", "presented",
    "preserved", "presiding", "pressured", "pretended", "prevalent", "primarily",
    "primitive", "principle", "prisoners", "probation", "procedure", "processed",
    "producing", "professor", "profiling", "programme", "projected", "promising",
    "promoting", "promotion", "pronounce", "propagate", "proposals", "proposing",
    "protected", "protested", "prototype", "providing", "provinces", "provision",
    "proximity", "published", "publisher", "purchased", "qualified", "quarterly",
    "questions", "quicksand", "quotation", "radiation", "radically", "rationale",
    "reactions", "realigned", "realities", "realistic", "realizing", "reasoning",
    "receiving", "recession", "reckoning", "recognize", "recommend", "recording",
    "recovered", "recruited", "recurring", "recycling", "redefined", "reduction",
    "redundant", "referring", "reflected", "reforming", "refreshed", "regarding",
    "registers", "regretted", "regulated", "regulator", "rehearsal", "reinstall",
    "reinstate", "reiterate", "rejection", "releasing", "relevance", "relieving",
    "religious", "reluctant", "remainder", "remaining", "rendering", "renewable",
    "renovated", "reopening", "repayment", "repeating", "replacing", "replicate",
    "reporting", "represent", "repressed", "reproduce", "requested", "requiring",
    "resembled", "reserving", "residence", "residency", "resistant", "resolving",
    "resonance", "resources", "respected", "responded", "restoring", "restraint",
    "resulting", "resurgent", "retailers", "retailing", "retention", "retrained",
    "retrieved", "returning", "reuniting", "revealing", "reversing", "revisions",
    "revolving", "righteous", "safeguard", "sanctuary", "sandstorm", "satellite",
    "satisfied", "scenarios", "scheduled", "scholarly", "scientist", "scrambled",
    "screening", "secretary", "sectarian", "selecting", "selection", "selective",
    "semantics", "semicolon", "seniority", "senseless", "sensitive", "sentiment",
    "separated", "separator", "september", "sequester", "servicing", "sexuality",
    "sheltered", "shielding", "shortcuts", "shortened", "shuffling", "sidelined",
    "sightings", "signaling", "signature", "simulated", "simulator", "singleton",
    "situation", "skeptical", "slaughter", "sleepless", "smuggling", "snowstorm",
    "socialist", "societies", "sociology", "solutions", "somewhere", "southeast",
    "southwest", "sovereign", "specially", "specifics", "specified", "specimens",
    "spectacle", "speculate", "spiritual", "splitting", "spokesman", "sponsored",
    "spotlight", "spreading", "squashing", "stabilize", "stalemate", "standards",
    "stationed", "statistic", "steadfast", "steamship", "stiffened", "stimulate",
    "storyline", "strangers", "strategic", "streaming", "stretched", "stringent",
    "strongest", "structure", "struggled", "subjected", "submarine", "submitted",
    "subscribe", "substance", "subtitled", "succeeded", "successor", "suffering",
    "suggested", "summarize", "summoning", "sunflower", "sunscreen", "superstar",
    "supplying", "supported", "supporter", "supposing", "supremacy", "surcharge",
    "surprised", "surrender", "surrogate", "surveying", "survivors", "suspected",
    "suspended", "sustained", "symbolize", "symmetric", "synagogue", "syndicate",
    "synthesis", "targeting", "taxpayers", "teachings", "technique", "teenagers",
    "telegraph", "telephone", "telescope", "temporary", "terrorism", "terrorist",
    "testified", "therefore", "thousands", "threatens", "threshold", "thrilling",
    "tightened", "tolerance", "tolerated", "touchdown", "townships", "trademark",
    "tradition", "transcend", "transfers", "transform", "transient", "translate",
    "transmits", "transport", "trapezoid", "traveling", "treasurer", "treatment",
    "triggered", "trimester", "troubling", "turmoil", "unanimous", "uncertain",
    "unchanged", "unclaimed", "undergone", "underline", "undermine", "undertake",
    "underwent", "unequaled", "unfounded", "unhealthy", "uniformed", "universal",
    "unleashed", "unlimited", "unmarried", "unnatural", "unpopular", "unrivaled",
    "unsettled", "untouched", "unwilling", "upgrading", "uppercase", "upholding",
    "uploading", "valuables", "vandalism", "vegetable", "venerable", "vengeance",
    "ventilate", "versatile", "vibration", "victorian", "victories", "violation",
    "virtually", "visualize", "volunteer", "warehouse", "warranted", "watershed",
    "wondering", "workbench", "workplace", "worksheet", "worldwide", "worsening",
    "wrestling", "yesterday"
]

GERMAN_WORDS = [
    # Common German
    "achtung", "arbeit", "ausgang", "bahn", "berg", "berlin", "blitz", "brot",
    "bruder", "bund", "burg", "dank", "deutsch", "dienst", "ding", "dorf",
    "drei", "ein", "eins", "ende", "fahrt", "feld", "fest", "flucht",
    "frau", "frei", "freund", "garten", "geheim", "geist", "geld", "gott",
    "grau", "grenz", "grenze", "gross", "grund", "gut", "haus", "herr",
    "heute", "hier", "himmel", "hoch", "jahr", "jung", "kalt", "kind",
    "klein", "konig", "kopf", "kraft", "krieg", "kunst", "kurz", "lang",
    "leben", "licht", "liebe", "luft", "macht", "mann", "mauer", "meer",
    "mein", "mitte", "morgen", "nacht", "name", "neben", "nehmen", "neu",
    "nicht", "nord", "nur", "ober", "oben", "ohne", "orden", "ort", "ost",
    "platz", "punkt", "recht", "reich", "rot", "ruhe", "sagen", "schlaf",
    "schluss", "schon", "schwarz", "schwer", "sehen", "sehr", "sein",
    "sicher", "sohn", "stadt", "stark", "stein", "strasse", "stuck", "sud",
    "tag", "teil", "tief", "tod", "tor", "tun", "turm", "uhr", "und",
    "unser", "unter", "unten", "vater", "versteck", "viel", "volk", "von",
    "vor", "wahr", "wand", "wasser", "wegen", "weit", "welt", "wenig",
    "wenn", "werk", "wert", "west", "wie", "wieder", "wissen", "wo",
    "wort", "zeit", "zentrum", "zimmer", "zu", "zugang", "zwei", "zwischen",
    # WWII/Cold War
    "abwehr", "akte", "bnd", "ddr", "enigma", "flak", "gestapo", "mauerfall",
    "panzer", "stasi", "sturm", "reich", "fuhrer", "bunker"
]

LATIN_WORDS = [
    "ab", "ad", "ante", "aqua", "ars", "audio", "caput", "carpe", "circa",
    "corpus", "credo", "deus", "dies", "dominus", "ego", "ergo", "est", "et",
    "ex", "fides", "gloria", "gratis", "homo", "idem", "ignis", "in", "locus",
    "lux", "magnus", "mare", "mors", "nihil", "non", "nox", "opus", "pax",
    "per", "post", "primus", "pro", "rex", "roma", "sanctus", "semper", "sic",
    "sol", "status", "sub", "sum", "tempus", "terra", "tres", "ultra", "unum",
    "urbs", "verbum", "veritas", "via", "vice", "vita", "vox"
]


def letter_value(c):
    """A=1, B=2, etc."""
    return ord(c.upper()) - ord('A') + 1


def check_is_anagram(text, word):
    """Check if text is an anagram of word"""
    return sorted(text.upper()) == sorted(word.upper())


def find_partial_words(text, word_list, min_len=3):
    """Find words that can be formed from the letters in text"""
    text = text.upper()
    text_counter = Counter(text)
    matches = []

    for word in word_list:
        word = word.upper()
        if min_len <= len(word) <= len(text):
            word_counter = Counter(word)
            if all(word_counter[c] <= text_counter[c] for c in word_counter):
                matches.append(word)

    return sorted(set(matches), key=len, reverse=True)


def check_substrings(text, word_list):
    """Check if any words appear as substrings"""
    text = text.upper()
    found = []
    for word in word_list:
        word = word.upper()
        if len(word) >= 2 and word in text:
            found.append((word, text.find(word)))
    return found


def every_nth(text, n, start=0):
    """Get every nth character starting at position start"""
    return ''.join(text[i] for i in range(start, len(text), n))


def reverse(text):
    return text[::-1]


def atbash(text):
    """A->Z, B->Y, etc."""
    return ''.join(chr(ord('Z') - (ord(c) - ord('A'))) if c.isalpha() else c
                   for c in text.upper())


def caesar(text, shift):
    """Caesar cipher with given shift"""
    return ''.join(chr((ord(c) - ord('A') + shift) % 26 + ord('A')) if c.isalpha() else c
                   for c in text.upper())


def to_numbers(text):
    """Convert to A=1 numbers"""
    return [letter_value(c) for c in text]


def check_coordinate_patterns(nums):
    """Check for geographic coordinate patterns"""
    results = []

    # K2 reference: 38.57.6.5 N, 77.8.44 W
    # Look for similar patterns

    # Langley coordinates: approximately 38.93 N, 77.15 W
    # Check if numbers could represent this

    for i in range(len(nums)-1):
        # Check for 38 (latitude) or 77 (longitude) patterns
        if nums[i] == 3 and i+1 < len(nums) and nums[i+1] == 8:
            results.append(f"Pattern '38' at position {i}")
        if nums[i] == 7 and i+1 < len(nums) and nums[i+1] == 7:
            results.append(f"Pattern '77' at position {i}")

        # Check for degree-like values (1-90 for lat, 1-180 for lon)
        if 1 <= nums[i] <= 26:
            for j in range(i+1, min(i+4, len(nums))):
                # Could be deg-min-sec format
                if i+2 < len(nums):
                    deg, min_v, sec = nums[i], nums[i+1], nums[i+2]
                    if deg <= 90 and min_v < 60 and sec < 60:
                        coord = f"{deg}d{min_v}'{sec}\""
                        results.append(f"Possible coord at {i}: {coord}")

    return results


def analyze_section(name, text):
    """Comprehensive analysis of a single section"""
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"Text: {text}")
    print(f"Length: {len(text)}")
    print("=" * 70)

    # Basic transforms
    print("\n--- BASIC TRANSFORMS ---")
    print(f"Reversed: {reverse(text)}")
    print(f"Atbash: {atbash(text)}")

    # Check ROT shifts for interesting results
    interesting_shifts = []
    for shift in range(1, 26):
        shifted = caesar(text, shift)
        # Check if shifted version contains common words
        for word in ["THE", "AND", "FOR", "KEY", "MAP", "SPY", "CIA", "GPS",
                     "LAT", "LON", "DEG", "POS", "REF"]:
            if word in shifted:
                interesting_shifts.append((shift, shifted, word))
    if interesting_shifts:
        print("Interesting Caesar shifts:")
        for shift, shifted, word in interesting_shifts:
            print(f"  Shift {shift}: {shifted} (contains '{word}')")
    else:
        print("No interesting Caesar shifts found")

    # Number encoding
    print("\n--- NUMERIC ENCODING (A=1, B=2, ...) ---")
    nums = to_numbers(text)
    print(f"Values: {nums}")
    print(f"Sum: {sum(nums)}")
    print(f"Product mod 100: {eval('*'.join(map(str, nums))) % 100 if len(nums) < 15 else 'too large'}")

    # Check coordinate patterns
    coord_patterns = check_coordinate_patterns(nums)
    if coord_patterns:
        print("Coordinate-like patterns:")
        for p in coord_patterns:
            print(f"  {p}")

    # Every nth letter analysis
    print("\n--- EVERY NTH LETTER ---")
    for n in [2, 3, 4, 5]:
        for start in range(n):
            extracted = every_nth(text, n, start)
            if len(extracted) >= 2:
                print(f"Every {n}th (offset {start}): {extracted}")

    # Check for German words/substrings
    print("\n--- GERMAN ANALYSIS ---")
    german_found = check_substrings(text, GERMAN_WORDS)
    german_found += check_substrings(reverse(text), GERMAN_WORDS)
    german_partial = find_partial_words(text, GERMAN_WORDS)
    if german_found:
        print("Substrings found:")
        for word, pos in german_found:
            print(f"  '{word}' at position {pos}")
    if german_partial:
        print(f"Words formable from letters: {german_partial[:10]}")
    if not german_found and not german_partial:
        print("No German patterns found")

    # Check for Latin words
    print("\n--- LATIN ANALYSIS ---")
    latin_found = check_substrings(text, LATIN_WORDS)
    latin_found += check_substrings(reverse(text), LATIN_WORDS)
    latin_partial = find_partial_words(text, LATIN_WORDS)
    if latin_found:
        print("Substrings found:")
        for word, pos in latin_found:
            print(f"  '{word}' at position {pos}")
    if latin_partial:
        print(f"Words formable from letters: {latin_partial[:10]}")
    if not latin_found and not latin_partial:
        print("No Latin patterns found")

    # Letter frequency analysis
    print("\n--- LETTER FREQUENCY ---")
    freq = Counter(text)
    print(f"Distribution: {dict(freq.most_common())}")

    # Calculate IoC
    n = len(text)
    if n > 1:
        ioc = sum(f * (f-1) for f in freq.values()) / (n * (n-1))
        print(f"Index of Coincidence: {ioc:.4f}")
        if ioc < 0.045:
            print("  -> Very flat (heavily encrypted)")
        elif ioc < 0.055:
            print("  -> Somewhat flat (cipher text)")
        else:
            print("  -> Near English (possible plaintext)")

    # Check for repeating patterns
    print("\n--- REPEATING PATTERNS ---")
    repeats = []
    for length in range(2, len(text)//2 + 1):
        for i in range(len(text) - length + 1):
            substr = text[i:i+length]
            count = text.count(substr)
            if count > 1:
                repeats.append((substr, count))
    repeats = list(set(repeats))
    repeats.sort(key=lambda x: (-len(x[0]), -x[1]))
    if repeats:
        for pat, count in repeats[:5]:
            print(f"  '{pat}' appears {count} times")
    else:
        print("  No repeating patterns")

    # Check if could be anagram of any 9-letter word (for 9-char sections)
    if len(text) == 9:
        print("\n--- ANAGRAM CHECK (9-letter words) ---")
        anagram_matches = [w for w in ENGLISH_9_LETTER if check_is_anagram(text, w)]
        if anagram_matches:
            print(f"FOUND ANAGRAMS: {anagram_matches}")
        else:
            print("No exact anagrams found")

    # Check if could be abbreviation
    print("\n--- ABBREVIATION ANALYSIS ---")
    if len(text) <= 6:
        print(f"Short enough to be abbreviation/acronym")
    # Check for common abbreviation patterns
    if text[0] in "QXZJK":
        print(f"Starts with uncommon letter '{text[0]}' - possible code designator")
    if all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in text):
        print("All uppercase letters (standard for abbreviations)")


def combined_analysis():
    """Analyze all sections together"""
    print("\n" + "=" * 70)
    print("COMBINED CROSS-SECTION ANALYSIS")
    print("=" * 70)

    texts = list(SECTIONS.values())
    names = list(SECTIONS.keys())

    # First letters
    firsts = ''.join(t[0] for t in texts)
    print(f"\nFirst letters: {firsts}")
    print(f"  Values: {to_numbers(firsts)}")

    # Last letters
    lasts = ''.join(t[-1] for t in texts)
    print(f"Last letters: {lasts}")
    print(f"  Values: {to_numbers(lasts)}")

    # Section lengths
    lengths = [len(t) for t in texts]
    print(f"\nSection lengths: {lengths}")
    print(f"Sum of lengths: {sum(lengths)}")

    # 11, 29, 9, 9, 9
    # K = 11, ? = 29, I = 9
    length_letters = []
    for n in lengths:
        if 1 <= n <= 26:
            length_letters.append(chr(ord('A') + n - 1))
        else:
            length_letters.append('?')
    print(f"Lengths as letters: {''.join(length_letters)}")

    # All text combined
    all_text = ''.join(texts)
    print(f"\nAll combined: {all_text}")
    print(f"Total length: {len(all_text)}")

    # Check combined text for patterns
    print("\n--- PATTERNS IN COMBINED TEXT ---")

    # Common English substrings
    common_words = ["THE", "AND", "FOR", "KEY", "MAP", "GPS", "REF", "LAT", "LON",
                    "POS", "DEG", "SEC", "MIN", "CODE", "ZONE", "AREA", "GRID",
                    "POINT", "COORD", "NORTH", "SOUTH", "EAST", "WEST"]
    found_in_combined = []
    for word in common_words:
        if word in all_text:
            found_in_combined.append((word, all_text.find(word)))
        if word in reverse(all_text):
            found_in_combined.append((word + " (rev)", len(all_text) - reverse(all_text).find(word) - len(word)))
    if found_in_combined:
        for word, pos in found_in_combined:
            print(f"  '{word}' at position {pos}")
    else:
        print("  No common word substrings found")


def main():
    print("=" * 70)
    print("COMPREHENSIVE K4 GIBBERISH ANALYSIS")
    print("=" * 70)

    for name, text in SECTIONS.items():
        analyze_section(name, text)

    combined_analysis()

    # Summary of key findings
    print("\n" + "=" * 70)
    print("SUMMARY OF KEY FINDINGS")
    print("=" * 70)

    print("""
SECTION 1 (QAPBZDBKZEL - 11 chars):
- Between UNDER and NORTHEAST
- IoC very low (0.036) - appears heavily encrypted
- No clear word patterns
- Contains letters B, Z repeated

SECTION 2 (LGUWCXDJFQGUZOUAFZFETMMNXPSOZ - 29 chars):
- Between NORTHEAST and BERLINCLOCK
- Contains Latin substring "ET" at position 19
- Pattern "GU" appears twice
- Contains "MM" doubled letters
- Reversed contains German "ZU"
- IoC very low (0.032)
- Words CODE, EAST, WEST, GATE can be formed from letters

SECTION 3 (MPAPGKPVH - 9 chars):
- Contains "PAP" substring
- Letter P appears 3 times
- Higher IoC (0.083) - closer to English
- Could be abbreviation

SECTION 4 (RSPVJWQUL - 9 chars):
- All unique letters (no repeats)
- IoC is 0 (completely flat)
- Between BERLINCLOCK and ABOVE

SECTION 5 (ZOLRKCAYF - 9 chars):
- After ABOVE (end of message)
- All unique letters
- IoC is 0 (completely flat)

CROSS-SECTION PATTERNS:
- First letters: QLMRZ (values: 17,12,13,18,26 = sum 86)
- Last letters: LZHLF (values: 12,26,8,12,6 = sum 64)
- Section lengths: 11, 29, 9, 9, 9 (sum 67)
- Length pattern: K, ?, I, I, I (11=K, 9=I)

POSSIBLE INTERPRETATIONS:
1. These may be encoded coordinates requiring a second cipher
2. May be intentional padding/noise (Sanborn's style)
3. May require a different key/method to decode
4. The three 9-letter sections could be related (same structure)
""")


if __name__ == "__main__":
    main()
