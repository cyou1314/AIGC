"""Shared layout data and coordinate helpers for storyboard analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
from PIL import Image

try:
    import cv2
except ImportError:
    cv2 = None

Rect = Tuple[int, int, int, int]


@dataclass(frozen=True)
class LayoutResult:
    """Immutable result of storyboard layout analysis."""

    panels: Tuple[Rect, ...]
    confidence: float
    reasons: Tuple[str, ...]
    analysis_size: Tuple[int, int]


def make_analysis_image(
    image: Image.Image, max_side: int = 1200
) -> Tuple[Image.Image, float, float]:
    """Return an RGB analysis image and analysis-to-source scale factors."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    longest_side = max(width, height)
    effective_max_side = min(max_side, 1200)

    if longest_side <= effective_max_side:
        return rgb, 1.0, 1.0

    ratio = effective_max_side / longest_side
    analysis_size = (
        max(1, round(width * ratio)),
        max(1, round(height * ratio)),
    )
    analysis = rgb.resize(analysis_size, Image.Resampling.BILINEAR)
    return analysis, width / analysis.width, height / analysis.height


def scale_rect(
    rect: Rect, scale_x: float, scale_y: float, bounds: Tuple[int, int]
) -> Rect:
    """Scale an analysis-space rectangle and clamp it to source bounds."""
    width, height = bounds
    x1, y1, x2, y2 = rect
    return (
        max(0, min(width, round(x1 * scale_x))),
        max(0, min(height, round(y1 * scale_y))),
        max(0, min(width, round(x2 * scale_x))),
        max(0, min(height, round(y2 * scale_y))),
    )


def _runs(mask: np.ndarray, minimum: int = 1) -> list[Tuple[int, int]]:
    """Return half-open runs from a one-dimensional boolean mask."""
    padded = np.concatenate(([False], mask.astype(bool), [False]))
    changes = np.flatnonzero(padded[1:] != padded[:-1])
    return [
        (int(start), int(end))
        for start, end in zip(changes[::2], changes[1::2])
        if end - start >= minimum
    ]


def _frame_pairs(
    projection: np.ndarray, minimum_span: int, threshold: float
) -> list[Tuple[int, int]]:
    """Pair strong frame-bar runs into the rectangular span they enclose."""
    bars = _runs(projection >= threshold)
    pairs = []
    for first, second in zip(bars, bars[1:]):
        start, _ = first
        _, end = second
        if end - start >= minimum_span:
            pairs.append((start, end))
    return pairs


def _rect_iou(first: Rect, second: Rect) -> float:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    intersection = max(0, right - left) * max(0, bottom - top)
    union = (first[2] - first[0]) * (first[3] - first[1])
    union += (second[2] - second[0]) * (second[3] - second[1])
    union -= intersection
    return intersection / union if union else 0.0


def _intersection_area(first: Rect, second: Rect) -> int:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    return max(0, right - left) * max(0, bottom - top)


def _overlap_smaller(first: Rect, second: Rect) -> float:
    first_area = (first[2] - first[0]) * (first[3] - first[1])
    second_area = (second[2] - second[0]) * (second[3] - second[1])
    smaller = min(first_area, second_area)
    return _intersection_area(first, second) / smaller if smaller else 0.0


def _normalize_candidates(
    candidates: Iterable[Rect], width: int, height: int
) -> Tuple[Rect, ...]:
    """Clamp, reject tiny/overlapping candidates, then preserve reading order."""
    minimum_width = max(12, round(width * 0.07))
    minimum_height = max(12, round(height * 0.035))
    normalized = []
    for x1, y1, x2, y2 in candidates:
        rect = (
            max(0, min(width, x1)),
            max(0, min(height, y1)),
            max(0, min(width, x2)),
            max(0, min(height, y2)),
        )
        if rect[2] - rect[0] >= minimum_width and rect[3] - rect[1] >= minimum_height:
            normalized.append(rect)

    accepted = []
    for candidate in sorted(
        normalized,
        key=lambda rect: (-(rect[2] - rect[0]) * (rect[3] - rect[1]), rect),
    ):
        if all(
            _rect_iou(candidate, existing) < 0.45
            and _overlap_smaller(candidate, existing) < 0.60
            for existing in accepted
        ):
            accepted.append(candidate)
    return sort_panels(tuple(accepted))


