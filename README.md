# Terms and Conditions Summarizer

A modern, responsive web application that simplifies complex legal documents using AI. Upload your Terms & Conditions files and get easy-to-understand summaries with customizable length settings.

## ✨ Features

- **Fully Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- **AI-Powered Summarization** - Uses Legal Pegasus model for accurate legal text processing
- **Multiple File Formats** - Supports PDF, TXT, and DOCX files (up to 8MB)
- **⚙Customizable Output** - Adjust summary length with min/max word limits
- **PDF Export** - Download summaries as formatted PDF files
- **Modern UI/UX** - Clean, intuitive interface with smooth animations
- **Drag & Drop** - Easy file upload with drag and drop support
- **Feedback System** - Built-in user feedback collection

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **AI Model**: [Legal Pegasus](https://huggingface.co/nsi319/legal-pegasus)
- **Text Processing**: KeyBERT for vocabulary simplification
- **Styling**: Modern CSS with CSS Grid and Flexbox
- **Deployment**: Railway

## 📋 How It Works

1. **Upload**: Drag and drop or select your Terms & Conditions document
2. **Configure**: Set minimum and maximum word limits for summary sections
3. **Process**: AI analyzes the document and extracts key clauses
4. **Simplify**: Complex legal jargon is replaced with everyday language
5. **Download**: Get your simplified summary as a PDF file

## 🏃‍♂️ Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChiragAJain/Terms-and-Condition-Summariser-using-NLP
   cd terms-conditions-summarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`


## 📱 Responsive Design

The application features a mobile-first responsive design that adapts to all screen sizes:

- **Mobile (< 480px)**: Optimized touch interface with stacked layouts
- **Tablet (480px - 768px)**: Balanced layout with improved spacing
- **Desktop (> 768px)**: Full-featured layout with side-by-side elements

## 🎨 UI Features

- **Modern Design System**: Consistent colors, typography, and spacing
- **Smooth Animations**: Subtle transitions and hover effects
- **Loading States**: Visual feedback during file processing
- **Error Handling**: User-friendly error messages and validation
- **Accessibility**: Semantic HTML and keyboard navigation support

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Legal Pegasus Model](https://huggingface.co/nsi319/legal-pegasus) for legal text summarization
- [KeyBERT](https://pypi.org/project/keybert/) for vocabulary simplification
- Modern web design principles and responsive design patterns

