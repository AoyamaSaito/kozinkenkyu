# Cyberpunk RED 世界観調査ノート — NetWatch（ネットウォッチ）のcanon整合検証

## 0. この調査の目的と方法

自作マーダーミステリー（Cyberpunk RED 世界・2045年＝赤の時代）で、「NetWatch捜査官が経歴を偽ってゼタテック等の中堅企業に潜入している」というキャラクターを使う想定の、設定的整合性を検証するための一次資料集め。

- 主な情報源: Cyberpunk Wiki (Fandom)、Grokipedia、R. Talsorian Games公式ブログ、Never Fade Away Wiki（RED専用ファンWiki）等。
- **`03_factions_canon.md` と同じ既知の問題として、WebFetchツールがcyberpunk.fandom.com本体および `never-fade-away.fandom.com` への直接アクセスをHTTP 402/403で拒否したため、本ノートもすべてWeb検索エンジンが返す抜粋・要約経由の情報である**。一次資料（コアルールブック・サプリメントPDF本文）を直接確認したわけではない点に注意。rtalsoriangames.com のブログ記事本文は検索エンジン経由の抜粋のみ取得でき、直接WebFetchは今回試行しなかった（検索結果に十分な抜粋が含まれていたため）。
- 時代区分は「1993年版(2013)/2020年版/RED版(2045)/2077年版」の4層で区別し、時代が特定できない情報は**未確認**と明記した。NetWatchは特に2077年ゲーム本編（およびDLC『Phantom Liberty』）での描写量が圧倒的に多く、2045年（RED）固有の情報と混同しやすい対象である点に最大限注意した。

---

## 1. 冒頭要約（Executive Summary）

| 調査項目 | 結論 | 確度 |
|---|---|---|
| 設立経緯 | RED/2077世代の設定では「1991年設立の英国民間ネットセキュリティ企業」が起源、2013年の条約で国際機関化。**2020年版旧設定（2013年に国連条約で新規設立）とは異なるレトコンが入っている** | 中（複数ソースで一致） |
| DataKrash後の状態 | 2022年のDataKrashでNET大部分が破壊された後も**組織自体は存続**。復旧を試みたが断念し大半のノードを閉鎖、公共アクセス層の巡回とBlackwall建設に転換 | 中 |
| **2045年時点の状態（最重要）** | **存続しているが、管轄は「公共アクセス層のNET」と「Blackwallの防衛」が中心。CitiNet（企業城下町ネット）は2045年時点ではまだZigguratという別企業が管理しており、NetWatchがCitiNetを接収するのは2050年代（RED以降）** | 中〜高（複数ソースで年代が符合） |
| Blackwallの存在 | **2044年に建設**——RED（2045年）の**わずか1年前**。極秘プロジェクトとして進行し、公式記録には存在しない「都市伝説」的な扱いだった時期に相当する | 中〜高 |
| 潜入捜査官のcanon事例 | 存在するが**すべて2077年（ゲーム本編・Phantom Liberty）の事例**で、**潜入先は企業ではなくギャング（ヴードゥー・ボーイズ）**。2045年時点の潜入捜査官の記述は検索範囲内で確認できなかった | 中（2077年の2事例は複数ソース一致、2045年適用は未確認） |
| 旧NET遺構サルベージへの関与 | NetWatch自身が「Old Netの残骸のサルベージ」を主要任務の一つとする記述はあるが、**民間企業による遺構サルベージを阻止する・妨害するという直接的な記述は確認できなかった（未確認）** | 低（要追加調査） |
| 代替案の材料 | CitiNet運営元Ziggurat社、各企業が個別に持つNETアーキテクチャ内蔵の警備プログラム（Black ICE）、企業お抱い/契約のネットランナー、の3系統が2045年設定として裏付けが取れる | 中〜高 |

**最優先での結論（潜入捜査官設定の成立性）**: 「NetWatch捜査官が2045年に中堅企業へ経歴偽装潜入する」というアイデアは、**canon的に"要脚色"判定**。理由は、(a) NetWatchの2045年時点の管轄が企業内部ネットではなく公共NET／Blackwall防衛に集中しており、地域企業への出向・潜入の職務上の必然性が薄いこと、(b) 潜入捜査官のcanon前例が2つとも2077年・対ギャング（企業ではない）であること、の2点。ただし「NetWatchの管轄外行動＝越権・個人的動機での潜入」という体で脚色すれば、矛盾なく成立させられる余地は大きい（詳細は§7）。

---

## 2. NetWatchの設立経緯・本来の任務

RED版・2077年版の設定では、NetWatchは**1991年に設立された英国の民間ネットセキュリティ企業**が前身であり、2013年にアメリカ/ユーロシアター間の条約によって国際的な取り締まり機関へと改組された、とされる。

