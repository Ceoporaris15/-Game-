import streamlit as st
import random

# --- 超凝縮・モバイルダッシュボード設計 ---
st.set_page_config(page_title="DEUS DASHBOARD", layout="centered")

st.markdown("""
    <style>
    /* スクロールを抑制し、フォントを最小化 */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden;
        background-color: #121212;
    }
    .main { color: #f2e8c9; font-size: 0.8rem; }
    
    /* 敵エリア：最上部に極細で配置 */
    .enemy-mini-box {
        border-bottom: 2px solid #8b0000; background: #2b0000;
        padding: 5px 10px; margin: -50px -20px 10px -20px;
    }
    
    /* ステータスグリッド */
    .status-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 5px;
        margin-bottom: 5px;
    }
    .mini-card {
        background: #222; border: 1px solid #d4af37;
        padding: 4px; border-radius: 2px; text-align: center;
    }

    /* 指令ボタン：横並びで高さを抑える */
    .stButton>button {
        height: 40px !important; padding: 0px !important;
        font-size: 0.85rem !important; font-weight: bold !important;
        background-color: #333 !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important; margin-bottom: 2px;
    }
    
    /* 核ボタン：目立つが場所を取らない */
    .nuke-btn > div > button {
        background-color: #8b0000 !important; color: #fff !important;
        border: 1px solid #ff0000 !important; height: 35px !important;
    }

    /* ログ：1〜2行に限定 */
    .log-area {
        font-size: 0.7rem; color: #aaa;
        border-top: 1px solid #444; padding-top: 5px;
    }
    
    /* Streamlitの余計な余白を消去 */
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 2rem !important; padding-bottom: 0px !important;}
    </style>
    """, unsafe_allow_html=True)

IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=400"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["SYSTEM READY"],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- ロジック ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"⚠️受損: {dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "容易" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            if random.random() < (0.4 if s["ai_awakened"] else 0.1):
                s["wmd_charging"] = True
                s["logs"].insert(0, "🚨敵核充填")
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP": p1["military"] += 25.0; p1["nuke_point"] += 20; s["logs"].insert(0, "🛠開発完了")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🛡防壁展開")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️攻撃:{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩接収")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"; p2["territory"] *= 0.2; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️神罰執行")
    
    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- 表示 ---
if s["difficulty"] is None:
    st.write("### 🚩 DEUS LOGIN")
    if st.button("小国"): s["difficulty"] = "容易"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国"): s["difficulty"] = "標準"; st.rerun()
    if st.button("超大国"): s["difficulty"] = "困難"; s["ai_awakened"] = True; st.rerun()
else:
    # 1. 敵ステータス（最小化）
    st.markdown(f'<div class="enemy-mini-box"><b>RED: DEUS {s["difficulty"]} | HP:{p2["territory"]:.0f}</b> {"[🚨WMD]" if s["wmd_charging"] else ""}</div>', unsafe_allow_html=True)

    # 2. 自軍ステータスグリッド
    st.markdown(f"""
    <div class="status-grid">
        <div class="mini-card">本国:{p1["territory"]:.0f}</div>
        <div class="mini-card">緩衝:{p1["colony"]:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    # 3. ゲージ類
    st.caption(f"軍:{p1['military']:.0f}/核:{p1['nuke_point']:.0f}")
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    # 4. 指令ボタン（2×2配置）
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("WIN" if p2["territory"] <= 0 else "LOSS")
        if st.button("REBOOT"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"T-{s['turn']} | AP:{s['player_ap']}")
        
        # 核兵器ボタン
        if p1["nuke_point"] >= 200:
            st.markdown('<div class="nuke-btn">', unsafe_allow_html=True)
            if st.button("☢️ 最終宣告"): player_step("NUKE"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("🛠 開発"): player_step("DEVELOP"); st.rerun()
        if c2.button("🛡 防備"): player_step("DEFEND"); st.rerun()
        if c1.button("⚔️ 進軍"): player_step("MARCH"); st.rerun()
        if c2.button("🚩 占領"): player_step("OCCUPY"); st.rerun()

    # 5. 核演出（出現しても場所を最小限に）
    if s["effect"] == "NUKE":
        st.image(IMG_NUKE, width=150)

    # 6. 通信ログ（最下部1行）
    st.markdown(f'<div class="log-area">LOG: {s["logs"][0] if s["logs"] else ""}</div>', unsafe_allow_html=True)
