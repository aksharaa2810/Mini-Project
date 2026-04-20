"""Migration script to normalize data/od_requests.csv to the expected header order.

It will:
- Back up the existing file to data/od_requests.csv.bak
- Read rows and try to map old malformed rows (15 columns) to the correct 12-column format
- Write a new cleaned file with header:
  request_id,student_id,date,start_time,end_time,reason,proof_file,status,submitted_at,approved_by,approved_at,remarks

Run:
    python utils/migrate_od_requests.py
"""
import csv
import shutil
import os

SRC = 'data/od_requests.csv'
BACKUP = 'data/od_requests.csv.bak'
TMP = 'data/od_requests.csv.tmp'

EXPECTED_HEADER = ['request_id','student_id','date','start_time','end_time','reason','proof_file','status','submitted_at','approved_by','approved_at','remarks']

if not os.path.exists(SRC):
    print('No od_requests.csv found; nothing to do.')
    exit(0)

print(f'Backing up {SRC} -> {BACKUP}')
shutil.copy2(SRC, BACKUP)

cleaned = []
with open(SRC, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

# If file is empty or only header, exit
if not rows:
    print('Empty file; nothing to migrate.')
    exit(0)

orig_header = rows[0]
print('Original header:', orig_header)

for i, row in enumerate(rows[1:], start=2):
    if not any(cell.strip() for cell in row):
        # skip empty rows
        continue
    # If row already matches expected columns (12), assume it's correct
    if len(row) == len(EXPECTED_HEADER):
        cleaned.append(row)
        continue
    # Handle known malformed format (15 columns)
    if len(row) >= 15:
        # Old format mapping (indices):
        # 0: request_id,1:student_id,2:student_name,3:class,4:date,5:start_time,6:end_time,
        # 7:od_type,8:reason,9:venue/proof_file?,10:status,11:submitted_at,12:approved_by,13:approved_at,14:remarks
        request_id = row[0]
        student_id = row[1]
        date = row[4]
        start_time = row[5]
        end_time = row[6]
        reason = row[8]
        proof_file = row[9] if row[9] and any(ext in row[9].lower() for ext in ['.pdf', '.jpg', '.png']) else ''
        status = row[10] if row[10] else 'pending'
        submitted_at = row[11]
        approved_by = row[12]
        approved_at = row[13]
        remarks = row[14]
        cleaned.append([request_id, student_id, date, start_time, end_time, reason, proof_file, status, submitted_at, approved_by, approved_at, remarks])
        continue
    # If row has fewer columns but looks like shifted, try best-effort: match by header names if present
    # Fallback: pad/truncate
    new_row = (row + [''] * len(EXPECTED_HEADER))[:len(EXPECTED_HEADER)]
    cleaned.append(new_row)

# Write tmp file
with open(TMP, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(EXPECTED_HEADER)
    writer.writerows(cleaned)

# Replace original
shutil.move(TMP, SRC)
print('Migration complete. Original backed up at', BACKUP)
print('Please verify data/od_requests.csv and restart the app if needed.')
