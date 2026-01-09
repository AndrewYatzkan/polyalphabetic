#!/usr/bin/env python3
"""
Analyze the K4 solutions found to identify the best English match.
"""

from collections import Counter
import re

# English letter frequencies
ENG_FREQ = {'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
            'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
            'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
            'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
            'Q': 0.10, 'Z': 0.07}

COMMON_WORDS = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL',
                'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'HIS', 'HAS',
                'ITS', 'SAY', 'SHE', 'TWO', 'WAY', 'WHO', 'BOY', 'DID',
                'GET', 'HIM', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE',
                'TIME', 'VERY', 'WHEN', 'COME', 'COULD', 'MAKE', 'THAN',
                'FIRST', 'BEEN', 'CALL', 'FIND', 'LONG', 'DOWN', 'OVER',
                'SUCH', 'TAKE', 'KNOW', 'EAST', 'WEST', 'NORTH', 'SOUTH',
                'CLOCK', 'BERLIN', 'DEGREES', 'MINUTES', 'LOCATION',
                'SECRET', 'HIDDEN', 'BURIED', 'SOMEWHERE', 'LANGLEY']

COMMON_BIGRAMS = ['TH', 'HE', 'IN', 'EN', 'NT', 'RE', 'ER', 'AN', 'TI', 'ES',
                  'ON', 'AT', 'SE', 'ND', 'OR', 'AR', 'AL', 'TE', 'CO', 'DE',
                  'TO', 'RA', 'ET', 'ED', 'IT', 'SA', 'EM', 'RO']

def calc_ioc(text):
    """Calculate Index of Coincidence."""
    freq = Counter(text)
    n = len(text)
    if n <= 1:
        return 0
    return sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))

def score_english(text):
    """Score text based on multiple English metrics."""
    score = 0

    # IoC score (closer to 0.067 is better)
    ioc = calc_ioc(text)
    ioc_score = 100 - abs(ioc - 0.067) * 1000

    # Word matches
    word_score = sum(10 for word in COMMON_WORDS if word in text and len(word) > 2)

    # Bigram frequency
    bigram_score = sum(1 for i in range(len(text)-1)
                       if text[i:i+2] in COMMON_BIGRAMS)

    # Letter frequency fit
    freq = Counter(text)
    n = len(text)
    freq_score = 0
    for letter, count in freq.items():
        observed = count / n * 100
        expected = ENG_FREQ.get(letter, 0)
        freq_score -= abs(observed - expected)

    return {
        'ioc': ioc,
        'ioc_score': ioc_score,
        'word_score': word_score,
        'bigram_score': bigram_score,
        'freq_score': freq_score,
        'total': ioc_score + word_score * 2 + bigram_score + freq_score / 2
    }

