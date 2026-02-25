#!/usr/bin/env python3
"""
K4 Duress Cipher Analysis

Ed Scheidt's interest in "duress ciphers" - multi-layered ciphers where you can 
give up one key that produces credible-looking plaintext without revealing the real message.

HYPOTHESIS: K4 has TWO valid decryptions:
- Layer 1 key produces one plaintext (the "BERLINCLOCK" message)
- Layer 2 key produces a different, hidden plaintext

Tests:
1. Double Vigenère (two passes)
2. Vigenère + position-dependent Caesar
3. Vigenère + XOR-like operations  
4. Split cipher (different methods for different sections)
5. Key derivation from cribs
"""

import sys
import time
from collections import Counter
from itertools import product

# ============================================================
# CONSTANTS
# ============================================================

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
K4_LEN = len(K4)  # 97

# Period-29 Vigenère partial decryption
DECRYPTED_P29 = "UDAYUQAPBZDBKZELNORTHEASTLGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGBBERLINCLOCKRSPVJWQULABOVEJYBUKCAYF"

# Known cribs and positions in the period-29 decryption
CRIBS = {
    "BERLINCLOCK": (64, 75),     # positions 64-74 inclusive
    "EASTNORTHEAST": (13, 26),   # "NORTHEAST" at 17-25, but EASTNORTHEAST potentially 13-25
    "NORTHEAST": (17, 26),
}

# Period-29 key (partially known)
# From NORTHEAST at pos 17-25 and BERLINCLOCK at pos 64-74
# key positions are pos % 29
P29_KEY = ['?'] * 29

# K1-K3 data for cross-referencing
K1_CT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_PT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUA NCEOFIQLUSION"
# Clean K1_PT
K1_PT = K1_PT.replace(" ", "")

K2_CT = "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEBEDMHDAFMJGZNUPLGESWJLLAETG"
K2_PT_RAW = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHISTHEYSHOULDITSBURIED OUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLASTMESSAGEXTHIRTYEIGHTDEGRESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVENDEGRESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
K2_PT = K2_PT_RAW.replace(" ", "")

K3_PT = "SLOWLYDESPARATLYSLOWTHEREMAINSOFPASSAGEDEBRRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREM BLINGHANDSIMADETINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINTHEHOLEALITTLEIINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERC AUSEDTHEFLAMETOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
K3_PT = K3_PT.replace(" ", "")

# ============================================================
# WORD LIST LOADING
# ============================================================

def load_words(filepath="/home/user/polyalphabetic/OxfordEnglishWords.txt"):
    """Load word list and create lookup structures."""
    words = set()
    with open(filepath, 'r') as f:
        for line in f:
            w = line.strip().upper()
            if len(w) >= 2:
                words.add(w)
    return words

print("Loading word list...")
WORD_SET = load_words()
# Pre-build sets by length for faster lookups
WORDS_BY_LEN = {}
for w in WORD_SET:
    l = len(w)
    if l not in WORDS_BY_LEN:
        WORDS_BY_LEN[l] = set()
    WORDS_BY_LEN[l].add(w)

# ============================================================
# CIPHER OPERATIONS (KRYPTOS ALPHABET)
# ============================================================

def k_index(c, alpha=KRYPTOS_ALPHA):
    """Get index of character in KRYPTOS alphabet."""
    return alpha.index(c)

def k_char(i, alpha=KRYPTOS_ALPHA):
    """Get character at index in KRYPTOS alphabet."""
    return alpha[i % len(alpha)]

