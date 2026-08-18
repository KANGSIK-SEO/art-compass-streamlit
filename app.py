from __future__ import annotations

import math
import re
from dataclasses import dataclass

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Art Compass · AI 미술관 추천",
    page_icon="🎨",
    layout="wide",
)


@dataclass(frozen=True)
class Artwork:
    title: str
    artist: str
    museum: str
    city: str
    year: str
    visual_tags: tuple[str, ...]
    caption: str
    description: str
    accent: str
    source_url: str


ARTWORKS = [
    Artwork("The Starry Night", "Vincent van Gogh", "MoMA", "뉴욕", "1889", ("파랑", "밤", "소용돌이", "풍경", "고독"), "푸른 밤하늘과 소용돌이치는 별빛 아래 조용한 마을", "강렬한 붓질과 청색 계열이 내면의 긴장과 밤의 정서를 전달한다.", "#3156A3", "https://www.moma.org/collection/works/79802"),
    Artwork("Water Lilies", "Claude Monet", "Musée de l'Orangerie", "파리", "1914-1926", ("파랑", "초록", "물", "연못", "평온", "인상주의"), "수면 위 수련과 반사된 하늘이 이어지는 고요한 풍경", "빛과 색의 변화에 집중한 인상주의 연작으로 몰입감 있는 전시 공간을 이룬다.", "#55A69B", "https://www.musee-orangerie.fr/en/node/197502"),
    Artwork("The Great Wave off Kanagawa", "Katsushika Hokusai", "The Met", "뉴욕", "ca. 1830-32", ("파랑", "바다", "파도", "역동", "일본", "판화"), "거대한 푸른 파도가 작은 배 위로 솟구치는 장면", "자연의 힘과 인간의 연약함을 선명한 윤곽과 프러시안 블루로 표현한다.", "#1F6C93", "https://www.metmuseum.org/art/collection/search/45434"),
    Artwork("The Scream", "Edvard Munch", "National Museum", "오슬로", "1893", ("빨강", "주황", "불안", "인물", "표현주의"), "붉은 하늘 아래 다리 위에서 비명을 지르는 듯한 인물", "왜곡된 선과 강한 색채가 불안과 실존적 긴장을 시각화한다.", "#D15A38", "https://www.nasjonalmuseet.no/en/collection/object/NG.M.00939"),
    Artwork("Girl with a Pearl Earring", "Johannes Vermeer", "Mauritshuis", "헤이그", "c. 1665", ("검정", "파랑", "노랑", "여성", "초상", "고요"), "어두운 배경에서 진주 귀걸이를 한 소녀가 돌아보는 초상", "부드러운 빛과 시선, 단순한 배경이 친밀하고 신비로운 분위기를 만든다.", "#C39B45", "https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring/"),
    Artwork("Impression, Sunrise", "Claude Monet", "Musée Marmottan Monet", "파리", "1872", ("주황", "파랑", "노을", "바다", "항구", "인상주의"), "안개 낀 항구 위로 주황빛 해가 떠오르는 풍경", "빠른 붓질과 보색 대비로 순간의 빛과 대기를 포착한다.", "#E47B4C", "https://www.marmottan.fr/en/collections/claude-monet/"),
    Artwork("Nighthawks", "Edward Hopper", "Art Institute of Chicago", "시카고", "1942", ("밤", "도시", "고독", "인물", "초록", "노랑"), "늦은 밤 밝은 식당 안에 떨어져 앉은 사람들", "도시의 빛과 비어 있는 거리로 현대인의 고립감을 강조한다.", "#47715D", "https://www.artic.edu/artworks/111628/nighthawks"),
    Artwork("The Fighting Temeraire", "J. M. W. Turner", "National Gallery", "런던", "1839", ("주황", "노을", "바다", "배", "쓸쓸", "풍경"), "노을 진 강 위에서 예인되는 오래된 전함", "사라지는 시대에 대한 애도와 빛의 장관을 함께 담은 풍경화다.", "#D8894B", "https://www.nationalgallery.org.uk/paintings/joseph-mallord-william-turner-the-fighting-temeraire"),
]


