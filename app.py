import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：知略の勝利", layout="wide")
st.title("⚔️ 国家間Game会改：Overdrive")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：分析開始。知略なき力は自滅を招くでしょう。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

# --- バランス調整された計算式 ---
def get_income(player):
    # 軍事と領土の積。軍拡しすぎると維持費で効率が落ちるよう調整
    return (player["military"] * player["territory"]) * 0.12

def get_max_ap(player):
    # 占領の価値を高める（植民地7ごとにAP+1）
    return 2 + int(player["colony"] / 7)

# --- AI：最適解だが「隙」を突ける思考 ---
def ai_logic_smart():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの優先順位（プレイヤーの行動に反応）
    # 1. 相手の領土が瀕死ならトドメ
    if (p2["military"] * 0.4) >= p1["territory"]:
        action = "ATTACK"
    # 2. プレイヤーが軍拡して「攻撃」の構えなら「防衛」でリソースを浪費させる
    elif p1["military"] > p2["military"] + 4 and not p2["shield"]:
        action = "DEFEND"
    # 3. 自分の国力が目標に近いなら「軍縮」で逃げ切りを狙う
    elif p2["power"] > 80:
        action = "ECONOMY"
    # 4. プレイヤーが防衛している隙に「占領」でリソースを奪う
    elif p1["shield"] and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 5. それ以外は状況に応じた「軍拡」または「攻撃」
    else:
        action = "MILITARY" if p2["military"] < 25 else "ATTACK"

    # AI実行
    if action == "MILITARY":
        p2["military"] += 4; p2["power"] -= 1.5; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。維持費により国力成長が微減。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。経済成長を最優先。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛展開。こちらの出方を伺っている。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.4
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"]-2.5)
            s["logs"].insert(0, "🔴 AI：攻撃！あなたの盾で防いだが軍事にダメージ。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：攻撃！領土に{dmg:.1f}の損害。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.2; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：占領。リソースが奪い取られた。")

def player_step(cmd):
    # アクション実行
    if cmd == "MILITARY": p1["military"] += 4; p1["power"] -= 1.5; s["logs"].insert(0, "🔵 あなた：軍拡（維持費発生）")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 あなた：軍縮（国力+7）")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 あなた：防衛。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: 
            p2["shield"] = False; p2["military"] = max(0, p2["military"]-2.5)
            s["logs"].insert(0, "🔵 あなた：攻撃！AIの盾に阻まれ軍事に反動。")
        else: 
            p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 あなた：攻撃！AI領土に{dmg:.1f}の被害。")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 あなた：占領成功。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # AIのカウンター
    ai_logic_smart()
    
    # ターン終了処理
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UIレイアウト ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/GOAL, 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"残りAP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (Deus)")
    st.progress(min(p2['power']/GOAL, 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"待機AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= GOAL or p1["territory"] <= 0 or p2["power"] >= GOAL or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= GOAL or p2["territory"] <= 0) else "AI"
    st.header(f"【結果】勝者：{winner}")
    if st.button("再戦する"): st.session_state.clear(); st.rerun()
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
