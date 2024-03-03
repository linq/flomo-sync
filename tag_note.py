import os
from collections import defaultdict
from datetime import datetime

from day_note import DayNote
from util import delete


class TagNode:
    def __init__(self, base_dir):
        self.base_dir = base_dir + "/tags"
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir, exist_ok=True)

    @staticmethod
    def memo_link(memo):
        date = memo['created_at']
        name = date.split()[0]
        date = date.replace(':', " ")
        return f'![[{name}#{date}]]'

    def write_links(self, tag, links):
        file_path = os.path.join(self.base_dir, f'{tag}.md')
        if len(links) == 0:
            delete(file_path)
            return

        markdown = '\n'.join(links)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown)

    def load_links(self, tag):
        file_path = os.path.join(self.base_dir, tag + ".md")
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content.split('\n')

    def write_note(self, tag, memos):
        memos.sort(key=lambda x: datetime.strptime(x['updated_at'], '%Y-%m-%d %H:%M:%S'), reverse=True)
        to_delete = {self.memo_link(memo) for memo in memos if memo['state'] == DayNote.STATE_DELETE}
        links = [self.memo_link(memo) for memo in memos]
        existing_links = self.load_links(tag)
        combined_links = [link for link in dict.fromkeys(links + existing_links) if link not in to_delete]
        self.write_links(tag, combined_links)

    def update(self, memos):
        tag_memos = TagNode.group_tag(memos)
        for tag, memos in tag_memos.items():
            self.write_note(tag, memos)

    @staticmethod
    def group_tag(data):
        grouped_data = defaultdict(list)
        for item in data:
            for tag in item['tags']:
                main_tag = tag.split('/')[0]
                grouped_data[main_tag].append(item)
        return dict(grouped_data)
