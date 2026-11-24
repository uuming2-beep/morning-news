# 어젯밤, 무슨 일이? 무료 RSS판
유료 API 및 API 키 불필요. 공개 GitHub 저장소의 무료 표준 Actions와 Pages를 전제로 합니다. 비공개 저장소는 요금제 및 무료 한도 확인이 필요합니다.
1. 기존 저장소를 백업하고 압축을 풀어 루트에 업로드합니다. 숨김 폴더 .github도 포함합니다. 기존 docs는 삭제하지 않습니다. 중복 workflow는 비활성화합니다.
2. Actions → Morning newsletter → Run workflow. Settings → Pages → Deploy from a branch → main /docs. 매일 08:10 KST 실행 목표이며 지연될 수 있습니다. GITHUB_TOKEN으로 푸시한 경우 Pages 자동 배포가 시작되지 않을 수 있으므로 별도 Pages 배포 설정이 필요합니다.
3. Google 뉴스 RSS의 제목·매체·시각·기사 이동 링크를 수집합니다. 분야별 최대 5건, 전날 08시~당일 08시. 기사 전문 요약 및 AI 쉬운 말 풀이는 제공하지 않으며 등록된 용어만 설명합니다. 트렌드는 검색 결과이지 인기 순위가 아닙니다.
4. Yahoo Finance 일봉 종가로 코스피와 환율을 표시합니다. 은행 매매기준율이 아닙니다. 제공처의 거래일 및 시각 차이가 있을 수 있습니다. 실패 시 확인 필요로 표시합니다.
5. fans.json에 검증한 공식 유튜브 채널 ID(channel_id, UC로 시작)를 등록하면 RSS에서 최신 영상을 수집합니다. 일정은 schedule에 date(YYYY-MM-DD HH:mm), title, place, source, url을 직접 등록합니다. 자동 일정 검색은 미지원입니다.
6. 외부 RSS/시세 서비스는 무료 공개 접근이 가능한 경우에만 동작하며 제한이나 변경이 있을 수 있습니다. 실제 네트워크 실행은 검증하지 않았습니다.
