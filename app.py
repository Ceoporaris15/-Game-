import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：真・最終兵器", layout="wide")
st.title("⚔️ 国家間Game会改：Overdrive")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["最終兵器AI：デウスがオンラインになりました。人類に勝機はありません。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    return 2 + int(player["colony"] * 0.1)

# --- AI：超思考・殲滅アルゴリズム ---
def ai_logic_extreme():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # 1. 【即死判定】相手の領土を削り切れるなら全リソースで攻撃
    if (p2["military"] * 0.4) >= p1["territory"]:
        action = "ATTACK"
    # 2. 【経済勝利王手】国力が90以上なら軍縮連打で勝ち逃げ
    elif p2["power"] >= 85:
        action = "ECONOMY"
    # 3. 【AP剥奪】プレイヤーの領土が豊か（12以上）なら「占領」で成長を破壊
    elif p1["territory"] >= 12 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 4. 【カウンター要塞】プレイヤーが軍拡して攻撃の構えなら「防衛」
    elif p1["military"] > p2["military"] + 2 and not p2["shield"] and random.random() < 0.8:
        action = "DEFEND"
    # 5. 【軍備増強】攻撃の威力が低いなら「軍拡」を優先
    elif p2["military"] < 30:
        action = "MILITARY"
    # 6. 【嫌がらせ】それ以外は一貫して領土を削る
    else:
        action = "ATTACK"

    if action == "MILITARY":
        p2["military"] += 5; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。戦力を圧倒的優位に保とうとしています。")
    elif action == "ECONOMY":
        p2["power"] += 5; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。経済勝利へのカウントダウンを開始。")
    elif action == "DEFEND":
        p2["shield"] = True; p2["military"] = max(0, p2["military"]-2); s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛。あなたの攻撃を完全に無効化する構えです。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.4
        if p1["shield"]: 
            p1["shield"] = False
            s["logs"].insert(0, "🔴 AI：攻撃！あなたの盾を粉砕しました。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：攻撃！領土に{dmg:.1f}の致命的な損害。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.25; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：占領！あなたのリソースをAIの血肉に変えました。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 4; s["logs"].insert(0, "🔵 あなた：軍拡。")
    elif cmd == "ECONOMY": p1["power"] += 5; s["logs"].insert(0, "🔵 あなた：軍縮。")
    elif cmd == "DEFEND": p1["shield"] = True; p1["military"] = max(0, p1["military"]-2); s["logs"].insert(0, "🔵 あなた：防衛。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 あなた：攻撃！AIの盾に阻まれました。")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 あなた：攻撃！AIに{dmg:.1f}の損害。")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 あなた：占領。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # AIの即時応答
    ai_logic_extreme()
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1
        p1["shield"] = False

# --- 表示画面 ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/100, 1.0), text=f"国力: {p1['power']:.1f}/100")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"残りAP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (DEUS)")
    st.progress(min(p2['power']/100, 1.0), text=f"国力: {p2['power']:.1f}/100")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"待機AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= 100 or p1["territory"] <= 0 or p2["power"] >= 100 or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= 100 or p2["territory"] <= 0) else "AI"
    if winner == "AI": st.error("人類の敗北です。AIが世界を再定義しました。")
    else: st.success("奇跡の勝利！AIの予測を超えました。")
    if st.button("再戦"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡"): player_step("MILITARY"); st.rerun()
    if c[1].button("軍縮"): player_step("ECONOMY"); st.rerun()
    if c[2].button("防衛"): player_step("DEFEND"); st.rerun()
    if c[3].button("攻撃"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領"): player_step("OCCUPY"); st.rerun()

st.write("### 📜 バトルログ")
for log in s["logs"][:5]: st.text(log)
