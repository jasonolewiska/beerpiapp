import tkinter as tk
import RPi.GPIO as GPIO
import os
import glob
import time
from tkinter import PhotoImage
from tkinter import font

#Set the GPIO mode to BCM (Broadcom SOC channel)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

 #Define the GPIO pins for each pump
PUMP_1_PIN = 17  # Change this to the actual GPIO pin for pump 1
PUMP_2_PIN = 18  # Change this to the actual GPIO pin for pump 2
PUMP_3_PIN = 19  # Change this to the actual GPIO pin for pump 3
PUMP_4_PIN = 20  # Change this to the actual GPIO pin for pump 4 (MASTER)
#Valves
PUMP_5_PIN = 21  # Change this to the actual GPIO pin for valve 5
PUMP_6_PIN = 22  # Change this to the actual GPIO pin for valve 6
PUMP_7_PIN = 23  # Change this to the actual GPIO pin for valve 7
#HEAT
PUMP_8_PIN = 24  # Change this to the actual GPIO pin for valve 8
PUMP_9_PIN = 26  # Change this to the actual GPIO pin for valve 9
PUMP_10_PIN = 27  # Change this to the actual GPIO pin for valve 10
# Set the GPIO pins as outputs
GPIO.setup(PUMP_1_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_2_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_3_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_4_PIN, GPIO.OUT, initial=GPIO.LOW) #(MASTER)
GPIO.setup(PUMP_5_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_6_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_7_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_8_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_9_PIN, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUMP_10_PIN, GPIO.OUT, initial=GPIO.LOW)
# Sensor reading code begins
sensor_names = {
    "MashTon": "28-031655cf13ff",  # Replace 'xxxxxx1' with the actual sensor folder name
    "HLT": "28-031655cd1bff",      # Replace 'xxxxxx2' with the actual sensor folder name
    "BoilKettle": "28-031655b50eff" # Replace 'xxxxxx3' with the actual sensor folder name
}

base_dir = '/sys/bus/w1/devices/'


def read_temperature(device_folder):
    try:
        device_file = os.path.join(device_folder, 'w1_slave')
        with open(device_file, 'r') as file:
            lines = file.readlines()
        if lines[0].strip()[-3:] == 'YES':
            temperature_data = lines[1].split('=')[1].strip()
            temperature_celsius = float(temperature_data) / 1000.0
            return temperature_celsius
            
        else:
            return None
    except Exception as e:
        print("Error reading temperature:", str(e))
        return None
# Sensor reading code ends


