import configparser
import platform
from tqdm import tqdm  # type: ignore
import time
from datetime import datetime

import subprocess
import threading
import os
import psutil  # type: ignore


class Ore:
    def __init__(self, config_path: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.priority_fee = int(config.get("ORE", "priority_fee"))

        self.keypairs_path = config.get("ORE", "keypairs_path")
        if os.path.exists(self.keypairs_path):
            self.keypairs = []
            for kp in os.listdir(self.keypairs_path):
                if os.path.splitext(kp)[1] == ".json":
                    self.keypairs.append(os.path.join(self.keypairs_path, kp))

            if not self.keypairs:
                print("Keypairs folder is empty.")
        else:
            print(f"The provided path: {self.keypairs_path} does not exist.")

        self.rpc = config.get("ORE", "rpc")
        self.rpc = self.rpc.split(", ")  # type: ignore

        self.threads = int(config.get("ORE", "threads"))

        self.parallel_miners = int(config.get("MINERS", "parallel_miners"))
        self.miners_phase = float(config.get("MINERS", "miners_phase"))
        self.miners_wave = int(config.get("MINERS", "miners_wave"))

        subprocess.run(
            "title OMC Controller", shell=True, capture_output=False, text=False
        )

    def get_output(self, command: str) -> str | None:
        try:
            output = subprocess.check_output(command, shell=True)
            return output.decode("utf-8")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return None

    def mine(self):
        command = f"ore --keypair {self.keypairs} --priority-fee {self.priority_fee} --rpc {self.rpc[0]} mine --threads {self.threads}"

        stdout = True

        if stdout:
            process = subprocess.Popen(command, shell=True)
        else:
            with open(os.devnull, "w") as devnull:
                process = subprocess.Popen(
                    command, shell=True, stdout=devnull, stderr=devnull
                )

        process.wait()

    def parallel_mining(self):
        results = []

        def command(keypair, rpc, id):
            path = os.getcwd()

            command = f'start cmd /c "cd {path} & mode con: cols=45 lines=10 & title OMC Mining Instance {id:03d} & '
            command += f"ore --keypair {keypair} --priority-fee {self.priority_fee} --rpc {rpc} mine --threads {self.threads}"
            command += ' & pause" /s'

            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate()
            results.append([stdout, stderr])

        print("In 5 seconds miners will start deploying...")
        time.sleep(5)

        status_bar = tqdm(
            total=len(self.keypairs * self.parallel_miners),
            desc="Deploying miners",
            unit="m",
        )

        i = 0
        threads = []

        min_sleep = 3
        min_cpu_usage = 35  # %
        for _ in range(self.parallel_miners):
            for keypair in self.keypairs:
                if i != 0 and i % self.miners_wave == 0:
                    time.sleep(min_sleep)
                    for _ in range(max(0, int(self.miners_phase - min_sleep))):
                        cpu_usage = psutil.cpu_percent(1)
                        if cpu_usage <= min_cpu_usage:
                            break
                else:
                    time.sleep(0.1)

                t = threading.Thread(
                    target=command, args=(keypair, self.rpc[i % len(self.rpc)], i + 1)
                )
                threads.append(t)
                t.start()

                i += 1
                status_bar.update(1)

    def rewards(self, keypair):
        command = f"ore --keypair {keypair} --rpc {self.rpc[0]} rewards"
        output: str = self.get_output(command)  # type: ignore

        if output is not None:
            rewards = float(output.split()[0])
        else:
            rewards = 0
        return rewards

    def rewards_multiple(self):
        rewards = 0
        for keypair in self.keypairs:
            rewards += self.rewards(keypair)
        return rewards

    def force_claim(self):
        rewards = self.rewards_multiple()

        if rewards == 0:
            print("You have no rewards to claim. Exiting.")
        else:
            print(f"Trying to claim {rewards:06f} ORE")

        for i, keypair in enumerate(self.keypairs):
            if self.rewards(keypair) == 0:
                continue

            command = f"ore --keypair {keypair} --priority-fee {self.priority_fee} --rpc {self.rpc[0]} claim"

            while True:
                output: str = self.get_output(command)  # type: ignore

                success_msg = "Transaction landed!"
                if success_msg in output:
                    print(f"Succesfully claimed your ORE for keypair file {i:03d}")
                    break


def main():
    ORE = Ore()

    initial_rewards = ORE.rewards_multiple()
    previous_rewards = initial_rewards

    start_time = time.time()

    if platform.system() == "Windows":
        import pygetwindow as pygw  # type: ignore

        initial_windows = pygw.getAllWindows()

    print(
        f"Starting mining session with {initial_rewards:06f} ORE (Ctrl + C inside the OMC Controller to close all the OMC Mining Instances)"
    )

    try:
        ORE.parallel_mining()

        while True:
            time.sleep(2 * 60)

            rewards = ORE.rewards_multiple()

            end_time = datetime.now()

            minutes_elapsed = (end_time.timestamp() - start_time) / 60
            rate = (rewards - initial_rewards) / minutes_elapsed

            print(
                f" --- [{end_time.strftime('%H:%M:%S')}] Gained {rewards - previous_rewards:06f} ORE | Total {rewards:06f} ORE | Rate {rate:06f} ORE/m {rate * 60:06f} ORE/h"
            )

            previous_rewards = rewards

    except KeyboardInterrupt:
        print(" --- Manually ending mining session")

        if platform.system() == "Windows":
            windows = pygw.getAllWindows()  # type: ignore

            miners_windows = [
                window for window in windows if "OMC Mining Instance" in window.title
            ]
            for window in miners_windows:
                if window not in initial_windows:  # type: ignore
                    window.close()

    rewards = ORE.rewards_multiple()

    print(
        f"\nGained a total of {rewards - initial_rewards:06f} ORE in this session, totaling to {rewards:06f} ORE"
    )


if __name__ == "__main__":
    main()
