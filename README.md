# Integracja ekopiec dla Home Assistant

Integracja Home Assistant dla sterownika pieca eCoal (ekopiec) produkowanego przez eSterownik.pl.

## Funkcje

- **Czujniki temperatury**: Temperatura kotła, powrotu, CWU, podajnika, spalin
- **Tryby pracy**: Przełączanie między trybem zima/lato oraz auto/ręczny
- **Parametry regulatora**: Czasy pracy podajnika, moc dmuchawy, temperatura spalin
- **Parametry numeryczne**: Ustawianie setpointów, czasów pracy z walidacją zakresów (jako pola tekstowe)
- **Czujniki paliwa**: Poziom paliwa, czas pracy podajnika, daty zasypania
- **Status wyjść**: Monitoring stanu pomp, dmuchawy
- **Pozycja zaworu 4D**: Monitoring pozycji zaworu
- **Daty**: Aktualna data, ostatnia data zasypu, data kolejnego zasypu

## Instalacja

### Metoda 1: HACS (rekomendowana)

1. Zainstaluj [HACS](https://hacs.xyz/)
2. Przejdź do HACS → Integracje → Menu (⋮) → Custom repositories
3. Dodaj repozytorium: `https://github.com/pawelszulik/homeassistant-ekopiec`
4. Kategoria: `Integration`
5. Zainstaluj integrację "eCoal (ekopiec)"
6. Zrestartuj Home Assistant

### Metoda 2: Ręczna instalacja

Skopiuj zawartość tego repozytorium do katalogu `/config/custom_components` w Home Assistant:

```bash
cd /config/custom_components
rm -rf ekopiec
git clone https://github.com/pawelszulik/homeassistant-ekopiec
cp -r homeassistant-ekopiec/custom_components/ekopiec .
rm -rf homeassistant-ekopiec
```

Lub pobierz i wypakuj ręcznie:

1. Pobierz najnowszą wersję z [Releases](https://github.com/pawelszulik/homeassistant-ekopiec/releases)
2. Wypakuj archiwum
3. Skopiuj folder `custom_components/ekopiec` do katalogu `custom_components` w Home Assistant
4. Zrestartuj Home Assistant

## Konfiguracja

1. Przejdź do **Ustawienia** → **Urządzenia i usługi** → **Dodaj integrację**
2. Wyszukaj **"ekopiec"** lub **"eCoal"**
3. Wprowadź dane połączenia:
   - **Adres IP**: Adres IP sterownika eCoal
   - **Port**: Port HTTP (domyślnie 80)
   - **Nazwa użytkownika**: Login do sterownika
   - **Hasło**: Hasło do sterownika
4. Kliknij **Prześlij**

Integracja automatycznie utworzy wszystkie dostępne encje.

## Zarządzanie encjami

Wszystkie encje są tworzone automatycznie. Jeśli nie potrzebujesz niektórych encji:

1. Przejdź do **Ustawienia** → **Urządzenia i usługi**
2. Znajdź urządzenie **ekopiec**
3. Kliknij na encję którą chcesz wyłączyć
4. Kliknij ikonę ustawień (⚙️) → **Wyłącz encję**

## Encje

### Czujniki (Sensors)

**Temperatury:**
- `tkot_value` - Temperatura kotła
- `tpow_value` - Temperatura powrotu
- `tpod_value` - Temperatura podajnika
- `tcwu_value` - Temperatura CWU
- `tsp_value` - Temperatura spalin

**Dmuchawa:**
- `dm_rms` - Wartość skuteczna dmuchawy/nawiewnika
- `act_dm_speed` - Aktualna moc dmuchawy

**Parametry regulatora (tylko odczyt):**
- `rr_g_pod_off` - Czas postoju podajnika
- `rr_g_pod_on` - Czas pracy podajnika
- `rr_rsp_dm_speed` - Minimalna moc dmuchawy
- `rr_rsp_tmax` - Maksymalna temperatura spalin
- `rr_rsp_en` - Regulator temperatury spalin
- `rr_g_dm_speed` - Moc dmuchawy

**Temperatury zadane (tylko odczyt):**
- `kot_tzad` - Temperatura zadana kotła
- `cwu_tzad` - Temperatura zadana CWU
- `pomp_ton` - Temperatura załączenia pomp
- `tpow_min` - Minimalna temperatura powrotu

**Parametry podajnika (tylko odczyt):**
- `p_pod_on` - Czas pracy podajnika - Podtrzymanie
- `p_pod_off` - Czas postoju podajnika - Podtrzymanie
- `p_pod_wait` - Czas krótkiej przerwy - Podtrzymanie
- `p_pod_cnt` - Ilość powtórzeń - Podtrzymanie

**Tryby pracy (tylko odczyt):**
- `zima_lato` - Tryb Zima/Lato (0=zima, 1=lato)
- `tryb_auto_state` - Tryb Pracy (0=ręczny, 1=auto)

**Paliwo:**
- `fuel_level` - Poziom paliwa w zasobniku
- `pod_run_time_str` - Czas pracy podajnika

**Zawór:**
- `ob1_zaw4d_pos` - Pozycja zaworu 4D

**Daty:**
- `datetime` - Aktualna data ze sterownika
- `add_fuel_time` - Ostatnia data zasypu
- `next_fuel_time` - Data kolejnego zasypu

### Klimatyzacja (Climate)

### Przełączniki (Switches)

**Tryby pracy:**
- `zima_lato` - Tryb Zima/Lato (OFF=zima, ON=lato)
- `tryb_auto_state` - Tryb Pracy (OFF=ręczny, ON=auto)

### Liczby (Numbers)

Wszystkie parametry wyświetlane jako pola tekstowe do wpisania wartości:

**Temperatury docelowe:**
- `kot_tzad` - Temperatura zadana kotła (10-85°C)
- `cwu_tzad` - Temperatura zadana CWU (10-85°C)
- `pomp_ton` - Temperatura załączenia pomp (10-85°C)
- `tpow_min` - Minimalna temperatura powrotu (10-85°C)

**Parametry podajnika - Podtrzymanie:**
- `p_pod_on` - Czas pracy podajnika (1-300s)
- `p_pod_off` - Czas postoju podajnika (1-3600s)
- `p_pod_wait` - Czas krótkiej przerwy (1-300s)
- `p_pod_cnt` - Ilość powtórzeń (1-20)

**Parametry regulatora:**
- `rr_g_pod_off` - Czas postoju podajnika (0-300s)
- `rr_g_pod_on` - Czas pracy podajnika (0-300s)
- `rr_rsp_dm_speed` - Minimalna moc dmuchawy (0-300)
- `rr_rsp_tmax` - Maksymalna temperatura spalin (0-300°C)
- `rr_rsp_en` - Regulator temperatury spalin (0-1)
- `rr_g_dm_speed` - Moc dmuchawy (0-300)

### Binarne czujniki (Binary Sensors)

**Status wyjść (tylko odczyt):**
- `out_pomp1` - Pompa 1
- `out_cwu` - Pompa CWU
- `out_miesz` - Pompa dodatkowa
- `out_dm` - Dmuchawa


## Wymagania

- Home Assistant 2023.1.0 lub nowszy
- Sterownik eCoal z dostępem przez HTTP
- Python 3.10+

## ⚠️ Ważne zmiany w wersji 1.0.0+

Z integracji zostały **usunięte** następujące elementy w celu uproszczenia:

- ❌ **Wszystkie alarmy (24 czujniki binarne)** - Alarmy kotła, paliwa, CWU, urządzeń, czujników i systemu
- ❌ **Regulatory temperatury (Climate)** - Obwody grzewcze 1-6

✅ **Pozostałe funkcje działają normalnie**: temperatury, parametry, wyjścia, tryby pracy, pozycja zaworu 4D.

## Rozwiązywanie problemów

Szczegółowe informacje znajdziesz w [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

W razie problemów:
1. Sprawdź logi Home Assistant: **Ustawienia** → **System** → **Logi**
2. Upewnij się, że sterownik jest dostępny w sieci
3. Sprawdź poprawność danych logowania
4. Sprawdź czy port 80 nie jest blokowany przez firewall
5. Zgłoś problem w [Issues](https://github.com/pawelszulik/homeassistant-ekopiec/issues)

## Dokumentacja

- [Instalacja](INSTALLATION.md) - Szczegółowa instrukcja instalacji
- [Encje](ENTITIES.md) - Pełna lista dostępnych encji
- [Rozwiązywanie problemów](TROUBLESHOOTING.md) - Pomoc przy problemach

## Wsparcie projektu

Jeśli integracja jest dla Ciebie przydatna:
- ⭐ Zostaw gwiazdkę na GitHub
- 🐛 Zgłaszaj błędy w Issues
- 💡 Proponuj nowe funkcje
- 🔧 Twórz Pull Requesty

## Licencja

MIT License - Zobacz [LICENSE](LICENSE)

## Autor

Integracja stworzona dla sterowników eCoal produkowanych przez [eSterownik.pl](https://esterownik.pl)

---

**Uwaga**: To nieoficjalna integracja stworzona przez społeczność. Nie jest powiązana z producentem sterowników eCoal.
