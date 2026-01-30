import streamlit as st
import random

st.set_page_config(page_title="DEUS: 50 Turn Judgement", layout="wide")
st.title("🌏 国家間Game：超大国 vs 属国（第50ターンの審判）")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"power": 10.0, "territory": 10.0, "military": 5.0, "colony": 0.0, "shield": False},
        "p2": {"power": 60.0, "territory": 60.0, "military": 60.0, "colony": 30.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 長期管理プロトコル。第50ターンに全リソースの強制執行を予定。"],
        "player_ap": 2,
        "ai_ap": 4 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 500.0 # 長期戦に合わせて目標値を引き上げ

def get_income(player, is_ai=False):
    base_rate = 0.40 if is_ai else 0.15
    income = (player["military"] * player["territory"]) * base_rate
    if not is_ai:
        # 徴収拒絶の確率は極めて低いが、50ターンあれば何度か発生する
        tax_rate = 0.0 if (p1["shield"] and random.random() < 0.15) else 0.35
        tax = income * tax_rate
        p2["power"] += tax
        return income - tax
    return income

def get_max_ap(player, is_ai=False):
    if is_ai:
        # 超巨大化したAIは、後半（パワー400以上）で組織の肥大化によりAPが低下する隙を見せる
        base = 3 if player["power"] > 400 else 4
        return base + int(player["colony"] / 15)
    return 2 + int(player["colony"] / 10)

# --- AI：50ターン照準・絶対覇権ロジック ---
def ai_logic_50(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2, True)
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # --- 50ターンの審判ロジック ---
    if p2["power"] >= GOAL:
        p2["power"] = GOAL; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：覇権確定。世界はDEUSの計算通りに再構成されました。")

    # 【最恐】第50ターン以降：真・市場開放
    elif s["turn"] >= 50 and p1["territory"] > 1.0:
        steal = p1["territory"] * 0.5 # 50%の領土を一気に奪う
        p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：第50ターン。審判の日。全市場を強制開放・吸収します。")

    # プレイヤーの反抗（軍拡）への徹底制裁
    elif player_last_action == "MILITARY" and p1["military"] > 20:
        p1["military"] = max(1.0, p1["military"] - 10.0); s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：軍事抑制。超大国の秩序を乱す武装を解除。")

    # 長期的な経済格差の維持
    elif p2["power"] < p1["power"] + 100:
        p2["power"] += 20.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：経済覇権の拡大。差を圧倒的なものにします。")

    # 領土を1.0以下にしない程度の嫌がらせ
    else:
        dmg = p2["military"] * 0.2
        if p1["territory"] - dmg > 1.0:
            p1["territory"] -= dmg
            s["logs"].insert(0, "🔴 DEUS：微細介入。管理可能な範囲に領土を調整。")
        else:
            p2["power"] += 15.0; s["ai_ap"] -= 1
            s["logs"].insert(0, "🔴 DEUS：経済投資。市場の成熟を待っています。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 5; p1["power"] -= 5.0; s["logs"].insert(0, "🔵 You：長き戦いに向けた軍拡")
    elif cmd == "ECONOMY": p1["power"] += 10; s["logs"].insert(0, "🔵 You：沈黙の経済成長")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：盾を構え、時を待つ")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.4
        if p2["shield"]: s["logs"].insert(0, "🔵 You：攻撃（AIの防壁は揺るがない）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：乾坤一擲の反撃（{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.1; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 You：植民地を広げAPを蓄える")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_50(cmd)
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI：不気味なカウントダウン ---
col1, col2 = st.columns([1, 2])
with col1:
    st.header(f"Turn: {s['turn']}")
    st.progress(min(max(p1['power']/GOAL, 0.0), 1.0), text=f"国力: {p1['power']:.1f}/{GOAL}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    
    countdown = 50 - s['turn']
    if countdown > 0:
        st.warning(f"審判の日まで：あと {countdown} ターン")
    else:
        st.error("🚨 市場開放プロトコル：執行中 🚨")

with col2:
    st.subheader("🟥 SUPERPOWER DEUS (神の領域)")
    st.progress(min(max(p2['power']/GOAL, 0.0), 1.0), text=f"覇権: {p2['power']:.1f}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"DEUS AP: {s['ai_ap']} (支配権限)")

st.divider()

# 勝利判定
if p2["power"] >= GOAL or p1["territory"] < 1.0:
    st.error("【支配完了】50ターンの忍従の末、人類はDEUSに屈しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p1["power"] >= GOAL or p2["territory"] < 1.0:
    st.success("【歴史的勝利】50年の雌伏を経て、ついに超大国を打倒しました！")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("軍縮(1)"): player_step("ECONOMY"); st.rerun()
    if c[2].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[3].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("### 📜 支配の記録")
for log in s["logs"][:8]: st.text(log)
