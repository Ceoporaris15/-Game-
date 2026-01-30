import streamlit as st
import random
import time

st.set_page_config(page_title="DEUS: Three Powers", layout="centered")

# --- 画像アセット（演出用） ---
IMG_AIR_STRIKE = "https://images.unsplash.com/photo-1517976384346-3136801d605d?auto=format&fit=crop&q=80&w=800" # 戦闘機
IMG_NUKE = "https://images.unsplash.com/photo-1515285761066-608677e5d263?auto=format&fit=crop&q=80&w=800" # 核爆発

if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"territory": 100.0, "military": 0.0, "colony": 20.0, "shield": False, "nuke_point": 0},
        "p2": {"territory": 300.0, "military": 100.0, "colony": 50.0, "shield": False},
        "turn": 1,
        "logs": ["SYSTEM: 難易度を選択して開始してください。"],
        "player_ap": 2, 
        "wmd_charging": False,
        "ai_awakened": False,
        "difficulty": None, # Easy, Normal, Hard
        "effect": None # 演出表示用
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# --- 難易度設定 ---
def set_difficulty(level):
    s["difficulty"] = level
    if level == "小国 (Easy)":
        s["p2"]["territory"] = 150.0
        s["p2"]["military"] = 30.0
    elif level == "超大国 (Hard)":
        s["p2"]["territory"] = 500.0
        s["p2"]["military"] = 100.0
        s["ai_awakened"] = True
    s["logs"] = [f"SYSTEM: 難易度【{level}】で開始。"]

# --- ダメージ処理 ---
def apply_damage_to_player(dmg, is_wmd=False):
    # 防衛の下方修正：ダメージを100%から40%カット(残り60%受ける)に変更
    if p1["shield"]:
        dmg *= 0.6
        s["logs"].insert(0, "🛡️ 防衛体制：被害を40%軽減。")

    if p1["colony"] > 0:
        shield_amt = min(p1["colony"], dmg)
        p1["colony"] -= shield_amt
        dmg -= shield_amt
        if shield_amt > 0:
            s["logs"].insert(0, f"🛡️ 占領地が {shield_amt:.1f} の被害を肩代わり。")
    
    if dmg > 0:
        p1["territory"] = max(0, p1["territory"] - dmg)
        s["logs"].insert(0, f"{'☢️' if is_wmd else '💥'} 本国が {dmg:.1f} の損害。")

# --- AIロジック ---
def ai_logic():
    # 行動回数の決定
    actions = 1 if s["difficulty"] == "小国 (Easy)" else 2
    
    # 覚醒判定 (Normalのみ)
    if s["difficulty"] == "大国 (Normal)" and not s["ai_awakened"]:
        if p1["military"] > 80 or p2["territory"] < 150 or p1["nuke_point"] > 100:
            s["ai_awakened"] = True
            s["logs"].insert(0, "🔴 WARNING: DEUS覚醒。")

    for _ in range(actions):
        if p2["territory"] <= 0: break
        
        # WMD発射
        if s["wmd_charging"]:
            nuke_dmg = p1["territory"] * 0.5
            apply_damage_to_player(nuke_dmg, is_wmd=True)
            s["wmd_charging"] = False
            continue

        choice = random.random()
        # WMDチャージ（Hardは確率高）
        wmd_chance = 0.4 if s["ai_awakened"] else 0.1
        if choice < wmd_chance and not s["wmd_charging"]:
            s["wmd_charging"] = True
            s["logs"].insert(0, "⚠️ ALERT: AIがWMDの充填を開始！")
        else:
            power = 1.6 if s["ai_awakened"] else 0.8
            dmg = p2["military"] * 0.25 * power
            apply_damage_to_player(dmg)

