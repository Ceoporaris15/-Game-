import streamlit as st
import random
import time

# --- 戦域設定 ---
st.set_page_config(page_title="STRATEGIC COMMAND", layout="wide", initial_sidebar_state="collapsed")

# カスタムCSS：戦争映画のような無機質なダークUI
st.markdown("""
    <style>
    .main { background-color: #0e1111; color: #d3d3d3; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { 
        width: 100%; border: 1px solid #4a4a4a; background-color: #1a1a1a; color: #00ff00;
        font-weight: bold; height: 3em; border-radius: 0px;
    }
    .stButton>button:hover { border: 1px solid #00ff00; background-color: #002200; }
    .stProgress > div > div > div > div { background-color: #00ff00; }
    h1, h2, h3 { color: #00ff00 !important; text-transform: uppercase; letter-spacing: 2px; font-size: 1.5rem; }
    .report-text { background-color: #001100; padding: 10px; border-left: 5px solid #00ff00; margin-bottom: 10px; font-size: 0.8rem; }
    /* 画像の最大高さを制限してスマホでのスクロールを防止 */
    .stImage > img { max-height: 300px; object-fit: cover; }
    </style>
    """, unsafe_allow_html=True)

# --- 教育用・歴史的資料画像（実際の歴史的記録写真） ---
IMAGE_ASSETS = {
    "RESEARCH": "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000", # 技術開発
    "DEFENSE": "https://images.unsplash.com/photo-1554123168-b407f93924dc?q=80&w=1000",  # レーダー/防空
    "MARCH": "https://images.unsplash.com/photo-1506774518161-b710d10e2733?q=80&w=1000",   # 進軍/地図
    "NUCLEAR": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1000", # 戦略兵器/大気圏
    "COLLAPSE": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?q=80&w=1000" # 陥落/焦土
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"land": 100.0, "milit": 0.0, "buffer": 20.0, "shield": False, "atom": 0},
        "p2": {"land": 350.0, "milit": 60.0, "shield": False},
        "turn": 1,
        "logs": ["司令部：作戦準備を完了せよ。"],
        "ap": 2, 
        "wmd": False,
        "hard_mode": False,
        "mode_selected": False,
        "action_img": None,
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
            s["action_img"] = (IMAGE_ASSETS["COLLAPSE"], "🚨 警告：第一防衛線が陥落。本土侵攻を許しました。")
            s["buffer_lost"] = True
    if dmg > 0:
        p1["land"] = max(0, p1["land"] - dmg)
        s["logs"].insert(0, f"被害：本国領土に着弾。損害 {dmg:.1f}")

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
                s["logs"].insert(0, "警告：敵勢力による大規模兵器のチャージを確認。")
            else:
                apply_strike(p2["milit"] * 0.25)

def exec_op(cmd):
    s["action_img"] = None
    if cmd == "DEV":
        p1["milit"] += 25.0; p1["atom"] += 20
        s["action_img"] = (IMAGE_ASSETS["RESEARCH"], "報告：戦略技術の最適化、及び軍備の蓄積を実行。")
    elif cmd == "DEF":
        p1["shield"] = True
        s["action_img"] = (IMAGE_ASSETS["DEFENSE"], "防衛：防空網を最大出力で展開。次撃の損害を40%軽減。")
    elif cmd == "ATK":
        s["action_img"] = (IMAGE_ASSETS["MARCH"], "攻勢：地上戦力及び航空支援による合同進軍を開始。")
        p2["land"] -= (p1["milit"] * 0.5) + (p1["buffer"] * 0.6)
    elif cmd == "OCC":
        if p1["milit"] >= 20:
            p1["milit"] -= 20
            stolen = max(p2["land"] * 0.2, 40.0)
            p2["land"] -= stolen; p1["buffer"] += stolen
            s["logs"].insert(0, f"占領：緩衝地帯を {stolen:.1f} 確保。防衛力が向上。")
    elif cmd == "NUKE":
        s["action_img"] = (IMAGE_ASSETS["NUCLEAR"], "最終兵器：戦略抑止兵器、発射。敵残存勢力の80%を無力化。")
        p2["land"] *= 0.2; p1["atom"] = 0

    if p1["milit"] >= 100:
        p2["land"] -= 100.0; p1["milit"] = 0
        s["logs"].insert(0, "総進軍：リミッター解除。全軍による飽和攻撃。")

    s["ap"] -= 1
    if s["ap"] <= 0:
        enemy_action()
        s["ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- 戦域インターフェース ---
if not s["mode_selected"]:
    st.title("🛡️ 統合戦域司令システム")
    if st.button("作戦開始 (Standard)"): s["mode_selected"] = True; st.rerun()
    if st.button("非常事態宣言 (Hard)"): s["hard_mode"] = True; s["mode_selected"] = True; st.rerun()
else:
    # 報告画像ジャック
    if s["action_img"]:
        st.image(s["action_img"][0], use_container_width=True)
        st.write(f"### {s['action_img'][1]}")
        if st.button("報告を確認し、戦域に戻る"): 
            s["action_img"] = None
            st.rerun()
        st.stop()

    # 指令コンソール
    st.subheader(f"COMMAND CENTER - TURN {s['turn']}")
    
    # 敵勢力情報
    st.write(f"🟥 敵勢力領土: {p2['land']:.1f} {'⚠️WMDチャージ中' if s['wmd'] else ''}")
    st.progress(max(0.0, min(p2['land']/500, 1.0)))
    
    st.divider()

    # 自軍情報
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("本国", f"{p1['land']:.1f}")
    col_stat2.metric("緩衝", f"{p1['buffer']:.1f}")
    col_stat3.metric("AP", f"{s['ap']}")
    
    col_bar1, col_bar2 = st.columns(2)
    col_bar1.write(f"軍備: {p1['milit']}/100")
    col_bar1.progress(p1['milit']/100)
    col_bar2.write(f"核開発: {p1['atom']}/200")
    col_bar2.progress(min(p1['atom']/200, 1.0))

    if p1["land"] <= 0:
        st.error("【敗北】本国機能が停止しました。歴史から消滅します。")
        if st.button("戦域を再構築"): st.session_state.clear(); st.rerun()
    elif p2["land"] <= 0:
        st.success("【勝利】対抗勢力を完全沈黙。恒久平和を確保しました。")
        if st.button("戦域を再構築"): st.session_state.clear(); st.rerun()
    else:
        # 作戦パネル（スマホでも押しやすい2x2配置）
        if p1["atom"] >= 200:
            if st.button("🚀 戦略抑止兵器・承認", type="primary", use_container_width=True): exec_op("NUKE"); st.rerun()
        
        btn_c1, btn_c2 = st.columns(2)
        if btn_c1.button("🛠 技術開発"): exec_op("DEV"); st.rerun()
        if btn_c2.button("🛡 領域防衛"): exec_op("DEF"); st.rerun()
        if btn_c1.button("⚔️ 攻勢進軍"): exec_op("ATK"); st.rerun()
        if btn_c2.button("🚩 緩衝確保"): exec_op("OCC"); st.rerun()

    st.divider()
    for log in s["logs"][:2]:
        st.markdown(f'<div class="report-text">{log}</div>', unsafe_allow_html=True)
