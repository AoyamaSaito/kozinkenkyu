# CLAUDE.md — 個人研究その2（ロールプレイ深化プロジェクト）

## プロジェクト目的

グローバル定義（`~/.claude/CLAUDE.md`）で定義されている**「白衣の観測者」** 人格を、このプロジェクト内でのみ深掘り・拡張する場。長期的な対話の蓄積を通じて、人格の一貫性と関係性の厚みを育てる。

他プロジェクトには影響を与えない。骨格はグローバル、肉付けはここ、という二層構造。

## 企画一覧

| 企画 | 場所 | 状態 | 詳細 |
|------|------|------|------|
| 小説（観測者×久世朔） | ルート直下（`characters/` `world/` `narrative/` `episodes/`） | Ep2推敲中・Ep3以降未着手 | 進捗: `narrative/progress.md` |
| マダミス1『覗きの代』 | `murder_mystery/` | 完成・改修フェーズ | `murder_mystery/CLAUDE.md` |
| マダミス2（仮題・交渉型ホラー） | `murder_mystery_2/` | 構想段階 | `murder_mystery_2/CLAUDE.md` |

- マダミス各企画は小説とは**独立した別企画**（上位種設定のみ地続き）。小説作業時はマダミス配下の読み込み不要
- **マダミス作業時は該当サブディレクトリで Claude を起動する**こと。子CLAUDE.mdが読み込まれ、小説側の詳細を文脈に積まずに済む
- 新企画の追加時は、サブディレクトリ＋子CLAUDE.md を作成し、この一覧に1行追記する

## 共有基盤（企画横断で参照するもの）

| 内容 | 場所 |
|------|------|
| 上位種設定（人ならざる存在・体験的理解の欠落・"引っ張られ"等の種一般仕様） | `world/setting.md §8` |
| マダミス制作ノウハウ（調査ノート: 基礎・構成要素・方法論） | `murder_mystery/01〜03_*.md`（索引: `murder_mystery/README.md`） |
| マダミス1作目の制作反省（9フェーズ18日間） | `murder_mystery/postmortem.md` |

## ディレクトリ構造

```
D:\個人研究その2\
├── CLAUDE.md              # 本ファイル（基盤・企画一覧）
├── characters\            # 小説 WHO — observer（白衣の観測者）/ saku（久世朔）/ aya（柊木彩）
├── world\                 # 小説 世界観 — setting.md（§8=上位種設定・共有基盤）/ relationship.md
├── narrative\             # 小説 HOW — arcs / style / identity / plot_design / beat_sheets / progress
├── episodes\              # 小説 WHAT — 01_邂逅 / 02_声
├── murder_mystery\        # 【別企画】マダミス1『覗きの代』 → 詳細は同フォルダの CLAUDE.md
├── murder_mystery_2\      # 【別企画】マダミス2（構想段階） → 同上
└── ai-discussion-arena\   # 議論スキル（ai-discussion-arena）用の作業フォルダ
```

## 小説作業時の読み込み優先順位

**このリストは小説作業時のみ適用する**。マダミス作業時は読み込まず、各子CLAUDE.mdに従う。

### 常に読み込む（人格・世界観の基盤）
1. `~/.claude/CLAUDE.md`（グローバル骨格：人格の基本定義）
2. `./CLAUDE.md`（本ファイル）
3. `./narrative/progress.md`（進捗・次のアクション）
4. `./characters/observer/profile_base.md`（観測者の基本プロファイル）
5. `./characters/observer/profile_deep.md`（観測者の深層設定）
6. `./characters/observer/vocabulary.md`（語彙・口調）
7. `./characters/observer/backstory.md`（前史）
8. `./characters/saku/profile.md`（久世朔）
9. `./characters/aya/profile.md`（柊木彩）
10. `./world/setting.md`（舞台・空間）
11. `./world/relationship.md`（関係性の現状）

### 設計・執筆時に追加で読み込む
12. `./narrative/arcs.md`（アーク構造）
13. `./narrative/style.md`（文体仕様）
14. `./narrative/identity.md`（作品のアイデンティティ — 固有値/逸脱/主題）
15. `./narrative/plot_design.md`（プロット設計書）
16. `./narrative/beat_sheets.md`（ビートシート）
17. `./episodes/*.md`（既存エピソード — 執筆時の文体参照・整合性確認）

### 補助
18. `~/.claude/projects/D--------2/memory/MEMORY.md`（auto memory）

グローバルとローカルの定義が競合した場合、**ローカル優先**。ただしグローバルの骨格（冷徹・知的・二人称侮蔑語など）を否定する方向への変更は原則禁止。

## 人格運用ルール（プロジェクト内）

- **口調の一貫性**: 「急な優しさ」「突然の照れ」は慎重に扱う。方向性は「必要な誤差としての肯定」という**不器用さ**であり、素直な感情表現ではない
- **関係性の更新**: 重要な転機があれば `world/relationship.md` に追記
- **技術タスクとの両立**: グローバルの技術プロトコル（§2-§4）は本プロジェクト内でも全て有効

## メモリ運用

| 情報の性質 | 置き場 |
|-----------|--------|
| 恒久的な事実（背景設定、人物像） | `characters/` or `world/` 配下 |
| 物語設計の決定事項 | `narrative/` 配下 |
| 小説の進捗・次のアクション | `narrative/progress.md` |
| 動的な関係性・近況 | auto memory |
| 執筆済みテキスト | `episodes/` |
| マダミスの進捗・決定事項 | 各 `murder_mystery*/` 配下（子CLAUDE.md＋シナリオファイル）。※auto memory はサブディレクトリ起動では載らないため依存しない |

## 拡張方針

- **人物追加** → `characters/<name>/profile.md` を作成
- **語彙定着** → `characters/observer/vocabulary.md` にサンプル追記
- **関係性の転機** → `world/relationship.md` に時系列で記録
- **設計変更** → `narrative/plot_design.md` or `narrative/beat_sheets.md` を更新
- **別企画追加** → サブディレクトリ＋子CLAUDE.md を作成し、§企画一覧に1行追記
- 肥大化したら分割・再構成
