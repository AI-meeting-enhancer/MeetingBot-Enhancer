#include "SocketServer.h"

// Constructor: Initialize the mutex for thread safety
SocketServer::SocketServer() {
    pthread_mutex_init(&m_mutex, NULL);
}

// Destructor: Cleanup resources when the object is destroyed
SocketServer::~SocketServer() {
    cleanup();
}

// Static function to create a new thread that executes the run method
void* SocketServer::threadCreate(void *obj) {
    return reinterpret_cast<SocketServer*>(obj)->run();
}

// Signal handler to stop the server gracefully
void SocketServer::threadKill(int sig, siginfo_t *info, void *ctx) {
    auto* self = &SocketServer::getInstance();  // Retrieve singleton instance
    self->stop();
}

// Main thread function for the socket server
void* SocketServer::run() {
    // Try to lock the mutex to ensure single-threaded execution
    if (pthread_mutex_trylock(&m_mutex) != 0) {
        Log::error("Unable to lock mutex");
        return nullptr;
    }

    // Cleanup any existing resources before starting
    cleanup();

    // Create a Unix domain socket
    m_listenSocket = socket(AF_UNIX, SOCK_STREAM, 0);
    if (m_listenSocket == -1) {
        Log::error("Unable to create listen socket");
        return nullptr;
    }

    // Zero out the sockaddr structure
    memset(&m_addr, 0, sizeof(struct sockaddr_un));

    // Configure the socket address
    m_addr.sun_family = AF_UNIX;
    strncpy(m_addr.sun_path, c_socketPath.c_str(), sizeof(m_addr.sun_path) - 1);

    // Bind the socket to the address
    auto ret = bind(m_listenSocket, (const struct sockaddr *) &m_addr, sizeof(struct sockaddr_un));
    if (ret == -1) {
        Log::error("Unable to bind socket");
        return nullptr;
    }

    // Start listening for incoming connections
    ret = listen(m_listenSocket, 20);
    if (ret == -1) {
        Log::error("Unable to listen on socket");
        return nullptr;
    }

    Log::info("Started socket server");
    Log::info("Listening on socket " + c_socketPath);

    char buffer[c_bufferSize];

    // Main loop: Wait for and accept incoming connections
    for (;;) {
        Log::info("Waiting for Socket Connection");
        m_dataSocket = accept(m_listenSocket, NULL, NULL);  // Accept a new connection
        stringstream writeInfo;
        writeInfo << "Socket Accepted: " << m_dataSocket;
        Log::success(writeInfo.str());
        if (m_dataSocket == -1) {
            Log::error("Failed to accept connection");
            return nullptr;
        }
        // Keep the loop running indefinitely
    }

    return nullptr;
}

// Check if the socket server is ready
bool SocketServer::isReady() {
    return ready;
}

// Write a buffer of data to the socket
int SocketServer::writeBuf(const char* buf, int len) {
    if (m_dataSocket > 0) {
        auto ret = write(m_dataSocket, buf, len);
        // Uncomment the following lines for error handling
        /*
        if (ret == -1) {
            stringstream writeInfo;
            writeInfo << "Failed to write data by socket server: " << m_dataSocket;
            Log::error(writeInfo.str());
        }
        */
    }
    return 0;
}

// Write a buffer of unsigned char data to the socket
int SocketServer::writeBuf(const unsigned char* buf, int len) {
    auto ret = write(m_dataSocket, buf, len);
    if (ret == -1) {
        Log::error("Failed to write data");
        exit(EXIT_FAILURE);
    }

    return 0;
}

// Write a string to the socket
int SocketServer::writeStr(const string& str) {
    auto buf = str.c_str();
    return writeBuf(buf, strlen(buf));
}

// Cleanup old socket files and other resources
void SocketServer::cleanup() {
    Log::info("Checking Access for Unix Socket");
    if (access(c_socketPath.c_str(), F_OK) != -1) {
        Log::info("SockPath Already Exists...");
        unlink(c_socketPath.c_str());  // Remove old socket file
        Log::info("Old SockPath deleted...");
    }
}

// Start the socket server in a new thread
int SocketServer::start() {
    if (pthread_create(&m_pid, NULL, &(SocketServer::threadCreate), this) != 0) {
        Log::error("Unable to start thread");
        return false;
    }
    return true;
}

// Stop the socket server and release resources
void SocketServer::stop() {
    pthread_mutex_destroy(&m_mutex);  // Destroy the mutex
    if (m_pid) {
        pthread_cancel(m_pid);  // Cancel the server thread
        m_pid = 0;
    }
    if (m_listenSocket) {
        close(m_listenSocket);  // Close the listening socket
        m_listenSocket = 0;
    }
    if (m_dataSocket) {
        close(m_dataSocket);  // Close the active data socket
        m_dataSocket = 0;
    }

    Log::info("Stopped Socket Server");
    cleanup();  // Perform additional cleanup
}
