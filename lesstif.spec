%define _disable_ld_no_undefined 1

%define major		2
%define libmrm		%mklibname Mrm %{major}
%define libuil		%mklibname Uil %{major}
%define libxm		%mklibname Xm %{major}
%define develname	%mklibname %{name} -d

%define lessdoxdir     %{_docdir}/%{name}

Summary:	A free Motif clone
Name:		lesstif
Version:	0.95.2
Release:	9
License:	LGPL
URL:		http://www.lesstif.org/
Group:		System/Libraries
Source:		http://downloads.sourceforge.net/project/%{name}/%{name}/%{version}/%{name}-%{version}.tar.bz2
Source2:	mwm.png
Source3:	mwm32.png
Source4:	lesstif-mwm-menu-xdg
# Fedora patches
Patch0: lesstif-0.95.2-motif-config.patch
Patch1: lesstif-0.95.0-XxxxProperty-64bit.patch
# Fix PutPixel32 crashing on 64 bit (RH bug #437133)
Patch2: lesstif-0.95.0-PutPixel32.patch
Patch3:		lesstif-0.95.2-link-fontconfig.patch
Patch4:		lesstif-0.95.2-automake-1.13.patch

BuildRequires:	flex
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xft)
BuildRequires:	pkgconfig(xt)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	fontconfig-devel
BuildRequires:	imake x11-util-cf-files
# For xdg_menu
BuildRequires:	desktop-common-data

# Having libXp installed while building lesstif results in lesstif linking
# to libXp -- which we don't want, libXp has been deprecated for ages and
# apparently never worked right.
BuildConflicts:	libxp-devel

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

%package -n %{develname}
Group:		Development/C
Summary:	Development library and header files for Lesstif/Motif development
Requires:	%{libmrm} = %{version}
Requires:	%{libuil} = %{version}
Requires:	%{libxm} = %{version}
Obsoletes:	%{name}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Conflicts:	libopenmotif-devel

%description -n %{develname}
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

perl -pi -e '\
s@^(appdir = ).*(/X11/app-defaults)@$1/usr/share$2@;\
s@^(mwmddir = ).*(/X11/mwm)@$1/usr/share$2@'\
    clients/Motif-2.1/mwm/Makefile
perl -pi -e 's@^(configdir = ).*@$1%{_datadir}/X11/config@' lib/config/Makefile
perl -pi -e 's@^(rootdir = ).*@$1%{lessdoxdir}@' `find doc -name Makefile`
perl -pi -e 's@/X11R6/@/@g' `find . -name Makefile` scripts/motif-config.in

%make

perl -pi -e '\
s@-L/usr(/X11R6)?/%{_lib} @@g;\
s@-I/usr(/X11R6)?/include @@g'\
    scripts/motif-config

%install
rm -rf %{buildroot}
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
mkdir -p %{buildroot}/%_prefix/lib/menu
install -m 0755 %{SOURCE4} %{buildroot}%_prefix/lib/menu/lesstif-mwm

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
%_prefix/lib/menu/%{name}-mwm
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

%files -n %{develname}
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



%changelog
* Mon Dec 26 2011 Matthew Dawkins <mattydaw@mandriva.org> 0.95.2-6
+ Revision: 745381
- fixed build
- added back post/un menus
- removed dup man5 page in devel
- rebuild
- split out each lib pkgs
- disable static
- cleaned up spec
- employed apply_patches (made p3 to patch level 1)

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 0.95.2-5
+ Revision: 666072
- mass rebuild

* Wed Feb 02 2011 Funda Wang <fwang@mandriva.org> 0.95.2-4
+ Revision: 635357
- fix conlficts file
- tighten BR

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.95.2-3mdv2011.0
+ Revision: 606401
- rebuild

* Sun Mar 14 2010 Oden Eriksson <oeriksson@mandriva.com> 0.95.2-2mdv2010.1
+ Revision: 519016
- rebuild

* Tue Aug 04 2009 Frederik Himpe <fhimpe@mandriva.org> 0.95.2-1mdv2010.0
+ Revision: 409499
- Update to new version 0.95.2
- Fix autoconf call with libtool 2.2 (fix via Macports)
- Remove old unneeded patches
- Sync patches with Fedora

