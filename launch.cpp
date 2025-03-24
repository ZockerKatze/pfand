/********************************************************
 * 	This is a Launch Script for the PfandApp	*
 * 		   Written 24.03.2025			*
 * 		C++ V20 / BUILD 1 / COPY		*
 *******************************************************/

#include <iostream>
#include <cstdlib>
#include <unistd.h>
#include <fstream>

int main() {
    // Define the working directory and the command
    const char* work_dir = getenv("HOME");
    if (!work_dir) {
        std::cerr << "Error: HOME environment variable not found.\n";
        return 1;
    }

    std::string full_work_dir = std::string(work_dir) + "/pfand";
    std::string command = "python3 " + full_work_dir + "/main.py & echo $! > /tmp/pfand_pid"; // Run in background and store PID

    // Change the working directory
    if (chdir(full_work_dir.c_str()) != 0) {
        std::cerr << "Error: Failed to change directory to " << full_work_dir << "\n";
        return 1;
    }

    // Launch the Python script in the background and store PID
    int ret_code = std::system(command.c_str());
    if (ret_code != 0) {
        std::cerr << "Error: Failed to execute " << command << "\n";
        return 1;
    }

    std::cout << "Process started in the background. PID stored in /tmp/pfand_pid\n";

    // Wait for the process to finish
    //
    // This doesnt really work!
    

    sleep(1); // Allow time for PID file creation
    std::ifstream pid_file("/tmp/pfand_pid");
    int pid;
    if (pid_file >> pid) {
        std::cout << "Tracking process " << pid << "...\n";

        // Monitor CPU and RAM usage
        std::string track_command = "top -b -d 1 -p " + std::to_string(pid) + " | awk '/" + std::to_string(pid) + "/ {print $9, $10}' > /tmp/pfand_stats &";
        std::system(track_command.c_str());

        // Wait for the process to complete
        std::string wait_command = "wait " + std::to_string(pid);
        std::system(wait_command.c_str());

        // Collect usage details
        std::ifstream stats_file("/tmp/pfand_stats");
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

