# Cyberpunk RED 世界観調査ノート — DataKrash・ナイトシティ大虐殺・戦後アラサカ処遇の時系列検証

## 0. この調査の目的と方法

自作マーダーミステリー（Cyberpunk RED 世界・2045年＝赤の時代、ナイトシティ周縁地域が舞台）の導入設定として使いたい因果チェーン——

> 「2022年頃 DataKrash で旧NETが論理的に死ぬ（データセンターのデータが外部同期される前に孤立・凍結）→ 2023年 アラサカタワー核爆発（ナイトシティ大虐殺）と第四次企業戦争の戦災で、周縁地域の旧NETデータセンターが物理的に埋没 → アラサカは北米追放され、大手不在の力の空白の中で2045年に周縁地域の再開発が始まり、工事中にデータセンターが出土する」

の各リンクが canon と整合するかを検証するための一次資料集め。

- 主な情報源: Cyberpunk Wiki (Fandom)、Grokipedia、World Anvil（ファンによるRED設定解説）、Cyberpunk Red 2047 Wiki（ファンWiki）、pupilswim.com（ファンブログ）等。
- **`03_factions_canon.md` `04_netwatch_canon.md` と同じ既知の問題として、WebFetchツールが cyberpunk.fandom.com への直接アクセスをHTTP 402/403で拒否した**。加えて今回は Grokipedia（403）、breezewiki（認証画面のみ）、pupilswim.com（404）へのWebFetchもすべて失敗し、**本ノートは完全にWeb検索エンジンが返す抜粋・要約経由の情報である**。一次資料（コアルールブック・サプリメントPDF本文）を直接確認したわけではない点に強く注意されたい。
- R. Talsorian Games公式ブログ（rtalsoriangames.com）への直接WebFetchは今回のトピックでは検索結果に出てこず試行機会がなかった（`Cyberpunk RED Alert: Night City` 記事のURLのみ確認、内容未取得）。
- 時代区分は「1993年版(2013)/2020年版/RED版(2045)/2077年版」の4層で区別。今回のトピック（DataKrash・大虐殺・戦後処理）は**全版に共通する背景史的事件**であり、他の調査ノートほど版間の混同リスクは高くないが、「戦後の再建」パートは2040年代前半（RED直前〜RED期）と2077年に至るまでの長期プロセスが連続しているため、**どの時点の描写かは都度年を明記する**。

---

## 1. 冒頭要約（Executive Summary）

