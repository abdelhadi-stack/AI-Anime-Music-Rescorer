import argparse
import os
import subprocess
from dotenv import load_dotenv

from vision_agent import VisionAgent
from audio_agent import AudioAgent
from separator_agent import SeparatorAgent
from editor_agent import EditorAgent
from utils import (
    sanitize_audio_prompt, 
    create_vlm_proxy, 
    create_clean_master, 
    get_iterative_filename
)

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="AI Anime Re-Scoring Pipeline: Vision, Audio, Separation & Editing.")
    parser.add_argument("-i", "--input", required=True, help="Chemin vers la vidéo source (.mp4)")
    parser.add_argument("-o", "--output", default="./output", help="Dossier de sortie")
    parser.add_argument("--audio_mode", choices=["speech", "sfx", "both", "none"], default="both",
                        help="Éléments audio à conserver de la vidéo originale (défaut: both)")
    parser.add_argument("--has_bgm", type=bool, default=True, action=argparse.BooleanOptionalAction,
                        help="Indique si la vidéo contient une musique à supprimer (Défaut: True)")
    parser.add_argument("--merl_dir", required=True, help="Chemin vers le dossier cocktail-fork-separation")
    
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    clean_video_path = create_clean_master(args.input, args.output)

    print("\n=== ÉTAPE 1 : ANALYSE VLM ===")
    vision = VisionAgent(model_name="gemini-3.5-flash-lite")
    proxy_video_path = create_vlm_proxy(clean_video_path, args.output)
    
    json_analysis, total_duration_sec = vision.analyze_video(proxy_video_path)
    print(json_analysis)

    print("\n=== ÉTAPE 2 : FORMATAGE DU PROMPT AUDIO ===")
    base_prompt = (
        f"Genre: {json_analysis['music_prompt']}. "
        f"Mood: {json_analysis['dominant_mood']}. "
        f"Tempo: {json_analysis['suggested_bpm']} BPM. "
        f"Total duration: {total_duration_sec} seconds.\n\n"
    )

    timeline_str = ""
    timeline_events = json_analysis['timeline']
    
    for i in range(len(timeline_events)):
        start_sec = timeline_events[i]['timestamp_sec']
        
        if i + 1 < len(timeline_events):
            end_sec = timeline_events[i+1]['timestamp_sec']
        else:
            if start_sec < total_duration_sec:
                end_sec = total_duration_sec
            else:
                end_sec = start_sec + 5 
            
        start_m, start_s = divmod(start_sec, 60)
        end_m, end_s = divmod(end_sec, 60)
        
        direction = timeline_events[i].get('musical_direction', '')
        structure = timeline_events[i]['intensity'].upper()
        
        timeline_str += f"[{start_m}:{start_s:02d} - {end_m}:{end_s:02d}] [{structure}] {direction}.\n"

    lyria_prompt = base_prompt + timeline_str
    safe_lyria_prompt = sanitize_audio_prompt(lyria_prompt)
    print("Prompt sécurisé pour l'API Audio :\n" + safe_lyria_prompt)

    print("\n=== ÉTAPE 3 : GÉNÉRATION AUDIO (LYRIA) ===")
    audio_agent = AudioAgent()
    ost_path = audio_agent.generate_ost(safe_lyria_prompt, args.output) 
    
    if not ost_path or not os.path.exists(ost_path):
        print("\n[ERREUR CRITIQUE] L'Agent Audio n'a pas pu générer la musique.")
        print("Arrêt du pipeline pour éviter de faire planter FFmpeg.")
        return 

    original_audio_path = None
    if args.audio_mode != "none":
        if args.has_bgm:
            print(f"\n=== ÉTAPE 4 : SÉPARATION IA (Suppression de l'OST via MERL) ===")
            separator = SeparatorAgent(
                output_dir=os.path.join(args.output, "separated"), 
                merl_dir=args.merl_dir
            )
            original_audio_path = separator.extract_audio(clean_video_path, mode=args.audio_mode)
        else:
            print(f"\n=== ÉTAPE 4 : EXTRACTION RAPIDE (Pas de musique détectée) ===")
            original_audio_path = get_iterative_filename(args.output, "extracted_original_audio", ".wav")
            subprocess.run([
                "ffmpeg", "-i", clean_video_path, "-vn", "-acodec", "pcm_s16le", original_audio_path, "-y"
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("\n=== ÉTAPE 4 : EXTRACTION AUDIO IGNORÉE (Mode 'none') ===")

    print("\n=== ÉTAPE 5 : MONTAGE FINAL ===")
    editor = EditorAgent(output_dir=args.output)
    editor.merge(
        video_path=clean_video_path,
        vocals_path=original_audio_path,
        ost_path=ost_path
    )

if __name__ == "__main__":
    main()