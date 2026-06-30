# -*- coding: utf-8 -*-
"""全証拠カード画像生成（16枚通常 + 4枚研究資料カード = 20枚）"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design_card import make_evidence_card_wa, make_shock_card

DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "dist")

# ================================================================
# P1: 初期調査（8枚）
# ================================================================
P1 = [
    dict(no=1, title="施設銘板（破損）",
         body="入口付近の金属銘板。\n「○○県御影村\n　██████研究所」\n名称の一部が\n意図的に削り取られている。\n裏面に設立年の刻印のみ。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=2, title="先遣隊 活動記録",
         body="[20██年5月12日]\n第3日。B区画の調査を継続。\n設備の劣化が激しいが\n通行に支障なし。\n明日は奥の区画に入る予定。\n\n──以降の記録はない。",
         variant="log", header="記録", prefix="L"),

    dict(no=3, title="防護服のロッカー",
         body="壁面のロッカーに\n特殊な防護服が数着。\n内側に焦げた跡のあるもの、\n未開封のまま残されたもの。\n通常とは異なる構造をしている。\n何を想定した装備なのか。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=4, title="古い神棚",
         body="研究室の壁に設えられた神棚。\n注連縄と御札。\n「鎮め」と墨書された木札が\n一枚だけ床に落ちている。\n科学施設には似つかわしくない。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=5, title="研究日誌の断片",
         body="対象の観察を継続する。\n既知の生物学的分類に該当しない。\n接触時の反応パターンを\n引き続き記録する。\n差し当たり、危険性は低い。",
         variant="log", header="記録", prefix="L"),

    dict(no=6, title="収容監視ログ",
         body="[自動記録]\n20██/5/8 収容状態：正常\n20██/5/9 収容状態：正常\n20██/5/10 収容状態：正常\n20██/5/11 収容状態：正常\n20██/5/12 収容状態：異常\n──Loss detected──\n以降の記録なし。",
         variant="log", header="記録", prefix="L"),

    dict(no=7, title="特殊保管容器（空）",
         body="頑丈な作りの容器。\n内壁に緩衝材と固定具。\n明らかに何かを\n収めるための形状だが\n中は空。\n蓋の内側に掻き傷がある。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=41, title="定期観察記録",
         body="管理番号: OBS-0041\n[19██年██月██日]\n定期観察記録。被験者7名中、\n5名に認知機能低下を確認。\n2名は異常なし。記録と一致せず。\n2系統の反応パターンを観測。\n要精査。　　　[署名判読不能]",
         variant="log", header="観察記録", prefix="OBS"),
]

# ================================================================
# P4: 第2調査（6枚 — うち1枚はshock）
# ================================================================
P4 = [
    dict(no=9, title="破損した拘束具",
         body="区画の奥に据えられた金属の椅子。\n両腕と両足に拘束ベルト。\n片方のベルトが\n根元から引きちぎられている。\n座面に経年の汚れ。\n長い間使われていた形跡がある。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=10, title="先遣隊の最終手記",
         body="[手書き・走り書き]\n奥の区画で遭遇。\n接触を試みたが\n反応が予測と異なる。\n退避を──\n\nここでインクが途切れている。\nノートの残りは白紙。",
         variant="log", header="記録", prefix="L"),

    # shock card
    dict(no=11, title="灰の残骸",
         body="隔離区画の奥に、灰の塊。\n先遣隊と違い、\n人の原型すらとどめていない。\nただの灰。",
         shock=True, header="物的証拠", prefix="C"),

    dict(no=12, title="封鎖プロトコル通知",
         body="[施設管理システム]\n\n20██/5/12 通信喪失を検知。\nプロトコルF-7を発動。\n外周封鎖──完了。\n\n解除条件: ██████████",
         variant="log", header="記録", prefix="L"),

    dict(no=13, title="散乱した調査装備",
         body="先遣隊のものと思われる装備。\n測定機器、記録媒体、通信端末。\n床に散乱している。\n一部はまだ電源が入ったまま。\n持ち主が突然\nいなくなったかのよう。",
         variant="ofuda", header="物的証拠", prefix="C"),

    dict(no=14, title="走査装置の動作ログ",
         body="[自動走査ログ]\n設置場所: 区画間認証機構\n\n20██/5/10 走査実行──非該当\n20██/5/11 走査実行──非該当\n20██/5/12 走査実行──該当(1)\n──区画間移動を検出──",
         variant="log", header="記録", prefix="L"),
]

# ================================================================
# P7（旧P6）: 最終調査（2枚）
# ================================================================
P7 = [
    dict(no=15, title="逃走記録",
         body="[施設保安記録]\n\n19██/██/██　収容区画より逸脱1件。\n追跡チームを展開。\n\n確保に至らず。\n捜索を打ち切る。\n──対象の所在は現在も不明。",
         variant="log", header="記録", prefix="L"),

    dict(no=16, title="封印装置",
         body="最奥区画に据えられた装置。\n椅子と、頭部に嵌める電極。\n壁面の銘板に一行──\n「意識の抽出および格納」\n注連縄が巻かれている。\nまだ使える状態に見える。",
         variant="ofuda", header="物的証拠", prefix="C"),
]

# ================================================================
# 研究資料カード（4枚）
# ================================================================
RESEARCH = [
    dict(no=1, title="段階的変容仮説",
         body="覗き込み現象の段階的記録。\n内部紀要 Vol.7 No.3\n――詳しく調べれば、より多くの\n情報が得られる気がする。",
         variant="research", header="研究資料", prefix="R"),

    dict(no=2, title="二経路モデル",
         body="認知崩壊の二経路に関する\n内部研究資料。\n内部紀要 Vol.7 No.4\n――詳しく調べれば、より多くの\n情報が得られる気がする。",
         variant="research", header="研究資料", prefix="R"),

    dict(no=3, title="収容個体の形質比較",
         body="収容個体に関する比較分析。\n内部紀要 Vol.8 No.1\n――詳しく調べれば、より多くの\n情報が得られる気がする。",
         variant="research", header="研究資料", prefix="R"),

    dict(no=4, title="施設閉鎖手順書",
         body="封じ込め機構の運用指針。\n管理文書 CLO-003-R3\n――詳しく調べれば、より多くの\n情報が得られる気がする。",
         variant="research", header="研究資料", prefix="R"),
]

# ================================================================
# 生成
# ================================================================
def gen(cards, out_dir, phase_label):
    os.makedirs(out_dir, exist_ok=True)
    for c in cards:
        if c.get("shock"):
            img = make_shock_card(c["no"], c["title"], c["body"],
                                 header=c["header"], prefix=c["prefix"])
        else:
            img = make_evidence_card_wa(c["no"], c["title"], c["body"],
                                       variant=c["variant"],
                                       header=c["header"], prefix=c["prefix"])
        fname = "%s-%02d_%s.png" % (c["prefix"], c["no"], c["title"])
        path = os.path.join(out_dir, fname)
        img.save(path)
        print("  %s: %s" % (phase_label, fname))


if __name__ == "__main__":
    print("=== P1 証拠カード (8枚) ===")
    gen(P1, os.path.join(DIST, "カード", "証拠_P1"), "P1")

    print("=== P4 証拠カード (6枚) ===")
    gen(P4, os.path.join(DIST, "カード", "証拠_P4"), "P4")

    print("=== P7 証拠カード (2枚) ===")
    gen(P7, os.path.join(DIST, "カード", "証拠_P7"), "P7")

    print("=== 研究資料カード (4枚) ===")
    gen(RESEARCH, os.path.join(DIST, "カード", "研究資料"), "研究")

    print("\n完了: 計 %d 枚" % (len(P1) + len(P4) + len(P7) + len(RESEARCH)))
