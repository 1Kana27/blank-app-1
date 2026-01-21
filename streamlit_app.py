import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)

import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

st.set_page_config(page_title="学習支援アプリ", layout="wide")
st.title("📚 学習支援アプリ（プロトタイプ）")

# --- セッション状態でデータ保持 ---
if "records" not in st.session_state:
    st.session_state.records = []

# --- サイドバー：入力フォーム ---
st.sidebar.header("学習記録の入力")

with st.sidebar.form("input_form"):
    grade = st.selectbox("学年", ["小1", "小2", "小3", "小4", "小5", "小6"])
    subject = st.selectbox("教科", ["算数", "国語", "理科", "社会", "英語"])
    unit = st.text_input("単元名（例：わり算、分数）")
    score = st.number_input("テスト点数", 0, 100, 80)
    test_date = st.date_input("実施日", value=date.today())
    submitted = st.form_submit_button("記録する")

if submitted:
    st.session_state.records.append(
        {
            "date": test_date,
            "grade": grade,
            "subject": subject,
            "unit": unit if unit else "未入力",
            "score": score,
        }
    )
    st.sidebar.success("記録しました！")

# --- データフレーム化 ---
df = pd.DataFrame(st.session_state.records)

if df.empty:
    st.info("まだデータがありません。左のフォームから学習記録を追加してください。")
    st.stop()

# --- レイアウト分割 ---
col1, col2 = st.columns([1, 2])

# =========================
# ① 学習履歴一覧
# =========================
with col1:
    st.subheader("📄 学習履歴")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, height=400)

    # 直近の結果
    st.markdown("### 🔍 直近のテスト結果")
    latest = df.sort_values("date").iloc[-1]
    st.write(f"- 日付：{latest['date']}")
    st.write(f"- 学年：{latest['grade']}")
    st.write(f"- 教科：{latest['subject']}")
    st.write(f"- 単元：{latest['unit']}")
    st.write(f"- 点数：{latest['score']}点")

    # 提案ロジック
    latest_score = latest["score"]

    st.markdown("### 🎯 次にすべきことの提案")
    if latest_score >= 80:
        st.success("とても良い調子！この単元は合格ライン。次の単元に進んでOKです。")
        suggestion = "次の単元に進む"
    elif latest_score >= 60:
        st.warning("おおむね理解できていますが、少し不安もあります。軽い復習をしてから次に進むと安心です。")
        suggestion = "軽い復習をしてから進む"
    else:
        st.error("この単元はまだ定着していないかもしれません。復習プリントを重点的にやるのがおすすめです。")
        suggestion = "復習を優先する"

    st.write(f"👉 **おすすめアクション：{suggestion}**")

# =========================
# ② 可視化エリア
# =========================
with col2:
    st.subheader("📊 学習状況の可視化")

    # フィルタ（学年・教科）
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        grade_filter = st.multiselect("学年フィルタ", sorted(df["grade"].unique()), default=list(df["grade"].unique()))
    with f_col2:
        subject_filter = st.multiselect("教科フィルタ", sorted(df["subject"].unique()), default=list(df["subject"].unique()))

    filtered_df = df[
        (df["grade"].isin(grade_filter)) &
        (df["subject"].isin(subject_filter))
    ]

    if filtered_df.empty:
        st.warning("選択された条件に合うデータがありません。フィルタを変更してください。")
    else:
        # --- 単元ごとの平均点 ---
        st.markdown("#### 単元ごとの平均点")

        avg_df = (
            filtered_df.groupby(["subject", "unit"])["score"]
            .mean()
            .reset_index()
            .rename(columns={"score": "avg_score"})
        )

        chart = (
            alt.Chart(avg_df)
            .mark_bar()
            .encode(
                x=alt.X("unit:N", title="単元"),
                y=alt.Y("avg_score:Q", title="平均点"),
                color=alt.condition(
                    alt.datum.avg_score >= 80,
                    alt.value("seagreen"),
                    alt.condition(
                        alt.datum.avg_score >= 60,
                        alt.value("gold"),
                        alt.value("crimson"),
                    ),
                ),
                column=alt.Column("subject:N", title="教科"),
                tooltip=["subject", "unit", "avg_score"],
            )
            .properties(height=250)
        )

        st.altair_chart(chart, use_container_width=True)

        # --- 時系列の推移 ---
        st.markdown("#### 点数の推移（時系列）")

        line_chart_df = filtered_df.sort_values("date")

        line_chart = (
            alt.Chart(line_chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="日付"),
                y=alt.Y("score:Q", title="点数", scale=alt.Scale(domain=[0, 100])),
                color="subject:N",
                tooltip=["date", "subject", "unit", "score"],
            )
            .properties(height=300)
        )

        st.altair_chart(line_chart, use_container_width=True)

# =========================
# ③ ちょっと発展：苦手単元リスト
# =========================
st.subheader("🧩 苦手単元のリストアップ")

threshold = st.slider("苦手とみなす平均点のしきい値", 0, 100, 60)

weak_df = (
    df.groupby(["subject", "unit"])["score"]
    .mean()
    .reset_index()
    .rename(columns={"score": "avg_score"})
)

weak_df = weak_df[weak_df["avg_score"] < threshold].sort_values("avg_score")

if weak_df.empty:
    st.success("しきい値未満の苦手単元はありません。よく頑張っています！")
else:
    st.write("このあたりの単元を復習候補にすると良さそうです：")
    st.dataframe(weak_df.reset_index(drop=True), use_container_width=True)
