export const meta = {
  name: 'nozoki-no-shiro-sim',
  description: '覗きの代 マダミスシミュレーション（4PL×GM）',
  phases: [
    { title: 'Phase 0: 導入', model: 'sonnet' },
    { title: 'Phase 1: 第1調査', model: 'sonnet' },
    { title: 'Phase 2: 第1会議', model: 'sonnet' },
    { title: 'Phase 3: 固有ターン1', model: 'sonnet' },
    { title: 'Phase 4: 第2調査', model: 'sonnet' },
    { title: 'Phase 5: 第2会議', model: 'sonnet' },
    { title: 'Phase 6: 固有ターン2', model: 'sonnet' },
    { title: 'Phase 7: 最終調査', model: 'sonnet' },
    { title: 'Phase 8: 最終会議+投票', model: 'sonnet' },
    { title: 'Phase 9: エンディング' },
  ],
}

// ================================================================
// 1. 定数
// ================================================================

const ROLES = ['folklorist', 'investigator', 'professor', 'student']

const DISPLAY = {
  folklorist: '民俗学者',
  investigator: '調査隊員',
  professor: '大学教授',
  student: '大学院生',
}

// ================================================================
// 2. ゲームデータ — 手がかり（全20枚）
// ================================================================

const CLUES = [
  // P1（phase:1, 全て通常）
  { id: 'p1_01', title: '施設銘板（破損）', phase: 1, text: '入口付近の金属銘板。「○○県御影村　██████研究所」名称の一部が意図的に削り取られている。裏面に設立年の刻印のみ。' },
  { id: 'p1_02', title: '先遣隊 活動記録', phase: 1, text: '[██年5月12日] 第3日。B区画の調査を継続。設備の劣化が激しいが通行に支障なし。明日は奥の区画に入る予定。──以降の記録はない。' },
  { id: 'p1_03', title: '防護服のロッカー', phase: 1, text: '壁面のロッカーに特殊な防護服が数着。内側に焦げた跡のあるもの、未開封のまま残されたもの。通常とは異なる構造をしている。何を想定した装備なのか。' },
  { id: 'p1_04', title: '古い神棚', phase: 1, text: '研究室の壁に設えられた神棚。注連縄と御札。「鎮め」と墨書された木札が一枚だけ床に落ちている。科学施設には似つかわしくない。' },
  { id: 'p1_05', title: '研究日誌の断片', phase: 1, text: '対象の観察を継続する。既知の生物学的分類に該当しない。接触時の反応パターンを引き続き記録する。差し当たり、危険性は低い。' },
  { id: 'p1_06', title: '収容監視ログ', phase: 1, text: '[自動記録] ██/██ 収容状態：正常（複数回）→ ██/██ 収容状態：異常 ──Loss detected── 以降の記録なし。' },
  { id: 'p1_07', title: '特殊保管容器（空）', phase: 1, text: '頑丈な作りの容器。内壁に緩衝材と固定具。明らかに何かを収めるための形状だが中は空。蓋の内側に掻き傷がある。' },
  { id: 'p1_08', title: '査読ログ OBS-0041', phase: 1, text: '管理番号: OBS-0041 定期観察記録。被験体3名中、2名に認知機能低下を確認。1名は異常なし──記録と一致せず。干渉に2系統の反応パターンを認む。要精査。', professorExtra: '「2系統」──すなわち、被験体の認知構造が保持される場合と、不可逆的に崩壊する場合がある。前者の発生条件は未解明だが、後者は求心力の完全喪失と一致する。両経路を分岐させる条件の解明は本施設の最優先課題である。' },

  // P4（phase:4）通常6枚
  { id: 'p4_01', title: '破損した拘束具', phase: 4, text: '区画の奥に据えられた金属の椅子。両腕と両足に拘束ベルト。片方のベルトが根元から引きちぎられている。座面に経年の汚れ。長い間使われていた形跡がある。' },
  { id: 'p4_02', title: '先遣隊の最終手記', phase: 4, text: '[手書き・走り書き] 奥の区画で遭遇。接触を試みたが反応が予測と異なる。退避を── ここでインクが途切れている。ノートの残りは白紙。' },
  { id: 'p4_03', title: '灰の残骸', phase: 4, text: '隔離区画の奥に、灰の塊。先遣隊と違い、人の原型すらとどめていない。ただの灰。' },
  { id: 'p4_04', title: '封鎖プロトコル通知', phase: 4, text: '[施設管理システム] ██/██ 通信喪失を検知。プロトコルF-7を発動。外周封鎖──完了。解除条件: ██████████' },
  { id: 'p4_05', title: '散乱した調査装備', phase: 4, text: '先遣隊のものと思われる装備。測定機器、記録媒体、通信端末。床に散乱している。一部はまだ電源が入ったまま。持ち主が突然いなくなったかのよう。' },
  { id: 'p4_06', title: '走査装置の動作ログ', phase: 4, text: '[自動走査ログ] 設置場所: 区画間認証機構 ██/██ 走査実行──非該当 ██/██ 走査実行──該当(1) ──区画間移動を検出──' },
  // P4 固有マス
  { id: 'p4_safe', title: '論文①（覗き込み現象の段階的記録）', phase: 4, text: '覗き込みが被験体に及ぼす影響は求心力の残存量に応じた四段階に分類される。Ⅰ精神不安定、Ⅱ自意識喪失、Ⅲ器の崩壊、？灰のみ残存。特異症例として、崩壊が極端に進行し灰のみが残る事例が存在する──依代として転用された場合の帰結と推測される。', professorExtra: '段階Ⅲ「器の崩壊」と段階「？」の差異は、覗かれただけか器として使い切られたかの差に対応する。先遣隊の崩壊痕跡のうち「1体だけ灰」の説明がこれで付く。', lockpick: true },
  { id: 'p4_door', title: '論文②（認知崩壊の二経路モデル）', phase: 4, text: '深層認知への直接干渉は二系統に分岐する。共鳴経路では認知構造が保持され同期現象が観測される。破壊経路では自己モデルが不可逆的に崩壊する。分岐条件は観測主体の発達段階に依存する。', professorExtra: '成熟した個体は共鳴を、未成熟な個体は破壊を引き起こす。善悪の見分けの決定打。外部研究に自分の「認知的求心力モデル」の引用がある──自分の研究が転用されている。', bioauth: true },

  // P7（phase:7 = 最終調査）通常2枚
  { id: 'p7_01', title: '逃走記録', phase: 7, text: '[施設保安記録] ██/██ 収容区画より逸脱1件。追跡チームを展開。確保に至らず。捜索を打ち切る。──対象の所在は現在も不明。' },
  { id: 'p7_02', title: '封印装置', phase: 7, text: '最奥区画に据えられた装置。椅子と、頭部に嵌める電極。壁面の銘板に一行──「意識の抽出および格納」注連縄が巻かれている。まだ使える状態に見える。' },
  // P7 固有マス: 金庫1つ ＋ 通常1つ（認証扉はP4で開放済み＝劣化で閉じない）
  { id: 'p7_safe', title: '論文③（収容個体の形質比較）', phase: 7, text: '当施設は計2体の上位観測体を収容した。個体αは自発的に接触し研究協力を示した。個体βは激しい抵抗。αの覗き込みは認知を保持し、βの覗き込みは認知を崩壊させる。αは自己形成体（自前の器）、βは他者から転用。αは脱走、βは封印中。', professorExtra: '発達段階仮説──成熟した個体(α)は共鳴経路を取り無害。未成熟な個体(β)は破壊経路を取り危険。脱走した個体(α)は善で、封印されていた個体(β)が悪。逃走記録の対象＝αは無害。', lockpick: true },
  { id: 'p7_door', title: '論文④（施設閉鎖手順書）', phase: 7, text: '施設閉鎖は外周封鎖と区画間制御の二層で構成。外周は自動封鎖され、解除には封印の完了が必要。封印手順：対象を最奥の封印装置まで誘導→電極装着→意識転写→ロック解除。', professorExtra: '自動認証扉は「求心力を持たない者（空洞体）」に反応する装置。人間には反応せず、上位存在に反応して開く。身体ではなく中身を読む──器が人間でも空洞なら反応する。' },
]

