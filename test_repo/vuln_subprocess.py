import subprocess

user_input = input("Command: ")

subprocess.run(
    user_input,
    shell=True
)
