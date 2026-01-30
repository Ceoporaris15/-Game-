import streamlit as st
import random
import os

# --- 司令部環境設定 ---
st.set_page_config(page_title="COMMAND", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #000; color: #0f0; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #0f0; background-color: #000; color: #0f0;
        height: 3.5em; border-radius: 0px; font-weight: bold;
    }
    .stProgress > div > div > div > div { background-color: #0f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 司令部：画像データベース（ファイル名の正確な一致が必要です） ---
IMAGES = {
    "DEFENSE": "Screenshot 2026-01-31 08.08.27.png",
    "RESEARCH": "Screenshot 2026-01-31 08.09.06.png",
    "MARCH": [
        "Screenshot 2026-01-31 08.09.51.png",
        "Screenshot 2026-01-31 08.09.28.png"
    ],
    "LOST": "Screenshot 2026-01-31 08.08.44.png",
    "NUCLEAR": "Screenshot 2026-01-31 08.12.07.png"
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 300.0, "milit": 50.0},
        "turn": 1, "ap": 2, "start": False,
        "monitor": None,
        "m_cnt": 0, "d_cnt": 0, "b_lost": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def exec_command(cmd):
    s["monitor"] = None
    if cmd == "DEV":
        p1["milit"] += 25; p1["atom"] += 20
        if p1["atom"] >= 150: s["monitor"] = IMAGES["RESEARCH"]
    elif cmd == "DEF":
        p1["shield"] = True; s["d_cnt"] += 1
        if s["d_cnt"] % 3 == 0: s["monitor"] = IMAGES["DEFENSE"]
    elif cmd == "ATK":
        s["m_cnt"] += 1
        if s["m_cnt"] % 3 == 0: s["monitor"] = random.choice(IMAGES["MARCH"])
        p2["land"] -= (p1["milit"] * 0.4) + (p1["buffer"] * 0.5)
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20; stl = max(p2["land"] * 0.2, 30.0)
            p2["land"] -= stl; p1["buffer"] += stl
    elif cmd == "NUKE":
        s["monitor"] = IMAGES["NUCLEAR"]
        p2["land"] *= 0.2; p1["atom"] = 0

    s["ap"] -= 1
    if s["ap"] <= 0:
        if p2["land"] > 0:
            dmg = p2["milit"] * 0.2
            if p1["buffer"] > 0:
                p1["buffer"] -= dmg
                if p1["buffer"] <= 0 and not s["b_lost"]:
                    s["monitor"] = IMAGES["LOST"]; s["b_lost"] = True
            else: p1["land"] -= dmg
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- メインインターフェース ---
if not s["start"]:
    st.title("IRON COMMAND")
    if st.button("INITIALIZE"): s["start"] = True; st.rerun()
else:
    # 記録画像ジャック
    if s["monitor"]:
        # ファイルの存在確認
        if os.path.exists(s["monitor"]):
            st.image(s["monitor"], use_container_width=True)
        else:
            st.error(f"【通信途絶】記録画像ファイルが見つかりません: {s['monitor']}")
            st.info("GitHubのリポジトリに画像ファイルが正しくアップロードされているか確認してください。")
        
        if st.button("RETURN TO COMMAND"):
            s["monitor"] = None
            st.rerun()
        st.stop()

    # 指令端末画面
    st.write(f"ENEMY INTEGRITY: {p2['land']:.1f}")
    st.progress(max(0.0, min(p2['land']/400, 1.0)))

    c1, c2, c3 = st.columns(3)
    c1.metric("HOME", f"{p1['land']:.0f}")
    c2.metric("ZONE", f"{p1['buffer']:.0f}")
    c3.metric("AP", f"{s['ap']}")

    if p1["land"] <= 0 or p2["land"] <= 0:
        st.error("MISSION OVER")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        if p1["atom"] >= 200:
            if st.button("🚀 EXECUTE FINAL DETERRENT", type="primary"): exec_command("NUKE"); st.rerun()
        
        btn1, btn2 = st.columns(2)
        if btn1.button("🛠 DEV"): exec_command("DEV"); st.rerun()
        if btn2.button("🛡 DEF"): exec_command("DEF"); st.rerun()
        if btn1.button("⚔️ ATK"): exec_command("ATK"); st.rerun()
        if btn2.button("🚩 OCC"): exec_command("OCC"); st.rerun()

    st.caption(f"TURN: {s['turn']} | MILITARY: {p1['milit']} | ATOM: {p1['atom']}")
