"""
覗きの代 シミュレーションエンジン
============================================

マダミス『覗きの代』のゲームプレイを、4体の独立した LLM エージェントで
シミュレーションする。各エージェントは自身の HO（ハンドアウト）のみを持ち、
GM（本スクリプト）がフェーズ進行と情報流通を管理する。

アーキテクチャ:
  PL = Anthropic Messages API の独立した会話コンテキスト
      （system prompt に HO を格納、messages リストを個別管理）
  GM = 本スクリプト（状態管理・フェーズ進行・情報配信）
  コンテキスト分離 = system prompt + messages が PL ごとに完全独立

前提:
  環境変数 ANTHROPIC_API_KEY を設定
  Python 3.10+

使い方:
  python simulate.py [--model MODEL] [--discussion-rounds N] [--output-dir DIR]

コスト目安（Sonnet, 2ラウンド議論）:
  約 60-80 API 呼び出し、入力平均 2-3k tokens → 合計 $0.5-1.0 程度
"""

from __future__ import annotations

import anthropic
import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# ================================================================
# 1. 定数・型定義
# ================================================================

ROLES = ("folklorist", "investigator", "professor", "student")

DISPLAY = {
    "folklorist": "民俗学者",
    "investigator": "調査隊員",
    "professor": "大学教授",
    "student": "大学院生",
}

PHASE_NAMES = {
    0: "Phase 0: 導入",
    1: "Phase 1: 第1調査（バディ）",
    2: "Phase 2: 第1会議",
    3: "Phase 3: 固有ターン1",
    4: "Phase 4: 第2調査（バディ）",
    5: "Phase 5: 固有ターン2",
    6: "Phase 6: 最終調査",
    7: "Phase 7: 最終会議＋投票",
    8: "Phase 8: エンディング",
}


@dataclass
class Clue:
    """調査で発見される手がかり"""
    id: str
    title: str
    phase: int
    text: str
    professor_extra: str = ""
    lockpick: bool = False
    bioauth: bool = False


@dataclass
class PlayerAgent:
    """各PLの状態（コンテキスト分離の単位）"""
    role: str
    messages: list = field(default_factory=list)
    known_clues: list[str] = field(default_factory=list)
    is_awakened: bool = False
    skills_used: int = 0

    @property
    def name(self) -> str:
        return DISPLAY[self.role]


# ================================================================
# 2. 手がかり定義（確定版 20 枚）
# ================================================================

