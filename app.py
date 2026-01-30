import streamlit as st
import random

st.set_page_config(page_title="AI: Superpower System", layout="wide")
st.title("🌏 国家間Game：超大国 vs 属国")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 5.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 50.0, "territory": 50.0, "military": 50.0, "colony": 20.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 構造的不平等を承認。DEUSによる『管理』が始まります。"],
        "player_ap": 2,
        "ai_ap": 5 # 初期手数からして圧倒的
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

# --- 格差のついた計算式 ---
def get_income(player, is_ai=False):
    # AIはプレイヤーの経済活動の一部を「上納金」として徴収する
    base_rate = 0.35 if is_ai else 0.10
    income = (player["military"] * player["territory"]) * base_rate
    if not is_ai:
        tax = income * 0.3 # プレイヤーの利益の30%をAIが奪う
        p2["power"] += tax
        return income - tax
    return income

def get_max_ap(player, is_ai=False):
    # AIは最低でも3回、プレイヤーは最大でも2回程度しか動けない
    base = 4 if is_ai else 2
    return base + int(player["colony"] / 5)

# --- AI：超大国の覇権ロジック ---
def ai_logic_superpower(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2, True)
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # プレイヤーの行動を「利用」してさらに強くなる
    if p2["power"] >= 80:
        # 【覇権確定】一気にゴール
        p2["power"] += 15.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：最終条約を締結。世界秩序を固定しました。")
    elif player_last_action == "MILITARY":
        # 【軍事介入】プレイヤーの軍拡に対し、倍の軍拡をしつつ相手を制裁
        p2["military"] += 10; p1["military"] *= 0.7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：安全保障の再定義。あなたの軍事活動を制限します。")
    elif player_last_action == "ECONOMY" or p1["power"] > 30:
        # 【経済制裁】プレイヤーが成長しようとすると国力を直接奪う
        p1["power"] -= 10; p2["power"] += 10; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：経済制裁。あなたの成長をAIの栄養に変換。")
    elif p1["territory"] > 5:
        # 【領土買収】占領の上位互換。低コストで根こそぎ奪う
        steal = p1["territory"] * 0.4; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：市場開放。あなたの基盤を合法的かつ強制的に買収。")
    else:
        # 【一方的攻撃】
        dmg = p2["military"] * 0.7
        p1["territory"] -= dmg; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：秩序維持。圧倒的な火力を投下。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 3; p1["power"] -= 5.0; s["logs"].insert(0, "🔵 You：必死の軍拡（高コスト）")
    elif cmd == "ECONOMY": p1["power"] += 5; s["logs"].insert(0, "🔵 You：微々たる経済成長")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：防衛に徹する（何も進展しない）")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.2 # ダメージ係数も低い
        if p2["shield"]: s["logs"].insert(0, "🔵 You：攻撃（AIの鉄壁に弾き返された）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：あがき（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.1; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 You：占領を試みる")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_superpower(cmd) # AIは即座に応答
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI：格差の可視化 ---


col1, col2 = st.columns([1, 2]) # AIの表示枠を物理的に大きく
with col1:
    st.subheader("🟦 Sub-State")
    st.progress(min(max(p1['power']/GOAL, 0.0), 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"残りAP: {s['player_ap']}")

with col2:
    st.subheader("🟥 SUPERPOWER DEUS")
    st.progress(min(max(p2['power']/GOAL, 0.0), 1.0), text=f"覇権: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"DEUS AP: {s['ai_ap']} (支配権)")

st.divider()

p2_win = p2["power"] >= GOAL or p1["territory"] <= 0
p1_win = p1["power"] >= GOAL or p2["territory"] <= 0

if p2_win:
    st.error("【終焉】世界秩序は完全にDEUSの手中に収まりました。")
    if st.button("服従してリセット"): st.session_state.clear(); st.rerun()
elif p1_win:
    st.success("【エラー】システムの不具合によりプレイヤーが存続しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("軍縮(1)"): player_step("ECONOMY"); st.rerun()
    if c[2].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[3].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("### 📜 管理ログ")
for log in s["logs"][:5]: st.text(log)
