# xmail

Outil en ligne de commande de renseignement (OSINT) sur une adresse e-mail.
À partir d'une adresse, `xmail` interroge plusieurs sources en parallèle et enregistre un rapport JSON.

## Modules

| Module    | Rôle                                                                 |
|-----------|----------------------------------------------------------------------|
| `domaine` | Enregistrements MX du domaine, détection des domaines jetables       |
| `gravatar`| Profil Gravatar public associé à l'adresse (nom, photo, liens)       |
| `comptes` | Sites où l'adresse est enregistrée, via [holehe](https://github.com/megadose/holehe) |
| `fuites`  | Fuites de données connues via Have I Been Pwned (clé API requise)    |
| `web`     | Liens de recherche (dorks) et résultats SearXNG si configuré         |

## Installation rapide

Prérequis : `python3` et `git` (Linux / macOS / WSL).

```bash
bash install.sh
```

Ou, si `install.sh` est hébergé :

```bash
curl -fsSL <url-brute-de-install.sh> | bash
```

Le script :

1. installe `holehe` avec `pipx` ;
2. clone ce dépôt dans `~/.local/share/xmail/repo` (ou le met à jour) ;
3. crée un environnement virtuel avec `requests` et `dnspython` ;
4. crée le lanceur `~/bin/xmail` et ajoute `~/bin` et `~/.local/bin` au `PATH`.

Ouvrez ensuite un nouveau terminal, ou lancez `source ~/.bashrc`.

Il peut être relancé à tout moment pour mettre l'outil à jour.

## Utilisation

```bash
xmail nom@exemple.com
xmail nom@exemple.com -o rapport.json
```

Le résultat s'affiche dans le terminal et est enregistré dans
`~/loot/xmail-<adresse>.json` par défaut, ou dans le fichier donné avec `-o`.

## Configuration (optionnelle)

Variables d'environnement, à ajouter par exemple à `~/.bashrc` :

```bash
export HIBP_API_KEY="votre_cle"               # active le module « fuites »
export SEARXNG_URL="https://searx.exemple.org" # active les résultats web
```

Sans ces variables, les modules concernés sont simplement ignorés.

## Installation manuelle (ancienne méthode)

```bash
pipx install holehe
pip install --user requests dnspython
mkdir -p ~/bin && cp xmail.py ~/bin/xmail
chmod +x ~/bin/xmail
echo 'export PATH=$HOME/bin:$HOME/.local/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
xmail nom@exemple.com
```

## Désinstallation

```bash
rm -rf ~/.local/share/xmail ~/bin/xmail
pipx uninstall holehe
```

## Usage responsable

Cet outil collecte des informations publiques liées à une adresse e-mail.
Utilisez-le uniquement sur vos propres adresses ou dans un cadre autorisé
(audit, test d'intrusion, enquête légitime), et dans le respect de la loi
et du RGPD. L'auteur décline toute responsabilité en cas de mauvais usage.
