"""Autotest silnika"""
from pathlib import Path

from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json")


PRZYPADKI = [
    (
        {"budzet": 2500, "grafika": "tak", "gry": "tak", "mobilnosc": "nie", "biznes": "nie"},
        "gamingowy_podstawowy",
        ["R1", "R4", "R7"]
    ),
    (
        {"budzet": 4500, "grafika": "tak", "gry": "nie", "mobilnosc": "nie", "biznes": "nie"},
        "profesjonalny_sredni",
        ["R2", "R5", "R13"]
    ),
    (
        {"budzet": 2000, "grafika": "nie", "gry": "nie", "mobilnosc": "tak", "biznes": "nie"},
        "mobilny_studencki_podstawowy",
        ["R1", "R6", "R9"]
    ),
    (
        {"budzet": 5500, "grafika": "nie", "gry": "nie", "mobilnosc": "nie", "biznes": "tak"},
        "biznesowy_sredni",
        ["R2", "R6", "R15"]
    ),
    (
        {"budzet": 8000, "grafika": "nie", "gry": "nie", "mobilnosc": "nie", "biznes": "nie"},
        "biurowy_wysoki",
        ["R3", "R6", "R21"]
    ),
]

cel = baza["cel"]

ok = 0
for wejscie, oczekiwane, oczekiwany_slad in PRZYPADKI:
    fakty, slad = wnioskuj_w_przod(baza, wejscie)
    w_przod_ok = fakty.get(cel) == oczekiwane and (oczekiwany_slad is None or slad == oczekiwany_slad)

    zadane = []
    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie[atrybut]
    wstecz = wnioskuj_wstecz(baza, cel, {}, zapytaj, [])
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))

    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] {wejscie} -> w przód: {fakty.get(cel)}, wstecz: {wstecz}, pytań: {len(zadane)}")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI)}")
