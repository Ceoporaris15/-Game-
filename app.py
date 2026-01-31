import streamlit as st
import random

# --- モバイル・ワンビューポート・インターフェース ---
st.set_page_config(page_title="DEUS COMMAND", layout="centered")

st.markdown("""
    <style>
    /* 全体設定：スクロールを殺し、コントラストを最大化 */
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden;
        background-color: #000000;
        color: #FFFFFF;
    }
    .main { font-family: 'Helvetica', 'Arial', sans-serif; }

    /* ヘッダーエリア（敵情報） */
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 5px; text-align: center; margin: -50px -15px 10px -15px;
    }
    .enemy-text { color: #FF0000; font-weight: bold; font-size: 1.1rem; }

    /* ステータスカード：金文字でハッキリと */
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 5px; margin-bottom: 5px;
    }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 1rem; }

    /* コマンドボタン：横一列4並び */
    div[data-testid="column"] button {
        height: 50px !important;
        font-size: 0.9rem !important;
        font-weight: 900 !important;
        background-color: #222 !important;
        color: #FFF !important;
        border: 2px solid #d4af37 !important;
        padding: 0px !important;
    }
    div[data-testid="column"] button:active {
        background-color: #d4af37 !important;
        color: #000 !important;
    }

    /* 核ボタン：列を崩さず強調 */
    .nuke-container button {
        background-color: #800 !important;
        border: 2px solid #F00 !important;
        margin-bottom: 10px;
    }

    /* 戦況実況ログ：読みやすさを追求 */
    .log-box {
        background: #050505; border-left: 3px solid #d4af37;
        padding: 8px; height: 120px; font-size: 0.85rem;
        line-height: 1.4; color: #EEE; overflow: hidden;
    }
    .log-entry { margin-bottom: 4px; border-bottom: 1px solid #222; }

    /* プログレスバー */
    .stProgress > div > div > div > div { background-color: #d4af37; }
    
    /* UI調整 */
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 3rem !important;}
    </style>
    """, unsafe_allow_html=True)

IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=400"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["システム起動。対象：DEUS", "戦況を待機中..."],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 戦術演算 ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    icon = "☢️" if is_wmd else "💥"
    s["logs"].insert(0, f"{icon} 被害報告: -{dmg:.1f}pts")

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
                s["logs"].insert(0, "🚨 ALERT: DEUSが核充填を開始")
            else: apply_damage_to_player(p2["military"] * 0.15)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP": p1["military"] += 25.0; p1["nuke_point"] += 20; s["logs"].insert(0, "🛠 開発: 軍事レベル上昇")
    elif cmd == "DEFEND": p1["shield"] = True; s["logs"].insert(0, "🛡 防衛: 防壁を展開")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍: 敵地-{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 占領: 緩衝地帯を確保")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"; p2["territory"] *= 0.2; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 最終宣告: 核発射")
    
    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI構築 ---
if s["difficulty"] is None:
    st.title("🚩 DEUS COMMAND")
    if st.button("小国（容易）"): s["difficulty"] = "容易"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国（標準）"): s["difficulty"] = "標準"; st.rerun()
    if st.button("超大国（困難）"): s["difficulty"] = "困難"; s["ai_awakened"] = True; st.rerun()
else:
    # 1. 敵ステータス（最上部固定）
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">ENEMY: DEUS {s["difficulty"]} | {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    if s["wmd_charging"]: st.error("🚨 Strategic Weapon Charging...")

    # 2. プレイヤーリソース
    st.markdown(f"""
    <div class="status-row">
        <div>本国: <span class="stat-val">{p1["territory"]:.0f}</span></div>
        <div>占領地: <span class="stat-val">{p1["colony"]:.0f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. 軍事・核ゲージ
    col_g1, col_g2 = st.columns(2)
    col_g1.caption(f"軍事: {p1['military']:.0f}/100")
    col_g2.caption(f"核承認: {p1['nuke_point']:.0f}/200")
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    # 4. 指令コンソール（AP表示と横一列ボタン）
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("### 作戦完了: " + ("勝利" if p2["territory"] <= 0 else "敗北"))
        if st.button("システム再起動"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**TURN: {s['turn']} | ACTION: {s['player_ap']}**")
        
        # 核発射ボタン（条件達成時のみ一列の上に出現）
        if p1["nuke_point"] >= 200:
            st.markdown('<div class="nuke-container">', unsafe_allow_html=True)
            if st.button("☢️ 最終審判を執行する", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 横一列のコマンドボタン
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🛠開発"): player_step("DEVELOP"); st.rerun()
        if c2.button("🛡防備"): player_step("DEFEND"); st.rerun()
        if c3.button("⚔️進軍"): player_step("MARCH"); st.rerun()
        if c4.button("🚩占領"): player_step("OCCUPY"); st.rerun()

    # 5. 核演出（画面を塞がないサイズ）
    if s["effect"] == "NUKE":
        st.image(IMG_NUKE, caption="TARGET ELIMINATED", width=200)

    # 6. 戦況実況ログ（複数行表示）
    st.write("---")
    log_html = "".join([f'<div class="log-entry">{log}</div>' for log in s["logs"][:4]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
