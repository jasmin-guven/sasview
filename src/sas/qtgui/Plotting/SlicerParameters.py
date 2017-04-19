"""
Allows users to modify the box slicer parameters.
"""
import numpy
import functools
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtWebKit

# Local UI
from sas.qtgui.Plotting.UI.SlicerParametersUI import Ui_SlicerParametersUI

class SlicerParameters(QtGui.QDialog, Ui_SlicerParametersUI):
    """
    Interaction between the QTableView and the underlying model,
    passed from a slicer instance.
    """
    close_signal = QtCore.pyqtSignal()
    def __init__(self, model=None, validate_method=None):
        super(SlicerParameters, self).__init__()

        self.setupUi(self)

        assert isinstance(model, QtGui.QStandardItemModel)

        self.model = model
        self.validate_method = validate_method

        # Define a proxy model so cell enablement can be finegrained.
        self.proxy = ProxyModel(self)
        self.proxy.setSourceModel(self.model)

        # Set the proxy model for display in the Table View.
        self.lstParams.setModel(self.proxy)

        # Disallow edit of the parameter name column.
        self.lstParams.model().setColumnReadOnly(0, True)

        # Specify the validator on the parameter value column.
        self.delegate = EditDelegate(self, validate_method=self.validate_method)
        self.lstParams.setItemDelegate(self.delegate)
        self.delegate.refocus_signal.connect(self.onFocus)

        # Display Help on clicking the button
        self.buttonBox.button(QtGui.QDialogButtonBox.Help).clicked.connect(self.onHelp)

        # Close doesn't trigger closeEvent automatically, so force it
        self.buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(functools.partial(self.closeEvent, None))

        # Disable row number display
        self.lstParams.verticalHeader().setVisible(False)
        self.lstParams.setAlternatingRowColors(True)
        self.lstParams.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)

        # Header properties for nicer display
        header = self.lstParams.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.Stretch)
        header.setStretchLastSection(True)

    def onFocus(self, row, column):
        """ Set the focus on the cell (row, column) """
        selection_model = self.lstParams.selectionModel()
        selection_model.select(self.model.index(row, column), QtGui.QItemSelectionModel.Select)
        self.lstParams.setSelectionModel(selection_model)
        self.lstParams.setCurrentIndex(self.model.index(row, column))

    def setModel(self, model):
        """ Model setter """
        self.model = model
        self.proxy.setSourceModel(self.model)

    def closeEvent(self, event):
        """
        Overwritten close widget method in order to send the close
        signal to the parent.
        """
        self.close_signal.emit()
        if event:
            event.accept()

    def onHelp(self):
        """
        Display generic data averaging help
        """
        location = "docs/sphinx-docs/build/html" + \
            "/user/sasgui/guiframe/graph_help.html#d-data-averaging"
        self.helpView = QtWebKit.QWebView()
        self.helpView.load(QtCore.QUrl(location))
        self.helpView.show()


class ProxyModel(QtGui.QIdentityProxyModel):
    """
    Trivial proxy model with custom column edit flag
    """
    def __init__(self, parent=None):
        super(ProxyModel, self).__init__(parent)
        self._columns = set()

    def columnReadOnly(self, column):
        '''Returns True if column is read only, false otherwise'''
        return column in self._columns

    def setColumnReadOnly(self, column, readonly=True):
        '''Add/removes a column from the readonly list'''
        if readonly:
            self._columns.add(column)
        else:
            self._columns.discard(column)

    def flags(self, index):
        '''Sets column flags'''
        flags = super(ProxyModel, self).flags(index)
        if self.columnReadOnly(index.column()):
            flags &= ~QtCore.Qt.ItemIsEditable
        return flags

class PositiveDoubleEditor(QtGui.QLineEdit):
    # a signal to tell the delegate when we have finished editing
    editingFinished = QtCore.Signal()

    def __init__(self, parent=None):
            # Initialize the editor object
            super(PositiveDoubleEditor, self).__init__(parent)
            self.setAutoFillBackground(True)
            validator = QtGui.QDoubleValidator()
            # Don't use the scientific notation, cause 'e'.
            validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

            self.setValidator(validator)

    def focusOutEvent(self, event):
            # Once focus is lost, tell the delegate we're done editing
            self.editingFinished.emit()


class EditDelegate(QtGui.QStyledItemDelegate):
    refocus_signal = QtCore.pyqtSignal(int, int)
    def __init__(self, parent=None, validate_method=None):
        super(EditDelegate, self).__init__(parent)
        self.editor = None
        self.index = None
        self.validate_method = validate_method

    def createEditor(self, parent, option, index):
        # Creates and returns the custom editor object we will use to edit the cell
        if not index.isValid():
            return 0

        result = index.column()
        if result==1:
                self.editor = PositiveDoubleEditor(parent)
                self.index = index
                return self.editor
        else:
                return QtGui.QStyledItemDelegate.createEditor(self, parent, option, index)

    def setModelData(self, editor, model, index):
        """
        Custom version of the model update, rejecting bad values
        """
        self.index = index

        # Find out the changed parameter name and proposed value
        new_value = self.editor.text().toFloat()[0]
        param_name = str(model.sourceModel().item(index.row(),0).text())

        validated = True
        if self.validate_method:
            # Validate the proposed value in the slicer
            value_accepted = self.validate_method(param_name, new_value)

        if value_accepted:
            # Update the model only if value accepted
            return super(EditDelegate, self).setModelData(editor, model, index)          