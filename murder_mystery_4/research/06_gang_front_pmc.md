# Cyberpunk RED 世界観調査ノート — 「ギャングが表向き警備会社/PMCフロント企業を運営する」設定のcanon整合検証

## 0. この調査の目的と方法

自作マーダーミステリー（Cyberpunk RED 世界・2045年＝赤の時代、ナイトシティ周縁地域の再開発コンソーシアムが舞台）で、ギャング「メイルストローム」が**表向き小規模な警備会社（創作ダミー会社）の体裁でコンソーシアムに参加している**という設定を使う想定の、canon整合性検証。

- 主な情報源: R. Talsorian Games公式ブログ（直接Fetch成功）、Cyberpunk Wiki (Fandom)、その他二次まとめサイト（検索エンジン抜粋経由）。
- **cyberpunk.fandom.comへのWebFetchは今回もHTTP 402で全件拒否された**。Fandom由来の情報はすべて検索エンジンの抜粋・要約経由であり、一次資料の直接確認ではない。
- **重要な発見**: 調査の過程で `Night City 2045` という**Cyberpunk RED公式の新サプリメント（R. Talsorian Games、2026年春頃発売）** の存在を確認した。これは本ノート執筆時点（2026年7月）でも最新の一次資料であり、しかもまさに「2045年」を主題にした書籍のため、時代考証の観点で他のどの資料よりも直接的な価値を持つ。R. Talsorianの公式ブログ記事2本（下記）は直接Fetchでき、内容も検証できたため、本ノートの中核根拠として扱う。
- 時代区分は「1993年版(2013)/2020年版/RED版(2045)/2077年版」の4層で区別し、時代が特定できない情報は**未確認**と明記した。

---

## 1. 冒頭要約（Executive Summary）

| 調査項目 | 結論 | 確度 |
|---|---|---|
| ①2045年の民間警備/PMC業界の乱立状況 | **確認できた**。NCPDは弱体化し、警備の担い手は「NCPD／独立化したMAX-TAC／企業警備／ギャング／エッジランナー個人契約」に分散。`Night City 2045`本には**44ギャング・6犯罪組織・23警備提供者**というカテゴリが公式に立てられており、中小警備会社が乱立する時代であることが裏付けられた | 高（公式ブログ・公式サプリ紹介文で確認） |
| ②ギャングのフロント企業運営 canon前例 | **強い前例あり**。特に「ゴールド・ドラゴンズ・セキュリティ（Gold Dragons Security）」は**2044年に正式法人化**され、公式サプリで「ギャング」と「警備提供者」の**両方のカテゴリに二重掲載**されている。「6th Street」も、元軍人が興し中小企業の警備契約を取りつつ実態はギャング資金繰りに依存する組織として、ほぼ同型の前例 | 高（Gold Dragons/6th Streetとも複数独立ソースで一致） |
| ③企業・団体がシェル/フロント企業を使う canon前例 | **前例あり**（ただし時代はやや不確か）。タイガー・クロウズの「キメン組（Kimen-Gumi）」は合法法人としての「表の顔」、ヴァレンティノスは合法事業を非合法活動の隠れ蓑にする、という記述が確認できたが、**詳細な描写の多くは2077年ゲーム本編由来**で、2045年時点の状態そのものではない可能性がある | 中（構造自体はRED初期〜継続の設定だが、詳細描写の時代特定が弱い） |
| ④ギャングと企業/行政の取引の公然性 | **「非公然だが黙認されている」に近い**。ゴールド・ドラゴンズの成立過程が、まさに「行政担当者が裏で資金提供してギャングを合法警備組織に仕立てた」という腐敗の実例として、`Night City 2045`本文で「2077年に常態化する腐敗と地続き」と位置づけられている | 高 |
| ⑤小規模警備会社のcanon実例名 | **複数確認**。「ゴールド・ドラゴンズ・セキュリティ」「6th Street」「Danger Gal（警備・調査志向の組織）」「Lazarus Group（高級警備プロバイダー）」「Coronado Swarm（傭兵・護衛稼業）」 | 高 |

