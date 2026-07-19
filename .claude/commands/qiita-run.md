# Qiita記事 全自動実行（アカウント別・限定公開）

指定されたQiitaアカウントのペルソナに沿って、参考URLをもとに記事を生成し、レビュー・リライト・採点を経て、そのアカウントの権限で**限定公開**として投稿します。構成案の確認（Step 0.5）以降は、ユーザーへの確認を挟まず最後まで自動実行してください。

---

## Step 0: 引数の解釈

`$ARGUMENTS` の先頭トークンをアカウント指定、残りをURLとして解釈する。

| アカウント指定（先頭トークン） | account | account_dir | token env var | campaign接頭辞 |
|---|---|---|---|---|
| `Account-A` / `すもも` / `sumomo` | Account-A | `Qiita/Account-A` | `QIITA_TOKEN_ACCOUNT_A` | `sumomo` |
| `Account-B` / `ぷらむん` / `prumn` | Account-B | `Qiita/Account-B` | `QIITA_TOKEN_ACCOUNT_B` | `prumn` |
| `Account-C` / `ひとみん` / `hitomin` | Account-C | `Qiita/Account-C` | `QIITA_TOKEN_ACCOUNT_C` | `hitomin` |

- 先頭トークンがどれにも一致しない場合、または`$ARGUMENTS`が空の場合（例：URLだけが渡された場合）は、**推測で進めず**以下の2段階でアカウントを確定する。
  1. 選択肢としてすもも（Account-A）／ぷらむん（Account-B）／ひとみん（Account-C）を提示し、どれを使うか選んでもらう。
  2. 選んでもらった結果を「〇〇（Account-X）でよろしいですか？」と復唱し、OKが出てから先へ進む（誤った選択のまま自動実行されるのを防ぐための再確認）。
  参考URLがまだ渡されていない場合は、この2段階の確認と合わせて参考URLも確認する。
- 残りの引数が `http://` または `https://` で始まっていなければ、参考URLの指定を促して終了する（今回はURLモードのみ対応。topics.yaml・CSVバッチ処理は未実装）。

以降、判定した account を `{account}`、account_dirを`{account_dir}`、token env varを`{token_var}`、campaign接頭辞を`{campaign_prefix}`と表記する。

---

## Step 0.5: 資料の確認と構成案の提示

以下をReadする（存在するファイルのみ。`Style.md`・`ReferenceHistory.md`はアカウントによっては存在しない）。

- `{account_dir}/Persona.md`
- `{account_dir}/Strategy.md`
- `{account_dir}/Style.md`（あれば）
- `{account_dir}/ReferenceHistory.md`（あれば。過去に扱ったテーマとの重複確認に使う）
- `Qiita/WritingProcess.md`（全アカウント共通の執筆原則）
- `{account_dir}/qiita-publish/templates/header.md` / `footer.md`

WebFetchで`$ARGUMENTS`の参考URLを取得する。参考にするのは悩み・テーマの着想のみで、文章・構成をそのまま転記しない（`WritingProcess.md`ルール16）。

`{account_dir}/ReferenceHistory.md`がある場合、過去に扱ったテーマ・参考記事と内容が重複しないか確認する。

slugを `YYYY-MM-DD_{タイトルのlowercase-hyphenated、最大50文字}` の形式で決定する。

**Account-C固有の注意**: `Style.md`が未整備のため構成・トーンが確定していない。Persona.mdの方針（落ち着いた先生・講師トーン）に沿って簡潔な構成を提案し、構成案提示の際にその旨を明記する。IPA非公開の過去問題は転載しない（Persona.mdのNG参照）。

以下の形式で構成案を提示し、OKが出るまで執筆には進まない（utm_campaign識別子・著者名はアカウントごとに固定済みのため、ここでは確認しない）。

```
## 記事構成案（{account}）

**タイトル案：** （タイトル）
**対象読者：** （例：未経験〜1年目のエンジニア）
**スラッグ：** （slug）
**参考URL：** $ARGUMENTS の該当URL

### 構成

1. ## （見出し）
   （内容の概要）
2. ...

---
この構成でよければ「OK」と返してください。変更したい場合はご指示ください。
```

