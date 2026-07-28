#!/usr/bin/env python3
"""Create a reproducible color-segmented Figure 2 digitization scaffold."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
IMAGE = HERE / "rendered_pages/page-06.png"
OUTPUT = HERE / "leader_color_digitized_figure2.json"
TIMES = [0, 1, 2, 3, 4, 5, 12, 24]
CURVES = {
    "red": {"dose_fold_mic": 0.5, "rgb_rule": "R>170,G<115,B<115,R>G+70"},
    "green": {"dose_fold_mic": 1.0, "rgb_rule": "G>100,R<130,B<130,G>R+40"},
    "purple": {"dose_fold_mic": 5.0, "rgb_rule": "B>150,R>70,G<120,B>G+70,R>G+40"},
}

# Coordinates are in the original 1489 x 2105 rendered page. Axis endpoints
# were detected from the long black x/y-axis pixel runs; marker x positions
# were detected from high-density color components at the eight plotted times.
PANELS = {
    "A": {"target": "Escherichia coli ATCC 8739", "x": [226, 268, 310, 352, 394, 435.5, 449, 502], "y_top": 303, "y_bottom": 486, "y_max": 8},
    "B": {"target": "Escherichia coli Clinical Isolate 1", "x": [582.5, 625.5, 668, 711, 754, 796.5, 810.5, 864], "y_top": 301, "y_bottom": 489, "y_max": 10},
    "C": {"target": "Escherichia coli Clinical Isolate 2", "x": [234, 277, 319.5, 362.5, 405, 447.5, 462, 515.5], "y_top": 590, "y_bottom": 779, "y_max": 12},
    "D": {"target": "Pseudomonas aeruginosa ATCC 9027", "x": [608, 648, 688.5, 729.5, 770, 810.5, 824.5, 881.5], "y_top": 584, "y_bottom": 776, "y_max": 8},
    "E": {"target": "Klebsiella pneumoniae ATCC 700603", "x": [993.5, 1033.5, 1074, 1114, 1154, 1194.5, 1208.5, 1271.5], "y_top": 568, "y_bottom": 760, "y_max": 8},
    "F": {"target": "Staphylococcus aureus ATCC 6538", "x": [238, 277.5, 317, 358, 398, 438, 453, 499], "y_top": 906, "y_bottom": 1094, "y_max": 14},
    "G": {"target": "Staphylococcus aureus Clinical Isolate 1", "x": [612, 654.5, 697, 739, 782, 824.5, 839, 892], "y_top": 913, "y_bottom": 1100, "y_max": 12},
    "H": {"target": "Staphylococcus aureus Clinical Isolate 2", "x": [994.5, 1036.5, 1079, 1121, 1164, 1206, 1220, 1273], "y_top": 899, "y_bottom": 1085, "y_max": 10},
    "I": {"target": "Staphylococcus aureus Clinical Isolate 3", "x": [240, 281.5, 322.5, 362, 403, 443.5, 456.5, 507], "y_top": 1213, "y_bottom": 1391, "y_max": 12},
    "J": {"target": "methicillin-resistant Staphylococcus aureus ATCC 43300", "x": [630, 672.5, 715, 757.5, 800, 843, 857, 910], "y_top": 1209, "y_bottom": 1396, "y_max": 12},
}


def image_sha256() -> str:
    return hashlib.sha256(IMAGE.read_bytes()).hexdigest()


def masks(rgb: np.ndarray) -> dict[str, np.ndarray]:
    red, green, blue = [rgb[:, :, index] for index in range(3)]
    return {
        "red": (red > 170) & (green < 115) & (blue < 115) & (red > green + 70),
        "green": (green > 100) & (red < 130) & (blue < 130) & (green > red + 40),
        "purple": (blue > 150) & (red > 70) & (green < 120) & (blue > green + 70) & (red > green + 40),
    }


def value_from_y(panel: dict[str, object], y: float) -> float:
    top = float(panel["y_top"])
    bottom = float(panel["y_bottom"])
    maximum = float(panel["y_max"])
    value = (bottom - y) / (bottom - top) * maximum
    return round(max(0.0, min(maximum, value)), 2)


def y_from_value(panel: dict[str, object], value: float) -> float:
    top = float(panel["y_top"])
    bottom = float(panel["y_bottom"])
    maximum = float(panel["y_max"])
    return round(bottom - value / maximum * (bottom - top), 1)


def main() -> int:
    image = np.array(Image.open(IMAGE).convert("RGB"))
    color_masks = masks(image)
    observations: list[dict[str, object]] = []
    missing: list[tuple[str, str, int]] = []

    for panel_name, panel in PANELS.items():
        panel_rows: dict[str, list[dict[str, object]]] = {}
        for color, curve in CURVES.items():
            rows: list[dict[str, object]] = []
            for time_h, x in zip(TIMES, panel["x"]):
                x_center = round(float(x))
                y_pixels = np.where(
                    color_masks[color][int(panel["y_top"]): int(panel["y_bottom"]) + 1, x_center - 4: x_center + 5]
                )[0] + int(panel["y_top"])
                if len(y_pixels):
                    y = float(np.median(y_pixels))
                    raw_value = value_from_y(panel, y)
                    status = "color_marker_or_line_median"
                    pixel_count = int(len(y_pixels))
                else:
                    y = float(panel["y_bottom"])
                    raw_value = 0.0
                    status = "temporarily_missing_color_pixels"
                    pixel_count = 0
                    missing.append((panel_name, color, time_h))
                rows.append({
                    "panel": panel_name,
                    "target": panel["target"],
                    "color": color,
                    "dose_fold_mic": curve["dose_fold_mic"],
                    "time_h": time_h,
                    "raw_value": raw_value,
                    "raw_unit": "CFU/mL (1 x 10^5)",
                    "image_coordinate_px": {"x": float(x), "y": round(y, 1)},
                    "pixel_count_in_x_band": pixel_count,
                    "digitization_status": status,
                    "exact_vs_approximate_status": "approximate_color_segmented_from_rendered_figure",
                    "raw_value_uncertainty": round(float(panel["y_max"]) / (float(panel["y_bottom"]) - float(panel["y_top"])) * 6, 2),
                    "coordinate_uncertainty_px": 6,
                    "treatment_control_role": "treatment",
                })
            panel_rows[color] = rows

        # At time zero the three curves overlap and later-drawn markers can hide
        # one color. Use the median visible baseline for a missing t=0 marker.
        visible_t0 = [rows[0]["raw_value"] for rows in panel_rows.values() if rows[0]["pixel_count_in_x_band"]]
        shared_t0 = round(float(np.median(visible_t0)), 2)
        for rows in panel_rows.values():
            if not rows[0]["pixel_count_in_x_band"]:
                rows[0]["raw_value"] = shared_t0
                rows[0]["image_coordinate_px"]["y"] = y_from_value(panel, shared_t0)
                rows[0]["digitization_status"] = "shared_visible_time_zero_baseline_due_to_curve_overlap"

        # Missing green/purple pixels at the later bottom axis are visually
        # coincident with zero; keep the value at zero and state the inference.
        for rows in panel_rows.values():
            for row in rows[1:]:
                if not row["pixel_count_in_x_band"]:
                    row["digitization_status"] = "axis_floor_zero_inferred_from_visible_curve_overlap"

        for color in CURVES:
            observations.extend(panel_rows[color])

    payload = {
        "paper_id": "PMC12019989",
        "figure": "Figure 2",
        "artifact_role": "leader_color_segmentation_scaffold_requires_worker3_source_review",
        "source_image": str(IMAGE.relative_to(HERE.parents[7])),
        "source_image_sha256": image_sha256(),
        "method": {
            "axis_detection": "long black pixel runs plus manual leader visual confirmation",
            "marker_detection": "RGB threshold masks in +/-4 px bands around color-component marker centers",
            "curve_colors": CURVES,
            "value_mapping": "linear y-axis mapping using panel-specific detected top/bottom and printed y maximum",
            "limitations": "rendered-image digitization is approximate; worker-3 must inspect trajectories and preserve uncertainty",
        },
        "panels": PANELS,
        "observation_count": len(observations),
        "missing_color_pixel_cases_before_overlap_resolution": [
            {"panel": panel, "color": color, "time_h": time_h} for panel, color, time_h in missing
        ],
        "observations": observations,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    unique_values = {row["raw_value"] for row in observations}
    print(json.dumps({
        "output": str(OUTPUT),
        "observations": len(observations),
        "curves": len(PANELS) * len(CURVES),
        "unique_values": len(unique_values),
        "source_image_sha256": payload["source_image_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
