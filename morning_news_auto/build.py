#!/usr/bin/env python3
"""Generate Korean morning magazine using verifiable RSS metadata (stdlib only)."""
import datetime as dt, email.utils, html, json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

KST=ZoneInfo('Asia/Seoul'); NOW=dt.datetime.now(KST); ISSUE=NOW.date(); PREV=ISSUE-dt.timedelta(days=1)
START=dt.datetime.combine(PREV,dt.time(18),KST); END=dt.datetime.combine(ISSUE,dt.time(0),KST)
ROOT=Path(__file__).parent; OUT=ROOT/'docs'; OUT.mkdir(exist_ok=True)
SECTIONS=[('📈 경제·금융','한국 경제 금융 환율 증시'),('🏛 정치·외교','정치 외교 대한민국'),('🚨 사회','대한민국 사회 사건 교육'),('🎬 연예·스포츠','한국 연예 스포츠'),('🌏 국제·기타','국제 세계 주요 뉴스')]
AGENT='Mozilla/5.0 (compatible; MorningNewsMagazine/2.0)'
ARTISTS=[{'name':'김준수','emoji':'💗🥥','cls':'pink','youtube':'junsuxiaofficial','insta':[('개인 인스타그램','xiaxiaxia1215'),('팜트리아일랜드','palmtreeisland.official')]},{'name':'이창섭','emoji':'🩵👍','cls':'sky','youtube':'offclleechangsub','insta':[('개인 인스타그램','lee_cs_btob'),('공식 인스타그램','leecs_official')]}]
def esc(x): return html.escape(str(x),quote=True)
def fetch(url,limit=1500000):
    req=urllib.request.Request(url,headers={'User-Agent':AGENT})
    with urllib.request.urlopen(req,timeout=22) as r:return r.read(limit)
def get_feed(query):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query+' when:1d','hl':'ko','gl':'KR','ceid':'KR:ko'})
    root=ET.fromstring(fetch(url)); result=[]
    for item in root.findall('./channel/item'):
        title=(item.findtext('title') or '').strip(); link=(item.findtext('link') or '').strip()
        source=item.find('source'); publisher=(source.text or '').strip() if source is not None else 'Google 뉴스'
        try: stamp=email.utils.parsedate_to_datetime(item.findtext('pubDate') or '').astimezone(KST)
        except Exception:continue
        if not START<=stamp<END or not link.startswith('https://news.google.com/'):continue
        if title.endswith(' - '+publisher):title=title[:-(len(publisher)+3)].strip()
        if len(title)<12:continue
        result.append({'title':title,'url':link,'publisher':publisher,'time':stamp.strftime('%H:%M')})
    return result

def article(x):
    # Five concise factual lines; NOT a fabricated five-line article summary.
    lines=[('핵심 제목',x['title']),('보도 매체',x['publisher']),('보도 시각',f"어젯밤 {x['time']} (한국 시간)"),('확인 범위','기사 제목과 공개 발행 정보만 확인했어요.'),('자세한 내용','아래 원문 링크에서 사실관계와 배경을 확인해 주세요.')]
    info=''.join(f'<li><b>{esc(k)}</b> {esc(v)}</li>' for k,v in lines)
    return f'<article class="story"><span class="tag">어젯밤 {esc(x["time"])} 보도</span><h3>{esc(x["title"])}</h3><ul class="five-lines">{info}</ul><div class="source">출처 · {esc(x["publisher"])} · {esc(x["time"])} KST<br><a href="{esc(x["url"])}" target="_blank" rel="noopener noreferrer">Google 뉴스에서 기사 읽기 ↗</a></div></article>'

def youtube_latest(handle):
    # YouTube public page provides channel ID; then official Atom feed provides video metadata.
    page=fetch('https://www.youtube.com/@'+handle,700000).decode('utf-8','replace')
    match=re.search(r'<meta\s+itemprop="channelId"\s+content="(UC[\w-]+)"',page) or re.search(r'"channelId":"(UC[\w-]+)"',page)
    if not match:return None
    atom=ET.fromstring(fetch('https://www.youtube.com/feeds/videos.xml?channel_id='+match.group(1)))
    ns={'a':'http://www.w3.org/2005/Atom','yt':'http://www.youtube.com/xml/schemas/2015'}
    entry=atom.find('a:entry',ns)
    if entry is None:return None
    vid=entry.findtext('yt:videoId',default='',namespaces=ns)
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}',vid):return None
    title=entry.findtext('a:title',default='최신 영상',namespaces=ns)
    published=entry.findtext('a:published',default='',namespaces=ns)[:10]
    return {'title':title,'date':published,'url':'https://www.youtube.com/watch?v='+vid,'thumb':'https://i.ytimg.com/vi/'+vid+'/hqdefault.jpg'}

