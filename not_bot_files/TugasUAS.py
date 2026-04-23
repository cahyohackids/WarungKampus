def hitung_tagihan_listrik(golongan, daya, pemakaian):
    if golongan == 'R1' and daya == 1300:
        tarif = 800
    elif golongan == 'R1' and daya == 2200:
        tarif = 1300
    elif golongan == 'R2' and daya == 3500:
        tarif = 1500
    else:
        return "Golongan atau daya tidak valid."
    return tarif * pemakaian

# Input
golongan = input("Golongan: ")
daya = int(input("Daya: "))
pemakaian = int(input("Pemakaian (kWh): "))

# ini output
print("Tagihan: Rp", hitung_tagihan_listrik(golongan, daya, pemakaian))
