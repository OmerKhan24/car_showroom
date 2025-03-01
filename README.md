# 🚗 Car Showroom Management System  

A **web-based** Car Showroom Management System designed to streamline vehicle listings, user inquiries, test drive scheduling, and financial management.  

## 📌 Project URL  
🔗 [GitHub Repository](https://github.com/OmerKhan24/car_showroom)  

## 👨‍💻 Team Members  
- [**Omer Khan**](github.com/OmerKhan24)
- [**Muhib Siddiqui**](https://github.com/muhibsiddiqui)
- [**Salik Ahmad**](https://github.com/saliksalik) 
 

---

## ✨ Features  

### 🏁 User Features  
- ✅ **Vehicle Listings** – View cars, bikes, and 3-wheelers with details, filters, and search options.  
- ✅ **Test Drive Scheduling** – Book test drives for available vehicles.  
- ✅ **User Inquiries** – Submit inquiries about vehicles, features, and installment plans.  
- ✅ **Favorites/Wishlist** – Save vehicles for future reference.  
- ✅ **Finance Management** – Calculate down payments and monthly installments.  
- ✅ **User Profiles** – Register, log in, and update user details.  

### 🔧 Admin Features  
- 🔹 **Vehicle Management** – CRUD operations for managing vehicle listings.  
- 🔹 **User Management** – Approve and update user accounts.  
- 🔹 **Inquiry Handling** – Track and respond to customer inquiries.  
- 🔹 **Database Operations** – Advanced SQL queries, reports on vehicle inventory, user activities, and finances.  
- 🔹 **Features Management** – Link features to specific vehicle listings.  

---

## 🛠️ Technologies Used  
- **Front-End:** HTML, CSS, JavaScript  
- **Back-End:** Python Flask  
- **Database:** MySQL (via XAMPP/phpMyAdmin)  

---

## 🚀 How to Run the Project  

### Prerequisites  
Ensure you have the following installed:  
- 🔹 Python 3.x  
- 🔹 Flask  
- 🔹 MySQL (via XAMPP)  
- 🔹 ReactJS  

### **1️⃣ Setup XAMPP (MySQL & Apache Server)**  
1. **Download and Install XAMPP:**  
   - [Download XAMPP](https://www.apachefriends.org/download.html)  
   - Install and open the **XAMPP Control Panel**.  
2. **Start Apache & MySQL:**  
   - Click **Start** next to **Apache** and **MySQL** in the XAMPP Control Panel.  
   - Open **phpMyAdmin** by visiting: `http://localhost/phpmyadmin/`  

### **2️⃣ Import the SQL Database**  
1. Open **phpMyAdmin** (`http://localhost/phpmyadmin/`).  
2. Click on **Databases** → **Create a new database** (e.g., `car_showroom_db`).  
3. Click on the newly created database.  
4. Go to the **Import** tab → Click **Choose File** → Select the provided `car_showroom.sql` file.  
5. Click **Go** to import the database.  

### **3️⃣ Configure Database Credentials in Code**  
Edit the database connection settings in the **Flask backend code** (e.g., `config.py` or `app.py`):  

```python
DB_HOST = "localhost"  # Change if using a remote server
DB_USER = "root"       # Default XAMPP user
DB_PASSWORD = ""       # Leave empty if no password is set
DB_NAME = "car_showroom_db"  # The database you created in phpMyAdmin
```

### If you set a MySQL password, update `DB_PASSWORD` accordingly.  

---

### 4️⃣ Run the Backend (Flask Server)  

1. Open a terminal and navigate to the backend folder:  
   ```bash
   cd car_showroom/backend
   ```
2. Install dependencies:
  ```bash
     pip install -r requirements.txt
  ```
3. Run the Flask server:
  ```bash
     python app.py
  ```
4. The backend API should now run at:
  ```bash
     http://127.0.0.1:5000/
  ```

---

## 📌 Future Improvements
🚀 Add payment gateway integration for purchases.
🚀 Implement an AI-based recommendation system for vehicle suggestions.
🚀 Improve UI/UX for a better user experience.

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/OmerKhan24/car_showroom/blob/main/LICENSE) file for details.
