%define	major	14
%define	libname %mklibname dnssec-tools %{major}
%define	devname	%mklibname dnssec-tools -d

Summary:	A suite of tools for managing dnssec aware DNS usage



Name:		dnssec-tools
Version:	2.0
Release:	1
License:	BSD-like
Group:		Networking/Other
URL:		http://www.dnssec-tools.org/
Source0:	http://www.dnssec-tools.org/download/dnssec-tools-%{version}.tar.gz
Source1:	dnssec-tools-dnsval.conf
Source2:	libval-config
Patch1:		dnssec-tools-linux-conf-paths-1.13.patch
Patch2:		dnssec-tools-zonefile-fast-nsec3-1.20.patch
Patch3:		dnssec-tools-zonefile-fast-misc.patch
Requires:	bind
Requires:	perl-Net-DNS
Requires:	perl-%{name} >= %{version}
Requires:	perl(Tk)
Requires:	perl(Tk::Dialog)
Requires:	perl(Tk::Pane)
Requires:	perl(Tk::Table)
BuildRequires:	perl-devel
BuildRequires:	openssl-devel
BuildRequires:	autoconf2.5
BuildRequires:	libtool
BuildRequires:	bind

%description
The goal of the DNSSEC-Tools project is to create a set of tools, patches,
applications, wrappers, extensions, and plugins that will help ease the
deployment of DNSSEC-related technologies.

%package -n	perl-%{name}
Summary:	Perl modules supporting DNSSEC (needed by the dnssec-tools)



Group:		Development/Perl

%description -n	perl-%{name}
The dnssec-tools project comes with a number of perl modules that are required
by the DNSSEC tools themselves as well as modules that are useful for other
developers.

%package -n	%{libname}
Summary:	C-based libraries for dnssec aware tools



Group:		System/Libraries
Requires:	openssl

%description -n	%{libname}
C-based libraries useful for developing dnssec aware tools.

%package -n	%{devname}
Summary:	C-based development libraries for dnssec aware tools



Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Obsoletes:	%{mklibname dnssec-tools -d 4}

%description -n	%{devname}
C-based libraries useful for developing dnssec aware tools.

%prep
%setup -q
%patch1 -p0
%patch2 -p2
%patch3 -p2

find -name \*.orig -o -name .gitignore|xargs rm -f

autoreconf -fi
pushd validator
autoreconf -fi
popd

%build
%configure2_5x \
        --with-validator-testcases-file=%{_datadir}/dnssec-tools/validator-testcases \
        --with-perl-build-args="INSTALLDIRS=vendor OPTIMIZE='%{optflags}'" \
        --sysconfdir=/etc \
        --with-root-hints=/etc/dnssec-tools/root.hints \
        --with-resolv-conf=/etc/dnssec-tools/resolv.conf \
        --disable-static \
        --with-nsec3 \
        --with-ipv6 \
        --with-dlv \
	--disable-bind-checks

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' validator/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' validator/libtool

%make

%install
%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}/KEY-SAFE

install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/dnsval.conf
install -m0644 tools/etc/%{name}/blinkenlights.conf %{buildroot}%{_sysconfdir}/%{name}/blinkenlights.conf

# not needed and installed in two places
rm -f %{buildroot}%{perl_vendorlib}/TrustMan.pl

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/%{name} << EOF
/var/log/%{name}/rollerd.log {
    rotate 5
    monthly
    missingok
    notifempty
    nocompress
}
EOF

# Move the architecture dependent config file to its own place
# (this allows multiple architecture rpms to be installed at the same time)
mv %{buildroot}/%{_bindir}/libval-config %{buildroot}/%{_bindir}/libval-config-%{_arch}
# Add a new wrapper script that calls the right file at run time
install -m 755 %{SOURCE2} %{buildroot}/%{_bindir}/libval-config

%files
%doc COPYING ChangeLog NEWS README tools/demos tools/linux/ifup-dyn-dns tools/logwatch
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/dnsval.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/blinkenlights.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/blinkenlights
%{_bindir}/bubbles
%{_bindir}/buildrealms
%{_bindir}/check-zone-expiration
%{_bindir}/cleanarch
%{_bindir}/cleankrf
%{_bindir}/convertar
%{_bindir}/dnspktflow
%{_bindir}/donuts
%{_bindir}/donutsd
%{_bindir}/drawvalmap
%{_bindir}/dt-danechk
%{_bindir}/dt-getaddr
%{_bindir}/dt-gethost
%{_bindir}/dt-getname
%{_bindir}/dt-getquery
%{_bindir}/dt-getrrset
%{_bindir}/dtck
%{_bindir}/dtconf
%{_bindir}/dtconfchk
%{_bindir}/dtdefs
%{_bindir}/dtinitconf
%{_bindir}/dtrealms
%{_bindir}/expchk
%{_bindir}/fixkrf
%{_bindir}/genkrf
%{_bindir}/getdnskeys
%{_bindir}/getds
%{_bindir}/grandvizier
%{_bindir}/keyarch
%{_bindir}/keymod
%{_bindir}/krfcheck
%{_bindir}/libval_check_conf
%{_bindir}/lights
%{_bindir}/lsdnssec
%{_bindir}/lskrf
%{_bindir}/lsrealm
%{_bindir}/lsroll
%{_bindir}/maketestzone
%{_bindir}/mapper
%{_bindir}/realmchk
%{_bindir}/realmctl
%{_bindir}/realminit
%{_bindir}/realmset
%{_bindir}/rollchk
%{_bindir}/rollctl
%{_bindir}/rollerd
%{_bindir}/rollinit
%{_bindir}/rolllog
%{_bindir}/rollrec-editor
%{_bindir}/rollset
%{_bindir}/signset-editor
%{_bindir}/tachk
%{_bindir}/timetrans
%{_bindir}/trustman
%{_bindir}/dt-validate
%{_bindir}/zonesigner

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/donuts
%dir %{_datadir}/%{name}/donuts/rules
%{_datadir}/%{name}/donuts/rules/*
%{_datadir}/%{name}/validator-testcases
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/KEY-SAFE
%dir /var/log/%{name}
%{_mandir}/man1/*
%{_mandir}/man3/p_ac_status.3*
%{_mandir}/man3/p_val_status.3*

%files -n perl-%{name}
%{perl_vendorarch}/Net/addrinfo*
%{perl_vendorarch}/Net/DNS/SEC/*
%{perl_vendorarch}/auto/Net/DNS/SEC/Validator
%{perl_vendorarch}/auto/Net/addrinfo/
%{perl_vendorarch}/Net/DNS/ZoneFile/
%{perl_vendorlib}/Net/DNS/SEC/Tools/Donuts/
%{perl_vendorlib}/Net/DNS/SEC/Tools/TrustAnchor*
%{_mandir}/man3/Net::*

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files -n %{devname}
%doc apps/*
%{_bindir}/libval-config*
%dir %{_includedir}/validator
%{_includedir}/validator/*.h
%{_libdir}/*.so
%{_mandir}/man3/dnsval.conf.3*
%{_mandir}/man3/dnsval_conf_get.3*
%{_mandir}/man3/dnsval_conf_set.3*
%{_mandir}/man3/libsres.3*
%{_mandir}/man3/libval.3*
%{_mandir}/man3/libval_shim.3.*
%{_mandir}/man3/resolv_conf_get.3*
%{_mandir}/man3/resolv_conf_set.3*
%{_mandir}/man3/root_hints_get.3*
%{_mandir}/man3/root_hints_set.3*
%{_mandir}/man3/val_*