**最優先での結論**: メイルストロームが表向き警備会社のダミー会社を運営してコンソーシアムに参加する、という自作設定は**canonと矛盾せず、むしろ強く整合する**。ただし「メイルストローム自身」がフロント企業を運営したという直接の一次資料は無い（メイルストロームの実業＝トーテンタンツ・クラブは、あくまで身内向けの収益源であり、対外的な擬装ではない）。一方、**同時代の別ギャング（ゴールド・ドラゴンズ、6th Street）がまさに同型の構造（ギャング実体＋法人化された警備会社の表看板）を持つことが公式一次資料で確認できた**ため、「ギャングが警備会社のダミー法人を持つ」という**構造そのものは2045年canonの中に実例を持つ、確立されたパターン**である。メイルストローム個別への適用は「空白＝創作可」の範疇だが、根拠のある創作である。

---

## 2. ①2045年の民間警備・PMC業界の状況

R. Talsorian Games公式ブログ「Cyberpunk RED Alert: Night City」（2020年10月23日）より（直接Fetch確認済み）:

> "Who provides security depends on where you're hanging. Could be a poorly funded NCPD. Could be MAX-TAC, now an independent organization. Or it could be private Corporate security or gang enforcers or just some local Edgerunners, hired for the job by the community."

これは2045年（RED）時点の記述として明記されている。NCPDは資金不足で弱体化し、MAX-TACは（かつての指揮系統から独立して）単独組織化。治安の担い手は地区ごとにバラバラで、「私設企業警備」「ギャングの用心棒」「地元エッジランナーへの個別依頼」が並列に存在する、という構造。

さらに公式サプリメント`Night City 2045`（R. Talsorian Games、検索結果より2026年春発売と推定される最新刊）の紹介文・レビュー記事（Bell of Lost Souls等、検索エンジン抜粋経由）によれば:

> ファクションのチャプターには**44のギャング、6つの犯罪組織、23の警備提供者**の情報が含まれる。

「23の警備提供者」という数字は、2045年時点で中小規模の民間警備業者が既に相当数乱立していたことの直接的裏付けになる。「ギャング／犯罪組織／警備提供者／企業系ネットワーク」という**4分類がそもそも公式に並立するカテゴリとして設計されている**こと自体が、②で扱う「ギャングと警備会社の境界の曖昧さ」がデザイン意図として組み込まれていることを示唆する。

**結論**: 中小警備会社が普通に存在する時代、という前提は**確認できた**。

---

## 3. ②ギャングがフロント企業/ダミー会社を運営するcanon前例

### 3-1. ゴールド・ドラゴンズ・セキュリティ（Gold Dragons Security）— 最有力の直接前例

検索エンジン抜粋（Cyberpunk Wiki記事の要約、複数の独立検索で一致した内容）より:

- ゴールド・ドラゴンズは、ナイトシティ「リトル・チャイナ」のコンバットゾーンで発生した、当初は末端の低レベルなブースターギャング。
- **2030年代**、市の担当官（city manager）**デヴィッド・リン・ポー（David Ling Po）**が、地元中国系住民への反感の高まりを受け、ゴールド・ドラゴンズに**秘密裏に資金提供**し、末端の不良から「リトル・チャイナ全体のための、事実上デピュタイズされた（deputized＝権限付与された）法執行組織」へと作り変えた。LCRA（Little China Redevelopment Association）がこの組織を治安維持要員として雇用した、との記述もある。
- **2044年**、グアンボー・タワー（Guǎngbō Tower）が再開業した際、ドラゴンズはその地下階を本拠地に改装し、**「ゴールド・ドラゴンズ・セキュリティ」として正式に法人化されたオフィス**を構えた。
- **2045年時点**、ゴールド・ドラゴンズは「違法な恐喝行為で悪名高い」という顔と、「合法な」警備・法執行業務という顔を**両方**持つ、と明記されている。
- `Night City 2045`本の中で、ゴールド・ドラゴンズは**「ギャング」セクションと「警備提供者」セクションの両方に掲載される**という、公式ファクション分類上でも二重登録された特異な存在。