def sort_panels(panels: Tuple[Rect, ...]) -> Tuple[Rect, ...]:
    """Sort panels top-to-bottom then left-to-right using adaptive row bands."""
    if not panels:
        return ()
    median_height = float(np.median([y2 - y1 for _, y1, _, y2 in panels]))
    tolerance = max(2.0, median_height * 0.35)
    ordered = sorted(panels, key=lambda rect: ((rect[1] + rect[3]) / 2, rect[0]))
    rows: list[list[Rect]] = []
    row_centers: list[float] = []
    for panel in ordered:
        center = (panel[1] + panel[3]) / 2
        if rows and abs(center - row_centers[-1]) <= tolerance:
            rows[-1].append(panel)
            row_centers[-1] = float(
                np.mean([(item[1] + item[3]) / 2 for item in rows[-1]])
            )
        else:
            rows.append([panel])
            row_centers.append(center)
    return tuple(panel for row in rows for panel in sorted(row, key=lambda rect: rect[0]))


def _row_candidates(ink: np.ndarray, dark: np.ndarray) -> list[Tuple[int, int]]:
    """Find panel-row spans from strong horizontal bars and content activity."""
    height = ink.shape[0]
    dark_projection = dark.mean(axis=1)
    ink_projection = ink.mean(axis=1)
    bar_threshold = max(0.16, float(np.percentile(dark_projection, 88)))
    rows = _frame_pairs(dark_projection, max(12, round(height * 0.06)), bar_threshold)

    activity_threshold = max(0.008, float(np.percentile(ink_projection, 38)))
    activity_runs = _runs(ink_projection >= activity_threshold, max(3, round(height * 0.015)))
    for start, end in activity_runs:
        if end - start >= max(12, round(height * 0.05)):
            rows.append((start, end))

    retained = []
    for row in rows:
        if all(
            (min(row[1], existing[1]) - max(row[0], existing[0]))
            / (max(row[1], existing[1]) - min(row[0], existing[0]))
            < 0.9
            for existing in retained
        ):
            retained.append(row)
    return retained


def _column_candidates(
    dark: np.ndarray, row: Tuple[int, int]
) -> list[Tuple[int, int]]:
    """Find columns bounded by dark bars connected to both row edges."""
    y1, y2 = row
    height = y2 - y1
    trim = max(1, round(height * 0.12))
    middle = dark[y1 + trim : max(y1 + trim + 1, y2 - trim)]
    projection = middle.mean(axis=0)
    threshold = max(0.03, float(np.percentile(projection, 90)) * 0.45)
    bars = _runs(projection >= threshold)
    probe_offset = max(2, round(height * 0.035))
    probe_width = max(2, round(height * 0.025))
    connected = []
    for start, end in bars:
        top = dark[
            min(y2, y1 + probe_offset) : min(
                y2, y1 + probe_offset + probe_width
            ),
            start:end,
        ]
        bottom = dark[
            max(y1, y2 - probe_offset - probe_width) : max(
                y1, y2 - probe_offset
            ),
            start:end,
        ]
        if top.size and bottom.size and top.mean() >= 0.12 and bottom.mean() >= 0.12:
            connected.append((start, end))

    minimum_span = max(12, round(dark.shape[1] * 0.07))
    pairs = []
    for first, second in zip(connected, connected[1:]):
        start, _ = first
        _, end = second
        if end - start >= minimum_span:
            pairs.append((start, end))
    return pairs


def _edge_runs(
    projection: np.ndarray, minimum_span: int, threshold: float
) -> list[Tuple[int, int]]:
    """Pair long gradient boundaries using their outer transition positions."""
    boundaries = _runs(projection >= threshold)
    pairs = []
    for first, second in zip(boundaries, boundaries[1:]):
        start = first[0]
        end = second[0]
        if end - start >= minimum_span:
            pairs.append((start, end))
    return pairs


