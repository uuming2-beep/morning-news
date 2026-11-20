#!/usr/bin/env python3
"""Generate a Korean mobile news magazine from timestamped Google News RSS headlines.
No AI summary: do not infer facts absent from titles. No external Python dependencies.
"""
import datetime as dt, email.utils, html, json, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

KST=ZoneInfo('Asia/Seoul')
NOW=dt.datetime.now(KST)
ISSUE=NOW.date()
PREV=ISSUE-dt.timedelta(days=1)
START=dt.datetime.combine(PREV,dt.time(18),KST)
END=dt.datetime.combine(ISSUE,dt.time(0),KST)
ROOT=Path(__file__).parent
OUT=ROOT/'docs'
OUT.mkdir(exist_ok=True)
SECTIONS=[('🏛 정치·외교','정치 외교 대한민국'),('📈 경제·금융','한국 경제 금융 환율 증시'),('🚨 사회','대한민국 사회 사건 교육'),('🎬 연예·스포츠','한국 연예 스포츠'),('🌏 국제·기타','국제 세계 주요 뉴스')]
AGENT='Mozilla/5.0 (compatible; MorningNewsMagazine/1.0)'

def get_feed(query):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query+' when:1d','hl':'ko','gl':'KR','ceid':'KR:ko'})
    req=urllib.request.Request(url,headers={'User-Agent':AGENT})
    with urllib.request.urlopen(req,timeout=22) as r:
        data=r.read(1_500_000)
    root=ET.fromstring(data)
    result=[]
    for item in root.findall('./channel/item'):
        title=(item.findtext('title') or '').strip()
        link=(item.findtext('link') or '').strip()
        published=item.findtext('pubDate') or ''
        source=item.find('source')
        publisher=(source.text or '').strip() if source is not None else 'Google 뉴스'
        try:
            timestamp=email.utils.parsedate_to_datetime(published).astimezone(KST)
        except Exception:
            continue
        if not (START<=timestamp<END) or not link.startswith('https://news.google.com/'):
            continue
        if title.endswith(' - '+publisher):
            title=title[:-(len(publisher)+3)].strip()
        if len(title)<12:continue
        result.append({'title':title,'url':link,'publisher':publisher,'time':timestamp.strftime('%H:%M')})
    return result

def esc(s):return html.escape(str(s),quote=True)

def article(x):
    return f'''<article class="story"><span class="tag">어젯밤 {esc(x['time'])} 보도</span><h3>{esc(x['title'])}</h3><p>📰 {esc(x['publisher'])}에서 전한 소식이에요. 제목을 확인하고 아래 기사에서 자세한 내용을 읽어보세요.</p><div class="source">출처 · {esc(x['publisher'])} · {esc(x['time'])} KST<br><a href="{esc(x['url'])}" target="_blank" rel="noopener noreferrer">Google 뉴스에서 해당 기사 보기 ↗</a></div></article>'''

def render():
    seen=set(); blocks=[]; count=0; errors=[]
    for heading,query in SECTIONS:
        try: candidates=get_feed(query)
        except Exception as e:
            errors.append(f'{heading}: {type(e).__name__}')
            candidates=[]
        chosen=[]
        for x in candidates:
            norm=re.sub(r'\W+','',x['title']).lower()
            if norm in seen:continue
            seen.add(norm);chosen.append(x)
            if len(chosen)==3:break
        if chosen:
            count+=len(chosen)
            blocks.append(f'<section class="section"><h2>{esc(heading)}</h2>'+''.join(map(article,chosen))+'</section>')
    if not count:
        blocks=['<section class="section"><h2>📰 오늘의 안내</h2><p>뉴스 원문을 수집하지 못했어요. 확인되지 않은 기사는 싣지 않았습니다. 잠시 후 다시 확인해 주세요.</p></section>']
    day=ISSUE.strftime('%Y.%m.%d')
    note='자동 수집된 기사 제목과 발행 시각만 사용했습니다. 기사 본문을 읽거나 AI로 검증한 요약이 아닙니다. 링크는 언론사 직접 주소가 아닌 Google 뉴스 경유 링크일 수 있습니다.'
    if errors:note+=' 일부 분야의 수집에 실패했습니다.'
    body=''.join(blocks)
    template=(ROOT/'template.html').read_text(encoding='utf-8')
    rendered=(template.replace('{{ISSUE}}',esc(day)).replace('{{WINDOW}}',esc(f'{PREV:%Y.%m.%d} 18:00~24:00 KST')).replace('{{COUNT}}',str(count)).replace('{{STORIES}}',body).replace('{{NOTE}}',esc(note)))
    (OUT/'index.html').write_text(rendered,encoding='utf-8')
    (OUT/'latest.json').write_text(json.dumps({'issue':day,'window_start':START.isoformat(),'window_end':END.isoformat(),'count':count,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote docs/index.html ({count} articles; {len(errors)} feed errors)')

if __name__=='__main__':render()
