import configparser
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
        self.parallel_terminals = int(config.get("ORE", "parallel_terminals"))
        self.terminal_phase = float(config.get("ORE", "terminal_phase"))

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

        threads = []
        for _ in range(self.parallel_terminals):
            t = threading.Thread(target=command)
            threads.append(t)
            t.start()

            time.sleep(self.terminal_phase)

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
    print(f"Starting mining session with {initial_rewards:06f} ORE (To finish the process close every mining terminal)")

    try:
        ORE.parallel_mining()
        print(" --- Mining session ended")

    except KeyboardInterrupt:
        print(" --- Manually ending mining session")

    rewards = ORE.rewards()

    print(
        f"\nGained a total of {rewards - initial_rewards:06f} ORE in this session, totaling to {rewards:06f} ORE"
    )


if __name__ == "__main__":
    main()
