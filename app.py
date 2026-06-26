import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# Load Excel Files
ankanam_rules = pd.read_excel("NMR_Rules_Full_Table.xlsx")
sqm_rules = pd.read_excel("NMR_Rules_SQM.xlsx")


def format_feet_inches(value_ft):
    try:
        total_feet = float(value_ft)

        feet = int(total_feet)

        inches = round((total_feet - feet) * 12)

        if inches == 12:
            feet += 1
            inches = 0

        return f"{feet}'{inches}''"

    except:
        return "N/A"


@app.route("/", methods=["GET", "POST"])
def home():

    results = []

    plot_size = ""

    road_width = ""

    unit_type = "ankanams"

    if request.method == "POST":

        unit_type = request.form["unit_type"]

        try:

            plot_size = float(
                request.form["plot_size"]
            )

            road_width = float(
                request.form["road_width"]
            )

        except:

            return render_template(
                "index.html",
                results=[],
                plot_size="",
                road_width="",
                unit_type=unit_type
            )

        rules = (
            ankanam_rules
            if unit_type == "ankanams"
            else sqm_rules
        )

        for _, row in rules.iterrows():

            # =====================
            # PLOT SIZE COLUMN
            # =====================

            if unit_type == "ankanams":

                plot_range = str(
                    row["Plot Size (Ankanams)"]
                )

            else:

                plot_range = str(
                    row["Plot Size (Sq.Mts)"]
                )

            match_plot = False

            if "Less than" in plot_range:

                limit = float(
                    plot_range.replace(
                        "Less than",
                        ""
                    ).strip()
                )

                if plot_size < limit:
                    match_plot = True

            elif "Above" in plot_range:

                limit = float(
                    plot_range.replace(
                        "Above",
                        ""
                    ).strip()
                )

                if plot_size > limit:
                    match_plot = True

            elif "-" in plot_range or "–" in plot_range:

                dash = (
                    "–"
                    if "–" in plot_range
                    else "-"
                )

                low, high = plot_range.split(
                    dash
                )

                low = float(low.strip())

                high = float(high.strip())

                if (
                    low
                    <= plot_size
                    <= high
                ):
                    match_plot = True

            if not match_plot:
                continue

            # =====================
            # ROAD WIDTH
            # =====================

            if unit_type == "ankanams":

                road_rule = str(
                    row[
                        "Abutting Road Width (ft)"
                    ]
                )

            else:

                road_rule = str(
                    row[
                        "Abutting Road Width (m)"
                    ]
                )

            match_road = False

            normalized = (
                road_rule
                .replace(" ", "")
                .replace("–", "-")
            )

            if road_rule == "All Roads":

                match_road = True

            elif "Upto" in normalized:

                try:

                    limit = float(
                        normalized
                        .replace("Upto", "")
                        .replace("m", "")
                        .replace("ftRoad", "")
                    )

                    if road_width <= limit:
                        match_road = True

                except:
                    pass

            elif (
                "Above" in road_rule
                and "12m" in road_rule
            ):

                if road_width > 12:
                    match_road = True

            elif (
                "Above" in road_rule
                and "18m" in road_rule
            ):

                if road_width > 18:
                    match_road = True

            elif (
                "Above" in road_rule
                and "24m" in road_rule
            ):

                if road_width > 24:
                    match_road = True

            elif (
                "12m and above"
                in road_rule
            ):

                if road_width >= 12:
                    match_road = True

            elif (
                "39.4-59.1"
                in normalized
            ):

                if (
                    39.4
                    <= road_width
                    <= 59.1
                ):
                    match_road = True

            elif (
                "59.1-78.7"
                in normalized
            ):

                if (
                    59.1
                    <= road_width
                    <= 78.7
                ):
                    match_road = True

            elif (
                "39.4ft&Above"
                in normalized
            ):

                if road_width >= 39.4:
                    match_road = True

            if not match_road:
                continue

            # =====================
            # RESULT
            # =====================

            matched_rule = row.to_dict()

            if unit_type == "ankanams":

                matched_rule[
                    "Height Display"
                ] = format_feet_inches(
                    matched_rule[
                        "Height Permissible (ft)"
                    ]
                )

                matched_rule[
                    "Front Display"
                ] = format_feet_inches(
                    matched_rule[
                        "Front Setback (ft)"
                    ]
                )

                matched_rule[
                    "Side Display"
                ] = format_feet_inches(
                    matched_rule[
                        "Remaining Side/Rear Setbacks (ft)"
                    ]
                )

            else:

                matched_rule[
                    "Height Display"
                ] = (
                    str(
                        matched_rule[
                            "Height Permissible (m)"
                        ]
                    )
                    + " m"
                )

                matched_rule[
                    "Front Display"
                ] = (
                    str(
                        matched_rule[
                            "Front Setback (m)"
                        ]
                    )
                    + " m"
                )

                matched_rule[
                    "Side Display"
                ] = (
                    str(
                        matched_rule[
                            "Remaining Side/Rear Setbacks (m)"
                        ]
                    )
                    + " m"
                )

            results.append(
                matched_rule
            )

    return render_template(
        "index.html",
        results=results,
        plot_size=plot_size,
        road_width=road_width,
        unit_type=unit_type
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )