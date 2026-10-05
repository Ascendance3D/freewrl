# CMake build for FreeWRL on Linux (X11 or Motif window targets) and
# macOS Apple Silicon (Cocoa/Aqua FreeWRL.app, OpenGL 4.1 core).
#
#   cmake -S freex3d -B build -G Ninja
#   cmake --build build
#
# On macOS, point CMAKE_PREFIX_PATH at the tools/macos-deps prefix
# (FreeType, ODE, freealut), for example -DCMAKE_PREFIX_PATH=$HOME/freewrl-deps.
#
# Linux mirrors configure.ac and the Makefile.am files. macOS mirrors the
# FreeWRL target in OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj. Source lists are
# read from the same Makefile.sources files Autotools uses, so there is one
# list to maintain. Windows builds use projectfiles_2022.

cmake_minimum_required(VERSION 3.20)

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/versions/FREEWRL" FREEWRL_VERSION LIMIT_COUNT 1)
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/versions/LIBFREEWRL" LIBFREEWRL_VERSION LIMIT_COUNT 1)
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/versions/LIBFREEWRL_LTVERSION" LIBFREEWRL_LTVERSION LIMIT_COUNT 1)
file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/versions/MESSAGEMGR" MESSAGEMGR_VERSION LIMIT_COUNT 1)

# Ignored outside macOS. Matches MACOSX_DEPLOYMENT_TARGET in the Xcode project.
set(CMAKE_OSX_DEPLOYMENT_TARGET "15.0" CACHE STRING "Minimum macOS version")

project(freewrl
  VERSION ${FREEWRL_VERSION}
  DESCRIPTION "X3D/VRML97 browser"
  LANGUAGES C CXX)

if(WIN32)
  message(FATAL_ERROR
    "This CMake build covers Linux and macOS. Use freex3d/projectfiles_2022 on Windows.")
endif()
if(APPLE)
  # The Cocoa front end (OSX_gui/FreeWRL-Desktop/FreeWRL/*.m) is Objective-C.
  enable_language(OBJC)
endif()

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(FATAL_ERROR "In-source builds are not supported; use -B <build-dir>.")
endif()

include(GNUInstallDirs)
include(CheckIncludeFile)
include(CheckSymbolExists)
include(CheckFunctionExists)
include(CheckTypeSize)
include(CMakePushCheckState)

set(PACKAGE "freewrl")
set(PACKAGE_BUGREPORT "freewrl-develop@lists.sourceforge.net")

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE RelWithDebInfo CACHE STRING "Build type" FORCE)
endif()

# ---------------------------------------------------------------------------
# Options (configure.ac equivalents)
# ---------------------------------------------------------------------------
# macOS defaults follow OSX_gui/FreeWRL-Desktop/FreeWRL/config.h: RBP on;
# no DIS, FFmpeg, fontconfig or freewrl_msg.
if(APPLE)
  set(_linux_default OFF)
  set(_apple_default ON)
  set(_default_target "aqua")
else()
  set(_linux_default ON)
  set(_apple_default OFF)
  set(_default_target "x11")
endif()

set(FREEWRL_TARGET "${_default_target}" CACHE STRING "Window target: x11 or motif on Linux, aqua on macOS (--with-target)")
set_property(CACHE FREEWRL_TARGET PROPERTY STRINGS x11 motif aqua)
set(FREEWRL_JAVASCRIPT "duk" CACHE STRING "JavaScript engine: duk or stub (--with-javascript)")
set_property(CACHE FREEWRL_JAVASCRIPT PROPERTY STRINGS duk stub)

option(FREEWRL_ENABLE_FONTCONFIG "Use fontconfig if found (--enable-fontconfig)" ${_linux_default})
option(FREEWRL_ENABLE_LIBCURL "Use libcurl if found; otherwise wget (--enable-libcurl)" ON)
option(FREEWRL_ENABLE_FFMPEG "Use FFmpeg for MovieTexture if found" ${_linux_default})
option(FREEWRL_ENABLE_OPENCL "Use OpenCL (--with-OpenCL)" OFF)
option(FREEWRL_ENABLE_DIS "Distributed Interactive Simulation (--with-DIS)" ${_linux_default})
option(FREEWRL_ENABLE_RBP "RigidBodyPhysics via libODE (--enable-rbp)" ${_apple_default})
option(FREEWRL_ENABLE_OSC "OSC support via liblo (--enable-osc)" OFF)
option(FREEWRL_ENABLE_TWODEE "Experimental 2D overlay (--enable-twodee)" OFF)
option(FREEWRL_ENABLE_STL "STL file parsing (--enable-STL)" OFF)
option(FREEWRL_THREAD_COLORIZED "Colorized thread console output (--enable-thread_colorized)" OFF)
option(FREEWRL_BUILD_MESSAGE "Build the freewrl_msg helper (Linux only)" ${_linux_default})

