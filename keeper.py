import configparser
from tqdm import tqdm  # type: ignore
import time

import subprocess
import threading
import os


class Ore:
    def __init__(self, config_path: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.priority_fee = int(config.get("ORE", "priority_fee"))
        self.keypair = config.get("ORE", "keypair_path")
        self.rpc = config.get("ORE", "rpc")
        self.threads = int(config.get("ORE", "threads"))

        self.parallel_miners = int(config.get("MINERS", "parallel_miners"))
        self.miners_phase = float(config.get("MINERS", "miners_phase"))
        self.miners_wave = int(config.get("MINERS", "miners_wave"))

    def get_output(self, command: str) -> str | None:
        try:
            output = subprocess.check_output(command, shell=True)
            return output.decode("utf-8")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return None

    def mine(self):
        command = f"ore --keypair {self.keypair} --priority-fee {self.priority_fee} --rpc {self.rpc} mine --threads {self.threads}"

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

        def command():
            path = os.getcwd()

            command = f'start cmd /c "cd {path} & mode con: cols=45 lines=10 & '
            command += f"ore --keypair {self.keypair} --priority-fee {self.priority_fee} --rpc {self.rpc} mine --threads {self.threads}"
            command += ' & pause" /s'

            process = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate()
            results.append([stdout, stderr])

        print("In 5 seconds miners will start deploying...")
        time.sleep(5)

        threads = []
        for i in tqdm(range(self.parallel_miners), desc="Deploying miners", unit="m"):
            t = threading.Thread(target=command)
            threads.append(t)
            t.start()

            if i != 0 and i % self.miners_wave == 0:
                time.sleep(self.miners_phase)
            else:
                time.sleep(0.1)

        for t in threads:
            t.join()

    def rewards(self):
        command = f"ore --keypair {self.keypair} rewards"
        output: str = self.get_output(command)  # type: ignore

        if output is not None:
            rewards = float(output.split()[0])
        else:
            rewards = 0
        return rewards


def main():
    ORE = Ore()

    initial_rewards = ORE.rewards()
    previous_rewards = initial_rewards

    print(
        f"Starting mining session with {initial_rewards:06f} ORE (To finish the process close every mining terminal)"
    )

    ORE.parallel_mining()

    try:
        while True:
            time.sleep(5 * 60)

            rewards = ORE.rewards()

            print(
                f" --- Gained {rewards - previous_rewards:06f} ORE, totaling to {rewards:06f} ORE"
            )

            previous_rewards = rewards

    except KeyboardInterrupt:
        print(" --- Manually ending mining session")

    rewards = ORE.rewards()

    print(
        f"\nGained a total of {rewards - initial_rewards:06f} ORE in this session, totaling to {rewards:06f} ORE"
    )


if __name__ == "__main__":
    main()