# Our found solutions
solutions = [
    ("KIAVVXTNZYWQVBZLKD", "ONNOZAQFHFXWFXSKIYBNJJUPMRURTZLMAIOQWIGDQVYGFXYORZOZKAUUBERLINCLOCKVORZYPEJLHYUOOHFJNORTHEASTTGCW"),
    ("FUHGENYMKNNUEPGPSP", "NGFHDFVGGUYVWPMHCCVGCZSBQYQDBXYWNPZRECSNORTHEASTFTLGQHCIRQFVLQBKCBERLINCLOCKZAWSTWJITDGMBMUKWGXHZ"),
    ("PQUNDTAJQOTFZSAYVCY", "YHOBERLINCLOCKXINPSOPLXLMGTCVIRRKZPBHYLFURVYTDOQNUODNIZRGTPQKYTFFCLKMNNORTHEASTOQFYQUBVCIIKNILATA"),
    ("ANXSQJJQFWSXZIKBINP", "XIYURIBERLINCLOCKNORTHEASTKLTGIRLSWITRGGMHFJUSGYLCORKCSLFKTLGMMPBLZXSNDFUETDPARMDKNJPJQWISAGVASKB"),
    ("PHFXVUJSMQGCWOHYVPL", "YQHPZDBZUQBBERLINCLOCKNORTHEASTPRMPBQGLMTVDEUQAODXAEFIZAXTCPUJGPVEYLUUQXRTQVAFGKBUNTWNGFLJNNIWMTG"),
    ("LMPLGRDVEHJRKUTKKNZ", "HJWDBTHCYKOJBERLINCLOCKHUDXMGPFKEYOTTOPHGPNORTHEASTUVLULJJOFYZACSMBHPMTBPKTHNBVALIZHTZDQHKPUEADJC"),
    ("LBNBDLEQVBZLKDKIARA", "HKANEHGELSVKBVOYBERLINCLOCKANQVKVSJWVWPXWFVIKSPLXJTSKYHCBJIVEYLBBAHOGMIFHNVSNMSJQZXJNORTHEASTZYJN"),
    ("WVUYBGPIQRKBZYMQWLK", "BFOZGMUJNGUCCTGWMUBERLINCLOCKNORTHEASTWDUMXNBEOXWZOHBWXNIDRQLTUJGCUTVNWQCPSGGTTVVPSUUFKGINIRHCCDO"),
    ("PQUCJUPODMYBLSAYVCY", "YHOMODUKPVNCLKXINPSOPLBERLINCLOCKZPBHYLFUEJEBUIAUZGDNIZRGTPQDVGJWNTYVRNORTHEASTIHUSOOUXGWIKNILATA"),
    ("RRIJMUTQUJMVEGWHZHT", "TAEEPDQEMXPUWNBPJXTAVWRCRJKBERLINCLOCKNORTHEASTCOENPPPVVESVKPQGIBBSFBAFIIRCCCZDBFUOJQWBZPBDAFFOSK"),
    ("PLWEIRYKDLPKTHOWVFP", "YLPJSTVOPWMLTMKQNKOOSISFUMQNDJGVMRBBERLINCLOCKIBQAKYUQZXFTSMBWALYNORTHEASTEDACYGIIADOVWUDAYXIHSTD"),
    ("RLBCOIVAJBMXTGKJEXW", "TLMMJJYXWSPNTNORTHEASTBVAXGGNRIVNSINZANIBERLINCLOCKPKRDFMSSADANWUGHFSHFFGIZJCCLIZRGPZOBWDBAOKYFSD"),
    ("PVBPJIHJLHVJIWLKJRI", "YFMXOJDIVKZRNCHLZENORTHEASTFGWWECIOHVILDBLJLWDBERLINCLOCKTRAJVNOFFBBHPYUPDVXATLUHRUQXZTOZXJUUZQTO"),
    ("XWNFKMSCVUIVPZEXFND", "AEAIUGMVLNSUOAQNPNXDKNORTHEASTLWAUAMTQVCWBSHOLPTBERLINCLOCKVAFJGNARIBIKROHTPFPSFTXPRNMEZEVVWZAZCT"),
    ("JMSNBLNJIJFAVOZKSLS", "IJQBGHOIXXCDFRSLCUYMOSXNORTHEASTRAOXSXTHDRXIMDDCEKBERLINCLOCKTLKFHSMWVQGPQSAQBNOVZJQKWHHMJBUOCPLC"),
    ("ZFHYWIDEXGTYPFFSHTE", "SVFZXJHQIRLIOQNERBWCEXITADCOHIEWQQZJNNUQYMCLRIRFNORTHEASTBERLINCLOCKYIGKWFNYEHEVARZZLKVNECUIWVXBI"),
    ("WJSGTWMEHPUGGJFFHBQ", "BMQHLBSQZEKTUJNORTHEASTWZYCIXXKGJQNJIDWJDAYCNIEVYQLKHOAYUDACSBERLINCLOCKLFINGDNEKNLZRDOBROUCWMIDE"),
    ("RRIJMUTQUEPGPSPFUHG", "TAEEPDQEMPMTOKYOQXUAVWRCRJKBJJKWKPNCCLNORTHEASTHQQRDWOKVYSVKPQGIBBERLINCLOCKCZDBFUOJQYWBEITCJFVSK"),
]

print("="*70)
print("K4 SOLUTION ANALYSIS")
print("="*70)

results = []
for key, pt in solutions:
    scores = score_english(pt)
    results.append((key, pt, scores))

# Sort by total score
results.sort(key=lambda x: x[2]['total'], reverse=True)

print("\nTop solutions ranked by English-likeness:")
print("-" * 70)

for i, (key, pt, scores) in enumerate(results[:10]):
    print(f"\n{i+1}. Key: {key}")
    print(f"   Plaintext: {pt}")
    print(f"   IoC: {scores['ioc']:.4f} (English=0.067)")
    print(f"   Words found: {scores['word_score']//10}")
    print(f"   Bigrams: {scores['bigram_score']}")
    print(f"   Total Score: {scores['total']:.1f}")

    # Find word positions
    words_found = [w for w in COMMON_WORDS if w in pt]
    if words_found:
        print(f"   Words: {', '.join(words_found)}")

print("\n" + "="*70)
print("BEST CANDIDATE ANALYSIS")
print("="*70)

best_key, best_pt, best_scores = results[0]
print(f"\nBest Key: {best_key}")
print(f"Plaintext: {best_pt}")
print(f"\nBreaking into possible words:")

# Try to find word boundaries
text = best_pt
for word_len in range(3, 8):
    print(f"\n{word_len}-letter segments:")
    for i in range(0, len(text) - word_len + 1, word_len):
        segment = text[i:i+word_len]
        is_word = segment in COMMON_WORDS or segment in ['BERLIN', 'CLOCK', 'NORTH', 'EAST', 'NORTHEAST', 'BERLINCLOCK']
        marker = " <--" if is_word else ""
        print(f"  {i:2d}: {segment}{marker}")
