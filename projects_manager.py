from ROOT_PATH import root_path
from pathlib import Path
from os import remove, listdir, path as os_path
from tkinter import Listbox, Entry, Label, END
from typing import List, Callable
from bezier_curve import BezierCurve
from canvas_point import P


def find_selected_project_filename(projects_listbox: Listbox) -> str | None:
    selected_projects = projects_listbox.curselection()

    if len(selected_projects) > 0:
        project_name = projects_listbox.get(selected_projects[0])

        selected_project_filename = str(
            Path(root_path, f"./saves/{project_name}.txt").resolve()
        )  # We can use only the first one selected because only one can be selected

        return selected_project_filename
    else:
        return None


def save_project(
    projects_listbox: Listbox,
    save_as_entry: Entry,
    save_info_label: Label,
    get_active_image_filename_func: Callable[[], str | None],
    get_list_of_curves_func: Callable[[], List[BezierCurve]],
) -> None:
    name_chosen_by_user: str = save_as_entry.get()

    list_of_curves: List[BezierCurve] = get_list_of_curves_func()

    if len(list_of_curves) > 0:
        if len(name_chosen_by_user) > 0 and not name_chosen_by_user.isspace():
            if name_chosen_by_user not in projects_listbox.get(0, END):
                name_of_project: str = name_chosen_by_user.strip()
                name_of_project = name_of_project.lower()
                name_of_project = name_of_project.replace(" ", "_")

                imported_image_filename: str | None = get_active_image_filename_func()

                try:
                    with open(
                        str(
                            Path(root_path, f"./saves/{name_of_project}.txt").resolve()
                        ),
                        "w",
                    ) as f:
                        f.write(name_of_project + "\n")

                        if imported_image_filename is not None:
                            f.write(imported_image_filename + "\n")
                        else:
                            f.write("\n")

                        for curve in list_of_curves:
                            points_seq: str = ""

                            for point in curve.points:
                                points_seq += (
                                    f"{point.point_coords[0]},{point.point_coords[1]};"
                                )

                            points_seq = points_seq.rstrip(";")

                            points_seq += "\n"

                            f.write(points_seq)

                    projects_listbox.insert(END, name_of_project)

                    save_as_entry.delete(0, END)

                    save_info_label.config(
                        text="Project saved successfully!", fg="green"
                    )
                except:
                    save_info_label.config(text="Error while creating file!", fg="red")
            else:
                save_info_label.config(text="Project name already exists!", fg="orange")
        else:
            save_info_label.config(text="Project has no name!", fg="orange")
    else:
        save_info_label.config(text="Project has no curves!", fg="orange")


def load_project(
    projects_listbox: Listbox,
    save_as_entry: Entry,
    save_info_label: Label,
    remove_everything_func: Callable[[], None],
    new_image_func: Callable[[str], None],
    new_curve_func: Callable[[int, List[P] | None], None],
) -> None:
    selected_project_filename = find_selected_project_filename(projects_listbox)

    if selected_project_filename is not None:
        img_filename: str | None = None

        all_curve_point_seqs: List[str] = []

        try:
            with open(selected_project_filename, "r") as f:
                lines = f.readlines()

                lines = [line.strip().rstrip("\n") for line in lines]

                _img_filename = lines[1]

                if len(_img_filename) > 0:
                    img_filename = _img_filename

                all_curve_point_seqs = lines[2:]
        except:
            save_info_label.config(text="Error while loading file!", fg="red")
        else:
            remove_everything_func()

            # Load project
            if img_filename is not None:
                new_image_func(img_filename)

            for point_seq in all_curve_point_seqs:
                all_points = point_seq.split(";")

                points: List[P] = []

                for point in all_points:
                    xy = point.split(",")

                    x = int(xy[0])
                    y = int(xy[1])

                    points.append((x, y))

                new_curve_func(len(all_points), points)

            save_info_label.config(text="Project loaded successfully!", fg="green")

            save_as_entry.delete(0, END)
    else:
        save_info_label.config(text="No project selected!", fg="orange")


def delete_project(
    projects_listbox: Listbox,
    save_as_entry: Entry,
    save_info_label: Label,
) -> None:
    selected_project_filename = find_selected_project_filename(projects_listbox)

    if selected_project_filename is not None:
        try:
            remove(selected_project_filename)
        except:
            save_info_label.config(text="Error while deleting project!", fg="red")
        else:
            projects_listbox.delete(projects_listbox.curselection()[0])

            save_info_label.config(text="Project deleted successfully!", fg="green")

        save_as_entry.delete(0, END)


def recognize_save_files(
    projects_listbox: Listbox,
    save_info_label: Label,
):
    try:
        for filename in listdir(str(Path(root_path, "./saves/").resolve())):
            if filename.endswith(".txt"):
                projects_listbox.insert(END, os_path.splitext(filename)[0])
    except:
        save_info_label.config(text="Error while importing projects!", fg="red")
