from PySide2 import QtCore, QtGui, QtWidgets, shiboken2 
import itasca



dockWidget = itasca.dockWidget("Demo GUI","",True)
dockWidget = shiboken2.wrapInstance(int(dockWidget),QtWidgets.QDockWidget)
widget = dockWidget.widget()


class Window(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.setWindowTitle(self.tr("Demo GUI"))

        verticalGroupBox = QtWidgets.QGroupBox("Settings")
        layout1 = QtWidgets.QVBoxLayout()
        ballLimit = 10000
        msg = "Number of balls (between {} and {}):"
        labelBalls = QtWidgets.QLabel(msg.format(0, ballLimit));
        layout1.addWidget(labelBalls)
        spinBox = QtWidgets.QSpinBox(self)
        spinBox.setRange(0, ballLimit)
        spinBox.setValue(1000)
        layout1.addWidget(spinBox)
        verticalGroupBox.setLayout(layout1)
        mainLayout.addWidget(verticalGroupBox)

        horizontalGroupBox = QtWidgets.QGroupBox("Actions")
        layout = QtWidgets.QHBoxLayout()
        buttons = []
        for i in range(4):
            button = QtWidgets.QPushButton("Button %d" % (i + 1))
            layout.addWidget(button)
            buttons.append(button)
        horizontalGroupBox.setLayout(layout)
        mainLayout.addWidget(horizontalGroupBox)

        #change the name of the first button to new and connect to a command
        buttons[0].setText("New")
        def onButton0():
            itasca.command("model new")
        buttons[0].clicked.connect(onButton0)

        #change the names of the later buttons
        buttons[1].setText("Domain")
        def onButton1():
            itasca.command("model domain extent -10 10")
        buttons[1].clicked.connect(onButton1)

        buttons[2].setText("Generate Balls")
        def onButton2():
            nballs = spinBox.value()
            try:
                itasca.command("ball generate number {}".format(nballs))
            except RuntimeError as error:
                warning_box = QtWidgets.QMessageBox(main)
                msg = "A PFC error has occurred: {}"
                warning_box.setText(msg.format(error))
                warning_box.show()
        buttons[2].clicked.connect(onButton2)

        buttons[3].setText("Show Balls")
        def onButton3():
            itasca.command('''
                plot create
                plot clear
                plot active on
                plot background 'white'
                plot item create ball
                plot show''')
        buttons[3].clicked.connect(onButton3)



widget.layout().addWidget(Window())
dockWidget.show()
dockWidget.raise_()

