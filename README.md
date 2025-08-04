# 🥗 Calorie Tracker
A full-stack web application that helps users monitor their daily calorie and macronutrient intake. Users can upload food images, and the app uses a large language model to estimate macronutrient data (calories, protein, carbs, and fat) for easy logging and visualization.

## 🔗 Live Demo
🌐 Visit the working site here: https://calorie-tracker-sage.vercel.app

## 🔧 Features
🔐 User Authentication: Secure registration and login using JSON Web Tokens (JWT).

📷 Image Analysis: Upload food images and extract nutrition data using a large language model.

📊 Progress Tracking: Visualize daily calorie, protein, carbohydrate, and fat consumption.

🗄️ Persistent Storage: PostgreSQL database powered by SQLAlchemy ORM.

🌐 Deployment: Backend deployed with Railway, frontend hosted on Vercel.

🔄 Cross-Origin Support: Configured CORS for seamless communication between frontend and backend.

🎨 Design: Figma mockups to guide responsive and user-friendly UI development.

## 🛠️ Tech Stack
Frontend: React.js, Tailwind CSS

Backend: Flask, SQLAlchemy, JWT, OpenAI API

Database: PostgreSQL (via Railway)

Deployment: Railway (backend), Vercel (frontend)