| 調査項目 | 結論 | 確度 |
|---|---|---|
| DataKrashの年月日 | **2022年6月3日**。Rache Bartmossが仕込んだR.A.B.I.D.Sウイルス群がNETの78.2%に感染、多数のAIを暴走（ローグAI）させ「Old Net」が崩壊 | 高（複数ソース一致） |
| 「論理的に死ぬ／データが取り残された」の妥当性 | **概ね支持できる**。R.A.B.I.D.Sは物理破壊ではなく感染型ウイルスで、崩壊後もNETは「断片化した孤島の群れ（an archipelago of algorithms and code separated by treacherous abysses of nothingness）」として残った。**エアギャップ（外部非接続）だったネットワークだけが無事だった**という記述もあり、「外部同期前に孤立」という表現は創作上の脚色ではあるが、実態（感染から隔離された断片が生き残った）と方向性は矛盾しない | 中〜高 |
| ナイトシティ大虐殺の日付・規模 | **2023年8月20日**。アラサカタワー南棟120階でMilitech強襲部隊（モーガン・ブラックハンド、ジョニー・シルバーハンド含む）が仕掛けた戦術核が予定より早く起爆。両タワー崩壊、コーポレート地区・シティ地区壊滅、即死1.2万人、負傷後死亡者50万人規模、その後数ヶ月で追加25万人死亡 | 高（複数ソース一致） |
| 周縁地域への物理的被害 | **直接の爆風被害は中心部（コーポレート/シティ地区）に集中**。周縁部（南ナイトシティ、ランチョ・コロナド等）への影響は**液状化・浸水（地盤の埋立地由来）**と、**約200万人規模の被災者流入によるテント集落化・過密化**が中心で、「戦闘そのものによる破壊」の直接記述は確認できなかった | 中〜高 |
| 第四次企業戦争の市街戦 | ナイトシティは大虐殺直前まで**アラサカが実効支配する北米最後の拠点**であり、周辺高地にNUSA・カリフォルニア州兵・Militechの部隊が集結していたが、**大規模な市街地上戦闘（歩兵戦・砲撃戦）がナイトシティ市内で行われたという直接記述は確認できなかった**。核爆発そのものが「戦災」の主因 | 中（未確認部分あり） |
| アラサカの戦後処遇 | **NUSA政府（Militech国有化）により北米大陸から追放**、日本本土への事実上の隔離が2045年時点（RED期）でも継続中。**追放解除はUnification War（2069-2070年）後**——2045年よりはるかに後 | 高 |
| 2045年時点の「大手不在の力の空白」の妥当性 | **要注意・部分的にのみ支持できる**。ナイトシティは市長職が長年空席で、企業・ノマド・エッジランナー・旧市政府の混成「シティ・カウンシル」による寡頭統治という**権力分散状態**にはあるが、**ゼタテック・バイオテクニカ・ペトロケムに加え「密かにアラサカも」カウンシルに議席を持つ**との記述があり、単純な「大手不在」ではない。周縁部（コンバットゾーン等）は**ギャング・フィクサー・企業が個別に実効支配する縄張り制**で、統一的な空白地帯というより「無数の小さな支配者が乱立する無秩序」に近い | 中〜高 |
| 旧NET物理インフラの2045年時点の扱い | **canon空白**。「旧NET遺構の物理サルベージ」「データセンター発掘」に直接言及する一次資料は検索範囲内で見つからなかった。ただし大虐殺後の瓦礫撤去（戦車・重機で瓦礫を湾へ投棄）や、周縁部の「ゴーストタウンの再開発」というモチーフは確認でき、**「工事中に旧時代の遺構が出土する」という筋書き自体は矛盾しない創作の余地**がある | 中（間接支持） |

**総括**: 因果チェーンは**大枠として成立するが、2つの箇所で表現の調整が必要**——(a) 周縁部の被害は「戦闘・爆風による直接破壊」ではなく「地盤災害＋難民流入による無秩序化」として描く方が正確、(b) 「大手不在の力の空白」は「単独の大手が支配権を握れない、無数の小勢力が乱立する権力の隙間」として描く方が正確（アラサカが完全不在ではなく隠然と関与している点は伏線・裏設定として使う余地あり）。詳細判定は §7 参照。

---

## 2. DataKrash（2022年）の詳細

### 正確な年月日と経緯
**2022年6月3日**、旧NETの大部分がR.A.B.I.D.S.（Roving Autonomous Bartmoss Interface Drones）ウイルス群により破壊された（DataKrash）。

### Rache Bartmossの死とウイルス起動のトリガー
Rache Bartmossは「NET最高のハッカー」とされる反企業のネットランナー。**R.A.B.I.D.S.ウイルスは2014年9月、Ihara-Grubb変換アルゴリズムのリリース時に、彼の死をトリガーとして起動するよう仕込まれた**（企業のデータフォートレスを全て強制的に暴き世界に公開する、という反企業的な「大義の一撃」構想）。

Bartmoss自身の死には**二段階の経緯**がある: (1) 2020年、ネットランニング中に心臓が停止（蘇生失敗）、ただし当時すでに冷凍保存システムへ移行済みだったため肉体は保存された。(2) **2022年、信号を辿られ、彼のコンアパートへの企業強襲部隊による襲撃で（冷凍保存されていた）肉体が破壊され、これが最終的な「死亡」と扱われ、ウイルスのトリガーが引かれた**。

