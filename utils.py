import os
import subprocess

def get_iterative_filename(directory, prefix, extension):
    """Cherche le dernier indice 'i' dans le dossier et retourne le chemin pour le fichier 'i+1'."""
    os.makedirs(directory, exist_ok=True)
    i = 1
    while True:
        filename = f"{prefix}_{i}{extension}"
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            return filepath
        i += 1

def sanitize_audio_prompt(prompt_text):
    """Remplacement des mots-clés violents qui déclenchent les filtres de sécurité des IA audio."""
    sensitive_words = {
        "battle": "dramatic sequence",
        "combat": "fast-paced sequence",
        "explosive": "sudden bursting",
        "aggressive": "powerful and bold",
        "distress": "high tension",
        "violence": "intensity",
        "blood": "drama",
        "fight": "struggle",
        "kill": "overcome",
        "gun": "percussive hit"
    }
    
    safe_prompt = prompt_text.lower()
    for word, replacement in sensitive_words.items():
        safe_prompt = safe_prompt.replace(word, replacement)
        
    return safe_prompt

def create_vlm_proxy(clean_video_path, output_dir):
    """Crée une version basse résolution avec le chronomètre incrusté pour aider le VLM."""
    print("\n[Pré-traitement] Création du Proxy Vidéo avec Timecode pour l'IA...")
    proxy_path = get_iterative_filename(output_dir, "vlm_proxy_timecode", ".mp4")
    
    command = [
        "ffmpeg", "-i", clean_video_path,
        "-vf", "scale=854:480,drawtext=text='%{eif\\:t\\:d} s':x=w-tw-20:y=h-th-20:fontsize=48:fontcolor=white:box=1:boxcolor=black@0.8",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-an",
        proxy_path, "-y"
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proxy_path

def create_clean_master(input_path, output_dir):
    """Règle le problème de décalage A/V en ré-encodant la vidéo proprement."""
    print("\n[Pré-traitement] Création du Master Vidéo propre (Synchronisation à 0)...")
    clean_path = get_iterative_filename(output_dir, "clean_master", ".mp4")
    
    command = [
        "ffmpeg", "-i", input_path,
        "-c:v", "libx264", "-preset", "ultrafast",
        "-c:a", "aac",
        "-async", "1",
        clean_path, "-y"
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return clean_path