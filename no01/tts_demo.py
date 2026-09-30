# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
# ]
# ///
import argparse
import os
import sys
import wave
from pathlib import Path

def get_client(api_key):
    from google import genai
    from google.genai import types
    return genai.Client(api_key=api_key), types


def write_wav(path: Path, pcm_data: bytes):
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(24000)
        wav.writeframes(pcm_data)

def main():
    parser = argparse.ArgumentParser(description="Gemini TTS Demo Generation")
    parser.add_argument("--only", choices=["a", "b", "c"], help="a: flat, b: tags, c: multi-speaker")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("APIキーが見つかりません。環境変数 GEMINI_API_KEY を設定してください。", file=sys.stderr)
        sys.exit(1)

    client, types = get_client(api_key)
    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir = Path("scripts")

    demos = {
        "a": {"name": "2_action1_before_flat", "type": "single", "voice": "Kore", "file": "a_flat.txt"},
        "b": {"name": "2_action1_laugh_pause", "type": "single", "voice": "Kore", "file": "b_tags.txt"},
        "c": {"name": "3_peak_radio_dialogue", "type": "multi", "file": "c_radio.txt"},
    }

    targets = [args.only] if args.only else ["a", "b", "c"]
    
    has_error = False
    for key in targets:
        demo = demos[key]
        out_path = out_dir / f"{demo['name']}.wav"
        text_path = scripts_dir / demo["file"]
        
        if not text_path.exists():
            print(f"  [Error] {text_path} が見つかりません。", file=sys.stderr)
            has_error = True
            continue

        text = text_path.read_text(encoding="utf-8")
        if demo["type"] == "single":
            contents = text.strip()
        else:
            # 話者はターンごとに speech_metadata で渡す（本文に話者名は書かない）
            parts = []
            for line in text.splitlines():
                if not line.strip() or line.startswith("#"):
                    continue
                speaker, style, body = line.split("|", 2)
                part = types.Part.from_text(text=body)
                part.speech_metadata = types.SpeechMetadata(speaker=speaker, style=style)
                parts.append(part)
            contents = [types.Content(role="user", parts=parts)]
        print(f"[{key}] {out_path.name} を生成中...")
        
        if demo["type"] == "single":
            speech_config = types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=demo["voice"])
                )
            )
        else:
            speech_config = types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Speaker 1",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Fenrir")
                            )
                        ),
                        types.SpeakerVoiceConfig(
                            speaker="Speaker 2",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                            )
                        )
                    ]
                )
            )

        config = types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=speech_config
        )

        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash-tts',
                contents=contents,
                config=config
            )
            
            audio_bytes = b""
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        audio_bytes = part.inline_data.data
                        break
            
            if audio_bytes:
                write_wav(out_path, audio_bytes)
                print("  完了")
            else:
                print("  [Error] 音声データがレスポンスに含まれていません。", file=sys.stderr)
                has_error = True
                
        except Exception as e:
            print(f"  [Error] API呼び出し失敗: {e}", file=sys.stderr)
            has_error = True

    if has_error:
        sys.exit(1)

if __name__ == "__main__":
    main()
