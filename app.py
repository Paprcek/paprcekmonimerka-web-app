import os
import requests
import datetime
# import time # TENTO IMPORT JSME ZRUSILI A NAHRAZUJEME DATETIME LOGIKOU
from flask import Flask, render_template

# --- NASTAVENÍ A KONFIGURACE ---

# Precteni API klice z promenne prostredi
API_KEY = os.getenv("OPENWEATHER_API_KEY") 

app = Flask(__name__)

# Souradnice pro Prahu
LAT = 50.07 
LON = 14.43

# --- POMOCNÉ FUNKCE pro API ---

def get_air_quality_data(lat, lon, api_key):
    """Získá aktuální data o kvalitě vzduchu z OpenWeatherMap API."""
    if not api_key:
        return {"error_title": "CHYBA KONFIGURACE", "error_message": "OPENWEATHER_API_KEY není nastaven! Data nelze získat."}

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 

        json_data = response.json()
        
        if json_data.get('list'):
            current_data = json_data['list'][0]
            
            # Extrakce klicovych dat
            aqi = current_data['main']['aqi']
            pm25 = current_data['components']['pm2_5']
            
            return {
                "aqi": aqi,
                "pm25": pm25
            }
        else:
            return {"error_title": "CHYBA DAT", "error_message": "API nevrátilo seznam dat (list)."}

    except requests.exceptions.HTTPError as e:
        error_code = e.response.status_code
        if error_code == 401:
            return {"error_title": "CHYBA AUTORIZACE (401)", "error_message": "Váš API klíč je neplatný nebo chybí."}
        else:
            return {"error_title": f"CHYBA HTTP ({error_code})", "error_message": f"Došlo k chybě při volání API: {e}"}
            
    except requests.exceptions.ConnectionError:
        return {"error_title": "CHYBA SÍTĚ", "error_message": "Nepodařilo se připojit k API."}
        
    except requests.exceptions.Timeout:
        return {"error_title": "VYPRŠENÍ ČASU", "error_message": "Volání API trvalo příliš dlouho."}
        
    except Exception as e:
        return {"error_title": "NEZNÁMÁ CHYBA", "error_message": f"Nastala neočekávaná chyba: {e}"}


def get_air_quality_history(lat, lon, api_key):
    """Získá historická data za posledních 72 hodin (3 dny)."""
    if not api_key:
        return {"error_title": "CHYBA KONFIGURACE", "error_message": "OPENWEATHER_API_KEY není nastaven! Historická data nelze získat."}

    # ZJEDNODUŠENÁ LOGIKA DATUMU:
    # Zjistime aktualni cas a odecteme 72 hodin pomoci datetime
    now = datetime.datetime.now(datetime.timezone.utc) # UTC cas (pozadavek OpenWeather)
    
    end_time_dt = now
    start_time_dt = now - datetime.timedelta(hours=72)
    
    # Prevod datetime objektu na UNIX timestamp (int)
    end_time = int(end_time_dt.timestamp())
    start_time = int(start_time_dt.timestamp())
    
    # API volání pro historickou kvalitu vzduchu
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={lon}&start={start_time}&end={end_time}&appid={api_key}"
    
    try:
        response = requests.get(url, timeout=20) # Vetsi timeout pro vetsi objem dat
        response.raise_for_status() 
        json_data = response.json()
        
        if json_data.get('list'):
            # Vratime cely seznam historickych dat
            return json_data['list']
        else:
            return {"error_title": "CHYBA DAT", "error_message": "API nevrátilo seznam historických dat (list)."}

    except Exception as e:
        return {"error_title": "NEZNÁMÁ CHYBA", "error_message": f"Nastala chyba pri volani historie: {e}"}

# --- ZPRACOVÁNÍ STATUSŮ (BEZE ZMĚN) ---

def get_aqi_status_css(aqi_index):
    """Prevede numericky AQI index na bezpecny anglicky status (pro CSS tridy)."""
    if aqi_index == 1:
        return "good"
    elif aqi_index == 2:
        return "moderate"
    elif aqi_index == 3:
        return "unhealthy_sensitive"
    elif aqi_index == 4:
        return "unhealthy"
    elif aqi_index == 5:
        return "hazardous"
    return "unknown"

def get_aqi_status_cz(aqi_index):
    """Prevede numericky AQI index na cesky status (pro zobrazeni uzivateli)."""
    if aqi_index == 1:
        return "Dobrá"
    elif aqi_index == 2:
        return "Uspokojivá"
    elif aqi_index == 3:
        return "Střední"
    elif aqi_index == 4:
        return "Špatná"
    elif aqi_index == 5:
        return "Velmi špatná"
    return "Neznámá"

# --- FLASK KONTEXTOVY PROCESOR ---

@app.context_processor
def inject_now():
    """Zpristupni funkci 'now' pro zobrazeni aktualniho roku ve footeru."""
    return {'now': datetime.datetime.utcnow}

# --- ROUTING (SMĚROVÁNÍ) ---

@app.route('/')
def index():
    """Hlavni stranka portfolia s prehledem projektu."""
    return render_template('index.html')

@app.route('/air-quality')
def air_quality():
    """Stranka pro projekt Monitor Kvality Vzduchu (Aktualni data)."""
    
    api_result = get_air_quality_data(LAT, LON, API_KEY)
    
    if 'error_message' in api_result:
        return render_template('air_quality.html', 
                               error_title=api_result['error_title'],
                               error_message=api_result['error_message'])
    else:
        data = api_result
        status_css = get_aqi_status_css(data['aqi'])
        status_cz = get_aqi_status_cz(data['aqi'])
        
        return render_template('air_quality.html', 
                               data=data, 
                               status_css=status_css, 
                               status_cz=status_cz)

@app.route('/air-history')
def air_history():
    """NOVA ROUTA: Historicka data AQI a PM2.5 pro vizualizaci."""
    
    history_data = get_air_quality_history(LAT, LON, API_KEY)
    
    if isinstance(history_data, dict) and 'error_message' in history_data:
        # Pokud doslo k chybe (napr. neplatny klic), posleme chybovou hlasku
        return render_template('history.html', 
                               error_title=history_data['error_title'],
                               error_message=history_data['error_message'])
    
    # 1. Extrakce dat pro graf
    labels = []  # Casove razitka pro osu X
    aqi_values = [] # Hodnoty AQI pro prvni radu Y
    pm25_values = [] # Hodnoty PM2.5 pro druhou radu Y
    
    # Historicka data z API prichazeji serazena
    for entry in history_data:
        # Prevod UNIX timestamp (entry['dt']) na citelny format (HH:MM dd.mm.)
        timestamp = entry['dt']
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime("%H:%M %d.%m.")
        
        labels.append(formatted_time)
        aqi_values.append(entry['main']['aqi'])
        pm25_values.append(entry['components']['pm2_5'])

    # 2. Renderovani sablony s daty ve formatu, ktery JS snadno zpracuje
    return render_template('history.html', 
                           labels=labels, 
                           aqi_values=aqi_values, 
                           pm25_values=pm25_values)

@app.route('/contacts')
def contacts():
    """Stranka s kontaktnimi udaji."""
    return render_template('contacts.html')


# --- SPUŠTĚNÍ ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
