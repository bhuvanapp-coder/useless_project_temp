# Notes But Not The Notes 🎯

## Basic Details

### Team Name: Unhinged

### Team Members

* Team Lead: Bhuvana P P - CHRIST College of Engineering, Irinjalakuda
* Member 2: Aswathy M S - CHRIST College of Engineering, Irinjalakuda

### Project Description

**Notes But Not The Notes** is an AI-powered study assistant that does exactly what you don't want it to do.

Upload your exam PDF and ask it to teach you. Instead of explaining the important topics, it confidently focuses on completely useless information like page numbers, headers, footers, author names, formatting, and other meaningless details.

### The Problem (that doesn't exist)

Students have a serious problem: **their notes contain too much useful information.**

Why waste time studying definitions, concepts, and important topics when you could spend your precious exam-preparation time learning that Chapter 3 starts on Page 27?

We decided to solve this completely imaginary crisis.

### The Solution (that nobody asked for)

Introducing **Notes But Not The Notes** — an AI tutor with exactly one mission:

> **Teach everything in the PDF except the actual notes.**

Upload a PDF and watch the AI transform useless information into unnecessarily confident lessons.

It can teach you:

* 📄 Page numbers
* 📝 Headers and footers
* 👤 Author names
* 📚 Table of contents
* 🔢 Formatting details
* 📑 Document metadata
* 🤡 Other completely irrelevant PDF information

Because if you're going to fail the exam, you might as well know the page numbers.

## Technical Details

### Technologies/Components Used

For Software:

* **Languages:** Python, JavaScript
* **Frontend:** React, Vite
* **Backend:** FastAPI
* **Libraries:** PyMuPDF (fitz), OpenAI API
* **Database/Services:** Supabase
* **Styling:** CSS
* **Tools:** VS Code, Git, GitHub
* **Deployment:** Vercel / Render

For Hardware:

* No special hardware required
* Any computer capable of running a modern web browser
* Internet connection required for AI-powered features

### Implementation

For Software:

The application follows a simple frontend-backend architecture.

1. User uploads an exam PDF through the React frontend.
2. The FastAPI backend receives the PDF.
3. PyMuPDF extracts document information and text.
4. The application identifies the deliberately useless parts of the document.
5. The AI generates hilariously unnecessary explanations based on those details.
6. The frontend displays the useless lessons and interactions to the user.

# Installation

Clone the repository and install the required dependencies.

```bash
git clone https://github.com/bhuvanapp-coder/useless_project_temp.git
cd useless_project_temp
npm install
pip install -r backend/requirements.txt
```

# Run

Start the backend:

```bash
python -m uvicorn backend.app.main:app --reload
```

Start the frontend in another terminal:

```bash
npm run dev
```

Then open the local URL provided by Vite in your browser.

### Project Documentation

For Software:

# Screenshots (Add at least 3)

![Screenshot1](Add screenshot 1 here with proper name)

*The main interface where users upload their exam PDF.*

![Screenshot2](Add screenshot 2 here with proper name)

*The AI proudly teaching completely useless information from the uploaded notes.*

![Screenshot3](Add screenshot 3 here with proper name)

*The final results showing the user's newly acquired and absolutely unnecessary knowledge.*

# Diagrams

![Workflow](Add your workflow/architecture diagram here)

*Workflow showing PDF upload → backend processing → useless information extraction → AI generation → frontend display.*

For Hardware:

# Schematic & Circuit

**Not applicable — this is a software-only project.**

# Build Photos

**Not applicable — this is a software-only project.**

### Project Demo

# Video

[Add your demo video link here]

*The demo shows the complete journey from uploading an exam PDF to receiving completely useless AI-generated lessons.*

# Additional Demos

* Live project demo: Add deployed link here
* GitHub repository: Add repository link here

## Team Contributions

* **Bhuvana P P:** Project concept and ideation, frontend development, UI design, React/Vite implementation, backend integration, testing and documentation.
* **Aswathy M S:** Project ideation, feature design, AI interaction concepts, frontend support, testing, debugging and presentation.

---

Made with ❤️ at TinkerHub Useless Projects

[![TinkerHub](https://img.shields.io/badge/TinkerHub-24-black)](https://www.tinkerhub.org/)
[![Useless Projects](https://img.shields.io/badge/Useless%20Projects-26--26-black)](https://tinkerhub.org/events/1M8ORET9A1/useless-projects-3.0)

![Static Badge](https://img.shields.io/badge/TinkerHub-24?color=%23000000&link=https%3A%2F%2Fwww.tinkerhub.org%2F)
![Static Badge](https://img.shields.io/badge/UselessProjects--26-26?link=https%3A%2F%2Ftinkerhub.org%2Fevents%2F1M8ORET9A1%2Fuseless-projects-3.0)



