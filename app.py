import streamlit as st
import random

st.set_page_config(page_title="DEUS: Total War WMD", layout="wide")
st.title("⚔️ 国家間Game：殲滅の50年（終末の足音）")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 50.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"territory": 150.0, "military": 80.0, "colony": 30.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 殲滅戦プロトコル継続。AIの大量破壊兵器(WMD)に警戒せよ。"],
        "player_ap": 2,
        "ai_ap": 4,
        "wmd_charging": False # AIの大量破壊兵器チャージフラグ
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- バランス調整済み計算式 ---
def get_max_ap(player, is_ai=False):
    if is_ai:
        if player["territory"] > 200: return 2
        if player["territory"] > 120: return 3
        return 4
    # 占領の強さを下方修正（15→20ごとにAP増加）
    return 2 + int(player["colony"] / 20)

# --- AI：大量破壊兵器を隠し持つ殲滅ロジック ---
def ai_logic_wmd(player_last_action):
    if s["ai_ap"] <= 0:
        s["ai_ap"] = get_max_ap(p2, True)
        p2["shield"] = False

    # 1. 大量破壊兵器(WMD)の発射プロセス
    if s["wmd_charging"]:
        # プレイヤーが「攻撃」をしていれば、30%の確率で阻止される
        if player_last_action == "ATTACK" and random.random() < 0.3:
            s["logs"].insert(0, "✅ SYSTEM：あなたの攻撃によりAIのWMD発射シーケンスが停止しました！")
            s["wmd_charging"] = False
        else:
            dmg = p1["territory"] * 0.5 # 領土の半分を破壊
            p1["territory"] -= dmg
            s["logs"].insert(0, f"☢️ AI：大量破壊兵器発射。あなたの領土の50%({dmg:.1f})が消滅しました。")
            s["wmd_charging"] = False
        s["ai_ap"] -= 1

    # 2. WMDのチャージ開始（10%の確率、または30ターン以降のピンチ時）
    elif not s["wmd_charging"] and (random.random() < 0.1 or (s["turn"] >= 30 and p2["territory"] < 100)):
        s["wmd_charging"] = True
        s["logs"].insert(0, "⚠️ ALERT：DEUSが大量破壊兵器を起動中。次ターンの発射を阻止せよ。")
        s["ai_ap"] -= 1

    # 3. 通常の戦略ロジック
    else:
        # 50ターン以降は市場開放（強奪）を優先
        if s["turn"] >= 50:
            action = "MARKET_OPEN"
        elif player_last_action == "MILITARY" and not p2["shield"]:
            action = "DEFEND"
        elif p2["territory"] < 80:
            action = "RECOVER"
        else:
            action = "ATTACK"

        if action == "MARKET_OPEN":
            steal = p1["territory"] * 0.3
            p1["territory"] -= steal; p2["territory"] += steal; s["ai_ap"] -= 1
            s["logs"].insert(0, f"🔴 AI：市場開放。領土{steal:.1f}を強制接収。")
        elif action == "DEFEND":
            p2["shield"] = True; s["ai_ap"] -= 1
            s["logs"].insert(0, "🔴 AI：防衛。迎撃態勢を整えています。")
        elif action == "RECOVER":
            p2["territory"] += 15.0; s["ai_ap"] -= 1
            s["logs"].insert(0, "🔴 AI：国家再生。領土を再建しています。")
        elif action == "ATTACK":
            dmg = p2["military"] * 0.25
            if p1["shield"]: 
                dmg *= 0.1
                s["logs"].insert(0, "🔴 AI：攻撃。防衛網が被害を抑制。")
            else:
                s["logs"].insert(0, f"🔴 AI：爆撃。領土に{dmg:.1f}のダメージ。")
            p1["territory"] = max(0, p1["territory"] - dmg)
            s["ai_ap"] -= 1

def player_step(cmd):
    if cmd == "MILITARY": p1["military"] += 7; s["logs"].insert(0, "🔵 You：軍事力増強")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🔵 You：防衛態勢（通常攻撃を90%カット）")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.5
        if p2["shield"]: 
            p2["shield"] = False; s["logs"].insert(0, "🔵 You：攻撃（AIの盾を破壊）")
        else: 
            p2["territory"] -= dmg; s["logs"].insert(0, f"🔵 You：攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        # 占領の強さを下方修正：奪える割合を減少
        steal = min(p2["territory"] * 0.10, 15.0)
        p2["territory"] -= steal; p1["colony"] += steal; p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 You：占領。植民地を拡大。")
    
    s["player_ap"] -= 2 if cmd == "OCCUPY" else 1
    ai_logic_wmd(cmd)
    
    if s["player_ap"] <= 0:
        s["player_ap"] = get_max_ap(p1)
        s["turn"] += 1; p1["shield"] = False

# --- UI描画 ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player")
    st.metric("領土 (Life)", f"{p1['territory']:.1f}")
    st.metric("軍事力", f"{p1['military']:.1f}")
    st.caption(f"AP: {s['player_ap']} | 🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 DEUS")
    if s["wmd_charging"]:
        st.error("☢️ WMD CHARGING NOW...")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.caption(f"AI AP: {s['ai_ap']}")

st.divider()

if p1["territory"] <= 0:
    st.error("【滅亡】あなたの国家は灰燼に帰しました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【覇権】超大国DEUSの支配を終わらせました！")
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
