"""Download public source snapshots for the development cases."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import datetime
import hashlib
import json
import requests

ROOT = Path(__file__).resolve().parent
URLS = {
    'NIST-pri55.html': 'https://www.itl.nist.gov/div898/handbook/pri/section5/pri55.htm',
    'NIST-foldover.html': 'https://www.itl.nist.gov/div898/handbook/pri/section3/pri3381.htm',
    'wind.html': 'https://wes.copernicus.org/articles/6/1427/2021/',
    'wind.pdf': 'https://wes.copernicus.org/articles/6/1427/2021/wes-6-1427-2021.pdf',
    'lens2.html': 'https://www.cesm.ucar.edu/community-projects/lens2',
    'catalyst.html': 'https://www.nature.com/articles/s41598-020-77629-3',
    'catalyst.pdf': 'https://www.nature.com/articles/s41598-020-77629-3.pdf',
    'powder.html': 'https://www.mdpi.com/2071-1050/15/21/15582',
    'powder-repository.html': 'https://researchonline.jcu.edu.au/86205/',
    'paired-fixed-1806.01871v1.pdf': 'https://arxiv.org/pdf/1806.01871v1',
    'fatigue-2107.02685v3.pdf': 'https://arxiv.org/pdf/2107.02685v3',
    'metrology.pdf': 'https://www.metrology.pg.gda.pl/full/2009/M%26MS_2009_377.pdf',
    'cloud-seeding.html': 'https://journals.ametsoc.org/view/journals/apme/57/11/jamc-d-17-0335.1.xml',
    'foldover-2507.14648.pdf': 'https://arxiv.org/pdf/2507.14648',
}

def fetch(item):
    name, url = item
    record = {'file': 'evidence/' + name, 'requested_url': url,
              'accessed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        response = requests.get(url, timeout=40)
        record.update(status_code=response.status_code, final_url=response.url,
                      content_type=response.headers.get('Content-Type'))
        response.raise_for_status()
        (ROOT / record['file']).write_bytes(response.content)
        record['sha256'] = hashlib.sha256(response.content).hexdigest()
        record['bytes'] = len(response.content)
    except requests.RequestException as exc:
        record['error'] = str(exc)
    return record

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(fetch, URLS.items()))
    (ROOT / 'download_log.json').write_text(json.dumps(records, indent=2) + '\n')
    for record in records:
        print(record['file'], record.get('status_code'), record.get('bytes'), record.get('error', ''))