### R.A.B.I.D.S.の挙動と「Old Net」崩壊のメカニズム
R.A.B.I.D.S.は当初「Bartmossの死をもって全企業のデータフォートレスを強制的に破って情報を世界に公開する」という設計意図だったが、**設計パラメータを大幅に超えて暴走し、NETの78.2%に感染、多数のAIを異常化・暴走（ローグAI化）させながらネット全域を荒らし回った**。ウイルスがあまりに強力だったため、**NetWatchでさえ駆除できず、NETを生存させる唯一の方法として、大部分を強力なICE「ブラックウォール」の内側へ封印すること**になった（ブラックウォール建設は2044年、別ノート`04_netwatch_canon.md`参照）。

### 「データが外部同期される前に孤立・凍結」という表現の評価
- 崩壊直後、NETはほぼ使用不能になり、多くの企業・政府は短期的に20世紀のパンチカード技術を復活させて業務を継続した。
- 崩壊後に生き残ったのは**「エアギャップ（外部非接続）ネットワークとデータのみ」**——Militech等、平時からこの機能を採用していた組織は無傷だったとされる。
- 崩壊後のNETは「断片化した孤島の集合（an archipelago of algorithms and code separated by treacherous abysses of nothingness）」として描写される。CitiNet（各都市のローカルネット）は当初エアギャップ状態で構築され、後に再構築された広域NET（当時、放棄都市ピッツバーグ等のサーバー上で稼働していたという記述もある）へ接続された。
- **評価**: 「データセンターのデータが外部同期される前に孤立・凍結」というシナリオ側の表現は、一次資料の文言そのものではないが、**「感染から隔離されたデータ／ネットワークだけが生き残り、断片化した孤島として取り残された」という実態とは方向性が一致する**。旧NET時代のデータセンターが同期未了のまま物理的に取り残された、という読み替えはcanonと矛盾しない創作上の解釈として成立する。

---

## 3. ナイトシティ大虐殺（アラサカタワー核爆発）

### 正確な日付
**2023年8月20日**。

### 経緯・規模
第四次企業戦争（2021-2025年）の最中、Militechの強襲部隊（モーガン・ブラックハンド、ジョニー・シルバーハンドを含む）がアラサカタワーへ潜入し、アラサカの「レリクアリ・データベース計画」（一部情報源ではソウルキラー・プログラムの破壊/奪取が目的とも）を核兵器で破壊しようとしたが、**戦術核（タクティカル・ニューク）が予定より早く、南棟120階で起爆**。爆発は両タワーを瞬時に破壊し、両棟が外側へ倒壊、シティ地区・コーポレート地区の大半が数秒で瓦礫と化した。

**被害規模**: タワー付近で即死約1.2万人、その後数週間〜数ヶ月で重傷後死亡が約50万人、さらに追加で約25万人が死亡（合計で数十万人規模の犠牲）。**ナイトシティ大都市圏で約200万人が住居を失った**。

### 地震・液状化と周縁地域への物理的影響
ナイトシティの多くは埋立地・砂地の上に建設されており、**核爆発により誘発された小規模な地震が地盤を液状化させ、都心部を浸水させた**。液状化した地盤の揺れはガス管・水道管・電力網も破壊した。この液状化・浸水は「都心部（inner city）」を中心とした記述であり、**周縁地域固有の直接的な爆風被害・戦闘被害についての記述は確認できなかった**。

周縁地域への影響として確認できたのは、**大規模な住居喪失と難民流入による過密化**である。焼失による住宅喪失で住民の多くが「湾の反対側の郊外、あるいはさらに遠方」へ移動を強いられ、**ノース・オーク、ウエストブルック、パシフィカ、ヘイウッド、南ナイトシティの周辺郊外に難民が押し寄せ、無数のテント集落を形成した**。**ランチョ・コロナドは戦後世界で最も影響を受けた地域の一つとなり**、戦争で他地区から逃れてきた住民と、都市再建区（Rebuilding Urban Center）のジェントリフィケーションで追われた住民の双方で、地域全体が難民キャンプ・テント集落で埋め尽くされた、との記述がある。

