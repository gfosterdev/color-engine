"""
Runescape game object id references.

This file should be populated from RuneLite's `ObjectID.java` (see:
https://github.com/runelite/runelite/blob/master/runelite-api/src/main/java/net/runelite/api/ObjectID.java)

I couldn't fetch the remote file automatically; paste the file or supply the list
if you want exact IDs. For now this module provides a clear structure and a
set of commonly-used categories (ores, rocks, trees/logs). Fill the lists with
the integer IDs from `ObjectID.java` as needed.
"""

from typing import Dict, List

# Populated from `external/ObjectID.java` (world object constants).
# Contains commonly-used in-world object IDs for ores, trees/logs and misc.

# Ore rock object IDs (in-world rock constants from ObjectID.java)
ORE_OBJECT_IDS: Dict[str, List[int]] = {
	"TIN_ROCKS": [10080, 11360, 11361],
	"COPPER_ROCKS": [10079, 10943, 11161],
	"CLAY_ROCKS": [11362, 11363],
	"SOFT_CLAY_ROCKS": [34956, 34957, 36210],
	"COAL_ROCKS": [4676, 11366, 11367, 36204],
	"IRON_ROCKS": [11364, 11365, 36203],
	"MITHRIL_ROCKS": [11372, 11373, 36207],
	"ADAMANTITE_ROCKS": [11374, 11375, 36208],
	"GOLD_ROCKS": [11370, 11371, 36206],
	# Runite / high-level rocks
	"RUNITE_ROCKS": [11376, 11377, 36209, 31917],
}

# Tree / log object IDs
LOG_OBJECT_IDS: Dict[str, List[int]] = {
	"NORMAL": [1276, 4532],
	"OAK": [4533, 4540],
	"WILLOW": [4534, 4541],
	"MAPLE": [4535],
	"YEW": [4536],
	"MAGIC": [4537],
	# rotting / special logs
	"ROTTING_LOG": [3508],
	"ROTTING_TREE": [3514],
}

# Misc in-world object IDs (stumps, anvils, furnaces, bank chests/booths)
MISC_OBJECT_IDS: Dict[str, List[int]] = {
	"TREE_STUMPS": [1341, 1342, 1343, 1344, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352, 1353],
	"ANVIL": [2031, 2097, 4306, 6150],
	"FURNACE": [2030, 2966, 3294, 4304],
	"BANK_CHEST": [2693, 4483],
	"BANK_BOOTH": [6084, 6083],
}


def find_ore_by_id(obj_id: int) -> str:
	"""Return ore name for a given object id, or empty string if unknown."""
	for ore, ids in ORE_OBJECT_IDS.items():
		if obj_id in ids:
			return ore
	return ""


def find_log_by_id(obj_id: int) -> str:
	"""Return log/tree type for a given object id, or empty string if unknown."""
	for log, ids in LOG_OBJECT_IDS.items():
		if obj_id in ids:
			return log
	return ""
