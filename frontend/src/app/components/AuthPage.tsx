import React, { useState } from 'react';
import { User, Mail, Lock, Sparkles } from 'lucide-react';

interface AuthPageProps {
  initialMode: 'login' | 'signup';
  onLoginSuccess: (token: string) => void;
}

export function AuthPage({ initialMode, onLoginSuccess }: AuthPageProps) {
  const [isLogin, setIsLogin] = useState(initialMode === 'login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/auth/token', {
          method: 'POST',
          body: formData
        });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Login failed. Please check credentials.');
        }
        const data = await response.json();
        onLoginSuccess(data.access_token);
      } else {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.detail || 'Registration failed.');
        }
        setIsLogin(true);
        setError('Registration successful! Please log in.');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-[calc(100vh-60px)] flex items-center justify-center bg-[#f4f6f8] py-12 px-4 overflow-hidden">
      {/* Decorative background geometric shapes */}
      <div className="absolute -bottom-16 -left-16 w-64 h-64 bg-amber-400/30 rounded-full blur-2xl pointer-events-none" />
      <div className="absolute -top-20 -right-20 w-80 h-80 bg-rose-500/20 rounded-full blur-3xl pointer-events-none" />

      {/* Split Card Container */}
      <div className="relative bg-white rounded-3xl shadow-2xl border border-gray-100 w-full max-w-4xl overflow-hidden flex flex-col md:flex-row min-h-[520px] transition-all duration-500">
        
        {/* Left Side: Welcome Overlay Banner */}
        <div className={`w-full md:w-5/12 bg-gradient-to-br from-emerald-600 via-teal-600 to-emerald-700 text-white p-8 md:p-10 flex flex-col justify-between relative overflow-hidden transition-all duration-500 ${isLogin ? 'order-first' : 'order-first'}`}>
          {/* Watermark shapes */}
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-3xl transform rotate-45 pointer-events-none" />
          <div className="absolute -bottom-10 -left-10 w-48 h-48 bg-white/10 rounded-full pointer-events-none" />

          {/* Logo / Branding */}
          <div className="relative z-10 flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">ArXivist AI</span>
          </div>

          {/* Welcome Text Content */}
          <div className="relative z-10 my-10 text-center">
            <h2 className="text-3xl font-extrabold mb-4 leading-tight">
              {isLogin ? 'Welcome Back!' : 'Hello, Friend!'}
            </h2>
            <p className="text-emerald-100 text-sm leading-relaxed max-w-xs mx-auto mb-8 font-light">
              {isLogin 
                ? 'To keep connected with us please login with your personal info' 
                : 'Enter your personal details and start your research journey with us'}
            </p>

            {/* Toggle Button */}
            <button
              type="button"
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
              className="inline-block px-10 py-2.5 border-2 border-white text-white font-semibold text-xs tracking-wider rounded-full hover:bg-white hover:text-emerald-700 transition-all duration-300 shadow-sm uppercase transform hover:scale-105 active:scale-95"
            >
              {isLogin ? 'SIGN UP' : 'SIGN IN'}
            </button>
          </div>

          {/* Footer watermark */}
          <div className="relative z-10 text-center text-[11px] text-emerald-200/80">
            © 2026 ArXivist AI Assistant
          </div>
        </div>

        {/* Right Side: Form Panel */}
        <div className="w-full md:w-7/12 bg-white p-8 md:p-12 flex flex-col justify-center relative">
          <div className="max-w-md mx-auto w-full">
            
            {/* Title */}
            <h2 className="text-3xl font-extrabold text-emerald-600 text-center mb-4 tracking-tight">
              {isLogin ? 'Sign In' : 'Create Account'}
            </h2>

            {/* Social Logins */}
            <div className="flex items-center justify-center gap-3 mb-6">
              <button 
                type="button" 
                className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 hover:shadow-md transition-all text-sm"
              >
                f
              </button>
              <button 
                type="button" 
                className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 hover:shadow-md transition-all text-xs"
              >
                G+
              </button>
              <button 
                type="button" 
                className="w-10 h-10 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 hover:shadow-md transition-all text-xs"
              >
                in
              </button>
            </div>

            <p className="text-center text-xs text-gray-400 mb-6">
              {isLogin ? 'or use your account credentials:' : 'or use your email for registration:'}
            </p>

            {/* Error or Success Banner */}
            {error && (
              <div className={`p-3.5 mb-5 text-xs rounded-xl transition-all ${
                error.includes('successful') 
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              }`}>
                {error}
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              
              {!isLogin && (
                <div className="relative flex items-center bg-gray-50/80 rounded-xl px-4 py-3 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                  <User className="w-4 h-4 text-gray-400 mr-3 shrink-0" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Name"
                    className="w-full bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none"
                  />
                </div>
              )}

              <div className="relative flex items-center bg-gray-50/80 rounded-xl px-4 py-3 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                <Mail className="w-4 h-4 text-gray-400 mr-3 shrink-0" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Username / Email"
                  className="w-full bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none"
                />
              </div>

              <div className="relative flex items-center bg-gray-50/80 rounded-xl px-4 py-3 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                <Lock className="w-4 h-4 text-gray-400 mr-3 shrink-0" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none"
                />
              </div>

              {isLogin && (
                <div className="text-right">
                  <button type="button" className="text-xs text-gray-400 hover:text-emerald-600 transition-colors">
                    Forgot your password?
                  </button>
                </div>
              )}

              <div className="pt-2 text-center">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-12 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs tracking-wider rounded-full shadow-md shadow-emerald-600/30 hover:shadow-lg hover:shadow-emerald-600/40 transition-all duration-300 uppercase transform active:scale-95 disabled:opacity-50"
                >
                  {loading ? 'Processing...' : isLogin ? 'SIGN IN' : 'SIGN UP'}
                </button>
              </div>

            </form>

            <div className="mt-6 md:hidden text-center">
              <button
                type="button"
                onClick={() => { setIsLogin(!isLogin); setError(''); }}
                className="text-xs text-emerald-600 font-semibold hover:underline"
              >
                {isLogin ? "Need an account? Sign Up" : "Already have an account? Sign In"}
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
