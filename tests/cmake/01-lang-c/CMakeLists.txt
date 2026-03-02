cmake_minimum_required(VERSION 3.15)
project(lang-c-test)

# Include the plxsversion.cmake script from the project root
include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

# Call the function with specific options for this test
plxsversion_create_target(LANG c TARGET_SUFFIX lang-c)

# Create a dummy executable that links against the version library
add_executable(c_app main.c)
target_link_libraries(c_app PRIVATE plxsversion-lang-c)

# Add a test to verify that this specific target builds successfully
add_test(NAME C_Lang_Build COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target c_app --config $<CONFIG>)
set_tests_properties(C_Lang_Build PROPERTIES PASS_REGULAR_EXPRESSION "Built target c_app")
