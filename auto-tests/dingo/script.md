# How to install crontab script

- Edit crontab files

```shell
crontab -e
```

- Copy Commands to Script

```shell
10 15 * * * /root/dingo/start.sh
```

- Docker configuration

```shell
{
	"auths": {
		"https://index.docker.io/v1/": {
			"auth": "ZGluZ29kYXRhYmFzZTpTZXJ2ZXIyMDIxIQ=="
		}
	},

    "proxies": {
                "default": {
         }
    }
}
```
