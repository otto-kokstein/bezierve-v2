import tkinter as tk
from tkinter import colorchooser
from typing import Callable
from bezier_curve import BezierCurve


class ColorChanger:
    def __init__(
        self,
        parent_frame: tk.Frame,
        default_color: str,
        title: str,
        get_selected_curve_func: Callable[[], BezierCurve | None],
        change_color_func: Callable[[str], None]
    ) -> None:
        self.default_color = default_color
        self.title = title
        self.get_selected_curve_func = get_selected_curve_func
        self.change_color_func = change_color_func

        self.button = tk.Button(
            parent_frame,
            command=self.change_color,
            width=5,
        )

        self.indicator = tk.Canvas(
            parent_frame, width=32, height=15, bg=default_color
        )

        self.indicator.place(
            in_=self.button, relx=0.5, rely=0.5, anchor=tk.CENTER
        )

        self.indicator.bind("<Button-1>", lambda event: self.button.invoke())

        self.label = tk.Label(parent_frame, text=title)

    def change_color(self) -> None:
        selected_curve = self.get_selected_curve_func()

        if selected_curve is not None:
            new_color = self.prompt_color_change(
                initial_color=self.default_color
            )

            if new_color is not None:
                self.change_color_func(new_color)

                self.indicator.config(bg=new_color)

    def prompt_color_change(self, initial_color: str) -> str | None:
        if self.get_selected_curve_func() is not None:
            new_color = colorchooser.askcolor(
                title=self.title, initialcolor=initial_color
            )

            new_color_code = new_color[1]

            return new_color_code
