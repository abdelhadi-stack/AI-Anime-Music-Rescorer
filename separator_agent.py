import subprocess
import os
from utils import get_iterative_filename

class SeparatorAgent:
    def __init__(self, output_dir="./output/separated", merl_dir=None):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        if not merl_dir or not os.path.exists(merl_dir):
            raise FileNotFoundError(f"Le dossier MERL spécifié est introuvable : {merl_dir}")
            
        self.merl_dir = os.path.abspath(merl_dir)
        self.merl_script_path = os.path.join(self.merl_dir, "separate.py") 

    def extract_audio(self, video_path, mode="both"):
        print("[SeparatorAgent] Lancement de MERL Cocktail Fork Separation...")
        
        temp_wav = os.path.join(self.output_dir, "temp_input.wav")
        subprocess.run(["ffmpeg", "-i", video_path, "-vn", temp_wav, "-y"], check=True, stdout=subprocess.DEVNULL)
        
        command = [
            "python", self.merl_script_path, 
            "--audio-path", temp_wav,       
            "--out-dir", self.output_dir    
        ]
        
        try:
            subprocess.run(command, check=True, cwd=self.merl_dir)
            
            speech_path = os.path.join(self.output_dir, "speech.wav")
            sfx_path = os.path.join(self.output_dir, "sfx.wav")
            
            if not os.path.exists(speech_path) or not os.path.exists(sfx_path):
                raise FileNotFoundError("Les fichiers MERL (speech.wav ou sfx.wav) sont introuvables.")

            if mode == "speech":
                print(f"[SeparatorAgent] Mode 'speech' : Conservation des dialogues uniquement.")
                return speech_path
                
            elif mode == "sfx":
                print(f"[SeparatorAgent] Mode 'sfx' : Conservation des bruitages uniquement.")
                return sfx_path
                
            elif mode == "both":
                print(f"[SeparatorAgent] Mode 'both' : Fusion des voix et des bruitages...")
                combined_path = get_iterative_filename(self.output_dir, "combined_speech_sfx", ".wav")
                mix_cmd = [
                    "ffmpeg",
                    "-i", speech_path,
                    "-i", sfx_path,
                    "-filter_complex", "[0:a]volume=3.0[v];[1:a]volume=2.0[s];[v][s]amix=inputs=2:duration=longest:normalize=0",
                    "-c:a", "pcm_s16le", 
                    combined_path,
                    "-y"
                ]
                subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return combined_path
            
        except subprocess.CalledProcessError as e:
            print(f"[SeparatorAgent] Erreur lors de l'exécution de MERL : {e}")
            return None