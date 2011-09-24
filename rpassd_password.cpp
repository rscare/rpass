extern "C" {
#include "rpass.h"
}
#include "rpassd_password.hxx"
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

void d_getRpassAccounts(const vector<string> &options, vector<char> &retval) {
    vector<string>::const_iterator i = options.begin();
    vector<string> fields;

    // First argument is filename
    string filename = *(i++);
    // Second argument indicates start/end of searchstring
    string search_start = *(i++);
    string sstring = "";
    for (; i < options.end(); ++i) {
        if (*i != search_start) {
            sstring.append(*i);
            sstring.append(" ");
        }
        else
            break;
    }
    sstring.erase(sstring.length() - 1); ++i;

    int flags = *((int *)((i++)->data()));

    for (; i < options.end(); ++i) {
        fields.push_back(*i);
    }

    rpass_parent *parent;

    getRpassAccounts(sstring.c_str(), &parent, filename.c_str(), flags, NULL);

    string retstring = rparentsToString(parent, fields);
    retval = vector<char>(retstring.begin(), retstring.end());

    freeRpassParents(parent);
}

void d_addRpassAccount(const vector<string> &opts, vector<char> &retval) {
    string err = "ERR";
    string noerr = "NOERR";

    vector<string>::const_iterator i = opts.begin();
    // First arg is filename
    string filename = *(i++);
    string account = "";

    for (; i < opts.end(); ++i) {
        account.append(*i); account.append(" ");
    }
    account.erase(account.length() - 1);

    rpass_parent *parent;
    searchStringForRpassParents(&parent, NULL, (void *)account.data(), account.length(), ALL_ACCOUNTS);
    addRpassParent(parent, filename.c_str());
    freeRpassParents(parent);
    retval = vector<char>(noerr.begin(), noerr.end());
}

string rparentsToString(const rpass_parent * const parent, const vector<string> &field) {
    const rpass_parent * cur = parent;
    const rpass_entry * rentry = NULL;
    string retval = "";
    while (cur) {
        retval.append("[");
        retval.append(cur->acname);
        retval.append("]");

        rentry = cur->first_entry;
        while (rentry) {
            if ((field.size() == 0) ||
                (find(field.begin(), field.end(), string(rentry->key)) != field.end())) {
                retval.append("\n");
                retval.append(rentry->key);
                retval.append("=");
                retval.append(rentry->value);
            }
            rentry = rentry->next_entry;
        }
        retval.append("\n");
        cur = cur->next_parent;
    }
    return retval;
}
