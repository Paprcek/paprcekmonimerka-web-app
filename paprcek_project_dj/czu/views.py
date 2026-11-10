import random
from pathlib import Path

from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_control

from .registry import SUBJECTS, semesters

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
ASSET_NAMES = {'engine.js', 'mlg.js'}


def _asset_version():
    # mění se s obsahem JS → po deployi prohlížeč nestáhne starou verzi z cache
    return int(max((ASSETS_DIR / n).stat().st_mtime for n in ASSET_NAMES))


def _subject(slug):
    try:
        return SUBJECTS[slug]
    except KeyError:
        raise Http404('Neznámý předmět')


def index(request):
    return render(request, 'czu/index.html', {'semesters': semesters()})


def subject(request, slug):
    s = _subject(slug)
    return render(request, 'czu/subject.html', {
        'slug': slug, 's': s, 'tests': range(1, s['tests'] + 1),
    })


def random_test(request, slug):
    _subject(slug)
    return redirect('czu:test', slug=slug, seed=random.randint(100, 99999))


def test(request, slug, seed):
    s = _subject(slug)
    if seed < 1 or seed > 99999:
        raise Http404()
    title = f'Cvičný test {seed}' if seed <= s['tests'] else f'Náhodný test #{seed}'
    next_url = reverse('czu:test', args=[slug, seed + 1]) if seed < s['tests'] else reverse('czu:random', args=[slug])
    return render(request, 'czu/test.html', {
        'slug': slug, 's': s, 'seed': seed, 'title': title, 'next_url': next_url,
        'v': _asset_version(),
    })


@cache_control(public=True, max_age=300)
def asset(request, name):
    # JS se servíruje přes Django view, protože /static/ na produkci obsluhuje Flask
    if name not in ASSET_NAMES:
        raise Http404()
    return HttpResponse((ASSETS_DIR / name).read_text(encoding='utf-8'),
                        content_type='application/javascript; charset=utf-8')
