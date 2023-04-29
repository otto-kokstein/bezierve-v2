from typing import List, Tuple, TypeAlias
from tkinter import Canvas


P: TypeAlias = Tuple[int, int]

DEFAULT_POINT_DIAMETER = 10

DEFAULT_POINT_SMALLER_DIAMETER = 8


class CanvasPoint:
    def __init__(
        self, point_coords: P, canvas: Canvas, color: str, point_diameter: int = DEFAULT_POINT_DIAMETER,
    ) -> None:
        self.point_diameter: int = point_diameter
        self.point_coords: P = point_coords
        self.canvas = canvas
        self.color = color
        self.point = self.create_canvas_point()

    def create_canvas_point(self) -> int:
        point = self.canvas.create_oval(
            self.point_coords[0] - self.point_diameter / 2,
            self.point_coords[1] - self.point_diameter / 2,
            self.point_coords[0] + self.point_diameter / 2,
            self.point_coords[1] + self.point_diameter / 2,
            fill=self.color
        )

        return point
    
    def reset_canvas_point(self) -> None:
        self.canvas.delete(self.point)
        self.point = self.create_canvas_point()
