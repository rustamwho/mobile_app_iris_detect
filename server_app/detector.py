from typing import List
import cv2

eye_cascade = cv2.CascadeClassifier('./haar/haarcascade_eye.xml')

DEBUG = False


class DetectedPupil:
    def __init__(self, x, y, r):
        self.x = int(x)
        self.y = int(y)
        self.r = int(r)


class DetectedIris:
    def __init__(self, x, y, r):
        self.x = int(x)
        self.y = int(y)
        self.r = int(r)
        self.pupil_list = []  # type: List[DetectedPupil]

    @property
    def left_top(self):
        return self.x - self.r, self.y - self.r


class DetectedEye:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.iris_list = []  # type: List[DetectedIris]
        self.selected_iris = None
        self.selected_pupil = None


def detect_iris(source_img):
    img_height, img_width = source_img.shape[:2]
    if img_height > 600:
        scale_factor = 600 / img_height
        source_img = cv2.resize(source_img, None, fx=scale_factor,
                                fy=scale_factor, interpolation=cv2.INTER_AREA)

    img = cv2.medianBlur(source_img, 9)  # Max: 9

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    eyes_rectangles = eye_cascade.detectMultiScale(gray, minSize=(
    img.shape[1] // 5, img.shape[0] // 5))
    eyes = []
    for (ex, ey, ew, eh) in eyes_rectangles:
        eye = DetectedEye(ex, ey, ew, eh)
        eyes.append(eye)
        crop_img = img[ey: ey + eh, ex: ex + ew]
        iris_gray = cv2.cvtColor(crop_img, cv2.COLOR_RGB2GRAY)
        iris_circles = cv2.HoughCircles(iris_gray, cv2.HOUGH_GRADIENT, 1, 10,
                                        param1=100,
                                        param2=30,
                                        minRadius=int(
                                            max(ew * 0.09, eh * 0.09)),
                                        maxRadius=int(min(ew * 0.3, eh * 0.3)))
        if iris_circles is not None:
            for (ix, iy, ir) in iris_circles[0]:
                if ir <= 0:
                    continue
                iris = DetectedIris(eye.x + ix, eye.y + iy, ir)
                eye.iris_list.append(iris)
                crop_iris = crop_img[int(iy - ir): int(iy + ir),
                            int(ix - ir): int(ix + ir)]
                pupil_gray = cv2.cvtColor(crop_iris, cv2.COLOR_RGB2GRAY)
                pupil_circles = cv2.HoughCircles(pupil_gray, cv2.HOUGH_GRADIENT,
                                                 1, 10,
                                                 param1=50,
                                                 param2=10,
                                                 maxRadius=int(ir * 0.8),
                                                 minRadius=int(ir * 0.07))
                if pupil_circles is not None:
                    for (px, py, pr) in pupil_circles[0]:
                        iris.pupil_list.append(
                            DetectedPupil(iris.left_top[0] + px,
                                          iris.left_top[1] + py, pr))

    i = 0
    for eye in eyes:  # type: DetectedEye
        if i < 2:
            cv2.rectangle(source_img, (eye.x, eye.y),
                          (eye.x + eye.w, eye.y + eye.h), (0, 255, 0), 2)
            i += 1

        if len(eye.iris_list) == 1:
            eye.selected_iris = eye.iris_list[0]
        elif len(eye.iris_list) > 1:
            iris_copy = eye.iris_list.copy()
            iris_mid_r = sum([i.r for i in iris_copy]) / len(
                [i.r for i in iris_copy])
            iris_copy = list(filter(lambda i: i.r >= iris_mid_r, iris_copy))
            eye.selected_iris = DetectedIris(
                sum([i.x for i in iris_copy]) // len(iris_copy),
                sum([i.y for i in iris_copy]) // len(iris_copy),
                sum([i.r for i in iris_copy]) // len(iris_copy)
            )

        def pupils_sort(p: DetectedPupil):
            return ((p.x - eye.selected_iris.x) ** 2 + (
                        p.y - eye.selected_iris.y) ** 2) ** 0.5

        pupils = sorted([p for i in eye.iris_list for p in i.pupil_list],
                        key=pupils_sort)
        if pupils:
            pupil_mid_r = sum([p.r for p in pupils[:1]]) / len(pupils[:1])
            eye.selected_pupil = pupils[0]
            eye.selected_pupil.r = int(pupil_mid_r)

        if eye.selected_iris:
            cv2.circle(source_img, (eye.selected_iris.x, eye.selected_iris.y),
                       eye.selected_iris.r,
                       (255, 0, 0), thickness=2)
        if eye.selected_pupil:
            cv2.circle(source_img, (eye.selected_pupil.x, eye.selected_pupil.y),
                       eye.selected_pupil.r,
                       (0, 0, 255), thickness=2)

        if DEBUG:
            for iris in eye.iris_list:  # type: DetectedIris
                cv2.circle(source_img, (iris.x, iris.y), iris.r, (255, 0, 0),
                           thickness=2)
                for pupil in iris.pupil_list:  # type: DetectedPupil
                    cv2.circle(source_img, (pupil.x, pupil.y), pupil.r,
                               (0, 0, 255), thickness=2)

    result_iris = []
    result_pupil = []

    for eye in eyes:
        if eye.selected_iris:
            result_iris.append(eye.selected_iris.r)

        if eye.selected_pupil:
            result_pupil.append(eye.selected_pupil.r)

    if result_iris:
        result_iris = sum(result_iris) / len(result_iris)
    else:
        result_iris = None

    if result_pupil:
        result_pupil = sum(result_pupil) / len(result_pupil)
    else:
        result_pupil = None

    if result_pupil and result_iris:
        return source_img, result_pupil / result_iris * 12
    else:
        return source_img, None
