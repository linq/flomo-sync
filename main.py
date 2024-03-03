import argparse

from day_note import DayNote
from flomo_api import FlomoAPI
from flomo_note import FlomoNote
from tag_note import TagNode

# The code below is for running the script and generating markdown files.
# It can be placed in a main function or a separate script.

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync flomo to markdown')
    parser.add_argument('dir_path', help='The markdown directory path')
    parser.add_argument('auth', help='The Flomo authorization')
    args = parser.parse_args()

    base_dir = args.dir_path
    flomo = FlomoAPI(f"Bearer {args.auth}")
    day_note = DayNote(base_dir)
    tag_note = TagNode(base_dir)
    flomo_note = FlomoNote(base_dir)

    try:
        memos = flomo.get_all_memos(flomo_note.load_latest_info())

        if len(memos) == 0:
            exit(0)

        day_note.update(memos)
        tag_note.update(memos)
        flomo_note.update(memos)

        print(f'sync {len(memos)} memos')

    except Exception as e:
        print(f"An error occurred: {e}")
