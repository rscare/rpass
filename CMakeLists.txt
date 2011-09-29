cmake_minimum_required (VERSION 2.8.5)
project (rpassd)

if (NOT CMAKE_BUILD_TYPE)
  set (CMAKE_BUILD_TYPE Release)
endif (NOT CMAKE_BUILD_TYPE)

add_executable(rpassd rpassd.cpp rpassd_password.cpp rpassd_signal_handlers.cpp)

find_package(Librpass)

include_directories(${LIBRPASS_INCLUDE_DIR})
target_link_libraries(rpassd ${LIBRPASS_LIBRARIES})

install(TARGETS rpassd RUNTIME DESTINATION bin)
