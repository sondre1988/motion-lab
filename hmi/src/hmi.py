from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import pyqtgraph as pg
import time
import pyads
import numpy as np
import ctypes
from ctypes import sizeof
import json
from scipy.optimize import curve_fit

from src.classes import RealTimePlot, RealTimeBar, WaveSpectrum
from src.datastructures import TxHmi, RxHmi
from src.gui import Ui_main
from src.opengl import MotionLabVisualizer


# Motionlab pybind module
from lib import motionlab as ml

# Background color pyqtgraph
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)

# PyQt signal
class Signals(QObject):
    a = pyqtSignal(float)
    b = pyqtSignal(int)
    c = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Signals, self).__init__(parent)

        # self.a.emit()

# Signals class
signals = Signals()

plc2 = pyads.Connection('192.168.90.150.1.1', 851)




@plc2.notification(pyads.PLCTYPE_REAL)
def callback(handle, name, timestamp, value):
    # Emit value to signal class
    signals.a.emit(value)
    
@plc2.notification(pyads.PLCTYPE_DINT)
def callback2(handle, name, timestamp, value):
    # Emit value to signal class
    signals.b.emit(value)

@plc2.notification(pyads.PLCTYPE_ARR_LREAL(2))
def callback3(handle, name, timestamp, value):
    # Emit value to signal class
    print(value)
    signals.c.emit(value)



