# 어젯밤, 무슨 일이? 🌙 — 자동 갱신 모바일 뉴스레터

아이폰과 카카오톡에서 동일한 고정 URL로 열 수 있는 **네이비 모바일 뉴스 매거진**입니다.

## 준비물
- GitHub 계정 (무료 공개 저장소)
- 이 ZIP 안의 파일들

## 아이폰에서 설정하기
1. GitHub.com에 로그인 → **+ → New repository** → 이름을 `morning-news`로 입력하고 **Public**으로 생성합니다.
2. 저장소의 **Add file → Upload files**에서 ZIP을 푼 **내부 파일과 폴더**를 올립니다. `.github/workflows/update.yml` 같은 숨김 폴더는 아이폰 파일 앱에서 선택하기 어려울 수 있어, 처음 업로드는 PC가 더 쉽습니다. 폴더가 누락되면 GitHub 웹의 **Add file → Create new file**에서 `.github/workflows/update.yml` 경로로 만들고 이 ZIP의 내용을 붙여넣어도 됩니다.
3. **Settings → Pages → Build and deployment → Deploy from a branch** → Branch `main`, Folder `/docs` → Save.
4. **Settings → Actions → General → Workflow permissions**에서 **Read and write permissions**를 허용하고 저장합니다. 조직 정책에 따라 선택이 막혀 있을 수 있습니다.
5. **Actions → Update morning newsletter → Run workflow**를 한 번 눌러 초기 뉴스레터를 만듭니다. (Actions가 활성화되어 있어야 합니다.)
6. Pages가 게시되면 주소는 보통 `https://사용자명.github.io/morning-news/` 입니다. **정확한 주소는 Settings → Pages에서 확인**하세요. 그 주소를 재훈이에게 카톡으로 보내면 됩니다.

## 매일 업데이트
- `.github/workflows/update.yml`은 **한국 시간 매일 오전 7시(UTC 전날 22:00)**에 실행되도록 예약합니다.
- GitHub의 예약 실행은 지연되거나 일부 실행이 누락될 수 있어 **정각 7시 게시를 보장하지 않습니다**.
- GitHub는 비활성 공개 저장소의 예약 워크플로를 중단할 수 있습니다. Actions 화면에서 상태를 확인하세요.
- 기존 Netlify URL(`sprightly-biscochitos-899405.netlify.app`)은 **이 GitHub Pages 설정으로 자동 갱신되지 않습니다**. 새 GitHub Pages 고정 주소를 공유해야 합니다.

## 데이터·정확성
- Google 뉴스 RSS의 **기사 제목·언론사·발행 시각**만 자동 수집합니다. **기사 본문을 읽어 요약하거나 사실관계를 검증하는 AI 뉴스레터는 아닙니다.**
- 발행 시각이 **전날 18:00 이상 ~ 오늘 00:00 미만(KST)**인 기사만 담습니다. RSS 데이터가 불완전하거나 늦으면 일부 뉴스가 빠질 수 있습니다.
- 출처 버튼은 Google 뉴스 경유 링크일 수 있습니다. 제목과 보도 시각은 피드 제공 값이므로 원문과 다를 수 있습니다.
- 팬 코너는 **김준수 💗🥥 / 이창섭 🩵👍**를 항상 보여주지만, 공식 발표 일정의 자동 검증 기능은 아직 없습니다. 따라서 확인되지 않은 일정을 생성하지 않습니다.
- API 키나 유료 계정은 필요 없지만, RSS 접근 제한·GitHub 무료 사용 한도·서비스 정책 변경에 따라 동작이 달라질 수 있습니다.

## 파일 설명
- `template.html`: 모바일 네이비 매거진 디자인
- `build.py`: 기사 수집과 HTML 생성
- `.github/workflows/update.yml`: 매일 오전 7시 실행 예약
- `docs/index.html`: GitHub Pages에 공개할 페이지
- `docs/latest.json`: 마지막 생성 날짜 및 수집 상태

## 직접 테스트
`python3 build.py` 실행. 인터넷 접속이 없으면 뉴스 수집이 실패할 수 있지만, 오류 안내 페이지를 만듭니다.