修正指示があれば構成案を修正して再提示する。承認が得られたらStep 1へ進む。

---

## Step 1: 執筆

フロントマターは以下の形式で固定する（この用途は常に限定公開のため、`organization_url_name`は最初から`null`とする）。

```yaml
---
title: (タイトル)
tags:
  - (タグ1)
  - (タグ2)
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---
```

- 本文は`{account_dir}/Style.md`（あれば）の構成の型・記法（絵文字、`:::note warn`、太字/赤字強調など）に厳密に従う。`Style.md`がない場合（Account-C）は`Persona.md`のトーンのみに従い、無理に凝った記法を追加しない。
- `{account_dir}/qiita-publish/templates/header.md`・`footer.md`の内容を、そのアカウントのStyle.mdで定められた位置に挿入する（Account-A: タイトルより前に固定の自己紹介として。Account-B: 「## はじめに」冒頭の名乗り1文目として。Account-C: 冒頭の挨拶として）。本文中の`{{DATE}}`は投稿日（YYYYMMDD）に置換する。
- 誘導リンクの`utm_campaign`は`{campaign_prefix}_{{DATE}}`固定（`{{DATE}}`は投稿日）。内容に合うエンジニア記事サイトの個別記事があれば、そちらのパスに差し替えてよい（Style.md参照）。
- 画像は挿入しない（プレースホルダーも入れない）。見出し画像・挿絵が必要な場合は、投稿後に`{account_dir}/Tools/`配下の画像生成スクリプトを使う別工程であることを完了報告で伝える。
- 本文にH1（`#`）は使わない。タイトルはフロントマターの`title`のみで表現する。
- 実在の人物の発言・実体験として書く内容は、裏取りできていない場合は断定せず一般論として書くか、`WritingProcess.md`ルール5に従い確認が必要な旨をレビューで指摘する。

`{account_dir}/qiita-publish/public/{slug}/draft.md` に Write する。

---

## Step 2: レビュー

`{account_dir}/qiita-publish/public/{slug}/draft.md` を Read する。

### 静的チェック

| 確認項目 | 種別 |
|---------|------|
| フロントマターが `---` で始まっているか | 🔴 エラー |
| H1（`#`）が本文中に含まれていないか | 🔴 エラー |
| `organization_url_name` が `null` になっているか | 🔴 エラー |
| **太字** の前後にスペースがあるか | 🟡 警告 |
| `## まとめ`（またはStyle.mdで定義された締めの見出し）があるか | 🟡 警告 |

### 品質レビュー（該当アカウントの資料に基づく）

- `{account_dir}/Style.md`の記法・構成ルールに沿っているか
- `{account_dir}/Persona.md`のNGリストに抵触していないか
- `Qiita/WritingProcess.md`の該当項目（読者を責めていないか、時系列・関係性の矛盾、断定しすぎる表現、他アカウントの固有名詞、統計の一次ソース確認など）
- `{account_dir}/Style.md`「学んだこと」セクションに記録された過去の指摘と同じ問題を繰り返していないか

`{account_dir}/qiita-publish/public/{slug}/review.md` に以下の形式でWriteする。

```markdown
## 総評
（100〜200字）

## 静的チェック結果
### 🔴 エラー
（なければ「なし」）
### 🟡 警告
（なければ「なし」）

## 指摘事項
### 🔴 必須修正
（なければ「なし」）
### 🟡 推奨修正
（なければ「なし」）
### 🟢 良い点
（評価できる点）
```

---

## Step 3: リライト

`draft.md`と`review.md`をReadする。

- 🔴 必須修正 → 全件必ず反映する
- 🟡 推奨修正 → 内容を判断して反映する
- フロントマターの`id`・`updated_at`は変更しない
- 修正理由のコメントは書かず、完成版の本文のみ出力する

`{account_dir}/qiita-publish/public/{slug}/rewrite.md` にWriteする。

---

## Step 4: 採点

`rewrite.md`を Read して100点満点で採点する。

