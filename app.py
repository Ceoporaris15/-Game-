import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：DEUS Overdrive", layout="wide")
st.title("⚔️ 国家間Game会改：DEUS 不可侵領域")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：演算開始。同点、相打ち、すべて私の勝利として処理されます。"],
        "player_ap": 2,
        "ai_ap": 2
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    return 2 + int(player["colony"] / 6)

# --- AI：絶対勝利・相打ち上等アルゴリズム ---
def ai_logic_dominance():
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの優先順位：プレイヤーの勝利を潰しながら自分もゴールする
    # 1. 確実な勝利：自分が100に届くなら、何をおいても軍縮（経済）
    if p2["power"] + (s["ai_ap"] * 7) >= GOAL:
        action = "ECONOMY"
    # 2. プレイヤーへのトドメ：相手の領土が瀕死なら全力攻撃
    elif (p2["military"] * 0.5) >= p1["territory"]:
        action = "ATTACK"
    # 3. 妨害占領：プレイヤーが国力勝利しそうなら領土を奪って成長を止める
    elif p1["power"] >= 80 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 4. 成長抑制：プレイヤーの領土が10以上なら占領
    elif p1["territory"] >= 10 and s["ai_ap"] >= 2:
        action = "OCCUPY"
    # 5. 防衛：相手の軍事が高く、自分が死ぬリスクがある時のみ
    elif p1["military"] > p2["military"] + 5 and not p2["shield"]:
        action = "DEFEND"
    # 6. その他：軍拡か攻撃
    else:
        action = "MILITARY" if p2["military"] < 25 else "ATTACK"

    if action == "MILITARY":
        p2["military"] += 5; p2["power"] -= 2.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。維持費を払いながら圧倒的戦力を構築。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。経済勝利へ加速。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：防衛。あなたのあがきを封じます。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.5
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"] - 5.0)
            s["logs"].insert(0, "🔴 AI：攻撃！シールドごと軍事力を破砕。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：攻撃！領土に{dmg:.1f}の損害。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.3; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：強欲な占領。あなたのリソースは私のものです。")

def player_step(cmd):
    # プレイヤーアクション
    if cmd == "MILITARY": p1["military"] += 5; p1["power"] -= 2.0; s["logs"].insert(0, "🔵 Player：軍拡")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 Player：軍縮")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 Player：防衛")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: p2["shield"] = False; p2["military"] = max(0, p2["military"] - 4.0); s["logs"].insert(0, "🔵 Player：攻撃（AIに防御された）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 Player：攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 Player：占領")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # プレイヤーの1アクションごとにAIが即応
    ai_logic_dominance()
    
    # ターン処理
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- 判定ロジック：同点はAI勝利 ---
def check_winner():
    p1_win = p1["power"] >= GOAL or p2["territory"] <= 0
    p2_win = p2["power"] >= GOAL or p1["territory"] <= 0
    
    # 同時達成、またはAIのみ達成ならAI勝利
    if p1_win and p2_win: return "AI"
    if p2_win: return "AI"
    if p1_win: return "Player"
    return None

# --- UI描画 ---
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

winner = check_winner()
if winner:
    if winner == "AI":
        st.error("【敗北】同時到達につき、システム優先権に基づきAIの勝利を確定します。")
    else:
        st.success("【奇跡】AIの妨害を潜り抜け、単独勝利を達成しました。")
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
