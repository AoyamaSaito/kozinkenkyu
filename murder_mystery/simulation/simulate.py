"""
覗きの代 シミュレーションエンジン（骨組み）
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
  pip install anthropic
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
# 2. 手がかり定義
#    TODO: 01_truth.md / 05_clues.md 確定後に実データへ差替
# ================================================================

CLUES: list[Clue] = [
    # ── Phase 1: 第1調査 ──
    Clue(
        "log_org_purpose", "研究ログ：組織の目的", 1,
        "この施設は「魂抜き」と呼ばれる現象を科学的に捕獲・研究する目的で設立された。"
        "被験体の「求心力」を測定する実験が繰り返されていた。",
    ),
    Clue(
        "log_subject_b", "研究ログ：被験体B", 1,
        "被験体Bは「接触した対象の求心力を急速に喪失させる」と記録。"
        "危険度最高。封印処置が施された。",
        professor_extra="実験プロトコルは自分の論文「認知的求心力モデル」をほぼそのまま転用している。",
    ),
    Clue(
        "log_subject_a", "研究ログ：被験体A", 1,
        "被験体Aは「擬態状態で安定し、宿主の人格を維持したまま共存する」と記録。"
        "ある日、施設から逃走。捕獲は断念された。",
    ),

    # ── Phase 4: 第2調査 ──
    Clue(
        "remains_variance", "崩壊痕跡の差異", 4,
        "先遣隊の遺体はすべて崩壊しているが、1体だけ崩壊が著しく進行。"
        "ほぼ灰のみで身元特定不可能。他は人のフォルムが残っている。",
    ),
    Clue(
        "equipment_mismatch", "装備の不一致", 4,
        "最も崩壊した遺体の周辺に、メンバーリストに載っていない装備品。"
        "誰かが先遣隊に紛れ込んでいた——あるいは入れ替わった。",
    ),
    Clue(
        "seal_device_record", "封印装置の実験記録", 4,
        "「意識抽出装置」の実験記録。頭部電極で意識を格納器に移す。"
        "身体は残るが意識が抜かれ廃人化。",
        professor_extra="抽出原理は自分の「求心力分離仮説」そのもの。上位存在専用ではなく人間にも適用可能。",
        lockpick=True,
    ),
    Clue(
        "bioauth_room", "自動認証区画の内部", 4,
        "自動認証で開く扉の奥。封印処置の詳細な手順書と、"
        "「2体目の被験体は逃走した」という追記がある。",
        bioauth=True,
    ),

    # ── Phase 6: 最終調査 ──
    Clue(
        "two_pathway_theory", "覗きの二経路理論", 6,
        "上位存在の「覗き」には2経路ある。"
        "①共鳴型：求心力を緩やかに減衰させるが崩壊には至らない。"
        "②破壊型：求心力を一方的に奪い急速な崩壊を引き起こす。",
        professor_extra="共鳴型=器を保つ(A)、破壊型=器を壊す(B)。善悪の見分けの決定打。",
    ),
    Clue(
        "escape_record", "逃走記録の断片", 6,
        "過去に1体の被験体が施設から逃走した警備ログ。"
        "「対象は人間の職員に擬態し、偽造IDで正門から脱出した」。",
    ),
    Clue(
        "deep_inconsistency", "深層のほころび", 6,
        "施設の心理テスト記録に、メンバーの過去データとの不一致。"
        "ある人物は過去の記憶が異様に薄く、別の人物は最近の記憶と性格に齟齬がある。",
        lockpick=True,
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
あなたは第二次探索チーム4名の1人として施設に降りた。降下直後、出口が封鎖された。

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
            "【公開】第二次探索チームの実務担当。施設調査・安全確認が職務。"
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
            "覗きの二経路理論（共鳴型／破壊型）の存在を知っている。\n"
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
            "あなたはもう人間ではない。上位存在（悪玉B）が器に乗り移った。\n"
            "過去にこの施設に囚われ封印されていた。先遣隊を「覗いて」崩壊させ知識を吸収した。\n"
            "もう1体の同種がこの中にいると感じるが、誰かは分からない。\n"
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
    """フェーズ・覚醒状態に応じたシステムプロンプトを動的に構築する。

    ポイント: system prompt は毎回の API 呼び出し時に再構築される。
    Phase 3 で is_awakened が True になると、覚醒 HO が注入される。
    ただし messages（会話履歴）は保持されるため、
    「人間だった頃の発言」が自然に偽装基盤として機能する。
    """
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
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.discussion_rounds = discussion_rounds
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.phase: int = 0
        self.players: dict[str, PlayerAgent] = {}
        self.transcript: list[str] = []
        self._api_calls = 0

        self._init_players()

    def _init_players(self):
        for role in ROLES:
            self.players[role] = PlayerAgent(role=role)

    # ── API 呼び出し（コンテキスト分離の核）──

    def _call(self, role: str, user_message: str, max_tokens: int = 512) -> str:
        """特定 PL にメッセージを送り応答を得る。

        各 PL は独立した system prompt と messages を持つ。
        他の PL のコンテキストには一切アクセスできない。
        """
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
        """公開議論。ラウンドロビンで発言し、全発言が全 PL に見える。

        各ラウンドで発言順をローテーションし、先手バイアスを軽減する。
        """
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
                # 開錠スキル判定
                if clue.lockpick:
                    if role_a != "investigator" and role_b != "investigator":
                        continue
                # 自動認証判定（A は常にエンティティ、B は覚醒後のみ）
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
            # 仮: 先に出た方を採用
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
            "【GM】第二次探索チーム4名が地下施設に降下しました。\n"
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

        # TODO: PL にペアを選ばせる方式に変更可能
        pairs = [("folklorist", "investigator"), ("professor", "student")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, [c.id for c in CLUES if c.phase == 1])

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

        # GM 通信: 人数不一致（全員に通知）
        self._broadcast(
            "【GM 通信（全員宛）】重要な報告です。\n"
            "本部の記録では、第二次探索チームの正規メンバーは **3名** です。\n"
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
            "新目標: ①もう1体（悪玉B）を特定し封印 ②正体の秘匿\n"
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
            "新目標: ①全研究資料を入手 ②崩壊の元凶を排除 ③生きて脱出\n"
        )
        if "log_subject_b" in self.players["professor"].known_clues:
            clue = next(c for c in CLUES if c.id == "log_subject_b")
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

        # ペアを変更して新しい組み合わせに
        pairs = [("folklorist", "professor"), ("investigator", "student")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, [c.id for c in CLUES if c.phase == 4])

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

        pairs = [("folklorist", "student"), ("investigator", "professor")]
        self._log(f"バディ: {DISPLAY[pairs[0][0]]}＆{DISPLAY[pairs[0][1]]}、"
                  f"{DISPLAY[pairs[1][0]]}＆{DISPLAY[pairs[1][1]]}")

        self.buddy_investigation(pairs, [c.id for c in CLUES if c.phase == 6])

    def phase_7_final_meeting(self) -> str:
        """Phase 7: 最終会議 + 投票"""
        self._log_phase(7)

        self.discussion(
            "これまでの調査結果を踏まえ、封印対象を決めます。\n"
            "「紛れ込んだ者」は誰か？ 「入れ替わった者」は誰か？\n"
            "この中で人間ではない「悪い何か」は誰か？\n"
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

        return outcome

    # ── ゲーム全体 ──

    def run(self) -> str:
        """全フェーズを順番に実行"""
        self._log("覗きの代 シミュレーション開始")
        self._log(f"モデル: {self.model}")
        self._log(f"議論ラウンド: {self.discussion_rounds}\n")

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

        # トランスクリプト保存
        ts_path = self.output_dir / "transcript.txt"
        ts_path.write_text("\n".join(self.transcript), encoding="utf-8")
        self._log(f"トランスクリプト保存: {ts_path}")

        # ゲーム状態保存
        state = {
            "outcome": outcome,
            "api_calls": self._api_calls,
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

    engine = SimulationEngine(
        model=args.model,
        discussion_rounds=args.discussion_rounds,
        output_dir=args.output_dir,
    )
    outcome = engine.run()
    print(f"\n===== 最終結果: {outcome} =====")


if __name__ == "__main__":
    main()
