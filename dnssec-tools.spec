%define major 5
%define libname %mklibname dnssec-tools %{major}
%define develname %mklibname dnssec-tools -d

Summary:	A suite of tools for managing dnssec aware DNS usage
Name:		dnssec-tools
Version:	1.12.1
Release:	1
License:	BSD-like
Group:		Networking/Other
URL:		http://www.dnssec-tools.org/
Source0:	http://www.dnssec-tools.org/download/dnssec-tools-%{version}.tar.gz
Source1:	dnssec-tools-dnsval.conf
Patch0:		dnssec-tools-linux-conf-paths-1.2.patch
Patch2:		dnssec-tools-DESTDIR.diff
Patch3:		dnssec-tools-linkage_fix.diff
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
BuildRequires:	chrpath
BuildRequires:	bind
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%package -n	%{develname}
Summary:	C-based development libraries for dnssec aware tools
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel
Provides:	lib%{name}-devel
Obsoletes:	%{mklibname dnssec-tools -d 4}

%description -n	%{develname}
C-based libraries useful for developing dnssec aware tools.

%prep

%setup -q
#patch0 -p0
%patch2 -p0
%patch3 -p0

autoreconf -fi
pushd validator
autoreconf -fi
popd

# clean up CVS stuff
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

%build
export PATH=$PATH:%{_sbindir}

%configure2_5x \
    --with-validator-testcases-file=%{_datadir}/%{name}/validator-testcases \
    --with-perl-build-args="INSTALLDIRS=vendor" \
    --with-root-hints=%{_localstatedir}/lib/named/var/named/named.ca \
    --with-resolv-conf=%{_sysconfdir}/resolv.conf \
    --with-nsec3 \
    --with-dlv \
    --with-ipv6

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' validator/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' validator/libtool

make

%install
rm -rf %{buildroot}

%makeinstall_std

install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}/KEY-SAFE

install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/dnsval.conf
install -m0644 tools/etc/%{name}/blinkenlights.conf %{buildroot}%{_sysconfdir}/%{name}/blinkenlights.conf

# not needed and installed in two places
rm -f %{buildroot}%{perl_vendorlib}/TrustMan.pl

# nuke one rpath
chrpath -d %{buildroot}%{perl_vendorarch}/auto/Net/DNS/SEC/Validator/Validator.so

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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc COPYING ChangeLog INSTALL NEWS README tools/demos tools/linux/ifup-dyn-dns tools/logwatch
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/dnsval.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/%{name}/blinkenlights.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/blinkenlights
%{_bindir}/cleanarch
%{_bindir}/cleankrf
%{_bindir}/dnspktflow
%{_bindir}/donuts
%{_bindir}/donutsd
%{_bindir}/drawvalmap
%{_bindir}/dtck
%{_bindir}/dtconf
%{_bindir}/dtconfchk
%{_bindir}/dtdefs
%{_bindir}/dtinitconf
%{_bindir}/expchk
%{_bindir}/fixkrf
%{_bindir}/genkrf
%{_bindir}/getaddr
%{_bindir}/getdnskeys
%{_bindir}/getds
%{_bindir}/gethost
%{_bindir}/getname
%{_bindir}/getquery
%{_bindir}/getrrset
%{_bindir}/keyarch
%{_bindir}/krfcheck
%{_bindir}/libval_check_conf
%{_bindir}/lsdnssec
%{_bindir}/lskrf
%{_bindir}/lsroll
%{_bindir}/maketestzone
%{_bindir}/mapper
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
%{_bindir}/validate
%{_bindir}/zonesigner

