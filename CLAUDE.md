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

1. **Most item weights are still placeholders.** `wt` is a flat per-category
   estimate for items flagged `wtEst` and shown as "(est)". Freight is
   calculated from weight, so the shipping calculator is decorative for any
   item still on the placeholder. A real-weight sourcing pass has started,
   following the same source-and-cite methodology as the `cap`/`wll` work
   below: sourced items get a real per-item `wt`, lose the `wtEst` flag, and
   gain a `wtSrc` citation string (rendered in the UI, shown as "(sourced)").
   User has named 12 categories to prioritize for launch (Shackles, Hooks,
   Hoists, Chain, Wire rope clips, Nylon slings, Poly round slings, Master
   links, Wedge sockets, Rope, Tools, Shop supplies) — several other
   categories will likely be cut before go-live.
   - **Shackles** — 32 of 61 items now carry a sourced `wt`/`wtSrc`: all 16
     "SPA" (Crosby G-209 screw-pin) and 13 "SAS" (Crosby G-2130 bolt-type)
     Domestic items from Crosby's official catalog weight tables, plus the
     3 CM Long Reach shackles. Two things worth flagging: (a) the G-2130
     7/8" catalog table says 3.95 lb, but two independent distributors
     selling that exact stock number (1019533) both say 3.87 lb — the
     distributor consensus was used; (b) the catalog's stored part number
     for the 5/8" Long Reach shackle (`M71519`, item `PH-00161`) returns no
     matches anywhere online — the real CM part is almost certainly
     `M7151P` (its weight, ~1.80 lb, is used), since that item's existing
     7,000 lb `cap` rating exactly matches M7151P's real-world WLL. Left at
     the placeholder: all 29 "Import" shackles, which have no vendor part
     number at all.
