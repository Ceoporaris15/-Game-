import streamlit as st
import random

st.set_page_config(page_title="DEUS: Three Powers", layout="centered")

# --- カスタム演出用スタイル（核兵器のみに使用） ---
st.markdown("""
    <style>
    .nuke-target-box {
        border: 2px solid #ff0000;
        background-color: rgba(255, 0, 0, 0.1);
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    .nuke-circle-static {
        width: 100px; height: 100px; border-radius: 50%;
        border: 4px double #ff0000; margin: 0 auto 10px;
        position: relative;
    }
    .nuke-circle-static::before {
        content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 2px; background: #ff0000;
    }
    .nuke-circle-static::after {
        content: ''; position: absolute; left: 50%; top: 0; width: 2px; height: 100%; background: #ff0000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 画像アセット ---
IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["SYSTEM: 難易度を選択して開始してください。"],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"{'☢️' if is_wmd else '💥'} Damage: {dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance: s["wmd_charging"] = True
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["effect"] = None # 演出リセット
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
    elif cmd == "DEFEND":
        p1["shield"] = True
    elif cmd == "MARCH":
        # 進軍時の画像演出(s["effect"] = "AIR")を削除しました
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"🔵 MARCH: AI領土 -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal
    elif cmd == "NUKE":
        s["effect"] = "NUKE" # 核演出フラグ
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["logs"].insert(0, "☢️🚀 FINAL JUDGEMENT!!")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI ---
if s["difficulty"] is None:
    st.subheader("🌐 SELECT DIFFICULTY")
    cols = st.columns(3)
    if cols[0].button("EASY"): s["difficulty"] = "小国 (Easy)"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("NORMAL"): s["difficulty"] = "大国 (Normal)"; st.rerun()
    if cols[2].button("HARD"): s["difficulty"] = "超大国 (Hard)"; s["ai_awakened"] = True; st.rerun()
else:
    # --- 核兵器発射時のみ表示される演出 ---
    if s["effect"] == "NUKE":
        st.markdown("""
            <div class="nuke-target-box">
                <div class="nuke-circle-static"></div>
                <strong style="color: #ff0000; font-size: 1.2rem;">CRITICAL TARGET LOCKED</strong>
            </div>
            """, unsafe_allow_html=True)
        st.image(IMG_NUKE, caption="☢️ JUDGEMENT DAY", use_container_width=True)

    # AI エリア
    st.subheader(f"🟥 AI: {p2['territory']:.1f}")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")

    st.write("---")

    # プレイヤー エリア
    st.subheader(f"🟦 Player (AP: {s['player_ap']})")
    c1, c2 = st.columns(2)
    c1.metric("領土", f"{p1['territory']:.1f}")
    c2.metric("占領地", f"{p1['colony']:.1f}")
    
    st.caption(f"Military: {p1['military']}/100 | Nuke: {p1['nuke_point']}/200")
    st.progress(min(p1['nuke_point']/200, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 核兵器発射", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        c = st.columns(2)
        if c[0].button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.rerun()
        if c[1].button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.rerun()
        if c[0].button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if c[1].button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    for log in s["logs"][:3]: st.text(log)
