#!/usr/bin/env python3
"""
Systematic brute force test of all 26^4 = 456,976 combinations
for K4 key positions (testing 4 specific positions).

Since K4 has unknown positions at 0-4 (5 positions) and 25-28 (4 positions),
we'll test positions 0, 1, 2, 3 (skip position 4 for now, giving us 4 positions = 26^4).
"""

import sys
import os
import re
from collections import Counter

# KRYPTOS alphabet
KRYPTOS_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Comprehensive English word list
COMMON_WORDS = set([
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
    'BEST', 'BOTH', 'CALL', 'CAME', 'COME', 'DARK', 'DOES', 'DONE', 'DOOR',
    'DOWN', 'DRUG', 'EAST', 'FACE', 'FACT', 'FAIL', 'FAIR', 'FALL', 'FEEL',
    'FELT', 'FILE', 'FILL', 'FIRE', 'FIRM', 'FISH', 'FIVE', 'FLAT', 'FLOW',
    'FOLK', 'FOOD', 'FOOT', 'FORM', 'FORT', 'FOUL', 'FOUR', 'FREE', 'FROM',
    'FULL', 'GAME', 'GANG', 'GATE', 'GAVE', 'GEAR', 'GIVE', 'GLAD', 'GOAL',
    'GOAT', 'GOES', 'GOLD', 'GONE', 'GRAB', 'GRAY', 'GREW', 'GREY', 'GRID',
    'GRIM', 'GRIP', 'GROW', 'GULF', 'HACK', 'HAIR', 'HALF', 'HALL', 'HANG',
    'HARD', 'HARM', 'HATE', 'HAVE', 'HAWK', 'HEAD', 'HEAR', 'HEAT', 'HEED',
    'HELD', 'HELP', 'HERE', 'HERO', 'HIGH', 'HILL', 'HIVE', 'HOLD', 'HOLE',
    'HOLY', 'HORN', 'HOST', 'HOUR', 'HUGE', 'HUNG', 'HUNT', 'HURT', 'ICON',
    'IDEA', 'IDLE', 'INTO', 'IRON', 'ISLE', 'ITEM', 'JACK', 'JAIL', 'JAZZ',
    'JEAN', 'JERK', 'JEST', 'JINX', 'JOIN', 'JOKE', 'JOLT', 'JULY', 'JUMP',
    'JUNE', 'JUNK', 'JURY', 'JUST', 'KEEN', 'KEEP', 'KEPT', 'KICK', 'KILL',
    'KIND', 'KING', 'KISS', 'KNEE', 'KNEW', 'KNIT', 'KNOT', 'KNOW', 'LACK',
    'LADY', 'LAID', 'LAIR', 'LAKE', 'LAMP', 'LAND', 'LANE', 'LARK', 'LAST',
    'LATE', 'LEAD', 'LEAF', 'LEAK', 'LEAN', 'LEAP', 'LEFT', 'LEND', 'LENS',
    'LENT', 'LESS', 'LIAR', 'LICE', 'LICK', 'LIED', 'LIEN', 'LIES', 'LIFE',
    'LIFT', 'LIKE', 'LILT', 'LILY', 'LIMB', 'LIME', 'LIMP', 'LINE', 'LINK',
    'LION', 'LIPS', 'LIST', 'LIVE', 'LOAD', 'LOAF', 'LOAN', 'LOCK', 'LOFT',
    'LONE', 'LONG', 'LOOK', 'LOOP', 'LOOT', 'LORD', 'LORE', 'LOSE', 'LOSS',
    'LOST', 'LOUD', 'LOUP', 'LOUT', 'LOVE', 'LUCK', 'LUMP', 'LUNG', 'LURE',
    'LURK', 'LUSH', 'LUST', 'MAKE', 'MALE', 'MALL', 'MALT', 'MANE', 'MANY',
    'MARS', 'MASK', 'MASS', 'MAST', 'MATE', 'MATH', 'MAUL', 'MAZE', 'MEAD',
    'MEAL', 'MEAN', 'MEAT', 'MEET', 'MELT', 'MEMO', 'MEND', 'MENU', 'MERE',
    'MESH', 'MESS', 'MICA', 'MICE', 'MILD', 'MILE', 'MILK', 'MILL', 'MIME',
    'MIND', 'MINE', 'MINT', 'MISS', 'MIST', 'MITT', 'MOAN', 'MOAT', 'MODE',
    'MOLD', 'MOLE', 'MOLT', 'MONK', 'MOOD', 'MOON', 'MOOR', 'MOOT', 'MOPE',
    'MORE', 'MOSS', 'MOST', 'MOTH', 'MOVE', 'MUCH', 'MUCK', 'MULE', 'MUSE',
    'MUSH', 'MUSK', 'MUST', 'MUTE', 'MYTH', 'NAIL', 'NAME', 'NAPE', 'NAVY',
    'NEAR', 'NEAT', 'NECK', 'NEED', 'NEON', 'NEST', 'NEWS', 'NEXT', 'NICE',
    'NICK', 'NINE', 'NODE', 'NONE', 'NOON', 'NORM', 'NOSE', 'NOTE', 'NOUN',
    'OAKS', 'OATH', 'OBEY', 'ODOR', 'OKAY', 'OMEN', 'OMIT', 'ONCE', 'ONLY',
    'ONTO', 'OOZE', 'OPAL', 'OPEN', 'ORAL', 'ORCA', 'ORES', 'OVAL', 'OVEN',
    'OVER', 'OWED', 'OWES', 'OWLS', 'OWNS', 'PACE', 'PACK', 'PAGE', 'PAID',
    'PAIL', 'PAIN', 'PAIR', 'PALE', 'PALL', 'PALM', 'PANE', 'PANG', 'PANT',
    'PARK', 'PART', 'PASS', 'PAST', 'PATH', 'PAVE', 'PAWN', 'PEAK', 'PEAL',
    'PEAR', 'PEAS', 'PEAT', 'PECK', 'PEEL', 'PEER', 'PELT', 'PENS', 'PENT',
    'PERK', 'PEST', 'PICK', 'PILE', 'PILL', 'PIMP', 'PINE', 'PING', 'PINK',
    'PINT', 'PIPE', 'PISS', 'PITH', 'PLAN', 'PLAY', 'PLEA', 'PLED', 'PLOD',
    'PLOP', 'PLOT', 'PLOW', 'PLOY', 'PLUG', 'PLUM', 'PLUS', 'POKE', 'POLE',
    'POLL', 'POLO', 'POND', 'PONY', 'POOL', 'POOR', 'POPE', 'PORK', 'PORT',
    'POSE', 'POST', 'POSY', 'POUR', 'POUT', 'PRAY', 'PREP', 'PREY', 'PRIM',
    'PROD', 'PROM', 'PROP', 'PREY', 'PULL', 'PULP', 'PUMA', 'PUMP', 'PUNK',
    'PURE', 'PURR', 'PUSH', 'RACE', 'RACK', 'RAFT', 'RAGE', 'RAID', 'RAIL',
    'RAIN', 'RAKE', 'RAMP', 'RANG', 'RANK', 'RANT', 'RARE', 'RASH', 'RATE',
    'RATS', 'RAVE', 'RAYS', 'READ', 'REAL', 'REAM', 'REAP', 'REAR', 'REDO',
    'REDS', 'REED', 'REEF', 'REEK', 'REEL', 'RELY', 'REND', 'RENT', 'REST',
    'RICE', 'RICH', 'RIDE', 'RIFE', 'RIFT', 'RIGHT', 'RIMS', 'RIND', 'RING',
    'RINK', 'RIOT', 'RIPE', 'RISE', 'RISK', 'RITE', 'ROAD', 'ROAM', 'ROAR',
    'ROBE', 'ROCK', 'RODE', 'ROLE', 'ROLL', 'ROOF', 'ROOM', 'ROOT', 'ROPE',
    'ROSE', 'ROSY', 'ROTE', 'ROTS', 'ROUT', 'ROVE', 'ROWS', 'RUBS', 'RUDE',
    'RUED', 'RUIN', 'RULE', 'RUNG', 'RUNS', 'RUSE', 'RUSH', 'RUST', 'SAFE',
    'SAGA', 'SAGE', 'SAID', 'SAIL', 'SAKE', 'SALE', 'SALT', 'SAME', 'SAND',
    'SANE', 'SANG', 'SANK', 'SASH', 'SAVE', 'SAWS', 'SAYS', 'SEAL', 'SEAM',
    'SEAS', 'SEAT', 'SECT', 'SEED', 'SEEK', 'SEEM', 'SEEN', 'SELF', 'SELL',
    'SEMI', 'SEND', 'SENT', 'SETS', 'SEWN', 'SEWS', 'SHAD', 'SHAG', 'SHAM',
    'SHAW', 'SHED', 'SHIM', 'SHIN', 'SHIP', 'SHOE', 'SHOD', 'SHOO', 'SHOP',
    'SHOT', 'SHOW', 'SHUT', 'SICK', 'SIDE', 'SIFT', 'SIGH', 'SIGN', 'SILK',
    'SILL', 'SILO', 'SING', 'SINK', 'SIPS', 'SIRE', 'SITE', 'SIZE', 'SKID',
    'SKIM', 'SKIN', 'SKIP', 'SLAB', 'SLAG', 'SLAM', 'SLAP', 'SLAT', 'SLAW',
    'SLAY', 'SLED', 'SLEW', 'SLID', 'SLIM', 'SLIP', 'SLIT', 'SLOB', 'SLOP',
    'SLOT', 'SLOW', 'SLUG', 'SLUM', 'SMOG', 'SNAP', 'SNOW', 'SNUB', 'SNUG',
    'SOAK', 'SOAP', 'SOAR', 'SOBS', 'SOCK', 'SODA', 'SOFT', 'SOIL', 'SOLD',
    'SOLE', 'SOLO', 'SOME', 'SONG', 'SOON', 'SOOT', 'SORE', 'SORT', 'SOUL',
    'SOUP', 'SOUR', 'SPAN', 'SPAR', 'SPAT', 'SPEC', 'SPED', 'SPIN', 'SPIT',
    'SPOT', 'STAB', 'STAG', 'STAR', 'STAT', 'STAY', 'STEM', 'STEP', 'STEW',
    'STIR', 'STOP', 'STUB', 'STUD', 'SUCH', 'SUDS', 'SUED', 'SUIT', 'SULK',
    'SUMS', 'SUNG', 'SUNK', 'SURE', 'SURF', 'SWAB', 'SWAM', 'SWAN', 'SWAP',
    'SWAY', 'SWIM', 'SWUM', 'TACK', 'TACO', 'TAIL', 'TAKE', 'TALE', 'TALK',
    'TALL', 'TAME', 'TANK', 'TAPE', 'TAPS', 'TARE', 'TARN', 'TARP', 'TART',
    'TASK', 'TAUT', 'TAXI', 'TEAK', 'TEAL', 'TEAM', 'TEAR', 'TEAS', 'TEAT',
    'TEEM', 'TELL', 'TEMP', 'TEND', 'TENS', 'TENT', 'TERM', 'TERN', 'TEST',
    'TEXT', 'THAN', 'THAT', 'THAW', 'THEE', 'THEM', 'THEN', 'THEY', 'THIN',
    'THIS', 'THOU', 'THUD', 'THUS', 'TICK', 'TIDE', 'TIDY', 'TIED', 'TIER',
    'TIES', 'TIFF', 'TIER', 'TIFF', 'TILE', 'TILL', 'TILT', 'TIME', 'TINT',
    'TINY', 'TIPS', 'TIRE', 'TOAD', 'TOES', 'TOGS', 'TOIL', 'TOLD', 'TOLL',
    'TOMB', 'TOME', 'TONE', 'TONS', 'TOOK', 'TOOL', 'TOPS', 'TORE', 'TORN',
    'TOSS', 'TOUR', 'TOUT', 'TOWN', 'TOYS', 'TRAP', 'TRAY', 'TREE', 'TREK',
    'TRIM', 'TRIO', 'TRIP', 'TROD', 'TROT', 'TRUE', 'TUBA', 'TUBE', 'TUBS',
    'TUCK', 'TUNA', 'TUNE', 'TURD', 'TURF', 'TURN', 'TUSK', 'TUTU', 'TWAS',
    'TWIG', 'TWIN', 'TWIT', 'TYPE', 'UGLY', 'UNDO', 'UNIT', 'UPON', 'URGE',
    'URNS', 'USED', 'USER', 'USES', 'VAIN', 'VALE', 'VAMP', 'VANE', 'VARY',
    'VASE', 'VAST', 'VEAL', 'VEIL', 'VEIN', 'VENT', 'VERB', 'VERY', 'VEST',
    'VETO', 'VICE', 'VIED', 'VIEW', 'VILE', 'VINE', 'VISA', 'VISE', 'VOID',
    'VOTE', 'VOWS', 'WAGE', 'WAIL', 'WAIT', 'WAKE', 'WALK', 'WALL', 'WAND',
    'WANE', 'WANT', 'WARD', 'WARE', 'WARM', 'WARN', 'WARP', 'WARS', 'WART',
    'WASH', 'WASP', 'WAVE', 'WAVY', 'WAXY', 'WAYS', 'WEAK', 'WEAN', 'WEAR',
    'WEARY', 'WEBS', 'WEED', 'WEEK', 'WEEP', 'WEIR', 'WELD', 'WELL', 'WELT',
    'WENT', 'WERE', 'WEST', 'WETS', 'WHAM', 'WHAT', 'WHEE', 'WHEN', 'WHET',
    'WHEW', 'WHICH', 'WHILE', 'WHIM', 'WHINE', 'WHIP', 'WHIR', 'WHISK', 'WHITE',
    'WHIZ', 'WHOM', 'WHOP', 'WICK', 'WIDE', 'WIFE', 'WIGS', 'WILD', 'WILE',
    'WILL', 'WILT', 'WILY', 'WIMP', 'WIND', 'WINE', 'WING', 'WINK', 'WINS',
    'WIPE', 'WIRE', 'WIRY', 'WISE', 'WISH', 'WISP', 'WITH', 'WITS', 'WOKE',
    'WOLF', 'WOMB', 'WOMEN', 'WONT', 'WOOD', 'WOOL', 'WORD', 'WORE', 'WORK',
    'WORM', 'WORN', 'WRAP', 'WREN', 'WRIT', 'YAKS', 'YARD', 'YARN', 'YAWN',
    'YEAR', 'YEAS', 'YELL', 'YENS', 'YEPS', 'YOKE', 'YOLK', 'YOUR', 'YULE',
    'ZEAL', 'ZERO', 'ZEST', 'ZINC', 'ZONE', 'ZOOM',
])

