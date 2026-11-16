---
type: regex
match: contains
target: { source: file, path: plug/prd-packs/leaflet/pack.yaml }
pattern: '\$\{PACK\}/check_pages\.py'
---

The manifest runs the copied validator through `${PACK}`, as step 6 says.
