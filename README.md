# Django eCommerce Website

This project is a full-fledged eCommerce website built using Django, a high-level Python web framework. It includes essential features such as user authentication, product browsing, cart management, checkout process, payment integration, and more. The website is designed to be robust, scalable, and user-friendly, providing a seamless shopping experience for customers.

## Table of Contents
- [Features](#features)
- [Screenshots](#screenshots)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- **User Authentication:** Secure user registration, login, reset password, and profile management.
  ```
      username: pankajbind
      password: Pankajbind30@

- **Product Catalog:** Browse and search products with detailed descriptions and images.
- **Shopping Cart:** Add, update, and remove items from the cart seamlessly.
- **Checkout Process:** Smooth checkout flow with order summary and address management.
- **Order Management:** View order history and status updates.
- **Responsive Design:** Mobile-friendly UI ensuring a consistent experience across devices.

## Future update
- **Payment integration**
- **Wishlist**
- **Admin panel**
- **UI enhancement**

## Screenshots

### Home Page
![{06FC7346-23E7-4B78-AF20-C3EF43440CEA}](https://github.com/user-attachments/assets/11990918-f13c-4b28-95e1-2b5dc7a48376)

### Wishlist Page
![{11C7A442-CB64-4431-8F66-D2D6519F2EB3}](https://github.com/user-attachments/assets/265c278e-a408-4021-943a-143c309b033d)

### Contact-Us Page
![{35798118-B966-435A-AACF-5AA6948426A8}](https://github.com/user-attachments/assets/0616fe79-e6b5-4952-a68f-ab8f0b05a8c9)

### About-Us Page
![{C3AB3E3F-5ADC-49BB-9A48-183DBA6D0DF4}](https://github.com/user-attachments/assets/6aedc30a-df5b-4736-8943-65a62c934bba)

### Product Page
![{31E93E0A-115A-48E2-9C44-43701F3B3F58}](https://github.com/user-attachments/assets/dc91a0af-5f9c-4dad-b5cc-4b67effbc680)

### Shopping Cart Page
![{E38440A2-E859-4D44-BD8B-31C53A359C8B}](https://github.com/user-attachments/assets/41ad05a4-c1a1-4aa4-b8be-9fe43dca7f5f)

### Login Page
![{D7D0E1AA-8CE4-4D41-AE5A-6C1333F9BE8E}](https://github.com/user-attachments/assets/887e0565-9f6b-46d7-b572-018bdd0f0f3f)

### Register Page
![{DBF9E159-6903-4A8D-9D98-A40294036DE9}](https://github.com/user-attachments/assets/44f44b34-f1bf-421d-9887-1887b292c575)

### Forgot Password Page
![{1AACDF37-FF5B-4107-851E-85A2A16F1CBD}](https://github.com/user-attachments/assets/511a3e68-b479-4d58-a8b8-4f14ac919015)

### Profile Page
![{C5D1385E-6B94-4652-90CE-E88FC957A56C}](https://github.com/user-attachments/assets/e57b0e5c-5faf-4c68-9d30-bb9c3fbf612c)

### Address Page
![{E2A8FBD0-44AE-4BB3-85CE-88F849BEA990}](https://github.com/user-attachments/assets/9d5ff7b4-ef12-4133-8878-07f5d7e00fb9)

### Change Password View
![{DCF16406-F2A1-4E65-823E-89AFDF4581DD}](https://github.com/user-attachments/assets/6e848666-ec6f-4425-9d0b-fa0ad3f3195d)


## Technologies Used
- **Django:** Python-based web framework for backend development.
- **HTML/CSS/JavaScript:** Frontend development for a responsive and interactive UI.
- **Razorpay API:** Payment gateway integration for secure transactions.{Future development}
- **Bootstrap:** Frontend framework for responsive design and UI components.

## Setup Instructions
To run this project locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pankaj-bind/Django-eCommerce-Website.git
   cd Django-eCommerce-Website
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
   
3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Open your web browser and navigate to:**
   ```
   http://127.0.0.1:8000/
   ```

## Usage
- **Admin Panel:** Access the admin panel at `http://127.0.0.1:8000/admin/` to manage products, orders, and users.
- **Shopping:** Browse products, add items to the cart, proceed to checkout, and make payments using Razorpay.
- **Profile:** Users can register, login, reset their password, view their order history, and update their profiles.

## Contributing
Contributions are welcome! Please fork this repository and create a pull request with your proposed features, enhancements, or bug fixes.

## License
This project is licensed under the [MIT License](LICENSE).

