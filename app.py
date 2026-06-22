import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load Excel File
rules = pd.read_excel("NMR_Rules_Full_Table.xlsx")


def format_feet_inches(value_ft):
    """Converts a decimal foot value to a formatted feet'inches'' string."""
    try:
        total_feet = float(value_ft)
        feet = int(total_feet)

        # Standard rounding: 4.44 becomes 4. Change round() to math.ceil() if you want 5.
        inches = round((total_feet - feet) * 12)

        if inches == 12:
            feet += 1
            inches = 0

        return f"{feet}'{inches}''"
    except (ValueError, TypeError):
        return "N/A"


@app.route("/", methods=["GET", "POST"])
def home():
    results = []
    plot_size = ""
    road_width = ""

    if request.method == "POST":
        try:
            plot_size = float(request.form["plot_size"])
            road_width = float(request.form["road_width"])
        except ValueError:
            # Handle empty or invalid numeric inputs safely
            return render_template(
                "index.html",
                results=[],
                plot_size=plot_size,
                road_width=road_width,
                error="Please enter valid numbers.",
            )

        for _, row in rules.iterrows():
            plot_range = str(row["Plot Size (Ankanams)"])
            match_plot = False

            # 1. Evaluate Plot Size Range
            if "Less than" in plot_range:
                limit = float(plot_range.replace("Less than", "").strip())
                if plot_size < limit:
                    match_plot = True

            elif "Above" in plot_range:
                limit = float(plot_range.replace("Above", "").strip())
                if plot_size > limit:
                    match_plot = True

            elif "–" in plot_range or "-" in plot_range:
                dash = "–" if "–" in plot_range else "-"
                low, high = plot_range.split(dash)
                if float(low.strip()) <= plot_size <= float(high.strip()):
                    match_plot = True

            if not match_plot:
                continue

            # 2. Evaluate Abutting Road Width Rule
            road_rule = str(row["Abutting Road Width (ft)"])
            # Remove spaces and standardize dashes for stable evaluation strings
            normalized_road_rule = (
                road_rule.replace(" ", "").replace("–", "-").strip()
            )
            match_road = False

            if road_rule == "All Roads":
                match_road = True

            elif "Upto" in normalized_road_rule:
                limit = float(
                    normalized_road_rule.replace("Upto", "")
                    .replace("ftRoad", "")
                    .strip()
                )
                if road_width <= limit:
                    match_road = True

            elif "Above" in normalized_road_rule and "Road" in road_rule:
                limit = float(
                    normalized_road_rule.replace("Above", "")
                    .replace("ftRoad", "")
                    .strip()
                )
                if road_width > limit:
                    match_road = True

            elif "39.4-59.1" in normalized_road_rule:
                if 39.4 <= road_width <= 59.1:
                    match_road = True

            elif "59.1-78.7" in normalized_road_rule:
                if 59.1 <= road_width <= 78.7:
                    match_road = True

            elif "39.4ft&Above" in normalized_road_rule:
                if road_width >= 39.4:
                    match_road = True

            # 3. Compile and Process Matched Row Details
            if match_road:
                matched_rule = row.to_dict()

                # Apply unified conversion and formatting utility helper function
                matched_rule["Height Display"] = format_feet_inches(
                    matched_rule["Height Permissible (ft)"]
                )
                matched_rule["Front Display"] = format_feet_inches(
                    matched_rule["Front Setback (ft)"]
                )
                matched_rule["Side Display"] = format_feet_inches(
                    matched_rule["Remaining Side/Rear Setbacks (ft)"]
                )

                results.append(matched_rule)

    return render_template(
        "index.html",
        results=results,
        plot_size=plot_size,
        road_width=road_width,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
