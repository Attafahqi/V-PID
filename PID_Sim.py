# ==============================================
#        ROOT LOCUS CONTROLLER DESIGN
#              Version 1.2.0
#              March 17,2025  
# ----------------------------------------------
#   Attafahqi Amirtha Dariswan - Elektro 2022
# ==============================================

import subprocess
import sys
import json
import requests
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QPushButton, QGraphicsDropShadowEffect
from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QCursor, QColor, QIcon
import sympy as sp
from sympy import symbols, expand
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg") 
import matplotlib.pyplot as plt
import control as ctrl
import math
import pandas as pd

import Asset.Resource

s = symbols('s') 

Firebase_URL = "https://root-locus-controller-default-rtdb.asia-southeast1.firebasedatabase.app/" ## Fill it by Firebase URL
ADMIN_NPM = "2206029891" ## Custom it by your secret number to access student grades

class HoverButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_size = None 
        self.default_pos = None  
        self.shadow_effect = None  

    def enterEvent(self, event):
        if self.default_size is None:
            self.default_size = self.size()  
            self.default_pos = self.pos()  
            self.hover_size = QSize(int(self.default_size.width() * 1.05), 
                                    int(self.default_size.height() * 1.05))  

        shift_x = (self.hover_size.width() - self.default_size.width()) // 2
        shift_y = (self.hover_size.height() - self.default_size.height()) // 2
        self.move(self.default_pos.x() - shift_x, self.default_pos.y() - shift_y)

        self.setFixedSize(self.hover_size)  
        self.setCursor(QCursor(Qt.PointingHandCursor))  

        if self.shadow_effect is None:
            self.shadow_effect = QGraphicsDropShadowEffect(self)
            self.shadow_effect.setBlurRadius(20)  
            self.shadow_effect.setXOffset(5)  
            self.shadow_effect.setYOffset(5)  
            self.shadow_effect.setColor(QColor(0, 0, 0, 100)) 
            self.setGraphicsEffect(self.shadow_effect)

        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.default_size and self.default_pos:
            self.setFixedSize(self.default_size)  
            self.move(self.default_pos)  
        self.setCursor(QCursor(Qt.ArrowCursor))  

        if self.shadow_effect:
            self.setGraphicsEffect(None)
            self.shadow_effect = None 

        super().leaveEvent(event)


class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        uic.loadUi("ui/Login.ui", self)
        self.setWindowTitle("Root Locus Controller Design")
        self.setWindowIcon(QIcon("Asset/Logo Control.png"))
        self.show()

        self.NPM.setFocusPolicy(Qt.ClickFocus)
        self.Login.clicked.connect(self.login)

    def auto_grade(self, firebase_url, output_csv):
        try:
            response = requests.get(f'{firebase_url}.json')
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch data from Firebase: {e}")
            return

        if not data:
            QMessageBox.warning(self, "Warning", "No data found in Firebase!")
            return

        # Memproses data
        extracted_data = []
        for id_number, details in data.items():
            if isinstance(details, dict) and "Avg error" in details:
                extracted_data.append({"NPM": id_number, "Avg error": details["Avg error"]})

        if not extracted_data:
            QMessageBox.warning(self, "Warning", "No valid data found in Firebase!")
            return

        df = pd.DataFrame(extracted_data)
        df["Avg error"] = pd.to_numeric(df["Avg error"], errors='coerce')
        df = df.dropna()

        if df.empty:
            QMessageBox.warning(self, "Warning", "All data contains invalid or missing values!")
            return

        min_error = df["Avg error"].min()
        max_error = df["Avg error"].max()

        if min_error == max_error:
            df["Grade"] = 100
        else:
            df["Grade"] = 60 + (40 * np.exp(-2 * (df["Avg error"] - min_error) / (max_error - min_error)))

        df["Grade"] = df["Grade"].round(2)
        df[["NPM", "Grade"]].to_csv(output_csv, index=False)
        QMessageBox.information(self, "Grading Done", f"Graded results saved to {output_csv}")
        subprocess.Popen(["notepad.exe", output_csv])

    def is_valid_npm(self, npm):
        return npm.isdigit() and len(npm) >= 10

    def login(self):
        NPM = self.NPM.text().strip()

        if NPM == ADMIN_NPM:
            self.auto_grade(Firebase_URL, "graded_results.csv")
            QApplication.quit()
            return

        if not self.is_valid_npm(NPM):
            QMessageBox.warning(self, "Login Failed", "NPM must be at least 10 digits and contain only numbers!")
            return

        self.main_window = Main(NPM)
        self.main_window.show()
        self.close()

