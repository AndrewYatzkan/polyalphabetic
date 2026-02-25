#!/usr/bin/env python3
"""
Kryptos K4 Running Key Cipher Analysis
=======================================
Tests running key cipher hypotheses per CryptoCrack analysis.
Ed Scheidt confirmed "masking technique" making frequency analysis useless.
Bonifacino claims 86-letter running key from Berlin Weltzeituhr.
"""

import math
import re
from collections import Counter

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"  # 26 chars, K=0
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Known cribs (0-indexed)
CRIBS = {
    "EASTNORTHEAST": (21, 33),
    "BERLINCLOCK": (63, 73),
}

# Known text sources
K1_PLAIN = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHETHENUBIALOFIQLUSIONENDIDITNOTTHEREWASTHETRANSLUCENCYOFTFSEENSQUARESCLOSEDOFFUNDERTHERELUCTANCEOFLASTYEARSINSISTANCE"
K2_PLAIN = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGABORFLOWSHEANSWEREDYESTHEREWASANEEDTOGOTOADEEPERPOINTOFTHETEXTTOCONCEALTHESECRETOFWHOKNOWSTHEDISCOVERYTHEBURIESTWASSLOWLYDESPAIRATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHUPPERINTHELEFTHANDCORNERANDTHENSENSITIVEUNTILTHEDOORWASCOMPLETELYCLEAREDANDTHEWHOLECHAMBERWASBEFOREME"
K3_PLAIN = "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENIGTHEHOLEALITTLEINSERTEDACANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
COORDS_TEXT = "THIRTYEIGHTDEGREESFIFSEVMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVDEGRESEIGHTMINUTESFORTYFOURSECONDSWEST"
# Alternative spellings of coordinates
COORDS_TEXT_V2 = "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVDEGRESEIGHTMINUTESFORTYFOURSECONDSWEST"
COORDS_TEXT_V3 = "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGRESEIGHTMINUTESFORTYFOURSECONDSWEST"
COORDS_FULL = "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGRESEIGHTMINUTESFORTYFOURSECONDSWEST"

# Howard Carter's text (original source for K3)
CARTER_TEXT = "ATFIRSTICOULDSEENOTHINGTHECANDLELIGHTCAUSEDTHEHOTAIRFROMTHECHAMBERTODANCEBEFOREMYEYESBUTPRESENTLYASTHEYGREWADJUSTEDTOTHELIGHTDETAILSOFTHEROOMWITHINMERGEDFROMTHEMISTSTRRANGEANIMALSFORGOTTENSSTATUESANDGOLDEVERYWHERETHEGLINTTOFGOLDITWASALLICOULDDOFORSOMEMOMENTSCAUGHTUPASIWASINTHESHEERMAZEMENTOFTHESIGHTTHENABOUTTOTURNAROUNDINOTICEDINTHELEFTCORNERWHATWASUNQUESTIONABLYTHEGREATESTDISCOVERYOFALLTHECLOSEDSEALDOOR"

# Berlin Weltzeituhr cities (24 timezone markers)
WELTZEITUHR_CITIES = [
    "HONOLULU", "ANCHORAGE", "VANCOUVER", "CHICAGO", "NEWYORK",
    "CARACAS", "RIODEJANEIRO", "DAKAR", "LONDON", "ROME",
    "CAIRO", "MOSCOW", "TEHERAN", "KABUL", "TASCHKENT",
    "DELHI", "DACCA", "BANGKOK", "PEKING", "TOKIO",
    "SYDNEY", "NOUMEA", "WELLINGTON", "SAMOA"
]

# Alternative city name renderings from the actual clock
WELTZEITUHR_CITIES_ALT = [
    "HONOLULU", "ANCHORAGE", "VANCOUVER", "CHICAGO", "NEWYORK",
    "CARACAS", "RIODEJANEIRO", "DAKAR", "LONDON", "ROM",
    "KAIRO", "MOSKAU", "TEHERAN", "KABUL", "TASCHKENT",
    "DELHI", "DACCA", "BANGKOK", "PEKING", "TOKIO",
    "SYDNEY", "NOUMEA", "WELLINGTON", "SAMOA"
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def load_quadgrams(filepath="/home/user/polyalphabetic/english_quadgrams.txt"):
    """Load quadgram frequencies for scoring."""
    qg = {}
    total = 0
    try:
        with open(filepath) as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    qg[parts[0]] = int(parts[1])
                    total += int(parts[1])
        floor_val = math.log10(0.01 / total)
        for k in qg:
            qg[k] = math.log10(qg[k] / total)
        return qg, floor_val
    except FileNotFoundError:
        return {}, -10.0

def load_words(filepath="/home/user/polyalphabetic/OxfordEnglishWords.txt"):
    """Load English word list."""
    words = set()
    try:
        with open(filepath) as f:
            for line in f:
                w = line.strip().upper()
                if w:
                    words.add(w)
    except FileNotFoundError:
        pass
    # Add common short words that might be missing
    for w in ["A", "I", "AN", "AT", "BY", "DO", "GO", "HE", "IF", "IN", "IS", "IT",
              "ME", "MY", "NO", "OF", "ON", "OR", "SO", "TO", "UP", "US", "WE",
              "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER",
              "WAS", "ONE", "OUR", "OUT", "HAS", "HIS", "HOW", "ITS", "MAY", "NEW",
              "NOW", "OLD", "SEE", "WAY", "WHO", "DID", "GET", "HAS", "HIM", "LET",
              "SAY", "SHE", "TOO", "USE", "THAT", "WITH", "HAVE", "THIS", "WILL",
              "YOUR", "FROM", "THEY", "BEEN", "CALL", "COME", "EACH", "MAKE", "LIKE",
              "LONG", "LOOK", "MANY", "SOME", "THAN", "THEM", "THEN", "TIME", "VERY",
              "WHEN", "WHAT", "EAST", "WEST", "NORTH", "SOUTH", "CLOCK", "BERLIN",
              "NORTHEAST", "EASTNORTHEAST"]:
        words.add(w)
    return words

QUADGRAMS, QG_FLOOR = load_quadgrams()
WORDS = load_words()

def score_quadgrams(text):
    """Score text using quadgram frequencies. Higher = more English-like."""
    if len(text) < 4:
        return -999
    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i:i+4]
        score += QUADGRAMS.get(qg, QG_FLOOR)
    return score / (len(text) - 3)  # Normalize by number of quadgrams

def find_words_in_text(text, min_len=3):
    """Find all English words that appear in a text string."""
    found = []
    text = text.upper()
    for length in range(min_len, min(len(text)+1, 20)):
        for i in range(len(text) - length + 1):
            sub = text[i:i+length]
            if sub in WORDS:
                found.append((i, sub))
    # Remove substrings of longer found words at same position
    found.sort(key=lambda x: (-len(x[1]), x[0]))
    return found

