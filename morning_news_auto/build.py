#!/usr/bin/env python3
"""Generate Korean morning magazine using verifiable RSS metadata (stdlib only)."""
import datetime as dt, email.utils, html, json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

KST=ZoneInfo('Asia/Seoul'); NOW=dt.datetime.now(KST); ISSUE=NOW.date(); PREV=ISSUE-dt.timedelta(days=1)
START=dt.datetime.combine(PREV,dt.time(8),KST); END=dt.datetime.combine(ISSUE,dt.time(8),KST)
ROOT=Path(__file__).parent; OUT=ROOT/'docs'; OUT.mkdir(exist_ok=True)
SECTIONS=[
 ('📈 경제·금융', ['한국 경제 금융 물가 금리 증시', '한국 소비자 물가 월급 환율 주식', '대한민국 기업 실적 금융 시장']),
 ('👟 패션·유통 트렌드', ['나이키 아디다스 무신사 슈마커 폴더 패션 유통', '무신사 나이키 아디다스 신제품 협업 스니커즈', '슈마커 폴더 신발 매장 유통 패션 트렌드', '패션 유통 2030 인기 브랜드 소비 트렌드']),
 ('🏛 정치·외교', ['대한민국 정치 외교 주요 현안', '국회 정부 정책 정치', '한국 외교 국제 관계']),
 ('🚨 사회', ['대한민국 사회 사건 교육 노동', '한국 생활 교통 안전 사회 이슈', '청년 주거 취업 교육 사회']),
 ('🎬 연예·스포츠', ['한국 연예 아이돌 배우 공연', '한국 스포츠 주요 경기 선수', '한국 대중문화 연예 화제']),
 ('🌏 국제·기타', ['세계 국제 주요 뉴스', '해외 기술 AI 문화 트렌드', '국제 경제 세계 주요 이슈'])
]
AGENT='Mozilla/5.0 (compatible; MorningNewsMagazine/2.0)'
ARTISTS=[{'name':'김준수','emoji':'💗🥥','cls':'pink','youtube':'junsuxiaofficial','official':'https://www.instagram.com/palmtreeisland.official/'},{'name':'이창섭','emoji':'🩵👍','cls':'sky','youtube':'offclleechangsub','official':'https://www.instagram.com/leecs_official/'}]
def esc(x): return html.escape(str(x),quote=True)
def fetch(url,limit=1500000):
    req=urllib.request.Request(url,headers={'User-Agent':AGENT})
    with urllib.request.urlopen(req,timeout=22) as r:return r.read(limit)
def get_feed(query):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query+' when:2d','hl':'ko','gl':'KR','ceid':'KR:ko'})
    root=ET.fromstring(fetch(url)); result=[]
    for item in root.findall('./channel/item'):
        title=(item.findtext('title') or '').strip(); link=(item.findtext('link') or '').strip()
        source=item.find('source'); publisher=(source.text or '').strip() if source is not None else 'Google 뉴스'
        try: stamp=email.utils.parsedate_to_datetime(item.findtext('pubDate') or '').astimezone(KST)
        except Exception:continue
        if not START<=stamp<END or not link.startswith('https://news.google.com/'):continue
        if title.endswith(' - '+publisher):title=title[:-(len(publisher)+3)].strip()
        if len(title)<12:continue
        result.append({'title':title,'url':link,'publisher':publisher,'time':stamp.strftime('%H:%M'),'date':stamp.strftime('%m.%d')})
    return result

def relevance(title, heading):
    """Simple relevance score, not an AI editorial judgment."""
    t=title.lower()
    if '패션' in heading:
        brands=['나이키','nike','아디다스','adidas','무신사','슈마커','폴더','folder','스니커즈','운동화','패션','유통','브랜드','신발','콜라보','협업','트렌드','리테일','의류','매장']
        return sum(3 if w in ('나이키','아디다스','무신사','슈마커','폴더') else 1 for w in brands if w in t)
    return 1

def choose_articles(heading, queries, seen, errors):
    candidates=[]
    for query in queries:
        try:candidates.extend(get_feed(query))
        except Exception as e:errors.append(f'{heading}: {type(e).__name__}')
    # Different headlines about the same story are not always detectable; prefer distinct titles.
    unique={}
    for x in candidates:
        key=re.sub(r'\W+','',x['title']).lower()
        if key not in unique:unique[key]=x
    ordered=sorted(unique.values(),key=lambda x:(relevance(x['title'],heading),x['date'],x['time']),reverse=True)
    chosen=[]
    for x in ordered:
        key=re.sub(r'\W+','',x['title']).lower()
        if key in seen:continue
        if '패션' in heading and relevance(x['title'],heading)==0:continue
        seen.add(key);chosen.append(x)
        if len(chosen)==5:break
    return chosen