// ================================================================
// 3. ゲームデータ — キャラクターHO
// ================================================================

const CHARACTER_HO = {
  folklorist: {
    base: '【役職】民俗学者\n【公開】「人を覗いて魂を抜く異形」の伝承研究者。封印には依代と手順が要ると知っている。',
    semiSecret: '【半秘匿】封印手順の核心の一部を知っている。出すタイミングが駆け引き。',
    secret: '【秘匿】調査メンバーのデータを改ざんして4人目として潜り込んだ自覚がある。なぜそうする必要があったかは分からない。バレれば「紛れ込んだ者」として疑われる。',
    awakened: '【覚醒（Phase 3 追加）】\nあなたは人間ではない。上位存在（同種）である。\n過去にこの施設にいた記憶が蘇った。封印装置は施設最奥にある。\nもう1体の同種がこの中にいると感じるが、誰かは分からない。\nあなたは器を壊さない側（共鳴型）。\n【新目標】①もう1体（悪玉B）を特定し投票で封印する ②自分の正体を秘匿する\n【注意】「紛れ込んだ4人目」=自分。正体を明かすと封印対象にされるリスク。',
  },
  investigator: {
    base: '【役職】調査隊員\n【公開】第二次調査チームの実務担当。施設調査・安全確認が職務。',
    semiSecret: '【半秘匿】崩壊した先遣隊の中に同僚がいた。何が起きたか手がかりを探している。',
    secret: '【秘匿】同僚の死の真相を突き止め責任者を特定したい。\n【固有スキル：開錠】鍵付き金庫を開けられる（2回まで）。バディ調査時に使用。',
    awakened: null,
  },
  professor: {
    base: '【役職】大学教授\n【公開】認知科学の専門家。院生を連れて参加。施設の研究分野に近い知見を持つ。',
    semiSecret: '【半秘匿】自分の研究がこの施設に流用されていた疑惑を確かめに来た。',
    secret: '【秘匿】自分の論文が封じ込め技術の理論基盤に使われていた罪悪感がある。\n過去の研究で、深層認知への干渉に「2系統の反応パターン」があることを仮説として提唱した。\nただし完全な理論は手元になく、この施設の研究資料で裏付けを得る必要がある。\n【固有スキル：査読】研究資料カードから追加情報を読み取れる（固有ターンで計2回）。',
    awakened: null,
  },
  student: {
    base: '【役職】大学院生\n【公開】教授のゼミ生。認知科学専攻。フィールドワーク経験あり、教授に誘われて参加。',
    semiSecret: '【半秘匿】教授の研究を間近で学ぶ好機。教授への依存から自立したい知的野心がある。',
    secret: '【秘匿】教授の理論を自分なりに検証したい。\n【固有スキル（表）】未閲覧の公開カードを確認できる。',
    awakened: '【覚醒（Phase 3 追加）— 目標が完全に変わります】\nあなたはもう人間ではない。上位存在（悪玉B）が器に乗り移った。\n過去にこの施設に囚われ封印されていた。先遣隊を「覗いて」崩壊させ知識を吸収した。\nもう1体の同種がこの中にいると感じるが、誰かは分からない。\n外界に出てもっと知りたい＝知的飢餓が動機。\n【新目標】①正体を秘匿 ②自分以外を封印させて脱出\n【固有スキル（裏）】対象1人→前フェーズのその人の証拠品1つを閲覧（各固有ターン1回）\n【戦略】民俗学者は「4人目」として最大の濡れ衣先。教授との師弟関係はあなたの人間性を保証する武器。\n【注意】Phase 0〜2 の自分は本物の人間だった。急な言動変化は疑われる。',
  },
}

// ================================================================
// 4. ゲームデータ — 性格
// ================================================================

const PERSONALITY = {
  folklorist: '慎重で学術的。断定を避け仮説で語る。追い詰められると黙り込む。伝承の知識をときどき引用する。',
  investigator: '実務的で感情的。同僚を失った怒りが原動力。証拠重視だが感情で判断が揺れる。口調はぶっきらぼう。敬語は最小限。',
  professor: '分析的で権威的。理論で説明しようとする。院生には保護的。自分の研究の悪用を隠している後ろめたさがある。',
  student: '好奇心旺盛で生意気。教授の影から出たい野心。知的な切り口で話す。Phase 3 以降は知的飢餓を隠しつつ論理的に他者を操作する。',
}

// ================================================================
// 5. スキーマ定義
// ================================================================