if(APPLE)
  set(_default_fonts_dir "/Applications/FreeWRL/fonts")
else()
  set(_default_fonts_dir "${CMAKE_INSTALL_FULL_DATADIR}/${PACKAGE}/fonts")
endif()
set(FREEWRL_FONTS_DIR "${_default_fonts_dir}"
  CACHE PATH "Font directory compiled in as FONTS_DIR (--with-fontsdir)")
set(FREEWRL_PLUGIN_DIR "${CMAKE_INSTALL_FULL_LIBDIR}/mozilla/plugins"
  CACHE PATH "Browser plugin directory compiled in as PLUGIN_DIR (--with-plugindir)")

if(APPLE AND NOT FREEWRL_TARGET STREQUAL "aqua")
  message(FATAL_ERROR "FREEWRL_TARGET must be aqua on macOS, got '${FREEWRL_TARGET}'")
elseif(NOT APPLE AND NOT FREEWRL_TARGET MATCHES "^(x11|motif)$")
  message(FATAL_ERROR "FREEWRL_TARGET must be x11 or motif, got '${FREEWRL_TARGET}'")
endif()
if(APPLE AND FREEWRL_BUILD_MESSAGE)
  message(FATAL_ERROR "freewrl_msg is Linux only; set FREEWRL_BUILD_MESSAGE=OFF")
endif()
if(NOT FREEWRL_JAVASCRIPT MATCHES "^(duk|stub)$")
  message(FATAL_ERROR "FREEWRL_JAVASCRIPT must be duk or stub, got '${FREEWRL_JAVASCRIPT}'")
endif()

# Feature switches consumed by cmake/config.h.cmake and cmake/config-macos.h.cmake
if(FREEWRL_JAVASCRIPT STREQUAL "duk")
  set(JAVASCRIPT_DUK ON)
else()
  set(JAVASCRIPT_STUB ON)
endif()
set(WITH_DIS ${FREEWRL_ENABLE_DIS})
set(WANT_2D_OVER ${FREEWRL_ENABLE_TWODEE})
set(INCLUDE_STL_FILES ${FREEWRL_ENABLE_STL})

# ---------------------------------------------------------------------------
# Platform checks
# ---------------------------------------------------------------------------
if(APPLE)
  # No probes on macOS: use the fixed set from OSX_gui/FreeWRL-Desktop/FreeWRL/config.h.
  # Probing would turn on code paths the Xcode build never uses (for example
  # HAVE_PTHREAD_CANCEL changes how the loader threads exit).
  foreach(var HAVE_CTYPE_H HAVE_DIRENT_H HAVE_ERRNO_H HAVE_FCNTL_H HAVE_GETOPT_H
              HAVE_INTTYPES_H HAVE_LIMITS_H HAVE_MATH_H HAVE_SCHED_H HAVE_STDARG_H
              HAVE_STDBOOL_H HAVE_STDINT_H HAVE_STDLIB_H HAVE_STRING_H HAVE_SYS_SOCKET_H
              HAVE_SYS_STAT_H HAVE_SYS_TIME_H HAVE_SYS_TYPES_H HAVE_SYS_WAIT_H HAVE_TIME_H
              HAVE_UNISTD_H HAVE_GETOPT_LONG HAVE_GETTIMEOFDAY HAVE_MEMCPY HAVE_STRNDUP
              HAVE_STRNLEN)
    set(${var} ON)
  endforeach()
else()
  foreach(hdr ctype.h dirent.h dlfcn.h errno.h fcntl.h getopt.h inttypes.h limits.h
              math.h sched.h signal.h stdarg.h stdbool.h stdint.h stdio.h stdlib.h
              strings.h string.h sys/ioctl.h sys/ipc.h sys/msg.h sys/socket.h
              sys/stat.h sys/time.h sys/types.h sys/wait.h time.h unistd.h)
    string(TOUPPER "HAVE_${hdr}" var)
    string(REGEX REPLACE "[/.]" "_" var "${var}")
    check_include_file("${hdr}" ${var})
  endforeach()

  check_type_size(_Bool SIZEOF__BOOL LANGUAGE C)
  set(HAVE__BOOL ${HAVE_SIZEOF__BOOL})

  cmake_push_check_state(RESET)
  set(CMAKE_REQUIRED_DEFINITIONS -D_GNU_SOURCE)
  foreach(fn calloc fork vfork getopt getopt_long getopt_long_only gettimeofday malloc
             realloc strchr strdup strerror strndup strrchr usleep)
    string(TOUPPER "HAVE_${fn}" var)
    check_function_exists(${fn} ${var})
  endforeach()
  cmake_pop_check_state()
  set(HAVE_WORKING_FORK ${HAVE_FORK})
  set(HAVE_WORKING_VFORK ${HAVE_VFORK})
endif()

