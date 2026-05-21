# CI/CD – paprcekmonimerka-web-app

## Architektura

```
git push origin main
       |
       v
GitHub Actions (detekce pushnutí do main)
       |
       v
Self-hosted runner na Buzzu (~/actions-runner/)
       |
       +-- git fetch + reset --hard origin/main
       +-- docker compose up --build -d flask_web django_game
       |
       v
Web běží na paprcekmonimerka.cz (Cloudflare Tunnel → Docker)
```

## Server – Buzz

| Parametr | Hodnota |
|---|---|
| IP | 192.168.0.76 |
| User | monika |
| Repo na serveru | `~/docker_projects/paprcek_project/` |
| Docker compose | `~/docker_projects/docker-compose.yml` |
| Runner | `~/actions-runner/` (systemd služba) |
| Routing | Cloudflare Tunnel (bez Nginx) |

## Workflow soubor

`.github/workflows/deploy.yml` – spouští se při každém push do `main`.

```yaml
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: self-hosted
    steps:
      - name: Pull latest code
        run: |
          cd ~/docker_projects/paprcek_project
          git fetch origin main
          git reset --hard origin/main

      - name: Rebuild and restart containers
        run: |
          cd ~/docker_projects
          docker compose up --build -d flask_web django_game
```

**Proč `reset --hard` místo `pull`:**  
`git pull` selže pokud má server lokální commity (divergentní branch). `reset --hard` vždy srovná server přesně s GitHubem.

## Runner – správa

Runner běží jako systemd služba, startuje automaticky po restartu Buzzu.

```bash
# Stav runneru
sudo systemctl status actions.runner.*

# Restart runneru
sudo systemctl restart actions.runner.*
```

Stav runneru lze ověřit i na GitHubu:  
`Settings → Actions → Runners` – runner "buzz" musí být **Online**.

## Větve

| Branch | Účel |
|---|---|
| `main` | Produkce – každý push = automatický deploy |
| `chatbot` | Rozdělaná práce na chatbotu – deployuje se až po mergi do main |

## Postup při vývoji

```bash
# Lokálně pracuj na feature branch nebo main
git add .
git commit -m "popis změny"
git push origin main   # ← tím se automaticky nasadí na web
```

## Troubleshooting

**Runner je offline:**
```bash
ssh monika@192.168.0.76
cd ~/actions-runner
./run.sh   # spustit ručně pro debug
```

**Deploy selhal – zobrazení logů:**
```bash
gh run list --repo Paprcek/paprcekmonimerka-web-app
gh run view <run-id> --log-failed
```

**Kontejner nesběhl správně:**
```bash
ssh monika@192.168.0.76
docker logs paprcek_flask_web
docker logs paprcek_django_game
```
