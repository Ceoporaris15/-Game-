import streamlit as st
import random

# --- ページ設定 ---
st.set_page_config(page_title="COMMAND", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00ff00; font-family: 'Courier New', monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #00ff00; background-color: #000; color: #00ff00;
        height: 3.5em; border-radius: 0px; font-weight: bold;
    }
    .stProgress > div > div > div > div { background-color: #00ff00; }
    /* 画像をスマホ画面にフィットさせる */
    img { width: 100%; max-height: 80vh; object-fit: contain; }
    </style>
    """, unsafe_allow_html=True)

# --- 指定アーカイブソース ---
# ※YouTubeは動画、その他はiframeや画像として処理
SOURCES = {
    "NUCLEAR": "https://www.youtube.com/watch?v=f_2ps6RIR9U",
    "LOST": "https://www.jiji.com/jc/d4?p=ddy601&d=d4_mili",
    "MARCH": [
        "https://www.cnn.co.jp/world/35079451.html",
        "https://www.yomiuri.co.jp/science/20240217-OYT1T50087/"
    ],
    "RESEARCH": "https://www.jiji.com/jc/d4?p=ncl122-jlp05027330&d=d4_mili",
    "DEFENSE": "https://www.mod.go.jp/msdf/about/role/"
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 300.0, "milit": 50.0},
        "turn": 1, "ap": 2, "start": False,
        "show_src": None,
        "m_cnt": 0, "d_cnt": 0, "b_lost": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def exec_op(cmd):
    s["show_src"] = None
    if cmd == "DEV":
        p1["milit"] += 25; p1["atom"] += 20
        if p1["atom"] >= 150: s["show_src"] = SOURCES["RESEARCH"]
    elif cmd == "DEF":
        p1["shield"] = True; s["d_cnt"] += 1
        if s["d_cnt"] % 3 == 0: s["show_src"] = SOURCES["DEFENSE"]
    elif cmd == "ATK":
        s["m_cnt"] += 1
        if s["m_cnt"] % 3 == 0: s["show_src"] = random.choice(SOURCES["MARCH"])
        p2["land"] -= (p1["milit"] * 0.5) + (p1["buffer"] * 0.6)
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20; stl = max(p2["land"] * 0.2, 30.0)
            p2["land"] -= stl; p1["buffer"] += stl
    elif cmd == "NUKE":
        s["show_src"] = SOURCES["NUCLEAR"]
        p2["land"] *= 0.2; p1["atom"] = 0

    s["ap"] -= 1
    if s["ap"] <= 0:
        if p2["land"] > 0:
            dmg = p2["milit"] * 0.2
            if p1["buffer"] > 0:
                p1["buffer"] -= dmg
                if p1["buffer"] <= 0 and not s["b_lost"]:
                    s["show_src"] = SOURCES["LOST"]; s["b_lost"] = True
            else: p1["land"] -= dmg
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- メイン画面 ---
if not s["start"]:
    st.title("STRATEGIC COMMAND")
    if st.button("INITIALIZE"): s["start"] = True; st.rerun()
else:
    # 画像・映像のみの表示モード
    if s["show_src"]:
        if "youtube.com" in s["show_src"]:
            st.video(s["show_src"])
        else:
            # 外部サイトを画像的に表示（埋め込み）
            st.markdown(f'<iframe src="{s["show_src"]}" width="100%" height="500px" style="border:none;"></iframe>', unsafe_allow_html=True)
        
        if st.button("CLOSE ARCHIVE"):
            s["show_src"] = None
            st.rerun()
        st.stop()

    # 司令コンソール（スマホ1画面に集約）
    st.write(f"ENEMY LAND: {p2['land']:.1f}")
    st.progress(max(0.0, min(p2['land']/400, 1.0)))

    c1, c2, c3 = st.columns(3)
    c1.metric("HOME", f"{p1['land']:.1f}")
    c2.metric("ZONE", f"{p1['buffer']:.1f}")
    c3.metric("AP", f"{s['ap']}")

    if p1["land"] <= 0 or p2["land"] <= 0:
        st.write("MISSION END")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        if p1["atom"] >= 200:
            if st.button("🚀 EXECUTE FINAL DETERRENT", type="primary"): exec_op("NUKE"); st.rerun()
        
        col_l, col_r = st.columns(2)
        if col_l.button("🛠 TECH DEV"): exec_op("DEV"); st.rerun()
        if col_r.button("🛡 DEFENSE"): exec_op("DEF"); st.rerun()
        if col_l.button("⚔️ STRIKE"): exec_op("ATK"); st.rerun()
        if col_r.button("🚩 ANNEX"): exec_op("OCC"); st.rerun()

    st.write(f"MILITARY: {p1['milit']:.0f} | ATOM: {p1['atom']:.0f}")
