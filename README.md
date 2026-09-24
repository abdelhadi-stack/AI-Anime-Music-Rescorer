# 🎵 AI Anime Music Rescorer (pipeline multi-agents)

Pipeline expérimental piloté par l'IA pour analyser une scène vidéo, retirer sa musique d'origine tout en conservant les dialogues et les bruitages (SFX), puis générer et synchroniser une nouvelle bande-son adaptée à l'action et à l'émotion.

> ⚠️ **Statut :** prototype expérimental. La qualité de la séparation audio et de la synchronisation musicale peut varier selon les scènes et les modèles utilisés.

## 🚀 Architecture

- **VisionAgent (Gemini)** : analyse un proxy vidéo horodaté pour identifier les transitions, le rythme et l'arc émotionnel, puis produit un prompt musical structuré dans le temps.
- **AudioAgent (Lyria/Replicate)** : génère une nouvelle bande-son à partir du prompt.
- **SeparatorAgent (MERL Cocktail-Fork)** : sépare la musique d'origine des voix et des bruitages.
- **EditorAgent (FFmpeg)** : assemble la vidéo, les éléments audio conservés et la nouvelle musique, en ajustant leur durée et leurs volumes.

### Flux de traitement

```text
Vidéo source
   │
   ├──► Proxy vidéo avec timecodes
   │          └──► VisionAgent (Gemini)
   │                     └──► Prompt musical horodaté
   │                                └──► AudioAgent (Lyria/Replicate)
   │                                           └──► Nouvelle OST
   │
   ├──► SeparatorAgent (MERL, si musique d'origine présente)
   │          └──► Voix + SFX
   │
   └──► EditorAgent (FFmpeg)
              └──► Vidéo finale rescorée
```

## 🛠️ Prérequis

- Python 3.8 ou version supérieure.
- FFmpeg installé et accessible depuis le `PATH`.
- Git et Git LFS pour récupérer les fichiers volumineux du séparateur MERL.
- Un compte [Google AI Studio](https://aistudio.google.com/) pour obtenir une clé API Gemini.
- Un compte [Replicate](https://replicate.com/) pour obtenir un jeton API de génération audio.

## 📦 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/abdelhadi-stack/AI-Anime-Music-Rescorer.git
cd ai-anime-music-rescorer
```

### 2. Créer un environnement virtuel

Sous Linux ou macOS :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Sous Windows PowerShell :

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3. Installer MERL Cocktail-Fork

Depuis la racine du projet :

```bash
git clone https://github.com/merlresearch/cocktail-fork-separation.git
cd cocktail-fork-separation
git lfs install
git lfs pull
python -m pip install -r requirements.txt
cd ..
```

### 4. Installer les dépendances du projet

```bash
python -m pip install -r requirements.txt
```

## 🔑 Configuration des clés API

Créez une clé API dans [Google AI Studio](https://aistudio.google.com/) et un jeton API sur [Replicate](https://replicate.com/). À la racine du projet, créez un fichier `.env` :

```dotenv
GEMINI_API_KEY=votre_cle_gemini_ici
REPLICATE_API_TOKEN=votre_token_replicate_ici
```


## 🎮 Utilisation

### Lancer le pipeline complet

```bash
python main.py -i "./video_test.mp4" --merl_dir "./cocktail-fork-separation"
```

### Choisir le dossier de sortie et les éléments audio conservés

```bash
python main.py \
  -i "./video_test.mp4" \
  --merl_dir "./cocktail-fork-separation" \
  --output "./output/episode_01" \
  --audio_mode both
```

### Traiter une vidéo sans musique d'origine

Si la vidéo ne contient pas de musique à retirer, désactivez la séparation audio :

```bash
python main.py \
  -i "./video_test.mp4" \
  --merl_dir "./cocktail-fork-separation" \
  --no-has_bgm
```

## ⚙️ Arguments de la ligne de commande

| Argument             | Requis | Valeur par défaut | Description                                                              |
| -------------------- | ------ | ------------------ | ------------------------------------------------------------------------ |
| `-i`, `--input`  | Oui    | —                 | Chemin de la vidéo source (`.mp4`, `.mkv`, etc.).                   |
| `--merl_dir`       | Oui    | —                 | Chemin du dossier local de MERL Cocktail-Fork.                           |
| `-o`, `--output` | Non    | `./output`       | Dossier de sortie des fichiers générés.                               |
| `--audio_mode`     | Non    | `both`           | Audio d'origine à conserver :`speech`, `sfx`, `both` ou `none`. |
| `--no-has_bgm`     | Non    | Désactivé        | Indique qu'il n'y a pas de musique d'origine et ignore MERL.             |

Valeurs possibles pour `--audio_mode` :

- `speech` : conserve les dialogues et les voix.
- `sfx` : conserve les bruitages.
- `both` : conserve les dialogues et les bruitages.
- `none` : ne conserve aucun élément audio d'origine.

## 🔄 Déroulement de l'exécution

1. Création d'un proxy vidéo allégé avec timecode incrusté.
2. Analyse de la scène par Gemini : rythme, transitions, événements et arc émotionnel.
3. Construction d'un prompt musical horodaté.
4. Génération de la nouvelle bande-son via Replicate.
5. Séparation éventuelle des dialogues et bruitages de la musique d'origine via MERL.
6. Mixage et assemblage avec FFmpeg.
7. Enregistrement des fichiers intermédiaires et de la vidéo finale dans le dossier de sortie.

## 🐛 Dépannage

### FFmpeg est introuvable

Vérifiez son installation et son accessibilité :

```bash
ffmpeg -version
```

Si la commande échoue, installez FFmpeg avec le gestionnaire de paquets de votre système, puis ouvrez un nouveau terminal.

### Une clé API n'est pas détectée

- Vérifiez que `.env` se trouve dans le même dossier que `main.py`.
- Vérifiez l'orthographe de `GEMINI_API_KEY` et `REPLICATE_API_TOKEN`.
- Supprimez les espaces ou guillemets superflus autour des valeurs.

### Les fichiers MERL ou Git LFS sont manquants

Depuis le dossier du séparateur :

```bash
git lfs install
git lfs pull
```

## 🗺️ Roadmap

- [ ] Adapter les prompts musicaux au genre de la scène : action, romance, thriller, etc.
- [ ] Détecter automatiquement les segments musicaux et les silences.
- [ ] Créer une interface graphique pour charger et traiter les vidéos.
- [ ] Prendre en charge le traitement par lots.

## ⚖️ Licence

Ce projet est distribué sous licence MIT.

Les services et modèles tiers peuvent être soumis à des licences et conditions d'utilisation distinctes. Vérifiez celles de Gemini, Replicate et MERL Cocktail-Fork avant toute utilisation commerciale.
