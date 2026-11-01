
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF: renders PDF pages for visual preview
from PIL import Image
from contextlib import ExitStack
import os


class PDFMergerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("PDF Toolkit")
        self.geometry("1100x800")
        self.minsize(900, 650)

        # Theme configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#1E1E2E")

        # Store PDF files and checkbox references
        self.pdf_files = []
        self.file_vars = {}
        self.file_checkboxes = {}

        # Application heading
        self.title_label = ctk.CTkLabel(
            self,
            text="PDF Toolkit",
            font=("Arial", 32, "bold")
        )
        self.title_label.pack(pady=(30, 25))

        # Add PDF button
        self.add_button = ctk.CTkButton(
            self,
            text="Add PDF Files",
            command=self.add_pdf_files,
            width=250,
            height=55,
            font=("Arial", 17)
        )
        self.add_button.pack(pady=15)

        # PDF count
        self.count_label = ctk.CTkLabel(
            self,
            text="Selected PDFs: 0",
            font=("Arial", 18, "bold")
        )
        self.count_label.pack(pady=15)

        # ------------------------------------------------
        # BUTTON CONTAINER
        # Pack BEFORE the PDF list to reserve bottom space
        # ------------------------------------------------

        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.button_frame.pack(
            side="bottom",
            pady=20
        )

        # Select All button
        self.select_all_button = ctk.CTkButton(
            self.button_frame,
            text="Select All",
            command=self.select_all_files,
            width=155,
            height=45,
            font=("Arial", 15)
        )
        self.select_all_button.pack(
            side="left",
            padx=6
        )

        # Remove Selected button
        self.remove_button = ctk.CTkButton(
            self.button_frame,
            text="Remove Selected",
            command=self.remove_selected_files,
            width=175,
            height=45,
            font=("Arial", 15)
        )
        self.remove_button.pack(
            side="left",
            padx=6
        )

        # Clear All button
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear All",
            command=self.clear_all_files,
            width=145,
            height=45,
            fg_color="#B83232",
            hover_color="#922B2B",
            font=("Arial", 15)
        )
        self.clear_button.pack(
            side="left",
            padx=6
        )

        # Merge PDFs button
        self.merge_button = ctk.CTkButton(
            self.button_frame,
            text="Merge PDFs",
            command=self.merge_pdfs,
            width=155,
            height=45,
            fg_color="#16804A",
            hover_color="#116638",
            font=("Arial", 15, "bold")
        )
        self.merge_button.pack(
            side="left",
            padx=6
        )

        # NEW: Split PDF button
        self.split_button = ctk.CTkButton(
            self.button_frame,
            text="Split PDF",
            command=self.split_pdf,
            width=155,
            height=45,
            fg_color="#8E44AD",
            hover_color="#71368A",
            font=("Arial", 15, "bold")
        )
        self.split_button.pack(
            side="left",
            padx=6
        )

        # Rotate PDF button with visual page preview
        self.rotate_button = ctk.CTkButton(
            self.button_frame,
            text="Rotate PDF",
            command=self.rotate_pdf,
            width=130,
            height=45,
            fg_color="#2874A6",
            hover_color="#1F5A82",
            font=("Arial", 15, "bold")
        )
        self.rotate_button.pack(
            side="left",
            padx=6
        )

        self.more_tools_button = ctk.CTkButton(
            self.button_frame,
            text="More Tools",
            command=self.open_more_tools,
            width=100,
            height=45,
            fg_color="#5555A5",
            hover_color="#41417F",
            font=("Arial", 15, "bold")
        )
        self.more_tools_button.pack(side="left", padx=6)

        # ------------------------------------------------
        # SCROLLABLE PDF LIST
        # Fixed height prevents buttons from disappearing
        # ------------------------------------------------

        self.file_list = ctk.CTkScrollableFrame(
            self,
            height=350,
            label_text="Selected PDF Files",
            fg_color="#2B2B2B"
        )

        self.file_list.pack(
            pady=15,
            padx=30,
            fill="both",
            expand=False
        )

    # ------------------------------------------------
    # ADD PDF FILES
    # ------------------------------------------------

    def add_pdf_files(self):

        selected_files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not selected_files:
            return

        added_count = 0

        for file_path in selected_files:

            if file_path in self.pdf_files:
                continue

            self.pdf_files.append(file_path)

            var = ctk.BooleanVar(value=True)

            filename = os.path.basename(file_path)

            self.create_file_row(file_path, len(self.pdf_files), var)

            self.file_vars[file_path] = var

            added_count += 1

        self.update_count()

        if added_count == 0:
            messagebox.showinfo(
                "Information",
                "These PDF files are already in the list."
            )

    # ------------------------------------------------
    # SELECT ALL PDF FILES
    # ------------------------------------------------

    def select_all_files(self):

        for var in self.file_vars.values():
            var.set(True)

    # ------------------------------------------------
    # REMOVE SELECTED PDF FILES
    # ------------------------------------------------

    def remove_selected_files(self):

        selected = [
            path for path, var in self.file_vars.items()
            if var.get()
        ]

        if not selected:
            messagebox.showinfo(
                "Information",
                "Please select at least one PDF file to remove."
            )
            return

        for file_path in selected:

            self.file_checkboxes[file_path].destroy()

            del self.file_checkboxes[file_path]
            del self.file_vars[file_path]

            self.pdf_files.remove(file_path)

        self.refresh_file_list()
        self.update_count()

    # ------------------------------------------------
    # CLEAR ALL PDF FILES
    # ------------------------------------------------

    def clear_all_files(self):

        if not self.pdf_files:
            return

        confirm = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to remove all PDF files?"
        )

        if not confirm:
            return

        for checkbox in self.file_checkboxes.values():
            checkbox.destroy()

        self.pdf_files.clear()
        self.file_vars.clear()
        self.file_checkboxes.clear()

        self.update_count()

    # ------------------------------------------------
    # REFRESH PDF LIST AND NUMBERING
    # ------------------------------------------------

    def refresh_file_list(self):

        for widget in self.file_list.winfo_children():
            widget.destroy()

        self.file_vars.clear()
        self.file_checkboxes.clear()

        for index, file_path in enumerate(
            self.pdf_files, start=1
        ):

            var = ctk.BooleanVar(value=True)

            filename = os.path.basename(file_path)

            self.create_file_row(file_path, index, var)

            self.file_vars[file_path] = var

    # ------------------------------------------------
    # ------------------------------------------------
    # CREATE PDF ROW WITH REORDER CONTROLS
    # ------------------------------------------------

    def create_file_row(self, file_path, index, var):

        row_frame = ctk.CTkFrame(
            self.file_list,
            fg_color="transparent"
        )
        row_frame.pack(fill="x", padx=10, pady=6)

        filename = os.path.basename(file_path)

        checkbox = ctk.CTkCheckBox(
            row_frame,
            text=f"{index}. {filename}",
            variable=var,
            font=("Arial", 15),
            checkbox_width=25,
            checkbox_height=25
        )
        checkbox.pack(side="left", padx=5)

        up_button = ctk.CTkButton(
            row_frame,
            text="↑",
            width=35,
            height=30,
            font=("Arial", 16, "bold"),
            command=lambda path=file_path: self.move_pdf(path, -1)
        )
        up_button.pack(side="right", padx=(4, 2))

        down_button = ctk.CTkButton(
            row_frame,
            text="↓",
            width=35,
            height=30,
            font=("Arial", 16, "bold"),
            command=lambda path=file_path: self.move_pdf(path, 1)
        )
        down_button.pack(side="right", padx=(2, 4))

        self.file_checkboxes[file_path] = row_frame

    # ------------------------------------------------
    # MOVE PDF UP OR DOWN
    # ------------------------------------------------

    def move_pdf(self, file_path, direction):

        current_index = self.pdf_files.index(file_path)
        new_index = current_index + direction

        if new_index < 0 or new_index >= len(self.pdf_files):
            return

        self.pdf_files[current_index], self.pdf_files[new_index] = (
            self.pdf_files[new_index],
            self.pdf_files[current_index]
        )

        checked_states = {
            path: var.get()
            for path, var in self.file_vars.items()
        }

        self.refresh_file_list()

        for path, was_checked in checked_states.items():
            if path in self.file_vars:
                self.file_vars[path].set(was_checked)

    # UPDATE PDF COUNT
    # ------------------------------------------------

    def update_count(self):

        self.count_label.configure(
            text=f"Selected PDFs: {len(self.pdf_files)}"
        )

    # ------------------------------------------------
    # MERGE SELECTED PDF FILES
    # EXISTING FUNCTIONALITY - RETAINED
    # ------------------------------------------------

    def merge_pdfs(self):

        # Get checked PDF files in displayed order
        selected_files = [
            path for path in self.pdf_files
            if self.file_vars[path].get()
        ]

        # Validate selection
        if not selected_files:
            messagebox.showwarning(
                "No PDFs Selected",
                "Please select at least one PDF file."
            )
            return

        # Ask destination and output filename
        output_path = filedialog.asksaveasfilename(
            title="Save Merged PDF",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            initialfile="Merged_Document.pdf"
        )

        if not output_path:
            return

        # Prevent overwriting one of the input files
        input_paths = {
            os.path.normcase(os.path.abspath(path))
            for path in selected_files
        }

        output_absolute_path = os.path.normcase(
            os.path.abspath(output_path)
        )

        if output_absolute_path in input_paths:

            messagebox.showerror(
                "Invalid Output Location",
                "Please choose a different output filename."
            )
            return

        writer = PdfWriter()

        try:

            # Keep source PDF files open during merging
            with ExitStack() as stack:

                for file_path in selected_files:

                    pdf_file = stack.enter_context(
                        open(file_path, "rb")
                    )

                    reader = PdfReader(pdf_file)

                    # Check password protection
                    if reader.is_encrypted:

                        if reader.decrypt("") == 0:
                            raise ValueError(
                                "Password-protected PDF:\n"
                                + os.path.basename(file_path)
                            )

                    # Append pages in displayed order
                    writer.append(reader)

                # Create merged PDF
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)

            messagebox.showinfo(
                "Merge Successful",
                f"PDFs merged successfully!\n\n"
                f"Files merged: {len(selected_files)}\n\n"
                f"Output file:\n{output_path}"
            )

        except Exception as error:

            messagebox.showerror(
                "Merge Failed",
                f"Unable to merge PDF files.\n\n"
                f"Error: {error}"
            )

        finally:
            writer.close()


    # ------------------------------------------------
    # ROTATE PDF WITH LIVE PAGE PREVIEW
    # ------------------------------------------------

    def rotate_pdf(self):

        selected_files = [
            path for path in self.pdf_files
            if self.file_vars[path].get()
        ]

        if len(selected_files) == 0:
            messagebox.showwarning(
                "Rotate PDF",
                "Please select one PDF file."
            )
            return

        if len(selected_files) > 1:
            messagebox.showwarning(
                "Rotate PDF",
                "Please select only ONE PDF file.\n\nUncheck the other files."
            )
            return

        input_path = selected_files[0]

        try:
            preview_document = fitz.open(input_path)

            if preview_document.needs_pass:
                preview_document.close()
                messagebox.showerror(
                    "Password Required",
                    "This PDF is password protected. "
                    "Password-protected PDFs are not supported yet."
                )
                return

            total_pages = len(preview_document)

            if total_pages == 0:
                preview_document.close()
                messagebox.showerror(
                    "Rotate PDF",
                    "The selected PDF contains no pages."
                )
                return

        except Exception as error:
            messagebox.showerror(
                "Unable to Open PDF",
                f"Could not open this PDF for preview.\n\nError: {error}"
            )
            return

        # Use the available screen size so the preview window never extends
        # below the Windows taskbar or beyond the display.
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1000, screen_width - 60)
        window_height = min(760, screen_height - 100)

        dialog = ctk.CTkToplevel(self)
        dialog.title("Rotate PDF - Page Preview")
        dialog.geometry(f"{window_width}x{window_height}")
        dialog.minsize(min(760, window_width), min(560, window_height))
        dialog.transient(self)
        dialog.grab_set()

        self.update_idletasks()
        x = max(0, (screen_width - window_width) // 2)
        y = max(0, (screen_height - window_height) // 2)
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

        page_rotations = [0] * total_pages
        current_page = {"index": 0}
        preview_image_reference = {"image": None}
        render_job = {"id": None}

        # Fixed-height control sections are packed first. The preview receives
        # only the remaining space and cannot push buttons outside the window.
        heading = ctk.CTkLabel(
            dialog,
            text="Rotate PDF Pages",
            font=("Arial", 22, "bold")
        )
        heading.pack(pady=(8, 2))

        filename_label = ctk.CTkLabel(
            dialog,
            text=os.path.basename(input_path),
            font=("Arial", 13),
            text_color="#B8B8B8"
        )
        filename_label.pack(pady=(0, 2))

        page_info_label = ctk.CTkLabel(
            dialog,
            text=f"Page 1 of {total_pages}",
            font=("Arial", 15, "bold")
        )
        page_info_label.pack(pady=(1, 4))

        navigation_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        navigation_frame.pack(pady=2)

        rotation_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        rotation_frame.pack(pady=2)

        rotation_info_label = ctk.CTkLabel(
            dialog,
            text="Rotation adjustment for this page: 0°",
            font=("Arial", 12, "bold")
        )
        rotation_info_label.pack(pady=(1, 4))

        bottom_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        bottom_frame.pack(side="bottom", pady=(3, 8))

        preview_frame = ctk.CTkFrame(
            dialog,
            fg_color="#242424",
            corner_radius=10
        )
        preview_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=4
        )

        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Loading page preview...",
            font=("Arial", 15)
        )
        preview_label.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=8
        )

        def render_current_page():
            if not dialog.winfo_exists():
                return

            page_index = current_page["index"]
            page = preview_document.load_page(page_index)

            # Render at a moderate resolution, then fit the complete page
            # inside the preview viewport while preserving its aspect ratio.
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False)
            page_image = Image.frombytes(
                "RGB", [pixmap.width, pixmap.height], pixmap.samples
            )

            rotation = page_rotations[page_index] % 360

            # PIL's negative angle produces clockwise rotation.
            if rotation:
                page_image = page_image.rotate(-rotation, expand=True)

            # Recalculate the available preview area on every render.
            # Do not impose a minimum image size: that caused clipping on
            # smaller screens and when a page was rotated to landscape.
            preview_frame.update_idletasks()
            available_width = max(preview_frame.winfo_width() - 70, 240)
            available_height = max(preview_frame.winfo_height() - 70, 220)

            fit_scale = min(
                available_width / page_image.width,
                available_height / page_image.height,
                1.0
            )
            fitted_size = (
                max(1, int(page_image.width * fit_scale)),
                max(1, int(page_image.height * fit_scale))
            )
            page_image = page_image.resize(
                fitted_size, Image.Resampling.LANCZOS
            )

            preview_ctk_image = ctk.CTkImage(
                light_image=page_image,
                dark_image=page_image,
                size=page_image.size
            )

            preview_image_reference["image"] = preview_ctk_image
            preview_label.configure(
                image=preview_ctk_image,
                text=""
            )

            page_info_label.configure(
                text=f"Page {page_index + 1} of {total_pages}"
            )
            rotation_info_label.configure(
                text=f"Rotation adjustment for this page: {rotation}°"
            )

            previous_button.configure(
                state="normal" if page_index > 0 else "disabled"
            )
            next_button.configure(
                state="normal" if page_index < total_pages - 1 else "disabled"
            )

        def schedule_render():
            # Wait briefly for the window/layout to settle before rendering.
            if render_job["id"] is not None:
                try:
                    dialog.after_cancel(render_job["id"])
                except Exception:
                    pass
            render_job["id"] = dialog.after(100, render_current_page)

        def show_previous_page():
            if current_page["index"] > 0:
                current_page["index"] -= 1
                schedule_render()

        def show_next_page():
            if current_page["index"] < total_pages - 1:
                current_page["index"] += 1
                schedule_render()

        def rotate_current_page(degrees):
            page_index = current_page["index"]
            page_rotations[page_index] = (
                page_rotations[page_index] + degrees
            ) % 360
            schedule_render()

        def reset_current_page():
            page_rotations[current_page["index"]] = 0
            schedule_render()

        previous_button = ctk.CTkButton(
            navigation_frame,
            text="← Previous Page",
            command=show_previous_page,
            width=155,
            height=34,
            font=("Arial", 13)
        )
        previous_button.pack(side="left", padx=8)

        next_button = ctk.CTkButton(
            navigation_frame,
            text="Next Page →",
            command=show_next_page,
            width=155,
            height=34,
            font=("Arial", 13)
        )
        next_button.pack(side="left", padx=8)

        rotate_left_button = ctk.CTkButton(
            rotation_frame,
            text="↶ Rotate Left 90°",
            command=lambda: rotate_current_page(-90),
            width=170,
            height=38,
            font=("Arial", 13, "bold")
        )
        rotate_left_button.pack(side="left", padx=6)

        rotate_right_button = ctk.CTkButton(
            rotation_frame,
            text="Rotate Right 90° ↷",
            command=lambda: rotate_current_page(90),
            width=180,
            height=38,
            font=("Arial", 13, "bold")
        )
        rotate_right_button.pack(side="left", padx=6)

        reset_button = ctk.CTkButton(
            rotation_frame,
            text="Reset Page",
            command=reset_current_page,
            width=120,
            height=38,
            fg_color="#666666",
            hover_color="#4D4D4D",
            font=("Arial", 13)
        )
        reset_button.pack(side="left", padx=6)

        def close_dialog():
            if render_job["id"] is not None:
                try:
                    dialog.after_cancel(render_job["id"])
                except Exception:
                    pass
            if not preview_document.is_closed:
                preview_document.close()
            if dialog.winfo_exists():
                dialog.destroy()

        def save_rotated_pdf():
            if not any(page_rotations):
                messagebox.showinfo(
                    "No Changes",
                    "No pages have been rotated.",
                    parent=dialog
                )
                return

            default_name = (
                os.path.splitext(os.path.basename(input_path))[0]
                + "_rotated.pdf"
            )

            output_path = filedialog.asksaveasfilename(
                parent=dialog,
                title="Save Rotated PDF",
                initialfile=default_name,
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )

            if not output_path:
                return

            if os.path.normcase(os.path.abspath(output_path)) == os.path.normcase(
                os.path.abspath(input_path)
            ):
                messagebox.showerror(
                    "Invalid Output Location",
                    "Cannot overwrite the original PDF. "
                    "Please choose another filename.",
                    parent=dialog
                )
                return

            writer = PdfWriter()

            try:
                with open(input_path, "rb") as input_file:
                    reader = PdfReader(input_file)

                    if reader.is_encrypted and reader.decrypt("") == 0:
                        raise ValueError("This PDF is password protected.")

                    if len(reader.pages) != total_pages:
                        raise ValueError(
                            "The PDF page count changed while it was open."
                        )

                    for page_index, page in enumerate(reader.pages):
                        rotation = page_rotations[page_index]
                        if rotation:
                            page.rotate(rotation)
                        writer.add_page(page)

                    with open(output_path, "wb") as output_file:
                        writer.write(output_file)

                messagebox.showinfo(
                    "Rotation Successful",
                    f"Rotated PDF saved successfully.\n\n"
                    f"Pages changed: "
                    f"{sum(1 for value in page_rotations if value)}\n\n"
                    f"Output file:\n{output_path}",
                    parent=dialog
                )
                close_dialog()

            except Exception as error:
                messagebox.showerror(
                    "Rotation Failed",
                    f"Unable to save the rotated PDF.\n\nError: {error}",
                    parent=dialog
                )

            finally:
                writer.close()

        save_button = ctk.CTkButton(
            bottom_frame,
            text="Save Rotated PDF",
            command=save_rotated_pdf,
            width=185,
            height=40,
            fg_color="#16804A",
            hover_color="#116638",
            font=("Arial", 14, "bold")
        )
        save_button.pack(side="left", padx=8)

        cancel_button = ctk.CTkButton(
            bottom_frame,
            text="Cancel",
            command=close_dialog,
            width=120,
            height=40,
            fg_color="#555555",
            hover_color="#3F3F3F",
            font=("Arial", 14)
        )
        cancel_button.pack(side="left", padx=8)

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        dialog.bind("<Escape>", lambda event: close_dialog())

        # Render after the dialog has its final usable dimensions.
        dialog.after(250, render_current_page)

    # ------------------------------------------------
    # CUSTOM PAGE-RANGE DIALOG
    # ------------------------------------------------

    def ask_page_range_dialog(self, total_pages):

        dialog = ctk.CTkToplevel(self)
        dialog.title("Split PDF - Select Pages")
        dialog.geometry("520x340")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Centre the dialog over the main application
        self.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 520) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 340) // 2
        dialog.geometry(f"520x340+{x}+{y}")

        result = {"page_range": None}

        heading = ctk.CTkLabel(
            dialog,
            text="Select Pages to Extract",
            font=("Arial", 22, "bold")
        )
        heading.pack(pady=(22, 12))

        page_count = ctk.CTkLabel(
            dialog,
            text=f"Total pages in this PDF: {total_pages}",
            font=("Arial", 16, "bold")
        )
        page_count.pack(pady=(0, 12))

        instructions = ctk.CTkLabel(
            dialog,
            text=(
                "Enter individual page numbers or page ranges.\\n"
                "Use commas to separate multiple pages or ranges.\\n\\n"
                "Examples:\\n"
                "1-10       Extract pages 1 through 10\\n"
                "5,10,15    Extract pages 5, 10 and 15\\n"
                "1-5,10,15-20"
            ),
            font=("Arial", 14),
            justify="left"
        )
        instructions.pack(pady=(0, 14))

        page_entry = ctk.CTkEntry(
            dialog,
            width=430,
            height=38,
            font=("Arial", 15),
            placeholder_text="Example: 1-5,10,15-20"
        )
        page_entry.pack(pady=(0, 18))
        page_entry.focus_set()

        button_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )
        button_frame.pack(pady=(0, 15))

        def extract_pages():
            result["page_range"] = page_entry.get().strip()
            dialog.destroy()

        def cancel_dialog():
            dialog.destroy()

        extract_button = ctk.CTkButton(
            button_frame,
            text="Extract",
            command=extract_pages,
            width=130,
            height=38,
            font=("Arial", 14, "bold")
        )
        extract_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=cancel_dialog,
            width=130,
            height=38,
            fg_color="#555555",
            hover_color="#3F3F3F",
            font=("Arial", 14)
        )
        cancel_button.pack(side="left", padx=10)

        dialog.bind("<Return>", lambda event: extract_pages())
        dialog.bind("<Escape>", lambda event: cancel_dialog())
        dialog.protocol("WM_DELETE_WINDOW", cancel_dialog)

        self.wait_window(dialog)
        return result["page_range"]

    # ------------------------------------------------
    # NEW FEATURE: SPLIT PDF
    # ------------------------------------------------

    def split_pdf(self):

        # Get checked PDF files
        selected_files = [
            path for path in self.pdf_files
            if self.file_vars[path].get()
        ]

        # Exactly one PDF must be selected
        if not selected_files:

            messagebox.showwarning(
                "Split PDF",
                "Please select one PDF file to split."
            )
            return

        if len(selected_files) > 1:

            messagebox.showwarning(
                "Split PDF",
                "Please select only ONE PDF file.\n\n"
                "Uncheck the other files."
            )
            return

        input_path = selected_files[0]

        try:

            # Open selected PDF
            with open(input_path, "rb") as input_file:

                reader = PdfReader(input_file)

                # Check password protection
                if reader.is_encrypted:

                    if reader.decrypt("") == 0:
                        messagebox.showerror(
                            "Password Required",
                            "This PDF is password protected."
                        )
                        return

                total_pages = len(reader.pages)

                if total_pages == 0:
                    messagebox.showerror(
                        "Error",
                        "The selected PDF contains no pages."
                    )
                    return

                # Ask for page range using a larger custom dialog
                page_range = self.ask_page_range_dialog(total_pages)

                if not page_range:
                    return

                # Parse page ranges
                pages_to_extract = set()

                try:

                    parts = page_range.split(",")

                    for part in parts:

                        part = part.strip()

                        if not part:
                            raise ValueError(
                                "Empty page range detected."
                            )

                        if "-" in part:

                            start, end = map(
                                int,
                                part.split("-", 1)
                            )

                            if start > end:
                                raise ValueError(
                                    "Start page cannot exceed end page."
                                )

                            if start < 1 or end > total_pages:
                                raise ValueError(
                                    f"Enter pages between 1 and {total_pages}."
                                )

                            pages_to_extract.update(
                                range(start, end + 1)
                            )

                        else:

                            page = int(part)

                            if page < 1 or page > total_pages:
                                raise ValueError(
                                    f"Enter pages between 1 and {total_pages}."
                                )

                            pages_to_extract.add(page)

                except ValueError as error:

                    messagebox.showerror(
                        "Invalid Page Range",
                        str(error)
                    )
                    return

                if not pages_to_extract:
                    return

                # Default output filename
                default_name = (
                    os.path.splitext(
                        os.path.basename(input_path)
                    )[0] + "_split.pdf"
                )

                # Ask where to save
                output_path = filedialog.asksaveasfilename(
                    title="Save Split PDF",
                    initialfile=default_name,
                    defaultextension=".pdf",
                    filetypes=[("PDF Files", "*.pdf")]
                )

                if not output_path:
                    return

                # Prevent overwriting original PDF
                if os.path.normcase(
                    os.path.abspath(output_path)
                ) == os.path.normcase(
                    os.path.abspath(input_path)
                ):

                    messagebox.showerror(
                        "Invalid Output Location",
                        "Cannot overwrite the original PDF."
                    )
                    return

                # Create extracted PDF
                writer = PdfWriter()

                try:

                    for page_number in sorted(pages_to_extract):

                        writer.add_page(
                            reader.pages[page_number - 1]
                        )

                    with open(output_path, "wb") as output_file:
                        writer.write(output_file)

                finally:
                    writer.close()

            messagebox.showinfo(
                "Split Successful",
                f"PDF split successfully!\n\n"
                f"Pages extracted: {len(pages_to_extract)}\n\n"
                f"Output file:\n{output_path}"
            )

        except Exception as error:

            messagebox.showerror(
                "Split Failed",
                f"Unable to split PDF.\n\n"
                f"Error: {error}"
            )



    def _large_input_dialog(
        self, title, prompt, initial_value="", password=False,
        integer=False, minimum=None
    ):
        """Larger, readable replacement for tkinter's small simpledialog prompts."""
        result = {"value": None}

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(560, screen_w - 80)
        height = min(290, screen_h - 120)

        window = ctk.CTkToplevel(self)
        window.title(title)
        window.geometry(
            f"{width}x{height}+{max(0, (screen_w-width)//2)}"
            f"+{max(0, (screen_h-height)//2)}"
        )
        window.minsize(min(460, width), min(250, height))
        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window, text=title, font=("Arial", 22, "bold")
        ).pack(pady=(22, 10))

        ctk.CTkLabel(
            window, text=prompt, font=("Arial", 16),
            wraplength=width - 60, justify="left"
        ).pack(fill="x", padx=28, pady=(0, 12))

        entry = ctk.CTkEntry(
            window,
            width=width - 70,
            height=42,
            font=("Arial", 16),
            show="*" if password else ""
        )
        entry.pack(padx=25, pady=4)
        if initial_value != "":
            entry.insert(0, str(initial_value))
        entry.focus_set()

        error_label = ctk.CTkLabel(
            window, text="", font=("Arial", 12), text_color="#E57373"
        )
        error_label.pack(pady=(4, 0))

        buttons = ctk.CTkFrame(window, fg_color="transparent")
        buttons.pack(side="bottom", pady=18)

        def submit():
            value = entry.get()
            if not value.strip():
                error_label.configure(text="Please enter a value.")
                entry.focus_set()
                return
            if integer:
                try:
                    parsed = int(value)
                    if minimum is not None and parsed < minimum:
                        raise ValueError
                except ValueError:
                    message = (
                        f"Enter a whole number greater than or equal to {minimum}."
                        if minimum is not None else "Enter a valid whole number."
                    )
                    error_label.configure(text=message)
                    entry.focus_set()
                    return
                result["value"] = parsed
            else:
                result["value"] = value
            window.destroy()

        def cancel():
            window.destroy()

        ctk.CTkButton(
            buttons, text="OK", command=submit, width=135, height=40,
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            buttons, text="Cancel", command=cancel, width=135, height=40,
            fg_color="#555555", hover_color="#3F3F3F",
            font=("Arial", 14)
        ).pack(side="left", padx=8)

        window.bind("<Return>", lambda event: submit())
        window.bind("<Escape>", lambda event: cancel())
        window.protocol("WM_DELETE_WINDOW", cancel)
        self.wait_window(window)
        return result["value"]

    # ================================================================
    # ADDITIONAL PDF TOOLS
    # ================================================================

    def open_more_tools(self):
        """Open additional PDF tools with a permanently visible Close button."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = min(680, screen_width - 80)
        window_height = min(760, screen_height - 100)

        window = ctk.CTkToplevel(self)
        window.title("Additional PDF Tools")
        window.geometry(
            f"{window_width}x{window_height}"
            f"+{max(0, (screen_width-window_width)//2)}"
            f"+{max(0, (screen_height-window_height)//2)}"
        )
        window.minsize(min(520, window_width), min(500, window_height))
        window.transient(self)
        window.grab_set()

        ctk.CTkLabel(
            window,
            text="Additional PDF Tools",
            font=("Arial", 24, "bold")
        ).pack(pady=(18, 5))

        ctk.CTkLabel(
            window,
            text="Select a tool. Most tools work with one selected PDF.",
            font=("Arial", 13),
            text_color="gray"
        ).pack(pady=(0, 8))

        # Pack the footer BEFORE the expanding scrollable frame.
        # This reserves space at the bottom, keeping Close visible.
        footer = ctk.CTkFrame(window, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=(6, 14))

        ctk.CTkButton(
            footer,
            text="Close",
            command=window.destroy,
            width=150,
            height=42,
            fg_color="#555555",
            hover_color="#3F3F3F",
            font=("Arial", 14, "bold")
        ).pack()

        tools_frame = ctk.CTkScrollableFrame(
            window,
            label_text="PDF operations"
        )
        tools_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(8, 4)
        )

        tools = [
            ("Delete PDF Pages with Preview", self.delete_pages_preview),
            ("Extract PDF Pages with Preview", self.extract_pages_preview),
            ("Rearrange PDF Pages with Preview", self.rearrange_pages_preview),
            ("Add Text Watermark", self.add_watermark),
            ("Add Page Numbers", self.add_page_numbers),
            ("Compress PDF", self.compress_pdf),
            ("Protect PDF with Password", self.protect_pdf),
            ("Unlock PDF (password required)", self.unlock_pdf),
            ("Convert PDF to Images", self.pdf_to_images),
            ("Convert Images to PDF", self.images_to_pdf),
        ]

        for label, command in tools:
            button = ctk.CTkButton(
                tools_frame,
                text=label,
                command=command,
                height=42,
                font=("Arial", 14, "bold")
            )
            button.pack(fill="x", padx=12, pady=6)

        window.bind("<Escape>", lambda event: window.destroy())
    def _get_one_selected_pdf(self, feature_name):
        selected = [
            path for path in self.pdf_files
            if self.file_vars[path].get()
        ]
        if not selected:
            messagebox.showwarning(
                feature_name, "Please select one PDF file."
            )
            return None
        if len(selected) != 1:
            messagebox.showwarning(
                feature_name,
                "Please select only ONE PDF file.\n\nUncheck the other files."
            )
            return None
        return selected[0]

    def _choose_output_pdf(self, input_path, suffix, title):
        base = os.path.splitext(os.path.basename(input_path))[0]
        output = filedialog.asksaveasfilename(
            title=title,
            initialfile=f"{base}_{suffix}.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not output:
            return None
        if os.path.normcase(os.path.abspath(output)) == os.path.normcase(
            os.path.abspath(input_path)
        ):
            messagebox.showerror(
                title, "The output cannot overwrite the original PDF."
            )
            return None
        return output

    def _page_selection_preview(self, mode):
        """
        Shared visual page selector.
        mode='delete': check pages to delete.
        mode='extract': check pages to keep in the extracted PDF.
        """
        feature = "Delete PDF Pages" if mode == "delete" else "Extract PDF Pages"
        input_path = self._get_one_selected_pdf(feature)
        if not input_path:
            return

        try:
            doc = fitz.open(input_path)
            if doc.needs_pass:
                doc.close()
                messagebox.showerror(feature, "Password-protected PDFs are not supported here.")
                return
            count = len(doc)
            if count == 0:
                doc.close()
                messagebox.showerror(feature, "This PDF has no pages.")
                return
        except Exception as error:
            messagebox.showerror(feature, f"Could not open PDF:\n{error}")
            return

        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1200, screen_w - 40), min(900, screen_h - 80)
        win = ctk.CTkToplevel(self)
        win.title(feature + " - Page Preview")
        win.geometry(f"{w}x{h}+{max(0,(screen_w-w)//2)}+{max(0,(screen_h-h)//2)}")
        win.minsize(min(760, w), min(580, h))
        win.transient(self)
        win.grab_set()

        # For delete, all pages start retained; for extract, none are selected.
        selected = set() if mode == "extract" else set()
        current = {"index": 0}
        image_ref = {"image": None}

        ctk.CTkLabel(win, text=feature, font=("Arial", 22, "bold")).pack(pady=(10, 2))
        info = ctk.CTkLabel(win, text=f"Page 1 of {count}", font=("Arial", 15, "bold"))
        info.pack(pady=3)

        status = ctk.CTkLabel(win, text="", font=("Arial", 13, "bold"))
        status.pack(pady=2)

        nav = ctk.CTkFrame(win, fg_color="transparent")
        nav.pack(pady=3)

        action_row = ctk.CTkFrame(win, fg_color="transparent")
        action_row.pack(pady=3)

        footer = ctk.CTkFrame(win, fg_color="transparent")
        footer.pack(side="bottom", pady=10)

        preview_frame = ctk.CTkFrame(win, fg_color="#242424")
        preview_frame.pack(fill="both", expand=True, padx=18, pady=5)

        preview = ctk.CTkLabel(preview_frame, text="Loading preview...")
        preview.pack(fill="both", expand=True, padx=8, pady=8)

        def close():
            if not doc.is_closed:
                doc.close()
            if win.winfo_exists():
                win.destroy()

        def render():
            idx = current["index"]
            page = doc.load_page(idx)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            preview_frame.update_idletasks()
            box_w = max(240, preview_frame.winfo_width() - 70)
            box_h = max(220, preview_frame.winfo_height() - 70)
            fit_scale = min(box_w / image.width, box_h / image.height, 1.0)
            image = image.resize(
                (max(1, int(image.width * fit_scale)),
                 max(1, int(image.height * fit_scale))),
                Image.Resampling.LANCZOS
            )
            cimage = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            image_ref["image"] = cimage
            preview.configure(image=cimage, text="")
            info.configure(text=f"Page {idx + 1} of {count}")
            if mode == "delete":
                state = "MARKED FOR DELETION" if idx in selected else "Will be kept"
            else:
                state = "SELECTED FOR EXTRACTION" if idx in selected else "Not selected"
            status.configure(text=state)
            prev.configure(state="normal" if idx > 0 else "disabled")
            nxt.configure(state="normal" if idx < count - 1 else "disabled")
            toggle.configure(
                text=("Keep this page" if idx in selected else "Mark page for deletion")
                if mode == "delete" else
                ("Unselect this page" if idx in selected else "Select this page")
            )

        def previous():
            if current["index"] > 0:
                current["index"] -= 1
                render()

        def next_page():
            if current["index"] < count - 1:
                current["index"] += 1
                render()

        def toggle_page():
            idx = current["index"]
            if idx in selected:
                selected.remove(idx)
            else:
                selected.add(idx)
            render()

        prev = ctk.CTkButton(nav, text="← Previous", command=previous, width=140)
        prev.pack(side="left", padx=8)
        nxt = ctk.CTkButton(nav, text="Next →", command=next_page, width=140)
        nxt.pack(side="left", padx=8)

        toggle = ctk.CTkButton(
            action_row, text="Mark page", command=toggle_page,
            width=230, height=38, font=("Arial", 13, "bold")
        )
        toggle.pack(side="left", padx=8)

        def save_selection():
            if mode == "delete":
                pages_to_keep = [i for i in range(count) if i not in selected]
                if not selected:
                    messagebox.showinfo(feature, "No pages were marked for deletion.", parent=win)
                    return
                if not pages_to_keep:
                    messagebox.showerror(feature, "You cannot delete every page. Keep at least one page.", parent=win)
                    return
                suffix = "pages_deleted"
            else:
                pages_to_keep = sorted(selected)
                if not pages_to_keep:
                    messagebox.showinfo(feature, "Select at least one page to extract.", parent=win)
                    return
                suffix = "pages_extracted"

            output = self._choose_output_pdf(input_path, suffix, "Save PDF")
            if not output:
                return

            writer = PdfWriter()
            try:
                with open(input_path, "rb") as f:
                    reader = PdfReader(f)
                    if reader.is_encrypted and reader.decrypt("") == 0:
                        raise ValueError("Password-protected PDF.")
                    for page_idx in pages_to_keep:
                        writer.add_page(reader.pages[page_idx])
                    with open(output, "wb") as out:
                        writer.write(out)
                messagebox.showinfo(
                    feature,
                    f"Saved successfully.\nPages in output: {len(pages_to_keep)}\n\n{output}",
                    parent=win
                )
                close()
            except Exception as error:
                messagebox.showerror(feature, f"Could not save PDF:\n{error}", parent=win)
            finally:
                writer.close()

        ctk.CTkButton(
            footer, text="Save PDF", command=save_selection,
            width=160, height=40, fg_color="#16804A"
        ).pack(side="left", padx=8)
        ctk.CTkButton(
            footer, text="Cancel", command=close,
            width=120, height=40, fg_color="#555555"
        ).pack(side="left", padx=8)

        win.protocol("WM_DELETE_WINDOW", close)
        win.bind("<Escape>", lambda event: close())
        win.after(200, render)

    def delete_pages_preview(self):
        self._page_selection_preview("delete")

    def extract_pages_preview(self):
        self._page_selection_preview("extract")

    def rearrange_pages_preview(self):
        input_path = self._get_one_selected_pdf("Rearrange PDF Pages")
        if not input_path:
            return
        try:
            doc = fitz.open(input_path)
            if doc.needs_pass:
                doc.close()
                messagebox.showerror("Rearrange Pages", "Password-protected PDFs are not supported here.")
                return
            total = len(doc)
            if total < 2:
                doc.close()
                messagebox.showinfo("Rearrange Pages", "At least two pages are required.")
                return
        except Exception as error:
            messagebox.showerror("Rearrange Pages", str(error))
            return

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1200, sw - 40), min(900, sh - 80)
        win = ctk.CTkToplevel(self)
        win.title("Rearrange PDF Pages - Preview")
        win.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        win.minsize(min(760, w), min(580, h))
        win.transient(self)
        win.grab_set()

        order = list(range(total))
        pos = {"index": 0}
        img_ref = {"image": None}

        ctk.CTkLabel(win, text="Rearrange PDF Pages", font=("Arial", 22, "bold")).pack(pady=(10, 2))
        info = ctk.CTkLabel(win, text=f"Output position 1 of {total}", font=("Arial", 15, "bold"))
        info.pack(pady=3)
        nav = ctk.CTkFrame(win, fg_color="transparent")
        nav.pack(pady=3)
        move = ctk.CTkFrame(win, fg_color="transparent")
        move.pack(pady=3)
        footer = ctk.CTkFrame(win, fg_color="transparent")
        footer.pack(side="bottom", pady=10)
        frame = ctk.CTkFrame(win, fg_color="#242424")
        frame.pack(fill="both", expand=True, padx=18, pady=5)
        preview = ctk.CTkLabel(frame, text="Loading preview...")
        preview.pack(fill="both", expand=True, padx=8, pady=8)

        def close():
            if not doc.is_closed:
                doc.close()
            if win.winfo_exists():
                win.destroy()

        def render():
            original_index = order[pos["index"]]
            page = doc.load_page(original_index)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            frame.update_idletasks()
            box_w = max(240, frame.winfo_width() - 70)
            box_h = max(220, frame.winfo_height() - 70)
            fit_scale = min(box_w / image.width, box_h / image.height, 1.0)
            image = image.resize(
                (max(1, int(image.width * fit_scale)),
                 max(1, int(image.height * fit_scale))),
                Image.Resampling.LANCZOS
            )
            cimage = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            img_ref["image"] = cimage
            preview.configure(image=cimage, text="")
            info.configure(text=f"Output position {pos['index']+1} of {total}  |  Original page {original_index+1}")
            back.configure(state="normal" if pos["index"] > 0 else "disabled")
            forward.configure(state="normal" if pos["index"] < total-1 else "disabled")
            up.configure(state="normal" if pos["index"] > 0 else "disabled")
            down.configure(state="normal" if pos["index"] < total-1 else "disabled")

        def previous():
            if pos["index"] > 0:
                pos["index"] -= 1
                render()

        def following():
            if pos["index"] < total-1:
                pos["index"] += 1
                render()

        def move_item(direction):
            old = pos["index"]
            new = old + direction
            if 0 <= new < total:
                order[old], order[new] = order[new], order[old]
                pos["index"] = new
                render()

        back = ctk.CTkButton(nav, text="← Previous", command=previous, width=140)
        back.pack(side="left", padx=8)
        forward = ctk.CTkButton(nav, text="Next →", command=following, width=140)
        forward.pack(side="left", padx=8)
        up = ctk.CTkButton(move, text="Move Earlier ↑", command=lambda: move_item(-1), width=150)
        up.pack(side="left", padx=8)
        down = ctk.CTkButton(move, text="Move Later ↓", command=lambda: move_item(1), width=150)
        down.pack(side="left", padx=8)

        def save_order():
            output = self._choose_output_pdf(input_path, "rearranged", "Save Rearranged PDF")
            if not output:
                return
            writer = PdfWriter()
            try:
                with open(input_path, "rb") as f:
                    reader = PdfReader(f)
                    if reader.is_encrypted and reader.decrypt("") == 0:
                        raise ValueError("Password-protected PDF.")
                    for idx in order:
                        writer.add_page(reader.pages[idx])
                    with open(output, "wb") as out:
                        writer.write(out)
                messagebox.showinfo("Rearrange Pages", f"Saved successfully:\n{output}", parent=win)
                close()
            except Exception as error:
                messagebox.showerror("Rearrange Pages", f"Could not save:\n{error}", parent=win)
            finally:
                writer.close()

        ctk.CTkButton(footer, text="Save New Order", command=save_order, width=170, height=40, fg_color="#16804A").pack(side="left", padx=8)
        ctk.CTkButton(footer, text="Cancel", command=close, width=120, height=40, fg_color="#555555").pack(side="left", padx=8)
        win.protocol("WM_DELETE_WINDOW", close)
        win.bind("<Escape>", lambda event: close())
        win.after(200, render)

    def add_watermark(self):
        input_path = self._get_one_selected_pdf("Add Watermark")
        if not input_path:
            return
        text = self._large_input_dialog("Text Watermark", "Enter the text to place on every PDF page:")
        if not text:
            return
        output = self._choose_output_pdf(input_path, "watermarked", "Save Watermarked PDF")
        if not output:
            return
        doc = None
        try:
            doc = fitz.open(input_path)
            if doc.needs_pass:
                raise ValueError("Password-protected PDFs are not supported here.")
            for page in doc:
                rect = page.rect
                fontsize = max(20, min(54, rect.width / max(len(text), 8) * 1.4))
                page.insert_text(
                    fitz.Point(rect.width * 0.18, rect.height * 0.55),
                    text,
                    fontsize=fontsize,
                    fontname="helv",
                    color=(0.65, 0.65, 0.65),
                    overlay=True,
                    morph=(fitz.Point(rect.width * 0.5, rect.height * 0.5), fitz.Matrix(1, 0, 0, 1, 0, 0))
                )
            doc.save(output, garbage=4, deflate=True)
            messagebox.showinfo("Watermark", f"Watermark added:\n{output}")
        except Exception as error:
            messagebox.showerror("Watermark", f"Could not add watermark:\n{error}")
        finally:
            if doc:
                doc.close()

    def add_page_numbers(self):
        input_path = self._get_one_selected_pdf("Add Page Numbers")
        if not input_path:
            return
        start = self._large_input_dialog("Page Numbers", "Enter the starting page number:", initial_value="1", integer=True, minimum=1)
        if start is None:
            return
        output = self._choose_output_pdf(input_path, "numbered", "Save Numbered PDF")
        if not output:
            return
        doc = None
        try:
            doc = fitz.open(input_path)
            if doc.needs_pass:
                raise ValueError("Password-protected PDFs are not supported here.")
            for idx, page in enumerate(doc):
                rect = page.rect
                label = str(start + idx)
                page.insert_text(
                    fitz.Point(rect.width / 2 - 5, rect.height - 28),
                    label,
                    fontsize=11,
                    fontname="helv",
                    color=(0, 0, 0),
                    overlay=True
                )
            doc.save(output, garbage=4, deflate=True)
            messagebox.showinfo("Page Numbers", f"Page numbers added:\n{output}")
        except Exception as error:
            messagebox.showerror("Page Numbers", f"Could not add page numbers:\n{error}")
        finally:
            if doc:
                doc.close()

    def compress_pdf(self):
        input_path = self._get_one_selected_pdf("Compress PDF")
        if not input_path:
            return
        output = self._choose_output_pdf(input_path, "compressed", "Save Compressed PDF")
        if not output:
            return
        doc = None
        try:
            original_size = os.path.getsize(input_path)
            doc = fitz.open(input_path)
            if doc.needs_pass:
                raise ValueError("Password-protected PDFs are not supported here.")
            doc.save(output, garbage=4, deflate=True, clean=True, deflate_images=True, deflate_fonts=True)
            doc.close()
            doc = None
            new_size = os.path.getsize(output)
            change = (1 - new_size / original_size) * 100 if original_size else 0
            messagebox.showinfo(
                "Compress PDF",
                f"Compression completed.\nOriginal: {original_size/1024:.1f} KB\nNew: {new_size/1024:.1f} KB\n"
                f"{'Reduced' if change >= 0 else 'Increased'} by {abs(change):.1f}%\n\n{output}"
            )
        except Exception as error:
            messagebox.showerror("Compress PDF", f"Could not compress PDF:\n{error}")
        finally:
            if doc:
                doc.close()

    def protect_pdf(self):
        input_path = self._get_one_selected_pdf("Protect PDF")
        if not input_path:
            return
        password = self._large_input_dialog("Protect PDF", "Set a password required to open this PDF:", password=True)
        if not password:
            return
        confirm = self._large_input_dialog("Confirm Password", "Re-enter the password to confirm:", password=True)
        if confirm is None:
            return
        if password != confirm:
            messagebox.showerror("Protect PDF", "Passwords do not match.")
            return
        output = self._choose_output_pdf(input_path, "protected", "Save Protected PDF")
        if not output:
            return
        writer = PdfWriter()
        try:
            with open(input_path, "rb") as f:
                reader = PdfReader(f)
                if reader.is_encrypted and reader.decrypt("") == 0:
                    raise ValueError("The source PDF is already password protected.")
                writer.append(reader)
                writer.encrypt(password)
                with open(output, "wb") as out:
                    writer.write(out)
            messagebox.showinfo("Protect PDF", f"Password protection added:\n{output}")
        except Exception as error:
            messagebox.showerror("Protect PDF", f"Could not protect PDF:\n{error}")
        finally:
            writer.close()

    def unlock_pdf(self):
        input_path = self._get_one_selected_pdf("Unlock PDF")
        if not input_path:
            return
        password = self._large_input_dialog(
            "Unlock PDF", "Enter the existing password for this PDF:",
            password=True
        )
        if password is None:
            return
        output = self._choose_output_pdf(input_path, "unlocked", "Save Unlocked PDF")
        if not output:
            return
        writer = PdfWriter()
        try:
            with open(input_path, "rb") as f:
                reader = PdfReader(f)
                if reader.is_encrypted and reader.decrypt(password) == 0:
                    raise ValueError("Incorrect password.")
                writer.append(reader)
                with open(output, "wb") as out:
                    writer.write(out)
            messagebox.showinfo("Unlock PDF", f"Password protection removed:\n{output}")
        except Exception as error:
            messagebox.showerror("Unlock PDF", f"Could not unlock PDF:\n{error}")
        finally:
            writer.close()

    def pdf_to_images(self):
        input_path = self._get_one_selected_pdf("PDF to Images")
        if not input_path:
            return
        folder = filedialog.askdirectory(title="Choose folder for page images")
        if not folder:
            return
        doc = None
        try:
            doc = fitz.open(input_path)
            if doc.needs_pass:
                raise ValueError("Password-protected PDFs are not supported here.")
            base = os.path.splitext(os.path.basename(input_path))[0]
            for idx, page in enumerate(doc, start=1):
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                pix.save(os.path.join(folder, f"{base}_page_{idx:03d}.png"))
            messagebox.showinfo("PDF to Images", f"Exported {len(doc)} page(s) as PNG images to:\n{folder}")
        except Exception as error:
            messagebox.showerror("PDF to Images", f"Could not convert PDF:\n{error}")
        finally:
            if doc:
                doc.close()

    def images_to_pdf(self):
        image_paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if not image_paths:
            return
        output = filedialog.asksaveasfilename(
            title="Save PDF from Images",
            initialfile="Images_Combined.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not output:
            return
        doc = fitz.open()
        try:
            for image_path in image_paths:
                image_doc = fitz.open(image_path)
                try:
                    rect = image_doc[0].rect
                    page = doc.new_page(width=rect.width, height=rect.height)
                    page.insert_image(page.rect, filename=image_path)
                finally:
                    image_doc.close()
            doc.save(output, garbage=4, deflate=True)
            messagebox.showinfo("Images to PDF", f"Created PDF from {len(image_paths)} image(s):\n{output}")
        except Exception as error:
            messagebox.showerror("Images to PDF", f"Could not create PDF:\n{error}")
        finally:
            doc.close()



# ------------------------------------------------
# APPLICATION ENTRY POINT
# ------------------------------------------------

if __name__ == "__main__":

    app = PDFMergerApp()
    app.mainloop()
