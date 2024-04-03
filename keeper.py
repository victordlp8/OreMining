import configparser

import subprocess
import os


class Ore:
    def __init__(self, config_path: str = "config.ini"):
        config = configparser.ConfigParser()
        config.read(config_path)

        self.priority_fee = config.get("ORE", "priority_fee")
        self.keypair = config.get("ORE", "keypair_path")
        self.rpc = config.get("ORE", "rpc")
        self.threads = config.get("ORE", "threads")

    def execute(self, command: str, stdout: bool):
        if stdout:
            process = subprocess.Popen(command, shell=True)
        else:
            with open(os.devnull, "w") as devnull:
                process = subprocess.Popen(
                    command, shell=True, stdout=devnull, stderr=devnull
                )

        process.wait()

    def get_output(self, command: str) -> str | None:
        try:
            output = subprocess.check_output(command, shell=True)
            return output.decode("utf-8")

        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return None

    def mine(self):
        command = f"ore --keypair {self.keypair} --priority-fee {self.priority_fee} --rpc {self.rpc} mine --threads {self.threads}"
        self.execute(command, False)

    def rewards(self):
        command = f"ore --keypair {self.keypair} rewards"
        output: str = self.get_output(command)  # type: ignore

        rewards = float(output.split()[0])
        return rewards


def main():
    ORE = Ore()

    initial_rewards = ORE.rewards()
    previous_rewards = initial_rewards
    print(f"Starting this mining session with {initial_rewards:06f} ORE")

    i, finish = 0, False
    while not finish:
        print(
            f"\nMining Iteration {i + 1:03d} (MIs can be ended at any moment manually with Ctrl+C)"
        )
        try:
            ORE.mine()
            print(" --- MI ended")

        except KeyboardInterrupt:
            print(" --- Manually ending MI")
            finish = True

        rewards = ORE.rewards()
        print(
            f" --- Gained {rewards - previous_rewards:06f} ORE, totaling to {rewards:06f} ORE"
        )
        previous_rewards = rewards

        i += 1

    print(
        f"\nGained a total of {rewards - initial_rewards:06f} ORE in this session, totaling to {rewards:06f} ORE"
    )


if __name__ == "__main__":
    main()
