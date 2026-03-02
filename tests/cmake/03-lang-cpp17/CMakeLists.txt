cmake_minimum_required(VERSION 3.15)
project(lang-cpp17-test)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_CURRENT_SOURCE_DIR}/../../../plxsversion.cmake)

plxsversion_create_target(LANG cpp TARGET_SUFFIX lang-cpp17)

add_executable(cpp17_app main.cpp)
target_link_libraries(cpp17_app PRIVATE plxsversion-lang-cpp17)

add_test(NAME CPP17_Lang_Build COMMAND ${CMAKE_COMMAND} --build ${CMAKE_BINARY_DIR} --target cpp17_app --config $<CONFIG>)
set_tests_properties(CPP17_Lang_Build PROPERTIES PASS_REGULAR_EXPRESSION "Built target cpp17_app")
