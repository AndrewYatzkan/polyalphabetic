#!/usr/bin/env python3
"""
Deep analysis of the best keys found.

The keys LMOW, LLMW, LMRW, LMMW show chi² < 0.77 on Gap 2.
This is suspiciously good - they might be the answer or artifacts.

Analyze if the decryptions contain real English words.
"""

from collections import Counter
import re

K4_PLAINTEXT = "UNDERQAPBZDBKZELNORTHEASTLGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVHBERLINCLOCKRSPVJWQULABOVEZOLRKCAYF"

GAP1 = "QAPBZDBKZEL"
GAP2 = "LGUWCXDJFQGUZOUAFZFETMMNXPSOZMPAPGKPVH"
GAP3 = "RSPVJWQUL"
GAP4 = "ZOLRKCAYF"

def vigenere_decrypt(ciphertext, key):
    """Decrypt using Vigenère cipher."""
    plaintext = ""
    key_idx = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('A')
            decrypted = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
            plaintext += decrypted
            key_idx += 1
        else:
            plaintext += char
    return plaintext

def chi_squared_english(text):
    """Calculate chi-squared against English distribution."""
    english_freq = {
        'A': 0.082, 'B': 0.015, 'C': 0.028, 'D': 0.043, 'E': 0.127,
        'F': 0.022, 'G': 0.020, 'H': 0.061, 'I': 0.070, 'J': 0.002,
        'K': 0.008, 'L': 0.040, 'M': 0.024, 'N': 0.067, 'O': 0.075,
        'P': 0.019, 'Q': 0.001, 'R': 0.060, 'S': 0.063, 'T': 0.091,
        'U': 0.028, 'V': 0.010, 'W': 0.024, 'X': 0.002, 'Y': 0.020,
        'Z': 0.001
    }

    freq = Counter(text)
    total = len(text)
    chi_sq = 0
    for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        observed = freq.get(char, 0) / total
        expected = english_freq[char]
        if expected > 0:
            chi_sq += (observed - expected) ** 2 / expected

    return chi_sq

