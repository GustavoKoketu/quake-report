Some assumptions were made:
  - When a player ended up killing itself (e.g. line 43 in log), it was considered as if "world" killed him, so the player loses a kill point.
  - Fields on the "kill_by_means" that weren't used won't show up in the death report.
    - This means that if no player was killed bt MOD_RAILGUN, it won't show up instead of appearing as "MOD_RAILGUN": 0.
  - The line 97 in the qgames.log has an unusual format and seems to omit a ShutdownGame: event, but it was accounted for in the code as a specific case.
  - Report logs were created right after each game concluded, instead of creating a "matches" array to store info of every indivudal match.