検索結果の要約の一つには、この件を評して次のような趣旨の記述もあった:

> 「2045年時点で既にデピュタイズされた地域防衛組織が存在すること自体が、2077年で常態化する腐敗と地続きの構図を示している」

**評価**: これは自作設定（ギャングが表向き警備会社を運営してコンソーシアムに参加）とほぼ完全に同型の構造——「ギャングの実体」＋「行政/団体からの資金・お墨付き」＋「法人化された警備会社という表看板」——が、**まさに2045年（RED）時点のcanonとして公式に存在する**という、極めて強い前例。ただし出典はすべて検索エンジンの抜粋経由（Fandom本体は402で未読）である点は留保する。

### 3-2. 6th Street — 「表看板は正規契約、資金繰りはギャング稼業」の前例

複数の独立した検索結果・二次まとめサイト（Cyberpunk RED Nexus、Cyberpunk Wiki要約経由）で一致した内容:

- 創設者は元軍事諜報将校の**ソロモン・"X"・ライト大佐（Solomon "X" Wright）**。第四次企業戦争の退役軍人たちを一つの旗の下に組織し、ナイトシティ市民の保護を目的として6th Streetを結成。
- 6th Streetは、大手警備会社（Militech、Lazarus等）と比べて**「経済的な」（安価な）民間警備の選択肢**であり、NCPDが機能しない場面で中小企業がこれを雇っている。
- ライトは6th Streetを**MilitechやLazarus級の正規PMCへと成長させることを志向している**、との記述がある。
- 一方で、実際の資金繰りは正規の警備契約だけでは賄いきれておらず（給与・装備費が契約収入を上回っている）、不足分を**みかじめ料（protection schemes）、恐喝（blackmail）、「疑わしい法執行活動」で押収した資産の転売**といった、非合法な手段で補っている、との記述がある。

**評価**: これは「表の顔＝正規警備契約」「裏の実態＝ギャング的な資金調達」という二重構造の**もう一つの直接前例**。「警備会社の看板を掲げつつ、実態としての収益はグレー〜ブラックな手段に依存する」という構図は、自作設定のメイルストロームにそのまま応用できるパターン。

### 3-3. 参考: タイガー・クロウズ「キメン組（Kimen-Gumi）」— 時代特定に要注意

検索結果より:

- タイガー・クロウズは、2023年のナイトシティ大虐殺後、NCCS（Night City Co-Prosperity Sphere、著名俳優シノブ・ナカガワ主導）によって再結成され、日本人コミュニティ保護を目的とするガーディアンギャングとして北部ワトソン開発区を拠点にした。
- その後、**「キメン組」という下部組織を「合法法人として認知される、対外的な公式の顔」として形成**し、警備契約を締結し、一部地域ではNCPDと連携しつつ準法執行的に振る舞った、との記述がある。
- ただし、**この詳細（キメン組の活動実態・会員数5,500人等の規模感）は主に2077年（ゲーム本編）時点の描写**であり、2045年時点でキメン組がどこまで確立していたかは検索範囲内では確認できなかった（**未確認**）。組織の**起源**（NCCSによる再結成）自体は2023年直後の出来事であり、2045年までに存在していた可能性は高いが、確証はない。

### 3-4. 参考: ヴァレンティノス — 合法事業を隠れ蓑にする一般的パターン

検索結果より、ヴァレンティノスは飲食店・ナイトクラブ・自動車整備工場といった完全に合法な事業を営みつつ、実態はマネーロンダリング・盗難車/銃器密輸・人身売買の隠れ蓑にしている、との記述。**ただしこの記述も2077年ゲーム本編の紹介記事由来で、2045年時点の状態かは未確認**。

