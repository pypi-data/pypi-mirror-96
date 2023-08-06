import pkg_resources
import traceback as tb

from PyQt5 import uic, QtCore, QtWidgets

from ...api import CKANAPI, APIKeyError
from ..tools import show_wait_cursor


class PreferencesDialog(QtWidgets.QMainWindow):
    show_server = QtCore.pyqtSignal()
    show_user = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        """Create a new window for preferences
        """
        super(PreferencesDialog, self).__init__(parent)
        path_ui = pkg_resources.resource_filename(
            "dcoraid.gui.preferences", "dlg_preferences.ui")
        uic.loadUi(path_ui, self)

        self.setWindowTitle("DCOR-Aid Preferences")
        self.show_server.connect(self.on_show_server)
        self.show_user.connect(self.on_show_user)
        self.tabWidget.currentChanged.connect(self.on_tab_changed)
        self.toolButton_user_update.clicked.connect(self.on_update_user)
        self.toolButton_server_update.clicked.connect(self.on_update_server)
        self.toolButton_api_key_purge.clicked.connect(self.on_api_key_purge)
        self.toolButton_eye.clicked.connect(self.on_toggle_api_password_view)

        self.settings = QtCore.QSettings()
        # hidden initially
        self.hide()

    def ask_change_server_or_api_key(self):
        """Ask user whether he really wants to change things

        ...because it implies a restart of DCOR-Aid.
        """
        button_reply = QtWidgets.QMessageBox.question(
            self,
            'DCOR-Aid restart required',
            "Changing the server or API key requires a restart of "
            + "DCOR-Aid. If you choose 'No', then the original server "
            + "and API key are NOT changed. Do you really want to quit "
            + "DCOR-Aid?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if button_reply == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    @QtCore.pyqtSlot()
    def on_toggle_api_password_view(self):
        cur_em = self.lineEdit_api_key.echoMode()
        if cur_em == QtWidgets.QLineEdit.Normal:
            new_em = QtWidgets.QLineEdit.PasswordEchoOnEdit
        else:
            new_em = QtWidgets.QLineEdit.Normal
        self.lineEdit_api_key.setEchoMode(new_em)

    @QtCore.pyqtSlot()
    def on_api_key_purge(self):
        if self.ask_change_server_or_api_key():
            self.settings.remove("auth/api key")
            QtWidgets.QApplication.quit()

    @QtCore.pyqtSlot()
    def on_show_server(self):
        self.comboBox_server.clear()
        for server in self.settings.value("server list",
                                          ["dcor.mpl.mpg.de"]):
            self.comboBox_server.addItem(server)
        self.comboBox_server.setCurrentText(
            self.settings.value("auth/server", "dcor.mpl.mpg.de"))
        self.lineEdit_api_key.setText(self.settings.value("auth/api key", ""))
        self.tabWidget.setCurrentIndex(0)  # server settings
        self.lineEdit_api_key.setEchoMode(
            QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.show()
        self.activateWindow()

    @QtCore.pyqtSlot()
    @show_wait_cursor
    def on_show_user(self):
        api = CKANAPI(
            server=self.settings.value("auth/server", "dcor.mpl.mpg.de"),
            api_key=self.settings.value("auth/api key", ""))
        try:
            user_dict = api.get_user_dict()
        except (ConnectionError, APIKeyError):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("No connection or wrong server or invalid API key!")
            msg.setWindowTitle("Warning")
            msg.setDetailedText(tb.format_exc())
            msg.exec_()
            self.on_show_server()
        else:
            self.lineEdit_user_id.setText(user_dict["name"])
            self.lineEdit_user_name.setText(user_dict["fullname"])
            self.lineEdit_user_email.setText(user_dict["email"])
            self.plainTextEdit_user_about.setPlainText(user_dict["about"])
            self.show()
            self.activateWindow()

    @QtCore.pyqtSlot(int)
    def on_tab_changed(self, index):
        if index == 0:
            self.on_show_server()
        elif index == 1:
            self.on_show_user()

    @QtCore.pyqtSlot()
    @show_wait_cursor
    def on_update_user(self):
        api = CKANAPI(
            server=self.settings.value("auth/server", "dcor.mpl.mpg.de"),
            api_key=self.settings.value("auth/api key", ""))
        try:
            user_dict = api.get_user_dict()
        except (ConnectionError, APIKeyError):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("No connection or wrong server or invalid API key!")
            msg.setWindowTitle("Warning")
            msg.setDetailedText(tb.format_exc())
            msg.exec_()
            self.on_show_server()
        update_dict = {}
        update_dict["id"] = user_dict["id"]
        update_dict["fullname"] = self.lineEdit_user_name.text()
        update_dict["email"] = self.lineEdit_user_email.text()
        update_dict["about"] = self.plainTextEdit_user_about.toPlainText()
        api.post("user_update", data=update_dict)

    @QtCore.pyqtSlot()
    @show_wait_cursor
    def on_update_server(self):
        old_server = self.settings.value("auth/server", "")
        old_api_key = self.settings.value("auth/api key", "")
        api_key = self.lineEdit_api_key.text()
        api_key = "".join([ch for ch in api_key if ch in "0123456789abcdef-"])
        server = self.comboBox_server.currentText().strip()
        # Test whether that works
        try:
            api = CKANAPI(server=server, api_key=api_key)
            api.get_user_dict()
        except BaseException:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Bad server / API key combination!")
            msg.setWindowTitle("Error")
            msg.setDetailedText(tb.format_exc())
            msg.exec_()
        else:
            if old_server != server or old_api_key != api_key:
                if self.ask_change_server_or_api_key():
                    self.settings.setValue("auth/api key", api_key)
                    self.settings.setValue("auth/server", server)
                    QtWidgets.QApplication.quit()
