from flask import Flask, render_template_string
import sqlite3, requests, os
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)
DB_PATH = "/data/prices.db"

def init_db():
    os.makedirs("/data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price TEXT,
            url TEXT,
            scraped_at TEXT
        )
    """)
    conn.commit()
    conn.close()

COMPONENTS = [
    {"name": "Ryzen 9 9950X3D", "url": "https://mdcomputers.in/product/amd-ryzen-9-9950x3d-100-100000719wof-desktop-processor/"},
    {"name": "Ryzen 9 9950X", "url": "https://mdcomputers.in/product/amd-ryzen-9-9950x-100-100001277wof-desktop-processor/"},
    {"name": "Ryzen 7 9800X3D", "url": "https://mdcomputers.in/product/amd-ryzen-7-9800x3d-100-1000001084wof-desktop-processor/"},
    {"name": "Ryzen 9 9900X", "url": "https://mdcomputers.in/product/amd-ryzen-9-9900x-100-100000662wof-desktop-processor/"},
    {"name": "Ryzen 9 7900X", "url": "https://mdcomputers.in/product/amd-ryzen-9-7900x-100-100000589wof-desktop-processor/"},
    {"name": "Ryzen 7 9700X", "url": "https://mdcomputers.in/product/amd-ryzen-7-9700x-100-100001404wof-desktop-processor/"},
    {"name": "Ryzen 7 7700X", "url": "https://mdcomputers.in/product/amd-ryzen-7-7700x-100-100000591wof-desktop-processor/"},
    {"name": "Ryzen 5 9600X", "url": "https://mdcomputers.in/product/amd-ryzen-5-9600x-100-100001405wof-desktop-processor/"},
    {"name": "Ryzen 5 7600X", "url": "https://mdcomputers.in/product/amd-ryzen-5-7600x-100-100000593wof-desktop-processor/"},
    {"name": "Ryzen 5 7600", "url": "https://mdcomputers.in/product/amd-ryzen-5-7600-100-100001015box-desktop-processor/"},
    {"name": "Ryzen 5 7500F", "url": "https://mdcomputers.in/product/amd-ryzen-5-7500f-100-100000597box-desktop-processor/"},
    {"name": "Asus Dual RX 9060 XT 16GB", "url": "https://mdcomputers.in/product/asus-dual-graphics-card-rx9060xt-16g/"},
    {"name": "ASRock RX 9070 Challenger 16GB", "url": "https://mdcomputers.in/product/asrock-challenger-graphics-card-rx9070-cl-16g/"},
    {"name": "MSI RTX 5060 Ti Ventus 16GB", "url": "https://mdcomputers.in/product/graphics-card/msi-rtx-5060-ti-ventus-2x-oc-graphics-card-g506t-16v2cp"},
    {"name": "INNO3D RTX 5070 Twin X2 OC 12GB", "url": "https://mdcomputers.in/product/graphics-card/inno3d-rtx5070-twin-x2-oc-graphics-card-n50702-12d7x-195064n"},
    {"name": "Asrock RX 9070 XT Challenger 16GB", "url": "https://mdcomputers.in/product/asrock-challenger-graphics-card-rx9070xt-cl-16g/"},
    {"name": "MSI RTX 5070 Ti Shadow 3X OC 16GB", "url": "https://mdcomputers.in/product/graphics-card/msi-rtx-5070-shadow-3x-oc-graphics-card-g507t-16s3c"},
    {"name": "G.Skill Ripjaws S5 16GB 5200MHz DDR5", "url": "https://mdcomputers.in/product/g-skill-ram-ripjaws-s5-16gb-ddr5-f5-5200j4040a16gx1-rs5k/"},
    {"name": "Crucial Pro 16GB 5600MHz DDR5", "url": "https://mdcomputers.in/product/crucial-ram-pro-cp16g56c46u5/"},
    {"name": "Crucial Pro 16GB 6000MHz DDR5", "url": "https://mdcomputers.in/product/crucial-ram-pro-16gb-ddr5-cp16g60c48u5/"},
    {"name": "Crucial E100 480GB NVMe Gen4 SSD", "url": "https://mdcomputers.in/product/crucial-e100-480gb-nvme-ssd-ct480e100ssd8/"},
    {"name": "WD Green SN350 500GB NVMe Gen3 SSD", "url": "https://mdcomputers.in/product/storage/ssd-drive/wd-green-sn350-500gb-nvme-ssd-wds500g2g0c"},
    {"name": "ADATA Legend 860 1000GB NVMe Gen4 SSD", "url": "https://mdcomputers.in/product/adata-legend-860-1000gb-nvme-ssd-sleg-860-1000gcs/"},
    {"name": "Kingston KC3000 512GB NVMe Gen4 SSD", "url": "https://mdcomputers.in/product/kingston-kc3000-512gb-nvme-ssd-skc3000s-512g/"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
}

def scrape_prices():
    conn = sqlite3.connect(DB_PATH)
    for item in COMPONENTS:
        try:
            res = requests.get(item["url"], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            price_el = (
                soup.select_one(".price-new") or
                soup.select_one(".special-price") or
                soup.select_one(".price")
            )
            price = price_el.get_text(strip=True) if price_el else "N/A"
            conn.execute(
                "INSERT INTO prices (name, price, url, scraped_at) VALUES (?, ?, ?, ?)",
                (item["name"], price, item["url"], datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
        except Exception as e:
            conn.execute(
                "INSERT INTO prices (name, price, url, scraped_at) VALUES (?, ?, ?, ?)",
                (item["name"], f"Error: {e}", item["url"], datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
    conn.commit()
    conn.close()

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>PC Price Tracker</title>
  <style>
    body { background:#0d1117; color:#e8e8e8; font-family:monospace; padding:32px; }
    h1 { color:#58a6ff; margin-bottom:4px; }
    .sub { color:#666; font-size:0.8rem; margin-bottom:32px; }
    table { width:100%; border-collapse:collapse; max-width:1100px; }
    th { text-align:left; padding:10px 12px; background:#161b22;
         color:#8b949e; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; }
    td { padding:10px 12px; border-bottom:1px solid #21262d; font-size:0.88rem; }
    tr:hover td { background:#161b22; }
    .price { color:#3fb950; font-weight:bold; }
    .time { color:#555; font-size:0.75rem; }
    a { color:#58a6ff; text-decoration:none; font-size:0.8rem; }
    .scrape-btn { background:#238636; color:#fff; border:none; padding:10px 20px;
                  border-radius:6px; cursor:pointer; font-family:monospace;
                  font-size:0.85rem; margin-bottom:24px; }
    .scrape-btn:hover { background:#2ea043; }
  </style>
</head>
<body>
  <h1>PC Parts Price Tracker</h1>
  <div class="sub">Scrapes mdcomputers.in — updates every 6 hours via cron</div>
  <form action="/scrape" method="post">
    <button class="scrape-btn" type="submit">scrape now</button>
  </form>
  <table>
    <thead>
      <tr><th>Component</th><th>Price</th><th>Link</th><th>Checked</th></tr>
    </thead>
    <tbody>
      {% for row in rows %}
      <tr>
        <td>{{ row[1] }}</td>
        <td class="price">{{ row[2] }}</td>
        <td><a href="{{ row[3] }}" target="_blank">view →</a></td>
        <td class="time">{{ row[4] }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>
"""

@app.route("/")
def index():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT * FROM prices ORDER BY scraped_at DESC LIMIT 100"
    ).fetchall()
    conn.close()
    return render_template_string(TEMPLATE, rows=rows)

@app.route("/scrape", methods=["POST"])
def manual_scrape():
    scrape_prices()
    return '<meta http-equiv="refresh" content="0; url=/">'

if __name__ == "__main__":
    init_db()
    scrape_prices()
    app.run(host="0.0.0.0", port=5000)
