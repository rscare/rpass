extern "C" {
#include "rpass.h"
}

#include "rpassd_signal_handlers.hxx"
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

void d_encryptDataToFile(const vector<string> &args, vector<char> &retval) {
    string noerr = "NOERR";
    string err = "ERR";
    vector<string>::const_iterator i = args.begin();

    string filename = *i;
    string data = "";
    for (++i; i < args.end(); ++i) {
        data.append(i->data(), i->length()); data.append(" ");
    }
    data.erase(data.length() - 1);
    encryptDataToFile(data.data(), data.length(), filename.c_str());
    retval = vector<char>(noerr.begin(), noerr.end());
}

void d_decryptFileToData(const vector<string> &filename, vector<char> &retval) {
    char *data = NULL;
    size_t data_size;
    decryptFileToData(filename[0].c_str(), (void **)&data, &data_size);
    retval.resize(data_size);
    copy(data, data + data_size, retval.begin());
    gcry_free(data);
}

void d_encryptFile(const vector<string> &filenames, vector<char> &retval) {
    string noerr = "NOERR";
    string err = "ERR";

    if (filenames.size() == 1) {
        encryptFile(filenames[0].c_str(), NULL);
        retval = vector<char>(noerr.begin(), noerr.end());
    }
    else if (filenames.size() == 2) {
        encryptFile(filenames[0].c_str(), filenames[1].c_str());
        retval = vector<char>(noerr.begin(), noerr.end());
    }
    retval = vector<char>(err.begin(), err.end());
}

void d_forgetCipher(const vector<string> &opts, vector<char> &retval) {
    string noerr = "NOERR";
    forgetCipher();
    retval = vector<char>(noerr.begin(), noerr.end());
}

void d_changePassphrase(const vector<string> &filename, vector<char> &retval) {
    string noerr = "NOERR";
    changePassphrase(filename[0].c_str());
    retval = vector<char>(noerr.begin(), noerr.end());
}
