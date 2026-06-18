# mywebapp - Simple Inventory (Лабораторні роботи №1-3)

**Виконав:** студент групи ІМ-43, Іщук Володимир Володимирович (ФІОТ, кафедра ОТ)

Лабораторна робота з автоматизованого розгортання веб-сервісу обліку обладнання (Simple Inventory). Цей репозиторій містить етапи розвитку проєкту від базового застосунку до контейнеризації та CI/CD пайплайнів.

## Опис проєкту
Веб-сервіс для обліку ІТ-обладнання (інвентаризація). Стек технологій включає:
* **Backend:** Python 3, Flask, Gunicorn
* **Database:** PostgreSQL (чисті SQL-запити без ORM)
* **Web Server & Reverse Proxy:** Nginx
* **Process Manager:** Systemd з підтримкою Socket Activation
* **Automation & CI/CD:** Bash-скрипти, Docker, Docker Compose, GitHub Actions

## Розрахунок варіанту
* **Номер варіанту:** 26
* **Відповідно до вимог варіанту:**
  * Веб-застосунок налаштовує з'єднання з базою даних через CLI-аргументи.
  * Номер варіанту (26) автоматично записується скриптом автоматизації у файл `/home/student/gradebook`.
  * Реалізовано Systemd Socket Activation на порті 5200.

## Інструкція локального запуску застосунку

### 1. Підготовка бази даних
Переконайтеся, що PostgreSQL запущено та створено необхідну БД та користувача:
    CREATE DATABASE inventory_db;
    CREATE USER app_user WITH PASSWORD 'app_password';
    GRANT ALL PRIVILEGES ON DATABASE inventory_db TO app_user;

### 2. Створення віртуального середовища
    python3 -m venv .venv
    # Для Linux/macOS:
    source .venv/bin/activate
    # Для Windows (PowerShell):
    .venv\Scripts\Activate.ps1

### 3. Встановлення залежностей
    pip install -r requirements.txt

### 4. Виконання міграції бази даних
Запустіть скрипт міграції для створення необхідних таблиць:
    python app/migrate.py --db-host 127.0.0.1 --db-user app_user --db-password app_password --db-name inventory_db

### 5. Запуск веб-застосунку
    python app/app.py --port 5200 --db-host 127.0.0.1 --db-user app_user --db-password app_password --db-name inventory_db

Застосунок буде доступний за адресою: http://127.0.0.1:5200.

## Вимоги до віртуальної машини та ОС (Лабораторна 2)
* **Базовий образ:** Офіційний образ Ubuntu Server 22.04 LTS.
* **Мінімальні ресурси:** 1 CPU, 1-2 GB RAM, 10-15 GB Disk.
* **Особливості встановлення:** Обов'язкове встановлення OpenSSH server для віддаленого доступу. Вхід здійснюється через створеного користувача student.

## Інструкція запуску deploy.sh на віртуальній машині
1. Перенесіть папку з проєктом mywebapp на цільову віртуальну машину (через scp або git).
2. Перейдіть у папку проєкту та запустіть скрипт розгортання від імені суперкористувача root:
    cd mywebapp
    chmod +x deploy/deploy.sh
    sudo ./deploy/deploy.sh

3. Після успішного завершення скрипту перевірте стан сокета та Nginx:
    systemctl status mywebapp.socket
    systemctl status nginx

4. Тестування роботи API (через Nginx порт 80):
    curl http://localhost/
    # Додавання нового предмету
    curl -X POST -H "Content-Type: application/json" -d '{"name": "Server Dell R740", "quantity": 3}' http://localhost/items
    # Перевірка блокування сторонніх шляхів (має повернути HTTP 403 Forbidden):
    curl http://localhost/health/alive
    curl http://localhost/health/ready

## Запуск за допомогою Docker Compose (Лабораторна 3)
Для зручного розгортання всього стеку застосунку (База даних PostgreSQL, Flask веб-додаток та веб-сервер Nginx) використовується Docker Compose.

1. Запуск системи у фоновому режимі (detached mode):
    docker compose up -d --build

2. Перегляд логів сервісів у реальному часі:
    docker compose logs -f

3. Зупинка системи та видалення контейнерів (дані бази даних при цьому зберігаються завдяки named volume db_data):
    docker compose down