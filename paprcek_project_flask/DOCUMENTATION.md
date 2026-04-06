# Paprcek Monimerka - Flask Aplikace Dokumentace

## 📋 Obsah

1. [Architektura](#architektura)
2. [Struktura projektu](#struktura-projektu)
3. [Blueprinty](#blueprinty)
4. [Konfigurace](#konfigurace)
5. [Extensions (Rozšíření)](#extensions-rozšíření)
6. [Spuštění a nasazení](#spuštění-a-nasazení)
7. [Překlad (i18n)](#překlad-i18n)

---

## Architektura

Projekt Paprcek Monimerka je modulární Flask aplikace postavená na principu **Blueprintů** a **Factory Patteru**. Tato architektura zajišťuje:

✅ **Modularitu** - Oddělení jednotlivých funkcí do logických celků
✅ **Škálovatelnost** - Jednoduché přidání nových featur bez ovlivnění existujícího kódu
✅ **Testovatelnost** - Snadné vytváření a testování jednotlivých komponent
✅ **Údržbovatelnost** - Jasná struktura a separace concerns

### Design Principy

```
┌─────────────────────────────────────────────────┐
│         app.py (Hlavní vstupní bod)             │
│  - Inicializace Flask aplikace                  │
│  - Registrace blueprintů                        │
│  - Globální context processory                  │
└──────────────┬──────────────────────────────────┘
               │
       ┌───────┴─────────┐
       ▼                 ▼
   ┌────────┐      ┌──────────┐
   │Extensions    │  Config   │
   │ (Mail)  │    │ (.env)    │
   └────────┘     └──────────┘
       ▲                △
       │                │
   ┌───┴────────────────┴────┐
   │   Blueprinty            │
   ├─────────────────────────┤
   │ • core_bp               │
   │   - Základní routes     │
   │   - Překlad jazyků      │
   │                         │
   │ • projects_bp           │
   │   - Specialní projekty  │
   │   - API integraci       │
   └─────────────────────────┘
```

---

## Struktura Projektu

### Adresářová struktura

```
paprcek_project_flask/
│
├── app.py                          # Hlavní vstupní bod aplikace
├── config.py                       # Centrální konfigurace
├── extensions.py                   # Inicializace rozšíření (Mail, DB, atd.)
│
├── modules/                        # Blueprinty
│   ├── __init__.py
│   ├── core.py                     # Základní blueprint (index, about, kontakty...)
│   └── projects.py                 # Blueprint projektů (watchdog, kvalita vzduchu...)
│
├── templates/                      # HTML šablony
│   ├── base.html                   # Základní šablona
│   ├── index.html                  # Domovská stránka
│   ├── about.html                  # O nás
│   ├── contacts.html               # Kontaktní formulář
│   ├── gdpr.html                   # GDPR informace
│   ├── air_quality.html            # Kvalita vzduchu
│   ├── history.html                # Historie kvality vzduchu
│   ├── binary.html                 # Binární překladač
│   ├── watchdog.html               # Watchdog - představení
│   └── watchdog_landing.html       # Watchdog - landing page
│
├── static/                         # Statické soubory
│   ├── css/                        # Stylové soubory
│   └── images/                     # Obrázky
│
├── translations.json               # Jazykové překlady (CS, EN)
├── requirements.txt                # Python závislosti
├── Dockerfile                      # Docker konfigurace
├── .env                            # Proměnné prostředí (gitignore)
└── DOCUMENTATION.md                # Tato dokumentace
```

### Sociální struktura

```
app.py
  ├── Importuje extensions.py (Mail)
  ├── Importuje config.py (Config)
  ├── Importuje modules/core.py (core_bp)
  └── Importuje modules/projects.py (projects_bp)

modules/core.py
  └── Importuje extensions.py (Mail)

modules/projects.py
  ├── Importuje extensions.py (Mail)
  └── Importuje current_app pro přístup k config
```

---

## Blueprinty

### Co je to Blueprint?

Blueprint je Flask objekt, který reprezentuje podmnožinu operací, které lze zaregistrovat v aplikaci. Umožňuje organizaci kódu do logických skupin, které lze pak zaregistrovat v hlavní aplikaci.

### 1. Core Blueprint (`modules/core.py`)

#### Účel

Core blueprint obsahuje základní a universální funkce aplikace, které jsou dostupné pro všechny uživatele.

#### Registrovaný Blueprint Prefix

```python
core_bp = Blueprint('core', __name__)
```

Žádný URL prefix - routes jsou dostupné v root cesty aplikace.

#### Trasy a jejich funkce

| Cesta | Metoda | Funkce | Popis |
|-------|--------|--------|-------|
| `/` | GET | `index()` | Domovská stránka s přehledem projektů |
| `/about` | GET | `about()` | Stránka O nás |
| `/gdpr` | GET | `gdpr()` | GDPR a ochrana dat |
| `/contacts` | GET, POST | `contacts()` | Kontaktní formulář |
| `/lang/<language>` | GET | `set_language()` | Přepínání jazyka (cs/en) |

#### Příklad použití v šablonách

```html
<!-- Odkaz na domovskou stránku -->
<a href="{{ url_for('core.index') }}">Domů</a>

<!-- Odkaz na kontakty -->
<a href="{{ url_for('core.contacts') }}">Kontakty</a>

<!-- Přepnutí na angličtinu -->
<a href="{{ url_for('core.set_language', language='en') }}">English</a>
```

#### Implementované funkce

**`contacts()` - Kontaktní formulář**
- Zpracovává POST požadavky z kontaktního formuláře
- Ověřuje GDPR souhlas uživatele
- Odesílá emaily přes Flask-Mail
- Vrací flash zprávu se statusem

```python
@core_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        # Validace GDPR souhlasu
        # Sebrání dat z formuláře
        # Zaslání emailu
        # Flash zpráva uživateli
    return render_template('contacts.html')
```

**`set_language()` - Přepínání jazyka**
- Nastaví vybraný jazyk do session
- Přesměruje zpět na předchozí stránku
- Zajišťuje persistenci jazyka během relace

```python
@core_bp.route('/lang/<language>')
def set_language(language):
    session['language'] = language
    session.modified = True
    return redirect(request.referrer or url_for('core.index'))
```

---

### 2. Projects Blueprint (`modules/projects.py`)

#### Účel

Projects blueprint obsahuje všechny speciální projekty a nástroje dostupné na webu. Modul je zodpovědný za integraci externích API a komplexnější business logiku.

#### Registrovaný Blueprint Prefix

```python
projects_bp = Blueprint('projects', __name__)
```

Bez URL prefixu - trasy jsou dostupné na `/`.

#### Trasy a jejich funkce

| Cesta | Metoda | Funkce | Popis |
|-------|--------|--------|-------|
| `/watchdog` | GET | `watchdog()` | Představení Watchdog služby |
| `/monitoring-eshopu` | GET | `watchdog_sales()` | Watchdog landing page |
| `/watchdog-order` | POST | `watchdog_order()` | Objednání Watchdog služby |
| `/air_quality` | GET | `air_quality()` | Aktuální kvalita vzduchu |
| `/air_history` | GET | `air_history()` | Historie kvality vzduchu (graf) |
| `/binary-translator` | GET, POST | `binary_translator()` | Text-to-Binary překladač |
| `/vysilacky-shoptet-feed.xml` | GET | `serve_shoptet_feed()` | XML feed |

#### Příklad použití v šablonách

```html
<!-- Odkaz na kvalitu vzduchu -->
<a href="{{ url_for('projects.air_quality') }}">Kvalita vzduchu</a>

<!-- Odkaz na watchdog -->
<a href="{{ url_for('projects.watchdog') }}">Watchdog</a>

<!-- Formulář pro objednávku -->
<form action="{{ url_for('projects.watchdog_order') }}" method="POST">
    <!-- Pole formuláře -->
</form>
```

#### Implementované funkce

**`air_quality()` - Kvalita vzduchu**
- Volá OpenWeather API pro aktuální data
- Parsuje AQI (Air Quality Index) a PM2.5 koncertaci
- Mapuje numerické hodnoty na lidsky čitelné status
- Ošetřuje chyby API s fallback zprávou

```python
@projects_bp.route('/air_quality')
def air_quality():
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    # Volání API
    # Parsování dat
    # Mapování statusu
    return render_template('air_quality.html', data=..., status_key=...)
```

**`air_history()` - Historie kvality vzduchu**
- Volá OpenWeather API pro historická data (posledních 72 hodin)
- Formátuje data do grafu
- Extrahuje časové štítky a hodnoty
- Vrací data ve formátu vhodném pro Chart.js

```python
@projects_bp.route('/air_history')
def air_history():
    # Výpočet časových razítek
    # Volání historického API
    # Formátování pro graf
    return render_template('history.html', labels=..., aqi_values=..., pm25_values=...)
```

**`watchdog_order()` - Objednávka Watchdog**
- Zpracovává POST požadavky z objednávkového formuláře
- Zvaliduje vstupní data
- Odesílá email s poptávkou
- Vrací redirect s status zprávou

```python
@projects_bp.route('/watchdog-order', methods=['POST'])
def watchdog_order():
    # Sebrání dat z formuláře
    # Vytvoření emailu
    # Zaslání emailu
    # Redirect s notifikací
```

**`binary_translator()` - Binární překladač**
- Převádí text na binární reprezentaci
- Jedna fyzická funkce pro obsluhu GET a POST
- Zobrazuje výsledek v textové oblasti
- Umožňuje editaci vstupního textu

```python
@projects_bp.route('/binary-translator', methods=['GET', 'POST'])
def binary_translator():
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        result = text_to_binary(input_text)
    return render_template('binary.html', result=result, input_text=input_text)
```

---

## Konfigurace

### config.py - Centrální správa konfigurace

Všechna nastavení aplikace jsou centralizována v jednom souboru `config.py`, což usnadňuje údržbu a umožňuje snadné přidání nových konfigurací.

#### Struktura konfigurace

```python
import os
import datetime

class Config:
    # Bezpečnost
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_fallback_secret_key")

    # API klíče
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

    # Sentry (Error tracking)
    SENTRY_DSN = os.getenv('SENTRY_DSN')

    # Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'paprcekmonimerka@gmail.com'
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = 'paprcekmonimerka@gmail.com'

    # Session
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)
```

#### Proměnné prostředí (.env)

```bash
# Bezpečnost
FLASK_SECRET_KEY=your-secret-key-here

# API
OPENWEATHER_API_KEY=your-openweather-key

# Email
MAIL_PASSWORD=your-gmail-password

# Error Tracking
SENTRY_DSN=your-sentry-dsn
```

#### Jak se konfigurace používá v aplikaci

```python
# V app.py
app.config.from_object(Config)

# V blueprintech
api_key = current_app.config.get('OPENWEATHER_API_KEY')
```

#### Best Practices

1. **Nikdy** neukládejte tajné údaje přímo v kódu
2. Používejte `.env` soubor pro lokální vývoj
3. V produkci nastavte proměnné prostředí ve vývojovém prostředí
4. Používejte `os.getenv()` s výchozími hodnotami pro volitelné klíče
5. Všechny nové konfigurace přidejte do `config.py`

---

## Extensions (Rozšíření)

### extensions.py - Inicializace rozšíření

Rozšíření jsou Flask pluginy, které přidávají funkcionalitu. Aby se zabránilo kruhových importů (circular imports), Jsou všechna rozšíření inicializována v samostatném souboru `extensions.py`.

#### Struktura extensions.py

```python
from flask_mail import Mail

mail = Mail()
```

**Proč takto?**

1. **Circular Import Prevention** - Blueprinty a app.py neimportují jeden druhého
2. **Separace Concerns** - Inicializace rozšíření je oddělena od logiky
3. **Testovatelnost** - Snazší mockování v testech
4. **Reusability** - Rozšíření lze snadno přidat do více aplikací

#### Dependency Graph

```
extensions.py
    ↑
    │ (import)
    ├─── modules/core.py
    ├─── modules/projects.py
    └─── app.py
```

**Pohled zezadu:**
- `extensions.py` **se neimportuje z ničeho** (je na vrcholu hiearchie)
- Vše ostatní jej importuje

### Flask-Mail Setup

#### Inicializace v app.py

```python
import os
import json
import datetime
from flask import Flask, render_template, request, g, session
from config import Config
from extensions import mail
from modules.core import core_bp
from modules.projects import projects_bp
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# 1. Inicializace Sentry (Error tracking)
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

# 2. Vytvoření Flask aplikace
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-pro-lokalni-vyvoj")
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 dní

# 3. Inicializace Extensions
mail.init_app(app)

# 4. Načtení a příprava překladů
def load_translations():
    path = os.path.join(app.root_path, 'translations.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Chyba při načítání překladů: {e}")
        return {}

ALL_TRANSLATIONS = load_translations()

# 5. Before Request Handler
@app.before_request
def before_request():
    lang = session.get('language', 'cs')
    g.lang = lang
    g.T = ALL_TRANSLATIONS.get(lang, ALL_TRANSLATIONS.get('cs', {}))

# 6. Context Processor pro globální dostupnost funkcí
@app.context_processor
def inject_global_vars():
    def _(key):
        return g.T.get(key, key)
    
    return {
        'dt': datetime,
        'now': datetime.datetime.now,
        '_': _,
        'current_language': g.lang
    }

# 7. Registrace Blueprintů
app.register_blueprint(core_bp)
app.register_blueprint(projects_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
```

#### Použití v blueprintech

```python
from extensions import mail
from flask_mail import Message

@core_bp.route('/contacts', methods=['POST'])
def contacts():
    msg = Message(
        subject="Nová zpráva",
        recipients=['recipient@example.com'],
        body="Obsah zprávy"
    )
    mail.send(msg)
    return "OK"
```

#### Konfigurace SMTP

Gmail SMTP nastavení (z config.py):
- Server: `smtp.gmail.com`
- Port: `587` (TLS)
- Uživatel: `paprcekmonimerka@gmail.com`
- Heslo: Z proměnné prostředí `MAIL_PASSWORD`

**Poznámka:** Pro Gmail je třeba povolit "Méně bezpečné aplikace" v nastavení účtu.

---

## Spuštění a Nasazení

### Lokální vývoj

```bash
# 1. Aktivujte virtuální prostředí
source venv/bin/activate

# 2. Nainstalujte závislosti
pip install -r requirements.txt

# 3. Nastavte proměnné prostředí
export FLASK_ENV=development
export FLASK_SECRET_KEY=your-secret-key
export OPENWEATHER_API_KEY=your-api-key
# ... ostatní klíče

# 4. Spusťte aplikaci
python app.py
```

### Docker nasazení

```bash
# Vytvořte image
docker build -t paprcek-monimerka:latest .

# Spusťte kontejner
docker run -p 5001:5001 \
  -e FLASK_SECRET_KEY=your-key \
  -e OPENWEATHER_API_KEY=your-key \
  paprcek-monimerka:latest
```

### Production (Gunicorn)

```bash
gunicorn --workers 3 --bind 0.0.0.0:5001 app:app
```

#### Systemd Service

Soubor: `/etc/systemd/system/monika_web.service`

```ini
[Unit]
Description=Paprcek Monimerka Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/monika/docker_projects/paprcek_project/paprcek_project_flask
ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Překlad (i18n)

### Architektura překladu

Aplikace podporuje dvě jazyky: **Česitnu (CS)** a **Angličtinu (EN)**.

### Struktura translations.json

```json
{
  "cs": {
    "nav_home": "Domů",
    "nav_about": "O nás",
    "nav_contact": "Kontakty",
    "project_air_title": "Kvalita Vzduchu",
    ...
  },
  "en": {
    "nav_home": "Home",
    "nav_about": "About",
    "nav_contact": "Contact",
    "project_air_title": "Air Quality",
    ...
  }
}
```

### Implementace v app.py

#### 1. Načtení překladů

```python
def load_translations():
    path = os.path.join(app.root_path, 'translations.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

ALL_TRANSLATIONS = load_translations()
```

#### 2. Context Processor pro překladovou funkci

```python
@app.context_processor
def inject_global_vars():
    """Vloží překladovou funkci _ a další proměnné do kontextu všech šablon."""
    def _(key):
        # Funkce pro překlad v šablonách
        return g.T.get(key, key)
    
    return {
        'dt': datetime,
        'now': datetime.datetime.now,
        '_': _,  # Tahle funkce _() teď bude fungovat v každém HTML
        'current_language': g.lang
    }
```

#### 3. Before Request Handler pro nastavení jazyka

```python
@app.before_request
def before_request():
    """Nastaví jazyk a uloží texty do globálního kontextu 'g' pro šablony."""
    # Získáme jazyk ze session, výchozí je 'cs'
    lang = session.get('language', 'cs')
    g.lang = lang
    # Do g.T uložíme konkrétní slovník pro daný jazyk
    g.T = ALL_TRANSLATIONS.get(lang, ALL_TRANSLATIONS.get('cs', {}))
```

### Použití v šablonách

#### Překlad textu

```html
<!-- Překlad pomocí funkce _ -->
<h1>{{ _('nav_home') }}</h1>
<p>{{ g.T['project_air_title'] }}</p>
```

#### Přepínání jazyka

```html
<!-- Odkaz pro přepnutí na angličtinu -->
<a href="{{ url_for('core.set_language', language='en') }}">
    English
</a>

<!-- Odkaz pro přepnutí na češtinu -->
<a href="{{ url_for('core.set_language', language='cs') }}">
    Čeština
</a>
```

### Tok překladu

```
Uživatel navštíví stránku
    ↓
before_request() - Nastaví g.T a g.lang ze session
    ↓
Šablona se renderuje s {{ _('klíč') }}
    ↓
inject_global_vars() - Funkce _ vrátí g.T.get('klíč', 'klíč')
    ↓
Uživatel vidí přeložený text
```

---

## Bezpečnost a Best Practices

### GDPR Souhlas

Kontaktní formulář vyžaduje GDPR souhlas:

```python
gdpr_consent = request.form.get('gdpr')
if not gdpr_consent:
    flash('Pro odeslání je nutný souhlas se zpracováním údajů.', 'error')
    return redirect(url_for('core.contacts'))
```

### Error Handling

Aplikace používá **Sentry** pro sledování chyb v produkci:

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

### Session Security

```python
app.permanent_session_lifetime = datetime.timedelta(days=30)
```

---

## Přílohy: Diagram importů

### Stav modulů

```
app.py ────────────────────── Cílový vstupní bod
  │
  ├─→ config.py (Config třída)
  ├─→ extensions.py (Mail instance)
  ├─→ modules/core.py (core_bp Blueprint)
  └─→ modules/projects.py (projects_bp Blueprint)

modules/core.py
  ├─→ extensions.py (Mail)
  ├─→ flask_mail.Message
  └─→ flask (Blueprint, render_template, ...)

modules/projects.py
  ├─→ extensions.py (Mail)
  ├─→ current_app (Pro přístup k config)
  ├─→ flask_mail.Message
  └─→ flask (Blueprint, render_template, ...)
```

### Kruhové importy - PŘEDCHÁNO

❌ **Špatně:**
```python
# app.py
from modules.core import core_bp
# modules/core.py
from app import app  # KRUHOVÁ ZÁVISLOST!
```

✅ **Správně:**
```python
# app.py
from extensions import mail
from modules.core import core_bp
# modules/core.py
from extensions import mail  # Bez kruhové závislosti
from flask import current_app  # Pro přístup k app config
```

---

## Přispívání a Rozšíření

### Přidání nového Blueprint

1. Vytvořte nový soubor v `modules/` složce
2. Importujte Blueprint a potřebné funkce
3. Zaregistrujte blueprint v `app.py`

```python
# modules/new_feature.py
from flask import Blueprint

new_bp = Blueprint('new', __name__)

@new_bp.route('/new-route')
def new_route():
    return render_template('new_template.html')
```

```python
# app.py
from modules.new_feature import new_bp
app.register_blueprint(new_bp)
```

### Přidání nového Extension

1. Inicializujte extension v `extensions.py`
2. Importujte v `app.py` a zavolejte `.init_app()`

```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

```python
# app.py
from extensions import db

db.init_app(app)
```

---

## Kontakt a Řešení Problémů

### Časté problémy

**Problem:** `ModuleNotFoundError: No module named 'flask_mail'`
**Řešení:** `pip install -r requirements.txt`

**Problem:** `SENTRY_DSN` není nastavena
**Řešení:** Přidejte `SENTRY_DSN` do `.env` souboru

**Problem:** Emaily se neposílají
**Řešení:** Zkontrolujte `MAIL_PASSWORD` a povolte "Méně bezpečné aplikace" v Gmail nastavení

---

**Poslední aktualizace:** 2026-04-06
**Verze:** 1.0 (Refactored Blueprint Architecture)
