%define _lesstifdir	%_prefix/LessTif 

%define name		lesstif
%define version		0.95.0
%define release		%mkrel 1

%define major		2
%define libname 	%mklibname %name %major
%define develname	%mklibname %name -d

Summary:	A free Motif clone
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	LGPL
URL:		http://www.lesstif.org/
Group:		System/Libraries
Source:		http://prdownloads.sourceforge.net/%name/%name-%version.tar.gz
Source2:	mwm.png.bz2
Source3:	mwm32.png.bz2
Source4:	lesstif-mwm-menu-xdg
Patch0:		lesstif-mdk-menu.patch
Patch1:		lesstif-0.93.94-libdir.patch
Patch2:		lesstif-0.93.94-libtool.patch
# Slightly ugly hack to disable libDtPrint build. It seems to be
# completely useless, I don't think any apps use it. Debian doesn't
# ship it. - AdamW 2007/07
Patch3:		lesstif-0.95.0-disable-dtprint.patch

BuildRequires:	flex, X11-devel, bison, xpm-devel, fontconfig-devel
BuildRequires:	imake
BuildRequires:  autoconf

%description
Lesstif is an API compatible clone of the Motif toolkit. It implements 
the Motif 2.1 API. Many Motif applications compile and run 
out-of-the-box with LessTif, and we want to hear about those that 
don't.

%package -n %libname
Summary:	Lesstif libraries
Group:		System/Libraries
Requires:	lesstif = %version
Obsoletes:	%{mklibname lesstif 1}

%description -n %libname
Lesstif is an API compatible clone of the Motif toolkit. It implements 
the Motif 2.1 API. Many Motif applications compile and run 
out-of-the-box with LessTif, and we want to hear about those that 
don't.

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
Requires:	lesstif = %version
Conflicts:	openmotif libopenmotif-devel

%description clients
Uil and xmbind clients for Lesstif.

%package -n %develname
Group:		Development/C
Summary:	Static library and header files for Lesstif/Motif development
Requires:	%libname = %version
Obsoletes:	%{name}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Conflicts:	libopenmotif-devel

%description -n %develname
This package contains the lesstif static library and header files
required to develop motif-based applications.

This package also contains development documentation in html (Lessdox),
and mxmkmf for Lesstif.

%prep
%setup -q -n lesstif-%{version}
%patch0 -p0 -b .mdk
%patch1 -p1 -b .libdir
%patch2 -p1 -b .libtool
autoconf
%patch3 -p1 -b .dtprint
LESSTIFTOP=$PWD

%build
CFLAGS="$RPM_OPT_FLAGS" ./configure \
				--prefix=%{_prefix} \
				--libdir=%{_libdir} \
                		--mandir=%{_mandir} \
				--enable-shared \
				--enable-static \
				--disable-maintainer-mode \
				--disable-debug \
				--enable-production


%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

install -d $RPM_BUILD_ROOT/etc/X11
ln -sf ../..%{_libdir}/X11/mwm $RPM_BUILD_ROOT/etc/X11/mwm

install -d $RPM_BUILD_ROOT%_lesstifdir/doc/Lessdox
install -c -m 644 doc/lessdox/*/*.html $RPM_BUILD_ROOT%_lesstifdir/doc/Lessdox || :

# generate config files 
cd $RPM_BUILD_ROOT%{_prefix}/lib/X11/config
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



cd $RPM_BUILD_ROOT%{_prefix}/bin/
sed -e 's/imake $args/imake -T Imake-lesstif.tmpl $args/' < `which xmkmf` > mxmkmf

# menu support
mv $RPM_BUILD_ROOT%{_libdir}/X11/mwm/system.mwmrc $RPM_BUILD_ROOT%{_libdir}/X11/mwm/system.mwmrc-menu
mkdir -p $RPM_BUILD_ROOT%_sysconfdir/menu.d
install -m 0755 %{SOURCE4} $RPM_BUILD_ROOT%_sysconfdir/menu.d/lesstif-mwm

#icons
mkdir -p $RPM_BUILD_ROOT%{_iconsdir}/hicolor/{16x16,32x32}/apps
bzcat %{SOURCE2} >$RPM_BUILD_ROOT%{_iconsdir}/hicolor/16x16/apps/mwm.png
bzcat %{SOURCE3} >$RPM_BUILD_ROOT%{_iconsdir}/hicolor/32x32/apps/mwm.png

rm -f $RPM_BUILD_ROOT%{_prefix}/lib/X11/config/host.def

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_lesstifdir}/[ABCFIR]*
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/app-defaults/Mwm
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/mwm/*

%post -n %libname -p /sbin/ldconfig
%postun -n %libname -p /sbin/ldconfig

%post mwm
%update_menus

%postun mwm
%clean_menus

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
#%doc etc/{example.motifbind,motifbind.sun+linux}
%doc AUTHORS BUG-REPORTING COPYING COPYING.LIB CREDITS
%doc ChangeLog NEWS
%doc README ReleaseNotes.txt ReleaseNotes.html
%doc doc/www.lesstif.org/FAQ.html
%{_mandir}/man1/lesstif.1*

%files -n %libname
%defattr(-,root,root,-)
%{_libdir}/*.so.*

%files mwm
%defattr(-,root,root,-)
%doc clients/Motif-2.1/mwm/{COPYING,README}
%config(noreplace) %_sysconfdir/X11/mwm
%{_sysconfdir}/menu.d/%{name}-mwm
%{_libdir}/X11/mwm
%{_libdir}/X11/app-defaults/Mwm
%{_mandir}/man1/mwm.1*
%{_mandir}/man5/mwmrc.5*
%{_bindir}/mwm
%{_iconsdir}/hicolor/16x16/apps/mwm.png
%{_iconsdir}/hicolor/32x32/apps/mwm.png

%files clients
%defattr(-,root,root,-)
%doc doc/UIL.txt
%{_bindir}/uil
%{_bindir}/xmbind
%{_mandir}/man1/xmbind.1*

%files -n %develname
%defattr(-,root,root,755)
#%doc doc/{*.html,*.txt,lessdox/*/*.html,www.lesstif.org}
%doc %{_lesstifdir}/doc
%{_includedir}/*
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_bindir}/motif-config
%{_bindir}/mxmkmf
%{_prefix}/lib/X11/config/*
%{_datadir}/aclocal/ac_find_motif.m4
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/man5/*