class MashApp:
    def __init__(self, master):
        self.master = master
        master.title("RASPI BREWING APP")
        master.geometry("800x480")
         # Set the window size
        window_width = 800
        window_height = 480
        # Get the screen dimension
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        # Find the center position
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        # Set the position of the window to the center of the screen
        master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        ## Custom font label
        custom_font = font.Font(family="Broadway", size=20, weight="bold")
        label = tk.Label(master, text="Welcome to RASPI Brewing App", font=custom_font)
        label.pack()

        # Load the background image (use PIL if it's not a GIF)
        self.background_image = PhotoImage(file='/home/Beerpi/beerpiapp/beerpic.gif')
         # Create a label with the image and make it an instance attribute
        self.background_label = tk.Label(master, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
  #      master.configure(background='black')
        self.temperature_labels = {}
        self.saved_data = {}
        self.mash_step_4_widget = None  # Initialize the 4th widget attribute here
        self.setup_mash_steps()

    def setup_mash_steps(self):
        self.label = tk.Label(self.master, text="Mash Steps", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.label.pack(side=tk.TOP, anchor='w', padx=(340,0))
        self.mash_steps_scale = tk.Scale(self.master, from_=1, to=5, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white', command=self.update_mash_step)
        self.mash_steps_scale.pack(side=tk.TOP, anchor='w', padx=(360,0))
        self.temp_frame = tk.Frame(self.master)
        self.temp_frame.pack(side=tk.TOP, anchor='w', padx=(10,0))
        self.temp_scales = []
        self.update_mash_step(1)
        self.save_button = tk.Button(self.master, text="Save Mash Steps", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white', command=self.save_mash_steps)
        self.save_button.pack(side=tk.TOP, anchor='w', padx=(310,0))
    def update_mash_step(self, val):
        mash_step = int(float(val))
        existing_sliders = len(self.temp_scales)
        if mash_step < existing_sliders:
            for _ in range(existing_sliders - mash_step):
                temp_label, temp_scale, time_label, time_scale = self.temp_scales.pop()
                temp_label.grid_forget()
                temp_scale.grid_forget()
                time_label.grid_forget()
                time_scale.grid_forget()
        for i in range(existing_sliders, mash_step):
            temp_label = tk.Label(self.temp_frame, text=f"Mash Step {i + 1} Temperature C", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
            temp_scale = tk.Scale(self.temp_frame, from_=10, to=100, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
            temp_scale.set(52 if i > 0 else self.saved_data.get('Mash Step 1 Temperature', 52))
            temp_scale.bind("<ButtonRelease-1>", self.on_temp_scale_change)  # Bind event to all scales
            time_label = tk.Label(self.temp_frame, text=f"Mash Step {i + 1} Time (MIN)", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
            time_scale = tk.Scale(self.temp_frame, from_=1, to=60, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
            time_scale.set(20)
            temp_label.grid(row=i, column=0)
            temp_scale.grid(row=i, column=1)
            time_label.grid(row=i, column=2)
            time_scale.grid(row=i, column=3)
            self.temp_scales.append((temp_label, temp_scale, time_label, time_scale))
    def on_temp_scale_change(self, event):
        for index, (_, temp_scale, _, _) in enumerate(self.temp_scales):
            if event.widget == temp_scale:
                # Check if there is a next scale and update it
                if index + 1 < len(self.temp_scales):
                    next_temp_scale = self.temp_scales[index + 1][1]
                    next_temp_scale.set(temp_scale.get())
                break
    def save_mash_steps(self):
        for i, (_, temp_scale, _, time_scale) in enumerate(self.temp_scales, start=1):
            self.saved_data[f'Mash Step {i} Temperature'] = temp_scale.get()
            self.saved_data[f'Mash Step {i} Time'] = time_scale.get()
        print("Saved Mash Step Data:", self.saved_data)
    # Clear existing widgets
        for widget in self.master.winfo_children():
            if widget != self.background_label:  # Skip the background label
                widget.destroy()
                
        # Add additional controls
        self.add_additional_controls()

    def add_additional_controls(self):
        self.grain_bill_label = tk.Label(self.master, text="Grain Bill X10 (1lbs=10)", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white')
        self.grain_bill_label.pack(side=tk.TOP)
        self.grain_bill_scale = tk.Scale(self.master, from_=1, to=100, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.grain_bill_scale.pack(side=tk.TOP)
        #default value of the scale to 10
        self.grain_bill_scale.set(50)
        self.batch_size_label = tk.Label(self.master, text="Batch Size X10 (1Gall=10)", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white')
        self.batch_size_label.pack(side=tk.TOP)
        self.batch_size_scale = tk.Scale(self.master, from_=1, to=250, orient="horizontal",  font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.batch_size_scale.pack(side=tk.TOP)
         # Set the default value of the scale to 50
        self.batch_size_scale.set(50)
        self.boil_off_label = tk.Label(self.master, text="Boil Off X10 (1Gall=10)", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white')
        self.boil_off_label.pack(side=tk.TOP)
        self.boil_off_scale = tk.Scale(self.master, from_=0, to=100, orient="horizontal",  font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.boil_off_scale.pack(side=tk.TOP)
        #default value of the scale to 10
        self.boil_off_scale.set(10)
        self.ratio_label = tk.Label(self.master, text="Grist Ratio 150=1.50", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white')
        self.ratio_label.pack(side=tk.TOP)
        self.ratio_scale = tk.Scale(self.master, from_=100, to=200, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.ratio_scale.pack(side=tk.TOP)
        #default value of the scale to 10
        self.ratio_scale.set(150)

        self.grain_temp_label = tk.Label(self.master, text="Grain Temperature (°C)", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white')
        self.grain_temp_label.pack(side=tk.TOP)
        self.grain_temp_scale = tk.Scale(self.master, from_=10, to=100, orient="horizontal", font=("Rockwell Extra Bold", 14, "bold"), bg='black', fg='white')
        self.grain_temp_scale.pack(side=tk.TOP)
    
        
        self.set_grain_temp_button = tk.Button(self.master, text="Set Grain Temperature", font=("Arial", 16, "bold"), command=self.set_grain_temp)
        self.set_grain_temp_button.pack(side=tk.TOP)

        self.save_additional_data_button = tk.Button(self.master, text="Lets Brew", font=("Rockwell Extra Bold", 16, "bold"), bg='black', fg='white', command=self.save_additional_data)
        self.save_additional_data_button.pack(side=tk.TOP)
        
    def set_grain_temp(self):
        # Read the temperature from the sensor for the MashTon
        sensor_folder = sensor_names["MashTon"]
        temperature_celsius = read_temperature(os.path.join(base_dir, sensor_folder))
        if temperature_celsius is not None:
            temperature_fahrenheit = (temperature_celsius)  # Convert to Fahrenheit
            # Set the temperature on the scale to reflect the sensor value
            self.grain_temp_scale.set(temperature_celsius)  # Set the scale value
            print("Grain Temperature Set from Sensor:", temperature_celsius)
        else:
            print("Failed to read temperature from sensor for MashTon.")

    def save_additional_data(self):
        self.saved_data['Grain Bill'] = self.grain_bill_scale.get() / 10.0
        self.saved_data['Batch Size'] = self.batch_size_scale.get() / 10.0
        self.saved_data['Boil Off'] = self.boil_off_scale.get() / 10.0
        self.saved_data['Grain Temperature', 20.0] = self.saved_data.get('Grain Temperature', 20.0)
        self.saved_data['Mash Step 1 Temperature', 20] = self.saved_data.get('Mash Step 1 Temperature', 20)
        self.saved_data['Grain Bill', 0] = self.saved_data.get('Grain Bill', 0) 
        self.saved_data['Grist Ratio'] = self.ratio_scale.get() / 100
        print("Saved Additional Data:", self.saved_data)
     
    
        # Clear existing widgets
        for widget in self.master.winfo_children():
            if widget != self.background_label:  # Skip the background label
                widget.destroy()
            
        #Return strike water
        self.calculate_strike_water()
        #Create pump buttons
        self.create_pump_buttons()
        
    def calculate_strike_water(self):
        temp_grain = self.saved_data.get('Grain Temperature', 20.0)  # Default to 20°C
        temp_mash = self.saved_data.get('Mash Step 1 Temperature', 20)
        weight_grain = self.saved_data.get('Grain Bill', 0)
        ratio = self.saved_data.get('Grist Ratio')
        #ratio = 1.5  # Quarts of water per pound of grain
        batch_size = self.saved_data.get('Batch Size')
        boil_off = self.saved_data.get('Boil Off')
        
        t_strike = (0.2 / ratio) * (temp_mash - temp_grain) + temp_mash
        v_strike = weight_grain * ratio / 4  # Convert quarts to gallons
        pre_boil_vol = batch_size + boil_off
        sparge_wtr = pre_boil_vol - v_strike
        #print("Strike Water Temperature:", t_strike)
        #print("Strike Water Volume:", v_strike)
        #print("Pre-Boil Volume (Gal):", pre_boil_vol)
        #print("Sparge Water (Gal):", sparge_wtr)
        #print("Mash Temperature C:", temp_grain)
        self.saved_data['Strike Water Temperature:'] = t_strike
        self.saved_data['Strike Water Volume'] = v_strike
        self.saved_data['Pre Boil Volume'] = pre_boil_vol
        self.saved_data['Sparge Water (Gal)'] = sparge_wtr
        #print("Saved Additional Data:", self.saved_data)
        return t_strike, v_strike, pre_boil_vol, sparge_wtr
        
    def create_labels(self):
        x, y = 300, 15
        for sensor_name in sensor_names:
            label = self.canvas.create_text(x, y, text="", fill="red", font=("Rockwell Extra Bold", 14, "bold"))
            self.temperature_labels[sensor_name] = label
            y += 25  # Adjust the y-coordinate for the next label
        
    def display_temperature_labels(self):
    # Get temperature readings from sensors and update the corresponding labels
        for sensor_name, label in self.temperature_labels.items():
            temperature = read_temperature(os.path.join(base_dir, sensor_names[sensor_name]))
            if temperature is not None:
                temp_str = f"{temperature:.2f}°C"
            else:
                temp_str = "N/A"

        # Update the text of the corresponding label
            self.canvas.itemconfig(label, text=f"{sensor_name}: {temp_str}")
        
    # Schedule the next update after 1000 milliseconds (1 second)
        self.master.after(1000, self.display_temperature_labels)
    

        
    def create_pump_buttons(self):
        
    # Create a Canvas widget
        # Create a Canvas widget
        self.canvas = tk.Canvas(self.master, width=800, height=480)
        self.background_image = PhotoImage(file='/home/Beerpi/beerpiapp/2.gif')
        # Add the background image to the canvas using the correct variable
        self.canvas.create_image(400, 240, image=self.background_image, anchor='center')  # Center the image
    # Create the first red circle on the canvas (initially "Pump Off")
        self.circle_1 = self.canvas.create_oval(50, 20, 150, 120, fill="red")
    # Create the label for the first circle right under it
        self.label_text_1 = self.canvas.create_text(100, 100, text="Pump 1 Off", fill="yellow", font=("Rockwell Extra Bold", 12, "bold"))
    # Create the second red circle on the canvas (initially "Pump Off")
        self.circle_2 = self.canvas.create_oval(50, 200, 150, 300, fill="red")
    # Create the label for the second circle right under it
        self.label_text_2 = self.canvas.create_text(100, 280, text="Pump 2 Off", fill="yellow", font=("Rockwell Extra Bold", 12, "bold"))
    # Create the third red circle on the canvas (initially "Pump Off")
        self.circle_3 = self.canvas.create_oval(50, 380, 150, 480, fill="red")
    # Create the label for the third circle right under it
        self.label_text_3 = self.canvas.create_text(100, 460, text="Pump 3 Off", fill="yellow", font=("Rockwell Extra Bold", 12, "bold"))
    # Create the label for the third circle right under it
        self.circle_4 = self.canvas.create_oval(600, 280, 800, 480, fill="blue")
    # Create the label for the fourth circle right under it 
        self.label_text_4 = self.canvas.create_text(700, 380, text="Emergency Stop", fill="yellow", font=("Rockwell Extra Bold", 12, "bold"))

#Valves  
    # Valve 3 - Adjusted to match the size of self.circle_8 and moved 10 pixels left
        self.circle_5 = self.canvas.create_oval(730, 10, 791, 71, fill="red")  # Shifted 10 pixels left
        self.label_text_5 = self.canvas.create_text(760.5, 81, text="Valve 3 Off", fill="yellow", font=("Rockwell Extra Bold", 8, "bold"))
    # Valve 2 - Adjusted to match the size and staggered like self.circle_9, moved 10 pixels left
        self.circle_6 = self.canvas.create_oval(664, 25, 725, 86, fill="red")  # Shifted 10 pixels left
        self.label_text_6 = self.canvas.create_text(694.5, 96, text="Valve 2 Off", fill="yellow", font=("Rockwell Extra Bold", 8, "bold"))
    # Valve 1 - Adjusted to match the size and staggered like self.circle_10, moved 10 pixels left
        self.circle_7 = self.canvas.create_oval(598, 40, 659, 101, fill="red")  # Shifted 10 pixels left
        self.label_text_7 = self.canvas.create_text(628.5, 111, text="Valve 1 Off", fill="yellow", font=("Rockwell Extra Bold", 8, "bold"))

#HEAT
        #MASH HEATER(elctric)
        self.circle_8 = self.canvas.create_oval(729, 165, 790, 226, fill="red")
    # Create the label for the first circle right under it
        self.label_text_8 = self.canvas.create_text(759.5, 236, text="Elec_HT Off", fill="black", font=("Rockwell Extra Bold", 9))
    #Pre Heat (gas Ignition)
        self.circle_9 = self.canvas.create_oval(663, 165 - 15, 724, 226 - 15, fill="red")
    # Create the label for the first circle right under it
        self.label_text_9 = self.canvas.create_text(693.5, 236 - 15, text="Ign Mash Off", fill="black", font=("Rockwell Extra Bold", 9))
    #Boil heat (gas ignition)
        self.circle_10 = self.canvas.create_oval(597, 165 - 30, 658, 226 - 30, fill="red")
    # Create the label for the first circle right under it
        self.label_text_10 = self.canvas.create_text(627.5, 236 - 30, text="Ign Boil Off", fill="black", font=("Rockwell Extra Bold", 9))


        
    #Strike water, Pre Boil, and Sparge water
        t_strike, v_strike, pre_boil_vol, sparge_wtr = self.calculate_strike_water()
        self.label_text_11 = self.canvas.create_text(352, 90, text="Strike Water Temperature C: {:.2f}".format(t_strike), fill="red", font=("Rockwell Extra Bold", 14, "bold"))       
        self.label_text_12 = self.canvas.create_text(335, 115, text="Strike Water Volume (Gal): {:.2f}".format(v_strike), fill="red", font=("Rockwell Extra Bold", 14, "bold"))
        self.label_text_13 = self.canvas.create_text(310, 140, text="Pre-Boil Volume (Gal): {:.2f}".format(pre_boil_vol), fill="red", font=("Rockwell Extra Bold", 14, "bold"))
        self.label_text_14 = self.canvas.create_text(300, 165, text="Sparge Water (Gal): {:.2f}".format(sparge_wtr), fill="red", font=("Rockwell Extra Bold", 14, "bold"))
    
    # Bind mouse click events to the circles
        self.canvas.tag_bind(self.circle_1, '<Button-1>', lambda event: self.toggle_pump(event, 1))
        self.canvas.tag_bind(self.circle_2, '<Button-1>', lambda event: self.toggle_pump(event, 2))
        self.canvas.tag_bind(self.circle_3, '<Button-1>', lambda event: self.toggle_pump(event, 3))
        self.canvas.tag_bind(self.circle_4, '<Button-1>', lambda event: self.toggle_pump(event, 4))
        self.canvas.tag_bind(self.circle_5, '<Button-1>', lambda event: self.toggle_pump(event, 5))
        self.canvas.tag_bind(self.circle_6, '<Button-1>', lambda event: self.toggle_pump(event, 6))
        self.canvas.tag_bind(self.circle_7, '<Button-1>', lambda event: self.toggle_pump(event, 7))
        self.canvas.tag_bind(self.circle_8, '<Button-1>', lambda event: self.toggle_pump(event, 8))
        self.canvas.tag_bind(self.circle_9, '<Button-1>', lambda event: self.toggle_pump(event, 9))
        self.canvas.tag_bind(self.circle_10, '<Button-1>', lambda event: self.toggle_pump(event, 10))
    # Initialize the pump state variables
        self.pump_on_1 = False
        self.pump_on_2 = False
        self.pump_on_3 = False
        self.pump_on_4 = True
        self.pump_on_5 = False
        self.pump_on_6 = False
        self.pump_on_7 = False
        self.pump_on_8 = False
        self.pump_on_9 = False
        self.pump_on_10 = False
    # Start displaying temperature labels
        self.create_labels()
        self.display_temperature_labels()
        self.canvas.pack()
    # Keep a reference to the background image to prevent garbage collection
        self.canvas.background_image = self.background_image
        
    def toggle_pump(self, event, pump_number):
        if pump_number == 4:
        # If pump 4 is on, turn off all pumps
            if self.pump_on_4:
                self.turn_off_all_pumps()
        # If pump 4 is off, do nothing
            else:
                return
        else:
        # If pump 4 is on, do not allow other pumps to turn on
            if self.pump_on_4:
                return
            self.toggle_individual_pump(pump_number)

    def turn_off_all_pumps(self):
        # Set all pump states to off
        self.pump_on_1 = False
        self.pump_on_2 = False
        self.pump_on_3 = False
        self.pump_on_4 = True  # This ensures that the pump 4 state is 'On' when used to turn off all pumps
        self.pump_on_5 = False
        self.pump_on_6 = False
        self.pump_on_7 = False
        self.pump_on_8 = False
        self.pump_on_9 = False
        self.pump_on_10 = False
    # Turn off all pumps
        GPIO.output(PUMP_1_PIN, GPIO.LOW)
        GPIO.output(PUMP_2_PIN, GPIO.LOW)
        GPIO.output(PUMP_3_PIN, GPIO.LOW)
        GPIO.output(PUMP_5_PIN, GPIO.LOW)
        GPIO.output(PUMP_6_PIN, GPIO.LOW)
        GPIO.output(PUMP_7_PIN, GPIO.LOW)
        GPIO.output(PUMP_8_PIN, GPIO.LOW)  #UPDATE BEFORE REMOVING
        GPIO.output(PUMP_9_PIN, GPIO.LOW)  #UPDATE BEFORE REMOVING
        GPIO.output(PUMP_10_PIN, GPIO.LOW)  #UPDATE BEFORE REMOVING
    # Update visuals for all pumps to show the "Off" state
        self.canvas.itemconfig(self.circle_1, fill="red")
        self.canvas.itemconfig(self.circle_2, fill="red")
        self.canvas.itemconfig(self.circle_3, fill="red")
        self.canvas.itemconfig(self.circle_4, fill="red")
        self.canvas.itemconfig(self.circle_5, fill="red")
        self.canvas.itemconfig(self.circle_6, fill="red")
        self.canvas.itemconfig(self.circle_7, fill="red")
        
    # Update the text labels for all pumps
        self.canvas.itemconfig(self.label_text_1, text="Pump 1 Off")
        self.canvas.itemconfig(self.label_text_2, text="Pump 2 Off")
        self.canvas.itemconfig(self.label_text_3, text="Pump 3 Off")
        self.canvas.itemconfig(self.label_text_4, text="EMERGENCY STOP ON")
        self.canvas.itemconfig(self.label_text_5, text="Valve 1 Off")
        self.canvas.itemconfig(self.label_text_6, text="Valve 2 Off")
        self.canvas.itemconfig(self.label_text_7, text="Valve 3 Off")
       
    def toggle_individual_pump(self, pump_number, valve_state):
    # Toggle the state of the individual pump
        pump_state = getattr(self, f'pump_on_{pump_number}')
        setattr(self, f'pump_on_{pump_number}', not pump_state)
        

    # Control the pump GPIO pin
        GPIO.output(globals()[f'PUMP_{pump_number}_PIN'], GPIO.HIGH if getattr(self, f'pump_on_{pump_number}') else GPIO.LOW)

    # Update the circle color based on pump state
        self.canvas.itemconfig(globals()[f'circle_{pump_number}'], fill="blue" if getattr(self, f'pump_on_{pump_number}') else "red")

    # Update the label text based on pump state
        self.canvas.itemconfig(globals()[f'label_text_{pump_number}'], text=f"Pump {pump_number} {'On' if getattr(self, f'pump_on_{pump_number}') else 'Off'}")

    def toggle_pump(self, event, pump_number):
        if pump_number == 1:
            self.pump_on_1 = not self.pump_on_1
            new_state = "On" if self.pump_on_1 else "Off"
            GPIO.output(PUMP_1_PIN, GPIO.HIGH if self.pump_on_1 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_1, fill="blue" if self.pump_on_1 else "red")
            self.canvas.itemconfig(self.label_text_1, text=f"Pump 1 {new_state}")
        elif pump_number == 2:
            self.pump_on_2 = not self.pump_on_2
            new_state = "On" if self.pump_on_2 else "Off"
            GPIO.output(PUMP_2_PIN, GPIO.HIGH if self.pump_on_2 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_2, fill="blue" if self.pump_on_2 else "red")
            self.canvas.itemconfig(self.label_text_2, text=f"Pump 2 {new_state}")
        elif pump_number == 3:
            self.pump_on_3 = not self.pump_on_3
            new_state = "On" if self.pump_on_3 else "Off"
            GPIO.output(PUMP_3_PIN, GPIO.HIGH if self.pump_on_3 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_3, fill="blue" if self.pump_on_3 else "red")
            self.canvas.itemconfig(self.label_text_3, text=f"Pump 2 {new_state}")
            #EMERGENCY STOP BUTTON
        elif pump_number == 4:
            self.pump_on_4 = not self.pump_on_4
            new_state = "On" if self.pump_on_4 else "Off"
            self.canvas.itemconfig(self.circle_4, fill="blue" if self.pump_on_4 else "red")
            self.canvas.itemconfig(self.label_text_4, text=f"Emergency Stop")
            self.canvas.itemconfig(self.circle_1, fill="red")
            self.canvas.itemconfig(self.label_text_1, text="Pump 1 Off")
            GPIO.output(PUMP_1_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_2, fill="red")
            self.canvas.itemconfig(self.label_text_2, text="Pump 2 Off")
            GPIO.output(PUMP_2_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_3, fill="red")
            self.canvas.itemconfig(self.label_text_3, text="Pump 3 Off")
            GPIO.output(PUMP_3_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_5, fill="red")
            self.canvas.itemconfig(self.label_text_5, text="Valve 1 Off")
            GPIO.output(PUMP_5_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_6, fill="red")
            self.canvas.itemconfig(self.label_text_6, text="Valve 2 Off")
            GPIO.output(PUMP_6_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_7, fill="red")
            self.canvas.itemconfig(self.label_text_7, text="Valve 3 Off")
            GPIO.output(PUMP_7_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_8, fill="red")
            self.canvas.itemconfig(self.label_text_8, text="Elec_HT Off")
            GPIO.output(PUMP_8_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_9, fill="red")
            self.canvas.itemconfig(self.label_text_9, text="Ign Mash Off")
            GPIO.output(PUMP_9_PIN, GPIO.LOW)
            self.canvas.itemconfig(self.circle_10, fill="red")
            self.canvas.itemconfig(self.label_text_10, text="Ign Boil Off")
            GPIO.output(PUMP_10_PIN, GPIO.LOW)
            self.master.after(3000, lambda: self.canvas.itemconfig(self.circle_4, fill="blue"))
            self.pump_on_4 = False
            print ("EMERGENCY STOP ALL OFF")
            
    #Valves
            #valve3
        elif pump_number == 5:
            self.pump_on_5 = not self.pump_on_5
            new_state = "On" if self.pump_on_5 else "Off"
            GPIO.output(PUMP_5_PIN, GPIO.HIGH if self.pump_on_5 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_5, fill="blue" if self.pump_on_5 else "red")
            self.canvas.itemconfig(self.label_text_5, text=f"Valve 3 {new_state}")
            #valve2
        elif pump_number == 6:
            self.pump_on_6 = not self.pump_on_6
            new_state = "On" if self.pump_on_6 else "Off"
            GPIO.output(PUMP_6_PIN, GPIO.HIGH if self.pump_on_6 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_6, fill="blue" if self.pump_on_6 else "red")
            self.canvas.itemconfig(self.label_text_6, text=f"Valve 2 {new_state}")
            #valve1
        elif pump_number == 7:
            self.pump_on_7 = not self.pump_on_7
            new_state = "On" if self.pump_on_7 else "Off"
            GPIO.output(PUMP_7_PIN, GPIO.HIGH if self.pump_on_7 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_7, fill="blue" if self.pump_on_7 else "red")
            self.canvas.itemconfig(self.label_text_7, text=f"Valve 1 {new_state}")
    #HEAT
            #
        elif pump_number == 8:
            self.pump_on_8 = not self.pump_on_8
            new_state = "On" if self.pump_on_8 else "Off"
            GPIO.output(PUMP_5_PIN, GPIO.HIGH if self.pump_on_8 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_8, fill="yellow" if self.pump_on_8 else "red")
            self.canvas.itemconfig(self.label_text_8, text=f"Elec_HT {new_state}")
            #valve2
        elif pump_number == 9:
            self.pump_on_9 = not self.pump_on_9
            new_state = "On" if self.pump_on_9 else "Off"
            GPIO.output(PUMP_9_PIN, GPIO.HIGH if self.pump_on_9 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_9, fill="yellow" if self.pump_on_9 else "red")
            self.canvas.itemconfig(self.label_text_9, text=f"Ign Mash {new_state}")
            #valve1
        elif pump_number == 10:
            self.pump_on_10 = not self.pump_on_10
            new_state = "On" if self.pump_on_10 else "Off"
            GPIO.output(PUMP_10_PIN, GPIO.HIGH if self.pump_on_10 else GPIO.LOW)  # Control GPIO pin
            self.canvas.itemconfig(self.circle_10, fill="yellow" if self.pump_on_10 else "red")
            self.canvas.itemconfig(self.label_text_10, text=f"Ign Boil {new_state}")    
        
            
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MashApp(root)
        root.mainloop()
        #self.master = root
    finally:
        # Clean up GPIO pins when the program exits
        GPIO.cleanup()
