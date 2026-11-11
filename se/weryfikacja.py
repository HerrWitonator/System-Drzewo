"""Weryfikacja bazy wiedzy (odpowiednik programu Cake z pakietu SPHINX) — do uzupełnienia na spotkaniu 3.
Uruchom: python se/weryfikacja.py wiedza/kawa_z_bledami.json
"""
import sys
from pathlib import Path

from silnik import OPERATORY, wczytaj_baze


def weryfikuj(baza):
    """Zwraca listę (poziom, komunikat); poziom to 'BŁĄD' albo 'UWAGA'."""
    raport = []
    atrybuty = baza["atrybuty"]
    reguly = baza["reguly"]

    # Test 1 (gotowy): powtórzone identyfikatory reguł
    ids = [r["id"] for r in reguly]
    for id_ in sorted({i for i in ids if ids.count(i) > 1}):
        raport.append(("BŁĄD", f"Powtórzony identyfikator reguły {id_}"))

    # Test 2 (gotowy): niezadeklarowane atrybuty i nieznane operatory w warunkach
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr not in atrybuty:
                raport.append(("BŁĄD", f"{r['id']}: niezadeklarowany atrybut '{atr}'"))
            if op not in OPERATORY:
                raport.append(("BŁĄD", f"{r['id']}: nieznany operator '{op}'"))

    # TODO 3: wartości spoza dziedziny — dla atrybutów z listą "wartosci"
    #         sprawdź warunki z operatorem == lub != (BŁĄD).
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if atr in atrybuty and op in ("==", "!="):
                dziedzina = atrybuty[atr].get("wartosci")
                if isinstance(dziedzina, list) and wart not in dziedzina:
                    raport.append(("BŁĄD", f"{r['id']}: wartość '{wart}' spoza dziedziny atrybutu '{atr}'"))

    # TODO 4: nieużywane atrybuty wejściowe (typ inny niż "wniosek", nieobecne w żadnym warunku)
    #         oraz nieużywane wartości atrybutów typu "wybor" (UWAGA).
    uzyte_atrybuty = {warunek[0] for r in reguly for warunek in r["jesli"]}
    for atr, opis in atrybuty.items():
        if opis["typ"] != "wniosek" and atr not in uzyte_atrybuty:
            raport.append(("UWAGA", f"Nieużywany atrybut wejściowy '{atr}'"))
        if opis["typ"] == "wybor":
            uzyte_wartosci = {
                wart for r in reguly for nazwa, op, wart in r["jesli"]
                if nazwa == atr and op in ("==", "!=")
            }
            for wart in opis.get("wartosci", []):
                if wart not in uzyte_wartosci:
                    raport.append(("UWAGA", f"Nieużywana wartość '{wart}' atrybutu '{atr}'"))

    # TODO 5: warunek niemożliwy do spełnienia — warunek atr == wart, gdzie atr jest typu "wniosek",
    #         a żadna reguła nie ma wniosku ["atr", "wart"] (BŁĄD).
    mozliwe_wnioski = {tuple(r["to"]) for r in reguly}
    for r in reguly:
        for atr, op, wart in r["jesli"]:
            if (op == "==" and atr in atrybuty
                    and atrybuty[atr]["typ"] == "wniosek"
                    and (atr, wart) not in mozliwe_wnioski):
                raport.append(("BŁĄD", f"{r['id']}: niemożliwy warunek '{atr} == {wart}'"))

    # TODO 6: porównaj każdą parę reguł (warunki zamień na zbiory krotek: {tuple(w) for w in r["jesli"]}):
    #   - te same warunki i ten sam wniosek       -> duplikat (UWAGA)
    #   - te same warunki, inna wartość wniosku   -> sprzeczność (BŁĄD)
    #   - ten sam wniosek, warunki A ⊂ warunki B  -> B jest pochłaniana przez A (UWAGA)
    for i, r1 in enumerate(reguly):
        warunki1 = {tuple(w) for w in r1["jesli"]}
        for r2 in reguly[i + 1:]:
            warunki2 = {tuple(w) for w in r2["jesli"]}
            if warunki1 == warunki2:
                if r1["to"] == r2["to"]:
                    raport.append(("UWAGA", f"Duplikat reguł {r1['id']} i {r2['id']}"))
                elif r1["to"][0] == r2["to"][0]:
                    raport.append(("BŁĄD", f"Sprzeczne reguły {r1['id']} i {r2['id']}"))
            elif r1["to"] == r2["to"]:
                if warunki1 < warunki2:
                    raport.append(("UWAGA", f"Reguła {r2['id']} pochłaniana przez {r1['id']}"))
                elif warunki2 < warunki1:
                    raport.append(("UWAGA", f"Reguła {r1['id']} pochłaniana przez {r2['id']}"))


    # TODO 7: cel główny baza["cel"] musi być wnioskiem co najmniej jednej reguły (BŁĄD).
    if not any(r["to"][0] == baza["cel"] for r in reguly):
        raport.append(("BŁĄD", f"Brak reguły wyprowadzającej cel '{baza['cel']}'"))

    return raport


if __name__ == "__main__":
    plik = sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json"
    wyniki = weryfikuj(wczytaj_baze(plik))
    if not wyniki:
        print("Baza wiedzy nie zawiera wykrytych problemów.")
    for poziom, komunikat in wyniki:
        print(f"[{poziom}] {komunikat}")
    print(f"\nZnaleziono: {len(wyniki)} ")
