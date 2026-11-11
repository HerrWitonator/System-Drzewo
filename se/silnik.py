"""Silnik wnioskujący — do uzupełnienia na spotkaniu 2. Miejsca do uzupełnienia oznaczono TODO."""
import json
import operator
from pathlib import Path

OPERATORY = {
    "==": operator.eq, "!=": operator.ne,
    ">": operator.gt, ">=": operator.ge,
    "<": operator.lt, "<=": operator.le,
}


def wczytaj_baze(sciezka):
    return json.loads(Path(sciezka).read_text(encoding="utf-8"))


def warunek_spelniony(warunek, fakty):
    """warunek to lista [atrybut, operator, wartość], np. ["temperatura", ">", 22]."""
    atrybut, op, wartosc = warunek
    return atrybut in fakty and fakty[atrybut] is not None and OPERATORY[op](fakty[atrybut], wartosc)


def regula_spelniona(regula, fakty):
    return all(
        warunek_spelniony(warunek, fakty)
        for warunek in regula["jesli"]
    )
    raise NotImplementedError


def wnioskuj_w_przod(baza, fakty):
    """Zwraca (fakty po wnioskowaniu, lista id odpalonych reguł)."""
    fakty = dict(fakty)
    slad = []
    zmiana = True
    while zmiana:
        zmiana = False
        for regula in baza["reguly"]:
            atrybut, wartosc = regula["to"]
            if atrybut not in fakty and regula_spelniona(regula, fakty):
                fakty[atrybut] = wartosc
                slad.append(regula["id"])
                zmiana = True
            pass
    return fakty, slad


def wnioskuj_wstecz(baza, cel, fakty, zapytaj, slad=None, powod=None):
    """Ustala wartość atrybutu `cel`. Brakujące dane pobiera funkcją zapytaj(atrybut, powod)."""
    if slad is None:
        slad = []
    if cel in fakty:                                   # już wiemy — nie pytamy drugi raz
        return fakty[cel]
    if cel not in baza["atrybuty"]:
        raise ValueError(f"Niezadeklarowany atrybut: {cel}")

    reguly = [r for r in baza["reguly"] if r["to"][0] == cel]

    # Wniosek bez reguł to luka w bazie: nie pytamy użytkownika o gotową decyzję.
    if not reguly and baza["atrybuty"][cel]["typ"] == "wniosek":
        fakty[cel] = None
        return None

    if not reguly:
        fakty[cel] = zapytaj(cel, powod)
        return fakty[cel]

    for regula in reguly:
        spelniona = True
        for atrybut, op, wartosc in regula["jesli"]:
            znana = wnioskuj_wstecz(
                baza, atrybut, fakty, zapytaj, slad, regula
            )

            if znana is None or not warunek_spelniony(
                (atrybut, op, wartosc), fakty
            ):
                spelniona = False
                break

            pass
        if spelniona:
            fakty[cel] = regula["to"][1]
            slad.append(regula["id"])
            return fakty[cel]

    fakty[cel] = None
    return None


def zapytaj_konsola(baza):
    """Pytanie w konsoli. Sprawdza odpowiedź, bo literówka („Tak”, „popoludnie”) dałaby ciche None."""
    def zapytaj(atrybut, powod):
        opis = baza["atrybuty"].get(atrybut, {})
        podpowiedz = f" ({'/'.join(opis['wartosci'])})" if "wartosci" in opis else ""
        while True:
            odp = input(f"{opis.get('pytanie', atrybut)}{podpowiedz} ").strip()
            if opis.get("typ") == "liczba":
                try:
                    return float(odp.replace(",", "."))
                except ValueError:
                    print("   Podaj liczbę.")
                    continue
            if "wartosci" in opis and odp not in opis["wartosci"]:
                print("   Dozwolone:", ", ".join(opis["wartosci"]))
                continue
            return odp
    return zapytaj

