"""
Kitap Takip Uygulaması 

Amaç: Okunan/okunacak kitapları ekleyen, listeleyen, durumunu (okundu/okunmadı)
güncelleyen ve silen gelişmiş bir konsol uygulaması. Kitaplar 'kitaplar.json'
dosyasında saklanır; program kapanıp açılınca kayıtlar korunur.



İşlevler:
    1. Kitapları Listele (Tümü veya Filtreli)
    2. Yeni Kitap Ekle (Puanlama desteği ile)
    3. Okundu/Okunmadı İşaretle
    4. Kitap Sil
    5. Kitap Ara (Gelişmiş Arama)
    6. Çıkış (Kayıtları kalıcı olarak yazar)
"""

import json
import os

class KitapYonetici:
    def __init__(self, dosya_adi="kitaplar.json"):
        self.dosya_adi = dosya_adi
        self.kitaplar = self._kitaplari_yukle()

    def _kitaplari_yukle(self):
        if not os.path.exists(self.dosya_adi):
            print("\n[Sistem] Kitap Takip Uygulamasına Hoş Geldiniz!")
            print("[Sistem] Kayıt dosyası bulunamadı. Yeni bir veri tabanı oluşturuldu.")
            return []
        
        try:
            with open(self.dosya_adi, "r", encoding="utf-8") as f:
                data = json.load(f)
                print("\n[Sistem] Kitap Takip Uygulamasına Hoş Geldiniz!")
                print(f"[Sistem] {len(data)} adet kitap başarıyla yüklendi.")
                return data
        except (json.JSONDecodeError, IOError):
            print("\n[Hata] Veri dosyası okunurken hata oluştu! Boş listeyle başlatılıyor.")
            return []

    def _kitaplari_kaydet(self):
        try:
            with open(self.dosya_adi, "w", encoding="utf-8") as f:
                json.dump(self.kitaplar, f, ensure_ascii=False, indent=4)
            print("[Sistem] Değişiklikler başarıyla diske kaydedildi.")
        except IOError:
            print("[Hata] Kritik Hata: Değişiklikler dosyaya yazılamadı!")

    def kitap_ekle(self):
        print("\n--- YENİ KİTAP EKLE ---")
        baslik = input("Kitap Adı: ").strip()
        yazar = input("Yazar Adı: ").strip()
        
        if not baslik or not yazar:
            print("[Hata] Kitap adı veya yazar alanı boş bırakılamaz!")
            return

        puan = "Belirtilmedi"
        puan_istegi = input("Kitaba puan vermek ister misiniz? (E/H): ").strip().upper()
        if puan_istegi == "E":
            try:
                giriş_puan = int(input("Puanınız (1-5 arası): ").strip())
                if 1 <= giriş_puan <= 5:
                    puan = f"{giriş_puan}/5"
                else:
                    print("[Uyarı] Geçersiz aralık. Puan 'Belirtilmedi' olarak ayarlandı.")
            except ValueError:
                print("[Uyarı] Sayısal değer girilmedi. Puan 'Belirtilmedi' olarak ayarlandı.")

        yeni_kitap = {
            "baslik": baslik,
            "yazar": yazar,
            "okundu": False,
            "puan": puan
        }
        
        self.kitaplar.append(yeni_kitap)
        print(f"[Başarılı] '{baslik}' koleksiyona dahil edildi.")
        self._kitaplari_kaydet()

    def kitaplari_listele(self, filtre_okunmadi=False):
        gosterilecek_liste = self.kitaplar
        
        if filtre_okunmadi:
            gosterilecek_liste = [k for k in self.kitaplar if not k["okundu"]]

        if not gosterilecek_liste:
            print("\n[Bilgi] Gösterilecek herhangi bir kitap kaydı bulunamadı.")
            return False

        print("\n" + "="*60)
        print(f"{'ID':<4} | {'KİTAP ADI':<22} | {'YAZAR':<18} | {'DURUM':<10} | {'PUAN'}")
        print("="*60)
        
        for index, kitap in enumerate(self.kitaplar, start=1):
            if filtre_okunmadi and kitap["okundu"]:
                continue
            durum = "Okundu" if kitap["okundu"] else "Okunmadı"
            print(f"{index:<4} | {kitap['baslik'][:22]:<22} | {kitap['yazar'][:18]:<18} | {durum:<10} | {kitap['puan']}")
        print("="*60)
        return True

    def durum_degistir(self):
        if not self.kitaplari_listele():
            return
            
        try:
            secim = input("\nDurumunu değiştirmek istediğiniz kitap ID'sini girin: ").strip()
            id_no = int(secim)
            
            if 1 <= id_no <= len(self.kitaplar):
                kitap = self.kitaplar[id_no - 1]
                kitap["okundu"] = not kitap["okundu"]
                yeni_durum = "Okundu" if kitap["okundu"] else "Okunmadı"
                print(f"[Başarılı] '{kitap['baslik']}' durumu '{yeni_durum}' olarak güncellendi.")
                self._kitaplari_kaydet()
            else:
                print("[Hata] Girilen ID numarasına ait kitap bulunamadı!")
        except ValueError:
            print("[Hata] Lütfen geçerli bir sayısal ID girin!")

    def kitap_sil(self):
        if not self.kitaplari_listele():
            return
            
        try:
            secim = input("\nSilmek istediğiniz kitap ID'sini girin: ").strip()
            id_no = int(secim)
            
            if 1 <= id_no <= len(self.kitaplar):
                silinen = self.kitaplar.pop(id_no - 1)
                print(f"[Başarılı] '{silinen['baslik']}' adlı kitap sistemden silindi.")
                self._kitaplari_kaydet()
            else:
                print("[Hata] Girilen ID numarasına ait kitap bulunamadı!")
        except ValueError:
            print("[Hata] Lütfen geçerli bir sayısal ID girin!")

    def kitap_ara(self):
        print("\n--- GELİŞMİŞ KİTAP ARAMA ---")
        arama_terimi = input("Aramak istediğiniz kelime (Kitap adı veya Yazar): ").strip().lower()
        
        if not arama_terimi:
            print("[Hata] Arama terimi boş olamaz!")
            return

        sonuclar = [k for k in self.kitaplar if arama_terimi in k["baslik"].lower() or arama_terimi in k["yazar"].lower()]
        
        if not sonuclar:
            print("[Sonuç] Eşleşen bir kitap bulunamadı.")
            return

        print("\n--- ARAMA SONUÇLARI ---")
        for k in sonuclar:
            durum = "Okundu" if k["okundu"] else "Okunmadı"
            print(f"- {k['baslik']} / {k['yazar']} [{durum}] (Puan: {k['puan']})")

