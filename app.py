import streamlit as st
import random

# --- モバイル・極限戦術画面 ---
st.set_page_config(page_title="DEUS: EXTERMINATION", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        overflow: hidden; background-color: #000; color: #FFF;
    }
    .enemy-banner {
        background-color: #300; border: 2px solid #F00;
        padding: 5px; text-align: center; margin: -50px -15px 10px -15px;
    }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1.1rem; }
    .status-row {
        display: flex; justify-content: space-around;
        background: #111; border: 1px solid #d4af37;
        padding: 5px; margin-bottom: 5px;
    }
    .stat-val { color: #d4af37; font-weight: bold; }
    div[data-testid="column"] button {
        height: 42px !important; font-size: 0.7rem !important;
        font-weight: 900 !important; background-color: #222 !important;
        color: #FFF !important; border: 1px solid #d4af37 !important;
        padding: 0px !important;
    }
    /* 超大国用の警告色 */
    .critical-warn { color: #FF0000; font-size: 0.7rem; font-weight: bold; animation: blink 0.5s infinite; }
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0;} 100% {opacity: 1;} }
    .log-box {
        background: #050505; border-left: 3px solid #d4af37;
        padding: 5px; height: 100px; font-size: 0.75rem; color: #EEE; overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=400"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "nuke_point": 0, "shield_active": False},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0},
        "turn": 1, "logs": ["殲滅指令を受信。"],
        "player_ap": 2, "wmd_charging": False, "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 戦術演算 ---
def apply_damage_to_player(dmg, is_wmd=False):
    # 防御システム：成功率が低い（30%のみ成功、それ以外は直撃）
    if p1["shield_active"]:
        if random.random() < 0.3:
            dmg = max(0, dmg - 40)
            s["logs"].insert(0, "🛡️ 防御成功：被害を大幅に減衰")
        else:
            s["logs"].insert(0, "❌ 防御失敗：防壁が貫通された")
    
    # AIはまず植民地（緩衝地帯）から破壊してくる
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
        if shield_amt > 0: s["logs"].insert(0, f"🚩 占領地が損耗: -{shield_amt:.1f}")
        
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    if dmg > 0: s["logs"].insert(0, f"💥 本国被害: -{dmg:.1f}pts")

def ai_logic():
    # 難易度設定
    actions = 1 if s["difficulty"] == "小国" else (2 if s["difficulty"] == "大国" else 6)
    
    for _ in range(actions):
        if p2["territory"] <= 0: break
        
        # --- AIの戦略ルーチン ---
        choice = random.random()
        
        # 1. AIのスパイ工作 (プレイヤーの核を妨害 / 行動不能にする)
        if choice < 0.25 and p1["nuke_point"] > 30:
            p1["nuke_point"] = max(0, p1["nuke_point"] - 50)
            s["logs"].insert(0, "🕵️ AIスパイ：我軍の核承認を無効化")
            continue

        # 2. AIの植民地拡大 (領土回復)
        if choice < 0.4 and s["difficulty"] == "超大国":
            restore = 30
            p2["territory"] += restore
            s["logs"].insert(0, "🏭 DEUS：占領地から資源を回収、修復完了")
            continue

        # 3. 攻撃フェーズ
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * (0.95 if s["difficulty"] == "超大国" else 0.5)
            apply_damage_to_player(nuke_dmg, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_rate = 0.7 if s["difficulty"] == "超大国" else 0.2
            if random.random() < wmd_rate:
                s["wmd_charging"] = True
                s["logs"].insert(0, "🚨 DEUS：最終審判プロトコル起動")
            else:
                p2_power = 2.5 if s["difficulty"] == "超大国" else 1.0
                apply_damage_to_player(p2["military"] * 0.2 * p2_power)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP": p1["military"] += 25.0; p1["nuke_point"] += 20; s["logs"].insert(0, "🛠 指令：兵器増産")
    elif cmd == "DEFEND": p1["shield_active"] = True; s["logs"].insert(0, "🛡 指令：防壁展開（成功率低）")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        if s["difficulty"] == "超大国": dmg *= 0.2 # 超大国には攻撃が通じにくい
        p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️ 進軍：敵地破壊 -{dmg:.1f}")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩 指令：占領地確保")
    elif cmd == "SPY":
        # 超大国戦でのみ有効なカウンター工作
        if s["wmd_charging"]:
            s["wmd_charging"] = False; s["logs"].insert(0, "🕵️ 工作：敵の核回路を遮断！")
        else:
            p1["nuke_point"] += 40; p2["territory"] -= 20; s["logs"].insert(0, "🕵️ 工作：敵内部に潜入")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"; p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️ 最終宣告：核執行")
    
    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield_active"] = 2, s["turn"] + 1, False

# --- UI構築 ---
if s["difficulty"] is None:
    st.title("🚩 DEUS COMMAND")
    if st.button("小国"): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if st.button("大国"): s["difficulty"] = "大国"; st.rerun()
    if st.button("超大国（絶望）"): s["difficulty"] = "超大国"; p2["territory"] = 2000.0; st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS ({s["difficulty"]}): {p2["territory"]:.0f}pts</span></div>', unsafe_allow_html=True)
    if s["wmd_charging"]: st.markdown('<div class="critical-warn">☢️ WARN: 戦略兵器ロックオン</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="status-row"><div>本国: <span class="stat-val">{p1["territory"]:.0f}</span></div><div>緩衝: <span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)

    c_g1, c_g2 = st.columns(2)
    c_g1.caption(f"軍事: {p1['military']:.0f}")
    c_g2.caption(f"核: {p1['nuke_point']:.0f}/200")
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.write("### 作戦完了: " + ("勝利" if p2["territory"] <= 0 else "敗北"))
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        st.write(f"**T-{s['turn']} | AP: {s['player_ap']}**")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        # 5列コマンド（超大国はSPYが生命線）
        cols = st.columns(5)
        if cols[0].button("🛠開発"): player_step("DEVELOP"); st.rerun()
        if cols[1].button("🛡防衛"): player_step("DEFEND"); st.rerun()
        if cols[2].button("⚔️進軍"): player_step("MARCH"); st.rerun()
        if cols[3].button("🚩占領"): player_step("OCCUPY"); st.rerun()
        if cols[4].button("🕵️潜入"): player_step("SPY"); st.rerun()

    if s["effect"] == "NUKE": st.image(IMG_NUKE, width=150)
    st.write("---")
    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:4]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
