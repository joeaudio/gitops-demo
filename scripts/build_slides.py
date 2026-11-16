"""Build the offline HTML, PDF and editable PowerPoint GitOps briefing."""

from html import escape
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from weasyprint import HTML


OUT = Path(__file__).resolve().parents[1] / "docs/slides"
OUT.mkdir(parents=True, exist_ok=True)
INK = "101B26"
PANEL = "172A35"
MINT = "B8F275"
WHITE = "F5F8F4"
MUTED = "ADC0C0"
CORAL = "FFAA8C"

SLIDES = [
    ("01 / PATTERN", "GitOps makes change reviewable", "A practical security story from a local k3s demo to ROSA.",
     ["Git is the desired state", "CI proves the change", "Argo CD reconciles the cluster"]),
    ("02 / WHY", "The problem security teams see", "Manual deployment steps are hard to review, repeat and audit.",
     ["Who changed the workload?", "Which checks ran first?", "Does the cluster match the approved version?"]),
    ("03 / LOOP", "One change, one visible path", "Issue → agent branch → PR → CI gates → image → Git tag → Argo CD → cluster.",
     ["Issue and agent draft", "Human PR review", "Tests and security scan", "Image and Git state", "Argo CD sync"]),
    ("04 / GATES", "Evidence before deployment", "A main-branch image is published only after the test and security jobs pass.",
     ["Unit: sourced advisory data", "Integration: HTTP page, JSON, headers", "Security: secrets, PII, container CVEs", "AI: primary source and human review"]),
    ("05 / TRUST", "Smaller trust boundaries", "The CI runner never receives a kubeconfig. Argo CD reads approved Git state.",
     ["Agent: branch only", "PR: human approval", "CI: scoped GitHub token", "Argo: pull and reconcile"]),
    ("06 / VALUE", "Safer and faster together", "A repeatable path reduces handoffs and makes the evidence easy to find.",
     ["Fewer manual cluster changes", "Fast feedback on every PR", "Rollback by reverting Git", "One audit trail for code and deployment"]),
    ("07 / ROSA", "Take the pattern to ROSA", "Keep the review and CI loop; replace the local target with a governed OpenShift environment.",
     ["Install Red Hat OpenShift GitOps", "Use a ROSA overlay and Route", "Apply namespace and RBAC policies", "Validate SCC and image access"]),
    ("08 / DEMO", "Show the evidence live", "Open the issue, merged PR, green workflow, Git tag, Argo CD app and site.",
     ["Issue #1 → PR #2", "CI tests + image + GitOps", "Argo: Synced / Healthy", "Site: four sourced briefings"]),
]


def rgb(code):
    return RGBColor.from_string(code)


