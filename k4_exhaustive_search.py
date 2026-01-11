#!/usr/bin/env python3
"""
K4 Exhaustive Word Search

Do an exhaustive search trying to maximize the number of English words found.
Test all combinations of starting words and words at various positions.
"""

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Fixed key constraints
BERLINCLOCK_KEY = {5: 'E', 6: 'L', 7: 'Y', 8: 'O', 9: 'I', 10: 'E', 11: 'C', 12: 'B', 13: 'A', 14: 'Q', 15: 'K'}
NORTHEAST_KEY = {16: 'V', 17: 'A', 18: 'A', 19: 'T', 20: 'C', 21: 'R', 22: 'D', 23: 'U', 24: 'M'}

def derive_key_char(ct_char, pt_char, alpha=KRYPTOS_ALPHA):
    ct_pos = alpha.index(ct_char)
    pt_pos = alpha.index(pt_char)
    key_val = (ct_pos - pt_pos) % len(alpha)
    return alpha[key_val]

def vigenere_decrypt(ct, key, alpha=KRYPTOS_ALPHA):
    result = []
    for i, c in enumerate(ct):
        ct_pos = alpha.index(c)
        key_pos = alpha.index(key[i % len(key)])
        pt_pos = (ct_pos - key_pos) % len(alpha)
        result.append(alpha[pt_pos])
    return ''.join(result)

