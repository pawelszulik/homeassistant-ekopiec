# Integracja ekopiec dla Home Assistant

Integracja Home Assistant dla sterownika pieca eCoal (ekopiec) produkowanego przez eSterownik.pl.

## Funkcje

- **Czujniki temperatury**: Temperatura kotła, powrotu, CWU oraz obwodów grzewczych
- **Sterowanie klimatyzacją**: 6 obwodów grzewczych z możliwością ustawienia temperatury i trybu pracy
- **Przełączniki**: Sterowanie pompami, dmuchawą, zaworami i podajnikiem
- **Parametry numeryczne**: Ustawianie setpointów, czasów pracy, mocy dmuchawy z walidacją zakresów
- **Czujniki paliwa**: Poziom paliwa, czas pracy, data zasypania, zużycie
- **Alarmy**: 24 binarne czujniki alarmów systemowych
- **Filtrowanie encji**: Możliwość włączania/wyłączania kategorii encji w opcjach

## Instalacja

### Metoda 1: HACS (rekomendowana)

1. Zainstaluj [HACS](https://hacs.xyz/)
2. Przejdź do HACS → Integracje → Menu (⋮) → Custom repositories
3. Dodaj repozytorium: `https://github.com/pawelszulik/homeassistant-ekopiec`
4. Zainstaluj integrację "eCoal (ekopiec)"
5. Zrestartuj Home Assistant

### Metoda 2: Ręczna instalacja

1. Skopiuj folder `custom_components/ekopiec` do katalogu `custom_components` w Home Assistant
2. Zrestartuj Home Assistant
3. Przejdź do Ustawienia → Urządzenia i usługi → Dodaj integrację
4. Wyszukaj "ekopiec" i postępuj zgodnie z instrukcjami

## Konfiguracja

1. Przejdź do **Ustawienia** → **Urządzenia i usługi** → **Dodaj integrację**
2. Wyszukaj **"ekopiec"** lub **"eCoal"**
3. Wprowadź dane połączenia:
   - **Adres IP**: Adres IP sterownika eCoal
   - **Port**: Port HTTP (domyślnie 80)
   - **Nazwa użytkownika**: Login do sterownika
   - **Hasło**: Hasło do sterownika
4. Kliknij **Prześlij**

Integracja automatycznie wykryje urządzenie i utworzy wszystkie dostępne encje.

## Opcje konfiguracji

Po dodaniu integracji możesz skonfigurować, które kategorie encji mają być wyświetlane:

1. Przejdź do **Ustawienia** → **Urządzenia i usługi**
2. Znajdź integrację **ekopiec** i kliknij **Konfiguruj**
3. Wybierz kategorie encji:
   - **Pokaż czujniki temperatury** (11 sensorów)
   - **Pokaż obwody grzewcze** (6 obwodów)
   - **Pokaż parametry CWU** (7 sensorów)
   - **Pokaż sterowanie wyjściami** (8 przełączników)
   - **Pokaż zarządzanie paliwem** (7 sensorów)
   - **Pokaż stany alarmów** (24 sensory) - domyślnie wyłączone
   - **Pokaż parametry regulacyjne** (50+ liczb)

## Encje

### Czujniki (Sensors)

- Temperatury: kotła, powrotu, CWU, obwodów grzewczych
- Paliwo: poziom, czas pracy, data zasypania, zużycie, pozostało, dni do zasypania
- CWU: ciśnienie, poziom, czas pracy, tryb, status, temperatura min/max
- Informacje: wersja oprogramowania, wersja sprzętu, typ urządzenia

### Klimatyzacja (Climate)

- 6 obwodów grzewczych z możliwością:
  - Ustawienia temperatury docelowej
  - Wyboru trybu pracy (OFF, HEAT, AUTO)
  - Włączania/wyłączania

### Przełączniki (Switches)

- Pompy: kotła, CWU, obwodów grzewczych (1-4)
- Dmuchawa
- Zawory: mieszający, trójdrogowy
- Podajnik
- Zapalarka
- Wentylator

### Liczby (Numbers)

- Temperatury docelowe: kotła, CWU, obwodów (1-6)
- Moc dmuchawy: min, max, aktualna
- Czasy: podajnik (ON/OFF), rozpalanie, gaszenie
- Histereza

Wszystkie parametry mają walidację zakresów wartości.

### Binarne czujniki (Binary Sensors)

- Alarmy systemowe: przegrzanie, niska temperatura, brak paliwa, awarie pomp, dmuchawy, podajnika, zapalarki
- Błędy czujników: temperatury, ciśnienia
- Błędy komunikacji i zasilania
- Alarmy obwodów grzewczych (1-6)

## Wymagania

- Home Assistant 2023.1.0 lub nowszy
- Sterownik eCoal z dostępem przez HTTP
- Python 3.10+

## Wsparcie

W razie problemów:
1. Sprawdź logi Home Assistant pod kątem błędów
2. Upewnij się, że sterownik jest dostępny w sieci
3. Sprawdź poprawność danych logowania
4. Zgłoś problem w [repozytorium GitHub](https://github.com/pawelszulik/homeassistant-ekopiec)

## Licencja

MIT License

## Autor

Integracja stworzona dla sterowników eCoal produkowanych przez eSterownik.pl

