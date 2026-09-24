import subprocess
import os
from utils import get_iterative_filename

class EditorAgent:
    def __init__(self, output_dir="./output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def merge(self, video_path, vocals_path, ost_path):
        """Assemble l'image d'origine, l'audio original séparé et la nouvelle OST avec nommage itératif."""
        final_path = get_iterative_filename(self.output_dir, "finale_video", ".mp4")
        print(f"\n[EditorAgent] Démarrage du mixage final...")
        
        if vocals_path:
            command = [
                "ffmpeg",
                "-i", video_path,
                "-i", vocals_path,
                "-i", ost_path,
                
                "-filter_complex", "[1:a]volume=1.5[v];[2:a]volume=0.9[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v",          
                "-map", "[a]",          
                "-c:v", "copy",         
                "-c:a", "aac",          
                "-b:a", "192k",
                final_path,
                "-y"                    
            ]
        else:
            command = [
                "ffmpeg",
                "-i", video_path,
                "-i", ost_path,
                "-map", "0:v",          
                "-map", "1:a",          
                "-c:v", "copy",         
                "-c:a", "aac",          
                "-b:a", "192k",
                "-shortest",            
                final_path,
                "-y"
            ]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"[EditorAgent] Montage terminé avec succès ! Vidéo finale : {final_path}")
            return final_path
            
        except subprocess.CalledProcessError as e:
            print(f"[EditorAgent] Erreur lors du montage FFmpeg : {e}")
            return None