ALIASES = {
    "푸른": "파랑", "푸른색": "파랑", "blue": "파랑",
    "붉은": "빨강", "red": "빨강", "orange": "주황",
    "외로운": "고독", "외로움": "고독", "쓸쓸한": "쓸쓸",
    "sea": "바다", "ocean": "바다", "portrait": "초상",
    "sunset": "노을", "night": "밤", "woman": "여성",
}


def tokens(text: str) -> set[str]:
    clean = re.sub(r"[^0-9a-zA-Z가-힣]+", " ", text.lower())
    result = set(clean.split())
    for source, target in ALIASES.items():
        if source in clean:
            result.add(target)
    return result


def rank_score(rank: int | None, k: int = 60) -> float:
    return 0.0 if rank is None else 1.0 / (k + rank)


def search(query: str, city: str, top_k: int) -> list[dict]:
    query_tokens = tokens(query)
    candidates = [item for item in ARTWORKS if city == "전체" or item.city == city]

    image_rows, text_rows = [], []
    for art in candidates:
        visual = set(art.visual_tags)
        text = tokens(f"{art.caption} {art.description} {art.title} {art.artist} {art.museum} {art.city}")
        visual_hits = len(query_tokens & visual)
        text_hits = len(query_tokens & text)
        image_score = visual_hits / math.sqrt(max(1, len(visual)))
        text_score = text_hits / math.sqrt(max(1, len(text)))
        if city != "전체" and art.city == city:
            image_score += 0.15
            text_score += 0.15
        image_rows.append((art, image_score))
        text_rows.append((art, text_score))

    image_rows.sort(key=lambda row: row[1], reverse=True)
    text_rows.sort(key=lambda row: row[1], reverse=True)
    image_rank = {row[0].title: index + 1 for index, row in enumerate(image_rows)}
    text_rank = {row[0].title: index + 1 for index, row in enumerate(text_rows)}
    image_value = {row[0].title: row[1] for row in image_rows}
    text_value = {row[0].title: row[1] for row in text_rows}

    fused = []
    for art in candidates:
        i_rank = image_rank[art.title]
        t_rank = text_rank[art.title]
        fused.append({
            "art": art,
            "image_rank": i_rank,
            "text_rank": t_rank,
            "image_score": image_value[art.title],
            "text_score": text_value[art.title],
            "rrf_score": rank_score(i_rank) + rank_score(t_rank),
        })
    fused.sort(key=lambda row: (row["rrf_score"], row["image_score"] + row["text_score"]), reverse=True)
    return fused[:top_k]


