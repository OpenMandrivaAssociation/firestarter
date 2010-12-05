Summary:	 A GUI firewall tool for GNOME 2
Name:		 firestarter
Version:	 1.0.3
Release:	 %mkrel 16
License:	 GPL
Group:		 System/Configuration/Networking
URL:		 http://firestarter.sourceforge.net
Source0:	 %{name}-%{version}.tar.bz2
Source1:	 %{name}.init
Patch0:		 firestarter-1.0.3-fix-str-fmt.patch
BuildRequires:	 imagemagick
BuildRequires:	 libgnomeui2-devel
Buildrequires:   perl(XML::Parser)
Buildrequires:   libglade2.0-devel
Buildrequires:   desktop-file-utils
Requires:	 userspace-ipfilter
Requires:	 usermode
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRoot:	 %{_tmppath}/%{name}-%{version}-buildroot

%description
FireStarter is a GUI firewall tool for setting up, monitoring
and administring Linux firewalls under GUI. It features:

  * User friendly graphical interface optimized for GNOME 2.
  * Easy to use wizard customizes firewall to your needs.
  * Real-time firewall hit monitor shows hostile probes.
  * Open and close ports, shaping your firewalling with a few mouse clicks.
  * Set up NAT or port forwarding for your home or company LAN.
  * Designed for the GNOME desktop, but works in KDE too.
  * Translated into over 38 languages.
  * Advanced kernel tuning features
  * Supports Linux kernel versions 2.6, 2.4 and 2.2.

%prep
%setup -q
%patch0 -p0

cp %{SOURCE1} %{name}.init

%build
%configure2_5x
%make

%install
rm -rf %{buildroot}

GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1 %makeinstall_std bindir=%{_sbindir}
mkdir -p %{buildroot}%{_bindir}
ln -sf consolehelper %{buildroot}%{_bindir}/%{name}

mkdir -p %{buildroot}%{_initrddir}
install -m0755 %{name}.init %{buildroot}%{_initrddir}/%{name}

# own firestarter generated files
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
for i in blocked-hosts blocked-ports forward open-ports stealthed-ports trusted-hosts; do
  touch %{buildroot}%{_sysconfdir}/%{name}/$i
done
echo '#!/bin/sh' > %{buildroot}%{_sysconfdir}/%{name}/firewall.sh

%{find_lang} %{name}

### icons and menu entry
mkdir -p %{buildroot}%{_iconsdir}  \
	 %{buildroot}%{_liconsdir} \
	 %{buildroot}%{_miconsdir}
install -m 0644         pixmaps/firestarter.png %{buildroot}%{_liconsdir}/%{name}.png
convert -geometry 32x32 pixmaps/firestarter.png %{buildroot}%{_iconsdir}/%{name}.png
convert -geometry 16x16 pixmaps/firestarter.png %{buildroot}%{_miconsdir}/%{name}.png

## xdg
mkdir -p %{buildroot}%_datadir/applications
cp %{buildroot}%_datadir/gnome/apps/Internet/firestarter.desktop %{buildroot}%_datadir/applications
perl -pi -e "s|%{name}\.png|%{name}|g" %{buildroot}%_datadir/applications/firestarter.desktop

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="X-MandrivaLinux-System-Configuration-Networking;Settings;Network" \
  --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

### consolehelper entry
mkdir -p %{buildroot}%{_sysconfdir}/security/console.apps
cat > %{buildroot}%{_sysconfdir}/security/console.apps/%{name} <<EOF
USER=root
PROGRAM=%{_sbindir}/%{name}
SESSION=true
FALLBACK=false
EOF

### pam entry
mkdir -p %{buildroot}%{_sysconfdir}/pam.d
cat > %{buildroot}%{_sysconfdir}/pam.d/%{name} <<EOF
auth       sufficient   pam_rootok.so
auth       required     pam_pwdb.so
session    optional     pam_xauth.so
account    required     pam_permit.so
EOF

%post
%if %mdkversion < 200900
%post_install_gconf_schemas firestarter
%endif

if [ $1 -eq 1 ]; then
  touch %{_sysconfdir}/%{name}/blocked-hosts	\
	%{_sysconfdir}/%{name}/blocked-ports	\
	%{_sysconfdir}/%{name}/forward		\
	%{_sysconfdir}/%{name}/open-ports	\
	%{_sysconfdir}/%{name}/stealthed-ports	\
	%{_sysconfdir}/%{name}/trusted-hosts
  echo "You have to decide whether to let iptables startup script"
  echo "or firestarter to control your firewall, using chkconfig."
fi
%_post_service %{name}
%if %mdkversion < 200900
%update_menus
%endif

%preun
%_preun_service %{name}
%preun_uninstall_gconf_schemas "$1"

%if %mdkversion < 200900
%postun
%clean_menus
%endif

%triggerpostun -- firestarter <= 0.9.2-1mdk
echo "You have to decide whether to let iptables startup script"
echo "or firestarter to control your firewall, using chkconfig."

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc README ChangeLog AUTHORS TODO COPYING CREDITS
%{_bindir}/*
%{_datadir}/gnome/apps/*/*.desktop
%{_datadir}/applications/*.desktop
%{_datadir}/pixmaps/*
%{_datadir}/%name
%{_sbindir}/*
%{_iconsdir}/%{name}.png
%{_liconsdir}/%{name}.png
%{_miconsdir}/%{name}.png
%{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/pam.d/%{name}
%config(noreplace) %{_sysconfdir}/security/console.apps/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/non-routables
%ghost %{_sysconfdir}/%{name}/blocked-hosts
%ghost %{_sysconfdir}/%{name}/blocked-ports
%attr(0755, root, root) %config(noreplace,missingok) %{_sysconfdir}/%{name}/firewall.sh
%ghost %{_sysconfdir}/%{name}/forward
%ghost %{_sysconfdir}/%{name}/open-ports
%ghost %{_sysconfdir}/%{name}/stealthed-ports
%ghost %{_sysconfdir}/%{name}/trusted-hosts
%{_sysconfdir}/gconf/schemas/*
