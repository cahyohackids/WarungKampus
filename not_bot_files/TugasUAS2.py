def hitung_ganjil(angka_list):
    jumlah_ganjil = 0
    total_ganjil = 0
    for angka in angka_list:
        if angka % 2 == 0:  
            continue
        jumlah_ganjil += angka
        total_ganjil += 1
    
    if total_ganjil == 0:  
        return "Tidak ada bilangan ganjil", None
    
    rata_rata = jumlah_ganjil / total_ganjil
    return jumlah_ganjil, rata_rata
angka_list = [3, 4, 7, 10, 15, 20, 22, 30]
jumlah, rata_rata = hitung_ganjil(angka_list)

if rata_rata is None:
    print(jumlah)
else:
    print("Jumlah angka ganjil:", jumlah)
    print("Rata-rata angka ganjil:", rata_rata)