**重要な注意（レトコンの存在）**: 旧2020年版の設定では「NetWatchは2013年、国連と世界通信ネットワーク（WCN）の間の条約により新規設立された」とされていたが、**RED版・2077年版ではこれが変更され、「1991年設立の既存の民間企業が母体」という設定に上書きされている**。どちらの版の情報を参照しているかで年表の食い違いが生じるため、シナリオでの言及時は「1991年起源説（RED/2077準拠）」を採用するのが安全。

当初の本来任務は、企業からの契約に基づき、悪質なハッカー・コンピュータ犯罪者を取り締まること（逮捕・収監が主目的だが、Black ICEプログラムを用いて敵対者を殺傷・無力化することもあったとされる）。国際化後は、国連傘下の「緩やかな世界規模の許認可」を得て、NET上の全公共アクセス層を巡回し、不正なネットランナー活動の追跡・摘発、危険なローグAIの狩り出し、Deep Net最深部の脅威の探索・無力化、Blackwall越えの人物・AIの移動阻止、公共ネット空間の拡張支援、を任務とする。

---

## 3. DataKrash（2022年）後のNetWatchの状態

2022年6月3日、Rache Bartmossが放ったR.A.B.I.D.Sウイルス群により、旧NETの大部分が破壊された（DataKrash）。直後の混乱期には、NET利用が困難になったため多くの企業・政府が20世紀のパンチカード技術を一時的に復活させて業務を継続した、との記述がある。

NetWatchはこの惨状の復旧を試みたが、最終的に断念し、大半のノードを閉鎖した（rtalsoriangames.com由来の記述）。その後、Blackwall完成（後述、2044年）までの間、NETは「企業・団体が個別に無秩序に構築した私設ネットの集合体」へと断片化し、NetWatchは**一般人がアクセス可能な部分の監視**に役割を絞った、とされる。

**組織自体が崩壊したという記述は確認できなかった**。弱体化・機能縮小はしたが、存続し続けている、というのが複数ソースで一致する見方。

---

## 4. 2045年（Cyberpunk RED）時点でのNetWatchの状態

DataKrash後の2030〜2040年代を通じて、NetWatchは公共NETの巡回とBlackwall関連プロジェクトに注力していた、とされる。

**CitiNetとの関係（要注意・情報の食い違いあり）**: 検索結果には「2030〜2040年代、NetWatchがCitiNet（各都市のローカルVPN）の開発を監督していた」という記述と、「CitiNetはZiggurat社が開発した」という記述の**両方が存在し、内容が矛盾している**。Ziggurat関連の複数ソースをクロスチェックした結果、**より具体的で年代の整合するのはZiggurat社説**であると判断した:
- Ziggurat社は2030年、ナイトシティで設立。DataKrashの後始末として、旧Data Term網を刷新する計画をNight Corp（助成金）とナイトシティ市議会（支援）の後押しで実行し、数ヶ月で最初のCitiNetを稼働させた。
- 2040年までに、Zigguratは新アメリカ合衆国・パシフィカ連合・自由諸州・カナダの主要な再建都市の大半にCitiNetとData Poolを展開済み。
- **NetWatchがZiggurat社を強制的に解体し、全世界のCitiNetの管理権を接収するのは2050年代**——つまり**RED（2045年）の時点より後**の出来事である。

この時系列を素直に読むと、**2045年時点ではCitiNet＝各都市のローカル企業ネットの管理主体はまだZiggurat社であり、NetWatchはまだCitiNetの直接統制権を持っていない**。NetWatchの2045年時点の実質的な管轄は「グローバルな公共NET層の巡回」と「Blackwall防衛」に留まっていた可能性が高い。ただし、CitiNet内のメール通信がNetWatchによって監視可能、という記述も別途あり、"接収前でも一定の監視協力関係はあった"という中間的な状態だった可能性も残る（**この点は一次資料未確認、検索エンジン要約の重ね合わせによる推定である**）。

**総括**: 2045年のNetWatchは、2077年の「都市の全CitiNetを直接支配する強大な管理機構」としてのイメージとは異なり、**まだ発展途上・管轄限定的な組織だった**と見るのが時系列上妥当。

---

## 5. Blackwallは2045年時点で存在するか

**存在する。ただし建設完了はRED設定のわずか1年前、2044年**。

NetWatchはDataKrash後、R.A.B.I.D.Sを生き延びたAI群（トランセンデンタルズ、ゴースト等と呼ばれる勢力）と2044年に接触し、旧NETを制御下に置くための共同プロジェクトを極秘に開始した。これが後に「ブラックウォール（Black Wall）」と呼ばれるようになったもので、当時は公式の書籍・記録には一切存在せず、「都市伝説」レベルの噂としてのみ知られていた、との記述がある。NetWatch屈指のネットランナー数十名が構築を担当し、断片化・不安定化しつつもまだ使用可能なNETを、廃墟と化したサイバースペースを徘徊するローグAIから守る防護壁として機能させた。

