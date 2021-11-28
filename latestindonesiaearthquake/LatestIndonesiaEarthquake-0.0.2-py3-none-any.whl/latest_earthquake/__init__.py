import requests
from bs4 import BeautifulSoup


class GempaTerkini:
    def __init__(self, url):
        self.description = 'Get latest earthquake in Indonesia'
        self.result = None
        self.url = url

    def ekstraksi_data(self):
        try:
            content = requests.get(self.url)
        except Exception:
            return None

        if content.status_code == 200:
            soup = BeautifulSoup(content.text, 'html.parser')
            gempa = soup.find('div', {'class': 'col-md-6 col-xs-6 gempabumi-detail no-padding'})
            gempa = gempa.findChildren('li')
            i = 0
            for res in gempa:
                if i == 0:
                    tgl = res.text.split(', ')
                    tanggal = tgl[0]
                    waktu = tgl[1]
                elif i == 1:
                    magnitudo = res.text
                elif i == 2:
                    kedalaman = res.text
                elif i == 3:
                    lokasi = res.text.split(' - ')
                    ls = lokasi[0]
                    bt = lokasi[1]
                elif i == 4:
                    pusat = res.text
                elif i == 5:
                    dirasakan = res.text
                i = i + 1

            hasil = dict()
            hasil['tanggal'] = tanggal
            hasil['waktu'] = waktu
            hasil['magnitudo'] = magnitudo
            hasil['kedalaman'] = kedalaman
            hasil['ls'] = ls
            hasil['bt'] = bt
            hasil['pusat_gempa'] = pusat
            hasil['dirasakan_skala_mmi'] = dirasakan
            self.result = hasil
        else:
            return None

    def tampilkan_data(self):
        if self.result is None:
            print("Tidak bisa mendapatkan data")
            return
        print('Gempa terkini berdasarkan BMKG')
        print(f"Tanggal: {self.result['tanggal']}")
        print(f"Waktu : {self.result['waktu']}")
        print(f"Magnitudo : {self.result['magnitudo']}")
        print(f"Kedalaman : {self.result['kedalaman']}")
        print(f"Lokasi : {self.result['ls']} {self.result['bt']}")
        print(f"{self.result['pusat_gempa']}")
        print(f"{self.result['dirasakan_skala_mmi']}")

    def run(self):
        self.ekstraksi_data()
        self.tampilkan_data()


if __name__ == '__main__':
    GempaIndonesia = GempaTerkini('https://bmkg.go.id')
    print('Description = ', GempaIndonesia.description)
    GempaIndonesia.run()