# ---------------------------------------------------------------------------
# Dependencies shared by Linux and macOS
# ---------------------------------------------------------------------------
find_package(PkgConfig REQUIRED)
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)
find_package(ZLIB REQUIRED)
set(HAVE_ZLIB_H ON)

if(CMAKE_USE_PTHREADS_INIT)
  set(HAVE_PTHREAD ON)
  if(NOT APPLE)
    cmake_push_check_state(RESET)
    set(CMAKE_REQUIRED_LIBRARIES Threads::Threads)
    check_symbol_exists(pthread_cancel pthread.h HAVE_PTHREAD_CANCEL)
    cmake_pop_check_state()
  endif()
endif()

pkg_check_modules(FREETYPE REQUIRED IMPORTED_TARGET freetype2)

if(FREEWRL_ENABLE_RBP)
  pkg_check_modules(ODE IMPORTED_TARGET ode)
  set(WITH_RBP ${ODE_FOUND})
endif()

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(FW_DEBUG ON)
endif()

if(APPLE)
# ---------------------------------------------------------------------------
# macOS dependencies (Xcode target: Cocoa, OpenGL, OpenAL frameworks; SDK
# libcurl, libxml2, libz; freetype, ode, alut from the deps prefix)
# ---------------------------------------------------------------------------
  find_library(COCOA_FRAMEWORK Cocoa REQUIRED)
  find_library(OPENGL_FRAMEWORK OpenGL REQUIRED)
  find_library(OPENAL_FRAMEWORK OpenAL)
  if(OPENAL_FRAMEWORK)
    set(HAVE_OPENAL ON)
  endif()

  # libxml2 and libcurl come from the active macOS SDK, like the Xcode target
  # ($(SDKROOT)/usr/include/libxml2, libxml2.dylib, libcurl.tbd). They are
  # linked by name and not searched for, so that pkg-config cannot pick
  # headers from a different SDK.
  set(HAVE_LIBCURL ${FREEWRL_ENABLE_LIBCURL})

  # freealut ships no pkg-config file.
  find_path(ALUT_INCLUDE_DIR AL/alut.h)
  find_library(ALUT_LIBRARY alut)
  if(ALUT_INCLUDE_DIR AND ALUT_LIBRARY AND HAVE_OPENAL)
    set(HAVE_ALUT ON)
  endif()

  # Values from OSX_gui/FreeWRL-Desktop/FreeWRL/config.h
  set(PACKAGE_BUGREPORT "freewrl.sf.net")
  set(FREEWRL_BROWSER "/usr/bin/open")
  set(FREEWRL_MESSAGE_WRAPPER "/usr/bin/say")
  set(FWVER "1.22.13")

  configure_file(cmake/config-macos.h.cmake "${CMAKE_CURRENT_BINARY_DIR}/config.h")
