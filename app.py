import streamlit as st
import random
import time

st.set_page_config(page_title="DEUS: Historical Strategy", layout="centered")

# --- 実際の記録映像・公共映像の埋め込み (YouTube等) ---
# ※Streamlitのvideo機能を使用します。リンクは実際の記録映像等に変更しています。
VIDEO_ASSETS = {
    "AIR": "https://www.youtube.com/watch?v=6id8pQY62rE",       # 爆撃機/空爆記録
    "ROCKET": "https://www.youtube.com/watch?v=ZfUf1m3_E7g",    # ロケット発射
    "NUKE": "https://www.youtube.com/watch?v=7uV_KscE-X0",      # 核実験（記録映像）
    "LAB": "https://www.youtube.com/watch?v=uKofV7uH3gU",       # 科学者・研究所（公文書）
    "DEFENSE": "https://www.youtube.com/watch?v=oXlZfGqGatA",   # 迎撃システム（広報映像）
    "INVASION": "https://www.youtube.com/watch?v=4uPZ6v6Teyo"   # ノルマンディー上陸作戦（記録）
}

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 50.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 難易度を選択してください。"],
        "player_ap": 2, 
        "wmd_charging": False,
        "ai_awakened": False,
        "difficulty": None,
        "effect": None,
        "march_count": 0,
        "colony_was_zero": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]:
        dmg *= 0.6 # 40%軽減
    
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if p1["colony"] <= 0 and not s["colony_was_zero"]:
            s["effect"] = (VIDEO_ASSETS["INVASION"], "🚨 占領地壊滅。本土への直接侵攻が開始されました。")
            s["colony_was_zero"] = True
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"💥 本国損害: {dmg:.1f}")

def ai_logic():
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    for _ in range(actions):
        if p2["territory"] <= 0: break
        if s["wmd_charging"]:
            apply_damage_to_player(p1["territory"] * 0.5, is_wmd=True)
            s["wmd_charging"] = False
        else:
            wmd_chance = 0.4 if s["ai_awakened"] else 0.1
            if random.random() < wmd_chance:
                s["wmd_charging"] = True
                s["logs"].insert(0, "⚠️ AIが核弾頭を充填しています。")
            else:
                apply_damage_to_player(p2["military"] * 0.25)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0
        p1["nuke_point"] += 20
        s["effect"] = (VIDEO_ASSETS["LAB"], "🔬 科学者による核開発の進捗報告。")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["effect"] = (VIDEO_ASSETS["DEFENSE"], "🛡️ 防空システムによる迎撃。")
    elif cmd == "MARCH":
        s["march_count"] += 1
        url = VIDEO_ASSETS["AIR"] if s["march_count"] == 1 else VIDEO_ASSETS["ROCKET"]
        cap = "✈️ 空爆作戦" if s["march_count"] == 1 else "🚀 ロケット発射"
        s["effect"] = (url, cap)
        p2["territory"] -= (p1["military"] * 0.5) + (p1["colony"] * 0.6)
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
    elif cmd == "NUKE":
        s["effect"] = (VIDEO_ASSETS["NUKE"], "☢️ 核抑止力の発動。")
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0

    if p1["military"] >= 100:
        p2["territory"] -= 100.0
        p1["military"] = 0
        s["logs"].insert(0, "💥 総進軍：全軍突撃。")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic()
        s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UIレイアウト ---
if s["difficulty"] is None:
    st.title("DEUS: Historical Strategy")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): s["difficulty"]="小国 (Easy)"; st.rerun()
    if cols[1].button("大国 (Normal)"): s["difficulty"]="大国 (Normal)"; st.rerun()
    if cols[2].button("超大国 (Hard)"): s["p2"]["territory"]=500.0; s["ai_awakened"]=True; s["difficulty"]="超大国 (Hard)"; st.rerun()
else:
    if s["effect"]:
        st.video(s["effect"][0]) # 実際の映像再生
        st.info(s["effect"][1])
        time.sleep(4) # 映像を少し長く見せるために4秒
        s["effect"] = None
        st.rerun()

    st.subheader(f"🟥 AI帝国 ({s['difficulty']})")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    if s["wmd_charging"]: st.error("🚨 敵WMD充填中")
    
    st.divider()

    st.subheader(f"🟦 プレイヤー | AP: {s['player_ap']}")
    st.metric("本国領土", f"{p1['territory']:.1f}", f"占領地:{p1['colony']:.1f}")
    
    c1, c2 = st.columns(2)
    c1.progress(p1['military']/100, f"軍事: {p1['military']}/100")
    c2.progress(min(p1['nuke_point']/200, 1.0), f"核開発: {p1['nuke_point']}/200")

    if p1["territory"] <= 0:
        st.error("国家が敗北しました。")
        if st.button("再始動"): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("勝利しました！")
        if st.button("再始動"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 核兵器発射", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        bc1, bc2 = st.columns(2)
        if bc1.button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.rerun()
        if bc2.button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.rerun()
        if bc1.button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if bc2.button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    st.divider()
    for log in s["logs"][:3]: st.caption(log)
