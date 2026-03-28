import os
import json
import requests
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from flask_mail import Mail, Message
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSNF'),
    integrations=[FlaskIntegration()],
    # Nastavení pro rok 2026 – zachytí 100 % transakcí pro začátek
    traces_sample_rate=1.0,
    # Pokud chceš vidět i těla požadavků (pozor na citlivá data)
    send_default_pii=True
)

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'paprcekmonimerka@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = 'paprcekmonimerka@gmail.com'

mail = Mail(app)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

LATITUDE = 50.0755
LONGITUDE = 14.4378

app.secret_key = SECRET_KEY if SECRET_KEY else 'default_fallback_secret_key'

app.permanent_session_lifetime = datetime.timedelta(days=30)

def load_translations():
    path = os.path.join(app.root_path, 'translations.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

ALL_TRANSLATIONS = load_translations()

@app.context_processor
def inject_global_vars():
    """
    Zpřístupní modul 'datetime' pod klíčem 'dt' a funkci datetime.datetime.now 
    pod klíčem 'now' pro použití v šablonách.
    """
    return {
        'dt': datetime,
        'now': datetime.datetime.now
    }

@app.context_processor
def inject_translation():
    """Vloží překladovou funkci _ do kontextu všech šablon."""
    def _(key):
        return g.T.get(key, key)
    
    return dict(_=_)


@app.before_request
def before_request_func():
    """Nastaví jazyk a uloží texty do globálního kontextu 'g' pro šablony."""
    lang = session.get('language', 'cs')
    
    if lang not in ALL_TRANSLATIONS:
        lang = 'cs'

    g.T = ALL_TRANSLATIONS[lang]
    g.lang = lang

@app.route('/language/<lang_code>')
def set_language(lang_code):
    """Mění jazyk a přesměruje zpět na předchozí stránku."""
    if lang_code in ALL_TRANSLATIONS:
        session['language'] = lang_code
        session.permanent = True
        
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    """Hlavní stránka portfolia s přehledem projektů."""
    return render_template('index.html')

@app.route('/watchdog')
def watchdog():
    """Specifikace projektu Watchdog"""
    return render_template('watchdog.html')

@app.route('/monitoring-eshopu')
def watchdog_sales():
    return render_template('watchdog_landing.html')

@app.route('/watchdog-order', methods=['POST'])
def watchdog_order():
    target_url = request.form.get('target_url')
    tracking_type = request.form.get('tracking_type')
    client_email = request.form.get('client_email')
    notes = request.form.get('notes')
    
    try:
        msg = Message(
            subject=f"Nová poptávka: Watchdog - {target_url}",
            recipients=['moncakbp@gmail.com'], 
            body=f"""
                Nová poptávka od: {client_email}

                Co chce hlídat: {tracking_type}
                Cílový web: {target_url}

                Specifika/Poznámka:
                {notes}
            """
        )
        mail.send(msg)
        flash(g.T.get('watchdog_success_msg', 'Zpráva byla úspěšně odeslána!'), 'success')
        print(f"Úspěch: Poptávka od {client_email} odeslána na e-mail.")
    except Exception as e:
        print(f"Kritická chyba: {e}", flush=True)
        flash(f"Chyba odesílání: {str(e)}", 'error') 

    return redirect(url_for('watchdog_sales'))


@app.route('/gdpr')
def gdpr():
    """Stránka s informacemi o ochraně osobních údajů."""
    return render_template('gdpr.html')

@app.route('/about')
def about():
    """Stránka O mně."""
    return render_template('about.html')

@app.route('/contacts', methods=['GET', 'POST']) 
def contacts():
    """Stránka s kontaktním formulářem a údaji."""
    if request.method == 'POST':
        gdpr_consent = request.form.get('gdpr')

        if not gdpr_consent:
            flash('Pro odeslání paprsku je nutné souhlasit se zpracováním údajů.', 'error')
            return redirect(url_for('contacts'))

        name = request.form.get('name')
        email = request.form.get('email')
        message_body = request.form.get('message')

        msg = Message(
            subject=f"Paprsek z webu od: {name}",
            recipients=['moncakbp@gmail.com'], 
            body=f"Nová zpráva!\n\nOd: {name}\nE-mail: {email}\n\nText:\n{message_body}"
        )

        try:
            mail.send(msg)
            flash('Tvůj digitální paprsek dorazil do Dejvic! Ozvu se ti co nejdříve.', 'success')
        except Exception as e:
            print(f"Kritická chyba odesílání: {e}")
            flash('Chyba v přenosu. Zkus to prosím znovu nebo mi napiš přímo na e-mail.', 'error')

        return redirect(url_for('contacts'))

    return render_template('contacts.html')

@app.route('/air_quality')
def air_quality():
    """Zobrazuje aktuální data kvality vzduchu."""
    if not API_KEY:
        return render_template('air_quality.html',
                               error_title=g.T['error_title'],
                               error_message=g.T['error_msg'])
    
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vyhodí chybu pro 4xx/5xx kódy
        data = response.json()

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
            		error_title=g.T.get('error_api_title', 'Chyba API'),
                    error_message=g.T.get('error_api_message', 'Klíč API může být neplatný nebo neaktivní.')
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

    end_timestamp = int(datetime.datetime.now().timestamp())
    start_timestamp = int((datetime.datetime.now() - datetime.timedelta(hours=72)).timestamp())

    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history"
    
    params = {
        'lat': LATITUDE,
        'lon': LONGITUDE,
        'start': start_timestamp,
        'end': end_timestamp,
        'appid': API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        labels = []
        aqi_values = []
        pm25_values = []

        for entry in data['list']:
            dt_object = datetime.datetime.fromtimestamp(entry['dt'])
            formatted_time = dt_object.strftime("%H:%M %d.%m.")

            labels.append(formatted_time)
            aqi_values.append(entry['main']['aqi'])
            pm25_values.append(entry['components']['pm2_5'])

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

@app.route('/binary-translator', methods=['GET', 'POST'])
def binary_translator():
    result = ""
    input_text = ""
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        result = text_to_binary(input_text)
        
    return render_template('binary.html', result=result, input_text=input_text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
