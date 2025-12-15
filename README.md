# PSD Analyst - Statistical Data Analysis Application

A comprehensive web-based statistical analysis application built with Streamlit, designed specifically for manufacturing industries (foundry and machining) to perform quality control and process analysis.

## 🎯 Features

### Data Input & Management
- **Multiple Input Methods:**
  - Upload CSV files with customizable delimiters and encoding
  - Upload Excel files (.xlsx, .xls) with sheet selection
  - Manual data entry with dynamic table editor
- **Data Manipulation:**
  - Add/remove rows and columns
  - Rename columns
  - Real-time data editing

### Data Visualization
- **Histogram** - Distribution analysis
- **Boxplot** - Outlier detection and quartile analysis
- **Scatter Plot** - Correlation visualization
- **Heatmap** - Correlation matrix with color coding
- **Q-Q Plot** - Normality assessment

### Statistical Analysis

#### Normality Tests
- Shapiro-Wilk Test
- Kolmogorov-Smirnov Test
- Anderson-Darling Test
- Ryan-Joiner Test
- D'Agostino's K² Test

#### Hypothesis Testing
- **Parametric Tests:**
  - One-Sample t-Test
  - Two-Sample t-Test (Independent)
  - Paired t-Test
  - One-Sample z-Test
  - One-Sample Proportion Test
  - Two-Sample Proportion Test
  - Variance Test (F-Test)
  - One-Way ANOVA
  
- **Non-Parametric Tests:**
  - Mann-Whitney U Test
  - Wilcoxon Signed-Rank Test

#### Data Transformation & Normalization
- Min-Max Scaling (0-1 normalization)
- Standardization (Z-Score)
- Log Transformation
- Box-Cox Transformation

### User Management & Security
- User registration and login system
- Role-based access control (Admin/User)
- Guest access option
- Admin approval workflow for new users
- SQLite database for user authentication

### Admin Controls
- Feature management (enable/disable specific analysis tools)
- User approval system
- Role management
- User deletion

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## 🚀 Installation

1. Clone or download this repository:
```bash
git clone <repository-url>
cd "trial cloning minitab"
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Ensure you have the following files in the same directory:
   - `cloning minitab.py` (main application file)
   - `gambarlogo.png` (logo image)
   - `icon.png` (page icon)

## 💻 Usage

1. Run the application:
```bash
streamlit run "cloning minitab.py"
```

2. The application will open in your default web browser at `http://localhost:8501`

3. **Login Options:**
   - **Default Admin Account:**
     - Username: `Prime`
     - Password: `666666`
   - **Guest Access:** Click "Login sebagai Tamu" for immediate access
   - **Create New Account:** Register and wait for admin approval

## 📊 Application Workflow

### For Users:
1. **Login** to the application
2. **Upload or Input Data:**
   - Upload CSV/Excel file, or
   - Use manual data entry
3. **View Data:**
   - Check data table and descriptive statistics
   - Visualize data with various plot types
4. **Perform Analysis:**
   - Run normality tests
   - Conduct hypothesis testing
   - Transform and normalize data
5. **Interpret Results:**
   - Review p-values and statistical outputs
   - Use the help section for guidance

### For Admins:
1. **Approve New Users** in the Admin Setting tab
2. **Manage Features** - Enable or disable specific analysis tools
3. **Manage Users** - Change roles or remove users
4. **Monitor System** - Review all registered users

## 🏭 Industry-Specific Use Cases

### Quality Control
- Verify product dimensions meet specifications
- Detect outliers in manufacturing processes
- Compare quality between different machines or shifts

### Process Validation
- Test if process changes have significant effects
- Validate consistency across production batches
- Monitor process stability over time

### Data-Driven Decision Making
- Statistical evidence for process improvements
- Identify sources of variation
- Support ISO/TS quality standards

## 📚 Help & Documentation

The application includes comprehensive help documentation covering:
- **Normality Tests:** When and how to use them
- **Data Normalization:** Different methods and their applications
- **Hypothesis Testing:** Detailed explanations with manufacturing examples
- **p-value Interpretation:** Clear guidelines for decision making

## 🗃️ Database Structure

The application uses SQLite database (`aplikasi_db.sqlite`) with two tables:

### Users Table
- `id` (TEXT, PRIMARY KEY) - User ID
- `password` (TEXT) - User password
- `role` (TEXT) - User role (Admin/User)
- `status` (TEXT) - Account status (pending/approved)

### Features Table
- `feature_name` (TEXT, PRIMARY KEY) - Feature name
- `is_enabled` (INTEGER) - Feature status (0/1)

## 🔒 Security Notes

- Passwords are stored in plain text in the SQLite database
- For production use, implement proper password hashing (e.g., bcrypt)
- Consider using environment variables for sensitive configuration
- Implement HTTPS for secure data transmission

## 🛠️ Customization

### Adding Custom Features
Modify the `default_features` dictionary in `init_db()` function to add new features.

### Changing Logo/Icon
Replace `gambarlogo.png` and `icon.png` with your custom images.

### Adjusting Plot Sizes
Use the slider controls in the visualization sections to customize graph dimensions.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or support, please contact the development team or refer to the in-app help documentation.

## 🔄 Version History

- **Version 1.0** (December 2025)
  - Initial release
  - Complete statistical analysis suite
  - User management system
  - Admin controls

## 🙏 Acknowledgments

- Built with Streamlit
- Statistical functions powered by SciPy and StatsModels
- Visualization using Matplotlib and Seaborn

---

**Note:** This application is designed for educational and professional use in manufacturing quality control. Always validate critical decisions with domain experts and follow your organization's quality standards.
