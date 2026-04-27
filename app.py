import streamlit as st
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Toko Buah ABS",
    page_icon="🍉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GOOGLE SHEETS SETUP ───────────────────────────────────────────────────────
SHEET_ID = st.secrets.get("SHEET_ID", "")          # isi di secrets.toml
SHEET_NAME_ORDERS = "orders"
SHEET_NAME_STATS  = "stats"

@st.cache_resource
def get_sheet_client():
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception:
        return None

def save_order_to_sheet(order_data: dict):
    client = get_sheet_client()
    if not client or not SHEET_ID:
        return False
    try:
        sh = client.open_by_key(SHEET_ID)
        try:
            ws = sh.worksheet(SHEET_NAME_ORDERS)
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet(SHEET_NAME_ORDERS, rows=1000, cols=15)
            ws.append_row(["Tanggal","Waktu","Nama","WhatsApp","Alamat",
                           "Item","Total (Rp)","Status"])
        row = [
            order_data["tanggal"], order_data["waktu"],
            order_data["nama"], order_data["whatsapp"],
            order_data["alamat"], order_data["items"],
            order_data["total"], "Baru"
        ]
        ws.append_row(row)
        return True
    except Exception:
        return False

# ─── CATALOGUE ────────────────────────────────────────────────────────────────
BUAH = {
    "🍊 Jeruk Navel":       {"harga": 18000, "satuan": "kg", "emoji": "🍊"},
    "🍋 Jeruk Kecil":       {"harga": 12000, "satuan": "kg", "emoji": "🍋"},
    "🥭 Mangga Harum Manis":{"harga": 22000, "satuan": "kg", "emoji": "🥭"},
    "🐉 Buah Naga":         {"harga": 20000, "satuan": "kg", "emoji": "🐉"},
    "🍌 Pisang Cavendish":  {"harga": 15000, "satuan": "kg", "emoji": "🍌"},
    "⭐ Belimbing":         {"harga": 14000, "satuan": "kg", "emoji": "⭐"},
    "🍈 Salak Pondoh":      {"harga": 16000, "satuan": "kg", "emoji": "🍈"},
    "🍏 Apel Hijau":        {"harga": 25000, "satuan": "kg", "emoji": "🍏"},
    "🍎 Apel Merah":        {"harga": 28000, "satuan": "kg", "emoji": "🍎"},
    "🍈 Melon":             {"harga": 12000, "satuan": "kg", "emoji": "🍈"},
    "🍍 Nanas":             {"harga": 10000, "satuan": "buah","emoji": "🍍"},
    "🍇 Anggur Merah":      {"harga": 45000, "satuan": "kg", "emoji": "🍇"},
    "🫐 Kelengkeng":        {"harga": 30000, "satuan": "kg", "emoji": "🫐"},
}