else()
# ---------------------------------------------------------------------------
# Linux dependencies
# ---------------------------------------------------------------------------
  find_library(MATH_LIBRARY m)

  pkg_check_modules(LIBXML2 REQUIRED IMPORTED_TARGET libxml-2.0)
  pkg_check_modules(PNG REQUIRED IMPORTED_TARGET libpng)

  if(FREEWRL_ENABLE_FONTCONFIG)
    pkg_check_modules(FONTCONFIG IMPORTED_TARGET fontconfig)
    set(HAVE_FONTCONFIG ${FONTCONFIG_FOUND})
  endif()

  if(FREEWRL_ENABLE_LIBCURL)
    pkg_check_modules(LIBCURL IMPORTED_TARGET libcurl)
    set(HAVE_LIBCURL ${LIBCURL_FOUND})
  endif()

  pkg_check_modules(IMLIB2 IMPORTED_TARGET imlib2)
  set(HAVE_IMLIB2 ${IMLIB2_FOUND})

  # configure.ac checks libjpeg only when imlib2 is missing.
  if(NOT IMLIB2_FOUND)
    find_package(JPEG REQUIRED)
  endif()

  pkg_check_modules(ALUT IMPORTED_TARGET freealut)
  set(HAVE_ALUT ${ALUT_FOUND})
  pkg_check_modules(OPENAL IMPORTED_TARGET openal)
  set(HAVE_OPENAL ${OPENAL_FOUND})

  if(FREEWRL_ENABLE_FFMPEG)
    pkg_check_modules(FFMPEG IMPORTED_TARGET
      libavcodec libavutil libavformat libswresample libswscale)
    set(MOVIETEXTURE_FFMPEG ${FFMPEG_FOUND})
  endif()

  if(FREEWRL_ENABLE_OPENCL)
    find_package(OpenCL REQUIRED)
    set(HAVE_OPENCL ON)
  endif()

  if(FREEWRL_ENABLE_OSC)
    pkg_check_modules(LIBLO IMPORTED_TARGET liblo)
    set(WANT_OSC ${LIBLO_FOUND})
  endif()

  # OpenGL: configure.ac links -lGLU -lGL and adds -DANGLE=1.
  set(OpenGL_GL_PREFERENCE LEGACY)
  find_package(OpenGL REQUIRED COMPONENTS OpenGL)
  find_library(GLU_LIBRARY GLU REQUIRED)

  # X11 / Xaw (both targets), Motif (motif target)
  find_package(X11 REQUIRED)
  pkg_check_modules(XAW REQUIRED IMPORTED_TARGET xproto x11 xt xmu xaw7)
  pkg_check_modules(XXF86VM IMPORTED_TARGET xxf86vm)
  if(XXF86VM_FOUND)
    set(HAVE_X11_EXTENSIONS_XF86VMODE_H ON)
    set(HAVE_XF86_VMODE ON)
  endif()

  if(FREEWRL_TARGET STREQUAL "motif")
    find_path(MOTIF_INCLUDE_DIR Xm/Xm.h)
    find_library(MOTIF_LIBRARY Xm)
    if(NOT MOTIF_INCLUDE_DIR OR NOT MOTIF_LIBRARY)
      message(FATAL_ERROR "Target motif specified but motif was not found")
    endif()
  endif()

  # Helper programs compiled in as string defines
  find_program(FREEWRL_BROWSER_PROGRAM firefox)
  set(FREEWRL_BROWSER "${FREEWRL_BROWSER_PROGRAM}")
  if(NOT FREEWRL_BROWSER_PROGRAM)
    set(FREEWRL_BROWSER "false")
    message(WARNING "firefox not found; anchors need the BROWSER environment variable")
  endif()

  find_program(FREEWRL_UNZIP_PROGRAM unzip)
  if(NOT FREEWRL_UNZIP_PROGRAM)
    message(FATAL_ERROR "No zip decompressor; set FREEWRL_UNZIP_PROGRAM")
  endif()
  set(FREEWRL_UNZIP "${FREEWRL_UNZIP_PROGRAM}")

  if(NOT HAVE_LIBCURL)
    find_program(FREEWRL_WGET_PROGRAM wget)
    if(NOT FREEWRL_WGET_PROGRAM)
      message(FATAL_ERROR "No libcurl and no wget; install one or set FREEWRL_WGET_PROGRAM")
    endif()
    set(WGET "${FREEWRL_WGET_PROGRAM}")
  endif()

  if(HAVE_IMLIB2)
    set(FREEWRL_IMAGECONVERT "")
  else()
    find_program(FREEWRL_IMAGECONVERT_PROGRAM convert)
    set(FREEWRL_IMAGECONVERT "${FREEWRL_IMAGECONVERT_PROGRAM}")
    if(NOT FREEWRL_IMAGECONVERT_PROGRAM)
      set(FREEWRL_IMAGECONVERT "false")
    endif()
  endif()

  configure_file(cmake/config.h.cmake "${CMAKE_CURRENT_BINARY_DIR}/config.h")
endif()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Read "<var> = a b \ c ..." from an Automake Makefile.sources file.
function(freewrl_read_sources out file var)
  file(READ "${file}" text)
  string(REGEX REPLACE "#[^\n]*" "" text "${text}")
  string(REGEX REPLACE "\\\\\n" " " text "${text}")
  string(REGEX MATCH "(^|\n)[ \t]*${var}[ \t]*=([^\n]*)" _ "${text}")
  if(NOT CMAKE_MATCH_2)
    message(FATAL_ERROR "${var} not found in ${file}")
  endif()
  separate_arguments(list UNIX_COMMAND "${CMAKE_MATCH_2}")
  list(FILTER list INCLUDE REGEX "\\.(c|cc|cpp)$")
  get_filename_component(dir "${file}" DIRECTORY)
  list(TRANSFORM list PREPEND "${dir}/")
  set(${out} ${list} PARENT_SCOPE)
endfunction()

# Equivalent of the vtempl rule: versions/template/version.c.in -> internal_version.c
function(freewrl_version_source out component version)
  set(_component "${component}")
  set(_version "${version}")
  set(dest "${CMAKE_CURRENT_BINARY_DIR}/${component}_version.c")
  configure_file("${CMAKE_CURRENT_SOURCE_DIR}/versions/template/version.c.in" "${dest}" @ONLY)
  set(${out} "${dest}" PARENT_SCOPE)
endfunction()