def player_step(cmd):
    s["effect"] = None
    if cmd == "DEVELOP": 
        p1["military"] += 25.0
        p1["nuke_point"] += 20 
    elif cmd == "DEFEND": 
        p1["shield"] = True
    elif cmd == "MARCH":
        s["effect"] = "AIR" # 空爆演出
        dmg = (p1["military"] * 0.5) + (p1["colony"] * 0.6)
        p2["territory"] -= dmg
        s["logs"].insert(0, f"🔵 Player: 進軍（AI領土-{dmg:.1f}）")
    elif cmd == "OCCUPY":
        if p1["military"] >= 20:
            p1["military"] -= 20
            steal = max(p2["territory"] * 0.20, 40.0)
            p2["territory"] -= steal
            p1["colony"] += steal
        else: return
    elif cmd == "NUKE":
        s["effect"] = "NUKE" # 核演出
        p2["territory"] *= 0.2
        p1["nuke_point"] = 0
        s["logs"].insert(0, "☢️🚀 FINAL JUDGEMENT!!")

    if p1["military"] >= 100:
        p2["territory"] -= 100.0
        p1["military"] = 0
        s["logs"].insert(0, "💥 BURST: 総進軍！")

    s["player_ap"] -= 1
    if s["player_ap"] <= 0:
        ai_logic()
        s["player_ap"] = 2
        s["turn"] += 1
        p1["shield"] = False

# --- UI (上下レイアウト) ---
if s["difficulty"] is None:
    st.subheader("🌐 難易度を選択してください")
    cols = st.columns(3)
    if cols[0].button("小国 (Easy)"): set_difficulty("小国 (Easy)"); st.rerun()
    if cols[1].button("大国 (Normal)"): set_difficulty("大国 (Normal)"); st.rerun()
    if cols[2].button("超大国 (Hard)"): set_difficulty("超大国 (Hard)"); st.rerun()
else:
    # --- 演出エリア ---
    if s["effect"] == "AIR":
        st.image(IMG_AIR_STRIKE, caption="✈️ 空爆開始...", use_container_width=True)
    elif s["effect"] == "NUKE":
        st.image(IMG_NUKE, caption="☢️ 最終宣告", use_container_width=True)

    # --- AI エリア (上段) ---
    st.subheader(f"🟥 DEUS ({s['difficulty']})")
    st.progress(max(0.0, min(p2['territory']/500, 1.0)))
    st.metric("AI領土", f"{p2['territory']:.1f}")
    if s["wmd_charging"]: st.error("🚨 WMDチャージ中")
    
    st.write("--- VS ---")

    # --- プレイヤー エリア (下段) ---
    st.subheader(f"🟦 Player (AP: {s['player_ap']})")
    st.metric("本国領土", f"{p1['territory']:.1f}")
    st.metric("占領地 (盾)", f"{p1['colony']:.1f}")
    
    col_st1, col_st2 = st.columns(2)
    col_st1.write(f"軍事: {p1['military']}/100")
    col_st1.progress(p1['military']/100)
    col_st2.write(f"核: {p1['nuke_point']}/200")
    col_st2.progress(min(p1['nuke_point']/200, 1.0))

    if p1["territory"] <= 0 or p2["territory"] <= 0:
        if p1["territory"] <= 0: st.error("敗北...")
        else: st.success("勝利！")
        if st.button("再起動"): st.session_state.clear(); st.rerun()
    else:
        # ボタンをスマホで見やすく大きく
        if p1["nuke_point"] >= 200:
            if st.button("🚀 核兵器発射", type="primary", use_container_width=True): player_step("NUKE"); st.rerun()
        
        c = st.columns(2)
        if c[0].button("🛠 開発", use_container_width=True): player_step("DEVELOP"); st.rerun()
        if c[1].button("🛡 防衛(40%減)", use_container_width=True): player_step("DEFEND"); st.rerun()
        if c[0].button("⚔️ 進軍", use_container_width=True): player_step("MARCH"); st.rerun()
        if c[1].button("🚩 占領", use_container_width=True): player_step("OCCUPY"); st.rerun()

    st.write("---")
    for log in s["logs"][:5]: st.text(log)
