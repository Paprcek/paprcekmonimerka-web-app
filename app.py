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
        'intro_text': 'Jmenuji se Monika a specializuji se na vývoj webových aplikací a automatizaci v Pythonu. Moje práce propojuje robustní backend (Flask, Django) s moderním nasazením v Dockeru. Zaměřuji se na tvorbu efektivních nástrojů, integraci API a inteligentní scraping dat, které klientům šetří čas a vnášejí do procesů řád.',
        'projects_title': 'Moje Projekty',
        'project_air_title': 'Air Quality Monitor (CZ)',
        'project_air_desc': 'Webová aplikace demonstrující integraci externího API (OpenWeatherMap) pro vizualizaci dat o znečištění ovzduší v Praze.',
        'project_air_link': 'Zobrazit aplikaci (Aktuální data)',
	'future_project': 'Herní Centrum',
	'future_placeholder': 'Zde jsou v současnosti vyvíjeny nové herní aplikace, postavené na frameworku Django.',
        'about_title': 'O Mně',
        'about_greeting': 'Ahoj, jsem Monika!',
        'about_text_placeholder': 'Moje cesta do světa IT začala u hledání chyb. Jako rekvalifikovaná testerka jsem nahlédla pod kapotu softwaru a pochopila, jak klíčová je jeho kvalita. Tato zkušenost mě přivedla k vlastní tvorbě – dnes chyby nejen hledám, ale aktivně jim předcházím skrze precizní kód. Baví mě tvořit systémy, které jsou logické, efektivní a mají reálný přínos.',
	'about_text_01': 'Specializuji se na backendový vývoj v Pythonu (Flask, Django) a automatizaci procesů. Moje technické zázemí zahrnuje kompletní správu vlastního serveru, kontejnerizaci projektů v Dockeru a bezpečné síťové propojení přes Cloudflare Tunnel. Nestavím jen webové stránky; buduji kompletní infrastrukturu od první řádky kódu až po nasazení do produkce. Mým cílem je neustálý debugging vlastních schopností a posouvání hranic toho, co se dá pomocí technologií zjednodušit.',
        'about_motto': ' „Kód nepíšu proto, aby existoval, ale aby osvobozoval. Ladění je proces, kterým z nekonečných smyček chaosu vytvářím prostor pro to, na čem skutečně záleží.“ ',
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
	'play_game': 'Spustit Hru',
    'nav_game_center': 'Herní centrum',
    'binar_trans': 'Překladač binárního kódu',
    'enter_text': 'Zadej text k "debugování" do binárky:',
    'translate': 'Přeložit do strojové řeči',
    'binary_code': 'Binární kód',
    'wd_popis': 'Python bot pro automatický monitoring cen a skladu velkoobchodu. Běží v Dockeru a posílá HTML zprávy.',
    'zobrazit_specifikaci': 'Zobrazit specifikaci',
    'tbn_popis':'Vývoj a technické nasazení webu dle specifických požadavků klientky. Od čistého kódování až po konfiguraci domény a hostingu.',
    'go_web': 'Navštívit web',
    },
    'en': {
        'home_title': "Monika Paprcek | IT Portfolio",
        'nav_home': 'Home',
        'nav_about': 'About Me',
        'nav_contact': 'Contact',
        'nav_air_quality': 'Air Quality',
        'nav_air_history': 'AQI History Data',
        'greeting': 'Welcome to my portfolio',
        'intro_text': 'My name is Monika and I specialize in web application development and automation in Python. My work combines robust backend (Flask, Django) with modern Docker deployment. I focus on creating efficient tools, API integration, and intelligent data scraping that save clients time and bring order to their processes.',
        'projects_title': 'My Projects',
        'project_air_title': 'Air Quality Monitor (EN)',
        'project_air_desc': 'A web application demonstrating the integration of an external API (OpenWeatherMap) to visualize air pollution data in Prague.',
        'project_air_link': 'View Application (Current data)',
        'future_project': 'Game Hub',
	'future_placeholder': 'A new game applications are currently being developed here, built on the Django framework.',
	'about_title': 'About Me',
        'about_greeting': 'Hi, I am Monika!',
        'about_text_placeholder': "My journey into the world of IT began with finding bugs. As a retrained tester, I looked under the hood of software and understood how crucial its quality is. This experience led me to my own creation - today I not only look for bugs, but also actively prevent them through precise code. I enjoy creating systems that are logical, efficient and have real benefits.",
        'about_text_01': "I specialize in backend development in Python (Flask, Django) and process automation. My technical background includes complete management of my own server, containerization of projects in Docker and secure network connection via Cloudflare Tunnel. I don't just build websites; I build complete infrastructure from the first line of code to deployment in production. My goal is to constantly debug my own abilities and push the boundaries of what can be simplified with technology.",
	'about_motto': " „I don't write code to exist, but to liberate. Debugging is the process of making space for what really matters from endless loops of chaos.“ ",
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
        'status_unknown': 'Unknown',
	'play_game': 'Play Game',
    'nav_game_center': 'Game Hub',
    'binar_trans': 'Binary To Text Convertor',
    'enter_text': 'Enter the text to "debug" into the binary:',
    'translate': 'Translate into machine language',
    'binary_code': 'Binary Code',
    'wd_popis': 'Python bot for automatic monitoring of wholesale prices and inventory. It runs in Docker and sends HTML messages.',
    'zobrazit_specifikaci': 'View specification',
    'tbn_popis':'Development and technical implementation of the website according to the specific requirements. From clean coding to domain and hosting configuration.',
    'go_web': 'Visit the Website'
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
