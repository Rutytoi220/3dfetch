# AUR package

The PKGBUILD here publishes 3dfetch to the Arch User Repository, so
users can install it with a single command:

```bash
yay -S 3dfetch
```

## Publishing it

The AUR is a git repository over SSH and every package needs an account
of its own, so these steps have to be done by you rather than by a bot:

1. Register at <https://aur.archlinux.org/account/register> and add an
   SSH key under *My Account* → *SSH Public Keys*.

2. Clone the package repository and push this PKGBUILD to it:

   ```bash
   git clone ssh://aur@aur.archlinux.org/3dfetch.git
   cd 3dfetch
   cp /path/to/3dfetch/aur/PKGBUILD .
   git add PKGBUILD
   git commit -m "Initial upload: 3dfetch 0.1.0"
   git push
   ```

3. The package is then built and published by the AUR automatically.
   Check it at <https://aur.archlinux.org/packages/3dfetch>.

## Before every release

Bump `pkgver` in the PKGBUILD, update `sha256sums` to the checksum of
the new source tarball, and push:

```bash
updpkgsums
git commit -am "up to v0.2.0" && git push
```

`updpkgsums` comes with the `pacman-contrib` package.
