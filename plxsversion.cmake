set(DIR_OF_PLXSVERSION "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "DIR_OF_PLXSVERSION")

find_package(Python COMPONENTS Interpreter REQUIRED)

macro(_set_relative_out_file_path LANG)
  set(REL_OUT_PATH "plxs/plxsversion/version.hpp")
  if(${LANG} STREQUAL "c")
    set(REL_OUT_PATH "plxs/plxsversion/version.h")
  endif()
endmacro(_set_relative_out_file_path)

function(_create_version_file LANG SOURCE INPUT)
  cmake_parse_arguments(
    CREATE
    ""
    ""
    "ADDITIONAL_OPTIONS"
    ${ARGN}
  )

  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs")
  file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/plxs/plxsversion")

  set(ENV{PYTHONPATH} "${DIR_OF_PLXSVERSION}/src:ENV{PYTHONPATH}")
  execute_process(
    COMMAND /usr/bin/env ${Python_EXECUTABLE} -m version_builder --lang ${LANG} --source ${SOURCE} --input ${INPUT} ${CREATE_ADDITIONAL_OPTIONS} "${CMAKE_CURRENT_BINARY_DIR}/${REL_OUT_PATH}"
		  RESULT_VARIABLE result)
  if(NOT ${result} EQUAL 0)
    message(FATAL_ERROR "Error running plxsversion tool. Return code is: ${result}")
  endif()
endfunction(_create_version_file)

# Load version string and write it to a cmake variable so it can be accessed from cmake.
function(_set_version_cmake_variable OUTPUT_VARIABLE)
  file(READ "${CMAKE_CURRENT_BINARY_DIR}/${REL_OUT_PATH}" VERSION_FILE_CONTENT)
  string(REGEX REPLACE ".*VERSION [{=] \"([^\"]*)\".*" "\\1" VERSION "${VERSION_FILE_CONTENT}")
  message(STATUS "Version from plxsversion: ${VERSION}")
  set(${OUTPUT_VARIABLE} "${VERSION}" CACHE INTERNAL "${OUTPUT_VARIABLE}")
endfunction(_set_version_cmake_variable)

# This function should be called from the CMakeLists.txt file that defines a library target that will include 
# the generated version file.
function(plxsversion_create_target)
  cmake_parse_arguments(
    VER
    "PRINT;TIME"
    "LANG;SOURCE;INPUT;TARGET_SUFFIX"
    ""
    ${ARGN}
  )

  set(OPTIONS "")
  if(VER_PRINT)
    list(APPEND OPTIONS "--print")
  endif()

  if(VER_TIME)
    list(APPEND OPTIONS "--time")
  endif()

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

  if(NOT VER_TARGET_SUFFIX)
    set(VERSION_LIBRARY plxsversion)
  else()
    set(VERSION_LIBRARY "plxsversion-${VER_TARGET_SUFFIX}")
  endif()

  _set_relative_out_file_path(${VER_LANG})
  _create_version_file(${VER_LANG} ${VER_SOURCE} ${VER_INPUT} ADDITIONAL_OPTIONS ${OPTIONS})

  add_library(${VERSION_LIBRARY} INTERFACE)
  target_include_directories(${VERSION_LIBRARY} 
    INTERFACE 
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/plxs>
      $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/plxs>)
  message(STATUS "${VERSION_LIBRARY} created.")

  set_property(TARGET ${VERSION_LIBRARY} APPEND PROPERTY ADDITIONAL_CLEAN_FILES "${CMAKE_CURRENT_BINARY_DIR}/${REL_OUT_PATH}")
  _set_version_cmake_variable(PLXSVERSION_STRING)
endfunction(plxsversion_create_target)