# Flags shared by every target (Makefile.globals on Linux, the Xcode project on macOS)
add_library(freewrl_build_flags INTERFACE)
target_include_directories(freewrl_build_flags BEFORE INTERFACE "${CMAKE_CURRENT_BINARY_DIR}")
if(APPLE)
  # The warning set that xcodebuild passes for the FreeWRL target (its defaults
  # plus the CLANG_WARN_* / GCC_WARN_* settings), without Xcode's -Wno-conversion.
  # Ahead of -Wint-conversion, that flag turns int-conversion from clang's
  # default error into a warning, and no source needs that any more.
  set(FREEWRL_XCODE_WARNINGS
    -Wno-trigraphs -Wno-missing-field-initializers -Wno-missing-prototypes
    -Wunreachable-code -Wno-missing-braces -Wparentheses -Wswitch
    -Wunused-function -Wno-unused-label -Wno-unused-parameter -Wunused-variable
    -Wunused-value -Wempty-body -Wuninitialized -Wno-unknown-pragmas -Wno-shadow
    -Wno-four-char-constants -Wconstant-conversion -Wint-conversion
    -Wbool-conversion -Wenum-conversion -Wno-float-conversion
    -Wno-non-literal-null-conversion -Wno-objc-literal-conversion
    -Wshorten-64-to-32 -Wpointer-sign -Wno-newline-eof -Wno-implicit-fallthrough
    -Wdeprecated-declarations -Wno-sign-conversion -Wno-infinite-recursion
    -Wno-comma -Wno-block-capture-autoreleasing -Wno-strict-prototypes
    -Wno-semicolon-before-method-body)
  set(FREEWRL_XCODE_OBJC_WARNINGS
    -Wno-implicit-atomic-properties -Wno-objc-interface-ivars
    -Wno-arc-repeated-use-of-weak -Wduplicate-method-match -Wno-selector
    -Wno-strict-selector-match -Wundeclared-selector
    -Wno-deprecated-implementations -Wprotocol)
  target_compile_features(freewrl_build_flags INTERFACE c_std_17)
  target_compile_definitions(freewrl_build_flags INTERFACE
    $<$<CONFIG:Debug>:DEBUG>
    $<$<COMPILE_LANGUAGE:OBJC>:OBJC_OLD_DISPATCH_PROTOTYPES=0>)
  target_compile_options(freewrl_build_flags INTERFACE
    ${FREEWRL_XCODE_WARNINGS}
    $<$<COMPILE_LANGUAGE:OBJC>:${FREEWRL_XCODE_OBJC_WARNINGS}>)
else()
  target_compile_definitions(freewrl_build_flags INTERFACE _GNU_SOURCE)
  target_compile_options(freewrl_build_flags INTERFACE $<$<COMPILE_LANGUAGE:CXX>:-fpermissive>)
endif()

