import re

def update_game_counter(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Match the HTML table
    table_match = re.search(r"<table.*?>.*?</table>", content, re.DOTALL)
    if not table_match:
        print("No table found in README.")
        return False

    # Count rows in the table body
    table_html = table_match.group(0)
    row_count = len(re.findall(r"<tr>", table_html)) - 1  # Subtract header row

    # Update the counter in the <span>
    updated_content = re.sub(
        r'(<span id="counter">)\d+(</span>)',
        rf"\g<1>{row_count}\g<2>",
        content,
    )

    with open(file_path, "w") as file:
        file.write(updated_content)

    print(f"Updated game counter to {row_count} in README.md.")
    return True

if __name__ == "__main__":
    update_game_counter("README.md")
