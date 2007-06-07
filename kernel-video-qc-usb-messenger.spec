# TODO:
# - make qc-usb-messenger main package and kernel-* subpackages
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace utility
#
%define		_module_name	qc-usb-messenger
%define	_rel	0.1
Summary:	Kernel module for Logitech QuickCam Messenger USB cameras
Summary(pl.UTF-8):	Moduł jądra do kamer USB Logitech QuickCam Messenger
Name:		kernel-video-%{_module_name}
Version:	1.5
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://home.mag.cx/messenger/source/%{_module_name}-%{version}.tar.gz
# Source0-md5:	8153aacef6a1875371a9d9d03fea8590
Patch0:		%{name}-compat_semaphore.patch
URL:		http://home.mag.cx/messenger/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build >= 3:2.6
%endif
BuildRequires:	rpmbuild(macros) >= 1.118
%if %{with kernel} && %{with dist_kernel}
%requires_releq_kernel
%endif
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Here are some information about the driver:
 - Support for Quickcam Messenger (0x046D, 0x08F0) & (0x046D, 0x08F6)
 - Support for Quickcam Communicate (0x046D, 0x08F5)
 - 162x124, 162x248, 324x124, 324x248 resolution available
 - Auto exposure works (need some tuning though)
 - Auto shutter-control works (need some tuning though)
 - Read status of the button on the camera
 - Compressed format is still unknown

%description -l pl.UTF-8
Trochę informacji o sterowniku:
 - obsługuje kamery Quickcam Messenger (0x046D, 0x08F0) i (0x046D,
   0x08F6)
 - obsługuje kamery Quickcam Communicate (0x046D, 0x08F5)
 - dostępne rozdzielczości to 162x124, 162x248, 324x124, 324x248
 - działa automatyczna ekspozycja (ale wymaga podregulowania)
 - działa automatyczna przysłona (ale wymaga podregulowania)
 - odczytuje status przycisku kamery
 - format kompresji pozostaje nieznany

%package -n %{_module_name}
Summary:	Documentation and test program to Logitech QuickCam Messenger USB
Summary(pl.UTF-8):	Dokumentacja i program testujący do kamer Logitech QuickCam Messenger USB
Release:	%{_rel}
Group:		Base/Kernel

%description -n %{_module_name}
Documentation and test program to Logitech QuickCam Messenger USB.

%description -n %{_module_name} -l pl.UTF-8
Dokumentacja i program testujący do kamer Logitech QuickCam Messenger
USB.

%prep
%setup -q -n %{_module_name}-%{version}
#%patch0 -p1

%build
rm -rf built

%build_kernel_modules -m quickcam

%if %{with userspace}
%{__make} -C testquickcam \
	CC="%{__cc} %{rpmcflags}"
%{__cc} %{rpmcflags} -lm -s -o qcset qcset.c
# TODO: %{__cc}, %{rpmcflags}
%endif

%install
rm -rf $RPM_BUILD_ROOT

%install_kernel_modules -m quickcam -d misc

%if %{with userspace}
install -D qcset $RPM_BUILD_ROOT%{_sbindir}/qcset
install testquickcam/testquickcam $RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*
%endif

%if %{with userspace}
%files -n %{_module_name}
%defattr(644,root,root,755)
%doc README
%attr(755,root,users) %{_sbindir}/testquickcam
%attr(755,root,users) %{_sbindir}/qcset
%endif
