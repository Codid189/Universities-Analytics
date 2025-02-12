import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkintermapview

class UniversiteMarocDashboard:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Dashboard des Universités Marocaines")
        self.root.geometry("1400x800")
        
        # Set the default theme to dark mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Définition des couleurs
        self.COLORS = {
        'primary': "#4e79a7",        # Bleu principal
        'primary_hover': "#3d5d80",  # Bleu plus foncé pour hover
        'secondary': "#59a14f",      # Vert pour les accents
        'background': "#ffffff",      # Blanc pour le fond
        'surface': "#f8f9fa",        # Gris très clair pour les surfaces
        'border': "#e9ecef",         # Gris clair pour les bordures
        'text': "#212529",           # Gris foncé pour le texte
        'text_secondary': "#6c757d"  # Gris moyen pour le texte secondaire
    }
        
        # Variables pour les métriques
        self.metric_vars = {
            'histo': tk.StringVar(),
            'pie': tk.StringVar(),
            'incline_histo': tk.StringVar()
        }
        
        # Variables pour la comparaison d'universités
        self.univ1_var = tk.StringVar()
        self.univ2_var = tk.StringVar()
        
        # Initialisation des menus (important de le faire avant setup_ui)
        self.univ1_menu = None
        self.univ2_menu = None
        self.files_listbox = None
        self.minimize_btn = None
        self.graphs_frame = None
        self.map_frame = None
        
        # Variable pour suivre le type de visualisation actuelle
        self.current_visualization_type = None
        
        # Variable pour la barre de statut
        self.status_var = tk.StringVar()
        self.status_var.set("Prêt")  # État initial
        
        # Données des universités
        self.universites = {
            "UIR": {"coords": (33.98391232876505, -6.72523400525739), "ville": "Rabat", "type": "Privé"},
            "UM5": {"coords": (33.98815786142078, -6.858587835447975), "ville": "Rabat", "type": "Public"},
            "UIC": {"coords": (33.49578639109119, -7.610392818271857), "ville": "Casablanca", "type": "Private"},
            "UH2C": {"coords": (33.593962759227985, -7.632103648958875), "ville": "Casablanca", "type": "Public"},
            "UAE": {"coords": (35.56211434165767, -5.364284885601487), "ville": "Tanger", "type": "Public"},
            "EMSI": {"coords": (35.770985107223154, -5.805145162333485), "ville": "Casablanca", "type": "Privé"}
        }
        
        # Stockage des DataFrames
        self.data_frames = {}
        
        # Configuration de l'interface
        self.setup_ui()

    def setup_ui(self):
        # Conteneur principal avec un padding uniforme
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Barre de menu horizontale en haut
        self.setup_horizontal_menu()

        # Frame pour le contenu principal avec une meilleure organisation
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Configuration du panel de visualisation amélioré
        self.setup_viz_panel()

    def setup_viz_panel(self):
        """Configure le panneau de visualisation principal"""
        # Container principal avec un design clair
        viz_container = ctk.CTkFrame(self.content_frame, fg_color="white")
        viz_container.pack(fill="both", expand=True)

        # Configuration du panneau de gauche (graphiques)
        left_panel = ctk.CTkFrame(viz_container, fg_color="white")
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Frame pour les graphiques
        self.graphs_frame = ctk.CTkFrame(left_panel, fg_color="white")
        self.graphs_frame.pack(fill="both", expand=True)

        # Configuration du panneau de droite (carte)
        right_panel = ctk.CTkFrame(viz_container, fg_color="white")
        right_panel.pack(side="right", fill="y", padx=10, pady=10)

        # Configuration de la carte avec dimensions fixes
        map_container = ctk.CTkFrame(
            right_panel,
            fg_color="white",
            width=400,
            height=500  # Augmenté la hauteur pour mieux voir la carte
        )
        map_container.pack(fill="both", expand=False)
        map_container.pack_propagate(False)

        # Titre de la carte
        map_title = ctk.CTkFrame(map_container, fg_color=self.COLORS['primary'], height=30)
        map_title.pack(fill="x")
        ctk.CTkLabel(
            map_title,
            text="🗺 Carte des Universités",
            text_color=self.COLORS['background']
        ).pack(pady=5)

        # Frame pour la carte avec une taille fixe
        self.map_frame = ctk.CTkFrame(map_container, fg_color="white")
        self.map_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configuration de la carte
        self.setup_map()

        # Créer les visualisations par défaut
        self.create_default_visualizations()

        # Configurer le redimensionnement
        viz_container.grid_columnconfigure(0, weight=3)
        viz_container.grid_columnconfigure(1, weight=1)

    def toggle_graphs(self):
        """Fonction pour minimiser/maximiser les graphiques"""
        if self.graphs_frame.winfo_viewable():
            self.graphs_frame.pack_forget()
            self.minimize_btn.configure(text="□")
        else:
            self.graphs_frame.pack(fill="both", expand=True)
            self.minimize_btn.configure(text="−")

    def setup_status_bar(self):
        """Configure la barre de statut"""
        status_frame = ctk.CTkFrame(self.root, height=25, fg_color="#2b2b2b")
        status_frame.pack(side="bottom", fill="x")
        
        status_label = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            anchor="w",
            text_color="#a0a0a0"
        )
        status_label.pack(side="left", padx=5)

    def setup_horizontal_menu(self):
        """Configure le menu horizontal avec un design moderne et cohérent"""
        # Frame pour le menu horizontal avec une hauteur fixe
        menu_frame = ctk.CTkFrame(
            self.main_container, 
            fg_color=self.COLORS['surface'],
            height=60
        )
        menu_frame.pack(fill="x", pady=(0, 10))
        menu_frame.pack_propagate(False)  # Empêche le redimensionnement automatique

        # Division en sections avec des largeurs fixes
        sections = {
            'import': ctk.CTkFrame(menu_frame, fg_color="transparent", width=200),
            'universities': ctk.CTkFrame(menu_frame, fg_color="transparent", width=320),
            'metrics': ctk.CTkFrame(menu_frame, fg_color="transparent", width=400),
            'actions': ctk.CTkFrame(menu_frame, fg_color="transparent", width=260)
        }

        # Configuration des sections avec pack_propagate(False) pour maintenir les dimensions
        for section in sections.values():
            section.pack(side="left", fill="y", padx=5, pady=5)
            section.pack_propagate(False)  # Maintient la taille fixe

        # Section Import avec style amélioré
        import_btn = ctk.CTkButton(
            sections['import'],
            text="📂 Import CSV",
            command=self.import_csv_files,
            height=35,
            width=100,
            fg_color=self.COLORS['primary'],
            hover_color=self.COLORS['primary_hover'],
            corner_radius=8
        )
        import_btn.pack(side="left", padx=5)

        # Liste des fichiers stylisée
        self.files_listbox = tk.Listbox(
            sections['import'],
            bg=self.COLORS['surface'],
            fg=self.COLORS['text'],
            selectmode=tk.MULTIPLE,
            height=1,
            width=10,
            borderwidth=1,
            relief="solid"
        )
        self.files_listbox.pack(side="left", fill="y", padx=5)

        # Section Universités
        for i, (var, label) in enumerate([
            (self.univ1_var, "Université 1"),
            (self.univ2_var, "Université 2")
        ]):
            menu = ctk.CTkOptionMenu(
                sections['universities'],
                variable=var,
                values=list(self.universites.keys()),
                dynamic_resizing=True,
                width=140,
                fg_color=self.COLORS['surface'],
                button_color=self.COLORS['primary'],
                button_hover_color=self.COLORS['primary_hover'],
                dropdown_fg_color=self.COLORS['background'],
                dropdown_hover_color=self.COLORS['surface'],
                dropdown_text_color=self.COLORS['text'],
                text_color=self.COLORS['text']
            )
            menu.pack(side="left", padx=5)

        # Section Métriques
        for metric_key in self.metric_vars.keys():
            metric_menu = ctk.CTkOptionMenu(
                sections['metrics'],
                variable=self.metric_vars[metric_key],
                values=[],
                width=120,
                fg_color=self.COLORS['surface'],
                button_color=self.COLORS['primary'],
                button_hover_color=self.COLORS['primary_hover'],
                dropdown_fg_color=self.COLORS['background'],
                dropdown_hover_color=self.COLORS['surface'],
                dropdown_text_color=self.COLORS['text'],
                text_color=self.COLORS['text']
            )
            metric_menu.pack(side="left", padx=5)
            setattr(self, f'metric_{metric_key}_menu', metric_menu)

        # Section Actions avec position fixe
        actions_container = ctk.CTkFrame(sections['actions'], fg_color="transparent")
        actions_container.pack(fill="both", expand=True)

        # Boutons d'action avec tailles fixes
        for text, command, icon in [
            ("Visualiser", self.visualiser_universite, "👁"),
            ("Comparer", self.comparer_universites, "⚖")
        ]:
            action_btn = ctk.CTkButton(
                actions_container,
                text=f"{icon} {text}",
                command=command,
                width=120,
                height=35,
                fg_color=self.COLORS['primary'],
                hover_color=self.COLORS['primary_hover'],
                corner_radius=8
            )
            action_btn.pack(side="left", padx=5)

    def setup_import_section(self, parent_frame):
        import_frame = ctk.CTkFrame(parent_frame, fg_color="#1e1e1e", corner_radius=8)
        import_frame.pack(fill="x", padx=10, pady=5)

        # En-tête de la section
        header_frame = ctk.CTkFrame(import_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text="Import des données",
            font=("Helvetica", 14, "bold"),
            text_color="#000000"
        ).pack(side="left")

        # Bouton d'import moderne
        import_button = ctk.CTkButton(
            import_frame,
            text="Importer CSV",
            command=self.import_csv_files,
            height=35,
            fg_color="#3a7ebf",
            hover_color="#2b5f8f",
            corner_radius=6
        )
        import_button.pack(padx=10, pady=(5, 10), fill="x")

        # Liste des fichiers avec style moderne
        files_frame = ctk.CTkFrame(import_frame, fg_color="#2b2b2b")
        files_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.files_listbox = tk.Listbox(
            files_frame,
            bg="#2b2b2b",
            fg="#ffffff",
            selectmode=tk.MULTIPLE,
            height=6,
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#3a7ebf",
            selectforeground="#ffffff"
        )
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_listbox.yview)
        
        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.files_listbox.config(yscrollcommand=scrollbar.set)

    def setup_university_selection(self, parent_frame):
        univ_frame = ctk.CTkFrame(parent_frame, fg_color="#1e1e1e", corner_radius=8)
        univ_frame.pack(fill="x", padx=10, pady=5)

        # En-tête
        ctk.CTkLabel(
            univ_frame,
            text="Sélection des universités",
            font=("Helvetica", 14, "bold"),
            text_color="#ffffff"
        ).pack(pady=10, padx=15, anchor="w")

        # Université 1
        univ1_container = ctk.CTkFrame(univ_frame, fg_color="transparent")
        univ1_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            univ1_container,
            text="Université 1:",
            text_color="#a0a0a0",
            anchor="w"
        ).pack(fill="x", padx=5)
        
        self.univ1_menu = ctk.CTkOptionMenu(
            univ1_container,
            variable=self.univ1_var,
            values=list(self.universites.keys()),
            dynamic_resizing=True,
            fg_color="#2b2b2b",
            button_color="#3a7ebf",
            button_hover_color="#2b5f8f",
            dropdown_fg_color="#2b2b2b",
            dropdown_hover_color="#3a7ebf",
            command=lambda _: self.update_map_for_university(self.univ1_var)
        )
        self.univ1_menu.pack(fill="x", padx=5, pady=(0, 5))

        # Université 2
        univ2_container = ctk.CTkFrame(univ_frame, fg_color="transparent")
        univ2_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            univ2_container,
            text="Université 2:",
            text_color="#a0a0a0",
            anchor="w"
        ).pack(fill="x", padx=5)
        
        self.univ2_menu = ctk.CTkOptionMenu(
            univ2_container,
            variable=self.univ2_var,
            values=list(self.universites.keys()),
            dynamic_resizing=True,
            fg_color="#2b2b2b",
            button_color="#3a7ebf",
            button_hover_color="#2b5f8f",
            dropdown_fg_color="#2b2b2b",
            dropdown_hover_color="#3a7ebf",
            command=lambda _: self.update_map_for_university(self.univ2_var)
        )
        self.univ2_menu.pack(fill="x", padx=5, pady=(0, 5))

    def setup_metrics_section(self, parent_frame):
        metrics_frame = ctk.CTkFrame(parent_frame, fg_color="#1e1e1e", corner_radius=8)
        metrics_frame.pack(fill="x", padx=10, pady=5)

        # En-tête
        ctk.CTkLabel(
            metrics_frame,
            text="Sélection des métriques",
            font=("Helvetica", 14, "bold"),
            text_color="#ffffff"
        ).pack(pady=10, padx=15, anchor="w")

        # Configuration des métriques
        graph_types = {
            'histo': 'Histogramme',
            'pie': 'Camembert',
            'incline_histo': 'Histogramme Incliné'
        }

        for metric_key, graph_name in graph_types.items():
            metric_container = ctk.CTkFrame(metrics_frame, fg_color="transparent")
            metric_container.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                metric_container,
                text=f"Métrique pour {graph_name}:",
                text_color="#a0a0a0",
                anchor="w"
            ).pack(fill="x", padx=5)
            
            metric_menu = ctk.CTkOptionMenu(
                metric_container,
                variable=self.metric_vars[metric_key],
                values=[],
                dynamic_resizing=True,
                fg_color="#2b2b2b",
                button_color="#3a7ebf",
                button_hover_color="#2b5f8f",
                dropdown_fg_color="#2b2b2b",
                dropdown_hover_color="#3a7ebf"
            )
            metric_menu.pack(fill="x", padx=5, pady=(0, 5))
            setattr(self, f'metric_{metric_key}_menu', metric_menu)

        # Boutons d'action
        buttons_frame = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            buttons_frame,
            text="Visualiser une université",
            command=self.visualiser_universite,
            height=35,
            fg_color="#3a7ebf",
            hover_color="#2b5f8f",
            corner_radius=6
        ).pack(pady=(0, 5), fill="x")

        ctk.CTkButton(
            buttons_frame,
            text="Comparer deux universités",
            command=self.comparer_universites,
            height=35,
            fg_color="#3a7ebf",
            hover_color="#2b5f8f",
            corner_radius=6
        ).pack(fill="x")

    def setup_map(self):
        """Configure la carte avec les marqueurs des universités"""
        try:
            # Créer le widget de carte avec une taille plus grande
            self.map_widget = tkintermapview.TkinterMapView(
                self.map_frame,
                corner_radius=0,
                width=800,  # Augmentation de la taille
                height=600  # Augmentation de la taille
            )
            self.map_widget.pack(fill="both", expand=True, padx=5, pady=5)

            # Centrer la carte sur le Maroc avec un meilleur zoom
            self.map_widget.set_position(31.7917, -7.0926)  # Ajustement des coordonnées
            self.map_widget.set_zoom(6)  # Ajustement du zoom

            # Données supplémentaires pour les universités avec coordonnées corrigées
            self.university_data = {
                "UIR": {
                    "coords": (33.98391232876505, -6.72523400525739),
                    "ville": "Rabat",
                    "type": "Privé",
                    "etudiants": "5000+",
                    "specialites": "Management, Ingénierie, Médecine",
                    "annee_creation": "2010"
                },
                "UM5": {
                    "coords": (33.98815786142078, -6.858587835447975),  # Coordonnées ajustées
                    "ville": "Rabat",
                    "type": "Public",
                    "etudiants": "60000+",
                    "specialites": "Droit, Sciences, Lettres",
                    "annee_creation": "1957"
                },
                "UIC": {
                    "coords": (33.49578639109119, -7.610392818271857),
                    "ville": "Casablanca",
                    "type": "Privé",
                    "etudiants": "3000+",
                    "specialites": "Business, Ingénierie",
                    "annee_creation": "2010"
                },
                "UH2C": {
                    "coords": (33.593962759227985, -7.632103648958875),
                    "ville": "Casablanca",
                    "type": "Public",
                    "etudiants": "100000+",
                    "specialites": "Sciences, Médecine, Technologie",
                    "annee_creation": "1975"
                },
                "UAE": {
                    "coords": (35.56211434165767, -5.364284885601487),
                    "ville": "Tanger",
                    "type": "Public",
                    "etudiants": "40000+",
                    "specialites": "Sciences, Technologie, Commerce",
                    "annee_creation": "1974"
                },
                "EMSI": {
                    "coords": (35.770985107223154, -5.805145162333485),  # Coordonnées ajustées
                    "ville": "Casablanca",
                    "type": "Privé",
                    "etudiants": "4000+",
                    "specialites": "Informatique, Réseaux, Management",
                    "annee_creation": "1986"
                }
            }

            # Style de carte personnalisé
            self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", 
                                        max_zoom=22)

            # Ajouter des marqueurs pour toutes les universités
            self.markers = {}
            self.hover_window = None

            def show_university_info(name, data):
                # Fermer la fenêtre précédente si elle existe
                if hasattr(self, 'info_window') and self.info_window:
                    self.info_window.destroy()
                
                # Créer la nouvelle fenêtre d'info
                self.info_window = ctk.CTkToplevel(self.root)
                self.info_window.title(name)
                self.info_window.geometry("300x400")
                
                # Style amélioré
                frame = ctk.CTkFrame(self.info_window)
                frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # En-tête avec le nom de l'université
                header = ctk.CTkFrame(frame, fg_color="#3a7ebf", corner_radius=10)
                header.pack(fill="x", padx=5, pady=(5,10))
                ctk.CTkLabel(
                    header,
                    text=f"🏛️ {name}",
                    font=("Helvetica", 16, "bold"),
                    text_color="white"
                ).pack(pady=5)
                
                # Informations détaillées
                info_text = f"""
                📍 Ville: {data['ville']}
                🎓 Type: {data['type']}
                👥 Étudiants: {data['etudiants']}
                📚 Spécialités: {data['specialites']}
                📅 Création: {data['annee_creation']}
                """
                
                ctk.CTkLabel(
                    frame,
                    text=info_text,
                    font=("Helvetica", 12),
                    justify="left",
                    anchor="w"
                ).pack(fill="x", padx=10, pady=10)
                
                # Centrer la fenêtre
                self.info_window.update_idletasks()
                width = self.info_window.winfo_width()
                height = self.info_window.winfo_height()
                x = (self.info_window.winfo_screenwidth() // 2) - (width // 2)
                y = (self.info_window.winfo_screenheight() // 2) - (height // 2)
                self.info_window.geometry(f'+{x}+{y}')
                
                # Rendre la fenêtre modale
                self.info_window.transient(self.root)
                self.info_window.grab_set()
            
            for univ_name, details in self.university_data.items():
                lat, lon = details["coords"]
                
                # Créer le marqueur
                marker = self.map_widget.set_marker(
                    lat, lon,
                    text=univ_name,
                    text_color="#000000",
                    marker_color_circle="#3a7ebf",
                    marker_color_outside="#8B0000",
                    font=("Helvetica", 12, "bold"),
                    command=lambda name=univ_name, data=details: show_university_info(name, data)
                )
                
                self.markers[univ_name] = marker

            # Ajouter les contrôles de la carte
            controls_frame = ctk.CTkFrame(self.map_frame, fg_color="transparent")
            controls_frame.pack(side="right", padx=5, pady=5)

            # Boutons de zoom avec style amélioré
            ctk.CTkButton(
                controls_frame,
                text="🔍+",
                width=40,
                height=40,
                fg_color="#3a7ebf",
                hover_color="#8B0000",
                command=lambda: self.map_widget.set_zoom(self.map_widget.get_zoom() + 1)
            ).pack(pady=2)

            ctk.CTkButton(
                controls_frame,
                text="🔍-",
                width=40,
                height=40,
                fg_color="#3a7ebf",
                hover_color="#8B0000",
                command=lambda: self.map_widget.set_zoom(self.map_widget.get_zoom() - 1)
            ).pack(pady=2)

            # Bouton de recentrage
            ctk.CTkButton(
                controls_frame,
                text="🎯",
                width=40,
                height=40,
                fg_color="#3a7ebf",
                hover_color="#8B0000",
                command=lambda: self.map_widget.set_position(31.7917, -7.0926)
            ).pack(pady=2)

            # Sélecteur de style de carte
            styles = {
                "Standard": "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
                "Satellite": "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga",
                "Terrain": "https://mt0.google.com/vt/lyrs=p&hl=en&x={x}&y={y}&z={z}&s=Ga"
            }
            
            style_var = tk.StringVar(value="Standard")
            style_menu = ctk.CTkOptionMenu(
                self.map_frame,
                values=list(styles.keys()),
                variable=style_var,
                fg_color="#3a7ebf",
                button_color="#8B0000",
                command=lambda x: self.map_widget.set_tile_server(styles[x])
            )
            style_menu.pack(side="top", padx=5, pady=5)

            self.update_status("Carte initialisée avec succès")
            
        except Exception as e:
            self.update_status(f"Erreur lors de l'initialisation de la carte: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de l'initialisation de la carte: {str(e)}")

    def create_default_visualizations(self):
        """Crée des visualisations par défaut avec les données du CSV"""
        plt.close('all')
        
        # Configuration du style
        plt.style.use('classic')
        
        # Charger les données
        data = pd.DataFrame({
            'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
            'taux_d_emploi': [0.847, 0.854, 0.845, 0.837, 0.823, 0.818, 0.811, 0.822, 0.812, 0.809],
            'nombre_etudiants': [296685, 312435, 335282, 347433, 366977, 383384, 401420, 412850, 432888, 448385],
            'taux_de_reussite': [0.900, 0.901, 0.900, 0.908, 0.901, 0.906, 0.909, 0.913, 0.922, 0.912],
            'nombre_de_recherches': [2540, 2971, 3522, 4033, 5116, 5501, 6095, 5643, 6102, 7002]
        })
        
        # Créer une figure avec 4 sous-graphiques
        fig = plt.figure(figsize=(12, 8), dpi=100, facecolor='white')
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # 1. Évolution du nombre de recherches (graphique temporel)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(data['Year'], data['nombre_de_recherches'], 'o-', color='#4e79a7', linewidth=2)
        
        for x, y in zip(data['Year'], data['nombre_de_recherches']):
            ax1.scatter(x, y, color='#4e79a7', s=50)
            ax1.annotate(f'{y}', 
                        (x, y),
                        textcoords="offset points",
                        xytext=(0,10),
                        ha='center')
        
        ax1.set_title('Évolution du nombre de recherches', pad=20)
        ax1.set_ylabel('Nombre de recherches')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # 2. Taux d'emploi (diagramme en bâtons)
        ax2 = fig.add_subplot(gs[0, 1])
        derniers_taux = data['taux_d_emploi'].tail(5) * 100
        dernieres_annees = data['Year'].tail(5)
        bars = ax2.bar(dernieres_annees, derniers_taux, color='#59a14f')
        
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')
        
        ax2.set_title('Taux d\'emploi (5 dernières années)', pad=20)
        ax2.set_ylabel('Taux d\'emploi (%)')
        ax2.grid(True, axis='y', linestyle='--', alpha=0.7)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_ylim(75, 90)

        # 3. Taux de réussite (diagramme circulaire)
        ax3 = fig.add_subplot(gs[1, 0])
        derniere_annee = data.iloc[-1]
        taux = {
            'Réussite': derniere_annee['taux_de_reussite'] * 100,
            'Échec': 100 - (derniere_annee['taux_de_reussite'] * 100)
        }
        
        colors = ['#4e79a7', '#ff9896']
        explode = (0.1, 0)
        
        wedges, texts, autotexts = ax3.pie(taux.values(), 
                                        explode=explode,
                                        labels=taux.keys(),
                                        colors=colors,
                                        autopct='%1.1f%%',
                                        shadow=True,
                                        startangle=90)
        
        ax3.set_title('Taux de réussite en 2024', pad=20)

        # 4. Nombre d'étudiants (diagramme horizontal)
        ax4 = fig.add_subplot(gs[1, 1])
        dernieres_5_annees = data['Year'].tail(5)
        derniers_nombres = data['nombre_etudiants'].tail(5)
        
        # Utiliser la couleur orange pour les barres
        bars = ax4.barh(range(len(dernieres_5_annees)), derniers_nombres, color='#ff7f0e')
        
        # Ajouter les étiquettes à droite des barres avec une meilleure disposition
        for i, (value, year) in enumerate(zip(derniers_nombres, dernieres_5_annees)):
            ax4.text(value + 1000, i, f'{value:,}', 
                    va='center', ha='left', fontsize=8)
            # Ajouter l'année à gauche des barres
            ax4.text(-10000, i, str(year), 
                    va='center', ha='right', fontsize=8)
        
        ax4.set_title('Nombre d\'étudiants (5 dernières années)', pad=20)
        ax4.set_yticks([])  # Cacher les étiquettes de l'axe y
        
        # Rotation des étiquettes de l'axe x pour éviter le chevauchement
        ax4.tick_params(axis='x', rotation=45)
        
        # Formatter les nombres sur l'axe x avec des séparateurs de milliers
        ax4.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        ax4.grid(True, axis='x', linestyle='--', alpha=0.7)
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        
        # Ajuster les marges pour les étiquettes rotées
        plt.setp(ax4.get_xticklabels(), ha='right')

        # Ajuster la mise en page
        plt.tight_layout(pad=3.0)

        # Créer le canvas Matplotlib
        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        
        # Configurer le widget canvas
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.configure(bg='white')
        canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Configurer le redimensionnement
        self.graphs_frame.grid_columnconfigure(0, weight=1)
        self.graphs_frame.grid_rowconfigure(0, weight=1)

        # Ajouter la barre d'outils de navigation
        toolbar_frame = ctk.CTkFrame(self.graphs_frame, fg_color="white")
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

    def setup_import_section(self):
        import_frame = ctk.CTkFrame(self.control_frame)
        import_frame.pack(fill="x", padx=10, pady=5)

        # Titre de la section
        ctk.CTkLabel(
            import_frame,
            text="Import des données",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        # Bouton d'import
        import_button = ctk.CTkButton(
            import_frame,
            text="Importer CSV",
            command=self.import_csv_files,
            height=35
        )
        import_button.pack(pady=10, fill="x")

        # Liste des fichiers avec scrollbar
        self.files_listbox = tk.Listbox(
            import_frame,
            bg="#2b2b2b",
            fg="white",
            selectmode=tk.MULTIPLE,
            height=6
        )
        scrollbar = tk.Scrollbar(import_frame)
        
        self.files_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)

    def setup_metrics_section(self):
        metrics_frame = ctk.CTkFrame(self.control_frame)
        metrics_frame.pack(fill="x", padx=10, pady=5)

        # Titre de la section
        ctk.CTkLabel(
            metrics_frame,
            text="Sélection des métriques",
            font=("Helvetica", 14, "bold")
        ).pack(pady=5)

        # Création des menus pour chaque type de graphique
        graph_types = {
            'histo': 'Histogramme',
            'pie': 'Camembert',
            'incline_histo': 'Histogramme Incliné'  # New graph type
        }

        for metric_key, graph_name in graph_types.items():
            ctk.CTkLabel(
                metrics_frame,
                text=f"Métrique pour {graph_name}:",
                anchor="w"
            ).pack(fill="x", padx=5, pady=2)
            
            metric_menu = ctk.CTkOptionMenu(
                metrics_frame,
                variable=self.metric_vars[metric_key],
                values=[],
                dynamic_resizing=True
            )
            metric_menu.pack(fill="x", padx=5, pady=2)
            setattr(self, f'metric_{metric_key}_menu', metric_menu)

        # Boutons d'action
        ctk.CTkButton(
            metrics_frame,
            text="Visualiser une université",
            command=self.visualiser_universite,
            height=35
        ).pack(pady=5, fill="x")

        ctk.CTkButton(
            metrics_frame,
            text="Comparer deux universités",
            command=self.comparer_universites,
            height=35
        ).pack(pady=5, fill="x")


    def import_csv_files(self):
        """Importe les fichiers CSV sélectionnés"""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers CSV",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if not files:
            return

        success_count = 0
        for file_path in files:
            file_name = file_path.split("/")[-1]
            
            if file_name in self.data_frames:
                continue
            
            try:
                # Read the CSV file
                df = pd.read_csv(file_path)
                
                # Clean numeric columns
                for column in df.select_dtypes(include=['object']).columns:
                    try:
                        # Remove underscores and 'millions' from values
                        df[column] = df[column].replace('_', '', regex=True)
                        df[column] = df[column].str.replace('millions', '', regex=False)
                        # Try to convert to numeric, if fails keep as is
                        df[column] = pd.to_numeric(df[column], errors='ignore')
                    except:
                        continue
                
                # Vérifier les colonnes requises
                required_columns = ['universite', 'filiere']
                if not all(col in df.columns for col in required_columns):
                    messagebox.showwarning(
                        "Format incorrect",
                        f"Le fichier {file_name} doit contenir les colonnes: {', '.join(required_columns)}"
                    )
                    continue

                self.data_frames[file_name] = df
                self.files_listbox.insert(tk.END, file_name)
                success_count += 1
                
            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"Erreur lors de l'importation de {file_name}: {str(e)}"
                )

        if success_count > 0:
            # Mettre à jour les menus avec les nouvelles données
            self.update_menus()
            messagebox.showinfo(
                "Succès",
                f"{success_count} fichier(s) importé(s) avec succès!"
            )
            self.update_status("Fichiers CSV importés avec succès")

    def update_menus(self):
        """Met à jour les menus déroulants avec les données disponibles"""
        if not self.data_frames:
            return

        # Récupérer le premier DataFrame pour les colonnes numériques
        first_df = next(iter(self.data_frames.values()))
        
        # Obtenir toutes les colonnes numériques sauf 'universite' et 'filiere'
        numeric_columns = first_df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_columns = [col for col in numeric_columns if col not in ['universite', 'filiere']]
        
        # Obtenir toutes les universités
        all_universities = set()
        for df in self.data_frames.values():
            all_universities.update(df['universite'].unique())
        universities = sorted(list(all_universities))

        # Mise à jour des menus des universités
        if hasattr(self, 'univ1_menu') and self.univ1_menu:
            self.univ1_menu.configure(values=universities)
        if hasattr(self, 'univ2_menu') and self.univ2_menu:
            self.univ2_menu.configure(values=universities)

        # Mise à jour des menus des métriques
        for metric_key in ['histo', 'pie', 'incline_histo']:
            menu_name = f'metric_{metric_key}_menu'
            if hasattr(self, menu_name):
                menu = getattr(self, menu_name)
                if menu:
                    menu.configure(values=numeric_columns)
                    # Définir une valeur par défaut si aucune n'est sélectionnée
                    if not self.metric_vars[metric_key].get() and numeric_columns:
                        self.metric_vars[metric_key].set(numeric_columns[0])

        self.update_status(f"Menus mis à jour avec {len(numeric_columns)} métriques disponibles")
    def toggle_theme(self):
            """Switch entre thème clair et sombre"""
            if ctk.get_appearance_mode() == "Dark":
                ctk.set_appearance_mode("Light")
                plt.style.use('default')
            else:
                ctk.set_appearance_mode("Dark")
                plt.style.use('dark_background')
            
            self.update_current_visualization()
            self.update_status("Thème changé")

    def update_current_visualization(self):
        """Met à jour les graphiques avec le nouveau thème"""
        if hasattr(self, 'current_visualization_type'):
            if self.current_visualization_type == 'single':
                self.visualiser_universite()
            elif self.current_visualization_type == 'comparison':
                self.comparer_universites()

    def visualiser_universite(self):
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Attention", 
                                 "Veuillez sélectionner un fichier à analyser.")
            return

        univ = self.univ1_var.get()
        metrics = {key: var.get() for key, var in self.metric_vars.items()}

        if not all(metrics.values()):
            messagebox.showwarning("Attention", 
                                 "Veuillez sélectionner toutes les métriques.")
            return

        if not univ:
            messagebox.showwarning("Attention", 
                                 "Veuillez sélectionner une université.")
            return

        combined_df = pd.DataFrame()
        for index in selected_indices:
            selected_file = self.files_listbox.get(index)
            df = self.data_frames[selected_file]
            combined_df = pd.concat([combined_df, df])

        df_univ = combined_df[combined_df['universite'] == univ]

        if df_univ.empty:
            messagebox.showwarning("Attention", 
                                 "Aucune donnée trouvée pour l'université sélectionnée.")
            return

        try:
            self.current_visualization_type = 'single'
            self.create_single_university_visualization(df_univ, univ, metrics)
        except Exception as e:
            messagebox.showerror("Erreur", 
                               f"Erreur lors de la création des visualisations: {str(e)}")
        self.update_status(f"Visualisation pour {univ} créée")

    def create_single_university_visualization(self, df, univ, metrics):
        plt.close('all')
        
        # Faire une copie des données et convertir en numérique
        df = df.copy()
        for col in metrics.values():
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Définir les couleurs cohérentes
        colors = {
            'bar1': '#4e79a7',        # Bleu
            'bar2': '#f28e2c',        # Orange
            'pie_colors': ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949']  # Palette cohérente
        }
        
        # Créer une figure plus grande avec plus d'espace
        fig = plt.figure(figsize=(15, 10), dpi=100)
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # Nettoyer le frame des graphiques
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        # 1. Histogramme
        ax1 = fig.add_subplot(gs[0, 0])
        df_histo = df.groupby('filiere')[metrics['histo']].mean().fillna(0)
        
        x = np.arange(len(df_histo)) * 1.2
        width = 0.8
        
        bars = ax1.bar(x, df_histo.values, width, 
                    color=colors['bar1'], 
                    label=f"{metrics['histo']} - {univ}")
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}', 
                    ha='center', 
                    va='bottom',
                    fontsize=9)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_histo.index, rotation=45, ha='right', fontsize=9)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.margins(x=0.1)
        ax1.set_title(f'Distribution par filière - {metrics["histo"]}')

        # 2. Histogramme incliné
        ax2 = fig.add_subplot(gs[0, 1])
        df_incline = df.groupby('filiere')[metrics['incline_histo']].mean().fillna(0)
        
        y = np.arange(len(df_incline)) * 1.2
        height = 0.8
        
        bars = ax2.barh(y, df_incline.values, height, 
                        color=colors['bar2'], 
                        label=f"{metrics['incline_histo']} - {univ}")
        
        for bar in bars:
            width = bar.get_width()
            ax2.text(width + (max(df_incline.values) * 0.02),
                    bar.get_y() + bar.get_height()/2.,
                    f'{width:.2f}',
                    ha='left',
                    va='center',
                    fontsize=9)
        
        ax2.set_yticks(y)
        ax2.set_yticklabels(df_incline.index, fontsize=9)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.margins(x=0.2)
        ax2.set_title(f'Distribution horizontale - {metrics["incline_histo"]}')

        # 3. Camembert
        ax3 = fig.add_subplot(gs[1, :])
        df_pie = df.groupby('filiere')[metrics['pie']].mean().fillna(0)
        
        wedges, texts, autotexts = ax3.pie(df_pie.values, 
                                        labels=[''] * len(df_pie),
                                        autopct='%1.1f%%',
                                        pctdistance=0.75,
                                        explode=[0.05] * len(df_pie),
                                        colors=colors['pie_colors'][:len(df_pie)],
                                        textprops={'fontsize': 9})
        
        ax3.legend(wedges, df_pie.index,
                title=f"{metrics['pie']} - {univ}",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10)

        # Ajuster la mise en page avec plus d'espace pour la légende
        plt.tight_layout(pad=3.0, rect=[0, 0, 0.85, 1])

        # Créer le canvas Matplotlib et l'intégrer dans le frame des graphiques
        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        
        # Configurer le widget canvas
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Ajouter la barre d'outils de navigation
        toolbar_frame = ctk.CTkFrame(self.graphs_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()


    def comparer_universites(self):
        """Méthode pour gérer la comparaison entre deux universités"""
        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Attention", 
                                "Veuillez sélectionner un fichier à analyser.")
            return

        univ1 = self.univ1_var.get()
        univ2 = self.univ2_var.get()
        metrics = {key: var.get() for key, var in self.metric_vars.items()}

        # Vérifications
        if not univ1 or not univ2:
            messagebox.showwarning("Attention", 
                                "Veuillez sélectionner deux universités à comparer.")
            return

        if univ1 == univ2:
            messagebox.showwarning("Attention", 
                                "Veuillez sélectionner deux universités différentes.")
            return

        if not all(metrics.values()):
            messagebox.showwarning("Attention", 
                                "Veuillez sélectionner toutes les métriques.")
            return

        # Combiner les données des fichiers sélectionnés
        combined_df = pd.DataFrame()
        for index in selected_indices:
            selected_file = self.files_listbox.get(index)
            df = self.data_frames[selected_file]
            combined_df = pd.concat([combined_df, df])

        # Filtrer les données pour les universités sélectionnées
        df_comparison = combined_df[combined_df['universite'].isin([univ1, univ2])]

        if df_comparison.empty:
            messagebox.showwarning("Attention", 
                                "Aucune donnée trouvée pour les universités sélectionnées.")
            return

        try:
            self.current_visualization_type = 'comparison'
            self.create_comparison_visualizations(df_comparison, univ1, univ2, metrics)
            self.update_status(f"Comparaison créée entre {univ1} et {univ2}")
        except Exception as e:
            messagebox.showerror("Erreur", 
                            f"Erreur lors de la création des visualisations: {str(e)}")
            
    def create_comparison_visualizations(self, df, univ1, univ2, metrics):
        plt.close('all')
        
        # Définir les couleurs cohérentes
        colors = {
            'bar1': '#4e79a7',        # Bleu
            'bar2': '#f28e2c',        # Orange
            'pie_colors': ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949']  # Palette cohérente
        }
        
        # Créer une figure plus grande pour mieux accommoder les données
        fig = plt.figure(figsize=(15, 10), dpi=100)
        gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3)

        # Nettoyer le frame des graphiques
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()

        # Filtrer les données pour chaque université
        df1 = df[df['universite'] == univ1].copy()
        df2 = df[df['universite'] == univ2].copy()

        # Convertir les colonnes en nombres
        for col in metrics.values():
            df1[col] = pd.to_numeric(df1[col], errors='coerce')
            df2[col] = pd.to_numeric(df2[col], errors='coerce')

        # 1. Histogramme comparatif
        ax1 = fig.add_subplot(gs[0, 0])
        df1_histo = df1.groupby('filiere')[metrics['histo']].mean().fillna(0)
        df2_histo = df2.groupby('filiere')[metrics['histo']].mean().fillna(0)

        x = np.arange(len(df1_histo)) * 1.5
        width = 0.35

        bars1 = ax1.bar(x - width/2, df1_histo.values, width, 
                        label=f"{univ1} - {metrics['histo']}", 
                        color=colors['bar1'])
        bars2 = ax1.bar(x + width/2, df2_histo.values, width, 
                        label=f"{univ2} - {metrics['histo']}", 
                        color=colors['bar2'])

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.2f}', 
                        ha='center', 
                        va='bottom',
                        fontsize=9)

        ax1.set_xticks(x)
        ax1.set_xticklabels(df1_histo.index, rotation=45, ha='right', fontsize=9)
        ax1.legend(loc='upper right', fontsize=10)
        ax1.margins(x=0.1)
        ax1.set_title(f'Comparaison - {metrics["histo"]}')

        # 2. Histogramme incliné comparatif
        ax2 = fig.add_subplot(gs[0, 1])
        df1_incline = df1.groupby('filiere')[metrics['incline_histo']].mean().fillna(0)
        df2_incline = df2.groupby('filiere')[metrics['incline_histo']].mean().fillna(0)

        y = np.arange(len(df1_incline)) * 1.2
        height = 0.35

        bars1 = ax2.barh(y - height/2, df1_incline.values, height, 
                        label=f"{univ1} - {metrics['incline_histo']}", 
                        color=colors['bar1'])
        bars2 = ax2.barh(y + height/2, df2_incline.values, height, 
                        label=f"{univ2} - {metrics['incline_histo']}", 
                        color=colors['bar2'])

        max_value = max(df1_incline.values.max(), df2_incline.values.max())
        for bars in [bars1, bars2]:
            for bar in bars:
                width = bar.get_width()
                ax2.text(width + max_value * 0.02,
                        bar.get_y() + bar.get_height()/2.,
                        f'{width:.2f}',
                        ha='left',
                        va='center',
                        fontsize=9)

        ax2.set_yticks(y)
        ax2.set_yticklabels(df2_incline.index, fontsize=9)
        ax2.legend(loc='upper right', fontsize=10)
        ax2.margins(x=0.2)
        ax2.set_title(f'Comparaison horizontale - {metrics["incline_histo"]}')

        # 3. Double camembert
        ax3 = fig.add_subplot(gs[1, 0])
        df1_pie = df1.groupby('filiere')[metrics['pie']].mean().fillna(0)
        
        wedges1, texts1, autotexts1 = ax3.pie(df1_pie.values, 
                                            labels=[''] * len(df1_pie),
                                            autopct='%1.1f%%',
                                            pctdistance=0.75,
                                            explode=[0.05] * len(df1_pie),
                                            colors=colors['pie_colors'][:len(df1_pie)],
                                            textprops={'fontsize': 9})
        
        ax3.legend(wedges1, df1_pie.index,
                title=f"{metrics['pie']} - {univ1}",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10)
        ax3.set_title(f'Distribution pour {univ1}')

        ax4 = fig.add_subplot(gs[1, 1])
        df2_pie = df2.groupby('filiere')[metrics['pie']].mean().fillna(0)
        
        wedges2, texts2, autotexts2 = ax4.pie(df2_pie.values, 
                                            labels=[''] * len(df2_pie),
                                            autopct='%1.1f%%',
                                            pctdistance=0.75,
                                            explode=[0.05] * len(df2_pie),
                                            colors=colors['pie_colors'][:len(df2_pie)],
                                            textprops={'fontsize': 9})
        
        ax4.legend(wedges2, df2_pie.index,
                title=f"{metrics['pie']} - {univ2}",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                fontsize=10)
        ax4.set_title(f'Distribution pour {univ2}')

        # Ajuster la mise en page avec plus d'espace pour les légendes
        plt.tight_layout(pad=3.0, rect=[0, 0, 0.85, 1])

        # Créer le canvas Matplotlib et l'intégrer dans le frame des graphiques
        canvas = FigureCanvasTkAgg(fig, master=self.graphs_frame)
        canvas.draw()
        
        # Configurer le widget canvas
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Ajouter la barre d'outils de navigation
        toolbar_frame = ctk.CTkFrame(self.graphs_frame)
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

    def update_status(self, message):
        """Met à jour le message de la barre de statut"""
        self.status_var.set(message)

    def run(self):
        """Lance l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = UniversiteMarocDashboard()
        app.run()
    except Exception as e:
        print(f"Erreur lors du lancement de l'application: {e}")