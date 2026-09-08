# Paducah Rigging / Phatrigging — Client Order Portal

Prototype client ordering portal. Single self-contained HTML file, no build step,
no dependencies. Open `index.html` in a browser and it runs.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire site — markup, styles, catalog data, and logic |
| `images/` | Product photos (optional — line drawings are used when absent) |

## What works

- Public catalog browsable without signing in, with no pricing shown
- Account request form with validation
- Client login (demo accounts, cosmetic — see Limitations)
- 498 items across 19 categories, with sub-tabs (domestic/import, hook type, hoist brand, chain grade)
- Item selection shows unique part #, vendor part #, ship weight, and marked-up cost
- Chain sold by the foot, straight cut only
- Web sling capacity chart (vertical / choker / basket) by width and ply
- Category descriptions and safety disclaimers
- Tiered pricing by trailing 12-month spend, tier-weighted rewards credit
- Weight-based freight estimate with destination zone multiplier
- Primary and secondary ship-to selection
- Cart, checkout with SOW terms acceptance, order history
- State persists per browser via `localStorage`

## Configuration

All at the top of the `<script>` block in `index.html`:

| Constant | Default | Effect |
|---|---|---|
| `ORDER_ENDPOINT` | `''` | Paste a Formspree / Web3Forms / Zapier URL to receive placed orders as JSON. Empty = nothing transmitted. |
| `ACCOUNT_ENDPOINT` | `''` | Same, for account requests. |
| `TIERS` | see file | Spend thresholds, product discount, freight discount, rewards rate per tier |
| `POINTS_PER_CREDIT` / `CREDIT_VALUE` | `2500` / `25` | Rewards redemption (1 point = $0.01) |
| `KEY` | `phatrigging_v2` | localStorage key. Bump it to force stale saved data to reset. |

### Product photos

Create an `images/` folder next to `index.html`. For any item the page tries,
in order:

1. `images/<unique part #>.jpg` — e.g. `images/PH-00123.jpg`
2. `images/<category>-<group>.jpg` — e.g. `images/shackles-domestic.jpg`
3. `images/<category>.jpg` — e.g. `images/shackles.jpg`

First one that exists wins. If none do, the built-in line drawing is used.
47 images (18 category + 29 group) covers all items.

## Running locally

No build step. Either open `index.html` directly in a browser, or serve it
(needed for the photo-lookup `fetch`/`onerror` chain to behave like it will
in production):

```
npm run serve      # python3 -m http.server 8000
```

Then visit `http://localhost:8000/index.html`.

## Testing

```
npm install
npx playwright install chromium   # once per machine
npm test
```

`npm test` starts its own throwaway local server, drives the page with
Playwright/Chromium, and shuts the server down when done — nothing is left
running afterward. It covers everything `CLAUDE.md`'s Testing section calls
for: every category and sub-group renders without `undefined`/`NaN`, the
logged-out catalog never shows a `$` price, stale-SKU cart/order data is
pruned correctly, an empty category/group renders a graceful empty state
instead of crashing, tier boundaries resolve to the right tier name, and a
full sign-in → browse → cart → checkout → order-history → account loop runs
clean for every seeded demo account. See `tests/e2e.spec.js`.

## Deploying with GitHub Pages

Settings → Pages → Build and deployment → Source: **Deploy from a branch**,
Branch: **main**, folder: **/ (root)**. Save. The site publishes at
`https://<user>.github.io/<repo>/` within a minute or two.

## Limitations — read before showing this to a customer

- **The login is cosmetic.** Credentials are checked in client-side JavaScript
  against accounts defined in the file. Anyone can read them by viewing source.
  This is not authentication.
- **No payment processing.** The card fields do nothing. Real card handling needs
  a processor (Stripe, Authorize.net) so card data never touches this site.
- **No server.** Orders are written to the visitor's own browser. Without an
  endpoint configured, nobody is notified of anything.
- **If this repo is public, so is every price in it.** The catalog data, including
  marked-up costs, is embedded in `index.html` in plain text.
- **Product data needs verification.** Item weights are placeholder estimates by
  category and drive the freight calculation. Load limits, capacity ratings, and
  the safety disclaimer copy are draft and must be confirmed against manufacturer
  literature before this is customer-facing. Seven categories are a partial
  exception, sourced by exact vendor part number with the citation shown in the
  product panel:
  - The 32 "Domestic" shackles carry a rated-capacity figure pulled from
    Crosby/CM's own published catalog PDFs.
  - 36 of 74 Hooks items (18 Eye hooks, 8 Swivel hooks, 10 Shur-Loc hooks)
    carry a rated-capacity figure pulled from official Crosby/CMCO, Green Pin,
    and Campbell/Apex catalog literature.
  - All 65 Hoists items (15 CM, 20 Harrington, 28 Tiger Lifting, 2 Black Bear)
    carry a rated-capacity figure pulled from official manufacturer manuals,
    catalog PDFs, and spec pages (CM Series 653-A and 622A manuals; Harrington's
    Manual Hoists brochure and L5LB Owner's Manual; Tiger Lifting's Industrial
    Range technical sheet; Black Bear's YL/YSF Series spec pages).
  - All 20 Master links carry a rated-capacity figure pulled from Crosby's
    A-342/A-345 official catalog PDFs and CARTEC's published CDFXA WLL tables.
  - All 12 Snatch blocks carry a rated-capacity figure (shown in metric tons
    with the lb equivalent) pulled from official Crosby/McKissick catalog pages.
  - All 5 Tie-downs carry a rated-capacity figure pulled from Durabilt's
    published catalog and product pages; 2 of the 5 (`RS-4-30-6-FH7`,
    `RS430LWH7`) couldn't be matched verbatim to a Durabilt catalog number
    despite extensive searching, so they're matched to the closest published
    SKU and flagged in the UI citation as an inferred match, not a confirmed one.
  - 6 of 7 Binders carry a rated-capacity figure pulled from Columbus
    McKinnon's and Durabilt's official product pages; the 7th (a "1/4\"
    LEVER BINDER" with no vendor part number) is left blank.

  Every one of these is still an unreviewed draft figure, not a substitute for
  the marking stamped on the physical part. No other category has real
  capacity data yet, and within Shackles/Hooks/Binders some items were
  deliberately left blank rather than guessed — the 29 "Import" shackles (no
  vendor part number to trace back to literature), all 30 Hooks "Latch kits"
  (a latch kit's rating comes from the hook it's installed on, not its own
  literature), 3 Hooks items where either no part number exists or no source
  publishes a WLL figure despite a real part number, and 1 Binders item with
  no vendor part number at all. Hoists, Master links, Snatch blocks, and
  Tie-downs had no such part-number gap — every item in those four
  categories has a real vendor part number, so all of them are sourced.
  Wire rope clips and Wedge sockets were investigated and deliberately
  excluded from this pattern: manufacturer literature (Crosby's Wire Rope
  End Termination manual and Clips Warnings PDF) defines their capacity as
  an efficiency percentage of the wire rope's own breaking strength, not a
  fixed WLL per fitting part number, so a single-value rating would
  misrepresent how they actually work.
- **No product photos.** `photoHTML()` falls back to built-in SVG line art for
  every item. Real photos need to come from the Crosby/CM/Harrington/Peerless
  dealer media libraries or from shooting the actual stock — generic/stock/
  AI-generated images aren't used here because they'd show the wrong part next
  to a real SKU and price. See `images/README.md` and
  `phatrigging-photo-shotlist.csv` for the filenames needed.
