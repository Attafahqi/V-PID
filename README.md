<h1 align="center">
  <img src="Asset\Title.png" alt="Logo">
</h1>

<details open="open">
<summary>Table of Contents</summary>

- [About](#about)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Set Up](#set-up)
  - [Running Program](#running-program)
- [Author](#author)

</details>

---

# About

<table>
<tr>
<td>

Welcome to V-PID, a software designed to facilitate students in control engineering lab sessions, particularly in understanding PID design using the root locus method. With this software, students can observe how the system operates and responds when using a PID controller. Additionally, it helps lab assistants assess students' calculations during the lab sessions.

</td>
</tr>
</table>

### Built With

<div >
	<img width="150" src="Asset\Python Logo.png" alt="Python" title="Python"/>
</div>

# Getting Started

### Prerequisites

To set up and run the V-PID, you need to install several Python libraries:

PyQt5 for the GUI.

```sh
pip install PyQt5
```

SymPy for symbolic mathematics.

```sh
pip install sympy
```

NumPy for numerical computations.

```sh
pip install numpy
```

Matplotlib for plotting.

```sh
pip install matplotlib
```

Control for control system analysis.

```sh
pip install control
```

Pandas for data manipulation.

```sh
pip install pandas
```

### Set Up

##### Make Database using Firebase

<table>
<tr>
<td>
The first step you need to take is to create a database using Firebase, as this software operates with a cloud database. The process is quite simple: just open the Firebase website, create a new Firebase project, and then select Realtime Database.

</td>
</tr>
</table>

##### Little Customization of the Source Code

<table>
<tr>
<td>
The next step is to open the source code and customize two key elements. First, you need to set the Firebase URL by copying the URL from the Realtime Database you created in Firebase and pasting it into the `Firebase_URL` (line 31) variable. Second, you need to set up an admin access code by choosing a numeric combination that allows you, as an admin, to access the students' scores. To simplify this process, you can use your student ID and assign it to the `ADMIN_NPM` (line 32) variable.
</td>
</tr>
</table>

##### Convert it to .exe

<table>
<tr>
<td>
Please run the following command in your terminal to create a .exe file:

```sh
pyinstaller --icon="Asset/Logo Control.png" --hidden-import=matplotlib.backends.backend_qt5agg --hidden-import=PyQt5 --hidden-import=scipy.linalg --hidden-import=numpy.f2py --exclude PyQt6  PID_Sim.py
```

</td>
</tr>
</table>

##### Set Up Directory

<table>
<tr>
<td>
Next, you can move the `PID_sim.exe` file and the `_internal` folder from `"dist/PID_sim/"` to the same directory as your original source code. After that, create a shortcut on your desktop to make it easier for students to access the application.

</td>
</tr>
</table>

### Running Program

<div >
	<img width="400" src="Asset\Login Page.jpg" alt="Login Page" title="Login Page"/>
</div>

##### Login

<table>
<tr>
<td>
First, you will be presented with the login page. Students should enter their respective student ID, while admins who want to check the scores can enter the secret code that was set up earlier.
</td>
</tr>
</table>

<div >
	<img width="600" src="Asset\Home Page.jpg" alt="Home Page" title="Home Page"/>
</div>

##### Checking the System Transfer Function

<table>
<tr>
<td>
To view the transfer function of the system, you can click on the servo motor image, which represents the system in this simulation. The transfer function has been randomized based on your student ID to create a unique system for each student.

</td>
</tr>
</table>

##### System Response without PID

<table>
<tr>
<td>
After this, you can observe the system response before applying the PID controller by clicking Run Simulation. You will then see three different scopes on the right, each displaying a different type of graph.

- The **top scope** shows the **error graph**.
- The **middle scope** displays the **system response for a continuous-time plant**.
- The **bottom scope** presents the **system response when the plant is converted to a discrete-time system**.
</td>
</tr>
</table>

##### Designing PID

<table>
<tr>
<td>
Students will design the PID controller by calculating the Kp, Ki, and Kd parameters using the **root locus method**. The design must meet the specification parameters displayed on the left side, which include **overshoot** and settling time requirements.

</td>
</tr>
</table>

##### Input PID Parameters

<table>
<tr>
<td>
To input the Kp, Ki, and Kd values obtained from your calculations, click on the "Proportional - Integral - Derivative" block. After entering the values, click Update to apply the changes.

</td>
</tr>
</table>

##### System Response with PID

<table>
<tr>
<td>
After entering the PID parameters, students should click Run Simulation again to observe the system response. The results will be displayed in the three scopes mentioned earlier, allowing students to compare the system’s behavior before and after applying the PID controller.

</td>
</tr>
</table>

##### Submit

<table>
<tr>
<td>
After that, students will click **Submit** to complete the lab session. The software will then calculate the **error** by comparing the students' computed values with the program’s calculations. Finally, the error data will be sent to the **Firebase database** for record-keeping.

</td>
</tr>
</table>

## Author

Attafahqi Amirtha Dariswan
