
import requests
from bs4 import BeautifulSoup
from exception import exception


def ekstraksi_data():
    try :
        content = requests.get("https://www.bmkg.go.id")
    except exception:
        return None
    if content.status_code == 200:
        soup = BeautifulSoup(content.text, "html.parser")

        result = soup.find("span",{"class": "waktu"})
        waktu = result.text.split(",")[1]
        tanggal = result.text.split(",")[0]
        result = soup.find ("div", {"class": "col-md-6 col-xs-6 gempabumi-detail no-padding"})
        result = result.findChildren("li")
        i = 0
        magnitudo = None
        kedalaman = None
        LS = None
        BT = None
        lokasi = None
        dirasakan = None
        for res in result:
            print(i,res)
            if i == 1:
                magnitudo = res.text
            elif i == 2:
                kedalaman = res.text
            elif i == 3:
                koordinate = res.text.split(" - ")
                LS = koordinate[0]
                BT = koordinate[1]
            elif i == 4:
                lokasi = res.text
            elif i == 5:
                dirasakan = res.text
            i = i + 1

        hasil = dict()
        hasil["tanggal"] = tanggal
        hasil["waktu"] = waktu
        hasil["magnitudo"] = magnitudo
        hasil["kedalaman"] = kedalaman
        hasil["koordinate"] = {"LS": LS, "BT": BT}
        hasil["lokasi"] = lokasi
        hasil["dirasakan"] = dirasakan
        print(hasil)
        return hasil
    else:
        return None


def tampilkan_data(result):
    if result is None:
        print("tedak ada data gempa terkini")
        return

    print("Tampilkan data gempa terkini")
    print(f'Tanggal {result["tanggal"]}')
    print(f'Waktu {result["waktu"]}')
    print(f'Magnitudo {result["magnitudo"]}')
    print(f'Kedalaman {result["kedalaman"]}')
    print(f'koordinate: LS={result["koordinate"]["LS"]}, BT={result["koordinate"]["BT"]}')
    print(f'lokasi {result["lokasi"]}')
    print(f'Dirasakan {result["dirasakan"]}')

if __name__ == "__main__":
    result = ekstraksi_data()
    tampilkan_data(result)