def load_wordlist():
    """Load common English words."""
    words = set()
    common_words_list = [
        'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER',
        'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM', 'HIS', 'HOW',
        'ITS', 'MAY', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO', 'BOY',
        'DID', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'BACK', 'CALL', 'CAME',
        'DOWN', 'EACH', 'EVEN', 'FIND', 'GAVE', 'GOOD', 'HAND', 'HERE', 'HOME',
        'JUST', 'KEEP', 'KIND', 'KNOW', 'LIKE', 'MADE', 'MAKE', 'MANY', 'MORE',
        'MOST', 'MUCH', 'MUST', 'NAME', 'NEED', 'NEXT', 'ONLY', 'OPEN', 'OVER',
        'PART', 'PLAY', 'SAID', 'SAME', 'TAKE', 'TELL', 'THAN', 'THAT', 'THEM',
        'THEN', 'THEY', 'THIS', 'TIME', 'TOLD', 'TOOK', 'VERY', 'WANT', 'WELL',
        'WENT', 'WERE', 'WHAT', 'WHEN', 'WITH', 'WORK', 'YEAR', 'ABLE', 'BEEN',
        'BEST', 'BOTH', 'BLUE', 'CALL', 'CAME', 'COME', 'DARK', 'DOES', 'DONE',
        'DOOR', 'DOWN', 'DRUG', 'EAST', 'FACE', 'FACT', 'FAIL', 'FAIR', 'FALL',
        'FEEL', 'FELT', 'FILE', 'FILL', 'FIRE', 'FIRM', 'FISH', 'FIVE', 'FLAT',
        'FLOW', 'FOLK', 'FOOD', 'FOOT', 'FORM', 'FORT', 'FOUR', 'FREE', 'FROM',
        'FULL', 'GAME', 'GANG', 'GATE', 'GAVE', 'GEAR', 'GIVE', 'GLAD', 'GOAL',
        'GOLD', 'GONE', 'GRAY', 'GREW', 'GREY', 'GRID', 'GRIM', 'GRIP', 'GROW',
        'GULF', 'HAIR', 'HALF', 'HALL', 'HAND', 'HANG', 'HARD', 'HARM', 'HATE',
        'HAVE', 'HEAD', 'HEAR', 'HEAT', 'HELD', 'HELP', 'HERE', 'HIGH', 'HILL',
        'HOLY', 'HORN', 'HOST', 'HOUR', 'HUGE', 'HUNG', 'HUNT', 'ICON', 'IDEA',
        'INTO', 'IRON', 'ITEM', 'JULY', 'JUMP', 'JUNE', 'JURY', 'KEEN', 'KEEP',
        'KEPT', 'KICK', 'KILL', 'KIND', 'KING', 'KISS', 'KNOW', 'LACK', 'LADY',
        'LAID', 'LAIR', 'LAKE', 'LAMP', 'LAND', 'LANE', 'LARK', 'LAST', 'LATE',
        'LEAD', 'LEAF', 'LEAK', 'LEAN', 'LEAP', 'LEFT', 'LEND', 'LESS', 'LIAR',
        'LICE', 'LICK', 'LIED', 'LIES', 'LIFE', 'LIFT', 'LIKE', 'LILY', 'LIMB',
        'LINE', 'LINK', 'LION', 'LIST', 'LIVE', 'LOAD', 'LOAF', 'LOAN', 'LOCK',
        'LOFT', 'LONE', 'LONG', 'LOOK', 'LOOP', 'LOOT', 'LORD', 'LORE', 'LOSE',
        'LOSS', 'LOST', 'LOUD', 'LOVE', 'LUCK', 'MADE', 'MAID', 'MAIL', 'MAIN',
        'MAKE', 'MALE', 'MALL', 'MALT', 'MANY', 'MARK', 'MARS', 'MASK', 'MASS',
        'MAST', 'MATH', 'MEAL', 'MEAN', 'MEAT', 'MEET', 'MESS', 'MICE', 'MILD',
        'MILE', 'MILK', 'MILL', 'MIND', 'MINE', 'MINT', 'MISS', 'MIST', 'MOAT',
        'MODE', 'MOLD', 'MOLE', 'MOOD', 'MOON', 'MOOR', 'MORE', 'MOSS', 'MOTH',
        'MOVE', 'MUCH', 'MULE', 'MUSE', 'MYTH', 'NAIL', 'NAME', 'NEAR', 'NEAT',
        'NECK', 'NEED', 'NEST', 'NEWS', 'NEXT', 'NICE', 'NICK', 'NINE', 'NODE',
        'NONE', 'NOON', 'NORM', 'NOSE', 'NOTE', 'NOUN', 'OVEN', 'OVER', 'OWES',
        'OWNS', 'PACE', 'PAGE', 'PAID', 'PAIL', 'PAIN', 'PAIR', 'PALE', 'PALM',
        'PANE', 'PANT', 'PARE', 'PARK', 'PART', 'PASS', 'PAST', 'PATH', 'PAWN',
        'PEAK', 'PEAR', 'PEAT', 'PECK', 'PEEL', 'PEER', 'PELT', 'PEST', 'PICK',
        'PIER', 'PILE', 'PINE', 'PINK', 'PINT', 'PIPE', 'PLAN', 'PLAY', 'PLEA',
        'PLOT', 'PLOW', 'PLUG', 'PLUM', 'PLUS', 'POEM', 'POET', 'POLE', 'POLL',
        'POND', 'PONY', 'POOL', 'POOR', 'POPE', 'PORK', 'PORT', 'POSE', 'POST',
        'POUR', 'PRAY', 'PREP', 'PREY', 'PUMP', 'PUNK', 'PUSH', 'QUIT', 'QUIZ',
        'RACE', 'RACK', 'RAFT', 'RAGE', 'RAID', 'RAIL', 'RAIN', 'RAKE', 'RAMP',
        'RAND', 'RANG', 'RANK', 'RARE', 'RASH', 'RATE', 'RAVE', 'RAZE', 'READ',
        'REAL', 'REAP', 'REAR', 'REDO', 'REED', 'REEL', 'RENT', 'REST', 'RICE',
        'RICH', 'RIDE', 'RIFE', 'RIFT', 'RING', 'RINK', 'RISE', 'RISK', 'ROAD',
        'ROAM', 'ROAR', 'ROBE', 'ROCK', 'RODE', 'ROLE', 'ROLL', 'ROOF', 'ROOM',
        'ROOT', 'ROPE', 'ROSE', 'ROTE', 'ROUT', 'ROVE', 'RUDE', 'RUIN', 'RULE',
        'RUNG', 'RUSE', 'RUSH', 'RUST', 'SACK', 'SAFE', 'SAGE', 'SAID', 'SAIL',
        'SAKE', 'SALE', 'SALT', 'SAME', 'SAND', 'SANE', 'SANG', 'SANK', 'SASH',
        'SAVE', 'SEAL', 'SEAM', 'SEAT', 'SECT', 'SEED', 'SEEK', 'SEEM', 'SEEN',
        'SELF', 'SELL', 'SEND', 'SENT', 'SHIP', 'SHOE', 'SHOP', 'SHOT', 'SHOW',
        'SHUT', 'SICK', 'SIDE', 'SIGH', 'SIGN', 'SILK', 'SILL', 'SINE', 'SING',
        'SINK', 'SITE', 'SIZE', 'SLAB', 'SLAG', 'SLAM', 'SLAP', 'SLAT', 'SLED',
        'SLEW', 'SLID', 'SLIM', 'SLIP', 'SLIT', 'SLOW', 'SLUG', 'SLUM', 'SOAP',
        'SOAR', 'SOCK', 'SODA', 'SOFA', 'SOFT', 'SOIL', 'SOLD', 'SOLE', 'SOME',
        'SONG', 'SOON', 'SORE', 'SORT', 'SOUL', 'SPAN', 'SPIN', 'SPIT', 'SPOT',
        'STAB', 'STAG', 'STAR', 'STAY', 'STEM', 'STEP', 'STEW', 'STIR', 'STOP',
        'SUCH', 'SUIT', 'SULK', 'SUNK', 'SURF', 'SWAM', 'SWAN', 'SWAY', 'SWIM',
        'TAIL', 'TAKE', 'TALE', 'TALK', 'TALL', 'TAME', 'TANG', 'TANK', 'TAPE',
        'TASK', 'TEAM', 'TEAR', 'TEASE', 'TEEN', 'TELL', 'TEND', 'TENT', 'TERM',
        'TEST', 'TEXT', 'THAN', 'THAT', 'THAW', 'THEE', 'THEM', 'THEN', 'THEY',
        'THIN', 'THIS', 'THOU', 'THUD', 'TICK', 'TIDE', 'TIDY', 'TIED', 'TIER',
        'TIES', 'TILE', 'TILT', 'TIME', 'TINE', 'TINT', 'TINY', 'TIRE', 'TOAD',
        'TOLL', 'TOMB', 'TOME', 'TONE', 'TOOK', 'TOOL', 'TORE', 'TORN', 'TOSS',
        'TOUR', 'TOWN', 'TRAP', 'TRAY', 'TREE', 'TREK', 'TRIM', 'TRIO', 'TRIP',
        'TROT', 'TRUE', 'TUBE', 'TUCK', 'TUFT', 'TUNE', 'TURN', 'TUSK', 'TYPE',
        'UGLY', 'UNDO', 'UNIT', 'UPON', 'USED', 'USER', 'USES', 'VAIN', 'VANE',
        'VARY', 'VASE', 'VAST', 'VEAL', 'VEIL', 'VEIN', 'VENT', 'VERB', 'VERY',
        'VEST', 'VETO', 'VICE', 'VIEW', 'VINE', 'VOID', 'VOTE', 'WADE', 'WAGE',
        'WAIT', 'WAKE', 'WALK', 'WALL', 'WAND', 'WANT', 'WARD', 'WARM', 'WARN',
        'WARP', 'WASH', 'WASP', 'WAVE', 'WAVY', 'WEAK', 'WEAR', 'WEED', 'WEEK',
        'WEEP', 'WELL', 'WENT', 'WERE', 'WEST', 'WHAT', 'WHEN', 'WHET', 'WHEY',
        'WHIM', 'WHIP', 'WICK', 'WIFE', 'WILD', 'WILL', 'WILT', 'WIND', 'WINE',
        'WING', 'WINK', 'WIPE', 'WIRE', 'WISE', 'WISH', 'WITH', 'WOKE', 'WOLF',
        'WOMB', 'WONT', 'WOOD', 'WOOL', 'WORD', 'WORE', 'WORK', 'WORM', 'WORN',
        'WRAP', 'WREN', 'WRIT', 'YANK', 'YARD', 'YARN', 'YAWN', 'YEAR', 'YELL',
        'YORK', 'YOUR', 'YOKE', 'ZEAL', 'ZINC',
        # Geographic/special terms
        'BERLIN', 'CLOCK', 'COORDINATES', 'LOCATION', 'POSITION', 'BEARING',
        'LATITUDE', 'LONGITUDE', 'UNDERGROUND', 'BENEATH', 'ABOVE', 'GROUND',
        'WORLD', 'EARTH', 'MAP', 'PLACE', 'SITE', 'POINT',
    ]
    return set(common_words_list)

