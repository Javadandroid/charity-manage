import { useState, useEffect, useRef } from 'react';
import { useEventStore } from '../store/useEventStore';
import api from '../api';

interface KioskInvoice {
  id: number;
  invoice_number: string;
  booth_name: string;
}

export default function Kiosk() {
  const { activeEvent } = useEventStore();
  const [invoices, setInvoices] = useState<KioskInvoice[]>([]);
  const [lastCalled, setLastCalled] = useState<KioskInvoice | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  // Fallback / initial load
  const fetchInvoices = async () => {
    if (!activeEvent) return;
    try {
      const res = await api.get(`/api/invoices/?event=${activeEvent.id}&status=ready`);
      // Assuming 'ready' status means ready to be called in Kiosk
      setInvoices(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchInvoices();
    // Simulate real-time by polling every 5 seconds
    const interval = setInterval(fetchInvoices, 5000);
    return () => clearInterval(interval);
  }, [activeEvent]);

  // Handle calling a number via TTS
  const callNumber = async (invoice: KioskInvoice) => {
    setLastCalled(invoice);

    // Extract numerical part from inv000025 -> 25
    const numMatch = invoice.invoice_number.match(/\d+/);
    const invoiceNum = numMatch ? parseInt(numMatch[0], 10) : invoice.invoice_number;

    const textToRead = `شماره ${invoiceNum}. ${invoice.booth_name}`;

    // Construct TTS URL and play
    const ttsUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/kiosk/tts/?text=${encodeURIComponent(textToRead)}`;

    if (audioRef.current) {
      audioRef.current.src = ttsUrl;
      try {
         await audioRef.current.play();
      } catch (err) {
         console.warn("Audio play failed. Browser policy might block autoplay until user interacts.", err);
         alert("برای پخش صدا، لطفاً یکبار روی صفحه کلیک کنید.");
      }
    }
  };

  if (!activeEvent) return <div className="p-10 text-center">رویداد فعالی وجود ندارد.</div>;

  return (
    <div className="bg-gray-900 text-white min-h-[calc(100vh-100px)] rounded-xl p-8 flex flex-col md:flex-row gap-8">
      <audio ref={audioRef} className="hidden" />

      {/* Latest Called Number (Big Display) */}
      <div className="md:w-1/2 flex flex-col items-center justify-center border-b md:border-b-0 md:border-l border-gray-700 pb-8 md:pb-0">
        <h2 className="text-3xl text-gray-400 mb-6">شماره فراخوانده شده</h2>
        {lastCalled ? (
          <div className="bg-blue-600 rounded-2xl p-12 text-center shadow-[0_0_50px_rgba(37,99,235,0.5)] w-full max-w-md animate-pulse">
            <div className="text-7xl font-bold font-mono mb-4">{lastCalled.invoice_number.replace('inv', '')}</div>
            <div className="text-3xl mt-4">{lastCalled.booth_name}</div>
          </div>
        ) : (
          <div className="text-gray-500 text-2xl">منتظر فراخوان...</div>
        )}
      </div>

      {/* List of Waiting Numbers */}
      <div className="md:w-1/2 flex flex-col">
        <h2 className="text-3xl text-gray-400 mb-6">در انتظار تحویل</h2>
        <div className="grid grid-cols-2 gap-4 auto-rows-max overflow-y-auto pr-2 max-h-[600px] custom-scrollbar">
          {invoices.length > 0 ? invoices.map((inv) => (
            <div
              key={inv.id}
              onClick={() => callNumber(inv)}
              className="bg-gray-800 p-6 rounded-xl border border-gray-700 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-700 transition"
            >
              <div className="text-4xl font-bold font-mono text-yellow-500">{inv.invoice_number.replace('inv', '')}</div>
              <div className="text-lg text-gray-300 mt-2 text-center">{inv.booth_name}</div>
            </div>
          )) : (
            <div className="col-span-2 text-center text-gray-500 py-10 text-xl">هیچ سفارشی در انتظار نیست.</div>
          )}
        </div>
      </div>
    </div>
  );
}
