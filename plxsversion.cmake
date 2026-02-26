set(DIR_OF_PLXSVERSION "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "DIR_OF_PLXSVERSION")

find_package(Python COMPONENTS Interpreter REQUIRED)

macro(_set_relative_out_file_path LANG)
  set(REL_OUT_PATH "plxs/plxsversion/version.hpp")
  if(${LANG} STREQUAL "c")
    set(REL_OUT_PATH "plxs/plxsversion/version.h")
  endif()
endmacro(_set_relative_out_file_path)

function(_create_version_file LANG SOURCE INPUT OUT_FILE)
  cmake_parse_arguments(
    CREATE
    ""
    ""
    "ADDITIONAL_OPTIONS"
    ${ARGN}
  )

  get_filename_component(OUT_DIR "${OUT_FILE}" DIRECTORY)
  file(MAKE_DIRECTORY "${OUT_DIR}")

  set(ENV{PYTHONPATH} "${DIR_OF_PLXSVERSION}/src:ENV{PYTHONPATH}")
  execute_process(
    COMMAND /usr/bin/env ${Python_EXECUTABLE} -m version_builder --lang ${LANG} --source ${SOURCE} --input ${INPUT} ${CREATE_ADDITIONAL_OPTIONS} "${OUT_FILE}"
		  RESULT_VARIABLE result)
  if(NOT ${result} EQUAL 0)
    file(REMOVE "${OUT_FILE}")
    message(FATAL_ERROR "Error running plxsversion tool. Return code is: ${result}")
  endif()
endfunction(_create_version_file)

# Load version string and write it to a cmake variable so it can be accessed from cmake.
function(_set_version_cmake_variable OUTPUT_VARIABLE IN_FILE)
  file(READ "${IN_FILE}" VERSION_FILE_CONTENT)
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
    "LANG;SOURCE;INPUT;TARGET_SUFFIX;NAMESPACE;INCLUDE_PREFIX"
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

  if(VER_NAMESPACE)
    list(APPEND OPTIONS "--namespace" ${VER_NAMESPACE})
    
  endif()

  if(VER_INCLUDE_PREFIX)
    list(APPEND OPTIONS "--include-prefix" ${VER_INCLUDE_PREFIX})
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

  if(VER_INCLUDE_PREFIX)
    set(REL_OUT_PATH "version.hpp")
    if(${VER_LANG} STREQUAL "c")
      set(REL_OUT_PATH "version.h")
    endif()
    set(INCLUDE_DIR ${CMAKE_CURRENT_BINARY_DIR})
  else()
    _set_relative_out_file_path(${VER_LANG})
    set(INCLUDE_DIR ${CMAKE_CURRENT_BINARY_DIR}/plxs)
  endif()

  set(OUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/${REL_OUT_PATH}")
  _create_version_file(${VER_LANG} ${VER_SOURCE} ${VER_INPUT} ${OUT_FILE} ADDITIONAL_OPTIONS ${OPTIONS})

  add_library(${VERSION_LIBRARY} INTERFACE)
  target_include_directories(${VERSION_LIBRARY}
    INTERFACE
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
      $<BUILD_INTERFACE:${INCLUDE_DIR}>)
  message(STATUS "${VERSION_LIBRARY} created.")

  set_property(TARGET ${VERSION_LIBRARY} APPEND PROPERTY ADDITIONAL_CLEAN_FILES "${OUT_FILE}")
  if(VER_INCLUDE_PREFIX)
    set(VERSION_FILE "${CMAKE_CURRENT_BINARY_DIR}/${VER_INCLUDE_PREFIX}/version.hpp")
    if(${VER_LANG} STREQUAL "c")
      set(VERSION_FILE "${CMAKE_CURRENT_BINARY_DIR}/${VER_INCLUDE_PREFIX}/version.h")
    endif()
    _set_version_cmake_variable(PLXSVERSION_STRING ${VERSION_FILE})
  else()
    _set_version_cmake_variable(PLXSVERSION_STRING ${OUT_FILE})
  endif()
endfunction(plxsversion_create_target)