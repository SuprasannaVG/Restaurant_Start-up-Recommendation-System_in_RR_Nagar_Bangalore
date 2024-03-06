import tkinter as tk
from tkinter import messagebox
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

# Load dataset
df = pd.read_csv("RR_Nagar_Resto_Pred5.csv")

# Preprocess the data
# Handle missing values, encode categorical variables
# For simplicity, assuming categorical variables are already encoded

# Define features and target variable
features = df[['Address', 'type', 'dish_liked', 'cuisines', 'approx_cost', 'Zone']]
target = df['Rate']

# Convert non-numerical columns to numerical using Label Encoding
label_encoders = {}
for column in features.select_dtypes(include=['object']).columns:
    label_encoders[column] = LabelEncoder()
    features[column] = label_encoders[column].fit_transform(features[column])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Train a regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model and label encoders
joblib.dump(model, 'RRmodel.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')

# Get valid options for each column
valid_options = {}
for column in features.columns:
    valid_options[column] = df[column].unique()

# Create a function to validate user input
def validate_input(user_input):
    for key, value in user_input.items():
        if key == 'approx_cost':
            try:
                float(value)
            except ValueError:
                messagebox.showerror("Error", f"Invalid input for {key}. Please enter a numerical value.")
                return False
        elif value not in valid_options[key]:
            messagebox.showerror("Error", f"Invalid input for {key}. Please select from {valid_options[key]}.")
            return False
    return True

# Create an interface to predict rate based on selected inputs
def predict_rate(input_data):
    model = joblib.load('RRmodel.pkl')
    label_encoders = joblib.load('label_encoders.pkl')
    
    encoded_input = {}
    for column in ['Address', 'type', 'dish_liked', 'cuisines', 'Zone']:
        if column in input_data:
            encoded_input[column] = label_encoders[column].transform([input_data[column]])[0]
        else:
            encoded_input[column] = 0  # Assuming 0 for missing feature
    
    # Include the numerical value of 'approx_cost'
    if 'approx_cost' in input_data:
        encoded_input['approx_cost'] = float(input_data['approx_cost'])
    else:
        encoded_input['approx_cost'] = 0  # Assuming 0 for missing feature
    
    # Convert the dictionary of encoded values to a list
    encoded_values = [encoded_input[column] for column in ['Address', 'type', 'dish_liked', 'cuisines', 'approx_cost', 'Zone']]
    
    # Reshape the input data to 2D array for prediction
    predicted_rate = round(model.predict([encoded_values])[0],1)
    
    # Return prediction and predicted rating
    if predicted_rate >=4:
        return "Good idea", predicted_rate
    elif 3.5 <= predicted_rate <= 4.0:
        return "Average idea", predicted_rate
    else:
        return "Bad idea", predicted_rate

def predict_from_input():
    user_input = {}
    for key, option in options.items():
        user_input[key] = option.get()
    if validate_input(user_input):
        predicted_idea, predicted_rate = predict_rate(user_input)
        messagebox.showinfo("Prediction", f"Predicted idea: {predicted_idea}\nPredicted rating: {predicted_rate}")

# Create Tkinter window
root = tk.Tk()
root.title("Restaurant Start-up Idea Predictor")

# Add heading
heading_label = tk.Label(root, text="Restaurant Start-up Idea Predictor", font=("Arial", 16, "bold"))
heading_label.pack(pady=10)

# Create frame for input form
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# Create input fields using OptionMenu
options = {}
for i, column in enumerate(features.columns):
    tk.Label(input_frame, text=f"{column}:").grid(row=i, column=0, padx=5, pady=5, sticky="e")
    if column == 'approx_cost':
        options[column] = tk.Entry(input_frame)
        options[column].grid(row=i, column=1, padx=5, pady=5, sticky="w")
    else:
        options[column] = tk.StringVar(root)
        options[column].set(valid_options[column][0])  # Set default value
        option_menu = tk.OptionMenu(input_frame, options[column], *valid_options[column])
        option_menu.grid(row=i, column=1, padx=5, pady=5, sticky="w")

# Create Predict Button
predict_button = tk.Button(root, text="Predict", command=predict_from_input)
predict_button.pack()

# Run Tkinter event loop
root.mainloop()