st.markdown("""
<style>
  .stApp { background: #F3EEE4; color: #171512; }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { max-width: 1180px; padding-top: 2.4rem; }
  .brand { font: 800 .78rem/1.2 sans-serif; letter-spacing: .18em; color: #CB1F2B; }
  .hero { font: 900 clamp(2.3rem,6vw,5.6rem)/.98 sans-serif; letter-spacing: -.06em; max-width: 980px; margin: .8rem 0 1.2rem; }
  .dek { font-size: 1.12rem; line-height: 1.65; color: #5F594F; max-width: 820px; margin-bottom: 2rem; }
  .art-card { border-top: 3px solid #171512; padding: 1.1rem 0 1.5rem; margin-top: .5rem; }
  .rank { font: 800 .76rem/1 sans-serif; color: #CB1F2B; letter-spacing: .12em; }
  .art-title { font: 900 1.55rem/1.25 sans-serif; margin: .45rem 0 .2rem; }
  .meta { color: #625C53; font-size: .9rem; }
  .reason { font-size: 1rem; line-height: 1.65; margin: .8rem 0; }
  .status { display:inline-block; padding:.3rem .55rem; background:#E7DED0; font:700 .72rem/1 sans-serif; }
  .swatch { height: 8px; border-radius: 99px; margin: .75rem 0; }
  .pipeline { display:grid; grid-template-columns:repeat(4,1fr); gap:.5rem; margin:1rem 0 2rem; }
  .pipe { padding:.8rem; border:1px solid #BEB5A8; font:700 .76rem/1.35 sans-serif; background:rgba(255,255,255,.22); }
  @media(max-width:700px){ .pipeline{grid-template-columns:1fr 1fr;} }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">ART COMPASS · MULTIMODAL MUSEUM FINDER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">보고 싶은 그림을 말하면,<br>갈 미술관을 찾아드려요.</div>', unsafe_allow_html=True)
st.markdown('<div class="dek">색감, 분위기, 주제와 지역을 자유롭게 설명하세요. 이미지의 시각 특징과 작품 캡션·해설을 함께 검색한 뒤 RRF로 통합해 추천합니다.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("검색 설정")
    city = st.selectbox("도시", ["전체", "서울", "뉴욕", "파리", "런던", "시카고", "오슬로", "헤이그"])
    top_k = st.slider("추천 작품 수", 3, 6, 5)
    st.divider()
    st.caption("이 앱은 수업용 프로토타입입니다. 소장 미술관과 현재 전시 여부는 다르므로 방문 전 공식 링크에서 확인하세요.")

examples = [
    "푸른색이 많고 고독한 분위기의 바다 그림",
    "따뜻한 노을빛의 인상주의 풍경화",
    "도시의 밤과 외로움을 보여주는 작품",
    "강렬한 색채의 여성 초상화",
]

query = st.text_input("원하는 작품을 설명해 주세요", placeholder=examples[0])
selected_example = st.radio(
    "예시",
    ["직접 입력", *examples],
    horizontal=True,
    label_visibility="collapsed",
)
if selected_example != "직접 입력" and not query:
    query = selected_example

st.markdown("""
<div class="pipeline">
  <div class="pipe">01 · 자연어 요청</div>
  <div class="pipe">02 · CLIP 시각 검색</div>
  <div class="pipe">03 · BLIP 캡션·해설 검색</div>
  <div class="pipe">04 · RRF 통합 순위</div>
</div>
""", unsafe_allow_html=True)

if not query:
    st.info("위 예시를 선택하거나 원하는 작품의 느낌을 직접 입력해 보세요.")
    st.stop()

results = search(query, city, top_k)
st.subheader(f"추천 결과 · {len(results)}점")
st.caption(f'검색 문장: “{query}” · 소장 정보 기준이며 현재 전시는 공식 확인이 필요합니다.')

for index, row in enumerate(results, start=1):
    art = row["art"]
    left, right = st.columns([4, 1.25])
    with left:
        st.markdown(
            f'<div class="art-card"><div class="rank">RECOMMENDATION {index:02d}</div>'
            f'<div class="art-title">{art.title}</div>'
            f'<div class="meta">{art.artist} · {art.year} · {art.museum}, {art.city}</div>'
            f'<div class="swatch" style="background:{art.accent}"></div>'
            f'<div class="reason">{art.caption}<br><span style="color:#625C53">{art.description}</span></div>'
            f'<span class="status">현재 전시 여부 공식 확인 필요</span></div>',
            unsafe_allow_html=True,
        )
        st.link_button("공식 소장품 페이지", art.source_url)
    with right:
        st.metric("RRF 점수", f'{row["rrf_score"]:.4f}')
        st.write(f'CLIP 순위  **#{row["image_rank"]}**')
        st.write(f'텍스트 순위  **#{row["text_rank"]}**')

with st.expander("검색 점수 자세히 보기"):
    frame = pd.DataFrame([
        {
            "최종 순위": index,
            "작품": row["art"].title,
            "CLIP 순위": row["image_rank"],
            "텍스트 순위": row["text_rank"],
            "RRF 점수": round(row["rrf_score"], 6),
        }
        for index, row in enumerate(results, start=1)
    ])
    st.dataframe(frame, hide_index=True, use_container_width=True)
    st.caption("현재 데모는 작품 태그와 캡션을 사용해 CLIP·텍스트 검색 흐름을 가볍게 재현합니다. 실제 모델·ChromaDB 연결 시 같은 UI를 유지할 수 있습니다.")
