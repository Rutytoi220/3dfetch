# 3dfetch

A donut.c-inspired fetch tool that spins your distro logo in 3D with live-updating system info.

![demo](demo.gif)

Takes any ASCII/Unicode distro logo, turns each character into a point cloud
based on its visual density, and renders it as a rotating 3D relief with
Blinn-Phong shading. System info is gathered natively with no external
dependencies. Works on Linux and macOS.

`3dfetch` is a standalone project built on
[fetch](https://github.com/areofyl/fetch) by [@areofyl](https://github.com/areofyl),
which in turn comes from [gentoo.c](https://github.com/areofyl/gentoo.c).
It adds the `3dfetch` name, keeps the info labels in the color of the logo,
and a few other things.

> New here? Start with the [getting started guide](docs/tutorial.md).

## Build & run

```
make
./fetch
```

Press any key to stop. The keypress passes through to the shell, so it
works as a startup fetch. Ctrl-C works too (but is less cool). Click and
drag the logo to rotate it by hand, release to fling it spinning.

## Install

### From source

```
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch
make
sudo make install
```

`PREFIX=~/.local make install` if you don't want it system-wide.

This installs two commands, `fetch` and `3dfetch`. They are the same
program, so you can launch it with whichever name you prefer:

```
3dfetch
```

### Prebuilt binaries

Grab a binary from the [releases page](https://github.com/Rutytoi220/3dfetch/releases):

```
tar xf 3dfetch-linux-x86_64.tar.gz
sudo install -m 755 3dfetch-linux-x86_64 /usr/local/bin/3dfetch
```

There are builds for x86_64 and aarch64, with checksums in `SHA256SUMS`.

### Flatpak

The Flatpak manifest lives in [flatpak/](flatpak/). It isn't on Flathub
yet — that submission has to be opened by hand — so for now build and
install it yourself:

```
flatpak install --user -y flathub org.flatpak.Builder
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch
flatpak run --command=flathub-build org.flatpak.Builder --install flatpak/io.github.rutytoi220._3dfetch.yml
```

Then run it:

```
flatpak run io.github.rutytoi220._3dfetch
```

Flatpak exports the binary under the app's ID rather than the name you
installed it with, so if you want to type `3dfetch` you'll need a symlink:

```
ln -sf ~/.local/share/flatpak/exports/bin/io.github.rutytoi220._3dfetch ~/.local/bin/3dfetch
```

Once it lands on Flathub this gets shorter:

```
flatpak install flathub io.github.rutytoi220._3dfetch
```

The manifest bundles fastfetch, which draws the logos, and the app reads
your host's `/etc/os-release` so it picks the right one for your
distribution.

### Homebrew

```
brew trust Rutytoi220/tap
brew install Rutytoi220/tap/3dfetch
```

The formula is called `threefetch` under the hood (Homebrew formula names
can't start with a digit), with a `3dfetch` alias. It installs both the
`3dfetch` and `fetch` commands.

### Arch Linux

Not in the AUR yet — the submission needs a maintainer account. The
PKGBUILD is in [aur/](aur/) and builds straight from the release tarball:

```
git clone https://github.com/Rutytoi220/3dfetch
cd 3dfetch/aur
makepkg -si
```

### Nix

```
nix run github:Rutytoi220/3dfetch
```

## Colors

The info labels (`OS`, `Host`, `Kernel`, ...) take the color the logo is
drawn in, so the text always matches the logo next to it. The logo keeps
its own colors:

```
3dfetch
```

On Arch that means the text is the same bright blue as the logo, on Bazzite
the same purple, on Linux Mint the same green, and so on. A logo that
carries no colors of its own (a custom `logo.txt`, say) falls back to the
distribution's brand color, and then to the `ANSI_COLOR` hint in
`/etc/os-release`.

Set `label_color` in your config to override the label color, or
`truecolor=0` if your terminal can't do 24-bit color.

<details>
<summary><h2>Package managers</h2></summary>

### Nix

```bash
nix run github:Rutytoi220/3dfetch
```

Or as a flake input, with a home-manager module — see
[nix/README.md](nix/README.md):

```nix
inputs.threefetch.url = "github:Rutytoi220/3dfetch";
```

### RPM (Fedora, openSUSE)

Build the spec that ships in the repo:

```bash
sudo dnf install @development-tools
rpmbuild -ba fetch.spec
sudo dnf install ~/rpmbuild/RPMS/*/3dfetch-*.rpm
```

On openSUSE, swap `dnf` for `zypper` and install `-t pattern devel_basis`.

### Debian / Ubuntu

Build a `.deb` locally:

```bash
sudo apt install build-essential devscripts debhelper
dpkg-buildpackage -us -uc -b
sudo apt install ../3dfetch_*.deb
```

Nothing here is in a distro repository yet — these build from the repo,
same as the Flatpak and the AUR PKGBUILD.

</details>

## Logos

Custom logos: [docs/custom-logos.md](docs/custom-logos.md)

By default it auto-detects your distro and grabs the logo from fastfetch
(if installed) with its original per-character colors preserved. Works with
any of fastfetch's 500+ distro logos!

You can also specify one directly:

```
./fetch -l arch
./fetch -l NixOS
./fetch -l asahi
```

Or drop a custom logo in `~/.config/fetch/logo.txt`:

```
# distro: gentoo
         -/oyddmdhs+:.
     -odNMMMMMMMMNNmhy+-`
...
```

Without fastfetch, the built-in Gentoo logo is used.

## System info

All system info is gathered natively. No fastfetch or neofetch needed:

- **OS** - `/etc/os-release`
- **Host** - `/proc/device-tree/model` or `/sys/class/dmi/id/product_name`
- **Kernel** - `uname()`
- **Uptime** - `/proc/uptime`
- **Packages** - emerge, pacman, dpkg, rpm, xbps, apk, flatpak, brew, nixpkgs
- **Shell** - parent process detection (not just `$SHELL`)
- **Display** - per-connector DRM enumeration (multi-monitor): active resolution and refresh rate from the CRTC mode, monitor name and physical size from EDID, built-in vs external
- **WM** - process scanning + DE-to-WM mapping
- **Display Manager** - process scanning
- **Theme/Icons/Font** - `~/.config/gtk-3.0/settings.ini`, `~/.gtkrc-2.0`, and Qt (`qt6ct`/`qt5ct`, `~/.config/kdeglobals`) on Linux, `defaults read` (macOS)
- **Cursor** - `~/.config/gtk-3.0/settings.ini` (Linux only)
- **CPU** - `/proc/cpuinfo`, device-tree (Apple Silicon), or `sysctl` (macOS)
- **GPU** - DRM + `lspci` for full names (Linux), `system_profiler` (macOS)
- **Memory/Swap** - `/proc/meminfo` (Linux), `vm_stat` (macOS)
- **Disk** - `statvfs()` + `/proc/mounts` (Linux), `getmntinfo` (macOS) – supports multiple mount points via config
- **Battery** - `energy_now/energy_full` plus `model_name` (Linux), IOKit (macOS)
- **Power Profile** - `/sys/firmware/acpi/platform_profile`, fallback `powerprofilesctl get 2>/dev/null` (Linux)
- **Local IP** - `getifaddrs()`

Stats like memory, battery, and uptime update in real-time while the logo spins.

## Config

Full reference: [docs/configuration.md](docs/configuration.md)

Create `~/.config/fetch/config` to customize:

```
# fields – list to show, in this order
# remove or comment out to hide
os
host
kernel
uptime
packages
shell
display
wm
displaymanager
theme
icons
font
cursor
terminal
cpu
gpu
memory
swap
disk
ip
battery
powerprofile
locale
colors

# separators (blank line between groups)
# ---

# custom static fields
# custom_Pronouns=he/him
# custom_Website=example.com

# extra disks (add more mount points)
# disk=/home
# disk=/data

# appearance
# label_color=magenta   (red, green, yellow, blue, magenta, cyan, white)
# separator=─           (character for the title separator)
# shading_mode=ascii    (ascii, or opt into blocks / sextants)
# shading=.,-~:;=!*#$@  (characters for 3D shading, supports UTF-8)
# box=0                 (adds a box around the system-data, 0 = off, 1 = on)

# logo colors (override distro defaults)
# logo_outer=magenta    (extruded side color)
# logo_inner=white      (front/back face color)

# 3d
# light=top-left        (top-left, top-right, top, left, right, front, bottom-left, bottom-right)
# spin=xy               (x, y, or xy)
# speed=1.0             (rotation speed)
# size=1.0              (logo scale, e.g. 2.0 for double size)
# depth=1.0             (3D extrusion depth, e.g. 3.0 for chunkier look)
# height=36             (override render height in rows)
# v_alignment=top       (top, center, bottom)
# h_alignment=left      (left, center, right)
```

## Options

| Flag | Description |
|------|-------------|
| `-l`, `--logo <name>` | Use a logo from fastfetch by name |
| `--rotate-x` | Lock rotation to X axis only |
| `--rotate-y` | Lock rotation to Y axis only |
| `-s`, `--speed <float>` | Speed multiplier (default 1.0, no upper limit, negative spins backwards) |
| `--size <float>` | Scale the logo (e.g. 2.0 for double size) |
| `--depth <float>` | Scale the 3D depth (default 1.0) |
| `--height <n>` | Override render height in rows |
| `--no-info` | Just the logo, no system info |
| `--nggyu` | Surprise. |
| `--no-color` | Disable coloring |
| `--frames <n>` | Stop after n frames (default 2000) |
| `--infinite` | Run forever (keypress or Ctrl-C to exit) |
| `--shading-mode <mode>` | `ascii` (default), or opt into sub-cell blocks with `sextants` (2x3) or `blocks` (2x2) |
| `--shading-chars <str>` | Custom shading ramp, supports UTF-8 |
| `--box` | Draw a border box around the info block |
| `-V`, `--version` | Show version |
| `-h`, `--help` | Show this help |

CLI flags override config file settings.

## Shading modes

Full reference: [docs/shading-modes.md](docs/shading-modes.md)

ASCII is the default. The sub-cell modes are opt-in, and trade the donut.c look
for a silhouette that lands on a fraction of a cell instead of snapping to the
character grid.

| `ascii` (default) | `blocks` | `sextants` |
|:---:|:---:|:---:|
| ![ascii](docs/shading-ascii.png) | ![blocks](docs/shading-blocks.png) | ![sextants](docs/shading-sextants.png) |
| brightness mapped onto `.,-~:;=!*#$@`, one character per cell | coverage sampled 2×2, edges on quadrants | coverage sampled 2×3, edges on block sextants |

`sextants` needs a terminal that draws the Symbols for Legacy Computing block
(kitty, Ghostty, foot and WezTerm do it themselves, so the font does not matter);
`blocks` works anywhere with a UTF-8 locale.

Same logo, same frame, same terminal palette in all three.

## Contributing

PRs are welcome! If you want to add a feature, fix a bug, or package fetch for
your distro, go for it. I try to keep the codebase small and easy to understand,
so smaller PRs are easier to merge than big ones.

If you want to chat about ideas before writing code, reach out on
[Reddit](https://www.reddit.com/user/areofyl) or open an issue.

## How it works

For a deep dive with visuals and code, see the [full blog post](https://asdesai.com/blog/how-fetch-works/).

1. **Logo loading** – reads ASCII/Unicode art from `~/.config/fetch/logo.txt` or
   grabs a distro logo via fastfetch. ANSI color codes are parsed and preserved
   per-character.

2. **Heightmap** – each character gets a weight based on visual density (`@` is
   heavy, `.` is light, `█` is full, `░` is thin). The weight becomes a Z height,
   turning the flat logo into a 3D relief map. Logos with low height variance
   (uniform characters) get their depth auto-scaled so they don't look flat.

3. **Point cloud** – the heightmap is sampled into 3D points. Interior cells get
   multiple Z layers for a solid extrusion, edge cells get only front and back
   faces to keep outlines clean.

4. **Surface normals** – computed from the height gradient at each cell using
   finite differences, giving each point a direction for lighting.

5. **Rotation + projection** – every frame, all points are rotated around X/Y
   axes, then perspective-projected onto the terminal grid with a z-buffer to
   handle occlusion.

6. **Shading** – Blinn-Phong lighting (diffuse + specular) gives every visible
   point a brightness, which maps onto the `.,-~:;=!*#$@` ramp, one character
   per cell. `--shading-mode sextants` or `blocks` instead samples coverage
   finer than the character cell – 2×3 or 2×2 – and each cell picks whichever
   glyph carries the right amount of ink: a shade block (`░▒▓█`) where the cell
   is filled, a partial block where the silhouette cuts through it. So an edge
   lands on a fraction of a cell instead of snapping to the character grid.

   Logos that ship their own colors keep them. The rest are two-toned by
   surface: front and back faces in `logo_inner`, extruded sides in
   `logo_outer`.

7. **Rendering** – the entire frame is written in a single `write()` syscall to
   avoid flicker. System info is displayed alongside the animation and
   fast-changing fields (uptime, memory, swap) update live every second.

Single file C, no dependencies beyond libm.