**評価**: 「周縁地域が物理的破壊を受けた」というよりは、「周縁地域が難民流入・過密化・インフラ未整備の放置状態に陥った」という描写がcanonにより近い。マーダーミステリーの舞台設定としては、**「戦闘で破壊された」ではなく「災害後の無秩序な過密化・インフラ空白地帯として長年放置された」という前提の方が一次資料との整合性が高い**。

### 第四次企業戦争のナイトシティ市街戦
大虐殺直前（2023年8月時点）、**ナイトシティはアラサカが実効支配する北米最後の拠点**であり、CEOケイ・アラサカがタワーから指揮を執り、Militech・米国政府との和平交渉を試みていた。ナイトシティは、カリフォルニア州知事デニース・デ・ラ・ベガが派遣した州兵、米陸軍のエリート特殊部隊・空挺部隊、Militech部隊（パトリック・エディントン将軍指揮）によって、**市外の高地から包囲**されていた。

**しかし、この包囲部隊とアラサカ守備隊との間で、市内で大規模な地上戦闘（歩兵戦・市街戦）が実際に行われたという直接的な記述は、検索範囲内では確認できなかった（未確認）**。核爆発そのものが「戦災」の中心的な原因であり、通常戦闘による周縁地域の建物破壊・放棄・埋没という筋書きの直接的裏付けは薄い。ただし、大虐殺後の瓦礫撤去作業では**「戦車や大型建設用ブルドーザーが投入され、爆心地周辺の瓦礫を湾へ押し流す」**という大規模な重機作業が行われたとの記述があり、**この瓦礫処理・土木作業の過程で何かが地中に埋もれる、という筋書きへの転用は可能**（ただし一次資料はこれを「データセンターの埋没」と結びつけていない）。

---

## 4. アラサカの戦後処遇（北米追放・2045年時点の状態）

### 追放の経緯と根拠
ナイトシティでの核兵器使用という重大な国際問題の隠蔽・処理のため、**アラサカは一時的に北米事業を停止**。米国政府は、依然として大規模な兵力を持つ米軍の統制下にMilitechを置き、**アラサカ東京本社への報復核攻撃の威嚇のもと、アラサカの全戦力を米国本土から追放**した。他国もこれに追随し、第四次企業戦争の両当事者（アラサカ・Militech双方）の資産を国有化・凍結する動きが広がった。

### 2045年（RED）時点の状態
**アラサカは数年間、日本国内での活動に事実上封じ込められ、評判の再建を図った**。この追放状態は**2045年（RED期）時点でも継続中**であることが確認できる（`03_factions_canon.md`ですでに確認済みの内容と一致）。

### 追放解除の時期
**追放解除はUnification War（統一戦争、2069年1月〜2070年6月）後**であり、これは**2045年よりはるかに後の出来事**。すなわち、**2045年時点で「アラサカが北米大陸内で公式に大手として活動できない」という前提は確度の高いcanon整合事実**である。

### 2045年時点のナイトシティ統治体制と「力の空白」の実態（重要な発見）
2045年（Time of the Red期）、ナイトシティの市政府は**技術的な非常事態が継続する状態**にあり、市長職は長年空席のまま、代わりに**旧市政府の生存者・エッジランナー派閥・ノマド一族・複数の企業からなる混成「シティ・カウンシル」（ジャンタ＝寡頭統治体）**が市政を運営していた。カウンシル参加企業として**ゼタテック、バイオテクニカ、ペトロケムに加え、「密かにアラサカも」参加している**との記述が確認できた。