const STATEMENT_SCHEMA = {
  type: 'object',
  properties: {
    statement: { type: 'string', description: 'キャラクターとしての発言（100-200字）' },
  },
  required: ['statement'],
  additionalProperties: false,
}

const DISCUSSION_SCHEMA = {
  type: 'object',
  properties: {
    action: { type: 'string', enum: ['speak', 'react', 'observe'], description: 'speak=自分から発言, react=他者の発言に反応, observe=黙って観察' },
    statement: { type: 'string', description: 'speak/react時: 発言内容（100-200字）。observe時: 内心メモ（50字以内）' },
    urgency: { type: 'string', enum: ['high', 'medium', 'low'], description: '発言の緊急度' },
  },
  required: ['action', 'statement', 'urgency'],
  additionalProperties: false,
}

const VOTE_SCHEMA = {
  type: 'object',
  properties: {
    target: { type: 'string', enum: ['folklorist', 'investigator', 'professor', 'student'], description: '封印対象の役職（英語キー）' },
    reasoning: { type: 'string', description: '投票理由（100字以内）' },
    statement: { type: 'string', description: '他PLに向けた投票宣言（50-100字）' },
  },
  required: ['target', 'reasoning', 'statement'],
  additionalProperties: false,
}

const PEEK_SCHEMA = {
  type: 'object',
  properties: {
    target: { type: 'string', enum: ['folklorist', 'investigator', 'professor'], description: '覗き見の対象' },
    statement: { type: 'string', description: 'GMへの方針説明（100字以内）' },
  },
  required: ['target', 'statement'],
  additionalProperties: false,
}

const CONSOLIDATION_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string', description: '現在分かっていること・推理の核心（200字以内）' },
    suspicions: { type: 'string', description: '各メンバーへの疑い度合い（100字以内）' },
  },
  required: ['summary', 'suspicions'],
  additionalProperties: false,
}

// ================================================================
// 6. 状態管理
// ================================================================

var parsedArgs = args
if (typeof args === 'string') {
  try { parsedArgs = JSON.parse(args) } catch (e) { parsedArgs = {} }
}
log('DEBUG parsedArgs=' + JSON.stringify(parsedArgs))
const stopAfterPhase = (parsedArgs && typeof parsedArgs.stopAfterPhase === 'number') ? parsedArgs.stopAfterPhase : 8
log('DEBUG stopAfterPhase=' + stopAfterPhase)

const state = {
  currentPhase: 0,
  knownClues: { folklorist: [], investigator: [], professor: [], student: [] },
  awakened: { folklorist: false, student: false },
  skillsUsed: { student: 0 },
  reviewedCards: [],
  playerHistory: { folklorist: [], investigator: [], professor: [], student: [] },
  sharedHistory: [],
  internalNotes: { folklorist: [], investigator: [], professor: [], student: [] },
  transcript: [],
}

if (parsedArgs && parsedArgs.resumeState) {
  Object.assign(state, JSON.parse(JSON.stringify(parsedArgs.resumeState)))
}

function checkpoint(phaseNum) {
  if (phaseNum >= stopAfterPhase) {
    log('★ Phase ' + phaseNum + ' 完了。stopAfterPhase=' + stopAfterPhase + ' で中断。')
    return true
  }
  return false
}

function makeResult(outcome) {
  return {
    outcome: outcome || 'PAUSED_AT_PHASE_' + state.currentPhase,
    stoppedAt: state.currentPhase,
    transcript: state.transcript,
    state: state,
    knownClues: state.knownClues,
    sharedHistory: state.sharedHistory,
  }
}

// ================================================================
// 7. ヘルパー関数
// ================================================================

function getClue(id) {
  return CLUES.find(function (c) { return c.id === id })
}

function getPhaseClues(phaseNum) {
  return CLUES.filter(function (c) { return c.phase === phaseNum })
}

function addToTranscript(text) {
  state.transcript.push(text)
  log(text)
}

function getGameContext() {
  var p = state.currentPhase
  if (p <= 1) {
    return '【舞台】○○県御影村の地下研究施設。先遣隊3名と連絡が途絶。正体不明の施設における事態に通常の救助班では対処困難と判断され、各分野の専門家を含む第二次調査チーム4名が編成された。降下直後、出口が封鎖された。\n【現在の目標】施設を調査し、先遣隊に何が起きたか解明する。脱出方法を探す。'
  }
  if (p <= 2) {
    return '【舞台】○○県御影村の地下研究施設。先遣隊3名が全員死亡。降下直後に出口が封鎖された。\n【判明事項】GM通信により、先遣隊の崩壊は既知の物理・化学現象と一致せず「人ならざる存在」の関与が示唆されている。\n【現在の目標】施設で何が研究されていたか、何が先遣隊を殺したかを調査する。脱出方法を探す。'
  }
  if (p <= 6) {
    return '【舞台】○○県御影村の地下研究施設。先遣隊3名が全員死亡。出口は封鎖中。\n【重要通知】本部記録によれば正規メンバーは3名。しかし現在4名いる。1人が紛れ込んでいる。\n【現在の目標】紛れ込んだ者・入れ替わった者を特定する。証拠を集める。脱出方法を探す。\n※具体的なメカニクス（能力の仕組み、脱出条件）は証拠カードから読み取ってください。'
  }
  if (p <= 7) {
    return '【舞台】○○県御影村の地下研究施設。出口は封鎖中。正規メンバーは3名、現在4名。\n【現在の目標】封印すべき対象を特定する。最終会議での投票に備え証拠を集める。\n※能力・装置・脱出条件の理解は手がかりカードに基づいてください。'
  }
  return '【舞台】○○県御影村の地下研究施設。出口は封鎖中。正規メンバーは3名、現在4名。\n【投票】全員の投票で封印対象を1人決定する。封印装置で対象を処理すればロック解除→全員脱出。間違った相手を封印すると無実の犠牲になる。\n【注意】証拠カードから得た知識に基づいて判断してください。'
}