def find_word_coverage(text, min_len=3):
    """Find how much of text can be covered by English words. Returns coverage ratio."""
    text = text.upper()
    n = len(text)
    covered = [False] * n
    
    words_found = find_words_in_text(text, min_len)
    # Greedily cover with longest words first
    for pos, word in words_found:
        for i in range(pos, pos + len(word)):
            if i < n:
                covered[i] = True
    
    return sum(covered) / n if n > 0 else 0

def alpha_index(ch, alphabet):
    """Get index of character in alphabet."""
    return alphabet.index(ch.upper())

def alpha_char(idx, alphabet):
    """Get character at index in alphabet."""
    return alphabet[idx % len(alphabet)]

def vigenere_decrypt_char(ct_ch, key_ch, alphabet):
    """Decrypt: pt = (ct - key) mod 26"""
    ct_idx = alpha_index(ct_ch, alphabet)
    key_idx = alpha_index(key_ch, alphabet)
    pt_idx = (ct_idx - key_idx) % 26
    return alpha_char(pt_idx, alphabet)

def vigenere_encrypt_char(pt_ch, key_ch, alphabet):
    """Encrypt: ct = (pt + key) mod 26"""
    pt_idx = alpha_index(pt_ch, alphabet)
    key_idx = alpha_index(key_ch, alphabet)
    ct_idx = (pt_idx + key_idx) % 26
    return alpha_char(ct_idx, alphabet)

def derive_key_char(ct_ch, pt_ch, alphabet, variant="vigenere"):
    """Derive key character from ciphertext and plaintext."""
    ct_idx = alpha_index(ct_ch, alphabet)
    pt_idx = alpha_index(pt_ch, alphabet)
    if variant == "vigenere":
        # ct = pt + key => key = ct - pt
        key_idx = (ct_idx - pt_idx) % 26
    elif variant == "beaufort":
        # ct = key - pt => key = ct + pt
        key_idx = (ct_idx + pt_idx) % 26
    elif variant == "variant_beaufort":
        # ct = pt - key => key = pt - ct
        key_idx = (pt_idx - ct_idx) % 26
    else:
        key_idx = (ct_idx - pt_idx) % 26
    return alpha_char(key_idx, alphabet)

def derive_key_at_crib(ct, plaintext, start, alphabet, variant="vigenere"):
    """Derive the running key at known crib positions."""
    key = ""
    for i, pt_ch in enumerate(plaintext):
        ct_ch = ct[start + i]
        key += derive_key_char(ct_ch, pt_ch, alphabet, variant)
    return key

def decrypt_with_running_key(ct, key, alphabet, variant="vigenere"):
    """Decrypt ciphertext with a running key."""
    pt = ""
    for i in range(min(len(ct), len(key))):
        ct_idx = alpha_index(ct[i], alphabet)
        key_idx = alpha_index(key[i], alphabet)
        if variant == "vigenere":
            pt_idx = (ct_idx - key_idx) % 26
        elif variant == "beaufort":
            pt_idx = (key_idx - ct_idx) % 26
        elif variant == "variant_beaufort":
            pt_idx = (ct_idx + key_idx) % 26  # pt = ct + key for variant beaufort decrypt
        else:
            pt_idx = (ct_idx - key_idx) % 26
        pt += alpha_char(pt_idx, alphabet)
    return pt

# ============================================================
# TEST 1: Derive running key at crib positions
# ============================================================

def test1_derive_key_at_cribs():
    """Derive running key at crib positions for all alphabet/variant combos."""
    print("=" * 80)
    print("TEST 1: DERIVE RUNNING KEY AT CRIB POSITIONS")
    print("=" * 80)
    
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    
    results = []
    
    for alpha_name, alpha in alphabets:
        for variant in variants:
            print(f"\n--- {alpha_name} alphabet, {variant} variant ---")
            all_key_fragments = {}
            
            for crib_name, (start, end) in CRIBS.items():
                crib_text = crib_name
                key_frag = derive_key_at_crib(K4, crib_text, start, alpha, variant)
                all_key_fragments[crib_name] = (start, key_frag)
                
                qg_score = score_quadgrams(key_frag) if len(key_frag) >= 4 else -999
                words = find_words_in_text(key_frag, 3)
                coverage = find_word_coverage(key_frag, 3)
                
                print(f"  Crib: {crib_name} at positions {start}-{end}")
                print(f"  CT:   {K4[start:end+1]}")
                print(f"  PT:   {crib_text}")
                print(f"  KEY:  {key_frag}")
                print(f"  Quadgram score: {qg_score:.4f}")
                print(f"  Word coverage:  {coverage:.1%}")
                if words:
                    print(f"  Words found: {[(w, pos) for pos, w in words[:10]]}")
                print()
                
                results.append({
                    "alpha": alpha_name, "variant": variant,
                    "crib": crib_name, "key": key_frag,
                    "score": qg_score, "coverage": coverage,
                    "words": words
                })
            
            # Show the full derived key stream with gaps
            # Positions 21-33 and 63-73
            full_key = ['?'] * len(K4)
            for crib_name, (start, key_frag) in all_key_fragments.items():
                for i, ch in enumerate(key_frag):
                    full_key[start + i] = ch
            
            # Print contiguous derived key region
            key_21_33 = ''.join(full_key[21:34])
            key_63_74 = ''.join(full_key[63:74])
            print(f"  Key at pos 21-33: {key_21_33}")
            print(f"  Key at pos 63-73: {key_63_74}")
            print(f"  Gap between cribs (pos 34-62): 29 unknown characters")
    
    # Find best results
    print("\n--- BEST KEY FRAGMENTS (by quadgram score) ---")
    results.sort(key=lambda x: x["score"], reverse=True)
    for r in results[:6]:
        print(f"  {r['alpha']:8s} {r['variant']:18s} {r['crib']:15s}: {r['key']}  score={r['score']:.4f}  coverage={r['coverage']:.1%}")
    
    return results

# ============================================================
# TEST 2: Known text sources as running key
# ============================================================