def find_word_patterns(text, wordlist):
    """Find English words in text."""
    words_found = []

    for word in wordlist:
        # Check for exact matches
        if word in text:
            pos = text.find(word)
            words_found.append((word, pos, len(word)))

        # Check for overlapping
        for i in range(len(text) - len(word) + 1):
            if text[i:i+len(word)] == word:
                words_found.append((word, i, len(word)))

    return words_found

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

print("="*80)
print("DEEP ANALYSIS OF BEST KEYS")
print("="*80)

wordlist = load_wordlist()

best_keys = [
    ("LMOW", 0.57),
    ("LLMW", 0.75),
    ("LMRW", 0.76),
    ("LMMW", 0.77),
    ("DEM", 1.46),
    ("BCM", 1.63),
    ("LMM", 1.66),
    ("ABOVE", 2.98),
    ("BERLIN", 2.85),
]

gaps = [
    ("Gap 1", GAP1),
    ("Gap 2", GAP2),
    ("Gap 3", GAP3),
    ("Gap 4", GAP4)
]

for key, chi_sq_score in best_keys:
    print(f"\n{'='*80}")
    print(f"KEY: {key:15s} (Chi² reference: {chi_sq_score:.2f})")
    print(f"{'='*80}")

    for gap_name, gap_text in gaps:
        decrypted = vigenere_decrypt(gap_text, key)
        chi_sq = chi_squared_english(decrypted)

        vowels = sum(1 for c in decrypted if c in 'AEIOU')
        vowel_ratio = vowels / len(decrypted) if decrypted else 0

        # Find words
        words = find_word_patterns(decrypted, wordlist)
        unique_words = list(set([w[0] for w in words]))

        print(f"\n{gap_name}: {decrypted}")
        print(f"  Chi²: {chi_sq:.2f}, Vowels: {vowel_ratio:.1%}")

        if unique_words:
            print(f"  ⚠ Found words: {', '.join(sorted(unique_words)[:10])}")
        else:
            print(f"  No English words found")

        # Analyze structure
        freq = Counter(decrypted)
        most_common = freq.most_common(3)
        print(f"  Most common: {most_common}")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("\nLooking for:")
print("- Chi² < 10 (close to English)")
print("- Vowel ratio 30-40%")
print("- Real English words present")
print("\nIf found, the key may be the correct decryption!")
