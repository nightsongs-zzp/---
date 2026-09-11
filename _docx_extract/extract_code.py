# -*- coding: utf-8 -*-
"""从 213.docx 代码表格提取 8 个 .py 文件。
Word 2 列表格: 代码沿左列向下流动、继续到右列顶部(报纸式分栏),
故正确顺序 = 列优先(先取完左列所有行, 再取右列)。
"""
import os
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, '..', '代码附件')
os.makedirs(OUTDIR, exist_ok=True)

z = zipfile.ZipFile('../213.docx')
root = ET.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')
tables = body.findall(W + 'tbl')


def cell_paras(cell):
    """单元格 -> 段落文本列表(每段一行, 保留缩进, 归一化空白)"""
    out = []
    for p in cell.iter(W + 'p'):
        txt = ''.join(t.text or '' for t in p.iter(W + 't'))
        txt = txt.replace(' ', ' ').replace('　', ' ').rstrip()
        if txt.strip() or True:
            out.append(txt)
    return out


def join_col_major(rows):
    ncols = max(len(r.findall(W + 'tc')) for r in rows)
    cols = [[] for _ in range(ncols)]
    for r in rows:
        for ci, tc in enumerate(r.findall(W + 'tc')):
            cols[ci].extend(cell_paras(tc))
    return '\n'.join('\n'.join(c) for c in cols)


def join_row_major(rows):
    out = []
    for r in rows:
        for tc in r.findall(W + 'tc'):
            out.extend(cell_paras(tc))
    return '\n'.join(out)


# 文件名表: 单元格段落均为 .py 文件名
file_groups = []
for ti, tbl in enumerate(tables):
    rows = tbl.findall(W + 'tr')
    names = []
    for r in rows:
        for tc in r.findall(W + 'tc'):
            for para in cell_paras(tc):
                para = para.strip()
                if para.endswith('.py') and ' ' not in para and len(para) < 60:
                    names.append(para)
    if names:
        file_groups.append((ti, names))
print('文件名表:', file_groups)

# 代码表: 第一个单元格以 import/from/def 开头
code_tables = []
for ti, tbl in enumerate(tables):
    if ti in [g[0] for g in file_groups]:
        continue
    rows = tbl.findall(W + 'tr')
    first = cell_paras(rows[0].findall(W + 'tc')[0]) if rows and rows[0].findall(W + 'tc') else []
    head = (first[0] if first else '') + (first[1] if len(first) > 1 else '')
    if head.strip().startswith(('import ', 'from ', 'def ', '#')) or 'import ' in head[:40]:
        code_tables.append((ti, rows))
print('代码表:', [(ti, len(rows)) for ti, rows in code_tables])

# 导出
all_names = [n for _, names in file_groups for n in names]
assert len(all_names) == len(code_tables), (len(all_names), len(code_tables))
for idx, ((ti, rows), name) in enumerate(zip(code_tables, all_names)):
    code = join_row_major(rows)
    # 行尾去空白、去掉行内多个空格挤出的分隔标记
    lines = []
    for ln in code.split('\n'):
        lines.append(ln.rstrip())
    text = '\n'.join(lines).rstrip() + '\n'
    path = os.path.join(OUTDIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('导出 %-28s %4d 行 -> %s' % (name, len(lines), path))
print('OK')
