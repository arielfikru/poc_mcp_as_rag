"""
Orchestrator: MCP Client + ReAct Agent Loop
Terhubung ke 3 MCP Agents (Konteks Auditor terintegrasi di A & C):
  - Agent A (server_a_postgres.py): SQLite Database & Salary Anomaly Check
  - Agent B (server_b_hr.py):       HR Knowledge Base
  - Agent C (server_c_it.py):       IT Policy, Access Violations, Monitoring & Audit Docs

Usage:
  python orchestrator.py "pertanyaan Anda di sini"
"""
import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from dotenv import load_dotenv

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from openai import AsyncOpenAI

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

TARGET_MODEL = "z-ai/glm-5.1"

# Definisi 3 Agent MCP (Auditor terintegrasi sebagai tema)
AGENTS = [
    {
        "name": "Agent A - Database",
        "script": "server_a_postgres.py",
    },
    {
        "name": "Agent B - HR Knowledge Base",
        "script": "server_b_hr.py",
    },
    {
        "name": "Agent C - IT Policy Knowledge Base",
        "script": "server_c_it.py",
    },
]


async def main():
    if len(sys.argv) > 1:
        initial_prompt = " ".join(sys.argv[1:])
    else:
        initial_prompt = (
            "Cari tahu nama dan role karyawan dengan ID 103, "
            "lalu cek apakah role tersebut diperbolehkan mengakses server produksi, "
            "dan juga jelaskan berapa cuti tahunan yang dia berhak dapatkan."
        )

    async with AsyncExitStack() as stack:
        print("\n" + "=" * 60)
        print("  🤖 AURESYS AI ORCHESTRATOR v2 — Multi-Agent MCP PoC")
        print("  📋 Agents: DB (Audited) | HR | IT & Policies (Audited)")
        print("=" * 60)
        print(f"\n[System] Menghubungkan ke {len(AGENTS)} MCP Agents...")

        sessions = []
        tool_to_session = {}
        all_tools = []

        for agent in AGENTS:
            params = StdioServerParameters(
                command=sys.executable,
                args=[agent["script"]],
            )
            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print(f"  ✅ {agent['name']}: Tools = {tool_names}")

            for t in tools_result.tools:
                tool_to_session[t.name] = {"session": session, "agent": agent["name"]}
                all_tools.append({
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema,
                    },
                })
            sessions.append(session)

        total_tools = [t["function"]["name"] for t in all_tools]
        print(f"\n[System] Total {len(total_tools)} tools siap digunakan: {total_tools}")
        print("\n" + "-" * 60)
        print(f"📝 User Prompt:\n   {initial_prompt}")
        print("-" * 60 + "\n")

        messages = [{"role": "user", "content": initial_prompt}]

        loop_count = 0
        while loop_count < 5:
            loop_count += 1
            print(f"🔄 [Iterasi {loop_count}] Memanggil LLM ({TARGET_MODEL})...")

            try:
                response = await client.chat.completions.create(
                    model=TARGET_MODEL,
                    messages=messages,
                    tools=all_tools,
                    tool_choice="auto",
                )
            except Exception as e:
                print(f"❌ [Error LLM] {e}")
                break

            msg = response.choices[0].message

            if msg.content:
                print(f"\n💬 [LLM Thinking]:\n{msg.content}\n")

            if not msg.tool_calls:
                print("✅ [System] LLM sudah selesai reasoning. Tidak ada tool lagi yang dipanggil.")
                print("\n" + "=" * 60)
                print("📌 JAWABAN AKHIR:")
                print("=" * 60)
                print(msg.content)
                print("=" * 60 + "\n")
                break

            # Append pesan asisten ke messages
            messages.append(msg)

            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = {}
                if tool_call.function.arguments:
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        print(f"  ⚠️ [Warning] Gagal parsing argumen: {tool_call.function.arguments}")

                agent_info = tool_to_session.get(tool_name)
                agent_label = agent_info["agent"] if agent_info else "UNKNOWN"
                print(f"  🔧 [{agent_label}] Tool Call → {tool_name}({tool_args})")

                if agent_info:
                    try:
                        result = await agent_info["session"].call_tool(tool_name, tool_args)
                        result_text = "\n".join(
                            [c.text for c in result.content if getattr(c, "type", "text") == "text"]
                        )
                        print(f"  📦 [Tool Result]:\n{result_text}\n")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": result_text or "Success (no output)",
                        })
                    except Exception as e:
                        err = f"Error saat eksekusi tool: {e}"
                        print(f"  ❌ [Tool Error] {err}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": err,
                        })
                else:
                    not_found = f"Tool '{tool_name}' tidak ditemukan di MCP servers manapun."
                    print(f"  ❌ [Error] {not_found}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": not_found,
                    })

        if loop_count >= 5:
            print("⚠️ [System] Mencapai batas maksimum iterasi (5). Loop dihentikan.")


if __name__ == "__main__":
    asyncio.run(main())
