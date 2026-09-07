"""Download the recorded study inputs without overwriting local data."""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import time
from urllib.request import urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(item, root):
    target = root / item['path']
    if target.exists():
        if digest(target) != item['sha256']:
            raise ValueError(f'Existing file differs; preserved: {target}')
        print(f'Checked {item["path"]}', flush=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as out:
                temporary = Path(out.name)
                with urlopen(item['url'], timeout=120) as response:
                    while chunk := response.read(1024 * 1024):
                        out.write(chunk)
            if digest(temporary) != item['sha256']:
                raise ValueError(f'Source snapshot changed: {item["url"]}')
            temporary.replace(target)
            print(f'Downloaded {item["path"]}', flush=True)
            return
        except ValueError:
            raise
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['01', '02', 'all'], default='all')
    parser.add_argument('--root', type=Path, default=ROOT,
                        help='Destination root; useful for a clean download check')
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name('sources.json').read_text())
    for item in manifest['files']:
        if args.stage in ('all', item['stage']):
            download(item, args.root)
    if args.stage in ('02', 'all'):
        folder = args.root / 'data/statcan'
        with zipfile.ZipFile(folder / '14100444-eng.zip') as archive:
            for name in ['14100444.csv', '14100444_MetaData.csv']:
                payload = archive.read(name)
                target = folder / name
                if target.exists():
                    if digest(target) != hashlib.sha256(payload).hexdigest():
                        raise ValueError(f'Existing extracted file differs: {target}')
                else:
                    with tempfile.NamedTemporaryFile(dir=folder, delete=False) as f:
                        f.write(payload)
                        temporary = Path(f.name)
                    temporary.replace(target)
        print('Statistics Canada extraction checked.')


if __name__ == '__main__':
    main()