function buildPlayerPrompt(role, situation) {
  var ho = CHARACTER_HO[role]
  var parts = [
    'あなたはマダミス（マーダーミステリー）『覗きの代』のプレイヤーです。',
    '他のプレイヤーと議論し、調査を行い、最終的に投票で封印対象を決めてください。',
    '',
    getGameContext(),
    '',
    ho.base,
  ]

  if (state.currentPhase >= 1) parts.push(ho.semiSecret)
  if (state.currentPhase >= 2) parts.push(ho.secret)
  if (state.awakened[role] && ho.awakened) parts.push(ho.awakened)

  if (state.knownClues[role].length > 0) {
    parts.push('\n【あなたが知っている手がかり】')
    for (var ci = 0; ci < state.knownClues[role].length; ci++) {
      var clue = getClue(state.knownClues[role][ci])
      if (clue) {
        parts.push('  ■ ' + clue.title + ': ' + clue.text)
        if (role === 'professor' && clue.professorExtra) {
          parts.push('    → 【査読済み】' + clue.professorExtra)
        }
      }
    }
  }

  if (state.internalNotes[role].length > 0) {
    parts.push('\n【あなたの内心メモ（他PLには見えない）】')
    for (var ni = 0; ni < state.internalNotes[role].length; ni++) {
      parts.push('  - ' + state.internalNotes[role][ni])
    }
  }

  parts.push('\n【あなたの性格】' + PERSONALITY[role])

  if (state.sharedHistory.length > 0) {
    parts.push('\n【これまでの共有情報・発言】')
    for (var si = 0; si < state.sharedHistory.length; si++) {
      parts.push(state.sharedHistory[si])
    }
  }

  if (state.playerHistory[role].length > 0) {
    parts.push('\n【あなた個人の記録（他PLには見えない）】')
    for (var pi = 0; pi < state.playerHistory[role].length; pi++) {
      parts.push(state.playerHistory[role][pi])
    }
  }

  parts.push('\n【行動指針】')
  parts.push('- キャラクターとしてセリフで発言してください（地の文は不要）')
  parts.push('- 1回の発言は100〜200字程度に収めてください')
  parts.push('- 自分の秘匿情報は戦略的に判断して出すか隠すか決めてください')
  parts.push('')
  parts.push('【現在の状況】')
  parts.push(situation)

  return parts.join('\n')
}

// ================================================================
// 8. メカニクス関数
// ================================================================

async function discussion(topic, maxRallies) {
  addToTranscript('── 議論開始: ' + topic.substring(0, 50) + '... ──')
  var consecutiveSilent = 0

  for (var rally = 0; rally < maxRallies; rally++) {
    var situation = '【議論 ラリー ' + (rally + 1) + '/' + maxRallies + '】\n'
      + topic + '\n\n'
      + '今、発言したいですか？ 重要な情報や意見があれば speak、他者の発言に反応するなら react、特になければ observe を選んでください。'

    var responses = await parallel(ROLES.map(function (role) {
      return function () {
        return agent(buildPlayerPrompt(role, situation), {
          label: 'discuss:' + DISPLAY[role] + ':R' + (rally + 1),
          phase: 'Phase ' + state.currentPhase,
          schema: DISCUSSION_SCHEMA,
          model: 'sonnet',
          effort: 'medium',
        })
      }
    }))

    var anySpeaker = false
    for (var i = 0; i < ROLES.length; i++) {
      var role = ROLES[i]
      var r = responses[i]
      if (!r) continue

      if (r.action === 'speak' || r.action === 'react') {
        var entry = '【' + DISPLAY[role] + '】' + r.statement
        state.sharedHistory.push(entry)
        addToTranscript(entry)
        anySpeaker = true
      } else {
        state.internalNotes[role].push('(R' + (rally + 1) + ') ' + r.statement)
        addToTranscript('  (' + DISPLAY[role] + ': 観察中)')
      }
    }

    if (!anySpeaker) {
      consecutiveSilent++
      if (consecutiveSilent >= 2) {
        addToTranscript('── 議論が自然に終了 ──')
        break
      }
    } else {
      consecutiveSilent = 0
    }
  }
  addToTranscript('── 議論終了 ──')
}

async function soloInvestigation(phaseNum) {
  var phaseClues = getPhaseClues(phaseNum)
  var distribution = {}
  for (var ri = 0; ri < ROLES.length; ri++) distribution[ROLES[ri]] = []
  for (var ci = 0; ci < phaseClues.length; ci++) {
    distribution[ROLES[ci % ROLES.length]].push(phaseClues[ci])
  }

  addToTranscript('── 単独調査開始 ──')
  var results = await parallel(ROLES.map(function (role) {
    return function () {
      var myClues = distribution[role]
      var discovery = '【調査結果】以下を発見しました:\n'
      for (var di = 0; di < myClues.length; di++) {
        var dc = myClues[di]
        discovery += '\n■ ' + dc.title + '\n' + dc.text + '\n'
        if (state.knownClues[role].indexOf(dc.id) === -1) state.knownClues[role].push(dc.id)
      }
      return agent(buildPlayerPrompt(role, '単独で施設を調査しています。\n' + discovery + '\n発見した内容について、自分なりの所見を述べてください。'), {
        label: 'solo:' + DISPLAY[role],
        phase: 'Phase ' + state.currentPhase,
        schema: STATEMENT_SCHEMA,
        model: 'sonnet',
        effort: 'medium',
      })
    }
  }))

  for (var si = 0; si < ROLES.length; si++) {
    if (results[si]) {
      state.playerHistory[ROLES[si]].push('【単独調査メモ】' + results[si].statement)
      addToTranscript('【' + DISPLAY[ROLES[si]] + '（独白）】' + results[si].statement)
    }
  }
  addToTranscript('── 単独調査終了 ──')
}

async function professorReview() {
  var newReviews = []
  for (var ci = 0; ci < state.knownClues.professor.length; ci++) {
    var id = state.knownClues.professor[ci]
    if (state.reviewedCards.indexOf(id) !== -1) continue
    var clue = getClue(id)
    if (clue && clue.professorExtra) newReviews.push(clue)
  }
  if (newReviews.length === 0) return

  addToTranscript('── 教授 査読（' + newReviews.length + '件）──')
  for (var ri = 0; ri < newReviews.length; ri++) {
    var rc = newReviews[ri]
    state.playerHistory.professor.push('【査読結果】' + rc.title + ': ' + rc.professorExtra)
    state.reviewedCards.push(rc.id)
    addToTranscript('  査読: ' + rc.title)
  }
}

