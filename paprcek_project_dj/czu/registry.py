"""
Registr studijních trenažérů.

Nový předmět = nový záznam v SUBJECTS + generátor v assets/<generator>.js
(window.CZU_GENERATORS['<generator>'] = function (seed) { ... }).
Engine, šablony i ukládání pokusů jsou společné pro všechny předměty.
"""

SUBJECTS = {
    'matematicka-logika': {
        'name': 'Matematická logika a grafy',
        'code': 'TAE75E / TAE41E',
        'semester': 'ZS 2026/27',
        'semester_label': '1. semestr – Informatika (kombinovaně)',
        'generator': 'mlg',
        'tests': 10,
        'time_limit_min': 50,
        'topics': [
            '1. Pravdivostní tabulka φ a ψ, ekvivalence, důsledek (10 b)',
            '2. Minimální disjunktivní tvar, 4 proměnné (10 b)',
            '3. Množinové operace na reálné ose (5 b)',
            '4. Vlastnosti relace (8 b)',
            '5. Doplnění relace na ekvivalenci / uspořádání / tranzitivní (5 b)',
        ],
        'note': 'Trenažér na první zápočtový test (výroková logika, množiny a relace). Grafy a automaty přijdou později.',
    },
}


def semesters():
    """Předměty seskupené podle semestru (pro rozcestník /czu/)."""
    out = {}
    for slug, s in SUBJECTS.items():
        out.setdefault(s['semester'], []).append({'slug': slug, **s})
    return out
