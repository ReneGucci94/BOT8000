import subprocess
import re

def main():
    # Use command_status output if I could... but I can only run commands.
    # I can't capture the background process output from a new command easily without a temporary file.
    # But wait, I have the background command ID. 
    # The system doesn't provide a way to 'cat' the background proc's stdout from a shell command.
    pass

if __name__ == "__main__":
    main()
