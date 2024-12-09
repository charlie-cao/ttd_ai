import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="max-w-4xl mx-auto text-center">
      <h1 className="text-4xl font-bold mb-8">Welcome to TDD Todo</h1>
      <p className="text-xl text-gray-600 mb-12">
        A simple todo application built with Test-Driven Development
      </p>

      {isAuthenticated ? (
        <div className="space-y-6">
          <p className="text-lg">
            Welcome back, <span className="font-semibold">{user?.username}</span>!
          </p>
          <Link
            to="/todos"
            className="inline-block px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Go to Your Todos
          </Link>
        </div>
      ) : (
        <div className="space-y-8">
          <p className="text-lg text-gray-600">
            Please login or register to start managing your todos
          </p>
          <div className="space-x-4">
            <Link
              to="/login"
              className="inline-block px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Login
            </Link>
            <Link
              to="/register"
              className="inline-block px-8 py-3 bg-white text-gray-700 rounded-lg border border-gray-300 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Register
            </Link>
          </div>
        </div>
      )}

      <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Simple & Intuitive</h2>
          <p className="text-gray-600">
            Easy to use interface for managing your daily tasks
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Secure</h2>
          <p className="text-gray-600">
            Built with modern security practices to protect your data
          </p>
        </div>
        <div className="p-6 bg-white rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Reliable</h2>
          <p className="text-gray-600">
            Developed using Test-Driven Development for maximum reliability
          </p>
        </div>
      </div>
    </div>
  );
} 