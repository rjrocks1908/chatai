# ChatAI - AI-Powered Code Generation Chat Application

A modern web application that provides an interactive chat interface for AI-powered code generation, featuring real-time streaming responses, code artifact management, and a beautiful user interface.

## 🚀 Live Demo

[https://chatai-beige.vercel.app](https://chatai-beige.vercel.app)

## 🏗️ Architecture

This application follows a modern full-stack architecture:

- **Frontend**: React + TypeScript + Vite + Redux Toolkit + Tailwind CSS
- **Backend**: FastAPI + Python + Gemini AI API
- **Real-time Communication**: Server-Sent Events (SSE) for streaming responses
- **State Management**: Redux Toolkit for predictable state management
- **Styling**: Tailwind CSS for responsive and modern UI

## 🛠️ Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rjrocks1908/chatai.git
   cd chatai/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory with the variables mentioned in the `.env.example` file.

5. **Run the backend server**
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   Create a `.env` file in the frontend directory with the variables mentioned in the `.env.example` file.

4. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

### Running the Complete Application

1. Start the backend server (from backend directory)
2. Start the frontend development server (from frontend directory)
3. Open `http://localhost:5173` in your browser

## 🎯 How I Approached the Problem

### 1. **Project Planning & Architecture Design**
I approached this AI-powered chat application with a systematic methodology:

- **Requirements Analysis**: Identified core features (real-time chat, code generation, artifact management)
- **Technology Stack Selection**: Chose modern, scalable technologies (React + FastAPI + Gemini AI)
- **Architecture Planning**: Designed a decoupled frontend-backend architecture with clear separation of concerns
- **User Experience Design**: Prioritized intuitive interactions and clean UI

### 2. **Development Methodology**
I followed an iterative development approach:

- **Bottom-up approach**: Started with core features and then added advanced features
- **Component-Driven Development**: Built reusable UI components with clear interfaces
- **State Management Strategy**: Implemented Redux Toolkit for predictable state management
- **API-First Design**: Designed RESTful APIs before implementing frontend features

### 3. **Key Technical Decisions**

#### **State Management Architecture**
- **Redux Toolkit**: Chose for state management

#### **Real-time Communication**
- **Server-Sent Events (SSE)**: Implemented for streaming responses
- **Chunked responses**: Handled partial content updates

#### **Code Artifact Management**
- **Message-artifact association**: Linked artifacts to specific messages
- **File download system**: Implemented client-side file generation
- **Preview functionality**: Real-time code preview with syntax highlighting

#### **UI/UX Design**
- **Loading states**: Smooth transitions and skeleton loaders
- **Error handling**: User-friendly error messages and recovery options

### 4. **Code Quality & Best Practices**

#### **TypeScript Implementation**
- **Interface segregation**: Clean separation of concerns
- **Type safety**: Compile-time error checking


#### **Error Handling**
- **Graceful degradation**: Fallback mechanisms for API failures
- **User feedback**: Clear error messages and recovery options
- **Logging**: Comprehensive error logging for debugging
