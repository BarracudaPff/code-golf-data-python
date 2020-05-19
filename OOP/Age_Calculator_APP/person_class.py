import datetime
import tkinter as tk
window = tk.Tk()
window.geometry("400x400")
window.title("Age Calculator APP!")
year_label = tk.Label(text="Year")
year_label.grid(column=0, row=1)
month_label = tk.Label(text="Month")
month_label.grid(column=0, row=2)
day_label = tk.Label(text="Day")
day_label.grid(column=0, row=3)
year_entry = tk.Entry()
year_entry.grid(column=1, row=1)
month_entry = tk.Entry()
month_entry.grid(column=1, row=2)
day_entry = tk.Entry()
day_entry.grid(column=1, row=3)
def calculate_age():
	print("Button was clicked!")
calculate_button = tk.Button(text="Calculate Now!", command=calculate_age)
calculate_button.grid(column=1, row=4)
class Person:
	def __init__(self, name, birthdate):
		self.name = name
		self.birthdate = birthdate
	def age(self):
		today = datetime.date.today()
		age = today.year - self.birthdate.year
		return age
qazi = Person("Qazi", datetime.date(1940, 8, 20))
window.mainloop()