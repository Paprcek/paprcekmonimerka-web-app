"""
Registr studijních trenažérů.

Nový předmět = nový záznam v SUBJECTS + generátor v assets/<generator>.js
(window.CZU_GENERATORS['<generator>'] = function (seed) { ... }).
Engine, šablony i ukládání pokusů jsou společné pro všechny předměty.
"""

SUBJECTS = {
    'matematicka-logika': {
        'name': 'Matematická logika a grafy – 1. zápočet',
        'code': 'TAE75E / TAE41E',
        'semester': 'ZS 2026/27',
        'semester_label': '1. semestr – Informatika (kombinovaně)',
        'generator': 'mlg',
        'tests': 10,
        'time_limit_min': 50,
        'structure': '5 úloh za 38 bodů',
        'topics': [
            '1. Pravdivostní tabulka φ a ψ, ekvivalence, důsledek (10 b)',
            '2. Minimální disjunktivní tvar, 4 proměnné (10 b)',
            '3. Množinové operace na reálné ose (5 b)',
            '4. Vlastnosti relace (8 b)',
            '5. Doplnění relace na ekvivalenci / uspořádání / tranzitivní (5 b)',
        ],
        'note': 'Trenažér na první zápočtový test: výroková logika, množiny a relace.',
    },
    'grafy': {
        'name': 'Matematická logika a grafy – 2. zápočet',
        'code': 'TAE75E / TAE41E',
        'semester': 'ZS 2026/27',
        'semester_label': '1. semestr – Informatika (kombinovaně)',
        'generator': 'grf',
        'tests': 10,
        'time_limit_min': 50,
        'structure': '6 úloh za 38 bodů',
        'topics': [
            '1. Skóre grafu (2 b)',
            '2. Izomorfismus orientovaných grafů (6 b)',
            '3. Eulerovský graf (4 b)',
            '4. Prefixová a postfixová notace (6 b)',
            '5. Maximální tok a minimální řezy (10 b)',
            '6. Minimální kostra (10 b)',
        ],
        'note': 'Trenažér na druhý zápočtový test: grafy, toky v sítích, kostry a notace výrazů.',
    },
}


def semesters():
    """Předměty seskupené podle semestru (pro rozcestník /czu/)."""
    out = {}
    for slug, s in SUBJECTS.items():
        out.setdefault(s['semester'], []).append({'slug': slug, **s})
    return out
