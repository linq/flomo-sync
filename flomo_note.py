import os
import re
from datetime import datetime
from pathlib import Path


class FlomoNote:
    def __init__(self, base_dir):
        self.filepath = os.path.join(base_dir, 'flomo.md')
        self.tags_folder = os.path.join(base_dir, 'tags')

    def update(self, memos):
        tags = self.build_tags()
        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write(self.markdown(tags, self.latest_memo(memos)))

    def load_latest_info(self):
        if not os.path.exists(self.filepath):
            return {}
        with open(self.filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        match = re.search(r'latest_updated_at:\s(.*)\nlatest_slug:\s(.*)\n', content)
        if match:
            update_at = match.group(1)
            latest_updated_at = int(datetime.fromisoformat(update_at).timestamp())
            return {'latest_slug': match.group(2), 'latest_updated_at': latest_updated_at}
        return {}

    def build_tags(self):
        md_files = [file.name.split('.')[0] for file in Path(self.tags_folder).glob('*.md')]
        return md_files

    @staticmethod
    def latest_memo(memos):
        memos.sort(key=lambda x: datetime.strptime(x['updated_at'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        return memos[0]

    @staticmethod
    def markdown(tags, latest_memo):
        flomo_markdown = f"""---
latest_updated_at: {latest_memo['updated_at']}
latest_slug: {latest_memo['slug']}
---

"""
        for tag in tags:
            flomo_markdown += f"[[{tag}|#{tag}]]\n"
        return flomo_markdown
