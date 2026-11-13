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

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(10.5)

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GOLD = RGBColor(0xB8, 0x86, 0x0B)
GREY = RGBColor(0x55, 0x55, 0x55)
WARN_RED = RGBColor(0x9E, 0x1B, 0x1B)
WARN_BG = 'FBEAEA'      # light red/pink tint for the caveat box
HILITE_BG = 'FDF3E0'    # light gold tint for the summary box

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

def colored_box(title, bullets_list, bg, title_color=NAVY):
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    cell = table.rows[0].cells[0]
    set_cell_bg(cell, bg)
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run(title)
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = title_color
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
r = sub.add_run('Weight-Tier Inventory Analysis (Preliminary / Placeholder Data)')
r.font.size = Pt(16)
r.font.color.rgb = GOLD

sub2 = doc.add_paragraph()
sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub2.add_run('Prepared for internal decision-making \u2014 NOT a final freight-accuracy sign-off')
r.italic = True
r.bold = True
r.font.size = Pt(10)
r.font.color.rgb = WARN_RED

doc.add_paragraph()
body('Purpose of this document:', bold=True)
body('This document groups Phatrigging\u2019s catalog into shipping-weight tiers, since weight directly drives the '
     'freight calculation already built into the order portal (UPS Ground for shipments \u2264150 lb, LTL freight above '
     'that). It is a companion to a separate document, \u201cInventory Software Comparison & Recommendation,\u201d which '
     'covers backend inventory-platform selection \u2014 a distinct topic, split out on its own.')

doc.add_paragraph()

# ================= QUICK HIGHLIGHTS (leads with the caveat) =================
h1('Quick Highlights')
colored_box('\u26a0 Read this first: the weight data behind this analysis is mostly NOT real yet', [
    (f'{wdata["placeholderCount"]} of {wdata["totalItems"]} SKUs ({wdata["placeholderCount"]/wdata["totalItems"]*100:.0f}%) are on flat, category-level placeholder weights ', '\u2014 e.g., every Hook = 4.0 lb, every Nylon sling = 4.0 lb, every Hoist = 40.0 lb \u2014 not an actual per-item weight. These numbers were never sourced from a spec sheet; they are generic stand-ins.'),
    (f'Only {wdata["sourcedCount"]} SKUs currently have verified, sourced weight data ', '\u2014 all of them in the Shackles category, with a citation trail back to manufacturer/distributor spec sheets. That is roughly 6% of the catalog.'),
    ('Every tier count below is therefore provisional. ', 'Because most placeholder weights happen to be small (3\u20134 lb for slings, 4 lb for hooks), the current breakdown shows the catalog as almost entirely Tier 1 \u2014 but that reflects the placeholder values, not necessarily reality. Categories with larger placeholder averages (Hoists at 40 lb, Rope at ~33 lb, Deck fittings up to 55 lb) are the most likely to shift, possibly into Tier 2 or 3, once real weights are sourced.'),
    ('Bottom line: ', 'treat this document as a plan for prioritizing weight-sourcing work and as a snapshot of \u201cwhat the freight math currently computes,\u201d not as a statement of what packages actually weigh or a final freight-accuracy report.'),
], WARN_BG, title_color=WARN_RED)

doc.add_paragraph()
colored_box('What IS solid in this document', [
    'The tier definitions themselves (Section 2) are anchored directly to the existing freight() code\u2019s 150 lb UPS Ground / LTL breakpoint \u2014 that logic is accurate and unaffected by the weight-data gap.',
    'The Shackles category (32 of 61 items) has real, sourced, citable weights and can be trusted as-is.',
    'The total catalog size (497 SKUs) and category boundaries are accurate; only the per-item weight values within most categories are placeholders.',
], HILITE_BG, title_color=NAVY)

doc.add_paragraph()
body('The rest of this document presents the tier framework and the current (largely placeholder-driven) breakdown, with the data-quality caveat above kept in mind throughout.', italic=True)

doc.add_page_break()

# ================= CONTENTS =================
h1('Contents')
bullet('1. Data quality status (expanded)')
bullet('2. Why weight tiers matter')
bullet('3. Proposed tier definitions')
bullet('4. Current catalog breakdown by tier (provisional)')
bullet('5. Key findings (read with caveat in mind)')
bullet('6. Recommended next steps')

doc.add_page_break()

# ================= SECTION 1: EXPANDED CAVEAT =================
h1('1. Data quality status (expanded)')
body('This section restates and expands the Quick Highlights warning in more detail, because it materially changes how every number in this document should be interpreted.', bold=True, color=WARN_RED)

