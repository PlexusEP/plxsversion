set(DIR_OF_PLXSVERSION "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "DIR_OF_PLXSVERSION")

function(_create_version_file LANG SOURCE INPUT)
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs")
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion")

  set(file_ext "hpp")
  if(LANG STREQUAL "c")
    set(file_ext "h")
  endif()

  set(ENV{PYTHONPATH} "${DIR_OF_PLXSVERSION}/src:ENV{PYTHONPATH}")
  execute_process(
    COMMAND /usr/bin/env python -m version_builder --lang ${LANG} --source ${SOURCE} --input "${INPUT}" "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion/version.${file_ext}"
		  RESULT_VARIABLE result)
  if(NOT ${result} EQUAL 0)
    message(FATAL_ERROR "Error running plxsversion tool. Return code is: ${result}")
  endif()
endfunction(_create_version_file)

# Load version string and write it to a cmake variable so it can be accessed from cmake.
function(_set_version_cmake_variable OUTPUT_VARIABLE)
  file(READ "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion/version.hpp" VERSION_FILE_CONTENT)
  string(REGEX REPLACE ".*VERSION_STRING = \"([^\"]*)\".*" "\\1" VERSION_STRING "${VERSION_FILE_CONTENT}")
  message(STATUS "Version from plxsversion: ${VERSION_STRING}")
  set(${OUTPUT_VARIABLE} "${VERSION_STRING}" CACHE INTERNAL "${OUTPUT_VARIABLE}")
endfunction(_set_version_cmake_variable)

######################################################
# Add version information for a target
# Uses:
#   target_plxsversion_init(buildtarget)
# Then, you can use it in your source file:
#   #include <plxsversion/version.hpp>
#   cout << plxsversion::VERSION.toString() << endl;
######################################################
function(target_plxsversion_init TARGET)
  cmake_parse_arguments(
    VER
    ""
    "LANG;SOURCE;INPUT"
    ""
    ${ARGN}
  )

  if(NOT VER_LANG)
    set(VER_LANG cpp)
  endif()

  if(NOT VER_SOURCE AND VER_INPUT)
    message(FATAL_ERROR "Error configuring plxsversion tool. Provided INPUT but no SOURCE.")
  endif()

  if(VER_SOURCE STREQUAL "file" AND NOT VER_INPUT)
    message(FATAL_ERROR "Error configuring plxsversion tool. Requested version from file, but did not provide INPUT.")
  endif()

  if(NOT VER_SOURCE)
    set(VER_SOURCE git)
  endif()

  if(NOT VER_INPUT)
    set(VER_INPUT ${CMAKE_CURRENT_SOURCE_DIR})
  endif()

  _create_version_file(${VER_LANG} ${VER_SOURCE} ${VER_INPUT})
  target_include_directories(${TARGET} PUBLIC "${CMAKE_CURRENT_BINARY_DIR}/plxs")
  _set_version_cmake_variable(PLXS_VERSION_STRING)
endfunction(target_plxsversion_init)