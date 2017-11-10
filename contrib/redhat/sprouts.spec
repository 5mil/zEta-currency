Name:           sprouts
Version:        0.6.3
Release:        1%{?dist}
Summary:        Sprouts Wallet
Group:          Applications/Internet
Vendor:         Sprouts
License:        GPLv3
URL:            https://nur1labs.net
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  autoconf automake libtool gcc-c++ openssl-devel >= 1:1.0.2d libdb4-devel libdb4-cxx-devel miniupnpc-devel boost-devel boost-static
Requires:       openssl >= 1:1.0.2d libdb4 libdb4-cxx miniupnpc logrotate

%description
Sprouts Wallet

%prep
%setup -q

%build
./autogen.sh
./configure
make

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir} -p $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT/etc/sprouts $RPM_BUILD_ROOT/etc/ssl/snc $RPM_BUILD_ROOT/var/lib/snc/.sprouts $RPM_BUILD_ROOT/usr/lib/systemd/system $RPM_BUILD_ROOT/etc/logrotate.d
%{__install} -m 755 src/sprtsd $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 755 src/sprts-cli $RPM_BUILD_ROOT%{_bindir}
%{__install} -m 600 contrib/redhat/sprouts.conf $RPM_BUILD_ROOT/var/lib/snc/.sprouts
%{__install} -m 644 contrib/redhat/sprtsd.service $RPM_BUILD_ROOT/usr/lib/systemd/system
%{__install} -m 644 contrib/redhat/sprtsd.logrotate $RPM_BUILD_ROOT/etc/logrotate.d/sprtsd
%{__mv} -f contrib/redhat/snc $RPM_BUILD_ROOT%{_bindir}

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%pretrans
getent passwd snc >/dev/null && { [ -f /usr/bin/sprtsd ] || { echo "Looks like user 'snc' already exists and have to be deleted before continue."; exit 1; }; } || useradd -r -M -d /var/lib/snc -s /bin/false snc

%post
[ $1 == 1 ] && {
  sed -i -e "s/\(^rpcpassword=MySuperPassword\)\(.*\)/rpcpassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)/" /var/lib/snc/.sprouts/sprouts.conf
  openssl req -nodes -x509 -newkey rsa:4096 -keyout /etc/ssl/snc/sprouts.key -out /etc/ssl/snc/sprouts.crt -days 3560 -subj /C=US/ST=Oregon/L=Portland/O=IT/CN=sprouts.snc
  ln -sf /var/lib/snc/.sprouts/sprouts.conf /etc/sprouts/sprouts.conf
  ln -sf /etc/ssl/snc /etc/sprouts/certs
  chown snc.snc /etc/ssl/snc/sprouts.key /etc/ssl/snc/sprouts.crt
  chmod 600 /etc/ssl/snc/sprouts.key
} || exit 0

%posttrans
[ -f /var/lib/snc/.sprouts/addr.dat ] && { cd /var/lib/snc/.sprouts && rm -rf database addr.dat nameindex* blk* *.log .lock; }
sed -i -e 's|rpcallowip=\*|rpcallowip=0.0.0.0/0|' /var/lib/snc/.sprouts/sprouts.conf
systsnctl daemon-reload
systsnctl status sprtsd >/dev/null && systsnctl restart sprtsd || exit 0

%preun
[ $1 == 0 ] && {
  systsnctl is-enabled sprtsd >/dev/null && systsnctl disable sprtsd >/dev/null || true
  systsnctl status sprtsd >/dev/null && systsnctl stop sprtsd >/dev/null || true
  pkill -9 -u snc > /dev/null 2>&1
  getent passwd snc >/dev/null && userdel snc >/dev/null 2>&1 || true
  rm -f /etc/ssl/snc/sprouts.key /etc/ssl/snc/sprouts.crt /etc/sprouts/sprouts.conf /etc/sprouts/certs
} || exit 0

%files
%doc COPYING
%attr(750,snc,snc) %dir /etc/sprouts
%attr(750,snc,snc) %dir /etc/ssl/snc
%attr(700,snc,snc) %dir /var/lib/snc
%attr(700,snc,snc) %dir /var/lib/snc/.sprouts
%attr(600,snc,snc) %config(noreplace) /var/lib/snc/.sprouts/sprouts.conf
%attr(4750,snc,snc) %{_bindir}/sprouts-cli
%defattr(-,root,root)
%config(noreplace) /etc/logrotate.d/sprtsd
%{_bindir}/sprtsd
%{_bindir}/snc
/usr/lib/systemd/system/sprtsd.service

%changelog
* Thu Aug 31 2017 Aspanta Limited <info@aspanta.com> 0.6.3
- There is no changelog available. Please refer to the CHANGELOG file or visit the website.
