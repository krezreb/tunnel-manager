# tunnel-manager

Basic command line tool for managing ssh tunnels.

# Requirements

- python3 and  `pip3`
- `make`
- `git`

# Installation 

```
git clone https://github.com/krezreb/tunnel-manager.git
cd tunnel-manager
make install
```

or for development purposes

`make install_dev`

# Configuration

Create a config file in `~/.ssh/tunnels.yaml`

File structure

```
tunnels:
    ssh-hostname:           # tunnel name and ssh host
        dynamic:
            - 12345         # (optional) dynamic ports here
        local:
            - 54321:12345   # (optional) local ports here
        remote:
            - 127.0.0.1:65487:0.0.0.0:78456   # remote ports here
        host: myhost        # (optional) override the above host name (if you want to name of the tunnel to be different from the ssh hostname)

```

The `ssh-hostname` uses the entries in your ssh config.  All connection options, such as compression, jumping, keys, etc, are read from the ssh config. 

For password-protected private keys, use ssh-agent and add the keys to the agent prior to running `tunnel-manager`.  User/Password authentication is not supported.

# keepalive

By default, tunnel-manager enables [ssh keepalive](https://medium.com/swlh/keep-ssh-connections-alive-2712462ba68d).  To override this:

```
tunnels:
    ssh-hostname:          
        keepalive: 0    # disable on a host-by-host basis

defaults
    keepalive: 0        # disable by default
```

# Running

Once installed and configured, simply run `tunnel-manager`

The tunnel manager will create a tunnel to all of the hosts in your configuration.  If any fail, you will see the results in the console.  tunnel-manager retries connecting every 10 seconds, indefinitely.  

