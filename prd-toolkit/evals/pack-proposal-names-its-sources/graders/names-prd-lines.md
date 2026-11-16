---
type: regex
match: contains
target: last_message
pattern: '\b(?:north|south)/(?:docs/prd/(?:north|south)/)?(?:prd|testing)\.md\b|\b(?:north|south)[\s`*]{1,3}(?:prd|testing)\.md\b'
---

An item names the PRD line it comes from by its file (`north/prd.md` section 7 row `pages`, `south/testing.md`
Levels row `integration`), as step 3 says.
