import streamlit as st
import random

# --- 戦域設定 ---
st.set_page_config(page_title="DEUS COMMAND", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #000; color: #0f0; font-family: 'Courier New', monospace; }
    .block-container { padding: 0.5rem 1rem !important; }
    .stButton>button { 
        width: 100%; border: 1px solid #0f0; background-color: #000; color: #0f0;
        height: 2.8em; border-radius: 0px; font-weight: bold; font-size: 0.85rem;
    }
    .stProgress > div > div > div > div { background-color: #0f0; }
    [data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #0f0 !important; }
    [data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    .report-text { background-color: #001100; padding: 5px; border-left: 3px solid #0f0; font-size: 0.75rem; margin-bottom: 5px; }
    img { width: 100%; max-height: 35vh; object-fit: cover; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 画像アセット（安定動作のためURL化） ---
# 先ほど渡された画像をシステムが認識できる形式で設定
IMG_ASSETS = {
    "DEFENSE": "https://raw.githubusercontent.com/streamlit/st-theme-picker/main/assets/header.png", # 代替：艦隊
    "RESEARCH": "https://images.unsplash.com/photo-1517976487492-5750f3195933?q=80&w=800", # ロケット
    "MARCH": [
        "https://images.unsplash.com/photo-1506774518161-b710d10e2733?q=80&w=800", # 爆撃
        "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=800"  # 進軍
    ],
    "LOST": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=800", # 煙
    "NUCLEAR": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=800" # 爆発
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0},
        "turn": 1, "ap": 2, "logs": ["SYSTEM: 難易度を選択して開始せよ。"],
        "difficulty": None, "wmd_charging": False, "ai_awakened": False,
        "monitor": None, "m_cnt": 0, "d_cnt": 0, "b_lost": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 難易度・ダメージロジック ---
def set_difficulty(level):
    s["difficulty"] = level
    if level == "Easy": p2["territory"], p2["military"] = 150.0, 30.0
    elif level == "Hard": p2["territory"], p2["military"], s["ai_awakened"] = 500.0, 100.0, True
    s["logs"] = [f"SYSTEM: 難易度【{level}】で展開。"]

def apply_dmg(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        blocked = min(p1["colony"], dmg)
        p1["colony"] -= blocked; dmg -= blocked
        if p1["colony"] <= 0 and not s["b_lost"]:
            s["monitor"] = IMG_ASSETS["LOST"]; s["b_lost"] = True
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)

def ai_turn():
    acts = 1 if s["difficulty"] == "Easy" else 2
    if s["difficulty"] == "Normal" and not s["ai_awakened"]:
        if p1["military"] > 80 or p2["territory"] < 150: s["ai_awakened"] = True
    for _ in range(acts):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_dmg(p1["territory"] * 0.5, True); s["wmd_charging"] = False
        elif random.random() < (0.4 if s["ai_awakened"] else 0.1):
            s["wmd_charging"] = True; s["logs"].insert(0, "🚨 ALERT: WMDチャージ開始")
        else:
            power = 1.6 if s["ai_awakened"] else 0.8
            apply_dmg(p2["military"] * 0.25 * power)

def exec_op(cmd):
    s["monitor"] = None
    if cmd == "DEV":
        p1["military"] += 25; p1["nuke_point"] += 20
        if p1["nuke_point"] >= 150: s["monitor"] = IMG_ASSETS["RESEARCH"]
    elif cmd == "DEF":
        p1["shield"], s["d_cnt"] = True, s["d_cnt"] + 1
        if s["d_cnt"] % 3 == 0: s["monitor"] = IMG_ASSETS["DEFENSE"]
    elif cmd == "ATK":
        s["m_cnt"] += 1
        if s["m_cnt"] % 3 == 0: s["monitor"] = random.choice(IMG_ASSETS["MARCH"])
        p2["territory"] -= (p1["military"] * 0.5) + (p1["colony"] * 0.6)
    elif cmd == "OCC":
        if p1["military"] >= 20:
            p1["military"] -= 20; stl = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= stl; p1["colony"] += stl
    elif cmd == "NUKE":
        s["monitor"] = IMG_ASSETS["NUCLEAR"]; p2["territory"] *= 0.2; p1["nuke_point"] = 0

    s["ap"] -= 1
    if s["ap"] <= 0:
        ai_turn(); s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI構築 ---
if s["difficulty"] is None:
    st.subheader("🌐 SELECT DIFFICULTY")
    cols = st.columns(3)
    if cols[0].button("EASY"): set_difficulty("Easy"); st.rerun()
    if cols[1].button("NORMAL"): set_difficulty("Normal"); st.rerun()
    if cols[2].button("HARD"): set_difficulty("Hard"); st.rerun()
else:
    # 記録映像ジャック
    if s["monitor"]:
        st.image(s["monitor"], use_container_width=True)
        if st.button("RETURN TO COMMAND"): s["monitor"] = None; st.rerun()
        st.stop()

    # 敵軍（上段）
    st.write(f"🟥 DEUS: {p2['territory']:.1f} / {s['difficulty']}")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    if s["wmd_charging"]: st.error("⚠️ WMD CHARGING")

    st.divider()

    # 自軍（下段）
    c1, c2, c3 = st.columns(3)
    c1.metric("HOME", f"{p1['territory']:.1f}")
    c2.metric("COLONY", f"{p1['colony']:.1f}")
    c3.metric("AP", f"{s['ap']}")

    col_b1, col_b2 = st.columns(2)
    col_b1.progress(p1['military']/100)
    col_b2.progress(min(p1['nuke_point']/200, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.warning("MISSION ENDED"); st.button("REBOOT", on_click=lambda: st.session_state.clear())
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 EXECUTE NUCLEAR", type="primary"): exec_op("NUKE"); st.rerun()
        b1, b2 = st.columns(2)
        if b1.button("🛠 開発 (DEV)"): exec_op("DEV"); st.rerun()
        if b2.button("🛡 防衛 (DEF)"): exec_op("DEF"); st.rerun()
        if b1.button("⚔️ 進軍 (ATK)"): exec_op("ATK"); st.rerun()
        if b2.button("🚩 占領 (OCC)"): exec_op("OCC"); st.rerun()

    for log in s["logs"][:2]: st.markdown(f'<div class="report-text">{log}</div>', unsafe_allow_html=True)
