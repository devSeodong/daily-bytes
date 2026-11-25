# 매일 아카이브하는 법

티스토리에 글 3편을 발행한 직후, 글마다 한 번씩 실행해요.

```bash
python3 scripts/add_post.py \
  --category ai-issue|ai-trend|dev-issue \
  --date YYYY-MM-DD \
  --slug 영문-키워드-슬러그 \
  --title "발행한 제목 그대로" \
  --url https://dongseodong.tistory.com/<글번호> \
  --tags "발행할 때 넣은 태그,쉼표로" \
  --html 발행한-본문.html \
  --cover 대표이미지.jpg
```

- 글 파일: `<카테고리>/<연>/<월>/<날짜>-<slug>.md` (front matter에 제목·날짜·티스토리 주소·태그)
- 대표 이미지: 같은 월 폴더의 `assets/`
- README(루트, 카테고리별)는 스크립트가 자동으로 다시 만들어요.

세 편을 다 넣은 뒤 한 번에 커밋해요.

```bash
git add -A && git commit -m "📝 YYYY-MM-DD 오늘의 IT 3편" && git push
```

필요한 것: python3, beautifulsoup4, pandoc