def fan_section():
    cards=[]; status={}
    for artist in ARTISTS:
        handle=artist['youtube']; vid=None
        try:vid=youtube_latest(handle)
        except Exception as e:status[handle]=type(e).__name__
        if vid:
            video=f'<a class="video" href="{esc(vid["url"])}" target="_blank" rel="noopener noreferrer"><img src="{esc(vid["thumb"])}" alt="{esc(artist["name"])} 공식 유튜브 최신 영상 썸네일" loading="lazy"><span class="play">▶</span></a><p class="video-title">🎬 {esc(vid["title"])}</p><p class="small">공식 유튜브 · {esc(vid["date"])}</p>'
        else:
            video=f'<div class="video-empty">🎬 최신 영상 정보를 가져오지 못했어요.<br><a href="https://www.youtube.com/@{esc(handle)}" target="_blank" rel="noopener noreferrer">공식 유튜브에서 확인 ↗</a></div>'
        social=''.join(f'<a href="https://www.instagram.com/{esc(username)}/" target="_blank" rel="noopener noreferrer">📸 {esc(label)} ↗</a>' for label,username in artist['insta'])
        cards.append(f'<div class="fan-card {artist["cls"]}"><h3>{esc(artist["name"])} {artist["emoji"]}</h3>{video}<div class="social-links">{social}<a href="https://www.youtube.com/@{esc(handle)}" target="_blank" rel="noopener noreferrer">▶ 공식 유튜브 ↗</a></div><p class="small">인스타그램 사진은 플랫폼 접근 제한으로 자동 표시하지 않아요. 공식 계정 링크에서 최신 게시물을 확인해 주세요.</p></div>')
    return '<section class="fan"><h2>🎤 덕질 레이더</h2><p class="fan-intro">공식 유튜브 최신 영상과 인스타그램 계정을 한눈에 💌</p>'+''.join(cards)+'</section>',status

def render():
    seen=set(); blocks=[]; count=0; errors=[]
    for heading,query in SECTIONS:
        try:candidates=get_feed(query)
        except Exception as e:errors.append(f'{heading}: {type(e).__name__}');candidates=[]
        chosen=[]
        for x in candidates:
            norm=re.sub(r'\W+','',x['title']).lower()
            if norm in seen:continue
            seen.add(norm);chosen.append(x)
            if len(chosen)==3:break
        if chosen:
            count+=len(chosen);blocks.append(f'<section class="section"><h2>{esc(heading)}</h2>'+''.join(map(article,chosen))+'</section>')
    if not count:blocks=['<section class="section"><h2>📰 오늘의 안내</h2><p>뉴스를 수집하지 못했어요. 확인되지 않은 기사는 싣지 않았습니다.</p></section>']
    fans,yt_status=fan_section()
    note='기사 제목과 발행 정보로 구성한 5줄 안내이며, 기사 본문을 읽고 검증한 5줄 요약은 아닙니다. 원문 링크를 확인해 주세요. 인스타그램 사진 자동 수집은 지원하지 않습니다.'
    if errors:note+=' 일부 뉴스 분야의 수집에 실패했습니다.'
    template=(ROOT/'template.html').read_text(encoding='utf-8')
    rendered=(template.replace('{{ISSUE}}',esc(ISSUE.strftime('%Y.%m.%d'))).replace('{{WINDOW}}',esc(f'{PREV:%Y.%m.%d} 18:00~24:00 KST')).replace('{{COUNT}}',str(count)).replace('{{STORIES}}',''.join(blocks)).replace('{{FANS}}',fans).replace('{{NOTE}}',esc(note)))
    (OUT/'index.html').write_text(rendered,encoding='utf-8')
    (OUT/'latest.json').write_text(json.dumps({'issue':str(ISSUE),'count':count,'news_errors':errors,'youtube_errors':yt_status},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote docs/index.html ({count} articles; {len(errors)} news errors; {len(yt_status)} YouTube errors)')
if __name__=='__main__':render()
