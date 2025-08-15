# Quiz App - Flask + SQLite

A modern, feature-rich quiz application built with Flask and SQLite. This application provides both admin and user interfaces for creating, managing, and taking quizzes.

## Features

### Admin Features
- **Dashboard**: Overview of all quizzes and management options
- **Create Quizzes**: Add new quizzes with categories
- **Add Questions**: Create multiple-choice questions for each quiz
- **View Questions**: Review all questions in a quiz
- **View Attempts**: Monitor all user quiz attempts and scores

### User Features
- **Take Quizzes**: Interactive quiz-taking interface
- **View Results**: See detailed quiz results with scores and feedback
- **Score History**: Track all quiz attempts and performance
- **User Registration**: Create new user accounts

### Technical Features
- **Secure Authentication**: Password hashing with PBKDF2
- **Session Management**: Secure user sessions
- **Responsive Design**: Modern, mobile-friendly UI
- **SQLite Database**: Lightweight, file-based database
- **Flash Messages**: User-friendly notifications

## Installation

1. **Clone or download the project**
   ```bash
   cd quiz_app_flask
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The application will automatically create the database and admin user

## Default Admin Account

The application automatically creates an admin account:
- **Username**: `admin`
- **Password**: `admin123`

**Important**: Change these credentials in production!

## Database Schema

The application uses SQLite with the following tables:

### Users
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Hashed password
- `role`: 'admin' or 'user'
- `created_at`: Account creation timestamp

### Quizzes
- `id`: Primary key
- `name`: Quiz name
- `category`: Quiz category
- `created_by`: Admin user ID
- `created_at`: Creation timestamp

### Questions
- `id`: Primary key
- `quiz_id`: Foreign key to quizzes
- `question`: Question text
- `option_a`, `option_b`, `option_c`, `option_d`: Answer options
- `correct_option`: Correct answer (A, B, C, or D)

### Attempts
- `id`: Primary key
- `user_id`: Foreign key to users
- `quiz_id`: Foreign key to quizzes
- `started_at`, `finished_at`: Timestamps
- `total_questions`: Number of questions in quiz
- `score`: User's score
- `details_json`: Detailed attempt data

## Scoring System

- **Correct Answer**: +4 points
- **Wrong Answer**: -1 point
- **No Answer**: 0 points

## Usage Guide

### For Admins

1. **Login** with admin credentials
2. **Create a Quiz**:
   - Go to Admin Dashboard
   - Click "Create New Quiz"
   - Enter quiz name and select category
3. **Add Questions**:
   - Click "Add Question" on any quiz
   - Enter question text and 4 options
   - Select the correct answer
4. **Monitor Performance**:
   - View all attempts in "View All Attempts"
   - See user scores and performance statistics

### For Users

1. **Register** a new account or **Login** with existing credentials
2. **Browse Quizzes** on the home page
3. **Take a Quiz**:
   - Click "Take Quiz" on any available quiz
   - Answer all questions (required)
   - Submit to see results
4. **View History**:
   - Check "My Scores" to see all attempts
   - Track your progress over time

## File Structure

```
quiz_app_flask/
│
├── app.py                  # Main Flask application
├── quiz.db                 # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── static/                 # Static files
│   └── style.css          # CSS styles
│
└── templates/              # HTML templates
    ├── base.html          # Base template with navigation
    ├── index.html         # Home page
    ├── login.html         # Login form
    ├── register.html      # Registration form
    ├── admin_dashboard.html    # Admin dashboard
    ├── create_quiz.html   # Create quiz form
    ├── add_question.html  # Add question form
    ├── view_questions.html     # View quiz questions
    ├── view_attempts.html      # View all attempts
    ├── take_quiz.html     # Quiz taking interface
    ├── quiz_result.html   # Quiz results page
    └── my_scores.html     # User score history
```

## Customization

### Adding New Categories
Edit the `create_quiz.html` template to add new quiz categories in the select dropdown.

### Changing Scoring
Modify the scoring logic in the `take_quiz` route in `app.py`.

### Styling
Customize the appearance by editing `static/style.css`.

## Security Notes

- Change the `secret_key` in `app.py` for production
- Use environment variables for sensitive configuration
- Consider using HTTPS in production
- Regularly backup the SQLite database

## Troubleshooting

### Database Issues
- Delete `quiz.db` to reset the database
- The application will recreate it automatically

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application. 