PARCEL = {
    "Parcel Kecil (3 buah)": {
        "harga": 85000,
        "isi": ["🍊 Jeruk Navel (0.5 kg)", "🥭 Mangga Harum Manis (0.5 kg)", "🍌 Pisang Cavendish (0.5 kg)"],
        "deskripsi": "Cocok untuk hadiah simpel & personal",
        "emoji": "🎁",
    },
    "Parcel Sedang (5 buah)": {
        "harga": 150000,
        "isi": ["🍊 Jeruk Navel (1 kg)", "🥭 Mangga Harum Manis (1 kg)", "🍌 Pisang Cavendish (1 kg)",
                "🍎 Apel Merah (0.5 kg)", "🍇 Anggur Merah (0.5 kg)"],
        "deskripsi": "Pilihan terbaik untuk acara keluarga",
        "emoji": "🎀",
    },
    "Parcel Besar (8 buah)": {
        "harga": 275000,
        "isi": ["🍊 Jeruk Navel (1 kg)", "🥭 Mangga Harum Manis (1 kg)", "🍌 Pisang Cavendish (1 kg)",
                "🍎 Apel Merah (1 kg)", "🍇 Anggur Merah (1 kg)", "🐉 Buah Naga (1 kg)",
                "🫐 Kelengkeng (0.5 kg)", "🍈 Melon (1 buah)"],
        "deskripsi": "Istimewa untuk momen spesial & lebaran",
        "emoji": "🎊",
    },
    "Parcel Premium Impor": {
        "harga": 450000,
        "isi": ["🍎 Apel Merah Impor (1 kg)", "🍏 Apel Hijau Impor (1 kg)", "🍇 Anggur Merah (1 kg)",
                "🫐 Kelengkeng Impor (1 kg)", "🥭 Mangga Harum Manis (1 kg)",
                "🍍 Nanas (1 buah)", "🐉 Buah Naga (1 kg)", "🍊 Jeruk Navel (1 kg)"],
        "deskripsi": "Koleksi buah pilihan lokal & impor terbaik",
        "emoji": "👑",
    },
}

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #1a6b1f 0%, #2e9e36 50%, #f7c948 100%);
    padding: 2.5rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 2rem;
    color: white;
    box-shadow: 0 8px 32px rgba(30,120,40,0.25);
}
.hero h1 { font-size: 2.8rem; font-weight: 700; margin: 0; text-shadow: 1px 2px 6px #0005; }
.hero p  { font-size: 1.1rem; margin: 0.4rem 0 0; opacity: 0.92; }

/* Info bar */
.info-bar {
    background: #fff8e1;
    border-left: 5px solid #f7c948;
    padding: 0.8rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    font-size: 0.9rem;
    color: #555;
}

/* Section titles */
.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1a6b1f;
    border-bottom: 3px solid #f7c948;
    padding-bottom: 0.3rem;
    margin: 1.5rem 0 1rem;
}

