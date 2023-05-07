from typing import List, Tuple, Dict
from canvas_point import P, CanvasPoint, DEFAULT_POINT_SMALLER_DIAMETER
from tkinter import Canvas
from math import sqrt


EPS = 10 ** (-6)

DEFAULT_CURVE_WIDTH: int = 3

DEFAULT_CURVE_COLOR: str = "#050505"

DEFAULT_ENDPOINT_COLOR = "#ff0000"

DEFAULT_CONTROL_POINT_COLOR = "#0066cc"

DEFAULT_X_EXTREMUM_COLOR = "#00cc00"

DEFAULT_Y_EXTREMUM_COLOR = "#cc00cc"

BEZIER_CURVE_DETAIL: int = 100

InvalidPointAmoundError: ValueError = ValueError("Invalid Amount of Points")

curve_names: Dict[int, str] = {
    2: "Linear",
    3: "Quadratic",
    4: "Cubic",
}


class BezierCurve:
    def __init__(
        self,
        name: str,
        points: List[CanvasPoint],
        canvas_height: int,
        width: int = DEFAULT_CURVE_WIDTH,
        color: str = DEFAULT_CURVE_COLOR,
    ) -> None:
        self.name: str = name
        self.points: List[CanvasPoint] = points
        self.curve = None
        self.equations: Tuple[str, str] = ("", "")
        self.extremum_points: List[CanvasPoint] = []
        self.x_extremum_points_color: str = DEFAULT_X_EXTREMUM_COLOR
        self.y_extremum_points_color: str = DEFAULT_Y_EXTREMUM_COLOR
        self.all_extrema: List[float] = []
        self.x_extrema: List[float] = []
        self.y_extrema: List[float] = []
        self.width: int = width
        self.dashed_line = None
        self.dashed_line_visible: bool = True
        self.extremum_points_visible: bool = True
        self.color: str = color
        self.endpoints_color: str = DEFAULT_ENDPOINT_COLOR
        self.control_points_color: str = DEFAULT_CONTROL_POINT_COLOR
        self.substituted_extremum: int | None = None  # Index of extrema list
        self.substituted_equations: Tuple[str, str] = ("", "")
        self.bounding_box_visible: bool = False
        self.bounding_box_canvas_line: int | None = None

        self.canvas_height = canvas_height

    def raise_curve_widgets(self, canvas: Canvas) -> None:
        if self.curve is not None:
            canvas.tag_raise(self.curve)

            for point in self.extremum_points:
                canvas.tag_raise(point.point)

            for point in self.points:
                canvas.tag_raise(point.point)

    def draw(self, canvas: Canvas) -> None:
        if self.curve is not None:
            canvas.delete(self.curve)
            self.curve = None
        if self.dashed_line is not None:
            canvas.delete(self.dashed_line)
            self.dashed_line = None
        if self.bounding_box_canvas_line is not None:
            canvas.delete(self.bounding_box_canvas_line)
            self.bounding_box_canvas_line = None

        for point in self.extremum_points:
            canvas.delete(point.point)
        self.extremum_points = []

        curve_points: List[Tuple[float, float]] = []

        # For linear Bézier curves
        if len(self.points) == 2:
            # Because linear Bézier curves are just straight lines, we do not have to calculate anything
            curve_points = [point.point_coords for point in self.points]
        # For quadratic & cubic Bézier curves
        else:
            for i in range(BEZIER_CURVE_DETAIL):
                t = i / (BEZIER_CURVE_DETAIL - 1)

                point_x, point_y = self.calculate_curve_point(t)

                curve_points.append((point_x, point_y))

        self.curve = canvas.create_line(
            *curve_points, width=self.width, fill=self.color
        )

        if self.dashed_line_visible:
            self.dashed_line = canvas.create_line(
                [point.point_coords for point in self.points],
                dash=(5, 1),
                fill=self.color,
            )

        self.create_parametric_equations()

        if self.extremum_points_visible:
            for x_extremum in self.x_extrema:
                self.create_extremum_point(
                    canvas, x_extremum, self.x_extremum_points_color
                )
            for y_extremum in self.y_extrema:
                self.create_extremum_point(
                    canvas, y_extremum, self.y_extremum_points_color
                )

        if self.bounding_box_visible:
            self.draw_bounding_box(canvas)

        self.raise_curve_widgets(canvas)

    def create_extremum_point(self, canvas, extremum: float, color: str):
        extremum_coords = self.calculate_curve_point(extremum)

        point = CanvasPoint(
            extremum_coords,
            canvas,
            color,
            point_diameter=DEFAULT_POINT_SMALLER_DIAMETER,
        )

        self.extremum_points.append(point)

    def calculate_curve_point(self, t: float) -> P:
        point_x = 0.0
        point_y = 0.0

        if len(self.points) == 2:
            point_x = (1 - t) * self.points[0].point_coords[0] + t * self.points[
                1
            ].point_coords[0]
            point_y = (1 - t) * self.points[0].point_coords[1] + t * self.points[
                1
            ].point_coords[1]

        elif len(self.points) == 3:
            point_x = (1 - t) * (
                (1 - t) * self.points[0].point_coords[0]
                + t * self.points[1].point_coords[0]
            ) + t * (
                (1 - t) * self.points[1].point_coords[0]
                + t * self.points[2].point_coords[0]
            )

            point_y = (1 - t) * (
                (1 - t) * self.points[0].point_coords[1]
                + t * self.points[1].point_coords[1]
            ) + t * (
                (1 - t) * self.points[1].point_coords[1]
                + t * self.points[2].point_coords[1]
            )

        elif len(self.points) == 4:
            point_x = (
                (1 - t) ** 3 * self.points[0].point_coords[0]
                + 3 * (1 - t) ** 2 * t * self.points[1].point_coords[0]
                + 3 * (1 - t) * t**2 * self.points[2].point_coords[0]
                + t**3 * self.points[3].point_coords[0]
            )

            point_y = (
                (1 - t) ** 3 * self.points[0].point_coords[1]
                + 3 * (1 - t) ** 2 * t * self.points[1].point_coords[1]
                + 3 * (1 - t) * t**2 * self.points[2].point_coords[1]
                + t**3 * self.points[3].point_coords[1]
            )

        else:
            raise InvalidPointAmoundError

        return (round(point_x), round(point_y))

    def create_parametric_equations(self) -> None:
        # Calculate new y coords because of the tkinter / math positive y axis inversion
        new_points_coords: List[P] = []

        for point in self.points:
            new_points_coords.append(
                (point.point_coords[0], self.canvas_height - point.point_coords[1])
            )

        self.all_extrema = []
        self.x_extrema = []
        self.y_extrema = []

        if len(self.points) == 2:
            X = [
                new_points_coords[1][0] - new_points_coords[0][0],
                new_points_coords[0][0],
            ]

            for i in X:
                i = round(i, 4)

            Y = [
                new_points_coords[1][1] - new_points_coords[0][1],
                new_points_coords[0][1],
            ]

            for i in Y:
                i = round(i, 4)

            self.equations = (f"x = {X[0]}*t + {X[1]}", f"y = {Y[0]}*t + {Y[1]}")

            # # Find extrema
            self.x_extrema = [X[0]]
            self.y_extrema = [Y[0]]

        elif len(self.points) == 3:
            X = [
                new_points_coords[0][0]
                - 2 * new_points_coords[1][0]
                + new_points_coords[2][0],
                -2 * new_points_coords[0][0] + 2 * new_points_coords[1][0],
                new_points_coords[0][0],
            ]

            for i in X:
                i = round(i, 4)

            Y = [
                new_points_coords[0][1]
                - 2 * new_points_coords[1][1]
                + new_points_coords[2][1],
                -2 * new_points_coords[0][1] + 2 * new_points_coords[1][1],
                new_points_coords[0][1],
            ]

            for i in Y:
                i = round(i, 4)

            self.equations = (
                f"x = {X[0]}*t^2 + {X[1]}*t + {X[2]}",
                f"y = {Y[0]}*t^2 + {Y[1]}*t + {Y[2]}",
            )

            # Find extrema
            extrema = self.find_extrema_quadratic(X, Y)

            self.x_extrema.append(extrema[0])
            self.y_extrema.append(extrema[1])

        elif len(self.points) == 4:
            X = [
                -new_points_coords[0][0]
                + 3 * new_points_coords[1][0]
                - 3 * new_points_coords[2][0]
                + new_points_coords[3][0],
                3 * new_points_coords[0][0]
                - 6 * new_points_coords[1][0]
                + 3 * new_points_coords[2][0],
                -3 * new_points_coords[0][0] + 3 * new_points_coords[1][0],
                new_points_coords[0][0],
            ]

            for i in X:
                i = round(i, 4)

            Y = [
                -new_points_coords[0][1]
                + 3 * new_points_coords[1][1]
                - 3 * new_points_coords[2][1]
                + new_points_coords[3][1],
                3 * new_points_coords[0][1]
                - 6 * new_points_coords[1][1]
                + 3 * new_points_coords[2][1],
                -3 * new_points_coords[0][1] + 3 * new_points_coords[1][1],
                new_points_coords[0][1],
            ]

            for i in Y:
                i = round(i, 4)

            self.equations = (
                f"x = {X[0]}*t^3 + {X[1]}*t^2 + {X[2]}*t + {X[3]}",
                f"y = {Y[0]}*t^3 + {Y[1]}*t^2 + {Y[2]}*t + {Y[3]}",
            )

            # Find extrema
            # In X axis
            a = 3 * X[0]
            b = 2 * X[1]
            c = X[2]

            D = b**2 - 4 * a * c

            if not (D > 0 or abs(D) < EPS):
                pass
            elif abs(a) < EPS:
                self.x_extrema.append(
                    self.find_extrema_quadratic([X[1], X[2], X[3]], [Y[1], Y[2], Y[3]])[
                        0
                    ]
                )
            else:
                self.x_extrema.append((-b + sqrt(D)) / (2 * a))
                self.x_extrema.append((-b - sqrt(D)) / (2 * a))

            # Calculate for Y
            a = 3 * Y[0]
            b = 2 * Y[1]
            c = Y[2]

            D = b**2 - 4 * a * c

            if not (D > 0 or abs(D) < EPS):
                pass
            elif abs(a) < EPS:
                self.y_extrema.append(
                    self.find_extrema_quadratic([X[1], X[2], X[3]], [Y[1], Y[2], Y[3]])[
                        1
                    ]
                )
            else:
                self.y_extrema.append((-b + sqrt(D)) / (2 * a))
                self.y_extrema.append((-b - sqrt(D)) / (2 * a))

        else:
            raise InvalidPointAmoundError

        # Delete untrue extrema and round the true ones
        def check_extremum_truthfulness(extremum: float) -> bool:
            if len(self.points) == 2:
                return extremum > 0 and extremum <= 1
            if len(self.points) == 3 or len(self.points) == 4:
                return extremum >= 0 and extremum < 1
            else:
                raise InvalidPointAmoundError

        for i in reversed(range(len(self.x_extrema))):
            extremum = self.x_extrema[i]

            if check_extremum_truthfulness(extremum):
                self.x_extrema[i] = round(extremum, 3)
            else:
                self.x_extrema.pop(i)

        for i in reversed(range(len(self.y_extrema))):
            extremum = self.y_extrema[i]

            if extremum > 0 and extremum < 1:
                self.y_extrema[i] = round(extremum, 3)
            else:
                self.y_extrema.pop(i)

        self.all_extrema = self.x_extrema + self.y_extrema

    def find_extrema_quadratic(self, X: List[int], Y: List[int]) -> List[float]:
        x_extremum = -1

        if X[0] != 0:
            x_extremum = X[1] / (-2 * X[0])

        y_extremum = -1

        if Y[0] != 0:
            y_extremum = Y[1] / (-2 * Y[0])

        return [x_extremum, y_extremum]

    def draw_bounding_box(self, canvas: Canvas) -> None:
        list_of_all_points = [self.points[0], self.points[-1], *self.extremum_points]

        all_points_x = [point.point_coords[0] for point in list_of_all_points]
        all_points_y = [point.point_coords[1] for point in list_of_all_points]

        min_x = min(all_points_x)
        max_x = max(all_points_x)
        min_y = min(all_points_y)
        max_y = max(all_points_y)

        left_top = (min_x, min_y)
        right_top = (max_x, min_y)
        left_bottom = (min_x, max_y)
        right_bottom = (max_x, max_y)

        bbox_corners = [left_top, right_top, right_bottom, left_bottom, left_top]

        self.bounding_box_canvas_line = canvas.create_line(
            bbox_corners, fill=self.color, dash=(4, 4, 1, 4)
        )

    def change_curve_color(self, canvas: Canvas, new_color_code: str) -> None:
        self.color = new_color_code
        self.draw(canvas)

    def change_endpoints_color(self, canvas: Canvas, new_color_code: str) -> None:
        for point in [self.points[0], self.points[-1]]:
            canvas.itemconfig(point.point, fill=new_color_code)
        self.endpoints_color = new_color_code

    def change_control_points_color(self, canvas: Canvas, new_color_code: str) -> None:
        for point in [
            point
            for point in self.points
            if self.points[0] != point and self.points[-1] != point
        ]:
            canvas.itemconfig(point.point, fill=new_color_code)
        self.control_points_color = new_color_code

    def substitute_extremum_for_t(self, canvas: Canvas) -> None:
        if self.substituted_extremum is not None and len(self.all_extrema) > 0:
            self.substituted_equations = (
                self.equations[0].replace(
                    "t", str(self.all_extrema[self.substituted_extremum])
                ),
                self.equations[1].replace(
                    "t", str(self.all_extrema[self.substituted_extremum])
                ),
            )

            for point in self.extremum_points:
                canvas.delete(point.point)

            self.extremum_points[self.substituted_extremum].create_canvas_point()

        elif self.substituted_extremum is None and len(self.all_extrema) > 0:
            for point in self.extremum_points:
                point.reset_canvas_point()
