import os
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

# Databáze textů pro CS a EN
TEXT_DATA = {
    'cs': {
        'home_title': 'Monika Paprcek | IT Portfolio',
        'nav_home': 'Domů',
        'nav_about': 'O Mně',
        'nav_contact': 'Kontakt',
        'nav_air_quality': 'Kvalita Vzduchu',
        'nav_air_history': 'Historická data AQI',
        'greeting': 'Vítejte v mém portfoliu',
        'intro_text': 'Jmenuji se Monika a věnuji se vývoji webových aplikací. Tento projekt slouží jako demonstrace mé práce s Pythonem (Flask), integrací API a frontendovým designem.',
        'projects_title': 'Moje Projekty',
        'project_air_title': 'Air Quality Monitor (CZ)',
        'project_air_desc': 'Webová aplikace demonstrující integraci externího API (OpenWeatherMap) pro vizualizaci dat o znečištění ovzduší v Praze.',
        'project_air_link': 'Zobrazit aplikaci (Aktuální data)',
	'future_project': 'Budoucí Projekt',
	'future_placeholder': 'Zde se brzy objeví další projekt, pravděpodobně zaměřený na datovou analýzu, vizualizaci nebo interaktivní hru.',
        'about_title': 'O Mně',
        'about_greeting': 'Ahoj, jsem Monika!',
        'about_text_placeholder': 'Zde brzy doplním podrobné informace o svých dovednostech a cestě k IT. Zaměřuji se na Python a Flask, ale ráda se učím i moderní frontendové frameworky.',
	'about_text_01': ' Věnuji se primárně Pythonu a frameworku Flask, abych dokázala vytvářet robustní backendové aplikace s jednoduchým, ale funkčním frontendem (jako je tento projekt, který využívá Tailwind CSS). Mým cílem je neustále se neustále učit a posouvat své hranice ve vývoji.',
        'about_motto': ' "Nejde o to, jak rychle kód píšete, ale kolik se toho naučíte, když ho ladíte." ',
	'error_title': 'Chyba API',
        'error_msg': 'Nastala chyba při volání OpenWeatherMap API. Zkuste to prosím později.',
        'contact_title': 'Kontaktní údaje',
        'contact_text': 'Níže naleznete nejpřímější cesty, jak mě kontaktovat a prohlédnout si moji práci. Těším se na Vaši zprávu nebo spolupráci!',
	'air_quality_title': 'Monitor Kvality Vzduchu v Praze',
	'air_project_desc': 'Projekt demonstruje integraci Flask backendu s externím API (OpenWeatherMap) a zpracování JSON dat.',
	'air_quality_back': 'Zpět na Přehled Projektů',
	'history_title': 'Historie Kvality Vzduchu (Posledních 72 hodin)',
	'history_desc': 'Vizualizace vývoje indexu AQI (Air Quality Index) a koncentrace PM2.5 v čase.',
	'footer': 'Všechna práva vyhrazena.',
	'aqi_status': 'Stav AQI',
        'status_good': 'Dobrý',
        'status_fair': 'Uspokojivý',
        'status_unhealthy_sensitive': 'Nezdravý pro citlivé skupiny',
        'status_unhealthy': 'Nezdravý',
        'status_hazardous': 'Velmi nezdravý',
        'status_unknown': 'Neznámý',

    },
    'en': {
        'home_title': "Monika Paprcek | IT Portfolio",
        'nav_home': 'Home',
        'nav_about': 'About Me',
        'nav_contact': 'Contact',
        'nav_air_quality': 'Air Quality',
        'nav_air_history': 'AQI History Data',
        'greeting': 'Welcome to my portfolio',
        'intro_text': 'My name is Monika and I focus on web application development. This project serves as a demonstration of my work with Python (Flask), API integration, and frontend design.',
        'projects_title': 'My Projects',
        'project_air_title': 'Air Quality Monitor (EN)',
        'project_air_desc': 'A web application demonstrating the integration of an external API (OpenWeatherMap) to visualize air pollution data in Prague.',
        'project_air_link': 'View Application (Current data)',
        'future_project': 'Future Project',
	'future_placeholder': 'Another project will appear here soon, probably focused on data analysis, visualizations, or an interactive game.',
	'about_title': 'About Me',
        'about_greeting': 'Hi, I am Monika!',
        'about_text_placeholder': 'I will soon fill in detailed information about my skills and journey into IT here. I focus on Python and Flask, but I am also keen on learning modern frontend frameworks.',
        'about_text_01': 'I primarily focus on Python and the Flask framework to create robust backend applications with a simple but functional frontend (like this project using Tailwind CSS). My goal is to constantly learn and push my boundaries in development.',
	'about_motto': ' "It is not how fast you write code, but how much you learn while debug it." ',
	'error_title': 'API Error',
        'error_msg': 'An error occurred while calling the OpenWeatherMap API. Please try again later.',
        'contact_title': 'Contact Details',
        'contact_text': 'Below you will find the most direct ways to contact me and view my work. I look forward to hearing from you or collaborating with you!',
	'air_quality_title': 'Prague Air Quality Monitor',
	'air_project_desc': 'The project demonstrates the integration of a Flask backend with an external API (OpenWeatherMap) and the processing of JSON data.',
	'air_quality_back': 'Back to Project Overview',
	'history_title': 'Air Quality History (Last 72 hours)',
	'history_desc':	'Visualization of the development of the AQI (Air Quality Index) and PM2.5 concentration over time.',
	'footer': 'All rights reserved.',
	'aqi_status': 'AQI Status',
        'status_good': 'Good',
        'status_fair': 'Moderate',
        'status_unhealthy_sensitive': 'Unhealthy for Sensitive Groups',
        'status_unhealthy': 'Unhealthy',
        'status_hazardous': 'Hazardous',
        'status_unknown': 'Unknown'
    }
}

# --- MIDDLEWARE A JAZYKOVÁ LOGIKA ---

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
    
    # 2. Kontrola, zda je jazyk podporován
    if lang not in TEXT_DATA:
        lang = 'cs'

    # 3. Uložení textů (T) a aktuálního jazyka (lang) do globálního kontextu Flasku
    g.T = TEXT_DATA[lang]
    g.lang = lang

@app.route('/language/<lang_code>')
def set_language(lang_code):
    """Mění jazyk a přesměruje zpět na předchozí stránku."""
    if lang_code in TEXT_DATA:
        session['language'] = lang_code
        
    # Presmeruje uzivatele zpet na predchozi stranku, odkud prisel
    return redirect(request.referrer or url_for('index'))

# --- FLASK ROUTES ---

@app.route('/')
def index():
    """Hlavní stránka portfolia s přehledem projektů."""
    return render_template('index.html')

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

# --- SPUŠTĚNÍ ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