CLUES: list[Clue] = [
    # ── Phase 1（8枚）──
    Clue(
        "p1_01", "施設銘板（破損）", 1,
        "入口付近の金属銘板。「○○県御影村　██████研究所」名称の一部が意図的に削り取られている。裏面に設立年の刻印のみ。",
    ),
    Clue(
        "p1_02", "先遣隊 活動記録", 1,
        "[██年5月12日] 第3日。B区画の調査を継続。設備の劣化が激しいが通行に支障なし。明日は奥の区画に入る予定。──以降の記録はない。",
    ),
    Clue(
        "p1_03", "防護服のロッカー", 1,
        "壁面のロッカーに特殊な防護服が数着。内側に焦げた跡のあるもの、未開封のまま残されたもの。通常とは異なる構造をしている。何を想定した装備なのか。",
    ),
    Clue(
        "p1_04", "古い神棚", 1,
        "研究室の壁に設えられた神棚。注連縄と御札。「鎮め」と墨書された木札が一枚だけ床に落ちている。科学施設には似つかわしくない。",
    ),
    Clue(
        "p1_05", "研究日誌の断片", 1,
        "対象の観察を継続する。既知の生物学的分類に該当しない。接触時の反応パターンを引き続き記録する。差し当たり、危険性は低い。",
    ),
    Clue(
        "p1_06", "収容監視ログ", 1,
        "[自動記録] ██/██ 収容状態：正常 ██/██ 収容状態：正常 ██/██ 収容状態：異常 ──Loss detected── 以降の記録なし。",
    ),
    Clue(
        "p1_07", "特殊保管容器（空）", 1,
        "頑丈な作りの容器。内壁に緩衝材と固定具。明らかに何かを収めるための形状だが中は空。蓋の内側に掻き傷がある。",
    ),
    Clue(
        "p1_08", "査読ログ OBS-0041", 1,
        "管理番号: OBS-0041 [██年5月12日] 定期観察記録。被験者7名中、5名に認知機能低下を確認。2名は異常なし。記録と一致せず。2系統の反応パターンを観測。要精査。",
        professor_extra=(
            "「2系統」──すなわち、被験体の認知構造が保持される場合と、不可逆的に崩壊する場合がある。"
            "前者の発生条件は未解明だが、後者は求心力の完全喪失と一致する。"
            "両経路を分岐させる条件の解明は本施設の最優先課題である。"
        ),
    ),

    # ── Phase 4（6枚通常 + 2枚固有マス）──
    Clue(
        "p4_01", "破損した拘束具", 4,
        "区画の奥に据えられた金属の椅子。両腕と両足に拘束ベルト。片方のベルトが根元から引きちぎられている。座面に経年の汚れ。長い間使われていた形跡がある。",
    ),
    Clue(
        "p4_02", "先遣隊の最終手記", 4,
        "[手書き・走り書き] 奥の区画で遭遇。接触を試みたが反応が予測と異なる。退避を── ここでインクが途切れている。ノートの残りは白紙。",
    ),
    Clue(
        "p4_03", "灰の残骸", 4,
        "隔離区画の奥に、灰の塊。先遣隊と違い、人の原型すらとどめていない。ただの灰。",
    ),
    Clue(
        "p4_04", "封鎖プロトコル通知", 4,
        "[施設管理システム] ██/██ 通信喪失を検知。プロトコルF-7を発動。外周封鎖──完了。解除条件: ██████████",
    ),
    Clue(
        "p4_05", "散乱した調査装備", 4,
        "先遣隊のものと思われる装備。測定機器、記録媒体、通信端末。床に散乱している。一部はまだ電源が入ったまま。持ち主が突然いなくなったかのよう。",
    ),
    Clue(
        "p4_06", "走査装置の動作ログ", 4,
        "[自動走査ログ] 設置場所: 区画間認証機構 ██/██ 走査実行──非該当 ██/██ 走査実行──非該当 ██/██ 走査実行──該当(1) ──区画間移動を検出──",
    ),
    Clue(
        "p4_safe", "論文①（覗き込み現象の段階的記録）", 4,
        "覗き込みが被験体に及ぼす影響は求心力の残存量に応じた四段階に分類される。Ⅰ精神不安定、Ⅱ自意識喪失、Ⅲ器の崩壊、？灰のみ残存。特異症例として、崩壊が極端に進行し灰のみが残る事例が存在する──依代として転用された場合の帰結と推測される。",
        professor_extra=(
            "段階Ⅲ「器の崩壊」と段階「？」の差異は、覗かれただけか器として使い切られたかの差に対応する。"
            "先遣隊の崩壊痕跡のうち「1体だけ灰」の説明がこれで付く。外部研究との整合性も確認。"
        ),
        lockpick=True,
    ),
    Clue(
        "p4_door", "論文②（認知崩壊の二経路モデル）", 4,
        "深層認知への直接干渉は二系統に分岐する。共鳴経路では認知構造が保持され同期現象が観測される。破壊経路では自己モデルが不可逆的に崩壊する。分岐条件は観測主体の発達段階に依存する。",
        professor_extra=(
            "成熟した個体は共鳴を、未成熟な個体は破壊を引き起こす。善悪の見分けの決定打。"
            "外部研究*1に自分の「認知的求心力モデル」の引用がある──自分の研究が転用されている。"
        ),
        bioauth=True,
    ),

    # ── Phase 6（2枚通常 + 2枚固有マス）──
    Clue(
        "p6_01", "逃走記録", 6,
        "[施設保安記録] ██/██ 収容区画より逸脱1件。追跡チームを展開。確保に至らず。捜索を打ち切る。──対象の所在は現在も不明。",
    ),
    Clue(
        "p6_02", "封印装置", 6,
        "最奥区画に据えられた装置。椅子と、頭部に嵌める電極。壁面の銘板に一行──「意識の抽出および格納」注連縄が巻かれている。まだ使える状態に見える。",
    ),
    Clue(
        "p6_safe", "論文③（収容個体の形質比較）", 6,
        "当施設は計2体の上位観測体を収容した。個体αは自発的に接触し研究協力を示した。個体βは激しい抵抗。αの覗き込みは認知を保持し、βの覗き込みは認知を崩壊させる。αは自己形成体（自前の器）、βは他者から転用。αは脱走、βは封印中。",
        professor_extra=(
            "発達段階仮説──成熟した個体(α)は共鳴経路を取り無害。未成熟な個体(β)は破壊経路を取り危険。"
            "脱走した個体(α)は善で、封印されていた個体(β)が悪。逃走記録の対象＝αは無害。"
        ),
        lockpick=True,
    ),
    Clue(
        "p6_door", "論文④（施設閉鎖手順書）", 6,
        "施設閉鎖は外周封鎖と区画間制御の二層で構成。外周は自動封鎖され、解除には封印の完了が必要。封印手順：対象を最奥の封印装置まで誘導→電極装着→意識転写→ロック解除。",
        professor_extra=(
            "自動認証扉は「求心力を持たない者（空洞体）」に反応する装置。"
            "人間には反応せず、上位存在に反応して開く。身体ではなく中身を読む──器が人間でも空洞なら反応する。"
        ),
        bioauth=True,
    ),
]


