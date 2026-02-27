cmake_minimum_required(VERSION 3.15)
project(target-suffix-test)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

plxsversion_create_target(TARGET_SUFFIX my-app)

# Check if the custom target exists
if(NOT TARGET plxsversion-my-app)
    message(FATAL_ERROR "TEST_FAIL: Custom target 'plxsversion-my-app' was not created.")
endif()

# Check that the default target does NOT exist
if(TARGET plxsversion)
    message(FATAL_ERROR "TEST_FAIL: Default target 'plxsversion' was created when a suffix was provided.")
endif()

# This test simply re-runs the configure step and checks its output.
add_test(
    NAME Target_Suffix_Check
    COMMAND ${CMAKE_COMMAND} --build . --config $<CONFIG>
)

set_tests_properties(Target_Suffix_Check PROPERTIES 
    PASS_REGULAR_EXPRESSION "TEST_FAIL"
    WILL_FAIL true
)
