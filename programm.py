import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QFileDialog, QLabel, QComboBox, QMessageBox, QLineEdit,
                             QTabWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageOps
import os
import io

class ImageConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Conversor de imagini")
        self.setGeometry(100, 100, 800, 600)

        self.input_path = ""
        self.output_path = ""
        self.current_image = None
        self.history = []  # adăugat: istoric pentru undo

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Taburi
        self.conversion_tab = QWidget()
        self.filter_tab = QWidget()
        self.resize_tab = QWidget()
        self.crop_tab = QWidget()

        self.tabs.addTab(self.conversion_tab, "Conversie")
        self.tabs.addTab(self.filter_tab, "Filtre")
        self.tabs.addTab(self.resize_tab, "Redimensionare")
        self.tabs.addTab(self.crop_tab, "Tăiere")

        # Inițializează fiecare tab
        self.init_conversion_ui()
        self.init_filter_ui()
        self.init_resize_ui()
        self.init_crop_ui()

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # Buton Undo
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        layout.addWidget(self.undo_button)

        self.setLayout(layout)

    def init_conversion_ui(self):
        layout = QVBoxLayout()

        self.input_button = QPushButton("Alege imaginea de intrare")
        self.input_button.clicked.connect(self.select_input_image)
        layout.addWidget(self.input_button)

        self.input_label = QLabel("Nicio imagine selectată")
        layout.addWidget(self.input_label)

        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["png", "jpg", "jpeg", "tiff", "webp", "bmp"])
        layout.addWidget(self.format_combobox)

        self.compression_combobox = QComboBox()
        self.compression_combobox.addItems(["lossless", "lossy"])
        layout.addWidget(self.compression_combobox)

        self.output_button = QPushButton("Alege directorul de ieșire")
        self.output_button.clicked.connect(self.select_output_directory)
        layout.addWidget(self.output_button)

        self.output_label = QLabel("Niciun director selectat")
        layout.addWidget(self.output_label)

        self.convert_button = QPushButton("Conversie")
        self.convert_button.clicked.connect(self.convert_image)
        layout.addWidget(self.convert_button)

        self.conversion_tab.setLayout(layout)

    def init_filter_ui(self):
        layout = QVBoxLayout()

        self.filter_combobox = QComboBox()
        self.filter_combobox.addItems(["Niciunul", "Alb-negru", "Sepia", "Estompare", "Claritate", "Invertire", "Contrast", "Saturare"])
        layout.addWidget(self.filter_combobox)

        self.apply_filter_button = QPushButton("Aplică filtru")
        self.apply_filter_button.clicked.connect(self.apply_filter_to_image)
        layout.addWidget(self.apply_filter_button)

        self.filter_tab.setLayout(layout)

    def init_resize_ui(self):
        layout = QVBoxLayout()

        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Lățime (px)")
        layout.addWidget(self.width_input)

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Înălțime (px)")
        layout.addWidget(self.height_input)

        self.resize_button = QPushButton("Aplică redimensionare")
        self.resize_button.clicked.connect(self.resize_image)
        layout.addWidget(self.resize_button)

        self.resize_tab.setLayout(layout)

    def init_crop_ui(self):
        layout = QVBoxLayout()

        self.crop_combobox = QComboBox()
        self.crop_combobox.addItems(["Niciunul", "Cerc", "Pătrat", "Triunghi", "Dreptunghi"])
        layout.addWidget(self.crop_combobox)

        self.crop_button = QPushButton("Aplică tăiere")
        self.crop_button.clicked.connect(self.apply_crop_to_image)
        layout.addWidget(self.crop_button)

        self.crop_tab.setLayout(layout)

    def select_input_image(self):
        options = QFileDialog.Options()
        self.input_path, _ = QFileDialog.getOpenFileName(self, "Alege imaginea de intrare", "", "Imagini (*.jpg *.jpeg *.png *.bmp *.tiff *.webp)", options=options)
        if self.input_path:
            self.input_label.setText(self.input_path)
            self.current_image = Image.open(self.input_path).convert("RGB")
            self.history.clear()  # resetăm istoricul când alegem o imagine nouă
            self.display_image()

    def select_output_directory(self):
        options = QFileDialog.Options()
        self.output_path = QFileDialog.getExistingDirectory(self, "Alege directorul de ieșire", options=options)
        if self.output_path:
            self.output_label.setText(self.output_path)

    def display_image(self):
        if self.current_image:
            data = io.BytesIO()
            self.current_image.save(data, format='PNG')
            data.seek(0)
            qt_img = QImage.fromData(data.read())
            pixmap = QPixmap.fromImage(qt_img)
            scaled_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)
            self.image_label.setPixmap(scaled_pixmap)

    def convert_image(self):
        if not self.current_image or not self.output_path:
            QMessageBox.critical(self, "Eroare", "Te rog să selectezi imaginea și directorul de ieșire.")
            return

        output_format = self.format_combobox.currentText()
        compression_type = self.compression_combobox.currentText()
        output_file = os.path.join(self.output_path, f"imagine_convertita.{output_format}")

        try:
            img = self.current_image

            if compression_type == "lossless":
                if output_format == 'png':
                    img.save(output_file, format='PNG', optimize=True)
                elif output_format == 'tiff':
                    img.save(output_file, format='TIFF', compression='tiff_lzw')
                else:
                    raise Exception("Compresie lossless nu suportată pentru acest format.")
            else:
                if output_format in ['jpg', 'jpeg']:
                    img.save(output_file, format='JPEG', quality=85, optimize=True)
                elif output_format == 'webp':
                    img.save(output_file, format='WEBP', quality=85, lossless=False)
                else:
                    raise Exception("Compresie lossy nu suportată pentru acest format.")

            QMessageBox.information(self, "Succes", f"Imaginea a fost convertită: {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))

    def apply_filter_to_image(self):
        if not self.current_image:
            QMessageBox.critical(self, "Eroare", "Nicio imagine încărcată.")
            return

        filter_type = self.filter_combobox.currentText()
        self.save_history()
        self.current_image = self.apply_filter(self.current_image, filter_type)
        self.display_image()

    def apply_filter(self, img, filter_type):
        if filter_type == "Alb-negru":
            return img.convert("L").convert("RGB")
        elif filter_type == "Sepia":
            width, height = img.size
            pixels = img.load()
            for py in range(height):
                for px in range(width):
                    r, g, b = img.getpixel((px, py))
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[px, py] = (min(255, tr), min(255, tg), min(255, tb))
            return img
        elif filter_type == "Estompare":
            return img.filter(ImageFilter.BLUR)
        elif filter_type == "Claritate":
            return img.filter(ImageFilter.SHARPEN)
        elif filter_type == "Invertire":
            return ImageOps.invert(img)
        elif filter_type == "Contrast":
            enhancer = ImageEnhance.Contrast(img)
            return enhancer.enhance(2)
        elif filter_type == "Saturare":
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.5)
        else:
            return img

    def resize_image(self):
        if not self.current_image:
            QMessageBox.critical(self, "Eroare", "Nicio imagine încărcată.")
            return

        try:
            new_width = int(self.width_input.text()) if self.width_input.text() else self.current_image.width
            new_height = int(self.height_input.text()) if self.height_input.text() else self.current_image.height

            self.save_history()
            self.current_image = self.current_image.resize((new_width, new_height))
            self.display_image()
        except Exception as e:
            QMessageBox.critical(self, "Eroare", str(e))

    def apply_crop_to_image(self):
        if not self.current_image:
            QMessageBox.critical(self, "Eroare", "Nicio imagine încărcată.")
            return

        crop_shape = self.crop_combobox.currentText()
        self.save_history()
        self.current_image = self.crop_image(self.current_image, crop_shape)
        self.display_image()

    def crop_image(self, img, shape):
        width, height = img.size

        if shape == "Cerc":
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, width, height), fill=255)
            img.putalpha(mask)
            return img
        elif shape == "Pătrat":
            min_side = min(width, height)
            left = (width - min_side) // 2
            top = (height - min_side) // 2
            right = (width + min_side) // 2
            bottom = (height + min_side) // 2
            return img.crop((left, top, right, bottom))
        elif shape == "Triunghi":
            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            draw.polygon([(width // 2, 0), (0, height), (width, height)], fill=255)
            img.putalpha(mask)
            return img
        elif shape == "Dreptunghi":
            return img.crop((50, 50, width-50, height-50))
        else:
            return img

    def save_history(self):
        if self.current_image:
            self.history.append(self.current_image.copy())

    def undo(self):
        if self.history:
            self.current_image = self.history.pop()
            self.display_image()
        else:
            QMessageBox.information(self, "Undo", "Nu mai există acțiuni de anulat.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageConverterApp()
    window.show()
    sys.exit(app.exec_())

