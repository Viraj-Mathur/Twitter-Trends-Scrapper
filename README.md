

# Twitter Trends Scraper

## Overview
The **Twitter Trends Scraper** is a web-based application that fetches and displays the latest trending topics from Twitter. Using **Selenium** for web scraping and **Flask** for the backend, the application dynamically fetches trends, stores them in **MongoDB**, and presents them in a visually appealing interface.

---

## Features

- **Dynamic Scraping**: Scrape trending topics from Twitter in real time.
- **MongoDB Integration**: Save and retrieve trends from a MongoDB database.
- **Responsive UI**: Beautifully designed frontend with a modern and professional look.

---

## Technologies Used

- **Backend**: Flask
- **Web Scraping**: Selenium with undetected-chromedriver
- **Database**: MongoDB
- **Frontend**: HTML, CSS (with a modern gradient design)
- **Environment Management**: python-dotenv

---

## Project Structure

```
project/
├── app.py                   # Main Flask application
├── scrapper_module.py       # Selenium script to scrape Twitter trends
├── templates/
│   └── index.html           # Frontend HTML template
├── proxy_auth_plugin.py     # ProxyMesh plugin for Selenium (if using proxies)
├── .env                     # Environment variables (e.g., MongoDB URI)
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
```

---

## Prerequisites

1. **Python 3.7 or higher** installed on your system.
2. **MongoDB** instance (local or cloud, e.g., MongoDB Atlas).
3. Browser-compatible **ChromeDriver**.

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/twitter-trends-scraper.git
cd twitter-trends-scraper
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory with the following content:

```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>
PROXYMESH_USERNAME=your_proxymesh_username
PROXYMESH_PASSWORD=your_proxymesh_password
TWITTER_USERNAME=your_twitter_username
TWITTER_PASSWORD=your_twitter_password
```

Replace `<username>`, `<password>`, `<cluster>`, and `<database>` with your MongoDB and other service details.

---

## Usage

### 1. Start the Flask Application
```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

### 2. Interact with the Application
- **Homepage**: Click the `Fetch Trending Topics` button to trigger the scraper.
- **Results**: View the trending topics with their metadata, including IP address and JSON extract.

---




## Contributing

Contributions are welcome! If you'd like to improve this project:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request.

---



Feel free to adjust any section based on your specific implementation details or preferences. Let me know if you need further customization!