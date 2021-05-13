/*   
   Workspace: Baabnq-Shell
   Author: EvilShibe
   Date: 12th May 
*/  

//  If you want to run code in baabnq, you can just use the compiler and the intepreter sitting in the folder 'code'
//  but the compiler and the intepreter are modified, so you won't get debug output. If you want the original files, you can download the 
//  compiler here: 'www.github.com/PyVa-exe/Baabnq-Compiler/' and the intepreter here: 'www.github.com/PyVa-exe/S1monsAssembly3-Interpreter-v3/'.

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Scanner;
import java.io.InputStreamReader;

public class BaabnqShell {
 
    public static void main(String[] args) {
        //print the introduce
        System.out.println();
        System.out.println("--- This is a inofficial Baabnq-'Shell' (it's literally just a test!) written by EvilShibe ---");
       
        //before starting the "shell" clear the file buffer
        clear();

        //start the "shell"
        boolean running = true;
        while(running) {
            System.out.print(">>");
            
            //get the input over the commandline
            String input = getInput();

            //catch commands for the "shell"
            //if the input is "clear()", then the screen is getting cleared
            if(input.equals("clear()")) {
                //run the clear command, that runs on windows, mac and linux
                run("@cls || clear");
                //continue the loop, so the command is not getting written into the file
                continue;

            //if the input is "exit()", then exit the program 
            }else if(input.equals("exit()")) {
                //before exiting the program, clear the file buffer
                clear();
                //exit the program with the errorcode 0
                System.exit(0);

            //if the input is "clearFile()", then clear the file
            }else if(input.equals("clearFile()")) {
                //clear the file with the clear() method
                clear();
                //continue the loop, so the command is not getting written into the file
                continue;
            }
            
            //if the input is not a command, write the line into the file buffer
            writeInput(input);

            //compile the file buffer over the commandline
            run("python3 code/Compiler_v4.3.py --input Code/shell.baabnq --output code/build");
            //interprete the file buffer over the commandline
            run("python3 code/S1monsAssembly3_Interpreter_v3_system_accurat.py --file code/build");
        }
    }

    //method for constantly getting input over the commandline
    private static String getInput() {
        Scanner inputScanner = new Scanner(System.in);
        
        //return the input
        return inputScanner.nextLine();
    }

    //write the command from getInput() into the file "shell.baabnq"
    private static void writeInput(String input) {
        try {
            //create a new instance of the file object
            File file = new File("code/shell.baabnq");
            
            //add a new PrintWriter to the file
            FileWriter fileWriter = new FileWriter(file, true);
            BufferedWriter bufferedWriter = new BufferedWriter(fileWriter);
            PrintWriter printWriter = new PrintWriter(bufferedWriter);

            //write a new line with the input into the file
            printWriter.println(input);

            //close the printWriter
            printWriter.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    //method for executing a command in the commandline
    private static void run(String command) {
        //saving the runtime in a object
        Runtime runtime = Runtime.getRuntime();
        try {
            //execute the command with the runtime
            Process process = runtime.exec(command);
            
            //save the inputStream of the process attached to a BufferedReader
            BufferedReader runtimeInput = new BufferedReader(new InputStreamReader(process.getInputStream()));

            //safe the errorStream of the process attached to a BufferedReader
            BufferedReader runtimeError = new BufferedReader(new InputStreamReader(process.getErrorStream()));

            String input = "";

            //print the "output" of the command which was executed
            while((input = runtimeInput.readLine()) != null) {
                System.out.println(input);
            }
            
            //print the errors of the command which was executed
            while ((input = runtimeError.readLine()) != null) {
                System.out.println(input);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    //method that will clear the file
    private static void clear() {
        //create a new object of the file
        File file = new File("code/shell.baabnq");

        try {
            //make a new FileWriter with the file attached
            FileWriter fileWriter = new FileWriter(file);
            
            //overwrite the file with nothing so the file is "empty"
            fileWriter.write("");

            //close the fileWriter
            fileWriter.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
} 