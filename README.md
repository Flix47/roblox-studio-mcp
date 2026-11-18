# Roblox Studio MCP Wrapper

A small Python wrapper that launches Roblox Studio and proxies its stdio, so an MCP (Model Context Protocol) client can talk to Studio through a local process.

## What it does

- Locates the Roblox Studio executable automatically:
  - Windows: scans %LOCALAPPDATA%\Roblox\Versions and picks the most recently modified RobloxStudioBeta.exe.
  - macOS: uses /Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio.
- Starts Studio as a child process with piped stdin/stdout/stderr.
- Forwards Studio's stdout and stderr to the wrapper's stdout and stderr using background threads.
- Reads JSON-RPC lines from stdin and forwards them to Studio's stdin.
- Intercepts the "server/discover" method and replies with a JSON-RPC "Method not found" error (-32601), instead of passing it to Studio.
- Cleans up the child process on exit, Ctrl+C, or broken pipe.

## Requirements

- Python 3.8+
- Roblox Studio installed
- Windows or macOS (Linux is not supported)

## Platform support

- Windows: tested.
- macOS: supported by the code, but NOT tested. The macOS path is hardcoded and may need adjustment depending on the Studio installation. Use at your own risk.

## Usage

Wire it into an MCP client configuration.

### Example MCP configuration

    "mcp": {
        "Roblox_Studio": {
          "type": "local",
          "command": [
            "python",
            "c:\\...\\mcp.py"
          ],
          "enabled": true
        }
      }

In this example, the MCP client launches mcp.py with python. The wrapper then starts Roblox Studio and bridges the JSON-RPC messages between the client and Studio over stdio. Adjust the path in "command" to wherever mcp.py actually lives on your machine.

## Notes

- All communication is line-delimited JSON-RPC over Studio.
- "server/discover" is answered locally by the wrapper, not by Studio.
- No external dependencies beyond the Python standard library.
