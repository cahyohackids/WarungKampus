def hitung_genap(angka_list):
    jumlah_genap = 0
    total_genap = 0
    for angka in angka_list:
        if angka % 2 != 0:
            continue
    jumlah_genap += angka
    total_genap += 1
    rata_rata = jumlah_genap / total_genap
    return jumlah_genap, rata_rata
angka_list = [3, 4, 7, 10, 15, 20, 22, 30]

jumlah, rata_rata = hitung_genap(angka_list)
print("Jumlah angka genap:", jumlah)
print("Rata-rata angka genap:", rata_rata)