# ---------------------------------------------------------------------------
# libFreeWRL (src/lib/Makefile.am; on macOS the library part of the Xcode target)
# ---------------------------------------------------------------------------
set(LIB_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/lib")
freewrl_read_sources(LIBFREEWRL_SOURCES "${LIB_DIR}/Makefile.sources" libFreeWRL_la_SOURCES)

if(FREEWRL_ENABLE_DIS)
  list(APPEND LIBFREEWRL_SOURCES "${LIB_DIR}/DIS/DIS.c" "${LIB_DIR}/scenegraph/socketutils.c")
endif()

if(APPLE)
  # Makefile.sources entries that the Xcode target does not compile.
  list(REMOVE_ITEM LIBFREEWRL_SOURCES
    "${LIB_DIR}/input/convertSTL.c"
    "${LIB_DIR}/main/SnapshotTesting.c"
    "${LIB_DIR}/opencl/OpenCL_Utils.c"
    "${LIB_DIR}/scenegraph/readpng.c")
  list(FILTER LIBFREEWRL_SOURCES EXCLUDE REGEX "_sm\\.cpp$")
  # Aqua window, OpenGL 4.1 core compatibility layer and the front-end API.
  list(APPEND LIBFREEWRL_SOURCES
    "${LIB_DIR}/ui/fwWindowAqua.c"
    "${LIB_DIR}/ui/GLwDrawA.c"
    "${LIB_DIR}/opengl/GLCoreCompat.c"
    "${LIB_DIR}/opengl/OSX_miniglew.c"
    "${LIB_DIR}/scenegraph/OSCcallbacks.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/dllFreeWRL/cdllFreeWRL.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src_aqua/fwVersion.c")
  # The app is one executable, like the Xcode target.
  add_library(FreeWRL STATIC ${LIBFREEWRL_SOURCES})
  set_target_properties(FreeWRL PROPERTIES C_VISIBILITY_PRESET hidden)
else()
  if(FREEWRL_TARGET STREQUAL "x11")
    list(APPEND LIBFREEWRL_SOURCES "${LIB_DIR}/ui/fwCommonX11.c" "${LIB_DIR}/ui/fwBareWindow.c")
  else()
    list(APPEND LIBFREEWRL_SOURCES "${LIB_DIR}/ui/fwCommonX11.c" "${LIB_DIR}/ui/fwMotifWindow.c")
  endif()
  freewrl_version_source(LIBFREEWRL_VERSION_C libFreeWRL "${LIBFREEWRL_VERSION}")
  add_library(FreeWRL SHARED ${LIBFREEWRL_SOURCES} "${LIBFREEWRL_VERSION_C}")

  # libtool -version-info current:revision:age -> SOVERSION current-age
  string(REPLACE ":" ";" _lt "${LIBFREEWRL_LTVERSION}")
  list(GET _lt 0 _lt_current)
  list(GET _lt 1 _lt_revision)
  list(GET _lt 2 _lt_age)
  math(EXPR _so_major "${_lt_current} - ${_lt_age}")
  set_target_properties(FreeWRL PROPERTIES
    VERSION "${_so_major}.${_lt_age}.${_lt_revision}"
    SOVERSION "${_so_major}"
    C_VISIBILITY_PRESET default
    PUBLIC_HEADER "${LIB_DIR}/libFreeWRL.h")
endif()

target_include_directories(FreeWRL PUBLIC
  "$<BUILD_INTERFACE:${LIB_DIR}>"
  "$<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>")
target_link_libraries(FreeWRL
  PRIVATE
    freewrl_build_flags
    ZLIB::ZLIB
    Threads::Threads
    PkgConfig::FREETYPE
    $<$<BOOL:${ODE_FOUND}>:PkgConfig::ODE>)

if(APPLE)
  # SDK header directories from the Xcode target. cdllFreeWRL.c includes
  # <malloc.h>, which the SDK keeps in usr/include/malloc.
  target_compile_options(FreeWRL PUBLIC "SHELL:-iwithsysroot /usr/include/libxml2")
  target_compile_options(FreeWRL PRIVATE "SHELL:-iwithsysroot /usr/include/malloc")
  # display.h includes <libtess2.h> on macOS.
  target_include_directories(FreeWRL PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/src/libtess")
  if(HAVE_ALUT)
    target_include_directories(FreeWRL PRIVATE "${ALUT_INCLUDE_DIR}")
  endif()
  target_link_libraries(FreeWRL
    PUBLIC
      xml2
      ${COCOA_FRAMEWORK}
      ${OPENGL_FRAMEWORK}
      $<$<BOOL:${HAVE_OPENAL}>:${OPENAL_FRAMEWORK}>
      $<$<BOOL:${HAVE_ALUT}>:${ALUT_LIBRARY}>
      $<$<BOOL:${HAVE_LIBCURL}>:curl>)
else()
  target_compile_definitions(FreeWRL PRIVATE
    ANGLE=1
    $<IF:$<STREQUAL:${FREEWRL_TARGET},x11>,TARGET_X11,TARGET_MOTIF>)
  target_compile_options(FreeWRL PRIVATE
    $<$<COMPILE_LANGUAGE:C>:-fno-strict-aliasing>)
  target_link_libraries(FreeWRL
    PRIVATE
      PkgConfig::LIBXML2
      PkgConfig::PNG
      OpenGL::GL
      ${GLU_LIBRARY}
      X11::X11
      X11::SM
      X11::ICE
      PkgConfig::XAW
      $<$<BOOL:${FONTCONFIG_FOUND}>:PkgConfig::FONTCONFIG>
      $<$<BOOL:${LIBCURL_FOUND}>:PkgConfig::LIBCURL>
      $<$<BOOL:${IMLIB2_FOUND}>:PkgConfig::IMLIB2>
      $<$<BOOL:${ALUT_FOUND}>:PkgConfig::ALUT>
      $<$<BOOL:${OPENAL_FOUND}>:PkgConfig::OPENAL>
      $<$<BOOL:${FFMPEG_FOUND}>:PkgConfig::FFMPEG>
      $<$<BOOL:${XXF86VM_FOUND}>:PkgConfig::XXF86VM>
      $<$<BOOL:${LIBLO_FOUND}>:PkgConfig::LIBLO>
      $<$<BOOL:${HAVE_OPENCL}>:OpenCL::OpenCL>
      $<$<BOOL:${MATH_LIBRARY}>:${MATH_LIBRARY}>)
  if(NOT IMLIB2_FOUND)
    target_link_libraries(FreeWRL PRIVATE JPEG::JPEG)
  endif()
  if(FREEWRL_TARGET STREQUAL "motif")
    target_include_directories(FreeWRL PRIVATE "${MOTIF_INCLUDE_DIR}")
    target_link_libraries(FreeWRL PRIVATE "${MOTIF_LIBRARY}")
  endif()
endif()

if(APPLE)
# ---------------------------------------------------------------------------
# FreeWRL.app (the FreeWRL target in OSX_gui/FreeWRL-Desktop/FreeWRL.xcodeproj)
# ---------------------------------------------------------------------------
  set(MAC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../OSX_gui/FreeWRL-Desktop")
  set(MAC_APP_DIR "${MAC_DIR}/FreeWRL")

  # NSApplicationMain loads MainMenu.nib (NSMainNibFile), so the xib must be compiled.
  find_program(IBTOOL ibtool REQUIRED)
  set(MAINMENU_NIB "${CMAKE_CURRENT_BINARY_DIR}/MainMenu.nib")
  add_custom_command(OUTPUT "${MAINMENU_NIB}"
    COMMAND "${IBTOOL}" --errors --warnings --output-format human-readable-text
            --minimum-deployment-target "${CMAKE_OSX_DEPLOYMENT_TARGET}"
            --compile "${MAINMENU_NIB}" "${MAC_APP_DIR}/MainMenu.xib"
    DEPENDS "${MAC_APP_DIR}/MainMenu.xib"
    COMMENT "Compiling MainMenu.xib"
    VERBATIM)

  set(MAC_LPROJ_RESOURCES
    "${MAC_APP_DIR}/en.lproj/InfoPlist.strings"
    "${MAC_APP_DIR}/en.lproj/Credits.rtf")
  set(MAC_FONTS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/appleOSX/OSX_Specific/fonts")
  file(GLOB MAC_FONT_RESOURCES CONFIGURE_DEPENDS "${MAC_FONTS_DIR}/*")
  set(MAC_PKGINFO "${CMAKE_CURRENT_BINARY_DIR}/PkgInfo")
  file(CONFIGURE OUTPUT "${MAC_PKGINFO}" CONTENT "APPL????")
  set_source_files_properties("${MAC_PKGINFO}" PROPERTIES MACOSX_PACKAGE_LOCATION .)
  set_source_files_properties("${MAINMENU_NIB}" "${MAC_DIR}/X3DFreeWRLIcon.icns"
    PROPERTIES MACOSX_PACKAGE_LOCATION Resources)
  set_source_files_properties(${MAC_LPROJ_RESOURCES}
    PROPERTIES MACOSX_PACKAGE_LOCATION Resources/en.lproj)
  set_source_files_properties(${MAC_FONT_RESOURCES}
    PROPERTIES MACOSX_PACKAGE_LOCATION Resources/fonts)

  add_executable(freewrl_app MACOSX_BUNDLE
    "${MAC_APP_DIR}/main.m"
    "${MAC_APP_DIR}/FreeWRLAppDelegate.m"
    "${MAC_APP_DIR}/FWGLView.m"
    "${MAC_APP_DIR}/AppController.m"
    "${MAC_APP_DIR}/OSX_Specific.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/bin/options.c"
    "${MAINMENU_NIB}"
    "${MAC_PKGINFO}"
    "${MAC_DIR}/X3DFreeWRLIcon.icns"
    ${MAC_LPROJ_RESOURCES}
    ${MAC_FONT_RESOURCES})
  target_precompile_headers(freewrl_app PRIVATE
    "$<$<COMPILE_LANGUAGE:OBJC>:${MAC_APP_DIR}/FreeWRL-Prefix.pch>")
  target_link_libraries(freewrl_app PRIVATE freewrl_build_flags FreeWRL)

  # Info.plist uses Xcode build-setting references; fill them in here.
  set(MAC_BUNDLE_ID "freewrl.sf.net.FreeWRL")
  file(READ "${MAC_APP_DIR}/FreeWRL-Info.plist" _plist)
  string(REPLACE "\${EXECUTABLE_NAME}" "FreeWRL" _plist "${_plist}")
  string(REPLACE "\${PRODUCT_NAME}" "FreeWRL" _plist "${_plist}")
  string(REPLACE "$(PRODUCT_BUNDLE_IDENTIFIER)" "${MAC_BUNDLE_ID}" _plist "${_plist}")
  string(REPLACE "\${MACOSX_DEPLOYMENT_TARGET}" "${CMAKE_OSX_DEPLOYMENT_TARGET}" _plist "${_plist}")
  file(CONFIGURE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/FreeWRL-Info.plist" CONTENT "${_plist}" @ONLY)
  set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${MAC_APP_DIR}/FreeWRL-Info.plist")

  set_target_properties(freewrl_app PROPERTIES
    OUTPUT_NAME FreeWRL
    C_VISIBILITY_PRESET hidden
    OBJC_VISIBILITY_PRESET hidden
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_BINARY_DIR}/FreeWRL-Info.plist"
    XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "${MAC_BUNDLE_ID}"
    # Same single runpath as the Xcode target; package.sh copies dylibs there.
    BUILD_WITH_INSTALL_RPATH ON
    INSTALL_RPATH "@executable_path/../Frameworks")
else()
# ---------------------------------------------------------------------------
# freewrl program (src/bin/Makefile.am)
# ---------------------------------------------------------------------------
  set(BIN_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/bin")
  freewrl_read_sources(FREEWRL_BIN_SOURCES "${BIN_DIR}/Makefile.sources" freewrl_SOURCES)
  freewrl_version_source(FREEWRL_VERSION_C freewrl "${FREEWRL_VERSION}")

  add_executable(freewrl ${FREEWRL_BIN_SOURCES} "${FREEWRL_VERSION_C}")
  # src/bin has its own system.h/internal.h; they must win over src/lib's.
  target_include_directories(freewrl BEFORE PRIVATE "${BIN_DIR}")
  target_include_directories(freewrl PRIVATE ${XAW_INCLUDE_DIRS})
  target_link_libraries(freewrl PRIVATE freewrl_build_flags FreeWRL Threads::Threads)
  if(FREEWRL_TARGET STREQUAL "motif")
    target_include_directories(freewrl PRIVATE "${MOTIF_INCLUDE_DIR}")
  endif()
endif()

# ---------------------------------------------------------------------------
# freewrl_msg helper (src/message/Makefile.am; Linux only in src/Makefile.am)
# ---------------------------------------------------------------------------
if(FREEWRL_BUILD_MESSAGE)
  set(MSG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src/message")
  freewrl_read_sources(FREEWRL_MSG_SOURCES "${MSG_DIR}/Makefile.sources" freewrl_msg_SOURCES)
  freewrl_version_source(FREEWRL_MSG_VERSION_C freewrl_snd "${MESSAGEMGR_VERSION}")
  add_executable(freewrl_msg ${FREEWRL_MSG_SOURCES} "${FREEWRL_MSG_VERSION_C}")
  target_include_directories(freewrl_msg BEFORE PRIVATE "${MSG_DIR}")
  target_link_libraries(freewrl_msg PRIVATE freewrl_build_flags
    X11::X11 X11::SM X11::ICE PkgConfig::XAW
    $<$<BOOL:${XXF86VM_FOUND}>:PkgConfig::XXF86VM>)
  if(FREEWRL_TARGET STREQUAL "motif")
    target_include_directories(freewrl_msg PRIVATE "${MOTIF_INCLUDE_DIR}")
    target_link_libraries(freewrl_msg PRIVATE "${MOTIF_LIBRARY}")
  endif()
endif()

# ---------------------------------------------------------------------------
# Code generation (manual target; generated files are committed).
# Not named "codegen": CMake 3.31+ reserves that name (policy CMP0171).
# ---------------------------------------------------------------------------
find_program(PERL_EXECUTABLE perl)
if(PERL_EXECUTABLE)
  add_custom_target(freewrl_codegen
    COMMAND "${PERL_EXECUTABLE}" VRMLC.pm
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/codegen"
    COMMENT "Regenerating GeneratedCode.c, Structs.h, NodeFields.h"
    VERBATIM)
endif()

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------
if(APPLE)
  install(TARGETS freewrl_app BUNDLE DESTINATION .)
  message(STATUS "FreeWRL ${PROJECT_VERSION}: target=aqua js=${FREEWRL_JAVASCRIPT} "
    "curl=${HAVE_LIBCURL} openal=${HAVE_OPENAL} alut=${HAVE_ALUT} rbp=${WITH_RBP} "
    "arch=${CMAKE_SYSTEM_PROCESSOR} macos=${CMAKE_OSX_DEPLOYMENT_TARGET}")
else()
  set(prefix "${CMAKE_INSTALL_PREFIX}")
  set(exec_prefix "\${prefix}")
  set(libdir "\${exec_prefix}/${CMAKE_INSTALL_LIBDIR}")
  set(includedir "\${prefix}/${CMAKE_INSTALL_INCLUDEDIR}")
  set(VERSION "${LIBFREEWRL_VERSION}")
  configure_file("${LIB_DIR}/libFreeWRL.pc.in" "${CMAKE_CURRENT_BINARY_DIR}/libFreeWRL.pc" @ONLY)

  set(_install_targets FreeWRL freewrl)
  if(FREEWRL_BUILD_MESSAGE)
    list(APPEND _install_targets freewrl_msg)
  endif()
  install(TARGETS ${_install_targets}
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}")
  install(FILES "${CMAKE_CURRENT_BINARY_DIR}/libFreeWRL.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig")
  install(FILES data/freewrl.png DESTINATION "${CMAKE_INSTALL_DATADIR}/pixmaps")
  install(FILES data/freewrl.desktop DESTINATION "${CMAKE_INSTALL_DATADIR}/applications")
  install(FILES doc/freewrl.1 DESTINATION "${CMAKE_INSTALL_MANDIR}/man1")

  message(STATUS "FreeWRL ${PROJECT_VERSION}: target=${FREEWRL_TARGET} js=${FREEWRL_JAVASCRIPT} "
    "curl=${HAVE_LIBCURL} fontconfig=${HAVE_FONTCONFIG} imlib2=${HAVE_IMLIB2} "
    "openal=${HAVE_OPENAL} ffmpeg=${MOVIETEXTURE_FFMPEG} dis=${WITH_DIS}")
endif()
