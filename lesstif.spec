%define _disable_ld_no_undefined 1

%define lessdoxdir     %{_docdir}/%{name}
%define major	2
%define libmrm	%mklibname Mrm %{major}
%define libuil	%mklibname Uil %{major}
%define libxm	%mklibname Xm %{major}
%define devname	%mklibname %{name} -d

Summary:	A free Motif clone
Name:		lesstif
Version:	0.95.2
Release:	14
License:	LGPLv2
Url:		http://www.lesstif.org/
Group:		System/Libraries
Source0:	http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}.tar.bz2
Source2:	mwm.png
Source3:	mwm32.png
Source4:	lesstif-mwm-menu-xdg
# Fedora patches
Patch0:	lesstif-0.95.2-motif-config.patch
Patch1:	lesstif-0.95.0-XxxxProperty-64bit.patch
# Fix PutPixel32 crashing on 64 bit (RH bug #437133)
Patch2:	lesstif-0.95.0-PutPixel32.patch
Patch3:	lesstif-0.95.2-link-fontconfig.patch
Patch4:	lesstif-0.95.2-automake-1.13.patch

# For xdg_menu
BuildRequires:	desktop-common-data
BuildRequires:	flex
BuildRequires:	imake
BuildRequires:	x11-util-cf-files
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xft)
BuildRequires:	pkgconfig(xt)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xrender)
# Having libXp installed while building lesstif results in lesstif linking
# to libXp -- which we don't want, libXp has been deprecated for ages and
# apparently never worked right.
BuildConflicts:	pkgconfig(xp)

%description
Lesstif is an API compatible clone of the Motif toolkit. It implements 
the Motif 2.1 API. Many Motif applications compile and run 
out-of-the-box with LessTif, and we want to hear about those that 
don't.

%package -n %{libmrm}
Summary:	Lesstif libraries
Group:		System/Libraries
Obsoletes:	%{mklibname lesstif 2}

%description -n %{libmrm}
This package contains a shared library for %{name}.

%package -n %{libuil}
Summary:	Lesstif libraries
Group:		System/Libraries
Obsoletes:	%{mklibname lesstif 2}

%description -n %{libuil}
This package contains a shared library for %{name}.

%package -n %{libxm}
Summary:	Lesstif libraries
Group:		System/Libraries
Obsoletes:	%{mklibname lesstif 2}

%description -n %{libxm}
This package contains a shared library for %{name}.

%package mwm
Summary:	Lesstif Motif window manager clone based on fvwm
Group:		Graphical desktop/Other
Requires:	desktop-common-data
Conflicts:	openmotif

%description mwm
MWM is a window manager that adheres largely
to the Motif mwm specification.

%package clients
Summary:	Lesstif clients
Group:		Graphical desktop/Other
Requires:	lesstif = %{version}
Conflicts:	openmotif libopenmotif-devel

%description clients
Uil and xmbind clients for Lesstif.

%package -n %{devname}
Group:		Development/C
Summary:	Development library and header files for Lesstif/Motif development
Requires:	%{libmrm} = %{version}
Requires:	%{libuil} = %{version}
Requires:	%{libxm} = %{version}
Provides:	%{name}-devel = %{version}-%{release}
Conflicts:	libopenmotif-devel

%description -n %{devname}
This package contains the lesstif development library and header files
required to develop motif-based applications.

This package also contains development documentation in html (Lessdox),
and mxmkmf for Lesstif.

%prep
%setup -q
%apply_patches

# Fix autoconf with libtool 2.2
# http://trac.macports.org/ticket/18287
sed -i -e "s:LT_HAVE_FREETYPE:FINDXFT_HAVE_FREETYPE:g" -e "s:LT_HAVE_XRENDER:FINDXFT_HAVE_XRENDER:g" acinclude.m4

libtoolize --force
aclocal -I .
automake -a
autoconf
#LESSTIFTOP=$PWD

%build
export CFLAGS="%{optflags} -DMWM_DDIR=\\\"%{_datadir}/X11/mwm\\\""
%configure2_5x \
	-enable-shared \
	-disable-maintainer-mode \
	-disable-debug \
	-enable-production
ln configure.ac configure.in

