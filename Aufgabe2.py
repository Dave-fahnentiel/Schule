# Beispiel einer Ablaufkette mit Abbruch des Ablaufs durch Not-Aus
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor
from Input_Output import Input, Output
from Lamp import Lamp
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("Aufgabe_Lamp_Control_GUI.ui", self)

        self.__step = 1

        # Instanziieren der Aktoren
        self.__lamp_P1 = Lamp(100, 11,  22, 22, "operation", False)
        self.__lamp_P2 = Lamp(100, 44,  22, 22, "operation", False)
        self.__lamp_P3 = Lamp(100, 77,  22, 22, "operation", False)
        self.__lamp_P4 = Lamp(100, 111, 22, 22,  "stop", False)
        self.__lamp_P5 = Lamp(100, 143, 22, 22,  "error", False)

        # Instanziieren der Input/Outputs
        self.__inp_S1 = Input(False)                        # Verbunden mit Schließerkontakt
        self.__inp_S2 = Input(False)                        # Verbunden mit Schließerkontakt
        self.__inp_S3 = Input(True)                         # Verbunden mit Öffnerkontakt
        self.__inp_S4 = Input(True)                         # Verbunden mit Öffnerkontakt
        self.__inp_B1 = Input(True)

        self.__out_P1 = Output(False, self.__lamp_P1)
        self.__out_P2 = Output(False, self.__lamp_P2)
        self.__out_P3 = Output(False, self.__lamp_P3)
        self.__out_P4 = Output(False, self.__lamp_P4)
        self.__out_B1 = Output(False, self.__lamp_P5)

        # Timer instanziieren
        self.timer_seq_chain = QTimer(self)
        
        # Signal des Timers mit Slot verbinden          
        self.timer_seq_chain.timeout.connect(self.seq_chain)
        self.timer_seq_chain.start(16)                          # Timer-Schleife starten

        # Signale des PushButtons mit Slots verbinden
        self.btn_S1.pressed.connect(self.btn_S1_pressed)
        self.btn_S1.released.connect(self.btn_S1_released)
        self.btn_S2.pressed.connect(self.btn_S2_pressed)
        self.btn_S2.released.connect(self.btn_S2_released)
        self.btn_S3.pressed.connect(self.btn_S3_pressed)
        self.btn_S3.released.connect(self.btn_S3_released)
        self.btn_S4.toggled.connect(self.swt_S4_toggled)
        self.sen_B1.toggled.connect(self.sen_B1_toggled)

    # Schließen des Tasters S1
    def btn_S1_pressed(self):
        self.__inp_S1.set_state(True)

    # Öffnen des Tasters S1
    def btn_S1_released(self):
        self.__inp_S1.set_state(False)

    # Slot Schließen des Tasters S2
    def btn_S2_pressed(self):
        self.__inp_S2.set_state(True)

    # Öffnen des Tasters S2
    def btn_S2_released(self):
        self.__inp_S2.set_state(False)

    # Öffnen des Tasters S3
    def btn_S3_pressed(self):
        self.__inp_S3.set_state(False)

    # Schließen des Tasters S3
    def btn_S3_released(self):
        self.__inp_S3.set_state(True)

    def swt_S4_toggled(self):
        if self.__inp_S4.get_state() == True:
            self.__inp_S4.set_state(False)
        elif self.__inp_S4.get_state() == False:
            self.__inp_S4.set_state(True)

    def sen_B1_toggled(self):
        if self.__inp_B1.get_state() == True:
            self.__inp_B1.set_state(False)
        elif self.__inp_B1.get_state() == False:
            self.__inp_B1.set_state(True)

    # Timer-Slot der Ablaufkette
    def seq_chain(self):
        # Programmlogik der Ablaufkette

        # Abbruch der Ablaufkette, wenn der Not-Aus betätigt wird
        if self.__inp_S4.get_state() == False:
            # Aktionen aller Schritte (außer Schritt 1) zurücksetzen
            self.__out_P1.set_state(True)
            self.__out_P2.set_state(False)
            self.__out_P3.set_state(False)
            self.__out_P4.set_state(True)
            self.__out_B1.set_state(False)
            # Zurücksetzen der Ablaufkette in Initialschritt 1
            self.__step = 1
        
        elif self.__inp_S4.get_state() == True:
            self.__out_P4.set_state(False)

        # Pausieren der Ablaufkette, wenn Störung vorliegt
        if self.__inp_B1.get_state() == False:
            self.__out_B1.set_state(True)
        elif self.__inp_B1.get_state() == True:
            self.__out_B1.set_state(False)

            # Schritt 1:
            if self.__step == 1:
                
                # Aktion des vorherigen Schrittes zurücksetzen
                self.__out_P3.set_state(False)
                # Aktion des aktuellen Schrittes ausführen
                self.__out_P1.set_state(True)
                # Überprüfung der Transitionsbedingung (Weiterschaltbedingung)
                if self.__step == 1 and self.__inp_S2.get_state() == True:
                    self.__step = 2
            
            # Schritt 2:
            elif self.__step == 2:
                # Aktion des vorherigen Schrittes zurücksetzen
                self.__out_P1.set_state(False)
                # Aktion des aktuellen Schrittes ausführen
                self.__out_P2.set_state(True)
                # Überprüfung der Transitionsbedingung (Weiterschaltbedingung)
                if self.__step == 2 and self.__inp_S3.get_state() == False:
                    self.__step = 3

            # Schritt 3:
            elif self.__step == 3:
                # Aktion des vorherigen Schrittes zurücksetzen
                self.__out_P2.set_state(False)
                # Aktion des aktuellen Schrittes ausführen
                self.__out_P3.set_state(True)
                # Überprüfung der Transitionsbedingung (Weiterschaltbedingung)
                if self.__step == 3 and self.__inp_S1.get_state() == True:
                    self.__step = 1
        self.update()

    # Event zum Zeichnen der Lampe
    def paintEvent(self, event):
        painter = QPainter(self) 
        self.draw_lamp(painter)

    # Methode zum Zeichnen der Lampe
    def draw_lamp(self, painter):
        # Lampe P1 zeichnen
        painter.setBrush(QColor(self.__lamp_P1.get_color()))
        painter.drawEllipse(self.__lamp_P1.get_pos_x(), self.__lamp_P1.get_pos_y(), self.__lamp_P1.get_width(), self.__lamp_P1.get_height())
        painter.setBrush(QColor(self.__lamp_P2.get_color()))
        painter.drawEllipse(self.__lamp_P2.get_pos_x(), self.__lamp_P2.get_pos_y(), self.__lamp_P2.get_width(), self.__lamp_P2.get_height())
        painter.setBrush(QColor(self.__lamp_P3.get_color()))
        painter.drawEllipse(self.__lamp_P3.get_pos_x(), self.__lamp_P3.get_pos_y(), self.__lamp_P3.get_width(), self.__lamp_P3.get_height())
        painter.setBrush(QColor(self.__lamp_P4.get_color()))
        painter.drawEllipse(self.__lamp_P4.get_pos_x(), self.__lamp_P4.get_pos_y(), self.__lamp_P4.get_width(), self.__lamp_P4.get_height())
        painter.setBrush(QColor(self.__lamp_P5.get_color()))
        painter.drawEllipse(self.__lamp_P5.get_pos_x(), self.__lamp_P5.get_pos_y(), self.__lamp_P5.get_width(), self.__lamp_P5.get_height())

# Hauptprogramm        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())