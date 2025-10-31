# GrowList - Aplikacja Todo Flask

Prosta aplikacja do zarządzania zadaniami z elementami gamifikacji

## Link do działającej wersji

## Uwagi dotyczące przeglądarki

Aplikację najlepiej testować w Firefox – ta przeglądarka była używana podczas developmentu, więc nie powinno być problemów z wyświetlaniem ani działaniem funkcji

## Funkcjonalności

- Dodawanie, edytowanie i usuwanie zadań
- Powiadomienia mailowe przypominające o deadlinach
- Podział zadań na listy
- Kalendarz
- Gamifikacja - hodowanie roślinki

## Ścieżki testowe

W pliku `test.py` znajdują się testowe ścieżki do symulacji działania aplikacji:

- `/test_1_day`, `/test_2_days`, `/test_3_days`, `/test_4_days` – symulacja usychania roślinki po x dniach i wysyłania powiadomień o jej stanie
- `/run_reminders` – wysyłanie powiadomień dotyczących deadlinów zadań (dotyczy zadań, które mają deadline za max 24h)
- `/reset_daily_tasks` – resetowanie liczby zadań wykonanych w ciągu dnia

> Na potrzeby testów w pliku `scheduler.py`, w funkcji `update_plant_health_status`, zakomentowany jest fragment kodu sprawdzający liczbę zadań wykonanych poprzedniego dnia. Zamiast tego wartość ustawiona jest na 0, aby testowe ścieżki do symulacji usychania rośliny zawsze działały.
