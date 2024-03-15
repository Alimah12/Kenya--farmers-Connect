from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window  # Import Window to get window dimensions
import mysql.connector
from kivy.uix.popup import Popup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Establish MySQL connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="*.*dennis",
    database="ruto"
)

mycursor = mydb.cursor()

# Function to create the users table if it does not exist
def create_users_table():
    mycursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            gender VARCHAR(255),
            region VARCHAR(255)
        )
    """)

# Call the function to create the users table
create_users_table()

# Function to insert product into MySQL database
def insert_product(product_name, quantity, amount):
    sql = "INSERT INTO products (product_name, quantity, amount) VALUES (%s, %s, %s)"
    val = (product_name, quantity, amount)
    mycursor.execute(sql, val)
    mydb.commit()
    print("Product inserted successfully.")

# Function to fetch user details from MySQL database
def get_user_details(email):
    sql = "SELECT * FROM users WHERE email = %s"
    val = (email,)
    mycursor.execute(sql, val)
    result = mycursor.fetchone()  # Fetch a single row
    return result

class FarmerLoginScreen(Screen):
    def login(self):
        email = self.ids.email_input.text
        password = self.ids.password_input.text
        print("Login clicked with email:", email, "and password:", password)
        if self.verify_login(email, password):
            self.show_toast("Login successful!")
            self.manager.current = 'dashboard'
        else:
            self.show_popup("Invalid credentials.")

    def verify_login(self, email, password):
        sql = "SELECT * FROM users WHERE email = %s AND password = %s"
        val = (email, password)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()
        if user:
            return True
        else:
            return False

    def show_toast(self, text):
        toast = Popup(title='Notification', content=Label(text=text), size_hint=(None, None), size=(250, 150))
        toast.open()

    def show_popup(self, text):
        invalid_popup = Popup(title='Error', content=Label(text=text), size_hint=(None, None), size=(250, 150))
        invalid_popup.open()

class RegistrationScreen(Screen):
    def register(self):
        username = self.ids.username_input.text
        email = self.ids.email_input.text  # Added email field
        password = self.ids.password_input.text
        confirm_password = self.ids.confirm_password_input.text
        gender = self.ids.gender_input.text
        region = self.ids.region_spinner.text
        print("Registration completed with username:", username, ", email:", email, ", password:", password, ", gender:", gender,
              ", region:", region)
        
        # Insert user information into the users table
        sql = "INSERT INTO users (username, email, password, gender, region) VALUES (%s, %s, %s, %s, %s)"
        val = (username, email, password, gender, region)
        mycursor.execute(sql, val)
        mydb.commit()
        print("User registered successfully.")

class DashboardScreen(Screen):
    def sell_product(self, product):
        print("Product sold:", product)

    def communicate_buyer(self, message):
        chat_screen = self.manager.get_screen('chat')  # Get reference to the chat screen
        chat_screen.start_conversation(message)  # Start the conversation with the provided message
        self.manager.current = 'chat'  # Navigate to the chat screen

    def predict_weather(self):
        self.manager.current = 'weather'

    def logout(self):
        self.manager.current = 'login'

    def view_profile(self):
        email = self.manager.get_screen('login').ids.email_input.text
        user = get_user_details(email)
        if user:
            self.manager.get_screen('profile').display_profile(user)

    def add_product(self):
        product_popup = ProductPopup()
        product_popup.open()

class ProfileScreen(Screen):
    def display_profile(self, user):
        if user:
            self.ids.username_label.text = "Username: " + user['username']
            self.ids.email_label.text = "Email: " + user['email']
            self.ids.gender_label.text = "Gender: " + user['gender']
            self.ids.region_label.text = "Region: " + user['region']

class WeatherScreen(Screen):
    pass

class ProductPopup(Popup):
    def __init__(self, **kwargs):
        super(ProductPopup, self).__init__(**kwargs)
        self.title = 'Add Product'
        self.size_hint = (None, None)
        self.size = (400, 300)
        layout = GridLayout(cols=2, padding=10, spacing=10)

        layout.add_widget(Label(text='Product Name:'))
        self.product_name_input = TextInput(multiline=False)
        layout.add_widget(self.product_name_input)

        layout.add_widget(Label(text='Quantity:'))
        self.quantity_input = TextInput(multiline=False)
        layout.add_widget(self.quantity_input)

        layout.add_widget(Label(text='Selling Amount:'))
        self.amount_input = TextInput(multiline=False)
        layout.add_widget(self.amount_input)

        self.add_widget(layout)

        button_layout = GridLayout(cols=2, spacing=10)

        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_button)

        add_button = Button(text='Add')
        add_button.bind(on_press=self.add_product)
        button_layout.add_widget(add_button)

        self.add_widget(button_layout)

    def add_product(self, instance):
        product_name = self.product_name_input.text
        quantity = self.quantity_input.text
        amount = self.amount_input.text
        print("Product Name:", product_name)
        print("Quantity:", quantity)
        print("Amount:", amount)
        insert_product(product_name, quantity, amount)
        self.dismiss()

from kivy.uix.popup import Popup

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super(ChatScreen, self).__init__(**kwargs)
        self.chat_history = TextInput(readonly=True, size_hint_y=None, height=200)
        self.new_message = TextInput(size_hint_y=None, height=100, multiline=False)
        self.mpesa_number_input = TextInput(hint_text='Enter M-Pesa Number', size_hint_y=None, height=40, multiline=False)
        self.pay_button = Button(text='Pay', size_hint_y=None, height=50)
        self.pay_button.bind(on_press=self.prompt_email)
        self.send_button = Button(text='Send', size_hint_y=None, height=50)
        self.send_button.bind(on_press=self.send_message)
        self.back_button = Button(text='Back', size_hint_y=None, height=50)
        self.back_button.bind(on_press=self.go_back)
        
        self.layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10])
        self.layout.add_widget(Label(text="Chat with Buyer", font_size=24, size_hint_y=None, height=50))
        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.new_message)
        self.layout.add_widget(self.mpesa_number_input)
        button_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=50)
        button_layout.add_widget(self.pay_button)
        button_layout.add_widget(self.send_button)
        button_layout.add_widget(self.back_button)
        self.layout.add_widget(button_layout)

        self.scroll_view = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll_view.add_widget(self.layout)
        self.add_widget(self.scroll_view)
        Clock.schedule_once(self.start_conversation, 1)

    def start_conversation(self, dt):
        self.add_to_chat_history("Welcome to the selling and buying platform. How can I assist you?")

    def send_message(self, instance):
        message = self.new_message.text
        mpesa_number = self.mpesa_number_input.text  # Get M-Pesa number input
        self.new_message.text = ''  
        self.add_to_chat_history("You: " + message)
        
        response = self.generate_response(message)
        self.add_to_chat_history("Buyer: " + response)

        # Check if the message contains a request for payment
        if "pay" in message.lower():
            # Initiate payment process with M-Pesa number
            self.initiate_payment(mpesa_number)

    def generate_response(self, message):
        # Check if the message contains any of the products
        if "watermelon" in message.lower():
            return "I'm interested in buying watermelon. What's the price per unit?"
        elif "mango" in message.lower():
            return "Do you have ripe mangoes available for sale?"
        elif "maize" in message.lower():
            return "I need maize for animal feed. Can you provide bulk quantities?"
        elif "wheat" in message.lower():
            return "Are you selling wheat flour or grains?"
        else:
            return "Could you please provide more details?"

    def add_to_chat_history(self, message):
        self.chat_history.text += message + '\n'
        
    def go_back(self, instance):
        self.manager.current = 'dashboard'

    def initiate_payment(self, mpesa_number):
        if mpesa_number:  # Check if M-Pesa number is provided
            # Prepare transaction details
            transaction_details = {'amount': 100, 'recipient': mpesa_number}  # Example transaction details
        
            # Initiate payment
            payment_response = initiate_payment(transaction_details)
        
            # Process payment response
            if payment_response['success']:
                self.add_to_chat_history("Payment initiated successfully. Please confirm on your M-Pesa.")
            else:
                self.add_to_chat_history("Payment initiation failed. Please try again.")
        else:
            self.add_to_chat_history("Please provide your M-Pesa number to initiate payment.")

    def prompt_email(self, instance):
        # Display a popup to prompt the user to input their email
        content = BoxLayout(orientation='vertical', spacing=10, padding=[20])
        email_input = TextInput(hint_text='Enter Email', multiline=False)
        submit_button = Button(text='Submit', size_hint_y=None, height=40)
        content.add_widget(email_input)
        content.add_widget(submit_button)
        
        popup = Popup(title='Enter Email',
                      content=content,
                      size_hint=(None, None), size=(300, 200))
        
        submit_button.bind(on_press=lambda x: self.on_submit_email(email_input.text, popup))
        
        popup.open()

    def on_submit_email(self, email, popup):
        popup.dismiss()
        if email:
            self.add_to_chat_history(f"Email submitted: {email}")
        else:
            self.add_to_chat_history("Please enter a valid email.")

class FarmerLoginApp(App):
    def build(self):
        Builder.load_string('''
<FarmerLoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [50, 20]
        canvas.before:
            Color:
                rgba: 0, 0, 1, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            text: 'Farmer Login'
            font_size: 24
        TextInput:
            id: email_input
            hint_text: 'Email'
        TextInput:
            id: password_input
            hint_text: 'Password'
            password: True
        Button:
            text: 'Login'
            size_hint_y: None
            height: 40
            on_press: root.login()
        Button:
            text: 'Register'
            size_hint_y: None
            height: 40
            on_press: root.manager.current = 'registration'

<RegistrationScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [50, 20]
        canvas.before:
            Color:
                rgba: 0, 0, 1, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            text: 'Registration'
            font_size: 24
        TextInput:
            id: username_input
            hint_text: 'Username'
        TextInput:
            id: email_input  # Added email field
            hint_text: 'Email'
        TextInput:
            id: password_input
            hint_text: 'Password'
            password: True
        TextInput:
            id: confirm_password_input
            hint_text: 'Confirm Password'
            password: True
        TextInput:
            id: gender_input
            hint_text: 'Gender (Male/Female)'
        Spinner:
            id: region_spinner
            text: 'Select Region'
            values: ('Makueni', 'Machakos', 'Uasin Gishu', 'Kericho', 'Nyeri', 'Muranga', 'Nakuru', 'Bungoma')
        TextInput:
            id: phone_input
            hint_text: 'Phone Number'
        Button:
            text: 'Register'
            size_hint_y: None
            height: 40
            on_press: root.register()
        Button:
            text: 'Back to Login'
            size_hint_y: None
            height: 40
            on_press: root.manager.current = 'login'

<DashboardScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [50, 20]
        canvas.before:
            Color:
                rgba: 1, 0, 1, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            text: 'WELCOME TO DASHBOARD'
            font_size: 48
            size_hint_y: None
            height: 80
            pos_hint: {'center_x': 0.5}
        BoxLayout:
            orientation: 'horizontal'
            spacing: 10
            TextInput:
                id: product_input
                hint_text: 'Enter product to sell'
                size_hint_y: None
                height: 40
            Button:
                text: 'Add Product'
                size_hint_y: None
                height: 40
                on_press: root.add_product()
        GridLayout:
            id: grid_layout
            cols: 2
            spacing: 10
            Button:
                text: 'View Profile'
                size_hint_y: None
                height: 40
                on_press: root.view_profile()
            Button:
                text: 'Sell Mango'
                size_hint_y: None
                height: 40
                on_press: root.sell_product('Mango')
            Button:
                text: 'Sell Maize'
                size_hint_y: None
                height: 40
                on_press: root.sell_product('Maize')
            Button:
                text: 'Sell Pineapple'
                size_hint_y: None
                height: 40
                on_press: root.sell_product('Pineapple')
            Button:
                text: 'Sell Watermelon'
                size_hint_y: None
                height: 40
                on_press: root.sell_product('Watermelon')
            Button:
                text: 'Communicate with Buyer'
                size_hint_y: None
                height: 40
                on_press: root.communicate_buyer('Hello, I want to buy your products.')
            Button:
                text: 'Predict Weather'
                size_hint_y: None
                height: 40
                on_press: root.predict_weather()
    Button:
        text: 'Logout'
        size_hint_y: None
        height: 40
        on_press: root.logout()

<ProfileScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [50, 20]
        canvas.before:
            Color:
                rgba: 1, 1, 1, 1
            Rectangle:
                size: self.size
                pos: self.pos
        Label:
            id: username_label
            text: ''
            font_size: 24
        Label:
            id: email_label
            text: ''
            font_size: 24
        Label:
            id: gender_label
            text: ''
            font_size: 24
        Label:
            id: region_label
            text: ''
            font_size: 24
        Button:
            text: 'Back to Dashboard'
            size_hint_y: None
            height: 40
            on_press: root.manager.current = 'dashboard'

<WeatherScreen>:
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [50, 20]
        Label:
            text: "Today's Weather: Sunny"  # Placeholder for weather information

''')
        sm = ScreenManager()
        sm.add_widget(FarmerLoginScreen(name='login'))
        sm.add_widget(RegistrationScreen(name='registration'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(WeatherScreen(name='weather'))
        sm.add_widget(ChatScreen(name='chat'))
        return sm

if __name__ == '__main__':
    FarmerLoginApp().run()
