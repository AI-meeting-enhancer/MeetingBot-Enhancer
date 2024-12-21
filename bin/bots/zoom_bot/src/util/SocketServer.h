#ifndef ZOOM_SDK_SOCKET_SERVER_H
#define ZOOM_SDK_SOCKET_SERVER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sstream>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <unistd.h>
#include <signal.h>
#include <pthread.h>

#include <iostream>

#include "Singleton.h"
#include "Log.h"

using namespace std;


class SocketServer : public Singleton<SocketServer> {
    friend class Singleton<SocketServer>;

    // const string c_socketPath = "./sock/meeting.sock";
    std::string c_socketPath = "./sock/meeting.sock";
    
    const int c_bufferSize = 1024;

    struct sockaddr_un m_addr;

    int m_listenSocket;
    int m_dataSocket = -1;

    pthread_t m_pid;
    pthread_mutex_t m_mutex;

    bool ready;

    void* run();
    static void* threadCreate(void* obj);
    static void threadKill(int sig, siginfo_t* info, void* ctx);

public:
    SocketServer();
    ~SocketServer();
    int start();
    void stop();

    int writeBuf(const unsigned char* buf, int len);
    int writeBuf(const char* buf, int len);
    int writeStr(const string& str);

    bool isReady();

    void cleanup();
};

#endif //ZOOM_SDK_SOCKET_SERVER_H
