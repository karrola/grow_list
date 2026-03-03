# GrowList - Aplikacja Todo

Prosta aplikacja do zarządzania zadaniami z elementami gamifikacji.

## Technologie

Python, Flask, SQLAlchemy, HTML5, CSS3

## Funkcjonalności

- Dodawanie, edytowanie i usuwanie zadań
- Powiadomienia mailowe przypominające o deadlinach
- Podział zadań na listy
- Kalendarz
- Gamifikacja - hodowanie roślinki

## Link do działającej wersji

https://grow-list.onrender.com

## Instrukcja uruchomienia lokalnie:

1. Sklonuj repozytorium
2. (zalecane) Stwórz wirtualne środowisko
3. Zainstaluj zależności
   ```
   pip install -r requirements.txt
   ```
4. Na podstawie .env.example przygotuj przygotuj plik .env
5. Wykonaj migracje bazy danych
   ```
   flask db upgrade
   ```
6. Uruchom serwer deweloperski

   ```
   flask run
   ```

   Aplikacja będzie dostępna pod adresem http://127.0.0.1:5000/.

## Uwagi dotyczące przeglądarki

Aplikację najlepiej testować w Firefox – ta przeglądarka była używana podczas developmentu, więc nie powinno być problemów z wyświetlaniem ani działaniem funkcji.

## Ścieżki testowe

W pliku `test.py` znajdują się testowe ścieżki do symulacji działania aplikacji:

- `/test_1_day`, `/test_2_days`, `/test_3_days`, `/test_4_days` – symulacja usychania roślinki po x dniach i wysyłania powiadomień o jej stanie
- `/run_reminders` – wysyłanie powiadomień dotyczących deadlinów zadań (dotyczy zadań, które mają deadline za max 24h)
- `/reset_daily_tasks` – resetowanie liczby zadań wykonanych w ciągu dnia

> Na potrzeby testów w pliku `scheduler.py`, w funkcji `update_plant_health_status`, zakomentowany jest fragment kodu sprawdzający liczbę zadań wykonanych poprzedniego dnia. Zamiast tego wartość ustawiona jest na 0, aby testowe ścieżki do symulacji usychania rośliny zawsze działały.

## Uwaga dot. powiadomień

Aplikacja jest przygotowana do wysyłania powiadomień e-mail, jednak w środowisku produkcyjnym Render outbound SMTP jest zablokowany. Z tego powodu na renderze wywołania funkcji `send_email` są obecnie symulowane (logowane w konsoli).

W trybie lokalnym po skonfigurowaniu zmiennych środowiskowych
`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER` itp. — maile wysyłane są poprawnie.