h2('1.1 What "placeholder weight" means here')
body('When the catalog (index.html\u2019s ITEMS array) was first built, every item needed some value in its wt field '
     'for the freight calculator to function \u2014 so each category was assigned one flat, estimated weight applied '
     'to every SKU in that category, regardless of actual size/rating differences within it. These are flagged '
     'internally with a wtEst marker (or, for a few categories, no marker at all \u2014 which is itself a data gap). '
     f'{wdata["placeholderCount"]} of {wdata["totalItems"]} SKUs ({wdata["placeholderCount"]/wdata["totalItems"]*100:.0f}%) are still in this state.')

h2('1.2 What "sourced weight" means, and how little of the catalog has it')
body(f'Only {wdata["sourcedCount"]} SKUs \u2014 all within the Shackles category \u2014 have been individually researched '
     'against publicly published manufacturer spec sheets (e.g., Crosby), with a citation string (wtSrc) recorded '
     'against each item. That work was completed in a prior session and committed to the codebase. No other '
     'category has been through this process yet.')

h2('1.3 Categories most likely to be materially wrong')
body('Ranked by how large their placeholder average is (a rough proxy for how much room there is to be wrong):')
risk_rows = []
for cat, d in wdata['byCategory'].items():
    risk_rows.append((cat, d['total'], d['avgWt'], d['placeholderCount']))
risk_rows.sort(key=lambda r: -r[2])
make_table(
    ['Category', 'SKUs', 'Current placeholder avg (lb)', 'SKUs still placeholder'],
    [[c, t, a, p] for c, t, a, p in risk_rows[:8]],
    col_widths=[1.8, 0.9, 2.2, 1.8]
)
body('Hoists, Rope, Barge & marine, and Deck fittings sit at the top of this list \u2014 not because they are confirmed '
     'heavy, but because their placeholder averages are highest, meaning the eventual correction (once real weights '
     'are sourced) has the most room to move the needle, potentially pushing individual SKUs into Tier 2 or Tier 3.', italic=True)

h2('1.4 Why this matters beyond just "the numbers might be off"')
bullet('Freight quotes shown to customers today are computed directly from these placeholder weights \u2014 a customer ordering a Hoist is currently quoted freight based on a flat 40 lb assumption, which may be significantly wrong for a specific model/capacity.')
bullet('Any business decision made from this document\u2014prioritizing packaging changes, LTL carrier negotiations, pallet planning\u2014should be treated as directional, not final, until more categories are sourced.')
bullet('The Shackles weight-sourcing effort (32 of 61 items, real data) is the only part of the catalog where this concern does not apply.')

doc.add_page_break()

# ================= SECTION 2 =================
h1('2. Why weight tiers matter')
body('The order portal already calculates freight directly from cart weight (see index.html, freight() function): '
     'shipments totaling 150 lb or less ship UPS Ground ($18 + $0.42/lb, times a destination zone multiplier); '
     'shipments over 150 lb switch to LTL freight ($145 + $0.19/lb, same zone multiplier). Because the freight '
     'quote a customer sees is a direct function of summed item weight, having accurate weight data \u2014 and knowing '
     'which SKUs cluster into which weight bands \u2014 is operationally important for:')
bullet('Freight accuracy: mispriced item weight compounds across multi-item orders and skews the UPS-vs-LTL crossover.')
bullet('Packaging/handling planning: heavier tiers likely need pallet or crate handling rather than a poly bag and a label.')
bullet('Prioritizing the weight-sourcing effort: knowing which categories contain the heaviest/most freight-sensitive SKUs tells us where getting a real (non-placeholder) weight matters most.')
body('Note: this section describes why the tier framework matters. It does not by itself validate the current data \u2014 see Section 1 for the data-quality status.', italic=True, color=WARN_RED)

# ================= SECTION 3 =================
h1('3. Proposed tier definitions')
body('These tiers were chosen around the portal\u2019s existing UPS Ground / LTL freight breakpoint at 150 lb, split '
     'into finer bands below that line. This framework itself is solid regardless of the weight-data gap \u2014 it is '
     'only the placement of specific SKUs into these tiers (Section 4) that is currently unreliable:')
make_table(
    ['Tier', 'Weight range', 'Rationale'],
    [
        ['Tier 1', '0\u201350 lb', 'Small hardware \u2014 hand-carryable, standard parcel shipping, no special handling'],
        ['Tier 2', '50\u2013100 lb', 'Two-person lift or hand truck; still parcel-shippable but nearing carrier weight surcharges'],
        ['Tier 3', '100\u2013150 lb', 'Upper edge of UPS Ground eligibility in the current freight logic; likely needs a pallet or crate'],
        ['Tier 4', '150+ lb', 'Automatically routes to LTL freight in the existing pricing code \u2014 pallet/freight-dock handling'],
    ], col_widths=[0.8, 1.3, 4.4]
)

