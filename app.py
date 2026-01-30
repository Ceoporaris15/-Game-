import streamlit as st
import random
import time

# --- 戦域設定 ---
st.set_page_config(page_title="STRATEGIC COMMAND", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：戦争映画のようなダークで無機質なUI
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        font-weight: bold; height: 3em; border-radius: 0px;
    }
    .stButton>button:hover { border: 1px solid #00ff00; background-color: #002200; }
    .stProgress > div > div > div > div { background-color: #ff0000; }
    h1, h2, h3 { color: #00ff00 !important; text-transform: uppercase; letter-spacing: 2px; }
    .report-text { background-color: #001100; padding: 10px; border-left: 5px solid #00ff00; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 映像アーカイブ（自動再生・ループ・全画面対応リンク） ---
# 実際の記録映像から、自動再生・ミュート・ループ設定を付与した埋め込み用URL
VIDEO_LINKS = {
    "MARCH_1": "https://www.youtube.com/embed/6id8pQY62rE?autoplay=1&mute=1&controls=0&loop=1&playlist=6id8pQY62rE",
    "MARCH_2": "https://www.youtube.com/embed/ZfUf1m3_E7g?autoplay=1&mute=1&controls=0&loop=1&playlist=ZfUf1m3_E7g",
    "NUCLEAR": "https://www.youtube.com/embed/7uV_KscE-X0?autoplay=1&mute=1&controls=0&loop=1&playlist=7uV_KscE-X0",
    "RESEARCH": "https://www.youtube.com/embed/uKofV7uH3gU?autoplay=1&mute=1&controls=0&loop=1&playlist=uKofV7uH3gU",
    "DEFENSE": "https://www.youtube.com/embed/oXlZfGqGatA?autoplay=1&mute=1&controls=0&loop=1&playlist=oXlZfGqGatA",
    "COLLAPSE": "https://www.youtube.com/embed/4uPZ6v6Teyo?autoplay=1&mute=1&controls=0&loop=1&playlist=4uPZ6v6Teyo"
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 350.0, "milit": 60.0, "shield": False},
        "turn": 1,
        "logs": ["司令部：作戦準備を完了せよ。敵勢力の無力化が最優先事項である。"],
        "ap": 2, 
        "wmd": False,
        "hard_mode": False,
        "mode_selected": False,
        "action_video": None,
        "march_history": 0,
        "buffer_lost": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 司令部ロジック ---
def apply_strike(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["buffer"] > 0:
        blocked = min(p1["buffer"], dmg)
        p1["buffer"] -= blocked
        dmg -= blocked
        if p1["buffer"] <= 0 and not s["buffer_lost"]:
            s["action_video"] = (VIDEO_LINKS["COLLAPSE"], "🚨 重要：防衛線突破。本土への直接侵攻が確認された。")
            s["buffer_lost"] = True
    if dmg > 0:
        p1["land"] = max(0, p1["land"] - dmg)
        s["logs"].insert(0, f"被害報告：本国領土に {dmg:.1f} の着弾を確認。")

def enemy_action():
    acts = 2 if s["hard_mode"] else 1
    for _ in range(acts):
        if p2["land"] <= 0: break
        if s["wmd"]:
            apply_strike(p1["land"] * 0.5, True)
            s["wmd"] = False
        else:
            if random.random() < (0.3 if s["hard_mode"] else 0.1):
                s["wmd"] = True
                s["logs"].insert(0, "警告：敵軍に戦略兵器の稼働予兆あり。")
            else:
                apply_strike(p2["milit"] * 0.25)

def exec_op(cmd):
    s["action_video"] = None
    if cmd == "DEV":
        p1["milit"] += 25.0; p1["atom"] += 20
        s["action_video"] = (VIDEO_LINKS["RESEARCH"], "報告：戦略技術の開発が進行中。")
    elif cmd == "DEF":
        p1["shield"] = True
        s["action_video"] = (VIDEO_LINKS["DEFENSE"], "防空：迎撃誘導弾の展開を完了。")
    elif cmd == "ATK":
        s["march_history"] += 1
        v = VIDEO_LINKS["MARCH_1"] if s["march_history"] == 1 else VIDEO_LINKS["MARCH_2"]
        s["action_video"] = (v, "攻勢：航空支援および長距離砲撃を開始。")
        p2["land"] -= (p1["milit"] * 0.5) + (p1["buffer"] * 0.6)
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20
            stolen = max(p2["land"] * 0.2, 40.0)
            p2["land"] -= stolen; p1["buffer"] += stolen
    elif cmd == "NUKE":
        s["action_video"] = (VIDEO_LINKS["NUCLEAR"], "最終審判：戦略抑止兵器、投下完了。")
        p2["land"] *= 0.2; p1["atom"] = 0

    if p1["milit"] >= 100:
        p2["land"] -= 100.0; p1["milit"] = 0
        s["logs"].insert(0, "総力戦：蓄積された全軍事力による一斉攻撃を敢行。")

    s["ap"] -= 1
    if s["ap"] <= 0:
        enemy_action()
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- 戦域インターフェース ---
if not s["mode_selected"]:
    st.title("🛡️ 統合戦域司令システム")
    if st.button("作戦開始 (標準難易度)"): s["mode_selected"] = True; st.rerun()
    if st.button("非常事態宣言 (敵軍最大強化)"): s["hard_mode"] = True; s["mode_selected"] = True; st.rerun()
else:
    # 映像ジャック（全画面風表示）
    if s["action_video"]:
        # YouTube埋め込み：自動再生・全画面サイズ
        st.markdown(f'<iframe width="100%" height="450" src="{s["action_video"][0]}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', unsafe_allow_html=True)
        st.write(f"### {s['action_video'][1]}")
        if st.button("通信を終了し帰還する"): 
            s["action_video"] = None
            st.rerun()
        st.stop()

    # 通常司令画面
    st.title(f"COMMAND CENTER - TURN {s['turn']}")
    
    # 敵軍情報
    st.subheader("🟥 対抗勢力")
    st.progress(max(0.0, min(p2['land']/500, 1.0)))
    st.write(f"敵残存領域: {p2['land']:.1f} | 脅威レベル: {'高' if s['wmd'] else '中'}")
    
    st.divider()

    # 自軍情報
    st.subheader(f"🟦 統合軍司令部 (残り行動回数: {s['ap']})")
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("本国領土", f"{p1['land']:.1f}")
    col_stat2.metric("緩衝地帯(防衛線)", f"{p1['buffer']:.1f}")
    
    col_bar1, col_bar2 = st.columns(2)
    col_bar1.write(f"軍備蓄積: {p1['milit']}/100")
    col_bar1.progress(p1['milit']/100)
    col_bar2.write(f"特殊兵器Pt: {p1['atom']}/200")
    col_bar2.progress(min(p1['atom']/200, 1.0))

    if p1["land"] <= 0:
        st.error("【敗北】司令部沈黙。本国は陥落した。")
        if st.button("歴史を再編する"): st.session_state.clear(); st.rerun()
    elif p2["land"] <= 0:
        st.success("【勝利】対抗勢力の全滅を確認。平和が回復した。")
        if st.button("歴史を再編する"): st.session_state.clear(); st.rerun()
    else:
        # 作戦パネル
        if p1["atom"] >= 200:
            if st.button("☢️ 戦略抑止兵器・投下承認", type="primary", use_container_width=True): exec_op("NUKE"); st.rerun()
        
        btn_c1, btn_c2 = st.columns(2)
        if btn_c1.button("🛠 技術開発 (DEV)"): exec_op("DEV"); st.rerun()
        if btn_c2.button("🛡 領域防衛 (DEF)"): exec_op("DEF"); st.rerun()
        if btn_c1.button("⚔️ 攻勢進軍 (ATK)"): exec_op("ATK"); st.rerun()
        if btn_c2.button("🚩 緩衝地帯確保 (OCC)"): exec_op("OCC"); st.rerun()

    st.divider()
    for log in s["logs"][:3]:
        st.markdown(f'<div class="report-text">{log}</div>', unsafe_allow_html=True)
