# Gemini TTS入門 サンプルリポジトリ

動画「Gemini TTS入門」のサンプルコードとスクリプトです。

## 必要なもの
- Gemini API キー
- uv

## 使い方
環境変数 `GEMINI_API_KEY` を設定して `uv run tts_demo.py` を実行するだけです。
```bash
GEMINI_API_KEY="AIza..." uv run tts_demo.py
```
（出力は `./out/` に書き出されます）

## 入っているもの
- 実演 a: 素読み（`scripts/a_flat.txt`）
- 実演 b: 笑いと間のタグ（`<laugh>` `<short pause>`）（`scripts/b_tags.txt`）
- 実演 c: 2人の掛け合い（`scripts/c_radio.txt`）

## 注意
- API の無料枠は1日10回が上限です（2026-09-30 時点）。
- 数字は変わることがあるので、上限は自分で確かめてください。
- 生成した音声の扱いはGoogleの利用規約に従ってください。

動画: https://youtu.be/n0EtEmKkKAo （2026-10-01 07:00 公開）
