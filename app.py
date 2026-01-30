import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：DEUS", layout="wide")
st.title("⚔️ 国家間Game会改：Overdrive")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：演算完了。あなたに勝機はありません。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

# --- ロジック定数 ---
def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    # 植民地6ごとにAP+1（AIが占領を狙う動機を強化）
    return 2 + int(player["colony"] / 6)

# --- AI：プレイヤー殲滅アルゴリズム ---
def ai_logic_overkill():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの最優先判断：キル・オア・ウィン
    # 1. 経済的勝利：あとAP数回で100に届くなら、迷わず軍縮を連打
    if p2["power"] + (s["ai_ap"] * 7) >= GOAL:
        action = "ECONOMY"
    # 2. 物理的殲滅：プレイヤーの領土を0にできるなら全APで攻撃
    elif (p2["military"] * 0.5) >= p1["territory"]:
        action = "ATTACK"
    # 3. リソース強奪：プレイヤーが領土を広げたら、即座に「占領」でAPボーナスを奪う
    elif p1["territory"] >= 8 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 4. カウンター防衛：プレイヤーの軍事が急増したときのみ「防衛」し、無駄撃ちさせる
    elif p1["military"] > p2["military"] + 5 and not p2["shield"]:
        action = "DEFEND"
    # 5. 基盤強化：軍事が25以下なら「軍拡」を優先（維持費-2を恐れない）
    elif p2["military"] < 25:
        action = "MILITARY"
    # 6. 嫌がらせ：それ以外は、プレイヤーの国力成長（領土）を削る
    else:
        action = "ATTACK"

    # AIアクション実行
    if action == "MILITARY":
        p2["military"] += 5; p2["power"] -= 2.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。戦力を圧倒的優位に保ちます。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。勝利への最終演算を実行。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛。あなたの攻撃は予測済みです。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.5
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"] - 4.0)
            s["logs"].insert(0, "🔴 AI：攻撃！あなたの盾を粉砕し、戦力を大きく削りました。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：猛攻！領土に{dmg:.1f}の甚大な損害。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.3; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：占領。あなたの領土を搾取し、手数を増やしました。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 5; p1["power"] -= 2.0; s["logs"].insert(0, "🔵 Player：軍拡（維持費-2.0）")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 Player：軍縮（国力+7.0）")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 Player：防衛体勢。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: 
            p2["shield"] = False; p2["military"] = max(0, p2["military"] - 4.0)
            s["logs"].insert(0, "🔵 Player：攻撃！AIの盾に防がれ、軍事に反動。")
        else: 
            p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 Player：攻撃！AI領土に{dmg:.1f}の損害。")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 Player：占領実行。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # プレイヤーの1行動に対し、AIが即座に最適解を出す
    ai_logic_overkill()
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- 画面描画 ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/GOAL, 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"残りAP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (DEUS)")
    st.progress(min(p2['power']/GOAL, 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= GOAL or p1["territory"] <= 0 or p2["power"] >= GOAL or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= GOAL or p2["territory"] <= 0) else "AI"
    if winner == "AI": st.error("【敗北】AIの論理が人類を凌駕しました。")
    else: st.success("【奇跡】あなたがAIを上回りました。")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
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
