# installation

- you need ircrobots, do `pip3 install ircrobots`
- copy `config.py.example` to `config.py` and edit it

## systemd user unit
this is optional but if you want it to autostart
on boot and stuff, do this.

 edit `relay.service` with the correct path and stuff

`mkdir -p ~/.config/systemd/user` and copy relay.service
to `~/.config/systemd/user`.

- to linger: `loginctl enable-linger`
- to start on boot: `systemctl --user enable relay`
- to run it: `systemctl --user start relay`

# run it
if you dont want systemd stuff you can just
`python3 bot.py` or `./bot.py`

