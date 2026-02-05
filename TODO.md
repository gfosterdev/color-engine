# To Do

1. ~~Combat handler class~~ ✅ **COMPLETED**
    - ~~properties~~
        - ~~current target info~~
            - ~~health left~~
            - ~~etc...~~
        - ~~curent player info~~
            - ~~health~~
            - ~~prayer points~~
            - ~~special attack energy~~
    - ~~methods~~
        - ~~is_player_in_combat~~
        - ~~is_npc_in_combat~~
        - ~~engage_npc~~
            - ~~use osrs.find_entity method~~
            - ~~use osrs.click method~~
    - **See COMBAT_HANDLER_PHASE2.md for Phase 2 features**
2. ~~Navigation testing tool~~ ✅ **COMPLETED**
    - ~~Interactive test file for bot navigation~~
    - ~~Test coordinate reading, pathfinding, and full navigation cycles~~
    - ~~Profile-specific testing for each bot~~
    - ~~See test_navigation.py and NAVIGATION_TESTING.md~~
3. Equipment handler
    - properties
        - each equipment slot data
    - methods
        - get_equipped_weapon
        - get_equipment
4. Navigation extended
    - Have multiple target world tiles on the path
    - Can interact with path blockers:
        - gates
        - shortcuts
