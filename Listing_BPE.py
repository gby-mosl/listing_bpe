import os
import sys
import datetime
import locale
from fpdf import FPDF
from pathlib import Path
from tkinter import messagebox
import logging
from dataclasses import dataclass
from contextlib import contextmanager
from abc import ABC, abstractmethod

# Constants
LOCALE_SETTINGS = 'fr_FR.UTF-8'
DATE_FORMAT = '%Y-%m-%d'
EDITING_DATE_FORMAT = '%d %B %Y'
# LOGO_PATH = "C:/Users/{}/VINCI Energies/GO-OMEXOM BE-Divers BE - Documents/02-GABARITS - FONDS DE PLAN/#GENERIQUE/5- Logo/1- OMEXOM/OMEXOM_COULEURS.png"
LOGO_PATH = "/Users/guillaume/Desktop/OMEXOM/OMEXOM_COULEURS.png"
PDF_OUTPUT_TEMPLATE = 'Liste BPE - {}.pdf'

# Colors
BLUE_COLOR = (43, 113, 184)
LIGHT_BLUE_COLOR = (0, 191, 220)
YELLOW_COLOR = (252, 181, 32)
GRAY_BACKGROUND = (240, 240, 240)


def resource_path(relative_path):
    """Récupère le chemin absolu du fichier, compatible PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def output_dir():
    if getattr(sys, 'frozen', False):
        # Si exécutable PyInstaller, dossier de l'exécutable
        return Path(sys.executable).parent
    else:
        # Si script Python normal, dossier courant
        return  Path.cwd()

# Interface pour la gestion des messages utilisateur
class UIMessageHandler(ABC):
    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        pass

    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        pass

    @abstractmethod
    def ask_yes_no(self, title: str, message: str) -> bool:
        pass


# Implémentation avec tkinter
class TkMessageHandler(UIMessageHandler):
    def show_error(self, title: str, message: str) -> None:
        messagebox.showerror(title=title, message=message)

    def show_info(self, title: str, message: str) -> None:
        messagebox.showinfo(title=title, message=message)

    def ask_yes_no(self, title: str, message: str) -> bool:
        return messagebox.askyesno(title=title, message=message)


@dataclass
class PDFGenerationError(Exception):
    """Exception personnalisée pour la génération PDF."""
    message: str
    original_error: Exception = None


class PDFDocument(FPDF):
    """Classe pour la génération de documents PDF personnalisés."""

    def footer(self):
        """Ajoute un pied de page personnalisé avec des lignes colorées et numérotation."""
        self.set_y(-15)
        self._draw_footer_lines()
        self._add_page_number()

    def _draw_footer_lines(self):
        """Dessine les lignes colorées dans le pied de page."""
        pos_y = 280
        line_segments = [
            (0, 120, BLUE_COLOR),
            (120, 180, LIGHT_BLUE_COLOR),
            (180, 210, YELLOW_COLOR)
        ]
        self.set_line_width(1)
        for start, end, color in line_segments:
            self.set_draw_color(*color)
            self.line(x1=start, y1=pos_y, x2=end, y2=pos_y)

    def _add_page_number(self):
        """Ajoute la numérotation des pages au pied de page."""
        self.set_font('FreeSans', 'I', 11)
        self.cell(0, 10, f"Page {self.page_no()} sur {{nb}}", align="C")


class ProjectDocument:
    """Classe principale pour la gestion des documents du projet."""

    def __init__(self, ui_handler: UIMessageHandler = None):
        self.ui_handler = ui_handler or TkMessageHandler()
        self._initialize_project_paths()
        self._parse_project_name()
        self.categories = self._get_folders()

        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=output_dir() / f'info.log'
        )
        logging.getLogger("fontTools.subset").disabled = True
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def _pdf_context(self):
        """Gestionnaire de contexte pour les ressources PDF."""
        pdf = None
        try:
            pdf = self._create_pdf_document()
            yield pdf
        finally:
            if pdf:
                del pdf

    def _add_title_section(self, pdf):
        """Ajoute la section titre au document PDF."""
        current_date = datetime.datetime.now().strftime(EDITING_DATE_FORMAT)
        pdf.set_font('FreeSans', 'B', 20)
        pdf.set_text_color(43, 113, 184)
        pdf.line(x1=10, y1=41, x2=200, y2=41)
        pdf.cell(0, 10, "Liste des Plans BPE", align="C")
        pdf.ln(9)
        pdf.set_font('FreeSans', 'I', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Edition du {current_date}", align="C")
        pdf.line(x1=10, y1=63, x2=200, y2=63)
        pdf.ln(16)

    def _add_project_info(self, pdf):
        """Ajoute les informations du projet au document PDF."""
        pdf.set_font('FreeSans', 'B', 20)
        pdf.set_text_color(0, 0, 0)
        pdf.set_draw_color(43, 113, 184)
        pdf.cell(80)
        pdf.cell(30, 10, f"Poste de {self.name}")
        pdf.ln(13)
        pdf.cell(80)
        pdf.set_font('FreeSans', 'I', 12)
        pdf.cell(25, 0, "Affaire N° :")
        pdf.set_font('FreeSans', '', 14)
        pdf.cell(25, 0, self.number)
        pdf.ln(7)
        pdf.cell(80)
        pdf.set_font('FreeSans', 'I', 12)
        pdf.cell(26, 0, "Classement :")
        pdf.set_font('FreeSans', '', 14)
        pdf.cell(26, 0, self.rank)
        pdf.ln(13)

    def _add_categories_content(self, pdf):
        """Ajoute le contenu des catégories au PDF."""
        for category in self.categories:
            if not category.startswith('#'):
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font('FreeSans', 'B', 14)
                pdf.cell(0, 10, category, align="L", fill=True)
                folder = self.bpe_dir / category
                pdf.ln(13)
                list_bpe = []
                for f in folder.iterdir():
                    if f.suffix == '.pdf':
                        fullname = f.stem
                        sep_index = fullname.find('-')
                        last_index = fullname.rfind('-')
                        dispatch_index = fullname.rfind('(')
                        dispatch_index_end = fullname.rfind(')')
                        number = f.stem[:sep_index]
                        name = f.stem[sep_index + 1: dispatch_index - 1]
                        version = f.stem[last_index + 1:dispatch_index - 1]
                        dispatch_number = f.stem[dispatch_index + 1:dispatch_index_end]
                        list_bpe += ((number, version, name, dispatch_number),)

                with pdf.table(text_align=("CENTER", "CENTER", "LEFT", "CENTER"), col_widths=(1, 1, 7, 1)) as table:
                    pdf.set_fill_color(0, 0, 0)
                    pdf.set_font('FreeSans', '', 11)
                    sorted_list_bpe = sorted(list_bpe)
                    sorted_list_bpe.insert(0, ('N°', 'Ind.', 'Document', 'Envoi'))
                    for data_row in sorted_list_bpe:
                        row = table.row()
                        for datum in data_row:
                            row.cell(datum, border="TOP")
                pdf.ln(13)

    def generate_bpe_listing(self):
        """Génère le document PDF avec la liste BPE."""
        try:
            file_date = datetime.datetime.now().strftime(DATE_FORMAT)
            output_file = output_dir() / Path(PDF_OUTPUT_TEMPLATE.format(file_date))

            if output_file.exists() and not self.ui_handler.ask_yes_no(
                    "Fichier existant",
                    f"Le fichier {output_file} existe déjà. Voulez-vous le remplacer?"
            ):
                return

            with self._pdf_context() as pdf:
                self._add_header(pdf)
                self._add_categories_content(pdf)

                pdf.output(str(output_file))

            self.ui_handler.show_info(
                "Succès",
                f'Le fichier "{output_file}" a été généré.'
            )
            self.logger.info(f"Document PDF généré avec succès: {output_file.name}")

        except PDFGenerationError as e:
            self.logger.error(f"Erreur de génération PDF: {e.message}", exc_info=e.original_error)
            self._handle_error("Erreur lors de la génération du PDF", e)
        except Exception as e:
            self.logger.error("Erreur inattendue", exc_info=e)
            self._handle_error("Erreur inattendue", e)

    def _initialize_project_paths(self):
        exe_path = Path(sys.executable).resolve()
        self.root = exe_path.parents[3].absolute()
        self.bpe_dir = self.root / "Project Files" / "12-BPE"

    def _parse_project_name(self):
        fullname = self.root.name[6:]
        end_sep = fullname.rfind("-")
        self.rank = fullname[:3]
        self.name = fullname[4:end_sep]
        self.number = fullname[end_sep + 1:]

    def _get_folders(self):
        """Récupère la liste des dossiers avec gestion d'erreurs spécifiques."""
        try:
            if not self.bpe_dir.exists():
                raise FileNotFoundError(f"Le répertoire BPE n'existe pas: {self.bpe_dir}")
            return sorted([f.name for f in self.bpe_dir.iterdir() if f.is_dir()])
        except FileNotFoundError as e:
            self._handle_error("Erreur d'accès au répertoire", e)
            return []
        except PermissionError as e:
            self._handle_error("Erreur de permission", e)
            return []
        except Exception as e:
            self._handle_error("Erreur inattendue", e)
            return []

    def _create_pdf_document(self):
        pdf = PDFDocument(orientation='P', format='A4', unit='mm')
        pdf.add_page()
        font_path = resource_path("FreeSans.ttf")
        pdf.add_font('FreeSans', '', resource_path('FreeSans.ttf'), uni=True)
        pdf.add_font('FreeSans', 'B', resource_path('FreeSansBold.ttf'), uni=True)
        pdf.add_font('FreeSans', 'I', resource_path('FreeSansOblique.ttf'), uni=True)
        pdf.add_font('FreeSans', 'BI', resource_path('FreeSansBoldOblique.ttf'), uni=True)
        return pdf

    def _add_header(self, pdf):
        user = os.getlogin().lower()
        # pdf.image(LOGO_PATH.format(user), 8, 6, 60)
        pdf.image(LOGO_PATH, 8, 6, 60)
        self._add_project_info(pdf)
        self._add_title_section(pdf)


    def _handle_error(self, message: str, error: Exception) -> None:
        """Gestion améliorée des erreurs avec logging."""
        error_message = f"{message} : {type(error).__name__} - {str(error)}"
        self.logger.error(error_message, exc_info=error)
        self.ui_handler.show_error("Erreur", error_message)


if __name__ == "__main__":
    locale.setlocale(locale.LC_TIME, LOCALE_SETTINGS)
    project = ProjectDocument()
    project.generate_bpe_listing()