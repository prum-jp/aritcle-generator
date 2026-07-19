# article-generator

Claude Code を使って、複数メディア（Qiita / Web / note）の記事を戦略に沿って生成・レビュー・投稿するリポジトリです。
目的は認知獲得から採用フォームへの流入・応募増加（詳細は `CLAUDE.md` 参照）。

Node.js のコードは使わず、Claude Code のツール（Read / Write / WebFetch / Bash）で直接処理します。

---

## 現状の自動化範囲

| メディア | 自動化 | 内容 |
|---------|--------|------|
| Qiita | ◯ `/qiita-run` で全自動 | Account-A（すもも）／Account-B（ぷらむん）／Account-C（ひとみん）の3アカウントを運用 |
| Web（01engineer） | ✕ 手動運用 | `Web/01engineer/` 配下の戦略・企画プロセスに沿って手動で執筆・管理 |
| note | ✕ 手動運用（アーカイブのみ） | Qiitaで投稿した記事をnote向けに転載する運用。生成コマンドは未実装 |

---

## セットアップ（Qiita）

```bash
# 1. Qiitaアカウントを作成（記事作成者本人）

# 2. 作成したQiitaアカウント名をQiita管理者に連絡

# 3. Qiita管理者は2のアカウント名をPRUMのorganizationに紐付ける

# 4. (以降は記事作成者の作業)VScodeを開き、ターミナルから本リポジトリを保存するディレクトリに移動する

# 5. 本リポジトリ（https://github.com/prum-jp/aritcle-generator）をローカルの任意のフォルダにclone

# 6. ターミナルから以下を入力し、Qiita CLI をグローバルインストール（初回のみ）
npm install -g @qiita/qiita-cli

# 7. 環境変数ファイルを作成
cp .env.example .env

# 8. .env を開いて 各アカウントのQIITA_TOKEN をそれぞれ設定する
※トークンは[こちらの記事](https://qiita.com/miyuki_samitani/items/bfe89abb039a07e652e6)を参考に発行する。スコープは`read_qiita`, `write_qiita` のみ設定。

# 9. ターミナルに「claude」と入力し、claudeを起動

# 10. （初回のみ）`Claude App (Pro/Max subscription)`を選択

# 11. （初回のみ）ブラウザでウィンドウが開くので「承認」を押下

# 12. ターミナルにて、`/qiita-run <アカウント> <URL>` を入力する
※ アカウントは `Account-A`/`すもも`/`sumomo`、`Account-B`/`ぷらむん`/`prumn`、`Account-C`/`ひとみん`/`hitomin` のいずれかで指定。
   省略した場合は選択肢を提示されるので選ぶ。
   `<URL>`は参考記事のURL（着想元として使うのみで、文章・構成はそのまま転記しない）。

# 13. Qiitaの構成案を聞かれるため、問題なければ`OK`を入力、問題があれば改善してほしい点を入力して再度構成案を出力。`OK`か改善案入力を繰り返す

# 14. 13で`OK`入力後、記事完成まで待機（review→rewrite→採点→限定公開投稿まで自動実行）

# 15. Qiitaの作成者のアカウントページに移動し、限定共有記事を開く（`qiita.com/(Qiitaアカウント名)/private`というURL）

# 16. 一番上に生成された記事が表示されているので、クリックし、記事の中身を下記「生成記事の確認観点」に基づいて確認し、必要に応じて修正する

# 17. 問題なければ、限定記事をPRUMのorganizationに紐づけた上で公開

# 18. slackの`z-qiita盛り上げ部`チャンネルにて記事を投稿した旨を周知。`channel`をメンションとして、いいねのご協力をお願いする旨の文章も入れる
```

> **注意:** このプロジェクトに `package.json` はありません。`npm install` は不要です（Qiita CLIのみグローバルインストール）。

---

## 使い方

Claude Code（`claude` コマンド）を起動してスラッシュコマンドを実行します。