%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/donuts
%dir %{_datadir}/%{name}/donuts/rules
%{_datadir}/%{name}/donuts/rules/*
%{_datadir}/%{name}/validator-testcases
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/KEY-SAFE
%dir /var/log/%{name}
%{_mandir}/man1/blinkenlights.1*
%{_mandir}/man1/cleanarch.1*
%{_mandir}/man1/cleankrf.1*
%{_mandir}/man1/dnspktflow.1*
%{_mandir}/man1/dnssec-tools.1.*
%{_mandir}/man1/donuts.1*
%{_mandir}/man1/donutsd.1*
%{_mandir}/man1/drawvalmap.1*
%{_mandir}/man1/dtck.1.*
%{_mandir}/man1/dtconf.1.*
%{_mandir}/man1/dtconfchk.1*
%{_mandir}/man1/dtdefs.1*
%{_mandir}/man1/dtinitconf.1*
%{_mandir}/man1/expchk.1*
%{_mandir}/man1/fixkrf.1*
%{_mandir}/man1/genkrf.1*
%{_mandir}/man1/getaddr.1*
%{_mandir}/man1/getdnskeys.1*
%{_mandir}/man1/getds.1*
%{_mandir}/man1/gethost.1*
%{_mandir}/man1/getname.1.*
%{_mandir}/man1/getquery.1.*
%{_mandir}/man1/getrrset.1.*
%{_mandir}/man1/keyarch.1*
%{_mandir}/man1/krfcheck.1*
%{_mandir}/man1/libval_check_conf.1.*
%{_mandir}/man1/lsdnssec.1*
%{_mandir}/man1/lskrf.1*
%{_mandir}/man1/lsroll.1*
%{_mandir}/man1/maketestzone.1*
%{_mandir}/man1/mapper.1*
%{_mandir}/man1/rollchk.1*
%{_mandir}/man1/rollctl.1*
%{_mandir}/man1/rollerd.1*
%{_mandir}/man1/rollinit.1*
%{_mandir}/man1/rolllog.1*
%{_mandir}/man1/rollrec-editor.1.*
%{_mandir}/man1/rollset.1*
%{_mandir}/man1/signset-editor.1*
%{_mandir}/man1/tachk.1*
%{_mandir}/man1/timetrans.1*
%{_mandir}/man1/trustman.1*
%{_mandir}/man1/validate.1*
%{_mandir}/man1/zonesigner.1*
%{_mandir}/man3/p_ac_status.3*
%{_mandir}/man3/p_val_status.3*

%files -n perl-%{name}
%defattr(-,root,root)
%{perl_vendorarch}/Net/addrinfo*
%{perl_vendorarch}/Net/DNS/SEC/*
%{perl_vendorarch}/auto/Net/DNS/SEC/Validator
%{perl_vendorarch}/auto/Net/addrinfo/
%{perl_vendorarch}/Net/DNS/ZoneFile/
%{perl_vendorlib}/Net/DNS/SEC/Tools/Donuts/
%{_mandir}/man3/Net::addrinfo.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::BootStrap.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::conf.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::defaults.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::dnssectools.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::Donuts::Rule.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::keyrec.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::QWPrimitives.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::rolllog.3pm.*
%{_mandir}/man3/Net::DNS::SEC::Tools::rollmgr.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::rollrec.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::timetrans.3pm*
%{_mandir}/man3/Net::DNS::SEC::Tools::tooloptions.3pm*
%{_mandir}/man3/Net::DNS::SEC::Validator.3pm*
%{_mandir}/man3/Net::DNS::ZoneFile::Fast.3pm*

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.%{major}*

%files -n %{develname}
%defattr(-,root,root)
%doc apps/*
%{_bindir}/libval-config
%dir %{_includedir}/validator
%{_includedir}/validator/*.h
%{_libdir}/*.a
%{_libdir}/*.so
%{_libdir}/*.la
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
%{_mandir}/man3/val_add_valpolicy.3*
%{_mandir}/man3/val_create_context.3*
%{_mandir}/man3/val_create_context_with_conf.3*
%{_mandir}/man3/val_does_not_exist.3*
%{_mandir}/man3/val_freeaddrinfo.3*
%{_mandir}/man3/val_free_answer_chain.3.*
%{_mandir}/man3/val_free_context.3*
%{_mandir}/man3/val_free_response.3*
%{_mandir}/man3/val_free_result_chain.3*
%{_mandir}/man3/val_getaddrinfo.3*
%{_mandir}/man3/val_gethostbyaddr.3*
%{_mandir}/man3/val_gethostbyaddr_r.3*
%{_mandir}/man3/val_gethostbyname2.3*
%{_mandir}/man3/val_gethostbyname2_r.3*
%{_mandir}/man3/val_gethostbyname.3*
%{_mandir}/man3/val_gethostbyname_r.3*
%{_mandir}/man3/val_getnameinfo.3*
%{_mandir}/man3/val_get_rrset.3.*
%{_mandir}/man3/val_istrusted.3*
%{_mandir}/man3/val_isvalidated.3*
%{_mandir}/man3/val_resolve_and_check.3*
%{_mandir}/man3/val_res_query.3*
%{_mandir}/man3/val_res_search.3*