# More comprehensive English word list
ENGLISH_WORDS = set([
    # 3-letter
    'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 'WAS', 'ONE',
    'OUR', 'OUT', 'HIS', 'HAS', 'ITS', 'NOW', 'HIM', 'HOW', 'MAN', 'NEW', 'WAY', 'DAY',
    'TWO', 'USE', 'SET', 'END', 'SEE', 'SAY', 'SHE', 'OWN', 'OLD', 'WHO', 'WHY', 'TRY',
    'DIG', 'DUG', 'MAP', 'KEY', 'SIX', 'TEN', 'RUN', 'SIT', 'LET', 'PUT', 'TOP', 'GET',
    'GOT', 'ASK', 'BOX', 'SUN', 'SKY', 'SEA', 'AIR', 'BAR', 'BIT', 'ODD', 'AGO', 'ERA',
    'FEW', 'FAR', 'LOW', 'BAD', 'BIG', 'CUT', 'LAY', 'LED', 'LIE', 'MET', 'NOR', 'OFF',
    'RAW', 'RED', 'ROW', 'RUB', 'TAP', 'TIE', 'WET', 'WON', 'YET', 'ADD', 'PER', 'ACE',
    'ACT', 'AGE', 'AID', 'AIM', 'ART', 'ATE', 'AWE', 'AXE', 'BAG', 'BAN', 'BAT', 'BAY',
    'BED', 'BET', 'BOW', 'BOY', 'BUS', 'BUY', 'CAB', 'CAP', 'CAR', 'CAT', 'COP', 'COW',
    'CRY', 'CUP', 'DAM', 'DEN', 'DEW', 'DOC', 'DOE', 'DOG', 'DOT', 'DRY', 'DUE', 'EAR',
    'EAT', 'EGG', 'ELF', 'ELM', 'EVE', 'EYE', 'FAN', 'FAT', 'FED', 'FEE', 'FIG', 'FIN',
    'FIT', 'FLY', 'FOE', 'FOG', 'FUN', 'FUR', 'GAP', 'GAS', 'GAY', 'GEM', 'GUN', 'GUT',
    'GUY', 'GYM', 'HAD', 'HAM', 'HAT', 'HAY', 'HEN', 'HID', 'HIP', 'HIT', 'HOG', 'HOP',
    'HOT', 'HUB', 'HUG', 'HUT', 'ICE', 'ICY', 'ILL', 'INN', 'ION', 'IVY', 'JAM', 'JAR',
    'JAW', 'JET', 'JOB', 'JOG', 'JOY', 'JUG', 'KID', 'KIT', 'LAB', 'LAD', 'LAP', 'LAW',
    'LEA', 'LEG', 'LID', 'LIP', 'LIT', 'LOG', 'LOT', 'MAD', 'MAT', 'MAY', 'MIX', 'MOB',
    'MOM', 'MOP', 'MUD', 'MUG', 'NAP', 'NET', 'NIT', 'NOD', 'NUN', 'NUT', 'OAK', 'OAT',
    'OIL', 'OPT', 'ORB', 'ORE', 'OWE', 'OWL', 'PAD', 'PAL', 'PAN', 'PAT', 'PAW', 'PAY',
    'PEA', 'PEG', 'PEN', 'PET', 'PIE', 'PIG', 'PIN', 'PIT', 'PLY', 'POD', 'POP', 'POT',
    'POW', 'PRO', 'PUB', 'PUN', 'PUP', 'RAG', 'RAM', 'RAN', 'RAP', 'RAT', 'RAY', 'REP',
    'RIB', 'RID', 'RIG', 'RIM', 'RIP', 'ROB', 'ROD', 'ROT', 'RUG', 'SAD', 'SAP', 'SAT',
    'SAW', 'SKI', 'SOB', 'SOD', 'SON', 'SOP', 'SOT', 'SOW', 'SOY', 'SPA', 'SPY', 'STY',
    'SUB', 'SUM', 'SUP', 'TAB', 'TAG', 'TAN', 'TAR', 'TAX', 'TEA', 'TIN', 'TIP', 'TOE',
    'TON', 'TOO', 'TOW', 'TOY', 'TUB', 'TUG', 'URN', 'VAN', 'VAT', 'VET', 'VIA', 'VIE',
    'VOW', 'WAD', 'WAR', 'WAX', 'WEB', 'WED', 'WIG', 'WIN', 'WIT', 'WOE', 'WOK', 'ZAP',
    'ZEN', 'ZIP', 'ZOO',
    # 4-letter
    'THAT', 'WITH', 'HAVE', 'THIS', 'WILL', 'YOUR', 'FROM', 'THEY', 'BEEN', 'CALL',
    'FIND', 'MANY', 'THEN', 'ALSO', 'INTO', 'JUST', 'OVER', 'SUCH', 'THAN', 'THEM',
    'WELL', 'WERE', 'SOME', 'TIME', 'VERY', 'WHEN', 'COME', 'MADE', 'EACH', 'ONLY',
    'KNOW', 'TAKE', 'YEAR', 'WORK', 'LAST', 'HERE', 'PART', 'SAID', 'BACK', 'MAKE',
    'LOOK', 'EVEN', 'MOST', 'LIKE', 'WHAT', 'MUST', 'LONG', 'EAST', 'WEST', 'NEAR',
    'LEFT', 'SIDE', 'HIGH', 'TURN', 'HEAD', 'HAND', 'FEET', 'DOOR', 'DOWN', 'UPON',
    'ROOM', 'AREA', 'SITE', 'BURY', 'DEEP', 'HIDE', 'TRUE', 'NEXT', 'WALL', 'STEP',
    'ZERO', 'FIVE', 'FOUR', 'NINE', 'HALF', 'MARK', 'LINE', 'PASS', 'PATH', 'YARD',
    'MILE', 'INCH', 'SPOT', 'CITY', 'GATE', 'SPAN', 'OPEN', 'WIDE', 'DARK', 'FIRE',
    'LAND', 'ROCK', 'TOMB', 'GOLD', 'COAL', 'IRON', 'CLAY', 'SAND', 'SOIL', 'TREE',
    'CODE', 'CLUE', 'HINT', 'WORD', 'TEXT', 'NOTE', 'SIGN', 'NAME', 'TELL', 'READ',
    'MOVE', 'KEEP', 'HOLD', 'LEAD', 'SEEK', 'SHOW', 'GAVE', 'FORM', 'GOES', 'GONE',
    'CAME', 'FELL', 'SENT', 'TOLD', 'TOOK', 'KNEW', 'COPY', 'PAST', 'SAFE', 'LOCK',
    'FACE', 'FACT', 'FAIL', 'FAIR', 'FALL', 'FAME', 'FAST', 'FATE', 'FEAR', 'FEED',
    'FEEL', 'FILE', 'FILL', 'FILM', 'FIRM', 'FISH', 'FLAG', 'FLAT', 'FLEW', 'FLOW',
    'FOLK', 'FOOD', 'FOOL', 'FOOT', 'FORE', 'FORK', 'FORT', 'FREE', 'FUEL', 'FULL',
    'FUND', 'GAIN', 'GAME', 'GAVE', 'GEAR', 'GIRL', 'GIVE', 'GLAD', 'GLOW', 'GOAL',
    'GOES', 'GOLF', 'GOOD', 'GRAB', 'GRAY', 'GREW', 'GREY', 'GRID', 'GRIM', 'GRIP',
    'GROW', 'GULF', 'GURU', 'GUYS', 'HACK', 'HAIL', 'HAIR', 'HALL', 'HALT', 'HANG',
    'HARD', 'HARM', 'HATE', 'HAUL', 'HEAL', 'HEAP', 'HEAR', 'HEAT', 'HEEL', 'HELD',
    'HELL', 'HELP', 'HERD', 'HERO', 'HILL', 'HIRE', 'HOLD', 'HOLE', 'HOLY', 'HOME',
    'HOOD', 'HOOK', 'HOPE', 'HORN', 'HOST', 'HOUR', 'HUGE', 'HUNG', 'HUNT', 'HURT',
    'ICON', 'IDEA', 'INCH', 'INTO', 'IRON', 'ITEM', 'JACK', 'JAIL', 'JAZZ', 'JEAN',
    'JOIN', 'JOKE', 'JUMP', 'JURY', 'KEEN', 'KEPT', 'KICK', 'KILL', 'KIND', 'KING',
    'KISS', 'KNEE', 'KNEW', 'KNIT', 'KNOB', 'KNOT', 'LACK', 'LAID', 'LAKE', 'LAMB',
    'LAMP', 'LANE', 'LATE', 'LAWN', 'LAWS', 'LEAD', 'LEAF', 'LEAN', 'LEAP', 'LEFT',
    'LEND', 'LENS', 'LESS', 'LEVY', 'LIAR', 'LIES', 'LIFE', 'LIFT', 'LIMB', 'LINK',
    'LION', 'LIST', 'LIVE', 'LOAD', 'LOAN', 'LOFT', 'LOGO', 'LONE', 'LOOP', 'LORD',
    'LOSE', 'LOSS', 'LOST', 'LOTS', 'LOUD', 'LOVE', 'LUCK', 'LUNG', 'LURE', 'LUSH',
    'MAID', 'MAIL', 'MAIN', 'MALL', 'MAPS', 'MARE', 'MARS', 'MASK', 'MASS', 'MATE',
    'MATH', 'MEAL', 'MEAN', 'MEAT', 'MEET', 'MELT', 'MEMO', 'MENU', 'MERE', 'MESH',
    'MESS', 'MILD', 'MILK', 'MILL', 'MIND', 'MINE', 'MINT', 'MISS', 'MODE', 'MOOD',
    'MOON', 'MORE', 'MOSS', 'MOTH', 'MUCH', 'MYTH', 'NAIL', 'NAVY', 'NECK', 'NEED',
    'NEST', 'NEWS', 'NICE', 'NODE', 'NONE', 'NOON', 'NORM', 'NOSE', 'NOUN', 'NUDE',
    # 5-letter
    'ABOUT', 'ABOVE', 'ABUSE', 'ACTED', 'ACTOR', 'ADAPT', 'ADDED', 'ADMIT', 'ADOPT',
    'ADULT', 'AFTER', 'AGAIN', 'AGENT', 'AGING', 'AGREE', 'AHEAD', 'AIDED', 'AIMED',
    'ALARM', 'ALBUM', 'ALERT', 'ALIEN', 'ALIGN', 'ALIKE', 'ALIVE', 'ALLEY', 'ALLOW',
    'ALONE', 'ALONG', 'ALTER', 'AMONG', 'ANGEL', 'ANGER', 'ANGLE', 'ANGRY', 'APART',
    'APPLE', 'APPLY', 'ARENA', 'ARGUE', 'ARISE', 'ARMED', 'ARMOR', 'ARRAY', 'ARROW',
    'ASIDE', 'ASSET', 'AVOID', 'AWAIT', 'AWAKE', 'AWARD', 'AWARE', 'AWFUL', 'BASIC',
    'BASIS', 'BEACH', 'BEARS', 'BEAST', 'BEGAN', 'BEGIN', 'BEGUN', 'BEING', 'BELOW',
    'BENCH', 'BERRY', 'BIRTH', 'BLACK', 'BLADE', 'BLAME', 'BLANK', 'BLAST', 'BLAZE',
    'BLEND', 'BLESS', 'BLIND', 'BLOCK', 'BLOOD', 'BLOWN', 'BLUES', 'BLUNT', 'BOARD',
    'BOAST', 'BONUS', 'BOOKS', 'BOOST', 'BOOTH', 'BOOTS', 'BOUND', 'BOXER', 'BRAIN',
    'BRAND', 'BRASS', 'BRAVE', 'BREAD', 'BREAK', 'BREED', 'BRICK', 'BRIDE', 'BRIEF',
    'BRING', 'BROAD', 'BROKE', 'BROOK', 'BROWN', 'BRUSH', 'BUILD', 'BUILT', 'BUNCH',
    'BURST', 'BUYER', 'CABIN', 'CABLE', 'CACHE', 'CARDS', 'CARGO', 'CARRY', 'CATCH',
    'CAUSE', 'CEASE', 'CHAIN', 'CHAIR', 'CHAOS', 'CHARM', 'CHART', 'CHASE', 'CHEAP',
    'CHECK', 'CHEST', 'CHIEF', 'CHILD', 'CHINA', 'CHOSE', 'CHUNK', 'CIVIC', 'CIVIL',
    'CLAIM', 'CLASS', 'CLEAN', 'CLEAR', 'CLERK', 'CLICK', 'CLIFF', 'CLIMB', 'CLOCK',
    'CLONE', 'CLOSE', 'CLOTH', 'CLOUD', 'CLUBS', 'CLUES', 'COACH', 'COAST', 'COULD',
    'COUNT', 'COURT', 'COVER', 'CRACK', 'CRAFT', 'CRASH', 'CRAZY', 'CREAM', 'CRIME',
    'CRISP', 'CROSS', 'CROWD', 'CROWN', 'CRUDE', 'CRUEL', 'CRUSH', 'CRYPT', 'CURVE',
    'CYCLE', 'DAILY', 'DAIRY', 'DANCE', 'DATED', 'DEALS', 'DEALT', 'DEATH', 'DEBUT',
    'DECAY', 'DELAY', 'DENSE', 'DEPTH', 'DETER', 'DIARY', 'DIGIT', 'DIRTY', 'DOING',
    'DOUBT', 'DOZEN', 'DRAFT', 'DRAIN', 'DRAMA', 'DRANK', 'DRAWN', 'DREAD', 'DREAM',
    'DRESS', 'DRIED', 'DRIFT', 'DRILL', 'DRINK', 'DRIVE', 'DROIT', 'DROPS', 'DROWN',
    'DRUNK', 'DYING', 'EAGER', 'EARLY', 'EARTH', 'EATEN', 'EATER', 'EDGES', 'EIGHT',
    'ELDER', 'ELECT', 'ELITE', 'EMPTY', 'ENEMY', 'ENJOY', 'ENTER', 'ENTRY', 'EQUAL',
    'EQUIP', 'ERROR', 'ESSAY', 'ETHER', 'EVENT', 'EVERY', 'EXACT', 'EXAMS', 'EXIST',
    'EXTRA', 'FADED', 'FAILS', 'FAINT', 'FAIRY', 'FAITH', 'FALSE', 'FAMED', 'FANCY',
    'FATAL', 'FAULT', 'FAVOR', 'FEAST', 'FEELS', 'FEWER', 'FIBER', 'FIELD', 'FIFTH',
    'FIFTY', 'FIGHT', 'FILED', 'FILMS', 'FINAL', 'FINDS', 'FIRED', 'FIRMS', 'FIRST',
    'FIXED', 'FLAGS', 'FLAME', 'FLASH', 'FLESH', 'FLIES', 'FLOAT', 'FLOCK', 'FLOOD',
    'FLOOR', 'FLOUR', 'FLOWS', 'FLUID', 'FLUSH', 'FOCAL', 'FOCUS', 'FOLKS', 'FORCE',
    'FORMS', 'FORTH', 'FORTY', 'FORUM', 'FOUND', 'FRAME', 'FRANK', 'FRAUD', 'FREED',
    'FRESH', 'FRIED', 'FRONT', 'FROST', 'FRUIT', 'FULLY', 'FUNDS', 'FUNNY', 'GAINS',
    'GAMES', 'GASES', 'GAUGE', 'GIANT', 'GIFTS', 'GIVEN', 'GIVES', 'GIVER', 'GLASS',
    'GLOBE', 'GLORY', 'GOALS', 'GOING', 'GOODS', 'GRACE', 'GRADE', 'GRAIN', 'GRAND',
    'GRANT', 'GRAPH', 'GRASP', 'GRASS', 'GRAVE', 'GRAYS', 'GREAT', 'GREEK', 'GREEN',
    'GREET', 'GRIEF', 'GRILL', 'GRIME', 'GRIND', 'GRIPS', 'GROSS', 'GROUP', 'GROVE',
    'GROWN', 'GROWS', 'GUARD', 'GUESS', 'GUEST', 'GUIDE', 'GUILD', 'GUILT', 'HABIT',
    'HALLS', 'HANDS', 'HANDY', 'HANGS', 'HAPPY', 'HARSH', 'HASTE', 'HAVEN', 'HEADS',
    'HEARD', 'HEART', 'HEATH', 'HEAVY', 'HEDGE', 'HEELS', 'HEIRS', 'HELLO', 'HELPS',
    'HENCE', 'HERBS', 'HILLS', 'HINTS', 'HIRED', 'HOBBY', 'HOLDS', 'HOLES', 'HOMES',
    'HONEY', 'HONOR', 'HOPED', 'HOPES', 'HORSE', 'HOSTS', 'HOTEL', 'HOURS', 'HOUSE',
    'HUMAN', 'HUMID', 'HUMOR', 'HURRY', 'HURTS', 'IDEAL', 'IDEAS', 'IMAGE', 'INDEX',
    'INDIA', 'INNER', 'INPUT', 'INTEL', 'INTER', 'INTRO', 'IRONY', 'ISSUE', 'ITEMS',
    'JAPAN', 'JESUS', 'JEWEL', 'JOANN', 'JOINT', 'JOKES', 'JONES', 'JUDGE', 'JUICE',
    'JUICY', 'JUMPS', 'KEEPS', 'KILLS', 'KINDS', 'KINGS', 'KNEES', 'KNIFE', 'KNOCK',
    'KNOWN', 'KNOWS', 'LABEL', 'LABOR', 'LACKS', 'LAMPS', 'LANDS', 'LANES', 'LARGE',
    'LASER', 'LATER', 'LATIN', 'LAUGH', 'LAYER', 'LEADS', 'LEAFS', 'LEAKS', 'LEAPS',
    'LEARN', 'LEASE', 'LEAST', 'LEAVE', 'LEGAL', 'LEMON', 'LEVEL', 'LEVER', 'LEWIS',
    'LIARS', 'LIBEL', 'LIDAR', 'LIFES', 'LIGHT', 'LIKED', 'LIKES', 'LIMBS', 'LIMIT',
    'LINED', 'LINER', 'LINES', 'LINKS', 'LIONS', 'LISTS', 'LITER', 'LIVED', 'LIVER',
    'LIVES', 'LOANS', 'LOCAL', 'LOCKS', 'LODGE', 'LOFTY', 'LOGIC', 'LOGOS', 'LOOKS',
    'LOOSE', 'LORDS', 'LOSES', 'LOVED', 'LOVER', 'LOVES', 'LOWER', 'LOYAL', 'LUCKY',
    'LUNAR', 'LUNCH', 'LYING', 'MAGIC', 'MAJOR', 'MAKER', 'MALES', 'MANOR', 'MAPLE',
    'MARCH', 'MARIA', 'MARKS', 'MARRY', 'MARSH', 'MASKS', 'MATCH', 'MATES', 'MATTE',
    'MAYBE', 'MAYOR', 'MEANS', 'MEANT', 'MEDAL', 'MEDIA', 'MEETS', 'MELON', 'MERCY',
    'MERGE', 'MERIT', 'MERRY', 'MESSY', 'METAL', 'METER', 'METRO', 'MICRO', 'MIDST',
    'MIGHT', 'MILES', 'MILLS', 'MINDS', 'MINED', 'MINER', 'MINES', 'MINOR', 'MINUS',
    'MIXED', 'MIXER', 'MODEL', 'MODES', 'MONEY', 'MONTH', 'MOODS', 'MORAL', 'MOTOR',
    'MOUNT', 'MOUSE', 'MOUTH', 'MOVED', 'MOVER', 'MOVES', 'MOVIE', 'MUDDY', 'MULTI',
    'MUSIC', 'NAILS', 'NAIVE', 'NAKED', 'NAMED', 'NAMES', 'NASTY', 'NAVAL', 'NEEDS',
    'NERVE', 'NEVER', 'NEWER', 'NEWLY', 'NEXUS', 'NIGHT', 'NINTH', 'NOBLE', 'NODES',
    'NOISE', 'NOISY', 'NORMS', 'NORTH', 'NOTCH', 'NOTED', 'NOTES', 'NOVEL', 'NURSE',
    'OCCUR', 'OCEAN', 'OFFER', 'OFTEN', 'OLIVE', 'ONSET', 'OPENS', 'OPERA', 'ORBIT',
    'ORDER', 'OTHER', 'OUGHT', 'OUNCE', 'OUTER', 'OUTGO', 'OWNED', 'OWNER', 'OXIDE',
    'OZONE', 'PACED', 'PACKS', 'PAGES', 'PAINT', 'PAIRS', 'PANEL', 'PANIC', 'PANTS',
    'PAPER', 'PARKS', 'PARTY', 'PASTA', 'PASTE', 'PATCH', 'PATHS', 'PAUSE', 'PEACE',
    'PEAKS', 'PEARL', 'PEERS', 'PENNY', 'PERKS', 'PESTS', 'PETTY', 'PHASE', 'PHONE',
    'PHOTO', 'PIANO', 'PICKS', 'PIECE', 'PILES', 'PILOT', 'PINCH', 'PIPES', 'PITCH',
    'PIZZA', 'PLACE', 'PLAIN', 'PLANE', 'PLANS', 'PLANT', 'PLATE', 'PLAYS', 'PLAZA',
    'PLEAD', 'PLOTS', 'PLUGS', 'PLUMS', 'PLUSH', 'POEMS', 'POETS', 'POINT', 'POLAR',
    'POLES', 'POLLS', 'PONDS', 'POOLS', 'POPUP', 'PORCH', 'PORES', 'PORTS', 'POSED',
    'POSES', 'POSTS', 'POUCH', 'POUND', 'POWER', 'PRESS', 'PRICE', 'PRIDE', 'PRIME',
    'PRINT', 'PRIOR', 'PRIZE', 'PROBE', 'PROMO', 'PRONE', 'PROOF', 'PROPS', 'PROSE',
    'PROUD', 'PROVE', 'PROXY', 'PULSE', 'PUMPS', 'PUPIL', 'PURSE', 'QUEEN', 'QUERY',
    'QUEST', 'QUEUE', 'QUICK', 'QUIET', 'QUILT', 'QUITE', 'QUOTA', 'QUOTE', 'RACES',
    'RADAR', 'RADIO', 'RAILS', 'RAISE', 'RALLY', 'RANCH', 'RANGE', 'RANKS', 'RAPID',
    'RATED', 'RATES', 'RATIO', 'REACH', 'REACT', 'READS', 'READY', 'REALM', 'REBEL',
    'REFER', 'REIGN', 'RELAX', 'RELAY', 'REPAY', 'REPLY', 'RESET', 'RIDGE', 'RIFLE',
    'RIGHT', 'RIGID', 'RINGS', 'RISEN', 'RISES', 'RISKS', 'RISKY', 'RITZY', 'RIVAL',
    'RIVER', 'ROADS', 'ROCKS', 'ROCKY', 'ROLES', 'ROMAN', 'ROOMS', 'ROOTS', 'ROPES',
    'ROSES', 'ROUGE', 'ROUGH', 'ROUND', 'ROUTE', 'ROYAL', 'RUGBY', 'RUINS', 'RULED',
    'RULER', 'RULES', 'RURAL', 'SADLY', 'SAFER', 'SAILS', 'SAINT', 'SALAD', 'SALES',
    'SALON', 'SALTS', 'SANDY', 'SAUCE', 'SAVED', 'SAVES', 'SCALE', 'SCAMS', 'SCARY',
    'SCENE', 'SCENT', 'SCOPE', 'SCORE', 'SCOUT', 'SCRAP', 'SCREW', 'SEALS', 'SEATS',
    'SEEDS', 'SEIZE', 'SELLS', 'SENSE', 'SERVE', 'SETUP', 'SEVEN', 'SHADE', 'SHAFT',
    'SHAKE', 'SHALL', 'SHAME', 'SHAPE', 'SHARE', 'SHARP', 'SHEER', 'SHEET', 'SHELF',
    'SHELL', 'SHIFT', 'SHINE', 'SHINY', 'SHIPS', 'SHIRT', 'SHOCK', 'SHOES', 'SHOOK',
    'SHOOT', 'SHOPS', 'SHORE', 'SHORT', 'SHOTS', 'SHOWN', 'SHOWS', 'SIDES', 'SIEGE',
    'SIGHT', 'SIGMA', 'SIGNS', 'SILLY', 'SINCE', 'SITES', 'SIXTH', 'SIXTY', 'SIZED',
    'SIZES', 'SKILL', 'SKINS', 'SKIRT', 'SKULL', 'SLATE', 'SLAVE', 'SLEEK', 'SLEEP',
    'SLICK', 'SLIDE', 'SLOPE', 'SLOTS', 'SMALL', 'SMART', 'SMELL', 'SMILE', 'SMITH',
    'SMOKE', 'SNAKE', 'SNEAK', 'SOLAR', 'SOLID', 'SOLVE', 'SONGS', 'SORRY', 'SORTS',
    'SOULS', 'SOUND', 'SOUTH', 'SPACE', 'SPARE', 'SPARK', 'SPAWN', 'SPEAK', 'SPEAR',
    'SPECS', 'SPEED', 'SPELL', 'SPEND', 'SPENT', 'SPICE', 'SPICY', 'SPILL', 'SPINE',
    'SPLIT', 'SPOKE', 'SPORT', 'SPOTS', 'SPRAY', 'SQUAD', 'STACK', 'STAFF', 'STAGE',
    'STAIN', 'STAKE', 'STAMP', 'STAND', 'STARE', 'STARK', 'STARS', 'START', 'STATE',
    'STAYS', 'STEAK', 'STEAL', 'STEAM', 'STEEL', 'STEEP', 'STEER', 'STEMS', 'STEPS',
    'STICK', 'STIFF', 'STILL', 'STOCK', 'STOLE', 'STONE', 'STOOD', 'STOPS', 'STORE',
    'STORM', 'STORY', 'STOVE', 'STRAP', 'STRAW', 'STRIP', 'STUCK', 'STUDY', 'STUFF',
    'STYLE', 'SUGAR', 'SUITS', 'SUITE', 'SUNNY', 'SUPER', 'SURGE', 'SUSHI', 'SWAMP',
    'SWEAR', 'SWEAT', 'SWEEP', 'SWEET', 'SWEPT', 'SWIFT', 'SWING', 'SWORD', 'SWORN',
    'SWUNG', 'TABLE', 'TACIT', 'TAILS', 'TAKEN', 'TAKES', 'TALES', 'TALKS', 'TANKS',
    'TAPES', 'TASKS', 'TASTE', 'TAXES', 'TEACH', 'TEAMS', 'TEARS', 'TEDDY', 'TEENS',
    'TEETH', 'TELLS', 'TEMPO', 'TENDS', 'TENSE', 'TENTH', 'TERMS', 'TESTS', 'TEXTS',
    'THANK', 'THEFT', 'THEIR', 'THEME', 'THICK', 'THIEF', 'THING', 'THINK', 'THIRD',
    'THOSE', 'THREE', 'THREW', 'THROW', 'THUMB', 'TIDAL', 'TIERS', 'TIGER', 'TIGHT',
    'TILES', 'TIMER', 'TIMES', 'TIRED', 'TITLE', 'TODAY', 'TOKEN', 'TONES', 'TOOLS',
    'TOOTH', 'TOPIC', 'TORCH', 'TOTAL', 'TOUCH', 'TOUGH', 'TOURS', 'TOWER', 'TOWNS',
    'TOXIC', 'TRACE', 'TRACK', 'TRACT', 'TRADE', 'TRAIL', 'TRAIN', 'TRAIT', 'TRASH',
    'TREAT', 'TREES', 'TREND', 'TRIAL', 'TRIBE', 'TRICK', 'TRIED', 'TRIES', 'TRIPS',
    'TROOP', 'TRUCK', 'TRULY', 'TRUNK', 'TRUST', 'TRUTH', 'TUBES', 'TULIP', 'TUMOR',
    'TUNES', 'TURNS', 'TUTOR', 'TWICE', 'TWINS', 'TWIST', 'TYPED', 'TYPES', 'ULTRA',
    'UNCLE', 'UNDER', 'UNION', 'UNITE', 'UNITY', 'UNITS', 'UNTIL', 'UPPER', 'UPSET',
    'URBAN', 'URGED', 'USAGE', 'USERS', 'USING', 'USUAL', 'UTTER', 'VAGUE', 'VALID',
    'VALUE', 'VALVE', 'VAULT', 'VEGAS', 'VENUE', 'VERGE', 'VERSE', 'VIDEO', 'VIEWS',
    'VILLA', 'VINES', 'VINYL', 'VIRAL', 'VIRUS', 'VISIT', 'VITAL', 'VIVID', 'VOCAL',
    'VODKA', 'VOICE', 'VOTED', 'VOTER', 'VOTES', 'WAGED', 'WAGES', 'WAGON', 'WAIST',
    'WALKS', 'WALLS', 'WANTS', 'WASTE', 'WATCH', 'WATER', 'WAVES', 'WEARS', 'WEEKS',
    'WEIRD', 'WELLS', 'WELSH', 'WHALE', 'WHEAT', 'WHEEL', 'WHERE', 'WHICH', 'WHILE',
    'WHITE', 'WHOLE', 'WHOSE', 'WIDER', 'WIDOW', 'WIDTH', 'WILLS', 'WINDS', 'WINES',
    'WINGS', 'WIRED', 'WIRES', 'WITCH', 'WIVES', 'WOMAN', 'WOMEN', 'WOODS', 'WORDS',
    'WORKS', 'WORLD', 'WORRY', 'WORSE', 'WORST', 'WORTH', 'WOULD', 'WOUND', 'WRATH',
    'WRECK', 'WRIST', 'WRITE', 'WRONG', 'WROTE', 'YACHT', 'YARDS', 'YEARS', 'YEAST',
    'YIELD', 'YOUNG', 'YOURS', 'YOUTH', 'ZONES',
    # 6+ letters
    'BURIED', 'HIDDEN', 'SECRET', 'LOCATE', 'CENTER', 'CORNER', 'INSIDE', 'GROUND',
    'METERS', 'STAIRS', 'BEHIND', 'BESIDE', 'ACROSS', 'AROUND', 'TOWARD', 'WITHIN',
    'BEFORE', 'DURING', 'TWENTY', 'THIRTY', 'ELEVEN', 'TWELVE', 'DEGREE', 'MINUTE',
    'SECOND', 'SHADOW', 'DEEPER', 'HIGHER', 'SEARCH', 'FOLLOW', 'DIRECT', 'ONWARD',
    'UPWARD', 'INWARD', 'TUNNEL', 'CELLAR', 'MARKER', 'SIGNAL', 'CIPHER', 'TEMPLE',
    'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST',
    'BERLIN', 'BERLINCLOCK', 'CLOCK', 'WALL', 'GATE',
])

