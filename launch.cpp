/********************************************************
 * 	This is a Launch Script for the PfandApp	*
 * 		   Written 24.03.2025			*
 * 		C++ V20 / BUILD 1 / COPY		*
 *******************************************************/


// build this project with
// g++ launch.cpp -O PfandApp 
// or something else



#include <complex>
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <string>
#include <iomanip>  // For formatting output
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

void print_tui_header() {
    std::cout << "+------------------------+----------------------+\n";
    std::cout << "| Statistic              | Value                |\n";
    std::cout << "+------------------------+----------------------+\n";
}

void print_tui_footer() {
    std::cout << "+------------------------+----------------------+\n";
}

void print_stat(const std::string& stat_name, const std::string& value) {
    std::cout << "| " << std::setw(22) << std::left << stat_name
              << "| " << std::setw(20) << std::left << value << "|\n";
}


void print_ascii_art() {
    std::string ascii_art[] = {
        "██████╗ ███████╗ █████╗ ███╗   ██╗██████╗  █████╗ ██████╗ ██████╗ ",
        "██╔══██╗██╔════╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗",
        "██████╔╝█████╗  ███████║██╔██╗ ██║██║  ██║███████║██████╔╝██████╔╝",
        "██╔═══╝ ██╔══╝  ██╔══██║██║╚██╗██║██║  ██║██╔══██║██╔═══╝ ██╔═══╝ ",
        "██║     ██║     ██║  ██║██║ ╚████║██████╔╝██║  ██║██║     ██║     ",
        "╚═╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝     ",
        "                                                                  ",
        "██╗   ██╗   ██████╗ ███████╗   ███████╗██████╗    ███████╗        ",
        "██║   ██║  ██╔════╝ ██╔════╝   ██╔════╝╚════██╗   ██╔════╝        ",
        "██║   ██║  ███████╗ ███████╗   ███████╗ █████╔╝   ███████╗        ",
        "╚██╗ ██╔╝  ██╔═══██╗╚════██║   ╚════██║ ╚═══██╗   ╚════██║        ",
        " ╚████╔╝██╗╚██████╔╝███████║██╗███████║██████╔╝██╗███████║        ",
        "  ╚═══╝ ╚═╝ ╚═════╝ ╚══════╝╚═╝╚══════╝╚═════╝ ╚═╝╚══════╝        "
    };

    std::cout << "\n";
    std::cout << "\033[1;32m"; // Green text color

    // Printing the top of the box
    std::cout << "╔════════════════════════════════════════════════════════════════════╗\n";

    // Printing the ASCII art
    for (const std::string& line : ascii_art) {
        std::cout << "║ " << line << " ║\n";
#ifdef _WIN32
        Sleep(50);  // Slow down printing for retro effect
#else
        usleep(50000);  // Sleep for 50 milliseconds for retro effect
#endif
    }

    // Printing the bottom of the box
    std::cout << "╚════════════════════════════════════════════════════════════════════╝\n";
    std::cout << "\033[0m"; // Reset text color to default
}


int main(int argc, char *argv[]) {
    std::string full_work_dir;
    std::string command;
    std::string pid_file;
    bool secret = false;

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
    command = "python3 " + full_work_dir + "/main.py & echo $! > /tmp/pfand_pid";  // Correctly capturing the PID
    pid_file = "/tmp/pfand_pid";
    chdir(full_work_dir.c_str());
#endif

    // Print the retro-style ASCII art
    print_ascii_art();

    for (int i = 1; i < argc; i++) {
	    std::string arg = argv[i];
	    if (arg == "-S") {
		    secret = true;
		    std::cout << "ur mom gay xD\n\a";
	    }
    }

    // Start the Python script in the background and capture the process PID.
    int ret_code = std::system(command.c_str());
    if (ret_code != 0) {
        std::cerr << "Error: Failed to execute " << command << "\n";
        return 1;
    }

    std::cout << "Python process started in the background. PID stored in " << pid_file << "\n";

#ifdef _WIN32
    Sleep(1000);
#else
    sleep(1);
#endif

    // Read the PID of the Python process.
    std::ifstream pid_stream(pid_file);
    int pid;
    if (pid_stream >> pid) {
        std::cout << "Tracking Python process " << pid << "...\n";

        // Define the command to get the stats of the Python process.
#ifdef _WIN32
        std::string stats_command = "wmic process where ProcessId=" + std::to_string(pid) + " get ProcessId,WorkingSetSize,KernelModeTime,UserModeTime /format:csv > C:\\pfand\\pfand_stats";
#else
        std::string stats_command = "top -b -n 1 -p " + std::to_string(pid) + " | tail -n +8 | awk '$1=='" + std::to_string(pid) + "' {print $9, $10, $1, $2, $5, $6}' > /tmp/pfand_stats";
#endif
        std::system(stats_command.c_str());

        // Wait for the Python process to finish by checking if it's still running
        bool process_running = true;
        while (process_running) {
#ifdef _WIN32
            std::string check_command = "tasklist /FI \"PID eq " + std::to_string(pid) + "\"";
            FILE* pipe = _popen(check_command.c_str(), "r");
            if (!pipe) {
                std::cerr << "Error: Failed to check process status.\n";
                return 1;
            }

            char buffer[128];
            std::string result = "";
            while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
                result += buffer;
            }
            _pclose(pipe);

            if (result.find(std::to_string(pid)) == std::string::npos) {
                process_running = false;
            }
#else
            std::string check_command = "ps -p " + std::to_string(pid) + " > /dev/null";
            ret_code = std::system(check_command.c_str());
            if (ret_code != 0) {
                process_running = false;
            }
#endif
            sleep(1);  // Wait for 1 second before checking again
        }

        // Now that the process has finished, collect stats from the stats file.
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
            // Output TUI
            print_tui_header();

            // Display CPU Usage
            print_stat("CPU Usage (%)", std::to_string(total_cpu / count));

            // Display Average RAM Usage (MiB)
#ifdef _WIN32
            double total_mem_mib = total_mem / (1024 * 1024);  // Convert from bytes to MiB
            print_stat("Average RAM Usage", std::to_string(total_mem_mib) + " MiB");
#else
            double total_mem_mib = total_mem / 1024.0;  // Convert from KiB to MiB
            print_stat("Average RAM Usage", std::to_string(total_mem_mib) + " MiB");
#endif

            // Display Thread Count
            print_stat("Thread Count", std::to_string(count)); // Placeholder for actual thread count

            print_tui_footer();
        } else {
            std::cerr << "Error: No usage data collected.\n";
        }
    } else {
        std::cerr << "Error: Failed to read PID from file\n";
    }

    return 0;
}

