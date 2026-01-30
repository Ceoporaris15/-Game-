import streamlit as st
import random

st.set_page_config(page_title="DEUS: Strategic Resistance", layout="wide")
st.title("🌏 国家間Game：逆転の50年")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"power": 20.0, "territory": 20.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"power": 80.0, "territory": 80.0, "military": 60.0, "colony": 30.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 戦略的自律権を確認。第50ターンまでに構造を解析せよ。"],
        "player_ap": 2,
        "ai_ap": 4 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 500.0

def get_income(player, is_ai=False):
    # AIは成長率が高いが、プレイヤーは「知略」によるボーナスがある
    base_rate = 0.40 if is_ai else 0.20
    income = (player["military"] * player["territory"]) * base_rate
    
    if not is_ai:
        tax_rate = 0.35
        # シールド展開中、低確率で税金を軍事費として横流しできる（試行錯誤要素）
        if p1["shield"] and random.random() < 0.3:
            s["logs"].insert(0, "🎁 闇市場：徴収された資金を軍事力に変換しました！")
            p1["military"] += (income * tax_rate) * 0.5
            return income
        
        tax = income * tax_rate
        p2["power"] += tax
        return income - tax
    return income

def get_max_ap(player, is_ai=False):
    if is_ai:
        # AIの弱点：肥大化による効率低下（400以上でAP激減）
        if player["power"] > 450: return 2
        if player["power"] > 350: return 3
        return 4
    # プレイヤーは「植民地」を広げることで、AIを超える手数を獲得可能
    return 2 + int(player["colony"] / 12)

# --- AI：強大だが予測可能な「帝国」ロジック ---
def ai_logic_fair_overlord(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2, True)
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # 1. 50ターン目のギミック：プレイヤーの植民地が多いとAIが躊躇する
    if s["turn"] >= 50:
        if p1["colony"] > 50:
            s["logs"].insert(0, "⚠️ DEUS：経済連鎖を懸念し、市場開放を一時見合わせ。")
            action = "ECONOMY"
        else:
            action = "MARKET_OPEN"
    # 2. プレイヤーが軍拡した際、AIは「外交（AP削り）」か「防衛」を選ぶ
    elif player_last_action == "MILITARY":
        action = "DEFEND" if not p2["shield"] else "ECONOMY"
    # 3. プレイヤーが経済優先なら、AIは「徴収強化」
    elif player_last_action == "ECONOMY":
        action = "ATTACK"
    else:
        action = "ECONOMY" if p2["power"] < p1["power"] + 150 else "ATTACK"

    # AIアクション実行
    if action == "MARKET_OPEN":
        steal = p1["territory"] * 0.4
        p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, f"🔴 DEUS：市場開放。領土{steal:.1f}が接収されました。")
    elif action == "ECONOMY":
        p2["power"] += 25.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：経済成長を優先。組織が巨大化しています。")
    elif action == "DEFEND":
        p2["shield"] = True; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：防衛展開。反撃を警戒しています。")
    elif action == "ATTACK":
        dmg = p2["military"] * 0.25
        p1["territory"] = max(1.0, p1["territory"] - dmg)
        s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：通常介入。領土の調整を行いました。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 6; p1["power"] -= 4.0; s["logs"].insert(0, "🔵 You：軍事力強化")
    elif cmd == "ECONOMY": p1["power"] += 12; s["logs"].insert(0, "🔵 You：経済の地盤固め")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：防衛・徴収回避の試み")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.5
        if p2["shield"]: s["logs"].insert(0, "🔵 You：攻撃（防衛網に阻まれた）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：反撃（{dmg:.1f}ダメージ）")
    elif cmd == "OCCUPY":
        # AIの領土が大きいほど占領効率アップ（巨人の足をすくう）
        steal = p2["territory"] * 0.12; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 You：占領により影響力を拡大")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_fair_overlord(cmd)
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UIレイアウト ---


col1, col2 = st.columns([1, 1])
with col1:
    st.header(f"Turn: {s['turn']}")
    st.progress(min(max(p1['power']/GOAL, 0.0), 1.0), text=f"Player: {p1['power']:.1f}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 植民地: {p1['colony']:.1f} (目標50でAIを牽制)")

with col2:
    st.subheader("🟥 DEUS (Empire)")
    st.progress(min(max(p2['power']/GOAL, 0.0), 1.0), text=f"Power: {p2['power']:.1f}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} (肥大化で低下)")

st.divider()

if p2["power"] >= GOAL or p1["territory"] < 1.0:
    st.error("【敗北】帝国の波に飲み込まれました。")
    if st.button("リトライ"): st.session_state.clear(); st.rerun()
elif p1["power"] >= GOAL or p2["territory"] < 1.0:
    st.success("【勝利】あなたの知略が巨大帝国を打倒しました！")
    if st.button("新世界へ"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("軍縮(1)"): player_step("ECONOMY"); st.rerun()
    if c[2].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[3].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if s["player_ap"] >= 2:
        if c[4].button("占領(2)"): player_step("OCCUPY"); st.rerun()

st.write("---")
for log in s["logs"][:6]: st.text(log)
