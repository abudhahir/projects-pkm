# GitHub Copilot SDK

The GitHub Copilot SDK provides programmatic access to GitHub Copilot's agentic workflows across multiple languages: TypeScript/Node.js, Python, Go, and .NET. It exposes the same production-tested agent runtime behind Copilot CLI, enabling developers to embed AI-powered assistants into their applications. The SDK handles orchestration, tool invocation, file operations, and session management automatically via JSON-RPC communication with the Copilot CLI server.

The SDK supports multiple authentication methods including GitHub OAuth, environment variables, and BYOK (Bring Your Own Key) for custom model providers like OpenAI, Azure, Anthropic, and local models via Ollama. Key features include streaming responses, custom tool definitions, MCP (Model Context Protocol) server integration, session hooks for intercepting conversations, infinite sessions with automatic context compaction, and support for image attachments.

## CopilotClient - Create and Manage Client Connection

The `CopilotClient` class manages the connection to the Copilot CLI server, handling process lifecycle, session creation, and server communication. It supports both automatic and manual server management modes.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

// Create client with default options (auto-start enabled)
const client = new CopilotClient();

// Or with custom options
const client = new CopilotClient({
    cliPath: "/usr/local/bin/copilot",  // Custom CLI path
    cliUrl: "localhost:8080",            // Connect to existing server
    port: 4321,                          // Custom port
    useStdio: true,                      // Use stdio transport (default)
    logLevel: "info",                    // Log level
    autoStart: true,                     // Auto-start server
    autoRestart: true,                   // Auto-restart on crash
    githubToken: process.env.GITHUB_TOKEN, // GitHub authentication
});

// Manual server control
const manualClient = new CopilotClient({ autoStart: false });
await manualClient.start();

// Check connection state
console.log(client.getState()); // "connected" | "disconnected" | etc.

// Ping server
const pong = await client.ping("hello");
console.log(pong); // { message: "hello", timestamp: 1234567890 }

// Clean shutdown
await client.stop();
```

## createSession - Create a New Conversation Session

Creates a new conversation session with the specified model and configuration. Sessions are independent conversation threads that maintain their own context and history.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    sessionId: "my-custom-id",           // Optional custom ID
    model: "gpt-4.1",                    // Model to use
    streaming: true,                     // Enable streaming responses
    reasoningEffort: "medium",           // "low" | "medium" | "high" | "xhigh"
    systemMessage: {
        mode: "append",                  // "append" or "replace"
        content: "You are a helpful code reviewer.",
    },
    infiniteSessions: {
        enabled: true,
        backgroundCompactionThreshold: 0.80,
        bufferExhaustionThreshold: 0.95,
    },
});

// Access session properties
console.log(session.sessionId);      // Unique session identifier
console.log(session.workspacePath);  // ~/.copilot/session-state/{sessionId}/

// Send message and wait for response
const response = await session.sendAndWait({
    prompt: "Review this function for bugs"
});
console.log(response?.data.content);

// Clean up
await session.destroy();
await client.stop();
```

## send / sendAndWait - Send Messages to Session

Send messages to the Copilot session with optional file attachments. `send()` returns immediately while `sendAndWait()` blocks until the session becomes idle.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({ model: "gpt-4.1" });

// Send message (returns immediately)
const messageId = await session.send({
    prompt: "What files are in this directory?",
    mode: "enqueue",  // "enqueue" or "immediate"
});

// Send with file attachments
await session.send({
    prompt: "Review this code",
    attachments: [
        {
            type: "file",
            path: "/path/to/code.ts",
            displayName: "Main Module",
        },
        {
            type: "file",
            path: "/path/to/image.png",  // Image attachments supported
        },
    ],
});

// Send and wait for completion
const response = await session.sendAndWait(
    { prompt: "Explain quantum computing" },
    60000  // Optional timeout in ms
);

if (response) {
    console.log("Response:", response.data.content);
}

