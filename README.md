# tunnel-manager

Basic command line tool for managing ssh tunnels.

# Requirements

- python3 and  `pip3`
- make

# installation 

`make install`

or for development purposes

`make install_dev`

# Configuration

Create a config file in `~/.ssh/tunnels.yaml`

File structure

```
tunnels:
    ssh-hostname:           # ssh host to connect to and tunnel name in console
        dynamic:
            - 12345         # dynamic ports here
        local:
            - 32154:12345   # local ports here
        remote:
            - 127.0.0.1:65487:0.0.0.0:78456   # remote ports here
        host: myhost        # override the above host name (if you want to name of the tunnel tobe different from the ssh hostname)

```

The `ssh-hostname` uses the entries in your ssh config.  All connection options, such as compression, jumping, keys, etc, are read from the ssh config.  You cannot use user / password authentication since tunnel-manager runs non-interactively and cannot prompt (you shouldn't be using user/password based auth anyway ☹).  Same for private keys with passwords.  If you really need private key password support, please open an incident.

# Running

Once installed and configured, simply run `tunnel-manager`

The tunnel manager will create a tunnel to all of the hosts in your configuration.  If any fail, you will see the results in the console.  tunnel-manager retries connecting every 10 seconds, indefinitely.  

