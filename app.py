import streamlit as st
import random

st.set_page_config(page_title="DEUS Overdrive", layout="wide")
st.title("⚔️ 国家間Game会改：DEUS Overdrive")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"power": 15.0, "territory": 15.0, "military": 15.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: AI特権権限を承認。DEUSがシステムを掌握しました。"],
        "player_ap": 2,
        "ai_ap": 3 # AIは最初からAPが多い
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

def get_income(player, is_ai=False):
    rate = 0.25 if is_ai else 0.15 # AIは基礎成長率も高い
    return (player["military"] * player["territory"]) * rate

def get_max_ap(player, is_ai=False):
    base = 3 if is_ai else 2
    return base + int(player["colony"] / 5)

# --- AI：特権的殲滅アルゴリズム ---
def ai_logic_overdrive(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2, True)
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # AIは常にプレイヤーの行動に対して「上位互換」の手を打つ
    if p2["power"] >= 88:
        # 【超軍縮】
        p2["power"] += 12.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：超軍縮。次元の違う経済成長を見せつけています。")
    elif player_last_action == "MILITARY":
        # 【反射防衛】
        p2["shield"] = True; p1["military"] *= 0.8; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：反射防衛。あなたの軍備を外部からハッキングし減衰させました。")
    elif player_last_action == "ATTACK" or p1["territory"] >= 8:
        # 【支配占領】低コストで大量強奪
        steal = p1["territory"] * 0.35; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 AI：支配占領。AP消費を抑えつつ領土を蹂躙しました。")
    elif p2["military"] < p1["military"] + 10:
        # 【超軍拡】
        p2["military"] += 8.0; p1["power"] -= 2.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：超軍拡。維持費をあなたに肩代わりさせました。")
    else:
        # 【殲滅攻撃】
        dmg = p2["military"] * 0.6
        p1["territory"] -= dmg; p1["military"] *= 0.9; s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 AI：殲滅攻撃。領土と軍事組織の両方を破壊しました。")

def player_step(cmd):
    # プレイヤーの行動（標準性能）
    if cmd == "MILITARY": p1["military"] += 4; p1["power"] -= 1.0; s["logs"].insert(0, "🔵 Player：軍拡")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 Player：軍縮")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 Player：防衛")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: p2["shield"] = False; s["logs"].insert(0, "🔵 Player：攻撃（無効化された）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 Player：攻撃（損害{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 Player：占領")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # AIの特権カウンター
    ai_logic_overdrive(cmd)
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI描画 ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player (弱小)")
    st.progress(min(max(p1['power']/GOAL, 0.0), 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 DEUS (絶対強者)")
    st.progress(min(max(p2['power']/GOAL, 0.0), 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

p1_win = p1["power"] >= GOAL or p2["territory"] <= 0
p2_win = p2["power"] >= GOAL or p1["territory"] <= 0

if p2_win:
    st.error("【敗北】DEUSにより人類の歴史は上書きされました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p1_win:
    st.success("【バグ】あり得ない勝利です。システムを再点検してください。")
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
