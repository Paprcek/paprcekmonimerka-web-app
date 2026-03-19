# 🌐 Hybrid Web Ecosystem: Django & Flask

Vítejte v mém digitálním prostoru. Tento projekt je modulární platforma postavená na Pythonu, kde využívám **Django** pro herní moduly a **Flask** pro prezentaci služeb a portfolia.

## 🚀 Moje vize: Technologie, které vrací čas
Věřím, že smyslem programování je eliminovat zbytečnou ruční práci. I když je tento web mým osobním portfoliem, slouží jako základna pro mé širší zaměření na:
* **Automatizaci:** Hledání cest, jak stroje mohou dělat nudnou práci za lidi.
* **Efektivitu:** Minimalistický přístup k vývoji a správě systémů.

## 🏗️ Architektura systému
Systém běží v **Dockeru** na vlastním **Ubuntu serveru**:

### 🎮 Django Core
Využívám Django pro herní sekci webu. Aktuálně slouží k efektivní správě databáze výsledků (nejlepší časy) pomocí Django ORM. Je to připravený základ pro budoucí implementaci uživatelských profilů.

### 💼 Flask Microservices
Flask obsluhuje mé portfolio a externí API volání. 
* **Watchdog Landing Page:** Prezentace mé služby pro monitoring dat u e-shopových dodavatelů.

## 🛠️ Technický Stack (tohoto projektu)
* **Jazyky & Frameworky:** Python (Django, Flask)
* **Databáze:** SQL (přes Django ORM / SQLite)
* **Frontend:** Jinja2, HTML5, CSS (Tailwind)
* **Infrastruktura:** Docker, Linux (Ubuntu), Git

## 📈 Služba Watchdog
Mimo tento web se věnuji vývoji nástroje **Watchdog**. Jde o řešení pro monitoring změn cen a skladu tam, kde chybí standardní API/XML rozhraní. V rámci této služby využívám techniky jako:
* **Web Scraping** (získávání dat z HTML)
* **ETL procesy** (čištění a transformace dat)
* **Automatizované notifikace** (E-mail)
