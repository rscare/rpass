cmake_minimum_required (VERSION 2.8.5)
project (rpassd)

include("${CMAKE_SOURCE_DIR}/../cmake/rpass.cmake")

add_executable(rpassd rpassd.cpp rpassd_password.cpp rpassd_signal_handlers.cpp)

find_package(Librpass)

include_directories(${LIBRPASS_INCLUDE_DIR})
target_link_libraries(rpassd ${LIBRPASS_LIBRARIES})

install(TARGETS rpassd RUNTIME DESTINATION bin)
