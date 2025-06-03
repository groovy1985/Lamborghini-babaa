# （上部はそのまま省略：importと関数群は同じ）

# ✅ CLIエントリーポイント（修正済）
if __name__ == "__main__":
    today = datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["weekly", "monthly"], required=False)
    args = parser.parse_args()

    mode = args.mode

    if not mode:
        if today.day == 1:
            mode = "monthly"
        elif today.weekday() == 1:
            mode = "weekly"
        else:
            print("🚫 自動判定による対象日ではありません（mode未指定）")
            exit(0)

    print(f"🧭 実行モード：{mode}")

    if mode == "weekly":
        generate_weekly_note()
    elif mode == "monthly":
        generate_monthly_zine()
