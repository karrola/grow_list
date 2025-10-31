# GrowList - Aplikacja Todo Flask

Prosta aplikacja do zarządzania zadaniami z elementami gamifikacji.

## Link do działającej wersji

https://grow-list.onrender.com

## Uwagi dotyczące przeglądarki

Aplikację najlepiej testować w Firefox – ta przeglądarka była używana podczas developmentu, więc nie powinno być problemów z wyświetlaniem ani działaniem funkcji.

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

## Uwaga dot. powiadomień

Aplikacja jest przygotowana do wysyłania powiadomień e-mail, jednak w środowisku produkcyjnym Render outbound SMTP jest zablokowany. Z tego powodu funkcja wysyłania maili została tymczasowo wyłączona.

W trybie lokalnym (np. `flask run`) po skonfigurowaniu zmiennych środowiskowych
`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER` itp. — maile wysyłane są poprawnie.

Na Renderze wywołania funkcji `send_email` są obecnie symulowane (logowane w konsoli).
