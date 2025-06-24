ukoly = []  # Globální seznam úkolů
def hlavni_menu():
    while True:
        print("\n===== TASK MANAGER =====")
        print("1 - Přidat úkol")
        print("2 - Zobrazit úkoly")
        print("3 - Odstranit úkol")
        print("4 - Konec programu")

        volba = input("Zadejte číslo volby: ")

        if volba == "1":
            pridat_ukol()
        elif volba == "2":
            zobrazit_ukoly()
        elif volba == "3":
            odstranit_ukol()
        elif volba == "4":
            print(">> Program ukončen.")
            break
        else:
            print("Neplatná volba. Zadejte prosím číslo 1-4.")

def pridat_ukol():
    while True:
        nazev = input("Zadejte název úkolu: ").strip()
        if nazev == "":
            print("⚠️ Název úkolu nesmí být prázdný.")
            continue

        popis = input("Zadejte popis úkolu: ").strip()
        if popis == "":
            print("⚠️ Popis úkolu nesmí být prázdný.")
            continue

        ukol = {"nazev": nazev, "popis": popis}
        ukoly.append(ukol)
        print(f"✅ Úkol '{nazev}' byl přidán.")
        break
def zobrazit_ukoly():
    if not ukoly:
        print("📭 Žádné úkoly nejsou k dispozici.")
        return

    print("\n📋 SEZNAM ÚKOLŮ:")
    for i, ukol in enumerate(ukoly, start=1):
        print(f"{i}. 📝 {ukol['nazev']}")
        print(f"   📌 {ukol['popis']}")
def odstranit_ukol():
    if not ukoly:
        print("📭 Žádné úkoly nejsou k odstranění.")
        return

    print("\n🗑️ SEZNAM ÚKOLŮ K ODSTRANĚNÍ:")
    for i, ukol in enumerate(ukoly, start=1):
        print(f"{i}. {ukol['nazev']}")

    try:
        cislo = int(input("Zadejte číslo úkolu, který chcete odstranit: "))
        if 1 <= cislo <= len(ukoly):
            odstraneny = ukoly.pop(cislo - 1)
            print(f"✅ Úkol '{odstraneny['nazev']}' byl odstraněn.")
        else:
            print("❌ Neplatné číslo úkolu.")
    except ValueError:
        print("❌ Neplatný vstup – zadejte číslo.")
# Spuštění hlavního menu
hlavni_menu()