カウンシルは通常100議席で、ナイトシティに存在する上位10社が議席の後ろ盾になっているとされ、構成派閥は「ノマド一族」「エッジランナー（ネットランナー・ソロ・ロッカーボーイ等）」「旧市政府」「企業勢力」の4系統。混乱に対応するため、**各地区の代表として選出される「シティ・マネージャー」制度による権力の地方分散**も進んでいた——2040年代には、各マネージャーはそれぞれの派閥から選ばれ、担当地区のデータプール管理・ゾーニング・道路インフラ税・私立探偵/警備ライセンス・建設/司法サービスの契約などを担っていた、とされる。**ただしコンバットゾーン（旧無法地帯）にもマネージャーは存在するものの実権はほとんどなく、各セクターの実質的な支配者はギャング・企業・フィクサーのいずれかである**、との記述がある。

### 評価（「大手不在の力の空白」の妥当性）
- **支持できる点**: 単独の巨大企業（アラサカ・Militechのような旧来のメガコーポ級プレイヤー）がナイトシティを一元支配する状態ではなく、**権力が企業・ノマド・エッジランナー・ギャング・フィクサーに細分化・分散した「隙間だらけの統治」状態**にある。周縁地域（コンバットゾーン等）は特に「統一的な支配者不在」の色合いが強い。
- **要注意な点**: 「大手が完全に不在」ではない——ゼタテック・バイオテクニカ・ペトロケムという中堅〜大手企業がカウンシルに議席を持ち、**アラサカでさえ「密かに」議席を持つ**とされる。「大手不在」を字義通りに使うと、この一次資料と矛盾する。
- **推奨**: シナリオの表現は「大手不在」ではなく、**「単独の大手が支配権を独占できない、無数の小勢力（中堅企業・ノマド・ギャング・フィクサー）が縄張りを分け合う権力の隙間」**とする方が、確認できた一次資料により忠実。「アラサカが表向き不在だが、実は密かに関与している」という構造は、むしろシナリオの裏設定（例: 潜入ネットランナーの黒幕がアラサカ系という捻り）として積極的に活用できる余地がある。

---

## 5. 旧NET物理インフラの2045年時点の扱い（データセンター遺構サルベージ）

### 検索結果の総括
「旧NET時代のデータセンター・サーバー施設が物理的な遺構として2045年時点で残存し、サルベージ・発掘の対象になる」という直接的なcanon記述は、**検索範囲内では見つからなかった（canon空白）**。

REDコアルールブックやBlack Chrome等サプリメントの該当ページを直接参照できておらず、WebFetchでの一次資料アクセスもすべて失敗したため、**この項目は一次資料未確認のまま**である。

### 間接的に支持材料になる周辺情報
- DataKrash後、崩壊したNETは「断片化した孤島の集合」として残存し、**当時のNETが再構築された広域網は放棄都市（例: ピッツバーグ）のサーバー上で稼働していた**、という記述がある。「旧時代のデータが、使われなくなった物理施設に取り残された」というモチーフ自体は存在する。
- ナイトシティ大虐殺後の瓦礫撤去では、**戦車・重機を投入して爆心地周辺の瓦礫を湾へ押し流す**という大規模土木作業が行われた、との記述がある。
- 2040年代の周縁部再開発は「**ゴーストタウン化していた地区が変貌していく**」プロセスとして描写され、**巨大複合施設（メガビルディング）建設が2040年代の再建の主眼**だったとされる一方、**コンバットゾーンなど一部地区は再建の対象から外れたまま放置**されていた、との記述もある。

### 評価
「工事中に旧NETデータセンターが出土する」という筋書きは、**直接のcanon記述による裏付けはないが、明確な矛盾も見当たらない「canon空白」領域**。周縁部に「長年手つかずのまま放置されたゴーストタウン」が実在し、2040年代にそこで大規模建設工事（メガビルディング建設等）が行われていたという設定的土壌は確認できるため、**「放置されていた地区の再開発工事中に、DataKrash期に取り残された旧時代のデータインフラが偶然発掘される」という筋書きは、シナリオ側で自由に創作してよい部類**と判断する。

