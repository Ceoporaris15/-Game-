import streamlit as st
import random
import math

# ページ設定
st.set_page_config(page_title="国家間Game会改：極限", layout="wide")
st.title("🌏 国家間Game会改：心理戦の極地")

# 初期化（目標ポイントを100に引き上げ、8分程度の重厚なプレイ感に設定）
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "プレイヤー", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI（デウス）", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["システム起動。100ポイントの国力を先に得た者が覇権を握る。"],
        "ap": 2,
        "is_ai_turn": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# 計算ロジック
def get_income(player):
    # 毎ターンの国力増加（軍事と領土のバランスが重要）
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    # 植民地10ごとにAP+1
    return 2 + int(player["colony"] * 0.1)

# --- AIの高度な思考ルーチン ---
def run_ai_logic():
    income = get_income(p2)
    p2["power"] += income
    p2["shield"] = False
    current_ap = get_max_ap(p2)
    
    while current_ap > 0:
        # プレイヤーの次の一手を予測する心理ロジック
        prob_player_attack = 0.7 if p1["military"] > p2["military"] else 0.3
        
        # 1. リーサル確認（勝ち逃げ）
        if p2["power"] + (current_ap * 5) >= 100:
            action = "ECONOMY"
        # 2. プレイヤーを滅ぼせるなら攻撃
        elif p2["military"] * 0.5 >= p1["territory"]:
            action = "ATTACK"
        # 3. 心理的防衛（プレイヤーが攻撃してきそうならあえて防衛）
        elif prob_player_attack > 0.6 and not p2["shield"] and random.random() < 0.8:
            action = "DEFEND"
        # 4. 植民地化（AP増加を狙う）
        elif current_ap >= 2 and p1["territory"] > 10 and random.random() < 0.5:
            action = "OCCUPY"
        # 5. 経済基盤の強化
        else:
            if p2["military"] < p2["territory"]:
                action = "MILITARY"
            else:
                action = "MILITARY" if random.random() < 0.6 else "ECONOMY"

        # 実行
        if action == "MILITARY":
            p2["military"] += 4; current_ap -= 1
            s["logs"].insert(0, f"AI：軍拡を選択。軍事バランスを最適化。")
        elif action == "ECONOMY":
            p2["power"] += 5; current_ap -= 1
            s["logs"].insert(0, f"AI：軍縮を選択。経済的な圧力を強める。")
        elif action == "DEFEND":
            p2["shield"] = True; p2["military"] = max(0, p2["military"]-2); current_ap -= 1
            s["logs"].insert(0, f"AI：防衛を選択。こちらの攻撃を警戒している。")
        elif action == "ATTACK":
            dmg = p2["military"] * 0.4
            if p1["shield"]: dmg = 0; p1["shield"] = False; s["logs"].insert(0, "AIの攻撃！こちらの防衛が辛うじて耐えた。")
            else: p1["territory"] -= dmg; s["logs"].insert(0, f"AIの猛攻！領土が{dmg:.1f}削られた。")
            current_ap -= 1
        elif action == "OCCUPY":
            steal = p1["territory"] * 0.2
            p1["territory"] -= steal; p2["colony"] += steal; current_ap -= 2
            s["logs"].insert(0, f"AIが占領を実行。植民地を拡大された。")

    s["turn"] += 1
    p1["power"] += get_income(p1)
    p1["shield"] = False
    s["ap"] = get_max_ap(p1)
    s["is_ai_turn"] = False

# --- メイン表示 ---


col1, col2 = st.columns(2)
with col1:
    st.subheader(f"🟦 {p1['name']}")
    st.progress(min(p1['power']/100, 1.0), text=f"国力: {p1['power']:.1f} / 100")
    st.write(f"🏔️ 領土: {p1['territory']:.1f} | 🪖 軍事: {p1['military']:.1f}")
    st.caption(f"🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader(f"🟥 {p2['name']}")
    st.progress(min(p2['power']/100, 1.0), text=f"国力: {p2['power']:.1f} / 100")
    st.write(f"🏔️ 領土: {p2['territory']:.1f} | 🪖 軍事: {p2['military']:.1f}")
    st.caption(f"🚩 植民地: {p2['colony']:.1f}")

st.divider()

# ゲーム終了判定
if p1["power"] >= 100 or p1["territory"] <= 0 or p2["power"] >= 100 or p2["territory"] <= 0:
    winner = p1["name"] if (p1["power"] >= 100 or p2["territory"] <= 0) else p2["name"]
    st.balloons()
    st.header(f"🏆 勝者：{winner}")
    if st.button("リスタート"):
        st.session_state.clear()
        st.rerun()
else:
    # プレイヤーの操作
    if not s["is_ai_turn"]:
        st.subheader(f"TURN {s['turn']} | 残りAP: {s['ap']}")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        if c1.button("軍拡 (AP1)"):
            p1["military"] += 4; s["ap"] -= 1; s["logs"].insert(0, "あなた：軍拡。戦力を強化した。")
        if c2.button("軍縮 (AP1)"):
            p1["power"] += 5; s["ap"] -= 1; s["logs"].insert(0, "あなた：軍縮。経済成長を加速。")
        if c3.button("防衛 (AP1)"):
            p1["shield"] = True; p1["military"] = max(0, p1["military"]-2); s["ap"] -= 1; s["logs"].insert(0, "あなた：防衛。AIの攻撃を警戒。")
        if c4.button("攻撃 (AP1)"):
            dmg = p1["military"] * 0.4
            if p2["shield"]: dmg = 0; p2["shield"] = False; s["logs"].insert(0, "あなたの攻撃！AIのシールドに防がれた。")
            else: p2["territory"] -= dmg; s["logs"].insert(0, f"あなたの攻撃！AIの領土を{dmg:.1f}破壊。")
            s["ap"] -= 1
        if s["ap"] >= 2:
            if c5.button("占領 (AP2)"):
                steal = p2["territory"] * 0.2
                p2["territory"] -= steal; p1["colony"] += steal; s["ap"] -= 2
                s["logs"].insert(0, f"あなた：占領。植民地を確保。")
        
        if s["ap"] <= 0:
            if st.button("ターン終了"):
                s["is_ai_turn"] = True
                st.rerun()
    else:
        # AIターンの自動実行
        run_ai_logic()
        st.rerun()

st.write("### 📜 ログ")
for log in s["logs"][:5]:
    st.write(log)



