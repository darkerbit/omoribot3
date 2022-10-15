# Omoribot 3

A discord bot for creating OMORI-styled text boxes.

### How do run?

1. Place bot token into `token` next to `main.py` (Message content intent required)
2. Place dialogue portraits into `portraits/` and fonts into `fonts/`
3. `pip3 install pipenv` (or `sudo dnf install pipenv` on Fedora)
4. `pipenv run python3 omoribot`

### How do use?

TODO

### Why is it #3?

omoribot 1 is the original version of omoribot,
written with very shoddy platform-specific Python code.

omoribot 2 was a failed attempt to rewrite omoribot with C#, abandoned
after discovering the lack of functioning cross-platform drawing libraries
for C#.

omoribot 3 is also written in Python, though I plan on putting a little more care into the design.