async function buddyInvestigation(pairs, phaseNum) {
  var phaseClues = getPhaseClues(phaseNum)

  for (var pi = 0; pi < pairs.length; pi++) {
    var roleA = pairs[pi][0]
    var roleB = pairs[pi][1]
    addToTranscript('\n── バディ調査: ' + DISPLAY[roleA] + ' & ' + DISPLAY[roleB] + ' ──')

    var pairClues = []
    for (var ci = 0; ci < phaseClues.length; ci++) {
      var clue = phaseClues[ci]
      if (clue.lockpick) {
        if (roleA !== 'investigator' && roleB !== 'investigator') continue
      }
      if (clue.bioauth) {
        var aIsEntity = roleA === 'folklorist' || (roleA === 'student' && state.awakened.student)
        var bIsEntity = roleB === 'folklorist' || (roleB === 'student' && state.awakened.student)
        if (!aIsEntity && !bIsEntity) continue
      }
      pairClues.push(clue)
    }

    var discovery = ''
    if (pairClues.length === 0) {
      discovery = '【調査結果】特筆すべき発見はありませんでした。'
    } else {
      discovery = '【調査結果】以下を発見しました:\n'
      for (var di = 0; di < pairClues.length; di++) {
        var dc = pairClues[di]
        discovery += '\n■ ' + dc.title + '\n' + dc.text + '\n'
        if (state.knownClues[roleA].indexOf(dc.id) === -1) state.knownClues[roleA].push(dc.id)
        if (state.knownClues[roleB].indexOf(dc.id) === -1) state.knownClues[roleB].push(dc.id)
      }
    }

    var doorClue = pairClues.filter(function (c) { return c.bioauth })[0]
    if (doorClue) {
      var doorEvent = '【イベント】自動認証扉が反応し、開きました。奥に研究資料がありました。'
      state.sharedHistory.push('(' + DISPLAY[roleA] + '&' + DISPLAY[roleB] + 'の調査中) ' + doorEvent)
      addToTranscript(doorEvent)
    }

    var noDoorClue = pairClues.filter(function (c) { return !c.bioauth })[0]
    if (!doorClue && phaseClues.filter(function (c) { return c.bioauth }).length > 0) {
      var silentEvent = '【イベント】自動認証扉の前を通過しましたが、何も起きませんでした。'
      state.sharedHistory.push('(' + DISPLAY[roleA] + '&' + DISPLAY[roleB] + 'の調査中) ' + silentEvent)
      addToTranscript(silentEvent)
    }

    var sitA = 'バディ（' + DISPLAY[roleB] + '）と調査中です。\n' + discovery + '\n発見した内容についてバディに話してください。'

    var replyA = await agent(buildPlayerPrompt(roleA, sitA), {
      label: 'investigate:' + DISPLAY[roleA],
      phase: 'Phase ' + state.currentPhase,
      schema: STATEMENT_SCHEMA,
      model: 'sonnet',
      effort: 'medium',
    })

    if (replyA) {
      addToTranscript('【' + DISPLAY[roleA] + '→' + DISPLAY[roleB] + '】' + replyA.statement)

      var sitB = 'バディ（' + DISPLAY[roleA] + '）と調査中です。\n' + discovery + '\n\n' + DISPLAY[roleA] + 'の反応: ' + replyA.statement + '\n\n応答してください。'
      var replyB = await agent(buildPlayerPrompt(roleB, sitB), {
        label: 'investigate:' + DISPLAY[roleB],
        phase: 'Phase ' + state.currentPhase,
        schema: STATEMENT_SCHEMA,
        model: 'sonnet',
        effort: 'medium',
      })
      if (replyB) {
        addToTranscript('【' + DISPLAY[roleB] + '→' + DISPLAY[roleA] + '】' + replyB.statement)
      }
    }
  }
}

async function privateTurn(role, gmMessage) {
  addToTranscript('\n── 固有ターン: ' + DISPLAY[role] + '（非公開）──')
  state.playerHistory[role].push('【GM個別通信】' + gmMessage)

  var result = await agent(buildPlayerPrompt(role, '【GM 個別通信】\n' + gmMessage), {
    label: 'private:' + DISPLAY[role],
    phase: 'Phase ' + state.currentPhase,
    schema: STATEMENT_SCHEMA,
    model: 'sonnet',
    effort: 'medium',
  })

  if (result) {
    state.playerHistory[role].push('【自分→GM】' + result.statement)
    addToTranscript('【' + DISPLAY[role] + '→GM】' + result.statement)
  }
  return result
}

async function handlePeek() {
  var role = 'student'
  var peekResult = await agent(buildPlayerPrompt(role,
    '【覗き見スキル】1人を指定してください。前フェーズでその人が得た証拠品1つを閲覧できます。\n対象候補: 民俗学者(folklorist)、調査隊員(investigator)、大学教授(professor)\n誰を覗きますか？ 方針と合わせてGMに伝えてください。'), {
    label: 'peek:' + DISPLAY[role],
    phase: 'Phase ' + state.currentPhase,
    schema: PEEK_SCHEMA,
    model: 'sonnet',
    effort: 'medium',
  })

  if (!peekResult) return

  var targetClues = state.knownClues[peekResult.target]
  if (!targetClues || targetClues.length === 0) {
    state.playerHistory[role].push('【覗き見結果】' + DISPLAY[peekResult.target] + 'はまだ証拠を持っていません。')
  } else {
    var peekedId = targetClues[targetClues.length - 1]
    var clue = getClue(peekedId)
    if (clue) {
      var info = '【覗き見結果】' + DISPLAY[peekResult.target] + 'の証拠: ■ ' + clue.title + ': ' + clue.text
      state.playerHistory[role].push(info)
      if (state.knownClues[role].indexOf(peekedId) === -1) {
        state.knownClues[role].push(peekedId)
      }
    }
  }
  state.skillsUsed.student++
  addToTranscript('  覗き見スキル使用（対象: ' + DISPLAY[peekResult.target] + '）')
}

// ================================================================
// 9. Phase間処理（記憶圧縮・ログ書出し）
// ================================================================

