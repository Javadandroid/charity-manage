import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

// Ensure you set VITE_API_URL in .env
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Invoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  is_ready: boolean;
}

const KioskQueue: React.FC = () => {
  const [readyInvoices, setReadyInvoices] = useState<Invoice[]>([]);
  const [preparingInvoices, setPreparingInvoices] = useState<Invoice[]>([]);
  const previousReadyIds = useRef<Set<number>>(new Set());
  const audioQueue = useRef<string[]>([]);
  const isPlaying = useRef<boolean>(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/invoices/invoices/`);
      const allInvoices: Invoice[] = response.data;
      
      const ready = allInvoices.filter(i => i.is_ready);
      const preparing = allInvoices.filter(i => !i.is_ready).slice(0, 10);
      
      setReadyInvoices(ready);
      setPreparingInvoices(preparing);

      // Check for new ready invoices to play TTS
      const currentReadyIds = new Set(ready.map(i => i.id));
      const newReadyInvoices = ready.filter(i => !previousReadyIds.current.has(i.id));
      
      if (newReadyInvoices.length > 0 && previousReadyIds.current.size > 0) {
        // Queue new audios
        newReadyInvoices.forEach(inv => {
          const cleanNum = inv.invoice_number.toLowerCase().replace('inv', '').replace(/^0+/, '') || '0';
          const audioUrl = `${API_URL}/media/tts/invoice_${inv.invoice_number}.mp3`;
          audioQueue.current.push(audioUrl);
        });
        playNextAudio();
      }
      
      previousReadyIds.current = currentReadyIds;
    } catch (error) {
      console.error("Error fetching invoices:", error);
    }
  };

  const playNextAudio = () => {
    if (isPlaying.current || audioQueue.current.length === 0) return;
    
    isPlaying.current = true;
    const nextUrl = audioQueue.current.shift();
    
    if (audioRef.current && nextUrl) {
      audioRef.current.src = nextUrl;
      audioRef.current.play().catch(e => {
        console.error("Audio playback failed:", e);
        isPlaying.current = false;
        playNextAudio();
      });
    } else {
      isPlaying.current = false;
    }
  };

  const handleAudioEnded = () => {
    isPlaying.current = false;
    // Add a small delay between announcements
    setTimeout(() => {
      playNextAudio();
    }, 1000);
  };

  useEffect(() => {
    fetchInvoices();
    const intervalId = setInterval(fetchInvoices, 5000); // Poll every 5 seconds
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="bg-slate-900 min-h-[calc(100vh-80px)] rounded-3xl p-8 shadow-2xl flex flex-col relative overflow-hidden">
      {/* Decorative Background Elements */}
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"></div>
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
      <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>

      <audio ref={audioRef} onEnded={handleAudioEnded} className="hidden" />

      <h1 className="text-4xl md:text-5xl font-extrabold text-white text-center mb-12 tracking-tight">
        سیستم نوبت‌دهی
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12 flex-grow z-10">
        
        {/* Preparing Section */}
        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-6 md:p-8 flex flex-col shadow-xl">
          <div className="flex items-center mb-8 border-b border-white/10 pb-4">
            <div className="w-4 h-4 rounded-full bg-yellow-400 animate-pulse ml-3 shadow-[0_0_10px_rgba(250,204,21,0.7)]"></div>
            <h2 className="text-2xl md:text-3xl font-bold text-white">در حال آماده‌سازی</h2>
          </div>
          
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4 auto-rows-max">
            {preparingInvoices.length === 0 ? (
              <p className="text-slate-400 text-lg col-span-full text-center py-10">هیچ سفارشی در حال آماده‌سازی نیست.</p>
            ) : (
              preparingInvoices.map(inv => (
                <div key={inv.id} className="bg-slate-800/80 border border-slate-700 rounded-2xl p-4 text-center transition-transform hover:scale-105 duration-300">
                  <span className="block text-3xl font-bold text-slate-200 tracking-wider">
                    {inv.invoice_number.replace('inv', '')}
                  </span>
                  <span className="block text-xs text-slate-400 mt-2 truncate">
                    {inv.customer_name}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Ready Section */}
        <div className="bg-gradient-to-br from-green-500/20 to-emerald-600/20 backdrop-blur-xl border border-green-500/30 rounded-3xl p-6 md:p-8 flex flex-col shadow-[0_0_40px_rgba(34,197,94,0.15)] relative overflow-hidden">
          <div className="flex items-center mb-8 border-b border-green-500/20 pb-4 relative z-10">
            <div className="w-4 h-4 rounded-full bg-green-400 animate-ping ml-3 shadow-[0_0_10px_rgba(74,222,128,0.8)]"></div>
            <h2 className="text-2xl md:text-3xl font-bold text-green-300">آماده تحویل</h2>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 lg:gap-6 auto-rows-max relative z-10">
            {readyInvoices.length === 0 ? (
              <p className="text-green-200/60 text-lg col-span-full text-center py-10">هیچ سفارشی آماده تحویل نیست.</p>
            ) : (
              readyInvoices.map(inv => (
                <div key={inv.id} className="bg-green-500/20 border border-green-400/40 rounded-2xl p-6 text-center transform transition-all duration-500 animate-fade-in-up hover:bg-green-500/30 shadow-[0_0_15px_rgba(34,197,94,0.2)]">
                  <span className="block text-5xl md:text-6xl font-black text-white tracking-widest drop-shadow-md">
                    {inv.invoice_number.replace('inv', '')}
                  </span>
                  <span className="block text-sm text-green-200 font-medium mt-3">
                    مشتری: {inv.customer_name}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default KioskQueue;
