cmake_minimum_required (VERSION 2.8.5)
project (rpassd)

add_executable(rpassd rpassd.cpp rpassd_password.cpp rpassd_signal_handlers.cpp)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/../cmake/Modules/")

find_package(Librpass)

include_directories(${LIBRPASS_INCLUDE_DIR})
target_link_libraries(rpassd ${LIBRPASS_LIBRARIES})

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE Debug)
endif (NOT CMAKE_BUILD_TYPE)

install(TARGETS rpassd DESTINATION bin)
