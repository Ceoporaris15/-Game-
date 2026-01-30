import streamlit as st
import random

# --- モバイル最適化・全体主義デザイン ---
st.set_page_config(page_title="DEUS MOBILE", layout="centered")

st.markdown("""
    <style>
    /* 全体：視認性の高いダークテーマ */
    .main { background-color: #121212; color: #f2e8c9; font-family: 'sans-serif'; }
    
    /* 敵エリア：威圧感のある赤 */
    .enemy-container {
        border-bottom: 4px solid #8b0000; background: #2b0000;
        padding: 15px; margin: -15px -15px 15px -15px;
    }
    
    /* ステータスカード */
    .status-card {
        background: #222; border: 1px solid #d4af37;
        padding: 10px; border-radius: 4px; margin-bottom: 10px;
    }

    /* 指令ボタン：スマホで押しやすいサイズ */
    .stButton>button {
        height: 60px !important; border-radius: 8px !important;
        font-size: 1.1rem !important; font-weight: bold !important;
        background-color: #333 !important; color: #d4af37 !important;
        border: 2px solid #d4af37 !important; width: 100%;
        margin-bottom: 5px;
    }
    .stButton>button:active { background-color: #d4af37 !important; color: #000 !important; }

    /* 核兵器ボタン：特別な警告色 */
    .nuke-btn > div > button {
        background-color: #8b0000 !important; color: white !important;
        border: 2px solid #ff0000 !important; animation: blink 1s infinite;
    }
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.7;} 100% {opacity: 1;} }

    /* 演出：ターゲットスコープ */
    .nuke-overlay {
        text-align: center; border: 4px solid #ff0000; background: #000;
        padding: 10px; margin-bottom: 10px; color: #ff0000;
    }
    </style>
    """, unsafe_allow_html=True)

IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["作戦開始。全軍待機中。"],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- システムロジック ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"⚠️ 被害報告: {'【核】' if is_wmd else '【爆撃】'} -{dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "容易" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "🚨 警告: 敵の戦略兵器が充填を開始！")
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
        s["logs"].insert(0, "🛠 指令: 軍需産業を強化。")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["logs"].insert(0, "🛡 指令: 防衛網を活性化。")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"⚔️ 指令: 敵地を {dmg:.1f} 破壊。")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal
            s["logs"].insert(0, "🚩 指令: 領土を接収した。")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["logs"].insert(0, "☢️ 最終宣告: 核兵器を射出。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- モバイルUI ---
if s["difficulty"] is None:
    st.title("🚩 DEUS MOBILE")
    st.write("対象勢力を選べ。")
    if st.button("小国（容易）"): s["difficulty"] = "容易"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国（標準）"): s["difficulty"] = "標準"; st.rerun()
    if st.button("超大国（困難）"): s["difficulty"] = "困難"; s["ai_awakened"] = True; st.rerun()
else:
    # 1. 敵ステータス（固定上部）
    st.markdown(f'<div class="enemy-container">', unsafe_allow_html=True)
    col_e1, col_e2 = st.columns([2, 1])
    col_e1.write(f"🚩 **敵: DEUS ({s['difficulty']})**")
    col_e2.write(f"**HP: {p2['territory']:.0f}**")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    if s["wmd_charging"]: st.error("🚨 敵：戦略核充填中")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. 演出
    if s["effect"] == "NUKE":
        st.markdown('<div class="nuke-overlay"><h2>TARGET DESTROYED</h2></div>', unsafe_allow_html=True)
        st.image(IMG_NUKE, use_container_width=True)

    # 3. プレイヤー情報
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f'<div class="status-card">本国: {p1["territory"]:.0f}</div>', unsafe_allow_html=True)
    with col_p2:
        st.markdown(f'<div class="status-card">占領: {p1["colony"]:.0f}</div>', unsafe_allow_html=True)

    # 4. 指令ボタン（巨大パネル）
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if p1["territory"] <= 0: st.error("敗北：国家崩壊")
        else: st.success("勝利：世界統一")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**作戦フェーズ: {s['turn']} (AP: {s['player_ap']})**")
        
        # 核兵器ボタン（使用可能な時のみ出現）
        if p1["nuke_point"] >= 200:
            st.markdown('<div class="nuke-btn">', unsafe_allow_html=True)
            if st.button("🚀 最終宣告執行（核）"): player_step("NUKE"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        if c1.button("🛠 開発"): player_step("DEVELOP"); st.rerun()
        if c2.button("🛡 防備"): player_step("DEFEND"); st.rerun()
        if c1.button("⚔️ 進軍"): player_step("MARCH"); st.rerun()
        if c2.button("🚩 占領"): player_step("OCCUPY"); st.rerun()

    # 5. ログ（スクロールを考慮し下部にコンパクトに）
    st.markdown("---")
    st.caption("【通信記録】")
    for log in s["logs"][:2]: st.caption(log)
