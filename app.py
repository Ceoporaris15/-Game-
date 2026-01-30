import streamlit as st
import random
import math
import time

# ページ構成
st.set_page_config(page_title="国家間Game会改：極限", layout="wide")
st.title("🔥 国家間Game会改：極限 Overdrive")

# 初期化
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "人類軍", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "神格AI：デウス", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["システム起動。人類の存亡を賭けた戦いが始まる。"],
        "ap": 2,
        "phase": "PLAYER"
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# 計算式（15ターン決着用の高レート設定）
# 国力増加 = 軍事 * 領土 * 0.2
# AP = 2 + (植民地 * 0.1)

def get_income(player):
    return player["military"] * player["territory"] * 0.2

def get_max_ap(player):
    return 2 + int(player["colony"] * 0.1)

# --- UIレイアウト ---


col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"### 🟦 {p1['name']}")
    st.progress(min(p1['power']/30, 1.0), text=f"国力: {p1['power']:.1f} / 30")
    st.write(f"🏔️ 領土: {p1['territory']:.1f} | 🪖 軍事: {p1['military']:.1f}")
    st.caption(f"🚩 植民地: {p1['colony']:.1f} (APボーナス中)")

with col_b:
    st.markdown(f"### 🟥 {p2['name']}")
    st.progress(min(p2['power']/30, 1.0), text=f"国力: {p2['power']:.1f} / 30")
    st.write(f"🏔️ 領土: {p2['territory']:.1f} | 🪖 軍事: {p2['military']:.1f}")
    st.caption(f"🚩 植民地: {p2['colony']:.1f}")

# --- AIの極悪思考ルーチン ---
def run_ai_turn():
    income = get_income(p2)
    p2["power"] += income
    p2["shield"] = False
    max_ap = get_max_ap(p2)
    
    s["logs"].insert(0, f"⚠️ {p2['name']}の思考中...")
    
    current_ap = max_ap
    while current_ap > 0:
        # 1. あなたが死ぬなら迷わず殺す
        if p2["military"] * 0.5 >= p1["territory"]:
            action = "ATTACK"
        # 2. 自分が勝てるなら軍縮連打
        elif p2["power"] >= 20:
            action = "ECONOMY"
        # 3. あなたの軍事が高すぎるなら防衛
        elif p1["military"] > p2["military"] and not p2["shield"]:
            action = "DEFEND"
        # 4. あなたの領土が多ければ奪う（占領）
        elif current_ap >= 2 and p1["territory"] > 8:
            action = "OCCUPY"
        # 5. 基本は軍拡（経済と攻撃のベース）
        else:
            action = "MILITARY"

        # 実行
        if action == "MILITARY":
            p2["military"] += 4; current_ap -= 1
            s["logs"].insert(0, f"🤖 {p2['name']}：軍拡。演算能力を戦闘に回した。")
        elif action == "ECONOMY":
            p2["power"] += 5; current_ap -= 1
            s["logs"].insert(0, f"🤖 {p2['name']}：軍縮。経済ドミナンスを加速。")
        elif action == "DEFEND":
            p2["shield"] = True; p2["military"] = max(0, p2["military"]-2); current_ap -= 1
            s["logs"].insert(0, f"🤖 {p2['name']}：防衛。ナノマシン装甲を展開。")
        elif action == "ATTACK":
            dmg = p2["military"] * 0.5
            if p1["shield"]: dmg = 0; p1["shield"] = False
            p1["territory"] -= dmg; current_ap -= 1
            s["logs"].insert(0, f"🤖 {p2['name']}：攻撃。人類の拠点を破壊。")
        elif action == "OCCUPY":
            steal = p1["territory"] * 0.25
            p1["territory"] -= steal; p2["colony"] += steal; current_ap -= 2
            s["logs"].insert(0, f"🤖 {p2['name']}：占領。領土をデジタル植民地化した。")
            
        if p2["power"] >= 30 or p1["territory"] <= 0: break

    s["turn"] += 1
    p1["power"] += get_income(p1)
    p1["shield"] = False
    s["ap"] = get_max_ap(p1)
    s["phase"] = "PLAYER"

# --- プレイヤー操作 ---
st.divider()
if p1["power"] < 30 and p1["territory"] > 0 and p2["power"] < 30 and p2["territory"] > 0:
    st.subheader(f"TURN {s['turn']} | 残りAP: {s['ap']}")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    if c1.button("🔥 軍拡 (AP1)"):
        p1["military"] += 3; s["ap"] -= 1; s["logs"].insert(0, "🛠️ 軍拡：戦力が増強された。")
    if c2.button("💎 軍縮 (AP1)"):
        p1["power"] += 5; s["ap"] -= 1; s["logs"].insert(0, "📊 軍縮：経済成長を優先。")
    if c3.button("🛡️ 防衛 (AP1)"):
        p1["shield"] = True; p1["military"] = max(0, p1["military"]-2); s["ap"] -= 1; s["logs"].insert(0, "🛡️ 防衛：盾を構えた。")
    if c4.button("⚔️ 攻撃 (AP1)"):
        dmg = p1["military"] * 0.4
        if p2["shield"]: dmg = 0; p2["shield"] = False; s["logs"].insert(0, "💥 攻撃！...だがAIの盾に防がれた！")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"💥 攻撃！AIの領土を{dmg:.1f}破壊！")
        s["ap"] -= 1
    if s["ap"] >= 2:
        if c5.button("🚀 占領 (AP2)"):
            steal = p2["territory"] * 0.2
            p2["territory"] -= steal; p1["colony"] += steal; s["ap"] -= 2
            s["logs"].insert(0, f"🚀 占領！AIのデータを{steal:.1f}奪った！")

    if s["ap"] <= 0:
        if st.button("AIのターンへ転送"):
            run_ai_turn()
            st.rerun()
else:
    if p1["power"] >= 30 or p2["territory"] <= 0:
        st.balloons()
        st.success("🎉 人類の勝利！神を越えた！")
    else:
        st.error("💀 敗北。人類の歴史は幕を閉じた。")
    if st.button("再挑戦"):
        st.session_state.clear()
        st.rerun()

st.write("### 📜 戦記ログ")
for log in s["logs"][:8]:
    st.write(log)
