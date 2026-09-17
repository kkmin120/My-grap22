```python
import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# =========================================================
# 제목
# =========================================================

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 그래프로 살펴봅니다."
)


# =========================================================
# 데이터 불러오기
# =========================================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL)


df = load_data()


# =========================================================
# 데이터 전처리
# =========================================================

# 장르가 여러 개 적혀 있으면 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

df["genre_first"] = df["genre_first"].replace("", "미상")


# 숫자 데이터 변환
df["first_scrn"] = pd.to_numeric(
    df["first_scrn"],
    errors="coerce"
)

df["total_audi"] = pd.to_numeric(
    df["total_audi"],
    errors="coerce"
)


# =========================================================
# 그래프 1
# 장르별 영화 편수 - 도넛 그래프
# =========================================================

st.divider()

st.header("📊 그래프 1. 장르별 영화 편수")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = ["장르", "영화 편수"]


fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화 편수",
    hole=0.45,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    height=550,
    font=dict(size=16),
    legend_title_text="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "이 기간에 박스오피스 10위권에 든 영화는 어떤 장르가 많고, "
    "각 장르가 전체 영화에서 어느 정도의 비율을 차지하는지 알 수 있다."
)


# =========================================================
# 그래프 2
# 장르 안에 영화가 들어 있는 트리맵
# 크기 = 총 관객
# =========================================================

st.divider()

st.header("🌳 그래프 2. 장르별 영화와 총 관객")

treemap_df = df.dropna(
    subset=["total_audi", "movieNm"]
).copy()


fig2 = px.treemap(
    treemap_df,
    path=["genre_first", "movieNm"],
    values="total_audi",
    title="장르 안에 들어 있는 영화와 총 관객"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    font=dict(size=16)
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    "각 장르 안에서 어떤 영화가 많은 관객을 모았는지, "
    "영화별 총 관객 규모의 차이를 한눈에 비교할 수 있다."
)


# =========================================================
# 그래프 3
# 총 관객 수 히스토그램
# =========================================================

st.divider()

st.header("📈 그래프 3. 총 관객 수의 분포")

hist_df = df.dropna(
    subset=["total_audi"]
).copy()


fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 수 분포",
    labels={
        "total_audi": "총 관객 수",
        "count": "영화 편수"
    }
)

fig3.update_layout(
    height=550,
    font=dict(size=16),
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수"
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 수 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# 가장 많이 몰린 구간 계산
counts, bins = pd.cut(
    hist_df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True
)

bin_counts = counts.value_counts().sort_index()

most_common_bin = bin_counts.idxmax()

low = int(most_common_bin.left)
high = int(most_common_bin.right)


# 가장 관객이 많은 영화
max_movie = hist_df.loc[
    hist_df["total_audi"].idxmax()
]

max_movie_name = max_movie["movieNm"]
max_movie_audience = int(max_movie["total_audi"])


st.subheader("💡 이 그래프로 알 수 있는 것")

st.info(
    f"대부분의 영화는 총 관객 **{low:,}명 ~ {high:,}명** 구간에 "
    f"가장 많이 몰려 있으며, 총 관객이 가장 많은 영화는 "
    f"**{max_movie_name}**으로 약 **{max_movie_audience:,}명**의 "
    f"관객을 기록했다."
)


# =========================================================
# 그래프 4
# 개봉일 스크린수와 총 관객의 산점도
# =========================================================

st.divider()

st.header("🔵 그래프 4. 개봉일 스크린수와 총 관객의 관계")

scatter_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "movieNm"
    ]
).copy()


fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객 수",
        "genre_first": "장르"
    }
)

fig4.update_traces(
    marker=dict(size=10),
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
```