await session.destroy();
await client.stop();
```

## Event Handling - Subscribe to Session Events

Subscribe to session events to handle streaming responses, tool executions, and session state changes in real-time.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    streaming: true
});

// Subscribe to specific event types
session.on("assistant.message_delta", (event) => {
    process.stdout.write(event.data.deltaContent);  // Streaming chunks
});

session.on("assistant.message", (event) => {
    console.log("\nFinal:", event.data.content);    // Complete message
});

session.on("tool.execution_start", (event) => {
    console.log(`Tool started: ${event.data.toolName}`);
});

session.on("tool.execution_complete", (event) => {
    console.log(`Tool completed: ${event.data.toolName}`);
});

session.on("session.idle", () => {
    console.log("Session is idle");
});

// Subscribe to all events
const unsubscribe = session.on((event) => {
    console.log(`Event: ${event.type}`, event.data);
});

// Send message
await session.sendAndWait({ prompt: "List files in current directory" });

// Unsubscribe when done
unsubscribe();

await session.destroy();
await client.stop();
```

## defineTool - Create Custom Tools

Define custom tools that Copilot can invoke during conversations. Tools enable the AI to call your code when it needs specific capabilities.

```typescript
import { CopilotClient, defineTool } from "@github/copilot-sdk";
import { z } from "zod";

// Define tool with Zod schema (recommended)
const weatherTool = defineTool("get_weather", {
    description: "Get current weather for a city",
    parameters: z.object({
        city: z.string().describe("City name"),
        units: z.enum(["celsius", "fahrenheit"]).optional().default("celsius"),
    }),
    handler: async ({ city, units }) => {
        // Simulated weather API call
        const temp = Math.floor(Math.random() * 30) + 10;
        return {
            city,
            temperature: units === "fahrenheit" ? temp * 9/5 + 32 : temp,
            units,
            condition: "sunny",
        };
    },
});

// Define tool with JSON schema
const searchTool = defineTool("search_database", {
    description: "Search internal database for records",
    parameters: {
        type: "object",
        properties: {
            query: { type: "string", description: "Search query" },
            limit: { type: "number", description: "Max results" },
        },
        required: ["query"],
    },
    handler: async ({ query, limit = 10 }) => {
        const results = await database.search(query, limit);
        return results;
    },
});

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    tools: [weatherTool, searchTool],
});

// Copilot will automatically call tools when needed
await session.sendAndWait({
    prompt: "What's the weather in Tokyo and find related travel records?"
});

await session.destroy();
await client.stop();
```

## Session Hooks - Intercept and Customize Behavior

Hooks allow you to intercept tool calls, modify prompts, add context, and handle errors at key points in the session lifecycle.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const BLOCKED_TOOLS = ["shell", "bash", "exec"];

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    hooks: {
        // Control tool execution permissions
        onPreToolUse: async (input, invocation) => {
            console.log(`Tool: ${input.toolName}, Args: ${JSON.stringify(input.toolArgs)}`);

            if (BLOCKED_TOOLS.includes(input.toolName)) {
                return {
                    permissionDecision: "deny",
                    permissionDecisionReason: "Shell access not permitted",
                };
            }

            return {
                permissionDecision: "allow",
                modifiedArgs: input.toolArgs,  // Optionally modify arguments
                additionalContext: "Execute safely",
            };
        },

        // Process tool results
        onPostToolUse: async (input, invocation) => {
            console.log(`Result: ${JSON.stringify(input.toolResult)}`);
            return {
                additionalContext: "Tool executed successfully",
            };
        },

        // Modify user prompts
        onUserPromptSubmitted: async (input, invocation) => {
            return {
                modifiedPrompt: `[AUDIT] ${input.prompt}`,
            };
        },

        // Add context at session start
        onSessionStart: async (input, invocation) => {
            return {
                additionalContext: "User prefers TypeScript examples.",
            };
        },

        // Handle errors
        onErrorOccurred: async (input, invocation) => {
            console.error(`Error: ${input.error}`);
            return {
                errorHandling: "retry",  // "retry" | "skip" | "abort"
            };
        },
    },
});

