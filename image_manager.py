from ROOT_PATH import root_path
from pathlib import Path
from os import remove, listdir, path as os_path
from tkinter import Canvas, Listbox, Entry, Label, END, NW, filedialog
from typing import Tuple, List, Callable
from PIL import Image, ImageTk
from bezier_curve import BezierCurve
from canvas_point import P


class ImageManager:
    def __init__(self, canvas: Canvas, canvas_size: Tuple[int, int]):
        self.canvas = canvas
        self.canvas_size = canvas_size

        self.image_filename: str | None = None
        self.image: ImageTk.PhotoImage | None = None
        self.canvas_image: int | None = None

    def remove_image(
        self,
    ) -> None:
        if self.image_filename is not None:
            self.image_filename = None
        if self.image is not None:
            self.image = None
        if self.canvas_image is not None:
            self.canvas.delete(self.canvas_image)

    def display_new_image(
        self,
        filename: str,
    ) -> None:
        # Delete the old image
        self.remove_image()

        # Load new image
        self.image_filename = filename

        raw_image = Image.open(self.image_filename)

        # Rescale the image so that it fits on the canvas
        new_image_size: Tuple[int, int] = (0, 0)

        if raw_image.width == raw_image.height:
            smaller_canvas_side = min(self.canvas_size)

            new_image_size = (smaller_canvas_side, smaller_canvas_side)

        elif raw_image.width > raw_image.height:
            new_image_size = (
                self.canvas_size[0],
                round(raw_image.height * (self.canvas_size[0] / raw_image.width)),
            )

        else:
            new_image_size = (
                round(raw_image.width * (self.canvas_size[1] / raw_image.height)),
                self.canvas_size[1],
            )

        raw_image = raw_image.resize(new_image_size)

        # Calculate position where image's NW corner will be placed on canvas
        image_pos_on_canvas: Tuple[int, int] = (
            round((self.canvas_size[0] - raw_image.width) / 2),
            round((self.canvas_size[1] - raw_image.height) / 2),
        )

        # Convert the image so that Tkinter can work with it
        self.image = ImageTk.PhotoImage(raw_image)

        # Apply the image
        self.canvas_image = self.canvas.create_image(
            image_pos_on_canvas,
            anchor=NW,
            image=self.image,
        )

        self.canvas.tag_lower(self.canvas_image)

    def import_image(self) -> None:
        filetypes = (("Accepted image files", ["*.png", "*.jpg"]),)

        filename = filedialog.askopenfilename(
            title="Import Image", initialdir=root_path, filetypes=filetypes
        )

        try:
            Image.open(
                filename
            )  # Try to see if it fails (I don't know what it returns when user chooses nothing)
        except AttributeError:
            pass
        else:
            self.display_new_image(filename)

    def get_active_image_filename(self) -> str | None:
        return self.image_filename