* Mon Jun 15 2009 Funda Wang <fwang@mandriva.org> 0.95.0-7mdv2010.0
+ Revision: 385992
- fix Xxxx Property from fedora
- more unbziped
- bunzip2 png files

* Sun Dec 21 2008 Oden Eriksson <oeriksson@mandriva.com> 0.95.0-6mdv2009.1
+ Revision: 316982
- rediffed fuzzy patches
- safer fix to disable libDtPrint (P3)
- use %%ldflags

* Fri Jul 04 2008 Anssi Hannula <anssi@mandriva.org> 0.95.0-5mdv2009.0
+ Revision: 231746
- move headers back to /usr/include where they are expected by other
  software and where they are on other distributions
- ensure major correctness in file list

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 0.95.0-4mdv2009.0
+ Revision: 222406
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers
    - fix pcpa typo

  + Paulo Andrade <pcpa@mandriva.com.br>
    - Don't directly use files from /usr/X11R6, neither advertise them.
      Install Motif headers unders /usr/include/X11.

* Wed Feb 13 2008 Adam Williamson <awilliamson@mandriva.org> 0.95.0-2mdv2008.1
+ Revision: 166850
- don't run update_menus and clean_menus for mwm, it has no menu entry

* Fri Dec 21 2007 Olivier Blin <blino@mandriva.org> 0.95.0-1mdv2008.1
+ Revision: 136535
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - buildrequires X11-devel instead of XFree86-devel

  + Pixel <pixel@mandriva.com>
    - add various explicit conflicts with openmotif and its subpackages

* Wed Jul 18 2007 Adam Williamson <awilliamson@mandriva.org> 0.95.0-1mdv2008.0
+ Revision: 53167
- correct paths for x86-64
- fd.o icons
- drop old menu entry
- drop old patch3 (merged upstream)
- rediff patches 1 and 2
- improve description
- new patch3: disable libDtPrint (useless)
- drop 1.x compatible build (as per upstream)
- new release 0.95.0


* Tue Aug 29 2006 Thierry Vignaud <tvignaud@mandriva.com> 0.93.94-12mdv2007.0
- lesstif doesn't need %%post/%%postun ldconfig, but the %%libname1 and
  %%libname2 packages sure do (vdanen)
- use --enable-production: security fix for CVE-2006-4124 (stew)

* Mon Jul 17 2006 Frederic Crozat <fcrozat@mandriva.com> 0.93.94-11mdv2007.0
- Final switch to XDG menu

* Fri Jul 14 2006 Olivier Thauvin <nanardon@mandriva.org> 0.93.94-10mdv2007.0
- fix path for lib64

* Sun Jun 25 2006 Götz Waschk <waschk@mandriva.org> 0.93.94-9mdv2007.0
- fix buildrequires

* Sat Jun 24 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 0.93.94-8
- add BuildRequires: x11-util-cf-files

* Sun Jun 11 2006 Olivier Thauvin <nanardon@mandriva.org> 0.93.94-7mdv2007.0
- fix prefix (aka /usr instead /usr/X11R6)
- %%mkrel

* Thu May 04 2006 Frederic Crozat <fcrozat@mandriva.com> 0.93.94-6mdk
- Update source1, patch0, we are Mandriva Linux now
- Add XDG menu script, patch0 will need to be update again 
  when old menu system is replaced by new XDG based scripts

* Sat Dec 31 2005 Mandriva Linux Team <http://www.mandrivaexpert.com/> 0.93.94-5mdk
- Rebuild

* Mon Mar 14 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.93.94-4mdk
- fix ordering of packages on upgrade (#14537)

* Thu Feb 24 2005 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 0.93.94-3mdk
- first round of 64-bit fixes

* Tue Feb 22 2005 Thierry Vignaud <tvignaud@mandrakesoft.com> 0.93.94-2mdk
- libification

* Mon Dec 01 2003 Götz Waschk <waschk@linux-mandrake.com> 0.93.94-1mdk
- bzip2 source1
- rediff patches
- new version

* Fri Nov 14 2003 Götz Waschk <waschk@linux-mandrake.com> 0.93.91-1mdk
- new version

