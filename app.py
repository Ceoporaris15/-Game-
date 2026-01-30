import streamlit as st
import random
import math

# ページ設定
st.set_page_config(page_title="国家間Game会改：絶望", layout="wide")
st.title("🌏 国家間Game会改：Overdrive")

# 初期化：目標100、AP増加しにくい設定で重厚感を出す
if 'state' not in st.session_state:
    st.session_state.state = {
        "p1": {"name": "Player", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "p2": {"name": "AI", "power": 10.0, "territory": 10.0, "military": 10.0, "colony": 0.0, "shield": False},
        "turn": 1,
        "logs": ["デウス・エクス・マキナ起動。人類に勝機なし。"],
        "ap": 2,
        "is_ai_turn": False
    }

s = st.session_state.state
p1, p2 = s["p1"], s["p2"]

# 計算式
def get_income(player):
    return (player["military"] * player["territory"]) * 0.15

def get_max_ap(player):
    return 2 + int(player["colony"] * 0.1)

# --- AI：プレイヤー殺戮特化ルーチン ---
def run_ai_logic():
    income = get_income(p2)
    p2["power"] += income
    p2["shield"] = False
    current_ap = get_max_ap(p2)
    
    while current_ap > 0:
        # プレイヤーの弱点を突く冷徹な判断
        can_kill_next = (p2["military"] * 0.4) >= p1["territory"]
        player_near_win = p1["power"] > 80
        
        # 1. トドメを刺せるなら全APを攻撃に注ぐ
        if can_kill_next:
            action = "ATTACK"
        # 2. プレイヤーが勝ちそうなら、奪ったAPで「占領」し経済成長を物理的に止める
        elif player_near_win and current_ap >= 2:
            action = "OCCUPY"
        # 3. プレイヤーの軍事が自分より高ければ「防衛」を1回混ぜて無力化する
        elif p1["military"] > p2["military"] + 5 and not p2["shield"]:
            action = "DEFEND"
        # 4. 攻撃こそ最大の防御：軍事が一定以下なら「軍拡」
        elif p2["military"] < 25:
            action = "MILITARY"
        # 5. プレイヤーの領土が削りやすいなら「占領」でリソース強奪
        elif current_ap >= 2 and p1["territory"] > 8:
            action = "OCCUPY"
        # 6. それ以外は「攻撃」で圧をかけ続ける
        else:
            action = "ATTACK"

        # 実行処理
        if action == "MILITARY":
            p2["military"] += 5; current_ap -= 1
            s["logs"].insert(0, "AI：軍備を拡張。破壊準備完了。")
        elif action == "DEFEND":
            p2["shield"] = True; p2["military"] = max(0, p2["military"]-3); current_ap -= 1
            s["logs"].insert(0, "AI：鉄壁の防衛。あなたの攻撃は予測済み。")
        elif action == "ATTACK":
            dmg = p2["military"] * 0.4
            if p1["shield"]: 
                dmg = 0; p1["shield"] = False
                s["logs"].insert(0, "AI：攻撃！...あなたは防衛に成功したが盾を失った。")
            else: 
                p1["territory"] -= dmg
                s["logs"].insert(0, f"AI：致命的な攻撃！領土を{dmg:.1f}喪失。")
            current_ap -= 1
        elif action == "OCCUPY":
            steal = p1["territory"] * 0.25
            p1["territory"] -= steal; p2["colony"] += steal; current_ap -= 2
            s["logs"].insert(0, f"AI：占領を強行。あなたの領土を植民地に変えた。")
        elif action == "ECONOMY": # AIは追い込まれた時だけ使う
            p2["power"] += 5; current_ap -= 1
            s["logs"].insert(0, "AI：経済演算中。勝利を確実にする。")

        if p2["power"] >= 100 or p1["territory"] <= 0: break

    s["turn"] += 1
    p1["power"] += get_income(p1)
    p1["shield"] = False
    s["ap"] = get_max_ap(p1)
    s["is_ai_turn"] = False

# --- メイン画面 ---


col1, col2 = st.columns(2)
with col1:
    st.subheader("🟦 Player")
    st.progress(min(p1['power']/100, 1.0), text=f"国力: {p1['power']:.1f}/100")
    st.metric("領土", f"{p1['territory']:.1f}", delta=f"軍事:{p1['military']:.1f}")
    st.caption(f"🚩 植民地: {p1['colony']:.1f}")

with col2:
    st.subheader("🟥 AI (Deus)")
    st.progress(min(p2['power']/100, 1.0), text=f"国力: {p2['power']:.1f}/100")
    st.metric("領土", f"{p2['territory']:.1f}", delta=f"軍事:{p2['military']:.1f}")
    st.caption(f"🚩 植民地: {p2['colony']:.1f}")

st.divider()

if p1["power"] >= 100 or p1["territory"] <= 0 or p2["power"] >= 100 or p2["territory"] <= 0:
    winner = "Player" if (p1["power"] >= 100 or p2["territory"] <= 0) else "AI"
    st.error(f"【終局】勝者：{winner}") if winner == "AI" else st.success(f"【奇跡】勝者：{winner}")
    if st.button("リブート"):
        st.session_state.clear(); st.rerun()
else:
    if not s["is_ai_turn"]:
        st.write(f"### TURN {s['turn']} | 命令権: {s['ap']} AP")
        btn = st.columns(5)
        if btn[0].button("🪖軍拡(1)"): p1["military"] += 4; s["ap"] -= 1; st.rerun()
        if btn[1].button("💰軍縮(1)"): p1["power"] += 5; s["ap"] -= 1; st.rerun()
        if btn[2].button("🛡️防衛(1)"): p1["shield"] = True; p1["military"] = max(0, p1["military"]-2); s["ap"] -= 1; st.rerun()
        if btn[3].button("⚔️攻撃(1)"):
            dmg = p1["military"] * 0.4
            if p2["shield"]: p2["shield"] = False; s["logs"].insert(0, "攻撃！AIの盾に阻まれた。")
            else: p2["territory"] -= dmg; s["logs"].insert(0, f"攻撃！AIに{dmg:.1f}の被害。")
            s["ap"] -= 1; st.rerun()
        if s["ap"] >= 2 and btn[4].button("🚩占領(2)"):
            steal = p2["territory"] * 0.2
            p2["territory"] -= steal; p1["colony"] += steal; s["ap"] -= 2; st.rerun()
        
        if s["ap"] <= 0:
            if st.button("ターンを渡す"): s["is_ai_turn"] = True; st.rerun()
    else:
        run_ai_logic(); st.rerun()

st.write("---")
for log in s["logs"][:5]: st.text(log)