def _strip_is_gutter(
    edge_mask: np.ndarray, rect: Rect, side: str, thickness: int
) -> bool:
    """Return whether the strip outside one rectangle side is low-texture."""
    height, width = edge_mask.shape
    x1, y1, x2, y2 = rect
    if side == "left":
        strip = edge_mask[y1:y2, max(0, x1 - thickness) : x1]
    elif side == "right":
        strip = edge_mask[y1:y2, x2 : min(width, x2 + thickness)]
    elif side == "top":
        strip = edge_mask[max(0, y1 - thickness) : y1, x1:x2]
    else:
        strip = edge_mask[y2 : min(height, y2 + thickness), x1:x2]
    return not strip.size or float(strip.mean()) <= 0.12


def _edge_background_candidates(gray: np.ndarray) -> Tuple[Rect, ...]:
    """Find rectangles bounded by gradients and separated by quiet gutters."""
    height, width = gray.shape
    values = gray.astype(np.int16, copy=False)
    x_difference = np.abs(np.diff(values, axis=1, prepend=values[:, :1]))
    y_difference = np.abs(np.diff(values, axis=0, prepend=values[:1, :]))
    nonzero = np.concatenate(
        (x_difference[x_difference > 0], y_difference[y_difference > 0])
    )
    edge_threshold = max(
        10.0, float(np.percentile(nonzero, 35)) if nonzero.size else 10.0
    )
    vertical_edges = x_difference >= edge_threshold
    horizontal_edges = y_difference >= edge_threshold
    edge_mask = vertical_edges | horizontal_edges

    row_projection = horizontal_edges.mean(axis=1)
    row_threshold = max(0.08, float(np.percentile(row_projection, 90)) * 0.55)
    row_pairs = _edge_runs(
        row_projection, max(12, round(height * 0.05)), row_threshold
    )

    candidates = []
    for y1, y2 in row_pairs:
        vertical_projection = vertical_edges[y1:y2].mean(axis=0)
        row_height = y2 - y1
        probe_offset = max(1, round(row_height * 0.01))
        probe_width = max(2, round(row_height * 0.02))
        top_probe = vertical_edges[
            min(y2, y1 + probe_offset) : min(
                y2, y1 + probe_offset + probe_width
            )
        ].mean(axis=0)
        bottom_probe = vertical_edges[
            max(y1, y2 - probe_offset - probe_width) : max(
                y1, y2 - probe_offset
            )
        ].mean(axis=0)
        connected_projection = np.where(
            (top_probe >= 0.12) & (bottom_probe >= 0.12),
            vertical_projection,
            0.0,
        )
        column_threshold = max(
            0.06, float(np.percentile(connected_projection, 90)) * 0.50
        )
        column_pairs = _edge_runs(
            connected_projection,
            max(12, round(width * 0.07)),
            column_threshold,
        )
        for x1, x2 in column_pairs:
            rect = (x1, y1, x2, y2)
            thickness = max(2, round(min(x2 - x1, y2 - y1) * 0.025))
            gutter_sides = sum(
                _strip_is_gutter(edge_mask, rect, side, thickness)
                for side in ("left", "right", "top", "bottom")
            )
            if gutter_sides >= 2:
                candidates.append(rect)
    return _normalize_candidates(candidates, width, height)