def vigenere_decrypt(ciphertext, key, alphabet):
    """Decrypt using Vigenere cipher with custom alphabet"""
    plaintext = []
    key_index = 0

    for char in ciphertext:
        if char not in alphabet:
            plaintext.append(char)
            continue

        char_pos = alphabet.index(char)
        key_char = key[key_index % len(key)]
        key_pos = alphabet.index(key_char)

        plain_pos = (char_pos - key_pos) % len(alphabet)
        plaintext.append(alphabet[plain_pos])
        key_index += 1

    return ''.join(plaintext)

def count_english_words(text, word_set):
    """Count English words in text"""
    words = re.findall(r'[A-Za-z]+', text)
    count = 0
    matched_words = []

    for word in words:
        word_upper = word.upper()
        if len(word_upper) >= 3 and word_upper in word_set:
            count += 1
            matched_words.append(word_upper)

    return count, matched_words

def main():
    K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    fixed_5_15 = "ELYOIECBAQK"
    fixed_16_24 = "VAATCRDUM"

    print("=" * 120)
    print("KRYPTOS K4 - SYSTEMATIC BRUTE FORCE TEST")
    print("Testing all 26^4 = 456,976 combinations for positions 0, 1, 2, 3")
    print("=" * 120)
    print(f"\nCiphertext: {K4}")
    print(f"Alphabet: {KRYPTOS_ALPHABET}")
    print(f"Fixed positions 5-15: {fixed_5_15}")
    print(f"Fixed positions 16-24: {fixed_16_24}")
    print(f"Word list: {len(COMMON_WORDS)} English words (3+ letters)\n")

    results = []
    total = 26 ** 4

    print("Testing all combinations...")
    tested = 0

    for i0 in range(26):
        for i1 in range(26):
            for i2 in range(26):
                for i3 in range(26):
                    # Build key for positions 0-3
                    key_part = (KRYPTOS_ALPHABET[i0] +
                               KRYPTOS_ALPHABET[i1] +
                               KRYPTOS_ALPHABET[i2] +
                               KRYPTOS_ALPHABET[i3])

                    # Full key (positions 0-3, 5-15, 16-24)
                    full_key = key_part + fixed_5_15 + fixed_16_24

                    # Decrypt
                    plaintext = vigenere_decrypt(K4, full_key, KRYPTOS_ALPHABET)

                    # Count words
                    word_count, found_words = count_english_words(plaintext, COMMON_WORDS)

                    # Store if any words found
                    if word_count > 0:
                        results.append({
                            'word_count': word_count,
                            'key_part': key_part,
                            'full_key': full_key,
                            'plaintext': plaintext,
                            'words': found_words
                        })

                    tested += 1
                    if tested % 50000 == 0:
                        pct = 100.0 * tested / total
                        print(f"  {tested:>7,} / {total:,} ({pct:>5.1f}%)")

    print(f"\n[*] Completed! Found {len(results):,} combinations with English words")
    print()

    # Sort by word count
    results.sort(reverse=True, key=lambda x: x['word_count'])

    # Print top 20
    print("=" * 120)
    print("TOP 20 RESULTS BY WORD COUNT")
    print("=" * 120)

    if not results:
        print("\n[!] No combinations found with recognizable English words!")
        print("[!] This may indicate:")
        print("    - Positions 0-3 are not the correct unknown positions")
        print("    - The fixed key parts may be incorrect")
        print("    - The ciphertext may use a different structure")
        return

    for rank, result in enumerate(results[:20], 1):
        print(f"\n{rank}. Words: {result['word_count']} | Key (0-3): {result['key_part']}")
        print(f"   Full Key: {result['full_key']}")
        print(f"   English Words Found: {result['words'][:15]}" +
              (f"... + {len(result['words']) - 15} more" if len(result['words']) > 15 else ""))
        print(f"   Plaintext:\n   {result['plaintext']}")

if __name__ == "__main__":
    main()
