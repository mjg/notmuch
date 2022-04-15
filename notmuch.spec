## Pull in upstream source:
# {{{ git submodule update --init 1>&2; git submodule }}}
%global gitversion      {{{ git -C source rev-parse HEAD }}}
%global gitshortversion {{{ git -C source rev-parse --short HEAD }}}
%global gitdescribefedversion	{{{ git -C source describe --tags --match '[0-9]*' | sed -e 's/^\(.*\)-\([0-9]*\)-g\(.*\)$/\1^\2.g\3/' }}}
%if 0%{?fedora} || 0%{?rhel} >= 8
%bcond_without tests
%else
%bcond_with tests
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
%global with_python3legacy 1
%global with_python3CFFI 1
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
%global with_python2 1
%endif

# build python 3 modules with python 3 ;)
%if 0%{?with_python3legacy} || 0%{?with_python3CFFI}
%global with_python3 1
%endif

Name:           notmuch
Version:        %{gitdescribefedversion}
Release:        1%{?dist}
Summary:        System for indexing, searching, and tagging email
License:        GPLv3+
URL:            https://notmuchmail.org/
# rpkg's git_pack does not cope well with submodules, so we force it to assume a dirty tree.
# The tree is unmodified (before possibly applying patches).
Source:         {{{ GIT_DIRTY=1 git_pack path=source dir_name=notmuch }}}
Patch1:		0001-test-allow-to-use-full-sync.patch
Patch2:		0001-fix-build-without-sfsexp.patch

BuildRequires:  make
BuildRequires:  bash-completion
BuildRequires:  emacs
BuildRequires:  emacs-el
BuildRequires:  emacs-nox
Buildrequires:  gcc gcc-c++
BuildRequires:  libtool
BuildRequires:  doxygen
BuildRequires:  texinfo
BuildRequires:  gnupg2
BuildRequires:  gnupg2-smime
BuildRequires:  gmime30-devel
BuildRequires:  libtalloc-devel
BuildRequires:  perl-interpreter
BuildRequires:  perl-generators
BuildRequires:  perl-podlators
%if 0%{?with_python2}
BuildRequires:  python2-devel
BuildRequires:  python2-docutils
BuildRequires:  python2-sphinx
%endif
BuildRequires:  ruby-devel
BuildRequires:  xapian-core-devel
BuildRequires:  zlib-devel

%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-docutils
BuildRequires:  python3-sphinx
%endif

%if 0%{?with_python3CFFI}
BuildRequires:  python3-setuptools
  %if %{with tests}
BuildRequires:  python3-pytest
# Not available on *EL, skip some tests there:
    %if 0%{?fedora}
BuildRequires:  python3-pytest-shutil
    %endif
  %endif
BuildRequires:  python3-cffi
%endif

%if %{with tests}
# Not available on *EL, skip some tests there:
  %if 0%{?fedora}
BuildRequires:  dtach
  %endif
BuildRequires:  gdb
BuildRequires:  man
BuildRequires:  openssl
# You might also want to rebuild with valgrind-devel libasan libasan-static.
%endif

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description
Fast system for indexing, searching, and tagging email.  Even if you
receive 12000 messages per month or have on the order of millions of
messages that you've been saving for decades, Notmuch will be able to
quickly search all of it.

Notmuch is not much of an email program. It doesn't receive messages
(no POP or IMAP support). It doesn't send messages (no mail composer,
no network code at all). And for what it does do (email search) that
work is provided by an external library, Xapian. So if Notmuch
provides no user interface and Xapian does all the heavy lifting, then
what's left here? Not much.

%package    devel
Summary:    Development libraries and header files for the Notmuch library
Requires:   %{name} = %{version}-%{release}

%description devel
Notmuch-devel contains the development libraries and header files for
Notmuch email program.  These libraries and header files are
necessary if you plan to do development using Notmuch.

Install notmuch-devel if you are developing C programs which will use the
Notmuch library.  You'll also need to install the notmuch package.

%package -n emacs-notmuch
Summary:    Not much support for Emacs
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   emacs(bin) >= %{_emacs_version}

%description -n emacs-notmuch
%{summary}.

%if 0%{?with_python2}
%package -n python2-notmuch
Summary:    Python2 bindings for notmuch
%{?python_provide:%python_provide python2-notmuch}

Requires:       python2

%description -n python2-notmuch
%{summary}.
%endif

%if 0%{?with_python3legacy}
%package -n python3-notmuch
Summary:    Python3 bindings for notmuch (legacy)
%{?python_provide:%python_provide python3-notmuch}

Requires:       python3

%description -n python3-notmuch
%{summary}.
%endif

%if 0%{?with_python3CFFI}
%package -n python3-notmuch2
Summary:    Python3 bindings for notmuch (cffi)
%{?python_provide:%python_provide python3-notmuch2}

Requires:       python3

%description -n python3-notmuch2
%{summary}.
%endif

%package -n ruby-notmuch
Summary:    Ruby bindings for notmuch
Requires:   %{name} = %{version}-%{release}

%description -n ruby-notmuch
%{summary}.

%package    mutt
Summary:    Notmuch (of a) helper for Mutt
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   perl(Term::ReadLine::Gnu)

%description mutt
notmuch-mutt provide integration among the Mutt mail user agent and
the Notmuch mail indexer.