/* Product card */
.prod-card {
    background: white;
    border-radius: 16px;
    padding: 1.2rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #e8f5e9;
    text-align: center;
    transition: transform 0.2s;
    height: 100%;
}
.prod-card:hover { transform: translateY(-4px); }
.prod-emoji { font-size: 3rem; }
.prod-name  { font-weight: 600; color: #333; margin: 0.3rem 0; font-size: 0.95rem; }
.prod-price { color: #2e9e36; font-weight: 700; font-size: 1rem; }

/* Parcel card */
.parcel-card {
    background: linear-gradient(135deg, #fff8e1, #fffde7);
    border: 2px solid #f7c948;
    border-radius: 16px;
    padding: 1.4rem;
    box-shadow: 0 4px 18px rgba(247,201,72,0.2);
}

/* Cart badge */
.cart-count {
    background: #e53935;
    color: white;
    border-radius: 50%;
    padding: 0.15rem 0.5rem;
    font-size: 0.85rem;
    font-weight: 700;
}

/* Checkout button */
.stButton > button {
    background: linear-gradient(135deg, #2e9e36, #1a6b1f) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "cart" not in st.session_state:
    st.session_state.cart = {}   # {"nama_produk": {"qty": int, "harga": int}}
if "page" not in st.session_state:
    st.session_state.page = "home"

# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div style="font-size:3.5rem">🍉</div>
  <h1>Toko Buah ABS</h1>
  <p>Menjual Aneka Buah Lokal & Impor Segar Pilihan</p>
  <p style="font-size:0.85rem; opacity:0.8">📍 Jl. Mandala Raya RT.02/RW.02, Ciparigi, Bogor Utara &nbsp;|&nbsp; ☎️ 087875957722 &nbsp;|&nbsp; 🕗 08.00–21.30 Setiap Hari</p>
</div>
""", unsafe_allow_html=True)

# ─── NAVIGATION ───────────────────────────────────────────────────────────────
total_item = sum(v["qty"] for v in st.session_state.cart.values())
nav_cols = st.columns([1,1,1,1,1])
with nav_cols[0]:
    if st.button("🏠 Beranda"):
        st.session_state.page = "home"
with nav_cols[1]:
    if st.button("🛒 Keranjang" + (f" ({total_item})" if total_item else "")):
        st.session_state.page = "cart"
with nav_cols[2]:
    if st.button("🎁 Parcel"):
        st.session_state.page = "parcel"
with nav_cols[3]:
    if st.button("📍 Lokasi"):
        st.session_state.page = "lokasi"
with nav_cols[4]:
    if st.button("💬 Kritik & Saran"):
        st.session_state.page = "saran"

st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "home":
    st.markdown('<div class="section-title">🍓 Pilih Buah Segar</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-bar">✅ Semua buah dipilih langsung dari petani terbaik · Diantar ke rumah Anda · Bayar saat barang tiba</div>', unsafe_allow_html=True)

    buah_list = list(BUAH.items())
    for row_start in range(0, len(buah_list), 4):
        cols = st.columns(4, gap="medium")
        for i, (nama, info) in enumerate(buah_list[row_start:row_start+4]):
            with cols[i]:
                st.markdown(f"""
                <div class="prod-card">
                  <div class="prod-emoji">{info['emoji']}</div>
                  <div class="prod-name">{nama.split(' ',1)[1]}</div>
                  <div class="prod-price">Rp {info['harga']:,}/{info['satuan']}</div>
                </div>
                """, unsafe_allow_html=True)
                qty_key = f"qty_{nama}"
                qty = st.number_input("Qty", min_value=0, max_value=50, value=0,
                                      key=qty_key, label_visibility="collapsed")
                if qty > 0:
                    st.session_state.cart[nama] = {"qty": qty, "harga": info["harga"],
                                                    "satuan": info["satuan"]}
                elif nama in st.session_state.cart:
                    del st.session_state.cart[nama]
        st.write("")

    if st.session_state.cart:
        total = sum(v["qty"]*v["harga"] for v in st.session_state.cart.values())
        st.success(f"🛒 {total_item} item dipilih · Total sementara: **Rp {total:,}**")
        if st.button("➡️ Lanjut ke Keranjang", use_container_width=True):
            st.session_state.page = "cart"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PARCEL
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "parcel":
    st.markdown('<div class="section-title">🎁 Pilih Paket Parcel</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-bar">🎀 Parcel dikemas cantik & bisa tambahkan kartu ucapan. Hubungi kami via WhatsApp untuk kustomisasi.</div>', unsafe_allow_html=True)

    for nama_parcel, info in PARCEL.items():
        with st.container():
            st.markdown(f"""
            <div class="parcel-card">
              <h3>{info['emoji']} {nama_parcel}</h3>
              <p style="color:#888; font-size:0.9rem">{info['deskripsi']}</p>
              <p><strong style="color:#2e9e36; font-size:1.2rem">Rp {info['harga']:,}</strong></p>
              <p style="font-size:0.85rem; color:#555"><strong>Isi paket:</strong><br>{"  ·  ".join(info['isi'])}</p>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns([1, 4])
            with c1:
                qty = st.number_input("Qty", min_value=0, max_value=10, value=0,
                                      key=f"parcel_{nama_parcel}", label_visibility="collapsed")
            with c2:
                st.write("")
            if qty > 0:
                st.session_state.cart[f"[Parcel] {nama_parcel}"] = {
                    "qty": qty, "harga": info["harga"], "satuan": "paket"
                }
            elif f"[Parcel] {nama_parcel}" in st.session_state.cart:
                del st.session_state.cart[f"[Parcel] {nama_parcel}"]
            st.write("")

    if any(k.startswith("[Parcel]") for k in st.session_state.cart):
        if st.button("➡️ Lanjut ke Keranjang", use_container_width=True):
            st.session_state.page = "cart"
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CART & CHECKOUT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "cart":
    st.markdown('<div class="section-title">🛒 Keranjang Belanja</div>', unsafe_allow_html=True)

    if not st.session_state.cart:
        st.info("Keranjang masih kosong. Yuk pilih buah dulu! 🍊")
        if st.button("← Kembali Belanja"):
            st.session_state.page = "home"
            st.rerun()
    else:
        total = 0
        for nama, info in list(st.session_state.cart.items()):
            subtotal = info["qty"] * info["harga"]
            total += subtotal
            c1, c2, c3 = st.columns([3,1,1])
            with c1: st.write(f"**{nama}**")
            with c2: st.write(f"{info['qty']} {info['satuan']}")
            with c3: st.write(f"Rp {subtotal:,}")

        st.divider()
        st.markdown(f"### Total Pembayaran: **Rp {total:,}**")
        st.info("🚚 Ongkos kirim akan dikonfirmasi setelah pesanan diterima · Bayar saat barang tiba (COD) atau transfer")

        st.markdown('<div class="section-title">📋 Data Pengiriman</div>', unsafe_allow_html=True)
        nama   = st.text_input("Nama Lengkap *")
        wa     = st.text_input("Nomor WhatsApp *", placeholder="08xxxxxxxxxx")
        alamat = st.text_area("Alamat Lengkap *", placeholder="Nama jalan, RT/RW, Kelurahan, Kecamatan")
        catatan = st.text_area("Catatan Tambahan (opsional)")

        if st.button("✅ Konfirmasi Pesanan", use_container_width=True):
            if not nama or not wa or not alamat:
                st.error("Mohon lengkapi semua data yang wajib diisi (*)")
            else:
                now = datetime.datetime.now()
                items_str = "; ".join([f"{n} x{v['qty']}" for n, v in st.session_state.cart.items()])
                order = {
                    "tanggal": now.strftime("%Y-%m-%d"),
                    "waktu":   now.strftime("%H:%M"),
                    "nama": nama, "whatsapp": wa, "alamat": alamat,
                    "items": items_str, "total": total,
                }
                saved = save_order_to_sheet(order)
                # Juga kirim via WhatsApp
                wa_clean = wa.replace("0","62",1) if wa.startswith("0") else wa
                wa_msg = (f"Halo Toko Buah ABS! Saya ingin memesan:%0A"
                          f"Nama: {nama}%0A"
                          f"Alamat: {alamat}%0A"
                          f"Pesanan: {items_str}%0A"
                          f"Total: Rp {total:,}%0A"
                          f"Catatan: {catatan}")
                wa_link = f"https://wa.me/6287875957722?text={wa_msg}"

                st.success("🎉 Pesanan berhasil dikirim! Kami akan segera menghubungi Anda.")
                if saved:
                    st.info("📊 Pesanan tercatat di sistem toko.")
                st.markdown(f"[📱 Konfirmasi via WhatsApp juga]({wa_link})", unsafe_allow_html=False)
                st.session_state.cart = {}

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LOKASI
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "lokasi":
    st.markdown('<div class="section-title">📍 Lokasi Toko</div>', unsafe_allow_html=True)
    st.markdown("""
    **Toko Buah ABS**  
    Jl. Mandala Raya, RT.02/RW.02, Ciparigi, Kec. Bogor Utara, Kota Bogor, Jawa Barat 16157  
    📞 087875957722  
    🕗 Buka setiap hari pukul 08.00–21.30
    """)
    maps_url = "https://www.google.com/maps?q=Jl.+Mandala+Raya+RT.02+RW.02+Ciparigi+Bogor+Utara+Bogor"
    st.markdown(f'[🗺️ Buka di Google Maps]({maps_url})')
    st.map(pd.DataFrame({"lat": [-6.5427], "lon": [106.8027]}), zoom=15)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: KRITIK & SARAN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "saran":
    st.markdown('<div class="section-title">💬 Kritik & Saran</div>', unsafe_allow_html=True)
    st.write("Pendapat Anda sangat berharga bagi kami untuk terus berkembang!")
    nama_s  = st.text_input("Nama (opsional)")
    rating  = st.slider("Rating Kepuasan", 1, 5, 5, format="%d ⭐")
    pesan   = st.text_area("Pesan / Saran Anda *")
    if st.button("Kirim Saran"):
        if not pesan:
            st.error("Pesan tidak boleh kosong.")
        else:
            client = get_sheet_client()
            if client and SHEET_ID:
                try:
                    sh = client.open_by_key(SHEET_ID)
                    try:
                        ws = sh.worksheet("saran")
                    except gspread.WorksheetNotFound:
                        ws = sh.add_worksheet("saran", rows=500, cols=5)
                        ws.append_row(["Tanggal","Nama","Rating","Pesan"])
                    ws.append_row([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                                   nama_s or "Anonim", rating, pesan])
                except Exception:
                    pass
            st.success("Terima kasih atas masukan Anda! 🙏")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.8rem">
  🍉 <strong>Toko Buah ABS</strong> · Jl. Mandala Raya, Bogor Utara · ☎️ 087875957722<br>
  Menjual Aneka Buah Lokal & Impor · Buka 08.00–21.30 Setiap Hari
</div>
""", unsafe_allow_html=True)