class Main(QMainWindow):
    def __init__(self, NPM):
        super(Main, self).__init__()
        
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        screen_width = screen_rect.width()
        screen_height = screen_rect.height()
        
        if screen_width >= 1920 and screen_height >= 1080:
            ui_file = "ui/Main.ui"
        else:
            ui_file = "ui/MainNoHD.ui"
        
        uic.loadUi(ui_file, self)
        self.setWindowIcon(QIcon("Asset/Logo Control.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.NPM = NPM
        self.replace_buttons()

        self.Kp = 1
        self.Ki = 0
        self.Kd = 0

        self.SP = 1
        self.ST = 1

        last_five = str(self.NPM)[-5:]
        
        # Replace '0' with '1' and convert back to integers
        A, B, C, D, E = map(lambda x: int(x) if x != '0' else 1, last_five)

        self.num = C 
        den = (s + D) * (s + E)

        self.den = expand(den)

        self.num_coeff = [1]
        den_exp = self.den.as_poly(s).all_coeffs()
        self.den_coeff = [float(c) for c in den_exp]  

        self.t_cont = None
        self.setpoint = None
        self.tz = None
        self.setpoint_z = None
        self.y_out_cont = None
        self.y_out_z = None
        self.error_signal_cont = None

        self.os = A + 10

        self.TS = (B + E) * 0.1

        self.TimeS.setText(str(self.TS))
        self.Overshoot.setText(str(self.os) + "%" )

        self.show()

    def trueValue(self):
        s = sp.Symbol('s')

        numerator_expanded = sp.expand(self.num)
        denominator_expanded = sp.expand(self.den)

        poles = sp.solve(self.den, s)

        Mp_fraction = self.os / 100 
        zeta = -np.log(Mp_fraction) / np.sqrt(np.pi**2 + (np.log(Mp_fraction))**2)
        omega_n = 4 / (self.TS * zeta)

        real = -zeta * omega_n
        imaginary = omega_n * np.sqrt(1 - zeta**2)
        pole_1 = complex(real, imaginary)

        def calculate_angle(pole, point):
            angle = 180 - np.angle(point - pole, deg=True)
            return angle

        def find_zero_using_angle_criterion(poles, dominant_pole):
            total_angle_from_poles = 0
            for pole in poles:
                angle = calculate_angle(pole, dominant_pole)
                total_angle_from_poles += angle

            required_angle_for_zero = -180 + total_angle_from_poles

            denominator = dominant_pole.real  
            numerator = dominant_pole.imag    
            angle_radians = math.radians(required_angle_for_zero)
            tan_value = math.tan(angle_radians)
            
            value = numerator / tan_value
            
            

            zero = denominator + value
            return zero

        poles_complex = [complex(pole, 0) for pole in poles]

        zero = abs(find_zero_using_angle_criterion(poles_complex, pole_1))

        def calculate_KD(zero, numerator_expanded, denominator_expanded, pole):
            Gcd_s = pole + zero
            
            numerator_value = numerator_expanded.subs(s, pole)
            denominator_value = denominator_expanded.subs(s, pole)
            
            G_s = numerator_value / denominator_value if denominator_value != 0 else float('inf')

            product = Gcd_s * G_s
            absolute_value = abs(product.evalf()) 
            
            KD = 1 / absolute_value if absolute_value != 0 else float('inf')  # Handle pembagi nol

            return KD

        KD_value = calculate_KD(zero, numerator_expanded, denominator_expanded, pole_1)

        def calculate_KI(zero, numerator_expanded, denominator_expanded, pole):
            Gci_s = (pole + 0.5)/pole
            Gpd_s = KD_value * (pole + zero)

            
            numerator_value = numerator_expanded.subs(s, pole)
            denominator_value = denominator_expanded.subs(s, pole)
            
            G_s = numerator_value / denominator_value if denominator_value != 0 else float('inf')

            product = Gci_s * Gpd_s * G_s

            absolute_value = abs(product.evalf()) 
            
            KI = 1 / absolute_value if absolute_value != 0 else float('inf')  # Handle pembagi nol
        

            return KI

        KI_value = calculate_KI(zero, numerator_expanded, denominator_expanded, pole_1)

        expression = (s + 0.5) * (s + zero)
        expanded = sp.expand(expression)
        
        x = abs(expanded.coeff(s, 1))  # Coefficient of s
        y = abs(expanded.coeff(s, 0))  # Constant term

        Kd_true = KI_value * KD_value
        Ki_true = KI_value * KD_value * y
        Kp_true = KI_value * KD_value * x

        print(KD_value)
        print(KI_value)
        print(zero)
        print(x)
        print(y)

        print(f'Kp: {Kp_true}')
        print(f'Ki: {Ki_true}')
        print(f'Kd: {Kd_true}')

        error_Kp = abs(Kp_true - self.Kp)
        error_Ki = abs(Ki_true - self.Ki)
        error_Kd = abs(Kd_true - self.Kd)

        error = (error_Kp + error_Ki + error_Kd) / 3

        url = f"{Firebase_URL}/{self.NPM}.json"  # Using .json is required for Firebase API
        payload = {
            "Kp error": float(error_Kp.evalf()) if isinstance(error_Kp, sp.Float) else float(error_Kp),
            "Ki error": float(error_Ki.evalf()) if isinstance(error_Ki, sp.Float) else float(error_Ki),
            "Kd error": float(error_Kd.evalf()) if isinstance(error_Kd, sp.Float) else float(error_Kd),
            "Avg error": float(error.evalf()) if isinstance(error, sp.Float) else float(error),
        }

        response = requests.put(url, data=json.dumps(payload))
        print(response.json())

        QApplication.quit()


    def controller(self):
        if hasattr(self, "controller_window") and self.controller_window.isVisible():
            self.controller_window.activateWindow() 
            
        else:
            self.controller_window = PID(self)
            self.controller_window.show()

    def reference(self):
        if hasattr(self, "reference_window") and self.reference_window.isVisible():
            self.reference_window.activateWindow() 
            
        else:
            self.reference_window = References(self)
            self.reference_window.show()
    
    def TransferFunction(self):
        if hasattr(self, "plant_window") and self.plant_window.isVisible():
            self.reference_window.activateWindow() 
            
        else:
            self.reference_window = TransferFunction(self)
            self.reference_window.show()
        
    def simulation(self):
        s = ctrl.TransferFunction.s
        Ts = 0.1  # Sampling time for Z-transform

        # Continuous PID Controller
        C = self.Kp + self.Ki / s + self.Kd * s

        # Continuous Plant G(s)
        G = ctrl.TransferFunction(self.num_coeff, self.den_coeff)

        # Closed-loop system in continuous time
        T_cont = ctrl.feedback(C * G, 1)

        # Convert G(s) to G(z) using Zero-Order Hold (ZOH)
        Gz = ctrl.sample_system(G, Ts, method='zoh')

        # Time vectors
        self.t_cont = np.linspace(0, 10, 1000)  # Continuous time
        self.tz = np.arange(0, 10, Ts)  # Discrete time

        # Define setpoint signal
        self.setpoint_cont = np.piecewise(self.t_cont, 
            [self.t_cont < self.ST, self.t_cont >= self.ST], 
            [0, self.SP]
        )
        self.setpoint_z = np.piecewise(self.tz, 
            [self.tz < self.ST, self.tz >= self.ST], 
            [0, self.SP]
        )

        # Simulate continuous-time response
        self.t_cont, self.y_out_cont = ctrl.forced_response(T_cont, T=self.t_cont, U=self.setpoint_cont)

        # Simulate hybrid response (Continuous PID, Discrete Plant)
        self.u_out = self.Kp * self.setpoint_z + self.Ki * np.cumsum(self.setpoint_z) * Ts + self.Kd * np.gradient(self.setpoint_z, Ts)  # ✅ Fixed
        self.tz, self.y_out_z = ctrl.forced_response(Gz, T=self.tz, U=self.u_out)

        # Compute error signals
        self.error_signal_cont = self.setpoint_cont - self.y_out_cont
        self.error_signal_z = self.setpoint_z - self.y_out_z

        QMessageBox.warning(self, "Simulation", "Simulation completed!")



    def outputResponse (self):
        if self.y_out_cont is None:
            QMessageBox.warning(self, "No Simulation", "Run simulation first!")
            return
        
        plt.figure(figsize=(8, 4))
        plt.plot(self.t_cont, self.setpoint_cont, 'r--', label="Setpoint")
        plt.plot(self.t_cont, self.y_out_cont, 'b', label="System Output (Continuous)")
        plt.xlabel("Time (s)")
        plt.ylabel("Output")
        plt.title("Output Response (PID(s) + Plant(s))")
        plt.legend()
        plt.grid()
        plt.show()
    
    def errorResponse (self):
        if self.error_signal_cont is None:
            QMessageBox.warning(self,"No Simulation", "Run simulation first!")
            return

        plt.figure(figsize=(8, 4))
        plt.plot(self.t_cont, self.error_signal_cont, 'g', label="Error Signal")
        plt.xlabel("Time (s)")
        plt.ylabel("Error")
        plt.title("Error Signal (PID(s) + Plant(s))")
        plt.legend()
        plt.grid()
        plt.show()

    def outputResponse_discrete(self):
        if self.y_out_z is None:
            QMessageBox.warning(self, "No Simulation", "Run simulation first!")
            return
        
        plt.figure(figsize=(8, 4))
        plt.step(self.tz, self.setpoint_z, 'r--', where='post', label="Setpoint")
        plt.step(self.tz, self.y_out_z, 'b', where='post', label="System Output (Hybrid)")
        plt.xlabel("Time (s)")
        plt.ylabel("Output")
        plt.title("Output Response (PID(s) + Plant(z))")
        plt.legend()
        plt.grid()
        plt.show()


    def replace_buttons(self):
        for button_name in ["Submit", "runSim", "Refrensi", "Controller", "Plant", "scopeOutput", "scopeController", "scopeOutput_Diskrit"]:
            button = self.findChild(QPushButton, button_name)
            if button:
                hover_button = HoverButton(button.text(), self)
                hover_button.setGeometry(button.geometry())
                hover_button.setStyleSheet(button.styleSheet())  
                hover_button.setObjectName(button.objectName())  
                
                # Reconnect signals
                if button_name == "Controller":
                    hover_button.clicked.connect(self.controller)
                elif button_name == "runSim":
                    hover_button.clicked.connect(self.simulation)
                elif button_name == "Refrensi":
                    hover_button.clicked.connect(self.reference)
                elif button_name == "Plant":
                    hover_button.clicked.connect(self.TransferFunction)
                elif button_name == "scopeOutput":
                    hover_button.clicked.connect(self.outputResponse)
                elif button_name == "scopeController":
                    hover_button.clicked.connect(self.errorResponse)
                elif button_name == "Submit":
                    hover_button.clicked.connect(self.trueValue)
                elif button_name == "scopeOutput_Diskrit":
                    hover_button.clicked.connect(self.outputResponse_discrete)

                button.deleteLater()



class PID(QMainWindow):
    def __init__(self, main_window):
        super(PID, self).__init__()
        uic.loadUi("ui/PIDparam.ui", self)
        self.setWindowIcon(QIcon("Asset/Logo Control.png"))
        self.setWindowTitle("PID Parameter")

        self.main_window = main_window

        self.LKp.setText(str(self.main_window.Kp))
        self.LKi.setText(str(self.main_window.Ki))
        self.LKd.setText(str(self.main_window.Kd))

        self.show()

        self.updatePID.clicked.connect(self.updateParam)

    def updateParam(self):
        Kp = self.LKp.text().strip()
        Ki = self.LKi.text().strip()
        Kd = self.LKd.text().strip()

        if not Kp.replace('.', '', 1).isdigit() or not Ki.replace('.', '', 1).isdigit() or not Kd.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Update Failed", "PID parameters must be numbers!") 
            return
        
        self.main_window.Kp = float(Kp)
        self.main_window.Ki = float(Ki)
        self.main_window.Kd = float(Kd)

        self.close()


class References(QMainWindow):
    def __init__(self, main_window):
        super(References, self).__init__()
        uic.loadUi("ui/ReferencePoint.ui", self)
        self.setWindowIcon(QIcon("Asset/Logo Control.png"))
        self.setWindowTitle("Reference Point")

        self.main_window = main_window

        self.SetPoint.setText(str(self.main_window.SP))
        self.SetTime.setText(str(self.main_window.ST))

        self.show()

        self.updateSP.clicked.connect(self.updateSetPoint)

    def updateSetPoint(self):
        SP = self.SetPoint.text().strip()
        ST = self.SetTime.text().strip()

        if not SP.replace('.', '', 1).isdigit() or not ST.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Update Failed", "Set Point must be numbers!")
            return
        
        self.main_window.SP = float(SP)
        self.main_window.ST = float(ST)

        self.close()


class TransferFunction(QMainWindow):
    def __init__(self, main_window):
        super(TransferFunction, self).__init__()
        uic.loadUi("ui/TransferFunction.ui", self)
        self.setWindowIcon(QIcon("Asset/Logo Control.png"))
        self.setWindowTitle("System Transfer Function")

        self.main_window = main_window

        self.Num.setText(str(self.main_window.num))
        self.Den.setText(str(self.main_window.den))

        self.show()

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
