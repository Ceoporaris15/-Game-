import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：Overdrive", layout="wide")
st.title("⚔️ 国家間Game会改：冷徹な支配者")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：戦術演算開始。時間をかけて、あなたの基盤を解体します。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    return 2 + int(player["colony"] / 7)

# --- AI：じわじわ追い詰める戦略ロジック ---
def ai_logic_strategic():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの思考：いきなり倒さず、有利な状況を積み上げる
    # 1. 確実なフィニッシュ（条件達成が目前なら実行）
    if p2["power"] >= 93:
        action = "ECONOMY"
    elif (p2["military"] * 0.45) >= p1["territory"]:
        action = "ATTACK"
    # 2. 妨害・破壊工作：プレイヤーのAP増加の芽（領土）を少しずつ摘む
    elif p1["territory"] > 12 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 3. 経済的嫌がらせ：プレイヤーが稼いでいるなら、自分も経済を回して差を広げる
    elif p1["power"] > p2["power"] + 5:
        action = "ECONOMY"
    # 4. 軍事的威圧：自分の軍事が低いと舐められないよう、着実に強化
    elif p2["military"] < p1["military"] + 5:
        action = "MILITARY"
    # 5. 牽制攻撃：プレイヤーに「防衛」を使わせてAPを無駄遣いさせる
    else:
        action = "ATTACK"

    if action == "MILITARY":
        p2["military"] += 4; p2["power"] -= 1.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。じわじわと戦力の圧を強めています。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。着実に国力の差を広げています。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛。あなたの反撃を冷静に受け流します。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.4
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"] - 2.0)
            s["logs"].insert(0, "🔴 AI：小規模攻撃。あなたの防衛リソースを削りました。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：牽制。領土を{dmg:.1f}破壊し、基盤を揺さぶります。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.2; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：工作員による占領。少しずつ支配権を奪っています。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 4; p1["power"] -= 1.0; s["logs"].insert(0, "🔵 あなた：軍拡")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 あなた：軍縮")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 あなた：防衛")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: p2["shield"] = False; p2["military"] = max(0, p2["military"] - 3.0); s["logs"].insert(0, "🔵 あなた：攻撃（防がれた）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 あなた：攻撃（損害{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 あなた：占領")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_strategic() # 即時応答
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/GOAL, 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (DEUS)")
    st.progress(min(p2['power']/GOAL, 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

# 勝利判定：同点ルール廃止（先に条件を満たした方が勝利。同時なら現時点ではPlayer優先だが、AIがそうさせないよう動く）
p1_win = p1["power"] >= GOAL or p2["territory"] <= 0
p2_win = p2["power"] >= GOAL or p1["territory"] <= 0

if p1_win or p2_win:
    winner = "AI" if p2_win else "Player"
    if winner == "AI": st.error("【敗北】AIに全リソースを掌握されました。")
    else: st.success("【勝利】AIの支配を打ち破りました！")
    if st.button("再戦"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("軍縮(1)"): player_step("ECONOMY"); st.rerun()
    if c[2].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[3].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("---")
for log in s["logs"][:5]: st.text(log)