def article(x):
    # Only show facts actually present in the RSS metadata. Do not pretend
    # to have read the article body or manufacture a five-line summary.
    return (f'<article class="story"><span class="tag">{esc(x["date"])} {esc(x["time"])} 보도</span>'
            f'<h3>{esc(x["title"])}</h3>'
            f'<p class="article-publisher">📰 {esc(x["publisher"])}</p>'
            f'<div class="source">출처 · {esc(x["publisher"])} · {esc(x["time"])} KST<br>'
            f'<a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">기사 보기 (Google 뉴스 경유) ↗</a>'
            f'</div></article>')

def youtube_latest(handle):
    # Try both the channel homepage and Videos tab. YouTube sometimes omits
    # channelId metadata, so fall back to a public videoId on the Videos tab.
    pages=[]
    for path in ('/videos',''):
        try:
            pages.append(fetch('https://www.youtube.com/@'+handle+path,2_000_000).decode('utf-8','replace'))
        except Exception as e:
            print(f'YouTube @{handle}{path}: {type(e).__name__}: {e}')
    if not pages:
        raise RuntimeError('YouTube pages unavailable')
    channel_id=None
    for page in pages:
        for pattern in (r'<meta\s+itemprop="channelId"\s+content="(UC[\w-]+)"',
                        r'"channelId":"(UC[\w-]+)"',
                        r'"externalId":"(UC[\w-]+)"',
                        r'https://www.youtube.com/channel/(UC[\w-]+)'):
            match=re.search(pattern,page)
            if match:
                channel_id=match.group(1);break
        if channel_id:break
    if channel_id:
        try:
            atom=ET.fromstring(fetch('https://www.youtube.com/feeds/videos.xml?channel_id='+channel_id))
            ns={'a':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015'}
            entry=atom.find('a:entry',ns)
            if entry is not None:
                vid=entry.findtext('yt:videoId',default='',namespaces=ns)
                if re.fullmatch(r'[A-Za-z0-9_-]{11}',vid):
                    title=entry.findtext('a:title',default='최신 영상',namespaces=ns)
                    date=entry.findtext('a:published',default='',namespaces=ns)[:10]
                    return {'title':title,'date':date,'url':'https://www.youtube.com/watch?v='+vid,'thumb':'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg'}
        except Exception as e:
            print(f'YouTube RSS @{handle}: {type(e).__name__}: {e}')
    # Fallback: public channel videos page data, when available.
    for page in pages:
        match=re.search(r'"videoRenderer":\{[^{}]{0,250}"videoId":"([A-Za-z0-9_-]{11})"',page)
        if not match:
            match=re.search(r'"videoId":"([A-Za-z0-9_-]{11})"',page)
        if match:
            vid=match.group(1)
            title_match=re.search(r'"videoId":"'+re.escape(vid)+r'".{0,1500}?"title":\{"runs":\[\{"text":"([^"\\]*(?:\\.[^"\\]*)*)"',page)
            title='공식 채널 영상 보기'
            if title_match:
                try:title=json.loads('"'+title_match.group(1)+'"')
                except Exception:pass
            print(f'YouTube @{handle}: used public video page fallback')
            return {'title':title,'date':'','url':'https://www.youtube.com/watch?v='+vid,'thumb':'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg'}
    print(f'YouTube @{handle}: no public video ID found')
    return None

def fan_section():
    cards=[]; status={}
    for artist in ARTISTS:
        handle=artist['youtube']; vid=None
        try:vid=youtube_latest(handle)
        except Exception as e:status[handle]=type(e).__name__
        if vid:
            print(f'YouTube @{handle}: thumbnail ready')
            video=f'<a class="video" href="{esc(vid["url"])}" target="_blank" rel="noopener noreferrer"><img src="{esc(vid["thumb"])}" alt="{esc(artist["name"])} 공식 유튜브 최신 영상 썸네일" loading="lazy"><span class="play">▶</span></a><p class="video-title">🎬 {esc(vid["title"])}</p><p class="small">공식 유튜브 · {esc(vid["date"])}</p>'
        else:
            status[handle]='no video found'
            video=f'<div class="video-empty">🎬 최신 영상 정보를 가져오지 못했어요.<br><a href="https://www.youtube.com/@{esc(handle)}" target="_blank" rel="noopener noreferrer">공식 유튜브에서 확인 ↗</a></div>'
        schedule=(f'<div class="schedule"><h4>📅 다가오는 공식 일정</h4>'
                  '<p>공식 일정 자동 검증 연결 전입니다. 확인되지 않은 공연·방송 일정은 표시하지 않아요.</p></div>')
        cards.append(f'<div class="fan-card {artist["cls"]}"><h3>{esc(artist["name"])} {artist["emoji"]}</h3>{schedule}{video}</div>')
    return '<section class="fan"><h2>🎤 덕질 레이더</h2><p class="fan-intro">공식 일정 확인 현황과 최신 유튜브 영상을 한눈에 💌</p>'+''.join(cards)+'</section>',status

def render():
    seen=set(); blocks=[]; count=0; errors=[]
    for heading,queries in SECTIONS:
        chosen=choose_articles(heading,queries,seen,errors)
        if chosen:
            count+=len(chosen);blocks.append(f'<section class="section"><h2>{esc(heading)}</h2>'+''.join(map(article,chosen))+'</section>')
    if not count:blocks=['<section class="section"><h2>📰 오늘의 안내</h2><p>뉴스를 수집하지 못했어요. 확인되지 않은 기사는 싣지 않았습니다.</p></section>']
    fans,yt_status=fan_section()
    note='기사 제목과 발행 정보만 수집했습니다. 기사 본문 기반 요약 및 언론사 직접 링크는 아직 지원하지 않으며, 링크는 Google 뉴스 경유 링크입니다. 공식 일정 자동 검증도 아직 지원하지 않습니다.'
    if errors:note+=' 일부 뉴스 분야의 수집에 실패했습니다.'
    template=(ROOT/'template.html').read_text(encoding='utf-8')
    rendered=(template.replace('{{ISSUE}}',esc(ISSUE.strftime('%Y.%m.%d'))).replace('{{WINDOW}}',esc(f'{PREV:%Y.%m.%d} 08:00 ~ {ISSUE:%Y.%m.%d} 08:00 KST')).replace('{{COUNT}}',str(count)).replace('{{STORIES}}',''.join(blocks)).replace('{{FANS}}',fans).replace('{{NOTE}}',esc(note)))
    archive=OUT/'archive'; archive.mkdir(exist_ok=True)
    existing=sorted([f.stem for f in archive.glob('????-??-??.html') if re.fullmatch(r'\d{4}-\d{2}-\d{2}',f.stem)],reverse=True)
    dates=sorted(set(existing+[str(ISSUE)]),reverse=True)
    # The archive contains independent snapshots; previous issues are not overwritten.
    links=''.join(f'<a class="archive-link" href="{{{{BASE}}}}archive/{d}.html">{d} 아침호</a>' for d in dates[:30])
    calendar=f'<section class="archive-nav"><h2>📅 날짜별 뉴스레터</h2><label for="issue-date">날짜 선택</label><input id="issue-date" type="date" min="{dates[-1]}" max="{dates[0]}" value="{ISSUE}" aria-label="뉴스 날짜 선택"><p id="date-message" class="small">저장된 날짜만 열 수 있어요.</p><div class="archive-links">{links}</div></section>'
    js='<script>const dates='+json.dumps(dates)+';document.getElementById("issue-date").addEventListener("change",function(){const d=this.value;if(dates.includes(d)){location.href=window.NEWS_BASE+"archive/"+d+".html";}else{document.getElementById("date-message").textContent="이 날짜의 뉴스레터는 아직 저장되지 않았어요.";}});</script>' 
    def page(base):
        return rendered.replace('{{CALENDAR}}',calendar.replace('{{BASE}}',base)).replace('{{SCRIPT}}','<script>window.NEWS_BASE='+json.dumps(base)+';</script>'+js)
    (OUT/'index.html').write_text(page('./'),encoding='utf-8')
    (archive/(str(ISSUE)+'.html')).write_text(page('../'),encoding='utf-8')
    (archive/'index.json').write_text(json.dumps({'dates':dates},ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'latest.json').write_text(json.dumps({'issue':str(ISSUE),'count':count,'news_errors':errors,'youtube_errors':yt_status},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote docs/index.html ({count} articles; {len(errors)} news errors; {len(yt_status)} YouTube errors)')
if __name__=='__main__':render()
