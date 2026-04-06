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

# 1. Inicializace Sentry
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)

app = Flask(__name__)
app.config.from_object(Config)

# 2. Nastavení Sessions a Secret Key
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-pro-lokalni-vyvoj")
#app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 dní

# 3. Inicializace Extensions
mail.init_app(app)

# 4. Načtení překladů (jednou při startu)
def load_translations():
    path = os.path.join(app.root_path, 'translations.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Chyba při načítání překladů: {e}")
        return {}

ALL_TRANSLATIONS = load_translations()

# 5. Hooks a Context Processors (tohle opraví ty překlady!)
@app.before_request
def before_request():
    # Získáme jazyk ze session, výchozí je 'cs'
    lang = session.get('language', 'cs')
    g.lang = lang
    # Do g.T uložíme konkrétní slovník pro daný jazyk
    g.T = ALL_TRANSLATIONS.get(lang, ALL_TRANSLATIONS.get('cs', {}))

@app.context_processor
def inject_global_vars():
    def _(key):
        # Funkce pro překlad v šablonách
        return g.T.get(key, key)
    
    return {
        'dt': datetime,
        'now': datetime.datetime.now,
        '_': _,  # Tahle funkce _() teď bude fungovat v každém HTML
        'current_language': g.lang
    }

# 6. Registrace Blueprintů
app.register_blueprint(core_bp)
app.register_blueprint(projects_bp)

if __name__ == '__main__':
    # Na serveru port 5001, debug raději False, pokud nejsi v testování
    app.run(host='0.0.0.0', port=5001, debug=False)