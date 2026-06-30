import json

with open("browser_history.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("actions_results.txt", "w", encoding="utf-8") as out:

    for step in data.get("history", []):

        model_output = step.get("model_output")

        if not model_output:
            continue

        actions = model_output.get("action", [])
        results = step.get("result", [])

        for action, result in zip(actions, results):

            action_name = list(action.keys())[0]
            action_data = action[action_name]

            out.write(f"ACTION TYPE: {action_name}\n")
            out.write(f"ACTION DATA: {action_data}\n")

            if isinstance(result, dict):
                out.write(
                    f"RESULT: {result.get('extracted_content', '')}\n"
                )

            out.write("-" * 80 + "\n")

print("Done")