# API roadmap

This is the planned API. This is not a documentation of what is done, just an idea of what should be done.

(`$URL/api/` implied)
Restriction key:
- **A**: Administrators only.
- **J**: Judges and administrators only.
- _?_: Other restrictions may apply

Method | Path | Description | Restrictions
---|---|---|---
`GET` | `/team` | Get team list.
`POST` | `/team` | Create a team. | **A**
`GET` | `/team/%teamId` | Show team name, category, matches and their current score
`PUT` | `/team/%teamId` | Edit a team name or category | **A**
`DELETE` | `/team/%teamId` | Delete a team. | **A** _?_
`GET` | `/category` | Get category list.
`POST` | `/category` | Create a category. | **A**
`GET` | `/category/%catId` | Get category full name and color.
`PUT` | `/category/%catId` | Edit category full name or color. | **A**
`DELETE` | `/category/%catId` | Delete category. | **A** _?_
`GET` | `/category/%catId/teams` | List all teams in a category.
`GET` | `/match` | Get match list in current schedule.
`GET` | `/match/%matchId` | Get match status, teams and, if available, scores.
`PUT` | `/match/%matchId` | Edit match status or scores. | **J**
`GET` | `/scoreboard` | Get current general scoreboard.
`GET` | `/scoreboard/?cat=%catId` | Get current scoreboard for category.
`POST` | `/scoreboard/freeze` | Freeze or unfreeze scoreboard.
`GET` | `/scoreboard/finalists` | Get finalists. | _?_
`POST` | `/scoreboard/finalists` | Choose finalists. | **A**
`DELETE` | `/scoreboard/finalists` | Drop chosen finalists. | **A**
`PUT` | `/scoreboard/finalists` | (Un)Publish finalists. | **A**
`GET` | `/schedule` | List schedule.
`POST` | `/schedule/editor` | Create a new (auto-)schedule. | **A**
`GET` | `/schedule/editor/%schedId` | View draft schedule. | **A**
`PUT` | `/schedule/editor/%schedId` | Manually edit draft schedule | **A**
`DELETE` | `/schedule/editor/%schedId` | Drop a draft schedule | **A**
`POST` | `/schedule/editor/%schedId` | Apply a draft schedule | **A** _?_
