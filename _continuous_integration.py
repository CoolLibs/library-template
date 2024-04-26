def setup_continuous_integration(lib_name, needs_imgui: bool):
    from tooling.internal_utils import make_clean_directory
    from _utils import path_to
    from os.path import join

    make_clean_directory(path_to(join(".github", "workflows")))

    from _utils import make_file

    make_file(
        join(".github", "workflows", "build_and_run_tests.yml"),
        f"""name: Build and run tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  cmake_configure_args: -D WARNINGS_AS_ERRORS_FOR_{lib_name.upper()}=ON
  cmakelists_folder: tests
  cmake_target: {lib_name}-tests

jobs:
  build-and-run-tests:
    name: ${{{{matrix.config.name}}}} ${{{{matrix.build_type}}}}
    runs-on: ${{{{matrix.config.os}}}}
    strategy:
      fail-fast: false
      matrix:
        config:
          - {{
              name: Windows MSVC,
              os: windows-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=cl CMAKE_CXX_COMPILER=cl,
            }}
          - {{
              name: Windows Clang,
              os: windows-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=clang -D CMAKE_CXX_COMPILER=clang,
            }}
          - {{
              name: Windows GCC,
              os: windows-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=gcc -D CMAKE_CXX_COMPILER=g++,
            }}
          - {{
              name: Linux Clang,
              os: ubuntu-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=clang -D CMAKE_CXX_COMPILER=clang++,
            }}
          - {{
              name: Linux GCC,
              os: ubuntu-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=gcc -D CMAKE_CXX_COMPILER=g++,
            }}
          - {{
              name: MacOS Clang,
              os: macos-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=clang -D CMAKE_CXX_COMPILER=clang++,
            }}
          - {{
              name: MacOS GCC,
              os: macos-latest,
              cmake_configure_args: -D CMAKE_C_COMPILER=gcc-13 -D CMAKE_CXX_COMPILER=g++-13,
            }}
        build_type:
          - Debug
          - Release

    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive

      - name: Set up MSVC # NOTE: required to find cl.exe and clang.exe when using the Ninja generator. And we need to use Ninja in order for ccache to be able to cache stuff on Windows.
        if: runner.os == 'Windows' && matrix.config.name != 'Windows GCC'
        uses: ilammy/msvc-dev-cmd@v1.13.0

      - name: ccache
        uses: hendrikmuhs/ccache-action@main
        with:
          key: ${{{{matrix.config.name}}}}-${{{{matrix.build_type}}}}

      - name: Build
        uses: lukka/run-cmake@v3
        with:
          cmakeListsOrSettingsJson: CMakeListsTxtAdvanced
          cmakeListsTxtPath: ${{{{github.workspace}}}}/${{{{env.cmakelists_folder}}}}/CMakeLists.txt
          cmakeAppendedArgs: ${{{{env.cmake_configure_args}}}} -G Ninja -D CMAKE_BUILD_TYPE=${{{{matrix.build_type}}}} ${{{{matrix.config.cmake_configure_args}}}} -D CMAKE_C_COMPILER_LAUNCHER=ccache -D CMAKE_CXX_COMPILER_LAUNCHER=ccache
          buildWithCMakeArgs: --config ${{{{matrix.build_type}}}} --target ${{{{env.cmake_target}}}}
          cmakeBuildType: ${{{{matrix.build_type}}}}
          buildDirectory: ${{{{github.workspace}}}}/build

      - name: Run
        run: ${{{{github.workspace}}}}/build/${{{{env.cmake_target}}}}
""",
    )
