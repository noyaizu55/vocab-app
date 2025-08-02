
import streamlit as st
import pandas as pd
import random
import datetime
import os

# --- 設定 ---
QUESTIONS_DIR = "questions"
WRONG_DIR = "wrong_answers"
DATE = datetime.date.today().isoformat()

# --- 初期化 ---
st.set_page_config(page_title="英単語テスト", layout="centered")
if not os.path.exists(WRONG_DIR):
    os.makedirs(WRONG_DIR)

# --- 問題ファイル選択 ---
files = [f for f in os.listdir(QUESTIONS_DIR) if f.endswith(".csv")]
selected_file = st.selectbox("問題ファイルを選択してください", files)

if selected_file:
    df = pd.read_csv(os.path.join(QUESTIONS_DIR, selected_file))
    df = df.sample(frac=1).reset_index(drop=True)  # シャッフル

    if len(df) > 10:
        df = df.iloc[:10]

    # --- セッション初期化 ---
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.wrong = []

    # --- JavaScript発音 ---
    def play_pronunciation(word):
        st.components.v1.html(f"""
        <script>
            const speak = () => {{
                const utterance = new SpeechSynthesisUtterance("{word}");
                utterance.lang = "en-US";
                speechSynthesis.speak(utterance);
            }};
            speak();
        </script>
        """, height=0)

    def play_pronunciation_button(word):
        st.components.v1.html(f"""
        <button onclick="const u=new SpeechSynthesisUtterance('{word}');u.lang='en-US';speechSynthesis.speak(u);">
            🔊 発音
        </button>
        """, height=40)

    # --- 出題処理 ---
    if st.session_state.index < len(df):
        row = df.iloc[st.session_state.index]
        st.markdown(f"### Q{st.session_state.index + 1}: 「{row['japanese']}」の英語は？")

        answer = st.text_input("英語で入力：", key=f"input_{st.session_state.index}")

        if st.button("答える"):
            if answer.strip().lower() == row["english"].strip().lower():
                st.success("正解！")
                st.session_state.score += 1
                play_pronunciation(row["english"])
            else:
                st.error(f"不正解。正解は「{row['english']}」")
                st.session_state.wrong.append(row)
                play_pronunciation(row["english"])
            play_pronunciation_button(row["english"])
            st.session_state.index += 1
            st.experimental_rerun()

    else:
        st.markdown("## 結果")
        st.write(f"{st.session_state.score} / {len(df)} 正解")

        if st.session_state.wrong:
            wrong_df = pd.DataFrame(st.session_state.wrong)
            file_path = os.path.join(WRONG_DIR, f"wrong_{DATE}.csv")

            # --- 既存ファイルがあれば追記、重複削除 ---
            if os.path.exists(file_path):
                existing = pd.read_csv(file_path)
                combined = pd.concat([existing, wrong_df]).drop_duplicates(subset=["id"])
            else:
                combined = wrong_df

            combined.to_csv(file_path, index=False)
            st.warning(f"間違えた単語を保存しました： {file_path}")
            st.dataframe(wrong_df)
        else:
            st.success("全問正解！おめでとうございます🎉")

        if st.button("もう一度やる"):
            st.session_state.index = 0
            st.session_state.score = 0
            st.session_state.wrong = []
            st.experimental_rerun()