def find_non_overlapping_words(text, min_len=3):
    found = []
    for word in ENGLISH_WORDS:
        if len(word) >= min_len:
            pos = 0
            while True:
                idx = text.find(word, pos)
                if idx == -1:
                    break
                found.append((word, idx))
                pos = idx + 1
    found.sort(key=lambda x: (-len(x[0]), x[1]))
    result = []
    used = set()
    for word, pos in found:
        word_positions = set(range(pos, pos + len(word)))
        if not word_positions & used:
            result.append((word, pos))
            used.update(word_positions)
    return sorted(result, key=lambda x: x[1])

# Test all combinations to find patterns with maximum words
STARTING_WORDS = [
    'ARENA', 'LODGE', 'DIGIT', 'DRAWN', 'EIGHT', 'EVERY', 'HOURS', 'PRESS', 'ROCKS',
    'THEME', 'WOMAN', 'WORDS', 'WORKS', 'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOURS',
    'AHEAD', 'ALLOW', 'APART', 'BELOW', 'BRING', 'LEVEL', 'MANOR', 'MINOR', 'TOURS',
    'USERS', 'UNDER', 'ABOVE', 'FIRST', 'THERE', 'WHERE', 'COULD', 'THEIR', 'WHICH',
    'SOUTH', 'NORTH', 'EARTH', 'LAYER', 'DEPTH', 'FOUND', 'STONE', 'GRAVE', 'TRUTH',
    'CLOCK', 'SIGHT', 'POINT', 'START', 'PLACE', 'LIGHT', 'NIGHT', 'RIGHT', 'BLOCK',
]

