# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'game_input_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_GameInputDialog(object):
    def setupUi(self, GameInputDialog):
        if not GameInputDialog.objectName():
            GameInputDialog.setObjectName(u"GameInputDialog")
        GameInputDialog.resize(407, 235)
        self.gridLayout = QGridLayout(GameInputDialog)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setObjectName(u"gridLayout")
        self.accept_button = QPushButton(GameInputDialog)
        self.accept_button.setObjectName(u"accept_button")

        self.gridLayout.addWidget(self.accept_button, 6, 0, 1, 1)

        self.auto_save_spoiler_check = QCheckBox(GameInputDialog)
        self.auto_save_spoiler_check.setObjectName(u"auto_save_spoiler_check")

        self.gridLayout.addWidget(self.auto_save_spoiler_check, 5, 0, 1, 2)

        self.output_file_button = QPushButton(GameInputDialog)
        self.output_file_button.setObjectName(u"output_file_button")

        self.gridLayout.addWidget(self.output_file_button, 4, 2, 1, 1)

        self.output_file_edit = QLineEdit(GameInputDialog)
        self.output_file_edit.setObjectName(u"output_file_edit")

        self.gridLayout.addWidget(self.output_file_edit, 4, 0, 1, 2)

        self.input_file_label = QLabel(GameInputDialog)
        self.input_file_label.setObjectName(u"input_file_label")
        self.input_file_label.setMaximumSize(QSize(16777215, 20))

        self.gridLayout.addWidget(self.input_file_label, 1, 0, 1, 2)

        self.description_label = QLabel(GameInputDialog)
        self.description_label.setObjectName(u"description_label")
        self.description_label.setWordWrap(True)

        self.gridLayout.addWidget(self.description_label, 0, 0, 1, 3)

        self.input_file_edit = QLineEdit(GameInputDialog)
        self.input_file_edit.setObjectName(u"input_file_edit")

        self.gridLayout.addWidget(self.input_file_edit, 2, 0, 1, 2)

        self.cancel_button = QPushButton(GameInputDialog)
        self.cancel_button.setObjectName(u"cancel_button")

        self.gridLayout.addWidget(self.cancel_button, 6, 2, 1, 1)

        self.output_file_label = QLabel(GameInputDialog)
        self.output_file_label.setObjectName(u"output_file_label")
        self.output_file_label.setMaximumSize(QSize(16777215, 20))

        self.gridLayout.addWidget(self.output_file_label, 3, 0, 1, 2)

        self.input_file_button = QPushButton(GameInputDialog)
        self.input_file_button.setObjectName(u"input_file_button")

        self.gridLayout.addWidget(self.input_file_button, 2, 2, 1, 1)


        self.retranslateUi(GameInputDialog)

        QMetaObject.connectSlotsByName(GameInputDialog)
    # setupUi

    def retranslateUi(self, GameInputDialog):
        GameInputDialog.setWindowTitle(QCoreApplication.translate("GameInputDialog", u"Game Patching", None))
        self.accept_button.setText(QCoreApplication.translate("GameInputDialog", u"Accept", None))
        self.auto_save_spoiler_check.setText(QCoreApplication.translate("GameInputDialog", u"Include a spoiler log on same directory", None))
        self.output_file_button.setText(QCoreApplication.translate("GameInputDialog", u"Select File", None))
        self.output_file_edit.setPlaceholderText(QCoreApplication.translate("GameInputDialog", u"Path where to place randomized game", None))
        self.input_file_label.setText(QCoreApplication.translate("GameInputDialog", u"Input File (Vanilla Gamecube ISO)", None))
        self.description_label.setText(QCoreApplication.translate("GameInputDialog", u"<html><head/><body><p>In order to create the randomized game, a ISO file of Metroid Prime 2: Echoes for the Nintendo Gamecube is necessary.</p><p>After using it once, a copy is kept by Randovania for later use.</p></body></html>", None))
        self.input_file_edit.setPlaceholderText(QCoreApplication.translate("GameInputDialog", u"Path to vanilla Gamecube ISO", None))
        self.cancel_button.setText(QCoreApplication.translate("GameInputDialog", u"Cancel", None))
        self.output_file_label.setText(QCoreApplication.translate("GameInputDialog", u"Output File", None))
        self.input_file_button.setText(QCoreApplication.translate("GameInputDialog", u"Select File", None))
    # retranslateUi

