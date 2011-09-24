#ifndef RPASSD_PASSWORD_H
#define RPASSD_PASSWORD_H

#include "rpass.h"
#include <string>
#include <vector>

void d_getRpassAccounts(const std::vector<std::string> &options, std::vector<char> &retval);
void d_addRpassAccount(const std::vector<std::string> &account, std::vector<char> &retval);
std::string rparentsToString(const rpass_parent * const parent, const std::vector<std::string> &field);

#endif