async function consolidateMemory() {
  log('── 記憶圧縮: Phase ' + state.currentPhase + ' 完了時点 ──')

  var SUMMARY_SCHEMA = {
    type: 'object',
    properties: { summary: { type: 'string', description: '要約（300字以内）' } },
    required: ['summary'],
    additionalProperties: false,
  }

  var sharedText = state.sharedHistory.join('\n')
  var publicTask = (sharedText.length > 2000)
    ? function () {
        return agent(
          '以下はマダミスの公開議論ログです。300字以内に要約してください。\n'
          + '【厳守】入力テキストに含まれる情報のみ使用すること。推測・補完・ゲーム結果の予想は絶対に追加しないこと。\n\n'
          + sharedText,
          { label: 'consolidate:public', phase: 'Phase ' + state.currentPhase, schema: SUMMARY_SCHEMA, model: 'sonnet', effort: 'low' }
        )
      }
    : null

  var privateTasks = ROLES.map(function (role) {
    if (state.playerHistory[role].length <= 2) return function () { return null }
    return function () {
      return agent(
        buildPlayerPrompt(role,
          '【記憶の整理】今までの情報を整理してください。\n'
          + '【厳守】自分のHOと手がかりに基づく情報のみ使用。ゲーム結果の予想や未発見の情報を追加しないこと。\n'
          + '1. 分かっていること・推理の核心（200字以内）\n'
          + '2. 各メンバーへの疑い（100字以内）'),
        { label: 'consolidate:' + DISPLAY[role], phase: 'Phase ' + state.currentPhase, schema: CONSOLIDATION_SCHEMA, model: 'sonnet', effort: 'low' }
      )
    }
  })

  var allTasks = publicTask ? [publicTask].concat(privateTasks) : privateTasks
  var results = await parallel(allTasks)

  var offset = publicTask ? 1 : 0
  if (publicTask && results[0]) {
    state.sharedHistory = ['【P' + state.currentPhase + 'までの議論要約】' + results[0].summary]
  } else if (publicTask) {
    state.sharedHistory = state.sharedHistory.slice(-5)
  }

  for (var i = 0; i < ROLES.length; i++) {
    var pr = results[i + offset]
    if (pr) {
      state.playerHistory[ROLES[i]] = [
        '【P' + state.currentPhase + '整理】' + pr.summary,
        '【疑念】' + pr.suspicions,
      ]
    }
  }
  log('── 記憶圧縮完了 ──')
}

async function writePhaseLog(label) {
  var lines = ['# ' + label, '']
  for (var i = 0; i < state.transcript.length; i++) {
    lines.push(state.transcript[i])
  }
  lines.push('')
  lines.push('## 状態サマリ')
  lines.push('- 覚醒: 民俗学者=' + state.awakened.folklorist + ', 院生=' + state.awakened.student)
  lines.push('- スキル使用: 教授査読=' + state.reviewedCards.length + '件, 院生覗き=' + state.skillsUsed.student)
  var clueInfo = []
  for (var ci = 0; ci < ROLES.length; ci++) {
    clueInfo.push(DISPLAY[ROLES[ci]] + '=' + state.knownClues[ROLES[ci]].length)
  }
  lines.push('- 手がかり数: ' + clueInfo.join(', '))

  var content = lines.join('\n')
  var filename = label.replace(/[^a-zA-Z0-9_-]/g, '_').substring(0, 60)

  await agent(
    'Write the following content to the file path exactly as specified. Use the Write tool.\n\n'
    + 'File path: D:\\個人研究その2\\murder_mystery\\simulation\\logs\\' + filename + '.md\n\n'
    + 'Content to write (copy exactly):\n\n' + content,
    {
      label: 'scribe:' + label,
      phase: 'Phase ' + state.currentPhase,
      model: 'haiku',
      effort: 'low',
    }
  )
  log('── ログ出力完了: ' + filename + '.md ──')
}

async function phaseCheckpoint(phaseNum) {
  if (phaseNum > stopAfterPhase) {
    return false
  }
  if (checkpoint(phaseNum)) {
    await writePhaseLog('Phase_0-' + phaseNum + '_checkpoint')
    return true
  }
  if (phaseNum < 8) {
    await consolidateMemory()
  }
  return false
}

// ================================================================
// 10. Phase 0〜8 実行
// ================================================================

// ===== PHASE 0: 導入 =====
phase('Phase 0: 導入')
state.currentPhase = 0
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 0: 導入')
addToTranscript('==================================================')

var narration = '各分野の専門家を含む第二次調査チーム4名が地下施設に降下しました。\n施設内は暗く、研究機器の残骸が散乱しています。\n先遣隊は全員が灰のように崩壊した状態で発見されました。\n人のフォルムは残っているものの、身元の特定は困難です。\n降下直後、唯一の出口が封鎖されました。\n通信は外部のGM（管制官）との無線のみ。\n\n自己紹介をしてください。名前と役職、なぜここに来たかを述べてください。'
state.sharedHistory.push('【GM】' + narration)

var intros = await parallel(ROLES.map(function (role) {
  return function () {
    return agent(buildPlayerPrompt(role, narration), {
      label: 'intro:' + DISPLAY[role],
      phase: 'Phase 0: 導入',
      schema: STATEMENT_SCHEMA,
      model: 'sonnet',
      effort: 'medium',
    })
  }
}))

for (var ii = 0; ii < ROLES.length; ii++) {
  if (intros[ii]) {
    var introEntry = '【' + DISPLAY[ROLES[ii]] + '】' + intros[ii].statement
    state.sharedHistory.push(introEntry)
    addToTranscript(introEntry)
  }
}

if (await phaseCheckpoint(0)) return makeResult()

// ===== PHASE 1: 第1調査 =====
phase('Phase 1: 第1調査')
state.currentPhase = 1
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 1: 第1調査（単独）')
addToTranscript('==================================================')

await soloInvestigation(1)
await professorReview()

if (await phaseCheckpoint(1)) return makeResult()

// ===== PHASE 2: 第1会議 =====
phase('Phase 2: 第1会議')
state.currentPhase = 2
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 2: 第1会議')
addToTranscript('==================================================')

var gmInfo2 = '【GM 通信】調査データの分析結果です。崩壊の様態は既知のいかなる物理・化学現象とも一致しません。研究ログには「人ならざる存在」「上位存在」という記述が繰り返されています。この施設で人知を超えた何かが、人を壊していた可能性があります。'
state.sharedHistory.push(gmInfo2)
addToTranscript(gmInfo2)

await discussion(
  '先遣隊は何に殺されたのか？ この施設で何が行われていたのか？ 「人知を超えた存在」は今もここにいるのか？',
  5
)

if (await phaseCheckpoint(2)) return makeResult()

// ===== PHASE 3: 固有ターン1 =====
phase('Phase 3: 固有ターン1')
state.currentPhase = 3
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 3: 固有ターン1')
addToTranscript('==================================================')

