# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'node_details_popup.ui'
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


class Ui_NodeDetailsPopup(object):
    def setupUi(self, NodeDetailsPopup):
        if not NodeDetailsPopup.objectName():
            NodeDetailsPopup.setObjectName(u"NodeDetailsPopup")
        NodeDetailsPopup.resize(556, 475)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NodeDetailsPopup.sizePolicy().hasHeightForWidth())
        NodeDetailsPopup.setSizePolicy(sizePolicy)
        NodeDetailsPopup.setMaximumSize(QSize(16777215, 16777215))
        self.main_layout = QVBoxLayout(NodeDetailsPopup)
        self.main_layout.setSpacing(6)
        self.main_layout.setContentsMargins(11, 11, 11, 11)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.name_layout = QHBoxLayout()
        self.name_layout.setSpacing(6)
        self.name_layout.setObjectName(u"name_layout")
        self.name_label = QLabel(NodeDetailsPopup)
        self.name_label.setObjectName(u"name_label")
        sizePolicy.setHeightForWidth(self.name_label.sizePolicy().hasHeightForWidth())
        self.name_label.setSizePolicy(sizePolicy)

        self.name_layout.addWidget(self.name_label)

        self.name_edit = QLineEdit(NodeDetailsPopup)
        self.name_edit.setObjectName(u"name_edit")

        self.name_layout.addWidget(self.name_edit)


        self.main_layout.addLayout(self.name_layout)

        self.heals_check = QCheckBox(NodeDetailsPopup)
        self.heals_check.setObjectName(u"heals_check")

        self.main_layout.addWidget(self.heals_check)

        self.location_group = QGroupBox(NodeDetailsPopup)
        self.location_group.setObjectName(u"location_group")
        self.location_group.setCheckable(True)
        self.location_group.setChecked(True)
        self.location_layout = QHBoxLayout(self.location_group)
        self.location_layout.setSpacing(6)
        self.location_layout.setContentsMargins(11, 11, 11, 11)
        self.location_layout.setObjectName(u"location_layout")
        self.location_layout.setContentsMargins(4, 2, 4, 2)
        self.location_x_label = QLabel(self.location_group)
        self.location_x_label.setObjectName(u"location_x_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.location_x_label.sizePolicy().hasHeightForWidth())
        self.location_x_label.setSizePolicy(sizePolicy1)
        self.location_x_label.setMinimumSize(QSize(20, 0))

        self.location_layout.addWidget(self.location_x_label)

        self.location_x_spin = QDoubleSpinBox(self.location_group)
        self.location_x_spin.setObjectName(u"location_x_spin")
        self.location_x_spin.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.location_x_spin.setMinimum(-999.990000000000009)
        self.location_x_spin.setMaximum(999.990000000000009)

        self.location_layout.addWidget(self.location_x_spin)

        self.location_y_label = QLabel(self.location_group)
        self.location_y_label.setObjectName(u"location_y_label")
        sizePolicy1.setHeightForWidth(self.location_y_label.sizePolicy().hasHeightForWidth())
        self.location_y_label.setSizePolicy(sizePolicy1)
        self.location_y_label.setMinimumSize(QSize(20, 0))

        self.location_layout.addWidget(self.location_y_label)

        self.location_y_spin = QDoubleSpinBox(self.location_group)
        self.location_y_spin.setObjectName(u"location_y_spin")
        self.location_y_spin.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.location_y_spin.setMinimum(-999.990000000000009)
        self.location_y_spin.setMaximum(999.990000000000009)

        self.location_layout.addWidget(self.location_y_spin)

        self.location_z_label = QLabel(self.location_group)
        self.location_z_label.setObjectName(u"location_z_label")
        sizePolicy1.setHeightForWidth(self.location_z_label.sizePolicy().hasHeightForWidth())
        self.location_z_label.setSizePolicy(sizePolicy1)
        self.location_z_label.setMinimumSize(QSize(20, 0))

        self.location_layout.addWidget(self.location_z_label)

        self.location_z_spin = QDoubleSpinBox(self.location_group)
        self.location_z_spin.setObjectName(u"location_z_spin")
        self.location_z_spin.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.location_z_spin.setMinimum(-999.990000000000009)
        self.location_z_spin.setMaximum(999.990000000000009)

        self.location_layout.addWidget(self.location_z_spin)


        self.main_layout.addWidget(self.location_group)

        self.node_type_combo = QComboBox(NodeDetailsPopup)
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.addItem("")
        self.node_type_combo.setObjectName(u"node_type_combo")

        self.main_layout.addWidget(self.node_type_combo)

        self.tab_widget = QTabWidget(NodeDetailsPopup)
        self.tab_widget.setObjectName(u"tab_widget")
        self.tab_generic = QWidget()
        self.tab_generic.setObjectName(u"tab_generic")
        self.generic_layout = QHBoxLayout(self.tab_generic)
        self.generic_layout.setSpacing(6)
        self.generic_layout.setContentsMargins(11, 11, 11, 11)
        self.generic_layout.setObjectName(u"generic_layout")
        self.label = QLabel(self.tab_generic)
        self.label.setObjectName(u"label")
        self.label.setAlignment(Qt.AlignCenter)

        self.generic_layout.addWidget(self.label)

        self.tab_widget.addTab(self.tab_generic, "")
        self.tab_dock = QWidget()
        self.tab_dock.setObjectName(u"tab_dock")
        self.dock_layout = QGridLayout(self.tab_dock)
        self.dock_layout.setSpacing(6)
        self.dock_layout.setContentsMargins(11, 11, 11, 11)
        self.dock_layout.setObjectName(u"dock_layout")
        self.dock_layout.setContentsMargins(2, 2, 2, 2)
        self.dock_type_combo = QComboBox(self.tab_dock)
        self.dock_type_combo.addItem("")
        self.dock_type_combo.addItem("")
        self.dock_type_combo.addItem("")
        self.dock_type_combo.addItem("")
        self.dock_type_combo.setObjectName(u"dock_type_combo")

        self.dock_layout.addWidget(self.dock_type_combo, 2, 1, 1, 1)

        self.dock_type_label = QLabel(self.tab_dock)
        self.dock_type_label.setObjectName(u"dock_type_label")

        self.dock_layout.addWidget(self.dock_type_label, 2, 0, 1, 1)

        self.dock_index_label = QLabel(self.tab_dock)
        self.dock_index_label.setObjectName(u"dock_index_label")

        self.dock_layout.addWidget(self.dock_index_label, 0, 0, 1, 1)

        self.dock_weakness_combo = QComboBox(self.tab_dock)
        self.dock_weakness_combo.setObjectName(u"dock_weakness_combo")

        self.dock_layout.addWidget(self.dock_weakness_combo, 3, 0, 1, 2)

        self.dock_index_spin = QSpinBox(self.tab_dock)
        self.dock_index_spin.setObjectName(u"dock_index_spin")

        self.dock_layout.addWidget(self.dock_index_spin, 0, 1, 1, 1)

        self.dock_connection_group = QGroupBox(self.tab_dock)
        self.dock_connection_group.setObjectName(u"dock_connection_group")
        self.dock_connection_layout = QHBoxLayout(self.dock_connection_group)
        self.dock_connection_layout.setSpacing(6)
        self.dock_connection_layout.setContentsMargins(11, 11, 11, 11)
        self.dock_connection_layout.setObjectName(u"dock_connection_layout")
        self.dock_connection_layout.setContentsMargins(2, 2, 2, 2)
        self.dock_connection_area_combo = QComboBox(self.dock_connection_group)
        self.dock_connection_area_combo.setObjectName(u"dock_connection_area_combo")

        self.dock_connection_layout.addWidget(self.dock_connection_area_combo)

        self.dock_connection_node_combo = QComboBox(self.dock_connection_group)
        self.dock_connection_node_combo.setObjectName(u"dock_connection_node_combo")

        self.dock_connection_layout.addWidget(self.dock_connection_node_combo)

        self.dock_connection_index_raw_spin = QSpinBox(self.dock_connection_group)
        self.dock_connection_index_raw_spin.setObjectName(u"dock_connection_index_raw_spin")
        self.dock_connection_index_raw_spin.setMaximumSize(QSize(40, 16777215))

        self.dock_connection_layout.addWidget(self.dock_connection_index_raw_spin)


        self.dock_layout.addWidget(self.dock_connection_group, 1, 0, 1, 2)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.dock_layout.addItem(self.verticalSpacer, 4, 0, 1, 1)

        self.tab_widget.addTab(self.tab_dock, "")
        self.tab_pickup = QWidget()
        self.tab_pickup.setObjectName(u"tab_pickup")
        self.pickup_layout = QGridLayout(self.tab_pickup)
        self.pickup_layout.setSpacing(6)
        self.pickup_layout.setContentsMargins(11, 11, 11, 11)
        self.pickup_layout.setObjectName(u"pickup_layout")
        self.pickup_layout.setContentsMargins(2, 2, 2, 2)
        self.major_location_check = QCheckBox(self.tab_pickup)
        self.major_location_check.setObjectName(u"major_location_check")

        self.pickup_layout.addWidget(self.major_location_check, 1, 0, 1, 2)

        self.pickup_index_spin = QSpinBox(self.tab_pickup)
        self.pickup_index_spin.setObjectName(u"pickup_index_spin")
        self.pickup_index_spin.setMaximum(999)

        self.pickup_layout.addWidget(self.pickup_index_spin, 0, 1, 1, 1)

        self.pickup_index_label = QLabel(self.tab_pickup)
        self.pickup_index_label.setObjectName(u"pickup_index_label")

        self.pickup_layout.addWidget(self.pickup_index_label, 0, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.pickup_layout.addItem(self.verticalSpacer_2, 2, 0, 1, 1)

        self.tab_widget.addTab(self.tab_pickup, "")
        self.tab_teleporter = QWidget()
        self.tab_teleporter.setObjectName(u"tab_teleporter")
        self.teleporter_layout = QGridLayout(self.tab_teleporter)
        self.teleporter_layout.setSpacing(6)
        self.teleporter_layout.setContentsMargins(11, 11, 11, 11)
        self.teleporter_layout.setObjectName(u"teleporter_layout")
        self.teleporter_layout.setContentsMargins(2, 2, 2, 2)
        self.teleporter_editable_check = QCheckBox(self.tab_teleporter)
        self.teleporter_editable_check.setObjectName(u"teleporter_editable_check")

        self.teleporter_layout.addWidget(self.teleporter_editable_check, 3, 0, 1, 1)

        self.teleporter_instance_id_edit = QLineEdit(self.tab_teleporter)
        self.teleporter_instance_id_edit.setObjectName(u"teleporter_instance_id_edit")

        self.teleporter_layout.addWidget(self.teleporter_instance_id_edit, 0, 1, 1, 1)

        self.teleporter_scan_asset_id_edit = QLineEdit(self.tab_teleporter)
        self.teleporter_scan_asset_id_edit.setObjectName(u"teleporter_scan_asset_id_edit")

        self.teleporter_layout.addWidget(self.teleporter_scan_asset_id_edit, 2, 1, 1, 1)

        self.teleporter_destination_group = QGroupBox(self.tab_teleporter)
        self.teleporter_destination_group.setObjectName(u"teleporter_destination_group")
        sizePolicy.setHeightForWidth(self.teleporter_destination_group.sizePolicy().hasHeightForWidth())
        self.teleporter_destination_group.setSizePolicy(sizePolicy)
        self.teleporter_destination_layout = QHBoxLayout(self.teleporter_destination_group)
        self.teleporter_destination_layout.setSpacing(6)
        self.teleporter_destination_layout.setContentsMargins(11, 11, 11, 11)
        self.teleporter_destination_layout.setObjectName(u"teleporter_destination_layout")
        self.teleporter_destination_layout.setContentsMargins(2, 2, 2, 2)
        self.teleporter_destination_world_combo = QComboBox(self.teleporter_destination_group)
        self.teleporter_destination_world_combo.setObjectName(u"teleporter_destination_world_combo")

        self.teleporter_destination_layout.addWidget(self.teleporter_destination_world_combo)

        self.teleporter_destination_area_combo = QComboBox(self.teleporter_destination_group)
        self.teleporter_destination_area_combo.setObjectName(u"teleporter_destination_area_combo")

        self.teleporter_destination_layout.addWidget(self.teleporter_destination_area_combo)


        self.teleporter_layout.addWidget(self.teleporter_destination_group, 1, 0, 1, 2)

        self.teleporter_scan_asset_id_label = QLabel(self.tab_teleporter)
        self.teleporter_scan_asset_id_label.setObjectName(u"teleporter_scan_asset_id_label")

        self.teleporter_layout.addWidget(self.teleporter_scan_asset_id_label, 2, 0, 1, 1)

        self.teleporter_vanilla_name_edit = QCheckBox(self.tab_teleporter)
        self.teleporter_vanilla_name_edit.setObjectName(u"teleporter_vanilla_name_edit")

        self.teleporter_layout.addWidget(self.teleporter_vanilla_name_edit, 3, 1, 1, 1)

        self.teleporter_instance_id_label = QLabel(self.tab_teleporter)
        self.teleporter_instance_id_label.setObjectName(u"teleporter_instance_id_label")

        self.teleporter_layout.addWidget(self.teleporter_instance_id_label, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.teleporter_layout.addItem(self.verticalSpacer_3, 4, 0, 1, 1)

        self.tab_widget.addTab(self.tab_teleporter, "")
        self.tab_event = QWidget()
        self.tab_event.setObjectName(u"tab_event")
        self.event_layout = QGridLayout(self.tab_event)
        self.event_layout.setSpacing(6)
        self.event_layout.setContentsMargins(11, 11, 11, 11)
        self.event_layout.setObjectName(u"event_layout")
        self.event_layout.setContentsMargins(2, 2, 2, 2)
        self.event_resource_label = QLabel(self.tab_event)
        self.event_resource_label.setObjectName(u"event_resource_label")

        self.event_layout.addWidget(self.event_resource_label, 0, 0, 1, 1)

        self.event_resource_combo = QComboBox(self.tab_event)
        self.event_resource_combo.setObjectName(u"event_resource_combo")

        self.event_layout.addWidget(self.event_resource_combo, 0, 1, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.event_layout.addItem(self.verticalSpacer_4, 1, 0, 1, 1)

        self.tab_widget.addTab(self.tab_event, "")
        self.tab_translator_gate = QWidget()
        self.tab_translator_gate.setObjectName(u"tab_translator_gate")
        self.translator_gate_layout = QGridLayout(self.tab_translator_gate)
        self.translator_gate_layout.setSpacing(6)
        self.translator_gate_layout.setContentsMargins(11, 11, 11, 11)
        self.translator_gate_layout.setObjectName(u"translator_gate_layout")
        self.translator_gate_layout.setContentsMargins(2, 2, 2, 2)
        self.translator_gate_spin = QSpinBox(self.tab_translator_gate)
        self.translator_gate_spin.setObjectName(u"translator_gate_spin")
        self.translator_gate_spin.setMaximum(999)

        self.translator_gate_layout.addWidget(self.translator_gate_spin, 0, 1, 1, 1)

        self.translator_gate_label = QLabel(self.tab_translator_gate)
        self.translator_gate_label.setObjectName(u"translator_gate_label")

        self.translator_gate_layout.addWidget(self.translator_gate_label, 0, 0, 1, 1)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.translator_gate_layout.addItem(self.verticalSpacer_5, 1, 0, 1, 1)

        self.tab_widget.addTab(self.tab_translator_gate, "")
        self.tab_logbook = QWidget()
        self.tab_logbook.setObjectName(u"tab_logbook")
        self.logbook_layout = QGridLayout(self.tab_logbook)
        self.logbook_layout.setSpacing(6)
        self.logbook_layout.setContentsMargins(11, 11, 11, 11)
        self.logbook_layout.setObjectName(u"logbook_layout")
        self.logbook_layout.setContentsMargins(2, 2, 2, 2)
        self.logbook_extra_label = QLabel(self.tab_logbook)
        self.logbook_extra_label.setObjectName(u"logbook_extra_label")

        self.logbook_layout.addWidget(self.logbook_extra_label, 2, 0, 1, 1)

        self.lore_type_combo = QComboBox(self.tab_logbook)
        self.lore_type_combo.addItem("")
        self.lore_type_combo.addItem("")
        self.lore_type_combo.addItem("")
        self.lore_type_combo.addItem("")
        self.lore_type_combo.setObjectName(u"lore_type_combo")

        self.logbook_layout.addWidget(self.lore_type_combo, 1, 1, 1, 1)

        self.logbook_extra_combo = QComboBox(self.tab_logbook)
        self.logbook_extra_combo.setObjectName(u"logbook_extra_combo")

        self.logbook_layout.addWidget(self.logbook_extra_combo, 2, 1, 1, 1)

        self.logbook_string_asset_id_edit = QLineEdit(self.tab_logbook)
        self.logbook_string_asset_id_edit.setObjectName(u"logbook_string_asset_id_edit")

        self.logbook_layout.addWidget(self.logbook_string_asset_id_edit, 0, 1, 1, 1)

        self.logbook_string_asset_id_label = QLabel(self.tab_logbook)
        self.logbook_string_asset_id_label.setObjectName(u"logbook_string_asset_id_label")

        self.logbook_layout.addWidget(self.logbook_string_asset_id_label, 0, 0, 1, 1)

        self.lore_type_label = QLabel(self.tab_logbook)
        self.lore_type_label.setObjectName(u"lore_type_label")

        self.logbook_layout.addWidget(self.lore_type_label, 1, 0, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.logbook_layout.addItem(self.verticalSpacer_6, 3, 0, 1, 1)

        self.tab_widget.addTab(self.tab_logbook, "")
        self.tab_player_ship = QWidget()
        self.tab_player_ship.setObjectName(u"tab_player_ship")
        self.player_ship_layout = QVBoxLayout(self.tab_player_ship)
        self.player_ship_layout.setSpacing(6)
        self.player_ship_layout.setContentsMargins(11, 11, 11, 11)
        self.player_ship_layout.setObjectName(u"player_ship_layout")
        self.player_ship_layout.setContentsMargins(2, 2, 2, 2)
        self.player_ship_unlocked_button = QPushButton(self.tab_player_ship)
        self.player_ship_unlocked_button.setObjectName(u"player_ship_unlocked_button")

        self.player_ship_layout.addWidget(self.player_ship_unlocked_button)

        self.player_ship_unlocked_group = QGroupBox(self.tab_player_ship)
        self.player_ship_unlocked_group.setObjectName(u"player_ship_unlocked_group")
        self.player_ship_unlocked_layout = QGridLayout(self.player_ship_unlocked_group)
        self.player_ship_unlocked_layout.setSpacing(2)
        self.player_ship_unlocked_layout.setContentsMargins(11, 11, 11, 11)
        self.player_ship_unlocked_layout.setObjectName(u"player_ship_unlocked_layout")
        self.player_ship_unlocked_layout.setContentsMargins(2, 2, 2, 2)

        self.player_ship_layout.addWidget(self.player_ship_unlocked_group)

        self.tab_widget.addTab(self.tab_player_ship, "")

        self.main_layout.addWidget(self.tab_widget)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.main_layout.addItem(self.verticalSpacer_7)

        self.button_box = QDialogButtonBox(NodeDetailsPopup)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.main_layout.addWidget(self.button_box)


        self.retranslateUi(NodeDetailsPopup)

        self.tab_widget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(NodeDetailsPopup)
    # setupUi

    def retranslateUi(self, NodeDetailsPopup):
        NodeDetailsPopup.setWindowTitle(QCoreApplication.translate("NodeDetailsPopup", u"Item Configuration", None))
        self.name_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Name:", None))
        self.heals_check.setText(QCoreApplication.translate("NodeDetailsPopup", u"Heals", None))
        self.location_group.setTitle(QCoreApplication.translate("NodeDetailsPopup", u"Location", None))
        self.location_x_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"X", None))
        self.location_y_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Y", None))
        self.location_z_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Z", None))
        self.node_type_combo.setItemText(0, QCoreApplication.translate("NodeDetailsPopup", u"Generic", None))
        self.node_type_combo.setItemText(1, QCoreApplication.translate("NodeDetailsPopup", u"Dock", None))
        self.node_type_combo.setItemText(2, QCoreApplication.translate("NodeDetailsPopup", u"Pickup", None))
        self.node_type_combo.setItemText(3, QCoreApplication.translate("NodeDetailsPopup", u"Teleporter", None))
        self.node_type_combo.setItemText(4, QCoreApplication.translate("NodeDetailsPopup", u"Event", None))
        self.node_type_combo.setItemText(5, QCoreApplication.translate("NodeDetailsPopup", u"Translator Gate", None))
        self.node_type_combo.setItemText(6, QCoreApplication.translate("NodeDetailsPopup", u"Logbook", None))
        self.node_type_combo.setItemText(7, QCoreApplication.translate("NodeDetailsPopup", u"Player Ship", None))

        self.label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Nothing!", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_generic), QCoreApplication.translate("NodeDetailsPopup", u"Generic", None))
        self.dock_type_combo.setItemText(0, QCoreApplication.translate("NodeDetailsPopup", u"Door", None))
        self.dock_type_combo.setItemText(1, QCoreApplication.translate("NodeDetailsPopup", u"Morph Ball Door", None))
        self.dock_type_combo.setItemText(2, QCoreApplication.translate("NodeDetailsPopup", u"Other", None))
        self.dock_type_combo.setItemText(3, QCoreApplication.translate("NodeDetailsPopup", u"Portal", None))

        self.dock_type_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Dock type:", None))
        self.dock_index_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Dock index:", None))
        self.dock_connection_group.setTitle(QCoreApplication.translate("NodeDetailsPopup", u"Dock Connection", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_dock), QCoreApplication.translate("NodeDetailsPopup", u"Dock", None))
        self.major_location_check.setText(QCoreApplication.translate("NodeDetailsPopup", u"Is major location", None))
        self.pickup_index_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Pickup Index:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_pickup), QCoreApplication.translate("NodeDetailsPopup", u"Pickup", None))
        self.teleporter_editable_check.setText(QCoreApplication.translate("NodeDetailsPopup", u"Randomizable?", None))
        self.teleporter_destination_group.setTitle(QCoreApplication.translate("NodeDetailsPopup", u"World/Area Selection", None))
        self.teleporter_scan_asset_id_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Scan asset id:", None))
        self.teleporter_vanilla_name_edit.setText(QCoreApplication.translate("NodeDetailsPopup", u"Keep name when vanilla?", None))
        self.teleporter_instance_id_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Instance id:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_teleporter), QCoreApplication.translate("NodeDetailsPopup", u"Teleporter", None))
        self.event_resource_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Event:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_event), QCoreApplication.translate("NodeDetailsPopup", u"Event", None))
        self.translator_gate_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Gate Index", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_translator_gate), QCoreApplication.translate("NodeDetailsPopup", u"Translator Gate", None))
        self.logbook_extra_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Extra:", None))
        self.lore_type_combo.setItemText(0, QCoreApplication.translate("NodeDetailsPopup", u"Luminoth Lore", None))
        self.lore_type_combo.setItemText(1, QCoreApplication.translate("NodeDetailsPopup", u"Luminoth Warrior", None))
        self.lore_type_combo.setItemText(2, QCoreApplication.translate("NodeDetailsPopup", u"Pirate Lore", None))
        self.lore_type_combo.setItemText(3, QCoreApplication.translate("NodeDetailsPopup", u"Sky Temple Key Hint", None))

        self.logbook_string_asset_id_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"String asset id", None))
        self.lore_type_label.setText(QCoreApplication.translate("NodeDetailsPopup", u"Lore type:", None))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_logbook), QCoreApplication.translate("NodeDetailsPopup", u"Logbook", None))
        self.player_ship_unlocked_button.setText(QCoreApplication.translate("NodeDetailsPopup", u"Edit unlocked by", None))
        self.player_ship_unlocked_group.setTitle("")
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_player_ship), QCoreApplication.translate("NodeDetailsPopup", u"Player Ship", None))
    # retranslateUi

