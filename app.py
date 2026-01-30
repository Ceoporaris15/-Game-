import streamlit as st
import random

# --- 戦域設定 ---
st.set_page_config(page_title="STRATEGIC COMMAND", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        font-weight: bold; height: 3em; border-radius: 0px;
    }
    .stButton>button:hover { border: 1px solid #00ff00; background-color: #002200; }
    .stProgress > div > div > div > div { background-color: #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 1.2rem; }
    .report-text { background-color: #001100; padding: 10px; border-left: 5px solid #00ff00; margin-bottom: 10px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 指定資料アーカイブ ---
ARCHIVE_LINKS = {
    "NUCLEAR": "https://www.youtube.com/watch?v=f_2ps6RIR9U", # 核兵器（記録）
    "LOST": "https://www.jiji.com/jc/d4?p=ddy601&d=d4_mili",    # 緩衝地帯消滅
    "MARCH": [
        "https://www.cnn.co.jp/world/35079451.html",
        "https://www.yomiuri.co.jp/science/20240217-OYT1T50087/"
    ], # 進軍（ランダム）
    "RESEARCH": "https://www.jiji.com/jc/d4?p=ncl122-jlp05027330&d=d4_mili", # 開発
    "DEFENSE": "https://www.mod.go.jp/msdf/about/role/" # 防衛
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 350.0, "milit": 60.0},
        "turn": 1, "ap": 2,
        "logs": ["司令部：作戦準備完了。記録資料の閲覧権限を承認。"],
        "mode_selected": False,
        "action_report": None,
        # カウンター
        "march_count": 0,
        "defense_count": 0,
        "buffer_lost_flag": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 司令部ロジック ---
def apply_damage(dmg):
    if p1["shield"]: dmg *= 0.6
    if p1["buffer"] > 0:
        blocked = min(p1["buffer"], dmg)
        p1["buffer"] -= blocked
        dmg -= blocked
        # 緩衝地帯（植民地）が全滅した時
        if p1["buffer"] <= 0 and not s["buffer_lost_flag"]:
            s["action_report"] = (ARCHIVE_LINKS["LOST"], "🚨 警告：前方防衛線（緩衝地帯）が全滅。本土侵攻を許しました。")
            s["buffer_lost_flag"] = True
    if dmg > 0:
        p1["land"] = max(0, p1["land"] - dmg)

def exec_op(cmd):
    s["action_report"] = None
    
    if cmd == "DEV":
        p1["milit"] += 25.0; p1["atom"] += 20
        # 研究（特殊兵器Pt）が150以上の時のみ流す
        if p1["atom"] >= 150:
            s["action_report"] = (ARCHIVE_LINKS["RESEARCH"], "報告：戦略技術開発の記録。")
            
    elif cmd == "DEF":
        p1["shield"] = True; s["defense_count"] += 1
        # 防衛は3回に一度流す
        if s["defense_count"] % 3 == 0:
            s["action_report"] = (ARCHIVE_LINKS["DEFENSE"], "防衛：領域警備および迎撃任務の記録。")
            
    elif cmd == "ATK":
        s["march_count"] += 1
        # 進軍は3回に一度流す
        if s["march_count"] % 3 == 0:
            link = random.choice(ARCHIVE_LINKS["MARCH"])
            s["action_report"] = (link, "攻勢：進軍および作戦展開の記録。")
        p2["land"] -= (p1["milit"] * 0.5) + (p1["buffer"] * 0.6)
        
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20
            stolen = max(p2["land"] * 0.2, 40.0)
            p2["land"] -= stolen; p1["buffer"] += stolen
            
    elif cmd == "NUKE":
        # 核兵器は毎度流す
        s["action_report"] = (ARCHIVE_LINKS["NUCLEAR"], "最終兵器：戦略抑止力の行使。")
        p2["land"] *= 0.2; p1["atom"] = 0

    s["ap"] -= 1
    if s["ap"] <= 0:
        if p2["land"] > 0: apply_damage(p2["milit"] * 0.25)
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- インターフェース ---
if not s["mode_selected"]:
    st.title("🛡️ STRATEGIC COMMAND")
    if st.button("SYSTEM INITIALIZE"): s["mode_selected"] = True; st.rerun()
else:
    # 資料報告ジャック
    if s["action_report"]:
        st.warning(f"【記録資料の提示】 {s['action_report'][1]}")
        st.markdown(f"資料URL: [こちらをクリックして確認]({s['action_report'][0]})")
        # 簡易的にプレビューを表示（可能な場合のみ）
        if "youtube" in s['action_report'][0]:
            st.video(s['action_report'][0])
        else:
            st.info("※セキュリティ保護のため、詳細は上記URLより公的アーカイブを確認してください。")
            
        if st.button("報告を確認し司令画面に戻る"): 
            s["action_report"] = None; st.rerun()
        st.stop()

    # 司令コンソール
    st.subheader(f"COMMAND CONSOLE - TURN {s['turn']}")
    
    # 敵情
    st.write(f"🟥 敵勢力領土: {p2['land']:.1f}")
    st.progress(max(0.0, min(p2['land']/500, 1.0)))
    
    st.divider()

    # 自軍
    c1, c2, c3 = st.columns(3)
    c1.metric("本国", f"{p1['land']:.1f}")
    c2.metric("緩衝", f"{p1['buffer']:.1f}")
    c3.metric("行動", f"{s['ap']}")
    
    st.write(f"軍備: {p1['milit']}/100 | 特殊兵器開発: {p1['atom']}/200")
    st.progress(min(p1['atom']/200, 1.0))

    if p1["land"] <= 0:
        st.error("【敗北】本国陥落。")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    elif p2["land"] <= 0:
        st.success("【勝利】対抗勢力沈黙。")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        if p1["atom"] >= 200:
            if st.button("🚀 戦略抑止兵器 使用承認", type="primary"): exec_op("NUKE"); st.rerun()
        
        col1, col2 = st.columns(2)
        if col1.button("🛠 技術開発"): exec_op("DEV"); st.rerun()
        if col2.button("🛡 領域防衛"): exec_op("DEF"); st.rerun()
        if col1.button("⚔️ 攻勢進軍"): exec_op("ATK"); st.rerun()
        if col2.button("🚩 緩衝確保"): exec_op("OCC"); st.rerun()

    st.divider()
    for log in s["logs"][:2]: st.caption(log)
