cmake_minimum_required(VERSION 3.15)
project(lang-cpp11-test)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

plxsversion_create_target(LANG cpp11 TARGET_SUFFIX lang-cpp11)

add_executable(cpp11_app main.cpp)
target_link_libraries(cpp11_app PRIVATE plxsversion-lang-cpp11)

add_test(NAME CPP11_Lang_Build COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target cpp11_app --config $<CONFIG>)
set_tests_properties(CPP11_Lang_Build PROPERTIES PASS_REGULAR_EXPRESSION "Built target cpp11_app")