WORDS_83 = [
    'DIG', 'DUG', 'LET', 'WAS', 'ADD', 'ALL', 'BUT', 'FEW', 'HER', 'ONE', 'RUB', 'SAY',
    'ASK', 'FIRST', 'THERE', 'THESE', 'WHERE', 'WHICH', 'AFTER', 'AGAIN', 'BEING',
    'COULD', 'EVERY', 'FOUND', 'GIVEN', 'GOING', 'GREAT', 'KNOWN', 'MIGHT', 'NEVER',
    'OTHER', 'PLACE', 'POINT', 'RIGHT', 'SHALL', 'SINCE', 'SMALL', 'SOUTH', 'STAND',
    'START', 'STATE', 'STILL', 'TAKEN', 'THINK', 'THOSE', 'THREE', 'TODAY', 'UNTIL',
    'WHILE', 'WHOLE', 'WORLD', 'WOULD', 'WRITE', 'YEARS', 'YOUNG', 'ABOVE', 'UNDER',
]

def test_combination(word0, word83, period=29):
    key = ['?'] * period
    for pos, char in BERLINCLOCK_KEY.items():
        key[pos] = char
    for pos, char in NORTHEAST_KEY.items():
        key[pos] = char

    for i, pt_char in enumerate(word0):
        if i < len(K4):
            ct_char = K4[i]
            key_char = derive_key_char(ct_char, pt_char)
            key[i % period] = key_char

    for i, pt_char in enumerate(word83):
        pos = 83 + i
        if pos < len(K4):
            ct_char = K4[pos]
            key_char = derive_key_char(ct_char, pt_char)
            key_pos = pos % period
            if key[key_pos] != '?' and key[key_pos] != key_char:
                return None
            key[key_pos] = key_char

    test_key = ''.join(c if c != '?' else 'K' for c in key)
    plaintext = vigenere_decrypt(K4, test_key)

    if plaintext[63:74] != 'BERLINCLOCK' or plaintext[16:25] != 'NORTHEAST':
        return None
    if plaintext[0:len(word0)] != word0 or plaintext[83:83+len(word83)] != word83:
        return None

    words_found = find_non_overlapping_words(plaintext, min_len=3)
    return {
        'word0': word0,
        'word83': word83,
        'key': test_key,
        'plaintext': plaintext,
        'words_found': words_found,
        'word_count': len(words_found),
    }

