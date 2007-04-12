%define _lesstifdir	%_prefix/LessTif 
%define _iconsdir	/usr/share/icons

%define libname1 %mklibname lesstif 1
%define libname2 %mklibname lesstif 2

Summary:	A free Motif clone
Name:		lesstif
Version:	0.93.94
Release:	%mkrel 12
License:	LGPL
URL:		http://www.lesstif.org/
Group:		System/Libraries
Source:		ftp://ftp.hungry.com/pub/hungry/lesstif/srcdist/%name-%version.tar.bz2
#Fast mirror: ftp://linux.mathematik.tu-darmstadt.de:/pub/linux/mirrors/misc/lesstif/srcdist/
Source2:	mwm.png.bz2
Source3:	mwm32.png.bz2
Source4:	lesstif-mwm-menu-xdg
Patch0:		lesstif-mdk-menu.patch
Patch1:		lesstif-0.93.94-libdir.patch
Patch2:		lesstif-0.93.94-libtool.patch
Patch3:		lesstif-0.93.94-64bit-fixes.patch

BuildRoot:	%{_tmppath}/%name-%version-root
BuildRequires:	flex, XFree86-devel, bison, xpm-devel
BuildRequires:	imake
BuildRequires:  autoconf2.5

%description
Lesstif is an API compatible clone of the Motif toolkit.

Most of the Motif 1.2 API is in place.
Motif 2.1 functionality is being improved.

Many Motif applications compile and run out-of-the-box with LessTif,
and we want to hear about those that don't.

%package -n %libname1
Summary:    Lesstif Libraries (Motif-1.x compatible)
Group:      System/Libraries
Requires:	lesstif = %version
Conflicts:  lesstif < 0.93.94-2mdk

%description -n %libname1
Lesstif is an API compatible clone of the Motif toolkit.
This is the Motif 1.2 compatible version of Lesstif.


%package -n %libname2
Summary:    Lesstif Libraries (Motif-2.x compatible)
Group:      System/Libraries
Requires:	lesstif = %version
Conflicts:  lesstif < 0.93.94-2mdk

%description -n %libname2
Lesstif is an API compatible clone of the Motif toolkit.
This is the Motif 2.1 compatible version of Lesstif.


%package mwm
Summary:	Lesstif Motif window manager clone based on fvwm
Group:		Graphical desktop/Other
Requires:	desktop-common-data

%description mwm
MWM is a window manager that adheres largely
to the Motif mwm specification.


%package clients
Summary:	Lesstif clients
Group:		Graphical desktop/Other
Requires:	lesstif = %version

%description clients
Uil and xmbind.


%package devel
Group:		Development/C
Summary:	Static library and header files for Lesstif/Motif development
Requires:	%libname1 = %version, %libname2 = %version

%description devel
This package contains the lesstif static library and header files
required to develop motif-based applications.

This package also contains development documentation in html (Lessdox),
and mxmkmf for Lesstif.

%prep
%setup -q -n lesstif-%{version}
%patch0 -p0 -b .mdk
%patch1 -p1 -b .libdir
%patch2 -p1 -b .libtool
%patch3 -p1 -b .64bit-fixes
autoconf
LESSTIFTOP=$PWD

%build
CFLAGS="$RPM_OPT_FLAGS" ./configure \
				--prefix=%{_prefix} \
				--libdir=%{_libdir} \
                --mandir=%{buildroot}%{_mandir} \
				--enable-shared \
				--enable-static \
				--enable-build-12 \
				--enable-build-20 \
				--enable-build-21 \
				--disable-maintainer-mode \
				--enable-default-21 \
				--disable-debug \
				--enable-production


%make

%install
rm -rf $RPM_BUILD_ROOT