**シナリオ上の含意**: 2045年（RED）の卓内正史でBlackwallに言及する場合、「つい最近完成したばかりの、まだ都市伝説めいた噂話の域を出ない極秘プロジェクト」として描くのが時代考証的に最も正確。2077年作品群で描かれる「誰もが知っている確立された防壁」というイメージをそのまま持ち込むのは不正確。

---

## 6. NetWatchが人的エージェント（潜入捜査官）を運用するcanon事例

確認できた具体的な潜入捜査官の事例は2件、**いずれも2077年（ゲーム本編・DLC『Phantom Liberty』）設定**:

1. **ブライス・モズリー（Bryce Mosley）**: メインストーリーのミッション「I Walk the Line」に登場。ヴードゥー・ボーイズのネットランニング作戦に潜入し、Blackwallを突破してローグAIと接触する計画を阻止しようとしていたNetWatch特別捜査官。任務中に捕らえられた状態でVに発見される。
2. **アラン・ノエル（Alan Noël）**: DLC『Phantom Liberty』に登場。ドッグタウンのヴードゥー・ボーイズに潜入するモグラ（もぐらエージェント）。ヴードゥー・ボーイズが「命令に従わない者のインプラントをハッキングして死に至らしめる」慣行を調べるのが任務。数ヶ月にわたる潜入生活を「嫌っていた」との人物描写あり。

**両事例に共通する重要な特徴**: (1) 時代はいずれも2077年、(2) 潜入先はどちらも**企業ではなくギャング（ヴードゥー・ボーイズ）**、(3) 動機はBlackwall/ローグAI関連の脅威監視という、NetWatch本来の管轄（対ローグAI・Blackwall防衛）に直結する任務。「中堅企業への経歴偽装潜入」という、対企業・産業スパイ的な構図の直接的なcanon前例は**検索範囲内では見つからなかった（未確認）**。

**時代の観点からの評価**: これら2事例をそのまま2045年に持ち込むのは時代考証上不適切（2077年固有）。ただし「NetWatchが自らの管轄事項（ローグAI・Blackwall・危険なネットランナー集団）に関わる標的へ、身分を隠して長期潜入する」という**手法・運用パターン自体**は、2045年に翻案する分には矛盾がない類推材料にはなる。

---

## 7. 旧NET遺構のサルベージに対するNetWatchの関与

NetWatch自身の本来任務の一つとして「Deep Net最深部（廃墟と化した旧NET領域）の探索・脅威の無力化」が挙げられており、**NetWatch自体が旧NET遺構の"サルベージ"に相当する活動を行う主体である**、という記述は確認できた。

一方で、**民間企業や第三者が旧NET遺構（本シナリオでの「工事中に出土した旧NETデータ遺跡」に相当するもの）を独自にサルベージしようとした際、NetWatchがそれを阻止・妨害する立場を取るという直接的な記述は、検索範囲内では確認できなかった（未確認）**。Blackwallの本来の目的が「ローグAIの越境阻止」であることから類推すると、**NetWatchが介入する可能性が高いのは「サルベージ対象の遺構にローグAIが潜んでいる／Blackwallの防御に影響する場合」に限定される**と考えるのが自然な拡張だが、これは一次資料に基づかない類推である点を明記しておく。

**シナリオへの適用示唆**: 「NetWatchは遺構サルベージそのものを一律に禁止する法執行機関」ではなく、「遺構の中に危険なデータ・AIが眠っている可能性を懸念して監視・介入する」という限定的な関与として描く方が、確認できた一次資料の範囲内では無難。

---

## 8. NetWatchが2045年に苦しい場合の代替勢力候補

企業潜入捜査官という筋書きの主体をNetWatch以外に置き換える場合の、2045年時点で実在が確認できる代替候補:

### 候補1: Ziggurat社（CitiNet運営元）
2030年設立、2040年までに新アメリカ合衆国・パシフィカ連合・自由諸州・カナダの主要都市にCitiNetを展開済みの、都市ネット運営専業企業。**2045年時点でCitiNetの管理主体はこの企業であり、NetWatchではない**ため、「都市ネットのセキュリティ監督者」という役回りを求めるなら、NetWatchよりむしろZigguratの方が2045年時点の管轄と整合する。ただしZiggurat社自体の企業文化・エージェント運用実態は**未確認**。

### 候補2: 各企業個別のネットセキュリティ（Black ICE運用担当部門）
RED本編のネットランニングルールでは、NETアーキテクチャ（企業内部ネット）は個々の企業が所有し、Black ICE（侵入対抗プログラム）を独自に配備して防衛する、という構造になっている。**企業内部ネットの警備は、NetWatchではなく各企業自身の情報セキュリティ部門が担う**、という構図がゲームシステム上も裏付けられる。「ゼタテックに潜入する捜査官」であれば、むしろ「競合他社（あるいは別の勢力）が送り込んだ産業スパイ・契約ネットランナー」という体の方が、NetWatchの管轄外領域に踏み込む必要がなく整合しやすい。

