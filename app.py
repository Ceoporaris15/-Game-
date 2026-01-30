import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：真・最終形態", layout="wide")
st.title("⚔️ 国家間Game会改：Overdrive")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：最終プロトコル起動。人類の敗北を計算済みです。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

# --- 強化された計算ロジック ---
def get_income(player):
    return (player["military"] * player["territory"]) * 0.12

def get_max_ap(player):
    # 植民地7ごとにAP+1
    return 2 + int(player["colony"] / 7)

# --- AI：超・最適解エンジン ---
def ai_logic_god():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの優先順位：常に「最短の勝利」と「相手の妨害」を天秤にかける
    # 1. フィニッシュ：軍縮連打で勝てるなら実行
    if p2["power"] + (s["ai_ap"] * 7) >= GOAL:
        action = "ECONOMY"
    # 2. 殺戮：一撃で相手の領土を0にできるなら攻撃
    elif (p2["military"] * 0.45) >= p1["territory"]:
        action = "ATTACK"
    # 3. リソース破壊：相手の領土が10以上かつ自分のAPが2以上なら占領
    elif p1["territory"] >= 10 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 4. カウンター：相手が軍拡し、軍事差をつけられたら防衛
    elif p1["military"] > p2["military"] + 3 and not p2["shield"]:
        action = "DEFEND"
    # 5. 成長：自分の軍事が不足しているなら軍拡（維持費を厭わない）
    elif p2["military"] < 30:
        action = "MILITARY"
    # 6. 牽制：それ以外は攻撃で相手の領土を削る
    else:
        action = "ATTACK"

    # AIアクション実行
    if action == "MILITARY":
        p2["military"] += 5; p2["power"] -= 2.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。戦力差で圧殺する構えです。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。経済勝利への最短演算を実行中。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛。あなたの攻撃を逆手に取る戦略です。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.45
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"]-3.0)
            s["logs"].insert(0, "🔴 AI：攻撃！あなたの盾を粉砕し、軍事に打撃を与えました。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：攻撃！領土に{dmg:.1f}の甚大な被害。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.25; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：占領。あなたのリソースを完全に奪取しました。")

def player_step(cmd):
    # アクション実行
    if cmd == "MILITARY": p1["military"] += 5; p1["power"] -= 2.0; s["logs"].insert(0, "🔵 あなた：軍拡（維持費-2.0）")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 あなた：軍縮（国力+7.0）")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 あなた：防衛体勢。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: 
            p2["shield"] = False; p2["military"] = max(0, p2["military"]-3.0)
            s["logs"].insert(0, "🔵 あなた：攻撃！AIの防衛網により軍事に反動。")
        else: 
            p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 あなた：攻撃！AI領土に{dmg:.1f}の損害。")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 あなた：占領を強行。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # AIの即時応答
    ai_logic_god()
    
    # ターンリセット
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI描画 ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/GOAL, 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"行動残数: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (DEUS)")
    st.progress(min(p2['power']/GOAL, 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= GOAL or p1["territory"] <= 0 or p2["power"] >= GOAL or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= GOAL or p2["territory"] <= 0) else "AI"
    if winner == "AI": st.error("人類の終焉。AIが新たな文明を定義しました。")
    else: st.success("歴史的勝利。あなたの知略が機械の計算を超えました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
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