def vig_decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Vigenère decrypt: pt = (ct - key) mod 26 in given alphabet."""
    ct_i = alpha.index(ct_char)
    k_i = alpha.index(key_char)
    return alpha[(ct_i - k_i) % len(alpha)]

def vig_encrypt_char(pt_char, key_char, alpha=KRYPTOS_ALPHA):
    """Vigenère encrypt: ct = (pt + key) mod 26 in given alphabet."""
    pt_i = alpha.index(pt_char)
    k_i = alpha.index(key_char)
    return alpha[(pt_i + k_i) % len(alpha)]

def beaufort_decrypt_char(ct_char, key_char, alpha=KRYPTOS_ALPHA):
    """Beaufort decrypt: pt = (key - ct) mod 26 in given alphabet."""
    ct_i = alpha.index(ct_char)
    k_i = alpha.index(key_char)
    return alpha[(k_i - ct_i) % len(alpha)]

def vig_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Full Vigenère decryption with repeating key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(vig_decrypt_char(c, k, alpha))
    return ''.join(result)

def vig_encrypt(pt, key, alpha=KRYPTOS_ALPHA):
    """Full Vigenère encryption with repeating key."""
    result = []
    for i, c in enumerate(pt):
        k = key[i % len(key)]
        result.append(vig_encrypt_char(c, k, alpha))
    return ''.join(result)

def beaufort_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    """Full Beaufort decryption with repeating key."""
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(beaufort_decrypt_char(c, k, alpha))
    return ''.join(result)

# Also support standard alphabet operations
def std_vig_decrypt_char(ct_char, key_char):
    return STANDARD_ALPHA[(STANDARD_ALPHA.index(ct_char) - STANDARD_ALPHA.index(key_char)) % 26]

def std_vig_decrypt(ct, key):
    result = []
    for i, c in enumerate(ct):
        k = key[i % len(key)]
        result.append(std_vig_decrypt_char(c, k))
    return ''.join(result)

# ============================================================
# SCORING
# ============================================================

# English letter frequencies
ENG_FREQ = {'A': 8.2, 'B': 1.5, 'C': 2.8, 'D': 4.3, 'E': 12.7, 'F': 2.2,
            'G': 2.0, 'H': 6.1, 'I': 7.0, 'J': 0.15, 'K': 0.8, 'L': 4.0,
            'M': 2.4, 'N': 6.7, 'O': 7.5, 'P': 1.9, 'Q': 0.10, 'R': 6.0,
            'S': 6.3, 'T': 9.1, 'U': 2.8, 'V': 1.0, 'W': 2.4, 'X': 0.15,
            'Y': 2.0, 'Z': 0.07}

# Common English bigrams
COMMON_BIGRAMS = set(['TH', 'HE', 'IN', 'ER', 'AN', 'RE', 'ON', 'AT', 'EN', 'ND',
                      'TI', 'ES', 'OR', 'TE', 'OF', 'ED', 'IS', 'IT', 'AL', 'AR',
                      'ST', 'TO', 'NT', 'NG', 'SE', 'HA', 'AS', 'OU', 'IO', 'LE',
                      'VE', 'CO', 'ME', 'DE', 'HI', 'RI', 'RO', 'IC', 'NE', 'EA',
                      'RA', 'CE', 'LI', 'CH', 'LL', 'BE', 'MA', 'SI', 'OM', 'UR'])

def score_english(text):
    """Score text for English-likeness. Higher is better."""
    if not text:
        return -9999
    
    score = 0.0
    text = text.upper()
    n = len(text)
    
    # 1. Word detection (biggest signal)
    word_chars = 0
    for wlen in range(8, 1, -1):  # Check longer words first
        if wlen not in WORDS_BY_LEN:
            continue
        for start in range(n - wlen + 1):
            substr = text[start:start + wlen]
            if substr in WORDS_BY_LEN[wlen]:
                word_chars += wlen
                score += wlen * wlen  # Quadratic bonus for word length
    
    # 2. Bigram frequency
    bigram_count = 0
    for i in range(n - 1):
        bg = text[i:i+2]
        if bg in COMMON_BIGRAMS:
            bigram_count += 1
    score += bigram_count * 3
    
    # 3. Letter frequency correlation
    freq = Counter(text)
    chi_sq = 0
    for letter in STANDARD_ALPHA:
        observed = freq.get(letter, 0) / n * 100
        expected = ENG_FREQ.get(letter, 0)
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected
    # Lower chi-squared is better, so subtract
    score -= chi_sq * 0.3
    
    # 4. Penalize rare letters heavily
    for rare in ['Q', 'X', 'Z', 'J']:
        score -= freq.get(rare, 0) * 4
    
    # 5. Consecutive consonant penalty
    vowels = set('AEIOU')
    max_consonants = 0
    current_consonants = 0
    for c in text:
        if c not in vowels:
            current_consonants += 1
            max_consonants = max(max_consonants, current_consonants)
        else:
            current_consonants = 0
    if max_consonants > 4:
        score -= (max_consonants - 4) * 5
    
    return score

# ============================================================
# DERIVE PERIOD-29 KEY
# ============================================================

def derive_p29_key():
    """Derive the period-29 key from known cribs."""
    key = ['?'] * 29
    
    # NORTHEAST at positions 17-25 in plaintext
    crib_ne = "NORTHEAST"
    for i, (p, c) in enumerate(zip(crib_ne, K4[17:26])):
        # key_char = ct - pt in KRYPTOS alphabet
        k_pos = (17 + i) % 29
        k_i = (KRYPTOS_ALPHA.index(c) - KRYPTOS_ALPHA.index(p)) % 26
        key[k_pos] = KRYPTOS_ALPHA[k_i]
    
    # BERLINCLOCK at positions 64-74 in plaintext
    crib_bc = "BERLINCLOCK"
    for i, (p, c) in enumerate(zip(crib_bc, K4[64:75])):
        k_pos = (64 + i) % 29
        k_i = (KRYPTOS_ALPHA.index(c) - KRYPTOS_ALPHA.index(p)) % 26
        key[k_pos] = KRYPTOS_ALPHA[k_i]
    
    return key

P29_KEY = derive_p29_key()
print(f"Period-29 key: {''.join(P29_KEY)}")

# Determine which key positions are known vs unknown
KNOWN_KEY_POS = set()
UNKNOWN_KEY_POS = set()
for i, k in enumerate(P29_KEY):
    if k != '?':
        KNOWN_KEY_POS.add(i)
    else:
        UNKNOWN_KEY_POS.add(i)

print(f"Known key positions: {sorted(KNOWN_KEY_POS)} ({len(KNOWN_KEY_POS)} of 29)")
print(f"Unknown key positions: {sorted(UNKNOWN_KEY_POS)} ({len(UNKNOWN_KEY_POS)} of 29)")

# Full decryption with partial key
def decrypt_p29_partial():
    """Decrypt K4 with the partial period-29 key."""
    result = []
    for i, c in enumerate(K4):
        k = P29_KEY[i % 29]
        if k == '?':
            result.append('?')
        else:
            result.append(vig_decrypt_char(c, k))
    return ''.join(result)

partial_dec = decrypt_p29_partial()
print(f"\nPartial P29 decryption: {partial_dec}")

# ============================================================
# RESULTS COLLECTION
# ============================================================

all_results = []  # (score, description, plaintext)

def record_result(score, description, plaintext):
    """Record a result for final ranking."""
    all_results.append((score, description, plaintext))

# ============================================================
# TEST 1: DOUBLE VIGENÈRE
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: DOUBLE VIGENÈRE")
print("=" * 70)

def test_double_vigenere():
    """
    Test: Vigenère(period 29) followed by Vigenère(period P)
    For the second layer, we derive what the key must be at crib positions,
    then check if remaining positions give English.
    """
    results = []
    
    # For each second period P
    for P2 in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        # The idea: the "real" plaintext went through TWO Vigenère encryptions
        # First with period P2, then with period 29 (or vice versa)
        # We know the period-29 decryption gives BERLINCLOCK/NORTHEAST
        # What if that's the "duress" plaintext, and the real one is hidden?
        
        # Approach: The period-29 decryption = intermediate text
        # intermediate = Vig_P2(real_plaintext)
        # So: real_plaintext = Vig_P2_decrypt(intermediate)
        # We need to find the P2 key
        
        # Use BERLINCLOCK and NORTHEAST positions to extract key2
        # At crib positions, intermediate text is known
        # If we assume the real plaintext has OTHER English words there,
        # we can try common words
        
        # Simpler approach: try all possible single-character keys for period P2
        # (effectively Caesar on period-P2 groups)
        
        # For small periods, try all key combinations using KRYPTOS alphabet
        if P2 <= 5:
            # Try random keys - for P2 <= 3, exhaustive; for P2=4,5 sample
            max_keys = 26 ** P2
            if max_keys > 50000:
                # Sample: try keys derived from known words
                continue
            
            for key_tuple in product(range(26), repeat=P2):
                key2 = ''.join(KRYPTOS_ALPHA[k] for k in key_tuple)
                # Decrypt the intermediate (DECRYPTED_P29) with this second key
                pt = vig_decrypt(DECRYPTED_P29, key2, KRYPTOS_ALPHA)
                sc = score_english(pt)
                if sc > 30:
                    results.append((sc, f"DoubleVig P29+P{P2} key2={key2}", pt))
        
        # For larger periods, use crib-guided approach
        # Extract what key2 would need to be at BERLINCLOCK positions
        # if the "real" plaintext had common words there
        
        # Also try: key2 derived from BERLINCLOCK or EASTNORTHEAST themselves
        for keyword in ["BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST", "KRYPTOS", 
                        "PALIMPSEST", "ABSCISSA", "CLOCK", "BERLIN", "SHADOW",
                        "LAYER", "HIDDEN", "SECRET", "DURESS", "SCHEIDT"]:
            if len(keyword) != P2:
                # Repeat/truncate to match period
                key2 = (keyword * ((P2 // len(keyword)) + 1))[:P2]
            else:
                key2 = keyword
            
            # Try both decrypt directions  
            for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
                try:
                    pt = vig_decrypt(DECRYPTED_P29, key2, alpha)
                    sc = score_english(pt)
                    if sc > 25:
                        results.append((sc, f"DoubleVig P29+key2={key2} ({alpha[:7]})", pt))
                    
                    # Also try: decrypt K4 with key2 first, then period-29
                    intermediate = vig_decrypt(K4, key2, alpha)
                    # Then apply period-29 key to intermediate
                    pt2_chars = []
                    for i, c in enumerate(intermediate):
                        k = P29_KEY[i % 29]
                        if k == '?':
                            pt2_chars.append('?')
                        else:
                            pt2_chars.append(vig_decrypt_char(c, k, KRYPTOS_ALPHA))
                    pt2 = ''.join(pt2_chars)
                    pt2_known = pt2.replace('?', '')
                    sc2 = score_english(pt2_known) if pt2_known else -999
                    if sc2 > 20:
                        results.append((sc2, f"DoubleVig key2={key2}+P29 ({alpha[:7]})", pt2))
                except (ValueError, IndexError):
                    pass
    
    # Also try: two passes with period 29, different keys
    # If key1 gives BERLINCLOCK plaintext, what key2 would give something else?
    # The duress idea: give up key1 -> get BERLINCLOCK message
    # Real key2 -> get hidden message
    for keyword in ["BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST", "KRYPTOS",
                    "PALIMPSEST", "ABSCISSA", "SHADOW", "LAYER"]:
        key2 = (keyword * 3)[:29]
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                pt = vig_decrypt(K4, key2, alpha)
                sc = score_english(pt)
                if sc > 25:
                    results.append((sc, f"SingleVig key={key2[:15]}.. ({alpha[:7]})", pt))
            except (ValueError, IndexError):
                pass
    
    return results

t0 = time.time()
dv_results = test_double_vigenere()
print(f"Double Vigenère: {len(dv_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(dv_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(dv_results)

# ============================================================
# TEST 2: VIGENÈRE + POSITION-DEPENDENT CAESAR
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: VIGENÈRE + POSITION-DEPENDENT CAESAR")
print("=" * 70)

def test_vig_plus_caesar():
    """
    After period-29 Vigenère, apply a position-dependent Caesar shift.
    """
    results = []
    intermediate = DECRYPTED_P29
    
    # Test various shift functions
    for desc, shift_fn in [
        # shift[i] = i mod N
        *[(f"shift=i%{N}", lambda i, N=N: i % N) for N in range(2, 30)],
        # shift[i] = (i*i) mod N
        *[(f"shift=i²%{N}", lambda i, N=N: (i*i) % N) for N in [7, 13, 26, 29]],
        # shift[i] = i mod 26 (progressive)
        ("shift=i%26", lambda i: i % 26),
        # shift[i] = constant
        *[(f"shift={s}", lambda i, s=s: s) for s in range(1, 26)],
        # shift based on K3 plaintext
        ("shift=K3pt", lambda i: STANDARD_ALPHA.index(K3_PT[i % len(K3_PT)]) if K3_PT[i % len(K3_PT)] in STANDARD_ALPHA else 0),
        # shift based on K4 ciphertext position value
        ("shift=K4ct", lambda i: KRYPTOS_ALPHA.index(K4[i])),
        # Fibonacci-like: shift[i] = fib(i) mod 26
        ("shift=fib%26", lambda i, _fib=[0,1]: (_fib.append(_fib[-1]+_fib[-2]) or _fib[i]) if i >= len(_fib) else _fib[i]),
        # Triangular numbers mod 26
        ("shift=tri%26", lambda i: (i*(i+1)//2) % 26),
        # Alternating direction
        *[(f"shift=alt±{s}", lambda i, s=s: s if i % 2 == 0 else -s) for s in range(1, 14)],
    ]:
        try:
            pt = []
            for i, c in enumerate(intermediate):
                if c in KRYPTOS_ALPHA:
                    shift = shift_fn(i) % 26
                    ci = KRYPTOS_ALPHA.index(c)
                    pt.append(KRYPTOS_ALPHA[(ci - shift) % 26])
                else:
                    pt.append(c)
            pt = ''.join(pt)
            sc = score_english(pt)
            if sc > 25:
                results.append((sc, f"VigP29+Caesar({desc})", pt))
        except Exception:
            pass
    
    # Also: apply Caesar to K4 first, THEN Vigenère
    for shift in range(1, 26):
        shifted = ''.join(KRYPTOS_ALPHA[(KRYPTOS_ALPHA.index(c) + shift) % 26] for c in K4)
        # Now decrypt with period-29 partial key
        pt_chars = []
        for i, c in enumerate(shifted):
            k = P29_KEY[i % 29]
            if k == '?':
                pt_chars.append('?')
            else:
                pt_chars.append(vig_decrypt_char(c, k))
        pt = ''.join(pt_chars).replace('?', '')
        sc = score_english(pt)
        if sc > 20:
            results.append((sc, f"Caesar({shift})+VigP29", ''.join(pt_chars)))
    
    return results

t0 = time.time()
vc_results = test_vig_plus_caesar()
print(f"Vig+Caesar: {len(vc_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(vc_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(vc_results)

# ============================================================
# TEST 3: VIGENÈRE + XOR-LIKE
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: VIGENÈRE + XOR-LIKE OPERATIONS")
print("=" * 70)

def test_vig_plus_xor():
    """
    After Vigenère, XOR (mod 26) with various patterns.
    XOR in mod-26: result = (a + b) mod 26 or (a - b) mod 26
    """
    results = []
    intermediate = DECRYPTED_P29
    
    # Prepare XOR streams
    xor_streams = {}
    
    # Reversed ciphertext
    xor_streams["rev_ct"] = K4[::-1]
    
    # K1 ciphertext (padded/repeated)
    xor_streams["K1ct"] = (K1_CT * 3)[:K4_LEN]
    
    # K2 ciphertext (truncated)
    xor_streams["K2ct"] = K2_CT[:K4_LEN] if len(K2_CT) >= K4_LEN else (K2_CT * 2)[:K4_LEN]
    
    # K1 plaintext 
    k1pt_clean = ''.join(c for c in K1_PT if c in STANDARD_ALPHA)
    xor_streams["K1pt"] = (k1pt_clean * 3)[:K4_LEN]
    
    # K2 plaintext
    k2pt_clean = ''.join(c for c in K2_PT if c in STANDARD_ALPHA)
    xor_streams["K2pt"] = (k2pt_clean * 2)[:K4_LEN]
    
    # K3 plaintext
    k3pt_clean = ''.join(c for c in K3_PT if c in STANDARD_ALPHA)
    xor_streams["K3pt"] = (k3pt_clean * 2)[:K4_LEN]
    
    # Alternating 0/13 (ROT13 every other char)
    xor_streams["alt013"] = ''.join(KRYPTOS_ALPHA[0] if i % 2 == 0 else KRYPTOS_ALPHA[13] for i in range(K4_LEN))
    
    # K4 itself (self-XOR)
    xor_streams["K4self"] = K4
    
    # KRYPTOS repeated
    xor_streams["KRYPTOS"] = ("KRYPTOS" * 20)[:K4_LEN]
    
    # BERLINCLOCK repeated
    xor_streams["BERLINCLK"] = ("BERLINCLOCK" * 10)[:K4_LEN]
    
    for stream_name, stream in xor_streams.items():
        for op_name, op in [("add", lambda a, b: (a + b) % 26), 
                            ("sub", lambda a, b: (a - b) % 26)]:
            for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
                try:
                    pt = []
                    for i, c in enumerate(intermediate):
                        if c in alpha and stream[i] in alpha:
                            a = alpha.index(c)
                            b = alpha.index(stream[i])
                            pt.append(alpha[op(a, b)])
                        else:
                            pt.append(c)
                    pt = ''.join(pt)
                    sc = score_english(pt)
                    if sc > 25:
                        results.append((sc, f"VigP29 {op_name} {stream_name} ({alpha[:4]})", pt))
                except (ValueError, IndexError):
                    pass
        
        # Also try XOR stream applied BEFORE Vigenère
        for op_name, op in [("add", lambda a, b: (a + b) % 26),
                            ("sub", lambda a, b: (a - b) % 26)]:
            try:
                # Apply XOR to K4 ciphertext first
                modified = []
                for i, c in enumerate(K4):
                    a = KRYPTOS_ALPHA.index(c)
                    b = KRYPTOS_ALPHA.index(stream[i]) if stream[i] in KRYPTOS_ALPHA else 0
                    modified.append(KRYPTOS_ALPHA[op(a, b)])
                modified = ''.join(modified)
                
                # Then decrypt with period-29 partial key
                pt_chars = []
                for i, c in enumerate(modified):
                    k = P29_KEY[i % 29]
                    if k == '?':
                        pt_chars.append('?')
                    else:
                        pt_chars.append(vig_decrypt_char(c, k))
                pt = ''.join(pt_chars).replace('?', '')
                sc = score_english(pt)
                if sc > 20:
                    results.append((sc, f"{op_name}({stream_name})+VigP29", ''.join(pt_chars)))
            except (ValueError, IndexError):
                pass
    
    return results

t0 = time.time()
xor_results = test_vig_plus_xor()
print(f"Vig+XOR: {len(xor_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(xor_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(xor_results)

# ============================================================
# TEST 4: SPLIT CIPHER
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: SPLIT CIPHER (DIFFERENT METHODS PER SECTION)")
print("=" * 70)

def test_split_cipher():
    """
    Different cipher methods for different sections.
    Sections defined by crib locations vs "gibberish" areas.
    """
    results = []
    
    # Define sections based on the partial decryption
    # Gibberish regions in DECRYPTED_P29:
    # 0-16: UDAYUQAPBZDBKZEL (some readable: DAY, but mostly gibberish)
    # 26-63: LGUWCIAASQGUZOUAFZFETMMNXPSOZMPAPGLKGB (CIA, KGB visible)
    # 75-81: RSPVJWQ
    # 87-96: JYBUKCAYF (partial gibberish)
    
    # Readable regions:
    # 17-25: NORTHEAST
    # 64-74: BERLINCLOCK
    # 82-86: ABOVE
    
    # Hypothesis: gibberish positions use Beaufort instead of Vigenère
    # (or vice versa)
    
    readable_positions = set()
    for start, end in [(17, 26), (64, 75), (82, 87)]:
        for i in range(start, end):
            readable_positions.add(i)
    
    # Test: Vigenère for crib positions, Beaufort for others
    for alpha in [KRYPTOS_ALPHA]:
        pt_chars = list(DECRYPTED_P29)  # Start with P29 decryption
        
        # For gibberish positions, try Beaufort decryption instead
        # This means: at those positions, instead of pt = ct - key, use pt = key - ct
        for i in range(K4_LEN):
            k = P29_KEY[i % 29]
            if k == '?' or i in readable_positions:
                continue
            # Re-decrypt this position using Beaufort
            ct_char = K4[i]
            pt_chars[i] = beaufort_decrypt_char(ct_char, k, alpha)
        
        pt = ''.join(pt_chars)
        sc = score_english(pt)
        results.append((sc, "Split: Vig(cribs)+Beaufort(gibberish)", pt))
    
    # Test: different periods for different sections
    section_defs = [
        ("5-section", [(0, 21), (21, 34), (34, 63), (63, 74), (74, 97)]),
        ("3-section", [(0, 26), (26, 64), (64, 97)]),
        ("crib-gap", [(0, 17), (17, 26), (26, 64), (64, 75), (75, 97)]),
    ]
    
    for sec_name, sections in section_defs:
        for periods in product([7, 11, 13, 17, 19, 23, 29], repeat=len(sections)):
            # Only test if at least one section differs from 29
            if all(p == 29 for p in periods):
                continue
            # Quick filter: skip if too many non-29 periods (too slow)
            if sum(1 for p in periods if p != 29) > 2:
                continue
            
            # For each section with period != 29, we'd need to find the key
            # This is intractable without more info, so just try period 29 
            # with shifted keys for non-standard sections
            for shift in range(1, 26):
                pt_chars = list('?' * K4_LEN)
                for sec_idx, (s_start, s_end) in enumerate(sections):
                    p = periods[sec_idx]
                    for i in range(s_start, min(s_end, K4_LEN)):
                        k = P29_KEY[i % 29]
                        if k == '?':
                            continue
                        if p != 29:
                            # Apply additional shift for this section
                            k_i = KRYPTOS_ALPHA.index(k)
                            k = KRYPTOS_ALPHA[(k_i + shift) % 26]
                        pt_chars[i] = vig_decrypt_char(K4[i], k)
                
                pt = ''.join(pt_chars)
                pt_clean = pt.replace('?', '')
                sc = score_english(pt_clean)
                if sc > 25:
                    results.append((sc, f"Split({sec_name}) periods={periods} shift={shift}", pt))
        
        # Limit combinations to avoid timeout
        break  # Only test first section definition with period combos
    
    # Test: Atbash on gibberish positions
    pt_chars = list(DECRYPTED_P29)
    for i in range(K4_LEN):
        if i not in readable_positions:
            c = pt_chars[i]
            if c in STANDARD_ALPHA:
                pt_chars[i] = STANDARD_ALPHA[25 - STANDARD_ALPHA.index(c)]
    pt = ''.join(pt_chars)
    sc = score_english(pt)
    results.append((sc, "Split: keep cribs, Atbash gibberish (std)", pt))
    
    # Test: Atbash in KRYPTOS alphabet on gibberish
    pt_chars = list(DECRYPTED_P29)
    for i in range(K4_LEN):
        if i not in readable_positions:
            c = pt_chars[i]
            if c in KRYPTOS_ALPHA:
                pt_chars[i] = KRYPTOS_ALPHA[25 - KRYPTOS_ALPHA.index(c)]
    pt = ''.join(pt_chars)
    sc = score_english(pt)
    results.append((sc, "Split: keep cribs, Atbash gibberish (krypt)", pt))
    
    # Test: ROT13 on gibberish positions
    pt_chars = list(DECRYPTED_P29)
    for i in range(K4_LEN):
        if i not in readable_positions:
            c = pt_chars[i]
            if c in STANDARD_ALPHA:
                pt_chars[i] = STANDARD_ALPHA[(STANDARD_ALPHA.index(c) + 13) % 26]
    pt = ''.join(pt_chars)
    sc = score_english(pt)
    results.append((sc, "Split: keep cribs, ROT13 gibberish", pt))
    
    # Test: reverse the gibberish sections
    gib_sections = [(0, 17), (26, 64), (75, 82), (87, 97)]
    pt_chars = list(DECRYPTED_P29)
    for gs, ge in gib_sections:
        section = list(DECRYPTED_P29[gs:ge])
        section.reverse()
        for j, c in enumerate(section):
            pt_chars[gs + j] = c
    pt = ''.join(pt_chars)
    sc = score_english(pt)
    results.append((sc, "Split: reverse gibberish sections", pt))
    
    return results

t0 = time.time()
split_results = test_split_cipher()
print(f"Split cipher: {len(split_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(split_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(split_results)

# ============================================================
# TEST 5: KEY DERIVATION FROM CRIBS
# ============================================================

print("\n" + "=" * 70)
print("TEST 5: KEY DERIVATION FROM CRIBS")
print("=" * 70)

def test_crib_key_derivation():
    """
    Use BERLINCLOCK and EASTNORTHEAST as secondary key material.
    """
    results = []
    
    # Test 5a: Use BERLINCLOCK as a secondary key for the whole message
    for key2 in ["BERLINCLOCK", "EASTNORTHEAST", "NORTHEAST", "CLOCKBERLIN",
                  "BERLINCLOCKEASTNORTHEAST", "EASTNORTHEASTBERLINCLOCK",
                  "ABOVE", "ABOVEBERLINCLOCK"]:
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                pt = vig_decrypt(DECRYPTED_P29, key2, alpha)
                sc = score_english(pt)
                if sc > 20:
                    results.append((sc, f"P29dec + Vig(key={key2[:20]}) ({alpha[:4]})", pt))
                
                pt2 = beaufort_decrypt(DECRYPTED_P29, key2, alpha) if alpha == KRYPTOS_ALPHA else None
                if pt2:
                    sc2 = score_english(pt2)
                    if sc2 > 20:
                        results.append((sc2, f"P29dec + Beaufort(key={key2[:20]})", pt2))
                
                # Also apply to K4 directly (as if the key were the full key)
                pt3 = vig_decrypt(K4, key2, alpha)
                sc3 = score_english(pt3)
                if sc3 > 20:
                    results.append((sc3, f"K4 + Vig(key={key2[:20]}) ({alpha[:4]})", pt3))
            except (ValueError, IndexError):
                pass
    
    # Test 5b: Use crib text as key ONLY for non-crib positions
    # The idea: at crib positions, use period-29 key (get BERLINCLOCK etc.)
    # At non-crib positions, use the crib text itself as key material
    
    readable_positions = set()
    for start, end in [(17, 26), (64, 75), (82, 87)]:
        for i in range(start, end):
            readable_positions.add(i)
    
    for key_word in ["BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST",
                      "BERLINCLOCKEASTNORTHEAST", "ABOVE",
                      "KRYPTOS", "PALIMPSEST", "ABSCISSA"]:
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                pt_chars = list(DECRYPTED_P29)
                ki = 0
                for i in range(K4_LEN):
                    if i not in readable_positions:
                        c = DECRYPTED_P29[i]
                        if c in alpha:
                            k = key_word[ki % len(key_word)]
                            if k in alpha:
                                pt_chars[i] = vig_decrypt_char(c, k, alpha)
                        ki += 1
                pt = ''.join(pt_chars)
                sc = score_english(pt)
                if sc > 25:
                    results.append((sc, f"Crib+key({key_word[:15]}) non-crib ({alpha[:4]})", pt))
            except (ValueError, IndexError):
                pass
    
    # Test 5c: Interleave BERLINCLOCK and EASTNORTHEAST as key
    interleaved_keys = []
    bc = "BERLINCLOCK"
    ne = "EASTNORTHEAST"
    
    # Simple interleave
    ik = []
    for i in range(max(len(bc), len(ne))):
        if i < len(bc):
            ik.append(bc[i])
        if i < len(ne):
            ik.append(ne[i])
    interleaved_keys.append(("interleave_BC_NE", ''.join(ik)))
    
    # Concatenations
    interleaved_keys.append(("BC+NE", bc + ne))
    interleaved_keys.append(("NE+BC", ne + bc))
    
    # Use BERLINCLOCK chars at even positions, EASTNORTHEAST at odd
    alt_key = []
    for i in range(K4_LEN):
        if i % 2 == 0:
            alt_key.append(bc[i % len(bc)])
        else:
            alt_key.append(ne[i % len(ne)])
    interleaved_keys.append(("alt_BC_NE", ''.join(alt_key[:29])))
    
    for key_name, key_str in interleaved_keys:
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                pt = vig_decrypt(K4, key_str, alpha)
                sc = score_english(pt)
                if sc > 20:
                    results.append((sc, f"K4+Vig({key_name}) ({alpha[:4]})", pt))
                
                pt2 = vig_decrypt(DECRYPTED_P29, key_str, alpha)
                sc2 = score_english(pt2)
                if sc2 > 20:
                    results.append((sc2, f"P29+Vig({key_name}) ({alpha[:4]})", pt2))
            except (ValueError, IndexError):
                pass
    
    # Test 5d: The key positions that are unknown in P29 - try filling them
    # with characters derived from BERLINCLOCK or NORTHEAST
    
    unknown_positions = sorted(UNKNOWN_KEY_POS)
    print(f"  Unknown key positions: {unknown_positions}")
    
    # Try filling unknowns with each crib, cycling through
    for fill_word in ["BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST", "KRYPTOS",
                       "ABOVE", "PALIMPSEST", "ABSCISSA", "CLOCK", "BERLIN"]:
        test_key = list(P29_KEY)
        for idx, pos in enumerate(unknown_positions):
            test_key[pos] = fill_word[idx % len(fill_word)]
        
        key_str = ''.join(test_key)
        pt = vig_decrypt(K4, key_str, KRYPTOS_ALPHA)
        sc = score_english(pt)
        if sc > 25:
            results.append((sc, f"P29key+fill({fill_word[:12]}) key={key_str}", pt))
    
    # Test 5e: Try all 26^5 combinations for the 5 unknown positions
    # This is 26^5 = 11,881,376 - need to be smart
    # Use frequency-based pruning: score partial decryptions
    
    print("  Brute-forcing 5 unknown key positions (sampling)...")
    
    # For efficiency, pre-compute which plaintext positions map to each unknown key position
    unknown_to_ct_pos = {u: [] for u in unknown_positions}
    for i in range(K4_LEN):
        kp = i % 29
        if kp in UNKNOWN_KEY_POS:
            unknown_to_ct_pos[kp].append(i)
    
    print(f"  Unknown key pos -> CT positions:")
    for u in unknown_positions:
        print(f"    Key pos {u}: CT positions {unknown_to_ct_pos[u]}")
    
    # Try common key characters for unknown positions
    # Score each independently first
    best_per_pos = {}
    for u_pos in unknown_positions:
        ct_positions = unknown_to_ct_pos[u_pos]
        best_score = -999
        best_chars = []
        for k_idx in range(26):
            k_char = KRYPTOS_ALPHA[k_idx]
            pt_chars = []
            for ct_pos in ct_positions:
                pt_chars.append(vig_decrypt_char(K4[ct_pos], k_char))
            # Score these characters for English-likeness
            sc = 0
            for c in pt_chars:
                sc += ENG_FREQ.get(c, 0)
            if sc > best_score:
                best_score = sc
                best_chars = [(k_char, sc)]
            elif abs(sc - best_score) < 1:
                best_chars.append((k_char, sc))
        best_per_pos[u_pos] = sorted(best_chars, key=lambda x: -x[1])[:6]
    
    print("  Best key chars per unknown position:")
    for u_pos, chars in best_per_pos.items():
        print(f"    Pos {u_pos}: {[(c, f'{s:.1f}') for c, s in chars]}")
    
    # Try top 6 for each position: 6^5 = 7776 combinations
    count = 0
    best_brute = []
    char_lists = [best_per_pos[u][: 6] for u in unknown_positions]
    
    for combo in product(*char_lists):
        test_key = list(P29_KEY)
        for pos, (char, _) in zip(unknown_positions, combo):
            test_key[pos] = char
        
        key_str = ''.join(test_key)
        pt = vig_decrypt(K4, key_str, KRYPTOS_ALPHA)
        sc = score_english(pt)
        
        if sc > 30:
            best_brute.append((sc, f"P29brute key={key_str}", pt))
        count += 1
    
    print(f"  Tested {count} key combinations")
    best_brute.sort(reverse=True)
    results.extend(best_brute[:50])
    
    # Also try with standard alphabet
    best_per_pos_std = {}
    for u_pos in unknown_positions:
        ct_positions = unknown_to_ct_pos[u_pos]
        candidates = []
        for k_idx in range(26):
            k_char = STANDARD_ALPHA[k_idx]
            pt_chars = []
            for ct_pos in ct_positions:
                ct_c = K4[ct_pos]
                if ct_c in STANDARD_ALPHA:
                    pt_chars.append(STANDARD_ALPHA[(STANDARD_ALPHA.index(ct_c) - k_idx) % 26])
            sc = sum(ENG_FREQ.get(c, 0) for c in pt_chars)
            candidates.append((k_char, sc))
        best_per_pos_std[u_pos] = sorted(candidates, key=lambda x: -x[1])[:6]
    
    char_lists_std = [best_per_pos_std[u][:6] for u in unknown_positions]
    count2 = 0
    for combo in product(*char_lists_std):
        test_key = list(P29_KEY)
        for pos, (char, _) in zip(unknown_positions, combo):
            test_key[pos] = char
        key_str = ''.join(test_key)
        
        pt_chars = []
        for i in range(K4_LEN):
            k = test_key[i % 29]
            ct_c = K4[i]
            if ct_c in STANDARD_ALPHA and k in STANDARD_ALPHA:
                pt_chars.append(STANDARD_ALPHA[(STANDARD_ALPHA.index(ct_c) - STANDARD_ALPHA.index(k)) % 26])
            else:
                pt_chars.append('?')
        pt = ''.join(pt_chars)
        sc = score_english(pt)
        if sc > 30:
            results.append((sc, f"P29brute(std) key={key_str}", pt))
        count2 += 1
    
    print(f"  Tested {count2} standard-alpha key combinations")
    
    return results

t0 = time.time()
crib_results = test_crib_key_derivation()
print(f"Crib key derivation: {len(crib_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(crib_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(crib_results)

# ============================================================
# BONUS TEST: AUTOKEY VARIANTS ON THE INTERMEDIATE
# ============================================================

print("\n" + "=" * 70)
print("BONUS: AUTOKEY AND VARIANT CIPHERS ON INTERMEDIATE")
print("=" * 70)

def test_autokey_variants():
    """
    Test autokey cipher (where the key extends with plaintext or ciphertext).
    Applied as a second layer on the period-29 intermediate.
    """
    results = []
    intermediate = DECRYPTED_P29
    
    for primer in ["BERLINCLOCK", "NORTHEAST", "EASTNORTHEAST", "KRYPTOS",
                   "ABOVE", "PALIMPSEST", "ABSCISSA", "SHADOW", "LAYER",
                   "K", "B", "E", "A", "S", "CLOCK", "BERLIN"]:
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                # Plaintext autokey: key = primer + plaintext
                pt = []
                key_stream = list(primer)
                for i, c in enumerate(intermediate):
                    if i < len(key_stream):
                        k = key_stream[i]
                    else:
                        k = pt[-1] if pt else alpha[0]
                        key_stream.append(k)
                    if c in alpha and k in alpha:
                        p = alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)]
                        pt.append(p)
                        if i >= len(primer):
                            key_stream.append(p)
                    else:
                        pt.append(c)
                
                pt_str = ''.join(pt)
                sc = score_english(pt_str)
                if sc > 25:
                    results.append((sc, f"Autokey(pt) primer={primer} ({alpha[:4]})", pt_str))
                
                # Ciphertext autokey: key = primer + ciphertext
                pt2 = []
                key_stream2 = list(primer)
                for i, c in enumerate(intermediate):
                    if i < len(key_stream2):
                        k = key_stream2[i]
                    else:
                        k = intermediate[i - len(primer)] if i >= len(primer) else alpha[0]
                    if c in alpha and k in alpha:
                        p = alpha[(alpha.index(c) - alpha.index(k)) % len(alpha)]
                        pt2.append(p)
                    else:
                        pt2.append(c)
                
                pt2_str = ''.join(pt2)
                sc2 = score_english(pt2_str)
                if sc2 > 25:
                    results.append((sc2, f"Autokey(ct) primer={primer} ({alpha[:4]})", pt2_str))
                    
            except (ValueError, IndexError):
                pass
    
    return results

t0 = time.time()
ak_results = test_autokey_variants()
print(f"Autokey variants: {len(ak_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(ak_results, reverse=True)[:5]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(ak_results)

# ============================================================
# BONUS TEST: STANDARD ALPHABET PERIOD-29 + SECOND LAYER
# ============================================================

print("\n" + "=" * 70)
print("BONUS: STANDARD ALPHABET PERIOD-29 VARIANTS")
print("=" * 70)

def test_standard_alpha_variants():
    """
    What if the Vigenère uses standard alphabet instead of KRYPTOS?
    Derive key from cribs and test second layers.
    """
    results = []
    
    # Derive period-29 key using standard alphabet
    std_key = ['?'] * 29
    
    # NORTHEAST at positions 17-25
    for i, p in enumerate("NORTHEAST"):
        ct_c = K4[17 + i]
        k_pos = (17 + i) % 29
        k_val = (STANDARD_ALPHA.index(ct_c) - STANDARD_ALPHA.index(p)) % 26
        std_key[k_pos] = STANDARD_ALPHA[k_val]
    
    # BERLINCLOCK at positions 64-74
    for i, p in enumerate("BERLINCLOCK"):
        ct_c = K4[64 + i]
        k_pos = (64 + i) % 29
        k_val = (STANDARD_ALPHA.index(ct_c) - STANDARD_ALPHA.index(p)) % 26
        std_key[k_pos] = STANDARD_ALPHA[k_val]
    
    print(f"  Standard alpha P29 key: {''.join(std_key)}")
    
    # Decrypt with standard alphabet partial key
    std_dec = []
    for i, c in enumerate(K4):
        k = std_key[i % 29]
        if k == '?':
            std_dec.append('?')
        else:
            std_dec.append(STANDARD_ALPHA[(STANDARD_ALPHA.index(c) - STANDARD_ALPHA.index(k)) % 26])
    std_dec = ''.join(std_dec)
    print(f"  Standard P29 partial: {std_dec}")
    
    sc_base = score_english(std_dec.replace('?', ''))
    results.append((sc_base, "Std alpha P29 partial", std_dec))
    
    # Apply second layers to this
    for key2 in ["BERLINCLOCK", "NORTHEAST", "KRYPTOS", "PALIMPSEST"]:
        pt = []
        for i, c in enumerate(std_dec):
            if c == '?':
                pt.append('?')
            else:
                k = key2[i % len(key2)]
                pt.append(STANDARD_ALPHA[(STANDARD_ALPHA.index(c) - STANDARD_ALPHA.index(k)) % 26])
        pt = ''.join(pt)
        sc = score_english(pt.replace('?', ''))
        if sc > 20:
            results.append((sc, f"StdP29+Vig({key2})", pt))
    
    return results

t0 = time.time()
std_results = test_standard_alpha_variants()
print(f"Standard alpha: {len(std_results)} candidates found in {time.time()-t0:.1f}s")
all_results.extend(std_results)

# ============================================================
# BONUS: BEAUFORT AS PRIMARY CIPHER
# ============================================================

print("\n" + "=" * 70)
print("BONUS: BEAUFORT AS PRIMARY CIPHER + SECOND LAYER")
print("=" * 70)

def test_beaufort_primary():
    """What if the primary cipher is Beaufort, not Vigenère?"""
    results = []
    
    # Derive Beaufort key from cribs: ct = key - pt => key = ct + pt
    beau_key = ['?'] * 29
    
    for crib, start in [("NORTHEAST", 17), ("BERLINCLOCK", 64)]:
        for i, p in enumerate(crib):
            ct_c = K4[start + i]
            k_pos = (start + i) % 29
            # Beaufort: ct = key - pt => key = ct + pt (mod 26)
            k_val = (KRYPTOS_ALPHA.index(ct_c) + KRYPTOS_ALPHA.index(p)) % 26
            beau_key[k_pos] = KRYPTOS_ALPHA[k_val]
    
    print(f"  Beaufort P29 key: {''.join(beau_key)}")
    
    beau_dec = []
    for i, c in enumerate(K4):
        k = beau_key[i % 29]
        if k == '?':
            beau_dec.append('?')
        else:
            beau_dec.append(beaufort_decrypt_char(c, k))
    beau_dec = ''.join(beau_dec)
    print(f"  Beaufort P29 partial: {beau_dec}")
    
    sc = score_english(beau_dec.replace('?', ''))
    results.append((sc, "Beaufort P29 partial (KRYPTOS)", beau_dec))
    
    # Second layers on Beaufort decryption
    for key2 in ["BERLINCLOCK", "NORTHEAST", "KRYPTOS"]:
        for alpha in [KRYPTOS_ALPHA]:
            pt = vig_decrypt(beau_dec.replace('?', 'A'), key2, alpha)
            sc2 = score_english(pt)
            if sc2 > 20:
                results.append((sc2, f"Beaufort+Vig({key2})", pt))
    
    return results

t0 = time.time()
beau_results = test_beaufort_primary()
print(f"Beaufort primary: {len(beau_results)} candidates found in {time.time()-t0:.1f}s")
all_results.extend(beau_results)

# ============================================================
# BONUS: RUNNING KEY WITH KNOWN TEXTS
# ============================================================

print("\n" + "=" * 70)
print("BONUS: RUNNING KEY WITH K1/K2/K3 TEXT")
print("=" * 70)

def test_running_key():
    """Use K1/K2/K3 plaintext or ciphertext as a running key."""
    results = []
    
    running_keys = {
        "K1pt": k1pt_clean if 'k1pt_clean' in dir() else K1_PT.replace(" ", ""),
        "K2pt": K2_PT,
        "K3pt": K3_PT,
        "K1ct": K1_CT,
        "K2ct": K2_CT,
    }
    
    for rk_name, rk_text in running_keys.items():
        rk_clean = ''.join(c for c in rk_text if c in STANDARD_ALPHA)
        if len(rk_clean) < K4_LEN:
            rk_clean = (rk_clean * 3)[:K4_LEN]
        else:
            rk_clean = rk_clean[:K4_LEN]
        
        for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
            try:
                # Running key on K4 directly
                pt = vig_decrypt(K4, rk_clean, alpha)
                sc = score_english(pt)
                if sc > 20:
                    results.append((sc, f"RunKey({rk_name}) on K4 ({alpha[:4]})", pt))
                
                # Running key on intermediate (after P29)
                pt2 = vig_decrypt(DECRYPTED_P29, rk_clean, alpha)
                sc2 = score_english(pt2)
                if sc2 > 20:
                    results.append((sc2, f"RunKey({rk_name}) on P29dec ({alpha[:4]})", pt2))
                
                # Beaufort running key
                pt3 = beaufort_decrypt(K4, rk_clean, alpha)
                sc3 = score_english(pt3)
                if sc3 > 20:
                    results.append((sc3, f"BeaufortRunKey({rk_name}) on K4 ({alpha[:4]})", pt3))
                    
            except (ValueError, IndexError):
                pass
        
        # Try different offsets into the running key
        for offset in [10, 20, 50, 100, 150, 200, 250]:
            rk_offset = rk_clean[offset:] + rk_clean[:offset]
            rk_offset = rk_offset[:K4_LEN]
            for alpha in [KRYPTOS_ALPHA, STANDARD_ALPHA]:
                try:
                    pt = vig_decrypt(K4, rk_offset, alpha)
                    sc = score_english(pt)
                    if sc > 25:
                        results.append((sc, f"RunKey({rk_name}+{offset}) ({alpha[:4]})", pt))
                except (ValueError, IndexError):
                    pass
    
    return results

t0 = time.time()
rk_results = test_running_key()
print(f"Running key: {len(rk_results)} candidates found in {time.time()-t0:.1f}s")
for sc, desc, pt in sorted(rk_results, reverse=True)[:3]:
    print(f"  Score {sc:.1f}: {desc}")
    print(f"    PT: {pt[:80]}")
all_results.extend(rk_results)

# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 70)
print("TOP 20 RESULTS")
print("=" * 70)

all_results.sort(key=lambda x: -x[0])

# Deduplicate by plaintext
seen = set()
unique_results = []
for sc, desc, pt in all_results:
    pt_key = pt[:50]
    if pt_key not in seen:
        seen.add(pt_key)
        unique_results.append((sc, desc, pt))

for rank, (sc, desc, pt) in enumerate(unique_results[:20], 1):
    print(f"\n{'─' * 60}")
    print(f"Rank {rank:2d} | Score: {sc:.1f}")
    print(f"Method: {desc}")
    print(f"PT: {pt}")
    
    # Highlight any English words found
    found_words = []
    for wlen in range(10, 2, -1):
        if wlen not in WORDS_BY_LEN:
            continue
        for start in range(len(pt) - wlen + 1):
            substr = pt[start:start + wlen].replace('?', '')
            if len(substr) == wlen and substr in WORDS_BY_LEN[wlen]:
                found_words.append((start, substr))
    if found_words:
        # Remove substrings
        filtered = []
        for s1, w1 in found_words:
            is_sub = False
            for s2, w2 in found_words:
                if w1 != w2 and w1 in w2 and s1 >= s2 and s1 + len(w1) <= s2 + len(w2):
                    is_sub = True
                    break
            if not is_sub:
                filtered.append((s1, w1))
        print(f"Words: {', '.join(f'{w}@{s}' for s, w in filtered[:15])}")

print(f"\n{'=' * 70}")
print(f"Total candidates tested across all methods: {len(all_results)}")
print(f"Unique results: {len(unique_results)}")
print("=" * 70)
