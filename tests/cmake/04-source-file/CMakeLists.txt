cmake_minimum_required(VERSION 3.15)
project(source-file-test)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

# Create a dummy version file
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/version.txt "3.2.1-beta")

plxsversion_create_target(
    SOURCE file
    INPUT ${CMAKE_CURRENT_BINARY_DIR}/version.txt
    TARGET_SUFFIX source-file
)

# This check runs at configure time. CTest will check the output of this run.
if(NOT SOURCE-FILE_BASE_VERSION STREQUAL "3.2.1")
    message(FATAL_ERROR "TEST_FAIL: BASE_VERSION variable was not set correctly! Got: ${SOURCE-FILE_BASE_VERSION}")
endif()

# This test simply re-runs the configure step and checks its output.
add_test(
    NAME Source_File_Variable_Check 
    COMMAND ${CMAKE_COMMAND} --build . --config $<CONFIG>
)

# CTest will pass this test if the "TEST_FAIL" string is NOT found in the configure output.
set_tests_properties(Source_File_Variable_Check PROPERTIES 
    PASS_REGULAR_EXPRESSION "TEST_FAIL"
    WILL_FAIL true
)
