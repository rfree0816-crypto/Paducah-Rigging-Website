import json
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

with open('/home/user/webapp/.tmp/weight_tier_data.json') as f:
    wdata = json.load(f)

doc = Document()

# ---------- base style ----------
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10.5)

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GOLD = RGBColor(0xB8, 0x86, 0x0B)
GREY = RGBColor(0x55, 0x55, 0x55)

def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def h1(text):
    p = doc.add_heading(level=1)
    r = p.add_run(text)
    r.font.color.rgb = NAVY
    r.font.size = Pt(18)
    return p

def h2(text):
    p = doc.add_heading(level=2)
    r = p.add_run(text)
    r.font.color.rgb = NAVY
    r.font.size = Pt(14)
    return p

def h3(text):
    p = doc.add_heading(level=3)
    r = p.add_run(text)
    r.font.color.rgb = GOLD
    r.font.size = Pt(12)
    return p

def body(text, bold=False, italic=False, size=10.5, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    return p

def bullet(text, bold_lead=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_lead:
        r = p.add_run(bold_lead)
        r.bold = True
        p.add_run(text)
    else:
        p.add_run(text)
    return p

def make_table(headers, rows, col_widths=None, header_bg='1F3A5F'):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = ''
        p = hdr[i].paragraphs[0]
        r = p.add_run(htext)
        r.bold = True
        r.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
        r.font.size = Pt(9.5)
        set_cell_bg(hdr[i], header_bg)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ''
            p = cells[i].paragraphs[0]
            r = p.add_run(str(val))
            r.font.size = Pt(9.5)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)
    return table

# ================= COVER =================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = title.add_run('Phatrigging')
r.bold = True
r.font.size = Pt(30)
r.font.color.rgb = NAVY

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run('Inventory System Selection & Weight-Tier Freight Analysis')
r.font.size = Pt(16)
r.font.color.rgb = GOLD

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub2.add_run('Prepared for internal decision-making — not a vendor-endorsed document')
r.italic = True
r.font.size = Pt(10)
r.font.color.rgb = GREY

doc.add_paragraph()
body('Purpose of this document:', bold=True)
body('This document has two parts. Part 1 compares inventory-management platforms considered for '
     'Phatrigging (QuickBooks, Fishbowl, inFlow Inventory, Cin7 Core, Zoho Inventory, and Shopify) and '
     'lands on a recommendation. Part 2 analyzes Phatrigging\u2019s existing 497-SKU catalog by shipping-weight '
     'tier, since weight directly drives the freight calculation already built into the order portal '
     '(UPS Ground for shipments \u2264150 lb, LTL freight above that).')
doc.add_page_break()

# ================= TOC-ish overview =================
h1('Contents')
bullet('Part 1 \u2014 Inventory Software Comparison')
bullet('    1.1 Baseline: QuickBooks')
bullet('    1.2 Fishbowl')
bullet('    1.3 inFlow Inventory')
bullet('    1.4 Cin7 Core (deep dive)')
bullet('    1.5 Zoho Inventory (deep dive)')
bullet('    1.6 Side-by-side comparison table')
bullet('    1.7 Why Shopify doesn\u2019t make sense here')
bullet('    1.8 Recommendation: inFlow vs. Zoho')
bullet('Part 2 \u2014 Weight-Tier Inventory Analysis')
bullet('    2.1 Why weight tiers matter')
bullet('    2.2 Proposed tier definitions')
bullet('    2.3 Current catalog breakdown by tier')
bullet('    2.4 Data quality caveat')
bullet('Part 3 \u2014 Recommended Next Steps')

doc.add_page_break()

# ================= PART 1 =================
h1('Part 1 \u2014 Inventory Software Comparison')
body('Phatrigging currently runs on a custom-built order portal (this project) that already handles '
     'B2B pricing tiers, weight-based freight, rewards, and order history. None of the tools below would '
     'replace that customer-facing portal \u2014 the question is which one should sit behind it as the system '
     'of record for stock levels, purchasing, and warehouse operations, feeding data into the portal via API.')

h2('1.1 Baseline: QuickBooks')
body('QuickBooks (Online or Desktop Enterprise) is accounting software with inventory bolted on, not '
     'dedicated inventory software. "Advanced Inventory" (Enterprise Platinum tier only) adds multi-location '
     'tracking, barcode scanning, and FIFO costing.')
p = doc.add_paragraph(style='List Bullet'); r=p.add_run('Strength: '); r.bold=True; p.add_run('it is already your books \u2014 no separate accounting sync needed.')
p = doc.add_paragraph(style='List Bullet'); r=p.add_run('Weakness: '); r.bold=True; p.add_run('no real B2B customer portal, no tiered/contract pricing logic, weak reorder-point automation, no lot/serial or certification tracking for rated hardware.')
body('Verdict: fine as the accounting system of record. Not viable on its own as inventory control for a multi-location rigging distributor.', italic=True)

h2('1.2 Fishbowl \u2014 QuickBooks-native inventory bolt-on')
body('Inventory + light manufacturing (BOMs, work orders) built specifically to sync tightly with QuickBooks.')
make_table(
    ['Attribute', 'Detail'],
    [
        ['Pricing', 'Cloud "Essentials" ~$229\u2013329/mo (2 users); on-prem perpetual licenses $4,300\u20136,500+ per user. Paid implementation required on every purchase.'],
        ['QuickBooks sync', 'Best-in-class \u2014 near real-time, purpose-built for this exact pairing.'],
        ['Multi-location', 'Good.'],
        ['B2B customer portal', 'Weak / limited \u2014 internal ops tool, not something customers log into.'],
        ['Lot/serial tracking', 'More granular than most tools at this price \u2014 closer to what rated-hardware traceability needs, though still manual-effort.'],
        ['Learning curve', 'Steep; dated UI.'],
    ], col_widths=[1.6, 5.0]
)
body('Best fit if: you are committed to keeping QuickBooks as your books long-term and want the tightest possible sync, and can tolerate a dated interface and implementation overhead.', italic=True)

h2('1.3 inFlow Inventory \u2014 cheapest real multi-location tool')
body('Lightweight, modern inventory/order-management SaaS. Cheapest tool here that still does multi-location correctly.')
make_table(
    ['Attribute', 'Detail'],
    [
        ['Pricing (2026)', 'Entrepreneur $129/mo, Small Business $349/mo, Mid-Size $699/mo, Enterprise custom (all billed annually; monthly rates run higher). Unlimited locations even on the entry Entrepreneur tier is notable, though that tier caps at 1 location with no sub-locations \u2014 multi-location really starts at Small Business.'],
        ['API access', 'Available as a paid add-on (~$49/mo) on Entrepreneur & Small Business tiers; included on Mid-Size and above. REST + JSON, with filtering, pagination, and an MCP server for AI-agent integration.'],
        ['B2B portal ("Showroom")', 'Included at Small Business tier and up; "Showroom Pro" (custom domain, abandoned-cart emails, remove inFlow branding) is a paid add-on at lower tiers, included at Mid-Size+.'],
        ['Lot/serial/expiry tracking', 'Add-on at lower tiers ($29\u201369/mo depending); included at Mid-Size+. Thinner than Fishbowl overall.'],
        ['QuickBooks/Xero sync', 'Included on all tiers (push invoices, purchases, inventory value).'],
        ['Onboarding', 'Optional on entry tier; required one-time $499 fee from Small Business tier up.'],
        ['Learning curve', 'Low \u2014 modern, clean UI; frequently cited as the easiest tool in this category to learn without formal training.'],
    ], col_widths=[1.8, 4.8]
)
body('Real users report the price jump between tiers is steep once you need add-ons (lot tracking, API, more integrations) \u2014 budget for the "Small Business" tier plus add-ons, not just the sticker $129/mo.', italic=True)
body('Best fit if: you want the lowest total cost of ownership for a genuinely modern multi-location tool, and are willing to add API access as a line item.', italic=True)

h2('1.4 Cin7 Core \u2014 deep dive')
body('The most commonly recommended mid-market platform specifically for B2B wholesalers/distributors. Positioned as '
     '"inventory management with light ERP/manufacturing," not a full ERP.')
h3('Pricing')
body('Standard $349/mo, Pro $599/mo, Advanced $1,199/mo. Tiers gate SKU count, user count, and automation depth. '
     'Multiple independent reviews flag Cin7\u2019s pricing as non-transparent \u2014 costs creep upward as SKU count and '
     'automation needs grow, beyond the advertised entry price.')
h3('Strengths')
bullet('Real, full-featured B2B ordering portals for wholesale customers \u2014 this is Cin7\u2019s headline differentiator versus every other tool on this list.')
bullet('Strong multi-channel sync, useful if you ever sell through channels beyond direct B2B.')
bullet('Automated reordering and a genuine workflow/automation engine.')
bullet('Handles both inventory operations and light manufacturing/assembly reasonably well.')
h3('Weaknesses (consistently reported across independent reviews)')
bullet('Steep learning curve.')
bullet('Support quality drops noticeably after onboarding \u2014 flagged repeatedly and specifically in reviews.')
bullet('No RFID support; no true enterprise-grade asset tracking.')
bullet('Pricing model is the top complaint \u2014 "hidden cost" surprises as SKU count/automation needs scale up.')
body('Critical point for Phatrigging specifically: Cin7\u2019s core selling point \u2014 its B2B ordering portal \u2014 is largely '
     'redundant here. Phatrigging already has a custom-built portal with tiered pricing, weight-based freight, and a '
     'rewards program that Cin7\u2019s generic portal cannot replicate. Paying Cin7\u2019s premium price partly buys a feature '
     'you would not use.', bold=True)
body('Best fit if: your top priority is a ready-made customer-facing B2B ordering experience \u2014 which is not the case '
     'here, since that already exists.', italic=True)

h2('1.5 Zoho Inventory \u2014 deep dive')
body('Budget-tier multi-warehouse inventory tool, part of the broader Zoho ecosystem (Zoho Books, CRM, etc.).')
h3('Pricing (2026, per Zoho\u2019s published pricing page)')
make_table(
    ['Plan', 'Price', 'Orders/mo', 'Users', 'Locations', 'Notable inclusions'],
    [
        ['Free', '$0', '50', '1', '1', 'Composite items, dropshipment, backordering'],
        ['Standard', '$29/mo (annual)', '500', '3', '2', 'Customer portal, dropshipment, backordering'],
        ['Premium', '$79/mo (annual)', '3,000', '5', '4', 'Barcode gen, batch/serial tracking, vendor portal, UoM conversion'],
        ['Plus', '$129/mo (annual)', '7,500', '10', '6', 'Everything in Premium'],
        ['Enterprise', '$249/mo (annual)', '15,000', '10', '10', 'Zoho Analytics, multi-currency per contact'],
    ], col_widths=[1.0, 1.3, 1.0, 0.7, 0.9, 2.5]
)
body('Add-ons (extra users, order-volume blocks, locations, advanced warehousing) are priced separately and stack on top of the base plan.', italic=True)
h3('API')
body('Full REST API (organization-scoped), 100 requests/minute per organization on every plan, with daily caps '
     'from 1,000/day (Free) up to 10,000/day (Premium & Enterprise). This is more than sufficient for a single-location '
     'or small-multi-location distributor syncing stock levels and orders into a custom front end.')
h3('Strengths')
bullet('Cheapest of the "real" multi-warehouse tools evaluated here by a wide margin.')
bullet('Barcode + RFID support \u2014 notably ahead of Cin7 on this specific point.')
bullet('Recent 2026 updates added batch/lot-level pricing, an incremental step toward the traceability rated hardware needs.')
bullet('If open to using Zoho Books instead of QuickBooks, the whole suite (CRM, accounting, inventory) integrates natively under one vendor.')
h3('Weaknesses (consistently reported)')
bullet('B2B functionality is described as "too thin" across multiple independent reviews \u2014 this is the single most repeated criticism, and it is the exact feature Cin7 is strong at.')
bullet('Weaker QuickBooks integration than Fishbowl\u2019s native-feeling sync (Zoho pushes you toward Zoho Books instead).')
bullet('Automation and reporting depth is behind Cin7\u2019s.')
body('For Phatrigging, the "B2B portal too thin" criticism matters far less than it would for a typical buyer, '
     'because the custom portal already fills that role. Zoho becomes purely a backend inventory/warehouse engine, '
     'which plays to its strengths (cheap, real multi-warehouse, decent API) and sidesteps its main weakness.', bold=True)

h2('1.6 Side-by-side comparison')
make_table(
    ['', 'QuickBooks Adv. Inv.', 'Fishbowl', 'inFlow', 'Cin7 Core', 'Zoho Inventory'],
    [
        ['Monthly cost (typical)', '~$200+/mo (whole QB suite)', '$229\u2013329/mo + implementation', '$129\u2013699/mo + add-ons', '$349\u20131,199/mo', '$29\u2013249/mo + add-ons'],
        ['Multi-location', 'Basic', 'Good', 'Good (from Small Business tier)', 'Strong', 'Good'],
        ['B2B customer portal', 'None', 'Weak', 'Basic\u2013good (Showroom)', 'Strong (redundant for Phatrigging)', 'Thin'],
        ['REST API', 'Limited', 'Yes', 'Yes (add-on on lower tiers)', 'Yes', 'Yes, generous rate limits'],
        ['QuickBooks/Xero sync', 'Native (it is QuickBooks)', 'Best-in-class', 'Included, all tiers', 'Syncs to QB/Xero', 'Weaker; favors Zoho Books'],
        ['Lot/serial/cert tracking', 'Minimal', 'Moderate \u2014 best of this group', 'Add-on, thinner', 'Minimal, no RFID', 'Has RFID; batch/lot improving'],
        ['Learning curve', 'Low if already on QB', 'High', 'Low', 'High', 'Low\u2013moderate'],
        ['Pricing transparency', 'Predictable', 'Predictable but implementation-heavy', 'Predictable, add-ons add up', 'Frequently flagged as a problem', 'Straightforward'],
    ], col_widths=[1.5, 1.2, 1.1, 1.1, 1.1, 1.1]
)

h2('1.7 Why Shopify doesn\u2019t make the most sense here')
body('Shopify opened its native B2B features (company accounts, custom price lists/catalogs, net terms) to all '
     'plans in 2026, so it is more viable for wholesale than it used to be. It was still ruled out for Phatrigging '
     'for three concrete reasons:')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Retail-shaped inventory model. '); r.bold=True
p.add_run('Shopify\u2019s inventory is SKU + quantity + location. It has no native lot/serial/certification tracking, no '
          'real warehouse operations (bin locations, pick/pack, transfer orders, cycle counts), and no purchasing/'
          'reorder automation without bolting on third-party apps (Stocky, Cin7, Extensiv). You would still need one '
          'of the tools compared above sitting behind Shopify \u2014 so Shopify adds a second license and a second sync '
          'point for no net gain.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('It would duplicate work already done. '); r.bold=True
p.add_run('Phatrigging has already built a custom order portal with tiered B2B pricing, weight-based freight, and a '
          'rewards program specific to how the business actually sells. Moving to Shopify\u2019s storefront/checkout would '
          'mean either abandoning that custom logic and rebuilding it inside Shopify\u2019s theme/app ecosystem (expensive, '
          'and Shopify\u2019s B2B logic is more rigid than fully custom code), or running two separate systems in parallel.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('No traceability for rated/safety-critical hardware. '); r.bold=True
p.add_run('None of Shopify\u2019s native or add-on inventory tools solve lot/cert traceability for load-rated rigging '
          'hardware \u2014 the one requirement that is most specific to this business. If that traceability is going to be '
          'built at all in the near term, it makes more sense to build it into the data model of the portal Phatrigging '
          'already owns than to pay for a Shopify+app stack that still would not solve it.')
body('In short: Shopify solves a problem Phatrigging doesn\u2019t have (a missing storefront) while leaving unsolved the '
     'problems it does have (real inventory operations, rated-hardware traceability). It was excluded from the '
     'detailed comparison above for this reason.', italic=True)

h2('1.8 Recommendation: inFlow vs. Zoho Inventory')
body('Because the custom portal is staying as the customer-facing layer, the deciding factor is not "which tool has '
     'the best B2B portal" \u2014 both Cin7 and Shopify are effectively overpaying for a feature that already exists '
     'elsewhere. The real decision is between inFlow and Zoho as the backend inventory engine.')

table = make_table(
    ['Factor', 'inFlow Inventory', 'Zoho Inventory', 'Edge'],
    [
        ['Entry cost', '$129/mo (1 location) / $349/mo for real multi-location', '$29\u2013129/mo covers 2\u20136 locations', 'Zoho'],
        ['API access', 'Paid add-on below Mid-Size tier ($49/mo extra)', 'Included on every plan, even Free', 'Zoho'],
        ['Multi-location depth', 'Strong once on Small Business tier', 'Strong, and cheaper per location', 'Zoho'],
        ['UI / learning curve', 'Very easy, modern', 'Easy, slightly more enterprise-feeling', 'Tie / inFlow'],
        ['QuickBooks sync', 'Included, solid', 'Weaker; ecosystem favors Zoho Books', 'inFlow'],
        ['Lot/serial tracking', 'Available (add-on)', 'Available, improving in 2026 (batch/lot pricing)', 'Tie'],
        ['Barcode/RFID', 'Barcode only', 'Barcode + RFID', 'Zoho'],
        ['Onboarding cost', 'Free at entry, $499 one-time from Small Business tier', 'No forced onboarding fee', 'Zoho'],
    ], col_widths=[1.3, 1.9, 1.9, 0.8]
)

h3('Recommendation: Zoho Inventory')
body('Zoho Inventory is the recommended choice, for four reasons specific to Phatrigging\u2019s situation:', bold=True)
bullet('Lowest total cost for the features actually needed. Since the B2B portal isn\u2019t needed from either tool (the custom portal already covers it), Zoho\u2019s Premium plan ($79/mo) covers 4 locations, batch tracking, and barcode generation \u2014 comparable functional depth to inFlow\u2019s $349/mo Small Business tier at roughly one-quarter the cost.')
bullet('API access is included at every tier, with no separate line-item fee \u2014 this matters directly, since the whole point of choosing a backend tool is to sync it into the existing portal via API. inFlow charges an extra $49/mo for the same access below its Mid-Size tier.')
bullet('RFID support gives more headroom toward the rated-hardware traceability need than inFlow currently offers, even though neither tool solves it fully out of the box.')
bullet('The commonly cited weakness ("B2B portal too thin") is irrelevant here, since Phatrigging is not looking for that at all.')
body('The one place inFlow wins clearly is QuickBooks sync depth and general polish/ease of use \u2014 if Phatrigging\u2019s '
     'books stay in QuickBooks specifically (not Zoho Books) and a slicker day-to-day UI matters more than saving on '
     'cost, inFlow remains a completely reasonable second choice. But on pure cost-to-capability for a backend-only '
     'role, Zoho is the stronger pick.', italic=True)

doc.add_page_break()

# ================= PART 2 =================
h1('Part 2 \u2014 Weight-Tier Inventory Analysis')

h2('2.1 Why weight tiers matter')
body('The order portal already calculates freight directly from cart weight (see index.html, freight() function): '
     'shipments totaling 150 lb or less ship UPS Ground ($18 + $0.42/lb, times a destination zone multiplier); '
     'shipments over 150 lb switch to LTL freight ($145 + $0.19/lb, same zone multiplier). Because the freight '
     'quote a customer sees is a direct function of summed item weight, having accurate weight data \u2014 and knowing '
     'which SKUs cluster into which weight bands \u2014 is operationally important for:')
bullet('Freight accuracy: mispriced item weight compounds across multi-item orders and skews the UPS-vs-LTL crossover.')
bullet('Packaging/handling planning: heavier tiers likely need pallet or crate handling rather than a poly bag and a label.')
bullet('Prioritizing the weight-sourcing effort: knowing which categories contain the heaviest/most freight-sensitive SKUs tells us where getting a real (non-placeholder) weight matters most.')

h2('2.2 Proposed tier definitions')
body('These tiers were chosen around the portal\u2019s existing UPS Ground / LTL freight breakpoint at 150 lb, split '
     'into finer bands below that line since nearly the entire current catalog falls under 150 lb per unit:')
make_table(
    ['Tier', 'Weight range', 'Rationale'],
    [
        ['Tier 1', '0\u201350 lb', 'Small hardware \u2014 hand-carryable, standard parcel shipping, no special handling'],
        ['Tier 2', '50\u2013100 lb', 'Two-person lift or hand truck; still parcel-shippable but nearing carrier weight surcharges'],
        ['Tier 3', '100\u2013150 lb', 'Upper edge of UPS Ground eligibility in the current freight logic; likely needs a pallet or crate'],
        ['Tier 4', '150+ lb', 'Automatically routes to LTL freight in the existing pricing code \u2014 pallet/freight-dock handling'],
    ], col_widths=[0.8, 1.3, 4.4]
)

h2('2.3 Current catalog breakdown by tier')
body(f'Across all {wdata["totalItems"]} SKUs currently in the catalog:', bold=True)

cat_rows = []
for cat, d in wdata['byCategory'].items():
    t1,t2,t3,t4 = [t['count'] for t in d['tiers']]
    cat_rows.append([cat, d['total'], t1, t2, t3, t4, d['maxWt'], d['placeholderCount']])
cat_rows.sort(key=lambda r: -r[1])

make_table(
    ['Category', 'SKUs', 'Tier 1\n(0-50)', 'Tier 2\n(50-100)', 'Tier 3\n(100-150)', 'Tier 4\n(150+)', 'Heaviest item (lb)', 'Still placeholder wt'],
    cat_rows,
    col_widths=[1.3, 0.5, 0.6, 0.6, 0.6, 0.5, 0.9, 0.9]
)

totalT1 = sum(r[2] for r in cat_rows)
totalT2 = sum(r[3] for r in cat_rows)
totalT3 = sum(r[4] for r in cat_rows)
totalT4 = sum(r[5] for r in cat_rows)

body('')
h3('Key findings')
bullet(f'Tier 1 (0\u201350 lb) dominates the catalog: {totalT1} of {wdata["totalItems"]} SKUs ({totalT1/wdata["totalItems"]*100:.0f}%). This is expected for a rigging hardware catalog \u2014 shackles, hooks, clips, and slings are individually light.')
bullet(f'Tier 2 (50\u2013100 lb): only {totalT2} SKUs, all large shackles (2" and 2-1/2" SAS/SPA) and one heavy deck fitting.')
bullet(f'Tiers 3 and 4 (100+ lb) are currently empty at the single-unit level: {totalT3 + totalT4} SKUs. No individual item in the catalog is heavy enough on its own to trigger LTL freight \u2014 the 150 lb LTL threshold in the existing freight code would currently only ever be reached through a multi-item order\u2019s summed weight, not any single SKU.')
bullet(f'{wdata["placeholderCount"]} of {wdata["totalItems"]} SKUs ({wdata["placeholderCount"]/wdata["totalItems"]*100:.0f}%) are still on a flat category-level placeholder weight, not a real sourced weight; only {wdata["sourcedCount"]} SKUs (Shackles only, so far) have a verified manufacturer/distributor-sourced weight with citation.')
bullet('The heaviest confirmed single item in the catalog is a 2-1/2" SAS shackle at 98.25 lb (Crosby G-2130, sourced this session) \u2014 still well inside Tier 2, nowhere near the LTL threshold on its own.')

h2('2.4 Data quality caveat \u2014 read before acting on these numbers')
body('This breakdown is only as good as the underlying weight data, and most of it is not real yet:', bold=True)
bullet(f'{wdata["placeholderCount"]} SKUs are sitting on a flat, made-up per-category placeholder (e.g., every Hook = 4.0 lb, every Nylon sling = 4.0 lb, every Hoist = 40.0 lb) rather than an actual per-item weight. This is why every non-Shackles category above shows 100% of its SKUs in Tier 1 \u2014 the placeholder values happen to be small, not because every item is actually that light.')
bullet('Only Shackles (32 of 61 SKUs) currently has verified, per-item, manufacturer/distributor-sourced weight data with a citation trail.')
bullet('Until more categories are sourced with real weights, this tier breakdown should be read as "what the freight math currently computes," not as "what packages will actually weigh." Heavier categories \u2014 Hoists (avg. placeholder 40 lb), Rope (avg. placeholder 33 lb), Deck fittings (up to 55 lb) \u2014 are the most likely to be materially wrong once real weights are sourced, and could plausibly push some SKUs into Tier 3 or even Tier 4 once corrected.')
body('Recommended reading: use this analysis to prioritize which categories to weight-source next (heaviest placeholder '
     'averages first \u2014 Hoists, Rope, Deck fittings, Barge & marine), not as a final freight-accuracy sign-off.', italic=True)

doc.add_page_break()

# ================= PART 3 =================
h1('Part 3 \u2014 Recommended Next Steps')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Pick the inventory backend. '); r.bold = True
p.add_run('Sign up for a Zoho Inventory trial (Premium tier, ~$79/mo) and confirm the API is workable for syncing '
          'stock levels and order data into the existing portal before committing annually.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Continue weight-sourcing by priority order. '); r.bold = True
p.add_run('Finish real per-item weights for the categories most likely to be wrong under the current flat placeholder: '
          'Hoists, Rope, Deck fittings, and Barge & marine, in addition to the remaining categories already agreed on '
          '(Chain, Wire rope clips, Master links, Wedge sockets, Tools, Shop supplies, and the still-unresolved Nylon '
          'slings / Poly round slings).')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Re-run the weight-tier analysis once more categories are sourced. '); r.bold = True
p.add_run('Confirm whether any SKUs actually land in Tier 3 or Tier 4 once real weights replace placeholders \u2014 this '
          'affects which orders will actually trigger LTL freight in practice.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Scope real accounts and payments as a separate phase. '); r.bold = True
p.add_run('Independent of inventory software, the portal currently has no real backend, no persistent accounts, and no '
          'real credit-card processing (see prior discussion) \u2014 that build-out (database, auth, Stripe integration) '
          'is a distinct project phase from inventory system selection.')

doc.add_page_break()
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = foot.add_run('Prepared by AI development assistant \u00b7 based on publicly available vendor pricing/feature pages and independent reviews as of the research date \u00b7 pricing and feature sets change frequently and should be reconfirmed directly with each vendor before purchase.')
r.italic = True
r.font.size = Pt(8.5)
r.font.color.rgb = GREY

doc.save('/home/user/webapp/.tmp/Phatrigging_Inventory_Software_and_Weight_Tier_Analysis.docx')
print("saved")
