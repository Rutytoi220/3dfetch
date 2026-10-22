# Getting started

A short, practical tour. Nothing here is required reading — skim it, grab
the install command for your system, and come back when you want to change
something.

## What it actually does

Your distro's logo gets turned into a cloud of points based on how heavy
each character looks, then spun around in 3D with the system info sitting
next to it. The info refreshes on its own, so you can leave it running and
watch your CPU do something interesting.

The labels (`OS`, `Host`, `Kernel`, ...) are painted in the same color the
logo is drawn in, so the whole thing looks like one piece.

## Install it

Pick whichever one suits you. They all give you the same program.

### Building it yourself

Needs a C compiler and `make`. Nothing else.

```bash
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch
make
sudo make install
```

If you'd rather not install it system-wide:

```bash
make
PREFIX=~/.local make install
```

### A prebuilt binary

Grab one from the [releases page](https://github.com/Rutytoi220/3dfetch/releases).
There are builds for x86_64 and aarch64.

```bash
tar xf 3dfetch-linux-x86_64.tar.gz
sudo install -m 755 3dfetch-linux-x86_64 /usr/local/bin/3dfetch
```

### Flatpak

It isn't on Flathub yet, so there's no install button to click. The
manifest is in the repo though, and a Flatpak is the least invasive way to
try it if you'd rather not touch your system at all.

First get the builder, if you don't have it:

```bash
flatpak install --user -y flathub org.flatpak.Builder
```

Then build and install the app from the repository:

```bash
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch
flatpak run --command=flathub-build org.flatpak.Builder --install flatpak/io.github.rutytoi220._3dfetch.yml
```

And run it:

```bash
flatpak run io.github.rutytoi220._3dfetch
```

The Flatpak bundles fastfetch so it has the logos to draw, and it reads
your host's `/etc/os-release` so it picks the right one for your machine
rather than the runtime's.

Once it lands on Flathub, this gets a lot shorter:

```bash
flatpak install flathub io.github.rutytoi220._3dfetch
```

#### The `3dfetch` command after a Flatpak install

This is the bit that trips people up. Flatpak exports the app's binary
under the app's ID rather than under the name you installed it with, so
afterwards you'll find:

```
~/.local/share/flatpak/exports/bin/io.github.rutytoi220._3dfetch
```

and `3dfetch` on its own will say *command not found*. Point a name at it
once and you're done:

```bash
mkdir -p ~/.local/bin
ln -sf ~/.local/share/flatpak/exports/bin/io.github.rutytoi220._3dfetch ~/.local/bin/3dfetch
```

If you installed it system-wide (the software centre usually does), the
export lives in `/var/lib/flatpak/exports/bin` instead:

```bash
sudo ln -sf /var/lib/flatpak/exports/bin/io.github.rutytoi220._3dfetch /usr/local/bin/3dfetch
```

The wrapper passes every argument through, so `3dfetch --logo ubuntu` and
friends work exactly like you'd expect.

Honestly though, if all you want is the command, the plain binary is the
easier way to run a terminal program. The Flatpak is there for people who
would rather not install anything on the host.

### Homebrew

```bash
brew trust Rutytoi220/tap
brew install Rutytoi220/tap/3dfetch
```

Homebrew formula names can't start with a digit, so the formula is called
`threefetch` and `3dfetch` is an alias for it. You still get the `3dfetch`
command. On older Homebrew the `brew trust` line just says the command
doesn't exist — skip it.

### Arch Linux

It isn't on the AUR yet, so `yay` won't find it. The PKGBUILD is in the
repo and works as-is:

```bash
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch/aur
makepkg -si
```

### Nix

```bash
nix run github:Rutytoi220/3dfetch
```

## Run it

```bash
3dfetch
```

It also installs as `fetch`, so if that name is free on your system, use
it instead. Same program, different name.

Press any key to quit. The keypress goes straight through to your shell
afterwards, so `3dfetch` and then `q` leaves you with a `q` in your
prompt — handy if you run it at login.

You can also grab the logo and spin it with the mouse. Click and drag to
turn it, let go and it keeps going.

## What you can change

Everything lives in `~/.config/fetch/`. Create the directory if it isn't
there:

```bash
mkdir -p ~/.config/fetch
```

### Picking the fields

The config file lists the fields you want, one per line, in the order you
want them:

```
os
host
kernel
uptime
cpu
gpu
memory
disk
```

**Watch out for this one:** the moment a config file exists, only the
fields listed in it show up. Delete the file and everything comes back.

### Your own logo

Drop your ASCII art in `~/.config/fetch/logo.txt`. The first line can name
a distro so the colors match:

```
# distro: bazzite
         -/oyddmdhs+:.
     -odNMMMMMMMMNNmhy+-`
   -yNMMMMMMMMMMMNNNmmdhy+-
```

Characters with more visual weight (`@`, `M`, `#`) come out taller in the
relief, and sparse ones (`.`, `-`, spaces) stay flat, so a bit of variety
makes for a much better shape. A logo that's all one character looks like
a pancake.

### Colors

Usually you don't need to touch this — the labels take the logo's color
and that's that. But if you want a specific color:

```
label_color=magenta
```

And if your terminal mangles 24-bit color:

```
truecolor=0
```

which drops everything to the nearest of the 16 basic colors.

## Handy flags

```
3dfetch --logo ubuntu      any logo fastfetch knows
3dfetch --frames 1         draw one frame and quit (good for screenshots)
3dfetch --speed 0.5        half speed
3dfetch --speed 10         ten times as fast
3dfetch --speed -3         spin it backwards
3dfetch --nggyu            a surprise
3dfetch --no-info          just the logo
3dfetch --box              draw a frame around the info
3dfetch --size 2           twice as big
3dfetch --height 20        shorter
3dfetch --help             everything else
```

There's no limit on `--speed`. `0` freezes it, `0.5` is half speed, `10`
is ten times as fast, and a negative number spins it backwards. The frame
rate goes up along with it, so a fast spin still looks smooth instead of
jumping about.

## A surprise

There's a flag in `--help` that reads like a dare. Take it:

```bash
3dfetch --nggyu
```

We won't say what it does. The system info stays put beside it, or drops
underneath on a narrow terminal, so you can still watch your machine while
whatever it is does its thing.

(The artwork is an ASCII portrait from
[johnsoupir/ASCII_Rickroll](https://github.com/johnsoupir/ASCII_Rickroll).)

## When something looks off

**`3dfetch: command not found` after a Flatpak install.** Flatpak exports
the binary under the app's ID, not the name you installed it with. See
[the note above](#the-3dfetch-command-after-a-flatpak-install) — it's a
one-line symlink.

**`flatpak run` says the app isn't installed.** You probably installed it
for your user only and left off `--user`:

```bash
flatpak run --user io.github.rutytoi220._3dfetch
```

**No logo, or the wrong one.** The logos come from fastfetch. If it isn't
installed, you get the built-in Gentoo logo instead:

```bash
sudo apt install fastfetch     # Debian/Ubuntu
sudo dnf install fastfetch     # Fedora
sudo pacman -S fastfetch       # Arch
```

**The labels are the wrong color.** Set `label_color=` in your config and
it stops mattering what the logo is doing.

**Everything is one flat color and you want the two-tone look.** Set
`logo_outer` and `logo_inner` in your config:

```
logo_outer=cyan
logo_inner=white
```

**It says it can't load a logo.** Same fastfetch problem as above.

**In a Flatpak the logo doesn't match your distro.** Older Flatpak
runtimes hide the host's `/etc/os-release`. The app reads
`/run/host/os-release` as well, so it should sort itself out — if it
doesn't, you're on an old runtime and it's worth reporting.

## Where things live

| What | Where |
|---|---|
| Config | `~/.config/fetch/config` |
| Custom logo | `~/.config/fetch/logo.txt` |
| The binary | `/usr/local/bin/3dfetch` (or wherever you put it) |
| Source | [github.com/Rutytoi220/3dfetch](https://github.com/Rutytoi220/3dfetch) |

## Where it came from

`3dfetch` is a fork of [fetch](https://github.com/areofyl/fetch) by
[@areofyl](https://github.com/areofyl), which is itself based on
[gentoo.c](https://github.com/areofyl/gentoo.c). Same ISC license, and
the original copyright is still intact.
