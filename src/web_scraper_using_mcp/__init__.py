def main() -> None:
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import main as mcp_main
    mcp_main.main()