def test2_known_text_sources():
    """Test known text sources as potential running keys."""
    print("\n" + "=" * 80)
    print("TEST 2: KNOWN TEXT SOURCES AS RUNNING KEY")
    print("=" * 80)
    
    sources = {
        "K1 plaintext": K1_PLAIN,
        "K2 plaintext": K2_PLAIN,
        "K3 plaintext": K3_PLAIN,
        "Coordinates": COORDS_FULL,
        "Carter text": CARTER_TEXT,
        "KRYPTOS repeated": ("KRYPTOS" * 20)[:97],
        "K1+K2+K3 concat": K1_PLAIN + K2_PLAIN + K3_PLAIN,
    }
    
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    
    best_results = []
    
    for source_name, source_text in sources.items():
        source_text = source_text.upper()
        # Only use alpha characters
        source_alpha = ''.join(c for c in source_text if c.isalpha())
        
        if len(source_alpha) < 10:
            continue
        
        print(f"\n--- Source: {source_name} (length {len(source_alpha)}) ---")
        
        for alpha_name, alpha in alphabets:
            for variant in variants:
                # Test various starting offsets in the source
                max_offset = min(len(source_alpha) - len(K4), 500) if len(source_alpha) > len(K4) else 0
                max_offset = max(max_offset, 0)
                
                best_offset = -1
                best_score = -999
                best_pt = ""
                
                for offset in range(max_offset + 1):
                    key = source_alpha[offset:offset + len(K4)]
                    if len(key) < len(K4):
                        # Wrap around or pad
                        key = (source_alpha * ((len(K4) // len(source_alpha)) + 2))[offset:offset + len(K4)]
                    
                    pt = decrypt_with_running_key(K4, key, alpha, variant)
                    
                    # Check if known cribs appear at expected positions
                    crib_match = True
                    for crib_name, (start, end) in CRIBS.items():
                        crib_len = len(crib_name)
                        if pt[start:start+crib_len] != crib_name:
                            crib_match = False
                            break
                    
                    if crib_match:
                        score = score_quadgrams(pt)
                        print(f"  *** CRIB MATCH at offset {offset}! ***")
                        print(f"      Alpha: {alpha_name}, Variant: {variant}")
                        print(f"      PT: {pt}")
                        print(f"      Score: {score:.4f}")
                        best_results.append((score, source_name, alpha_name, variant, offset, pt))
                    
                    # Also check overall quality
                    score = score_quadgrams(pt)
                    if score > best_score:
                        best_score = score
                        best_offset = offset
                        best_pt = pt
                
                # Report best for this combo
                if best_score > -8.0:  # Only report reasonably good scores
                    print(f"  {alpha_name:8s} {variant:18s} offset={best_offset:3d}  score={best_score:.4f}")
                    print(f"    PT: {best_pt[:50]}...")
                    words = find_words_in_text(best_pt, 4)
                    if words:
                        print(f"    Words: {[(w, pos) for pos, w in words[:8]]}")
                    best_results.append((best_score, source_name, alpha_name, variant, best_offset, best_pt))
    
    # Also test individual K1/K2/K3 at specific alignments
    print("\n--- Testing specific alignments with known plaintexts ---")
    
    # What if key starts at a round number in K2?
    for alpha_name, alpha in alphabets:
        for variant in variants:
            for source_name, source_text in [("K2", K2_PLAIN), ("K3", K3_PLAIN), ("K1", K1_PLAIN)]:
                src = source_text.upper()
                for offset in [0, 26, 52, 78, 97, 100, 150, 200, 250, 300]:
                    if offset + len(K4) > len(src) * 3:
                        continue
                    key = (src * 5)[offset:offset + len(K4)]
                    pt = decrypt_with_running_key(K4, key, alpha, variant)
                    
                    # Check crib at pos 63
                    if "BERLIN" in pt[60:80] or "CLOCK" in pt[60:80]:
                        print(f"  BERLIN/CLOCK found: {source_name} offset={offset} {alpha_name} {variant}")
                        print(f"    PT: {pt}")
                    if "EASTNORTHEAST" in pt:
                        print(f"  EASTNORTHEAST found: {source_name} offset={offset} {alpha_name} {variant}")
                        print(f"    PT: {pt}")
    
    if best_results:
        print("\n--- TOP RESULTS ---")
        best_results.sort(key=lambda x: x[0], reverse=True)
        for score, src, alpha, var, off, pt in best_results[:10]:
            print(f"  score={score:.4f} {src:20s} {alpha:8s} {var:18s} off={off}")
            print(f"    {pt[:60]}...")
    
    return best_results

# ============================================================
# TEST 3: Crib dragging / key extension
# ============================================================

def test3_crib_dragging():
    """Attempt to extend key fragments using English word search."""
    print("\n" + "=" * 80)
    print("TEST 3: CRIB DRAGGING - EXTEND KEY FRAGMENTS")
    print("=" * 80)
    
    # Use the best alphabet/variant combos from Test 1
    # Test all combos and try to extend
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    # Build a dictionary of words by length for faster searching
    words_by_length = {}
    for w in WORDS:
        l = len(w)
        if l not in words_by_length:
            words_by_length[l] = []
        words_by_length[l].append(w)
    
    best_extensions = []
    
    for alpha_name, alpha in alphabets:
        for variant in variants:
            # Derive key at both crib positions
            key_ene = derive_key_at_crib(K4, "EASTNORTHEAST", 21, alpha, variant)
            key_bc = derive_key_at_crib(K4, "BERLINCLOCK", 63, alpha, variant)
            
            print(f"\n--- {alpha_name} {variant} ---")
            print(f"  Key at pos 21-33 (from ENE):  {key_ene}")
            print(f"  Key at pos 63-73 (from BC):   {key_bc}")
            
            # Try to find English words containing these key fragments
            # Key at 21-33 is 13 chars, at 63-73 is 11 chars
            
            # Search for words containing key_ene (or substrings)
            for substr_len in range(6, len(key_ene) + 1):
                for start in range(len(key_ene) - substr_len + 1):
                    substr = key_ene[start:start + substr_len]
                    matching_words = [w for w in WORDS if substr in w and len(w) >= substr_len]
                    if matching_words and len(matching_words) <= 20:
                        for mw in matching_words[:5]:
                            print(f"  ENE key substr '{substr}' (pos {21+start}-{21+start+substr_len-1}) found in word: {mw}")
            
            for substr_len in range(6, len(key_bc) + 1):
                for start in range(len(key_bc) - substr_len + 1):
                    substr = key_bc[start:start + substr_len]
                    matching_words = [w for w in WORDS if substr in w and len(w) >= substr_len]
                    if matching_words and len(matching_words) <= 20:
                        for mw in matching_words[:5]:
                            print(f"  BC key substr '{substr}' (pos {63+start}-{63+start+substr_len-1}) found in word: {mw}")
            
            # Try extending key_ene to the left and right
            # Extend right: we know key[21:34], try to guess key[34] onwards
            # If the key is English text, letters after key_ene should form words
            
            # Also try: if key at pos 21-73 is continuous English text (53 chars)
            # We know chars at 21-33 and 63-73, with 29 unknown in between
            # Check: does the combined fragment look like it could be from English?
            combined = key_ene + "?" * 29 + key_bc
            print(f"  Combined key (pos 21-73): {combined}")
            
            # Score the known fragments
            ene_score = score_quadgrams(key_ene)
            bc_score = score_quadgrams(key_bc)
            print(f"  ENE key quadgram score: {ene_score:.4f}")
            print(f"  BC key quadgram score:  {bc_score:.4f}")
            
            # For reference, typical English text scores around -2.5 to -2.0
            # Random text scores around -4.5 to -5.0
            
            # Try extending by 1-3 chars in each direction using brute force
            print(f"\n  Extending key fragments:")
            
            # Extend key_ene to the right (positions 34, 35, 36...)
            for ext_len in range(1, 5):
                best_ext_score = -999
                best_ext = ""
                for trial in range(26**ext_len):
                    ext = ""
                    t = trial
                    for _ in range(ext_len):
                        ext = alpha[t % 26] + ext
                        t //= 26
                    
                    test_key = key_ene + ext
                    # This key would decrypt positions 21 through 33+ext_len
                    test_ct = K4[21:34+ext_len]
                    test_pt = decrypt_with_running_key(test_ct, test_key, alpha, variant)
                    
                    # Score the plaintext
                    if len(test_pt) >= 4:
                        pt_score = score_quadgrams(test_pt)
                        # Also score the key
                        key_score = score_quadgrams(test_key)
                        combined_score = pt_score + key_score
                        
                        if combined_score > best_ext_score:
                            best_ext_score = combined_score
                            best_ext = ext
                            best_pt = test_pt
                            best_full_key = test_key
                
                if ext_len <= 2:
                    print(f"    Extend ENE key right by {ext_len}: best ext='{best_ext}' -> key={best_full_key}")
                    print(f"      PT would be: {best_pt}  (combined score: {best_ext_score:.4f})")
            
            # Extend key_ene to the left (positions 20, 19, 18...)
            for ext_len in range(1, 5):
                best_ext_score = -999
                best_ext = ""
                for trial in range(26**ext_len):
                    ext = ""
                    t = trial
                    for _ in range(ext_len):
                        ext = alpha[t % 26] + ext
                        t //= 26
                    
                    test_key = ext + key_ene
                    start_pos = 21 - ext_len
                    if start_pos < 0:
                        continue
                    test_ct = K4[start_pos:34]
                    test_pt = decrypt_with_running_key(test_ct, test_key, alpha, variant)
                    
                    if len(test_pt) >= 4:
                        pt_score = score_quadgrams(test_pt)
                        key_score = score_quadgrams(test_key)
                        combined_score = pt_score + key_score
                        
                        if combined_score > best_ext_score:
                            best_ext_score = combined_score
                            best_ext = ext
                            best_pt = test_pt
                            best_full_key = test_key
                
                if ext_len <= 2:
                    print(f"    Extend ENE key left by {ext_len}: best ext='{best_ext}' -> key={best_full_key}")
                    print(f"      PT would be: {best_pt}  (combined score: {best_ext_score:.4f})")
            
            # Similarly extend BC key
            for ext_len in range(1, 3):
                best_ext_score = -999
                best_ext = ""
                for trial in range(26**ext_len):
                    ext = ""
                    t = trial
                    for _ in range(ext_len):
                        ext = alpha[t % 26] + ext
                        t //= 26
                    
                    test_key = key_bc + ext
                    test_ct = K4[63:74+ext_len]
                    if 74 + ext_len > len(K4):
                        continue
                    test_pt = decrypt_with_running_key(test_ct, test_key, alpha, variant)
                    
                    if len(test_pt) >= 4:
                        pt_score = score_quadgrams(test_pt)
                        key_score = score_quadgrams(test_key)
                        combined_score = pt_score + key_score
                        
                        if combined_score > best_ext_score:
                            best_ext_score = combined_score
                            best_ext = ext
                            best_pt = test_pt
                            best_full_key = test_key
                
                print(f"    Extend BC key right by {ext_len}: best ext='{best_ext}' -> key={best_full_key}")
                print(f"      PT would be: {best_pt}  (combined score: {best_ext_score:.4f})")
            
            for ext_len in range(1, 3):
                best_ext_score = -999
                best_ext = ""
                for trial in range(26**ext_len):
                    ext = ""
                    t = trial
                    for _ in range(ext_len):
                        ext = alpha[t % 26] + ext
                        t //= 26
                    
                    test_key = ext + key_bc
                    start_pos = 63 - ext_len
                    if start_pos < 0:
                        continue
                    test_ct = K4[start_pos:74]
                    test_pt = decrypt_with_running_key(test_ct, test_key, alpha, variant)
                    
                    if len(test_pt) >= 4:
                        pt_score = score_quadgrams(test_pt)
                        key_score = score_quadgrams(test_key)
                        combined_score = pt_score + key_score
                        
                        if combined_score > best_ext_score:
                            best_ext_score = combined_score
                            best_ext = ext
                            best_pt = test_pt
                            best_full_key = test_key
                
                print(f"    Extend BC key left by {ext_len}: best ext='{best_ext}' -> key={best_full_key}")
                print(f"      PT would be: {best_pt}  (combined score: {best_ext_score:.4f})")
            
            best_extensions.append((alpha_name, variant, key_ene, key_bc, ene_score, bc_score))
    
    return best_extensions

# ============================================================
# TEST 4: Test alignment of known texts as key
# ============================================================

def test4_alignment_search():
    """Exhaustive search for correct offset in known texts."""
    print("\n" + "=" * 80)
    print("TEST 4: ALIGNMENT SEARCH IN KNOWN TEXTS")
    print("=" * 80)
    
    sources = {
        "K1": K1_PLAIN.upper(),
        "K2": K2_PLAIN.upper(),
        "K3": K3_PLAIN.upper(),
        "K1+K2+K3": (K1_PLAIN + K2_PLAIN + K3_PLAIN).upper(),
        "K2+K3": (K2_PLAIN + K3_PLAIN).upper(),
        "K3+K2+K1": (K3_PLAIN + K2_PLAIN + K1_PLAIN).upper(),
        "Carter": CARTER_TEXT.upper(),
        "Coords": COORDS_FULL.upper(),
    }
    
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    results = []
    
    for source_name, source_text in sources.items():
        src = ''.join(c for c in source_text if c.isalpha())
        
        for alpha_name, alpha in alphabets:
            for variant in variants:
                max_off = max(0, len(src) - len(K4))
                
                for offset in range(max_off + 1):
                    key = src[offset:offset + len(K4)]
                    if len(key) < len(K4):
                        continue
                    
                    pt = decrypt_with_running_key(K4, key, alpha, variant)
                    
                    # Check if BERLINCLOCK appears at position 63
                    bc_match = (pt[63:74] == "BERLINCLOCK")
                    ene_match = (pt[21:34] == "EASTNORTHEAST")
                    
                    if bc_match or ene_match:
                        score = score_quadgrams(pt)
                        print(f"\n  *** CRIB MATCH ***")
                        print(f"  Source: {source_name}, Offset: {offset}")
                        print(f"  Alpha: {alpha_name}, Variant: {variant}")
                        print(f"  BC match: {bc_match}, ENE match: {ene_match}")
                        print(f"  PT: {pt}")
                        print(f"  Score: {score:.4f}")
                        results.append((score, source_name, alpha_name, variant, offset, pt))
                    
                    # Also check partial matches
                    if pt[63:69] == "BERLIN" or pt[21:34] == "EASTNORTHEAST":
                        score = score_quadgrams(pt)
                        if (score, source_name, alpha_name, variant, offset, pt) not in results:
                            print(f"\n  Partial match: {source_name} off={offset} {alpha_name} {variant}")
                            print(f"  PT[21:34]={pt[21:34]}  PT[63:74]={pt[63:74]}")
                            if score > -6.0:
                                print(f"  Full PT: {pt}")
                            results.append((score, source_name, alpha_name, variant, offset, pt))
    
    if not results:
        print("\n  No crib matches found with known text sources as running key.")
    
    return results

# ============================================================
# TEST 5: Weltzeituhr city names as running key
# ============================================================

def test5_weltzeituhr():
    """Test Berlin World Time Clock city names as running key source."""
    print("\n" + "=" * 80)
    print("TEST 5: WELTZEITUHR (BERLIN WORLD TIME CLOCK) AS KEY SOURCE")
    print("=" * 80)
    
    # Generate various orderings of city names
    key_streams = {}
    
    # Concatenate all cities in order
    key_streams["Cities in order"] = ''.join(WELTZEITUHR_CITIES)
    key_streams["Cities (German) in order"] = ''.join(WELTZEITUHR_CITIES_ALT)
    
    # Reverse order
    key_streams["Cities reversed"] = ''.join(reversed(WELTZEITUHR_CITIES))
    
    # Starting from different cities (rotate)
    for start_idx in range(24):
        rotated = WELTZEITUHR_CITIES[start_idx:] + WELTZEITUHR_CITIES[:start_idx]
        key_name = f"Starting from {WELTZEITUHR_CITIES[start_idx]}"
        key_streams[key_name] = ''.join(rotated)
    
    # Just the first letters
    key_streams["First letters only"] = ''.join(c[0] for c in WELTZEITUHR_CITIES) * 5
    
    # City names with spaces removed, repeated to cover K4 length
    all_cities = ''.join(WELTZEITUHR_CITIES)
    key_streams["Cities repeated"] = (all_cities * 3)[:200]
    
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    results = []
    
    for key_name, key_source in key_streams.items():
        key_alpha = ''.join(c for c in key_source.upper() if c.isalpha())
        
        for alpha_name, alpha in alphabets:
            for variant in variants:
                # Test various offsets within the key source
                max_off = max(0, len(key_alpha) - len(K4))
                
                for offset in range(min(max_off + 1, 200)):
                    key = key_alpha[offset:offset + len(K4)]
                    if len(key) < len(K4):
                        # Wrap
                        wrapped = (key_alpha * 5)
                        key = wrapped[offset:offset + len(K4)]
                        if len(key) < len(K4):
                            continue
                    
                    pt = decrypt_with_running_key(K4, key, alpha, variant)
                    
                    # Check cribs
                    bc_match = (pt[63:74] == "BERLINCLOCK")
                    ene_match = (pt[21:34] == "EASTNORTHEAST")
                    
                    if bc_match or ene_match:
                        score = score_quadgrams(pt)
                        print(f"\n  *** CRIB MATCH ***")
                        print(f"  Key: {key_name}, Offset: {offset}")
                        print(f"  Alpha: {alpha_name}, Variant: {variant}")
                        print(f"  PT: {pt}")
                        results.append((score, key_name, alpha_name, variant, offset, pt))
                    
                    # Check general quality
                    score = score_quadgrams(pt)
                    if score > -6.5:
                        results.append((score, key_name, alpha_name, variant, offset, pt))
    
    # Now check: does the derived key at crib positions match any Weltzeituhr patterns?
    print("\n--- Checking if derived key fragments match Weltzeituhr city names ---")
    
    for alpha_name, alpha in alphabets:
        for variant in variants:
            key_ene = derive_key_at_crib(K4, "EASTNORTHEAST", 21, alpha, variant)
            key_bc = derive_key_at_crib(K4, "BERLINCLOCK", 63, alpha, variant)
            
            # Check if these key fragments appear in any city name concatenation
            for key_name, key_source in key_streams.items():
                key_alpha = ''.join(c for c in key_source.upper() if c.isalpha())
                
                # Check if key_ene appears in the stream
                if key_ene in key_alpha:
                    pos = key_alpha.index(key_ene)
                    print(f"  ENE key '{key_ene}' found in '{key_name}' at position {pos}")
                    print(f"    Alpha: {alpha_name}, Variant: {variant}")
                    # If found, check what the full key would be
                    full_key_start = pos - 21
                    if full_key_start >= 0:
                        full_key = key_alpha[full_key_start:full_key_start + len(K4)]
                        if len(full_key) == len(K4):
                            pt = decrypt_with_running_key(K4, full_key, alpha, variant)
                            print(f"    Full PT: {pt}")
                            results.append((score_quadgrams(pt), key_name, alpha_name, variant, full_key_start, pt))
                
                if key_bc in key_alpha:
                    pos = key_alpha.index(key_bc)
                    print(f"  BC key '{key_bc}' found in '{key_name}' at position {pos}")
                    print(f"    Alpha: {alpha_name}, Variant: {variant}")
                    full_key_start = pos - 63
                    if full_key_start >= 0:
                        full_key = key_alpha[full_key_start:full_key_start + len(K4)]
                        if len(full_key) == len(K4):
                            pt = decrypt_with_running_key(K4, full_key, alpha, variant)
                            print(f"    Full PT: {pt}")
                            results.append((score_quadgrams(pt), key_name, alpha_name, variant, full_key_start, pt))
                
                # Also check substrings
                for sub_len in range(5, min(len(key_ene), len(key_bc)) + 1):
                    for sub_start in range(len(key_ene) - sub_len + 1):
                        sub = key_ene[sub_start:sub_start + sub_len]
                        if sub in key_alpha and sub_len >= 6:
                            print(f"  ENE key substr '{sub}' ({alpha_name}/{variant}) found in '{key_name}'")
                    for sub_start in range(len(key_bc) - sub_len + 1):
                        sub = key_bc[sub_start:sub_start + sub_len]
                        if sub in key_alpha and sub_len >= 6:
                            print(f"  BC key substr '{sub}' ({alpha_name}/{variant}) found in '{key_name}'")
    
    if results:
        print("\n--- TOP WELTZEITUHR RESULTS ---")
        results.sort(key=lambda x: x[0], reverse=True)
        for score, kn, an, var, off, pt in results[:10]:
            print(f"  score={score:.4f} {kn:30s} {an:8s} {var:18s} off={off}")
            print(f"    {pt[:60]}...")
    else:
        print("\n  No significant matches found with Weltzeituhr keys.")
    
    return results

# ============================================================
# TEST 6: Comprehensive English-key brute force at crib positions
# ============================================================

def test6_deep_crib_analysis():
    """Deep analysis of what the running key must be if it's English text."""
    print("\n" + "=" * 80)
    print("TEST 6: DEEP ANALYSIS - IS THE RUNNING KEY ENGLISH TEXT?")
    print("=" * 80)
    
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    # Typical English text quadgram score is around -2.3 to -2.5
    # Random text is around -4.5 to -5.0
    
    print("\nReference scores:")
    ref_texts = {
        "THEUNITEDSTATESOFAMERICA": "English phrase",
        "BETWEENSUBTLESHADINGAND": "K1 start",
        "SLOWLYDESPERATELYSLOWLY": "K3 start",
        "XZQJWKBPFMVYLGHTNDCRUSA": "Random-ish",
    }
    for text, desc in ref_texts.items():
        print(f"  {text:30s} ({desc:15s}): {score_quadgrams(text):.4f}")
    
    print("\nDerived key fragments and their English-likeness:")
    
    summary = []
    
    for alpha_name, alpha in alphabets:
        for variant in variants:
            key_ene = derive_key_at_crib(K4, "EASTNORTHEAST", 21, alpha, variant)
            key_bc = derive_key_at_crib(K4, "BERLINCLOCK", 63, alpha, variant)
            
            ene_score = score_quadgrams(key_ene)
            bc_score = score_quadgrams(key_bc)
            avg_score = (ene_score + bc_score) / 2
            
            ene_words = find_words_in_text(key_ene, 3)
            bc_words = find_words_in_text(key_bc, 3)
            ene_cov = find_word_coverage(key_ene, 3)
            bc_cov = find_word_coverage(key_bc, 3)
            
            english_like = "YES" if avg_score > -3.5 else ("MAYBE" if avg_score > -4.5 else "NO")
            
            summary.append((avg_score, alpha_name, variant, key_ene, key_bc, 
                           ene_score, bc_score, ene_cov, bc_cov,
                           ene_words, bc_words, english_like))
    
    summary.sort(key=lambda x: x[0], reverse=True)
    
    for avg, an, var, ke, kb, es, bs, ec, bc, ew, bw, el in summary:
        print(f"\n  {an:8s} {var:18s}  avg_score={avg:.4f}  English-like: {el}")
        print(f"    ENE key: {ke}  score={es:.4f}  word_coverage={ec:.1%}")
        if ew:
            print(f"      Words: {[(w, p) for p, w in ew[:8]]}")
        print(f"    BC key:  {kb}  score={bs:.4f}  word_coverage={bc:.1%}")
        if bw:
            print(f"      Words: {[(w, p) for p, w in bw[:8]]}")
    
    # Highlight the best candidate
    best = summary[0]
    print(f"\n  BEST CANDIDATE: {best[1]} {best[2]}")
    print(f"    ENE key fragment: {best[3]}")
    print(f"    BC key fragment:  {best[4]}")
    print(f"    Average quadgram score: {best[0]:.4f}")
    print(f"    Assessment: {'Key fragments LOOK like English' if best[0] > -3.5 else 'Key fragments do NOT clearly look like English'}")
    
    return summary

# ============================================================
# TEST 7: Try constructing the full key by hill-climbing
# ============================================================

def test7_hill_climb():
    """Hill-climbing approach: optimize key to maximize English quality of both PT and key."""
    print("\n" + "=" * 80)
    print("TEST 7: HILL-CLIMBING KEY RECOVERY")
    print("=" * 80)
    
    import random
    random.seed(42)
    
    # Use standard alphabet, Vigenere (most common)
    # But also test the best combo from Test 6
    
    configs = [
        ("STANDARD", STANDARD_ALPHA, "vigenere"),
        ("STANDARD", STANDARD_ALPHA, "beaufort"),
        ("KRYPTOS", KRYPTOS_ALPHA, "vigenere"),
        ("KRYPTOS", KRYPTOS_ALPHA, "beaufort"),
    ]
    
    for alpha_name, alpha, variant in configs:
        print(f"\n--- Hill-climbing: {alpha_name} {variant} ---")
        
        # Initialize key with derived values at crib positions
        key_ene = derive_key_at_crib(K4, "EASTNORTHEAST", 21, alpha, variant)
        key_bc = derive_key_at_crib(K4, "BERLINCLOCK", 63, alpha, variant)
        
        # Start with random key, fixing known positions
        best_key = list(alpha[random.randint(0, 25)] for _ in range(len(K4)))
        
        # Fix known positions
        for i, ch in enumerate(key_ene):
            best_key[21 + i] = ch
        for i, ch in enumerate(key_bc):
            best_key[63 + i] = ch
        
        fixed_positions = set(range(21, 34)) | set(range(63, 74))
        
        def evaluate(key_list):
            key_str = ''.join(key_list)
            pt = decrypt_with_running_key(K4, key_str, alpha, variant)
            pt_score = score_quadgrams(pt)
            key_score = score_quadgrams(key_str)
            # Weight: both plaintext and key should be English-like
            return pt_score * 0.6 + key_score * 0.4
        
        best_score = evaluate(best_key)
        
        # Hill climbing
        iterations = 50000
        no_improve = 0
        temperature = 1.0
        
        for iteration in range(iterations):
            # Pick a random non-fixed position
            pos = random.randint(0, len(K4) - 1)
            while pos in fixed_positions:
                pos = random.randint(0, len(K4) - 1)
            
            # Try a different character
            old_char = best_key[pos]
            new_char = alpha[random.randint(0, 25)]
            if new_char == old_char:
                continue
            
            best_key[pos] = new_char
            new_score = evaluate(best_key)
            
            # Accept if better, or with probability based on temperature
            diff = new_score - best_score
            if diff > 0 or random.random() < math.exp(diff / temperature):
                best_score = new_score
                no_improve = 0
            else:
                best_key[pos] = old_char
                no_improve += 1
            
            # Cool down
            temperature *= 0.99999
            
            if iteration % 10000 == 0:
                key_str = ''.join(best_key)
                pt = decrypt_with_running_key(K4, key_str, alpha, variant)
                print(f"  Iter {iteration:6d}: score={best_score:.4f}  temp={temperature:.4f}")
                print(f"    PT:  {pt[:50]}...")
                print(f"    Key: {key_str[:50]}...")
        
        # Final result
        key_str = ''.join(best_key)
        pt = decrypt_with_running_key(K4, key_str, alpha, variant)
        final_score = score_quadgrams(pt)
        key_score = score_quadgrams(key_str)
        
        print(f"\n  Final result:")
        print(f"    PT:  {pt}")
        print(f"    Key: {key_str}")
        print(f"    PT score:  {final_score:.4f}")
        print(f"    Key score: {key_score:.4f}")
        
        # Find words in PT and key
        pt_words = find_words_in_text(pt, 4)
        key_words = find_words_in_text(key_str, 4)
        if pt_words:
            print(f"    PT words: {[(w, p) for p, w in pt_words[:10]]}")
        if key_words:
            print(f"    Key words: {[(w, p) for p, w in key_words[:10]]}")

# ============================================================
# TEST 8: Verify crib positions and basic sanity checks
# ============================================================

def test8_sanity_checks():
    """Verify all cribs and sanity check the setup."""
    print("\n" + "=" * 80)
    print("TEST 8: SANITY CHECKS AND CRIB VERIFICATION")
    print("=" * 80)
    
    print(f"\nK4 ciphertext ({len(K4)} chars):")
    # Print with position markers
    for i in range(0, len(K4), 10):
        chunk = K4[i:i+10]
        print(f"  {i:3d}-{i+len(chunk)-1:3d}: {chunk}")
    
    print(f"\nCrib positions:")
    for crib, (start, end) in CRIBS.items():
        ct_at_pos = K4[start:start+len(crib)]
        print(f"  {crib} at positions {start}-{start+len(crib)-1}")
        print(f"    CT: {ct_at_pos}")
        print(f"    PT: {crib}")
    
    print(f"\nAlphabet verification:")
    print(f"  STANDARD: {STANDARD_ALPHA} ({len(STANDARD_ALPHA)} chars)")
    print(f"  KRYPTOS:  {KRYPTOS_ALPHA} ({len(KRYPTOS_ALPHA)} chars)")
    assert len(set(STANDARD_ALPHA)) == 26, "Standard alphabet not 26 unique chars"
    assert len(set(KRYPTOS_ALPHA)) == 26, "Kryptos alphabet not 26 unique chars"
    assert len(STANDARD_ALPHA) == 26
    assert len(KRYPTOS_ALPHA) == 26
    print("  Both alphabets verified: 26 unique characters each.")
    
    # Verify Vigenere: encrypt then decrypt should give back original
    print(f"\nVigenere self-test:")
    for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
        for variant in ["vigenere", "beaufort", "variant_beaufort"]:
            test_pt = "TESTPLAINTEXT"
            test_key = "SOMEKEYVALUE"
            # Encrypt
            ct = ""
            for i in range(len(test_pt)):
                pt_idx = alpha_index(test_pt[i], alpha)
                key_idx = alpha_index(test_key[i % len(test_key)], alpha)
                if variant == "vigenere":
                    ct_idx = (pt_idx + key_idx) % 26
                elif variant == "beaufort":
                    ct_idx = (key_idx - pt_idx) % 26
                elif variant == "variant_beaufort":
                    ct_idx = (pt_idx - key_idx) % 26
                ct += alpha_char(ct_idx, alpha)
            
            # Decrypt
            recovered = decrypt_with_running_key(ct, test_key, alpha, variant)
            match = "PASS" if recovered == test_pt else "FAIL"
            print(f"  {alpha_name:8s} {variant:18s}: {match}")
            if match == "FAIL":
                print(f"    Original: {test_pt}")
                print(f"    Recovered: {recovered}")
    
    # Verify key derivation roundtrip
    print(f"\nKey derivation roundtrip test:")
    for alpha_name, alpha in [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]:
        for variant in ["vigenere", "beaufort", "variant_beaufort"]:
            for crib, (start, end) in CRIBS.items():
                key = derive_key_at_crib(K4, crib, start, alpha, variant)
                # Using the derived key, decrypt should give back the crib
                ct_at_pos = K4[start:start+len(crib)]
                recovered = decrypt_with_running_key(ct_at_pos, key, alpha, variant)
                match = "PASS" if recovered == crib else "FAIL"
                if match == "FAIL":
                    print(f"  {alpha_name:8s} {variant:18s} {crib:15s}: {match}")
                    print(f"    Key: {key}")
                    print(f"    Expected: {crib}")
                    print(f"    Got:      {recovered}")
    print("  All key derivation roundtrips passed (failures shown above if any).")

# ============================================================
# TEST 9: Dictionary-based key search
# ============================================================

def test9_dictionary_key():
    """Try common English phrases/sentences as running key."""
    print("\n" + "=" * 80)
    print("TEST 9: DICTIONARY PHRASE SEARCH AS KEY")
    print("=" * 80)
    
    # If the key is English text of 97 chars, that's roughly 20 words
    # We can try to find what word starts the key at various positions
    
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    # Get words of length 4+ for efficiency
    word_list = sorted([w for w in WORDS if len(w) >= 4], key=len, reverse=True)
    
    for alpha_name, alpha in alphabets:
        for variant in variants:
            # Derive key at crib positions
            key_ene = derive_key_at_crib(K4, "EASTNORTHEAST", 21, alpha, variant)
            key_bc = derive_key_at_crib(K4, "BERLINCLOCK", 63, alpha, variant)
            
            # Try to find what word the key fragment at ENE could be part of
            # key_ene starts at key position 21
            # If a word starts at position X in the key, and X <= 21, and X + len(word) > 21
            # then the word contains key_ene[0:?]
            
            print(f"\n--- {alpha_name} {variant} ---")
            print(f"  Key@21-33: {key_ene}")
            print(f"  Key@63-73: {key_bc}")
            
            # Search for words that START with beginning of key_ene
            for prefix_len in range(4, len(key_ene) + 1):
                prefix = key_ene[:prefix_len]
                matches = [w for w in word_list if w.startswith(prefix)]
                if matches and len(matches) <= 5:
                    print(f"    Words starting with '{prefix}': {matches}")
            
            # Search for words that END with end of key_ene
            for suffix_len in range(4, len(key_ene) + 1):
                suffix = key_ene[-suffix_len:]
                matches = [w for w in word_list if w.endswith(suffix)]
                if matches and len(matches) <= 5:
                    print(f"    Words ending with '{suffix}': {matches}")
            
            # Search for words that CONTAIN key_ene substrings
            for sub_len in range(5, len(key_ene) + 1):
                for start in range(len(key_ene) - sub_len + 1):
                    sub = key_ene[start:start + sub_len]
                    matches = [w for w in word_list if sub in w]
                    if matches and len(matches) <= 3:
                        print(f"    Words containing '{sub}' (key pos {21+start}-{21+start+sub_len-1}): {matches}")
            
            # Same for BC key
            for prefix_len in range(4, len(key_bc) + 1):
                prefix = key_bc[:prefix_len]
                matches = [w for w in word_list if w.startswith(prefix)]
                if matches and len(matches) <= 5:
                    print(f"    Words starting with '{prefix}' (BC): {matches}")
            
            for suffix_len in range(4, len(key_bc) + 1):
                suffix = key_bc[-suffix_len:]
                matches = [w for w in word_list if w.endswith(suffix)]
                if matches and len(matches) <= 5:
                    print(f"    Words ending with '{suffix}' (BC): {matches}")
            
            for sub_len in range(5, len(key_bc) + 1):
                for start in range(len(key_bc) - sub_len + 1):
                    sub = key_bc[start:start + sub_len]
                    matches = [w for w in word_list if sub in w]
                    if matches and len(matches) <= 3:
                        print(f"    Words containing '{sub}' (BC key pos {63+start}-{63+start+sub_len-1}): {matches}")

# ============================================================
# BONUS: Test Bonifacino's specific 86-letter claim
# ============================================================

def test_bonifacino_86():
    """Test the specific claim of an 86-letter running key from Weltzeituhr."""
    print("\n" + "=" * 80)
    print("BONUS: BONIFACINO'S 86-LETTER WELTZEITUHR KEY CLAIM")
    print("=" * 80)
    
    print(f"\nK4 has {len(K4)} characters. An 86-letter key would leave {len(K4) - 86} characters unkeyed.")
    print("This might mean:")
    print("  - The first 86 chars are encrypted, last 11 are plaintext")
    print("  - The last 86 chars are encrypted, first 11 are plaintext")  
    print("  - Or some other arrangement")
    
    # Construct 86-letter keys from Weltzeituhr cities
    all_cities = ''.join(WELTZEITUHR_CITIES)
    all_cities_alt = ''.join(WELTZEITUHR_CITIES_ALT)
    
    print(f"\nAll Weltzeituhr cities concatenated: {len(all_cities)} chars")
    print(f"  {all_cities}")
    print(f"\nAll Weltzeituhr cities (German names): {len(all_cities_alt)} chars")
    print(f"  {all_cities_alt}")
    
    # Try taking exactly 86 characters from various offsets
    alphabets = [("STANDARD", STANDARD_ALPHA), ("KRYPTOS", KRYPTOS_ALPHA)]
    variants = ["vigenere", "beaufort", "variant_beaufort"]
    
    for city_set_name, city_str in [("International", all_cities), ("German", all_cities_alt)]:
        for alpha_name, alpha in alphabets:
            for variant in variants:
                for offset in range(len(city_str)):
                    # Take 86 chars starting at offset (with wrap)
                    key86 = (city_str * 3)[offset:offset + 86]
                    if len(key86) < 86:
                        continue
                    
                    # Try key for first 86 chars of K4
                    pt = decrypt_with_running_key(K4[:86], key86, alpha, variant)
                    # Append last 11 chars as-is (if they're plaintext)
                    pt_full = pt + K4[86:]
                    
                    if "BERLINCLOCK" in pt or "EASTNORTHEAST" in pt:
                        score = score_quadgrams(pt)
                        print(f"\n  MATCH! {city_set_name} off={offset} {alpha_name} {variant}")
                        print(f"  Key: {key86}")
                        print(f"  PT:  {pt_full}")
                    
                    # Try key for last 86 chars
                    pt_last = decrypt_with_running_key(K4[11:], key86[:86], alpha, variant)
                    pt_full2 = K4[:11] + pt_last
                    
                    if "BERLINCLOCK" in pt_last or "EASTNORTHEAST" in pt_last:
                        score = score_quadgrams(pt_last)
                        print(f"\n  MATCH (last 86)! {city_set_name} off={offset} {alpha_name} {variant}")
                        print(f"  PT: {pt_full2}")
    
    # Also: maybe 86 is the total length of some subset of cities
    # Find subsets that sum to exactly 86 letters
    print("\n--- Finding city subsets that total exactly 86 letters ---")
    city_lengths = [(c, len(c)) for c in WELTZEITUHR_CITIES]
    print(f"  City lengths: {city_lengths}")
    total_all = sum(len(c) for c in WELTZEITUHR_CITIES)
    print(f"  Total of all cities: {total_all}")
    
    # Check which cities to exclude to get 86
    needed_exclusion = total_all - 86
    print(f"  Need to exclude {needed_exclusion} chars worth of cities")
    
    # Try single city exclusion
    for city in WELTZEITUHR_CITIES:
        if len(city) == needed_exclusion:
            print(f"    Excluding '{city}' ({len(city)} chars) gives exactly 86!")
    
    # Try two-city exclusion
    for i, c1 in enumerate(WELTZEITUHR_CITIES):
        for j, c2 in enumerate(WELTZEITUHR_CITIES):
            if j <= i:
                continue
            if len(c1) + len(c2) == needed_exclusion:
                remaining = [c for k, c in enumerate(WELTZEITUHR_CITIES) if k != i and k != j]
                key86 = ''.join(remaining)
                print(f"    Excluding '{c1}' + '{c2}' = {len(c1)+len(c2)} chars gives {len(key86)} chars")
                if len(key86) == 86:
                    print(f"      Key: {key86[:50]}...")

# ============================================================
# MAIN
# ============================================================

def main():
    print("KRYPTOS K4 RUNNING KEY CIPHER ANALYSIS")
    print("=" * 80)
    print(f"K4 ciphertext: {K4}")
    print(f"Length: {len(K4)}")
    print()
    
    # Run sanity checks first
    test8_sanity_checks()
    
    # Test 1: Derive key at crib positions
    test1_results = test1_derive_key_at_cribs()
    
    # Test 6: Deep analysis of key English-likeness
    test6_results = test6_deep_crib_analysis()
    
    # Test 9: Dictionary key search
    test9_dictionary_key()
    
    # Test 2: Known text sources
    test2_results = test2_known_text_sources()
    
    # Test 4: Alignment search
    test4_results = test4_alignment_search()
    
    # Test 5: Weltzeituhr
    test5_results = test5_weltzeituhr()
    
    # Test Bonifacino's 86-letter claim
    test_bonifacino_86()
    
    # Test 3: Crib dragging
    test3_results = test3_crib_dragging()
    
    # Test 7: Hill climbing (this is slower)
    test7_hill_climb()
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    
    print("""
KEY FINDINGS:
=============

1. DERIVED KEY FRAGMENTS AT CRIB POSITIONS:
   These are the key values that MUST be correct if K4 uses a running key cipher
   with the given cribs. The question is whether these fragments are English text.

2. KEY ENGLISH-LIKENESS:
   If the running key is English text (as in a book cipher / running key cipher),
   the derived fragments should score well on quadgram analysis and contain
   recognizable English words.

3. KNOWN TEXT SOURCES:
   None of the tested known text sources (K1/K2/K3 plaintexts, coordinates, 
   Carter text) produce both cribs at the expected positions when used as a 
   running key - unless a match was found (reported above).

4. WELTZEITUHR:
   The Berlin World Time Clock city names were tested in various orderings
   and offsets. Results reported above.

5. BONIFACINO'S 86-LETTER CLAIM:
   Analysis of how 86 letters could be derived from Weltzeituhr cities.

NOTE: A running key cipher makes frequency analysis useless (matching Scheidt's
hint about a "masking technique"), but requires the key to be as long as the
message. The key must come from a pre-agreed text source.
""")

if __name__ == "__main__":
    main()
