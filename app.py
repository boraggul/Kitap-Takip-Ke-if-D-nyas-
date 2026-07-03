from flask import Flask, render_template, request, redirect, url_for
import json
import os
import requests
import random

app = Flask(__name__)

class KitapYonetici:
    def __init__(self, dosya_adi="kitaplar.json"):
        self.dosya_adi = dosya_adi
        # Veritabanı yapısını genişletiyoruz: hem kitaplar listesi hem de özel not alanı
        self.veri = self._verileri_yukle()

    def _verileri_yukle(self):
        varsayilan = {"kitaplar": [], "gunun_notu": ""}
        if not os.path.exists(self.dosya_adi):
            return varsayilan
        try:
            with open(self.dosya_adi, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "kitaplar" not in data:
                    data = {"kitaplar": data, "gunun_notu": ""}
                return data
        except (json.JSONDecodeError, IOError):
            return varsayilan

    def _verileri_kaydet(self):
        try:
            with open(self.dosya_adi, "w", encoding="utf-8") as f:
                json.dump(self.veri, f, ensure_ascii=False, indent=4)
        except IOError:
            print("[Hata] Dosya yazılamadı.")

    @property
    def kitaplar(self):
        return self.veri["kitaplar"]

    def kitap_ekle(self, baslik, yazar, kategori):
        yeni_kitap = {
            "baslik": baslik,
            "yazar": yazar,
            "kategori": kategori if kategori else "Genel",
            "okundu": False
        }
        self.veri["kitaplar"].append(yeni_kitap)
        self._verileri_kaydet()

    def durum_degistir(self, index):
        if 0 <= index < len(self.kitaplar):
            self.kitaplar[index]["okundu"] = not self.kitaplar[index]["okundu"]
            self._verileri_kaydet()

    def kitap_sil(self, index):
        if 0 <= index < len(self.kitaplar):
            self.veri["kitaplar"].pop(index)
            self._verileri_kaydet()

    def not_guncelle(self, yeni_not):
        self.veri["gunun_notu"] = yeni_not
        self._verileri_kaydet()

yonetici = KitapYonetici()

def open_library_kitap_ara(sorgu, max_sonuc=5):
    if not sorgu:
        return []
    if "subject:" in sorgu:
        sorgu = sorgu.replace("subject:", "")

    api_url = f"https://openlibrary.org/search.json?q={requests.utils.quote(sorgu)}&limit={max_sonuc}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    kitaplar = []
    try:
        response = requests.get(api_url, headers=headers, timeout=8)
        if response.status_code == 200:
            data = response.json()
            if "docs" in data and data["docs"]:
                for doc in data["docs"][:max_sonuc]:
                    baslik = doc.get("title", "Bilinmeyen Kitap")
                    yazarlar = doc.get("author_name", ["Bilinmeyen Yazar"])
                    kategoriler = doc.get("subject", ["Genel"])
                    kategori = kategoriler[0] if kategoriler else "Genel"
                    yıl = doc.get("first_publish_year", "Bilinmiyor")
                    acıklama = f"İlk yayınlanma yılı: {yıl}."

                    kitaplar.append({
                        "baslik": baslik,
                        "yazar": ", ".join(yazarlar),
                        "kategori": kategori,
                        "acıklama": acıklama
                    })
    except Exception as e:
        print(f"API Hatası: {e}")
    return kitaplar

@app.route('/')
def index():
    filtre = request.args.get('filtre', 'tumu')
    arama_terimi = request.args.get('arama', '').strip()
    kategori_filtre = request.args.get('kategori', '').strip()

    # İSTATİSTİKLER VE DİNAMİK HEDEF HESAPLAMA
    toplam_kitap = len(yonetici.kitaplar)
    okunan_kitap = len([k for k in yonetici.kitaplar if k["okundu"]])
    okunacak_kitap = toplam_kitap - okunan_kitap
    oran = int((okunan_kitap / toplam_kitap) * 100) if toplam_kitap > 0 else 0

    # Yıllık 50 kitap hedefine göre yüzde hesabı
    hedef_toplam = 50
    hedef_yuzde = int((okunan_kitap / hedef_toplam) * 100) if okunan_kitap <= hedef_toplam else 100

    stats = {
        "toplam": toplam_kitap,
        "okunan": okunan_kitap,
        "okunacak": okunacak_kitap,
        "oran": oran,
        "hedef_toplam": hedef_toplam,
        "hedef_yuzde": hedef_yuzde
    }

    sozler = [
        {"soz": "Kitapsız bir oda, ruhsuz bir beden gibidir.", "yazar": "Cicero"},
        {"soz": "Bir kitap, içimizdeki donmuş denizi kırmaya yarayan bir baltadır.", "yazar": "Franz Kafka"},
        {"soz": "Okumak, sana hiç bilmediğin dünyaların kapısını açar.", "yazar": "Anonim"}
    ]
    gunun_sozu = random.choice(sozler)

    benim_kitaplar = list(enumerate(yonetici.kitaplar))
    if filtre == 'okunmadi':
        benim_kitaplar = [(i, k) for i, k in benim_kitaplar if not k["okundu"]]
    elif filtre == 'okundu':
        benim_kitaplar = [(i, k) for i, k in benim_kitaplar if k["okundu"]]

    if arama_terimi:
        sorgu = arama_terimi
        aktif_etiket = f"Aranan: '{arama_terimi}'"
    elif kategori_filtre:
        sorgu = kategori_filtre
        aktif_etiket = f"Kategori: {kategori_filtre}"
    else:
        sorgu = "Classic"
        aktif_etiket = "Öne Çıkan Popüler Kitaplar"

    canli_kitaplar = open_library_kitap_ara(sorgu)

    return render_template(
        'index.html', 
        benim_kitaplar=benim_kitaplar, 
        canli_kitaplar=canli_kitaplar, 
        aktif_etiket=aktif_etiket, 
        filtre=filtre, 
        arama=arama_terimi,
        stats=stats,
        gunun_sozu=gunun_sozu,
        gunun_notu=yonetici.veri["gunun_notu"]  # Kaydedilen notu HTML'e gönderiyoruz
    )

@app.route('/ekle', methods=['POST'])
def ekle():
    baslik = request.form.get('baslik')
    yazar = request.form.get('yazar')
    kategori = request.form.get('kategori')
    if baslik and yazar:
        yonetici.kitap_ekle(baslik, yazar, kategori)
    return redirect(url_for('index'))

@app.route('/not_kaydet', methods=['POST'])
def not_kaydet():
    yeni_not = request.form.get('not_icerik', '').strip()
    yonetici.not_guncelle(yeni_not)
    return redirect(url_for('index'))

@app.route('/durum/<int:index>')
def durum(index):
    yonetici.durum_degistir(index)
    return redirect(url_for('index'))

@app.route('/sil/<int:index>')
def sil(index):
    yonetici.kitap_sil(index)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)