# Brakująca funkcja, prawdopodobnie miałem dodać
def coto(baza, slad):
    """Zwraca opis decyzji końcowej z ostatniej użytej reguły."""
    reguly = {regula["id"]: regula for regula in baza["reguly"]}
    for identyfikator in reversed(slad):
        regula = reguly.get(identyfikator)
        if regula and regula["to"][0] == baza["cel"]:
            return regula.get("coto", "Brak opisu rekomendacji.")
    return "Brak opisu rekomendacji."

# Brakująca funkcja po raz drugi
def wyjasnij_jak(baza, slad):
    """Zwraca listę opisów reguł uruchomionych podczas wnioskowania."""
    reguly = {regula["id"]: regula for regula in baza["reguly"]}
    kroki = []
    for identyfikator in slad:
        regula = reguly.get(identyfikator)
        if regula is None:
            kroki.append(f"{identyfikator}: nie znaleziono reguły w bazie.")
            continue
        warunki = " ORAZ ".join(
            f"{atrybut} {operator} {wartosc}"
            for atrybut, operator, wartosc in regula["jesli"]
        ) or "zawsze"
        atrybut, wartosc = regula["to"]
        opis = f"{identyfikator}: JEŻELI {warunki}, TO {atrybut} = {wartosc}"
        if regula.get("metafora"):
            opis += f". {regula['metafora']}"
        kroki.append(opis)
    return kroki

def zapytaj_z_dlaczego(atrybut, powod):
        opis = baza["atrybuty"].get(atrybut, {})
        podpowiedz = f" ({'/'.join(opis['wartosci'])})" if "wartosci" in opis else ""
        while True:
            odp = input(f"{opis.get('pytanie', atrybut)}{podpowiedz} ").strip()
            if odp == "?":
                if powod is not None:
                    warunki = " ORAZ ".join(
                        f"{a} {op} {w}" for a, op, w in powod["jesli"]
                    )
                    print(f"Dlaczego? Sprawdzam regułę {powod['id']}:")
                    print(f"  JEŻELI {warunki}, TO {powod['to'][0]} = {powod['to'][1]}")
                    if powod.get("metafora"):
                        print(" ", powod["metafora"])
                else:
                    print("Dlaczego? Ta odpowiedź jest potrzebna do ustalenia celu:", cel)
                continue
            if opis.get("typ") == "liczba":
                try:
                    return float(odp.replace(",", "."))
                except ValueError:
                    print("   Podaj liczbę lub ?")
                    continue
            if "wartosci" in opis and odp not in opis["wartosci"]:
                print("   Dozwolone:", ", ".join(opis["wartosci"]), "lub ?")
                continue
            return odp


if __name__ == "__main__":
    # Część 5 instrukcji: tu podmieniasz plik bazy i przykładowe fakty na swoje.
    PLIK_BAZY = Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json"
    FAKTY = {
    "budzet": 4500,
    "grafika": "tak",
    "gry": "nie",
    "mobilnosc": "nie",
    "biznes": "nie"
    }

    baza = wczytaj_baze(PLIK_BAZY)
    cel = baza["cel"]

    print("=== Wnioskowanie w przód ===")
    fakty, slad = wnioskuj_w_przod(baza, FAKTY)
    print("Wynik:", fakty.get(cel), "| reguły:", " -> ".join(slad))
    print("Jak doszedłem do wniosku?")
    for krok in wyjasnij_jak(baza, slad):
        print(" -", krok)

    print("\n=== Wnioskowanie wstecz ===")
    print("Wpisz ? przy dowolnym pytaniu, aby dowiedzieć się, dlaczego zostało zadane.")
    slad = []
    wynik = wnioskuj_wstecz(baza, cel, {}, zapytaj_z_dlaczego, slad)
    print("Polecam:", wynik)
    print("Reguły:", " -> ".join(slad))
    print("Jak doszedłem do wniosku?")
    for krok in wyjasnij_jak(baza, slad):
        print(" -", krok)
    if wynik is not None:
        print("Co to?", coto(baza, slad))
