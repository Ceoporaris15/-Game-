import streamlit as st
import random

# --- 極秘軍事指令：画面設計 ---
st.set_page_config(page_title="TOTALITARIAN COMMAND", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #f2e8c9; font-family: 'Courier New', monospace; }
    .enemy-box {
        border: 4px solid #8b0000; background: #2b0000;
        padding: 15px; border-radius: 0px; margin-bottom: 20px;
        box-shadow: 5px 5px 0px #000;
    }
    .player-box {
        border: 4px solid #d4af37; background: #2f2f2f;
        padding: 15px; border-radius: 0px;
        box-shadow: 5px 5px 0px #000;
    }
    .nuke-overlay {
        text-align: center; border: 5px solid #ff0000;
        padding: 20px; background: #000; margin-bottom: 10px;
        color: #ff0000; font-weight: bold;
    }
    .target-scope {
        width: 100px; height: 100px; border: 3px solid #ff0000;
        border-radius: 50%; margin: 0 auto 10px; position: relative;
    }
    .target-scope::before { content: ''; position: absolute; top: 50%; left: -20%; width: 140%; height: 3px; background: #ff0000; }
    .target-scope::after { content: ''; position: absolute; left: 50%; top: -20%; width: 3px; height: 140%; background: #ff0000; }
    .stButton>button {
        border-radius: 0px; background-color: #4a4a4a; color: #f2e8c9;
        border: 2px solid #d4af37; font-weight: bold; height: 3em; width: 100%;
    }
    .stButton>button:hover { background-color: #d4af37; color: #000; }
    </style>
    """, unsafe_allow_html=True)

IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800"

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1, "logs": ["通報：システム稼働開始。敵対勢力を殲滅せよ。"],
        "player_ap": 2, "wmd_charging": False, "ai_awakened": False,
        "difficulty": None, "effect": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 演算処理 ---
def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]: dmg *= 0.6
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt; dmg -= shield_amt
    if dmg > 0: p1["territory"] = max(0, p1["territory"] - dmg)
    s["logs"].insert(0, f"報告：{'【核】' if is_wmd else '【爆撃】'} 本国被害 {dmg:.1f} セクター")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "警告：DEUSが戦略兵器の充填を開始した！")
            else: apply_damage_to_player(p2["military"] * 0.2)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0; p1["nuke_point"] += 20
        s["logs"].insert(0, "指令：軍需産業を拡張。軍備を増強。")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["logs"].insert(0, "指令：防衛線を構築。被害を抑制。")
    elif cmd == "MARCH":
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"指令：総攻撃。敵領土を {dmg:.1f} 破壊。")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal
            s["logs"].insert(0, "指令：敵植民地を接収。緩衝地帯とした。")
    elif cmd == "NUKE":
        s["effect"] = "NUKE"
        p2["territory"] *= 0.2; p1["nuke_point"] = 0
        s["logs"].insert(0, "ゴールド・コード戦意をくじけ。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic(); s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- 戦術指令画面 ---
if s["difficulty"] is None:
    st.title("🚩 DEUS 戦術指令コンソール")
    cols = st.columns(3)
    if cols[0].button("小国"): s["difficulty"] = "小国"; p2["territory"] = 150.0; st.rerun()
    if cols[1].button("大国"): s["difficulty"] = "大国"; st.rerun()
    if cols[2].button("超大国"): s["difficulty"] = "超大国"; s["ai_awakened"] = True; st.rerun()
else:
    # 敵陣営
    st.markdown(f'<div class="enemy-box">', unsafe_allow_html=True)
    st.write(f"### 🚩 敵対勢力: DEUS [{s['difficulty']}]")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    col_e1, col_e2 = st.columns(2)
    col_e1.metric("残存勢力値", f"{p2['territory']:.1f}")
    if s["wmd_charging"]: st.warning("🚨 戦略核：充填完了")
    st.markdown('</div>', unsafe_allow_html=True)

    # 核演出
    if s["effect"] == "NUKE":
        st.markdown('<div class="nuke-overlay"><div class="target-scope"></div><h2>最終審判：目標殲滅</h2></div>', unsafe_allow_html=True)
        st.image(IMG_NUKE, use_container_width=True)

    # 自陣営
    st.markdown(f'<div class="player-box">', unsafe_allow_html=True)
    st.write(f"### 🎖️ 自国司令部 [作戦第 {s['turn']} 段階]")
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.metric("本国領土", f"{p1['territory']:.1f}")
    col_p2.metric("緩衝地帯", f"{p1['colony']:.1f}")
    col_p3.metric("行動権", s["player_ap"])

    c_m1, c_m2 = st.columns(2)
    # 【修正箇所】値を0.0〜1.0の範囲に収めるためにmin(..., 1.0)を追加
    mil_val = min(p1['military'] / 100.0, 1.0)
    nuke_val = min(p1['nuke_point'] / 200.0, 1.0)
    
    c_m1.caption(f"軍事動員数: {p1['military']}/100")
    c_m1.progress(mil_val)
    c_m2.caption(f"核承認率: {p1['nuke_point']}/200")
    c_m2.progress(nuke_val)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if p1["territory"] <= 0: st.error("国家崩壊：司令官、貴公は敗北した。")
        else: st.success("闘争勝利：敵対勢力は歴史から消去された。")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 最終宣告（核）を執行", type="primary"): player_step("NUKE"); st.rerun()
        
        btn_cols = st.columns(2)
        if btn_cols[0].button("🛠 開発"): player_step("DEVELOP"); st.rerun()
        if btn_cols[1].button("🛡️ 防備"): player_step("DEFEND"); st.rerun()
        if btn_cols[0].button("🔫 進軍"): player_step("MARCH"); st.rerun()
        if btn_cols[1].button("🚩 占領"): player_step("OCCUPY"); st.rerun()

    st.write("---")
    for log in s["logs"][:4]: st.text(log)
