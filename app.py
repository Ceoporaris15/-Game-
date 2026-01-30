import streamlit as st
import random

st.set_page_config(page_title="DEUS: Strategic Dominance", layout="wide")
st.title("🌏 国家間Game：超大国 vs 属国（第15ターンの審判）")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"power": 10.0, "territory": 10.0, "military": 5.0, "colony": 0.0, "shield": False},
        "p2": {"power": 50.0, "territory": 50.0, "military": 50.0, "colony": 20.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 監視プロトコル作動中。第15ターンに市場開放を予定しています。"],
        "player_ap": 2,
        "ai_ap": 4 
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]
GOAL = 100.0

def get_income(player, is_ai=False):
    base_rate = 0.35 if is_ai else 0.12
    income = (player["military"] * player["territory"]) * base_rate
    if not is_ai:
        tax_rate = 0.0 if (p1["shield"] and random.random() < 0.2) else 0.3
        tax = income * tax_rate
        p2["power"] += tax
        return income - tax
    return income

def get_max_ap(player, is_ai=False):
    if is_ai:
        # AIが後半になるほど管理が複雑化し、わずかに隙ができる
        base = 3 if player["power"] > 95 else 4
        return base + int(player["colony"] / 10)
    return 2 + int(player["colony"] / 8)

# --- AI：第15ターン照準・最適化ロジック ---
def ai_logic_timed(player_last_action):
    if s["ai_ap"] <= 0:
        p2["power"] += get_income(p2, True)
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # --- 行動優先順位 ---
    # 1. フィニッシュ（100達成）
    if p2["power"] >= 93:
        p2["power"] += 7.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：最終合意を形成。勝利は確定しました。")
        
    # 2. 第15ターン以降：市場開放（領土買収）解禁
    elif s["turn"] >= 15 and p1["territory"] > 2.5:
        steal = p1["territory"] * 0.3
        p1["territory"] -= steal; p2["colony"] += steal; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：第15ターン。市場開放を強制執行。あなたの基盤を吸収します。")
        
    # 3. カウンター制裁（軍拡への反応）
    elif player_last_action == "MILITARY" and p1["military"] > 10:
        p1["military"] = max(1.0, p1["military"] - 4.0); s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：安全保障制裁。不均衡な武装を解除させました。")
        
    # 4. 経済加速
    elif p2["power"] < p1["power"] + 20:
        p2["power"] += 10.0; s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：経済覇権。一気に差を広げます。")
        
    # 5. 通常攻撃（牽制）
    else:
        dmg = p2["military"] * 0.3
        p1["territory"] = max(1.0, p1["territory"] - dmg)
        s["ai_ap"] -= 1
        s["logs"].insert(0, "🔴 DEUS：秩序維持。小規模な軍事介入を実行。")

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 4; p1["power"] -= 3.0; s["logs"].insert(0, "🔵 You：必死の軍拡")
    elif cmd == "ECONOMY": p1["power"] += 6; s["logs"].insert(0, "🔵 You：耐え忍ぶ経済成長")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：防衛（徴収回避）")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.3
        if p2["shield"]: s["logs"].insert(0, "🔵 You：攻撃（AIに弾かれた）")
        else: p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：反撃（{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = p2["territory"] * 0.15; p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🔵 You：占領工作")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_timed(cmd)
    
    if s["player_ap"] <= 0:
        p1["power"] += get_income(p1)
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI ---


col1, col2 = st.columns([1, 2])
with col1:
    st.subheader(f"🟦 Turn: {s['turn']}")
    st.progress(min(max(p1['power']/GOAL, 0.0), 1.0), text=f"国力: {p1['power']:.1f}")
    st.metric("領土", f"{p1['territory']:.1f}", f"軍事:{p1['military']:.1f}")

with col2:
    st.subheader("🟥 SUPERPOWER DEUS")
    st.progress(min(max(p2['power']/GOAL, 0.0), 1.0), text=f"覇権: {p2['power']:.1f}")
    st.metric("領土", f"{p2['territory']:.1f}", f"軍事:{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']} | 第15ターンまで：あと {max(0, 15 - s['turn'])} ターン")

st.divider()

# 勝利判定
if p2["power"] >= GOAL or p1["territory"] < 1.0:
    st.error("【支配完了】DEUSが新たな世界秩序を宣言しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p1["power"] >= GOAL or p2["territory"] < 1.0:
    st.success("【奇跡】1%の勝機を掴み、超大国の計画を狂わせました！")
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
