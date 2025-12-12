# 1. BASE IMAGE
FROM python:3.11-slim

# 2. NASTAVENÍ: Pracovní adresář v kontejneru
WORKDIR /usr/src/app

# 3. KÓD: Kopíruje závislosti a instaluje je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. KÓD: Zkopírujeme celý kód aplikace
COPY . /usr/src/app/

# 5. PŘÍKAZ: Spustíme Django přes Gunicorn na portu 5002
# paprcek_hra je název tvého hlavního settings modulu
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5002", "paprcek_hra.wsgi:application"]