def ana_akis():
    yonetici = KitapYonetici()
    
    while True:
        print("\n::::: KİTAP TAKİP SİSTEMİ MENÜSÜ :::::")
        print("1. Tüm Kitapları Listele")
        print("2. Sadece Okunmayan Kitapları Listele")
        print("3. Yeni Kitap Kaydı Oluştur")
        print("4. Kitap Okuma Durumu Güncelle")
        print("5. Kitap Kaydı Sil")
        print("6. Detaylı Kitap Arama")
        print("7. Güvenli Çıkış")
        
        secim = input("Lütfen yapmak istediğiniz işlemi seçin (1-7): ").strip()
        
        if secim == "1":
            yonetici.kitaplari_listele(filtre_okunmadi=False)
        elif secim == "2":
            yonetici.kitaplari_listele(filtre_okunmadi=True)
        elif secim == "3":
            yonetici.kitap_ekle()
        elif secim == "4":
            yonetici.durum_degistir()
        elif secim == "5":
            yonetici.kitap_sil()
        elif secim == "6":
            yonetici.kitap_ara()
        elif secim == "7":
            print("\n[Sistem] Oturum kapatılıyor. İyi günler dileriz...")
            break
        else:
            print("[Hata] Geçersiz komut! Lütfen menüdeki seçeneklerden (1-7) birini girin.")

if __name__ == "__main__":
    ana_akis()