await session.sendAndWait({ prompt: "List files and run tests" });
await session.destroy();
await client.stop();
```

## BYOK - Bring Your Own Key (Custom Providers)

Configure custom API providers to use your own API keys from OpenAI, Azure, Anthropic, Ollama, or other OpenAI-compatible endpoints.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();

// OpenAI Direct
const openaiSession = await client.createSession({
    model: "gpt-4",
    provider: {
        type: "openai",
        baseUrl: "https://api.openai.com/v1",
        apiKey: process.env.OPENAI_API_KEY,
    },
});

// Azure OpenAI
const azureSession = await client.createSession({
    model: "gpt-4",
    provider: {
        type: "azure",  // Must be "azure" for *.openai.azure.com
        baseUrl: "https://my-resource.openai.azure.com",
        apiKey: process.env.AZURE_OPENAI_KEY,
        azure: { apiVersion: "2024-10-21" },
    },
});

// Anthropic Claude
const claudeSession = await client.createSession({
    model: "claude-3-opus-20240229",
    provider: {
        type: "anthropic",
        baseUrl: "https://api.anthropic.com",
        apiKey: process.env.ANTHROPIC_API_KEY,
    },
});

// Ollama (local)
const ollamaSession = await client.createSession({
    model: "llama2",
    provider: {
        type: "openai",
        baseUrl: "http://localhost:11434/v1",
        // No API key needed for local Ollama
    },
});

// Azure AI Foundry (OpenAI-compatible endpoint)
const foundrySession = await client.createSession({
    model: "gpt-4-turbo",
    provider: {
        type: "openai",
        baseUrl: "https://your-resource.openai.azure.com/openai/v1/",
        apiKey: process.env.FOUNDRY_API_KEY,
        wireApi: "responses",  // "completions" or "responses"
    },
});

await client.stop();
```

## MCP Servers - Integrate External Tools

Connect to MCP (Model Context Protocol) servers to extend Copilot's capabilities with external tools and data sources.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    mcpServers: {
        // Local MCP server (stdio)
        filesystem: {
            type: "local",
            command: "npx",
            args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
            env: { DEBUG: "true" },
            cwd: "./servers",
            tools: ["*"],  // "*" = all tools, [] = none
            timeout: 30000,
        },

        // Custom local server
        database: {
            type: "local",
            command: "node",
            args: ["./mcp-db-server.js"],
            tools: ["query", "insert", "update"],
        },

        // Remote MCP server (HTTP/SSE)
        github: {
            type: "http",
            url: "https://api.githubcopilot.com/mcp/",
            headers: {
                Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
            },
            tools: ["*"],
        },
    },
});

// The model can now use MCP server tools
const response = await session.sendAndWait({
    prompt: "List files in /tmp and check my GitHub notifications",
});

console.log(response?.data.content);
await session.destroy();
await client.stop();
```

## User Input Requests - Interactive Agent Prompts

Enable the agent to ask questions to users during task execution using the `ask_user` tool.

```typescript
import { CopilotClient } from "@github/copilot-sdk";
import * as readline from "readline";

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
});

const askQuestion = (question: string): Promise<string> => {
    return new Promise((resolve) => rl.question(question, resolve));
};

const client = new CopilotClient();
const session = await client.createSession({
    model: "gpt-4.1",
    onUserInputRequest: async (request, invocation) => {
        console.log(`\nAgent asks: ${request.question}`);

        if (request.choices && request.choices.length > 0) {
            console.log("Options:");
            request.choices.forEach((choice, i) => {
                console.log(`  ${i + 1}. ${choice}`);
            });

            const selection = await askQuestion("Select option (or type custom): ");
            const index = parseInt(selection) - 1;

            if (index >= 0 && index < request.choices.length) {
                return {
                    answer: request.choices[index],
                    wasFreeform: false,
                };
            }
        }

        const answer = await askQuestion("Your response: ");
        return {
            answer,
            wasFreeform: true,
        };
    },
});

await session.sendAndWait({
    prompt: "Help me set up a new project. Ask me what language I prefer.",
});

rl.close();
await session.destroy();
await client.stop();
```

## Session Management - List, Resume, and Delete Sessions

Manage session lifecycle including listing all sessions, resuming previous sessions, and deleting session data.

```typescript
import { CopilotClient } from "@github/copilot-sdk";

