# Утилита TgSafeBox

Утилита TgSafeBox предназначена для управления загрузкой файлов, их скачиванием и извлечением информации с использованием Telegram в качестве облачного хранилища. Она предлагает функции шифрования и надежного управления файлами.

## Особенности

-   **Безопасность**: Шифрует файлы перед загрузкой на Telegram.
-   **Отсутствие Лимитов**: Эффективно обрабатывает большие файлы, разделяя их на части, благодоря чему обходит ограничения Telegram.
-   **Целостность Файлов**: Обеспечивает целостность данных и надежность во время загрузки и скачивания.
-   **Интеграция с Telegram**: Использует Telegram в качестве безопасного облачного хранилища.
-   **Кроссплатформенность**: Сохраняет пути файлов и директорий в виде массивов.

## Предварительные требования

-   Python 3.11.9 или выше (Возможно будет работать и с версиями ниже)
-   Необходимые пакеты Python можно установить с помощью `pip install -r requirements.txt`

## Установка

`git clone https://github.com/Syn3xuS/TgSafeBox`

`cd TgSafeBox`

`pip install -r requirements.txt`

`python setup.py install`

## Использование

### Команды

-   `client list`

    Выводит список клиентов в формате:

        <client_number> - <id> - <hash>

-   `client add <id> <hash>`

    -   Инициализирует клиент Telegram с указанными API ключами.
    -   api_id и api_hash брать -> [тут](https://my.telegram.org/auth)
    -   Никому не передавайте ваши api_id и api_hash

-   `client del <number>`

    -   Удаляет клиент из списка

-   `upload <client_number> <chat_id> <box_name> <file_or_directory_paths>`

    -   `-af` - флаг для указания файла с описанием. (Необязателен)

    -   Загружает указанные файлы или директории в чат Telegram.

-   `download <client_number> <box_name> <output_directory>`

    -   `-o` - флаг для указания выходной директории (Необязателен)

    -   Скачивает файлы из чата Telegram с использованием указанного конфигурационного файла.

-   `info <box_name>`

    -   Получает подробную информацию о сконфигурированной 'коробке' (tsb файл).

-   `-h`, `-help`

    -   Отображает справочную информацию.

### Примеры Использования

`tgsafebox client list`

`tgsafebox client add 123456789 abcdef1234567890abcdef1234567890`

`tgsafebox client del 1`

`tgsafebox upload 1 -100987654321 BoxName /путь/к/файл1.txt /путь/к/директория1 /путь/к/файл2.jpg`

`tgsafebox upload 1 -100987654321 BoxName /путь/к/файл1.txt /путь/к/директория1 /путь/к/файл2.jpg -af ./MyTexts/aboutforbox1.txt`

`tgsafebox download 1 ./myboxs/Box1.tsb`

`tgsafebox download 1 ./myboxs/Box1.tsb -o /выходная/директория`

`tgsafebox info ./myboxs/Box1.tsb`


## Автор

-   [Syn3xuS](https://t.me/Syn3xuS)
