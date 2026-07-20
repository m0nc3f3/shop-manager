"""
StockFlow - Application de Gestion de Magasin
Gestion des produits, ventes et statistiques avec interface PyQt5.
"""

import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class StockFlow(QMainWindow):
    """Application principale de gestion de magasin."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StockFlow - Gestion de Magasin")
        self.setGeometry(100, 100, 1050, 720)

        # Connexion a la base de donnees
        self.conn = sqlite3.connect("stockflow.db")
        self.cursor = self.conn.cursor()
        self._init_database()

        # Construction de l'interface
        self._build_ui()
        self._load_products()
        self._load_sales()
        self._load_combos()

    # ----------------------------------------------------------------
    # BASE DE DONNEES
    # ----------------------------------------------------------------

    def _init_database(self):
        """Cree les tables si elles n'existent pas."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                category TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER,
                total REAL,
                date TEXT,
                customer TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        self.conn.commit()

    # ----------------------------------------------------------------
    # INTERFACE UTILISATEUR
    # ----------------------------------------------------------------

    def _build_ui(self):
        """Construit l'interface complete avec onglets."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Barre de titre
        title = QLabel("StockFlow - Gestion de Magasin")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1a237e; padding: 10px;")
        main_layout.addWidget(title)

        # Onglets
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #3f51b5; border-radius: 6px; }
            QTabBar::tab { padding: 10px 25px; font-size: 13px; font-weight: bold; }
            QTabBar::tab:selected { background: #3f51b5; color: white; }
            QTabBar::tab:!selected { background: #e8eaf6; color: #1a237e; }
        """)
        main_layout.addWidget(tabs)

        # Construire chaque onglet
        tabs.addTab(self._build_products_tab(), "Produits")
        tabs.addTab(self._build_sales_tab(), "Ventes")
        tabs.addTab(self._build_stats_tab(), "Statistiques")

    def _build_products_tab(self):
        """Onglet de gestion des produits."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # --- Formulaire d'ajout ---
        form_group = QGroupBox("Ajouter un produit")
        form_group.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #1a237e; font-size: 13px; 
                        border: 2px solid #c5cae9; border-radius: 8px; margin-top: 15px; padding-top: 20px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }
        """)
        layout.addWidget(form_group)

        form = QGridLayout(form_group)
        form.setVerticalSpacing(10)

        form.addWidget(QLabel("Nom:"), 0, 0)
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Nom du produit")
        form.addWidget(self.input_name, 0, 1)

        form.addWidget(QLabel("Prix (DH):"), 0, 2)
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("0.00")
        form.addWidget(self.input_price, 0, 3)

        form.addWidget(QLabel("Stock:"), 1, 0)
        self.input_stock = QLineEdit()
        self.input_stock.setPlaceholderText("0")
        form.addWidget(self.input_stock, 1, 1)

        form.addWidget(QLabel("Categorie:"), 1, 2)
        self.input_category = QLineEdit()
        self.input_category.setPlaceholderText("Ex: Electronique")
        form.addWidget(self.input_category, 1, 3)

        btn_add = QPushButton("+ Ajouter le produit")
        btn_add.clicked.connect(self._add_product)
        btn_add.setStyleSheet("""
            QPushButton { background: #3f51b5; color: white; padding: 10px; 
                          font-weight: bold; border-radius: 6px; font-size: 13px; }
            QPushButton:hover { background: #303f9f; }
        """)
        form.addWidget(btn_add, 2, 0, 1, 4)

        # --- Tableau des produits ---
        list_group = QGroupBox("Liste des produits")
        list_group.setStyleSheet(form_group.styleSheet())
        layout.addWidget(list_group)
        list_layout = QVBoxLayout(list_group)

        # Barre de recherche
        search_row = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText("Rechercher par nom ou categorie...")
        self.input_search.textChanged.connect(self._search_products)
        search_row.addWidget(self.input_search)

        btn_refresh = QPushButton("Rafraichir")
        btn_refresh.clicked.connect(self._load_products)
        btn_refresh.setStyleSheet("""
            QPushButton { background: #00acc1; color: white; padding: 8px 15px; 
                          border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #00838f; }
        """)
        search_row.addWidget(btn_refresh)
        list_layout.addLayout(search_row)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["ID", "Nom", "Prix (DH)", "Stock", "Categorie"])
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget { alternate-background-color: #e8eaf6; }
            QHeaderView::section { background: #3f51b5; color: white; padding: 6px; font-weight: bold; }
        """)
        list_layout.addWidget(self.products_table)

        # Boutons d'action
        actions = QHBoxLayout()
        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self._edit_product)
        btn_edit.setStyleSheet("""
            QPushButton { background: #ff9800; color: white; padding: 10px 20px; 
                          border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #e65100; }
        """)
        actions.addWidget(btn_edit)

        btn_delete = QPushButton("Supprimer")
        btn_delete.clicked.connect(self._delete_product)
        btn_delete.setStyleSheet("""
            QPushButton { background: #f44336; color: white; padding: 10px 20px; 
                          border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #b71c1c; }
        """)
        actions.addWidget(btn_delete)
        list_layout.addLayout(actions)

        return tab

    def _build_sales_tab(self):
        """Onglet des ventes."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # --- Nouvelle vente ---
        sale_group = QGroupBox("Nouvelle vente")
        sale_group.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #1a237e; font-size: 13px; 
                        border: 2px solid #c5cae9; border-radius: 8px; margin-top: 15px; padding-top: 20px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }
        """)
        layout.addWidget(sale_group)

        sale_form = QGridLayout(sale_group)
        sale_form.setVerticalSpacing(10)

        sale_form.addWidget(QLabel("Produit:"), 0, 0)
        self.combo_products = QComboBox()
        self.combo_products.currentTextChanged.connect(self._update_price_display)
        sale_form.addWidget(self.combo_products, 0, 1)

        sale_form.addWidget(QLabel("Prix unitaire:"), 0, 2)
        self.label_unit_price = QLabel("0.00 DH")
        self.label_unit_price.setStyleSheet("font-weight: bold; color: #2e7d32; font-size: 14px;")
        sale_form.addWidget(self.label_unit_price, 0, 3)

        sale_form.addWidget(QLabel("Quantite:"), 1, 0)
        self.input_quantity = QSpinBox()
        self.input_quantity.setMinimum(1)
        self.input_quantity.setMaximum(9999)
        self.input_quantity.valueChanged.connect(self._update_total)
        sale_form.addWidget(self.input_quantity, 1, 1)

        sale_form.addWidget(QLabel("Client:"), 1, 2)
        self.input_customer = QLineEdit()
        self.input_customer.setPlaceholderText("Nom du client")
        sale_form.addWidget(self.input_customer, 1, 3)

        total_row = QHBoxLayout()
        total_row.addStretch()
        self.label_total = QLabel("Total: 0.00 DH")
        self.label_total.setStyleSheet("font-weight: bold; font-size: 20px; color: #e65100;")
        total_row.addWidget(self.label_total)
        total_row.addStretch()

        btn_sell = QPushButton("Effectuer la vente")
        btn_sell.clicked.connect(self._make_sale)
        btn_sell.setStyleSheet("""
            QPushButton { background: #2e7d32; color: white; padding: 12px; 
                          font-weight: bold; border-radius: 6px; font-size: 14px; }
            QPushButton:hover { background: #1b5e20; }
        """)

        sale_form.addLayout(total_row, 3, 0, 1, 4)
        sale_form.addWidget(btn_sell, 4, 0, 1, 4)

        # --- Historique ---
        history_group = QGroupBox("Historique des ventes")
        history_group.setStyleSheet(sale_group.styleSheet())
        layout.addWidget(history_group)
        hist_layout = QVBoxLayout(history_group)

        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Produit", "Quantite", "Total (DH)", "Date", "Client"])
        self.sales_table.horizontalHeader().setStretchLastSection(True)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.sales_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setStyleSheet("""
            QTableWidget { alternate-background-color: #e8eaf6; }
            QHeaderView::section { background: #3f51b5; color: white; padding: 6px; font-weight: bold; }
        """)
        hist_layout.addWidget(self.sales_table)

        btn_refresh_sales = QPushButton("Rafraichir l'historique")
        btn_refresh_sales.clicked.connect(self._load_sales)
        btn_refresh_sales.setStyleSheet("""
            QPushButton { background: #00acc1; color: white; padding: 8px; 
                          border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background: #00838f; }
        """)
        hist_layout.addWidget(btn_refresh_sales)

        return tab

    def _build_stats_tab(self):
        """Onglet des statistiques."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Cartes de statistiques
        cards = QGridLayout()
        layout.addLayout(cards)

        self.card_total = self._make_stat_card("Chiffre d'affaires", "0.00 DH", "#2e7d32")
        cards.addWidget(self.card_total, 0, 0)

        self.card_count = self._make_stat_card("Nombre de ventes", "0", "#1565c0")
        cards.addWidget(self.card_count, 0, 1)

        self.card_top = self._make_stat_card("Produit star", "Aucun", "#e65100")
        cards.addWidget(self.card_top, 1, 0, 1, 2)

        btn_calc = QPushButton("Calculer les statistiques")
        btn_calc.clicked.connect(self._compute_stats)
        btn_calc.setStyleSheet("""
            QPushButton { background: #7b1fa2; color: white; padding: 12px; 
                          font-weight: bold; border-radius: 6px; font-size: 14px; }
            QPushButton:hover { background: #4a148c; }
        """)
        layout.addWidget(btn_calc)

        # Top produits
        top_group = QGroupBox("Top 5 des produits les plus vendus")
        top_group.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #1a237e; font-size: 13px; 
                        border: 2px solid #c5cae9; border-radius: 8px; margin-top: 15px; padding-top: 20px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; }
        """)
        layout.addWidget(top_group)
        top_layout = QVBoxLayout(top_group)

        self.top_table = QTableWidget()
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels(["Produit", "Quantite vendue", "Total (DH)"])
        self.top_table.horizontalHeader().setStretchLastSection(True)
        self.top_table.setAlternatingRowColors(True)
        top_layout.addWidget(self.top_table)

        return tab

    def _make_stat_card(self, title, value, color):
        """Cree une carte de statistique coloree."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{ background: white; border: 2px solid {color}; border-radius: 10px; padding: 15px; }}
        """)
        card_layout = QVBoxLayout(card)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #546e7a; font-size: 12px;")
        lbl_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(lbl_title)
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setObjectName("card_value")
        card_layout.addWidget(lbl_value)
        return card

    # ----------------------------------------------------------------
    # OPERATIONS PRODUITS
    # ----------------------------------------------------------------

    def _add_product(self):
        """Ajoute un nouveau produit."""
        name = self.input_name.text().strip()
        price_text = self.input_price.text().strip()
        stock_text = self.input_stock.text().strip()
        category = self.input_category.text().strip()

        if not name or not price_text or not stock_text:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        try:
            price = float(price_text)
            stock = int(stock_text)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Le prix et le stock doivent etre des nombres valides.")
            return

        self.cursor.execute(
            "INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)",
            (name, price, stock, category)
        )
        self.conn.commit()

        # Vider les champs
        self.input_name.clear()
        self.input_price.clear()
        self.input_stock.clear()
        self.input_category.clear()

        self._load_products()
        self._load_combos()
        QMessageBox.information(self, "Succes", f"Produit '{name}' ajoute avec succes.")

    def _load_products(self):
        """Charge tous les produits dans le tableau."""
        self.cursor.execute("SELECT * FROM products ORDER BY name")
        products = self.cursor.fetchall()

        self.products_table.setRowCount(0)
        for row_idx, product in enumerate(products):
            self.products_table.insertRow(row_idx)
            for col_idx, value in enumerate(product):
                if col_idx == 2:  # Prix formate
                    value = f"{float(value):.2f}"
                self.products_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def _load_combos(self):
        """Charge les produits dans le menu deroulant des ventes."""
        self.combo_products.clear()
        self.cursor.execute("SELECT id, name, price FROM products WHERE stock > 0 ORDER BY name")
        for product in self.cursor.fetchall():
            self.combo_products.addItem(f"{product[1]} - {product[2]:.2f} DH", product[0])

    def _search_products(self):
        """Filtre les produits selon la recherche."""
        text = self.input_search.text().strip()
        if text:
            self.cursor.execute(
                "SELECT * FROM products WHERE name LIKE ? OR category LIKE ? ORDER BY name",
                (f"%{text}%", f"%{text}%")
            )
        else:
            self.cursor.execute("SELECT * FROM products ORDER BY name")

        products = self.cursor.fetchall()
        self.products_table.setRowCount(0)
        for row_idx, product in enumerate(products):
            self.products_table.insertRow(row_idx)
            for col_idx, value in enumerate(product):
                if col_idx == 2:
                    value = f"{float(value):.2f}"
                self.products_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def _edit_product(self):
        """Modifie le produit selectionne."""
        row = self.products_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Selectionnez un produit a modifier.")
            return

        product_id = self.products_table.item(row, 0).text()
        name = self.products_table.item(row, 1).text()
        price = self.products_table.item(row, 2).text()
        stock = self.products_table.item(row, 3).text()
        category = self.products_table.item(row, 4).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier le produit")
        dialog.setModal(True)
        dialog.setMinimumWidth(350)

        dlg_layout = QGridLayout(dialog)
        dlg_layout.addWidget(QLabel("Nom:"), 0, 0)
        dlg_name = QLineEdit(name)
        dlg_layout.addWidget(dlg_name, 0, 1)
        dlg_layout.addWidget(QLabel("Prix:"), 1, 0)
        dlg_price = QLineEdit(price)
        dlg_layout.addWidget(dlg_price, 1, 1)
        dlg_layout.addWidget(QLabel("Stock:"), 2, 0)
        dlg_stock = QLineEdit(stock)
        dlg_layout.addWidget(dlg_stock, 2, 1)
        dlg_layout.addWidget(QLabel("Categorie:"), 3, 0)
        dlg_cat = QLineEdit(category)
        dlg_layout.addWidget(dlg_cat, 3, 1)

        btn_ok = QPushButton("Enregistrer")
        btn_ok.clicked.connect(dialog.accept)
        dlg_layout.addWidget(btn_ok, 4, 0, 1, 2)

        if dialog.exec_() == QDialog.Accepted:
            try:
                self.cursor.execute(
                    "UPDATE products SET name=?, price=?, stock=?, category=? WHERE id=?",
                    (dlg_name.text(), float(dlg_price.text()), int(dlg_stock.text()), dlg_cat.text(), product_id)
                )
                self.conn.commit()
                self._load_products()
                self._load_combos()
                QMessageBox.information(self, "Succes", "Produit modifie avec succes.")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _delete_product(self):
        """Supprime le produit selectionne."""
        row = self.products_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Erreur", "Selectionnez un produit a supprimer.")
            return

        product_id = self.products_table.item(row, 0).text()
        name = self.products_table.item(row, 1).text()

        reply = QMessageBox.question(
            self, "Confirmation", f"Supprimer definitivement '{name}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            self.conn.commit()
            self._load_products()
            self._load_combos()
            QMessageBox.information(self, "Succes", "Produit supprime.")

    # ----------------------------------------------------------------
    # OPERATIONS VENTES
    # ----------------------------------------------------------------

    def _update_price_display(self):
        """Met a jour l'affichage du prix unitaire."""
        idx = self.combo_products.currentIndex()
        if idx >= 0:
            price = self.combo_products.itemData(idx)
            if price:
                self.label_unit_price.setText(f"{float(price):.2f} DH")
                self._update_total()

    def _update_total(self):
        """Calcule le total de la vente en cours."""
        quantity = self.input_quantity.value()
        idx = self.combo_products.currentIndex()
        if idx >= 0:
            price = self.combo_products.itemData(idx)
            if price:
                total = float(price) * quantity
                self.label_total.setText(f"Total: {total:.2f} DH")

    def _make_sale(self):
        """Enregistre une vente."""
        idx = self.combo_products.currentIndex()
        if idx < 0:
            QMessageBox.warning(self, "Erreur", "Selectionnez un produit.")
            return

        product_id = self.combo_products.itemData(idx)
        quantity = self.input_quantity.value()
        customer = self.input_customer.text().strip() or "Client anonyme"

        self.cursor.execute("SELECT price, stock FROM products WHERE id=?", (product_id,))
        product = self.cursor.fetchone()
        if not product:
            QMessageBox.warning(self, "Erreur", "Produit introuvable.")
            return

        price, stock = product
        if quantity > stock:
            QMessageBox.warning(self, "Erreur", f"Stock insuffisant. Disponible: {stock}")
            return

        total = price * quantity
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            "INSERT INTO sales (product_id, quantity, total, date, customer) VALUES (?, ?, ?, ?, ?)",
            (product_id, quantity, total, date, customer)
        )
        self.cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (quantity, product_id))
        self.conn.commit()

        # Reinitialiser
        self.input_quantity.setValue(1)
        self.input_customer.clear()
        self.label_total.setText("Total: 0.00 DH")

        self._load_sales()
        self._load_products()
        self._load_combos()

        QMessageBox.information(self, "Succes", f"Vente reussie!\nTotal: {total:.2f} DH\nClient: {customer}")

    def _load_sales(self):
        """Charge l'historique des ventes."""
        self.cursor.execute("""
            SELECT s.id, p.name, s.quantity, s.total, s.date, s.customer
            FROM sales s JOIN products p ON s.product_id = p.id
            ORDER BY s.date DESC
        """)
        sales = self.cursor.fetchall()

        self.sales_table.setRowCount(0)
        for row_idx, sale in enumerate(sales):
            self.sales_table.insertRow(row_idx)
            for col_idx, value in enumerate(sale):
                if col_idx == 3:
                    value = f"{float(value):.2f}"
                self.sales_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    # ----------------------------------------------------------------
    # STATISTIQUES
    # ----------------------------------------------------------------

    def _compute_stats(self):
        """Calcule et affiche les statistiques."""
        # Total des ventes
        self.cursor.execute("SELECT COALESCE(SUM(total), 0) FROM sales")
        total = self.cursor.fetchone()[0]
        card = self.card_total.findChild(QLabel, "card_value")
        if card:
            card.setText(f"{total:.2f} DH")

        # Nombre de ventes
        self.cursor.execute("SELECT COUNT(*) FROM sales")
        count = self.cursor.fetchone()[0]
        card = self.card_count.findChild(QLabel, "card_value")
        if card:
            card.setText(str(count))

        # Top 5 produits
        self.cursor.execute("""
            SELECT p.name, SUM(s.quantity), SUM(s.total)
            FROM sales s JOIN products p ON s.product_id = p.id
            GROUP BY p.id ORDER BY SUM(s.quantity) DESC LIMIT 5
        """)
        top = self.cursor.fetchall()

        self.top_table.setRowCount(0)
        for row_idx, item in enumerate(top):
            self.top_table.insertRow(row_idx)
            self.top_table.setItem(row_idx, 0, QTableWidgetItem(item[0]))
            self.top_table.setItem(row_idx, 1, QTableWidgetItem(str(item[1])))
            self.top_table.setItem(row_idx, 2, QTableWidgetItem(f"{item[2]:.2f}"))

        # Produit star
        if top:
            card = self.card_top.findChild(QLabel, "card_value")
            if card:
                card.setText(f"{top[0][0]} ({top[0][1]} ventes)")
        else:
            card = self.card_top.findChild(QLabel, "card_value")
            if card:
                card.setText("Aucune vente")

        QMessageBox.information(self, "Statistiques", "Statistiques mises a jour avec succes.")

    def closeEvent(self, event):
        """Ferme la connexion DB a la fermeture de la fenetre."""
        self.conn.close()
        event.accept()


# ================================================================
# POINT D'ENTREE
# ================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StockFlow()
    window.show()
    sys.exit(app.exec_())