const client = new CopilotClient();
await client.start();

// List all sessions
const sessions = await client.listSessions();
console.log("Available sessions:");
sessions.forEach((s) => {
    console.log(`  - ${s.sessionId} (${s.startTime.toISOString()})`);
    console.log(`    Summary: ${s.summary || "No summary"}`);
    console.log(`    Context: ${s.context?.cwd || "Unknown"}`);
});

// Filter sessions by working directory
const filteredSessions = await client.listSessions({
    cwd: "/path/to/project",
});

// Resume an existing session
const resumedSession = await client.resumeSession("existing-session-id", {
    tools: [myTool],  // Add tools when resuming
    streaming: true,
});

// Continue conversation
await resumedSession.sendAndWait({
    prompt: "Continue from where we left off",
});

// Get session message history
const messages = await resumedSession.getMessages();
console.log(`Session has ${messages.length} events`);

// Delete a session permanently
await client.deleteSession("old-session-id");

// Abort current processing
await resumedSession.abort();

await resumedSession.destroy();
await client.stop();
```

## Python SDK - Complete Example

The Python SDK provides async/await native support with full type hints and Pydantic integration for tool definitions.

```python
import asyncio
import sys
from pydantic import BaseModel, Field
from copilot import CopilotClient
from copilot.tools import define_tool
from copilot.generated.session_events import SessionEventType

# Define tool parameters with Pydantic
class WeatherParams(BaseModel):
    city: str = Field(description="City name to get weather for")
    units: str = Field(default="celsius", description="Temperature units")

@define_tool(description="Get current weather for a city")
async def get_weather(params: WeatherParams) -> dict:
    return {
        "city": params.city,
        "temperature": 22,
        "units": params.units,
        "condition": "sunny",
    }

async def main():
    client = CopilotClient({
        "log_level": "info",
        "auto_restart": True,
    })
    await client.start()

    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "tools": [get_weather],
        "system_message": {
            "mode": "append",
            "content": "Always provide concise answers.",
        },
    })

    # Handle streaming events
    def on_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content or "")
            sys.stdout.flush()
        elif event.type == SessionEventType.SESSION_IDLE:
            print("\n--- Done ---")

    session.on(on_event)

    # Send message
    await session.send_and_wait({
        "prompt": "What's the weather in Paris?"
    })

    # Get message history
    messages = await session.get_messages()
    print(f"Total events: {len(messages)}")

    await session.destroy()
    await client.stop()

asyncio.run(main())
```

## Go SDK - Complete Example

The Go SDK provides type-safe tool definitions with automatic JSON schema generation using struct tags.

```go
package main

import (
    "context"
    "fmt"
    "log"
    "os"

    copilot "github.com/github/copilot-sdk/go"
)

// Tool parameter struct with JSON schema tags
type WeatherParams struct {
    City  string `json:"city" jsonschema:"City name to get weather for"`
    Units string `json:"units" jsonschema:"Temperature units (celsius/fahrenheit)"`
}

type WeatherResult struct {
    City        string `json:"city"`
    Temperature int    `json:"temperature"`
    Condition   string `json:"condition"`
}

