import os
import json
import requests
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, g

# --- NASTAVENÍ A KONFIGURACE ---

# Precteni API klice z promenne prostredi (Gunicorn)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

# Konstanta pro Prahu
LATITUDE = 50.0755
LONGITUDE = 14.4378

app = Flask(__name__)
# Nastaveni SECRET_KEY pro session (důležité pro zapamatování jazyka)
app.secret_key = SECRET_KEY if SECRET_KEY else 'default_fallback_secret_key'

# Nastaveni trvani session na 30 dni (pro zapamatovani jazyka)
# Pouzijeme datetime.timedelta, protoze modul datetime je importovan
app.permanent_session_lifetime = datetime.timedelta(days=30)

# --- MIDDLEWARE A JAZYKOVÁ LOGIKA ---

# Funkce pro načtení překladů ze souboru
def load_translations():
    path = os.path.join(app.root_path, 'translations.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Načteme všechna data do jedné proměnné
ALL_TRANSLATIONS = load_translations()

# ZMĚNA: ZPŘÍSTUPNÍME CELÝ MODUL DATETIME A FUNKCI now()
@app.context_processor
def inject_global_vars():
    """
    Zpřístupní modul 'datetime' pod klíčem 'dt' a funkci datetime.datetime.now 
    pod klíčem 'now' pro použití v šablonách.
    """
    return {
        'dt': datetime,
        'now': datetime.datetime.now # Přidáno pro použití v šabloně jako {{ now().year }}
    }

@app.context_processor
def inject_translation():
    """Vloží překladovou funkci _ do kontextu všech šablon."""
    def _(key):
        # Vezme aktuálně vybraný jazyk (g.lang) a vrátí překlad pro daný klíč (key)
        # Zajišťuje, že se neobjeví chyba, když překlad chybí
        return g.T.get(key, key)
    
    # Do šablony se vloží funkce, kterou lze volat jako _('klíč')
    return dict(_=_)


@app.before_request
def before_request_func():
    """Nastaví jazyk a uloží texty do globálního kontextu 'g' pro šablony."""
    # 1. Získání jazyka ze Session, nebo defaultně 'cs'
    lang = session.get('language', 'cs')
    
    # 2. Kontrola, zda je jazyk v našem novém souboru
    if lang not in ALL_TRANSLATIONS:
        lang = 'cs'

    # 3. Uložení správné jazykové větve do g.T
    g.T = ALL_TRANSLATIONS[lang]
    g.lang = lang

@app.route('/language/<lang_code>')
def set_language(lang_code):
    """Mění jazyk a přesměruje zpět na předchozí stránku."""
    # Kontrolujeme v ALL_TRANSLATIONS místo starého TEXT_DATA
    if lang_code in ALL_TRANSLATIONS:
        session['language'] = lang_code
        session.permanent = True # Aby si to prohlížeč pamatoval těch 30 dní
        
    return redirect(request.referrer or url_for('index'))

# --- FLASK ROUTES ---

@app.route('/')
def index():
    """Hlavní stránka portfolia s přehledem projektů."""
    return render_template('index.html')

@app.route('/watchdog')
def watchdog():
    """Specifikace projektu Watchdog"""
    return render_template('watchdog.html')

@app.route('/about')
def about():
    """Stránka O mně."""
    return render_template('about.html')

@app.route('/contacts') 
def contacts():
    """Stránka s kontaktními údaji (statické odkazy)."""
    return render_template('contacts.html')

@app.route('/air_quality')
def air_quality():
    """Zobrazuje aktuální data kvality vzduchu."""
    if not API_KEY:
        return render_template('air_quality.html',
                               error_title=g.T['error_title'],
                               error_message=g.T['error_msg'])
    
    # URL pro aktuální data
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vyhodí chybu pro 4xx/5xx kódy
        data = response.json()

        # Zpracování dat
        aqi = data['list'][0]['main']['aqi']
        pm25 = data['list'][0]['components']['pm2_5']

        aqi_map = {
            1: ('status_good', 'good'),
            2: ('status_fair', 'moderate'),
            3: ('status_unhealthy_sensitive', 'unhealthy_sensitive'),
            4: ('status_unhealthy', 'unhealthy'),
            5: ('status_hazardous', 'hazardous')
        }
        status_key, status_css = aqi_map.get(aqi, ('status_unknown', 'unknown'))

        return render_template('air_quality.html',
                               data={'aqi': aqi, 'pm25': round(pm25, 2)},
                               status_key=status_key, 
                               status_css=status_css,
                               error_title=None)

    except (requests.exceptions.RequestException, KeyError) as e:
        error_message = f"Nastala chyba: {response.status_code} - {e.response.reason}. Klíč API může být neplatný nebo neaktivní."
       	return render_template('air_quality.html',
            		data={'aqi': 'N/A', 'pm25': 'N/A'},
            		status_key='status_unknown',  # Nyní posíláme klíč pro "Neznámý"
            		status_css='unknown',
            		error_title=_('error_api_title'),
            		error_message=_('error_api_message')
            		)

    except Exception as e:
        error_message = f"Nastala chyba při zpracování dat: {e}"
        return render_template('air_quality.html',
                               error_title=g.T['error_title'],
                               error_message=error_message)


@app.route('/air_history')
def air_history():
    """Zobrazuje historická data kvality vzduchu v grafu."""
    if not API_KEY:
        return render_template('history.html', 
                               error_title=g.T['error_title'], 
                               error_message=g.T['error_msg'])

    # Výpočet časových razítek pro 72 hodin zpět
    end_timestamp = int(datetime.datetime.now().timestamp())
    start_timestamp = int((datetime.datetime.now() - datetime.timedelta(hours=72)).timestamp())

    # URL pro historická data (vyžaduje parametry start/end)
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history"
    
    params = {
        'lat': LATITUDE,
        'lon': LONGITUDE,
        'start': start_timestamp,
        'end': end_timestamp,
        'appid': API_KEY # Musí být jen samotný API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        labels = []
        aqi_values = []
        pm25_values = []

        for entry in data['list']:
            # Prevod UNIX timestamp na citelny format (HH:MM dd.mm.)
            dt_object = datetime.datetime.fromtimestamp(entry['dt'])
            formatted_time = dt_object.strftime("%H:%M %d.%m.")

            labels.append(formatted_time)
            aqi_values.append(entry['main']['aqi'])
            pm25_values.append(entry['components']['pm2_5'])

        # Renderovani sablony s daty pro Chart.js
        return render_template('history.html',
                               labels=labels,
                               aqi_values=aqi_values,
                               pm25_values=pm25_values,
                               error_message=None)

    except requests.exceptions.HTTPError as e:
        error_message = f"Nastala chyba při volání historie: {response.status_code} - {e.response.reason}"
        return render_template('history.html',
                               error_title=g.T['error_title'],
                               error_message=error_message)
    except Exception as e:
        error_message = f"Nastala chyba při zpracování historických dat: {e}"
        return render_template('history.html',
                               error_title=g.T['error_title'],
                               error_message=error_message)

def text_to_binary(text):
    binary_list = [format(ord(char), '08b') for char in text]
    return "\n".join(binary_list)

# 2. Pak tvoje routa, která tu funkci použije
@app.route('/binary-translator', methods=['GET', 'POST'])
def binary_translator():
    result = ""
    input_text = ""
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        # Tady zavoláš svou funkci!
        result = text_to_binary(input_text)
        
    return render_template('binary.html', result=result, input_text=input_text)

# --- SPUŠTĚNÍ ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
