"""
Research Paper & Code Analysis Agent
Uses AgentRouter API to analyze research papers and their associated code.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

from readers import read_paper, read_code_file, scan_folder

load_dotenv()

AGENTROUTER_API_KEY = os.getenv("AGENTROUTER_API_KEY")
AGENTROUTER_BASE_URL = os.getenv("AGENTROUTER_BASE_URL", "https://api.agentrouter.ai/v1")
MODEL = os.getenv("AGENTROUTER_MODEL", "gpt-4o")

PAPER_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs", ".r", ".ipynb", ".sh", ".yaml", ".yml", ".json", ".toml"}


def get_client() -> OpenAI:
    if not AGENTROUTER_API_KEY:
        print("Error: AGENTROUTER_API_KEY not set. Add it to your .env file or environment.")
        sys.exit(1)
    return OpenAI(api_key=AGENTROUTER_API_KEY, base_url=AGENTROUTER_BASE_URL)


def chat(client: OpenAI, messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
    )
    return response.choices[0].message.content


def analyse_paper(client: OpenAI, paper_content: str, paper_name: str) -> dict:
    print(f"\n[*] Analysing paper: {paper_name}")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert research paper analyst. "
                "Provide structured, detailed analysis of academic papers. "
                "Focus on: main contributions, methodology, datasets, results, and limitations."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Analyse the following research paper titled '{paper_name}'.\n\n"
                "Provide a structured analysis with these sections:\n"
                "1. **Summary** (2-3 sentences)\n"
                "2. **Key Contributions** (bullet points)\n"
                "3. **Methodology** (how the approach works)\n"
                "4. **Datasets & Experiments** (what was tested)\n"
                "5. **Results & Claims** (key numbers/findings)\n"
                "6. **Limitations & Future Work**\n"
                "7. **Core Concepts** (list of important terms/algorithms used)\n\n"
                f"Paper content:\n\n{paper_content[:12000]}"
            ),
        },
    ]
    return {"name": paper_name, "analysis": chat(client, messages)}


def analyse_code(client: OpenAI, code_files: list[dict], paper_summary: str) -> dict:
    if not code_files:
        return {"analysis": "No code files found in the folder."}

    code_context = "\n\n".join(
        f"--- File: {f['name']} ---\n{f['content'][:3000]}"
        for f in code_files[:10]  # cap at 10 files to stay within token limits
    )

    print(f"[*] Analysing {len(code_files)} code file(s)...")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert code reviewer specialising in research implementations. "
                "Analyse code for correctness, clarity, and alignment with the described research."
            ),
        },
        {
            "role": "user",
            "content": (
                "The following code files implement (or relate to) a research paper.\n\n"
                f"**Paper Summary:**\n{paper_summary}\n\n"
                "Analyse the code and provide:\n"
                "1. **Architecture Overview** (high-level structure of the codebase)\n"
                "2. **Key Modules / Files** (what each important file does)\n"
                "3. **Algorithm Implementation** (how the core algorithm from the paper is implemented)\n"
                "4. **Alignment with Paper** (does the code match the paper's methodology?)\n"
                "5. **Code Quality** (readability, documentation, modularity)\n"
                "6. **Potential Issues or Bugs** (anything suspicious)\n"
                "7. **How to Run** (infer from scripts/READMEs if possible)\n\n"
                f"Code files:\n\n{code_context}"
            ),
        },
    ]
    return {"analysis": chat(client, messages), "files_analysed": [f["name"] for f in code_files]}


def cross_analyse(client: OpenAI, paper_analysis: str, code_analysis: str) -> str:
    print("[*] Running cross-analysis (paper ↔ code alignment)...")
    messages = [
        {
            "role": "system",
            "content": "You are a research scientist reviewing both a paper and its implementation.",
        },
        {
            "role": "user",
            "content": (
                "Given the paper analysis and code analysis below, provide a final cross-analysis:\n\n"
                "1. **Reproducibility Score** (1-10, with reasoning)\n"
                "2. **Missing Implementations** (claims in paper not reflected in code)\n"
                "3. **Undocumented Code** (code features not explained in the paper)\n"
                "4. **Suggested Improvements** (for both paper clarity and code quality)\n"
                "5. **Overall Assessment**\n\n"
                f"**Paper Analysis:**\n{paper_analysis}\n\n"
                f"**Code Analysis:**\n{code_analysis}"
            ),
        },
    ]
    return chat(client, messages)


def save_report(output: dict, folder: Path) -> Path:
    report_path = folder / "research_analysis_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Research Paper & Code Analysis Report\n\n")
        f.write(f"**Folder analysed:** `{folder}`\n\n")
        f.write("---\n\n")

        f.write("## Paper Analysis\n\n")
        for paper in output.get("papers", []):
            f.write(f"### {paper['name']}\n\n")
            f.write(paper["analysis"])
            f.write("\n\n---\n\n")

        f.write("## Code Analysis\n\n")
        code = output.get("code", {})
        if code.get("files_analysed"):
            f.write(f"**Files analysed:** {', '.join(code['files_analysed'])}\n\n")
        f.write(code.get("analysis", ""))
        f.write("\n\n---\n\n")

        f.write("## Cross-Analysis (Paper ↔ Code)\n\n")
        f.write(output.get("cross_analysis", ""))
        f.write("\n")

    return report_path


def run_agent(folder: str) -> None:
    folder_path = Path(folder).expanduser().resolve()
    if not folder_path.exists() or not folder_path.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Research Analysis Agent")
    print(f"  Folder: {folder_path}")
    print(f"{'='*60}")

    client = get_client()

    paper_files, code_files_raw = scan_folder(folder_path, PAPER_EXTENSIONS, CODE_EXTENSIONS)

    if not paper_files and not code_files_raw:
        print("No recognisable paper or code files found in the folder.")
        sys.exit(0)

    print(f"\nFound {len(paper_files)} paper(s) and {len(code_files_raw)} code file(s).")

    # --- Analyse papers ---
    paper_results = []
    combined_paper_summary = ""
    for pf in paper_files:
        content = read_paper(pf)
        if not content.strip():
            print(f"  [!] Could not extract text from {pf.name}, skipping.")
            continue
        result = analyse_paper(client, content, pf.name)
        paper_results.append(result)
        combined_paper_summary += result["analysis"] + "\n\n"

    # --- Analyse code ---
    code_data = [{"name": cf.name, "content": read_code_file(cf)} for cf in code_files_raw]
    code_result = analyse_code(client, code_data, combined_paper_summary or "No paper content available.")

    # --- Cross-analysis ---
    cross = ""
    if paper_results and code_data:
        cross = cross_analyse(client, combined_paper_summary, code_result["analysis"])

    output = {
        "papers": paper_results,
        "code": code_result,
        "cross_analysis": cross,
    }

    report_path = save_report(output, folder_path)
    print(f"\n{'='*60}")
    print(f"  Analysis complete!")
    print(f"  Report saved to: {report_path}")
    print(f"{'='*60}\n")

    # Print summary to terminal
    for paper in paper_results:
        print(f"\n{'─'*60}")
        print(f"PAPER: {paper['name']}")
        print(f"{'─'*60}")
        print(paper["analysis"])

    print(f"\n{'─'*60}")
    print("CODE ANALYSIS")
    print(f"{'─'*60}")
    print(code_result["analysis"])

    if cross:
        print(f"\n{'─'*60}")
        print("CROSS-ANALYSIS")
        print(f"{'─'*60}")
        print(cross)


def interactive_mode(folder: str) -> None:
    """Follow-up Q&A session after the initial analysis."""
    folder_path = Path(folder).expanduser().resolve()
    client = get_client()

    paper_files, code_files_raw = scan_folder(folder_path, PAPER_EXTENSIONS, CODE_EXTENSIONS)
    context_parts = []
    for pf in paper_files:
        content = read_paper(pf)
        if content.strip():
            context_parts.append(f"[Paper: {pf.name}]\n{content[:6000]}")
    for cf in code_files_raw[:5]:
        content = read_code_file(cf)
        if content.strip():
            context_parts.append(f"[Code: {cf.name}]\n{content[:2000]}")

    combined_context = "\n\n".join(context_parts)
    history: list[dict] = [
        {
            "role": "system",
            "content": (
                "You are an expert research assistant with full access to the following research paper(s) and code.\n\n"
                f"{combined_context}\n\n"
                "Answer questions clearly and cite specific parts of the paper or code when relevant."
            ),
        }
    ]

    print("\nEntering interactive Q&A mode. Type 'exit' or 'quit' to stop.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        history.append({"role": "user", "content": user_input})
        response = chat(client, history)
        history.append({"role": "assistant", "content": response})
        print(f"\nAgent: {response}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Research Paper & Code Analysis Agent (powered by AgentRouter)"
    )
    parser.add_argument("folder", help="Path to the folder containing your research paper and code")
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="After analysis, enter interactive Q&A mode to ask questions about the paper/code",
    )
    parser.add_argument(
        "--api-key", "-k",
        help="AgentRouter API key (overrides AGENTROUTER_API_KEY env variable)",
    )
    parser.add_argument(
        "--model", "-m",
        default=None,
        help="Model to use via AgentRouter (default: gpt-4o)",
    )
    args = parser.parse_args()

    # Allow inline API key override
    if args.api_key:
        os.environ["AGENTROUTER_API_KEY"] = args.api_key

    if args.model:
        global MODEL
        MODEL = args.model

    run_agent(args.folder)

    if args.interactive:
        interactive_mode(args.folder)


if __name__ == "__main__":
    main()
