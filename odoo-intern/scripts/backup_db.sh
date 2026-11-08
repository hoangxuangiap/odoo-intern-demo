#!/usr/bin/env bash
# Backup DB (có filestore) qua API quản lý DB của Odoo -> file .zip để nộp cho người hướng dẫn.
# Dùng:  ./scripts/backup_db.sh [tên_db] [master_password] [url]
DB="${1:-minhan}"; MASTER="${2:-admin}"; URL="${3:-http://localhost:8069}"
mkdir -p "$(dirname "$0")/../backups"
OUT="$(dirname "$0")/../backups/${DB}_$(date +%Y%m%d_%H%M).zip"
curl -sS -X POST -F "master_pwd=$MASTER" -F "name=$DB" -F "backup_format=zip" "$URL/web/database/backup" -o "$OUT" \
  && echo "Đã backup: $OUT ($(du -h "$OUT" | cut -f1))"
echo "Khôi phục: Odoo › Database Manager (/web/database/manager) › Restore, chọn file zip."
