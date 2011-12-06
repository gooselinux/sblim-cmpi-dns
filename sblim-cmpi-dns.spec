%define tog_pegasus_version 2:2.5.1
%define provider_dir %{_libdir}/cmpi/

Name:           sblim-cmpi-dns
Version:        1.0
Release:        1%{?dist}
Summary:        SBLIM WBEM-SMT Dns

Group:          Applications/System
License:        EPL
URL:            http://sblim.wiki.sourceforge.net/
Source0:        http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0:         sblim-cmpi-dns-0.5.2-include.patch

#BuildRequires:  sed
BuildRequires:  flex bison
BuildRequires:  sblim-tools-libra-devel
BuildRequires:  tog-pegasus-devel >= %{tog_pegasus_version}
BuildRequires:  sblim-cmpi-devel
Requires:       sblim-tools-libra
Requires:       bind
Requires:       /etc/ld.so.conf.d
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Provides:       cmpi-dns = %{version}
Requires:       tog-pegasus >= %{tog_pegasus_version}

%description
The cmpi-dns package provides access to the dns configuration data
via CIMOM technology/infrastructure.
It contains the Dns CIM Model, CMPI Provider with the Samba task specific
Resource Access.

%package devel
Summary:        SBLIM WBEM-SMT Dns - Header Development Files
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       tog-pegasus >= %{tog_pegasus_version}

%description devel
SBLIM WBEM-SMT Dns Development Package contains header files and
link libraries for dependent provider packages

%package test
Summary:        SBLIM WBEM-SMT Dns - Testcase Files
Group:          Applications/System
Requires:       %{name} = %{version}-%{release}
Requires:       sblim-testsuite
Requires:       tog-pegasus >= %{tog_pegasus_version}

%description test
SBLIM WBEM-SMT DNS Provider Testcase Files for the SBLIM Testsuite

%prep
%setup -q
%patch0 -p1 -b .include

%build
%ifarch s390 s390x ppc ppc64
export CFLAGS="$RPM_OPT_FLAGS -fsigned-char"
%else
export CFLAGS="$RPM_OPT_FLAGS" 
%endif
%configure \
   TESTSUITEDIR=%{_datadir}/sblim-testsuite \
   CIMSERVER=pegasus \
   PROVIDERDIR=%{provider_dir}
# try to remove RPATH from libtool generated libraries
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
# remove unused libtool files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*a
rm -f $RPM_BUILD_ROOT/%{_libdir}/cmpi/*a
# shared libraries
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d
echo "%{_libdir}/cmpi" > $RPM_BUILD_ROOT/%{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf
sed -i -e '1d;2i#!/usr/bin/awk -f' $RPM_BUILD_ROOT/%{_datadir}/%{name}/smt_dns_ra_lines.awk

%files
%defattr(-,root,root,0755)
%doc %{_datadir}/doc/%{name}-%{version}
%doc %{_mandir}/man5/smt_dns_ra_support.conf.5.gz
%{_datadir}/%{name}
%{_libdir}/libRaToolsDns.so.*
%{_libdir}/libIBM_DnsProviderTooling.so.*
%{_libdir}/libLinux_DnsGeneralProviderBasic.so.*
%config(noreplace) %{_sysconfdir}/smt_dns*.conf
%{_libdir}/cmpi/libcmpiLinux_Dns*.so
%{_libdir}/cmpi/libcmpiDnsCIM_ConcreteJob.so
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/%{name}-%{_arch}.conf

%files devel
%defattr(-,root,root,0755)
%{_includedir}/sblim/smt_dns*.h
%{_libdir}/libRaToolsDns.so
%{_libdir}/libIBM_DnsProviderTooling.so
%{_libdir}/libLinux_DnsGeneralProviderBasic.so

%files test
%defattr(-,root,root,0755)
%{_datadir}/sblim-testsuite/elephant.example2.com.conf
%{_datadir}/sblim-testsuite/buffalo.example2.com.conf
%{_datadir}/sblim-testsuite/named.conf
%{_datadir}/sblim-testsuite/testlocaldomain.zone
%{_datadir}/sblim-testsuite/testnamed.local
%{_datadir}/sblim-testsuite/testnamed.ca
%{_datadir}/sblim-testsuite/testlocalhost.zone
%{_datadir}/sblim-testsuite/testnamed.ip6.local
%{_datadir}/sblim-testsuite/testnamed.zero
%{_datadir}/sblim-testsuite/test-cmpi-dns.sh
%{_datadir}/sblim-testsuite/testnamed.broadcast
%{_datadir}/sblim-testsuite/cobra.example1.com.conf
%{_datadir}/sblim-testsuite/rhino.example1.com.conf
%{_datadir}/sblim-testsuite/system/linux/Linux_Dns*
%{_datadir}/sblim-testsuite/cim/Linux_Dns*

# Conditional definition of schema and registration files
%define DNS_SCHEMA %{_datadir}/%{name}/Linux_Dns.mof
%define DNS_REGISTRATION %{_datadir}/%{name}/Linux_Dns.registration

%pre
# If upgrading, deregister old version
if [ $1 -gt 1 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{DNS_REGISTRATION} -m %{DNS_SCHEMA} > /dev/null 2>&1 || :;
fi

%post
/sbin/ldconfig
if [ $1 -ge 1 ]; then
  # Register Schema and Provider - this is higly provider specific
  %{_datadir}/%{name}/provider-register.sh \
  -t pegasus -r %{DNS_REGISTRATION} -m %{DNS_SCHEMA} > /dev/null 2>&1 || :;
fi;

%preun
# Deregister only if not upgrading 
if [ $1 -eq 0 ]; then
  %{_datadir}/%{name}/provider-register.sh -d \
  -t pegasus -r %{DNS_REGISTRATION} -m %{DNS_SCHEMA} > /dev/null 2>&1 || :;
fi

%postun
# Run ldconfig only if not upgrading
if [ $1 -eq 0 ]; then
  /sbin/ldconfig
fi

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Jun 30 2010 Vitezslav Crhonek <vcrhonek@redhat.com> - 1.0-1
- Update to sblim-cmpi-dns-1.0

* Thu Oct 22 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.5.2-2
- Fix "include" patch

* Thu Oct 15 2009 Vitezslav Crhonek <vcrhonek@redhat.com> - 0.5.2-1
- Initial support
