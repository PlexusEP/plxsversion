cmake_minimum_required(VERSION 3.15)
project(cmake-interface-tests)

include(CTest)
enable_testing()

message(STATUS "Configuring CMake tests for plxsversion...")

# Get all the subdirectories that represent our tests, sorted alphabetically
file(GLOB test_cases LIST_DIRECTORIES true "*")
list(SORT test_cases)

foreach(test_case ${test_cases})
  if(IS_DIRECTORY "${test_case}")
    # Each subdirectory is a standalone CMake project test
    message(STATUS "Adding test case: ${test_case}")
    add_subdirectory("${test_case}")
  endif()
endforeach()

message(STATUS "Finished configuring CMake tests.")
