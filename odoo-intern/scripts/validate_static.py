#!/usr/bin/env python3
"""Kiểm tra tĩnh (không cần Odoo): cú pháp Python/XML, file trong manifest tồn tại, tên model trong CSV."""
import ast, csv, os, re, sys
import xml.dom.minidom as minidom

ROOT = os.path.join(os.path.dirname(__file__), '..', 'addons')
errors = []
for mod in sorted(os.listdir(ROOT)):
    base = os.path.join(ROOT, mod)
    if not os.path.isdir(base):
        continue
    manifest_path = os.path.join(base, '__manifest__.py')
    if not os.path.exists(manifest_path):
        errors.append(f'{mod}: thiếu __manifest__.py'); continue
    manifest = ast.literal_eval(open(manifest_path).read())
    for key in ('data', 'demo'):
        for rel in manifest.get(key, []):
            if not os.path.exists(os.path.join(base, rel)):
                errors.append(f'{mod}: file khai báo không tồn tại: {rel}')
    models = set()
    for dp, _, files in os.walk(base):
        for f in files:
            path = os.path.join(dp, f)
            if f.endswith('.py'):
                try:
                    tree = ast.parse(open(path, encoding='utf-8').read())
                except SyntaxError as e:
                    errors.append(f'{path}: {e}'); continue
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for st in node.body:
                            if isinstance(st, ast.Assign) and getattr(st.targets[0], 'id', '') == '_name':
                                models.add(st.value.value)
            elif f.endswith('.xml'):
                try:
                    minidom.parse(path)
                except Exception as e:
                    errors.append(f'{path}: {e}')
    acl = os.path.join(base, 'security', 'ir.model.access.csv')
    if os.path.exists(acl):
        for row in csv.DictReader(open(acl, encoding='utf-8')):
            ref = row['model_id:id']
            if ref.startswith('model_'):
                name = ref[6:]
                if not any(m.replace('.', '_') == name for m in models):
                    errors.append(f'{mod}: ACL tham chiếu model không có trong module: {ref}')
    # menu parents / depends sanity
    for dep in manifest.get('depends', []):
        pass
print('Modules:', len([m for m in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, m))]))
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('OK: cú pháp, manifest, ACL hợp lệ')