2. **Load limits are mostly missing.** Nylon slings have real ratings
   (vertical/choker/basket, from a chart Ryan supplied). The sourced-`cap`
   pilot that started with Shackles has now been extended to Hooks and Hoists:
   - **Shackles** — all 32 "Domestic" shackles carry a `cap: {rating, src}`
     field, a single WLL figure pulled from Crosby's official G-209/G-2130
     catalog PDF and CM's Long Reach brochure, matched by exact vendor part
     number. The 29 "Import" shackles have NO vendor part number at all, so
     they were deliberately left blank.
   - **Hooks** — 36 of 74 items now carry sourced `cap` data: 18 Eye hooks
     (Crosby L-320/A-350 series, one Green Pin P-6731 sorting hook, one
     Campbell/Apex #31, and the Crosby S-377 barrel hooks), 8 Swivel hooks
     (Crosby L-322 series), and 10 of 11 Shur-Loc hooks (Crosby
     S-1316/S-1317/S-1326 series), each matched by exact vendor part number
     and cited inline in the UI. Deliberately left blank: all 30 "Latch
     kits" (a latch kit's rating is tied to the hook it's installed on, not
     independent — see `NOTES['Hooks|Latch kits']`), 1 Shur-Loc item
     (`PH-00492`, part `1004314`, "1/4" swivel Shur-Loc" — no source
     anywhere confirms this as a genuine Crosby stock number), and 3 "Misc
     hooks" items (2 with no vendor part number at all, plus `PH-00369`
     "roll off box hook", which has a real, traceable part number
     `5121573` but no retailer or manufacturer source publishes an actual
     WLL figure for it).
   - **Hoists** — all 65 items carry sourced `cap` data (every Hoists SKU
     has a real vendor part number, unlike some Hooks items, so there were
     no blanks to leave). 15 CM items: 12 confirmed against the official CM
     Series 653-A Lever Hoist manual PDF (cmhoist.com) plus the official
     CM Series 622A Hand Chain Hoist manual PDF (tamu.edu mirror of the
     CMCO document), the remaining 3 (0214/0216 mini lever hoists)
     corroborated via cmco.com/cmhoist.com product pages and independent
     distributor listings quoting the same CM catalog figures. 20 Harrington
     items: CF hand chain hoists and LX mini lever hoists confirmed against
     the official "Harrington Manual Hoists" brochure PDF (harringtonhoists.com,
     mirrored at tool-smith.com); L5LB lever hoists confirmed against
     Harrington's L5LB Owner's Manual and LB Lever Hoist spec page
     (harringtonhoists.com), cross-checked against independent dealer
     listings (Western Equipment, PicClick/eBay) for the part-number-to-
     capacity mapping. 28 Tiger items: confirmed against Tiger Lifting's own
     "Technical Sheet — Industrial Range" PDF (tigerlifting.com) for the
     TRL/TRC capacity-by-tonnage tables, with TR7LH/TR7CB/PROCB part-number
     naming cross-checked against Tiger's authorized USA dealer (liftgear.com)
     per-SKU model-lineup tables. 2 Black Bear items: confirmed against
     Black Bear Hoist's own YL Series and YSF Series spec pages
     (blackbearhoists.com). Added/updated 4 `NOTES['Hoists|<group>']`
     entries (CM, Harrington, Tiger, Black Bear) with the same
     citation-and-disclaimer pattern used for Shackles/Hooks.
   - **Master links** — all 20 items carry sourced `cap` data (100% part
     -number coverage, same as Hoists — no blanks needed). 14 Crosby alloy
     items: 9 A-342 master links confirmed against the Crosby Group's
     official catalog page 134 PDF (thecrosbygroup.com), 5 A-345 master
     link assemblies confirmed against the Crosby Group's official catalog
     page 135 PDF, both matched by exact Crosby stock number. 6 CARTEC
     clevis master link sets (2-leg and 4-leg, in 5/16"/3/8"/1/2" chain
     sizes): confirmed against the CDFXA WLL table published by All
     Material Handling, the CDFXA importer/distributor
     (allmaterialhandling.com), cross-checked against Holloway Houston
     Interests' per-part listings (hhilifting.com), matched by exact part
     number.
   - **Snatch blocks** — all 12 items carry sourced `cap` data (100% part
     -number coverage, no blanks needed). Crosby/McKissick 417/418/419/420
     series, confirmed against three official kitocrosby.com catalog page
     variants (hook-fitting single sheave 2-12t; shackle-fitting single
     sheave 2-12t; hook-fitting single sheave 15-30t, for the one 15-ton
     item), matched by exact stock number, cross-checked against
     independent retailer WLL listings (lifting.com, riggingwarehouse.com,
     hhilifting.com, hanessupply.com). Ratings shown in the catalog's
     native metric tons with the lb equivalent alongside, e.g. "2 t
     (4,400 lb)".
   - **Tie-downs** — all 5 items carry sourced `cap` data. 3 of 5 matched
     Durabilt's published 2019 catalog (jordanwirerope.com mirror) and
     current product pages (durabiltusa.com) by exact or near-exact
     catalog number. The other 2 (`RS-4-30-6-FH7`, `RS430LWH7`) do NOT
     appear verbatim in any source found — extensive searching turned up
     no Durabilt SKU with a matching handle-size segment. These were
     matched to the closest published Durabilt SKU (`RS-4-30-L-FH7` /
     `RS-4-30-L-WH7`, the only 4"x30' flat-hook and wire-hook straps
     Durabilt publishes) on width/length/hook-type, and the `src` string
     says explicitly that this is an inferred match, not a verbatim
     confirmation — treat these two ratings with more caution than the
     rest.
   - **Poly round slings** — 16 of 37 items carry sourced vertical/choker/
     basket `wll` data (plus a `wllSrc` citation, same pattern as the
     existing Nylon slings `wll` field). The catalog's own part numbers use
     two industry-standard color-code families: "SWG###" codes, confirmed
     against Industrial Wire Rope & Supply's published chart
     (industrialrope.com) and independently cross-checked against Southwest
     Wire Rope's chart (southwestwirerope.com) and LGH Rigging Rental's
     EN/A-code table (rentlgh.com) — all agree, including the fact that
     SWG180 = Orange (this matters: a different manufacturer's *own*
     internal EN-code chart assigns White to that number, but that chart
     doesn't match this catalog's color names, so it was not used); and
     "A###" codes, confirmed against Arabi Sling's official catalog
     (arabisling.com), also cross-checked against the LGH table. One item,
     `A24X20` ("20' BLUE POLY ROUND SLING"), has a part number that doesn't
     match any published code (24 isn't in either chart) — every other
     Blue item in this catalog uses code 240, and 240 is the only code that
     maps to Blue, so this was treated as a data-entry typo (missing
     trailing zero) and given the A240/Blue rating, with the `wllSrc` text
     explicitly flagging this as a typo call rather than a verbatim part
     match — treat this one rating with more caution than the rest, and
     flag it to Ryan for correction against the physical tag. The remaining
     21 of 37 items have no vendor part number at all (color/length only)
     and were left blank per the standard rule.
   - **Wire rope clips and Wedge sockets were investigated and
     deliberately excluded from this pattern** — they don't have a
     standalone WLL the way the categories above do. Crosby's own Wire
     Rope End Termination User's Manual states a wedge socket's rated
     load is a function of the wire rope's own breaking strength times an
     80% connection-efficiency factor, not a fixed number per socket part
     number; Crosby's Clips Warnings literature gives wire rope clips the
     same treatment (80%/90% efficiency depending on clip size, applied
     to whatever rope is used, plus a "number of clips"/torque table by
     rope size — not a WLL by clip part number). Putting a single `cap`
     value on these part numbers would misrepresent how their capacity
     actually works, since it depends on a rope spec this catalog doesn't
     capture. Do not add `cap` to these two categories without first
     changing the data model to also record the paired rope size.
   - **Binders** — 6 of 7 items carry sourced `cap` data. 3 CM items
     (48305 lever binder, 48810 and 48366 ratchet binders) confirmed
     against Columbus McKinnon's official product pages (cmco.com), which
     give a WLL range per binder type rather than a per-part table — the
     exact figure per part number was cross-checked against multiple
     independent distributor listings (tsriggingequipment.com,
     dkhardware.com, homelectrical.com, mscdirect.com, truckpro.com,
     fleetpride.com) that all agree. 3 Durabilt DTT items (DTT-1, DTT-2,
     DTT-3) confirmed against Durabilt's own per-part spec pages
     (durabiltusa.com), which do give an exact Work Load Limit per
     product number. The 7th item, a "1/4\" LEVER BINDER" with no vendor
     part number at all, was deliberately left blank — same rule as
     unnumbered items in every other category.
   - Everything else (chain, turnbuckles...) still shows no capacity.
   **This is still draft/unreviewed** — see Safety-critical content below
   before treating any of it as final. Ryan said he'd work on the rest.
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
  Ryan or a safety professional, and the UI says so.
- The same methodology was applied to Hooks: 36 of 74 items now carry sourced
  `cap` data from official Crosby/CMCO catalog pages (kitocrosby.com), a
  Crosby PDF catalog (iandisling.com), a Crosby spec-sheet PDF mirrored at
  boiserigging.com, Green Pin's own product page (greenpin.com), and a
  Campbell/Apex distributor listing that echoes the manufacturer's catalog
  description (aronson-campbell.com). Two items with real, traceable part
  numbers were deliberately left blank rather than guessed: `PH-00492`
  (part `1004314`) because no source anywhere confirms it as a genuine
  Crosby stock number, and `PH-00369` (part `5121573`, roll-off box hook)
  because the part number is confirmed real but no source publishes a WLL
  figure for it. All 30 Latch kits were intentionally excluded on
  architectural grounds, not a sourcing gap — a latch kit's rating is
  inherited from the hook it's installed on. Do not extend this pattern to
  other categories, or to the 29 unnumbered Import shackles, the 3
  no-part-number Misc hooks items, or the Latch kits, without either a real
  vendor part number to trace back to literature or (for Latch kits) a
  reason to revisit the inherited-rating architecture.
- The same methodology was applied to Hoists: all 65 items now carry sourced
  `cap` data. Primary sources used, by brand: CM — the official CM Series
  653-A Lever Hoist manual PDF (cmhoist.com) and CM Series 622A Hand Chain
  Hoist manual PDF (a CMCO document, mirrored at instrumentation.tamu.edu),
  both parsed with `pdftotext -layout` to extract the SKU-to-capacity spec
  tables directly, plus cmco.com/cmhoist.com product pages for the 2 mini
  lever hoist SKUs (0214/0216) not covered by either manual. Harrington —
  the official "Harrington Manual Hoists" brochure PDF (harringtonhoists.com,
  mirrored at tool-smith.com) for CF/LX series, and Harrington's own L5LB
  Owner's Manual plus LB Lever Hoist spec page (harringtonhoists.com) for
  the L5LB series, cross-checked against independent dealer listings
  (Western Equipment, PicClick/eBay) confirming part-number-to-capacity.
  Tiger Lifting — Tiger's own "Technical Sheet — Industrial Range" PDF
  (tigerlifting.com), which gives capacity-by-tonnage for the TRL/TRC
  families directly, cross-checked against Tiger's authorized USA dealer
  (liftgear.com) for exact TR7LH/TR7CB/PROCB part-number-to-capacity model
  lineups. Black Bear — the manufacturer's own YL Series and YSF Series
  spec pages (blackbearhoists.com). Unlike Hooks, every one of the 65
  Hoists items has a real, traceable vendor part number, so there was no
  "leave it blank" decision to make for this category — all 65 are sourced.
  Do not extend this pattern to any other category without an equivalent
  primary-source manufacturer document (a manual, catalog PDF, or the
  manufacturer's own product/spec page) matched by exact vendor part
  number.
- The same methodology was applied to Master links: all 20 items now carry
  sourced `cap` data. 9 Crosby A-342 alloy master links and 5 Crosby A-345
  master link assemblies were confirmed against the Crosby Group's own
  official catalog PDFs, pages 134 and 135 respectively
  (thecrosbygroup.com), fetched with `curl` and parsed with
  `pdftotext -layout` after the crawler tool failed on the PDF URL directly.
  6 CARTEC clevis master link sets were confirmed against the CDFXA WLL
  table published by All Material Handling, the CDFXA importer/distributor
  (allmaterialhandling.com), cross-checked against Holloway Houston
  Interests' per-part listings (hhilifting.com). All matched by exact stock
  number; no blanks.
- The same methodology was applied to Snatch blocks: all 12 items now carry
  sourced `cap` data, pulled from three official Crosby/McKissick catalog
  page variants on kitocrosby.com (hook-fitting and shackle-fitting single
  sheave 2-12t, plus hook-fitting single sheave 15-30t for the one 15-ton
  item), matched by exact stock number and cross-checked against
  independent retailer WLL listings. No blanks.
- The same methodology was applied to Tie-downs, with a caveat: 3 of 5
  items matched Durabilt's published 2019 catalog and current product
  pages by exact or near-exact catalog number. The remaining 2
  (`RS-4-30-6-FH7`, `RS430LWH7`) could not be found verbatim anywhere after
  extensive searching (Durabilt's own site, the 2019 catalog PDF, and
  several independent retailers) — they were matched to the closest
  published Durabilt SKU on width/length/hook-type, and the UI citation
  says explicitly that this is an inferred match, not a verbatim
  confirmation. Treat those two ratings as lower-confidence than every
  other sourced `cap` value on the site, and revisit if Ryan can confirm
  the exact catalog number against the physical strap's label.
- **Wire rope clips and Wedge sockets were researched and deliberately
  excluded** from the `cap` pattern — not a sourcing gap, an architectural
  mismatch. Both Crosby's Wire Rope End Termination User's Manual and its
  Clips Warnings literature define these fittings' "rated load" as an
  efficiency percentage (80% for wedge sockets; 80–90% for wire rope clips
  depending on size) applied to the *wire rope's own* breaking strength —
  there is no fixed WLL number per fitting part number independent of what
  rope it's paired with. A single `cap:{rating,src}` value would
  misrepresent this. If this gets revisited, it needs a rope-size input,
  not just a part-number lookup.
- The same methodology was applied to Binders: 6 of 7 items now carry
  sourced `cap` data. 3 CM items (48305, 48810, 48366) confirmed against
  Columbus McKinnon's official product pages (cmco.com), which publish a
  WLL range per binder family rather than a per-part table — the exact
  figure for each part number was cross-checked against six independent
  distributor listings that all agree on the same number. 3 Durabilt DTT
  items (DTT-1/2/3) confirmed against Durabilt's own per-part spec pages
  (durabiltusa.com), which do give an exact Work Load Limit per product
  number, cross-checked against independent retailer listings. The 7th
  item, "1/4\" LEVER BINDER", has no vendor part number and was left
  blank, consistent with every other category's rule for unnumbered
  items.
- Poly round slings got the same treatment via `wll`/`wllSrc` (the same
  shape already used for Nylon slings) rather than `cap`, since round
  slings rate by vertical/choker/basket like webbing slings do: 16 of 37
  items matched a published SWG- or A-code color/capacity chart
  (industrialrope.com, southwestwirerope.com, arabisling.com, rentlgh.com
  — all cross-checked and in agreement, including SWG180 = Orange, which
  matches this catalog's own color name even though it's not what every
  manufacturer's internal chart says). One item (`A24X20`) had a
  non-matching code treated as a probable typo for `A240` and flagged as
  such in its `wllSrc` citation — see "Known data gaps" #2 above. The
  other 21 of 37 items have no part number and were left blank.

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
  see "Known data gaps" #2 above.
- Extended the same sourced-`cap` methodology to Hooks: 36 of 74 items now
  cite official Crosby/CMCO, Green Pin, and Campbell/Apex catalog literature
  (see "Known data gaps" #2 and "Safety-critical content" above for exactly
  which items and why 3 items with real part numbers were left blank).
  Added/updated 5 `NOTES['Hooks|<group>']` entries with the same
  citation-and-disclaimer pattern used for Shackles.
- Extended the same sourced-`cap` methodology to Hoists: all 65 items now
  cite official CM/Harrington/Tiger Lifting/Black Bear manuals, catalog PDFs,
  and manufacturer spec pages (see "Known data gaps" #2 and "Safety-critical
  content" above for exactly which document was used per brand). Unlike
  Hooks, every Hoists SKU has a real vendor part number, so all 65 were
  sourced — none were left blank. Added/updated 4
  `NOTES['Hoists|<group>']` entries (CM, Harrington, Tiger, Black Bear) with
  the same citation-and-disclaimer pattern used for Shackles/Hooks.
  Deliberately did NOT add photos or fabricate ratings for anything else in
  that pass; photos remain out of scope per the sourcing rule above.
- Extended the same sourced-`cap` methodology to Master links (all 20
  items, Crosby A-342/A-345 catalog PDFs + CARTEC CDFXA WLL tables),
  Snatch blocks (all 12 items, Crosby/McKissick catalog pages), and
  Tie-downs (all 5 items, Durabilt catalog/product pages -- 2 of the 5 via
  an explicitly-flagged inferred part-number match rather than a verbatim
  one). See "Known data gaps" #2 and "Safety-critical content" above for
  full citations. Upgraded `NOTES['Master links']` and
  `NOTES['Snatch blocks']` from info to warn level, and added the same
  sourced-capacity disclaimer text to `NOTES['Tie-downs']`. Also
  researched Wire rope clips and Wedge sockets and deliberately did NOT
  add `cap` data to either -- both express capacity as an efficiency
  percentage of the wire rope's own breaking strength rather than a fixed
  WLL per part number, so the single-value `cap` pattern doesn't fit them
  without also capturing a rope spec.
- Extended the same sourced-`cap` methodology to Binders: 6 of 7 items now
  cite official Columbus McKinnon (cmco.com) and Durabilt (durabiltusa.com)
  product literature, cross-checked against independent distributor
  listings (see "Known data gaps" #2 and "Safety-critical content" above).
  Upgraded `NOTES['Binders']` with the same sourced-capacity disclaimer
  language. The 1 unnumbered item ("1/4\" LEVER BINDER") was left blank.
- Extended the pattern to Poly round slings using `wll`/`wllSrc` (the
  vertical/choker/basket shape, matching Nylon slings) instead of `cap`:
  16 of 37 items now cite published SWG/A-code round-sling charts
  (industrialrope.com, southwestwirerope.com, arabisling.com, rentlgh.com).
  One item (`A24X20`) is flagged in its own citation as a likely
  data-entry typo. Upgraded `NOTES['Poly round slings']` from info to warn
  level with the same sourced-capacity disclaimer pattern. The remaining
  21 unnumbered items were left blank. Also added generic rendering
  support for the new `wllSrc` citation field (mirrors the existing `cap`
  citation paragraph). Everything outside Shackles/Hooks/Hoists/Master
  links/Snatch blocks/Tie-downs/Binders/Poly round slings (chain,
  turnbuckles, wire rope clips, wedge sockets...) still shows no capacity.