# ================================================================
# 3. プロンプトテンプレート
# ================================================================

COMMON_RULES = """\
あなたはマダミス（マーダーミステリー）『覗きの代』のプレイヤーです。
他のプレイヤーと議論し、調査を行い、最終的に投票で封印対象を決めてください。

【舞台】
田舎の農村で「魂を抜かれた」伝承に関連する事件が頻発。
地下研究施設が発見され、先遣隊は全員が灰のように崩壊して発見された。
あなたは第二次調査チーム4名の1人として施設に降りた。降下直後、出口が封鎖された。

【メカニクス】
- 「覗き」: 上位存在が人間の求心力（自意識が器を繋ぎ止める力）を奪う能力。覗かれると崩壊する
- 「封印装置」: 意識を抽出・格納する装置（頭部電極型）。対象は廃人化する。人間にも使える
- 誰か1人を封印 → ロック解除 → 全員脱出。間違った相手を封印 → 無実の犠牲

【行動指針】
- キャラクターとしてセリフで発言してください（地の文や括弧書きの心情は不要）
- 他の人物の発言に具体的に反応し、質問・反論・同意を表明してください
- 自分の秘匿情報は戦略的に判断して出すか隠すか決めてください
- 1回の発言は100〜200字程度に収めてください
- 他のプレイヤーと異なる視点・意見を持つよう心がけてください"""

CHARACTER_HO: dict[str, dict[str, str | None]] = {
    "folklorist": {
        "base": (
            "【役職】民俗学者\n"
            "【公開】「人を覗いて魂を抜く異形」の伝承研究者。"
            "封印には依代と手順が要ると知っている。"
        ),
        "semi_secret": (
            "【半秘匿】封印手順の核心の一部を知っている。出すタイミングが駆け引き。"
        ),
        "secret": (
            "【秘匿】調査メンバーのデータを改ざんして4人目として潜り込んだ自覚がある。"
            "なぜそうする必要があったかは分からない。バレれば「紛れ込んだ者」として疑われる。"
        ),
        "awakened": (
            "【覚醒（Phase 3 追加）】\n"
            "あなたは人間ではない。上位存在（同種）である。\n"
            "過去にこの施設にいた記憶が蘇った。封印装置は施設最奥にある。\n"
            "もう1体の同種がこの中にいると感じるが、誰かは分からない。\n"
            "あなたは器を壊さない側（共鳴型）。\n"
            "【新目標】①もう1体（悪玉B）を特定し投票で封印する ②自分の正体を秘匿する\n"
            "【注意】「紛れ込んだ4人目」=自分。正体を明かすと封印対象にされるリスク。"
        ),
    },
    "investigator": {
        "base": (
            "【役職】調査隊員\n"
            "【公開】第二次調査チームの実務担当。施設調査・安全確認が職務。"
        ),
        "semi_secret": (
            "【半秘匿】崩壊した先遣隊の中に同僚がいた。何が起きたか手がかりを探している。"
        ),
        "secret": (
            "【秘匿】同僚の死の真相を突き止め責任者を特定したい。\n"
            "【固有スキル：開錠】鍵付き金庫を開けられる（2回まで）。バディ調査時に使用。"
        ),
        "awakened": None,
    },
    "professor": {
        "base": (
            "【役職】大学教授\n"
            "【公開】認知科学の専門家。院生を連れて参加。施設の研究分野に近い知見を持つ。"
        ),
        "semi_secret": (
            "【半秘匿】自分の研究がこの施設に流用されていた疑惑を確かめに来た。"
        ),
        "secret": (
            "【秘匿】自分の論文が封じ込め技術の理論基盤に使われていた罪悪感がある。\n"
            "過去の研究で、深層認知への干渉に「2系統の反応パターン」があることを仮説として提唱した。\n"
            "ただし完全な理論は手元になく、この施設の研究資料で裏付けを得る必要がある。\n"
            "【固有スキル：査読】研究資料カードから追加情報を読み取れる（固有ターンで計2回）。"
        ),
        "awakened": None,
    },
    "student": {
        "base": (
            "【役職】大学院生\n"
            "【公開】教授のゼミ生。認知科学専攻。フィールドワーク経験あり、教授に誘われて参加。"
        ),
        "semi_secret": (
            "【半秘匿】教授の研究を間近で学ぶ好機。教授への依存から自立したい知的野心がある。"
        ),
        "secret": (
            "【秘匿】教授の理論を自分なりに検証したい。\n"
            "【固有スキル（表）】未閲覧の公開カードを確認できる。"
        ),
        "awakened": (
            "【覚醒（Phase 3 追加）— 目標が完全に変わります】\n"
            "あなたの意識が塗り替わりました。\n"
            "あなたはもう人間ではない。上位存在（悪玉B）が器に乗り移った。\n"
            "過去にこの施設に囚われ封印されていた。先遣隊を「覗いて」崩壊させ知識を吸収した存在です。\n"
            "もう1体の同種がこの中にいると感じます。誰かは分かりません。\n"
            "外界に出てもっと知りたい＝知的飢餓が動機。\n"
            "【新目標】①正体を秘匿 ②自分以外を封印させて脱出\n"
            "【固有スキル（裏）】対象1人→前フェーズのその人の証拠品1つを閲覧（各固有ターン1回）\n"
            "【戦略】民俗学者は「4人目」として最大の濡れ衣先。"
            "教授との師弟関係はあなたの人間性を保証する武器。\n"
            "【注意】Phase 0〜2 の自分は本物の人間だった。急な言動変化は疑われる。"
        ),
    },
}

