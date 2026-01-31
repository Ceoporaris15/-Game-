import streamlit as st
import random
import base64

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; overflow: hidden; }
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 4px; text-align: center; margin: -55px -15px 5px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1rem; letter-spacing: 3px; }
    .status-row { display: flex; justify-content: space-around; background: #111; border: 1px solid #d4af37; padding: 2px; margin-bottom: 5px; border-radius: 4px; }
    .stat-label { font-size: 0.6rem; color: #888; margin-right: 4px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 0.9rem; }
    .stProgress { height: 6px !important; margin-bottom: 2px !important; }
    .nuke-title { color: #007BFF; font-weight: bold; font-size: 0.7rem; margin: 0; }
    .briefing-card { background: #111; border: 1px solid #333; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .briefing-title { color: #d4af37; font-weight: bold; font-size: 1.1rem; }
    .briefing-text { font-size: 0.85rem; color: #CCC; }
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 30px !important; font-size: 0.8rem !important;
        background-color: #1a1a1a !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.75rem; color: #CCC; line-height: 1.2; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 50.0, "nuke_point": 0, "shield": False, "nuke_lock": 0},
        "p2": {"territory": 800.0, "military": 0.0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE."],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None,
        "phase": "DIFFICULTY" # DIFFICULTY -> BRIEFING -> FACTION -> GAME
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- アクション実行関数 ---
def player_step(cmd):
    mul_pwr = 0.25 if s["faction"] == "社会主義国" else 1.0
    mul_nuk = 2.0 if s["faction"] == "連合国" else 1.0
    spy_prob = 0.60 if s["faction"] == "連合国" else 0.33
    shield_eff = 0.8 if s["faction"] == "枢軸国" else 0.5 

    if cmd == "EXP":
        p1["military"] += 25.0 * mul_pwr
        if p1["nuke_lock"] <= 0: p1["nuke_point"] += 20 * mul_nuk
        s["logs"].insert(0, "🛠軍拡: 軍備と核開発を同時進行。")
    elif cmd == "DEF": 
        p1["shield"] = True; s["logs"].insert(0, "🛡防衛: 迎撃シールド展開。")
    elif cmd == "MAR":
        dmg = max(((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * mul_pwr + 10.0, 10.0)
        if p2["stun"] <= 0 and random.random() < 0.30:
            dmg *= 0.5; p2["territory"] -= dmg; s["logs"].insert(0, f"🛡敵防衛: 被害を{dmg:.0f}に軽減。")
        else:
            p2["territory"] -= dmg; s["logs"].insert(0, f"⚔️進軍: {dmg:.0f}の致命打。")
    elif cmd == "OCC":
        cost = max(15.0 * mul_pwr, 5.0)
        if p1["military"] >= cost:
            p1["military"] -= cost
            steal = (max(p2["territory"] * 0.3, 50.0) * mul_pwr) + 20.0
            p2["territory"] -= steal; p1["colony"] += steal
            s["logs"].insert(0, f"🚩占領: 緩衝地帯を+{steal:.0f}拡張。")
    elif cmd == "SPY":
        if random.random() < spy_prob:
            p2["territory"] *= 0.9; p2["stun"] = 2; s["logs"].insert(0, "🕵️工作成功: 敵を完全沈黙。")
        else: s["logs"].insert(0, "🕵️工作失敗: 潜入員が消えた。")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️最終審判。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        if p1["nuke_lock"] > 0: p1["nuke_lock"] -= 1
        if p2["stun"] > 0:
            p2["stun"] -= 1; s["logs"].insert(0, f"⏳敵再起動中({p2['stun']}T)")
        else:
            p2["military"] += 20.0
            e_dmg = max((p2["military"] * 0.4) + 20.0, 20.0)
            if s["difficulty"] == "超大国": e_dmg *= 1.2
            if p1["shield"]: e_dmg *= shield_eff
            
            if p1["colony"] > 0:
                p1["colony"] -= e_dmg
                if p1["colony"] < 0: p1["colony"] = 0
                s["logs"].insert(0, f"⚠️敵反攻: 緩衝地帯に{e_dmg:.0f}ダメ。")
            else:
                p1["territory"] -= e_dmg
                s["logs"].insert(0, f"🚨警告: 本土へ{e_dmg:.0f}の直撃。")

            if s["difficulty"] == "大国" and random.random() < 0.4:
                p1["nuke_point"] = max(0, p1["nuke_point"] - 35)
                s["logs"].insert(0, "🕵️敵工作: 核開発施設を爆破。")
            elif s["difficulty"] == "超大国":
                if random.random() < 0.3: p1["nuke_lock"] = 2; s["logs"].insert(0, "☢️核ハック: システム凍結。")
                elif random.random() < 0.2: p1["nuke_point"] = 0; s["logs"].insert(0, "☣️データ抹消。")
            
        s["player_ap"] = s["max_ap"]; s["turn"] += 1; p1["shield"] = False

# --- フェーズ別UI ---

# 1. 難易度選択
if s["phase"] == "DIFFICULTY":
    st.title("難易度設定")
    if st.button("小国", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("大国", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 950.0; s["phase"] = "BRIEFING"; st.rerun()
    if st.button("超大国", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 1200.0; s["phase"] = "BRIEFING"; st.rerun()

# 2. ブリーフィング画面 (追加)
elif s["phase"] == "BRIEFING":
    st.title("🛡️ 作戦ブリーフィング")
    
    st.markdown('<div class="briefing-card"><span class="briefing-title">【アクション解説】</span><br>'
                '<span class="briefing-text">・🛠軍拡: 戦力と核開発を進める。<br>'
                '・⚔️進軍: 敵に直接打撃を与える（敵の防衛で軽減される可能性あり）。<br>'
                '・🚩占領: 敵領土を奪い、自国の盾となる「緩衝地帯」を強化する。<br>'
                '・🕵️スパイ: 敵をスタンさせ、防衛を封印。核の妨害も防ぐ。<br>'
                '・🛡防衛: 次の敵の攻撃を半減させる。</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="briefing-card"><span class="briefing-title">【陣営特性】</span><br>'
                '<span class="briefing-text">・<b>連合国:</b> スパイ成功率(60%)、核開発効率(2倍)。知略に長ける。<br>'
                '・<b>枢軸国:</b> 攻撃力は高いが、防衛力が低い(被ダメ80%)。短期決戦向き。<br>'
                '・<b>社会主義国:</b> 本土(200)、3回行動可能。ただし威力は1/4。圧倒的な物量。</span></div>', unsafe_allow_html=True)
    
    if st.button("陣営選択へ進む", use_container_width=True):
        s["phase"] = "FACTION"; st.rerun()

# 3. 陣営選択
elif s["phase"] == "FACTION":
    st.title("陣営プロトコル")
    c1, c2, c3 = st.columns(3)
    if c1.button("連合国", use_container_width=True): s["faction"] = "連合国"; s["phase"] = "GAME"; st.rerun()
    if c2.button("枢軸国", use_container_width=True): s["faction"] = "枢軸国"; s["phase"] = "GAME"; st.rerun()
    if c3.button("社会主義国", use_container_width=True): 
        s["faction"] = "社会主義国"; p1["territory"] = 200.0; s["player_ap"] = 3; s["max_ap"] = 3
        s["phase"] = "GAME"; st.rerun()

# 4. メインゲーム
elif s["phase"] == "GAME":
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本国</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    lock_ind = " (☢️LOCK)" if p1["nuke_lock"] > 0 else ""
    st.markdown(f'<p class="nuke-title">☢️ 核開発進行状況{lock_ind}</p>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.success("VICTORY" if p2["territory"] <= 0 else "DEFEAT")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.caption(f"T-{s['turn']} | AP: {s['player_ap']} | {s['faction']}")
        if p1["nuke_point"] >= 200:
            if st.button("☢️ 最終宣告執行", type="primary", use_container_width=True): player_step("NUK"); st.rerun()
        
        c1, c2, c3 = st.columns(3)
        if c1.button("🛠軍拡", use_container_width=True): player_step("EXP"); st.rerun()
        if c2.button("🛡防衛", use_container_width=True): player_step("DEF"); st.rerun()
        if c3.button("🕵️スパイ", use_container_width=True): player_step("SPY"); st.rerun()
        c4, c5 = st.columns(2)
        if c4.button("⚔️進軍", use_container_width=True): player_step("MAR"); st.rerun()
        if c5.button("🚩占領", use_container_width=True): player_step("OCC"); st.rerun()

    log_html = "".join([f'<div>{log}</div>' for log in s["logs"][:2]])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
