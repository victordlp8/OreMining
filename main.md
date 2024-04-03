# Welcome to how to easily mine some ORE tutorial

### What is ORE?
Check its [explanation](https://ore.supply/what-is-mining), [tokenomics](https://ore.supply/ore-tokenomics) and its [X](https://twitter.com/OreSupply). But simply ORE is a token in the Solana blockchain that you can mine from your computer anywhere with any computational capability.

## Where to start
You can check their recommendations [here](https://ore.supply/download) but I'm gonna simplify those to you.


### 1. Installing Rust
First you have to install Rust, go to their [official website](https://www.rust-lang.org/tools/install) and follow the steps to install it.

### 2. Installing Python
Go to their [official website](https://www.python.org/downloads/) and follow the steps to install the latest version.

### 3. Installing the Solana CLI
Same as with Rust and Python, follow the steps they provide for your Operative System [here](https://docs.solanalabs.com/es/cli/install#use-solanas-install-tool)

### 4. Generating your Solana CLI wallet
Use this command to generate your Solana CLI wallet. This will be the wallet used for mining ORE on your computer.
```
solana-keygen new
```

The path where it is created should appear on the terminal. Once you have created your wallet, you will need to copy the ``id.json`` file into this working directory and rename it to ``ore_keypair.json``.

### 5. Installing the ORE CLI cargo
Just execute the following command, this step may take a while.
```
cargo install ore-cli
```

### 6. Final touches
Install the Python dependencies by running the following command on the terminal.
```
pip install -r requirements.txt
```

You can edit the ``config.ini`` file as your liking. Recommended settings are the ones provided.

With Solana's congestion it is recommended to have at least some lamports of priority fee. You can also change the default rpc to a better one, that would help with landing the validation transactions of ORE.

Finally change the number of threads to any number you want as long as it's lower than your maximum number of threads. The mining part is pretty CPU intensive and currently the main limitation is Solana's congestion on the validation part so I don't recommend spending all your threads but do as you wish, experiment with it.

### 7. Finally mining some ORE
Just doble click or execute from the terminal the ``start.bat`` file or execute the ``keeper.py`` script using Python.

Whenever you want to claim your ORE you should use this command and you will receive it to your wallet.
```
ore --keypair ore_keypair.json --priority-fee 88 claim
```
