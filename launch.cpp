/********************************************************
 * 	This is a Launch Script for the PfandApp	*
 * 		   Written 24.03.2025			*
 * 		C++ V20 / BUILD 1 / COPY		*
 *******************************************************/

#include <iostream>
#include <cstdlib>
#include <fstream>
#ifdef _WIN32
    #include <windows.h>
#else
    #include <unistd.h>
#endif

int main() {
    std::string full_work_dir;
    std::string command;
    std::string pid_file;

#ifdef _WIN32
    full_work_dir = "C:\\pfand";
    command = "start /B python " + full_work_dir + "\\main.py > C:\\pfand\\pfand_pid";
    pid_file = "C:\\pfand\\pfand_pid";
    SetCurrentDirectory(full_work_dir.c_str());
#else
    const char* home_dir = getenv("HOME");
    if (!home_dir) {
        std::cerr << "Error: HOME environment variable not found.\n";
        return 1;
    }
    full_work_dir = std::string(home_dir) + "/pfand";
    command = "python3 " + full_work_dir + "/main.py & echo $! > /tmp/pfand_pid";
    pid_file = "/tmp/pfand_pid";
    chdir(full_work_dir.c_str());
#endif

    int ret_code = std::system(command.c_str());
    if (ret_code != 0) {
        std::cerr << "Error: Failed to execute " << command << "\n";
        return 1;
    }

    std::cout << "Process started in the background. PID stored in " << pid_file << "\n";

#ifdef _WIN32
    Sleep(1000);
#else
    sleep(1);
#endif

    std::ifstream pid_stream(pid_file);
    int pid;
    if (pid_stream >> pid) {
        std::cout << "Tracking process " << pid << "...\n";
#ifdef _WIN32
        std::string stats_command = "wmic process where ProcessId=" + std::to_string(pid) + " get ProcessId,WorkingSetSize,KernelModeTime,UserModeTime /format:csv > C:\\pfand\\pfand_stats";
#else
        std::string stats_command = "top -b -d 1 -p " + std::to_string(pid) + " | awk '/" + std::to_string(pid) + "/ {print $9, $10}' > /tmp/pfand_stats &";
#endif
        std::system(stats_command.c_str());

#ifdef _WIN32
        std::string wait_command = "timeout /t 5";
#else
        std::string wait_command = "wait " + std::to_string(pid);
#endif
        std::system(wait_command.c_str());

        std::ifstream stats_file(pid_file);
        double total_cpu = 0, total_mem = 0;
        int count = 0;
        double cpu, mem;
        while (stats_file >> cpu >> mem) {
            total_cpu += cpu;
            total_mem += mem;
            count++;
        }
        stats_file.close();

        if (count > 0) {
            std::cout << "Process finished.\n";
            std::cout << "Average CPU Usage: " << (total_cpu / count) << "%\n";
            std::cout << "Average RAM Usage: " << (total_mem / count) << "%\n";
        } else {
            std::cerr << "Error: No usage data collected.\n";
        }
    } else {
        std::cerr << "Error: Failed to read PID from file\n";
    }
    
    return 0;
}

