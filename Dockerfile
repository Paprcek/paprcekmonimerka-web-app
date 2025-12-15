# 1. BASE IMAGE: Vycházíme z oficiálního, lehkého Python obrazu (vhodné pro Debian)
FROM python:3.11-slim

# 2. NASTAVENÍ: Vytvoříme pracovní adresář v kontejneru
WORKDIR /usr/src/app

# 3. KÓD: Zkopírujeme soubor se závislostmi (requirements.txt) a nainstalujeme je
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. KÓD: Zkopírujeme zbytek tvého kódu do kontejneru
COPY . /usr/src/app/

# 5. PŘÍKAZ: Definuje, co se spustí, když se kontejner spustí
# Tvá aplikace se spouští pomocí Gunicorn na portu 5000 (jako v tvém .service souboru)
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5001", "app:app"]
