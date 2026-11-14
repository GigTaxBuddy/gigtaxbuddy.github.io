"""Daily report: sales from Gumroad, today's posts, site health. Opens a GitHub issue (GitHub emails it to the owner).
Usage: python promo/report.py   (reads promo_results.json and site_check.json if present)
Env: GUMROAD_TOKEN (optional), GH_TOKEN + GITHUB_REPOSITORY (set automatically in GitHub Actions), DRY_RUN=1 to only print."""
import datetime as dt, json, os, subprocess
import requests

today = dt.date.today(); yday = today - dt.timedelta(days=1)


def gumroad():
    tok = os.environ.get('GUMROAD_TOKEN')
    if not tok: return None
    sales, url, params = [], 'https://api.gumroad.com/v2/sales', dict(access_token=tok, after='2026-11-01')
    while url:
        r = requests.get(url, params=params, timeout=30).json()
        if not r.get('success'): return dict(error=str(r)[:200])
        sales += r.get('sales', [])
        url = r.get('next_page_url') and 'https://api.gumroad.com' + r['next_page_url']; params = dict(access_token=tok) if url else None
    def day(s): return s.get('created_at', '')[:10]
    money = lambda L: sum(int(s.get('price', 0)) for s in L if not s.get('refunded')) / 100
    yl = [s for s in sales if day(s) == yday.isoformat()]
    refunds = [s for s in sales if s.get('refunded') and day(s) >= (today - dt.timedelta(days=7)).isoformat()]
    src = {}
    for s in sales: src[s.get('referrer') or 'direct'] = src.get(s.get('referrer') or 'direct', 0) + 1
    return dict(yesterday=len(yl), yesterday_money=money(yl), total=len(sales), total_money=money(sales), refunds_7d=len(refunds), sources=src)


def load(f):
    try: return json.load(open(f))
    except Exception: return None


g, posts, site = gumroad(), load('promo_results.json'), load('site_check.json')
L = [f'## Gig Tax Buddy daily report, {today:%b %d, %Y}', '']
L += ['### Sales (gross, before Gumroad fees)']
if g is None: L.append('Gumroad not connected yet.')
elif 'error' in g: L.append(f"Could not read Gumroad: {g['error']}")
else:
    L += [f"- Yesterday: **{g['yesterday']}** sale(s), ${g['yesterday_money']:,.2f}", f"- Since launch: **{g['total']}** sale(s), ${g['total_money']:,.2f}",
          f"- Refunds in the last 7 days: {g['refunds_7d']}", '- Where buyers came from: ' + (', '.join(f'{k} {v}' for k, v in g['sources'].items()) or 'none yet')]
L += ['', "### Today's video"]
if posts:
    L.append(f"**{posts['title']}** ([watch]({posts['url']}))")
    L += [f"- {p['platform']}: {p['result']}" for p in posts['posts']]
else: L.append('No video made today (check the workflow run).')
L += ['', '### Website']
L.append('Working on phone and computer.' if site and site.get('ok') else 'Problem found: ' + '; '.join((site or {}).get('problems', ['no check result'])))
L += ['', 'Customer emails and refund requests go to gigtaxbuddy@gmail.com.']
body = '\n'.join(L); print(body)

if os.environ.get('DRY_RUN') != '1' and os.environ.get('GITHUB_REPOSITORY'):
    subprocess.run(['gh', 'label', 'create', 'daily-report', '--color', 'F5B700', '--force'], check=False)
    subprocess.run(['gh', 'issue', 'create', '--title', f'Daily report {today:%b %d}', '--label', 'daily-report', '--body', body], check=True)
    # keep the list tidy: close reports older than 7 days
    old = subprocess.run(['gh', 'issue', 'list', '--label', 'daily-report', '--state', 'open', '--json', 'number,createdAt'], capture_output=True, text=True).stdout
    for i in json.loads(old or '[]'):
        if i['createdAt'][:10] < (today - dt.timedelta(days=7)).isoformat(): subprocess.run(['gh', 'issue', 'close', str(i['number'])], check=False)
