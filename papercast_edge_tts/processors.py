from papercast.base import BaseProcessor
import asyncio
import edge_tts
from edge_tts import VoicesManager
from papercast.production import Production
from pathlib import Path
from papercast.types import PathLike


class EdgeTTSProcessor(BaseProcessor):
    input_types = {"text": str, "title": str}
    output_types = {"mp3_path": str}

    def __init__(self, mp3_dir: PathLike, txt_dir: PathLike):
        self.mp3_dir = Path(mp3_dir)
        self.txt_dir = Path(txt_dir)
        if not self.mp3_dir.exists():
            self.mp3_dir.mkdir(parents=True)
        if not self.txt_dir.exists():
            self.txt_dir.mkdir(parents=True)

    def narrate(self, text: str, title: str) -> str:
        txt_path = self.txt_dir / f"{title}.txt"
        mp3_path = self.mp3_dir / f"{title}.mp3"
        
        with open(txt_path, "w") as f:
            f.write(text)
            
        # Run the async function to generate speech
        asyncio.run(self._generate_speech(text, str(mp3_path)))
            
        return str(mp3_path)
    
    async def _generate_speech(self, text: str, output_file: str) -> None:
        """Generate speech using Edge TTS"""
        voices = await VoicesManager.create()
        voice = voices.find(Gender="Male", Language="en")
        
        communicate = edge_tts.Communicate(text, voice[0]["Name"])
        await communicate.save(output_file)

    def process(self, input: Production, method=None, **kwargs) -> Production:
        input.mp3_path = self.narrate(input.text, input.title)
        return input