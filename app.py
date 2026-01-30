import streamlit as st
import random

st.set_page_config(page_title="DEUS: Spy & War", layout="wide")
st.title("⚔️ 国家間Game：スパイと核の均衡")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 80.0, "military": 10.0, "colony": 0.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 200.0, "military": 100.0, "colony": 40.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 監視開始。AIは現在、あなたを「低脅威」と見なしています。"],
        "wmd_charging": False,
        "ai_serious": False # AIの本気モードフラグ
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- AI：段階的覚醒ロジック ---
def ai_logic_adaptive(player_last_action):
    # 拮抗判定：AIの領土がプレイヤーの1.5倍を下回ると本気モード
    if p2["territory"] < p1["territory"] * 1.5 and not s["ai_serious"]:
        s["ai_serious"] = True
        s["logs"].insert(0, "🔴 ALERT: DEUSが「最大脅威」を検知。本気モードに移行します。")

    for i in range(2):
        if p2["territory"] <= 0: break
        
        # 1. WMD発射シーケンス
        if s["wmd_charging"]:
            # プレイヤーが「攻撃」または「スパイ成功」で阻止可能
            if player_last_action == "ATTACK" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 攻撃によりAIのWMDを無力化！")
                s["wmd_charging"] = False
            else:
                dmg = p1["territory"] * 0.5
                p1["territory"] -= dmg
                s["logs"].insert(0, f"☢️ AI: 本気の核攻撃。領土の50%({dmg:.1f})を喪失。")
                s["wmd_charging"] = False
            continue

        # 2. WMDチャージ（本気モード時は確率アップ）
        chance = 0.5 if s["ai_serious"] else 0.1
        if not s["wmd_charging"] and (p2["territory"] < 70 or p1["nuke_point"] > 80):
            if random.random() < chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "⚠️ ALERT: DEUSが最終兵器をチャージ中！")
                continue

        # 3. 通常行動
        # 本気モードならダメージ係数がアップ
        power_mult = 1.5 if s["ai_serious"] else 0.6
        
        if i == 0 and player_last_action == "ATTACK" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御展開。")
        elif p2["territory"] < 100 and s["ai_serious"]:
            p2["territory"] += 20.0
            s["logs"].insert(0, "🔴 AI: 急速自己修復。")
        else:
            dmg = p2["military"] * 0.2 * power_mult
            if p1["shield"]: dmg *= 0.1
            p1["territory"] = max(0, p1["territory"] - dmg)
            s["logs"].insert(0, f"🔴 AI: 爆撃（出力:{'最大' if s['ai_serious'] else '通常'}）。領土ダメージ {dmg:.1f}")

def player_step(cmd):
    spy_success = False
    if cmd == "MILITARY": 
        p1["military"] += 8
        p1["nuke_point"] += 10 
        s["logs"].insert(0, f"🔵 Player: 軍拡（核ポイント:{p1['nuke_point']}）")
    elif cmd == "DEFEND": 
        p1["shield"] = True
        s["logs"].insert(0, "🔵 Player: 全面防衛。")
    elif cmd == "ATTACK":
        dmg = p1["military"] * 0.5
        if p2["shield"]: 
            p2["shield"] = False
            s["logs"].insert(0, "🔵 Player: 攻撃（盾粉砕）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.1, 15.0)
        p2["territory"] -= steal
        p1["colony"] += steal
        p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 Player: 占領による領土奪還。")
    elif cmd == "SPY":
        if random.random() < 0.1: # 10分の1
            spy_success = True
            dmg = p2["territory"] * 0.5 # AIの核が自分に誤爆
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🕵️‍♂️ SPY SUCCESS!! AIの核を内部爆発させました（AI領土-{dmg:.1f}）")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL: スパイは捕らえられ、情報は遮断されました。")
    elif cmd == "NUKE":
        dmg = p2["territory"] * 0.8
        p2["territory"] -= dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"🚀 Player: 自国製核兵器発射！！AI領土-{dmg:.1f}")
    
    # AIの行動
    ai_logic_adaptive(cmd)
    s["turn"] += 1
    p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player (1 Action)")
    st.metric("領土 (Life)", f"{p1['territory']:.1f}")
    st.metric("核開発", f"{p1['nuke_point']}/100")
    st.progress(min(p1['nuke_point']/100, 1.0))
    st.caption(f"軍事力: {p1['military']:.1f}")

with col2:
    st.subheader("🟥 DEUS" + (" (AWAKENED)" if s["ai_serious"] else ""))
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.write(f"モード: {'👿 本気' if s['ai_serious'] else '😴 油断'}")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】あなたは歴史から抹消されました。")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】超大国を内側と外側から崩壊させました！")
    if st.button("再起動"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if c[3].button("占領(1)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("🕵️‍♂️ スパイ(1)"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        if st.button("🚀 核兵器発射", type="primary", use_container_width=True):
            player_step("NUKE"); st.rerun()

st.write("---")
for log in s["logs"][:8]: st.text(log)
