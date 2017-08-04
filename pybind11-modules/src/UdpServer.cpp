#include "UdpServer.h"

UdpServer::UdpServer(unsigned int port) : run_thread() {
    slen = sizeof(si_client);

    Feedback = reinterpret_cast<RemoteFeedback*>(rx_buff);
    Control = reinterpret_cast<RemoteControl*>(tx_buff);

    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        std::cout << "WSA Startup Failed. Error Code: " <<  WSAGetLastError() << std::endl;
        WSACleanup();
        exit(EXIT_FAILURE);
    }

    if ((sock = (socket(AF_INET, SOCK_DGRAM, 0))) == INVALID_SOCKET)
    {
        std::cout << "Could not create socket: " << WSAGetLastError() << std::endl;
        WSACleanup();
        exit(EXIT_FAILURE);
    }
    std::cout << "Socket created" << std::endl;

    si_server.sin_family = AF_INET;
    si_server.sin_addr.s_addr = INADDR_ANY;
    si_server.sin_port = htons(port);

    if (bind(sock, (struct sockaddr*) &si_server, sizeof(si_server)) == SOCKET_ERROR)
    {
        std::cout << "Bind failed with error code: " << WSAGetLastError() << std::endl;
        WSACleanup();
        exit(EXIT_FAILURE);
    }
    std::cout << "Socket bind done" << std::endl;
}

UdpServer::~UdpServer() {
    close();
}

void UdpServer::run() {
    while (running) {
        mtx.lock();
        rx_size = recvfrom(sock, rx_buff, sizeof(rx_buff), 0, (struct sockaddr*) &si_client, &slen);
        mtx.unlock();

        if (rx_size == SOCKET_ERROR) {
            std::cout << "recvfrom() failed with error code: " << WSAGetLastError() << std::endl;
            WSACleanup();
            exit(EXIT_FAILURE);
        }

        mtx.lock();
        tx_size = sendto(sock, tx_buff, sizeof(tx_buff), 0, (struct sockaddr*) &si_client, slen);
        mtx.unlock();

        if (tx_size == SOCKET_ERROR) {
            std::cout << "sendto() failed with error code: " << WSAGetLastError() << std::endl;
            WSACleanup();
            exit(EXIT_FAILURE);
        }
    }
}

void UdpServer::start() {
    running = true;
    run_thread = std::thread(&UdpServer::run, this);
}

void UdpServer::close() {
    running = false;
    if (run_thread.joinable()) {
        run_thread.join();
        std::cout << "UDP thread joined sucessfully!" << std::endl;

        WSACleanup();
        closesocket(sock);
    }
}