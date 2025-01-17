<div align="center">

# HITSZ Connect Verge

[English](README.md) | [中文](README.zh-CN.md)

![Action](https://github.com/kowyo/hitsz-connect-verge/actions/workflows/release.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/kowyo/hitsz-connect-verge)
![Downloads](https://img.shields.io/github/downloads/kowyo/hitsz-connect-verge/total)
![License](https://img.shields.io/github/license/kowyo/hitsz-connect-verge)
![License](https://img.shields.io/github/stars/kowyo/hitsz-connect-verge)

</div>

## Introduction

HITSZ Connect Verge is a GUI of [ZJU Connect](https://github.com/Mythologyli/zju-connect). It helps you connect to the campus network of HITSZ remotely.

## Features

- Fast and green compared to **EasyConnect**.
- Simplified UI and Fluent UI (Windows only).
- Built with PySide6 and Python, making it beginner-friendly to contribute and maintain.
- Multi-platform support, providing out-of-box experience without executing additional scripts.
- Advanced settings (coming soon).

## Installation

You can install HITSZ Connect Verge in two ways: downloading pre-built binaries or building from source.

> [!NOTE]
> 
> 1. Username and password are the same as the ones you use to log in to the [Unified Identity Authentic Platform](https://ids.hit.edu.cn)
> 2. If the download speed is slow, you can try using [gh-proxy](https://gh-proxy.com) to download.

### Method 1: Downloading pre-built binaries

HITSZ Connect Verge provides out-of-the-box experience. You can download the latest version from the [release page](https://github.com/kowyo/hitsz-connect-verge/releases/latest).

> [!IMPORTANT]
> For macOS version, you need to grant access to the application by running:
>
> ```bash
> sudo xattr -rd com.apple.quarantine hitsz-connect-verge.app
> ```
>
> In some case, you need to go to macOS `Settings` -> `System Preferences` -> 
> `Security & Privacy` -> `Open Anyway`.

### Method 2: Building from source

1. Clone the repository:

    ```bash
    git clone https://github.com/kowyo/hitsz-connect-verge.git
    cd hitsz-connect-verge
    ```

2. Install dependencies:

    It is strongly recommended to use a virtual environment. You can create a virtual environment by running:

    ```bash
    python -m venv venv
    source venv/bin/activate # activate the virtual environment
    ```

    Then, install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python main.py
    ```

4. (Optional) Build the binaries:

    You can build the binaries for Windows by running:

    ```bash
    pyinstaller --clean --onefile --noconsole `
    --icon assets/icon.ico `
    --add-data "assets;assets" `
    --add-data "core/zju-connect;core" `
    -n hitsz-connect-verge main.py
    ```

    For macOS/Linux, you can run the following commands:

    ```bash
    pyinstaller --clean --onefile --noconsole --windowed \
    --icon assets/icon.icns \
    --add-data "assets:assets" \
    --add-data "core/zju-connect:core" \
    -n hitsz-connect-verge main.py
    ```

## Screenshots

|   Windows   |   Mac   |  Linux   |
| ---- | ---- | ---- |
|  <img width="412" alt="windows" src="assets/windows.png" />   | <img width="412" alt="mac" src="assets/mac.png" />  | <img width="412" alt="linux" src="assets/linux.png" />  |

As of now, Linux version only supports building from source.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

Also, any typo is welcome to be fixed.

## Related Projects

- [chenx-dust/HITsz-Connect-for-Windows](https://github.com/chenx-dust/HITsz-Connect-for-Windows): HITsz Edition of ZJU-Connect-for-Windows. Support advanced settings and multi-platform.
- [Co-ding-Man/hitsz-connect-for-windows](https://github.com/Co-ding-Man/hitsz-connect-for-windows): Out-of-the-box zju-connect simple GUI for Windows, suitable for HITSZ.