---

## 6. 補足: NetWatchとの関係整理

`04_netwatch_canon.md` で確認済みの通り、**Old Netの残骸（Deep Net最深部）の探索・脅威の無力化はNetWatch自身の本来任務の一つ**とされる。したがって、本シナリオで「周縁部で旧NETデータセンターが出土する」という事件が起きた場合、**NetWatchが（阻止ではなく）介入・調査に乗り出す動機は一次資料の範囲内で自然に成立する**（民間による遺構サルベージを一律に禁止する記述はないが、遺構内にローグAI等の脅威が眠っている可能性を懸念して監視・介入する、という限定的な関与は矛盾しない）。

---

## 7. 因果チェーンの各リンク判定（canon整合／矛盾／空白）

| # | リンク | 判定 | 理由・修正提案 |
|---|---|---|---|
| 1 | 2022年頃DataKrashで旧NETが論理的に死ぬ（データが外部同期される前に孤立・凍結） | **canon整合**（表現は脚色だが方向性一致） | 年月日は2022年6月3日で確定。「エアギャップ外のデータ・NETは崩壊、断片化した孤島として取り残された」という実態と整合。「外部同期前に孤立」という言い回しはそのまま使ってよい創作的表現 |
| 2 | 2023年アラサカタワー核爆発（ナイトシティ大虐殺）と第四次企業戦争の戦災で、周縁地域の旧NETデータセンターが物理的に埋没 | **要修正（部分的にcanon矛盾）** | 日付・爆発規模はcanon整合（2023年8月20日、両タワー崩壊、都心部壊滅）。だが**「戦災による周縁地域の物理的破壊」は一次資料に直接の裏付けがない**——周縁部への実際の影響は「地盤液状化」ではなく主に「難民流入による過密化・放置」。**修正案**: 「戦闘・爆風で埋没」ではなく、「大虐殺後の混乱・難民流入で周縁部のインフラ整備が長年放置され、旧NET時代の施設もゴーストタウン化した区画に埋もれるように放棄された」という因果に寄せると一次資料と整合しやすい |
| 3 | アラサカは北米追放され、大手不在の力の空白の中で2045年に周縁地域の再開発が始まる | **要注意（大枠は整合、表現の精度に要修正）** | アラサカの北米追放・2045年時点での継続は**canon整合**（確度高）。だが「大手不在」は不正確——**ゼタテック・バイオテクニカ・ペトロケムに加え密かにアラサカもシティ・カウンシルに議席を持つ**。**修正案**: 「大手不在」ではなく「単独の大手が支配できない、無数の中堅企業・ノマド・ギャング・フィクサーが縄張りを分け合う権力の隙間」と表現し、必要なら「アラサカは表向き不在だが実は隠然と関与している」という裏設定を活かす |
| 4 | 工事中にデータセンターが出土する | **canon空白（創作で埋めてよい）** | 直接の一次資料裏付けはないが、矛盾も見当たらない。周縁部のゴーストタウン化・2040年代のメガビルディング建設ラッシュという土壌はcanonで確認済みであり、その延長線上の出土イベントとして自由に設計してよい |

**全体の推奨修正版（因果チェーン）**:
> 2022年6月、DataKrashで旧NETの大部分が崩壊。外部と同期できなかった一部データ・施設は「孤立した遺物」として旧NET内に取り残される。2023年8月、ナイトシティ大虐殺と第四次企業戦争の混乱で都市機能が麻痺、周縁地域は難民流入による無秩序な過密化とインフラ整備の長年の放置に陥り、その中で当該の旧NETデータセンターも顧みられずゴーストタウン化した区画に埋もれていく。アラサカは北米から追放され表向き大手不在となるが、実際には単独の大手が支配権を握れない無数の中堅企業・ノマド・ギャング・フィクサーが縄張りを分け合う権力の隙間が生じ、2045年、その隙間を埋めるべく周縁地域の再開発コンソーシアムが立ち上がる。工事中、忘れられていたデータセンターが偶然出土する。

