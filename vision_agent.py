import time
import json
import cv2
from google import genai
from pydantic import BaseModel, Field

class TimelineEvent(BaseModel):
    timestamp_sec: int = Field(description="The exact second this event happens.")
    intensity: str = Field(description="Musical structure: 'Intro', 'Build-up', 'Climax', 'Drop', 'Outro'")
    musical_direction: str = Field(description="Strict musical instructions for this segment (e.g., 'Sudden choir crescendo with heavy brass', 'Drop to solo piano', 'Fast staccato strings start'). NO visual descriptions here.")
    visual_context: str = Field(description="Very brief 2-4 words summarizing the visual context (e.g., 'Mecha explosions', 'Character shouting')")

class VideoMusicAnalysis(BaseModel):
    scene_summary: str = Field(description="A brief summary of the scene's visual action and atmosphere")
    dominant_mood: str = Field(description="The primary emotion or mood")
    pacing: str = Field(description="The speed of the scene cuts and action")
    suggested_bpm: int = Field(description="Suggested musical tempo in Beats Per Minute")
    instruments: list[str] = Field(description="List of suggested instruments")
    music_prompt: str = Field(description="A detailed musical prompt for MusicGen. Do NOT use comma-separated tags. Write 2-3 full sentences describing the primary genre, the specific instruments playing (e.g., 'rapid staccato strings', 'booming taiko drums'), the rhythmic pacing, and the sonic texture.")
    timeline: list[TimelineEvent] = Field(description="Key visual moments in the video to synchronize music drops")

class VisionAgent:
    def __init__(self, model_name="gemini-1.5-flash"):
        self.client = genai.Client()
        self.model_name = model_name

    def _get_video_duration(self, video_path):
        """Méthode interne pour calculer la durée de la vidéo en secondes."""
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_sec = int(frame_count / fps)
        video.release()
        return duration_sec

    def analyze_video(self, video_path):
        """Upload la vidéo, l'analyse et retourne un dictionnaire Python."""
        duration_sec = self._get_video_duration(video_path)
        print(f"[VisionAgent] Durée de la vidéo : {duration_sec} sec.")

        print("[VisionAgent] Upload de la vidéo...")
        video_file = self.client.files.upload(file=video_path)

        print("[VisionAgent] Traitement côté serveur Google...")
        while video_file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = self.client.files.get(name=video_file.name)

        if video_file.state.name == "FAILED":
            raise Exception("[VisionAgent] Erreur de traitement vidéo côté serveur.")

        print("\n[VisionAgent] Lancement de l'analyse musicale...")
        
        prompt = f"""
        You are an expert AI Music Director and composer scoring an anime video. 
        The video provided may already have a musical track (OST) — you MUST STRICTLY IGNORE the existing music. 

        CRITICAL CONSTRAINTS:
        - The video is EXACTLY {duration_sec} seconds long.
        - All timeline timestamps MUST strictly fall between 0 and {duration_sec}.
        - Never output an event timestamp greater than {duration_sec}.
        - Focus only on the 4 to 6 most critical pacing/intensity transitions.

        ADAPTIVE GENRE SCORING (AVOID BIAS):
        You must adapt your musical choices STRICTLY to the actual genre and emotion of the scene. Do NOT force epic, action, or battle music if the scene is peaceful, emotional, or conversational.
        - If Action/Battle: Fast BPM, heavy percussion, intense orchestral or rock, aggressive.
        - If Sad/Emotional/Romance: Low BPM, slow soft piano, ambient strings, melancholic or touching.
        - If Slice of Life/Comedy: Upbeat bouncy rhythm, playful pizzicato, acoustic guitar, lighthearted.
        - If Mystery/Tension: Slow creeping tempo, dark synth pads, dissonant chords, suspenseful.

        Base your analysis SOLELY on:
        1. Visual context (movement, environment, lighting, character facial expressions, tears, smiles).
        2. Sound effects (SFX like wind, footsteps, explosions, or absolute silence).
        3. Dialogues (tone of voice: shouting, crying, whispering, laughing).

        Analyze the emotional arc, the pacing, and the intensity peaks of the scene. 
        Your goal is to provide a structured JSON analysis that will be sent to an AI Music Generator to create a brand new, highly synchronized OST that perfectly fits the video's TRUE mood.
        """

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[prompt, video_file],
            config={
                "response_mime_type": "application/json",
                "response_json_schema": VideoMusicAnalysis.model_json_schema(),
            },
        )
        
        return json.loads(response.text), duration_sec