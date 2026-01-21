import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="学習支援アプリ", layout="wide")
st.title("📘 学習支援アプリ（5教科＋関連単元＋得意/苦手可視化）")

# =========================================
# ① 学年 × 教科 × 単元データ
# =========================================
UNIT_LIST = {
    "小1": {
        "国語": ["ひらがな", "カタカナ", "語彙", "物語文", "説明文"],
        "算数": ["たし算", "ひき算", "時計", "図形の基礎"],
        "英語": ["あいさつ", "アルファベット"],
        "理科": ["季節と生き物"],
        "社会": ["学校の生活"]
    },
    "小2": {
        "国語": ["漢字", "物語文", "説明文", "語彙"],
        "算数": ["かけ算", "長さ", "かさ", "図形"],
        "英語": ["単語", "簡単な会話"],
        "理科": ["生き物の観察", "天気"],
        "社会": ["町の様子"]
    },
    "小3": {
        "国語": ["漢字", "物語文", "説明文", "敬語"],
        "算数": ["わり算", "分数", "小数", "表とグラフ"],
        "英語": ["単語", "簡単な文", "自己紹介"],
        "理科": ["植物", "昆虫", "光と音", "磁石"],
        "社会": ["市の様子", "仕事とくらし"]
    },
    "小4": {
        "国語": ["漢字", "説明文", "物語文", "熟語"],
        "算数": ["角度", "面積", "分数の計算", "小数の計算"],
        "英語": ["単語", "文の基本", "会話"],
        "理科": ["水の変化", "電気", "人体", "天気"],
        "社会": ["都道府県", "産業"]
    },
    "小5": {
        "国語": ["漢字", "説明文", "物語文", "文法"],
        "算数": ["割合", "速さ", "体積", "図形"],
        "英語": ["文法", "会話", "リスニング"],
        "理科": ["植物の発芽", "ふりこ", "電流", "天体"],
        "社会": ["日本の地理", "歴史の学習"]
    },
    "小6": {
        "国語": ["漢字", "説明文", "物語文", "論説文"],
        "算数": ["比例・反比例", "分数の計算", "図形", "データの活用"],
        "英語": ["文法", "会話", "スピーキング"],
        "理科": ["電気", "水溶液", "生物", "地層"],
        "社会": ["歴史", "政治", "国際理解"]
    }
}

# =========================================
# ② 関連単元（復習のつながり）
# =========================================
RELATED_UNITS = {
    # 算数
    "わり算": ["かけ算", "たし算", "ひき算"],
    "分数": ["倍数・約数", "かけ算", "わり算"],
    "分数の計算": ["分数", "倍数・約数"],
    "小数": ["たし算", "ひき算"],
    "割合": ["分数", "小数"],
    "速さ": ["割合", "単位変換"],
    "比例・反比例": ["割合", "速さ"],

    # 国語
    "説明文": ["接続語", "段落構成"],
    "物語文": ["語彙", "漢字"],
    "論説文": ["説明文", "語彙"],

    # 英語
    "文法": ["単語", "語順"],
    "会話": ["単語", "発音"],
    "スピーキング": ["単語", "会話"],

    # 理科
    "電気": ["回路の基本"],
    "水溶液": ["物質の性質"],
    "天体": ["地球の動き"],

    # 社会
    "歴史": ["地理の基礎"],
    "政治": ["社会の仕組み"],
}

# =========================================
# ③ データ保存
# =========================================
if "records" not in st.session_state:
    st.session_state.records = []

# =========================================
# ④ 入力フォーム
# =========================================
st.sidebar.header("📥 学習記録の入力")

with st.sidebar.form("input_form"):
    grade = st.selectbox("学年", list(UNIT_LIST.keys()))
    subject = st.selectbox("教科", list(UNIT_LIST[grade].keys()))
    unit = st.selectbox("単元", UNIT_LIST[grade][subject])

    score = st.number_input("テスト点数", 0, 100, 80)
    test_date = st.date_input("実施日", value=date.today())

    submitted = st.form_submit_button("記録する")

if submitted:
    st.session_state.records.append(
        {
            "date": test_date,
            "grade": grade,
            "subject": subject,
            "unit": unit,
            "score": score,
        }
    )
    st.sidebar.success("記録しました！")

# =========================================
# ⑤ データ表示
# =========================================
df = pd.DataFrame(st.session_state.records)

if df.empty:
    st.info("まだデータがありません。左のフォームから記録を追加してください。")
    st.stop()

col1, col2 = st.columns([1, 2])

