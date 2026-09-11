# -*- coding: utf-8 -*-
"""
213.docx -> LaTeX 项目报告书转换脚本 (v2)
"""
import re, sys, os, shutil
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_TEX = os.path.join(os.path.dirname(BASE), '213.tex')
FIG_DIR = os.path.join(os.path.dirname(BASE), 'figures')

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
M = '{http://schemas.openxmlformats.org/officeDocument/2006/math}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A_BLP = '{http://schemas.openxmlformats.org/drawingml/2006/main}blip'

tree = ET.parse(os.path.join(BASE, 'word/document.xml'))
styles_tree = ET.parse(os.path.join(BASE, 'word/styles.xml'))
rels_tree = ET.parse(os.path.join(BASE, 'word/_rels/document.xml.rels'))

style_map = {}
for st in styles_tree.iter(W + 'style'):
    sid = st.get(W + 'styleId')
    nm = st.find(W + 'name')
    style_map[sid] = nm.get(W + 'val') if nm is not None else ''

rel_map = {}
for rel in rels_tree.getroot():
    rid = rel.get('Id')
    if rid and rel.get('Type', '').endswith('/image'):
        rel_map[rid] = rel.get('Target')

# ---------------- OMML -> LaTeX ----------------
MATH_TRANS = {
    'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta', 'ε': r'\varepsilon',
    'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta', 'ι': r'\iota', 'κ': r'\kappa',
    'λ': r'\lambda', 'μ': r'\mu', 'ν': r'\nu', 'ξ': r'\xi', 'π': r'\pi',
    'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'υ': r'\upsilon', 'φ': r'\varphi',
    'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
    'Γ': r'\Gamma', 'Δ': r'\Delta', 'Θ': r'\Theta', 'Λ': r'\Lambda', 'Ξ': r'\Xi',
    'Π': r'\Pi', 'Σ': r'\Sigma', 'Φ': r'\Phi', 'Ψ': r'\Psi', 'Ω': r'\Omega',
    '×': r'\times', '÷': r'\div', '±': r'\pm', '∓': r'\mp', '·': r'\cdot',
    '≤': r'\leq', '≥': r'\geq', '≠': r'\neq', '≈': r'\approx', '≡': r'\equiv',
    '∞': r'\infty', '∂': r'\partial', '∇': r'\nabla', '∫': r'\int', '∮': r'\oint',
    '∑': r'\sum', '∏': r'\prod', '→': r'\rightarrow', '←': r'\leftarrow',
    '⇒': r'\Rightarrow', '⇔': r'\Leftrightarrow', '∈': r'\in', '∉': r'\notin',
    '∝': r'\propto', '≪': r'\ll', '≫': r'\gg', '°': r'^\circ', '″': r"''",
    '…': r'\cdots', '⋯': r'\cdots', '∼': r'\sim', '≅': r'\cong', '∥': r'\parallel',
    '⊥': r'\perp', '∠': r'\angle', '⟶': r'\longrightarrow', '−': '-', '–': '-',
    '′': "'", '≃': r'\simeq', '∪': r'\cup', '∩': r'\cap',
    '\u2062': '', '\u2061': '', '\u200b': '',
}
FUNC_NAMES = {'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'arcsin', 'arccos', 'arctan',
              'ln', 'log', 'lg', 'exp', 'lim', 'max', 'min', 'det', 'Re', 'Im'}

def _trans_chars(s):
    out = []
    for i, ch in enumerate(s):
        if ch in MATH_TRANS:
            tr = MATH_TRANS[ch]
            out.append(tr)
            # 宏以字母结尾且下一个源字符是 ASCII 字母时补空格(如 \pia -> \pi a, \pmk -> \pm k)
            if (tr.startswith('\\') and tr[-1:].isalpha()
                    and i + 1 < len(s) and s[i + 1].isascii() and s[i + 1].isalpha()):
                out.append(' ')
        elif ch in '{}#%&$~^_\\':
            out.append('\\' + ch)
        else:
            out.append(ch)
    return ''.join(out)

def math_text(t):
    if t is None:
        return ''
    if t in FUNC_NAMES:
        return '\\' + t + ' '
    # 以 U+2061(函数应用符) 为界: 分段前一段结尾若是函数名则转为 \sin 等
    segs = t.split('⁡')
    out = []
    for idx, seg in enumerate(segs):
        if idx < len(segs) - 1:
            m = re.match(r'^(.*?)([a-zA-Z]+)$', seg, re.S)
            if m:
                tail = m.group(2)
                cand = None
                for name in sorted(FUNC_NAMES, key=len, reverse=True):
                    if tail.endswith(name):
                        cand = name
                        break
                if cand:
                    prefix = m.group(1) + tail[:-len(cand)]
                    out.append(_trans_chars(prefix) + '\\' + cand + ' ')
                    continue
        out.append(_trans_chars(seg))
    return ''.join(out)

def m_child(el, name):
    c = el.find(M + name)
    return math_children(c) if c is not None else ''

def math_children(el):
    if el is None:
        return ''
    return ''.join(math_el(c) for c in list(el))

def math_el(el):
    tag = el.tag
    if tag == M + 't':
        return math_text(el.text)
    if tag == M + 'r':
        sty = None
        mpr = el.find(M + 'rPr')
        if mpr is not None:
            se = mpr.find(M + 'sty')
            if se is not None:
                sty = se.get(M + 'val')
        txt = math_children(el)
        if sty == 'p' and txt:
            s = txt.strip()
            if s in FUNC_NAMES:
                return '\\' + s + ' '
            return r'\mathrm{%s}' % txt
        return txt
    if tag == M + 'f':
        return r'\frac{%s}{%s}' % (m_child(el, 'num'), m_child(el, 'den'))
    if tag == M + 'sSup':
        return '{%s}^{%s}' % (m_child(el, 'e'), m_child(el, 'sup'))
    if tag == M + 'sSub':
        return '{%s}_{%s}' % (m_child(el, 'e'), m_child(el, 'sub'))
    if tag == M + 'sSubSup':
        return '{%s}_{%s}^{%s}' % (m_child(el, 'e'), m_child(el, 'sub'), m_child(el, 'sup'))
    if tag == M + 'sPre':
        sub = el.find(M + 'sub')
        sup = el.find(M + 'sup')
        e = el.find(M + 'e')
        parts = []
        if sub is not None:
            parts.append('_{%s}' % math_children(sub))
        if sup is not None:
            parts.append('^{%s}' % math_children(sup))
        return ''.join(parts) + ('{%s}' % math_children(e) if e is not None else '')
    if tag == M + 'd':
        dpr = el.find(M + 'dPr')
        beg, end, sep = '(', ')', None
        if dpr is not None:
            b = dpr.find(M + 'begChr')
            e2 = dpr.find(M + 'endChr')
            s = dpr.find(M + 'sepChr')
            if b is not None and b.get(M + 'val'):
                beg = b.get(M + 'val')
            if e2 is not None and e2.get(M + 'val'):
                end = e2.get(M + 'val')
            if s is not None and s.get(M + 'val'):
                sep = s.get(M + 'val')
        bmap = {'(': '(', ')': ')', '[': '[', ']': ']', '{': r'\{', '}': r'\}',
                '|': '|', '‖': r'\|', '': '', '⟨': r'\langle', '⟩': r'\rangle'}
        bl, br = bmap.get(beg, '('), bmap.get(end, ')')
        if not bl and beg:
            bl, br = math_text(beg), math_text(end)
        es = el.findall(M + 'e')
        if len(es) <= 1:
            inner = math_children(es[0]) if es else ''
            return r'\left%s %s \right%s' % (bl, inner, br)
        parts = [math_children(e) for e in es]
        if sep:
            sep_t = bmap.get(sep, sep)
            body = (' \\middle%s ' % sep_t).join(parts)
        else:
            body = ' '.join(parts)
        return r'\left%s %s \right%s' % (bl, body, br)
    if tag == M + 'nary':
        npr = el.find(M + 'naryPr')
        chrval = '∫'
        if npr is not None:
            ce = npr.find(M + 'chr')
            if ce is not None and ce.get(M + 'val'):
                chrval = ce.get(M + 'val')
        opmap = {'∫': r'\int', '∑': r'\sum', '∏': r'\prod', '∮': r'\oint',
                 '∬': r'\iint', '∭': r'\iiint', '∪': r'\bigcup', '∩': r'\bigcap'}
        op = opmap.get(chrval, r'\int')
        sub = el.find(M + 'sub')
        sup = el.find(M + 'sup')
        e = el.find(M + 'e')
        s = math_children(sub) if sub is not None else ''
        t = math_children(sup) if sup is not None else ''
        lim = ''
        if s and t:
            lim = '_{%s}^{%s}' % (s, t)
        elif s:
            lim = '_{%s}' % s
        elif t:
            lim = '^{%s}' % t
        return '%s%s %s' % (op, lim, math_children(e))
    if tag == M + 'rad':
        deg = el.find(M + 'deg')
        if deg is not None and len(list(deg)) > 0:
            return r'\sqrt[%s]{%s}' % (math_children(deg), m_child(el, 'e'))
        return r'\sqrt{%s}' % m_child(el, 'e')
    if tag == M + 'func':
        fn = el.find(M + 'fName')
        fn_txt = math_children(fn).strip()
        arg = m_child(el, 'e')
        return '%s{%s}' % (fn_txt, arg)
    if tag == M + 'limLow':
        return r'\lim_{%s} %s' % (m_child(el, 'lim'), m_child(el, 'e'))
    if tag == M + 'limUpp':
        return r'\lim^{%s} %s' % (m_child(el, 'lim'), m_child(el, 'e'))
    if tag == M + 'bar':
        pos = 'top'
        bpr = el.find(M + 'barPr')
        if bpr is not None:
            pe = bpr.find(M + 'pos')
            if pe is not None:
                pos = pe.get(M + 'val')
        if pos == 'bot':
            return r'\underline{%s}' % m_child(el, 'e')
        return r'\bar{%s}' % m_child(el, 'e')
    if tag == M + 'acc':
        chrval = ''
        apr = el.find(M + 'accPr')
        if apr is not None:
            ce = apr.find(M + 'chr')
            if ce is not None and ce.get(M + 'val'):
                chrval = ce.get(M + 'val')
        amap = {'^': r'\hat', '~': r'\tilde', '¯': r'\bar', '\u0307': r'\dot',
                '\u00a8': r'\ddot', '\u20d7': r'\vec', '→': r'\overrightarrow'}
        a = amap.get(chrval, r'\hat')
        return '%s{%s}' % (a, m_child(el, 'e'))
    if tag == M + 'eqArr':
        rows = [math_children(e) for e in el.findall(M + 'e')]
        return r'\begin{gathered} %s \end{gathered}' % r' \\ '.join(rows)
    if tag == M + 'm':
        rows = []
        for mr in el.findall(M + 'mr'):
            cells = [math_children(c) for c in mr.findall(M + 'e')]
            rows.append(' & '.join(cells))
        return r'\begin{pmatrix}%s\end{pmatrix}' % r' \\ '.join(rows)
    if tag == M + 'groupChr':
        chrval = ''
        gpr = el.find(M + 'groupChrPr')
        if gpr is not None:
            ce = gpr.find(M + 'chr')
            if ce is not None and ce.get(M + 'val'):
                chrval = ce.get(M + 'val')
        e = m_child(el, 'e')
        sup = el.find(M + 'sup')
        sub = el.find(M + 'sub')
        if chrval == '\u23de':
            return r'\overbrace{%s}^{%s}' % (e, math_children(sup) if sup is not None else '')
        if chrval == '\u23df':
            return r'\underbrace{%s}_{%s}' % (e, math_children(sub) if sub is not None else '')
        return e
    if tag == M + 'borderBox':
        return r'\boxed{%s}' % m_child(el, 'e')
    if tag == M + 'phant':
        return r'\phantom{%s}' % m_child(el, 'e')
    if tag == M + 'box' or tag == M + 'sty':
        return math_children(el)
    return math_children(el)

# ---------------- 文本转义 ----------------
def esc(t):
    return (t.replace('\\', r'\textbackslash{}')
             .replace('{', r'\{').replace('}', r'\}')
             .replace('$', r'\$').replace('&', r'\&')
             .replace('#', r'\#').replace('%', r'\%')
             .replace('_', r'\_').replace('~', r'\textasciitilde{}')
             .replace('^', r'\textasciicircum{}'))

# ---------------- 图片处理 ----------------
FORMULA_DISPLAY_IMG = {
    'rId14': ('image1.png', r'''U(P)=C\oint_{\Sigma}U(Q)\,\frac{e^{ikr}}{r}\,K(\theta)\,\mathrm{d}\sigma'''),
    'rId16': ('image3.png', r'''d\sin\theta=k\lambda,\qquad a\sin\theta=k'\lambda'''),
    'rId18': ('image5.GIF', r'''\Delta\theta_k=\frac{\lambda}{Nd\cos\theta_k}'''),
    'rId22': ('image9.GIF', r'''R=\frac{\lambda}{\delta\lambda}=kN'''),
}
FORMULA_INLINE_IMG = {
    'rId19': r'\theta_k',
    'rId20': r'\delta\lambda',
    'rId21': r'\lambda',
}

used_media = set()

def resolve_media(rid):
    tgt = rel_map.get(rid, '')
    if not tgt:
        return None
    src = os.path.join(BASE, 'word', tgt.replace('/', os.sep))
    if not os.path.exists(src):
        d = os.path.dirname(src)
        base = os.path.basename(src).lower()
        for f in os.listdir(d):
            if f.lower() == base:
                src = os.path.join(d, f)
                break
    return src

def media_ref(rid):
    src = resolve_media(rid)
    if src is None:
        return 'MISSING'
    ext = os.path.splitext(src)[1].lower()
    name = os.path.basename(src)
    if ext in ('.gif', '.svg'):
        name = os.path.splitext(name)[0] + '.png'
    used_media.add((src, name))
    return 'figures/' + name

PLACEHOLDERS = []

def protect(s):
    PLACEHOLDERS.append(s)
    return '\x00PH%d\x00' % (len(PLACEHOLDERS) - 1)

def restore(t):
    return re.sub(r'\x00PH(\d+)\x00', lambda m: PLACEHOLDERS[int(m.group(1))], t)

def bold_on(el):
    v = el.get(W + 'val')
    if v in ('0', 'false', 'off'):
        return False
    return True

# ---------------- 段落解析 ----------------
def iter_block_children(el):
    out = []
    for c in list(el):
        tag = c.tag
        if tag == W + 'pPr':
            continue
        if tag in (W + 'bookmarkStart', W + 'bookmarkEnd', W + 'proofErr',
                   W + 'commentRangeStart', W + 'commentRangeEnd'):
            continue
        out.append(c)
    return out

def run_pieces(r):
    rpr = r.find(W + 'rPr')
    bold = italic = strike = ul = False
    va = None
    if rpr is not None:
        be = rpr.find(W + 'b')
        ie = rpr.find(W + 'i')
        se = rpr.find(W + 'strike')
        ue = rpr.find(W + 'u')
        ve = rpr.find(W + 'vertAlign')
        bold = be is not None and bold_on(be)
        italic = ie is not None and bold_on(ie)
        strike = se is not None and bold_on(se)
        ul = ue is not None and bold_on(ue)
        if ve is not None:
            va = ve.get(W + 'val')
    key = (bold, italic, strike, ul, va or '')
    parts = []
    for c in list(r):
        tag = c.tag
        if tag == W + 't':
            parts.append(c.text or '')
        elif tag == W + 'drawing':
            for blip in c.iter(A_BLP):
                rid = blip.get(R + 'embed')
                if rid in FORMULA_INLINE_IMG:
                    parts.append(protect('$%s$' % FORMULA_INLINE_IMG[rid]))
                elif rid in FORMULA_DISPLAY_IMG:
                    parts.append(protect(r'\includegraphics[width=0.7\textwidth]{%s}' % media_ref(rid)))
                else:
                    parts.append(protect(r'\includegraphics{%s}' % media_ref(rid)))
        elif tag == W + 'br':
            parts.append('\n\n')
        elif tag == W + 'tab':
            parts.append(' ')
        elif tag in (W + 'fldChar', W + 'instrText'):
            continue
    txt = ''.join(parts)
    return key, txt

def fmt_wrap(key, txt):
    bold, italic, strike, ul, va = key
    txt = esc(txt)
    txt = restore(txt)
    if va == 'superscript':
        txt = r'\textsuperscript{%s}' % txt
    elif va == 'subscript':
        txt = r'\textsubscript{%s}' % txt
    if bold and italic:
        txt = r'\textbf{\textit{%s}}' % txt
    elif bold:
        txt = r'\textbf{%s}' % txt
    elif italic:
        txt = r'\textit{%s}' % txt
    if strike:
        txt = r'\sout{%s}' % txt
    return txt

def para_info(p):
    style = numid = ilvl = jc = None
    ppr = p.find(W + 'pPr')
    if ppr is not None:
        se = ppr.find(W + 'pStyle')
        if se is not None:
            style = se.get(W + 'val')
        ne = ppr.find(W + 'numPr')
        if ne is not None:
            ni = ne.find(W + 'numId')
            il = ne.find(W + 'ilvl')
            if ni is not None:
                numid = ni.get(W + 'val')
            if il is not None:
                ilvl = il.get(W + 'val')
        je = ppr.find(W + 'jc')
        if je is not None:
            jc = je.get(W + 'val')
    pieces = []
    imgs = []
    for c in iter_block_children(p):
        tag = c.tag
        if tag == W + 'r':
            pieces.append(run_pieces(c))
            for blip in c.iter(A_BLP):
                rid = blip.get(R + 'embed')
                if rid:
                    imgs.append(rid)
        elif tag == W + 'hyperlink':
            for r in c.findall(W + 'r'):
                pieces.append(run_pieces(r))
        elif tag == M + 'oMath':
            pieces.append((None, protect('$%s$' % math_children(c))))
        elif tag == M + 'oMathPara':
            om = c.find(M + 'oMath')
            pieces.append((None, protect('\n\\begin{equation*}\n%s\n\\end{equation*}\n' % math_children(om))))
    merged = []
    for key, txt in pieces:
        if merged and merged[-1][0] == key:
            merged[-1] = (key, merged[-1][1] + txt)
        else:
            merged.append((key, txt))
    chunks = []
    for key, txt in merged:
        if key is None:
            chunks.append(restore(txt))
        else:
            chunks.append(fmt_wrap(key, txt))
    content = ''.join(chunks)
    return style, numid, ilvl, jc, content, imgs

def plain_text(p):
    return ''.join(t.text or '' for t in p.iter(W + 't'))

# ---------------- 表格解析 ----------------
def table_rows(tbl):
    rows = []
    for tr in tbl.findall(W + 'tr'):
        cells = []
        for tc in tr.findall(W + 'tc'):
            cell_paras = []
            imgs = []
            for p in tc.findall(W + 'p'):
                st, numid, ilvl, jc, content, pimgs = para_info(p)
                cell_paras.append((plain_text(p), content))
                imgs.extend(pimgs)
            cells.append({'paras': cell_paras, 'imgs': imgs})
        rows.append(cells)
    return rows

def cell_plain_lines(cell):
    return [t for t, c in cell['paras']]

def looks_like_code(cell):
    for t, c in cell['paras']:
        if re.search(r'(from manim|import numpy|import matplotlib|def |class |self\.|\bAxes\b|\bplt\.)', t):
            return True
    return False

# ---------------- 主转换 ----------------
body = tree.getroot().find(W + 'body')
elements = [e for e in list(body) if e.tag != W + 'sectPr']

out = []
warnings = []

def w(*args):
    out.append(' '.join(str(a) for a in args))

i = 0
n = len(elements)

# ---- 标题页 ----
title_elements = []
while i < n:
    el = elements[i]
    if el.tag == W + 'p':
        t = plain_text(el).strip()
        if t == '摘要':
            break
    title_elements.append(el)
    i += 1

title_paras = []
title_labels = []
title_table_vals = []
for el in title_elements:
    if el.tag == W + 'p':
        t = plain_text(el).strip()
        if not t:
            continue
        szs = [e.get(W + 'val') for e in el.iter(W + 'sz')]
        if re.match(r'^[\s\w]*(赛道|课题)[\s：:]*$', t) or t.rstrip().endswith(':'):
            title_labels.append(re.sub(r'\s+', '', t).rstrip('：:') + '：')
        else:
            title_paras.append((t, szs))
    elif el.tag == W + 'tbl':
        for row in table_rows(el):
            for cell in row:
                txt = ' '.join(cell_plain_lines(cell)).strip()
                if txt:
                    title_table_vals.append(txt)

title_lines_before = [p for p in title_paras if p[0] != '2026年8月28日']
date_line = next((p for p in title_paras if p[0] == '2026年8月28日'), None)

w(r'\begin{titlepage}')
w(r'\begin{center}')
w(r'\vspace*{1.5cm}')
for t, szs in title_lines_before:
    if '96' in szs:
        w(r'{\fontsize{48pt}{58pt}\selectfont\bfseries %s\par}' % esc(t))
        w(r'\vspace{1cm}')
    else:
        w(r'{\zihao{3}\heiti\bfseries %s\par}' % esc(t))
        w(r'\vspace{0.8cm}')
w(r'\vspace{2.5cm}')
for lab, val in zip(title_labels, title_table_vals):
    w(r'{\zihao{3} %s\underline{%s}\par}' % (esc(lab), esc(val)))
    w(r'\vspace{1.2cm}')
if date_line is not None:
    w(r'\vfill')
    w(r'{\zihao{3} %s\par}' % esc(date_line[0]))
w(r'\end{center}')
w(r'\end{titlepage}')
w('')

# ---- 摘要区 ----
i += 1  # 跳过 "摘要" 标题
w(r'\section*{摘要}')
abstract_pending = True
while i < n:
    el = elements[i]
    if el.tag == W + 'p':
        t = plain_text(el).strip()
        st, numid, ilvl, jc, content, imgs = para_info(el)
        if not t and not content.strip() and not imgs:
            i += 1
            continue
        if t.startswith('关键词'):
            rest = t[len('关键词'):].lstrip('：:')
            w(r'\noindent 关键词：\textbf{%s}' % esc(rest))
            w('')
            abstract_pending = False
            i += 1
            while i < n:
                el2 = elements[i]
                if el2.tag == W + 'p' and not plain_text(el2).strip():
                    i += 1
                    continue
                break
            break
        if abstract_pending:
            w((content.strip() or esc(t)).strip())
            w('')
            i += 1
            continue
    i += 1

# ---- 目录区 ----
while i < n:
    el = elements[i]
    if el.tag == W + 'p':
        st, numid, ilvl, jc, content, imgs = para_info(el)
        sname = style_map.get(st, '') if st else ''
        if sname.startswith('toc') and plain_text(el).strip():
            w(r'\tableofcontents')
            w('')
            i += 1
            while i < n:
                el2 = elements[i]
                if el2.tag == W + 'p':
                    st2 = para_info(el2)[0]
                    sname2 = style_map.get(st2, '') if st2 else ''
                    if sname2.startswith('toc'):
                        i += 1
                        continue
                break
            break
        if not plain_text(el).strip():
            i += 1
            continue
        break
    i += 1

# ---- 正文循环 ----
pending_list = None
in_bibliography = False
bib_items = []

def flush_list():
    global pending_list
    if pending_list == 'enumerate':
        w(r'\end{enumerate}')
        w('')
    pending_list = None

def flush_bib():
    global in_bibliography, bib_items
    if in_bibliography:
        w(r'\begin{thebibliography}{9}')
        for k, item in enumerate(bib_items, 1):
            w(r'\bibitem{ref%d} %s' % (k, item))
        w(r'\end{thebibliography}')
        w('')
        in_bibliography = False
        bib_items = []

HEAD_NUM_RE = re.compile(r'^\s*(?:\d+(?:\.\d+)*)[\.\s]*\s*')

while i < n:
    el = elements[i]
    if el.tag == W + 'p':
        st, numid, ilvl, jc, content, imgs = para_info(el)
        sname = style_map.get(st, '') if st else ''
        t = plain_text(el).strip()
        if not t and not content.strip() and not imgs:
            i += 1
            continue
        if sname.startswith('heading'):
            flush_list()
            # 标题可能带字面序号(如 "6 参考资料"), 先去序号再比较
            htxt0 = HEAD_NUM_RE.sub('', t).strip()
            if htxt0 == '摘要':
                i += 1
                continue
            if htxt0 == '参考资料':
                flush_bib()
                w(r'\section{参考资料}')
                w('')
                in_bibliography = True
                i += 1
                continue
            flush_bib()
            lvl = {'heading 2': 'section', 'heading 3': 'subsection',
                   'heading 4': 'subsubsection'}.get(sname, 'subsubsection')
            if t.startswith('附件'):
                w(r'\section*{%s}' % esc(t))
                w(r'\addcontentsline{toc}{section}{%s}' % esc(t))
            else:
                w(r'\%s{%s}' % (lvl, esc(htxt0)))
            w('')
            i += 1
            continue
        if in_bibliography and re.match(r'^\[\d+\]', t):
            bib_items.append(esc(re.sub(r'^\[\d+\]\s*', '', t)))
            i += 1
            continue
        if numid == '1' and ilvl == '0':
            flush_bib()
            if pending_list != 'enumerate':
                flush_list()
                w(r'\begin{enumerate}[label=\arabic*., leftmargin=2em, itemsep=0pt]')
                pending_list = 'enumerate'
            w(r'\item %s' % (content.strip() or esc(t)))
            i += 1
            continue
        if numid == '2':
            flush_list()
            flush_bib()
            w(r'\noindent (2)%s' % esc(t))
            w('')
            i += 1
            continue
        flush_list()
        flush_bib()
        if imgs and not t and all(rid in FORMULA_DISPLAY_IMG for rid in imgs):
            for rid in imgs:
                fname, formula = FORMULA_DISPLAY_IMG[rid]
                w(r'%% 原文档此处为公式图片 %s, 已重建为 LaTeX 公式(请对照原文核对)' % fname)
                w(r'\begin{equation*}')
                w(formula)
                w(r'\end{equation*}')
            w('')
            i += 1
            continue
        if jc == 'center':
            w(r'\begin{center}')
            w((content.strip() or esc(t)).strip())
            w(r'\end{center}')
            w('')
        else:
            w((content.strip() or esc(t)).strip())
            w('')
        i += 1
        continue
    if el.tag == W + 'tbl':
        flush_list()
        flush_bib()
        rows = table_rows(el)
        all_imgs = [im for row in rows for cell in row for im in cell['imgs']]
        any_text = any(''.join(cell_plain_lines(c)).strip() for row in rows for c in row)
        any_code = any(looks_like_code(c) for row in rows for c in row)
        if any_code:
            code_lines = []
            for row in rows:
                for cell in row:
                    for tline, cline in cell['paras']:
                        code_lines.append(tline.replace('\xa0', ' '))
            while code_lines and not code_lines[-1].strip():
                code_lines.pop()
            w(r'\begin{lstlisting}[style=pycode]')
            w('\n'.join(code_lines))
            w(r'\end{lstlisting}')
            w('')
        elif all_imgs and any_text:
            nrows = len(rows)
            ncols = len(rows[0]) if rows else 1
            pairs = []
            for ri, row in enumerate(rows):
                for ci, cell in enumerate(row):
                    if cell['imgs']:
                        cap = ''
                        if ri + 1 < nrows and ci < len(rows[ri + 1]):
                            nxt = rows[ri + 1][ci]
                            if not nxt['imgs']:
                                cap = ' '.join(cell_plain_lines(nxt)).strip()
                        pairs.append((cell['imgs'][0], cap))
            if ncols == 2:
                w(r'\begin{figure}[htbp]')
                w(r'\centering')
                for k, (rid, cap) in enumerate(pairs):
                    w(r'\begin{subfigure}[b]{0.48\textwidth}')
                    w(r'\centering')
                    w(r'\includegraphics[width=\textwidth]{%s}' % media_ref(rid))
                    if cap:
                        w(r'\caption{%s}' % esc(cap))
                    w(r'\end{subfigure}')
                    if k < len(pairs) - 1:
                        w(r'\hfill')
                w(r'\end{figure}')
                w('')
            else:
                for rid, cap in pairs:
                    w(r'\begin{figure}[htbp]')
                    w(r'\centering')
                    w(r'\includegraphics[width=0.9\textwidth]{%s}' % media_ref(rid))
                    if cap:
                        w(r'\caption{%s}' % esc(cap))
                    w(r'\end{figure}')
                    w('')
        elif any_text and not all_imgs and not any_code:
            all_lines = [ln for row in rows for c in row for ln in cell_plain_lines(c)]
            lines = [ln.strip() for ln in all_lines if ln.strip()]
            if lines and all(re.search(r'\.py\s*$', ln) for ln in lines):
                w(r'\begin{itemize}[leftmargin=2em, itemsep=0pt]')
                for ln in lines:
                    w(r'\item \texttt{%s}' % esc(ln.strip()))
                w(r'\end{itemize}')
                w('')
            else:
                data = []
                for row in rows:
                    cells_txt = []
                    for cell in row:
                        cells_txt.append(' '.join(cell_plain_lines(cell)).strip())
                    if any(cells_txt):
                        data.append(cells_txt)
                if data:
                    ncols = max(len(r) for r in data)
                    for r in data:
                        while len(r) < ncols:
                            r.append('')
                    colspec = 'l' * ncols
                    w(r'\begin{table}[htbp]')
                    w(r'\centering')
                    w(r'\begin{tabular}{%s}' % colspec)
                    w(r'\toprule')
                    for ri, r in enumerate(data):
                        w(' & '.join(esc(x) for x in r) + r' \\')
                        if ri == 0:
                            w(r'\midrule')
                    w(r'\bottomrule')
                    w(r'\end{tabular}')
                    w(r'\end{table}')
                    w('')
        i += 1
        continue
    i += 1

flush_list()
flush_bib()

# ---- 组装文档 ----
preamble = r'''% !TeX program = xelatex
% !TeX encoding = UTF-8
% ============================================================
%  第二十七届华南大学生物理实验设计大赛 命题类作品研究报告
%  《刻线之间见星河——光栅衍射背后的国之重器》
%  由 213.docx 自动转换生成（编译方式: xelatex）
% ============================================================
\documentclass[12pt,a4paper]{ctexrep}

% ---- 页面设置 (与原 Word 文档页边距一致) ----
\usepackage[top=1in,bottom=1in,left=1.25in,right=1.25in]{geometry}

% ---- 数学与公式 ----
\usepackage{amsmath}
\usepackage{amssymb}

% ---- 图片 / 表格 / 图表标题 ----
\usepackage{graphicx}
\graphicspath{{figures/}}
\usepackage{booktabs}
\usepackage{array}
\usepackage{caption}
\usepackage[font=small]{subcaption}

% ---- 列表 ----
\usepackage{enumitem}

% ---- 代码 ----
\usepackage{xcolor}
\usepackage{listings}
\lstdefinestyle{pycode}{
  language=Python,
  basicstyle=\ttfamily\footnotesize,
  keywordstyle=\color{blue!70!black},
  commentstyle=\color{green!45!black},
  stringstyle=\color{red!60!black},
  showstringspaces=false,
  breaklines=true,
  breakatwhitespace=false,
  columns=fullflexible,
  keepspaces=true,
  frame=single,
  framesep=4pt,
  xleftmargin=4pt,
  xrightmargin=4pt,
  numbers=left,
  numberstyle=\tiny\color{gray},
}
\lstset{style=pycode}

% ---- 下划线(标题页) ----
\usepackage[normalem]{ulem}

% ---- 超链接 ----
\usepackage[hidelinks]{hyperref}

% ---- 中文字体与段落 ----
\setlength{\parindent}{2em}
\usepackage{indentfirst}
\linespread{1.2}

% ---- 等宽字体 ----
% 代码注释/字符串中含希腊字母(λ θ π 等), 默认 Latin Modern Mono 无对应字形,
% 改用 Windows 自带 Consolas(覆盖希腊字母及上下标符号)
\setmonofont{Consolas}

% ---- 正文裸希腊字母 ----
% 正文中直接出现的希腊字母(如 "波长 λ"、"衍射角 θ")由中文字体渲染,
% Latin Modern Roman 无希腊字形
\xeCJKDeclareCharClass{CJK}{"03B1 -> "03C9, "03D1, "03D5, "03D6, "03F0, "03F1}

% ---- 参考资料标题 ----
\renewcommand{\bibname}{参考资料}

\begin{document}
'''

out.insert(0, preamble)
out.append('\\end{document}\n')

tex = '\n'.join(out)
tex = re.sub(r'[ \t]+$', '', tex, flags=re.M)

with open(OUT_TEX, 'w', encoding='utf-8') as f:
    f.write(tex)

# ---- 拷贝图片 ----
os.makedirs(FIG_DIR, exist_ok=True)
copied = 0
for src, name in sorted(used_media):
    dst = os.path.join(FIG_DIR, name)
    ext = os.path.splitext(src)[1].lower()
    try:
        if ext == '.gif':
            from PIL import Image
            im = Image.open(src).convert('RGBA')
            bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
            bg.alpha_composite(im)
            bg.convert('RGB').save(dst)
        elif ext == '.svg':
            warnings.append('SVG 图片 %s 未转换, 需手动处理' % src)
            continue
        else:
            shutil.copyfile(src, dst)
        copied += 1
    except Exception as e:
        warnings.append('拷贝 %s 失败: %s' % (src, e))

print('=== 输出:', OUT_TEX)
print('=== 已拷贝图片 %d 张到 %s' % (copied, FIG_DIR))
for wt in warnings:
    print('WARN:', wt)
print('段落总数:', len(elements), ' tex 行数:', tex.count('\n'))
