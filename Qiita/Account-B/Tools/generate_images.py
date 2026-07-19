"""
Gemini(Nano Banana)で記事用の画像をまとめて生成するスクリプト。

事前準備:
1. Google AI Studio (https://aistudio.google.com/apikey) でAPIキーを取得する
   ※無料枠あり。1024x1024で1日あたり500枚まで無料（2026年7月時点）。
2. このスクリプトを実行する自分のPC（またはローカル環境）で、
   環境変数 GEMINI_API_KEY にそのキーを設定する。
   例（Mac/Linuxのターミナル）:
       export GEMINI_API_KEY="ここに自分のAPIキー"
   例（Windows PowerShell）:
       $env:GEMINI_API_KEY="ここに自分のAPIキー"
   ※ APIキーはこのファイルやチャットには直接書き込まないこと。
3. 依存パッケージをインストールする:
       pip install google-genai --break-system-packages
4. 下の IMAGES リストに、作りたい画像のファイル名とプロンプトを追加する。
5. python generate_images.py を実行する。
   生成された画像は OUTPUT_DIR に保存される。

使い方の想定:
- 記事のプレースホルダー（例:【サムネ】）に対応する画像を、この設定リストに
  1件ずつ追加してから実行する。
- 生成後、OUTPUT_DIR内の画像をQiitaの記事に実際にアップロードし、
  発行されたURLで本文の画像リンクを差し替える（Qiitaは外部からの直リンク
  貼り付けができないため、Qiita上に一度アップロードする必要がある）。
"""

import os
import sys
from pathlib import Path

from google import genai
from google.genai import types

# ---- ここを編集する ----------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "generated_images"

# (出力ファイル名, プロンプト, アスペクト比) のリスト
# アスペクト比は "1:1" "4:3" "3:4" "16:9" "9:16" などから選ぶ
IMAGES = [
    {
        "filename": "sample_thumbnail.png",
        "prompt": (
            "かわいいタイガーのマスコットキャラクターが、パソコンの前で"
            "困った顔をしているシンプルなフラットイラスト。"
            "背景は明るいオレンジ系の単色。Qiita記事のサムネイル向け。"
        ),
        "aspect_ratio": "16:9",
    },
    # 必要な分だけ追加する
    # {
    #     "filename": "sample_body_image.png",
    #     "prompt": "...",
    #     "aspect_ratio": "4:3",
    # },
]

# モデル名（2026年7月時点の推奨: Nano Banana系）
MODEL = "gemini-2.5-flash-image"

# ------------------------------------------------------------------------


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(
            "エラー: 環境変数 GEMINI_API_KEY が設定されていません。\n"
            "自分のAPIキーを環境変数として設定してから実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for item in IMAGES:
        print(f"生成中: {item['filename']} ...")
        response = client.models.generate_content(
            model=MODEL,
            contents=item["prompt"],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=item.get("aspect_ratio", "1:1"),
                ),
            ),
        )

        saved = False
        for part in response.parts:
            if part.inline_data:
                image = part.as_image()
                out_path = OUTPUT_DIR / item["filename"]
                image.save(out_path)
                print(f"  -> 保存しました: {out_path}")
                saved = True
                break

        if not saved:
            print(f"  -> 画像が生成されませんでした: {item['filename']}")

    print("完了しました。")


if __name__ == "__main__":
    main()