class GUI(QMainWindow, Ui_main):
    _ampEM1500 = []


    def __init__(self):
        super(GUI, self).__init__()
        Ui_main.__init__(self)
        self.setupUi(self)

        # Start ADS communications
        self.plc = pyads.Connection('192.168.90.150.1.1', 851)
        self.plc.open()

        plc2.open()
        plc2.add_device_notification(
            'MAIN.test2',
            pyads.NotificationAttrib(4),
            callback
        )

        plc2.add_device_notification(
            'MAIN.test',
            pyads.NotificationAttrib(sizeof(pyads.PLCTYPE_DINT)),
            callback2
        )

        plc2.add_device_notification(
            'MAIN.phi',
            pyads.NotificationAttrib(sizeof(pyads.PLCTYPE_ARR_LREAL(2))),
            callback3
        )

        signals.a.connect(self.emitTest)
        signals.b.connect(self.emitTest2)
        signals.c.connect(self.emitTest3)

        # Setup plotEM1500
        self.plotEM1500_A = RealTimePlot(self._plotEM1500.addPlot())
        self.plotEM1500_A.plot.setLabel('left', 'Position', 'm')
        self.plotEM1500_A.plot.setYRange(-0.5, 0.5)
        self.plotEM1500_A.add_curves(['r', 'g', 'b'], ['Surge', 'Sway', 'Heave'])
        self._plotEM1500.nextRow()
        self.plotEM1500_B = RealTimePlot(self._plotEM1500.addPlot())
        self.plotEM1500_B.plot.setLabel('left', 'Angle', 'deg')
        self.plotEM1500_B.plot.setYRange(-6.0, 6.0)
        self.plotEM1500_B.add_curves(['r', 'g', 'b'], ['Roll', 'Pitch', 'Yaw'])

        self.plotEM8000_A = RealTimePlot(self._plotEM8000.addPlot())
        self.plotEM8000_A.plot.setLabel('left', 'Position', 'm')
        self.plotEM8000_A.plot.setYRange(-0.5, 0.5)
        self.plotEM8000_A.add_curves(['r', 'g', 'b'], ['Surge', 'Sway', 'Heave'])
        self._plotEM8000.nextRow()
        self.plotEM8000_B = RealTimePlot(self._plotEM8000.addPlot())
        self.plotEM8000_B.plot.setLabel('left', 'Angle', 'deg')
        self.plotEM8000_B.plot.setYRange(-6.0, 6.0)
        self.plotEM8000_B.add_curves(['r', 'g', 'b'], ['Roll', 'Pitch', 'Yaw'])
        
        # Sine wave parameters
        self._ampEM1500.append(self._ampEM1500_0)
        self._ampEM1500.append(self._ampEM1500_1)
        self._ampEM1500.append(self._ampEM1500_2)
        self._ampEM1500.append(self._ampEM1500_3)
        self._ampEM1500.append(self._ampEM1500_4)
        self._ampEM1500.append(self._ampEM1500_5)
        

        self.connectTabStewart('EM1500')
        self.connectTabStewart('EM8000')

        # Calling the initUI function
        self.initUI()

    @pyqtSlot(float)
    def emitTest(self, value):
        print('Emitted value is: '+ str(value))
        
    @pyqtSlot(int)
    def emitTest2(self, value):
        print('Emitted value is: '+ str(value))

    @pyqtSlot(object)
    def emitTest3(self, value):
        print('Emitted value is: '+ str(value))

    def connectTabStewart(self, name):
        if name == 'EM1500':
            maxSurge = 0.2
            maxSway = 0.2
            maxHeave = 0.6
            maxRoll = 5.0/180*np.pi
            maxPitch = 5.0/180*np.pi
            maxYaw = 5.0/180*np.pi
 
        elif name == 'EM8000':
            maxSurge = 0.4
            maxSway = 0.4
            maxHeave = 0.6
            maxRoll = 10.0/180*np.pi
            maxPitch = 10.0/180*np.pi
            maxYaw = 10.0/180*np.pi

        # FB_StewartInterface.eMode
        eval('self._eMode' + name).currentIndexChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.eMode',
                    eval('self._eMode' + name).currentIndex(),
                    pyads.PLCTYPE_USINT
                ),
                self.toggleSineSettings(name, eval('self._eMode' + name).currentIndex())
            )
        )

        # FB_StewartInterface.bStop
        eval('self._bStop' + name).clicked.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.bStop',
                    True,
                    pyads.PLCTYPE_BOOL
                )
            )
        )

        # FB_StewartInterface.bReset
        eval('self._bReset' + name).clicked.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.bReset',
                    True,
                    pyads.PLCTYPE_BOOL
                ),
                eval('self._eMode' + name).setCurrentIndex(0)
            )
        )

        # FB_StewartInterface.sineAmplitude[0]
        eval('self._amp' + name + '_0').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[0]',
                    eval('self._amp' + name + '_0').value(),
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_0').setMinimum(0.0)
        eval('self._amp' + name + '_0').setMaximum(maxSurge)
        eval('self._amp' + name + '_0').setSingleStep(0.01)
        
        # FB_StewartInterface.sineAmplitude[1]
        eval('self._amp' + name + '_1').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[1]',
                    eval('self._amp' + name + '_1').value(),
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_1').setMinimum(0.0)
        eval('self._amp' + name + '_1').setMaximum(maxSway)
        eval('self._amp' + name + '_1').setSingleStep(0.01)

        # FB_StewartInterface.sineAmplitude[2]
        eval('self._amp' + name + '_2').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[2]',
                    eval('self._amp' + name + '_2').value(),
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_2').setMinimum(0.0)
        eval('self._amp' + name + '_2').setMaximum(maxHeave)
        eval('self._amp' + name + '_2').setSingleStep(0.01)

        # FB_StewartInterface.sineAmplitude[3]
        eval('self._amp' + name + '_3').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[3]',
                    eval('self._amp' + name + '_3').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_3').setMinimum(0.0)
        eval('self._amp' + name + '_3').setMaximum(maxRoll/np.pi*180.0)
        eval('self._amp' + name + '_3').setSingleStep(0.01)

        # FB_StewartInterface.sineAmplitude[4]
        eval('self._amp' + name + '_4').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[4]',
                    eval('self._amp' + name + '_4').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_4').setMinimum(0.0)
        eval('self._amp' + name + '_4').setMaximum(maxPitch/np.pi*180.0)
        eval('self._amp' + name + '_4').setSingleStep(0.01)

        # FB_StewartInterface.sineAmplitude[5]
        eval('self._amp' + name + '_5').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineAmplitude[5]',
                    eval('self._amp' + name + '_5').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._amp' + name + '_5').setMinimum(0.0)
        eval('self._amp' + name + '_5').setMaximum(maxYaw/np.pi*180.0)
        eval('self._amp' + name + '_5').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[0]
        eval('self._freq' + name + '_0').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[0]',
                    eval('self._freq' + name + '_0').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_0').setMinimum(0.0)
        eval('self._freq' + name + '_0').setMaximum(1.0)
        eval('self._freq' + name + '_0').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[1]
        eval('self._freq' + name + '_1').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[1]',
                    eval('self._freq' + name + '_1').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_1').setMinimum(0.0)
        eval('self._freq' + name + '_1').setMaximum(1.0)
        eval('self._freq' + name + '_1').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[2]
        eval('self._freq' + name + '_2').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[2]',
                    eval('self._freq' + name + '_2').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_2').setMinimum(0.0)
        eval('self._freq' + name + '_2').setMaximum(1.0)
        eval('self._freq' + name + '_2').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[3]
        eval('self._freq' + name + '_3').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[3]',
                    eval('self._freq' + name + '_3').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_3').setMinimum(0.0)
        eval('self._freq' + name + '_3').setMaximum(1.0)
        eval('self._freq' + name + '_3').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[4]
        eval('self._freq' + name + '_4').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[4]',
                    eval('self._freq' + name + '_4').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_4').setMinimum(0.0)
        eval('self._freq' + name + '_4').setMaximum(1.0)
        eval('self._freq' + name + '_4').setSingleStep(0.01)

        # FB_StewartInterface.sineOmega[5]
        eval('self._freq' + name + '_5').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sineOmega[5]',
                    eval('self._freq' + name + '_5').value()*2.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._freq' + name + '_5').setMinimum(0.0)
        eval('self._freq' + name + '_5').setMaximum(1.0)
        eval('self._freq' + name + '_5').setSingleStep(0.01)

        # FB_StewartInterface.sinePhase[0]
        eval('self._phase' + name + '_0').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[0]',
                    eval('self._phase' + name + '_0').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_0').setMinimum(0)
        eval('self._phase' + name + '_0').setMaximum(360)
        eval('self._phase' + name + '_0').setSingleStep(5)

         # FB_StewartInterface.sinePhase[1]
        eval('self._phase' + name + '_1').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[1]',
                    eval('self._phase' + name + '_1').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_1').setMinimum(0)
        eval('self._phase' + name + '_1').setMaximum(360)
        eval('self._phase' + name + '_1').setSingleStep(5)

         # FB_StewartInterface.sinePhase[2]
        eval('self._phase' + name + '_2').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[2]',
                    eval('self._phase' + name + '_2').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_2').setMinimum(0)
        eval('self._phase' + name + '_2').setMaximum(360)
        eval('self._phase' + name + '_2').setSingleStep(5)

         # FB_StewartInterface.sinePhase[3]
        eval('self._phase' + name + '_3').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[3]',
                    eval('self._phase' + name + '_3').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_3').setMinimum(0)
        eval('self._phase' + name + '_3').setMaximum(360)
        eval('self._phase' + name + '_3').setSingleStep(5)

         # FB_StewartInterface.sinePhase[4]
        eval('self._phase' + name + '_4').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[4]',
                    eval('self._phase' + name + '_4').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_4').setMinimum(0)
        eval('self._phase' + name + '_4').setMaximum(360)
        eval('self._phase' + name + '_4').setSingleStep(5)

         # FB_StewartInterface.sinePhase[5]
        eval('self._phase' + name + '_5').valueChanged.connect(
            lambda: (
                self.plc.write_by_name(
                    'MAIN.' + name + '.sinePhase[5]',
                    eval('self._phase' + name + '_5').value()/180.0*np.pi,
                    pyads.PLCTYPE_LREAL
                )
            )
        )
        eval('self._phase' + name + '_5').setMinimum(0)
        eval('self._phase' + name + '_5').setMaximum(360)
        eval('self._phase' + name + '_5').setSingleStep(5)


    def toggleSineSettings(self, name, eMode):
        
        eval('self._amp' + name + '_0').setDisabled(eMode == 3)
        eval('self._amp' + name + '_1').setDisabled(eMode == 3)
        eval('self._amp' + name + '_2').setDisabled(eMode == 3)
        eval('self._amp' + name + '_3').setDisabled(eMode == 3)
        eval('self._amp' + name + '_4').setDisabled(eMode == 3)
        eval('self._amp' + name + '_5').setDisabled(eMode == 3)

        eval('self._freq' + name + '_0').setDisabled(eMode == 3)
        eval('self._freq' + name + '_1').setDisabled(eMode == 3)
        eval('self._freq' + name + '_2').setDisabled(eMode == 3)
        eval('self._freq' + name + '_3').setDisabled(eMode == 3)
        eval('self._freq' + name + '_4').setDisabled(eMode == 3)
        eval('self._freq' + name + '_5').setDisabled(eMode == 3)

        eval('self._phase' + name + '_0').setDisabled(eMode == 3)
        eval('self._phase' + name + '_1').setDisabled(eMode == 3)
        eval('self._phase' + name + '_2').setDisabled(eMode == 3)
        eval('self._phase' + name + '_3').setDisabled(eMode == 3)
        eval('self._phase' + name + '_4').setDisabled(eMode == 3)
        eval('self._phase' + name + '_5').setDisabled(eMode == 3)


    # Function that initialize all the objects in the UI
    def initUI(self):
        

        

        try:
            self.plc.read_state()
            self.plc_active = True
        except pyads.ADSError:
            self.plc_active = False

        # Xbox controller
        self.xbox = ml.XboxController()
        self.xbox.start()

        # Default function values
        self.waveSpectrumDP1 = WaveSpectrum()
        self.waveSpectrumDP2 = WaveSpectrum()

        # Setup of the different plots
        self.plot_setup()

        if self.plc_active:
            # Timer function for plot update
            self.timerFast = QTimer()
            self.timerFast.timeout.connect(self.updateFast)
            self.timerFast.start(50)

            # SLow timer for staus updates
            self.timerSlow = QTimer()
            self.timerSlow.timeout.connect(self.updateSlow)
            self.timerSlow.start(2000)

            self.EM8000_wave()

        # OpenGL
        text = open('./src/calib.json').read()
        calib = json.loads(text)
        self.visualizer = MotionLabVisualizer(calib)

        # Read inition time
        self.tStart = time.time()

        # Misc
        self.fastCounter = 0

        # Connect the interaction functionality of the GUI
        self.ui_connect()

        # Show UI
        self.show()
    

    # EM8000 Wave Settings
    def EM8000_wave(self):
            # Current wave spectrum data
            Hs = self.waveSpectrumDP1.Hs
            T1 = self.waveSpectrumDP1.T1
            spec = self.waveSpectrumDP1.spec

            try:
                objectName = self.sender().objectName()
                if objectName == "EM8000_wave_spectra":
                    spec = str(self.sender().currentText())

                elif objectName == "EM8000_wave_height":
                    Hs = int(self.sender().text())

                elif objectName == "EM8000_wave_period":
                    T1 = int(self.sender().text())
 
            except AttributeError:
                pass

            # Update wave spectrum and plot
            self.waveSpectrumDP1.calculate(Hs, T1, spec)

            self.DP1_spectrum.plot.setYRange(0, max(self.waveSpectrumDP1.S) + 5)
            self.DP1_spectrum.static_plot(self.waveSpectrumDP1.w,
                    [self.waveSpectrumDP1.S, self.waveSpectrumDP1.Slin]
                )

            # Write to TcCOM object containg WaveSimulator
            self.plc.write_by_name('MAIN.w0', 
                    self.waveSpectrumDP1.w0, pyads.PLCTYPE_LREAL
                )

            self.plc.write_by_name('MAIN.sigma', 
                    self.waveSpectrumDP1.sigma, pyads.PLCTYPE_LREAL
                )

            self.plc.write_by_name('MAIN.lambda', 
                    self.waveSpectrumDP1.Lambda, pyads.PLCTYPE_LREAL
                )
    

    # Plot setup
    def plot_setup(self):

        # Plot time range setting
        self.time_range = 20

        # Ship Simulator tab:
        #------------------------------------------------------#

        # EM8000
        self.DP1_1 = RealTimePlot(self.DP1_SimStates.addPlot())
        self.DP1_1.plot.setLabel('left', 'Position', 'm')
        self.DP1_1.plot.setYRange(-0.5, 0.5)
        self.DP1_1.add_curves(['r', 'g', 'b'], ['Surge', 'Sway', 'Heave'])
        self.DP1_SimStates.nextRow()
        self.DP1_2 = RealTimePlot(self.DP1_SimStates.addPlot())
        self.DP1_2.plot.setLabel('left', 'Angle', 'deg')
        self.DP1_2.plot.setYRange(-6.0, 6.0)
        self.DP1_2.add_curves(['r', 'g', 'b'], ['Roll', 'Pitch', 'Yaw'])

        self.DP1_spectrum = RealTimePlot(self.DP1_wavespectrum.addPlot())
        self.DP1_spectrum.plot.setLabel('left', 'Spectrum Energy', '-')
        self.DP1_spectrum.plot.setLabel('bottom', 'Wave Period', 'rad/s')
        self.DP1_spectrum.plot.setYRange(0, 30)
        self.DP1_spectrum.add_curves(['r','b'], ['Wave Spectrum', 'Linear Spectrum'])

        # EM1500
        self.DP2_1 = RealTimePlot(self.DP2_SimStates.addPlot())
        self.DP2_1.plot.setLabel('left', 'Position', 'm')
        self.DP2_1.plot.setYRange(-0.5, 0.5)
        self.DP2_1.add_curves(['r', 'g', 'b'], ['Surge', 'Sway', 'Heave'])
        self.DP2_SimStates.nextRow()
        self.DP2_2 = RealTimePlot(self.DP2_SimStates.addPlot())
        self.DP2_2.plot.setLabel('left', 'Angle', 'deg')
        self.DP2_2.plot.setYRange(-6.0, 6.0)
        self.DP2_2.add_curves(['r', 'g', 'b'], ['Roll', 'Pitch', 'Yaw'])

        # Trending tab
        #------------------------------------------------------#
        self.EM1500_1 = RealTimePlot(self.EM1500_plot.addPlot())
        self.EM1500_1.plot.setYRange(-0.5, 0.5)
        self.EM1500_1.plot.setLabel('left', 'Position', 'm')
        self.EM1500_1.add_curves(['r', 'g', 'b', 'k', 'k', 'k'], ['Surge', 'Sway', 'Heave', 'Surge(MRU)', 'Sway(MRU)', 'Heave(MRU)'])
        # self.EM1500_1.add_curves(['r', 'g', 'b'], ['Surge', 'Sway', 'Heave'])
        self.EM1500_1.add_text_displays([
                self.EM1500_output_pos_x, 
                self.EM1500_output_pos_y, 
                self.EM1500_output_pos_z,
                self.MRU2_output_pos_x,
                self.MRU2_output_pos_y,
                self.MRU2_output_pos_z
            ])
        self.EM1500_plot.nextRow()
        self.EM1500_2 = RealTimePlot(self.EM1500_plot.addPlot())
        self.EM1500_2.plot.setYRange(-5, 5)
        self.EM1500_2.plot.setLabel('left', 'Angle', 'deg')
        # self.EM1500_2.add_curves(['r', 'g', 'b'], ['Roll', 'Pitch', 'Yaw'])
        self.EM1500_2.add_curves(['r', 'g', 'b', 'k', 'k', 'k'], ['Roll', 'Pitch', 'Yaw', 'Roll(MRU)', 'Pitch(MRU)', 'Yaw(MRU)'])
        self.EM1500_2.add_text_displays([
                self.EM1500_output_ang_r, 
                self.EM1500_output_ang_p, 
                self.EM1500_output_ang_y,
                self.MRU2_output_ang_r,
                self.MRU2_output_ang_p,
                self.MRU2_output_ang_y,
            ])
        
        self.EM8000_1 = RealTimePlot(self.EM8000_plot.addPlot())
        self.EM8000_1.plot.setYRange(-1, 1)
        self.EM8000_1.plot.setLabel('left', 'Position', 'm')
        self.EM8000_1.add_curves(['r', 'g', 'b', 'k', 'k', 'k'], ['Surge', 'Sway', 'Heave', 'Surge(MRU)', 'Sway(MRU)', 'Heave(MRU)'])
        self.EM8000_1.add_text_displays([
                self.EM8000_output_pos_x, 
                self.EM8000_output_pos_y, 
                self.EM8000_output_pos_z,
                self.MRU1_output_pos_x,
                self.MRU1_output_pos_y,
                self.MRU1_output_pos_z
            ])
        self.EM8000_plot.nextRow()
        self.EM8000_2 = RealTimePlot(self.EM8000_plot.addPlot())
        self.EM8000_2.plot.setLabel('left', 'Angle', 'deg')
        self.EM8000_2.plot.setYRange(-5, 5)
        self.EM8000_2.add_curves(['r', 'g', 'b', 'k', 'k', 'k'], ['Roll', 'Pitch', 'Yaw', 'Roll(MRU)', 'Pitch(MRU)', 'Yaw(MRU)'])
        self.EM8000_2.add_text_displays([
                self.EM8000_output_ang_r, 
                self.EM8000_output_ang_p, 
                self.EM8000_output_ang_y,
                self.MRU1_output_ang_r,
                self.MRU1_output_ang_p,
                self.MRU1_output_ang_y
            ])

        self.COMAU = RealTimePlot(self.COMAU_plot.addPlot())
        self.COMAU.plot.setYRange(-180, 180)
        self.COMAU.plot.setLabel('left', 'Angle', 'deg')
        self.COMAU.add_curves(['r', 'g', 'b', 'y', 'm', 'c'], ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'])
        self.COMAU.add_text_displays([
                self.COMAU_output_pos_j1, 
                self.COMAU_output_pos_j2, 
                self.COMAU_output_pos_j3,
                self.COMAU_output_pos_j4, 
                self.COMAU_output_pos_j5, 
                self.COMAU_output_pos_j6
            ])

        # Joint stroke bar indicators
        self.EM1500_bars = RealTimeBar()
        self.EM1500_bars.max_values = [0.395]*12
        self.EM1500_bars.bars = [
                self.EM1500_bar1_l1, 
                self.EM1500_bar1_l2, 
                self.EM1500_bar1_l3, 
                self.EM1500_bar1_l4, 
                self.EM1500_bar1_l5, 
                self.EM1500_bar1_l6,
                self.EM1500_bar2_l1, 
                self.EM1500_bar2_l2, 
                self.EM1500_bar2_l3, 
                self.EM1500_bar2_l4, 
                self.EM1500_bar2_l5, 
                self.EM1500_bar2_l6
            ]
        
        self.EM8000_bars = RealTimeBar()
        self.EM8000_bars.max_values = [0.776]*12
        self.EM8000_bars.bars = [
                self.EM8000_bar1_l1, 
                self.EM8000_bar1_l2, 
                self.EM8000_bar1_l3, 
                self.EM8000_bar1_l4, 
                self.EM8000_bar1_l5, 
                self.EM8000_bar1_l6,
                self.EM8000_bar2_l1, 
                self.EM8000_bar2_l2, 
                self.EM8000_bar2_l3, 
                self.EM8000_bar2_l4, 
                self.EM8000_bar2_l5, 
                self.EM8000_bar2_l6
            ]
        
        self.COMAU_bars = RealTimeBar()
        self.COMAU_bars.max_values = [180]*12
        self.COMAU_bars.bars = [
                self.COMAU_bar1_j1, 
                self.COMAU_bar1_j2, 
                self.COMAU_bar1_j3,
                self.COMAU_bar1_j4, 
                self.COMAU_bar1_j5, 
                self.COMAU_bar1_j6,
                self.COMAU_bar2_j1, 
                self.COMAU_bar2_j2, 
                self.COMAU_bar2_j3, 
                self.COMAU_bar2_j4, 
                self.COMAU_bar2_j5, 
                self.COMAU_bar2_j6
            ]

        # Xbox controller
        self.XBOX_bars = RealTimeBar()
        self.XBOX_bars.max_values = [1.0]*4
        self.XBOX_bars.bars = [
                self.XboxJoystickLeft_x,
                self.XboxJoystickLeft_y,
                self.XboxJoystickRight_x,
                self.XboxJoystickRight_y,
            ]

        # Pendel estimator related plots
        self.swingAnglesPlot = RealTimePlot(self.swingAnglesWidget.addPlot())
        self.swingAnglesPlot.plot.setYRange(-10, 10)
        self.swingAnglesPlot.plot.setLabel('left', 'Angle', 'deg')
        self.swingAnglesPlot.add_curves(['r', 'b'], ['phi[0]', 'phi[1]'])    

        self.swingVelocityPlot = RealTimePlot(self.swingVelocityWidget.addPlot())
        self.swingVelocityPlot.plot.setYRange(-20, 20)
        self.swingVelocityPlot.plot.setLabel('left', 'Angle', 'deg/s')
        self.swingVelocityPlot.add_curves(['r', 'b'], ['phi_t[0]', 'phi_t[1]'])

        self.dampingParamPlot = RealTimePlot(self.dampingParamPlotWidget.addPlot())
        self.dampingParamPlot.plot.setYRange(0, 0.5)
        self.dampingParamPlot.plot.setLabel('left', 'Damping', '-')
        self.dampingParamPlot.add_curves(['r'], ['c'])

        self.errorStatePlot = RealTimePlot(self.errorStatePlotWidget.addPlot())
        self.errorStatePlot.plot.setYRange(-0.1, 0.1)
        self.errorStatePlot.plot.setLabel('left', 'Error', 'm')
        self.errorStatePlot.add_curves(['r', 'g', 'b'], ['x', 'ey', 'ez'])

    # UI connections
    def ui_connect(self):
        # Interface Tab:
        #------------------------------------------------ ----------#
        # Connecting EM 8000 Interface-buttons to functions
        self.EM8000_settled_btn.clicked.connect(self.EM8000_settled)
        self.EM8000_neutral_btn.clicked.connect(self.EM8000_neutral)
        self.EM8000_engaged_btn.clicked.connect(self.EM8000_engaged)

        # Connecting EM 1500 Interface-buttons to functions
        self.EM1500_settled_btn.clicked.connect(self.EM1500_settled)
        self.EM1500_neutral_btn.clicked.connect(self.EM1500_neutral)
        self.EM1500_engaged_btn.clicked.connect(self.EM1500_engaged)

        # Connecting COMAU Interface-buttons to functions
        self.COMAU_settled_btn.clicked.connect(self.COMAU_settled)
        self.COMAU_engaged_btn.clicked.connect(self.COMAU_engaged)
        self.COMAU_engaged_fast_btn.clicked.connect(self.COMAU_engaged_fast)

        # Connecting SYSTEM Interface-buttons to functions
        self.SYSTEM_settled_btn.clicked.connect(self.SYSTEM_settled)
        self.SYSTEM_stop_btn.clicked.connect(self.SYSTEM_stop)

        # Plotting Tab:
        #----------------------------------------------------------#
        self.EM1500_plot_time_range.currentIndexChanged.connect(self.plot_time_axis_range)
        self.EM8000_plot_time_range.currentIndexChanged.connect(self.plot_time_axis_range)
        self.COMAU_plot_time_range.currentIndexChanged.connect(self.plot_time_axis_range)

        # Ship Simulator tab:
        #----------------------------------------------------------#
        self.EM8000_plot_time_range_ship.currentIndexChanged.connect(self.plot_time_axis_range)

        # Limit values for input
        self.validator_height = QIntValidator(1, 10)
        self.validator_period = QIntValidator(1, 20)

        self.EM8000_wave_height.setText(str(self.waveSpectrumDP1.Hs))
        self.EM8000_wave_height.setValidator(self.validator_height)

        self.EM8000_wave_period.setText(str(self.waveSpectrumDP1.T1))
        self.EM8000_wave_period.setValidator(self.validator_period)

        self.EM8000_wave_height.returnPressed.connect(self.EM8000_wave)
        self.EM8000_wave_period.returnPressed.connect(self.EM8000_wave)
        self.EM8000_wave_spectra.currentIndexChanged.connect(self.EM8000_wave)
        
        # Winch related
        self.winchSettled.clicked.connect(self.WINCH_settled)
        self.winchEngaged.clicked.connect(self.WINCH_engaged)
        self.winchEngagedFast.clicked.connect(self.WINCH_engaged_fast)
        self.winchOff.clicked.connect(self.WINCH_off)
        self.winchOn.clicked.connect(self.WINCH_on)


        # Controller System
        self.antiSwayPlotRange.currentIndexChanged.connect(self.plot_time_axis_range)

        self.btnActivateAntiSway.clicked.connect(self.activateAntiSway)
        self.btnDeactivateAntiSway.clicked.connect(self.deactivateAntiSway)
        self.btnResetAntiSway.clicked.connect(self.resetAntiSway)

        self.btnEnableMruEKF.clicked.connect(self.enableMruEKF)
        self.btnDisableMruEKF.clicked.connect(self.disableMruEKF)
        self.btnResetEKF.clicked.connect(self.resetPendulumEKF)

        self.btnEnableMruWinch.clicked.connect(self.enableMruWinchController)
        self.btnDisableMruWinch.clicked.connect(self.disableMruWinchController)

        self.btnEnableMruCM.clicked.connect(self.enableMruCM)
        self.btnDisableMruCM.clicked.connect(self.disableMruCM)

        # Show 3D visulaization of motion-lab
        self.show3dView.clicked.connect(self.visualizer.show)

    def updateSlow(self):
        if self.plc_active:
            # EM8000 activity
            if self.plc.read_by_name('MAIN.em8000.bActive', pyads.PLCTYPE_BOOL):
                self.activeEM8000.setCheckState(True)
            else:
                self.activeEM8000.setCheckState(False)
            
            # EM1500 activity
            if self.plc.read_by_name('MAIN.em1500.bActive', pyads.PLCTYPE_BOOL):
                self.activeEM1500.setCheckState(True)
            else:
                self.activeEM1500.setCheckState(False)

            # MRU1 activity
            if self.plc.read_by_name('MAIN.mru1.active', pyads.PLCTYPE_BOOL):
                self.activeMRU1.setCheckState(True)
            else:
                self.activeMRU1.setCheckState(False)

            # MRU2 activity
            if self.plc.read_by_name('MAIN.mru2.active', pyads.PLCTYPE_BOOL):
                self.activeMRU2.setCheckState(True)
            else:
                self.activeMRU2.setCheckState(False)

            # QTM activity
            if self.plc.read_by_name('MAIN.qtm.active', pyads.PLCTYPE_BOOL):
                self.activeQTM.setCheckState(True)
            else:
                self.activeQTM.setCheckState(False)

            # WINCH activity
            if self.plc.read_by_name('MAIN.winch.active', pyads.PLCTYPE_BOOL):
                self.activeWINCH.setCheckState(True)
            else:
                self.activeWINCH.setCheckState(False)

            # COMAU activity
            if self.plc.read_by_name('MAIN.comau.active', pyads.PLCTYPE_BOOL):
                self.activeCOMAU.setCheckState(True)
            else:
                self.activeCOMAU.setCheckState(False)

            # LEICA Activity
            if self.plc.read_by_name('MAIN.at960.active', pyads.PLCTYPE_BOOL):
                self.activeLEICA.setCheckState(True)
            else:
                self.activeLEICA.setCheckState(False)

        # XBOX controller activity
        if self.xbox.is_connected():
            self.activeXBOX.setCheckState(True)
        else:
            self.activeXBOX.setCheckState(False)

    # Update fastData
    def updateFast(self):
        # Update fast counter
        self.fastCounter = self.fastCounter + 1

        # Update HMI data
        if self.plc_active:
            txHmi = self.plc.read_by_name('MAIN.txHmi', TxHmi)

        rxHmi = RxHmi()

        rxHmi.counter = self.fastCounter
        rxHmi.xboxLeftX = self.xbox.left.x
        rxHmi.xboxLeftY = self.xbox.left.y
        rxHmi.xboxRightX = self.xbox.right.x
        rxHmi.xboxRightY = self.xbox.right.y
        rxHmi.xboxLT = self.xbox.LT
        rxHmi.xboxRT = self.xbox.RT



        if self.xbox.A:
            self.activateAntiSway()

        if self.xbox.B:
            self.deactivateAntiSway()

        # Update visualizer data
        self.visualizer.setTxHmi(txHmi)

        if self.visualizer.isVisible():
            self.visualizer.update()
        
        rxBuffer = bytearray(rxHmi)
        rxSize = len(rxBuffer)*pyads.PLCTYPE_BYTE
        self.plc.write_by_name('MAIN.rxHmi', rxBuffer, rxSize)
        
        self.t = time.time() - self.tStart

        # Plot EM1500
        plotModeEM1500 = self._plotModeEM1500.currentIndex()
        if plotModeEM1500 == 0:
            etaEM1500 = txHmi.em1500.etaSim

        elif plotModeEM1500 == 1:
            etaEM1500 = txHmi.em1500.etaSine

        else:
            etaEM1500 = np.zeros(6)

        self.plotEM1500_A.update(self.t, 
            [
                etaEM1500[0],
                etaEM1500[1],
                etaEM1500[2],
            ]
        )

        self.plotEM1500_B.update(self.t, 
            [
                etaEM1500[3]/np.pi*180,
                etaEM1500[4]/np.pi*180,
                etaEM1500[5]/np.pi*180,
            ]
        )

        # Plot EM8000
        plotModeEM8000 = self._plotModeEM8000.currentIndex()
        if plotModeEM8000 == 0:
            etaEM8000 = txHmi.em8000.etaSim

        elif plotModeEM8000 == 1:
            etaEM8000 = txHmi.em8000.etaSine

        else:
            etaEM8000 = np.zeros(6)

        self.plotEM8000_A.update(self.t, 
            [
                etaEM8000[0],
                etaEM8000[1],
                etaEM8000[2],
            ]
        )

        self.plotEM8000_B.update(self.t, 
            [
                etaEM8000[3]/np.pi*180,
                etaEM8000[4]/np.pi*180,
                etaEM8000[5]/np.pi*180,
            ]
        )

        ######################################################
    
        self.DP1_1.time_range = self.time_range
        self.DP1_1.update(self.t, [
                txHmi.em8000.etaSim[0],
                txHmi.em8000.etaSim[1],
                txHmi.em8000.etaSim[2]
            ])
        
        self.DP1_2.time_range = self.time_range
        self.DP1_2.update(self.t, [
                txHmi.em8000.etaSim[3]/np.pi*180.0,
                txHmi.em8000.etaSim[4]/np.pi*180.0,
                txHmi.em8000.etaSim[5]/np.pi*180.0
            ])
 
        self.DP2_1.time_range = self.time_range
        self.DP2_1.update(self.t, [
                txHmi.em1500.etaSim[0],
                txHmi.em1500.etaSim[1],
                txHmi.em1500.etaSim[2]
            ])
        
        self.DP2_2.time_range = self.time_range
        self.DP2_2.update(self.t, [
                txHmi.em1500.etaSim[3]/np.pi*180.0,
                txHmi.em1500.etaSim[4]/np.pi*180.0,
                txHmi.em1500.etaSim[5]/np.pi*180.0
            ])

        self.EM1500_1.time_range = self.time_range
        self.EM1500_1.update(self.t, [
                txHmi.em1500.eta[0],
                txHmi.em1500.eta[1],
                txHmi.em1500.eta[2],
                txHmi.mru2.eta[0],
                txHmi.mru2.eta[1],
                txHmi.mru2.eta[2]
            ])
        self.EM1500_2.time_range = self.time_range
        self.EM1500_2.update(self.t, [
                txHmi.em1500.eta[3]/np.pi*180.0,
                txHmi.em1500.eta[4]/np.pi*180.0,
                txHmi.em1500.eta[5]/np.pi*180.0,
                txHmi.mru2.eta[3]/np.pi*180.0,
                txHmi.mru2.eta[4]/np.pi*180.0,
                txHmi.mru2.eta[5]/np.pi*180.0
            ])

        self.EM8000_1.time_range = self.time_range
        self.EM8000_1.update(self.t, [
                txHmi.em8000.eta[0],
                txHmi.em8000.eta[1],
                txHmi.em8000.eta[2],
                txHmi.mru1.eta[0],
                txHmi.mru1.eta[1],
                txHmi.mru1.eta[2]
            ])
        self.EM8000_2.time_range = self.time_range
        self.EM8000_2.update(self.t, [
                txHmi.em8000.eta[3]/np.pi*180.0,
                txHmi.em8000.eta[4]/np.pi*180.0,
                txHmi.em8000.eta[5]/np.pi*180.0,
                txHmi.mru1.eta[3]/np.pi*180.0,
                txHmi.mru1.eta[4]/np.pi*180.0,
                txHmi.mru1.eta[5]/np.pi*180.0
            ])
        
        self.COMAU.time_range = self.time_range
        self.COMAU.update(self.t, [
                txHmi.comau.q[0]/np.pi*180.0, 
                txHmi.comau.q[1]/np.pi*180.0, 
                txHmi.comau.q[2]/np.pi*180.0,
                txHmi.comau.q[3]/np.pi*180.0, 
                txHmi.comau.q[4]/np.pi*180.0, 
                txHmi.comau.q[5]/np.pi*180.0
            ])
        
        self.EM8000_bars.update([
                txHmi.em8000.cyl[0], 
                txHmi.em8000.cyl[1], 
                txHmi.em8000.cyl[2],
                txHmi.em8000.cyl[3], 
                txHmi.em8000.cyl[4], 
                txHmi.em8000.cyl[5],
                txHmi.em8000.cyl[0], 
                txHmi.em8000.cyl[1], 
                txHmi.em8000.cyl[2],
                txHmi.em8000.cyl[3], 
                txHmi.em8000.cyl[4], 
                txHmi.em8000.cyl[5]
            ])

        self.EM1500_bars.update([
                txHmi.em1500.cyl[0], 
                txHmi.em1500.cyl[1], 
                txHmi.em1500.cyl[2],
                txHmi.em1500.cyl[3], 
                txHmi.em1500.cyl[4], 
                txHmi.em1500.cyl[5],
                txHmi.em1500.cyl[0], 
                txHmi.em1500.cyl[1], 
                txHmi.em1500.cyl[2],
                txHmi.em1500.cyl[3], 
                txHmi.em1500.cyl[4], 
                txHmi.em1500.cyl[5]
            ])

        self.COMAU_bars.update([
                txHmi.comau.q[0]/np.pi*180.0, 
                txHmi.comau.q[1]/np.pi*180.0, 
                txHmi.comau.q[2]/np.pi*180.0,
                txHmi.comau.q[3]/np.pi*180.0, 
                txHmi.comau.q[4]/np.pi*180.0, 
                txHmi.comau.q[5]/np.pi*180.0,
                txHmi.comau.q[0]/np.pi*180.0, 
                txHmi.comau.q[1]/np.pi*180.0, 
                txHmi.comau.q[2]/np.pi*180.0,
                txHmi.comau.q[3]/np.pi*180.0, 
                txHmi.comau.q[4]/np.pi*180.0, 
                txHmi.comau.q[5]/np.pi*180.0
            ])

        # Pendulum Swing angles and velocities
        self.swingAnglesPlot.time_range = self.time_range
        self.swingAnglesPlot.update(self.t, [
            txHmi.phi[0]/np.pi*180.0,
            txHmi.phi[1]/np.pi*180.0
        ])

        self.swingVelocityPlot.time_range = self.time_range
        self.swingVelocityPlot.update(self.t, [
            txHmi.phi_t[0]/np.pi*180.0,
            txHmi.phi_t[1]/np.pi*180.0
        ])

        self.dampingParamPlot.time_range = self.time_range
        self.dampingParamPlot.update(self.t, [
            txHmi.c
        ])

        self.errorStatePlot.time_range = self.time_range
        self.errorStatePlot.update(self.t, [
            txHmi.e[0],
            txHmi.e[1],
            txHmi.e[2]
        ])
    
        # Xbox data
        self.XBOX_bars.update([
                self.xbox.left.x,
                self.xbox.left.y,
                self.xbox.right.x,
                self.xbox.right.y
            ])

    # Function to change the time axis range of the plots
    def plot_time_axis_range(self):
        # (This function is universal for all combobox objects in the plot tabs)

        # Set the time_range equal to combobox-object text
        self.time_range = int(self.sender().currentText())

        # Find and set the selected index to all combobox objects in the plot tabs
        val = self.sender().currentIndex()
        
        # Plotting tabs:
        self.EM8000_plot_time_range.setCurrentIndex(val)
        self.EM1500_plot_time_range.setCurrentIndex(val)
        self.COMAU_plot_time_range.setCurrentIndex(val)
        self.EM8000_plot_time_range_ship.setCurrentIndex(val)
        self.antiSwayPlotRange.setCurrentIndex(val)

    # EM 8000 button functions
    def EM8000_settled(self):
        self.EM8000_settled_btn.setStyleSheet("background-color: #cccccc")
        self.EM8000_neutral_btn.setStyleSheet("background-color: none   ")
        self.EM8000_engaged_btn.setStyleSheet("background-color: none   ")

        # Write to PLC: EM8000 settled = 1
        self.plc.write_by_name('MAIN.em8000.cmnd', 1, pyads.PLCTYPE_DINT)

    def EM8000_neutral(self):
        self.EM8000_settled_btn.setStyleSheet("background-color: none   ")
        self.EM8000_neutral_btn.setStyleSheet("background-color: #cccccc")
        self.EM8000_engaged_btn.setStyleSheet("background-color: none   ")

        # Write to PLC: EM8000 neutral = 3
        self.plc.write_by_name('MAIN.em8000.cmnd', 3, pyads.PLCTYPE_DINT)

    def EM8000_engaged(self):
        self.EM8000_settled_btn.setStyleSheet("background-color: none   ")
        self.EM8000_neutral_btn.setStyleSheet("background-color: none   ")
        self.EM8000_engaged_btn.setStyleSheet("background-color: #cccccc")

        # Write to PLC: EM8000 engaged = 7
        self.plc.write_by_name('MAIN.em8000.cmnd', 7, pyads.PLCTYPE_DINT)

    # EM 1500 button functions
    def EM1500_settled(self):
        self.EM1500_settled_btn.setStyleSheet("background-color: #cccccc")
        self.EM1500_neutral_btn.setStyleSheet("background-color: none   ")
        self.EM1500_engaged_btn.setStyleSheet("background-color: none   ")

        # Write to PLC: EM1500 settled = 1
        self.plc.write_by_name('MAIN.em1500.cmnd', 1, pyads.PLCTYPE_DINT)

    def EM1500_neutral(self):
        self.EM1500_settled_btn.setStyleSheet("background-color: none   ")
        self.EM1500_neutral_btn.setStyleSheet("background-color: #cccccc")
        self.EM1500_engaged_btn.setStyleSheet("background-color: none   ")

        # Write to PLC: EM1500 neutral = 3
        self.plc.write_by_name('MAIN.em1500.cmnd', 3, pyads.PLCTYPE_DINT)

    def EM1500_engaged(self):
        self.EM1500_settled_btn.setStyleSheet("background-color: none   ")
        self.EM1500_neutral_btn.setStyleSheet("background-color: none   ")
        self.EM1500_engaged_btn.setStyleSheet("background-color: #cccccc")

        # Write to PLC: EM1500 engaged = 7
        self.plc.write_by_name('MAIN.em1500.cmnd', 7, pyads.PLCTYPE_DINT)

    # Winch butttons
    def WINCH_settled(self):
        self.winchSettled.setStyleSheet("background-color: #cccccc")
        self.winchEngaged.setStyleSheet("background-color: none   ")
        self.winchEngagedFast.setStyleSheet("background-color: none   ")

        self.plc.write_by_name('MAIN.winch.mode', 0, pyads.PLCTYPE_UINT)

    def WINCH_engaged(self):
        self.winchSettled.setStyleSheet("background-color: none   ")
        self.winchEngaged.setStyleSheet("background-color: #cccccc")
        self.winchEngagedFast.setStyleSheet("background-color: none   ")

        self.plc.write_by_name('MAIN.winch.mode', 1, pyads.PLCTYPE_UINT)

    def WINCH_engaged_fast(self):
        self.winchSettled.setStyleSheet("background-color: none")
        self.winchEngaged.setStyleSheet("background-color: none")
        self.winchEngagedFast.setStyleSheet("background-color: #cccccc")

        self.plc.write_by_name('MAIN.winch.mode', 2, pyads.PLCTYPE_UINT)

    def WINCH_on(self):
        self.winchOn.setStyleSheet("background-color: #cccccc")
        self.winchOff.setStyleSheet("background-color: none   ")
    
        self.plc.write_by_name('MAIN.winch.enable', True, pyads.PLCTYPE_BOOL)

    def WINCH_off(self):
        self.winchOn.setStyleSheet("background-color: none")
        self.winchOff.setStyleSheet("background-color: #cccccc")

        self.plc.write_by_name('MAIN.winch.enable', False, pyads.PLCTYPE_BOOL)

    # COMAU button functions
    def COMAU_settled(self):
        self.COMAU_settled_btn.setStyleSheet("background-color: #cccccc")
        self.COMAU_engaged_btn.setStyleSheet("background-color: none   ")
        self.COMAU_engaged_fast_btn.setStyleSheet("background-color: none")

        # Write to PLC: COMAU settled = 1
        self.plc.write_by_name('MAIN.comau.cmnd', 0, pyads.PLCTYPE_DINT)

    def COMAU_engaged(self):
        self.COMAU_settled_btn.setStyleSheet("background-color: none   ")
        self.COMAU_engaged_btn.setStyleSheet("background-color: #cccccc")
        self.COMAU_engaged_fast_btn.setStyleSheet("background-color: none")

        # Write to PLC: COMAU engaged = 1
        self.plc.write_by_name('MAIN.comau.cmnd', 1, pyads.PLCTYPE_DINT)

    def COMAU_engaged_fast(self):
        self.COMAU_settled_btn.setStyleSheet("background-color: none")
        self.COMAU_engaged_btn.setStyleSheet("background-color: none")
        self.COMAU_engaged_fast_btn.setStyleSheet("background-color: #cccccc")

        # Write to PLC: COMAU engaged-fast = 2
        self.plc.write_by_name('MAIN.comau.cmnd', 2, pyads.PLCTYPE_DINT)

    # SYSTEM button functions
    def SYSTEM_settled(self):
        self.SYSTEM_settled_btn.setStyleSheet("background-color: #cccccc")
        self.EM8000_settled()
        self.EM1500_settled()
        self.COMAU_settled()

    def SYSTEM_stop(self):
        self.SYSTEM_settled_btn.setStyleSheet("background-color: none")
        self.EM8000_settled()
        self.EM1500_settled()
        self.COMAU_settled()

    # Controller functions
    def activateAntiSway(self):
        self.plc.write_by_name('MAIN.lqrAntiSwing.active', True, pyads.PLCTYPE_BOOL)

    def deactivateAntiSway(self):
        self.plc.write_by_name('MAIN.lqrAntiSwing.active', False, pyads.PLCTYPE_BOOL)

    def resetAntiSway(self):
        self.plc.write_by_name('MAIN.lqrAntiSwing.resetPath', True, pyads.PLCTYPE_BOOL)

    def enableMruEKF(self):
        self.plc.write_by_name('MAIN.pendelEstimator.useMru', True, pyads.PLCTYPE_BOOL)

    def disableMruEKF(self):
        self.plc.write_by_name('MAIN.pendelEstimator.useMru', False, pyads.PLCTYPE_BOOL)

    def resetPendulumEKF(self):
        self.plc.write_by_name('MAIN.pendelEstimator.reset', True, pyads.PLCTYPE_BOOL)

    def enableMruCM(self):
        self.plc.write_by_name('MAIN.controlMapping.useMru', True, pyads.PLCTYPE_BOOL)

    def disableMruCM(self):
        self.plc.write_by_name('MAIN.controlMapping.useMru', False, pyads.PLCTYPE_BOOL)

    def enableMruWinchController(self):
        self.plc.write_by_name('MAIN.winchController.useMru', True, pyads.PLCTYPE_BOOL)

    def disableMruWinchController(self):
        self.plc.write_by_name('MAIN.winchController.useMru', False, pyads.PLCTYPE_BOOL)


    # Stop all function
    def stop_all(self):
        self.SYSTEM_stop()
        print('APPLICATION STOPPED')

    # Function to handle the closing event of to the application
    def closeEvent(self, event):
        # reply = QMessageBox.question(self, 'Message',
        #     "Are you sure to quit?", QMessageBox.Yes |
        # QMessageBox.No, QMessageBox.No)


        plc2.close()

        reply = QMessageBox.Yes

        if reply == QMessageBox.Yes:
            self.stop_all()
            
            # Stop timed data read
            self.timerFast.stop()

            if self.plc_active:
                # # Close ADS ports
                self.plc.close()
                print('Beckhoff ADS Connection Closed')

            # Stop xbox thread
            self.xbox.close()

            event.accept()
        else:
            event.ignore()
            
           
        