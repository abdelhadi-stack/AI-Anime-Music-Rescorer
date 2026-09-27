# 🎵 AI Anime Music Rescorer (Multi-Agent Pipeline)

Experimental AI-driven pipeline to analyze a video scene, remove its original music while preserving dialogues and sound effects (SFX), and then generate and synchronize a new soundtrack adapted to the action and emotion.

> ⚠️ **Status:** Experimental prototype. The quality of audio separation and musical synchronization may vary depending on the scenes and models used.

## 🚀 Architecture

- **VisionAgent (Gemini)**: Analyzes a timecoded video proxy to identify transitions, rhythm, and the emotional arc, then produces a time-stamped musical prompt.
- **AudioAgent (Lyria/Replicate)**: Generates a new soundtrack from the prompt.
- **SeparatorAgent (MERL Cocktail-Fork)**: Separates the original music from voices and SFX.
- **EditorAgent (FFmpeg)**: Assembles the video, preserved audio elements, and the new music, adjusting their duration and volumes.

### Processing Flow

```text
Source Video
   │
   ├──► Video Proxy with timecodes
   │          └──► VisionAgent (Gemini)
   │                     └──► Time-stamped musical prompt
   │                                └──► AudioAgent (Lyria/Replicate)
   │                                           └──► New OST
   │
   ├──► SeparatorAgent (MERL, if original music is present)
   │          └──► Voices + SFX
   │
   └──► EditorAgent (FFmpeg)
              └──► Final rescored video
```

## 🛠️ Prerequisites

- Python 3.8 or higher.
- FFmpeg installed and accessible from your system's `PATH`.
- Git and Git LFS to fetch the large files required for the MERL separator.
- A [Google AI Studio](https://aistudio.google.com/) account to get a Gemini API key.
- A [Replicate](https://replicate.com/) account to get an audio generation API token.

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/abdelhadi-stack/AI-Anime-Music-Rescorer.git
cd ai-anime-music-rescorer
```

### 2. Create a virtual environment

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 3. Install MERL Cocktail-Fork

From the project root:

```bash
git clone https://github.com/merlresearch/cocktail-fork-separation.git
cd cocktail-fork-separation
git lfs install
git lfs pull
python -m pip install -r requirements.txt
cd ..
```

### 4. Install project dependencies

```bash
python -m pip install -r requirements.txt
```

## 🔑 API Keys Configuration

Create an API key in [Google AI Studio](https://aistudio.google.com/) and an API token on [Replicate](https://replicate.com/). At the root of the project, create a `.env` file:

```dotenv
GEMINI_API_KEY=your_gemini_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
```

## 🎮 Usage

### Run the complete pipeline

```bash
python main.py -i "./video_test.mp4" --merl_dir "./cocktail-fork-separation"
```

### Choose output folder and preserved audio elements

```bash
python main.py \
  -i "./video_test.mp4" \
  --merl_dir "./cocktail-fork-separation" \
  --output "./output/episode_01" \
  --audio_mode both
```

### Process a video without original music

If the video does not contain any music that needs to be removed, disable the audio separation:

```bash
python main.py \
  -i "./video_test.mp4" \
  --merl_dir "./cocktail-fork-separation" \
  --no-has_bgm
```

## ⚙️ Command-Line Arguments

| Argument             | Required | Default Value      | Description                                                              |
| -------------------- | -------- | ------------------ | ------------------------------------------------------------------------ |
| `-i`, `--input`      | Yes      | —                  | Path to the source video (`.mp4`, `.mkv`, etc.).                         |
| `--merl_dir`         | Yes      | —                  | Path to the local MERL Cocktail-Fork folder.                             |
| `-o`, `--output`     | No       | `./output`         | Output folder for generated files.                                       |
| `--audio_mode`       | No       | `both`             | Original audio to preserve: `speech`, `sfx`, `both`, or `none`.          |
| `--no-has_bgm`       | No       | Disabled           | Indicates there is no original music and bypasses MERL.                  |

Possible values for `--audio_mode`:

- `speech`: Keeps dialogues and voices.
- `sfx`: Keeps sound effects.
- `both`: Keeps both dialogues and sound effects.
- `none`: Does not keep any original audio elements.

## 🔄 Execution Flow

1. Creation of a lightweight video proxy with embedded timecode.
2. Scene analysis by Gemini: rhythm, transitions, events, and emotional arc.
3. Construction of a time-stamped musical prompt.
4. Generation of the new soundtrack via Replicate.
5. Optional separation of dialogues and SFX from the original music via MERL.
6. Mixing and assembly with FFmpeg.
7. Saving intermediate files and the final video to the output folder.

## 🐛 Troubleshooting

### FFmpeg is not found

Check its installation and accessibility:

```bash
ffmpeg -version
```

If the command fails, install FFmpeg using your system's package manager, then open a new terminal.

### An API key is not detected

- Ensure that the `.env` file is located in the same folder as `main.py`.
- Check the spelling of `GEMINI_API_KEY` and `REPLICATE_API_TOKEN`.
- Remove any extra spaces or quotes around the values.

### MERL or Git LFS files are missing

From the separator folder:

```bash
git lfs install
git lfs pull
```

## 🗺️ Roadmap

- [ ] Adapt musical prompts to the scene's genre: action, romance, thriller, etc.
- [ ] Automatically detect musical segments and silences.
- [ ] Create a graphical user interface (GUI) to load and process videos.
- [ ] Support batch processing.

## ⚖️ License

This project is licensed under the MIT License.

Third-party models and services may be subject to separate licenses and terms of use. Please review the terms for Gemini, Replicate, and MERL Cocktail-Fork prior to any commercial use.