---

## 8. 参照URL一覧

- [DataKrash | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/DataKrash)
- [Rache Bartmoss | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Rache_Bartmoss)
- [R.A.B.I.D.S. | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/R.A.B.I.D.S.)
- [Rache Bartmoss — Grokipedia](https://grokipedia.com/page/Rache_Bartmoss)
- [Cyberpunk 2077: Who Rache Bartmoss Really Was — ScreenRant](https://screenrant.com/cyberpunk-2077-rache-bartmoss-netrunner-lore-night-city/)
- [Deathwish | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Deathwish)
- [Night City Holocaust | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Night_City_Holocaust)
- [The Night City Holocaust | Cyberpunk Red 2047 Wiki | Fandom](https://cyberpunk-red-2047.fandom.com/wiki/The_Night_City_Holocaust)
- [Night City Holocaust — Grokipedia](https://grokipedia.com/page/Night_City_Holocaust)
- [The Day the Tower Fell | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/The_Day_the_Tower_Fell)
- [Arasaka Towers | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Arasaka_Towers)
- [Arasaka Memorial | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Arasaka_Memorial)
- [Night City Holocaust | Cyberpunk+BreezeWiki](https://breezewiki.com/cyberpunk/wiki/Night_City_Holocaust)
- [Fourth Corporate War | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Fourth_Corporate_War)
- [The Fourth Corporate war Military Conflict in Night City | World Anvil](https://www.worldanvil.com/w/night-city-mindlessorca/a/the-fourth-corporate-war-militaryConflict)
- [Water, Chrome and Blood - THE FOURTH CORPORATE WAR | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Water,_Chrome_and_Blood_-_THE_FOURTH_CORPORATE_WAR)
- [Arasaka (Cyberpunk 2077) — Grokipedia](https://grokipedia.com/page/Arasaka_Cyberpunk_2077)
- [Arasaka | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Arasaka)
- [Arasaka Organization in Cyberpunk Red 2045 | World Anvil](https://www.worldanvil.com/w/cyberpunk-red-2045-chefrude/a/arasaka-organization)
- [Unification War | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Unification_War)
- [Time of the Red | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Time_of_the_Red)
- [Cyberpunk 2077 Lore - The Time Of Red — pupilswim.com](https://pupilswim.com/cyberpunk-2077-history/the-age-of-red)
- [Timeline | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Timeline)
- [Combat Zone (RED) | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Combat_Zone_(RED))
- [South Night City (RED) | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/South_Night_City_(RED))
- [Watson Development | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Watson_Development)
- [Government of Night City | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Government_of_Night_City)
- [Night City Council Organization in Cyberpunk RED | World Anvil](https://www.worldanvil.com/w/cyberpunk-red-gamemonstergr/a/night-city-council-organization)
- [Night City Overview | Cyberpunk Red 2047 Wiki | Fandom](https://cyberpunk-red-2047.fandom.com/wiki/Night_City_Overview)
- [Night City Settlement in Night City | World Anvil](https://www.worldanvil.com/w/night-city-mindlessorca/a/night-city-settlement)
- [Night City Settlement in The Dark Future | World Anvil](https://www.worldanvil.com/w/the-dark-future-rotten-daydream/a/night-city-settlement)
- [Rancho Coronado (RED) | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Rancho_Coronado_(RED))
- [Rancho Coronado | Cyberpunk Red 2047 Wiki | Fandom](https://cyberpunk-red-2047.fandom.com/wiki/Rancho_Coronado)
- [Overpacked Suburbs | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Overpacked_Suburbs)
- [Heywood (RED) | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Heywood_(RED))
- [Net | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Net)
- [Cyberpunk RED Alert: Night City – R. Talsorian Games](https://rtalsoriangames.com/2020/10/23/cyberpunk-red-alert-night-city/amp/)