# =========================================
# ⑥ 学習履歴
# =========================================
with col1:
    st.subheader("📄 学習履歴")
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True, height=400)

    latest = df.sort_values("date").iloc[-1]

    st.markdown("### 🔍 直近のテスト結果")
    st.write(f"- 日付：{latest['date']}")
    st.write(f"- 学年：{latest['grade']}")
    st.write(f"- 教科：{latest['subject']}")
    st.write(f"- 単元：{latest['unit']}")
    st.write(f"- 点数：{latest['score']}点")

    st.markdown("### 🎯 次にすべきこと")
    if latest["score"] >= 80:
        st.success("とても良い調子！次の単元に進んでOK。")
    elif latest["score"] >= 60:
        st.warning("理解はできていますが、軽い復習をしてから進むと安心。")
    else:
        st.error("苦手の可能性あり。復習を優先しましょう。")

    # 関連単元の提案
    st.markdown("### 🔗 関連単元の復習提案")
    if latest["unit"] in RELATED_UNITS:
        st.write("この単元が苦手な場合、次の単元を復習すると効果的です：")
        for r in RELATED_UNITS[latest["unit"]]:
            st.write(f"- {r}")
    else:
        st.write("関連単元データはありません。")

# =========================================
# ⑦ 可視化（平均点・時系列）
# =========================================
with col2:
    st.subheader("📊 学習状況の可視化")

    f1, f2 = st.columns(2)
    with f1:
        grade_filter = st.multiselect("学年フィルタ", sorted(df["grade"].unique()), default=list(df["grade"].unique()))
    with f2:
        subject_filter = st.multiselect("教科フィルタ", sorted(df["subject"].unique()), default=list(df["subject"].unique()))

    filtered_df = df[
        (df["grade"].isin(grade_filter)) &
        (df["subject"].isin(subject_filter))
    ]

    if filtered_df.empty:
        st.warning("選択された条件に合うデータがありません。")
    else:
        st.markdown("#### 単元ごとの平均点")

        avg_df = (
            filtered_df.groupby(["grade", "subject", "unit"])["score"]
            .mean()
            .reset_index()
            .rename(columns={"score": "avg_score"})
        )

        chart = (
            alt.Chart(avg_df)
            .mark_bar()
            .encode(
                x="unit:N",
                y="avg_score:Q",
                color=alt.condition(
                    alt.datum.avg_score >= 80,
                    alt.value("seagreen"),
                    alt.condition(
                        alt.datum.avg_score >= 60,
                        alt.value("gold"),
                        alt.value("crimson"),
                    ),
                ),
                column="subject:N",
                tooltip=["grade", "subject", "unit", "avg_score"],
            )
            .properties(height=250)
        )

        st.altair_chart(chart, use_container_width=True)

        st.markdown("#### 点数の推移（時系列）")

        line_chart = (
            alt.Chart(filtered_df.sort_values("date"))
            .mark_line(point=True)
            .encode(
                x="date:T",
                y=alt.Y("score:Q", scale=alt.Scale(domain=[0, 100])),
                color="subject:N",
                tooltip=["date", "subject", "unit", "score"],
            )
            .properties(height=300)
        )

        st.altair_chart(line_chart, use_container_width=True)

# =========================================
# ⑧ 得意・苦手の可視化（レーダーチャート）
# =========================================
st.subheader("🌟 得意・苦手の可視化（レーダーチャート）")

subject_avg = (
    df.groupby("subject")["score"]
    .mean()
    .reset_index()
    .rename(columns={"score": "avg_score"})
)

if not subject_avg.empty:
    categories = subject_avg["subject"].tolist()
    values = subject_avg["avg_score"].tolist()

    values += values[:1]
    categories += categories[:1]

    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="平均点",
                line=dict(color="royalblue")
            )
        ]
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================
# ⑨ 苦手単元リスト
# =========================================
st.subheader("🧩 苦手単元のリストアップ")

threshold = st.slider("苦手とみなす平均点のしきい値", 0, 100, 60)

weak_df = (
    df.groupby(["grade", "subject", "unit"])["score"]
    .mean()
    .reset_index()
    .rename(columns={"score": "avg_score"})
)

weak_df = weak_df[weak_df["avg_score"] < threshold].sort_values("avg_score")

if weak_df.empty:
    st.success("苦手単元はありません。よく頑張っています。")
else:
    st.write("復習候補の単元：")
    st.dataframe(weak_df.reset_index(drop=True), use_container_width=True)
