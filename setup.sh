#!/bin/bash


if [ "$EUID" -ne 0 ]; then
  echo "Будь ласка, запустіть скрипт з sudo (наприклад: sudo ./setup.sh)"
  exit
fi

echo "1. Оновлення пакетів та встановлення залежностей..."
apt update
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl sudo

echo "2. Створення користувачів..."
# Користувач student
useradd -m -s /bin/bash -G sudo student
echo "student:student123" | chpasswd # Тимчасовий пароль для входу


useradd -m -s /bin/bash -G sudo teacher
echo "teacher:12345678" | chpasswd
chage -d 0 teacher


useradd -r -s /bin/false app

# Користувач operator з обмеженими правами
useradd -m -s /bin/bash operator
echo "operator:12345678" | chpasswd
chage -d 0 operator


cat <<EOF > /etc/sudoers.d/operator
operator ALL=(ALL) NOPASSWD: /usr/bin/systemctl start mywebapp.service, /usr/bin/systemctl stop mywebapp.service, /usr/bin/systemctl restart mywebapp.service, /usr/bin/systemctl status mywebapp.service, /usr/bin/systemctl reload nginx
EOF
chmod 440 /etc/sudoers.d/operator

echo "3. Налаштування PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE inventory_db;"
sudo -u postgres psql -c "CREATE USER app WITH PASSWORD '123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory_db TO app;"
sudo -u postgres psql -d inventory_db -c "GRANT ALL ON SCHEMA public TO app;"

echo "4. Копіювання файлів та розгортання застосунку..."
mkdir -p /opt/mywebapp
mkdir -p /etc/mywebapp


cp app.py migrate.py requirements.txt /opt/mywebapp/
cp config.json /etc/mywebapp/
cp mywebapp.service /opt/mywebapp/
cp mywebapp.conf /opt/mywebapp/

# Встановлюємо правильні права
chown -R app:app /opt/mywebapp
chown -R app:app /etc/mywebapp

python3 -m venv /opt/mywebapp/venv
/opt/mywebapp/venv/bin/pip install -r /opt/mywebapp/requirements.txt


sed -i 's|/usr/bin/python3|/opt/mywebapp/venv/bin/python|g' /opt/mywebapp/mywebapp.service

echo "5. Налаштування systemd для застосунку..."
cp /opt/mywebapp/mywebapp.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable mywebapp.service
systemctl start mywebapp.service

echo "6. Налаштування Nginx..."
cp /opt/mywebapp/mywebapp.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/mywebapp.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

echo "7. Створення gradebook..."
echo "11" > /home/student/gradebook
chown student:student /home/student/gradebook

echo "8. Блокування дефолтного користувача..."

if [ -n "$SUDO_USER" ]; then
    usermod -L "$SUDO_USER"
    echo "Користувач $SUDO_USER успішно заблокований."
else
    echo "Не вдалося визначити дефолтного користувача."
fi

echo "✅ Встановлення завершено успішно! Сервіс працює."