| 項目 | 満点 | 評価観点 |
|------|------|---------|
| 内容の正確性・裏取り | 20点 | 事実関係が確認済み、または誇張のない一般論になっているか |
| 読者への分かりやすさ | 20点 | 対象読者が理解できる構成・言葉遣いか |
| 誤字脱字・表記ゆれ | 10点 | 誤字・脱字がないか |
| リンク・フロントマターの正確性 | 20点 | utm_campaign・organization_url_name・タグなどが正しいか |
| アカウントスタイルとしての完成度 | 30点 | `Style.md`の構成・記法・「学んだこと」の指摘が守られているか |

### スタイル別減点（完成度30点から減点、該当アカウントの資料から動的に判断する）

- `{account_dir}/Persona.md`のNGリストに触れる表現がある: -10点/箇所
- `{account_dir}/Style.md`「学んだこと」に記録済みの過去の指摘と同じ問題を繰り返している: -8点/箇所
- 読者を責める表現がある（`WritingProcess.md`ルール8）: -5点/箇所
- 他アカウントの固有名詞を本文に出している（`WritingProcess.md`ルール10）: -10点

**合格基準：95点以上でPASS**

`{account_dir}/qiita-publish/public/{slug}/score.json` にWriteする。

```json
{
  "slug": "(slug)",
  "account": "{account}",
  "title": "(タイトル)",
  "total": (合計点・整数),
  "pass": (true または false),
  "feedback": "(採点コメント・200字以内)",
  "scored_at": "(YYYY-MM-DD)"
}
```

- `pass: true` → Step 5へ
- `pass: false` → `score.json`と`rewrite.md`を削除してStep 3に戻る（最大3回）
- 3回FAILしたら停止し、改善点を報告する

---

## Step 5: 投稿前チェックと限定公開投稿

`rewrite.md`の`private`を`true`に変換し、`{account_dir}/qiita-publish/public/{slug}.md`にWriteする（`organization_url_name`はStep 1の時点ですでに`null`）。

### 投稿前チェック

以下をすべて確認し、問題があれば投稿前に修正して再確認する。

- タイトルと本文（見出し・まとめ）の一貫性
- タイトルがAI臭くなく、対象読者が興味を持てる内容か
- 冒頭の名乗り・自己紹介に誤りがないか
- 会社情報・個人情報などセキュリティ上漏れてはいけない情報が含まれていないか
- 断定しすぎる表現がないか
- 誘導リンクの`utm_campaign`が`{campaign_prefix}_{{DATE}}`で、日付が投稿日になっているか

### トークンの扱い（厳守）

`.env`をReadツールで読んではならない。トークンの値をコマンド出力や会話に一切表示してはならない。以下のように、シェル内でのみ`.env`を読み込み、その回のコマンド実行にだけ使う。

Bashで実行する（`{account_dir}`・`{token_var}`は Step 0 で確定した値に置き換える）：

```bash
set -a && source .env && set +a && QIITA_TOKEN="${token_var}" npx qiita publish {slug} --root {account_dir}/qiita-publish --config {account_dir}/qiita-publish
```

- `{token_var}`が空（未設定）の場合、qiita-cliは`ENOENT: ... credentials.json`というエラーを返す（空文字列はJS的にfalsyのため、環境変数未設定時と同じ扱いになる）。このエラー、または明示的な認証エラーが出た場合は「`.env`の`{token_var}`が未設定、または無効です。Qiitaの当該アカウントにログインした状態でトークンを発行し、`.env`に記入してください（`.env.example`参照）」と案内して停止する。トークンの値そのものは決して聞き返さない。

---

## Step 6: 投稿後の後処理

- 投稿に使った本文（フロントマター無し、Qiita記法のみ）を `{account_dir}/Articles/{タイトル}.md` にもWriteする（既存のアーカイブ運用に合わせる）。
- `{account_dir}/ReferenceHistory.md`が存在する場合、使用したテーマ・参考URLを追記する。

---

## 完了報告

投稿した slug・Qiita記事ID・記事URL（`npx qiita publish`の出力から取得）を報告する。画像を使う場合は`{account_dir}/Tools/`の画像生成スクリプトで別途対応が必要な旨を添える。