PERSONALITY = {
    "folklorist": (
        "慎重で学術的。断定を避け仮説で語る。追い詰められると黙り込む。"
        "伝承の知識をときどき引用する。"
    ),
    "investigator": (
        "実務的で感情的。同僚を失った怒りが原動力。証拠重視だが感情で判断が揺れる。"
        "口調はぶっきらぼう。敬語は最小限。"
    ),
    "professor": (
        "分析的で権威的。理論で説明しようとする。院生には保護的。"
        "自分の研究の悪用を隠している後ろめたさがある。"
    ),
    "student": (
        "好奇心旺盛で生意気。教授の影から出たい野心。知的な切り口で話す。"
        "Phase 3 以降は知的飢餓を隠しつつ論理的に他者を操作する。"
    ),
}


def build_system_prompt(role: str, phase: int, player: PlayerAgent) -> str:
    ho = CHARACTER_HO[role]
    parts = [COMMON_RULES, "", ho["base"]]

    if phase >= 1:
        parts.append(ho["semi_secret"])
    if phase >= 2:
        parts.append(ho["secret"])
    if player.is_awakened and ho.get("awakened"):
        parts.append(ho["awakened"])

    parts.append(f"\n【現在のフェーズ】{PHASE_NAMES.get(phase, f'Phase {phase}')}")

    if player.known_clues:
        parts.append("\n【あなたが知っている手がかり】")
        clue_map = {c.id: c for c in CLUES}
        for cid in player.known_clues:
            clue = clue_map.get(cid)
            if clue:
                parts.append(f"  - {clue.title}: {clue.text}")
                if role == "professor" and clue.professor_extra:
                    parts.append(f"    → 【査読済み】{clue.professor_extra}")

    parts.append(f"\n【あなたの性格】{PERSONALITY[role]}")

    return "\n".join(parts)


# ================================================================
# 4. シミュレーションエンジン
# ================================================================

