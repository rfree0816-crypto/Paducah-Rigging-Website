# CLAUDE.md — Phatrigging client order portal

Context for continuing this project. Written at handoff from a chat session
where the prototype was built. Read this before changing anything.

## What this is

A B2B client ordering portal for Phatrigging, a rigging supply company
(related to Paducah Rigging). One self-contained `index.html` — markup, CSS,
catalog data, and logic all in one file. No build step, no dependencies, no
framework. Open it in a browser and it runs.

That was a deliberate choice for prototyping speed. If this becomes a real
site it needs a backend (see Limitations), and at that point the single-file
structure should be revisited — but don't split it up just for tidiness while
it's still a prototype.

## The person you're working with

Ryan. Prefers fast working prototypes over planning discussion, gives terse
directional feedback, and fact-checks. He wants diagnosis and execution, not
clarifying questions — make a reasonable call, ship it, and say plainly what
you decided so he can overrule. He catches errors, so flag your own
assumptions before he finds them.

## Architecture

Everything lives in `index.html`:

- **Three top-level pages**, toggled by adding/removing `.hidden`:
  `#loginPage`, `#publicPage` (catalog without pricing), `#reqPage`
  (account request form), plus `#app` once signed in.
- **`ITEMS`** — flat array of every sellable item, generated from Ryan's
  spreadsheet. Each has `upn` (unique part #, `PH-00123`), `part` (vendor part
  #, may be empty), `name`, `cat`, `grp`, `price`, `wt`, `uom`.
  `sku` and `list` are aliases assigned at load; `CATALOG === ITEMS`.
- **`CATS_META`** — category list with display order, art key, sub-groups, count.
- **Rendering** is string-template functions (`catalogHTML`, `cartHTML`,
  `selectorHTML`, `ordersHTML`, `accountHTML`) called by `render()`, which
  re-renders the whole view and re-wires handlers in `wire()`. Not efficient,
  very easy to reason about. Keep the pattern.
- **State** persists in `localStorage` under `KEY` (`phatrigging_v2`).
  `sanitize()` runs on load and drops cart/order lines whose SKU is no longer
  in the catalog — necessary because catalog data gets regenerated often.
  Bump `KEY` if a data shape changes.

## Config constants (top of the script)

| Constant | Default | Effect |
|---|---|---|
| `ORDER_ENDPOINT` | `''` | POST placed orders as JSON (Formspree/Web3Forms/Zapier). Empty = nothing transmitted. |
| `ACCOUNT_ENDPOINT` | `''` | Same, for account requests. |
| `TIERS` | see file | Spend threshold, product discount, freight discount, rewards rate per tier |
| `POINTS_PER_CREDIT` / `CREDIT_VALUE` | 2500 / 25 | 1 point = $0.01 |
| `KEY` | `phatrigging_v2` | localStorage key |

## Data provenance and rules

Catalog came from `PHAT_Summary.xlsx` (585 rows, 38 tabs — Ryan has it; it is
NOT in this repo and should not be committed, it contains raw costs).
Rules applied when generating `ITEMS`:

- **Excluded barge ratchets entirely** — Ryan's instruction.
- **Excluded rows with no cost** (highlighted yellow in his sheet) — not stocked.
  94 rows dropped this way.
- **Used the marked-up cost column**, never the raw cost. Markup is not uniform
  in the source: 396 rows at 1.45x, 83 at 2.0x, 5 at 3.0x. Left as-is.
- Categories and sub-groups were assigned by source tab. Structure Ryan asked for:
  Shackles and Wire rope clips split Domestic/Import; Hooks split by hook type
  (Eye/Swivel/Shur-Loc/Misc/Latch kits); Hoists split by brand (CM/Harrington/
  Tiger/Black Bear); Chain split by grade.
- **Chain** came from a separate reel list. Reels were collapsed to one sellable
  item per size+grade, since customers buy "3/8 GR100", not a reel ID. Where
  reels of the same spec had different prices, Ryan chose: 1/2" GR70 = $4.74,
  3/8" GR120 = $15.41, 3/8" GR70 = $4.17.
- The 5/16" row marked grade "BLK" was merged into GR100 at $4.31 — its reel ID
  (`CHAIN1002501`) matches the Grade 100 prefix, so BLK was almost certainly a
  finish, not a grade.
- Chain is sold by the foot (`uom: 'ft'`), straight cut only. The ft path is
  generic: any item with `uom: 'ft'` gets a feet input instead of a qty box.

## Known data gaps — highest value work first

1. **No item weights.** `wt` is a placeholder estimate per category, flagged
   `wtEst` and shown as "(est)". Freight is calculated from weight, so the
   shipping calculator is decorative until real weights exist. This is the
   single most valuable thing to fix.
2. **Load limits are mostly missing.** Nylon slings have real ratings
   (vertical/choker/basket, from a chart Ryan supplied). As a scoped pilot, the
   32 "Domestic" shackles now carry a `cap: {rating, src}` field — a single WLL
   figure pulled from Crosby's official G-209/G-2130 catalog PDF and CM's Long
   Reach brochure, matched by the exact vendor part number already in `ITEMS`,
   with the source cited inline in the UI (see `selectorHTML()`). The 29
   "Import" shackles have NO vendor part number in the data at all, so they were
   deliberately left blank rather than guessed — there's no way to trace an
   unnumbered import part to real literature. Everything outside Shackles
   (hooks, hoists, chain, master links, snatch blocks, wedge sockets,
   turnbuckles, wire rope clips...) still shows no capacity. **This is still
   draft/unreviewed** — see Safety-critical content below before treating any
   of it as final. Ryan said he'd work on the rest.
3. **98 of 498 items have no vendor part number** — concentrated in import
   shackles (29), poly round slings (21), rope (20), clips (13). The Part #
   field is hidden entirely for those items, per Ryan's instruction.
4. **Descriptions are truncated/coded** from the source sheet — "1-1/2\" SAS",
   "1-1/2 TON ALLOY EYE HOOK W/LAT". Fine at the counter, not fine for
   customers. Needs expansion before public launch.
5. **Photos.** None yet. `photoHTML()` looks for `images/<upn>.jpg`, then
   `images/<category>-<group>.jpg`, then `images/<category>.jpg`, falling back
   to built-in SVG line art. 47 images (18 category + 29 group) covers
   everything; `phatrigging-photo-shotlist.csv` lists every filename.
   Legitimate sources are the Crosby / CM / Harrington / Peerless dealer media
   libraries, or shooting the actual stock. Not random web images.

## Safety-critical content — treat carefully

This site sells load-rated equipment. Wrong numbers here can hurt someone.

- Every category has a disclaimer in `NOTES`, keyed `"Category"` or
  `"Category|Group"`, with `level: 'warn'` (red) or `'info'`.
- The important ones: Grade 70 chain and binders/tie-downs are transport only,
  NOT overhead lifting. Chain cut off the reel is uncertified until assembled,
  proof tested, and tagged. Latch kits must match the hook model.
  Hoists are not for lifting people.
- **All disclaimer copy is draft, written by an AI, not reviewed by a lawyer or
  a safety professional.** Same for the SOW terms in `SOW_TERMS`. Ryan has been
  told this repeatedly. Keep telling him until it's reviewed.
- Two values in the sling chart he supplied didn't reconcile with their own
  rows (6" 2-ply vertical read 18800, 12" 2-ply choker read 26830). The
  conservative arithmetic-consistent values (16800, 26880) are in the file.
  Both need confirming against printed manufacturer literature.
- The 32 Domestic shackle `cap` ratings added as a pilot are sourced from
  Crosby's own 2019 catalog PDF (pages 77 & 79, thecrosbygroup.com) and CM's
  official Long Reach Shackle brochure, matched to this catalog's exact vendor
  part numbers (e.g. 1018419 → G-209 3/8" SPA → 1 ton) and cross-checked
  against a second independent retailer citation per size before entry. Full
  citation is shown in the UI next to the rating. This is a published-spec
  lookup, not an engineering judgment call — but it is still unreviewed by
  Ryan or a safety professional, and the UI says so. Do not extend this
  pattern to other categories or to the 29 unnumbered Import shackles without
  a real vendor part number to trace back to literature.

## Commercial decisions already made

- **Credit card only.** No ACH, no PO, no Net 30. 3% processing fee. This was
  explicit — don't reintroduce other payment methods.
- **Tiers:** Standard (any spend) / Bronze $150k / Silver $300k / Gold $500k.
  Product discount 0/2/4/6%. Freight discount 0/0/3/5%. The $300k and $500k
  thresholds were assumed by the assistant, not specified by Ryan — confirm.
- **Rewards ("rig credit"):** tier-weighted, 0.5/1/1.25/1.5% back. 1 point =
  $0.01, redeemed at 2,500 points = $25.
- **Tagline:** "The gear to get the job done", subline "In stock across five
  locations". Ryan said five; an earlier list of branches had six — unresolved.
- Catalog is public without login; pricing requires sign-in.
- Deck fittings, life vests, booster pumps, damming foam and paint are in the
  catalog. Whether Phatrigging sells the full marine supply line or only rigging
  is an open business question.

## Limitations — this is a prototype

- **The login is cosmetic.** Accounts are in client-side JS, readable in source.
  Not authentication.
- **No payment processing.** Card fields do nothing. Real cards need Stripe or
  Authorize.net so card data never touches this site (PCI scope).
- **No server.** Orders write to the visitor's browser. Nobody is notified
  unless `ORDER_ENDPOINT` is set.
- **If this repo is public, all pricing is public** — it's plain text in
  `index.html`, and permanent in commit history.

## Testing

Real test suite now exists: `tests/e2e.spec.js`, run with `npm test`
(installs Playwright + Chromium once, then `npx playwright install chromium`;
see README). It drives a live page with a real browser rather than stubbing
the DOM under Node, since the render functions touch real DOM nodes and
`localStorage`. Covers every case that previously caught real bugs:

- Renders every category and every sub-group (public and signed-in), asserts
  no `undefined` or `NaN` in the output.
- Asserts no `$` appears anywhere in the logged-out catalog HTML (pricing leak).
- Calls `sanitize()` on state referencing SKUs that no longer exist and checks
  the dead lines/orders are dropped (this crashed the app twice historically).
- Temporarily injects a category/group with zero items and asserts
  `selectorHTML()` renders a graceful empty state instead of throwing (crashed
  once historically).
- Checks tier boundary values ($0, $149,999, $150,000, $299,999, $300,000,
  $499,999, $500,000) resolve to the expected tier name.
- Runs the full sign-in → browse every category → add to cart → checkout →
  place order → order history → account loop for every seeded demo account.
- Account request form: empty submit is rejected, valid submit succeeds.

Re-run this after any change to `ITEMS`, `CATS_META`, `TIERS`, or the render
functions. 305 assertions currently pass clean.

## Next steps, in Ryan's stated order

1. Item detail — photos and load limits. Load limits partially started: see
   "Known data gaps" #2 for the 32 Domestic shackles now sourced from Crosby/CM
   catalog literature. Photos still untouched — needs real dealer photography
   or Ryan's own stock shots, per the sourcing rule above; generic/stock/AI
   images were intentionally not substituted because they'd misrepresent the
   specific vendor SKU next to its real part number and price.
2. Account request form — DONE, needs `ACCOUNT_ENDPOINT` wired to Formspree
3. Get it into the repo and onto GitHub Pages — DONE (repo exists, see README
   for the GitHub Pages steps; still needs someone to flip the Pages setting on)

Immediate technical priorities regardless of order: real item weights, then
wiring the two endpoints so the thing actually notifies someone.

## Fixed since handoff

- Signed-in top nav (Catalog/Cart/Orders/Account/Sign out) overlapped the
  brand lockup and got clipped below ~700px width. Now wraps to its own
  horizontally-scrollable row on narrow screens. CSS only, in the
  `.topbar-in`/`.nav` rules.
- Added a favicon (inline SVG, no new file) — was 404ing on every page load.
- Added `tests/e2e.spec.js` + `npm test` — see Testing section above.
- Added sourced `cap` (rated capacity) data to the 32 Domestic shackle items,
  pulled from Crosby/CM published catalog literature and cited in the UI —
  see "Known data gaps" #2 above. Deliberately did NOT add photos or fabricate
  ratings for anything else in this pass; both remain open per the sourcing
  and safety rules in this file.