make install prefix=$RPM_BUILD_ROOT%{_prefix} libdir=$RPM_BUILD_ROOT%{_libdir} mandir=%{buildroot}%{_mandir}
install -d $RPM_BUILD_ROOT/etc/X11
ln -sf ../..%{_prefix}/lib/X11/mwm $RPM_BUILD_ROOT/etc/X11/mwm

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
' < %{_libdir}/X11/config/Imake.tmpl > Imake-lesstif.tmpl



cd $RPM_BUILD_ROOT%{_prefix}/bin/
sed -e 's/imake $args/imake -T Imake-lesstif.tmpl $args/' < `which xmkmf` > mxmkmf

# cleanup in a preparation for an installation - unify layout
#mkdir -p $RPM_BUILD_ROOT/%_prefix/man{1,5}
#pushd $RPM_BUILD_ROOT%_lesstifdir
#	mkdir ../man/man{1,5}
#	mv doc/man/man1/* ../man/man1/
#	mv doc/man/man3/* ../man/man3/
#	mv doc/man/man5/* ../man/man5/
#	rmdir doc/man{/*,}
#popd

# menu support
mv $RPM_BUILD_ROOT%{_prefix}/lib/X11/mwm/system.mwmrc $RPM_BUILD_ROOT%{_prefix}/lib/X11/mwm/system.mwmrc-menu
mkdir -p $RPM_BUILD_ROOT%_menudir $RPM_BUILD_ROOT%_sysconfdir/menu.d
cat > $RPM_BUILD_ROOT%_menudir/%{name}-mwm << EOF
?package(%{name}-mwm): needs=wm icon=mwm.png section=Session/Windowmanagers title=Mwm command=mwm \
longtitle="A free Motif clone" \
xdg="true"
EOF
install -m 0755 %{SOURCE4} $RPM_BUILD_ROOT%_sysconfdir/menu.d/lesstif-mwm

#mdk icons
install -d $RPM_BUILD_ROOT%{_iconsdir}/mini
bzcat %{SOURCE2} >$RPM_BUILD_ROOT%{_iconsdir}/mini/mwm.png
bzcat %{SOURCE3} >$RPM_BUILD_ROOT%{_iconsdir}/mwm.png
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/X11/config/host.def

rm -f $RPM_BUILD_ROOT%{_prefix}/%{_lib}/*.so.2.0.0

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_lesstifdir}/[ABCFIR]*
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/app-defaults/Mwm
rm -f $RPM_BUILD_ROOT%{_prefix}/lib/mwm/*

%post -n %libname1 -p /sbin/ldconfig
%postun -n %libname1 -p /sbin/ldconfig

%post -n %libname2 -p /sbin/ldconfig
%postun -n %libname2 -p /sbin/ldconfig

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

%files -n %libname1
%defattr(-,root,root,-)
%{_libdir}/*.so.1*

%files -n %libname2
%defattr(-,root,root,-)
%{_libdir}/*.so.2*

%files mwm
%defattr(-,root,root,-)
%doc clients/Motif-1.2/mwm/{COPYING,README}
%config(noreplace) %_sysconfdir/X11/mwm
%{_sysconfdir}/menu.d/%{name}-mwm
%{_prefix}/lib/X11/mwm
%{_prefix}/lib/X11/app-defaults/Mwm
%{_mandir}/man1/mwm.1*
%{_mandir}/man5/mwmrc.5*
%{_bindir}/mwm
%{_menudir}/%{name}-mwm
%{_iconsdir}/mwm.png
%{_iconsdir}/mini/mwm.png

%files clients
%defattr(-,root,root,-)
%doc doc/UIL.txt
%{_bindir}/uil
%{_bindir}/xmbind
%{_mandir}/man1/xmbind.1*

%files devel
%defattr(-,root,root,755)
#%doc doc/{*.html,*.txt,lessdox/*/*.html,www.lesstif.org}
%doc %{_lesstifdir}/doc
%{_includedir}/*
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/*.so
%{_bindir}/mxmkmf
%{_prefix}/lib/X11/config/*
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_mandir}/man5/*

