from ROOT_PATH import root_path
import tkinter as tk
from pathlib import Path
from typing import List, Tuple, Dict
from bezier_curve import (
    BezierCurve,
    DEFAULT_CURVE_COLOR,
    DEFAULT_ENDPOINT_COLOR,
    DEFAULT_CONTROL_POINT_COLOR,
    DEFAULT_X_EXTREMUM_COLOR,
    DEFAULT_Y_EXTREMUM_COLOR,
    curve_names,
    get_points_default_pos,
)
from canvas_point import P, CanvasPoint
import projects_manager
from image_manager import ImageManager
from color_changer import ColorChanger


# Obtain path to icon
absolute_path_to_icon = str(Path(root_path, "./bezierve_icon_2.ico").resolve())


class MainFrame(tk.Frame):
    def __init__(self, parent: tk.Tk | None = None) -> None:
        super().__init__(parent)
        self.parent = parent

        self.curves: List[BezierCurve] = []

        self.canvas_frame = tk.Frame(master=self)
        self.right_panel_frame = tk.Frame(master=self)
        self.bottom_panel_frame = tk.Frame(master=self)
        self.left_panel_frame = tk.Frame(master=self)
        self.curves_management_frame = tk.Frame(master=self.right_panel_frame)
        self.saving_management_frame = tk.Frame(master=self.left_panel_frame)
        self.equations_frame = tk.Frame(master=self.bottom_panel_frame)
        self.curve_appearance_frame = tk.Frame(master=self.right_panel_frame)
        self.curve_equations_options_frame = tk.Frame(master=self.bottom_panel_frame)
        self.curve_show_toggle_options_frame = tk.Frame(master=self.bottom_panel_frame)
        self.image_options_frame = tk.Frame(master=self.left_panel_frame)

        self.side_panel_width = 22

        self.side_panel_listbox_width = self.side_panel_width + 5

        self.widget_padding = 3

        self.canvas = tk.Canvas(
            master=self.canvas_frame,
            highlightthickness=2,
            highlightbackground="#0066cc",
        )

        # Set up curves listbox manager
        self.curves_listbox = tk.Listbox(
            self.curves_management_frame,
            width=self.side_panel_listbox_width,
            height=25,
        )

        # Create button for adding new curves
        self.new_linear_button = tk.Button(
            self.curves_management_frame,
            text="New Linear",  # To highlight a specific character, put \u0332 after it
            command=lambda: self.new_curve(2),
            width=self.side_panel_width,
        )

        self.new_quadratic_button = tk.Button(
            self.curves_management_frame,
            text="New Quadratic",
            command=lambda: self.new_curve(3),
            width=self.side_panel_width,
        )

        self.new_cubic_button = tk.Button(
            self.curves_management_frame,
            text="New Cubic",
            command=lambda: self.new_curve(4),
            width=self.side_panel_width,
        )

        # Create button for deleting currently selected curve
        self.delete_curve_button = tk.Button(
            self.curves_management_frame,
            text="Delete",
            command=self.delete_selected_curve,
            width=self.side_panel_width,
        )

        self.curves_listbox.bind(
            "<Delete>", lambda event: self.delete_curve_button.invoke()
        )

        self.selected_curve: BezierCurve | None = None

        self.selected_point: CanvasPoint | None = None
        self.selected_point_offset: Tuple[int, int] = (0, 0)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<B1-Motion>", self.handle_drag)

        self.curves_listbox.bind("<<ListboxSelect>>", self.handle_curve_select)

        # Set up curve options manager
        self.curve_color_changer = ColorChanger(
            self.curve_appearance_frame,
            DEFAULT_CURVE_COLOR,
            "Curve Color",
            self.get_selected_curve,
            self.change_curve_color,
        )

        self.x_equation_text = tk.Text(
            self.equations_frame,
            height=1,
            state=tk.DISABLED,
        )
        self.y_equation_text = tk.Text(
            self.equations_frame,
            height=1,
            state=tk.DISABLED,
        )
        self.update_equation_texts(None)
        self.copy_equations_button = tk.Button(
            self.curve_equations_options_frame,
            text="Copy As Tuple",
            command=self.copy_equations,
        )

        self.not_found_x_extrema_label_text = "No Extremum in X"
        self.not_found_y_extrema_label_text = "No Extremum in Y"
        self.found_x_extrema_label_text = "Extremum in X at t = "
        self.found_y_extrema_label_text = "Extremum in Y at t = "
        self.x_extrema_label = tk.Label(
            self.equations_frame,
            text=self.not_found_x_extrema_label_text,
            anchor=tk.W,
        )
        self.y_extrema_label = tk.Label(
            self.equations_frame,
            text=self.not_found_y_extrema_label_text,
            anchor=tk.W,
        )
        self.substitute_extrema_button = tk.Button(
            self.curve_equations_options_frame,
            text="Substitute Extrema for t",
            command=self.substitute_extrema_for_t,
        )

        self.reset_points_button = tk.Button(
            self.curves_management_frame,
            text="Reset Points",
            command=self.reset_points,
            width=self.side_panel_width,
        )

        self.show_dashed_line_var: tk.IntVar = tk.IntVar(value=1)

        self.show_dashed_line_checkbutton = tk.Checkbutton(
            self.curve_show_toggle_options_frame,
            text="Show Dash. Line",
            variable=self.show_dashed_line_var,
            onvalue=1,
            offvalue=0,
            command=self.toggle_dashed_line_showing,
            state=tk.DISABLED,
        )

        self.show_extremum_points_var: tk.IntVar = tk.IntVar(value=1)

        self.show_extremum_points_checkbutton = tk.Checkbutton(
            self.curve_show_toggle_options_frame,
            text="Show Extr. Pts",
            variable=self.show_extremum_points_var,
            onvalue=1,
            offvalue=0,
            command=self.toggle_extremum_points_showing,
            state=tk.DISABLED,
        )

        self.image_manager = ImageManager(self.canvas)

        self.import_image_button = tk.Button(
            self.image_options_frame,
            text="Import Image",
            command=self.image_manager.import_image,
            width=self.side_panel_width,
        )

        self.remove_image_button = tk.Button(
            self.image_options_frame,
            text="Remove Image",
            command=self.image_manager.remove_image,
            width=self.side_panel_width,
        )

        self.show_bounding_box_var: tk.IntVar = tk.IntVar(value=0)

        self.show_bounding_box_checkbutton = tk.Checkbutton(
            self.curve_show_toggle_options_frame,
            text="Show B. Box",
            variable=self.show_bounding_box_var,
            onvalue=1,
            offvalue=0,
            command=self.toggle_bounding_box_showing,
            state=tk.DISABLED,
        )

        # Enable saving
        self.save_as_label = tk.Label(self.saving_management_frame, text="Save As:")

        self.save_as_entry = tk.Entry(
            self.saving_management_frame, width=self.side_panel_listbox_width
        )

        self.projects_listbox = tk.Listbox(
            self.saving_management_frame,
            width=self.side_panel_listbox_width,
            height=25,
        )

        self.save_info_label = tk.Label(self.saving_management_frame)

        self.save_project_button = tk.Button(
            self.saving_management_frame,
            text="Save Project",
            command=lambda: projects_manager.save_project(
                self.projects_listbox,
                self.save_as_entry,
                self.save_info_label,
                self.image_manager.get_active_image_filename,
                self.get_list_of_curves,
            ),
            width=self.side_panel_width,
        )

        self.load_project_button = tk.Button(
            self.saving_management_frame,
            text="Load Project",
            command=lambda: projects_manager.load_project(
                self.projects_listbox,
                self.save_as_entry,
                self.save_info_label,
                self.remove_everything,
                self.image_manager.display_new_image,
                self.new_curve,
            ),
            width=self.side_panel_width,
        )

        self.delete_project_button = tk.Button(
            self.saving_management_frame,
            text="Delete Project",
            command=lambda: projects_manager.delete_project(
                self.projects_listbox, self.save_as_entry, self.save_info_label
            ),
            width=self.side_panel_width,
        )

        projects_manager.recognize_save_files(
            self.projects_listbox, self.save_info_label
        )

    # Define function that executes every time user selects a different curve
    def handle_curve_select(self, event) -> None:
        if len(self.curves_listbox.curselection()) > 0:
            self.selected_curve = self.curves[self.curves_listbox.curselection()[0]]

            self.selected_curve.raise_curve_widgets(self.canvas)

            # Put the points of the selected curve on top & hide all other points
            for curve in self.curves:
                for point in curve.points:
                    if point in self.selected_curve.points:
                        self.canvas.itemconfig(point.point, state=tk.NORMAL)
                        self.canvas.tag_raise(point.point)
                    else:
                        self.canvas.itemconfig(point.point, state=tk.HIDDEN)

                    for point in curve.extremum_points:
                        self.canvas.delete(point.point)

                if curve.dashed_line is not None:
                    if curve == self.selected_curve:
                        self.canvas.itemconfig(curve.dashed_line, state=tk.NORMAL)
                    else:
                        self.canvas.itemconfig(curve.dashed_line, state=tk.HIDDEN)

            self.display_curve_equations()

            self.display_curve_extrema()

            self.selected_curve.substituted_extremum = None

            self.selected_curve.substitute_extremum_for_t(self.canvas)

            self.show_dashed_line_checkbutton.config(state=tk.NORMAL)

            self.show_dashed_line_var.set(self.selected_curve.dashed_line_visible)

            self.show_extremum_points_checkbutton.config(state=tk.NORMAL)

            self.show_extremum_points_var.set(
                self.selected_curve.extremum_points_visible
            )

            self.show_bounding_box_checkbutton.config(state=tk.NORMAL)

            self.show_bounding_box_var.set(self.selected_curve.bounding_box_visible)

            self.curve_color_changer.force_change_color(self.selected_curve.color)

    def get_selected_curve(self) -> BezierCurve | None:
        return self.selected_curve

    def get_list_of_curves(self) -> List[BezierCurve]:
        return self.curves

    # Define function for creating points on canvas
    def new_canvas_points(self, points_coords: List[P]) -> List[CanvasPoint]:
        canvas_points_list = []

        for point_tuple in points_coords:
            color = DEFAULT_CONTROL_POINT_COLOR
            if point_tuple == points_coords[0] or point_tuple == points_coords[-1]:
                color = DEFAULT_ENDPOINT_COLOR
            canvas_point = CanvasPoint(point_tuple, self.canvas, color=color)
            canvas_points_list.append(canvas_point)

        return canvas_points_list

    # Define functions for creating new curves
    def new_curve(
        self, amount_of_points: int, points_list: List[P] | None = None
    ) -> None:
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        new_points = None

        if points_list is None:
            new_points = self.new_canvas_points(
                get_points_default_pos(
                    amount_of_points,
                    canvas_width,
                    canvas_height,
                )
            )
        else:
            new_points = self.new_canvas_points(points_list)

        last_curve_number = 0

        for curve in self.curves:
            if len(curve.points) == len(new_points):
                last_curve_number = int(curve.name.split("#")[-1])

        new_curve_name = f"{curve_names[amount_of_points]} #{last_curve_number + 1}"

        new_curve = BezierCurve(
            name=new_curve_name,
            points=new_points,
            canvas_height=canvas_width,
        )

        self.curves.append(new_curve)

        new_curve.draw(self.canvas)

        if self.selected_curve is not None:
            self.selected_curve.raise_curve_widgets(self.canvas)

        self.curves_listbox.insert(tk.END, new_curve_name)

        # Because the newly added curve is not automatically selected, we can immediately hide its points
        for point in new_curve.points:
            self.canvas.itemconfig(point.point, state=tk.HIDDEN)
        for point in new_curve.extremum_points:
            self.canvas.itemconfig(point.point, state=tk.HIDDEN)
        if new_curve.dashed_line is not None:
            self.canvas.itemconfig(new_curve.dashed_line, state=tk.HIDDEN)

    def draw_selected_curve(self) -> None:
        if self.selected_curve is not None:
            self.selected_curve.draw(self.canvas)

            self.display_curve_equations()

            self.display_curve_extrema()

    # Define function for deleting currently selected curve
    def delete_selected_curve(self) -> None:
        if len(self.curves_listbox.curselection()) > 0:
            curve_index_to_be_deleted = self.curves_listbox.curselection()[0]

            curve_to_be_deleted = self.curves[curve_index_to_be_deleted]

            if self.selected_curve == curve_to_be_deleted:
                self.selected_curve = None

            for point in curve_to_be_deleted.points:
                if self.selected_point == point.point:
                    self.selected_point = None

                self.canvas.delete(point.point)

            if curve_to_be_deleted.curve is not None:
                self.canvas.delete(curve_to_be_deleted.curve)

            if curve_to_be_deleted.dashed_line is not None:
                self.canvas.delete(curve_to_be_deleted.dashed_line)

            for extremum_point in curve_to_be_deleted.extremum_points:
                self.canvas.delete(extremum_point.point)

            if curve_to_be_deleted.bounding_box_canvas_line is not None:
                self.canvas.delete(curve_to_be_deleted.bounding_box_canvas_line)

            self.curves.pop(curve_index_to_be_deleted)

            self.curves_listbox.delete(self.curves_listbox.curselection())

            # Revert every widget to default

            self.display_curve_equations()

            self.display_curve_extrema()

            self.show_dashed_line_var.set(value=1)

            self.show_dashed_line_checkbutton.config(state=tk.DISABLED)

            self.show_extremum_points_var.set(value=1)

            self.show_extremum_points_checkbutton.config(state=tk.DISABLED)

            self.show_bounding_box_var.set(value=0)

            self.show_bounding_box_checkbutton.config(state=tk.DISABLED)

            self.curve_color_changer.revert_original_color()

    # Handle mouse events
    def handle_click(self, event) -> None:
        if self.selected_curve is not None:
            for point in self.selected_curve.points:
                tags = self.canvas.gettags(point.point)
                if "current" in tags:
                    self.selected_point = point
                    break
            else:
                self.selected_point = None

            if self.selected_point is not None:
                self.selected_point_offset = (
                    event.x - self.selected_point.point_coords[0],
                    event.y - self.selected_point.point_coords[1],
                )

    def handle_drag(self, event) -> None:
        if self.selected_point:
            # Calculate distance moved from last position
            dx, dy = (
                event.x
                - self.selected_point.point_coords[0]
                + -1 * self.selected_point_offset[0],
                event.y
                - self.selected_point.point_coords[1]
                + -1 * self.selected_point_offset[1],
            )

            # Ensure that the point doesn't get out of bounds
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if (self.selected_point.point_coords[0] + dx) < 0:
                dx = -self.selected_point.point_coords[0]
            elif (self.selected_point.point_coords[0] + dx) > canvas_width:
                dx = canvas_width - self.selected_point.point_coords[0]
            if (self.selected_point.point_coords[1] + dy) < 0:
                dy = -self.selected_point.point_coords[1]
            elif (self.selected_point.point_coords[1] + dy) > canvas_height:
                dy = canvas_height - self.selected_point.point_coords[1]

            self.canvas.move(self.selected_point.point, dx, dy)

            self.selected_point.point_coords = (
                self.selected_point.point_coords[0] + dx,
                self.selected_point.point_coords[1] + dy,
            )

            self.draw_selected_curve()

    # Define functions for setting certain colors
    def change_curve_color(self, new_color: str) -> None:
        if self.selected_curve is not None:
            self.selected_curve.change_curve_color(self.canvas, new_color)

    def change_endpoints_color(self, new_color) -> None:
        if self.selected_curve is not None:
            self.selected_curve.change_endpoints_color(self.canvas, new_color)

    def change_control_points_color(self, new_color) -> None:
        if self.selected_curve is not None:
            self.selected_curve.change_control_points_color(self.canvas, new_color)

    def change_x_extremum_points_color(self, new_color) -> None:
        if self.selected_curve is not None:
            self.selected_curve.x_extremum_points_color = new_color
            self.selected_curve.draw(self.canvas)

    def change_y_extremum_points_color(self, new_color) -> None:
        if self.selected_curve is not None:
            self.selected_curve.y_extremum_points_color = new_color
            self.selected_curve.draw(self.canvas)

    def update_equation_texts(self, new_text: Tuple[str, str] | None) -> None:
        # Make the texts accesible for the program
        self.x_equation_text.config(state=tk.NORMAL)
        self.y_equation_text.config(state=tk.NORMAL)

        # Clear the texts
        self.x_equation_text.delete(1.0, tk.END)
        self.y_equation_text.delete(1.0, tk.END)

        # Update the texts
        if new_text is not None:
            self.x_equation_text.insert(1.0, new_text[0])
            self.y_equation_text.insert(1.0, new_text[1])
        else:
            self.x_equation_text.insert(1.0, "x =")
            self.y_equation_text.insert(1.0, "y =")

        # Make the texts read-only for the user
        self.x_equation_text.config(state=tk.DISABLED)
        self.y_equation_text.config(state=tk.DISABLED)

    def display_curve_equations(self) -> None:
        if self.selected_curve is not None:
            self.update_equation_texts(self.selected_curve.equations)
        else:
            self.update_equation_texts(None)

    def copy_equations(self) -> None:
        # If the texts are empty, don't put it into the user's clipboard
        if self.selected_curve is not None:
            if self.parent is not None:
                # Clear user's clipboard
                self.parent.clipboard_clear()

                # Strip string off of the "x = " and "\n" (I don't know why these are created)
                new_x_equation = self.x_equation_text.get(1.0, tk.END)

                while new_x_equation.endswith("\n"):
                    new_x_equation = new_x_equation[:-1]

                new_x_equation = new_x_equation.lstrip("x = ")

                # Same with y
                new_y_equation = self.y_equation_text.get(1.0, tk.END)

                while new_y_equation.endswith("\n"):
                    new_y_equation = new_y_equation[:-1]

                new_y_equation = new_y_equation.lstrip("y = ")

                # Finally, put the tuple into the user's clipboard
                self.parent.clipboard_append(f"({new_x_equation}, {new_y_equation})")

    def display_curve_extrema(self) -> None:
        if self.selected_curve is not None:
            # Extrema in X
            if len(self.selected_curve.x_extrema) > 0:
                text = f"{self.found_x_extrema_label_text}"

                for i in range(len(self.selected_curve.x_extrema)):
                    extremum = self.selected_curve.x_extrema[i]

                    if i != 0:
                        text += f"; {extremum}"
                    else:
                        text += str(extremum)

                self.x_extrema_label.config(text=text)
            else:
                self.x_extrema_label.config(text=self.not_found_x_extrema_label_text)

            # Extrema in Y
            if len(self.selected_curve.y_extrema) > 0:
                text = f"{self.found_y_extrema_label_text}"

                for i in range(len(self.selected_curve.y_extrema)):
                    extremum = self.selected_curve.y_extrema[i]

                    if i != 0:
                        text += f"; {extremum}"
                    else:
                        text += str(extremum)

                self.y_extrema_label.config(text=text)
            else:
                self.y_extrema_label.config(text=self.not_found_y_extrema_label_text)
        else:
            self.x_extrema_label.config(text=self.not_found_x_extrema_label_text)
            self.y_extrema_label.config(text=self.not_found_y_extrema_label_text)

    def substitute_extrema_for_t(self) -> None:
        if self.selected_curve is not None:
            if len(self.selected_curve.all_extrema) > 0:
                if self.selected_curve.substituted_extremum is None:
                    self.selected_curve.substituted_extremum = 0
                elif self.selected_curve.substituted_extremum < (
                    (len(self.selected_curve.all_extrema) - 1)
                ):
                    self.selected_curve.substituted_extremum += 1
                else:
                    self.selected_curve.substituted_extremum = None
            else:
                self.selected_curve.substituted_extremum = None

            self.selected_curve.substitute_extremum_for_t(self.canvas)

            if self.selected_curve.substituted_extremum is not None:
                self.update_equation_texts(self.selected_curve.substituted_equations)
            else:
                self.display_curve_equations()

    def reset_points(self) -> None:
        if self.selected_curve is not None:
            new_points_pos = get_points_default_pos(
                len(self.selected_curve.points),
                self.canvas.winfo_width(),
                self.canvas.winfo_height(),
            )

            for i in range(len(self.selected_curve.points)):
                dx, dy = (
                    new_points_pos[i][0]
                    - self.selected_curve.points[i].point_coords[0],
                    new_points_pos[i][1]
                    - self.selected_curve.points[i].point_coords[1],
                )

                self.canvas.move(self.selected_curve.points[i].point, dx, dy)

                self.selected_curve.points[i].point_coords = new_points_pos[i]

            self.draw_selected_curve()

    # Define functions for toggling showing of certain elements
    def toggle_dashed_line_showing(self) -> None:
        if self.selected_curve is not None:
            self.selected_curve.dashed_line_visible = bool(
                self.show_dashed_line_var.get()
            )

            self.selected_curve.draw(self.canvas)

    def toggle_extremum_points_showing(self) -> None:
        if self.selected_curve is not None:
            self.selected_curve.extremum_points_visible = bool(
                self.show_extremum_points_var.get()
            )

            self.selected_curve.draw(self.canvas)

    def toggle_bounding_box_showing(self) -> None:
        if self.selected_curve is not None:
            self.selected_curve.bounding_box_visible = bool(
                self.show_bounding_box_var.get()
            )

            self.selected_curve.draw(self.canvas)

    def remove_everything(self):
        self.image_manager.remove_image()

        self.selected_curve = None

        for i in range(len(self.curves)):
            self.curves_listbox.selection_set(tk.END)

            self.delete_selected_curve()

    def grid_widgets(self) -> None:
        # MAIN GRID
        self.canvas_frame.grid(
            column=1,
            row=0,
            sticky=tk.NSEW,
            padx=self.widget_padding,
            pady=self.widget_padding,
        )
        self.right_panel_frame.grid(
            column=2, row=0, rowspan=2, sticky=tk.NS, padx=(0, self.widget_padding)
        )
        self.bottom_panel_frame.grid(
            column=1, row=1, sticky=tk.SW, pady=self.widget_padding
        )
        self.left_panel_frame.grid(
            column=0, row=0, rowspan=2, sticky=tk.NS, padx=(self.widget_padding, 0)
        )

        # FRAMES' CHILD FRAMES GRID
        self.equations_frame.grid(column=0, row=0, pady=(0, self.widget_padding))
        self.curve_appearance_frame.grid(
            column=0, row=1, sticky=tk.S, pady=self.widget_padding
        )
        self.curve_equations_options_frame.grid(column=0, row=1, sticky=tk.W)
        self.curve_show_toggle_options_frame.grid(
            column=1, row=1, padx=self.widget_padding, sticky=tk.E
        )
        self.saving_management_frame.grid(column=0, row=0, sticky=tk.N)
        self.image_options_frame.grid(
            column=0, row=1, sticky=tk.S, pady=self.widget_padding
        )
        self.curves_management_frame.grid(column=0, row=0, sticky=tk.N)

        # Canvas frame grid
        self.canvas.grid(
            column=0,
            row=0,
            sticky=tk.NSEW,
        )

        # Right panel frame grid
        self.curves_listbox.grid(
            column=0,
            row=0,
            pady=self.widget_padding,
            sticky=tk.E,
        )

        self.new_linear_button.grid(column=0, row=1, pady=self.widget_padding)
        self.new_quadratic_button.grid(column=0, row=2)
        self.new_cubic_button.grid(column=0, row=3, pady=self.widget_padding)
        self.delete_curve_button.grid(column=0, row=4)
        self.reset_points_button.grid(column=0, row=5, pady=self.widget_padding)

        self.curve_color_changer.label.grid(
            column=0,
            row=0,
        )
        self.curve_color_changer.button.grid(
            column=1,
            row=0,
        )
        self.curve_color_changer.indicator.grid(
            column=1,
            row=0,
        )

        # Bottom panel frame grid
        self.x_equation_text.grid(
            column=0,
            row=0,
            columnspan=1,
            padx=self.widget_padding,
            pady=self.widget_padding,
            sticky=tk.W,
        )
        self.y_equation_text.grid(
            column=0,
            row=1,
            columnspan=1,
            padx=self.widget_padding,
            pady=self.widget_padding,
            sticky=tk.W,
        )
        self.x_extrema_label.grid(
            column=1, row=0, pady=self.widget_padding, sticky=tk.E
        )
        self.y_extrema_label.grid(
            column=1, row=1, pady=self.widget_padding, sticky=tk.W
        )

        self.copy_equations_button.grid(
            column=0,
            row=0,
        )
        self.substitute_extrema_button.grid(column=1, row=0, padx=self.widget_padding)

        self.show_dashed_line_checkbutton.grid(column=0, row=0)
        self.show_extremum_points_checkbutton.grid(column=1, row=0)
        self.show_bounding_box_checkbutton.grid(column=2, row=0)

        # Left panel frame grid
        left_panel_padding = (2 * self.widget_padding, self.widget_padding)

        self.projects_listbox.grid(column=0, row=0, pady=self.widget_padding)
        self.save_project_button.grid(column=0, row=1)
        self.save_as_label.grid(
            column=0,
            row=2,
            padx=left_panel_padding,
            pady=self.widget_padding,
            sticky=tk.W,
        )
        self.save_as_entry.grid(column=0, row=3)
        self.save_info_label.grid(column=0, row=4, pady=self.widget_padding)
        self.load_project_button.grid(column=0, row=5)
        self.delete_project_button.grid(column=0, row=6, pady=self.widget_padding)

        self.import_image_button.grid(
            column=0, row=0, padx=self.widget_padding, pady=self.widget_padding
        )
        self.remove_image_button.grid(column=0, row=1)

        # Configure weights

        self.grid_columnconfigure(1, weight=5)

        self.grid_rowconfigure(0, weight=1)

        self.canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.bottom_panel_frame.grid_columnconfigure(0, weight=1)

        self.bottom_panel_frame.grid_rowconfigure(0, weight=1)
        self.bottom_panel_frame.grid_rowconfigure(1, weight=1)
        self.bottom_panel_frame.grid_rowconfigure(2, weight=1)

        self.equations_frame.grid_columnconfigure(0, weight=1)

        self.equations_frame.grid_rowconfigure(0, weight=1)
        self.equations_frame.grid_rowconfigure(1, weight=1)

        self.left_panel_frame.grid_rowconfigure(0, weight=1)
        self.left_panel_frame.grid_rowconfigure(1, weight=1)

        self.saving_management_frame.grid_rowconfigure(0, weight=1)

        self.right_panel_frame.grid_rowconfigure(0, weight=1)
        self.right_panel_frame.grid_rowconfigure(1, weight=1)

        self.curves_management_frame.grid_rowconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Bezierve v2")
        self.iconbitmap(absolute_path_to_icon)
        self.wm_state("zoomed")
        self.create_widgets()

    def create_widgets(self) -> None:
        frame = MainFrame(self)
        frame.grid_widgets()
        frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