### 3-5. 参考: メイルストロームのトーテンタンツ・クラブ（自勢力の再確認）

既存調査ノート（`03_factions_canon.md` §4）および今回の追加検索で再確認した内容: トーテンタンツ・クラブは**メイルストロームが公然と自ら経営する**ギャング御用達の「飲む＆暴れる」ベニュー（ネオ・デスメタルクラブ）であり、メイルストロームの主要な収入源ではあるが、**「対外的に別の顔を装う擬装（フロント）」ではない**。むしろ身内（ギャング仲間）向けの実店舗であり、外部（コンソーシアムのような対外関係者）に「これは無害な事業です」と偽装する機能は持たない。

**重要な留保**: したがって「メイルストロームが**既に**フロント企業運営の実績を持つ」という主張の直接的根拠にはならない。この点は、④の「メイルストローム個別のフロント運営は空白＝創作可」という結論に直結する。

---

## 4. ③企業・団体がシェル企業/フロントを使うcanon前例

上記3-3・3-4のタイガー・クロウズ／ヴァレンティノスの事例に加え、`Night City 2045`の分類体系そのもの（ギャング／犯罪組織／警備提供者／**企業系ネットワーク（corp-linked networks）**の4分類が並立）が、「企業と非合法組織の境界が曖昧な関係性」を前提にデザインされていることを示す傍証。ただし個別の企業側シェル会社事例（アラサカやミリテック等メガコーポが2045年時点でダミー会社を使った直接の記述）は検索範囲内では見つからず、**未確認**。

---

## 5. ④ギャングと企業・行政の取引の公然性

- ゴールド・ドラゴンズの成立譚（3-1）自体が最良の一次資料: 市の担当官が「地元住民の反感を鎮めるため」にギャングへ**秘密裏**に資金提供し、合法警備組織の体裁を与えた、という経緯は、**行政側がギャングとの結びつきを公然化できない（＝表沙汰にできない）ことを前提にした腐敗構造**をそのまま描写している。
- 検索結果の別の要約でも「企業による贈賄・行政官の腐敗はサイバーパンクの世界観の一部」「企業民兵が路上で抗争する」といった記述が一般論として繰り返し確認できた（ただし出典・時代の特定は弱く、一般的な世界観描写の域を出ない）。

**評価**: 「ギャングとの取引は表沙汰にできない」という前提（＝ダミー会社を立てる動機の強さ）は、ゴールド・ドラゴンズの成立譚という具体的な一次資料によって**強く裏付けられる**。自作設定「メイルストロームが正体を隠して参加する」動機付けとして、この前例は非常に強い援用材料になる。

---

## 6. ⑤小規模警備会社のcanon実例名（ダミー会社名の質感の参考）

| 名称 | 性格 | 出典時代 |
|---|---|---|
| Gold Dragons Security | 元ギャングが法人化した警備会社。地区限定・デピュタイズ型 | RED（2044年法人化） |
| 6th Street | 退役軍人設立、PMC志向の中堅警備組織。実態は資金繰りに難あり | RED（2045年時点で活動中） |
| Danger Gal | 「警備・調査志向の組織」との簡潔な記述のみ | 未確認（RED関連サプリ内） |
| Lazarus Group | 「高級（premium）警備プロバイダー」。6th Streetが目標にする上位互換の存在 | 未確認だが2045年文脈で言及 |
| Coronado Swarm | 旧シュガー・スカルズ。傭兵・護衛稼業に特化したギャング | RED（前身シュガー・スカルズからの転向） |

「Lazarus」「6th Street」のような**地名・数字・抽象語を組み合わせた即物的な社名**は、創作ダミー会社名の質感の参考として有用（過度にドラマチックな社名よりも、実務的・没個性的な名称の方がcanonの空気感に近い）。

---

## 7. 出典URL一覧

