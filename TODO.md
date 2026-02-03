# To Do

1. Bank functionality
    - Withdraw specific item
2. Combat handler class
    - properties
        - current target info
            - health left
            - etc...
        - curent player info
            - health
            - prayer points
            - special attack energy
    - methods
        - is_player_in_combat
        - is_npc_in_combat
        - engage_npc
            - use osrs.find_entity method
            - use osrs.click method
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
5. Magic handler
    - methods
        - cast_spell
        - can_cast_spell
        - is_spell_active
            - for spells that require a target clicked after the factv (alching, telegrab etc)
6. Handle login/logout authentication
