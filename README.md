<div align="center">

<img src="https://github.com/user-attachments/assets/f72235d8-9a80-476a-b2e8-5de1608d5632" 
         width="128" 
         height="128" 
         alt="Icon">

# HITSZ Connect Verge

[English](README.md) | [中文](README.zh-CN.md)

![Action](https://github.com/kowyo/hitsz-connect-verge/actions/workflows/release.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/kowyo/hitsz-connect-verge)
![Downloads](https://img.shields.io/github/downloads/kowyo/hitsz-connect-verge/total)
![License](https://img.shields.io/github/license/kowyo/hitsz-connect-verge)
![Stars](https://img.shields.io/github/stars/kowyo/hitsz-connect-verge)

</div>

> [!IMPORTANT]
> EasyConnect has been deprecated in HITSZ since May 6th, 2025 (or earlier), and related API accessed from ZJU Connect and HITSZ Connect Verge is disabled. If your faculty can still use EasyConnect, this project will still work for you, enjoy it.
>
> If you cannot use EasyConnect/this project, the official replacement is [aTrust](https://www.sangfor.com.cn/sangfor-security/atrust), which is still disgusting for me. If you are from HITSZ, you can access aTrust from <https://trust.hitsz.edu.cn>
>
> I will recommend you to have a look at [docker-easyconnect](https://github.com/docker-easyconnect/docker-easyconnect), which mentions its compatibility with aTrust. Although I haven't tested it.

## Introduction

HITSZ Connect Verge is a GUI of [ZJU Connect](https://github.com/Mythologyli/zju-connect). It is built for users of ZJU Connect/EasyConnect.


## Features

- Fast and green compared to **EasyConnect**.
- Built with PySide6, easy to build and maintain.
- Multi-platform support, with native optimization for the **macOS** version.
- Works with other applications like Clash, Remote Desktop, and SSH. (See [Working with other applications](#working-with-other-applications))
- Supports custom server address/DNS/HTTP/SOCKS5 proxy port, and keep-alive settings. (If you need additional parameters, please submit an issue/PR)

## Installation

You can install HITSZ Connect Verge in two ways: downloading pre-built binaries or building from source.

> [!NOTE]
>
> 1. If you are a student of HITSZ, username and password are the same as the ones you use to log in to the [Unified Identity Authentic Platform](https://ids.hit.edu.cn).
> 2. If the download speed is slow, you can try using [gh-proxy](https://gh-proxy.com) to download.

### Method 1: Downloading pre-built binaries

HITSZ Connect Verge provides out-of-the-box experience. You can download the latest version from the [release page](https://github.com/kowyo/hitsz-connect-verge/releases/latest).

> [!IMPORTANT]
> For macOS version, you need to grant access to the application by running:
>
> ```bash
> sudo xattr -rd com.apple.quarantine /Applications/HITSZ\ Connect\ Verge.app
> ```

### Method 2: Building from source

1. Clone the repository:

    ```bash
    git clone https://github.com/kowyo/hitsz-connect-verge.git
    cd hitsz-connect-verge
    ```

2. Install dependencies:

    - Install [uv](https://docs.astral.sh/uv/getting-started/installation/)

    - Sync the environment:

        ```bash
        uv sync
        ```

3. Run the application:

    macOS/Linux

    ```bash
    source .venv/bin/activate
    uv run app/main.py
    ```

    Windows (Powershell)

    ```powershell
    .\.venv\Scripts\activate.ps1
    uv run .\app\main.py
    ```

4. (Optional) Build the binaries:

    Please refer to our [GitHub Actions workflow](.github/workflows/release.yml) for more information.

## Working with other applications

### Basic information

- **Server**: vpn.hitsz.edu.cn
- **SOCKS5 Proxy**: 1080
- **HTTP Proxy**: 1081
- **DNS Server**: 10.248.98.30

If you want to learn more about the network configuration, you can visit [Mythologyli/zju-connect](https://github.com/Mythologyli/zju-connect).

### Clash

If you want to use Clash at the same time (e.g. watching Youtube and visiting <http://jw.hitsz.edu.cn> at the same time), you can add the following configuration to your clash configuration file.

For example, if you are using [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev), you can go to 'Profiles' -> Right click on the profile you are using -> 'Edit File' -> Add the following configuration:

```yaml
# note: do not append this to the end of the file directly, append it separately to the corresponding position
proxies:
    # your existing proxies...
    - { name: 'HITSZ Connect Verge', type: socks5, server: 127.0.0.1, port: 1080, udp: true }

proxy-groups:
    # your existing proxy-groups...
    - { name: 校园网, type: select, proxies: ['DIRECT', 'HITSZ Connect Verge']}

rules:
    # your existing rules...
    - 'DOMAIN,vpn.hitsz.edu.cn,DIRECT'
    - 'DOMAIN-SUFFIX,hitsz.edu.cn,校园网'
    - 'IP-CIDR,10.0.0.0/8,校园网,no-resolve'
    # - 'IP-CIDR,<other_ip>,校园网,no-resolve'
```

> [!NOTE]
>
> 1. You need to enable `TUN Mode` in Clash, and enable the `Auto Configure Proxy` option of this software.
> 2. You need to turn off the `Always use Default Bypass` option in the `System Proxy` settings, and add `localhost` to the `Proxy Bypass` field.s
> 3. A useful [global extend script](./clash-utils.js) is provided if you want to avoid the automatic update of the profiles overwrite your custom rules.

<!-- > (Confusion) 3. There is no need to enable the `Auto Configure Proxy` feature of this software. In this case, Clash will host the system proxy and the proxy of this software will be forwarded by Clash. -->

[Learn more](https://oldkingok.cc/share/8bFQXBjOkXt8)

### Remote Desktop

If you want to connect to the remote desktop in the campus network, you can use [Parallels Client](https://www.parallels.com/hk/products/ras/capabilities/parallels-client/), and configure the local 1080 port as a proxy.

### SSH

If you want to use SSH, you can use the following command to establish a connection.

For macOS/Linux users:

```bash
ssh -o ProxyCommand="nc -X 5 -x 127.0.0.1:1080 %h %p" <root>@<server> -p <port>
```

For Windows users, you can use [ncat](https://nmap.org/download.html) to setup SOCKS 5 proxy. Run the following command after installing ncat:

``` powershell
ssh -o "ProxyCommand=ncat --proxy 127.0.0.1:1080 --proxy-type socks5 %h %p" <root>@<server> -p <port>
```

[Learn more](https://hoa.moe/blog/using-hitsz-connect-verge-to-ssh-school-server/#windows)

## Screenshots

|   Windows   |   Mac   |  Linux   |
| ---- | ---- | ---- |
|  <img width="412" alt="windows" src="assets/windows.png" />   | <img width="412" alt="mac" src="assets/mac.png" />  | <img width="412" alt="linux" src="assets/linux.png" />  |

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

Also, any typo is welcome to be fixed.

## Related Projects

- [chenx-dust/HITsz-Connect-for-Windows](https://github.com/chenx-dust/HITsz-Connect-for-Windows): HITsz Edition of ZJU-Connect-for-Windows. Support advanced settings and multi-platform.
- [Co-ding-Man/hitsz-connect-for-windows](https://github.com/Co-ding-Man/hitsz-connect-for-windows): Out-of-the-box zju-connect simple GUI for Windows, suitable for HITSZ.

## Credits

- [Mythologyli](https://github.com/Mythologyli) for the project [ZJU Connect](https://github.com/Mythologyli/zju-connect).

- [Keldos](https://github.com/Keldos-Li) for designing the macOS version's icon.

- [EasierConnect](https://github.com/lyc8503/EasierConnect).

- All the contributors to this project.
