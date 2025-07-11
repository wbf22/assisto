#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>

/*

valgrind --leak-check=full --show-leak-kinds=all ./test_exe

leaks -atExit -- ./test_exe
*/

void run_command(char* command, char* out, size_t output_size, int print) {
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        perror("popen");
        return;
    }

    // Read the output 
    while(fgets(out, output_size, fp) != NULL) {
        if (print) {
            printf("%s\n", out);
        }
    }

    // Close the file pointer
    pclose(fp);
}

int main() {
    
    /*
    
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install python

        python3 -m venv env
        source env/bin/activate
        pip install fastapi uvicorn

        uvicorn editor:app --reload
    */

    // home brew
    char buffer[1024];
    run_command("brew --version", buffer, 1024, 0);
    if(strncmp(buffer, "Homebrew", 8) != 0) {
        printf("\n\nINSTALLING HOMEBREW\n\n");
        run_command("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", buffer, 1024, 1);
    }

    // python
    run_command("python3 --version", buffer, 1024, 0);
    if(strncmp(buffer, "Python 3", 8) != 0) {
        printf("\n\nINSTALLING PYTHON\n\n");
        run_command("brew install python", buffer, 1024, 1);
    }

    // install FastAPI
    char* dir = "./your_website";
    if (chdir(dir) != 0) {
        perror("Your website directory is missing!");
        return 1;
    }
    printf("\n\nINSTALLING FastAPI\n\n");
    run_command("python3 -m venv env", buffer, 1024, 1);
    run_command("source env/bin/activate", buffer, 1024, 1);
    run_command("pip3 install fastapi uvicorn", buffer, 1024, 1);

    // start server
    run_command("python3 server.py", buffer, 1024, 1);

    int loop = 1;
    while(loop) {
        sleep(10);
    }


    return 0;
}
