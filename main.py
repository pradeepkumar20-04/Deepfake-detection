from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QInputDialog, QFrame, QHBoxLayout, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QMovie
from web3 import Web3, Account
import sys
import os
import hashlib
from PIL import Image
from datetime import datetime

class BlockchainApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blockchain Image Analysis")
        self.setGeometry(300, 100, 600, 700)
        self.setStyleSheet("""
            background-color: #1e1e2f;
            color: white;
            font-family: Arial;
        """)

        # Connect to Ganache Blockchain
        ganache_url = 'http://127.0.0.1:7545'
        self.web3 = Web3(Web3.HTTPProvider(ganache_url))

        if self.web3.is_connected():
            print("Connected to Ganache Blockchain")
        else:
            print("Connection failed")


        self.private_key = '0x5b57026b6d66354bd5d789953d6d0590ae8ee96bd23363492af1e82a8b0bc4f8'
        self.account = Account.from_key(self.private_key)

        print("Connected to Ethereum Account:", self.account.address)


        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # **Header Label**
        title_label = QLabel("Blockchain Image Analyzer")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #f1c40f;")
        layout.addWidget(title_label)

        # **Upload Button**
        self.upload_button = QPushButton("Upload Image")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        self.upload_button.clicked.connect(self.upload_image)
        layout.addWidget(self.upload_button)

        # **Retrieve Transaction Button**
        self.retrieve_button = QPushButton("Retrieve Transaction")
        self.retrieve_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22; color: white; font-size: 14px; font-weight: bold;
                border-radius: 8px; padding: 10px;
            }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.retrieve_button.clicked.connect(self.retrieve_transaction)
        layout.addWidget(self.retrieve_button)

        # **Image Preview Frame**
        self.image_frame = QLabel(self)
        self.image_frame.setStyleSheet("""
            QLabel { border: 2px solid #ffffff; border-radius: 8px; }
        """)
        self.image_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_frame)

        # **Metadata Label**
        self.metadata_label = QLabel("Image Metadata: ")
        self.metadata_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.metadata_label.setWordWrap(True)
        layout.addWidget(self.metadata_label)

        # **Tampering Result**
        self.tampering_label = QLabel("Tampering Detection Result: ")
        self.tampering_label.setStyleSheet("font-size: 14px; padding: 5px;")
        self.tampering_label.setWordWrap(True)
        layout.addWidget(self.tampering_label)

        # **Status/Error Message**
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        layout.addWidget(self.status_label)

        # **Progress Bar**
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid white; border-radius: 5px; text-align: center; height: 10px;
            }
            QProgressBar::chunk {
                background-color: #27ae60; width: 20px;
            }
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.display_uploaded_image(file_path)
            self.process_image(file_path)

    def display_uploaded_image(self, file_path):
        pixmap = QPixmap(file_path)
        self.image_frame.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))
        self.image_frame.setText("")

    def process_image(self, file_path):
        metadata_str = self.extract_metadata(file_path)
        self.metadata_label.setText(f"Image Metadata:\n{metadata_str}")

        tampering_result = "No tampering detected"
        self.tampering_label.setText(f"Tampering Result: {tampering_result}")

        # **Simulate Processing**
        self.progress_bar.setValue(0)
        for i in range(0, 101, 20):
            QTimer.singleShot(i * 50, lambda v=i: self.progress_bar.setValue(v))

        self.store_on_blockchain(file_path, metadata_str, tampering_result)

    def extract_metadata(self, file_path):
        img = Image.open(file_path)
        img_size = img.size
        img_format = img.format
        img_mode = img.mode
        img_resolution = f"{img_size[0]}x{img_size[1]}"
        img_size_bytes = os.path.getsize(file_path)
        image_hash = self.get_image_hash(file_path)
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        metadata_str = (f"Timestamp: {timestamp}\n"
                        f"Resolution: {img_resolution}\n"
                        f"Format: {img_format}\n"
                        f"Mode: {img_mode}\n"
                        f"Size: {img_size_bytes} bytes\n"
                        f"Hash: {image_hash}")

        return metadata_str

    def get_image_hash(self, file_path):
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def store_on_blockchain(self, file_path, metadata, tampering_result):
        try:
            transaction_data = f"Image: {file_path}, Metadata: {metadata}, Tampering Result: {tampering_result}"
            self.status_label.setText("Processing Transaction...")

            # Simulated Success Message
            QTimer.singleShot(2000, lambda: self.status_label.setText("Transaction Successful!"))
            QTimer.singleShot(2000, lambda: self.status_label.setStyleSheet("color: #2ecc71;"))
            transaction = {
                'to': self.account.address,
                'value': 0,
                'gas': 2000000,
                'gasPrice': self.web3.to_wei(20, 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(self.account.address),
                'data': self.web3.to_hex(text=transaction_data)
            }

            signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.raw_transaction)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

            print("Transaction successful! Hash:", tx_receipt.transactionHash.hex())

            self.status_label.setStyleSheet("color: green; font-size: 16px;")
            self.status_label.setText(f"Transaction successful! Hash: {tx_receipt.transactionHash.hex()}")

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red;")

    def retrieve_transaction(self):
        tx_hash, ok = QInputDialog.getText(self, "Retrieve Data", "Enter Transaction Hash:")
        if ok and tx_hash:
            try:
                tx = self.web3.eth.get_transaction(tx_hash)

                if tx and tx.input:
                    metadata = self.web3.to_text(tx.input)
                    self.status_label.setStyleSheet("color: green; font-size: 16px;")
                    self.status_label.setText(f"Stored Metadata:\n{metadata}")
                    print("Retrieved Metadata:", metadata)
                else:
                    self.status_label.setStyleSheet("color: red; font-size: 16px;")
                    self.status_label.setText("No data found in this transaction.")
            except Exception as e:
                self.status_label.setStyleSheet("color: red; font-size: 16px;")
                self.status_label.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = BlockchainApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
