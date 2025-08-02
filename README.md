# Mark My Paper - AI-Powered Answer Sheet Grading

A modern web application that uses AI to automatically grade handwritten answer sheets. Built with Flask, Transformers, and MongoDB.

## Features

- 🤖 **AI-Powered OCR**: Advanced handwriting recognition using TrOCR
- 📊 **Smart Grading**: Customizable keyword-based grading system
- 🔐 **User Authentication**: Secure JWT-based authentication
- 📱 **Modern UI**: Beautiful, responsive design with dark theme
- ⚡ **Real-time Processing**: Instant grading results
- 📈 **Analytics**: Detailed performance insights

## Tech Stack

- **Backend**: Flask, Python
- **AI/ML**: Transformers, TrOCR, BERT
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: JWT (JSON Web Tokens)

## Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd answer-sheet-grading
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     env\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update the connection string in `app.py` if using Atlas:
     ```python
     client = MongoClient("mongodb+srv://username:password@cluster.mongodb.net/")
     ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The application will be running on port 5000

## Project Structure

```
answer-sheet-grading/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/               # Static files (CSS, JS)
│   ├── home.css         # Home page styles
│   ├── login.css        # Login page styles
│   └── upload.css       # Upload page styles
└── templates/           # HTML templates
    ├── home.html        # Landing page
    ├── login.html       # Login/Register page
    └── index.html       # Upload page
```

## Usage

1. **Home Page** (`/`)
   - Landing page with feature overview
   - Navigation to other sections

2. **Login/Register** (`/login.html`)
   - User authentication
   - JWT token management
   - Password reset functionality

3. **Upload & Grade** (`/upload`)
   - Drag & drop file upload
   - Customizable grading criteria
   - Real-time AI processing
   - Results display

## API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login
- `GET /api/user` - Get user info (protected)
- `POST /api/logout` - User logout (protected)

### Password Reset
- `POST /api/reset-password-request` - Request password reset
- `POST /api/reset-password` - Reset password with token

### File Processing
- `GET /upload` - Upload form
- `POST /upload` - Process uploaded file

## Grading System

The application uses a keyword-based grading system:

1. **Upload Answer Sheet**: Scan or upload handwritten answer sheets
2. **Set Criteria**: Define keywords and their weights
3. **AI Processing**: OCR extracts text from handwriting
4. **Grading**: System matches keywords and calculates scores
5. **Results**: Display extracted text and final score

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
MONGODB_URI=mongodb://localhost:27017
FLASK_ENV=development
```

### MongoDB Setup
1. Install MongoDB Community Edition
2. Start MongoDB service
3. Create database `userdb`
4. Create collection `users`

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Debug Mode
The application runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## AI Models Used

- **TrOCR**: Microsoft's Transformer OCR for handwriting recognition
- **BERT**: Bidirectional Encoder Representations for text analysis
- **Vision Encoder Decoder**: For image-to-text conversion

## Security Features

- JWT-based authentication
- Password hashing with Werkzeug
- CORS support for cross-origin requests
- Input validation and sanitization
- Secure file upload handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Acknowledgments

- Microsoft for TrOCR model
- Hugging Face for Transformers library
- Flask community for the web framework
- MongoDB for the database solution