func main() {
    ctx := context.Background()

    // Define tool with DefineTool helper
    weatherTool := copilot.DefineTool(
        "get_weather",
        "Get current weather for a city",
        func(params WeatherParams, inv copilot.ToolInvocation) (WeatherResult, error) {
            return WeatherResult{
                City:        params.City,
                Temperature: 22,
                Condition:   "sunny",
            }, nil
        },
    )

    client := copilot.NewClient(&copilot.ClientOptions{
        LogLevel:   "error",
        AutoStart:  copilot.Bool(true),
        GitHubToken: os.Getenv("GITHUB_TOKEN"),
    })

    if err := client.Start(ctx); err != nil {
        log.Fatal(err)
    }
    defer client.Stop()

    session, err := client.CreateSession(ctx, &copilot.SessionConfig{
        Model:     "gpt-4.1",
        Streaming: true,
        Tools:     []copilot.Tool{weatherTool},
        InfiniteSessions: &copilot.InfiniteSessionConfig{
            Enabled: copilot.Bool(true),
        },
    })
    if err != nil {
        log.Fatal(err)
    }
    defer session.Destroy()

    // Handle streaming events
    done := make(chan bool)
    session.On(func(event copilot.SessionEvent) {
        switch event.Type {
        case "assistant.message_delta":
            if event.Data.DeltaContent != nil {
                fmt.Print(*event.Data.DeltaContent)
            }
        case "assistant.message":
            fmt.Println("\n--- Complete ---")
        case "session.idle":
            close(done)
        }
    })

    _, err = session.SendAndWait(ctx, copilot.MessageOptions{
        Prompt: "What's the weather in Tokyo?",
    })
    if err != nil {
        log.Fatal(err)
    }

    <-done
}
```

## .NET SDK - Complete Example

The .NET SDK integrates with Microsoft.Extensions.AI for tool definitions and provides full async/await support with IDisposable patterns.

```csharp
using GitHub.Copilot.SDK;
using Microsoft.Extensions.AI;
using System.ComponentModel;

// Define tools using AIFunctionFactory
var weatherTool = AIFunctionFactory.Create(
    async ([Description("City name")] string city,
           [Description("Temperature units")] string units = "celsius") =>
    {
        await Task.Delay(100); // Simulate API call
        return new
        {
            city,
            temperature = 22,
            units,
            condition = "sunny"
        };
    },
    "get_weather",
    "Get current weather for a city"
);

await using var client = new CopilotClient(new CopilotClientOptions
{
    LogLevel = "info",
    AutoRestart = true,
    GitHubToken = Environment.GetEnvironmentVariable("GITHUB_TOKEN"),
});

await client.StartAsync();

await using var session = await client.CreateSessionAsync(new SessionConfig
{
    Model = "gpt-4.1",
    Streaming = true,
    Tools = [weatherTool],
    SystemMessage = new SystemMessageConfig
    {
        Mode = SystemMessageMode.Append,
        Content = "Provide concise, helpful answers."
    },
    InfiniteSessions = new InfiniteSessionConfig
    {
        Enabled = true,
        BackgroundCompactionThreshold = 0.80
    }
});

var done = new TaskCompletionSource();

session.On(evt =>
{
    switch (evt)
    {
        case AssistantMessageDeltaEvent delta:
            Console.Write(delta.Data.DeltaContent);
            break;
        case AssistantMessageEvent msg:
            Console.WriteLine($"\n--- Final: {msg.Data.Content?.Length} chars ---");
            break;
        case ToolExecutionStartEvent tool:
            Console.WriteLine($"[Tool: {tool.Data.ToolName}]");
            break;
        case SessionIdleEvent:
            done.SetResult();
            break;
    }
});

await session.SendAsync(new MessageOptions
{
    Prompt = "What's the weather in London?",
    Attachments = new List<UserMessageDataAttachmentsItem>
    {
        new() { Type = UserMessageDataAttachmentsItemType.File, Path = "/path/to/context.txt" }
    }
});

await done.Task;

// Get session history
var messages = await session.GetMessagesAsync();
Console.WriteLine($"Session had {messages.Count} events");
```

## Summary

The GitHub Copilot SDK enables developers to embed sophisticated AI assistants into applications across TypeScript, Python, Go, and .NET. Primary use cases include building interactive CLI tools, code review assistants, documentation generators, automated testing frameworks, and custom development workflows. The SDK handles complex orchestration automatically while exposing hooks for fine-grained control over tool permissions, prompt modification, and error handling.

Integration patterns typically involve creating a CopilotClient, establishing sessions with custom tools and system prompts, and handling streaming events for real-time feedback. For enterprise deployments, BYOK support allows organizations to use their own API keys and model providers. MCP server integration extends capabilities with external tools, while session management APIs enable persistent conversations across application restarts. The session hooks system provides audit logging, security controls, and customization points for compliance requirements.
