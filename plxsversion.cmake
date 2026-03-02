set(DIR_OF_PLXSVERSION "${CMAKE_CURRENT_LIST_DIR}" CACHE INTERNAL "DIR_OF_PLXSVERSION")

find_package(Python COMPONENTS Interpreter REQUIRED)

macro(_set_relative_out_file_path LANG CUSTOM_PATH)
  set(REL_OUT_PATH "plxs/${CUSTOM_PATH}/version.hpp")
  if(${LANG} STREQUAL "c")
    set(REL_OUT_PATH "plxs/${CUSTOM_PATH}/version.h")
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

# Generic function to load a specific variable from the version file and set it in CMake.
function(_set_version_cmake_variable OUTPUT_VARIABLE IN_FILE VAR_NAME)
  file(READ "${IN_FILE}" VERSION_FILE_CONTENT)
  # This regex now uses VAR_NAME to find the right line
  string(REGEX REPLACE ".*${VAR_NAME}[ {=]+ \"([^\"]*)\".*" "\\1" EXTRACTED_VALUE "${VERSION_FILE_CONTENT}")
  message(STATUS "CMake ${OUTPUT_VARIABLE} variable set to: ${EXTRACTED_VALUE}")
  set(${OUTPUT_VARIABLE} "${EXTRACTED_VALUE}" CACHE INTERNAL "${OUTPUT_VARIABLE}")
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

  if(NOT VER_INCLUDE_PREFIX)
    set(VER_INCLUDE_PREFIX "plxsversion")
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

  _set_relative_out_file_path(${VER_LANG} ${VER_INCLUDE_PREFIX})
  set(OUT_FILE "${CMAKE_CURRENT_BINARY_DIR}/${REL_OUT_PATH}")

  _create_version_file(${VER_LANG} ${VER_SOURCE} ${VER_INPUT} ${OUT_FILE} ADDITIONAL_OPTIONS ${OPTIONS})

  add_library(${VERSION_LIBRARY} INTERFACE)
  target_include_directories(${VERSION_LIBRARY}
    INTERFACE
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}/plxs>
      $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/plxs>)

  set_property(TARGET ${VERSION_LIBRARY} APPEND PROPERTY ADDITIONAL_CLEAN_FILES "${OUT_FILE}")

  if(VER_TARGET_SUFFIX)
    # If the user provided a suffix for the target, use it to set the VERSION and BASE_VERSION
    string(TOUPPER ${VER_TARGET_SUFFIX} VER_PREFIX)
    set(full_version_var ${VER_PREFIX}_VERSION)
    set(base_version_var ${VER_PREFIX}_BASE_VERSION)

    _set_version_cmake_variable(${full_version_var} ${OUT_FILE} "VERSION")
    _set_version_cmake_variable(${base_version_var} ${OUT_FILE} "BASE_VERSION")
  else()
    # Otherwise, maintain the old behavior for backward compatibility
    _set_version_cmake_variable(PLXSVERSION_STRING_VERSION ${OUT_FILE} "VERSION")
    _set_version_cmake_variable(PLXSVERSION_STRING_BASE_VERSION ${OUT_FILE} "BASE_VERSION")
  endif()

  message(STATUS "${VERSION_LIBRARY} created.")
endfunction(plxsversion_create_target)