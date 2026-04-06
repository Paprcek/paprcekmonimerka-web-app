import requests
import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, g, current_app, send_from_directory
from flask_mail import Message
from extensions import mail

projects_bp = Blueprint('projects', __name__)

LATITUDE = 50.0755
LONGITUDE = 14.4378

@projects_bp.route('/watchdog')
def watchdog():
    return render_template('watchdog.html')

@projects_bp.route('/monitoring-eshopu')
def watchdog_sales():
    return render_template('watchdog_landing.html')

@projects_bp.route('/watchdog-order', methods=['POST'])
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

    return redirect(url_for('projects.watchdog_sales'))

@projects_bp.route('/air_quality')
def air_quality():
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    """Zobrazuje aktuální data kvality vzduchu."""
    if not api_key:
        return render_template('air_quality.html',
                               error_title=g.T['error_title'],
                               error_message=g.T['error_msg'])

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={api_key}"

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
        error_message = f"Nastala chyba: {response.status_code} - {response.reason}. Klíč API může být neplatný nebo neaktivní."
        return render_template('air_quality.html',
                               data={'aqi': 'N/A', 'pm25': 'N/A'},
                               status_key='status_unknown',
                               status_css='unknown',
                               error_title=g.T.get('error_api_title', 'Chyba API'),
                               error_message=g.T.get('error_api_message', 'Klíč API může být neplatný nebo neaktivní.')
                               )

    except Exception as e:
        error_message = f"Nastala chyba při zpracování dat: {e}"
        return render_template('air_quality.html',
                               error_title=g.T['error_title'],
                               error_message=error_message)

@projects_bp.route('/air_history')
def air_history():
    """Zobrazuje historická data kvality vzduchu v grafu."""
    api_key = current_app.config.get('OPENWEATHER_API_KEY')
    if not api_key:
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
        'appid': api_key
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
        error_message = f"Nastala chyba při volání historie: {response.status_code} - {response.reason}"
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

@projects_bp.route('/binary-translator', methods=['GET', 'POST'])
def binary_translator():
    result = ""
    input_text = ""
    if request.method == 'POST':
        input_text = request.form.get('text', '')
        result = text_to_binary(input_text)

    return render_template('binary.html', result=result, input_text=input_text)

@projects_bp.route('/vysilacky-shoptet-feed.xml')
def serve_shoptet_feed():
    directory = "/app/feeds"
    return send_from_directory(directory, "shoptet_feed.xml", mimetype='application/xml')
