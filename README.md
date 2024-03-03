sync flomo cards to local folder.

directory tree: 
```bash
flomo
├─ 2024
│    ├─ 01
│    │    ├─ 2024-01-15.md
│    ├─ 02
│    └─ 03
├─ flomo.md
└─ tags
       ├─ 项目.md
       └─ 领域.md
```

usage:
```bash
usage: main.py [-h] dir_path auth

Sync flomo to markdown

positional arguments:
  dir_path    The markdown directory path
  auth        The Flomo authorization

options:
  -h, --help  show this help message and exit
```

more links:
- alfred workflow: [Workflows](https://github.com/linq/my-workflows/blob/main/Flomo.alfredworkflow)
- refer: [flomo-sync](https://fancylinq.netlify.app/posts/flomo-sync/)
