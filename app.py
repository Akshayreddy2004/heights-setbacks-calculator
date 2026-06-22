from unittest import result

from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load Excel File
rules = pd.read_excel("NMR_Rules_Full_Table.xlsx")


def setback_display(value_ft):

    total_feet = float(value_ft)

    feet = int(total_feet)

    inches = round((total_feet - feet) * 12)

    if inches == 12:
        feet += 1
        inches = 0

    return f"{feet}'{inches}''"

def height_display(value_ft):

    total_feet = float(value_ft)

    feet = int(total_feet)

    inches = round((total_feet - feet) * 12)

    if inches == 12:
        feet += 1
        inches = 0

    return f"{feet}'{inches}''"


@app.route("/", methods=["GET", "POST"])
def home():

    results = []

    plot_size = ""
    road_width = ""

    if request.method == "POST":

        plot_size = float(request.form["plot_size"])
        road_width = float(request.form["road_width"])

        for _, row in rules.iterrows():

            plot_range = str(row["Plot Size (Ankanams)"])

            match_plot = False

            # Less than 7.5
            if "Less than" in plot_range:

                limit = float(
                    plot_range.replace("Less than", "").strip()
                )

                if plot_size < limit:
                    match_plot = True

            # Above 299
            elif "Above" in plot_range:

                limit = float(
                    plot_range.replace("Above", "").strip()
                )

                if plot_size > limit:
                    match_plot = True

            # 45 – 75 etc
            elif "–" in plot_range:

                low, high = plot_range.split("–")

                low = float(low.strip())
                high = float(high.strip())

                if low <= plot_size <= high:
                    match_plot = True

            if not match_plot:
                continue

            road_rule = str(row["Abutting Road Width (ft)"])

            match_road = False

            # All Roads
            if road_rule == "All Roads":

                match_road = True

            # Up to 39.4 ft Road
            elif "Up to" in road_rule:

                limit = float(
                    road_rule.replace("Up to", "")
                    .replace("ft Road", "")
                    .strip()
                )

                if road_width <= limit:
                    match_road = True

            # Above 39.4 ft Road
            elif "Above" in road_rule and "Road" in road_rule:

                limit = float(
                    road_rule.replace("Above", "")
                    .replace("ft Road", "")
                    .strip()
                )

                if road_width > limit:
                    match_road = True

            # 39.4–59.1 ft Road
            elif "39.4–59.1" in road_rule:

                if 39.4 <= road_width <= 59.1:
                    match_road = True

            # 59.1–78.7 ft Road
            elif "59.1–78.7" in road_rule:

                if 59.1 <= road_width <= 78.7:
                    match_road = True

            # 39.4 ft & Above Road
            elif "39.4 ft & Above" in road_rule:

                if road_width >= 39.4:
                    match_road = True

            if match_road:

                result = row.to_dict()

                # Height -> ONLY FEET
                # Height -> FEET + INCHES
                height_ft = float(
                    result["Height Permissible (ft)"]
                )

                result["Height Display"] = height_display(
                    height_ft
             )

                # Front Setback -> FEET + INCHES ONLY
                front_ft = float(
                    result["Front Setback (ft)"]
                )

                result["Front Display"] = setback_display(
                    front_ft
                )

                # Side/Rear Setback -> FEET + INCHES ONLY
                side_ft = float(
                    result["Remaining Side/Rear Setbacks (ft)"]
                )

                result["Side Display"] = setback_display(
                    side_ft
                )

                results.append(result)

    return render_template(
        "index.html",
        results=results,
        plot_size=plot_size,
        road_width=road_width
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)