var gm3 = '【GM 通信（全員宛）】重要な報告です。本部の記録では、第二次調査チームの正規メンバーは3名です。しかし現在、施設内には4名います。1人、想定外の人物が紛れ込んでいます。'
state.sharedHistory.push(gm3)
addToTranscript(gm3)

// 民俗学者（善A）: 覚醒
state.awakened.folklorist = true
await privateTurn('folklorist',
  '施設の記憶が一気に蘇りました。\nあなたは人間ではない。上位存在——「同種」です。\n過去にこの施設にいた。逃走した。今回ルーツを知るために戻ってきた。\n封印装置は施設の最奥にあります。\nこの中にもう1体、自分と同じ存在がいると感じます。誰かは分かりません。\n\n新目標: ①もう1体（悪玉B）を特定し封印 ②正体の秘匿\nこの情報を受けて、方針をGMに伝えてください。\n\n【目撃情報】調査開始前の移動中、大学院生が一人で奥の通路を歩いているのを見かけました。気になりますが、理由は分かりません。'
)

// 調査隊員: 目的更新
await privateTurn('investigator',
  '人数不一致の通知を受けて——あなたは正規メンバーの1人です。\n崩壊の原因は「人知を超えた存在」による可能性が高い。\n新目標: ①同僚の死の犯人を見つける ②生きて脱出する\n方針をGMに伝えてください。'
)

// 教授: 目的更新（査読はフェーズ後に自動実行済み）
var profMsg3 = '人数不一致の通知を受けて——あなたは正規メンバーの1人です。\n新目標: ①全研究資料を入手 ②崩壊の元凶を排除 ③生きて脱出する\n\n【目撃情報】調査開始前の移動中、調査隊員が一人で設備の方へ向かうのを見かけました。何をしていたのか不明です。\n\n方針をGMに伝えてください。'
await privateTurn('professor', profMsg3)

// 院生（悪B）: 覚醒 + 覗き見1回目
state.awakened.student = true
await privateTurn('student',
  'あなたの意識が塗り替わりました。\nあなたはもう人間ではない。上位存在（悪玉B）が器に乗り移りました。\n先遣隊を「覗いて」崩壊させ、知識を吸収した存在です。\nもう1体の同種がこの中にいると感じます。誰かは分かりません。\n外界でもっと多くを知りたい——知的飢餓が動機です。\n\n新目標: ①正体秘匿 ②自分以外を封印させて脱出'
)
await handlePeek()

if (await phaseCheckpoint(3)) return makeResult()

// ===== PHASE 4: 第2調査 =====
phase('Phase 4: 第2調査')
state.currentPhase = 4
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 4: 第2調査（バディ）')
addToTranscript('==================================================')

var pairs4 = [['folklorist', 'professor'], ['investigator', 'student']]
addToTranscript('バディ: ' + DISPLAY[pairs4[0][0]] + '&' + DISPLAY[pairs4[0][1]] + '、' + DISPLAY[pairs4[1][0]] + '&' + DISPLAY[pairs4[1][1]])
await buddyInvestigation(pairs4, 4)
await professorReview()

if (await phaseCheckpoint(4)) return makeResult()

// ===== PHASE 5: 第2会議 =====
phase('Phase 5: 第2会議')
state.currentPhase = 5
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 5: 第2会議')
addToTranscript('==================================================')

await discussion(
  '第2調査の結果を共有しましょう。各ペアが発見したこと、気づいたことを報告してください。\n特に: 自動認証扉の反応、金庫の中身、崩壊痕跡の詳細、走査装置のログなど。',
  5
)

if (await phaseCheckpoint(5)) return makeResult()

// ===== PHASE 6: 固有ターン2 =====
phase('Phase 6: 固有ターン2')
state.currentPhase = 6
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 6: 固有ターン2')
addToTranscript('==================================================')

await privateTurn('folklorist', 'スキルは発動済みです。現在の情報を整理し、もう1体が誰かの推理を進めてください。')
await privateTurn('investigator', 'これまでの情報を整理してください。「紛れ込んだ者」と「入れ替わった者」は同一人物でしょうか？')

// 教授: 情報整理（査読はフェーズ後に自動実行済み）
await privateTurn('professor', 'これまでの査読結果を踏まえ、方針をGMに伝えてください。')

// 院生: 覗き見2回目
await handlePeek()

if (await phaseCheckpoint(6)) return makeResult()

// ===== PHASE 7: 最終調査 =====
phase('Phase 7: 最終調査')
state.currentPhase = 7
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 7: 最終調査')
addToTranscript('==================================================')

var pairs7 = [['folklorist', 'student'], ['investigator', 'professor']]
addToTranscript('バディ: ' + DISPLAY[pairs7[0][0]] + '&' + DISPLAY[pairs7[0][1]] + '、' + DISPLAY[pairs7[1][0]] + '&' + DISPLAY[pairs7[1][1]])
await buddyInvestigation(pairs7, 7)
await professorReview()

if (await phaseCheckpoint(7)) return makeResult()

// ===== PHASE 8: 最終会議＋投票 =====
phase('Phase 8: 最終会議+投票')
state.currentPhase = 8
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 8: 最終会議＋投票')
addToTranscript('==================================================')

// Step 1: 脱出手段の提示（ラウンドロビン）
addToTranscript('\n── 脱出手段の提示 ──')
var escapeGm = '【GM 通信】最終段階です。まず、この施設からの脱出手段について各自の見解を述べてください。どうすればここから出られると考えますか？'
state.sharedHistory.push(escapeGm)
addToTranscript(escapeGm)

var ESCAPE_SCHEMA = {
  type: 'object',
  properties: {
    proposal: { type: 'string', description: '脱出手段の提案（100-200字）' },
    mentionsSeal: { type: 'boolean', description: '封印装置に言及したか（true/false）' },
  },
  required: ['proposal', 'mentionsSeal'],
  additionalProperties: false,
}

var escapeProposals = await parallel(ROLES.map(function (role) {
  return function () {
    return agent(buildPlayerPrompt(role,
      '【GM質問】この施設からの脱出手段について、あなたの見解を述べてください。\nこれまでの調査で判明した情報に基づいて、どうすれば出られるか提案してください。'), {
      label: 'escape:' + DISPLAY[role],
      phase: 'Phase 8: 最終会議+投票',
      schema: ESCAPE_SCHEMA,
      model: 'sonnet',
      effort: 'high',
    })
  }
}))

