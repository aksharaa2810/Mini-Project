import time
from dataclasses import dataclass

import cv2
from mtcnn import MTCNN


@dataclass(frozen=True)
class HybridDetectionConfig:
    min_confidence: float = 0.90
    min_box_size: int = 40  # ignore very small Haar boxes
    haar_scale_factor: float = 1.1
    haar_min_neighbors: int = 5
    haar_pad_ratio: float = 0.15  # expand Haar ROI before MTCNN
    draw_landmarks: bool = True


def _clip_xywh(box, img_w, img_h):
    x, y, w, h = box
    x = max(0, int(x))
    y = max(0, int(y))
    w = max(0, int(w))
    h = max(0, int(h))
    if x >= img_w or y >= img_h:
        return 0, 0, 0, 0
    w = min(w, img_w - x)
    h = min(h, img_h - y)
    return x, y, w, h


def _expand_xywh(x, y, w, h, img_w, img_h, pad_ratio):
    pad_x = int(w * pad_ratio)
    pad_y = int(h * pad_ratio)
    x2 = max(0, x - pad_x)
    y2 = max(0, y - pad_y)
    w2 = min(img_w - x2, w + 2 * pad_x)
    h2 = min(img_h - y2, h + 2 * pad_y)
    return x2, y2, w2, h2


def _draw_landmarks(image_bgr, keypoints, offset_x=0, offset_y=0):
    for _, point in keypoints.items():
        px, py = int(point[0] + offset_x), int(point[1] + offset_y)
        cv2.circle(image_bgr, (px, py), 2, (0, 0, 255), 2)


def hybrid_face_detection(
    image,
    *,
    haar=None,
    mtcnn=None,
    config: HybridDetectionConfig | None = None,
):
    """
    Hybrid face detection:
    - Haar Cascade on grayscale for fast region proposals
    - MTCNN verification + refinement on each cropped ROI (no full-image MTCNN)

    Args:
        image (np.ndarray): BGR image (OpenCV).
        haar: Optional pre-created cv2.CascadeClassifier for reuse.
        mtcnn: Optional pre-created MTCNN detector for reuse.
        config: Optional HybridDetectionConfig.

    Returns:
        annotated_image (np.ndarray): Image copy with drawn boxes (and landmarks optionally).
        faces (list[dict]): Each dict contains:
            - box: [x, y, w, h] in original image coords
            - confidence: float
            - keypoints: dict (optional)
    """
    if config is None:
        config = HybridDetectionConfig()

    if image is None:
        return None, []

    if haar is None:
        haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if haar.empty():
        raise RuntimeError("Failed to load Haar Cascade classifier.")

    if mtcnn is None:
        mtcnn = MTCNN()

    img_h, img_w = image.shape[:2]
    annotated = image.copy()

    # 1) Haar on grayscale only (performance)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    haar_rects = haar.detectMultiScale(
        gray,
        scaleFactor=config.haar_scale_factor,
        minNeighbors=config.haar_min_neighbors,
        minSize=(config.min_box_size, config.min_box_size),
    )

    final_faces = []

    # 2) For each Haar ROI, run MTCNN on crop (accuracy)
    for (x, y, w, h) in haar_rects:
        x, y, w, h = _clip_xywh((x, y, w, h), img_w, img_h)
        if w < config.min_box_size or h < config.min_box_size:
            continue

        x2, y2, w2, h2 = _expand_xywh(x, y, w, h, img_w, img_h, config.haar_pad_ratio)
        roi_bgr = image[y2 : y2 + h2, x2 : x2 + w2]
        if roi_bgr.size == 0:
            continue

        roi_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
        detections = mtcnn.detect_faces(roi_rgb)
        if not detections:
            continue

        # Keep the best MTCNN detection inside this ROI
        best = max(detections, key=lambda d: d.get("confidence", 0))
        conf = float(best.get("confidence", 0))
        if conf <= config.min_confidence:
            continue

        bx, by, bw, bh = best["box"]  # ROI-local box
        fx, fy, fw, fh = _clip_xywh((x2 + bx, y2 + by, bw, bh), img_w, img_h)
        if fw < config.min_box_size or fh < config.min_box_size:
            continue

        face = {"box": [fx, fy, fw, fh], "confidence": conf}
        if "keypoints" in best and best["keypoints"]:
            face["keypoints"] = best["keypoints"]

        final_faces.append(face)

        # 3) Draw on annotated image
        cv2.rectangle(annotated, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"{conf:.2f}",
            (fx, max(0, fy - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2,
        )
        if config.draw_landmarks and face.get("keypoints"):
            _draw_landmarks(annotated, face["keypoints"], offset_x=x2, offset_y=y2)

    return annotated, final_faces


def webcam_hybrid_demo(camera_index=0):
    """Bonus: webcam demo with FPS overlay."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    haar = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    mtcnn = MTCNN()
    config = HybridDetectionConfig()

    prev_t = time.time()
    fps = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        annotated, faces = hybrid_face_detection(frame, haar=haar, mtcnn=mtcnn, config=config)

        now = time.time()
        dt = now - prev_t
        prev_t = now
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt)

        cv2.putText(
            annotated,
            f"FPS: {fps:.1f}  Faces: {len(faces)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.imshow("Hybrid Face Detection (Haar + MTCNN)", annotated)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    webcam_hybrid_demo(0)

