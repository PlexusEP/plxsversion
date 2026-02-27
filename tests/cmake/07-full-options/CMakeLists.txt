cmake_minimum_required(VERSION 3.15)
project(full-options-test)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

plxsversion_create_target(
    LANG cpp
    TARGET_SUFFIX full
    NAMESPACE foo::bar
    INCLUDE_PREFIX my-includes/foo/bar
)

# Check that the custom CMake variable was set based on the suffix.
if(NOT DEFINED FULL_BASE_VERSION)
    message(FATAL_ERROR "TEST_FAIL: Custom base version variable 'FULL_BASE_VERSION' was not set.")
endif()

add_executable(full_app main.cpp)
target_link_libraries(full_app PRIVATE plxsversion-full)

# Add a test that checks if the configure step was successful.
add_test(
    NAME Full_Options_Configure_Check 
    COMMAND ${CMAKE_COMMAND} --build . --config $<CONFIG>
)
set_tests_properties(Full_Options_Configure_Check PROPERTIES 
    PASS_REGULAR_EXPRESSION "TEST_FAIL"
    WILL_FAIL true
)

# Add a test to verify the project builds, which implicitly tests the custom include path
add_test(NAME Full_Options_Build_Check COMMAND ${CMAKE_COMMAND} --build . --target full_app --config $<CONFIG>)
set_tests_properties(Full_Options_Build_Check PROPERTIES PASS_REGULAR_EXPRESSION "Built target full_app")
