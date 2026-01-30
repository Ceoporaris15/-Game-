import streamlit as st
import random
import time

st.set_page_config(page_title="DEUS: Apocalypse Strategy", layout="centered")

# --- 演出用URL（演出の雰囲気を出すためのイメージ） ---
VIDEO_AIR_STRIKE = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJpbm56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/CE2xyYy6W7S9O/giphy.gif" # 爆撃
VIDEO_ROCKET = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNXBxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKyxqXloWIs9Nzs/giphy.gif" # ロケット
VIDEO_NUKE = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNm5xeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/HhTXt43pk1I1W/giphy.gif" # 核実験
VIDEO_LAB = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExN25xeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l41lTfuxNqHMeE8Ni/giphy.gif" # 研究
VIDEO_DEFENSE = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHNxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/l0IxYD16MqcAdpWF2/giphy.gif" # 迎撃
VIDEO_INVASION = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXNxeG56NmR6bm96amIxeHl6amR6amZ6amZ6amZ6amZ6amZ6amZ6JmVwPXYxX2ludGVybmFsX2dpZl9ieV9pZCZjdD1n/3o7TKVUn7iM8FMEU24/giphy.gif" # ノルマンディー

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

def set_difficulty(level):
    s["difficulty"] = level
    if level == "小国 (Easy)":
        s["p2"]["territory"], s["p2"]["military"] = 150.0, 30.0
    elif level == "超大国 (Hard)":
        s["p2"]["territory"], s["p2"]["military"] = 500.0, 100.0
        s["ai_awakened"] = True
    s["logs"] = [f"SYSTEM: 難易度【{level}】で開始。"]

def apply_damage_to_player(dmg, is_wmd=False):
    if p1["shield"]:
        dmg *= 0.6
        s["logs"].insert(0, "🛡️ 迎撃システム稼働：被害を40%軽減。")
    
    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if p1["colony"] <= 0 and not s["colony_was_zero"]:
            s["effect"] = (VIDEO_INVASION, "🚨 占領地壊滅！ノルマンディー上陸作戦：本土侵攻が開始されました！")
            s["colony_was_zero"] = True
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"{'☢️' if is_wmd else '💥'} 本国に {dmg:.1f} のダメージ。")

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
                s["logs"].insert(0, "⚠️ ALERT: AIが核ミサイルを充填中。")
            else:
                power = 1.6 if s["ai_awakened"] else 0.8
                apply_damage_to_player(p2["military"] * 0.2 * power)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP":
        p1["military"] += 25.0
        p1["nuke_point"] += 20
        s["effect"] = (VIDEO_LAB, "🔬 科学者報告：核兵器の研究が進行中。")
    elif cmd == "DEFEND":
        p1["shield"] = True
        s["effect"] = (VIDEO_DEFENSE, "🛡️ 防衛体制：爆撃機・ロケットを迎撃中。")
    elif cmd == "MARCH":
        s["march_count"] += 1
        s["effect"] = (VIDEO_AIR_STRIKE, "✈️ 初回限定：大規模空爆作戦。") if s["march_count"] == 1 else (VIDEO_ROCKET, "🚀 ロケット進軍：AI本国を狙撃。")
        p2["territory"] -= (p1["military"] * 0.5) + (p1["colony"] * 0.6)
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
    elif cmd == "NUKE":
        s["effect"] = (VIDEO_NUKE, "☢️ 核実験成功：AI領土の80%が蒸発。")
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0

    if p1["military"] >= 100:
        p2["territory"] -= 100.0
        p1["military"] = 0
        s["logs"].insert(0, "💥 総進軍バースト！")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic()
        s["player_ap"], s["turn"], p1["shield"] = 2, s["turn"] + 1, False

# --- UI表示 ---
if s["difficulty"] is None:
    st.title("⚔️ DEUS: Apocalypse Strategy")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): set_difficulty("小国 (Easy)"); st.rerun()
    if cols[1].button("大国 (Normal)"): set_difficulty("大国 (Normal)"); st.rerun()
    if cols[2].button("超大国 (Hard)"): set_difficulty("超大国 (Hard)"); st.rerun()
else:
    if s["effect"]:
        st.image(s["effect"][0], caption=s["effect"][1], use_container_width=True)
        time.sleep(2)
        s["effect"] = None
        st.rerun()

    st.subheader(f"🟥 DEUS ({s['difficulty']}) | AI領土: {p2['territory']:.1f}")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    if s["wmd_charging"]: st.error("🚨 AI WMDチャージ中")
    
    st.divider()

    st.subheader(f"🟦 Player | AP: {s['player_ap']}")
    st.metric("本国領土", f"{p1['territory']:.1f}", delta=f"占領地:{p1['colony']:.1f}")
    
    c1, c2 = st.columns(2)
    c1.progress(p1['military']/100, text=f"軍事: {p1['military']}/100")
    c2.progress(min(p1['nuke_point']/200, 1.0), text=f"核: {p1['nuke_point']}/200")

    if p1["territory"] <= 0:
        st.error("【敗北】国家は壊滅しました。")
        if st.button("再試行"): st.session_state.clear(); st.rerun()
    elif p2["territory"] <= 0:
        st.success("【勝利】AI帝国を打倒しました！")
        if st.button("再試行"): st.session_state.clear(); st.rerun()
    else:
        if p1["nuke_point"] >= 200:
            if st.button("🚀 核兵器使用", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        bc1, bc2 = st.columns(2)
        if bc1.button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.rerun()
        if bc2.button("🛡 防衛", use_container_width=True): player_step("DEFEND"); st.rerun()
        if bc1.button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if bc2.button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    st.divider()
    for log in s["logs"][:5]: st.caption(log)
