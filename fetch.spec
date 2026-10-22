Name:           3dfetch
Version:        0.5.1
Release:        1%{?dist}
Summary:        Animated 3D fetch tool for your terminal

License:        ISC
URL:            https://github.com/Rutytoi220/3dfetch
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/3dfetch-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make

%description
A donut.c-inspired fetch tool that spins your distro logo in 3D with live-updating
system info. Takes any ASCII/Unicode distro logo, turns each character into a point
cloud based on its visual density, and renders it as a rotating 3D relief with
Blinn-Phong shading. System info is gathered natively from /proc, /sys, and GTK
config — no external dependencies required.

Installs both the 3dfetch and fetch commands.

%prep
%autosetup -n 3dfetch-%{version}

%build
%make_build

%install
%make_install DESTDIR=%{buildroot} PREFIX=%{_prefix}

%files
%doc README.md
%license LICENSE
%{_bindir}/fetch
%{_bindir}/3dfetch

%changelog
* Thu Oct 22 2026 Rutytoi220 <154633139+Rutytoi220@users.noreply.github.com> - 0.5.1-1
- 3dfetch 0.5.1: full-width rickroll at its original speed, packaging fixes

* Thu Oct 22 2026 Rutytoi220 <154633139+Rutytoi220@users.noreply.github.com> - 0.5.0-1
- 3dfetch 0.5.0: logo-coloured labels, unlimited --speed, --nggyu