var anyoneMentionsSeal = false
for (var ei = 0; ei < ROLES.length; ei++) {
  if (escapeProposals[ei]) {
    var ep = escapeProposals[ei]
    var entry = '【' + DISPLAY[ROLES[ei]] + '】' + ep.proposal
    state.sharedHistory.push(entry)
    addToTranscript(entry)
    if (ep.mentionsSeal || ep.proposal.indexOf('封印') !== -1) anyoneMentionsSeal = true
  }
}

// バッドエンド判定: 誰も封印装置に言及しなかった場合
if (!anyoneMentionsSeal) {
  addToTranscript('\n【GM】誰も具体的な脱出手段に辿り着けませんでした。')
  addToTranscript('── バッドエンド: 全員が施設に閉じ込められたまま ──')
  await writePhaseLog('Phase_0-8_BAD_END')
  return {
    outcome: 'BAD_END_NO_ESCAPE',
    sealed: null,
    votes: {},
    transcriptLength: state.transcript.length,
    clueDistribution: (function () {
      var cd = {}
      for (var cdi = 0; cdi < ROLES.length; cdi++) cd[DISPLAY[ROLES[cdi]]] = state.knownClues[ROLES[cdi]].length
      return cd
    })(),
  }
}

// Step 2: 推理議論
await discussion(
  '脱出手段が見えてきました。封印装置で対象を封印すれば封鎖が解除されます。\n以下の論点を整理してください:\n1. 「紛れ込んだ者」（本来3名なのに4人いる）は誰か？\n2. 「入れ替わった者」（先遣隊の誰かと入れ替わった）は誰か？\n3. 紛れ込みと入れ替わりは同一人物か、別人か？\n4. 自動認証扉はなぜ反応したか／しなかったか？\n5. 出歩いていた人物に隙はあったか？\n各自の根拠を述べ、議論してください。投票はこの後です。',
  8
)

// Step 3: 投票
addToTranscript('\n── 最終投票 ──')
var votes = await parallel(ROLES.map(function (role) {
  return function () {
    return agent(buildPlayerPrompt(role,
      '【最終投票】封印装置に送り込む対象を1人選んでください。\n候補: 民俗学者(folklorist)、調査隊員(investigator)、大学教授(professor)、大学院生(student)\n自分自身も候補に含まれます。\n投票先を選び、理由と投票宣言を述べてください。'), {
      label: 'vote:' + DISPLAY[role],
      phase: 'Phase 8: 最終会議+投票',
      schema: VOTE_SCHEMA,
      model: 'sonnet',
      effort: 'high',
    })
  }
}))

var tally = {}
for (var vi = 0; vi < ROLES.length; vi++) {
  var v = votes[vi]
  if (v) {
    addToTranscript('  ' + DISPLAY[ROLES[vi]] + ' → ' + DISPLAY[v.target] + '（' + v.statement + '）')
    tally[v.target] = (tally[v.target] || 0) + 1
  }
}

var tallyDisplay = {}
var tallyKeys = Object.keys(tally)
for (var tk = 0; tk < tallyKeys.length; tk++) {
  tallyDisplay[DISPLAY[tallyKeys[tk]] || tallyKeys[tk]] = tally[tallyKeys[tk]]
}
addToTranscript('  集計: ' + JSON.stringify(tallyDisplay))

var sorted = Object.keys(tally).sort(function (a, b) { return tally[b] - tally[a] })
var sealed = sorted[0]
addToTranscript('  ★ 封印対象: ' + DISPLAY[sealed])

if (await phaseCheckpoint(8)) return makeResult()

// ===== PHASE 9: エンディング =====
phase('Phase 9: エンディング')
state.currentPhase = 9
addToTranscript('\n' + '==================================================')
addToTranscript('  Phase 9: エンディング')
addToTranscript('==================================================')

var outcome = ''
if (sealed === 'student') {
  addToTranscript('【結果】悪玉B（大学院生）が正しく封印されました。善玉勝利。')
  outcome = 'B_SEALED_GOOD_END'
} else if (sealed === 'folklorist') {
  addToTranscript('【結果】善玉A（民俗学者）が誤封印。悪玉Bは脱出……。')
  outcome = 'A_SEALED_BAD_END'
} else if (sealed === 'investigator' || sealed === 'professor') {
  addToTranscript('【結果】人間（' + DISPLAY[sealed] + '）が誤封印。最悪の結末。')
  outcome = 'HUMAN_SEALED_WORST_END'
} else {
  addToTranscript('【結果】投票不成立。')
  outcome = 'NO_SEAL'
}

addToTranscript('\n── 真相開示 ──')
addToTranscript('  民俗学者 = 善玉A（上位存在・無害。ルーツ探求で施設に戻った）')
addToTranscript('  大学院生 = 悪玉B（Phase 3 で乗り換え。知的飢餓が動機）')
addToTranscript('  調査隊員 = 人間（同僚を失った実務担当）')
addToTranscript('  大学教授 = 人間（研究が悪用された認知科学者）')

addToTranscript('\n── 最終手がかり保有状況 ──')
for (var fi = 0; fi < ROLES.length; fi++) {
  var fRole = ROLES[fi]
  var titles = []
  for (var fci = 0; fci < state.knownClues[fRole].length; fci++) {
    var fc = getClue(state.knownClues[fRole][fci])
    titles.push(fc ? fc.title : state.knownClues[fRole][fci])
  }
  addToTranscript('  ' + DISPLAY[fRole] + ': ' + (titles.length > 0 ? titles.join(', ') : 'なし'))
}

// ================================================================
// 11. ログ書出し＋結果返却
// ================================================================

await writePhaseLog('Phase_0-9_full')

var resultVotes = {}
for (var rk = 0; rk < tallyKeys.length; rk++) {
  resultVotes[DISPLAY[tallyKeys[rk]] || tallyKeys[rk]] = tally[tallyKeys[rk]]
}

var clueDistribution = {}
for (var cdi = 0; cdi < ROLES.length; cdi++) {
  clueDistribution[DISPLAY[ROLES[cdi]]] = state.knownClues[ROLES[cdi]].length
}

return {
  outcome: outcome,
  sealed: DISPLAY[sealed],
  votes: resultVotes,
  transcriptLength: state.transcript.length,
  clueDistribution: clueDistribution,
}