def _contour_candidates(gray: np.ndarray) -> Tuple[Rect, ...]:
    """Find closed panel-scale boundaries with the optional OpenCV detector."""
    if cv2 is None:
        return ()

    height, width = gray.shape
    edges = cv2.Canny(gray.astype(np.uint8), 30, 90)
    edges = cv2.morphologyEx(
        edges, cv2.MORPH_CLOSE, np.ones((3, 3), dtype=np.uint8)
    )
    contours, _ = cv2.findContours(
        edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    minimum_width = max(12, round(width * 0.07))
    minimum_height = max(12, round(height * 0.08))
    image_area = width * height
    candidates = []
    for contour in contours:
        x, y, candidate_width, candidate_height = cv2.boundingRect(contour)
        box_area = candidate_width * candidate_height
        contour_fill = abs(cv2.contourArea(contour)) / max(1, box_area)
        area_fraction = box_area / image_area
        if (
            candidate_width >= minimum_width
            and candidate_height >= minimum_height
            and 0.025 <= area_fraction <= 0.50
            and contour_fill >= 0.55
        ):
            candidates.append(
                (x + 1, y + 1, x + candidate_width, y + candidate_height)
            )
    return _normalize_candidates(candidates, width, height)


def _layout_metrics(
    panels: Tuple[Rect, ...], analysis_size: Tuple[int, int]
) -> Tuple[float, float, float, float]:
    """Return coverage, non-overlap, row alignment, and repeated-height scores."""
    if not panels:
        return 0.0, 0.0, 0.0, 0.0
    width, height = analysis_size
    areas = np.asarray(
        [(x2 - x1) * (y2 - y1) for x1, y1, x2, y2 in panels], dtype=float
    )
    coverage = min(1.0, float(areas.sum()) / (width * height * 0.55))
    overlap = sum(
        _intersection_area(first, second)
        for index, first in enumerate(panels)
        for second in panels[index + 1 :]
    )
    non_overlap = max(0.0, 1.0 - 2.0 * overlap / max(1.0, float(areas.sum())))
    heights = np.asarray([y2 - y1 for _, y1, _, y2 in panels], dtype=float)
    median_height = max(1.0, float(np.median(heights)))
    repeated_heights = float(
        np.clip(1.0 - float(np.std(heights)) / median_height, 0.0, 1.0)
    )

    tolerance = max(2.0, median_height * 0.35)
    row_centers: list[list[float]] = []
    for _, y1, _, y2 in sort_panels(panels):
        center = (y1 + y2) / 2
        if row_centers and abs(center - float(np.mean(row_centers[-1]))) <= tolerance:
            row_centers[-1].append(center)
        else:
            row_centers.append([center])
    residual = float(np.mean([np.std(row) for row in row_centers]))
    alignment = float(np.clip(1.0 - residual / (median_height * 0.18), 0.0, 1.0))
    return coverage, non_overlap, alignment, repeated_heights


def _layout_quality(panels: Tuple[Rect, ...], analysis_size: Tuple[int, int]) -> float:
    coverage, non_overlap, alignment, repeated_heights = _layout_metrics(
        panels, analysis_size
    )
    return (
        0.35 * coverage
        + 0.30 * non_overlap
        + 0.10 * alignment
        + 0.25 * repeated_heights
    )


def _signal_agreement(
    panels: Tuple[Rect, ...], independent: Tuple[Rect, ...]
) -> float:
    """Score bidirectional matches while penalizing candidate-count divergence."""
    if not panels or not independent:
        return 0.0
    selected_match_rate = float(
        np.mean(
            [
                any(_rect_iou(panel, other) >= 0.40 for other in independent)
                for panel in panels
            ]
        )
    )
    independent_match_rate = float(
        np.mean(
            [
                any(_rect_iou(other, panel) >= 0.40 for panel in panels)
                for other in independent
            ]
        )
    )
    count_balance = min(len(panels), len(independent)) / max(
        len(panels), len(independent)
    )
    return min(selected_match_rate, independent_match_rate) * count_balance


def _confidence(
    panels: Tuple[Rect, ...],
    analysis_size: Tuple[int, int],
    independent: Tuple[Rect, ...],
) -> float:
    """Score coverage, alignment, repetition, overlap, and signal agreement."""
    if not panels:
        return 0.0
    coverage, non_overlap, alignment, repeated_heights = _layout_metrics(
        panels, analysis_size
    )
    agreement = _signal_agreement(panels, independent)
    geometry = (
        0.30 * coverage
        + 0.25 * non_overlap
        + 0.20 * alignment
        + 0.25 * repeated_heights
    )
    return float(
        np.clip(
            0.62 * geometry + 0.38 * agreement,
            0.0,
            1.0,
        )
    )


def _opencv_confidence(
    panels: Tuple[Rect, ...],
    analysis_size: Tuple[int, int],
    independent: Tuple[Rect, ...],
) -> float:
    """Score a closed-boundary primary result plus independent corroboration."""
    if not panels:
        return 0.0
    coverage, non_overlap, alignment, repeated_heights = _layout_metrics(
        panels, analysis_size
    )
    agreement = _signal_agreement(panels, independent)
    return float(
        np.clip(
            0.25 * coverage
            + 0.20 * non_overlap
            + 0.20 * alignment
            + 0.20 * repeated_heights
            + 0.15 * agreement,
            0.0,
            1.0,
        )
    )


def detect_layout(image: Image.Image, max_side: int = 1200) -> LayoutResult:
    """Detect framed storyboard panels and return source-resolution rectangles."""
    analysis, scale_x, scale_y = make_analysis_image(image, max_side=max_side)
    pixels = np.asarray(analysis, dtype=np.int16)
    gray = (pixels[..., 0] * 30 + pixels[..., 1] * 59 + pixels[..., 2] * 11) // 100
    dark = gray < 72
    x_difference = np.abs(np.diff(gray, axis=1, prepend=gray[:, :1]))
    y_difference = np.abs(np.diff(gray, axis=0, prepend=gray[:1, :]))
    ink = dark | ((x_difference + y_difference) > 58)
    height, width = gray.shape

    frame_candidates = []
    for row in _row_candidates(ink, dark):
        for x1, x2 in _column_candidates(dark, row):
            frame_candidates.append((x1, row[0], x2, row[1]))

    frame_panels = _normalize_candidates(frame_candidates, width, height)
    edge_background_panels = _edge_background_candidates(gray)
    if cv2 is not None:
        contour_panels = _contour_candidates(gray)
        frame_quality = _layout_quality(frame_panels, (width, height))
        contour_quality = _layout_quality(contour_panels, (width, height))
        if frame_quality > contour_quality + 0.03:
            panels = frame_panels
            independent = contour_panels
            selected_signal = "dark frame bars"
            detector_reason = "detector: dark frame bars with OpenCV contour check"
        else:
            panels = contour_panels
            independent = frame_panels
            selected_signal = "closed contours"
            detector_reason = (
                "detector: OpenCV closed contours with dark-frame corroboration"
            )
        signal_reasons = (
            f"closed contours retained {len(contour_panels)} panel candidates",
            f"dark frame bars retained {len(frame_panels)} candidates",
        )
    else:
        frame_quality = _layout_quality(frame_panels, (width, height))
        edge_background_quality = _layout_quality(
            edge_background_panels, (width, height)
        )
        if frame_panels and frame_quality >= edge_background_quality - 0.03:
            panels = frame_panels
            independent = edge_background_panels
            selected_signal = "dark frame bars"
        else:
            panels = edge_background_panels
            independent = frame_panels
            selected_signal = "edge-background gutters"
        detector_reason = "detector: Pillow/NumPy fallback"
        signal_reasons = (
            f"edge-background gutters retained {len(edge_background_panels)} candidates",
            f"dark frame bars retained {len(frame_panels)} candidates",
        )
    scaled_panels = tuple(
        scale_rect(panel, scale_x, scale_y, image.size) for panel in panels
    )
    if selected_signal == "closed contours":
        confidence = _opencv_confidence(panels, (width, height), independent)
        confidence_reason = "closed-boundary geometry and corroboration"
    else:
        confidence = _confidence(panels, (width, height), independent)
        confidence_reason = (
            "conservative geometry and symmetric independent-signal agreement"
        )
    reasons = (
        detector_reason,
        *signal_reasons,
        f"{selected_signal} won layout regularity scoring",
        f"{confidence_reason} confidence {confidence:.2f}",
    )
    return LayoutResult(scaled_panels, confidence, reasons, analysis.size)
