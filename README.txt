SYSTEM EKSPERTOWY – DOBÓR LAPTOPA
================================

Autor: Witold Kłopocki
Przedmiot: Inżynieria wiedzy i maszynowe uczenie (IWiMU), 2026/2027
Repozytorium: https://github.com/HerrWitonator/System-Drzewo

1. OPIS PROJEKTU
----------------
Projekt przedstawia regułowy system ekspertowy wspomagający wybór klasy laptopa na podstawie budżetu i potrzeb użytkownika. Obejmuje zadania Z1 (drzewo decyzyjne i dane uczące), Z2 (baza wiedzy JSON oraz wnioskowanie w przód i wstecz) i Z3 (wyjaśnienia, weryfikacja bazy i interfejs Streamlit).

System rekomenduje kategorię sprzętu i orientacyjną konfigurację, a nie konkretny model dostępny w sklepie. Nie korzysta z bieżących cen ani ofert handlowych.

2. DANE WEJŚCIOWE I WNIOSKI
---------------------------
Atrybuty wejściowe:
- budzet: liczba, od 1000 do 10000 zł;
- grafika: czy wymagana jest wysoka wydajność graficzna (tak/nie);
- gry: czy laptop ma służyć głównie do gier (tak/nie);
- mobilnosc: czy ważna jest wysoka mobilność (tak/nie);
- biznes: czy laptop ma służyć do pracy biznesowej (tak/nie).

Wnioski pośrednie:
- klasa_budzetowa: podstawowa (budzet <= 3000), srednia (3000 < budzet <= 6000), wysoka (budzet > 6000);
- profil_wydajnosci: gamingowy, profesjonalny albo standardowy.

Cel główny: rekomendacja. System rozróżnia 15 wyników: pięć zastosowań (gamingowy, profesjonalny, mobilny_studencki, biznesowy, biurowy) w trzech klasach budżetowych (podstawowy, sredni, wysoki).

3. BAZA WIEDZY I REGUŁY
-----------------------
Baza wiedzy jest zapisana w JSON. Zawiera 21 reguł:
- R1–R3: ustalenie klasy budżetowej;
- R4–R6: ustalenie profilu wydajności;
- R7–R21: wybór rekomendacji końcowej.

Łańcuch wnioskowania ma trzy poziomy: dane wejściowe -> wnioski pośrednie -> rekomendacja. Każda reguła zawiera pole "metafora", a reguły końcowe również pole "coto" z opisem sugerowanego laptopa.

Przykład:
  budzet = 4500, grafika = tak, gry = nie
  R2 -> klasa_budzetowa = srednia
  R5 -> profil_wydajnosci = profesjonalny
  R13 -> rekomendacja = profesjonalny_sredni

W przypadku profilu standardowego system uwzględnia dodatkowo mobilność i zastosowania biznesowe.

4. STRUKTURA PROJEKTU
---------------------
se/silnik.py              - silnik wnioskowania w przód i wstecz oraz obsługa konsultacji
se/weryfikacja.py         - sprawdzanie spójności i poprawności bazy wiedzy
se/test_silnik.py         - testy silnika (jeżeli plik jest obecny w danej wersji)
se/test_moja_dziedzina.py - testy własnej bazy (jeżeli plik jest obecny)
se/app.py lub app.py      - aplikacja Streamlit (zależnie od wersji projektu)
wiedza/                   - pliki baz wiedzy JSON, w tym moja_dziedzina.json
 docs/                    - dokumentacja i materiały projektu
README.txt                - opis projektu

Materiały zadania Z1 obejmują drzewo w formatach draw.io/SVG/PNG, zestaw reguł oraz plik wybor_laptopa.lrn. Dokładna lokalizacja tych plików zależy od struktury katalogu docs/.

5. URUCHOMIENIE
---------------
Wymagany jest Python 3 i biblioteka streamlit do uruchomienia interfejsu.

W katalogu głównym repozytorium można utworzyć środowisko wirtualne:
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install streamlit

Uruchomienie konsultacji w konsoli:
  python se/silnik.py

Uruchomienie interfejsu (jeżeli plik znajduje się w katalogu se/):
  python -m streamlit run se/app.py

Jeżeli app.py znajduje się w katalogu głównym:
  python -m streamlit run app.py

Aplikacja otwiera się zwykle pod adresem http://localhost:8501.

Uwaga: w używanej wersji app.py ścieżka PLIK_BAZY może wskazywać na przykładową bazę kawa.json. Aby pracować na systemie laptopowym, należy wskazać właściwy plik wiedza/moja_dziedzina.json i upewnić się, że ścieżka jest zgodna z lokalizacją app.py.

6. WNIOSKOWANIE I WYJAŚNIENIA
-----------------------------
Wnioskowanie w przód wyprowadza nowe fakty z podanych danych wejściowych i zapisuje identyfikatory uruchomionych reguł. Wnioskowanie wstecz rozpoczyna od celu i pyta tylko o dane potrzebne do jego ustalenia.

Moduł wyjaśnień pozwala pokazać:
- "Jak?" - które reguły doprowadziły do wyniku;
- "Dlaczego?" - z jakiego powodu system zadaje pytanie podczas konsultacji;
- "Co to?" - opis rekomendacji zapisany w polu coto.

Przykład z konsoli:
  budzet = 2500, grafika = tak, gry = tak
  Polecam: gamingowy_podstawowy
  Reguły: R1 -> R4 -> R7

7. WERYFIKACJA I TESTY
----------------------
Weryfikator sprawdza m.in. powtórzone identyfikatory, niezadeklarowane atrybuty, nieznane operatory, wartości spoza dziedziny, nieużywane atrybuty i wartości, niemożliwe warunki, duplikaty, sprzeczności, pochłanianie reguł oraz osiągalność celu.

Uruchomienie:
  python se/weryfikacja.py wiedza/moja_dziedzina.json

Test bazy z celowo wprowadzonymi błędami (jeżeli plik jest dostępny):
  python se/weryfikacja.py wiedza/kawa_z_bledami.json

W zadaniu Z3 wymagane jest wykrycie 10 problemów w kawa_z_bledami.json i 0 problemów w kawa.json. Wyniki tych testów należy potwierdzić rzeczywistym uruchomieniem programu.

W dotychczasowych testach pięć przykładowych przypadków wnioskowania w przód i wstecz zakończyło się poprawnie (5/5). Osobnej weryfikacji wymagają przypadki graniczne i konfliktowe oraz testy Z3.

8. MATERIAŁY Z1 I OGRANICZENIA
------------------------------
Plik wybor_laptopa.lrn zawiera 60 syntetycznych przykładów, pięć atrybutów wejściowych i jedną kolumnę wyjściową z 15 klasami. Kolumny oddzielone są tabulatorami; kodowanie: Windows-1250. Wnioski pośrednie nie są osobnymi kolumnami pliku LRN.

Konfiguracje sprzętu mają charakter orientacyjny. Przykłady uczące są syntetyczne, a system nie zastępuje porównania konkretnych modeli. Test w programie DeTreex nie został potwierdzony.
