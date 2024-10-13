# HearthstoneAccess Patcher
An application that automates patching Hearthstone using the [HearthstoneAccess Community Patch](https://www.hearthstoneaccess.com/)

## Overview
This app (referred to as the patcher) performs the following tasks:
* Downloads the zipped archive of the HearthstoneAccess Community Patch
* Unzips the archive
* Places the contents in your Hearthstone installation directory
* Prompts if you want the changelog put on your desktop

There are two general target audiences: those who wish to simply use the patcher, and those who wish to develop/build the patcher.

## Using the Patcher
To use the patcher, download the latest executable from the [latest release page](https://github.com/leibylucw/hearthstone-access-patcher/releases/latest) and run like any other program.

## Developing the Patcher
### Install System Dependencies
Make sure you have the following dependencies installed and available on your system:
* [Git](https://git-scm.com/): any recent version
* [GitHub CLI](https://cli.github.com/) (optional): any recent version
* .NET 8 sdk, either from [dotnet.microsoft.com](https://dotnet.microsoft.com/en-us/download) or install using visual studio.

### Clone the Repo
With Git:

```shell
git clone https://github.com/leibylucw/hearthstone-access-patcher.git
cd hearthstone-access-patcher
```

Or with gh:

```shell
gh repo clone leibylucw/hearthstone-access-patcher
cd hearthstone-access-patcher
```

### Common Development Tasks:

- **Running the Program:**
  To quickly run your program during development, type `dotnet run` in the terminal. This command compiles and runs the program in **debug mode**, meaning it prioritizes fast compilation times without any optimization. It's useful for testing and debugging but not ideal for final performance tests or releases.

- **Building the Program:**
  If you want to compile the program without running it, use `dotnet build`. By default, this also builds in **debug mode**, where the focus is on fast feedback and ease of debugging. Optimizations are turned off, so the build is quick, but not the most efficient. Use this primarily during development when you need to verify that the program compiles correctly.

- **Publishing the Program:**
  For a version of the program that’s ready to distribute or deploy, use `dotnet publish`. This builds the program in **release mode**, enabling optimizations that improve performance and reduce the final file size. The output is typically placed in a folder like `bin\Release\net8.0-windows\win-x86\publish`. The exact path might vary based on your runtime and platform, but it will always follow a similar structure.
