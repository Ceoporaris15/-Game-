import streamlit as st
import random

st.set_page_config(page_title="DEUS: Total War", layout="wide")
st.title("⚔️ 国家間Game：殲滅の50年")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 30.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"territory": 100.0, "military": 60.0, "colony": 30.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 殲滅戦プロトコル。相手の領土を0にした側が覇者となります。"],
        "player_ap": 2,
        "ai_ap": 4 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 殲滅戦用の調整 ---
def get_max_ap(player, is_ai=False):
    if is_ai:
        # AIの弱点：領土が広すぎると維持コストでAPが減少する（プレイヤーの逆転チャンス）
        if player["territory"] > 150: return 2
        if player["territory"] > 100: return 3
        return 4
    # プレイヤーは「占領」で手数を増やすことが生存戦略の鍵
    return 2 + int(player["colony"] / 15)

# --- AI：冷徹な殲滅ロジック ---
def ai_logic_annihilator(player_last_action):
    if s["ai_ap"] <= 0:
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # AIの優先順位：破壊 ＞ 占領 ＞ 防衛
    # 1. 第50ターン：市場開放（領土強奪）解禁
    if s["turn"] >= 50:
        action = "MARKET_OPEN"
    # 2. プレイヤーが軍拡した際、AIはカウンター防衛
    elif player_last_action == "MILITARY" and not p2["shield"]:
        action = "DEFEND"
    # 3. プレイヤーの領土が脆い（20以下）なら畳み掛ける
    elif p1["territory"] < 20:
        action = "ATTACK"
    # 4. 自身の領土をさらに広げて「手数」の基礎を作る（序盤）
    elif p2["territory"] < 150:
        action = "OCCUPY"
    else:
        action = "ATTACK"

    if action == "MARKET_OPEN":
        steal = p1["territory"] * 0.35
        p1["territory"] -= steal; p2["territory"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 DEUS：市場開放。領土{steal:.1f}を強制接収。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：防衛。あなたの軍拡を警戒しています。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.3
        if p1["shield"]: 
            dmg *= 0.1
            s["logs"].insert(0, "🔴 DEUS：攻撃。あなたの防衛網が被害を最小限に抑えました。")
        else:
            s["logs"].insert(0, f"🔴 DEUS：猛攻。領土に{dmg:.1f}のダメージ。")
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        p2["territory"] += 10.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：領土拡張。支配領域を広げています。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 8; s["logs"].insert(0, "🔵 You：軍事力増強（次なる一撃へ）")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：防衛態勢（被害を大幅軽減）")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.6
        if p2["shield"]: 
            p2["shield"] = False; s["logs"].insert(0, "🔵 You：攻撃（AIの盾を粉砕したがダメージ無効）")
        else: 
            p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：反撃（AI領土へ{dmg:.1f}ダメージ！）")
    elif cmd == "OCCUPY":
        # AIの領土から「植民地」として奪う（AP増加に繋がる）
        steal = min(p2["territory"] * 0.15, 20.0)
        p2["territory"] -= steal; p1["colony"] += steal; p1["territory"] += steal * 0.5
        s["logs"].insert(0, "🔵 You：領土奪還。植民地として組み込みました。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_annihilator(cmd)
    
    if s["player_ap"] <= 0:
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- 画面描画 ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player")
    st.metric("領土 (生命線)", f"{p1['territory']:.1f}")
    st.metric("軍事力", f"{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 SUPERPOWER DEUS")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} (領土が広いと管理低下)")

st.divider()

# 勝利判定：領土が0になったら終了
if p1["territory"] <= 0:
    st.error("【壊滅】あなたの領土は地図から消滅しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】超大国DEUSを地図から消し去りました！")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(4)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[3].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("---")
for log in s["logs"][:8]: st.text(log)