perl -p -i -e '\
s@^(appdir = ).*(/X11/app-defaults)@$1/usr/share$2@;\
s@^(mwmddir = ).*(/X11/mwm)@$1/usr/share$2@'\
    clients/Motif-2.1/mwm/Makefile
perl -p -i -e 's@^(configdir = ).*@$1%{_datadir}/X11/config@' lib/config/Makefile
perl -p -i -e 's@^(rootdir = ).*@$1%{lessdoxdir}@' `find doc -name Makefile`
perl -p -i -e 's@/X11R6/@/@g' `find . -name Makefile` scripts/motif-config.in

%make

perl -p -i -e '\
s@-L/usr(/X11R6)?/%{_lib} @@g;\
s@-I/usr(/X11R6)?/include @@g'\
    scripts/motif-config

%install
%makeinstall_std

install -d %{buildroot}%{lessdoxdir}/Lessdox
install -c -m 644 doc/lessdox/*/*.html %{buildroot}%{lessdoxdir}/Lessdox || :

# generate config files 
mkdir -p %{buildroot}%{_datadir}/X11/config
cd %{buildroot}%{_datadir}/X11/config
#mv Imake.tmpl Imake-lesstif.tmpl.orig

perl -ne ' 
    if( /#include <Imake.rules>/ ){              
        print $_;
        print "#include <Motif-lesstif.tmpl>\n";
        print "#include <Motif-lesstif.rules>\n";
    }
    elsif ( /IMAKE_CMD = \$\(IMAKE\)/ ){
        print STDERR "found\n";
        s|\$\(IMAKE\)|\$(IMAKE) -T Imake-lesstif.tmpl|;
        print $_;
    }
    else {
        print $_;
    }
' < %{_datadir}/X11/config/Imake.tmpl > Imake-lesstif.tmpl


cd %{buildroot}%{_bindir}
sed -e 's/imake $args/imake -T Imake-lesstif.tmpl $args/' < `which xmkmf` > mxmkmf

# menu support
mkdir -p %{buildroot}/%{_prefix}/lib/menu
install -m 0755 %{SOURCE4} %{buildroot}%{_prefix}/lib/menu/lesstif-mwm

#icons
mkdir -p %{buildroot}%{_iconsdir}/hicolor/{16x16,32x32}/apps
cp %{SOURCE2} %{buildroot}%{_iconsdir}/hicolor/16x16/apps/mwm.png
cp %{SOURCE3} %{buildroot}%{_iconsdir}/hicolor/32x32/apps/mwm.png

rm -f %{buildroot}%{_datadir}/X11/config/host.def

# remove unpackaged files
rm -fr %{buildroot}/%{_prefix}/LessTif

%files
%doc AUTHORS BUG-REPORTING COPYING COPYING.LIB CREDITS
%doc ChangeLog NEWS
%doc README ReleaseNotes.txt ReleaseNotes.html
%doc doc/www.lesstif.org/FAQ.html
%{_mandir}/man1/lesstif.1*

%files -n %{libmrm}
%{_libdir}/libMrm.so.%{major}*

%files -n %{libuil}
%{_libdir}/libUil.so.%{major}*

%files -n %{libxm}
%{_libdir}/libXm.so.%{major}*

%files mwm
%doc clients/Motif-2.1/mwm/{COPYING,README}
%{_prefix}/lib/menu/%{name}-mwm
%{_datadir}/X11/mwm
%{_datadir}/X11/app-defaults/Mwm
%{_mandir}/man1/mwm.1*
%{_mandir}/man5/mwmrc.5*
%{_bindir}/mwm
%{_iconsdir}/hicolor/16x16/apps/mwm.png
%{_iconsdir}/hicolor/32x32/apps/mwm.png

%files clients
%doc doc/UIL.txt
%{_bindir}/uil
%{_bindir}/xmbind
%{_mandir}/man1/xmbind.1*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%{_bindir}/motif-config
%{_bindir}/mxmkmf
%{_datadir}/X11/config/*
%{_datadir}/aclocal/ac_find_motif.m4
%{_mandir}/man1/ltversion.1.*
%{_mandir}/man1/uil.1.*
%{_mandir}/man3/*
%{_mandir}/man5/*
%exclude %{_mandir}/man5/mwmrc.5*

