"""Make today's promo video.
Usage: python promo/make_video.py [YYYY-MM-DD] [--out media]
Needs: pillow, qrcode, kokoro-onnx, soundfile, ffmpeg; Kokoro files in promo/tts/ (kokoro.onnx, voices.bin).
Writes media/<id>.mp4 and media/<id>.json (title, caption)."""
import json, os, sys, subprocess, tempfile, datetime as dt
from PIL import Image, ImageDraw, ImageFont
import qrcode, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.environ.get('SITE_URL', 'https://gigtaxbuddy.github.io/')
W, H = 1080, 1920
ASPHALT, LANE, WHITE, MUTED = '#0e1a2b', '#f5b700', '#ffffff', '#c9d2e0'
F = lambda size, w='Bold': ImageFont.truetype(os.path.join(HERE, 'fonts', f'Inter-{w}.otf'), size)


def wrap(d, text, font, width):
    lines, cur = [], ''
    for word in text.split():
        t = (cur + ' ' + word).strip()
        if d.textlength(t, font=font) <= width: cur = t
        else: lines.append(cur); cur = word
    return lines + [cur] if cur else lines


def base():
    im = Image.new('RGB', (W, H), ASPHALT); d = ImageDraw.Draw(im)
    for x in range(0, W, 110): d.rectangle([x, 1840, x + 64, 1852], fill=LANE)
    icon = Image.open(os.path.join(HERE, 'assets', 'icon.png')).convert('RGB').resize((84, 84))
    im.paste(icon, (60, 70)); d.text((164, 92), 'Gig Tax Buddy', font=F(40), fill=WHITE)
    return im, d


def text_block(d, y, text, font, fill, width=940, gap=12):
    for line in wrap(d, text, font, width):
        d.text(((W - d.textlength(line, font=font)) / 2, y), line, font=font, fill=fill); y += font.size + gap
    return y


def title_card(s):
    im, d = base()
    big = F(104, 'ExtraBold'); lines = wrap(d, s['text'], big, 940)
    sub = F(52, 'Regular'); sl = wrap(d, s['sub'], sub, 900) if s['sub'] else []
    total = len(lines) * 120 + (30 + len(sl) * 66 if sl else 0); y = (H - total) // 2
    y = text_block(d, y, s['text'], big, WHITE, gap=16)
    if sl: text_block(d, y + 30, s['sub'], sub, LANE, 900, 14)
    return im


def screen_card(s):
    im, d = base()
    y = text_block(d, 200, s['text'], F(70, 'ExtraBold'), WHITE, gap=10)
    if s['sub']: y = text_block(d, y + 6, s['sub'], F(44, 'Regular'), LANE, gap=8)
    shot = Image.open(os.path.join(HERE, 'assets', s['img'] + '.png')).convert('RGB')
    top = max(y + 40, 470); ph = 1800 - top; pw = int(ph * shot.width / shot.height)
    if pw > 760: pw = 760; ph = int(pw * shot.height / shot.width)
    x = (W - pw) // 2
    d.rounded_rectangle([x - 18, top - 18, x + pw + 18, top + ph + 18], radius=56, fill='#05080e', outline='#2c3a52', width=3)
    mask = Image.new('L', (pw, ph), 0); ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw, ph], radius=42, fill=255)
    im.paste(shot.resize((pw, ph)), (x, top), mask)
    return im


def end_card(src):
    im, d = base()
    y = text_block(d, 330, 'Know what to set aside for taxes.', F(76, 'ExtraBold'), WHITE, gap=12)
    text_block(d, y + 6, 'Free. No account.', F(76, 'ExtraBold'), LANE)
    q = qrcode.QRCode(border=2, box_size=12); q.add_data(f'{SITE}?from={src}'); q.make()
    qr = q.make_image(fill_color=ASPHALT, back_color='white').convert('RGB').resize((540, 540)); im.paste(qr, ((W - 540) // 2, 720))
    text_block(d, 1320, 'Scan, or tap the link in our profile', F(44, 'Regular'), MUTED)
    text_block(d, 1420, SITE.replace('https://', '').rstrip('/'), F(54), LANE)
    return im


_k = None
def say(text, path):
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        t = os.path.join(HERE, 'tts'); _k = Kokoro(os.path.join(t, 'kokoro.onnx'), os.path.join(t, 'voices.bin'))
    a, sr = _k.create(text, voice=os.environ.get('VOICE', 'af_heart'), speed=1.0, lang='en-us')
    sf.write(path, a, sr); return len(a) / sr


def make(item, outdir, src='video'):
    os.makedirs(outdir, exist_ok=True); tmp = tempfile.mkdtemp()
    scenes = item['scenes'] + [dict(type='end', vo='Try it free today. Tap the link in our profile.')]
    parts = []
    for i, s in enumerate(scenes):
        img = {'title': title_card, 'screen': screen_card}.get(s['type'], lambda _: end_card(src))(s)
        png = os.path.join(tmp, f'{i}.png'); img.save(png)
        wav = os.path.join(tmp, f'{i}.wav'); dur = say(s['vo'], wav) + (0.6 if s['type'] != 'end' else 1.6)
        seg = os.path.join(tmp, f'{i}.mp4')
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '30', '-i', png, '-i', wav,
                        '-vf', f'format=yuv420p,loop=-1:1,trim=duration={dur:.3f}', '-af', f'adelay=150|150,apad,atrim=0:{dur:.3f}',
                        '-c:v', 'libx264', '-crf', '22', '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '1',
                        '-t', f'{dur:.3f}', seg], check=True)
        parts.append(seg)
    lst = os.path.join(tmp, 'l.txt'); open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    out = os.path.join(outdir, item['id'] + '.mp4'); part = out + '.part.mp4'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'copy', '-af', 'loudnorm=I=-16:TP=-1.5', '-c:a', 'aac', '-b:a', '128k', '-ar', '48000', '-movflags', '+faststart', part], check=True)
    os.replace(part, out)
    json.dump(dict(id=item['id'], title=item['title'], caption=item['caption']), open(out[:-4] + '.json', 'w'), indent=1)
    return out


def pick(day):
    items = json.load(open(os.path.join(HERE, 'scripts.json')))
    for it in items:
        if it['date'] == day: return it
    return items[(dt.date.fromisoformat(day) - dt.date.fromisoformat(items[0]['date'])).days % len(items)]


if __name__ == '__main__':
    day = next((a for a in sys.argv[1:] if a[:2] == '20'), dt.date.today().isoformat())
    outdir = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(HERE, '..', 'media')
    print(make(pick(day), outdir))
