"""Post one video to every platform that has credentials set. Skips the rest.
Usage: python promo/post.py media/<id>.mp4   (DRY_RUN=1 to only print what would happen)
Writes a JSON list of results to stdout (and to promo_results.json)."""
import json, os, sys, time
import requests

SITE = os.environ.get('SITE_URL', 'https://gigtaxbuddy.github.io/')
GRAPH = 'https://graph.facebook.com/' + os.environ.get('GRAPH_VERSION', 'v22.0')
DRY = os.environ.get('DRY_RUN') == '1'
env = lambda *k: all(os.environ.get(x) for x in k)


def caption(meta, src):
    return meta['caption'] + ('' if src in ('instagram', 'tiktok', 'youtube') else f"\n\nTry it free: {SITE}?from={src}")


def instagram(path, meta, url):
    if not env('IG_USER_ID', 'META_TOKEN'): return 'skipped: not connected'
    if DRY: return 'dry run'
    tok, uid = os.environ['META_TOKEN'], os.environ['IG_USER_ID']
    r = requests.post(f'{GRAPH}/{uid}/media', data=dict(media_type='REELS', video_url=url, caption=caption(meta, 'instagram'), share_to_feed='true', access_token=tok), timeout=60).json()
    if 'id' not in r: raise RuntimeError(r)
    cid = r['id']
    for _ in range(40):
        st = requests.get(f'{GRAPH}/{cid}', params=dict(fields='status_code', access_token=tok), timeout=30).json().get('status_code')
        if st == 'FINISHED': break
        if st == 'ERROR': raise RuntimeError('Instagram could not process the video')
        time.sleep(15)
    r = requests.post(f'{GRAPH}/{uid}/media_publish', data=dict(creation_id=cid, access_token=tok), timeout=60).json()
    if 'id' not in r: raise RuntimeError(r)
    return 'posted ' + r['id']


def facebook(path, meta, url):
    if not env('FB_PAGE_ID', 'META_TOKEN'): return 'skipped: not connected'
    if DRY: return 'dry run'
    r = requests.post(GRAPH.replace('graph.', 'graph-video.') + f"/{os.environ['FB_PAGE_ID']}/videos",
                      data=dict(file_url=url, description=caption(meta, 'facebook'), access_token=os.environ['META_TOKEN']), timeout=120).json()
    if 'id' not in r: raise RuntimeError(r)
    return 'posted ' + r['id']


def youtube(path, meta, url):
    if not env('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'): return 'skipped: not connected'
    if DRY: return 'dry run'
    tok = requests.post('https://oauth2.googleapis.com/token', data=dict(client_id=os.environ['YT_CLIENT_ID'], client_secret=os.environ['YT_CLIENT_SECRET'],
                        refresh_token=os.environ['YT_REFRESH_TOKEN'], grant_type='refresh_token'), timeout=30).json()['access_token']
    size = os.path.getsize(path)
    body = dict(snippet=dict(title=(meta['title'][:90] + ' #Shorts'), description=caption(meta, 'youtube') + f"\n\n{SITE}?from=youtube", categoryId='27'),
                status=dict(privacyStatus='public', selfDeclaredMadeForKids=False, containsSyntheticMedia=True))
    r = requests.post('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', json=body, timeout=30,
                      headers={'Authorization': f'Bearer {tok}', 'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(size)})
    r.raise_for_status()
    with open(path, 'rb') as f:
        v = requests.put(r.headers['Location'], data=f, timeout=600, headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'video/mp4'}).json()
    if 'id' not in v: raise RuntimeError(v)
    return f"posted https://youtube.com/shorts/{v['id']} ({v.get('status', {}).get('privacyStatus', '?')})"


def tiktok(path, meta, url):
    if not env('TT_CLIENT_KEY', 'TT_CLIENT_SECRET', 'TT_REFRESH_TOKEN'): return 'skipped: not connected'
    if DRY: return 'dry run'
    t = requests.post('https://open.tiktokapis.com/v2/oauth/token/', data=dict(client_key=os.environ['TT_CLIENT_KEY'], client_secret=os.environ['TT_CLIENT_SECRET'],
                      grant_type='refresh_token', refresh_token=os.environ['TT_REFRESH_TOKEN']), timeout=30).json()
    h = {'Authorization': f"Bearer {t['access_token']}", 'Content-Type': 'application/json; charset=UTF-8'}
    info = requests.post('https://open.tiktokapis.com/v2/post/publish/creator_info/query/', headers=h, timeout=30).json()['data']
    opts = info.get('privacy_level_options', [])
    privacy = 'PUBLIC_TO_EVERYONE' if 'PUBLIC_TO_EVERYONE' in opts else 'SELF_ONLY'  # unaudited apps can only post privately
    size = os.path.getsize(path)
    r = requests.post('https://open.tiktokapis.com/v2/post/publish/video/init/', headers=h, timeout=30, json=dict(
        post_info=dict(title=caption(meta, 'tiktok')[:2200], privacy_level=privacy, disable_comment=False, is_aigc=True),
        source_info=dict(source='FILE_UPLOAD', video_size=size, chunk_size=size, total_chunk_count=1))).json()
    d = r.get('data') or {}
    if 'upload_url' not in d: raise RuntimeError(r)
    with open(path, 'rb') as f:
        requests.put(d['upload_url'], data=f, timeout=600, headers={'Content-Type': 'video/mp4', 'Content-Range': f'bytes 0-{size - 1}/{size}'}).raise_for_status()
    return f"posted ({'public' if privacy == 'PUBLIC_TO_EVERYONE' else 'private until TikTok approves the app'})"


def main(path):
    meta = json.load(open(path[:-4] + '.json'))
    url = SITE.rstrip('/') + '/media/' + os.path.basename(path)
    out = []
    for name, fn in [('Instagram', instagram), ('Facebook', facebook), ('YouTube', youtube), ('TikTok', tiktok)]:
        try: res = fn(path, meta, url); ok = not str(res).startswith(('skipped', 'dry'))
        except Exception as e: res, ok = f'failed: {str(e)[:300]}', False
        out.append(dict(platform=name, result=str(res), ok=ok))
    json.dump(dict(video=meta['id'], title=meta['title'], url=url, posts=out), open('promo_results.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
