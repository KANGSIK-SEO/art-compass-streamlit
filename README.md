# Art Compass

원하는 그림의 색감·분위기·주제를 자연어로 입력하면 작품과 소장 미술관을 추천하는 Streamlit 수업용 프로토타입입니다.

## 실행

```bash
cd "/Users/kangsikseo/Desktop/비전수업/art_museum_streamlit"
streamlit run app.py
```

현재 버전은 가벼운 태그·캡션 점수로 CLIP/BLIP/RRF 흐름을 재현합니다. 이후 실제 CLIP 임베딩, BLIP 캡션, ChromaDB 컬렉션으로 검색 함수만 교체할 수 있습니다.
