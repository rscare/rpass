extern "C" {
#include "rpass.h"
}
#include "rpass_sys_config.h"

#ifdef RPASS_SUPPORT
#include "rpassd_password.hxx"
#endif

#include "rpassd_signal_handlers.hxx"

#include <unistd.h>
#include <stddef.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <iostream>
#include <sstream>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cctype>
#include <gcrypt.h>

#define ALLOWED_CONNECTIONS 3

typedef void (*OPERATOR_FUNCTION)(const std::vector<std::string> &args, std::vector<char> &retval);

using namespace std;

void daemonize();
void close_std_fds();
void setupSocket();

vector<string> splitArgs(const string &args);

void setupOperators(map<string, OPERATOR_FUNCTION> &o);

void daemonize () {
    pid_t pid;

    if (getppid() == 1)
        return;

    pid = fork();
    if (pid < 0)
        exit(1);
    if (pid > 0)
        exit(0);

    if (setsid() < 0)
        exit(1);

    if (chdir("/tmp") < 0)
        exit(1);

    close_std_fds();
}

void close_std_fds() {
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
}

vector<string> splitArgs(const string &args) {
    vector<string> parsed_args;
    stringstream ss(args);
    string item;
    while (getline(ss, item, ' ')) {
        parsed_args.push_back(item);
    }
    return parsed_args;
}

void setupSocket() {
    unsigned int s1 = socket(AF_UNIX, SOCK_STREAM, 0), s2;
    sockaddr_un local;
    char buffer[BUFSIZ];
    string instructions = "";
    vector<char> retval;
    vector<string> args;
    ssize_t read_size;

    map<string, OPERATOR_FUNCTION>::iterator found;
    map<string, OPERATOR_FUNCTION> instructions_operator;

    setupOperators(instructions_operator);

    local.sun_family = AF_UNIX;
    strcpy(local.sun_path, SOCKET_NAME);
    unlink(local.sun_path);

    bind(s1, (struct sockaddr *)&local, strlen(local.sun_path) + sizeof(local.sun_family));
    listen(s1, ALLOWED_CONNECTIONS);

    while (1) {
        s2 = accept(s1, NULL, NULL);
        while ((read_size = recv(s2, buffer, BUFSIZ, 0)) > 0) {
            instructions.append(buffer, read_size);
            if (read_size < BUFSIZ)
                break;
        }

        if (instructions.length() > 0) {
            args = splitArgs(instructions);
            if (args[0] == RPASS_DAEMON_MSG_STOP)
                break;

            if ((found = instructions_operator.find(args[0])) != instructions_operator.end()) {
                args.erase(args.begin());
                found->second(args, retval);
                send(s2, (void *)&retval[0], retval.size(), 0);
            }
        }

        instructions = "";
        close(s2);
    }

    close(s1);
    unlink(local.sun_path);
}

void setupOperators(map<string, OPERATOR_FUNCTION> &o) {
    o[RPASS_DAEMON_MSG_DECRYPTFILE] = d_decryptFileToData;
    o[RPASS_DAEMON_MSG_ENCRYPTFILE] = d_encryptFile;
    o[RPASS_DAEMON_MSG_ENCRYPTDATATOFILE] = d_encryptDataToFile;
#ifdef RPASS_SUPPORT
    o[RPASS_DAEMON_MSG_GETACCOUNTS] = d_getRpassAccounts;
    o[RPASS_DAEMON_MSG_ADDACCOUNT] = d_addRpassAccount;
#endif
}

int main(int argc, char *argv[]) {
    bool foreground = false, verbose = false;

    if (argc > 1) {
        for (int c = 1; c < argc; ++c) {
            if ((string("--help") == argv[c]) || (string("-h") == argv[c])) {
                cout << "Options: [--foreground|-F] [--verbose|-v]" << endl;
                exit(0);
            }
            if ((string("--foreground") == argv[c]) || (string("-F") == argv[c])) {
                foreground = true;
            }
            if ((string("--verbose") == argv[c]) || (string("-v") == argv[c])) {
                verbose = true;
            }
        }
    }

    if (!foreground) {
        if (verbose)
            cout << "Daemonizing process..." << endl;
        daemonize();
    }

    if (verbose)
        cout << "Setting up socket..." << endl;

    setupSocket();

    return 0;
}
