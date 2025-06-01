#!/usr/bin/env python3
import paramiko
import time
import csv
import os
import json
from otii_tcp_client import otii_client

class AppException(Exception):
    '''Application Exception'''

def run_benchmarks(otii, device, project, rpi, linux, version, hostname, username, password):
    # Define command to run script
    command = "bash Python_Application_Energy_Consumption/scripts/experiment/run_benchmarks.sh " + version

    try:
        # Create an SSH client
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the SSH server
        print(f"Connecting to {username}@{hostname}...")
        ssh_client.connect(hostname, username=username, password=password)
        print("Connection established.")

        # print(f"Running command: {version} -m pyperf system tune")
        # stdin, stdout, stderr = ssh_client.exec_command(f"sudo {version} -m pyperf system tune")

        # # Wait for the command to complete and fetch outputs
        # exit_status = stdout.channel.recv_exit_status()
        # print(f"Command completed with exit status: {exit_status}")

        # Execute the command
        project.start_recording()
        print(f"Running command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Wait for the command to complete and fetch outputs
        exit_status = stdout.channel.recv_exit_status()
        print(f"Command completed with exit status: {exit_status}")
        project.stop_recording()

        # Print the standard output and error
        # print("Standard Output:")
        # for line in stdout.read().decode().splitlines():
        #     print(line)

        print("Standard Error:")
        for line in stderr.read().decode().splitlines():
            print(line)

        # Execute the command
        print(f"Running command: rm {version}.json")
        stdin, stdout, stderr = ssh_client.exec_command(f"rm {version}.json")

        # Wait for the command to complete and fetch outputs
        exit_status = stdout.channel.recv_exit_status()
        print(f"Command completed with exit status: {exit_status}")

        # Print the standard output and error
        print("Standard Output:")
        for line in stdout.read().decode().splitlines():
            print(line)

        print("Standard Error:")
        for line in stderr.read().decode().splitlines():
            print(line)
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the connection
        ssh_client.close()
        print("Connection closed.")

    # Get statistics for the recording
    time.sleep(10)
    recording = project.get_last_recording()
    info = recording.get_channel_info(device.id, 'mp')
    statistics_mp = recording.get_channel_statistics(device.id, 'mp', info['from'], info['to'])
    
    recording.rename(f"recording_{rpi}_{linux}_{version}")

    # Assume info and statistics_mp are already defined
    duration = info["to"] - info["from"]
    energy_joules = statistics_mp["average"] * duration

    # Column headers (must match order of data)
    headers = [
        "From", "To", "Offset", "Sample rate",
        "Min", "Max", "Average", "Duration", "Energy consumption"
    ]

    # Row of data to append
    row = [
        info["from"],
        info["to"],
        info["offset"],
        info["sample_rate"],
        round(statistics_mp["min"], 5),
        round(statistics_mp["max"], 5),
        round(statistics_mp["average"], 5),
        round(duration, 5),
        round(energy_joules, 5)
    ]

    file_path = f"../../results/results_{rpi}_{linux}_{version}.csv"

    # Check if file exists
    file_exists = os.path.isfile(file_path)

    # Open the file in append mode
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(headers)
        
        # Write the data row
        writer.writerow(row)



def main(otii, device, project, rpi, linux, version, hostname, username, password):
    '''Connect to the Otii 3 application and run the measurement'''
    try:
        run_benchmarks(otii, device, project, rpi, linux, version, hostname, username, password)
    except Exception as error:
        print(f"Something went wrong: {error}. Retrying")
        run_benchmarks(otii, rpi, linux, version, hostname, username, password)

if __name__ == '__main__':
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        # Get a reference to a Arc or Ace device
        devices = otii.get_devices()
        if len(devices) == 0:
            raise AppException('No Arc or Ace connected!')
        device = devices[0]

        # Configure the device
        device.set_main_voltage(5.1)
        device.set_exp_voltage(4.9)
        device.set_max_current(2.5)

        # Enable the main current channel
        device.enable_channel('mp', True)
        device.enable_channel('mc', True)

        # Get the active project
        project = otii.get_active_project()
        with open("credentials.json") as f:
            credentials = json.load(f)
            max = 11     
            for i in range(max):
                print(f"Running iteration {i+1} of {max}")
                try:
                    main(otii, device, project, "RPi3B+", "Alpine", "python3.13", credentials["hostname"], credentials["username"], credentials["password"])
                    time.sleep(5)
                except Exception as error:
                    print(f"Something went wrong: {error}. Skipping iteration.")
                    time.sleep(10)
            for i in range(max):
                print(f"Running iteration {i+1} of {max}")
                try:
                    main(otii, device, project, "RPi3B+", "Alpine", "python3.12", credentials["hostname"], credentials["username"], credentials["password"])
                    time.sleep(5)
                except Exception as error:
                    print(f"Something went wrong: {error}. Skipping iteration.")
                    time.sleep(10)
            for i in range(max):
                print(f"Running iteration {i+1} of {max}")
                try:
                    main(otii, device, project, "RPi3B+", "Alpine", "python3.11", credentials["hostname"], credentials["username"], credentials["password"])
                    time.sleep(5)
                except Exception as error:
                    print(f"Something went wrong: {error}. Skipping iteration.")
                    time.sleep(10)
            for i in range(max):
                print(f"Running iteration {i+1} of {max}")
                try:
                    main(otii, device, project, "RPi3B+", "Alpine", "python3.10", credentials["hostname"], credentials["username"], credentials["password"])
                    time.sleep(5)
                except Exception as error:
                    print(f"Something went wrong: {error}. Skipping iteration.")
                    time.sleep(10)
            for i in range(max):
                print(f"Running iteration {i+1} of {max}")
                try:
                    main(otii, device, project, "RPi3B+", "Alpine", "python3.9", credentials["hostname"], credentials["username"], credentials["password"])
                    time.sleep(5)
                except Exception as error:
                    print(f"Something went wrong: {error}. Skipping iteration.")
                    time.sleep(10)