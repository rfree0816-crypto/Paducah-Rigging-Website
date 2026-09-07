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
  literature before this is customer-facing.
