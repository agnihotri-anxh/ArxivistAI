import React, { useState } from 'react';
import { X, User, Mail, Lock, Sparkles } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (token: string) => void;
}

export function AuthModal({ isOpen, onClose, onLoginSuccess }: AuthModalProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

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
        const text = await response.text();
        let data: any = {};
        if (text && text.trim()) {
          try { data = JSON.parse(text); } catch {}
        }
        if (!response.ok) {
          throw new Error(data.detail || 'Login failed');
        }
        onLoginSuccess(data.access_token);
        onClose();
      } else {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password })
        });
        const text = await response.text();
        let data: any = {};
        if (text && text.trim()) {
          try { data = JSON.parse(text); } catch {}
        }
        if (!response.ok) {
          throw new Error(data.detail || 'Registration failed');
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
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md p-4 animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 w-full max-w-4xl overflow-hidden flex flex-col md:flex-row relative min-h-[480px]">
        {/* Close Button */}
        <button 
          onClick={onClose} 
          className="absolute top-4 right-4 z-20 w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 flex items-center justify-center transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Left Side: Welcome Banner */}
        <div className="w-full md:w-5/12 bg-gradient-to-br from-emerald-600 via-teal-600 to-emerald-700 text-white p-8 flex flex-col justify-between relative overflow-hidden">
          <div className="absolute -top-10 -right-10 w-36 h-36 bg-white/10 rounded-3xl transform rotate-45 pointer-events-none" />
          <div className="relative z-10 flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl bg-white/20 backdrop-blur-md flex items-center justify-center">
              <Sparkles className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold text-base tracking-tight">ArXivist AI</span>
          </div>

          <div className="relative z-10 my-8 text-center">
            <h2 className="text-2xl font-extrabold mb-3 leading-tight">
              {isLogin ? 'Welcome Back!' : 'Hello, Friend!'}
            </h2>
            <p className="text-emerald-100 text-xs leading-relaxed max-w-xs mx-auto mb-6 font-light">
              {isLogin 
                ? 'To keep connected with us please login with your personal info' 
                : 'Enter your personal details and start your research journey with us'}
            </p>
            <button
              type="button"
              onClick={() => { setIsLogin(!isLogin); setError(''); }}
              className="inline-block px-8 py-2 border-2 border-white text-white font-semibold text-xs tracking-wider rounded-full hover:bg-white hover:text-emerald-700 transition-all duration-300 shadow-sm uppercase"
            >
              {isLogin ? 'SIGN UP' : 'SIGN IN'}
            </button>
          </div>

          <div className="relative z-10 text-center text-[10px] text-emerald-200/80">
            ArXivist AI Portal
          </div>
        </div>

        {/* Right Side: Form Panel */}
        <div className="w-full md:w-7/12 bg-white p-8 md:p-10 flex flex-col justify-center">
          <div className="max-w-md mx-auto w-full">
            <h2 className="text-2xl font-extrabold text-emerald-600 text-center mb-4 tracking-tight">
              {isLogin ? 'Sign In' : 'Create Account'}
            </h2>

            <div className="flex items-center justify-center gap-2.5 mb-5">
              <button type="button" className="w-9 h-9 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 transition-all text-xs">f</button>
              <button type="button" className="w-9 h-9 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 transition-all text-xs">G+</button>
              <button type="button" className="w-9 h-9 rounded-full border border-gray-200 flex items-center justify-center text-gray-600 font-semibold hover:border-emerald-500 hover:text-emerald-600 transition-all text-xs">in</button>
            </div>

            <p className="text-center text-[11px] text-gray-400 mb-5">
              {isLogin ? 'or use your account credentials:' : 'or use your email for registration:'}
            </p>

            {error && (
              <div className={`p-3 mb-4 text-xs rounded-xl ${error.includes('successful') ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}`}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5">
              {!isLogin && (
                <div className="relative flex items-center bg-gray-50/80 rounded-xl px-3.5 py-2.5 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                  <User className="w-4 h-4 text-gray-400 mr-2.5 shrink-0" />
                  <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Name" className="w-full bg-transparent text-xs text-gray-800 placeholder-gray-400 outline-none" />
                </div>
              )}

              <div className="relative flex items-center bg-gray-50/80 rounded-xl px-3.5 py-2.5 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                <Mail className="w-4 h-4 text-gray-400 mr-2.5 shrink-0" />
                <input type="text" required value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Username / Email" className="w-full bg-transparent text-xs text-gray-800 placeholder-gray-400 outline-none" />
              </div>

              <div className="relative flex items-center bg-gray-50/80 rounded-xl px-3.5 py-2.5 border border-gray-100 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-2 focus-within:ring-emerald-500/20 transition-all">
                <Lock className="w-4 h-4 text-gray-400 mr-2.5 shrink-0" />
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" className="w-full bg-transparent text-xs text-gray-800 placeholder-gray-400 outline-none" />
              </div>

              <div className="pt-2 text-center">
                <button
                  type="submit"
                  disabled={loading}
                  className="px-10 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs tracking-wider rounded-full shadow-md shadow-emerald-600/30 transition-all uppercase disabled:opacity-50"
                >
                  {loading ? 'Processing...' : isLogin ? 'SIGN IN' : 'SIGN UP'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
