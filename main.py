import sqlite3
from datetime import datetime

conn = sqlite3.connect("wydatki.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS wydatki (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kategoria TEXT NOT NULL,
    kwota REAL NOT NULL,
    data TEXT NOT NULL,
    opis TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS wplywy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zrodlo TEXT NOT NULL,
    kwota REAL NOT NULL,
    data TEXT NOT NULL,
    opis TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS budzety (
    miesiac TEXT PRIMARY KEY,
    budzet REAL NOT NULL
)
''')

conn.commit()


def dodaj_wydatek():
    print("Dodawanie nowego wydatku:")
    kategoria = input("Podaj kategorię: ") or "Nieokreślona"
    kwota = float(input("Podaj kwotę: ") or 0.0)
    data = input("Podaj datę (YYYY-MM-DD) [Domyślnie dzisiejsza]: ")
    opis = input("Podaj opis (opcjonalnie): ")

    if not data:
        data = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO wydatki (kategoria, kwota, data, opis) VALUES (?, ?, ?, ?)",
        (kategoria, kwota, data, opis)
    )
    conn.commit()
    print("Wydatek dodany pomyślnie!\n")


def dodaj_wplyw():
    print("Dodawanie nowego wpływu:")
    zrodlo = input("Podaj źródło: ") or "Nieokreślone"
    kwota = float(input("Podaj kwotę: ") or 0.0)
    data = input("Podaj datę (YYYY-MM-DD) [Domyślnie dzisiejsza]: ")
    opis = input("Podaj opis (opcjonalnie): ")

    if not data:
        data = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO wplywy (zrodlo, kwota, data, opis) VALUES (?, ?, ?, ?)",
        (zrodlo, kwota, data, opis)
    )
    conn.commit()
    print("Wpływ dodany pomyślnie!\n")


def wyswietl_wydatek():
    cursor.execute("SELECT * FROM wydatki")
    wydatki = cursor.fetchall()

    if not wydatki:
        print("Brak wydatków do wyświetlenia.\n")
        return

    print("Lista wydatków:")
    print("ID | Kategoria | Kwota | Data | Opis")
    print("-" * 50)
    for w in wydatki:
        print(f"{w[0]} | {w[1]} | {w[2]:.2f} | {w[3]} | {w[4]}")
    print()


def wyswietl_wplywy():
    cursor.execute("SELECT * FROM wplywy")
    wplywy = cursor.fetchall()

    if not wplywy:
        print("Brak wpływów do wyświetlenia.\n")
        return

    print("Lista wpływów:")
    print("ID | Źródło | Kwota | Data | Opis")
    print("-" * 50)
    for w in wplywy:
        print(f"{w[0]} | {w[1]} | {w[2]:.2f} | {w[3]} | {w[4]}")
    print()


def usun_wydatek():
    wyswietl_wydatek()
    try:
        wydatek_id = int(input("Podaj ID wydatku do usunięcia: "))
        cursor.execute("DELETE FROM wydatki WHERE id = ?", (wydatek_id,))
        conn.commit()
        print("Wydatek usunięty pomyślnie!\n")
    except ValueError:
        print("Nieprawidłowy ID. Spróbuj ponownie.\n")


def usun_wplyw():
    wyswietl_wplywy()
    try:
        wplyw_id = int(input("Podaj ID wpływu do usunięcia: "))
        cursor.execute("DELETE FROM wplywy WHERE id = ?", (wplyw_id,))
        conn.commit()
        print("Wpływ usunięty pomyślnie!\n")
    except ValueError:
        print("Nieprawidłowy ID. Spróbuj ponownie.\n")


def miesiac_slownie(miesiac):
    miesiace = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]
    return miesiace[int(miesiac) - 1]


def generuj_raporty():
    cursor.execute(
        "SELECT DISTINCT strftime('%Y-%m', data) AS miesiac FROM (SELECT data FROM wydatki UNION SELECT data FROM wplywy) ORDER BY miesiac")
    miesiace = cursor.fetchall()

    if not miesiace:
        print("Brak danych do wygenerowania raportu.\n")
        return

    print("Dostępne miesiące:")
    for i, (miesiac,) in enumerate(miesiace, start=1):
        rok, miesiac_num = miesiac.split('-')
        print(f"{i}. {rok} {miesiac_slownie(miesiac_num)}")

    try:
        wybor = int(input("Wybierz miesiąc (numer): "))
        if 1 <= wybor <= len(miesiace):
            wybrany_miesiac = miesiace[wybor - 1][0]

            cursor.execute("SELECT SUM(kwota) FROM wplywy WHERE strftime('%Y-%m', data) = ?", (wybrany_miesiac,))
            suma_wplywow = cursor.fetchone()[0] or 0.0

            cursor.execute("SELECT SUM(kwota) FROM wydatki WHERE strftime('%Y-%m', data) = ?", (wybrany_miesiac,))
            suma_wydatkow = cursor.fetchone()[0] or 0.0

            rok, miesiac_num = wybrany_miesiac.split('-')
            print(f"\nRaport dla miesiąca {rok} {miesiac_slownie(miesiac_num)}:")

            print("Wpływy:")
            cursor.execute("SELECT * FROM wplywy WHERE strftime('%Y-%m', data) = ?", (wybrany_miesiac,))
            wplywy = cursor.fetchall()
            if wplywy:
                print("ID | Źródło | Kwota | Data | Opis")
                print("-" * 50)
                for w in wplywy:
                    print(f"{w[0]} | {w[1]} | {w[2]:.2f} | {w[3]} | {w[4]}")
            else:
                print("Brak wpływów.")

            print("\nWydatki:")
            cursor.execute("SELECT * FROM wydatki WHERE strftime('%Y-%m', data) = ?", (wybrany_miesiac,))
            wydatki = cursor.fetchall()
            if wydatki:
                print("ID | Kategoria | Kwota | Data | Opis")
                print("-" * 50)
                for w in wydatki:
                    print(f"{w[0]} | {w[1]} | {w[2]:.2f} | {w[3]} | {w[4]}")
            else:
                print("Brak wydatków.")

            print(f"\nBilans: {suma_wplywow - suma_wydatkow:.2f}\n")

            cursor.execute("SELECT budzet FROM budzety WHERE miesiac = ?", (wybrany_miesiac,))
            budzet = cursor.fetchone()
            if budzet:
                budzet = budzet[0]
                bilans_budzetu = budzet - suma_wydatkow
                print(f"Zaplanowany budżet: {budzet:.2f} zł")
                print(f"Bilans względem budżetu: {'+' if bilans_budzetu >= 0 else ''}{bilans_budzetu:.2f} zł")
            else:
                print("Brak zaplanowanego budżetu na ten miesiąc.")

        else:
            print("Nieprawidłowy numer miesiąca. Spróbuj ponownie.\n")
    except ValueError:
        print("Nieprawidłowy wybór. Spróbuj ponownie.\n")

def zaplanuj_budzet():
    print("Planowanie budżetu:")
    miesiac = input("Podaj miesiąc (YYYY-MM): ").strip()
    if not miesiac:
        print("Nie podano miesiąca. Operacja anulowana.")
        return

    try:
        budzet = float(input("Podaj kwotę budżetu: "))
        cursor.execute(
            "INSERT INTO budzety (miesiac, budzet) VALUES (?, ?) ON CONFLICT(miesiac) DO UPDATE SET budzet = excluded.budzet",
            (miesiac, budzet)
        )
        conn.commit()
        print(f"Budżet na miesiąc {miesiac} został zaplanowany.\n")
    except ValueError:
        print("Nieprawidłowa kwota. Spróbuj ponownie.\n")

def wyswietl_budzety():
    cursor.execute("SELECT * FROM budzety ORDER BY miesiac")
    budzety = cursor.fetchall()

    if not budzety:
        print("Brak zaplanowanych budżetów.\n")
        return

    print("Zaplanowane budżety:")
    print("Miesiąc | Kwota")
    print("-" * 20)
    for b in budzety:
        print(f"{b[0]} | {b[1]:.2f}")
    print()


def menu():
    options = {
        "1": dodaj_wydatek,
        "2": dodaj_wplyw,
        "3": wyswietl_wydatek,
        "4": wyswietl_wplywy,
        "5": usun_wydatek,
        "6": usun_wplyw,
        "7": generuj_raporty,
        "8": zaplanuj_budzet,
        "9": wyswietl_budzety
    }
    while True:
        print("\nMenu aplikacji:\n")
        print("1. Dodaj wydatek")
        print("2. Dodaj wpływ")
        print("3. Wyświetl wydatki")
        print("4. Wyświetl wpływy")
        print("5. Usuń wydatek")
        print("6. Usuń wpływ")
        print("7. Generuj raport")
        print("8. Zaplanuj budżet")
        print("9. Edytuj planowane budżety")
        print("10. Wyjdź")

        wybor = input("Wybierz opcję (1-10): ").strip()

        if wybor in options:
            options[wybor]()
        elif wybor == "10":
            print("Dziękujemy za skorzystanie z aplikacji!")
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.\n")


if __name__ == "__main__":
    try:
        menu()
    except EOFError:
        print("\nWejście zakończone. Aplikacja zamknięta.")

conn.close()
