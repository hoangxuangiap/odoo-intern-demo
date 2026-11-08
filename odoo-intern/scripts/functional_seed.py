# Chạy bên trong `odoo shell`:  echo "exec(open('scripts/functional_seed.py').read())" | odoo-bin shell -d minhan ...
# Biến `env` do odoo shell cung cấp.
import os
scope = [s for s in os.environ.get('FUNC_SCOPE', '').split(',') if s] or None
report = env['intern.functional.setup'].run(scope=scope, commit=True, report_dir=os.environ.get('REPORT_DIR'))
env.cr.commit()
print(report)
