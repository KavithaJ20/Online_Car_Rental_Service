# Online_Car_Rental_Service

🚗 Drive Wheels – Car Rental Web Application (Django)

Drive Wheels is a full-stack car rental web application built using Django. The project allows users to browse available cars, filter them based on preferences, book vehicles for a selected duration, and complete payments securely using Razorpay. It also includes user authentication, reviews, and an admin dashboard for management.

🔑 Key Features

-User Authentication

-User registration, login, and logout

-Secure password handling using Django authentication

-Car Listing & Filtering

-View available cars

Filter cars by:

-Fuel type

-Transmission

-Seating capacity

-Location

-Sort cars by price (low to high / high to low)

Car Booking System

Select car, date & time, and rental hours

Automatic total rent calculation

Booking history for logged-in users

Online Payment Integration

Razorpay payment gateway integration

Secure payment verification

Payment status tracking (Paid / Pending)

Customer Reviews

Users can submit ratings and reviews

Reviews displayed on the About Us page

Contact Form

Users can send queries or feedback

Stored securely in the database

Admin Panel

Manage cars, bookings, users, contacts, and reviews

View payment details and booking status

🛠️ Technologies Used

Backend: Django (Python)

Frontend: HTML, CSS, Bootstrap

Database: SQLite (default Django DB)

Payment Gateway: Razorpay

Authentication: Django Auth System

ORM: Django ORM

📂 Project Structure Overview

views.py – Handles business logic and request/response flow

models.py – Defines database models (Car, Booking, Review, Contact)

admin.py – Admin panel configurations

templates/ – HTML templates

static/ – CSS, JS, images

🎯 Purpose of the Project

This project is designed to demonstrate:

-Real-world Django CRUD operations

-Payment gateway integration

-Secure user authentication

-Scalable backend design for rental platforms

-It is suitable for academic projects, learning Django, and portfolio showcase.

📌 Future Enhancements

Email notifications for bookings

Booking cancellation & refunds

Car availability calendar

API support for mobile apps

Role-based admin access
