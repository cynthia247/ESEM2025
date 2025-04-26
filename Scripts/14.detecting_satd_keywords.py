import os
import pandas as pd

# Define keyword patterns for each community smell
COMMUNITY_SMELL_KEYWORDS = {
    "Prima Donna Effect": [
        "only [a-z]* knows", "only .* understands", "not changing .* code",
        "legacy code from", "waiting for .* to review", "needs approval from", "don't want to change"
    ],
    "Toxic Communication": [
        "someone broke this", "who wrote this", "this mess", "do it right", "not my code",
        "ask .*", "tired of fixing", "nobody follows", "garbage", "idiot", "blame"
    ],
    "Black Cloud Effect": [
        "again", "as usual", "always my job", "stuck with", "still assigned",
        "once again", "nobody else", "have to clean up", "legacy workaround"
    ]
}

def detect_smell_keywords(text, patterns):
    text_lower = text.lower()
    found = []
    for smell, keywords in patterns.items():
        for pattern in keywords:
            if pattern in text_lower:
                found.append(smell)
                break  # Only need one match to assign the smell
    return found

def analyze_satd_comments(folder_path):
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)

            if 'Commit Message' not in df.columns:
                print(f"⚠️ Skipping {filename}: 'Comment' column not found.")
                continue

            for index, row in df.iterrows():
                comment = str(row['Commit Message'])  # Ensure it's a string
                matched_smells = detect_smell_keywords(comment, COMMUNITY_SMELL_KEYWORDS)
                if matched_smells:
                    results.append({
                        'File': filename,
                        'Index': index,
                        'Comment': comment,
                        'Detected Smells': ', '.join(matched_smells)
                    })

    return pd.DataFrame(results)

# Example usage
if __name__ == "__main__":
    folder = "satd-datasets/only-satd-comments"
    result_df = analyze_satd_comments(folder)
    result_df.to_csv("community_smell_satd_matches.csv", index=False)
    print("✅ Analysis complete. Results saved to 'community_smell_satd_matches.csv'.")
    print(result_df.head())