### 候補3: 企業お抱え／契約のネットランナー（フィクサー経由の傭兵型）
NetWatchのような法執行機関ではなく、フィクサーを介して各企業・勢力が個別に雇う独立系ネットランナーという立場。「経歴を偽って潜入する」動機を、法執行としての正義感ではなく金銭・私的な依頼・別勢力への忠誠として設計でき、交渉・推理重視のシナリオ構造（プレイヤー間の腹の探り合い）とも相性が良い。

### 候補4（脚色前提での折衷案）: 元NetWatch／NetWatch出身の独立系エージェント
NetWatch現職ではなく、**NetWatchを離職・除籍された元捜査官**という設定にすれば、(a) NetWatch由来のスキルセット・人脈・Blackwall関連の専門知識という説得力ある背景を持たせつつ、(b) 現組織の管轄外行動という制約を受けず自由に企業潜入させられる、という両立が可能。2045年時点のNetWatchが「発展途上でまだ全能ではない」という調査結果（§4）とも整合し、「本流から外れた者が独自の正義感・私怨・金銭目的で動く」という人物造形は、交渉重視のマーダーミステリーの動機設計として扱いやすい。

---

## 9. 参照URL一覧

- [NetWatch | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/NetWatch)
- [NetWatch — Grokipedia](https://grokipedia.com/page/netwatch)
- [NetWatch | Never Fade Away (A Cyberpunk Red Tabletop Game) Wiki | Fandom](https://never-fade-away.fandom.com/wiki/NetWatch)
- [NetWatch regional agents | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/NetWatch_regional_agents)
- [NetWatch Regional Directors | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/NetWatch_Regional_Directors)
- [List of NetWatch employees | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/List_of_NetWatch_employees)
- [Looking for a career change? Join NetWatch! | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Looking_for_a_career_change%3F_Join_NetWatch!)
- [Guide :: NetWatch - Cyberpunk 2077 (Steam Community)](https://steamcommunity.com/sharedfiles/filedetails/?id=3594999196)
- [Bryce Mosley | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Bryce_Mosley)
- [The best Cyberpunk 2077 NetWatch Agent choice explained | GamesRadar+](https://www.gamesradar.com/cyberpunk-2077-netwatch-agent-data-confront-incapacitate-i-walk-the-line/)
- [Cyberpunk 2077 I Walk the Line quest | PCGamer](https://www.pcgamer.com/cyberpunk-2077-i-walk-the-line-netwatch-choice/)
- [Cyberpunk 2077: Should you side with the Netwatch Agent or Voodoo Boys? | Dot Esports](https://dotesports.com/cyberpunk/news/cyberpunk-2077-should-you-side-with-the-netwatch-agent-or-voodoo-boys)
- [DataKrash | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/DataKrash)
- [Blackwall | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Blackwall)
- [Blackwall (Cyberpunk 2077) — Grokipedia](https://grokipedia.com/page/Blackwall_Cyberpunk_2077)
- [Artificial Intelligence | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Artificial_Intelligence)
- [CitiNet | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/CitiNet)
- [Data Pool | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Data_Pool)
- [Ziggurat | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Ziggurat)
- [Ziggurat (The Info-Giant) — Grokipedia](https://grokipedia.com/page/Ziggurat_The_Info-Giant)
- [Ziggurat Organization in Cyberpunk Red 2045 | World Anvil](https://www.worldanvil.com/w/cyberpunk-red-2045-chefrude/a/ziggurat-organization)
- [Ziggurat | Cyberpunk RED Nexus (Demiplane)](https://app.demiplane.com/nexus/cyberpunkred/corporations/ziggurat)
- [Intrusion Countermeasures Electronics | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Intrusion_Countermeasures_Electronics)
- [Black ICE | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Black_ICE)
- [The Net in Night City | World Anvil](https://www.worldanvil.com/w/night-city-mindlessorca/a/the-net-article)
- [Danger Gal Dossier | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Danger_Gal_Dossier)
- [Night City 2045 – R. Talsorian Games](https://rtalsoriangames.com/night-city-2045/)
- [Night City 2045 | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Night_City_2045)
- [Cyberpunk RED | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Cyberpunk_RED)
- [Netrunner | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Netrunner)
- [Netrunner - Roles | Cyberpunk RED Nexus (Demiplane)](https://app.demiplane.com/nexus/cyberpunkred/roles/netrunner)
- [Timeline | Cyberpunk Wiki | Fandom](https://cyberpunk.fandom.com/wiki/Timeline)
