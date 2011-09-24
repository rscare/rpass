#ifndef RPASSD_SIGNAL_HANDLERS_H
#define RPASSD_SIGNAL_HANDLERS_H

#include <vector>
#include <string>

void d_encryptDataToFile(const std::vector<std::string> &args, std::vector<char> &retval);
void d_decryptFileToData(const std::vector<std::string> &filename, std::vector<char> &retval);
void d_encryptFile(const std::vector<std::string> &filenames, std::vector<char> &retval);

#endif
