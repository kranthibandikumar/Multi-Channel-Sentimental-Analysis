import os
import speech_recognition as sr
from pydub import AudioSegment as PydubAudioSegment
import numpy as np
from pathlib import Path
import tempfile
import logging
from typing import List  # Add this import
from backend.models.data_models import AudioAnalysisResult, AudioSegment, SentimentScore
from backend.services.sentiment_analyzer import SentimentAnalyzer

ffmpeg_dir = r"C:\Users\bk85936\Downloads\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin"
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
PydubAudioSegment.converter = os.path.join(ffmpeg_dir, "ffmpeg.exe")
PydubAudioSegment.ffprobe = r"C:\Users\bk85936\Downloads\ffmpeg-8.0-full_build\ffmpeg-8.0-full_build\bin\ffprobe.exe"

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.sentiment_analyzer = SentimentAnalyzer()

    async def analyze_audio(self, file_content: bytes, filename: str) -> AudioAnalysisResult:
        try:
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name

            # Convert audio to WAV for processing
            audio = PydubAudioSegment.from_file(temp_path)  # Updated to use renamed import
            duration = len(audio) / 1000.0  # Convert to seconds

            # Split audio into 30-second segments
            segment_length = 30 * 1000  # 30 seconds in milliseconds
            segments = []
            
            for start in range(0, len(audio), segment_length):
                end = start + segment_length
                chunk = audio[start:min(end, len(audio))]
                
                # Convert chunk to wav for speech recognition
                chunk.export(temp_path, format="wav")
                
                with sr.AudioFile(temp_path) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data)
                        if text:
                            # Analyze sentiment for segment
                            sentiment_result = self.sentiment_analyzer.analyze_text(text)
                            
                            segment = AudioSegment(
                                start_time=start/1000.0,
                                end_time=min(end/1000.0, duration),
                                text=text,
                                sentiment=sentiment_result["sentiment"]
                            )
                            segments.append(segment)
                    except sr.UnknownValueError:
                        logger.warning(f"Could not understand audio segment at {start/1000.0}s")
                    except sr.RequestError as e:
                        logger.error(f"Error with speech recognition service: {str(e)}")

            # Calculate overall sentiment
            if segments:
                overall_sentiment = self._calculate_overall_sentiment(segments)
            else:
                overall_sentiment = SentimentScore(positive=0.0, negative=0.0, neutral=1.0)

            return AudioAnalysisResult(
                file_name=filename,
                duration=duration,
                segments=segments,
                overall_sentiment=overall_sentiment,
                metadata={
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "format": Path(filename).suffix[1:]
                }
            )

        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise

    def _calculate_overall_sentiment(self, segments: List[AudioSegment]) -> SentimentScore:
        positives = []
        negatives = []
        neutrals = []
        
        for segment in segments:
            if segment.sentiment:
                positives.append(segment.sentiment.positive)
                negatives.append(segment.sentiment.negative)
                neutrals.append(segment.sentiment.neutral)
        
        return SentimentScore(
            positive=np.mean(positives) if positives else 0.0,
            negative=np.mean(negatives) if negatives else 0.0,
            neutral=np.mean(neutrals) if neutrals else 1.0
        )