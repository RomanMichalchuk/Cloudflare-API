# Cloudflare-API
Скрипт на Python для массового обновления данных по API Cloudflare

Этот скрипт позволяет массово управлять настройками доменов в Cloudflare с использованием API, включая параметры IPv6, Always Use HTTPS, TLS 1.3, режима "Under Attack", ECH и очистки кэша.

## Скриншот интерфейса

![Скриншот интерфейса](ECH.jpg)

## Установка и подготовка

### Шаг 1: Установка Python и необходимых библиотек

1. Убедитесь, что у вас установлен **Python 3.7+**. Если Python ещё не установлен, скачайте и установите его с официального сайта [python.org](https://www.python.org/downloads/).
2. Установите необходимые библиотеки, выполнив следующую команду в терминале:

    ```bash
    pip install pandas aiohttp openpyxl
    ```

### Шаг 2: Подготовка данных в Excel

Создайте файл `cloudflare_accounts.xlsx` со следующими колонками:
- **Domain**: Доменное имя, для которого будут изменяться настройки.
- **API_Token**: Токен доступа для Cloudflare API.
- **Zone_ID**: Идентификатор зоны Cloudflare для данного домена.
- **Email**: Email аккаунта Cloudflare (некоторые настройки требуют аутентификации с Email и API Token).

Каждая строка файла должна содержать информацию для одного домена. Убедитесь, что все данные заполнены корректно.

### Шаг 3: Запуск скрипта

Сохраните код скрипта в файл, например, `Cloudflare-API.py`, и запустите его:

```bash
python Cloudflare-API.py
```

## Использование интерфейса

1. **Ввод доменов**: В главном окне скрипта введите список доменов, каждый с новой строки.

2. **Настройка параметров**:
    - **IPv6**: Включает или отключает поддержку IPv6.
    - **Always Use HTTPS**: Включает принудительное использование HTTPS.
    - **TLS 1.3**: Отключает поддержку TLS 1.3, который может быть заблокирован в некоторых регионах.
    - **Under Attack Mode**: Включает режим "Под атакой" для защиты от ДДОС-атак.
    - **Очистка кеша**: Полностью очищает кэш Cloudflare для выбранных доменов.

3. **Выбор опций**:
    - Выберите нужные параметры для применения, установив галочки возле них.
    - Можно выбрать все параметры сразу, установив флажок "Выбрать все".

4. **Применение настроек**:
    - Нажмите на кнопку **"Применить выбранное"**. Скрипт выполнит изменения для всех указанных доменов, а результат будет отображён в окне прогресса.
    - После завершения появится уведомление о выполнении операций.

## Примечания

- Скрипт использует **асинхронные задачи** для ускорения выполнения и предотвращения перегрузки сервера.
- **Лимит одновременных задач** составляет 5, что можно изменить, отредактировав переменную `MAX_CONCURRENT_TASKS`.
- Все изменения записываются в консоль, где отображается статус выполнения по каждому домену.

Скрипт создан для удобного и быстрого управления массовыми настройками доменов через Cloudflare API.

## Пример данных в Excel

| Domain         | API_Token             | Zone_ID              | Email                  |
|----------------|-----------------------|----------------------|------------------------|
| example1.com   | your_api_token_here   | your_zone_id_here    | your_email@example.com |
| example2.com   | another_api_token_here| another_zone_id_here | another_email@example.com |

Сохраните файл как `cloudflare_accounts.xlsx` и поместите его в ту же директорию, что и скрипт.

## Результат выполнения скрипта

![Скриншот интерфейса](Cloudflare-API-result.jpg)

## Поддержка

Если у вас есть вопросы или предложения по улучшению скрипта, создайте новый Issue в репозитории. Мы рады вашим отзывам!
