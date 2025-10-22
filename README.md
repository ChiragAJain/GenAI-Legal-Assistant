# GenAI Legal Assistant

A modern, intelligent web application that transforms complex legal documents into clear, actionable insights using Google's Generative AI. Upload your Terms & Conditions, contracts, or legal documents and get comprehensive analysis with interactive Q&A capabilities.

## Features

### GenAI-Powered Analysis
- **Abstractive Summarization** - Uses Google's Gemini AI for human-like summaries
- **Interactive Q&A** - Ask specific questions about your document and get instant answers
- **Risk Analysis** - Automatically identifies potentially risky or non-standard clauses
- **Plain Language Translation** - Complex legal jargon explained in simple terms

### Modern User Experience
- **Fully Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- **Multiple File Formats** - Supports PDF, TXT, and DOCX files (up to 8MB)
- **Drag & Drop Upload** - Easy file upload with visual feedback
- **Real-time Processing** - Fast document analysis with progress indicators
- **PDF Export** - Download comprehensive analysis as formatted PDF files

### Smart Features
- **Document Intelligence** - Understands legal document structure and context
- **Customizable Analysis** - Adjust summary depth and focus areas
- **Feedback System** - Built-in user feedback collection for continuous improvement
- **Multi-mode Support** - Falls back gracefully when GenAI is unavailable

## Technology Stack

- **Backend**: Flask (Python) with SQLite database
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **GenAI**: Google Gemini Pro for document analysis and Q&A
- **Fallback AI**: Legal Pegasus model for offline processing
- **Document Processing**: PyPDF2, python-docx for file handling
- **Styling**: Modern CSS with CSS Grid and Flexbox
- **Development**: GCP Cloud Run deployment

## How It Works

1. **Upload**: Drag and drop or select your legal document (PDF, TXT, or DOCX)
2. **AI Analysis**: Google's Gemini AI analyzes the document structure and content
3. **Smart Summary**: Get key points, rights, obligations, and important terms
4. **Risk Assessment**: Automatically identifies potentially problematic clauses
5. **Interactive Q&A**: Ask specific questions about any part of the document
6. **Export**: Download comprehensive analysis as a formatted PDF

## Quick Start

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChiragAJain/Terms-and-Condition-Summariser-using-NLP
   cd genai-legal-assistant
   ```
2. **Install the required modules**
   ```
   pip install -r requirements.txt
   ```
3. **Configure API key (optional for GenAI features)**
   
   Edit the `.env` file and replace:
   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   ```
   
   With your actual API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`


## Responsive Design

The application features a mobile-first responsive design that adapts to all screen sizes:

- **Mobile (< 480px)**: Optimized touch interface with stacked layouts
- **Tablet (480px - 768px)**: Balanced layout with improved spacing
- **Desktop (> 768px)**: Full-featured layout with side-by-side elements

## UI Features

- **Modern Design System**: Consistent colors, typography, and spacing
- **Smooth Animations**: Subtle transitions and hover effects
- **Loading States**: Visual feedback during file processing
- **Error Handling**: User-friendly error messages and validation
- **Accessibility**: Semantic HTML and keyboard navigation support

## Future Work & Roadmap
To evolve the GenAI Legal Assistant into a more robust and globally capable platform, the future roadmap is focused on three key areas:

- **Custom Fine-Tuned Models**: Transition from using pre-trained models like Legal Pegasus to fine-tuning a specialized, open-source LLM on a curated corpus of legal documents. This will significantly enhance the model's accuracy, domain-specific knowledge, and ability to generate more nuanced legal insights.

- **Enhanced User Interface**: Redesign the front-end with a modern JavaScript framework like React.js to create a more dynamic, professional, and intuitive user experience. This will include adding features for better document management, advanced visualization of risk analysis, and real-time collaboration.

- **Internationalization and Legal Context**: Expand the model's knowledge base to include legal frameworks and policies from different countries. This will involve training the model to recognize and adapt its analysis based on the jurisdiction of a document, providing globally-aware legal context and insights.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source and available under the [GPL 3.0 License](LICENSE).

## Troubleshooting

### Common Issues

**"ModuleNotFoundError" when running the app:**
- Run `requirements.txt` to install dependencies
- Make sure you're using Python 3.8 or higher

**GenAI features not working:**
- Check that your `.env` file has a valid `GEMINI_API_KEY`
- Make sure the API key is not the placeholder `your-gemini-api-key-here`
- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Verify your API key has access to Gemini models
- The app will fall back to pegasus-based analysis without a valid API key

**File upload not working:**
- Check that the `static` directory exists (created automatically by setup scripts)
- Ensure file size is under 8MB
- Supported formats: PDF, TXT, DOCX

**Port already in use:**
- Another application might be using port 5000
- Stop other Flask applications or change the port in `app.py`

## Configuration

### Environment Variables

The application uses a `.env` file for configuration (created automatically on first run):

- `GEMINI_API_KEY`: Required for GenAI features. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- `FLASK_ENV`: Set to `development` for local development
- `FLASK_DEBUG`: Set to `True` for debug mode
- `DATABASE_URL`: SQLite database path (default: `sqlite:///project.db`)

### Operating Modes

The application automatically detects available dependencies and operates in the best available mode:

1. **GenAI Mode**: Full features with Google Gemini AI (requires API key)
2. **HuggingFace Mode**: Legal Pegasus + KeyBERT analysis (requires ML dependencies)
3. **Lite Mode**: Rule-based analysis (minimal dependencies)

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for advanced language understanding
- [Legal Pegasus Model](https://huggingface.co/nsi319/legal-pegasus) for legal text summarization
- Modern web design principles and responsive design patterns
- Flask development server for local testing

