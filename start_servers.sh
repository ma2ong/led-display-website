#!/bin/bash
# Start both frontend and backend servers

echo "🚀 Starting LED Display Website - Full Stack"
echo "============================================"

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask==2.3.3 werkzeug==2.3.7 flask-cors==4.0.0 pillow==10.0.1

# Initialize database
echo "🗄️ Initializing database..."
cd admin
python -c "from app import init_db; init_db(); print('Database initialized successfully')"

# Start backend server in background
echo "🔧 Starting backend server..."
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Go back to root directory
cd ..

# Start frontend server
echo "🌐 Starting frontend server..."
python -m http.server 8080 &
FRONTEND_PID=$!

echo "✅ Both servers started successfully!"
echo "🌐 Frontend: http://localhost:8080"
echo "🔧 Admin Panel: http://localhost:5000"
echo "👤 Admin Login: admin / admin123"

# Keep script running
wait $FRONTEND_PID