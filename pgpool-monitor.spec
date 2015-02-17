%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define module_name pgpool_monitor

Name:           %{module_name}
Version:        0.1.0
Release:        1
Summary:        Send pgpool status to Zabbix

License:        Rackspace Internal
URL:            https://github.rackspace.com/cloud-integration-ops/pgpool-monitor
Source0:        %{module_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-setuptools
Requires:       python-setuptools python-psycopg2

%description
This monitor checks the status of pgpool's ability to execute read and write
queries against the backend it is configured for.  It also has options for
checking the status of nodes and it will attempt to reattach a node if it
is down at the time of an active node count.

%prep
%setup -q -n %{module_name}-%{version}


%build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT

%files
%doc README.md
%{python_sitelib}/*
%attr(0755,-,-) %{_bindir}/%{name}
%config(noreplace) %attr(0640,-,-) %{_sysconfdir}/%{name}.cfg


%changelog
* Tue Feb 17 2015 Alex Schultz <alex.schultz@rackspace.com> - 0.1.0-1
- Initial version of the package
