from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10.5)

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GOLD = RGBColor(0xB8, 0x86, 0x0B)
GREY = RGBColor(0x55, 0x55, 0x55)
HILITE_BG = 'FDF3E0'  # light gold tint for highlight box cells

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

def highlight_box(title, bullets_list):
    """A single-cell shaded table used as a visually distinct highlight box."""
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.rows[0].cells[0]
    set_cell_bg(cell, HILITE_BG)
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = NAVY
    for b in bullets_list:
        bp = cell.add_paragraph(style='List Bullet')
        if isinstance(b, tuple):
            lead, rest = b
            rr = bp.add_run(lead); rr.bold = True; rr.font.size = Pt(10.5)
            rr2 = bp.add_run(rest); rr2.font.size = Pt(10.5)
        else:
            rr = bp.add_run(b); rr.font.size = Pt(10.5)
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
r = sub.add_run('Inventory Software Comparison & Recommendation')
r.font.size = Pt(16)
r.font.color.rgb = GOLD

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub2.add_run('Prepared for internal decision-making \u2014 not a vendor-endorsed document')
r.italic = True
r.font.size = Pt(10)
r.font.color.rgb = GREY

doc.add_paragraph()
body('Purpose of this document:', bold=True)
body('This document compares inventory-management platforms considered as the backend system of record for '
     'Phatrigging (QuickBooks, Fishbowl, inFlow Inventory, Cin7 Core, Zoho Inventory, and Shopify), and lands on '
     'a recommendation. It is a companion to a separate document, \u201cWeight-Tier Inventory Analysis,\u201d which covers '
     'catalog shipping-weight tiers and freight \u2014 a distinct topic, split out on its own.')

doc.add_paragraph()

# ================= QUICK HIGHLIGHTS =================
h1('Quick Highlights')
highlight_box('TL;DR \u2014 read this first', [
    ('Recommendation: Zoho Inventory. ', 'Lowest cost for the features actually needed (Premium tier, ~$79/mo, covers 4 locations + batch tracking + barcode), API access included on every tier with no extra fee, and RFID support gives more headroom for future rated-hardware traceability.'),
    ('Shopify is ruled out. ', 'It has a retail-shaped inventory model (no lot/serial/cert tracking, no real warehouse ops) and would duplicate the custom B2B portal Phatrigging already built \u2014 it solves a problem this business doesn\u2019t have.'),
    ('Cin7 Core is ruled out. ', 'Its headline feature \u2014 a built-in B2B ordering portal \u2014 is redundant here, since Phatrigging already has a custom portal with tiered pricing, weight-based freight, and rewards that Cin7\u2019s generic portal can\u2019t replicate. Its premium price partly buys a feature that would sit unused.'),
    ('Runner-up: inFlow Inventory. ', 'A completely reasonable second choice if QuickBooks-sync depth/polish matters more than raw cost \u2014 but inFlow charges extra for API access below its Mid-Size tier ($699/mo), while Zoho includes API access at every tier, including Free.'),
    ('None of these tools replace the existing order portal. ', 'The custom-built portal stays as the customer-facing layer regardless of which tool is chosen; the winning tool only needs to feed stock/purchasing data into it via API.'),
    ('Suggested next step: ', 'trial Zoho Inventory Premium (~$79/mo) and confirm its API is workable for syncing into the existing portal before committing annually.'),
])
doc.add_paragraph()
body('The rest of this document walks through the full comparison behind that recommendation.', italic=True)

doc.add_page_break()

# ================= CONTENTS =================
h1('Contents')
bullet('1.1 Baseline: QuickBooks')
bullet('1.2 Fishbowl')
bullet('1.3 inFlow Inventory')
bullet('1.4 Cin7 Core (deep dive)')
bullet('1.5 Zoho Inventory (deep dive)')
bullet('1.6 Side-by-side comparison table')
bullet('1.7 Why Shopify doesn\u2019t make sense here')
bullet('1.8 Recommendation: inFlow vs. Zoho')
bullet('1.9 Recommended next steps')

doc.add_page_break()

# ================= BODY =================
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

make_table(
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

h2('1.9 Recommended next steps')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Pick the inventory backend. '); r.bold = True
p.add_run('Sign up for a Zoho Inventory trial (Premium tier, ~$79/mo) and confirm the API is workable for syncing '
          'stock levels and order data into the existing portal before committing annually.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Pilot the API integration on a small slice first. '); r.bold = True
p.add_run('Sync one or two categories\u2019 stock levels into the portal before committing the full catalog, to validate '
          'the data model and rate limits under real usage.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Scope real accounts and payments as a separate phase. '); r.bold = True
p.add_run('Independent of inventory software, the portal currently has no real backend, no persistent accounts, and no '
          'real credit-card processing \u2014 that build-out (database, auth, Stripe integration) is a distinct project '
          'phase from inventory system selection.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Revisit if traceability requirements tighten. '); r.bold = True
p.add_run('If certificate/lot traceability for rated hardware becomes a hard compliance requirement, re-evaluate '
          'Fishbowl specifically \u2014 it has the strongest lot/serial handling of the tools reviewed, at the cost of a '
          'steeper learning curve and heavier implementation.')

doc.add_page_break()
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = foot.add_run('Prepared by AI development assistant \u00b7 based on publicly available vendor pricing/feature pages and independent reviews as of the research date \u00b7 pricing and feature sets change frequently and should be reconfirmed directly with each vendor before purchase.')
r.italic = True
r.font.size = Pt(8.5)
r.font.color.rgb = GREY

doc.save('/home/user/webapp/.tmp/Phatrigging_Inventory_Software_Comparison.docx')
print("saved A")
