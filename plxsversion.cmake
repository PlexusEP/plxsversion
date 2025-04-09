set(DIR_OF_PLXSVERSION "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "DIR_OF_PLXSVERSION")

function(_create_version_file LANG)
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs")
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion")

  set(file_ext "hpp")
  if(LANG STREQUAL "c")
    set(file_ext "h")
  endif()

  set(ENV{PYTHONPATH} "${DIR_OF_PLXSVERSION}/src:ENV{PYTHONPATH}")
  execute_process(
    COMMAND /usr/bin/env python -m version_builder --lang ${LANG} --source git --input "${CMAKE_CURRENT_SOURCE_DIR}" "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion/version.${file_ext}"
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
    "LANG"
    ""
    ${ARGN}
  )

  if(NOT VER_LANG)
    set(VER_LANG cpp)
  endif()

  _create_version_file(${VER_LANG})
  target_include_directories(${TARGET} PUBLIC "${CMAKE_CURRENT_BINARY_DIR}/plxs")
  _set_version_cmake_variable(PLXS_VERSION_STRING)
endfunction(target_plxsversion_init)