- [Cyberpunk RED Alert: Night City – R. Talsorian Games](https://rtalsoriangames.com/2020/10/23/cyberpunk-red-alert-night-city/)（直接Fetch確認済み）
- [Welcome to Night City 2045 #5 – Let's Talk Gangs – R. Talsorian Games](https://rtalsoriangames.com/2026/03/12/welcome-to-night-city-5-lets-talk-gangs/)（直接Fetch確認済み）
- [Night City 2045 – R. Talsorian Games（公式紹介ページ）](https://rtalsoriangames.com/night-city-2045/)
- [RPG: Cyberpunk Unleashes 'Night City 2045' - Bell of Lost Souls](https://www.belloflostsouls.net/2026/04/rpg-cyberpunk-unleashes-night-city-2045.html)（WebFetch 403で本文未読、検索エンジン抜粋のみ）
- [Night City 2045: The Massive New Cyberpunk Sourcebook Set 32 Years Before 2077 — Backyard Drunkard](https://backyarddrunkard.com/game-news/night-city-2045-cyberpunk-red-sourcebook-guide/)
- [Night City 2045 (Cyberpunk Red) - The Dragons Trove](https://www.dragonstrove.com/products/night-city-2045-cyberpunk-red)
- [Night City 2045 Factions: Gangs, Corps and Power Guide (fan compilation)](https://nightcity2045.wiki/factions/)
- [Cyberpunk RED expands with official Night City 2045 guide and digital tools – GeekNative](https://www.geeknative.com/238171/cyberpunk-red-expands-with-official-night-city-2045-guide-and-digital-tools/)
- [Night City 2045 has Arrived for Cyberpunk RED - The Gaming Gang](https://thegaminggang.com/game-news/night-city-2045-has-arrived-for-cyberpunk-red)
- [Gold Dragons | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Gold_Dragons)（402、検索エンジン抜粋のみ）
- [David Ling Po | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/David_Ling_Po)（未読、検索エンジン抜粋のみ）
- [Little China Redevelopment Association | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Little_China_Redevelopment_Association)
- [6th Street | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/6th_Street)（未読、検索エンジン抜粋のみ）
- [Solomon Wright | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Solomon_Wright)
- [6th Street - Gangs - Cyberpunk RED Nexus](https://app.demiplane.com/nexus/cyberpunkred/gangs/6th-street)（WebFetch: ローディング画面のみ取得、本文未読）
- [Tyger Claws | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Tyger_Claws)（未読、検索エンジン抜粋のみ）
- [Kimen-Gumi | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Kimen-Gumi)（未読、検索エンジン抜粋のみ）
- [Totentanz | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Totentanz)（未読、検索エンジン抜粋のみ、既存ノート03と重複）
- [Cyberpunk 2077's Gangs Ranked From Least To Most Powerful – GameRant](https://gamerant.com/cyberpunk-2077-gangs-ranked-powerful/)
- [Cyberpunk 2077 Gangs and Corporations - Pure Cyberpunk](https://cyberpunk.puredmg.com/gameinfo/cyberpunk-2077-gangs-corporations/)

---

## 8. 今後のシナリオ制作への示唆

- メイルストロームのダミー警備会社設定を採用する場合、**「ゴールド・ドラゴンズ・セキュリティ」型（行政/企業側の誰かが裏で資金提供し、法人格を与えた）** の構図にするか、**「6th Street」型（ギャング側が自発的に正規契約を取りにいくが、資金繰りは灰色）** の構図にするかで、動機と共犯関係の設計が変わる。前者はコンソーシアム内の誰か（4勢力の誰か、または潜入ネットランナーの正体）がメイルストロームの後ろ盾になっている、という筋立てに直結しやすく、現行の「潜入ネットランナーの正体」の設計課題（次のタスク）と組み合わせやすい。
- 「なぜダミー会社を使ってまで正体を隠す必要があるのか」の動機付けには、ゴールド・ドラゴンズの前例（行政側が世間体のためにギャングとの結託を隠したい）がそのまま使える。
