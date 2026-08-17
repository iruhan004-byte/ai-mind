import os
import subprocess
from pydub import AudioSegment

DOWNLOAD_DIR = "downloads"

FFMPEG_DIR = (
    r"C:\Users\MT\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0-full_build\bin"
)

YTDLP = os.path.abspath(
    r".venv\Scripts\yt-dlp.exe"
)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

AudioSegment.converter = os.path.join(
    FFMPEG_DIR, "ffmpeg.exe"
)
AudioSegment.ffprobe = os.path.join(
    FFMPEG_DIR, "ffprobe.exe"
)


def download_youtube_audio(url: str) -> str:
    print("Downloading YouTube audio...")

    command = [
        YTDLP,
        "--remote-components", "ejs:github",
        "-f", "140",
        "-o", os.path.join(
            DOWNLOAD_DIR,
            "%(title)s.%(ext)s"
        ),
        url,
    ]

    subprocess.run(command, check=True)

    # Find the newest downloaded m4a file
    files = [
        os.path.join(DOWNLOAD_DIR, f)
        for f in os.listdir(DOWNLOAD_DIR)
        if f.lower().endswith(".m4a")
    ]

    if not files:
        raise FileNotFoundError(
            "yt-dlp finished, but no M4A file was found."
        )

    input_file = max(files, key=os.path.getmtime)

    # Convert to WAV
    output_file = os.path.splitext(input_file)[0] + ".wav"

    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(output_file, format="wav")

    print(f"Downloaded audio: {output_file}")

    return output_file


def convert_to_wav(input_path: str) -> str:
    output_path = (
        os.path.splitext(input_path)[0]
        + "_converted.wav"
    )

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(output_path, format="wav")

    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start:start + chunk_ms]

        chunk_path = f"{wav_path}_chunk_{i}.wav"

        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith(("http://", "https://")):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    chunks = chunk_audio(wav_path)

    print(f"Audio ready — {len(chunks)} chunk(s) created.")

    return chunks