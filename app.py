import os
import requests
import datetime
from flask import Flask, render_template

# --- NASTAVENÍ A KONFIGURACE ---

# Precteni API klice z promenne prostredi (bezpecne ulozeno v .env)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
app = Flask(__name__)

# --- POMOCNÉ FUNKCE pro API (Znovu aktivováno) ---

def get_air_quality_data(lat, lon, api_key):
    """Získá data o kvalitě vzduchu z OpenWeatherMap API a ošetřuje chyby."""
    if not api_key:
        return {"error_title": "CHYBA KONFIGURACE", "error_message": "OPENWEATHERMAP_API_KEY není nastaven! Data nelze získat."}

    # API volání pro aktuální kvalitu vzduchu
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    
    try:
        # Volani API s timeoutem 10s
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Vyhodi chybu pro 4xx/5xx odpovedi (napr. 401)

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
            return {"error_title": "CHYBA AUTORIZACE (401)", "error_message": "Váš API klíč je neplatný nebo chybí. Zkontrolujte OPENWEATHERMAP_API_KEY."}
        else:
            return {"error_title": f"CHYBA HTTP ({error_code})", "error_message": f"Došlo k chybě při volání API: {e}"}
            
    except requests.exceptions.ConnectionError:
        return {"error_title": "CHYBA SÍTĚ", "error_message": "Nepodařilo se připojit k OpenWeatherMap API. Zkontrolujte síťové připojení serveru."}
        
    except requests.exceptions.Timeout:
        return {"error_title": "VYPRŠENÍ ČASU", "error_message": "Volání API trvalo příliš dlouho a vypršel časový limit (10 sekund)."}
        
    except Exception as e:
        return {"error_title": "NEZNÁMÁ CHYBA", "error_message": f"Nastala neočekávaná chyba: {e}"}


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

# --- FLASK KONTEXTOVY PROCESOR (PRO FOOTER) ---

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
    """Stranka pro projekt Monitor Kvality Vzduchu. POUŽÍVÁ REÁLNÁ DATA."""
    
    # Souradnice pro Prahu (50.07, 14.43)
    lat = 50.07 
    lon = 14.43
    
    api_result = get_air_quality_data(lat, lon, API_KEY)
    
    # Kontrola, zda vysledek obsahuje chybovou zpravu (klic 'error_message')
    if 'error_message' in api_result:
        # Pokud je v datech chyba, renderujeme template s chybovou zpravou
        return render_template('air_quality.html', 
                               error_title=api_result['error_title'],
                               error_message=api_result['error_message'])
    else:
        # Zpracovani a zobrazeni realnych dat
        data = api_result
        status_css = get_aqi_status_css(data['aqi'])
        status_cz = get_aqi_status_cz(data['aqi'])
        
        return render_template('air_quality.html', 
                               data=data, 
                               status_css=status_css, 
                               status_cz=status_cz)

@app.route('/contacts')
def contacts():
    """Stranka s kontaktnimi udaji."""
    return render_template('contacts.html')


# --- SPUŠTĚNÍ ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
