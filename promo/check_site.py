"""Check the live site works like a customer would use it. Exit code 1 if anything is broken.
Usage: python promo/check_site.py [url]"""
import json, sys
from playwright.sync_api import sync_playwright

URL = (sys.argv[1] if len(sys.argv) > 1 else 'https://gigtaxbuddy.github.io/').rstrip('/') + '/'
problems, notes = [], []

with sync_playwright() as p:
    b = p.chromium.launch()
    for name, view in [('phone', dict(viewport={'width': 390, 'height': 844}, is_mobile=True)), ('computer', dict(viewport={'width': 1366, 'height': 900}))]:
        page = b.new_context(**view).new_page(); errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            r = page.goto(URL + '?check=1', wait_until='load', timeout=60000)
            if not r or r.status != 200: problems.append(f'{name}: site returned {r and r.status}')
            page.wait_for_timeout(1500)
            if page.title() != 'Gig Tax Buddy': problems.append(f'{name}: wrong page title')
            week = page.text_content('#o_week') or ''
            if not week.startswith('$'): problems.append(f'{name}: calculator shows no number')
            page.evaluate("()=>{const e=document.getElementById('c_earn');e.value=900;e.dispatchEvent(new Event('input'))}")
            if page.text_content('#o_week') == week: problems.append(f'{name}: calculator does not react')
            broken = page.evaluate('()=>[...document.images].filter(i=>!i.naturalWidth).length')
            if broken: problems.append(f'{name}: {broken} image(s) not loading')
            page.evaluate('()=>openApp()'); page.wait_for_timeout(1500)
            app = page.frame_locator('#appframe')
            if 'Gig Tax Buddy' not in (app.locator('body').inner_text(timeout=10000)): problems.append(f'{name}: app does not open')
            for tab in ['history', 'tools', 'settings', 'home']:
                app.locator(f'.tabs button[data-v={tab}]').click()
                if len(app.locator('#main').inner_text()) < 20: problems.append(f'{name}: app tab {tab} is empty')
            if errors: problems.append(f'{name}: script errors: ' + '; '.join(errors)[:300])
        except Exception as e:
            problems.append(f'{name}: {str(e)[:300]}')
    page = b.new_page()
    for g in ['guides/doordash-taxes-2026.html', 'guides/uber-1099-k-explained.html', 'guides/no-tax-on-tips-drivers.html']:
        try:
            r = page.goto(URL + g, timeout=30000)
            if not r or r.status != 200: problems.append(f'guide {g} returned {r and r.status}')
        except Exception as e:
            problems.append(f'guide {g}: {str(e)[:200]}')
    b.close()

print(json.dumps(dict(url=URL, ok=not problems, problems=problems), indent=1))
sys.exit(1 if problems else 0)
