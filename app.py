import streamlit as st
import random

st.set_page_config(page_title="DEUS: Awakened Giant", layout="wide")
st.title("⚔️ 国家間Game：覚醒する巨人")

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 80.0, "military": 10.0, "colony": 0.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 200.0, "military": 50.0, "colony": 40.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 監視開始。AIは現在、軍事力50で待機中。"],
        "wmd_charging": False,
        "ai_awakened": False # AIの覚醒フラグ
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- AI：脅威検知・覚醒ロジック ---
def ai_logic_awakening(player_last_action):
    # 覚醒判定
    if not s["ai_awakened"]:
        if p1["military"] > 40 or p1["territory"] > 120 or player_last_action == "NUKE":
            s["ai_awakened"] = True
            s["logs"].insert(0, "🔴 WARNING: DEUSが脅威を認定。軍拡制限を解除しました。")

    for i in range(2): # AIは2回行動
        if p2["territory"] <= 0: break
        
        # 1. 特殊兵器シーケンス（覚醒時のみ確率アップ）
        if s["wmd_charging"]:
            if player_last_action == "ATTACK" and random.random() < 0.4:
                s["logs"].insert(0, "✅ SYSTEM: 阻止成功！AIの兵器システムを一時ダウン。")
                s["wmd_charging"] = False
            else:
                dmg = p1["territory"] * 0.5
                p1["territory"] -= dmg
                s["logs"].insert(0, f"☢️ AI: 最終兵器使用。領土の50%({dmg:.1f})が消滅。")
                s["wmd_charging"] = False
            continue

        # 2. 覚醒時の軍拡行動（AIが本気なら必ず軍事力を上げる）
        if s["ai_awakened"] and random.random() < 0.6:
            gain = random.randint(15, 25)
            p2["military"] += gain
            s["logs"].insert(0, f"🔴 AI: 全力軍拡中。軍事力が {gain} 上昇。")
            continue

        # 3. 通常の戦略
        if i == 0 and player_last_action == "ATTACK" and not p2["shield"]:
            p2["shield"] = True
            s["logs"].insert(0, "🔴 AI: 防御展開。")
        elif p2["territory"] < 100:
            p2["territory"] += 20.0
            s["logs"].insert(0, "🔴 AI: 領土修復。")
        elif not s["wmd_charging"] and s["ai_awakened"] and random.random() < 0.2:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: DEUSが最終兵器をチャージ開始！")
        else:
            # 覚醒していると攻撃が激化
            power_mult = 1.8 if s["ai_awakened"] else 0.7
            dmg = p2["military"] * 0.2 * power_mult
            if p1["shield"]: dmg *= 0.1
            p1["territory"] = max(0, p1["territory"] - dmg)
            s["logs"].insert(0, f"🔴 AI: 攻撃（出力:{'最大' if s['ai_awakened'] else '通常'}）。ダメージ {dmg:.1f}")

def player_step(cmd):
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
            s["logs"].insert(0, "🔵 Player: 攻撃（AIの盾を破壊）")
        else: 
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🔵 Player: 攻撃（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        steal = min(p2["territory"] * 0.1, 15.0)
        p2["territory"] -= steal
        p1["colony"] += steal
        p1["territory"] += steal * 0.4
        s["logs"].insert(0, "🔵 Player: 領土奪還。")
    elif cmd == "SPY":
        if random.random() < 0.1:
            dmg = p2["territory"] * 0.5
            p2["territory"] -= dmg
            s["logs"].insert(0, f"🕵️‍♂️ SPY SUCCESS!! AIの領土-{dmg:.1f}")
        else:
            s["logs"].insert(0, "🕵️‍♂️ SPY FAIL: スパイは排除されました。")
    elif cmd == "NUKE":
        dmg = p2["territory"] * 0.8
        p2["territory"] -= dmg
        p1["nuke_point"] = 0
        s["logs"].insert(0, f"🚀 Player: 核使用！！AI領土-{dmg:.1f}")
    
    ai_logic_awakening(cmd)
    s["turn"] += 1
    p1["shield"] = False

# --- UI ---
col1, col2 = st.columns(2)
with col1:
    st.header(f"Turn: {s['turn']}")
    st.subheader("🟦 Player (1 Action)")
    st.metric("領土 (Life)", f"{p1['territory']:.1f}")
    st.metric("軍事力", f"{p1['military']:.1f}")
    st.metric("核開発", f"{p1['nuke_point']}/100")
    st.progress(min(p1['nuke_point']/100, 1.0))

with col2:
    status_text = "👿 AWAKENED" if s["ai_awakened"] else "😴 SLEEPING"
    st.subheader(f"🟥 DEUS ({status_text})")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")
    st.metric("領土", f"{p2['territory']:.1f}")
    st.metric("軍事力", f"{p2['military']:.1f}")
    st.caption("AIは常に2連続行動を行います")

st.divider()

if p1["territory"] <= 0:
    st.error("【敗北】国家は滅亡しました。")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
elif p2["territory"] <= 0:
    st.success("【完全勝利】覚醒した巨人を打ち破りました！")
    if st.button("リスタート"): st.session_state.clear(); st.rerun()
else:
    c = st.columns(5)
    if c[0].button("軍拡(1)"): player_step("MILITARY"); st.rerun()
    if c[1].button("防衛(1)"): player_step("DEFEND"); st.rerun()
    if c[2].button("攻撃(1)"): player_step("ATTACK"); st.rerun()
    if c[3].button("占領(1)"): player_step("OCCUPY"); st.rerun()
    if c[4].button("🕵️‍♂️ スパイ(1)"): player_step("SPY"); st.rerun()
    
    if p1["nuke_point"] >= 100:
        if st.button("🚀 核兵器発射 (AI領土8割滅)", type="primary", use_container_width=True):
            player_step("NUKE"); st.rerun()

st.write("---")
for log in s["logs"][:8]: st.text(log)
