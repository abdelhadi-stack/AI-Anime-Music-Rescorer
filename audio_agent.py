import replicate
import os
from utils import get_iterative_filename

class AudioAgent:
    def __init__(self):
        self.model_id = "google/lyria-3-pro"

    def generate_ost(self, music_prompt, output_dir="./output"):
        """Génère la musique via l'API Replicate et la sauvegarde sur le disque avec un nom itératif."""
        output_path = get_iterative_filename(output_dir, "ost_ai_genere", ".mp3")
        
        print(f"[AudioAgent] Démarrage de la génération musicale...")
        print(f"[AudioAgent] Prompt : {music_prompt}")

        try:
            output = replicate.run(
                self.model_id,
                input={
                    "prompt": music_prompt,
                }
            )

            print(f"[AudioAgent] Musique générée ! Téléchargement vers {output_path}...")
            
            with open(output_path, "wb") as file:
                file.write(output.read())
                
            print(f"[AudioAgent] Sauvegarde réussie : {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[AudioAgent] Erreur lors de la génération : {e}")
            return None