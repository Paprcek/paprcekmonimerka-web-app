# modules/core.py
from flask import Blueprint, render_template, g, session, redirect, url_for, request, current_app, flash
from flask_mail import Message
from extensions import mail


# Vytvoříme Blueprint (mini-aplikaci)
core_bp = Blueprint('core', __name__)

@core_bp.route('/')
def index():
    return render_template('index.html')

@core_bp.route('/about')
def about():
    return render_template('about.html')

@core_bp.route('/gdpr')
def gdpr():
    return render_template('gdpr.html')

@core_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    """Stránka s kontaktním formulářem a údaji."""
    if request.method == 'POST':
        gdpr_consent = request.form.get('gdpr')

        if not gdpr_consent:
            flash('Pro odeslání paprsku je nutné souhlasit se zpracováním údajů.', 'error')
            return redirect(url_for('core.contacts'))

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

        return redirect(url_for('core.contacts'))

    return render_template('contacts.html')

@core_bp.route('/lang/<language>') # Zkráceno na /lang/
def set_language(language):
    session['language'] = language
    session.modified = True
    return redirect(request.referrer or url_for('core.index'))