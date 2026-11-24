import datetime as dt, pathlib, re, json, html
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from email.utils import parsedate_to_datetime
import requests, feedparser
from jinja2 import Environment, FileSystemLoader, select_autoescape
root=pathlib.Path(__file__).parent; out=root/'docs'; out.mkdir(exist_ok=True)
now=dt.datetime.now(ZoneInfo('Asia/Seoul')); end=now.replace(hour=8,minute=0,second=0,microsecond=0); start=end-dt.timedelta(days=1)
queries={'경제·금융':'경제 금리 증시 물가','정치·외교':'정치 외교 정부 국회','사회·생활':'사회 생활 사건 정책','국제':'국제 세계 외교','연예·스포츠':'연예 문화 스포츠','패션·유통':'나이키 OR 아디다스 OR 무신사 OR 슈마커 OR 폴더','MZ 트렌드':'SNS OR 밈 OR 캐릭터 OR 숏폼 트렌드'}
terms={'기준금리':'한국은행이 정하는 정책금리로 대출과 예금 금리에 영향을 줍니다.','환율':'외국 돈을 우리 돈으로 바꿀 때 적용되는 가격입니다.','개각':'정부의 장관 등 주요 책임자를 교체하는 인사입니다.','자사주':'기업이 발행한 자기 회사의 주식입니다.','영업이익':'매출에서 본업에 들어간 비용을 뺀 이익입니다.','팝업':'일정 기간만 운영하는 임시 매장입니다.','협업':'두 브랜드 등이 함께 상품이나 콘텐츠를 만드는 것입니다.','숏폼':'짧은 길이의 영상 콘텐츠입니다.'}
def get(url,**kw):
 r=requests.get(url,timeout=20,headers={'User-Agent':'Mozilla/5.0'},**kw);r.raise_for_status();return r

def news(q,seen):
 url='https://news.google.com/rss/search?'+urlencode({'q':q+' when:2d','hl':'ko','gl':'KR','ceid':'KR:ko'})
 rows=[]
 for e in feedparser.parse(get(url).content).entries:
  try:t=parsedate_to_datetime(e.published).astimezone(end.tzinfo)
  except Exception:continue
  if not start<=t<end or e.link in seen:continue
  source=e.get('source',{}).get('title','Google 뉴스'); title=e.title.removesuffix(' - '+source)
  if title in seen:continue
  easy=' '.join(v for k,v in terms.items() if k in title) or '기사 전문을 확인해야 정확한 설명이 가능합니다.'
  rows.append(dict(title=title,summary='기사 제목 기준으로 수집했습니다. 세부 내용은 원문에서 확인해 주세요.',easy=easy,why='기사 전문 미확인 · 영향 분석 보류',source=source,published=t.strftime('%m/%d %H:%M'),url=e.link));seen.update([title,e.link])
  if len(rows)==5:break
 return rows

def market():
 import yfinance as yf
 rows=[]
 for name,ticker,mult in [('코스피','^KS11',1),('달러','KRW=X',1),('엔화','JPYKRW=X',100)]:
  try:
   h=yf.Ticker(ticker).history(period='15d',interval='1d',auto_adjust=False); h=h[h.index.date<end.date()]['Close'].dropna(); a,b=map(float,h.iloc[-2:]);rows.append(dict(name=name,value=f'{b*mult:,.2f}',change=(b-a)*mult,percent=(b/a-1)*100,date=str(h.index[-1].date()),source='Yahoo Finance · 일봉 종가',url='https://finance.yahoo.com/quote/'+ticker+'/'))
  except Exception as e:print(name,e)
 return rows

def fans():
 cfg=json.loads((root/'fans.json').read_text()); result=[]
 for f in cfg:
  videos=[]; cid=f.get('channel_id','')
  if cid:
   try:
    e=feedparser.parse(get('https://www.youtube.com/feeds/videos.xml',params={'channel_id':cid}).content).entries[0]; vid=e.yt_videoid;videos=[dict(title=e.title,date=e.published[:10],url=e.link,thumb=f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg')]
   except Exception as e:print(e)
  result.append(dict(name=f['name'],schedule=[s for s in f.get('schedule',[]) if s.get('date','')[:10]>=str(end.date()) and s.get('url','').startswith('https://')],videos=videos))
 return result

def main():
 seen=set();sections=[]
 for name,q in queries.items():
  try:items=news(q,seen)
  except Exception as e:print(name,e);items=[]
  sections.append(dict(name=name,items=items))
 if not any(s['items'] for s in sections):raise SystemExit('뉴스 수집 실패: 기존 발행본 유지')
 issue=str(end.date()); archive=sorted(set([p.stem for p in out.glob('????-??-??.html')]+[issue]),reverse=True)
 env=Environment(loader=FileSystemLoader(root),autoescape=select_autoescape(['html']));page=env.get_template('template.html').render(issue=issue,start=start.strftime('%m/%d %H:%M'),end=end.strftime('%m/%d %H:%M'),sections=sections,metrics=market(),fans=fans(),archive=archive)
 for name in [issue,'index']:(out/f'{name}.html').write_text(page,encoding='utf-8')
if __name__=='__main__':main()