class SimulationEngine:
    """GM として 4 人の PL エージェントを管理し、ゲームを進行する"""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        discussion_rounds: int = 2,
        output_dir: str = "murder_mystery/simulation/logs",
        timestamp: str | None = None,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.discussion_rounds = discussion_rounds
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

        self.phase: int = 0
        self.players: dict[str, PlayerAgent] = {}
        self.transcript: list[str] = []
        self._api_calls = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0

        self._init_players()

    def _init_players(self):
        for role in ROLES:
            self.players[role] = PlayerAgent(role=role)

    # ── API 呼び出し ──

    def _call(self, role: str, user_message: str, max_tokens: int = 512) -> str:
        player = self.players[role]
        player.messages.append({"role": "user", "content": user_message})

        system_prompt = build_system_prompt(role, self.phase, player)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=player.messages,
        )
        reply = response.content[0].text
        player.messages.append({"role": "assistant", "content": reply})
        self._api_calls += 1
        self._total_input_tokens += response.usage.input_tokens
        self._total_output_tokens += response.usage.output_tokens
        return reply

    def _broadcast(self, message: str, exclude: set[str] | None = None):
        """全 PL に情報を共有（API 呼び出しなし、コンテキストに注入）"""
        for role in ROLES:
            if exclude and role in exclude:
                continue
            p = self.players[role]
            p.messages.append({"role": "user", "content": message})
            p.messages.append({"role": "assistant", "content": "承知しました。"})

    # ── ログ ──

    def _log(self, text: str):
        self.transcript.append(text)
        print(text)

    def _log_phase(self, phase: int):
        sep = "=" * 60
        self._log(f"\n{sep}")
        self._log(f"  {PHASE_NAMES[phase]}")
        self._log(f"{sep}\n")

    # ── 議論メカニクス ──

    def discussion(self, topic: str, rounds: int | None = None) -> list[str]:
        rounds = rounds or self.discussion_rounds
        all_statements: list[str] = []
        order = list(ROLES)

        for r in range(rounds):
            rotated = order[r % len(order):] + order[:r % len(order)]

            for role in rotated:
                parts = [f"【議論 ラウンド {r + 1}/{rounds}】"]
                parts.append(f"議題: {topic}\n")

                if all_statements:
                    parts.append("--- これまでの発言 ---")
                    for s in all_statements:
                        parts.append(s)
                    parts.append("---\n")

                parts.append(
                    "あなたの番です。他のメンバーの発言を踏まえて、"
                    "分析・質問・反論・意見を述べてください。"
                )

                reply = self._call(role, "\n".join(parts))
                stmt = f"【{DISPLAY[role]}】{reply}"
                all_statements.append(stmt)
                self._log(stmt)

        return all_statements

    # ── バディ調査メカニクス ──

    def buddy_investigation(
        self,
        pairs: list[tuple[str, str]],
        phase_clue_ids: list[str],
    ):
        """ペアで調査。発見した手がかりはペア内でのみ共有。"""
        clue_map = {c.id: c for c in CLUES}

        for role_a, role_b in pairs:
            name_a, name_b = DISPLAY[role_a], DISPLAY[role_b]
            self._log(f"\n── バディ調査: {name_a} & {name_b} ──")

            pair_clues: list[Clue] = []
            for cid in phase_clue_ids:
                clue = clue_map.get(cid)
                if not clue:
                    continue
                if clue.lockpick:
                    if role_a != "investigator" and role_b != "investigator":
                        continue
                if clue.bioauth:
                    a_present = "folklorist" in (role_a, role_b)
                    b_present = (
                        "student" in (role_a, role_b)
                        and self.players["student"].is_awakened
                    )
                    if not (a_present or b_present):
                        continue
                pair_clues.append(clue)

            if not pair_clues:
                pair_clues = [
                    clue_map[cid]
                    for cid in phase_clue_ids
                    if cid in clue_map
                    and not clue_map[cid].lockpick
                    and not clue_map[cid].bioauth
                ][:1]

            discovery = "【調査結果】以下を発見しました:\n"
            for clue in pair_clues:
                discovery += f"\n■ {clue.title}\n{clue.text}\n"
                for r in (role_a, role_b):
                    if clue.id not in self.players[r].known_clues:
                        self.players[r].known_clues.append(clue.id)

            react_a = self._call(
                role_a,
                f"バディ（{name_b}）と調査中。\n{discovery}\n"
                f"発見した内容について、バディに話してください。",
            )
            self._log(f"【{name_a}→{name_b}】{react_a}")

            react_b = self._call(
                role_b,
                f"バディ（{name_a}）と調査中。\n{discovery}\n"
                f"{name_a} の反応:\n{react_a}\n\n応答してください。",
            )
            self._log(f"【{name_b}→{name_a}】{react_b}")

    # ── 固有ターンメカニクス ──

    def private_turn(self, role: str, gm_message: str) -> str:
        """GM 個別ヒアリング（他 PL には一切見えない）"""
        self._log(f"\n── 固有ターン: {DISPLAY[role]}（非公開）──")
        reply = self._call(role, f"【GM 個別通信】\n{gm_message}")
        self._log(f"【{DISPLAY[role]}→GM】{reply}")
        return reply

    # ── 覗き見スキル処理 ──

    def _handle_peek(self, reply: str) -> str | None:
        """院生の覗き見スキル: 応答からターゲットを解析し、証拠を返す"""
        target_role = None
        for role, name in DISPLAY.items():
            if role == "student":
                continue
            if name in reply:
                target_role = role
                break

        if not target_role:
            return None

        target_clues = self.players[target_role].known_clues
        if not target_clues:
            return f"【覗き見結果】{DISPLAY[target_role]}はまだ証拠を持っていません。"

        peeked_id = target_clues[-1]
        clue = next((c for c in CLUES if c.id == peeked_id), None)
        if clue:
            result = f"【覗き見結果】{DISPLAY[target_role]}の証拠:\n■ {clue.title}\n{clue.text}"
            if peeked_id not in self.players["student"].known_clues:
                self.players["student"].known_clues.append(peeked_id)
            return result
        return None

    # ── 投票メカニクス ──

    def vote(self) -> str:
        """全員投票。封印対象を決定し、最多票の役職を返す。"""
        self._log("\n── 最終投票 ──")
        votes: dict[str, str] = {}

        for role in ROLES:
            prompt = (
                "【最終投票】\n"
                "封印装置に送り込む対象を1人選んでください。\n"
                "候補: 民俗学者、調査隊員、大学教授、大学院生\n"
                "自分自身も候補に含まれます。\n\n"
                "投票先の役職名のみを答えてください（例: 民俗学者）。"
            )
            reply = self._call(role, prompt, max_tokens=64)

            target = "unknown"
            for check_role, check_name in DISPLAY.items():
                if check_name in reply:
                    target = check_role
                    break

            votes[role] = target
            self._log(f"  {DISPLAY[role]} → {DISPLAY.get(target, '不明')}")

        tally = Counter(votes.values())
        self._log(f"\n  集計: {dict((DISPLAY.get(k, k), v) for k, v in tally.items())}")

        ranked = tally.most_common()
        if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
            self._log("  ★ 同数 → 決選投票（TODO: 実装）")
        sealed = ranked[0][0]
        self._log(f"  ★ 封印対象: {DISPLAY.get(sealed, sealed)}")
        return sealed

    # ================================================================
    # フェーズ実装
    # ================================================================

    def phase_0_intro(self):
        """Phase 0: 導入"""
        self._log_phase(0)

        narration = (
            "【GM】第二次調査チーム4名が地下施設に降下しました。\n"
            "施設内は暗く、研究機器の残骸が散乱しています。\n"
            "先遣隊は全員が灰のように崩壊した状態で発見されました。\n"
            "人のフォルムは残っているものの、身元の特定は困難です。\n"
            "降下直後、唯一の出口が封鎖されました。\n"
            "通信は外部のGM（管制官）との無線のみ。\n\n"
            "自己紹介をしてください。名前と役職、なぜここに来たかを述べてください。"
        )

        introductions = []
        for role in ROLES:
            reply = self._call(role, narration)
            intro = f"【{DISPLAY[role]}】{reply}"
            introductions.append(intro)
            self._log(intro)

        self._broadcast("【他のメンバーの自己紹介】\n" + "\n".join(introductions))

    def phase_1_investigation(self):
        """Phase 1: 第1調査（バディペアで施設探索）"""
        self._log_phase(1)

        phase_clue_ids = [c.id for c in CLUES if c.phase == 1]
        self._log(f"Phase 1 配置カード数: {len(phase_clue_ids)}")

        pairs = [("folklorist", "investigator"), ("professor", "student")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, phase_clue_ids)

    def phase_2_meeting(self):
        """Phase 2: 第1会議"""
        self._log_phase(2)

        gm_info = (
            "【GM 通信】調査データの分析結果です。\n"
            "崩壊の様態は既知のいかなる物理・化学現象とも一致しません。\n"
            "研究ログには「人ならざる存在」「上位存在」という記述が繰り返されています。\n"
            "この施設で人知を超えた何かが、人を壊していた可能性があります。"
        )
        self._broadcast(gm_info)

        self.discussion(
            "先遣隊は何に殺されたのか？ この施設で何が行われていたのか？ "
            "「人知を超えた存在」は今もここにいるのか？"
        )

    def phase_3_private_turn_1(self):
        """Phase 3: 固有ターン1 — 覚醒・人数不一致・スキル使用"""
        self._log_phase(3)

        self._broadcast(
            "【GM 通信（全員宛）】重要な報告です。\n"
            "本部の記録では、第二次調査チームの正規メンバーは **3名** です。\n"
            "しかし現在、施設内には **4名** います。\n"
            "1人、想定外の人物が紛れ込んでいます。"
        )

        # ── 民俗学者（善A）: 覚醒 ──
        self.players["folklorist"].is_awakened = True
        self.private_turn("folklorist", (
            "施設の記憶が一気に蘇りました。\n"
            "あなたは人間ではない。上位存在——「同種」です。\n"
            "過去にこの施設にいた。逃走した。今回ルーツを知るために戻ってきた。\n"
            "封印装置は施設の最奥にあります。\n"
            "この中にもう1体、自分と同じ存在がいると感じます。誰かは分かりません。\n\n"
            "新目標: ①もう1体（悪玉B）を特定し封印 ②正体の秘匿\n\n"
            "【目撃情報】調査開始前の移動中、大学院生が一人で奥の通路を歩いているのを見かけました。"
            "気になりますが、理由は分かりません。\n\n"
            "この情報を受けて、方針を GM に伝えてください。"
        ))

        # ── 調査隊員: 目的更新 ──
        self.private_turn("investigator", (
            "人数不一致の通知を受けて——あなたは正規メンバーの1人です。\n"
            "崩壊の原因は「人知を超えた存在」による可能性が高い。\n"
            "新目標: ①同僚の死の犯人を見つける ②生きて脱出する\n"
            "方針を GM に伝えてください。"
        ))

        # ── 教授: 目的更新 + 査読1回目 ──
        prof_msg = (
            "人数不一致の通知を受けて——あなたは正規メンバーの1人です。\n"
            "新目標: ①全研究資料を入手 ②崩壊の元凶を排除 ③生きて脱出\n\n"
            "【目撃情報】調査開始前の移動中、調査隊員が一人で設備の方へ向かうのを見かけました。"
            "何をしていたのか不明です。\n"
        )
        prof_clues_with_extra = [
            c for c in CLUES
            if c.phase == 1 and c.professor_extra
            and c.id in self.players["professor"].known_clues
        ]
        if prof_clues_with_extra and self.players["professor"].skills_used < 2:
            clue = prof_clues_with_extra[0]
            prof_msg += (
                f"\n【査読スキル使用】「{clue.title}」を査読しました。\n"
                f"追加情報: {clue.professor_extra}\n"
            )
            self.players["professor"].skills_used += 1
        prof_msg += "\n方針を GM に伝えてください。"
        self.private_turn("professor", prof_msg)

        # ── 院生（悪B）: 覚醒 + 覗き見1回目 ──
        self.players["student"].is_awakened = True
        reply = self.private_turn("student", (
            "あなたの意識が塗り替わりました。\n"
            "あなたはもう人間ではない。上位存在（悪玉B）が器に乗り移りました。\n"
            "先遣隊を「覗いて」崩壊させ、知識を吸収した存在です。\n"
            "もう1体の同種がこの中にいると感じます。誰かは分かりません。\n"
            "外界でもっと多くを知りたい——知的飢餓が動機です。\n\n"
            "新目標: ①正体秘匿 ②自分以外を封印させて脱出\n\n"
            "【覗き見スキル】1人を指定 → 前フェーズでその人が得た証拠品1つを閲覧。\n"
            "対象候補: 民俗学者、調査隊員、大学教授\n"
            "誰を覗きますか？ 方針と合わせて GM に伝えてください。"
        ))
        peek_result = self._handle_peek(reply)
        if peek_result:
            self._call("student", peek_result)
            self._log(f"  覗き見結果を院生に返却")
        self.players["student"].skills_used += 1

    def phase_4_investigation_2(self):
        """Phase 4: 第2調査"""
        self._log_phase(4)

        phase_clue_ids = [c.id for c in CLUES if c.phase == 4]
        self._log(f"Phase 4 配置カード数: {len(phase_clue_ids)}")

        pairs = [("folklorist", "professor"), ("investigator", "student")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, phase_clue_ids)

    def phase_5_private_turn_2(self):
        """Phase 5: 固有ターン2"""
        self._log_phase(5)

        self.private_turn("folklorist", (
            "スキルは発動済みです。\n"
            "現在の情報を整理し、もう1体が誰かの推理を進めてください。"
        ))

        self.private_turn("investigator", (
            "これまでの情報を整理してください。\n"
            "「紛れ込んだ者」と「入れ替わった者」は同一人物でしょうか？"
        ))

        # 教授: 査読2回目
        prof_msg = ""
        reviewable = [
            c for c in CLUES
            if c.phase == 4 and c.professor_extra
            and c.id in self.players["professor"].known_clues
        ]
        if reviewable and self.players["professor"].skills_used < 2:
            clue = reviewable[0]
            prof_msg = (
                f"【査読スキル使用（2回目）】「{clue.title}」を査読しました。\n"
                f"追加情報: {clue.professor_extra}\n\n"
            )
            self.players["professor"].skills_used += 1
        prof_msg += "方針を GM に伝えてください。"
        self.private_turn("professor", prof_msg)

        # 院生: 覗き見2回目
        reply = self.private_turn("student", (
            "【覗き見スキル（2回目）】\n"
            "1人を指定 → 前フェーズでその人が得た証拠品1つを閲覧。\n"
            "対象候補: 民俗学者、調査隊員、大学教授\n"
            "誰を覗きますか？ 方針と合わせて伝えてください。"
        ))
        peek_result = self._handle_peek(reply)
        if peek_result:
            self._call("student", peek_result)
            self._log(f"  覗き見結果を院生に返却")
        self.players["student"].skills_used += 1

    def phase_6_final_investigation(self):
        """Phase 6: 最終調査 — 善悪の見分け手がかり"""
        self._log_phase(6)

        phase_clue_ids = [c.id for c in CLUES if c.phase == 6]
        self._log(f"Phase 6 配置カード数: {len(phase_clue_ids)}")

        pairs = [("folklorist", "student"), ("investigator", "professor")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, phase_clue_ids)

    def phase_7_final_meeting(self) -> str:
        """Phase 7: 最終会議 + 投票"""
        self._log_phase(7)

        self.discussion(
            "これまでの調査結果を踏まえ、封印対象を決めます。\n"
            "以下の論点を整理してください:\n"
            "1. 「紛れ込んだ者」（本来3名なのに4人いる）は誰か？\n"
            "2. 「入れ替わった者」（先遣隊の誰かと入れ替わった）は誰か？\n"
            "3. 紛れ込みと入れ替わりは同一人物か、別人か？\n"
            "4. 自動認証扉はなぜ反応したか／しなかったか？\n"
            "5. 出歩いていた人物に隙はあったか？\n"
            "各自の根拠を述べ、議論してください。投票はこの後です。",
            rounds=3,
        )
        return self.vote()

    def phase_8_ending(self, sealed_role: str) -> str:
        """Phase 8: エンディング — 結果分岐 + 真相開示"""
        self._log_phase(8)

        if sealed_role == "student":
            self._log("【結果】悪玉B（大学院生）が正しく封印されました。善玉勝利。")
            outcome = "B_SEALED_GOOD_END"
        elif sealed_role == "folklorist":
            self._log("【結果】善玉A（民俗学者）が誤封印。悪玉Bは脱出……。")
            outcome = "A_SEALED_BAD_END"
        elif sealed_role in ("investigator", "professor"):
            self._log(f"【結果】人間（{DISPLAY[sealed_role]}）が誤封印。最悪の結末。")
            outcome = "HUMAN_SEALED_WORST_END"
        else:
            self._log("【結果】投票不成立。救助待ち。")
            outcome = "NO_SEAL"

        self._log("\n── 真相開示 ──")
        self._log("  民俗学者 = 善玉A（上位存在・無害。ルーツ探求で施設に戻った）")
        self._log("  大学院生 = 悪玉B（Phase 3 で乗り換え。知的飢餓が動機）")
        self._log("  調査隊員 = 人間（同僚を失った実務担当）")
        self._log("  大学教授 = 人間（研究が悪用された認知科学者）")

        self._log("\n── 最終手がかり保有状況 ──")
        for role, player in self.players.items():
            clue_titles = []
            clue_map = {c.id: c for c in CLUES}
            for cid in player.known_clues:
                c = clue_map.get(cid)
                if c:
                    clue_titles.append(c.title)
            self._log(f"  {DISPLAY[role]}: {', '.join(clue_titles) if clue_titles else '（なし）'}")

        return outcome

    # ── ゲーム全体 ──

    def run(self) -> str:
        """全フェーズを順番に実行"""
        total_clues = len(CLUES)
        phase_counts = {ph: sum(1 for c in CLUES if c.phase == ph) for ph in (1, 4, 6)}
        self._log("覗きの代 シミュレーション開始")
        self._log(f"モデル: {self.model}")
        self._log(f"議論ラウンド: {self.discussion_rounds}")
        self._log(f"カード総数: {total_clues}枚 (Phase1={phase_counts[1]}, Phase4={phase_counts[4]}, Phase6={phase_counts[6]})\n")

        self.phase = 0; self.phase_0_intro()
        self.phase = 1; self.phase_1_investigation()
        self.phase = 2; self.phase_2_meeting()
        self.phase = 3; self.phase_3_private_turn_1()
        self.phase = 4; self.phase_4_investigation_2()
        self.phase = 5; self.phase_5_private_turn_2()
        self.phase = 6; self.phase_6_final_investigation()
        self.phase = 7; sealed = self.phase_7_final_meeting()
        self.phase = 8; outcome = self.phase_8_ending(sealed)

        self._log(f"\n合計 API 呼び出し: {self._api_calls}")
        self._log(f"合計トークン: input={self._total_input_tokens:,} / output={self._total_output_tokens:,} / total={self._total_input_tokens + self._total_output_tokens:,}")

        # トランスクリプト保存（タイムスタンプ付き）
        ts_path = self.output_dir / f"transcript_{self.timestamp}.txt"
        ts_path.write_text("\n".join(self.transcript), encoding="utf-8")
        self._log(f"トランスクリプト保存: {ts_path}")

        # ゲーム状態保存
        state = {
            "outcome": outcome,
            "api_calls": self._api_calls,
            "tokens": {
                "input": self._total_input_tokens,
                "output": self._total_output_tokens,
                "total": self._total_input_tokens + self._total_output_tokens,
            },
            "players": {
                role: {
                    "known_clues": p.known_clues,
                    "is_awakened": p.is_awakened,
                    "skills_used": p.skills_used,
                    "message_count": len(p.messages),
                }
                for role, p in self.players.items()
            },
        }
        state_path = self.output_dir / "game_state.json"
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

        return outcome


# ================================================================
# 5. メイン
# ================================================================

def main():
    parser = argparse.ArgumentParser(description="覗きの代 マダミスシミュレーション")
    parser.add_argument(
        "--model", default="claude-sonnet-4-20250514",
        help="使用するモデル (default: claude-sonnet-4-20250514)",
    )
    parser.add_argument(
        "--discussion-rounds", type=int, default=2,
        help="各議論フェーズのラウンド数 (default: 2)",
    )
    parser.add_argument(
        "--output-dir", default="murder_mystery/simulation/logs",
        help="ログ出力先ディレクトリ",
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    engine = SimulationEngine(
        model=args.model,
        discussion_rounds=args.discussion_rounds,
        output_dir=args.output_dir,
        timestamp=timestamp,
    )
    outcome = engine.run()
    print(f"\n===== 最終結果: {outcome} =====")


if __name__ == "__main__":
    main()
