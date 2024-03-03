import os
import re
from datetime import datetime
from typing import List, Optional, Dict, Any

import html2text

from util import delete


class DayNote:
    DAY_NOTE_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2}).md')
    STATE_NONE = None
    STATE_NEW = 'new'
    STATE_UPDATE = 'update'
    STATE_DELETE = "delete"

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = True
        self.converter.ignore_images = True
        self.day_notes = {}

    def classify_memos(self, memos):
        slug_dict = self.load_slugs()
        for memo in memos:
            slug = memo['slug']
            memo['state'] = DayNote.STATE_NEW

            if memo['deleted_at']:
                memo['state'] = DayNote.STATE_DELETE
                continue

            if slug in slug_dict:
                memo['state'] = DayNote.STATE_NONE
                updated_at = slug_dict[slug]
                if updated_at != memo['updated_at']:
                    memo['state'] = DayNote.STATE_UPDATE

    @staticmethod
    def extract_memo_meta(content):
        match = re.search(r'<!-- (\w+):([\d\- :]+) -->', content)
        if match:
            return {'slug': match.group(1), 'updated_at': match.group(2)}
        return {}

    def load_slugs(self):
        result = {}
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                match = re.search(DayNote.DAY_NOTE_PATTERN, file)
                if not match:
                    continue
                note_path = os.path.join(root, file)
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(r'<!-- (\w+):([\d\- :]+) -->', content)
                    result.update({key: value for key, value in matches})
        return result

    def update(self, memos):
        self.classify_memos(memos)
        grouped_data = {}
        for memo in memos:
            key = memo['created_at'].split(' ')[0]
            grouped_data[key] = grouped_data.get(key, []) + [memo]
        for date, items in grouped_data.items():
            self.update_note(date, items)

    def _2markdown(self, memo: Dict[str, Any]) -> str:
        html = memo['content']
        markdown_content = self.converter.handle(html)
        comment = f"<!-- {memo['slug']}:{memo['updated_at']} -->\n"
        full_markdown = f"### {memo['created_at']}\n{markdown_content}{comment}\n---\n"
        return full_markdown

    def update_note(self, date: str, memos: List[Dict[str, Any]]):
        memos.sort(key=lambda x: datetime.strptime(x['updated_at'], '%Y-%m-%d %H:%M:%S'))
        filename, content = self.note_file(date)
        should_write = False
        for memo in sorted(memos, key=lambda x: datetime.strptime(x['updated_at'], '%Y-%m-%d %H:%M:%S')):
            if memo['state'] in (DayNote.STATE_NEW, DayNote.STATE_UPDATE):
                content = self._remove_memo_content(content, memo)
                content = self._2markdown(memo) + content
                should_write = True
            elif memo['state'] == DayNote.STATE_DELETE:
                content = self._remove_memo_content(content, memo)
                should_write = True

        if should_write and content.strip():
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
        elif not content.strip():
            delete(filename)

    def note_file(self, date):
        path = datetime.strptime(date, '%Y-%m-%d').strftime('%Y/%m')
        if self.base_dir:
            path = os.path.join(self.base_dir, path)
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, f'{date}.md')
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return filename, file.read()
        else:
            return filename, ''

    @staticmethod
    def _remove_memo_content(content: str, memo: Dict[str, Any]) -> str:
        pattern = r'### .*?<!-- ' + re.escape(memo['slug']) + r'.*?-->\n\n---'
        return re.sub(pattern, '', content, flags=re.DOTALL)
