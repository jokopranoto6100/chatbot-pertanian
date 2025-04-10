import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys
import re
import json
import os

# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not json_str:
    raise Exception("Environment variable GOOGLE_APPLICATION_CREDENTIALS is missing!")

info = json.loads(json_str)
creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(creds)
sheet = client.open("Data Luas Panen").sheet1
data = sheet.get_all_records()

# Fungsi pencarian utama
def cari_luas_panen(bulan=None, kabupaten=None, tahun=None, ringkasan=False, subround=None):
    hasil = []

    # Subround
    subround_map = {
        1: ['januari', 'februari', 'maret', 'april'],
        2: ['mei', 'juni', 'juli', 'agustus'],
        3: ['september', 'oktober', 'november', 'desember']
    }
    if subround and tahun:
        total = 0
        for row in data:
            if row['Tahun'] == tahun and row['Bulan'].lower() in subround_map[subround]:
                total += float(row['Luas Panen'])
        if total == 0:
            return "📛 Data tidak ditemukan."
        return f"📋 Total Luas Panen Kalimantan Barat Subround {subround} Tahun {tahun}:\n🟩 {total:,.2f} hektar"

    # Ringkasan Kalbar (semua kabupaten)
    if ringkasan and kabupaten in ["kalimantan barat", "kalbar"]:
        total = 0
        for row in data:
            if (not bulan or row['Bulan'].lower() == bulan.lower()) and row['Tahun'] == tahun:
                total += float(row['Luas Panen'])
        if total == 0:
            return "📛 Data tidak ditemukan."
        keterangan = f"📋 Ringkasan Luas Panen Kalimantan Barat"
        keterangan += f" Bulan {bulan.capitalize()} {tahun}" if bulan else f" Tahun {tahun}"
        return f"{keterangan}:\n🟩 Total: {total:,.2f} hektar"

    # Ringkasan semua kabupaten (tanpa menyebut nama kabupaten)
    if ringkasan and not bulan and not kabupaten and tahun:
        hasil.append(f"📋 Ringkasan Luas Panen per Kabupaten Tahun {tahun}")
        kabupaten_set = sorted(set([row['Kabupaten'] for row in data]))
        for kab in kabupaten_set:
            total = sum(float(row['Luas Panen']) for row in data if row['Kabupaten'].lower() == kab.lower() and row['Tahun'] == tahun)
            hasil.append(f"▪️ {kab}: {total:,.2f} hektar")
        return "\n".join(hasil)

    # Ringkasan kabupaten tertentu
    if ringkasan and kabupaten and not bulan and tahun:
        total = sum(float(row['Luas Panen']) for row in data if row['Kabupaten'].lower() == kabupaten.lower() and row['Tahun'] == tahun)
        if total == 0:
            return "📛 Data tidak ditemukan."
        return f"📋 Total Luas Panen {kabupaten.title()} Tahun {tahun}: {total:,.2f} hektar"

    # ⛳ Permintaan kabupaten + tahun tanpa "ringkasan" → tetap kita jumlahkan
    if kabupaten and not bulan and tahun:
        total = sum(float(row['Luas Panen']) for row in data if row['Kabupaten'].lower() == kabupaten.lower() and row['Tahun'] == tahun)
        if total == 0:
            return "📛 Data tidak ditemukan."
        return f"📋 Total Luas Panen {kabupaten.title()} Tahun {tahun}: {total:,.2f} hektar"

    # Cek data per bulan-kabupaten-tahun
    for row in data:
        if row['Bulan'].lower() == bulan.lower() and row['Kabupaten'].lower() == kabupaten.lower() and row['Tahun'] == tahun:
            return f"📍 Luas Panen {kabupaten.title()} Bulan {bulan.title()} {tahun}: {row['Luas Panen']:,.2f} hektar"

    return "📛 Data tidak ditemukan."

# Parsing input
query = " ".join(sys.argv[1:]).lower()
bulan_list = [
    'januari', 'februari', 'maret', 'april', 'mei', 'juni',
    'juli', 'agustus', 'september', 'oktober', 'november', 'desember'
]

bulan = next((b for b in bulan_list if b in query), None)
kabupaten = next((row['Kabupaten'].lower() for row in data if row['Kabupaten'].lower() in query), None)
tahun_match = re.search(r'20\d{2}', query)
tahun = int(tahun_match.group()) if tahun_match else None
ringkasan = any(kata in query for kata in ['ringkasan', 'semua kabupaten', 'total', 'rekap'])

# Tangkap "kalbar" sebagai ringkasan Kalimantan Barat
if not ringkasan and ("kalbar" in query or "kalimantan barat" in query) and tahun:
    kabupaten = "kalimantan barat"
    ringkasan = True

# Subround
subround = None
if "subround 1" in query:
    subround = 1
elif "subround 2" in query:
    subround = 2
elif "subround 3" in query:
    subround = 3

# Eksekusi dan kirim hasil
hasil = cari_luas_panen(bulan, kabupaten, tahun, ringkasan, subround)
sys.stdout.buffer.write(hasil.encode('utf-8'))
