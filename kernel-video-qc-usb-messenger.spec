# TODO:
# - make qc-usb-messenger main package and kernel-* subpackages
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace utility
#
%ifarch sparc
%undefine with_smp
%endif
%define		_module_name	qc-usb-messenger
Summary:	Kernel module for Logitech QuickCam Messenger USB cameras
Summary(pl):	Modu³ j±dra do kamer USB Logitech QuickCam Messenger
Name:		kernel-video-%{_module_name}
Version:	1.1
%define	_rel	0.2
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://home.mag.cx/messenger/source/%{_module_name}-%{version}.tar.gz
# Source0-md5:	47cdbf10bdff4dd111c867127ffc7928
Patch0:		%{name}-compat_semaphore.patch
URL:		http://home.mag.cx/messenger/
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build >= 2.6}
%endif
BuildRequires:	rpmbuild(macros) >= 1.118
%if %{with kernel} && %{with dist_kernel}
%requires_releq_kernel_up
%endif
Requires(post,postun):	/sbin/depmod
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Here are some information about the driver:

    * Support for Quickcam Messenger (0x046D, 0x08F0) & (0x046D, 0x08F6)
    * Support for Quickcam Communicate (0x046D, 0x08F5)
    * 162x124, 162x248, 324x124, 324x248 resolution available
    * Auto exposure works (need some tuning though)
    * Auto shutter-control works (need some tuning though)
    * Read status of the button on the camera
    * Compressed format is still unknown

%package -n kernel-smp-video-%{_module_name}
Summary:	SMP kernel module for Logitech QuickCam Messenger USB cameras
Summary(pl):	Modu³ j±dra SMP do kamer USB Logitech QuickCam Messenger
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%if %{with kernel} && %{with dist_kernel}
%requires_releq_kernel_smp
%endif
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-video-%{_module_name}
Logitech QuickCam Messenger USB cameras driver for SMP kernel.

%description -n kernel-smp-video-%{_module_name} -l pl
Sterownik do kamer USB Logitech QuickCam Messenger dla j±dra SMP.

%package -n %{_module_name}
Summary:	Documentation and test program to Logitech QuickCam Messenger USB
Summary(pl):	Dokumentacja i program testuj±cy do kamer Logitech QuickCam Messenger USB
Release:	%{_rel}
Group:		Base/Kernel

%description -n %{_module_name}
Documentation and test program to Logitech QuickCam Messenger USB.

%description -n %{_module_name} -l pl
Dokumentacja i program testuj±cy do kamer Logitech QuickCam Messenger USB.

%prep
%setup -q -n %{_module_name}-%{version}
%patch0 -p1

%build
rm -rf built
mkdir -p built/{nondist,smp,up}
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	
	mv *.ko built/$cfg
done

%if %{with userspace}
%{__make} -C testquickcam \
	CC="%{__cc} %{rpmcflags}"
%{__cc} %{rpmcflags} -lm -s -o qcset qcset.c
# TODO: %{__cc}, %{rpmcflags}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},/lib/modules/%{_kernel_ver}{smp,}/video}

%if %{with kernel}
%if %{with dist_kernel} && %{with smp}
install built/smp/quickcam.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/video/quickcam.ko
%endif
install built/up/quickcam.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/video/quickcam.ko
%endif

%if %{with userspace}
install testquickcam/testquickcam $RPM_BUILD_ROOT%{_sbindir}
install qcset $RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post	-n kernel-smp-video-%{_module_name}
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-video-%{_module_name}
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/video/*

%if %{with dist_kernel} && %{with smp}
%files -n kernel-smp-video-%{_module_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/video/*
%endif
%endif

%if %{with userspace}
%files -n %{_module_name}
%defattr(644,root,root,755)
%doc README
%attr(755,root,users) %{_sbindir}/testquickcam
%attr(755,root,users) %{_sbindir}/qcset
%endif