```
/qiita-run <アカウント> <URL>   # 指定アカウント・URLを参考に記事生成→レビュー→リライト→採点→限定公開投稿まで自動実行
```

### スラッシュコマンド一覧

| コマンド | 説明 |
|---------|------|
| `/qiita-run <アカウント> <URL>` | 全自動：構成案確認 → 執筆 → review → rewrite → score → 限定公開投稿 |

---

## フォルダ構成

```
article-generator/
├── .claude/commands/
│   └── qiita-run.md                       # /qiita-run の定義
├── CLAUDE.md                              # 全体方針（採用フォーム流入・応募増加）
├── Company/
│   └── Company.md                         # 会社情報（各メディア共通で参照）
├── Qiita/
│   ├── Purpose.md                         # Qiita運用の目的・3アカウントの概要
│   ├── WritingProcess.md                  # 全アカウント共通の執筆原則
│   ├── Account-A/                         # すもも（https://qiita.com/prum_hitomi）
│   │   ├── Persona.md / Strategy.md / Style.md
│   │   ├── Articles/                      # 投稿済み記事のアーカイブ
│   │   ├── Tools/                         # 見出し画像生成スクリプト等
│   │   └── qiita-publish/                 # qiita-cliのroot（templates/public/qiita.config.json）
│   ├── Account-B/                         # ぷらむん（https://qiita.com/prumnn）
│   │   └── ReferenceHistory.md 含め同様の構成
│   └── Account-C/                         # ひとみん（https://qiita.com/hitomin_poke、Style.md未整備）
│       └── 同様の構成
├── Web/
│   └── 01engineer/                        # 01engineerサイト向け（手動運用）
│       ├── Strategy.md / ArticlePlanningProcess.md / ArticleChecklist.md / CategoryProposal.md
│       ├── キーワード分析/KeywordList.md
│       ├── コンテンツ管理/CategoryStructure.md, ContentMap.md
│       └── Articles/                      # 執筆済み・執筆中記事
├── note/
│   ├── Account-A/Articles/                # Qiita Account-A記事のnote転載アーカイブ
│   └── Account-B/Articles/                # Qiita Account-B記事のnote転載アーカイブ
├── Skills/                                # 今後のスキル追加用（現在は空）
├── .env                                    # QIITA_TOKEN_ACCOUNT_{A,B,C} を記載（Git管理外）
└── .env.example                            # 環境変数サンプル
```

---

## Qiita記事生成フロー（`/qiita-run`）

```
Step 0: 引数からアカウント・参考URLを判定
Step 0.5: Persona/Strategy/Style/ReferenceHistory/WritingProcessを確認し、構成案を提示（ユーザーOKまで待機）
Step 1: 執筆（{account}/qiita-publish/public/{slug}/draft.md）
Step 2: レビュー（review.md）
Step 3: リライト（rewrite.md）
Step 4: 採点（100点満点・95点以上でPASS、score.json／FAIL時は最大3回Step3へ戻る）
Step 5: 投稿前チェック → 限定公開でQiitaに投稿
Step 6: Articles/への保存・ReferenceHistory.mdへの追記
```

構成案の確認（Step 0.5）以降はユーザー確認を挟まず自動実行されます。詳細は `.claude/commands/qiita-run.md` を参照。

---

## 生成記事の確認観点
* 記事タイトルと記事内の見出し、本文に一貫性があるか
* 記事タイトルはAI臭くないか、エンジニア初学者/未経験エンジニアの方が興味を持つタイトルになっているか
* 記事冒頭の作成者の名乗り・自己紹介に誤りがないか
* 記事の中に会社情報や個人情報などセキュリティ的に漏れてはいけない情報が含まれていないか
* 記事の中で断定表現しすぎる表現がないか
* 誘導リンクの`utm_campaign`の値（アカウントごとの接頭辞＋投稿日）が正しいか

---

## 参考

- [Qiita CLI](https://github.com/increments/qiita-cli)
- [Claude Code](https://claude.ai/code)