doc.add_page_break()

# ================= SECTION 4 =================
h1('4. Current catalog breakdown by tier (provisional)')
colored_box('Reminder before reading this table', [
    'Every row below except Shackles is built almost entirely from placeholder weights. Read the "Still placeholder wt" column on the right of the table \u2014 not the tier columns \u2014 as the most trustworthy number in each row.',
], WARN_BG, title_color=WARN_RED)
doc.add_paragraph()
body(f'Across all {wdata["totalItems"]} SKUs currently in the catalog, using whatever weight value (real or placeholder) each item currently carries:', bold=True)

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

doc.add_page_break()

# ================= SECTION 5 =================
h1('5. Key findings (read with caveat in mind)')
body('Each finding below is phrased to reflect that it describes the current, largely placeholder-driven data \u2014 not a confirmed physical fact about the catalog.', italic=True, color=WARN_RED)
bullet(f'Based on current data (mostly placeholders), Tier 1 (0\u201350 lb) appears to dominate the catalog: {totalT1} of {wdata["totalItems"]} SKUs ({totalT1/wdata["totalItems"]*100:.0f}%). This is plausible for a rigging hardware catalog \u2014 shackles, hooks, clips, and slings are individually light \u2014 but it is also exactly what would happen if every category\u2019s placeholder simply happens to be a small number, regardless of true weight.')
bullet(f'Tier 2 (50\u2013100 lb) currently shows only {totalT2} SKUs, all large shackles (2" and 2-1/2" SAS/SPA) and one deck fitting flagged at the tier boundary \u2014 and Shackles is the one category where this placement is actually verified, not placeholder-driven.')
bullet(f'Tiers 3 and 4 (100+ lb) show as empty at the single-unit level: {totalT3 + totalT4} SKUs. This should NOT be read as "no item is that heavy" \u2014 it may simply mean no placeholder value happens to be that high yet. Hoists (placeholder avg. 40 lb), Rope (placeholder avg. ~33 lb), and Deck fittings (up to 55 lb placeholder) are plausible candidates to move into Tier 2 or 3 once real weights replace their placeholders.')
bullet(f'{wdata["placeholderCount"]} of {wdata["totalItems"]} SKUs ({wdata["placeholderCount"]/wdata["totalItems"]*100:.0f}%) are still on a flat category-level placeholder weight; only {wdata["sourcedCount"]} SKUs (Shackles only) have a verified, sourced weight with citation. This is the single most important number in this document.')
bullet('The heaviest CONFIRMED (non-placeholder) item in the catalog is a 2-1/2" SAS shackle at 98.25 lb (Crosby G-2130, sourced in a prior session) \u2014 still inside Tier 2, nowhere near the LTL threshold on its own. No claim is made here about the heaviest item overall, since most categories are unverified.')

doc.add_page_break()

# ================= SECTION 6 =================
h1('6. Recommended next steps')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Do not act on tier placements yet for non-Shackles categories. '); r.bold = True
p.add_run('Treat Sections 4\u20135 as a prioritization map for sourcing work, not as inputs to freight, packaging, or carrier-contract decisions.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Source real weights next for the highest-risk categories identified in Section 1.3. '); r.bold = True
p.add_run('In order: Hoists, Rope, Barge & marine, and Deck fittings \u2014 these have the highest placeholder averages and the most room to shift tiers once corrected.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Revisit Nylon slings and Poly round slings weight-sourcing when time allows. '); r.bold = True
p.add_run('This was intentionally paused in a prior session due to unreliable distributor source data (Poly round slings had a workable source; Nylon slings\u2019 source data was internally inconsistent) \u2014 not because these categories are low priority.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Re-run this analysis after each new category is sourced. '); r.bold = True
p.add_run('Regenerate the tier breakdown from the live catalog data each time a category moves from placeholder to sourced, to track how the picture changes and confirm whether any SKUs actually land in Tier 3 or 4.')
p = doc.add_paragraph(style='List Number')
r = p.add_run('Only treat this document as final once the placeholder count is at or near zero. '); r.bold = True
p.add_run('Until then, continue to caveat any freight, packaging, or carrier decisions derived from it.')

doc.add_page_break()
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = foot.add_run('Prepared by AI development assistant \u00b7 weight data computed directly from the live catalog (index.html) as of the generation date \u00b7 the majority of per-item weights are category-level placeholders pending professional/manufacturer sourcing \u2014 see Section 1 before relying on any figure in this document.')
r.italic = True
r.font.size = Pt(8.5)
r.font.color.rgb = GREY

doc.save('/home/user/webapp/.tmp/Phatrigging_Weight_Tier_Analysis_PRELIMINARY.docx')
print("saved B")
