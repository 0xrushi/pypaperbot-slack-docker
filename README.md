# pypaperbot-slack-docker
A docker enviornment implementing a slack chatbot for [PyPaperBot](https://github.com/ferru97/PyPaperBot) on ARM servers 


# To host on Oracle ARM

## Open port 5000
![image](https://user-images.githubusercontent.com/6279035/183801116-49ca2392-4ff2-418d-a8b0-21acaf3321ae.png)

## Enable connections on port 5000 through firewall

```bash
sudo  firewall-cmd  --permanent --zone=public --list-ports
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --permanent --zone=public --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Add the public ip of the server in the Slack API for / commands

![image](https://user-images.githubusercontent.com/6279035/183801367-2ad73af9-be20-4b08-9e62-c908b13cc804.png)