def add_text(slide, text, x, y, w, h, size=18, color=WHITE, bold=False, font="Aptos", align=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(.02)
    frame.margin_top = frame.margin_bottom = Inches(.01)
    p = frame.paragraphs[0]
    p.text = text
    if align:
        p.alignment = align
    p.font.name = font
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = rgb(color)
    return box


def add_rect(slide, x, y, w, h, fill, line=None, radius=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE,
                                   Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    shape.line.fill.background() if line is None else None
    if line:
        shape.line.color.rgb = rgb(line)
    return shape


def build_pptx():
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    for index, (eyebrow, title, subtitle, cards) in enumerate(SLIDES, 1):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = rgb(INK)
        add_rect(slide, 0, 0, .16, 7.5, MINT)
        add_text(slide, "V/  VULNERABILITY DROP", .58, .38, 5.2, .4, 12, MINT, True)
        add_text(slide, eyebrow, .62, 1.18, 5, .35, 13, MINT, True)
        add_text(slide, title, .62, 1.62, 11.8, 1.28, 38, WHITE, True, "Aptos Display")
        add_text(slide, subtitle, .65, 2.95, 11.6, .85, 19, MUTED)
        count = len(cards)
        gap = .16
        width = (12.05 - gap * (count - 1)) / count
        for n, card in enumerate(cards):
            x = .64 + n * (width + gap)
            add_rect(slide, x, 4.18, width, 1.68, PANEL, "35515A", True)
            add_text(slide, f"{n + 1:02d}", x + .2, 4.38, .65, .35, 13, MINT, True)
            add_text(slide, card, x + .2, 4.78, width - .38, .78, 17 if count < 5 else 14, WHITE, True)
            if n < count - 1 and index in (3, 5, 7):
                add_text(slide, "→", x + width - .05, 4.7, .3, .5, 20, MINT, True)
        add_rect(slide, .64, 6.75, 12.05, .015, "35515A")
        add_text(slide, "OPEN SOURCE  •  ISSUE → REVIEW → PROOF → RECONCILE", .65, 6.9, 10, .3, 10, MUTED)
        add_text(slide, f"{index:02d} / 08", 11.6, 6.9, 1.1, .3, 10, MINT, True, align=PP_ALIGN.RIGHT)
    prs.save(OUT / "gitops-security-briefing.pptx")


def build_html():
    sections = []
    for index, (eyebrow, title, subtitle, cards) in enumerate(SLIDES, 1):
        cells = ''.join(f'<div class="card"><b>{n:02d}</b><p>{escape(card)}</p></div>' for n, card in enumerate(cards, 1))
        flow = " flow" if index in (3, 5, 7) else ""
        sections.append(f'''<section class="slide"><div class="rail"></div><header>V/ &nbsp; VULNERABILITY DROP</header>
        <main><div class="eyebrow">{escape(eyebrow)}</div><h1>{escape(title)}</h1><h2>{escape(subtitle)}</h2>
        <div class="cards count-{len(cards)}{flow}">{cells}</div></main>
        <footer><span>OPEN SOURCE &nbsp; • &nbsp; ISSUE → REVIEW → PROOF → RECONCILE</span><span>{index:02d} / 08</span></footer></section>''')
    css = '''@page{{size:13.333in 7.5in;margin:0}}*{{box-sizing:border-box}}html,body{{margin:0;background:#{INK};color:#{WHITE};font-family:Arial,sans-serif}}.slide{{width:13.333in;height:7.5in;position:relative;overflow:hidden;page-break-after:always;background:radial-gradient(circle at 87% 17%,#254940 0,#101b26 39%);padding:.4in .64in}}.rail{{position:absolute;left:0;top:0;width:.16in;height:100%;background:#{MINT}}}header{{font-size:12px;letter-spacing:.16em;color:#{MINT};font-weight:800}}main{{margin-top:.74in}}.eyebrow{{color:#{MINT};font-size:13px;letter-spacing:.18em;font-weight:800}}h1{{font-size:45px;letter-spacing:-.045em;margin:.35in 0 .14in;line-height:1.08}}h2{{font-size:20px;color:#{MUTED};font-weight:400;max-width:10.8in;line-height:1.4;margin:0}}.cards{{display:flex;gap:.16in;margin-top:.7in}}.card{{flex:1;min-width:0;height:1.7in;background:#{PANEL};border:1px solid #35515a;border-radius:12px;padding:.2in}}.card b{{font-size:13px;color:#{MINT}}}.card p{{font-size:18px;line-height:1.25;font-weight:700;margin:.26in 0 0}}.count-5 .card p{{font-size:15px}}footer{{position:absolute;left:.65in;right:.64in;bottom:.37in;border-top:1px solid #35515a;padding-top:.15in;display:flex;justify-content:space-between;color:#{MUTED};font-size:10px;letter-spacing:.07em}}footer span:last-child{{color:#{MINT}}}@media screen{{body{{padding:24px}}.slide{{margin:0 auto 24px;box-shadow:0 24px 60px #0008}}}}'''
    css = css.replace('{{', '{').replace('}}', '}')
    css += '.card{position:relative}.flow .card:not(:last-child):after{content:"→";position:absolute;right:-.16in;top:.64in;color:#B8F275;font-size:22px;z-index:2}'
    for name, value in {"INK": INK, "WHITE": WHITE, "MINT": MINT, "MUTED": MUTED, "PANEL": PANEL}.items():
        css = css.replace("#{" + name + "}", "#" + value)
    html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GitOps security briefing</title><style>' + css + '</style></head><body>' + ''.join(sections) + '</body></html>'
    path = OUT / "gitops-security-briefing.html"
    path.write_text(html)
    HTML(string=html, base_url=str(OUT)).write_pdf(OUT / "gitops-security-briefing.pdf")


if __name__ == "__main__":
    build_html()
    build_pptx()
    print("Built HTML, PDF and PowerPoint in", OUT)
