import streamlit as st
import random
import base64

# --- 1. レイアウト設定 ---
st.set_page_config(page_title="DEUS", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #000; color: #FFF; overflow: hidden; }
    .stAudio { display: none; } 
    .enemy-banner { background-color: #200; border-bottom: 1px solid #F00; padding: 4px; text-align: center; margin: -55px -15px 5px -15px; }
    .enemy-text { color: #F00; font-weight: bold; font-size: 1rem; letter-spacing: 3px; }
    .status-row { display: flex; justify-content: space-around; background: #111; border: 1px solid #d4af37; padding: 2px; margin-bottom: 5px; border-radius: 4px; }
    .stat-label { font-size: 0.6rem; color: #888; margin-right: 4px; }
    .stat-val { color: #d4af37; font-weight: bold; font-size: 0.9rem; }
    .stProgress { height: 6px !important; margin-bottom: 2px !important; }
    .stProgress > div > div > div > div { background-color: #007BFF; }
    .nuke-title { color: #007BFF; font-weight: bold; font-size: 0.7rem; margin: 0; }
    div[data-testid="column"] button, div[data-testid="stVerticalBlock"] button {
        height: 28px !important; font-size: 0.75rem !important;
        padding: 0px !important; margin-bottom: -15px !important;
        background-color: #1a1a1a !important; color: #d4af37 !important;
        border: 1px solid #d4af37 !important; border-radius: 2px !important;
    }
    .log-box { background: #000; border-top: 1px solid #333; padding: 4px 8px; height: 60px; font-size: 0.75rem; color: #CCC; line-height: 1.2; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BGM同期 ---
def setup_audio_engine():
    try:
        with open('Vidnoz_AIMusic.mp3', 'rb') as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""<audio id="bgm" loop><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
            <script>var audio = document.getElementById('bgm'); window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{once: true}});</script>"""
            st.components.v1.html(audio_html, height=0)
    except: pass

# --- 3. システム初期化 ---
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 150.0, "military": 0.0, "colony": 30.0, "nuke_point": 0, "shield": False, "nuke_lock": 0},
        "p2": {"territory": 800.0, "military": 0.0, "stun": 0}, 
        "turn": 1, "logs": ["SYSTEM ONLINE. 核開発を阻止せよ。"],
        "player_ap": 2, "max_ap": 2, "difficulty": None, "faction": None
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def player_step(cmd):
    mul_exp = 2.0 if s["faction"] == "社会主義国" else 1.0
    mul_mar = 2.0 if s["faction"] in ["枢軸国", "社会主義国"] else 1.0
    mul_nuk = 2.0 if s["faction"] == "連合国" else 1.0
    
    if cmd == "EXP":
        p1["military"] += 25.0 * mul_exp
        if p1["nuke_lock"] <= 0:
            p1["nuke_point"] += 20 * mul_nuk
            s["logs"].insert(0, "🛠軍拡: 戦力・核開発進行")
        else:
            s["logs"].insert(0, f"🛠軍拡: 戦力のみ強化(核はロック中)")
    elif cmd == "DEF": p1["shield"] = True; s["logs"].insert(0, "🛡防衛: シールド展開")
    elif cmd == "MAR":
        dmg_val = ((p1["military"] * 0.5) + (p1["colony"] * 0.6)) * mul_mar
        p2["territory"] -= dmg_val; s["logs"].insert(0, f"⚔️進軍: 敵へ{dmg_val:.0f}打撃")
    elif cmd == "OCC":
        if p1["military"] >= 20:
            p1["military"] -= 20; steal = max(p2["territory"] * 0.2, 40.0)
            p2["territory"] -= steal; p1["colony"] += steal; s["logs"].insert(0, "🚩占領: 領土吸収")
    elif cmd == "SPY":
        if random.random() < 0.33:
            p2["territory"] *= 0.9; p2["stun"] = 2
            s["logs"].insert(0, "🕵️工作成功: 敵を2T停止")
        else: s["logs"].insert(0, "🕵️工作失敗: 工作員消失")
    elif cmd == "NUK":
        p2["territory"] *= 0.15; p1["nuke_point"] = 0; s["logs"].insert(0, "☢️核執行: 焦土化")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        if p1["nuke_lock"] > 0: p1["nuke_lock"] -= 1
        
        if p2["stun"] > 0:
            p2["stun"] -= 1; s["logs"].insert(0, f"⏳敵再起動中({p2['stun']}T)")
        else:
            # --- 敵AIの行動 (軍拡と妨害) ---
            p2["military"] += 20.0 # 敵も毎ターン軍拡
            # プレイヤーと同程度の攻撃力計算
            enemy_dmg = (p2["military"] * 0.4) + 10.0
            
            if s["difficulty"] == "大国":
                if random.random() < 0.40: # 妨害スパイ
                    p1["nuke_point"] = max(0, p1["nuke_point"] - 35)
                    s["logs"].insert(0, "🕵️大国スパイ: 核施設を爆破(-35P)")
            elif s["difficulty"] == "超大国":
                enemy_dmg *= 1.2 # 少しだけ強力
                if random.random() < 0.30: # 核ロック
                    p1["nuke_lock"] = 2
                    s["logs"].insert(0, "☢️核ハック: システム凍結(2T進行不能)")
                elif random.random() < 0.20:
                    p1["nuke_point"] = 0
                    s["logs"].insert(0, "☣️データ消去: 核開発データが喪失")

            if p1["shield"]: enemy_dmg *= 0.5
            p1["territory"] -= enemy_dmg
            s["logs"].insert(0, f"⚠️敵反撃: 被害{enemy_dmg:.0f}")
            
        s["player_ap"] = s["max_ap"]
        s["turn"] += 1
        p1["shield"] = False

# --- UI構築 ---
setup_audio_engine()

if s["difficulty"] is None:
    st.title("難易度選択")
    if st.button("小国", use_container_width=True): s["difficulty"] = "小国"; p2["territory"] = 200.0; st.rerun()
    if st.button("大国", use_container_width=True): s["difficulty"] = "大国"; p2["territory"] = 900.0; st.rerun()
    if st.button("超大国", use_container_width=True): s["difficulty"] = "超大国"; p2["territory"] = 1100.0; st.rerun()
elif s["faction"] is None:
    st.title("陣営プロトコル")
    for f in ["連合国", "枢軸国", "社会主義国"]:
        if st.button(f, use_container_width=True): 
            s["faction"] = f
            if f == "社会主義国": s["player_ap"] = 1; s["max_ap"] = 1
            st.rerun()
else:
    st.markdown(f'<div class="enemy-banner"><span class="enemy-text">DEUS: {p2["territory"]:.0f}</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-row"><div><span class="stat-label">本国</span><span class="stat-val">{p1["territory"]:.0f}</span></div><div><span class="stat-label">緩衝</span><span class="stat-val">{p1["colony"]:.0f}</span></div></div>', unsafe_allow_html=True)
    
    lock_msg = " (⚠️LOCK)" if p1["nuke_lock"] > 0 else ""
    st.markdown(f'<p class="nuke-title">☢️ 核開発進行状況{lock_msg}</p>', unsafe_allow_html=True)
    st.progress(min(p1['nuke_point']/200.0, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        st.success("作戦終了" if p2["territory"] <= 0 else "敗北")
        if st.button("REBOOT", use_container_width=True): st.session_state.clear(); st.rerun()
    else:
        st.caption(f"T-{s['turn']} | AP: {s['player_ap']}")
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
    