print("="*80)
print("K4 EXHAUSTIVE WORD SEARCH")
print("="*80)

results = []
for word0 in STARTING_WORDS:
    for word83 in WORDS_83:
        result = test_combination(word0, word83)
        if result:
            results.append(result)

results.sort(key=lambda x: -x['word_count'])

print(f"Found {len(results)} valid combinations\n")

# Check for 7+ word results
print("="*80)
print("LOOKING FOR 7+ WORD COMBINATIONS")
print("="*80)

seven_plus = [r for r in results if r['word_count'] >= 7]
if seven_plus:
    for r in seven_plus:
        print(f"\n=== {r['word0']} + {r['word83']} -> {r['word_count']} words ===")
        print(f"Words: {[w for w, p in r['words_found']]}")
        print(f"Plaintext: {r['plaintext']}")
        for word, pos in r['words_found']:
            print(f"  Position {pos}: {word}")
else:
    print("No 7+ word combinations found with current word lists.")

# Show best 6-word results
print("\n" + "="*80)
print("TOP 20 BEST 6-WORD RESULTS")
print("="*80)

for i, r in enumerate(results[:20]):
    if r['word_count'] >= 6:
        print(f"\n{i+1}. {r['word0']} + {r['word83']} -> {r['word_count']} words")
        non_crib_words = [w for w, p in r['words_found'] if w not in ['NORTHEAST', 'BERLINCLOCK', r['word0'], r['word83']]]
        print(f"   Extra words: {non_crib_words}")
        print(f"   All: {[w for w, p in r['words_found']]}")
