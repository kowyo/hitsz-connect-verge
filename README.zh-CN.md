<div align="center">

<img src="https://github.com/user-attachments/assets/f72235d8-9a80-476a-b2e8-5de1608d5632" 
         width="128" 
         height="128" 
         alt="Icon">

# HITSZ Connect Verge

[中文](README.zh-CN.md) | [English](README.md)

![Action](https://github.com/kowyo/hitsz-connect-verge/actions/workflows/release.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/kowyo/hitsz-connect-verge)
![Downloads](https://img.shields.io/github/downloads/kowyo/hitsz-connect-verge/total)
![License](https://img.shields.io/github/license/kowyo/hitsz-connect-verge)
![Stars](https://img.shields.io/github/stars/kowyo/hitsz-connect-verge)

</div>

## 简介

HITSZ Connect Verge 是 [ZJU Connect](https://github.com/Mythologyli/zju-connect) 的图形用户界面（GUI）。适用于 ZJU Connect/EasyConnect 的用户。

## 功能特点

- 与 **EasyConnect** 相比更快速、更轻量
- 基于 PySide6，易于构建，方便初学者参与维护
- 跨平台支持，对 **macOS** 版本进行了原生适配和优化
- 可与 Clash、远程桌面、SSH 等应用协同工作（参见[与其他应用协同工作](#与其他应用协同工作)章节）
- 支持自定义服务器地址/DNS/HTTP/SOCKS5 代理端口、定时保活等 ZJU Connect 常用的参数（如果有需要额外添加的参数，请提交 issue/PR）

## 安装指南

您可通过两种方式安装 HITSZ Connect Verge：下载预编译版本或从源码构建。

> [!NOTE]
>
> 1. 如果你是 HITSZ 校内学生，用户名与密码与[统一身份认证平台](https://ids.hit.edu.cn)的登录凭证相同
> 2. 若下载速度较慢，可尝试使用 [gh-proxy](https://gh-proxy.com) 进行加速

### 方式一：下载预编译版本

HITSZ Connect Verge提供开箱即用体验，您可从[发布页面](https://github.com/kowyo/hitsz-connect-verge/releases/latest)获取最新版本。

> [!IMPORTANT]
> macOS 版本需通过以下命令授予应用权限：
>
> ```bash
> sudo xattr -rd com.apple.quarantine HITSZ\ Connect\ Verge.app
> ```
>
> 或者，前往 macOS `设置`->`隐私与安全性`->`安全性`->`打开`——`仍要打开` 来打开应用。

### 方式二：从源码构建

1. 克隆仓库：

    ```bash
    git clone https://github.com/kowyo/hitsz-connect-verge.git
    cd hitsz-connect-verge
    ```

2. 安装依赖：

    强烈建议使用虚拟环境。可通过以下命令创建：

    ```bash
    python -m venv venv
    source venv/bin/activate # 激活虚拟环境
    ```

    安装依赖项：

    ```bash
    pip install -r requirements.txt
    ```

3. 运行应用：

    ```bash
    python main.py
    ```

4. （可选）构建二进制文件：

    请参考我们的 [GitHub Actions 工作流](.github/workflows/release.yml)。

## 与其他应用协同工作

### 基础信息

- **服务器地址**: vpn.hitsz.edu.cn
- **SOCKS5代理端口**: 1080
- **HTTP代理端口**: 1081
- **DNS服务器**: 10.248.98.30

如需了解更详细的网络配置信息，请访问 [Mythologyli/zju-connect](https://github.com/Mythologyli/zju-connect)。

### Clash 配置

如果您想同时使用 Clash（比如，同时观看 YouTube 和访问 <http://jw.hitsz.edu.cn> ），您可以将以下配置添加到您的 Clash 配置文件中。

例如，如果您使用 [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev)，您可以前往“配置文件” -> 右键单击您正在使用的配置文件 -> “编辑文件” -> 添加以下配置：

```yaml
# 注：请勿将此直接附加到文件末尾，而是分别将其附加到每个配置块的末尾
proxies:
    # 您现有的代理...
    - { name: 'HITSZ Connect Verge', type: socks5, server: 127.0.0.1, port: 1080, udp: true }

proxy-groups:
    # 您现有的代理组...
    - { name: 校园网, type: select, proxies: ['DIRECT', 'HITSZ Connect Verge'] }

rules:
    # 您现有的规则...
    - 'DOMAIN,vpn.hitsz.edu.cn,DIRECT'
    - 'DOMAIN-SUFFIX,hitsz.edu.cn,校园网'
    - 'IP-CIDR,10.0.0.0/8,校园网,no-resolve'
    # - 'IP-CIDR,<其他_ip>,校园网,no-resolve'

```

> [!NOTE]
>
> 1. 建议启用 `TUN 模式`
> 2. 需要关闭内网绕过代理, 并添加 `localhost` 到`代理绕过设置`区域

[了解更多](https://oldkingok.cc/share/8bFQXBjOkXt8)

### 远程桌面连接

如需接入校园网内的远程桌面，可使用 [Parallels Client](https://www.parallels.com/hk/products/ras/capabilities/parallels-client/)，并将本地 1080 端口配置为代理。

### SSH连接

如果你是 macOS/Linux 用户，可以通过以下命令建立SSH连接：

```bash
ssh -o ProxyCommand="nc -X 5 -x 127.0.0.1:1080 %h %p" <用户名>@<服务器地址> -p <端口>
```

如果你是 Windows 用户，可以使用 [PuTTY](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) 并在 `Connection` -> `Proxy` 中配置 `SOCKS5` 代理。

[了解更多](https://www.simplified.guide/putty/connect-via-proxy)

## 截图

|   Windows   |   macOS    |   Linux    |
| ---- | ---- | ---- |
|  <img width="412" alt="windows" src="assets/windows.png" />   | <img width="412" alt="mac" src="assets/mac.png" />  | <img width="412" alt="linux" src="assets/linux.png" />  |

## 贡献

欢迎贡献代码！您可以通过提交 Issue 或 Pull Request 参与项目。重大修改建议先创建 Issue 讨论。

同时，欢迎修正任何拼写错误。

## 相关项目

- [chenx-dust/HITsz-Connect-for-Windows](https://github.com/chenx-dust/HITsz-Connect-for-Windows)：支持高级设置与多平台的 HITsz 版 ZJU-Connect
- [Co-ding-Man/hitsz-connect-for-windows](https://github.com/Co-ding-Man/hitsz-connect-for-windows)：适用于 HITSZ 的开箱即用版 zju-connect 简易 GUI

## 鸣谢

- [Mythologyli](https://github.com/Mythologyli) 开发的项目 [ZJU Connect](https://github.com/Mythologyli/zju-connect)

- [Keldos](https://github.com/Keldos-Li) 为本项目重新设计了 macOS 版本的图标

- [EasierConnect](https://github.com/lyc8503/EasierConnect)

- 本项目的所有贡献者
