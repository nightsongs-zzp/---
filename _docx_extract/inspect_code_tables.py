# -*- coding: utf-8 -*-
"""检查 213.docx 中的代码表格: 判断代码按'列优先'还是'行优先'拼接才是原始顺序"""
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
z = zipfile.ZipFile('../213.docx')
root = ET.fromstring(z.read('word/document.xml'))
body = root.find(W + 'body')
tables = body.findall(W + 'tbl')
out = []
out.append('表格总数: %d' % len(tables))

KEYS = ['MidpointArrow', 'danfenyanshe', 'def ', 'import ']


def cell_lines(cell):
    txt = ''.join(t.text or '' for t in cell.iter(W + 't'))
    txt = txt.replace(' ', ' ').replace('', '')
    return txt.split('\n')


for ti, tbl in enumerate(tables):
    rows = tbl.findall(W + 'tr')
    if not rows:
        continue
    first_cells = rows[0].findall(W + 'tc')
    if not first_cells:
        continue
    sample = ''.join(t.text or '' for t in first_cells[0].iter(W + 't'))[:100]
    if not any(k in sample for k in KEYS):
        continue
    ncols = len(first_cells)
    out.append('--- 表格#%d: %d行 x %d列, 首个单元格样本: %r' % (ti, len(rows), ncols, sample[:60]))
    for ri, row in enumerate(rows[:6]):
        cells = row.findall(W + 'tc')
        for ci, cell in enumerate(cells[:ncols]):
            lines = cell_lines(cell)
            head = lines[0][:36] if lines and lines[0].strip() else '(空)'
            tail = lines[-1][:36] if lines and lines[-1].strip() else '(空)'
            out.append('  r%02dc%d [%2d行] 首:%r 尾:%r' % (ri, ci, len(lines), head, tail))
    out.append('')

with open('code_tables_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('done, lines:', len(out))
