import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Navbar } from './components/layout/Navbar'
import { Home } from './pages/Home'
import { LoginForm } from './components/auth/LoginForm'
import { RegisterForm } from './components/auth/RegisterForm'

function App() {
  const handleLogin = async (data: { email: string; password: string }) => {
    console.log('Login:', data)
    // TODO: 实现登录逻辑
  }

  const handleRegister = async (data: { username: string; email: string; password: string }) => {
    console.log('Register:', data)
    // TODO: 实现注册逻辑
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={
              <div className="pt-24">
                <LoginForm onSubmit={handleLogin} />
              </div>
            }
          />
          <Route
            path="/register"
            element={
              <div className="pt-24">
                <RegisterForm onSubmit={handleRegister} />
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  )
}

export default App
