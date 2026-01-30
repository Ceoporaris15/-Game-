import streamlit as st
import random

st.set_page_config(page_title="国家間Game会改：完全対策システム", layout="wide")
st.title("⚔️ 国家間Game会改：完全対策DEUS")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["AI：全選択肢への対策を完了。論理的敗北をお楽しみください。"],
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
    return 2 + int(player["colony"] / 7)

# --- AI：全選択肢対策アルゴリズム ---
def ai_logic_perfect_counter(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2)
        s["ai_ap"] = get_max_ap(p2)
        p2["shield"] = False

    # AIの意思決定マトリックス
    # 1. 確実な勝利演算
    if p2["power"] + (s["ai_ap"] * 7) >= GOAL:
        action = "ECONOMY"
    # 2. プレイヤーの行動に対する直撃カウンター
    elif player_last_action == "MILITARY":
        # プレイヤーの軍拡に対し、即座に「防衛」を張り攻撃を無効化しつつ軍事を削る
        action = "DEFEND" if not p2["shield"] else "OCCUPY"
    elif player_last_action == "ATTACK":
        # プレイヤーの攻撃後、手薄な領土を「占領」してリソースを奪う
        action = "OCCUPY" if s["ai_ap"] >= 2 else "MILITARY"
    elif player_last_action == "DEFEND":
        # プレイヤーの防衛（攻撃待ち）に対し、攻撃をせず「軍縮」で経済差をつける
        action = "ECONOMY"
    elif player_last_action == "ECONOMY":
        # プレイヤーの経済優先に対し、最大火力で「攻撃」し成長の土台（領土）を破壊する
        action = "ATTACK"
    elif player_last_action == "OCCUPY":
        # プレイヤーの占領に対し、自分も「占領」し返してAP差をつけさせない
        action = "OCCUPY" if s["ai_ap"] >= 2 else "ATTACK"
    else:
        action = "MILITARY"

    # AIアクション実行
    if action == "MILITARY":
        p2["military"] += 4; p2["power"] -= 1.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍拡。戦力を均衡、またはそれ以上に保ちます。")
    elif action == "ECONOMY":
        p2["power"] += 7; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：軍縮。経済効率であなたを突き放します。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 AI：カウンター防衛。あなたの軍備増強を無効化します。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.45
        if p1["shield"]: 
            p1["shield"] = False; p1["military"] = max(0, p1["military"] - 4.0)
            s["logs"].insert(0, "🔴 AI：強襲。シールドを破壊し、軍事力を減衰させました。")
        else: 
            p1["territory"] -= dmg
            s["logs"].insert(0, f"🔴 AI：精密攻撃。領土を{dmg:.1f}削り、国力を低下させました。")
        s["ai_ap"] -= 1
    elif action == "OCCUPY":
        steal = p1["territory"] * 0.25; p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 2
        s["logs"].insert(0, f"🔴 AI：占領工作。あなたの手数を奪い、自らの支配を広げます。")

def player_step(cmd):
    # プレイヤーの行動
    if cmd == "MILITARY": p1["military"] += 4; p1["power"] -= 1.0; s["logs"].insert(0, "🔵 Player：軍拡")
    elif cmd == "ECONOMY": p1["power"] += 7; s["logs"].insert(0, "🔵 Player：軍縮")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 Player：防衛")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: p2["shield"] = False; p2["military"] = max(0, p2["military"] - 3.0); s["logs"].insert(0, "🔵 Player：攻撃（防御され軍事損傷）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 Player：攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.2; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 Player：占領")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    
    # プレイヤーの行動を引数に渡し、AIが「完全対策」を実行
    ai_logic_perfect_counter(cmd)
    
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
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (DEUS)")
    st.progress(min(p2['power']/GOAL, 1.0), text=f"国力: {p2['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 🚩 植民地: {p2['colony']:.1f}")

st.divider()

p1_win = p1["power"] >= GOAL or p2["territory"] <= 0
p2_win = p2["power"] >= GOAL or p1["territory"] <= 0

if p1_win or p2_win:
    winner = "AI" if p2_win else "Player"
    if winner == "AI": st.error("【敗北】AIの論理から逃れることはできませんでした。")
    else: st.success("【奇跡】AIの対策を力でねじ伏せました！")
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