%package    vim
Summary:    A Vim plugin for notmuch
Requires:   ruby-%{name} = %{version}-%{release}
Requires:   rubygem-mail
Requires:   vim-enhanced
# Required for updating helptags in scriptlets.
Requires(post):    vim-enhanced
Requires(postun):  vim-enhanced

%description vim
notmuch-vim is a Vim plugin that provides a fully usable mail client
interface, utilizing the notmuch framework.

%prep
%autosetup -n notmuch -p1

%build
# DEBUG mtime/stat
%configure --emacslispdir=%{_emacs_sitelispdir}
%make_build CFLAGS="$RPM_OPT_FLAGS -fPIC"

# Build the python bindings
pushd bindings/python
    %if 0%{?with_python2}
    %py2_build
    %endif
    %if 0%{?with_python3}
    %py3_build
    %endif
popd

# Build the python cffi bindings
pushd bindings/python-cffi
    %if 0%{?with_python3CFFI}
    %py3_build
    %endif
popd

# Build notmuch-mutt
pushd contrib/notmuch-mutt
    make
popd

%if %{with tests}
%check
# armv7hl pulls in libasan but we build without, and should test without it.
# At least some rhel builds show mtime/stat related Heisenbugs when
# notmuch new takes shortcuts, so enforce --full-scan there.
NOTMUCH_SKIP_TESTS="asan" make test V=1 %{?rhel:NOTMUCH_TEST_FULLSCAN=1}
%endif

%install
%make_install

# Enable dynamic library stripping.
find %{buildroot}%{_libdir} -name *.so* -exec chmod 755 {} \;

# Install the python bindings and documentation
pushd bindings/python
    %if 0%{?with_python2}
    %py2_install
    %endif
    %if 0%{?with_python3legacy}
    %py3_install
    %endif
popd

# Install the python cffi bindings and documentation
pushd bindings/python-cffi
    %if 0%{?with_python3CFFI}
    %py3_install
    %endif
popd

# Install the ruby bindings
pushd bindings/ruby
    make install DESTDIR=%{buildroot}
popd

# Install notmuch-mutt
install -m0755 contrib/notmuch-mutt/notmuch-mutt \
    %{buildroot}%{_bindir}/notmuch-mutt
install -m0644 contrib/notmuch-mutt/notmuch-mutt.1 \
    %{buildroot}%{_mandir}/man1/notmuch-mutt.1

# Install notmuch-vim
pushd vim
    make install DESTDIR=%{buildroot} prefix="%{_datadir}/vim/vimfiles"
popd

rm -f %{buildroot}/%{_datadir}/applications/mimeinfo.cache
rm -f %{buildroot}%{_infodir}/dir

%post vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%postun vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%files
%doc AUTHORS COPYING COPYING-GPL-3 README
%{_datadir}/zsh/site-functions/_notmuch
%{_datadir}/zsh/site-functions/_email-notmuch
%{_datadir}/bash-completion/completions/notmuch
%{_bindir}/notmuch
%{_mandir}/man1/notmuch.1*
%{_mandir}/man1/notmuch-address.1*
%{_mandir}/man1/notmuch-config.1*
%{_mandir}/man1/notmuch-count.1*
%{_mandir}/man1/notmuch-dump.1*
%{_mandir}/man1/notmuch-insert.1*
%{_mandir}/man1/notmuch-new.1*
%{_mandir}/man1/notmuch-reindex.1*
%{_mandir}/man1/notmuch-reply.1*
%{_mandir}/man1/notmuch-restore.1*
%{_mandir}/man1/notmuch-search.1*
%{_mandir}/man1/notmuch-setup.1*
%{_mandir}/man1/notmuch-show.1*
%{_mandir}/man1/notmuch-tag.1*
%{_mandir}/man1/notmuch-compact.1*
%{_mandir}/man5/notmuch*.5*
%{_mandir}/man7/notmuch*.7*
%{_infodir}/*.info*
%{_libdir}/libnotmuch.so.5*

%files devel
%{_libdir}/libnotmuch.so
%{_includedir}/*
%{_mandir}/man3/notmuch*.3*

%files -n emacs-notmuch
%{_emacs_sitelispdir}/*.el
%{_emacs_sitelispdir}/*.elc
%{_emacs_sitelispdir}/notmuch-logo.svg
%{_mandir}/man1/notmuch-emacs-mua.1*
%{_bindir}/notmuch-emacs-mua
%{_datadir}/applications/notmuch-emacs-mua.desktop

%if 0%{?with_python2}
%files -n python2-notmuch
%doc bindings/python/README
%{python2_sitelib}/notmuch*
%endif

%if 0%{?with_python3legacy}
%files -n python3-notmuch
%doc bindings/python/README
%{python3_sitelib}/notmuch*
%endif

%if 0%{?with_python3CFFI}
%files -n python3-notmuch2
%{python3_sitearch}/notmuch*
%endif

%files -n ruby-notmuch
%{ruby_vendorarchdir}/*

%files mutt
%{_bindir}/notmuch-mutt
%{_mandir}/man1/notmuch-mutt.1*

%files vim
%{_datadir}/vim/vimfiles/doc/notmuch.txt
%{_datadir}/vim/vimfiles/plugin/notmuch.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-compose.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-folders.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-git-diff.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-search.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-show.vim

%changelog
* Tue Mar 29 2022 Michael J Gruber <mjg@fedoraproject.org> - 0.35^29.g04b43dc4-1
- build from git/copr
