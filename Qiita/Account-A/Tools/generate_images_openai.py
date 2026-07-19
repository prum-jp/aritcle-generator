"""
ChatGPT（OpenAI gpt-image API）で記事用の画像をまとめて生成し、
生成直後に自動で圧縮まで行うスクリプト。

事前準備:
1. OpenAI（https://platform.openai.com/api-keys）でAPIキーを取得する
   ※画像生成は従量課金。料金は https://openai.com/api/pricing/ で確認する。
2. このスクリプトを実行する自分のPC（またはローカル環境）で、
   環境変数 OPENAI_API_KEY にそのキーを設定する。
   例（Mac/Linuxのターミナル）:
       export OPENAI_API_KEY="ここに自分のAPIキー"
   例（Windows PowerShell）:
       $env:OPENAI_API_KEY="ここに自分のAPIキー"
   ※ APIキーはこのファイルやチャットには直接書き込まないこと。
3. 依存パッケージをインストールする:
       pip install openai pillow --break-system-packages
4. 下の IMAGES リストに、作りたい画像のファイル名とプロンプトを追加する。
5. python generate_images_openai.py を実行する。
   生成された画像は OUTPUT_DIR に保存される（生成直後に自動で圧縮も行う）。

使い方の想定:
- 記事のプレースホルダー（例:【サムネ】【挿絵】）に対応する画像を、
  この設定リストに1件ずつ追加してから実行する。
- 生成後、OUTPUT_DIR内の画像をQiita/noteの記事に実際にアップロードし、
  発行されたURLで本文の画像リンクを差し替える
  （Qiitaは外部からの直リンク貼り付けができないため、
  Qiita上に一度アップロードする必要がある）。

このスクリプトについて:
- 画像生成にはOpenAIの gpt-image-2 モデルを使用する
  （2026年7月時点の最新画像生成モデル。旧称ChatGPTの画像生成と同じ仕組み）。
- 生成直後に自動でリサイズ・再圧縮を行うため、
  「ChatGPTで生成→手動でコピー→圧縮」という手作業が丸ごと不要になる。
- 圧縮処理だけを単体で使いたい場合（例: 手動でダウンロードした画像を圧縮したい時）は、
  compress_image() 関数を他のスクリプトからimportして使うこともできる。
"""

import base64
import os
import sys
from pathlib import Path

from openai import OpenAI
from PIL import Image

# ---- ここを編集する ----------------------------------------------------

OUTPUT_DIR = Path(__file__).parent / "generated_images"

# 圧縮後の画像の最大の辺（px）。これより大きい場合は縮小する。
MAX_DIMENSION = 1600

# 圧縮後の目標ファイルサイズ（KB）。JPEGの画質を自動調整してこれに近づける。
TARGET_KB = 300

# (出力ファイル名, プロンプト, サイズ, 画質) のリスト
# サイズは "1024x1024"（正方形・1:1）
#          "1536x1024"（横長・サムネ16:9向け）
#          "1024x1536"（縦長・挿絵2:3向け）
#          "auto"（プロンプトから自動判断）などから選ぶ
# 画質は "low"（下書き・速い）"medium"（通常）"high"（精細・コスト高）から選ぶ
IMAGES = [
    {
        "filename": "sample_thumbnail.png",
        "prompt": (
            "シンプルでかわいいフラットイラスト。……（記事ごとに差し替える）"
        ),
        "size": "1536x1024",
        "quality": "medium",
    },
    # 必要な分だけ追加する
    # {
    #     "filename": "sample_illust_1.png",
    #     "prompt": "...",
    #     "size": "1024x1536",
    #     "quality": "medium",
    # },
]

MODEL = "gpt-image-2"

# ------------------------------------------------------------------------


def compress_image(src_path, dst_path=None, max_dimension=MAX_DIMENSION, target_kb=TARGET_KB):
    """画像をリサイズ・再圧縮して保存する。

    - 長辺が max_dimension を超える場合は縮小する
    - 透過（アルファチャンネル）があるものはPNGのまま最適化のみ行う
      （サムネ等、文字が入っている画像はPNGの方が文字が潰れにくい）
    - 透過がないものはJPEGに変換し、target_kbに近づくよう画質を自動調整する
    """
    src_path = Path(src_path)
    dst_path = Path(dst_path) if dst_path else src_path
    img = Image.open(src_path)

    w, h = img.size
    scale = min(1.0, max_dimension / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)

    if has_alpha:
        out_path = dst_path.with_suffix(".png")
        img.save(out_path, format="PNG", optimize=True)
        return out_path

    rgb = img.convert("RGB")
    out_path = dst_path.with_suffix(".jpg")
    quality = 90
    while quality >= 40:
        rgb.save(out_path, format="JPEG", quality=quality, optimize=True)
        size_kb = out_path.stat().st_size / 1024
        if size_kb <= target_kb:
            break
        quality -= 10
    return out_path


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "エラー: 環境変数 OPENAI_API_KEY が設定されていません。\n"
            "自分のAPIキーを環境変数として設定してから実行してください。",
            file=sys.stderr,
        )
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for item in IMAGES:
        print(f"生成中: {item['filename']} ...")
        result = client.images.generate(
            model=MODEL,
            prompt=item["prompt"],
            size=item.get("size", "auto"),
            quality=item.get("quality", "medium"),
        )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        raw_path = OUTPUT_DIR / item["filename"]
        raw_path.write_bytes(image_bytes)
        before_kb = raw_path.stat().st_size / 1024

        compressed_path = compress_image(raw_path)
        after_kb = compressed_path.stat().st_size / 1024

        print(f"  -> 生成: {raw_path.name} ({before_kb:.0f}KB)")
        if compressed_path != raw_path:
            print(f"  -> 圧縮: {compressed_path.name} ({after_kb:.0f}KB)")
        else:
            print(f"  -> 圧縮後: {after_kb:.0f}KB")

    print("完了しました。")


if __name__ == "__main__":
    main()
