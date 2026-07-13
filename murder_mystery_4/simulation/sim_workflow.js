export const meta = {
  name: 'cyberpunk-madamis4-sim',
  description: 'マダミス4（仮題・サイバーパンク） マダミスシミュレーション（4PL×GM）',
  phases: [
    // Phase構成に合わせて編集する
    { title: 'Phase 0: 導入', model: 'sonnet' },
    { title: 'Phase 1: {{種別}}', model: 'sonnet' },
    { title: 'Phase 2: {{種別}}', model: 'sonnet' },
    // ... Phase数に応じて追加
    { title: 'Phase N: エンディング' },
  ],
}

// ================================================================
// 1. 定数
// ================================================================

// キャラクターID（英語キー）とPC数に応じて定義
const ROLES = ['pc1', 'pc2', 'pc3', 'pc4']

const DISPLAY = {
  pc1: '{{PC1表示名}}',
  pc2: '{{PC2表示名}}',
  pc3: '{{PC3表示名}}',
  pc4: '{{PC4表示名}}',
}

// ================================================================
// 2. ゲームデータ — 手がかり
// ================================================================

// 証拠カードデータ: 05_clues.md から転記
const CLUES = [
  // Phase別に列挙
  // { id: 'p1_01', title: '...', phase: 1, text: '...' },
]

// ================================================================
// 3. ゲームデータ — キャラクターHO
// ================================================================

// 04_characters/ から転記。公開層・秘匿層・深層
const CHARACTER_HO = {
  // pc1: { base: '...', semiSecret: '...', secret: '...', awakened: null },
}

// ================================================================
// 4. ヘルパー関数
// ================================================================

function cluesForPhase(p) {
  return CLUES.filter(c => c.phase === p)
}

function clueText(clue) {
  return `【${clue.title}】${clue.text}`
}

function hoText(role, includeSecret, includeAwakened) {
  const ho = CHARACTER_HO[role]
  let text = ho.base
  if (includeSecret && ho.semiSecret) text += '\n' + ho.semiSecret
  if (includeSecret && ho.secret) text += '\n' + ho.secret
  if (includeAwakened && ho.awakened) text += '\n' + ho.awakened
  return text
}

// ================================================================
// 5. GMエージェント
// ================================================================

// GM: 進行管理・情報開示・NPC演出
async function gmAgent(phaseTitle, instruction, context) {
  return await agent(
    `あなたはマダミス「マダミス4（仮題・サイバーパンク）」のGMです。\n\n` +
    `【現在のPhase】${phaseTitle}\n` +
    `【GM指示】${instruction}\n` +
    `【コンテキスト】${context}`,
    { label: `GM:${phaseTitle}`, phase: phaseTitle, model: 'sonnet' }
  )
}

// ================================================================
// 6. PLエージェント
// ================================================================

// PL: キャラクターとしてロールプレイ + 推理
async function plAgent(role, phaseTitle, situation, memory) {
  return await agent(
    `あなたはマダミス「マダミス4（仮題・サイバーパンク）」のプレイヤーです。\n` +
    `【あなたの役職】${DISPLAY[role]}\n` +
    `【あなたの情報】${memory}\n` +
    `【現在の状況】${situation}\n\n` +
    `キャラクターとしてロールプレイしつつ、推理を進めてください。\n` +
    `行動を選択し、発言内容を出力してください。`,
    { label: `PL:${DISPLAY[role]}`, phase: phaseTitle, model: 'sonnet' }
  )
}

// ================================================================
// 7. メインフロー
// ================================================================

// -- Phase 0: 導入 --
phase('Phase 0: 導入')
log('Phase 0 開始: プロローグ読み上げ＋HO配布')

// GMがプロローグを読み上げ
const prologue = await gmAgent('Phase 0', 'プロローグを読み上げてください', '')

// 各PLに初期HOを配布し、自己紹介
const introductions = await parallel(
  ROLES.map(role => () =>
    plAgent(role, 'Phase 0', prologue, hoText(role, true, false))
  )
)

// PLの記憶を初期化
const plMemory = {}
ROLES.forEach((role, i) => {
  plMemory[role] = hoText(role, true, false) + '\n\n【自己紹介ラウンド】\n' +
    introductions.filter(Boolean).map((intro, j) => `${DISPLAY[ROLES[j]]}: ${intro}`).join('\n')
})

log('Phase 0 完了')

// -- 以降のPhaseは 00_concept.md のPhase構成に合わせて実装 --
// テンプレートとして Phase 1（調査）と Phase 2（会議）のパターンを示す

// -- Phase 1: 調査 --
// phase('Phase 1: {{種別}}')
// log('Phase 1 開始')
// const p1Clues = cluesForPhase(1)
// ... 調査ロジック（バディ制 / 自由探索 etc.）を実装
// ... 証拠カードの発見処理
// ... PLの記憶に追加

// -- Phase 2: 会議 --
// phase('Phase 2: {{種別}}')
// log('Phase 2 開始')
// ... 議論ラウンド（PLエージェント並列発言 → 集約 → 次ラウンド）
// ... GMの進行管理

// -- 最終Phase: 投票＋ED --
// phase('Phase N: エンディング')
// ... 投票処理
// ... ED分岐判定
// ... 結果出力

log('シミュレーション完了')
