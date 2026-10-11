import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
import zxingcpp
import requests

#FUNCTION PLATE 1
def scan_barcode(image_path):
    img = Image.open(image_path)
    detected_barcodes = zxingcpp.read_barcodes(img)
    if len(detected_barcodes) > 0:
        return detected_barcodes[0].text
    else:
        return None


#FUNCTION PLATE 2
def fetch_product_data(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    # Websites often block scripts that don't identify themselves.
    # I added a "User-Agent" so the API knows we are a friendly app, not a malicious bot.
    headers = {
        "User-Agent": "ConsumerConsciousnessApp/1.0"
    }

    try:
        #  Im sending requests
        response = requests.get(url, headers=headers)

        # If the website sends back an error (like a 404 or 403), stop here
        if response.status_code != 200:
            return None
        data = response.json()

        # We Check if the product was successfully found (status == 1)
        if data.get("status") == 1:
            product = data.get("product", {})
            name = product.get("product_name", "Unknown Product Name")
            ingredients = product.get("ingredients_text", "Ingredients not listed.")
            nutriments = product.get("nutriments", {})
            sugar = nutriments.get("sugars_100g", 0)
            fat = nutriments.get("fat_100g", 0)
            salt = nutriments.get("salt_100g", 0)

            return name, ingredients, sugar, fat, salt
        else:
            return None

    except Exception:
        # To Catch JSON errors or loss of internet connection so the app doesn't crash
        return None


#IF ELSE ELIF LADDER FOR SAFTEY RATTING
def evaluate_health(sugar, fat, salt):

    # RED: Very unhealthy. 
    # If a product has more than 20g of sugar, OR more than 20g of fat, OR more than 1.5g of salt.
    if sugar > 20 or fat > 20 or salt > 1.5:
        color = "red"
        message = "RED RATING: Unhealthy. High in Sugar, Fat, or Salt!"

    # YELLOW: Moderate. 
    # If it didn't trigger the red warning, we check if it has moderate amounts.
    # More than 5g of sugar, OR 3g of fat, OR 0.3g of salt.
    elif sugar > 5 or fat > 3 or salt > 0.3:
        color = "yellow"
        message = "YELLOW RATING: Moderate. Shouldn't be consumed regularly."

    # GREEN: Healthy. 
    # If it passes both the RED and YELLOW checks, it is healthy.
    else:
        color = "green"
        message = "GREEN RATING: Healthy choice. Low in bad nutrients."

    return color, message

# FUNCTION 4 PLATE ( MORE BORING BACKEND CONDITIONING)
def process_image():
    # Open a file dialog to let the user select a picture
    file_path = filedialog.askopenfilename(
        title="Select a Barcode Picture",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )

    # If the user actually selected a file
    if file_path:
        text_box.delete("0.0", "end")
        rating_label.configure(text="", text_color="white")

        text_box.insert("end", "Scanning picture for barcode...\n\n")
        app.update()  # Refresh screen code

        barcode = scan_barcode(file_path)

        if barcode:
            text_box.insert("end", f"Barcode Found: {barcode}\nLooking up ingredients online...\n\n")
            app.update()

            # 2. Getting data
            product_data = fetch_product_data(barcode)

            if product_data:
                name, ingredients, sugar, fat, salt = product_data

                # 3. Evaluating health
                color, message = evaluate_health(sugar, fat, salt)

                # 4. Showing the results on screen
                text_box.insert("end", f"PRODUCT NAME: {name}\n\n")
                text_box.insert("end", f"INGREDIENTS:\n{ingredients}\n\n")
                text_box.insert("end", f"NUTRITION (per 100g):\n")
                text_box.insert("end", f"- Sugar: {sugar:.2f}g\n")
                text_box.insert("end", f"- Fat: {fat:.2f}g\n")
                text_box.insert("end", f"- Salt: {salt:.2f}g\n")
                rating_label.configure(text=message, text_color=color)

            else:
                text_box.insert("end", "Sorry, this product was not found in the database.")
        else:
            text_box.insert("end", "Could not find a barcode in this picture. Please try a clearer image.")


# User interface


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Consumer Consciousness")
app.geometry("600x700")

title = ctk.CTkLabel(app, text="Consumer Consciousness", font=("Arial", 28, "bold"))
title.pack(pady=20)

upload_btn = ctk.CTkButton(app, text="Attach Picture of Barcode", font=("Arial", 16), command=process_image)
upload_btn.pack(pady=10)

text_box = ctk.CTkTextbox(app, width=500, height=450, font=("Arial", 14), wrap="word")
text_box.pack(pady=20)

rating_label = ctk.CTkLabel(app, text="", font=("Arial", 20, "bold"))
rating_label.pack(pady=10)
app.mainloop()